"""cr's control: the rerun of GENCMP amendment E step C-R (fd_gencmp overlap --arm refined on partc-r2's Q_R, exactly
fd/gencmp-e/c-r/e_cr.sh's arguments) must reproduce the committed fd/gencmp-e/c-r/overlap_refined.json.
Equal means: the parsed JSON objects are identical after (1) dropping "argv" (it names the output path) and (2)
rewriting every "inputs" key's deploy prefix from the rerun's deploy (as given, or its realpath: the recorder may
resolve symlinks) to step C-R's (/pscratch/sd/j/josephrb/gencmp-e-20261101/deploy). Everything else must be equal exactly, including code_sha256,
every input's sha256/pinned/atime_unchanged, atime_deviations and every reading. Exit 0 PASS, 1 STOP.
    python3 cr_compare.py --rerun overlap_refined.json --committed <committed overlap_refined.json> --rerun-deploy D
"""
import argparse
import json
import os
import sys

STEP_CR_DEPLOY = "/pscratch/sd/j/josephrb/gencmp-e-20261101/deploy"


def norm(d, deploys):
    d = dict(d)
    d.pop("argv", None)
    out = {}
    for k, v in d["inputs"].items():
        for dep in deploys:
            if k.startswith(dep + "/"):
                k = STEP_CR_DEPLOY + k[len(dep):]
                break
        out[k] = v
    d["inputs"] = out
    return d


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
    for k in ("--rerun", "--committed", "--rerun-deploy"):
        ap.add_argument(k, required=True)
    a = ap.parse_args()
    c = norm(json.load(open(a.committed)), [STEP_CR_DEPLOY])
    dep = a.rerun_deploy.rstrip("/")
    r = norm(json.load(open(a.rerun)), sorted({dep, os.path.realpath(dep)}, key=len, reverse=True))
    d = diff(c, r)
    for line in d[:40]:
        print("DIFF", line)
    print(f"CR-CONTROL {'PASS' if not d else 'STOP'}: {len(d)} difference(s) after dropping argv and the deploy prefix")
    return 0 if not d else 1


if __name__ == "__main__":
    sys.exit(main())
