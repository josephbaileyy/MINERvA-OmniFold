#!/usr/bin/env python3
"""Exercise the bounded audit with synthetic readers and real forward checks.

No ROOT source is opened. Linux runs enforce the source-audit resource limits;
other platforms are local compatibility checks without Linux resource acceptance.
The optional ROOT import tests library coexistence only.
"""

from __future__ import annotations

import argparse
import copy
import importlib
import json
import math
import os
from pathlib import Path
import sys
from typing import Any, cast

import launch_typed_descriptor_source_audit as launcher

# The launcher sets CPU/thread environment variables before NumPy or TensorFlow.
import typed_descriptor_source_audit as audit
import typed_descriptor_source_smoke as source

FIXTURE = Path(__file__).resolve().parent / "runtime_fixtures/source_audit.json"


class SyntheticReader:
    """Supply synthetic numeric declarations and independent copies of fake rows."""

    def __init__(self, resolved: source.ResolvedSource) -> None:
        fixture = json.loads(FIXTURE.read_text())
        if fixture["kind"] != "SYNTHETIC_NOT_SOURCE_DATA":
            raise ValueError("Runtime preflight requires the synthetic fixture")
        self.rows = fixture["rows"]
        self.metadata = {
            "uuid": resolved.spec.expected_uuid,
            "tree": source.TREE_NAME,
            "entries": audit.ENTRY_STOP,
            "branches": {
                name: {
                    "dtype": "f8",
                    "shape": rule["shape"],
                    "declaration": "SYNTHETIC float64",
                }
                for name, rule in audit.branch_contract().items()
            },
            "producer_markers_verbatim": [],
            "publisher_checksum": None,
        }

    def read_entry(self, entry: int) -> dict[str, Any]:
        """Copy a synthetic row with a distinct fake event key; never read ROOT."""
        raw = copy.deepcopy(self.rows[entry % len(self.rows)])
        raw["ev_gate"] = entry
        return cast(dict[str, Any], raw)

    def close(self) -> None:
        """Satisfy the reader lifecycle without opening a file handle."""


def check_activation_accuracy() -> dict[str, float]:
    """Measure the elementary activation allowance on a fixture-independent grid."""
    import numpy as np

    tf = importlib.import_module("tensorflow")
    values = np.concatenate(
        (
            np.linspace(-20, 20, 20001, dtype=np.float32),
            np.array([-1e-30, 0, 1e-30], dtype=np.float32),
        )
    )
    oracle = np.array([math.tanh(float(value)) for value in values])
    errors = {
        name: float(np.max(np.abs(actual - oracle)))
        for name, actual in (
            ("numpy", np.tanh(values)),
            ("keras_tensorflow", tf.math.tanh(values).numpy()),
        )
    }
    if any(
        not math.isfinite(error) or error > audit.ACTIVATION_ATOL
        for error in errors.values()
    ):
        raise AssertionError("Elementary tanh accuracy exceeds activation allowance")
    return errors


def main() -> int:
    """Run the complete fake-reader audit and report measured runtime resources."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--with-root", action="store_true")
    args = parser.parse_args()
    launcher.check_preparation()
    budget = launcher.RuntimeBudget() if sys.platform == "linux" else None
    initialized = False
    forward = None
    versions: dict[str, str] = {}
    activation_errors: dict[str, float] = {}

    def record_versions() -> None:
        for name in ("numpy", "scipy", "tensorflow", "keras", "ROOT"):
            module = sys.modules.get(name)
            if module is not None:
                versions[name] = str(getattr(module, "__version__", "UNKNOWN"))

    record_versions()

    def resources() -> None:
        nonlocal initialized
        if not initialized:
            initialized = True
            if budget is not None:
                budget.install()
            if args.with_root:
                importlib.import_module("ROOT")
                record_versions()
        if budget is not None:
            budget.check()

    def check_forward(batch: source.SourceContractBatch) -> None:
        nonlocal forward
        try:
            if forward is None:
                forward = audit.ForwardCheck()
                activation_errors.update(check_activation_accuracy())
            forward(batch)
        finally:
            record_versions()
            resources()

    receipt = audit.run_audit(
        launcher.REPO_ROOT,
        args.output,
        reader_factory=SyntheticReader,
        forward_check=check_forward,
        check_resources=resources,
        bindings={
            "execution_mode": "SYNTHETIC_FAKE_READER_NOT_SOURCE_EVIDENCE",
            "versions": versions,
            "TF_ENABLE_ONEDNN_OPTS": os.environ.get("TF_ENABLE_ONEDNN_OPTS"),
            "fixture_sha256": launcher.digest_file(FIXTURE),
            "probe_sha256": launcher.digest_file(Path(__file__)),
            "preparation_sha256": launcher.digest_file(launcher.BINDING_FILE),
            "linux_resource_limits_enforced": budget is not None,
            "root_library_import_requested": args.with_root,
            "root_source_opens": 0,
        },
    )
    summary = {
        "kind": "SYNTHETIC_RUNTIME_ONLY",
        "terminal": receipt["terminal"],
        "mapping": receipt["mapping"],
        "versions": versions,
        "linux_resource_limits_enforced": budget is not None,
        "peak_observed_threads": budget.peak_threads if budget else None,
        "peak_observed_rss_bytes": budget.peak_rss if budget else None,
        "source_execution_authorized": False,
        "activation_grid_max_absolute_errors": activation_errors,
        "numerical_checks_first_chunk": forward.numerical_checks if forward else [],
    }
    (args.output / "runtime-summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(summary, sort_keys=True))
    return 0 if receipt["terminal"] == "COMPLETE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
