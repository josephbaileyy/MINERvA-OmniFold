"""COV2D's scorer at a truth (COV2D-DECLARATION.md sections 4.2 and 5; the director's R4 of 2026-11-04): the errors
e = x_hat - x_true on E_R's 205 cells after the surrogates, graded by 1B's own ``fd_1b_mc.grade``
(section 5.1-5.2: counts, flags against the null, chi2 on C_T's non-null subspace with the Cholesky equality when
ndf = 205, to the tolerance the caller passes: 1B's 1e-9 by default, addendum A5's max(1e-9, 10 kappa_2 eps) from the
driver; the joint count, pulls, mean chi2/ndf, s_c, attribution, over-coverage, size, COVERS / UNDER-COVERS).

* The surrogates, in the declaration table's order (R4): the lateral first, x_hat + sum_b s_b Delta_b(T) / 2 with each
  draw's ``lateral_signs`` over ``cov2d.LATERAL_BANDS`` (Muon_Energy_MINOS after X01), then the normalization,
  x (1 + 0.014 z) with the draw's ``norm_z``. The two do not commute; their difference is 0.014 z sum_b s_b Delta_b / 2,
  reported in sigma_c, descriptively.
* The weakened-pass label (section 5.2): a cell not flagged, at a truth where it is in ``cov2d.weakened_cells`` of C2's
  record, reads "passes, weakened by clipping"; the joint reading carries the share of weakened cells. The verdict is
  unchanged by the label.
* The outlier cell (``cov2d.OUTLIER_CELL``) is read by name.
* INVALID at T when any section 9 control failed for T (the caller says which); the grade is still computed and kept,
  unrepaired.

MEASURES: the grade of one truth's toys. CANNOT AUTHORIZE: a change to C_T or to the rule.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
for p in (HERE, REPO / "nd-unfolding"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
import cov2d as c  # noqa: E402

MINOS = "Muon_Energy_MINOS"


def lateral_deltas(bands: dict, minos_x) -> np.ndarray:
    """Delta_b(T), the endpoint difference x_0 - x_1 per lateral band in ``cov2d.LATERAL_BANDS`` order."""
    return np.stack([np.asarray(minos_x if b == MINOS else bands[b], np.float64)[0]
                     - np.asarray(minos_x if b == MINOS else bands[b], np.float64)[1] for b in c.LATERAL_BANDS])


def surrogate(x_hat: np.ndarray, signs, norm_z: float, deltas: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(x_hat after the lateral then the normalization surrogate, the non-commuting difference from the other order)."""
    s = np.asarray(signs, np.float64)
    if s.shape != (len(c.LATERAL_BANDS),) or not np.all(np.abs(s) == 1):
        raise c.Refusal("one sign of +-1 per lateral band")
    lat = (s[:, None] * deltas).sum(axis=0) / 2
    x = (np.asarray(x_hat, np.float64) + lat) * (1 + c.NORM * float(norm_z))
    return x, c.NORM * float(norm_z) * lat


def errors(x_hat: np.ndarray, x_true: np.ndarray, natures: list[dict], deltas: np.ndarray, C_T: np.ndarray):
    """E (toys x 205) after the surrogates, and the cross term's size in sigma_c = sqrt(diag C_T) (descriptive, R4)."""
    toys = [n for n in natures if n["role"] == "toy"]
    if not (len(toys) == x_hat.shape[0] == x_true.shape[0]):
        raise c.Refusal("one unfold and one truth per toy")
    sigma = np.sqrt(np.diag(np.asarray(C_T, np.float64)))
    if sigma.shape != (x_hat.shape[1],):
        raise c.Refusal("C_T must be one row and column per cell")
    E, cross = [], []
    for k, n in enumerate(toys):
        xs, d = surrogate(x_hat[k], n["lateral_signs"], n["norm_z"], deltas)
        E.append(xs - x_true[k])
        cross.append(np.abs(d) / sigma)
    cross = np.stack(cross)
    return np.stack(E), {"max_over_sigma": float(cross.max()), "median_over_sigma": float(np.median(cross)),
                         "p90_over_sigma": float(np.percentile(cross, 90))}


def score(E: np.ndarray, C_T: np.ndarray, null: dict, truth: str, cells: np.ndarray, weakened_ratio: np.ndarray,
          controls_failed: list[str] | None = None, chol_tol: float = 1e-9, chol_out: dict | None = None) -> dict:
    """1B's grade, then the weakened labels, the outlier cell and INVALID. ``cells`` are E_R's 205 flat cell indices,
    ``weakened_ratio`` C2's option-1 clipped variance ratio on them, at this truth. ``chol_tol`` and ``chol_out`` go to
    1B's grade unchanged (its Cholesky cross-check at full rank; COV2D-BINDING-2 addendum A5); the defaults are 1B's."""
    import fd_1b_mc as mc
    if E.shape[1] != 205 or C_T.shape != (205, 205) or len(cells) != 205:
        raise c.Refusal("205 cells are required")
    if E.shape[0] != len(c.TOY_SEEDS[truth]):     # section 5.2's rule is Bin(300, ...); 1B refuses another seed set
        raise c.Refusal(f"{E.shape[0]} toys; the declared {truth} set is {len(c.TOY_SEEDS[truth])}")
    if c.OUTLIER_CELL not in [int(x) for x in cells]:     # section 5.2: its reading "whatever it is"
        raise c.Refusal(f"the outlier cell {c.OUTLIER_CELL} is not among the cells")
    g = mc.grade(E, C_T, null, chol_tol=chol_tol, chol_out=chol_out)
    weak = set(c.weakened_cells(weakened_ratio, cells))
    cells = [int(x) for x in cells]
    g["weakened_pass"] = [cell for i, cell in enumerate(cells) if cell in weak and not g["cell_flag"][i]]
    g["weakened_share"] = len(weak) / 205
    g["flagged_cells"] = [cell for i, cell in enumerate(cells) if g["cell_flag"][i]]
    i = cells.index(c.OUTLIER_CELL)
    g["outlier_cell"] = {"cell": c.OUTLIER_CELL, "count": g["counts"][i], "k_cell": g["k_cell"][i],
                         "flagged": g["cell_flag"][i], "pull_mean": g["pull_mean"][i], "s_c": g["s_c"][i]}
    g["truth"] = truth
    g["controls_failed"] = list(controls_failed or [])
    if g["controls_failed"]:
        g["verdict_graded"] = g["verdict"]
        g["verdict"] = "INVALID"
    return g
