"""Unit tests for covfix_core (COVFIX-DECLARATION.md rev 11.4 sections 2, 5.2, 6.1). Synthetic inputs only.

  python3 -B -m unittest -v test_covfix_core.py
"""
from __future__ import annotations

import math
import unittest

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
        # bitwise the form cov2d_blocks.assemble uses for C_model_abs (cov2d_blocks.py:143)
        np.testing.assert_array_equal(cc.absolute(C, x), x[:, None] * C * x[None, :])


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


class EigBasis(unittest.TestCase):
    def test_descending_reconstructs_and_signs(self):
        V = rand_psd(6, seed=3)
        lam, U = cc.eig_basis(V)
        self.assertTrue(np.all(np.diff(lam) <= 0))
        np.testing.assert_allclose((U * lam) @ U.T, V, atol=1e-13)
        idx = np.argmax(np.abs(U), axis=0)
        self.assertTrue(np.all(U[idx, np.arange(6)] > 0))

    def test_sign_fix_flips_negative_leader(self):
        U = np.array([[-0.8, 0.6], [0.6, 0.8]])
        F = cc._sign_fix(U)
        np.testing.assert_array_equal(F[:, 0], [0.8, -0.6])
        np.testing.assert_array_equal(F[:, 1], U[:, 1])

    def test_identity_is_canonical_axes(self):
        lam, U = cc.eig_basis(np.eye(4))
        np.testing.assert_allclose(U, np.eye(4), atol=1e-15)

    def test_tied_subspace_does_not_depend_on_rotation(self):
        rng = np.random.default_rng(5)
        Q = np.linalg.qr(rng.normal(size=(5, 5)))[0]
        lam = np.array([3.0, 2.0, 2.0, 1.0, 0.5])
        out = []
        for th in (0.0, 0.7):
            R = np.eye(5)
            R[1:3, 1:3] = [[math.cos(th), -math.sin(th)], [math.sin(th), math.cos(th)]]
            Qr = Q @ R
            V = (Qr * lam) @ Qr.T
            V = 0.5 * (V + V.T)
            l2, U2 = cc.eig_basis(V)
            out.append((l2, U2))
        # equal-to-float ties only arise when the solver returns them; force exact ties to exercise the branch
        U0 = Q[:, 1:3]
        A = cc._canonical_tied(U0)
        B = cc._canonical_tied(U0 @ np.array([[math.cos(0.7), -math.sin(0.7)], [math.sin(0.7), math.cos(0.7)]]))
        np.testing.assert_allclose(A, B, atol=1e-12)
        np.testing.assert_allclose(A.T @ A, np.eye(2), atol=1e-12)

    def test_canonical_tied_skips_null_projection(self):
        U = np.array([[0.0], [1.0], [0.0]])           # e_1 projects to zero; e_2 spans it
        np.testing.assert_allclose(cc._canonical_tied(U), U, atol=0)

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
        lam = np.geomspace(1, 1e-6, 205)
        b = cc.band_of(lam)
        self.assertEqual(int(np.sum(b == 0)), 73)
        self.assertEqual(int(np.sum(b == 1)), 66)
        self.assertEqual(int(np.sum(b == 2)), 66)
        self.assertEqual(b[72], 0)
        self.assertEqual(b[73], 1)
        self.assertEqual(b[138], 1)
        self.assertEqual(b[139], 2)

    def test_cluster_straddling_edges_goes_low(self):
        lam = np.geomspace(1, 1e-6, 205)
        lam[73] = lam[72] * (1 - 0.5e-9)       # ranks 73 and 74 tie within 1e-9
        lam[139] = lam[138] * (1 - 0.5e-9)     # ranks 139 and 140
        b = cc.band_of(lam)
        self.assertEqual(b[73], 0)
        self.assertEqual(b[139], 1)
        self.assertEqual(b[140], 2)

    def test_gap_above_tie_not_clustered(self):
        lam = np.geomspace(1, 1e-6, 205)
        lam[73] = lam[72] * (1 - 2e-9)
        self.assertEqual(cc.band_of(lam)[73], 1)

    def test_kept_mask_is_strict(self):
        np.testing.assert_array_equal(cc.kept_mask(np.array([1.0, 1e-12, 2e-12]), 1.0), [True, False, True])

    def test_band_of_exactly_ten_is_used(self):
        u = cc.bands_used(cc.band_of(np.geomspace(1, 1e-3, 83)))
        self.assertEqual(u["R2"], {"n": 10, "used": True})

    def test_bands_used(self):
        u = cc.bands_used(cc.band_of(np.geomspace(1, 1e-3, 80)))
        self.assertEqual(u["R1"], {"n": 73, "used": True})
        self.assertEqual(u["R2"], {"n": 7, "used": False})
        self.assertEqual(u["R3"], {"n": 0, "used": False})


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
        self.assertIn("refused", cc.guard(np.array([1.0])))
        self.assertIn("refused", cc.guard(np.array([1.0, np.nan])))

    def test_labels(self):
        self.assertEqual(cc.label(0.5, 0.1), "over")
        self.assertEqual(cc.label(1.0, 0.1), "covers")
        self.assertEqual(cc.label(2.0, 0.1), "under")
        self.assertEqual(cc.label(0.9, 0.1), "covers")          # lo = 0.8 exactly
        self.assertEqual(cc.label(1.15, 0.1), "covers")         # hi = 1.25 exactly
        self.assertEqual(cc.label(0.8, 0.1), "unresolved across over/covers")
        self.assertEqual(cc.label(1.25, 0.1), "unresolved across covers/under")
        self.assertEqual(cc.label(1.0, 1.0), "unresolved across over/covers/under")
        self.assertEqual(cc.label(0.7, 0.1 - 1e-12), "over")    # hi just below 0.8
        self.assertEqual(cc.label(0.8, 0.0), "covers")          # [0.8, 0.8] lies inside covers
        self.assertEqual(cc.label(1.25, 0.0), "covers")
        self.assertEqual(cc.label(1.2, 0.08), "unresolved across covers/under")   # hi 1.28 crosses 1.25


class ModeReadings(unittest.TestCase):
    def test_gaussian_reads_about_one_and_identities(self):
        n = 30
        V = rand_psd(n, seed=7, spread=2)
        E = np.random.default_rng(8).multivariate_normal(np.zeros(n), V, size=4000)
        r = cc.mode_readings(E, V, V)
        self.assertEqual(r["ndf"], n)
        self.assertLess(abs(r["M"]["X"] - 1.0), 0.05)
        self.assertLess(r["identity_q_m2_v_max_abs"], 1e-12)
        self.assertAlmostEqual(r["M_split"]["mean_part"] + r["M_split"]["spread_part"], r["M"]["X"], places=12)
        self.assertAlmostEqual(float(r["q"].mean()), r["M"]["X"], places=12)
        self.assertEqual(r["bands"]["R2"]["n"], 0)
        self.assertIn("dropped", r["bands"]["R2"])
        self.assertIn("guard", r["bands"]["R1"])

    def test_cut_referenced_to_fluctuation_block(self):
        n = 6
        V_F = np.diag([1.0, 1.0, 1.0, 1.0, 1.0, 1e-11])          # every mode above 1e-12 of V_F's lambda_1
        b = np.zeros(n)
        b[0] = 1e3
        V = V_F + np.outer(b, b)                                # V's own lambda_1 is 1e6: 1e-11 < 1e-12 * 1e6
        E = np.random.default_rng(2).normal(size=(50, n))
        self.assertEqual(cc.mode_readings(E, V, V_F)["ndf"], 6)
        self.assertEqual(cc.mode_readings(E, V, V)["ndf"], 5)

    def test_band_guard_is_band_chi2_over_n(self):
        n = 80
        V = rand_psd(n, seed=11, spread=2)
        E = np.random.default_rng(12).multivariate_normal(np.zeros(n), V, size=300)
        r = cc.mode_readings(E, V, V)
        Z, band = r["_Z"], r["band"]
        psi = np.sum(Z[:, band == 0] ** 2, axis=1) / 73
        self.assertAlmostEqual(r["bands"]["R1"]["guard"]["X"], float(psi.mean()), places=12)
        self.assertAlmostEqual(r["bands"]["R1"]["Q_R"], float(r["q"][band == 0].mean()), places=12)
        self.assertNotIn("guard", r["bands"]["R2"])               # 7 modes

    def test_evr_agreement(self):
        n = 20
        V = rand_psd(n, seed=13, spread=2)
        E = np.random.default_rng(14).multivariate_normal(np.zeros(n), V, size=500)
        r = cc.mode_readings(E, V, V)
        a = cc.evr_agreement(E, V, V, r)
        self.assertEqual(a["ndf_evr"], n)
        self.assertLess(a["max_d"], 1e-8)
        self.assertEqual(a["unresolved_ranks"], [])

    def test_evr_count_mismatch_is_noted(self):
        n = 5
        V = np.eye(n)
        E = np.ones((3, n))
        r = cc.mode_readings(E, V, V)
        r = dict(r, ndf=4)
        self.assertIn("note", cc.evr_agreement(E, V, V, r))


class Residual(unittest.TestCase):
    def setUp(self):
        self.n = 8
        rng = np.random.default_rng(21)
        self.Q = np.linalg.qr(rng.normal(size=(self.n, self.n)))[0]
        self.lam = np.array([1.0, 0.5, 0.2, 0.1, 0.05, 1e-3, 1e-7, 1e-9])   # last two below 1e-6: tail
        self.V = (self.Q * self.lam) @ self.Q.T

    def test_same_matrix(self):
        r = cc.residual_rule(self.V, self.V, self.V, self.V)
        self.assertEqual(r["n_well"], 6)
        self.assertEqual(r["tail_modes"], 2)
        self.assertLess(r["residual"], 1e-12)
        self.assertFalse(r["fires"])

    def test_dropped_well_direction_fires(self):
        lam = self.lam.copy()
        lam[2] = 0.0
        Vn = (self.Q * lam) @ self.Q.T
        r = cc.residual_rule(self.V, self.V, Vn, Vn)
        self.assertAlmostEqual(r["residual"], 1.0, places=8)
        self.assertTrue(r["fires"])
        self.assertAlmostEqual(r["max_principal_angle_deg"], 90.0, places=4)

    def test_dropped_tail_direction_does_not_fire(self):
        lam = self.lam.copy()
        lam[6] = 0.0
        Vn = (self.Q * lam) @ self.Q.T
        r = cc.residual_rule(self.V, self.V, Vn, Vn)
        self.assertFalse(r["fires"])
        self.assertAlmostEqual(r["tail_max_residual"], 1.0, places=6)

    def test_directed_extra_span_passes(self):
        lam = self.lam.copy()
        lam[7] = 0.0
        Vr = (self.Q * lam) @ self.Q.T
        r = cc.residual_rule(Vr, Vr, self.V, self.V)            # new span is larger
        self.assertLess(r["residual"], 1e-10)

    def test_rotation_angle(self):
        th = 0.2
        R = np.eye(self.n)
        R[[0, 0, 6, 6], [0, 6, 0, 6]] = [math.cos(th), -math.sin(th), math.sin(th), math.cos(th)]
        lam = self.lam.copy()
        lam[6] = 0.0                                            # rotate well mode 1 toward a dropped axis
        Qn = self.Q @ R
        Vn = (Qn * lam) @ Qn.T
        r = cc.residual_rule(self.V, self.V, Vn, Vn)
        self.assertAlmostEqual(r["residual"], math.sin(th), places=8)
        self.assertTrue(r["fires"])

    def test_spectral_not_frobenius(self):
        th = 0.05                                               # two well modes, each rotated toward a dropped axis
        R = np.eye(self.n)
        for a, b in ((0, 6), (1, 7)):
            R[[a, a, b, b], [a, b, a, b]] = [math.cos(th), -math.sin(th), math.sin(th), math.cos(th)]
        lam = self.lam.copy()
        lam[6] = lam[7] = 0.0
        Qn = self.Q @ R
        Vn = (Qn * lam) @ Qn.T
        r = cc.residual_rule(self.V, self.V, Vn, Vn)
        self.assertAlmostEqual(r["residual"], math.sin(th), places=8)   # Frobenius would be sqrt(2) sin(th)

    def test_bar_is_strict(self):
        self.assertEqual(cc.RESIDUAL_MAX, 0.1)
        th = math.asin(0.0999)
        R = np.eye(self.n)
        R[[0, 0, 6, 6], [0, 6, 0, 6]] = [math.cos(th), -math.sin(th), math.sin(th), math.cos(th)]
        lam = self.lam.copy()
        lam[6] = 0.0
        Qn = self.Q @ R
        Vn = (Qn * lam) @ Qn.T
        self.assertFalse(cc.residual_rule(self.V, self.V, Vn, Vn)["fires"])

    def test_well_cut_value(self):
        lam = self.lam.copy()
        lam[6] = 3e-6                                           # well under 1e-6, not under 1e-5
        V = (self.Q * lam) @ self.Q.T
        self.assertEqual(cc.residual_rule(V, V, V, V)["n_well"], 7)

    def test_well_cut_uses_reference_fluctuation(self):
        F = self.V * 1e-3                                       # smaller lambda_1(F): more modes well-determined
        self.assertEqual(cc.residual_rule(self.V, F, self.V, self.V)["n_well"], 7)

    def test_cut_diagnostic(self):
        lam = self.lam.copy()
        lam[7] = 0.0
        Vn = (self.Q * lam) @ self.Q.T
        d = cc.cut_diagnostic(self.V, self.V, Vn, Vn)
        self.assertEqual(d["ndf_ref"], 8)
        self.assertEqual(d["ndf_new"], 7)
        self.assertEqual(d["ref_kept_outside_new_kept_span"], 1)
        self.assertAlmostEqual(d["max_residual_of_ref_kept_modes"], 1.0, places=6)
        self.assertAlmostEqual(d["new_smallest_kept"], 1e-7, places=12)
        self.assertLess(abs(d["new_largest_dropped"]), 1e-12)

    def test_angles(self):
        A = np.eye(4)[:, :2]
        self.assertLess(cc.principal_angles_deg(A, A).max(), 1e-6)
        self.assertAlmostEqual(cc.principal_angles_deg(A, np.eye(4)[:, 2:]).max(), 90.0)


if __name__ == "__main__":
    unittest.main()
