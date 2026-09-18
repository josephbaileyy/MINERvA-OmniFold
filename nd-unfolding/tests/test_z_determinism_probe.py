#!/usr/bin/env python3
"""Tests for the determinism probe, whose job is to REPLACE an assumption with a measurement.

Joseph's instruction was specific: *"Do not assume that setting four OpenMP variables establishes
determinism."* So the probe's own failure modes matter more than usual, and two of them are the
reason this file exists:

* `test_blind_probe_reports_unavailable_not_agreement` -- if the subject cannot load, the probe
  must say UNAVAILABLE. A probe that reported "no differences found" would be a blind instrument
  reporting zero, which reads identically to a clean pass. **This one runs against the REAL
  absence of LightGBM in this interpreter**, so its substrate is the impossibility rather than a
  simulation of it.
* `test_row_floor_is_recorded_as_waived_when_waived` -- a probe truncated to fit stops before the
  hazard. Below the floor LightGBM does not thread histogram construction, so every arm agrees and
  the agreement is a property of the fixture. A record that did not disclose the waiver would be
  green for the wrong reason.

The aggregation is tested through `summarise`, which is pure. The cells it is given are
hand-built HERE, and that is deliberate: `summarise`'s job is to decide what a set of digests
means, so feeding it constructed digest patterns is testing exactly its contract. The digests
themselves come from the backend in real use and are never invented there.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PROBE = REPO / "nd-unfolding" / "z_determinism_probe.py"
sys.path.insert(0, str(REPO / "nd-unfolding"))

import z_determinism_probe as Z  # noqa: E402


def _cell(arm, threads, digests):
    return {"arm": arm, "threads": threads, "digests": list(digests),
            "within_process_identical": len(set(digests)) == 1}


class BlindAndFloor(unittest.TestCase):
    def test_blind_probe_reports_unavailable_not_agreement(self):
        """LightGBM is genuinely absent here, so this is the real blind case, not a mock."""
        r = subprocess.run([sys.executable, str(PROBE), "--mode", "driver", "--rows", "5000",
                            "--allow-small-rows", "--repeats", "1", "--thread-grid", "1,2"],
                           capture_output=True, text=True)
        rec = json.loads(r.stdout)
        self.assertEqual(rec["verdict"], "UNAVAILABLE")
        self.assertIn("blind instrument reporting zero", rec["verdict_note"])
        self.assertEqual(r.returncode, 3, "a blind probe must exit nonzero")
        self.assertEqual(len(rec["unavailable"]), 5, "3 arms over a 2-wide grid, pinned pinned")
        self.assertIn("lightgbm", rec["unavailable"][0]["stderr"].lower())

    def test_row_floor_refuses_below_the_minimum(self):
        r = subprocess.run([sys.executable, str(PROBE), "--mode", "worker", "--arm", "historical",
                            "--rows", "1000"], capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("MIN_ROWS", r.stderr)
        self.assertIn("property of the fixture", r.stderr)

    def test_row_floor_is_recorded_as_waived_when_waived(self):
        rec = Z.summarise([], [], rows=1000, seed=42, repeats=2, thread_grid=(1,))
        self.assertTrue(rec["row_floor"].startswith("WAIVED"))
        self.assertIn("cannot support any determinism claim", rec["row_floor"])

    def test_row_floor_is_recorded_as_satisfied_at_the_floor(self):
        rec = Z.summarise([], [], rows=Z.MIN_ROWS, seed=42, repeats=2, thread_grid=(1,))
        self.assertEqual(rec["row_floor"], "SATISFIED")


class Aggregation(unittest.TestCase):
    def test_thread_variation_is_reported_as_not_invariant(self):
        """The finding that would make repeats pointless: output tracks the thread count."""
        cells = [_cell("historical", 1, ["aa", "aa"]), _cell("historical", 4, ["bb", "bb"])]
        rec = Z.summarise(cells, [], rows=Z.MIN_ROWS, seed=42, repeats=2, thread_grid=(1, 4))
        arm = rec["per_arm"]["historical"]
        self.assertTrue(arm["within_process_identical"])
        self.assertFalse(arm["invariant_across_thread_grid"])
        self.assertEqual(len(arm["distinct_digests"]), 2)

    def test_within_process_difference_is_reported(self):
        """The `4.452e-14` shape: two fits in ONE process disagreeing."""
        cells = [_cell("historical", 1, ["aa", "ab"])]
        rec = Z.summarise(cells, [], rows=Z.MIN_ROWS, seed=42, repeats=2, thread_grid=(1,))
        self.assertFalse(rec["per_arm"]["historical"]["within_process_identical"])

    def test_full_invariance_is_reported_without_being_called_determinism(self):
        cells = [_cell("pinned", 1, ["cc", "cc"])]
        rec = Z.summarise(cells, [], rows=Z.MIN_ROWS, seed=42, repeats=2, thread_grid=(1,))
        self.assertTrue(rec["per_arm"]["pinned"]["invariant_across_thread_grid"])
        self.assertEqual(rec["verdict"], "PARTIAL", "one arm of three is not a complete matrix")

    def test_verdict_is_partial_until_every_arm_reports(self):
        cells = [_cell("historical", 1, ["aa", "aa"]), _cell("det_only", 1, ["aa", "aa"])]
        rec = Z.summarise(cells, [], rows=Z.MIN_ROWS, seed=42, repeats=2, thread_grid=(1,))
        self.assertEqual(rec["verdict"], "PARTIAL")
        self.assertFalse(rec["arms_complete"])

    def test_complete_matrix_is_measured_not_adopted(self):
        # ⚠ This originally used a ONE-VALUE grid and asserted `MEASURED`, i.e. it encoded the
        # defect job 58507305 exposed -- a complete set of arms over a degenerate axis is not a
        # measurement of the axis. The grid is varied now; `DegenerateAxisIsNotAMeasurement`
        # covers the one-value case explicitly.
        cells = [_cell(a, t, ["x", "x"]) for a in Z.ARMS for t in (1, 4)]
        rec = Z.summarise(cells, [], rows=Z.MIN_ROWS, seed=42, repeats=2, thread_grid=(1, 4))
        self.assertEqual(rec["verdict"], "MEASURED")
        self.assertTrue(rec["arms_complete"])
        # The verdict must not overstate itself in any of three directions.
        self.assertIn("does NOT adopt", rec["verdict_note"])
        self.assertIn("across NODES", rec["verdict_note"])
        self.assertIn("material change to the estimator", rec["verdict_note"])


class ConfigurationUnderTest(unittest.TestCase):
    def test_the_three_arms_are_historical_det_only_and_pinned(self):
        self.assertEqual(set(Z.ARMS), {"historical", "det_only", "pinned"})

    def test_historical_arm_applies_no_overlay(self):
        """It must be what production constructs, or the baseline is not the baseline."""
        self.assertEqual(Z.ARMS["historical"], {})

    def test_pinned_arm_matches_the_repository_proposal(self):
        """The knobs are not retyped here: they must equal `z_reproducibility.Z_REPRO_KNOBS`,
        so a change to the proposal cannot leave this probe testing the old one."""
        import z_reproducibility as R
        proposed = {k: v for k, (v, _) in R.Z_REPRO_KNOBS.items()}
        self.assertEqual(Z.ARMS["pinned"], proposed)

    def test_production_params_are_read_from_the_production_factory(self):
        """Not retyped. A copy of the configuration would not drift when the original did."""
        src = PROBE.read_text()
        self.assertIn("core.make_estimators", src)
        self.assertNotIn("n_estimators=100", src)

    def test_dataset_seed_is_not_the_estimator_seed(self):
        """Sharing one seed would make a data difference indistinguishable from an estimator one."""
        src = PROBE.read_text()
        self.assertIn("1000003 + seed", src)

    def test_the_four_env_vars_are_set_in_the_child_environment(self):
        """Set in the CHILD, because OMP_NUM_THREADS is read at OpenMP initialisation. Setting it
        after the import may do nothing, and 'no effect' would then be ambiguous between a
        variable that is ignored and one that was set too late."""
        src = PROBE.read_text()
        for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS",
                    "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
            self.assertIn(var, src)
        self.assertIn("env=env", src)


class DegenerateAxisIsNotAMeasurement(unittest.TestCase):
    """THE DEFECT JOB 58507305 FOUND, and it is the worst kind: a GREEN run that measured nothing.

    That job COMPLETED in 54 s, exit 0, verdict `MEASURED`, with
    `invariant_across_thread_grid: true` for all three arms. It had run every cell at ONE thread.
    `sbatch --export=ALL,A=1,B=2` parses its argument as a comma-separated list of NAME=VALUE, so
    the commas inside `MNV_THREAD_GRID=1,2,4,8` (backslash-escaped) split the LIST -- backslash escaping does not
    survive it -- and `MNV_THREAD_GRID` exported as `1`.

    The invariance claim was arithmetically correct over a population of one. This is the
    empty-population failure with the population equal to a single point, and the probe reported it
    as a pass. Now: per-arm `VACUOUS`, overall verdict `DEGENERATE`, and a launcher refusal.

    ⚠ The `pinned` arm is single-valued BY DESIGN -- it sets `num_threads=1` -- so `VACUOUS` is the
    honest answer for that arm and not a defect. The distinction is tested below.
    """

    def _cells(self, arm, pairs):
        return [_cell(arm, t, ds) for t, ds in pairs]

    def test_one_thread_value_is_vacuous_not_true(self):
        rec = Z.summarise(self._cells("historical", [(1, ["aa", "aa"])]), [],
                          rows=Z.MIN_ROWS, seed=42, repeats=2, thread_grid=(1,))
        across = rec["per_arm"]["historical"]["invariant_across_thread_grid"]
        self.assertIsInstance(across, str, "a one-point axis must not report a boolean")
        self.assertTrue(across.startswith("VACUOUS"), across)
        self.assertEqual(rec["per_arm"]["historical"]["n_thread_values"], 1)

    def test_two_thread_values_report_a_real_boolean(self):
        rec = Z.summarise(self._cells("historical", [(1, ["aa", "aa"]), (4, ["aa", "aa"])]), [],
                          rows=Z.MIN_ROWS, seed=42, repeats=2, thread_grid=(1, 4))
        self.assertIs(rec["per_arm"]["historical"]["invariant_across_thread_grid"], True)
        rec2 = Z.summarise(self._cells("historical", [(1, ["aa", "aa"]), (4, ["bb", "bb"])]), [],
                           rows=Z.MIN_ROWS, seed=42, repeats=2, thread_grid=(1, 4))
        self.assertIs(rec2["per_arm"]["historical"]["invariant_across_thread_grid"], False)

    def test_degenerate_grid_downgrades_the_whole_verdict(self):
        """Even with every arm present, a one-valued grid is not `MEASURED`."""
        cells = [_cell(a, 1, ["x", "x"]) for a in Z.ARMS]
        rec = Z.summarise(cells, [], rows=Z.MIN_ROWS, seed=42, repeats=2, thread_grid=(1,))
        self.assertEqual(rec["verdict"], "DEGENERATE")
        self.assertFalse(rec["thread_axis_varied"])
        self.assertIn("NOTHING was measured about thread-count invariance", rec["verdict_note"])

    def test_varied_grid_is_measured_and_says_so(self):
        cells = [_cell(a, t, ["x", "x"]) for a in Z.ARMS for t in (1, 4)]
        rec = Z.summarise(cells, [], rows=Z.MIN_ROWS, seed=42, repeats=2, thread_grid=(1, 4))
        self.assertEqual(rec["verdict"], "MEASURED")
        self.assertTrue(rec["thread_axis_varied"])
        self.assertNotIn("DEGENERATE", rec["verdict_note"])

    def test_a_repeated_thread_value_does_not_count_as_variation(self):
        """`--thread-grid 4:4` is one point written twice."""
        rec = Z.summarise([_cell(a, 4, ["x", "x"]) for a in Z.ARMS], [],
                          rows=Z.MIN_ROWS, seed=42, repeats=2, thread_grid=(4, 4))
        self.assertEqual(rec["verdict"], "DEGENERATE")


class GridSeparatorSurvivesSbatchExport(unittest.TestCase):
    def test_colon_is_the_default_and_parses(self):
        src = PROBE.read_text()
        self.assertIn('default="1:2:4:8"', src)
        self.assertIn("[:,\\s]+", src.replace("\\\\", "\\"))

    def test_all_three_separators_parse_to_the_same_grid(self):
        import subprocess as sp
        for spec in ("1:2:4:8", "1,2,4,8", "1 2 4 8"):
            with self.subTest(spec=spec):
                r = sp.run([sys.executable, str(PROBE), "--mode", "driver", "--rows", "1000",
                            "--allow-small-rows", "--repeats", "1", "--thread-grid", spec],
                           capture_output=True, text=True)
                rec = json.loads(r.stdout)
                self.assertEqual(rec["thread_grid"], [1, 2, 4, 8], spec)

    def test_launcher_refuses_a_one_valued_grid_with_rc14(self):
        """The refusal, so a degenerate axis cannot produce a green run at all."""
        sh = (REPO / "nd-unfolding" / "run_determinism_probe.sh").read_text()
        self.assertIn("exit 14", sh)
        self.assertIn("MNV_THREAD_GRID:-1:2:4:8", sh)
        self.assertIn("comma-separated NAME=VALUE list", sh)


if __name__ == "__main__":
    unittest.main()
