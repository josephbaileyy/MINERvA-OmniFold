#!/usr/bin/env python3
"""s5p Stage 2: matched resampling / rounding-perturbation products for one estimator configuration.

Contract ``stages.2_construction_questions.items.numerical_bootstrap_overlap`` of
``docs/orchestration/state/s5p/contract.json`` (frozen design in contract amendment 2). One invocation
builds ONE base construction -- the real data (``--construction data``: ``s5n_pseudo.build_data``) or one
background-inclusive repeated experiment (``--construction pseudo``: ``s5n_pseudo.build_pseudo``) -- and
unfolds it for each requested ``(bootstrap_seed, jitter_seed)`` pair:

* ``bootstrap_seed``: one replica of the s5n repaired bootstrap (``s5n_pseudo.bootstrap_replica``:
  per-event Poisson(k) on observed rows, Poisson(1) on unfolding-MC and template rows; the refinement is
  refit on the replica), or ``-`` for the base construction itself;
* ``jitter_seed``: one edge-safe rounding-scale perturbation of every input coordinate (MC truth, MC reco,
  observed and background-template coordinates), each value moved uniformly within +-1/2 of its float32
  ulp by ``s5e_trace.jitter_coords`` with values on a grid edge never moved; or ``-`` for none.

The estimator is the production one: the measured side is ``s5e_trace.measured_side`` (the driver's
``refine_stay_positive`` through ``s5n_pseudo.refine``, which verifies every refinement parameter it
built) and the unfold is ``s5c_unfold.unfold`` (``omnifold_nn_core.omnifold_loop`` with the F2
parameters, verified by its own factory check). A jittered product runs in float64 coordinates so the
sub-float32 perturbation survives; an unjittered product runs in the production float32 coordinates, so
it reproduces the s5n/s5e products bitwise. The configuration (``--config``) is R (s5e amendment 3) plus
an optional OmniFold capacity and iteration count, both recorded and verified.

Grid membership is preserved and CHECKED: a jittered product whose fine-grid cell assignment of any
truth, reco, observed or template row differs from the unperturbed one is refused (exit 5).

MEASURES: the numerical (rounding-scale) sensitivity of one configuration and its overlap with the
refit-per-replica bootstrap. CANNOT AUTHORIZE: an interval, a covariance, a numerical-component
definition or any stability verdict by itself (the frozen analysis of amendment 2 does that).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from contextlib import contextmanager
from pathlib import Path

import numpy as np

_ND = Path(__file__).resolve().parent
if str(_ND) not in sys.path:
    sys.path.insert(0, str(_ND))
import s5c_pseudo  # noqa: E402
import s5c_unfold  # noqa: E402
import s5e_candidate  # noqa: E402
import s5e_trace  # noqa: E402
import s5n_pseudo  # noqa: E402

COORD_KEYS = ("MCgen", "MCreco", "measured")


def parse_pairs(text: str) -> list[tuple[int | None, int | None]]:
    """``"-:-,1:-,1:101"`` -> [(None, None), (1, None), (1, 101)]; bootstrap first, jitter second."""
    out = []
    for item in text.split(","):
        b, j = item.split(":")
        out.append((None if b == "-" else int(b), None if j == "-" else int(j)))
    if len(set(out)) != len(out):
        raise ValueError("duplicate (bootstrap, jitter) pair")
    return out


def product_name(tag: str, b: int | None, j: int | None, seed: int | None = None) -> str:
    s = "" if seed is None else f"_s{seed}"
    return f"{tag}{s}_b{'-' if b is None else b}_j{'-' if j is None else j}.npz"


def cell_membership(inputs: dict, bkg_reco: np.ndarray) -> dict:
    edges = inputs["edges"]
    return {k: s5e_trace.flat_index(np.asarray(inputs[k], np.float64), edges) for k in COORD_KEYS} | {
        "bkg_reco": s5e_trace.flat_index(np.asarray(bkg_reco, np.float64), edges)}


def jittered(inputs: dict, bkg: dict, seed: int | None) -> tuple[dict, dict]:
    """float64 copies; with a seed, the edge-safe +-1/2 float32-ulp perturbation of every coordinate."""
    edges = inputs["edges"]
    ji = dict(inputs)
    for k in COORD_KEYS:
        ji[k] = s5e_trace.jitter_coords(inputs[k], seed, edges)
    jb = dict(bkg)
    jb["bkg_reco"] = s5e_trace.jitter_coords(bkg["bkg_reco"], seed, edges)
    return ji, jb


@contextmanager
def omnifold_capacity(capacity: tuple[int, int] | None):
    """Add n_estimators/num_leaves to the deterministic configuration's parameters for this process;
    ``s5c_unfold.unfold`` then verifies that every estimator it built carries them."""
    if capacity is None:
        yield
        return
    original = s5c_unfold.config_params

    def params(config, threads):
        out = original(config, threads)
        if config == "deterministic":
            out = {**out, "n_estimators": int(capacity[0]), "num_leaves": int(capacity[1])}
        return out

    s5c_unfold.config_params = params
    try:
        yield
    finally:
        s5c_unfold.config_params = original


def unfold_one(exp: dict, dtype, estimator_seed: int, threads: int, iters: int, unfold_fn=None) -> tuple[np.ndarray, dict]:
    feat, w_ref, ev = s5e_trace.measured_side(exp, estimator_seed, threads, None, dtype)
    unf_in = s5e_trace.unf_inputs(exp, feat, w_ref)
    xs, params = (unfold_fn or s5c_unfold.unfold)(unf_in, "deterministic", estimator_seed, threads, iters)
    return xs, {"refinement": ev, "estimator_params": params}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--npz", type=Path, required=True)
    ap.add_argument("--bkg", type=Path, required=True)
    ap.add_argument("--expect-npz-sha256", required=True)
    ap.add_argument("--expect-bkg-sha256", required=True)
    ap.add_argument("--config", choices=("R",), default="R", help="the refinement candidate (s5e amendment 3)")
    ap.add_argument("--capacity", default=None, help="N,L: n_estimators,num_leaves of the three OmniFold estimators")
    ap.add_argument("--iters", type=int, default=5)
    ap.add_argument("--construction", choices=("data", "pseudo"), required=True)
    ap.add_argument("--truth", default="nominal")
    ap.add_argument("--amplitude", type=float, default=0.0)
    ap.add_argument("--eavail-ratio", type=Path, default=None)
    ap.add_argument("--pseudo-seed", type=int, default=None)
    ap.add_argument("--pseudo-seeds", default=None, help="first:last; the pairs are applied to each experiment")
    ap.add_argument("--fixed-split-seed", type=int, default=None,
                    help="DEVELOPMENT DIAGNOSTIC: every experiment uses the MC split key of this seed")
    ap.add_argument("--pairs", required=True, help="bootstrap:jitter[,...]; '-' = none")
    ap.add_argument("--estimator-seed", type=int, default=42)
    ap.add_argument("--threads", type=int, default=int(os.environ.get("SLURM_CPUS_PER_TASK", "32")))
    ap.add_argument("--tag", required=True)
    ap.add_argument("--out", type=Path, required=True, help="output directory")
    a = ap.parse_args(argv)
    if (a.construction == "pseudo") != ((a.pseudo_seed is not None) or (a.pseudo_seeds is not None)):
        print("--pseudo-seed(s) is required for, and only for, --construction pseudo", file=sys.stderr)
        return 2
    if a.pseudo_seed is not None and a.pseudo_seeds is not None:
        print("give one of --pseudo-seed and --pseudo-seeds", file=sys.stderr)
        return 2
    if a.fixed_split_seed is not None and a.construction != "pseudo":
        print("--fixed-split-seed applies to pseudo experiments only", file=sys.stderr)
        return 2
    pairs = parse_pairs(a.pairs)
    if a.pseudo_seeds is not None:
        first, last = (int(v) for v in a.pseudo_seeds.split(":"))
        seeds = list(range(first, last + 1))
    else:
        seeds = [a.pseudo_seed]
    capacity = s5e_trace.parse_pair(a.capacity)
    s5e_candidate.install(a.config)
    t0 = time.time()
    npz_sha, bkg_sha = s5n_pseudo.sha256_path(a.npz), s5n_pseudo.sha256_path(a.bkg)
    if npz_sha != a.expect_npz_sha256 or bkg_sha != a.expect_bkg_sha256:
        print(f"input digests {npz_sha} / {bkg_sha} differ from the expected ones", file=sys.stderr)
        return 4
    inputs = s5c_unfold.load_inputs(a.npz)
    bz = np.load(a.bkg, allow_pickle=True)
    bkg = {"bkg_reco": bz["bkg_reco"], "bkg_w": bz["bkg_w"], "bkg_nd": bz["bkg_nd"]}
    if json.loads(str(bz["meta"]))["npz_sha256"] != npz_sha:
        print("refusing: background dump was made against a different npz", file=sys.stderr)
        return 4
    ratio, ratio_sha = None, None
    if a.eavail_ratio is not None:
        ratio, ratio_sha = json.loads(a.eavail_ratio.read_text()), s5n_pseudo.sha256_path(a.eavail_ratio)
    base_cells = cell_membership(inputs, bkg["bkg_reco"])
    a.out.mkdir(parents=True, exist_ok=True)
    status = 0
    work = [(s, b, j) for s in seeds for (b, j) in pairs]
    for seed, b, j in work:
        target = a.out / product_name(a.tag, b, j, seed if a.pseudo_seeds is not None else None)
        if target.exists():
            continue
        t1 = time.time()
        if j is None:
            ji, jb, dtype = inputs, bkg, np.float32
        else:
            ji, jb = jittered(inputs, bkg, j)
            dtype = np.float64
            moved = {k: int((v != base_cells[k]).sum()) for k, v in cell_membership(ji, jb["bkg_reco"]).items()}
            if any(moved.values()):
                print(f"refusing: jitter {j} changed grid membership {moved}", file=sys.stderr)
                return 5
        x_true, info, split_key = None, {}, None
        if a.construction == "data":
            exp = s5n_pseudo.build_data(ji, jb)
            info = {"n_observed": int(exp["obs"].shape[0]), "n_template": int(exp["tmpl"].shape[0])}
        else:
            split_key = s5c_pseudo.split_key_for(seed if a.fixed_split_seed is None else a.fixed_split_seed)
            exp, x_true, info = s5n_pseudo.build_pseudo(ji, jb, a.truth, a.amplitude, split_key, seed, ratio)
        if b is not None:
            exp = s5n_pseudo.bootstrap_replica(exp, b)
        with omnifold_capacity(capacity):
            xs, ev = unfold_one(exp, dtype, a.estimator_seed, a.threads, a.iters)
        meta = {"schema": "s5p-numerics/1", "config": a.config, "capacity": capacity, "iters": a.iters,
                "construction": a.construction, "truth": a.truth, "amplitude": a.amplitude,
                "pseudo_seed": seed, "split_key": split_key, "fixed_split_seed": a.fixed_split_seed,
                "bootstrap_seed": b, "jitter_seed": j,
                "jitter_mode": "edge_safe", "coords": "float64" if j is not None else "float32",
                "estimator_seed": a.estimator_seed, "threads": a.threads, "input_npz_sha256": npz_sha,
                "bkg_dump_sha256": bkg_sha, "eavail_ratio_sha256": ratio_sha, "experiment": info, **ev,
                "code_sha256": {**s5n_pseudo.code_digests(), "s5e_trace.py": s5n_pseudo.sha256_path(_ND / "s5e_trace.py"),
                                "s5p_numerics.py": s5n_pseudo.sha256_path(Path(__file__).resolve())},
                "slurm_job": os.environ.get("SLURM_JOB_ID"), "slurm_step": os.environ.get("SLURM_STEP_ID"),
                "seconds_load": round(t1 - t0, 3), "seconds_unfold": round(time.time() - t1, 3)}
        arrays = {"xsec_flat": xs.ravel(order="C"), "shape": np.array(xs.shape)}
        if x_true is not None:
            arrays["xtrue_flat"] = np.asarray(x_true).ravel(order="C")
        rc = s5n_pseudo.write_product(target, arrays, meta)
        status |= rc
        print(json.dumps({"out": target.name, "rc": rc, "seconds_unfold": meta["seconds_unfold"]}))
        t0 = time.time()
    return status


if __name__ == "__main__":
    sys.exit(main())
