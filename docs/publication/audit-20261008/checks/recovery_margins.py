"""Audit check: margins of the recovered (lost-seed) pseudo-experiments to the observed statistics.
Uses the RC4 replay's statistic functions; recovered draws = union seeds not in frozen seeds."""
import json, sys
from pathlib import Path
import numpy as np
rc = Path(sys.argv[1]); sys.path.insert(0, str(rc / "code"))
import replay_inference as rp
zf = np.load(rc / "data/frozen/inference_sufficient.npz"); zu = np.load(rc / "data/recovery-union/inference_sufficient.npz")
man = json.loads((rc / "data/recovery-union/inference_sufficient.npz.manifest.json").read_text())
V, f_data, coefs = zu["V"], zu["f_data"], man["shift_coefficients"]
rows = []; nrec_tot = 0
for key, nm in man["nulls"].items():
    sf = set(zf[f"seeds__{key}"].tolist()); su = zu[f"seeds__{key}"]
    rec = np.array([s not in sf for s in su.tolist()])
    nrec_tot += int(rec.sum())
    F, seeds = zu[f"F__{key}"][rec], su[rec]
    mu, var, dom = zu[f"mu__{key}"], zu[f"var__{key}"], zu[f"dom__{key}"].astype(bool)
    S = zu[f"S__{key}"] if f"S__{key}" in zu.files else None
    tt_o, ts_o = rp.statistics(f_data[None, :], mu, var, V, dom, 0, draw=False)
    variants = [(f"c={c}", (c * S if S is not None else 0.0)) for c in (coefs if S is not None else [0.0])]
    if nm["m1"] is not None:
        d1, ka, kr = zu[f"d1__{key}"], nm["m1"]["kappa"], nm["m1"]["kappa_robust"]
        variants += [(f"m1+{ka}", ka * d1), (f"m1-{ka}", -ka * d1), (f"m1+{kr} (robust)", kr * d1), (f"m1-{kr} (robust)", -kr * d1)]
    for name, sv in variants:
        tt, ts = rp.statistics(F + sv, mu, var, V, dom, nm["surrogate_seed0"], seeds=seeds)
        rows.append((key, "total", name, float(tt_o[0]), float(tt.max()), float(tt_o[0] - tt.max()), int((tt >= tt_o[0]).sum())))
        rows.append((key, "shape", name, float(ts_o[0]), float(ts.max()), float(ts_o[0] - ts.max()), int((ts >= ts_o[0]).sum())))
rows.sort(key=lambda r: r[5])
print("recovered draws total:", nrec_tot)
print("n rows", len(rows), "any recovered >= obs:", sum(r[6] for r in rows))
for r in rows[:6]:
    print(f"{r[0]:22s} {r[1]:5s} {r[2]:18s} T_obs={r[3]:.2f} max_rec={r[4]:.2f} gap={r[5]:.2f} n>=obs={r[6]}")
