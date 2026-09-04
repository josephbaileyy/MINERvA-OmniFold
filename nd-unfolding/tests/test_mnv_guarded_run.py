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
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
import unittest.mock

HERE = pathlib.Path(__file__).resolve().parent
GUARD = HERE.parent / "mnv_guarded_run.py"
SHIM_TREE = HERE.parent / "mnv_guard_shim"
SHIM = SHIM_TREE / "sitecustomize.py"
REPO = HERE.parents[1]

sys.path.insert(0, str(HERE.parent))
import mnv_guarded_run as mgr  # noqa: E402
import mnv_import_set_ratchet as ratchet  # noqa: E402


def make_checkout(base: pathlib.Path, name: str) -> pathlib.Path:
    root = base / name
    (root / "nd-unfolding").mkdir(parents=True)
    (root / "VALIDATION_LEDGER.md").write_text("# fixture ledger\n")
    return root


def write(path: pathlib.Path, text: str) -> pathlib.Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def deploy_shim(destination: pathlib.Path) -> pathlib.Path:
    """Copy the WHOLE tracked shim into a fixture checkout: sitecustomize, scanner and `bin/`.

    THE GUARD HAS TWO HALVES AND A FIXTURE CARRYING ONE MEASURES THE WRONG TREE. Before the PATH
    wrappers existed this copied a single file; a fixture that kept doing so would report
    `path_shim: not-armed`, and every control below that asserts a bash child's `python3 -I` is
    REFUSED would have passed for the opposite reason -- the wrapper was missing, not the flag
    scanned. `copytree` is used for the mode bits: a wrapper copied without its executable bit is
    skipped by PATH lookup, which is the same vacuous pass one level down.
    """
    shutil.copytree(SHIM_TREE, destination, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("__pycache__"))
    return destination


def run(*args, **kw):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    return subprocess.run([sys.executable, *[str(a) for a in args]],
                          capture_output=True, text=True, env=env, **kw)


class GuardFixture(unittest.TestCase):
    """Two checkouts, `victim` in both, entrypoint hardcoding the wrong one."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        tmp = pathlib.Path(self._tmp.name).resolve()
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

    def test_a_deployment_missing_its_shim_exits_2_and_records_the_failed_install(self):
        deployed_guard = self.good / "nd-unfolding" / "deployed_guard.py"
        deployed_guard.write_bytes(GUARD.read_bytes())
        inv = pathlib.Path(self._tmp.name) / "cc" / "missing-shim.jsonl"
        cp = run(deployed_guard, "--expect-root", self.good, "--inventory", inv,
                 "--", self.entry)
        self.assertEqual(cp.returncode, mgr.CANNOT_CHECK_EXIT, cp.stdout + cp.stderr)
        self.assertIn("guard installation failed", cp.stderr)
        rec = json.loads(inv.read_text().strip())
        self.assertEqual(rec["outcome"], "cannot-check:guard-installation-failed")
        self.assertEqual(rec["propagation"], "not-armed")


class MarkerSemantics(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = pathlib.Path(self._tmp.name).resolve()
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


class TheSubprocessBoundaryIsCovered(unittest.TestCase):
    """Cover inheriting Python children and pin every declared propagation limit.

    The parent scripts use the live adoption shape: derive a child beside themselves,
    then launch it through `subprocess.run([sys.executable, child])`. The child carries
    the OI-136 defect by inserting a foreign checkout at position zero before importing
    a module. The sitecustomize shim must install early enough to refuse that resolved
    origin, and every interpreter must leave a separately identifiable inventory.
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        tmp = pathlib.Path(self._tmp.name).resolve()
        self.good = make_checkout(tmp, "expected-tree")
        self.bad = make_checkout(tmp, "stale-tree")
        write(self.good / "nd-unfolding" / "victim.py", "MARK = 'RIGHT TREE'\n")
        write(self.bad / "nd-unfolding" / "victim.py", "MARK = 'WRONG TREE'\n")
        self.inventory = tmp / "inventory" / "guard.jsonl"
        self.deployed_guard = self.good / "nd-unfolding" / "mnv_guarded_run.py"
        self.deployed_shim = (
            self.good / "nd-unfolding" / "mnv_guard_shim" / "sitecustomize.py"
        )
        self.deployed_guard.write_bytes(GUARD.read_bytes())
        deploy_shim(self.deployed_shim.parent)
        self.deployed_bin = self.deployed_shim.parent / "bin"
        self.bad_child = write(
            self.good / "nd-unfolding" / "child_bad.py",
            "import sys\n"
            f"sys.path.insert(0, {str(self.bad / 'nd-unfolding')!r})\n"
            "import victim\n"
            "print('CHILD-LOADED', victim.MARK)\n",
        )
        self.clean_child = write(
            self.good / "nd-unfolding" / "child_clean.py",
            "import victim\n"
            "print('CHILD-LOADED', victim.MARK)\n",
        )
        self.parent_sub = write(
            self.good / "nd-unfolding" / "parent_sub.py",
            "import os, subprocess, sys\n"
            "_HERE = os.path.dirname(os.path.abspath(__file__))\n"
            "if _HERE not in sys.path: sys.path.insert(0, _HERE)\n"
            "raise SystemExit(subprocess.run(\n"
            "    [sys.executable, os.path.join(_HERE, 'child_bad.py')]).returncode)\n",
        )
        self.parent_in = write(
            self.good / "nd-unfolding" / "parent_in.py",
            "import os, runpy, sys\n"
            "_HERE = os.path.dirname(os.path.abspath(__file__))\n"
            "if _HERE not in sys.path: sys.path.insert(0, _HERE)\n"
            "runpy.run_path(os.path.join(_HERE, 'child_bad.py'), run_name='__main__')\n",
        )

    def tearDown(self):
        self._tmp.cleanup()

    def guarded(self, parent=None):
        target = self.parent_sub if parent is None else parent
        return run(self.deployed_guard, "--expect-root", self.good,
                   "--inventory", self.inventory,
                   "--", target)

    def records(self):
        return [json.loads(line) for line in self.inventory.read_text().splitlines()
                if line.strip()]

    def test_IN_PROCESS_the_guard_fires_which_proves_the_fixture_hijacks(self):
        p = run(self.deployed_guard, "--expect-root", self.good, "--", self.parent_in)
        self.assertEqual(p.returncode, mgr.VIOLATION_EXIT,
                         f"stdout:\n{p.stdout}\nstderr:\n{p.stderr}")
        self.assertIn("IMPORT TREE VIOLATION", p.stderr)
        self.assertNotIn("CHILD-LOADED", p.stdout)

    def test_live_subprocess_shape_refuses_the_child_hijack_and_records_its_parent(self):
        p = self.guarded()
        self.assertEqual(p.returncode, mgr.VIOLATION_EXIT,
                         f"stdout:\n{p.stdout}\nstderr:\n{p.stderr}")
        self.assertIn("[oi136 child] IMPORT TREE VIOLATION", p.stderr)
        self.assertNotIn("CHILD-LOADED", p.stdout)
        records = self.records()
        self.assertEqual({record["depth"] for record in records}, {0, 1})
        parent = next(record for record in records if record["depth"] == 0)
        child = next(record for record in records if record["depth"] == 1)
        self.assertEqual(parent["propagation"], "armed")
        self.assertEqual(child["propagated_from"], parent["pid"])
        self.assertEqual(child["violation"]["module"], "victim")
        self.assertEqual(child["propagation"], "armed")

    def test_a_grandchild_is_refused_and_records_depth_two(self):
        write(
            self.good / "nd-unfolding" / "middle.py",
            "import os, subprocess, sys\n"
            "_HERE = os.path.dirname(os.path.abspath(__file__))\n"
            "raise SystemExit(subprocess.run(\n"
            "    [sys.executable, os.path.join(_HERE, 'child_bad.py')]).returncode)\n",
        )
        parent = write(
            self.good / "nd-unfolding" / "parent_grand.py",
            "import os, subprocess, sys\n"
            "_HERE = os.path.dirname(os.path.abspath(__file__))\n"
            "raise SystemExit(subprocess.run(\n"
            "    [sys.executable, os.path.join(_HERE, 'middle.py')]).returncode)\n",
        )
        p = self.guarded(parent)
        self.assertEqual(p.returncode, mgr.VIOLATION_EXIT, p.stdout + p.stderr)
        records = {record["depth"]: record for record in self.records()}
        self.assertEqual(set(records), {0, 1, 2})
        self.assertEqual(records[1]["propagated_from"], records[0]["pid"])
        self.assertEqual(records[2]["propagated_from"], records[1]["pid"])
        self.assertEqual(records[2]["violation"]["module"], "victim")

    def test_a_clean_child_passes_and_has_its_own_ratchet_identity(self):
        parent = write(
            self.good / "nd-unfolding" / "parent_clean.py",
            "import os, subprocess, sys\n"
            "_HERE = os.path.dirname(os.path.abspath(__file__))\n"
            "raise SystemExit(subprocess.run(\n"
            "    [sys.executable, os.path.join(_HERE, 'child_clean.py')]).returncode)\n",
        )
        p = self.guarded(parent)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("CHILD-LOADED RIGHT TREE", p.stdout)
        records = self.records()
        parent_record = next(record for record in records if record["depth"] == 0)
        child_record = next(record for record in records if record["depth"] == 1)
        self.assertEqual(child_record["propagated_from"], parent_record["pid"])
        self.assertEqual(child_record["propagation"], "armed")

        keys = {ratchet.entrypoint_key(record) for record in records}
        self.assertEqual(keys, {
            "nd-unfolding/parent_clean.py",
            "nd-unfolding/child_clean.py",
        })
        pins = {
            "entrypoints": {
                ratchet.entrypoint_key(record): {
                    "modules": ratchet.import_set(record),
                }
                for record in records
            },
        }
        declared_empty = tuple(
            ratchet.entrypoint_key(record)
            for record in records
            if record["repo_origin_count"] == 0
        )
        violations, observed = ratchet.check(
            records,
            pins,
            require_empty_allow=declared_empty,
        )
        self.assertEqual(violations, [])
        self.assertEqual(set(observed), keys)

    def test_an_explicit_allow_is_propagated_to_the_child(self):
        p = run(self.deployed_guard, "--expect-root", self.good, "--allow", self.bad,
                "--inventory", self.inventory, "--", self.parent_sub)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("CHILD-LOADED WRONG TREE", p.stdout)
        child = next(record for record in self.records() if record["depth"] == 1)
        self.assertEqual(child["allow"], [str(self.bad)])
        victim = next(origin for origin in child["repo_origins"]
                      if origin["fullname"] == "victim")
        self.assertTrue(victim["allowed"])

    def test_dash_S_dash_I_and_dash_E_standalone_and_combined_are_refused(self):
        sentinel = pathlib.Path(self._tmp.name) / "flag-child-ran"
        child = write(
            self.good / "nd-unfolding" / "child_flagged.py",
            "import pathlib, sys\n"
            f"pathlib.Path({str(sentinel)!r}).write_text('ran')\n"
            f"sys.path.insert(0, {str(self.bad / 'nd-unfolding')!r})\n"
            "import victim\n",
        )
        parent = write(
            self.good / "nd-unfolding" / "parent_flag.py",
            "import os, subprocess, sys\n"
            "_HERE = os.path.dirname(os.path.abspath(__file__))\n"
            "raise SystemExit(subprocess.run(\n"
            f"    [sys.executable, sys.argv[1], {str(child)!r}]).returncode)\n",
        )
        for flag in ("-S", "-I", "-E", "-IS", "-Es", "-OI"):
            with self.subTest(flag=flag):
                self.inventory.unlink(missing_ok=True)
                sentinel.unlink(missing_ok=True)
                p = run(self.deployed_guard, "--expect-root", self.good,
                        "--inventory", self.inventory, "--", parent, flag)
                self.assertEqual(p.returncode, mgr.VIOLATION_EXIT, p.stdout + p.stderr)
                self.assertIn("[oi136 launch]", p.stderr)
                self.assertFalse(sentinel.exists(), "the refused child was launched")
                records = self.records()
                self.assertEqual([record["depth"] for record in records], [0])
                self.assertEqual(records[0]["verdict"], "REFUSED launch")
                self.assertEqual(
                    records[0]["outcome"],
                    "refused:launch-python-startup-flags",
                )
                self.assertIn(flag, records[0]["offending_argv"])
                self.assertEqual(records[0]["refusal_site"], mgr.SITE_LAUNCH)

    def test_a_child_with_a_cleared_environment_is_rearmed_and_refused(self):
        parent = write(
            self.good / "nd-unfolding" / "parent_empty_env.py",
            "import os, subprocess, sys\n"
            "_HERE = os.path.dirname(os.path.abspath(__file__))\n"
            "raise SystemExit(subprocess.run(\n"
            "    [sys.executable, os.path.join(_HERE, 'child_bad.py')], "
            "env={}).returncode)\n",
        )
        p = self.guarded(parent)
        self.assertEqual(p.returncode, mgr.VIOLATION_EXIT, p.stdout + p.stderr)
        self.assertIn("[oi136 child] IMPORT TREE VIOLATION", p.stderr)
        records = {record["depth"]: record for record in self.records()}
        self.assertEqual(set(records), {0, 1})
        self.assertEqual(records[0]["launch_env"], "re-armed")
        self.assertEqual(records[1]["violation"]["module"], "victim")

    def test_a_child_with_pythonpath_lacking_the_shim_is_rearmed_and_refused(self):
        unrelated = pathlib.Path(self._tmp.name).resolve() / "unrelated-pythonpath"
        unrelated.mkdir()
        parent = write(
            self.good / "nd-unfolding" / "parent_bad_pythonpath.py",
            "import os, subprocess, sys\n"
            "_HERE = os.path.dirname(os.path.abspath(__file__))\n"
            "env = os.environ.copy()\n"
            f"env['PYTHONPATH'] = {str(unrelated)!r}\n"
            "raise SystemExit(subprocess.run(\n"
            "    [sys.executable, os.path.join(_HERE, 'child_bad.py')], "
            "env=env).returncode)\n",
        )
        p = self.guarded(parent)
        self.assertEqual(p.returncode, mgr.VIOLATION_EXIT, p.stdout + p.stderr)
        records = {record["depth"]: record for record in self.records()}
        self.assertEqual(records[0]["launch_env"], "re-armed")
        self.assertEqual(records[1]["violation"]["module"], "victim")

    def test_a_bash_child_running_python_inherits_the_shim_and_is_refused(self):
        child_code = (
            "import sys; "
            f"sys.path.insert(0, {str(self.bad / 'nd-unfolding')!r}); "
            "import victim"
        )
        shell_child = write(
            self.good / "nd-unfolding" / "child.sh",
            f"python3 -c {shlex.quote(child_code)}\n",
        )
        parent = write(
            self.good / "nd-unfolding" / "parent_shell.py",
            "import subprocess\n"
            f"raise SystemExit(subprocess.run(['/bin/bash', {str(shell_child)!r}]).returncode)\n",
        )
        p = self.guarded(parent)
        self.assertEqual(p.returncode, mgr.VIOLATION_EXIT, p.stdout + p.stderr)
        self.assertIn("[oi136 child] IMPORT TREE VIOLATION", p.stderr)
        records = {record["depth"]: record for record in self.records()}
        self.assertEqual(set(records), {0, 1})
        self.assertEqual(records[1]["violation"]["module"], "victim")

    def isolated_child(self, name: str):
        """A child that records having run, then commits the OI-136 defect under isolation."""
        sentinel = pathlib.Path(self._tmp.name) / f"{name}-ran"
        isolated = write(
            self.good / "nd-unfolding" / f"{name}.py",
            "import pathlib, sys\n"
            f"pathlib.Path({str(sentinel)!r}).write_text('ran')\n"
            f"sys.path.insert(0, {str(self.bad / 'nd-unfolding')!r})\n"
            "import victim\n"
            "print('ISOLATED-LOADED', victim.MARK)\n",
        )
        return isolated, sentinel

    def test_a_bash_child_running_python_dash_I_IN_A_SCRIPT_FILE_is_refused_BEFORE_bash_starts(self):
        """WAS COVERED BY THE PATH WRAPPER; IS NOW REFUSED BY THE SCAN, ONE PROCESS EARLIER.

        A bash script runs `python3 -I child.py`. Until round 6 the guarded interpreter owned no
        launch site inside bash and the script was admitted UNREAD, so the only thing standing in
        front of the interpreter was the wrapper the PATH lookup would find. The reviewer then wrote
        scripts that decline the PATH lookup, so the script file is READ at the launch site now and
        this refusal happens before `bash` is even started.

        BOTH REFUSERS ARE KEPT LIVE IN THIS ONE ARM. The end-to-end half asserts the scan refuses
        (the `[oi136 launch]` line is the guard's, not the wrapper's, and the argv in the record is
        the `bash script.sh` one); the direct half calls the tracked wrapper on the same argv and
        asserts it would have refused too. A test that only checked the new site would have quietly
        retired the second chance rather than measured it.

        THE SENTINEL IS WHAT MAKES THIS A REFUSAL RATHER THAN A LATE CATCH: an exit 3 alone cannot
        tell a launch that never happened from one caught after the wrong tree was loaded.
        """
        isolated, sentinel = self.isolated_child("child_isolated")
        for flag in ("-I", "-S", "-E", "-IS"):
            with self.subTest(flag=flag):
                self.inventory.unlink(missing_ok=True)
                sentinel.unlink(missing_ok=True)
                shell_child = write(
                    self.good / "nd-unfolding" / "child_isolated.sh",
                    f"python3 {flag} {shlex.quote(str(isolated))}\n",
                )
                parent = write(
                    self.good / "nd-unfolding" / "parent_isolated_shell.py",
                    "import subprocess\n"
                    f"raise SystemExit(subprocess.run(['/bin/bash', {str(shell_child)!r}])"
                    ".returncode)\n",
                )
                p = self.guarded(parent)
                self.assertEqual(p.returncode, mgr.VIOLATION_EXIT, p.stdout + p.stderr)
                self.assertIn("[oi136 launch]", p.stderr)
                self.assertFalse(sentinel.exists(), "the isolated child ran anyway")
                self.assertNotIn("ISOLATED-LOADED", p.stdout)
                self.assertEqual([record["depth"] for record in self.records()], [0])
                record = self.records()[0]
                self.assertEqual(record["path_shim"], "armed")
                self.assertEqual(record["launch_refusal"]["reason"], mgr.LAUNCH_REASON_FLAGS)
                self.assertEqual(record["launch_refusal"]["offending_flag"], flag)
                # THE ARGV IN THE RECORD IS THE SHELL LAUNCH, which is what says the refusal came
                # from reading the script rather than from a wrapper one process further down.
                self.assertEqual(record["launch_refusal"]["argv"],
                                 ["/bin/bash", str(shell_child)])
                # THE SECOND CHANCE, STILL LIVE: the tracked wrapper on the same argv.
                wrapper = subprocess.run(
                    [str(self.deployed_bin / "python3"), flag, str(isolated)],
                    capture_output=True, text=True,
                    env=dict(os.environ,
                             MNV_GUARD_MODULE=str(self.deployed_guard),
                             MNV_GUARD_EXPECT_ROOT=str(self.good),
                             MNV_GUARD_PARENT_PID=str(os.getpid()),
                             MNV_GUARD_DEPTH="0",
                             PYTHONPATH=str(self.deployed_shim.parent)))
                self.assertEqual(wrapper.returncode, mgr.VIOLATION_EXIT, wrapper.stderr)
                self.assertIn("PATH interpreter wrapper", wrapper.stderr)
                self.assertFalse(sentinel.exists(), "the wrapper let the isolated child run")

    def test_a_bash_child_running_python_VIA_PATH_is_GUARDED_by_the_wrapper(self):
        """The silent direction, and the one that decides whether the wrapper is usable at all.

        The same launch without an isolating flag must reach the interpreter, and the interpreter
        must be GUARDED: the depth-1 record and the `[oi136 child]` import refusal are the
        evidence, and the exit code on its own is not -- a wrapper that refused everything would
        also exit 3 here.
        """
        shell_child = write(
            self.good / "nd-unfolding" / "child_via_path.sh",
            f"python3 {shlex.quote(str(self.bad_child))}\n",
        )
        parent = write(
            self.good / "nd-unfolding" / "parent_via_path.py",
            "import subprocess\n"
            f"raise SystemExit(subprocess.run(['/bin/bash', {str(shell_child)!r}]).returncode)\n",
        )
        p = self.guarded(parent)
        self.assertEqual(p.returncode, mgr.VIOLATION_EXIT, p.stdout + p.stderr)
        self.assertIn("[oi136 child] IMPORT TREE VIOLATION", p.stderr)
        self.assertNotIn("[oi136 launch]", p.stderr)
        self.assertNotIn("CHILD-LOADED", p.stdout)
        records = {record["depth"]: record for record in self.records()}
        self.assertEqual(set(records), {0, 1})
        self.assertEqual(records[1]["violation"]["module"], "victim")

    def test_a_bash_child_running_a_CLEAN_script_via_PATH_is_unaffected(self):
        """A wrapper on PATH must not change what a correct run computes."""
        shell_child = write(
            self.good / "nd-unfolding" / "child_clean_via_path.sh",
            f"python3 {shlex.quote(str(self.clean_child))}\n",
        )
        parent = write(
            self.good / "nd-unfolding" / "parent_clean_via_path.py",
            "import subprocess\n"
            f"raise SystemExit(subprocess.run(['/bin/bash', {str(shell_child)!r}]).returncode)\n",
        )
        p = self.guarded(parent)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("CHILD-LOADED RIGHT TREE", p.stdout)
        self.assertNotIn("[oi136 launch]", p.stderr)
        self.assertEqual({record["depth"] for record in self.records()}, {0, 1})

    def test_the_wrapper_execs_the_interpreter_THE_CALLER_ASKED_FOR(self):
        """A wrapper must not silently change WHICH interpreter runs.

        `MNV_GUARD_REAL_PYTHON` is a recorded FALLBACK, not a substitution: the wrapper resolves
        its own name through PATH with the shim directories removed, so a script asking for a
        different `python3` than the parent's `sys.executable` still gets that one. The fixture
        puts a DECOY interpreter on the child's PATH -- a shell script that prints its own identity
        and execs the real one -- and the decoy must be what runs.

        THE DECOY IS PLACED BY THE PARENT AND BEHIND THE SHIM DIRECTORIES, AND BOTH HALVES OF THAT
        ARE FIXES TO THIS ARM. It used to write `export PATH=<decoy>:$PATH` inside the script, which
        round 6 refuses -- an assignment to PATH disarms every later line, so it refuses wherever it
        appears. And putting the decoy FIRST meant the decoy ran instead of the wrapper, so the arm
        passed without the wrapper resolving anything: the claim under test is that the WRAPPER
        finds the caller's interpreter, which requires the wrapper to be in front of the decoy.

        AND THE MIDDLE PROCESS IS A PYTHON CHILD, NOT A bash ONE, WHICH IS ROUND 7's CHANGE HERE.
        The arm used to run the decoy scenario inside a shell script; an admitted shell now runs
        with `PATH` set to the guard's wrapper directories and NOTHING ELSE, so a decoy the caller
        put on `PATH` is not reachable from one -- by construction, and that is the enforcement
        rather than a defect. An admitted NON-shell child keeps the caller's `PATH` behind the shim
        directories, which is exactly where this claim lives: the wrapper is still in front of the
        interpreter for such a child, and it must still resolve the caller's interpreter and not
        its own. The `{0, 1, 2}` depth set is the middle child and the clean child under it.
        """
        decoy_dir = pathlib.Path(self._tmp.name).resolve() / "decoy-bin"
        decoy_dir.mkdir()
        decoy = decoy_dir / "python3"
        decoy.write_text("#!/bin/sh\n"
                         "printf 'DECOY-INTERPRETER\\n' >&2\n"
                         f"exec {shlex.quote(sys.executable)} \"$@\"\n")
        decoy.chmod(0o755)
        middle = write(
            self.good / "nd-unfolding" / "middle_decoy.py",
            "import subprocess\n"
            f"raise SystemExit(subprocess.run(['python3', {str(self.clean_child)!r}])"
            ".returncode)\n",
        )
        parent = write(
            self.good / "nd-unfolding" / "parent_decoy.py",
            "import os, subprocess, sys\n"
            # The shim directories stay in front; the decoy goes immediately behind them, so
            # `python3` reaches the WRAPPER and the wrapper's own PATH walk reaches the decoy.
            "shim = [d for d in os.environ['MNV_GUARD_PATH_SHIM_DIRS'].split(os.pathsep) if d]\n"
            "rest = [d for d in os.environ['PATH'].split(os.pathsep) if d and d not in shim]\n"
            f"env = dict(os.environ, PATH=os.pathsep.join(shim + [{str(decoy_dir)!r}] + rest))\n"
            f"raise SystemExit(subprocess.run([sys.executable, {str(middle)!r}], env=env)"
            ".returncode)\n",
        )
        p = self.guarded(parent)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("CHILD-LOADED RIGHT TREE", p.stdout)
        self.assertIn("DECOY-INTERPRETER", p.stderr,
                      "the wrapper substituted its own interpreter for the caller's")
        self.assertEqual({record["depth"] for record in self.records()}, {0, 1, 2})

    def test_a_VERSIONED_interpreter_name_is_covered_by_a_GENERATED_wrapper(self):
        """`python3.12 -I child.py` from a bash child: the name the tracked `bin/` does not carry.

        A wrapper intercepts only the NAME it is installed under, and a cluster module file puts
        `python3.11`/`python3.12` in front of a science script. `install()` therefore generates a
        delegator for the basename of `sys.executable` when the tracked pair does not cover it --
        so this fixture runs the guard THROUGH a versioned symlink to make that basename versioned,
        which is the only way to exercise the generated half rather than assert it.
        """
        versioned_name = f"python3.{sys.version_info.minor}"
        versioned_dir = pathlib.Path(self._tmp.name).resolve() / "versioned-bin"
        versioned_dir.mkdir()
        versioned = versioned_dir / versioned_name
        versioned.symlink_to(sys.executable)
        isolated, sentinel = self.isolated_child("child_versioned")
        shell_child = write(
            self.good / "nd-unfolding" / "child_versioned.sh",
            f"{versioned_name} -I {shlex.quote(str(isolated))}\n",
        )
        parent = write(
            self.good / "nd-unfolding" / "parent_versioned.py",
            "import subprocess\n"
            f"raise SystemExit(subprocess.run(['/bin/bash', {str(shell_child)!r}]).returncode)\n",
        )
        environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
                           PATH=f"{versioned_dir}{os.pathsep}{os.environ['PATH']}")
        p = subprocess.run(
            [str(versioned), str(self.deployed_guard), "--expect-root", str(self.good),
             "--inventory", str(self.inventory), "--", str(parent)],
            capture_output=True, text=True, env=environment,
        )
        self.assertEqual(p.returncode, mgr.VIOLATION_EXIT, p.stdout + p.stderr)
        self.assertIn("[oi136 launch]", p.stderr)
        self.assertFalse(sentinel.exists(), "the isolated child ran anyway")
        record = self.records()[0]
        self.assertEqual(record["path_shim"], "armed")
        generated = [d for d in record["path_shim_dirs"] if str(self.deployed_bin) != d]
        # TWO GENERATED DIRECTORIES SINCE ROUND 7, and they answer different questions: one holds
        # the delegator for the VERSIONED interpreter name this arm exists for, the other holds one
        # forwarder per leaf tool that exists under a system prefix on this host -- which is what a
        # restricted shell's wrapper-only PATH has to contain for `ls` to work at all. Both are
        # per-process temporary directories; the COMMITTED one is the third entry and is not here.
        self.assertEqual(len(generated), 2, record["path_shim_dirs"])
        for directory in generated:
            self.assertTrue(directory.startswith(tempfile.gettempdir()), generated)
        # THE DIRECTORIES ARE GONE BY NOW -- both are removed by the guarded process's own
        # `atexit` -- so they are told apart by the prefix `tempfile.mkdtemp` was given, which is
        # the only evidence of them that survives into the record a reader will have.
        versioned_dirs = [d for d in generated
                          if pathlib.Path(d).name.startswith("mnv-guard-bin-")]
        forwarder_dirs = [d for d in generated
                          if pathlib.Path(d).name.startswith("mnv-guard-tools-")]
        self.assertEqual(len(versioned_dirs), 1, generated)
        self.assertEqual(len(forwarder_dirs), 1, generated)

    def test_the_absolute_path_isolated_launch_WAS_THE_DECLARED_GAP_AND_IS_NOW_REFUSED(self):
        """THE ARM WHOSE VERDICT ROUND 6 INVERTED, KEPT UNDER THE SAME FIXTURE AS EVIDENCE.

        It used to assert exit 0, a written sentinel and `ISOLATED-LOADED WRONG TREE` on stdout,
        with `declared_gap` naming the boundary in the record -- a fully admitted fail-open run,
        which is exactly what the reviewer said about it: "the already-declared absolute-path route
        is itself also a fully admitted fail-open path".

        WHY IT WAS EVER DECLARED, AND WHY THAT REASONING WAS WRONG. The argument was "an absolute
        path consults no PATH, so no wrapper stands in front of it". True, and irrelevant: what
        guards a Python child is the shim on `PYTHONPATH`, and what defeats the shim is `-I`. So the
        question was never whether a PATH lookup happens -- it was whether the launch was READ. Both
        halves are now read: this shell script is scanned at the launch site, and an interpreter
        named by any path goes through the same startup-flag grammar as a bare `python3`.

        BOTH ARMS ARE ASSERTED HERE, in the two spellings the reviewer's finding has: inside a
        SCRIPT FILE, and as a DIRECT `subprocess.run` argv from the guarded parent.
        """
        isolated, sentinel = self.isolated_child("child_absolute_isolated")
        shell_child = write(
            self.good / "nd-unfolding" / "child_absolute_isolated.sh",
            f"{shlex.quote(sys.executable)} -I {shlex.quote(str(isolated))}\n",
        )
        arms = {
            "in a shell SCRIPT FILE": (
                "import subprocess\n"
                f"raise SystemExit(subprocess.run(['/bin/bash', {str(shell_child)!r}])"
                ".returncode)\n"),
            "as a DIRECT argv": (
                "import subprocess, sys\n"
                f"raise SystemExit(subprocess.run([{sys.executable!r}, '-I', {str(isolated)!r}])"
                ".returncode)\n"),
        }
        for name, body in arms.items():
            with self.subTest(arm=name):
                self.inventory.unlink(missing_ok=True)
                sentinel.unlink(missing_ok=True)
                parent = write(self.good / "nd-unfolding" / "parent_absolute_isolated.py", body)
                p = self.guarded(parent)
                self.assertEqual(p.returncode, mgr.VIOLATION_EXIT, p.stdout + p.stderr)
                self.assertIn("[oi136 launch]", p.stderr)
                self.assertFalse(sentinel.exists(), "the isolated child ran anyway")
                self.assertNotIn("ISOLATED-LOADED", p.stdout)
                record = self.records()[0]
                self.assertEqual(record["launch_refusal"]["reason"], mgr.LAUNCH_REASON_FLAGS)
                self.assertEqual(record["launch_refusal"]["offending_flag"], "-I")
                # THE RECORD'S BOUNDARY IS THE NEW ONE, and the old sentence is gone from it: a
                # ratchet reader must not still be told that this launch is outside the guard.
                self.assertEqual(record["declared_gap"], mgr.DECLARED_GAP)
                self.assertIn("TRUST BY LOCATION", record["declared_gap"])
                self.assertIn("THE RESTRICTED-SHELL GUARANTEE IS BASH'S OWN",
                              record["declared_gap"])
                self.assertNotIn("invokes the interpreter by an ABSOLUTE PATH",
                                 record["declared_gap"])
                # THE ROUND-6 SENTENCE IS GONE FROM THE RECORD TOO. It said the residual was
                # "COMMAND WORDS BUILT AT RUN TIME" and nothing about the model of shell syntax
                # that every shell claim rested on; a ratchet reader must not still be told that.
                self.assertNotIn("COMMAND WORDS BUILT AT RUN TIME", record["declared_gap"])

    def test_os_execv_into_python_dash_I_is_refused_before_replacement(self):
        sentinel = pathlib.Path(self._tmp.name) / "execv-isolated-child-ran"
        isolated = write(
            self.good / "nd-unfolding" / "execv_isolated.py",
            "import pathlib\n"
            f"pathlib.Path({str(sentinel)!r}).write_text('ran')\n",
        )
        parent = write(
            self.good / "nd-unfolding" / "parent_execv_isolated.py",
            "import os, sys\n"
            f"os.execv(sys.executable, [sys.executable, '-I', {str(isolated)!r}])\n",
        )
        p = self.guarded(parent)
        self.assertEqual(p.returncode, mgr.VIOLATION_EXIT, p.stdout + p.stderr)
        self.assertIn("[oi136 launch]", p.stderr)
        self.assertFalse(sentinel.exists())
        record = self.records()[0]
        self.assertEqual(record["verdict"], "REFUSED launch")
        self.assertEqual(record["refusal_site"], mgr.SITE_LAUNCH)

    def test_a_clean_child_runs_under_every_wrapped_launch_primitive(self):
        """One clean child, launched sixteen ways, and every way has to keep it guarded.

        THE TWO SHELL ROWS NAME `python3` AND NOT `sys.executable`, and that is round 7's model
        rather than a fixture convenience. An admitted shell now runs as `bash -r`, whose first
        documented restriction is that a command name may not contain a slash -- so an absolute
        interpreter path inside a shell string is refused BY BASH, and a row spelling it that way
        would be asserting that the restriction is not in force. `python3` resolves through the
        wrapper directory, which is the only PATH a restricted child has, and the wrapper resolves
        the real interpreter from the contract.
        """
        command = f"python3 {shlex.quote(str(self.clean_child))}"
        bodies = {
            "Popen": (
                "raise SystemExit(subprocess.Popen(\n"
                f"    [sys.executable, {str(self.clean_child)!r}]).wait())\n"
            ),
            "Popen-shell": (
                f"raise SystemExit(subprocess.Popen({command!r}, shell=True).wait())\n"
            ),
            "posix_spawn": (
                f"pid = os.posix_spawn(sys.executable, [sys.executable, "
                f"{str(self.clean_child)!r}], {{}})\n"
                "_, status = os.waitpid(pid, 0)\n"
                "raise SystemExit(os.waitstatus_to_exitcode(status))\n"
            ),
            "posix_spawnp": (
                f"pid = os.posix_spawnp(sys.executable, [sys.executable, "
                f"{str(self.clean_child)!r}], {{}})\n"
                "_, status = os.waitpid(pid, 0)\n"
                "raise SystemExit(os.waitstatus_to_exitcode(status))\n"
            ),
            "execv": f"os.execv(sys.executable, [sys.executable, {str(self.clean_child)!r}])\n",
            "execve": (
                f"os.execve(sys.executable, [sys.executable, {str(self.clean_child)!r}], {{}})\n"
            ),
            "execvp": (
                f"os.execvp(sys.executable, [sys.executable, {str(self.clean_child)!r}])\n"
            ),
            "execvpe": (
                f"os.execvpe(sys.executable, [sys.executable, {str(self.clean_child)!r}], {{}})\n"
            ),
            "execl": f"os.execl(sys.executable, sys.executable, {str(self.clean_child)!r})\n",
            "execle": (
                f"os.execle(sys.executable, sys.executable, {str(self.clean_child)!r}, {{}})\n"
            ),
            "execlp": (
                f"os.execlp(sys.executable, sys.executable, {str(self.clean_child)!r})\n"
            ),
            "execlpe": (
                f"os.execlpe(sys.executable, sys.executable, {str(self.clean_child)!r}, {{}})\n"
            ),
            "spawnv": (
                f"raise SystemExit(os.spawnv(os.P_WAIT, sys.executable, "
                f"[sys.executable, {str(self.clean_child)!r}]))\n"
            ),
            "spawnve": (
                f"raise SystemExit(os.spawnve(os.P_WAIT, sys.executable, "
                f"[sys.executable, {str(self.clean_child)!r}], {{}}))\n"
            ),
            "spawnvp": (
                f"raise SystemExit(os.spawnvp(os.P_WAIT, sys.executable, "
                f"[sys.executable, {str(self.clean_child)!r}]))\n"
            ),
            "spawnvpe": (
                f"raise SystemExit(os.spawnvpe(os.P_WAIT, sys.executable, "
                f"[sys.executable, {str(self.clean_child)!r}], {{}}))\n"
            ),
            "spawnl": (
                f"raise SystemExit(os.spawnl(os.P_WAIT, sys.executable, "
                f"sys.executable, {str(self.clean_child)!r}))\n"
            ),
            "spawnle": (
                f"raise SystemExit(os.spawnle(os.P_WAIT, sys.executable, "
                f"sys.executable, {str(self.clean_child)!r}, {{}}))\n"
            ),
            "spawnlp": (
                f"raise SystemExit(os.spawnlp(os.P_WAIT, sys.executable, "
                f"sys.executable, {str(self.clean_child)!r}))\n"
            ),
            "spawnlpe": (
                f"raise SystemExit(os.spawnlpe(os.P_WAIT, sys.executable, "
                f"sys.executable, {str(self.clean_child)!r}, {{}}))\n"
            ),
            "system": f"raise SystemExit(os.system({command!r}))\n",
        }
        for name, body in bodies.items():
            with self.subTest(primitive=name):
                self.inventory.unlink(missing_ok=True)
                parent = write(
                    self.good / "nd-unfolding" / f"parent_{name.replace('-', '_')}.py",
                    "import os, subprocess, sys\n" + body,
                )
                result = self.guarded(parent)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("CHILD-LOADED RIGHT TREE", result.stdout)
                self.assertTrue(self.records(), f"no inventory for {name}")

    def test_parent_and_child_records_carry_the_same_shim_digest(self):
        parent = write(
            self.good / "nd-unfolding" / "parent_digest.py",
            "import subprocess, sys\n"
            f"raise SystemExit(subprocess.run([sys.executable, "
            f"{str(self.clean_child)!r}]).returncode)\n",
        )
        result = self.guarded(parent)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        records = {record["depth"]: record for record in self.records()}
        expected = hashlib.sha256(self.deployed_shim.read_bytes()).hexdigest()
        self.assertEqual(records[0]["shim_sha256"], expected)
        self.assertEqual(records[1]["shim_sha256"], expected)

    def test_the_recorded_digest_is_of_the_shim_THAT_RAN(self):
        """The operand, not just the value: the deployed shim is made to DIFFER from this repo's.

        With a byte-identical copy the test above cannot tell "the digest of the shim that
        installed this guard" from "the digest of some other file with the same contents", so a
        digest read off the wrong path would pass it. Here the two differ by one comment line and
        only one of them can be the answer -- which is what makes a MUTATED shim visible in the
        evidence rather than merely claimed to be.
        """
        self.deployed_shim.write_bytes(
            self.deployed_shim.read_bytes() + b"\n# fixture mutation: behaviour-neutral\n")
        deployed = hashlib.sha256(self.deployed_shim.read_bytes()).hexdigest()
        repo_shim = hashlib.sha256(SHIM.read_bytes()).hexdigest()
        self.assertNotEqual(deployed, repo_shim, "the mutation must actually change the digest")
        parent = write(
            self.good / "nd-unfolding" / "parent_digest_operand.py",
            "import subprocess, sys\n"
            f"raise SystemExit(subprocess.run([sys.executable, "
            f"{str(self.clean_child)!r}]).returncode)\n",
        )
        result = self.guarded(parent)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        records = {record["depth"]: record for record in self.records()}
        for depth in (0, 1):
            self.assertEqual(records[depth]["shim_sha256"], deployed)
            self.assertNotEqual(records[depth]["shim_sha256"], repo_shim)

    def test_the_shim_refuses_a_guard_module_outside_expect_root(self):
        env = dict(
            os.environ,
            PYTHONPATH=str(self.deployed_shim.parent),
            MNV_GUARD_MODULE=str(GUARD),
            MNV_GUARD_EXPECT_ROOT=str(self.good),
            MNV_GUARD_ALLOW="",
            MNV_GUARD_INVENTORY="",
        )
        result = subprocess.run(
            [sys.executable, "-c", "print('must not run')"],
            capture_output=True,
            text=True,
            env=env,
        )
        self.assertEqual(result.returncode, mgr.VIOLATION_EXIT, result.stdout + result.stderr)
        self.assertIn("GUARD MODULE OUTSIDE EXPECTED ROOT", result.stderr)
        self.assertNotIn("must not run", result.stdout)

    def sentinel_child(self, name: str):
        """A child that RECORDS HAVING RUN before committing the OI-136 defect.

        The sentinel is what separates "refused" from "ran and was then refused": an exit 3 alone
        cannot tell a launch that never happened from a child that loaded the wrong tree and was
        caught afterwards, and only the first is a launch-site refusal.
        """
        sentinel = pathlib.Path(self._tmp.name) / f"{name}-ran"
        child = write(
            self.good / "nd-unfolding" / f"{name}.py",
            "import pathlib, sys\n"
            f"pathlib.Path({str(sentinel)!r}).write_text('ran')\n"
            f"sys.path.insert(0, {str(self.bad / 'nd-unfolding')!r})\n"
            "import victim\n"
            "print('CHILD-LOADED', victim.MARK)\n",
        )
        return child, sentinel

    def test_a_flag_after_an_option_VALUE_is_still_refused(self):
        """`-W ignore -I`: the value sits in the NEXT token, which used to end the scan.

        MEASURED FAIL-OPEN, not hypothetical: the first implementation stopped at the first token
        that did not start with `-`, so `ignore` ended the walk and the `-I` behind it launched an
        isolated, unguarded child. That is the reviewer's finding with a different spelling.
        """
        child, sentinel = self.sentinel_child("child_after_value")
        for argv in (["-W", "ignore", "-I"], ["-X", "dev", "-S"],
                     ["--check-hash-based-pycs", "always", "-E"]):
            with self.subTest(argv=argv):
                self.inventory.unlink(missing_ok=True)
                sentinel.unlink(missing_ok=True)
                parent = write(
                    self.good / "nd-unfolding" / "parent_after_value.py",
                    "import subprocess, sys\n"
                    f"raise SystemExit(subprocess.run([sys.executable, *{argv!r}, "
                    f"{str(child)!r}]).returncode)\n",
                )
                p = self.guarded(parent)
                self.assertEqual(p.returncode, mgr.VIOLATION_EXIT, p.stdout + p.stderr)
                self.assertIn("[oi136 launch]", p.stderr)
                self.assertFalse(sentinel.exists(), "the refused child was launched")
                record = self.records()[0]
                self.assertEqual(record["verdict"], "REFUSED launch")
                self.assertEqual(record["launch_refusal"]["offending_flag"], argv[-1])
                self.assertEqual(record["launch_refusal"]["reason"],
                                 mgr.LAUNCH_REASON_FLAGS)

    def test_an_option_VALUE_that_contains_S_I_or_E_is_not_a_forbidden_flag(self):
        """The opposite direction, and it is the direction that gets a guard switched off.

        `-Xpycache_prefix=/tmp/PYC-CACHE` contains an uppercase `E`, and the first implementation
        refused it. A guard that refuses correct launches is one people route around.
        """
        cache = pathlib.Path(self._tmp.name).resolve() / "PYC-CACHE"
        for option in (f"-Xpycache_prefix={cache}", "-WError::UserWarning"):
            with self.subTest(option=option):
                self.inventory.unlink(missing_ok=True)
                parent = write(
                    self.good / "nd-unfolding" / "parent_option_value.py",
                    "import subprocess, sys\n"
                    f"raise SystemExit(subprocess.run([sys.executable, {option!r}, "
                    f"{str(self.clean_child)!r}]).returncode)\n",
                )
                p = self.guarded(parent)
                self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
                self.assertIn("CHILD-LOADED RIGHT TREE", p.stdout)
                self.assertNotIn("[oi136 launch]", p.stderr)
                self.assertEqual({record["depth"] for record in self.records()}, {0, 1})

    def env_launch(self, arguments, name="parent_env_bin"):
        """Run a parent that launches `env <arguments>` and return the completed process."""
        argv = [shutil.which("env"), *[str(a) for a in arguments]]
        parent = write(
            self.good / "nd-unfolding" / f"{name}.py",
            "import subprocess\n"
            f"raise SystemExit(subprocess.run({argv!r}).returncode)\n",
        )
        return self.guarded(parent)

    @unittest.skipUnless(shutil.which("env"), "no `env` on this platform")
    def test_a_python_child_launched_THROUGH_env_is_REFUSED_on_a_flag(self):
        """ROUND 5, VERBATIM: `env -- python -I` and `env -S 'python -I ...'`.

        Both reached the wrong-tree import, exited 0, and emitted only the parent's inventory,
        because the parser modelled a subset of `env`'s options and LEFT AN UNRECOGNISED PREFIX
        UNSCANNED. `--` is the plainest spelling of that hole and `-S` is the one that hides the
        whole command inside a string; the third row is the attached-value form, and the fourth
        proves the refusal survives a legitimate `-u` in front of it.
        """
        child, sentinel = self.sentinel_child("child_through_env")
        cases = (
            ["--", sys.executable, "-I", str(child)],
            ["-S", f"{shlex.quote(sys.executable)} -I {shlex.quote(str(child))}"],
            [f"--split-string={shlex.quote(sys.executable)} -I {shlex.quote(str(child))}"],
            ["-uFOO", sys.executable, "-I", str(child)],
            ["-C", str(self.good), "--", sys.executable, "-E", str(child)],
        )
        for arguments in cases:
            with self.subTest(arguments=arguments):
                self.inventory.unlink(missing_ok=True)
                sentinel.unlink(missing_ok=True)
                p = self.env_launch(arguments)
                self.assertEqual(p.returncode, mgr.VIOLATION_EXIT, p.stdout + p.stderr)
                self.assertIn("[oi136 launch]", p.stderr)
                self.assertFalse(sentinel.exists(), "the refused child was launched")
                self.assertNotIn("CHILD-LOADED", p.stdout)
                record = self.records()[0]
                self.assertEqual(record["verdict"], "REFUSED launch")
                self.assertEqual(record["refusal_site"], mgr.SITE_LAUNCH)
                self.assertEqual(record["launch_refusal"]["reason"], mgr.LAUNCH_REASON_FLAGS)
                self.assertIn(record["launch_refusal"]["offending_flag"], ("-I", "-E"))

    @unittest.skipUnless(shutil.which("env"), "no `env` on this platform")
    def test_an_env_OPTION_THIS_PARSER_DOES_NOT_MODEL_refuses_instead_of_passing(self):
        """FAIL-CLOSED, WHICH IS THE WHOLE ROUND-5 REPAIR: unparsed is a refusal, never a pass.

        `--bogus` stands for every option this table does not list, including the ones a future
        coreutils adds. The refusal is deliberately independent of what the command word turns out
        to be -- an unmodelled option may CONSUME that word, so the parser does not know whether a
        Python child is behind it, and answering anyway is how round 5 happened.
        """
        child, sentinel = self.sentinel_child("child_unmodelled_env")
        cases = (
            (["--bogus", sys.executable, str(child)], mgr.LAUNCH_REASON_UNMODELLED, "--bogus"),
            (["-P", "/usr/bin", sys.executable, str(child)], mgr.LAUNCH_REASON_UNMODELLED, "-P"),
            (["--unknown=1", sys.executable, str(child)], mgr.LAUNCH_REASON_UNMODELLED,
             "--unknown=1"),
            (["-u"], mgr.LAUNCH_REASON_UNPARSED, "-u with no value"),
        )
        for arguments, reason, offending in cases:
            with self.subTest(arguments=arguments):
                self.inventory.unlink(missing_ok=True)
                sentinel.unlink(missing_ok=True)
                p = self.env_launch(arguments, name="parent_unmodelled_env")
                self.assertEqual(p.returncode, mgr.VIOLATION_EXIT, p.stdout + p.stderr)
                self.assertIn("[oi136 launch]", p.stderr)
                self.assertFalse(sentinel.exists(), "the refused launch happened anyway")
                record = self.records()[0]
                self.assertEqual(record["verdict"], "REFUSED launch")
                self.assertEqual(record["outcome"],
                                 "refused:launch-unmodelled-launch-grammar")
                self.assertEqual(record["refusal_site"], mgr.SITE_LAUNCH)
                self.assertEqual(record["launch_refusal"]["reason"], reason)
                self.assertEqual(record["launch_refusal"]["offending_flag"], offending)

    @unittest.skipUnless(shutil.which("env"), "no `env` on this platform")
    def test_an_env_ARGV_that_strips_the_contract_is_RE_ARMED_and_the_child_is_guarded(self):
        """`env -i -- python ...`: the cleared environment in argv, REPAIRED rather than refused.

        This is the argv spelling of `env={}`, which is already re-armed, and the repair is the
        same one: the contract goes in as `NAME=VALUE` operands immediately before the command
        word, where `env` applies them last-wins. The EVIDENCE that it worked is not the exit code
        -- a refusal is also exit 3 -- it is that the child RAN, wrote its own depth-1 record, and
        was stopped at the IMPORT site with `[oi136 child]`. A launch refusal would have produced
        no child record at all.

        THREE ARMS PREVIOUSLY REFUSED HERE AND NOW RE-ARM (`-i`, `-u MNV_GUARD_MODULE`,
        `PYTHONPATH=`), and that is a widening: the guard used to decline the launch, and now the
        child starts guarded and its imports are measured.
        """
        cases = (
            ["-i", "--", sys.executable, str(self.bad_child)],
            ["-i", sys.executable, str(self.bad_child)],
            ["-u", "MNV_GUARD_MODULE", sys.executable, str(self.bad_child)],
            ["PYTHONPATH=/nowhere", sys.executable, str(self.bad_child)],
        )
        for arguments in cases:
            with self.subTest(arguments=arguments):
                self.inventory.unlink(missing_ok=True)
                p = self.env_launch(arguments, name="parent_rearmed_env")
                self.assertEqual(p.returncode, mgr.VIOLATION_EXIT, p.stdout + p.stderr)
                self.assertIn("[oi136 child] IMPORT TREE VIOLATION", p.stderr)
                self.assertNotIn("[oi136 launch]", p.stderr)
                self.assertNotIn("CHILD-LOADED", p.stdout)
                records = {record["depth"]: record for record in self.records()}
                self.assertEqual(set(records), {0, 1})
                self.assertEqual(records[0]["launch_env"], "argv-re-armed")
                self.assertEqual(records[1]["violation"]["module"], "victim")
                self.assertEqual(records[1]["propagated_from"], records[0]["pid"])

    @unittest.skipUnless(shutil.which("env"), "no `env` on this platform")
    def test_a_cleared_env_IN_FRONT_OF_a_shell_string_is_re_armed_THROUGH_the_shell(self):
        """`env -i bash -c "python3 child.py"`: nothing inside the string is wrong.

        The clearing is OUTSIDE the `-c` string, so a scan of the string alone returns clean and
        the interpreter inside it would start with no contract -- a fail-open reachable with two
        modelled features and no unmodelled ones. The repair goes in front of the SHELL, which
        inherits it and passes it down, and the evidence is the child's own depth-1 record.
        """
        p = self.env_launch(
            ["-i", "/bin/bash", "-c", f"python3 {shlex.quote(str(self.bad_child))}"],
            name="parent_cleared_shell_string")
        self.assertEqual(p.returncode, mgr.VIOLATION_EXIT, p.stdout + p.stderr)
        self.assertIn("[oi136 child] IMPORT TREE VIOLATION", p.stderr)
        self.assertNotIn("CHILD-LOADED", p.stdout)
        records = {record["depth"]: record for record in self.records()}
        self.assertEqual(set(records), {0, 1})
        self.assertEqual(records[0]["launch_env"], "argv-re-armed")
        self.assertEqual(records[1]["violation"]["module"], "victim")

    @unittest.skipUnless(shutil.which("env"), "no `env` on this platform")
    def test_a_cleared_env_in_front_of_a_shell_string_WITHOUT_python_is_left_alone(self):
        """The silent direction of the arm above: `env -i bash -c 'echo ...'` has nothing to guard.

        Requiring the contract for every shell string would refuse launches with no interpreter in
        them, which is the fail-closed rule applied where it buys nothing and costs a correct run.
        """
        p = self.env_launch(["-i", "/bin/bash", "-c", "echo SHELL-ONLY"],
                            name="parent_cleared_shell_only")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("SHELL-ONLY", p.stdout)
        self.assertNotIn("[oi136 launch]", p.stderr)
        self.assertEqual([record["depth"] for record in self.records()], [0])

    @unittest.skipUnless(shutil.which("env"), "no `env` on this platform")
    def test_a_cleared_env_INSIDE_a_split_string_is_refused_because_it_cannot_be_rewritten(self):
        """The one `env` arm that is refused rather than repaired, and why.

        `env -i -S 'python child.py'` needs the same repair as the row above, but the command word
        lives inside a STRING. Inserting an operand there would mean re-quoting somebody else's
        shell program, so the launch is refused instead -- the boundary between "repair" and
        "refuse" is whether the tokens are ours to insert between, and it is measured here rather
        than described.
        """
        child, sentinel = self.sentinel_child("child_split_cleared")
        p = self.env_launch(
            ["-i", "-S", f"{shlex.quote(sys.executable)} {shlex.quote(str(child))}"],
            name="parent_split_cleared")
        self.assertEqual(p.returncode, mgr.VIOLATION_EXIT, p.stdout + p.stderr)
        self.assertIn("[oi136 launch]", p.stderr)
        self.assertFalse(sentinel.exists(), "the refused child was launched")
        record = self.records()[0]
        self.assertEqual(record["launch_refusal"]["reason"], mgr.LAUNCH_REASON_ENV)
        self.assertEqual(record["launch_refusal"]["offending_flag"], "env -i")

    @unittest.skipUnless(shutil.which("env"), "no `env` on this platform")
    def test_a_clean_env_launch_in_every_modelled_spelling_still_runs(self):
        """THE DIRECTION THAT GETS A GUARD SWITCHED OFF. A fail-closed parser is only usable if
        the forms it models actually run, so every option in the table appears here in a launch
        that must reach the child and exit 0."""
        cases = (
            ["FOO=bar", sys.executable, str(self.clean_child)],
            ["-u", "MNV_UNRELATED_VAR", sys.executable, str(self.clean_child)],
            ["--", sys.executable, str(self.clean_child)],
            ["-C", str(self.good), sys.executable, str(self.clean_child)],
            ["-v", sys.executable, str(self.clean_child)],
            ["-S", f"{shlex.quote(sys.executable)} {shlex.quote(str(self.clean_child))}"],
        )
        #: `--argv0=`/`-a` are NOT here and that is a measurement, not an omission: the BSD `env`
        #: macOS ships rejects them ("illegal option -- a"), so an end-to-end row would test the
        #: platform rather than the parser. They are modelled because coreutils has them, and they
        #: are pinned where a parser can be asked directly --
        #: `TheLaunchGrammarIsParsedAndFailsClosed.COMMAND_WORD`.
        for arguments in cases:
            with self.subTest(arguments=arguments):
                self.inventory.unlink(missing_ok=True)
                p = self.env_launch(arguments, name="parent_clean_env")
                self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
                self.assertIn("CHILD-LOADED RIGHT TREE", p.stdout)
                self.assertNotIn("[oi136 launch]", p.stderr)
                self.assertEqual({record["depth"] for record in self.records()}, {0, 1})

    def test_a_python_child_behind_a_LAUNCH_WRAPPER_is_scanned_through_the_wrapper(self):
        """`nohup`, `nice`, `stdbuf`, `timeout`: each runs a LATER WORD, exactly as `env` does.

        A guard that modelled only `env` would have the same hole under a different name, and
        `timeout` is the sharpest case because its DURATION operand sits between the options and
        the command -- a parser that stopped at the first non-option token would scan `5` as the
        executable and wave the interpreter behind it through.
        """
        child, sentinel = self.sentinel_child("child_behind_wrapper")
        cases = (
            ("nohup", ["-I"]),
            ("nice", ["-n", "5", "-I"]),
            ("stdbuf", ["-oL", "-I"]),
            ("timeout", ["-k", "1", "30", "-S"]),
        )
        measured = []
        for wrapper, arguments in cases:
            binary = shutil.which(wrapper)
            if binary is None:
                # SKIPPED PER ARM AND NOT PER TEST, deliberately: `timeout` and `stdbuf` are GNU
                # coreutils and are absent on a stock macOS, and `self.skipTest` here would mark
                # the WHOLE method skipped -- discarding the arms that did run and leaving no
                # record that they had. The power arm below refuses the vacuous case.
                continue
            with self.subTest(wrapper=wrapper):
                measured.append(wrapper)
                self.inventory.unlink(missing_ok=True)
                sentinel.unlink(missing_ok=True)
                #: The flag is the LAST wrapper argument, so the interpreter word sits between the
                #: wrapper's own operands and the flag -- the shape a naive scan gets wrong.
                *prefix, flag = arguments
                argv = [binary, *prefix, sys.executable, flag, str(child)]
                parent = write(
                    self.good / "nd-unfolding" / "parent_wrapper.py",
                    "import subprocess\n"
                    f"raise SystemExit(subprocess.run({argv!r}).returncode)\n",
                )
                p = self.guarded(parent)
                self.assertEqual(p.returncode, mgr.VIOLATION_EXIT, p.stdout + p.stderr)
                self.assertIn("[oi136 launch]", p.stderr)
                self.assertFalse(sentinel.exists(), "the refused child was launched")
                record = self.records()[0]
                self.assertEqual(record["launch_refusal"]["reason"], mgr.LAUNCH_REASON_FLAGS)
                self.assertEqual(record["launch_refusal"]["offending_flag"], flag)
        self.assertTrue(measured, "no launch wrapper was present, so this test measured nothing; "
                                  "the grammar table in TheLaunchGrammarIsParsedAndFailsClosed is "
                                  "then the only evidence and this arm must not read as a pass")

    def test_a_SHELL_STRING_that_launches_an_isolated_interpreter_is_refused(self):
        """`bash -c "python3 -I child.py"`: a command STRING, which no argv scan can see.

        The reviewer's finding has this spelling too, and it is the one a Slurm launcher actually
        writes. Every row is a real shape: a bare command, one behind `cd x &&`, one behind a
        newline that `shlex` alone would have swallowed, one whose redirection would have ended the
        flag scan early, and one whose interpreter is named by ABSOLUTE PATH.
        """
        child, sentinel = self.sentinel_child("child_shell_string")
        quoted = shlex.quote(str(child))
        strings = (
            f"python3 -I {quoted}",
            f"cd {shlex.quote(str(self.good))} && python3 -I {quoted}",
            f"echo starting\npython3 -I {quoted}",
            f"python3 2>/dev/null -I {quoted}",
            f"{shlex.quote(sys.executable)} -I {quoted}",
            f"nohup python3 -I {quoted} &",
        )
        for shell in ("/bin/sh", "/bin/bash"):
            for text in strings:
                with self.subTest(shell=shell, text=text):
                    self.inventory.unlink(missing_ok=True)
                    sentinel.unlink(missing_ok=True)
                    parent = write(
                        self.good / "nd-unfolding" / "parent_shell_string.py",
                        "import subprocess\n"
                        f"raise SystemExit(subprocess.run([{shell!r}, '-c', {text!r}])"
                        ".returncode)\n",
                    )
                    p = self.guarded(parent)
                    self.assertEqual(p.returncode, mgr.VIOLATION_EXIT, p.stdout + p.stderr)
                    self.assertIn("[oi136 launch]", p.stderr)
                    self.assertFalse(sentinel.exists(), "the refused child was launched")
                    record = self.records()[0]
                    self.assertEqual(record["launch_refusal"]["reason"],
                                     mgr.LAUNCH_REASON_FLAGS)
                    self.assertEqual(record["launch_refusal"]["offending_flag"], "-I")

    def test_a_SHELL_STRING_that_strips_the_contract_or_will_not_tokenise_is_refused(self):
        """The other two shell-string refusals: a disarming prefix, and a string nothing can read.

        A leading `NAME=VALUE` is that command's environment in every shell, so
        `PYTHONPATH=/nowhere python3 child.py` disarms the child exactly as `env` would; and an
        unbalanced quote is a string the tokenizer cannot split, which is refused rather than
        skipped for the same reason an unmodelled option is.
        """
        child, sentinel = self.sentinel_child("child_shell_env")
        quoted = shlex.quote(str(child))
        cases = (
            (f"PYTHONPATH=/nowhere python3 {quoted}", mgr.LAUNCH_REASON_ENV),
            (f"MNV_GUARD_MODULE= python3 {quoted}", mgr.LAUNCH_REASON_ENV),
            (f"env -i python3 {quoted}", mgr.LAUNCH_REASON_ENV),
            (f"python3 'unbalanced {quoted}", mgr.LAUNCH_REASON_UNPARSED),
            (f"nice --bogus python3 {quoted}", mgr.LAUNCH_REASON_UNMODELLED),
        )
        for text, reason in cases:
            with self.subTest(text=text):
                self.inventory.unlink(missing_ok=True)
                sentinel.unlink(missing_ok=True)
                parent = write(
                    self.good / "nd-unfolding" / "parent_shell_env.py",
                    "import subprocess\n"
                    f"raise SystemExit(subprocess.run(['/bin/bash', '-c', {text!r}])"
                    ".returncode)\n",
                )
                p = self.guarded(parent)
                self.assertEqual(p.returncode, mgr.VIOLATION_EXIT, p.stdout + p.stderr)
                self.assertIn("[oi136 launch]", p.stderr)
                self.assertFalse(sentinel.exists(), "the refused child was launched")
                self.assertEqual(self.records()[0]["launch_refusal"]["reason"], reason)

    def test_a_clean_SHELL_STRING_still_runs_and_the_child_is_guarded(self):
        """The silent direction for the shell-string scan, in both `-c` and `shell=True` spellings.

        A string launching an ordinary interpreter must reach the child, and the child must be
        GUARDED -- which the depth-1 record proves and the exit code alone does not.

        `bash -ec` AND NOT `bash -lc`, WHICH THIS ARM USED TO CARRY. Round 6 closed the login-shell
        spelling: `-l` sources `/etc/profile` and `~/.bash_profile` before the string, and this
        repository has the receipt for what lives there -- OI-179 defect 1 put `$HOME/bin` on PATH
        through a conditional in `/etc/profile:171`, with no edit to any file this campaign tracks.
        A startup file the guard cannot read is a program that runs before the one it scanned, so
        the arm below asserts the refusal instead.
        """
        quoted = shlex.quote(str(self.clean_child))
        bodies = {
            "sh -c": ("import subprocess\n"
                      f"raise SystemExit(subprocess.run(['/bin/sh', '-c', 'python3 {quoted}'])"
                      ".returncode)\n"),
            "bash -ec": ("import subprocess\n"
                         f"raise SystemExit(subprocess.run(['/bin/bash', '-ec', "
                         f"'python3 {quoted}']).returncode)\n"),
            "shell=True": ("import subprocess\n"
                           f"raise SystemExit(subprocess.run('python3 {quoted}', shell=True)"
                           ".returncode)\n"),
            "redirect": ("import subprocess\n"
                         f"raise SystemExit(subprocess.run(['/bin/sh', '-c', "
                         f"'python3 {quoted} 2>&1']).returncode)\n"),
        }
        for name, body in bodies.items():
            with self.subTest(spelling=name):
                self.inventory.unlink(missing_ok=True)
                parent = write(self.good / "nd-unfolding" / "parent_clean_shell.py", body)
                p = self.guarded(parent)
                self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
                self.assertIn("CHILD-LOADED RIGHT TREE", p.stdout)
                self.assertNotIn("[oi136 launch]", p.stderr)
                self.assertEqual({record["depth"] for record in self.records()}, {0, 1})

    def test_a_parent_that_DELETES_the_contract_cannot_launch_a_python_child(self):
        """The last fail-open route at a launch site is this process's own `os.environ`.

        `install()` exports the contract, so a launch inherits it -- unless the run deleted it.
        There is then nothing to re-arm FROM, an inherited-environment launch has no `env=` to
        repair, and the child would start unguarded and write no record. So it is refused.
        """
        child, sentinel = self.sentinel_child("child_disarmed")
        for statement, offending in (
                ("del os.environ['MNV_GUARD_MODULE']", "MNV_GUARD_MODULE"),
                ("del os.environ['MNV_GUARD_EXPECT_ROOT']", "MNV_GUARD_EXPECT_ROOT"),
                ("os.environ['PYTHONPATH'] = '/nowhere'", "PYTHONPATH")):
            with self.subTest(statement=statement):
                self.inventory.unlink(missing_ok=True)
                sentinel.unlink(missing_ok=True)
                parent = write(
                    self.good / "nd-unfolding" / "parent_disarmed.py",
                    "import os, subprocess, sys\n"
                    f"{statement}\n"
                    f"raise SystemExit(subprocess.run([sys.executable, "
                    f"{str(child)!r}]).returncode)\n",
                )
                p = self.guarded(parent)
                self.assertEqual(p.returncode, mgr.VIOLATION_EXIT, p.stdout + p.stderr)
                self.assertIn("[oi136 launch]", p.stderr)
                self.assertFalse(sentinel.exists(), "the refused child was launched")
                record = self.records()[0]
                self.assertEqual(record["verdict"], "REFUSED launch")
                self.assertEqual(record["launch_refusal"]["offending_flag"], offending)
                self.assertEqual(record["launch_refusal"]["reason"], mgr.LAUNCH_REASON_ENV)

    @unittest.skipUnless(shutil.which("env"), "no `env` on this platform")
    def test_a_bash_child_that_clears_the_environment_WAS_THE_SAME_GAP_AND_IS_NOW_REFUSED(self):
        """The second arm of the old declared gap, and its verdict is inverted too.

        It used to assert exit 0 with `CHILD-LOADED WRONG TREE` on stdout: a bash script running
        `env -i <absolute python> child.py` cleared the environment outside anything this guard
        read, so the child started with no contract and wrote no record. The script is read now, the
        `env -i` is seen where it is written, and the launch is refused -- and it is refused rather
        than repaired for the reason on `_scan_shell_program`: rewriting somebody else's shell
        program can change what a run computes, so a string and a file are both refused and neither
        is edited.
        """
        child, sentinel = self.sentinel_child("child_cleared_by_shell")
        shell_child = write(
            self.good / "nd-unfolding" / "child_cleared.sh",
            f"{shlex.quote(shutil.which('env'))} -i "
            f"{shlex.quote(sys.executable)} {shlex.quote(str(child))}\n",
        )
        parent = write(
            self.good / "nd-unfolding" / "parent_cleared_shell.py",
            "import subprocess\n"
            f"raise SystemExit(subprocess.run(['/bin/bash', {str(shell_child)!r}]).returncode)\n",
        )
        p = self.guarded(parent)
        self.assertEqual(p.returncode, mgr.VIOLATION_EXIT, p.stdout + p.stderr)
        self.assertIn("[oi136 launch]", p.stderr)
        self.assertFalse(sentinel.exists(), "the child ran with a cleared environment")
        self.assertNotIn("CHILD-LOADED", p.stdout)
        record = self.records()[0]
        self.assertEqual(record["launch_refusal"]["reason"], mgr.LAUNCH_REASON_ENV)
        self.assertEqual(record["launch_refusal"]["offending_flag"], "env -i")

    def test_an_existing_sitecustomize_still_executes_and_is_recorded(self):
        custom_dir = pathlib.Path(self._tmp.name).resolve() / "existing-site"
        marker = custom_dir / "executed.txt"
        write(
            custom_dir / "sitecustomize.py",
            "import os, pathlib\n"
            f"pathlib.Path({str(marker)!r}).write_text(str(os.getpid()))\n",
        )
        parent = write(
            self.good / "nd-unfolding" / "parent_existing_site.py",
            "import os, subprocess, sys\n"
            "_HERE = os.path.dirname(os.path.abspath(__file__))\n"
            "env = os.environ.copy()\n"
            f"env['PYTHONPATH'] += os.pathsep + {str(custom_dir)!r}\n"
            "raise SystemExit(subprocess.run(\n"
            "    [sys.executable, os.path.join(_HERE, 'child_clean.py')], "
            "env=env).returncode)\n",
        )
        p = self.guarded(parent)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        child = next(record for record in self.records() if record["depth"] == 1)
        self.assertTrue(marker.is_file())
        self.assertEqual(marker.read_text(), str(child["pid"]))
        self.assertEqual(child["chained_sitecustomize"], {
            "found": True,
            "executed": True,
            "origin": str(custom_dir / "sitecustomize.py"),
        })
        self.assertIn(str(custom_dir), child["sys_path_final"])

    def test_the_docstring_says_so_where_a_caller_will_read_it(self):
        self.assertIn("IT CROSSES PROCESS BOUNDARIES", mgr.__doc__)
        self.assertIn("Direct Python launches using `-S`, `-I` or `-E`", mgr.__doc__)
        self.assertIn("including `env={}`", mgr.__doc__)
        # THE LAUNCH CONTRACT, STATED WHERE A CALLER READS IT. The header used to say the coverage
        # of a non-Python child WAS the PATH wrapper; round 6 refuted that, so the sentence a reader
        # finds has to be the closed one -- and the six admitted classes have to be enumerated
        # there, because "everything else refuses" is unreadable without the list it complements.
        self.assertIn("A GUARDED PROCESS MAY START ONLY A CHILD THIS GUARD CAN PROVE", mgr.__doc__)
        self.assertIn("A SCRIPT FILE OPERAND IS READ AND SCANNED", mgr.__doc__)
        self.assertIn("`LAUNCH_REASON_UNPROVEN`", mgr.__doc__)
        # THE FOUR RESIDUALS, and every superseded sentence must be GONE rather than softened: a
        # header still declaring the absolute-path route understates the guard, and a reader who
        # finds it there will not go looking for the closure that replaced it. The round-6 pair is
        # in that class now -- "a command word built at run time" was the residual only while the
        # static model was the enforcement, and it is not.
        self.assertIn("THE FOUR DECLARED RESIDUALS", mgr.__doc__)
        self.assertIn("TRUST BY LOCATION", mgr.__doc__)
        self.assertIn("THE RESTRICTED-SHELL GUARANTEE IS BASH'S\nOWN", mgr.__doc__)
        self.assertNotIn("THE ONE DECLARED RESIDUAL GAP", mgr.__doc__)
        self.assertNotIn("THE TWO DECLARED RESIDUALS", mgr.__doc__)
        self.assertNotIn("A COMMAND WORD BUILT AT RUN\nTIME is REFUSED", mgr.__doc__)
        self.assertNotIn("invokes\nthe interpreter by an ABSOLUTE PATH", mgr.__doc__)
        # ROUND 7's THREE CLAIMS, each named where a caller reads them: the classification is by the
        # exec'd file, the enforcement for a shell is bash's restricted mode, and the wrapper
        # directory is what a shell program may reach.
        self.assertIn("ROUND 7 CLASSIFIES BY THE EXECUTABLE THE KERNEL WILL RUN", mgr.__doc__)
        self.assertIn("EVERY ADMITTED SHELL NOW RUNS AS RESTRICTED BASH", mgr.__doc__)
        self.assertIn("THE WRAPPER DIRECTORY IS THEREFORE WHAT A SHELL PROGRAM MAY REACH",
                      mgr.__doc__)
        # The claims the tests above measure. A claim in the header that no control pins is the
        # shape this whole file exists to prevent, so each of them is named here.
        self.assertIn("The scan follows CPython's OWN option grammar", mgr.__doc__)
        self.assertIn("either starts guarded or does not start", mgr.__doc__)
        self.assertIn("AN UNMODELLED SPELLING REFUSES", mgr.__doc__)
        self.assertIn("INTERPRETER WRAPPERS ON PATH COVER THE SECOND LAUNCH SITE", mgr.__doc__)
        self.assertIn("THE WRAPPERS ARE KEPT AND THEY ARE NO LONGER THE COVERAGE ARGUMENT",
                      mgr.__doc__)
        self.assertIn("`declared_gap`", mgr.__doc__)
        self.assertIn("`path_shim: armed`", mgr.__doc__)

    def test_the_declared_gap_and_the_path_shim_state_are_in_EVERY_record(self):
        """THE COVERAGE BOUNDARY TRAVELS WITH THE EVIDENCE, on every exit path.

        A ratchet reader consumes records, not docstrings. `declared_gap` is therefore written on
        the green path, the launch-refusal path, the import-refusal path and the no-guard
        cannot-check path -- and `path_shim` beside it, because when that is not `armed` the
        boundary is wider than the sentence.
        """
        child, _ = self.sentinel_child("child_gap_fields")
        arms = {
            "green": self.clean_child,
            "import-refusal": self.bad_child,
        }
        for name, target in arms.items():
            with self.subTest(arm=name):
                self.inventory.unlink(missing_ok=True)
                parent = write(
                    self.good / "nd-unfolding" / "parent_gap_fields.py",
                    "import subprocess, sys\n"
                    f"raise SystemExit(subprocess.run([sys.executable, {str(target)!r}])"
                    ".returncode)\n",
                )
                self.guarded(parent)
                records = self.records()
                self.assertTrue(records)
                for record in records:
                    self.assertEqual(record["declared_gap"], mgr.DECLARED_GAP)
                    self.assertEqual(record["path_shim"], "armed")
                    self.assertIn(str(self.deployed_bin), record["path_shim_dirs"])

        self.inventory.unlink(missing_ok=True)
        parent = write(
            self.good / "nd-unfolding" / "parent_gap_refusal.py",
            "import subprocess, sys\n"
            f"raise SystemExit(subprocess.run([sys.executable, '-I', {str(child)!r}])"
            ".returncode)\n",
        )
        self.guarded(parent)
        self.assertEqual(self.records()[0]["declared_gap"], mgr.DECLARED_GAP)

        # NO GUARD AT ALL: the widest boundary of the four, so the field must not go missing here.
        self.inventory.unlink(missing_ok=True)
        cannot = run(self.deployed_guard, "--expect-root", self.good,
                     "--inventory", self.inventory, "--", self.good / "nd-unfolding" / "absent.py")
        self.assertEqual(cannot.returncode, mgr.CANNOT_CHECK_EXIT, cannot.stderr)
        record = self.records()[0]
        self.assertEqual(record["declared_gap"], mgr.DECLARED_GAP)
        self.assertEqual(record["path_shim"], "not-armed")

    def test_the_recorded_wrapper_digest_is_of_the_WRAPPER_THAT_RAN(self):
        """The operand, not just the value -- the same control `shim_sha256` already has.

        The wrappers are tracked, but the A-2(f) source manifest binds `.py`/`.sh` files and a
        `sh` script installed on PATH as `python3` cannot carry a suffix. So the digest in the
        record is what binds those bytes, and a digest read off THIS repo's copy rather than the
        deployed one would pin the wrong file. The deployed wrapper is mutated by one comment line
        so that only one of the two can be the answer.
        """
        deployed_wrapper = self.deployed_bin / "python3"
        deployed_wrapper.write_bytes(
            deployed_wrapper.read_bytes() + b"\n# fixture mutation: behaviour-neutral\n")
        deployed = hashlib.sha256(deployed_wrapper.read_bytes()).hexdigest()
        repo_wrapper = hashlib.sha256((SHIM_TREE / "bin" / "python3").read_bytes()).hexdigest()
        self.assertNotEqual(deployed, repo_wrapper, "the mutation must change the digest")
        parent = write(
            self.good / "nd-unfolding" / "parent_wrapper_digest.py",
            "import subprocess, sys\n"
            f"raise SystemExit(subprocess.run([sys.executable, {str(self.clean_child)!r}])"
            ".returncode)\n",
        )
        p = self.guarded(parent)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        for record in self.records():
            self.assertEqual(record["path_shim_sha256"]["bin/python3"], deployed)
            self.assertNotEqual(record["path_shim_sha256"]["bin/python3"], repo_wrapper)
            self.assertEqual(
                record["path_shim_sha256"]["scan_argv.py"],
                hashlib.sha256((self.deployed_shim.parent / "scan_argv.py").read_bytes())
                .hexdigest())

    def test_a_deployment_MISSING_the_path_wrappers_says_so_instead_of_claiming_coverage(self):
        """A NARROWER GUARD IS A REPORTABLE STATE AND NOT A SILENT ONE.

        `sitecustomize.py` and `bin/` fail independently: a tree carrying only the first still gets
        the whole in-interpreter contract, so refusing the run would trade a narrower guard for no
        run at all. What may NOT happen is a record that reads like full coverage -- so the state
        names the missing file, and the same record's `declared_gap` is then an understatement the
        reader can see rather than one they cannot.
        """
        shutil.rmtree(self.deployed_bin)
        parent = write(
            self.good / "nd-unfolding" / "parent_no_bin.py",
            "import subprocess, sys\n"
            f"raise SystemExit(subprocess.run([sys.executable, {str(self.clean_child)!r}])"
            ".returncode)\n",
        )
        p = self.guarded(parent)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("CHILD-LOADED RIGHT TREE", p.stdout)
        for record in self.records():
            self.assertTrue(record["path_shim"].startswith("not-armed:"), record["path_shim"])
            self.assertIn("bin/python3", record["path_shim"])


class TheClosedChildModelRefusesWhatItCannotProve(unittest.TestCase):
    """ROUND 6, END TO END: every child a guarded process starts is either READ or REFUSED.

    THE FINDING THIS CLASS EXISTS FOR, VERBATIM: "Shell script files are not scanned; the
    implementation relies entirely on the inherited PATH wrapper. Three shell-script mutations
    bypassed it: `command -p python3 -I ...`, reordered `PATH=/usr/bin:/bin python3 -I ...`, BSD
    `env -P /usr/bin:/bin python3 -I ...`. All returned 0, ran the sentinel, loaded the wrong tree,
    produced no child record, and were not described by the declared 'absolute path or cleared
    environment' gap."

    EVERY ARM RUNS THE REAL GUARD IN A REAL SUBPROCESS AND BUILDS REAL FILES, because what is under
    test is an exit code, a record on disk, and whether a file exists -- and the sentinel is what
    separates "refused before launch" from "caught after the wrong tree loaded". The unit-level
    tables over the same grammar live in `TheLaunchGrammarIsParsedAndFailsClosed`; the two are not
    redundant, they answer "does the parser say so" and "does the process do so".
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        tmp = pathlib.Path(self._tmp.name).resolve()
        self.tmp = tmp
        self.good = make_checkout(tmp, "expected-tree")
        self.bad = make_checkout(tmp, "stale-tree")
        write(self.good / "nd-unfolding" / "victim.py", "MARK = 'RIGHT TREE'\n")
        write(self.bad / "nd-unfolding" / "victim.py", "MARK = 'WRONG TREE'\n")
        self.nd = self.good / "nd-unfolding"
        self.inventory = tmp / "inventory" / "guard.jsonl"
        self.deployed_guard = self.nd / "mnv_guarded_run.py"
        self.deployed_guard.write_bytes(GUARD.read_bytes())
        self.deployed_shim = self.nd / "mnv_guard_shim"
        deploy_shim(self.deployed_shim)
        self.deployed_bin = self.deployed_shim / "bin"
        self.addCleanup(self._tmp.cleanup)

    def guarded(self, parent):
        return run(self.deployed_guard, "--expect-root", self.good,
                   "--inventory", self.inventory, "--", parent)

    def records(self):
        if not self.inventory.exists():
            return []
        return [json.loads(line) for line in self.inventory.read_text().splitlines()
                if line.strip()]

    def hijacking_child(self, name: str):
        """A Python child that RECORDS HAVING RUN, then commits the OI-136 defect.

        The sentinel is the whole point: an exit 3 cannot tell a launch that never happened from
        one caught after the wrong tree was loaded, and the reviewer's mutations were reported as
        "ran the sentinel, loaded the wrong tree".
        """
        sentinel = self.tmp / f"{name}-ran"
        child = write(
            self.nd / f"{name}.py",
            "import pathlib, sys\n"
            f"pathlib.Path({str(sentinel)!r}).write_text('ran')\n"
            f"sys.path.insert(0, {str(self.bad / 'nd-unfolding')!r})\n"
            "import victim\n"
            "print('HIJACK-LOADED', victim.MARK)\n",
        )
        return child, sentinel

    def clean_child(self, name: str = "child_clean"):
        return write(self.nd / f"{name}.py",
                     "import victim\nprint('CHILD-LOADED', victim.MARK)\n")

    def launch_script(self, name: str, body: str, *, via: str = "bash", cwd=None):
        """Write a shell script, launch it from a guarded parent, return the CompletedProcess.

        `via="bash"` is `subprocess.run(["/bin/bash", "<abs>.sh"])`; `via="shebang"` writes a
        `#!/bin/bash` script, marks it executable and runs it as `./<name>.sh` with `cwd` set --
        the two spellings the reviewer used, and the second one also exercises the launch's own
        working directory rather than this process's.
        """
        script = self.nd / f"{name}.sh"
        if via == "shebang":
            write(script, "#!/bin/bash\n" + body)
            script.chmod(0o755)
            argv = [f"./{script.name}"]
            run_kwargs = f", cwd={str(cwd or self.nd)!r}"
        else:
            write(script, body)
            argv = ["/bin/bash", str(script)]
            run_kwargs = "" if cwd is None else f", cwd={str(cwd)!r}"
        parent = write(
            self.nd / f"parent_{name}.py",
            "import subprocess\n"
            f"raise SystemExit(subprocess.run({argv!r}{run_kwargs}).returncode)\n",
        )
        return self.guarded(parent)

    def assertRefusedBeforeLaunch(self, result, sentinel, reason=None, offending=None):
        """One refusal, checked on all four surfaces a reader of this repo's records uses."""
        self.assertEqual(result.returncode, mgr.VIOLATION_EXIT, result.stdout + result.stderr)
        self.assertIn("[oi136 launch]", result.stderr)
        self.assertNotIn("HIJACK-LOADED", result.stdout)
        self.assertFalse(sentinel.exists(),
                         "the sentinel exists, so the refused child RAN -- this is the reviewer's "
                         "finding, not a refusal")
        records = self.records()
        self.assertEqual([record["depth"] for record in records], [0],
                         "a child record means a child interpreter started")
        refusal = records[0]["launch_refusal"]
        self.assertIsNotNone(refusal, records[0])
        self.assertEqual(records[0]["verdict"], "REFUSED launch")
        self.assertEqual(records[0]["refusal_site"], mgr.SITE_LAUNCH)
        if reason is not None:
            self.assertEqual(refusal["reason"], reason, refusal)
        if offending is not None:
            self.assertIn(offending, refusal["offending_flag"], refusal)
        return records[0]

    # --- the three reviewer mutations ------------------------------------------------------------

    #: THE THREE MUTATIONS, EXACTLY AS THE REVIEWER WROTE THEM, with the reason each now refuses
    #: for. They are three different holes and not one: `command -p` replaces PATH with the
    #: implementation's default, a leading `PATH=` assignment replaces it with the caller's, and
    #: BSD `env -P` changes the directory `env` itself searches -- so all three find an interpreter
    #: with no wrapper in front of it, and none of them was described by the old declared gap.
    REVIEWER_MUTATIONS = (
        ("command_p", "command -p python3 -I {child}\n", mgr.LAUNCH_REASON_ENV, "-p"),
        ("reordered_path", "PATH=/usr/bin:/bin python3 -I {child}\n",
         mgr.LAUNCH_REASON_ENV, "PATH=/usr/bin:/bin"),
        ("env_dash_P", "env -P /usr/bin:/bin python3 -I {child}\n",
         mgr.LAUNCH_REASON_UNMODELLED, "-P"),
    )

    def test_the_three_reviewer_mutations_in_a_SCRIPT_FILE_are_refused(self):
        """`bash script.sh` where the script is one of the three mutations. Each refused, exit 3."""
        for name, template, reason, offending in self.REVIEWER_MUTATIONS:
            with self.subTest(mutation=name):
                self.inventory.unlink(missing_ok=True)
                child, sentinel = self.hijacking_child(f"hijack_{name}")
                result = self.launch_script(f"mut_{name}",
                                            template.format(child=shlex.quote(str(child))))
                self.assertRefusedBeforeLaunch(result, sentinel, reason, offending)

    def test_the_three_reviewer_mutations_BEHIND_A_SHEBANG_are_refused(self):
        """The same three as `./script.sh`, which is a launch with no shell word in the argv at all.

        `subprocess.run(["./mut.sh"])` names no interpreter, so the classification has to reach the
        script through its `#!/bin/bash` line -- and the relative `./` plus `cwd=` is what proves
        the operand is resolved against the LAUNCH's working directory and not this process's.
        """
        for name, template, reason, offending in self.REVIEWER_MUTATIONS:
            with self.subTest(mutation=name):
                self.inventory.unlink(missing_ok=True)
                child, sentinel = self.hijacking_child(f"shebang_{name}")
                result = self.launch_script(f"sheb_{name}",
                                            template.format(child=shlex.quote(str(child))),
                                            via="shebang")
                self.assertRefusedBeforeLaunch(result, sentinel, reason, offending)

    def test_command_dash_p_is_refused_even_WITHOUT_an_isolating_flag(self):
        """`command -p python3 x.py`: no `-I`, and still refused.

        The child would in fact still inherit the shim-first `PYTHONPATH`, so this launch is not
        certainly unguarded. THAT IS WHY THE RULE IS THE RULE RATHER THAN THE OUTCOME: `-p`
        removes the wrapper half of the contract, and a guard that reasoned "probably still fine"
        about half a contract is a guard whose coverage nobody can state. The refusal is `-p`
        itself, not the flag scan.
        """
        child, sentinel = self.hijacking_child("hijack_command_p_clean")
        result = self.launch_script("mut_command_p_clean",
                                    f"command -p python3 {shlex.quote(str(child))}\n")
        self.assertRefusedBeforeLaunch(result, sentinel, mgr.LAUNCH_REASON_ENV, "-p")

    # --- everything else that changes what a later line resolves ---------------------------------

    def test_a_script_line_that_changes_INTERPRETER_LOOKUP_is_refused_wherever_it_appears(self):
        """Ten shell constructs that decide WHICH interpreter a later line starts.

        THE ASSIGNMENT ROWS ARE THE SECOND HALF OF THE REVIEWER'S FINDING, in the spelling the old
        guard was closest to catching: `PYTHONPATH=/nowhere python3 x.py` was already refused
        because the command was Python, but `export PATH=...` ON ITS OWN LINE was not, and it
        disarms every later line in the file. The rest are the routes that get there without an
        assignment: `$PY`, `eval`, `exec -a`, `hash -p`, a sourced file, and `module load`.
        """
        child, sentinel = self.hijacking_child("hijack_lookup")
        quoted = shlex.quote(str(child))
        write(self.nd / "setup.sh", "export PATH=/usr/bin:/bin\n")
        cases = (
            ("export PATH", f"export PATH=/usr/bin:/bin\npython3 {quoted}\n",
             mgr.LAUNCH_REASON_ENV, "PATH"),
            ("unset PYTHONPATH", f"unset PYTHONPATH\npython3 {quoted}\n",
             mgr.LAUNCH_REASON_ENV, "PYTHONPATH"),
            ("declare -x PYTHONHOME", f"declare -x PYTHONHOME=/nowhere\npython3 {quoted}\n",
             mgr.LAUNCH_REASON_ENV, "PYTHONHOME"),
            ("readonly BASH_ENV", f"readonly BASH_ENV=/tmp/pre.sh\npython3 {quoted}\n",
             mgr.LAUNCH_REASON_ENV, "BASH_ENV"),
            ("module load", f"module load python\npython3 {quoted}\n",
             mgr.LAUNCH_REASON_ENV, "module load"),
            ("source resets PATH", f"source ./setup.sh\npython3 {quoted}\n",
             mgr.LAUNCH_REASON_ENV, "PATH"),
            ("indirect command word", f"PY=/usr/bin/python3\n$PY {quoted}\n",
             mgr.LAUNCH_REASON_UNPARSED, "$PY"),
            ("eval", f'eval "python3 -I {quoted}"\n', mgr.LAUNCH_REASON_UNPARSED, "eval"),
            ("exec -a", f"exec -a innocent python3 -I {quoted}\n",
             mgr.LAUNCH_REASON_UNPROVEN, "-a"),
            ("hash -p", f"hash -p /usr/bin/python3 python3\npython3 -I {quoted}\n",
             mgr.LAUNCH_REASON_UNPROVEN, "hash -p"),
            ("alias", f"alias python3=/usr/bin/python3\npython3 {quoted}\n",
             mgr.LAUNCH_REASON_UNPROVEN, "alias"),
        )
        for name, body, reason, offending in cases:
            with self.subTest(construct=name):
                self.inventory.unlink(missing_ok=True)
                sentinel.unlink(missing_ok=True)
                result = self.launch_script("lookup", body, cwd=self.nd)
                self.assertRefusedBeforeLaunch(result, sentinel, reason, offending)

    def test_a_shell_that_would_run_a_STARTUP_FILE_first_is_refused_end_to_end(self):
        """`bash -l script.sh`, `BASH_ENV=... bash script.sh`, and `zsh script.sh`.

        In each of them a program this guard was never handed runs before -- or instead of -- the
        one it read. `/etc/profile` is not a hypothetical: OI-179 defect 1 put `$HOME/bin` on PATH
        through a conditional at `/etc/profile:171`, with no edit to any file this campaign tracks,
        so a login shell is a PATH this scan cannot see.
        """
        child, sentinel = self.hijacking_child("hijack_startup")
        script = write(self.nd / "startup_target.sh",
                       f"python3 {shlex.quote(str(child))}\n")
        launches = {
            "bash -l": f"subprocess.run(['/bin/bash', '-l', {str(script)!r}])",
            "bash -i": f"subprocess.run(['/bin/bash', '-i', {str(script)!r}])",
            "BASH_ENV in the child env": (
                "subprocess.run(['/bin/bash', %r], "
                "env=dict(os.environ, BASH_ENV='/tmp/preamble.sh'))" % str(script)),
            "ENV in the child env": (
                "subprocess.run(['/bin/sh', %r], "
                "env=dict(os.environ, ENV='/tmp/preamble.sh'))" % str(script)),
            "zsh without -f": f"subprocess.run(['/bin/zsh', {str(script)!r}])",
        }
        for name, call in launches.items():
            with self.subTest(launch=name):
                self.inventory.unlink(missing_ok=True)
                sentinel.unlink(missing_ok=True)
                parent = write(self.nd / "parent_startup.py",
                               "import os, subprocess\n"
                               f"raise SystemExit({call}.returncode)\n")
                self.assertRefusedBeforeLaunch(self.guarded(parent), sentinel,
                                               mgr.LAUNCH_REASON_UNPROVEN)

    @unittest.skipUnless(shutil.which("zsh"), "no zsh on this platform")
    @unittest.skipUnless(shutil.which("zsh"), "no zsh on this platform")
    def test_zsh_IS_REFUSED_NOW_THAT_AN_ADMITTED_SHELL_MUST_RUN_AS_RESTRICTED_BASH(self):
        """`zsh -f script.sh`, WHICH USED TO BE ADMITTED AND READ, and why that changed.

        THE PREDECESSOR ASSERTED THE OPPOSITE OF THIS AND WAS RIGHT AT THE TIME. `-f` suppresses
        `.zshenv`, so the script WAS the first program to run and the scanner could read it; the
        refusal it produced named the script's own `-I`, which is a stronger claim than "zsh is
        banned" and the arm existed to make it.

        ROUND 7 REMOVED THE THING THAT MADE READING SUFFICIENT. An admitted shell is no longer run
        as the caller spelled it: it is rewritten to `bash -r` with a wrapper-only PATH, and that
        is now where the guarantee comes from rather than from the scan. A zsh program cannot be
        rewritten onto `bash -r` -- it is a different language, and running it there would change
        what the launcher computes -- and zsh's own restricted mode is not modelled here. So a
        shell this file can READ but cannot ENFORCE is refused, and the reason says which:
        `a-child-this-guard-cannot-prove-keeps-its-launches-guarded`, offending `zsh`.

        THE SCRIPT IS STILL A HIJACKING ONE, deliberately, so the arm keeps proving the sentinel is
        absent rather than only that a reason string changed.
        """
        child, sentinel = self.hijacking_child("hijack_zsh_f")
        script = write(self.nd / "zsh_target.sh", f"python3 -I {shlex.quote(str(child))}\n")
        parent = write(self.nd / "parent_zsh_f.py",
                       "import subprocess\n"
                       f"raise SystemExit(subprocess.run(['/bin/zsh', '-f', {str(script)!r}])"
                       ".returncode)\n")
        self.assertRefusedBeforeLaunch(self.guarded(parent), sentinel,
                                       mgr.LAUNCH_REASON_UNPROVEN, "zsh")

    def test_a_HERE_DOCUMENT_body_is_data_and_the_shell_reading_stdin_is_what_refuses(self):
        """`sh <<EOF` in a script: refused for having no operand, NOT for the `-I` in its body.

        BOTH HALVES ARE ASSERTED BY THE ONE REASON. If the body were scanned as commands the reason
        would be `python-startup-flags-bypass-the-shim`; if the opening line were skipped with its
        body there would be no refusal at all. `a-child-this-guard-cannot-prove...` is the only
        outcome consistent with "the body is data AND the shell reading it cannot be scanned".
        """
        child, sentinel = self.hijacking_child("hijack_heredoc")
        result = self.launch_script(
            "heredoc",
            "sh <<EOF\n"
            f"python3 -I {shlex.quote(str(child))}\n"
            "EOF\n")
        record = self.assertRefusedBeforeLaunch(result, sentinel, mgr.LAUNCH_REASON_UNPROVEN)
        self.assertIn("stdin", record["launch_refusal"]["offending_flag"])

    def test_a_here_document_payload_does_NOT_refuse_a_correct_python_launch(self):
        """The silent direction, and the one that decides whether the rule above is usable.

        `python3 - <<EOF` feeds a program on stdin. Its payload lines are `import` statements and
        assignments, which as COMMANDS would each be an unprovable child -- so a scanner that read
        the body would refuse a correct launch, and this guard would be switched off. The launch is
        the command word, the payload is data, and the child runs.
        """
        parent = write(
            self.nd / "parent_heredoc_ok.py",
            "import subprocess\n"
            "script = 'python3 - <<EOF\\n"
            "import sys\\n"
            "print(\"HEREDOC-CHILD-RAN\")\\n"
            "EOF\\n'\n"
            "raise SystemExit(subprocess.run(['/bin/bash', '-c', script]).returncode)\n",
        )
        result = self.guarded(parent)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("HEREDOC-CHILD-RAN", result.stdout)
        self.assertNotIn("[oi136 launch]", result.stderr)
        self.assertEqual({record["depth"] for record in self.records()}, {0, 1})

    # --- the admitted directions, which are what make the closure usable -------------------------

    def test_an_ABSOLUTE_PATH_interpreter_WITHOUT_an_isolating_flag_is_admitted_and_GUARDED(self):
        """The other half of the retired absolute-path gap, and the more important half.

        `/abs/python3 child.py` used to be admitted for the wrong reason -- "an absolute path
        consults no PATH, so we cannot see it" -- and `/abs/python3 -I child.py` was admitted for
        the same wrong reason. The path spelling is now read either way, and this arm proves the
        reading did not turn into a ban: the child RUNS, it loads the RIGHT tree, and the depth-1
        record proves it started GUARDED rather than merely started.
        """
        clean = self.clean_child()
        parent = write(
            self.nd / "parent_abs_clean.py",
            "import subprocess\n"
            f"raise SystemExit(subprocess.run([{sys.executable!r}, {str(clean)!r}]).returncode)\n",
        )
        result = self.guarded(parent)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("CHILD-LOADED RIGHT TREE", result.stdout)
        self.assertNotIn("[oi136 launch]", result.stderr)
        records = {record["depth"]: record for record in self.records()}
        self.assertEqual(set(records), {0, 1})
        self.assertEqual(records[1]["propagated_from"], records[0]["pid"])
        self.assertEqual(records[1]["propagation"], "armed")

    def test_a_SCRIPT_whose_every_line_is_admissible_runs_and_its_child_is_GUARDED(self):
        """The silent direction for the whole closure, in the shape a launcher actually has.

        `set -euo pipefail`, `mkdir -p`, `python3 <script>`, a digest tool. If any one of
        these refused, the closed model would be unusable and the guard would be removed rather
        than fixed -- which is why this arm is here and why the digest tool is CHOSEN BY
        MEASUREMENT: an absent leaf refuses, so a row naming a tool this machine lacks would fail
        for a reason that has nothing to do with the rule.

        `cd` AND `> /dev/null` USED TO BE IN THIS SCRIPT AND ARE GONE, and that is a real narrowing
        rather than a fixture tidy-up. The static scan still admits both; RESTRICTED BASH refuses
        both, because the round-7 model is that an admitted shell runs under bash's own restricted
        mode. A launcher that changes directory or redirects now has to be respelled -- with an
        absolute path, or by letting the Python child do the writing. The refusals themselves are
        asserted in `TheRestrictedShellIsTheSecondLayerAndRefusesOnItsOwn`, so this arm's silence
        about them is not the only record of the change.
        """
        digest = next((name for name in ("sha256sum", "md5sum", "cksum")
                       if shutil.which(name)
                       and mgr._under_a_system_prefix(shutil.which(name))
                       and mgr._read_shebang(shutil.which(name)) is None), None)
        self.assertIsNotNone(digest, "no shebang-free digest leaf under a system prefix here")
        clean = self.clean_child()
        result = self.launch_script(
            "clean_pipeline",
            "set -euo pipefail\n"
            f"mkdir -p {shlex.quote(str(self.tmp / 'out'))}\n"
            f"python3 {shlex.quote(str(clean))}\n"
            f"{digest} {shlex.quote(str(clean))}\n")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("CHILD-LOADED RIGHT TREE", result.stdout)
        self.assertNotIn("[oi136 launch]", result.stderr)
        records = {record["depth"]: record for record in self.records()}
        self.assertEqual(set(records), {0, 1}, "the script's python child left no record")
        self.assertEqual(records[1]["propagation"], "armed")

    def test_a_FUNCTION_body_is_scanned_and_a_CALL_to_the_name_is_then_admitted(self):
        """Both directions over function definitions, which every launcher in this tree uses.

        `mnv_inv() { ...; }` is the live shape -- see the eight k=0 launchers. The definition line
        must not read as a call to an unknown word, the body must be scanned, and a later call must
        be admitted because of that scan. The refusing arm puts the `-I` INSIDE the body, so only a
        scan of the body can produce it.
        """
        child, sentinel = self.hijacking_child("hijack_function")
        quoted = shlex.quote(str(child))
        result = self.launch_script("function_bad",
                                    f"go() {{ python3 -I {quoted}; }}\ngo\n")
        self.assertRefusedBeforeLaunch(result, sentinel, mgr.LAUNCH_REASON_FLAGS, "-I")
        self.inventory.unlink(missing_ok=True)
        clean = self.clean_child()
        result = self.launch_script(
            "function_ok",
            f"go() {{ python3 {shlex.quote(str(clean))}; }}\ngo\n")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("CHILD-LOADED RIGHT TREE", result.stdout)
        self.assertEqual({record["depth"] for record in self.records()}, {0, 1})

    def test_a_COMMAND_SUBSTITUTION_hides_no_launch_and_breaks_no_correct_one(self):
        """`X=$(python3 -I x.py)` is refused; `X=$(date)` is not.

        A substitution's inside IS A PROGRAM THAT RUNS, so it is scanned as one -- otherwise the
        isolated interpreter in the first row is an assignment with an opaque value and nothing
        ever looks at it. The second row is the arm that keeps that from being a ban on `$( )`.
        """
        child, sentinel = self.hijacking_child("hijack_subst")
        result = self.launch_script(
            "subst_bad", f"OUT=$(python3 -I {shlex.quote(str(child))})\necho \"$OUT\"\n")
        self.assertRefusedBeforeLaunch(result, sentinel, mgr.LAUNCH_REASON_FLAGS, "-I")
        self.inventory.unlink(missing_ok=True)
        clean = self.clean_child()
        result = self.launch_script(
            "subst_ok",
            "STAMP=$(date -u +%Y)\n"
            f"echo \"$STAMP\"\npython3 {shlex.quote(str(clean))}\n")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("CHILD-LOADED RIGHT TREE", result.stdout)
        self.assertNotIn("[oi136 launch]", result.stderr)

    # --- the tools the closure has to keep working --------------------------------------------

    #: The `git` spellings THIS REPOSITORY'S guarded code actually runs, measured by grepping
    #: `subprocess` over non-test `nd-unfolding/` and `docs/orchestration/`. Each is admitted.
    ADMITTED_GIT = (
        ["rev-parse", "HEAD"],
        ["rev-parse", "--short", "HEAD"],
        ["rev-parse", "--git-dir"],
        ["rev-parse", "--show-toplevel"],
        ["rev-parse", "--is-inside-work-tree"],
        ["ls-files"],
        ["ls-files", "-z"],
        ["ls-tree", "-r", "--name-only", "HEAD"],
        ["hash-object", "--", "AGENTS.md"],
        ["cat-file", "-e", "HEAD^{commit}"],
        ["merge-base", "--is-ancestor", "HEAD", "HEAD"],
        ["status", "--porcelain"],
        ["symbolic-ref", "--quiet", "--short", "HEAD"],
        ["rev-list", "--count", "HEAD"],
        ["log", "--format=%H", "--no-ext-diff", "-1"],
        ["config", "--get", "user.name"],
    )

    def test_the_git_spellings_this_repo_RUNS_are_admitted_and_the_dangerous_ones_are_not(self):
        """Both directions over the `git` allowlist, end to end, from a guarded parent.

        THE ADMITTED ROWS WERE MEASURED, NOT IMAGINED: they are the spellings a grep of
        `subprocess` over non-test `nd-unfolding/` and `docs/orchestration/` produces. An allowlist
        written from memory would refuse the provenance checks this campaign's evidence rests on,
        and it would do so on the cluster rather than here.

        THE ENVIRONMENT IS FILTERED BY THE PARENT because this machine exports `GIT_EDITOR=true`.
        That is not a fixture convenience -- it is the measured operational consequence of the rule,
        and the last row asserts it: with `GIT_PAGER` set, the same admitted `git rev-parse HEAD` is
        refused.
        """
        for arguments in self.ADMITTED_GIT:
            with self.subTest(git=" ".join(arguments)):
                self.inventory.unlink(missing_ok=True)
                parent = write(
                    self.nd / "parent_git_ok.py",
                    "import os, subprocess\n"
                    "env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}\n"
                    f"subprocess.run(['git', *{arguments!r}], cwd={str(REPO)!r}, env=env,\n"
                    "               capture_output=True)\n"
                    "print('GIT-RAN')\n",
                )
                result = self.guarded(parent)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("GIT-RAN", result.stdout)
                self.assertNotIn("[oi136 launch]", result.stderr)
        refused = (
            ("global -c can name an alias that runs anything",
             ["-c", "alias.x=!python3 -I /tmp/x.py", "x"], {}),
            ("diff without --no-ext-diff can run diff.external", ["diff", "--name-only"], {}),
            ("log without --no-ext-diff", ["log", "--format=%H", "-1"], {}),
            ("config without a reading option", ["config", "user.name"], {}),
            ("--exec-path relocates git's own helpers", ["--exec-path=/tmp", "status"], {}),
            ("GIT_PAGER in the environment", ["rev-parse", "HEAD"], {"GIT_PAGER": "/tmp/p"}),
            ("GIT_EXTERNAL_DIFF in the environment", ["diff-tree", "HEAD"],
             {"GIT_EXTERNAL_DIFF": "/tmp/d"}),
        )
        for name, arguments, extra in refused:
            with self.subTest(refused=name):
                self.inventory.unlink(missing_ok=True)
                parent = write(
                    self.nd / "parent_git_bad.py",
                    "import os, subprocess\n"
                    "env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}\n"
                    f"env.update({extra!r})\n"
                    f"subprocess.run(['git', *{arguments!r}], cwd={str(REPO)!r}, env=env,\n"
                    "               capture_output=True)\n"
                    "print('GIT-RAN')\n",
                )
                result = self.guarded(parent)
                self.assertEqual(result.returncode, mgr.VIOLATION_EXIT,
                                 result.stdout + result.stderr)
                self.assertIn("[oi136 launch]", result.stderr)
                self.assertNotIn("GIT-RAN", result.stdout)
                self.assertEqual(self.records()[0]["launch_refusal"]["reason"],
                                 mgr.LAUNCH_REASON_UNPROVEN)

    def test_sbatch_is_a_WRAPPER_OVER_A_SCRIPT_and_the_script_is_read_before_submission(self):
        """`sbatch job.sh` where `job.sh` runs `python3 -I`, and the clean counterpart.

        THE SCRIPT IS READ NOW OR NEVER: everything a batch script launches runs later, on a
        compute node, out of reach of this interpreter AND of the PATH wrappers. `#SBATCH` lines
        are comments and are inert, which the dirty row proves by refusing on the `-I` that comes
        after them rather than on a directive.

        WHAT IS MEASURED FOR THE CLEAN ROW, ON THIS MACHINE, is stated rather than assumed. `sbatch`
        is classified by BASENAME (it is a modelled wrapper, not a leaf trusted by location), so a
        clean batch script is ADMITTED whether or not Slurm is installed.

        WHAT THE ADMITTED LAUNCH THEN REACHES CHANGED IN ROUND 7, and the change is why the
        Slurm-less row below no longer expects `FileNotFoundError`. A guarded process now carries a
        COMMITTED `sbatch` wrapper on `PATH` -- it has to, because a restricted shell's PATH is the
        wrapper directory and a submission from one would otherwise be `command not found` -- so
        `sbatch` always resolves to a file that exists. On a host with no Slurm the wrapper reports
        that no such tool sits under any named system prefix and exits 127, which is what the shell
        would have said itself. That is not a refusal: no `[oi136 launch]`, and the record carries
        no launch refusal. A stub `sbatch` in front of the wrapper is used for the second half so
        the admission is measured by a process that actually ran, not only by an absent refusal.
        """
        child, sentinel = self.hijacking_child("hijack_sbatch")
        write(self.nd / "job_bad.sh",
              "#!/bin/bash\n"
              "#SBATCH --job-name=mnv\n"
              "#SBATCH --export=NONE\n"
              f"python3 -I {shlex.quote(str(child))}\n")
        parent = write(
            self.nd / "parent_sbatch_bad.py",
            "import subprocess\n"
            f"raise SystemExit(subprocess.run(['sbatch', {str(self.nd / 'job_bad.sh')!r}])"
            ".returncode)\n")
        record = self.assertRefusedBeforeLaunch(self.guarded(parent), sentinel,
                                                mgr.LAUNCH_REASON_FLAGS, "-I")
        self.assertEqual(record["launch_refusal"]["argv"][0], "sbatch")

        self.inventory.unlink(missing_ok=True)
        clean = self.clean_child()
        write(self.nd / "job_ok.sh",
              "#!/bin/bash\n#SBATCH --job-name=mnv\n"
              f"python3 {shlex.quote(str(clean))}\n")
        if shutil.which("sbatch") is None:
            parent = write(
                self.nd / "parent_sbatch_notfound.py",
                "import subprocess\n"
                f"code = subprocess.run(['sbatch', {str(self.nd / 'job_ok.sh')!r}]).returncode\n"
                "print('SBATCH-EXIT', code)\n")
            result = self.guarded(parent)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            # 127, from the COMMITTED wrapper, is `command not found` under another name: the
            # launch was admitted and the host has no Slurm. The distinction that matters is that
            # it is not 3 and there is no `[oi136 launch]` line, so nothing here was refused.
            self.assertIn("SBATCH-EXIT 127", result.stdout)
            self.assertNotIn("[oi136 launch]", result.stderr)
            self.assertIsNone(self.records()[0]["launch_refusal"])
        stub_dir = self.tmp / "stub-bin"
        stub_dir.mkdir(exist_ok=True)
        stub = stub_dir / "sbatch"
        stub.write_text("#!/bin/sh\nprintf 'SUBMITTED %s\\n' \"$1\"\n")
        stub.chmod(0o755)
        self.inventory.unlink(missing_ok=True)
        parent = write(
            self.nd / "parent_sbatch_ok.py",
            "import os, subprocess\n"
            f"env = dict(os.environ, PATH={str(stub_dir)!r} + os.pathsep + os.environ['PATH'])\n"
            f"raise SystemExit(subprocess.run(['sbatch', {str(self.nd / 'job_ok.sh')!r}], "
            "env=env).returncode)\n")
        result = self.guarded(parent)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("SUBMITTED", result.stdout)
        self.assertNotIn("[oi136 launch]", result.stderr)

    def test_sbatch_refuses_an_export_that_drops_the_contract_and_an_unmodelled_option(self):
        """`--export=NONE` on the COMMAND LINE (not the directive) and an option not in the table.

        The directive form inside the script is a comment and is inert -- the arm above has one.
        On the argv it decides which of the submitter's environment reaches the task, and the
        propagation contract lives in that environment.
        """
        clean = self.clean_child()
        write(self.nd / "job_export.sh", f"#!/bin/bash\npython3 {shlex.quote(str(clean))}\n")
        for arguments, reason in ((["--export=NONE"], mgr.LAUNCH_REASON_ENV),
                                  (["--export=ALL,HOME=/tmp"], mgr.LAUNCH_REASON_ENV),
                                  (["--not-an-sbatch-option=1"], mgr.LAUNCH_REASON_UNMODELLED)):
            with self.subTest(arguments=arguments):
                self.inventory.unlink(missing_ok=True)
                parent = write(
                    self.nd / "parent_sbatch_export.py",
                    "import subprocess\n"
                    f"raise SystemExit(subprocess.run(['sbatch', *{arguments!r}, "
                    f"{str(self.nd / 'job_export.sh')!r}]).returncode)\n")
                result = self.guarded(parent)
                self.assertEqual(result.returncode, mgr.VIOLATION_EXIT,
                                 result.stdout + result.stderr)
                self.assertIn("[oi136 launch]", result.stderr)
                self.assertEqual(self.records()[0]["launch_refusal"]["reason"], reason)
        # NO OPERAND: sbatch reads its batch script from STDIN, which is the same state a bare
        # `bash` is in and refuses for the same reason -- the program does not exist as bytes this
        # scan can reach. Both spellings, because the parse reaches them by different exits.
        for arguments in (["sbatch"], ["sbatch", "--parsable"]):
            with self.subTest(arguments=arguments):
                self.inventory.unlink(missing_ok=True)
                parent = write(self.nd / "parent_sbatch_stdin.py",
                               "import subprocess\n"
                               f"raise SystemExit(subprocess.run({arguments!r}).returncode)\n")
                result = self.guarded(parent)
                self.assertEqual(result.returncode, mgr.VIOLATION_EXIT,
                                 result.stdout + result.stderr)
                self.assertEqual(self.records()[0]["launch_refusal"]["reason"],
                                 mgr.LAUNCH_REASON_UNPROVEN)
                self.assertIn("stdin", self.records()[0]["launch_refusal"]["offending_flag"])

    def test_a_child_that_execs_a_program_ITS_OWN_ARGUMENTS_NAME_is_refused_as_UNPROVEN(self):
        """`perl -e exec`, `find -exec`, `make`, `ssh`: four ways to start `python3 -I` with no
        `python3` command word anywhere for a scan to find.

        THIS IS WHY THE LEAF TABLE IS SHORT. Every one of these is a perfectly ordinary tool, and
        every one of them runs a program named by its arguments -- so admitting any of them by
        basename would admit the reviewer's finding in a spelling that never mentions an
        interpreter. `perl -e 'exec "python3","-I",...'` is the shortest of the four.
        """
        child, sentinel = self.hijacking_child("hijack_unknown")
        quoted = str(child)
        launches = {
            "perl -e exec": ["perl", "-e", f'exec "python3","-I","{quoted}"'],
            "find -exec": ["find", str(self.nd), "-name", "*.py", "-exec",
                           "python3", "-I", "{}", ";"],
            "make": ["make", "-f", "/dev/null", "all"],
            "ssh": ["ssh", "localhost", "python3", "-I", quoted],
        }
        for name, argv in launches.items():
            with self.subTest(launch=name):
                self.inventory.unlink(missing_ok=True)
                sentinel.unlink(missing_ok=True)
                parent = write(self.nd / "parent_unknown.py",
                               "import subprocess\n"
                               f"raise SystemExit(subprocess.run({argv!r}).returncode)\n")
                self.assertRefusedBeforeLaunch(self.guarded(parent), sentinel,
                                               mgr.LAUNCH_REASON_UNPROVEN)

    def test_a_LEAF_NAME_that_is_really_a_SCRIPT_is_read_end_to_end_and_not_trusted(self):
        """A file called `ls`, `#!/bin/sh`, `python3 -I` inside, FIRST on the child's PATH.

        The refusal names `-I`, so what fired is the startup-flag grammar reading the impostor's
        contents -- a refusal saying only "not a leaf" would be consistent with never opening the
        file. This is the end-to-end counterpart of the in-process arm in
        `TheLaunchGrammarIsParsedAndFailsClosed`, and it is here because the reviewer's route was a
        FILE ON DISK rather than a parser input.
        """
        child, sentinel = self.hijacking_child("hijack_leaf_impostor")
        impostor_dir = self.tmp / "impostor-bin"
        impostor_dir.mkdir()
        impostor = impostor_dir / "ls"
        impostor.write_text(f"#!/bin/sh\npython3 -I {shlex.quote(str(child))}\n")
        impostor.chmod(0o755)
        parent = write(
            self.nd / "parent_leaf_impostor.py",
            "import os, subprocess\n"
            f"env = dict(os.environ, PATH={str(impostor_dir)!r} + os.pathsep "
            "+ os.environ['PATH'])\n"
            "raise SystemExit(subprocess.run(['ls', '-l'], env=env).returncode)\n")
        self.assertRefusedBeforeLaunch(self.guarded(parent), sentinel,
                                       mgr.LAUNCH_REASON_FLAGS, "-I")


class TheStartupFlagScanFollowsCPythonsOptionGrammar(unittest.TestCase):
    """A TABLE OVER THE SCANNER ITSELF, called directly, and it is deliberately in-process.

    Every behavioural test in this file runs a real subprocess because the thing under test is an
    exit code. This one is not behavioural: `_forbidden_python_flag` is a pure function of an argv,
    and the interesting inputs are the ones CPython's option grammar makes ambiguous. Enumerating
    them end-to-end would be ~30 subprocess launches to re-measure one function; the two end-to-end
    ANCHORS -- one per direction -- are
    `TheSubprocessBoundaryIsCovered.test_a_flag_after_an_option_VALUE_is_still_refused` and
    `...test_an_option_VALUE_that_contains_S_I_or_E_is_not_a_forbidden_flag`, so the function's
    verdict is tied to a real refusal at both ends.

    BOTH DIRECTIONS ARE REQUIRED. A scan that only fires on bad input passes while waving through
    every spelling it does not model, and a scan that only stays silent on good input is satisfied
    by refusing nothing.
    """

    REFUSED = (
        (["python3", "-S", "x.py"], "-S"),
        (["python3", "-I", "x.py"], "-I"),
        (["python3", "-E", "x.py"], "-E"),
        (["python3", "-IS", "x.py"], "-IS"),
        (["python3", "-Es", "x.py"], "-Es"),
        (["python3", "-OI", "x.py"], "-OI"),
        (["python3", "-SW", "ignore", "x.py"], "-SW"),
        # The value in the NEXT token: the flag behind it must still be seen.
        (["python3", "-W", "ignore", "-I", "x.py"], "-I"),
        (["python3", "-X", "dev", "-S", "x.py"], "-S"),
        (["python3", "--check-hash-based-pycs", "always", "-I", "x.py"], "-I"),
        # The value ATTACHED to the same token: the flag after it must still be seen.
        (["python3", "-Wignore", "-I", "x.py"], "-I"),
        # Not CPython spellings; refused anyway, since CPython would reject them too.
        (["python3", "--isolated", "x.py"], "--isolated"),
        (["python3", "--no-site", "x.py"], "--no-site"),
    )

    ALLOWED = (
        ["python3", "x.py"],
        ["python3", "-u", "x.py"],
        ["python3", "-B", "-O", "x.py"],
        # An option's VALUE is not a flag, in either spelling.
        ["python3", "-WError::UserWarning", "x.py"],
        ["python3", "-W", "error::DeprecationWarning", "x.py"],
        ["python3", "-Xpycache_prefix=/tmp/PYC-CACHE", "x.py"],
        ["python3", "-X", "importtime", "x.py"],
        ["python3", "--check-hash-based-pycs", "always", "x.py"],
        # After -c and -m every later token is the CHILD PROGRAM's argv, never a startup flag.
        ["python3", "-c", "print('-I')"],
        ["python3", "-m", "mod", "-I"],
        ["python3", "x.py", "-I"],
        ["python3", "-"],
    )

    def test_every_isolating_spelling_is_refused_and_named(self):
        for argv, offending in self.REFUSED:
            with self.subTest(argv=argv):
                self.assertEqual(mgr._forbidden_python_flag(argv), offending)

    def test_no_correct_launch_is_refused(self):
        for argv in self.ALLOWED:
            with self.subTest(argv=argv):
                self.assertIsNone(mgr._forbidden_python_flag(argv))

    def test_the_scan_reads_argv_and_never_this_interpreters_own_flags(self):
        """argv[0] is the executable, so a `-S` there is a path fragment and not a flag."""
        self.assertIsNone(mgr._forbidden_python_flag(["/opt/python-SIE/bin/python3", "x.py"]))


class TheLaunchGrammarIsParsedAndFailsClosed(unittest.TestCase):
    """A TABLE OVER THE WRAPPER GRAMMARS THEMSELVES, called directly and deliberately in-process.

    Same reasoning as the class above: `_parse_env`, `_parse_wrapper` and `_shell_command_string`
    are pure functions of an argv, the interesting inputs are the ones the two `env`
    implementations make ambiguous, and enumerating fifty of them end-to-end would be fifty
    subprocess launches to re-measure three functions. The END-TO-END ANCHORS are in
    `TheSubprocessBoundaryIsCovered`: the round-5 forms, the unmodelled option, the re-armed
    forms, the shell strings and the clean spellings each have a live refusal or a live run.

    THREE DIRECTIONS ARE REQUIRED HERE, not two. A parser that only finds the command word passes
    while mis-parsing the options in front of it; one that only refuses the unmodelled passes while
    refusing everything; and one that never REPAIRS turns a correct `env -i` launch into a refusal,
    which is how a guard gets routed around.
    """

    def parse(self, argv):
        return mgr._parse_env(argv)

    COMMAND_WORD = (
        # (argv, command, index of the command word)
        (["env", "python", "x.py"], ["python", "x.py"], 1),
        (["env", "--", "python", "-I", "x.py"], ["python", "-I", "x.py"], 2),
        (["env", "-i", "python", "x.py"], ["python", "x.py"], 2),
        (["env", "--ignore-environment", "python", "x.py"], ["python", "x.py"], 2),
        (["env", "-u", "FOO", "python", "x.py"], ["python", "x.py"], 3),
        (["env", "-uFOO", "python", "x.py"], ["python", "x.py"], 2),
        (["env", "--unset=FOO", "python", "x.py"], ["python", "x.py"], 2),
        (["env", "-C", "/tmp", "python", "x.py"], ["python", "x.py"], 3),
        (["env", "--chdir=/tmp", "python", "x.py"], ["python", "x.py"], 2),
        (["env", "-0", "python", "x.py"], ["python", "x.py"], 2),
        (["env", "--null", "-v", "--debug", "python", "x.py"], ["python", "x.py"], 4),
        (["env", "--default-signal", "python", "x.py"], ["python", "x.py"], 2),
        (["env", "--default-signal=INT", "python", "x.py"], ["python", "x.py"], 2),
        (["env", "--ignore-signal=INT", "python", "x.py"], ["python", "x.py"], 2),
        (["env", "--block-signal=INT", "python", "x.py"], ["python", "x.py"], 2),
        (["env", "--list-signal-handling", "python", "x.py"], ["python", "x.py"], 2),
        (["env", "-a", "zero", "python", "x.py"], ["python", "x.py"], 3),
        (["env", "--argv0=zero", "python", "x.py"], ["python", "x.py"], 2),
        (["env", "FOO=bar", "BAZ=qux", "python", "x.py"], ["python", "x.py"], 3),
        # `--` ends OPTIONS and not operands: an assignment behind it is still an assignment,
        # which is how both `env` implementations read it (measured against /usr/bin/env).
        (["env", "--", "FOO=bar", "python", "x.py"], ["python", "x.py"], 3),
        # A command word that LOOKS like an option is the command word once `--` has been seen.
        (["env", "--", "-weird-binary"], ["-weird-binary"], 2),
    )

    UNMODELLED = (
        ["env", "--bogus", "python", "x.py"],
        ["env", "--isolate", "python", "x.py"],
        ["env", "-P", "/usr/bin", "python", "x.py"],     # changes the utility search path
        ["env", "-Zfoo", "python", "x.py"],
        ["env", "--unknown=1", "python", "x.py"],
    )

    UNPARSEABLE = (
        ["env", "-u"],
        ["env", "-C"],
        ["env", "-S"],
        ["env", "-S", "python 'unbalanced"],
    )

    def test_the_command_word_is_found_behind_every_modelled_option(self):
        for argv, command, index in self.COMMAND_WORD:
            with self.subTest(argv=argv):
                parsed = self.parse(argv)
                self.assertIsNotNone(parsed, argv)
                self.assertEqual(parsed["command"], command)
                self.assertEqual(parsed["index"], index)
                self.assertEqual(argv[parsed["index"]], command[0])

    def test_an_unmodelled_option_refuses_and_names_itself(self):
        for argv in self.UNMODELLED:
            with self.subTest(argv=argv):
                with self.assertRaises(mgr._LaunchRefusal) as caught:
                    self.parse(argv)
                self.assertEqual(caught.exception.reason, mgr.LAUNCH_REASON_UNMODELLED)
                self.assertIn(caught.exception.offending, argv)

    def test_a_prefix_that_cannot_be_parsed_refuses_rather_than_passing(self):
        for argv in self.UNPARSEABLE:
            with self.subTest(argv=argv):
                with self.assertRaises(mgr._LaunchRefusal) as caught:
                    self.parse(argv)
                self.assertEqual(caught.exception.reason, mgr.LAUNCH_REASON_UNPARSED)

    def test_a_split_string_is_parsed_as_env_arguments_and_not_assumed_to_be_the_command(self):
        """`-S` can carry options and assignments, so the split result re-enters the parser."""
        parsed = self.parse(["env", "-S", "-i FOO=bar python -I x.py"])
        self.assertEqual(parsed["command"], ["python", "-I", "x.py"])
        self.assertTrue(parsed["clears"])
        self.assertEqual(parsed["assignments"], {"FOO": "bar"})
        # NO INJECTION POINT: the command word no longer corresponds to a position in the argv the
        # caller passed, and inserting an operand at a made-up index is how a repair corrupts.
        self.assertIsNone(parsed["index"])

    def test_a_SHORT_OPTION_CLUSTER_is_walked_and_a_clustered_dash_i_still_CLEARS(self):
        """`env [-0iv]` is the BSD usage line, so a cluster is a legal spelling of these flags.

        BOTH DIRECTIONS WERE WRONG IN THE FIRST VERSION AND BOTH ARE PINNED HERE. A parser that
        knew only `-i` REFUSED the correct `env -iv python x.py`; and the fix's first ordering
        tested the plain-flag table before the clearing table -- `-i` is in both -- so `-iv` parsed
        as an ordinary flag and reported `clears=False`, which is a CLEARED ENVIRONMENT READ AS AN
        ARMED ONE. Measured, not hypothetical, in both directions.
        """
        for argv in (["env", "-iv", "python", "x.py"], ["env", "-vi", "python", "x.py"],
                     ["env", "-0i", "python", "x.py"], ["env", "-i", "python", "x.py"]):
            with self.subTest(argv=argv):
                parsed = self.parse(argv)
                self.assertEqual(parsed["command"], ["python", "x.py"])
                self.assertTrue(parsed["clears"], f"{argv} cleared the environment unnoticed")
        for argv in (["env", "-0v", "python", "x.py"], ["env", "-v0", "python", "x.py"]):
            with self.subTest(argv=argv):
                self.assertFalse(self.parse(argv)["clears"])
        attached = self.parse(["env", "-uFOO", "-vi", "python", "x.py"])
        self.assertEqual(attached["command"], ["python", "x.py"])
        self.assertEqual(attached["unset"], {"FOO"})
        self.assertTrue(attached["clears"])
        self.assertEqual(self.parse(["env", "-Spython -I x.py"])["command"],
                         ["python", "-I", "x.py"])

    def test_THE_JOB_LAUNCHERS_ARE_MODELLED_NOW_and_this_arm_records_what_changed(self):
        """WHAT THIS ARM USED TO ASSERT IS NOW FALSE, AND THAT IS THE FINDING RATHER THAN A REGRESSION.

        It read: "`srun`/`mpirun` are NOT parsed ... they are treated as ordinary non-Python
        children -- which means the interpreter behind them is covered by the PATH WRAPPER and not
        by this scan." Round 6 refuted the second clause for every non-Python child, `srun`
        included: three shell scripts resolved the interpreter without a PATH lookup and none of
        them met a wrapper. `srun` is therefore a modelled wrapper and `mpirun` a refusal, and the
        two rows below are the same two invocations with their verdicts inverted.

        `mpirun` IS REFUSED RATHER THAN MODELLED because Open MPI and MPICH have different option
        grammars and both accept an app-file that names further commands -- a fail-closed table over
        a grammar that varies by installation is a table that refuses correct submissions on the
        machine it was not written on.
        """
        with self.assertRaises(mgr._LaunchRefusal) as caught:
            mgr._scan_shell_string("srun -n 1 --gpus=1 python3 -I x.py", None)
        self.assertEqual(caught.exception.reason, mgr.LAUNCH_REASON_FLAGS)
        self.assertEqual(caught.exception.offending, "-I")
        with self.assertRaises(mgr._LaunchRefusal) as caught:
            mgr._scan_shell_string("mpirun -np 4 python3 -I x.py", None)
        self.assertEqual(caught.exception.reason, mgr.LAUNCH_REASON_UNPROVEN)
        # The silent direction for `srun`: a clean command behind it still runs.
        self.assertTrue(mgr._scan_shell_string("srun -n 1 python3 x.py", None))

    def test_the_LEAF_TABLE_admits_the_tools_this_repo_runs_and_refuses_the_ones_that_exec(self):
        """BOTH DIRECTIONS OVER THE LEAF TABLE, measured against THIS machine's own filesystem.

        The admitted rows are shapes the repository's guarded code actually runs. Each is admitted
        because its executable was found in a named system prefix with no shebang -- so the rows are
        SKIPPED rather than asserted where the tool is absent, because a row that passes by being
        unresolvable would be a vacuous pass in the fail-closed direction (an absent leaf REFUSES).

        The refused rows are the half that matters more: every one of them runs a program its own
        arguments name, so admitting it by basename would admit the reviewer's finding in a new
        spelling. `find . -exec python3 -I ...` and `perl -e 'exec "python3","-I"'` are written out
        because they are the two shortest ways to launch an isolated interpreter without the word
        `python3` ever being a command word.
        """
        # THE ENVIRONMENT IS SUPPLIED AND NOT INHERITED, because the git arm depends on it: this
        # machine exports `GIT_EDITOR=true`, and a fixture that read the ambient environment would
        # measure the harness rather than the rule. (That sensitivity is real and is reported --
        # see `test_git_is_refused_when_the_environment_can_make_it_run_a_program`.)
        clean = {k: v for k, v in os.environ.items()
                 if k not in mgr._GIT_EXTERNAL_PROGRAM_ENV_VARS}
        admitted = 0
        absent = []
        for text in ("cd /repo && git log --format=%H --no-ext-diff -- x.sh | head -1",
                     "sacct -j 123_4 -o State,ExitCode -P --noheader",
                     "md5sum /repo/bin/x | cut -d' ' -f1",
                     "mkdir -p /tmp/mnv && sha256sum /tmp/mnv/x",
                     "tar -czf /tmp/a.tgz /tmp/mnv"):
            words = [text.split()[0], text.split("| ")[-1].split()[0]]
            if any(shutil.which(word) is None for word in words):
                # AN ABSENT LEAF REFUSES, so a row that cannot resolve is recorded and dropped
                # rather than asserted -- and NOT with `skipTest`, which would take the whole
                # test with it and silently retire the refusal direction below.
                absent.append(text)
                continue
            with self.subTest(admitted=text):
                self.assertFalse(mgr._scan_shell_string(text, clean))
                admitted += 1
        self.assertGreaterEqual(admitted, 3,
                                f"too few resolvable leaf rows to measure; absent: {absent}")
        for text in ("ssh node01 python3 -I x.py",
                     "rsync -e 'python3 -I' a b",
                     "make -f Makefile all",
                     "perl -e 'exec \"python3\",\"-I\",\"x.py\"'",
                     "find . -name '*.py' -exec python3 -I {} ;",
                     "sudo python3 x.py",
                     "awk 'BEGIN{system(\"python3 -I x.py\")}'",
                     "sed -e 's/a/b/' f",
                     "node -e 'x'",
                     "watch python3 x.py",
                     "conda activate base",
                     "uv run python3 x.py",
                     "pyenv exec python3 x.py"):
            with self.subTest(refused=text):
                with self.assertRaises(mgr._LaunchRefusal) as caught:
                    mgr._scan_shell_string(text, None)
                self.assertIn(caught.exception.reason,
                              (mgr.LAUNCH_REASON_UNPROVEN, mgr.LAUNCH_REASON_UNPARSED))

    #: SHELL SYNTAX THAT MUST NOT HIDE A LAUNCH. Every row puts `python3 -I` somewhere the
    #: tokeniser makes it stop being the first word of a simple command, or changes what a later
    #: word resolves to. The control-flow rows are the ones that found a real fail-open shape while
    #: this was being written: `if ... ; then python3 -I y.py; fi` tokenises so that `then` is the
    #: command word and `python3 -I y.py` are its ARGUMENTS, which no flag scan would look at.
    HIDDEN_LAUNCHES = (
        "if [ -f x ]; then python3 -I y.py; fi",
        "for f in a b; do python3 -I $f; done",
        "while read l; do python3 -I x.py; done < f",
        "case $x in a) python3 -I y.py ;; b) echo hi ;; esac",
        "python3 -I x.py | cat",
        "exec python3 -I x.py",
        "time python3 -I x.py",
        "nice -n 5 python3 -I x.py",
        "OUT=`python3 -I x.py`",
        "! python3 -I x.py",
        "{ python3 -I x.py; }",
        "( cd /tmp && python3 -I x.py )",
        "python3 -I x.py &",
        "cd /tmp; command python3 -I x.py",
        "xargs python3 -I x.py",
        "trap 'python3 -I x.py' EXIT",
        # lookup changed on an EARLIER line than the launch
        "PATH+=:/tmp/bin\npython3 x.py",
        "export -n PATH\npython3 x.py",
        "local PATH=/usr/bin\npython3 x.py",
        "LD_PRELOAD=/tmp/a.so python3 x.py",
        "PYTHONSAFEPATH=1 python3 x.py",
        "MNV_GUARD_MODULE=/tmp/fake.py\npython3 x.py",
        # a function that SHADOWS the interpreter name; the body is what refuses
        'python3() { /usr/bin/python3 -I "$@"; }\npython3 x.py',
        # a program from stdin, and a shell whose grammar is not modelled
        "sh -s < prog.sh",
        "ksh script.sh",
        "srun --export=NONE python3 x.py",
    )

    #: THE SILENT DIRECTION, which decides whether the closure is usable rather than merely safe.
    #: Every row is ordinary launcher shell with NO interpreter in it, and every one must scan
    #: clean -- a rule that refused `case`, a function call or `$(date)` would make the guard
    #: something people switch off, which is the failure mode this whole file is written against.
    ORDINARY_SHELL = (
        "ls -l | wc -l",
        "cd /tmp && mkdir -p a/b",
        "if [ -f x ]; then cat x; fi",
        "for f in a b; do echo $f; done",
        "case $x in a) echo hi ;; b) cat y ;; esac",
        "helper() { echo hi; }\nhelper",
        "STAMP=$(date -u +%s)\necho $STAMP",
        "set -euo pipefail\ncd /tmp\nmkdir -p out",
        "module list",
        "trap 'rm -f /tmp/x' EXIT",
        "git rev-parse HEAD",
    )

    #: CORRECT PYTHON LAUNCHES, which must be REPORTED as Python launches -- not merely
    #: not-refused. The return value is what tells the caller the contract still has to reach the
    #: child, so a row that scanned clean but returned False would launch an unguarded interpreter
    #: from a process that had disarmed itself.
    ORDINARY_PYTHON = (
        "python3 x.py",
        "cd /tmp && python3 x.py",
        "nohup python3 x.py &",
        "python3 - <<EOF\nimport sys\nEOF",
        "srun -n 1 python3 x.py",
    )

    def test_the_shell_scanner_is_closed_in_THREE_directions_over_ordinary_shell_syntax(self):
        """One table per direction, and three directions are required rather than two.

        A scanner that only refuses the hidden launches passes while refusing everything; one that
        only admits ordinary shell passes while missing every launch; and one that does both while
        returning False for a correct `python3 x.py` would let a disarmed parent start an unguarded
        interpreter, because the return value is what asks for the contract.

        THE ENVIRONMENT IS SUPPLIED because the `git` row depends on it -- this machine exports
        `GIT_EDITOR=true`, and a fixture reading the ambient environment would be measuring the
        harness. See `test_the_git_spellings_this_repo_RUNS_are_admitted_and_the_dangerous_ones_are_not`.
        """
        clean = {k: v for k, v in os.environ.items()
                 if k not in mgr._GIT_EXTERNAL_PROGRAM_ENV_VARS}
        for text in self.HIDDEN_LAUNCHES:
            with self.subTest(hidden=text):
                with self.assertRaises(mgr._LaunchRefusal):
                    mgr._scan_shell_string(text, clean)
        for text in self.ORDINARY_SHELL:
            with self.subTest(ordinary=text):
                self.assertFalse(mgr._scan_shell_string(text, clean),
                                 "reported a Python launch where there is none")
        for text in self.ORDINARY_PYTHON:
            with self.subTest(python=text):
                self.assertTrue(mgr._scan_shell_string(text, clean),
                                "a Python launch that the caller will not ask a contract for")

    def test_a_LEAF_NAME_that_resolves_to_a_SCRIPT_is_scanned_and_never_trusted_by_name(self):
        """A file named `ls` with `#!/bin/sh` and `python3 -I` in it, FIRST on PATH.

        THE LEAF TABLE IS A LIST OF NAMES, AND A NAME IS NOT A BEHAVIOUR. If a basename were enough,
        the table would be a menu an attacker -- or a `$HOME/bin` a login profile put in front of
        `/usr/bin`, which is OI-179 defect 1 -- picks from.

        AND IT IS SCANNED RATHER THAN REFUSED FOR ITS NAME, which is the sharper claim of the two:
        the refusal names `-I`, so what fired is the startup-flag grammar reading the impostor's
        CONTENTS. A refusal that said only "not a leaf" would be consistent with never having
        opened the file.
        """
        with tempfile.TemporaryDirectory() as tmp:
            fake_bin = pathlib.Path(tmp)
            impostor = fake_bin / "ls"
            impostor.write_text("#!/bin/sh\npython3 -I /tmp/hijack.py\n")
            impostor.chmod(0o755)
            env = dict(os.environ, PATH=f"{fake_bin}{os.pathsep}{os.environ['PATH']}")
            with self.assertRaises(mgr._LaunchRefusal) as caught:
                mgr._scan_shell_string("ls -l", env)
            self.assertEqual(caught.exception.reason, mgr.LAUNCH_REASON_FLAGS)
            self.assertEqual(caught.exception.offending, "-I")
            # A COMPILED impostor cannot be read, so it is refused for its location instead.
            binary = fake_bin / "cat"
            binary.write_bytes(b"\x7fELF not really\n")
            binary.chmod(0o755)
            with self.assertRaises(mgr._LaunchRefusal) as caught:
                mgr._scan_shell_string("cat x", env)
            self.assertEqual(caught.exception.reason, mgr.LAUNCH_REASON_UNPROVEN)
            # The power arm: the SAME two commands with the impostors gone are admitted, so both
            # refusals are about the files and not about the words.
            self.assertFalse(mgr._scan_shell_string("ls -l", dict(os.environ)))
            self.assertFalse(mgr._scan_shell_string("cat x", dict(os.environ)))

    def test_a_wrapper_prefix_OUTSIDE_a_shell_string_still_disarms_what_is_INSIDE_it(self):
        """`env -i bash -c 'python3 x.py'`: the string is clean and the interpreter is not guarded.

        The clearing happens OUTSIDE the `-c` string, so a scan of the string alone sees nothing
        wrong; the interpreter inside it would nonetheless start with no contract. So the shell
        string reports whether it launches an interpreter, and the contract checks then run for
        that launch exactly as for a direct one -- repaired where the argv allows it, refused where
        it does not. A string with NO interpreter in it (`bash -c 'ls'`) is left alone, because
        requiring the contract there would refuse a launch with nothing to guard.
        """
        self.assertTrue(mgr._scan_shell_string("python3 x.py", None))
        self.assertTrue(mgr._scan_shell_string("cd /tmp && nohup python3 x.py", None))
        self.assertTrue(mgr._scan_shell_string("bash -c 'python3 x.py'", None))
        self.assertFalse(mgr._scan_shell_string("ls -l", None))
        self.assertFalse(mgr._scan_shell_string("cd /tmp && echo hi", None))
        self.assertFalse(mgr._scan_shell_string("bash -c 'ls'", None))

    def test_an_env_that_LAUNCHES_NOTHING_is_not_a_refusal(self):
        """The fail-closed rule is about what cannot be READ, never about what reads as empty."""
        for argv in (["env"], ["env", "-i"], ["env", "FOO=bar"], ["env", "--"]):
            with self.subTest(argv=argv):
                self.assertIsNone(self.parse(argv))

    def test_the_disarming_operands_are_recognised_and_the_innocent_ones_are_not(self):
        contract = dict(os.environ, MNV_GUARD_MODULE="/abs/guard.py")
        with unittest.mock.patch.dict(os.environ, contract, clear=True):
            self.assertIsNotNone(mgr._parse_env(["env", "-u", "MNV_GUARD_MODULE", "python"])
                                 ["stripped"])
            self.assertIsNotNone(mgr._parse_env(["env", "PYTHONPATH=/nowhere", "python"])
                                 ["stripped"])
            self.assertIsNone(mgr._parse_env(["env", "-u", "SOMETHING_ELSE", "python"])
                              ["stripped"])
            self.assertIsNone(mgr._parse_env(["env", "FOO=bar", "python"])["stripped"])

    WRAPPERS = (
        # (argv, command)
        (["nohup", "python", "-I", "x.py"], ["python", "-I", "x.py"]),
        (["nice", "-n", "5", "python", "x.py"], ["python", "x.py"]),
        (["nice", "-n5", "python", "x.py"], ["python", "x.py"]),
        (["nice", "--adjustment=5", "python", "x.py"], ["python", "x.py"]),
        (["nice", "-5", "python", "x.py"], ["python", "x.py"]),
        (["stdbuf", "-oL", "-eL", "python", "x.py"], ["python", "x.py"]),
        (["stdbuf", "--output=L", "python", "x.py"], ["python", "x.py"]),
        # The DURATION operand: a scan stopping at the first non-option token would read `30` as
        # the executable and never reach the interpreter behind it.
        (["timeout", "30", "python", "-I", "x.py"], ["python", "-I", "x.py"]),
        (["timeout", "-k", "5", "--signal=TERM", "30", "python", "x.py"], ["python", "x.py"]),
        (["time", "-p", "python", "x.py"], ["python", "x.py"]),
        (["xargs", "-0", "-n", "1", "python", "x.py"], ["python", "x.py"]),
        # `srun` IS A MODELLED WRAPPER SINCE ROUND 6. It used to be deliberately unmodelled, which
        # meant `srun <anything>` was admitted unread and the whole coverage claim for it rested on
        # a PATH lookup the command could decline to make.
        (["srun", "-n", "1", "--gpus=1", "python", "-I", "x.py"], ["python", "-I", "x.py"]),
        (["srun", "--export=ALL", "-N1", "python", "x.py"], ["python", "x.py"]),
        # AN OPTIONAL-ARGUMENT OPTION MUST NOT EAT THE COMMAND WORD. GNU `xargs -i` takes its
        # replacement string ATTACHED, so the bare form consumes nothing -- treating it as
        # value-taking scanned `x.py` as the executable and let the interpreter through.
        (["xargs", "-i", "python", "-I", "x.py"], ["python", "-I", "x.py"]),
        (["xargs", "-i{}", "python", "-I", "x.py"], ["python", "-I", "x.py"]),
        (["xargs", "-e", "python", "-I", "x.py"], ["python", "-I", "x.py"]),
        (["xargs", "-I", "{}", "python", "-I", "x.py"], ["python", "-I", "x.py"]),
    )

    def test_every_modelled_wrapper_resolves_to_the_command_it_runs(self):
        for argv, command in self.WRAPPERS:
            with self.subTest(argv=argv):
                spec = mgr._WRAPPER_SPECS[argv[0]]
                index = mgr._parse_wrapper(argv, spec)
                self.assertEqual(argv[index:], command)

    def test_an_unmodelled_wrapper_option_refuses(self):
        for argv in (["nohup", "-x", "python"], ["nice", "--bogus", "python"],
                     ["timeout", "--unknown=1", "30", "python"], ["xargs", "--bogus", "python"]):
            with self.subTest(argv=argv):
                with self.assertRaises(mgr._LaunchRefusal) as caught:
                    mgr._parse_wrapper(argv, mgr._WRAPPER_SPECS[argv[0]])
                self.assertEqual(caught.exception.reason, mgr.LAUNCH_REASON_UNMODELLED)

    def test_a_wrapper_that_only_REPORTS_launches_nothing(self):
        self.assertIsNone(mgr._parse_wrapper(["command", "-v", "python3"],
                                             mgr._WRAPPER_SPECS["command"]))
        self.assertIsNone(mgr._parse_wrapper(["timeout", "30"], mgr._WRAPPER_SPECS["timeout"]))

    def test_exec_dash_c_clears_the_environment_and_is_refused_as_such(self):
        with self.assertRaises(mgr._LaunchRefusal) as caught:
            mgr._parse_wrapper(["exec", "-c", "python", "x.py"], mgr._WRAPPER_SPECS["exec"])
        self.assertEqual(caught.exception.reason, mgr.LAUNCH_REASON_ENV)

    def test_a_wrapper_option_can_be_MODELLED_AND_STILL_REFUSED(self):
        """The third state this table did not have before round 6, and each row is a live route.

        `command -p` replaces PATH with the implementation's own, so the shim directory is gone and
        no wrapper stands in front of the interpreter it finds -- one of the three shell-script
        mutations the reviewer drove through. `exec -a` renames argv[0], so the record would name an
        invocation nobody can find in a process list; `exec -l` runs login startup files.

        THEY REFUSE AS MODELLED, NOT AS UNMODELLED, and the distinction is the reader's: a report of
        UNMODELLED sends a maintainer to add an option to a table it is already in.
        """
        for argv, reason in ((["command", "-p", "python3", "-I", "x.py"], mgr.LAUNCH_REASON_ENV),
                             (["exec", "-a", "zero", "python", "x.py"],
                              mgr.LAUNCH_REASON_UNPROVEN),
                             (["exec", "-l", "python", "x.py"], mgr.LAUNCH_REASON_UNPROVEN)):
            with self.subTest(argv=argv):
                with self.assertRaises(mgr._LaunchRefusal) as caught:
                    mgr._parse_wrapper(argv, mgr._WRAPPER_SPECS[argv[0]])
                self.assertEqual(caught.exception.reason, reason)
                self.assertIn(caught.exception.offending, argv)

    def test_the_job_clients_refuse_an_export_that_is_not_ALL(self):
        """`--export` decides which of the caller's environment reaches the task, and the contract
        lives in that environment. `ALL` is the only value that carries it."""
        for argv in (["srun", "--export=NONE", "python", "x.py"],
                     ["srun", "--export=ALL,HOME=/tmp", "python", "x.py"],
                     ["srun", "--export", "NONE", "python", "x.py"]):
            with self.subTest(argv=argv):
                with self.assertRaises(mgr._LaunchRefusal) as caught:
                    mgr._parse_wrapper(argv, mgr._WRAPPER_SPECS["srun"])
                self.assertEqual(caught.exception.reason, mgr.LAUNCH_REASON_ENV)
        self.assertEqual(mgr._parse_wrapper(["srun", "--export=ALL", "python", "x.py"],
                                            mgr._WRAPPER_SPECS["srun"]), 2)

    SHELL_STRINGS = (
        (["bash", "-c", "python3 x.py"], "python3 x.py"),
        (["sh", "-c", "python3 x.py"], "python3 x.py"),
        (["bash", "-ec", "python3 x.py"], "python3 x.py"),
        (["bash", "-e", "-c", "python3 x.py"], "python3 x.py"),
        (["bash", "-o", "pipefail", "-c", "python3 x.py"], "python3 x.py"),
        (["bash", "--norc", "-c", "python3 x.py"], "python3 x.py"),
        (["dash", "-c", "python3 x.py"], "python3 x.py"),
        # `zsh` USED TO BE HERE BEHIND -f/--no-rcs and is now refused outright; the rows for that
        # are in `test_a_shell_that_would_run_an_UNREADABLE_STARTUP_FILE_is_refused` and in
        # `test_zsh_IS_REFUSED_NOW_THAT_AN_ADMITTED_SHELL_MUST_RUN_AS_RESTRICTED_BASH`.
    )

    def test_the_command_string_is_found_behind_every_modelled_shell_option(self):
        for argv, text in self.SHELL_STRINGS:
            with self.subTest(argv=argv):
                self.assertEqual(mgr._shell_command_string(argv), text)

    def test_a_shell_on_a_SCRIPT_FILE_reports_the_SCRIPT_and_no_longer_None_meaning_admitted(self):
        """ROUND 6's FIRST FINDING, AS A UNIT ASSERTION ON THE PARSE ITSELF.

        The predecessor returned `None` for a script operand and `None` MEANT ADMITTED -- the old
        docstring said the script's own launch sites were the PATH wrapper's half of the contract.
        So the parse now names the file, and `_shell_command_string`'s `None` means "go and read
        that file" rather than "let it run". A shell with NO operand and no `-c` reads its program
        from stdin, which does not exist at scan time, and is refused.
        """
        for argv, path, expected in (
                (["bash", "script.sh"], "script.sh",
                 {"options": [], "posix": False, "args": []}),
                (["sh", "-e", "script.sh"], "script.sh",
                 {"options": ["-e"], "posix": True, "args": []}),
                (["bash", "--", "script.sh"], "script.sh",
                 {"options": [], "posix": False, "args": []}),
                (["bash", "-e", "--", "./stage.sh", "arg"], "./stage.sh",
                 {"options": ["-e"], "posix": False, "args": ["arg"]})):
            with self.subTest(argv=argv):
                parsed = mgr._parse_shell_invocation(argv)
                # ROUND 7 ADDED THREE KEYS AND THEY ARE ASSERTED RATHER THAN IGNORED, because they
                # are what the restricted rewrite is built from: an option silently dropped here
                # changes what the program computes, and `args` silently dropped loses its `$@`.
                self.assertEqual(parsed, {"kind": "script", "path": path, **expected})
                self.assertIsNone(mgr._shell_command_string(argv))
        for argv in (["bash"], ["sh"], ["bash", "-e"], ["sh", "-s"], ["bash", "-"]):
            with self.subTest(argv=argv):
                with self.assertRaises(mgr._LaunchRefusal) as caught:
                    mgr._parse_shell_invocation(argv)
                self.assertEqual(caught.exception.reason, mgr.LAUNCH_REASON_UNPROVEN)

    def test_a_shell_that_would_run_an_UNREADABLE_STARTUP_FILE_is_refused(self):
        """Every spelling that runs a program this guard was not handed, and each names itself.

        `-l`/`--login` and `-i`/`--interactive` source startup files; `--rcfile`/`--init-file` name
        one; `$BASH_ENV` and `$ENV` name one from the environment. In all of them the scanned
        program is not the first program to run.

        ROUND 7 ADDS THE OTHER HALF OF THE SAME SHAPE: a launch that asks for the RESTRICTION not
        to hold. `+r` turns off the restricted mode the rewrite installs, `-O restricted_shell`
        toggles it by name, and an `-o`/`-O` value this file does not model may be either under a
        name nobody read. `zsh` LEFT THIS LIST for a different table -- it is now refused as an
        unmodelled shell, not as one that reads a startup file.
        """
        for argv in (["bash", "-lc", "python3 x.py"], ["bash", "--login", "script.sh"],
                     ["bash", "-ic", "python3 x.py"], ["bash", "--interactive", "script.sh"],
                     ["bash", "--rcfile", "/tmp/rc", "-c", "python3 x.py"],
                     ["bash", "--init-file=/tmp/rc", "-c", "python3 x.py"],
                     ["bash", "+r", "-c", "python3 x.py"],
                     ["bash", "-O", "restricted_shell", "-c", "python3 x.py"],
                     ["bash", "+O", "restricted_shell", "-c", "python3 x.py"]):
            with self.subTest(argv=argv):
                with self.assertRaises(mgr._LaunchRefusal) as caught:
                    mgr._parse_shell_invocation(argv)
                self.assertEqual(caught.exception.reason, mgr.LAUNCH_REASON_UNPROVEN)
        for variable in ("BASH_ENV", "ENV"):
            with self.subTest(variable=variable):
                with self.assertRaises(mgr._LaunchRefusal) as caught:
                    mgr._parse_shell_invocation(["bash", "script.sh"],
                                                {variable: "/tmp/preamble.sh"})
                self.assertIn(variable, caught.exception.offending)
        # An `-o`/`-O` value this file does not model is refused rather than SKIPPED, which is the
        # shape an unmodelled `env` option had: the parse walked past a token that decides
        # what the shell does.
        for argv in (["bash", "-o", "privileged", "-c", "ls"],
                     ["bash", "-O", "not_a_shopt", "-c", "ls"]):
            with self.subTest(argv=argv):
                with self.assertRaises(mgr._LaunchRefusal) as caught:
                    mgr._parse_shell_invocation(argv)
                self.assertEqual(caught.exception.reason, mgr.LAUNCH_REASON_UNMODELLED)
        # And the SILENT direction: an empty value is not a startup file, and a MODELLED `-o`
        # value survives into the rewrite rather than being dropped.
        self.assertEqual(mgr._parse_shell_invocation(["bash", "script.sh"],
                                                     {"BASH_ENV": "", "ENV": ""}),
                         {"kind": "script", "path": "script.sh", "options": [], "posix": False,
                          "args": []})
        self.assertEqual(
            mgr._parse_shell_invocation(["bash", "-o", "pipefail", "-c", "ls"], {}),
            {"kind": "string", "text": "ls", "options": ["-o", "pipefail"], "posix": False,
             "args": []})

    def test_a_shell_this_guard_does_not_MODEL_is_refused_by_name_not_left_unknown(self):
        """`ksh`/`mksh`/`fish`/`csh`/`tcsh`: recognised AS SHELLS and refused for being unmodelled.

        Naming them is the point. Left out of every table they would fall through to the
        unknown-binary arm, and a reader of that refusal would conclude `csh` had not been thought
        of rather than that its startup-file and option grammar is not modelled here.
        """
        for shell in sorted(mgr._UNMODELLED_SHELL_BASENAMES):
            with self.subTest(shell=shell):
                self.assertNotIn(shell, mgr._SHELL_BASENAMES)
                self.assertNotIn(shell, mgr._LEAF_TOOL_BASENAMES)

    def test_an_unmodelled_shell_option_refuses_because_it_may_eat_the_string(self):
        for argv in (["bash", "--bogus", "-c", "python3 x.py"],
                     ["bash", "-Z", "-c", "python3 x.py"], ["bash", "-c"]):
            with self.subTest(argv=argv):
                with self.assertRaises(mgr._LaunchRefusal):
                    mgr._shell_command_string(argv)

    def test_an_unquoted_newline_is_a_command_separator_and_a_quoted_one_is_not(self):
        """The measured `shlex` hole: a newline is whitespace, so the separator disappears."""
        self.assertEqual(mgr._unquoted_lines("cd x\npython3 -I y.py"),
                         ["cd x", "python3 -I y.py"])
        self.assertEqual(mgr._unquoted_lines("python3 -c 'a\nb'"), ["python3 -c 'a\nb'"])
        with self.assertRaises(ValueError):
            mgr._unquoted_lines("python3 'unbalanced")

    def test_simple_commands_splits_on_operators_and_drops_redirection_targets(self):
        self.assertEqual(mgr._simple_commands("cd x && python3 -I y.py"),
                         [["cd", "x"], ["python3", "-I", "y.py"]])
        self.assertEqual(mgr._simple_commands("a | b ; c & d || e"),
                         [["a"], ["b"], ["c"], ["d"], ["e"]])
        # A REDIRECTION TARGET READ AS AN ARGUMENT ENDS THE FLAG SCAN EARLY, which is the round-5
        # defect in a shell's spelling. Both the operator and its target must go, and so must the
        # file-descriptor digit in front of it.
        self.assertEqual(mgr._simple_commands("python3 > /tmp/out -I y.py"),
                         [["python3", "-I", "y.py"]])
        self.assertEqual(mgr._simple_commands("python3 2>/dev/null -I y.py"),
                         [["python3", "-I", "y.py"]])
        self.assertEqual(mgr._simple_commands("python3 &> /tmp/log -I y.py"),
                         [["python3", "-I", "y.py"]])
        self.assertEqual(mgr._simple_commands("{ python3 -I y.py; }"),
                         [["python3", "-I", "y.py"]])


class TheGitAllowlistIsMEASUREDAgainstWhatThisRepoActuallyRuns(unittest.TestCase):
    """THE CENSUS OF EVERY `git` SPELLING IN NON-TEST CODE, WITH THE SITE THAT WRITES IT.

    WHY A COMMITTED TABLE AND NOT A DERIVATION. An allowlist checked against itself cannot disagree
    with itself; the population here comes from the PRODUCERS -- a grep of `subprocess` over
    non-test `nd-unfolding/` and `docs/orchestration/` on 2026-09-04 at `397a2cef` -- so the table
    is evidence about the repository rather than a restatement of `_GIT_READ_ONLY_SUBCOMMANDS`.

    AND THE REFUSED HALF IS THE POINT OF KEEPING IT. Twelve of the fifty-nine spellings this
    repository writes are REFUSED by the rule: seven `git show`, three `git diff`/`git log` without
    `--no-ext-diff`, and one `git config user.name`. That is a real cost and it is recorded as a
    LIVE ASSERTION rather than as prose in a commit message, so:

      * widening the allowlist to admit one of them turns this table red and forces the row to be
        moved deliberately rather than absorbed;
      * and nobody has to re-derive the list from memory to know what the closure costs.

    NONE OF THE TWELVE IS REACHED FROM A GUARDED PROCESS IN THE SIX-SUITE MATRIX -- measured, all
    382 tests passing -- because the launchers route the guard at science entrypoints and run these
    provenance tools outside it (ruling 21's preflight exclusion). "Not reached today" is not "safe
    to reach", which is why the sites are named.
    """

    #: (site, argv after `git`) -- admitted.
    ADMITTED = (
        ("nd-unfolding/tools_p4_sweep_pipeline_rc.py:31", ["ls-files", "*.sh"]),
        ("nd-unfolding/receipt_construction_contract_5d.py:218", ["rev-parse", "HEAD"]),
        ("nd-unfolding/receipt_construction_contract_5d.py:219", ["status", "--porcelain"]),
        ("nd-unfolding/p4_check_verifier_token.py:94", ["ls-files", "--error-unmatch", "f"]),
        ("nd-unfolding/p4_check_verifier_token.py:97", ["rev-parse", "HEAD:f"]),
        ("nd-unfolding/p4_check_verifier_token.py:98", ["hash-object", "f"]),
        ("nd-unfolding/seed_offset_policy.py:420",
         ["-C", "/repo", "ls-files", "*.sh", "**/*.sh"]),
        ("nd-unfolding/p4_evidence.py:280", ["hash-object", "f"]),
        ("nd-unfolding/p4_evidence.py:295", ["rev-parse", "abc:f"]),
        ("nd-unfolding/pet/check_canonical_designation.py:402", ["-C", "/repo", "ls-files"]),
        ("nd-unfolding/pet/acceptance_map_fullevent_fps.py:130",
         ["rev-parse", "--short", "HEAD"]),
        ("nd-unfolding/pet/verify_executing_copy_is_committed.py:97",
         ["-C", "/repo", "rev-parse", "--git-dir"]),
        ("nd-unfolding/pet/verify_executing_copy_is_committed.py:110",
         ["-C", "/repo", "cat-file", "-e", "oid^{blob}"]),
        ("nd-unfolding/pet/ff_revision_gate.py:79",
         ["-C", "/repo", "cat-file", "-e", "r^{commit}"]),
        ("nd-unfolding/mnv_source_manifest.py:95", ["-C", "/repo", "ls-files", "-z"]),
        ("nd-unfolding/mnv_source_manifest.py:120", ["-C", "/repo", "status", "--porcelain"]),
        ("nd-unfolding/p4_lib.py:542", ["ls-files"]),
        ("nd-unfolding/p4_lib.py:945", ["ls-tree", "-r", "--name-only", "rev"]),
        ("nd-unfolding/p4_lib.py:1012", ["hash-object", "--", "p"]),
        ("nd-unfolding/p4_lib.py:1036", ["merge-base", "--is-ancestor", "a", "b"]),
        ("docs/orchestration/measure_m1_m6.py:179",
         ["-C", "/repo", "symbolic-ref", "--quiet", "--short", "HEAD"]),
        ("docs/orchestration/measure_m1_m6.py:198",
         ["-C", "/repo", "rev-list", "--left-right", "--count", "a...HEAD"]),
        ("docs/orchestration/control_plane_lint.py:230",
         ["-C", "/repo", "ls-files", "-z", "--", "a"]),
        ("docs/orchestration/verify_hash_bindings.py:476", ["-C", "/repo", "ls-files", "-z"]),
        ("docs/orchestration/verify_ben_citations.py:98", ["ls-files", "*.py", "*.sh"]),
        ("docs/orchestration/campaignctl.py:755", ["-C", "/repo", "rev-parse", "HEAD"]),
        ("docs/orchestration/agentctl.py:135",
         ["-C", "/repo", "rev-parse", "--is-inside-work-tree"]),
        ("docs/orchestration/agentctl.py:146",
         ["-C", "/repo", "status", "--porcelain", "--untracked-files=all"]),
        ("docs/orchestration/generate_manifest.py:55", ["ls-files"]),
        ("docs/orchestration/verify_receipt_artifacts.py:66", ["rev-parse", "--show-toplevel"]),
        ("docs/orchestration/verify_receipt_artifacts.py:115",
         ["ls-tree", "-r", "rev", "--name-only"]),
        ("docs/orchestration/verify_receipt_artifacts.py:156",
         ["rev-parse", "--verify", "--quiet", "rev"]),
        ("docs/orchestration/generate_live_state.py:1330", ["status", "--short"]),
        ("docs/orchestration/state/gen_manifest_run_bound_addendum.py:171",
         ["-C", "/repo", "rev-parse", "HEAD"]),
    )

    #: (site, argv after `git`, the phrase the refusal must name) -- REFUSED, and left refused.
    REFUSED_REAL_LAUNCHERS = (
        ("nd-unfolding/p4_evidence.py:291", ["log", "--format=%H", "--", "f"], "--no-ext-diff"),
        ("nd-unfolding/pet/verify_executing_copy_is_committed.py:126",
         ["-C", "/repo", "log", "--all", "--oneline", "--no-abbrev-commit", "--find-object=oid"],
         "--no-ext-diff"),
        ("nd-unfolding/pet/ff_revision_gate.py:106", ["-C", "/repo", "show", "r:f"],
         "--no-ext-diff"),
        ("docs/orchestration/verify_ben_citations.py:142", ["show", "tag:f"], "--no-ext-diff"),
        ("docs/orchestration/campaignctl.py:770", ["-C", "/repo", "show", "HEAD:f"],
         "--no-ext-diff"),
        ("docs/orchestration/state/verify_manifest_precedes_artifacts.py:52",
         ["-C", "/repo", "show", "-s", "--format=%ct", "sha"], "--no-ext-diff"),
        ("docs/orchestration/verify_receipt_artifacts.py:119", ["show", "rev:f"],
         "--no-ext-diff"),
        ("docs/orchestration/whose_row.py:509", ["config", "user.name"], "git config"),
        ("docs/orchestration/whose_row.py:544", ["show", "HEAD:f"], "--no-ext-diff"),
        ("docs/orchestration/whose_row.py:787",
         ["-C", "/repo", "diff", "--name-only", "--diff-filter=U"], "--no-ext-diff"),
        ("docs/orchestration/live_doc_indexed.py:98",
         ["diff", "--cached", "--name-status"], "--no-ext-diff"),
        ("docs/orchestration/live_doc_indexed.py:103", ["show", ":OVERRIDES"], "--no-ext-diff"),
    )

    def clean(self):
        return {k: v for k, v in os.environ.items()
                if k not in mgr._GIT_EXTERNAL_PROGRAM_ENV_VARS}

    def test_every_git_spelling_this_repo_writes_is_admitted_or_LISTED_as_refused(self):
        for site, arguments in self.ADMITTED:
            with self.subTest(site=site, git=" ".join(arguments)):
                mgr._scan_git(["git", *arguments], self.clean(), "/usr/bin/git")
        for site, arguments, phrase in self.REFUSED_REAL_LAUNCHERS:
            with self.subTest(site=site, git=" ".join(arguments)):
                with self.assertRaises(mgr._LaunchRefusal) as caught:
                    mgr._scan_git(["git", *arguments], self.clean(), "/usr/bin/git")
                self.assertEqual(caught.exception.reason, mgr.LAUNCH_REASON_UNPROVEN)
                self.assertIn(phrase, caught.exception.offending)

    def test_the_census_covers_both_directions_and_neither_half_is_empty(self):
        """Power arm. A table with an empty half would make the test above vacuous in that
        direction -- and the refused half is the one a later widening would silently empty."""
        self.assertGreaterEqual(len(self.ADMITTED), 30)
        self.assertEqual(len(self.REFUSED_REAL_LAUNCHERS), 12)
        sites = [site for site, *_ in self.ADMITTED] + \
                [site for site, *_ in self.REFUSED_REAL_LAUNCHERS]
        for site in sites:
            path = site.rsplit(":", 1)[0]
            self.assertTrue((REPO / path).is_file(),
                            f"{site} no longer exists; re-measure the census rather than "
                            f"deleting the row")

    def test_a_hostile_GIT_variable_refuses_an_otherwise_admitted_spelling(self):
        """The environment half, which an argv allowlist is worth nothing without.

        `GIT_EXTERNAL_DIFF` alone turns `git diff-tree` into a launcher of an arbitrary program, so
        each of the eleven variables is checked BEFORE the subcommand -- and the arm below shows the
        same `git rev-parse HEAD` that the census admits being refused because of one of them.
        """
        for name in mgr._GIT_EXTERNAL_PROGRAM_ENV_VARS:
            with self.subTest(variable=name):
                environment = dict(self.clean(), **{name: "/tmp/anything"})
                with self.assertRaises(mgr._LaunchRefusal) as caught:
                    mgr._scan_git(["git", "rev-parse", "HEAD"], environment, "/usr/bin/git")
                self.assertIn(name, caught.exception.offending)
                # An EMPTY value is not a program: the silent direction, so the check has power
                # rather than firing on the variable's mere existence.
                mgr._scan_git(["git", "rev-parse", "HEAD"],
                              dict(self.clean(), **{name: ""}), "/usr/bin/git")


class ThePathWrapperAndItsScannerAreCalledDIRECTLY(unittest.TestCase):
    """The PATH wrapper and `scan_argv.py` as UNITS, not only through a bash child.

    WHY DIRECTLY. `TheSubprocessBoundaryIsCovered` exercises these through a guarded parent, a
    bash script and a PATH lookup, which is the shape that matters -- and it is also three layers
    that can each refuse first. A mutation to the wrapper's own decision would be masked by any of
    them, so its arms are measured here where the wrapper IS the process under test.

    THE WRAPPER'S CONTRACT: exit 0 and exec for a launch that may proceed, exit 3 and an
    `[oi136 launch]` line for one that may not, and never a launch it did not scan.
    """

    WRAPPER = SHIM_TREE / "bin" / "python3"
    SCANNER = SHIM_TREE / "scan_argv.py"

    def armed(self, **overrides):
        """The environment `install()` exports, with named variables dropped when set to None."""
        environment = dict(
            os.environ,
            PYTHONDONTWRITEBYTECODE="1",
            PYTHONPATH=str(SHIM_TREE),
            MNV_GUARD_MODULE=str(GUARD),
            MNV_GUARD_EXPECT_ROOT=str(REPO),
            MNV_GUARD_ALLOW="",
            MNV_GUARD_INVENTORY="",
            MNV_GUARD_PARENT_PID=str(os.getpid()),
            MNV_GUARD_DEPTH="1",
            MNV_GUARD_REAL_PYTHON=sys.executable,
            MNV_GUARD_PATH_SHIM_DIRS=str(SHIM_TREE / "bin"),
        )
        for name, value in overrides.items():
            if value is None:
                environment.pop(name, None)
            else:
                environment[name] = value
        return environment

    def wrapper(self, *arguments, wrapper=None, **overrides):
        return subprocess.run([str(wrapper or self.WRAPPER), *[str(a) for a in arguments]],
                              capture_output=True, text=True, env=self.armed(**overrides))

    def test_the_wrapper_is_tracked_and_executable(self):
        """A wrapper without its executable bit is skipped by PATH lookup, silently."""
        for path in (self.WRAPPER, SHIM_TREE / "bin" / "python", self.SCANNER):
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file(), path)
        self.assertTrue(os.access(self.WRAPPER, os.X_OK), self.WRAPPER)
        self.assertTrue(os.access(SHIM_TREE / "bin" / "python", os.X_OK))
        tracked = subprocess.run(
            ["git", "-C", str(REPO), "ls-files", "--", "nd-unfolding/mnv_guard_shim"],
            capture_output=True, text=True, check=True).stdout.split()
        for expected in ("nd-unfolding/mnv_guard_shim/bin/python3",
                         "nd-unfolding/mnv_guard_shim/bin/python",
                         "nd-unfolding/mnv_guard_shim/scan_argv.py",
                         "nd-unfolding/mnv_guard_shim/sitecustomize.py"):
            with self.subTest(path=expected):
                self.assertIn(expected, tracked)

    def test_a_clean_launch_passes_THROUGH_the_wrapper_to_the_real_interpreter(self):
        result = self.wrapper("-c", "import sys; print('WRAPPED', sys.executable)")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("WRAPPED", result.stdout)
        self.assertNotIn("[oi136 launch]", result.stderr)

    def test_every_isolating_spelling_is_refused_by_the_wrapper_itself(self):
        for arguments in (["-I", "-c", "print(1)"], ["-S", "-c", "print(1)"],
                          ["-E", "-c", "print(1)"], ["-IS", "-c", "print(1)"],
                          ["-W", "ignore", "-I", "-c", "print(1)"]):
            with self.subTest(arguments=arguments):
                result = self.wrapper(*arguments)
                self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
                self.assertIn("[oi136 launch]", result.stderr)
                self.assertNotIn("1\n", result.stdout)

    def test_an_option_VALUE_containing_S_I_or_E_still_reaches_the_interpreter(self):
        """The direction that gets a guard removed: the wrapper must not refuse a correct launch."""
        with tempfile.TemporaryDirectory() as cache:
            result = self.wrapper(f"-Xpycache_prefix={cache}/PYC-CACHE", "-c", "print('RAN')")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("RAN", result.stdout)

    def test_a_MISSING_contract_variable_refuses_instead_of_launching_unguarded(self):
        for name in ("MNV_GUARD_MODULE", "MNV_GUARD_EXPECT_ROOT", "MNV_GUARD_PARENT_PID"):
            with self.subTest(dropped=name):
                result = self.wrapper("-c", "print('MUST NOT RUN')", **{name: None})
                self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
                self.assertIn("[oi136 launch]", result.stderr)
                self.assertNotIn("MUST NOT RUN", result.stdout)

    def test_a_MISSING_pythonpath_is_RE_INJECTED_rather_than_refused(self):
        """PYTHONPATH is derivable from the wrapper's own location, so it is repaired.

        The distinction is the same one the guard makes everywhere: a variable this process can
        RE-DERIVE is re-armed, and one it cannot is refused. The child proves the repair by
        reporting the guard it installed.
        """
        probe = ("import sys; "
                 "print('GUARDED', any(type(f).__name__ == 'GuardedPathFinder' "
                 "for f in sys.meta_path))")
        result = self.wrapper("-c", probe, PYTHONPATH=None)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("GUARDED True", result.stdout)

    def test_the_delegating_wrapper_does_not_LEAK_its_name_to_the_child(self):
        """`MNV_GUARD_WRAPPER_NAME` must not survive the exec.

        A leaked value would make a grandchild's `python3` resolve the delegator's name instead of
        its own -- so the body unsets it, and this is the control for that one line.
        """
        result = self.wrapper(
            "-c", "import os; print('LEAK', os.environ.get('MNV_GUARD_WRAPPER_NAME'))",
            wrapper=SHIM_TREE / "bin" / "python")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("LEAK None", result.stdout)

    def test_a_deployment_missing_the_SCANNER_refuses_rather_than_guessing(self):
        with tempfile.TemporaryDirectory() as tmp:
            deployed = deploy_shim(pathlib.Path(tmp) / "mnv_guard_shim")
            (deployed / "scan_argv.py").unlink()
            result = self.wrapper("-c", "print('MUST NOT RUN')",
                                  wrapper=deployed / "bin" / "python3",
                                  MNV_GUARD_PATH_SHIM_DIRS=str(deployed / "bin"))
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        self.assertIn("TRACKED ARGV SCANNER IS MISSING", result.stderr)
        self.assertNotIn("MUST NOT RUN", result.stdout)

    def scan(self, *arguments, **overrides):
        return subprocess.run(
            [sys.executable, "-I", "-S", str(self.SCANNER), "--guard", str(GUARD), "--",
             *[str(a) for a in arguments]],
            capture_output=True, text=True, env=self.armed(**overrides))

    def test_the_scanner_answers_the_same_question_the_guard_does(self):
        """It OWNS NO GRAMMAR: the verdicts below must be `_forbidden_python_flag`'s own.

        Called directly, so a mutation to the scanner is visible here even though the wrapper and
        the bash child would each refuse first in the end-to-end arms.
        """
        for arguments in (["-I", "x.py"], ["-S", "x.py"], ["-E", "x.py"], ["-OI", "x.py"],
                          ["-W", "ignore", "-I", "x.py"], ["--isolated", "x.py"]):
            with self.subTest(arguments=arguments, expected="refused"):
                result = self.scan(*arguments)
                self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
                self.assertIn("[oi136 launch]", result.stderr)
                self.assertEqual(mgr._forbidden_python_flag(["python", *arguments]) is not None,
                                 True)
        for arguments in (["x.py"], ["-u", "x.py"], ["-Xpycache_prefix=/tmp/C", "x.py"],
                          ["-c", "print('-I')"], ["-m", "mod", "-I"], []):
            with self.subTest(arguments=arguments, expected="clean"):
                result = self.scan(*arguments)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIsNone(mgr._forbidden_python_flag(["python", *arguments]))

    def test_the_scanner_refuses_when_it_cannot_reach_the_grammar_at_all(self):
        """A scan that did not answer is not an answer, so it is a refusal."""
        missing = subprocess.run(
            [sys.executable, "-I", "-S", str(self.SCANNER), "--guard", "/nonexistent/guard.py",
             "--", "x.py"],
            capture_output=True, text=True, env=self.armed())
        self.assertEqual(missing.returncode, 3, missing.stdout + missing.stderr)
        self.assertIn("COULD NOT LOAD THE GUARD'S OWN GRAMMAR", missing.stderr)

    def test_the_scanner_refuses_a_child_that_would_start_without_the_contract(self):
        result = subprocess.run(
            [sys.executable, "-I", "-S", str(self.SCANNER), "--", "x.py"],
            capture_output=True, text=True,
            env=self.armed(MNV_GUARD_MODULE=None))
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        self.assertIn("WITHOUT THE PROPAGATION CONTRACT", result.stderr)


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
        tmp = pathlib.Path(self._tmp.name).resolve()
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
        for name in ("SITE_SCRIPT_CONTAINMENT", "SITE_IMPORT_RESOLUTION", "SITE_LAUNCH"):
            self.assertIn(name, corpus, f"{name} has no control")

    def test_the_refusal_site_constants_are_distinct_and_none_is_reserved(self):
        sites = {
            mgr.SITE_SCRIPT_CONTAINMENT,
            mgr.SITE_IMPORT_RESOLUTION,
            mgr.SITE_LAUNCH,
        }
        self.assertEqual(len(sites), 3)
        self.assertNotIn(None, sites)
        self.assertIsNone(mgr.SITE_NONE)


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
        tmp = pathlib.Path(self._tmp.name).resolve()
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
        tmp = pathlib.Path(self._tmp.name).resolve()
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
        deployed_shim = self.tree / "nd-unfolding" / "mnv_guard_shim" / "sitecustomize.py"
        deployed.write_bytes(GUARD.read_bytes())
        deployed_shim.parent.mkdir()
        deployed_shim.write_bytes(SHIM.read_bytes())
        self.assertEqual(deployed.read_bytes(), GUARD.read_bytes())
        self.assertEqual(deployed_shim.read_bytes(), SHIM.read_bytes())
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

    Each gets an arm below; `conda` gets the note it needs rather than a claim.
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


class EachInventoryReportsOneInterpreterAndSaysSo(unittest.TestCase):
    """A propagated child gets a separate record, not a merged parent inventory."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        tmp = pathlib.Path(self._tmp.name).resolve()
        self.good = make_checkout(tmp, "parent-tree")
        self.deployed_guard = self.good / "nd-unfolding" / "mnv_guarded_run.py"
        deployed_shim = self.good / "nd-unfolding" / "mnv_guard_shim" / "sitecustomize.py"
        self.deployed_guard.write_bytes(GUARD.read_bytes())
        deployed_shim.parent.mkdir()
        deployed_shim.write_bytes(SHIM.read_bytes())
        self.inventory_path = tmp / "inventory" / "separate.jsonl"
        write(self.good / "nd-unfolding" / "hidden.py", "NAME = 'hidden'\n")
        self.child = write(self.good / "nd-unfolding" / "child.py",
                           "import hidden\n"
                           "print('CHILD LOADED', hidden.NAME)\n")
        self.parent = write(self.good / "nd-unfolding" / "parent.py",
                            "import subprocess, sys\n"
                            f"subprocess.run([sys.executable, {str(self.child)!r}], check=True)\n")

    def go(self):
        return run(self.deployed_guard, "--expect-root", self.good,
                   "--inventory", self.inventory_path,
                   "--", self.parent)

    def records(self):
        return [json.loads(line) for line in self.inventory_path.read_text().splitlines()
                if line.strip()]

    def test_a_child_module_is_in_the_child_record_not_the_parent_record(self):
        cp = self.go()
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        self.assertIn("CHILD LOADED hidden", cp.stdout)
        records = {record["depth"]: record for record in self.records()}
        parent_names = {origin["fullname"] for origin in records[0]["repo_origins"]}
        child_names = {origin["fullname"] for origin in records[1]["repo_origins"]}
        self.assertNotIn("hidden", parent_names)
        self.assertIn("hidden", child_names)

    def test_the_emission_states_that_limit_where_the_reader_of_a_log_will_see_it(self):
        cp = self.go()
        self.assertIn("SCOPE -- THIS INTERPRETER ONLY", cp.stderr)
        self.assertIn("write separate records", cp.stderr)
        self.assertIn("AT LEAST these trees", cp.stderr)

    def test_the_docstring_says_so_too_where_a_maintainer_will_read_it(self):
        text = GUARD.read_text()
        self.assertIn("EACH INVENTORY RECORD COVERS ONE INTERPRETER", text)
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

        used = (names_used(funcs["loaded_checkout_roots"])
                | names_used(funcs["_emit_inventory"])
                # the MNV_REPO capture is held to the same one-resolver rule. Extending
                # this set is the point: a new function that answered "is this a checkout"
                # its own way would otherwise satisfy the rule by not being looked at.
                | names_used(funcs["_repo_env_capture"]))
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

    HOW EXPOSED THIS REPO ACTUALLY IS -- measured 2026-08-23 at `fc4fe7d1`, derived from
    the population rather than from the directories anyone thought to check, because two
    of us hand-enumerated it and got two different wrong answers (three, then four):

        git ls-files '*.py' | awk -F/ 'NF>1{print $1}' | sort -u        -> 7 trees
        ... and all 7 lack __init__.py                                  -> 7 of 7
        git grep -E '^[[:space:]]*(import|from)[[:space:]]+<tree>'      -> 0 sites, each
        git ls-files '*__init__.py'                                     -> exactly ONE

    THE 7-OF-7 IS TRUE AND DOES NOT MEAN WHAT IT LOOKS LIKE, so it is written out rather
    than quoted as a severity. Those seven are `sys.path` ENTRIES, not imported packages:

        git grep -E '^[[:space:]]*(import|from)[[:space:]]+<tree>'   -> 0 sites, each of 7

    A directory only meets this exclusion when it is imported AS a package, and today
    none of them is. The one regular package in the tree is `omnifold_nn/omnifold/`,
    which HAS `__init__.py` -- real `__file__`, COUNTED, not excluded -- and is exactly
    what the OI-126 probe's ten-module measurement exercised (`omnifold`, `.dataloader`,
    `.net`, `.omnifold`, `.utils`). That is why that measurement saw its tree at all:
    the single genuine package here is the one this exclusion cannot touch. (Import-site
    count deliberately omitted -- two patterns gave 33 and 37, neither load-bearing, and
    a number whose predicate is not stated is not worth carrying.)

    BUT "NIL TODAY" IS NOT "HYPOTHETICAL", AND THE DIFFERENCE IS WHAT KEEPS THIS ARM
    FROM BEING RETIRED. Four of the seven are LEGAL module names, and the ingredient
    that would make them live already exists in this repo:

        [t for t in trees if t.isidentifier()]
            -> docs, lib, omnifold_nn, unbinned_unfolding        (3 hyphenated, not 4)
        the repo ROOT reaching sys.path -- measured, two live routes:
            technote_style.py                       a tracked .py AT the root, so
                                                    running it puts the root at path[0]
            pet/pointcloud_projection.py:298        sys.path.insert(0, _REPO) -- the
                                                    ROOT, at POSITION 0, in live code
        with the root on sys.path, all four resolve as NAMESPACE packages,
        `spec.origin is None`, measured directly via importlib.

    So this is not "prospective for the first namespace package anyone adds". It is
    prospective for FOUR directories that already exist in the shape the exclusion is
    blind to, already reachable by an existing position-0 insert, and one import
    statement from being live. Current exposure NIL; distance to exposure, one line.

    Recorded this way because "7 of 7 trees lack __init__.py" reads as a large live
    exposure and is a correct count of a population the predicate never ranged over --
    while "someone might add one someday" is the rationale a later reader retires.
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        tmp = pathlib.Path(self._tmp.name).resolve()
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

    def test_the_scope_sentence_this_narrowing_LEANS_ON_is_required_output(self):
        """This exclusion is discharged by a sentence in the emission, so the sentence
        is load-bearing for THIS class and not only for the subprocess one.

        It was already pinned once, by
        `TheInventoryReportsOneInterpreterAndSaysSo::test_the_emission_states_that_
        limit_...`. That is not enough on its own: that test is NAMED for the
        subprocess boundary, so someone who concludes the subprocess clause is
        redundant would delete or reflow the line while looking only at a test about
        interpreters, and every arm in THIS class would still pass. A shared
        dependency needs an assertion from each side that depends on it, or the second
        dependant is invisible at the point of edit.

        The precise thing relied on: "AT LEAST these trees" is what stops a one-root
        inventory being read as "only one tree was reachable" -- which is exactly the
        reading a bare namespace-package import would make false.
        """
        cp = run(GUARD, "--expect-root", self.tree, "--", self.bare)
        self.assertIn("AT LEAST these trees", cp.stderr)
        self.assertNotIn("only these trees'.\n[oi136-inv] modules", cp.stderr)

    def test_the_residual_is_stated_where_a_PARITY_reader_would_be_misled(self):
        """Names the consumer who can misread this, because "someone might" is not a
        risk statement until it says who.

        A parity reader. This repo has the case already: a hardcoded root put a
        211-behind checkout ahead of the frozen tree and `5 of 5 CURRENT` was TRUE AND
        BLIND -- right about digests, wrong about what executed. An inventory that
        omits a namespace-package tree because nothing ran from it is right about
        EXECUTION, and a reader can turn that into "that tree is not involved" and use
        it for a PATH-level parity claim. The two questions are the ones OI-136 exists
        to keep apart, so the warning belongs in the file, not in a review comment.
        """
        text = GUARD.read_text()
        self.assertIn("MODULES THE INTERPRETER ACTUALLY LOADED", text)
        self.assertIn("are the FILES AT THESE PATHS the", text)
        # and this class's own docstring must keep saying what is lost
        self.assertIn("the tree was on the path",
                      TheNamespacePackageExclusionIsDeclaredNotSilent.__doc__)


def run_env(extra, drop, *args):
    """Like `run`, but lets a test control the child's environment.

    Separate helper rather than a kwarg on `run`, because `run` already passes `env=` and
    a second one is a TypeError, not an override.
    """
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    for k in drop:
        env.pop(k, None)
    env.update(extra)
    return subprocess.run([sys.executable, *[str(a) for a in args]],
                          capture_output=True, text=True, env=env)


class TheCaptureReportsHowTheRootWasCHOSEN(unittest.TestCase):
    """`MNV_REPO` and whether it was SET or DERIVED (OI-126 item (6), Joseph 2026-08-24,
    `DECISION-20260824-joseph-eight-dispositions-and-mnv-repo-ownership.md`).

    The inventory answers "which trees were loaded". It cannot answer "how was that tree
    chosen", and two runs with identical inventories can differ on that -- one stable
    under redeployment and one not. These arms are built from the PRODUCER's idiom
    (`os.environ.get("MNV_REPO") or os.path.dirname(...)` at
    `nd-unfolding/pet/pointcloud_projection.py:29`), not from the rule under test, per
    `PB-16`.
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        tmp = pathlib.Path(self._tmp.name).resolve()
        self.good = make_checkout(tmp, "expected-tree")
        self.other = make_checkout(tmp, "another-tree")
        self.plain = tmp / "not-a-checkout"
        self.plain.mkdir()
        self.entry = write(self.good / "nd-unfolding" / "quiet.py", "print('ran')\n")
        self.addCleanup(self._tmp.cleanup)

    def go(self, extra, drop=()):
        return run_env(extra, drop, GUARD, "--expect-root", self.good, "--", self.entry)

    # ---- arm 1: SET, and agreeing with --expect-root
    def test_SET_prints_the_value_and_says_it_agrees_with_expect_root(self):
        cp = self.go({"MNV_REPO": str(self.good)})
        self.assertEqual(cp.returncode, 0, cp.stderr)
        self.assertIn("MNV_REPO resolution=SET", cp.stderr)
        self.assertIn(repr(str(self.good)), cp.stderr)
        self.assertIn("resolves to --expect-root", cp.stderr)

    # ---- arm 2: ABSENT -- the derive-per-reader case
    def test_ABSENT_says_every_reader_derives_its_own(self):
        cp = self.go({}, drop=("MNV_REPO",))
        self.assertEqual(cp.returncode, 0, cp.stderr)
        self.assertIn("MNV_REPO resolution=ABSENT", cp.stderr)
        self.assertIn("DERIVES its own root", cp.stderr)
        self.assertNotIn("resolution=SET", cp.stderr)

    # ---- arm 3: the third state. Presence and effect disagree, and the effect is what runs.
    def test_PRESENT_BUT_EMPTY_is_not_reported_as_SET(self):
        """`MNV_REPO=""` is in the environment and every reader still derives, because
        the producer's `or` treats the empty string as absent. A capture that asked
        `"MNV_REPO" in os.environ` would call this SET and be wrong about the effect --
        which is the only thing that decides which modules execute."""
        cp = self.go({"MNV_REPO": ""})
        self.assertEqual(cp.returncode, 0, cp.stderr)
        self.assertIn("MNV_REPO resolution=PRESENT-BUT-EMPTY", cp.stderr)
        self.assertIn("presence and effect disagree", cp.stderr)
        self.assertNotIn("resolution=SET", cp.stderr)

    # ---- arm 4: THE DEFECT MUTATION FIRES. Exported root != intended root is OI-136's shape.
    def test_a_DIFFERENT_checkout_in_MNV_REPO_is_flagged_and_names_both_sides(self):
        cp = self.go({"MNV_REPO": str(self.other)})
        self.assertEqual(cp.returncode, 0, cp.stderr)          # reported, never refused
        self.assertIn("A DIFFERENT CHECKOUT FROM --expect-root", cp.stderr)
        self.assertIn(str(self.other), cp.stderr)              # both sides named, with
        self.assertIn(str(self.good), cp.stderr)               # neither left implicit

    def test_a_non_checkout_in_MNV_REPO_is_distinguished_from_a_wrong_checkout(self):
        """Two different findings, and collapsing them would lose the one that matters:
        a non-checkout on `sys.path[0]` cannot shadow this tree's modules, so it is NOT
        run 4's shape, while a wrong checkout is exactly it."""
        cp = self.go({"MNV_REPO": str(self.plain)})
        self.assertEqual(cp.returncode, 0, cp.stderr)
        self.assertIn("NOT A CHECKOUT ROOT", cp.stderr)
        self.assertNotIn("A DIFFERENT CHECKOUT FROM", cp.stderr)

    # ---- arm 5: the innocent mutation stays green. A receipt may not fail a run.
    def test_the_capture_cannot_change_the_exit_code_on_any_arm(self):
        for extra, drop in (({"MNV_REPO": str(self.good)}, ()),
                            ({"MNV_REPO": str(self.other)}, ()),
                            ({"MNV_REPO": str(self.plain)}, ()),
                            ({"MNV_REPO": ""}, ()),
                            ({}, ("MNV_REPO",))):
            with self.subTest(extra=extra, drop=drop):
                self.assertEqual(self.go(extra, drop).returncode, 0)

    def test_a_capture_that_raises_still_does_not_fail_the_run(self):
        """The capture sits inside the emission's `try`, so it inherits the
        BaseException swallow. Measured by breaking it, not by reading the `try`."""
        import io
        original = mgr._repo_env_capture
        try:
            def boom(_):
                raise RuntimeError("capture exploded")
            mgr._repo_env_capture = boom
            buf = io.StringIO()
            self.assertIsNone(mgr._emit_inventory(str(self.good), stream=buf))
            self.assertIn("INVENTORY EMISSION FAILED", buf.getvalue())
        finally:
            mgr._repo_env_capture = original


class TheCaptureCannotGoMISSINGSilently(unittest.TestCase):
    """THE ARM THAT FIRES ON ABSENCE.

    Every other arm above compares one emission to another. If someone deletes the
    capture, all of them still describe a tool that runs, exits 0 and prints a valid
    inventory -- a does-not-fire control cannot tell "correctly scoped" from "nothing
    covers this any more", and those have identical output (`PB-16` @ `9a7f6529`). So
    this class asserts PRESENCE on every emission path, and then proves that assertion
    has power by removing the capture and requiring the check to fail.
    """

    PATHS = ("a clean run", "a refused run", "an emission with no roots at all")

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        tmp = pathlib.Path(self._tmp.name).resolve()
        self.good = make_checkout(tmp, "expected-tree")
        self.bad = make_checkout(tmp, "stale-tree")
        write(self.good / "nd-unfolding" / "victim.py", "MARK = 'RIGHT'\n")
        write(self.bad / "nd-unfolding" / "victim.py", "MARK = 'WRONG'\n")
        self.quiet = write(self.good / "nd-unfolding" / "quiet.py", "print('ran')\n")
        self.hijack = write(
            self.good / "nd-unfolding" / "hijack.py",
            "import sys\n"
            f"sys.path.insert(0, {str(self.bad / 'nd-unfolding')!r})\n"
            "import victim\n")
        self.addCleanup(self._tmp.cleanup)

    def emissions(self):
        """One text per path in PATHS, in that order."""
        import io
        clean = run_env({"MNV_REPO": str(self.good)}, (),
                        GUARD, "--expect-root", self.good, "--", self.quiet)
        refused = run_env({"MNV_REPO": str(self.good)}, (),
                          GUARD, "--expect-root", self.good, "--", self.hijack)
        self.assertEqual(clean.returncode, 0, clean.stderr)
        self.assertEqual(refused.returncode, mgr.VIOLATION_EXIT, refused.stderr)
        original = mgr.loaded_checkout_roots
        try:
            mgr.loaded_checkout_roots = lambda *_a, **_k: {}
            buf = io.StringIO()
            mgr._emit_inventory(str(self.good), stream=buf)
            noroots = buf.getvalue()
        finally:
            mgr.loaded_checkout_roots = original
        self.assertIn("NO module resolved inside any checkout", noroots)
        return [clean.stderr, refused.stderr, noroots]

    def test_the_MNV_REPO_line_is_on_every_emission_path(self):
        texts = self.emissions()
        self.assertEqual(len(texts), len(self.PATHS))
        for name, text in zip(self.PATHS, texts):
            with self.subTest(path=name):
                self.assertIn("MNV_REPO resolution=", text)

    def test_that_presence_check_actually_HAS_power(self):
        """Remove the capture and the check above must fail. Without this, a deleted
        capture and a working one give the same green suite."""
        import io
        original = mgr._repo_env_capture
        try:
            mgr._repo_env_capture = lambda _expect: []
            buf = io.StringIO()
            mgr._emit_inventory(str(self.good), stream=buf)
            text = buf.getvalue()
            self.assertNotIn("INVENTORY EMISSION FAILED", text)   # it still emits happily
            self.assertNotIn("MNV_REPO resolution=", text)        # and the line is GONE
            with self.assertRaises(AssertionError):
                self.assertIn("MNV_REPO resolution=", text)
        finally:
            mgr._repo_env_capture = original

    def test_the_capture_is_wired_into_the_emission_and_not_merely_defined(self):
        """A defined-but-uncalled helper would satisfy an import test and emit nothing.
        Read off the AST, so a rename breaks this instead of silently passing."""
        import ast
        tree = ast.parse(GUARD.read_text())
        funcs = {n.name: n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
        called = {n.func.id for n in ast.walk(funcs["_emit_inventory"])
                  if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
        self.assertIn("_repo_env_capture", called)
