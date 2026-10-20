#!/usr/bin/env python3
"""MP3-C production sizing (variances only, no H cross-section value is read): the B4 ratio of ONE probe task,
(1/13) sqrt(U^2 sumw2_H) / ((12/13) sqrt(U^2 sumw2_C12)) per cell of GiBUU's 72-cell domain, and the task count K
at which the projected ratio ratio_1 / sqrt(K) (sumw2 of the mean over K runs scales as 1/K) is <= 1/3 in every cell.
Usage (root_6_28): python3 mp3c_size.py PROBE_FinalEvents.dat INPUTS_DIR
"""
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402

import mp3c_build as b  # noqa: E402
import s5p_joint as sj  # noqa: E402

fe, inp = sys.argv[1], Path(sys.argv[2])
b.gfr.import_root()
g5 = b.gfr.load_g5(b.gfr.DEFAULTS["gen5d_tree"])
b.G5 = g5
a, M, nev, enu, al = b.events([fe], 1)
z, _, _ = b.gfr.load_phi_t(b.sup.OUT)
ge, fc, pg, cut, step = b.gibuu_density(b.gfr.DEFAULTS["gibuu_jobcard"])
r, _ = b.weights(a, ge, pg, z["edges"], z["phi_t_density"], float(z["Phi_t"]))
_, vh, nh = b.build(g5, a, M, r)
design = json.loads((inp / "design.json").read_text())
supported = json.loads((inp / "s5c_contract.json").read_text())["measurement"]["partition_J"]["supported_cells"]
U, names, pz_index = sj.j_matrix({}, supported)
dom = pz_index <= 1
_, var_c = sj.prediction(design["nulls"]["GiBUU_2019"]["prediction"], U)
ratio1 = (b.F_H * np.sqrt((U ** 2) @ vh)) / (b.F_C * np.sqrt(var_c))
rd = ratio1[dom]
K = int(np.ceil((rd.max() * 3) ** 2))
nH = ((U > 0).astype(float) @ nh)[dom]
print(json.dumps({"probe_events": nev, "probe_in_grid": int(nh.sum()), "ratio_1task": {"min": float(rd.min()),
      "median": float(np.median(rd)), "max": float(rd.max())}, "worst_cell": names[int(np.where(dom)[0][np.argmax(rd)])],
      "cells_with_zero_probe_events": int(np.sum(nH == 0)), "K_for_bound_at_worst_cell": K,
      "ratio_projected_at_K80": {"median": float(np.median(rd) / np.sqrt(80)), "max": float(rd.max() / np.sqrt(80))}}))
