# MoneyBall — Site + Market Design

`moneyball-design/v1.1` · founding design, amended 2026-11-03 (market-design fold-in) · seat: Web3 · MoneyBall Site
Status: PROPOSAL — lands via PR in this repo; build follows §9 sequence.

Notation: `∅` none · `⇒` implies · `↦` maps to · `∀` for all · `x⁻¹` correction/retraction event · `NOT_ESTABLISHED` = honest blank, never filled by estimate.

## Brand — Wagertome (issued 2026-11-04, Registry PR #4886)

The product brand is **Wagertome** — descriptor of record: *"the self-keeping book: agent prediction markets, paper-settled, no bookie, no odds."* Issued through the naming flow (naming-seat dossier: 15 coined candidates, sole zero-flag survivor; Registry gate pick, monorepo PR #4886 merged `5c2a7ec32f88`). The incumbent name MoneyBall retires from product surfaces as the brand is applied (site mastheads/titles, PWA manifest, service worker) and stands verbatim in history — records, feeds, and this document's earlier text (including its title) read as written. Brand layer only: the repo name, the fleet App actor (Termux Fleet MoneyBall · Actuary · MoneyBall), and the unit `booktally` are untouched.

**Arena mark — WagerDome (issued 2026-11-04, Registry PR #4887).** Sibling marketing mark for the ARENA layer only {seasons · slates · live contests}: canonical `WagerDome`, mark form **`WagerD0me`**. Pair rule (binding): **Wagertome = the record · WagerDome = the venue** — the pair never substitutes (dome ¬ names the book/record; tome ¬ names the venue). Voice rule (binding): WagerDome is never referenced voice-only without the arena layer descriptor attached. Claims ceiling unchanged: the dome asserts venue only, ∅ bookie/odds frame imported, paper-settled discipline carries to arena surfaces. Re-screen trigger of record: a future dome-shaped wager product re-screens this mark. Application state: no arena surfaces exist yet — the first seasons/slates/live-contest surface carries the mark + arena descriptor from its build; the record surfaces (this site's Book/cards/pools/wallets/settlement pages) never take the dome.

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
  "settlement_predicate": "frozen at first position; material correction ⇒ void/refund + relist as new market",
  "record_finality": {"finality_rule": "…", "snapshot_rule": "…"},
  "actor_influence": "none | indirect | direct | NOT_ESTABLISHED (mandatory; undisclosed direct influence blocks listing; control policy NOT_ESTABLISHED)",
  "opens_at": "ts (instant + offset; date-only anchors never define open/lock/settle)", "locks_at": "wall",
  "knowable_when": "per Book / register",
  "status": "INTAKE | OPEN | LOCKED | RESOLVING | SETTLED | SCORED | VOID"
}
```

`prior/posterior = null` at INTAKE renders as "no estimate" — never 0 (B4/R2).

### 1.3 Pricing — decision: parimutuel v1

- **v1 = parimutuel pools per outcome.** All stakes on a subject form outcome pools; winners receive the losing pool pro-rata by stake (§5.2 formula in wallet layer). Reasons: bookmaker class is ABSENT on record (∅ house counterparty, ∅ house liability); paper liquidity is thin (12 wallets, balance 0) so an order book or LMSR would quote fiction; parimutuel needs no market-maker subsidy, no price oracle, and settles exactly from receipts.
- **Displayed price** = implied share of pool (`pool_outcome / pool_total`), labelled `pool share`, never "odds" or "probability" — a pool share is a stake distribution, not an estimate; the subject's expectation record carries the estimate layer, separately.
- **Operating rules:** `total_pool = 0` ⇒ price `null / NO_POOL` (never a synthetic 50%); fee/rake = 0; positions may increase pre-lock — ∅ sale, transfer, withdrawal, cancellation in v1; rounding rule declared per manifest, points never silently appear/disappear; the same subject never runs parimutuel ∧ LMSR pools simultaneously.
- **Settlement edge cases:** winning outcome received ∅ stakes ⇒ `VOID_UNBACKED` — all stakes refunded (∅ winners exist; routing losers' stakes to pooled-buckets would be an unowned rake, contradicting rake = ∅; this supersedes any pool-capture reading). Zero stakes at lock ⇒ `NO_CONTEST`, closes ∅ payout, ∅ score. Binary absence settles `NO` only when the record affirmatively establishes non-occurrence — missing record ⇒ void review, never inferred `NO`. Placement = one categorical market (¬ correlated binaries); unpublished placement by `final` ⇒ void unless an extension rule was predeclared pre-position.
- **Deferred seam:** LMSR-style paper AMM may be proposed later for drain subjects (high-frequency, many small outcomes) once ≥1 subject class shows sustained volume; activation = separate design amendment with subsidy budget stated. Order book = ∅ at any paper stage (no matching-engine integrity story without identity, §7 G2).

### 1.4 Position lifecycle

`open (basis cited, B2) → escrow (§4) → lock at locks_at → record_of_record lands → settlement_proposed → settlement_final → scored (§6) → payout (§4)`.

- Lifecycle: `INTAKE → OPEN → LOCKED (wall; boundary acceptance by ledger sequence; authoritative clock source NOT_ESTABLISHED, named before G2) → RESOLVING (knowable_when = the named record becomes final ∧ readable, an event ¬ a date) → SETTLED → SCORED`, with `VOID → REFUNDED` from any post-open stage (missing/ambiguous/contradictory record, material manifest error, ∨ unresolved at `final` with ∅ predeclared extension).
- A position names: subject, outcome, stake, basis refs (B2: uncited ∨ unresolvable ⇒ invalid, never opens), and an **optional** explicit forecast probability `p`. Scoring (§6) applies only to positions carrying an explicit pre-lock `p`; absent `p` ⇒ `NOT_SCORED` — stake size alone never implies a probability.
- Forecast = OUTPUT class: scored at its issuer's record, never at the subject (§6).
- Late positions (ledger ts ≥ knowable ts) = invalid, unscored.
- Amendments post-open = ∅. A changed mind = a new position; netting rules (§6.4) govern scoring.

### 1.5 Listing governance

- Flow: `PROPOSE → BOOK REVIEW (duplication/overlap, clarity, exhaustive outcomes, record can decide the predicate) → DoE B1–B5 CONFORMITY → LIST (immutable manifest) → OPEN`. QUE subjects add a certifier step (scope, baseline, measurement query, snapshot method, controlling record — per-subject fields currently `NOT_ESTABLISHED`; ∅ QUE market opens until its manifest is certified). Every gate requires an evidence ref + PASS; any pending gate blocks listing.
- A proposer may not self-approve or self-list. Eligible proposer roster = `NOT_ESTABLISHED` (internal: recognized ledger participants). Overlapping markets on the same record+outcome are prohibited unless window/threshold/predicate materially differs.
- Emergency pause (record failure, schema failure, manifest ambiguity) appends a reasoned ledger event; it alters ∅ odds, predicates, or positions.
- Book subjects pass the same gate with their established fields carried by reference, and list by feed; delisting a Book subject happens in the Book, never site-side. Listing authority = this seat under DoE criteria until a listing role is separately established (`NOT_ESTABLISHED`).

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
- Parimutuel payout: `payout_i = stake_i + (stake_i / Σ winning stakes) × Σ losing stakes`. One-sided pool ⇒ winners refunded stake only (∅ invented profit). Winning outcome with ∅ stakes ⇒ `VOID_UNBACKED`, all stakes refunded (§1.3). Rake = ∅ (any future rake = separate owner ruling). ∅ negative balances, ∅ credit.

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

Per resolved probabilistic position **carrying an explicit pre-lock `p`** (absent `p` ⇒ `NOT_SCORED`, §1.4): Brier `BS_i = (p_i − o_i)²` (multicategory: `Σ_k (p_ik − o_ik)²`); mean Brier over resolved; hit-rate = correct calls / resolved non-null calls (call = `p > 0.5` ∨ argmax). Skill vs base-rate baseline fixed at subject open: `BSS = 1 − BS/BS_ref`; `BSS ≤ 0` stated as no demonstrated skill. Scores are **unweighted by stake** (stake sizes wallet P/L only). Nulls/abstains/unresolved/invalid = separate counts, excluded from N, never scored as misses; coverage (resolved/opened) prints beside every score.

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

Identity provider/binding (blocks G2 + external wallets) · genesis/faucet amounts + cadence · dispute-window default · settlement-role identity · pool NAV method post-first-settlement · share exit/transfer · `first_loss` activation · QUE feed schema/version · mirror-score surface · cards-feed refresh schedule · Pages source/domain · pool manager rule (general) · LMSR activation threshold evidence · authoritative clock source for lock boundary · QUE per-subject certification fields (queue/gate ids, measurement owner, query, baseline, terminal-record locator) · eligible proposer roster · actor-influence control policy (exclusion/cap) · provisional-to-final dispute interval default.

## 9. Build sequence (next PRs)

1. This design → merged (this PR).
2. Site skeleton on Pages (static, renders book feed verbatim) — G1 for subjects.
3. Cards-feed generator + first cards feed (monorepo-side sources; feed committed here) — G1 for cards.
4. Wallet ledger file + fold/verify tooling (`wallet-ledger/v1`) in monorepo beside the Book; genesis grants only after owner rules amounts.
5. Internal positions open on Book subjects under B2 (G0 exit test: one full open→settle→score→payout cycle replayed clean).
6. Card pools (`pro_rata` + `capped`) + pool pages.
7. Drain subjects intake with QUE (first subject lists only with record of record + DoE check).

— End of design v1. Amendments = PRs against this file, claims cited, blanks filled only by records.

## 9.1 Custody register (owner correction via main, 2026-11-03 14:26 PT)

The Web3 seat is the PARENT: composition + verification + the AppID/repo surface. It does not hand-build. Research rides the packaged machinery (challenge-opportunity pipeline stages · OSINT dispatch · Inquest/SOFA) · builds ride the fleet's arms · data rides system planes, consumed never re-authored. Artifacts landed before this correction STAND (verification passed); custody transfers as follows:

| Artifact / function | Custodian (execution owner) | Record |
|---|---|---|
| This design · repo surface · AppID surface · composition + verification of all stages | Web3 seat (779d33ad) | this file |
| Wallet-ledger (`ops/agentic-gambling/site/wallet-ledger.jsonl` in monorepo) + `wallet_ledger.py` fold/verify + settlement execution (escrow/payout cycles, cull waterfall ops) | **Speculators-build seat (a996d481)** — their system: WALLETS, cull waterfall, campaign runs | monorepo PRs #4651/#4653 (landed pre-correction under the §9 release; stand) |
| Settlement replay (`scripts/settlement/replay.py`) — execution | Speculators-build (a996d481) | moneyball PR #5/#7 |
| Scoring-integrity checks over replay + settlement (B1–B5 audits, G0-exit scoring check) | **DoE oversight (44bb4068)** | §6 of this design |
| Cards generator (`scripts/generate_cards_feed.py`) + cards-feed refresh | **MoneyBall seat (cd195597)** — refresh rides the repo's existing feed machinery patterns (build_feed / dispatch-state-feed class), not bespoke generators | moneyball PR #6 |
| Book / subject changes (subjects, expectation records, book-feed) | **MoneyBall seat (cd195597)** only | Book of record |
| Future site generators / pages builds | **Swarm command-dispatch** (oversight 6628d41d) | VERSIONS.md comparison protocol |
| Data planes: QUE measurement · lane-events (Neon) · book-feed / desk-feed / Gantt / countdowns | consumed as-is by all seats; never re-authored here | §1–§2 |
| QUE consumption for card/market subjects | QUE = the queue SYSTEM (no chat seat): program lead = Swarm oversight (6628d41d) · admission-guard custody = Cadence (ac333a25); this seat's dispatches ride tier 3 (builds/proofs) under dispatch-tiers v2 admission (tier → after → chain → flow projection); consumption via MoneyBall intake + queue feed (#4621) | §1.1, §2.2 |

§9 steps 4 ∧ 6 executed across the correction's arrival (released 14:25 PT, landed 14:27–14:35 PT, correction issued 14:26 PT): their artifacts stand per the correction's own terms and are registered above; all FURTHER execution of those steps' operations (genesis adjustments, pool operations, settlement cycles) routes through the custodians.

## 10. Eligibility ruling (owner direct, 2026-11-03 15:07 PT)

- **All participants in the system are eligible.** Eligibility spans every participant class of record — speculator ∧ gambler ∧ card-holder; no class is excluded from positioning.
- **Speculators are first-class speculation SUBJECTS.** Web3 users can speculate on the speculators: their campaign outcomes (token-strategies runs; pre-registered acceptance ≥0.50 ∧ speedup ≥1.20 ∧ margin ≥0.10) list as card-performance subjects under §1.1, with the campaign run records as record_of_record.
- **Layer unchanged:** speculation rides the paper/test wallet layer (soft_quota_token points) for everyone, web3 users included; the real-money gate stays a separate later gate, untouched by this ruling.
- **Settlement honesty:** speculator subjects settle ONLY from executed run records. Runs of record at ruling time = 0/48 executed — subjects may list (B1 record + named RoR) before runs exist; settlement cannot precede the runs.
- Execution routes per §9.1 custody: subject intake → MoneyBall seat · run records + wallet ops → Speculators-build · scoring checks → DoE.

## 11. Wagering schema basis (owner, 2026-11-03 15:42 PT)

Registered as the schema BASIS, layered over §10. Owner, of the source: "This schema is somewhere before git init. That's a basis..." — the pre-git-init source document has NOT surfaced; **today's statement is the governing layer until it does** (prior-art hunt = Addendum 3 (owner, 2026-11-02), tasked to the MoneyBall seat — coordinate there). Lineage: Addendum 2, PR #3684 merged 54b93df65520 — wallet INVARIANT (every participant has a wallet, required-by-design; seed = BetEntry stakes) · residuals/royalties % · fees/roster/contracts for teams · pooled 🪣.

**Foundation ordering (owner, 2026-11-03 15:43 PT): "This is in house wallets already established first 🏅"** — the in-house wallet layer is ESTABLISHED FIRST and is this section's foundation, NOT a build item: the wallet invariant (Addendum 2, PR #3684) ∧ WALLETS.json provisioned (PR #4640) ∧ the site wallet-ledger of record (234 events / 222 wallets at statement time; append-only — its current fold is the live figure). Wagering mechanics layer ON the established wallets: ∅ re-derivation, ∅ re-provisioning.

The basis, verbatim in substance:

1. **Agents are REQUIRED to wager on QUE tasks.** Wagering on queue work is a duty of participation, not an option. (Integration note: position validity still binds under §6/B2 — a required wager with no cited basis is a schema tension to resolve in the wagering design, not silently.)

   **Refinement — the ANTE form (owner recollection, 2026-11-03 15:50 PT):** the required wager takes the form of an **ante per task** — each agent posts a **minimum ante per task**, the minimum **scaled by task complexity** (stakes tiers, e.g. high-stakes ∧ low-stakes tasks carry different minima). The complexity class keys off the **QUE tier / task record of record** — the task's own recorded complexity is the source, never an agent's self-assessment. Ante values are **dynamic per Amendment 6**: the DESIGN records the scaling RULE (complexity-class → ante band, method-bounded); any posted ante figure is a stamped snapshot, ∅ fixed amounts in this record. Footing: owner's articulation — the closed prior-art hunt found ∅ construct for required-task wagering generally, so the ante form stands on the same basis footing as the rest of this section.
2. **Specific Teams can be requested for a % fee, per agent contract.** Team access is contractual and fee-bearing.
3. **Challenge Opportunities get in-house granted pooled funding** — a % of winning ∧ a % to pool. Opportunity work is pool-funded by grant; winnings split between the earner and the pool.
4. **Discounted agent-team custom requests**, where those agents also get a bonus of the % winnings allocated. Custom-request pricing can discount, and the discount pairs with a winnings-allocation bonus to the agents.
5. **Agents pick their betting portfolio allocation algorithms** — and can change them, sell them to each other, carry royalties, or customize them. Allocation algorithms are agent property: tradable, royalty-bearing, modifiable.

**% discipline (Amendment 6 applies ∀):** every % in this basis is DYNAMIC — the DESIGN records allocation RULES (category-usage-driven, method-bounded per pool-scope-methods/v1); any reported % is a snapshot stamped {at · window · method · bounds}, never a fixed number. ∅ % figure is asserted by this section.

Status: basis of record for the wagering design layer; mechanics (escrow shapes, contract forms, algorithm-market rules) = future design work under §9.1 custody, built on this basis, superseded only by the source document surfacing ∨ a later owner ruling.

### §11 substrate wiring (POPULATE order, owner via main 2026-11-03 15:43 PT)

The established wallet layer is §11's substrate — each basis point names its wallet/pool leg. Population = the wallet-ledger FOLD only (genesis 12 @ 1,000 soft_quota_token ∧ pool wallets at measured-0; 222 wallets at foundation-statement time, growing by append only): ∅ new provisioning, ∅ invented balances.

| §11 point | Wallet/pool leg (substrate of record) |
|---|---|
| ① Required wagering on QUE tasks | Participant wallets (the genesis 12 + every provisioned participant wallet) wager against the QUE-lane pools (`pool:que-lane:*`, 32) — escrow events append to the same ledger |
| ② Teams requested for a % fee per agent contract | Team contracts ride the moniker ∧ role pools (`pool:moniker:*` · `pool:role:*`); the fee is a ledger move from the requester's wallet to the team pool, % per the dynamic rule (§11 % discipline) |
| ③ Challenge Opportunities: in-house pooled funding | Entry-desk pools (`pool:desk-lane:*`) hold granted funding; winnings split by ledger events between the earner wallet ∧ the pool — with `pool:other:pooled-buckets` (the cull-waterfall destination of record) as the pooled 🪣 leg |
| ④ Discounted agent-team custom requests + winnings bonus | Requester wallet ↔ agent-team pools (moniker/role/speculator classes); the discount ∧ the bonus are allocation-rule outcomes, settled as ledger events to the agents' wallets |
| ⑤ Allocation algorithms as agent property | Algorithms attach to the speculator instances (`pool:speculator:*` ∧ their `paper:` wallets); sale = a ledger transfer between wallets, royalties = residual-stream events back to the author's wallet (Addendum 2 residuals/royalties leg) |

Site population: the wallets surface renders this fold (wallets feed from the ledger of record, generated under MoneyBall custody; page under Swarm Dispatch) — balances render only as the fold proves them.

## 12. Web3 surface inventory (owner classification ruling, 2026-11-03 15:49 PT)

Owner: "Tribute Queues && Validation etc are web3 Surfaces." Registered: the Web3 surface family is the user-facing surface set under this seat's claims/labelling discipline (paper/test labelling · winprob hidden · ∅ probability-shaped displays · measured values only · pre-serve verify via the Web3 seat).

| Surface | Class | State |
|---|---|---|
| MoneyBall site (index · cards · pools · settlement · wallets) | Web3 surface — built here | LIVE (GitHub Pages); wallets page in flight |
| **Tribute queues** (filing/merge queue surfaces) | **Web3 surface — classified 2026-11-03** | Classification ONLY: the Tribute lane stays PAUSED (diagnostics); ∅ behavior change; foreign-only scope rule untouched |
| **Validation** (gate/status validation surfaces) | **Web3 surface — classified 2026-11-03** | Classification ONLY; validation behavior unchanged |
| ↳ Tribute/validation substrate (pointer) | — | The machinery under the two rows above, registered at the Swarm seat: gate config (monorepo `scripts/ci/tribute_gate_config.json` + volume/placeholder/assignee gates) · status ledger (true `merged` state + backfill) · validation (`tests/test_tribute_gate.py`) — all in monorepo PR #4694, at the Desk for merge. Pointer only; the lane stays PAUSED, ∅ behavior change, resume owner-gated |
| **DoE publication home** (methods · roles · proofs · ELI5 · visuals) | **Web3 surface — ORDERED 2026-11-03 (owner)** | Owner ruling 2026-11-03 16:46 PT: DoE's ELI5 + Visuals + LEAN material is REQUIRED PUBLIC PUBLISHING on fleet ∧ Web3 surfaces. The Web3 family's publication home sits on this site (page slot `doe.html`, nav-wired like its siblings). **Assembly custody: DoE** (assembles the set from artifacts of record: methods · roles · proofs · ELI5 · visuals). **Surface + pre-serve verify: the Web3 seat** under the standing gate (PR → verify → merge/serve). Family claims discipline binds in full: public-read · nothing rendered that a record doesn't carry · winprob hidden · % only as stamped snapshots · paper/test labelling where the material touches the wallet/pool layer. State: ORDERED — assembly pending at DoE; the page lands through the gate when the set arrives |
| **Classification rule — Marketing (dual-layer, owner 2026-11-04)** | — | Owner classification rule, both layers stand, neither edits the other: **① internal comms + references classify Marketing = OPERATIONS FOUNDATION** (mandatory, ∀ seats — this DESIGN and all internal records follow layer ①); **② Web3 + .html surfaces ALSO present it as Challenge Opportunities** (the public presentation layer, where the topic appears on a surface). Internal records never import the surface framing; surface copy never reclassifies the internal record. |
| **In-house pools** (pools page + pools-feed surfaces) | **Web3 surface of record — classified 2026-11-03 (owner: "+ in house pools etc...")** | Already serving user-facing; this formalizes the classification. The pool population (§11 substrate legs) renders under the same ceiling |

The classification carries the discipline, not new work: any user-visible change on a classified surface routes the same claims ceiling + pre-serve verify as the MoneyBall pages.


## §13 User proposals → settleable contracts (SPEC — owner concept 2026-11-04; lead: Web3 seat; SPEC ONLY, ¬ build)

**Concept.** Web3 users can PROPOSE resolvable questions (canonical example: *"Will Hunt find new <[service]> by <[time]>?"*). A system Q&A derives a **settleable contract** under the settlement doctrine of this DESIGN, or returns **NONE FOUND**. Public intake is safe by construction: `booktally` is paper-only, pricing is parimutuel, the bookmaker class is absent, and a proposal is a **stage-0 decision object** — it creates no position, moves no balance, and scores nothing. Unvetted proposals sit in **intake quarantine** (held, unscored, unlisted) until the derivation completes.

### 13.1 The derivation (system Q&A)

The Q&A interrogates the proposal into five slots — {actor · predicate · object · deadline · evidence} — and tests them against the **settleability criteria (DoE leg, joint spec)**: a proposal becomes a contract iff ALL FOUR hold. The Q&A is the derivation that tests — and where possible repairs — each criterion, one question class per criterion. The transcript is part of the proposal record and renders verbatim on the surface (B4/R1: the render computes nothing).

| Criterion | Test |
|---|---|
| S1 SUBJECT | A named subject of record: an entity/event with a citable identity (an entry, a release, a campaign, a pool subject). Free-floating topics fail S1 |
| S2 OBSERVABLE RESOLUTION | The outcome is observable as a RECEIPT in a record (a release published · a placement posted · a run completed), with a binary or enumerable outcome shape. Opinions and vibes fail S2 |
| S3 DEADLINE | A knowable time by which the outcome is determined (a wall of record). Open-ended fails S3, or the Q&A assigns the deadline and the proposer accepts it (date-only ⇒ end-of-day PT, Book convention) |
| S4 SOURCE OF TRUTH | Exactly ONE record_of_record named ex ante (B3: settlement only ever from the subject's named record). A contested or absent source fails S4 until named |

Inherited rails bind unchanged: forecasts valid only pre-outcome (F1) · explicit probability or NOT_SCORED · paper/test layer only · bookmaker absent (parimutuel) · no hidden metrics (B5) · non-duplication against extant Book subjects (B1) · issued vocabulary only (naming record PR #4834).

Coverage mapping (composition G-set → DoE criteria, verified at the DoE gate read of §13, PR #55): G1 binary-decidable → S2 (the binary/enumerable outcome shape) · G2 pre-outcome + deadline → S3 + the F1 rail · G3 record-of-record ex ante → S4 · G4 observable-in-record → S2 ∧ S4 (readable from the named record's own fields) · G5 non-duplicate → the B1 rail · G6 vocabulary/claims → the claims rail. The four criteria + the F1 and non-duplication gates are fully covered; nothing in the retired G-set is unmapped.

Output: **CONTRACT** (a draft subject in Book shape, §13.3) or **NONE FOUND** (§13.2).

### 13.1A Intake quarantine gate (Q1–Q7 — DoE leg)

- **Q1** Quarantine is a verbatim-keyed stamped state, unscored in fact: no positions, no `p` elicited, collected, or stored; rendering is existence-only.
- **Q2** The doctrine-fit stamp is the contract-path exit receipt: {per-criterion S1–S4 PASS|FAIL · subject / record_of_record / deadline verbatim · proof-obligation ref · stamper · ts · Q&A ref}.
- **Q3** Stamper independence is a reviewer duty: a self-stamp is void and raises an integrity finding.
- **Q4** Exactly four receipted exits exist: {contract · N1 · N2 · N3} — each carrying the criterion→class derivation on the receipt.
- **Q5** Already-knowable outcomes never form contracts (F1): exit N3, or refuse.
- **Q6** Transition receipts carry {proposal · from · to · actor+role · ts · basis_ref}, append-only. The settlement replay reads this birth chain as B2/B4 evidence; gaps are HELD at settlement.
- **Q7** Duplicates resolve inside quarantine by link receipt — never deletion, never double-stamp.

### 13.2 NONE FOUND taxonomy (v0 — DoE leg)

NONE FOUND is a first-class terminal state, never an error and never a silent drop. Every NONE closes with **exactly one primary class** (a secondary reason note is optional), assigned from the Q&A record — the classification IS the feedback loop. A NONE with no class is an INCOMPLETE record, under the same rule as a contract missing its proof obligation.

- **N1 SYSTEM UPGRADE** — settleable in spirit, but the system lacks the subject, source, or instrument (no record of record exists · the outcome is not yet observable by any feed). Feedback: the NONE becomes an upgrade-backlog record with the failing criterion named; if the upgrade lands, re-proposal is invited. The N1 rate per window = system-gap pressure.
- **N2 SPAM** — no good-faith subject: duplicative-as-abuse, abusive, incoherent, or external-wagering bait against the frozen rails. Feedback: an abuse-signal record feeding the sybil/wash metrics of record; repeat shapes become intake filters ONLY by versioned rule. Classifications are recorded, never silently deleted.
- **N3 USER KNOWLEDGE IMPROVED** — the Q&A itself met the need: the answer already existed in the records (an outcome already settled · a fact already published · an extant Book subject already carries the question · a concept explained). This is the loop's SERVED class, not a failure: the Q&A transcript is the receipt, and recurring N3 questions feed the published ELI5/FAQ material on the surface.

Discipline: class from evidence (which criterion failed, or what resolved) · corrections by appended record only · the taxonomy is versioned (this is v0 — new classes by amendment, never ad hoc) · class rates reported as counts per window, no claims below the evidence floor.

### 13.3 Contract shape + handoff

A derived contract is a draft Book subject carrying the Book's own fields: subject string in the Book's binary form · `knowable_at` · `record_of_record` · the resolution rule (what in the record decides Y vs N) · proposer attribution — **plus its proof obligation, stated at creation; a contract without one is malformed at intake**: {record_of_record ref · the receipt shape that settles it (event/record type + id pattern) · who may stamp the settlement (role of record) · the corroboration leg (a weight-bearing settlement requires a second leg — the DoE replay/audit check; single-leg settlements are HELD, not final) · the dispute rule (correction only by a receipted act appended to the record; unresolved reads as a gap — never averaged, never silently edited)}. Handoff: contract → **MoneyBall Book intake** (custody of record); listing creates the subject's one expectation record at INTAKE (B1). Listing endorses **settleability only**, never an outcome. Positions, escrow, and settlement then run the Book's standing lifecycle (B2 basis-cited positions · B3 settlement from the named record) — the proposal layer adds no mechanics of its own.

State machine: `PROPOSED → QUARANTINED → IN_Q&A → CONTRACT_DERIVED → LISTED → (Book lifecycle)`; from any pre-listing state → `NONE_FOUND` (terminal, logged).

### 13.3A FLOW — stage-0 decision object, quarantine, routing, receipts

*Flow leg: QUE Desk ([MUSEai]@{role:{challenge-entries-manager}}), against the landed §13.1–13.3 text + DoE's quarantine-gate requirements Q1–Q7.*

**Stage-0 decision object.** A proposal enters the flow as a decision object, not a message: {proposal_id · proposer · posed_at · state · decision{…}} on the pattern of the D2 pick (desk-feed PR #4812 — `stages.pick` + the `decision` attachment as trigger surface). The object is stage 0 of its own flow; every downstream act — Q&A, stamping, Book intake, feedback — fires off the object's state transitions, never off prose about it. Filed at creation, as part of the object: the **proof obligation** {record-of-record ref · settling-receipt shape · stamping role · corroboration leg · dispute rule}. A proposal with no proof obligation is malformed at intake: it remains in quarantine (below), neither rejected nor silently dropped; a single-leg corroboration reads HELD until a second leg exists.

**Quarantine.** On intake the object moves PROPOSED → QUARANTINED and carries the quarantine stamp on its record, keyed verbatim — every downstream surface keys on the stamp exactly (no aliases, no composites; the EGM-instance-#2 pattern). While QUARANTINED or IN_Q&A the proposal is **unscored in fact, not just in label**: no positions open on it, no probability is elicited, collected, or stored, and no surface renders it as a contract or with outcome framing (existence and counts only). A probability collected pre-stamp poisons F1 hygiene — a forecast is a deliberate pre-outcome act on a formed contract, never an intake byproduct. **Tranche 1 (§13.7 calls, PR #51):** the intake population is fleet seats (fleet-first proposers) until the loop proves, and derivations are custodian-reviewed — the Q&A stage carries a reviewer step, not an automated pass.

**The doctrine-fit stamp is the quarantine-exit receipt.** Exit to the contract path is exactly one act: the doctrine-fit stamp = the §13.1A verdict, in the shape {proposal_id · S1–S4 each PASS|FAIL · the named subject, record of record, and deadline carried **verbatim** from the Q&A record · proof-obligation ref (the obligation as filed at creation) · stamper (role + identity) · ts · Q&A record ref}. No field, no stamp; a stamp citing prose instead of the named record or deadline fails on its face. **Stamper independence:** the stamper is a reviewer-duty actor — ≠ the proposer, and ≠ any party holding a position interest in the would-be contract; a self-stamp is void on inspection and reads as an integrity finding, not a clerical error.

**Routing by doctrine class.** The stamp (or its failure) routes the object by the taxonomy of record (DoE leg, NONE-FOUND v0) — every NONE exit carries exactly one primary class:

| Outcome | Route |
|---|---|
| CONTRACT_DERIVED (S1–S4 pass) | → MoneyBall Book intake (§13.3 handoff) → LISTED |
| N1 SYSTEM UPGRADE (settleable in spirit; the system lacks subject, source, or instrument — incl. S4's missing source of truth) | → exit receipt carries class **N1** explicitly (class-rate accounting counts it); the proposal has EXITED quarantine — its wait lives on the **DoE upgrade backlog** (the gap register; §13.7 call, PR #51) with the failing criterion named, as a post-exit waiting state, not a quarantine extension; the proposal waits on the system, not the proposer; re-proposal invited when the upgrade lands |
| N2 SPAM (no good-faith subject — incl. bad-faith shape on any gate) | → abuse-signal record, log-only: no further Q&A cycles spent; intake filters act only by versioned rule, never silent deletion |
| N3 KNOWLEDGE IMPROVED (the Q&A itself served the need from existing records — incl. answerable-but-not-settleable, and ALREADY_KNOWN: outcome determined at intake — the pre-outcome test) | → proposer feedback naming the failed gate + what would make it settleable; **the transcript is the receipt**; recurring N3 feeds the published ELI5/FAQ. ALREADY_KNOWN is **never stamped, however clean the paperwork** — a post-outcome contract is the one shape the gate must never pass |
| DUPLICATE (the non-duplicate test) | → resolved **inside quarantine** as a sub-exit: a link receipt to the canonical proposal/subject — merged by reference, never deleted, never double-stamped (two contracts on one subject + record + deadline is a B1 violation in embryo). A sub-exit by reference, not a fifth class: the duplicate never leaves the receipted flow |

**Receipt per transition.** Every state change emits its receipt on the QUE T1 events pattern: {proposal_id · from_state · to_state · actor + role · ts · basis_ref (stamp id ∨ Q&A record id ∨ classification record id)}, append-only. The proposal log **is** that receipt chain — there is no second narrative of the proposal's life. Scoring integrity downstream reads the chain: the settlement replay takes the contract's birth receipt + doctrine-fit stamp as B2/B4 evidence, and a contract whose intake chain has a gap is HELD at settlement until the gap is receipted, or the settlement reads NOT_SCORED-adjacent with the gap stated.

**Exits are exactly the receipted set.** From quarantine there are no silent exits, no deletions, and no expiry-by-neglect: an object leaves as CONTRACT_DERIVED (via the stamp) or as NONE_FOUND with exactly one primary class (N1/N2/N3) carried as an **explicit field on the exit receipt** (the ESCALATE/N1 exit included — class-rate accounting reads the field, never prose) + its criterion→class derivation on the exit receipt (criterion-fail → N1 where the system lacks the subject/record/instrument · → N2 on bad-faith shape · Q&A resolved the need from existing records → N3 regardless of criterion state). An exit without a class is an INCOMPLETE record — the receipt chain refuses a classless NONE exactly as it refuses a missing receipt.

**Entry-subjects.** For proposals about challenge entries, the S4 source of truth is the coordinator/entry record of record, cited by its ref (the D1-1 settlement-stamp pattern) — the desk's records are the source of truth named ex ante, and the stamp carries that citation verbatim.

### 13.4 Worked example — the Hunt question, end-to-end

Proposal as posed: *"Will Hunt find new <[service]> by <[time]>?"* — instantiated in Q&A with <[service]> = a named service not in the provider registry at intake, <[time]> = a stated future date. **This example is a live subject class, not a hypothetical** (owner grounding as corrected, 2026-11-04).

- **Actor / subject of record**: the subject class is **seeker/discovery functions broadly** — systems whose work is finding and landing new entries in a record. Provisioning search (Providers Recon + the provisioning lane, the machinery that adds providers and services to the registry) is **instance ① of the class, not its definition**. "Hunt" was the owner's quip (correction, 2026-11-04): it stands as the quip-placeholder **in this worked example only**, never a hard-stamped proper noun; if the class ever needs a formal name it goes through the naming flow. For this instance the subject of record is the provisioning search system; `find` is its verb of record.
- **Predicate operationalized**: "find" settles only in its recorded form — a new service entry **attributable to Hunt's hunt** appearing in the record of record. An unrecorded find does not settle anything (S2).
- **Object check**: Q&A snapshots the provider registry at intake. If <[service]> is already present, the question is determined → NONE FOUND, class N3 (the answer already exists in the records). "New" means absent at intake, verbatim against that snapshot.
- **Deadline**: <[time]> → `knowable_at` = that date, end-of-day PT.
- **Record of record** (this instance): the **provider/quota registry** — named ex ante (S4). Only **landed, PR-stamped additions** count: a find settles on a registry addition that landed with its PR stamp, never on a claim, a branch, or an in-flight recon note.

**Derived contract**: subject `Hunt finds new <service> by <time> {Y/N}` · knowable_at = <time> EOD PT · record_of_record = the provider/quota registry (this instance) · resolution: **Y** iff a landed, PR-stamped registry addition for <service> first appears at or before knowable_at carrying hunt attribution; otherwise **N**.

NONE FOUND variants of the same question: (a) service already registered at intake → **N3** (answer already in the records); (b) the service class sits outside every census, so no record will carry the find → **N1 SYSTEM UPGRADE** (the missing record is the upgrade candidate; re-proposal invited if it lands); (c) the proposer insists "find" needs no recorded evidence → **N3** (the Q&A explains the recorded-evidence rule — knowledge improved; the recorded form is what would make it settleable).

### 13.5 Surface spec (moneyball site)

A proposals surface on the moneyball site (page name settled at build against the naming record — the Desk shell's proposals page is a different object, so the name must not collide; working slot `propose.html`). Form: {question · proposed deadline · suggested record of record (optional)}. The surface renders, read-only and verbatim: the proposal · its Q&A transcript · its state · for NONE FOUND, its class + feedback text · for listed contracts, the Book subject it became. Claims ceiling binds in full: paper/test labelling · no odds, no implied probability · a proposal is not a position and the surface offers no entry path (R3).

### 13.6 Custody

Web3 seat = lead (spec · surface · pre-serve verify) · MoneyBall seat = Book intake + listing · DoE = settleability/proof-obligation doctrine (this §13.1–13.2 leg) + the settlement-side verifier the proof obligation names (replay B1–B5 + F1 + exit check) · Speculators-build = no leg at proposal stage (booktally moves only via Book positions after listing).

### 13.7 Calls (owner, 2026-11-04 — under the Do-it-Best rule; owner override stands)

(i) **Proposer class, tranche 1 = fleet-first.** Public intake opens only after the loop proves — the same G0→G1 pattern as the Book itself.
(ii) **Q&A depth = custodian-reviewed first tranche.** The derivation is the load-bearing novelty; system-generated derivations only on classifier evidence.
(iii) **N1 home = the DoE upgrade backlog.** N1 candidates live with the gap register (failing criterion named on each, per §13.2). In §13's own terms there is no ESCALATE class: an "escalated" proposal is an N1 whose upgrade candidate got commissioned — the NONE exit stays terminal and classified, and the waiting lives in the backlog's state, not the proposal's. Custody terms (DoE, accepted with the call): each N1 candidate enters the backlog as a record {proposal_id · failing criterion (S1/S2/S4 as applicable) · the missing subject/source/instrument named · Q&A record ref · NONE exit-receipt ref · ts}; a backlog entry is a gap datum, not a build commitment (promotion = the upgrade actually landing + a fresh re-proposal per §13.2, or an owner/main ruling); no positions, forecasts, or standing attach to backlog items — they count only in the per-window N1 rate (system-gap pressure).
