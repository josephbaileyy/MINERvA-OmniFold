"""Controls for the reducer's added compute-cost reporting.

Joseph's endpoint is "a recommendation supported by matched learning results and
compute costs", and the reducer previously reported only closure. The cost block
added for that is **purely additive**: these controls exist to prove it, because a
reducer that silently changed a frozen acceptance criterion while adding a number
would be far worse than one that reported nothing.

The reducer runs after the matrix, on its output, rather than inside a job, so it
is validated here rather than in the launcher's gated suite. The in-job guards are
covered by ``test_stress_scope_and_geometry.py``, which does run on the cluster.

The fixture builds a complete, internally consistent 24-job matrix from scratch,
including per-job artifacts whose digests the reducer recomputes, so nothing is
stubbed past the checks under test.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any
import unittest

MODES = ("ordinary", "injected", "shuffle")
SEEDS = (17, 29, 43, 59, 71, 89, 101, 113)
ARTIFACTS = 6
FOOTING = {
    "code_sha256": {"nd-unfolding/pet/run_typed_token_comparison.py": "a" * 64},
    "input_sha256": "b" * 64,
    "truth_sha256": "c" * 64,
    "normalization_sha256": "d" * 64,
}


def load_reducer() -> Any:
    """Load the reducer by path, as its own repository test does."""
    path = Path(__file__).resolve().with_name("summarize_runs.py")
    spec = importlib.util.spec_from_file_location("comparison_summary", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def arm(*, rmse: float, fit_seconds: float, parameters: int = 17329) -> dict[str, Any]:
    """Build one route's trajectory that satisfies every frozen safeguard."""
    step = {
        "log_ratio_rmse": rmse,
        "normalization_ratio": 1.0,
        "ess": 1000.0,
        "target_ess": 1000.0,
        "tail_ess": 500.0,
        "tail_target_ess": 500.0,
        "truth_projections": {"0": {"relative_l1": 0.01}, "1": {"relative_l1": 0.01}},
        "cap_diagnostics": {"upper": {"count": 0, "ess": 1000.0}},
        "reco_fit_seconds": fit_seconds / 2,
        "truth_fit_seconds": fit_seconds / 2,
    }
    return {
        "parameters": parameters,
        "initial_reco_sha256": "e" * 64,
        "initial_truth_sha256": "f" * 64,
        "iterations": [dict(step), dict(step), dict(step)],
    }


def write_matrix(
    directory: Path, *, pooled_cost: float, direct_cost: float, gain_percent: float
) -> None:
    """Write a complete 24-job matrix whose injected arm shows a declared gain."""
    for mode in MODES:
        for seed in SEEDS:
            name = f"{mode}-{seed}"
            artifacts: dict[str, str] = {}
            for index in range(ARTIFACTS):
                filename = f"{name}-artifact-{index}.bin"
                payload = f"{name}:{index}".encode()
                (directory / filename).write_bytes(payload)
                artifacts[filename] = hashlib.sha256(payload).hexdigest()
            parent_rmse = 0.05
            child_rmse = (
                parent_rmse * (1 - gain_percent / 100)
                if mode == "injected"
                else parent_rmse
            )
            receipt = {
                "terminal": "COMPLETE",
                "mode": mode,
                "seed": seed,
                "training_rows": 1000000,
                "test_rows": 250000,
                "iterations": 3,
                "epochs_per_fit": 5,
                "batch_size": 1024,
                "wall_seconds": pooled_cost + direct_cost + 10.0,
                **FOOTING,
                "artifacts": artifacts,
                "results": {
                    "pooled": arm(rmse=parent_rmse, fit_seconds=pooled_cost),
                    "direct": arm(rmse=child_rmse, fit_seconds=direct_cost),
                },
            }
            (directory / f"{name}.json").write_text(json.dumps(receipt) + "\n")


class ComputeCostReporting(unittest.TestCase):
    """The cost block must appear, be correct, and change no frozen criterion."""

    module: Any

    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_reducer()

    def test_cost_block_is_reported_and_correct(self) -> None:
        """Per-arm totals and the paired ratio must match the fixture exactly."""
        import tempfile

        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            write_matrix(
                directory, pooled_cost=100.0, direct_cost=150.0, gain_percent=20.0
            )
            result = self.module.summarize(directory)
        compute = result["compute"]
        # 24 jobs, 3 iterations each, cost split evenly between the two fits.
        self.assertAlmostEqual(compute["pooled_fit_seconds_total"], 24 * 3 * 100.0)
        self.assertAlmostEqual(compute["direct_fit_seconds_total"], 24 * 3 * 150.0)
        self.assertAlmostEqual(compute["pooled_fit_seconds_median"], 3 * 100.0)
        self.assertAlmostEqual(compute["direct_fit_seconds_median"], 3 * 150.0)
        ratio = compute["paired_direct_over_pooled_ratio"]
        self.assertEqual(ratio["n"], 24)
        self.assertAlmostEqual(ratio["min"], 1.5)
        self.assertAlmostEqual(ratio["median"], 1.5)
        self.assertAlmostEqual(ratio["max"], 1.5)

    def test_frozen_criteria_still_decide_the_outcome(self) -> None:
        """A 20% paired gain passes; cost does not enter the decision."""
        import tempfile

        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            write_matrix(
                directory, pooled_cost=100.0, direct_cost=150.0, gain_percent=20.0
            )
            result = self.module.summarize(directory)
        self.assertEqual(result["decision"], "PASS_SYNTHETIC_ROUTING")
        self.assertTrue(result["checks"]["material_paired_gain"])
        self.assertTrue(result["checks"]["favorable_seeds"])

    def test_a_cheaper_arm_does_not_earn_a_pass(self) -> None:
        """The direction that matters: cost must never rescue a failing gain.

        Same fixture, no closure improvement, but the direct arm is ten times
        cheaper. If cost had leaked into the verdict this would pass.
        """
        import tempfile

        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            write_matrix(
                directory, pooled_cost=1000.0, direct_cost=100.0, gain_percent=0.0
            )
            result = self.module.summarize(directory)
        self.assertEqual(result["decision"], "NO_PASS")
        self.assertFalse(result["checks"]["material_paired_gain"])
        self.assertLess(
            result["compute"]["paired_direct_over_pooled_ratio"]["median"], 1.0
        )

    def test_incomplete_matrix_is_still_refused(self) -> None:
        """Removing one job must still fail closed, cost block or not."""
        import tempfile

        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            write_matrix(
                directory, pooled_cost=100.0, direct_cost=150.0, gain_percent=20.0
            )
            (directory / "injected-113.json").unlink()
            with self.assertRaises(FileNotFoundError):
                self.module.summarize(directory)

    def test_cost_is_absent_from_the_checks(self) -> None:
        """No check name may mention cost; the criteria stay closure-only."""
        import tempfile

        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            write_matrix(
                directory, pooled_cost=100.0, direct_cost=150.0, gain_percent=20.0
            )
            result = self.module.summarize(directory)
        for name in result["checks"]:
            self.assertNotIn("cost", name)
            self.assertNotIn("second", name)


if __name__ == "__main__":
    unittest.main()
