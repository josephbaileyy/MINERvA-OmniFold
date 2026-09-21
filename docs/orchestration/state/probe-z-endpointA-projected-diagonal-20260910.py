#!/usr/bin/env python3
"""Does a RELEASED projected uncertainty depend on the OFF-DIAGONAL entries of the
covariance it was projected from?

WHY THIS EXISTS.  `PACKET-20260910` argues (CATALOG.md:227 at 173baf44) that
"`cause3_corr`'s hazard is UNREALIZED -- no released consumer reads off-diagonal
structure".  Endpoint A releases Z's covariance AND its declared PROJECTED
uncertainties.  A projected uncertainty for destination bin i is

    sigma_i = sqrt( (M C M^T)_ii ) = sqrt( sum_{j,k} M_ij M_ik C_jk ),

so every off-diagonal C_jk whose j and k land in the same destination bin enters it.
This probe measures that on the PRODUCTION construction and the PRODUCTION function,
and it separates the effect from two things it could be confused with.

WHAT IS PRODUCTION HERE, AND WHAT IS MINE.
  * `uq_math.project_covariance`         -- imported, not reimplemented (:171-180 at 6f24fb00)
  * the `Mew` scatter-assign             -- copied verbatim in shape from
                                            `eavailW_covariance.py:404-406` at 6f24fb00
  * the axis edges                       -- `unfold_nd_omnifold_unbinned.py:97-119` (eavail 7, W 6, q3 7)
                                            `2d-unfolding/unfold_2d_omnifold_unbinned.py:29-33` (pt 14, pz 16)
  * the two covariances, and the arm sizes, are MINE and are declared as fixtures below.

DECLARED LIMITATION.  The real reported mask (10,694 of 65,856 cells, `x5flat > 0`)
lives in a cluster product that is not readable from this checkout, so ARM 1 uses a
small grid with FULL support and ARM 2 uses the real MEAN row support as a scalar.
Nothing in the conclusion depends on WHICH cells are reported -- only on some
destination row receiving at least two of them, which the geometry forces (10,694
reported cells into 42 destination bins).

Run from the repository root:  python3 docs/orchestration/state/probe-z-endpointA-projected-diagonal-20260910.py
"""
import os
import sys

import numpy as np

_ND = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))), "nd-unfolding")
sys.path.append(_ND)
from uq_math import project_covariance          # noqa: E402  PRODUCTION function

# ---- production axis edges (cited above) -------------------------------------------------
PT_EDGES = [0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55,
            0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50]
PZ_EDGES = [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0,
            6.0, 7.0, 8.0, 9.0, 10.0, 15.0, 20.0, 40.0, 60.0]
Q3_EDGES = [0.0, 0.2, 0.4, 0.6, 0.8, 1.2, 2.0, 100.0]
EA_EDGES = [0.0, 0.1, 0.2, 0.4, 0.8, 1.5, 3.0, 100.0]
W_EDGES = [0.0, 1.1, 1.4, 1.8, 2.2, 3.0, 100.0]

N_PT, N_PZ, N_Q3 = len(PT_EDGES) - 1, len(PZ_EDGES) - 1, len(Q3_EDGES) - 1
N_EA, N_W = len(EA_EDGES) - 1, len(W_EDGES) - 1
N_DEST = N_EA * N_W                       # 42 destination (E_avail, W) bins
N_GRID = N_PT * N_PZ * N_Q3 * N_EA * N_W  # 65,856 full 5D cells
N_REPORTED = 10694                        # app_statmethods.tex:640 / RANK-AND-INVERSION-20260810.md:88

_line = "-" * 92


def build_mew(i5p, i5z, i5e, i5q, i5w, dpt, dpz, dq3, n_dest, unit_weights=False):
    """The `eavailW_covariance.py:404-406` construction, shape-for-shape.

        Mew = np.zeros((n, report5.size))
        ewrow = i5e * n_w + i5w
        Mew[ewrow, np.arange(report5.size)] = dpt[i5p] * dpz[i5z] * dq3[i5q]
    """
    ncol = i5p.size
    Mew = np.zeros((n_dest, ncol))
    ewrow = i5e * N_W + i5w
    weights = np.ones(ncol) if unit_weights else dpt[i5p] * dpz[i5z] * dq3[i5q]
    Mew[ewrow, np.arange(ncol)] = weights
    return Mew


def equicorrelated(sigma, rho):
    """PSD, and its DIAGONAL is exactly sigma**2 for every rho in [-1/(n-1), 1]."""
    n = sigma.size
    R = (1.0 - rho) * np.eye(n) + rho * np.ones((n, n))
    lo = -1.0 / (n - 1)
    if not (lo - 1e-12 <= rho <= 1.0 + 1e-12):
        raise ValueError(f"rho={rho} outside PSD range [{lo:.6g}, 1]")
    return (sigma[:, None] * R) * sigma[None, :]


def released_sigma(C, M):
    return np.sqrt(np.clip(np.diag(project_covariance(C, M)), 0.0, None))


print(_line)
print("0. GEOMETRY, MEASURED FROM THE PRODUCTION EDGE ARRAYS")
print(_line)
print(f"pt {N_PT} x pz {N_PZ} x eavail {N_EA} x q3 {N_Q3} x W {N_W} = {N_GRID} full 5D cells")
print(f"destination (E_avail, W) bins                              = {N_DEST}")
print(f"reported 5D cells (cited, not recomputed here)             = {N_REPORTED}")
print(f"=> mean destination row support                            = {N_REPORTED / N_DEST:.1f}")
print(f"=> PIGEONHOLE: some row carries at least ceil({N_REPORTED}/{N_DEST}) = "
      f"{-(-N_REPORTED // N_DEST)} reported cells.")
print("   A row with >= 2 nonzeros makes diag(M C M^T) a function of C's off-diagonals.")
print("   This is forced by the counts alone; it needs no knowledge of WHICH cells report.")

# ==========================================================================================
print()
print(_line)
print("1. ARM 1 -- FULL PRODUCTION PATH ON A SMALL GRID (exact, all 42 destination rows)")
print(_line)
# a reduced (pt, pz, q3) inner block so the source covariance can be materialized exactly
n_pt_s, n_pz_s, n_q3_s = 3, 3, 3
dpt = np.diff(PT_EDGES)[:n_pt_s]
dpz = np.diff(PZ_EDGES)[:n_pz_s]
dq3 = np.diff(Q3_EDGES)[:n_q3_s]
inner = n_pt_s * n_pz_s * n_q3_s
shape_s = (n_pt_s, n_pz_s, N_EA, n_q3_s, N_W)      # the production C-order: pt, pz, eavail, q3, W
report_s = np.arange(int(np.prod(shape_s)))         # FULL support, declared above
i5p, i5z, i5e, i5q, i5w = np.unravel_index(report_s, shape_s)
M = build_mew(i5p, i5z, i5e, i5q, i5w, dpt, dpz, dq3, N_DEST)
support = (M != 0).sum(axis=1)
print(f"M shape {M.shape};  nonzeros per COLUMN: min={ (M!=0).sum(axis=0).min() } "
      f"max={ (M!=0).sum(axis=0).max() }   (production guarantees exactly 1)")
print(f"nonzeros per ROW: min={support.min()} median={int(np.median(support))} max={support.max()}"
      f"   (= the {inner} inner (pt,pz,q3) cells)")

rng = np.random.default_rng(20260910)
sigma = np.exp(rng.normal(-3.0, 0.8, size=report_s.size))    # positive, spread over ~2 decades
C_diag = equicorrelated(sigma, 0.0)                          # uncorrelated
C_corr = equicorrelated(sigma, 0.6)                          # SAME diagonal, correlated

assert np.allclose(np.diag(C_diag), np.diag(C_corr)), "fixture broken: diagonals must be identical"
print(f"\nfixture: two PSD source covariances, max |diag difference| = "
      f"{np.abs(np.diag(C_diag) - np.diag(C_corr)).max():.3e}  (identical by construction)")

s_diag = released_sigma(C_diag, M)
s_corr = released_sigma(C_corr, M)
ratio = s_corr / s_diag
print(f"released sigma with rho=0.0 : min={s_diag.min():.6e} max={s_diag.max():.6e}")
print(f"released sigma with rho=0.6 : min={s_corr.min():.6e} max={s_corr.max():.6e}")
print(f"RATIO per destination bin   : min={ratio.min():.4f} median={np.median(ratio):.4f} "
      f"max={ratio.max():.4f}")
print(f"VERDICT: the released uncertainty {'MOVES' if ratio.max() > 1.001 else 'does NOT move'} "
      f"when ONLY off-diagonal entries change.")

# ==========================================================================================
print()
print(_line)
print("2. CONTROL A -- SELECTION-ONLY M (one nonzero per row AND column): the effect must VANISH")
print(_line)
sel_cols = np.arange(N_DEST)                                  # 42 distinct source cells
M_sel = np.zeros((N_DEST, report_s.size))
M_sel[np.arange(N_DEST), sel_cols] = dpt[0] * dpz[0] * dq3[0]
print(f"nonzeros per ROW: max={(M_sel != 0).sum(axis=1).max()}")
d_sel = np.abs(released_sigma(C_diag, M_sel) - released_sigma(C_corr, M_sel)).max()
print(f"max |released sigma difference| = {d_sel:.3e}")
print(f"VERDICT: {'PASS' if d_sel < 1e-18 else 'FAIL'} -- with row support 1 the off-diagonals "
      f"cannot enter, so the effect is attributable to ROW SUPPORT and to nothing else.")

# ==========================================================================================
print()
print(_line)
print("3. CONTROL B -- UNIT WEIGHTS: width-weighting is NOT the cause")
print(_line)
M_unit = build_mew(i5p, i5z, i5e, i5q, i5w, dpt, dpz, dq3, N_DEST, unit_weights=True)
r_unit = released_sigma(C_corr, M_unit) / released_sigma(C_diag, M_unit)
print(f"RATIO per destination bin (unit weights): min={r_unit.min():.4f} "
      f"median={np.median(r_unit):.4f} max={r_unit.max():.4f}")
print(f"VERDICT: {'PASS' if r_unit.max() > 1.001 else 'FAIL'} -- the effect survives with the "
      f"widths removed. `project_cov_nd.py:5-8`'s width-weighting sets the WEIGHTS; what admits")
print("         the off-diagonals is that a destination row aggregates more than one source cell.")

# ==========================================================================================
print()
print(_line)
print("4. CONTROL C -- OPPOSITE DIRECTION: at rho = 0 the comparison must be SILENT")
print(_line)
s_a = released_sigma(equicorrelated(sigma, 0.0), M)
s_b = released_sigma(equicorrelated(sigma, 0.0), M)
same = np.abs(s_a - s_b).max()
C_shift = equicorrelated(sigma * 1.05, 0.0)                   # diagonal moves, off-diagonals still 0
r_shift = released_sigma(C_shift, M) / s_diag
print(f"identical inputs        -> max |difference| = {same:.3e}   (must be 0)")
print(f"diagonal scaled by 1.05 -> ratio min={r_shift.min():.6f} max={r_shift.max():.6f}   "
      f"(must be 1.05)")
print(f"VERDICT: {'PASS' if same == 0.0 and abs(r_shift.mean() - 1.05) < 1e-9 else 'FAIL'} -- the "
      f"measurement is silent when nothing changes and tracks the diagonal when only it changes.")

# ==========================================================================================
print()
print(_line)
print("5. ARM 2 -- MAGNITUDE AT THE REAL ROW SUPPORT (exact, one destination row)")
print(_line)
m_real = int(round(N_REPORTED / N_DEST))
w = np.resize(np.multiply.outer(np.multiply.outer(np.diff(PT_EDGES), np.diff(PZ_EDGES)),
                                np.diff(Q3_EDGES)).ravel(), m_real)
sig_r = np.exp(rng.normal(-3.0, 0.8, size=m_real))
base = float(np.sqrt(w @ equicorrelated(sig_r, 0.0) @ w))
rows = []
for rho in (-1.0 / (m_real - 1), 0.0, 0.05, 0.25, 0.6, 1.0):
    val = float(np.sqrt(w @ equicorrelated(sig_r, rho) @ w))
    rows.append((rho, val, val / base))
print(f"one destination row, support m = {m_real} (the measured mean), real width weights")
print(f"{'rho':>12} | {'released sigma':>16} | {'factor vs rho=0':>16}")
for rho, val, fac in rows:
    print(f"{rho:12.6f} | {val:16.6e} | {fac:16.4f}")
print(f"\nNOTE ON sqrt(m).  sqrt(m) = {np.sqrt(m_real):.2f} is the full-correlation factor ONLY when")
print("   the w_j*sigma_j terms are EQUAL. This fixture's weights span the real bin widths and its")
print("   sigmas span two decades, so the attained factor is the inverse participation ratio of the")
print(f"   w*sigma vector, {rows[-1][2]:.4f}, NOT sqrt(m). Quoting sqrt(m) here would overstate it.")

print()
print(_line)
print("6. THE EXACT ENVELOPE AT FIXED DIAGONAL (constructive, not a one-parameter family)")
print(_line)
# Equicorrelation is a single-parameter family and cannot reach the extremes. Rank-one
# SIGN correlation matrices R = s s^T with s in {-1,+1}^m are valid correlation matrices
# (PSD, unit diagonal) and give w^T D^(1/2) R D^(1/2) w = (sum_j s_j v_j)^2 exactly.
v = w * sig_r
print(f"v = w * sigma,  m = {v.size},  all v_j > 0: {bool(np.all(v > 0))}")

s_max = np.ones(v.size)                       # all +1  -> rho = 1
val_max = abs(float(s_max @ v))
order = np.argsort(-v)                        # greedy balance: largest first, to the lighter side
s_min = np.zeros(v.size); run = 0.0
for j in order:
    sgn = -1.0 if run > 0 else 1.0
    s_min[j] = sgn; run += sgn * v[j]
val_min = abs(float(s_min @ v))
assert set(np.unique(s_min)).issubset({-1.0, 1.0}), "sign vector must be +/-1"

for tag, s in (("all +1 (rho = 1)", s_max), ("greedy sign balance", s_min)):
    R = np.outer(s, s)
    C_s = (sig_r[:, None] * R) * sig_r[None, :]
    assert np.allclose(np.diag(C_s), sig_r ** 2), "sign construction must preserve the diagonal"
    ev = np.linalg.eigvalsh(R)
    print(f"  {tag:22s}: diag preserved, min eig(R) = {ev.min():+.3e} (PSD), "
          f"released sigma = {float(np.sqrt(w @ C_s @ w)):.6e}")

print(f"\nreleased sigma, exact extremes reachable at FIXED diagonal:")
print(f"  maximum  = sum_j w_j sigma_j = {val_max:.6e}   -> factor {val_max/base:.4f} vs rho = 0")
print(f"  minimum  = {val_min:.6e}   -> factor {val_min/base:.3e} vs rho = 0")
print(f"  ratio max/min = {val_max/val_min:.3e}")
print("=> with the diagonal held EXACTLY fixed, off-diagonal structure alone moves this released")
print(f"   error bar over a factor of {val_max/val_min:.2e}, and can drive it to ~0. A released bin")
print("   with a near-zero error bar is the SAME hazard `eavailW_covariance.py:410-413` already")
print("   names for empty projection rows: \"it does not look like missing data -- it looks like a")
print("   very good measurement\".")

print()
print(_line)
print("CONCLUSION")
print(_line)
print("A released projected uncertainty is a linear functional of the source covariance's")
print("OFF-DIAGONAL entries whenever the destination row aggregates more than one source cell,")
print("which the 10,694 -> 42 geometry forces (section 0, pigeonhole).")
print()
print("Measured, at this analysis's own mean row support of 255 and with the diagonal held exactly")
print(f"fixed: equicorrelation alone spans {rows[0][2]:.3f}x to {rows[-1][2]:.3f}x (section 5), and the exact")
print(f"envelope over all PSD source covariances spans a factor of {val_max/val_min:.2e} (section 6).")
print()
print("There is no third branch: either the projected uncertainty is computed as M C M^T, in which")
print("case the off-diagonals enter, or it is computed by summing per-cell variances, which is the")
print("error `eavailW_covariance.py:393-395` exists to forbid -- \"Never sum standard deviations")
print("across marginalized cells.\"")
