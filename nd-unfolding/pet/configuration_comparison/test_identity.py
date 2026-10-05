"""Tests for the configuration registry: names mean one thing each."""

from __future__ import annotations

import unittest

import configuration_identity as ci


class Identity(unittest.TestCase):
    def setUp(self):
        self._saved = dict(ci.REGISTRY)

    def tearDown(self):
        ci.REGISTRY.clear()
        ci.REGISTRY.update(self._saved)

    def test_the_complete_arm_satisfies_his_identity(self):
        self.assertEqual(ci.identity_gaps(ci.THEIRS_COMPLETE), [])
        ci.require_his_complete_arm(ci.THEIRS_COMPLETE)

    def test_the_degraded_arm_cannot_be_called_his_configuration(self):
        gaps = ci.identity_gaps(ci.THEIRS_DEGRADED)
        self.assertIn("pid_channel absent", gaps)
        self.assertIn("auxiliary_channel absent", gaps)
        self.assertIn("event globals absent", gaps)
        self.assertIn("token cap 12 != 33", gaps)
        with self.assertRaises(ValueError) as caught:
            ci.require_his_complete_arm(ci.THEIRS_DEGRADED)
        self.assertIn("not Gregor's complete arm", str(caught.exception))

    def test_each_identity_requirement_is_enforced_on_its_own(self):
        """A configuration missing exactly one piece is still not his arm."""
        for field, value in (("pid_channel", False), ("auxiliary_channel", False),
                             ("globals", None), ("token_cap", 12)):
            with self.subTest(field=field):
                broken = ci.Configuration(
                    name="probe", owner="us", status="probe",
                    architecture={}, inputs={**ci.THEIRS_COMPLETE.inputs, field: value},
                    recipe={}, provenance="test")
                self.assertTrue(ci.identity_gaps(broken))
                with self.assertRaises(ValueError):
                    ci.require_his_complete_arm(broken)

    def test_the_complete_arm_is_blocked_and_says_so(self):
        self.assertFalse(ci.THEIRS_COMPLETE.runnable_today)
        self.assertTrue(any("R2" in b for b in ci.THEIRS_COMPLETE.blockers))

    def test_the_degraded_arm_is_runnable_and_labelled(self):
        self.assertTrue(ci.THEIRS_DEGRADED.runnable_today)
        self.assertEqual(ci.THEIRS_DEGRADED.status, "DEGRADED_NOT_HIS_CONFIGURATION")
        self.assertIsNotNone(ci.THEIRS_DEGRADED.rationale)

    def test_exactly_one_incumbent(self):
        self.assertEqual(ci.incumbent().name, "ours_incumbent")
        self.assertEqual(ci.incumbent().status, "PROMOTED_INCUMBENT")

    def test_a_candidate_is_not_the_incumbent(self):
        candidate = ci.declare_candidate(
            "ours_cap33", {"inputs": {"token_cap": 33}},
            rationale="matching his cap removes a confound")
        self.assertEqual(candidate.status, "CANDIDATE_NOT_PROMOTED")
        self.assertEqual(candidate.parent, "ours_incumbent")
        self.assertEqual(ci.incumbent().name, "ours_incumbent")
        self.assertEqual(ci.incumbent().inputs["token_cap"], 12)

    def test_a_candidate_needs_a_rationale(self):
        with self.assertRaises(ValueError):
            ci.declare_candidate("ours_x", {"inputs": {"token_cap": 33}}, rationale="  ")

    def test_a_candidate_that_changes_nothing_is_refused(self):
        with self.assertRaises(ValueError):
            ci.declare_candidate("ours_y", {}, rationale="no change")

    def test_a_duplicate_name_is_refused(self):
        with self.assertRaises(ValueError):
            ci.declare_candidate("ours_incumbent", {"inputs": {"token_cap": 33}},
                                 rationale="clash")

    def test_the_incumbent_is_the_promoted_production_estimator(self):
        incumbent = ci.incumbent()
        self.assertEqual(incumbent.architecture["num_heads"], 2)
        self.assertEqual(incumbent.architecture["K"], 3)
        self.assertEqual(incumbent.inputs["token_cap"], 12)
        self.assertEqual(incumbent.recipe["batch_size"], 512)


if __name__ == "__main__":
    unittest.main(verbosity=1)
