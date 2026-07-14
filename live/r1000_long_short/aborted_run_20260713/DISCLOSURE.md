# ABORTED RUN — 2026-07-13

The first live deployment of the R1000 long/short book. **Abandoned. Not part of the track record.**
Published here so it cannot be said we hid it.

## What happened

Deployed 2026-07-13 19:10Z against the sealed book
(`live/r1000_long_short/optimizer_output/20260713`, sha256 `1a2cf6270dce92f9faae5209db9496700f4d124084007bf0ac74a554439cb903`,
SSH-signed commit `abbe336`, OTS-stamped to Bitcoin at 18:33Z — **before** this run or its replacement).

It filled **236 of the 276** committed names. Three defects were then found in the executor:

1. **Fabricated borrow cost.** It charged a flat 0.4%/yr accrual we wrote ourselves, rather than
   Interactive Brokers' real per-name rates (which range from 0.25%/yr to >90%/yr).
2. **`NullShortableProvider`** — unlimited shorting of any name, with no borrow-availability check.
3. **A rebalance path that would have been a silent no-op** at the next scheduled rebalance.

The run was abandoned and the positions closed. We relaunched on 2026-07-14 with a rewritten executor,
against the **identical sealed weights**.

## Result

| | |
|---|---|
| Started | $250,000,000.00 |
| Ended | $249,742,804.22 |
| **P&L** | **$-257,195.78  (-0.1029%)** |
| Gross traded | $484,223,240  (1.94x NAV) |
| Orders | 237 (236 filled) |
| Holdings at close | 0 |

Decomposed: **−1.3 bp** from the trading day itself (essentially the commission) and **−9.0 bp** from
unwinding $484M of gross when we stopped the algorithm. The strategy was flat; the loss was the cost of
our own engineering error.

## Why this is not cherry-picking

The weights are **the same in both runs**, and were timestamped into Bitcoin **before either one**. There
was no signal to select — only an executor to fix, and the abandoned run was *up* on market P&L when we
killed it. We gave up a small gain and paid 9 bp to correct the cost model against ourselves.

The full order log is in `orders.csv` (sha256 `90d4ee707e6688d9ca4d295b8a9eddcc4c76fc14a3ac4181fe38fde455582a7b`), OTS-stamped.
Unlike the rest of the chain this is **not encrypted**: it is a disclosure of a known outcome, not a
forward pre-commitment, so it must be readable by anyone without a key.

Aborted project: QuantConnect `34105164`. Live record: QuantConnect `34119776` (inception 2026-07-14).
