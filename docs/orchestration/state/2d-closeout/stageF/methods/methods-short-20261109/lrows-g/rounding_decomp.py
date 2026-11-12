"""L-row G3 (referee6 major 7): how much of the reported statistical variance is the rounding jitter that every
bootstrap replica carries, per cell on R00-R15, from committed readouts only (diagonal). Run from the repository root:
python3 -I <this file>.

Inputs: RS1's R0 readout (rs1_r0.json: sigma_J_over_f, the jitter-to-jitter spread of the data result over f, from
I0's 20 data jitters; sigma_S1_stat_rel, S1's bootstrap statistical sigma over f; R0a = their ratio) and the reported
covariance C_total + C_resp + C_PL5D (fd_data_product_cpl.json), for the scale against the total.
Assumption (RS1 R0b's, rs1_r0.json [assumption]): the jitter and the remaining sampling variances add per cell, so
the bootstrap variance without the jitter is sigma_S1^2 - sigma_J^2. Diagonal only: no committed product holds the
jitter covariance's off-diagonals (I0 recorded the per-cell spread only), so the change in the statistical
covariance's correlations is not computed here; G3's price is in the readout."""
import hashlib
import json
from pathlib import Path

import numpy as np

FD = Path("docs/orchestration/state/measurement-paper/5d-community-20261024")
R0 = FD / "fd/rounding-stability-20261106/receipts/full-a1/read/rs1_r0.json"
DP = FD / "fd/with-cpl/data-product/fd_data_product_cpl.json"
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()  # noqa: E731
r = json.loads(R0.read_text())
dp = json.loads(DP.read_text())
sj, ss = np.array(r["sigma_J_over_f"]), np.array(r["sigma_S1_stat_rel"])
R0a = np.array(r["R0a"]); assert np.allclose(R0a, sj / ss, rtol=1e-12, atol=0)
frac_var = R0a ** 2                                  # share of the bootstrap variance that is jitter
ss_nojit = ss * np.sqrt(1 - frac_var)                # the bootstrap sigma without the jitter (R0b's assumption)
f = np.array(dp["f"]); C = np.array(dp["matrices"]["C_total_plus_C_resp_plus_C_PL5D"])
s_tot = np.sqrt(np.diag(C)) / f
tot_drop = 1 - np.sqrt(1 - (sj / s_tot) ** 2)        # relative drop in the reported sigma if the jitter left it
cells = r["cells"]
q = lambda x: {"median": float(np.median(x)), "min": float(x.min()), "max": float(x.max()),  # noqa: E731
               "max_cell": cells[int(x.argmax())]}
out = {"schema": "lrows-g3-rounding/1", "inputs_sha256": {"rs1_r0": sha(R0), "dp_cpl": sha(DP)}, "cells": cells,
       "assumption": r["assumption"],
       "jitter_share_of_bootstrap_variance": frac_var.tolist(), "summary_jitter_share": q(frac_var),
       "bootstrap_sigma_rel_with_jitter": ss.tolist(), "bootstrap_sigma_rel_without_jitter": ss_nojit.tolist(),
       "bootstrap_sigma_drop": (1 - np.sqrt(1 - frac_var)).tolist(), "summary_bootstrap_sigma_drop": q(1 - np.sqrt(1 - frac_var)),
       "reported_sigma_rel": s_tot.tolist(), "reported_sigma_drop_without_jitter": tot_drop.tolist(),
       "summary_reported_sigma_drop": q(tot_drop),
       "off_diagonals": "not computable from committed products (I0 per-cell spread only)",
       "price": {"exact_jitter_covariance": "the 20 data-jitter unfolds I0 graded, if they survive on pscratch: a login read, "
                                            "0 node-h, sha256 of the read script to the director first",
                 "bootstrap_without_jitter": "S1's 50 statistical replicas (s1_assembly meta stat_replicas) rerun without "
                                             "the jitter: 50 unfolds, at Part 1's 0.027-0.029 node-h per item about 1.4-1.5 "
                                             "node-h (FD-1B-PRECHECK-FD-DECLARATION.md:229-230)"}}
Path(__file__).with_name("rounding_decomp.json").write_text(json.dumps(out, indent=1) + "\n")
for k in ("summary_jitter_share", "summary_bootstrap_sigma_drop", "summary_reported_sigma_drop"):
    print(k, {a: (round(b, 4) if isinstance(b, float) else b) for a, b in out[k].items()})
