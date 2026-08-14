#!/usr/bin/env python3
"""Independent terminal validator for the Gate-5 N=50 training artifacts.

This validator complements ``reconcile_gate5_family.py``.  The reconciler independently
replays all three Poisson streams and verifies receipts, markers, hashes, code continuity,
and 50/50 completeness.  This tool opens the produced NPZ files and verifies the evidence
that otherwise exists only as a producer claim: the frozen estimator/subsample policy, the
realized two-base/four-annealed optimizer fits, the full and restricted signal factors, the
full background factors, source/target/identity bindings, task logs, accounting, and isolated
output namespaces.  It never extracts a spectrum and contains no covariance code.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

import numpy as np


DECLARED_N = 50
SEED_BASE = 50000
ARRAY_JOB_ID = "56857233"
SEED_POLICY_STRING = "gate5-cstat-n50-v1: bootstrap_seed=50000+replica_index"
SOURCE_SHA256 = "fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625"
EXPECTED_HEAD = "b82ac63f9c5685c9cc05df059d2bbb4ae42d3258"
ESTIMATOR = "pet-fullevent-fps-v1"
BKG_MODE = "negweight-refined"
EXPECTED_CODE = {
    "replica_driver": "4fb2902eeb2e8f08ad78a7542bcf82d2c509e0af392b3410bedafac229502f4c",
    "nominal_driver_unmodified": "91144bee2ff89ae62497c8282174f0fc1c344f455945d6b52b7b8219ecb4e7bc",
    "loader": "e1402370cdb8bd6349419ba6fbefa68817b799b3699cc97b673933f1f0220ce1",
}
LR_POLICY = {
    "schedule": "fit-time-anneal-after-iteration-0",
    "base_lr": 1e-4,
    "annealed_lr": 1e-5,
    "applies_from_iteration": 1,
    "mechanism": (
        "MultiFold subclass overriding CompileModel at fit time; omnifold.py is NOT edited"
    ),
}
FROZEN_POLICY = {
    "estimator_seed": 42,
    "subsample_seed": 0,
    "niter": 3,
    "epochs": 8,
    "train_events": 2_000_000,
    "batch_size": 512,
    "lr_policy": LR_POLICY,
}

TRAIN_ARTIFACT = "GATE5_REPLICA_WEIGHTS.npz"
TRAIN_RECEIPT = "GATE5_REPLICA_TRAINING_RECEIPT.json"
TARGET_ARTIFACT = "GATE5_REPLICA_TARGET.npy"
TARGET_RECEIPT = "GATE5_REPLICA_TARGET_RECEIPT.json"


def sha256_file(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def hash_array(value: np.ndarray) -> str:
    """Exact Gate-5 factor contract: dtype || compact JSON(shape) || raw bytes."""
    a = np.ascontiguousarray(value)
    h = hashlib.sha256()
    h.update(str(a.dtype).encode("ascii"))
    h.update(json.dumps(list(a.shape), separators=(",", ":")).encode("ascii"))
    h.update(memoryview(a).cast("B"))
    return h.hexdigest()


def scalar(store, key):
    return np.asarray(store[key]).item()


class Checks:
    def __init__(self):
        self.passed = []
        self.failed = []

    @staticmethod
    def _plain(value):
        if isinstance(value, np.generic):
            return value.item()
        if isinstance(value, Path):
            return str(value)
        return value

    def eq(self, name, got, want, note=None):
        got, want = self._plain(got), self._plain(want)
        row = {"check": name, "got": got, "want": want}
        if note:
            row["note"] = note
        (self.passed if got == want else self.failed).append(row)

    def truth(self, name, value, note=None):
        self.eq(name, bool(value), True, note)

    def close(self, name, got, want, atol=1e-12):
        ok = bool(np.isclose(float(got), float(want), rtol=0.0, atol=atol))
        row = {"check": name, "got": float(got), "want": float(want), "atol": atol}
        (self.passed if ok else self.failed).append(row)

    def summary(self):
        return {
            "n_passed": len(self.passed),
            "n_failed": len(self.failed),
            "failures": self.failed,
        }


def read_json(path: Path):
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def family_target_rows(report):
    rows = report.get("targets") or []
    return {int(row.get("replica_index", -1)): row for row in rows}


def expected_checkpoints() -> set[str]:
    names = set()
    for iteration in range(3):
        for step in (1, 2):
            stem = f"OmniFold_fe_nominal_nominal_iter{iteration}_step{step}"
            names.add(stem + ".pkl")
            names.add(stem + ".weights.h5")
    names.add("OmniFold_fe_nominal_nominal_iter2_step1_final.weights.h5")
    names.add("OmniFold_fe_nominal_nominal_iter2_step2_final.weights.h5")
    return names


def validate_member(idx, campaign: Path, target_row, expected_indices: np.ndarray):
    checks = Checks()
    seed = SEED_BASE + idx
    replica = campaign / "replicas" / f"replica_{idx:02d}"
    train_dir = replica / "training"
    target_dir = replica / "target"
    artifact = train_dir / TRAIN_ARTIFACT
    receipt_path = train_dir / TRAIN_RECEIPT
    target_path = target_dir / TARGET_ARTIFACT
    target_receipt_path = target_dir / TARGET_RECEIPT

    required = [artifact, artifact.with_name(artifact.name + ".done"), receipt_path,
                receipt_path.with_name(receipt_path.name + ".done"), target_path,
                target_receipt_path]
    for path in required:
        checks.truth(f"exists_regular_not_symlink[{path.name}]",
                     path.is_file() and not path.is_symlink())
    if checks.failed:
        return {"replica_index": idx, "verdict": "FAIL", "checks": checks.summary()}

    receipt = read_json(receipt_path)
    target_receipt = read_json(target_receipt_path)
    artifact_sha = sha256_file(artifact)
    target_sha = sha256_file(target_path)
    target_receipt_sha = sha256_file(target_receipt_path)

    checks.eq("receipt_status", receipt.get("status"), "PASS")
    checks.eq("receipt_verdict", receipt.get("verdict"),
              "GATE5_REPLICA_TRAINING_PASS_EXTRACTION_PENDING")
    checks.eq("receipt_index", receipt.get("replica_index"), idx)
    checks.eq("receipt_seed", receipt.get("bootstrap_seed"), seed)
    checks.eq("receipt_seed_policy", receipt.get("seed_policy"), SEED_POLICY_STRING)
    execution = receipt.get("execution") or {}
    checks.eq("receipt_array_job", str(execution.get("slurm_array_job_id")), ARRAY_JOB_ID)
    checks.eq("receipt_array_task", str(execution.get("slurm_array_task_id")), str(idx))
    checks.eq("receipt_runtime_head", execution.get("head_at_runtime"), EXPECTED_HEAD)
    checks.eq("receipt_artifact_path", os.path.realpath(receipt["artifact"]["path"]),
              os.path.realpath(artifact))
    checks.eq("artifact_sha256", artifact_sha, receipt["artifact"].get("sha256"))
    checks.eq("artifact_size", artifact.stat().st_size,
              receipt["artifact"].get("size_bytes"))
    checks.eq("receipt_target_path", os.path.realpath(receipt["target"]["path"]),
              os.path.realpath(target_path))
    checks.eq("target_sha256", target_sha, receipt["target"].get("sha256"))
    checks.eq("target_receipt_sha256", target_receipt_sha,
              receipt["target"].get("receipt_sha256"))
    for role, digest in EXPECTED_CODE.items():
        checks.eq(f"receipt_code_sha256[{role}]",
                  (receipt.get("code", {}).get(role) or {}).get("sha256"), digest)

    bootstrap = target_receipt.get("bootstrap") or {}
    identities = bootstrap.get("input_identity_hashes")
    replay = (target_row or {}).get("replay") or {}
    checks.eq("family_target_row_verdict", (target_row or {}).get("verdict"), "PASS")
    checks.eq("canonical_factor_replay_performed", replay.get("performed"), True)
    checks.eq("canonical_data_factor_hash",
              replay.get("data_factor_sha256_REDRAWN"), bootstrap.get("data_factor_sha256"))
    checks.eq("canonical_signal_factor_hash",
              replay.get("signal_factor_sha256_REDRAWN"), bootstrap.get("signal_factor_sha256"))
    checks.eq("canonical_background_factor_hash",
              replay.get("background_factor_sha256_REDRAWN"),
              bootstrap.get("background_factor_sha256"))

    with np.load(artifact, allow_pickle=True) as store:
        required_keys = {
            "campaign_role", "replica_index", "bootstrap_seed", "replica_seed_policy",
            "seed_policy", "estimator_fingerprint", "bkg_mode", "tag", "inputs_sha256",
            "inventory_hashes", "input_identity_hashes", "n_sig_full", "n_data_full",
            "n_bkg_full", "mc_indices", "sig_bootstrap_factor_full",
            "sig_bootstrap_factor", "bkg_indices", "bkg_bootstrap_factor",
            "bootstrap_factor_sha256", "replica_target_sha256",
            "replica_target_receipt_sha256", "replica_target_receipt_path",
            "lr_policy_realized", "weights_push", "target", "inference_contract",
        }
        checks.eq("required_npz_keys_missing", sorted(required_keys - set(store.files)), [])
        if required_keys - set(store.files):
            return {"replica_index": idx, "verdict": "FAIL", "checks": checks.summary()}

        checks.eq("artifact_role", scalar(store, "campaign_role"),
                  "gate5-cstat-coherent-replica")
        checks.eq("artifact_replica_index", int(scalar(store, "replica_index")), idx)
        checks.eq("artifact_bootstrap_seed", int(scalar(store, "bootstrap_seed")), seed)
        checks.eq("artifact_replica_seed_policy", scalar(store, "replica_seed_policy"),
                  SEED_POLICY_STRING)
        checks.eq("frozen_estimator_policy", scalar(store, "seed_policy"), FROZEN_POLICY)
        checks.eq("estimator_fingerprint", scalar(store, "estimator_fingerprint"), ESTIMATOR)
        checks.eq("background_mode", scalar(store, "bkg_mode"), BKG_MODE)
        checks.eq("training_tag", scalar(store, "tag"), "nominal")
        checks.eq("source_sha256", scalar(store, "inputs_sha256"), SOURCE_SHA256)

        n_sig = int(scalar(store, "n_sig_full"))
        n_data = int(scalar(store, "n_data_full"))
        n_bkg = int(scalar(store, "n_bkg_full"))
        checks.eq("n_sig_full", n_sig, bootstrap.get("n_sig_full"))
        checks.eq("n_data_full", n_data, bootstrap.get("n_data_full"))
        checks.eq("n_bkg_full", n_bkg, bootstrap.get("n_bkg_full"))
        checks.eq("inventory_hashes", scalar(store, "inventory_hashes"),
                  bootstrap.get("inventory_hashes"))
        checks.eq("input_identity_hashes", scalar(store, "input_identity_hashes"), identities)

        mc_indices = np.asarray(store["mc_indices"], dtype=np.int64)
        sig_full = np.asarray(store["sig_bootstrap_factor_full"], dtype=np.uint8)
        sig_subset = np.asarray(store["sig_bootstrap_factor"], dtype=np.uint8)
        bkg_indices = np.asarray(store["bkg_indices"], dtype=np.int64)
        bkg_full = np.asarray(store["bkg_bootstrap_factor"], dtype=np.uint8)
        checks.truth("mc_indices_exact_frozen_subsample",
                     np.array_equal(mc_indices, expected_indices),
                     "independently regenerated from default_rng(0).choice before this loop")
        checks.eq("signal_full_shape", list(sig_full.shape), [n_sig])
        checks.eq("signal_subset_shape", list(sig_subset.shape), [FROZEN_POLICY["train_events"]])
        checks.truth("signal_subset_is_exact_full_restriction",
                     np.array_equal(sig_subset, sig_full[mc_indices]))
        checks.truth("background_indices_are_complete_ordered_inventory",
                     np.array_equal(bkg_indices, np.arange(n_bkg, dtype=np.int64)))
        checks.eq("background_full_shape", list(bkg_full.shape), [n_bkg])

        factor_meta = scalar(store, "bootstrap_factor_sha256")
        sig_hash = hash_array(sig_full)
        bkg_hash = hash_array(bkg_full)
        checks.eq("signal_full_hash_vs_target", sig_hash, bootstrap.get("signal_factor_sha256"))
        checks.eq("signal_full_hash_vs_canonical_replay", sig_hash,
                  replay.get("signal_factor_sha256_REDRAWN"))
        checks.eq("background_full_hash_vs_target", bkg_hash,
                  bootstrap.get("background_factor_sha256"))
        checks.eq("background_full_hash_vs_canonical_replay", bkg_hash,
                  replay.get("background_factor_sha256_REDRAWN"))
        for key in ("data_factor_sha256", "signal_factor_sha256",
                    "background_factor_sha256", "inventory_hashes", "n_data_full",
                    "n_sig_full", "n_bkg_full", "input_identity_hashes"):
            checks.eq(f"persisted_bootstrap_metadata[{key}]", factor_meta.get(key),
                      bootstrap.get(key))

        checks.eq("artifact_target_sha", scalar(store, "replica_target_sha256"), target_sha)
        checks.eq("artifact_target_receipt_sha",
                  scalar(store, "replica_target_receipt_sha256"), target_receipt_sha)
        checks.eq("artifact_target_receipt_path",
                  os.path.realpath(scalar(store, "replica_target_receipt_path")),
                  os.path.realpath(target_receipt_path))
        target_meta = scalar(store, "target")
        checks.eq("target_meta_mode", target_meta.get("target_mode"), BKG_MODE)
        checks.eq("target_meta_seed", target_meta.get("bootstrap_seed"), seed)
        checks.eq("target_meta_fingerprint", target_meta.get("estimator_fingerprint"), ESTIMATOR)
        checks.eq("target_meta_identity", target_meta.get("input_identity_hashes"), identities)
        checks.eq("target_meta_consumed_path",
                  os.path.realpath(target_meta.get("consumed_precomputed_target", "")),
                  os.path.realpath(target_path))

        realized = scalar(store, "lr_policy_realized")
        fits = realized.get("fits") or []
        checks.eq("optimizer_verified", realized.get("verified_from_optimizer"), True)
        checks.eq("n_fits_base_lr", realized.get("n_fits_base_lr"), 2)
        checks.eq("n_fits_annealed", realized.get("n_fits_annealed"), 4)
        checks.eq("fit_count", len(fits), 6)
        expected_rates = [1e-4, 1e-4, 1e-5, 1e-5, 1e-5, 1e-5]
        expected_iterations = [0, 0, 1, 1, 2, 2]
        checks.eq("fit_iterations", [f.get("iteration") for f in fits], expected_iterations)
        for fit_idx, (fit, expected) in enumerate(zip(fits, expected_rates)):
            checks.close(f"fit_learning_rate[{fit_idx}]", fit.get("learning_rate"), expected,
                         atol=3e-12)

        weights = np.asarray(store["weights_push"])
        checks.eq("weights_push_shape", list(weights.shape), [FROZEN_POLICY["train_events"]])
        checks.truth("weights_push_finite", np.all(np.isfinite(weights)))
        checks.truth("weights_push_nonnegative", np.all(weights >= 0))

        contract = scalar(store, "inference_contract")
        expected_final = {
            "step1_checkpoint": train_dir / "w_nominal" /
                "OmniFold_fe_nominal_nominal_iter2_step1_final.weights.h5",
            "step2_checkpoint": train_dir / "w_nominal" /
                "OmniFold_fe_nominal_nominal_iter2_step2_final.weights.h5",
        }
        checks.eq("checkpoint_semantics", contract.get("checkpoint_semantics"),
                  "final-epoch weights, round-trip verified (BEN-043)")
        for key, path in expected_final.items():
            checks.eq(f"inference_contract_{key}", os.path.realpath(contract.get(key, "")),
                      os.path.realpath(path))
            checks.truth(f"checkpoint_exists[{key}]", path.is_file() and not path.is_symlink())

    checkpoint_dir = train_dir / "w_nominal"
    got_checkpoints = {p.name for p in checkpoint_dir.iterdir() if p.is_file()}
    checks.eq("checkpoint_file_set", sorted(got_checkpoints), sorted(expected_checkpoints()))
    root_entries = {p.name for p in train_dir.iterdir()}
    checks.eq("training_namespace_root_entries", sorted(root_entries), sorted({
        TRAIN_ARTIFACT, TRAIN_ARTIFACT + ".done", TRAIN_RECEIPT,
        TRAIN_RECEIPT + ".done", "w_nominal",
    }))

    stdout = campaign / "logs" / f"train_{ARRAY_JOB_ID}_{idx}.out"
    stderr = campaign / "logs" / f"train_{ARRAY_JOB_ID}_{idx}.err"
    checks.truth("stdout_regular", stdout.is_file() and not stdout.is_symlink())
    checks.truth("stderr_regular", stderr.is_file() and not stderr.is_symlink())
    out_text = stdout.read_text(errors="replace") if stdout.is_file() else ""
    err_text = stderr.read_text(errors="replace") if stderr.is_file() else ""
    checks.eq("log_start_line_count",
              out_text.count(f"[gate5-train] index={idx} seed={seed} job={ARRAY_JOB_ID}_{idx}"), 1)
    checks.eq("log_config_gate_pass_count", out_text.count('"config_gate": "PASS"'), 1)
    checks.eq("log_optimizer_proof_count",
              out_text.count("LR anneal VERIFIED from the optimizer: 2 fit(s) at 0.0001, 4 at 1e-05"), 1)
    checks.eq("log_pass_receipt_count", out_text.count('"status": "PASS"'), 1)
    checks.eq("log_done_count", out_text.count(f"[gate5-train] DONE index={idx} seed={seed}"), 1)
    fatal_tokens = ["Traceback (most recent call last)", "[gate5-train][FAIL]", "SystemExit:"]
    checks.eq("fatal_log_tokens", [t for t in fatal_tokens if t in out_text or t in err_text], [])

    return {
        "replica_index": idx,
        "bootstrap_seed": seed,
        "artifact": {"path": str(artifact), "sha256": artifact_sha,
                     "size_bytes": artifact.stat().st_size},
        "target_sha256": target_sha,
        "log_sha256": {"stdout": sha256_file(stdout), "stderr": sha256_file(stderr)},
        "checks": checks.summary(),
        "verdict": "PASS" if not checks.failed else "FAIL",
    }


def parse_sacct(path: Path):
    rows = {}
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        fields = line.split("|")
        if len(fields) < 8 or not fields[0].startswith(ARRAY_JOB_ID + "_"):
            continue
        idx = int(fields[0].split("_", 1)[1])
        rows[idx] = {
            "job_id": fields[0], "job_id_raw": fields[1], "state": fields[2],
            "exit_code": fields[3], "elapsed": fields[4], "start": fields[5],
            "end": fields[6], "node": fields[7],
        }
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--campaign-root", required=True)
    ap.add_argument("--family-report", required=True)
    ap.add_argument("--sacct", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    campaign = Path(args.campaign_root).resolve()
    family_report_path = Path(args.family_report).resolve()
    sacct_path = Path(args.sacct).resolve()
    report = read_json(family_report_path)
    top = Checks()
    top.eq("family_reconciler_verdict", report.get("verdict"), "FAMILY_COMPLETE_PASS")
    top.eq("family_reconciler_full_strength", report.get("is_full_strength"), True)
    top.eq("family_reconciler_weakened_axes", report.get("weakened_axes"), [])
    top.eq("family_reconciler_declared_inventory", report.get("declared_inventory"), DECLARED_N)
    top.eq("family_reconciler_counts", report.get("counts"), {
        "targets_present": 50, "targets_passing": 50, "trainings_present": 50,
        "trainings_passing": 50, "trainings_in_progress": 0,
        "trainings_not_started": 0, "trainings_name_mismatch": 0, "targets_absent": 0,
    })
    top.eq("family_reconciler_failures", (report.get("family_checks") or {}).get("n_failed"), 0)

    target_rows = family_target_rows(report)
    top.eq("family_target_row_ids", sorted(target_rows), list(range(DECLARED_N)))
    sacct_rows = parse_sacct(sacct_path)
    top.eq("sacct_task_ids", sorted(sacct_rows), list(range(DECLARED_N)))
    for idx, row in sacct_rows.items():
        top.eq(f"sacct_state[{idx}]", row["state"], "COMPLETED")
        top.eq(f"sacct_exit_code[{idx}]", row["exit_code"], "0:0")

    # The subsample is fixed independently of the bootstrap seed and therefore generated once.
    first_target = read_json(campaign / "replicas" / "replica_00" / "target" / TARGET_RECEIPT)
    n_sig = int(first_target["bootstrap"]["n_sig_full"])
    expected_indices = np.sort(np.random.default_rng(0).choice(
        n_sig, FROZEN_POLICY["train_events"], replace=False
    )).astype(np.int64)

    rows = [validate_member(idx, campaign, target_rows.get(idx), expected_indices)
            for idx in range(DECLARED_N)]
    failing = [r["replica_index"] for r in rows if r["verdict"] != "PASS"]
    top.eq("training_members_failing", failing, [])
    artifact_paths = [r.get("artifact", {}).get("path") for r in rows if r.get("artifact")]
    artifact_hashes = [r.get("artifact", {}).get("sha256") for r in rows if r.get("artifact")]
    top.eq("artifact_paths_unique", len(set(artifact_paths)), DECLARED_N)
    top.eq("artifact_hashes_unique", len(set(artifact_hashes)), DECLARED_N,
           "distinct training products are collision evidence, not a physics criterion")

    verdict = "GATE5_TRAINING_ARTIFACTS_PASS" if not top.failed else "BLOCK"
    output = {
        "tool": "validate_gate5_training_artifacts.py",
        "verdict": verdict,
        "declared_inventory": DECLARED_N,
        "array_job_id": ARRAY_JOB_ID,
        "family_report": {"path": str(family_report_path),
                          "sha256": sha256_file(family_report_path)},
        "sacct": {"path": str(sacct_path), "sha256": sha256_file(sacct_path),
                  "rows": sacct_rows},
        "frozen_policy": FROZEN_POLICY,
        "source_sha256": SOURCE_SHA256,
        "C_stat": None,
        "why_C_stat_is_null": (
            "This terminal gate validates training artifacts only. Full-input extraction and "
            "mean-centered covariance construction are separate predeclared stages."
        ),
        "members": rows,
        "summary": {"members_present": len(rows), "members_passing": DECLARED_N - len(failing),
                    "members_failing": failing, "checks": top.summary()},
    }
    out = Path(args.out)
    out.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"verdict": verdict, "members_passing": DECLARED_N - len(failing),
                      "members_failing": failing, "family_failures": top.failed}, indent=2))
    return 0 if verdict.endswith("PASS") else 2


if __name__ == "__main__":
    raise SystemExit(main())
