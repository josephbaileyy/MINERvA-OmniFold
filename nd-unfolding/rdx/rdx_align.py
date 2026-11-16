#!/usr/bin/env python3
"""RDX C-ALIGN-1A and C-ALIGN-PL (RDX-DECLARATION.md rev 3 §3): W2's "equal" rule between a reference omnifile and
the patched loop's output, on the intersection of branches, with the only extra branches C1's.

    rdx_align.py REFERENCE.root PATCHED.root [--out x.json]

Each file is read at every TTree's highest cycle by MP-1's omnifile_io.read_latest (scalar branches; vector
branches are listed, not compared, as W2's rule does). PASS requires: the same trees; equal entries per tree; every
common scalar branch equal (publication/w2/compare_omnifiles.same: bitwise, NaN equal to NaN); no reference branch
missing from the patched file; and the patched file's extra branches exactly C1's eight on mc_signal_reco and
mc_truth_denom, and none on any other tree. Exit 0 PASS, 1 FAIL, 2 could not check.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
for _p in (str(_HERE), str(_ROOT / "measurement-paper/phase1/mp1"), str(_ROOT / "publication/w2")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import rdx_common as C  # noqa: E402


def compare(A: dict, B: dict, same) -> dict:
    """A: the reference, B: the patched output, each {tree: {"n", "cols", "skipped"}}."""
    bad = []
    if set(A) != set(B):
        bad.append(f"trees differ: {sorted(set(A) ^ set(B))}")
    extras = {}
    for t in sorted(set(A) & set(B)):
        if A[t]["n"] != B[t]["n"]:
            bad.append(f"{t}: entries {A[t]['n']} != {B[t]['n']}")
            continue
        ca, cb = A[t]["cols"], B[t]["cols"]
        missing = sorted(set(ca) - set(cb))
        extra = sorted(set(cb) - set(ca))
        extras[t] = extra
        if missing:
            bad.append(f"{t}: reference branches missing from the patched file: {missing}")
        want = sorted(C.C1_BRANCHES) if t in C.C1_TREES else []
        if extra != want:
            bad.append(f"{t}: extra branches {extra}, declared {want}")
        for k in sorted(set(ca) & set(cb)):
            if not same(ca[k], cb[k]):
                bad.append(f"{t}.{k}: values differ")
    return {"mode": "rdx-equal", "trees": {t: A[t]["n"] for t in A}, "extra_branches": extras,
            "nonscalar_branches_not_compared": {t: A[t]["skipped"] for t in A if A[t]["skipped"]},
            "failures": bad, "verdict": "PASS" if not bad else "FAIL"}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("reference")
    ap.add_argument("patched")
    ap.add_argument("--out", type=Path)
    a = ap.parse_args(argv)
    try:
        import compare_omnifiles as co
        import omnifile_io as io
        res = compare(io.read_latest(a.reference), io.read_latest(a.patched), co.same)
        res.update(reference=a.reference, patched=a.patched, reader="omnifile_io.read_latest (highest TTree cycle)",
                   cycles={"reference": io.cycles(a.reference), "patched": io.cycles(a.patched)})
    except Exception as exc:  # noqa: BLE001 - a check that could not run must not read as PASS
        print(json.dumps({"verdict": "COULD_NOT_CHECK", "error": repr(exc)}))
        return 2
    text = json.dumps(res, indent=1)
    print(text)
    if a.out:
        a.out.write_text(text + "\n")
    return 0 if res["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
