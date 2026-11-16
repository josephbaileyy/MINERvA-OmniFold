"""L-row G2 (referee6, the GEANT "middle option"): the share of GEANT_Neutron and GEANT_Proton in the reported 5D
covariance on R00-R15, and their contribution to the fake-data bias tests' chi2. Read-only, from committed files only;
for the readout, never printed (Joseph decides). Run from the repository root: python3 -I <this file>.

Inputs (each sha256 printed):
- S1's universe unfolds for the two bands, s1/readout/s1_assembly/S1_GEANT_{Neutron,Proton}_{0,1}.npz, through the
  float64 U of the committed H2 definition (as s1_assemble builds its blocks, s1_assemble.py:303), each band's block by
  s1_assemble.mat_cov over its two universes. Control: the four detector bands so rebuilt reproduce S1's committed
  detector relative sigma (s1_assembly.json [relative_sigma/detector]).
- The reported covariance C_total + C_resp + C_PL5D and its parts, fd/with-cpl/data-product/fd_data_product_cpl.json.
- C_model's vertex shifts S (C_model = sum_j s_j s_j^T, C_abs = diag(x) C_model diag(x)), nd-unfolding/pv-ladder/readouts/
  cmodel_5d.json, for the leave-own-vertex-out grade matrices.
- F0b's graded truths, fd/with-cpl/readout/fd_f0b_readout.json: bias b (relative), noise_sigma, own_vertex, and the
  committed chi2. The grade is chi2 = b^T (C^(T)/(f f^T) + C_x/(f f^T) + N_T)^-1 b (fd_f0_regrade.py:14-15, :31),
  C^(T) = C_e + diag(f) sum_{j != own(T)} s_j s_j^T diag(f), C_x = C_resp + C_PL5D, and N_T the full covariance of
  the truth's mean (fd_f0_regrade.py:217, :792). Only N_T's diagonal is committed (noise_sigma), so N_T is taken
  diagonal here and the committed chi2 is reproduced only approximately: each truth's relative error is recorded, and
  the run refuses if a graded truth's exceeds 1 %. The exact N_T is on pscratch (the regrade's per-experiment
  products); a 0 node-h login read would make it exact. Each truth is also given at N_T = 0, the noise-free limit.
The GEANT contribution is chi2(C) - chi2(C - G), G the two bands' blocks (part of C_e): the change if the two bands
were dropped from the grade matrix. It is a sensitivity of the metric, not a test."""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, "nd-unfolding")
import s1_assemble as sa  # noqa: E402

FD = Path("docs/orchestration/state/measurement-paper/5d-community-20261024")
S1D = FD / "s1/readout/s1_assembly"
FILES = {"s1_json": FD / "s1/readout/s1_assembly.json", "dp_cpl": FD / "fd/with-cpl/data-product/fd_data_product_cpl.json",
         "cmodel": Path("nd-unfolding/pv-ladder/readouts/cmodel_5d.json"),
         "f0b": FD / "fd/with-cpl/readout/fd_f0b_readout.json",
         "definition": Path("nd-unfolding/pv-ladder/readouts/h2_definition.json")}
BANDS = ("GEANT_Neutron", "GEANT_Pion", "GEANT_Proton", "MinosEfficiency")
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()  # noqa: E731
U = sa.functional_matrix(sa.fine_map(FILES["definition"]))
blk, univ_sha = {}, {}
for b in BANDS:
    ps = [S1D / f"S1_{b}_{i}.npz" for i in (0, 1)]
    univ_sha.update({str(p): sha(p) for p in ps})
    blk[b] = sa.mat_cov(np.array([U @ sa.xs(p) for p in ps]))
dp = json.loads(FILES["dp_cpl"].read_text())
M = {k: np.array(v) for k, v in dp["matrices"].items()}
f = np.array(dp["f"])
s1j = json.loads(FILES["s1_json"].read_text())
det_rel = np.sqrt(np.diag(sum(blk.values()))) / f
c_det = float(np.max(np.abs(det_rel / np.array(s1j["relative_sigma"]["detector"]) - 1)))
assert c_det < 1e-10, c_det
G = blk["GEANT_Neutron"] + blk["GEANT_Proton"]
C_rep = M["C_total_plus_C_resp_plus_C_PL5D"]
cells = s1j["cells"]
share = {"GEANT_Neutron": np.diag(blk["GEANT_Neutron"]) / np.diag(C_rep), "GEANT_Proton": np.diag(blk["GEANT_Proton"]) / np.diag(C_rep)}
share["both"] = np.diag(G) / np.diag(C_rep)
share_Ce = np.diag(G) / np.diag(M["C_e"])
sig_drop = 1 - np.sqrt(1 - share["both"])            # relative drop in the reported sigma if the two were removed
trace_share = float(np.trace(G / np.outer(f, f)) / np.trace(C_rep / np.outer(f, f)))
# the bias tests
cm = json.loads(FILES["cmodel"].read_text())
x = np.array(cm["x"]); assert np.max(np.abs(x / f - 1)) < 1e-12
Sk = dict(zip(cm["vertices"], np.array(cm["S"])))
ff = np.outer(f, f)
Cx = (M["C_resp"] + M["C_PL5D"]) / ff
f0b = json.loads(FILES["f0b"].read_text())
truths, worst = [], 0.0
for t in f0b["truths"]:
    b = np.array(t["bias"]); N = np.diag(np.array(t["noise_sigma"]) ** 2)
    Cm = sum(np.outer(s, s) for k, s in Sk.items() if k != t["own_vertex"])
    C = M["C_e"] / ff + Cm + Cx + N
    c2 = float(b @ np.linalg.solve(C, b))
    rel = abs(c2 / t["grade"]["chi2"] - 1)
    if t["graded"]:
        worst = max(worst, rel)
    c2g = float(b @ np.linalg.solve(C - G / ff, b))
    C0 = C - N
    c20, c20g = float(b @ np.linalg.solve(C0, b)), float(b @ np.linalg.solve(C0 - G / ff, b))
    z, zg = b / np.sqrt(np.diag(C)), b / np.sqrt(np.diag(C - G / ff))
    truths.append({"truth": t["name"], "graded": t["graded"], "own_vertex": t["own_vertex"], "chi2": c2,
                   "chi2_committed": t["grade"]["chi2"], "reproduction_rel_error": rel,
                   "chi2_without_geant_np": c2g, "delta_chi2": c2g - c2, "delta_chi2_rel": (c2g - c2) / c2,
                   "at_N0": {"chi2": c20, "chi2_without_geant_np": c20g, "delta_chi2": c20g - c20},
                   "max_abs_z": float(np.max(np.abs(z))), "max_abs_z_without": float(np.max(np.abs(zg))),
                   "cells_abs_z_gt_2": [cells[i] for i in np.flatnonzero(np.abs(z) > 2)],
                   "cells_abs_z_gt_2_without": [cells[i] for i in np.flatnonzero(np.abs(zg) > 2)]})
assert worst < 0.01, worst
out = {"schema": "lrows-g2-geant/1", "label": "readout only; not for print without Joseph (the director, 2026-11-12)",
       "inputs_sha256": {**{k: sha(p) for k, p in FILES.items()}, **univ_sha},
       "controls": {"detector_relative_sigma_max_rel_diff": c_det, "f0b_graded_chi2_max_rel_diff_diagonal_N": worst},
       "cells": cells,
       "diag_share_of_reported": {k: v.tolist() for k, v in share.items()},
       "diag_share_of_C_e": share_Ce.tolist(),
       "reported_sigma_relative_drop_without_both": sig_drop.tolist(),
       "fractional_trace_share_of_reported": trace_share,
       "summary": {"both_share_median": float(np.median(share["both"])), "both_share_max": float(share["both"].max()),
                   "both_share_max_cell": cells[int(share["both"].argmax())],
                   "sigma_drop_median": float(np.median(sig_drop)), "sigma_drop_max": float(sig_drop.max())},
       "bias_tests": truths}
Path(__file__).with_name("geant_share.json").write_text(json.dumps(out, indent=1) + "\n")
print(f"controls: detector sigma {c_det:.1e}; F0b graded chi2 reproduced to {worst:.1e} (diagonal N)")
s = out["summary"]
print(f"diag share of reported, both bands: median {s['both_share_median']:.4f}, max {s['both_share_max']:.4f} ({s['both_share_max_cell']}); "
      f"sigma drop median {s['sigma_drop_median']:.4f}, max {s['sigma_drop_max']:.4f}; fractional trace share {trace_share:.4f}")
for c, a, n, p in zip(cells, share["both"], share["GEANT_Neutron"], share["GEANT_Proton"]):
    print(f"  {c} both {a:.4f} (n {n:.4f}, p {p:.4f})")
for t in truths:
    print(f"  {t['truth']:14s} {'graded' if t['graded'] else 'ungraded':8s} chi2 {t['chi2']:8.3f} (committed {t['chi2_committed']:8.3f}, "
          f"rel {t['reproduction_rel_error']:.1e}) -> {t['chi2_without_geant_np']:8.3f} (delta {t['delta_chi2']:+.3f}, "
          f"{100 * t['delta_chi2_rel']:+.1f} %); N=0 delta {t['at_N0']['delta_chi2']:+.3f}; |z|>2 {t['cells_abs_z_gt_2']} -> {t['cells_abs_z_gt_2_without']}")
