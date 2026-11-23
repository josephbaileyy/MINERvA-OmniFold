"""Unit tests for covfix_core (COVFIX-DECLARATION.md rev 11.4 sections 2, 5.2, 6.1, 8). Synthetic inputs only.

  python3 -B -m unittest -v test_covfix_core.py
"""
from __future__ import annotations

import json
import math
import unittest
from unittest import mock

import numpy as np
from scipy import stats

import covfix_core as cc


def rand_psd(n, rank=None, seed=0, spread=3.0):
    rng = np.random.default_rng(seed)
    A = np.linalg.qr(rng.normal(size=(n, n)))[0]
    k = n if rank is None else rank
    lam = np.zeros(n)
    lam[:k] = 10.0 ** rng.uniform(-spread, 0, size=k)
    return (A * lam) @ A.T


class Carry(unittest.TestCase):
    def test_factor_and_product(self):
        V = rand_psd(5)
        xt, xr = np.array([1.0, 2, 3, 4, 5]), np.array([2.0, 2, 2, 2, 2])
        d = cc.carry_factor(xt, xr)
        np.testing.assert_array_equal(d, xt / xr)
        np.testing.assert_allclose(cc.carry(V, d), np.diag(d) @ V @ np.diag(d), rtol=0, atol=1e-15)

    def test_identity_at_equal_x(self):
        V = rand_psd(4)
        x = np.array([1.0, 2, 3, 4])
        np.testing.assert_array_equal(cc.carry(V, cc.carry_factor(x, x)), V)

    def test_refusals(self):
        xr = np.ones(3)
        for xt in (np.array([1.0, 0, 1]), np.array([1.0, np.inf, 1]), np.array([1.0, np.nan, 1])):
            with self.assertRaises(cc.Refusal):
                cc.carry_factor(xt, xr)
        with self.assertRaises(cc.Refusal):
            cc.carry_factor(np.ones(3), np.array([1.0, 0, 1]))
        with self.assertRaises(cc.Refusal):
            cc.carry_factor(np.ones(3), np.ones(4))
        with self.assertRaises(cc.Refusal):
            cc.carry_factor(np.ones((3, 1)), np.ones((3, 1)))

    def test_absolute(self):
        C = rand_psd(3)
        x = np.array([2.0, 3, 5])
        np.testing.assert_allclose(cc.absolute(C, x), C * np.outer(x, x), rtol=1e-15, atol=0)
        np.testing.assert_array_equal(cc.absolute(C, x), x[:, None] * C * x[None, :])   # cov2d_blocks.py:143


class PSD(unittest.TestCase):
    def test_bar(self):
        U = np.linalg.qr(np.random.default_rng(1).normal(size=(4, 4)))[0]
        for lam_min, ok in ((-0.5e-12, True), (-2e-12, False), (0.0, True)):
            C = (U * np.array([1.0, 0.5, 0.1, lam_min])) @ U.T
            self.assertEqual(cc.psd_check(C, "c")["pass"], ok, lam_min)

    def test_zero_matrix_passes(self):
        self.assertTrue(cc.psd_check(np.zeros((3, 3)), "z")["pass"])

    def test_asymmetry_is_printed_not_barred(self):
        C = np.eye(3)
        C[0, 1] = 1e-6
        r = cc.psd_check(C, "a")
        self.assertTrue(r["pass"])
        self.assertGreater(r["asymmetry_rel"], 0)

    def test_one_representation(self):
        C = np.array([[1.0, 0.0], [2.0, 1.0]])            # the symmetric part has eigenvalues 2 and 0
        self.assertEqual(cc.psd_check(C, "c")["lambda_min"], 0.0)
        lam, _ = cc.eig_basis(C)
        np.testing.assert_allclose(lam, [2.0, 0.0], atol=1e-15)
        self.assertEqual(cc.lambda_1(C), 2.0)


class EigBasis(unittest.TestCase):
    def test_descending_reconstructs_and_signs(self):
        V = rand_psd(6, seed=3)
        lam, U = cc.eig_basis(V)
        self.assertTrue(np.all(np.diff(lam) <= 0))
        np.testing.assert_allclose((U * lam) @ U.T, V, atol=1e-13)
        idx = np.argmax(np.abs(U), axis=0)
        self.assertTrue(np.all(U[idx, np.arange(6)] > 0))

    def test_evr_driver_same_basis(self):
        V = rand_psd(6, seed=4)
        l1, U1 = cc.eig_basis(V)
        l2, U2 = cc.eig_basis(V, driver="evr")
        np.testing.assert_allclose(l1, l2, rtol=1e-12)
        np.testing.assert_allclose(U1, U2, atol=1e-10)
        with self.assertRaises(ValueError):
            cc.eig_basis(V, driver="lapack")

    def test_sign_fix_flips_negative_leader(self):
        U = np.array([[-0.8, 0.6], [0.6, 0.8]])
        F = cc._sign_fix(U)
        np.testing.assert_array_equal(F[:, 0], [0.8, -0.6])
        np.testing.assert_array_equal(F[:, 1], U[:, 1])

    def test_identity_is_canonical_axes(self):
        lam, U = cc.eig_basis(np.eye(4))
        np.testing.assert_allclose(U, np.eye(4), atol=1e-15)

    def test_tied_subspace_does_not_depend_on_rotation(self):
        Q = np.linalg.qr(np.random.default_rng(5).normal(size=(5, 5)))[0]
        U0 = Q[:, 1:3]
        c, s = math.cos(0.7), math.sin(0.7)
        A = cc._canonical_tied(U0)
        B = cc._canonical_tied(U0 @ np.array([[c, -s], [s, c]]))
        np.testing.assert_allclose(A, B, atol=1e-12)
        np.testing.assert_allclose(A.T @ A, np.eye(2), atol=1e-12)

    def test_canonical_tied_skips_null_projection(self):
        U = np.array([[0.0], [1.0], [0.0]])           # e_1 projects to zero; e_2 spans it
        np.testing.assert_allclose(cc._canonical_tied(U), U, atol=0)

    def test_small_genuine_projection_is_kept_in_order(self):
        w = np.array([1e-11, 0.0, 1.0])
        w /= np.linalg.norm(w)
        U = np.column_stack([np.array([0.0, 1.0, 0.0]), w])  # e_1 projects to 1e-11 w: genuine, so it comes first
        A = cc._canonical_tied(U)
        np.testing.assert_allclose(A[:, 0], w, atol=1e-12)
        np.testing.assert_allclose(A[:, 1], [0.0, 1.0, 0.0], atol=1e-12)

    def test_tiny_genuine_projection_in_205_cells(self):
        n = 205
        w = np.zeros(n)
        w[0], w[5] = 1e-13, 1.0
        w /= np.linalg.norm(w)
        e3 = np.zeros(n)
        e3[2] = 1.0
        A = cc._canonical_tied(np.column_stack([e3, w]))
        np.testing.assert_allclose(A[:, 0], w, atol=1e-15)          # e_1's 1e-13 projection is genuine: first

    def test_nearly_dependent_projections_stay_in_span(self):
        rng = np.random.default_rng(31)
        U = np.linalg.qr(rng.normal(size=(40, 3)))[0]
        U[1, :] = U[0, :] + 1e-9 * rng.normal(size=3)                 # rows 0 and 1 nearly dependent
        U = np.linalg.qr(U)[0]
        A = cc._canonical_tied(U)
        np.testing.assert_allclose(A.T @ A, np.eye(3), atol=1e-12)
        np.testing.assert_allclose(U @ (U.T @ A), A, atol=1e-13)      # inside span(U)

    def test_tie_groups(self):
        self.assertEqual(cc.tie_groups(np.array([3.0, 2.0, 2.0, 1.0, 1.0, 1.0, 0.5])), [(1, 3), (3, 6)])
        self.assertEqual(cc.tie_groups(np.array([1.0])), [])

    def test_canonical_tied_refuses_when_not_spanned(self):
        U = np.array([[1.0, 1.0], [0.0, 0.0], [0.0, 0.0]])  # rank 1, two columns
        with self.assertRaises(cc.Refusal):
            cc._canonical_tied(U)

    def test_tied_branch_used_in_eig_basis(self):
        V = np.diag([2.0, 1.0, 1.0])
        lam, U = cc.eig_basis(V)
        np.testing.assert_array_equal(lam, [2.0, 1.0, 1.0])
        np.testing.assert_allclose(U, np.eye(3), atol=1e-15)


class Bands(unittest.TestCase):
    def test_ranks(self):
        b = cc.band_of(np.geomspace(1, 1e-6, 205))
        self.assertEqual([int(np.sum(b == i)) for i in range(3)], [73, 66, 66])
        self.assertEqual(list(b[[72, 73, 138, 139]]), [0, 1, 1, 2])

    def test_cluster_straddling_edges_goes_low(self):
        lam = np.geomspace(1, 1e-6, 205)
        lam[73] = lam[72] * (1 - 0.5e-9)
        lam[139] = lam[138] * (1 - 0.5e-9)
        b = cc.band_of(lam)
        self.assertEqual(list(b[[73, 139, 140]]), [0, 1, 2])

    def test_chained_cluster(self):
        lam = np.geomspace(1, 1e-6, 205)
        lam[73] = lam[72] * (1 - 0.6e-9)                   # adjacent gaps 0.6e-9; the ends are 1.2e-9 apart
        lam[74] = lam[73] * (1 - 0.6e-9)
        self.assertEqual(list(cc.band_of(lam)[[72, 73, 74, 75]]), [0, 0, 0, 1])

    def test_gap_above_tie_not_clustered(self):
        lam = np.geomspace(1, 1e-6, 205)
        lam[73] = lam[72] * (1 - 2e-9)
        self.assertEqual(cc.band_of(lam)[73], 1)

    def test_kept_mask_is_strict(self):
        np.testing.assert_array_equal(cc.kept_mask(np.array([1.0, 1e-12, 2e-12]), 1.0), [True, False, True])

    def test_band_of_exactly_ten_is_used(self):
        self.assertEqual(cc.bands_used(cc.band_of(np.geomspace(1, 1e-3, 83)))["R2"], {"n": 10, "used": True})
        self.assertEqual(cc.bands_used(cc.band_of(np.geomspace(1, 1e-3, 82)))["R2"], {"n": 9, "used": False})

    def test_bands_used(self):
        u = cc.bands_used(cc.band_of(np.geomspace(1, 1e-3, 80)))
        self.assertEqual(u, {"R1": {"n": 73, "used": True}, "R2": {"n": 7, "used": False},
                             "R3": {"n": 0, "used": False}})


class GuardLabel(unittest.TestCase):
    def test_guard_values(self):
        psi = np.array([1.0, 2.0, 3.0, 4.0])
        g = cc.guard(psi)
        se = psi.std(ddof=1) / 2
        self.assertAlmostEqual(g["X"], 2.5)
        self.assertAlmostEqual(g["SE"], se)
        self.assertAlmostEqual(g["h"], stats.t.ppf(0.975, 3) * se)

    def test_guard_refuses(self):
        self.assertIn("refused", cc.guard(np.ones(5)))
        r = cc.guard(np.array([1.0]))
        self.assertIn("refused", r)
        self.assertIsNone(r["SE"])
        r = cc.guard(np.array([1.0, np.nan]))
        self.assertIsNone(r["X"])
        self.assertIsNone(r["SE"])

    def test_labels(self):
        self.assertEqual(cc.label(0.5, 0.1), "over")
        self.assertEqual(cc.label(1.0, 0.1), "covers")
        self.assertEqual(cc.label(2.0, 0.1), "under")
        self.assertEqual(cc.label(0.9, 0.1), "covers")          # lo = 0.8 exactly
        self.assertEqual(cc.label(1.15, 0.1), "covers")         # hi = 1.25 exactly
        self.assertEqual(cc.label(0.8, 0.1), "unresolved across over/covers")
        self.assertEqual(cc.label(1.25, 0.1), "unresolved across covers/under")
        self.assertEqual(cc.label(1.0, 1.0), "unresolved across over/covers/under")
        self.assertEqual(cc.label(0.7, 0.1 - 1e-12), "over")
        self.assertEqual(cc.label(0.8, 0.0), "covers")
        self.assertEqual(cc.label(1.25, 0.0), "covers")
        self.assertEqual(cc.label(1.2, 0.08), "unresolved across covers/under")


class ModeReadings(unittest.TestCase):
    def test_hand_oracle(self):
        E = np.array([[1.0, 2.0], [3.0, -2.0]])           # V = diag(4, 1): z = (x/2, y)
        r = cc.mode_readings(E, np.diag([4.0, 1.0]), np.diag([4.0, 1.0]))
        np.testing.assert_allclose(r["m"], [1.0, 0.0])
        np.testing.assert_allclose(r["v"], [0.25, 4.0])
        np.testing.assert_allclose(r["q"], [1.25, 4.0])
        self.assertAlmostEqual(r["M"]["X"], (1.25 + 4.0) / 2)
        self.assertAlmostEqual(r["M_split"]["mean_part"], 0.5)
        self.assertAlmostEqual(r["M_split"]["spread_part"], 2.125)
        np.testing.assert_allclose(r["_Z"], [[0.5, 2.0], [1.5, -2.0]])
        infl = (r["_Z"] - r["m"]) ** 2 - r["v"]
        psi = infl.sum(axis=1) / 2
        self.assertEqual(r["F"]["X"], float(r["v"].mean()))
        self.assertAlmostEqual(r["F"]["SE"], float(psi.std(ddof=1) / math.sqrt(2)))
        self.assertNotIn("label", r["F"])

    def test_spread_guard_refuses_at_zero_se(self):
        E = np.array([[1.0, 1.0], [-1.0, -1.0], [1.0, 1.0], [-1.0, -1.0]])   # (z - m)^2 = v for every toy
        r = cc.mode_readings(E, np.eye(2), np.eye(2))
        self.assertIn("refused", r["F"])

    def test_gaussian_reads_about_one_and_identities(self):
        n = 30
        V = rand_psd(n, seed=7, spread=2)
        E = np.random.default_rng(8).multivariate_normal(np.zeros(n), V, size=4000)
        r = cc.mode_readings(E, V, V)
        self.assertEqual(r["ndf"], n)
        self.assertLess(abs(r["M"]["X"] - 1.0), 0.05)
        self.assertLess(r["identity_q_m2_v_max_abs"], 1e-12)
        self.assertAlmostEqual(r["M_split"]["mean_part"] + r["M_split"]["spread_part"], r["M"]["X"], places=12)
        self.assertEqual(r["bands"]["R2"], {"n": 0, "used": False, "dropped": "R2 holds 0 kept modes, fewer than 10"})
        self.assertIn("guard", r["bands"]["R1"])

    def test_no_kept_mode_refuses(self):
        with self.assertRaises(cc.Refusal):
            cc.mode_readings(np.ones((3, 2)), np.zeros((2, 2)), np.eye(2))

    def test_cut_referenced_to_fluctuation_block(self):
        n = 6
        V_F = np.diag([1.0, 1.0, 1.0, 1.0, 1.0, 1e-11])
        b = np.zeros(n)
        b[0] = 1e3
        V = V_F + np.outer(b, b)
        E = np.random.default_rng(2).normal(size=(50, n))
        self.assertEqual(cc.mode_readings(E, V, V_F)["ndf"], 6)
        self.assertEqual(cc.mode_readings(E, V, V)["ndf"], 5)

    def test_band_guard_and_dropped_band(self):
        n = 80
        V = rand_psd(n, seed=11, spread=2)
        E = np.random.default_rng(12).multivariate_normal(np.zeros(n), V, size=300)
        r = cc.mode_readings(E, V, V)
        Z, band = r["_Z"], r["band"]
        psi = np.sum(Z[:, band == 0] ** 2, axis=1) / 73
        self.assertAlmostEqual(r["bands"]["R1"]["guard"]["X"], float(psi.mean()), places=12)
        self.assertAlmostEqual(r["bands"]["R1"]["Q_R"], float(r["q"][band == 0].mean()), places=12)
        self.assertEqual(set(r["bands"]["R2"]), {"n", "used", "dropped"})   # 7 modes: no statistics
        infl = (Z - r["m"]) ** 2 - r["v"]
        g = r["bands"]["R1"]["guard_F_R"]
        self.assertEqual(g["X"], r["bands"]["R1"]["F_R"])
        self.assertAlmostEqual(g["SE"], float((infl[:, band == 0].sum(axis=1) / 73).std(ddof=1) / math.sqrt(300)))

    def test_evr_agreement(self):
        n = 20
        V = rand_psd(n, seed=13, spread=2)
        E = np.random.default_rng(14).multivariate_normal(np.zeros(n), V, size=500)
        a = cc.evr_agreement(E, V, V, cc.mode_readings(E, V, V))
        self.assertEqual(a["ndf_evr"], n)
        self.assertLess(a["max_d"], 1e-8)
        self.assertEqual((a["unresolved_ranks"], a["ranks_without_d"]), ([], 0))

    def test_evr_tied_space_agrees_and_zero_energy_counted(self):
        V = np.diag([3.0, 2.0, 2.0, 2.0, 1.0])
        E = np.random.default_rng(15).normal(size=(200, 5))
        E[:, 4] = 0.0                                       # the rank-5 mode has m = v = 0
        a = cc.evr_agreement(E, V, V, cc.mode_readings(E, V, V))
        self.assertLess(a["max_d"], 1e-12)
        self.assertEqual(a["ranks_without_d"], 1)

    def test_evr_partition_differs_is_not_compared(self):
        V = np.diag([3.0, 2.0, 1.5, 1.0])
        E = np.random.default_rng(16).normal(size=(100, 4))
        rd = cc.mode_readings(E, V, V)
        lk = rd["lambda_kept"].copy()
        lk[2] = lk[1]                                         # numpy's record now claims an exact tie at ranks 2-3
        a = cc.evr_agreement(E, V, V, dict(rd, lambda_kept=lk))
        self.assertEqual(a["partition_differs_ranks"], [2, 3])

    def test_evr_refusal_is_a_diagnostic(self):
        V = np.eye(3)
        E = np.ones((4, 3))
        rd = cc.mode_readings(E, V, V)
        real = cc.mode_readings

        def fake(E_, V_, VF_, driver="numpy"):
            if driver == "evr":
                raise cc.Refusal("readings: no kept mode")
            return real(E_, V_, VF_, driver)
        with mock.patch.object(cc, "mode_readings", fake):
            a = cc.evr_agreement(E, V, V, rd)
        self.assertEqual(a["ndf_evr"], 0)
        self.assertIn("refused", a["note"])

    def test_evr_count_mismatch_is_noted(self):
        V = np.eye(5)
        E = np.ones((3, 5))
        r = dict(cc.mode_readings(E, V, V), ndf=4)
        self.assertIn("note", cc.evr_agreement(E, V, V, r))


class Residual(unittest.TestCase):
    def setUp(self):
        self.n = 8
        self.Q = np.linalg.qr(np.random.default_rng(21).normal(size=(self.n, self.n)))[0]
        self.lam = np.array([1.0, 0.5, 0.2, 0.1, 0.05, 1e-3, 1e-7, 1e-9])   # last two below 1e-6: tail
        self.V = (self.Q * self.lam) @ self.Q.T

    def mat(self, lam, Q=None):
        Q = self.Q if Q is None else Q
        return (Q * lam) @ Q.T

    def rot(self, pairs, th):
        R = np.eye(self.n)
        for a, b in pairs:
            R[[a, a, b, b], [a, b, a, b]] = [math.cos(th), -math.sin(th), math.sin(th), math.cos(th)]
        return self.Q @ R

    def test_same_matrix(self):
        r = cc.residual_rule(self.V, self.V, self.V, self.V)
        self.assertEqual(r["n_well"], 6)
        self.assertEqual([(t["rank"], t["ref_kept"]) for t in r["below_well_modes"]], [(7, True), (8, True)])
        self.assertLess(r["residual"], 1e-12)
        self.assertFalse(r["fires"])

    def test_dropped_well_direction_fires(self):
        lam = self.lam.copy()
        lam[2] = 0.0
        Vn = self.mat(lam)
        r = cc.residual_rule(self.V, self.V, Vn, Vn)
        self.assertAlmostEqual(r["residual"], 1.0, places=8)
        self.assertTrue(r["fires"])
        self.assertAlmostEqual(r["directed_angle_deg"], 90.0, places=4)

    def test_dropped_tail_direction_does_not_fire(self):
        lam = self.lam.copy()
        lam[6] = 0.0
        Vn = self.mat(lam)
        r = cc.residual_rule(self.V, self.V, Vn, Vn)
        self.assertFalse(r["fires"])
        self.assertAlmostEqual(r["below_well_max_residual"], 1.0, places=6)
        self.assertAlmostEqual(r["below_well_modes"][0]["residual"], 1.0, places=6)
        self.assertEqual(r["below_well_modes"][0]["rank"], 7)

    def test_below_well_lists_modes_the_reference_drops(self):
        lam = self.lam.copy()
        lam[7] = 1e-14                                          # below the reference's own 1e-12 cut
        V = self.mat(lam)
        r = cc.residual_rule(V, V, V, V)
        self.assertEqual([(t["rank"], t["ref_kept"]) for t in r["below_well_modes"]], [(7, True), (8, False)])

    def test_well_spans_angle_is_printed_beside_the_trigger(self):
        C = np.diag([1.0, 1e-7])                                # the codex-school2 example
        Cr = np.diag([0.0, 1e8])
        r = cc.residual_rule(C, C, C + Cr, C + Cr)
        self.assertLess(r["directed_angle_deg"], 1e-6)          # e_1 lies in the new kept span: the rule does not fire
        self.assertFalse(r["fires"])
        self.assertAlmostEqual(r["well_spans_max_angle_deg"], 90.0)   # but the well-determined spans are orthogonal

    def test_exact_bar_does_not_fire(self):
        u = np.array([math.sqrt(0.99), 0.1])
        Vn = np.outer(u, u)
        r = cc.residual_rule(np.diag([1.0, 0.0]), np.diag([1.0, 0.0]), Vn, Vn)
        self.assertEqual(r["residual"], 0.1)
        self.assertFalse(r["fires"])

    def test_directed_extra_span_passes(self):
        lam = self.lam.copy()
        lam[7] = 0.0
        Vr = self.mat(lam)
        self.assertLess(cc.residual_rule(Vr, Vr, self.V, self.V)["residual"], 1e-10)

    def test_rotation_angle(self):
        lam = self.lam.copy()
        lam[6] = 0.0
        Vn = self.mat(lam, self.rot([(0, 6)], 0.2))
        r = cc.residual_rule(self.V, self.V, Vn, Vn)
        self.assertAlmostEqual(r["residual"], math.sin(0.2), places=8)
        self.assertTrue(r["fires"])

    def test_spectral_not_frobenius(self):
        lam = self.lam.copy()
        lam[6] = lam[7] = 0.0
        Vn = self.mat(lam, self.rot([(0, 6), (1, 7)], 0.05))
        self.assertAlmostEqual(cc.residual_rule(self.V, self.V, Vn, Vn)["residual"], math.sin(0.05), places=8)

    def test_bar_is_strict(self):
        self.assertEqual(cc.RESIDUAL_MAX, 0.1)
        lam = self.lam.copy()
        lam[6] = 0.0
        Vn = self.mat(lam, self.rot([(0, 6)], math.asin(0.0999)))
        self.assertFalse(cc.residual_rule(self.V, self.V, Vn, Vn)["fires"])

    def test_well_cut_value_and_equality(self):
        lam = self.lam.copy()
        lam[6] = 3e-6                                           # well under 1e-6, not under 1e-5
        V = self.mat(lam)
        self.assertEqual(cc.residual_rule(V, V, V, V)["n_well"], 7)
        D = np.diag([1.0, 0.5, 1e-6, 1e-7])                     # exactly 1e-6 lambda_1: well-determined (>=)
        self.assertEqual(cc.residual_rule(D, D, D, D)["n_well"], 3)

    def test_well_cut_uses_reference_fluctuation(self):
        self.assertEqual(cc.residual_rule(self.V, self.V * 1e-2, self.V, self.V)["n_well"], 7)   # cut 1e-8: 1e-7 in, 1e-9 out

    def test_cut_diagnostic(self):
        lam = self.lam.copy()
        lam[7] = 0.0
        Vn = self.mat(lam)
        d = cc.cut_diagnostic(self.V, self.V, Vn, Vn)
        self.assertEqual((d["ndf_ref"], d["ndf_new"], d["n_ref_kept_outside_new_kept_span"]), (8, 7, 1))
        self.assertEqual(d["ref_kept_outside_new_kept_span"][0]["rank"], 8)
        self.assertAlmostEqual(d["ref_kept_outside_new_kept_span"][0]["residual"], 1.0, places=6)
        self.assertAlmostEqual(d["max_residual_of_ref_kept_modes"], 1.0, places=6)
        self.assertEqual(len(d["kept_ref_lambda"]), 8)
        self.assertEqual(len(d["kept_new_lambda"]), 7)
        self.assertAlmostEqual(d["new_smallest_kept"], 1e-7, places=12)
        self.assertLess(abs(d["new_largest_dropped"]), 1e-12)

    def test_angles(self):
        A = np.eye(4)[:, :2]
        self.assertLess(cc.principal_angles_deg(A, A).max(), 1e-6)
        self.assertAlmostEqual(cc.principal_angles_deg(A, np.eye(4)[:, 2:]).max(), 90.0)


class Json(unittest.TestCase):
    def test_jsonable(self):
        rec = {"a": np.float64("nan"), "b": [np.float32(0.5), np.int64(3), np.bool_(True)], "c": np.array([1.0, np.inf]),
               "d": (None, "s"), 4: float("-inf")}
        s = json.dumps(cc.jsonable(rec), allow_nan=False)
        self.assertEqual(json.loads(s), {"a": None, "b": [0.5, 3, True], "c": [1.0, None], "d": [None, "s"], "4": None})
        with self.assertRaises(TypeError):
            cc.jsonable(object())


if __name__ == "__main__":
    unittest.main()
