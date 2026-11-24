"""COVFIX seal check (COVFIX-DECLARATION.md rev 11.4 section 4.2, Copies): PG's ciphertexts against a PG-SEAL.sha256,
with no decryption and no secret. Used before P1's first connect, for the HPSS copy, and before PV.

  covfix_sealcheck.py --sealed DIR --seal-file PATH [--seal-sha256 <64 hex>]

--seal-sha256 pins the seal file itself (the committed PG-SEAL.sha256's digest). Prints one JSON line; exit 0 only if
the sealed dir holds exactly the canonical set's files with exactly the listed bytes (and the seal file matches its
pin). Diagnostics are fixed codes, counts and opaque names only.
MEASURES: ciphertext integrity. CANNOT AUTHORIZE: anything about the plaintext.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import covfix_seal as cs  # noqa: E402


def main(argv=None, stdout=None) -> int:
    ap = argparse.ArgumentParser(prog="covfix_sealcheck.py", allow_abbrev=False)
    ap.add_argument("--sealed", type=Path, required=True)
    ap.add_argument("--seal-file", type=Path, required=True)
    ap.add_argument("--seal-sha256")
    a = ap.parse_args(argv)
    out = stdout or sys.stdout
    try:
        data = a.seal_file.read_bytes()
        rec = {"seal_sha256": hashlib.sha256(data).hexdigest()}
        if a.seal_sha256 is not None and rec["seal_sha256"] != a.seal_sha256:
            rec |= {"ok": False, "refused": "the seal file is not its pinned sha256"}
        else:
            rec |= cs.seal_check(a.sealed, data.decode("ascii"))
    except cs.Refusal as e:
        rec = {"ok": False, "refused": str(e)}
    except (OSError, UnicodeDecodeError):
        rec = {"ok": False, "refused": "the seal file or the sealed dir cannot be read"}
    print(json.dumps(rec, sort_keys=True), file=out)
    return 0 if rec["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
