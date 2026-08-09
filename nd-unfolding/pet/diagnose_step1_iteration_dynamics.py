#!/usr/bin/env python3
"""Controlled full-input arms for the post-feedback Step-1 collapse.

This is a diagnostic wrapper around the publication driver, not a replacement estimator.  It changes
only two engine behaviours in a subclass, leaving the hash-bound shared engine untouched:

* ``warm_fresh_split`` keeps the trained Step-1 model but rebuilds its shuffled feature/split cache;
* ``cold_fixed_split`` resets Step 1 to the same untrained template after iteration 0;
* ``cold_fresh_split`` applies both interventions.

The completed nominal is the fourth factorial cell (warm model, fixed split).  Every arm still consumes
the exact Gate-2 target, schema, seeds, batch size, epochs, and Step-2 implementation through
``train_fullevent_nominal.py``.  Outputs live in diagnostic-only, arm/job-specific namespaces.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import tempfile

import numpy as np


ARMS = ("warm_fresh_split", "cold_fixed_split", "cold_fresh_split")
SCHEMA = "pet-step1-iteration-dynamics-arm-v1"


def array_sha256(arrays) -> str:
    h = hashlib.sha256()
    for a in arrays:
        x = np.ascontiguousarray(a)
        h.update(str(x.dtype).encode())
        h.update(str(x.shape).encode())
        h.update(memoryview(x).cast("B"))
    return h.hexdigest()


def step1_metrics(push_before, pull_after, w_reco, pass_reco, R, cap):
    """Pure telemetry used by the runtime subclass and unit tests."""
    push_before = np.asarray(push_before, dtype=np.float64)
    pull_after = np.asarray(pull_after, dtype=np.float64)
    w_reco = np.asarray(w_reco, dtype=np.float64)
    mask = np.asarray(pass_reco).astype(bool)
    if not (push_before.shape == pull_after.shape == w_reco.shape == mask.shape):
        raise ValueError("Step-1 telemetry arrays are not row-aligned")
    if not mask.any() or not np.isfinite(w_reco[mask]).all() or w_reco[mask].sum() <= 0:
        raise ValueError("Step-1 telemetry has no finite positive reco support")
    increment = np.ones_like(pull_after)
    np.divide(pull_after, push_before, out=increment, where=push_before != 0)
    if (push_before[mask] == 0).any() or not np.isfinite(increment[mask]).all():
        raise ValueError("Step-1 increment is undefined/non-finite on reco support")
    denom = float(w_reco[mask].sum())
    wmean = lambda x: float((np.asarray(x)[mask] * w_reco[mask]).sum() / denom)
    base = wmean(push_before)
    achieved = wmean(increment)
    required = float(R) / base
    vals = increment[mask]
    ww = w_reco[mask]
    return {
        "push_prev_mean_w_reco": base,
        "r1_mean_w_reco": achieved,
        "r1_required_mean": required,
        "r1_achieved_over_required": achieved / required,
        "correction_sign_is_wrong": bool((achieved - 1.0) * (required - 1.0) < 0),
        "pull_mean_w_reco": wmean(pull_after),
        "r1_weight_mass_below_one": float(ww[vals < 1.0].sum() / denom),
        "r1_cap_saturated_frac": float(
            ww[np.abs(np.log(np.clip(vals, 1e-300, None))) >= 0.999 * cap].sum() / denom
        ),
        "r1_percentiles_unweighted": {
            str(p): float(np.percentile(vals, p)) for p in (1, 5, 25, 50, 75, 95, 99)
        },
    }


def atomic_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as fh:
            json.dump(payload, fh, indent=2, sort_keys=True)
            fh.write("\n")
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--arm", required=True, choices=ARMS)
    ap.add_argument("--result-json", required=True)
    ap.add_argument("--out", required=True, help="diagnostic weights artifact passed to the canonical driver")
    ap.add_argument("--inputs", required=True)
    ap.add_argument("--gate3-manifest", required=True)
    ap.add_argument("--target-npy")
    ap.add_argument("--target-receipt")
    args = ap.parse_args(argv)

    # Lazy imports preserve login-safe --help and pure-function tests.
    import tensorflow as tf
    import omnifold
    import omnifold.omnifold as engine
    from omnifold import MultiFold as BaseMultiFold
    import train_fullevent_nominal as nominal

    reset_each_iteration = args.arm.startswith("cold_")
    fresh_split_each_iteration = args.arm.endswith("fresh_split")
    instances = []

    class DynamicsMultiFold(BaseMultiFold):
        def __init__(self, *a, **kw):
            super().__init__(*a, **kw)
            self.dynamics_rows = []
            self.split_records = []
            self.reset_records = []
            self._diag_iteration = None
            instances.append(self)

        def cache(self, label, weights, stepn, cached, NTRAIN):
            requested_cached = bool(cached)
            effective_cached = requested_cached
            if stepn == 1 and fresh_split_each_iteration and requested_cached:
                effective_cached = False
            out = super().cache(label, weights, stepn, effective_cached, NTRAIN)
            if stepn == 1:
                self.split_records.append({
                    "iteration": int(self._diag_iteration),
                    "requested_cached": requested_cached,
                    "effective_cached": effective_cached,
                    "index_sha256": array_sha256([np.asarray(self.idx_1)]),
                })
            return out

        def RunModel(self, labels, weights, iteration, model, stepn, NTRAIN=1000, cached=False):
            self._diag_iteration = int(iteration)
            if stepn == 1 and iteration > self.start and reset_each_iteration:
                if len(self.step1_models) != 1:
                    raise RuntimeError(f"cold Step-1 arm expected one model, found {len(self.step1_models)}")
                fresh = tf.keras.models.clone_model(self.model1)
                fresh.set_weights(self.model1.get_weights())
                self.step1_models[0] = fresh
                self.reset_records.append({
                    "iteration": int(iteration),
                    "template_weight_sha256": array_sha256(fresh.get_weights()),
                })
            return super().RunModel(labels, weights, iteration, model, stepn, NTRAIN, cached)

        def RunStep1(self, i):
            before = np.asarray(self.weights_push, dtype=np.float64).copy()
            super().RunStep1(i)
            data_mask = np.asarray(self.data.pass_reco).astype(bool)
            mc_mask = np.asarray(self.mc.pass_reco).astype(bool)
            row = step1_metrics(
                before, self.weights_pull, self.mc_weight_reco, self.mc.pass_reco,
                float(np.asarray(self.data.weight)[data_mask].sum() /
                      np.asarray(self.mc_weight_reco)[mc_mask].sum()),
                float(engine.REWEIGHT_LOGIT_CAP),
            )
            row["iteration"] = int(i)
            row["trained_model_weight_sha256"] = array_sha256(self.step1_models[0].get_weights())
            self.dynamics_rows.append(row)

        def RunStep2(self, i):
            super().RunStep2(i)
            row = self.dynamics_rows[-1]
            w = np.asarray(self.mc_weight_reco, dtype=np.float64)
            m = np.asarray(self.mc.pass_reco).astype(bool)
            row["push_mean_w_reco"] = float(
                (np.asarray(self.weights_push)[m] * w[m]).sum() / w[m].sum()
            )

    # Patch only this process. The tracked shared engine is neither edited nor reissued.
    omnifold.MultiFold = DynamicsMultiFold
    driver_argv = [
        "--inputs", args.inputs,
        "--out", args.out,
        "--tag", "nominal",
        "--gate3-manifest", args.gate3_manifest,
    ]
    if args.target_npy:
        driver_argv += ["--target-npy", args.target_npy]
    if args.target_receipt:
        driver_argv += ["--target-receipt", args.target_receipt]
    rc = nominal.main(driver_argv)
    if rc != 0 or len(instances) != 1:
        raise SystemExit(f"canonical driver rc={rc}; diagnostic engine instances={len(instances)}")
    inst = instances[0]
    if len(inst.dynamics_rows) != nominal.NOMINAL_SEED_POLICY["niter"]:
        raise SystemExit("diagnostic did not record exactly one row per frozen iteration")
    if len(inst.split_records) != nominal.NOMINAL_SEED_POLICY["niter"]:
        raise SystemExit("diagnostic did not record exactly one Step-1 split per iteration")
    expected_resets = nominal.NOMINAL_SEED_POLICY["niter"] - 1 if reset_each_iteration else 0
    if len(inst.reset_records) != expected_resets:
        raise SystemExit(f"diagnostic reset count {len(inst.reset_records)} != {expected_resets}")

    out = Path(args.out).resolve()
    result = Path(args.result_json).resolve()
    payload = {
        "schema": SCHEMA,
        "status": "COMPLETE",
        "arm": args.arm,
        "publication_candidate": False,
        "interventions": {
            "step1_model_reset_after_iteration0": reset_each_iteration,
            "step1_fresh_split_after_iteration0": fresh_split_each_iteration,
            "step2_changed": False,
            "shared_engine_edited": False,
        },
        "frozen_policy": nominal.NOMINAL_SEED_POLICY,
        "driver_output": str(out),
        "driver_output_sha256": hashlib.sha256(out.read_bytes()).hexdigest(),
        "rows": inst.dynamics_rows,
        "split_records": inst.split_records,
        "reset_records": inst.reset_records,
        "code": {
            "wrapper": str(Path(__file__).resolve()),
            "wrapper_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "driver": str(Path(nominal.__file__).resolve()),
            "driver_sha256": hashlib.sha256(Path(nominal.__file__).read_bytes()).hexdigest(),
            "engine": str(Path(engine.__file__).resolve()),
            "engine_sha256": hashlib.sha256(Path(engine.__file__).read_bytes()).hexdigest(),
        },
        "interpretation_contract": {
            "warm_fresh_split_repairs": "fixed split/order is implicated",
            "cold_fixed_split_repairs": "warm-started Step-1 state is implicated",
            "only_cold_fresh_split_repairs": "warm-start and split reuse interact",
            "no_arm_repairs": "intrinsic push feedback / representation-tail contraction remains",
            "repair_definition": "iteration 2 Step-1 correction has correct sign and achieved_over_required >= 0.90",
        },
    }
    for row in payload["rows"]:
        if not all(math.isfinite(float(row[k])) for k in (
            "push_prev_mean_w_reco", "r1_mean_w_reco", "r1_required_mean",
            "r1_achieved_over_required", "push_mean_w_reco"
        )):
            raise SystemExit("non-finite diagnostic telemetry")
    atomic_json(result, payload)
    print(json.dumps({"diagnostic": "COMPLETE", "arm": args.arm, "result": str(result),
                      "rows": payload["rows"]}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
