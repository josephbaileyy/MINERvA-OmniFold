#!/usr/bin/env python3
"""m5/Fm7: the injected per-(E_avail, W) change of the withheld truths W1-W3, from the fetched s5e truths.

Usage (repo root): python -I m5_injected.py <members/w_truth_z.npz> <out m5_injected.json>

Definition, the lower-capacity panel's (s5n_truth_check.py): injected = M1 @ x(W) / M1 @ x(nominal) - 1, x the
full-sample true cross section on the 65,856 fine cells, M1 the analysis's (E_avail, W) projection
(s5c_coverage.reported_functionals, rows EW0..EW41).

Why the fetched half-sample truths give the full-sample x exactly. s5n_pseudo.true_xsec divides half B's
r-weighted truth by half B's completeness ofin_B / denom_nd, so per fine cell x = (flux/POT/nucleon factors) *
denom_nd * (sum_B w r / sum_B w): seed-independent wherever half B populates the cell and r is constant inside
it, zero where half B is empty. Checked, not assumed: (1) every cell's nonzero values agree across a set's
seeds to RTOL; (2) the union support over all 100 products is counted, and any cell of that support empty in
every seed of one set is reported (its value for that set is then unknown, and the output says so).
Controls: W1 reweights by E_avail bin only (r = c * rho_k, amplitude 1), so (1 + injected)/rho_k must be one
constant over every EW cell; W2 reweights by (E_avail, W) cell, so (1 + injected)/rho_EW must be one constant.
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

REPO = Path.cwd()
sys.path.insert(0, str(REPO / "nd-unfolding"))
import s5c_coverage  # noqa: E402

RTOL = 1e-12
src, out = Path(sys.argv[1]), Path(sys.argv[2])
z = np.load(src, allow_pickle=False)
contract = REPO / "docs/orchestration/state/s5c/contract.json"
U, names = s5c_coverage.reported_functionals(json.loads(contract.read_text()))
assert names[:42] == [f"EW{i}" for i in range(42)] and names[42] == "EW_all_ones"
M1 = U[:42]

x_all = {s: z[f"{s}__xtrue_flat"] for s in ("nominal", "W1", "W2", "W3")}
support = np.zeros(M1.shape[1], bool)
for x in x_all.values():
    support |= (x != 0).any(0)
rec = {"input_path": str(src.resolve().relative_to(REPO.resolve())), "input_bytes_digest_sha256": hashlib.sha256(src.read_bytes()).hexdigest(),
       "contract_sha256": hashlib.sha256(contract.read_bytes()).hexdigest(),
       "s5c_coverage_sha256": hashlib.sha256((REPO / "nd-unfolding/s5c_coverage.py").read_bytes()).hexdigest(),
       "rtol": RTOL, "support_cells_union_100": int(support.sum()), "sets": {}}
full = {}
for s, x in x_all.items():
    nzm = x != 0
    mx = np.where(nzm, x, -np.inf).max(0)
    mn = np.where(nzm, x, np.inf).min(0)
    have = nzm.any(0)
    dev = float(np.max(np.abs(mx[have] - mn[have]) / np.abs(mx[have])))
    if dev > RTOL:
        raise SystemExit(f"STOP: {s}: nonzero values differ across seeds by {dev} > {RTOL}")
    full[s] = np.where(have, mx, 0.0)
    missing = support & ~have
    rec["sets"][s] = {"n_seeds": int(x.shape[0]), "max_rel_dev_nonzero": dev,
                      "cells_zero_in_some_seed": int((have & ~nzm.all(0)).sum()),
                      "support_cells_empty_in_every_seed": int(missing.sum()),
                      "support_cells_empty_EW": sorted({int(i) for i in np.flatnonzero(M1[:, missing].any(1))})}
f0 = M1 @ full["nominal"]
inj = {w: (M1 @ full[w]) / f0 - 1 for w in ("W1", "W2", "W3")}
rec["injected_change_pct"] = {w: (100 * v).tolist() for w, v in inj.items()}
rec["max_abs_injected_pct"] = {w: [round(float(np.max(np.abs(100 * v))), 3), f"EW{int(np.argmax(np.abs(v)))}"]
                               for w, v in inj.items()}


def control(w, ratio_path, key, per_cell):
    rp = REPO / ratio_path
    rho = np.asarray(json.loads(rp.read_text())[key], float)
    c = (1 + inj[w]) / per_cell(rho)
    spread = float((c.max() - c.min()) / c.mean())
    return {"ratio_path": ratio_path, "ratio_bytes_digest_sha256": hashlib.sha256(rp.read_bytes()).hexdigest(),
            "constant_mean": float(c.mean()), "constant_rel_spread": spread, "pass": spread < 1e-9}


ie = np.repeat(np.arange(7), 6)  # EW index = ie * 6 + iw (s5n_truth_check.py: cell = ie * n_W + iw)
rec["control_W1"] = control("W1", "docs/orchestration/state/s5n/eavail-ratio-nuwro-over-genie.json",
                            "shape_ratio", lambda rho: rho[ie])
rec["control_W2"] = control("W2", "docs/orchestration/state/s5e/w2-genie-mec-over-cv-eavailW.json",
                            "shape_ratio", lambda rho: rho.ravel())
out.write_text(json.dumps(rec, indent=1) + "\n")
print(json.dumps({k: v for k, v in rec.items() if k != "injected_change_pct"}, indent=1))
ok = rec["control_W1"]["pass"] and rec["control_W2"]["pass"] and all(
    v["support_cells_empty_in_every_seed"] == 0 for v in rec["sets"].values())
print("M5-INJECTED " + ("OK" if ok else "CHECK FAILED"))
sys.exit(0 if ok else 5)
