#!/usr/bin/env python3
"""Z's assembly algebra and the five inflation gates -- mutation-tested, both directions.

THE TEST THAT CARRIES THE MOST WEIGHT is `AnUninflatedObjectPassesFourGatesAndFailsOnlyTheFifth`.
Spec review round 2 found gates 1, 2, 4 and 5 JOINTLY SATISFIABLE by an object with `g == 1`
everywhere -- an uninflated candidate wearing Z's shape. That test asserts the four DO pass on
exactly such an object, which is the only way to show the fifth gate is load-bearing rather than
decorative. Asserting only that G3 fails would leave open that some other gate caught it first.

Every mutation below is checked against a clean control built by the same fixture, so a gate that
fired for an unrelated reason cannot be mistaken for a gate that works.
"""
import os
import sys
import unittest

import numpy as np

ND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ND not in sys.path:
    sys.path.insert(0, ND)

import z_assembly as za          # noqa: E402
import z_contract as zc          # noqa: E402


def psd(rng, n, scale=1.0):
    A = rng.standard_normal((n, n))
    return scale * (A @ A.T) / n


def build_scenario(n=24, n_pinned=3, seed=7):
    """A consistent, gate-passing Z. Built from the PRODUCER's algebra, not from the gates'.

    The last `n_pinned` bins have a zero vertical block variance, so `g` is pinned to 1 there --
    the case §1.3a singles out and the one a producer is most likely to get wrong.
    """
    rng = np.random.default_rng(seed)
    S_V = psd(rng, n, 1.0)
    # Zero whole rows/columns so the block sum stays PSD with an exactly-zero diagonal entry.
    for i in range(n - n_pinned, n):
        S_V[i, :] = 0.0
        S_V[:, i] = 0.0
    v_blk = np.diag(S_V).copy()

    # The mean-centred unified diagonal, and the shift that separates the two variants.
    v_uni_mean = v_blk * rng.uniform(0.8, 1.6, size=n)
    v_uni_mean[v_blk == 0.0] = 0.0
    ms = rng.normal(0.0, 0.05, size=n)
    v_uni_cv = v_uni_mean + ms ** 2          # the exact coupling C_cv = C_mean + ms ms^T

    g, pinned = za.compute_g(v_uni_cv, v_blk)
    S_R, S_A = psd(rng, n, 0.3), psd(rng, n, 0.2)
    C_stat, C_ML = psd(rng, n, 0.1), psd(rng, n, 0.05)
    C_Z = za.assemble(g, S_V, S_R, S_A, C_stat, C_ML)
    return dict(n=n, S_V=S_V, S_R=S_R, S_A=S_A, C_stat=C_stat, C_ML=C_ML,
                v_blk=v_blk, v_uni_cv=v_uni_cv, v_uni_mean=v_uni_mean, ms=ms,
                g=g, pinned=pinned, C_Z=C_Z)


def gate_kwargs(s, **over):
    kw = dict(C_Z=s["C_Z"], g=s["g"], pinned_mask=s["pinned"], v_uni=s["v_uni_cv"],
              v_blk=s["v_blk"], cov_vert_sum=s["S_V"], cov_residual_sum=s["S_R"],
              cov_lateral_sum=s["S_A"], cov_stat=s["C_stat"], cov_ml=s["C_ML"],
              bands_vert=list(zc.VERT_BANDS),
              bands_residual=[f"r{i}" for i in range(zc.N_RESIDUAL)],
              bands_lateral=list(zc.LATERAL_BANDS))
    kw.update(over)
    return kw


class TheCleanObjectPasses(unittest.TestCase):
    """The control. Without it, every failure below could be the fixture rather than the gate."""

    def test_all_five_gates_pass_on_a_consistent_z(self):
        s = build_scenario()
        out = za.run_inflation_gates(**gate_kwargs(s))
        self.assertEqual(set(out), {"G1_closure_identity", "G2_g_domain", "G3_g_reconstruction",
                                    "G4_symmetry_psd", "G5_band_partition"})
        self.assertLessEqual(out["G1_closure_identity"]["max_rel_residual"], zc.IDENTITY_RTOL)
        self.assertGreater(out["G2_g_domain"]["n_gt_one"], 0,
                           "fixture is degenerate: nothing is actually inflated, so the gates "
                           "below would be tested against an uninflated control")
        self.assertEqual(out["G2_g_domain"]["n_pinned"], 3)

    def test_g_is_exactly_one_where_the_block_variance_is_zero(self):
        s = build_scenario()
        self.assertTrue(np.all(s["g"][s["v_blk"] == 0.0] == 1.0))

    def test_g_is_never_below_one(self):
        s = build_scenario()
        self.assertGreaterEqual(float(s["g"].min()), 1.0)


class AnUninflatedObjectPassesFourGatesAndFailsOnlyTheFifth(unittest.TestCase):
    """Spec review round 2's finding, as an executable test.

    An object built and recorded with `g == 1` while its own operands say otherwise satisfies
    closure, the floor, the zero rule and PSD. Only the independent reconstruction sees it.
    """

    def setUp(self):
        s = build_scenario()
        ones = np.ones_like(s["g"])
        s["g"] = ones
        s["C_Z"] = za.assemble(ones, s["S_V"], s["S_R"], s["S_A"], s["C_stat"], s["C_ML"])
        self.s = s

    def test_G1_closure_passes_on_the_uninflated_object(self):
        za.gate_closure_identity(self.s["C_Z"], self.s["g"], self.s["S_V"], self.s["S_R"],
                                 self.s["S_A"], self.s["C_stat"], self.s["C_ML"])

    def test_G2_g_domain_passes_on_the_uninflated_object(self):
        za.gate_g_domain(self.s["g"], self.s["pinned"], self.s["v_blk"])

    def test_G4_psd_passes_on_the_uninflated_object(self):
        za.gate_symmetry_psd(self.s["C_Z"])

    def test_G5_partition_passes_on_the_uninflated_object(self):
        zc.check_band_partition(list(zc.VERT_BANDS),
                                [f"r{i}" for i in range(zc.N_RESIDUAL)],
                                list(zc.LATERAL_BANDS))

    def test_G3_reconstruction_is_the_only_gate_that_catches_it(self):
        with self.assertRaises(zc.ZContractError) as cm:
            za.gate_g_reconstruction(self.s["g"], self.s["v_uni_cv"], self.s["v_blk"])
        self.assertIn("g reconstruction", str(cm.exception))

    def test_the_full_suite_therefore_still_refuses_it(self):
        with self.assertRaises(zc.ZContractError):
            za.run_inflation_gates(**gate_kwargs(self.s))


class TheDroppedShiftIsCaughtByTheVariantCoupling(unittest.TestCase):
    """§3.3 condition 4b's second failure -- `g^cv` equal to `g^mean` -- via an exact identity."""

    def test_the_correct_coupling_passes(self):
        s = build_scenario()
        out = za.check_variant_coupling(s["v_uni_cv"], s["v_uni_mean"], s["ms"])
        self.assertLessEqual(out["max_rel_residual"], zc.IDENTITY_RTOL)
        self.assertGreater(out["ms_norm"], 0.0)

    def test_reusing_one_variants_operands_for_both_is_caught(self):
        s = build_scenario()
        with self.assertRaises(zc.ZContractError) as cm:
            za.check_variant_coupling(s["v_uni_mean"], s["v_uni_mean"], s["ms"])
        self.assertIn("dropped-shift", str(cm.exception))

    def test_an_identically_zero_shift_is_refused_rather_than_passing_vacuously(self):
        s = build_scenario()
        z = np.zeros_like(s["ms"])
        with self.assertRaises(zc.ZContractError) as cm:
            za.check_variant_coupling(s["v_uni_mean"], s["v_uni_mean"], z)
        self.assertIn("identically zero", str(cm.exception))

    def test_a_perturbed_shift_is_caught(self):
        s = build_scenario()
        bad = s["ms"].copy()
        bad[0] *= 1.5
        with self.assertRaises(zc.ZContractError):
            za.check_variant_coupling(s["v_uni_cv"], s["v_uni_mean"], bad)


class EachGateFiresOnItsOwnDefect(unittest.TestCase):
    def test_g_below_the_floor_is_caught(self):
        s = build_scenario()
        g = s["g"].copy()
        g[0] = 0.5
        with self.assertRaises(zc.ZContractError) as cm:
            za.gate_g_domain(g, s["pinned"], s["v_blk"])
        self.assertIn("floor", str(cm.exception))

    def test_a_pinned_bin_that_is_not_exactly_one_is_caught(self):
        s = build_scenario()
        g = s["g"].copy()
        pinned_idx = np.flatnonzero(s["v_blk"] == 0.0)[0]
        g[pinned_idx] = 1.0 + 1e-12
        with self.assertRaises(zc.ZContractError) as cm:
            za.gate_g_domain(g, s["pinned"], s["v_blk"])
        self.assertIn("not exactly 1", str(cm.exception))

    def test_a_misdeclared_pinned_mask_is_caught_against_v_blk(self):
        s = build_scenario()
        bad_mask = np.zeros_like(s["pinned"])
        with self.assertRaises(zc.ZContractError) as cm:
            za.gate_g_domain(s["g"], bad_mask, s["v_blk"])
        self.assertIn("pinned mask", str(cm.exception))

    def test_a_broken_closure_is_caught(self):
        s = build_scenario()
        C = s["C_Z"].copy()
        C[0, 0] *= 1.01
        with self.assertRaises(zc.ZContractError) as cm:
            za.gate_closure_identity(C, s["g"], s["S_V"], s["S_R"], s["S_A"],
                                     s["C_stat"], s["C_ML"])
        self.assertIn("closure identity", str(cm.exception))

    def test_asymmetry_is_caught(self):
        s = build_scenario()
        C = s["C_Z"].copy()
        C[0, 1] += 0.05 * abs(C).max()
        with self.assertRaises(zc.ZContractError) as cm:
            za.gate_symmetry_psd(C)
        self.assertIn("symmetry", str(cm.exception))

    def test_a_negative_eigenvalue_is_caught_on_the_inflated_object(self):
        s = build_scenario()
        C = s["C_Z"].copy()
        w, V = np.linalg.eigh(0.5 * (C + C.T))
        w[0] = -0.05 * abs(w).max()
        C_bad = V @ np.diag(w) @ V.T
        with self.assertRaises(zc.ZContractError) as cm:
            za.gate_symmetry_psd(C_bad)
        self.assertIn("psd", str(cm.exception))

    def test_cholesky_and_eigvalsh_agree_on_the_clean_object(self):
        s = build_scenario()
        a = za.gate_symmetry_psd(s["C_Z"], method="eigvalsh")
        b = za.gate_symmetry_psd(s["C_Z"], method="cholesky")
        self.assertTrue(a["eigenvalues_computed"])
        self.assertFalse(b["eigenvalues_computed"])

    def test_an_unknown_psd_method_is_refused(self):
        s = build_scenario()
        with self.assertRaises(zc.ZContractError):
            za.gate_symmetry_psd(s["C_Z"], method="probably_fine")


class TheAlgebraRefusesMalformedOperands(unittest.TestCase):
    def test_mismatched_diagonal_shapes(self):
        with self.assertRaises(zc.ZContractError):
            za.compute_g(np.ones(5), np.ones(6))

    def test_negative_variance(self):
        with self.assertRaises(zc.ZContractError):
            za.compute_g(np.array([-1.0, 1.0]), np.array([1.0, 1.0]))

    def test_non_finite_operands(self):
        with self.assertRaises(zc.ZContractError):
            za.compute_g(np.array([np.nan, 1.0]), np.array([1.0, 1.0]))

    def test_assemble_refuses_a_wrongly_shaped_part(self):
        s = build_scenario(n=8)
        with self.assertRaises(zc.ZContractError) as cm:
            za.assemble(s["g"], s["S_V"], np.zeros((7, 7)), s["S_A"], s["C_stat"], s["C_ML"])
        self.assertIn("residual", str(cm.exception))

    def test_inflation_is_the_two_sided_product(self):
        """`D_Z S D_Z`, not `g * S` -- a one-sided scaling would break symmetry silently."""
        n = 6
        g = np.linspace(1.0, 2.0, n)
        S = np.eye(n)
        Z = za.assemble(g, S, np.zeros((n, n)), np.zeros((n, n)),
                        np.zeros((n, n)), np.zeros((n, n)))
        np.testing.assert_allclose(np.diag(Z), g ** 2, rtol=1e-12)
        np.testing.assert_allclose(Z, Z.T, rtol=1e-12)


if __name__ == "__main__":
    unittest.main(verbosity=2)
