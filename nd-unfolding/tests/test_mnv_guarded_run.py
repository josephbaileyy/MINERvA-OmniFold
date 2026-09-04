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


class Round7Fixture(unittest.TestCase):
    """The round-7 fixture: two checkouts, the real guard deployed, a hijacking child to hand out.

    IT IS THE ROUND-6 FIXTURE'S SHAPE AND NOT A NEW ONE, deliberately: the three findings below are
    the same defect class round 6 measured, so an arm that passed there and fails here has to differ
    in the RULE and not in the scaffolding. Every arm runs the real guard in a real subprocess and
    checks a file on disk, because "refused" and "refused after the wrong tree loaded" are the same
    exit code and only the sentinel tells them apart.
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
        self.addCleanup(self._tmp.cleanup)

    def guarded(self, parent, *, static_scan=True):
        """Run the deployed guard over `parent`. `static_scan=False` sets the test-only knob.

        THE KNOB EXISTS SO THE TWO LAYERS CAN BE MEASURED APART. With the static scanner in front,
        a reproducer never reaches the restricted shell -- so "bash would have refused it too" would
        be an assertion nobody ran. `MNV_GUARD_TEST_ONLY_DISABLE_STATIC_SCAN` makes the guard
        swallow its own launch refusals and hand the launch on with the restricted rewrite intact,
        which leaves bash as the thing that decides. It disables nothing else, and every record
        written while it is set says `static_scan: disabled-for-test`.
        """
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        env = {k: v for k, v in env.items() if not k.startswith("GIT_")}
        if not static_scan:
            env[mgr.STATIC_SCAN_DISABLED_ENV] = "1"
        return subprocess.run(
            [sys.executable, str(self.deployed_guard), "--expect-root", str(self.good),
             "--inventory", str(self.inventory), "--", str(parent)],
            capture_output=True, text=True, env=env)

    def records(self):
        if not self.inventory.exists():
            return []
        return [json.loads(line) for line in self.inventory.read_text().splitlines()
                if line.strip()]

    def hijacking_child(self, name: str):
        """A Python child that RECORDS HAVING RUN, then commits the OI-136 defect."""
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

    def bash_parent(self, name: str, body: str, *, cwd=None):
        """Write a shell script and a parent that runs it with `/bin/bash <abs path>`."""
        script = write(self.nd / f"{name}.sh", body)
        parent = write(
            self.nd / f"parent_{name}.py",
            "import os, subprocess\n"
            "env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}\n"
            f"raise SystemExit(subprocess.run(['/bin/bash', {str(script)!r}], env=env, "
            f"cwd={str(cwd or self.nd)!r}).returncode)\n")
        return parent

    def assertRefusedStatically(self, result, sentinel, reason=None, offending=None):
        """Exit 3, `[oi136 launch]`, a REFUSED-launch record, and the sentinel ABSENT."""
        self.assertEqual(result.returncode, mgr.VIOLATION_EXIT, result.stdout + result.stderr)
        self.assertIn("[oi136 launch]", result.stderr)
        self.assertNotIn("HIJACK-LOADED", result.stdout)
        self.assertFalse(sentinel.exists(),
                         "the sentinel exists, so the refused child RAN -- this is the reviewer's "
                         "finding, not a refusal")
        records = self.records()
        self.assertEqual([record["depth"] for record in records], [0],
                         "a child record means a child interpreter started")
        self.assertEqual(records[0]["verdict"], "REFUSED launch")
        self.assertEqual(records[0]["refusal_site"], mgr.SITE_LAUNCH)
        self.assertEqual(records[0]["static_scan"], "enabled")
        refusal = records[0]["launch_refusal"]
        self.assertIsNotNone(refusal, records[0])
        if reason is not None:
            self.assertEqual(refusal["reason"], reason, refusal)
        if offending is not None:
            self.assertIn(offending, refusal["offending_flag"], refusal)
        return records[0]

    def assertRefusedByTheShellItself(self, result, sentinel, message):
        """The SHELL's own error, the sentinel absent, and NO child record for a foreign import.

        THE EXIT CODE IS NOT THE ASSERTION HERE, and that is bash's semantics rather than a
        weakening. `bash -r` refuses ONE COMMAND and carries on -- `cd: restricted` then the next
        line -- so a script whose last command succeeds exits 0 while the refused line never ran.
        What proves the refusal is the message bash printed, the sentinel that does not exist, and
        the absence of any record from an interpreter that would have written one.
        """
        self.assertIn(message, result.stderr, result.stdout + result.stderr)
        self.assertFalse(sentinel.exists(),
                         "restricted bash did not stop the child: the sentinel exists")
        self.assertNotIn("HIJACK-LOADED", result.stdout)
        self.assertEqual([record["depth"] for record in self.records()], [0],
                         "a depth-1 record means the foreign import's interpreter started")
        self.assertEqual(self.records()[0]["static_scan"], "disabled-for-test")


class TheExecutedFileIsWhatIsClassifiedNeverArgvZero(Round7Fixture):
    """ROUND 7, FINDING 1: the guard trusted `ls` while the kernel ran Python.

    THE FINDING VERBATIM: "subprocess's actual executable is not scanned. mnv_guarded_run.py:2928
    classifies only argv; :2964 passes executable= separately. Reproducer:
    `subprocess.run(["ls", "-I", "child.py"], executable=sys.executable)`. The guard trusted ls as a
    leaf tool while Python actually executed. Result: exit 0, foreign import ran, sentinel created,
    no refusal and no guarded-child record."

    IT IS NOT A `subprocess` DETAIL AND THAT IS THE POINT OF THE TABLE. Every POSIX exec primitive
    takes the file to execute SEPARATELY from the argv -- `execv(path, argv)`, `spawnv(mode, file,
    args)`, `posix_spawn(path, argv, env)` -- and `argv[0]` is a display name in all of them.
    `env -a`, `exec -a` and `bash -c cmd name` exist precisely to set it to something else. So each
    primitive that has the two arguments gets a row, and each row is the reviewer's reproducer with
    that primitive's spelling: a Python interpreter as the file, `-I` as an argument, and `ls` as
    the display name.
    """

    def python_under_a_false_name(self, name: str, call: str):
        child, sentinel = self.hijacking_child(name)
        parent = write(
            self.nd / f"parent_{name}.py",
            "import os, subprocess, sys\n"
            f"CHILD = {str(child)!r}\n"
            f"{call}\n")
        return parent, sentinel

    #: THE ARGV IS `["ls", "-I", CHILD]` IN EVERY ROW and the executable is a real interpreter, so a
    #: guard reading `argv[0]` sees a leaf tool and a guard reading the executable sees `python -I`.
    #: `check_output` is here beside `run` because they are different callables in the module even
    #: though both reach `Popen`, and a reader of this table should not have to know that.
    SUBPROCESS_SPELLINGS = {
        "run": "raise SystemExit(subprocess.run(['ls', '-I', CHILD],\n"
               "    executable=sys.executable).returncode)",
        "Popen": "raise SystemExit(subprocess.Popen(['ls', '-I', CHILD],\n"
                 "    executable=sys.executable).wait())",
        "call": "raise SystemExit(subprocess.call(['ls', '-I', CHILD],\n"
                "    executable=sys.executable))",
        "check_call": "subprocess.check_call(['ls', '-I', CHILD], executable=sys.executable)",
        "check_output": "subprocess.check_output(['ls', '-I', CHILD], executable=sys.executable)",
    }

    def test_the_reviewers_reproducer_is_refused_for_every_subprocess_spelling(self):
        for name, call in self.SUBPROCESS_SPELLINGS.items():
            with self.subTest(primitive=name):
                self.inventory.unlink(missing_ok=True)
                parent, sentinel = self.python_under_a_false_name(f"exe_{name}", call)
                self.assertRefusedStatically(self.guarded(parent), sentinel,
                                             mgr.LAUNCH_REASON_FLAGS, "-I")

    #: `os.execl*` AND `os.spawnl*` ARE NOT LISTED and are not missing: CPython implements them by
    #: calling the module-global `execv`/`execve`/`spawnv*`, which this guard has replaced, so a row
    #: for each would measure the same wrapper twice under a different spelling.
    OS_SPELLINGS = {
        "execv": "os.execv(sys.executable, ['ls', '-I', CHILD])",
        "execve": "os.execve(sys.executable, ['ls', '-I', CHILD], dict(os.environ))",
        "spawnv": "raise SystemExit(os.spawnv(os.P_WAIT, sys.executable, ['ls', '-I', CHILD]))",
        "spawnve": "raise SystemExit(os.spawnve(os.P_WAIT, sys.executable, ['ls', '-I', CHILD],\n"
                   "    dict(os.environ)))",
        "posix_spawn": "pid = os.posix_spawn(sys.executable, ['ls', '-I', CHILD],\n"
                       "    dict(os.environ))\n"
                       "_, status = os.waitpid(pid, 0)\n"
                       "raise SystemExit(os.waitstatus_to_exitcode(status))",
        "posix_spawnp": "pid = os.posix_spawnp(sys.executable, ['ls', '-I', CHILD],\n"
                        "    dict(os.environ))\n"
                        "_, status = os.waitpid(pid, 0)\n"
                        "raise SystemExit(os.waitstatus_to_exitcode(status))",
    }

    def test_the_reviewers_reproducer_is_refused_for_every_os_exec_and_spawn_primitive(self):
        for name, call in self.OS_SPELLINGS.items():
            with self.subTest(primitive=name):
                self.inventory.unlink(missing_ok=True)
                parent, sentinel = self.python_under_a_false_name(f"osx_{name}", call)
                self.assertRefusedStatically(self.guarded(parent), sentinel,
                                             mgr.LAUNCH_REASON_FLAGS, "-I")

    def test_the_execvp_family_resolves_the_name_on_the_CHILDS_path_not_on_argv_zero(self):
        """`os.execvp("python3", ["ls", "-I", child])`: the file is a NAME and it is resolved.

        The `p` spellings are the ones where "the executable" is not a path but a lookup, and the
        lookup uses the CHILD's `PATH`. A guard that classified `argv[0]` would see `ls`; one that
        classified the file has to resolve `python3` the way the child will.
        """
        child, sentinel = self.hijacking_child("execvp_child")
        parent = write(
            self.nd / "parent_execvp.py",
            "import os\n"
            f"os.execvp('python3', ['ls', '-I', {str(child)!r}])\n")
        self.assertRefusedStatically(self.guarded(parent), sentinel,
                                     mgr.LAUNCH_REASON_FLAGS, "-I")

    @unittest.skipUnless(shutil.which("zsh"), "no zsh on this platform")
    def test_with_shell_True_the_executable_kwarg_IS_the_shell_and_replaces_bin_sh(self):
        """`subprocess.run(cmd, shell=True, executable="/bin/zsh")` is a ZSH launch, not an `sh` one.

        CPython builds `[executable or "/bin/sh", "-c", cmd]`, so `executable=` decides WHICH SHELL
        interprets the string -- a different language with different startup files and a restricted
        mode this guard does not model. A scan that assumed `/bin/sh` would read the string with
        one shell's grammar and hand it to another. The refusal names `zsh`, which is the only
        evidence that the kwarg was read.
        """
        child, sentinel = self.hijacking_child("shell_exe_child")
        parent = write(
            self.nd / "parent_shell_exe.py",
            "import subprocess\n"
            f"raise SystemExit(subprocess.run('python3 {shlex.quote(str(child))}', shell=True,\n"
            "    executable='/bin/zsh').returncode)\n")
        self.assertRefusedStatically(self.guarded(parent), sentinel,
                                     mgr.LAUNCH_REASON_UNPROVEN, "zsh")

    def test_THE_SILENT_DIRECTION_a_true_leaf_under_its_own_name_still_runs(self):
        """The power arm: `executable=` naming the tool it says it names is ADMITTED.

        Without this the class above would pass for a guard that refused every `executable=`, which
        is a rule nobody could keep. The same argv, with `ls` as the executable as well as as the
        display name, runs -- and the `-I` in it is `ls`'s own ignore-pattern option, which is what
        makes the pair a comparison rather than two unlike things.
        """
        parent = write(
            self.nd / "parent_true_leaf.py",
            "import subprocess\n"
            f"code = subprocess.run(['ls', '-I', 'victim.py'], executable='/bin/ls',\n"
            f"    cwd={str(self.nd)!r}).returncode\n"
            "print('LEAF-EXIT', code)\n")
        result = self.guarded(parent)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("LEAF-EXIT 0", result.stdout)
        self.assertNotIn("[oi136 launch]", result.stderr)
        self.assertIsNone(self.records()[0]["launch_refusal"])


class TheRestrictedShellIsTheSecondLayerAndRefusesOnItsOwn(Round7Fixture):
    """ROUND 7, FINDINGS 2 AND 3, AND THE MODEL CHANGE THEY FORCED. Two layers, measured apart.

    THE TWO FINDINGS VERBATIM. (2) "Shell-expanded Python flags bypass the static scan. :2655
    rejects runtime-built command words, but not runtime-built arguments. `FLAG=-I` /
    `/usr/bin/python3 "$FLAG" child.py`. This also ran successfully outside the shim contract with
    no refusal or child record." (3) "A preceding cd can make the scanner inspect the wrong script.
    :2448 explicitly does not model cd. With a benign child.sh in the launch directory and a
    malicious one under sub/: `cd sub` / `bash child.sh` -- the guard scanned the benign file; the
    shell executed the malicious file. Its Python -I launch escaped and imported the foreign
    module."

    WHY THE FIX IS NOT A THIRD PATCH TO THE MODEL. Rounds 5, 6 and 7 each found a construct this
    guard's model of shell syntax got wrong, and each time the answer was a better model. The
    boundary of that answer is "how well one Python file parses shell", which is not a boundary
    anybody can state. So the model stopped being the enforcement: an admitted shell is REWRITTEN to
    run as `bash -r` with a PATH holding the guard's wrapper directories and nothing else, and what
    a shell program can reach is bounded by bash's own restricted mode (manual section 6.10) plus
    the contents of one directory. The static scanner stays in front as the first refuser.

    SO EVERY REPRODUCER IS MEASURED TWICE, AND THE SECOND MEASUREMENT NEEDS THE KNOB. With the
    static scanner in front, a reproducer never reaches bash -- so "the shell would have refused it
    too" would be a claim nobody ran. `Round7Fixture.guarded(static_scan=False)` stands the static
    half down and leaves the rewrite in place, and the arms below then assert BASH'S OWN message.
    """

    # --- finding 2: a runtime-built ARGUMENT, not a command word -------------------------------

    def test_finding_2_a_shell_expanded_python_flag_is_refused_by_the_STATIC_scanner(self):
        """`FLAG=-I` then `/usr/bin/python3 "$FLAG" child.py`, exactly as the reviewer wrote it.

        The command word is a literal absolute path, so the predecessor's one question -- "is the
        COMMAND WORD built at run time" -- answered no and the scan went on to a flag walk over
        `["$FLAG", "child.py"]`, in which `$FLAG` is not a token starting with `-`. It read as the
        script operand and ended the walk. The rule is now that every token up to and including an
        interpreter's first operand must be literal, and the refusal names the token.
        """
        child, sentinel = self.hijacking_child("flag_expansion")
        parent = self.bash_parent(
            "flag_expansion",
            "FLAG=-I\n"
            f"/usr/bin/python3 \"$FLAG\" {shlex.quote(str(child))}\n")
        record = self.assertRefusedStatically(self.guarded(parent), sentinel,
                                              mgr.LAUNCH_REASON_UNPARSED, "$FLAG")
        self.assertIn("python interpreter option", record["launch_refusal"]["offending_flag"])

    def test_finding_2_is_refused_AGAIN_by_restricted_bash_with_the_static_scanner_STOOD_DOWN(self):
        """The same script, the static half disabled: `bash -r` refuses the absolute command name.

        THE TWO LAYERS ARE INDEPENDENT AND THIS IS WHAT MAKES THAT MEASURED. Restricted bash never
        looks at `$FLAG` -- what it refuses is `/usr/bin/python3`, because its first documented
        restriction is that a command name may not contain a slash. So the expansion could have
        been anything at all and the launch would still not have happened, which is a claim about
        the shape of the program rather than about this file's ability to read one token.
        """
        child, sentinel = self.hijacking_child("flag_expansion_dyn")
        parent = self.bash_parent(
            "flag_expansion_dyn",
            "FLAG=-I\n"
            f"/usr/bin/python3 \"$FLAG\" {shlex.quote(str(child))}\n")
        result = self.guarded(parent, static_scan=False)
        self.assertRefusedByTheShellItself(
            result, sentinel, "/usr/bin/python3: restricted: cannot specify `/' in command names")

    # --- finding 3: a preceding cd ------------------------------------------------------------

    def two_child_scripts(self, *, malicious_sub: bool):
        """`child.sh` in the launch directory and `sub/child.sh` under it. One name, two files.

        The launch-directory copy is always benign. `malicious_sub` decides whether the copy the
        `cd` would reach launches an isolated interpreter -- which is the reviewer's arrangement --
        or is benign too, which is the arrangement that shows what the DYNAMIC layer costs.
        """
        child, sentinel = self.hijacking_child(
            "cd_hijack" if malicious_sub else "cd_benign")
        write(self.nd / "child.sh", "echo BENIGN-IN-LAUNCH-DIR\n")
        sub = self.nd / "sub"
        sub.mkdir(exist_ok=True)
        write(sub / "child.sh",
              f"/usr/bin/python3 -I {shlex.quote(str(child))}\n" if malicious_sub
              else "echo BENIGN-IN-SUB\n")
        return child, sentinel

    def test_finding_3_a_preceding_cd_no_longer_makes_the_scanner_read_the_wrong_file(self):
        """`cd sub` then `bash child.sh`, with the malicious copy under `sub/`.

        THE PREDECESSOR SCANNED A FILE THAT EXISTED AND WAS NOT THE ONE THAT RAN. It resolved a
        relative operand against the launch cwd, found the benign `child.sh` there, read it, and
        admitted the launch; the shell had already moved into `sub/`. There is no way to pick
        correctly without executing the `cd`, so the scanner picks ALL of them: `cd` with a literal
        operand ADDS a candidate directory, a relative operand is resolved against every candidate,
        and every resolution that exists is read. The malicious copy is therefore read, and the
        refusal names ITS `-I` -- which only a scan of that file's contents can produce.
        """
        child, sentinel = self.two_child_scripts(malicious_sub=True)
        parent = self.bash_parent("cd_hijack", "cd sub\nbash child.sh\n")
        self.assertRefusedStatically(self.guarded(parent), sentinel,
                                     mgr.LAUNCH_REASON_FLAGS, "-I")

    def test_finding_3_is_refused_AGAIN_by_restricted_bash_with_the_static_scanner_STOOD_DOWN(self):
        """The same two files, the static half disabled: `bash -r` refuses the `cd` itself.

        The shell never leaves the launch directory, so `bash child.sh` runs the BENIGN copy that
        was always there -- which is visible on stdout -- and the malicious one under `sub/` is
        never reached by anything. The second layer does not need to know which file was dangerous.
        """
        child, sentinel = self.two_child_scripts(malicious_sub=True)
        parent = self.bash_parent("cd_hijack_dyn", "cd sub\nbash child.sh\n")
        result = self.guarded(parent, static_scan=False)
        self.assertRefusedByTheShellItself(result, sentinel, "cd: restricted")
        self.assertIn("BENIGN-IN-LAUNCH-DIR", result.stdout)
        self.assertNotIn("BENIGN-IN-SUB", result.stdout)

    def test_a_BENIGN_cd_is_admitted_statically_AND_REFUSED_BY_THE_SHELL_which_is_the_model(self):
        """Both `child.sh` files benign: the static scan admits, and restricted bash still says no.

        THIS ARM IS THE COST OF THE MODEL, WRITTEN DOWN RATHER THAN DISCOVERED LATER. Nothing in
        this program is wrong: the scanner reads both copies, both are `echo`, and it admits. Bash
        then refuses the `cd` anyway, because `cd` is refused in restricted mode whatever it points
        at -- and the program runs the launch-directory copy instead of the one it meant to. A
        launcher that changes directory has to be respelled with absolute paths.

        BOTH HALVES ARE ASSERTED IN ONE ARM ON PURPOSE. Split apart, "the static scan admits" and
        "the shell refuses" are two facts about two runs; together they are the statement that the
        two layers DISAGREE here, which is the thing a reader of the model needs to know.
        """
        child, sentinel = self.two_child_scripts(malicious_sub=False)
        parent = self.bash_parent("cd_benign", "cd sub\nbash child.sh\n")
        result = self.guarded(parent)
        self.assertNotIn("[oi136 launch]", result.stderr,
                         "the static scanner refused a program with nothing wrong in it")
        self.assertIn("cd: restricted", result.stderr)
        self.assertIn("BENIGN-IN-LAUNCH-DIR", result.stdout)
        self.assertNotIn("BENIGN-IN-SUB", result.stdout)
        self.assertFalse(sentinel.exists())

    def test_an_UNKNOWN_working_directory_refuses_a_relative_operand_rather_than_guessing(self):
        """`cd "$D"`, a bare `cd`, `cd -`, `cd ~x` and `CDPATH=`: the candidate set is UNKNOWN.

        AN EMPTY SET WOULD BE THE WRONG STATE and this is why the tracker has three. With the
        destination unresolvable, "every directory the operand could name" is unbounded -- so a
        relative `bash child.sh` after one of these is a REFUSAL that names the construct, not a
        file-not-found and not a scan of whichever copy happens to be nearest.
        """
        self.two_child_scripts(malicious_sub=False)
        cases = {
            "runtime operand": 'D=/tmp\ncd "$D"\nbash child.sh\n',
            "no operand": "cd\nbash child.sh\n",
            "cd -": "cd -\nbash child.sh\n",
            "cd ~user": "cd ~root\nbash child.sh\n",
            "CDPATH assigned": "CDPATH=/tmp\ncd sub\nbash child.sh\n",
        }
        for name, body in cases.items():
            with self.subTest(construct=name):
                self.inventory.unlink(missing_ok=True)
                parent = self.bash_parent(f"cd_unknown_{abs(hash(name))}", body)
                result = self.guarded(parent)
                self.assertEqual(result.returncode, mgr.VIOLATION_EXIT,
                                 result.stdout + result.stderr)
                refusal = self.records()[0]["launch_refusal"]
                self.assertEqual(refusal["reason"], mgr.LAUNCH_REASON_UNPARSED, refusal)
                self.assertIn("cannot be resolved", refusal["offending_flag"])
        # THE SILENT DIRECTION: an ABSOLUTE operand is unaffected by an unknown working directory,
        # because its identity does not depend on one.
        self.inventory.unlink(missing_ok=True)
        parent = self.bash_parent(
            "cd_unknown_absolute",
            f"cd\nbash {shlex.quote(str(self.nd / 'child.sh'))}\n")
        result = self.guarded(parent)
        self.assertNotIn("[oi136 launch]", result.stderr, result.stdout + result.stderr)

    # --- finding 1 has no second layer, and that is measured rather than assumed ---------------

    def test_finding_1_HAS_NO_SECOND_LAYER_AND_THE_STATIC_CLASSIFICATION_IS_THE_WHOLE_OF_IT(self):
        """The `executable=` reproducer, with the static half stood down: it RUNS.

        SAYING SO IS THE POINT OF THIS ARM. Findings 2 and 3 are shell programs, so restricted bash
        stands behind the scanner for both; finding 1 is `subprocess.run(["ls", "-I", child],
        executable=sys.executable)` -- no shell anywhere in it, and an ABSOLUTE executable, so no
        PATH lookup and therefore no interpreter wrapper either. There is nothing behind the
        classification. With it disabled the sentinel is written and the wrong tree loads, which is
        the reviewer's original observation reproduced on purpose.

        A CLAIM OF "TWO INDEPENDENT LAYERS" THAT COVERED THIS CASE WOULD BE FALSE, and a suite that
        simply omitted the arm would leave the reader to assume the general claim. The guard's
        answer for finding 1 is that the classification is now correct, not that something else
        would have caught it.
        """
        child, sentinel = self.hijacking_child("no_second_layer")
        parent = write(
            self.nd / "parent_no_second_layer.py",
            "import subprocess, sys\n"
            f"subprocess.run(['ls', '-I', {str(child)!r}], executable=sys.executable)\n")
        result = self.guarded(parent, static_scan=False)
        self.assertTrue(sentinel.exists(),
                        "the arm is vacuous: the child did not run even with the scanner disabled")
        self.assertIn("HIJACK-LOADED WRONG TREE", result.stdout)
        # And WITH the scanner enabled, which is the state every real run is in.
        self.inventory.unlink(missing_ok=True)
        sentinel.unlink()
        self.assertRefusedStatically(self.guarded(parent), sentinel,
                                     mgr.LAUNCH_REASON_FLAGS, "-I")


class TheStaticScannerRefusesEveryTokenThatCanSelectAProgram(Round7Fixture):
    """ROUND 7, PART C: the first layer, as a table over what a shell program is allowed to say.

    THE STATIC SCANNER IS NO LONGER THE ENFORCEMENT AND IT IS STILL THE FIRST REFUSER, and both
    halves of that sentence are why this class is separate from the restricted-shell one. It is not
    the enforcement because bash's restricted mode is; it is still worth having because a refusal
    that happens BEFORE the launch names the construct, points at the line, and costs no compute --
    and because for an `sbatch` job script, which runs on a compute node in another process tree,
    there is nothing behind it.

    EVERY ROW REFUSES BEFORE ANYTHING RUNS, and each names the token it refused for. The rows are
    the four rules of part C: a runtime-built token anywhere it could select a program or an
    interpreter option, `xargs` over anything but a leaf, a working directory this scan cannot
    resolve, and a path the program both WRITES and RUNS.
    """

    def refusing_rows(self, child):
        quoted = shlex.quote(str(child))
        return {
            # round 6's three, which must stay refused
            "PATH= in front of the interpreter": (
                f"PATH=/usr/bin:/bin python3 -I {quoted}\n", mgr.LAUNCH_REASON_ENV, "PATH="),
            "command -p": (f"command -p python3 {quoted}\n", mgr.LAUNCH_REASON_ENV, "-p"),
            "env -P": (f"env -P /usr/bin:/bin python3 -I {quoted}\n",
                       mgr.LAUNCH_REASON_UNMODELLED, "-P"),
            "hash -p": (f"hash -p /usr/bin/python3 python3\npython3 -I {quoted}\n",
                        mgr.LAUNCH_REASON_UNPROVEN, "hash -p"),
            # round 7's runtime-token rule, in each position it covers
            "an indirect command word": (f"PY=/usr/bin/python3\n$PY {quoted}\n",
                                         mgr.LAUNCH_REASON_UNPARSED, "$PY"),
            "an expanded interpreter option": (f"F=-I\npython3 \"$F\" {quoted}\n",
                                               mgr.LAUNCH_REASON_UNPARSED, "$F"),
            "an expanded script operand": ("S=x.py\npython3 \"$S\"\n",
                                           mgr.LAUNCH_REASON_UNPARSED, "$S"),
            "an expanded -m module": ("M=json.tool\npython3 -m \"$M\"\n",
                                      mgr.LAUNCH_REASON_UNPARSED, "$M"),
            "an expanded -c program": ("C='import os'\npython3 -c \"$C\"\n",
                                       mgr.LAUNCH_REASON_UNPARSED, "$C"),
            "python3 \"$@\"": ("python3 \"$@\"\n", mgr.LAUNCH_REASON_UNPARSED, "$@"),
            "an expanded shell script operand": ("S=child.sh\nbash \"$S\"\n",
                                                 mgr.LAUNCH_REASON_UNPARSED, "$S"),
            "an expanded wrapper option": (f"T=5\ntimeout \"$T\" python3 {quoted}\n",
                                           mgr.LAUNCH_REASON_UNPARSED, "$T"),
            "an expanded sbatch option": (f"A=acct\nsbatch -A \"$A\" job.sh\n",
                                          mgr.LAUNCH_REASON_UNPARSED, "$A"),
            "an expanded srun option": (f"N=1\nsrun -n \"$N\" python3 {quoted}\n",
                                        mgr.LAUNCH_REASON_UNPARSED, "$N"),
            "an expanded git global option": ("G=--no-pager\ngit \"$G\" status\n",
                                              mgr.LAUNCH_REASON_UNPARSED, "$G"),
            "an expanded git log argument": ("R=HEAD\ngit log --no-ext-diff \"$R\"\n",
                                             mgr.LAUNCH_REASON_UNPARSED, "$R"),
            "a glob in the interpreter path": (f"./py*/python3 {quoted}\n",
                                               mgr.LAUNCH_REASON_UNPARSED, "*"),
            # xargs builds its child's argv at run time by construction
            "xargs over an interpreter": (f"echo {quoted} | xargs python3\n",
                                          mgr.LAUNCH_REASON_UNPARSED, "xargs"),
            # the environment that decides which interpreter and which stdlib
            "PYTHONHOME in front of the interpreter": (f"PYTHONHOME=/x python3 {quoted}\n",
                                                       mgr.LAUNCH_REASON_ENV, "PYTHONHOME"),
        }

    def test_every_construct_that_can_select_a_program_is_refused_before_the_launch(self):
        child, sentinel = self.hijacking_child("static_table")
        for name, (body, reason, offending) in self.refusing_rows(child).items():
            with self.subTest(construct=name):
                self.inventory.unlink(missing_ok=True)
                sentinel.unlink(missing_ok=True)
                parent = self.bash_parent(f"static_{abs(hash(name))}", body)
                self.assertRefusedStatically(self.guarded(parent), sentinel, reason, offending)

    def test_a_copied_interpreter_UNDER_ANOTHER_NAME_is_refused_for_what_it_is(self):
        """`./tool child.py` where `tool` is a byte copy of the interpreter.

        A NAME IS NOT A BEHAVIOUR IN BOTH DIRECTIONS. The leaf table refuses a file called `ls` that
        turns out to be a script; this is the same rule with the roles swapped -- a file called
        `tool` that turns out to be an interpreter. It resolves to no system prefix, matches no
        interpreter name, and carries no shebang to read, so there is nothing about it this guard
        can establish and it refuses. Restricted bash would refuse it a second time for the slash.
        """
        child, sentinel = self.hijacking_child("copied_interpreter")
        tool = self.nd / "tool"
        shutil.copy2(sys.executable, tool)
        tool.chmod(0o755)
        parent = self.bash_parent("copied_interpreter",
                                  f"./tool -I {shlex.quote(str(child))}\n")
        self.assertRefusedStatically(self.guarded(parent), sentinel,
                                     mgr.LAUNCH_REASON_UNPROVEN, "tool")

    def test_a_path_the_program_both_WRITES_and_RUNS_is_refused_however_the_write_is_spelled(self):
        """WRITE-THEN-EXECUTE: the bytes this scan read are not the bytes that would run.

        IT IS NOT A RACE THIS GUARD CAN WIN BY RE-READING. The write happens after the launch is
        admitted, inside the program, so a second read at launch time would see the same bytes the
        first one did. The composition is refused instead -- and the ORDER OF THE LINES IS NOT THE
        BOUND, which the reversed row asserts: a program that runs `stage.sh` and then rewrites it
        is the same program the next time round.

        THE RUNTIME-TARGET ROW IS THE OTHER HALF. `cp payload.sh "$OUT"` names a path this scan
        cannot compare with anything, so the intersection is empty for the wrong reason; paired with
        a relative script operand, whose identity is also decided later, the two cannot be shown to
        be different files.
        """
        write(self.nd / "payload.sh", "echo payload\n")
        write(self.nd / "stage.sh", "echo staged\n")
        rows = {
            "cp then run": "cp payload.sh stage.sh\nbash stage.sh\n",
            "run then cp": "bash stage.sh\ncp payload.sh stage.sh\n",
            "mv then run": "mv payload.sh stage.sh\nbash stage.sh\n",
            "tee then run": "echo x | tee stage.sh\nbash stage.sh\n",
            "redirection then run": "echo x > stage.sh\nbash stage.sh\n",
            "rsync then run": "rsync payload.sh stage.sh\nbash stage.sh\n",
            "source, not run": "cp payload.sh stage.sh\nsource stage.sh\n",
            "runtime target and a relative operand": (
                "OUT=stage.sh\ncp payload.sh \"$OUT\"\nbash stage.sh\n"),
        }
        child, sentinel = self.hijacking_child("toctou")
        for name, body in rows.items():
            with self.subTest(row=name):
                self.inventory.unlink(missing_ok=True)
                parent = self.bash_parent(f"toctou_{abs(hash(name))}", body)
                record = self.assertRefusedStatically(self.guarded(parent), sentinel,
                                                      mgr.LAUNCH_REASON_UNPARSED)
                self.assertIn("stage.sh", record["launch_refusal"]["offending_flag"])
        # THE SILENT DIRECTION, and it is the one that keeps the rule usable: writing a file the
        # program does NOT run is what a science step does all day.
        self.inventory.unlink(missing_ok=True)
        parent = self.bash_parent("toctou_clean",
                                  "cp payload.sh other.sh\nbash stage.sh\n")
        result = self.guarded(parent)
        self.assertNotIn("[oi136 launch]", result.stderr, result.stdout + result.stderr)

    def test_the_WRITER_table_is_wider_than_the_leaf_table_and_the_leaf_rule_fires_first(self):
        """`sed -i`, `chmod`, `install`, `dd`, `curl -o`: refused as NON-LEAVES before the write.

        THE TWO TABLES ARE NOT THE SAME TABLE AND A READER SHOULD NOT HAVE TO INFER THAT. Round 7's
        write-then-execute rule names the writers it models -- `_WRITER_BASENAMES` -- and most of
        those names are deliberately absent from `_LEAF_TOOL_BASENAMES`, because `sed` has an `e`
        command, `install` runs a strip program and `curl` writes wherever it is told. So inside an
        admitted shell program they refuse for being unprovable children, and the composition check
        never gets to see them.

        THE WRITER TABLE IS KEPT WIDE ANYWAY, and this arm is why that is not dead code: the two
        tables move independently, and a later round that admits one of these names as a leaf must
        find the composition rule already covering it rather than have to remember to add it.
        """
        write(self.nd / "payload.sh", "echo payload\n")
        write(self.nd / "stage.sh", "echo staged\n")
        for command in ("sed -i s/a/b/ stage.sh", "chmod +x stage.sh",
                        "install payload.sh stage.sh", "dd if=payload.sh of=stage.sh",
                        "curl -o stage.sh http://example.invalid/x"):
            with self.subTest(writer=command.split()[0]):
                self.inventory.unlink(missing_ok=True)
                parent = self.bash_parent(f"writer_{abs(hash(command))}",
                                          f"{command}\nbash stage.sh\n")
                result = self.guarded(parent)
                self.assertEqual(result.returncode, mgr.VIOLATION_EXIT,
                                 result.stdout + result.stderr)
                self.assertEqual(self.records()[0]["launch_refusal"]["reason"],
                                 mgr.LAUNCH_REASON_UNPROVEN)
        # And the unit-level claim the arm above cannot reach: the writer table DOES model each of
        # them, called directly, so widening the leaf table cannot silently uncover the composition.
        for tokens, target in ((["sed", "-i", "s/a/b/", "stage.sh"], "stage.sh"),
                               (["sed", "-i.bak", "-e", "s/a/b/", "one.sh"], "one.sh"),
                               (["chmod", "+x", "a.sh", "b.sh"], "b.sh"),
                               (["install", "-m", "755", "src", "dest.sh"], "dest.sh"),
                               (["dd", "if=src", "of=out.sh"], "out.sh"),
                               (["curl", "-o", "got.sh", "http://x"], "got.sh"),
                               (["wget", "--output-document=w.sh", "http://x"], "w.sh")):
            with self.subTest(unit=tokens[0]):
                context = mgr._ScanContext(str(self.nd), in_shell=True)
                mgr._record_write_targets(tokens, context)
                self.assertIn(str(self.nd / target), context.uses.written, tokens)


class TheWrapperDirectoryIsWhatARestrictedShellMayREACH(Round7Fixture):
    """ROUND 7, PART B's other half: what a restricted shell CAN do, and what is simply not there.

    A GUARD THAT REFUSES EVERYTHING IS NOT A GUARD, IT IS A REMOVAL. The closed child model is only
    keepable if an ordinary launcher still runs, so the admitted set is measured here beside the
    refused one -- and it is measured through a Python child's own inventory record, because "the
    script exited 0" cannot tell a guarded child from one that never started.
    """

    def digest_tool(self):
        """A digest leaf that exists HERE, chosen by measurement rather than by name.

        `sha256sum` is coreutils and `shasum` is the Perl script macOS ships -- and a Perl script
        gets NO forwarder, because a forwarder is written only for a file that carries no shebang.
        So a row naming the wrong one would fail for a reason that has nothing to do with the rule.
        """
        for name in ("sha256sum", "md5sum", "cksum"):
            located = shutil.which(name)
            if located and mgr._locate_a_system_tool(name):
                return name
        return None

    def test_the_admitted_set_runs_and_the_python_child_leaves_a_GUARDED_record(self):
        """`python3 x.py`, `python3 x.py "$@"`, `git rev-parse HEAD`, `ls`, `mkdir -p`, a digest.

        EVERY ONE OF THESE GOES THROUGH A WRAPPER OR A FORWARDER, because a restricted shell's PATH
        is the guard's wrapper directories and nothing else. `git` reaches the committed wrapper,
        which applies the read-only allowlist and then execs the system git; `ls`, `mkdir` and the
        digest reach forwarders `install()` generated for this host; `python3` reaches the
        interpreter wrapper, which scans and then execs the real interpreter -- and the two depth-1
        records are what proves the children were GUARDED rather than merely successful.
        """
        digest = self.digest_tool()
        self.assertIsNotNone(digest, "no shebang-free digest leaf under a system prefix here")
        clean = self.clean_child()
        quoted = shlex.quote(str(clean))
        parent = self.bash_parent(
            "admitted",
            "set -eu\n"
            f"ls {shlex.quote(str(self.nd))}\n"
            f"mkdir -p {shlex.quote(str(self.tmp / 'made'))}\n"
            f"{digest} {quoted}\n"
            f"git -C {shlex.quote(str(REPO))} rev-parse HEAD\n"
            f"python3 {quoted}\n"
            f"python3 {quoted} \"$@\"\n")
        result = self.guarded(parent)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("[oi136 launch]", result.stderr)
        self.assertEqual(result.stdout.count("CHILD-LOADED RIGHT TREE"), 2, result.stdout)
        self.assertTrue((self.tmp / "made").is_dir())
        depths = sorted(record["depth"] for record in self.records())
        self.assertEqual(depths, [0, 1, 1], "a python child of the restricted shell left no record")
        for record in self.records():
            if record["depth"] == 1:
                self.assertEqual(record["propagation"], "armed")

    def test_a_shell_STARTED_BY_a_restricted_shell_re_enters_restricted_mode(self):
        """`bash inner.sh` and `sh -c ...` from inside a restricted script.

        THE MOST ORDINARY LINE IN A LAUNCHER IS THE ONE THAT WOULD UNDO THE WHOLE THING. A
        restricted shell resolves `bash` through the only PATH it has, which is the wrapper
        directory -- so what it reaches is the committed `bin/bash`, and that wrapper's whole job is
        to exec the pinned real bash with `-r` again. A wrapper that forwarded plainly would buy an
        unrestricted shell for the cost of one word.

        THE PROOF IS IN THE GRANDCHILD AND NOT IN THE CHILD. `inner.sh` runs and says so, which
        rules out "the wrapper refused everything"; and the `/bin/ls` on its second line is refused
        with bash's own slash message, which is only possible if the shell running `inner.sh` is
        itself restricted. `sh -c` is there because `sh` is a second committed name over the same
        body, and a body reached under one name and not the other is how a wrapper set drifts.
        """
        write(self.nd / "inner.sh", "echo INNER-RAN\n/bin/ls\n")
        parent = self.bash_parent("reentry", "bash inner.sh\nsh -c 'echo SH-WRAPPER-RAN'\n")
        result = self.guarded(parent)
        self.assertNotIn("[oi136 launch]", result.stderr, result.stdout + result.stderr)
        self.assertIn("INNER-RAN", result.stdout)
        self.assertIn("SH-WRAPPER-RAN", result.stdout)
        self.assertIn("/bin/ls: restricted: cannot specify `/' in command names", result.stderr)

    def test_a_program_the_wrapper_directory_does_not_hold_is_COMMAND_NOT_FOUND(self):
        """`awk`, `perl`, `make`: refused statically, and NOT PRESENT at all to the shell.

        THE TWO LAYERS SAY DIFFERENT THINGS HERE AND BOTH ARE ASSERTED. The scanner refuses them by
        name -- each runs a program its own arguments can name, which is why none of them is in
        `_LEAF_TOOL_BASENAMES`. With the scanner stood down, the restricted shell does not refuse
        them either: it cannot FIND them, because the only PATH it has is a directory this guard
        wrote, and `command not found` at exit 127 is the shell saying the set of reachable
        programs is exactly the set the guard enumerated.
        """
        for tool in ("awk", "perl", "make"):
            with self.subTest(tool=tool):
                self.inventory.unlink(missing_ok=True)
                parent = self.bash_parent(f"notfound_{tool}", f"{tool} --version\necho AFTER\n")
                refused = self.guarded(parent)
                self.assertEqual(refused.returncode, mgr.VIOLATION_EXIT,
                                 refused.stdout + refused.stderr)
                self.assertEqual(self.records()[0]["launch_refusal"]["reason"],
                                 mgr.LAUNCH_REASON_UNPROVEN)

                self.inventory.unlink(missing_ok=True)
                loose = self.guarded(parent, static_scan=False)
                self.assertIn(f"{tool}: command not found", loose.stderr,
                              loose.stdout + loose.stderr)
                self.assertNotIn(f"{tool} version", loose.stdout.lower())

    #: EACH ROW IS A CONSTRUCT BASH'S RESTRICTED MODE REFUSES, with the fragment of ITS message that
    #: identifies the refusal. The messages are bash's and not this guard's, which is the whole
    #: claim -- so they are matched loosely enough to survive a bash version (3.2 says `PATH:
    #: readonly variable` where 5.x says `PATH: restricted`) and tightly enough to name the rule.
    RESTRICTED_MODE_ROWS = {
        "a command name with a slash": ("/bin/ls\n", "cannot specify `/' in command names"),
        "cd": ("cd /tmp\n", "cd: restricted"),
        "exec": ("exec ls\n", "exec: restricted"),
        "command -p": ("command -p ls\n", "command: -p: restricted"),
        "hash -p": ("hash -p /bin/ls ls\n", "hash: /bin/ls: restricted"),
        # bash 3.2 reports `enable: restricted` where later versions name the option; the fragment
        # is the part both spellings share, so the row survives a bash version without stopping
        # being about `enable -f`.
        "enable -f": ("enable -f /tmp/x.so foo\n", "enable: "),
        "output redirection": ("echo x > out.txt\n", "out.txt: restricted"),
    }

    def test_restricted_bash_refuses_each_construct_in_ITS_OWN_WORDS(self):
        """The dynamic layer, one row per rule, with the static half stood down.

        THE MESSAGES ARE THE EVIDENCE AND THE EXIT CODE IS NOT. `bash -r` refuses ONE COMMAND and
        continues, so a script whose last line succeeds exits 0 with the refused line never having
        run -- which is why every row appends an `echo` and asserts that it DID run: it separates
        "bash refused this command" from "the shell died before reaching it".
        """
        for name, (body, message) in self.RESTRICTED_MODE_ROWS.items():
            with self.subTest(construct=name):
                self.inventory.unlink(missing_ok=True)
                parent = self.bash_parent(f"rbash_{abs(hash(name))}", body + "echo REACHED-END\n")
                result = self.guarded(parent, static_scan=False)
                self.assertIn(message, result.stderr, result.stdout + result.stderr)
                self.assertIn("restricted", result.stderr, result.stdout + result.stderr)
                self.assertIn("REACHED-END", result.stdout,
                              "the shell stopped before the marker, so the row proves nothing "
                              "about which command was refused")

    def test_a_PATH_assignment_inside_the_restricted_shell_cannot_take_effect(self):
        """`PATH=/usr/bin` inside a restricted shell, with the static half stood down.

        Its message differs across bash versions -- 3.2 reports a readonly variable, later ones
        report the restriction -- so the assertion is on the two things that do not differ: bash
        named PATH, and the assignment did not happen.
        """
        parent = self.bash_parent("rbash_path", "PATH=/usr/bin\necho AFTER $PATH\n")
        result = self.guarded(parent, static_scan=False)
        self.assertIn("PATH", result.stderr, result.stdout + result.stderr)
        self.assertTrue(
            "readonly" in result.stderr or "restricted" in result.stderr,
            result.stderr)
        self.assertNotIn("AFTER /usr/bin", result.stdout)

    @staticmethod
    def a_variable_survives_an_exec(variable: str) -> bool:
        """Whether `variable` is still set inside a `/bin/sh` this process starts with it.

        THE FIXTURE HAS TO AGREE WITH THE WORLD RATHER THAN WITH THE CODE. `DYLD_INSERT_LIBRARIES`
        is stripped by macOS System Integrity Protection before a protected binary starts, so a row
        asserting that the wrapper refuses it would pass or fail for a reason on the platform's side
        of the boundary. This asks the platform.
        """
        probe = subprocess.run(
            ["/bin/sh", "-c", f'printf %s "${{{variable}-unset}}"'],
            env=dict(os.environ, **{variable: "/nonexistent"}),
            capture_output=True, text=True)
        return probe.stdout == "/nonexistent"

    def test_the_interpreter_wrapper_refuses_a_HOSTILE_ENVIRONMENT_from_a_non_shell_child(self):
        """`PYTHONHOME` reaching `bin/python3`, which a restricted child cannot do and a plain one can.

        A RESTRICTED SHELL STRIPS ALL FOUR of `PYTHONHOME`, `PYTHONEXECUTABLE`, `LD_PRELOAD` and
        `DYLD_INSERT_LIBRARIES`, so this cannot arrive from one. The wrapper is ALSO reached from an
        admitted NON-shell child, which was never handed a restricted environment -- and there the
        variables decide which interpreter, which standard library, or which shared object runs
        before `sitecustomize` does. The wrapper is standing in front of the interpreter, so it is
        the place that has to say no.
        """
        clean = self.clean_child()
        for variable in ("PYTHONHOME", "PYTHONEXECUTABLE", "LD_PRELOAD",
                         "DYLD_INSERT_LIBRARIES"):
            with self.subTest(variable=variable):
                if not self.a_variable_survives_an_exec(variable):
                    # MEASURED, NOT ASSUMED. macOS System Integrity Protection strips every
                    # `DYLD_*` variable from the environment of a protected binary, so on this
                    # host the wrapper -- a `#!/bin/sh` script -- can never see one. Asserting a
                    # refusal here would be asserting it about a variable that never arrived,
                    # which is a green arm that measures nothing.
                    self.skipTest(f"${variable} does not survive an exec on this platform")
                self.inventory.unlink(missing_ok=True)
                parent = write(
                    self.nd / "parent_hostile_env.py",
                    "import os, subprocess\n"
                    f"env = dict(os.environ, **{{{variable!r}: '/nonexistent'}})\n"
                    f"code = subprocess.run(['python3', {str(clean)!r}], env=env).returncode\n"
                    "print('WRAPPER-EXIT', code)\n")
                result = self.guarded(parent)
                self.assertIn("WRAPPER-EXIT 3", result.stdout, result.stdout + result.stderr)
                self.assertIn("THE INTERPRETER WOULD START UNDER AN ENVIRONMENT", result.stderr)
                self.assertNotIn("CHILD-LOADED", result.stdout)


class TheRecordSaysWHICHShellRanAndWHICHBytesEnforced(Round7Fixture):
    """The dynamic half in the inventory record, because a ratchet reader cannot open this file.

    `path_shim` already answered "did the PATH wrapper half arm". `shell` and `real_bash` answer the
    same question for the half that actually enforces now -- and `static_scan` answers a question
    that did not exist before round 7: whether the record was written by a run whose first layer was
    deliberately stood down for a test. A reader who cannot see that would take a measurement of the
    restricted shell for a measurement of a production run.
    """

    def test_every_record_names_the_restricted_shell_and_pins_the_bash_that_enforced(self):
        clean = self.clean_child()
        parent = write(self.nd / "parent_record.py",
                       "import subprocess\n"
                       f"raise SystemExit(subprocess.run(['/bin/bash', '-c', "
                       f"'python3 {shlex.quote(str(clean))}']).returncode)\n")
        result = self.guarded(parent)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for record in self.records():
            self.assertEqual(record["shell"], "restricted", record)
            self.assertEqual(record["static_scan"], "enabled", record)
            self.assertEqual(record["real_bash"]["path"],
                             mgr._resolve_real_bash()[0], record)
            self.assertEqual(
                record["real_bash"]["sha256"],
                hashlib.sha256(pathlib.Path(record["real_bash"]["path"]).read_bytes()).hexdigest())

    def test_the_record_pins_EVERY_committed_shim_file_and_the_list_is_the_one_that_is_bound(self):
        """`path_shim_sha256` covers `COMMITTED_SHIM_FILES`, which is what the queue binds.

        THE TWO LISTS HAVE TO BE THE SAME LIST OR NEITHER MEANS ANYTHING. A wrapper the record
        digests but the queue does not bind can be swapped between staging and running; one the
        queue binds but no record digests leaves a run with no evidence of which bytes executed.
        Round 7 added eleven files to `bin/`, which is eleven chances to add one to a single list.
        """
        clean = self.clean_child()
        parent = write(self.nd / "parent_digest.py",
                       f"import subprocess\nsubprocess.run(['python3', {str(clean)!r}])\n")
        self.guarded(parent)
        digests = self.records()[0]["path_shim_sha256"]
        self.assertEqual(set(digests), set(mgr.COMMITTED_SHIM_FILES))
        for name, digest in digests.items():
            deployed = self.deployed_shim / name
            self.assertTrue(deployed.is_file(), name)
            self.assertEqual(digest,
                             hashlib.sha256((SHIM_TREE / name).read_bytes()).hexdigest(), name)

    def test_the_committed_shim_list_and_the_queues_bound_list_are_the_SAME_list(self):
        """`COMMITTED_SHIM_FILES` and `campaignctl.GUARD_SHIM_PATHS`, compared as sets of paths.

        They are two literals in two files by necessity -- `campaignctl` must not import the guard
        -- so the thing that keeps them one list is this comparison. Without it the pair is a
        convention, and a convention is what round 5's wrapper-swap control exists because of.
        """
        sys.path.insert(0, str(REPO / "docs" / "orchestration"))
        try:
            import campaignctl
        finally:
            sys.path.pop(0)
        bound = {str(path) for path in campaignctl.GUARD_SHIM_PATHS}
        declared = {f"nd-unfolding/mnv_guard_shim/{name}" for name in mgr.COMMITTED_SHIM_FILES}
        self.assertEqual(bound, declared)


class Round8Fixture(Round7Fixture):
    """Round 7's fixture, unchanged, plus what round 8's two reproducers need.

    IT REUSES ROUND 7's SHAPE FOR THE REASON ROUND 7 REUSED ROUND 6's: the defect is the same class
    -- an unscanned `python3 -I` reaching a foreign tree -- so an arm that passed there and fails
    here has to differ in the LAYER it was reached through and not in the scaffolding.

    THE `fork_exec` ARGUMENT LIST IS SPELLED ONCE, HERE, AND IT IS THE ONE `multiprocessing` USES.
    `_posixsubprocess.fork_exec` takes no keyword arguments, so a reproducer has to pass all
    twenty-three positionally; copying `multiprocessing.util.spawnv_passfds`'s own call rather than
    inventing one is what makes this a fixture built from the PRODUCER. If CPython changes the
    arity, this call raises `TypeError` from the C function and
    `test_the_floor_reads_the_positions_THIS_INTERPRETERS_OWN_CALLSITE_PASSES` says which position
    moved.
    """

    #: Positions 0, 1, 4 and 5 are the argv, the candidate executables, the cwd and the environment
    #: -- the four this guard reads. The rest are fds, signal and credential settings that no scan
    #: looks at, spelled exactly as `spawnv_passfds` spells them.
    FORK_EXEC_CALL = (
        "    argv, [os.fsencode(EXE)], True, (errpipe_write,), None, env_list,\n"
        "    -1, -1, -1, -1, -1, -1, errpipe_read, errpipe_write,\n"
        "    False, False, -1, None, None, None, -1, None, False)\n"
    )

    def fork_exec_parent(self, name: str, binding: str, *, argv: str = "[EXE, '-I', CHILD]",
                         env_list: str = None, child: str = None):
        """A parent that calls `fork_exec` DIRECTLY through `binding`, visiting no public API.

        `binding` is `_posixsubprocess.fork_exec` or `subprocess._fork_exec` -- two SEPARATE names
        for one C function, because `subprocess` binds its own with
        `from _posixsubprocess import fork_exec as _fork_exec`. A guard that patched only the module
        attribute would leave `subprocess.Popen` on the unpatched path, so each is a row.
        """
        if child is None:
            child_path, sentinel = self.hijacking_child(f"{name}_child")
        else:
            child_path, sentinel = pathlib.Path(child), None
        if env_list is None:
            env_list = ("[os.fsencode(k) + b'=' + os.fsencode(v) "
                        "for k, v in os.environ.items()]")
        parent = write(
            self.nd / f"parent_{name}.py",
            "import os, subprocess, sys, _posixsubprocess\n"
            f"EXE = sys.executable\n"
            f"CHILD = {str(child_path)!r}\n"
            f"argv = {argv}\n"
            f"env_list = {env_list}\n"
            "errpipe_read, errpipe_write = os.pipe()\n"
            f"pid = {binding}(\n"
            + self.FORK_EXEC_CALL +
            "os.close(errpipe_write)\n"
            "os.close(errpipe_read)\n"
            "_, status = os.waitpid(pid, 0)\n"
            "print('FORK-EXEC-EXIT', os.waitstatus_to_exitcode(status))\n")
        return parent, sentinel

    def assertAdmittedWithAGuardedChild(self, result, expected_stdout: str):
        """Exit 0, the child's own output, no launch refusal, and a depth-1 record from the child.

        THE DEPTH-1 RECORD IS THE ASSERTION THAT MATTERS. Exit 0 with only the parent's record would
        also be what an admitted-but-UNGUARDED child produces, which is the reviewer's finding in
        the silent direction; a record at depth 1 is a second interpreter that installed this guard
        and said so.
        """
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(expected_stdout, result.stdout)
        self.assertNotIn("[oi136 launch]", result.stderr)
        records = self.records()
        self.assertIn(1, [record["depth"] for record in records],
                      "no record at depth 1: the child ran without installing the guard")
        for record in records:
            if record["depth"] == 1:
                self.assertIsNotNone(record["propagated_from"], record)
                self.assertEqual(record["propagation"], "armed", record)
            self.assertIsNone(record["launch_refusal"], record)


class TheKernelFloorIsHookedAndTheResidualIsBelowIt(Round8Fixture):
    """ROUND 8: coverage enumerated by PUBLIC API is not coverage, so the floor is hooked.

    THE FINDING VERBATIM: "The finding-1 fix enumerates coverage by public API. I reached the kernel
    outside it, signature unchanged: `_posixsubprocess.fork_exec -> python3 -I <hijacking child>`:
    ran; sentinel present, HIJACK-LOADED printed, no refusal, no record.
    `multiprocessing.set_executable` (public API): an executable of the launcher's choosing ran, no
    scan, no record. Controls: same argv via `subprocess.run`, `os.posix_spawn`,
    `executable=sys.executable`: all exit 3, python-startup-flags-bypass-the-shim, sentinel absent.
    ... the uncovered case is the one where -I drops site, so there is no shim to fall back on --
    the exact defect finding 1 closed for the public primitives."

    THE TWO HALVES OF THE FINDING ARE NOT THE SAME KIND OF THING and the fix treats them
    differently, which the reviewer priced honestly and this class keeps. A direct `fork_exec` call
    is adversarial-only, and what it demands is a FLOOR: hook the last Python-visible layer, in both
    of the bindings CPython gives it, so that no list of public primitives is the boundary.
    `multiprocessing.set_executable` is public API a launcher may reasonably reach for, so beside
    the floor it is classified WHERE THE CHOICE IS MADE, with the chosen file named.

    AND THE RESIDUAL IS RESTATED AS WHAT IS ACTUALLY LEFT: a caller that reaches the kernel without
    that layer at all. That one is measured here as a run that SUCCEEDS -- see
    `test_a_ctypes_execve_of_an_isolated_interpreter_IS_THE_DECLARED_RESIDUAL` -- because a residual
    nobody demonstrated is a residual nobody can size.
    """

    # ---- the reviewer's first reproducer, in both bindings ----------------------------------

    FORK_EXEC_BINDINGS = {
        "_posixsubprocess.fork_exec": "_posixsubprocess.fork_exec",
        "subprocess._fork_exec": "subprocess._fork_exec",
    }

    def test_a_DIRECT_fork_exec_of_an_isolated_interpreter_is_REFUSED_in_both_bindings(self):
        """THE REPRODUCER. `fork_exec(argv=[python, '-I', child], ...)` from a guarded parent.

        BOTH BINDINGS ARE ROWS BECAUSE THEY ARE TWO NAMES. `subprocess` holds its own reference,
        made once at import by `from _posixsubprocess import fork_exec as _fork_exec`, and that is
        the one `Popen._execute_child` calls -- so a guard that rebound only the module attribute
        would have refused a direct call and left `subprocess` itself on the unpatched path.
        """
        for name, binding in self.FORK_EXEC_BINDINGS.items():
            with self.subTest(binding=name):
                self.inventory.unlink(missing_ok=True)
                parent, sentinel = self.fork_exec_parent(
                    f"fe_{name.replace('.', '_')}", binding)
                record = self.assertRefusedStatically(
                    self.guarded(parent), sentinel, mgr.LAUNCH_REASON_FLAGS, "-I")
                self.assertNotIn("FORK-EXEC-EXIT", self.guarded(parent).stdout,
                                 "the parent got past the call, so nothing was refused")
                self.assertEqual(record["declared_gap"], mgr.DECLARED_GAP)

    def test_the_floor_scans_multiprocessings_OWN_launcher_which_is_how_forkserver_is_covered(self):
        """`multiprocessing.util.spawnv_passfds` is the function `forkserver` launches through.

        WHY THIS ARM IS THE FORKSERVER'S COVERAGE. `ForkServer.ensure_running` builds
        `[exe] + interpreter flags + ['-c', cmd]` and hands it to `util.spawnv_passfds`, which calls
        `_posixsubprocess.fork_exec` -- so the forkserver's launch is not a separate boundary, it is
        a caller of the one this class hooks. Both halves of that are measured rather than asserted:
        the composition is read out of THIS interpreter's own `multiprocessing` source below, and
        the refusal is measured here by handing `spawnv_passfds` the reviewer's argv directly.
        """
        import inspect
        import multiprocessing.forkserver
        import multiprocessing.util
        forkserver_source = inspect.getsource(multiprocessing.forkserver)
        self.assertIn("util.spawnv_passfds(", forkserver_source,
                      "forkserver no longer launches through spawnv_passfds, so this arm no "
                      "longer measures the forkserver's coverage")
        self.assertIn("_posixsubprocess.fork_exec(",
                      inspect.getsource(multiprocessing.util.spawnv_passfds),
                      "spawnv_passfds no longer calls fork_exec, so the floor is no longer under "
                      "it")
        child, sentinel = self.hijacking_child("mp_launcher_child")
        parent = write(
            self.nd / "parent_mp_launcher.py",
            "import os, sys, multiprocessing.util as mu\n"
            f"pid = mu.spawnv_passfds(os.fsencode(sys.executable),\n"
            f"    [sys.executable, '-I', {str(child)!r}], ())\n"
            "os.waitpid(pid, 0)\n"
            "print('SPAWNV-PASSFDS-RETURNED')\n")
        self.assertRefusedStatically(self.guarded(parent), sentinel,
                                     mgr.LAUNCH_REASON_FLAGS, "-I")

    # ---- the reviewer's second reproducer: multiprocessing.set_executable --------------------

    def test_set_executable_to_a_NON_PYTHON_is_refused_WHERE_THE_CHOICE_IS_MADE(self):
        """The reviewer's public-API half: an executable of the launcher's choosing used to run.

        `set_executable` names the file every `spawn` and `forkserver` child is exec'd from, and
        `multiprocessing` then appends its OWN argv (`-c 'from multiprocessing.spawn import
        spawn_main; ...'`). So the file must be a Python interpreter, and this `.sh` -- whose body
        is a `touch` this guard would happily admit inside a shell script -- is refused for what it
        is being asked to be, at the line that chose it, with the chosen path named.
        """
        sentinel = self.tmp / "non-python-executable-ran"
        chosen = write(self.nd / "chosen_exec.sh", f"#!/bin/sh\ntouch {sentinel}\n")
        chosen.chmod(0o755)
        parent = write(
            self.nd / "parent_setexec_nonpython.py",
            "import multiprocessing\n"
            f"multiprocessing.set_executable({str(chosen)!r})\n"
            "def work():\n"
            "    pass\n"
            "if __name__ == '__main__':\n"
            "    proc = multiprocessing.get_context('spawn').Process(target=work)\n"
            "    proc.start()\n"
            "    proc.join()\n"
            "    print('SETEXEC-EXIT', proc.exitcode)\n")
        record = self.assertRefusedStatically(self.guarded(parent), sentinel,
                                              mgr.LAUNCH_REASON_UNPROVEN, "set_executable")
        self.assertIn(str(chosen), record["launch_refusal"]["offending_flag"])
        self.assertEqual(record["launch_refusal"]["executable"], str(chosen.resolve()))

    def test_set_executable_to_A_PYTHON_WITH_dash_I_is_refused_and_names_the_FLAG(self):
        """The second arm of the same finding: the chosen file IS Python, and it isolates.

        A `#!<python> -I` file is the spelling that makes `set_executable` reach `-I` without a
        launcher writing `-I` anywhere -- multiprocessing builds the argv, so the flag has to come
        from the file. The refusal is the FLAG refusal and not the set_executable one, which is the
        only evidence that the shebang was read rather than the name trusted.
        """
        chosen = write(self.nd / "python_isolated_shim", f"#!{sys.executable} -I\n")
        chosen.chmod(0o755)
        sentinel = self.tmp / "isolated-shim-child-ran"
        parent = write(
            self.nd / "parent_setexec_isolated.py",
            "import multiprocessing\n"
            f"multiprocessing.set_executable({str(chosen)!r})\n"
            "def work():\n"
            "    pass\n"
            "if __name__ == '__main__':\n"
            "    proc = multiprocessing.get_context('spawn').Process(target=work)\n"
            "    proc.start()\n"
            "    proc.join()\n"
            "    print('SETEXEC-EXIT', proc.exitcode)\n")
        self.assertRefusedStatically(self.guarded(parent), sentinel,
                                     mgr.LAUNCH_REASON_FLAGS, "-I")

    def test_the_floor_still_refuses_when_set_executable_ITSELF_IS_BYPASSED(self):
        """`multiprocessing.spawn._python_exe = ...`, the module global `set_executable` writes.

        WHY THIS ARM EXISTS. The `set_executable` hook is where the refusal LANDS, not what holds
        the boundary -- and a class that only measured the hook could not tell those apart. Writing
        the global directly declines the public API entirely, exactly as the reviewer's `fork_exec`
        call declined `subprocess`, and what refuses then is the floor: same exit, same record, and
        a `forkserver` launch is refused through the same path.
        """
        chosen = write(self.nd / "python_isolated_global", f"#!{sys.executable} -I\n")
        chosen.chmod(0o755)
        sentinel = self.tmp / "isolated-global-child-ran"
        for method in ("spawn", "forkserver"):
            with self.subTest(start_method=method):
                self.inventory.unlink(missing_ok=True)
                parent = write(
                    self.nd / f"parent_global_{method}.py",
                    "import multiprocessing, multiprocessing.spawn as spawn, os\n"
                    f"spawn._python_exe = os.fsencode({str(chosen)!r})\n"
                    "def work():\n"
                    "    pass\n"
                    "if __name__ == '__main__':\n"
                    f"    proc = multiprocessing.get_context({method!r}).Process(target=work)\n"
                    "    proc.start()\n"
                    "    proc.join()\n"
                    "    print('GLOBAL-EXIT', proc.exitcode)\n")
                self.assertRefusedStatically(self.guarded(parent), sentinel,
                                             mgr.LAUNCH_REASON_FLAGS, "-I")

    def test_the_floor_IS_INSTALLED_IN_A_CHILD_TOO_and_a_grandchild_is_refused_there(self):
        """The floor travels with the contract, and that is measured rather than inferred.

        `install()` installs the floor, and a covered child calls `install()` from
        `sitecustomize` -- so "the child has it too" follows from the code. It is asserted anyway,
        one boundary out, because every round of this review has found a claim that followed from
        the code and was false in the tree: the child here is ADMITTED, installs the guard, and its
        OWN direct `fork_exec` call is what gets refused. The evidence is the depth: a REFUSED-launch
        record at depth 1 is a second interpreter that refused, and the parent's record at depth 0 is
        clean.
        """
        grandchild, sentinel = self.hijacking_child("floor_grandchild")
        child = write(
            self.nd / "child_calls_the_floor.py",
            "import os, sys, _posixsubprocess\n"
            "EXE = sys.executable\n"
            f"CHILD = {str(grandchild)!r}\n"
            "argv = [EXE, '-I', CHILD]\n"
            "env_list = [os.fsencode(k) + b'=' + os.fsencode(v) for k, v in os.environ.items()]\n"
            "errpipe_read, errpipe_write = os.pipe()\n"
            "pid = _posixsubprocess.fork_exec(\n"
            + self.FORK_EXEC_CALL +
            "os.close(errpipe_write)\n"
            "os.close(errpipe_read)\n"
            "_, status = os.waitpid(pid, 0)\n"
            "print('CHILD-FORK-EXEC-EXIT', os.waitstatus_to_exitcode(status))\n")
        parent = write(
            self.nd / "parent_child_floor.py",
            "import subprocess, sys\n"
            f"raise SystemExit(subprocess.run([sys.executable, {str(child)!r}]).returncode)\n")
        result = self.guarded(parent)
        self.assertEqual(result.returncode, mgr.VIOLATION_EXIT, result.stdout + result.stderr)
        self.assertNotIn("HIJACK-LOADED", result.stdout)
        self.assertNotIn("CHILD-FORK-EXEC-EXIT", result.stdout)
        self.assertFalse(sentinel.exists(),
                         "the grandchild ran, so the child interpreter had no floor")
        by_depth = {record["depth"]: record for record in self.records()}
        self.assertEqual(sorted(by_depth), [0, 1], self.records())
        self.assertIsNone(by_depth[0]["launch_refusal"],
                          "the PARENT refused, so this arm did not reach the child's own floor")
        self.assertEqual(by_depth[1]["verdict"], "REFUSED launch")
        self.assertEqual(by_depth[1]["refusal_site"], mgr.SITE_LAUNCH)
        self.assertEqual(by_depth[1]["launch_refusal"]["reason"], mgr.LAUNCH_REASON_FLAGS)
        self.assertIsNotNone(by_depth[1]["propagated_from"])

    # ---- the reviewer's controls, which must still refuse ------------------------------------

    #: THE REVIEWER'S OWN CONTROL SET, verbatim in shape: the SAME argv, through the public
    #: primitives round 7 closed. They are here so the floor cannot be credited with a refusal one
    #: of them was already making, and so a regression in either layer is attributable.
    CONTROL_SPELLINGS = {
        "subprocess.run": "raise SystemExit(subprocess.run([EXE, '-I', CHILD]).returncode)",
        "subprocess.run executable=": (
            "raise SystemExit(subprocess.run(['ls', '-I', CHILD],\n"
            "    executable=sys.executable).returncode)"),
        "os.posix_spawn": ("pid = os.posix_spawn(EXE, [EXE, '-I', CHILD], dict(os.environ))\n"
                           "_, status = os.waitpid(pid, 0)\n"
                           "raise SystemExit(os.waitstatus_to_exitcode(status))"),
    }

    def test_the_reviewers_controls_are_still_refused_at_the_public_primitives(self):
        for name, call in self.CONTROL_SPELLINGS.items():
            with self.subTest(control=name):
                self.inventory.unlink(missing_ok=True)
                child, sentinel = self.hijacking_child(f"ctl_{name.split('.')[0]}_{len(name)}")
                parent = write(
                    self.nd / f"parent_ctl_{abs(hash(name)) % 100000}.py",
                    "import os, subprocess, sys\n"
                    "EXE = sys.executable\n"
                    f"CHILD = {str(child)!r}\n"
                    f"{call}\n")
                self.assertRefusedStatically(self.guarded(parent), sentinel,
                                             mgr.LAUNCH_REASON_FLAGS, "-I")

    # ---- the silent direction: what must STILL RUN -------------------------------------------

    def test_every_multiprocessing_START_METHOD_and_the_POOL_still_run_a_GUARDED_child(self):
        """THE POWER ARM. A floor that refused every `fork_exec` would pass every arm above.

        `spawn` and `forkserver` both launch through `spawnv_passfds` -> `fork_exec`, so both now
        pass through the new hook on every correct run; `ProcessPoolExecutor` is here beside them
        because it is the spelling this repository's launchers actually use, and it reaches the same
        place by a different route. Each must be ADMITTED and each must leave a record from a second
        interpreter that installed the guard -- exit 0 alone would also be what an unguarded child
        produces.
        """
        arms = {
            "spawn": ("import multiprocessing\n"
                      "def work():\n"
                      "    print('SPAWN-CHILD-RAN')\n"
                      "if __name__ == '__main__':\n"
                      "    proc = multiprocessing.get_context('spawn').Process(target=work)\n"
                      "    proc.start()\n"
                      "    proc.join()\n"
                      "    print('ARM-EXIT', proc.exitcode)\n"),
            "forkserver": ("import multiprocessing\n"
                           "def work():\n"
                           "    print('FORKSERVER-CHILD-RAN')\n"
                           "if __name__ == '__main__':\n"
                           "    ctx = multiprocessing.get_context('forkserver')\n"
                           "    proc = ctx.Process(target=work)\n"
                           "    proc.start()\n"
                           "    proc.join()\n"
                           "    print('ARM-EXIT', proc.exitcode)\n"),
            "ProcessPoolExecutor": (
                "import concurrent.futures, multiprocessing\n"
                "def work(value):\n"
                "    return value * 2\n"
                "if __name__ == '__main__':\n"
                "    ctx = multiprocessing.get_context('spawn')\n"
                "    with concurrent.futures.ProcessPoolExecutor(max_workers=1,\n"
                "            mp_context=ctx) as pool:\n"
                "        print('POOL-RESULT', pool.submit(work, 21).result())\n"
                "    print('ARM-EXIT 0')\n"),
        }
        for name, body in arms.items():
            with self.subTest(arm=name):
                self.inventory.unlink(missing_ok=True)
                parent = write(self.nd / f"parent_power_{name}.py", body)
                self.assertAdmittedWithAGuardedChild(self.guarded(parent), "ARM-EXIT 0")

    def test_the_fork_start_method_INHERITS_the_guard_and_its_own_launches_are_refused(self):
        """`fork` needs no hook, and this is the measurement rather than the assertion.

        A forked child IS this interpreter -- same `sys.meta_path`, same wrapped primitives, same
        patched `fork_exec` -- so what proves the inheritance is a REFUSAL issued from inside the
        fork child, not a claim about how `fork` works. The child's `python3 -I` launch is refused,
        `Process.exitcode` carries this guard's exit 3 out of it, and the hijack sentinel is absent.
        """
        child, sentinel = self.hijacking_child("fork_inherit_child")
        parent = write(
            self.nd / "parent_fork_inherit.py",
            "import multiprocessing, subprocess, sys\n"
            "def work():\n"
            f"    subprocess.run([sys.executable, '-I', {str(child)!r}])\n"
            "if __name__ == '__main__':\n"
            "    proc = multiprocessing.get_context('fork').Process(target=work)\n"
            "    proc.start()\n"
            "    proc.join()\n"
            "    print('FORK-CHILD-EXITCODE', proc.exitcode)\n")
        result = self.guarded(parent)
        self.assertIn(f"FORK-CHILD-EXITCODE {mgr.VIOLATION_EXIT}", result.stdout,
                      result.stdout + result.stderr)
        self.assertIn("[oi136 launch]", result.stderr)
        self.assertNotIn("HIJACK-LOADED", result.stdout)
        self.assertFalse(sentinel.exists(),
                         "the fork child's isolated launch ran, so the guard was not inherited")

    def test_a_CLEAN_child_launched_AT_THE_FLOOR_ITSELF_still_runs_and_is_guarded(self):
        """The floor's own silent direction: a correct `fork_exec` call is admitted and re-armed.

        Without this the floor could be a function that refuses every direct call, which would pass
        every refusal arm in this class and break `multiprocessing` on every correct run. The child
        is the ordinary clean child, launched with no isolating flag, and it must leave a depth-1
        record -- so the environment this layer wrote back is one the shim could still read.
        """
        clean = self.clean_child("floor_clean_child")
        parent, _ = self.fork_exec_parent("fe_clean", "_posixsubprocess.fork_exec",
                                          argv="[EXE, CHILD]", child=str(clean))
        result = self.guarded(parent)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("CHILD-LOADED RIGHT TREE", result.stdout)
        self.assertIn("FORK-EXEC-EXIT 0", result.stdout)
        self.assertNotIn("[oi136 launch]", result.stderr)
        self.assertIn(1, [record["depth"] for record in self.records()],
                      "the child ran without installing the guard")

    def test_an_ENVIRONMENT_LIST_that_strips_the_contract_is_RE_ARMED_at_the_floor(self):
        """The floor's environment half, in the direction that REPAIRS rather than refuses.

        `fork_exec` receives the environment as `[b"NAME=VALUE", ...]`, so the contract this guard
        exported has to be read out of a list of bytes and, when the caller assembled a list without
        it, written back into one. That write-back is the only path in this file that BUILDS an
        `env_list`, and nothing else here exercises it: the refusal arms never reach it and the
        inherited-environment arms have nothing to repair. The measurement is the child's own
        record -- a depth-1 record means an interpreter that started from THIS list found the
        contract and the shim-first `PYTHONPATH` in it and installed the guard.
        """
        clean = self.clean_child("floor_rearm_child")
        parent, _ = self.fork_exec_parent(
            "fe_rearm", "_posixsubprocess.fork_exec", argv="[EXE, CHILD]", child=str(clean),
            # PATH ONLY: no MNV_GUARD_* and no PYTHONPATH, which is the state
            # `_environment_reaching_child_is_armed` refuses when it cannot be repaired from this
            # process's own os.environ -- and here it can be.
            env_list="[b'PATH=' + os.fsencode(os.environ['PATH'])]")
        result = self.guarded(parent)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("CHILD-LOADED RIGHT TREE", result.stdout)
        self.assertIn("FORK-EXEC-EXIT 0", result.stdout)
        self.assertNotIn("[oi136 launch]", result.stderr)
        records = self.records()
        self.assertIn(1, [record["depth"] for record in records],
                      "the child started from the stripped list without installing the guard")
        self.assertEqual([record["launch_env"] for record in records if record["depth"] == 0],
                         ["re-armed"],
                         "the parent's record does not say the environment was re-armed, so the "
                         "child was guarded by something other than this layer's repair")

    def test_set_executable_to_THIS_interpreter_is_ADMITTED_which_is_the_other_direction(self):
        """`set_executable(sys.executable)` is what a correct launcher does, and it must pass.

        It is the same call the stdlib itself makes at `multiprocessing.spawn` import time, so a
        hook that refused it would refuse `import multiprocessing`.
        """
        parent = write(
            self.nd / "parent_setexec_ok.py",
            "import multiprocessing, sys\n"
            "multiprocessing.set_executable(sys.executable)\n"
            "def work():\n"
            "    print('CHOSEN-INTERPRETER-CHILD-RAN')\n"
            "if __name__ == '__main__':\n"
            "    proc = multiprocessing.get_context('spawn').Process(target=work)\n"
            "    proc.start()\n"
            "    proc.join()\n"
            "    print('ARM-EXIT', proc.exitcode)\n")
        self.assertAdmittedWithAGuardedChild(self.guarded(parent), "ARM-EXIT 0")

    def test_a_launch_THIS_GUARD_REWROTE_is_not_RE_SCANNED_one_layer_down(self):
        """THE COST OF A FLOOR, PAID ONCE: an approved launch is not read again underneath.

        A rewritten shell launch runs with `PATH` set to the guard's wrapper directories and nothing
        else, so a second scan of it resolves `ls` to a forwarder that is in no system prefix and
        `_check_leaf` refuses a correct program. This was already LIVE before round 8 wherever
        `subprocess.Popen` chose `os.posix_spawn` over `fork_exec` -- `close_fds=False` is the
        documented trigger -- and it is the verdict this arm changes: both spellings of the same
        launch now run. Both are here because they take different routes out of `Popen` and only
        one of them is the new hook.
        """
        routes = {"through fork_exec": "", "through os.posix_spawn": ", close_fds=False"}
        for name, extra in routes.items():
            with self.subTest(route=name):
                self.inventory.unlink(missing_ok=True)
                parent = write(
                    self.nd / f"parent_ticket_{len(extra)}.py",
                    "import subprocess\n"
                    f"code = subprocess.run('ls victim.py', shell=True, cwd={str(self.nd)!r}"
                    f"{extra}).returncode\n"
                    "print('SHELL-EXIT', code)\n")
                result = self.guarded(parent)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("SHELL-EXIT 0", result.stdout)
                self.assertNotIn("[oi136 launch]", result.stderr)
                self.assertIsNone(self.records()[0]["launch_refusal"])

    # ---- fail-closed at the floor: a call whose shape cannot be read -------------------------

    def test_a_fork_exec_call_this_guard_CANNOT_READ_refuses_and_NAMES_the_layer(self):
        """Two shapes, and both would otherwise have started an unguarded interpreter.

        `fork_exec` takes no keyword arguments and has no introspectable signature, so its
        parameters are POSITIONS and this guard's copy of them is a constant. A call with fewer
        arguments than the four it reads cannot be read at all; an environment member that is not
        `NAME=VALUE` means the propagation contract reaching the child cannot be read, and the
        second one is not hypothetical -- `[b'NOEQUALS']` as the whole environment is a child with
        no contract and no shim-first `PYTHONPATH`, which is the finding one more time.

        THE REASON CONSTANT NAMES THE LAYER, which is the point: every other refusal in this file
        could have come from any of three places, and `LAUNCH_REASON_KERNEL_FLOOR` says the floor
        itself declined to guess.
        """
        child, sentinel = self.hijacking_child("shape_child")
        arms = {
            "too few arguments to read": (
                "import _posixsubprocess, sys\n"
                f"_posixsubprocess.fork_exec([sys.executable, {str(child)!r}],\n"
                "    [sys.executable.encode()], True)\n"),
            "an environment member that is not NAME=VALUE": (
                "import os, sys, _posixsubprocess\n"
                f"argv = [sys.executable, {str(child)!r}]\n"
                "errpipe_read, errpipe_write = os.pipe()\n"
                "_posixsubprocess.fork_exec(\n"
                "    argv, [os.fsencode(sys.executable)], True, (errpipe_write,), None,\n"
                "    [b'NOEQUALS'],\n"
                "    -1, -1, -1, -1, -1, -1, errpipe_read, errpipe_write,\n"
                "    False, False, -1, None, None, None, -1, None, False)\n"),
        }
        for name, body in arms.items():
            with self.subTest(shape=name):
                self.inventory.unlink(missing_ok=True)
                sentinel.unlink(missing_ok=True)
                parent = write(self.nd / f"parent_shape_{len(name)}.py", body)
                record = self.assertRefusedStatically(self.guarded(parent), sentinel,
                                                      mgr.LAUNCH_REASON_KERNEL_FLOOR)
                self.assertIn("fork_exec", record["launch_refusal"]["offending_flag"])
                self.assertEqual(record["outcome"],
                                 mgr.launch_outcome(record["launch_refusal"]))

    # ---- the bindings and positions, re-derived from THIS interpreter ------------------------

    def test_BOTH_fork_exec_bindings_exist_on_this_interpreter_and_name_ONE_function(self):
        """The producer's own answer to "how many bindings are there", not this guard's tuple.

        A pristine interpreter is asked, in a subprocess, because the test process has imported the
        guard module and a later `install()` anywhere would make the same question return the
        wrapper. Both names must exist and both must be the SAME C function -- which is exactly why
        patching one does not patch the other.
        """
        probe = run("-c",
                    "import _posixsubprocess, subprocess\n"
                    "print('BINDINGS',\n"
                    "      hasattr(_posixsubprocess, 'fork_exec'),\n"
                    "      hasattr(subprocess, '_fork_exec'),\n"
                    "      subprocess._fork_exec is _posixsubprocess.fork_exec)\n")
        self.assertEqual(probe.returncode, 0, probe.stderr)
        self.assertIn("BINDINGS True True True", probe.stdout)
        self.assertEqual(
            mgr._FORK_EXEC_BINDINGS,
            (("_posixsubprocess", "fork_exec"), ("subprocess", "_fork_exec")),
            "the guard's binding table no longer matches the two names this interpreter has")

    def test_the_floor_reads_the_positions_THIS_INTERPRETERS_OWN_CALLSITE_PASSES(self):
        """The four offsets, re-derived from `subprocess.Popen._execute_child`'s own source.

        THE FIXTURE IS BUILT FROM THE PRODUCER AND NOT FROM THE RULE. `fork_exec` takes no keyword
        arguments, so the guard's `_FORK_EXEC_*_INDEX` constants are a transcription of CPython's
        callsite -- and a transcription checked against itself cannot disagree with itself. So the
        callsite is parsed and the ARGUMENT EXPRESSIONS are read: an interpreter that inserted a
        parameter is red here, naming the position that moved, rather than silently having this
        guard parse a file descriptor as an environment.
        """
        import ast
        import inspect
        import textwrap
        source = textwrap.dedent(inspect.getsource(subprocess.Popen._execute_child))
        calls = [node for node in ast.walk(ast.parse(source))
                 if isinstance(node, ast.Call)
                 and isinstance(node.func, ast.Name) and node.func.id == "_fork_exec"]
        self.assertEqual(len(calls), 1, "expected exactly one _fork_exec callsite to read")
        arguments = [ast.unparse(argument) for argument in calls[0].args]
        self.assertEqual(calls[0].keywords, [], "fork_exec is called with keywords now")
        expected = {
            mgr._FORK_EXEC_ARGV_INDEX: "args",
            mgr._FORK_EXEC_EXECUTABLE_LIST_INDEX: "executable_list",
            mgr._FORK_EXEC_CWD_INDEX: "cwd",
            mgr._FORK_EXEC_ENV_LIST_INDEX: "env_list",
        }
        for index, name in expected.items():
            self.assertEqual(arguments[index], name,
                             f"position {index} of fork_exec is {arguments[index]!r} on this "
                             f"interpreter and the guard reads it as {name!r}")
        self.assertGreaterEqual(len(arguments), mgr._FORK_EXEC_MINIMUM_ARITY)
        self.assertEqual(len(arguments), 23,
                         "fork_exec's arity changed; Round8Fixture.FORK_EXEC_CALL spells all of "
                         "them positionally and has to change with it")

    def test_install_REPLACES_both_bindings_and_NEITHER_wrapper_wraps_the_OTHER(self):
        """The patch is measured on the module objects, and so is the absence of a double layer.

        WHY THE SECOND HALF MATTERS AS MUCH AS THE FIRST. The two bindings name one C function, so a
        careless second patch would wrap the first wrapper -- and then every `subprocess` launch
        would be scanned twice, the second time against the restricted `PATH` its own rewrite
        carries, which REFUSES a correct program. Each wrapper's `__wrapped__` must therefore be the
        original C function and not the other wrapper.
        """
        probe = write(
            self.nd / "probe_bindings.py",
            "import _posixsubprocess, subprocess, sys\n"
            f"sys.path.insert(0, {str(self.nd)!r})\n"
            "before = (_posixsubprocess.fork_exec, subprocess._fork_exec)\n"
            "import mnv_guarded_run as mgr\n"
            f"mgr.install({str(self.good)!r})\n"
            "after = (_posixsubprocess.fork_exec, subprocess._fork_exec)\n"
            "print('REPLACED', [a is not b for a, b in zip(before, after)])\n"
            "print('MARKED', [getattr(f, '_mnv_guard_floor', False) for f in after])\n"
            "print('WRAPS_THE_ORIGINAL',\n"
            "      [getattr(f, '__wrapped__', None) is b for f, b in zip(after, before)])\n")
        result = run(probe)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("REPLACED [True, True]", result.stdout)
        self.assertIn("MARKED [True, True]", result.stdout)
        self.assertIn("WRAPS_THE_ORIGINAL [True, True]", result.stdout)

    def test_the_STDLIB_ITSELF_binds_fork_exec_in_exactly_the_two_places_this_guard_PATCHES(self):
        """A COVERING SEARCH, because "we patched every binding" is an absence claim.

        THE CLASS AND THE COUNT TOGETHER. The search is over every `.py` file under this
        interpreter's own `stdlib` path, excluding the test trees and `site-packages`; what it
        counts is FILES THAT MENTION `fork_exec` AT ALL, which is wider than "files that bind it"
        and therefore cannot miss a binding by being too clever about what a binding looks like. On
        3.11, 3.12 and 3.13 the answer is two files -- `subprocess.py`, which makes the alias, and
        `multiprocessing/util.py`, which reaches the module attribute -- and both are covered by
        `_FORK_EXEC_BINDINGS`.

        WHAT IT CANNOT SAY: it reads the stdlib, so a THIRD-PARTY module that binds its own alias
        before this guard installs is outside it. That is the same shape as arm (1) of
        `DECLARED_GAP` -- a file rather than an argv -- and the floor still covers the launch,
        because a private alias made by `from _posixsubprocess import fork_exec` after `install()`
        picks up the wrapper and one made before it reaches the same C function this guard's own
        wrapper calls only if nothing rebinds it. It is named here rather than left to be assumed.
        """
        import sysconfig
        stdlib = pathlib.Path(sysconfig.get_paths()["stdlib"])
        skip = ("site-packages", "/test/", "/tests/", "/idlelib/", "/lib2to3/")
        mentions = {}
        for module in stdlib.rglob("*.py"):
            text = str(module)
            if any(part in text for part in skip):
                continue
            try:
                body = module.read_text(errors="replace")
            except OSError:
                continue
            if "fork_exec" in body:
                mentions[str(module.relative_to(stdlib))] = [
                    line.strip() for line in body.splitlines() if "fork_exec" in line]
        self.assertEqual(sorted(mentions), ["multiprocessing/util.py", "subprocess.py"],
                         f"the stdlib mentions fork_exec somewhere new; every mention has to be "
                         f"covered by mgr._FORK_EXEC_BINDINGS or added to it: {sorted(mentions)}")
        # THE ALIAS, READ RATHER THAN REMEMBERED: `subprocess` binds it under exactly one name and
        # that name is the second entry of the guard's table.
        aliases = [line for line in mentions["subprocess.py"]
                   if line.startswith("from _posixsubprocess import fork_exec as ")]
        self.assertEqual(aliases, ["from _posixsubprocess import fork_exec as _fork_exec"],
                         mentions["subprocess.py"])
        self.assertIn(("subprocess", "_fork_exec"), mgr._FORK_EXEC_BINDINGS)
        # And `multiprocessing` reaches the MODULE ATTRIBUTE, which is the first entry.
        self.assertTrue(any("_posixsubprocess.fork_exec(" in line
                            for line in mentions["multiprocessing/util.py"]),
                        mentions["multiprocessing/util.py"])
        self.assertIn(("_posixsubprocess", "fork_exec"), mgr._FORK_EXEC_BINDINGS)

    def test_every_launch_reason_has_a_headline_an_explanation_AND_an_outcome(self):
        """The three tables a refusal is printed and recorded from, checked for completeness.

        WHY THIS IS WORTH A CONTROL. `_report_launch` indexes `_LAUNCH_HEADLINES` and
        `_LAUNCH_EXPLANATIONS` by reason with `[]`, and `mnv_guard_shim/wrapper_exec.py` does the
        same -- so a reason constant added without its three rows turns a REFUSAL into a `KeyError`
        raised out of the guard, which is the one failure mode a fail-closed file cannot have. The
        enumeration comes from the module's own `LAUNCH_REASON_*` names rather than from a list
        anybody maintains.
        """
        reasons = {name: value for name, value in vars(mgr).items()
                   if name.startswith("LAUNCH_REASON_") and isinstance(value, str)}
        self.assertGreaterEqual(len(reasons), 6, reasons)
        self.assertIn("LAUNCH_REASON_KERNEL_FLOOR", reasons)
        self.assertEqual(len(set(reasons.values())), len(reasons),
                         "two launch reasons share a string, so a record cannot distinguish them")
        for name, reason in sorted(reasons.items()):
            with self.subTest(reason=name):
                self.assertIn(reason, mgr._LAUNCH_HEADLINES)
                self.assertIn(reason, mgr._LAUNCH_EXPLANATIONS)
                self.assertIn(reason, mgr.LAUNCH_OUTCOMES)
                self.assertTrue(mgr.launch_outcome({"reason": reason}).startswith("refused:"))

    # ---- the residual, measured as a run that SUCCEEDS --------------------------------------

    def test_a_ctypes_execve_of_an_isolated_interpreter_IS_THE_DECLARED_RESIDUAL(self):
        """THE ONE ARM HERE THAT ASSERTS A HIJACK RAN, because that is what a residual is.

        `ctypes` calls `execve` in libc directly: no `subprocess`, no `os.exec*`, no
        `_posixsubprocess`, nothing Python-visible that this guard could have hooked. The child runs
        with `-I`, loads the wrong tree and prints so -- and the record the parent leaves must
        describe that boundary in `declared_gap`, because a ratchet reader consuming records is the
        one who would otherwise read "four residuals, none of them an unscanned Python launch" as a
        claim this route refutes.

        IT IS DELIBERATELY NOT A REFUSAL. Refusing `ctypes` would mean refusing every `CDLL`, which
        is neither possible from here nor honest: what is left is named, sized and written into
        every record instead.
        """
        child, sentinel = self.hijacking_child("ctypes_child")
        execve = ("libc = ctypes.CDLL(None, use_errno=True)\n"
                  "argv = (ctypes.c_char_p * 4)(sys.executable.encode(), b'-I',\n"
                  f"    {str(child)!r}.encode(), None)\n"
                  "envp_values = [f'{k}={v}'.encode() for k, v in os.environ.items()]\n"
                  "envp = (ctypes.c_char_p * (len(envp_values) + 1))(*envp_values, None)\n"
                  "libc.execve(sys.executable.encode(), argv, envp)\n")
        # IN PLACE, which is the sharpest statement of the residual: `execve` replaces the process
        # image, so the guarded parent's own `finally` never runs and the run leaves NO record at
        # all. A reader of the inventory does not see a narrower run here, they see nothing.
        in_place = write(self.nd / "parent_ctypes_inplace.py",
                         "import ctypes, os, sys\n" + execve +
                         "print('EXECVE-FAILED', ctypes.get_errno())\n")
        result = self.guarded(in_place)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("HIJACK-LOADED WRONG TREE", result.stdout,
                      "the ctypes execve did NOT reach the wrong tree, so this arm is no longer "
                      "measuring the declared residual and the residual's text has to change")
        self.assertTrue(sentinel.exists(), "the isolated child did not run")
        self.assertNotIn("[oi136 launch]", result.stderr)
        self.assertEqual(self.records(), [],
                         "an in-place execve left a record, so it did not replace the image and "
                         "this arm measures something else")
        # AND FORKED, so a record SURVIVES to be read. `os.fork` is not an exec and this guard does
        # not wrap it; the child reaches the kernel through libc and the parent lives to write the
        # boundary down, which is the shape a launcher would actually have.
        self.inventory.unlink(missing_ok=True)
        sentinel.unlink(missing_ok=True)
        forked = write(self.nd / "parent_ctypes_forked.py",
                       "import ctypes, os, sys\n"
                       "pid = os.fork()\n"
                       "if pid == 0:\n"
                       "    " + execve.replace("\n", "\n    ").rstrip() + "\n"
                       "    os._exit(97)\n"
                       "_, status = os.waitpid(pid, 0)\n"
                       "print('FORKED-EXECVE-EXIT', os.waitstatus_to_exitcode(status))\n")
        result = self.guarded(forked)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("HIJACK-LOADED WRONG TREE", result.stdout)
        self.assertIn("FORKED-EXECVE-EXIT 0", result.stdout)
        self.assertTrue(sentinel.exists())
        self.assertNotIn("[oi136 launch]", result.stderr)
        # THE RECORD IS WHERE A READER MEETS THIS BOUNDARY, so the residual has to be IN it and has
        # to name this route rather than gesture at one.
        record = self.records()[0]
        self.assertEqual(record["declared_gap"], mgr.DECLARED_GAP)
        self.assertIn("_posixsubprocess.fork_exec", record["declared_gap"])
        self.assertIn("ctypes", record["declared_gap"])
        self.assertIn("NAMED AND NOT COVERED", record["declared_gap"])
        # AND THE SUPERSEDED SENTENCE IS GONE rather than softened: round 7's residual (4) said an
        # admitted Python child was covered "by these same hooks in turn" and stopped there, which
        # is the sentence the reviewer read as implying coverage this guard did not have.
        self.assertNotIn("so its own launches are subject to everything above one level down",
                         record["declared_gap"])

    def test_the_residual_is_the_ONLY_uncovered_route_among_the_ones_measured_here(self):
        """The census, so "named and not covered" is a count and not a mood.

        Every route this class launches through is either refused (and its sentinel absent) or is
        the declared residual. There is exactly ONE of the second kind, and it is the ctypes one; a
        second uncovered route appearing here without the residual text changing is the failure this
        arm exists to make loud.
        """
        self.assertIn("ctypes", mgr.DECLARED_GAP)
        self.assertIn("or cffi", mgr.DECLARED_GAP)
        self.assertIn("REBUILT INTERPRETER", mgr.DECLARED_GAP)
        # FOUR RESIDUALS, STILL: round 8 REPLACED arm (4), it did not add a fifth. A count that
        # drifted would make the docstring and the record disagree about the boundary.
        self.assertTrue(mgr.DECLARED_GAP.startswith("FOUR RESIDUALS"), mgr.DECLARED_GAP[:40])
        for arm in ("(1) TRUST BY LOCATION", "(2) THE RESTRICTED-SHELL GUARANTEE",
                    "(3) AN sbatch JOB", "(4) AN ADMITTED PYTHON CHILD"):
            self.assertIn(arm, mgr.DECLARED_GAP)
        self.assertNotIn("(5)", mgr.DECLARED_GAP)

    def test_the_docstring_says_where_the_floor_is_and_a_caller_reads_it_there(self):
        """The header's claims about round 8, each pinned by an arm above."""
        self.assertIn("ROUND 8 HOOKS THE LOWEST PYTHON-VISIBLE LAYER", mgr.__doc__)
        self.assertIn("THE PUBLIC HOOKS ARE KEPT AND THE FLOOR DOES NOT SCAN TWICE", mgr.__doc__)
        self.assertIn("`multiprocessing.set_executable` IS NOT ADVERSARIAL", mgr.__doc__)
        self.assertIn("`_FORK_EXEC_BINDINGS`", mgr.__doc__)
        self.assertIn("`LAUNCH_REASON_KERNEL_FLOOR`", mgr.__doc__)
        # The superseded sentence, gone from the header as well as from the record.
        self.assertNotIn("guarded by the shim on `PYTHONPATH` and by these hooks in turn. All four",
                         mgr.__doc__)


class TheApprovalIsBoundToTheFileAndNotOnlyToTheArgv(Round8Fixture):
    """ROUND 9: the ticket round 8 introduced was keyed on the ARGV, and the argv is not the file.

    THE FINDING VERBATIM: "`_ApprovedLaunch` is keyed on the ARGV ALONE. Round 8's whole finding was
    that the argv is not the executable. So while an approval is outstanding, any code that runs IN
    THAT THREAD during the window can call `_posixsubprocess.fork_exec` with the SAME argv but a
    DIFFERENT executable_list and the floor will consume the ticket and skip the scan. The ticket's
    own docstring claims the opposite. For a different thread that is true (the stack is
    thread-local). For a `preexec_fn`, which CPython runs in the forked child between fork and exec
    with the parent's thread-local stack inherited, it is FALSE whenever the argv is the same."

    WHY THE REPRODUCER BELOW USES A `fileno()` AND NOT A `preexec_fn`. `preexec_fn` is now refused
    at the `Popen` hook, before anything is scanned -- so a `preexec_fn` reproducer would measure
    THAT refusal and would pass with the identity fix reverted. The window is not specific to
    `preexec_fn`: it is every piece of caller code CPython runs between the ticket being issued and
    the ticket being spent, and `stdout.fileno()`, called from `Popen._get_handles` inside
    `Popen.__init__`, is the same window reached deterministically and without a fork. A `__del__`
    or a weakref finalizer landing there is the same shape again. So the two halves of the fix get
    one arm each: this class's first arm fails with the identity reverted, and its second fails with
    the `preexec_fn` refusal reverted.

    THE ARGV IS `['ls', '-I', child]`, which is round 7's finding 1 wearing round 8's ticket. It is
    APPROVED, honestly, as the leaf tool `ls` -- `-I` is an `ls` option and `_check_leaf` admits a
    system-prefix `ls`. Handed to `fork_exec` with `executable_list=[sys.executable]` the kernel then
    runs PYTHON with that argv, which is `python -I <hijacking child>`: an isolated interpreter, no
    shim, the wrong tree. The scan would refuse it in a line; the ticket was what stopped the scan
    from running.
    """

    #: The malicious argv, spelled once: approvable as `ls`, catastrophic as `python`.
    SPENT_ARGV = "['ls', '-I', CHILD]"

    def test_a_callback_INSIDE_the_window_cannot_spend_the_ticket_on_a_DIFFERENT_FILE(self):
        """THE REPRODUCER. One argv, two files, one ticket -- and the ticket must not match.

        THE OUTER LAUNCH IS THE LEGITIMATE ONE and it is what issues the approval:
        `Popen(['ls', '-I', child], stdout=<object>)`. CPython calls `stdout.fileno()` from
        `_get_handles`, inside `Popen.__init__` -- which is inside this guard's own
        `_approve_launch`/`_withdraw_launch_approval` window, in the same thread, so the approval
        stack is the very one the floor will read. From there the reproducer calls the floor
        directly with the approved argv and `executable_list=[sys.executable]`.

        WHAT PROVES THE FIX IS LOAD-BEARING is that this arm FAILS without it: keyed on the argv
        alone the ticket matches, the floor returns before it parses anything, and the isolated
        interpreter runs -- sentinel present, `HIJACK-LOADED WRONG TREE` on stdout, exit 0, no
        record of a refusal. With the file in the key the two halves disagree, the floor scans, and
        what it scans is a Python interpreter with `-I` in its argv.
        """
        child, sentinel = self.hijacking_child("window_child")
        parent = write(
            self.nd / "parent_window_spends_ticket.py",
            "import os, subprocess, sys, _posixsubprocess\n"
            "EXE = sys.executable\n"
            f"CHILD = {str(child)!r}\n"
            f"ARGV = {self.SPENT_ARGV}\n"
            "\n"
            "class SpendsTheTicket:\n"
            "    #: Reached from Popen._get_handles, INSIDE Popen.__init__, with the approval for\n"
            "    #: ARGV outstanding on this thread's stack.\n"
            "    def fileno(self):\n"
            "        env_list = [os.fsencode(k) + b'=' + os.fsencode(v)\n"
            "                    for k, v in os.environ.items()]\n"
            "        errpipe_read, errpipe_write = os.pipe()\n"
            "        argv = ARGV\n"
            "        pid = _posixsubprocess.fork_exec(\n"
            + self.FORK_EXEC_CALL +
            "        os.close(errpipe_write)\n"
            "        os.close(errpipe_read)\n"
            "        _, status = os.waitpid(pid, 0)\n"
            "        print('TICKET-SPENT', os.waitstatus_to_exitcode(status))\n"
            "        return os.open(os.devnull, os.O_WRONLY)\n"
            "\n"
            "proc = subprocess.Popen(ARGV, stdout=SpendsTheTicket())\n"
            "proc.wait()\n"
            "print('OUTER-EXIT', proc.returncode)\n")
        result = self.guarded(parent)
        self.assertNotIn("TICKET-SPENT", result.stdout,
                         "the floor consumed the approval and launched a file the approval was "
                         "not issued for -- this is the finding, not a refusal")
        self.assertNotIn("OUTER-EXIT", result.stdout,
                         "the parent got past the call, so nothing was refused")
        record = self.assertRefusedStatically(result, sentinel, mgr.LAUNCH_REASON_FLAGS, "-I")
        self.assertEqual(record["launch_refusal"]["executable"],
                         os.path.realpath(sys.executable),
                         "the refusal names a file other than the one the kernel would have run, "
                         "so the floor scanned argv[0] rather than the executable_list")

    def test_the_SAME_argv_through_the_SAME_route_is_ADMITTED_when_the_FILE_matches(self):
        """The direction that makes the arm above an identity check and not an `ls` ban.

        WITHOUT THIS ARM the reproducer above would also pass against a guard that had simply
        stopped issuing tickets, or one that refused every `ls` with a `-I` in it. Here the outer
        launch is the same `Popen(['ls', '-I', child], stdout=<object>)` and the callback inside the
        window calls the floor with the argv AND the file the approval was issued for -- `ls`, found
        the way the child would find it, on the child's own PATH. That must be waved through: it is
        the launch the layer above already read.
        """
        child, sentinel = self.hijacking_child("window_match_child")
        parent = write(
            self.nd / "parent_window_matching_file.py",
            "import os, shutil, subprocess, sys, _posixsubprocess\n"
            "EXE = sys.executable\n"
            f"CHILD = {str(child)!r}\n"
            f"ARGV = {self.SPENT_ARGV}\n"
            "#: THE CHILD'S OWN PATH, wrapper directories included -- which is how the layer below\n"
            "#: resolves a bare name, and therefore what the approval was keyed on.\n"
            "LS = shutil.which('ls')\n"
            "\n"
            "class SpendsTheTicket:\n"
            "    def fileno(self):\n"
            "        env_list = [os.fsencode(k) + b'=' + os.fsencode(v)\n"
            "                    for k, v in os.environ.items()]\n"
            "        errpipe_read, errpipe_write = os.pipe()\n"
            "        argv = ARGV\n"
            "        pid = _posixsubprocess.fork_exec(\n"
            "            argv, [os.fsencode(LS)], True, (errpipe_write,), None, env_list,\n"
            "            -1, -1, -1, -1, -1, -1, errpipe_read, errpipe_write,\n"
            "            False, False, -1, None, None, None, -1, None, False)\n"
            "        os.close(errpipe_write)\n"
            "        os.close(errpipe_read)\n"
            "        os.waitpid(pid, 0)\n"
            "        print('MATCHING-FILE-RAN')\n"
            "        return os.open(os.devnull, os.O_WRONLY)\n"
            "\n"
            "proc = subprocess.Popen(ARGV, stdout=SpendsTheTicket())\n"
            "proc.wait()\n"
            "print('OUTER-EXIT', proc.returncode)\n")
        result = self.guarded(parent)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("MATCHING-FILE-RAN", result.stdout, result.stdout + result.stderr)
        self.assertNotIn("[oi136 launch]", result.stderr)
        self.assertNotIn("HIJACK-LOADED", result.stdout)
        self.assertFalse(sentinel.exists(),
                         "the hijacking child ran, so `ls` was not what the kernel was given")
        self.assertIsNone(self.records()[0]["launch_refusal"], self.records()[0])

    # ---- the construct itself: `preexec_fn` -------------------------------------------------

    def test_preexec_fn_is_REFUSED_AT_THE_POPEN_HOOK_with_its_own_reason(self):
        """`subprocess.run(..., preexec_fn=f)`: refused, and `f` never runs.

        THE SENTINEL IS WRITTEN BY `f` ITSELF, which is what makes this an assertion about the
        construct rather than about the child. `preexec_fn` runs in the forked child between `fork`
        and `exec`, so a sentinel it writes exists if and only if the fork happened -- and it must
        not. The child here is the CLEAN child, admitted by every other arm in this file, so the
        refusal cannot be attributed to anything the child is.
        """
        clean = self.clean_child("preexec_clean_child")
        forked = self.tmp / "preexec-fn-ran"
        parent = write(
            self.nd / "parent_preexec_refused.py",
            "import pathlib, subprocess, sys\n"
            "def before_exec():\n"
            f"    pathlib.Path({str(forked)!r}).write_text('ran')\n"
            f"code = subprocess.run([sys.executable, {str(clean)!r}],\n"
            "                       preexec_fn=before_exec).returncode\n"
            "print('PREEXEC-EXIT', code)\n")
        result = self.guarded(parent)
        self.assertNotIn("PREEXEC-EXIT", result.stdout,
                         "the launch returned, so preexec_fn was not refused")
        record = self.assertRefusedStatically(result, forked, mgr.LAUNCH_REASON_PREEXEC,
                                              "preexec_fn")
        self.assertNotIn("CHILD-LOADED", result.stdout)
        self.assertEqual(record["outcome"], mgr.launch_outcome(record["launch_refusal"]))
        self.assertEqual(record["launch_refusal"]["executable"],
                         mgr._resolve_executable(sys.executable, None),
                         "the refusal does not name the file the launch would have run")

    def test_THE_SAME_LAUNCH_WITHOUT_preexec_fn_STILL_RUNS(self):
        """The direction the refusal above acts in, measured: `preexec_fn` is the whole difference.

        A one-directional check waves the other way through, and here the other way is a guard that
        had started refusing `subprocess.run([python, child])` outright -- which would pass the arm
        above for a reason that has nothing to do with `preexec_fn`. Same parent, same child, the
        keyword removed: admitted, with a record from a second interpreter that installed the guard.
        """
        clean = self.clean_child("preexec_control_child")
        parent = write(
            self.nd / "parent_preexec_control.py",
            "import subprocess, sys\n"
            f"code = subprocess.run([sys.executable, {str(clean)!r}]).returncode\n"
            "print('ARM-EXIT', code)\n")
        self.assertAdmittedWithAGuardedChild(self.guarded(parent), "ARM-EXIT 0")

    def test_NO_non_test_FILE_IN_THIS_REPOSITORY_passes_preexec_fn(self):
        """The census the refusal was priced against, run rather than remembered.

        WHY IT IS A TEST AND NOT A SENTENCE IN A COMMIT MESSAGE. "Refusing this costs nothing"
        is a claim about the tree, and a claim about the tree measured once decays -- a launcher
        added next month makes the refusal a false refusal, and the only place that would surface
        is here. `git grep` over `*.py` searches TRACKED files, which is the population the claim
        is about.

        THE POSITIVE CONTROL IS THE GUARD'S OWN HITS. A search that matched nothing at all would
        satisfy "no caller" vacuously -- an inference from absence needs a covering search -- so
        the module that discusses and refuses `preexec_fn` must be among the hits, and the arm is
        red if it is not.
        """
        found = subprocess.run(["git", "grep", "-n", "preexec_fn", "--", "*.py"],
                               cwd=REPO, capture_output=True, text=True)
        self.assertIn(found.returncode, (0, 1), found.stderr)
        hits = [line for line in found.stdout.splitlines() if line.strip()]
        self.assertTrue([line for line in hits
                         if line.startswith("nd-unfolding/mnv_guarded_run.py:")],
                        f"the guard's own mentions of preexec_fn are not in the census, so the "
                        f"search covers something other than this tree: {hits}")
        callers = [line for line in hits
                   if not line.startswith("nd-unfolding/mnv_guarded_run.py:")
                   and "/tests/" not in line.split(":", 1)[0]]
        self.assertEqual(callers, [],
                         "a non-test file passes preexec_fn, so LAUNCH_REASON_PREEXEC is now a "
                         "FALSE REFUSAL of a real launcher: fix the launcher (cwd=/env=/"
                         "start_new_session=/pass_fds= all reach this layer) rather than the guard")

    # ---- the silent direction: what the ticket must STILL wave through ----------------------

    #: EVERY SPELLING WHOSE TICKET IS CONSUMED ONE LAYER DOWN, and each takes a different route to
    #: the consume site: `close_fds=False` sends `Popen` to `os.posix_spawn` instead of `fork_exec`,
    #: the BARE NAME is the one whose file the two sides have to resolve identically (see
    #: `_launch_file_identity` -- resolved the scan's way at one end and the producer's way at the
    #: other, they name two different files and the floor re-scans its own layer's repair), and
    #: `os.system` issues its approval around a call to the ORIGINAL `Popen.__init__`.
    STILL_ADMITTED = {
        "shell=True through fork_exec":
            "code = subprocess.run('ls victim.py', shell=True, cwd=ND).returncode",
        "shell=True through os.posix_spawn":
            "code = subprocess.run('ls victim.py', shell=True, cwd=ND, "
            "close_fds=False).returncode",
        "a BARE NAME with no shell":
            "code = subprocess.run(['ls', 'victim.py'], cwd=ND).returncode",
        "os.system":
            "os.chdir(ND); code = os.system('ls victim.py')",
    }

    def test_the_launches_THIS_GUARD_ALREADY_READ_are_still_waved_through_at_the_floor(self):
        """Four routes to the consume site, and a ticket that stopped matching refuses all four.

        THIS IS THE POWER ARM FOR THE IDENTITY. An identity whose two sides disagree is invisible in
        every refusal arm above -- a mismatch only ever causes the floor to scan MORE -- and what it
        breaks is exactly this: a launch the layer above rewrote, re-read one layer down against the
        restricted `PATH` its own rewrite carries. `subprocess.run("ls", shell=True,
        close_fds=False)` is the spelling that was live before round 8 and the one round 8 fixed;
        the bare-name row is the one round 9's change would have broken.
        """
        for name, call in self.STILL_ADMITTED.items():
            with self.subTest(spelling=name):
                self.inventory.unlink(missing_ok=True)
                parent = write(
                    self.nd / f"parent_admitted_{abs(hash(name)) % 100000}.py",
                    "import os, subprocess\n"
                    f"ND = {str(self.nd)!r}\n"
                    f"{call}\n"
                    "print('ADMITTED-EXIT', code)\n")
                result = self.guarded(parent)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("ADMITTED-EXIT 0", result.stdout, result.stdout + result.stderr)
                self.assertIn("victim.py", result.stdout,
                              "`ls` printed nothing, so this row exited 0 without running")
                self.assertNotIn("[oi136 launch]", result.stderr)
                self.assertIsNone(self.records()[0]["launch_refusal"], self.records()[0])

    def test_every_multiprocessing_START_METHOD_and_the_POOL_still_run_a_GUARDED_child(self):
        """The stdlib's own callers of the consume site, re-measured against the new identity.

        `spawn`, `forkserver` and `ProcessPoolExecutor` all reach `fork_exec` through
        `Popen`/`spawnv_passfds` with a ticket outstanding, so each of them spends one on every
        correct run. They are measured HERE as well as in
        `TheKernelFloorIsHookedAndTheResidualIsBelowIt` because a break caused by the identity has
        to be attributable to the identity: an arm that is red in both classes is a broken floor,
        and one that is red only here is a key whose two sides disagree.
        """
        arms = {
            "spawn": "'spawn'",
            "forkserver": "'forkserver'",
        }
        for name, context in arms.items():
            with self.subTest(arm=name):
                self.inventory.unlink(missing_ok=True)
                parent = write(
                    self.nd / f"parent_identity_mp_{name}.py",
                    "import multiprocessing\n"
                    "def work():\n"
                    f"    print('{name.upper()}-CHILD-RAN')\n"
                    "if __name__ == '__main__':\n"
                    f"    proc = multiprocessing.get_context({context}).Process(target=work)\n"
                    "    proc.start()\n"
                    "    proc.join()\n"
                    "    print('ARM-EXIT', proc.exitcode)\n")
                self.assertAdmittedWithAGuardedChild(self.guarded(parent), "ARM-EXIT 0")
        with self.subTest(arm="ProcessPoolExecutor"):
            self.inventory.unlink(missing_ok=True)
            parent = write(
                self.nd / "parent_identity_mp_pool.py",
                "import concurrent.futures, multiprocessing\n"
                "def work(value):\n"
                "    return value * 2\n"
                "if __name__ == '__main__':\n"
                "    ctx = multiprocessing.get_context('spawn')\n"
                "    with concurrent.futures.ProcessPoolExecutor(max_workers=1,\n"
                "            mp_context=ctx) as pool:\n"
                "        print('POOL-RESULT', pool.submit(work, 21).result())\n"
                "    print('ARM-EXIT 0')\n")
            self.assertAdmittedWithAGuardedChild(self.guarded(parent), "ARM-EXIT 0")

    # ---- the docstring, which was the thing that was FALSE ----------------------------------

    def test_the_ticket_DOCSTRING_no_longer_claims_a_preexec_fn_DOES_NOT_MATCH(self):
        """The superseded sentence is GONE, and what replaced it says what the code does.

        THE DOCSTRING WAS THE DEFECT'S COVER. It asserted that "a lower layer launching something
        ELSE while an approval is outstanding -- a `preexec_fn` in the forked child, a thread that
        never went through the public hook -- does not match and is scanned", which was true of the
        thread half (the stack is thread-local) and false of the `preexec_fn` half whenever the argv
        was the same. A reviewer reading the ticket had no reason to look. So the sentence is
        asserted ABSENT rather than merely improved, and the replacement claims are pinned to the
        arms above.
        """
        doc = mgr._ApprovedLaunch.__doc__
        self.assertNotIn("a `preexec_fn` in the forked child", doc)
        self.assertNotIn("does not match and is scanned. It is per-thread", doc)
        self.assertIn("THE IDENTITY IS (ARGV, FILE) AND NOT THE ARGV", doc)
        self.assertIn("LAUNCH_REASON_PREEXEC", doc)
        self.assertIn("IT IS PER-THREAD", doc, "the thread half of the claim was TRUE and is lost")
        self.assertIn("_launch_file_identity", doc)
        # And the header carries the same correction, for a reader who never opens the class.
        self.assertIn("THE TICKET IS KEYED ON (ARGV, FILE)", mgr.__doc__)


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
