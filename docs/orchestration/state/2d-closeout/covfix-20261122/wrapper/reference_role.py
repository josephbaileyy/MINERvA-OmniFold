#!/usr/bin/env python3
"""A reference bound binary: the stdin side of covfix_wrapper.py's interface, for tests and the synthetic seal.

It is NOT PG or PV code. It shows what cov2d's binaries must do with the frame:
  1. read stdin to EOF and require exactly the role's frame (covfix_wrapper.py's docstring);
  2. hand the passphrase to gpg on fd 3 through an internal pipe, with the pinned decrypt flags, and stream the
     ciphertext on gpg's stdin and the plaintext on gpg's stdout;
  3. use no decrypted byte before gpg has exited 0 (an MDC failure is a refusal);
  4. keep plaintext in memory only, and print no secret.

  reference_role.py --role pv-writer --sealed DIR [--fail-after-decrypt]
  reference_role.py --role pg-connect
"""
import argparse
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import covfix_wrapper as cw  # noqa: E402


def read_frame(stream, with_seed: bool):
    data = stream.read()
    pattern = rb"([0-9a-f]{64})\n([1-9][0-9]*)\n" if with_seed else rb"([0-9a-f]{64})\n"
    m = re.fullmatch(pattern, data)
    if not m:
        raise SystemExit("reference-role: the stdin frame is malformed")
    passphrase = m.group(1).decode("ascii")
    seed_base = int(m.group(2)) if with_seed else None
    return passphrase, seed_base


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--role", required=True, choices=sorted(cw.ROLES))
    ap.add_argument("--sealed")
    ap.add_argument("--fail-after-decrypt", action="store_true")
    a = ap.parse_args(argv)
    with_seed = cw.ROLES[a.role][1]
    passphrase, seed_base = read_frame(sys.stdin.buffer, with_seed)
    if with_seed:
        if not cw.SEED_BASE_LO <= seed_base < cw.SEED_BASE_HI:
            raise SystemExit("reference-role: seed base out of range")
        print(f"reference-role: {a.role} frame ok (passphrase and seed base received)")
        return 0
    with open(os.path.join(a.sealed, "PG-MANIFEST.json.gpg"), "rb") as f:
        manifest = json.loads(cw.gpg_run(cw.GPG_DECRYPT, passphrase, f.read()))
    n = 0
    for name, want in sorted(manifest["products"].items()):
        with open(os.path.join(a.sealed, name + ".gpg"), "rb") as f:
            plain = cw.gpg_run(cw.GPG_DECRYPT, passphrase, f.read())
        if hashlib.sha256(plain).hexdigest() != want:
            raise SystemExit(f"reference-role: {name} does not reproduce its plaintext sha256")
        del plain
        n += 1
    if a.fail_after_decrypt:
        print("reference-role: simulated crash after decryption", file=sys.stderr)
        return 1
    print(f"reference-role: {a.role} verified {n} product(s) against the sealed manifest")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except cw.Stop as e:
        print(f"reference-role: {e}", file=sys.stderr)
        sys.exit(e.code)
