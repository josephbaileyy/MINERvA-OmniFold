"""Tests of regrade_crep.py on synthetic matrices only (no study input is read): the carry, R-chi2's one factorisation
and its identities, the one-sided reading in each direction and on each operand, the C_T_minus removal, A0's three
parts, C-PSD, the strict null wrapper and the descriptive labels.

    python3 -B -m unittest -v test_regrade_crep.py
"""
from __future__ import annotations

import math
import sys
import unittest
import warnings
from pathlib import Path
from unittest import mock

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import regrade_crep as rc  # noqa: E402
import fd_1b_null as fn  # noqa: E402


def spd(n, rng, scale=1.0, rank=None):
    A = rng.standard_normal((n, rank or n))
    return scale * (A @ A.T) / (rank or n)


def explicit_A(C):
    lam, V = np.linalg.eigh(C)
    keep = lam > fn.RANK_REL * lam.max()
    return V[:, keep] @ np.diag(1 / lam[keep]) @ V[:, keep].T, int(keep.sum())


class Carry(unittest.TestCase):
    def test_frac_is_diag_product(self):
        rng = np.random.default_rng(1)
        C, xn, xd = spd(5, rng), rng.uniform(1, 2, 5), rng.uniform(1, 2, 5)
        D = np.diag(xn / xd)
        np.testing.assert_allclose(rc.carry_frac(C, xn, xd), D @ C @ D, rtol=1e-14)

    def test_frac_identity_at_equal_x(self):
        rng = np.random.default_rng(2)
        C, x = spd(4, rng), rng.uniform(1, 2, 4)
        np.testing.assert_array_equal(rc.carry_frac(C, x, x), C)

    def test_rel_is_diag_product(self):
        rng = np.random.default_rng(3)
        P, X = spd(4, rng), rng.uniform(1, 2, 4)
        np.testing.assert_allclose(rc.carry_rel(P, X), np.diag(X) @ P @ np.diag(X), rtol=1e-14)

    def test_rel_reproduces_cpl_block_identity_shape(self):
        rng = np.random.default_rng(4)
        P, f = spd(16, rng, rank=2), rng.uniform(1, 3, 16)
        C = np.outer(f, f) * P
        self.assertLess(float(np.max(np.abs(rc.carry_rel(P, f) - C)) / np.max(np.abs(C))), 1e-14)


class RChi2(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(10)
        self.n, self.d = 300, 12
        self.C_T = spd(self.d, rng)
        self.C_add = spd(self.d, rng, scale=0.3, rank=2)
        self.E = rng.multivariate_normal(rng.normal(0, 0.3, self.d), self.C_T, size=self.n)

    def test_chi2_and_M_use_chi2_nonnull(self):
        r = rc.r_chi2(self.E, self.C_T, self.C_add)
        chi2, ndf = fn.chi2_nonnull(self.E, self.C_T + self.C_add)
        self.assertEqual(r["ndf"], ndf)
        self.assertAlmostEqual(r["M_prime"], chi2.mean() / ndf, places=13)
        self.assertAlmostEqual(r["SE"], chi2.std(ddof=1) / math.sqrt(self.n) / ndf, places=13)

    def test_tau_is_trace_A_Cadd(self):
        r = rc.r_chi2(self.E, self.C_T, self.C_add)
        A, ndf = explicit_A(self.C_T + self.C_add)
        self.assertAlmostEqual(r["tau"], np.trace(A @ self.C_add) / ndf, places=12)

    def test_split_divisor_n(self):
        r = rc.r_chi2(self.E, self.C_T, self.C_add)
        A, ndf = explicit_A(self.C_T + self.C_add)
        eb = self.E.mean(axis=0)
        S_n = (self.E - eb).T @ (self.E - eb) / self.n
        S_1 = np.cov(self.E, rowvar=False, ddof=1)
        self.assertAlmostEqual(r["mean_error_part"], eb @ A @ eb / ndf, places=12)
        self.assertAlmostEqual(r["spread_part"], np.trace(A @ S_n) / ndf, places=12)
        self.assertNotAlmostEqual(r["spread_part"], np.trace(A @ S_1) / ndf, places=6)
        self.assertAlmostEqual(r["mean_error_part"] + r["spread_part"], r["M_prime"], places=13)

    def test_M_full_is_M_plus_tau(self):
        r = rc.r_chi2(self.E, self.C_T, self.C_add)
        self.assertEqual(r["M_full"], r["M_prime"] + r["tau"])

    def test_zero_add_gives_tau_zero(self):
        r = rc.r_chi2(self.E, self.C_T, np.zeros_like(self.C_T))
        self.assertEqual(r["tau"], 0.0)
        self.assertEqual(r["M_full"], r["M_prime"])

    def test_cut_matches_chi2_nonnull_on_rank_deficient(self):
        rng = np.random.default_rng(11)
        C_T = spd(8, rng, rank=6)
        E = rng.multivariate_normal(np.zeros(8), C_T, size=50)
        r = rc.r_chi2(E, C_T, np.zeros_like(C_T))
        self.assertEqual(r["ndf"], 6)
        self.assertEqual(r["cut"]["ndf_C_T"], 6)
        self.assertIsNotNone(r["cut"]["largest_dropped_rel"])


class Reading(unittest.TestCase):
    """The rule: 'under-describes on average' iff M_full - 1 > 3 SE (strict), else 'not shown'."""

    def run_with(self, M, se, tau):
        """r_chi2 with chi2_nonnull faked: the 300 toy rows give mean M*ndf and the SE asked for; the mean row gives 0;
        the two eigenvector rows of C_add give tau*ndf and 0 (with eigenvalues 1 and 0), so tau enters only through
        the declared trace."""
        ndf, n = 10, 300
        sd = se * math.sqrt(n) * ndf
        base = np.tile([-1.0, 1.0], n // 2)
        base = base * (sd / base.std(ddof=1)) + M * ndf

        def fake(E, C):
            if E.shape[0] == n:
                return base, ndf
            if E.shape[0] == 1:
                return np.array([0.0]), ndf
            return np.array([tau * ndf, 0.0]), ndf
        with mock.patch.object(rc.fn, "chi2_nonnull", side_effect=fake), \
                mock.patch.object(rc.np.linalg, "eigh", return_value=(np.array([1.0, 0.0]), np.eye(2))), \
                mock.patch.object(rc.np.linalg, "eigvalsh", return_value=np.array([1.0, 2.0])):
            return rc.r_chi2(np.zeros((n, 2)), np.eye(2), np.ones((2, 2)))

    def test_rule_strict_at_exact_boundary(self):
        self.assertFalse(rc.read_rule(1.75, 0.25))          # 0.75 == 3 x 0.25 exactly in binary
        self.assertTrue(rc.read_rule(1.75 + 2 ** -40, 0.25))
        self.assertFalse(rc.read_rule(1.75 - 2 ** -40, 0.25))
        self.assertFalse(rc.read_rule(0.25, 0.25))           # far below 1: never a positive reading

    def test_fires_above(self):
        self.assertEqual(self.run_with(1.2, 0.05, 0.0)["reading"], "under-describes on average")

    def test_strict_at_boundary(self):
        r = self.run_with(1.0, 0.05, 0.15)
        self.assertAlmostEqual(r["M_full"] - 1, 3 * r["SE"], places=9)
        expect = "under-describes on average" if r["M_full"] - 1 > 3 * r["SE"] else "not shown"
        self.assertEqual(r["reading"], expect)
        self.assertEqual(self.run_with(1.0, 0.05, 0.1500001)["reading"], "under-describes on average")
        self.assertEqual(self.run_with(1.0, 0.05, 0.1499999)["reading"], "not shown")

    def test_not_shown_below(self):
        self.assertEqual(self.run_with(1.05, 0.05, 0.0)["reading"], "not shown")

    def test_reads_M_full_not_M_prime(self):
        r = self.run_with(0.80, 0.05, 0.40)     # M' < 1, but M_full - 1 = 0.20 > 0.15
        self.assertEqual(r["reading"], "under-describes on average")
        self.assertFalse(r["toys_own_mean_line"]["toys_mean_exceeds_1_by_3SE"])

    def test_low_M_prime_is_never_over(self):
        r = self.run_with(0.5, 0.01, 0.0)
        self.assertEqual(r["reading"], "not shown")

    def test_uses_SE_scale(self):
        self.assertEqual(self.run_with(1.2, 0.10, 0.0)["reading"], "not shown")   # 0.2 < 0.3


class Null2D(unittest.TestCase):
    def test_removes_C_T_minus_and_adds_C_run_once(self):
        B = {"C_T": np.eye(3), "C08": 0.1 * np.eye(3), "C_T_minus": 5 * np.eye(3), "minos_x": np.zeros((2, 3)),
             "w_flux": np.ones(2), "band__Flux": np.zeros((2, 3))}
        C_run = 0.5 * np.eye(3)
        seen = {}

        def fake(b, bands, minos_x, w_flux):
            seen.update(b=b, bands=bands)
            return {"null": "N"}
        import cov2d_null
        with mock.patch.object(cov2d_null, "null_at_T", side_effect=fake):
            null, C1 = rc.null_2d(B, C_run)
        self.assertNotIn("C_T_minus", seen["b"])
        np.testing.assert_array_equal(seen["b"]["C08"], 0.6 * np.eye(3))
        np.testing.assert_array_equal(seen["b"]["C_T"], 1.5 * np.eye(3))
        np.testing.assert_array_equal(C1, 1.5 * np.eye(3))
        self.assertEqual(list(seen["bands"]), ["Flux"])
        np.testing.assert_array_equal(B["C_T"], np.eye(3))     # the input dict is not modified


class A0(unittest.TestCase):
    def base(self):
        g = {"ndf": 10, "joint_count": 3, "counts": [1, 2], "chi2_mean_over_ndf": 4.0, "k_joint": 5,
             "cell_flag": [True, False]}
        c = dict(g, flagged_cells=[7])
        return g, c

    def test_pass_equal(self):
        g, c = self.base()
        r = rc.a0_compare(g, c, "flagged_cells", [7])
        self.assertEqual(r["c_reading"], "equal")

    def test_each_exact_part_stops(self):
        for k, v in (("ndf", 11), ("joint_count", 4), ("counts", [1, 3])):
            g, c = self.base()
            g[k] = v
            with self.assertRaises(rc.Stop, msg=k):
                rc.a0_compare(g, c, "flagged_cells", [7])

    def test_chi2_tolerance(self):
        g, c = self.base()
        g["chi2_mean_over_ndf"] = 4.0 * (1 + 0.5e-9)
        rc.a0_compare(g, c, "flagged_cells", [7])
        g["chi2_mean_over_ndf"] = 4.0 * (1 + 2e-9)
        with self.assertRaises(rc.Stop):
            rc.a0_compare(g, c, "flagged_cells", [7])

    def test_c_mismatch_is_not_a_stop(self):
        g, c = self.base()
        g["k_joint"] = 6
        self.assertEqual(rc.a0_compare(g, c, "flagged_cells", [7])["c_reading"], "null redraw differs")
        g, c = self.base()
        self.assertEqual(rc.a0_compare(g, c, "flagged_cells", [8])["c_reading"], "null redraw differs")


class Controls(unittest.TestCase):
    def test_psd_zero_skipped(self):
        self.assertIn("skipped", rc.check_psd(np.zeros((3, 3)), "z"))

    def test_psd_negative_stops(self):
        with self.assertRaises(rc.Stop):
            rc.check_psd(np.diag([1.0, -1e-6]), "neg")

    def test_psd_tiny_negative_passes(self):
        rc.check_psd(np.diag([1.0, -1e-13]), "tiny")

    def test_psd_asym_stops(self):
        with self.assertRaises(rc.Stop):
            rc.check_psd(np.array([[1.0, 0.1], [0.0, 1.0]]), "asym")

    def test_strict_turns_warning_into_stop(self):
        def warns():
            warnings.warn("covariance is not symmetric positive-semidefinite.", RuntimeWarning)
        with self.assertRaises(rc.Stop):
            rc._strict(warns)

    def test_strict_turns_refusal_into_stop(self):
        def refuses():
            raise fn.Refusal("miss")
        with self.assertRaises(rc.Stop):
            rc._strict(refuses)

    def test_strict_passes_value(self):
        self.assertEqual(rc._strict(lambda x: x + 1, 1), 2)

    def test_real_numpy_nonpsd_warning_is_stop(self):
        def draw():
            return np.random.default_rng(0).multivariate_normal(np.zeros(2), np.array([[1.0, 0.0], [0.0, -1e-3]]),
                                                                 size=2, method="eigh")
        with self.assertRaises(rc.Stop):
            rc._strict(draw)

    def test_descriptive_prefix(self):
        g = {"joint_count": 0, "k_joint": 1, "joint_flag": True, "ndf": 3, "cell_flag": [False], "counts": [1],
             "k_cell": [0], "chi2_mean_over_ndf": 2.0, "verdict": "UNDER-COVERS"}
        d = rc.descriptive(g)
        self.assertEqual(d["verdict"], "descriptive-UNDER-COVERS")
        self.assertEqual(d["note"], "a reading, not a proof")

    def test_pins_are_full_digests(self):
        for k, (p, s) in rc.PINS.items():
            self.assertRegex(s, r"^[0-9a-f]{64}$", k)
        self.assertRegex(rc.Q205_SHA, r"^[0-9a-f]{64}$")

    def test_null_seeds_are_ll5d_s(self):
        import ll5d
        self.assertEqual(rc.NULL_SEED_16, ll5d.NULL_SEED)


class CMap16AndCut(unittest.TestCase):
    def test_cmap16_passes_on_committed_metadata(self):
        with np.load(rc.PINS["cpl_block"][0], allow_pickle=False) as z:
            f = np.asarray(z["f"], np.float64)
        rec = rc.cmap16(f)
        self.assertEqual(rec["cells_csv"], [f"R{i:02d}" for i in range(16)])
        self.assertTrue(rec["npz_named"])

    def test_cmap16_stops_on_reordered_f(self):
        with np.load(rc.PINS["cpl_block"][0], allow_pickle=False) as z:
            f = np.asarray(z["f"], np.float64)
        with self.assertRaises(rc.Stop):
            rc.cmap16(f[::-1].copy())

    def test_cmap16_stops_on_changed_csv(self):
        import shutil, tempfile
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "cells.csv"
            shutil.copy(rc.PINS["cpl_cells_csv"][0], p)
            p.write_text(p.read_text().replace("R01,", "R99,", 1))
            with mock.patch.dict(rc.PINS, {"cpl_cells_csv": (p, rc.sha256(p))}):
                with np.load(rc.PINS["cpl_block"][0], allow_pickle=False) as z:
                    with self.assertRaises(rc.Stop):
                        rc.cmap16(np.asarray(z["f"], np.float64))

    def test_run16_records_stop_when_cmap16_fails(self):
        with mock.patch.object(rc, "cmap16", side_effect=rc.Stop("C-MAP16: test")):
            out = rc.run16(Path("/nonexistent"))
        self.assertEqual({v["status"] for v in out["evaluations"].values()}, {"STOP"})
        self.assertEqual(len(out["evaluations"]), 4)

    def test_kept_set_count(self):
        rng = np.random.default_rng(7)
        C_T = spd(6, rng)
        E = rng.standard_normal((20, 6))
        r = rc.r_chi2(E, C_T, np.zeros_like(C_T))
        self.assertEqual(r["cut"]["C_T_kept_modes_outside_C_prime_kept_span"], 0)
        # a huge added block lifts lambda_max so far that C_T's smallest modes fall under the 1e-12 cut
        lam, V = np.linalg.eigh(C_T)
        C_T2 = V @ np.diag([1e-3, 1, 1, 1, 1, 1]) @ V.T
        u = V[:, -1]
        r2 = rc.r_chi2(E, C_T2, 1e12 * np.outer(u, u))
        self.assertGreaterEqual(r2["cut"]["C_T_kept_modes_outside_C_prime_kept_span"], 1)


if __name__ == "__main__":
    unittest.main()
