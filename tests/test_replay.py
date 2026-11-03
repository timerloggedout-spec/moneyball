"""Settlement replay (scripts/settlement/replay.py): F1 forecast
timing (§6.1), the named B4/B5 check homes, and F3 (p = 0.5 is
abstention-shaped) — DoE replay-audit findings, 2026-11-03."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _replay():
    spec = importlib.util.spec_from_file_location(
        "replay", ROOT / "scripts/settlement/replay.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _subject(sid="S-1", knowable="2026-11-04", value=None):
    return {"id": sid, "knowable": knowable,
            "record_of_record": "official record",
            "expectation_record": {"quantity": "P(Y)"},
            "settle": {"source": "official record", "value": value}}


def _position(pid="POS-1", opened="2026-11-03", p=0.7, sid="S-1"):
    return {"position_id": pid, "subject_id": sid, "opened": opened,
            "basis": "cited basis", "status": "open", "p": p,
            "gambler": "tester"}


def test_f1_late_position_invalid_and_unscored(tmp_path):
    rp = _replay()
    book = {"subjects": [_subject(value="Y")],
            "positions": [_position(opened="2026-11-05")],
            "ledger_of_record": "book/ledger.jsonl"}
    inv, invalid = rp.validate(book["subjects"], book["positions"],
                               [], book)
    assert not inv["F1_forecast_timing_pre_outcome"]["pass"]
    assert invalid == {"POS-1"}


def test_f1_pre_outcome_passes_and_unestablished_listed():
    rp = _replay()
    book = {"subjects": [_subject(),
                         _subject(sid="S-2",
                                  knowable="NOT_ESTABLISHED (event)")],
            "positions": [_position(),
                          _position(pid="POS-2", sid="S-2")],
            "ledger_of_record": "book/ledger.jsonl"}
    inv, invalid = rp.validate(book["subjects"], book["positions"],
                               [], book)
    f1 = inv["F1_forecast_timing_pre_outcome"]
    assert f1["pass"] and invalid == set()
    assert any("POS-2" in x for x in f1["not_established"])


def test_b5_numeric_winprob_import_flagged():
    rp = _replay()
    book = {"subjects": [_subject()], "positions": [_position()],
            "ledger_of_record": "book/ledger.jsonl",
            "hidden": {"winprob": 0.83}}
    inv, _ = rp.validate(book["subjects"], book["positions"], [], book)
    assert not inv["B5_hidden_winprob_never_imported"]["pass"]
    clean = {"subjects": [_subject()], "positions": [_position()],
             "ledger_of_record": "book/ledger.jsonl",
             "note": "winprob stays home (boundary note string)"}
    inv2, _ = rp.validate(clean["subjects"], clean["positions"], [],
                          clean)
    assert inv2["B5_hidden_winprob_never_imported"]["pass"]
    assert inv2["B4_ledger_first_public_render_only"]["pass"]


def test_f3_abstention_excluded_from_scoring(tmp_path):
    rp = _replay()
    book = {"subjects": [_subject(value="Y")],
            "positions": [_position(p=0.5)],
            "ledger_of_record": "book/ledger.jsonl"}
    bp = tmp_path / "book.json"
    bp.write_text(json.dumps(book))
    lp = tmp_path / "ledger.jsonl"
    lp.write_text("")
    out = tmp_path / "report.json"
    rc = rp.main(["replay.py", str(bp), str(lp), "--out", str(out)])
    assert rc == 0
    report = json.loads(out.read_text())
    assert report["abstentions"] == ["POS-1"]
    assert report["scores"] == {}
    assert report["coverage"]["resolved"] == 0
