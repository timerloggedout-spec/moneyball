# Feed automation

MoneyBall publishes deterministic projections of source records held in
`timerloggedout-spec/termux-monorepo`. The source repository remains the
record of authority; this repository stores render-ready projections.

## Refresh cadence

`.github/workflows/book-feed-refresh.yml` runs every 15 minutes, accepts
manual `workflow_dispatch`, and accepts the repository-dispatch events
`book-feed-changed`, `cards-feed-changed`, `wallets-feed-changed`,\n`pools-feed-changed`, and `proposals-feed-changed`.

The scheduled run provides the automatic refresh path. The repository
currently has no webhook delivery configured for the MoneyBall App, and
the App profile records an installation scoped to the MoneyBall repository.
The event receiver is ready; upstream event delivery remains a separate
owner-approved integration. The polling cadence keeps feeds current while
preserving the App's repository-only credential boundary.

## Source-to-feed map

| Projection | Source | Derivation |
|---|---|---|
| `book-feed.json` | Monorepo Book publication feed | Verbatim mirror |
| `cards-feed.json` | `docs/ops/AGENT-MONIKERS.md` + Book feed | Registry identities and receipt-backed/null-state card records |
| `wallets-feed.json` | `ops/agentic-gambling/site/wallet-ledger.jsonl` | Verified append-only fold; last-event balances and receipts |
| `pools-feed.json` | Wallet ledger | Pool provisioning events and fold-proven balances |
| `proposals-feed.json` | Local proposal store + append-only proposal receipt chain | Chain-verified projection |

## Wallet projection guarantees

`scripts/generate_wallets_feed.py` validates sequence continuity,
SHA-256 payload receipts, previous-receipt links, and each
`balance_after` against the running fold. It derives one row per
provisioned wallet and checks the resulting paper/test population.
The display unit follows the Registry-issued `booktally (observational)`
vocabulary while preserving the ledger's historical unit and receipt bytes.

`validate-feeds.yml` downloads the current authoritative ledger and its
verifier, verifies the chain, regenerates the wallets projection, and
compares every wallet row, reconciliation count, claims ceiling, unit
transition, and source blob with the published feed.

## Publication identity

The refresh workflow mints a short-lived installation token for
`termux-fleet-moneyball[bot]` using the MoneyBall App credentials stored
in this repository's Actions configuration. The token receives the
contents and pull-request permissions required for a maintained review
PR. Feed refreshes publish through `automation/feed-refresh`; the
workflow's PR is the review boundary before `main` changes.

The refresh workflow uses the specialist App token for repository writes.
The source ledgers remain read-only inputs, and the Book ledger is never
rewritten by feed generation.
