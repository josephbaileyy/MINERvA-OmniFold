#!/usr/bin/env python3
"""PRD read 1, R2: reproduce Table III's total and shape-only chi2 for the 16-cell predictions from committed operands, and
read why freeing the normalization barely lowers them for GENIE + MEC and the Tune v1. Local arithmetic, nothing printed in
the paper: the drop from adding 100 f f^T is the residual's squared component along f in C^-1's metric, so the GLS scale
of r = f - g along f, with its sigma, says how large that component is.
Operands: the reported matrix C_total + C_resp + C_PL5D of fd_data_product_cpl.json (d6752d2c) and, per prediction, f, g
and V_g (sigma_Vg_over_f) of Stage G's fd_g_readout.json (a19009e0).
usage: python3 -I r2_check.py <worktree>"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

wt = Path(sys.argv[1])
B = wt / "docs/orchestration/state/measurement-paper/5d-community-20261024/fd"
paths = {"dp": B / "with-cpl/data-product/fd_data_product_cpl.json",
         "g": B / "gencmp-e/rerun1/chain/chdefs/with/readout/fd_g_readout.json"}
for k, p in paths.items():
    print(f"{k}: {p.relative_to(wt)} sha256 {hashlib.sha256(p.read_bytes()).hexdigest()[:8]}")
dp, g = (json.loads(p.read_text()) for p in paths.values())
C0 = np.array(dp["matrices"]["C_total_plus_C_resp_plus_C_PL5D"])
for p in g["predictions"]:
    if p["n_cells"] != 16:
        continue
    f, gg = np.array(p["f"]), np.array(p["g"])
    r = f - gg
    C = C0 + np.diag((np.array(p["sigma_Vg_over_f"]) * f) ** 2)
    Ci = np.linalg.inv(C)
    chi = r @ Ci @ r
    chis = r @ np.linalg.inv(C + 100 * np.outer(f, f)) @ r
    a, sa = (f @ Ci @ r) / (f @ Ci @ f), (f @ Ci @ f) ** -0.5
    below = sum(x < 0 for x in p["g_over_f_minus_1"])
    print(f"{p['name']:11s} total {chi:7.2f} (readout {p['total']['chi2']:.2f})  shape-only {chis:7.2f} "
          f"(readout {p['shape_only']['chi2']:.2f})  drop {chi - chis:6.2f}  GLS scale {a:+.3f} +- {sa:.3f}  "
          f"g < f in {below} of 16 cells")
