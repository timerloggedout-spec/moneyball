"""DESIGN §13 machinery tests — the rails as pins.

Covers: intake filing + malformed flag · quarantine state
machine · stamp completeness (Q2) · self-stamp void +
integrity finding (Q3) · exactly-4-exits + classless NONE
refused (Q4) · duplicate link inside quarantine (Q7) ·
receipt chain validity + tamper detection (Q6) · feed
fold + the no-probability scan (Q1/B5).
"""
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location(
    "proposals", ROOT / "scripts" / "proposals.py")
P = importlib.util.module_from_spec(spec)
spec.loader.exec_module(P)

fspec = importlib.util.spec_from_file_location(
    "gen_proposals_feed",
    ROOT / "scripts" / "generate_proposals_feed.py")
G = importlib.util.module_from_spec(fspec)
fspec.loader.exec_module(G)

OB = {"record_of_record_ref": "registry X",
      "settling_receipt_shape": "landed addition w/ PR stamp",
      "stamping_role": "Book settlement stamper",
      "corroboration_leg": "DoE replay (second leg)",
      "dispute_rule": "correction by appended receipted act"}

SPEC = {"proposal_id": "prop-t1", "proposer": "fleet-seat-A",
        "question": "Will Hunt find new Fireworks AI by "
                    "2026-12-31?",
        "proposed_deadline": "2026-12-31",
        "slots": {"actor": "provisioning search",
                  "predicate": "find (landed, PR-stamped)",
                  "object": "Fireworks AI",
                  "deadline": "2026-12-31 EOD PT",
                  "evidence": "registry addition"},
        "proof_obligation": OB}

QA = {"carried": {"subject": "provisioning search system",
                  "record_of_record": "registry X",
                  "deadline": "2026-12-31 EOD PT"},
      "criteria": {"s1": "PASS", "s2": "PASS", "s3": "PASS",
                   "s4": "PASS"},
      "rails_checked": {
          "f1_pre_outcome": "PASS — candidate absent at "
                            "intake; deadline future"},
      "transcript": [{"q": "S1?", "a": "named subject"}]}

STAMP = {"s1": "PASS", "s2": "PASS", "s3": "PASS",
         "s4": "PASS", "subject": "provisioning search system",
         "record_of_record": "registry X",
         "deadline": "2026-12-31 EOD PT",
         "proof_obligation_ref": "prop-t1#proof-obligation",
         "stamper": {"identity": "fleet-seat-B",
                     "role": "custodian reviewer"},
         "ts": "2026-11-04T00:00:00Z", "qa_ref": "prop-t1.qa",
         "contract_subject": "Hunt finds new Fireworks AI by "
                             "2026-12-31 {Y/N}",
         "knowable_at": "2026-12-31T23:59:59-08:00",
         "resolution_rule": "Y iff landed addition by "
                            "knowable_at"}


@pytest.fixture(autouse=True)
def home(tmp_path, monkeypatch):
    monkeypatch.setattr(P, "HOME", tmp_path)
    return tmp_path


def _to_qa(pid="prop-t1"):
    P.propose(SPEC, "fleet-seat-A", "proposer")
    P.quarantine(pid, "fleet-seat-A", "proposer")
    P.begin_qa(pid, "custodian", "reviewer")
    P.record_qa(pid, QA, "custodian", "reviewer")


def test_full_contract_path():
    _to_qa()
    out = P.stamp("prop-t1", STAMP, "custodian", "reviewer")
    obj = out["obj"]
    assert obj["state"] == "CONTRACT_DERIVED"
    assert obj["decision"]["contract"]["subject"].endswith(
        "{Y/N}")
    P.handoff("prop-t1", "custodian", "reviewer")
    obj = P.load_obj("prop-t1")
    assert obj["decision"]["handoff"]["state"] == "HANDED_OFF"
    assert P.verify_chain()


def test_malformed_obligation_flagged_never_stampable():
    bad = dict(SPEC, proposal_id="prop-t2",
               proof_obligation={"record_of_record_ref": "x"})
    obj = P.propose(bad, "fleet-seat-A", "proposer")
    assert "malformed_at_intake" in obj["decision"]
    P.quarantine("prop-t2", "fleet-seat-A", "proposer")
    P.begin_qa("prop-t2", "custodian", "reviewer")
    st = dict(STAMP,
              proof_obligation_ref="prop-t2#proof-obligation")
    with pytest.raises(P.MalformedAtIntake):
        P.stamp("prop-t2", st, "custodian", "reviewer")


def test_stamp_missing_field_refused():
    _to_qa()
    st = dict(STAMP)
    del st["deadline"]
    with pytest.raises(P.IncompleteRecord):
        P.stamp("prop-t1", st, "custodian", "reviewer")


def test_stamp_fail_criterion_refused():
    _to_qa()
    st = dict(STAMP, s3="FAIL")
    with pytest.raises(P.IncompleteRecord):
        P.stamp("prop-t1", st, "custodian", "reviewer")


def test_self_stamp_void_and_finding_receipted():
    _to_qa()
    st = dict(STAMP, stamper={"identity": "fleet-seat-A",
                              "role": "custodian reviewer"})
    with pytest.raises(P.IntegrityFinding):
        P.stamp("prop-t1", st, "custodian", "reviewer")
    rows = P.read_log()
    assert any(r.get("kind") == "integrity_finding"
               for r in rows)
    assert P.load_obj("prop-t1")["state"] == "IN_Q&A"
    assert P.verify_chain()


def test_none_exit_classes_and_classless_refused():
    P.propose(SPEC, "fleet-seat-A", "proposer")
    P.quarantine("prop-t1", "fleet-seat-A", "proposer")
    with pytest.raises(P.IncompleteRecord):
        P.close_none("prop-t1", None, "no class",
                     "custodian", "reviewer")
    with pytest.raises(P.IncompleteRecord):
        P.close_none("prop-t1", "N9", "bad class",
                     "custodian", "reviewer")
    obj = P.close_none("prop-t1", "N1",
                       "S4 fail → N1 (no record of record)",
                       "custodian", "reviewer",
                       failing_criterion="S4",
                       missing="a record of record")
    assert obj["state"] == "NONE_FOUND"
    assert obj["exit"]["class"] == "N1"


def test_duplicate_link_inside_quarantine():
    P.propose(SPEC, "fleet-seat-A", "proposer")
    dup = dict(SPEC, proposal_id="prop-t3")
    P.propose(dup, "fleet-seat-C", "proposer")
    P.quarantine("prop-t3", "fleet-seat-C", "proposer")
    obj = P.link_duplicate("prop-t3", "prop-t1",
                           "custodian", "reviewer")
    assert obj["decision"]["duplicate_of"] == "prop-t1"
    assert obj["state"] == "QUARANTINED"  # never deleted


def test_quarantine_stamp_on_record():
    obj = P.propose(SPEC, "fleet-seat-A", "proposer")
    assert obj["intake"]["public_intake"].startswith("CLOSED")
    P.quarantine("prop-t1", "fleet-seat-A", "proposer")
    obj = P.load_obj("prop-t1")
    qs = obj["quarantine_stamp"]
    assert qs["key"] == "quarantine"
    assert qs["unscored_in_fact"] is True
    assert qs["receipt_seq"] == 2


def test_q5_already_known_never_stamped():
    _to_qa()
    qa = dict(QA, determination="ALREADY_KNOWN")
    P.record_qa("prop-t1", qa, "custodian", "reviewer")
    with pytest.raises(P.IncompleteRecord):
        P.stamp("prop-t1", STAMP, "custodian", "reviewer")
    rows = P.read_log()
    assert any(r.get("kind") == "q5_refusal" for r in rows)
    assert P.load_obj("prop-t1")["state"] == "IN_Q&A"
    # the one lawful exit: NONE, class N3
    obj = P.close_none(
        "prop-t1", "N3",
        "F1 fail → N3 (outcome determined at intake — "
        "ALREADY_KNOWN)", "custodian", "reviewer")
    assert obj["exit"]["class"] == "N3"


def test_n1_exit_emits_backlog_record(home):
    P.propose(SPEC, "fleet-seat-A", "proposer")
    P.quarantine("prop-t1", "fleet-seat-A", "proposer")
    with pytest.raises(P.IncompleteRecord):
        P.close_none("prop-t1", "N1", "S4 fail → N1",
                     "custodian", "reviewer")
    obj = P.close_none(
        "prop-t1", "N1", "S4 fail → N1 (no source)",
        "custodian", "reviewer", failing_criterion="S4",
        missing="a record of record for the subject")
    assert obj["exit"]["backlog_ref"] == "backlog/prop-t1.json"
    rec = json.loads((home / "proposals" / "backlog"
                      / "prop-t1.json").read_text())
    assert rec["failing_criterion"] == "S4"
    assert rec["qa_ref"] == "prop-t1.qa"
    assert "exit_receipt_ref" in rec and rec["ts"]


def test_chain_tamper_detected():
    _to_qa()
    rows = P.read_log()
    rows[1]["actor"] = "forged"
    assert not P.verify_chain(rows)


def _scan(o, path="$"):
    hits = []
    if isinstance(o, dict):
        for k, v in o.items():
            if "probab" in k or k in ("p", "odds"):
                hits.append(f"{path}.{k}")
            hits += _scan(v, f"{path}.{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            hits += _scan(v, f"{path}[{i}]")
    return hits


def test_feed_fold_and_no_probability(home):
    _to_qa()
    P.stamp("prop-t1", STAMP, "custodian", "reviewer")
    feed = G.build(home)
    assert feed["schema"] == "moneyball-proposals-feed/v1"
    assert feed["chain"]["valid"]
    assert feed["counts"]["by_state"] == {
        "CONTRACT_DERIVED": 1}
    # the scan covers proposal DATA; claims_ceiling is the
    # doctrine statement of the rail itself (asserted
    # present), not a data field
    assert "probability_rail" in feed["claims_ceiling"]
    data = {k: v for k, v in feed.items()
            if k != "claims_ceiling"}
    assert _scan(data) == [], _scan(data)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
