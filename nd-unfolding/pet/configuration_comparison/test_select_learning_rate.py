"""Selection happens on the tuning split, on the frozen grid, or not at all."""
from __future__ import annotations

import unittest

import frozen_design as fd
import select_learning_rate as sl

POINTS = [float(x) for x in fd.TUNING_GRID["points"]]
SEEDS = list(fd.SEEDS["tuning"])


def rows(best_for=None, recovery=0.3, drop=None):
    best_for = best_for or {}
    out = []
    for arm in ("ours", "theirs"):
        for lr in POINTS:
            for seed in SEEDS:
                if drop and (arm, lr, seed) == drop:
                    continue
                bonus = 0.1 if best_for.get(arm) == lr else 0.0
                out.append({"arm": arm, "seed": seed, "learning_rate": lr,
                            "recovery": recovery + bonus})
    return out


class Selection(unittest.TestCase):
    def test_it_picks_the_point_with_the_best_mean_over_the_tuning_seeds(self):
        got = sl.select(rows(best_for={"ours": 2e-4, "theirs": 5e-5}))
        self.assertEqual(got["selected"]["ours"]["learning_rate"], 2e-4)
        self.assertEqual(got["selected"]["theirs"]["learning_rate"], 5e-5)

    def test_the_arms_are_selected_independently(self):
        """`same_for_both_arms` offers the same four points, not the same pick."""
        got = sl.select(rows(best_for={"ours": 4e-4, "theirs": 1e-4}))
        self.assertNotEqual(got["selected"]["ours"]["learning_rate"],
                            got["selected"]["theirs"]["learning_rate"])
        self.assertTrue(got["arms_selected_independently"])

    def test_a_tie_goes_to_the_smaller_rate(self):
        got = sl.select(rows())           # every point identical
        self.assertEqual(got["selected"]["ours"]["learning_rate"], min(POINTS))

    def test_a_point_missing_a_seed_is_excluded_not_fatal(self):
        """A diverged rate is the grid doing its job, not a campaign failure.

        Within a point the rule is unchanged -- all its seeds or none -- but a
        point that did not complete is recorded unusable and selection
        proceeds among the rest.
        """
        got = sl.select(rows(drop=("ours", 2e-4, SEEDS[1])))
        self.assertIn(2e-4, got["selected"]["ours"]["unusable_points"])
        self.assertNotIn(2e-4, got["selected"]["ours"]["eligible_points"])
        self.assertNotEqual(got["selected"]["ours"]["learning_rate"], 2e-4)

    def test_an_excluded_point_is_reported_with_the_seeds_it_lost(self):
        got = sl.select(rows(drop=("ours", 2e-4, SEEDS[1])))
        entry = got["selected"]["ours"]["unusable_points"][2e-4]
        self.assertEqual(entry["missing_seeds"], [SEEDS[1]])

    def test_the_arms_can_end_with_different_eligible_sets(self):
        """His arm may diverge at a rate ours tolerates."""
        bad = [r for r in rows()
               if not (r["arm"] == "theirs" and r["learning_rate"] == 4e-4)]
        got = sl.select(bad)
        self.assertIn(4e-4, got["selected"]["ours"]["eligible_points"])
        self.assertNotIn(4e-4, got["selected"]["theirs"]["eligible_points"])

    def test_it_still_refuses_when_no_point_completed(self):
        """Excluding every point is not a selection."""
        only_one_seed = [r for r in rows() if r["seed"] == SEEDS[0]]
        with self.assertRaisesRegex(ValueError, "nothing to select between"):
            sl.select(only_one_seed)

    def test_an_off_grid_rate_is_refused(self):
        bad = rows()
        bad.append({"arm": "ours", "seed": SEEDS[0], "learning_rate": 3e-4,
                    "recovery": 0.99})
        with self.assertRaisesRegex(ValueError, "not on the frozen grid"):
            sl.select(bad)

    def test_every_point_is_reported_not_only_the_winner(self):
        got = sl.select(rows(best_for={"ours": 2e-4}))
        by_point = got["selected"]["ours"]["mean_recovery_by_point"]
        self.assertEqual(sorted(by_point), sorted(POINTS))

    def test_it_records_that_selection_used_the_tuning_split_only(self):
        got = sl.select(rows())
        self.assertIn("tuning split", got["selected_on"])


class TheLauncherSweepsTheGrid(unittest.TestCase):
    def test_the_tuning_array_covers_every_arm_seed_rate_once(self):
        arms = ["ours", "theirs"]
        seen = []
        for task in range(1, 2 * len(SEEDS) * len(POINTS) + 1):
            i = task - 1
            rest = i // 2
            seen.append((arms[i % 2], SEEDS[rest % 4], POINTS[rest // 4]))
        self.assertEqual(len(set(seen)), 2 * len(SEEDS) * len(POINTS))
        for arm in arms:
            for lr in POINTS:
                self.assertEqual(
                    sum(1 for x in seen if x[0] == arm and x[2] == lr), len(SEEDS))

    def test_selection_runs_afterany_so_a_diverged_rate_cannot_kill_it(self):
        from pathlib import Path
        text = (Path(__file__).resolve().parent
                / "sbatch_join_and_launch.sh").read_text()
        self.assertIn("--dependency=afterany:$TUNING", text)
        self.assertNotIn("--dependency=afterok:$TUNING", text)

    def test_the_launcher_sweeps_and_the_other_stages_do_not(self):
        from pathlib import Path
        text = (Path(__file__).resolve().parent / "sbatch_campaign.sh").read_text()
        self.assertIn('if [[ "$STAGE" == "tuning" ]]', text)
        self.assertIn("GRID=(0.00005 0.0001 0.0002 0.0004)", text)
        self.assertIn("selected_learning_rate.json", text)

    def test_pilot_and_final_refuse_to_default_the_rate(self):
        from pathlib import Path
        text = (Path(__file__).resolve().parent / "sbatch_campaign.sh").read_text()
        self.assertIn("no tuning selection at", text)
        self.assertNotIn('LR="${LEARNING_RATE:-0.0001}"', text)

    def test_the_tuning_run_directory_carries_the_rate(self):
        """Two tasks differing only in rate are different runs."""
        from pathlib import Path
        text = (Path(__file__).resolve().parent / "sbatch_campaign.sh").read_text()
        self.assertIn("seed${SEED}-lr${LR}", text)
