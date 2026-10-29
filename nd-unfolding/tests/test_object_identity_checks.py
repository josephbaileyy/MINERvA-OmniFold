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
  (4) the committed table carries no derived column: editing a record, or adding a record that
      cites it, moves no existing row, while `--query` and `--retention` measure the citation
      count on demand -- an uncited LIVE doc is reported and is silent once something cites it.
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
            HDR + f"{ORCH}/A.md\tLIVE\topen\t\n{ORCH}/CATALOG.md\tLIVE\topen\t\n")
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

    def reclassify_a(self):
        """An unstaged change to a COMMITTED column: A.md's overrides row LIVE -> ARCHIVAL."""
        ov = self.tmp / ORCH / "MANIFEST-overrides.tsv"
        ov.write_text(ov.read_text().replace(f"{ORCH}/A.md\tLIVE\topen", f"{ORCH}/A.md\tARCHIVAL\tterminal"))

    def add_override_row(self, row):
        """Insert at the row's sorted position; the generator refuses an unsorted file."""
        ov = self.tmp / ORCH / "MANIFEST-overrides.tsv"
        header, *rows = ov.read_text().splitlines()
        ov.write_text("\n".join([header] + sorted(rows + [row], key=lambda r: r.split("\t")[0])) + "\n")

    def add_doc(self, name, text, cls="LIVE", status="open"):
        (self.tmp / ORCH / name).write_text(text)
        self.add_override_row(f"{ORCH}/{name}\t{cls}\t{status}\t")
        git(self.tmp, "add", f"{ORCH}/{name}", f"{ORCH}/MANIFEST-overrides.tsv")
        self.assertEqual(self.manifest().returncode, 0)
        git(self.tmp, "add", f"{ORCH}/MANIFEST.tsv")
        git(self.tmp, "commit", "-q", "-m", f"add {name}")

    # ---- (1) + (2) ------------------------------------------------------------------------
    def test_at_sha_output_does_not_move_with_an_unstaged_or_staged_edit(self):
        before = self.manifest("--at-sha", "HEAD")
        self.assertEqual(before.returncode, 0, before.stderr)
        self.assertEqual(before.stdout, (self.tmp / ORCH / "MANIFEST.tsv").read_text())
        self.reclassify_a()
        unstaged = self.manifest("--at-sha", "HEAD")
        self.assertEqual(unstaged.stdout, before.stdout)
        git(self.tmp, "add", f"{ORCH}/MANIFEST-overrides.tsv")
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
        self.reclassify_a()
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
        self.add_override_row(f"{ORCH}/C-new.md\tARCHIVAL\tterminal\t")
        git(self.tmp, "add", f"{ORCH}/C-new.md", f"{ORCH}/MANIFEST-overrides.tsv")
        r = self.run_py("live_doc_indexed.py", "--check")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("1 tracked doc(s) have NO overrides row", r.stdout)   # B-unrowed.md

    def test_unrowed_lists_the_whole_tree_and_exits_1(self):
        r = self.run_py("live_doc_indexed.py", "--unrowed")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn(f"{ORCH}/B-unrowed.md", r.stdout)
        self.assertNotIn(f"{ORCH}/A.md", r.stdout)
        self.add_override_row(f"{ORCH}/B-unrowed.md\tARCHIVAL\tterminal\t")
        git(self.tmp, "add", f"{ORCH}/MANIFEST-overrides.tsv")
        self.assertEqual(self.run_py("live_doc_indexed.py", "--unrowed").returncode, 0)

    # ---- (4) ------------------------------------------------------------------------------
    def test_editing_or_citing_a_record_moves_no_committed_row(self):
        self.assertNotIn("inbound_count", (self.tmp / ORCH / "MANIFEST.tsv").read_text())
        self.add_doc("D.md", "delta\n")
        before = (self.tmp / ORCH / "MANIFEST.tsv").read_text()
        (self.tmp / ORCH / "D.md").write_text("delta, edited and much longer than before\n")
        git(self.tmp, "add", f"{ORCH}/D.md")
        git(self.tmp, "commit", "-q", "-m", "edit D")
        self.assertEqual(self.manifest("--at-sha", "HEAD", "--check").returncode, 0)
        # a new record citing D.md adds exactly its own row and leaves D.md's untouched
        self.add_doc("E.md", "epsilon, cites D.md\n", "ARCHIVAL", "terminal")
        after = (self.tmp / ORCH / "MANIFEST.tsv").read_text()
        self.assertEqual(set(after.splitlines()) - set(before.splitlines()),
                         {f"{ORCH}/E.md\ttracked\tARCHIVAL\tdocument\t\t\tterminal\t\t"
                          "exact-path-only\tyes"})
        self.assertEqual(set(before.splitlines()) - set(after.splitlines()), set())

    def test_query_measures_the_citation_count_on_demand(self):
        self.add_doc("D.md", "delta\n")
        self.add_doc("E.md", "epsilon, cites D.md\n", "ARCHIVAL", "terminal")
        r = self.manifest("--query", f"{ORCH}/D.md", "--at-sha", "HEAD")
        self.assertEqual(r.returncode, 0, r.stderr)
        header, row = r.stdout.splitlines()
        cells = dict(zip(header.split("\t"), row.split("\t")))
        self.assertEqual((cells["inbound_count"], cells["lines"], cells["bytes"]), ("1", "1", "6"))
        self.assertEqual(self.manifest("--query", f"{ORCH}/nope.md").returncode, 2)

    def test_retention_fires_on_an_uncited_live_doc_and_is_silent_once_cited(self):
        self.add_doc("D.md", "delta\n")
        r = self.manifest("--retention", "--at-sha", "HEAD")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(f"uncited LIVE  {ORCH}/D.md", r.stdout)
        self.assertNotIn(f"uncited LIVE  {ORCH}/A.md", r.stdout)     # CATALOG.md cites A.md
        self.add_doc("E.md", "epsilon, cites D.md\n", "ARCHIVAL", "terminal")
        r = self.manifest("--retention", "--at-sha", "HEAD")
        self.assertNotIn(f"uncited LIVE  {ORCH}/D.md", r.stdout)

    def test_an_unsorted_overrides_file_is_refused_and_a_sorted_one_passes(self):
        ov = self.tmp / ORCH / "MANIFEST-overrides.tsv"
        sorted_text = ov.read_text()
        header, *rows = sorted_text.splitlines()
        ov.write_text("\n".join([header] + rows[::-1]) + "\n")          # reverse: out of order
        r = self.manifest("--check", "--committed-only")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("must be sorted by path", r.stderr)
        ov.write_text(sorted_text)
        self.assertEqual(self.manifest("--check", "--committed-only").returncode, 0)

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
