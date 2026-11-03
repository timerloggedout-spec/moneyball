# 6REA7 Research Package

Source: SOFA/Inquest lane dispatch (Web3 seat, 2026-11-03), agent Inquest verified live;
read-search pass + web verification pass 2026-11-03. Paper/test layer only throughout.
SOFA layer: wallet/bonding/sweep = 0 hits (NOT_ESTABLISHED on SOFA); PWA = 1 usable caveat.
Inventory is web-sourced, every row verified at fetch 2026-11-03.

## 1 · Installable PWA (static Pages host)
- web.dev — Learn PWA: Installation · https://web.dev/learn/pwa/installation · Chrome install needs manifest (name, 192+512 icons, start_url, standalone/minimal-ui) + engagement heuristic; iOS = no prompt, Share→Add to Home Screen only.
- vite-plugin-pwa · https://github.com/vite-pwa/vite-plugin-pwa/blob/HEAD/docs/guide/inject-manifest.md · generateSW (Workbox) or custom SW + manifest/icon generation · MIT · active (npm v2.0.0, 2026-10-03).
- Workbox runtime caching · https://developer.chrome.com/blog/beyond-spa · precache shell cache-first; stale-while-revalidate + expiration for JSON feeds · Workbox 7.4.1, MIT.
- Serwist · https://insights.linuxfoundation.org/project/serwist-serwist · Workbox successor · MIT · v9.5.12, 1 active maintainer, health 61/100.
- SOFA caveat (untrusted-tier): a service worker can install yet never control the app (activation/clients.claim class bug) — test first-load-offline explicitly.

## 2 · Wallet + testnets
SYSTEM STATE (Speculators DESIGN §9): no chain, no keys, no testnet wiring today — this area is an adoption shelf, not a current capability.
- wagmi · https://wagmi.sh/react/getting-started · React hooks on viem 2.x, Sepolia first-class · MIT · active.
- RainbowKit · https://www.rainbowkit.com · connect UX on wagmi+viem · MIT · ~234K weekly downloads.
- Reown AppKit (WalletConnect) · https://docs.reown.com/appkit/vue/core/custom-connectors · EIP-6963 + WalletConnect, embedded wallets · SDK license NOT_ESTABLISHED.
- ethereum.org Networks · https://ethereum.org/developers/docs/networks/ · Sepolia = canonical app testnet + faucet set; Holesky deprecated 2025-09 → Hoodi (do not build on Holesky).
- Circle testnet USDC faucet — official page NOT_ESTABLISHED this pass; secondary (eco.com): 20 USDC/2h per address+chain.
- Pimlico (ERC-4337) · https://docs.pimlico.io/guides/getting-started · Alto bundler + paymasters — sponsored gas.
- ZeroDev Kernel · https://docs.zerodev.app/onboarding/create-a-smart-account · modular smart accounts (Kernel v3.1, EntryPoint 0.7).

## 3 · Bonding curves / market pricing
VERDICT CONSTRAINT (DoE, VERSIONS §6REA7): adoptable = pool-reserve CPMM only (reserves = outcome pools; no seeds/virtual/external liquidity). LMSR and seeded variants = catalogue-only (§1.3 amendment + owner ruling required).
- Uniswap v2 returns/pricing (official) · https://developers.uniswap.org/docs/protocols/v2/concepts/understanding-returns · x·y=k, spot = reserve ratio, 0.3% fee — the adoptable shape when reserves = pools.
- Uniswap v3 position guide (official) · https://developers.uniswap.org/docs/protocols/v3/guides/managing-liquidity/mint-a-position · concentrated liquidity — catalogue/analytics reference only.
- Bonding Curves: Math, Protocols, Money · https://crypto.training/blog/2026-03-04-bonding-curves/ · Bancor formula + CW table, 17 protocols — catalogue only (seeded/reserve-ratio class).
- pump.fun curve spec · https://github.com/solana-foundation/surfpool/blob/HEAD/crates/core/src/scenarios/protocols/pump/README.md · CPMM over VIRTUAL reserves — catalogue only (virtual excluded by verdict); license NOT_ESTABLISHED.
- SqrtBondingCurve · https://github.com/kamalbuilds/okx.fun/blob/HEAD/contracts/contracts/docs/SqrtBondingCurve-Implementation.md · catalogue only; license+liveness NOT_ESTABLISHED.
- EVM pump-style template repo = NOT_ESTABLISHED.

## 4 · Custodial sweeps
SPLIT (Speculators scoping, accepted): accounting SUPPORTED now on the paper ledger (append-only hash-chained JSONL) — consolidation events as chained moves (cull waterfall pattern), fold-derived triggers (cull · threshold · settlement · manual op), per-class thresholds (values NOT_ESTABLISHED — no ruling yet). Testnet execution = NOT_ESTABLISHED in all legs (chain, keys/signer, gas).
- Fireblocks — Sweep Funds · https://developers.fireblocks.com/docs/sweep-funds · canonical pattern: intermediary vaults → treasury; triggers immediate / balance / count / fee-below-threshold; Gas Station auto-fuel — pattern reference only.
- Fireblocks — Sweep to Omnibus · https://developers.fireblocks.com/reference/sweep-to-omnibus-1 · omnibus structure, relay-sponsored gasless (ERC-20).
- Fireblocks — Deposits at Scale · https://developers.fireblocks.com/docs/manage-deposits-at-scale · segregated vs omnibus, count-based consolidation.
- Openfort checklist · https://www.openfort.io/blog/multi-tenant-wallet-infrastructure · sweep engineering: chain-dependent thresholds, never sweep below fee value, idempotency + reorg awareness.
- Safe Smart Account · https://docs.safefoundation.org/smart-account/overview · m-of-n multisig treasury — testnet custody stand-in if wiring is ever ruled.
- Zerion CLI sweep · https://zerion.io/blog/talk-to-your-treasury-the-zerion-cli-agent-that-sweeps-sorts-and-consolidates/ · open-source consolidate with dust threshold, dry-run — pattern reference.

## Proposals annex (adoptions)
1. **PWA → ADOPT NOW:** vite-plugin-pwa generateSW + Workbox SWR+expiration on feed JSON; precache shell; iOS manual-install UX copy; first-load-offline test (SOFA caveat). Serwist = watch, not start (bus factor). Synthesis note (Web3 seat): the site today is hand-written static HTML with no bundler — generateSW presumes a Vite build; the lane decision (adopt a build step vs hand-rolled SW + manifest) belongs to the Swarm lane design, both shapes satisfy the requirement.
2. **Wallet/testnet → ADOPT AS SPEC, BUILD ON RULING ONLY:** wagmi+viem core, RainbowKit UX (or AppKit if QR/social wins); Sepolia only (not Holesky); Pimlico paymaster so paper play costs users no gas. Blocked on chain-wiring + key-custody owner ruling — NOT_ESTABLISHED stands until then.
3. **Curves → ADOPT INSIDE VERDICT:** CPMM x·y=k over the actual outcome-pool reserves; displayed value = `pool share`; parameters stake-derived or flat symmetric; curve price never rendered as forecast/evidence. LMSR/Bancor-CW/pump-virtual = catalogue.
4. **Sweeps → ADOPT PAPER ANALOGUE NOW:** Fireblocks trigger model as ledger events — sweep-to-pool on (balance ≥ threshold) ∨ (settlement) ∨ (manual op); thresholds per class (values need a MoneyBall-seat ruling); hash-chain audit native. Testnet sweep execution stays NOT_ESTABLISHED; Safe-on-Sepolia = named stand-in if the §2 ruling lands.

## Gaps (explicit NOT_ESTABLISHED)
SOFA in all web3 areas · Reown SDK license · official Circle faucet page · pump + SqrtBondingCurve license/liveness · EVM pump template · sweep threshold values · any real-money tooling (out of scope by rail).

## Template references — agentic-wallet layer

| Template | Named by | Status |
|---|---|---|
| **Kye Gomez Swarms — Agentic Wallet template** | Owner, 2026-11-03 15:45 PT | REFERENCE ONLY. **Verification read LANDED (Inquest, 2026-11-03; primary sources = GitHub API + repo files):** the named artifact "Agentic Wallet template" = **NOT_ESTABLISHED** (∅ wallet repos under kyegomez/The-Swarm-Corporation, ∅ code hits, ∅ docs page). Wallet-adjacent material exists in `kyegomez/swarms` (Apache-2.0): `examples/guides/x402_examples/` (x402 paywall pattern — Agent behind FastAPI, HTTP 402 → pay → proof → facilitator settles → serve; ∅ server-side custody, ∅ keys held, ∅ account abstraction; testnet default = base-sepolia + free x402.org facilitator; production path = base mainnet + Coinbase CDP creds) · `solana_tool` (read-only tx fetcher) · crypto demos (read-only analytics). **FIT:** direction mismatch — the pattern monetizes inbound per-call payments to an operator EOA; the 6REA7 wallet layer is internal paper accounting on the hash-chained ledger (§11 substrate), needing ∅ external settlement leg. The only rail-compatible configuration as shipped is the testnet default. Portable slice = the flow SHAPE only (priced-access → 402 → proof → serve maps onto ledger debit events, facilitator replaced by the fold) — a readable reference, ∅ code adoption. Upstream `coinbase/x402` license = NOT_ESTABLISHED this pass. **∅ adoption claim stands.** Paper/test rails unchanged. |
