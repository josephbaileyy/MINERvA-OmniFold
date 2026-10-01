"""The three scalar estimators of the matched comparison, on a `selection_data.Problem`.

* `omnifold` -- scalar two-step OmniFold. Miss rule `carry` IS the predecessor's
  `phase_b/scalar/scalar_omnifold.run_scalar_omnifold` (called, not copied: misses carry the
  previous push into step 2). Miss rule `efficiency_corrected` is the same loop with step 2 trained
  on the prior's ACCEPTED rows only (pass_reco & pass_truth) and the learned truth ratio applied
  to every truth-passing row, misses included -- the PET path's `--step2-miss-mode
  efficiency_corrected` (`phase_b/pet/b2_driver.py`, Huang et al. arXiv:2504.06857 sec. V.A).
  Everything else is the predecessor's engine mirror: normalization of both step-1 legs to 1e6, a
  train/validation split drawn once per step and reused, logits capped at +-30, HGB refit at every
  iteration with early stopping on the external validation split (`scalar_omnifold.HGBRatio`).
* `aussie` -- AUSSIE (arXiv:2602.24282), AutoDiff variant, the predecessor's
  `phase_f/aussie_scalar.train_classifier` / `train_unfolder` (called, not copied) generalized from
  the hard-wired historical halves to any problem: step 1 is an MLP density-ratio classifier on
  the reco inputs; step 2 an MLP truth-level ratio trained to make the gradient of the MLC loss
  w.r.t. the frozen classifier vanish; misses enter through the penalty
  `lambda * E_miss[w (log R(z))^2]` (lambda = 0: unconstrained extrapolation, the analogue of
  efficiency correction; lambda = 1000: misses pinned to R = 1, the analogue of carry-misses).
  Same engine normalization as OmniFold.
* `ibu` -- binned iterative unfolding in the engine's event-weight form
  (`phase_b/scalar/binned_unfolding.binned_omnifold`, called), reco bins = the historical
  (p_T, p_par) reporting cells x the seven reco E_avail bins (+1 off-grid cell), truth bins =
  reporting cells x seven truth E_avail bins, both miss modes, engine normalization -- the
  `muon_eavail` variant of `phase_b/scalar/run_ibu.py`.

Each yields a push aligned to ALL prior rows (1 on rows failing pass_truth, as the engine).
"""
from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Any, Callable, Iterator

import numpy as np

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.append(str(HERE))

import selection_data as sd  # noqa: E402  (puts phase_b/scalar, phase_e, phase_f on the path)
import binned_unfolding as bu  # noqa: E402
import run_ibu  # noqa: E402
import scalar_omnifold as so  # noqa: E402

MISS_RULES = ("carry", "efficiency_corrected")
AUSSIE_LAMBDA = {"efficiency_corrected": 0.0, "carry": 1000.0}   # matched miss handling
IBU_MODE = {"carry": bu.MODE_CARRY_MISSES, "efficiency_corrected": bu.MODE_EFFICIENCY_CORRECTED}


# --------------------------------------------------------------------------------------------- #
# OmniFold, both miss rules
# --------------------------------------------------------------------------------------------- #
def omnifold(*, X_reco_mc: np.ndarray, X_reco_data: np.ndarray, X_gen_mc: np.ndarray,
             pass_reco_mc: np.ndarray, pass_gen_mc: np.ndarray, w_truth_mc: np.ndarray,
             w_reco_mc: np.ndarray, w_data: np.ndarray,
             make_step1: Callable[[int], Any], make_step2: Callable[[int], Any],
             iterations: int, seed: int, miss_rule: str,
             callback: Callable[[dict[str, Any]], None] | None = None) -> dict[str, np.ndarray]:
    """Scalar OmniFold with the given miss rule. ``pass_reco_mc`` is the step-1 flag
    (pass_reco & pass_gen, as the engine receives it)."""
    if miss_rule not in MISS_RULES:
        raise ValueError(f"unknown miss rule {miss_rule!r}")
    kw = dict(X_reco_mc=X_reco_mc, X_reco_data=X_reco_data, X_gen_mc=X_gen_mc,
              pass_reco_mc=pass_reco_mc, pass_gen_mc=pass_gen_mc, w_truth_mc=w_truth_mc,
              w_reco_mc=w_reco_mc, w_data=w_data, make_step1=make_step1, make_step2=make_step2,
              iterations=iterations, seed=seed, callback=callback)
    if miss_rule == "carry":
        return so.run_scalar_omnifold(**kw)
    return _omnifold_efficiency_corrected(**kw)


def _omnifold_efficiency_corrected(*, X_reco_mc, X_reco_data, X_gen_mc, pass_reco_mc,
                                   pass_gen_mc, w_truth_mc, w_reco_mc, w_data, make_step1,
                                   make_step2, iterations, seed, callback=None):
    """`scalar_omnifold.run_scalar_omnifold` line for line, except step 2: both classes are the
    ACCEPTED rows (class 0 at w_truth, class 1 at w_truth x pull) and the ratio is applied to all
    pass_gen rows."""
    s1 = np.asarray(pass_reco_mc, dtype=bool)
    pg = np.asarray(pass_gen_mc, dtype=bool)
    if (s1 & ~pg).any():
        raise ValueError("efficiency correction needs the step-1 flag to imply pass_gen")
    w_t = np.asarray(w_truth_mc, dtype=np.float64).copy()
    w_r = np.asarray(w_reco_mc, dtype=np.float64).copy()
    w_d = np.asarray(w_data, dtype=np.float64).copy()
    c = bu.ENGINE_NORMALIZATION / w_r[s1].sum()
    w_t *= c
    w_r *= c
    w_d *= bu.ENGINE_NORMALIZATION / w_d.sum()

    rng = np.random.default_rng(int(seed))
    n_mc1 = int(s1.sum())
    X1 = np.concatenate([np.asarray(X_reco_mc)[s1], np.asarray(X_reco_data)], axis=0)
    y1 = np.concatenate([np.zeros(n_mc1), np.ones(len(w_d))])
    tr1, va1 = so._split(X1.shape[0], rng)
    Xg = np.asarray(X_gen_mc)[pg]
    Xa = np.asarray(X_gen_mc)[s1]
    n_acc = int(s1.sum())
    X2 = np.concatenate([Xa, Xa], axis=0)
    y2 = np.concatenate([np.zeros(n_acc), np.ones(n_acc)])
    tr2, va2 = so._split(X2.shape[0], rng)

    push = np.ones(w_t.shape[0], dtype=np.float64)
    pull = push.copy()
    for k in range(1, iterations + 1):
        m1 = make_step1(k)
        w1 = np.concatenate([(push * w_r)[s1], w_d])
        t0 = time.perf_counter()
        info1 = m1.fit(X1[tr1], y1[tr1], w1[tr1], X1[va1], y1[va1], w1[va1])
        ratio1, sat1 = so._capped_ratio(m1.logit(np.asarray(X_reco_mc)[s1]))
        info1.update({"seconds": time.perf_counter() - t0, "saturated": sat1})
        prev_push = push
        pull = push.copy()
        pull[s1] = push[s1] * ratio1

        m2 = make_step2(k)
        w2 = np.concatenate([w_t[s1], (w_t * pull)[s1]])
        t0 = time.perf_counter()
        info2 = m2.fit(X2[tr2], y2[tr2], w2[tr2], X2[va2], y2[va2], w2[va2])
        ratio2, sat2 = so._capped_ratio(m2.logit(Xg))
        info2.update({"seconds": time.perf_counter() - t0, "saturated": sat2,
                      "rows": [n_acc, n_acc]})
        push = np.ones_like(push)
        push[pg] = ratio2
        if callback is not None:
            callback({"iteration": k, "pull": pull, "push": push, "prev_push": prev_push,
                      "step1": info1, "step2": info2})
    return {"pull": pull, "push": push}


def hgb_factory(params: dict[str, Any], seed: int, threads: int | None = None):
    """A distinct reproducible HGB seed per (task seed, iteration), as run_scalar_omnifold."""
    def factory(k: int):
        return so.HGBRatio(seed=seed * 1000 + k, **params)
    return factory


def run_omnifold(prob: sd.Problem, *, truth_set: str, miss_rule: str, params: dict[str, Any],
                 seed: int, iterations: int,
                 on_iteration: Callable[[int, np.ndarray, dict[str, Any]], None]) -> float:
    """Run OmniFold on the problem; ``on_iteration(k, push, info)``. Returns seconds."""
    X_reco_mc, _ = prob.reco_matrix("prior")
    X_reco_data, _ = prob.reco_matrix("pseudo")
    X_gen, _ = prob.truth_matrix(truth_set)
    t0 = time.perf_counter()
    last = [t0]

    def cb(rec: dict[str, Any]) -> None:
        now = time.perf_counter()
        info = {"step1": {k: rec["step1"].get(k) for k in ("n_iter", "val_logloss", "seconds",
                                                           "saturated")},
                "step2": {k: rec["step2"].get(k) for k in ("n_iter", "val_logloss", "seconds",
                                                           "saturated")},
                "seconds_iteration": now - last[0]}
        last[0] = now
        on_iteration(rec["iteration"], rec["push"], info)

    omnifold(X_reco_mc=X_reco_mc, X_reco_data=X_reco_data[prob.s1_pseudo], X_gen_mc=X_gen,
             pass_reco_mc=prob.s1_prior, pass_gen_mc=prob.pg_prior,
             w_truth_mc=prob.prior["w_truth"], w_reco_mc=prob.prior["w_reco"],
             w_data=prob.w_data, make_step1=hgb_factory(params, seed),
             make_step2=hgb_factory(params, seed + 500), iterations=iterations, seed=seed,
             miss_rule=miss_rule, callback=cb)
    return time.perf_counter() - t0


# --------------------------------------------------------------------------------------------- #
# AUSSIE
# --------------------------------------------------------------------------------------------- #
def run_aussie(prob: sd.Problem, *, truth_set: str, lam: float, seed: int, lr: float,
               epochs: int) -> tuple[np.ndarray, dict[str, Any]]:
    """AUSSIE on the problem; returns (push over all prior rows, info)."""
    import torch
    import aussie_scalar as au
    s1, pg = prob.s1_prior, prob.pg_prior
    miss = pg & ~prob.prior["pass_reco"]
    X_reco_mc, _ = prob.reco_matrix("prior")
    X_reco_data, _ = prob.reco_matrix("pseudo")
    X_gen, _ = prob.truth_matrix(truth_set)
    w_t = prob.prior["w_truth"].copy()
    w_r = prob.prior["w_reco"].copy()
    w_d = prob.w_data.copy()
    c = bu.ENGINE_NORMALIZATION / w_r[s1].sum()
    w_t *= c
    w_r *= c
    w_d *= bu.ENGINE_NORMALIZATION / w_d.sum()
    t0 = time.perf_counter()
    clf, c_mean, c_std = au.train_classifier(X_reco_mc[s1], X_reco_data[prob.s1_pseudo], w_r[s1],
                                             w_d, epochs=epochs, lr=lr, seed=seed)
    t1 = time.perf_counter()
    unf, z_mean, z_std = au.train_unfolder(clf, c_mean, c_std, X_gen[s1], X_reco_mc[s1], w_t[s1],
                                           X_gen[miss], w_t[miss], lambda_miss=float(lam),
                                           epochs=epochs, lr=lr, seed=seed)
    t2 = time.perf_counter()
    unf.eval()
    with torch.no_grad():
        Zt = np.sign(X_gen[pg]) * np.log1p(np.abs(X_gen[pg]))
        lw = unf(torch.tensor((Zt - z_mean) / z_std, dtype=torch.float32)).numpy()
    push = np.ones(prob.prior["rows"].size, dtype=np.float64)
    push[pg] = au._capped_ratio(lw)
    info = {"seconds_step1": t1 - t0, "seconds_step2": t2 - t1,
            "seconds": time.perf_counter() - t0,
            "saturated": int((np.abs(lw) >= au.LOGIT_CAP).sum()),
            "mean_push_missed": float(np.average(push[miss], weights=w_t[miss])),
            "mean_push_accepted": float(np.average(push[s1], weights=w_t[s1]))}
    return push, info


# --------------------------------------------------------------------------------------------- #
# IBU
# --------------------------------------------------------------------------------------------- #
def ibu_bins(prob: sd.Problem) -> dict[str, Any]:
    """Truth bins (truth cell x 7 truth E_avail) and reco bins (reco cell x 7 reco E_avail)."""
    edges = np.asarray(sd.GRID["endpoint_edges"], float)
    n_cells = (len(sd.GRID["edges_pt"]) - 1) * (len(sd.GRID["edges_pz"]) - 1)
    P, D = prob.prior, prob.pseudo

    def cell(pt, pz):
        c = sd.truth_cell(pt, pz).astype(np.int64)
        return np.where(c >= 0, c, n_cells)

    t = P["truth_scalars"]
    truth = cell(t[:, 0], t[:, 1]) * run_ibu.N_EAV + run_ibu.eavail_bin(t[:, 2], edges)
    reco_mc = (cell(P["reco_scalars"][:, 0], P["reco_scalars"][:, 1]) * run_ibu.N_EAV
               + run_ibu.eavail_bin(P["reco_eavail"], edges))
    s1d = prob.s1_pseudo
    reco_d = (cell(D["reco_scalars"][s1d, 0], D["reco_scalars"][s1d, 1]) * run_ibu.N_EAV
              + run_ibu.eavail_bin(D["reco_eavail"][s1d], edges))
    n = (n_cells + 1) * run_ibu.N_EAV
    return {"truth": truth, "reco_mc": reco_mc, "reco_data": reco_d, "n_bins": n}


def run_ibu_iter(prob: sd.Problem, miss_rule: str, iterations: int
                 ) -> Iterator[dict[str, Any]]:
    b = ibu_bins(prob)
    yield from bu.binned_omnifold(
        reco_bin_mc=b["reco_mc"], truth_bin_mc=b["truth"], pass_reco_mc=prob.s1_prior,
        pass_gen_mc=prob.pg_prior, w_truth_mc=prob.prior["w_truth"],
        w_reco_mc=prob.prior["w_reco"], reco_bin_data=b["reco_data"], w_data=prob.w_data,
        n_reco_bins=b["n_bins"], n_truth_bins=b["n_bins"], iterations=iterations,
        mode=IBU_MODE[miss_rule])
