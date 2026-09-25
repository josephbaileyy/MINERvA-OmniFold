"""Controls for s5c_with_estimator's permutation layer (no LightGBM needed)."""
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(1, str(Path(__file__).resolve().parents[1]))
import s5c_with_estimator as swe  # noqa: E402


def fake_loop(MCgen, MCreco, measured, pass_reco, pass_truth, meas_pass_reco, iters, kind=None,
              MCgen_weights=None, MCreco_weights=None, measured_weights=None, **_):
    sel = np.asarray(pass_truth)
    # row-wise, plus a data-dependent global scale that is order-invariant
    scale = float(np.sum(measured_weights[meas_pass_reco])) if measured_weights is not None else 1.0
    pull = MCgen[sel, 0] * MCgen_weights[sel] * scale
    push = MCreco[sel, 1] + MCreco_weights[sel] + iters
    return pull, push


class Permutation(unittest.TestCase):
    def test_restores_original_row_order(self):
        rng = np.random.default_rng(0)
        n, nd = 1000, 300
        args = (rng.random((n, 5)), rng.random((n, 5)), rng.random((nd, 5)), rng.random(n) < 0.7,
                rng.random(n) < 0.9, np.ones(nd, bool), 5)
        kw = dict(kind="lgbm", MCgen_weights=rng.random(n), MCreco_weights=rng.random(n), measured_weights=rng.random(nd))
        ref = fake_loop(*args, **kw)
        record = []
        got = swe.permuted(fake_loop, 7, record, "test")(*args, **dict(kw))
        for r, g in zip(ref, got):
            np.testing.assert_allclose(g, r, rtol=1e-12)
        self.assertEqual(record[0]["kind"], "permutation")

    def test_a_wrong_inverse_would_be_caught(self):
        rng = np.random.default_rng(1)
        n = 50
        args = (rng.random((n, 5)), rng.random((n, 5)), rng.random((20, 5)), np.ones(n, bool),
                np.ones(n, bool), np.ones(20, bool), 1)
        kw = dict(MCgen_weights=np.ones(n), MCreco_weights=np.ones(n), measured_weights=np.ones(20))
        ref = fake_loop(*args, **kw)
        # the permuted loop's raw output (without restoring order) differs from the reference
        pm = np.random.default_rng(7).permutation(n)
        raw = fake_loop(args[0][pm], args[1][pm], args[2], args[3], args[4], args[5], 1, **kw)
        self.assertFalse(np.allclose(raw[0], ref[0]))


class Refinement(unittest.TestCase):
    """The s5n successor: the refinement classifier must carry the configuration, and a
    negweight-refined target that never refines must fail verification."""

    class FakeClf:
        def __init__(self, **params):
            self.params = params

        def get_params(self):
            return dict(self.params)

    def fake_u2d(self):
        import types

        mod = types.SimpleNamespace()

        def make(estimator, params, device):
            return self.FakeClf(n_estimators=100, num_leaves=8, learning_rate=0.1, verbose=-1, **(params or {}))

        def refine(feat, signed_w, estimator="exact", device="cpu", params=None, verbose=False):
            mod._make_bkg_classifier(estimator, params, device)
            g = np.where(np.asarray(signed_w) > 0, 0.8, 0.4)
            return np.abs(signed_w) * np.clip(2 * g - 1, 0, None), g, 0.0

        mod._make_bkg_classifier = make
        mod.refine_stay_positive = refine
        return mod

    def test_configuration_reaches_the_refinement_classifier(self):
        extra = {"deterministic": True, "num_threads": 4}
        record, mod = [], self.fake_u2d()
        swe.install_refinement(extra, record, u2d=mod)
        mod.refine_stay_positive(np.zeros((3, 2)), np.array([1.0, 1.0, -0.5]), estimator="lgbm",
                                 params={"random_state": 45})
        self.assertEqual(record[0]["params"][0]["deterministic"], True)
        self.assertEqual(record[0]["params"][0]["random_state"], 45)
        self.assertEqual(swe.verify(extra, record, ["drv.py", "--bkg-mode", "negweight-refined"]), [])
        self.assertAlmostEqual(record[0]["evidence"]["signed_sum"], 1.5)

    def test_negweight_target_without_a_refinement_fails_and_purity_target_does_not(self):
        extra = {"deterministic": True}
        loop_call = [{"site": "omnifold.omnifold", "kind": "lgbm", "params": [dict(extra)] * 3}]
        self.assertTrue(swe.verify(extra, loop_call, ["drv.py", "--bkg-mode=negweight-refined"]))
        self.assertEqual(swe.verify(extra, loop_call, ["drv.py", "--bkg-mode", "purity"]), [])

    def test_a_classifier_missing_the_configuration_is_caught(self):
        extra = {"deterministic": True}
        record = [{"site": "unfold_2d_omnifold_unbinned.refine_stay_positive", "kind": "lgbm",
                   "params": [{"random_state": 45}]}]
        self.assertTrue(swe.verify(extra, record, ["drv.py", "--bkg-mode", "negweight-refined"]))


if __name__ == "__main__":
    unittest.main()
