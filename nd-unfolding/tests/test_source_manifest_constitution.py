#!/usr/bin/env python3
"""A-2(c)(d)(e)(g): the code-root constitution checks, and proof they can both fire and stay quiet.

Joseph, 2026-08-22 round 3: *"A-2(d), (e), and (g) may not remain merely documented. Before Gate 1,
add fail-closed checks rejecting a nested checkout, a code root nested inside another checkout, and
a writable code root; apply and verify write protection."*

THE SILENT ARMS MATTER AS MUCH AS THE FIRING ONES, and they are the reason this file is long.
Three new fail-closed checks sitting on the execution path are three new ways to block a run that
was fine. Every check below therefore gets both: a fixture where it MUST refuse, and a legitimate
clean code root where it MUST NOT -- including one arm that turns on all four requirements at once
against a tree that satisfies them, because checks can interact even when each is right alone.

(d) AND (e) ARE THE SAME HAZARD FROM OPPOSITE SIDES. `checkout_root_of` returns the INNERMOST
matching ancestor, deliberately, so a frozen deployment inside another directory resolves to itself.
The consequence is that a checkout nested INSIDE the code root resolves to ITSELF -- which is not
`--expect-root` -- so every module under it is refused on a tree the operator believes is approved.
The contract's A-2 records the realised instance: a peer's live `.claude/worktrees/` audit checkout
made the OI-136 ratchet read 369 instead of the recorded 58.
"""
import json
import os
import pathlib
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
ND = HERE.parent
TOOL = ND / "mnv_source_manifest.py"

sys.path.insert(0, str(ND))
import mnv_guarded_run as mgr          # noqa: E402
import mnv_source_manifest as msm      # noqa: E402

CANNOT_CHECK = 2


def git(repo, *args):
    env = dict(os.environ, GIT_AUTHOR_NAME="f", GIT_AUTHOR_EMAIL="f@f",
               GIT_COMMITTER_NAME="f", GIT_COMMITTER_EMAIL="f@f")
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, env=env)
    if r.returncode != 0:
        raise AssertionError(f"git {args} failed in {repo}: {r.stdout}{r.stderr}")
    return r.stdout


def make_checkout(root: pathlib.Path) -> pathlib.Path:
    """A directory the OI-136 guard would call a checkout: BOTH markers, never one."""
    (root / "nd-unfolding").mkdir(parents=True, exist_ok=True)
    (root / "VALIDATION_LEDGER.md").write_text("# fixture ledger\n")
    return root


def chmod_tree(root: pathlib.Path, writable: bool):
    """Apply or undo A-2(g) over the SOURCE, never over `.git`.

    `.git` is excluded because git must keep writing there -- `git status` refreshes its stat cache
    -- and a protection that breaks the tools which verify it protects nothing.
    """
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for name in filenames:
            f = pathlib.Path(dirpath) / name
            m = stat.S_IMODE(os.stat(f).st_mode)
            os.chmod(f, m | 0o200 if writable else m & ~0o222)
        if pathlib.Path(dirpath) != root:
            m = stat.S_IMODE(os.stat(dirpath).st_mode)
            os.chmod(dirpath, m | 0o200 if writable else m & ~0o222)


class Fixture(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.mkdtemp(dir="/private/tmp" if os.path.isdir("/private/tmp") else None)
        self.tmp = pathlib.Path(self._tmp)
        # Cleanup must run even after a read-only arm, or the whole suite leaks temp trees.
        self.addCleanup(self._cleanup)
        self.code = make_checkout(self.tmp / "code-root")
        (self.code / "nd-unfolding" / "mod.py").write_text("MARK = 1\n")
        (self.code / "run.sh").write_text("echo hi\n")
        git(self.code, "init", "-q")
        git(self.code, "add", "-A")
        git(self.code, "commit", "-qm", "fixture")

    def _cleanup(self):
        chmod_tree(self.tmp, writable=True)
        shutil.rmtree(self._tmp, ignore_errors=True)

    def run_tool(self, *args, repo=None):
        """Status captured UNPIPED into a variable before anything reads it."""
        cp = subprocess.run([sys.executable, str(TOOL), "--repo", str(repo or self.code), *args],
                            capture_output=True, text=True)
        return cp

    ALL = ("--require-checkout", "--require-no-nested-checkout",
           "--require-not-nested", "--require-readonly")


class TheDefinitionOfCheckoutIsNotRestated(Fixture):
    def test_the_tool_IMPORTS_the_guards_markers_rather_than_copying_them(self):
        """A second copy would drift the first time either moved -- which is how `AGENTS.md`
        became the wrong marker for trees frozen before it was rewritten."""
        self.assertIs(msm.MARKERS, mgr.MARKERS)
        self.assertIs(msm.is_checkout, mgr.is_checkout)
        self.assertEqual(msm.MARKERS, ("VALIDATION_LEDGER.md", "nd-unfolding"))


class D_NestedCheckoutBeneathTheCodeRoot(Fixture):
    def test_it_FIRES_on_a_nested_checkout_and_names_it(self):
        make_checkout(self.code / "frozen-inner")
        cp = self.run_tool("--write", os.devnull, "--require-no-nested-checkout")
        self.assertEqual(cp.returncode, CANNOT_CHECK, cp.stdout + cp.stderr)
        self.assertIn("A-2(d)", cp.stderr)
        self.assertIn("frozen-inner", cp.stderr)

    def test_it_FIRES_on_the_RECORDED_instance_a_worktree_under_dot_claude(self):
        """The named realisation, not a hypothetical: `.claude/worktrees/<name>` is where a peer's
        live audit checkout made the OI-136 ratchet read 369 instead of 58."""
        make_checkout(self.code / ".claude" / "worktrees" / "lane-c")
        cp = self.run_tool("--write", os.devnull, "--require-no-nested-checkout")
        self.assertEqual(cp.returncode, CANNOT_CHECK, cp.stdout + cp.stderr)
        self.assertIn(".claude/worktrees/lane-c", cp.stderr)

    def test_the_INNERMOST_semantics_this_protects_are_real(self):
        """Not a claim about the checker -- a claim about the guard, measured on the guard."""
        inner = make_checkout(self.code / "frozen-inner")
        mod = inner / "nd-unfolding" / "m.py"
        mod.write_text("\n")
        self.assertEqual(mgr.checkout_root_of(str(mod), _cache={}), str(inner))
        self.assertNotEqual(mgr.checkout_root_of(str(mod), _cache={}), str(self.code))

    def test_it_is_SILENT_on_a_clean_code_root(self):
        cp = self.run_tool("--write", os.devnull, "--require-no-nested-checkout")
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)

    def test_a_HALF_marked_directory_is_not_a_nested_checkout(self):
        """`is_checkout` is conjunctive. A directory holding only `nd-unfolding/` -- which every
        deployment has -- must not read as a nested checkout, or this check fires on everything."""
        (self.code / "products" / "nd-unfolding").mkdir(parents=True)
        cp = self.run_tool("--write", os.devnull, "--require-no-nested-checkout")
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)

    def test_dot_git_is_pruned_and_that_prune_cannot_hide_a_real_nest(self):
        cp = self.run_tool("--write", os.devnull, "--require-no-nested-checkout")
        self.assertEqual(cp.returncode, 0, cp.stderr)
        self.assertEqual(msm.PRUNE_DIRS, (".git", "__pycache__"))
        make_checkout(self.code / "sub" / "deep" / "nest")
        self.assertIn("sub/deep/nest", msm.nested_checkouts(str(self.code)))


class E_TheCodeRootInsideAnotherCheckout(Fixture):
    def test_it_FIRES_and_names_the_enclosing_tree(self):
        outer = make_checkout(self.tmp / "outer")
        inner = make_checkout(outer / "inner-code-root")
        (inner / "nd-unfolding" / "mod.py").write_text("MARK = 1\n")
        git(inner, "init", "-q")
        git(inner, "add", "-A")
        git(inner, "commit", "-qm", "fixture")
        cp = self.run_tool("--write", os.devnull, "--require-not-nested", repo=inner)
        self.assertEqual(cp.returncode, CANNOT_CHECK, cp.stdout + cp.stderr)
        self.assertIn("A-2(e)", cp.stderr)
        self.assertIn(str(outer), cp.stderr)

    def test_it_is_SILENT_on_a_code_root_that_is_not_nested(self):
        cp = self.run_tool("--write", os.devnull, "--require-not-nested")
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)

    def test_a_non_checkout_parent_directory_does_NOT_count(self):
        """Living under `/pscratch/sd/j/josephrb/` is not "nested inside a checkout"."""
        plain = self.tmp / "plain-parent"
        plain.mkdir()
        moved = make_checkout(plain / "code")
        (moved / "nd-unfolding" / "mod.py").write_text("MARK = 1\n")
        git(moved, "init", "-q")
        git(moved, "add", "-A")
        git(moved, "commit", "-qm", "f")
        cp = self.run_tool("--write", os.devnull, "--require-not-nested", repo=moved)
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)


class G_WriteProtection(Fixture):
    def test_it_FIRES_on_a_writable_source_tree_and_says_how_to_fix_it(self):
        cp = self.run_tool("--write", os.devnull, "--require-readonly")
        self.assertEqual(cp.returncode, CANNOT_CHECK, cp.stdout + cp.stderr)
        self.assertIn("A-2(g)", cp.stderr)
        self.assertIn("chmod a-w", cp.stderr)

    def test_it_is_SILENT_once_protection_is_APPLIED(self):
        chmod_tree(self.code, writable=False)
        cp = self.run_tool("--write", os.devnull, "--require-readonly")
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)

    def test_ONE_writable_file_is_enough_to_refuse(self):
        """The direction that matters: protection is not 'mostly applied'."""
        chmod_tree(self.code, writable=False)
        target = self.code / "nd-unfolding" / "mod.py"
        os.chmod(target, stat.S_IMODE(os.stat(target).st_mode) | 0o200)
        cp = self.run_tool("--write", os.devnull, "--require-readonly")
        self.assertEqual(cp.returncode, CANNOT_CHECK, cp.stdout + cp.stderr)
        self.assertIn("nd-unfolding/mod.py", cp.stderr)

    def test_a_writable_DIRECTORY_is_refused_even_when_every_file_is_read_only(self):
        """Write on a directory permits replacing a read-only file by unlink-and-create, so file
        bits alone are not the property A-2(g) is after."""
        chmod_tree(self.code, writable=False)
        d = self.code / "nd-unfolding"
        os.chmod(d, stat.S_IMODE(os.stat(d).st_mode) | 0o200)
        cp = self.run_tool("--write", os.devnull, "--require-readonly")
        self.assertEqual(cp.returncode, CANNOT_CHECK, cp.stdout + cp.stderr)
        self.assertIn("nd-unfolding/", cp.stderr)

    def test_the_two_definitions_of_writable_are_BOTH_recorded_and_only_one_is_enforced(self):
        """`mode_writable` is a property of the TREE and is enforced; `uid_writable` is a property
        of WHO IS ASKING and is reported. Enforcing the uid form alone would pass a tree any other
        account can rewrite mid-run, and would pass anything at all for root."""
        chmod_tree(self.code, writable=False)
        out = self.tmp / "m.json"
        cp = self.run_tool("--write", str(out))
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        con = json.loads(out.read_text())["constitution"]
        self.assertEqual(con["mode_writable"], [])
        self.assertIn("uid_writable", con)
        self.assertIsInstance(con["uid_writable"], list)

    def test_git_keeps_working_after_protection_is_applied(self):
        """The check must not describe a state that breaks the tools which verify it: `.git` stays
        writable, so `git ls-files` and `git status` still answer."""
        chmod_tree(self.code, writable=False)
        self.assertIn("nd-unfolding/mod.py", git(self.code, "ls-files"))
        self.assertEqual(git(self.code, "status", "--porcelain").strip(), "")


class TheConstitutionIsRecordedWhetherOrNotItWasREQUIRED(Fixture):
    def test_the_manifest_carries_all_four_findings_with_no_flag_passed(self):
        """P-3's rule applied to this record: an absent key cannot distinguish 'there was no nested
        checkout' from 'nobody looked', and this file is read later by people who did not run it."""
        make_checkout(self.code / "frozen-inner")
        out = self.tmp / "m.json"
        cp = self.run_tool("--write", str(out))
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        con = json.loads(out.read_text())["constitution"]
        for key in ("is_checkout", "markers", "nested_checkouts", "enclosing_checkout",
                    "mode_writable", "uid_writable"):
            self.assertIn(key, con)
        self.assertEqual(con["nested_checkouts"], ["frozen-inner"])
        self.assertTrue(con["is_checkout"])


class C_ItMustLookLikeACheckoutToTheGuard(Fixture):
    def test_it_FIRES_when_a_marker_is_missing(self):
        (self.code / "VALIDATION_LEDGER.md").unlink()
        git(self.code, "add", "-A")
        git(self.code, "commit", "-qm", "drop marker")
        cp = self.run_tool("--write", os.devnull, "--require-checkout")
        self.assertEqual(cp.returncode, CANNOT_CHECK, cp.stdout + cp.stderr)
        self.assertIn("A-2(c)", cp.stderr)

    def test_it_is_SILENT_on_a_real_checkout(self):
        cp = self.run_tool("--write", os.devnull, "--require-checkout")
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)


class ALL_FOUR_TOGETHER_ON_A_LEGITIMATE_ROOT(Fixture):
    """The arm that answers 'three new fail-closed checks are three new ways to block an innocent
    run'. Checks can interact even when each is correct alone, so they are exercised together."""

    def test_a_clean_protected_unnested_checkout_passes_EVERY_requirement_at_once(self):
        chmod_tree(self.code, writable=False)
        cp = self.run_tool("--write", os.devnull, "--require-clean", *self.ALL)
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)

    def test_and_the_same_tree_fails_each_requirement_when_that_one_thing_is_broken(self):
        """Power, one variable at a time: same fixture, one mutation each, four refusals."""
        chmod_tree(self.code, writable=False)
        base = ("--write", os.devnull, "--require-clean", *self.ALL)
        self.assertEqual(self.run_tool(*base).returncode, 0)

        chmod_tree(self.code, writable=True)
        self.assertEqual(self.run_tool(*base).returncode, CANNOT_CHECK, "g")
        chmod_tree(self.code, writable=False)

        make_checkout(self.code / "nested")
        self.assertEqual(self.run_tool(*base).returncode, CANNOT_CHECK, "d")
        shutil.rmtree(self.code / "nested")

        chmod_tree(self.code, writable=True)
        (self.code / "nd-unfolding" / "dirty.py").write_text("x = 1\n")
        git(self.code, "add", "-A")
        self.assertEqual(self.run_tool(*base).returncode, CANNOT_CHECK, "b")


if __name__ == "__main__":
    unittest.main(verbosity=2)
