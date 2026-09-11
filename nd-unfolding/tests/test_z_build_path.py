#!/usr/bin/env python3
"""Local synthetic tests for Z's decoupled build path. No cluster, no products, no adoption.

THE SHAPE JOSEPH ASKED FOR: *"the complete path can both pass valid controls and reject relevant
mutations."* Both arms. So every detector below has a NEGATIVE control (clean input -> silent) and a
POSITIVE control (mutated input -> fires), and the suite ends with a POWER TEST that **RAISES** if
any detector was not shown to fire -- the `audit_gates_that_cannot_fail.py:592-593` idiom, because a
detector never demonstrated to fire is untested, not working.
"""
import os
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

#: every detector that must be SHOWN to fire. The power test at the end asserts this is empty.
FIRED = set()
DETECTORS = {
    "population_too_small", "population_duplicate", "population_no_baseline",
    "population_baseline_only", "block_source_undefaulted", "shared_needs_digests",
    "arm1_source_orphan", "arm2_destination_orphan", "kappa_undeclared_refuses",
    "degenerate_structural", "degenerate_by_kappa", "support_changed",
    "receipt_no_seeds", "receipt_digest_mismatch", "receipt_no_revision",
    "preservation_refuses_overwrite",
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
