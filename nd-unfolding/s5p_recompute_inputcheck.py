"""Mechanical checks of s5p_recompute's geometry and inputs on the real frozen inputs (read-only).

Run on a login node from a directory holding s5p_recompute.py, design.json, s5c_contract.json (the s5c contract),
null-mnvtune_v1-J.json (state/s5p/ratios/nullsJ) and units.json (state/s5p/stage3/prefreeze). Checks: J integrals of
the MnvTune prediction against the committed coarse-null integrals; delta_M1 = f(fine) - f(mid) against the frozen
M1 files; the rounding-noise and lateral scales; the predictions' J totals. Prints JSON; decides nothing.
"""
import json, sys, time
import numpy as np
sys.path.insert(0, ".")
import s5p_recompute as R
design = json.load(open("design.json")); c = json.load(open("s5c_contract.json"))
t0 = time.time()
ev = R.Evaluator(design, "/pscratch/sd/j/josephrb/s5p-20260926/stage3/V/V-s3v.npz", c, log=lambda *a: None)
out = {"init_s": time.time() - t0, "n_cells": ev.geom.n, "gibuu_domain": int(ev.geom.domain("pz_lt_6").size)}
nj = json.load(open("null-mnvtune_v1-J.json"))
mu, var = ev.prediction("MnvTune_v1")
ref = np.asarray(nj["numerator_cell_integrals"], float)[[int(n[1:]) for n in ev.names]]
out["mnvtune_J_vs_nullsJ_max_rel"] = float(np.max(np.abs(mu / ref - 1)))
units = json.load(open("units.json"))
m1 = {}
for g, p in units["inputs"]["generators"].items():
    fine = ev.geom.integrate(R.load_x(p["fine"])); mid = ev.geom.integrate(R.load_x(p["mid"]))
    with np.load(design["m1_shift"][g]["path"]) as z:
        d = np.asarray(z["D_J"])
    m1[g] = {"max_abs_diff_over_max_abs": float(np.max(np.abs((fine - mid) - d)) / np.max(np.abs(d))),
             "fine_minus_mid_matches": bool(np.allclose(fine - mid, d, rtol=1e-12, atol=0))}
out["m1_reproduced"] = m1
out["s_num_median_rel"] = float(np.median(ev.sur.s_num / ev.f_data))
out["lateral_median_abs_rel"] = {b: float(np.median(np.abs(ev.sur.delta[i] / ev.f_data))) for i, b in enumerate(ev.bands)}
for key in design["nulls"]:
    mu, var = ev.prediction(key)
    out.setdefault("prediction", {})[key] = {"sum_J": float(mu.sum()), "median_rel_mc_sd": float(np.median(np.sqrt(var) / mu))}
print(json.dumps(out, indent=1))
