"""s5n controls that need the analysis environment (LightGBM and the driver's ROOT-importing module).

Run on Perlmutter after `source setup_salloc_env.sh`; skipped where either is unavailable. Contract
control C2 on a synthetic signed sample: the successor calls the driver's own refine_stay_positive
(there is no second implementation), the F2 parameters reach the classifier, the refinement is
bitwise reproducible and seed-inert, and the refined weights preserve the signed total to the
classifier's calibration."""
import importlib.util
import sys
import unittest
from pathlib import Path

import numpy as np

ND = Path(__file__).resolve().parents[1]
sys.path.insert(1, str(ND))
HAVE = importlib.util.find_spec("lightgbm") is not None and importlib.util.find_spec("ROOT") is not None


@unittest.skipUnless(HAVE, "needs lightgbm and ROOT (the analysis environment)")
class Refinement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import s5n_pseudo

        cls.s5n = s5n_pseudo
        rng = np.random.default_rng(11)
        n_d, n_b = 40_000, 6_000
        data = rng.normal(0.0, 1.0, (n_d, 5))
        bkg = rng.normal(1.0, 0.7, (n_b, 5))
        cls.feat = np.concatenate([data, bkg])
        cls.w = np.concatenate([np.ones(n_d), -np.full(n_b, 0.5)])

    def test_calls_the_driver_function_with_the_f2_parameters(self):
        u2d = self.s5n.load_u2d()
        self.assertTrue(Path(u2d.__file__).resolve().is_relative_to(ND.parent))
        w_ref, ev = self.s5n.refine(self.feat, self.w, 42, 4)
        p = ev["classifier_params"]
        self.assertEqual((p["random_state"], p["deterministic"], p["force_row_wise"], p["num_threads"]), (45, True, True, 4))
        self.assertEqual(p["n_estimators"], 100)
        self.assertEqual(p["num_leaves"], 8)
        self.assertTrue(np.all(w_ref >= 0))
        self.assertLess(abs(ev["refined_over_signed"] - 1.0), 0.02)
        direct, _, _ = u2d.refine_stay_positive(self.feat, self.w, estimator="lgbm", device="cpu",
                                                params=self.s5n.refine_params(42, 4))
        np.testing.assert_array_equal(w_ref, direct)

    def test_bitwise_reproducible_and_seed_inert(self):
        a, _ = self.s5n.refine(self.feat, self.w, 42, 4)
        b, _ = self.s5n.refine(self.feat, self.w, 42, 4)
        c, _ = self.s5n.refine(self.feat, self.w, 43, 4)
        np.testing.assert_array_equal(a, b)
        np.testing.assert_array_equal(a, c)

    def test_the_bare_driver_parameters_differ(self):
        """Innocent-neighbour control: the driver's own call (random_state only) is a different
        classifier configuration, so the parameter check is not vacuous."""
        u2d = self.s5n.load_u2d()
        clf = u2d._make_bkg_classifier("lgbm", {"random_state": 45}, "cpu")
        self.assertNotEqual(clf.get_params().get("deterministic"), True)


if __name__ == "__main__":
    unittest.main()
