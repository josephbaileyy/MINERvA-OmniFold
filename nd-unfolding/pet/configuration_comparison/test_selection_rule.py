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

import selection_rule as sr
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
        # The regional gate is a third dimension of the partition, so the sweep
        # covers it: absent, passing, and failing. Leaving it out would let the
        # totality claim be true only of a slice of the input space.
        passing = sr.regional_safeguard(
            {"ours": {"poor": 0.9}, "theirs": {"poor": 0.9}},
            floor=0.5, scoreable_regions=["poor"])
        failing = sr.regional_safeguard(
            {"ours": {"poor": 0.1}, "theirs": {"poor": 0.9}},
            floor=0.5, scoreable_regions=["poor"])
        gates = [None, passing, failing]

        seen = set()
        count = 0
        for gate in gates:
            for ours, theirs in product([True, False], repeat=2):
                for low, high in product(edges, repeat=2):
                    if low > high:
                        continue
                    outcome = decide(ours_adequate=ours, theirs_adequate=theirs,
                                     ci_low=low, ci_high=high, delta=DELTA,
                                     delta_switch=SWITCH, regional=gate)
                    self.assertIsInstance(outcome.verdict, Verdict)
                    self.assertIsInstance(outcome.recommendation, Recommendation)
                    seen.add(outcome.verdict)
                    count += 1
        # 14 edges give 14*15/2 = 105 ordered pairs, times 4 adequacy combinations,
        # times 3 gate states. Asserting the exact count makes a silently-skipped
        # branch visible.
        self.assertEqual(count, 3 * 4 * len(edges) * (len(edges) + 1) // 2)
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


class Soundness(unittest.TestCase):
    """Properties every verdict must satisfy, checked over a grid rather than asserted.

    These are the tests that catch the class of defect this module actually had: a
    verdict claiming a magnitude the interval does not support.
    """

    GRID = [-0.30, -0.10, -0.05, -SWITCH - 1e-9, -SWITCH, -SWITCH + 1e-9, -0.018,
            -DELTA, -DELTA + 1e-9, -0.010, -1e-9, 0.0, 1e-9, 0.010, DELTA, SWITCH,
            SWITCH + 1e-9, 0.10]

    def intervals(self):
        for low in self.GRID:
            for high in self.GRID:
                if low <= high:
                    yield low, high

    def test_below_threshold_is_claimed_only_when_the_interval_is_inside_it(self):
        """THE COUNTEREXAMPLE'S CLASS: ci_high < 0 alone must never license this verdict."""
        for low, high in self.intervals():
            outcome = call(True, True, low, high)
            if outcome.verdict is Verdict.THEIRS_BETTER_BELOW_SWITCHING_THRESHOLD:
                self.assertGreater(low, -SWITCH, f"[{low}, {high}] does not bound the advantage")
                self.assertLess(high, 0.0, f"[{low}, {high}] does not establish an advantage")

    def test_theirs_superior_is_claimed_only_when_the_advantage_exceeds_the_threshold(self):
        for low, high in self.intervals():
            outcome = call(True, True, low, high)
            if outcome.verdict is Verdict.THEIRS_SUPERIOR:
                self.assertLess(high, -SWITCH, f"[{low}, {high}] does not exceed the threshold")

    def test_non_inferiority_is_claimed_only_when_the_deficit_is_bounded_by_delta(self):
        for low, high in self.intervals():
            outcome = call(True, True, low, high)
            if outcome.verdict is Verdict.OURS_NON_INFERIOR:
                self.assertGreater(low, -DELTA, f"[{low}, {high}] admits a deficit >= delta")

    def test_ours_is_never_adopted_when_his_advantage_provably_exceeds_the_threshold(self):
        """The scientific implication: a policy must not override a demonstrated margin."""
        for low, high in self.intervals():
            outcome = call(True, True, low, high)
            if high < -SWITCH:
                self.assertNotEqual(outcome.recommendation, Recommendation.ADOPT_OURS,
                                    f"[{low}, {high}] provably exceeds the threshold")

    def test_more_uncertainty_never_yields_a_stronger_claim(self):
        """Widening an interval about its midpoint must not strengthen the verdict.

        A rule that got stronger with more uncertainty would reward noisy measurements.
        """
        strong = {Verdict.OURS_SUPERIOR, Verdict.THEIRS_SUPERIOR,
                  Verdict.THEIRS_BETTER_BELOW_SWITCHING_THRESHOLD}
        for centre in (-0.06, -0.03, -0.01, 0.0, 0.01, 0.03):
            for half in (0.001, 0.005, 0.02, 0.05, 0.12):
                narrow = call(True, True, centre - 0.001, centre + 0.001)
                wide = call(True, True, centre - half, centre + half)
                if wide.verdict in strong:
                    self.assertIn(narrow.verdict, strong,
                                  f"widening at centre {centre} strengthened the verdict")

    def test_shifting_the_interval_toward_his_arm_never_favours_ours_more(self):
        """Monotonicity in the physical direction of the difference."""
        rank = {Recommendation.ADOPT_THEIRS: 0, Recommendation.NO_SELECTION: 1,
                Recommendation.ADOPT_OURS: 2}
        for low, high in [(-0.01, 0.05), (0.0, 0.04), (-0.005, 0.01)]:
            previous = 2
            for shift in (0.0, 0.01, 0.02, 0.04, 0.06, 0.08, 0.10, 0.15):
                got = rank[call(True, True, low - shift, high - shift).recommendation]
                self.assertLessEqual(got, previous,
                                     f"shifting [{low}, {high}] by {shift} favoured ours more")
                previous = got


class Boundaries(unittest.TestCase):
    """Which side of each breakpoint the rule falls on, fixed by test rather than by luck."""

    def test_the_reported_counterexample(self):
        """CI = [-0.10, -0.01] must NOT establish the advantage is below the threshold."""
        outcome = call(True, True, -0.10, -0.01)
        self.assertEqual(outcome.verdict, Verdict.THEIRS_BETTER_MAGNITUDE_UNRESOLVED)
        self.assertEqual(outcome.recommendation, Recommendation.NO_SELECTION)
        self.assertEqual(outcome.measured["favours"], "theirs")
        self.assertTrue(outcome.measured["difference_resolved"])
        self.assertIn("UNRESOLVED", " ".join(outcome.notes))
        # It is not a policy decision either: nothing was retained on a threshold
        # argument the data does not support.
        self.assertIsNone(outcome.preference)

    def test_ci_low_exactly_at_minus_delta_is_not_non_inferior(self):
        """Touching the margin does not clear it: the rule is strict, deliberately."""
        outcome = call(True, True, -DELTA, 0.05)
        self.assertNotEqual(outcome.verdict, Verdict.OURS_NON_INFERIOR)
        self.assertEqual(outcome.verdict, Verdict.INCONCLUSIVE)

    def test_ci_low_just_inside_minus_delta_is_non_inferior(self):
        outcome = call(True, True, -DELTA + 1e-9, 0.05)
        self.assertEqual(outcome.verdict, Verdict.OURS_NON_INFERIOR)

    def test_ci_high_exactly_zero_does_not_establish_his_advantage(self):
        outcome = call(True, True, -0.05, 0.0)
        self.assertEqual(outcome.verdict, Verdict.INCONCLUSIVE)
        self.assertFalse(outcome.measured["difference_resolved"])

    def test_ci_low_exactly_at_minus_switch_leaves_the_magnitude_unresolved(self):
        outcome = call(True, True, -SWITCH, -0.001)
        self.assertEqual(outcome.verdict, Verdict.THEIRS_BETTER_MAGNITUDE_UNRESOLVED)

    def test_ci_low_just_inside_minus_switch_bounds_the_advantage(self):
        outcome = call(True, True, -SWITCH + 1e-9, -0.001)
        self.assertEqual(outcome.verdict, Verdict.THEIRS_BETTER_BELOW_SWITCHING_THRESHOLD)

    def test_ci_high_exactly_at_minus_switch_is_not_superiority(self):
        outcome = call(True, True, -0.10, -SWITCH)
        self.assertEqual(outcome.verdict, Verdict.THEIRS_BETTER_MAGNITUDE_UNRESOLVED)

    def test_a_degenerate_interval_is_handled(self):
        """Zero width: the rule must still return one verdict."""
        for point in (-0.10, -SWITCH, -DELTA, 0.0, DELTA, SWITCH, 0.10):
            outcome = call(True, True, point, point)
            self.assertIsInstance(outcome.verdict, Verdict)


if __name__ == "__main__":
    unittest.main()


class RegionalSafeguard(unittest.TestCase):
    """The gate that a marginal cannot see, and what failing it costs."""

    SCOREABLE = ["poor", "moderate", "good"]
    PASSING = {"poor": 0.62, "moderate": 0.70, "good": 0.81}

    def _gate(self, ours=None, theirs=None, floor=0.5):
        return sr.regional_safeguard(
            {"ours": dict(self.PASSING if ours is None else ours),
             "theirs": dict(self.PASSING if theirs is None else theirs)},
            floor=floor, scoreable_regions=self.SCOREABLE)

    def test_both_passing_does_not_block(self):
        gate = self._gate()
        self.assertTrue(gate["arms"]["ours"]["eligible"])
        self.assertTrue(gate["arms"]["theirs"]["eligible"])
        outcome = sr.decide(ours_adequate=True, theirs_adequate=True, ci_low=0.01,
                            ci_high=0.05, delta=0.017, delta_switch=0.02, regional=gate)
        self.assertNotEqual(outcome.verdict, sr.Verdict.REGIONAL_SAFEGUARD_FAILED)

    def test_a_regional_failure_blocks_even_a_superior_arm(self):
        """The point of the safeguard: winning the aggregate does not license it."""
        failing = {**self.PASSING, "poor": 0.10}
        outcome = sr.decide(ours_adequate=True, theirs_adequate=True, ci_low=0.20,
                            ci_high=0.30, delta=0.017, delta_switch=0.02,
                            regional=self._gate(ours=failing))
        self.assertEqual(outcome.verdict, sr.Verdict.REGIONAL_SAFEGUARD_FAILED)
        self.assertEqual(outcome.recommendation, sr.Recommendation.NO_SELECTION)

    def test_one_arm_failing_does_not_select_the_other(self):
        """Their failure is not our evidence; the consequence is NO_SELECTION."""
        outcome = sr.decide(ours_adequate=True, theirs_adequate=True, ci_low=-0.30,
                            ci_high=-0.20, delta=0.017, delta_switch=0.02,
                            regional=self._gate(theirs={**self.PASSING, "poor": 0.05}))
        self.assertEqual(outcome.recommendation, sr.Recommendation.NO_SELECTION)
        self.assertIn("theirs FAILED", outcome.notes)

    def test_an_unreported_region_counts_as_failed(self):
        gate = self._gate(ours={"poor": 0.62, "good": 0.81})
        self.assertFalse(gate["arms"]["ours"]["eligible"])
        self.assertEqual(gate["arms"]["ours"]["regions_not_reported"], ["moderate"])

    def test_the_floor_is_applied_to_every_scoreable_region(self):
        for region in self.SCOREABLE:
            with self.subTest(region=region):
                gate = self._gate(ours={**self.PASSING, region: 0.01})
                self.assertFalse(gate["arms"]["ours"]["eligible"])
                self.assertEqual(gate["arms"]["ours"]["regions_below_floor"], [region])

    def test_exactly_at_the_floor_passes(self):
        gate = self._gate(ours={**self.PASSING, "poor": 0.5}, floor=0.5)
        self.assertTrue(gate["arms"]["ours"]["eligible"])

    def test_a_region_outside_the_scoreable_set_cannot_block(self):
        """Exempt regions are reported, not enforced; the exemption is auditable."""
        gate = sr.regional_safeguard(
            {"ours": {**self.PASSING, "unresolvable": 0.0},
             "theirs": {**self.PASSING, "unresolvable": 0.0}},
            floor=0.5, scoreable_regions=self.SCOREABLE)
        self.assertTrue(gate["arms"]["ours"]["eligible"])

    def test_no_scoreable_region_at_all_is_refused(self):
        with self.assertRaises(ValueError):
            sr.regional_safeguard({"ours": {}, "theirs": {}}, floor=0.5,
                                  scoreable_regions=[])

    def test_omitting_the_gate_leaves_the_rule_unchanged(self):
        """Backward compatibility: `regional=None` must not alter any verdict."""
        without = sr.decide(ours_adequate=True, theirs_adequate=True, ci_low=0.01,
                            ci_high=0.05, delta=0.017, delta_switch=0.02)
        with_passing = sr.decide(ours_adequate=True, theirs_adequate=True, ci_low=0.01,
                                 ci_high=0.05, delta=0.017, delta_switch=0.02,
                                 regional=self._gate())
        self.assertEqual(without.verdict, with_passing.verdict)
        self.assertEqual(without.recommendation, with_passing.recommendation)
