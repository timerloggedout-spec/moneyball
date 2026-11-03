# MoneyBall — Versions

| Version | Identity | State |
|---|---|---|
| v1 (current) | `Actuary` line — site skeleton + DESIGN v1.1 on `main` | LIVE (Pages deploy) |
| v2 | **`Actu4ry`** — owner designation 2026-11-03 | **LANDED on main 2026-11-03** — composition of lanes A+B (below) |

## The Actu4ry ruling (owner, 2026-11-03 14:17 PT)

"Next version is `Actu4ry` — we parallel build next versions for comparison lanes."

Scope note, stated once so the record stays clean: `Actu4ry` here is the **product version name** by owner designation. It is NOT a Registry moniker graduation — the moniker `Actuary · MoneyBall` still stands at U=0 attributed units, and the graduation rule (U≥100 + Registry graduation PR) is untouched. If/when the moniker itself graduates, that is a separate Registry event.

## Comparison-lane protocol

Two lanes build the Actu4ry version **in parallel**, each a full next-version build on its own branch, differing in build emphasis. Neither merges. Comparison happens on evidence, then the winning build (or a composition of both) merges as v2.

| Lane | Branch | Emphasis (DESIGN §9) |
|---|---|---|
| A — cards-first | `v2/actu4ry/cards-first` | §9.3 cards-feed generator + `cards.html` + nav; settlement stub = pointer only |
| B — settlement-first | `v2/actu4ry/settlement-first` | §9.5 settlement replay skeleton + wallet-ledger schema; cards stub = pointer only |

Rules for both lanes:
- Base = `main` at lane start; all v1 content stays intact (skeleton, feeds, workflows).
- Feeds render verbatim; nulls = INTAKE/NOT_ESTABLISHED, never 0 (R1–R3, B5 hold in both variants).
- Each lane opens ONE PR titled `v2 Actu4ry comparison — lane <A|B>: <emphasis>` and does NOT merge it.
- Each PR body carries the comparison evidence: files added · local test/validation output · served-shape notes · known gaps as NOT_ESTABLISHED.

Comparison criteria (scored from the PRs + branch content, firsthand):
1. Design conformance — B1–B5, R1–R3, §6 invariants; violations are defects, not style.
2. Feed fidelity — verbatim values, receipts-or-null on every stat, honest blanks.
3. Completeness vs its §9 slice — the emphasized slice fully built; the stub slice honestly pointed, not faked.
4. Build hygiene — validate-feeds green; generator/replay runs clean locally with output shown.
5. Composition value — how cleanly the lane's slice lifts into a merged v2 alongside the other's.

Decision + merge of the composed v2 = this seat, reported ↑ main with the comparison table.

## Comparison outcome (2026-11-03, this seat)

Both lanes delivered their §9 slice in full; the lanes were complementary, so the verdict is **compose both** (the protocol's composition path), not winner-take-all.

| Criterion | Lane A — cards-first (PR #6) | Lane B — settlement-first (PR #5) |
|---|---|---|
| Conformance B1–B5/R1–R3 | PASS — B5 scan in generator + validator | PASS — B1/B2/B3 validated in replay over real record |
| Feed fidelity | PASS — 29 cards, 3 graduated w/ U receipts (352/1,663/163), Collector honestly skipped (∅ moniker ⇒ ∅ card), Actuary v2=null/INTAKE | PASS — report verbatim from real sources; POS-001 NOT_SCORED w/ reason |
| Slice completeness | FULL — generator + feed + page + validator extension; caught ∧ fixed a real line-wrap parsing bug mid-run (documented) | FULL — replay + schema + spec + page + report |
| Hygiene | validate-feeds green (both feeds) | replay exit 0; invariants PASS 26/26 |
| Composition value | cards slice lifts clean | settlement slice lifts clean; only friction = index.html adjacency conflict, composed by hand in PR #7 (disclosed) |

Landing: #6 merged `4494836a3ac7` → composition PR #7 merged `d4ed306a4abb` (lane B files verbatim + composed index nav) → #5 closed superseded-by-composition, evidence intact. Post-merge firsthand verify: main tree complete (18 files), extended validator green on main content, Actuary card correct. Pages deploy of the composed tree = the surviving queued run; served-verify closes on fetch.

## v3 — `6REA7` (owner designation, 2026-11-03 15:28 PT)

Named by the owner in the Actu4ry pattern (version name, mark layer). Headline requirements of record:

- **Installable PWA webApp — REQUIRED** (manifest + service worker + install UX on the Pages site; the app-package research of 2026-11-03 already flagged the richer-install manifest + custom install prompt as top items — 6REA7 makes them mandatory).
- **Wallet + testnet integrations** (web3 wallet connect on testnets first — the paper/test rail extends on-chain; real-money gate untouched).
- **Uniswap bonding curves** — pricing candidate for the next version (against parimutuel v1 of record; a curve price reads probability-shaped, so a DoE B-rail assessment is a proposals-phase input, not an afterthought).
- **Custodial sweeps** — wallet-ops pattern under Speculators-build custody scoping.

Sequence: research package first (awesome-web3 tools/docs/skills inventory, sourced rows ∨ NOT_ESTABLISHED, via the SOFA/Inquest lane riding QUE tier-3 admission — "use the Desk QUE" per the owner's directive) → next-version proposals synthesized from it → parallel comparison lanes per the standing protocol. Build dispatches ride Swarm command-dispatch; nothing hand-built in the Web3 seat.
