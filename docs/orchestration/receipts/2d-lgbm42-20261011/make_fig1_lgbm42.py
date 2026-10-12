#!/usr/bin/env python3
"""Regenerate the article's Fig. 1 with the LightGBM seed-42 2D central value (decision 2026-10-11).

The released arrays (fig_arrays.npz, sha256 72394a2b...) carry the exact-split central value as `ours_v`.
Fig. 1 reads only `ours_v` for the OmniFold curve, its ratios, the residual map and the residual
statistics (make_figs.py fig1()). This script replaces `ours_v` on the 205 reported cells with the
LightGBM seed-42 values committed in remote_reduce.json (`central.CV42_universe_file`, float64, from
2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root, sha256 4f5a1b6d...), writes the modified arrays to --tmp,
and calls make_figs.py on them. With --cov (cov2d_blocks_205.npz, exported read-only on NERSC from the
VL170/VL172 universe+bootstrap rollup hCov_combined and the ML block hCov2D_reported; identities in
cov2d_blocks_205.json) it also adds `cov_ours`, their sum on the 224-bin grid, so Fig. 1 draws this
analysis's own +-1 sigma band. The blocks reproduce the committed per-cell sigmas (remote_reduce.json) to
2e-16 and the 6.8707 % budget median against the seed-42 central value.

  python3 make_fig1_lgbm42.py --npz fig_arrays.npz --reduce remote_reduce.json \
      --make-figs publication/release/figs/make_figs.py --values docs/analysis-note/values.tex \
      --tmp <dir> --outdir <dir>
"""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

ap = argparse.ArgumentParser()
for k in ("npz", "reduce", "make_figs", "values", "tmp", "outdir"):
    ap.add_argument("--" + k.replace("_", "-"), required=True, type=Path)
ap.add_argument("--cov", type=Path, default=None)
a = ap.parse_args()
digest = hashlib.sha256(a.npz.read_bytes()).hexdigest()
assert digest.startswith("72394a2b"), digest
z = dict(np.load(a.npz, allow_pickle=False))
rr = json.loads(a.reduce.read_text())
gids = np.array([pt * 16 + pz for pt, pz in rr["cells"]])
mask = np.diag(z["cov_stat"]) > 0
assert mask.sum() == 205 and np.array_equal(np.sort(gids), np.flatnonzero(mask))
ctl = np.zeros(224); ctl[gids] = rr["central"]["E_C"]
assert np.array_equal(ctl[mask], z["ours_v"][mask]), "E_C in remote_reduce must equal the released ours_v"
new = np.zeros_like(z["ours_v"]); new[gids] = rr["central"]["CV42_universe_file"]
z["ours_v"] = new
if a.cov is not None:
    cz = np.load(a.cov, allow_pickle=False)
    c205 = cz["universe_plus_boot"] + cz["ml"]
    assert c205.shape == (205, 205)
    sab = {k: np.asarray(v, float) for k, v in rr["sigma_abs"].items()}
    assert np.allclose(np.sqrt(np.diag(cz["ml"])), sab["ml"], rtol=1e-12, atol=0), "ML block cell order"
    quad = np.sqrt(sab["universe"] ** 2 + sab["boot_vl170"] ** 2 + sab["ml"] ** 2)
    assert np.allclose(np.sqrt(np.diag(c205)), quad, rtol=1e-12, atol=0), "total covariance cell order"
    c224 = np.zeros((224, 224)); c224[np.ix_(gids, gids)] = c205
    z["cov_ours"] = c224
a.tmp.mkdir(parents=True, exist_ok=True)
out_npz = a.tmp / "fig_arrays_lgbm42.npz"
np.savez(out_npz, **z)
sys.exit(subprocess.call([sys.executable, str(a.make_figs), "--npz", str(out_npz), "--outdir", str(a.outdir),
                          "--values", str(a.values)]))
