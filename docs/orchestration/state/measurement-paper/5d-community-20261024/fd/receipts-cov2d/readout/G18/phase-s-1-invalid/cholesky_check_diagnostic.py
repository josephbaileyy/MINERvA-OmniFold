"""Diagnostic for G18 phase S attempt 1 (INVALID): does fd_1b_mc.grade's Cholesky equality (fd_1b_mc.py:662-667: when
ndf == 205, max |chi2_nonnull / chi2_cholesky - 1| must be <= 1e-9) hold on G18's committed C_T for ANY errors?
Reads only the committed blocks (../blocks_<T>.npz); the errors are synthetic (no toy is read). Usage:
    python cholesky_check_diagnostic.py <readout dir>     (the directory holding G18/ and AR23/)"""
import hashlib
import sys
from pathlib import Path

import numpy as np

RANK_REL, TOL = 1e-12, 1e-9          # fd_1b_null.RANK_REL; fd_1b_mc.grade's tolerance
d = Path(sys.argv[1])
for T in ("G18", "AR23"):
    p = d / T / f"blocks_{T}.npz"
    if not p.exists():
        print(f"{T}: {p} absent"); continue
    C = np.load(p)["C_T"]
    lam, V = np.linalg.eigh(C)
    keep = lam > RANK_REL * lam.max()
    ndf = int(keep.sum())
    print(f"{T}: blocks sha256 {hashlib.sha256(p.read_bytes()).hexdigest()}; min/max eig {lam[0] / lam[-1]:.6e}; "
          f"cond {lam[-1] / lam[0]:.4e}; ndf {ndf}")
    if ndf != C.shape[0]:
        print(f"{T}: ndf < {C.shape[0]}, so grade skips the Cholesky equality"); continue
    L = np.linalg.cholesky(C)
    rng = np.random.default_rng(1)
    for name, E in (("E ~ N(0, C_T)", rng.multivariate_normal(np.zeros(C.shape[0]), C, size=300, method="eigh")),
                    ("E independent N(0, sigma_c)", rng.standard_normal((300, C.shape[0])) * np.sqrt(np.diag(C)))):
        Z = E @ V[:, keep]
        chi2 = np.sum(Z * Z / lam[keep], axis=1)
        ref = np.sum(np.linalg.solve(L, E.T) ** 2, axis=0)
        m = float(np.max(np.abs(chi2 / ref - 1)))
        print(f"{T}: 300 synthetic rows, {name}: max |chi2/ref - 1| = {m:.3e} ({'over' if m > TOL else 'within'} {TOL:g})")
print("numpy", np.__version__)
