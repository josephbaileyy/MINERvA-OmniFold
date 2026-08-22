"""Tests for mnv_guarded_run.py -- the OI-136 import-tree guard.

EVERY BEHAVIOURAL TEST RUNS A REAL SUBPROCESS, because the thing under test is an
exit code and an import resolution order, and an in-process test of either would be
testing the harness. The fixtures reproduce run 57266000_0's exact shape: two real
checkouts, a module present in BOTH, and an entrypoint that hardcodes an absolute
insert(0, ...) pointing at the wrong one.

THE FIRST TEST IS THE ONE THAT MATTERS: it asserts the fixture is a GENUINE hijack
without the guard (unguarded python loads the wrong module and exits 0) before
asserting the guard refuses it. A guard test whose fixture does not actually hijack
passes for the wrong reason -- that is BEN-class "the gate that cannot fail".
"""
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
GUARD = HERE.parent / "mnv_guarded_run.py"
REPO = HERE.parents[1]

sys.path.insert(0, str(HERE.parent))
import mnv_guarded_run as mgr  # noqa: E402


def make_checkout(base: pathlib.Path, name: str) -> pathlib.Path:
    root = base / name
    (root / "nd-unfolding").mkdir(parents=True)
    (root / "VALIDATION_LEDGER.md").write_text("# fixture ledger\n")
    return root


def write(path: pathlib.Path, text: str) -> pathlib.Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def run(*args, **kw):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    return subprocess.run([sys.executable, *[str(a) for a in args]],
                          capture_output=True, text=True, env=env, **kw)


class GuardFixture(unittest.TestCase):
    """Two checkouts, `victim` in both, entrypoint hardcoding the wrong one."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        tmp = pathlib.Path(self._tmp.name)
        self.good = make_checkout(tmp, "expected-tree")
        self.bad = make_checkout(tmp, "stale-tree")
        write(self.good / "nd-unfolding" / "victim.py", "MARK = 'RIGHT TREE'\n")
        write(self.bad / "nd-unfolding" / "victim.py", "MARK = 'WRONG TREE'\n")
        self.entry = write(
            self.good / "nd-unfolding" / "entry.py",
            "import sys\n"
            f"sys.path.insert(0, {str(self.bad / 'nd-unfolding')!r})\n"
            "import victim\n"
            "print('loaded:', victim.MARK)\n",
        )
        self.addCleanup(self._tmp.cleanup)


class TheFixtureReallyHijacks(GuardFixture):
    def test_unguarded_run_loads_the_wrong_tree_and_succeeds(self):
        """The control. If this passes cleanly the guard has nothing to prove."""
        cp = run(self.entry)
        self.assertEqual(cp.returncode, 0, cp.stderr)
        self.assertIn("WRONG TREE", cp.stdout)
        self.assertNotIn("RIGHT TREE", cp.stdout)


class GuardRefuses(GuardFixture):
    def test_violation_exits_3_and_names_module_origin_and_both_roots(self):
        cp = run(GUARD, "--expect-root", self.good, "--", self.entry)
        self.assertEqual(cp.returncode, mgr.VIOLATION_EXIT, cp.stdout + cp.stderr)
        self.assertIn("victim", cp.stderr)
        self.assertIn(str(self.bad), cp.stderr)
        self.assertIn(str(self.good), cp.stderr)
        self.assertNotIn("WRONG TREE", cp.stdout)

    def test_the_message_says_a_redeploy_will_not_fix_it(self):
        """The wrong repair is the expensive one; the message must foreclose it."""
        cp = run(GUARD, "--expect-root", self.good, "--", self.entry)
        self.assertIn("re-deploy will", cp.stderr)
        self.assertIn("PYTHONPATH", cp.stderr)

    def test_allow_makes_the_second_tree_explicit_rather_than_silent(self):
        cp = run(GUARD, "--expect-root", self.good, "--allow", self.bad, "--", self.entry)
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        self.assertIn("WRONG TREE", cp.stdout)


class GuardPassesWhatItShould(GuardFixture):
    def test_same_tree_import_runs_and_loads_the_right_module(self):
        entry = write(self.good / "nd-unfolding" / "ok.py",
                      "import sys, pathlib\n"
                      "sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))\n"
                      "import victim\n"
                      "print('loaded:', victim.MARK)\n")
        cp = run(GUARD, "--expect-root", self.good, "--", entry)
        self.assertEqual(cp.returncode, 0, cp.stderr)
        self.assertIn("RIGHT TREE", cp.stdout)

    def test_stdlib_and_site_packages_are_not_flagged(self):
        entry = write(self.good / "nd-unfolding" / "std.py",
                      "import json, re, argparse, unittest, email.parser\n"
                      "print('stdlib ok')\n")
        cp = run(GUARD, "--expect-root", self.good, "--", entry)
        self.assertEqual(cp.returncode, 0, cp.stderr)
        self.assertIn("stdlib ok", cp.stdout)

    def test_the_guard_actually_inspected_something(self):
        """Guards that inspect zero imports pass every test above vacuously."""
        entry = write(self.good / "nd-unfolding" / "count.py",
                      "import sys\n"
                      "g = [f for f in sys.meta_path if type(f).__name__ == 'GuardedPathFinder']\n"
                      "assert len(g) == 1, g\n"
                      "import json  # noqa: F401\n"
                      "print('checked:', g[0].checked > 0)\n")
        cp = run(GUARD, "--expect-root", self.good, "--", entry)
        self.assertEqual(cp.returncode, 0, cp.stderr)
        self.assertIn("checked: True", cp.stdout)


class ChildContract(GuardFixture):
    def test_child_exit_status_is_preserved_not_swallowed(self):
        entry = write(self.good / "nd-unfolding" / "boom.py", "import sys\nsys.exit(7)\n")
        cp = run(GUARD, "--expect-root", self.good, "--", entry)
        self.assertEqual(cp.returncode, 7, cp.stdout + cp.stderr)

    def test_argv_after_the_split_is_forwarded_verbatim_even_when_it_collides(self):
        entry = write(self.good / "nd-unfolding" / "argv.py",
                      "import sys\nprint('ARGV', sys.argv[1:])\n")
        cp = run(GUARD, "--expect-root", self.good, "--",
                 entry, "--expect-root", "NOPE", "--allow", "X", "--out", "f.root")
        self.assertEqual(cp.returncode, 0, cp.stderr)
        self.assertIn("ARGV ['--expect-root', 'NOPE', '--allow', 'X', '--out', 'f.root']",
                      cp.stdout)

    def test_argv0_and_dunder_file_are_the_script_like_direct_execution(self):
        entry = write(self.good / "nd-unfolding" / "who.py",
                      "import sys\nprint('ARGV0', sys.argv[0])\nprint('FILE', __file__)\n"
                      "print('NAME', __name__)\n")
        cp = run(GUARD, "--expect-root", self.good, "--", entry)
        self.assertIn(f"ARGV0 {entry}", cp.stdout)
        self.assertIn("who.py", cp.stdout)
        self.assertIn("NAME __main__", cp.stdout)

    def test_script_directory_is_on_sys_path_like_direct_execution(self):
        """runpy.run_path does NOT do this; differing silently would be the same bug."""
        write(self.good / "nd-unfolding" / "sibling.py", "VALUE = 'sibling ok'\n")
        entry = write(self.good / "nd-unfolding" / "implicit.py",
                      "import sibling\nprint(sibling.VALUE)\n")
        cp = run(GUARD, "--expect-root", self.good, "--", entry)
        self.assertEqual(cp.returncode, 0, cp.stderr)
        self.assertIn("sibling ok", cp.stdout)


class CannotCheckIsNotClean(GuardFixture):
    """EVERY ARM ASSERTS ITS `outcome`, NOT ONLY THE EXIT CODE. Four distinct conditions here all
    return CANNOT_CHECK_EXIT, so the code alone cannot say which one fired -- the same blindness
    that let B-4 quietly take over F-9's exit 3. Added when the refusal-site coverage gate below
    went red on its first run and named these three as uncontrolled."""

    def _cc_record(self, name, *args):
        # NOT `_outcome`: unittest.TestCase already owns `self._outcome` and shadowing
        # it makes every arm in this class die with '_Outcome object is not callable'.
        inv = pathlib.Path(self._tmp.name) / "cc" / f"{name}.jsonl"
        # `--inventory` FIRST, before the caller's args. Appending it put the flag AFTER the `--`,
        # where the wrapper forwards it to the child verbatim -- which is the documented behaviour
        # this file's own `test_argv_after_the_split_is_forwarded_verbatim...` pins, and it bit the
        # first version of this helper: no record was written and every arm died on a missing file.
        cp = run(GUARD, "--inventory", inv, *args)
        self.assertEqual(cp.returncode, mgr.CANNOT_CHECK_EXIT, cp.stdout + cp.stderr)
        return json.loads(inv.read_text().strip())

    def test_missing_split_exits_2(self):
        cp = run(GUARD, "--expect-root", self.good, self.entry)
        self.assertEqual(cp.returncode, mgr.CANNOT_CHECK_EXIT, cp.stdout + cp.stderr)
        self.assertIn("MANDATORY", cp.stderr)
        rec = self._cc_record("usage", "--expect-root", str(self.good), str(self.entry))
        self.assertEqual(rec["outcome"], "cannot-check:usage")
        self.assertEqual(rec["checked_provenance"], mgr.CHECKED_NOT_MEASURED)

    def test_nothing_after_the_split_exits_2(self):
        cp = run(GUARD, "--expect-root", self.good, "--")
        self.assertEqual(cp.returncode, mgr.CANNOT_CHECK_EXIT, cp.stderr)
        rec = self._cc_record("split", "--expect-root", str(self.good), "--")
        self.assertEqual(rec["outcome"], "cannot-check:nothing-after-split")

    def test_expect_root_that_is_not_a_checkout_exits_2_not_3(self):
        cp = run(GUARD, "--expect-root", self.good / "nd-unfolding", "--", self.entry)
        self.assertEqual(cp.returncode, mgr.CANNOT_CHECK_EXIT, cp.stdout + cp.stderr)
        self.assertNotEqual(cp.returncode, mgr.VIOLATION_EXIT)
        rec = self._cc_record("noroot", "--expect-root", str(self.good / "nd-unfolding"),
                            "--", str(self.entry))
        self.assertEqual(rec["outcome"], "cannot-check:expect-root-is-not-a-checkout")

    def test_missing_script_exits_2(self):
        cp = run(GUARD, "--expect-root", self.good, "--", self.good / "nope.py")
        self.assertEqual(cp.returncode, mgr.CANNOT_CHECK_EXIT, cp.stderr)
        rec = self._cc_record("noscript", "--expect-root", str(self.good), "--",
                            str(self.good / "nope.py"))
        self.assertEqual(rec["outcome"], "cannot-check:no-such-script")


class MarkerSemantics(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = pathlib.Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def test_markers_are_conjunctive_so_nd_unfolding_is_not_its_own_root(self):
        root = make_checkout(self.tmp, "co")
        self.assertTrue(mgr.is_checkout(root))
        self.assertFalse(mgr.is_checkout(root / "nd-unfolding"))

    def test_a_directory_with_one_marker_is_not_a_checkout(self):
        half = self.tmp / "half"
        (half / "nd-unfolding").mkdir(parents=True)
        self.assertFalse(mgr.is_checkout(half))

    def test_root_of_a_file_outside_every_checkout_is_none(self):
        loose = self.tmp / "loose" / "mod.py"
        write(loose, "\n")
        self.assertIsNone(mgr.checkout_root_of(str(loose), _cache={}))

    def test_innermost_checkout_wins_so_a_frozen_tree_resolves_to_itself(self):
        outer = make_checkout(self.tmp, "outer")
        inner = make_checkout(outer, "frozen-inner")
        mod = write(inner / "nd-unfolding" / "m.py", "\n")
        self.assertEqual(mgr.checkout_root_of(str(mod), _cache={}), str(inner))

    def test_the_real_repo_resolves_to_the_real_repo(self):
        self.assertEqual(mgr.checkout_root_of(str(GUARD), _cache={}), str(REPO))

    def test_agents_md_is_not_a_marker(self):
        """It was rewritten 2026-08-20, so it cannot recognise older frozen trees."""
        self.assertNotIn("AGENTS.md", mgr.MARKERS)


class TheSubprocessBoundaryIsNotCovered(unittest.TestCase):
    """PIN THE LIMIT, so a green guarded run is never read as more than it is.

    The guard wraps THIS interpreter's `PathFinder`. A child interpreter starts with a
    clean `sys.meta_path`, so a hijack that happens inside a subprocess is invisible to
    it. Both directions are asserted: in-process the guard fires, through a subprocess it
    does not. Asserting only the failure would leave "maybe the fixture is broken" open;
    asserting only the pass would leave the limit undocumented in the only place that
    cannot rot.

    THIS IS THE SHAPE OF THIS REPO'S ADOPTION PATH, NOT A CONTRIVANCE:
    `mii_adopt_unified_5d_stamped.py` resolves `adopt_unified_5d.py` from its own
    `__file__` and runs it as a subprocess on purpose, and `adopt_unified_5d.py` is one
    of the fail-open 59.
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        tmp = pathlib.Path(self._tmp.name)
        self.good = make_checkout(tmp, "expected-tree")
        self.bad = make_checkout(tmp, "stale-tree")
        write(self.good / "nd-unfolding" / "victim.py", "MARK = 'RIGHT TREE'\n")
        write(self.bad / "nd-unfolding" / "victim.py", "MARK = 'WRONG TREE'\n")
        # The CHILD carries the defect: an absolute insert(0, <other checkout>).
        write(self.good / "nd-unfolding" / "child.py",
              "import sys\n"
              f"sys.path.insert(0, {str(self.bad / 'nd-unfolding')!r})\n"
              "import victim\n"
              "print('CHILD-LOADED', victim.MARK)\n")
        # The PARENT is correct: it derives its own directory, exactly as the fix asks.
        self.parent_sub = write(
            self.good / "nd-unfolding" / "parent_sub.py",
            "import os, subprocess, sys\n"
            "_HERE = os.path.dirname(os.path.abspath(__file__))\n"
            "if _HERE not in sys.path: sys.path.insert(0, _HERE)\n"
            "raise SystemExit(subprocess.run(\n"
            "    [sys.executable, os.path.join(_HERE, 'child.py')]).returncode)\n")
        self.parent_in = write(
            self.good / "nd-unfolding" / "parent_in.py",
            "import os, runpy, sys\n"
            "_HERE = os.path.dirname(os.path.abspath(__file__))\n"
            "if _HERE not in sys.path: sys.path.insert(0, _HERE)\n"
            "runpy.run_path(os.path.join(_HERE, 'child.py'), run_name='__main__')\n")

    def tearDown(self):
        self._tmp.cleanup()

    def test_IN_PROCESS_the_guard_fires_which_proves_the_fixture_hijacks(self):
        p = run(GUARD, "--expect-root", self.good, "--", self.parent_in)
        self.assertEqual(p.returncode, mgr.VIOLATION_EXIT,
                         f"stdout:\n{p.stdout}\nstderr:\n{p.stderr}")
        self.assertIn("IMPORT TREE VIOLATION", p.stderr)
        self.assertNotIn("CHILD-LOADED", p.stdout)

    def test_THROUGH_A_SUBPROCESS_the_same_hijack_is_NOT_caught(self):
        """Exit 0 and the WRONG module loaded. Recorded so nobody assumes otherwise."""
        p = run(GUARD, "--expect-root", self.good, "--", self.parent_sub)
        self.assertEqual(p.returncode, 0,
                         f"stdout:\n{p.stdout}\nstderr:\n{p.stderr}")
        self.assertIn("CHILD-LOADED WRONG TREE", p.stdout)
        self.assertNotIn("IMPORT TREE VIOLATION", p.stderr)

    def test_the_docstring_says_so_where_a_caller_will_read_it(self):
        """A limit known only to a test is a limit callers will not know."""
        self.assertIn("DOES NOT CROSS A SUBPROCESS BOUNDARY", mgr.__doc__)


class ScriptContainment(unittest.TestCase):
    """B-4, 2026-08-22: the guard must refuse a SCRIPT that lives in another checkout.

    THE FIRST TEST IS THE CONTROL AND IT COMES FIRST ON PURPOSE. The entrypoint used here imports
    NOTHING from any repository -- which is the whole point, because that is the shape
    (`adopt_unified_5d.py`) for which the import guard has nothing to resolve and exits 0. If the
    unguarded arm did not really run the wrong tree's copy, the refusal below would be proving
    something else.
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        tmp = pathlib.Path(self._tmp.name)
        self.good = make_checkout(tmp, "expected-tree")
        self.bad = make_checkout(tmp, "forbidden-tree")
        # NO repository import anywhere in it. Only stdlib, and it announces which copy ran.
        body = ("import json  # stdlib only: nothing here is a repository import\n"
                "print('MARK', {mark!r})\n"
                "print('RANFILE', __file__)\n")
        self.good_copy = write(self.good / "nd-unfolding" / "noimports.py",
                               body.format(mark="RIGHT TREE"))
        self.bad_copy = write(self.bad / "nd-unfolding" / "noimports.py",
                              body.format(mark="WRONG TREE"))
        self.loose = write(tmp / "not-a-checkout" / "noimports.py",
                           body.format(mark="LOOSE COPY"))
        self.addCleanup(self._tmp.cleanup)

    def test_unguarded_the_forbidden_copy_really_runs_and_says_so(self):
        """The control. Two distinguishable copies, and the wrong one executes cleanly."""
        cp = run(self.bad_copy)
        self.assertEqual(cp.returncode, 0, cp.stderr)
        self.assertIn("MARK WRONG TREE", cp.stdout)
        self.assertIn(f"RANFILE {self.bad_copy}", cp.stdout)

    def test_the_import_half_of_the_guard_has_nothing_to_fire_on_here(self):
        """WHY B-4 IS NEEDED AT ALL, measured rather than argued.

        This entrypoint resolves ZERO repository origins, so the IMPORT half of the guard would
        have exited 0 no matter which checkout the file came from. That is the vacuity B-4 closes,
        and it is the measured shape of `adopt_unified_5d.py`.
        """
        inv = pathlib.Path(self._tmp.name) / "inv" / "vacuous.jsonl"
        cp = run(GUARD, "--expect-root", self.good, "--inventory", inv, "--", self.good_copy)
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        rec = json.loads(inv.read_text().strip())
        self.assertEqual(rec["repo_origin_count"], 0)
        self.assertTrue(rec["repo_origin_inventory_is_empty"])

    def test_a_script_in_another_checkout_is_refused_3(self):
        cp = run(GUARD, "--expect-root", self.good, "--", self.bad_copy)
        self.assertEqual(cp.returncode, mgr.VIOLATION_EXIT, cp.stdout + cp.stderr)
        self.assertIn("SCRIPT OUTSIDE THE EXPECTED TREE", cp.stderr)
        self.assertIn(str(self.bad), cp.stderr)
        self.assertIn(str(self.good), cp.stderr)

    def test_the_refusal_happens_before_the_script_produces_anything(self):
        """Ordering, not just an exit code: the script's own first stdout line never appears."""
        cp = run(GUARD, "--expect-root", self.good, "--", self.bad_copy)
        self.assertEqual(cp.returncode, mgr.VIOLATION_EXIT, cp.stdout + cp.stderr)
        self.assertNotIn("MARK", cp.stdout)
        self.assertNotIn("RANFILE", cp.stdout)

    def test_the_SAME_script_inside_expect_root_is_NOT_refused(self):
        """The other direction. A narrowing needs a test that it is silent where it should be."""
        cp = run(GUARD, "--expect-root", self.good, "--", self.good_copy)
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        self.assertIn("MARK RIGHT TREE", cp.stdout)
        self.assertIn(f"RANFILE {self.good_copy}", cp.stdout)

    def test_allow_does_NOT_launder_a_script_from_another_checkout(self):
        """--allow declares an IMPORT tree. It has never declared an EXECUTION tree."""
        cp = run(GUARD, "--expect-root", self.good, "--allow", self.bad, "--", self.bad_copy)
        self.assertEqual(cp.returncode, mgr.VIOLATION_EXIT, cp.stdout + cp.stderr)
        self.assertNotIn("MARK", cp.stdout)

    def test_a_script_outside_EVERY_checkout_is_not_refused_and_is_recorded_as_such(self):
        """The documented limit. `checkout_root_of` returns None: there is no other tree it came
        from, so there is nothing to refuse -- but the record says `null` rather than staying
        silent, because silence is what makes a limit un-auditable."""
        inv = pathlib.Path(self._tmp.name) / "inv" / "loose.jsonl"
        cp = run(GUARD, "--expect-root", self.good, "--inventory", inv, "--", self.loose)
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        self.assertIn("MARK LOOSE COPY", cp.stdout)
        self.assertIsNone(json.loads(inv.read_text().strip())["script_checkout_root"])


class TheInventoryIsThePositiveEvidence(GuardFixture):
    """P-1, 2026-08-22. `checked` was written at one line and read at none; a guarded production
    run emitted nothing that distinguished "inspected many imports, all clean" from "inspected
    nothing". These arms pin both halves of that distinction, because an exit code cannot carry it.
    """

    def _inv(self, name="inv.jsonl"):
        return pathlib.Path(self._tmp.name) / "run-scoped" / name

    def test_a_repository_import_is_recorded_with_its_origin_root_and_digest(self):
        entry = write(self.good / "nd-unfolding" / "uses_sibling.py",
                      "import victim\nprint('loaded:', victim.MARK)\n")
        inv = self._inv()
        cp = run(GUARD, "--expect-root", self.good, "--inventory", inv, "--", entry)
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        rec = json.loads(inv.read_text().strip())
        self.assertGreater(rec["checked"], 0)
        self.assertGreater(rec["repo_origin_count"], 0)
        self.assertFalse(rec["repo_origin_inventory_is_empty"])
        self.assertEqual(rec["repo_origins_outside_expect_root"], 0)
        self.assertTrue(rec["verdict"].startswith("REPOSITORY-ORIGINS-INSPECTED"))
        got = {o["fullname"]: o for o in rec["repo_origins"]}
        self.assertIn("victim", got)
        # The ORIGIN is asserted, never merely the exit code.
        self.assertEqual(got["victim"]["origin"],
                         str(self.good / "nd-unfolding" / "victim.py"))
        self.assertEqual(got["victim"]["checkout_root"], str(self.good))
        self.assertTrue(got["victim"]["under_expect_root"])
        expect = hashlib.sha256(
            (self.good / "nd-unfolding" / "victim.py").read_bytes()).hexdigest()
        self.assertEqual(got["victim"]["sha256"], expect)

    def test_an_entrypoint_with_NO_repository_import_is_EXPLICITLY_EMPTY_not_silent(self):
        """P-3. A green arm that saw nothing must be distinguishable from one that approved
        everything it saw, and an ABSENT key cannot make that distinction."""
        entry = write(self.good / "nd-unfolding" / "stdlib_only.py",
                      "import json, re  # noqa: F401\nprint('nothing repository-local here')\n")
        inv = self._inv("empty.jsonl")
        cp = run(GUARD, "--expect-root", self.good, "--inventory", inv, "--", entry)
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        rec = json.loads(inv.read_text().strip())
        self.assertIn("repo_origin_count", rec)               # PRESENT, not absent
        self.assertIn("repo_origin_inventory_is_empty", rec)  # PRESENT, not absent
        self.assertEqual(rec["repo_origin_count"], 0)
        self.assertTrue(rec["repo_origin_inventory_is_empty"])
        self.assertTrue(rec["verdict"].startswith("EMPTY-REPOSITORY-ORIGIN-SET"), rec["verdict"])
        self.assertGreater(rec["checked"], 0)   # it DID look; it found nothing repository-local
        self.assertIn("verdict=EMPTY-REPOSITORY-ORIGIN-SET", cp.stderr)

    def test_a_B4_REFUSAL_never_records_itself_as_an_EMPTY_GREEN_RUN(self):
        """FOUND BY RUNNING THE REAL N-1 ARM ON THE CLUSTER, 2026-08-22, not by a test.

        A script-containment refusal raises no `ImportTreeViolation`, so the verdict fell through
        to the empty-green string and the record of a refusal read "THE GUARD REFUSED NOTHING
        BECAUSE IT SAW NOTHING". Both clauses were false. The record of a red run must not be
        readable as the record of a vacuous green one -- that is the same conflation P-3 exists to
        prevent, reintroduced inside the field that prevents it.
        """
        other = make_checkout(pathlib.Path(self._tmp.name), "another-tree")
        stray = write(other / "nd-unfolding" / "stray.py", "print('should never run')\n")
        inv = self._inv("b4refusal.jsonl")
        cp = run(GUARD, "--expect-root", self.good, "--inventory", inv, "--", stray)
        self.assertEqual(cp.returncode, mgr.VIOLATION_EXIT, cp.stdout + cp.stderr)
        rec = json.loads(inv.read_text().strip())
        self.assertTrue(rec["outcome"].startswith("refused:script-outside-expect-root"))
        self.assertTrue(rec["verdict"].startswith("REFUSED"), rec["verdict"])
        self.assertNotIn("REFUSED NOTHING", rec["verdict"])
        self.assertNotEqual(rec["verdict"], mgr.VERDICT_EMPTY)
        self.assertNotIn("should never run", cp.stdout)

    def test_a_cannot_check_record_says_COULD_NOT_LOOK_and_not_EMPTY(self):
        inv = self._inv("cannotlook.jsonl")
        cp = run(GUARD, "--expect-root", self.good / "nd-unfolding",
                 "--inventory", inv, "--", self.entry)
        self.assertEqual(cp.returncode, mgr.CANNOT_CHECK_EXIT, cp.stdout + cp.stderr)
        rec = json.loads(inv.read_text().strip())
        self.assertIn("COULD NOT LOOK", rec["verdict"])
        self.assertNotEqual(rec["verdict"], mgr.VERDICT_EMPTY)

    def test_the_two_kinds_of_ZERO_are_distinguishable(self):
        """Ruling 20 makes `checked = 0` the EXPECTED value on the containment path, which is
        exactly when a defaulted zero passes unnoticed. Two states produce a zero and they are
        completely different evidence: the guard installed and resolved nothing, versus the guard
        was never installed because the run was refused first. `checked` alone cannot tell them
        apart, so it never carries the claim on its own -- the triple does.
        """
        other = make_checkout(pathlib.Path(self._tmp.name), "another-tree")
        stray = write(other / "nd-unfolding" / "stray.py", "print('never')\n")
        inv_a = self._inv("zero_not_measured.jsonl")
        cp = run(GUARD, "--expect-root", self.good, "--inventory", inv_a, "--", stray)
        self.assertEqual(cp.returncode, mgr.VIOLATION_EXIT, cp.stdout + cp.stderr)
        a = json.loads(inv_a.read_text().strip())

        entry = write(self.good / "nd-unfolding" / "nothing_at_all.py", "pass\n")
        inv_b = self._inv("zero_measured.jsonl")
        cp = run(GUARD, "--expect-root", self.good, "--inventory", inv_b, "--", entry)
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        b = json.loads(inv_b.read_text().strip())

        self.assertEqual(a["checked"], 0)
        self.assertEqual(a["checked_provenance"], mgr.CHECKED_NOT_MEASURED)
        self.assertFalse(a["guard_installed"])
        self.assertEqual(a["refusal_site"], mgr.SITE_SCRIPT_CONTAINMENT)

        self.assertEqual(b["checked_provenance"], mgr.CHECKED_MEASURED)
        self.assertTrue(b["guard_installed"])
        self.assertIsNone(b["refusal_site"])
        self.assertNotEqual(a["checked_provenance"], b["checked_provenance"])

    def test_the_refusal_SITE_is_a_field_because_exit_3_cannot_carry_it(self):
        """Every refusal here returns the same VIOLATION_EXIT. That is how B-4 silently invalidated
        F-9's import-specific expectation the day B-4 landed: both arms were "exit 3" and nothing in
        the artifact said which check refused."""
        other = make_checkout(pathlib.Path(self._tmp.name), "yet-another")
        stray = write(other / "nd-unfolding" / "s.py", "pass\n")
        inv_a = self._inv("site_b4.jsonl")
        a_rc = run(GUARD, "--expect-root", self.good, "--inventory", inv_a, "--", stray).returncode
        inv_b = self._inv("site_import.jsonl")
        b_rc = run(GUARD, "--expect-root", self.good, "--inventory", inv_b, "--",
                   self.entry).returncode
        self.assertEqual(a_rc, b_rc, "the two refusals are INDISTINGUISHABLE by exit code")
        a, b = (json.loads(x.read_text().strip()) for x in (inv_a, inv_b))
        self.assertEqual(a["refusal_site"], mgr.SITE_SCRIPT_CONTAINMENT)
        self.assertEqual(b["refusal_site"], mgr.SITE_IMPORT_RESOLUTION)
        self.assertNotEqual(a["refusal_site"], b["refusal_site"])
        self.assertNotEqual(a["outcome"], b["outcome"])

    def test_the_label_is_recorded_so_an_ARM_is_identifiable_from_its_artifact(self):
        """Two arms differing only in --expect-root are easy to confuse in a directory of records,
        and a distinction the reader has to reconstruct is not carried by the artifact."""
        inv = self._inv("labelled.jsonl")
        cp = run(GUARD, "--expect-root", self.good, "--inventory", inv,
                 "--label", "N-1 forbidden configuration", "--", self.entry)
        self.assertEqual(cp.returncode, mgr.VIOLATION_EXIT, cp.stdout + cp.stderr)
        self.assertEqual(json.loads(inv.read_text().strip())["label"],
                         "N-1 forbidden configuration")

    def test_the_two_green_verdicts_are_actually_different_strings(self):
        """If they were equal the whole distinction would be decorative."""
        self.assertNotEqual(mgr.VERDICT_INSPECTED, mgr.VERDICT_EMPTY)

    def test_a_REFUSED_run_also_writes_its_inventory(self):
        """A record that only appears on success cannot establish anything about a failure."""
        inv = self._inv("refused.jsonl")
        cp = run(GUARD, "--expect-root", self.good, "--inventory", inv, "--", self.entry)
        self.assertEqual(cp.returncode, mgr.VIOLATION_EXIT, cp.stdout + cp.stderr)
        rec = json.loads(inv.read_text().strip())
        self.assertTrue(rec["verdict"].startswith("REFUSED"))
        self.assertEqual(rec["violation"]["module"], "victim")
        self.assertEqual(rec["violation"]["found_root"], str(self.bad))
        self.assertEqual(rec["repo_origins_outside_expect_root"], 1)

    def test_a_child_that_calls_sys_exit_still_leaves_a_record(self):
        entry = write(self.good / "nd-unfolding" / "exiting.py",
                      "import victim, sys\nprint(victim.MARK)\nsys.exit(7)\n")
        inv = self._inv("exiting.jsonl")
        cp = run(GUARD, "--expect-root", self.good, "--inventory", inv, "--", entry)
        self.assertEqual(cp.returncode, 7, cp.stdout + cp.stderr)
        rec = json.loads(inv.read_text().strip())
        self.assertGreater(rec["repo_origin_count"], 0)
        self.assertTrue(rec["outcome"].startswith("child-systemexit"))

    def test_the_env_var_is_an_equal_route_to_the_flag(self):
        entry = write(self.good / "nd-unfolding" / "envroute.py", "import victim\n")
        inv = self._inv("env.jsonl")
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
                   MNV_GUARD_INVENTORY=str(inv))
        cp = subprocess.run([sys.executable, str(GUARD), "--expect-root", str(self.good),
                             "--", str(entry)], capture_output=True, text=True, env=env)
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        self.assertEqual(mgr.INVENTORY_ENV, "MNV_GUARD_INVENTORY")
        self.assertTrue(inv.is_file())

    def test_it_APPENDS_so_a_multi_process_run_keeps_every_record(self):
        entry = write(self.good / "nd-unfolding" / "twice.py", "import victim\n")
        inv = self._inv("append.jsonl")
        for _ in range(2):
            cp = run(GUARD, "--expect-root", self.good, "--inventory", inv, "--", entry)
            self.assertEqual(cp.returncode, 0, cp.stderr)
        lines = [l for l in inv.read_text().splitlines() if l.strip()]
        self.assertEqual(len(lines), 2, lines)
        self.assertNotEqual(json.loads(lines[0])["pid"], json.loads(lines[1])["pid"])

    def test_an_UNWRITABLE_inventory_downgrades_a_green_run_to_CANNOT_CHECK(self):
        """A run that emits no record must not read as a clean one. 2, never 0."""
        blocked = pathlib.Path(self._tmp.name) / "blocked"
        blocked.mkdir(mode=0o500)
        self.addCleanup(lambda: blocked.chmod(0o700))
        entry = write(self.good / "nd-unfolding" / "blockedinv.py", "import victim\n")
        cp = run(GUARD, "--expect-root", self.good, "--inventory", blocked / "x.jsonl",
                 "--", entry)
        self.assertEqual(cp.returncode, mgr.CANNOT_CHECK_EXIT, cp.stdout + cp.stderr)
        self.assertIn("INVENTORY WRITE FAILED", cp.stderr)

    def test_an_unwritable_inventory_does_NOT_downgrade_a_REFUSAL(self):
        """Exit 3 is the finding and it outranks the bookkeeping."""
        blocked = pathlib.Path(self._tmp.name) / "blocked2"
        blocked.mkdir(mode=0o500)
        self.addCleanup(lambda: blocked.chmod(0o700))
        cp = run(GUARD, "--expect-root", self.good, "--inventory", blocked / "x.jsonl",
                 "--", self.entry)
        self.assertEqual(cp.returncode, mgr.VIOLATION_EXIT, cp.stdout + cp.stderr)
        self.assertIn("IMPORT TREE VIOLATION", cp.stderr)
        self.assertIn("INVENTORY WRITE FAILED", cp.stderr)

    def test_no_inventory_flag_means_no_file_and_that_is_not_a_pass(self):
        """Stated as a test so the reviewer's F-4 has something to fail against: a run without
        `--inventory` produces no record, and a run with no record establishes nothing."""
        entry = write(self.good / "nd-unfolding" / "silent.py", "import victim\n")
        cp = run(GUARD, "--expect-root", self.good, "--", entry)
        self.assertEqual(cp.returncode, 0, cp.stderr)
        self.assertNotIn("[oi136] inventory:", cp.stderr)


class EveryRefusalSiteHasAControlThatNamesItsOutcome(unittest.TestCase):
    """THE RULE THAT WOULD HAVE CAUGHT B-4 INVALIDATING F-9 THE DAY B-4 LANDED.

    Every exit path in `mnv_guarded_run.py` that refuses or declines to look records an `outcome`
    string. Adding a check AHEAD of an existing one changes which site fires first, so every
    downstream control has to be re-derived -- and that re-derivation is a memory exercise unless
    something enumerates the sites and demands a control for each. This does the enumeration from
    the SOURCE and the demand from the TEST FILES, so a new refusal site with no control is red on
    the commit that adds it rather than on the review that misses it.

    It is a coverage check against the implementation, which is the instrument I did not have when
    P-4 went undisclosed in round 1: a list of the decisions I remember taking is not one of these.
    """

    #: Prefixes of dynamically-built outcomes. Their suffixes are runtime values, so the prefix is
    #: the whole of what a control can name.
    DYNAMIC = ("child-systemexit:", "child-exception:")

    @staticmethod
    def _outcomes():
        import re
        src = GUARD.read_text()
        lit = set(re.findall(r'"(refused:[a-z0-9:-]+)"', src))
        lit |= set(re.findall(r'"(cannot-check:[a-z0-9:-]+)"', src))
        lit |= set(re.findall(r'f"(child-[a-z]+):', src))
        return lit

    def _corpus(self):
        return "\n".join(p.read_text() for p in sorted(HERE.glob("test_*.py")))

    def test_the_enumeration_is_not_empty_and_finds_both_refusal_families(self):
        """Power arm. A regex that matched nothing would make the next test pass forever."""
        got = self._outcomes()
        self.assertGreaterEqual(len(got), 5, got)
        self.assertIn("refused:script-outside-expect-root", got)
        self.assertIn("refused:import-tree-violation", got)
        self.assertTrue(any(o.startswith("cannot-check:") for o in got), got)

    def test_every_outcome_string_is_NAMED_by_some_control(self):
        corpus = self._corpus()
        missing = sorted(o for o in self._outcomes() if o not in corpus)
        self.assertEqual(missing, [],
                         "these refusal outcomes have no control naming them; a new check added "
                         "ahead of an existing one silently re-routes the arms that used to reach "
                         f"it: {missing}")

    def test_every_refusal_SITE_constant_is_named_by_some_control(self):
        corpus = self._corpus()
        for name in ("SITE_SCRIPT_CONTAINMENT", "SITE_IMPORT_RESOLUTION"):
            self.assertIn(name, corpus, f"{name} has no control")

    def test_the_two_site_constants_are_distinct_and_neither_is_None(self):
        self.assertNotEqual(mgr.SITE_SCRIPT_CONTAINMENT, mgr.SITE_IMPORT_RESOLUTION)
        self.assertIsNotNone(mgr.SITE_SCRIPT_CONTAINMENT)
        self.assertIsNotNone(mgr.SITE_IMPORT_RESOLUTION)
        self.assertIsNone(mgr.SITE_NONE)


if __name__ == "__main__":
    unittest.main()
