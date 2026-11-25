#!/usr/bin/env python3
"""Bitwise comparison of two event-loop ROOT dumps, tree by tree and branch by branch (DECLARATION.md §4 P0.4).

    python3 -I dumpcmp.py A.root B.root [--exempt REGEX] [--allow-extra REGEX] [--json OUT]

Rules (each breach is a problem, and any problem is FAIL; exit 0 only on PASS):
  - A and B have the same TTree names (highest cycle of each) and equal entry counts per tree;
  - every branch of A is in B; a branch of B that is not in A is allowed only if it matches --allow-extra;
  - every branch present in both and not matching --exempt is equal entry by entry, BITWISE: the same dtype, and the
    same bytes (so NaN payloads count and -0.0 differs from 0.0). A jagged branch is equal when every entry has the
    same length and the same bytes;
  - a branch matching --exempt is reported (and its number of differing entries counted) but not judged.
C0d runs it as `pin pat --exempt <the six w_truth_GEANT targets>`; C0f as `reference pin --allow-extra <GEANT
universe branches>`. Event-key joins are not done here: C2's pre-check brings its own, with the P2 package.
"""
import argparse
import json
import re
import sys

import numpy as np
import uproot


def _bits(a):
    """The raw bytes of a numeric numpy array, row by row (an unsigned view of the same width)."""
    a = np.ascontiguousarray(a)
    return a.view(np.dtype(f"u{a.dtype.itemsize}")) if a.dtype.kind in "fiub" else a


def _ndiff(x, y):
    """(number of differing entries, first differing index or None, reason or None)."""
    if x.dtype != y.dtype:
        return len(x), 0, f"dtype {x.dtype} != {y.dtype}"
    if x.shape != y.shape:
        return len(x), 0, f"shape {x.shape} != {y.shape}"
    if x.dtype == object:   # jagged: each entry must have the same dtype, length and bytes
        bad = [i for i, (u, v) in enumerate(zip(x, y))
               if not (np.asarray(u).dtype == np.asarray(v).dtype and np.array_equal(_bits(u), _bits(v)))]
        return len(bad), (bad[0] if bad else None), None
    ne = _bits(x) != _bits(y)
    if ne.ndim > 1:
        ne = ne.reshape(len(ne), -1).any(axis=1)
    idx = np.flatnonzero(ne)
    return int(idx.size), (int(idx[0]) if idx.size else None), None


def _trees(f):
    """{name: tree at its highest cycle}: reading a bare name always takes the highest cycle."""
    return {name: f[name] for name in {k.split(";")[0] for k in f.keys(filter_classname="TTree")}}


def compare(path_a, path_b, exempt=None, allow_extra=None):
    ex = re.compile(exempt) if exempt else None
    ok_extra = re.compile(allow_extra) if allow_extra else None
    rep = {"a": str(path_a), "b": str(path_b), "exempt": exempt, "allow_extra": allow_extra, "trees": {},
           "problems": []}
    P = rep["problems"]
    with uproot.open(path_a) as fa, uproot.open(path_b) as fb:
        ta, tb = _trees(fa), _trees(fb)
        if set(ta) != set(tb):
            P.append(f"tree sets differ: only in A {sorted(set(ta) - set(tb))}, only in B {sorted(set(tb) - set(ta))}")
        for t in sorted(set(ta) & set(tb)):
            na, nb = int(ta[t].num_entries), int(tb[t].num_entries)
            info = rep["trees"][t] = {"entries": [na, nb], "branches": {}}
            if na != nb:
                P.append(f"{t}: entries {na} != {nb}")
                continue
            ba, bb = set(ta[t].keys()), set(tb[t].keys())
            for name in sorted(ba - bb):
                P.append(f"{t}: branch {name} missing from B")
            for name in sorted(bb - ba):
                if not (ok_extra and ok_extra.fullmatch(name)):
                    P.append(f"{t}: extra branch {name} in B is not allowed")
            for name in sorted(ba & bb):
                x = ta[t][name].array(library="np")
                y = tb[t][name].array(library="np")
                n, first, why = _ndiff(x, y)
                judged = not (ex and ex.fullmatch(name))
                info["branches"][name] = {"judged": judged, "n_diff": n, "first_diff": first}
                if judged and (n or why):
                    P.append(f"{t}: {name} differs in {n} entries (first {first}){': ' + why if why else ''}")
    rep["verdict"] = "FAIL" if P else "PASS"
    return rep


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--exempt")
    ap.add_argument("--allow-extra")
    ap.add_argument("--json")
    args = ap.parse_args(argv)
    rep = compare(args.a, args.b, args.exempt, args.allow_extra)
    if args.json:
        with open(args.json, "w") as fh:
            json.dump(rep, fh, indent=1)
    print(f"dumpcmp {rep['verdict']}: {len(rep['problems'])} problem(s)")
    for p in rep["problems"][:50]:
        print("  " + p)
    return 0 if rep["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
