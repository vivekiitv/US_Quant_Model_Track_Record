# Changelog

Dated log of the strategy specification, model versions, and any operational events (missed days,
corrections). Append-only — past entries are never edited.

## 2026-07-15 — ticker correction: published symbols are now canonical (market) tickers

**What changed.** The human-readable `ticker` column in the encrypted backtest + alpha record was
re-serialized from the SEC-filing ticker (EDGAR `dei` TradingSymbol) to the **canonical market ticker**
(Sharadar dated-ticker-history). The SEC ticker lags corporate renames and mislabels share classes; the
canonical ticker is the symbol a broker or allocator actually sees. Corrected examples: `Z`→`ZG` (Zillow
class), `IAC`→`PPLI` (IAC renamed People Inc.), `BRKA`→`BRK.B`, `BFA`→`BF.B`, `CRD-A`→`CRD.A`, plus several
hundred renames across the alpha universe and the corresponding names in the book-of-record.

**No return, weight, or position changed.** Every artifact is keyed by an internal, immutable `sec_id`; the
ticker is a display label joined at serialization time. This correction rewrites only that label — net
Sharpe, NAV, per-name weights, and the rebalance schedule are byte-for-byte identical. A relabeling, not a
re-run.

**Delisted names.** Where a name's canonical coverage ends at delisting, its final held sessions now carry
its **last-known canonical ticker** (carried forward) instead of a blank — e.g. `BJS` (BJ Services, acquired
2010) stays `BJS` on its last days. Residual blank cells fell from ~1,035 to 5 (one newly-listed name whose
canonical coverage began after it entered the universe; the original record was blank there too).

**EchoStar.** A dated-ticker-history defect had collapsed EchoStar — which renamed `SATS`→`ECHO` in June
2026 — to `ECHO` across its entire history, colliding with Echo Global Logistics' real `ECHO` (2009-2021).
Corrected to `SATS` through 2026-06-26 and `ECHO` from 2026-06-29.

**Method (same path, versioned by content hash).** Each of the **63 affected artifacts** was re-encrypted
(fresh AES-256-GCM key + nonce) and **overwritten at its existing path** in an SSH-signed commit; a new key
record was appended to the (private) keystore, keyed by the new plaintext SHA-256. The superseded SEC-ticker
ciphertexts and their keys remain in git history and stay decryptable — an open forward correction, not a
history rewrite. New `.sha256.ots` stamps were created (Bitcoin anchoring pending, upgraded by cron).
Independently re-verified: a fresh clone + disclosure keyfile decrypts and SHA-matches **70/70** artifacts.

**Live record — immutable, not re-encrypted.** The live artifacts committed on/after 2026-07-13 are never
modified. The `2026-07-13` live optimizer target displays the SEC tickers `Z` (Zillow; canonical `ZG`) and
`IAC` (canonical `PPLI`) for two of its 276 names; those commitments stand as-is. The underlying positions
were always `sec_id`-keyed and correct, and broker fills reconciled on the security, not the string. From
this entry forward the live record's displayed tickers are canonical.

**Model code.** `US_quant_model` @ `c416c10` (canonical DTH build + EchoStar override); track-record tooling
@ `fb11428`.

## 2026-07-14c — extended-history backtest published: 2001-2009 (NOT out-of-sample)

Published at `backtest/r1000_long_short/_extended_2001_2009/`, **unencrypted** — a disclosure of a period
that already happened, not a forward pre-commitment, so it must be readable without a key. The positions are
published in full (with point-in-time tickers) so the return series can be **independently recomputed from
public prices** rather than taken on trust.

**This is NOT an out-of-sample test and we do not claim it as one.** The alpha's factor set was researched
with visibility of the full 2000-2026 history; its design saw this decade. What *is* verifiable: the v1.0
**spec** (constraints, risk model, composite definitions, cost model, every parameter) was sealed in the
`2026-07-09` entry and OTS-stamped, and this backtest was run on `2026-07-14` against that frozen spec with
nothing refit. **The configuration was not tuned to the result. The factor set may have been.**

**Why publish it:** the committed record covers 2010-2026, a window with one short crisis. This decade
contains the dot-com bust and the global financial crisis.

**Result** (production configuration, unchanged): 2001-08-01 .. 2009-12-31 — **net Sharpe 1.270, 5.68%/yr,
vol 4.47%, maxDD -5.28%**, 121 rebalances, **every year positive**, and **2008: +7.68%** (vol 6.88%,
maxDD -5.12%). In-sample 2010-2026 for comparison: 1.656 / 7.70%.

**Why the return is lower:** a substantial part of the alpha did not exist yet. Several of its constituent
signals rely on data sources that begin only in the mid-2000s, and a further group from 2009-2010. Roughly
**half** the alpha's inputs have usable data in 2001-2005, about **70%** in 2006-2009, against **95%** from
2010. The 5.68%/yr was earned by approximately half the model.

**And the styles it neutralises away paid enormously in that decade** — value returned **+7.29%/yr in
2006-2009** (vs +0.97% in 2010-2026), *more than the book's entire return*. The book took none of it.

**Two ways this backtest is OPTIMISTIC, stated rather than buried:**
- **Costs.** The production cost cache starts at 2010, so it was rebuilt for 2000-2009 with the same
  function, unmodified (rank-bucket half-spread, 21d median dollar volume, 63d sigma; past-only windows, no
  refit). But those half-spread constants are calibrated on the modern era and **real spreads in 2001-2009
  were materially wider**. Costs are understated by an unquantified amount.
- **Borrow.** Charged at a flat **0.5%/yr** (the pre-2017 feed is a single constant — see `2026-07-14b`), so
  the "real borrow <= 1%" filter excludes nothing and **every name is shortable**. Optimistic for 2008, when
  799 financials were under a short-sale ban.

**What was NOT published, and why the absence is on the record:** the same window run against a research risk
model scored higher (Sharpe 1.507). It is not used and not published — its exposure matrix is
**rank-deficient** (a constant market column exactly equal to the sum of the industry dummies), so its factor
returns are unidentified. Its edge came from two years (2002, 2008) and **failed to reproduce in 2020**, the
one crisis inside the in-sample window, where it *lost* 2.15%.

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
