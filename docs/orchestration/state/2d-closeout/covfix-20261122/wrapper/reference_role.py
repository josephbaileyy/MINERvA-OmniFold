#!/usr/bin/env python3
"""A reference bound binary: the stdin side of covfix_wrapper.py's interface, for tests and the synthetic seal.

It is NOT PG or PV code. It shows what cov2d's binaries must do with the frame:
  1. read stdin to EOF and require exactly the role's frame (covfix_wrapper.py's docstring);
  2. hand the passphrase to gpg on fd 3 through an internal pipe, with the pinned decrypt flags, in a fresh empty
     GNUPGHOME, and stream the ciphertext on gpg's stdin and the plaintext on gpg's stdout;
  3. use no decrypted byte before gpg has exited 0 (an MDC failure is a refusal);
  4. keep plaintext in memory only, and print no secret;
  5. exit covfix_wrapper.BREAK_RC (66) on a confirmed integrity break, so the wrapper stops the whole seal.

  5b. print "covfix-break <attempt>" as the last stdout line with that exit, and "covfix-receipt <attempt>" as
      the last stdout line after the role's work succeeded.

  reference_role.py --role pv-writer --covfix-attempt N --covfix-seal-root DIR --covfix-freeze-root DIR
  reference_role.py --role pg-connect --covfix-attempt N
  test flags: --fail-after-decrypt, --no-receipt, --echo-secret
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


def broken(attempt: str, why: str) -> int:
    """A confirmed integrity break: the typed line on stdout, the reason on stderr, exit BREAK_RC."""
    print(f"reference-role: {why}", file=sys.stderr)
    print(f"covfix-break {attempt}", flush=True)
    return cw.BREAK_RC


def main(argv=None) -> int:
    cw.no_core_dumps()
    ap = argparse.ArgumentParser()
    ap.add_argument("--role", required=True, choices=sorted(cw.ROLES))
    ap.add_argument("--covfix-attempt", required=True)
    ap.add_argument("--covfix-seal-root")
    ap.add_argument("--covfix-freeze-root")
    ap.add_argument("--fail-after-decrypt", action="store_true")
    ap.add_argument("--no-receipt", action="store_true")
    ap.add_argument("--echo-secret", action="store_true")
    a = ap.parse_args(argv)
    with_seed = cw.ROLES[a.role][1]
    passphrase, seed_base = read_frame(sys.stdin.buffer, with_seed)
    if a.echo_secret:
        print(f"debug: frame was {passphrase}", flush=True)
    if with_seed:
        if not cw.SEED_BASE_LO <= seed_base < cw.SEED_BASE_HI:
            raise SystemExit("reference-role: seed base out of range")
        print(f"reference-role: {a.role} frame ok (passphrase and seed base received)")
    else:
        sealed = a.covfix_seal_root
        try:
            with open(os.path.join(sealed, "PG-MANIFEST.json.gpg"), "rb") as f:
                blob = f.read()
        except OSError as e:
            return broken(a.covfix_attempt, f"the sealed manifest cannot be opened ({e})")
        try:
            manifest = json.loads(cw.gpg_run(cw.GPG_DECRYPT, passphrase, blob))
            products = manifest["products"]
            assert isinstance(products, dict) and products
        except (ValueError, KeyError, TypeError, AssertionError):
            return broken(a.covfix_attempt, "the authenticated manifest is not a product map")
        n = 0
        for name, want in sorted(products.items()):
            try:
                with open(os.path.join(sealed, name + ".gpg"), "rb") as f:
                    ct = f.read()
            except OSError as e:
                return broken(a.covfix_attempt, f"{name} cannot be opened ({e})")
            plain = cw.gpg_run(cw.GPG_DECRYPT, passphrase, ct)
            if hashlib.sha256(plain).hexdigest() != want:
                return broken(a.covfix_attempt, f"{name} does not reproduce its plaintext sha256")
            del plain
            n += 1
        if a.fail_after_decrypt:
            print("reference-role: simulated crash after decryption", file=sys.stderr)
            return 1
        print(f"reference-role: {a.role} verified {n} product(s) against the sealed manifest")
    if not a.no_receipt:
        print(f"covfix-receipt {a.covfix_attempt}", flush=True)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except cw.Stop as e:
        print(f"reference-role: {e}", file=sys.stderr)
        sys.exit(e.code)
