#!/usr/bin/env python3
"""MoneyBall settlement replay — DESIGN §6.2 pipeline skeleton (lane B, settlement-first).

Deterministic, replayable from the records alone (stdlib only, no discretion, no overrides):
  1. load Book (challenges-book.json) + append-only ledger (ledger.jsonl)
  2. validate invariants B1 / B2 / B3, the named B4 / B5 check homes, and the §6.1
     forecast-timing invariant F1 (exit 1 on any violation; fail-closed)
  3. settlements = subjects whose settle.value is non-null (settlement comes ONLY from the
     subject's named record of record — the settle.source scaffolding is what B3 checks here;
     this job never substitutes another source)
  4. score positions carrying an explicit pre-lock probability p (absent p => NOT_SCORED;
     p = 0.5 exactly => abstention-shaped, a separate count, never a call — §6.3, DoE F3)
     with Brier + hit-rate per §6.3, unweighted by stake
  5. emit the replay report (moneyball-settlement-replay/v1) — honest empty states:
     no settlements => settlements [], scores {}, ranking UNRANKED / INSUFFICIENT_N

Usage: replay.py BOOK_JSON LEDGER_JSONL [--out REPORT_JSON]
The report JSON is printed to stdout; --out also writes it to a file.
"""
import json, re, sys, pathlib
from datetime import datetime, time, timedelta, timezone

SCHEMA = "moneyball-settlement-replay/v1"
RANKING_GATE_N = 30          # §6.3 public-ranking gate
RANKING_GATE_SUBJECTS = 10
PT = timezone(timedelta(hours=-8))   # book anchors are PT (fleet convention)


def parse_ts(value, *, end_of_day=False):
    """Parse an ISO date/datetime to an aware datetime; None when the
    value is not a timestamp (e.g. 'NOT_ESTABLISHED ...' text).
    Date-only values follow the fleet convention: a position opened
    on a date counts from that date's start; a knowable date counts
    to that date's end (23:59:59 PT)."""
    if not isinstance(value, str):
        return None
    v = value.strip()
    try:
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
            d = datetime.strptime(v, "%Y-%m-%d").date()
            t = time(23, 59, 59) if end_of_day else time(0, 0, 0)
            return datetime.combine(d, t, tzinfo=PT)
        dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=PT)
    except ValueError:
        return None


def position_ts(position, ledger_events):
    """The position's open timestamp: its own `opened` field, else the
    ledger's position_opened event for its id (B2's ref resolution)."""
    ts = parse_ts(position.get("opened"))
    if ts:
        return ts
    pid = position.get("position_id") or ""
    for e in ledger_events:
        if event_type(e) == "position_opened" and pid and \
                pid in json.dumps(e):
            ts = parse_ts(e.get("at") or e.get("ts"))
            if ts:
                return ts
    return None


def knowable_ts(subject, ledger_events):
    """Earliest instant the subject's outcome is knowable: the
    subject's `knowable` timestamp when established, else the first
    settlement event for the subject in the ledger. None when
    NOT_ESTABLISHED (an event, not a date — §5 lifecycle)."""
    cands = []
    k = parse_ts(subject.get("knowable"), end_of_day=True)
    if k:
        cands.append(k)
    sid = subject.get("id") or ""
    for e in ledger_events:
        if event_type(e) in ("settlement_proposed", "settlement_final") \
                and sid and sid in json.dumps(e):
            ts = parse_ts(e.get("at") or e.get("ts"))
            if ts:
                cands.append(ts)
    return min(cands) if cands else None

def load_book(path):
    return json.loads(pathlib.Path(path).read_text())

def load_ledger(path):
    events = []
    for line in pathlib.Path(path).read_text().splitlines():
        if line.strip():
            events.append(json.loads(line))
    return events

def event_type(e):
    return e.get("event") or e.get("type")

def has_basis(rec):
    b = rec.get("basis") or rec.get("basis_refs")
    if isinstance(b, str):
        return bool(b.strip())
    if isinstance(b, list):
        return len(b) > 0
    return False

def _walk(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield f"{path}.{k}" if path else k, k, v
            yield from _walk(v, f"{path}.{k}" if path else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _walk(v, f"{path}[{i}]")


def validate(subjects, positions, ledger_events, book=None):
    """Returns ({invariant: {pass, violations, ...}}, invalid_position_ids)
    for B1, B2, B3, the named B4/B5 check homes, and F1 (§6.1 timing)."""
    inv = {}
    # B1 — exactly one expectation_record per subject (object, or list of length 1)
    v = []
    for s in subjects:
        er = s.get("expectation_record")
        if er is None:
            v.append(f"{s.get('id')}: no expectation_record")
        elif isinstance(er, list) and len(er) != 1:
            v.append(f"{s.get('id')}: {len(er)} expectation_records")
        elif not isinstance(er, (dict, list)):
            v.append(f"{s.get('id')}: expectation_record malformed")
    inv["B1_one_expectation_record_per_subject"] = {"pass": not v, "violations": v}
    # B3 — every subject names its record of record + settle.source scaffolding
    v = []
    for s in subjects:
        if not (s.get("record_of_record") or "").strip():
            v.append(f"{s.get('id')}: record_of_record missing")
        settle = s.get("settle") or {}
        if not (settle.get("source") or "").strip():
            v.append(f"{s.get('id')}: settle.source missing")
    inv["B3_record_of_record_named"] = {"pass": not v, "violations": v}
    # B2 — every position cites basis: book positions by field; ledger position_opened
    # events by their own basis field or by resolving the referenced book position.
    v = []
    by_id = {p.get("position_id"): p for p in positions}
    for p in positions:
        if not has_basis(p):
            v.append(f"{p.get('position_id')}: position cites no basis")
    for e in ledger_events:
        if event_type(e) == "position_opened":
            if has_basis(e):
                continue
            m = re.search(r"POS-\d+", json.dumps(e))
            ref = by_id.get(m.group(0)) if m else None
            if ref is not None and has_basis(ref):
                continue
            v.append(f"ledger position_opened at {e.get('at')}: basis not cited (event or referenced position)")
    inv["B2_basis_cited"] = {"pass": not v, "violations": v}
    # B4 — named check home (input side): the ledger of record is the
    # private append-only ledger and no position carries external
    # participation. (Render-side R1–R3 are verified at the render,
    # not here; B4 was discharged for public read-only render by
    # owner ruling 2026-11-02 — entries stay internal/observational.)
    v = []
    lor = (book or {}).get("ledger_of_record") or ""
    if "ledger.jsonl" not in str(lor):
        v.append("book does not name the append-only ledger.jsonl "
                 "as ledger_of_record")
    for p in positions:
        if p.get("external") or p.get("external_participation"):
            v.append(f"{p.get('position_id')}: external participation "
                     f"flag present (B4: entries internal only)")
    inv["B4_ledger_first_public_render_only"] = {
        "pass": not v, "violations": v,
        "note": "input-side home; render R1-R3 verified at render"}
    # B5 — named check home: hidden metrics_internal winprob is never
    # imported into the scoring/render path. A winprob/metrics_internal
    # KEY carrying a numeric value anywhere in book or ledger is an
    # import; string mentions (the boundary note itself) are not.
    v = []
    for root_name, root in (("book", book or {}),
                            ("ledger", ledger_events)):
        for path, key, val in _walk(root):
            if key.lower() in ("winprob", "win_prob",
                               "metrics_internal") and isinstance(
                                   val, (int, float)):
                v.append(f"{root_name}:{path} carries numeric "
                         f"{key}={val} (B5 import)")
            if key.lower() == "metrics_internal" and isinstance(
                    val, dict) and any(
                        isinstance(x, (int, float))
                        for x in val.values()):
                v.append(f"{root_name}:{path} carries numeric "
                         f"metrics_internal values (B5 import)")
    inv["B5_hidden_winprob_never_imported"] = {
        "pass": not v, "violations": v}
    # F1 — §6.1 forecast-timing invariant: forecasts valid only
    # pre-outcome (position ts < knowable ts). A position at/after
    # its subject's knowable instant is invalid and unscored
    # (fail-closed). Knowable NOT_ESTABLISHED => listed, not failed:
    # the outcome is an event, not a date, and no settlement exists
    # to be post-outcome against.
    v, ne, invalid = [], [], set()
    by_subject = {s.get("id"): s for s in subjects}
    for p in positions:
        subj = by_subject.get(p.get("subject_id"))
        if subj is None:
            continue
        kts = knowable_ts(subj, ledger_events)
        pts = position_ts(p, ledger_events)
        if kts is None:
            ne.append(f"{p.get('position_id')}: knowable ts "
                      f"NOT_ESTABLISHED for {subj.get('id')}")
            continue
        if pts is None:
            v.append(f"{p.get('position_id')}: no position ts "
                     f"(fail-closed: cannot prove pre-outcome)")
            invalid.add(p.get("position_id"))
            continue
        if pts >= kts:
            v.append(f"{p.get('position_id')}: opened {pts.isoformat()} "
                     f">= knowable {kts.isoformat()} — post-outcome, "
                     f"invalid, unscored")
            invalid.add(p.get("position_id"))
    inv["F1_forecast_timing_pre_outcome"] = {
        "pass": not v, "violations": v, "not_established": ne}
    return inv, invalid

def binary_outcome(settle_value):
    """Map a settled value to 1/0 when it is an unambiguous binary token; else None."""
    t = str(settle_value).strip().lower()
    if t in ("y", "yes", "true", "1", "landed", "hit"):
        return 1
    if t in ("n", "no", "false", "0", "missed"):
        return 0
    return None

def main(argv):
    if len(argv) < 3:
        print(__doc__); return 2
    book_path, ledger_path = argv[1], argv[2]
    out_path = None
    if "--out" in argv:
        out_path = argv[argv.index("--out") + 1]
    book = load_book(book_path)
    events = load_ledger(ledger_path)
    subjects = book.get("subjects", [])
    positions = book.get("positions", [])
    invariants, invalid_ids = validate(subjects, positions, events,
                                       book)

    settled = {s["id"]: s for s in subjects if (s.get("settle") or {}).get("value") is not None}
    settlements = [{"subject_id": s["id"], "value": s["settle"]["value"],
                    "source": s["settle"].get("source"), "record_of_record": s.get("record_of_record")}
                   for s in subjects if s["id"] in settled]

    scores, not_scored, scored_n, scored_subjects = {}, [], 0, set()
    abstentions = []
    per_issuer = {}
    for p in positions:
        pid = p.get("position_id")
        if pid in invalid_ids:
            not_scored.append({"position_id": pid, "reason": "INVALID — F1 forecast-timing violation (post-outcome or unprovable), unscored"})
            continue
        subj = settled.get(p.get("subject_id"))
        if subj is None:
            not_scored.append({"position_id": pid, "reason": "subject unresolved — no settlement from record of record yet"})
            continue
        prob = None
        for k in ("p", "probability", "forecast_p"):
            if isinstance(p.get(k), (int, float)):
                prob = float(p[k]); break
        if prob is None:
            not_scored.append({"position_id": pid, "reason": "NOT_SCORED — no explicit pre-lock p (stake never implies a probability)"})
            continue
        if prob == 0.5:
            # F3: p = 0.5 exactly is abstention-shaped (no directional
            # call) — a separate count, excluded from N (§6.3).
            abstentions.append(pid)
            not_scored.append({"position_id": pid, "reason": "ABSTAIN — p = 0.5 exactly (abstention-shaped, no directional call)"})
            continue
        o = binary_outcome(subj["settle"]["value"])
        if o is None:
            not_scored.append({"position_id": pid, "reason": "settled value is not an unambiguous binary token; multicategory form NOT_ESTABLISHED in skeleton"})
            continue
        agg = per_issuer.setdefault(p.get("gambler") or "NOT_ESTABLISHED", {"brier_sum": 0.0, "calls": 0, "correct": 0, "subjects": set()})
        agg["brier_sum"] += (prob - o) ** 2
        agg["calls"] += 1
        agg["correct"] += 1 if (prob > 0.5) == (o == 1) else 0
        agg["subjects"].add(p.get("subject_id"))
        scored_n += 1; scored_subjects.add(p.get("subject_id"))
    for issuer, a in per_issuer.items():
        scores[issuer] = {"n_resolved": a["calls"], "distinct_subjects": len(a["subjects"]),
                          "mean_brier": a["brier_sum"] / a["calls"], "hit_rate": a["correct"] / a["calls"]}
    ranking = "RANKED" if (scored_n >= RANKING_GATE_N and len(scored_subjects) >= RANKING_GATE_SUBJECTS) else "UNRANKED / INSUFFICIENT_N"

    report = {
        "schema": SCHEMA,
        "generated_from": {"book": book_path, "ledger": ledger_path, "ledger_events": len(events)},
        "subjects_checked": len(subjects),
        "positions_total": len(positions),
        "positions_open": sum(1 for p in positions if (p.get("status") or "").lower() == "open"),
        "settlements": settlements,
        "scores": scores,
        "abstentions": abstentions,
        "invalid_positions": sorted(x for x in invalid_ids if x),
        "not_scored": not_scored,
        "ranking": ranking,
        "coverage": {"opened": len(positions), "resolved": scored_n,
                     "ratio": (scored_n / len(positions)) if positions else None},
        "invariants": invariants,
    }
    text = json.dumps(report, indent=1)
    print(text)
    if out_path:
        pathlib.Path(out_path).write_text(text + "\n")
    failed = [k for k, v in invariants.items() if not v["pass"]]
    if failed:
        print(f"INVARIANT VIOLATIONS: {failed}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
