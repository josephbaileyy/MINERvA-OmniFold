"""xk's control: `fd_xcov.py k --products re2` into a scratch run directory (the copies) must reproduce the committed
fd/xcov/run/k/k.json. The committed readout names no deploy or run-directory path (its "inputs" keys are the pinned
pscratch inputs, unchanged), so the parsed objects must be identical, with no normalization. Byte identity is reported
beside it. Exit 0 PASS, 1 STOP. Differences are listed (up to 40).
    python3 xk_compare.py --rerun k.json --committed <committed k.json>
"""
import argparse
import json
import sys


def diff(a, b, path=""):
    out = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                out.append(f"{path}/{k}: only in {'committed' if k in a else 'rerun'}")
            else:
                out += diff(a[k], b[k], f"{path}/{k}")
    elif isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        for i, (x, y) in enumerate(zip(a, b)):
            out += diff(x, y, f"{path}[{i}]")
    elif a != b:
        out.append(f"{path}: committed {a!r} rerun {b!r}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rerun", required=True)
    ap.add_argument("--committed", required=True)
    a = ap.parse_args()
    rb, cb = open(a.rerun, "rb").read(), open(a.committed, "rb").read()
    d = diff(json.loads(cb), json.loads(rb))
    for line in d[:40]:
        print("DIFF", line)
    print(f"XK-CONTROL {'PASS' if not d else 'STOP'}: {len(d)} difference(s); bytes {'identical' if rb == cb else 'differ'}")
    return 0 if not d else 1


if __name__ == "__main__":
    sys.exit(main())
