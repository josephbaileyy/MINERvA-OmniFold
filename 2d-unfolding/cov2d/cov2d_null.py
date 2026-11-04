"""COV2D's null at a truth (COV2D-DECLARATION.md section 5; the director's R5 of 2026-11-04): ``fd_1b_null``,
imported unchanged, on the remade products at T, before any toy error is read.

* One ``Discrete`` law per drawn band, from the same unfold outputs the blocks are built from (cov2d_blocks), so each
  law's covariance is that band's block exactly: the Flux universes centred at w_u / sum w, 2p2h's three at 1/3, every
  other universe band's two endpoints at 1/2, and each lateral band's +-Delta_b(T)/2 (Muon_Energy_MINOS after X01).
* One Gaussian with covariance C_stat + C_norm + C08 + C_model_abs.
* ``fd_1b_null.null_contents`` checks the components sum to C_T to 1e-12 (``check_matched``) or refuses, then simulates
  N_MC = 2,000,000 error vectors at ``cov2d.NULL_SEED`` = 5,742,000, passed explicitly (fd_1b_null's default seed and
  16-cell constants are 1B's). ``thresholds`` divides ALPHA_CELLS by the number of cells it is given, 205, asserted.

MEASURES: the null contents and flag counts at T. CANNOT AUTHORIZE: a verdict by itself.
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
import fd_1b_null as nl  # noqa: E402

N_CELLS = 205
MINOS = "Muon_Energy_MINOS"


def laws_at_T(bands: dict, minos_x: np.ndarray, w_flux: np.ndarray) -> list:
    """The drawn bands' laws, in draw order then the laterals in their declared order."""
    laws = []
    for b in c.ORDER:
        X = np.asarray(bands[b], np.float64)
        if X.shape[0] != c.BANDS[b]:
            raise c.Refusal(f"{b}: {X.shape[0]} universes, declared {c.BANDS[b]}")
        p = np.asarray(w_flux, float) / np.sum(w_flux) if b == c.FLUX else np.full(X.shape[0], 1.0 / X.shape[0])
        laws.append(nl.Discrete.centred(X, p))
    for b in c.LATERAL_BANDS:
        X = np.asarray(minos_x if b == MINOS else bands[b], np.float64)
        if X.shape[0] != 2:
            raise c.Refusal(f"lateral {b}: {X.shape[0]} endpoints")
        laws.append(nl.Discrete.two_point(X[0] - X[1]))
    return laws


def null_at_T(blocks: dict, bands: dict, minos_x, w_flux, n_mc: int = nl.N_MC, n_toys: int = len(c.TOY_SEEDS["G18"])):
    """The null contents, flag counts and size at T, from cov2d_blocks.assemble's output and its band inputs."""
    C_T = blocks["C_T"]
    if C_T.shape != (N_CELLS, N_CELLS):
        raise c.Refusal(f"C_T is {C_T.shape}, not 205 x 205")
    gauss = blocks["C_stat"] + blocks["C_norm"] + blocks["C08"] + blocks["C_model_abs"]
    null = nl.null_contents(laws_at_T(bands, minos_x, w_flux), gauss, C_T, n_mc=n_mc, seed=c.NULL_SEED)
    thr = nl.thresholds(null, n=n_toys)
    if len(thr["p_used"]) != N_CELLS or thr["alpha_cell"] != nl.ALPHA_CELLS / N_CELLS:
        raise c.Refusal("the cell rule must divide ALPHA_CELLS by 205")
    out = {"null": null, "thresholds": thr, "size": nl.size(null, thr)}
    if "C_T_minus" in blocks:   # the leave-out-MEC variant's null, here beside C_T's, as 1B builds both (fd_1b_mc.py:740)
        minus_abs = blocks["C_T_minus"] - (C_T - blocks["C_model_abs"])
        g_minus = blocks["C_stat"] + blocks["C_norm"] + blocks["C08"] + minus_abs
        out["null_minus"] = nl.null_contents(laws_at_T(bands, minos_x, w_flux), g_minus, blocks["C_T_minus"],
                                             n_mc=n_mc, seed=c.NULL_SEED)
    return out
