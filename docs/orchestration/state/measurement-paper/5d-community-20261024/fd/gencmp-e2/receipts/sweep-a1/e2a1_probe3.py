"""E2-A1 sweep probe, C2 and C3 on the cluster in RE-1's environment, from E2's deploy at M'' (chi2_rows, model_abs and
the C2/C3 comparisons unchanged by E2-A1 but for being named functions). Committed repo files only. Read-only."""
import json, sys, platform
from pathlib import Path
R = Path("/pscratch/sd/j/josephrb/gencmp-e2-20261102")
sys.path[:0] = [str(R / "deploy/nd-unfolding"), str(R / "deploy/nd-unfolding/pv-ladder")]
import numpy as np, fd_gencmp_e2 as E2, fd_cpl_addition as A
cm = json.loads(E2.CMODEL5.read_text()); S = np.asarray(cm["S"], float)
dp = json.loads(A.pinned(E2.DP, E2.DP_SHA256, "data product", "C0")); blk = np.load(E2.BLOCK, allow_pickle=False)
f = np.asarray(blk["f"], float); Ce, Cma = (np.asarray(dp["matrices"][k], float) for k in ("C_e", "C_model_abs"))
arms = {"with": Ce + np.asarray(blk["C_resp"], float) + np.asarray(blk["C_PL5D"], float), "nopl": Ce + np.asarray(blk["C_resp"], float)}
out = {"numpy": np.__version__, "python": sys.version.split()[0], "machine": platform.node(),
       "C2": bool(np.all(np.abs(E2.model_abs(f, S) - Cma) <= 1e-12 * np.abs(Cma).max())), "C3_rel": {}}
for arm, C in arms.items():
    r1 = json.loads((E2.E1 / arm / "readout" / "fd_g_readout.json").read_text())
    rows = E2.chi2_rows(r1, f, C, S)
    for p in r1["predictions"]:
        if p["name"] in rows:
            for k in ("total", "shape_only"):
                out["C3_rel"][f"{arm} {p['name']} {k}"] = (rows[p["name"]][k] - p[k]["chi2"]) / abs(p[k]["chi2"])
out["C3_pass_1e-10"] = all(abs(v) <= E2.TOL for v in out["C3_rel"].values())
out["C3_max_abs_rel"] = max(abs(v) for v in out["C3_rel"].values())
print(json.dumps(out))
