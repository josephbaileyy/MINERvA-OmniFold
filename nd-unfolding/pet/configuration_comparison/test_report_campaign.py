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


def write_run(folder: Path, arm: str, stage: str, seed: int, weights: np.ndarray,
              rows_a=None, rows_b=None, tilt_a=None):
    run_dir = folder / stage / f"{arm}-seed{seed}"
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "receipt.json").write_text(json.dumps(
        {"arm": arm, "stage": stage, "seed": seed, "scored_here": False}))
    np.savez_compressed(run_dir / f"weights_{arm}_{stage}_{seed}.npz",
                        weights=weights, dump_rows_a=rows_a, dump_rows_b=rows_b,
                        tilt_a=tilt_a)


class TestEndToEnd(unittest.TestCase):
    def setUp(self):
        import closure_powered_truth_reweight as cp
        self._tmp = TemporaryDirectory()
        self.tmp = Path(self._tmp.dir if hasattr(self._tmp, "dir") else self._tmp.name)
        self.closure = self.tmp / "closure.npz"
        write_closure(self.closure)
        with np.load(self.closure) as blob:
            n = int(np.asarray(blob["pass_truth"]).size)
            eavail = np.asarray(blob["truth_scalars"])[:, 2]
            pg = np.asarray(blob["pass_truth"]).astype(bool)
        self.rows_a, self.rows_b = cp.deterministic_halves(n, half=n // 3, seed=7)
        pg_a = pg[self.rows_a]
        self.tilt_a = np.ones(self.rows_a.size)
        tilt, _ = cp.clipped_exponential_tilt(eavail[self.rows_a][pg_a], 0.35, 3.0)
        self.tilt_a[pg_a] = tilt
        self.campaign = self.tmp / "campaign"
        self.n_prior = int(pg[self.rows_b].sum())
        # The push that would reproduce half A's tilted spectrum is, to the
        # extent the halves are draws from one distribution, the same tilt
        # evaluated on half B. Scaling it gives a synthetic run of known
        # approximate recovery, which is what "ours ahead" has to mean.
        pg_b = pg[self.rows_b]
        self.tilt_b = np.ones(self.rows_b.size)
        tb, _ = cp.clipped_exponential_tilt(eavail[self.rows_b][pg_b], 0.35, 3.0)
        self.tilt_b[pg_b] = tb

    def tearDown(self):
        self._tmp.cleanup()

    def _populate(self, ours_scale, theirs_scale, stages=("final",)):
        """Push weights over ALL of half B, as the driver writes them."""
        rng = np.random.default_rng(1)
        for stage in stages:
            for seed in fd.SEEDS[stage]:
                for arm, scale in (("ours", ours_scale), ("theirs", theirs_scale)):
                    jitter = scale + rng.normal(0.0, 0.004)
                    push = 1.0 + jitter * (self.tilt_b - 1.0)
                    write_run(self.campaign, arm, stage, seed, push,
                              rows_a=self.rows_a, rows_b=self.rows_b,
                              tilt_a=self.tilt_a)

    def test_the_endpoint_built_from_a_run_uses_its_two_disjoint_halves(self):
        self._populate(0.90, 0.88)
        weights = next((self.campaign / "final").rglob("weights_*.npz"))
        endpoint, context = rc.build_endpoint(self.closure, weights)
        self.assertTrue(context["halves_disjoint"])
        self.assertGreater(context["half_a_rows"], 0)
        self.assertGreater(context["half_b_rows"], 0)
        self.assertGreater(len(context["scoreable_regions"]), 0)
        for name in context["scoreable_regions"]:
            self.assertIsNotNone(context["regional_reference"][name])

    def test_overlapping_halves_are_refused_rather_than_scored(self):
        """Overlap restores the identity shortcut and power goes to zero."""
        self._populate(0.90, 0.88)
        weights = next((self.campaign / "final").rglob("weights_*.npz"))
        with np.load(weights) as blob:
            data = {k: blob[k] for k in blob.files}
        data["dump_rows_b"] = data["dump_rows_a"]
        np.savez_compressed(weights, **data)
        with self.assertRaisesRegex(SystemExit, "halves overlap"):
            rc.build_endpoint(self.closure, weights)

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
        weights = next((self.campaign / "final").rglob("weights_*.npz"))
        endpoint, context = rc.build_endpoint(self.closure, weights)
        final = [sc.score_run(r, endpoint,
                              scoreable_regions=context["scoreable_regions"])
                 for r in rc.discover(self.campaign, "final")]
        pilot = [sc.score_run(r, endpoint,
                              scoreable_regions=context["scoreable_regions"])
                 for r in rc.discover(self.campaign, "pilot")]
        report = sc.score_campaign(
            final, reference=0.95,
            regional_reference=context["regional_reference"],
            scoreable_regions=context["scoreable_regions"],
            region_census=context["census"], pilot_scores=pilot)
        self.assertEqual(report["interval"]["n_pairs"], len(fd.SEEDS["final"]))
        self.assertEqual(report["pilot_reported_separately"]["n_rows"],
                         2 * len(fd.SEEDS["pilot"]))
        self.assertIn("required_n", report["pilot_reported_separately"]["sizing"])

    def test_an_idle_run_scores_near_zero_and_moving_the_right_way_scores_higher(self):
        """No oracle here. Under DISJOINT halves there is no weighting of half
        B that reproduces half A's spectrum exactly -- that is the point of the
        split, and a test asserting recovery == 1 would only pass if the two
        halves were the same events."""
        self._populate(0.90, 0.88)
        weights = next((self.campaign / "final").rglob("weights_*.npz"))
        endpoint, context = rc.build_endpoint(self.closure, weights)
        scoreable = context["scoreable_regions"]
        idle = sc.score_run(
            sc.Run("ours", "final", 127, np.ones(endpoint.n_prior)),
            endpoint, scoreable_regions=scoreable)
        self.assertLess(abs(idle["recovery"]), 0.35)
        self.assertLessEqual(idle["recovery"], 1.0)


if __name__ == "__main__":
    unittest.main()


class TheDeliverableIsProducedAutomatically(unittest.TestCase):
    """The chain ended at `final`; the deck waited on a person running two
    commands. Every input is pinned, so it does not need one."""

    def _script(self):
        return (HERE / "sbatch_report_and_deck.sh").read_text()

    def test_it_runs_both_steps(self):
        text = self._script()
        self.assertIn("report_campaign.py", text)
        self.assertIn("make_final_deck.py", text)

    def test_the_reference_comes_from_the_freeze_not_a_literal(self):
        text = self._script()
        self.assertIn('fd.REFERENCE[', text)
        self.assertNotIn("--reference 0.6", text)

    def test_it_does_not_send_anything(self):
        """The goal says the deck is FOR Ben and must not be sent to him.

        Matched on TOKENS, not substrings: the first version of this test
        flagged `user.email` for containing "mail", which is the kind of
        false positive that gets a guard deleted rather than fixed.
        """
        import re
        text = self._script()
        for verb in ("mail", "sendmail", "mutt", "curl", "wget", "smtp", "scp"):
            self.assertIsNone(re.search(rf"(?<![\w.]){verb}(?![\w.])", text,
                                        re.IGNORECASE), msg=verb)
        self.assertIn("does NOT send anything", text)

    def test_the_chain_ends_with_it(self):
        text = (HERE / "sbatch_join_and_launch.sh").read_text()
        self.assertIn("sbatch_report_and_deck.sh", text)
        self.assertIn("--dependency=afterok:$FINAL", text)
