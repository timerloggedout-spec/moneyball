#!/usr/bin/env python3
"""MoneyBall proposals machinery (DESIGN §13, tranche 1).

Stage-0 decision objects + intake quarantine + the Q&A record
store + the doctrine-fit stamp surface + the receipt chain
(the proposal log IS the chain — §13.3A). Custody: build arm
[MUSEai]@{role:{optimizations-assurance}} under Web3's
composition hand; doctrine = DESIGN §13.1–13.3A (DoE leg).

Rails enforced in code, not prose:
- a proposal is filed WITH its proof obligation (5 fields);
  an incomplete obligation flags the object malformed at
  intake — it stays in quarantine, never rejected, never
  silently dropped, and can never be stamped (§13.3A);
- quarantine is unscored in fact (Q1): this module has no
  probability field anywhere; nothing here elicits one;
- exactly four receipted exits (Q4): contract (via the
  doctrine-fit stamp) · N1 · N2 · N3. A NONE exit without
  exactly one primary class is REFUSED by the chain writer;
- the stamp is the contract-path exit receipt (Q2): no
  field, no stamp; a self-stamp is void and appends an
  integrity finding instead (Q3);
- duplicates resolve inside quarantine by link receipt —
  never deletion, never double-stamp (Q7);
- every transition appends its Q6 receipt {proposal_id ·
  from_state · to_state · actor · role · ts · basis_ref}
  to the hash-chained log; gaps are detectable by verify.

Store layout (repo root = parent of this script's dir):
  data/proposals/<proposal_id>.json       the object
  data/proposals/<proposal_id>.qa.json    the Q&A record
  data/proposal-log.jsonl                 the receipt chain
PROPOSALS_HOME overrides the data dir (tests).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOME = Path(os.environ.get("PROPOSALS_HOME", ROOT / "data"))
SCHEMA = "moneyball-proposal/v1"
STATES = ("PROPOSED", "QUARANTINED", "IN_Q&A",
          "CONTRACT_DERIVED", "LISTED", "NONE_FOUND")
EXIT_CLASSES = ("N1", "N2", "N3")
OBLIGATION_FIELDS = ("record_of_record_ref",
                     "settling_receipt_shape", "stamping_role",
                     "corroboration_leg", "dispute_rule")


class MalformedAtIntake(Exception):
    pass


class IncompleteRecord(Exception):
    pass


class IntegrityFinding(Exception):
    pass


def now() -> str:
    return datetime.now(timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ")


def _canon(obj) -> str:
    return json.dumps(obj, sort_keys=True,
                      separators=(",", ":"))


def _hash(prev: str, row: dict) -> str:
    body = {k: v for k, v in row.items()
            if k not in ("hash", "prev_hash")}
    return hashlib.sha256(
        (prev + _canon(body)).encode()).hexdigest()[:24]


# ---------- store ----------

def obj_path(pid: str) -> Path:
    return HOME / "proposals" / f"{pid}.json"


def qa_path(pid: str) -> Path:
    return HOME / "proposals" / f"{pid}.qa.json"


def log_path() -> Path:
    return HOME / "proposal-log.jsonl"


def load_obj(pid: str) -> dict:
    return json.loads(obj_path(pid).read_text())


def save_obj(obj: dict) -> None:
    obj_path(obj["proposal_id"]).parent.mkdir(
        parents=True, exist_ok=True)
    obj_path(obj["proposal_id"]).write_text(
        json.dumps(obj, indent=1) + "\n")


def load_qa(pid: str) -> dict:
    p = qa_path(pid)
    return json.loads(p.read_text()) if p.exists() else {}


def save_qa(pid: str, qa: dict) -> None:
    qa_path(pid).parent.mkdir(parents=True, exist_ok=True)
    qa_path(pid).write_text(json.dumps(qa, indent=1) + "\n")


def read_log() -> list[dict]:
    p = log_path()
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text().splitlines()
            if l.strip()]


def verify_chain(rows: list[dict] | None = None) -> bool:
    rows = read_log() if rows is None else rows
    prev = "GENESIS"
    for i, r in enumerate(rows, 1):
        if r.get("seq") != i or r.get("prev_hash") != prev:
            return False
        if r.get("hash") != _hash(prev, r):
            return False
        prev = r["hash"]
    return True


def append_receipt(pid: str, frm: str, to: str, actor: str,
                   role: str, basis_ref: str,
                   extra: dict | None = None) -> dict:
    rows = read_log()
    prev = rows[-1]["hash"] if rows else "GENESIS"
    row = {"seq": len(rows) + 1, "ts": now(),
           "proposal_id": pid, "from_state": frm,
           "to_state": to, "actor": actor, "role": role,
           "basis_ref": basis_ref, "prev_hash": prev}
    if extra:
        row.update(extra)
    row["hash"] = _hash(prev, row)
    log_path().parent.mkdir(parents=True, exist_ok=True)
    with log_path().open("a") as fh:
        fh.write(json.dumps(row) + "\n")
    return row


def _transition(obj: dict, to: str, actor: str, role: str,
                basis_ref: str,
                extra: dict | None = None) -> dict:
    frm = obj["state"]
    r = append_receipt(obj["proposal_id"], frm, to, actor,
                       role, basis_ref, extra)
    obj["state"] = to
    save_obj(obj)
    return r


# ---------- intake ----------

def obligation_complete(ob: dict | None) -> bool:
    return bool(ob) and all(
        str(ob.get(f) or "").strip() for f in OBLIGATION_FIELDS)


def propose(spec: dict, actor: str, role: str) -> dict:
    pid = spec["proposal_id"]
    if obj_path(pid).exists():
        raise MalformedAtIntake(f"{pid} already filed")
    ob = spec.get("proof_obligation") or {}
    obj = {
        "schema": SCHEMA, "proposal_id": pid,
        "proposer": spec["proposer"],
        "posed_at": spec.get("posed_at") or now(),
        "question": spec["question"],
        "proposed_deadline": spec.get("proposed_deadline"),
        "suggested_record_of_record":
            spec.get("suggested_record_of_record"),
        "slots": spec.get("slots") or {},
        "proof_obligation": {f: ob.get(f) for f in
                             OBLIGATION_FIELDS},
        "state": "PROPOSED", "decision": {},
        "qa_ref": f"{pid}.qa", "stamp": None, "exit": None,
        "quarantine_stamp": None,
        "intake": {"channel": "fleet-machinery",
                   "tranche": 1,
                   "public_intake": "CLOSED (fleet-first, "
                                    "§13.7 call i)"},
    }
    if not obligation_complete(ob):
        # malformed at intake: filed, flagged, quarantined —
        # neither rejected nor silently dropped (§13.3A)
        obj["decision"]["malformed_at_intake"] = (
            "proof obligation incomplete: "
            + ", ".join(f for f in OBLIGATION_FIELDS
                        if not str(ob.get(f) or "").strip()))
    save_obj(obj)
    append_receipt(pid, "∅", "PROPOSED", actor, role,
                   "intake filing")
    return obj


def quarantine(pid: str, actor: str, role: str) -> dict:
    obj = load_obj(pid)
    if obj["state"] != "PROPOSED":
        raise MalformedAtIntake(
            f"quarantine from {obj['state']}")
    r = _transition(obj, "QUARANTINED", actor, role,
                    "intake quarantine gate (§13.1A)")
    # Q1: quarantine is a verbatim-keyed stamped state —
    # the object carries the stamp on its record and every
    # downstream surface keys on it exactly (no aliases)
    obj = load_obj(pid)
    obj["quarantine_stamp"] = {
        "key": "quarantine", "state": "QUARANTINED",
        "unscored_in_fact": True, "by": actor, "role": role,
        "at": r["ts"], "receipt_seq": r["seq"],
        "receipt_hash": r["hash"]}
    save_obj(obj)
    return obj


def begin_qa(pid: str, actor: str, role: str) -> dict:
    obj = load_obj(pid)
    if obj["state"] != "QUARANTINED":
        raise MalformedAtIntake(f"begin_qa from {obj['state']}")
    _transition(obj, "IN_Q&A", actor, role, obj["qa_ref"])
    return obj


def record_qa(pid: str, qa: dict, actor: str,
              role: str) -> dict:
    obj = load_obj(pid)
    if obj["state"] != "IN_Q&A":
        raise MalformedAtIntake(f"record_qa from {obj['state']}")
    qa = dict(qa)
    qa.setdefault("proposal_id", pid)
    qa["recorded_by"] = actor
    qa["recorded_at"] = now()
    save_qa(pid, qa)
    append_receipt(pid, "IN_Q&A", "IN_Q&A", actor, role,
                   obj["qa_ref"],
                   {"kind": "qa_recorded"})
    return obj


# ---------- the doctrine-fit stamp (Q2/Q3) ----------

STAMP_FIELDS = ("s1", "s2", "s3", "s4", "subject",
                "record_of_record", "deadline",
                "proof_obligation_ref", "stamper", "ts",
                "qa_ref")
# the derived contract's own fields (§13.3), filed by the
# stamper with the stamp act — the contract is the stamp's
# output, carried on the object under decision.contract
CONTRACT_FIELDS = ("contract_subject", "knowable_at",
                   "resolution_rule")


def stamp(pid: str, st: dict, actor: str, role: str) -> dict:
    obj = load_obj(pid)
    if obj["state"] != "IN_Q&A":
        raise MalformedAtIntake(f"stamp from {obj['state']}")
    missing = [f for f in STAMP_FIELDS + CONTRACT_FIELDS
               if st.get(f) in (None, "")]
    if missing:
        raise IncompleteRecord(
            f"stamp missing fields: {missing} — no field, "
            "no stamp (Q2)")
    for c in ("s1", "s2", "s3", "s4"):
        if st[c] not in ("PASS", "FAIL"):
            raise IncompleteRecord(f"{c} must be PASS|FAIL")
    stamper_id = (st.get("stamper") or {}).get("identity", "")
    if not stamper_id or stamper_id == obj["proposer"]:
        # Q3: a self-stamp is void + an integrity finding
        append_receipt(pid, "IN_Q&A", "IN_Q&A", actor, role,
                       "Q3 self-stamp attempt",
                       {"kind": "integrity_finding",
                        "finding": "self-stamp void (Q3): "
                                   "stamper == proposer"})
        raise IntegrityFinding(
            "self-stamp void (Q3) — integrity finding "
            "receipted; object remains IN_Q&A")
    if not obligation_complete(obj["proof_obligation"]):
        raise MalformedAtIntake(
            "proof obligation incomplete — malformed at "
            "intake, cannot be stamped (§13.3A)")
    if st["proof_obligation_ref"] != f"{pid}#proof-obligation":
        raise IncompleteRecord(
            "stamp must cite the obligation as filed at "
            f"creation ({pid}#proof-obligation)")
    qa = load_qa(pid)
    carried = qa.get("carried") or {}
    for f in ("subject", "record_of_record", "deadline"):
        if carried.get(f) and st[f] != carried[f]:
            raise IncompleteRecord(
                f"stamp {f} must carry the Q&A record "
                "verbatim")
    if any(st[c] != "PASS" for c in ("s1", "s2", "s3", "s4")):
        raise IncompleteRecord(
            "contract path requires S1–S4 PASS; a FAIL "
            "routes to a classified NONE exit (Q4)")
    # Q5/F1: already-knowable outcomes NEVER form contracts
    # — ALREADY_KNOWN is never stamped, however clean the
    # paperwork; and the pre-outcome attestation must be on
    # the Q&A record (no field, no stamp)
    if qa.get("determination") == "ALREADY_KNOWN":
        append_receipt(pid, "IN_Q&A", "IN_Q&A", actor, role,
                       obj["qa_ref"],
                       {"kind": "q5_refusal",
                        "finding": "ALREADY_KNOWN — stamp "
                                   "refused (Q5); route = "
                                   "NONE exit, class N3"})
        raise IncompleteRecord(
            "ALREADY_KNOWN is never stamped (Q5) — the "
            "exit is NONE_FOUND, class N3")
    f1 = (qa.get("rails_checked") or {}).get(
        "f1_pre_outcome", "")
    if not str(f1).startswith("PASS"):
        raise IncompleteRecord(
            "Q&A record carries no F1 pre-outcome PASS "
            "attestation — no field, no stamp (Q2/Q5)")
    obj["stamp"] = st
    r = _transition(obj, "CONTRACT_DERIVED", actor, role,
                    f"{pid}#doctrine-fit-stamp")
    obj = load_obj(pid)
    obj["decision"]["contract"] = {
        "subject": st["contract_subject"],
        "knowable_at": st["knowable_at"],
        "record_of_record": st["record_of_record"],
        "resolution_rule": st["resolution_rule"],
        "proposer_attribution": obj["proposer"],
        "proof_obligation": obj["proof_obligation"],
    }
    save_obj(obj)
    return {"receipt": r, "obj": obj}


def void_stamp(pid: str, actor: str, role: str,
               basis_ref: str) -> dict:
    obj = load_obj(pid)
    if obj["state"] != "CONTRACT_DERIVED" or not obj["stamp"]:
        raise MalformedAtIntake("no live stamp to void")
    _transition(obj, "IN_Q&A", actor, role, basis_ref,
                {"kind": "stamp_voided"})
    obj = load_obj(pid)
    obj["stamp"] = None
    obj["decision"].pop("contract", None)
    obj["decision"].pop("handoff", None)
    save_obj(obj)
    return obj


def handoff(pid: str, actor: str, role: str) -> dict:
    obj = load_obj(pid)
    if obj["state"] != "CONTRACT_DERIVED":
        raise MalformedAtIntake(f"handoff from {obj['state']}")
    r = append_receipt(pid, "CONTRACT_DERIVED",
                       "CONTRACT_DERIVED", actor, role,
                       f"{pid}#doctrine-fit-stamp",
                       {"kind": "book_intake_handoff"})
    obj["decision"]["handoff"] = {
        "to": "MoneyBall Book intake",
        "state": "HANDED_OFF", "at": now(),
        "receipt_seq": r["seq"], "receipt_hash": r["hash"],
    }
    save_obj(obj)
    return obj


# ---------- classified NONE exits (Q4) ----------

def close_none(pid: str, exit_class: str, derivation: str,
               actor: str, role: str,
               failing_criterion: str | None = None,
               missing: str | None = None) -> dict:
    obj = load_obj(pid)
    if obj["state"] in ("CONTRACT_DERIVED", "LISTED",
                        "NONE_FOUND"):
        raise MalformedAtIntake(
            f"NONE exit from {obj['state']}")
    if exit_class not in EXIT_CLASSES:
        # the chain refuses a classless NONE exactly as it
        # refuses a missing receipt (§13.3A)
        raise IncompleteRecord(
            f"exit class must be exactly one of "
            f"{EXIT_CLASSES}; got {exit_class!r} — a "
            "classless NONE is an INCOMPLETE record")
    if not derivation.strip():
        raise IncompleteRecord(
            "exit receipt must carry the criterion→class "
            "derivation (Q4)")
    if exit_class == "N1" and not (
            failing_criterion in ("S1", "S2", "S4")
            and missing):
        raise IncompleteRecord(
            "an N1 exit must name its failing criterion "
            "(S1/S2/S4) and the missing subject/source/"
            "instrument — the backlog record is part of "
            "the exit (§13.7 call iii)")
    r = _transition(obj, "NONE_FOUND", actor, role,
                    obj["qa_ref"],
                    {"kind": "none_exit",
                     "exit_class": exit_class,
                     "derivation": derivation})
    obj = load_obj(pid)
    obj["exit"] = {"class": exit_class,
                   "derivation": derivation,
                   "receipt_seq": r["seq"],
                   "receipt_hash": r["hash"], "at": r["ts"]}
    save_obj(obj)
    if exit_class == "N1":
        # the N1 home = the DoE upgrade backlog; the exit
        # emits the backlog record in the §13.7(iii) shape
        backlog = {"proposal_id": pid,
                   "failing_criterion": failing_criterion,
                   "missing": missing,
                   "qa_ref": obj["qa_ref"],
                   "exit_receipt_ref":
                       f"seq {r['seq']} · {r['hash']}",
                   "ts": r["ts"]}
        bp = HOME / "proposals" / "backlog" / f"{pid}.json"
        bp.parent.mkdir(parents=True, exist_ok=True)
        bp.write_text(json.dumps(backlog, indent=1) + "\n")
        obj["exit"]["backlog_ref"] = f"backlog/{pid}.json"
        save_obj(obj)
    return obj


# ---------- duplicates (Q7) ----------

def duplicate_key(obj: dict) -> tuple:
    carried = (load_qa(obj["proposal_id"]).get("carried")
               or {})
    return ((carried.get("subject") or "").strip().lower(),
            (carried.get("record_of_record") or "")
            .strip().lower(),
            (carried.get("deadline") or "").strip().lower())


def link_duplicate(pid: str, canonical_id: str, actor: str,
                   role: str) -> dict:
    obj = load_obj(pid)
    if obj["state"] not in ("QUARANTINED", "IN_Q&A"):
        raise MalformedAtIntake(
            f"duplicate link from {obj['state']} — "
            "duplicates resolve inside quarantine (Q7)")
    if not obj_path(canonical_id).exists():
        raise IncompleteRecord(
            f"canonical {canonical_id} not filed")
    append_receipt(pid, obj["state"], obj["state"], actor,
                   role, canonical_id,
                   {"kind": "duplicate_link",
                    "canonical": canonical_id})
    obj["decision"]["duplicate_of"] = canonical_id
    save_obj(obj)
    return obj


# ---------- CLI ----------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="proposals")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("propose", "record-qa", "stamp"):
        p = sub.add_parser(name)
        p.add_argument("file")
        p.add_argument("--actor", required=True)
        p.add_argument("--role", required=True)
    for name in ("quarantine", "begin-qa", "handoff"):
        p = sub.add_parser(name)
        p.add_argument("proposal_id")
        p.add_argument("--actor", required=True)
        p.add_argument("--role", required=True)
    p = sub.add_parser("none")
    p.add_argument("proposal_id")
    p.add_argument("--class", dest="exit_class", required=True)
    p.add_argument("--derivation", required=True)
    p.add_argument("--failing-criterion", default=None)
    p.add_argument("--missing", default=None)
    p.add_argument("--actor", required=True)
    p.add_argument("--role", required=True)
    p = sub.add_parser("link")
    p.add_argument("proposal_id")
    p.add_argument("--canonical", required=True)
    p.add_argument("--actor", required=True)
    p.add_argument("--role", required=True)
    p = sub.add_parser("void-stamp")
    p.add_argument("proposal_id")
    p.add_argument("--basis", required=True)
    p.add_argument("--actor", required=True)
    p.add_argument("--role", required=True)
    sub.add_parser("verify")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "propose":
            obj = propose(json.loads(Path(a.file).read_text()),
                          a.actor, a.role)
            print(f"filed {obj['proposal_id']} PROPOSED")
        elif a.cmd == "quarantine":
            quarantine(a.proposal_id, a.actor, a.role)
            print(f"{a.proposal_id} QUARANTINED")
        elif a.cmd == "begin-qa":
            begin_qa(a.proposal_id, a.actor, a.role)
            print(f"{a.proposal_id} IN_Q&A")
        elif a.cmd == "record-qa":
            qa = json.loads(Path(a.file).read_text())
            record_qa(qa["proposal_id"], qa, a.actor, a.role)
            print(f"{qa['proposal_id']} Q&A recorded")
        elif a.cmd == "stamp":
            st = json.loads(Path(a.file).read_text())
            out = stamp(st["proposal_id"], st, a.actor,
                        a.role)
            print(f"{st['proposal_id']} CONTRACT_DERIVED "
                  f"(receipt seq {out['receipt']['seq']})")
        elif a.cmd == "handoff":
            handoff(a.proposal_id, a.actor, a.role)
            print(f"{a.proposal_id} HANDED_OFF → Book intake")
        elif a.cmd == "none":
            close_none(a.proposal_id, a.exit_class,
                       a.derivation, a.actor, a.role,
                       a.failing_criterion, a.missing)
            print(f"{a.proposal_id} NONE_FOUND [{a.exit_class}]")
        elif a.cmd == "link":
            link_duplicate(a.proposal_id, a.canonical,
                           a.actor, a.role)
            print(f"{a.proposal_id} linked → {a.canonical}")
        elif a.cmd == "void-stamp":
            void_stamp(a.proposal_id, a.actor, a.role, a.basis)
            print(f"{a.proposal_id} stamp VOIDED → IN_Q&A")
        elif a.cmd == "verify":
            rows = read_log()
            ok = verify_chain(rows)
            print(f"chain {'VALID' if ok else 'INVALID'}: "
                  f"{len(rows)} receipts")
            return 0 if ok else 1
    except (MalformedAtIntake, IncompleteRecord,
            IntegrityFinding) as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
