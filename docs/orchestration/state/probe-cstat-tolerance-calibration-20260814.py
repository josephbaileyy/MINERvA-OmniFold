"""Calibration: does the predeclared tolerance false-alarm on two CORRECT implementations?

This is the one test that can invalidate the threshold in COMPARATOR-PREDECLARATION. If two
legitimate, genuinely different formulations of the same sample covariance disagree by more
than TOL_CORR_ABS, the tolerance is too tight and will manufacture a finding out of rounding.

Also re-checks the tier-3 eigenvalue metric, which the mutation run reported as ~1.0 for a
PERMUTATION -- a similarity transform that provably preserves the spectrum. Either the
mutation broke the spectrum (it cannot) or my metric is broken (it can).
"""
import sys
import pathlib

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import compare_cstat_implementations as H  # noqa: E402

rng = np.random.default_rng(20260814)
x = rng.normal(size=(H.N_REPLICAS, H.N_CELLS))
x[:, 228] = 0.0

# --- four legitimate, genuinely different routes to the SAME sample covariance -------------
a = np.cov(x, rowvar=False, ddof=1)

xc = x - x.mean(axis=0, keepdims=True)
b = (xc.T @ xc) / (H.N_REPLICAS - 1)                       # explicit BLAS dgemm

c = np.einsum("ki,kj->ij", xc, xc) / (H.N_REPLICAS - 1)    # einsum, different contraction

d = np.zeros((H.N_CELLS, H.N_CELLS))                       # accumulate outer products
for k in range(H.N_REPLICAS):
    d += np.outer(xc[k], xc[k])
d /= (H.N_REPLICAS - 1)

names = {"np.cov": a, "Xc.T@Xc": b, "einsum": c, "sum-of-outer": d}


def corr_scaled_worst(p, q):
    dg = np.clip(np.diag(p), 0, None)
    scale = np.sqrt(np.outer(dg, dg))
    diff = np.abs(p - q)
    out = np.zeros_like(diff)
    np.divide(diff, scale, out=out, where=scale > 0)
    return float(out.max()), float(diff.max())


print("=== worst correlation-scaled disagreement between CORRECT implementations ===")
print(f"    predeclared TOL_CORR_ABS = {H.TOL_CORR_ABS:.0e}\n")
keys = list(names)
worst_overall = 0.0
for i in range(len(keys)):
    for j in range(i + 1, len(keys)):
        cs, ab = corr_scaled_worst(names[keys[i]], names[keys[j]])
        worst_overall = max(worst_overall, cs)
        verdict = "OK" if cs <= H.TOL_CORR_ABS else "*** WOULD FALSE-ALARM ***"
        print(f"  {keys[i]:14s} vs {keys[j]:14s}: corr-scaled={cs:.3e}  abs={ab:.3e}  {verdict}")

print(f"\n  worst across all pairs = {worst_overall:.3e}")
print(f"  headroom to tolerance  = {H.TOL_CORR_ABS / worst_overall:.1f}x"
      if worst_overall > 0 else "  (bit-identical)")

# --- the tier-3 eigenvalue metric --------------------------------------------------------
print("\n=== tier-3 eigenvalue metric, checked against a PERMUTATION ===")
p = np.empty(H.N_CELLS, dtype=int)
for i in range(H.N_PT):
    for j in range(H.N_PP):
        p[i * H.N_PP + j] = j * H.N_PT + i
ap = a[np.ix_(p, p)]
ea, ep = np.linalg.eigvalsh((a + a.T) / 2), np.linalg.eigvalsh((ap + ap.T) / 2)
de = np.abs(ea - ep)
ne = np.maximum(np.abs(ea), np.abs(ep))
rel = np.zeros_like(de)
np.divide(de, ne, out=rel, where=ne > 0)
k = int(np.argmax(rel))
print("  a permutation is a similarity transform: the spectrum MUST be preserved")
print(f"  worst RELATIVE eig difference = {rel.max():.3e}   at index {k}")
print(f"    eig_A={ea[k]:.6e}  eig_permuted={ep[k]:.6e}   <-- both numerically ZERO")
print(f"  worst ABSOLUTE eig difference = {de.max():.3e}")
print(f"  |lambda_max|                  = {np.abs(ea).max():.6e}")
print(f"  worst absolute, scaled by |lambda_max| = {de.max() / np.abs(ea).max():.3e}")
print(f"\n  n eigenvalues with |lambda| < 1e-10 * |lambda_max| : "
      f"{int((np.abs(ea) < 1e-10 * np.abs(ea).max()).sum())} of {ea.size}")
print("  -> the relative metric is dividing by numerical zero. The metric is wrong,")
print("     not the mutation. Absolute-scaled-by-lambda_max is the correct form.")
