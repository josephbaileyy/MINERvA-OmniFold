from pathlib import Path
import unittest


PET = Path(__file__).resolve().parents[1] / "pet"
WRAPPER = PET / "diagnose_step1_annealed_lr.py"
LAUNCHER = PET / "sbatch_step1_annealed_lr.sh"


class AnnealedLRTests(unittest.TestCase):
    def test_fit_time_compile_forces_fixed_only_after_iteration_zero(self):
        src = WRAPPER.read_text()
        self.assertIn("self._inside_fit_compile and self._diag_iteration > self.start", src)
        self.assertIn("effective_fixed = True", src)
        self.assertIn("expected = 1e-4 if rec[\"iteration\"] == 0 else 1e-5", src)

    def test_shared_engine_is_monkeypatched_not_edited(self):
        src = WRAPPER.read_text()
        self.assertIn("omnifold.MultiFold = AnnealedMultiFold", src)
        self.assertIn('"shared_engine_edited": False', src)
        self.assertNotIn("write_text", src)

    def test_arm_is_warm_fixed_except_lr(self):
        src = WRAPPER.read_text()
        self.assertIn('ARM = "warm_fixed_annealed_lr"', src)
        self.assertIn('"step1_model_reset_after_iteration0": False', src)
        self.assertIn('"step1_fresh_split_after_iteration0": False', src)
        self.assertIn('"anneal_applies_to_steps": [1, 2]', src)

    def test_launcher_is_collision_isolated_and_pinned(self):
        src = LAUNCHER.read_text()
        self.assertIn('warm_fixed_annealed_lr/slurm-${SLURM_JOB_ID}', src)
        self.assertIn('[[ ! -e "$WEIGHTS"', src)
        self.assertIn('EXPECTED_WRAPPER="fa4ad80aee1457', src)
        self.assertNotIn("--array", src)
        self.assertNotIn("scancel", src)


if __name__ == "__main__":
    unittest.main()
