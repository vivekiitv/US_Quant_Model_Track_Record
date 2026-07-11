# Changelog

Dated log of the strategy specification, model versions, and any operational events (missed days,
corrections). Append-only — past entries are never edited.

## 2026-07-09 — v1.0 launch (L), production spec frozen

**Strategy:** US dollar-neutral Russell-1000 long/short equity.

**Frozen production spec v1.0** — the configuration behind every committed artifact from `L`:
- **Universe:** investable Russell-1000.
- **Alpha:** `alpha_v1_neut` — per-date style-neutralized composite (styles: size, volatility, liquidity,
  beta, revenue_growth, momentum, value), 4 dp.
- **Construction:** dollar-neutral, gross ≈ 2× (GMV = 2× capital); per-name box, ADV/impact caps, target
  vol, turnover cap; NAV-dependent optimizer output; SHORT book GC-only (real borrow ≤ 1%).
- **Costs:** transaction-cost model + GC borrow, net of both.
- **Conventions:** zero risk-free rate; daily-computed net Sharpe.
- **Model code:** `US_quant_model` @ `69c4e99`.

**Launched artifacts (stamped-2026-07-09):**
- `alpha/_historical/` — alpha 2000–2026 (27 per-year shards).
- `backtest/r1000_long_short/_historical/optimizer/` — 2010–2026 (17 shards).
- `backtest/r1000_long_short/_historical/ledger/` — 2010–2026 (17 shards).
- These are a frozen pre-commitment (existence-as-of-`L`; the returns within are already known).
- The **daily forward chain** (alpha + ledger daily; optimizer on rebalance dates) begins the first
  trading session after `L`, each entry committed before that day's return.

**Canonical anchor:** `github.com/vivekiitv/US_Quant_Model_Track_Record`, **repo ID `1297232051`**
(`node_id R_kgDOTVIwsw`, created 2026-07-11T07:36Z). Identify by the immutable ID, not the name (see README).
The `_historical/` bundles cover data **through L = 2026-07-09**; they were committed + OTS-stamped on
**2026-07-11** (existence-as-of-commit — a pre-commitment, since the returns within are already known). The
"stamped-2026-07-09" label denotes the L data cutoff, not the commit instant.

**Identity / anti-cherry-pick:** sole chain on `github.com/vivekiitv`; private key backup at
`vivekiitv/US_quant_model_KEYS`; commits SSH-signed (Verified). Reused the launch-day encrypted artifacts
for the alpha + optimizer historical bundles (identical ciphertexts, no re-encryption); ledger historical
generated at launch. Forward daily / rebalance folders that overlapped the `_historical/` partial-2026
shards were intentionally excluded (historical-only up to `L`).
