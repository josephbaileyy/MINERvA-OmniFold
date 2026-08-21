#!/usr/bin/env python3
"""OI-141 (the verdict must not depend on prose) and OI-140 (identity is RECOMPUTED, not declared).

Both items were filed after a measured fail-open: the gate's verdict was rebuilt by parsing the
`"UNCOMPARABLE "` prefix out of another module's message text, and a symmetric full-suite mutation
of that literal was caught by ZERO of ~1992 tests -- 5 failed / 1987 passed in both arms with the
failure sets identical by name. These are the tests that make it not happen again.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import mii_anchor_comparator as C          # noqa: E402
import mii_root_payload_classes as K       # noqa: E402

ADOPTED = "adopted_uthrow.root"
G1, G2 = "upstream_estimator_seed_g1_checked", "upstream_estimator_seed_g2_checked"
OLD_PREFIX = "UNCOMPARABLE "


def _old_parse(findings):
    """EXACTLY the deleted consumer, kept so a test can prove the new path does not depend on it."""
    return [l.split(":", 1)[0].replace(OLD_PREFIX, "").strip()
            for l in findings if l.startswith(OLD_PREFIX)]


class OI141_TheVerdictIsStructuredNotParsed(unittest.TestCase):
    """The uncomparable-key list must come from data, not from a message prefix."""

    def setUp(self):
        # member carries the two _checked keys; a 2026-07-14 archive cannot.
        self.member = {G1: 1, G2: 1}
        self.result = K.compare(ADOPTED, {}, self.member)

    def test_compare_still_unpacks_as_a_two_tuple(self):
        """Every existing `verdict, findings = compare(...)` call site must keep working."""
        self.assertEqual(len(self.result), 2)
        verdict, findings = self.result
        self.assertIn(verdict, ("PASS", "INCOMPLETE", "FAIL"))
        self.assertIsInstance(findings, list)

    def test_compare_exposes_the_uncomparable_keys_STRUCTURALLY(self):
        self.assertEqual(set(self.result.uncomparable), {G1, G2},
                         "the caller must be able to get these without reading prose")

    def test_REWORDING_THE_DIAGNOSTIC_CANNOT_CHANGE_THE_VERDICT(self):
        """THE REGRESSION. This is the mutation that survived, expressed as an assertion.

        The old consumer is applied to REWORDED findings and yields nothing, which is exactly how
        the gate used to fail open. The structured field is unaffected, and the audit built on it
        reaches the same verdict either way.
        """
        reworded = [f"[b2] {l}" for l in self.result[1]]
        self.assertEqual(_old_parse(reworded), [],
                         "sanity: the OLD parse is defeated by a one-token reword -- that was the bug")
        self.assertEqual(set(self.result.uncomparable), {G1, G2},
                         "the STRUCTURED list must be untouched by any rewording of the messages")
        # and the branch that decides the verdict agrees on both
        self.assertEqual(C.audit_uncomparable(ADOPTED, _old_parse(self.result[1])),
                         C.audit_uncomparable(ADOPTED, list(self.result.uncomparable)))

    def test_the_audit_is_not_dead_a_key_with_no_coverage_still_FAILS(self):
        """Negative control. If everything were skipped the audit would be vacuously green."""
        # `n_throws_checked` on this artifact is CONFIGURATION, derive:None, has no
        # RECOMPUTABILITY row and is not declared -- so it lands squarely in the failing branch.
        # (globalCompleteness was the first choice and is UNCLASSIFIED here, which exits 2 rather
        # than reaching the branch: a control has to be able to arrive at what it is controlling.)
        uncovered = "n_throws_checked"
        self.assertNotIn(uncovered, C.declared_unverified())
        self.assertIsNot(C.RECOMPUTABILITY.get(uncovered, (None,))[0], C.IN_FILE)
        self.assertIsNot(K.classify(ADOPTED, uncovered), K.PROVENANCE)
        _, failed = C.audit_uncomparable(ADOPTED, [uncovered])
        self.assertTrue(failed, "a key that is neither PROVENANCE, IN_FILE nor declared must FAIL")


class OI140_IdentityIsRecomputedNotDeclared(unittest.TestCase):
    """The two `_checked` keys are IN_FILE because something checks them."""

    BASE = {"g1": 42, "g2": 1000}

    def _sc(self, **over):
        sc = {"est_seed_offset_declared": 1, "est_seed_offset": 1200,
              "upstream_estimator_seed_g1": 1242, G1: 1,
              "upstream_estimator_seed_g2": 2200, G2: 1}
        sc.update(over)
        return sc

    def test_the_two_checked_keys_are_NOT_in_DECLARED_UNVERIFIED(self):
        """The route taken was verification, not declaration. If someone swaps it, say so loudly."""
        for k in (G1, G2):
            self.assertNotIn(k, C.declared_unverified(),
                             f"{k} was moved to DECLARED_UNVERIFIED -- that greens the gate while "
                             "leaving remedy (A)'s central identity claim unchecked (OI-140)")
            self.assertIs(C.RECOMPUTABILITY[k][0], C.IN_FILE)

    def test_the_IN_FILE_CLAIM_IS_NOT_A_LIE(self):
        """An IN_FILE row asserts a recomputation exists. Prove it by making it FAIL."""
        for k, seed_key in ((G1, "upstream_estimator_seed_g1"), (G2, "upstream_estimator_seed_g2")):
            with self.subTest(key=k):
                _, failed = C.verify_leg_identity(ADOPTED, self._sc(**{seed_key: 999999}),
                                                  baselines=self.BASE)
                self.assertTrue(failed, f"{k} claims IN_FILE coverage but nothing rejected a wrong seed")

    def test_baselines_come_from_the_policy_table(self):
        self.assertEqual(C.leg_baselines(), self.BASE,
                         "baselines must be derived from seed_offset_policy.LEG_BASELINES")

    def test_the_intended_declared_path_PASSES(self):
        """A filter needs a test in the direction it does NOT act."""
        lines, failed = C.verify_leg_identity(ADOPTED, self._sc(), baselines=self.BASE)
        self.assertFalse(failed, lines)
        self.assertTrue(all("OK" in l for l in lines), lines)

    def test_a_leg_that_ran_UNHOOKED_is_caught(self):
        """Seed == its own baseline while a non-zero offset is declared: provably wrong."""
        _, failed = C.verify_leg_identity(
            ADOPTED, self._sc(upstream_estimator_seed_g1=42), baselines=self.BASE)
        self.assertTrue(failed)

    def test_a_flag_contradicting_its_own_seed_is_caught(self):
        _, failed = C.verify_leg_identity(ADOPTED, self._sc(**{G1: 0}), baselines=self.BASE)
        self.assertTrue(failed)

    def test_a_DECLARED_member_with_a_missing_seed_is_caught(self):
        sc = self._sc(**{G2: 0})
        del sc["upstream_estimator_seed_g2"]
        _, failed = C.verify_leg_identity(ADOPTED, sc, baselines=self.BASE)
        self.assertTrue(failed, "_checked = 0 is ABSENCE, not a pass")

    def test_an_UNDECLARED_member_is_UNVERIFIABLE_and_fails(self):
        """Today's products. Self-consistent, and identity still not established."""
        lines, failed = C.verify_leg_identity(
            ADOPTED, {"est_seed_offset_declared": 0, "est_seed_offset": 0, G1: 0, G2: 0},
            baselines=self.BASE)
        self.assertTrue(failed)
        self.assertTrue(any("UNVERIFIABLE" in l for l in lines), lines)

    def test_an_artifact_without_the_keys_is_silent(self):
        """Must not fire on the five artifacts that never carry these keys."""
        self.assertEqual(C.verify_leg_identity(ADOPTED, {"n_throws": 160}), ([], False))


class OI149_ALegsOwnDeclarationIsCompared(unittest.TestCase):
    """OI-149. A declared adopter may not stamp over legs that say they were unhooked.

    Measured end-to-end on the real archive before this fix: a product built from two genuinely
    unhooked legs was ADMITTED, both legs reporting `[identity] OK`, because the legs' own
    `est_seed_offset_declared` was read into LEG_IDENTITY_KEYS and then consulted by nothing while
    the product's flag came from the adopting process's environment.

    WHY THE OFFSET CHECKS CANNOT SUBSTITUTE, and it is arithmetic: at k=0 the cross-leg test
    `int(o1) != int(o2)` and the per-leg test `int(o) != int(off_value)` are both `0 != 0`. Two legs
    that were never hooked -- each stamping its own baseline offset of 0 -- are numerically identical
    to a deliberate zero anchor at every site that looked. k=0 is also the ONLY member stage 1 is
    declared to gate, so the invariant had power everywhere except where it was needed.
    """

    W = None

    @classmethod
    def setUpClass(cls):
        import importlib
        cls.W = importlib.import_module("mii_adopt_unified_5d_stamped")

    def _legs(self, g1_decl, g2_decl, off=0):
        mk = lambda d: ({"est_seed_offset": off} if d is None
                        else {"est_seed_offset_declared": d, "est_seed_offset": off})
        return mk(g1_decl), mk(g2_decl)

    def _run(self, g1_decl, g2_decl, off_declared, off=0):
        g1, g2 = self._legs(g1_decl, g2_decl, off)
        return self.W.assert_legs_are_one_member(g1, g2, off_declared, off)

    def test_THE_k0_LAUNDERING_CASE_IS_REFUSED(self):
        """The measured admission, turned into an assertion."""
        with self.assertRaises(BaseException):
            self._run(0, 0, 1)

    def test_a_single_undeclared_leg_is_refused(self):
        with self.assertRaises(BaseException):
            self._run(1, 0, 1)
        with self.assertRaises(BaseException):
            self._run(0, 1, 1)

    def test_a_leg_carrying_NO_flag_is_NOT_refused_HERE(self):
        """Deliberately narrower than the gate, and the reason is a modelled legacy case.

        A leg with no flag predates the stamp, which this function's own tests model on purpose
        (an empty dict for a combined leg). Refusing it here would be stricter than the ruling and
        would break that case. The GATE covers it instead: `verify_leg_identity` reports a declared
        member with absent identity keys as UNVERIFIABLE and fails it.
        """
        self.assertTrue(self._run(None, 1, 1))

    def test_the_LEGITIMATE_k0_MEMBER_STILL_PASSES(self):
        """A filter needs a test in the direction it does NOT act, and k=0 is the whole point."""
        self.assertTrue(self._run(1, 1, 1, off=0))

    def test_a_legitimate_nonzero_offset_still_passes(self):
        self.assertTrue(self._run(1, 1, 1, off=1200))

    def test_an_UNDECLARED_adopter_over_undeclared_legs_is_not_refused_here(self):
        """Nothing is declared, so nothing can be concluded at this site. `verify_leg_identity`
        is what reports that member UNVERIFIABLE -- this function must not double-refuse it."""
        self.assertTrue(self._run(0, 0, 0))


if __name__ == "__main__":
    unittest.main()
