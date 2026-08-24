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
    def test_missing_split_exits_2(self):
        cp = run(GUARD, "--expect-root", self.good, self.entry)
        self.assertEqual(cp.returncode, mgr.CANNOT_CHECK_EXIT, cp.stdout + cp.stderr)
        self.assertIn("MANDATORY", cp.stderr)

    def test_nothing_after_the_split_exits_2(self):
        cp = run(GUARD, "--expect-root", self.good, "--")
        self.assertEqual(cp.returncode, mgr.CANNOT_CHECK_EXIT, cp.stderr)

    def test_expect_root_that_is_not_a_checkout_exits_2_not_3(self):
        cp = run(GUARD, "--expect-root", self.good / "nd-unfolding", "--", self.entry)
        self.assertEqual(cp.returncode, mgr.CANNOT_CHECK_EXIT, cp.stdout + cp.stderr)
        self.assertNotEqual(cp.returncode, mgr.VIOLATION_EXIT)

    def test_missing_script_exits_2(self):
        cp = run(GUARD, "--expect-root", self.good, "--", self.good / "nope.py")
        self.assertEqual(cp.returncode, mgr.CANNOT_CHECK_EXIT, cp.stderr)


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


if __name__ == "__main__":
    unittest.main()


# =================================================================================
# THE LOADED-CHECKOUT INVENTORY (promoted 2026-08-23 from the OI-126 lane's probe).
#
# The instrument was specified and measured by another lane inside a probe, and
# reimplemented here from the SPEC rather than copied, so that agreement between the
# two is a reproduction rather than a duplicate. The probe's measured output is
# recorded in `TheProbeMeasurement` below, with its provenance, because a figure
# quoted without its measurement point is not reproducible -- the count is a function
# of WHERE in the program the walk runs, so the SET is the invariant and the count is
# not.
#
# WHAT THESE TESTS ARE FOR, IN PB-16'S TERMS. The emission is an addition to a tool
# whose refusal behaviour other lanes route compute through, so "purely additive" is
# itself a narrowing claim and gets its own arm: `TheRefusalIsUnchanged` asserts the
# gate still fires and still ignores each case the module docstring names, WITH the
# emission present. `TheEmissionCannotFailARun` is the other direction -- a receipt
# that can fail a run is not a receipt.
# =================================================================================

INV = "[oi136-inv]"


def inventory(stderr: str):
    """Parse the emission back into {root: (label, count, [module names])}, + totals.

    Parsed from the PRODUCED text rather than from a format constant, so a change to
    the emission that these tests do not follow shows up as a parse failure instead of
    as a silently empty assertion.
    """
    rows, total, distinct = {}, None, None
    head = f"{INV}   ["
    for line in stderr.splitlines():
        if line.startswith(head):
            label, rest = line[len(head):].split("] ", 1)
            root, rest = rest.split("  (", 1)
            count, names = rest.split(") ", 1)
            rows[root] = (label, int(count), sorted(n for n in names.split(", ") if n))
        elif line.startswith(f"{INV} modules loaded from inside a checkout:"):
            body = line.split(":", 1)[1]
            total = int(body.split()[0])
            distinct = int(body.rsplit(":", 1)[1])
    return rows, total, distinct


def only_child_roots(rows, guard_root):
    """Every root except the one this wrapper itself was loaded from.

    The wrapper lives inside a checkout, so its own root is ALWAYS present and is not a
    finding. In production it coincides with `--expect-root` and there is one row; in
    these fixtures `--expect-root` is a tmpdir and there are two. Isolating it here
    keeps the fixture's arithmetic honest instead of hiding a term.
    """
    return {r: v for r, v in rows.items() if r != guard_root}


GUARD_ROOT = mgr.checkout_root_of(str(GUARD))


class TenModuleFixture(unittest.TestCase):
    """One checkout, four explicit imports pulling six more -- the probe's shape.

    Built from the PRODUCER: the checkout is made by `make_checkout`, the same helper
    every other fixture in this file uses, so the marker pair under test is the one the
    fixture actually writes and not a literal restated from `is_checkout`.
    """

    EXPLICIT = ("alpha", "beta", "gamma", "delta")
    TRANSITIVE = ("a1", "a2", "b1", "d1", "g1", "g2")

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        tmp = pathlib.Path(self._tmp.name)
        self.tree = make_checkout(tmp, "one-tree")
        nd = self.tree / "nd-unfolding"
        for leaf in self.TRANSITIVE:
            write(nd / f"{leaf}.py", f"NAME = {leaf!r}\n")
        write(nd / "alpha.py", "import a1, a2\n")
        write(nd / "beta.py", "import b1\n")
        write(nd / "gamma.py", "import g1, g2\n")
        write(nd / "delta.py", "import d1\n")
        self.entry = write(nd / "entry.py",
                           "import " + ", ".join(self.EXPLICIT) + "\n"
                           "print('CHILD OK')\n")

    def go(self, *extra):
        cp = run(GUARD, "--expect-root", self.tree, *extra, "--", self.entry)
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        return cp


class TheProbeMeasurement(TenModuleFixture):
    """Reproduce the figure the OI-126 lane measured with its own implementation.

    THE PROBE'S MEASUREMENT, and its provenance, because it changes how much this is
    worth. Reported by the OI-126 lane 2026-08-23 from an untracked scratch probe
    (`/pscratch/sd/j/josephrb/oi126_r1r3_work/split_probe.py`, output in
    `R5_SPLIT_PROBE.json`).

    THE MEASUREMENT IS NOT IN ANY COMMIT AND IS NOT EXPECTED TO BE. Three commits are
    adjacent to it and NONE of them carries it; the distinction is the point, so the
    citations are split rather than collapsed onto whichever is newest:

      68f979fe   the CORRECTION THAT MOTIVATED the instrument -- verified present as
                 `CORRECTION_20260823_my_OI136_claim_was_wrong.instrument_added` in both
                 the R1 and R3 receipts. Prose. Carries no measured output.
      9a881c03   the R5 receipt, which records THIS promotion at `7054426a` and
                 attributes the by-construction caveat below. **IT ALSO SPELLS THE
                 FIGURE "10 modules, 1 distinct root" IN PROSE, AND THAT IS NOT A
                 RECEIPT OF THE MEASUREMENT** -- no command, cwd, interpreter, module
                 set or exit status, and no reference to `R5_SPLIT_PROBE.json`. Anyone
                 grepping for the figure lands here and gets a confident hit on a
                 citation that cannot support it. Cite it for the ROUTING, never for
                 the number.
      (none)     the measured output itself. The scratch file became unretrievable when
                 the NERSC certificate expired 2026-08-23T20:22:13Z, and the measuring
                 lane declined to transcribe the figure from memory into a receipt --
                 which is the right call and the reason this stays a scratch
                 measurement rather than a live result.

    The emitted lines, as reported:

        [probe] loaded modules inside a checkout: 10
        [probe] distinct checkout roots: ['<CANONICAL-CLUSTER-ROOT>']

    -- the root is NOT SPELLED HERE, and that is not squeamishness. The OI-136 probe
    counts `.py` files containing that literal, so a test quoting it joins the
    population the ratchet beside this file guards, exactly as
    `test_oi136_failopen_inventory_ratchet.py`'s docstring warns. Measured: writing it
    out moved the probe's candidate count by one and put this file in the list.

    ten modules: annealed_estimator, atomic_write, extract_fullevent_fps,
    fullevent_fps_dataloader, omnifold, omnifold.dataloader, omnifold.net,
    omnifold.omnifold, omnifold.utils, train_fullevent_nominal -- four imported
    explicitly, six transitively.

    TWO THINGS THAT MEASUREMENT CANNOT DO, RECORDED HERE RATHER THAN GLOSSED:

    (1) IT WAS SINGLE-ROOT BY CONSTRUCTION, NOT BY MEASUREMENT. The probe script sat
        outside every checkout and `PYTHONPATH` named exactly one, so there was no
        second checkout for it to find. Reproducing it therefore validates the
        ENUMERATION and says nothing about the DISCRIMINATION -- a stub returning 10
        and one hardcoded root would pass it. `TheDefectMutationFires` is the arm that
        can fail for the right reason, and it is the load-bearing one.

    (2) THE COUNT IS MEASUREMENT-POINT DEPENDENT. The probe walked `sys.modules` inline
        right after its imports; this walks it when the wrapped script has finished. On
        the same configuration a later walk legitimately returns a larger number. So
        the count is asserted only against a fixture whose measurement point is fixed
        here, and the SET is what carries across.

    CONFIRMED BY THE ORIGINAL IMPLEMENTER 2026-08-23, which is what makes this a
    reproduction and not two programs agreeing by luck: the probe's 10 and this
    fixture's 11 differ by EXACTLY the `__main__` term and nothing else. Its `croot()`
    returned None for `__main__` because the probe sat outside every checkout; this
    wrapper sits inside one. Two host programs, one enumeration.
    """

    def test_the_child_tree_contributes_ten_modules_under_one_root(self):
        rows, total, distinct = inventory(self.go().stderr)
        child = only_child_roots(rows, GUARD_ROOT)
        self.assertEqual(list(child), [str(self.tree)], rows)
        self.assertEqual(child[str(self.tree)][1], 10, child)
        self.assertEqual(total, 11)      # ten + this wrapper's own __main__
        self.assertEqual(distinct, 2)    # the child's tree and this wrapper's

    def test_the_module_SET_matches_and_not_merely_the_count(self):
        """The lane's own caveat: compare the set, because the count moves."""
        rows, _, _ = inventory(self.go().stderr)
        self.assertEqual(rows[str(self.tree)][2],
                         sorted(self.EXPLICIT + self.TRANSITIVE))

    def test_the_second_root_is_this_wrapper_itself_and_is_labelled_as_such(self):
        """The one term the probe's fixture could not have, named rather than netted.

        The probe ran from outside every checkout; this runs from inside one, because
        the instrument now lives in a tool that is itself a repo file. That is a real
        difference between the two host programs and not a discrepancy between the two
        implementations -- so it is accounted for exactly (one module, `__main__`) and
        tagged in the output, rather than subtracted quietly.
        """
        rows, _, _ = inventory(self.go().stderr)
        self.assertIn(GUARD_ROOT, rows)
        self.assertEqual(rows[GUARD_ROOT][2], ["__main__"])
        self.assertIn("this-guard", rows[GUARD_ROOT][0])

    def test_the_wrapped_script_is_not_itself_counted(self):
        """`runpy` restores the real `__main__` before the emission runs.

        Pinned because it is the difference between "10" and "11" and would otherwise
        look like an off-by-one in whichever implementation someone checked second.
        """
        rows, _, _ = inventory(self.go().stderr)
        self.assertNotIn("entry", rows[str(self.tree)][2])


class TheDefectMutationFires(unittest.TestCase):
    """PB-16, direction one: a run that GENUINELY loads two checkouts emits two roots.

    Manufactured in a subprocess against real files on disk -- two checkouts, a module
    imported out of each -- rather than by handing the walker a synthetic `sys.modules`.
    A fixture assembled in memory would test the dict comprehension; this tests the
    thing the instrument exists to answer.
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        tmp = pathlib.Path(self._tmp.name)
        self.first = make_checkout(tmp, "first-tree")
        self.second = make_checkout(tmp, "second-tree")
        write(self.first / "nd-unfolding" / "here.py", "NAME = 'first'\n")
        write(self.second / "nd-unfolding" / "there.py", "NAME = 'second'\n")
        self.entry = write(
            self.first / "nd-unfolding" / "entry.py",
            "import sys\n"
            f"sys.path.insert(0, {str(self.second / 'nd-unfolding')!r})\n"
            "import here, there\n"
            "print('LOADED BOTH')\n",
        )

    def test_two_checkouts_produce_two_child_roots_naming_both_trees(self):
        cp = run(GUARD, "--expect-root", self.first, "--allow", self.second,
                 "--", self.entry)
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        self.assertIn("LOADED BOTH", cp.stdout)
        rows, _, _ = inventory(cp.stderr)
        child = only_child_roots(rows, GUARD_ROOT)
        self.assertEqual(sorted(child), sorted([str(self.first), str(self.second)]))
        self.assertEqual(child[str(self.first)][2], ["here"])
        self.assertEqual(child[str(self.second)][2], ["there"])

    def test_the_second_tree_is_labelled_NOT_expect_root(self):
        """Two roots is not the finding; WHICH two is. An unlabelled row is a number."""
        cp = run(GUARD, "--expect-root", self.first, "--allow", self.second,
                 "--", self.entry)
        rows, _, _ = inventory(cp.stderr)
        self.assertEqual(rows[str(self.second)][0], "NOT expect-root")
        self.assertIn("expect-root", rows[str(self.first)][0])

    def test_more_than_one_checkout_is_announced_and_still_exits_zero(self):
        """The announcement must not be mistaken for the refusal it deliberately isn't."""
        cp = run(GUARD, "--expect-root", self.first, "--allow", self.second,
                 "--", self.entry)
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        self.assertIn("MORE THAN ONE CHECKOUT IS LOADED", cp.stderr)
        self.assertNotIn("IMPORT TREE VIOLATION", cp.stderr)


class TheInnocentMutationStaysGreen(TenModuleFixture):
    """PB-16, direction two: a clean single-root run emits ONE root and does not refuse.

    Two arms, because the fixture and production differ in one term. In these fixtures
    `--expect-root` is a tmpdir and this wrapper is not inside it, so the honest
    single-root statement is about the CHILD's roots. The second arm removes that
    difference by pointing `--expect-root` at the real checkout the wrapper lives in --
    which is the production configuration, where the whole inventory is one row.
    """

    def test_one_child_root_and_no_refusal(self):
        cp = self.go()
        rows, _, _ = inventory(cp.stderr)
        self.assertEqual(len(only_child_roots(rows, GUARD_ROOT)), 1, rows)
        self.assertNotIn("IMPORT TREE VIOLATION", cp.stderr)
        self.assertIn("CHILD OK", cp.stdout)

    def test_production_shape_is_exactly_one_root_in_total(self):
        """Guard and script inside the SAME checkout: `distinct checkout roots: 1`.

        Run against a copy of this file placed inside the fixture checkout, asserted
        byte-identical first, because that is what production actually does --
        `sbatch_gate5_data_only_train_array.sh:115` sets `GUARD=${CODE_ROOT}/...`, so
        the wrapper a deployed run executes is the deployed tree's own copy and its
        root IS `--expect-root`. Using the repo's copy against a tmpdir `--expect-root`
        would test a configuration no launcher uses, and writing a probe script into
        the repo to avoid that would put an untracked file under the working tree the
        OI-136 ratchet walks.
        """
        deployed = self.tree / "nd-unfolding" / "mnv_guarded_run.py"
        deployed.write_bytes(GUARD.read_bytes())
        self.assertEqual(deployed.read_bytes(), GUARD.read_bytes())
        cp = run(deployed, "--expect-root", self.tree, "--", self.entry)
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        rows, total, distinct = inventory(cp.stderr)
        self.assertEqual(distinct, 1, rows)
        self.assertEqual(list(rows), [str(self.tree)])
        self.assertEqual(rows[str(self.tree)][0], "expect-root,this-guard")
        self.assertEqual(total, 11)  # the ten, plus the deployed wrapper's __main__
        self.assertNotIn("MORE THAN ONE CHECKOUT IS LOADED", cp.stderr)


class TheRefusalIsUnchanged(GuardFixture):
    """"Purely additive" is itself a NARROWING claim, so it gets its own arm (PB-16).

    A does-not-fire control cannot distinguish "correctly scoped" from "nothing covers
    this any more". So this class does not merely assert that the emission fires no
    refusals -- it re-asserts, with the emission present, that the GATE still fires
    where it did and still ignores exactly what the module docstring says it ignores.
    The ignore cases are taken from the docstring's own sentence, not from reading the
    code:

        "The stdlib, site-packages, conda and any path outside a checkout are IGNORED"

    plus the subprocess boundary, which the docstring says it deliberately does not
    cross. Each gets an arm below; `conda` gets the note it needs rather than a claim.
    """

    def test_a_genuine_import_tree_violation_still_exits_3_with_the_same_banner(self):
        cp = run(GUARD, "--expect-root", self.good, "--", self.entry)
        self.assertEqual(cp.returncode, mgr.VIOLATION_EXIT, cp.stdout + cp.stderr)
        self.assertIn("IMPORT TREE VIOLATION", cp.stderr)
        self.assertIn("victim", cp.stderr)
        self.assertIn(str(self.bad), cp.stderr)
        self.assertNotIn("WRONG TREE", cp.stdout)

    def test_the_refusal_still_precedes_the_receipt_in_the_output(self):
        """The gate speaks first. A reader scanning stderr must not meet the inventory
        before the verdict, or the receipt reads as the finding."""
        cp = run(GUARD, "--expect-root", self.good, "--", self.entry)
        self.assertLess(cp.stderr.index("IMPORT TREE VIOLATION"), cp.stderr.index(INV))

    def test_a_refusal_says_the_blocked_module_is_absent_from_its_own_inventory(self):
        """Otherwise a one-root inventory beside a two-root refusal reads as a
        contradiction between the two halves of the same tool."""
        cp = run(GUARD, "--expect-root", self.good, "--", self.entry)
        self.assertIn("THE RUN WAS REFUSED", cp.stderr)
        rows, _, _ = inventory(cp.stderr)
        self.assertNotIn(str(self.bad), rows)
        self.assertNotIn("victim", sum((v[2] for v in rows.values()), []))

    def test_stdlib_is_still_ignored_and_is_absent_from_the_inventory(self):
        """Docstring case 1. Not refused, AND not reported -- the second half matters:
        an inventory listing every stdlib module would be the noise that makes people
        switch the whole tool off, which is the docstring's stated reason for the
        ignore in the first place."""
        entry = write(self.good / "nd-unfolding" / "std.py",
                      "import json, os, textwrap\nprint('stdlib ok')\n")
        cp = run(GUARD, "--expect-root", self.good, "--", entry)
        self.assertEqual(cp.returncode, 0, cp.stderr)
        rows, _, _ = inventory(cp.stderr)
        names = sum((v[2] for v in rows.values()), [])
        for m in ("json", "os", "textwrap"):
            self.assertNotIn(m, names)

    def test_site_packages_is_still_ignored_and_absent(self):
        """Docstring case 2, exercised against this interpreter's REAL purelib rather
        than a directory named `site-packages`, since the rule under test is "walk up
        and find both markers", not a path-name rule."""
        import sysconfig
        purelib = pathlib.Path(sysconfig.get_paths()["purelib"])
        installed = sorted(d.name for d in purelib.iterdir()
                           if (d / "__init__.py").is_file() and not d.name.startswith("_"))
        self.assertTrue(installed, f"no importable package in {purelib}; arm is vacuous")
        victim = installed[0]
        entry = write(self.good / "nd-unfolding" / "sp.py",
                      f"import {victim}\nprint('site ok')\n")
        cp = run(GUARD, "--expect-root", self.good, "--", entry)
        self.assertEqual(cp.returncode, 0, cp.stderr)
        self.assertIsNone(mgr.checkout_root_of(str(purelib / victim / "__init__.py")))
        rows, _, _ = inventory(cp.stderr)
        self.assertNotIn(victim, sum((v[2] for v in rows.values()), []))

    def test_conda_is_the_same_mechanism_as_site_packages_not_a_separate_one(self):
        """Docstring case 3, and the honest form of it.

        `conda` is not a distinct code path: `checkout_root_of` has exactly one rule --
        walk up until both markers are present -- so a conda prefix is ignored for the
        same reason site-packages is, and there is nothing separate to fire on. This
        arm therefore does not claim to cover conda by name; it asserts the claim it
        can, that the two resolve identically. On THIS interpreter they are literally
        the same directory tree, which the assertion records; where they are not, the
        `outside a checkout` arm below is what covers it and this arm says so rather
        than leaving the case uncovered and untested-looking.
        """
        import sysconfig
        purelib = sysconfig.get_paths()["purelib"]
        self.assertIsNone(mgr.checkout_root_of(purelib + "/anything.py"))
        self.assertIsNone(mgr.checkout_root_of(sys.prefix + "/lib/anything.py"))

    def test_a_path_outside_every_checkout_is_still_ignored_and_absent(self):
        """Docstring case 4, and the general one the other three are instances of.

        A directory with NEITHER marker -- built by omitting what `make_checkout`
        writes, so the fixture is derived from the producer of checkouts rather than
        from `is_checkout`."""
        plain = pathlib.Path(self._tmp.name) / "not-a-checkout"
        plain.mkdir()
        write(plain / "loose.py", "NAME = 'loose'\n")
        entry = write(self.good / "nd-unfolding" / "out.py",
                      "import sys\n"
                      f"sys.path.insert(0, {str(plain)!r})\n"
                      "import loose\nprint('outside ok')\n")
        cp = run(GUARD, "--expect-root", self.good, "--", entry)
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        self.assertIn("outside ok", cp.stdout)
        rows, _, _ = inventory(cp.stderr)
        self.assertNotIn("loose", sum((v[2] for v in rows.values()), []))

    def test_cannot_check_exits_still_emit_nothing_because_nothing_ran(self):
        """Exit 2 means the tool could not look. An inventory there would be a receipt
        for a run that never started, which is the `2 is deliberately not 3` confusion
        one level down."""
        for args in ((GUARD, "--expect-root", self.good, self.entry),
                     (GUARD, "--expect-root", self.good, "--"),
                     (GUARD, "--expect-root", self.bad / "nope", "--", self.entry),
                     (GUARD, "--expect-root", self.good, "--", self.good / "ghost.py")):
            cp = run(*args)
            self.assertEqual(cp.returncode, mgr.CANNOT_CHECK_EXIT, cp.stdout + cp.stderr)
            self.assertNotIn(INV, cp.stderr)
            self.assertNotIn(INV, cp.stdout)


class TheEmissionCannotFailARun(GuardFixture):
    """The other direction of the additive constraint: a receipt may not fail a run.

    Mutations are manufactured in the CHILD, in a real subprocess, against the real
    installed guard -- reaching the wrapper's module namespace through the finder it
    installed in `sys.meta_path`. Patching `mgr` in this process would test this
    process.
    """

    REACH = ("g = [f for f in sys.meta_path "
             "     if type(f).__name__ == 'GuardedPathFinder'][0]\n"
             "gmod = type(g).find_spec.__globals__\n")

    def test_a_module_whose_dunder_file_raises_does_not_lose_the_inventory(self):
        entry = write(self.good / "nd-unfolding" / "poison.py",
                      "import sys\n"
                      "class Boom:\n"
                      "    @property\n"
                      "    def __file__(self):\n"
                      "        raise RuntimeError('detonated')\n"
                      "sys.modules['poison_mod'] = Boom()\n"
                      "import victim\n"
                      "print('SURVIVED')\n")
        cp = run(GUARD, "--expect-root", self.good, "--", entry)
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        self.assertIn("SURVIVED", cp.stdout)
        self.assertNotIn("EMISSION FAILED", cp.stderr)
        rows, _, _ = inventory(cp.stderr)
        self.assertIn("victim", sum((v[2] for v in rows.values()), []))

    def test_an_emission_that_raises_leaves_a_passing_run_passing(self):
        entry = write(self.good / "nd-unfolding" / "breakit.py",
                      "import sys\n" + self.REACH +
                      "def boom(*a, **k):\n"
                      "    raise RuntimeError('inventory exploded')\n"
                      "gmod['loaded_checkout_roots'] = boom\n"
                      "print('CHILD FINISHED')\n")
        cp = run(GUARD, "--expect-root", self.good, "--", entry)
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        self.assertIn("CHILD FINISHED", cp.stdout)
        self.assertIn("INVENTORY EMISSION FAILED", cp.stderr)
        self.assertIn("NOT a gate failure", cp.stderr)

    def test_an_emission_that_raises_leaves_a_REFUSED_run_refused(self):
        """The mutation must not be able to launder an exit 3 into anything else."""
        entry = write(self.good / "nd-unfolding" / "breakrefuse.py",
                      "import sys\n" + self.REACH +
                      "def boom(*a, **k):\n"
                      "    raise RuntimeError('inventory exploded')\n"
                      "gmod['loaded_checkout_roots'] = boom\n"
                      f"sys.path.insert(0, {str(self.bad / 'nd-unfolding')!r})\n"
                      "import victim\n")
        cp = run(GUARD, "--expect-root", self.good, "--", entry)
        self.assertEqual(cp.returncode, mgr.VIOLATION_EXIT, cp.stdout + cp.stderr)
        self.assertIn("IMPORT TREE VIOLATION", cp.stderr)
        self.assertIn("INVENTORY EMISSION FAILED", cp.stderr)

    def test_an_emission_that_raises_leaves_the_childs_own_exit_status_alone(self):
        entry = write(self.good / "nd-unfolding" / "breakexit.py",
                      "import sys\n" + self.REACH +
                      "def boom(*a, **k):\n"
                      "    raise RuntimeError('inventory exploded')\n"
                      "gmod['loaded_checkout_roots'] = boom\n"
                      "sys.exit(7)\n")
        cp = run(GUARD, "--expect-root", self.good, "--", entry)
        self.assertEqual(cp.returncode, 7, cp.stdout + cp.stderr)
        self.assertIn("INVENTORY EMISSION FAILED", cp.stderr)

    def test_an_unwritable_stream_does_not_raise_out_of_the_emitter(self):
        """Both the emission and its own failure notice go to the same stream, so the
        failure path has to survive the failure it is reporting."""
        class Dead:
            def write(self, *_a):
                raise OSError("stream is gone")
            def flush(self):
                raise OSError("stream is gone")
        self.assertIsNone(mgr._emit_inventory(str(self.good), stream=Dead()))


class TheChildsExitPathsAllKeepTheReceipt(GuardFixture):
    """`SystemExit` is the NORMAL way a real entrypoint ends, so an emission that only
    ran on the fall-through path would be missing from almost every production run.
    This is the arm that justifies `finally` over a statement after `run_path`."""

    def _entry(self, name, body):
        return write(self.good / "nd-unfolding" / name,
                     "import victim\n" + body)

    def test_sys_exit_zero_still_emits(self):
        cp = run(GUARD, "--expect-root", self.good, "--",
                 self._entry("e0.py", "import sys\nsys.exit(0)\n"))
        self.assertEqual(cp.returncode, 0, cp.stderr)
        self.assertIn(INV, cp.stderr)

    def test_sys_exit_nonzero_still_emits_and_keeps_the_status(self):
        cp = run(GUARD, "--expect-root", self.good, "--",
                 self._entry("e7.py", "import sys\nsys.exit(7)\n"))
        self.assertEqual(cp.returncode, 7, cp.stderr)
        self.assertIn(INV, cp.stderr)

    def test_an_uncaught_child_exception_still_emits(self):
        cp = run(GUARD, "--expect-root", self.good, "--",
                 self._entry("eboom.py", "raise ValueError('child broke')\n"))
        self.assertEqual(cp.returncode, 1, cp.stderr)
        self.assertIn("ValueError", cp.stderr)
        self.assertIn(INV, cp.stderr)


class TheReceiptDoesNotTouchTheChildsStdout(TenModuleFixture):
    """Consumers parse the child's stdout; the two Gate-5 launchers grep it."""

    def test_not_one_inventory_byte_reaches_stdout(self):
        cp = self.go()
        self.assertNotIn(INV, cp.stdout)
        self.assertNotIn("LOADED-CHECKOUT INVENTORY", cp.stdout)
        self.assertEqual(cp.stdout, "CHILD OK\n")

    def test_the_whole_inventory_is_on_stderr(self):
        cp = self.go()
        self.assertIn("LOADED-CHECKOUT INVENTORY", cp.stderr)
        self.assertIn(str(self.tree), cp.stderr)


class TheInventoryReportsOneInterpreterAndSaysSo(unittest.TestCase):
    """The blind spot, asserted rather than described.

    The emission walks the PARENT's `sys.modules`. The tool's own docstring already
    records that the refusal half does not cross a subprocess boundary; the receipt
    half does not either, and for the same reason. That is a limit on what a green
    inventory means, so it is asserted here AND printed in the emission itself -- a
    caveat that lives only in a docstring is not attached to the artifact a reader
    holds.
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        tmp = pathlib.Path(self._tmp.name)
        self.good = make_checkout(tmp, "parent-tree")
        self.other = make_checkout(tmp, "child-only-tree")
        write(self.other / "nd-unfolding" / "hidden.py", "NAME = 'hidden'\n")
        self.child = write(self.other / "nd-unfolding" / "child.py",
                           "import sys\n"
                           f"sys.path.insert(0, {str(self.other / 'nd-unfolding')!r})\n"
                           "import hidden\n"
                           "print('CHILD LOADED', hidden.NAME)\n")
        self.parent = write(self.good / "nd-unfolding" / "parent.py",
                            "import subprocess, sys\n"
                            f"subprocess.run([sys.executable, {str(self.child)!r}], check=True)\n")

    def test_a_subprocess_childs_checkout_is_NOT_in_the_parents_inventory(self):
        cp = run(GUARD, "--expect-root", self.good, "--", self.parent)
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        self.assertIn("CHILD LOADED hidden", cp.stdout)
        rows, _, _ = inventory(cp.stderr)
        self.assertNotIn(str(self.other), rows)

    def test_the_emission_states_that_limit_where_the_reader_of_a_log_will_see_it(self):
        cp = run(GUARD, "--expect-root", self.good, "--", self.parent)
        self.assertIn("SCOPE -- THIS INTERPRETER ONLY", cp.stderr)
        self.assertIn("subprocess.run", cp.stderr)
        self.assertIn("AT LEAST these trees", cp.stderr)

    def test_the_docstring_says_so_too_where_a_maintainer_will_read_it(self):
        text = GUARD.read_text()
        self.assertIn("THE SCOPE IS ONE INTERPRETER", text)
        self.assertIn("IT CANNOT REFUSE, BY CONSTRUCTION", text)


class TheInventoryReusesTheGuardsOwnResolver(unittest.TestCase):
    """One resolver, one marker pair. A receipt that answered "is this a checkout"
    differently from the gate could report a clean single root for a tree the gate
    would have refused -- two products disagreeing with neither being wrong."""

    def test_the_inventory_contains_no_second_marker_test(self):
        """Read off the shipped file's AST, not off its prose.

        A token count would pass on a comment and fail on a rename. What has to be true
        is structural: the enumeration reaches the marker pair ONLY through
        `checkout_root_of`, and touches neither `is_checkout` nor `MARKERS` itself.
        """
        import ast
        tree = ast.parse(GUARD.read_text())
        funcs = {n.name: n for n in ast.walk(tree)
                 if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
        self.assertIn("loaded_checkout_roots", funcs)
        self.assertIn("is_checkout", funcs)

        def names_used(node):
            return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}

        used = names_used(funcs["loaded_checkout_roots"]) | names_used(funcs["_emit_inventory"])
        self.assertIn("checkout_root_of", used)
        self.assertNotIn("is_checkout", used)
        self.assertNotIn("MARKERS", used)

        # and the marker pair itself is read in exactly the two places it already was:
        # the predicate, and main's exit-2 message that names what --expect-root needs.
        # Anything else in this list is a second marker test by another name.
        self.assertEqual(
            sorted(f for f, n in funcs.items() if "MARKERS" in names_used(n)),
            ["is_checkout", "main"])

    def test_the_walker_routes_through_checkout_root_of(self):
        """Measured by mutation, not by reading: break the shared resolver and the
        inventory must go blind with it."""
        original = mgr.checkout_root_of
        try:
            mgr.checkout_root_of = lambda *_a, **_k: None
            self.assertEqual(mgr.loaded_checkout_roots(), {})
        finally:
            mgr.checkout_root_of = original
        self.assertNotEqual(mgr.loaded_checkout_roots(), {})

    def test_the_walker_agrees_with_the_gate_on_the_real_repo(self):
        self.assertEqual(mgr.checkout_root_of(str(GUARD)), str(REPO))
        self.assertIn(str(REPO), mgr.loaded_checkout_roots())


class TheNamespacePackageExclusionIsDeclaredNotSilent(unittest.TestCase):
    """PB-16 @ 9a7f6529, second sentence: a narrowing's control must name what covers
    the excluded case, or say nothing does.

    `loaded_checkout_roots` skips any module with no `__file__`. For built-in and frozen
    modules that is free -- they are outside every checkout anyway. For NAMESPACE
    PACKAGES it is not free, because a namespace package's `__file__` IS None while the
    directory it resolved to can sit inside a real checkout. `nd-unfolding/` has no
    `__init__.py`, so this is the repo's own shape and not a contrived one.

    MEASURED, BOTH BRANCHES, before either was claimed:

      import pkg            -> the fixture checkout is ABSENT from the inventory
                               entirely (1 module / 1 root, and that root is the
                               wrapper's own). Covered by NOTHING.
      import pkg.sub        -> `pkg.sub` has a real `__file__`, so the tree appears.
                               The submodule is the covering mechanism.

    SO THE FIRST PB-16 BRANCH IS AVAILABLE AND IS TAKEN: the mechanism covering the
    excluded case is any submodule import, and the test below ASSERTS THAT IT FIRES
    rather than merely observing that the bare case does not.

    AND THE RESIDUAL IS DECLARED RATHER THAN LEFT TO LOOK COVERED. A bare `import pkg`
    that never reaches a submodule is invisible here, and that is defensible on the
    guard's own subject: a namespace package has no `__init__.py`, so NO CODE FROM THAT
    TREE EXECUTED. OI-136 is about which tree's code ran, and in that state none did.
    The moment any of it does run, it runs through a submodule and the arm below
    catches it. What is genuinely lost is the weaker fact that the tree was on the path
    at all -- so this is a narrowing with a stated cost, not a clean scoping.
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        tmp = pathlib.Path(self._tmp.name)
        self.tree = make_checkout(tmp, "ns-tree")
        # deliberately NO __init__.py -- that is what makes it a namespace package,
        # and the fixture is the producer of that condition rather than a restatement
        # of the `__file__ is None` rule under test.
        write(self.tree / "nd-unfolding" / "pkg" / "sub.py", "NAME = 'sub'\n")
        self.bare = write(self.tree / "nd-unfolding" / "bare.py",
                          "import pkg\n"
                          "assert getattr(pkg, '__file__', None) is None, 'not a namespace pkg'\n"
                          "print('BARE OK')\n")
        self.viasub = write(self.tree / "nd-unfolding" / "viasub.py",
                            "import pkg.sub\nprint('SUB OK')\n")

    def test_the_fixture_really_produces_a_namespace_package(self):
        """The precondition, asserted in the child. If `pkg` ever gained an
        `__init__.py` this whole class would pass vacuously against a normal package."""
        cp = run(GUARD, "--expect-root", self.tree, "--", self.bare)
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        self.assertIn("BARE OK", cp.stdout)

    def test_a_bare_namespace_import_leaves_the_checkout_ABSENT(self):
        """The excluded case, measured rather than reasoned about."""
        cp = run(GUARD, "--expect-root", self.tree, "--", self.bare)
        rows, _, _ = inventory(cp.stderr)
        self.assertNotIn(str(self.tree), rows)
        self.assertEqual(list(only_child_roots(rows, GUARD_ROOT)), [])

    def test_the_covering_mechanism_FIRES_as_soon_as_a_submodule_is_imported(self):
        """PB-16's first branch: name the mechanism and assert it fires.

        This is the arm that distinguishes "correctly scoped" from "nothing covers this
        any more" -- without it the previous test is a does-not-fire control with
        identical output in both worlds.
        """
        cp = run(GUARD, "--expect-root", self.tree, "--", self.viasub)
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        rows, _, _ = inventory(cp.stderr)
        self.assertIn(str(self.tree), rows)
        self.assertEqual(rows[str(self.tree)][2], ["pkg.sub"])

    def test_the_guard_half_skips_namespace_origins_too_so_neither_half_covers_it(self):
        """The exclusion is not an asymmetry between the two halves -- `find_spec`
        returns early on `origin in ("built-in", "frozen", "namespace")`. Pinned so a
        future reader does not "fix" the inventory into disagreeing with the gate."""
        import ast
        tree = ast.parse(GUARD.read_text())
        fn = next(n for n in ast.walk(tree)
                  if isinstance(n, ast.FunctionDef) and n.name == "find_spec")
        consts = {c.value for c in ast.walk(fn) if isinstance(c, ast.Constant)}
        self.assertIn("namespace", consts)
