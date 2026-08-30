#!/usr/bin/env python3
"""Run the GAP-3 changed retry with the original scientific audit core."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys
from types import ModuleType


CONTRACT_ID = "PET-G6-GAP3-RECO-TRUNCATION-20260830-CHANGED-RETRY1"
THREADS = 18
CORE_RELATIVE_PATH = Path("nd-unfolding/pet/audit_reco_truncation.py")
PREDECLARATION_RELATIVE_PATH = Path(
    "docs/orchestration/"
    "PREDECLARATION-20260830-gate6-gap3-reco-truncation-changed-retry1.md"
)
PROPOSAL_RELATIVE_PATH = Path(
    "docs/orchestration/state/"
    "gate6-gap3-reco-truncation-changed-retry1-proposal-20260830.json"
)


def _load_core(code_root: Path) -> ModuleType:
    """Load the hash-bound original audit core from the supplied checkout."""
    core_path = code_root / CORE_RELATIVE_PATH
    spec = importlib.util.spec_from_file_location("gap3_original_audit_core", core_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import audit core: {core_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _verify_retry_artifacts(args: argparse.Namespace, core: ModuleType) -> None:
    """Verify the retry-only wrapper and proposal before source inspection."""
    code_root = args.code_root.resolve()
    bindings = {
        "changed-retry wrapper": (
            Path(__file__).resolve(),
            args.expected_wrapper_sha256,
        ),
        "changed-retry proposal": (
            code_root / PROPOSAL_RELATIVE_PATH,
            args.expected_proposal_sha256,
        ),
    }
    for label, (path, expected) in bindings.items():
        if not path.is_file():
            raise FileNotFoundError(f"missing {label}: {path}")
        actual = core.sha256_file(path)
        if actual != expected:
            raise RuntimeError(f"{label} SHA-256 mismatch: {actual} != {expected}")


def _enrich_result(
    args: argparse.Namespace,
    core: ModuleType,
    status_code: int,
) -> None:
    """Attach retry-only provenance without changing scientific operands."""
    output = args.output.resolve()
    if not output.is_file():
        return
    payload = json.loads(output.read_text(encoding="utf-8"))
    payload["contract_id"] = CONTRACT_ID
    payload["changed_retry"] = {
        "number": 1,
        "status_code": status_code,
        "threads": THREADS,
        "wrapper_sha256": args.expected_wrapper_sha256,
        "proposal_sha256": args.expected_proposal_sha256,
        "scientific_core": str(CORE_RELATIVE_PATH),
        "scientific_core_sha256": args.expected_audit_sha256,
        "scientific_operands_changed": False,
        "automatic_retry": False,
        "further_retry_authorized": False,
    }
    core._write_json_atomic(output, payload)


def parse_args() -> argparse.Namespace:
    """Parse the immutable changed-retry command line."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--code-root", type=Path, required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expected-head", required=True)
    parser.add_argument("--expected-audit-sha256", required=True)
    parser.add_argument("--expected-wrapper-sha256", required=True)
    parser.add_argument("--expected-predeclaration-sha256", required=True)
    parser.add_argument("--expected-proposal-sha256", required=True)
    parser.add_argument("--expected-guard-sha256", required=True)
    parser.add_argument("--threads", type=int, default=THREADS)
    args = parser.parse_args()
    if args.threads != THREADS:
        parser.error(f"the changed retry requires exactly {THREADS} threads")
    args.predeclaration_relative_path = PREDECLARATION_RELATIVE_PATH
    return args


def main() -> int:
    """Execute the original scientific audit under the changed resource contract."""
    args = parse_args()
    core = _load_core(args.code_root.resolve())
    _verify_retry_artifacts(args, core)
    core.CONTRACT_ID = CONTRACT_ID
    status_code = core.run(args)
    _enrich_result(args, core, status_code)
    return status_code


if __name__ == "__main__":
    raise SystemExit(main())
