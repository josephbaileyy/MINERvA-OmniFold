#!/usr/bin/env python3
"""RE-2 part C: the purity dry run's opened-file record, from strace (RE2-DECLARATION-C.md §4.1, the director's
condition (b)).

    python3 -I re2c_audit.py --strace S.log --dry DIR --refined ROOT[,ROOT...] --out audit.json

Reads `strace -f -e trace=open,openat,creat,rename*,unlink*,mkdir*` output. Every successful call (no "= -1") is
classed by its path:
  refined   under a refined product root (part B's out/ and J0's out/): must be zero calls of any kind;
  write     opened for writing (O_WRONLY, O_RDWR, O_CREAT, O_TRUNC, creat) or a rename, unlink or mkdir;
            each written path is listed, grouped by whether it is inside the dry-run directory.
A relative path (strace prints the name a call was given: `mkdir -p` components, matplotlib's font cache opened
relative to MPLCONFIGDIR) cannot be placed by this record; those are listed separately for review.
Exit 0 only if no refined path was touched and no absolute write fell outside the dry-run directory other than the
environment's own caches (the conda env's fontconfig cache and Python bytecode, listed separately and counted).
"""
import argparse
import json
import re
import sys
from collections import Counter

CALL = re.compile(r'^(?:\d+\s+)?(\w+)\((.*)\)\s+=\s+(-?\d+)')
PATH = re.compile(r'"([^"]*)"')
WRITE_FLAGS = ("O_WRONLY", "O_RDWR", "O_CREAT", "O_TRUNC")
CACHE = (re.compile(r"/var/cache/fontconfig/"), re.compile(r"/__pycache__/.*\.pyc"))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--strace", required=True)
    ap.add_argument("--dry", required=True)
    ap.add_argument("--refined", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    roots = [r.rstrip("/") + "/" for r in a.refined.split(",")]
    dry = a.dry.rstrip("/") + "/"
    refined, inside, cache, outside, relative = Counter(), Counter(), Counter(), Counter(), Counter()
    n = 0
    for ln in open(a.strace, errors="replace"):
        m = CALL.match(ln.strip())
        if not m or int(m.group(3)) < 0:
            continue
        n += 1
        call, args = m.group(1), m.group(2)
        paths = PATH.findall(args)
        if not paths:
            continue
        for p in paths:
            if any(p.startswith(r) for r in roots):
                refined[f"{call} {p}"] += 1
        is_write = call in ("creat", "rename", "renameat", "renameat2", "unlink", "unlinkat", "mkdir", "mkdirat") or (
            call in ("open", "openat") and any(f in args for f in WRITE_FLAGS))
        if not is_write:
            continue
        for p in (paths if call.startswith("rename") else paths[:1]):
            if p.startswith(dry) or p == dry.rstrip("/"):
                inside[p] += 1
            elif any(c.search(p) for c in CACHE):
                cache[p] += 1
            elif p.startswith("/dev/") or p.startswith("/proc/"):
                continue
            elif not p.startswith("/"):
                relative[p] += 1
            else:
                outside[p] += 1
    out = {"schema": "re2c-audit/1", "calls_successful": n, "refined_roots": roots, "dry": dry,
           "refined_touched": dict(refined), "writes_inside_dry": len(inside),
           "writes_environment_caches": {"n": sum(cache.values()), "paths": sorted(cache)},
           "writes_outside": dict(outside), "writes_relative_for_review": dict(relative)}
    out["verdict"] = "PASS" if not refined and not outside else "FAIL"
    json.dump(out, open(a.out, "w"), indent=1)
    print(json.dumps(dict({k: out[k] for k in ("verdict", "calls_successful", "writes_inside_dry")},
                          refined_touched=len(refined), cache_writes=out["writes_environment_caches"]["n"],
                          writes_outside=out["writes_outside"], writes_relative=out["writes_relative_for_review"]),
                     indent=1))
    return 0 if out["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
