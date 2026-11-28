#!/usr/bin/env python3
"""Write UOMNI's four top-level TParameters into each slim omnifile, from the slim build's record, under PyROOT
(p2p3/AMENDMENT-P2P3.md A3; cov2d's (C) amendment 3: UOMNI is opened once, by p3_slim.py build).

    python3 slim_tparams.py BUILD.json SLIM [SLIM ...]

uproot reads TParameter<T> but cannot write it, so this one step uses ROOT, in the root_6_28 env. It never opens
UOMNI. BUILD.json's "uomni" record holds each TParameter's class and value, read in build's single open. Each slim
is opened in UPDATE mode, and dataPOTUsed, mcPOTUsed, hasTruthOnlyMisses and nTruthOnlyMisses are written under the
same names, as a TParameter of the recorded class with the recorded value. It refuses if the record lacks one, names
a class other than TParameter<double|int|long>, or a slim cannot be opened or already has one. `p3_slim.py verify`
then reads the class and value of each back with uproot and compares them with the record. Exit 0 done, 2 refused.
"""
import json
import re
import sys

TPARAMS = ("dataPOTUsed", "mcPOTUsed", "hasTruthOnlyMisses", "nTruthOnlyMisses")
CLASS = re.compile(r"^TParameter<(double|int|long)>$")


def write(root, record, slims):
    tp = record.get("uomni", {}).get("tparams", {})
    if set(tp) != set(TPARAMS):
        return f"the record's TParameters are {sorted(tp)}, not {list(TPARAMS)}"
    objs = {}
    for n in TPARAMS:
        m = CLASS.match(str(tp[n].get("class", "")))
        if not m or "value" not in tp[n]:
            return f"the record's {n} is {tp[n]!r}"
        objs[n] = root.TParameter(m.group(1))(n, tp[n]["value"])
    for s in slims:
        fout = root.TFile.Open(s, "UPDATE")
        if not fout or fout.IsZombie():
            return f"cannot open {s}"
        try:
            have = [n for n in TPARAMS if fout.Get(n)]
            if have:
                return f"{s} already has {have}"
            fout.cd()
            for n in TPARAMS:
                objs[n].Write(n)
            print(f"wrote {list(TPARAMS)} into {s}")
        finally:
            fout.Close()
    return None


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) < 2:
        print("REFUSED: usage: slim_tparams.py BUILD.json SLIM [SLIM ...]")
        return 2
    try:
        record = json.load(open(argv[0]))
    except (OSError, ValueError) as e:
        print(f"REFUSED: cannot read {argv[0]}: {e}")
        return 2
    import ROOT
    ROOT.gROOT.SetBatch(True)
    err = write(ROOT, record, argv[1:])
    if err:
        print(f"REFUSED: {err}")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
