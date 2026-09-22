"""Binned iterative unfolding in the OmniFold engine's event-weight form (pure numpy).

The historical estimator is `omnifold_nn/omnifold/omnifold.py`. With the classifiers replaced by
their Bayes-optimal BINNED versions -- a classifier that sees only a bin index returns the ratio
of the two classes' weight sums in that bin -- its two steps become:

step 1  r_i  = D_i / M_i,   M_i = sum over prior events with pass_reco&pass_gen in reco bin i of
                            push * w_reco;  D_i the pseudo-data weight in reco bin i.
        pull = push * r_{i(e)} on those events; pull = push elsewhere
        ("Don't update weights where there's no reco events", RunStep1).
step 2  push_j = sum_{e in truth bin j, pass_gen} w_truth * pull / sum_{same} w_truth
        and push = 1 where pass_gen is false (RunStep2: both classes carry w_truth * pass_gen,
        the second times pull; the new push is the ratio, not a product with the old push).

A missed event (pass_gen, not pass_reco) therefore keeps its prior push through step 1 and enters
the step-2 average at that value. That is `MODE_CARRY_MISSES`, and it is the binned twin of what
the historical PET run did. With a diagonal response of acceptance ``a_j`` it gives
``T_j - t_j^(k) = (1 - a_j)^k (T_j - t_j^(0))`` -- the historical reference model `1-(1-a)^k` is
this estimator's own convergence law in the zero-smearing limit (tested in
`test_scalar_references.py`).

`MODE_EFFICIENCY_CORRECTED` is textbook D'Agostini IBU: the step-2 average runs over ACCEPTED
events only, which is ``t_j <- (1/eps_j) sum_i P(j|i) d_i``. Truth bins with no accepted event keep
their previous push (there is no information to move them).

NORMALIZATION, AS THE ENGINE DOES IT. The prior's weights are scaled so its step-1 leg sums to
`1e6` over pass_reco rows (`DataLoader(normalize=True)`), and the pseudo-data is scaled to `1e6`
too. That equates the pseudo-data's accepted total with the prior's, which is an assumption about
the unknown spectrum whenever acceptance correlates with the injected variable. `data_total` lets
a caller replace it (e.g. with the rate-matched value, which a real measurement gets from POT
normalization) and the difference is reported as its own diagnostic.
"""
from __future__ import annotations

from typing import Iterator

import numpy as np

MODE_CARRY_MISSES = "carry_misses"
MODE_EFFICIENCY_CORRECTED = "efficiency_corrected"
MODES = (MODE_CARRY_MISSES, MODE_EFFICIENCY_CORRECTED)
ENGINE_NORMALIZATION = 1_000_000.0


def _check_bins(bins: np.ndarray, n: int, label: str) -> np.ndarray:
    b = np.asarray(bins, dtype=np.int64)
    if b.size and (b.min() < 0 or b.max() >= n):
        raise ValueError(f"{label} bin index outside [0, {n})")
    return b


def binned_omnifold(*, reco_bin_mc: np.ndarray, truth_bin_mc: np.ndarray,
                    pass_reco_mc: np.ndarray, pass_gen_mc: np.ndarray,
                    w_truth_mc: np.ndarray, w_reco_mc: np.ndarray,
                    reco_bin_data: np.ndarray, w_data: np.ndarray,
                    n_reco_bins: int, n_truth_bins: int, iterations: int,
                    mode: str = MODE_CARRY_MISSES,
                    data_total: float | None = None,
                    ) -> Iterator[dict[str, np.ndarray | float | int]]:
    """Yield one record per iteration: {"iteration", "pull", "push", "ratio", "lost_data"}.

    ``pass_reco_mc`` is the step-1 flag the engine receives (the historical driver passes
    ``pass_reco & pass_gen``); ``reco_bin_mc`` is read only where it is true and ``truth_bin_mc``
    only where ``pass_gen_mc`` is true. ``pull``/``push`` are per event, aligned to the MC arrays.
    ``lost_data`` is the pseudo-data weight in reco bins that hold no prior weight: a binned
    classifier cannot move it anywhere, so it is reported rather than silently dropped.
    """
    if mode not in MODES:
        raise ValueError(f"unknown mode {mode!r}; expected one of {MODES}")
    if iterations < 1:
        raise ValueError("iterations must be >= 1")
    s1 = np.asarray(pass_reco_mc, dtype=bool)
    pg = np.asarray(pass_gen_mc, dtype=bool)
    if (s1 & ~pg).any() and mode == MODE_EFFICIENCY_CORRECTED:
        raise ValueError("efficiency_corrected mode needs pass_reco_mc to imply pass_gen_mc")
    w_t = np.asarray(w_truth_mc, dtype=np.float64).copy()
    w_r = np.asarray(w_reco_mc, dtype=np.float64).copy()
    w_d = np.asarray(w_data, dtype=np.float64).copy()
    rb = _check_bins(np.asarray(reco_bin_mc)[s1], n_reco_bins, "reco (mc)")
    tb_pg = _check_bins(np.asarray(truth_bin_mc)[pg], n_truth_bins, "truth")
    rb_d = _check_bins(reco_bin_data, n_reco_bins, "reco (data)")
    if not (np.isfinite(w_t).all() and np.isfinite(w_r).all() and np.isfinite(w_d).all()):
        raise ValueError("non-finite weights")

    # DataLoader(normalize=True): one constant from the reco leg over pass_reco, applied to both.
    c = ENGINE_NORMALIZATION / w_r[s1].sum()
    w_t *= c
    w_r *= c
    w_d *= (ENGINE_NORMALIZATION if data_total is None else float(data_total)) / w_d.sum()
    D = np.bincount(rb_d, weights=w_d, minlength=n_reco_bins)

    den_all = np.bincount(tb_pg, weights=w_t[pg], minlength=n_truth_bins)
    acc_pg = s1[pg]
    den_acc = np.bincount(tb_pg[acc_pg], weights=w_t[pg][acc_pg], minlength=n_truth_bins)

    push = np.ones(w_t.shape[0], dtype=np.float64)
    push_bin = np.ones(n_truth_bins, dtype=np.float64)
    for k in range(1, iterations + 1):
        M = np.bincount(rb, weights=(push * w_r)[s1], minlength=n_reco_bins)
        ratio = np.where(M > 0, D / np.where(M > 0, M, 1.0), 1.0)
        lost = float(D[M <= 0].sum())
        pull = push.copy()
        pull[s1] = push[s1] * ratio[rb]
        if mode == MODE_CARRY_MISSES:
            num = np.bincount(tb_pg, weights=(w_t * pull)[pg], minlength=n_truth_bins)
            new_bin = np.where(den_all > 0, num / np.where(den_all > 0, den_all, 1.0), 1.0)
        else:
            num = np.bincount(tb_pg[acc_pg], weights=(w_t * pull)[pg][acc_pg],
                              minlength=n_truth_bins)
            new_bin = np.where(den_acc > 0, num / np.where(den_acc > 0, den_acc, 1.0), push_bin)
        push_bin = new_bin
        push = np.ones_like(push)
        push[pg] = push_bin[tb_pg]
        yield {"iteration": k, "pull": pull, "push": push.copy(), "ratio": ratio,
               "lost_data": lost, "data_total": float(w_d.sum()),
               "prior_step1_total": float(M.sum())}


def reco_level_recovery(reco_bin_mc: np.ndarray, s1: np.ndarray, w_reco_mc: np.ndarray,
                        before: np.ndarray, after: np.ndarray, reco_bin_data: np.ndarray,
                        w_data: np.ndarray, n_bins: int) -> dict[str, float]:
    """Detector-level check of step 1: how much of the reco-level data/prior difference, in
    ``n_bins`` reco bins, the step-1 reweighting (before -> after) removed. Normalized L1, the
    same convention as the truth-level score."""
    s1 = np.asarray(s1, dtype=bool)
    rb = np.asarray(reco_bin_mc)[s1]
    prior = np.bincount(rb, weights=(before * w_reco_mc)[s1], minlength=n_bins)
    moved = np.bincount(rb, weights=(after * w_reco_mc)[s1], minlength=n_bins)
    target = np.bincount(np.asarray(reco_bin_data), weights=w_data, minlength=n_bins)
    prior, moved, target = (a / a.sum() for a in (prior, moved, target))
    injected = float(np.abs(target - prior).sum())
    residual = float(np.abs(target - moved).sum())
    # None rather than NaN: the result files are written with allow_nan=False
    return {"injected_l1": injected, "residual_l1": residual,
            "recovery": 1.0 - residual / injected if injected > 0 else None}
