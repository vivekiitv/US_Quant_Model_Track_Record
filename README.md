# US Quant Model — Public Track Record

A cryptographically verifiable, third-party-timestamped record of the daily **alpha signal** and
**book-of-record** of a US dollar-neutral Russell-1000 long/short equity strategy operated by
**Vivek ([`@vivekiitv`](https://github.com/vivekiitv))**. Its purpose is to let a track record be
**proven** — not merely asserted — while keeping contents confidential until selectively disclosed.

Launched **2026-07-09** (`L`). Everything under `_historical/` is a one-time pre-commitment as of `L`;
the daily forward chain runs from the next session onward, each entry committed **before** that day's
return is realized.

## How to verify (3 steps)

Requires Python with `pip install cryptography opentimestamps-client`.

1. **Clone** this repository.
2. Obtain a **disclosure keyfile** (JSON), provided directly for the window under review.
3. Run:
   ```
   python verify.py --repo . --keys <keyfile.json> --ots
   ```
   For each covered artifact it decrypts the ciphertext, re-computes the SHA-256, and matches it against
   the `*.sha256` committed on that date; `--ots` also checks the OpenTimestamps Bitcoin proof. It prints
   `PASS`/`FAIL` per artifact.

## What proves what

| claim | mechanism |
|---|---|
| **What** existed | SHA-256 of the plaintext, committed publicly (`*.sha256`) — you re-hash the revealed file yourself |
| **When** it existed | GitHub's public push-event record ([GH Archive](https://www.gharchive.org/), server-recorded, not settable) + OpenTimestamps → Bitcoin. Commits are SSH-signed ("Verified") for authorship |
| **Confidential** | AES-256-GCM; only ciphertext + hashes are public; per-file keys → any subset selectively disclosable |
| **One unbroken chain** | one entry per artifact per trading day; no deletions, no history rewrites; gaps explained here in `CHANGELOG.md` |

## Contents

```
alpha/YYYYMMDD/                                       daily alpha signal (the NAV-independent prediction)
alpha/_historical/<year>/                             2000..L, one-time, historical-stamped-2026-07-09
backtest/r1000_long_short/ledger/YYYYMMDD/            daily book-of-record (positions, value, NAV)
backtest/r1000_long_short/optimizer_output/YYYYMMDD/  target weights on rebalance dates
backtest/r1000_long_short/_historical/{ledger,optimizer}/<year>/   2010..L, one-time
verify.py                                             the reviewer tool above
```
Each artifact folder holds `<name>.enc` (ciphertext), `<name>.sha256` (the commitment), and
`<name>.sha256.ots` (the OpenTimestamps proof). Files are frozen at commit time: CSV, UTF-8, sorted by
`sec_id`, dual-keyed by `sec_id` **and** point-in-time-resolved `ticker`, all floating values at 4 decimals.

**Historical vs live.** `_historical/` shards are **stamped-at-launch**: they prove existence *as of* `L`,
not before the (already-known) returns — a frozen pre-commitment, not a before-the-outcome proof. The
per-year `_historical/` folders are a *disclosure* convenience, **not** per-year timestamps. Only the daily
`YYYYMMDD/` folders committed forward, before each day's return, are the strong before-the-outcome record.

## Exclusivity statement

> This repository is the **sole** verification chain for the **sole** US equity long/short strategy operated
> by Vivek ([`github.com/vivekiitv`](https://github.com/vivekiitv)). **One entry per trading day. No resets.
> No deletions.** A terminated strategy, if ever, will be sealed here — not removed. (Stated 2026-07-11.)
>
> **Canonical anchor — repo ID `1297232051`** (`node_id R_kgDOTVIwsw`). GitHub repo IDs are immutable and
> survive renames; a delete+recreate or a swapped-in repo gets a *different* ID. Identify this chain by its
> **ID**, not its name, and verify its public history (creation, every push, any rename/delete/visibility
> change) via **GH Archive** keyed on the repo ID. The name is cosmetic; the ID is the anchor.

## Uniqueness — honest limitations

Uniqueness is **not** cryptographically provable (that would require proving a negative — "no other
chains"). It is made expensive and discoverable:
- **Public-witness standard:** a commit counts only if it was *publicly witnessed at the time*, provable via
  **GH Archive** (GitHub's permanent public-event log). A privately-developed chain published later shows no
  public events at the claimed time and is excluded; a publicly-run parallel chain breaks the one-repo claim.
- **Un-fabricable identity:** the account `vivekiitv` carries 12 years of continuous public history (since
  2014) that no account created later can reproduce.
- **Third-party reconciliation:** committed positions reconcile against an independent execution record.

**Residual (stated plainly):** a *fully separate account/identity* cannot be cryptographically excluded — it
is deterred, not disproven, by the un-fabricable identity plus the public singularity claim. This is the
standard institutional due diligence operates on.

## Conventions

- Returns quoted at a **zero risk-free rate** (raw, not excess).
- **GMV = 2× capital** (dollar-neutral long/short).
- Sharpe is **daily-computed, net of costs**.
- The historical backtest exhibit compounds from **$50M** (2010→); a live paper deployment runs at a
  different NAV — weights differ across the two because the optimizer output is NAV-dependent.
- Production spec + model code version: see `CHANGELOG.md`.

## Contact

Reach out via GitHub — [`@vivekiitv`](https://github.com/vivekiitv) — or open an issue on this repository
for disclosure requests.
