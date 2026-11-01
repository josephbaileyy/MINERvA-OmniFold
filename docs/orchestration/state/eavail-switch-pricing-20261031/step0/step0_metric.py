"""Step-0 shift vectors in the reported covariance's metric (first order; committed inputs and the step-0 outputs).

For each shift (prior level, step0.json truth_denom; first-order unfolded, step0b.json), Delta_c = (relative change of
cell c) x f_c with f the data product's; reports per-cell Delta_c/sigma_c and the full-covariance norm
sqrt(Delta^T M^-1 Delta) by Cholesky, for M = C_total + C_resp (data product) and M + C_PL5D (fd/with-cpl).
Usage: python3 -I -B step0_metric.py <repo> <step0.json> <step0b.json>
"""
import json, sys
from pathlib import Path
import numpy as np
R = Path(sys.argv[1]); FD = R / "docs/orchestration/state/measurement-paper/5d-community-20261024/fd"
dp = json.loads((FD / "data-product/fd_data_product.json").read_text())
f = np.asarray(dp["f"], float)
mats = {"C_total_plus_C_resp": np.asarray(dp["matrices"]["C_total_plus_C_resp"], float)}
j = json.loads((FD / "with-cpl/data-product/fd_data_product_cpl.json").read_text())
k = [x for x in j["matrices"] if x.endswith("plus_C_PL5D")][0]; mats[k] = np.asarray(j["matrices"][k], float)
shifts = {"prior_level": json.loads(Path(sys.argv[2]).read_text())["truth_denom"]["cells_rel_change"],
          "first_order_unfolded": json.loads(Path(sys.argv[3]).read_text())["a_unfolded_cells_rel_change"]}
out = {}
for name, rel in shifts.items():
    d = np.asarray(rel, float) * f
    o = {}
    for mn, M in mats.items():
        y = np.linalg.solve(np.linalg.cholesky(M), d)
        o[mn] = {"norm_sqrt_dCinvd": float(np.sqrt(y @ y)), "dCinvd": float(y @ y),
                 "per_cell_over_sigma": [round(float(v), 4) for v in d / np.sqrt(np.diag(M))],
                 "max_abs_over_sigma": float(np.max(np.abs(d / np.sqrt(np.diag(M))))),
                 "quadrature_of_per_cell": float(np.sqrt(np.sum((d / np.sqrt(np.diag(M))) ** 2)))}
    out[name] = o
print(json.dumps(out, indent=1))
