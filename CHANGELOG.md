# Changelog

Dated log of the strategy specification, model versions, and any operational events (missed days,
corrections). Append-only — past entries are never edited.

## 2026-07-14b — correction: the GC-only short filter did not bind before 2017

**What the v1.0 spec claims (2026-07-09 entry):** *"SHORT book GC-only (real borrow <= 1%)."*

**What was actually enforced:** the borrow *feed* only carries real per-name rates **from 2017**. Every
observation from 2001 to 2016 is a **single constant, 0.004** — 728,208 observations before 2010 with
**one distinct value**. It is the model's own `GC_FALLBACK` constant, not a vendor rate.

Consequence: because no name ever reads above 1% pre-2017, the `FILTER_THRESH <= 1%` rule **excluded
nothing**. For **2010-2016 — nine of the committed backtest's sixteen years — the short book carried no
borrow-availability constraint at all.** From 2017 the filter binds as specified (18k-38k name-days a year
exceed 1% and are excluded).

**What is NOT affected:** the borrow *charge* was applied throughout — a flat 0.4%/yr pre-2017, real
per-name rates after. The backtest's costs are not understated by this; the returns stand. What is
overstated is the *constraint*: the spec describes a GC-only short book, and that was only true from 2017.

**Direction of the error:** pre-2017 the book could short names that a real prime broker might have priced
above 1% or been unable to locate. That flatters the pre-2017 short leg by an unknown amount. We publish
the fact rather than estimate it.

No artifact is revised. The chain is append-only; this entry corrects the *description*, not the data.

## 2026-07-14 — live paper launch, $250M — and the 2026-07-13 aborted run

**The live book trades on QuantConnect (paper), $250,000,000, inception 2026-07-14.** QC is a third party:
it prices every fill, charges Interactive Brokers' commission and slippage, applies Reg-T margin, and
charges **IB's real per-name short borrow**. We do not mark our own executions.

### The aborted run of 2026-07-13 — disclosed, not deleted

A first executor was deployed 2026-07-13 19:10Z against the sealed book
(`live/r1000_long_short/optimizer_output/20260713`, sha256 `1a2cf627...`, signed commit `abbe336`,
OTS-stamped to Bitcoin at 18:33Z). It filled **236 of the 276** committed names. Three defects were then
found in it:

1. **Fabricated borrow.** It charged a flat 0.4%/yr accrual we had written ourselves, instead of IB's real
   per-name rates (measured range: 0.25%/yr to >90%/yr).
2. **`NullShortableProvider`** -- unlimited shorting of any name, no borrow-availability check.
3. **A rebalance path that would have been a silent no-op** at the next scheduled rebalance.

The run was abandoned and its positions closed. **Result: -$257,195.78 (-0.1029%)** on $484,223,240 of
gross traded -- of which **-1.3 bp was the trading day itself** (essentially commission) and **-9.0 bp was
the cost of unwinding**. The strategy was flat; the loss was the price of our own engineering error.

The complete order log is published **unencrypted** at `live/r1000_long_short/aborted_run_20260713/`
(`orders.csv`, sha256 `90d4ee70...`, OTS-stamped). The rest of the chain is encrypted because it makes
*forward* claims; this is a disclosure of a known outcome and must be readable without a key.

**It is not cherry-picking, and that is checkable rather than assertable:** both runs trade the **same
weights**, timestamped into Bitcoin **before either one**. There was no signal to select -- only an
executor to fix. The abandoned run was *up* on market P&L when we killed it; we gave up a small gain and
paid 9 bp to correct the cost model **against ourselves**.

### The executor (v2) -- makes no decisions

Frozen in the deployed code: capital, the IB brokerage model (fees / slippage / fills / Reg-T margin),
`DataNormalizationMode.Raw` (corporate actions adjust the **share count**, as at a real broker), the
financing model, and the security subscriptions. **Nothing else.** No rebalance calendar, no weights, no
portfolio logic. Every order is sent from outside in **shares**, each one a delta against the broker's
**actual** holdings -- so splits, partial fills and reruns all self-correct, and a name already at its
target generates no order at all.

**Financing.** `InteractiveBrokersShortableProvider` supplies IB's real per-name borrow;
`ShortMarginInterestRateModel` charges it. Where IB has no data for a name, prod's `GC_FALLBACK` (0.4%/yr)
applies -- without it such a name would be shorted **free**. **No rebate is credited and no interest is
paid on cash**, so live returns are **excess-of-cash**, matching `walk.py` (`cash -= borrow; cash -= tcost`,
nothing credited). The live record and the backtest remain comparable.

**Divergences from our own data, kept rather than hidden:** IB prices the borrow on three names above our
1% GC threshold (`QXO` 2.26%, `AVAV` 1.37%, `DEC` 1.83%) where our vendor feed said otherwise. We keep the
positions and pay IB's rate. IB can locate all 133 shorts.

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
