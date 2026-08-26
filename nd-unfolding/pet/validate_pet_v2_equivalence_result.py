#!/usr/bin/env python3
"""Read-only validation and terminal reclassification for PET-v2 equivalence.

All scientific inputs are hashed before and after validation.  The sole write is
the separately named validation receipt, published last.  This validator cannot
submit, retry, construct a covariance, or change an existing artifact.
"""

import argparse
import datetime as dt
import json
import os
import socket
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from atomic_write import atomic_write, is_complete, mark_complete  # noqa: E402
from pet_v2_equivalence_common import (  # noqa: E402
    AUTHORIZATION_TOKEN, CONTRACT_ID, PROHIBITIONS, classify, git_head,
    sha256_file,
)

SCHEMA = "pet-v2-equivalence-independent-readback-v1"
ARMS = ("W_A", "W_B", "L")


def _regular(path, label):
    path = Path(path).resolve()
    if not path.is_file() or path.is_symlink():
        raise SystemExit(f"[pet-v2-validate] invalid {label}: {path}")
    return path


def _json(path, label):
    path = _regular(path, label)
    if not is_complete(str(path)):
        raise SystemExit(f"[pet-v2-validate] invalid completion marker for {label}: {path}")
    return path, json.loads(path.read_text(encoding="utf-8"))


def _write(path, payload):
    def writer(tmp):
        with open(tmp, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
    atomic_write(str(path), writer, suffix=".json", overwrite=False, fsync=True)
    mark_complete(str(path), note="PET-v2 equivalence read-only validation")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected-head", required=True)
    parser.add_argument("--proposal", required=True)
    parser.add_argument("--target-receipt", required=True)
    for arm in ARMS:
        parser.add_argument(f"--{arm.lower()}-receipt", required=True)
    parser.add_argument("--result", required=True)
    parser.add_argument("--result-receipt", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    if git_head(REPO) != args.expected_head:
        raise SystemExit("[pet-v2-validate] runtime HEAD mismatch")
    output = Path(args.output).resolve()
    if os.path.lexists(output) or os.path.lexists(f"{output}.done"):
        raise SystemExit(f"[pet-v2-validate] collision/no-clobber guard: {output}")

    # The proposal is a committed source operand inside the immutable checkout, not a runtime
    # product.  Requiring a sidecar completion marker here would force the worker to dirty that
    # checkout.  Its clean exact HEAD is checked above; content is hashed before and after below.
    proposal_path = _regular(args.proposal, "proposal")
    proposal = json.loads(proposal_path.read_text(encoding="utf-8"))
    target_path, target = _json(args.target_receipt, "target receipt")
    result_receipt_path, result_receipt = _json(args.result_receipt, "result receipt")
    result_path = _regular(args.result, "result artifact")
    if not is_complete(str(result_path)):
        raise SystemExit("[pet-v2-validate] result artifact completion marker invalid")
    arm_receipts = {}
    arm_paths = {}
    for arm in ARMS:
        arm_paths[arm], arm_receipts[arm] = _json(
            getattr(args, f"{arm.lower()}_receipt"), f"{arm} receipt")
    inputs = [proposal_path, target_path, result_receipt_path, result_path, *arm_paths.values()]
    # Include every payload named by receipts so validation proves it did not mutate them.
    for arm in ARMS:
        for info in arm_receipts[arm].get("artifacts", {}).values():
            payload_path = _regular(info["path"], f"{arm} payload")
            if not is_complete(str(payload_path)):
                raise SystemExit(f"[pet-v2-validate] invalid {arm} payload completion marker")
            inputs.append(payload_path)
    before = {str(path): sha256_file(path) for path in inputs}

    failures = []
    if proposal.get("contract_id") != CONTRACT_ID or proposal.get("status") != "AUTHORIZED_READY":
        failures.append("proposal is not AUTHORIZED_READY for the fixed contract")
    if proposal.get("launchable") is not True:
        failures.append("proposal launchable is not true")
    if proposal.get("authorization", {}).get("token") != AUTHORIZATION_TOKEN:
        failures.append("proposal authorization token mismatch")
    expected_prohibitions = {key: True for key in PROHIBITIONS}
    if proposal.get("governing_gate6", {}).get("prohibitions_applied") != expected_prohibitions:
        failures.append("proposal Gate-6 prohibitions drift")
    if target.get("status") != "PASS_TARGETS_AND_SPLIT" or target.get("contract_id") != CONTRACT_ID:
        failures.append("target receipt status/contract mismatch")
    if target.get("execution", {}).get("head") != args.expected_head:
        failures.append("target HEAD mismatch")
    if target.get("prohibitions_applied") != expected_prohibitions:
        failures.append("target prohibitions drift")
    for arm in ARMS:
        receipt = arm_receipts[arm]
        if receipt.get("status") != "PASS_ARM_COMPLETE" or receipt.get("arm") != arm:
            failures.append(f"{arm} receipt status/identity mismatch")
        if receipt.get("execution", {}).get("head") != args.expected_head:
            failures.append(f"{arm} HEAD mismatch")
        if receipt.get("prohibitions_applied") != expected_prohibitions:
            failures.append(f"{arm} prohibitions drift")
        for info in receipt.get("artifacts", {}).values():
            path = Path(info["path"]).resolve()
            if before.get(str(path)) != info.get("sha256"):
                failures.append(f"{arm} payload digest mismatch: {path}")
            if path.stat().st_size != int(info.get("size_bytes", -1)):
                failures.append(f"{arm} payload size mismatch: {path}")
    if result_receipt.get("schema") != "pet-v2-equivalence-result-v1" or \
            result_receipt.get("status") != "PASS_EVALUATION_COMPLETE":
        failures.append("result receipt status/schema mismatch")
    if result_receipt.get("existing_gate6_remains_blocked") is not True:
        failures.append("result does not explicitly preserve Gate-6 block")
    if result_receipt.get("prohibitions_applied") != expected_prohibitions:
        failures.append("result prohibitions drift")
    metrics = result_receipt.get("metrics", {})
    primary = {}
    for name, values in metrics.items():
        try:
            primary[name] = {key: float(values[key])
                             for key in ("D_same", "D_cross_max", "D_cross_min")}
        except (KeyError, TypeError, ValueError):
            failures.append(f"malformed primary metric {name}")
    reclassified = classify(primary, controls_valid=not failures)
    if reclassified != result_receipt.get("terminal_classification"):
        failures.append(
            f"terminal reclassification {reclassified} != recorded "
            f"{result_receipt.get('terminal_classification')}")
    if sha256_file(result_path) != result_receipt.get("artifact", {}).get("sha256"):
        failures.append("result artifact digest mismatch")
    with np.load(result_path, allow_pickle=True) as store:
        artifact_terminal = str(store["terminal_classification"].item())
        artifact_metrics = np.asarray(store["metrics"], dtype=object).item()
        if artifact_terminal != result_receipt.get("terminal_classification"):
            failures.append("result artifact/receipt terminal mismatch")
        if artifact_metrics != metrics:
            failures.append("result artifact/receipt metrics mismatch")

    after = {str(path): sha256_file(path) for path in inputs}
    mutated = {path: {"before": before[path], "after": after[path]}
               for path in before if before[path] != after[path]}
    if mutated:
        failures.append(f"validator input mutation detected: {mutated}")
    status = "PASS_READ_ONLY_VALIDATION" if not failures else "FAIL_INVALID_OR_INCOMPLETE"
    final_terminal = (result_receipt.get("terminal_classification") if not failures
                      else "INVALID_OR_NOISY")
    payload = {
        "schema": SCHEMA, "status": status, "terminal_classification": final_terminal,
        "contract_id": CONTRACT_ID,
        "execution": {"head": git_head(REPO), "host": socket.gethostname(),
                      "completed_at_utc": dt.datetime.now(dt.timezone.utc).isoformat()},
        "failures": failures, "reclassified_terminal": reclassified,
        "read_only_evidence": {"input_sha256_before": before,
                               "input_sha256_after": after, "mutated": mutated},
        "existing_gate6_remains_blocked": True,
        "prohibitions_applied": expected_prohibitions,
        "what_this_terminal_result_cannot_authorize": [
            *PROHIBITIONS, "interval coverage", "valid PET uncertainty", "ordinary closure",
            "C_stat", "C_ML", "total covariance", "central adoption", "publication claims",
            "coverage campaign", "larger family", "convergence tuning", "further compute"],
    }
    _write(output, payload)
    print(json.dumps({"status": status, "terminal": final_terminal,
                      "output": str(output)}, sort_keys=True))
    return 0 if not failures else 2


if __name__ == "__main__":
    raise SystemExit(main())
