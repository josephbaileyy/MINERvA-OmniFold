#!/usr/bin/env python3
"""`thread_environment_snapshot` captures the threading environment; it sets nothing.

It exists because `PREDECLARATION-20260916-B-estimator-and-coverage.md` §3 offers two remedies for
the incomplete pin set -- set the reduction-order variables, or capture their process-visible values
in every receipt -- and capturing is the one that cannot change a result. Without it, a
NOT-IDENTICAL repeat outcome is ambiguous between "the design cannot be pinned" and "the design was
never fully pinned".

⚠ THE TESTS RUN IN BOTH DIRECTIONS ON PURPOSE. A capture that only ever reported "unset" would pass
any absence-only test while being unable to notice a value, which is this repository's most-repeated
defect shape. So `test_reports_fully_pinned_when_they_ARE_set` is the one that gives the other five
their meaning.
"""
import os
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "nd-unfolding"))
import z_reproducibility as Z

ORDER = ("OMP_DYNAMIC", "OMP_SCHEDULE", "OMP_PROC_BIND", "OMP_PLACES")


def snapshot_with(env):
    """Run the capture in a CHILD with a controlled environment -- the parent's env is shared state
    and mutating it would make this test blame, or be blamed by, other tests."""
    code = ("import sys, json; sys.path.insert(0, %r); import z_reproducibility as Z; "
            "print(json.dumps(Z.thread_environment_snapshot()))" % str(REPO / "nd-unfolding"))
    e = {k: v for k, v in os.environ.items() if k not in Z._THREAD_ENV}
    e.update(env)
    out = subprocess.run([sys.executable, "-c", code], env=e, capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    import json
    return json.loads(out.stdout)


class ThreadEnvironmentSnapshot(unittest.TestCase):
    def test_reports_the_four_order_controls_unset_when_they_are(self):
        s = snapshot_with({})
        self.assertEqual(sorted(s["order_controls_unset"]), sorted(ORDER))
        self.assertFalse(s["order_controls_fully_pinned"])

    def test_reports_fully_pinned_when_they_ARE_set(self):
        """THE OTHER DIRECTION. Without this, a capture stuck at 'unset' passes everything else."""
        s = snapshot_with({"OMP_DYNAMIC": "FALSE", "OMP_SCHEDULE": "static",
                           "OMP_PROC_BIND": "true", "OMP_PLACES": "cores"})
        self.assertEqual(s["order_controls_unset"], [])
        self.assertTrue(s["order_controls_fully_pinned"])
        self.assertEqual(s["captured"]["OMP_SCHEDULE"], "static")

    def test_partial_pinning_names_exactly_what_is_missing(self):
        s = snapshot_with({"OMP_DYNAMIC": "FALSE", "OMP_PLACES": "cores"})
        self.assertEqual(sorted(s["order_controls_unset"]), ["OMP_PROC_BIND", "OMP_SCHEDULE"])
        self.assertFalse(s["order_controls_fully_pinned"])

    def test_unset_is_None_and_not_a_substituted_default(self):
        """A substituted default would make 'the runtime chose' indistinguishable from 'we chose'."""
        s = snapshot_with({})
        for k in ORDER:
            self.assertIsNone(s["captured"][k], f"{k} must be None when unset, not a default")

    def test_the_five_thread_COUNTS_are_captured_too(self):
        s = snapshot_with({"OMP_NUM_THREADS": "32", "MKL_NUM_THREADS": "2"})
        self.assertEqual(s["captured"]["OMP_NUM_THREADS"], "32")
        self.assertEqual(s["captured"]["MKL_NUM_THREADS"], "2")
        self.assertIsNone(s["captured"]["OPENBLAS_NUM_THREADS"])

    def test_it_disclaims_what_it_does_not_establish(self):
        s = snapshot_with({})
        self.assertTrue(s["asserts_nothing_about_defaults"])
        self.assertIn("4.452e-14", s["is_not_a_diagnosis_of"])

    def test_capture_does_NOT_mutate_the_environment(self):
        """Capture only. A function that set anything here would change a production run."""
        before = {k: os.environ.get(k) for k in Z._THREAD_ENV}
        Z.thread_environment_snapshot()
        self.assertEqual({k: os.environ.get(k) for k in Z._THREAD_ENV}, before)


class PinSetRatchet(unittest.TestCase):
    def test_the_repo_wide_claim_counts_SETTINGS_not_MENTIONS(self):
        """The claim is that nothing SETS the four reduction-order controls.

        ⚠ THE FIRST VERSION OF THIS TEST COUNTED MENTIONS AND IMMEDIATELY FAILED -- because the
        capture module and this file NAME all four, so adding the capture made "zero occurrences
        repo-wide" false while changing nothing about whether anything sets them. The detector was
        right to break and the pattern was wrong: a variable named in a capture list is not a
        variable assigned in an execution environment. Counting assignments is both the correct
        measurement and immune to its own repair.

        The positive control is not optional. An absence claim needs proof the search can find
        anything at all, or a broken pattern reads as a clean sweep.
        """
        def assignments(names):
            # shell `export X=` / `X=`, and python os.environ["X"] = / .setdefault("X",
            pat = "|".join(
                [rf'(^|[^A-Za-z_]){n}=' for n in names]
                + [rf'environ\[.{n}.\]\s*=' for n in names]
                + [rf'environ\.setdefault\(.{n}.' for n in names])
            r = subprocess.run(["git", "grep", "-c", "-I", "-E", pat],
                               cwd=REPO, capture_output=True, text=True)
            return {l.rsplit(":", 1)[0]: int(l.rsplit(":", 1)[1])
                    for l in r.stdout.splitlines() if ":" in l}

        control = assignments(["OMP_NUM_THREADS"])
        self.assertGreater(sum(control.values()), 5,
                           "positive control found no OMP_NUM_THREADS ASSIGNMENT -- pattern broken")
        found = assignments(list(ORDER))
        self.assertEqual(found, {},
                         f"something now ASSIGNS a reduction-order control: {found}. If they have "
                         f"been deliberately pinned that is good news, and this ratchet should be "
                         f"updated deliberately rather than silenced.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
