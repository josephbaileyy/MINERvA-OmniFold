"""Tests for the selection rule: the partition must be total and unambiguous.

The rule's value is that every input maps to exactly one verdict, so these tests
enumerate the partition instead of sampling it: a grid over adequacy and over interval
positions spanning every breakpoint, asserting that a verdict is always produced and
that the intended verdict is the one produced.

The tests that matter most are the ones about *separation*: that a case where Gregor's
arm measurably wins still reports that it won, and that a recommendation reached by
policy is flagged as such.
"""

from __future__ import annotations

from itertools import product
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from selection_rule import Recommendation, Verdict, decide, describe

DELTA = 0.017
SWITCH = 0.02


def call(ours: bool, theirs: bool, low: float, high: float):
    return decide(
        ours_adequate=ours, theirs_adequate=theirs,
        ci_low=low, ci_high=high, delta=DELTA, delta_switch=SWITCH,
    )


class Totality(unittest.TestCase):
    def test_every_input_yields_exactly_one_known_verdict(self):
        """No combination of adequacy and interval position is unhandled."""
        edges = [-0.10, -SWITCH - 1e-6, -SWITCH, -SWITCH + 1e-6, -0.018,
                 -DELTA, -DELTA + 1e-6, -0.001, 0.0, 0.001, DELTA, SWITCH,
                 SWITCH + 1e-6, 0.10]
        seen = set()
        count = 0
        for ours, theirs in product([True, False], repeat=2):
            for low, high in product(edges, repeat=2):
                if low > high:
                    continue
                outcome = call(ours, theirs, low, high)
                self.assertIsInstance(outcome.verdict, Verdict)
                self.assertIsInstance(outcome.recommendation, Recommendation)
                seen.add(outcome.verdict)
                count += 1
        # 14 edges give 14*15/2 = 105 ordered pairs, times 4 adequacy combinations.
        # Asserting the exact count makes a silently-skipped branch visible.
        self.assertEqual(count, 4 * len(edges) * (len(edges) + 1) // 2)
        # Every verdict in the enum is reachable; an unreachable branch is dead code
        # masquerading as coverage.
        self.assertEqual(seen, set(Verdict))

    def test_inverted_interval_is_refused(self):
        with self.assertRaises(ValueError):
            call(True, True, 0.05, -0.05)

    def test_switch_must_exceed_delta(self):
        """A switching threshold inside the non-inferiority margin makes the rule ambiguous."""
        with self.assertRaises(ValueError):
            decide(ours_adequate=True, theirs_adequate=True, ci_low=0.0, ci_high=0.0,
                   delta=0.02, delta_switch=0.02)

    def test_delta_must_be_positive(self):
        with self.assertRaises(ValueError):
            decide(ours_adequate=True, theirs_adequate=True, ci_low=0.0, ci_high=0.0,
                   delta=0.0, delta_switch=0.02)


class Adequacy(unittest.TestCase):
    def test_neither_adequate_is_no_selection_however_good_the_interval(self):
        outcome = call(False, False, 0.5, 0.6)
        self.assertEqual(outcome.verdict, Verdict.NEITHER_ADEQUATE)
        self.assertEqual(outcome.recommendation, Recommendation.NO_SELECTION)

    def test_only_ours_adequate_adopts_ours_but_not_on_the_comparison(self):
        """Even when the interval favours his arm strongly."""
        outcome = call(True, False, -0.5, -0.4)
        self.assertEqual(outcome.verdict, Verdict.ONLY_OURS_ADEQUATE)
        self.assertEqual(outcome.recommendation, Recommendation.ADOPT_OURS)
        self.assertEqual(outcome.measured["favours"], "theirs")
        self.assertIn("NOT by the comparison", " ".join(outcome.notes))

    def test_only_theirs_adequate_adopts_theirs_even_if_ours_scored_higher(self):
        """Switching costs protect an adequate incumbent, not an inadequate one."""
        outcome = call(False, True, 0.4, 0.5)
        self.assertEqual(outcome.verdict, Verdict.ONLY_THEIRS_ADEQUATE)
        self.assertEqual(outcome.recommendation, Recommendation.ADOPT_THEIRS)
        self.assertEqual(outcome.measured["favours"], "ours")
        self.assertIsNone(outcome.preference)


class BothAdequate(unittest.TestCase):
    def test_ours_superior(self):
        outcome = call(True, True, SWITCH + 0.001, 0.1)
        self.assertEqual(outcome.verdict, Verdict.OURS_SUPERIOR)
        self.assertTrue(outcome.decided_by_measurement)

    def test_ours_non_inferior(self):
        outcome = call(True, True, -DELTA + 0.001, 0.03)
        self.assertEqual(outcome.verdict, Verdict.OURS_NON_INFERIOR)
        self.assertEqual(outcome.recommendation, Recommendation.ADOPT_OURS)
        self.assertTrue(outcome.decided_by_measurement)

    def test_non_inferior_can_still_measure_theirs_ahead(self):
        """Non-inferiority is not superiority, and the report must not conflate them."""
        outcome = call(True, True, -0.016, -0.002)
        self.assertEqual(outcome.verdict, Verdict.OURS_NON_INFERIOR)
        self.assertEqual(outcome.measured["favours"], "theirs")
        self.assertTrue(outcome.measured["difference_resolved"])
        self.assertIn("non-inferiority is not superiority", " ".join(outcome.notes))

    def test_theirs_superior(self):
        outcome = call(True, True, -0.09, -SWITCH - 0.001)
        self.assertEqual(outcome.verdict, Verdict.THEIRS_SUPERIOR)
        self.assertEqual(outcome.recommendation, Recommendation.ADOPT_THEIRS)
        self.assertTrue(outcome.decided_by_measurement)

    def test_theirs_better_below_switch_keeps_ours_by_policy(self):
        outcome = call(True, True, -0.019, -0.003)
        self.assertEqual(outcome.verdict, Verdict.THEIRS_BETTER_BELOW_SWITCHING_THRESHOLD)
        self.assertEqual(outcome.recommendation, Recommendation.ADOPT_OURS)
        self.assertEqual(outcome.measured["favours"], "theirs")
        self.assertTrue(outcome.measured["difference_resolved"])
        self.assertFalse(outcome.decided_by_measurement)
        self.assertFalse(outcome.preference_is_ratified)
        self.assertIn("MEASURABLY WON", " ".join(outcome.notes))
        self.assertIn("Never as 'no", " ".join(outcome.notes))

    def test_inconclusive(self):
        outcome = call(True, True, -0.05, 0.05)
        self.assertEqual(outcome.verdict, Verdict.INCONCLUSIVE)
        self.assertEqual(outcome.recommendation, Recommendation.NO_SELECTION)
        self.assertFalse(outcome.decided_by_measurement)
        self.assertFalse(outcome.measured["difference_resolved"])


class Separation(unittest.TestCase):
    def test_no_verdict_reports_an_unresolved_difference_as_favouring_anyone(self):
        for low, high in [(-0.05, 0.05), (-0.001, 0.2), (-0.3, 0.0)]:
            outcome = call(True, True, low, high)
            self.assertEqual(outcome.measured["favours"], "unresolved", (low, high))

    def test_every_policy_decision_is_unratified_and_named(self):
        """A recommendation not licensed by measurement must say which policy decided it."""
        for low, high in [(-0.019, -0.003), (-0.05, 0.05)]:
            outcome = call(True, True, low, high)
            self.assertIsNotNone(outcome.preference)
            self.assertFalse(outcome.preference_is_ratified)
            self.assertIn("UNRATIFIED", describe(outcome))

    def test_measurement_backed_recommendations_claim_no_policy(self):
        for low, high in [(SWITCH + 0.01, 0.1), (-0.09, -SWITCH - 0.01),
                          (-DELTA + 0.001, 0.02)]:
            outcome = call(True, True, low, high)
            self.assertIsNone(outcome.preference)
            self.assertIn("licensed by the measurement", describe(outcome))


if __name__ == "__main__":
    unittest.main()
