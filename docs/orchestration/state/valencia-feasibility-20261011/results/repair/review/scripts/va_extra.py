#!/usr/bin/env python3
"""Reviewer checks: (1) fixed code vs committed flux-fold sigma(E) on its whole grid (old per-E
sign rule must have picked -1 everywhere for the 'not rerun' claim); (2) free-nucleon V-A trace
sanity of the derived convention. Usage: va_extra.py DCOPY NUWRO_SRC OUT_JSON"""
import json
import sys
from pathlib import Path

import numpy as np

DC = Path(sys.argv[1])
sys.path.insert(0, str(DC / "code"))
sys.path.insert(0, str(DC / "tests"))
import valencia_tensor_xsec as vx  # noqa: E402

out = {}
tables = vx.load_tables(Path(sys.argv[2]), "C12")
ff = json.loads((DC / "results/integrator-C12-nu-fluxfold.json").read_text())
rows = []
for E, old in zip(ff["grid_MeV"], ff["sigma_per_nucleon_cm2"]):
    new = sum(vx.sigma(tables, E, "nu", "C12", ff["n_sub"]).values())
    # interference alone (W12 only) for the margin of the old rule
    only = {ch: {c: (a if c == "W12" else np.zeros_like(a)) for c, a in comps.items()}
            for ch, comps in tables.items()}
    inter = sum(vx.sigma(only, E, "nu", "C12", 2).values())
    rows.append({"E": E, "committed": old, "fixed": new,
                 "rel": (new / old - 1) if old else (0.0 if new == 0 else float("inf")),
                 "interference_nsub2": inter})
out["fluxfold_n4_g36"] = rows
out["fluxfold_max_abs_rel"] = max(abs(r["rel"]) for r in rows if r["committed"])
out["fluxfold_any_nonpositive_interference"] = [r["E"] for r in rows if r["interference_nsub2"] <= 0]

# free nucleon n -> p at rest, pure V-A, massless-structure trace, same Dirac matrices as C1
import check_va_convention as cv  # noqa: E402
M = 938.9
res = []
for E, om, q in ((1000.0, 300.0, 600.0), (3000.0, 500.0, 1000.0), (800.0, 150.0, 450.0)):
    p = np.array([M, 0, 0, 0.0])
    pp = np.array([M + om, 0, 0, q])
    P = cv.ONE - cv.GAM5
    A, B = cv.slash(pp) + M * cv.ONE, cv.slash(p) + M * cv.ONE
    GU = cv.GAM_UP
    W = np.array([[np.trace(A @ GU[a] @ P @ B @ GU[b] @ P) for b in range(4)] for a in range(4)]) / 8
    imW12 = W[1, 2].imag
    w = {"W00": np.array([W[0, 0].real]), "W03": np.array([W[0, 3].real]), "W11": np.array([W[1, 1].real]),
         "W33": np.array([W[3, 3].real]), "W12": np.array([imW12])}
    s_nu, i_nu = vx.lepton_contraction(E, np.array([om]), np.array([q]), w, "nu")
    s_nb, i_nb = vx.lepton_contraction(E, np.array([om]), np.array([q]), w, "nubar")
    # cross-check against full trace contraction with the trace W (no table encoding involved)
    k, kp = cv.kinematics(E, om, q)
    full_nu = np.sum(cv.trace_lepton(k, kp, vx.M_MU, "nu") * W)
    full_nb = np.sum(cv.trace_lepton(k, kp, vx.M_MU, "nubar") * W)
    res.append({"E": E, "omega": om, "q": q, "ImW12": imW12, "ReW12": W[1, 2].real,
                "W21_plus_W12": abs(W[1, 2] + W[2, 1]),
                "interference_nu": float(i_nu[0]), "LW_nu_code": float(s_nu[0] + i_nu[0]),
                "LW_nubar_code": float(s_nb[0] + i_nb[0]),
                "LW_nu_full_trace": [full_nu.real, full_nu.imag], "LW_nubar_full_trace": [full_nb.real, full_nb.imag]})
out["free_nucleon"] = res
Path(sys.argv[3]).write_text(json.dumps(out, indent=1, default=float) + "\n")
print(json.dumps({k: v for k, v in out.items() if k != "fluxfold_n4_g36"}, indent=1, default=float))
