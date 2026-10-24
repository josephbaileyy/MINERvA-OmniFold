#!/usr/bin/env python3
"""RE-2 part C: Fig. 1's central values on the 205 reported cells, by name (RE2-DECLARATION-C.md §3.8, P13).

    python3 -I re2c_reduce.py --ec E_C.root --eu E_U.root --er E_R.root --remote-reduce remote_reduce.json --out R.json

Fig. 1 does not read a ROOT file: make_fig1_q.py swaps the drawn central value in from a reduction JSON. The committed
reduction, `next-preparation-20261009/two-d-path/operands/remote_reduce.json` (2ecfc243...), names E_U
"CV42_universe_file". This writes the same cell list and the same three-object read for E_C, E_U and E_R, each
under its own name, so make_fig1 can name E_R explicitly.

Control (it stops): the E_C and E_U values written here must equal the committed reduction's "E_C" and
"CV42_universe_file" exactly, on the same cells in the same order. The read is remote_reduce.py's (th2, the
row-major E_C > 0 cell order).

MEASURES: nothing new; a re-read of three pinned products. Login node, root_6_28.
"""
import argparse
import hashlib
import json
import sys

import numpy as np

PINS = {
    "ec": "142a45b0efc753d91e95376c28ac3f6a477d582014a919e49d6d71079a127fd5",
    "eu": "4f5a1b6d44b9e7212b233650bb00bfb626ae65461e3bf8033cd67866dbd7eb2c",
    "er": "a5c13fc38d64242bc9ee459fac87568a2f97fddf7a3ac97cc6f91eb4c2a31cef",
    "remote_reduce": "2ecfc243ab4a6c508a69df0e231676019106f3ad86f34e3ac3423f7bd2bca9ce",
}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 22), b""):
            h.update(blk)
    return h.hexdigest()


def th2(path):
    """remote_reduce.py's th2(), on hXSec2D."""
    import ROOT
    ROOT.gROOT.SetBatch(True)
    f = ROOT.TFile.Open(path)
    if not f or f.IsZombie():
        raise SystemExit(f"[FAIL] cannot open {path}")
    h = f.Get("hXSec2D")
    nx, ny = h.GetNbinsX(), h.GetNbinsY()
    a = np.array([[h.GetBinContent(i + 1, j + 1) for j in range(ny)] for i in range(nx)])
    f.Close()
    return a


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for k in PINS:
        ap.add_argument("--" + k.replace("_", "-"), dest=k, required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    inputs = {}
    for k, want in PINS.items():
        got = sha256(getattr(a, k))
        if got != want:
            raise SystemExit(f"[FAIL] {k}: sha256 {got} != pinned {want}")
        inputs[k] = {"path": getattr(a, k), "sha256": got}
    cen = {"E_C": th2(a.ec), "E_U": th2(a.eu), "E_R": th2(a.er)}
    reported = cen["E_C"] > 0
    for k in ("E_U", "E_R"):
        if not np.array_equal(cen[k] > 0, reported):
            raise SystemExit(f"[FAIL] {k} > 0 is not the E_C > 0 reported set")
    idx = np.argwhere(reported)          # row-major (pT bin, pz bin), the paper's GlobalID order
    out = {"cells": [[int(i), int(j)] for i, j in idx],
           "central": {k: [float(v[i, j]) for i, j in idx] for k, v in cen.items()},
           "inputs": inputs}
    rr = json.load(open(a.remote_reduce))
    ctl = {"cells_equal": rr["cells"] == out["cells"],
           "E_C_equal": rr["central"]["E_C"] == out["central"]["E_C"],
           "E_U_equal_CV42_universe_file": rr["central"]["CV42_universe_file"] == out["central"]["E_U"]}
    out["control_vs_committed_remote_reduce"] = ctl
    if not all(ctl.values()):
        raise SystemExit(f"[FAIL] control: {ctl}")
    with open(a.out, "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
        f.write("\n")
    print(json.dumps({"n_cells": len(out["cells"]), "control": ctl, "out": a.out, "sha256": sha256(a.out)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
