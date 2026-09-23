"""KNOWN_ISSUES row 60: checks whose green must map to an object.

Hermetic: the real `generate_manifest.py`, `live_doc_indexed.py` and `lib/tree_state.py` are
copied into a throwaway git repository, so an unstaged edit, a staged doc and a missing overrides
row can be manufactured without touching any shared checkout.

  (1) `generate_manifest.py --at-sha HEAD` is a function of the commit: an unstaged (and a staged)
      edit leaves its output byte-identical, while the working-tree mode moves -- both directions.
  (2) the `--check` verdict is the LAST stdout line and carries `exit=` and the object, so a pipe
      into `tail -1` still shows it.
  (3) `live_doc_indexed.py` fires on a newly added doc with NO overrides row, is silent once any
      row (ARCHIVAL) exists, and `--unrowed` lists the whole-tree set and exits 1.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ORCH = "docs/orchestration"
HDR = "path\tclass\tevent_status\tcanonical_successor\n"


def git(cwd, *args):
    return subprocess.run(["git", "-c", "core.hooksPath=/dev/null", "-c", "user.name=t",
                           "-c", "user.email=t@t", *args],
                          cwd=cwd, capture_output=True, text=True, check=True).stdout


class ObjectIdentityChecks(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="object-identity-"))
        (self.tmp / ORCH).mkdir(parents=True)
        (self.tmp / "lib").mkdir()
        for rel in (f"{ORCH}/generate_manifest.py", f"{ORCH}/live_doc_indexed.py",
                    "lib/tree_state.py"):
            shutil.copy2(REPO / rel, self.tmp / rel)
        (self.tmp / ORCH / "MANIFEST-overrides.tsv").write_text(
            HDR + f"{ORCH}/CATALOG.md\tLIVE\topen\t\n{ORCH}/A.md\tLIVE\topen\t\n")
        (self.tmp / ORCH / "CATALOG.md").write_text("# router\n- [`A.md`](A.md)\n")
        (self.tmp / ORCH / "A.md").write_text("alpha, see CATALOG.md\n")
        (self.tmp / ORCH / "B-unrowed.md").write_text("beta\n")
        (self.tmp / ".gitignore").write_text("__pycache__/\n")   # as the real repo's .gitignore
        git(self.tmp, "init", "-q")
        git(self.tmp, "add", ".")
        git(self.tmp, "commit", "-q", "-m", "base")
        self.manifest()                                  # worktree mode writes MANIFEST.tsv
        git(self.tmp, "add", f"{ORCH}/MANIFEST.tsv")
        git(self.tmp, "commit", "-q", "-m", "manifest")

    def tearDown(self):
        shutil.rmtree(self.tmp, True)

    def run_py(self, script, *args):
        return subprocess.run([sys.executable, str(self.tmp / ORCH / script), *args],
                              cwd=self.tmp, capture_output=True, text=True,
                              env={k: v for k, v in os.environ.items()
                                   if not k.startswith("GIT_")})

    def manifest(self, *args):
        return self.run_py("generate_manifest.py", *args)

    # ---- (1) + (2) ------------------------------------------------------------------------
    def test_at_sha_output_does_not_move_with_an_unstaged_or_staged_edit(self):
        before = self.manifest("--at-sha", "HEAD")
        self.assertEqual(before.returncode, 0, before.stderr)
        self.assertEqual(before.stdout, (self.tmp / ORCH / "MANIFEST.tsv").read_text())
        (self.tmp / ORCH / "A.md").write_text("alpha, edited and much longer than before\n")
        unstaged = self.manifest("--at-sha", "HEAD")
        self.assertEqual(unstaged.stdout, before.stdout)
        git(self.tmp, "add", f"{ORCH}/A.md")
        staged = self.manifest("--at-sha", "HEAD")
        self.assertEqual(staged.stdout, before.stdout)
        # the direction that makes the above meaningful: the working-tree mode DOES move
        self.assertEqual(self.manifest("--check", "--committed-only").returncode, 1)
        self.assertEqual(self.manifest("--at-sha", "HEAD", "--check").returncode, 0)

    def test_at_sha_never_writes_the_working_tree(self):
        target = self.tmp / ORCH / "MANIFEST.tsv"
        target.write_text("scribbled\n")
        self.manifest("--at-sha", "HEAD")
        self.assertEqual(target.read_text(), "scribbled\n")

    def test_the_verdict_is_the_last_stdout_line_with_exit_and_object(self):
        head = git(self.tmp, "rev-parse", "HEAD").strip()
        ok = self.manifest("--at-sha", "HEAD", "--check")
        self.assertEqual(ok.stdout.splitlines()[-1],
                         f"MANIFEST-CHECK :: OK exit=0 :: head={head} "
                         f"tree=at-sha(working tree not read) scope=.")
        (self.tmp / ORCH / "A.md").write_text("alpha, edited\n")
        bad = self.manifest("--check", "--committed-only")
        self.assertEqual(bad.returncode, 1)
        last = bad.stdout.splitlines()[-1]
        self.assertTrue(last.startswith("MANIFEST-CHECK :: OUT OF DATE exit=1 :: "
                                        f"head={head} tree=dirty(tracked=1,"), last)

    def test_an_unresolvable_rev_is_exit_2_not_a_verdict(self):
        r = self.manifest("--at-sha", "no-such-rev", "--check")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)

    # ---- (3) ------------------------------------------------------------------------------
    def test_a_newly_added_doc_with_no_overrides_row_fires(self):
        (self.tmp / ORCH / "C-new.md").write_text("gamma\n")
        git(self.tmp, "add", f"{ORCH}/C-new.md")
        r = self.run_py("live_doc_indexed.py", "--check")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("NO row", r.stdout)
        self.assertIn(f"{ORCH}/C-new.md", r.stdout)

    def test_the_same_doc_with_an_archival_row_passes(self):
        (self.tmp / ORCH / "C-new.md").write_text("gamma\n")
        ov = self.tmp / ORCH / "MANIFEST-overrides.tsv"
        ov.write_text(ov.read_text() + f"{ORCH}/C-new.md\tARCHIVAL\tterminal\t\n")
        git(self.tmp, "add", f"{ORCH}/C-new.md", f"{ORCH}/MANIFEST-overrides.tsv")
        r = self.run_py("live_doc_indexed.py", "--check")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("1 tracked doc(s) have NO overrides row", r.stdout)   # B-unrowed.md

    def test_unrowed_lists_the_whole_tree_and_exits_1(self):
        r = self.run_py("live_doc_indexed.py", "--unrowed")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn(f"{ORCH}/B-unrowed.md", r.stdout)
        self.assertNotIn(f"{ORCH}/A.md", r.stdout)
        ov = self.tmp / ORCH / "MANIFEST-overrides.tsv"
        ov.write_text(ov.read_text() + f"{ORCH}/B-unrowed.md\tARCHIVAL\tterminal\t\n")
        git(self.tmp, "add", f"{ORCH}/MANIFEST-overrides.tsv")
        self.assertEqual(self.run_py("live_doc_indexed.py", "--unrowed").returncode, 0)

    # ---- the shared helper ------------------------------------------------------------------
    def test_tree_state_names_clean_dirty_and_no_git(self):
        spec = __import__("importlib.util").util.spec_from_file_location(
            "tree_state_under_test", self.tmp / "lib" / "tree_state.py")
        ts = __import__("importlib.util").util.module_from_spec(spec)
        spec.loader.exec_module(ts)
        head = git(self.tmp, "rev-parse", "HEAD").strip()
        self.assertEqual(ts.format_state(ts.describe(self.tmp)), f"head={head} tree=clean scope=.")
        (self.tmp / ORCH / "A.md").write_text("edited\n")
        (self.tmp / "untracked.txt").write_text("x\n")
        self.assertEqual(ts.format_state(ts.describe(self.tmp)),
                         f"head={head} tree=dirty(tracked=1,untracked=1) scope=.")
        self.assertEqual(ts.format_state(ts.describe(self.tmp, "lib")),
                         f"head={head} tree=clean scope=lib")
        outside = Path(tempfile.mkdtemp(prefix="no-git-"))
        try:
            self.assertEqual(ts.describe(outside)["tree"], "no-git")
        finally:
            shutil.rmtree(outside, True)


if __name__ == "__main__":
    unittest.main()
