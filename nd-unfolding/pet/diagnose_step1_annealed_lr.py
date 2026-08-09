#!/usr/bin/env python3
"""Full-input control that makes the engine's intended post-iteration LR anneal effective.

The shared engine calls ``CompileModels(fixed=True)`` after an iteration, but ``RunModel`` recompiles
the trained clone at full LR immediately before every fit.  This diagnostic subclass forces that
fit-time compile to ``fixed=True`` for iterations > 0, for both OmniFold steps.  Everything else is
the completed warm-model/fixed-split nominal configuration.  The shared engine is not edited.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np

import diagnose_step1_iteration_dynamics as diag


ARM = "warm_fixed_annealed_lr"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--result-json", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--inputs", required=True)
    ap.add_argument("--gate3-manifest", required=True)
    ap.add_argument("--target-npy")
    ap.add_argument("--target-receipt")
    args = ap.parse_args(argv)

    import tensorflow as tf
    import omnifold
    import omnifold.omnifold as engine
    from omnifold import MultiFold as BaseMultiFold
    import train_fullevent_nominal as nominal

    instances = []

    class AnnealedMultiFold(BaseMultiFold):
        def __init__(self, *a, **kw):
            super().__init__(*a, **kw)
            self.dynamics_rows = []
            self.split_records = []
            self.fit_lr_records = []
            self._diag_iteration = None
            self._diag_stepn = None
            self._inside_fit_compile = False
            instances.append(self)

        def cache(self, label, weights, stepn, cached, NTRAIN):
            out = super().cache(label, weights, stepn, cached, NTRAIN)
            if stepn == 1:
                self.split_records.append({
                    "iteration": int(self._diag_iteration),
                    "requested_cached": bool(cached),
                    "effective_cached": bool(cached),
                    "index_sha256": diag.array_sha256([np.asarray(self.idx_1)]),
                })
            return out

        def CompileModel(self, model, num_steps, fixed=False):
            effective_fixed = bool(fixed)
            if self._inside_fit_compile and self._diag_iteration > self.start:
                effective_fixed = True
            out = super().CompileModel(model, num_steps, fixed=effective_fixed)
            if self._inside_fit_compile:
                lr = float(tf.keras.backend.get_value(model.optimizer.learning_rate))
                self.fit_lr_records.append({
                    "iteration": int(self._diag_iteration),
                    "step": int(self._diag_stepn),
                    "requested_fixed": bool(fixed),
                    "effective_fixed": effective_fixed,
                    "learning_rate": lr,
                })
            return out

        def RunModel(self, labels, weights, iteration, model, stepn, NTRAIN=1000, cached=False):
            self._diag_iteration = int(iteration)
            self._diag_stepn = int(stepn)
            self._inside_fit_compile = True
            try:
                return super().RunModel(labels, weights, iteration, model, stepn, NTRAIN, cached)
            finally:
                self._inside_fit_compile = False

        def RunStep1(self, i):
            before = np.asarray(self.weights_push, dtype=np.float64).copy()
            super().RunStep1(i)
            data_mask = np.asarray(self.data.pass_reco).astype(bool)
            mc_mask = np.asarray(self.mc.pass_reco).astype(bool)
            row = diag.step1_metrics(
                before, self.weights_pull, self.mc_weight_reco, self.mc.pass_reco,
                float(np.asarray(self.data.weight)[data_mask].sum() /
                      np.asarray(self.mc_weight_reco)[mc_mask].sum()),
                float(engine.REWEIGHT_LOGIT_CAP),
            )
            row["iteration"] = int(i)
            row["trained_model_weight_sha256"] = diag.array_sha256(self.step1_models[0].get_weights())
            self.dynamics_rows.append(row)

        def RunStep2(self, i):
            super().RunStep2(i)
            row = self.dynamics_rows[-1]
            w = np.asarray(self.mc_weight_reco, dtype=np.float64)
            m = np.asarray(self.mc.pass_reco).astype(bool)
            row["push_mean_w_reco"] = float(
                (np.asarray(self.weights_push)[m] * w[m]).sum() / w[m].sum()
            )

    omnifold.MultiFold = AnnealedMultiFold
    driver_argv = ["--inputs", args.inputs, "--out", args.out, "--tag", "nominal",
                   "--gate3-manifest", args.gate3_manifest]
    if args.target_npy:
        driver_argv += ["--target-npy", args.target_npy]
    if args.target_receipt:
        driver_argv += ["--target-receipt", args.target_receipt]
    rc = nominal.main(driver_argv)
    if rc != 0 or len(instances) != 1:
        raise SystemExit(f"canonical driver rc={rc}; diagnostic engine instances={len(instances)}")
    inst = instances[0]
    niter = nominal.NOMINAL_SEED_POLICY["niter"]
    if len(inst.dynamics_rows) != niter or len(inst.fit_lr_records) != 2 * niter:
        raise SystemExit("annealed-LR arm emitted incomplete trajectory/LR telemetry")
    for rec in inst.fit_lr_records:
        expected = 1e-4 if rec["iteration"] == 0 else 1e-5
        if not math.isclose(rec["learning_rate"], expected, rel_tol=1e-5, abs_tol=1e-10):
            raise SystemExit(f"fit LR {rec} does not match intended {expected}")

    out = Path(args.out).resolve()
    result = Path(args.result_json).resolve()
    payload = {
        "schema": diag.SCHEMA,
        "status": "COMPLETE",
        "arm": ARM,
        "publication_candidate": False,
        "interventions": {
            "step1_model_reset_after_iteration0": False,
            "step1_fresh_split_after_iteration0": False,
            "effective_post_iteration_learning_rate": 1e-5,
            "anneal_applies_to_steps": [1, 2],
            "shared_engine_edited": False,
        },
        "frozen_policy_except_diagnostic_lr": nominal.NOMINAL_SEED_POLICY,
        "driver_output": str(out),
        "driver_output_sha256": hashlib.sha256(out.read_bytes()).hexdigest(),
        "rows": inst.dynamics_rows,
        "split_records": inst.split_records,
        "fit_lr_records": inst.fit_lr_records,
        "code": {
            "wrapper": str(Path(__file__).resolve()),
            "wrapper_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "factorial_helper": str(Path(diag.__file__).resolve()),
            "factorial_helper_sha256": hashlib.sha256(Path(diag.__file__).read_bytes()).hexdigest(),
            "driver": str(Path(nominal.__file__).resolve()),
            "driver_sha256": hashlib.sha256(Path(nominal.__file__).read_bytes()).hexdigest(),
            "engine": str(Path(engine.__file__).resolve()),
            "engine_sha256": hashlib.sha256(Path(engine.__file__).read_bytes()).hexdigest(),
        },
        "interpretation_contract": {
            "repair_definition": "iteration 2 Step-1 correction has correct sign and achieved_over_required >= 0.90",
            "repairs": "dead per-iteration LR anneal is implicated",
            "does_not_repair": "dead anneal alone does not explain the collapse",
        },
    }
    diag.atomic_json(result, payload)
    print(json.dumps({"diagnostic": "COMPLETE", "arm": ARM, "result": str(result),
                      "fit_lr_records": inst.fit_lr_records, "rows": inst.dynamics_rows}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
