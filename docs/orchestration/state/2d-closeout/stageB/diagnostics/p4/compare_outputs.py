#!/usr/bin/env python3
"""Tree-content comparison of two runEventLoopOmniFold outputs (P4 no-op control and production bridge).

For every TTree present in both files: entry counts, and for every branch present in both, exact equality
of the full column (scalar branches via RDataFrame.AsNumpy; vector branches element by element). TParameter
and TNamed objects present in both are compared by value; any other object class present in both is
reported DIFFERENT (unhandled), never vacuously equal. Objects or branches present in only one file are
listed, not failed, unless --strict.

  python compare_outputs.py A.root B.root [--strict] [--json out.json]

Exit 0 iff every common tree/branch/parameter is identical (and, with --strict, the object and branch sets
are equal too).
"""
import argparse
import json
import sys

import numpy as np
import ROOT

ROOT.gROOT.SetBatch(True)


def objects(f):
    out = {}
    for k in f.GetListOfKeys():
        out[k.GetName()] = k.GetClassName()
    return out


def scalar_value(o):
    if o.InheritsFrom("TNamed") and not o.InheritsFrom("TTree") and o.ClassName() == "TNamed":
        return o.GetTitle()
    if hasattr(o, "GetVal"):
        return float(o.GetVal())
    return None


def column_equal(a, b):
    if a.dtype == object or b.dtype == object:
        if len(a) != len(b):
            return False, "length"
        for i, (x, y) in enumerate(zip(a, b)):
            if list(x) != list(y):
                return False, f"first difference at entry {i}"
        return True, ""
    if a.shape != b.shape:
        return False, "shape"
    if np.array_equal(a, b, equal_nan=True):
        return True, ""
    if a.dtype.kind == "f":
        neq = ~((a == b) | (np.isnan(a) & np.isnan(b)))
    else:
        neq = a != b
    d = np.flatnonzero(neq)
    return False, f"{d.size} entries differ, first at {d[0]}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--json", default=None)
    args = ap.parse_args()
    fa, fb = ROOT.TFile.Open(args.a), ROOT.TFile.Open(args.b)
    oa, ob = objects(fa), objects(fb)
    rep = {"a": args.a, "b": args.b, "only_a": sorted(set(oa) - set(ob)), "only_b": sorted(set(ob) - set(oa)),
           "trees": {}, "params": {}, "ok": True}
    for name in sorted(set(oa) & set(ob)):
        if oa[name] != ob[name]:
            rep["params"][name] = {"equal": False, "why": f"class {oa[name]} vs {ob[name]}"}
            rep["ok"] = False
            continue
        if oa[name] == "TTree":
            ta, tb = fa.Get(name), fb.Get(name)
            ba = {x.GetName() for x in ta.GetListOfBranches()}
            bb = {x.GetName() for x in tb.GetListOfBranches()}
            tr = {"entries": [int(ta.GetEntries()), int(tb.GetEntries())],
                  "only_a": sorted(ba - bb), "only_b": sorted(bb - ba), "branches": {}}
            if ta.GetEntries() != tb.GetEntries():
                tr["equal"] = False
                rep["ok"] = False
            else:
                common = sorted(ba & bb)
                ca = ROOT.RDataFrame(ta).AsNumpy(common) if common else {}
                cb = ROOT.RDataFrame(tb).AsNumpy(common) if common else {}
                for br in common:
                    eq, why = column_equal(np.asarray(ca[br]), np.asarray(cb[br]))
                    tr["branches"][br] = "equal" if eq else why
                    if not eq:
                        rep["ok"] = False
                tr["equal"] = all(v == "equal" for v in tr["branches"].values())
            if args.strict and (tr["only_a"] or tr["only_b"]):
                rep["ok"] = False
            rep["trees"][name] = tr
        else:
            va, vb = scalar_value(fa.Get(name)), scalar_value(fb.Get(name))
            if va is None or vb is None:  # a class this script does not compare is never "equal"
                eq = False
                rep["params"][name] = {"equal": False, "why": f"unhandled class {oa[name]}"}
            else:
                eq = va == vb
                rep["params"][name] = {"equal": eq, "a": va, "b": vb}
            if not eq:
                rep["ok"] = False
    if args.strict and (rep["only_a"] or rep["only_b"]):
        rep["ok"] = False
    for t, tr in rep["trees"].items():
        bad = {k: v for k, v in tr["branches"].items() if v != "equal"}
        print(f"[tree] {t}: entries {tr['entries']}, {len(tr['branches'])} common branches, "
              f"{'ALL EQUAL' if tr.get('equal') else 'DIFFER ' + str(bad)[:300]}; "
              f"only_a {tr['only_a']} only_b {tr['only_b']}")
    for p, v in rep["params"].items():
        print(f"[obj] {p}: {'equal' if v['equal'] else 'DIFFER ' + str(v)}")
    print(f"[only_a] {rep['only_a']}\n[only_b] {rep['only_b']}")
    print("RESULT:", "IDENTICAL" if rep["ok"] else "DIFFERENT")
    if args.json:
        json.dump(rep, open(args.json, "w"), indent=1)
    sys.exit(0 if rep["ok"] else 1)


if __name__ == "__main__":
    main()
