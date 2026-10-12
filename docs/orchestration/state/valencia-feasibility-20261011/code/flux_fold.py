#!/usr/bin/env python3
"""Integrator cross-check of the flux-averaged predecessor cross section (diagnostic).

sigma(E) is computed on a log grid, interpolated linearly in log E, and folded
with the piecewise-constant corrected ME-FHC flux (phi_t) over 0-100 GeV.
Reports per-nucleon values in the authors' convention (cos^2 theta_C inside W, as
NuWro and GENIE also use) and, as a diagnostic, with an extra V_ud^2 factor.
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import valencia_tensor_xsec as vx  # noqa: E402

tables = vx.load_tables(Path(sys.argv[1]), "C12")
d = np.load(sys.argv[2])
grid = np.geomspace(150.0, 100000.0, int(sys.argv[5]) if len(sys.argv) > 5 else 36)
sig = []
for E in grid:
    s = vx.sigma(tables, E, "nu", "C12", int(sys.argv[3]))
    sig.append(sum(s.values()))
sig = np.array(sig)
edges = d["edges"] * 1000.0
dens = d["phi_t_density"]
num = 0.0
for lo, hi, ph in zip(edges[:-1], edges[1:], dens):
    e = np.linspace(lo, hi, 201)
    se = np.interp(np.log(np.maximum(e, 1.0)), np.log(grid), sig, left=0.0, right=sig[-1])
    num += ph * np.trapz(se, e) / 1000.0  # density is per GeV
avg = num / float(d["Phi_t"])
out = {"grid_MeV": grid.tolist(), "sigma_per_nucleon_cm2": sig.tolist(),
       "flux_avg_per_nucleon_cm2_authors_convention": avg,
       "flux_avg_per_nucleon_cm2_with_extra_Vud2": avg * vx.VUD ** 2, "n_sub": int(sys.argv[3])}
Path(sys.argv[4]).write_text(json.dumps(out, indent=1) + "\n")
print(json.dumps({k: v for k, v in out.items() if not isinstance(v, list)}))
print("sigma(E) at 1, 3, 10, 30, 100 GeV:", [float(np.interp(np.log(x), np.log(grid), sig)) for x in (1e3, 3e3, 1e4, 3e4, 1e5)])
