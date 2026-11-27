#!/usr/bin/env python3
"""Copy UOMNI's four top-level TParameters into each slim omnifile (p2p3/AMENDMENT-P2P3.md A3), under PyROOT.

    python3 slim_tparams.py UOMNI SLIM [SLIM ...]

uproot reads TParameter<T> but cannot write it, so this one step uses ROOT, in the root_6_28 env. It opens UOMNI
read-only, a plain in-place read under cov2d's (C) grant, covered by the job's atime/mtime log. Each slim is opened
in UPDATE mode, and dataPOTUsed, mcPOTUsed, hasTruthOnlyMisses and nTruthOnlyMisses are written under the same
names. It refuses if UOMNI or a slim cannot be opened, a TParameter is missing, or a slim already has one. The values
are proven afterwards by `p3_slim.py check`/`patchcheck`, which read them back with uproot and compare them with
UOMNI's. Exit 0 done, 2 refused.
"""
import sys

TPARAMS = ("dataPOTUsed", "mcPOTUsed", "hasTruthOnlyMisses", "nTruthOnlyMisses")


def copy(root, uomni, slims):
    fin = root.TFile.Open(uomni, "READ")
    if not fin or fin.IsZombie():
        return f"cannot open {uomni}"
    try:
        objs = {n: fin.Get(n) for n in TPARAMS}
        missing = [n for n, o in objs.items() if not o]
        if missing:
            return f"{uomni} lacks {missing}"
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
    finally:
        fin.Close()
    return None


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) < 2:
        print("REFUSED: usage: slim_tparams.py UOMNI SLIM [SLIM ...]")
        return 2
    import ROOT
    ROOT.gROOT.SetBatch(True)
    err = copy(ROOT, argv[0], argv[1:])
    if err:
        print(f"REFUSED: {err}")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
