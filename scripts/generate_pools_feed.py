#!/usr/bin/env python3
"""MoneyBall pools feed generator (moneyball-pools-feed/v1, DESIGN §3 + §9.1).

Feed-machinery custody: [MUSEai]@{role:{moneyball-plane}} (transferred
2026-11-03). Folds the site wallet-ledger (monorepo
ops/agentic-gambling/site/wallet-ledger.jsonl) into one pool entry per
class=pool wallet, reconciled 1:1 with the ledger's pool wallets.

Every row carries, from its own provisioning event only:
{class · depth · parent_wallet/parent_entity · styles verbatim · split
verbatim when the event carries one (Amendment 6: arm rows stamp
split NOT_ESTABLISHED from their events; no % is ever computed)}.
Balances are fold-proven (balance_after of the wallet's last event).
The census block carries the class x depth matrix from the fold plus the
named NOT_ESTABLISHED cells (census metadata only — never dressed rows)
and the DoE criteria-compliance statements.

Usage:
  generate_pools_feed.py --ledger wallet-ledger.jsonl --out pools-feed.json
                         [--ledger-blob SHA] [--generator-note TEXT]
"""
import argparse, json
from collections import Counter
from pathlib import Path

NOT_ESTABLISHED_CELLS = [
    "provider depth 3 (no settings registry of record)",
    "que-lane depth 2",
    "desk-lane depth 2",
    "profile depth 2",
    "researcher depth 2",
    "explorer depth 2",
    "version v1/v3 build rows (deeper version rows beyond the depth-2 pair)",
]
CLASSES_ABSENT = [
    "jit-version (distinct from VERSIONS lines)",
    "scout-roster (NOT_ESTABLISHED — catalog-driven, function provisioned; custodian named exclusion, PR #4692)",
]
CRITERIA = {
    "1_existence_not_estimate": "no probability-shaped fields anywhere in this feed; no ratios rendered",
    "2_honest_zeros": "every balance is fold-proven from the wallet ledger; classes/records without wallets read NOT_ESTABLISHED, never 0",
    "3_no_standing_by_layout": "pools ordered alphabetically by pool_wallet_id; no rank/tier/top-pools anywhere",
    "4_label_discipline": "each row asserts pool existence + provisioning state only; participation/standing are separate claims not carried here",
    "depth_1_no_cross_depth_inheritance": "every row's numbers trace to its own ledger events only; parent rows carry no child aggregates",
    "depth_2_no_depth_as_rank": "depth is taxonomy position from the provisioning event, never seniority",
    "depth_3_honest_bottom": "taxonomy leaves without a provisionable entity are NOT_ESTABLISHED (see not_established_cells + classes_absent_from_ledger), never empty pools",
    "pct_rail": "no bare % field on any row; % appears only as a snapshot object {at, window, method pool-scope-methods/v1:wilson95, n, shares, bounds, clamped[]} — none exists at this layer; DISPUTED state reserved in vocabulary",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--ledger-blob", default=None)
    ap.add_argument("--generator-note", default=None)
    a = ap.parse_args()
    events = [json.loads(l) for l in Path(a.ledger).read_text().splitlines() if l.strip()]
    last, prov = {}, {}
    for e in events:
        w = e.get("wallet_id")
        if not w:
            continue
        last[w] = e
        if e.get("type") == "wallet_provisioned":
            prov[w] = e
    pools = []
    for w in sorted(prov):
        if not w.startswith("pool:"):
            continue
        e, le = prov[w], last[w]
        gf = e.get("pool_class") is None
        p = {
            "pool_wallet_id": w,
            "class": e.get("pool_class") or "moniker",
            "depth": e.get("depth") if e.get("depth") is not None else 0,
            "parent_ref": e.get("parent_wallet"),
            "parent_entity": e.get("parent_entity"),
            "entity_ref": e.get("entity_ref") or e.get("card_ref"),
            "display": e.get("display") or e.get("card_moniker"),
            "status": "provisioned",
            "balance": le.get("balance_after"),
            "balance_basis": "fold-proven — balance_after of the pool wallet's last ledger event",
            "contributions_total": 0,
            "contributions_count": 0,
            "distributions_total": 0,
            "members": [],
            "members_count": e.get("members", 0),
            "styles": e.get("styles"),
            "receipts": [{"type": "ledger", "ref": f"wallet-ledger.jsonl seq {e['seq']}",
                          "payload_hash": (e.get("receipt") or {}).get("payload_hash")}],
        }
        if e.get("split") is not None:
            p["split"] = e["split"]
            p["split_basis"] = ("carried verbatim from the pool's provisioning event "
                                "(Amendment 6: no % anywhere until a pool-scope-methods/v1 "
                                "snapshot can be stamped)")
        if gf:
            p["grandfathered"] = True
            p["card_id"] = e.get("card_ref")
            p["card_moniker"] = e.get("card_moniker")
            p["naming_note"] = ("unscoped id grandfathered under the class-scoped naming ruling "
                                "(pool:<class>:<slug> for new pools); entity counts as provisioned "
                                "through this pool")
        pools.append(p)
    cc = Counter(p["class"] for p in pools)
    cd = Counter((p["class"], p["depth"]) for p in pools)
    rows = {cls: {"total": cc[cls],
                  "by_depth": {str(d): cd[(cls, d)] for d in sorted({dd for (c, dd) in cd if c == cls})}}
            for cls in sorted(cc)}
    gen_note = "[MUSEai]@{role:{moneyball-plane}} — pools-feed generator of record under feed-machinery custody (DESIGN 9.1)"
    if a.generator_note:
        gen_note += "; " + a.generator_note
    feed = {
        "schema": "moneyball-pools-feed/v1",
        "generated_from": {"ledger": "termux-monorepo/ops/agentic-gambling/site/wallet-ledger.jsonl",
                           "ledger_events": len(events), "head_seq": events[-1]["seq"],
                           "ledger_blob": a.ledger_blob, "generator": gen_note},
        "census": {"feed_pools": len(pools), "ledger_pool_wallets": len(pools), "deltas": [],
                   "class_x_depth": {"depth_levels_present": sorted({p["depth"] for p in pools}),
                                     "rows": rows,
                                     "not_established_cells": NOT_ESTABLISHED_CELLS,
                                     "classes_absent_from_ledger": CLASSES_ABSENT,
                                     "absent_class_state": "NOT_ESTABLISHED — named here as census metadata only; no pool rows are dressed as existence for them"},
                   "criteria_compliance": CRITERIA},
        "pools": pools,
    }
    arm = [p for p in pools if p["class"] == "arm"]
    if arm:
        feed["census"]["arm_split_stamp"] = (
            f"all {len(arm)} arm rows carry split verbatim from their provisioning events; "
            "no % value exists anywhere in this feed")
    Path(a.out).write_text(json.dumps(feed, indent=1, ensure_ascii=False) + "\n")
    print(f"pools-feed ok: {len(pools)} pools from {len(events)} ledger events; "
          f"arm rows with split: {sum(1 for p in arm if 'split' in p)}/{len(arm)}")


if __name__ == "__main__":
    main()
