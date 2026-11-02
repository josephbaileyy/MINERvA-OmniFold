"""E2 sensitivity readouts (DECISION-20261102-joseph-cmodel-keep-carbon-state-effect.md, item 4), from existing products
with E2's bound functions (fd_gencmp_e2 at M''' 372db765, imported read-only from $R2/deploy), at 0 node-h on a login
node in RE-1's environment. Inputs: the pinned data product, with-block and E-1 readouts (rest_matrices, e1_readout,
C0), cmodel_5d.json (pinned), and the run's own e2.json (read O_NOATIME, sha256 checked) for S_CH.
(1) chi2 with C_model removed (S = 0) and doubled (C_rest + C_model passed as the rest, with the carbon S), for the
    four corner predictions, both arms, both kinds; controls: the carbon and CH rows reproduce e2.json's exactly.
(2) per-cell sigma, carbon S against CH S: of C_model alone and of each arm's whole matrix."""
import hashlib, json, os, sys
sys.path.insert(0, "nd-unfolding")
import numpy as np
import fd_gencmp_e2 as E2

E2J, E2J_SHA = "/pscratch/sd/j/josephrb/gencmp-e2a1-20261102/chi2/e2.json", \
    "0aa73ebf654242ca07aa754f92670d582b097ae50fbcbc2a33e38b588d94985e"
fd = os.open(E2J, os.O_RDONLY | os.O_NOATIME)
with os.fdopen(fd, "rb") as fh:
    raw = fh.read()
assert hashlib.sha256(raw).hexdigest() == E2J_SHA, "e2.json is not the run's record"
e2 = json.loads(raw)
cm = json.loads(E2.A.pinned(E2.CMODEL5, E2.CMODEL5_SHA256, "cmodel_5d.json", "C0"))
S_c, S_ch = np.asarray(cm["S"], float), np.asarray(e2["S_CH"], float)
ctrl = {"S_carbon is cmodel_5d.json's S (bitwise)": bool(np.array_equal(S_c, np.asarray(e2["S_carbon"], float)))}
f, Cma, arms = E2.rest_matrices()
ctrl["C2: diag(f) S^T S diag(f) is C_model_abs (1e-12)"] = E2.c2_ok(f, S_c, Cma)
out = {"chi2": {}, "sigma": {}}
sig = lambda C: np.sqrt(np.diag(C))  # noqa: E731
Mc, Mch = E2.model_abs(f, S_c), E2.model_abs(f, S_ch)
for arm, C_rest in arms.items():
    r1 = E2.e1_readout(arm)
    carbon, ch = E2.chi2_rows(r1, f, C_rest, S_c), E2.chi2_rows(r1, f, C_rest, S_ch)
    removed = E2.chi2_rows(r1, f, C_rest, np.zeros_like(S_c))
    doubled = E2.chi2_rows(r1, f, C_rest + Mc, S_c)
    for p in E2.CORNER:
        for k in ("total", "shape_only"):
            ctrl[f"{arm} {p} {k}: carbon and CH reproduce e2.json exactly"] = (
                carbon[p][k] == e2["chi2"][arm][p][k]["carbon"] and ch[p][k] == e2["chi2"][arm][p][k]["CH"])
    ctrl[f"{arm}: C3 (carbon S reproduces E-1, 1e-10)"] = not E2.c3_failures(r1, carbon)
    out["chi2"][arm] = {p: {k: {"removed": removed[p][k], "carbon": carbon[p][k], "doubled": doubled[p][k],
                                "CH": ch[p][k]} for k in ("total", "shape_only")} for p in E2.CORNER}
    sc, sch = sig(C_rest + Mc), sig(C_rest + Mch)
    rel = sch / sc - 1
    i = int(np.argmax(np.abs(rel)))
    out["sigma"][f"{arm}_total"] = {"max_abs_rel_change": float(abs(rel[i])), "signed": float(rel[i]), "cell": i,
                                    "sigma_over_f_carbon": float(sc[i] / f[i]), "sigma_over_f_CH": float(sch[i] / f[i]),
                                    "per_cell_rel_change": rel.tolist()}
mc, mch = sig(Mc) / f, sig(Mch) / f            # C_model alone, as a fraction of f (= the column norms of S)
d = mch - mc
i, j = int(np.argmax(np.abs(d))), int(np.argmax(np.abs(mch / mc - 1)))
out["sigma"]["C_model"] = {"max_abs_change_over_f": float(abs(d[i])), "signed_change_over_f": float(d[i]), "cell": i,
                           "sigma_over_f_carbon": float(mc[i]), "sigma_over_f_CH": float(mch[i]),
                           "max_abs_rel_change": float(abs(mch[j] / mc[j] - 1)), "cell_rel": j,
                           "per_cell_sigma_over_f_carbon": mc.tolist(), "per_cell_sigma_over_f_CH": mch.tolist(),
                           "n_cells": int(f.size), "cells_with_zero_carbon_sigma": int((mc == 0).sum())}
out.update(controls=ctrl, all_pass=all(ctrl.values()),
           env={"python": sys.version.split()[0], "numpy": np.__version__})
print(json.dumps(out, indent=1))
