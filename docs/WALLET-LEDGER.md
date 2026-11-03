# Wallet Ledger — `wallet-ledger/v1` Schema Spec

Lane B (settlement-first) build-ready spec for DESIGN §4.2. The ledger file itself lives in the
monorepo at `ops/agentic-gambling/site/wallet-ledger.jsonl` (beside the Book) when the wallet
layer is built — a later step. This repo carries this spec + the machine-readable event schema
at `scripts/settlement/wallet-ledger.schema.json`.

## Position vs the Book ledger

`wallet-ledger.jsonl` is NOT an extension of `book/ledger.jsonl`. The book ledger is the
low-frequency, audited settlement record (B1–B5 conformant); wallet events are high-frequency
balance movements. Mixing them would force a conformity re-audit per wallet event and let
balance bugs contaminate the settlement record. Either ledger verifies alone; they join by
reference only:

- wallet events carry `position_ref` → a book-ledger position (e.g. `POS-001`)
- book settlement events carry `settlement_ref` → wallet payout events (by `receipt_id`)

## Event shape (every line, append-only)

| Field | Type | Rule |
|---|---|---|
| `seq` | integer ≥ 1 | strictly increasing, gapless per file; assigned by the writer at append |
| `ts` | string (ISO 8601 instant + offset) | append time; never backdated |
| `event_type` | enum, §Event types | — |
| `wallet_id` | string | opaque, chain-agnostic (`paper:<hash>` pattern of record) |
| `delta` | number | signed points movement for this wallet; 0 allowed only for `wallet_provisioned` |
| `balance_after` | number | a CLAIM: recomputable as the fold of all `delta` for this wallet up to `seq`; mismatch = defect |
| `ref` | string | receipted reference for the movement (position, settlement, pool, cull record…) |
| `position_ref` | string \| null | book-ledger position this event belongs to, when any |
| `receipt` | object | `{receipt_id, payload_hash, prev_receipt_hash}` — hash chain, §Receipts |

Balances are a derived fold of events, never a mutable stored field. Stored balances anywhere
else (e.g. `WALLETS.json`) are snapshot caches only.

## Event types

| Type | When | Notes |
|---|---|---|
| `wallet_provisioned` | wallet created | `delta` = genesis grant (amount `NOT_ESTABLISHED`, owner-ruled pre-launch) or 0 |
| `faucet_issued` | periodic faucet | cadence/cap `NOT_ESTABLISHED`; finite, once per verified identity (G2 sybil rule) |
| `stake_escrowed` | position opens | `available → escrow` in the same wallet; requires `position_ref` + cited basis (B2 failure ⇒ the escrow is rejected, never appended) |
| `stake_released` | position void/cancelled pre-resolution | full escrow returns to available |
| `payout_credited` | book settlement lands | cites the book settlement via `ref`/`settlement_ref`; parimutuel per §4.3 |
| `pool_contribution` | member contributes to a pool wallet | records shares issued pro-rata at contribution-time NAV |
| `pool_distribution` | pool pays members after a pool position settles | pro-rata by shares held at settlement `seq` |
| `cull_transferred` | cull waterfall | balance moves to pooled-buckets in one paired event; culling never destroys value; the cull record names `{culled_participant, wallet_balance_at_cull, pool_destination}` |
| `adjustment` | correction only | cites the prior event it corrects (`ref` = that event's `receipt_id`); never an edit or delete — `x⁻¹` semantics in derived state |

## Receipts (hash chain)

Every event issues a receipt:

```json
"receipt": {
  "receipt_id": "wr_<seq>",
  "payload_hash": "sha256 of the canonical event payload (all fields except receipt)",
  "prev_receipt_hash": "payload_hash of seq-1, or GENESIS for seq 1"
}
```

The chain makes the file tamper-evident and independently verifiable today, off-chain.
A later on-chain/testnet anchoring leg (only after the separate legal + payments gate)
publishes `payload_hash` only; payloads stay in the ledger. Signature scheme / key custody =
`NOT_ESTABLISHED` (no keys exist; never invented).

## Validation

`scripts/settlement/wallet-ledger.schema.json` (JSON Schema) validates a single event's shape.
Fold-level checks (seq gapless, `balance_after` == fold, chain continuity) are writer/verifier
duties beyond per-event schema — verifier tooling is `NOT_ESTABLISHED` in this lane's slice.

## Cross-references of record

- DESIGN §4.2 (ledger decision), §4.3 (issuance/escrow/parimutuel payout), §4.4 (cull waterfall), §4.5 (web3 seams)
- Book ledger: `termux-monorepo/ops/agentic-gambling/book/ledger.jsonl`
- Wallet provisioning of record: `termux-monorepo/experiments/speculators/token-strategies/WALLETS.json` (`speculators-wallets/v1`, 12 paper|test wallets)
