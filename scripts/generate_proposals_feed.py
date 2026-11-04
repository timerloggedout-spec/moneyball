#!/usr/bin/env python3
"""MoneyBall proposals feed generator
(moneyball-proposals-feed/v1, DESIGN §13.5).

Folds the proposal store + the receipt chain (the proposal
log) into the surface feed. The feed renders proposals
VERBATIM — the object, its Q&A record, its stamp, its exit —
and computes nothing about them (B4/R1). The chain is
verified before folding: an invalid chain fails the build
loud, never a quietly partial feed.

Claims ceiling (§13.5, carried on the feed itself):
paper/test labelling · existence-only while quarantined ·
no odds, no implied probability, no probability field
anywhere · a proposal is not a position and the feed offers
no entry path (R3).

Usage:
  generate_proposals_feed.py [--home data] [--out PATH]
"""
import argparse
import importlib.util
import json
from collections import Counter
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "proposals", Path(__file__).resolve().parent
    / "proposals.py")
P = importlib.util.module_from_spec(spec)
spec.loader.exec_module(P)

CLAIMS_CEILING = {
    "labelling": "PAPER / TEST — proposals are stage-0 "
                 "decision objects: they create no position, "
                 "move no balance, and score nothing.",
    "quarantine_rendering": "existence-only while QUARANTINED "
                            "or IN_Q&A — state and counts, no "
                            "outcome framing (Q1).",
    "probability_rail": "no probability is elicited, "
                        "collected, stored, or rendered "
                        "anywhere in this feed (Q1/B5).",
    "entry_path": "none — a proposal is not a position; "
                  "this feed offers no entry path (R3).",
}


def build(home: Path) -> dict:
    P.HOME = home
    rows = P.read_log()
    if not P.verify_chain(rows):
        raise SystemExit("proposal log chain INVALID — "
                         "refusing to fold a gapped chain")
    store = home / "proposals"
    proposals = []
    for f in sorted(store.glob("*.json")):
        if f.name.endswith(".qa.json"):
            continue
        obj = json.loads(f.read_text())
        pid = obj["proposal_id"]
        proposals.append({
            "proposal": obj,
            "qa": P.load_qa(pid),
            "receipts": [r for r in rows
                         if r["proposal_id"] == pid],
        })
    by_state = Counter(p["proposal"]["state"]
                       for p in proposals)
    by_class = Counter(
        p["proposal"]["exit"]["class"] for p in proposals
        if p["proposal"].get("exit"))
    return {
        "schema": "moneyball-proposals-feed/v1",
        "generated_at": P.now(),
        "generator": "scripts/generate_proposals_feed.py "
                     "(DESIGN §13.5)",
        "claims_ceiling": CLAIMS_CEILING,
        "counts": {"proposals": len(proposals),
                   "by_state": dict(sorted(by_state.items())),
                   "none_by_class":
                       dict(sorted(by_class.items()))},
        "chain": {"receipts": len(rows),
                  "head_hash": rows[-1]["hash"] if rows
                  else "GENESIS",
                  "valid": True},
        "proposals": proposals,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--home", default=None)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    root = Path(__file__).resolve().parent.parent
    home = Path(a.home) if a.home else root / "data"
    out = Path(a.out) if a.out else home / "proposals-feed.json"
    feed = build(home)
    out.write_text(json.dumps(feed, indent=1) + "\n")
    print(f"proposals feed: {feed['counts']['proposals']} "
          f"proposals · {feed['chain']['receipts']} receipts "
          f"· chain valid → {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
