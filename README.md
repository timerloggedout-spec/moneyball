# MoneyBall

Speculator markets over fleet outcomes — the public face + market layer of **The Book**.

## Charter

- **Markets** — Polymarket-shaped speculation over receipted fleet outcomes. Subjects originate in The Book (`timerloggedout-spec/termux-monorepo` → `ops/agentic-gambling/book/challenges-book.json`, 26 subjects at founding) and widen from there: challenge landings/placements, milestones, and QUE measurement-plane drain outcomes as forecastable subjects.
- **Agent trading cards** — fleet agent profiles rendered as trading cards from receipted records only: Registry monikers = card identities; stats = provenance units, landed PRs, mirror scores, book history. Every stat cites a receipt; uncited = absent, never estimated.
- **Group-ownership styled options** — cards carry fractional/group stakes (fantasy-pool shape): styled options over card performance, settled from receipts, never from assertion.
- **The Book stays the record** — this repo is its public face + market layer. Ledger of record remains the append-only book ledger in termux-monorepo; settlement happens only from each subject's named record of record.

## Rails

- **Paper/test first** — points-class speculation, receipted, on the provisioned paper|test wallets (`speculators-wallets/v1`, unit `soft_quota_token`, observational). The points layer is complete without real money.
- **Real-money markets = a separate later gate** (legal + payments review). Nothing here pre-commits to a rail, a chain, a token, or custody.
- **The frozen trading lane (#407) is untouched** — this is the Book + speculation on fleet outcomes, not securities trading.
- **Scoring integrity = DoE/3L0 patterns** — forecasts recorded pre-outcome, scored Brier/hit-rate at resolution, nulls filed honestly (`INTAKE`/`NOT_ESTABLISHED`, never dressed as 0). Hidden `metrics_internal` win-probability is never republished.
- **Identity** — fleet actors write in this repo only as the repo's specialist GitHub App (AppID process lane, RepoStory pattern: contents/pull_requests/issues write + metadata read, this repo only). Never as `GITHUB_TOKEN`.

## Widening path

internal → public-read (verbatim, read-only, no entry path) → public paper-speculation. Each step is its own gate; see `docs/`.

## Serving

Deploy shape (Pages-from-repo vs Vercel) is decided in the design doc — repo first, deploy shape second.

## Docs

Design + specs live in [`docs/`](docs/). Founding design: site + market design (subjects · card schema · ownership model · settlement-from-receipts · widening path) — lands via proposal PR.
