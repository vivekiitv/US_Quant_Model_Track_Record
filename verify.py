#!/usr/bin/env python3
"""Reviewer verification tool for the track-record chain (TRACK_RECORD_DESIGN.md §11).

SELF-CONTAINED by design: a reviewer clones the public repo and runs this file with only
`pip install cryptography opentimestamps-client`. No trust in any privately-delivered code.

Given a repo clone + a disclosure keyfile, for each covered artifact it:
  1. decrypts `<id>.enc` with the provided key (AES-256-GCM),
  2. SHA-256s the plaintext and compares to the committed `<id>.sha256`  (the load-bearing check),
  3. optionally (--ots) verifies the `<id>.sha256.ots` OpenTimestamps proof.
Prints PASS/FAIL per artifact and a summary.

Keyfile format (from export_keys):  {"meta": {...}, "keys": {"<repo-relative .enc path>": "<key_hex>"}}

Usage:
  python verify.py --repo <clone_dir> --keys disclosure.json [--ots]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

NONCE_BYTES = 12


def _decrypt(blob: bytes, key: bytes) -> bytes:
    return AESGCM(key).decrypt(blob[:NONCE_BYTES], blob[NONCE_BYTES:], None)


def _sha_path(enc_path: Path) -> Path:
    # <name>.enc -> <name>.sha256   (co-located)
    return enc_path.with_name(enc_path.name[:-4] + ".sha256") if enc_path.name.endswith(".enc") \
        else enc_path.with_suffix(".sha256")


def _check_ots(sha_file: Path) -> str:
    ots_file = sha_file.with_name(sha_file.name + ".ots")
    if not ots_file.exists():
        return "ots:MISSING"
    try:
        r = subprocess.run(["ots", "verify", str(ots_file)], capture_output=True, text=True, timeout=120)
        out = (r.stdout + r.stderr).lower()
        if "success" in out:
            return "ots:BITCOIN-OK"
        if "pending" in out:
            return "ots:PENDING"
        if "bitcoin" in out and ("could not" in out or "no block" in out or "not connect" in out):
            return "ots:COMPLETE(no-node-to-check-block)"
        return "ots:UNVERIFIED"
    except FileNotFoundError:
        return "ots:NO-CLI(pip install opentimestamps-client)"
    except Exception as e:                                          # noqa: BLE001
        return f"ots:ERR({type(e).__name__})"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", required=True, type=Path, help="local clone of the verification repo")
    ap.add_argument("--keys", required=True, type=Path, help="disclosure keyfile (JSON)")
    ap.add_argument("--ots", action="store_true", help="also verify the OpenTimestamps proofs")
    a = ap.parse_args()

    payload = json.loads(a.keys.read_text(encoding="utf-8"))
    keys = payload.get("keys", payload)                            # accept {id:hex} or {meta,keys}
    if payload.get("meta"):
        print(f"# {json.dumps(payload['meta'], sort_keys=True)}")

    npass = nfail = 0
    for id_, key_hex in sorted(keys.items()):
        enc = a.repo / id_
        sha_file = _sha_path(enc)
        try:
            if not enc.exists():
                raise FileNotFoundError(f"missing ciphertext {id_}")
            if not sha_file.exists():
                raise FileNotFoundError(f"missing committed hash {sha_file.relative_to(a.repo)}")
            plain = _decrypt(enc.read_bytes(), bytes.fromhex(key_hex))
            got = hashlib.sha256(plain).hexdigest()
            want = sha_file.read_text(encoding="utf-8").strip()
            ok = (got == want)
            tag = _check_ots(sha_file) if a.ots else ""
            if ok:
                npass += 1
                print(f"PASS  {id_}  {got[:16]}…  {tag}")
            else:
                nfail += 1
                print(f"FAIL  {id_}  hash mismatch (got {got[:16]}… want {want[:16]}…)  {tag}")
        except Exception as e:                                     # noqa: BLE001
            nfail += 1
            print(f"FAIL  {id_}  {type(e).__name__}: {e}")

    print(f"\n{npass} PASS / {nfail} FAIL  ({npass + nfail} artifacts)")
    return 0 if nfail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
