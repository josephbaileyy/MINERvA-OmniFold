#!/usr/bin/env python3
"""Arms for `measure_m1_m6.py`'s canonical-root detector.

ROUND-7 `F-17(a)`. The instrument shipped with an exact-equality test and therefore reported FIVE
surviving literals on the canonical checkout where there are SEVEN — `bootstrap_nd.py` and
`seedscan_split.py` hold the root as a SUBPATH (`.../MINERvA-OmniFold/nd-unfolding`) and each feeds
`sys.path.insert(0, _ND)` with three repository modules straight after. Two of ten rows read
`literal=-` for files carrying an active rooted insert, and nothing disclosed the blind spot.

The instrument had no tests at all. That is the actual root cause: the same substring/exact-match
failure class was found and fixed in `m6` earlier the same day, in this same file, and the sibling
function four definitions above was never swept. These arms exist so the class cannot recur silently.

BOTH DIRECTIONS ARE PINNED. A guard needs an arm that it FIRES; a narrowing needs an arm that it does
NOT. The over-broad arm matters concretely: `MINERvA-OmniFold-Analysis-Note` is a real sibling
repository, and a bare `startswith` would report a hazard in a tree that has none.
"""
import ast
import contextlib
import datetime
import importlib.util
import io
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

_HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("mm", _HERE / "measure_m1_m6.py")
mm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mm)

ROOT = mm.CANONICAL_LITERAL


class TheCanonicalRootDetectorSeesBothForms(unittest.TestCase):

    def test_the_EXACT_form_is_detected(self):
        self.assertEqual(mm.canonical_form(ROOT), "exact")

    def test_the_SUBPATH_form_is_detected__the_round_7_defect(self):
        """The arm that fails against the shipped instrument."""
        self.assertEqual(mm.canonical_form(ROOT + "/nd-unfolding"), "subpath")
        self.assertEqual(mm.canonical_form(ROOT + "/2d-unfolding/baseline_flux/"), "subpath")

    def test_a_LONGER_SIBLING_path_is_NOT_matched__the_over_broad_direction(self):
        """`startswith` alone would call these hazards. They are different repositories."""
        for sibling in (ROOT + "-Analysis-Note", ROOT + "-gregor-pet2", ROOT + "2", ROOT + "_old"):
            with self.subTest(path=sibling):
                self.assertIsNone(mm.canonical_form(sibling))

    def test_unrelated_and_partial_paths_are_NOT_matched(self):
        for other in ("/pscratch/sd/j/josephrb", "/pscratch/sd/j/josephrb/k0r2/clean",
                      "MINERvA-OmniFold", "", "/"):
            with self.subTest(path=other):
                self.assertIsNone(mm.canonical_form(other))


class M1CountsWhatTheFilesActuallyCarry(unittest.TestCase):
    """Fixtures built from the PRODUCER's shapes -- the real forms these entrypoints use -- rather
    than from the rule, so a fixture cannot agree with the code by construction."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tree = pathlib.Path(self._tmp.name)
        nd = self.tree / "nd-unfolding"
        nd.mkdir(parents=True)
        # two real repository modules so "imports after the insert" can be non-zero
        (nd / "omnifold_nn_core.py").write_text("x = 1\n")
        (nd / "xsec_nd.py").write_text("y = 2\n")

    def _run(self, name, src):
        (self.tree / "nd-unfolding" / name).write_text(src)
        orig = mm.M1_FILES
        mm.M1_FILES = (f"nd-unfolding/{name}",)
        try:
            return mm.m1(self.tree)[0]
        finally:
            mm.M1_FILES = orig

    def test_the_SUBPATH_assignment_shape_is_counted_and_named(self):
        """bootstrap_nd.py's exact shape on the canonical checkout."""
        r = self._run("bootstrap_nd.py", f'''import sys
_ND="{ROOT}/nd-unfolding"
if _ND not in sys.path: sys.path.insert(0,_ND)
from omnifold_nn_core import omnifold_loop
import xsec_nd
''')
        self.assertEqual(len(r["literals"]), 1)
        self.assertEqual(r["literals"][0]["name"], "_ND")
        self.assertEqual(r["literals"][0]["form"], "subpath")
        self.assertEqual(r["first_insert"], 3)
        self.assertEqual(r["n_after"], 2)

    def test_the_EXACT_assignment_shape_is_counted(self):
        r = self._run("adopt.py", f'''import sys
_REPO = "{ROOT}"
sys.path.insert(0, _REPO + "/nd-unfolding")
''')
        # ONE literal, not two. `_REPO + "/nd-unfolding"` is a runtime CONCATENATION; the string
        # constant `"/nd-unfolding"` does not name the canonical root and is correctly not counted.
        # This arm's first draft expected two and was wrong -- recorded because the limitation is
        # real: THIS INSTRUMENT COUNTS LITERALS, NOT COMPUTED PATHS. A file that builds the canonical
        # root by concatenation or os.path.join would carry the hazard and show zero literals here.
        # No such construction exists in the ten M-1 files on either tree, checked; if one appears,
        # this instrument goes blind to it and the next arm below is where that would be caught.
        self.assertEqual([l["form"] for l in r["literals"]], ["exact"])
        self.assertEqual(r["literals"][0]["name"], "_REPO")

    def test_an_INLINE_literal_with_no_variable_is_still_counted(self):
        """The shipped version only looked at assignment right-hand sides, so a bare inline path
        was invisible even in its exact form."""
        r = self._run("inline.py", f'''import sys
sys.path.insert(0, "{ROOT}/nd-unfolding")
import xsec_nd
''')
        self.assertEqual(len(r["literals"]), 1)
        self.assertEqual(r["literals"][0]["name"], "<inline>")
        self.assertEqual(r["literals"][0]["form"], "subpath")

    def test_a_DERIVED_root_carries_NO_literal__silent_on_good(self):
        """The B-1 repair's shape. If this ever fails, the instrument reports a hazard in a repaired
        file, which is a wrong refusal and worse than the miss it was added for."""
        r = self._run("repaired.py", '''import sys
from pathlib import Path
_REPO = str(Path(__file__).resolve().parents[1])
sys.path.insert(0, _REPO + "/nd-unfolding")
import xsec_nd
''')
        self.assertEqual(r["literals"], [])
        self.assertIsNotNone(r["first_insert"])

    def test_a_SIBLING_repository_path_is_NOT_reported_as_a_hazard(self):
        r = self._run("sibling.py", f'''import sys
_OTHER = "{ROOT}-Analysis-Note"
sys.path.insert(0, _OTHER)
''')
        self.assertEqual(r["literals"], [])


class MeasurementIdentityIsCapturedByTheProducer(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tree = pathlib.Path(self._tmp.name)
        subprocess.run(["git", "init", "-b", "fixture-branch", str(self.tree)], check=True,
                       capture_output=True, text=True)
        subprocess.run(["git", "-C", str(self.tree), "config", "user.name", "Fixture"],
                       check=True)
        subprocess.run(["git", "-C", str(self.tree), "config", "user.email", "fixture@example"],
                       check=True)
        (self.tree / "tracked.txt").write_text("fixture\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(self.tree), "add", "tracked.txt"], check=True)
        subprocess.run(["git", "-C", str(self.tree), "commit", "-m", "fixture"], check=True,
                       capture_output=True, text=True)

    def measure(self):
        completed = subprocess.run(
            [sys.executable, str(_HERE / "measure_m1_m6.py"), "--tree", str(self.tree),
             "--label", "fixture", "--json"],
            check=True, capture_output=True, text=True)
        return json.loads(completed.stdout)

    def test_branch_and_measurement_interval_are_emitted(self):
        document = self.measure()
        self.assertEqual(document["branch_or_detached"],
                         {"state": "branch", "name": "fixture-branch"})
        clock = document["measurement_wall_clock"]
        started = datetime.datetime.strptime(clock["started_utc"], "%Y-%m-%dT%H:%M:%SZ")
        completed = datetime.datetime.strptime(clock["completed_utc"], "%Y-%m-%dT%H:%M:%SZ")
        self.assertLessEqual(started, completed)

    def test_detached_state_is_emitted_without_inventing_a_branch_name(self):
        subprocess.run(["git", "-C", str(self.tree), "switch", "--detach"], check=True,
                       capture_output=True, text=True)
        self.assertEqual(self.measure()["branch_or_detached"],
                         {"state": "detached", "name": None})

    def test_a_NON_CHECKOUT_is_reported_as_such_and_carries_no_name(self):
        """N5/M13 of the 2026-08-28 grade: the THIRD state the decision names, never produced.

        `branch_or_detached` has three outcomes and two of them had arms. A state that no test ever
        produces is a state whose emission nobody has seen, which is how `not-a-git-checkout` could
        have been deleted outright with the suite green.
        """
        with tempfile.TemporaryDirectory() as outside:
            plain = pathlib.Path(outside)
            completed = subprocess.run(
                [sys.executable, str(_HERE / "measure_m1_m6.py"), "--tree", str(plain),
                 "--label", "plain", "--json"],
                check=True, capture_output=True, text=True)
            document = json.loads(completed.stdout)
        self.assertEqual(document["branch_or_detached"],
                         {"state": "not-a-git-checkout", "name": None})

    def test_the_interval_is_TWO_clock_reads_and_not_ONE_STAMP_EMITTED_TWICE(self):
        """N3 of the 2026-08-28 grade. The arm above passes on `completed_utc = started_utc`.

        `utc_now()` has one-second precision, so a real run against a small fixture tree already
        emits equal endpoints -- indistinguishable from the mutation that collapses the interval and
        defeats the word "real" in surface 1's title. Asserting inequality against the real clock
        would be flaky; DRIVING the clock is not, and it pins that the two stamps come from two
        separate reads rather than one value assigned twice.
        """
        stamps = iter(["2026-01-01T00:00:00Z", "2026-01-01T00:00:07Z"])
        real_utc_now = mm.utc_now
        mm.utc_now = lambda: next(stamps)
        self.addCleanup(setattr, mm, "utc_now", real_utc_now)
        argv = sys.argv
        sys.argv = ["measure_m1_m6.py", "--tree", str(self.tree), "--label", "fixture", "--json"]
        self.addCleanup(setattr, sys, "argv", argv)
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            mm.main()
        clock = json.loads(buffer.getvalue())["measurement_wall_clock"]
        self.assertEqual(clock["started_utc"], "2026-01-01T00:00:00Z")
        self.assertEqual(clock["completed_utc"], "2026-01-01T00:00:07Z",
                         "completed_utc must be a SECOND read of the clock, not started_utc reused")


class FarEndShellFailsClosedAroundTheRepairedSurfaces(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.source = (_HERE / "measure_k0_farend_f1b_f17b.sh").read_text(encoding="utf-8")

    def test_a_failed_measurer_exits_before_the_loop_can_continue(self):
        loop = self.source[
            self.source.index('for pair in "deploy:$CODE_ROOT" "canonical:$CANON"; do'):
            self.source.index("MEASURER_POST=")]
        rc_check = loop.index('if [ "$rc" -ne 0 ]; then')
        refusal = loop.index("no later measurement or comparison was run", rc_check)
        exit_call = loop.index('exit "$rc"', refusal)
        self.assertLess(rc_check, refusal)
        self.assertLess(refusal, exit_call)

    def test_preserver_digest_is_bracketed_across_its_own_invocation(self):
        block = self.source[self.source.index("PRESERVER_PRE="):]
        before = block.index("PRESERVER_PRE=")
        invocation = block.index('"$PY" "$PRESERVER" --source')
        after = block.index("PRESERVER_POST=")
        mismatch = block.index('if [ "$PRESERVER_PRE" != "$PRESERVER_POST" ]; then')
        failed = block.index('if [ "$prc" -ne 0 ]; then')
        self.assertLess(before, invocation)
        self.assertLess(invocation, after)
        self.assertLess(after, mismatch)
        self.assertLess(mismatch, failed)

    def test_the_preserver_drift_branch_REFUSES_rather_than_merely_warning(self):
        """N2 of the 2026-08-28 grade: the ordering arm above asserts the WRAPPER, not the payload.

        Measured by the grader: replacing the drift branch's body with a bare `echo "NOTE: ..."` --
        downgrading an approved refusal to a warning that lets publication stand -- left all 100
        tests green. Surface 4's arm does not have this hole because it pins `exit "$rc"` literally,
        so this arm pins `exit 13` the same way.
        """
        block = self.source[
            self.source.index('if [ "$PRESERVER_PRE" != "$PRESERVER_POST" ]; then'):]
        body = block[:block.index("\nfi")]
        self.assertIn("exit 13", body,
                      "the preserver-drift branch must REFUSE, not warn and continue")


if __name__ == "__main__":
    unittest.main()
