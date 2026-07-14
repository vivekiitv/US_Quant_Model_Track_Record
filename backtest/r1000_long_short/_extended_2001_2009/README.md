# Extended-history backtest — 2001-08-01 .. 2009-12-31

## THIS IS NOT AN OUT-OF-SAMPLE TEST

The alpha's factor set was researched with visibility of the full 2000-2026 history. Its **design saw this
decade.** Do not read what follows as out-of-sample validation; we will not describe it that way.

**What IS true, and is verifiable on this chain:** the production **spec** — constraints, risk model,
composite definitions, cost model, every parameter — was sealed in the `2026-07-09` CHANGELOG entry and
OTS-stamped. This backtest was **run on 2026-07-14 against that frozen spec, with nothing refit.** So the
*configuration* was not tuned to this result. The *factor set* may have been. That is the entire claim.

## Why publish it

The committed record covers 2010-2026 — a window with one short crisis. This decade contains the dot-com
bust and the global financial crisis. Publishing the less flattering period is the point.

## Result — production configuration, unchanged

| | |
|---|---|
| Period | 2001-08-01 .. 2009-12-31 (8.4y, 2,117 sessions) |
| Net Sharpe | **1.270** |
| Annualised (net) | **5.68%** |
| Volatility | 4.47% |
| Max drawdown | -5.28% |
| Rebalances | 121 |
| **2008 (GFC)** | **+7.68%**, vol 6.88%, maxDD -5.12% |

Every year positive:

| year | net return |
|---|---|
| 2001 | +2.85% |
| 2002 | +7.85% |
| 2003 | +1.23% |
| 2004 | +5.92% |
| 2005 | +7.85% |
| 2006 | +2.89% |
| 2007 | +7.96% |
| 2008 | +7.68% |
| 2009 | +4.18% |

In-sample (2010-02 .. 2026-07) for comparison: **1.656 net Sharpe, 7.70%/yr.**

## Why the return is lower than in-sample

**A substantial part of the alpha did not exist yet.** Several of its constituent signals depend on data
sources that do not begin until the mid-2000s, and a further group only from 2009-2010. Measured on our own
coverage: **roughly half** of the alpha's inputs have usable data in 2001-2005, about **70%** in 2006-2009,
against **95%** from 2010. The 5.68%/yr was earned by approximately **half the model**.

## And the styles it neutralises away paid enormously in that decade

Annualised style factor returns, from the production risk model — these are the premia the book bands to
+/-0.10 and **gives up**:

| style | 2001-2005 | 2006-2009 | 2010-2026 |
|---|---|---|---|
| value | +3.57% | **+7.29%** | +0.97% |
| size | -3.66% | -2.73% | +0.90% |
| liquidity | +3.65% | -1.10% | +1.76% |
| momentum | +2.14% | -1.58% | +3.70% |

**Value alone paid +7.29%/yr in 2006-2009 — more than the book's entire return.** The book took none of it.
An allocator who neutralises our styles in their own risk model removes nothing, because it was never there.

## What differs from the production run — only what had to

**1. Start date.** The risk-model snapshots begin `2001-05-30`. There is no covariance matrix before that,
so the optimizer cannot solve. **2000 is unreachable.**

**2. Transaction costs — REBUILT, and OPTIMISTIC.** The production cost cache starts at 2010. We re-ran
**the same function, unmodified**, for 2000-2009: a rank-bucket half-spread, 21d median dollar volume, 63d
trailing sigma — all past-only windows, no refit, no look-ahead. **But the half-spread constants are
calibrated on the modern era, and real spreads in 2001-2009 were materially wider (decimalisation had only
just completed). The costs here are understated by an unquantified amount.**

**3. Borrow — FLAT 0.5%/yr, and the GC filter does not bind.** Our borrow feed carries real per-name rates
only **from 2017**; every observation from 2001-2016 is a single constant. Rather than pretend it is data,
we discard it and charge a flat 0.5%/yr. **Consequence: the "short only names with real borrow <= 1%" rule
excludes NOTHING — every name is shortable.** That is optimistic for 2008 in particular, when 799 financials
were under an outright short-sale ban and many names were unborrowable at any price. The alternative —
back-filling modern per-name rates into 2001 — invents a locate market we cannot observe, which is worse.
See the `2026-07-14b` CHANGELOG entry.

**Everything else is production, unchanged:** the same style-neutralised alpha; the same 7 styles banded at
+/-0.10; beta +/-0.10; gross 2.0x with the same +/-10% breach band (both sides); FF49 industry (net +/-2.5%,
gross <=15%); FF12 sector (net +/-5%, gross <=30%); 10%/side turnover; 1% box; 5% target volatility (soft);
ridge 1e-3; 5bp minimum position; 4dp weights.

## Files

- `daily.csv` — the daily return series (sha256 `72d6bfa32997081b1028b927ccf716c28b8599cc6e7da24c44e079681c632fd5`)
- `optimizer.csv` — **every rebalance's solved book**, with PIT tickers (sha256 `8146877aa05016acff5b2d2deb7f77cd7883283af9cffbb90ee596dc552ba847`)
- `daily.sha256.ots` — OpenTimestamps proof (Bitcoin)

**Unencrypted, deliberately.** The rest of this chain encrypts because it makes *forward* claims and reveals
keys later. This is a backtest of a period that already happened — a disclosure, not a pre-commitment — so it
must be readable without a key. The positions are published in full so the return series can be independently
recomputed from public prices rather than taken on trust.

## What was NOT published, and why the absence is on the record

We also ran this window against a research risk model that scored higher (Sharpe 1.507). It is **not used and
not published**: its exposure matrix is rank-deficient — a constant market column exactly equal to the sum of
the industry dummies — so its factor returns are not identified. Its apparent edge came from two years (2002,
2008) and **failed to reproduce in 2020**, the one crisis inside the in-sample window, where it *lost* 2.15%.
We state this so the absence is a fact on the record rather than a choice you cannot see.
