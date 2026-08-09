import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

import numpy as np


SCRIPT = Path(__file__).resolve().parents[1] / "pet" / "diagnose_step1_iteration_dynamics.py"
LAUNCHER = Path(__file__).resolve().parents[1] / "pet" / "sbatch_step1_iteration_dynamics_array.sh"
spec = importlib.util.spec_from_file_location("step1_dynamics", SCRIPT)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


class Step1DynamicsTests(unittest.TestCase):
    def test_metrics_rederive_required_ratio_and_sign(self):
        push = np.array([1.0, 2.0, 1.0])
        increment = np.array([0.5, 0.5, 1.5])
        pull = push * increment
        w = np.ones(3)
        mask = np.array([True, True, False])
        got = mod.step1_metrics(push, pull, w, mask, R=2.0, cap=30.0)
        self.assertAlmostEqual(got["push_prev_mean_w_reco"], 1.5)
        self.assertAlmostEqual(got["r1_mean_w_reco"], 0.5)
        self.assertAlmostEqual(got["r1_required_mean"], 4.0 / 3.0)
        self.assertTrue(got["correction_sign_is_wrong"])

    def test_metrics_fail_closed_on_alignment_or_zero_push(self):
        with self.assertRaises(ValueError):
            mod.step1_metrics([1], [1, 2], [1], [True], 1.1, 30)
        with self.assertRaises(ValueError):
            mod.step1_metrics([0], [1], [1], [True], 1.1, 30)

    def test_atomic_json_replaces_and_parses(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "r.json"
            mod.atomic_json(p, {"schema": mod.SCHEMA, "status": "COMPLETE"})
            import json
            self.assertEqual(json.loads(p.read_text())["status"], "COMPLETE")

    def test_three_factorial_arms_are_declared(self):
        self.assertEqual(set(mod.ARMS), {
            "warm_fresh_split", "cold_fixed_split", "cold_fresh_split"
        })

    def test_wrapper_does_not_edit_shared_engine(self):
        src = SCRIPT.read_text()
        self.assertIn("omnifold.MultiFold = DynamicsMultiFold", src)
        self.assertIn('"shared_engine_edited": False', src)
        self.assertNotIn("write_text", src)

    def test_launcher_is_parallel_and_collision_isolated(self):
        src = LAUNCHER.read_text()
        self.assertIn("#SBATCH --array=0-2%3", src)
        self.assertIn('slurm-${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}', src)
        self.assertIn('[[ ! -e "$WEIGHTS"', src)
        self.assertIn('EXPECTED_WRAPPER="831117d84866', src)
        self.assertNotIn("scancel", src)


if __name__ == "__main__":
    unittest.main()
