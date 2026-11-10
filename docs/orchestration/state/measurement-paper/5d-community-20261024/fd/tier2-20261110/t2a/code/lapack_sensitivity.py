#!/usr/bin/env python3
"""The LAPACK-sensitivity measurement behind T2-BINDING-1 addendum 1 (2026-11-10): on the committed C_T only, with 300
SYNTHETIC error vectors (N(0, C_T) draws, seed 11, plus a 0.3 sigma_c offset; not the toys), how much does
fd_1b_null.chi2_nonnull's mean move under (i) an eps-level symmetric perturbation of C_T (2.2e-16 x max|C_T|, seeds
100-104) and (ii) scipy.linalg.eigh(driver="evr") in place of numpy's eigh? Usage: lapack_sensitivity.py <code> <blocks dir>"""
import sys
from pathlib import Path
import numpy as np
import numpy.linalg as la
import scipy
import scipy.linalg as sl
code, bdir = Path(sys.argv[1]), Path(sys.argv[2])
sys.path.insert(0, str(code / "nd-unfolding"))
import fd_1b_null as nl  # noqa: E402
print("numpy", np.__version__, "scipy", scipy.__version__)
for T in ("AR23", "G18"):
    C = np.load(bdir / T / f"blocks_{T}.npz", allow_pickle=False)["C_T"]
    rng = np.random.default_rng(11)
    lam, _ = la.eigh(C)
    E = rng.multivariate_normal(np.zeros(205), C, size=300, method="eigh") + 0.3 * np.sqrt(np.diag(C))
    base, ndf = nl.chi2_nonnull(E, C)
    pert = []
    for s in range(5):
        P = np.random.default_rng(100 + s).normal(size=C.shape); P = (P + P.T) / 2
        c2, n2 = nl.chi2_nonnull(E, C + 2.2e-16 * np.abs(C).max() * P)
        pert.append(f"ndf {n2} rel {abs(c2.mean() / base.mean() - 1):.2e}")
    l2, V2 = sl.eigh(C, driver="evr")
    keep = l2 > nl.RANK_REL * l2.max(); Z = E @ V2[:, keep]
    c3 = np.sum(Z * Z / l2[keep], axis=1)
    print(f"{T}: ndf {ndf}; lambda_min/lambda_max {lam[lam > 0].min() / lam.max():.3g}; eps perturbations: {pert}; "
          f"evr: ndf {int(keep.sum())}, mean-chi2 rel diff {abs(c3.mean() / base.mean() - 1):.2e}")
