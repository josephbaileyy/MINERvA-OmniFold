"""cov2d_score: the surrogate order (R4: lateral, then normalization) and its cross term, the errors, 1B's grade imported
unchanged, the weakened labels, the outlier cell and INVALID. numpy only.
    cd 2d-unfolding/cov2d/tests && python -B -m unittest -v test_cov2d_score
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest import mock

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import cov2d as c  # noqa: E402
import cov2d_score as sc  # noqa: E402

N = 205


class Surrogate(unittest.TestCase):
    def setUp(self):
        r = np.random.default_rng(2)
        self.x = r.uniform(1, 2, N)
        self.d = r.normal(0, 0.05, (5, N))
        self.s = [1, -1, 1, 1, -1]
        self.z = 1.3

    def test_lateral_then_normalization(self):
        x, cross = sc.surrogate(self.x, self.s, self.z, self.d)
        lat = sum(si * di for si, di in zip(self.s, self.d)) / 2
        np.testing.assert_allclose(x, (self.x + lat) * (1 + 0.014 * self.z), rtol=1e-15)
        other = self.x * (1 + 0.014 * self.z) + lat
        self.assertFalse(np.allclose(x, other, rtol=1e-12))          # the orders differ...
        np.testing.assert_allclose(x - other, cross, rtol=1e-9, atol=1e-18)   # ...by exactly the reported term

    def test_signs_must_be_one_per_lateral_band(self):
        for bad in ([1, -1, 1, 1], [1, -1, 1, 1, 0]):
            with self.subTest(bad), self.assertRaises(c.Refusal):
                sc.surrogate(self.x, bad, self.z, self.d)

    def test_deltas_use_minos_x01(self):
        r = np.random.default_rng(3)
        bands = {b: r.normal(size=(2, N)) for b in c.LATERAL_BANDS}
        mx = r.normal(size=(2, N))
        d = sc.lateral_deltas(bands, mx)
        i = c.LATERAL_BANDS.index(sc.MINOS)
        np.testing.assert_array_equal(d[i], mx[0] - mx[1])
        np.testing.assert_array_equal(d[0], bands[c.LATERAL_BANDS[0]][0] - bands[c.LATERAL_BANDS[0]][1])


class Score(unittest.TestCase):
    def setUp(self):
        r = np.random.default_rng(5)
        A = r.normal(size=(N, N)) * 0.1
        self.C = A @ A.T + np.eye(N) * 0.05
        L = np.linalg.cholesky(self.C)
        self.E = (L @ r.standard_normal((N, 300))).T
        self.cells = np.sort(r.choice(224, N, replace=False))
        if c.OUTLIER_CELL not in self.cells:
            self.cells[-1] = c.OUTLIER_CELL
            self.cells = np.sort(self.cells)
        import fd_1b_null as nl
        self.null = {"p_cell": np.full(N, nl.P0), "se_cell": np.zeros(N), "q_joint": nl.P0, "se_joint": 0.0,
                     "chi2_cut": float(__import__("fd_1b_inv").chi2_ppf(nl.P0, N)), "ndf": N}
        self.ratio = np.ones(N)
        self.ratio[:7] = 0.85            # seven weakened cells

    def test_grade_is_1bs_and_gaussian_errors_cover(self):
        import fd_1b_mc as mc
        g = sc.score(self.E, self.C, self.null, "G18", self.cells, self.ratio)
        ref = mc.grade(self.E, self.C, self.null)
        for k in ("counts", "cell_flag", "joint_count", "ndf", "s_c"):
            self.assertEqual(g[k], ref[k], k)
        self.assertEqual(g["ndf"], 205)
        self.assertEqual(g["verdict"], "COVERS")
        self.assertEqual(sorted(g["weakened_pass"]), sorted(int(x) for x in self.cells[:7]))
        self.assertAlmostEqual(g["weakened_share"], 7 / 205)
        self.assertEqual(g["outlier_cell"]["cell"], 216)

    def test_too_narrow_c_t_under_covers_and_a_weakened_cell_that_flags_is_not_labelled(self):
        g = sc.score(self.E * 1.6, self.C, self.null, "G18", self.cells, self.ratio)
        self.assertEqual(g["verdict"], "UNDER-COVERS")
        self.assertTrue(g["flagged_cells"])
        self.assertFalse(set(g["weakened_pass"]) & set(g["flagged_cells"]))

    def test_a_failed_control_is_invalid_and_keeps_the_grade(self):
        g = sc.score(self.E, self.C, self.null, "AR23", self.cells, self.ratio, controls_failed=["9.11"])
        self.assertEqual(g["verdict"], "INVALID")
        self.assertEqual(g["verdict_graded"], "COVERS")

    def test_the_outlier_cells_values_are_read_at_its_own_position(self):
        E = self.E.copy()
        i = list(self.cells).index(c.OUTLIER_CELL)
        E[:, i] *= 3.0                                           # flagged there, unlike cell 0
        g = sc.score(E, self.C, self.null, "G18", self.cells, self.ratio)
        o = g["outlier_cell"]
        self.assertEqual((o["count"], o["k_cell"], o["flagged"], o["pull_mean"], o["s_c"]),
                         (g["counts"][i], g["k_cell"][i], True, g["pull_mean"][i], g["s_c"][i]))
        self.assertNotEqual(o["count"], g["counts"][0])

    def test_weakened_share_counts_every_weakened_cell_when_they_flag(self):
        E = self.E.copy()
        E[:, :7] *= 3.0                                          # all seven weakened cells flag
        g = sc.score(E, self.C, self.null, "G18", self.cells, self.ratio)
        self.assertEqual(g["verdict"], "UNDER-COVERS")
        self.assertEqual(g["weakened_pass"], [])
        self.assertAlmostEqual(g["weakened_share"], 7 / 205)

    def test_refuses_any_toy_count_but_the_declared_300(self):
        for n in (299, 150):
            with self.subTest(n), self.assertRaises(c.Refusal):
                sc.score(self.E[:n], self.C, self.null, "G18", self.cells, self.ratio)

    def test_refuses_cells_without_the_outlier(self):
        cells = np.array([x for x in range(224) if x != c.OUTLIER_CELL][:N])
        with self.assertRaises(c.Refusal):
            sc.score(self.E, self.C, self.null, "G18", cells, self.ratio)

    def test_needs_205_cells(self):
        with self.assertRaises(c.Refusal):
            sc.score(self.E[:, :200], self.C[:200, :200], self.null, "G18", self.cells[:200], self.ratio[:200])

    def test_errors_apply_the_surrogates_per_toy(self):
        r = np.random.default_rng(9)
        nat = [{"role": "toy", "lateral_signs": list(r.choice([-1, 1], 5)), "norm_z": float(r.normal())}
               for _ in range(4)] + [{"role": "realization"}]
        xh, xt = r.uniform(1, 2, (4, N)), r.uniform(1, 2, (4, N))
        d = r.normal(0, 0.05, (5, N))
        C_T = np.diag(r.uniform(0.005, 0.02, N))
        E, cross = sc.errors(xh, xt, nat, d, C_T)
        crosses = []
        for k in range(4):
            want, ck = sc.surrogate(xh[k], nat[k]["lateral_signs"], nat[k]["norm_z"], d)
            np.testing.assert_allclose(E[k], want - xt[k], rtol=1e-15)
            crosses.append(np.abs(ck) / np.sqrt(np.diag(C_T)))          # sigma_c = sqrt(diag C_T)
        self.assertAlmostEqual(cross["max_over_sigma"], float(np.max(crosses)), places=15)
        self.assertAlmostEqual(cross["median_over_sigma"], float(np.median(crosses)), places=15)
        with self.assertRaises(c.Refusal):
            sc.errors(xh[:3], xt, nat, d, C_T)
        with self.assertRaises(c.Refusal):
            sc.errors(xh, xt, nat, d, C_T[:200, :200])


if __name__ == "__main__":
    unittest.main()
