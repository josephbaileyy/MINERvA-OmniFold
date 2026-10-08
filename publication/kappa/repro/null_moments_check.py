#!/usr/bin/env python3
"""Extra reference check: per-variant null-T median and SD (which depend on every pseudo-experiment's draw)
against the frozen evaluator's recorded null_T_*_median/_sd, using kappa_repro.py's Null (imported).
Usage: null_moments_check.py <worktree> <rc4> <out.json>"""
import importlib.util, json, sys
import numpy as np
wt, rc4, out = sys.argv[1:4]
sys.dont_write_bytecode = True
sys.argv = ["kappa_repro.py", wt, rc4, "/dev/null"]
spec = importlib.util.spec_from_file_location("kappa_repro", __file__.replace("null_moments_check.py", "kappa_repro.py"))
kr = importlib.util.module_from_spec(spec); spec.loader.exec_module(kr)
si = kr.si
from pathlib import Path
res = {}
for rd, npz, exp in (("frozen", "data/frozen/inference_sufficient.npz", "expected/joint-evaluate.json"),
                     ("union", "data/recovery-union/inference_sufficient.npz", "expected/resolved-evaluate.json")):
    R = kr.Reading(Path(rc4) / npz); E = json.load(open(Path(rc4) / exp))
    worst = 0.0; n = 0
    for g, nl in R.nulls.items():
        for vname, v in E["tests"][g]["variants"].items():
            sh = float(vname) * nl.S if not vname.startswith("m1") else (1 if "+" in vname else -1) * 2.0 * nl.d1
            F = nl.F + sh; d = nl.dom
            tt = np.array([si.stat_total(F[i][d], nl.r_mu[i][d], nl.Winv) for i in range(nl.B)])
            ts = np.array([si.stat_shape(F[i][d], nl.r_mu[i][d], nl.W) for i in range(nl.B)])
            for s, t in (("total", tt), ("shape", ts)):
                for q, val in (("median", np.median(t)), ("sd", np.std(t))):
                    e = v[f"null_T_{s}_{q}"]; rel = abs(val - e) / abs(e); worst = max(worst, rel); n += 1
    res[rd] = {"n_compared": n, "max_rel_diff": worst}
    print(rd, res[rd], flush=True)
json.dump(res, open(out, "w"), indent=1)
