"""Tests for the scoring pass.

The special functions are checked against PUBLISHED TABLES, not against a second
implementation of mine. The first version of `_t_quantile` agreed with itself
perfectly and was off by a factor of two at one degree of freedom; only an
outside number caught it.
"""
from __future__ import annotations

import json
import math
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np

import frozen_design as fd
import score_campaign as sc
import selection_rule as sr


# Two-sided 0.975 Student-t quantiles, from a standard table.
T_TABLE = {1: 12.7062, 2: 4.30265, 3: 3.18245, 5: 2.57058, 7: 2.36462,
           10: 2.22814, 15: 2.13145, 30: 2.04227, 100: 1.98397}
# Chi-square lower-tail quantiles, from a standard table.
CHI2_TABLE = {(1, 0.20): 0.0642, (3, 0.20): 1.0052, (7, 0.20): 3.8223,
              (10, 0.05): 3.9403, (5, 0.95): 11.0705}


class TestSpecialFunctions(unittest.TestCase):
    def test_t_quantiles_match_the_published_table(self):
        for df, ref in T_TABLE.items():
            self.assertAlmostEqual(sc._t_quantile(0.975, df), ref, places=4,
                                   msg=f"df={df}")

    def test_chi2_quantiles_match_the_published_table(self):
        for (df, p), ref in CHI2_TABLE.items():
            self.assertAlmostEqual(sc._chi2_quantile(p, df), ref, places=3,
                                   msg=f"df={df} p={p}")

    def test_incomplete_beta_matches_its_closed_form_at_a_b_half(self):
        for x in (0.01, 0.1, 0.37, 0.5, 0.9, 0.999):
            self.assertAlmostEqual(sc._betainc_half(0.5, x),
                                   2.0 / math.pi * math.asin(math.sqrt(x)),
                                   places=12, msg=f"x={x}")

    def test_t_quantile_grows_as_degrees_of_freedom_fall(self):
        values = [sc._t_quantile(0.975, df) for df in (1, 2, 5, 10, 50, 200)]
        self.assertEqual(values, sorted(values, reverse=True))
        self.assertAlmostEqual(values[-1], 1.9719, places=3)  # -> normal 1.96


# --------------------------------------------------------------------------- #
def _endpoint(n=4000, seed=0):
    rng = np.random.default_rng(seed)
    eavail = rng.gamma(2.0, 0.5, size=n)
    labels = np.array([name for name, _lo, _hi in sc._safeguard_regions()])
    region = labels[rng.integers(0, labels.size, size=n)]
    return sc.Endpoint(truth_eavail=eavail, region_of_event=region)


class TestEndpoint(unittest.TestCase):
    def test_an_oracle_run_scores_one_and_a_do_nothing_run_scores_zero(self):
        ep = _endpoint()
        oracle = sc.Run("ours", "final", 127,
                        sc.injected_truth_weights(ep.truth_eavail, ep.amplitude,
                                                  ep.clip))
        idle = sc.Run("theirs", "final", 127, np.ones(ep.n_events))
        scored_oracle = sc.score_run(oracle, ep, scoreable_regions=["good"])
        scored_idle = sc.score_run(idle, ep, scoreable_regions=["good"])
        self.assertAlmostEqual(scored_oracle["recovery"], 1.0, places=10)
        self.assertAlmostEqual(scored_idle["recovery"], 0.0, places=10)

    def test_overshoot_is_reported_and_not_clipped(self):
        # Overshoot means going too far ALONG the injected direction, so the run
        # is the target's own displacement scaled past 1 -- not a differently
        # shaped injection, which moves somewhere else entirely and scores low.
        ep = _endpoint()
        target = sc.injected_truth_weights(ep.truth_eavail, ep.amplitude, ep.clip)
        over = sc.Run("ours", "final", 127, 1.0 + 1.5 * (target - 1.0))
        scored = sc.score_run(over, ep, scoreable_regions=["good"])
        # The L1 score CANNOT exceed 1 -- residual is a sum of absolute values --
        # so overshoot shows up as a score below 1 with a projection above it.
        self.assertLessEqual(scored["recovery"], 1.0)
        self.assertAlmostEqual(scored["overshoot_projection"], 1.5, places=6)
        self.assertTrue(scored["overshoot"])
        self.assertFalse(scored["wrong_direction"])

    def test_the_l1_score_is_bounded_above_by_one_for_any_weights(self):
        ep = _endpoint(n=800, seed=3)
        rng = np.random.default_rng(11)
        for trial in range(25):
            run = sc.Run("ours", "final", 127, rng.gamma(1.0, 1.0, ep.n_events))
            self.assertLessEqual(
                sc.score_run(run, ep, scoreable_regions=["good"])["recovery"],
                1.0 + 1e-12, msg=f"trial {trial}")

    def test_moving_away_from_the_target_scores_below_zero(self):
        ep = _endpoint()
        target = sc.injected_truth_weights(ep.truth_eavail, ep.amplitude, ep.clip)
        # -0.4 along the injected direction. A full -1.0 step would drive some
        # weights negative, which is a broken run rather than a bad one.
        backwards = sc.Run("ours", "final", 127, 1.0 - 0.4 * (target - 1.0))
        scored = sc.score_run(backwards, ep, scoreable_regions=["good"])
        self.assertAlmostEqual(scored["recovery"], -0.4, places=6)
        self.assertAlmostEqual(scored["overshoot_projection"], -0.4, places=6)
        self.assertTrue(scored["wrong_direction"])
        self.assertTrue(scored["worse_than_doing_nothing"])

    def test_region_labels_must_be_frozen_regions(self):
        with self.assertRaisesRegex(ValueError, "not frozen regions"):
            sc.Endpoint(truth_eavail=np.ones(3),
                        region_of_event=np.array(["good", "excellent", "good"]))

    def test_a_length_mismatch_between_weights_and_events_is_refused(self):
        ep = _endpoint(n=100)
        run = sc.Run("ours", "final", 127, np.ones(99))
        with self.assertRaisesRegex(ValueError, "different event sets"):
            sc.score_run(run, ep, scoreable_regions=["good"])


class TestRun(unittest.TestCase):
    def test_an_off_list_seed_is_refused(self):
        with self.assertRaisesRegex(ValueError, "not on the frozen final list"):
            sc.Run("ours", "final", 12345, np.ones(4))

    def test_a_pilot_seed_is_not_a_final_seed(self):
        sc.Run("ours", "pilot", fd.SEEDS["pilot"][0], np.ones(4))
        with self.assertRaises(ValueError):
            sc.Run("ours", "final", fd.SEEDS["pilot"][0], np.ones(4))

    def test_non_finite_weights_are_a_failed_run_not_a_low_score(self):
        with self.assertRaisesRegex(ValueError, "non-finite"):
            sc.Run("ours", "final", 127, np.array([1.0, np.nan, 1.0]))

    def test_load_run_refuses_a_filename_that_contradicts_the_receipt(self):
        with TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "receipt.json").write_text(json.dumps(
                {"arm": "ours", "stage": "final", "seed": 127}))
            path = folder / "weights_theirs_final_127.npz"
            np.savez(path, weights=np.ones(4))
            with self.assertRaisesRegex(ValueError, "different run"):
                sc.load_run(path)

    def test_load_run_requires_a_receipt(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "weights_ours_final_127.npz"
            np.savez(path, weights=np.ones(4))
            with self.assertRaisesRegex(FileNotFoundError, "no receipt"):
                sc.load_run(path)


# --------------------------------------------------------------------------- #
def _scores(stage, ours, theirs, regions=("good", "moderate")):
    rows = []
    for seed, (o, t) in zip(fd.SEEDS[stage], zip(ours, theirs)):
        for arm, value in (("ours", o), ("theirs", t)):
            rows.append({
                "arm": arm, "stage": stage, "seed": seed, "recovery": value,
                "recovery_by_region": {r: value for r in regions},
            })
    return rows


class TestPairing(unittest.TestCase):
    def test_half_a_pair_is_refused(self):
        rows = _scores("final", [0.5] * 8, [0.5] * 8)
        rows = [r for r in rows if not (r["seed"] == 139 and r["arm"] == "theirs")]
        with self.assertRaisesRegex(ValueError, "only one arm scored"):
            sc.paired_differences(rows, "final")

    def test_a_missing_pair_is_a_missing_observation_not_a_smaller_sample(self):
        rows = [r for r in _scores("final", [0.5] * 8, [0.5] * 8)
                if r["seed"] != 223]
        with self.assertRaisesRegex(ValueError, "missing observation"):
            sc.paired_differences(rows, "final")

    def test_differences_are_ours_minus_theirs_per_seed(self):
        rows = _scores("final", [0.6] * 8, [0.5] * 8)
        diffs = sc.paired_differences(rows, "final")
        self.assertEqual(set(diffs), set(fd.SEEDS["final"]))
        for value in diffs.values():
            self.assertAlmostEqual(value, 0.1)


class TestInterval(unittest.TestCase):
    def test_one_pair_gives_no_interval(self):
        with self.assertRaisesRegex(ValueError, "at least two pairs"):
            sc.t_interval([0.1])

    def test_interval_matches_a_hand_computation(self):
        d = [0.10, 0.12, 0.08, 0.14]
        out = sc.t_interval(d)
        mean, sd, n = np.mean(d), np.std(d, ddof=1), len(d)
        half = T_TABLE[3] * sd / math.sqrt(n)
        self.assertAlmostEqual(out["mean"], mean)
        self.assertAlmostEqual(out["half_width"], half, places=5)
        self.assertEqual(out["df"], 3)


class TestSizing(unittest.TestCase):
    def test_sizing_uses_the_upper_sigma_bound_so_it_exceeds_naive_sizing(self):
        pilot = [0.01, -0.02, 0.03, 0.00]
        out = sc.size_from_pilot(pilot)
        self.assertGreater(out["sigma_upper_bound"], out["sigma_hat"])
        naive = 2
        while (sc._t_quantile(0.975, naive - 1) * out["sigma_hat"]
               / math.sqrt(naive)) > out["delta"]:
            naive += 1
        self.assertGreaterEqual(out["required_n"], naive)

    def test_a_tiny_spread_needs_few_pairs_and_a_large_one_needs_many(self):
        tight = sc.size_from_pilot([0.001, 0.0, -0.001, 0.0005])
        loose = sc.size_from_pilot([0.02, -0.03, 0.025, -0.015])
        self.assertTrue(tight["feasible"] and loose["feasible"])
        self.assertLess(tight["required_n"], loose["required_n"])

    def test_the_size_is_reported_infeasible_rather_than_delta_widened(self):
        out = sc.size_from_pilot([5.0, -6.0, 4.0, -7.0], max_n=32)
        self.assertFalse(out["feasible"])
        self.assertIsNone(out["required_n"])
        self.assertEqual(out["delta"], fd.THRESHOLDS["non_inferiority_delta"])


# --------------------------------------------------------------------------- #
REGIONAL_REF = {"good": 0.90, "moderate": 0.70, "poor": 0.40,
                "low_acceptance": 0.14}


class TestCampaign(unittest.TestCase):
    def test_pilot_rows_passed_as_campaign_scores_are_refused(self):
        rows = _scores("final", [0.7] * 8, [0.7] * 8) \
            + _scores("pilot", [0.7] * 4, [0.7] * 4)
        with self.assertRaisesRegex(ValueError, "pilot rows were passed"):
            sc.score_campaign(rows, reference=0.85,
                              regional_reference=REGIONAL_REF,
                              scoreable_regions=["good", "moderate"])

    def test_a_scoreable_region_without_its_own_reference_is_refused(self):
        rows = _scores("final", [0.7] * 8, [0.7] * 8)
        with self.assertRaisesRegex(ValueError, "no regional reference"):
            sc.score_campaign(rows, reference=0.85,
                              regional_reference={"good": 0.9, "moderate": None},
                              scoreable_regions=["good", "moderate"])

    def test_an_arm_below_absolute_adequacy_is_ineligible(self):
        rows = _scores("final", [0.75] * 8, [0.20] * 8)
        report = sc.score_campaign(rows, reference=0.85,
                                   regional_reference=REGIONAL_REF,
                                   scoreable_regions=["good", "moderate"])
        self.assertTrue(report["absolute_adequacy"]["arms"]["ours"]["adequate"])
        self.assertFalse(report["absolute_adequacy"]["arms"]["theirs"]["adequate"])

    def test_one_arm_failing_does_not_disqualify_the_other(self):
        rows = _scores("final", [0.80] * 8, [0.10] * 8)
        report = sc.score_campaign(rows, reference=0.85,
                                   regional_reference=REGIONAL_REF,
                                   scoreable_regions=["good", "moderate"])
        self.assertEqual(report["verdict"], sr.Verdict.ONLY_OURS_ELIGIBLE.value)

    def test_theirs_better_but_retained_is_reported_as_that(self):
        # his arm ahead by 0.01: inside the 0.04 switching threshold.
        ours = [0.800, 0.802, 0.798, 0.801, 0.799, 0.800, 0.803, 0.797]
        theirs = [v + 0.010 for v in ours]
        rows = _scores("final", ours, theirs)
        report = sc.score_campaign(rows, reference=0.85,
                                   regional_reference=REGIONAL_REF,
                                   scoreable_regions=["good", "moderate"])
        self.assertTrue(report["theirs_scored_better"])
        self.assertEqual(report["recommendation"],
                         sr.Recommendation.ADOPT_OURS.value)
        if report["recommendation"] == sr.Recommendation.ADOPT_OURS.value:
            self.assertTrue(report["retained_ours_though_theirs_scored_better"])
            self.assertIn("Non-inferiority is not superiority",
                          report["non_inferiority_is_not_superiority"])

    def test_low_acceptance_is_reported_and_never_called_unresolvable(self):
        rows = _scores("final", [0.7] * 8, [0.7] * 8,
                       regions=("good", "moderate", "low_acceptance"))
        report = sc.score_campaign(rows, reference=0.85,
                                   regional_reference=REGIONAL_REF,
                                   scoreable_regions=["good", "moderate"])
        band = report["low_acceptance"]
        self.assertTrue(band["retained"])
        self.assertIsNotNone(band["mean_recovery_by_arm"]["ours"])
        self.assertNotIn("unresolvable", band["reading"].lower().replace(
            "not called fundamentally unresolvable", ""))

    def test_the_report_carries_the_step_two_scope_limit(self):
        rows = _scores("final", [0.7] * 8, [0.7] * 8)
        report = sc.score_campaign(rows, reference=0.85,
                                   regional_reference=REGIONAL_REF,
                                   scoreable_regions=["good", "moderate"])
        self.assertIn("what_it_cannot_speak_to", report["scope"])
        self.assertTrue(report["pilot_excluded"])


if __name__ == "__main__":
    unittest.main()


class TestTheirsBetweenTheTwoThresholds(unittest.TestCase):
    """His arm ahead by more than delta but less than the switching threshold."""

    def test_the_verdict_names_his_lead_and_the_recommendation_keeps_ours(self):
        ours = [0.800, 0.802, 0.798, 0.801, 0.799, 0.800, 0.803, 0.797]
        theirs = [v + 0.030 for v in ours]
        report = sc.score_campaign(_scores("final", ours, theirs),
                                   reference=0.85,
                                   regional_reference=REGIONAL_REF,
                                   scoreable_regions=["good", "moderate"])
        self.assertEqual(
            report["verdict"],
            sr.Verdict.THEIRS_BETTER_BELOW_SWITCHING_THRESHOLD.value)
        self.assertTrue(report["theirs_scored_better"])
        self.assertTrue(report["retained_ours_though_theirs_scored_better"])
        self.assertIn("Non-inferiority is not superiority",
                      report["non_inferiority_is_not_superiority"])
