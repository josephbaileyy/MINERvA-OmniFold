#!/usr/bin/env python3
"""Run an unmodified production arm under an s5c estimator configuration.

    s5c_with_estimator.py --config deterministic --threads 32 --evidence E.json -- <script.py> [args...]

The production scripts are not edited (several are hash-bound by receipts). Instead, before the
target runs (``runpy.run_path`` with its own ``sys.argv``), this process:

* rebinds ``omnifold_nn_core.make_estimators`` so every estimator ``omnifold_loop`` builds carries
  the configuration's parameters (the npz/bank arms: bootstrap, seed-split, sweep, throws); and
* wraps ``omnifold.OmniFold_helper_functions.omnifold`` (``unbinned_unfolding/python``, the driver's backend) so its three
  LightGBM parameter dicts are merged with the same parameters (the driver arms: detector, lateral,
  central).

EVIDENCE, NOT TRUST: every factory call and driver call is recorded with the estimators' final
parameters and written to ``--evidence``; the run exits 7 (after the target finishes) if no call
was intercepted or any intercepted estimator lacks a configuration parameter -- a configuration
that silently did not reach the arm must not produce a product that claims it.
``production`` is accepted for symmetry and patches nothing (it still records the calls).
"""
from __future__ import annotations

import argparse
import json
import runpy
import sys
from pathlib import Path

_ND = Path(__file__).resolve().parent
for p in (str(_ND), str(_ND.parent / "unbinned_unfolding" / "python")):
    if p not in sys.path:
        sys.path.insert(1, p)

import s5c_unfold  # noqa: E402  (config_params: the one definition of each configuration)


def permuted(fn, seed: int, record: list, site: str):
    """Wrap an OmniFold loop so it sees its MC and data rows in a seeded random order.

    Both backends take (MCgen, MCreco, measured, pass_reco, pass_truth, meas_pass_reco, iters, ...)
    with MCgen_weights / MCreco_weights / measured_weights as keywords, and return two weight arrays
    over the pass-truth MC rows. Inputs are permuted consistently and the returned weights are put
    back in the original row order, so in exact arithmetic the caller's result is unchanged: any
    movement measures the estimator's sensitivity to an irrelevant choice.
    """
    import numpy as np

    def wrapped(MCgen, MCreco, measured, pass_reco, pass_truth, meas_pass_reco, *args, **kwargs):
        rng = np.random.default_rng(seed)
        n_mc, n_d = len(MCgen), len(measured)
        pm, pd = rng.permutation(n_mc), rng.permutation(n_d)
        pt = np.asarray(pass_truth)
        for key in ("MCgen_weights", "MCreco_weights"):
            if kwargs.get(key) is not None:
                kwargs[key] = np.asarray(kwargs[key])[pm]
        if kwargs.get("measured_weights") is not None:
            kwargs["measured_weights"] = np.asarray(kwargs["measured_weights"])[pd]
        out = fn(np.asarray(MCgen)[pm], np.asarray(MCreco)[pm], np.asarray(measured)[pd],
                 np.asarray(pass_reco)[pm], pt[pm], np.asarray(meas_pass_reco)[pd], *args, **kwargs)
        selected = np.flatnonzero(pt)
        position = np.empty(n_mc, dtype=np.int64)
        position[selected] = np.arange(selected.size)
        where = position[pm[pt[pm]]]  # original selected-row position of each permuted selected row
        restored = []
        for w in out:
            back = np.empty_like(np.asarray(w))
            back[where] = w
            restored.append(back)
        record.append({"site": site, "kind": "permutation", "seed": seed, "n_mc": n_mc, "n_data": n_d})
        return tuple(restored)

    return wrapped


def install(extra: dict, record: list, permute_seed: int | None = None) -> None:
    import omnifold_nn_core as onc

    if permute_seed is not None:
        onc.omnifold_loop = permuted(onc.omnifold_loop, permute_seed, record, "omnifold_nn_core.omnifold_loop")

    original_factory = onc.make_estimators

    def factory(kind, nvars, seed=None):
        estimators = original_factory(kind, nvars, seed=seed)
        for est in estimators:
            if extra and hasattr(est, "set_params"):
                est.set_params(**extra)
        record.append({"site": "omnifold_nn_core.make_estimators", "kind": kind,
                       "params": [est.get_params() if hasattr(est, "get_params") else None
                                  for est in estimators]})
        return estimators

    onc.make_estimators = factory

    try:
        from omnifold import OmniFold_helper_functions as ohf  # the driver's own import
    except ImportError:
        return
    original_omnifold = ohf.omnifold  # a plain function on the class, called as ohf.omnifold(...)

    def wrapped(*args, **kwargs):
        if kwargs.get("estimator", "lgbm") == "lgbm":
            for key in ("classifier1_params", "classifier2_params", "regressor_params"):
                kwargs[key] = {**(kwargs.get(key) or {}), **extra}
            record.append({"site": "omnifold.omnifold", "kind": "lgbm",
                           "params": [kwargs[k] for k in ("classifier1_params", "classifier2_params",
                                                          "regressor_params")]})
        else:
            record.append({"site": "omnifold.omnifold", "kind": kwargs.get("estimator"), "params": None})
        return original_omnifold(*args, **kwargs)

    ohf.omnifold = wrapped if permute_seed is None else permuted(
        wrapped, permute_seed, record, "omnifold.OmniFold_helper_functions.omnifold")


def verify(extra: dict, record: list) -> list[str]:
    problems = []
    if not record:
        problems.append("no estimator construction was intercepted")
    for call in record:
        if call["kind"] == "permutation":
            continue
        if call["kind"] != "lgbm":
            problems.append(f"{call['site']}: estimator kind {call['kind']!r} is not lgbm")
            continue
        for params in call["params"]:
            for key, value in extra.items():
                if params is None or params.get(key) != value:
                    problems.append(f"{call['site']}: {key}={None if params is None else params.get(key)!r}")
    return problems


def main() -> int:
    if "--" not in sys.argv:
        print("usage: s5c_with_estimator.py --config C [--threads N] --evidence E -- script.py [args]",
              file=sys.stderr)
        return 2
    cut = sys.argv.index("--")
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", choices=s5c_unfold.CONFIGS, required=True)
    ap.add_argument("--threads", type=int, default=32)
    ap.add_argument("--evidence", type=Path, required=True)
    ap.add_argument("--permute-seed", type=int, default=None,
                    help="present the loop's MC and data rows in a seeded random order (G-stab-F2 probe)")
    a = ap.parse_args(sys.argv[1:cut])
    target = sys.argv[cut + 1:]
    if not target:
        return 2
    extra = s5c_unfold.config_params(a.config, a.threads)
    record: list = []
    install(extra, record, a.permute_seed)
    sys.argv = target
    exit_code = 0
    try:
        runpy.run_path(target[0], run_name="__main__")
    except SystemExit as exc:
        exit_code = exc.code if isinstance(exc.code, int) else (0 if exc.code is None else 1)
    problems = verify(extra, record)
    if a.permute_seed is not None and not any(c.get("kind") == "permutation" for c in record):
        problems.append("--permute-seed given but no loop call was permuted")
    a.evidence.write_text(json.dumps({"schema": "s5c-estimator-evidence/1", "config": a.config,
                                      "permute_seed": a.permute_seed,
                                      "extra": extra, "target": target, "target_exit": exit_code,
                                      "calls": record, "problems": problems}, indent=1, default=str))
    if exit_code not in (0, 2):  # a real failure of the target passes through
        return exit_code
    return 7 if problems else exit_code  # 2 is z_build's documented success code


if __name__ == "__main__":
    sys.exit(main())
