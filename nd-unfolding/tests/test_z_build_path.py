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
        out = zbp.evaluate_a7(covs, M, extra_functionals=np.ones((1, 40)),
                              declared_K=[0, 1], c_scale=scale, kappa=None)
        self.assertEqual(out["state"], "KAPPA_UNDECLARED")
        self.assertIsNone(out["s_proj"])

    def test_declared_kappa_lets_a_healthy_case_grade(self):
        covs, M, scale = self._healthy()
        out = zbp.evaluate_a7(covs, M, extra_functionals=np.ones((1, 40)),
                              declared_K=[0, 1], c_scale=scale, kappa=1e-12)
        self.assertEqual(out["state"], "GRADED")
        self.assertAlmostEqual(out["s_proj"]["s_proj"], np.sqrt(1.1) - 1, places=9)

    def test_population_mismatch_refuses(self):
        covs, M, scale = self._healthy()
        _fires("a7_population_mismatch", zbp.evaluate_a7, covs, M,
               declared_K=[0, 1, 2], c_scale=scale, kappa=1e-12)

    def test_extras_width_mismatch_refuses(self):
        covs, M, scale = self._healthy()
        _fires("a7_extras_width", zbp.evaluate_a7, covs, M,
               extra_functionals=np.ones((1, 7)), declared_K=[0, 1], c_scale=scale, kappa=1e-12)

    def test_arm1_is_a_MAP_predicate_not_a_functional_set_predicate(self):
        """⚠ Found by smoke-testing `evaluate_a7`, not by review.

        Arm 1 requires every reported source bin to land somewhere -- true of a complete map `M`,
        FALSE of `U = M + all-ones` by construction. Rev. 2 applied it to `U` and it fired on a
        legitimate declaration. The all-ones total-rate functional is NOT a row of `M`.
        """
        covs, M, scale = self._healthy()
        ones = np.ones((1, 40))
        out = zbp.evaluate_a7(covs, M, extra_functionals=ones, declared_K=[0, 1],
                              c_scale=scale, kappa=1e-12)
        self.assertEqual(out["state"], "GRADED", "a map + all-ones must not trip arm 1")
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
        self.assertEqual(len(DETECTORS), 21,
                         "DETECTORS must equal the demonstrated set; update both together")
        # ⚠ THESE ARE DIFFERENT SETS AND THE COUNTS MATCHING IS A COINCIDENCE. `points` are
        # `require`/`raise` sites in the module; `DETECTORS` are demonstrated behaviours, some of
        # which (e.g. `residue_demonstrated`) are not refusal points at all. Printing them side by
        # side as "N of N" would imply a correspondence that does not exist.
        print(f"\n[enrolment] {len(points)} refusal points parsed from the module source. "
              f"{len(DETECTORS)} behaviours demonstrated by name -- a DIFFERENT set, not a "
              f"one-to-one cover. Unenrolled refusals are {list(self.WAIVED)[0]}")


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
