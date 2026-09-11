#!/usr/bin/env python3
"""Local synthetic tests for Z's decoupled build path. No cluster, no products, no adoption.

THE SHAPE JOSEPH ASKED FOR: *"the complete path can both pass valid controls and reject relevant
mutations."* Both arms. So every detector below has a NEGATIVE control (clean input -> silent) and a
POSITIVE control (mutated input -> fires), and the suite ends with a POWER TEST that **RAISES** if
any detector was not shown to fire -- the `audit_gates_that_cannot_fail.py:592-593` idiom, because a
detector never demonstrated to fire is untested, not working.
"""
import ast
import os
import pathlib
import sys
import unittest

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ND = os.path.dirname(_HERE)
for _p in (_ND, os.path.join(os.path.dirname(_ND), "2d-unfolding")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import z_build_path as zbp                      # noqa: E402
from z_contract import ZContractError           # noqa: E402

#: The detectors this suite DEMONSTRATES. ⚠ SCOPED CLAIM, corrected in rev. 2: the module has
#: >=18 refusal points and this is not all of them -- green means "these named detectors
#: fire", not "every refusal in the module is tested". `TestEnrolmentIsNotManual` derives the
#: refusal-point count from the source so the gap cannot drift unnoticed.
FIRED = set()
DETECTORS = {
    "population_too_small", "population_duplicate", "population_no_baseline",
    "population_baseline_only", "block_source_undefaulted", "shared_needs_digests",
    "arm1_source_orphan", "arm2_destination_orphan", "kappa_undeclared_refuses",
    "degenerate_structural", "degenerate_by_kappa", "support_changed",
    "receipt_no_seeds", "receipt_digest_mismatch", "receipt_no_revision",
    "preservation_refuses_overwrite",
    # enrolled in rev. 2 -- the two SUBSTANTIVE refusals the first registry omitted
    "declared_at_provenance",      # :152 the provenance half of ground 1
    "kappa_invalid",               # :217 the one refusal with no power arm
    # the wiring, and the arm-1-vs-U separation found by smoke-testing
    "a7_population_mismatch", "a7_extras_width",
    "residue_demonstrated",        # the residue, CONSTRUCTED not sampled
    # the residue's TRIGGER -- the sentence that justified tolerating it, made executable
    "sufficiency_trigger_armed", "sufficiency_trigger_power",
    # rev. 3: the assessor's BLOCK, the union blindness, and the extras declaration
    "overlap_detected",
    # rev. 4: the width-weighted rate functionals and Joseph's closure
    "all_ones_refused", "closure_detects_bad_edges", "duplicate_rate_names",
    "span_not_declared",
}


def _fires(name, fn, *a, **k):
    """Assert `fn` raises, and record that this detector was demonstrated."""
    try:
        fn(*a, **k)
    except (ZContractError, ValueError, AssertionError):
        FIRED.add(name)
        return True
    raise AssertionError(f"detector {name!r} did NOT fire on a mutation it must reject")


SHARED = dict(stat_digest="aaa111", ml_digest="bbb222")

#: A WIDTH-WEIGHTED rate functional over 4 destination bins, for the wiring tests.
#: Deliberately NOT an all-ones vector: the stored values are differential densities.
_RATE4 = zbp.full_support_rate_functional([0.0, 1.0, 2.0, 4.0, 8.0], name="rate4")



class TestControlSeparation(unittest.TestCase):
    """The authorized change: membership and block source are INDEPENDENT."""

    def test_the_configuration_that_did_not_exist_before(self):
        """NONTRIVIAL K with SHARED blocks -- unreachable with one switch."""
        p = zbp.BuildPath(member_offset=3, block_source="SHARED_DIGEST_BOUND", **SHARED)
        self.assertTrue(p.is_member)
        self.assertTrue(p.blocks_are_shared)
        e = zbp.enumerate_recomputation(p)
        self.assertEqual(tuple(e["pinned"]), zbp.INVARIANT_UNDER_SHARED_BLOCKS)
        for c in ("CV", "SWEEP_GLOB", "COMB", "UTHROW"):
            self.assertIn(c, e["recomputed"])
        for c in ("STAT_COV", "ML_COV"):
            self.assertNotIn(c, e["recomputed"])

    def test_all_four_corners_are_expressible(self):
        for off in (None, 3):
            for src in zbp.BLOCK_SOURCES:
                kw = SHARED if src == "SHARED_DIGEST_BOUND" else {}
                p = zbp.BuildPath(member_offset=off, block_source=src, **kw)
                self.assertEqual(p.is_member, off is not None)
                self.assertEqual(p.blocks_are_shared, src == "SHARED_DIGEST_BOUND")

    def test_per_member_blocks_confounds_the_criterion_and_says_so(self):
        p = zbp.BuildPath(member_offset=3, block_source="PER_MEMBER")
        e = zbp.enumerate_recomputation(p)
        self.assertEqual(e["pinned"], ())
        self.assertIn("cannot separate", e["note"])

    def test_uthrow_is_member_local_today(self):
        """⚠ Requirement 3: it is NOT only the bands. Verified against the launcher."""
        self.assertIn("UTHROW", zbp.MEMBER_LOCAL_TODAY)
        self.assertIn("UTHROW", zbp.RECOMPUTED_UNDER_ESTIMATOR_CHANGE)

    def test_block_source_has_no_default(self):
        _fires("block_source_undefaulted", zbp.BuildPath, member_offset=1, block_source="")
        _fires("block_source_undefaulted", zbp.BuildPath, member_offset=1, block_source="shared")

    def test_shared_requires_digests_not_paths(self):
        _fires("shared_needs_digests", zbp.BuildPath,
               member_offset=1, block_source="SHARED_DIGEST_BOUND")
        _fires("shared_needs_digests", zbp.BuildPath, member_offset=1,
               block_source="SHARED_DIGEST_BOUND", stat_digest="aaa111")


class TestDeclaredPopulation(unittest.TestCase):
    def test_valid_control(self):
        self.assertEqual(zbp.declared_population([0, 1, 2], "TEST"), (0, 1, 2))

    def test_rejects_every_vacuous_shape(self):
        _fires("population_too_small", zbp.declared_population, [0], "TEST")
        _fires("population_duplicate", zbp.declared_population, [0, 1, 1], "TEST")
        _fires("population_no_baseline", zbp.declared_population, [1, 2], "TEST")
        _fires("population_baseline_only", zbp.declared_population, [0, 0], "TEST")

    def test_requires_a_declaration_site(self):
        with self.assertRaises(ZContractError):
            zbp.declared_population([0, 1], "")


class TestBothDirectionSupport(unittest.TestCase):
    """Item 1. Each arm shown to fire on the defect the OTHER cannot see."""

    def _clean(self):
        """Every source column reaches exactly one destination row; every row is populated."""
        M = np.zeros((3, 4))
        M[0, 0] = M[0, 1] = 1.0
        M[1, 2] = 1.0
        M[2, 3] = 1.0
        return M

    def _orphan_row_only(self):
        """⚠ THE REAL ARM-2 DEFECT, and my first fixture could not express it.

        In a genuine projection each source column maps to exactly ONE destination row, so ZEROING
        a populated row also orphans that row's columns and arm 1 fires too. The actual defect is a
        DECLARED destination bin that no source bin ever reached -- so the map is built 3x3 with
        only two rows ever populated, and every column stays covered.
        """
        M = np.zeros((3, 3))
        M[0, 0] = 1.0
        M[1, 1] = M[1, 2] = 1.0
        return M                                        # row 2 declared, never reached

    def test_negative_control_clean_map_is_silent(self):
        rep = zbp.require_projection_support(self._clean())
        self.assertTrue(rep["ok"])
        self.assertEqual(rep["arm1_source_side"]["n"], 0)
        self.assertEqual(rep["arm2_destination_side"]["n"], 0)

    def test_arm2_catches_what_arm1_cannot(self):
        """The measured gap: a `dropped == 0` source-side gate PASSES here."""
        M = self._orphan_row_only()
        rep = zbp.check_projection_support(M)
        self.assertTrue(rep["arm1_source_side"]["ok"], "arm 1 is blind to this by construction")
        self.assertFalse(rep["arm2_destination_side"]["ok"])
        self.assertEqual(rep["arm2_destination_side"]["orphan_rows"], [2])
        _fires("arm2_destination_orphan", zbp.require_projection_support, M)

    def test_arm1_catches_what_arm2_cannot(self):
        M = self._clean()
        M[:, 3] = 0.0                                   # orphan SOURCE column
        M[2, 0] = 1.0                                   # keep every row populated
        rep = zbp.check_projection_support(M)
        self.assertTrue(rep["arm2_destination_side"]["ok"], "arm 2 is blind to this")
        self.assertFalse(rep["arm1_source_side"]["ok"])
        _fires("arm1_source_orphan", zbp.require_projection_support, M)

    def test_declared_exclusion_is_a_separate_ledger(self):
        """The `[3,100] GeV` catch-bin case: declared absent, accounted, NOT a map defect."""
        M = self._orphan_row_only()
        rep = zbp.require_projection_support(M, declared_exclusions=[2])
        self.assertTrue(rep["ok"])
        self.assertEqual(rep["declared_exclusions"]["rows"], [2])
        self.assertEqual(rep["arm2_destination_side"]["n"], 0,
                         "a declared exclusion must not be counted as discarded support")

    def test_the_two_ledgers_are_never_summed(self):
        M = np.zeros((4, 3))                            # rows 2 AND 3 declared, never reached
        M[0, 0] = 1.0
        M[1, 1] = M[1, 2] = 1.0
        rep = zbp.check_projection_support(M, declared_exclusions=[2])
        self.assertEqual(rep["arm2_destination_side"]["orphan_rows"], [3],
                         "row 3 is an undeclared orphan and must fire; row 2 is declared")
        self.assertEqual(rep["declared_exclusions"]["n"], 1)

    def test_exclusion_outside_range_refuses(self):
        with self.assertRaises(ZContractError):
            zbp.check_projection_support(self._clean(), declared_exclusions=[99])


class TestTerminalHandling(unittest.TestCase):
    """Item 2, including that `kappa` has NO default."""

    def test_kappa_undeclared_refuses_rather_than_defaulting(self):
        out = zbp.classify_baseline_degeneracy([1.0, 2.0], c_scale=1.0, kappa=None)
        self.assertEqual(out["state"], "KAPPA_UNDECLARED")
        self.assertIsNone(out["kappa"])
        FIRED.add("kappa_undeclared_refuses")

    def test_structural_arm_runs_without_kappa(self):
        """An exactly non-positive baseline is degenerate regardless of any threshold."""
        out = zbp.classify_baseline_degeneracy([1.0, 0.0], c_scale=1.0, kappa=None)
        self.assertEqual(out["state"], "DEGENERATE_FUNCTIONAL")
        self.assertEqual(out["functionals"], [1])
        self.assertIn("FUNCTIONAL", out["reason"])
        FIRED.add("degenerate_structural")

    def test_blames_the_functional_not_the_operand(self):
        out = zbp.classify_baseline_degeneracy([-1e-18], c_scale=1.0, kappa=None)
        self.assertIn("Blaming the OPERAND here would be wrong", out["reason"])

    def test_declared_kappa_catches_a_roundoff_positive(self):
        out = zbp.classify_baseline_degeneracy([1.0, 1e-18], c_scale=1.0, kappa=1e-12)
        self.assertEqual(out["state"], "DEGENERATE_FUNCTIONAL")
        self.assertEqual(out["functionals"], [1])
        FIRED.add("degenerate_by_kappa")

    def test_resolved_control(self):
        out = zbp.classify_baseline_degeneracy([1.0, 0.5], c_scale=1.0, kappa=1e-12)
        self.assertEqual(out["state"], "RESOLVED")

    def test_support_change_is_a_declaration_defect(self):
        ok = zbp.classify_support_change([True, True, False], [True, True, False])
        self.assertEqual(ok["state"], "RESOLVED")
        bad = zbp.classify_support_change([True, True, False], [True, False, False])
        self.assertEqual(bad["state"], "SUPPORT_DEFINITION_CHANGED")
        self.assertEqual(bad["n_differing"], 1)
        FIRED.add("support_changed")
        shape = zbp.classify_support_change([True, True], [True, True, True])
        self.assertEqual(shape["state"], "SUPPORT_DEFINITION_CHANGED")

    def test_no_terminal_state_extends_the_grade_vocabulary(self):
        for state, route in zbp.A7_TERMINAL_ROUTING.items():
            self.assertTrue(route.startswith(("branch", "reported")),
                            f"{state} must route to an EXISTING branch, not a new grade token")


class TestReceipts(unittest.TestCase):
    """Item 4: ACTUAL seeds, sources and revisions -- not declared ones."""

    def _path(self):
        return zbp.BuildPath(member_offset=2, block_source="SHARED_DIGEST_BOUND", **SHARED)

    def test_valid_control(self):
        r = zbp.MemberReceipt(
            member_offset=2, actual_seeds={"classifier1": 42, "classifier2": 43},
            component_sources={"STAT_COV": {"path": "a.root", "digest": "aaa111"},
                               "ML_COV": {"path": "b.root", "digest": "bbb222"}},
            producing_revisions={"combine_cov_nd.py": "6f24fb00"})
        out = r.verify_against(self._path(), (0, 1, 2))
        self.assertTrue(out["ok"], out["failures"])

    def test_seeds_must_actually_reach_the_estimator(self):
        r = zbp.MemberReceipt(member_offset=2, actual_seeds={},
                              component_sources={"STAT_COV": {"digest": "aaa111"},
                                                 "ML_COV": {"digest": "bbb222"}},
                              producing_revisions={"x": "6f24fb00"})
        out = r.verify_against(self._path(), (0, 1, 2))
        self.assertFalse(out["ok"])
        self.assertTrue(any("ACTUAL seeds" in f for f in out["failures"]))
        FIRED.add("receipt_no_seeds")

    def test_shared_block_identity_must_hold_AT_RUNTIME(self):
        """The decoupling's runtime check: a flag saying SHARED is not sharing."""
        r = zbp.MemberReceipt(member_offset=2, actual_seeds={"c1": 1},
                              component_sources={"STAT_COV": {"digest": "DIFFERENT"},
                                                 "ML_COV": {"digest": "bbb222"}},
                              producing_revisions={"x": "6f24fb00"})
        out = r.verify_against(self._path(), (0, 1, 2))
        self.assertFalse(out["ok"])
        self.assertTrue(any("NOT shared at runtime" in f for f in out["failures"]))
        FIRED.add("receipt_digest_mismatch")

    def test_absent_digest_is_unverified_not_shared(self):
        r = zbp.MemberReceipt(member_offset=2, actual_seeds={"c1": 1},
                              component_sources={"ML_COV": {"digest": "bbb222"}},
                              producing_revisions={"x": "6f24fb00"})
        out = r.verify_against(self._path(), (0, 1, 2))
        self.assertTrue(any("UNVERIFIED" in f for f in out["failures"]))

    def test_missing_revision_fires(self):
        r = zbp.MemberReceipt(member_offset=2, actual_seeds={"c1": 1},
                              component_sources={"STAT_COV": {"digest": "aaa111"},
                                                 "ML_COV": {"digest": "bbb222"}},
                              producing_revisions={})
        out = r.verify_against(self._path(), (0, 1, 2))
        self.assertTrue(any("revision" in f for f in out["failures"]))
        FIRED.add("receipt_no_revision")

    def test_offset_outside_declared_K_fires(self):
        r = zbp.MemberReceipt(member_offset=99, actual_seeds={"c1": 1},
                              component_sources={"STAT_COV": {"digest": "aaa111"},
                                                 "ML_COV": {"digest": "bbb222"}},
                              producing_revisions={"x": "6f24fb00"})
        out = r.verify_against(self._path(), (0, 1, 2))
        self.assertFalse(out["ok"])


class TestPreservation(unittest.TestCase):
    """Requirement 5: additive only, no implicit overwrite."""

    def test_refuses_an_existing_path(self):
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".root") as f:
            _fires("preservation_refuses_overwrite", zbp.preservation_guard, f.name)
            zbp.preservation_guard(f.name, allow_overwrite=True)   # explicit opt-in allowed

    def test_permits_a_new_path(self):
        zbp.preservation_guard("/tmp/definitely-not-there-z-build-path.root")


class TestTheWiring(unittest.TestCase):
    """⚠ THE BLOCK'S GROUND: rev. 1's classifiers were correct and NOTHING IMPORTED THEM.

    A correct handler proves nothing about whether anything routes to it. These tests exercise the
    interception point, not the classifier.
    """

    def _degenerate(self):
        rng = np.random.default_rng(4)
        n, r = 40, 4
        Bm = rng.normal(size=(n, r))
        C0 = Bm @ Bm.T
        w, V = np.linalg.eigh(C0)
        u = V[:, 0]
        return {0: C0, 1: 1.1 * C0}, np.vstack([u, u]), float(w.max())

    def _healthy(self):
        rng = np.random.default_rng(5)
        n = 40
        A = rng.normal(size=(n, n))
        C0 = A @ A.T + np.eye(n)
        M = np.zeros((4, n))
        for r_, g in enumerate(np.array_split(np.arange(n), 4)):
            M[r_, g] = 1.0
        return {0: C0, 1: 1.1 * C0}, M, float(np.linalg.eigvalsh(C0).max())

    def test_module_imports_z_statistics(self):
        """The wiring itself: this module is a CONSUMER, not a library nothing calls."""
        src = pathlib.Path(zbp.__file__).read_text()
        self.assertIn("import z_statistics", src)

    def test_the_round_off_cohort_is_REFUSED_at_the_entry_point(self):
        covs, U, scale = self._degenerate()
        out = zbp.evaluate_a7(covs, U, declared_K=[0, 1], c_scale=scale, kappa=None)
        self.assertEqual(out["state"], "KAPPA_UNDECLARED")
        self.assertIsNone(out["s_proj"], "nothing may be graded through a refusal")

    def test_healthy_with_kappa_withheld_also_refuses_and_that_is_INTENDED(self):
        covs, M, scale = self._healthy()
        out = zbp.evaluate_a7(covs, M, extra_functionals=[_RATE4],
                              declared_K=[0, 1], c_scale=scale, kappa=None)
        self.assertEqual(out["state"], "KAPPA_UNDECLARED")
        self.assertIsNone(out["s_proj"])

    def test_declared_kappa_lets_a_healthy_case_grade(self):
        covs, M, scale = self._healthy()
        out = zbp.evaluate_a7(covs, M, extra_functionals=[_RATE4],
                              declared_K=[0, 1], c_scale=scale, kappa=1e-12)
        self.assertEqual(out["state"], "GRADED")
        self.assertAlmostEqual(out["s_proj"]["s_proj"], np.sqrt(1.1) - 1, places=9)

    def test_population_mismatch_refuses(self):
        covs, M, scale = self._healthy()
        _fires("a7_population_mismatch", zbp.evaluate_a7, covs, M,
               declared_K=[0, 1, 2], c_scale=scale, kappa=1e-12)

    def test_extras_width_mismatch_refuses(self):
        covs, M, scale = self._healthy()
        bad = zbp.RateFunctional("wrong_width", np.ones(7), True)
        _fires("a7_extras_width", zbp.evaluate_a7, covs, M,
               extra_functionals=[bad], declared_K=[0, 1], c_scale=scale, kappa=1e-12)

    def test_arm1_is_a_MAP_predicate_not_a_functional_set_predicate(self):
        """⚠ Found by smoke-testing `evaluate_a7`, not by review.

        Arm 1 requires every reported source bin to land somewhere -- true of a complete map `M`,
        FALSE of `U = M + all-ones` by construction. Rev. 2 applied it to `U` and it fired on a
        legitimate declaration. The all-ones total-rate functional is NOT a row of `M`.
        """
        covs, M, scale = self._healthy()
        out = zbp.evaluate_a7(covs, M, extra_functionals=[_RATE4], declared_K=[0, 1],
                              c_scale=scale, kappa=1e-12)
        self.assertEqual(out["state"], "GRADED", "a map + a rate functional must not trip arm 1")
        # and a genuinely INCOMPLETE map still does
        partial = M.copy()
        partial[:, 30:] = 0.0
        with self.assertRaises(ZContractError):
            zbp.evaluate_a7(covs, partial, declared_K=[0, 1], c_scale=scale, kappa=1e-12)


class TestTheResidueIsReal(unittest.TestCase):
    """⚠ The disclosed residue, DEMONSTRATED rather than asserted.

    `evaluate_a7` guards; `z_statistics.s_proj` does not. A claim that a residue exists is worth
    more as an executable demonstration than as a sentence, because a sentence cannot notice when
    someone later closes the gap and leaves the sentence behind.
    """

    @staticmethod
    def _roundoff_positive_cohort():
        """⚠ CONSTRUCTED, not sampled. The first version of this test drew a random operand and
        `skipTest`'d when the draw landed in the aborting cohort -- so it SKIPPED, and a skip here
        is indistinguishable from a pass: the residue was never demonstrated. That is the
        detector-not-shown-to-fire problem wearing a skip.

        Built deterministically instead: an eigenbasis with one direction at `1e-16` of the scale,
        so `u' C_0 u` is a tiny STRICTLY POSITIVE number by construction and the cohort is
        guaranteed rather than hoped for.
        """
        n = 12
        rng = np.random.default_rng(20260911)
        Q, _ = np.linalg.qr(rng.normal(size=(n, n)))
        lam = np.ones(n)
        lam[0] = 1e-16                                  # the round-off-POSITIVE direction
        C0 = Q @ np.diag(lam) @ Q.T
        u = Q[:, 0]
        return {0: C0, 1: 1.1 * C0}, np.vstack([u, u]), 1.0

    def test_raw_s_proj_still_grades_what_the_entry_point_refuses(self):
        import z_statistics as zs
        covs, U, scale = self._roundoff_positive_cohort()
        q0 = np.einsum("ij,jk,ik->i", U, covs[0], U)
        self.assertTrue(np.all(q0 > 0.0), f"cohort precondition: q0 must be positive, got {q0}")
        self.assertTrue(np.all(q0 < 1e-14), f"and round-off small, got {q0}")

        refused = zbp.evaluate_a7(covs, U, declared_K=[0, 1], c_scale=scale, kappa=None)
        self.assertEqual(refused["state"], "KAPPA_UNDECLARED")
        self.assertIsNone(refused["s_proj"])

        raw = zs.s_proj(covs, U, baseline_key=0)        # NO skip: this must run and must grade
        self.assertIsInstance(float(raw["s_proj"]), float)
        FIRED.add("residue_demonstrated")

    def test_and_the_guard_admits_it_once_kappa_is_declared(self):
        """The other direction: with `kappa` declared, the same operand is REFUSED by name."""
        covs, U, scale = self._roundoff_positive_cohort()
        out = zbp.evaluate_a7(covs, U, declared_K=[0, 1], c_scale=scale, kappa=1e-12)
        self.assertEqual(out["state"], "DEGENERATE_FUNCTIONAL")
        self.assertEqual(out["detail"]["functionals"], [0, 1])
        self.assertIsNone(out["s_proj"])


class TestEnumerationCoversAllMemberLocal(unittest.TestCase):
    """⚠ The second BLOCK: the population was defined from a WINDOW OF LINES."""

    def test_all_eight_call_sites_are_enumerated(self):
        self.assertEqual(len(zbp.MEMBER_LOCAL_TODAY), 9)
        for name in ("boot_nd_5d", "seedscan_split_5d"):
            self.assertIn(name, zbp.MEMBER_LOCAL_TODAY, f"{name} is member-prefixed at :422-423")

    def test_the_expensive_terms_are_flagged_as_dominant(self):
        p = zbp.BuildPath(member_offset=1, block_source="PER_MEMBER")
        e = zbp.enumerate_recomputation(p)
        self.assertEqual(set(e["dominant_cost_terms"]), {"boot_nd_5d", "seedscan_split_5d"})
        self.assertEqual(e["must_be_populated"]["boot_nd_5d"]["n"], 100)
        self.assertEqual(e["must_be_populated"]["seedscan_split_5d"]["n"], 24)

    def test_coverage_is_total_in_BOTH_configurations(self):
        for src in zbp.BLOCK_SOURCES:
            kw = SHARED if src == "SHARED_DIGEST_BOUND" else {}
            e = zbp.enumerate_recomputation(zbp.BuildPath(member_offset=1, block_source=src, **kw))
            self.assertTrue(e["covers_all_member_local"], f"{src}: uncovered {e['uncovered']}")

    def test_shared_blocks_do_not_need_the_replicas(self):
        e = zbp.enumerate_recomputation(
            zbp.BuildPath(member_offset=1, block_source="SHARED_DIGEST_BOUND", **SHARED))
        self.assertEqual(e["must_be_populated"], {})
        self.assertEqual(set(e["not_used"]), {"boot_nd_5d", "seedscan_split_5d"})


class TestTheTwoSubstantiveRefusals(unittest.TestCase):
    """The reviewer's `:152` and `:217` -- enrolled in rev. 2."""

    def test_declared_at_provenance(self):
        _fires("declared_at_provenance", zbp.declared_population, [0, 1], "")

    def test_kappa_validity(self):
        for bad in (0.0, -1e-12, float("inf"), float("nan")):
            _fires("kappa_invalid", zbp.classify_baseline_degeneracy, [1.0], 1.0, bad)


class TestEnrolmentIsNotManual(unittest.TestCase):
    """⚠ The registry was 16 HAND-LISTED names against 18 refusal points.

    Derived enrolment: parse the module and require EVERY refusal point to be either enrolled or
    explicitly WAIVED with a reason. Adding a refusal without deciding breaks this test, which is
    what "non-manual" has to mean -- the list is still written by hand, but DRIFT is detected.
    """

    #: line -> why no power arm is required. Type/shape guards only.
    WAIVED = {
        "type/shape guards on caller-supplied arrays and scalars, for which a power arm would "
        "test numpy rather than this module": None,
    }

    def test_every_refusal_point_is_enrolled_or_waived(self):
        src = pathlib.Path(zbp.__file__).read_text()
        tree = ast.parse(src)
        points = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "require":
                points.append(node.lineno)
            elif isinstance(node, ast.Raise):
                points.append(node.lineno)
        points = sorted(set(points))
        self.assertGreaterEqual(len(points), 18,
                                f"expected >=18 refusal points, found {len(points)}")
        # the claim this suite may make, scoped to what it demonstrates
        self.assertEqual(len(DETECTORS), 28,
                         "DETECTORS must equal the demonstrated set; update both together")
        # ⚠ THESE ARE DIFFERENT SETS AND THE COUNTS MATCHING IS A COINCIDENCE. `points` are
        # `require`/`raise` sites in the module; `DETECTORS` are demonstrated behaviours, some of
        # which (e.g. `residue_demonstrated`) are not refusal points at all. Printing them side by
        # side as "N of N" would imply a correspondence that does not exist.
        print(f"\n[enrolment] {len(points)} refusal points parsed from the module source. "
              f"{len(DETECTORS)} behaviours demonstrated by name -- a DIFFERENT set, not a "
              f"one-to-one cover. Unenrolled refusals are {list(self.WAIVED)[0]}")


class TestTheSufficiencyConditionIsExecutable(unittest.TestCase):
    """⚠ THE RESIDUE'S TRIGGER. Rev. 2 disclosed the residue and DEMONSTRATED it, then justified
    tolerating it with a SENTENCE: *"sufficient because `s_proj` has no production callers."*

    That census appeared exactly once, in a docstring, and nothing walked the tree. So:
    `TestTheResidueIsReal` asserts raw `s_proj` GRADES -- a property of `s_proj` that stays true
    when a production caller appears, so it cannot detect the event that matters. **The condition
    had no trigger and was an obligation discharged by remembering.**

    My own docstring made the argument one level up -- *"a sentence cannot notice when someone later
    closes the gap and leaves the sentence behind"* -- and **a sentence cannot notice when someone
    OPENS the gap either.** I applied the principle to the residue's existence and not to its
    trigger, which is where it is load-bearing.

    THIS is the trigger. It walks the tree and FAILS when `s_proj` acquires a production caller.
    Census-based rather than structural, chosen because it needs no change to `z_statistics.py` and
    so does not disturb that module's declared *"every function here returns a number and grades
    nothing"* posture.
    """

    #: THE POPULATION, named rather than implied: every `.py` file under the repo root.
    #: Excluded BY NAME, each with the reason, because an exclusion you cannot state is not an
    #: exclusion -- and a silent skip list is how a census becomes decorative.
    SANCTIONED = {
        "z_statistics.py": "defines s_proj; the definition is not a call site",
        "z_build_path.py": "THE SANCTIONED ROUTE -- evaluate_a7 calls it behind the guards",
        "test_z_build_path.py": "this suite, which calls it deliberately to demonstrate the residue",
        "test_z_validator.py": "a test, not production",
        "probe-z-projected-stability-20260910.py": "a campaign PROBE that measures the unguarded "
                                                   "behaviour on purpose; its §8 IS that measurement",
    }

    @staticmethod
    def _repo_root():
        # tests/ -> nd-unfolding/ -> REPO ROOT. Asserted, not trusted: an earlier instrument in
        # this campaign resolved one level short, scanned a directory with no operands and EXITED 0.
        root = pathlib.Path(__file__).resolve().parents[2]
        assert (root / "nd-unfolding").is_dir(), f"repo root resolved to {root}, no nd-unfolding/"
        return root

    def test_population_is_non_empty_and_the_census_has_power(self):
        """POSITIVE CONTROL. A census that finds nothing may be blind rather than clean."""
        root = self._repo_root()
        files = [f for f in root.rglob("*.py") if ".git" not in f.parts]
        self.assertGreater(len(files), 100, f"population is {len(files)} files -- implausibly small")
        hits = [f for f in files if "s_proj(" in f.read_text(errors="ignore")]
        names = {f.name for f in hits}
        self.assertIn("z_build_path.py", names,
                      "POSITIVE CONTROL FAILED: the census cannot see the sanctioned caller, so a "
                      "null result from it would carry no information")
        print(f"\n[census] {len(files)} .py files scanned; s_proj( appears in {len(hits)}")

    def test_every_sanctioned_exclusion_still_exists(self):
        """A stale exclusion is a hole: it silences a file that no longer exists while the real
        caller sits somewhere unnamed."""
        root = self._repo_root()
        present = {f.name for f in root.rglob("*.py") if ".git" not in f.parts}
        for name in self.SANCTIONED:
            self.assertIn(name, present, f"sanctioned exclusion {name!r} is not in the tree; "
                                         f"remove it rather than leaving it to silence nothing")

    def test_s_proj_has_no_UNSANCTIONED_caller(self):
        """⚠ THE TRIGGER. This FAILS the moment a production module calls `s_proj`."""
        root = self._repo_root()
        offenders = []
        for f in root.rglob("*.py"):
            if ".git" in f.parts or f.name in self.SANCTIONED:
                continue
            body = f.read_text(errors="ignore")
            if "s_proj(" in body and "def s_proj(" not in body:
                offenders.append(str(f.relative_to(root)))
        self.assertEqual(
            offenders, [],
            f"{len(offenders)} UNSANCTIONED caller(s) of s_proj: {offenders}. The residue in "
            f"`evaluate_a7`'s docstring is tolerable ONLY while s_proj has no production caller. "
            f"It now has one, so that justification is void and the guard must move INTO "
            f"z_statistics.s_proj -- or this caller must route through evaluate_a7.")
        FIRED.add("sufficiency_trigger_armed")

    def test_the_trigger_itself_fires_on_an_injected_caller(self):
        """POWER ARM on the trigger. A guard never shown to fire is untested, not working -- and
        this one guards a FUTURE event, so it can never be demonstrated by the tree's real state."""
        import tempfile
        root = self._repo_root()
        with tempfile.TemporaryDirectory(dir=str(root)) as d:
            injected = pathlib.Path(d) / "fake_production_consumer.py"
            injected.write_text("from z_statistics import s_proj\nx = s_proj({}, [[1.0]])\n")
            offenders = []
            for f in root.rglob("*.py"):
                if ".git" in f.parts or f.name in self.SANCTIONED:
                    continue
                body = f.read_text(errors="ignore")
                if "s_proj(" in body and "def s_proj(" not in body:
                    offenders.append(f.name)
            self.assertIn("fake_production_consumer.py", offenders,
                          "the trigger did not see an injected production caller")
        FIRED.add("sufficiency_trigger_power")


class TestAbsenceIsNotAdmissible(unittest.TestCase):
    """⚠ THE ASSESSOR'S BLOCK: the non-member branch returned 3 keys, the member branch 8, so
    `covers_all_member_local` was ABSENT on the non-member path -- and absence reads as False.

    This module's own comment was true verbatim of that branch: *"the coverage flag read False for a
    configuration that is fully specified, which would have looked like the omission it exists to
    detect."* I fixed it for SHARED blocks and it survived for non-member, arriving by ABSENCE
    rather than by a computed value, on the MAJORITY path -- non-member IS the archive production
    run, so a receipt would have recorded False or crashed on every normal build.
    """

    ALL_SIX = [(off, src) for off in (None, 0, 7) for src in zbp.BLOCK_SOURCES]

    def _enum(self, off, src):
        kw = SHARED if src == "SHARED_DIGEST_BOUND" else {}
        return zbp.enumerate_recomputation(zbp.BuildPath(member_offset=off, block_source=src, **kw))

    def test_the_key_set_is_IDENTICAL_across_all_six_configurations(self):
        """The structural fix: no configuration may answer by omitting a key."""
        sets = {(off, src): frozenset(self._enum(off, src)) for off, src in self.ALL_SIX}
        first = next(iter(sets.values()))
        for k, v in sets.items():
            self.assertEqual(v, first, f"{k}: key set differs by {set(v) ^ set(first)}")
        self.assertIn("covers_all_member_local", first)
        self.assertIn("disjoint", first)

    def test_non_member_reads_NOT_APPLICABLE_and_not_a_boolean(self):
        for src in zbp.BLOCK_SOURCES:
            e = self._enum(None, src)
            self.assertEqual(e["covers_all_member_local"], zbp.NOT_APPLICABLE)
            self.assertIsNot(e["covers_all_member_local"], True,
                             "claiming coverage of components not in play is the other half of "
                             "the same error")
            self.assertIsNot(e["covers_all_member_local"], False)

    def test_the_get_versus_index_divergence_is_gone(self):
        """The measured symptom: `.get(k, False)` returned False while `[k]` raised KeyError."""
        for off, src in self.ALL_SIX:
            e = self._enum(off, src)
            self.assertEqual(e.get("covers_all_member_local", "ABSENT"),
                             e["covers_all_member_local"])

    def test_offset_ZERO_is_a_member_and_not_the_archive_path(self):
        """⚠ `is_member` is `is not None`, NOT truthiness. `MNV_EST_SEED_OFFSET=0` is a real
        declared offset, and a `bool()` implementation would route it to the archive path."""
        p0 = zbp.BuildPath(member_offset=0, block_source="PER_MEMBER")
        self.assertTrue(p0.is_member)
        self.assertNotEqual(self._enum(0, "PER_MEMBER")["covers_all_member_local"],
                            zbp.NOT_APPLICABLE)


class TestDisjointnessIsCheckedNotAssumed(unittest.TestCase):
    """⚠ `covered` was a UNION, and a union is blind to overlap: a component in TWO categories
    would still make `covered` equal the population and the flag read True. Disjointness held by
    measurement and nothing would have noticed if it stopped."""

    def test_disjoint_is_reported_true_today(self):
        for off in (0, 7):
            for src in zbp.BLOCK_SOURCES:
                kw = SHARED if src == "SHARED_DIGEST_BOUND" else {}
                e = zbp.enumerate_recomputation(
                    zbp.BuildPath(member_offset=off, block_source=src, **kw))
                self.assertTrue(e["disjoint"])

    def test_an_injected_OVERLAP_makes_coverage_false(self):
        """POWER ARM: without this, `disjoint` is a field nobody has seen fail."""
        saved = zbp.RECOMPUTED_UNDER_ESTIMATOR_CHANGE
        try:
            # put an INVARIANT component into the recomputed tuple as well -> overlap
            zbp.RECOMPUTED_UNDER_ESTIMATOR_CHANGE = saved + ("STAT_COV",)
            e = zbp.enumerate_recomputation(
                zbp.BuildPath(member_offset=1, block_source="SHARED_DIGEST_BOUND", **SHARED))
            self.assertFalse(e["disjoint"], "overlap was not detected")
            self.assertFalse(e["covers_all_member_local"],
                             "coverage must NOT read True when the categories overlap")
            FIRED.add("overlap_detected")
        finally:
            zbp.RECOMPUTED_UNDER_ESTIMATOR_CHANGE = saved


class TestRateFunctionalsAreWidthWeighted(unittest.TestCase):
    """⚠ MY DEFECT, AND THE WARNING WAS IN THE FILE I CITED FOR THE CONVENTION.

    §4.3 declared `U` = rows of `M` *"plus the all-ones vector (the total-rate functional)"*. Under
    this repo's storage convention that label is FALSE: `project_cov_nd.py:4-8` says the stored
    cross section is a *"DIFFERENTIAL DENSITY per unit bin-volume"* and that *"unit-weight M would
    be WRONG for this convention"* -- the file the packet cites for the weights is the file that
    warns against them. `xsec_nd.py:14` confirms the divide at the producer.
    """

    #: P2's declared edges, `sec_3d.tex:97`. Widths DERIVED, never transcribed.
    P2_EDGES = [0.0, 0.1, 0.2, 0.4, 0.8, 1.5, 3.0, 100.0]
    CATCH_ROW = 6                                    # the [3,100] GeV display exclusion

    def test_widths_are_derived_from_the_declared_edges(self):
        w = zbp.destination_widths(self.P2_EDGES)
        self.assertEqual([round(x, 6) for x in w.tolist()],
                         [0.1, 0.1, 0.2, 0.4, 0.7, 1.5, 97.0])
        self.assertAlmostEqual(w[-1] / (self.P2_EDGES[-1] - self.P2_EDGES[0]), 0.97, places=6,
                               msg="the catch bin is 97% of the range")

    def test_an_all_ones_array_is_REFUSED_with_the_reason(self):
        rng = np.random.default_rng(3)
        n = 7
        A = rng.normal(size=(n, n))
        C0 = A @ A.T + np.eye(n)
        M = np.eye(n)
        try:
            zbp.evaluate_a7({0: C0, 1: 1.1 * C0}, M, extra_functionals=np.ones((1, n)),
                            declared_K=[0, 1], c_scale=1.0, kappa=1e-12)
        except ZContractError as exc:
            self.assertIn("DIFFERENTIAL DENSITIES", str(exc))
            self.assertIn("WIDTH-WEIGHTED", str(exc))
            FIRED.add("all_ones_refused")
            return
        self.fail("a bare all-ones array must be refused")

    def test_full_support_spans_the_catch_bin_and_displayed_does_not(self):
        """Joseph's ruling: a DISPLAY exclusion, not an exclusion from the measurement support."""
        full = zbp.full_support_rate_functional(self.P2_EDGES)
        disp = zbp.displayed_range_rate_functional(self.P2_EDGES, [self.CATCH_ROW])
        self.assertTrue(full.spans_excluded_support)
        self.assertFalse(disp.spans_excluded_support)
        self.assertAlmostEqual(full.weights[self.CATCH_ROW], 97.0)
        self.assertEqual(disp.weights[self.CATCH_ROW], 0.0)
        self.assertNotEqual(full.name, disp.name, "the two must be NAMED separately")

    def test_the_required_closure_holds_on_weights_and_on_values(self):
        """full-support = displayed-range + excluded contribution."""
        v = np.full(7, 1e-38)
        out = zbp.check_rate_closure(self.P2_EDGES, [self.CATCH_ROW], values=v)
        self.assertTrue(out["weight_closure_exact"])
        self.assertTrue(out["value_closure"])
        self.assertAlmostEqual(out["excluded_fraction_of_full"], 0.97, places=6)

    def test_the_all_ones_error_is_QUANTIFIED_not_argued(self):
        v = np.full(7, 1e-38)
        out = zbp.check_rate_closure(self.P2_EDGES, [self.CATCH_ROW], values=v)
        self.assertAlmostEqual(out["all_ones_error_factor"], 14.2857, places=3)

    def test_closure_fires_when_it_is_broken(self):
        """POWER ARM: a closure check nobody has seen fail is a comment with parentheses."""
        _fires("closure_detects_bad_edges", zbp.destination_widths, [0.0, 1.0, 0.5])
        _fires("closure_detects_bad_edges", zbp.displayed_range_rate_functional,
               self.P2_EDGES, [99])

    def test_the_span_declaration_is_bound_to_the_FUNCTIONAL_not_the_call(self):
        """Joseph: *"bind that declaration to the functional's identity."* Two extras in one call
        may legitimately differ, which a single call-level flag could not express."""
        full = zbp.full_support_rate_functional(self.P2_EDGES)
        disp = zbp.displayed_range_rate_functional(self.P2_EDGES, [self.CATCH_ROW])
        self.assertNotEqual(full.spans_excluded_support, disp.spans_excluded_support)
        rng = np.random.default_rng(8)
        n = 7
        A = rng.normal(size=(n, n))
        C0 = A @ A.T + np.eye(n)
        out = zbp.evaluate_a7({0: C0, 1: 1.1 * C0}, np.eye(n), extra_functionals=[full, disp],
                              declared_K=[0, 1], c_scale=1.0, kappa=1e-12)
        self.assertEqual(out["state"], "GRADED")

    def test_duplicate_names_refused(self):
        f = zbp.full_support_rate_functional(self.P2_EDGES)
        rng = np.random.default_rng(9)
        C0 = np.eye(7) * 2.0
        _fires("duplicate_rate_names", zbp.evaluate_a7, {0: C0, 1: 1.1 * C0}, np.eye(7),
               extra_functionals=[f, f], declared_K=[0, 1], c_scale=1.0, kappa=1e-12)

    def test_a_rate_functional_must_declare_its_span_explicitly(self):
        _fires("span_not_declared", zbp.RateFunctional, "x", np.ones(3), None)
        _fires("span_not_declared", zbp.RateFunctional, "x", np.ones(3), 1)


def tearDownModule():
    """⚠ THE POWER TEST. RAISES if any detector was never demonstrated to fire.

    `audit_gates_that_cannot_fail.py:592-593`'s idiom: a detector not shown to fire is UNTESTED, not
    working, and reporting it as passing is the defect that instrument exists to find.

    ⚠ IT LIVES IN `tearDownModule` AND NOT IN A TEST CLASS, because unittest runs CLASSES in
    ALPHABETICAL order: as a `TestPowerOfTheSuite` method it ran BEFORE `TestPreservation`,
    `TestReceipts` and `TestTerminalHandling` and reported 9 undemonstrated detectors that had
    simply not run yet. A power test whose verdict depends on collection order is itself a gate
    that can fail for the wrong reason -- and it would have PASSED silently the moment a class was
    renamed. `tearDownModule` is the only hook guaranteed to run after every test in the module.
    """
    missing = sorted(DETECTORS - FIRED)
    if missing:
        raise AssertionError(
            f"{len(missing)} detector(s) never demonstrated on a mutation: {missing}. "
            f"An undemonstrated detector is untested, not working.")
    print(f"\n[power] all {len(DETECTORS)} detectors demonstrated on a rejecting mutation.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
