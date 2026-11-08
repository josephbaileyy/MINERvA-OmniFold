#!/usr/bin/env python3
"""R4's power: the published covariance's own uncertainty on the p_par step ratio (DECLARATION.md section 5).

Covariance only: no unfolded result is read and nothing is compared. It reads the rounded TEXT release (cross section
and covariances on the 205 StatOnly cells) and the bound run re-measures the same quantity on the precision ROOT
(readout R4 sigma_pub). sigma_pub(st) = (1 + st) G, so with no group noise R4 reads "differs" only for
st >= 3G / (1 - 3G), and "matches" up to 2G / (1 - 2G). Usage: python3 -B r4_power_txt.py
"""
import os
import sys
import types

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import ROOT  # noqa: F401
except ImportError:
    sys.modules["ROOT"] = types.ModuleType("ROOT")
import numpy as np  # noqa: E402

import per_period_benchmark as P  # noqa: E402
import test_per_period_benchmark as T  # noqa: E402  (the text-release loaders)

m = P.import_reused()
met, w_lo, w_hi = P.step_ops(m, T.CELLS, T.PRED)
for name, cov in (("TotalCovariance", T.TOT), ("StatOnlyCovariance", T.STAT)):
    V = cov[np.ix_(T.MASK, T.MASK)]
    G = P.step_sigma_pub(0.0, w_lo, w_hi, T.PRED, V)
    print(f"{name:20s} G = sigma_pub(st=0) = {G:.5f}   'differs' needs st >= {3 * G / (1 - 3 * G):.4f}"
          f"   'matches' up to st = {2 * G / (1 - 2 * G):.4f}")
