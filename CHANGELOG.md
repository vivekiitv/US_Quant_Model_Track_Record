# Changelog

Dated log of the strategy specification, model versions, and any operational events (missed days,
corrections). Append-only — past entries are never edited.

## 2026-08-25 — note: a vendor-ingest watermark bug dropped cash dividends from our price data 2026-08-14..08-24; the data layer was corrected (dividend-inclusive returns restored, point-in-time stamped), and the sealed ledgers are NOT restated — the net book impact was +3.1bp of NAV over the 7 sessions (longs missed dividend income +6.4bp, shorts avoided paying −3.3bp), within ordinary daily noise.

## 2026-08-20 — correction: a pricing-path return bound zeroed a genuine +177% move on 2026-08-19; books restated

**What happened.** On 2026-08-19 Moderna (MRNA), held short in both books, returned **+176.97%**
($62.96 → $174.38). The portfolio pricing path (`walk.py`) loaded returns with a legacy data-clean
bound of [−90%, +100%] that NULLS any value outside it (a bad-print guard), and then zero-filled the
null — so both books booked **zero P&L** on the position that day. The market data itself was correct
and uncorrected (a genuine move); the factor/alpha/risk layers use wider bounds ([−90%, +200%],
winsorized) and priced the move correctly. In 16.5 years of history this bound was hit by a held
name exactly once: this day.

**Impact (2026-08-19 only).** Live book: missed −1.52% of NAV (published net return −0.13% vs true
−1.67%; NAV $253.5M vs true $249.7M). Backtest book: missed −0.52% (published −0.15% vs true −0.70%;
NAV $175.3M vs true $174.0M). The error was caught on 2026-08-20 via the daily broker reconciliation
(model NAV vs broker equity diverged by ~1.5%; the gap after correction is −0.24%, normal daily
territory).

**Fix.** Pricing bounds widened to [−90%, +500%] and changed from null-and-zero-fill to winsorize
(a genuine move beyond the bound books at the bound instead of vanishing). Model code fixed in
`US_quant_model` (`prod/portfolio/walk.py`, `prod/portfolio/_snapshots.py`).

**Restatement.** Both book-of-record stores were rolled back for 2026-08-19 and re-walked under the
corrected pricing (a pure drift day — no optimizer target was involved). Corrected 2026-08-19 values:
live net return **−1.67%**, NAV **$249,671,650**; backtest net return **−0.70%**, NAV **$174,045,591**.

**Chain integrity note.** The 2026-08-19 artifacts sealed on 2026-08-20 ~10:00Z (commits `b4b72b6`
live_ledger, `65f558f` ledger) contain the PRE-correction ledgers and are left untouched — per this
chain's doctrine, corrections are disclosed forward, never rewritten. From 2026-08-20 onward the daily
chain continues from the corrected stores; the 08-19 → 08-20 discontinuity in the sealed series is
exactly the restatement described here.

## 2026-08-12 — correction to the 2026-08-04 entry: the broker chart history was not lost

**This entry corrects the 2026-08-04 disclosure. That entry stands as written — this log is append-only —
but three of its statements about the broker's equity chart are wrong, and the error was ours.**

The 2026-08-04 entry said the broker's equity chart was deployment-scoped and "did not survive the
redeploy"; that QuantConnect's chart endpoint returned a **single** session after it; and that 2026-08-03
was consequently a permanent gap in that series, for which "no like-for-like broker return can be
computed". None of that is true. The full history is present at QuantConnect. Our request was malformed.

**The cause.** Our chart fetch called `live/chart/read` with `start: 0, end: 0` — a degenerate time
window. QuantConnect answers that with `success: true` and one data point, rather than an error or an
empty result. A one-session series is indistinguishable from a newly-created deployment, so nothing
downstream registered a fault. Fixed 2026-08-12 (`US_quant_model` @ `8aa1cd1`): a real bounded window at
full resolution. Two properties of that endpoint were also misunderstood — `count` is a *resolution*
control, not a row limit (QuantConnect buckets the requested window into approximately `count` samples, so
a wider window at fixed `count` returns coarser data, not more of it), and omitting `count` returns
`success: false`.

**What is actually there.** Measured 2026-08-12 against live project `34165977`, whose current deployment
`L-47af23d9…` was created 2026-08-03 19:10:26Z:

- **29 sessions, 2026-07-15 through 2026-08-12**, including the pre-redeploy period 07-15..08-02. The
  series therefore spans the deployment boundary; it is not deployment-scoped in the way we described.
- **2026-08-03 is present**, not missing: 5,314 intraday samples over 17:00–21:00Z and a settled close of
  **$251,483,439**.

**The 19-minute flat window is visible in the broker's own data, and it corroborates our timeline to the
second.** This is the strongest verification we have of the 2026-08-03 event, and we did not have it when
we wrote that entry:

```
18:42:22Z -> 18:51:00Z   no samples for 518s              deployment stopped 18:42:21Z
18:51:00Z -> 19:09:49Z   416 consecutive samples,
                         equity EXACTLY $251,712,789      the flat deployment, 18m49s
                         ONE distinct value               no positions, so equity cannot move
19:09:49Z -> 19:10:38Z   no samples for 49s               book reseeded 19:10:26Z
```

The control is the sampling density either side: **one** distinct equity value across those 19 minutes,
against **20** distinct values in the preceding 12 minutes and **30** in the following 20. The equity was
pinned, not thinly sampled. A second, independent series agrees — the Exposure chart records both Long
Ratio and Short Ratio at **zero** at 19:09:50Z. The two sampling gaps fall precisely on the two redeploy
instants, and the pinned span sits inside the disclosed 18:50:50–19:10:26Z window.

**Effect on the record.**

| | 2026-08-04 entry | corrected |
|---|---|---|
| Broker chart sessions held | 19 (07-15..08-02), described as surviving only in our copy | 28 (07-15..08-11), retrievable from QuantConnect |
| 2026-08-03 in the chart | absent, permanent gap | present, settled close $251,483,439 |
| Broker return for 2026-08-03 | "no like-for-like comparison can be computed" | computable: chart-to-chart, model −0.199% vs broker −0.209%, tracking error **+0.9 bp** |
| Settled-chart cumulative since $250M deploy | +0.80% (frozen at 07-31) | **+1.39%** (2026-08-11), against model +1.06% |
| Settled-chart tracking error | n=12, mean +0.68 bp/day, 95% CI [−0.5, +1.9] | n=19, mean **+0.31 bp/day**, 95% CI [−1.1, +1.7] |

**The 2026-08-03 figure is now computable but is still not a clean execution measurement.** The +0.9 bp
tracking error above spans 07-31 to 08-03 and therefore contains the flat window, during which the broker
held no exposure while the model did. As stated on 2026-08-04, that window is worth roughly 6.5 bp (1σ,
sign random) on a book of this volatility. We therefore correct the claim that the day cannot be measured,
without upgrading it to a claim about execution quality on that day.

**The previously-stored sessions are unchanged.** Refetching at full resolution reproduced 18 of the 19
stored sessions to 0.000 bp. The one exception is 2026-07-15, the launch session, which moves by 2.1 bp
($249,906,278 → $249,853,189) because the deployment began 17:27 that day and the day's final sample moves
with sampling resolution. It is immaterial and is noted only for completeness.

**Unaffected.** The headline book-of-record is a model-computed walk of the sealed weights on our
point-in-time closing prices, not a read of the broker account (see the 2026-07-16 entry), and nothing here
touches it. No sealed artifact was altered, re-encrypted or re-stamped; no strategy parameter changed; the
deployed executor is unchanged. The 2026-07-24 to 2026-08-03 command outage, the redeploy, and the flat
window all stand exactly as disclosed — this entry strengthens the evidence for them rather than revising
them.

**What we changed so this does not recur.** The chart fetch now logs a warning when a response is
implausibly sparse, so a truncated series can no longer pass as a young one. Separately, a daily check
(`check_qc_channel.sh`) now alerts when either broker series stops advancing against the trading calendar;
under it, this fault would have surfaced within two sessions rather than nine days.
## 2026-08-04 — operational disclosure: broker command outage, redeploy, and a 19-minute flat window on 2026-08-03

**What happened.** From 2026-07-24 the QuantConnect cloud stopped delivering commands to our live
deployment. The algorithm kept running normally — scheduled events on time, data feed healthy, logging in
real time — but nothing sent *to* it arrived. Every API call returned `success: true` and had no effect,
and QuantConnect's own web UI could not place an order on the deployment either. There was no redeploy and
no change on our side in that window; the last command that reached the algorithm was 2026-07-24 21:31Z,
and the first that did not was 2026-07-27 21:30Z. The cause is on the platform side and is with
QuantConnect support.

**Consequence.** The broker account could not be traded. The scheduled monthly rebalance for trade date
2026-08-03 could not be sent through the normal path. Restoring command delivery required a redeploy, which
is why the live record shows a new deployment ID on 2026-08-03.

**Timeline, 2026-08-03 (UTC).**
- `18:42:21` deployment `L-080386c6…` (live since 2026-07-15) stopped. Stopping retains holdings: 275
  positions, cash unchanged, order history intact.
- `18:50:50` redeployed as `L-3ca9e582…`. `holdings` and `cash` are required fields when creating a
  QuantConnect-brokerage deployment; the deployment was created without them, which QuantConnect reads as
  an account holding nothing, so it came up FLAT. Nothing was liquidated — no orders were placed and the
  order count never moved — the position value simply appeared as cash.
- `19:10:26` redeployed as `L-47af23d9…`, seeding the book back from the pre-stop state. All 275 positions
  restored with original cost basis and unrealized P&L intact.
- `19:39–19:52` the 2026-08-03 rebalance was sent and filled: 292 orders, $59.0M notional.

**The flat window.** Between `18:50:50Z` and `19:10:26Z` — **19 minutes of open market** — the broker
account held no positions. Account equity was carried across intact ($251.7M); what was absent was position
exposure for that interval. The strategy is dollar-neutral, so the omitted exposure was ~2.0× gross and
approximately market-neutral, but this is a real execution-side gap and is disclosed as such.

**What was preserved at the broker, and what was not.**

| preserved | reset / lost |
|---|---|
| Holdings (once seeded), cash, cost basis, unrealized P&L | **Return / net-profit baseline** — rebased to the new deployment's starting equity |
| Full order history (276 orders pre-rebalance, unbroken) | In-memory algorithm state |
| — | **The broker's own equity-chart history** — see below |
| — | Deployment ID |

The **return figure shown on the QuantConnect side now reads from the 2026-08-03 redeploy, not from the
2026-07-14 $250M inception.** Anyone reading broker-side return directly should account for that rebase.
Our own ledger and this chain remain the authority on since-inception performance.

**The broker's equity chart is deployment-scoped, and did not survive the redeploy.** Measured on
2026-08-04: after the redeploy, QuantConnect's chart endpoint returned a **single** session (2026-07-15).
The 18 sessions from 2026-07-16 to 2026-08-02 survive only because we hold our own copy — our recon job
was changed on 2026-08-04 to *merge* the fetched series into stored history rather than overwrite it,
which is the only reason that record still exists. Anyone relying on the broker-side chart for continuity
across a redeploy should not.

**2026-08-03 is a gap in the broker chart series.** It is absent from both the post-redeploy fetch and our
stored copy. The point-in-time probe reading for that date (taken 21:31Z) may therefore be the only
broker-side observation of it. Both broker series operate normally from 2026-08-04.

**Effect on the record — stated plainly.** The headline book-of-record is unchanged in method and is
unaffected by this event: since 2026-07-16 it is a model-computed walk of the sealed weights on our
point-in-time closing prices with the disclosed cost model, not a read of the broker account (see the
2026-07-16 entry). No sealed artifact was altered, re-encrypted or re-stamped; no strategy parameter
changed; the deployed executor is byte-identical to the code running before the outage.

What *is* affected is the **independent execution recon**:
- The point-in-time probe series has **no observations from 2026-07-24 to 2026-08-03** (the probe travels
  over the same broken channel); it resumed 2026-08-03 21:31Z.
- The settled chart series is missing 2026-08-03, as above.
- The 19-minute flat window means broker-realized P&L for 2026-08-03 excludes that interval, while the
  model NAV does not.

**On measuring 2026-08-03 specifically.** Because the chart series lacks that date and the probe series
lacks 2026-07-31, no like-for-like broker return can be computed for the session. The only available
comparison mixes the two series (07-31 settled chart → 08-03 probe) and puts the broker ~10 bp below the
model on the day. That figure is not a measurement: the two series differ by 5–8 bp by construction, and
the flat window is itself worth ~6.5 bp (1σ, sign random) on a book of this volatility. We therefore make
no claim about execution quality for 2026-08-03 in either direction. Both series resume normal operation
from 2026-08-04.

**A standing clarification on the model-vs-broker level gap — this event did not cause it.** The broker
equity series has run roughly **+0.4% above the model NAV since 2026-07-15**, and that offset is a
**start-date artifact, not slippage and not a cost**:

```
2026-07-13  model $250,000,000   (walk begins from the committed launch state, flat)
2026-07-14  model $249,133,313   (builds the 276-name book; 34.67 bp modeled transaction cost)
2026-07-15  model $248,877,220   broker $250,000,000   <- broker's first session
```

The model walk is seeded from the committed 2026-07-13 launch state and had already built the book and
absorbed its modeled build cost before the current deployment existed. The live deployment dates only from
2026-07-15 — after the aborted 2026-07-13 run and the short-rebate/configuration redeploys described in the
2026-07-16 entry — and its account began at exactly $250,000,000. The gap on the first overlapping session
is therefore **$1,122,780**, which is *exactly* the model's 07-13 → 07-15 P&L on a book the broker was not
yet holding.

It should not be read as execution shortfall. The meaningful execution measure is **daily tracking**, which
the recon puts at **+0.51 bps/day** on the settled series. For reference the level gap was **$833,720
(+0.332%)** at the 2026-07-31 close — i.e. it has narrowed since inception, not widened.

**One position differs going forward.** The rebalance target holds 286 names; the broker holds 285. `MNR`
cannot be priced by the broker — the ticker was reused (the prior issuer delisted in 2022, a new listing
took the symbol in 2023-10), so it resolves to a security with no market data and no order can be placed.
Target weight is 0.0012 (12 bp). The model book-of-record holds it; the broker does not. This is a known,
bounded divergence and will persist until the ticker resolves or the name leaves the book.

**Method / provenance.** No change to sealing, verification, or the publication procedure. Deployment IDs
for audit: `L-080386c6628e9d1ab20ce6d5ef755d88` (2026-07-15 → 2026-08-03), `L-3ca9e5823ee8e6e80654924ffcda8ec4`
(18:50–19:09Z, flat), `L-47af23d9cdb1572a1a348d5acf157291` (2026-08-03 →).

## 2026-07-28 — added a blind backtest tear sheet (`tearsheet.pdf`)

**What changed.** Committed `tearsheet.pdf` at the repo root — a 4-page summary of the backtest: headline
statistics (net Sharpe 1.66, 7.9% net CAGR, −5.5% max drawdown, 2.00× gross, monthly rebalance) and
cumulative-return / drawdown curves, 2010–2026. Added to the README.

**What it does and does not disclose.** It is **blind**: aggregate performance only. No alpha signal, no
positions, no holdings, and no per-name data appear — those remain sealed (AES-256-GCM) and disclosable
only per-file. Every figure is derived from the already-committed book-of-record; the tear sheet asserts
nothing that is not recomputable from a disclosed window. No change to the chain, the artifacts, or the
verification procedure.

## 2026-07-16 — the live book-of-record is now a model-computed walk; the broker becomes an independent execution recon

**What changed.** The live daily NAV (`live/r1000_long_short/ledger/`) is now computed by us — the sealed optimizer weights, marked forward on our point-in-time closing prices with the disclosed cost model (`walk.daily_step`) — rather than reconstructed from the QuantConnect brokerage account. The book-of-record is the strategy applied to public prices, not a read of a broker's ledger.

**Why.** A model-computed NAV is **reproducible**: anyone holding a session's committed weights can recompute that day's return from public closing prices and the published cost model, and check it against the sealed number. It is also **continuous** — independent of broker-side operational events. During the first days of live operation (2026-07-13 through 07-15) the QuantConnect paper deployment was redeployed three times to correct a short-rebate crediting error and the borrow/subscription configuration; each redeploy reset the paper account to its starting cash. Those resets are execution-plumbing events, not strategy events, and a book-of-record read from that account would have inherited the discontinuities. The model walk does not.

**What this means for the claim — stated plainly.** The load-bearing property is unchanged and is the one that matters: **each session's weights are cryptographically sealed (SHA-256 + OTS/Bitcoin + SSH-signed) before the session they apply to** — signal precedes fills. What this entry changes is how the *NAV* attached to those weights is produced. From 2026-07-16 the headline live NAV is a **model book-of-record**: our marks, our disclosed cost model (modeled transaction cost and borrow, not the broker's realized fills). It is not a statement of broker-realized P&L.

**The broker is retained as a separate, date-aligned execution recon.** The QuantConnect paper deployment continues to trade the same sealed targets, and its actual equity is reported alongside the model NAV as an independent check that the strategy is executable at scale and that real fills track the model — reported as its own series, never folded into the headline number. Where they diverge (slippage, partial or missed fills, financing differences) the recon is where that shows.

**One concrete example of the model-vs-execution distinction.** Building the $250M book from flat on the first session carries a modeled transaction cost of **34.7 bps** (half-spread × ~2.0× turnover, plus impact), which appears as an explicit line in the 07-14 ledger. That is the model's estimate of the build cost; the recon reports what the broker actually paid to build.

**Continuity of the launch commitment.** The 2026-07-13 launch artifacts — the all-cash launch state ($250M) and the 276-name optimizer target — are immutable and unchanged. The walk is seeded from exactly that committed launch state (it re-serializes identically), builds into the launch target on 2026-07-14, and marks forward from there.

**Method.** `live_ledger` for 2026-07-14 and 2026-07-15 was sealed identically to every other artifact (AES-256-GCM + plaintext SHA-256 + `.ots` + SSH-signed commit): 07-14 `5096a84`, 07-15 `71c6d54`, both independently Verified. NAV: 07-13 $250,000,000 → 07-15 $248,877,220 (−0.449% since launch). Model code `US_quant_model` @ `b68c4df`.

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

## 2026-07-14 — live paper launch, $250M

**The live book trades on QuantConnect (paper), $250,000,000, inception 2026-07-14.** QC is a third party:
it prices every fill, charges Interactive Brokers' commission and slippage, applies Reg-T margin, and
charges **IB's real per-name short borrow**. We do not mark our own executions.

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
