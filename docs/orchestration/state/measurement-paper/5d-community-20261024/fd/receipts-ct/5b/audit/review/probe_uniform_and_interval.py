"""Probe: (1) the normalization candidate's shape ratio under the committed g_sig weights, for S1's construction
outer(NF f, NF f)/outer(f, f) on random f ~ 1e-39 (is it reliably below UNIFORM_REL = 1e-12?);
(2) would test_nu_eff_and_the_interval's assertions (lo < 1, hi > 2) pass for a 95% instead of a 68% interval?"""
import json, math, sys
from pathlib import Path
import numpy as np
W = Path(sys.argv[1]); sys.path.insert(0, str(W / "nd-unfolding"))
import fd_ct_5b_audit as au
from scipy import stats
ro = json.loads((W / "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/readout/fd_ct_5b_periods.json").read_text())
sig = {X: np.asarray(ro["g_vs_5A"]["periods"][X]["g_5b_noise_sigma"]) for X in au.PER}
worst = 0.0
for s in range(500):
    f = np.random.default_rng(s).uniform(0.2, 5.0, 16) * 1e-39
    B = np.outer(0.014 * f, 0.014 * f) / np.outer(f, f)
    ms = au.modes(B, au.CAND_TOP, au.CAND_FRAC)
    d = math.sqrt(ms[0][0]) * ms[0][1]
    worst = max(worst, min(au.shape_norm_ratio(d, 1 / sig[X] ** 2) for X in ("PB", "PC")))
    assert len(ms) == 1
print("normalization: worst shape ratio over 500 f:", worst, "(UNIFORM_REL 1e-12); modes per draw: 1")
nu = au.nu_eff(ro["constants"]["exposure_share"])
lo95, hi95 = math.sqrt(nu / stats.chi2.ppf(0.975, nu)), math.sqrt(nu / stats.chi2.ppf(0.025, nu))
print(f"95% interval at nu={nu:.4f}: [{lo95:.3f}, {hi95:.3f}] -> test's lo<1 and hi>2 pass: {lo95 < 1 and hi95 > 2}")
