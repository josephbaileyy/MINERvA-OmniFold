#!/usr/bin/env python3
"""Guards on the coupled-phi curve combiner, all added 2026-07-31 after review.

Each of these is a check that was absent or mis-specified while the curve it protects was already
being quoted. They are tested because an unexercised guard is the same defect one level up -- the
review that produced them found six checks that could not fail, and adding a seventh would be a
poor way to close it.

NOT COVERED: closure_coupled_phi_sweep.main(). Its `gain_at_zero_coupling` fix and its per-point
`extended_ok` field only materialize inside a run that trains three arms per point on a GPU. The
extended-arm gate itself IS covered, because the summarizer re-derives it from the recorded
`extended` value rather than trusting the driver's flag -- which is also why the ten already-banked
points did not need re-running.
"""
import copy
import json
import os
import sys
import tempfile
import unittest

PET = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pet")
if PET not in sys.path:
    sys.path.insert(0, PET)

import closure_coupled_phi_summarize as ccs      # noqa: E402

CONFIG = {"seed": 0, "n_events": 60000, "tokens": 5, "strata": 10, "amplitude": 1.2,
          "niter": 3, "epochs": 8, "batch_size": 512}


def point(coupling, *, corr, leak, extended, control=0.9):
    return {"coupling": coupling, "corr": {"cosphi_pt": corr}, "leak": leak,
            "extended": extended, "gain": extended - leak, "control": control,
            "control_ok": control > 0.5, "accepted_fraction": 0.5}


def run_file(seed, points, **cfg_overrides):
    config = dict(CONFIG, seed=seed, **cfg_overrides)
    return {"config": config, "points": points}


def three_points(offset=0.0):
    """A minimal curve: four couplings, gains well clear of CLEARANCE.

    Four rather than three so a test can invalidate one point and still leave the three the
    summarizer requires before it will draw a curve at all.
    """
    return [point(0.0, corr=0.00, leak=0.000 + offset, extended=0.90),
            point(1.0, corr=0.30, leak=0.090 + offset, extended=0.90),
            point(1.5, corr=0.45, leak=0.203 + offset, extended=0.90),
            point(2.0, corr=0.60, leak=0.360 + offset, extended=0.90)]


class SummarizerGuards(unittest.TestCase):

    def summarize(self, files, extra_argv=()):
        """Write the given run dicts and invoke the real main()."""
        with tempfile.TemporaryDirectory() as td:
            for i, run in enumerate(files):
                name = f"closure_coupled_phi_sweep_{i}_s{run['config']['seed']}.json"
                with open(os.path.join(td, name), "w") as fh:
                    json.dump(run, fh)
            out = os.path.join(td, "curve.json")
            argv = ["prog", "--dirs", td, "--out", out, *extra_argv]
            old = sys.argv
            try:
                sys.argv = argv
                ccs.main()
            finally:
                sys.argv = old
            with open(out) as fh:
                return json.load(fh)

    def test_two_files_one_seed_is_rejected(self):
        """Counting points is not counting seeds.

        The original grid and the high-lambda extension deliberately share lambda=2.2, so two
        same-seed files satisfy `len(pts) >= 2` while carrying zero retraining information.
        """
        same_seed = [run_file(0, three_points()), run_file(0, three_points(offset=0.001))]
        with self.assertRaises(SystemExit) as cm:
            self.summarize(same_seed)
        self.assertIn("distinct seed", str(cm.exception))

    def test_two_distinct_seeds_are_accepted(self):
        out = self.summarize([run_file(0, three_points()), run_file(7, three_points(0.002))])
        self.assertEqual([r["n_seeds"] for r in out["points"]], [2, 2, 2, 2])

    def test_fixture_mismatch_is_rejected(self):
        """The sibling feature_rank_summarize.py:51 hard-fails on this; here it merged on trust."""
        with self.assertRaises(SystemExit) as cm:
            self.summarize([run_file(0, three_points()),
                            run_file(7, three_points(0.002), epochs=16)])
        self.assertIn("disagree on the fixture", str(cm.exception))

    def test_differing_lambda_grids_are_still_allowed(self):
        """The one config axis that MAY differ -- that is why the glob picks up both files."""
        hi = [point(2.0, corr=0.60, leak=0.360, extended=0.90),
              point(3.0, corr=0.80, leak=0.640, extended=0.90)]
        out = self.summarize([run_file(0, three_points()), run_file(7, three_points(0.002)),
                              run_file(0, hi), run_file(7, copy.deepcopy(hi))])
        self.assertEqual([r["coupling"] for r in out["points"]], [0.0, 1.0, 1.5, 2.0, 3.0])

    def test_undertrained_extended_arm_invalidates_the_point(self):
        """gain = extended - leak collapses whether the leak rose or the extended arm died.

        The driver's positive control runs the BASE arm, so it passes in both cases. Without this
        gate the second reads as a real crossing.
        """
        broken = three_points()
        broken[3] = point(2.0, corr=0.60, leak=0.360, extended=0.10)   # control still fine
        other = three_points(0.002)
        other[3] = point(2.0, corr=0.60, leak=0.362, extended=0.10)
        out = self.summarize([run_file(0, broken), run_file(7, other)])
        by_lam = {r["coupling"]: r for r in out["points"]}
        self.assertTrue(by_lam[0.0]["valid"])
        self.assertFalse(by_lam[2.0]["valid"],
                         "an extended arm at 0.10 did not train; that is not a gain collapse")

    def test_pooled_floor_uses_leak_noise_not_gain_noise(self):
        """The residual judged is a leak residual, so the floor must be the leak's own scatter.

        Constructed so the two differ starkly and in the direction that mattered: the extended
        arm's scatter cancels out of the gain, so the gain spread understates the leak spread.
        Here seed 7's leak and extended both move by 0.10, leaving every gain identical.
        """
        a = three_points()
        b = [point(p["coupling"], corr=p["corr"]["cosphi_pt"], leak=p["leak"] + 0.10,
                   extended=p["extended"] + 0.10) for p in a]
        out = self.summarize([run_file(0, a), run_file(7, b)],
                             extra_argv=("--law-fit-max-corr", "0.35"))
        for r in out["points"]:
            self.assertAlmostEqual(r["gain_spread"], 0.0, places=9)
            self.assertAlmostEqual(r["leak_spread"], 0.10, places=9)
        self.assertAlmostEqual(out["law_leak_eq_corr2"]["pooled_seed_noise"], 0.10, places=9,
                               msg="pooled floor fell back to the gain spread (0.0), which is the "
                                   "26x understatement this fix removes")


class RecordedCurveIsUnchanged(unittest.TestCase):
    """The fixes above must not move the banked result, only its justification."""

    def test_committed_curve_still_reads_as_published(self):
        path = os.path.join(os.path.dirname(PET), "products", "pet", "coupled_phi_curve.json")
        if not os.path.exists(path):
            self.skipTest("curve product absent")
        with open(path) as fh:
            c = json.load(fh)
        self.assertEqual(c["verdict"], "CROSSING_RESOLVED")
        self.assertAlmostEqual(c["crossing_mean"], 0.7768, places=4)
        law = c["law_leak_eq_corr2"]
        self.assertFalse(law["holds_out_of_sample"])
        self.assertEqual((law["out_of_sample_broken"], law["out_of_sample_n"]), (2, 4))
        self.assertAlmostEqual(law["tolerance"], 0.023258, places=6)
        self.assertTrue(all(p["valid"] for p in c["points"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
