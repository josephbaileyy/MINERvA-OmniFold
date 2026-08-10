#!/usr/bin/env python3
"""Finalize the existing annealed powered-closure artifact without retraining.

This is deliberately a post-processing lane.  It independently re-derives the
powered-closure spectra from the frozen full-event dump and persisted row/weight
artifact, applies the adopted Gate-4 criterion, proves the diagnostic remains
non-quotable, and writes one job-keyed receipt.  It never imports or edits the
shared training engine.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import sys
import traceback

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
for path in (HERE, REPO / "nd-unfolding", REPO / "nd-unfolding" / "pet"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import pet_diagnostic_quarantine as quarantine  # noqa: E402
import validate_pet_nominal_gate4 as gate4  # noqa: E402


def sha256_file(path, chunk=1 << 22):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(chunk), b""):
            digest.update(block)
    return digest.hexdigest()


def utc_now():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def atomic_json(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name("." + path.name + ".tmp-" + str(os.getpid()))
    with open(temporary, "x") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def require_hash(path, expected, checks, label):
    got = sha256_file(path)
    ok = got == expected
    checks.append({"name": "hash:" + label, "ok": ok,
                   "detail": "{} == {}".format(got, expected)})
    if not ok:
        raise RuntimeError("{} hash mismatch: {} != {}".format(label, got, expected))
    return got


def vector_metrics(report):
    prior = np.asarray(report["h_prior"], dtype=np.float64)
    target = np.asarray(report["h_target"], dtype=np.float64)
    unfolded = np.asarray(report["h_unfolded"], dtype=np.float64)
    untilted = np.asarray(report["h_untilted"], dtype=np.float64)
    gap = float(np.abs(prior - target).sum())
    floor = float(np.abs(prior - untilted).sum())
    residual = float(np.abs(unfolded - target).sum())
    return {
        "gap": gap,
        "floor": floor,
        "residual": residual,
        "floor_over_gap": floor / gap,
        "residual_over_gap": residual / gap,
        "recovery": 1.0 - residual / gap,
        "derivation": ("arithmetic on report vectors only after the authoritative validator "
                       "required each vector to match its independent dump/artifact re-derivation"),
    }


def check_lr_proof(report):
    proof = ((report.get("annealed_lr_arm") or {}).get("lr_proof") or {})
    records = proof.get("records") or []
    expected = [(0, 1, 1e-4), (0, 2, 1e-4),
                (1, 1, 1e-5), (1, 2, 1e-5),
                (2, 1, 1e-5), (2, 2, 1e-5)]
    actual = [(int(item.get("iteration")), int(item.get("step")),
               float(item.get("learning_rate"))) for item in records]
    ok = (len(actual) == len(expected)
          and all(a[:2] == e[:2] and abs(a[2] - e[2]) <= 5e-12
                  for a, e in zip(actual, expected))
          and int(proof.get("n_fits_base_lr", -1)) == 2
          and int(proof.get("n_fits_annealed", -1)) == 4)
    return ok, {"records": records,
                "expected": [{"iteration": i, "step": s, "learning_rate": lr}
                             for i, s, lr in expected]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--preflight", required=True)
    parser.add_argument("--inputs", required=True)
    parser.add_argument("--gate2-receipt", required=True)
    parser.add_argument("--nominal-weights", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--receipt", required=True)
    parser.add_argument("--lock", required=True)
    parser.add_argument("--source-job", required=True)
    parser.add_argument("--expected", action="append", default=[],
                        help="label:path:sha256; repeatable")
    args = parser.parse_args()

    checks = []
    receipt = {
        "schema": "annealed-shape-independent-finalization-v1",
        "started_at_utc": utc_now(),
        "source_job_id": str(args.source_job),
        "finalizer_job_id": os.environ.get("SLURM_JOB_ID", "nojob"),
        "retrained": False,
        "engine_edited": False,
        "threshold_changed": False,
        "promotion_authorized": False,
        "branch_c_opened": False,
        "checks": checks,
    }

    lock_fd = None
    exit_code = 1
    try:
        if Path(args.receipt).exists() or Path(args.manifest).exists():
            raise RuntimeError("collision: receipt or source-job manifest already exists")
        lock_fd = os.open(args.lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o444)
        os.write(lock_fd, ("job={} source_job={} started={}\n".format(
            receipt["finalizer_job_id"], args.source_job, receipt["started_at_utc"])).encode())
        os.fsync(lock_fd)

        for item in args.expected:
            label, path, expected = item.split(":", 2)
            require_hash(path, expected, checks, label)

        report = json.load(open(args.report))
        gate2_receipt = json.load(open(args.gate2_receipt))
        official_ok, official_checks = gate4.check_powered_closure(
            report, inputs_npz=args.inputs, gate2_receipt=gate2_receipt)
        checks.extend(official_checks)
        receipt["authoritative_gate4_powered_closure"] = {
            "ok": bool(official_ok),
            "validator": "validate_pet_nominal_gate4.check_powered_closure",
            "validator_sha256": sha256_file(HERE / "validate_pet_nominal_gate4.py"),
            "n_checks": len(official_checks),
            "n_failed": sum(not item.get("ok", False) for item in official_checks),
        }
        if not official_ok:
            raise RuntimeError("authoritative independent powered-closure validation failed")

        metrics = vector_metrics(report)
        primary_threshold = float(gate4.FROZEN["powered_closure"]["recovery_fraction_of_ceiling"]) * float(
            gate4.FROZEN["powered_closure"]["acceptance_limited_ceiling"])
        baseline, band = 0.546853, 0.02
        primary_ok = metrics["recovery"] >= primary_threshold
        if metrics["recovery"] > baseline + band:
            secondary = "REAL_REPAIR"
        elif metrics["recovery"] < baseline - band:
            secondary = "TRADE_OFF_CONFIRMED_ARM_REJECTED"
        else:
            secondary = "NO_INFORMATION_ON_SHAPE"
        receipt["scientific_reading"] = {
            "metrics": metrics,
            "primary": {
                "criterion": "recovery >= f * acceptance_limited_ceiling",
                "threshold": primary_threshold,
                "pass": primary_ok,
                "margin": metrics["recovery"] - primary_threshold,
                "rank": "PRIMARY_DECIDES",
            },
            "secondary": {
                "baseline": baseline,
                "band": band,
                "difference": metrics["recovery"] - baseline,
                "verdict": secondary,
                "rank": "SECONDARY_ASSUMPTION",
            },
            "combined": ("PRIMARY_PASS_SECONDARY_TRADE_OFF_CRITERION_DISAGREEMENT"
                         if primary_ok and secondary == "TRADE_OFF_CONFIRMED_ARM_REJECTED"
                         else "NO_PREDECLARED_DISAGREEMENT"),
        }
        if not primary_ok:
            raise RuntimeError("adopted primary recovery criterion failed")

        lr_ok, lr_detail = check_lr_proof(report)
        checks.append({"name": "anneal:fit_time_lr_proof", "ok": lr_ok,
                       "detail": lr_detail})
        if not lr_ok:
            raise RuntimeError("fit-time annealed learning-rate proof failed")

        manifest = quarantine.build_diagnostic_manifest(
            weights_npz=args.nominal_weights,
            xsec_npz=args.report,
            push_npz=args.artifact,
            xsec_summary=args.preflight,
            inputs_npz=args.inputs,
            out_path=args.manifest,
            job_id=args.source_job,
            extra={
                "launcher": "sbatch_finalize_annealed_shape_validation.sh",
                "finalizer_job_id": receipt["finalizer_job_id"],
                "source_training_job_id": str(args.source_job),
                "arm": "powered_closure_warm_fixed_annealed_lr",
                "predeclaration": "docs/orchestration/PREDECLARATION-20260810-annealed-shape-validation.md",
                "reused_existing_artifact_without_retraining": True,
                "engine_edited": False,
                "authorizes_engine_change": False,
            })
        quarantine_ok = (manifest.get("publication_gate_rejects_this") is True
                         and manifest.get("publication_gate_rejects_this_on_physics_alone") is True)
        checks.append({"name": "quarantine:dual_publication_rejection", "ok": quarantine_ok,
                       "detail": {"as_written": manifest.get("publication_gate_rejects_this"),
                                  "physics_alone": manifest.get(
                                      "publication_gate_rejects_this_on_physics_alone")}})
        if not quarantine_ok:
            raise RuntimeError("quarantine proof did not establish both rejection conditions")

        receipt["quarantine_manifest"] = {
            "path": str(Path(args.manifest).resolve()),
            "sha256": sha256_file(args.manifest),
            "publication_gate_rejects_this": True,
            "publication_gate_rejects_this_on_physics_alone": True,
        }
        receipt["status"] = "PASS_DIAGNOSTIC_PRIMARY_PASS_SECONDARY_TRADE_OFF_NONQUOTABLE"
        exit_code = 0
    except Exception as exc:
        receipt["status"] = "FAIL_CLOSED"
        receipt["error"] = "{}: {}".format(type(exc).__name__, exc)
        receipt["traceback"] = traceback.format_exc()
    finally:
        if lock_fd is not None:
            os.close(lock_fd)
        receipt["finished_at_utc"] = utc_now()
        receipt["exit_code"] = exit_code
        atomic_json(args.receipt, receipt)

    print("[ann-finalize] status={} receipt={}".format(receipt["status"], args.receipt))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
