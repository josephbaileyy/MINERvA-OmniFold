#!/usr/bin/env python3
"""Apply the predeclared annealed-production fold-forward reproduction test.

This evaluator is deliberately nominal-only.  It does not run extraction,
compute a cross section, assess powered-closure recovery, or promote an
artifact.  The thresholds are the immutable values predeclared before job
56563092 was submitted.
"""

import argparse
import hashlib
import json
import math
import os
import tempfile
from datetime import datetime, timezone

import numpy as np


EXPECTED_DEV = -0.011724
BAND = 0.010
LOW = EXPECTED_DEV - BAND
HIGH = EXPECTED_DEV + BAND
BASE_LR = 1.0e-4
ANNEALED_LR = 1.0e-5
EXPECTED_ITERATIONS = [0, 0, 1, 1, 2, 2]


def _item(value):
    try:
        return value.item()
    except (AttributeError, ValueError):
        return value


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1 << 22), b""):
            digest.update(block)
    return digest.hexdigest()


def atomic_json(path, payload):
    directory = os.path.dirname(os.path.abspath(path)) or "."
    os.makedirs(directory, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".annealed-reproduction-", suffix=".json", dir=directory)
    try:
        with os.fdopen(fd, "w") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.remove(temporary)


def evaluate(artifact):
    marker = artifact + ".done"
    if not os.path.isfile(artifact) or not os.path.isfile(marker):
        raise RuntimeError("artifact and hash-bound completion marker must both exist")
    with open(marker) as stream:
        marker_payload = json.load(stream)
    stat = os.stat(artifact)
    if "size" in marker_payload and int(marker_payload["size"]) != stat.st_size:
        raise RuntimeError("completion marker size does not match the artifact")
    if "mtime" in marker_payload and int(marker_payload["mtime"]) != int(stat.st_mtime):
        raise RuntimeError("completion marker mtime does not match the artifact")

    with np.load(artifact, allow_pickle=True) as data:
        required = {
            "fold_forward_sum_w_push_reco",
            "fold_forward_sum_w_reco",
            "step1_class_ratio",
            "seed_policy",
            "lr_policy_realized",
        }
        missing = sorted(required.difference(data.files))
        if missing:
            raise RuntimeError("artifact lacks required fields: {}".format(missing))
        numerator = float(np.asarray(data["fold_forward_sum_w_push_reco"]).reshape(-1)[0])
        denominator = float(np.asarray(data["fold_forward_sum_w_reco"]).reshape(-1)[0])
        ratio = float(np.asarray(data["step1_class_ratio"]).reshape(-1)[0])
        seed_policy = dict(_item(data["seed_policy"]))
        realized = dict(_item(data["lr_policy_realized"]))

    if not all(math.isfinite(x) for x in (numerator, denominator, ratio)):
        raise RuntimeError("fold-forward inputs must be finite")
    if denominator <= 0.0 or ratio <= 0.0:
        raise RuntimeError("fold-forward denominator and R must be positive")

    declared = seed_policy.get("lr_policy")
    if not isinstance(declared, dict):
        raise RuntimeError("seed_policy.lr_policy is absent or not a mapping")
    declared_ok = (
        declared.get("schedule") == "fit-time-anneal-after-iteration-0"
        and int(declared.get("applies_from_iteration", -1)) == 1
        and math.isclose(float(declared.get("base_lr", float("nan"))), BASE_LR, rel_tol=1e-12)
        and math.isclose(float(declared.get("annealed_lr", float("nan"))), ANNEALED_LR, rel_tol=1e-12)
    )
    if not declared_ok:
        raise RuntimeError("declared seed_policy.lr_policy does not match the adopted policy")

    fits = list(realized.get("fits", []))
    iterations = [int(record["iteration"]) for record in fits]
    rates = [float(record["learning_rate"]) for record in fits]
    realized_ok = (
        realized.get("verified_from_optimizer") is True
        and math.isclose(float(realized.get("base_lr", float("nan"))), BASE_LR, rel_tol=1e-12)
        and math.isclose(float(realized.get("annealed_lr", float("nan"))), ANNEALED_LR, rel_tol=1e-12)
        and int(realized.get("n_fits_base_lr", -1)) == 2
        and int(realized.get("n_fits_annealed", -1)) == 4
        and iterations == EXPECTED_ITERATIONS
        and len(rates) == 6
        and all(math.isclose(rate, BASE_LR, rel_tol=1e-4, abs_tol=1e-12) for rate in rates[:2])
        and all(math.isclose(rate, ANNEALED_LR, rel_tol=1e-4, abs_tol=1e-12) for rate in rates[2:])
    )
    if not realized_ok:
        raise RuntimeError("lr_policy_realized does not prove two base-LR plus four annealed-LR fits")

    deviation = (numerator / denominator) / ratio - 1.0
    if LOW <= deviation <= HIGH:
        verdict = "REPRODUCED"
    elif abs(deviation) < 0.05:
        verdict = "FINDING_CODE_PATHS_DISAGREE"
    else:
        verdict = "FINDING_ANNEAL_POLICY_OR_ESTIMATOR_FAILURE"

    return {
        "fold_forward": {
            "sum_w_push_reco": numerator,
            "sum_w_reco": denominator,
            "step1_class_ratio_R": ratio,
            "deviation": deviation,
            "expected_deviation": EXPECTED_DEV,
            "absolute_band": BAND,
            "pass_window": [LOW, HIGH],
            "verdict": verdict,
        },
        "anneal_discriminator": {
            "declared_policy": declared,
            "declared_policy_pass": declared_ok,
            "realized_policy": realized,
            "realized_policy_pass": realized_ok,
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--receipt", required=True)
    parser.add_argument("--predeclaration", required=True)
    parser.add_argument("--source-job", default=os.environ.get("SLURM_JOB_ID", ""))
    args = parser.parse_args()

    result = evaluate(args.artifact)
    payload = {
        "schema": "annealed-production-reproduction-v1",
        "recorded_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_job_id": str(args.source_job),
        "artifact": os.path.abspath(args.artifact),
        "artifact_sha256": sha256_file(args.artifact),
        "completion_marker_sha256": sha256_file(args.artifact + ".done"),
        "predeclaration": os.path.abspath(args.predeclaration),
        "predeclaration_sha256": sha256_file(args.predeclaration),
        "reproduction_test": result,
        "scope": {
            "nominal_fold_forward_only": True,
            "recovery_evaluated": False,
            "extraction_run": False,
            "cross_section_run": False,
            "promotion_authorized": False,
            "branch_c_opened": False,
        },
        "status": result["fold_forward"]["verdict"],
    }
    atomic_json(args.receipt, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
