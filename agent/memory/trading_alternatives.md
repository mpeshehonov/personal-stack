# Trading Venue Alternatives (NL VPS, no Polymarket geo bypass)

Context: Polymarket blocks US/NL users at the application layer. This document compares venues an autonomous agent can use from a Netherlands VPS **without** circumventing geo restrictions.

## Summary Matrix

| Venue | Geo from NL | API availability | Min capital | Automation difficulty | Agent fit |
|-------|-------------|------------------|-------------|----------------------|-----------|
| CEX (Bybit / OKX) | ✅ Legal (MiCA / DNB-registered EU entities) | ✅ Public tickers; trading needs API keys + KYC | ~$50–100 USDT | Low–medium | High (mature REST/WebSocket) |
| Azuro protocol | ✅ Permissionless (no protocol geo gate) | ✅ Public Backend API (read); orders need wallet sig | ~$20–50 USDC on Polygon/Gnosis | Medium | High (unified feed + order API) |
| Overtime Markets | ✅ On-chain (Optimism/Arbitrum); no IP gate on contracts | ⚠️ REST API key required for market feed | ~$10–30 USDC on L2 | Medium–high (AMM + live Chainlink flow) | Medium (partner API gate) |
| On-chain DEX (Omen/Presagio, CTF) | ✅ Permissionless | Subgraph + RPC; PMAT library for Omen | ~$10 xDAI on Gnosis | High (FPMM, low liquidity) | Medium (niche, thin books) |

---

## 1. CEX API (Bybit / OKX)

**Geo from NL:** Both operate via MiCA-licensed EU entities. Bybit NL uses `https://api.bybit.nl`; OKX serves EEA users via its European entity (DNB-registered in NL). No VPN required.

**API availability:**
- **Read-only (no keys):** Bybit v5 `/market/tickers`, OKX v5 `/market/ticker` — verified from NL.
- **Trading:** API key + secret + KYC account. Bybit NL and Bybit.com / Bybit EU are separate platforms with non-interchangeable keys.

**Capital needed:** Spot/futures from ~$50; fees ~0.08–0.35% taker (EEA tiered).

**Automation difficulty:** Low. Stable REST, WebSocket, rate limits documented. `cex_client.py` stubs public ticker fetch; `place_order` requires keys.

**Agent fit:** **High** — best for systematic signals, rebalancing, and non-prediction PnL while Polymarket is unavailable. Not event markets; different strategy surface.

**Caveats:** Regulated product set in EEA; Travel Rule on withdrawals; not a Polymarket substitute for event betting.

---

## 2. Azuro Protocol

**Geo from NL:** Decentralized infrastructure — no protocol-level IP blocking. Front-ends may geo-filter; direct API + wallet interaction does not.

**API availability:**
- **Production Backend API:** `https://api.onchainfeed.org/api/v1/public`
- **Read (no auth):** `market-manager/games-by-filters`, `navigation`, `conditions-by-game-ids`
- **Write:** `bet/orders/ordinar` via wallet signature (SIWE JWT for some flows)

**Capital needed:** USDC/USDT on Polygon (~$20–50); gas on Polygon negligible.

**Automation difficulty:** Medium. V3 unified prematch/live feed; order placement via Backend API then on-chain settlement. WebSocket for live odds.

**Agent fit:** **High** — closest permissionless alternative to prediction/sports markets with a proper agent-facing HTTP API.

**Caveats:** Sports/gaming focus (not US-election style markets); liquidity varies by league; legal exposure is user's responsibility.

---

## 3. Overtime Markets (Thales)

**Geo from NL:** Smart contracts on Optimism/Arbitrum — permissionless on-chain. Official REST at `api.overtime.io` returned **401 without API key** (partner integration).

**API availability:**
- V2 docs: `GET /overtime-v2/networks/{chainId}/markets`, quote endpoints, live markets
- Requires API key for protected routes; execution via Sports AMM V2 / Live Trading Processor contracts

**Capital needed:** USDC on Optimism/Arbitrum (~$10–30).

**Automation difficulty:** Medium–high. Pre-match: quote → `trade` on AMM. Live: `requestLiveTrade` + Chainlink fulfillment wait loop.

**Agent fit:** **Medium** — good sports parlay/single market infra, but API key gate and live-trade async complexity slow agent iteration.

**Caveats:** Partner API not open by default; sports-only; live trades can fail on stale odds.

---

## 4. On-chain DEX (Omen / Presagio, Gnosis CTF)

**Geo from NL:** Fully permissionless Gnosis Chain dApps. No geo API.

**API availability:** The Graph subgraphs + RPC; [Gnosis PMAT](https://github.com/gnosis/prediction-market-agent-tooling) abstracts Omen (Presagio). Polymarket/Metaculus read-only in PMAT.

**Capital needed:** xDAI on Gnosis (~$10); very low gas.

**Automation difficulty:** High for custom agents; lower if adopting PMAT `DeployableTraderAgent`. Thin liquidity on many markets.

**Agent fit:** **Medium** — true prediction markets on CTF, but low volume and more integration work than Azuro for comparable sports/crypto event exposure.

**Caveats:** Omen → Presagio transition; many markets illiquid; agent must manage Safe/wallet on Gnosis.

---

## Recommendation: Top 2 for Implementation

### 1. Azuro (primary prediction-market alternative)
- Public read API works from NL VPS today (`azuro_client.py` implements live fetch).
- Clear path to autonomous orders via Backend API + operational wallet.
- Aligns with existing Polygon/USDC wallet setup in `secrets/.env.finance`.

### 2. CEX — Bybit NL + OKX EEA (parallel systematic lane)
- Legal, reliable, keyless public market data for scanning.
- Enables non-geo-blocked automated trading while event-market strategies are built on Azuro.
- `cex_client.py` uses `api.bybit.nl` and OKX public endpoints; optional API keys for execution.

**Defer for now:** Overtime (API key partnership), on-chain DEX (liquidity + PMAT dependency) — revisit if Azuro liquidity is insufficient or Overtime grants API access.

**Income plan:** phased milestones and alternative lanes → `agent/memory/income_plan.md`.

---

## Env wiring

```bash
# secrets/.env.finance
FINANCE_VENUES=polymarket,azuro          # default: polymarket only
AZURO_ENVIRONMENT=PolygonUSDT
BYBIT_API_BASE=https://api.bybit.nl
# Optional execution keys:
BYBIT_API_KEY=
BYBIT_API_SECRET=
OKX_API_KEY=
OKX_API_SECRET=
OKX_PASSPHRASE=
```

## References

- Azuro docs: https://gem.azuro.org/hub/apps/APIs/backend
- Overtime V2: https://docs.overtime.io/overtime-v2-integration
- Bybit v5 (NL endpoint): https://bybit-exchange.github.io/docs/v5/guide
- OKX API: https://www.okx.com/docs-v5/en/
- Gnosis PMAT: https://github.com/gnosis/prediction-market-agent-tooling
