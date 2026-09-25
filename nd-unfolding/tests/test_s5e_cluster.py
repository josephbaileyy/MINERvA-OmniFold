"""s5e controls that need the analysis environment (LightGBM; ROOT for the refinement).

Run on Perlmutter after `source setup_salloc_env.sh`; skipped where unavailable. With REAL LightGBM
estimators in the F2 configuration: tracing leaves the unfold bitwise unchanged and its per-iteration
rebuild passes every check; the capacity and per-estimator-seed probes reach the estimators; the
refinement override reaches the refinement classifier."""
import importlib.util
import sys
import unittest
from pathlib import Path

import numpy as np

ND = Path(__file__).resolve().parents[1]
sys.path.insert(1, str(ND))
sys.path.insert(1, str(ND / "tests"))
HAVE_LGBM = importlib.util.find_spec("lightgbm") is not None
HAVE_ROOT = importlib.util.find_spec("ROOT") is not None


@unittest.skipUnless(HAVE_LGBM, "needs lightgbm (the analysis environment)")
class TracedLightGBM(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import s5c_unfold
        import s5e_trace
        from test_s5e_trace import SHAPE, toy_inputs

        cls.su, cls.st = s5c_unfold, s5e_trace
        inp = toy_inputs(n=20000, seed=4)
        r = 1.0 + 0.3 * (inp["MCgen"][:, 2] > 1.0)
        cls.unf_in, _ = s5e_trace.asimov_same(inp, r)
        cls.r = r
        cls.U = np.random.default_rng(3).uniform(size=(5, int(np.prod(SHAPE))))

    def run_traced(self, iters, **kw):
        rec = self.st.Recorder(self.unf_in, self.r, self.U, iters)
        return self.st.traced_unfold(self.unf_in, rec, 42, 4, iters, **kw), rec

    def test_tracing_is_bitwise_invisible_with_lightgbm(self):
        ref, _ = self.su.unfold(self.unf_in, "deterministic", 42, 4, 3)
        (xs, params, tracer), _ = self.run_traced(3)
        np.testing.assert_array_equal(xs, ref)
        self.assertEqual(tracer.checks, {"step1_mc_weights": 3, "step2_pull_weights": 3})
        self.assertTrue(all(p["deterministic"] for p in params))

    def test_probes_reach_the_estimators(self):
        (xs, params, _), _ = self.run_traced(1, capacity=(400, 31), seed_per_estimator=True)
        self.assertEqual([p["n_estimators"] for p in params], [400] * 3)
        self.assertEqual([p["num_leaves"] for p in params], [31] * 3)
        self.assertEqual([p["random_state"] for p in params], [42, 43, 44])


@unittest.skipUnless(HAVE_LGBM and HAVE_ROOT, "needs lightgbm and ROOT (the analysis environment)")
class RefinementOverride(unittest.TestCase):
    def test_override_reaches_the_refinement_classifier(self):
        import s5e_trace

        rng = np.random.default_rng(11)
        feat = np.concatenate([rng.normal(0, 1, (20000, 5)), rng.normal(1, 0.7, (3000, 5))])
        w = np.concatenate([np.ones(20000), -np.full(3000, 0.5)])
        w_ref, ev = s5e_trace.refine_variant(feat, w, 42, 4, {"n_estimators": 400, "num_leaves": 31})
        self.assertEqual(ev["classifier_params"]["n_estimators"], 400)
        self.assertEqual(ev["classifier_params"]["num_leaves"], 31)
        self.assertEqual(ev["classifier_params"]["random_state"], 45)
        self.assertTrue(np.all(w_ref >= 0))


if __name__ == "__main__":
    unittest.main()
