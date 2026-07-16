# Arweave permanent mirror

Every `alpha/` file in this repo (and each rebalance-day `live/.../optimizer_output/` file) is ALSO stored
permanently and immutably on **Arweave** via [ar.io Turbo](https://ar.io) — a second, censorship-resistant
anchor beside this GitHub repo and the OpenTimestamps/Bitcoin proofs.

## How to verify
- **`arweave/index.jsonl`** — one line per file: `{path, tx, sha256, kind, uploaded}`. Each `path` matches
  this repo's tree exactly; `tx` is that file's permanent Arweave transaction. Fetch a file directly at
  `https://arweave.net/<tx>`. Its `sha256` equals the co-located `.sha256` here (the load-bearing commitment).
- **`arweave/manifest.json`** — the current Arweave **path manifest** (a browsable directory). Browse the tree
  at `https://arweave.net/<manifest_tx>/<path>`, e.g.
  `https://arweave.net/<manifest_tx>/alpha/_historical/2015/alpha.enc`.

## Timestamps / provenance
Each file is its own Arweave transaction; its Arweave **block time** is the immutable upload timestamp
(Arweave is itself a timestamped ledger — the on-chain equivalent of the OTS layer). The historical bundle was
backfilled, so it carries its backfill date — a disclosed pre-commitment of already-known data, exactly as the
CHANGELOG states for the GitHub historical bundle. The **forward daily** files each land in a bundle mined on
their own day, carrying a per-file, before-trade-date timestamp.

## Stable name (ArNS) — coming later
A permanent AR.IO **ArNS** name will be pointed at the latest manifest so one URL always resolves to the
current tree. ArNS pointers are mutable and can be set/updated at any time, so the name is added later without
re-uploading anything.

## Manifest immutability
Arweave transactions can't be edited, so each upload publishes a **new** manifest tx (a fresh directory
snapshot). The current one is in `arweave/manifest.json`; older snapshots stay valid but list fewer files.
Individual file txs never change.
