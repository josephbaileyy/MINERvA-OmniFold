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


def raw_operands(s, **over):
    """The §1.3b operand set: what a producer hands the validator, per variant.

    Note what is NOT here: `v_uni_cv`. The gate derives it. Passing it would be handing the gate
    the quantity under test, which is the defect the gate exists to catch.
    """
    g_mean, _ = za.compute_g(s["v_uni_mean"], s["v_blk"])
    kw = dict(g_recorded={"mean": g_mean, "cv": s["g"]},
              diag_c_unified_mean=s["v_uni_mean"],
              diag_c_blocksum=s["v_blk"],
              joint_mean_shift=s["ms"])
    kw.update(over)
    return kw


class TheRawOperandReconstructionCatchesWhatG3CANNOT(unittest.TestCase):
    """§1.3b's gate, integrated 2026-09-07 under Joseph's authorization.

    Every test here is paired against `gate_g_reconstruction` where the contrast is the point:
    the older gate takes `v_uni` as an argument, so it cannot see a mis-BUILT `v_uni`.
    """

    def test_a_correct_operand_set_passes_and_reports_it_can_discriminate(self):
        s = build_scenario()
        out = za.gate_raw_operand_reconstruction(**raw_operands(s))
        self.assertTrue(out["discriminating"])
        for variant in ("mean", "cv"):
            self.assertLessEqual(out["per_variant"][variant]["max_rel_diff"], out["rtol"])

    def test_A_DROPPED_MEAN_SHIFT_IS_REFUSED(self):
        """THE reason this gate exists. The producer computed g^cv from v_uni^MEAN.

        Measured on the same input, `gate_g_reconstruction` PASSES: it rebuilds g from the v_uni
        it was handed, and a v_uni^cv missing the shift is perfectly self-consistent with the g
        derived from it. That contrast is asserted below, not described.
        """
        s = build_scenario()
        g_mean, _ = za.compute_g(s["v_uni_mean"], s["v_blk"])

        # the OLD gate, fed the producer's own (wrong) v_uni -- passes, seeing nothing
        za.gate_g_reconstruction(g_mean, s["v_uni_mean"], s["v_blk"])

        # the NEW gate derives v_uni^cv itself, so the same defect cannot hide
        with self.assertRaises(zc.ZContractError) as cm:
            za.gate_raw_operand_reconstruction(
                **raw_operands(s, g_recorded={"mean": g_mean, "cv": g_mean}))
        msg = str(cm.exception)
        self.assertIn("g^cv", msg)
        self.assertNotIn("g^mean", msg)          # cv ALONE is the dropped-shift signature

    def test_an_UNINFLATED_object_is_refused_on_both_variants(self):
        """g == 1 everywhere satisfies the other four gates jointly (§1.3b's own table)."""
        s = build_scenario()
        ones = np.ones_like(s["g"])
        with self.assertRaises(zc.ZContractError) as cm:
            za.gate_raw_operand_reconstruction(
                **raw_operands(s, g_recorded={"mean": ones, "cv": ones}))
        self.assertIn("g^mean", str(cm.exception))
        self.assertIn("g^cv", str(cm.exception))

    def test_ONE_VARIANT_is_refused_because_reuse_is_invisible_from_one(self):
        s = build_scenario()
        g_mean, _ = za.compute_g(s["v_uni_mean"], s["v_blk"])
        for only in ({"mean": g_mean}, {"cv": s["g"]}):
            with self.subTest(supplied=sorted(only)):
                with self.assertRaises(zc.ZContractError) as cm:
                    za.gate_raw_operand_reconstruction(**raw_operands(s, g_recorded=only))
                self.assertIn("BOTH variants", str(cm.exception))

    def test_the_two_variants_are_derived_from_DIFFERENT_v_uni_by_exactly_ms_squared(self):
        """The reuse fault §1.3b names is structurally impossible here; this pins that."""
        s = build_scenario()
        out = za.gate_raw_operand_reconstruction(**raw_operands(s))
        # the gate rebuilt both; if it had reused one v_uni the g's would coincide where ms != 0
        g_mean, _ = za.compute_g(s["v_uni_mean"], s["v_blk"])
        g_cv, _ = za.compute_g(s["v_uni_mean"] + s["ms"] ** 2, s["v_blk"])
        moved = np.sum(g_mean != g_cv)
        self.assertGreater(moved, 0, "fixture cannot distinguish the variants")
        self.assertEqual(out["per_variant"]["mean"]["max_rel_diff"], 0.0)

    def test_a_STORED_cv_diagonal_is_cross_checked_and_never_substituted(self):
        s = build_scenario()
        out = za.gate_raw_operand_reconstruction(
            **raw_operands(s, diag_c_unified_cv=s["v_uni_cv"]))
        self.assertTrue(out["stored_cv_cross_checked"])
        self.assertLessEqual(out["stored_cv_deviation"], 1e-12)

    def test_a_stored_cv_diagonal_that_DISAGREES_is_refused(self):
        s = build_scenario()
        bad = s["v_uni_cv"].copy()
        bad[0] *= 1.5
        with self.assertRaises(zc.ZContractError) as cm:
            za.gate_raw_operand_reconstruction(**raw_operands(s, diag_c_unified_cv=bad))
        self.assertIn("cross-checked, never substituted", str(cm.exception))

    def test_a_stored_cv_diagonal_cannot_RESCUE_a_dropped_shift(self):
        """The substitution hazard, in the direction that matters.

        If the gate had used the stored cv diagonal instead of deriving it, a producer who
        dropped the shift in BOTH the diagonal and the g would be self-consistent and pass.
        """
        s = build_scenario()
        g_mean, _ = za.compute_g(s["v_uni_mean"], s["v_blk"])
        with self.assertRaises(zc.ZContractError):
            za.gate_raw_operand_reconstruction(
                **raw_operands(s, g_recorded={"mean": g_mean, "cv": g_mean},
                               diag_c_unified_cv=s["v_uni_mean"]))

    def test_it_reports_when_the_shift_is_too_small_to_discriminate_AND_names_no_fallback(self):
        """Round 3 and 4 both softened this by naming a check that did not cover it."""
        n = 6
        s = dict(v_uni_mean=np.full(n, 2.0), v_blk=np.full(n, 1.0), ms=np.full(n, 1e-9))
        g_mean, _ = za.compute_g(s["v_uni_mean"], s["v_blk"])
        out = za.gate_raw_operand_reconstruction(
            g_recorded={"mean": g_mean, "cv": g_mean},      # dropped shift, and it PASSES
            diag_c_unified_mean=s["v_uni_mean"], diag_c_blocksum=s["v_blk"],
            joint_mean_shift=s["ms"])
        self.assertFalse(out["discriminating"])
        self.assertIn("NO further gate behind this one", out["note"])
        self.assertIn("UNTESTED", out["note"])

    # ---- ⚠ ROUND-6 BLOCKER 1: discrimination is measured by RUNNING the mutation -----------
    def test_SATURATION_is_reported_as_non_discriminating(self):
        """The reviewer's counterexample verbatim: v_uni_mean=1, v_blk=100, mean_shift=1.

        `g = sqrt(max(v_uni, v_blk))/sqrt(v_blk)` is exactly 1 whenever `v_uni <= v_blk`, so a
        shift of ANY size moves `g` not at all. The first flag compared ms**2 against a tolerance
        on the DIAGONALS and reported discriminating=True on this input -- false assurance about
        a mutation it could not have seen. Three docstring revisions reasoned about `g` while the
        arithmetic measured the diagonals.
        """
        v_mean, v_blk, ms = np.array([1.0]), np.array([100.0]), np.array([1.0])
        g, _ = za.compute_g(v_mean, v_blk)
        self.assertEqual(float(g[0]), 1.0)                       # the fixture really saturates
        out = za.gate_raw_operand_reconstruction(
            g_recorded={"mean": g, "cv": g}, diag_c_unified_mean=v_mean,
            diag_c_blocksum=v_blk, joint_mean_shift=ms)
        self.assertFalse(out["discriminating"])
        self.assertEqual(out["discrimination_blockers"]["n_saturated_v_uni_below_v_blk"], 1)
        self.assertIn("saturated", out["note"])

    def test_PINNED_bins_are_reported_as_non_discriminating(self):
        v_mean, v_blk, ms = np.array([1.0]), np.array([0.0]), np.array([1.0])
        g, _ = za.compute_g(v_mean, v_blk)
        out = za.gate_raw_operand_reconstruction(
            g_recorded={"mean": g, "cv": g}, diag_c_unified_mean=v_mean,
            diag_c_blocksum=v_blk, joint_mean_shift=ms)
        self.assertFalse(out["discriminating"])
        self.assertEqual(out["discrimination_blockers"]["n_pinned"], 1)

    def test_a_shift_UNDER_TOLERANCE_is_reported_as_non_discriminating(self):
        out = za.gate_raw_operand_reconstruction(
            g_recorded={"mean": za.compute_g(np.array([2.0]), np.array([1.0]))[0],
                        "cv": za.compute_g(np.array([2.0]), np.array([1.0]))[0]},
            diag_c_unified_mean=np.array([2.0]), diag_c_blocksum=np.array([1.0]),
            joint_mean_shift=np.array([1e-9]))
        self.assertFalse(out["discriminating"])
        self.assertEqual(out["discrimination_blockers"]["n_shift_below_tolerance"], 1)

    def test_a_SEPARABLE_operand_set_reports_discriminating_with_its_margin(self):
        v_mean, v_blk, ms = np.array([2.0]), np.array([1.0]), np.array([0.5])
        g_cv, _ = za.compute_g(v_mean + ms ** 2, v_blk)
        g_mean, _ = za.compute_g(v_mean, v_blk)
        out = za.gate_raw_operand_reconstruction(
            g_recorded={"mean": g_mean, "cv": g_cv}, diag_c_unified_mean=v_mean,
            diag_c_blocksum=v_blk, joint_mean_shift=ms)
        self.assertTrue(out["discriminating"])
        self.assertGreater(out["discrimination_blockers"]["max_separation"], out["rtol"])

    def test_the_blocker_buckets_PARTITION_every_bin(self):
        """Named mechanisms that do not add up would leave a fourth cause unaccounted for."""
        s = build_scenario()
        out = za.gate_raw_operand_reconstruction(**raw_operands(s))
        b = out["discrimination_blockers"]
        self.assertEqual(b["n_separated"] + b["n_pinned"]
                         + b["n_saturated_v_uni_below_v_blk"] + b["n_shift_below_tolerance"],
                         b["n_bins"])

    # ---- ⚠ ROUND-6 BLOCKER 3: §1.3a clips both raw diagonals -------------------------------
    def test_NEGATIVE_raw_entries_are_CLIPPED_per_the_contract_not_refused(self):
        """§1.3a: `v_uni^c = clip(diag(C_unified), 0, inf)`, `v_blk = clip(...)`.

        A low-rank throw estimator does produce negative variance entries. The first version
        passed them straight to `compute_g`, which refused them as "negative variance" -- the
        gate rejecting an operand set the contract defines a transformation for.
        """
        out = za.gate_raw_operand_reconstruction(
            g_recorded={"mean": np.array([1.0]), "cv": np.array([1.0])},
            diag_c_unified_mean=np.array([-1e-18]), diag_c_blocksum=np.array([1.0]),
            joint_mean_shift=np.array([0.0]))
        self.assertEqual(out["n_clipped_unified"], 1)

    def test_a_negative_BLOCKSUM_entry_is_clipped_and_counted_too(self):
        out = za.gate_raw_operand_reconstruction(
            g_recorded={"mean": np.array([1.0]), "cv": np.array([1.0])},
            diag_c_unified_mean=np.array([0.0]), diag_c_blocksum=np.array([-1e-20]),
            joint_mean_shift=np.array([0.0]))
        self.assertEqual(out["n_clipped_blocksum"], 1)

    def test_the_shift_is_added_AFTER_clipping_not_before(self):
        """The contract's ORDER. clip(-4)+9 == 9, whereas clip(-4+9) == 5 -- different g."""
        v_mean, v_blk, ms = np.array([-4.0]), np.array([1.0]), np.array([3.0])
        expected, _ = za.compute_g(np.array([0.0 + 9.0]), v_blk)      # clip first, then + ms**2
        wrong, _ = za.compute_g(np.array([5.0]), v_blk)               # add first, then clip
        self.assertNotAlmostEqual(float(expected[0]), float(wrong[0]))
        g_mean, _ = za.compute_g(np.array([0.0]), v_blk)
        out = za.gate_raw_operand_reconstruction(
            g_recorded={"mean": g_mean, "cv": expected}, diag_c_unified_mean=v_mean,
            diag_c_blocksum=v_blk, joint_mean_shift=ms)
        self.assertLessEqual(out["per_variant"]["cv"]["max_rel_diff"], out["rtol"])
        with self.assertRaises(zc.ZContractError):      # the add-then-clip ordering is refused
            za.gate_raw_operand_reconstruction(
                g_recorded={"mean": g_mean, "cv": wrong}, diag_c_unified_mean=v_mean,
                diag_c_blocksum=v_blk, joint_mean_shift=ms)

    # ---- ⚠ ROUND-6 BLOCKER 2: the optional operand was never validated ---------------------
    def test_a_NON_FINITE_stored_cv_diagonal_is_refused_before_any_tolerance(self):
        """Measured: `inf <= inf` is True, so it was reported CROSS-CHECKED."""
        s = build_scenario()
        for bad in (np.inf, -np.inf, np.nan):
            with self.subTest(value=bad):
                stored = s["v_uni_cv"].copy()
                stored[0] = bad
                with self.assertRaises(zc.ZContractError) as cm:
                    za.gate_raw_operand_reconstruction(
                        **raw_operands(s, diag_c_unified_cv=stored))
                self.assertIn("not finite", str(cm.exception))

    def test_the_stored_diagonal_check_reports_its_OWN_discrimination(self):
        """It is a different comparison from the g-level one and saturates differently.

        On the saturated input the g-level flag is False while the DIAGONAL comparison could
        still separate a dropped shift -- conflating the two was blocker 1.
        """
        v_mean, v_blk, ms = np.array([1.0]), np.array([100.0]), np.array([1.0])
        g, _ = za.compute_g(v_mean, v_blk)
        out = za.gate_raw_operand_reconstruction(
            g_recorded={"mean": g, "cv": g}, diag_c_unified_mean=v_mean,
            diag_c_blocksum=v_blk, joint_mean_shift=ms,
            diag_c_unified_cv=v_mean + ms ** 2)
        self.assertFalse(out["discriminating"])            # g cannot move
        self.assertTrue(out["stored_cv_discriminating"])   # the diagonal still can

    def test_stored_cv_discrimination_is_None_when_no_diagonal_was_supplied(self):
        s = build_scenario()
        self.assertIsNone(za.gate_raw_operand_reconstruction(
            **raw_operands(s))["stored_cv_discriminating"])

    # ---- ⚠ ROUND-7 ISSUE 1: one runner must not give two verdicts on one build ------------
    def test_the_CLIPPING_EXAMPLE_survives_the_PAIR_RUNNER_with_a_stored_cv_diagonal(self):
        """The reviewer's counterexample, through the runner, with the optional diagonal present.

        Measured before the fix: the raw gate ACCEPTED (clip(-4)=0, so v_uni^cv = 0+9 = 9) and
        `run_pair_gates` then handed the UNCLIPPED -4 to the coupling check, which predicted
        -4+9 = 5 and REFUSED the identical build. Two operand semantics inside one runner.
        """
        kw = dict(g_recorded={"mean": np.array([1.0]), "cv": np.array([3.0])},
                  diag_c_unified_mean=np.array([-4.0]), diag_c_blocksum=np.array([1.0]),
                  joint_mean_shift=np.array([3.0]), diag_c_unified_cv=np.array([9.0]))
        standalone = za.gate_raw_operand_reconstruction(**kw)
        res = za.run_pair_gates(**kw)                       # must NOT disagree with it
        self.assertEqual(res["G3R_raw_operand_reconstruction"]["n_clipped_unified"],
                         standalone["n_clipped_unified"])
        self.assertIn("G3b_variant_coupling", res)

    def test_the_two_checks_agree_on_every_clipped_operand_set(self):
        """Property form, so a future caller cannot reintroduce the divergence on other inputs."""
        rng = np.random.default_rng(11)
        for trial in range(8):
            raw_mean = rng.normal(0.0, 1.0, size=6)          # deliberately includes negatives
            v_blk = np.abs(rng.normal(1.0, 0.5, size=6)) + 0.1
            ms = rng.normal(0.0, 0.3, size=6)
            d = za.derive_variant_diagonals(raw_mean, v_blk, ms)
            g_mean, _ = za.compute_g(d["v_uni_mean"], d["v_blk"])
            g_cv, _ = za.compute_g(d["v_uni_cv"], d["v_blk"])
            with self.subTest(trial=trial):
                za.run_pair_gates(g_recorded={"mean": g_mean, "cv": g_cv},
                                  diag_c_unified_mean=raw_mean, diag_c_blocksum=v_blk,
                                  joint_mean_shift=ms, diag_c_unified_cv=d["v_uni_cv"])

    def test_the_coupling_check_REFUSES_raw_diagonals_rather_than_answering_differently(self):
        """The ambiguity is closed by refusing, not by documenting.

        A clipped v_uni is non-negative by construction, so a negative entry means the caller
        handed over a raw diagonal -- and silently answering a different question is what reached
        review.
        """
        with self.assertRaises(zc.ZContractError) as cm:
            za.check_variant_coupling(np.array([9.0]), np.array([-4.0]), np.array([3.0]))
        self.assertIn("CLIPPED v_uni values", str(cm.exception))
        self.assertIn("derive_variant_diagonals", str(cm.exception))

    def test_the_shared_derivation_is_the_only_place_the_clip_lives(self):
        d = za.derive_variant_diagonals(np.array([-4.0]), np.array([-1.0]), np.array([3.0]))
        self.assertEqual(list(d["v_uni_mean"]), [0.0])
        self.assertEqual(list(d["v_blk"]), [0.0])
        self.assertEqual(list(d["v_uni_cv"]), [9.0])         # clip FIRST, then + ms**2
        self.assertEqual(d["n_clipped_unified"], 1)
        self.assertEqual(d["n_clipped_blocksum"], 1)

    def test_the_pair_runner_still_catches_a_genuinely_inconsistent_stored_diagonal(self):
        """The fix must not have turned the coupling check into a rubber stamp."""
        s = build_scenario()
        bad = s["v_uni_cv"].copy()
        bad[0] *= 2.0
        with self.assertRaises(zc.ZContractError):
            za.run_pair_gates(**raw_operands(s, diag_c_unified_cv=bad))

    def test_the_pair_runner_carries_the_gate_under_its_section_name(self):
        s = build_scenario()
        res = za.run_pair_gates(**raw_operands(s, diag_c_unified_cv=s["v_uni_cv"]))
        self.assertIn("G3R_raw_operand_reconstruction", res)
        self.assertIn("G3b_variant_coupling", res)

    def test_malformed_operands_are_refused_rather_than_broadcast(self):
        s = build_scenario()
        g_mean, _ = za.compute_g(s["v_uni_mean"], s["v_blk"])
        with self.assertRaises(zc.ZContractError):
            za.gate_raw_operand_reconstruction(**raw_operands(s, diag_c_blocksum=s["v_blk"][:-1]))
        with self.assertRaises(zc.ZContractError):
            bad = s["ms"].copy(); bad[0] = np.nan
            za.gate_raw_operand_reconstruction(**raw_operands(s, joint_mean_shift=bad))
        with self.assertRaises(zc.ZContractError):
            za.gate_raw_operand_reconstruction(**raw_operands(s, g_recorded=["not", "a", "dict"]))

    def test_the_gate_consults_NO_acceptance_boundary(self):
        """Structural, not scientific. It must work with every boundary withheld, as they are."""
        s = build_scenario()
        self.assertTrue(all(not b.is_declared for b in zc.Z_BOUNDARIES.values()))
        za.gate_raw_operand_reconstruction(**raw_operands(s))     # would raise if it reached one


def gate_kwargs(s, **over):
    kw = dict(C_Z=s["C_Z"], g=s["g"], pinned_mask=s["pinned"], v_uni=s["v_uni_cv"],
              v_blk=s["v_blk"], cov_vert_sum=s["S_V"], cov_residual_sum=s["S_R"],
              cov_lateral_sum=s["S_A"], cov_stat=s["C_stat"], cov_ml=s["C_ML"],
              bands_vert=list(zc.VERT_BANDS),
              bands_residual=[f"r{i}" for i in range(zc.N_RESIDUAL)],
              bands_lateral=list(zc.LATERAL_BANDS),
              band_inventory=(list(zc.VERT_BANDS) + [f"r{i}" for i in range(zc.N_RESIDUAL)]
                              + list(zc.LATERAL_BANDS)))
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
        R = [f"r{i}" for i in range(zc.N_RESIDUAL)]
        zc.check_band_partition(list(zc.VERT_BANDS), R, list(zc.LATERAL_BANDS),
                                list(zc.VERT_BANDS) + R + list(zc.LATERAL_BANDS))

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
        self.assertLessEqual(out["max_deviation"], out["max_allowance"])
        self.assertGreater(out["ms_norm"], 0.0)
        self.assertTrue(out["discriminating"], "fixture cannot exercise the gate")

    def test_reusing_one_variants_operands_for_both_is_caught(self):
        s = build_scenario()
        with self.assertRaises(zc.ZContractError) as cm:
            za.check_variant_coupling(s["v_uni_mean"], s["v_uni_mean"], s["ms"])
        self.assertIn("dropped-shift", str(cm.exception))

    def test_a_zero_shift_is_ACCEPTED_and_reported_as_non_discriminating(self):
        """Review finding 4: a zero shift legitimately makes the variants equal.

        The old version raised here, rejecting a correct operand set from inside an algebraic
        identity. "Both variants must exist" is a real requirement, but it is §3.3 condition 14's,
        and it is not this function's to enforce.
        """
        s = build_scenario()
        z = np.zeros_like(s["ms"])
        out = za.check_variant_coupling(s["v_uni_mean"], s["v_uni_mean"], z)
        self.assertFalse(out["discriminating"])
        self.assertIn("WITHOUT DISCRIMINATING", out["note"])

    def test_a_correct_input_near_the_cancellation_regime_is_ACCEPTED(self):
        """Review finding 4's counterexample, verbatim: v_mean=1, ms=1e-5, v_cv=v_mean+ms**2.

        The subtraction-based residual reported 8.3e-8 against a 1e-9 tolerance and rejected this.
        """
        v_mean, ms = np.array([1.0]), np.array([1e-5])
        out = za.check_variant_coupling(v_mean + ms ** 2, v_mean, ms)
        self.assertLessEqual(out["max_deviation"], out["max_allowance"])

    def test_the_gate_still_catches_a_dropped_shift_where_it_CAN_discriminate(self):
        out_ok = za.check_variant_coupling(np.array([1.25]), np.array([1.0]), np.array([0.5]))
        self.assertTrue(out_ok["discriminating"])
        with self.assertRaises(zc.ZContractError):
            za.check_variant_coupling(np.array([1.0]), np.array([1.0]), np.array([0.5]))

    def test_it_reports_when_the_shift_is_too_small_to_discriminate(self):
        """A gate that cannot fail must say so rather than supply false assurance."""
        v_mean, ms = np.array([1.0]), np.array([1e-9])
        out = za.check_variant_coupling(v_mean + ms ** 2, v_mean, ms)
        self.assertFalse(out["discriminating"])

    def test_a_perturbed_shift_is_caught(self):
        s = build_scenario()
        bad = s["ms"].copy()
        bad[0] *= 4.0
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

    def test_a_materially_negative_eigenvalue_at_PHYSICAL_SCALE_is_caught(self):
        """Review finding 2, verbatim, and the sharpest defect in this module.

        `max(abs(lam_max), 1.0)` made the tolerance ABSOLUTE. Z's covariances live near 1e-38, so
        the 1.0 floor swallowed everything: 1e-76 * [[1,2],[2,1]] has eigenvalues -1e-76 and
        3e-76 -- a third of the spectrum negative -- and it passed. This is the same clamp §3.1a
        names as "the whole defect" in unified_throw_cov.py:517, rebuilt inside the gate meant to
        enforce that finding.
        """
        C = 1e-76 * np.array([[1.0, 2.0], [2.0, 1.0]])
        self.assertLess(float(np.linalg.eigvalsh(C)[0]), 0.0)     # the fixture really is bad
        with self.assertRaises(zc.ZContractError) as cm:
            za.gate_symmetry_psd(C)
        self.assertIn("psd", str(cm.exception))

    def test_the_psd_verdict_is_invariant_under_rescaling(self):
        """The property that makes the tolerance scale-free, tested rather than asserted."""
        good = build_scenario()["C_Z"]
        bad = 1e-76 * np.array([[1.0, 2.0], [2.0, 1.0]])
        for c in (1e-60, 1e-30, 1.0, 1e30):
            with self.subTest(scale=c):
                za.gate_symmetry_psd(good * c)                    # still passes
                with self.assertRaises(zc.ZContractError):
                    za.gate_symmetry_psd(bad * c)                 # still fails

    def test_a_SINGULAR_psd_matrix_is_accepted_though_cholesky_would_refuse_it(self):
        """Why Cholesky was removed: it tests positive DEFINITENESS, which is strictly stronger.

        A covariance with a null direction is PSD and perfectly valid, and nothing in §1.3a
        guarantees the assembled object has full rank. A Cholesky gate would refuse such a build --
        a guard that fires on a correct run. (This asserts the property of the two METHODS, not a
        claim about Z's rank, which this lane has not established.)
        """
        n = 6
        rng = np.random.default_rng(1)
        A = rng.standard_normal((n, n - 1))
        C = A @ A.T                                   # PSD, rank n-1: exactly one null direction
        w = np.linalg.eigvalsh(C)
        self.assertLess(abs(w[0]) / w[-1], 1e-12, "fixture is not actually singular")
        za.gate_symmetry_psd(C)                       # accepted, correctly
        with self.assertRaises(np.linalg.LinAlgError):
            np.linalg.cholesky(C)                     # would have refused it


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
