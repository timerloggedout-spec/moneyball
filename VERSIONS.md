# MoneyBall — Versions

| Version | Identity | State |
|---|---|---|
| v1 (current) | `Actuary` line — site skeleton + DESIGN v1.1 on `main` | LIVE (Pages deploy) |
| v2 (next) | **`Actu4ry`** — owner designation 2026-11-03 | parallel comparison builds, below |

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
