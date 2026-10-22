#!/usr/bin/env python3
"""RE-1 K3: is a regenerated figure the current one, byte for byte?

    re1_cmp_fig.py NEW REF   ->  prints one JSON line; exit 0 when equal, 1 when not

PNG files are compared as they are. Matplotlib PDFs embed a ``/CreationDate (D:...)`` value of fixed length,
so in PDFs only that value is replaced by a constant before the comparison; every other byte, including the
cross-reference offsets, must be equal. Nothing else is normalized.
"""
import hashlib
import json
import re
import sys

DATE = re.compile(rb"/CreationDate \(D:[0-9]{14}(Z|[+-][0-9]{2}'[0-9]{2}')\)")


def norm(b: bytes, pdf: bool) -> tuple[bytes, int]:
    if not pdf:
        return b, 0
    out, n = DATE.subn(lambda m: b"/CreationDate (D:" + b"0" * (len(m.group(0)) - 18) + b")", b)
    return out, n


def main(new: str, ref: str) -> int:
    pdf = new.lower().endswith(".pdf")
    a, na = norm(open(new, "rb").read(), pdf)
    b, nb = norm(open(ref, "rb").read(), pdf)
    same = a == b
    print(json.dumps({"new": new, "ref": ref, "equal": same, "dates_normalized": [na, nb],
                      "new_sha256": hashlib.sha256(open(new, "rb").read()).hexdigest(),
                      "ref_sha256": hashlib.sha256(open(ref, "rb").read()).hexdigest()}))
    return 0 if same else 1


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:3]))
