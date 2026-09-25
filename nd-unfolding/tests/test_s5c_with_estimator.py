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


if __name__ == "__main__":
    unittest.main()
