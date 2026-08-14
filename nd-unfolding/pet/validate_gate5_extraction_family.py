#!/usr/bin/env python3
"""Independent terminal validator for the predeclared 50-member Gate-5 extraction.

The validator reports the declared family as a whole.  It never selects a subset or
constructs C_stat.  A missing/failed unit produces a durable BLOCK report and a
non-zero return code; only 50/50 can publish the complete-family marker.
"""

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
for item in (HERE, REPO / "nd-unfolding"):
    if str(item) not in os.sys.path:
        os.sys.path.insert(0, str(item))

from atomic_write import atomic_write, is_complete  # noqa: E402
from extract_fullevent_replica import (  # noqa: E402
    PUSH_SCHEMA, ROLE, SEED_POLICY, XSEC_SCHEMA, sha256_file,
)

VERDICT_PASS = "GATE5_EXTRACTION_FAMILY_COMPLETE_PASS"
VERDICT_BLOCK = "GATE5_EXTRACTION_FAMILY_BLOCKED"


def scalar(store, key):
    value = store[key]
    if isinstance(value, np.ndarray) and value.dtype == object and value.shape == ():
        return value.item()
    if isinstance(value, np.ndarray) and value.ndim == 0:
        value = value.item()
        return value.decode() if isinstance(value, bytes) else value
    return value


def write_json(path, payload, mark=False):
    def writer(tmp):
        with open(tmp, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())

    return atomic_write(path, writer, suffix=".json", overwrite=False, fsync=True,
                        mark=mark, note="Gate-5 extraction family terminal validation")


def load_promoted_training_inventory(path):
    with open(path, encoding="utf-8") as stream:
        report = json.load(stream)
    if report.get("verdict") != "GATE5_TRAINING_ARTIFACTS_PASS":
        raise SystemExit("[gate5-extract-validate] promoted training inventory is not PASS")
    if int(report.get("declared_inventory", -1)) != 50:
        raise SystemExit("[gate5-extract-validate] promoted training inventory is not N=50")
    rows = report.get("members") or []
    if len(rows) != 50:
        raise SystemExit("[gate5-extract-validate] promoted report lacks 50 member rows")
    out = {}
    for row in rows:
        idx = int(row.get("replica_index", -1))
        if idx in out or row.get("verdict") != "PASS":
            raise SystemExit("[gate5-extract-validate] promoted training member is invalid")
        out[idx] = row
    if set(out) != set(range(50)):
        raise SystemExit("[gate5-extract-validate] promoted training indices are not 0..49")
    return report, out


def validate_member(root, idx, promoted, args):
    seed = 50000 + idx
    base = Path(root) / "replicas" / f"replica_{idx:02d}"
    weights = base / "training/GATE5_REPLICA_WEIGHTS.npz"
    outdir = base / "extraction"
    paths = {
        "push": outdir / "GATE5_REPLICA_FULL_PUSH.npz",
        "xsec": outdir / "GATE5_REPLICA_XSEC.npz",
        "summary": outdir / "GATE5_REPLICA_XSEC.summary.json",
        "receipt": outdir / "GATE5_REPLICA_EXTRACTION_RECEIPT.json",
    }
    failures = []
    for label, path in paths.items():
        if not is_complete(path):
            failures.append(f"{label}: missing or invalid completion marker")
    if not is_complete(weights):
        failures.append("training artifact completion marker invalid")
    if failures:
        return {"replica_index": idx, "bootstrap_seed": seed,
                "verdict": "FAIL", "failures": failures}

    try:
        with open(paths["receipt"], encoding="utf-8") as stream:
            receipt = json.load(stream)
        if receipt.get("verdict") != "GATE5_REPLICA_FULL_EXTRACTION_PASS":
            failures.append("task receipt verdict is not PASS")
        if (int(receipt.get("replica_index", -1)),
                int(receipt.get("bootstrap_seed", -1))) != (idx, seed):
            failures.append("task receipt index/seed mismatch")
        if receipt.get("seed_policy") != SEED_POLICY:
            failures.append("task receipt seed policy mismatch")
        execution = receipt.get("execution") or {}
        if execution.get("head_at_runtime") != args.expected_head:
            failures.append("runtime code HEAD mismatch")
        if str(execution.get("slurm_array_job_id")) != str(args.source_array_job):
            failures.append("source array job mismatch")
        if int(execution.get("slurm_array_task_id", -1)) != idx:
            failures.append("source array task mismatch")

        training = receipt.get("training_artifact") or {}
        promoted_sha = (promoted.get("artifact") or {}).get("sha256")
        if training.get("sha256") != promoted_sha:
            failures.append("training artifact differs from promoted 50/50 inventory")
        if sha256_file(weights) != promoted_sha:
            failures.append("on-disk training artifact hash drift")
        if (receipt.get("source") or {}).get("sha256") != args.expected_inputs_sha:
            failures.append("source SHA-256 mismatch")

        factors = receipt.get("coherent_factors") or {}
        for key in ("signal_applied_to_full_truth_counts",
                    "signal_applied_to_completeness_and_reporting_mask",
                    "background_applied_before_target_refinement",
                    "canonical_replay_verified"):
            if factors.get(key) is not True:
                failures.append(f"coherent-factor proof {key} is not true")
        code = receipt.get("code") or {}
        for key, want in (
            ("replica_extractor_sha256", args.expected_driver_sha),
            ("gate4_pinned_nominal_extractor_sha256", args.expected_nominal_extractor_sha),
            ("loader_sha256", args.expected_loader_sha),
        ):
            if code.get(key) != want:
                failures.append(f"code pin mismatch: {key}")

        receipt_artifacts = receipt.get("artifacts") or {}
        raw_hashes = {}
        for label in ("push", "xsec", "summary"):
            got = sha256_file(paths[label])
            raw_hashes[label] = got
            if (receipt_artifacts.get(label) or {}).get("sha256") != got:
                failures.append(f"{label} hash differs from task receipt")

        with np.load(paths["push"], allow_pickle=True) as push:
            if scalar(push, "push_schema") != PUSH_SCHEMA:
                failures.append("push schema mismatch")
            if scalar(push, "campaign_role") != ROLE:
                failures.append("push campaign role mismatch")
            if (int(scalar(push, "replica_index")),
                    int(scalar(push, "bootstrap_seed"))) != (idx, seed):
                failures.append("push index/seed mismatch")
            if scalar(push, "source_weights_sha256") != promoted_sha:
                failures.append("push is not bound to promoted training artifact")
            if scalar(push, "inputs_sha256") != args.expected_inputs_sha:
                failures.append("push source input SHA mismatch")
            if scalar(push, "full_ordered_coverage_verified") is not True:
                failures.append("push does not persist full ordered coverage PASS")

        with np.load(paths["xsec"], allow_pickle=True) as xsec_store:
            if scalar(xsec_store, "xsec_schema") != XSEC_SCHEMA:
                failures.append("xsec schema mismatch")
            if scalar(xsec_store, "campaign_role") != ROLE:
                failures.append("xsec campaign role mismatch")
            if (int(scalar(xsec_store, "replica_index")),
                    int(scalar(xsec_store, "bootstrap_seed"))) != (idx, seed):
                failures.append("xsec index/seed mismatch")
            if scalar(xsec_store, "training_artifact_sha256") != promoted_sha:
                failures.append("xsec is not bound to promoted training artifact")
            if scalar(xsec_store, "push_sha256") != raw_hashes["push"]:
                failures.append("xsec push hash mismatch")
            values = np.asarray(xsec_store["xsec"], dtype=np.float64)
            pt = np.asarray(xsec_store["edges_pt"], dtype=np.float64)
            pp = np.asarray(xsec_store["edges_pparallel"], dtype=np.float64)
            if values.shape != (pt.size - 1, pp.size - 1):
                failures.append("xsec shape/edge mismatch")
            if not np.isfinite(values).all() or (values < 0).any():
                failures.append("xsec contains non-finite or negative cells")
            total = float(scalar(xsec_store, "total_sigma_cm2_per_nucleon"))
            if not np.isfinite(total) or total <= 0:
                failures.append("xsec total is invalid")
            telem = scalar(xsec_store, "extraction_telemetry")
            if telem.get("gate5_signal_factor_applied_to_truth_counts") is not True:
                failures.append("xsec telemetry lacks count-factor proof")
            if telem.get(
                    "gate5_signal_factor_applied_to_completeness_and_reporting_mask") is not True:
                failures.append("xsec telemetry lacks completeness-factor proof")

        with open(paths["summary"], encoding="utf-8") as stream:
            summary = json.load(stream)
        if summary.get("status") != "PASS" or summary.get("C_stat", "missing") is not None:
            failures.append("summary is not PASS with C_stat null")
        if summary.get("signal_factor_applied_to_truth_counts") is not True:
            failures.append("summary lacks count-factor proof")
        if summary.get("signal_factor_applied_to_completeness_and_reporting_mask") is not True:
            failures.append("summary lacks completeness-factor proof")

        return {
            "replica_index": idx,
            "bootstrap_seed": seed,
            "verdict": "PASS" if not failures else "FAIL",
            "failures": failures,
            "training_artifact_sha256": promoted_sha,
            "push_sha256": raw_hashes.get("push"),
            "xsec_sha256": raw_hashes.get("xsec"),
            "summary_sha256": raw_hashes.get("summary"),
            "receipt_sha256": sha256_file(paths["receipt"]),
        }
    except Exception as exc:  # terminal report must name a malformed member, not disappear
        failures.append(f"exception while validating member: {type(exc).__name__}: {exc}")
        return {"replica_index": idx, "bootstrap_seed": seed,
                "verdict": "FAIL", "failures": failures}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", required=True)
    ap.add_argument("--promoted-training-report", required=True)
    ap.add_argument("--source-array-job", required=True)
    ap.add_argument("--expected-head", required=True)
    ap.add_argument("--expected-inputs-sha", required=True)
    ap.add_argument("--expected-driver-sha", required=True)
    ap.add_argument("--expected-nominal-extractor-sha", required=True)
    ap.add_argument("--expected-loader-sha", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    promoted_report, promoted = load_promoted_training_inventory(
        args.promoted_training_report
    )
    rows = [validate_member(args.root, idx, promoted[idx], args) for idx in range(50)]
    passing = sum(row["verdict"] == "PASS" for row in rows)
    verdict = VERDICT_PASS if passing == 50 else VERDICT_BLOCK
    payload = {
        "schema_version": 1,
        "tool": "validate_gate5_extraction_family.py",
        "recorded_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "verdict": verdict,
        "declared_inventory": 50,
        "members_present_and_passing": passing,
        "members_failing": [row["replica_index"] for row in rows
                            if row["verdict"] != "PASS"],
        "source_array_job_id": str(args.source_array_job),
        "source_sha256": args.expected_inputs_sha,
        "promoted_training_report": {
            "path": os.path.abspath(args.promoted_training_report),
            "sha256": sha256_file(args.promoted_training_report),
            "verdict": promoted_report["verdict"],
        },
        "immutable_code": {
            "head": args.expected_head,
            "replica_extractor_sha256": args.expected_driver_sha,
            "gate4_pinned_nominal_extractor_sha256": args.expected_nominal_extractor_sha,
            "loader_sha256": args.expected_loader_sha,
        },
        "members": rows,
        "C_stat": None,
        "subset_selected": False,
        "why_C_stat_is_null":
            "This terminal gate validates complete extraction only. Centering on the replica "
            "mean and constructing C_stat are separate actions after 50/50 promotion.",
    }
    write_json(args.out, payload, mark=True)
    print(json.dumps({"verdict": verdict, "passing": passing, "declared": 50,
                      "out": os.path.abspath(args.out)}, sort_keys=True))
    return 0 if verdict == VERDICT_PASS else 1


if __name__ == "__main__":
    raise SystemExit(main())
