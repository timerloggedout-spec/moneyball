#!/usr/bin/env python3
"""MoneyBall cards feed generator — moneyball-cards-feed/v1 (DESIGN §2).

Pipeline: sources (read-only) -> generator -> data/cards-feed.json -> render (verbatim).
Identity = Registry moniker only (termux-monorepo/docs/ops/AGENT-MONIKERS.md).
Population v1: (a) lead SSOT table rows, (b) Fleet GitHub App function identity rows.
Every non-null stat carries a receipt; every null carries an honest state
(INTAKE / NOT_ESTABLISHED) — never 0, never estimated. Hidden internal
win-probability is never read, never emitted (B5).
Stdlib only. Usage:
  generate_cards_feed.py --monikers AGENT-MONIKERS.md --book-feed book-feed.json --out data/cards-feed.json
"""
import argparse, json, re, sys
from datetime import datetime, timezone

SCHEMA = "moneyball-cards-feed/v1"
REGISTRY_REF = "termux-monorepo/docs/ops/AGENT-MONIKERS.md"

def slugify(moniker):
    s = moniker.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s

def split_row(line, maxsplit):
    # line like: | a | b | c | rest... |
    body = line.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|"):
        body = body[:-1]
    return [c.strip() for c in body.split("|", maxsplit)]

def table_rows_after(lines, header_pred):
    """Yield rows of the first markdown table whose header satisfies header_pred."""
    for i, ln in enumerate(lines):
        if ln.strip().startswith("|") and header_pred(ln):
            j = i + 2  # skip separator row
            while j < len(lines) and lines[j].strip().startswith("|"):
                yield lines[j]
                j += 1
            return

def backticked(cell):
    m = re.search(r"`([^`]+)`", cell)
    return m.group(1) if m else None

def parse_graduations(text):
    """`v1` -> `v2` ... U = N attributed units  =>  {v1: (v2, U)}"""
    grads = {}
    pat = re.compile(r"`([A-Za-z0-9]+)`\s*→\s*`([A-Za-z0-9]+)`.*?U\s*=\s*([\d,]+)\s+attributed\s+units", re.S)
    for m in pat.finditer(text):
        grads[m.group(1)] = (m.group(2), int(m.group(3).replace(",", "")))
    return grads

def base_stats(book_feed):
    settlements = book_feed.get("settlements") or []
    resolved = len(settlements)
    return {
        "provenance_units": None,
        "landed_prs": None,
        "mirror_scores": None,
        "book": {
            "forecasts_issued": None,
            "brier": None,
            "hit_rate": None,
            "open_positions": None,
        },
        "subjects_active": None,
        "countdown_refs": None,
    }, {
        "provenance_units": "NOT_ESTABLISHED",
        "landed_prs": "NOT_ESTABLISHED",
        "mirror_scores": "NOT_ESTABLISHED",
        "book.forecasts_issued": "INTAKE" if resolved == 0 else "NOT_ESTABLISHED",
        "book.brier": "INTAKE" if resolved == 0 else "NOT_ESTABLISHED",
        "book.hit_rate": "INTAKE" if resolved == 0 else "NOT_ESTABLISHED",
        "book.open_positions": "NOT_ESTABLISHED",
        "subjects_active": "NOT_ESTABLISHED",
        "countdown_refs": "NOT_ESTABLISHED",
    }

MECHANICS_SOURCES = {
    "allocation_algorithm": "Speculators strategies registry (termux-monorepo experiments/speculators/token-strategies DESIGN.json, campaign token-strategies-1) — per-card records arrive via the Speculators-build source leg",
    "allocation_snapshot": "pool-scope-methods/v1 (termux-monorepo docs/ops/POOL-SCOPE-METHODS.md) — stampable only from a category-usage window with N>=30",
    "terms": "moneyball DESIGN S.11 (owner wagering-schema basis, 2026-11-03) — schema-level basis; per-agent recorded terms are the only renderable source",
}

def base_mechanics(mechanics_records, card_id, receipts):
    """Mechanics block (owner mechanics-publication leg, 2026-11-03).
    Cards rule binds every field: stat receipt OR null — no invented
    mechanics, no dressed defaults. A non-null value is emitted only from
    a mechanics record of record carrying its own receipt."""
    mech = {"allocation_algorithm": None, "allocation_snapshot": None, "terms": None}
    states = {
        "allocation_algorithm": "NOT_ESTABLISHED - no per-card allocation-algorithm record of record; the strategies registry covers campaign instances (6 strategies x 2 verifiers, factorial), not card agents",
        "allocation_snapshot": "NOT_ESTABLISHED - no category-usage window exists (campaign runs 0 executed); the pool-scope-methods/v1 N>=30 floor cannot be met, so no number is rendered",
        "terms": "NOT_ESTABLISHED - DESIGN S.11 records the schema-level basis only; no per-agent recorded change/sale/royalty terms exist",
    }
    rec = (mechanics_records or {}).get(card_id) or {}
    for field in mech:
        entry = rec.get(field)
        if entry and entry.get("value") is not None and entry.get("receipt"):
            mech[field] = entry["value"]
            states.pop(field, None)
            receipts.append({"field": f"mechanics.{field}", "type": "record", "ref": entry["receipt"]})
    return mech, states

def make_card(moniker_v1, moniker_v2, role, source, row_ref, grads, book_feed, generated_at, mechanics_records=None):
    stats, states = base_stats(book_feed)
    receipts = [{"field": "identity", "type": "feed", "ref": row_ref},
                {"field": "status", "type": "feed", "ref": row_ref}]
    mechanics, mechanics_states = base_mechanics(mechanics_records, slugify(moniker_v1), receipts)
    if moniker_v1 in grads:
        v2, units = grads[moniker_v1]
        moniker_v2 = v2
        stats["provenance_units"] = units
        states.pop("provenance_units", None)
        gref = f"{REGISTRY_REF}#graduations-of-record ({moniker_v1} -> {v2}, U={units}, counted 2026-11-01)"
        receipts.append({"field": "moniker_v2", "type": "feed", "ref": gref})
        receipts.append({"field": "provenance_units", "type": "feed", "ref": gref})
    return {
        "card_id": slugify(moniker_v1),
        "moniker_v1": moniker_v1,
        "moniker_v2": moniker_v2,
        "role": role,
        "source": source,
        "status": "INTAKE",
        "stats": stats,
        "stat_null_states": states,
        "mechanics": mechanics,
        "mechanics_null_states": mechanics_states,
        "snapshot_at": generated_at,
        "receipts": receipts,
    }

def validate(cards):
    errs, seen = [], set()
    for c in cards:
        if c["card_id"] in seen:
            errs.append(f"duplicate card_id {c['card_id']}")
        seen.add(c["card_id"])
        fields = {r["field"] for r in c["receipts"]}
        flat = {"provenance_units": c["stats"]["provenance_units"],
                "landed_prs": c["stats"]["landed_prs"],
                "mirror_scores": c["stats"]["mirror_scores"],
                "book.forecasts_issued": c["stats"]["book"]["forecasts_issued"],
                "book.brier": c["stats"]["book"]["brier"],
                "book.hit_rate": c["stats"]["book"]["hit_rate"],
                "book.open_positions": c["stats"]["book"]["open_positions"],
                "subjects_active": c["stats"]["subjects_active"],
                "countdown_refs": c["stats"]["countdown_refs"]}
        for name, v in flat.items():
            if v is not None and name not in fields and name.split(".")[-1] not in fields:
                errs.append(f"{c['card_id']}: stat {name} non-null without receipt")
            if v is None and name not in c["stat_null_states"]:
                errs.append(f"{c['card_id']}: stat {name} null without honest state")
        if c["moniker_v2"] is not None and "moniker_v2" not in fields:
            errs.append(f"{c['card_id']}: moniker_v2 without graduation receipt")
        for field, v in c["mechanics"].items():
            if v is not None and f"mechanics.{field}" not in fields:
                errs.append(f"{c['card_id']}: mechanics.{field} non-null without receipt")
            if v is None and field not in c["mechanics_null_states"]:
                errs.append(f"{c['card_id']}: mechanics.{field} null without honest state")
    return errs

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--monikers", required=True)
    ap.add_argument("--book-feed", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--mechanics", required=False, default=None,
                    help="optional JSON: per-card mechanics records of record, keyed by card_id; each field {value, receipt}")
    a = ap.parse_args()
    text = open(a.monikers, encoding="utf-8").read()
    lines = text.splitlines()
    book_feed = json.load(open(a.book_feed, encoding="utf-8"))
    mechanics_records = json.load(open(a.mechanics, encoding="utf-8")) if a.mechanics else {}
    if book_feed.get("schema") != "agentic-gambling-book-feed/v1":
        print(f"FATAL: unexpected book feed schema {book_feed.get('schema')!r}", file=sys.stderr); sys.exit(1)
    grads = parse_graduations(text)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    cards, skipped = [], []

    # (a) lead SSOT table
    for row in table_rows_after(lines, lambda l: "Role" in l and "Display moniker" in l):
        cells = split_row(row, 3)
        if len(cells) < 4 or cells[0] == "Role":
            continue
        role, disp, _trigger, notes = cells[0], cells[1], cells[2], cells[3]
        disp = backticked(disp)
        if not disp:
            continue
        v1, v2 = disp, None
        m = re.search(r"v2 graduated[^()]*\(v1 `([^`]+)`", notes)
        if m:
            v1 = m.group(1)
        cards.append(make_card(v1, v2, role, "ssot-lead",
                               f"{REGISTRY_REF}#ssot-lead row `{v1}`", grads, book_feed, generated_at, mechanics_records))

    # (b) Fleet GitHub App function identities
    for row in table_rows_after(lines, lambda l: "App (provisioning name)" in l):
        cells = split_row(row, 3)
        if len(cells) < 4 or cells[0].startswith("App "):
            continue
        app, disp = cells[0], cells[1]
        moniker = backticked(disp)
        if not moniker:
            skipped.append(f"{app}: no moniker issued in Registry -> no card (DESIGN §2.1)")
            continue
        card = make_card(moniker, None, app, "fleet-app",
                         f"{REGISTRY_REF}#fleet-app-identities row `{moniker}`", grads, book_feed, generated_at, mechanics_records)
        card["actor"] = backticked(cells[2]) or cells[2]
        cards.append(card)

    errs = validate(cards)
    blob = json.dumps(cards)
    if "win_prob" in blob or "winprob" in blob.lower().replace("win_prob", ""):
        errs.append("B5 violation: hidden internal metric present in feed")
    if errs:
        print("GENERATION FAILED (fail loud, previous feed stays served):")
        for e in errs: print(" -", e)
        sys.exit(1)
    feed = {
        "schema": SCHEMA,
        "generated_at": generated_at,
        "generator": "scripts/generate_cards_feed.py (moneyball repo, lane A)",
        "generator_run_id": f"local-{generated_at}",
        "sources": {
            "registry": REGISTRY_REF,
            "book_feed_schema": book_feed.get("schema"),
            "book_subjects": len(book_feed.get("subjects") or []),
            "book_settlements": len(book_feed.get("settlements") or []),
        },
        "population_scope": "v1: lead SSOT table + Fleet GitHub App function identities; lane-coordination monikers and 4n0n entrant identities are NOT card population (Registry boundary rules)",
        "mechanics_sources": MECHANICS_SOURCES,
        "mechanics_note": "Mechanics publication (owner leg 2026-11-03): every card carries a mechanics block; each field renders only from a record of record with its receipt, otherwise null with its honest state in mechanics_null_states.",
        "skipped": skipped,
        "cards": cards,
    }
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(feed, f, indent=1, ensure_ascii=False)
        f.write("\n")
    grad_count = sum(1 for c in cards if c["moniker_v2"])
    print(f"cards-feed ok: {len(cards)} cards, {grad_count} graduated (v2), {len(skipped)} skipped")
    for s in skipped: print(" - skipped:", s)

if __name__ == "__main__":
    main()
