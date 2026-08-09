from pathlib import Path
import unittest


PET = Path(__file__).resolve().parents[1] / "pet"
ARRAY = PET / "sbatch_step1_iteration_dynamics_array_r2.sh"
LR = PET / "sbatch_step1_annealed_lr_r2.sh"


class Step1RetryLauncherTests(unittest.TestCase):
    def test_changed_retry_declares_import_path_and_preflight(self):
        for path in (ARRAY, LR):
            src = path.read_text()
            self.assertIn('export PYTHONPATH="${REPO}/omnifold_nn', src)
            self.assertIn("python3 -c 'import omnifold, omnifold.omnifold'", src)
            self.assertIn("import preflight failed", src)

    def test_scientific_inputs_remain_pinned(self):
        for path in (ARRAY, LR):
            src = path.read_text()
            self.assertIn('EXPECTED_DRIVER="66aa1f8f62087', src)
            self.assertIn('EXPECTED_LOADER="57f33f87b07e', src)
            self.assertIn('EXPECTED_ENGINE="3a2022b0809f', src)
            self.assertIn('EXPECTED_TARGET="544b2f6a2451', src)
            self.assertIn('EXPECTED_TARGET_RECEIPT="336e8e27fc8a', src)
            self.assertIn('EXPECTED_GATE3="306e54596802', src)

    def test_retries_remain_collision_isolated(self):
        self.assertIn('slurm-${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}', ARRAY.read_text())
        self.assertIn('warm_fixed_annealed_lr/slurm-${SLURM_JOB_ID}', LR.read_text())
        for path in (ARRAY, LR):
            src = path.read_text()
            self.assertIn('[[ ! -e "$WEIGHTS"', src)
            self.assertNotIn("scancel", src)


if __name__ == "__main__":
    unittest.main()
