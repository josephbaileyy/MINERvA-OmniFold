#!/usr/bin/env python3
"""s5e (``OI-192``) diagnosis instrumentation: one traced unfold of a declared construction.

Authority: ``docs/orchestration/AUTHORIZATION-20260925-oi192-estimator-diagnosis.md``; contract
``docs/orchestration/state/s5e/contract.json`` (``stage_D_diagnosis``).

THE LOOP IS NOT RE-IMPLEMENTED. The unfold is ``s5c_unfold.unfold`` (the production
``omnifold_nn_core.omnifold_loop`` with the F2 parameters), reached through
``s5n_pseudo.unfold_negweight`` for the background-inclusive and data constructions. Tracing works by
rebinding ``omnifold_nn_core.make_estimators`` (the same hook ``s5c_unfold.estimator_config`` uses) so
the loop receives thin wrappers around the three real estimators. From what the loop passes to them
the tracer rebuilds ``w_pull`` and ``w_push`` at every iteration and checks the rebuild BITWISE against
the weights the loop itself hands to the next step (step 2's second class carries ``w_pull * w_truth``;
the next step 1's MC class carries ``w_push * w_reco``). A final check recomputes the unfold from the
last ``w_push`` with ``s5c_unfold.unfold``'s own extraction lines and requires equality with the
returned unfold. A run that fails any check writes nothing.

Constructions (``--construction``):

* ``pseudo``: ``s5n_pseudo.build_pseudo`` (background-inclusive, or ``--no-background``), then
  ``s5n_pseudo.unfold_negweight`` -- exactly the s5n development experiment.
* ``asimov_same``: noise-free. The full MC is the unfolding MC and the pseudo-data source; the
  pseudo-data are every reco-passing MC row at weight ``w_reco * r``; truth is the full MC truth
  reweighted by ``r``. No Poisson, no background, no refinement.
* ``data``: the real data against the full background dump (``s5n_pseudo.build_data``), refined.

One-factor probes (each changes one declared thing; the default is B0 exactly): ``--capacity N,L``
(n_estimators, num_leaves of all three OmniFold estimators); ``--missed unity`` (reco-failing events
keep new_w = 1 instead of the regressor's fill); ``--seed-per-estimator`` (random_state seed, seed+1,
seed+2 as the driver sets them); ``--coords float64`` / ``--jitter-f32 S`` (float64 coordinates,
optionally perturbed uniformly within +-1/2 float32 ulp); ``--refine-capacity N,L`` (the refinement
classifier); ``--expectation-template`` (the template is the background source rows at their expected
weight 2 w_bkg).

Per iteration it records truth functionals from ``w_push`` and ``w_pull``, reco-level forward folds
(5D grid, (E_avail,W) projection) of ``w_pull`` and ``w_push`` beside the measured side, the folded
truth model and the prior, and per truth (E_avail,W) cell the sums that separate reco-passing and
reco-failing (regressor-filled) events.

MEASURES: the internal response of one unfold of one construction. CANNOT AUTHORIZE: a cause by
itself (the contract's attribution rule needs interventions and noise), a coverage verdict, or any
statement about the real data beyond pipeline behaviour.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parent
if str(_ND) not in sys.path:
    sys.path.insert(0, str(_ND))
import omnifold_nn_core as onc  # noqa: E402
import s5c_pseudo  # noqa: E402
import s5c_unfold  # noqa: E402
import s5n_pseudo  # noqa: E402
from xsec_nd import extract_cross_section_nd  # noqa: E402

CONSTRUCTIONS = ("pseudo", "asimov_same", "data")
SNAPSHOTS = (1, 2, 3, 5, 8, 10, 15, 20, 25, 30)


class TraceError(RuntimeError):
    """The rebuilt weights disagree with the loop's own: the trace does not describe this unfold."""


# ------------------------------------------------------------------------------------ binning


def flat_index(coords: np.ndarray, edges: list) -> np.ndarray:
    """np.histogramdd's bin of every row as a flat C-order index, -1 outside (last edge inclusive)."""
    shape = tuple(len(e) - 1 for e in edges)
    ok = np.ones(coords.shape[0], bool)
    parts = []
    for k, e in enumerate(edges):
        e = np.asarray(e, float)
        x = np.asarray(coords[:, k], float)
        i = np.searchsorted(e, x, side="right") - 1
        i[x == e[-1]] = len(e) - 2
        ok &= (i >= 0) & (i < len(e) - 1)
        parts.append(np.clip(i, 0, len(e) - 2))
    flat = np.ravel_multi_index(parts, shape)
    flat[~ok] = -1
    return flat


def binned(flat: np.ndarray, w: np.ndarray, n: int) -> np.ndarray:
    ok = flat >= 0
    return np.bincount(flat[ok], weights=np.asarray(w, float)[ok], minlength=n)


def ew_of_flat(flat: np.ndarray, shape: tuple) -> np.ndarray:
    """The (E_avail, W) cell ie*6+iw of each 5D flat index (-1 stays -1)."""
    out = -np.ones(flat.shape, dtype=np.int64)
    ok = flat >= 0
    idx = np.unravel_index(flat[ok], shape)
    out[ok] = idx[2] * shape[4] + idx[4]
    return out


def xs_from_push(d: dict, wpush: np.ndarray) -> np.ndarray:
    """``s5c_unfold.unfold``'s extraction lines, verbatim, applied to a given w_push."""
    m = d["pass_truth"]
    edges = d["edges"]
    samp = np.column_stack([d["MCgen"][m, i] for i in range(d["MCgen"].shape[1])])
    unf, _ = np.histogramdd(samp, bins=edges, weights=wpush * d["w_truth"][m])
    ofin, _ = np.histogramdd(samp, bins=edges, weights=d["w_truth"][m])
    dn = d["denom_nd"]
    comp = np.zeros_like(ofin)
    nz = dn > 0
    comp[nz] = ofin[nz] / dn[nz]
    xs, _ = extract_cross_section_nd(unf, comp, d["flux"], float(d["data_pot"]),
                                     float(d["n_nucleons"]), edges)
    return xs


def reweight_like_loop(p: np.ndarray) -> np.ndarray:
    """``omnifold_nn_core._reweight`` applied to predict_proba output already in hand."""
    p = np.asarray(p)[:, 1]
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return np.nan_to_num(p / (1.0 - p))


# ------------------------------------------------------------------------------------ tracer


class _Wrapped:
    """Delegate to a real estimator; the tracer observes calls."""

    def __init__(self, tracer: "Tracer", role: str, inner):
        self._tracer, self._role, self._inner = tracer, role, inner

    def get_params(self, deep=True):
        return self._inner.get_params(deep)

    def set_params(self, **kw):
        self._inner.set_params(**kw)
        return self

    def fit(self, X, y, sample_weight=None):
        self._tracer.on_fit(self._role, X, y, sample_weight)
        self._inner.fit(X, y, sample_weight=sample_weight)
        return self

    def predict_proba(self, X):
        out = self._inner.predict_proba(X)
        self._tracer.on_proba(self._role, out)
        return out

    def predict(self, X):
        out = self._tracer.on_predict(self._role, X, self._inner)
        return out


class Tracer:
    """Rebuilds the loop's weights per iteration and hands them to ``callback``.

    ``ctx`` holds the pass-truth-filtered MC arrays as the loop sees them: ``pass_reco``, ``w_truth``,
    ``w_reco``. ``callback(k, w_pull, w_push, new_w)`` runs after iteration k (1-based)."""

    def __init__(self, ctx: dict, callback, capacity: tuple | None = None, missed: str = "regress",
                 seed_per_estimator: bool = False):
        if missed not in ("regress", "unity"):
            raise ValueError(missed)
        self.pr = np.asarray(ctx["pass_reco"], bool)
        self.w_truth = np.asarray(ctx["w_truth"], float)
        self.w_reco = np.asarray(ctx["w_reco"], float)
        self.n = self.pr.size
        self.callback = callback
        self.capacity = capacity
        self.missed = missed
        self.seed_per_estimator = seed_per_estimator
        self.k = 0
        self.w_push = np.ones(self.n)
        self.nw_pass = None
        self.fill = None
        self.checks = {"step1_mc_weights": 0, "step2_pull_weights": 0}
        self.factory_calls = 0
        self.built_params: list = []

    def factory(self, original):
        def make(kind, nvars, seed=None):
            self.factory_calls += 1
            ests = list(original(kind, nvars, seed=seed))
            for i, est in enumerate(ests):
                if self.capacity is not None:
                    est.set_params(n_estimators=int(self.capacity[0]), num_leaves=int(self.capacity[1]))
                if self.seed_per_estimator and seed is not None:
                    est.set_params(random_state=int(seed) + i)
            return (_Wrapped(self, "step1", ests[0]), _Wrapped(self, "step2", ests[1]),
                    _Wrapped(self, "reg", ests[2]))
        return make

    # -- observed calls -----------------------------------------------------------------------
    def on_fit(self, role, X, y, w):
        if role == "step1":
            self.nw_pass = self.fill = None
            npr = int(self.pr.sum())
            want = self.w_push[self.pr] * self.w_reco[self.pr]
            if not np.array_equal(np.asarray(w)[:npr], want):
                raise TraceError(f"iteration {self.k + 1}: step-1 MC weights differ from the rebuilt w_push")
            self.checks["step1_mc_weights"] += 1
        elif role == "reg":
            self.nw_pass = np.array(y, dtype=float, copy=True)  # the loop's own new_w[pass_reco]
        elif role == "step2":
            new_w = np.ones(self.n)
            if self.nw_pass is None:
                raise TraceError("step 2 before step 1's reweighting was observed")
            new_w[self.pr] = self.nw_pass
            if self.fill is not None:
                new_w[~self.pr] = self.fill
            w_pull = self.w_push * new_w
            w = np.asarray(w)
            if not (np.array_equal(w[:self.n], self.w_truth) and np.array_equal(w[self.n:], w_pull * self.w_truth)):
                raise TraceError(f"iteration {self.k + 1}: step-2 weights differ from the rebuilt w_pull")
            self.checks["step2_pull_weights"] += 1
            self._pending = (w_pull, new_w)

    def on_proba(self, role, out):
        if role == "step1":
            if self.nw_pass is None:
                self.nw_pass = reweight_like_loop(out)  # replaced by the regressor's target when it runs
        elif role == "step2":
            w_push = reweight_like_loop(out)
            w_pull, new_w = self._pending
            self.k += 1
            self.callback(self.k, w_pull, w_push, new_w)
            self.w_push = w_push

    def on_predict(self, role, X, inner):
        if role != "reg":
            return inner.predict(X)
        out = inner.predict(X) if self.missed == "regress" else np.ones(len(X))
        self.fill = np.array(out, dtype=float, copy=True)
        return out


def traced_unfold(unf_in: dict, recorder, seed: int, threads: int, iters: int, capacity=None,
                  missed="regress", seed_per_estimator=False) -> tuple[np.ndarray, list, "Tracer"]:
    """``s5c_unfold.unfold`` with the tracer installed; verifies the final state bitwise."""
    m = np.asarray(unf_in["pass_truth"], bool)
    ctx = {"pass_reco": np.asarray(unf_in["pass_reco"])[m], "w_truth": np.asarray(unf_in["w_truth"])[m],
           "w_reco": np.asarray(unf_in["w_reco"])[m]}
    tracer = Tracer(ctx, recorder.on_iteration, capacity, missed, seed_per_estimator)
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
    recorder.finish(unf_in, tracer)
    return xs, params, tracer


# ---------------------------------------------------------------------------------- recorder


class Recorder:
    """Per-iteration reductions. ``r`` is the truth reweight of the unfolding-MC rows (ones if none)."""

    def __init__(self, unf_in: dict, r: np.ndarray, U: np.ndarray, iters: int, snapshots=SNAPSHOTS):
        m = np.asarray(unf_in["pass_truth"], bool)
        self.edges = unf_in["edges"]
        self.shape = tuple(len(e) - 1 for e in self.edges)
        self.ncell = int(np.prod(self.shape))
        self.n_ew = self.shape[2] * self.shape[4]
        self.U = U
        self.iters = iters
        self.snap = [k for k in snapshots if k <= iters]
        gen, reco = np.asarray(unf_in["MCgen"])[m], np.asarray(unf_in["MCreco"])[m]
        self.pr = np.asarray(unf_in["pass_reco"])[m]
        self.wt = np.asarray(unf_in["w_truth"], float)[m]
        self.wr = np.asarray(unf_in["w_reco"], float)[m]
        self.r = np.asarray(r, float)[m]
        self.tflat = flat_index(gen, self.edges)
        self.rflat = flat_index(reco[self.pr], self.edges)
        self.tew = ew_of_flat(self.tflat, self.shape)
        ofin = binned(self.tflat, self.wt, self.ncell).reshape(self.shape)
        dn = unf_in["denom_nd"]
        self.comp = np.zeros_like(ofin)
        self.comp[dn > 0] = ofin[dn > 0] / dn[dn > 0]
        self.flux, self.pot, self.nn = unf_in["flux"], float(unf_in["data_pot"]), float(unf_in["n_nucleons"])
        mflat = flat_index(np.asarray(unf_in["measured"]), self.edges)
        mw = np.asarray(unf_in["measured_weights"], float)
        self.out = {
            "reco5d_D": binned(mflat, mw, self.ncell), "reco5d_Dvar": binned(mflat, mw ** 2, self.ncell),
            "reco5d_true": self.reco(self.r), "reco5d_prior": self.reco(np.ones_like(self.r)),
            "fn_true_A": self.fn(self.wt * self.r),
            "fn_pull": np.zeros((iters, U.shape[0])), "fn_push": np.zeros((iters, U.shape[0])),
            "reco_ew_pull": np.zeros((iters, self.n_ew)), "reco_ew_push": np.zeros((iters, self.n_ew)),
        }
        for key in ("w", "wnew", "wr", "wpull", "wpush"):
            for side in ("pass", "fail"):
                self.out[f"truth_ew_{side}_{key}"] = np.zeros((iters, self.n_ew))
        for key in ("D", "true", "prior"):
            self.out[f"reco_ew_{key}"] = self.ew_project(self.out[f"reco5d_{key}"])
        self.out["mean_fill_fail"] = np.zeros(iters)
        self.xs_it5 = None

    def reco(self, w_row: np.ndarray) -> np.ndarray:
        return binned(self.rflat, self.wr[self.pr] * np.asarray(w_row)[self.pr], self.ncell)

    def fn(self, w_truth_row: np.ndarray) -> np.ndarray:
        unf = binned(self.tflat, w_truth_row, self.ncell).reshape(self.shape)
        xs, _ = extract_cross_section_nd(unf, self.comp, self.flux, self.pot, self.nn, self.edges)
        return self.U @ xs.ravel(order="C")

    def ew_project(self, h5: np.ndarray) -> np.ndarray:
        return np.asarray(h5).reshape(self.shape).sum(axis=(0, 1, 3)).ravel(order="C")

    def on_iteration(self, k, w_pull, w_push, new_w):
        i = k - 1
        o = self.out
        o["fn_pull"][i] = self.fn(self.wt * w_pull)
        o["fn_push"][i] = self.fn(self.wt * w_push)
        rp, rq = self.reco(w_pull), self.reco(w_push)
        o["reco_ew_pull"][i] = self.ew_project(rp)
        o["reco_ew_push"][i] = self.ew_project(rq)
        if k in self.snap:
            o[f"reco5d_pull_it{k}"] = rp.astype(np.float32)
            o[f"reco5d_push_it{k}"] = rq.astype(np.float32)
        for side, sel in (("pass", self.pr), ("fail", ~self.pr)):
            ew = np.where(sel, self.tew, -1)
            for key, w in (("w", self.wt), ("wnew", self.wt * new_w), ("wr", self.wt * self.r),
                           ("wpull", self.wt * w_pull), ("wpush", self.wt * w_push)):
                o[f"truth_ew_{side}_{key}"][i] = binned(ew, w, self.n_ew)
        fail = ~self.pr
        o["mean_fill_fail"][i] = float(new_w[fail].mean()) if fail.any() else 1.0
        if k == 5:
            self._wpush5 = w_push.copy()

    def finish(self, unf_in, tracer):
        """The iteration-5 unfold through the production extraction (control D0 compares it bitwise)."""
        if getattr(self, "_wpush5", None) is not None:
            self.xs_it5 = xs_from_push(unf_in, self._wpush5)
            self._wpush5 = None


# ------------------------------------------------------------------------------ constructions


def jitter_coords(x: np.ndarray, seed: int | None, edges: list | None = None) -> np.ndarray:
    """float64 copy; with a seed, each value moved uniformly within +-1/2 of its float32 ulp.

    With ``edges`` (edge-safe mode) a value equal to a grid edge of its axis is NOT moved. Without it
    (the original D2(b) probe) exact zeros sitting on the lower edge 0 -- 293,292 truth E_avail and
    231,685 reco W rows of the MC, 48,082 reco W rows of the data -- can be pushed below the edge and
    out of the grid, a change that float64-to-float32 rounding never makes (0 is exact in both)."""
    x32 = np.asarray(x, np.float32)
    out = x32.astype(np.float64)
    if seed is None:
        return out
    ulp = np.spacing(np.abs(x32)).astype(np.float64)
    rng = np.random.default_rng(seed)
    step = rng.uniform(-0.5, 0.5, out.shape) * ulp
    if edges is not None:
        for k, e in enumerate(edges):
            step[np.isin(out[:, k], np.asarray(e, np.float32).astype(np.float64)), k] = 0.0
    return out + step


def drop_sentinel_rows(inputs: dict) -> int:
    """Mark MC rows with a -9999 truth sentinel on any axis as failing the truth selection (the driver
    never admits them: its truth-passing set is 2,801 rows smaller than the npz's); returns the count."""
    bad = np.any(np.asarray(inputs["MCgen"]) < -9000, axis=1)
    inputs["pass_truth"] = np.asarray(inputs["pass_truth"], bool) & ~bad
    return int(bad.sum())


def asimov_same(inputs: dict, r: np.ndarray) -> tuple[dict, np.ndarray]:
    """Noise-free: the full MC unfolds its own reco-passing rows reweighted by r."""
    pr = inputs["pass_reco"] & inputs["pass_truth"]
    unf_in = {k: inputs[k] for k in ("MCgen", "MCreco", "pass_reco", "pass_truth", "w_truth", "w_reco",
                                     "denom_nd", "flux", "data_pot", "n_nucleons", "edges")}
    unf_in["measured"] = inputs["MCreco"][pr]
    unf_in["measured_weights"] = inputs["w_reco"][pr] * r[pr]
    m = inputs["pass_truth"]
    samp = inputs["MCgen"][m]
    edges = inputs["edges"]
    unf, _ = np.histogramdd(samp, bins=edges, weights=inputs["w_truth"][m] * r[m])
    ofin, _ = np.histogramdd(samp, bins=edges, weights=inputs["w_truth"][m])
    dn = inputs["denom_nd"]
    comp = np.zeros_like(ofin)
    comp[dn > 0] = ofin[dn > 0] / dn[dn > 0]
    x_true, _ = extract_cross_section_nd(unf, comp, inputs["flux"], float(inputs["data_pot"]),
                                         float(inputs["n_nucleons"]), edges)
    return unf_in, x_true


def expectation_template(exp: dict, bkg: dict, split_key: int) -> dict:
    """The template becomes the background SOURCE rows (half C) at their expected weight 2 w_bkg."""
    nb = bkg["bkg_w"].shape[0]
    is_c = s5c_pseudo.half_mask(nb, s5n_pseudo.bkg_split_key(split_key))
    tmpl = bkg["bkg_reco"][is_c]
    keep = s5n_pseudo.fid_mask(tmpl, exp["edges"])
    out = dict(exp)
    out["tmpl"], out["tmpl_w"] = tmpl[keep], 2.0 * bkg["bkg_w"][is_c][keep]
    return out


def refine_variant(feat, signed, seed: int, threads: int, override: dict) -> tuple[np.ndarray, dict]:
    """The driver's refinement with the F2 parameters plus a declared override, evidence recorded."""
    u2d = s5n_pseudo.load_u2d()
    params = {**s5n_pseudo.refine_params(seed, threads), **override}
    record: list = []
    t0 = time.time()
    with s5n_pseudo.recorded_classifier(u2d, record):
        w_ref, g, frac = u2d.refine_stay_positive(feat, signed, estimator="lgbm", device="cpu",
                                                  params=params, verbose=False)
    if len(record) != 1 or any(record[0].get(k) != v for k, v in override.items()):
        raise RuntimeError(f"refinement override did not reach the classifier: {record}")
    return w_ref, s5n_pseudo.refinement_evidence(signed, w_ref, g, frac, record[0], time.time() - t0)


def measured_side(exp: dict, seed: int, threads: int, refine_override: dict | None,
                  coords_dtype=np.float32) -> tuple[np.ndarray, np.ndarray, dict]:
    """``s5n_pseudo.unfold_negweight``'s measured side, with an optional refinement override."""
    feat, signed, n_obs, n_tmpl = s5n_pseudo.signed_sample(exp)
    if n_tmpl == 0:
        w_ref, ev = signed.copy(), {"ran": False, "reason": "no negative weights (signal-only reference)"}
    elif refine_override:
        w_ref, ev = refine_variant(feat, signed, seed, threads, refine_override)
    else:
        w_ref, ev = s5n_pseudo.refine(feat, signed, seed, threads)
    ev.update({"n_observed_rows": n_obs, "n_template_rows": n_tmpl})
    return feat.astype(coords_dtype), w_ref, ev


def unf_inputs(exp: dict, feat, w_ref) -> dict:
    unf_in = {k: exp[k] for k in ("MCgen", "MCreco", "pass_reco", "pass_truth", "w_truth", "w_reco",
                                  "denom_nd", "flux", "data_pot", "n_nucleons", "edges")}
    unf_in["measured"], unf_in["measured_weights"] = feat, w_ref
    return unf_in


# ------------------------------------------------------------------------------------------ cli


def parse_pair(text: str | None) -> tuple | None:
    if text is None:
        return None
    a, b = (int(v) for v in text.split(","))
    return a, b


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--npz", type=Path, required=True)
    ap.add_argument("--bkg", type=Path, required=True)
    ap.add_argument("--expect-npz-sha256", required=True)
    ap.add_argument("--expect-bkg-sha256", required=True)
    ap.add_argument("--s5c-contract", type=Path, required=True, help="defines the reported functionals")
    ap.add_argument("--construction", choices=CONSTRUCTIONS, required=True)
    ap.add_argument("--truth", choices=s5n_pseudo.TRUTHS, default="nominal")
    ap.add_argument("--amplitude", type=float, default=0.0)
    ap.add_argument("--eavail-ratio", type=Path, default=None)
    ap.add_argument("--pseudo-seed", type=int, default=None)
    ap.add_argument("--no-background", action="store_true")
    ap.add_argument("--estimator-seed", type=int, default=42)
    ap.add_argument("--iters", type=int, default=5)
    ap.add_argument("--capacity", default=None, help="N,L: n_estimators,num_leaves of the OmniFold estimators")
    ap.add_argument("--missed", choices=("regress", "unity"), default="regress")
    ap.add_argument("--seed-per-estimator", action="store_true")
    ap.add_argument("--coords", choices=("float32", "float64"), default="float32")
    ap.add_argument("--jitter-f32", type=int, default=None, help="seed of the +-1/2 float32-ulp perturbation")
    ap.add_argument("--jitter-mode", choices=("all", "edge_safe"), default="all",
                    help="edge_safe: values equal to a grid edge are not moved (amendment 2)")
    ap.add_argument("--drop-sentinel-rows", action="store_true",
                    help="rows with a -9999 truth sentinel fail the truth selection, as in the driver (amendment 2)")
    ap.add_argument("--refine-capacity", default=None, help="N,L of the refinement classifier")
    ap.add_argument("--expectation-template", action="store_true")
    ap.add_argument("--threads", type=int, default=int(os.environ.get("SLURM_CPUS_PER_TASK", "32")))
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        print(f"refusing to overwrite {a.out}", file=sys.stderr)
        return 3
    if (a.construction == "pseudo") != (a.pseudo_seed is not None):
        print("--pseudo-seed is required for, and only for, --construction pseudo", file=sys.stderr)
        return 2
    if a.construction != "pseudo" and (a.no_background or a.expectation_template):
        print("background variants apply to --construction pseudo only", file=sys.stderr)
        return 2
    if a.construction == "asimov_same" and a.refine_capacity:
        print("the asimov construction has no refinement", file=sys.stderr)
        return 2
    if a.jitter_f32 is not None and a.coords != "float64":
        print("--jitter-f32 needs --coords float64", file=sys.stderr)
        return 2
    if a.construction == "pseudo" and (a.coords != "float32" or a.drop_sentinel_rows):
        print("the pseudo construction is the s5n experiment (float32 coordinates)", file=sys.stderr)
        return 2
    t0 = time.time()
    npz_sha, bkg_sha = s5n_pseudo.sha256_path(a.npz), s5n_pseudo.sha256_path(a.bkg)
    if npz_sha != a.expect_npz_sha256 or bkg_sha != a.expect_bkg_sha256:
        print(f"input digests {npz_sha} / {bkg_sha} differ from the expected ones", file=sys.stderr)
        return 4
    import s5c_coverage

    U, names = s5c_coverage.reported_functionals(json.loads(a.s5c_contract.read_text()))
    inputs = s5c_unfold.load_inputs(a.npz)
    bz = np.load(a.bkg, allow_pickle=True)
    bkg = {"bkg_reco": bz["bkg_reco"], "bkg_w": bz["bkg_w"], "bkg_nd": bz["bkg_nd"]}
    if json.loads(str(bz["meta"]))["npz_sha256"] != npz_sha:
        print("refusing: background dump was made against a different npz", file=sys.stderr)
        return 4
    ratio, ratio_sha = None, None
    if a.eavail_ratio is not None:
        ratio, ratio_sha = json.loads(a.eavail_ratio.read_text()), s5n_pseudo.sha256_path(a.eavail_ratio)
    n_dropped = drop_sentinel_rows(inputs) if a.drop_sentinel_rows else 0
    if a.coords == "float64":
        je = inputs["edges"] if a.jitter_mode == "edge_safe" else None
        for key in ("MCgen", "MCreco", "measured"):
            inputs[key] = jitter_coords(inputs[key], a.jitter_f32, je)
        bkg["bkg_reco"] = jitter_coords(bkg["bkg_reco"], a.jitter_f32, je)
    capacity, refine_cap = parse_pair(a.capacity), parse_pair(a.refine_capacity)
    refine_override = {"n_estimators": refine_cap[0], "num_leaves": refine_cap[1]} if refine_cap else None
    r_full = s5n_pseudo.truth_weight(a.truth, inputs, a.amplitude, ratio)
    info, x_true, ev = {}, None, {"ran": False, "reason": a.construction}
    split_key = None
    if a.construction == "pseudo":
        split_key = s5c_pseudo.split_key_for(a.pseudo_seed)
        exp, x_true, info = s5n_pseudo.build_pseudo(inputs, bkg, a.truth, a.amplitude, split_key,
                                                    a.pseudo_seed, ratio, a.no_background)
        if a.expectation_template:
            exp = expectation_template(exp, bkg, split_key)
        is_b = s5c_pseudo.half_mask(inputs["MCgen"].shape[0], split_key)
        r_unf = r_full[~is_b]
    elif a.construction == "asimov_same":
        unf_in, x_true = asimov_same(inputs, r_full)
        r_unf = r_full
    else:
        exp = s5n_pseudo.build_data(inputs, bkg)
        r_unf = np.ones(inputs["MCgen"].shape[0])
    if a.construction in ("pseudo", "data"):
        dtype = np.float32 if a.coords == "float32" else np.float64
        feat, w_ref, ev = measured_side(exp, a.estimator_seed, a.threads, refine_override, dtype)
        unf_in = unf_inputs(exp, feat, w_ref)
    t_build = time.time() - t0
    rec = Recorder(unf_in, r_unf, U, a.iters)
    xs, params, tracer = traced_unfold(unf_in, rec, a.estimator_seed, a.threads, a.iters, capacity,
                                       a.missed, a.seed_per_estimator)
    t_unf = time.time() - t0 - t_build
    arrays = dict(rec.out)
    arrays["xsec_flat"] = xs.ravel(order="C")
    if rec.xs_it5 is not None:
        arrays["xsec_it5_flat"] = rec.xs_it5.ravel(order="C")
    if x_true is not None:
        arrays["xtrue_flat"] = np.asarray(x_true).ravel(order="C")
        arrays["fn_true"] = U @ arrays["xtrue_flat"]
    meta = {
        "schema": "s5e-trace/1", "construction": a.construction, "truth": a.truth, "amplitude": a.amplitude,
        "pseudo_seed": a.pseudo_seed, "split_key": split_key, "no_background": a.no_background,
        "estimator_seed": a.estimator_seed, "iters": a.iters, "capacity": capacity, "missed": a.missed,
        "seed_per_estimator": a.seed_per_estimator, "coords": a.coords, "jitter_f32": a.jitter_f32,
        "jitter_mode": a.jitter_mode, "sentinel_rows_dropped": n_dropped,
        "refine_override": refine_override, "expectation_template": a.expectation_template,
        "threads": a.threads, "input_npz_sha256": npz_sha, "bkg_dump_sha256": bkg_sha,
        "eavail_ratio_sha256": ratio_sha, "functional_names": names, "snapshots": rec.snap,
        "trace_checks": tracer.checks, "estimator_params": params, "refinement": ev, "experiment": info,
        "code_sha256": {**s5n_pseudo.code_digests(), "s5e_trace.py": s5n_pseudo.sha256_path(Path(__file__).resolve())},
        "slurm_job": os.environ.get("SLURM_JOB_ID"), "slurm_step": os.environ.get("SLURM_STEP_ID"),
        "seconds_build": round(t_build, 3), "seconds_unfold": round(t_unf, 3),
    }
    rc = s5n_pseudo.write_product(a.out, arrays, meta)
    print(json.dumps({"out": a.out.name, "rc": rc, "seconds_unfold": meta["seconds_unfold"],
                      "checks": tracer.checks}))
    return rc


if __name__ == "__main__":
    sys.exit(main())
