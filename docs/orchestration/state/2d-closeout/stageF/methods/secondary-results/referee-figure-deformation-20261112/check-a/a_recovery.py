#!/usr/bin/env python3
"""Check A of the figure referee read (the director, 2026-11-12): does the unfolded (E_avail, W) cell move toward the
changed truth? Descriptive, from committed records only. Usage (repo root): python -I a_recovery.py <out.json>

Per cell, i = injected change = truth(changed)/truth(nominal) - 1 over the full simulation (GiBUU: truth_check.json
eavail_shape M1_ratio - 1, the same truth, ratio file and amplitude as the assessment's eavail_gibuu; W1-W3:
pscr-20261112/derived/m5_injected.json). r = residual = mean over the 20 pseudo-experiments of (unfolded - truth)/truth
against each experiment's own (changed) half-sample truth (assess_receipt.json points.<truth>.per_functional.mean_rel),
r_nom the same at the nominal truth (points.nominal, 40 experiments). The unfolded value against nominal is
(1 + r)(1 + i) - 1; the response to the change, net of the nominal closure, is (1 + r)(1 + i) - (1 + r_nom), and its
recovered fraction f = response / i: 0 <= f <= 1 partial recovery, f > 1 overshoot, f < 0 movement opposite to the
change. Cells: supported (stage1_inspect.json mc.EW reported) with |i| > 2 %. The product uses the full-sample i
with the half-sample residual; the two truths agree in every fine cell populated in a half (pscr README reading 1).
"""
import hashlib, json, sys
from pathlib import Path
import numpy as np

R = Path.cwd()
SRC = {"truth_check": "docs/orchestration/state/s5n/stage1/truth_check.json",
       "assess": "docs/orchestration/state/s5e/cand/assess_receipt.json",
       "m5": "docs/orchestration/state/2d-closeout/stageF/methods/methods-short-20261109/pscr-20261112/derived/m5_injected.json",
       "s1i": "docs/orchestration/state/s5p/stage1/stage1_inspect.json"}
d = {k: json.loads((R / p).read_text()) for k, p in SRC.items()}
rep = np.array(d["s1i"]["mc"]["EW"]["reported"], bool)
P = d["assess"]["points"]
rn = np.array(P["nominal"]["per_functional"]["mean_rel"][:42])
sn = np.array(P["nominal"]["per_functional"]["se_rel"][:42])
inj = {"GiBUU": np.array(d["truth_check"]["departures"]["eavail_shape"]["M1_ratio"][:42]) - 1}
inj.update({w: np.array(d["m5"]["injected_change_pct"][w]) / 100 for w in ("W1", "W2", "W3")})
key = {"GiBUU": "eavail_gibuu", "W1": "W1", "W2": "W2", "W3": "W3"}
out = {"schema": "figure-referee-check-a/1", "label": "descriptive only",
       "sources": {k: {"path": p, "bytes_digest_sha256": hashlib.sha256((R / p).read_bytes()).hexdigest()} for k, p in SRC.items()},
       "nominal_closure_max_abs_supported": float(np.abs(rn[rep]).max()), "shapes": {}}
for k in ("GiBUU", "W1", "W2", "W3"):
    i = inj[k]; r = np.array(P[key[k]]["per_functional"]["mean_rel"][:42])
    s = np.array(P[key[k]]["per_functional"]["se_rel"][:42])
    u = (1 + r) * (1 + i) - 1
    resp = (1 + r) * (1 + i) - (1 + rn)
    ok = rep & (np.abs(i) > 0.02)
    f = np.full(42, np.nan); f[ok] = resp[ok] / i[ok]
    # standard error of f from the two ensembles' standard errors of the mean (i is exact)
    sf = np.full(42, np.nan); sf[ok] = np.sqrt((s[ok] * (1 + i[ok])) ** 2 + sn[ok] ** 2) / np.abs(i[ok])
    near = ok & ((np.abs(f) < 3 * sf) | (np.abs(f - 1) < 3 * sf))
    out["shapes"][k] = {"n_cells": int(ok.sum()), "n_opposite": int((f[ok] < 0).sum()),
                        "n_partial": int(((f[ok] >= 0) & (f[ok] <= 1)).sum()), "n_overshoot": int((f[ok] > 1).sum()),
                        "f_median": float(np.median(f[ok])), "sigma_f_max": float(np.nanmax(sf)),
                        "n_within_3sigma_of_a_class_boundary": int(near.sum()),
                        "within_3sigma_cells": [f"EW{c}" for c in np.flatnonzero(near)],
                        "n_within_3sigma_of_f0": int((ok & (np.abs(f) < 3 * sf)).sum()),
                        "n_within_3sigma_of_f1": int((ok & (np.abs(f - 1) < 3 * sf)).sum()),
                        "max_abs_residual_supported": float(np.max(np.abs(r[rep]))),
                        "max_abs_residual_supported_cell": f"EW{int(np.flatnonzero(rep)[np.argmax(np.abs(r[rep]))])}",
                        "EW29": {"injected": float(i[29]), "residual": float(r[29]), "unfolded_vs_nominal": float(u[29]),
                                 "f": float(f[29]) if ok[29] else None},
                        "opposite_cells": [f"EW{c}" for c in np.flatnonzero(ok) if f[c] < 0],
                        "per_cell": [{"cell": f"EW{c}", "injected": float(i[c]), "residual": float(r[c]),
                                      "unfolded_vs_nominal": float(u[c]), "f": (float(f[c]) if ok[c] else None),
                                      "sigma_f": (float(sf[c]) if ok[c] else None)} for c in range(42)]}
Path(sys.argv[1]).write_text(json.dumps(out, indent=1) + "\n")
for k, s in out["shapes"].items():
    print(k, {x: s[x] for x in ("n_cells", "n_opposite", "n_partial", "n_overshoot", "f_median", "n_within_3sigma_of_a_class_boundary", "within_3sigma_cells")})
