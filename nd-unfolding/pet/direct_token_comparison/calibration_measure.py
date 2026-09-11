"""Measure the frozen synthetic calibration on one allocated A100."""

from __future__ import annotations

import argparse
import cProfile
import importlib
import json
import os
import platform
import shutil
import subprocess
from pathlib import Path
import resource
import sys
import time
from typing import Any
from unittest.mock import patch

PET_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PET_ROOT))

import run_typed_token_comparison as comparison  # noqa: E402
import typed_descriptor_keras as adapter  # noqa: E402


def runtime_versions() -> dict[str, str]:
    """Check versions of guarded imports without distribution-discovery hooks."""
    versions = {
        name: str(importlib.import_module(name).__version__)
        for name in ("numpy", "tensorflow", "keras", "scipy", "pytest")
    }
    expected = {
        "numpy": "1.26.4",
        "tensorflow": "2.16.2",
        "keras": "3.15.1",
        "scipy": "1.16.3",
        "pytest": "9.1.1",
    }
    if versions != expected:
        raise RuntimeError(f"Environment mismatch: {versions}")
    return versions


def main() -> None:
    """Check the runtime and device, then call the unchanged calibration runner."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--tests-only", action="store_true")
    parser.add_argument("--include-source-smoke-tests", action="store_true")
    parser.add_argument("--runtime-versions-only", action="store_true")
    args = parser.parse_args()
    if args.runtime_versions_only:
        args.output.write_text(json.dumps(runtime_versions(), indent=2) + "\n")
        return
    if args.tests_only:
        # NumPy's optional SVE probe launches lscpu. This test dependency falls
        # back on OSError; use that fallback without launching an unmodeled tool.
        # SVE is inapplicable on x86_64; an absent lscpu has the same fallback.
        if platform.machine() != "x86_64" and shutil.which("lscpu") is not None:
            raise RuntimeError("Optional SVE probe cannot be disabled on this platform")
        guarded_run = subprocess.run

        def without_optional_probe(
            command: Any, *positional: Any, **keywords: Any
        ) -> Any:
            if command == "lscpu":
                raise FileNotFoundError("Optional SVE probe disabled for these tests")
            return guarded_run(command, *positional, **keywords)

        with patch("subprocess.run", side_effect=without_optional_probe):
            importlib.import_module("numpy.testing")

        import pytest

        root = PET_ROOT.parent / "tests"
        names = [
            "test_typed_descriptors.py",
            "test_typed_descriptor_keras.py",
            "test_typed_descriptor_compatibility.py",
            "test_prong_semantics.py",
            "test_typed_token_comparison.py",
        ]
        if args.include_source_smoke_tests:
            names.append("test_typed_descriptor_source_smoke.py")
        raise SystemExit(
            pytest.main(
                [
                    "-q",
                    *[str(root / name) for name in names],
                ]
            )
        )
    args.output.mkdir(exist_ok=False)
    started = time.monotonic()
    affinity = sorted(os.sched_getaffinity(0))
    if len(affinity) < 8:
        raise RuntimeError("Fewer than eight CPUs available to the application")
    os.sched_setaffinity(0, set(affinity[:8]))
    versions = runtime_versions()
    tf = adapter.require_tensorflow()
    tf.config.threading.set_intra_op_parallelism_threads(7)
    tf.config.threading.set_inter_op_parallelism_threads(1)
    tf.config.experimental.enable_op_determinism()
    devices = tf.config.list_physical_devices("GPU")
    if len(devices) != 1:
        raise RuntimeError(f"Expected one visible GPU, observed {devices}")
    details = tf.config.experimental.get_device_details(devices[0])
    if "A100" not in details.get("device_name", ""):
        raise RuntimeError(f"Expected A100, observed {details}")
    tf.config.experimental.set_memory_growth(devices[0], True)
    with tf.device("/GPU:0"):
        product = tf.linalg.matmul(tf.ones((2, 2)), tf.ones((2, 2)))
    if "GPU:0" not in product.device or float(tf.reduce_sum(product)) != 8.0:
        raise RuntimeError("GPU operation validation failed")
    environment: dict[str, Any] = {
        "versions": versions,
        "python": sys.version,
        "gpu_details": details,
        "tensorflow_build": tf.sysconfig.get_build_info(),
        "initial_cpu_affinity": affinity,
        "application_cpu_affinity": sorted(os.sched_getaffinity(0)),
        "gpu_operation_device": product.device,
    }
    (args.output / "environment.json").write_text(json.dumps(environment, indent=2))
    print(json.dumps({"phase": "GPU_RUNTIME_PASS", "versions": versions}), flush=True)
    run_args = argparse.Namespace(
        rows=32768,
        test_rows=8192,
        seed=17,
        mode="injected",
        epochs=1,
        iterations=1,
        batch_size=1024,
        output=args.output / "calibration.json",
    )
    profiler = cProfile.Profile()
    receipt = profiler.runcall(comparison.run, run_args)
    profiler.dump_stats(str(args.output / "calibration.pstats"))
    run_args.output.write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n")
    measurement = {
        "terminal": "COMPLETE",
        "wall_seconds": time.monotonic() - started,
        "peak_rss_KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "gpu_memory": tf.config.experimental.get_memory_info("GPU:0"),
        "scope": "calibration and runtime validation only; excluded from the seed matrix",
    }
    (args.output / "measurement.json").write_text(json.dumps(measurement, indent=2))
    print(json.dumps(measurement), flush=True)


if __name__ == "__main__":
    main()
