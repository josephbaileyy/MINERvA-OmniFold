#!/usr/bin/env python3
"""T3 arms: ``s5e_trace``'s tracer with one pipeline component replaced, and the per-iteration readouts.

Declaration: ``docs/orchestration/state/measurement-paper/5d-community-20261024/fd/tier3-20261110/
T3-PIPELINE-TESTS-DECLARATION.md`` (§3.3 the arms, §4 the quantities, §6 C-TRACE and C-ARM).

THE LOOP IS NOT RE-IMPLEMENTED. The unfold is ``s5c_unfold.unfold`` (the production
``omnifold_nn_core.omnifold_loop``), reached with ``omnifold_nn_core.make_estimators`` rebound so the loop receives
thin wrappers around its own three estimators, as ``s5e_trace.traced_unfold`` does. ``s5e_trace``'s bitwise rebuild
of w_pull and w_push at every iteration is inherited unchanged. Each arm acts only on what one wrapped estimator
returns or receives:

* ``B0``: nothing (the trace only).
* ``MU``: misses keep new_w = 1 (``s5e_trace``'s bound ``missed="unity"``).
* ``MW``: the regressor's ``fit`` receives ``sample_weight = w_push * w_truth`` on the reco-passing rows, where the
  loop passes none (``omnifold_nn_core.py:259``); the target is the loop's own.
* ``MO``: ``reg.predict`` returns r / w_push on the misses, so their w_pull is the true per-event weight r.
* ``OP``: the step-1 classifier's output gives new_w = r / w_push on the reco-passing rows, and ``reg.predict`` gives
  it on the misses, so every event's w_pull is r.
* ``SO`` changes the pseudo-data, not the loop (``t3p_probe.install``); here it is ``B0``.

MEASURES: the internal response of one unfold of one arm. CANNOT AUTHORIZE: a cause by itself, an estimator change
(MO and OP use the truth), or any statement about data.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parents[1]
if str(_ND) not in sys.path:
    sys.path.insert(0, str(_ND))
import omnifold_nn_core as onc  # noqa: E402
import s5c_unfold  # noqa: E402
import s5e_trace  # noqa: E402
from s5e_trace import Recorder, TraceError, Tracer, _Wrapped, binned, xs_from_push  # noqa: E402

ARMS = ("B0", "MU", "MW", "MO", "SO", "OP")
ITERS = {"B0": 50, "MU": 50, "MW": 50, "MO": 50, "SO": 50, "OP": 2}
PAIR_KS = (5, 10, 20, 50)  # C-PAIR: B0's unfold at these k against FD-PRR's B0, K10, K20 and K50 products
CLIP = 1e-6  # omnifold_nn_core._reweight's clip (omnifold_nn_core.py:154), counted, never replaced
ORACLE_RTOL = 1e-12  # C-ARM: an oracle's w_pull equals r to this relative tolerance (p/(1-p) round trip)
N_CELLS = 16


class ArmWrapped(_Wrapped):
    """``s5e_trace._Wrapped`` with the arm's intervention on the regressor's fit (MW) and the step-1 output (OP)."""

    def fit(self, X, y, sample_weight=None):
        t = self._tracer
        if self._role == "reg" and t.arm == "MW":
            if sample_weight is not None:
                raise TraceError("the loop passed the regressor a sample weight: MW replaces none")
            sample_weight = t.mw_weight()
            if len(sample_weight) != len(y):
                raise TraceError("MW: the weight does not match the regressor's rows")
            t.mw_given = sample_weight
        t.on_fit(self._role, X, y, sample_weight)
        self._inner.fit(X, y, sample_weight=sample_weight)
        return self

    def predict_proba(self, X):
        t = self._tracer
        out = self._inner.predict_proba(X)
        if self._role == "step1" and t.arm == "OP":
            q = t.oracle_new_w(pass_side=True)
            if len(q) != len(X):
                raise TraceError("OP: the oracle does not match step 1's rows")
            p = q / (1.0 + q)
            out = np.column_stack([1.0 - p, p])
        t.count_clip(self._role, out)
        t.on_proba(self._role, out)
        return out


class ArmTracer(Tracer):
    """``s5e_trace.Tracer`` for one arm. ``r`` is the truth reweight of the pass-truth unfolding-MC rows."""

    def __init__(self, ctx: dict, callback, arm: str, r: np.ndarray):
        if arm not in ARMS:
            raise ValueError(f"unknown arm {arm!r}")
        super().__init__(ctx, self._checked(callback), None, "unity" if arm == "MU" else "regress", False)
        self.arm = arm
        self.r = np.asarray(r, float)
        if self.r.shape != (self.n,) or not np.all(np.isfinite(self.r)) or np.any(self.r <= 0):
            raise TraceError("r must be one finite positive weight per pass-truth unfolding-MC row")
        self.mw_given = None
        self.clip = {"step1": [], "step2": []}  # per iteration: (n at the low edge, n at the high edge)
        self.evidence = {"arm": arm, "mw_fits": 0, "max_rel_oracle": [], "fill_all_one": [], "op_push_rel_change": None}
        self._prev_push = None

    def factory(self, original):
        def make(kind, nvars, seed=None):
            self.factory_calls += 1
            ests = list(original(kind, nvars, seed=seed))
            return tuple(ArmWrapped(self, role, est) for role, est in zip(("step1", "step2", "reg"), ests))
        return make

    # -- the interventions -----------------------------------------------------------------------
    def mw_weight(self) -> np.ndarray:
        """MW: the population the loop is reweighting at this iteration, on the reco-passing rows."""
        return self.w_push[self.pr] * self.w_truth[self.pr]

    def oracle_new_w(self, pass_side: bool) -> np.ndarray:
        """The new_w that makes w_pull = r on one side (reco-passing or missed rows)."""
        sel = self.pr if pass_side else ~self.pr
        return self.r[sel] / self.w_push[sel]

    def on_predict(self, role, X, inner):
        if role == "reg" and self.arm in ("MO", "OP"):
            out = self.oracle_new_w(pass_side=False)
            if len(out) != len(X):
                raise TraceError(f"{self.arm}: the oracle does not match the misses")
            self.fill = np.array(out, dtype=float, copy=True)
            return out
        return super().on_predict(role, X, inner)

    def count_clip(self, role, out):
        if role in self.clip:
            p = np.asarray(out)[:, 1]
            self.clip[role].append((int(np.sum(p <= CLIP)), int(np.sum(p >= 1.0 - CLIP))))

    # -- C-ARM, checked at every iteration --------------------------------------------------------
    def _checked(self, callback):
        def cb(k, w_pull, w_push, new_w):
            self.arm_check(k, w_pull, w_push, new_w)
            callback(k, w_pull, w_push, new_w)
        return cb

    def arm_check(self, k, w_pull, w_push, new_w):
        fail = ~self.pr
        ev = self.evidence
        if self.arm == "MU":
            ok = bool(np.all(new_w[fail] == 1.0))
            ev["fill_all_one"].append(ok)
            if not ok:
                raise TraceError(f"C-ARM MU: iteration {k}: a miss fill is not 1")
        if self.arm == "MW":
            want = self.w_push[self.pr] * self.w_truth[self.pr]  # still the w_push this iteration started from
            if self.mw_given is None or not np.array_equal(self.mw_given, want):
                raise TraceError(f"C-ARM MW: iteration {k}: the regressor's weight is not w_push * w_truth")
            ev["mw_fits"] += 1
            self.mw_given = None
        if self.arm in ("MO", "OP"):
            sel = fail if self.arm == "MO" else np.ones(self.n, bool)
            dev = float(np.max(np.abs(w_pull[sel] / self.r[sel] - 1.0))) if sel.any() else 0.0
            ev["max_rel_oracle"].append(dev)
            if not dev <= ORACLE_RTOL:
                raise TraceError(f"C-ARM {self.arm}: iteration {k}: w_pull departs from r by {dev:.3e}")
        if self.arm == "OP":  # recorded, not gated: w_pull = r only to the p/(1-p) round trip, so step 2's inputs
            if self._prev_push is not None:  # repeat to ~1e-16 and its output need not repeat bitwise
                ev["op_push_rel_change"] = float(np.max(np.abs(w_push / self._prev_push - 1.0)))
            self._prev_push = np.array(w_push, copy=True)


class ArmRecorder(Recorder):
    """``s5e_trace.Recorder`` with U = M16 (so its truth functionals are R00-R15) and the reco cells: ``fm`` is S1's
    fine map (fine cell -> reporting cell, -1 outside), applied to reco counts with no bin volume (§4.3)."""

    def __init__(self, unf_in: dict, r: np.ndarray, M16: np.ndarray, fm: np.ndarray, iters: int):
        super().__init__(unf_in, r, M16, iters, snapshots=())
        fm = np.asarray(fm)
        if fm.shape != (self.ncell,):
            raise TraceError("the fine map does not match the grid")
        self.Mc = np.vstack([(fm == c).astype(float) for c in range(N_CELLS)])
        self.unf_in = unf_in
        o = self.out
        for key in ("D", "true", "prior"):
            o[f"R16_{key}"] = self.Mc @ o[f"reco5d_{key}"]
        o["R16_in_cells_prior"] = float(o["reco5d_prior"][fm >= 0].sum())  # C-RECO
        o["R16_in_cells_D"] = float(o["reco5d_D"][fm >= 0].sum())
        for key in ("R16_pull", "R16_push", "miss_share16"):
            o[key] = np.zeros((iters, N_CELLS))
        for key in ("norm_pull", "norm_push"):
            o[key] = np.zeros(iters)
        self.xs_at = {}

    def on_iteration(self, k, w_pull, w_push, new_w):
        super().on_iteration(k, w_pull, w_push, new_w)
        i, o = k - 1, self.out
        o["R16_pull"][i] = self.Mc @ self.reco(w_pull)
        o["R16_push"][i] = self.Mc @ self.reco(w_push)
        full = self.fn(self.wt * w_pull)
        miss = self.fn(self.wt * w_pull * (~self.pr))
        o["miss_share16"][i] = np.divide(miss, full, out=np.zeros_like(full), where=full != 0)
        o["norm_pull"][i] = float(np.sum(self.wt * w_pull) / np.sum(self.wt))
        o["norm_push"][i] = float(np.sum(self.wt * w_push) / np.sum(self.wt))
        if k in PAIR_KS:
            self.xs_at[k] = xs_from_push(self.unf_in, w_push).ravel(order="C")

    def arrays(self, tracer: ArmTracer) -> dict:
        """The product's trace arrays (``t3p_read`` reads them; every name is fixed here)."""
        o = self.out
        out = {"X16_push": o["fn_push"], "X16_pull": o["fn_pull"], "R16_pull": o["R16_pull"], "R16_push": o["R16_push"],
               "R16_D": o["R16_D"], "R16_true": o["R16_true"], "R16_prior": o["R16_prior"],
               "miss_share16": o["miss_share16"], "norm_pull": o["norm_pull"], "norm_push": o["norm_push"],
               "mean_fill_fail": o["mean_fill_fail"],
               "reco_in_cells": np.array([o["R16_in_cells_prior"], o["R16_in_cells_D"]]),
               "clip_step1": np.array(tracer.clip["step1"], float).reshape(-1, 2),
               "clip_step2": np.array(tracer.clip["step2"], float).reshape(-1, 2)}
        for k, xs in self.xs_at.items():
            out[f"xs_k{k}"] = xs
        return out


def traced_unfold_arm(unf_in: dict, recorder: ArmRecorder, seed: int, threads: int, iters: int, arm: str,
                      r_rows: np.ndarray) -> tuple[np.ndarray, list, ArmTracer]:
    """``s5c_unfold.unfold`` with the arm's tracer installed; ``r_rows`` is r on every unfolding-MC row (before the
    pass-truth filter). Verifies the final state bitwise, as ``s5e_trace.traced_unfold`` does."""
    m = np.asarray(unf_in["pass_truth"], bool)
    r_rows = np.asarray(r_rows, float)
    if r_rows.shape != m.shape:
        raise TraceError("r does not have one entry per unfolding-MC row")
    ctx = {"pass_reco": np.asarray(unf_in["pass_reco"])[m], "w_truth": np.asarray(unf_in["w_truth"])[m],
           "w_reco": np.asarray(unf_in["w_reco"])[m]}
    tracer = ArmTracer(ctx, recorder.on_iteration, arm, r_rows[m])
    original = onc.make_estimators
    onc.make_estimators = tracer.factory(original)
    try:
        xs, params = s5c_unfold.unfold(unf_in, "deterministic", seed, threads, iters)
    finally:
        onc.make_estimators = original
    if tracer.factory_calls != 1 or tracer.k != iters:
        raise TraceError(f"factory calls {tracer.factory_calls}, iterations traced {tracer.k} of {iters}")
    if not np.array_equal(xs, xs_from_push(unf_in, tracer.w_push)):
        raise TraceError("the unfold recomputed from the traced final w_push differs from the returned one")
    if arm == "MW" and tracer.evidence["mw_fits"] != iters:
        raise TraceError(f"C-ARM MW: {tracer.evidence['mw_fits']} weighted fits in {iters} iterations")
    if arm == "OP" and tracer.evidence["op_push_rel_change"] is None:
        raise TraceError("C-ARM OP: the second iteration was not observed")
    recorder.finish(unf_in, tracer)
    return xs, params, tracer


__all__ = ["ARMS", "ITERS", "PAIR_KS", "ArmTracer", "ArmRecorder", "traced_unfold_arm", "binned", "s5e_trace"]
