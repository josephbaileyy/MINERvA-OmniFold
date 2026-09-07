#!/usr/bin/env python3
"""Z's statistics, the outcome branches over a declared leg set, and the receipt.

THE CENTRAL TEST is `AWithheldBoundaryCanNeverProduceAPass`. Joseph, 2026-09-07: *"Missing or
unapproved acceptance boundaries must produce an explicit non-passing result. Do not choose
provisional numerical defaults that could grade a production artifact."* Everything else here is
support for being able to say that with evidence.

The grading path is exercised in BOTH directions. The accepting direction needs a DECLARED
boundary, which this baseline deliberately has none of -- so those tests inject one through
`patch.dict` rather than shipping one. If the accepting path were left untested, "we never return
MET" would be true for the wrong reason and nobody would know until a boundary was approved.
"""
import os
import sys
import tempfile
import unittest
from unittest import mock

import numpy as np

ND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ND not in sys.path:
    sys.path.insert(0, ND)

import z_contract as zc          # noqa: E402
import z_statistics as zs        # noqa: E402
import z_validator as zv         # noqa: E402
import z_receipt as zrec         # noqa: E402


def writable_tmpdir_or_skip(case):
    """Same reason as `tests/conftest.py`: an errored test looks like a defect."""
    try:
        d = tempfile.TemporaryDirectory()
    except Exception as exc:
        case.skipTest(f"no writable tmpdir: {exc}")
    case.addCleanup(d.cleanup)
    return d.name


def all_valid(**over):
    v = zv.Validity(footing_ok=True, digests_agree=True, partition_agrees=True,
                    identities_pass=True, cv_held_fixed=True, offsets_match_K=True,
                    offset_declared_nonzero=True, product_digests_distinct=True,
                    all_members_finite=True)
    for k, val in over.items():
        setattr(v, k, val)
    return v


def toy_covs(rng=None, n=12, offsets=(0, 1, 2)):
    rng = rng or np.random.default_rng(3)
    A = rng.standard_normal((n, n))
    base = (A @ A.T) / n + np.eye(n)
    out = {}
    for k in offsets:
        out[k] = base * (1.0 + 0.01 * k)     # a clean, monotone family
    return out


# --------------------------------------------------------------------------------- statistics --
class TheStatisticsMeasureWhatTheySay(unittest.TestCase):
    def test_s_agg_is_the_maximum_relative_change_over_the_declared_set(self):
        covs = toy_covs()
        out = zs.s_agg(covs, baseline_key=0)
        # sqrt(Tr(c*C)) = sqrt(c)*sqrt(Tr C), so the k=2 member sits at sqrt(1.02)-1.
        self.assertAlmostEqual(out["s_agg"], np.sqrt(1.02) - 1.0, places=12)
        self.assertEqual(out["argmax_offset"], 2)

    def test_s_agg_reports_the_sd_but_does_not_grade_on_it(self):
        out = zs.s_agg(toy_covs())
        self.assertIn("sd_of_members", out)
        self.assertGreater(out["sd_of_members"], 0.0)

    def test_the_baseline_member_must_be_present(self):
        with self.assertRaises(zc.ZContractError):
            zs.s_agg(toy_covs(offsets=(1, 2)), baseline_key=0)

    def test_s_med_uses_a_cv_held_fixed_at_the_baseline(self):
        covs = toy_covs()
        n = covs[0].shape[0]
        x = np.abs(np.random.default_rng(5).normal(10.0, 1.0, size=n))
        mask = np.ones(n, bool)
        out = zs.s_med(covs, x, mask, baseline_key=0)
        # sigma scales by sqrt(1.01k'), and x is fixed, so the median ratio scales the same way.
        self.assertAlmostEqual(out["s_med"], np.sqrt(1.02) - 1.0, places=12)

    def test_per_bin_movement_reports_a_distribution_and_an_argmax(self):
        covs = toy_covs()
        n = covs[0].shape[0]
        mask = np.ones(n, bool)
        out = zs.per_bin_movement(covs, mask)
        for key in ("median", "p90", "max", "argmax_support_index", "argmax_grid_index"):
            self.assertIn(key, out)
        self.assertGreaterEqual(out["max"], out["p90"])
        self.assertGreaterEqual(out["p90"], out["median"])

    def test_per_bin_movement_finds_a_concentrated_mover_the_median_would_hide(self):
        """The reason the argmax bin is reported at all."""
        n = 40
        C0 = np.eye(n)
        C1 = np.eye(n)
        C1[7, 7] = 4.0                       # one bin doubles in sigma; 39 do not move
        out = zs.per_bin_movement({0: C0, 1: C1}, np.ones(n, bool))
        self.assertAlmostEqual(out["median"], 0.0, places=12)
        self.assertAlmostEqual(out["max"], 1.0, places=12)
        self.assertEqual(out["argmax_grid_index"], 7)


class BothAdoptedStatisticsAreBlindToCorrelation(unittest.TestCase):
    """§3.7d, as an executable demonstration rather than an assertion in prose."""

    def setUp(self):
        self.I2 = np.eye(2)
        self.R9 = np.array([[1.0, 0.9], [0.9, 1.0]])
        self.covs = {0: self.I2, 1: self.R9}
        self.x = np.array([1.0, 1.0])
        self.mask = np.ones(2, bool)

    def test_s_agg_returns_exactly_zero(self):
        self.assertEqual(zs.s_agg(self.covs)["s_agg"], 0.0)

    def test_s_med_returns_exactly_zero(self):
        self.assertEqual(zs.s_med(self.covs, self.x, self.mask)["s_med"], 0.0)

    def test_per_bin_movement_returns_exactly_zero(self):
        self.assertEqual(zs.per_bin_movement(self.covs, self.mask)["max"], 0.0)

    def test_the_sum_and_difference_uncertainties_move_by_tens_of_percent(self):
        u, d = np.array([1.0, 1.0]), np.array([1.0, -1.0])
        self.assertAlmostEqual(np.sqrt(u @ self.R9 @ u) / np.sqrt(u @ self.I2 @ u) - 1,
                               0.378404875209022, places=12)
        self.assertAlmostEqual(np.sqrt(d @ self.R9 @ d) / np.sqrt(d @ self.I2 @ d) - 1,
                               -0.6837722339831621, places=12)

    def test_s_proj_over_those_functionals_does_see_it(self):
        U = np.array([[1.0, 1.0], [1.0, -1.0]])
        out = zs.s_proj(self.covs, U)
        self.assertGreater(out["s_proj"], 0.6)

    def test_s_corr_sees_it(self):
        self.assertGreater(zs.s_corr(self.covs)["s_corr"], 0.5)

    def test_s_eig_sees_it(self):
        self.assertGreater(zs.s_eig(self.covs)["s_eig"], 0.5)


class TheNullRatioAndItsReconstruction(unittest.TestCase):
    def test_the_ratio_is_the_scale_relative_one(self):
        x1 = np.array([0.0, 2.0, 4.0, 0.0, 4.0])
        x2 = x1 + np.array([0.0, 0.03, 0.04, 0.0, 0.0])
        out = zs.null_ratio(x1, x2)
        self.assertEqual(out["n_rep"], 3)
        self.assertAlmostEqual(out["cv_norm"], 6.0, places=12)
        self.assertAlmostEqual(out["num_norm"], 0.05, places=12)
        self.assertAlmostEqual(out["r_null"], 0.05 / 6.0, places=12)

    def test_bins_outside_the_reported_support_do_not_enter_either_norm(self):
        x1 = np.array([0.0, 3.0, 4.0])
        a = zs.null_ratio(x1, x1.copy())
        b = zs.null_ratio(x1, np.array([99.0, 3.0, 4.0]))   # differs only off-support
        self.assertEqual(a["r_null"], 0.0)
        self.assertEqual(b["r_null"], 0.0)

    def test_an_empty_support_aborts(self):
        with self.assertRaises(zc.ZContractError):
            zs.null_ratio(np.zeros(4), np.zeros(4))

    def test_reconstruction_from_persisted_operands_agrees_with_the_producer(self):
        rng = np.random.default_rng(11)
        x1 = np.abs(rng.normal(5.0, 1.0, size=50))
        x1[:5] = 0.0
        x2 = x1 + rng.normal(0.0, 1e-9, size=50)
        mask = zs.support_mask(x1)
        direct = zs.null_ratio(x1, x2, mask=mask)
        rebuilt = zs.reconstruct_null_ratio(x1, x2, mask)
        self.assertEqual(direct["r_null"], rebuilt["r_null"])

    def test_a_persisted_mask_selecting_nothing_is_refused(self):
        with self.assertRaises(zc.ZContractError):
            zs.reconstruct_null_ratio(np.ones(3), np.ones(3), np.zeros(3, bool))


# ---------------------------------------------------------------------------------- validator --
AGG = zv.Leg("agg", "aggregate", "cause3_agg", "s_agg")
MED = zv.Leg("med", "per-bin", "cause3_med", "s_med")


class AWithheldBoundaryCanNeverProduceAPass(unittest.TestCase):
    """The constraint the whole module exists for."""

    def setUp(self):
        self.L = zv.LegSet([AGG, MED], predeclared_at="TEST")

    def test_a_tiny_statistic_is_still_not_assessable(self):
        out = zv.assess(self.L, {"s_agg": 1e-30, "s_med": 1e-30}, all_valid())
        self.assertFalse(out.assessable)
        self.assertFalse(out.is_met)
        self.assertIsNone(out.branch)
        self.assertIn("4c", out.reject_conditions)

    def test_a_zero_statistic_is_still_not_assessable(self):
        out = zv.assess(self.L, {"s_agg": 0.0, "s_med": 0.0}, all_valid())
        self.assertFalse(out.is_met)

    def test_every_withheld_leg_is_named(self):
        out = zv.assess(self.L, {"s_agg": 0.0, "s_med": 0.0}, all_valid())
        self.assertEqual(set(out.failing_legs), {"agg", "med"})
        for name in ("agg", "med"):
            self.assertEqual(out.leg_results[name]["verdict"], "NOT ASSESSABLE")

    def test_the_reason_names_the_boundary_rather_than_being_generic(self):
        out = zv.assess(self.L, {"s_agg": 0.0, "s_med": 0.0}, all_valid())
        self.assertIn("cause3_agg", out.leg_results["agg"]["reason"])

    def test_a_missing_statistic_is_not_a_passing_leg(self):
        with self.assertRaises(zc.ZContractError):
            zv.assess(self.L, {"s_agg": 0.0}, all_valid())

    def test_the_null_is_refused_the_same_way(self):
        out = zv.assess_null(1e-30)
        self.assertFalse(out["assessable"])
        self.assertEqual(out["verdict"], "NOT ASSESSABLE")
        self.assertIn("4c", out["reject_conditions"])


class WithADeclaredBoundaryTheGradingPathWorksBothWays(unittest.TestCase):
    """Injected, never shipped. Without this the refusal above would be untested as a mechanism."""

    def setUp(self):
        self.declared = {
            "cause3_agg": zc.Boundary.declared("cause3_agg", 0.01, "TEST-RECORD §1"),
            "cause3_med": zc.Boundary.declared("cause3_med", 0.02, "TEST-RECORD §1"),
        }
        self.L = zv.LegSet([AGG, MED], predeclared_at="TEST")

    def test_within_both_limits_is_MET(self):
        with mock.patch.dict(zc.Z_BOUNDARIES, self.declared):
            out = zv.assess(self.L, {"s_agg": 0.005, "s_med": 0.005}, all_valid())
        self.assertTrue(out.assessable)
        self.assertTrue(out.is_met)
        self.assertEqual(out.branch, 3)

    def test_equality_is_favourable(self):
        with mock.patch.dict(zc.Z_BOUNDARIES, self.declared):
            out = zv.assess(self.L, {"s_agg": 0.01, "s_med": 0.02}, all_valid())
        self.assertTrue(out.is_met)

    def test_the_aggregate_leg_alone_gives_branch_4(self):
        with mock.patch.dict(zc.Z_BOUNDARIES, self.declared):
            out = zv.assess(self.L, {"s_agg": 0.5, "s_med": 0.001}, all_valid())
        self.assertEqual(out.branch, 4)
        self.assertEqual(out.failing_legs, ("agg",))
        self.assertFalse(out.is_met)

    def test_the_per_bin_leg_alone_gives_branch_5(self):
        with mock.patch.dict(zc.Z_BOUNDARIES, self.declared):
            out = zv.assess(self.L, {"s_agg": 0.001, "s_med": 0.5}, all_valid())
        self.assertEqual(out.branch, 5)

    def test_both_classes_give_branch_6(self):
        with mock.patch.dict(zc.Z_BOUNDARIES, self.declared):
            out = zv.assess(self.L, {"s_agg": 0.5, "s_med": 0.5}, all_valid())
        self.assertEqual(out.branch, 6)

    def test_one_withheld_leg_among_declared_ones_still_blocks_the_pass(self):
        """A partially declared set must not grade. This is the realistic near-miss."""
        partial = {"cause3_agg": self.declared["cause3_agg"]}    # med stays withheld
        with mock.patch.dict(zc.Z_BOUNDARIES, partial):
            out = zv.assess(self.L, {"s_agg": 0.001, "s_med": 0.001}, all_valid())
        self.assertFalse(out.is_met)
        self.assertEqual(out.failing_legs, ("med",))


class ADeclaredThirdLegBindsWithoutEditingTheBranches(unittest.TestCase):
    """The rev.-16 fix: rev. 7-15 hardcoded the pair, so a third leg would have been ignored."""

    def setUp(self):
        self.corr = zv.Leg("corr", "aggregate", "cause3_corr", "s_corr", sees_correlations=True)
        self.L3 = zv.LegSet([AGG, MED, self.corr], predeclared_at="TEST")
        self.declared = {
            "cause3_agg": zc.Boundary.declared("cause3_agg", 0.01, "T"),
            "cause3_med": zc.Boundary.declared("cause3_med", 0.02, "T"),
            "cause3_corr": zc.Boundary.declared("cause3_corr", 0.03, "T"),
        }

    def test_a_third_leg_failing_prevents_MET(self):
        with mock.patch.dict(zc.Z_BOUNDARIES, self.declared):
            out = zv.assess(self.L3, {"s_agg": 0.001, "s_med": 0.001, "s_corr": 0.9},
                            all_valid())
        self.assertFalse(out.is_met)
        self.assertEqual(out.failing_legs, ("corr",))

    def test_all_three_within_limits_is_MET(self):
        with mock.patch.dict(zc.Z_BOUNDARIES, self.declared):
            out = zv.assess(self.L3, {"s_agg": 0.001, "s_med": 0.001, "s_corr": 0.001},
                            all_valid())
        self.assertTrue(out.is_met)

    def test_a_leg_must_declare_one_of_the_two_R4_classes(self):
        with self.assertRaises(zc.ZContractError) as cm:
            zv.Leg("c", "correlation", "cause3_corr", "s_corr")
        self.assertIn("class", str(cm.exception))

    def test_a_leg_naming_an_unknown_boundary_is_refused_at_declaration(self):
        with self.assertRaises(zc.ZContractError):
            zv.Leg("x", "aggregate", "not_a_boundary", "s_x")

    def test_an_empty_leg_set_is_refused(self):
        with self.assertRaises(zc.ZContractError):
            zv.LegSet([])

    def test_duplicate_leg_names_are_refused(self):
        with self.assertRaises(zc.ZContractError):
            zv.LegSet([AGG, AGG])


class ValidityDominatesEveryNumericalBranch(unittest.TestCase):
    def setUp(self):
        self.L = zv.LegSet([AGG, MED], predeclared_at="TEST")
        self.declared = {"cause3_agg": zc.Boundary.declared("cause3_agg", 0.01, "T"),
                         "cause3_med": zc.Boundary.declared("cause3_med", 0.02, "T")}

    def test_a_footing_failure_gives_branch_1_even_with_perfect_statistics(self):
        with mock.patch.dict(zc.Z_BOUNDARIES, self.declared):
            out = zv.assess(self.L, {"s_agg": 0.0, "s_med": 0.0}, all_valid(footing_ok=False))
        self.assertEqual(out.branch, 1)
        self.assertFalse(out.is_met)

    def test_a_vacuous_baseline_gives_branch_2_and_zero_spread_is_not_favourable(self):
        with mock.patch.dict(zc.Z_BOUNDARIES, self.declared):
            out = zv.assess(self.L, {"s_agg": 0.0, "s_med": 0.0},
                            all_valid(offset_declared_nonzero=False))
        self.assertEqual(out.branch, 2)
        self.assertFalse(out.is_met)

    def test_the_defaults_are_the_safe_direction(self):
        """A caller who forgets to populate Validity gets branch 1, never MET."""
        with mock.patch.dict(zc.Z_BOUNDARIES, self.declared):
            out = zv.assess(self.L, {"s_agg": 0.0, "s_med": 0.0}, zv.Validity())
        self.assertEqual(out.branch, 1)

    def test_the_diagonal_only_scope_statement_travels_with_the_result(self):
        with mock.patch.dict(zc.Z_BOUNDARIES, self.declared):
            out = zv.assess(self.L, {"s_agg": 0.0, "s_med": 0.0}, all_valid())
        self.assertIn("does NOT license", out.scope_statement)
        self.assertIn("marginalization", out.scope_statement)

    def test_a_caller_can_no_longer_suppress_the_scope_statement(self):
        """Review finding 8: it used to be a keyword argument, so a caller could simply assert it.

        The declared leg set is the only thing that decides it now, and `assess` takes no such
        argument at all -- a signature that cannot be lied to beats one that is merely documented.
        """
        with self.assertRaises(TypeError):
            zv.assess(self.L, {"s_agg": 0.0, "s_med": 0.0}, all_valid(),
                      correlation_leg_present=True)

    def test_the_scope_statement_is_dropped_only_when_a_leg_actually_sees_correlations(self):
        corr = zv.Leg("corr", "aggregate", "cause3_corr", "s_corr", sees_correlations=True)
        L3 = zv.LegSet([AGG, MED, corr], predeclared_at="TEST")
        declared = dict(self.declared)
        declared["cause3_corr"] = zc.Boundary.declared("cause3_corr", 0.03, "T")
        with mock.patch.dict(zc.Z_BOUNDARIES, declared):
            out = zv.assess(L3, {"s_agg": 0.0, "s_med": 0.0, "s_corr": 0.0}, all_valid())
        self.assertIsNone(out.scope_statement)
        self.assertTrue(L3.sees_correlations)

    def test_a_leg_set_of_diagonal_only_legs_reports_that_it_sees_no_correlations(self):
        self.assertFalse(self.L.sees_correlations)


class TheStatisticDomainIsValidatedBeforeAnyComparison(unittest.TestCase):
    """Review finding 7. Every statistic here is |a-b|/b with b>0: finite and non-negative."""

    def setUp(self):
        self.L = zv.LegSet([AGG, MED], predeclared_at="TEST")
        self.declared = {"cause3_agg": zc.Boundary.declared("cause3_agg", 0.01, "T"),
                         "cause3_med": zc.Boundary.declared("cause3_med", 0.02, "T")}

    def test_negative_infinity_no_longer_returns_MET(self):
        """Measured before the fix: -inf <= delta is True, so this graded as a PASS."""
        with mock.patch.dict(zc.Z_BOUNDARIES, self.declared):
            out = zv.assess(self.L, {"s_agg": float("-inf"), "s_med": 0.0}, all_valid())
        self.assertFalse(out.is_met)
        self.assertEqual(out.branch, 1)
        self.assertIn("agg", out.validity["invalid_statistics"])

    def test_NaN_is_inconclusive_rather_than_an_unfavourable_measurement(self):
        """NaN <= delta is False, which used to read as a measured excess. It is not one."""
        with mock.patch.dict(zc.Z_BOUNDARIES, self.declared):
            out = zv.assess(self.L, {"s_agg": float("nan"), "s_med": 0.0}, all_valid())
        self.assertEqual(out.branch, 1)
        self.assertNotEqual(out.branch, 4)

    def test_positive_infinity_is_inconclusive(self):
        with mock.patch.dict(zc.Z_BOUNDARIES, self.declared):
            out = zv.assess(self.L, {"s_agg": float("inf"), "s_med": 0.0}, all_valid())
        self.assertEqual(out.branch, 1)

    def test_a_negative_relative_change_is_out_of_domain(self):
        with mock.patch.dict(zc.Z_BOUNDARIES, self.declared):
            out = zv.assess(self.L, {"s_agg": -0.001, "s_med": 0.0}, all_valid())
        self.assertEqual(out.branch, 1)
        self.assertIn("negative", out.validity["invalid_statistics"]["agg"])

    def test_a_non_numeric_statistic_is_out_of_domain(self):
        with mock.patch.dict(zc.Z_BOUNDARIES, self.declared):
            out = zv.assess(self.L, {"s_agg": "small", "s_med": 0.0}, all_valid())
        self.assertEqual(out.branch, 1)

    def test_valid_statistics_still_grade_normally(self):
        with mock.patch.dict(zc.Z_BOUNDARIES, self.declared):
            out = zv.assess(self.L, {"s_agg": 0.0, "s_med": 0.0}, all_valid())
        self.assertTrue(out.is_met)
        self.assertEqual(out.validity["invalid_statistics"], {})


class TheNullAbortsRatherThanScoringBadly(unittest.TestCase):
    def test_an_exceeded_bound_carries_its_reject_condition(self):
        """Review finding 7: it used to return an EMPTY reject list, reading as a clean run."""
        with mock.patch.dict(zc.Z_BOUNDARIES,
                             {"null_epsilon": zc.Boundary.declared("null_epsilon", 1e-11, "T")}):
            out = zv.assess_null(1.0)
        self.assertEqual(out["verdict"], "exceeds bound")
        self.assertIn("11", out["reject_conditions"])
        self.assertTrue(out["aborts"])

    def test_a_satisfied_bound_does_not_abort(self):
        with mock.patch.dict(zc.Z_BOUNDARIES,
                             {"null_epsilon": zc.Boundary.declared("null_epsilon", 1e-11, "T")}):
            out = zv.assess_null(1e-13)
        self.assertEqual(out["verdict"], "within bound")
        self.assertEqual(out["reject_conditions"], [])
        self.assertFalse(out["aborts"])

    def test_a_non_finite_ratio_is_refused_before_the_bound_is_consulted(self):
        with mock.patch.dict(zc.Z_BOUNDARIES,
                             {"null_epsilon": zc.Boundary.declared("null_epsilon", 1e-11, "T")}):
            for bad in (float("nan"), float("inf"), -1.0):
                with self.subTest(r_null=bad):
                    out = zv.assess_null(bad)
                    self.assertFalse(out["assessable"])
                    self.assertTrue(out["aborts"])


# ------------------------------------------------------------------------------------ receipt --
class TheReceiptPersistsTheNullOperands(unittest.TestCase):
    def test_round_trip_reproduces_the_ratio_without_the_producers_scalar(self):
        d = writable_tmpdir_or_skip(self)
        rng = np.random.default_rng(2)
        x1 = np.abs(rng.normal(5.0, 1.0, size=200))
        x1[:20] = 0.0
        x2 = x1 + rng.normal(0.0, 1e-10, size=200)
        mask = zs.support_mask(x1)
        path = os.path.join(d, "z_null_operands.npz")
        meta = zrec.persist_null_operands(path, x1, x2, mask)
        self.assertEqual(meta["n_rep"], int(mask.sum()))
        self.assertEqual(meta["n_grid"], 200)

        a, b, m = zrec.load_null_operands(path)
        rebuilt = zs.reconstruct_null_ratio(a, b, m)
        direct = zs.null_ratio(x1, x2, mask=mask)
        self.assertEqual(rebuilt["r_null"], direct["r_null"])

    def test_a_missing_operand_is_a_reject_not_a_fallback(self):
        d = writable_tmpdir_or_skip(self)
        path = os.path.join(d, "partial.npz")
        np.savez_compressed(path, x_cv=np.ones(4))       # no x_cv2, no mask
        with self.assertRaises(zc.ZContractError) as cm:
            zrec.load_null_operands(path)
        self.assertIn("11b", str(cm.exception))

    def test_persistence_refuses_mismatched_shapes(self):
        d = writable_tmpdir_or_skip(self)
        with self.assertRaises(zc.ZContractError):
            zrec.persist_null_operands(os.path.join(d, "x.npz"),
                                       np.ones(4), np.ones(5), np.ones(4, bool))

    def test_the_array_digest_separates_shape_from_bytes(self):
        a = np.arange(6, dtype=float)
        self.assertNotEqual(zrec.sha256_array(a), zrec.sha256_array(a.reshape(2, 3)))


# What `za.run_pair_gates` actually returns on a correct build, trimmed to the fields the receipt
# reads. Shaped from the GATE's output, not invented here -- a fixture built from the rule it
# feeds cannot disagree with it.
PASSING_RECONSTRUCTION = {
    "G3R_raw_operand_reconstruction": {
        "per_variant": {"mean": {"max_rel_diff": 0.0, "worst_bin": 0, "n_pinned": 3,
                                 "n_inflated": 21},
                        "cv": {"max_rel_diff": 1.1e-16, "worst_bin": 4, "n_pinned": 3,
                               "n_inflated": 21}},
        "rtol": 1e-9,
        "discriminating": True,
    },
}


class TheReceiptRefusesToRecordAPassItCannotJustify(unittest.TestCase):
    def _blocks(self):
        return dict(
            z_stamp={"path": "/tmp/z.root", "sha256": "0" * 64},
            variant="cv",
            parent={"candidate": "G", "sha256": "1" * 64},
            code_identity={"revision": "10c24678", "import_closure_digests": {"z_contract": "a"}},
            inflation={"n_pinned": 3, **PASSING_RECONSTRUCTION},
            null_block={"r_null": 1e-13},
            cause_blocks={"cause3": {}},
            closure={"max_rel_residual": 1e-15},
        )

    def test_a_well_formed_receipt_carries_the_withheld_boundaries_and_the_negative_statement(self):
        r = zrec.build_receipt(**self._blocks())
        self.assertEqual(r["schema_version"], zrec.Z_RECEIPT_SCHEMA_VERSION)
        self.assertEqual(set(r["withheld_boundaries"]), set(zc.Z_BOUNDARIES))
        self.assertIn("are not evidence that Z was produced", r["negative_statement"])

    def test_an_unnamed_centering_variant_is_refused(self):
        blocks = self._blocks()
        blocks["variant"] = "both"
        with self.assertRaises(zc.ZContractError):
            zrec.build_receipt(**blocks)

    def test_code_identity_without_import_closure_digests_is_refused(self):
        blocks = self._blocks()
        blocks["code_identity"] = {"revision": "10c24678"}
        with self.assertRaises(zc.ZContractError) as cm:
            zrec.build_receipt(**blocks)
        self.assertIn("import-closure", str(cm.exception))

    def test_a_met_verdict_on_an_unassessable_outcome_is_refused(self):
        blocks = self._blocks()
        blocks["outcome"] = {"assessable": False, "branch": 3}
        with self.assertRaises(zc.ZContractError) as cm:
            zrec.build_receipt(**blocks)
        self.assertIn("withheld boundary cannot produce a passing grade", str(cm.exception))

    def test_a_MET_outcome_whose_legs_rest_on_WITHHELD_boundaries_is_refused(self):
        """Review finding 1, second half.

        assessable=True with branch=3 used to be written happily while the receipt's own
        withheld_boundaries block recorded all four as withheld. The receipt carried its own
        refutation and never looked at it.
        """
        blocks = self._blocks()
        blocks["outcome"] = {
            "assessable": True, "branch": 3, "branch_label": "MET",
            "leg_results": {"agg": {"class": "aggregate", "statistic": 0.0,
                                    "boundary": {"name": "cause3_agg", "status": "WITHHELD",
                                                 "value": None}}}}
        with self.assertRaises(zc.ZContractError) as cm:
            zrec.build_receipt(**blocks)
        self.assertIn("not backed by a declared boundary", str(cm.exception))

    def test_a_MET_outcome_with_no_legs_at_all_is_refused(self):
        blocks = self._blocks()
        blocks["outcome"] = {"assessable": True, "branch": 3, "leg_results": {}}
        with self.assertRaises(zc.ZContractError) as cm:
            zrec.build_receipt(**blocks)
        self.assertIn("records no leg results", str(cm.exception))

    def test_a_MET_outcome_whose_boundary_was_withdrawn_since_is_refused(self):
        """The stale-outcome case: the dict says DECLARED, the live registry disagrees."""
        blocks = self._blocks()
        blocks["outcome"] = self._met(name="cause3_agg", value=0.01, prov="stale", limit=0.01)
        with self.assertRaises(zc.ZContractError) as cm:
            zrec.build_receipt(**blocks)
        self.assertIn("withheld in the registry now", str(cm.exception))

    # ---- ⚠ ROUND-3 FINDING 1: the chain from the cited name to the applied limit --------------
    def test_an_UNKNOWN_boundary_name_is_refused(self):
        """Measured before this fix: `cause3_aggg` -- one keystroke off -- graded MET.

        `Z_BOUNDARIES.get(name)` returns None for an unknown name, and `live is not None` guarded
        the only check that consulted it, so a name Z has never heard of skipped every test. The
        receipt listed all four real boundaries as withheld in the same document.
        """
        blocks = self._blocks()
        blocks["outcome"] = self._met(name="cause3_aggg", value=1.0, prov=None, limit=1.0)
        with self.assertRaises(zc.ZContractError) as cm:
            zrec.build_receipt(**blocks)
        self.assertIn("not in Z's registry", str(cm.exception))

    def test_a_CHANGED_declaration_is_refused(self):
        """Measured: limit 1.0 under APPROVAL-OLD passed while the live boundary was 0.1."""
        blocks = self._blocks()
        blocks["outcome"] = self._met(name="cause3_agg", value=1.0, prov="APPROVAL-OLD", limit=1.0)
        with self._live(0.1, "APPROVAL-NEW"), self.assertRaises(zc.ZContractError) as cm:
            zrec.build_receipt(**blocks)
        self.assertIn("the outcome is stale", str(cm.exception))

    def test_the_right_VALUE_under_a_SUPERSEDED_approval_record_is_refused(self):
        """Two records can name the same number for different reasons; the record is the citation.

        This is the half a value comparison alone would wave through -- and the half that matters
        under BEN-381, where which record approved a limit is the whole question.
        """
        blocks = self._blocks()
        blocks["outcome"] = self._met(name="cause3_agg", value=0.1, prov="APPROVAL-OLD", limit=0.1)
        with self._live(0.1, "APPROVAL-NEW"), self.assertRaises(zc.ZContractError) as cm:
            zrec.build_receipt(**blocks)
        self.assertIn("superseded criterion", str(cm.exception))

    def test_a_limit_that_does_not_match_the_boundary_it_cites_is_refused(self):
        """The declaration can be perfect and the number actually APPLIED still be another one."""
        blocks = self._blocks()
        blocks["outcome"] = self._met(name="cause3_agg", value=0.1, prov="APPROVAL-NEW", limit=1.0)
        with self._live(0.1, "APPROVAL-NEW"), self.assertRaises(zc.ZContractError) as cm:
            zrec.build_receipt(**blocks)
        self.assertIn("applied limit", str(cm.exception))

    def test_a_leg_citing_no_boundary_name_at_all_is_refused(self):
        blocks = self._blocks()
        blocks["outcome"] = {"assessable": True, "branch": 3,
                             "leg_results": {"agg": {"limit": 0.1, "boundary": {}}}}
        with self.assertRaises(zc.ZContractError) as cm:
            zrec.build_receipt(**blocks)
        self.assertIn("cites no boundary name", str(cm.exception))

    # ---- §1.3b integration, 2026-09-07: a MET receipt must PROVE the reconstruction ran ------
    def test_a_MET_receipt_without_the_reconstruction_block_is_refused(self):
        """The gate that makes the other four capable of failing must be shown, not asserted."""
        blocks = self._blocks()
        blocks["inflation"] = {"n_pinned": 3}          # the other gates only
        blocks["outcome"] = self._met(name="cause3_agg", value=0.01, prov="TEST", limit=0.01)
        with self._live(0.01, "TEST"), self.assertRaises(zc.ZContractError) as cm:
            zrec.build_receipt(**blocks)
        self.assertIn("G3R_raw_operand_reconstruction", str(cm.exception))

    def test_a_MET_receipt_recording_only_ONE_variant_is_refused(self):
        blocks = self._blocks()
        one = {"per_variant": {"cv": {"max_rel_diff": 0.0}}, "rtol": 1e-9}
        blocks["inflation"] = {"G3R_raw_operand_reconstruction": one}
        blocks["outcome"] = self._met(name="cause3_agg", value=0.01, prov="TEST", limit=0.01)
        with self._live(0.01, "TEST"), self.assertRaises(zc.ZContractError) as cm:
            zrec.build_receipt(**blocks)
        self.assertIn("BOTH", str(cm.exception))

    def test_a_MET_receipt_whose_reconstruction_EXCEEDED_its_tolerance_is_refused(self):
        blocks = self._blocks()
        bad = {"per_variant": {"mean": {"max_rel_diff": 0.0},
                               "cv": {"max_rel_diff": 1e-3}},         # the dropped-shift signature
               "rtol": 1e-9}
        blocks["inflation"] = {"G3R_raw_operand_reconstruction": bad}
        blocks["outcome"] = self._met(name="cause3_agg", value=0.01, prov="TEST", limit=0.01)
        with self._live(0.01, "TEST"), self.assertRaises(zc.ZContractError) as cm:
            zrec.build_receipt(**blocks)
        self.assertIn("did NOT pass", str(cm.exception))

    def test_a_recorded_VERDICT_is_not_a_recorded_MEASUREMENT(self):
        """`{"passed": true}` is exactly the shape §1.3b rejects."""
        blocks = self._blocks()
        blocks["inflation"] = {"G3R_raw_operand_reconstruction": {"passed": True}}
        blocks["outcome"] = self._met(name="cause3_agg", value=0.01, prov="TEST", limit=0.01)
        with self._live(0.01, "TEST"), self.assertRaises(zc.ZContractError) as cm:
            zrec.build_receipt(**blocks)
        self.assertIn("not a recorded measurement", str(cm.exception))

    def test_a_reconstruction_with_no_stated_TOLERANCE_is_refused(self):
        blocks = self._blocks()
        blocks["inflation"] = {"G3R_raw_operand_reconstruction": {
            "per_variant": {"mean": {"max_rel_diff": 0.0}, "cv": {"max_rel_diff": 0.0}}}}
        blocks["outcome"] = self._met(name="cause3_agg", value=0.01, prov="TEST", limit=0.01)
        with self._live(0.01, "TEST"), self.assertRaises(zc.ZContractError) as cm:
            zrec.build_receipt(**blocks)
        self.assertIn("cannot be re-checked", str(cm.exception))

    def test_a_NON_DISCRIMINATING_pass_is_carried_through_rather_than_refused(self):
        """A tiny genuine mean shift must not make the receipt refuse a correct build.

        It must arrive WITH its disclosure, though -- see the two tests below.
        """
        blocks = self._blocks()
        blk = {k: dict(v) for k, v in PASSING_RECONSTRUCTION.items()}
        blk["G3R_raw_operand_reconstruction"].update(
            discriminating=False,
            note="PASSED WITHOUT DISCRIMINATING: 3 bin(s) saturated with v_uni <= v_blk.",
            discrimination_blockers={"n_bins": 3, "n_separated": 0, "n_pinned": 0,
                                     "n_saturated_v_uni_below_v_blk": 3,
                                     "n_shift_below_tolerance": 0, "max_separation": 0.0})
        blocks["inflation"] = blk
        blocks["outcome"] = self._met(name="cause3_agg", value=0.01, prov="TEST", limit=0.01)
        with self._live(0.01, "TEST"):
            r = zrec.build_receipt(**blocks)
        self.assertEqual(r["outcome"]["branch"], 3)
        self.assertFalse(r["inflation"]["G3R_raw_operand_reconstruction"]["discriminating"])

    def test_a_NON_passing_outcome_is_not_required_to_carry_the_reconstruction(self):
        """The requirement is on a PASS. A refusal must not itself need the gate to have run."""
        blocks = self._blocks()
        blocks["inflation"] = {"n_pinned": 3}
        blocks["outcome"] = {"assessable": False, "branch": None, "reject_conditions": ["4c"]}
        r = zrec.build_receipt(**blocks)
        self.assertIsNone(r["outcome"]["branch"])

    def test_what_the_REAL_gate_emits_satisfies_the_receipt(self):
        """End to end: `run_pair_gates`'s own output, unedited, must be acceptable.

        A receipt rule the real producer does not satisfy would be a rule that only fires on
        hand-written fixtures -- the defect this suite has already found twice.
        """
        import z_assembly as za
        n = 12
        v_blk = np.full(n, 2.0)
        v_uni_mean = v_blk * 1.3
        ms = np.full(n, 0.05)
        g_mean, _ = za.compute_g(v_uni_mean, v_blk)
        g_cv, _ = za.compute_g(v_uni_mean + ms ** 2, v_blk)
        res = za.run_pair_gates(g_recorded={"mean": g_mean, "cv": g_cv},
                                diag_c_unified_mean=v_uni_mean, diag_c_blocksum=v_blk,
                                joint_mean_shift=ms)
        blocks = self._blocks()
        blocks["inflation"] = res
        blocks["outcome"] = self._met(name="cause3_agg", value=0.01, prov="TEST", limit=0.01)
        with self._live(0.01, "TEST"):
            r = zrec.build_receipt(**blocks)
        self.assertEqual(r["outcome"]["branch"], 3)
        self.assertTrue(r["inflation"]["G3R_raw_operand_reconstruction"]["discriminating"])

    # ---- ⚠ ROUND-6 BLOCKER 2: the receipt compared against unvalidated values -------------
    def _recon(self, **over):
        blk = {"per_variant": {"mean": {"max_rel_diff": 0.0}, "cv": {"max_rel_diff": 0.0}},
               "rtol": 1e-9, "discriminating": True}
        blk.update(over)
        blocks = self._blocks()
        blocks["inflation"] = {"G3R_raw_operand_reconstruction": blk}
        blocks["outcome"] = self._met(name="cause3_agg", value=0.01, prov="TEST", limit=0.01)
        return blocks

    def test_an_INFINITE_tolerance_is_refused(self):
        """Measured: rtol=inf with max_rel_diff=100 wrote a MET receipt. 100 <= inf is True.

        An infinite tolerance is not a loose one -- it is the absence of one, and every residual
        satisfies it. Same shape as the PSD gate's absolute floor.
        """
        blocks = self._recon(
            rtol=float("inf"),
            per_variant={"mean": {"max_rel_diff": 100.0}, "cv": {"max_rel_diff": 100.0}})
        with self._live(0.01, "TEST"), self.assertRaises(zc.ZContractError) as cm:
            zrec.build_receipt(**blocks)
        self.assertIn("not a finite positive tolerance", str(cm.exception))

    def test_a_ZERO_or_negative_tolerance_is_refused(self):
        for bad in (0.0, -1e-9):
            with self.subTest(rtol=bad):
                with self._live(0.01, "TEST"), self.assertRaises(zc.ZContractError):
                    zrec.build_receipt(**self._recon(rtol=bad))

    def test_a_NEGATIVE_INFINITE_residual_is_refused(self):
        """Measured: max_rel_diff=-inf wrote a MET receipt, because -inf <= rtol is True."""
        blocks = self._recon(per_variant={"mean": {"max_rel_diff": float("-inf")},
                                          "cv": {"max_rel_diff": 0.0}})
        with self._live(0.01, "TEST"), self.assertRaises(zc.ZContractError) as cm:
            zrec.build_receipt(**blocks)
        self.assertIn("finite and non-negative", str(cm.exception))

    def test_a_NaN_residual_is_refused(self):
        blocks = self._recon(per_variant={"mean": {"max_rel_diff": float("nan")},
                                          "cv": {"max_rel_diff": 0.0}})
        with self._live(0.01, "TEST"), self.assertRaises(zc.ZContractError):
            zrec.build_receipt(**blocks)

    def test_a_BOOLEAN_masquerading_as_a_measurement_is_refused(self):
        """`isinstance(True, int)` is True in Python, so a bare bool would have slipped through."""
        with self._live(0.01, "TEST"), self.assertRaises(zc.ZContractError):
            zrec.build_receipt(**self._recon(rtol=True))
        with self._live(0.01, "TEST"), self.assertRaises(zc.ZContractError):
            zrec.build_receipt(**self._recon(
                per_variant={"mean": {"max_rel_diff": True}, "cv": {"max_rel_diff": 0.0}}))

    def test_an_OMITTED_discriminating_field_is_refused(self):
        """Measured: the disclosure could simply be left out and the receipt still said MET."""
        blk = {"per_variant": {"mean": {"max_rel_diff": 0.0}, "cv": {"max_rel_diff": 0.0}},
               "rtol": 1e-9}
        blocks = self._blocks()
        blocks["inflation"] = {"G3R_raw_operand_reconstruction": blk}
        blocks["outcome"] = self._met(name="cause3_agg", value=0.01, prov="TEST", limit=0.01)
        with self._live(0.01, "TEST"), self.assertRaises(zc.ZContractError) as cm:
            zrec.build_receipt(**blocks)
        self.assertIn("omits `discriminating`", str(cm.exception))

    def test_a_non_boolean_discriminating_verdict_is_refused(self):
        with self._live(0.01, "TEST"), self.assertRaises(zc.ZContractError):
            zrec.build_receipt(**self._recon(discriminating="probably"))

    def test_a_non_discriminating_pass_WITHOUT_its_note_is_refused(self):
        blocks = self._recon(discriminating=False,
                             discrimination_blockers={"n_bins": 1})
        with self._live(0.01, "TEST"), self.assertRaises(zc.ZContractError) as cm:
            zrec.build_receipt(**blocks)
        self.assertIn("carries no limitation note", str(cm.exception))

    def test_a_non_discriminating_pass_WITHOUT_its_blockers_is_refused(self):
        """WHY it was blind is the actionable part, and saturation is invisible to a tolerance."""
        blocks = self._recon(discriminating=False, note="blind here")
        with self._live(0.01, "TEST"), self.assertRaises(zc.ZContractError) as cm:
            zrec.build_receipt(**blocks)
        self.assertIn("discrimination_blockers", str(cm.exception))

    # ---- ⚠ ROUND-7 ISSUE 2: requiring the key was not requiring the content ---------------
    def _blockers(self, **over):
        b = {"n_bins": 3, "n_separated": 0, "n_pinned": 0,
             "n_saturated_v_uni_below_v_blk": 3, "n_shift_below_tolerance": 0,
             "max_separation": 0.0}
        b.update(over)
        return self._recon(discriminating=False, note="blind here",
                           discrimination_blockers=b)

    def test_an_EMPTY_blockers_dict_is_refused(self):
        """Measured: `{}` satisfied "is a dict" and a MET receipt was written."""
        blocks = self._recon(discriminating=False, note="blind here",
                             discrimination_blockers={})
        with self._live(0.01, "TEST"), self.assertRaises(zc.ZContractError) as cm:
            zrec.build_receipt(**blocks)
        self.assertIn("omits", str(cm.exception))

    def test_a_PARTIAL_blockers_dict_names_what_is_missing(self):
        blocks = self._recon(discriminating=False, note="blind here",
                             discrimination_blockers={"n_bins": 3})
        with self._live(0.01, "TEST"), self.assertRaises(zc.ZContractError) as cm:
            zrec.build_receipt(**blocks)
        self.assertIn("n_separated", str(cm.exception))

    def test_counts_that_DO_NOT_PARTITION_the_bins_are_refused(self):
        """A breakdown that does not add up leaves a fifth cause unnamed -- which is how
        saturation went unnoticed for a whole round."""
        with self._live(0.01, "TEST"), self.assertRaises(zc.ZContractError) as cm:
            zrec.build_receipt(**self._blockers(n_bins=10))
        self.assertIn("do not partition", str(cm.exception))

    def test_a_record_CONTRADICTING_its_own_verdict_is_refused(self):
        """discriminating=False beside n_separated=5: two halves from different runs."""
        with self._live(0.01, "TEST"), self.assertRaises(zc.ZContractError) as cm:
            zrec.build_receipt(**self._blockers(
                n_bins=5, n_separated=5, n_saturated_v_uni_below_v_blk=0, max_separation=0.5))
        self.assertIn("did not come from the same run", str(cm.exception))

    def test_the_same_contradiction_in_the_OTHER_direction_is_refused(self):
        """discriminating=True with n_separated=0. The consistency check must be two-sided."""
        blocks = self._recon(
            discriminating=True,
            discrimination_blockers={"n_bins": 3, "n_separated": 0, "n_pinned": 3,
                                     "n_saturated_v_uni_below_v_blk": 0,
                                     "n_shift_below_tolerance": 0, "max_separation": 0.0})
        with self._live(0.01, "TEST"), self.assertRaises(zc.ZContractError) as cm:
            zrec.build_receipt(**blocks)
        self.assertIn("did not come from the same run", str(cm.exception))

    def test_NEGATIVE_or_non_integer_counts_are_refused(self):
        for bad in ({"n_pinned": -1}, {"n_pinned": 1.5}, {"n_pinned": True}, {"n_bins": 0}):
            with self.subTest(**bad):
                with self._live(0.01, "TEST"), self.assertRaises(zc.ZContractError):
                    zrec.build_receipt(**self._blockers(**bad))

    def test_a_non_finite_max_separation_is_refused(self):
        for bad in (float("inf"), float("nan"), -1.0):
            with self.subTest(max_separation=bad):
                with self._live(0.01, "TEST"), self.assertRaises(zc.ZContractError):
                    zrec.build_receipt(**self._blockers(max_separation=bad))

    def test_a_COMPLETE_and_CONSISTENT_disclosure_is_accepted(self):
        """The positive direction, so the refusals above are not passing for the wrong reason."""
        with self._live(0.01, "TEST"):
            r = zrec.build_receipt(**self._blockers())
        blk = r["inflation"]["G3R_raw_operand_reconstruction"]
        self.assertFalse(blk["discriminating"])
        self.assertEqual(blk["discrimination_blockers"]["n_saturated_v_uni_below_v_blk"], 3)

    def test_the_REAL_gates_blockers_satisfy_the_receipt_in_BOTH_directions(self):
        """Discriminating and non-discriminating output from the real gate must both be writable.

        A validation rule the producer cannot satisfy is a rule that only fires on fixtures.
        """
        import z_assembly as za
        cases = {
            "discriminating": dict(v_mean=np.array([2.0]), v_blk=np.array([1.0]),
                                   ms=np.array([0.5])),
            "saturated": dict(v_mean=np.array([1.0]), v_blk=np.array([100.0]),
                              ms=np.array([1.0])),
        }
        for label, c in cases.items():
            with self.subTest(case=label):
                d = za.derive_variant_diagonals(c["v_mean"], c["v_blk"], c["ms"])
                g_mean, _ = za.compute_g(d["v_uni_mean"], d["v_blk"])
                g_cv, _ = za.compute_g(d["v_uni_cv"], d["v_blk"])
                res = za.run_pair_gates(g_recorded={"mean": g_mean, "cv": g_cv},
                                        diag_c_unified_mean=c["v_mean"],
                                        diag_c_blocksum=c["v_blk"], joint_mean_shift=c["ms"])
                blocks = self._blocks()
                blocks["inflation"] = res
                blocks["outcome"] = self._met(name="cause3_agg", value=0.01, prov="TEST",
                                              limit=0.01)
                with self._live(0.01, "TEST"):
                    r = zrec.build_receipt(**blocks)
                self.assertEqual(r["outcome"]["branch"], 3)

    def test_a_genuinely_backed_MET_outcome_is_accepted(self):
        """The positive direction, so the refusals above are not passing for the wrong reason."""
        blocks = self._blocks()
        blocks["outcome"] = self._met(name="cause3_agg", value=0.01, prov="TEST", limit=0.01)
        with self._live(0.01, "TEST"):
            r = zrec.build_receipt(**blocks)
        self.assertEqual(r["outcome"]["branch"], 3)

    def test_what_the_VALIDATOR_actually_emits_is_accepted_unchanged(self):
        """The end-to-end direction: `assess` must produce a receipt the receipt will take.

        A validation rule invented in the receipt and never satisfied by the real producer would
        be a rule that only fires on hand-written fixtures. This passes `assess`'s own output
        straight through, so the two agree on the shape by construction rather than by my reading.
        """
        declared = {"cause3_agg": zc.Boundary.declared("cause3_agg", 0.5, "TEST-APPROVAL"),
                    "cause3_med": zc.Boundary.declared("cause3_med", 0.5, "TEST-APPROVAL")}
        with mock.patch.dict(zc.Z_BOUNDARIES, declared):
            out = zv.assess(zv.LegSet([AGG, MED], predeclared_at="TEST"),
                            {"s_agg": 0.0, "s_med": 0.0}, all_valid())
            self.assertEqual(out.branch, 3)
            blocks = self._blocks()
            blocks["outcome"] = out.describe()
            r = zrec.build_receipt(**blocks)
        self.assertEqual(r["outcome"]["branch"], 3)

    @staticmethod
    def _met(name, value, prov, limit):
        return {"assessable": True, "branch": 3, "branch_label": "MET",
                "leg_results": {"agg": {"class": "aggregate", "statistic": 0.0, "limit": limit,
                                        "boundary": {"name": name, "status": "DECLARED",
                                                     "value": value, "provenance": prov}}}}

    @staticmethod
    def _live(value, provenance):
        return mock.patch.dict(
            zc.Z_BOUNDARIES,
            {"cause3_agg": zc.Boundary.declared("cause3_agg", value, provenance)})

    def test_the_real_unassessable_outcome_records_cleanly(self):
        L = zv.LegSet([AGG, MED], predeclared_at="TEST")
        out = zv.assess(L, {"s_agg": 0.0, "s_med": 0.0}, all_valid())
        blocks = self._blocks()
        blocks["outcome"] = out.describe()
        r = zrec.build_receipt(**blocks)
        self.assertFalse(r["outcome"]["assessable"])
        self.assertIsNone(r["outcome"]["branch"])

    def test_the_receipt_writes_and_stamps_atomically(self):
        d = writable_tmpdir_or_skip(self)
        path = os.path.join(d, "z_receipt.json")
        stamp = zrec.write_receipt(path, zrec.build_receipt(**self._blocks()))
        self.assertTrue(os.path.exists(path))
        self.assertEqual(len(stamp["sha256"]), 64)
        for key in ("inode", "device", "mtime_ns", "stamped_at_utc"):
            self.assertIn(key, stamp)


if __name__ == "__main__":
    unittest.main(verbosity=2)
