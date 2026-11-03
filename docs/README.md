# MoneyBall — Docs

Home for the site + market design record.

| Doc | State |
|---|---|
| [DESIGN.md](DESIGN.md) — Site + market DESIGN v1 (subjects · card schema · ownership model · settlement-from-receipts · widening path · serving decision) | LANDED — PR #1 merged `d6108a10adb7` |

Rules for this directory:

- Claims carry receipts (PR#, run id, ledger line, feed ref). Uncited = invalid.
- Honest blanks: `INTAKE` / `NOT_ESTABLISHED` render verbatim — never 0, never estimated.
- The Book (`termux-monorepo/ops/agentic-gambling/book/`) is the record; docs here describe the public face + market layer over it.
