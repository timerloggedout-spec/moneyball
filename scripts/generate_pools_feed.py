#!/usr/bin/env python3
"""MoneyBall pools feed generator (moneyball-pools-feed/v1, DESIGN §3).
Reads the site wallet-ledger (monorepo ops/agentic-gambling/site/wallet-ledger.jsonl)
+ cards feed; emits one pool entry per class=pool wallet. All values are
ledger folds with receipts — contributions/distributions/members counted
from events, never asserted. Usage:
  generate_pools_feed.py --ledger wallet-ledger.jsonl --cards cards-feed.json --out pools-feed.json"""
import argparse, json, sys
from pathlib import Path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", required=True); ap.add_argument("--cards", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    events = [json.loads(l) for l in Path(a.ledger).read_text().splitlines() if l.strip()]
    cards = {c["card_id"] for c in json.loads(Path(a.cards).read_text())["cards"]}
    pools = {}
    for ev in events:
        wid = ev["wallet_id"]
        if ev.get("type") == "wallet_provisioned" and ev.get("class") == "pool":
            if ev["card_ref"] not in cards:
                print(f"FAIL: pool {wid} references unknown card {ev['card_ref']}"); sys.exit(1)
            pools[wid] = {"pool_wallet_id": wid, "card_id": ev["card_ref"], "card_moniker": ev.get("card_moniker"),
                          "status": "provisioned", "styles": ev.get("styles"), "balance": 0,
                          "contributions_total": 0, "contributions_count": 0, "distributions_total": 0,
                          "members": [], "receipts": [{"type": "ledger", "ref": f"wallet-ledger.jsonl seq {ev['seq']}", "payload_hash": ev["receipt"]["payload_hash"]}]}
        if ev.get("type") == "pool_contribution" and ev.get("pool_wallet") in pools:
            p = pools[ev["pool_wallet"]]; p["contributions_total"] += ev.get("points_in", 0); p["contributions_count"] += 1
            if ev.get("member_wallet") not in p["members"]: p["members"].append(ev["member_wallet"])
        if ev.get("type") == "pool_distribution" and wid in pools:
            pools[wid]["distributions_total"] += abs(ev.get("delta", 0))
        if wid in pools:
            pools[wid]["balance"] += ev.get("delta", 0)
    for p in pools.values():
        p["members_count"] = len(p["members"])
    feed = {"schema": "moneyball-pools-feed/v1",
            "generated_from": {"ledger": "termux-monorepo/ops/agentic-gambling/site/wallet-ledger.jsonl", "ledger_events": len(events)},
            "pools": sorted(pools.values(), key=lambda p: p["pool_wallet_id"])}
    Path(a.out).write_text(json.dumps(feed, indent=1) + "\n")
    print(f"pools feed ok: {len(feed['pools'])} pools, contributions {sum(p['contributions_count'] for p in feed['pools'])}, balances {[p['balance'] for p in feed['pools']]}")

if __name__ == "__main__":
    main()
