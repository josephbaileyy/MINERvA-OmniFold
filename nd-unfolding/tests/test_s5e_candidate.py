"""Controls for the s5e withheld multi-dimensional deformations and the candidate wrapper (no LightGBM)."""
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(1, str(Path(__file__).resolve().parents[1]))
import s5e_deform as sd  # noqa: E402
import s5n_pseudo  # noqa: E402
from test_s5e_trace import EDGES, toy_inputs  # noqa: E402


def ratio_2d(rho):
    return {"schema": "s5e-shape-ratio/1", "axes": [2, 4], "edges": [EDGES[2].tolist(), EDGES[4].tolist()],
            "shape_ratio": np.asarray(rho, float).ravel().tolist()}


class RatioWeight(unittest.TestCase):
    def setUp(self):
        self.inp = toy_inputs(n=5000)
        self.inp["MCgen"][:30, 4] = -9999.0
        self.rho = np.array([[1.3, 0.8], [1.0, 1.2], [0.7, 1.5]])

    def test_pure_shape_outside_rows_untouched(self):
        g, w = self.inp["MCgen"], self.inp["w_truth"]
        r = sd.ratio_weight(g, EDGES, w, ratio_2d(self.rho), 1.0)
        np.testing.assert_array_equal(r[:30], 1.0)
        ok = r != 1.0
        self.assertAlmostEqual((w[30:] * r[30:]).sum() / w[30:].sum(), 1.0, places=12)
        ie = np.searchsorted(EDGES[2], g[ok, 2], side="right") - 1
        iw = np.searchsorted(EDGES[4], g[ok, 4], side="right") - 1
        const = r[ok] / self.rho[ie, iw]
        self.assertLess(np.ptp(const), 1e-12)

    def test_wrong_edges_and_nonpositive_refused(self):
        bad = ratio_2d(self.rho)
        bad["edges"][1] = [0.0, 2.0, 9.0]
        with self.assertRaises(ValueError):
            sd.ratio_weight(self.inp["MCgen"], EDGES, self.inp["w_truth"], bad, 1.0)
        with self.assertRaises(ValueError):
            sd.ratio_weight(self.inp["MCgen"], EDGES, self.inp["w_truth"], ratio_2d(-self.rho), 1.0)

    def test_contents_rules_empty_cells_and_clip(self):
        num = np.array([[1.0, 0.0], [1.2, 5.0]])
        den = np.array([[1.0, 1.0], [1.0, 0.4]])  # rho = 0.333, -, 0.4, 4.17
        rho, st = sd.ratio_from_contents(num, den, np.ones((2, 2)))
        self.assertEqual(rho[0, 1], 1.0)
        self.assertEqual(st["cells_without_shape_information"], 1)
        self.assertEqual(rho[1, 1], 4.0)
        self.assertEqual(st["cells_clipped"], 1)


class CandidateWrapper(unittest.TestCase):
    def setUp(self):
        self.saved = (s5n_pseudo.refine_params, s5n_pseudo.code_digests, s5n_pseudo.truth_weight, s5n_pseudo.TRUTHS)

    def tearDown(self):
        s5n_pseudo.refine_params, s5n_pseudo.code_digests, s5n_pseudo.truth_weight, s5n_pseudo.TRUTHS = self.saved

    def test_candidate_r_override_reaches_the_verified_refinement(self):
        import s5e_candidate

        s5e_candidate.install("R")
        seen = []

        def fake_refine(feat, w, params):
            seen.append(params)
            return np.abs(w), np.full(w.size, 0.9), 0.0

        w_ref, ev = s5n_pseudo.refine(np.zeros((4, 5)), np.array([1.0, 1.0, -0.5, 1.0]), 42, 4, refine_fn=fake_refine)
        self.assertEqual((seen[0]["n_estimators"], seen[0]["num_leaves"], seen[0]["random_state"]), (400, 31, 45))
        self.assertEqual(ev["classifier_params"]["n_estimators"], 400)
        self.assertEqual(s5n_pseudo.code_digests()["candidate"], "R")

    def test_b0_changes_no_refinement_parameter(self):
        import s5e_candidate

        before = s5n_pseudo.refine_params(42, 4)
        s5e_candidate.install("B0")
        self.assertEqual(s5n_pseudo.refine_params(42, 4), before)

    def test_ratio_nd_dispatch_and_other_truths_untouched(self):
        sd.install_ratio_truth(s5n_pseudo)
        inp = toy_inputs(n=2000)
        r = s5n_pseudo.truth_weight("ratio_nd", inp, 1.0, ratio_2d(np.full((3, 2), 1.1) + np.eye(3, 2)))
        self.assertGreater(np.ptp(r), 0.0)
        np.testing.assert_array_equal(s5n_pseudo.truth_weight("nominal", inp, 0.0, None), 1.0)
        with self.assertRaises(ValueError):
            s5n_pseudo.truth_weight("ratio_nd", inp, 1.0, {"schema": "s5n-eavail-ratio/1"})
        self.assertIn("ratio_nd", s5n_pseudo.TRUTHS)


if __name__ == "__main__":
    unittest.main()
