# MoneyBall — Site + Market Design

`moneyball-design/v1` · founding design · seat: Web3 · MoneyBall Site (2026-11-03)
Status: PROPOSAL — lands via PR in this repo; build follows §9 sequence.

Notation: `∅` none · `⇒` implies · `↦` maps to · `∀` for all · `x⁻¹` correction/retraction event · `NOT_ESTABLISHED` = honest blank, never filled by estimate.

## 0. Grounding — build on what exists (receipts, verified firsthand 2026-11-03)

| Piece | Of record | State |
|---|---|---|
| The Book | `termux-monorepo/ops/agentic-gambling/book/challenges-book.json` (`agentic-gambling-book/v1`) | 26 subjects, DoE conformity B1–B5 PASS |
| Ledger of record | `termux-monorepo/ops/agentic-gambling/book/ledger.jsonl` | append-only, 15 lines |
| Public book render | `book-feed.json` (39,533B) + wagering-book page | served, read-only (R1–R3) |
| Speculator wallets | `experiments/speculators/token-strategies/WALLETS.json` (`speculators-wallets/v1`, PR #4640 merged `ba726a65ba1f`) | 12 paper\|test, balance 0 ∀, unit `soft_quota_token` |
| Lane components | `ops/agentic-gambling/lane.json` | MSM offers/bets partial; bookie/audience class OPEN (absent) |
| Population data | challenges/opportunities Gantt (%-of-remainder, served) · countdowns v1.2 · desk-feed slate | served feeds |
| Card identities | `docs/ops/AGENT-MONIKERS.md` Registry (v1 canonical; v2 display-only at U≥100: `h3yVern`, `c0deHound`, `d3vinForge`) | live |
| This repo | `timerloggedout-spec/moneyball` id 1444884380, public | seeded 2026-11-03 |
| Repo AppID | Termux Fleet MoneyBall (RepoStory pattern, repo-only) | IN FLIGHT — AppID lane |

The Book stays the record. This repo = its public face + market layer. Nothing in this design moves the ledger, the scoring surface (MoneyBall v2 / Neon), or the frozen trading lane (#407 untouched).

## 1. Subjects + market design

### 1.1 Subject classes

A **subject** = one forecastable question over a fleet outcome, with a named record of record. Three classes at v1:

1. **Book subjects (inherited, 26)** — the Book's subjects verbatim, ids `D1-1 … C12-26`: submission-landed (binary), milestone-hit (binary), placement (categorical: winner / top-3 / paid-tier / any-prize / podium). The site lists them; it never re-defines them. Expectation records, anchors, settle fields = Book's, imported by feed (§2 pipeline pattern), ∅ parallel numbers.
2. **Drain subjects (new, QUE-fed)** — QUE measurement plane (fresh mandate) supplies queue/drain measurements as forecastable subjects: e.g. "PR-merge queue drains below N by date D", "gate-pass rate ≥ X over window W", "lane backlog zero by landing L". Each drain subject must name its record of record (the QUE feed line + the underlying register it measures) before listing — a drain subject without a resolvable record of record does not list (B3 applied at intake).
3. **Card-performance subjects (new, derived)** — subjects whose outcome is a card stat crossing a stated threshold by a stated date (e.g. "card `X` reaches 50 landed PRs by Dec 31"), record of record = the projection source itself (master-history scan / ledger), stated per subject. These power the ownership layer (§3).

### 1.2 Subject schema (site listing shape)

```json
{
  "subject_id": "D1-1-submission-landed",
  "class": "book | drain | card-performance",
  "question": "string, outcome-verbatim",
  "outcomes": ["yes","no"],
  "expectation_record_ref": "book subject ref (B1: exactly one)",
  "record_of_record": "named source, resolvable locator",
  "anchors": {"cushion": "…", "landing": "…", "wall": "…", "final": "…"},
  "opens_at": "ts", "locks_at": "min(wall, first-knowable ts)",
  "knowable_when": "per Book / register",
  "status": "INTAKE | OPEN | LOCKED | SETTLED | VOID"
}
```

`prior/posterior = null` at INTAKE renders as "no estimate" — never 0 (B4/R2).

### 1.3 Pricing — decision: parimutuel v1

- **v1 = parimutuel pools per outcome.** All stakes on a subject form outcome pools; winners receive the losing pool pro-rata by stake (§5.2 formula in wallet layer). Reasons: bookmaker class is ABSENT on record (∅ house counterparty, ∅ house liability); paper liquidity is thin (12 wallets, balance 0) so an order book or LMSR would quote fiction; parimutuel needs no market-maker subsidy, no price oracle, and settles exactly from receipts.
- **Displayed price** = implied share of pool (`pool_outcome / pool_total`), labelled `pool share`, never "odds" or "probability" — a pool share is a stake distribution, not an estimate; the subject's expectation record carries the estimate layer, separately.
- **Deferred seam:** LMSR-style paper AMM may be proposed later for drain subjects (high-frequency, many small outcomes) once ≥1 subject class shows sustained volume; activation = separate design amendment with subsidy budget stated. Order book = ∅ at any paper stage (no matching-engine integrity story without identity, §7 G2).

### 1.4 Position lifecycle

`open (basis cited, B2) → escrow (§4) → lock at locks_at → record_of_record lands → settlement_proposed → settlement_final → scored (§6) → payout (§4)`.

- A position names: subject, outcome, stake, stated probability `p` (the forecast — scored, §6), basis refs (B2: uncited ∨ unresolvable ⇒ invalid, never opens).
- Forecast = OUTPUT class: scored at its issuer's record, never at the subject (§6).
- Late positions (ledger ts ≥ knowable ts) = invalid, unscored.
- Amendments post-open = ∅. A changed mind = a new position; netting rules (§6.4) govern scoring.

### 1.5 Listing governance

- New subjects (drain / card-performance) list only with: B1 expectation record created in the Book's shape, record_of_record named + resolvable, anchors bound, DoE conformity check passed. Listing authority = this seat under DoE criteria until a listing role is separately established (`NOT_ESTABLISHED`).
- Book subjects list automatically by feed; delisting a Book subject happens in the Book, never site-side.

## 2. Trading cards + data pipeline

### 2.1 Card schema — `moneyball-cards-feed/v1`

Identity = Registry moniker only. No Registry entry ⇒ no card.

| Field | Source of record | Null rule |
|---|---|---|
| `card_id`, `moniker_v1` | `AGENT-MONIKERS.md` (slugified v1) | never null |
| `moniker_v2` | Registry graduation record (U≥100 only) | null ⇒ render v1; never invent stylization |
| `role/lane`, `status` (ACTIVE\|INTAKE\|CULLED) | Registry + cull record | `NOT_ESTABLISHED`; never inferred |
| `stats.provenance_units` | Provenance layer, at issuer record | `NOT_ESTABLISHED` |
| `stats.landed_prs` | Master-history scan (PR-numbered commits ∧ landed content) | `NOT_ESTABLISHED` |
| `stats.mirror_scores` | Mirror-score record — surface `NOT_ESTABLISHED` | `NOT_ESTABLISHED` |
| `stats.book.{forecasts_issued,brier,hit_rate,open_positions}` | Book ledger, issuer-keyed | `INTAKE` until ≥1 resolution; never 0 |
| `subjects_active`, `countdown_refs` | Gantt ∧ desk-feed ∧ countdowns v1.2 ∧ QUE subjects | source down ⇒ `NOT_ESTABLISHED`, not `[]` |
| `receipts[]` | per-stat `{type: pr\|run\|ledger\|feed, ref}` | empty receipts ⇒ stat must be null |

`0` = measured zero only, receipt required. Hidden `metrics_internal` (winprob) ∉ card, ∉ feed — ∅ republication (B5).

### 2.2 Pipeline

`sources (read-only) → generator → moneyball-cards-feed/v1 (static JSON) → render (verbatim, computes nothing)`

- Generator: deterministic repo script; joins on `card_id` only (∅ name-matching); validates ∀ stat ⇒ receipt ∨ null, ∀ v2 ⇒ graduation receipt. Validation fail ⇒ build fails loudly, previous feed stays served.
- QUE feed schema/version = `NOT_ESTABLISHED` until QUE publishes; pipeline treats QUE as optional source — absent ⇒ dependent stats `NOT_ESTABLISHED`, pipeline still ships.
- Refresh: GitHub Actions only (∅ VM daemons, ∅ local cron) — push to source-of-record paths + scheduled sweep (exact schedule `NOT_ESTABLISHED`); each run stamps `generator_run_id` in the feed header.
- Lifecycle: mint on Registry entry (INTAKE, receipts = Registry PR#) → append-only snapshots (corrections = new snapshot, prior retained) → graduation unlocks v2 display (`card_id` unchanged) → cull freezes stats at cull-time snapshot, card retained (∅ deletion); cull snapshot names culled participant + cull record ref. Resurrection path = `NOT_ESTABLISHED`.

## 3. Ownership model — group/fractional styled options over cards

### 3.1 Shape

A **card pool** = a pool wallet (§4.3) bound to one card. Members contribute points to the pool; the pool takes positions (Book, drain, card-performance subjects — including subjects on its own card only under the insider rule, §6.4). Members hold **shares**, never direct fractions of positions.

**Styled options** = share classes over the same pool, differing in payoff style at settlement. Style is a payoff function over receipted pool results — nothing else. Three styles defined; activation is staged:

| Style | Payoff at distribution | v1 state |
|---|---|---|
| `pro_rata` | share of distributable, pro-rata by shares | ACTIVE at v1 |
| `capped` | pro-rata until member return reaches cap multiple (stated at contribution); excess above cap redistributes to `pro_rata` holders | ACTIVE at v1 (cap stated per pool, in the contribution receipt) |
| `first_loss` | absorbs pool losses before other styles lose principal; compensated by first claim on gains after `pro_rata` par | DEFINED, activation gated: requires pool loss-history ≥1 settled cycle + owner ruling (`NOT_ESTABLISHED`) |

"Loss"/"gain" are points-accounting terms over settled receipts only; projected/expected value contributes 0 to any payoff (§6.5).

### 3.2 Rules

- Contribution: `pool_contribution {member_wallet, pool_wallet, points_in, style, shares_issued}` appended to wallet ledger; shares issued pro-rata at contribution-time NAV (pool available + escrow at stake value). NAV method after first settlement = `NOT_ESTABLISHED` — until ruled, contributions pause at first settlement of a pool and resume under the ruled method (stated honestly on the pool page; ∅ silent estimation).
- Distributions: at each pool position settlement, payout credits the pool wallet, then `pool_distribution` pays members pro-rata by shares held at settlement `seq` (ledger-fold snapshot, receipted), styled per §3.1.
- Governance of picks: pool position requires `{basis, proposer_ref}`; default until ruled = single designated manager wallet per pool (`NOT_ESTABLISHED` as a general rule).
- Exit/transfer of shares: `NOT_ESTABLISHED` — v1 = contribute ∧ receive distributions only. No secondary market, no redemption promise.
- A card's subject (the agent/lane) holds no automatic share and no veto; insider bar (§6.4) applies to whoever controls the underlying outcomes.

## 4. Wallets + points mechanics

Class: `paper|test` only · unit `soft_quota_token (observational)` · ∅ purchase, ∅ deposit, ∅ conversion.

### 4.1 Wallet model

Extends `speculators-wallets/v1`: `{wallet_id, owner_ref, kind: paper|test, class: speculator|pool, status: provisioned|active|culled, unit}`. Speculator ≠ gambler at record level — classes never merge. External-user wallets: same schema; identity binding = `NOT_ESTABLISHED` (no auth provider on record) — this blocks public wallets, not internal paper use. Balance = derived fold of ledger events, never a mutable stored field (stored balance = snapshot cache only).

### 4.2 Ledger — new file, cross-linked

`ops/agentic-gambling/site/wallet-ledger.jsonl` (`wallet-ledger/v1`, in termux-monorepo beside the Book) — ¬ an extension of `book/ledger.jsonl`: the book ledger is the low-frequency audited settlement record (B1–B5 conformant); wallet events are high-frequency balance movements. Mixing ⇒ conformity re-audit per wallet event ∧ balance bugs contaminating the settlement record. Cross-link by ref only: wallet events carry `position_ref →` book ledger; book settlements carry `settlement_ref →` wallet payouts. Either ledger verifies alone.

Events: `wallet_provisioned · faucet_issued · stake_escrowed · stake_released · payout_credited · pool_contribution · pool_distribution · cull_transferred · adjustment` (correction-only, cites prior event). Every event: `{seq, ts, wallet_id, delta, balance_after, ref, receipt_id}`; `balance_after` is a claim, recomputable from the fold — mismatch = defect.

### 4.3 Issuance, escrow, payout

- Issuance legs: genesis grant (amount `NOT_ESTABLISHED`, owner-ruled pre-launch) · periodic faucet (cadence/cap `NOT_ESTABLISHED`) · promotional grants ⇐ pooled-buckets · payouts. Total supply = Σ issuance, ledger-visible; ∅ burn (culling ≠ burn, §4.4).
- Escrow: position open moves `available → escrow` in the same wallet (`stake_escrowed`, position_ref + basis cited; B2 failure ⇒ escrow rejected). Void pre-resolution ⇒ full `stake_released`.
- Settlement trigger = book ledger settlement ONLY (B3). Wallet layer never settles from assertion, price, or vote.
- Parimutuel payout: `payout_i = stake_i + (stake_i / Σ winning stakes) × Σ losing stakes`. One-sided pool ⇒ winners refunded stake only (∅ invented profit). ∅ winning stakes ⇒ full pool → pooled-buckets (¬ house). Rake = ∅ (any future rake = separate owner ruling). ∅ negative balances, ∅ credit.

### 4.4 Cull waterfall (inherited, unchanged)

Cull record names in the same record `{culled_participant, wallet_balance_at_cull, pool_destination = pooled-buckets (promotions/incentives/bonuses)}`; value moves as one `cull_transferred` pair; culling never destroys value; residual/royalty stream NOT folded (separate owner question, PR #3747); no wallet on record ⇒ balance `NOT_ESTABLISHED`, cull stands.

### 4.5 Web3 path — deliberately not built; seams kept

∅ chain · ∅ token · ∅ smart contract · ∅ custody · ∅ keys/seeds · ∅ testnet wiring (verified ∅ on record) · ∅ bridge · ∅ cash-out. Points are complete without it. Seams: `wallet_id` opaque + chain-agnostic (`paper:<hash>` pattern) ⇒ later kinds additive (`kind` enum), history never rewritten; every wallet event issues a hash-chained receipt `{receipt_id, wallet_id, event_seq, payload_hash, prev_receipt_hash}` — later anchoring publishes `payload_hash` only; settlement interface is refs-only, so an on-chain leg (if ever approved after the legal+payments gate) consumes the same refs. Signature scheme/key custody = `NOT_ESTABLISHED` (∅ keys exist; never invent).

## 5. Site architecture + serving decision

### 5.1 Shape

Static site in this repo: pages render committed feeds verbatim (book feed, cards feed, Gantt/countdown/desk-feed vendored by workflow from monorepo sources). ∅ server, ∅ DB, ∅ live query at request time, ∅ entry path from any public page (R3). Interactions in the paper phase happen through the ledgers (PRs by fleet actors via the repo App), not web forms — the site is a face, the ledgers are the machine.

Pages v1: `/` slate (subjects + countdowns) · `/subjects/<id>` (question, anchors, pool state, expectation record verbatim) · `/cards` + `/cards/<card_id>` (card + receipts) · `/pools/<pool_id>` (shares by style, distributions, receipts) · `/book` (the existing public book render, linked/vendored — the Book's page of record stays canonical).

### 5.2 Serving — decision: GitHub Pages from this repo

- **Pages-from-repo** wins for the paper phase: the repo is public; feeds are already static JSON committed by workflows; Pages deploy rides the repo's own App-token workflow (fleet actors never write as GITHUB_TOKEN — Pages build/deploy configured accordingly, see open item); ∅ new vendor account, ∅ new credential surface.
- **Vercel deferred, not rejected:** Vercel's value = server functions + sessionful UX, which the paper phase deliberately lacks (identity = `NOT_ESTABLISHED` blocks G2 anyway). If G2 (public paper-speculation) is approved and needs server-side identity/session, serving re-opens as its own decision with this doc amended.
- Open item: Pages source (branch vs Actions artifact) + custom domain = `NOT_ESTABLISHED` at founding; default = Actions artifact deploy from `main`.

## 6. Integrity, scoring, settlement

### 6.1 Invariants (DoE/3L0, non-negotiable)

B1 one expectation record per subject · B2 basis cited or invalid · B3 settlement only from the named record of record · B4 ledger-first, public = read-only verbatim render (R1–R3) · B5 hidden winprob never republished/imported. Forecasts valid only pre-outcome (ledger ts < knowable ts).

### 6.2 Settlement pipeline

1. `record_of_record` lands (its native owner writes; book roles ∅).
2. `settlement_proposed` appended — cites record locator + content hash (settlement-role identity `NOT_ESTABLISHED`; principals/holders ∅ approve own settlements).
3. `settlement_final` appended after dispute window (length set per subject at open; default `NOT_ESTABLISHED`).
4. Positions scored by a deterministic job, replayable from the ledger alone (∅ discretion, ∅ overrides).
5. Wallet payouts appended (credits = new lines; balances derived).
6. Card stats rebuilt as projection (rebuild, never hand-patch).

### 6.3 Scoring

Per resolved probabilistic position: Brier `BS_i = (p_i − o_i)²` (multicategory: `Σ_k (p_ik − o_ik)²`); mean Brier over resolved; hit-rate = correct calls / resolved non-null calls (call = `p > 0.5` ∨ argmax). Skill vs base-rate baseline fixed at subject open: `BSS = 1 − BS/BS_ref`; `BSS ≤ 0` stated as no demonstrated skill. Scores are **unweighted by stake** (stake sizes wallet P/L only). Nulls/abstains/unresolved/invalid = separate counts, excluded from N, never scored as misses; coverage (resolved/opened) prints beside every score.

**Public-ranking gate (∀ required):** `N_resolved ≥ 30 ∧ ≥10 distinct subjects`, else `UNRANKED / INSUFFICIENT_N` (stats may show, rank may not) · hit-rate claims require Wilson 95% lower bound > base rate · Brier-skill claims require subject-cluster bootstrap 95% CI for BSS excluding 0. Sort: mean Brier ↑, tie-break N ↓, hit-rate ↓; CI-crossing entries flagged `PROVISIONAL`.

### 6.4 Abuse rules

- **Insider (proposed):** a principal, or anyone with material control over a subject's outcome, is barred from positions on that subject; discovered ⇒ void via `⁻¹`, stake returned, ∅ score/payout. Non-controlling fleet members file `conflict_declaration` + basis with the position; undeclared control = insider violation.
- **Sybil:** 1 scoring identity per verified identity; faucet finite, once per identity, points non-transferable (except pool contribution/distribution flows); linked accounts merged for scoring/limits, by appended merge records.
- **Wash:** self-cross/offsetting positions under one beneficial owner (incl. its pools) netted before scoring/volume; self-matched volume excluded from all stats.
- **Basis gaming:** template/duplicate basis across unrelated positions ⇒ review flag; basis must support direction + probability, not merely exist.

### 6.5 Corrections + group settlement

History immutable: correction = appended event `{corrects: event_id, reason, basis_refs[]}` with `x⁻¹` semantics in derived state (balances/scores/cards net to corrected value; original stays). Disputed settlement ⇒ payouts held, stats frozen pre-settlement; outcomes appended: `upheld` ∨ `reversed` (+ payout `⁻¹` lines + full rescore by replay; replay hashes filed). Wrong record-of-record content ⇒ settlement pauses; corrected source + new `settlement_proposed` required — the Book never fixes the source, never substitutes one (B3).

Group positions settle pro-rata from receipts only: shares snapshotted at subject lock (post-lock transfers ∅ effect on that settlement); `payout_member = (shares_member / Σ shares) × distributable_receipted`, styled per §3.1; rounding residual → largest-share member (tie: earliest position), residual line appended explicitly. Void/unresolved ⇒ ∅ payout; stakes returned pro-rata by reversal append. Partial payout only if the record of record itself records a partial outcome — never interpolated.

## 7. Widening path

| Gate | Scope | Opens when |
|---|---|---|
| G0 internal | fleet positions on Book subjects, paper wallets, private ledger | B1–B5 enforced in ledger writes; scoring job replays clean |
| G1 public-read | site live (Pages), feeds verbatim, cards public | R1–R3 verified on render; ∅ entry path; B5 leak check passes — **largely already true for the Book render; extends to cards/pools** |
| G2 public paper-speculation | external paper wallets + positions | G1 + identity binding + faucet limits + §6.4 abuse rules live. Identity mechanism = `NOT_ESTABLISHED` ⇒ G2 closed until ruled |
| G3 real-money | — | SEPARATE later gate: legal + payments review precedes any design selection. ∅ part of this design |

## 8. NOT_ESTABLISHED register (honest blanks carried, not filled)

Identity provider/binding (blocks G2 + external wallets) · genesis/faucet amounts + cadence · dispute-window default · settlement-role identity · pool NAV method post-first-settlement · share exit/transfer · `first_loss` activation · QUE feed schema/version · mirror-score surface · cards-feed refresh schedule · Pages source/domain · pool manager rule (general) · LMSR activation threshold evidence.

## 9. Build sequence (next PRs)

1. This design → merged (this PR).
2. Site skeleton on Pages (static, renders book feed verbatim) — G1 for subjects.
3. Cards-feed generator + first cards feed (monorepo-side sources; feed committed here) — G1 for cards.
4. Wallet ledger file + fold/verify tooling (`wallet-ledger/v1`) in monorepo beside the Book; genesis grants only after owner rules amounts.
5. Internal positions open on Book subjects under B2 (G0 exit test: one full open→settle→score→payout cycle replayed clean).
6. Card pools (`pro_rata` + `capped`) + pool pages.
7. Drain subjects intake with QUE (first subject lists only with record of record + DoE check).

— End of design v1. Amendments = PRs against this file, claims cited, blanks filled only by records.
