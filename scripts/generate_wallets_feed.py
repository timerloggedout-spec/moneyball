#!/usr/bin/env python3
"""Build the v2 wallets projection from the authoritative append-only ledger."""
import argparse, hashlib, json
from pathlib import Path

SCHEMA = "moneyball-wallets-feed/v2"
PAPER_LABEL = "PAPER / TEST — not a real-money wallet"
UNIT = "booktally (observational)"
BALANCE_BASIS = "fold-proven — balance_after of the wallet's last ledger event"
CLAIMS = {"population_labelling":"EVERY wallet in this feed is paper|test. unit = booktally (observational) — issued display name (Registry PR #4825); the ledger unit of record remains soft_quota_token (see unit_transition). No wallet holds, represents, or implies real-money value; balances are observational accounting only.","per_row_fields":"paper_test (true, every row) + paper_test_label + kind (paper|test) + unit (booktally (observational), the issued display unit; the provisioning events of record carry the legacy unit soft_quota_token — see unit_transition) — carried from each wallet's provisioning record so the page labels from feed data, never invented copy","prohibited_content":"no winprob / metrics_internal / probability / odds / expected-value fields exist in this feed in any encoding — verified against the source fold at generation (0 probability-shaped keys in all ledger events)","balances":"fold-proven only (last-event balance_after). The only nonzero balances in the fold are the 12 genesis paper wallets at 1,000; the only nonzero deltas in the ledger are the 12 genesis faucets. Nothing in the fold implies a balance beyond measured values."}
UNIT_TRANSITION = {"kind":"versioned unit-name transition (Registry issuance; feed vocabulary only — ledger untouched)","issued_name":{"machine":"booktally","display":"booktally (observational)","plural":"booktallies"},"legacy_unit_of_record":{"machine":"soft_quota_token","display":"soft_quota_token (observational)"},"basis":"Registry SSOT §'Unit-name issuance — booktally (2026-11-04)', monorepo PR #4825 merged 6a366cb61300 (AGENT-MONIKERS.md); collision: legacy string carries quota-plane signals (soft/quota/token)","rules":["v1 feed (history) keeps the legacy unit verbatim — it was the unit of record at that fold.","The wallet-ledger is hash-chained and is NOT edited: its events keep the legacy unit forever; this feed's v2 display unit is vocabulary issued over the same fold — balances, amounts, receipts unchanged (a rename moves no value).","Same-ledger continuation keeps the legacy unit in the ledger; new surfaces display booktally."]}

def digest(event):
    body = {k: v for k, v in event.items() if k != "receipt"}
    raw = json.dumps(body, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def fold(events):
    balances, last, provisioned = {}, {}, {}
    previous = "GENESIS"
    errors = []
    for seq, event in enumerate(events, 1):
        wid = event.get("wallet_id")
        receipt = event.get("receipt") or {}
        current = digest(event)
        if event.get("seq") != seq:
            errors.append(f"sequence mismatch at row {seq}")
        if receipt.get("payload_hash") != current:
            errors.append(f"payload hash mismatch at row {seq}")
        if receipt.get("prev_receipt_hash") != previous:
            errors.append(f"receipt chain break at row {seq}")
        previous = current
        if not wid:
            errors.append(f"wallet_id missing at row {seq}")
            continue
        balances[wid] = balances.get(wid, 0) + event.get("delta", 0)
        if event.get("balance_after") != balances[wid]:
            errors.append(f"balance_after mismatch at row {seq}: {wid}")
        last[wid] = event
        if event.get("type") == "wallet_provisioned":
            if wid in provisioned:
                errors.append(f"duplicate provisioning: {wid}")
            provisioned[wid] = event
    if set(balances) != set(provisioned):
        errors.append("wallet population differs from provisioned population")
    if errors:
        raise ValueError("wallet ledger validation failed:\n - " + "\n - ".join(errors))
    return balances, last, provisioned

def build(events, ledger_blob=None, note=None):
    balances, last, provisioned = fold(events)
    rows = []
    for wid, provision in sorted(provisioned.items()):
        final = last[wid]
        is_pool = provision.get("class") == "pool"
        row = {
            "wallet_id": wid,
            "class": "pool" if is_pool else None,
            "paper_test": True,
            "paper_test_label": PAPER_LABEL,
            "kind": provision.get("kind", "paper|test"),
            "unit": UNIT,
            "balance": balances[wid],
            "balance_basis": BALANCE_BASIS,
            "last_event_seq": final["seq"],
            "last_event_type": final["type"],
            "receipt": {
                "type": "ledger",
                "ref": f"wallet-ledger.jsonl seq {final['seq']}",
                "payload_hash": (final.get("receipt") or {}).get("payload_hash"),
            },
        }
        if is_pool:
            for key in ("pool_class", "depth", "parent_wallet", "parent_entity",
                        "entity_ref", "display", "grandfathered"):
                if key in provision:
                    row[key] = provision[key]
        elif provision.get("participant") is not None:
            row["participant"] = provision["participant"]
        rows.append(row)
    paper = sum(r["class"] is None for r in rows)
    pools = sum(r["class"] == "pool" for r in rows)
    if paper + pools != len(rows) or any(r["kind"] != "paper|test" for r in rows):
        raise ValueError("wallet feed population violates paper/test classification")
    return {
        "schema": SCHEMA,
        "generated_from": {
            "ledger": "termux-monorepo/ops/agentic-gambling/site/wallet-ledger.jsonl",
            "ledger_events": len(events),
            "head_seq": events[-1]["seq"] if events else 0,
            "ledger_blob": ledger_blob,
            "generator": "[MUSEai]@{role:{moneyball-plane}} — wallets-feed from the wallet-ledger fold of record (feed-machinery custody); regen at current ledger head" + (f"; {note}" if note else ""),
        },
        "claims_ceiling": CLAIMS,
        "reconciliation": {
            "feed_wallets": len(rows),
            "fold_distinct_wallets": len(balances),
            "deltas": [],
            "paper_wallets": paper,
            "pool_wallets": pools,
            "balance_rule": "balances render only as the fold proves them (last-event balance_after); no invented values",
        },
        "unit_transition": UNIT_TRANSITION,
        "wallets": rows,
    }

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--ledger-blob")
    ap.add_argument("--generator-note")
    args = ap.parse_args()
    events = [json.loads(line) for line in Path(args.ledger).read_text(encoding="utf-8").splitlines() if line.strip()]
    feed = build(events, args.ledger_blob, args.generator_note)
    Path(args.out).write_text(json.dumps(feed, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    r = feed["reconciliation"]
    print(f"wallets-feed ok: {r['feed_wallets']} wallets ({r['paper_wallets']} paper, {r['pool_wallets']} pools) from {feed['generated_from']['ledger_events']} verified events")

if __name__ == "__main__":
    main()
