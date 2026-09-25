#!/usr/bin/env python3
"""One scalar-5D OmniFold unfold for the s5c campaign, from the ROOT-free npz inputs.

Authority: docs/orchestration/AUTHORIZATION-20260924-scalar5d-campaign-activation.md (plan §§2, 6).
The loop is the production ``omnifold_nn_core.omnifold_loop`` and the cross-section extraction is
``xsec_nd.extract_cross_section_nd``, exactly as ``bootstrap_nd.py`` calls them; only the LightGBM
parameters differ between configurations, and nothing in the production modules is edited.

Estimator configurations (candidate families of the s5c contract):

``production``
    ``omnifold_nn_core.make_estimators`` unchanged: ``random_state=seed`` and LightGBM defaults
    otherwise.  With no bagging or feature subsampling, the seed's main reach is LightGBM's random
    ``bin_construct_sample_cnt`` (default 200,000) row sample that sets the histogram bin edges.
``full_binning``
    ``production`` plus ``bin_construct_sample_cnt`` above any row count, so bin edges come from
    every row and not from a seed-chosen sample.
``deterministic``
    ``full_binning`` plus ``deterministic=True``, ``force_row_wise=True`` and a fixed
    ``num_threads`` (the knobs of ``z_reproducibility.Z_REPRO_KNOBS``, with the thread count set to
    the allocation's instead of 1, which is unaffordable on 32.85M rows).

``--permute-seed`` permutes the row order of the MC and data arrays consistently.  In exact
arithmetic the result is invariant, so any movement measures sensitivity to an irrelevant choice.

The factory patch is PROVEN to reach the loop: every estimator the loop builds is recorded and the
run refuses to write its product unless exactly one factory call happened and each of its three
estimators carries the configuration's parameters.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import time
from contextlib import contextmanager
from pathlib import Path

import numpy as np

_ND = str(Path(__file__).resolve().parent)
if _ND not in sys.path:
    sys.path.insert(0, _ND)
import omnifold_nn_core as onc  # noqa: E402
from xsec_nd import extract_cross_section_nd, total_xsec  # noqa: E402

CONFIGS = ("production", "full_binning", "deterministic")
ALL_ROWS = 2**31 - 1  # LightGBM uses min(bin_construct_sample_cnt, num_data)


def config_params(config: str, threads: int) -> dict:
    if config == "production":
        return {}
    extra = {"bin_construct_sample_cnt": ALL_ROWS}
    if config == "deterministic":
        extra.update(deterministic=True, force_row_wise=True, num_threads=int(threads))
    return extra


@contextmanager
def estimator_config(extra: dict, record: list):
    """Rebind ``omnifold_nn_core.make_estimators`` for the duration of one loop.

    ``omnifold_loop`` resolves ``make_estimators`` in its module's globals at call time, so the
    rebinding is what it calls; ``record`` receives every estimator's parameters as evidence.
    """
    original = onc.make_estimators

    def factory(kind, nvars, seed=None):
        estimators = original(kind, nvars, seed=seed)
        for est in estimators:
            if extra:
                est.set_params(**extra)
        record.append([est.get_params() for est in estimators])
        return estimators

    onc.make_estimators = factory
    try:
        yield
    finally:
        onc.make_estimators = original


def sha256_path(path: Path, chunk: int = 1 << 24) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            block = fh.read(chunk)
            if not block:
                return h.hexdigest()
            h.update(block)


def load_inputs(npz_path: Path) -> dict:
    d = np.load(npz_path, allow_pickle=True)
    keys = ("MCgen", "MCreco", "measured", "pass_reco", "pass_truth", "w_truth", "w_reco",
            "measured_weights", "denom_nd", "flux", "data_pot", "n_nucleons", "nedges")
    out = {k: d[k] for k in keys}
    out["edges"] = [np.asarray(d[f"edges_{i}"], float) for i in range(int(d["nedges"]))]
    return out


def permute(inputs: dict, seed: int) -> dict:
    rng = np.random.default_rng(seed)
    n_mc = inputs["MCgen"].shape[0]
    n_data = inputs["measured"].shape[0]
    pm, pd = rng.permutation(n_mc), rng.permutation(n_data)
    out = dict(inputs)
    for key in ("MCgen", "MCreco", "pass_reco", "pass_truth", "w_truth", "w_reco"):
        out[key] = inputs[key][pm]
    for key in ("measured", "measured_weights"):
        out[key] = inputs[key][pd]
    return out


def unfold(inputs: dict, config: str, seed: int, threads: int, iters: int) -> tuple[np.ndarray, list]:
    record: list = []
    extra = config_params(config, threads)
    d = inputs
    with estimator_config(extra, record):
        _, wpush = onc.omnifold_loop(
            d["MCgen"], d["MCreco"], d["measured"], d["pass_reco"], d["pass_truth"],
            np.ones(len(d["measured"]), bool), iters, kind="lgbm",
            MCgen_weights=d["w_truth"], MCreco_weights=d["w_reco"],
            measured_weights=d["measured_weights"], seed=seed, verbose=False)
    if len(record) != 1:
        raise RuntimeError(f"expected one estimator-factory call, saw {len(record)}")
    for params in record[0]:
        for key, value in extra.items():
            if params.get(key) != value:
                raise RuntimeError(f"estimator parameter {key}={params.get(key)!r}, wanted {value!r}")
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
    return xs, record[0]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--npz", type=Path, required=True)
    ap.add_argument("--config", choices=CONFIGS, required=True)
    ap.add_argument("--estimator-seed", type=int, required=True)
    ap.add_argument("--permute-seed", type=int, default=None)
    ap.add_argument("--threads", type=int, default=int(os.environ.get("SLURM_CPUS_PER_TASK", "32")))
    ap.add_argument("--iters", type=int, default=5)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--expect-npz-sha256", default=None)
    a = ap.parse_args(argv)

    if a.out.exists():
        print(f"refusing to overwrite {a.out}", file=sys.stderr)
        return 3
    t0 = time.time()
    npz_sha = sha256_path(a.npz)
    if a.expect_npz_sha256 and npz_sha != a.expect_npz_sha256:
        print(f"input {a.npz} sha256 {npz_sha} != expected {a.expect_npz_sha256}", file=sys.stderr)
        return 4
    inputs = load_inputs(a.npz)
    if a.permute_seed is not None:
        inputs = permute(inputs, a.permute_seed)
    t1 = time.time()
    xs, params = unfold(inputs, a.config, a.estimator_seed, a.threads, a.iters)
    t2 = time.time()
    import lightgbm

    meta = {
        "schema": "s5c-unfold/1",
        "config": a.config,
        "estimator_seed": a.estimator_seed,
        "permute_seed": a.permute_seed,
        "threads": a.threads,
        "iters": a.iters,
        "extra_params": config_params(a.config, a.threads),
        "estimator_params": params,
        "input_npz": str(a.npz),
        "input_npz_sha256": npz_sha,
        "code_sha256": {
            "s5c_unfold.py": sha256_path(Path(__file__).resolve()),
            "omnifold_nn_core.py": sha256_path(Path(onc.__file__).resolve()),
        },
        "lightgbm": lightgbm.__version__,
        "numpy": np.__version__,
        "host": platform.node(),
        "slurm_job": os.environ.get("SLURM_JOB_ID"),
        "slurm_array_task": os.environ.get("SLURM_ARRAY_TASK_ID"),
        "seconds_load": round(t1 - t0, 3),
        "seconds_unfold": round(t2 - t1, 3),
        "total_xsec": float(total_xsec(xs, inputs["edges"])),
    }
    tmp = a.out.with_name(a.out.name + ".partial.npz")
    np.savez_compressed(tmp, xsec_flat=xs.ravel(order="C"), shape=np.array(xs.shape),
                        meta=json.dumps(meta, default=str))
    os.replace(tmp, a.out)
    print(json.dumps({k: meta[k] for k in ("config", "estimator_seed", "permute_seed",
                                            "seconds_unfold", "total_xsec")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
