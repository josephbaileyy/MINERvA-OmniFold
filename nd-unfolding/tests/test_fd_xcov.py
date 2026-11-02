"""Controls for fd_xcov.py (FD-GENCMP-X-DECLARATION.md), on synthetic inputs. No real prediction, covariance or data
value is read; the only real file read is the H2 definition, for its geometry.

Every control is tested in the direction it acts and in the other: the joins (a subsequence, a non-subsequence, an
ambiguous row), the 2D data mask at each window edge, MC row identity (a differing row, a wrong sentinel count), the
draws against RE-2's and s5n_pseudo's own, the mapped replica, the cross blocks against each side's own rule, the bound
matrix's PSD joint, the chi2_4 survival function, the rule at each of its branches, route A's r*, and route B's
correlation."""
import sys
import unittest
from pathlib import Path

import numpy as np

ND = Path(__file__).resolve().parents[1]
sys.path.insert(1, str(ND))
import fd_gencmp as gc  # noqa: E402
import fd_xcov as X  # noqa: E402
import s1_assemble as sa  # noqa: E402
import s5n_pseudo  # noqa: E402

RNG = np.random.default_rng(20261102)


def spd(n, s=1.0):
    M = RNG.normal(size=(n, n))
    return (M @ M.T / n + np.eye(n)) * s


class Joins(unittest.TestCase):
    def setUp(self):
        self.big = RNG.uniform(0, 5, (500, 2)).astype(np.float32)
        self.keep = np.sort(RNG.choice(500, 470, replace=False))

    def test_a_subsequence_maps_back_to_its_rows(self):
        m, amb = X.subsequence_join(self.big, self.big[self.keep])
        self.assertTrue(np.array_equal(m, self.keep))
        self.assertEqual(amb, 0)

    def test_a_row_not_in_order_refuses(self):
        small = self.big[self.keep].copy()
        small[[10, 11]] = small[[11, 10]]
        with self.assertRaises(gc.Stop) as e:
            X.subsequence_join(self.big, small)
        self.assertIn("J", str(e.exception))

    def test_a_row_absent_from_2d_refuses(self):
        small = self.big[self.keep].copy()
        small[5, 0] = np.float32(99.0)
        with self.assertRaises(gc.Stop):
            X.subsequence_join(self.big, small)

    def test_an_ambiguous_row_is_counted(self):
        big = self.big.copy()
        big[101] = big[100]
        m, amb = X.subsequence_join(big, big[[100, 200]])
        self.assertEqual(m.tolist(), [100, 200])
        self.assertEqual(amb, 1)

    def test_float64_2d_values_match_their_float32_5d_copies(self):
        b64 = RNG.uniform(0, 5, (50, 2))
        m, _ = X.subsequence_join(b64.astype(np.float32), b64[::2].astype(np.float32))
        self.assertEqual(m.tolist(), list(range(0, 50, 2)))


class Mask(unittest.TestCase):
    def test_the_closed_window_and_each_rejection(self):
        pt = np.array([0.0, 4.5, 4.5000001, 1.0, 1.0, np.nan, 2e3, 1.0])
        pz = np.array([1.5, 60.0, 2.0, 1.4999999, 60.0000001, 2.0, 2.0, 2.0])
        ps = np.array([1, 1, 1, 1, 1, 1, 1, 0])
        self.assertEqual(X.mask_2d_data(pt, pz, ps).tolist(), [True, True, False, False, False, False, False, False])


class Rows(unittest.TestCase):
    def setUp(self):
        n = 3000
        self.mc = RNG.uniform(0, 5, (n, 5)).astype(np.float32)
        self.mc[:X.SENTINEL_ROWS, :] = -9999.0
        self.pt, self.pz = self.mc[:, 0].astype(float), self.mc[:, 1].astype(float)
        self.w2 = RNG.uniform(0.5, 2, n)

    def test_the_same_rows_pass_and_record_the_weight_scale(self):
        r = X.mc_positional(self.pt, self.pz, self.mc, self.w2, 3.0 * self.w2)
        self.assertTrue(r["pass"])
        self.assertAlmostEqual(r["weight_scale"], 3.0)

    def test_one_differing_row_refuses(self):
        pt = self.pt.copy()
        pt[-1] += 0.25
        self.assertFalse(X.mc_positional(pt, self.pz, self.mc)["pass"])

    def test_a_wrong_sentinel_count_refuses(self):
        mc = self.mc.copy()
        mc[0, :] = 1.0
        self.assertFalse(X.mc_positional(self.pt, self.pz, mc)["pass"])

    def test_a_different_row_count_refuses(self):
        self.assertFalse(X.mc_positional(self.pt[:-1], self.pz[:-1], self.mc)["pass"])


class Draws(unittest.TestCase):
    def exp(self, n_obs=40, n_mc=60, n_t=20):
        return {"obs_counts": np.ones(n_obs), "w_truth": RNG.uniform(0.5, 2, n_mc), "w_reco": RNG.uniform(0.5, 2, n_mc),
                "tmpl_w": RNG.uniform(0.5, 2, n_t), "obs": np.zeros((n_obs, 5))}

    def test_draws_are_re2s_streams(self):
        d, m, g = X.draws_2d(7, 50, 60, 30)
        self.assertTrue(np.array_equal(d, np.random.default_rng(7).poisson(1.0, size=50).astype(float)))
        self.assertTrue(np.array_equal(m, np.random.default_rng(7 + 10_000_000).poisson(1.0, size=60).astype(float)))
        self.assertTrue(np.array_equal(g, np.random.default_rng(7 + 20_000_000).poisson(1.0, size=30).astype(float)))

    def test_native_draws_reproduce_s5n_pseudo_bitwise(self):
        exp = self.exp()
        a, b = X.replica_external(exp, *X.native_draws(exp, 3)), s5n_pseudo.bootstrap_replica(exp, 3)
        for k in ("obs_counts", "w_truth", "w_reco", "tmpl_w"):
            self.assertTrue(np.array_equal(a[k], b[k]), k)

    def test_the_mapped_replica_carries_each_2d_draw_to_its_5d_row(self):
        exp = self.exp(40, 60, 20)
        j, entry = np.sort(RNG.choice(50, 40, replace=False)), np.sort(RNG.choice(30, 20, replace=False))
        rep = X.make_mapped_replica(j, entry, (50, 60, 30))(exp, 5)
        d, m, g = X.draws_2d(5, 50, 60, 30)
        self.assertTrue(np.array_equal(rep["obs_counts"], d[j]))
        self.assertTrue(np.array_equal(rep["w_truth"], exp["w_truth"] * m))
        self.assertTrue(np.array_equal(rep["tmpl_w"], exp["tmpl_w"] * g[entry]))

    def test_a_map_of_the_wrong_length_refuses(self):
        exp = self.exp(40, 60, 20)
        with self.assertRaises(gc.Stop):
            X.make_mapped_replica(np.arange(39), np.arange(20), (50, 60, 30))(exp, 1)

    def test_the_draw_check_prints_re2s_format(self):
        line = X.draw_sums_line(2, (50, 60, 30))
        d = np.random.default_rng(2).poisson(1.0, size=50).astype(float)
        self.assertEqual(line["data"], f"data factor sum={d.sum():.6g} (n=50")


class Algebra(unittest.TestCase):
    def test_cross_cov_is_each_sides_own_rule_on_the_diagonal(self):
        X16 = RNG.normal(size=(100, 4))
        w = RNG.uniform(0, 1, 100)
        self.assertTrue(np.allclose(X.cross_cov(X16, X16, w), sa.mat_cov(X16, w)))
        self.assertTrue(np.allclose(X.cross_cov(X16[:2], X16[:2]), sa.mat_cov(X16[:2])))

    def test_cross_cov_transposes_with_its_arguments(self):
        A, B = RNG.normal(size=(30, 4)), RNG.normal(size=(30, 4))
        self.assertTrue(np.allclose(X.cross_cov(A, B), X.cross_cov(B, A).T))
        with self.assertRaises(gc.Stop):
            X.cross_cov(A, B[:-1])

    def test_paired_universes_keep_the_joint_matrix_psd(self):
        X16, X2 = RNG.normal(size=(100, 4)), RNG.normal(size=(100, 4))
        J = X.cross_cov(np.hstack([X16, X2]), np.hstack([X16, X2]))
        self.assertTrue(np.allclose(J[:4, 4:], X.cross_cov(X16, X2)))
        self.assertGreaterEqual(np.linalg.eigvalsh(J).min(), -1e-12)

    def test_outer_pairs(self):
        v = [RNG.normal(size=4) for _ in range(3)]
        u = [RNG.normal(size=4) for _ in range(3)]
        self.assertTrue(np.allclose(X.outer_pairs(v, u), sum(np.outer(a, b) for a, b in zip(v, u))))
        with self.assertRaises(gc.Stop):
            X.outer_pairs(v, u[:2])

    def test_the_bound_matrix_keeps_the_joint_psd_at_every_r(self):
        S16, S2 = spd(4), spd(4, 3.0)
        M = X.bound_matrix(S16, S2)
        for r in (0.0, 0.5, 1.0):
            J = np.block([[S16, r * M], [r * M.T, S2]])
            self.assertGreaterEqual(np.linalg.eigvalsh(J).min(), -1e-10, r)

    def test_chi2_sf4(self):
        self.assertAlmostEqual(X.chi2_sf4(9.487729036781154), 0.05, places=10)
        self.assertAlmostEqual(X.chi2_sf4(0.0), 1.0)

    def test_quadrant_vectors_on_the_definition(self):
        e_pt, e_pz = (np.asarray(sa.s1.FINE[k], float) for k in ("pt", "pz"))
        ncell = (len(e_pt) - 1) * (len(e_pz) - 1)
        cells = np.arange(ncell)
        area = np.ones(ncell)
        import json
        A, B = X.quadrant_vectors(json.loads(gc.DEFINITION.read_text()), cells, area, e_pt, e_pz)
        self.assertEqual(A.sum(axis=1).tolist(), [4.0] * 4)
        self.assertTrue(np.all((B > 0).sum(axis=0) <= 1))       # no 2D bin in two quadrants


class Rule(unittest.TestCase):
    V = np.diag([1.0, 1.0, 1.0, 1.0])

    def test_agree(self):
        r = X.verdict(np.array([0.5, -0.5, 1.0, 0.2]), self.V)
        self.assertEqual((r["outcome"], r["named"]), ("agree", []))

    def test_a_quadrant_over_2_5_is_a_named_differ(self):
        r = X.verdict(np.array([0.1, 2.6, 0.0, 0.0]), self.V)
        self.assertEqual((r["outcome"], r["named"]), ("differ", ["QB"]))

    def test_exactly_2_5_is_not_over(self):
        self.assertEqual(X.verdict(np.array([2.5, 0.0, 0.0, 0.0]), self.V)["quadrants_over"], [])

    def test_a_joint_p_below_0_05_with_no_quadrant_over_is_a_joint_differ(self):
        r = X.verdict(np.array([2.2, 2.2, 0.0, 0.0]), self.V)          # chi2 9.68 > 9.488
        self.assertEqual((r["outcome"], r["named"]), ("differ", ["joint"]))
        self.assertLess(r["p"], 0.05)

    def test_a_non_positive_definite_vd_refuses(self):
        with self.assertRaises(gc.Stop):
            X.verdict(np.zeros(4), np.diag([1.0, 1.0, 1.0, 0.0]))

    def test_vd_subtracts_the_cross_term_twice(self):
        C16, C2, K = spd(4), spd(4), 0.1 * RNG.normal(size=(4, 4))
        self.assertTrue(np.allclose(X.Vd_of(C16, C2, K), C16 + C2 - K - K.T))

    def test_route_a_reports_r_star_where_the_reading_changes(self):
        C = np.eye(4)
        M = 0.9 * np.eye(4)
        d = np.array([0.0, 1.5, 0.0, 0.0])            # V_d = 2 - 1.8 r, so z = 1.5/sqrt(2 - 1.8 r) passes 2.5 at r = 0.9111
        r = X.route_a(d, C, C, np.zeros((4, 4)), M, grid=1001)
        self.assertEqual((r["r0"]["outcome"], r["r1"]["outcome"]), ("agree", "differ"))
        self.assertAlmostEqual(r["r_star"], (2 - 0.36) / 1.8, delta=0.002)
        same = X.route_a(np.zeros(4), C, C, np.zeros((4, 4)), M)
        self.assertEqual((same["outcome"], same["r_star"]), ("agree", None))


class Stat(unittest.TestCase):
    def test_fully_paired_replicas_give_rho_one_and_k_sigma_sigma(self):
        S = RNG.normal(size=(100, 4))
        out = X.stat_cross(S, 2.0 * S + 1.0, np.ones(4), 3.0 * np.ones(4))
        self.assertTrue(np.allclose(out["rho_diag"], 1.0))
        self.assertTrue(np.allclose(np.diag(out["K"]), 3.0))
        self.assertTrue(np.allclose(out["rho_diag_jackknife_se"], 0.0, atol=1e-12))

    def test_independent_replicas_give_rho_near_zero(self):
        out = X.stat_cross(RNG.normal(size=(400, 4)), RNG.normal(size=(400, 4)), np.ones(4), np.ones(4))
        self.assertTrue(np.all(np.abs(out["rho_diag"]) < 0.2))


class Shares(unittest.TestCase):
    def test_the_shares_sum_to_one(self):
        a, b, k = spd(4), spd(4), 0.05 * spd(4)
        Vd = X.Vd_of(a, b, k)
        sh = X.shares({"a": a}, {"b": b}, {"k": k}, Vd)
        self.assertTrue(np.allclose(np.sum(list(sh.values()), axis=0), 1.0))


if __name__ == "__main__":
    unittest.main()
