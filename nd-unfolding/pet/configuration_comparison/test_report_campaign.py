"""End-to-end: a synthetic campaign directory in, a verdict out.

The point of this file is the WIRING. Every piece it exercises is unit-tested
elsewhere; what is not tested elsewhere is that the closure file's keys, the
receipt's fields, the weights' length, the region labels and the selection rule
all line up when a real directory is handed over. They have failed to line up
before -- the driver once expected a pre-packed array that nothing writes.
"""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np

import frozen_design as fd
import report_campaign as rc
import score_campaign as sc

HERE = Path(__file__).resolve().parent


def write_closure(path: Path, n=6000, seed=0):
    """A closure file with the keys `characterize_regions` reads from the real one."""
    rng = np.random.default_rng(seed)
    pt = rng.uniform(0.0, 2.0, n)
    pz = rng.uniform(0.0, 20.0, n)
    eavail = rng.gamma(2.0, 0.5, n)
    # Acceptance falls with pT, so the cells span bands rather than sitting in one.
    accept_prob = np.clip(0.95 - 0.45 * pt, 0.01, 0.99)
    np.savez(path,
             truth_scalars=np.column_stack([pt, pz, eavail]),
             pass_truth=np.ones(n, bool),
             pass_reco=rng.uniform(size=n) < accept_prob,
             w_truth=rng.gamma(4.0, 0.25, n),
             edges_0=np.linspace(0.0, 2.0, 16),
             edges_1=np.linspace(0.0, 20.0, 20))


def write_run(folder: Path, arm: str, stage: str, seed: int, weights: np.ndarray):
    run_dir = folder / stage / f"{arm}-seed{seed}"
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "receipt.json").write_text(json.dumps(
        {"arm": arm, "stage": stage, "seed": seed, "scored_here": False}))
    np.savez_compressed(run_dir / f"weights_{arm}_{stage}_{seed}.npz",
                        weights=weights)


class TestEndToEnd(unittest.TestCase):
    def setUp(self):
        self._tmp = TemporaryDirectory()
        self.tmp = Path(self._tmp.dir if hasattr(self._tmp, "dir") else self._tmp.name)
        self.closure = self.tmp / "closure.npz"
        write_closure(self.closure)
        self.endpoint, self.context = rc.build_endpoint(self.closure)
        self.campaign = self.tmp / "campaign"

    def tearDown(self):
        self._tmp.cleanup()

    def _populate(self, ours_scale, theirs_scale, stages=("final",)):
        target = sc.injected_truth_weights(
            self.endpoint.truth_eavail, fd.ENDPOINT["amplitude"],
            fd.ENDPOINT["clip"])
        rng = np.random.default_rng(1)
        for stage in stages:
            for seed in fd.SEEDS[stage]:
                for arm, scale in (("ours", ours_scale), ("theirs", theirs_scale)):
                    jitter = scale + rng.normal(0.0, 0.004)
                    write_run(self.campaign, arm, stage, seed,
                              1.0 + jitter * (target - 1.0))

    def test_the_endpoint_built_from_a_closure_file_is_usable(self):
        self.assertEqual(self.endpoint.n_events, 6000)
        self.assertGreater(len(self.context["scoreable_regions"]), 0)
        for name in self.context["scoreable_regions"]:
            self.assertIsNotNone(self.context["regional_reference"][name])

    def test_a_full_campaign_produces_a_verdict(self):
        self._populate(0.90, 0.88)
        output = self.tmp / "report.json"
        code = subprocess.run(
            [sys.executable, str(HERE / "report_campaign.py"),
             "--campaign", str(self.campaign), "--closure-npz", str(self.closure),
             "--reference", "0.95", "--output", str(output)],
            cwd=HERE, capture_output=True, text=True)
        self.assertEqual(code.returncode, 0, msg=code.stderr[-3000:])
        report = json.loads(output.read_text())
        self.assertEqual(report["interval"]["n_pairs"], len(fd.SEEDS["final"]))
        self.assertGreater(report["interval"]["mean"], 0.0)  # ours ahead
        self.assertIn("verdict", report)
        self.assertTrue(report["pilot_excluded"])
        self.assertEqual(len(report["per_run"]), 2 * len(fd.SEEDS["final"]))

    def test_an_incomplete_campaign_is_refused_not_scored_short(self):
        self._populate(0.90, 0.88)
        missing = self.campaign / "final" / "theirs-seed223"
        for path in missing.iterdir():
            path.unlink()
        missing.rmdir()
        output = self.tmp / "report.json"
        code = subprocess.run(
            [sys.executable, str(HERE / "report_campaign.py"),
             "--campaign", str(self.campaign), "--closure-npz", str(self.closure),
             "--reference", "0.95", "--output", str(output)],
            cwd=HERE, capture_output=True, text=True)
        self.assertNotEqual(code.returncode, 0)
        self.assertIn("only one arm scored", code.stderr)
        self.assertFalse(output.exists())

    def test_a_campaign_with_no_final_stage_is_refused(self):
        self._populate(0.90, 0.88, stages=("pilot",))
        with self.assertRaisesRegex(FileNotFoundError, "not complete"):
            rc.discover(self.campaign, "final")

    def test_the_pilot_is_reported_and_sizes_n_without_entering_the_interval(self):
        self._populate(0.90, 0.88, stages=("final", "pilot"))
        final = [sc.score_run(r, self.endpoint,
                              scoreable_regions=self.context["scoreable_regions"])
                 for r in rc.discover(self.campaign, "final")]
        pilot = [sc.score_run(r, self.endpoint,
                              scoreable_regions=self.context["scoreable_regions"])
                 for r in rc.discover(self.campaign, "pilot")]
        report = sc.score_campaign(
            final, reference=0.95,
            regional_reference=self.context["regional_reference"],
            scoreable_regions=self.context["scoreable_regions"],
            region_census=self.context["census"], pilot_scores=pilot)
        self.assertEqual(report["interval"]["n_pairs"], len(fd.SEEDS["final"]))
        self.assertEqual(report["pilot_reported_separately"]["n_rows"],
                         2 * len(fd.SEEDS["pilot"]))
        self.assertIn("required_n", report["pilot_reported_separately"]["sizing"])

    def test_an_oracle_pair_recovers_one_and_an_idle_pair_recovers_zero(self):
        target = sc.injected_truth_weights(
            self.endpoint.truth_eavail, fd.ENDPOINT["amplitude"],
            fd.ENDPOINT["clip"])
        scoreable = self.context["scoreable_regions"]
        oracle = sc.score_run(sc.Run("ours", "final", 127, target),
                              self.endpoint, scoreable_regions=scoreable)
        idle = sc.score_run(sc.Run("ours", "final", 127,
                                   np.ones(self.endpoint.n_events)),
                            self.endpoint, scoreable_regions=scoreable)
        self.assertAlmostEqual(oracle["recovery"], 1.0, places=9)
        self.assertAlmostEqual(idle["recovery"], 0.0, places=9)
        for name in scoreable:
            self.assertAlmostEqual(oracle["recovery_by_region"][name], 1.0, places=9)


if __name__ == "__main__":
    unittest.main()
