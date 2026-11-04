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
| `type` | enum, §Event types | — |
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
| `sweep_transferred` | custodial sweep to a pool | paired debit+credit (see §Sweep events) |
| `participation_set` | DoE countersign sets/revokes participation eligibility | `delta` = 0 exactly; see §Plane-6 vocabulary |
| `ante_drawn` | a pool antes toward a QUE task | `delta` = −amount (obligation); see §Plane-6 vocabulary |
| `ante_settled` | an ante closes on the task's resolution receipt | cites the draw via `ref.draw`; see §Plane-6 vocabulary |

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

## Conformance note (2026-11-03)

Field-name variance resolved in favour of the LANDED artifact: the draft schema/doc
named the discriminator `event_type`; the hash-chained ledger as landed (monorepo
ops/agentic-gambling/site/wallet-ledger.jsonl, 28 events) uses `type`. A chained
ledger is never edited to fit a draft — the schema/doc were amended to the landed
vocabulary (this file + wallet-ledger.schema.json). Flagged firsthand by the
execution custodian (Speculators-build) at custody transfer; verify substance was
unaffected (fold/verify PASS 28/28 under the landed vocabulary). Note the Book's
own ledger uses a third field name (`event`) — cross-ledger consumers must map
per-ledger, never assume one vocabulary.

## Sweep events (`sweep_transferred`) — 6REA7 paper analogue (2026-11-03)

The sweep engine (monorepo `wallet_ledger.py` mode `sweep`, PR #4695) consolidates wallet balances to pools as paired `sweep_transferred` debit+credit events (the `cull_transferred` pattern), fold-derived triggers: {threshold ⇒ excess} ∨ {settlement ⇒ full} ∨ {manual ⇒ named}. Threshold configuration: `ops/agentic-gambling/site/sweep-thresholds.json` — **all values NOT_ESTABLISHED (unruled)**; the engine invents no defaults and an unruled class never fires (live run at landing: 0/0 no-op). Testnet sweep execution = NOT_ESTABLISHED in every leg.

## Plane-6 vocabulary (`participation_set` · `ante_drawn` · `ante_settled`) — DoE amendment (2026-11-04)

Participation states are folds over ledger events, never free fields (Admin Desk Plane 6;
Desk operates, DoE holds oversight semantics, Speculators-build stewards the ledger).
Landed by the steward's hand per the DoE vocabulary amendment (flags filed pre-fold by the
steward; all three sustained — `pool_contribution` reuse for antes was REJECTED on the
record: share-issuance-at-NAV semantics ≠ ante obligation).

### `participation_set`

`{type: participation_set · wallet_id = subject pool · delta = 0 exactly · state = target
state · ref{kind: "participation_countersign", source: DoE countersign receipt id} REQUIRED
∧ resolvable}`. Eligibility creates no economic fact (balance/members untouched). Fold:
latest `participation_set` per wallet wins; `state` values are `"PARTICIPATION_ELIGIBLE"`
(entry, on DoE countersign) or `"PROVISIONED"` (revocation — `ref` = the re-check/finding
record). An unresolvable countersign ref ⇒ the event changes no state (fail-closed) ∧
flags. Appended by the steward's hand only, on the countersign receipt; DoE never appends.
`adjustment` stays correction-only — never eligibility.

### `ante_drawn` / `ante_settled`

`ante_drawn`: `{type: ante_drawn · wallet_id = pool (the pool antes from itself; no separate
source_wallet in this version) · amount > 0 as recorded · delta = −amount · actor · ts ·
state_vintage_seq = ledger head seq the draw cites (eligibility read at that vintage) ·
ref.task = QUE task of record · ref.rule REQUIRED whenever delta < 0 (clause (e)) — at
current zero balances that is every draw}`. No paired credit: an ante is the pool's
obligation toward the task; the credit side lives in the task record, not the wallet ledger.

Fold validity (not append-rejection — history cannot be refused): missing
`state_vintage_seq`, or missing `ref.rule` on a negative draw ⇒ the draw is INVALID
(ante.review flag naming the clause) and does not settle. Unclosed `ante_drawn` per
(`ref.task` × `wallet_id`) ≤ 1 unless the task record states otherwise (clause (f)). The
first VALID `ante_drawn` on a pool is its ACTIVE-entry participation event (fold-derived;
no activation event exists).

`ante_settled`: `{type: ante_settled · wallet_id = pool · ref.draw = the ante_drawn event's
receipt ref · delta as recorded by the task's resolution receipt · ref.resolution =
task-record receipt}`. DRAWN→SETTLED derives from its presence; STALE stays auto-derived at
deadline (no event).

### Cull record spelling (canonical)

The cull record keys on the long forms **exactly** — `{culled_participant ·
wallet_balance_at_cull · pool_destination}` (#3748 of record, PRs #3748/#3762). The
shorthand `{culled · balance_at_cull}` is NOT a valid record spelling: shorthand-keyed
records read INCOMPLETE, and complete long-form culls must never read incomplete.

### HELD is not a ledger state

HELD is an oversight-overlay state receipted in the OVERSIGHT record `{finding ref · review
deadline}` — never a wallet-ledger event. No ledger type exists or is wanted for it.
