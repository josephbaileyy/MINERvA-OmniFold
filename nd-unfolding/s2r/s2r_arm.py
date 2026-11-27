#!/usr/bin/env python3
"""S2R: the production unfold with step 2 learned relative to the previous push weights, and its traced readouts.

Declaration: ``docs/orchestration/state/measurement-paper/5d-community-20261024/fd/s2r-20261124/S2R-DECLARATION.md``.

THE LOOP IS NOT RE-IMPLEMENTED. As in ``tier3/t3p_arms.py``, the unfold is ``s5c_unfold.unfold`` (the production
``omnifold_nn_core.omnifold_loop``), reached with ``omnifold_nn_core.make_estimators`` rebound so the loop receives thin
wrappers around its own three estimators; ``s5e_trace``'s bitwise rebuild of w_pull and w_push is inherited unchanged.

* ``B0``: nothing (the trace only); the production estimator.
* ``S2R``: step 2 in the form of Andreassen et al., arXiv:1911.09107, Step 2,
  nu_n = nu_{n-1} * L[(omega_n^pull, Gen), (nu_{n-1}, Gen)]. The loop hands step 2's fit the weights
  [w_truth, w_pull * w_truth] (``omnifold_nn_core.py``, s2w), which the tracer checks bitwise as it always does; the
  wrapper then fits the inner classifier on [nu_{n-1} * w_truth, w_pull * w_truth] instead, and its ``predict_proba``
  returns p with p / (1 - p) = nu_{n-1} * L, L being the inner classifier's clipped ratio. So the loop's own
  ``_reweight`` sets w_push = nu_{n-1} * L (C-ARM STOPs if any row's nu_{n-1} * L reaches the loop's clip of p, where
  the loop would saturate it). Nothing else changes: step 1, the regressor and the extraction are the
  loop's. At n = 1, nu_0 = 1, so S2R's first fit is B0's (its output differs only by the p -> q -> p round trip).

S2R uses only w_pull and w_push, which the loop computes from the pseudo-data and the simulation: no truth weight
reaches it. ``r`` enters only the recorder (the readouts), as in T3.

MEASURES: the internal response of one unfold. CANNOT AUTHORIZE: an estimator change (that is the director's, then
Joseph's), or any statement about data.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parents[1]
for _p in (_ND, _ND / "tier3"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
import omnifold_nn_core as onc  # noqa: E402
import s5c_unfold  # noqa: E402
import t3p_arms as A  # noqa: E402
from s5e_trace import TraceError, reweight_like_loop, xs_from_push  # noqa: E402

ARMS = ("B0", "S2R")
ITERS = {"B0": 5, "S2R": 20}
GRADE_K = 5  # the production iteration count: the declared test reads every arm at k = 5
ROUND_TRIP_RTOL = 1e-10  # C-ARM: w_push equals nu_{n-1} * L to this relative tolerance where neither is clipped
CLIP = A.CLIP
Q_LOW, Q_HIGH = 1.01 * CLIP / (1 - CLIP), 0.99 * (1 - CLIP) / CLIP  # inside the loop's clip of p, with margin


class S2RWrapped(A.ArmWrapped):
    """``t3p_arms.ArmWrapped`` with S2R's step-2 intervention (fit weights and output)."""

    def fit(self, X, y, sample_weight=None):
        t = self._tracer
        if self._role == "step2" and t.arm == "S2R":
            t.on_fit(self._role, X, y, sample_weight)  # the loop's own weights, checked bitwise by s5e_trace
            w = t.s2r_weight(sample_weight)
            self._inner.fit(X, y, sample_weight=w)
            return self
        return super().fit(X, y, sample_weight=sample_weight)

    def predict_proba(self, X):
        t = self._tracer
        if self._role == "step2" and t.arm == "S2R":
            inner = self._inner.predict_proba(X)
            t.count_clip(self._role, inner)
            out = t.s2r_output(inner)
            t.on_proba(self._role, out)
            return out
        return super().predict_proba(X)


class S2RTracer(A.ArmTracer):
    """``t3p_arms.ArmTracer`` for B0 or S2R."""

    def __init__(self, ctx: dict, callback, arm: str, r: np.ndarray):
        if arm not in ARMS:
            raise ValueError(f"unknown arm {arm!r}")
        super().__init__(ctx, callback, "B0", r)  # B0's tracer: no T3 intervention fires for "S2R" either
        self.arm = arm
        self.evidence["arm"] = arm
        self.evidence.update({"s2r_fits": 0, "s2r_max_round_trip": [], "s2r_clipped": [], "s2r_ref_is_push": []})
        self._s2r_ref = None
        self._s2r_q = None

    def factory(self, original):
        def make(kind, nvars, seed=None):
            self.factory_calls += 1
            ests = list(original(kind, nvars, seed=seed))
            return tuple(S2RWrapped(self, role, est) for role, est in zip(("step1", "step2", "reg"), ests))
        return make

    # -- the intervention ------------------------------------------------------------------------
    def s2r_weight(self, loop_w) -> np.ndarray:
        """Step 2's fit weights with the first class at nu_{n-1} * w_truth (the loop's second class kept)."""
        loop_w = np.asarray(loop_w, float)
        if loop_w.shape != (2 * self.n,):
            raise TraceError("S2R: step 2's weights do not cover both classes")
        ref = np.array(self.w_push, dtype=float, copy=True)  # nu_{n-1}: the tracer's w_push before this step 2
        self._s2r_ref = ref
        w = loop_w.copy()
        w[:self.n] = ref * self.w_truth
        self.evidence["s2r_fits"] += 1
        return w

    def s2r_output(self, inner) -> np.ndarray:
        """predict_proba with p / (1 - p) = nu_{n-1} * L."""
        if self._s2r_ref is None:
            raise TraceError("S2R: step 2 predicted before its fit")
        inner = np.asarray(inner)
        if inner.shape != (self.n, 2):
            raise TraceError("S2R: step 2's output does not match the truth rows")
        q = self._s2r_ref * reweight_like_loop(inner)
        self._s2r_q = q
        p = q / (1.0 + q)
        return np.column_stack([1.0 - p, p])

    # -- C-ARM, checked at every iteration --------------------------------------------------------
    def arm_check(self, k, w_pull, w_push, new_w):
        super().arm_check(k, w_pull, w_push, new_w)
        if self.arm != "S2R":
            return
        ev = self.evidence
        if ev["s2r_fits"] != k or self._s2r_q is None:
            raise TraceError(f"C-ARM S2R: iteration {k}: {ev['s2r_fits']} relative fits")
        if not np.array_equal(self._s2r_ref, self.w_push):  # the tracer's w_push is still nu_{n-1} here
            raise TraceError(f"C-ARM S2R: iteration {k}: the reference is not the previous push weights")
        q = self._s2r_q
        free = (q > Q_LOW) & (q < Q_HIGH)
        dev = float(np.max(np.abs(w_push[free] / q[free] - 1.0))) if free.any() else 0.0
        ev["s2r_max_round_trip"].append(dev)
        ev["s2r_clipped"].append(int((~free).sum()))
        ev["s2r_ref_is_push"].append(bool(k > 1 or np.all(self._s2r_ref == 1.0)))
        if not free.all():  # the loop's clip of p would replace nu_(n-1) * L on these rows: not the declared product
            raise TraceError(f"C-ARM S2R: iteration {k}: {int((~free).sum())} rows of nu_(n-1) * L outside "
                             f"({Q_LOW:.3g}, {Q_HIGH:.3g}), where the loop's clip of p saturates")
        if not dev <= ROUND_TRIP_RTOL:
            raise TraceError(f"C-ARM S2R: iteration {k}: w_push departs from nu_(n-1) * L by {dev:.3e}")
        if k == 1 and not np.all(self._s2r_ref == 1.0):
            raise TraceError("C-ARM S2R: iteration 1's reference is not nu_0 = 1")
        self._s2r_ref = self._s2r_q = None


def traced_unfold_s2r(unf_in: dict, recorder: A.ArmRecorder, seed: int, threads: int, iters: int, arm: str,
                      r_rows: np.ndarray):
    """``s5c_unfold.unfold`` with the arm's tracer installed (``t3p_arms.traced_unfold_arm``'s checks)."""
    m = np.asarray(unf_in["pass_truth"], bool)
    r_rows = np.asarray(r_rows, float)
    if r_rows.shape != m.shape:
        raise TraceError("r does not have one entry per unfolding-MC row")
    if iters != ITERS[arm]:
        raise TraceError(f"arm {arm} runs {ITERS[arm]} iterations, not {iters}")
    ctx = {"pass_reco": np.asarray(unf_in["pass_reco"])[m], "w_truth": np.asarray(unf_in["w_truth"])[m],
           "w_reco": np.asarray(unf_in["w_reco"])[m]}
    tracer = S2RTracer(ctx, recorder.on_iteration, arm, r_rows[m])
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
    if arm == "S2R" and tracer.evidence["s2r_fits"] != iters:
        raise TraceError(f"C-ARM S2R: {tracer.evidence['s2r_fits']} relative fits in {iters} iterations")
    recorder.finish(unf_in, tracer)
    return xs, params, tracer


__all__ = ["ARMS", "ITERS", "GRADE_K", "S2RTracer", "S2RWrapped", "traced_unfold_s2r"]
