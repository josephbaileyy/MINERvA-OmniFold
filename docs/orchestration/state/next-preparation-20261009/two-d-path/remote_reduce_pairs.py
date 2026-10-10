"""Read-only login-node reduction: +/-1 sigma pair asymmetry in the two seed-42 2D sweeps.

Run from the Perlmutter canonical checkout root after `source setup_salloc_env.sh`:
    python3 - < remote_reduce_pairs.py > remote_reduce_pairs.json

For every two-universe band of uq/universes_full_list.txt it reads the adopted sweep
(uq/universe_sweep_fluxfix/) and the July background-aware sweep (uq/purity_newomni/), each against
its own matched CV, and prints,
per reported cell, the half-difference h = |x+ - x-|/2 (the MAT variance term for a pair) and the
signed common displacement A = (x+ + x-)/2 - x_CV, which the MAT convention does not count as variance.
It writes nothing on the cluster.
"""
import json
import os
import sys

import numpy as np
import ROOT

ROOT.gROOT.SetBatch(True)
B = "2d-unfolding"
SW = f"{B}/uq/universe_sweep_fluxfix"


def xsec(path):
    f = ROOT.TFile.Open(path)
    h = f.Get("hXSec2D")
    a = np.array([[h.GetBinContent(i + 1, j + 1) for j in range(h.GetNbinsY())] for i in range(h.GetNbinsX())])
    f.Close()
    return a


SWEEPS = {  # name: (directory, file prefix, matched CV)
    "adopted_fluxfix": (SW, "2d_xsec_MEFHC_5iter_lgbm_uni_full_", f"{B}/uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root"),
    "purity_newomni": (f"{B}/uq/purity_newomni", "2d_xsec_MEFHC_5iter_lgbm_pn_uni_",
                       f"{B}/uq/purity_newomni/2d_xsec_MEFHC_5iter_lgbm_pn_uni_CV.root"),
}
rep = xsec(f"{B}/2d_crossSection_omnifold_MEFHC_5iter.root") > 0
universes = [ln.strip() for ln in open(f"{B}/uq/universes_full_list.txt") if ln.strip() and not ln.startswith("#")]
bands = {}
for u in universes:
    band, idx = u.rsplit(":", 1)
    bands.setdefault(band, []).append(idx)
out = {"host": os.uname().nodename, "sweeps": {}}
for name, (sw, prefix, cvpath) in SWEEPS.items():
    cv = xsec(cvpath)[rep]
    pairs = {}
    for band, idxs in bands.items():
        if len(idxs) != 2:
            continue
        a = [xsec(f"{sw}/{prefix}{band}_{i}.root")[rep] for i in idxs]
        pairs[band] = {"h_abs": (np.abs(a[0] - a[1]) / 2).tolist(),
                       "A_signed": ((a[0] + a[1]) / 2 - cv).tolist()}
    out["sweeps"][name] = {"dir": sw, "cv": cvpath, "pairs": pairs}
json.dump(out, sys.stdout, sort_keys=True)
sys.stdout.write("\n")
