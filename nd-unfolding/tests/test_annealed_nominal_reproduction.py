import importlib.util
import json
import os
import tempfile
import unittest

import numpy as np


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PET = os.path.join(ROOT, "pet")
EVALUATOR_PATH = os.path.join(PET, "evaluate_annealed_nominal_reproduction.py")
SPEC = importlib.util.spec_from_file_location("annealed_nominal_reproduction", EVALUATOR_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class AnnealedNominalReproductionTest(unittest.TestCase):
    def artifact(self, directory, deviation, bad_schedule=False):
        path = os.path.join(directory, "artifact.npz")
        lr = {
            "verified_from_optimizer": True,
            "base_lr": 1e-4,
            "annealed_lr": 1e-5,
            "n_fits_base_lr": 2,
            "n_fits_annealed": 4,
            "fits": [
                {"iteration": i, "learning_rate": 1e-4 if i == 0 or bad_schedule else 1e-5}
                for i in (0, 0, 1, 1, 2, 2)
            ],
        }
        seed = {
            "lr_policy": {
                "schedule": "fit-time-anneal-after-iteration-0",
                "base_lr": 1e-4,
                "annealed_lr": 1e-5,
                "applies_from_iteration": 1,
            }
        }
        np.savez_compressed(
            path,
            fold_forward_sum_w_push_reco=np.asarray(1.0 + deviation),
            fold_forward_sum_w_reco=np.asarray(1.0),
            step1_class_ratio=np.asarray(1.0),
            seed_policy=np.asarray(seed, dtype=object),
            lr_policy_realized=np.asarray(lr, dtype=object),
        )
        with open(path + ".done", "w") as stream:
            json.dump({"output": path}, stream)
        return path

    def test_predeclared_band(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(MODULE.evaluate(self.artifact(directory, -0.011724))["fold_forward"]["verdict"],
                             "REPRODUCED")

    def test_disagreement_is_a_finding(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(MODULE.evaluate(self.artifact(directory, -0.04))["fold_forward"]["verdict"],
                             "FINDING_CODE_PATHS_DISAGREE")

    def test_realized_schedule_is_required(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(RuntimeError, "lr_policy_realized"):
                MODULE.evaluate(self.artifact(directory, -0.011724, bad_schedule=True))


if __name__ == "__main__":
    unittest.main()
