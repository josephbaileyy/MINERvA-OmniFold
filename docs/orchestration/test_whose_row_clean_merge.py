#!/usr/bin/env python3
"""The clean-merge terminal state of `whose_row.py`, exercised on REAL temporary repositories.

WHY EVERY FIXTURE HERE IS A REAL `git merge`
--------------------------------------------
The state under test is "the merge of these exact parents was conflict-free", and the only artifact
that can disagree with a fabricated `MERGE_HEAD` is a merge git actually performed. A hand-written
index or a touched-up `MERGE_HEAD` would be a fixture derived from the rule it tests, which cannot
disagree with it -- the failure this repository has recorded twice (`a-fixture-derived-from-the-rule`
and the 178 controls that missed an unsatisfiable guard). So every case below runs `git init`,
`git commit` and `git merge` for real, and the CRITICAL NEGATIVE resolves its conflict with the two
commands an operator would actually use (`printf` + `git add`, and `git checkout --theirs` + `git add`).

THE CRITICAL NEGATIVE IS THE POINT OF THE FILE
----------------------------------------------
The cheap version of this repair -- "MERGE_HEAD present + zero unmerged entries -> 0" -- launders a
refusal. Hit a foreign conflict, get refused, resolve it by hand, `git add`, and the index is clean;
that version hands out a 0 for the exact act the gate exists to refuse. `test_hand_resolved_*` and
`test_checkout_theirs_*` are the two tests that must never go green on a 0, and they are the reason
the pass requires an INDEPENDENT reconstruction rather than an inspection of the current index.

BOTH DIRECTIONS, because a guard that only fires is as useless as one that never does: the clean
merge must PASS (`test_genuine_clean_merge_*`), and it must pass while printing what it measured, so
"no conflict" is a measurement and not an absence.

THE GATE UNDER TEST IS SWAPPABLE, and that is not a production seam -- `MNV_CLEAN_MERGE_GATE_SRC`
is read only here, so `mutation_whose_row_clean_merge.py` can point this suite at a MUTATED COPY of
the gate without a mutated file ever existing inside the repository. The infrastructure the copy
needs (FINDINGS.md's real block table, ROW-OWNERS.tsv, merge_guard.sh, VALIDATION_LEDGER.md) always
comes from the real tree, so a mutation can only be in the thing being mutated.
"""
from __future__ import annotations

import hashlib
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REAL_REPO = HERE.parent.parent
REAL_GATE = HERE / "whose_row.py"
GATE_SRC = Path(os.environ["MNV_CLEAN_MERGE_GATE_SRC"]).resolve() \
    if os.environ.get("MNV_CLEAN_MERGE_GATE_SRC") else REAL_GATE

# Copied verbatim from the real tree into every fixture repo, so the gate's own derivations
# (`ben_blocks` off FINDINGS.md's header, the ROW-OWNERS side table, merge_guard.sh's ledger arm)
# run against the REAL tables. A synthetic block table would make BEN-131's ownership a property of
# this file rather than of the repository, and the whole point of the foreign-row cases is that the
# ownership is somebody else's in the world, not in the fixture.
INFRA = ("docs/orchestration/FINDINGS.md",
         "docs/orchestration/ROW-OWNERS.tsv",
         "docs/orchestration/merge_guard.sh",
         "VALIDATION_LEDGER.md")

CONTESTED = "BEN-131"          # owner "C — PET" in the real header table; foreign to lane B
LANE = "B"                     # the lane every gate run below claims to be
ROWS = "docs/orchestration/LANE-ROWS.md"

# git must not read the operator's config here: `core.hooksPath` in this repository is an ABSOLUTE
# path (EnterWorktree normalises it for every lane), and a global hooksPath would make a throwaway
# repo run this campaign's pre-commit hook. Identity comes from the environment rather than
# `git config`, so no fixture depends on a repo-local write having happened first.
GIT_ENV = {
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_SYSTEM": os.devnull,
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_AUTHOR_NAME": "Fixture", "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
    "GIT_COMMITTER_NAME": "Fixture", "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
    "GIT_AUTHOR_DATE": "2026-09-08T00:00:00 +0000",
    "GIT_COMMITTER_DATE": "2026-09-08T00:00:00 +0000",
}


def _load_gate():
    spec = importlib.util.spec_from_file_location("whose_row_under_test", GATE_SRC)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


WR = _load_gate()


def _env():
    e = dict(os.environ)
    e.update(GIT_ENV)
    e.pop("MNV_LANE", None)     # merge_guard.sh falls back to it; a leaked value would forge a lane
    return e


class Fixture:
    """A throwaway repository laid out like this one, carrying a COPY of the gate under test."""

    def __init__(self, root: Path, git_init: bool = True):
        self.root = root
        (root / "docs/orchestration").mkdir(parents=True, exist_ok=True)
        for rel in INFRA:
            dst = root / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REAL_REPO / rel, dst)
        self.gate_path = root / "docs/orchestration/whose_row.py"
        shutil.copyfile(GATE_SRC, self.gate_path)
        if git_init:
            self.git("init", "-q", "-b", "main", ".")

    # -- plumbing ---------------------------------------------------------------------------------
    def git(self, *args, check=True) -> subprocess.CompletedProcess:
        r = subprocess.run(["git", *args], cwd=self.root, capture_output=True, text=True, env=_env())
        if check and r.returncode != 0:
            raise AssertionError(f"fixture setup: git {' '.join(args)} -> {r.returncode}\n"
                                 f"{r.stdout}\n{r.stderr}")
        return r

    def write(self, rel: str, text: str):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")

    def read(self, rel: str) -> str:
        return (self.root / rel).read_text(encoding="utf-8")

    def commit(self, msg: str):
        self.git("add", "-A")
        self.git("commit", "-q", "-m", msg)

    # -- the gate, end to end ---------------------------------------------------------------------
    def gate(self, *args) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(self.gate_path), *args],
                              cwd=self.root, capture_output=True, text=True, env=_env())

    def guard(self, *args) -> subprocess.CompletedProcess:
        return subprocess.run(["bash", "docs/orchestration/merge_guard.sh", *args],
                              cwd=self.root, capture_output=True, text=True, env=_env())

    def verdict(self):
        return WR.verify_clean_merge(self.root)

    # -- fixture states ---------------------------------------------------------------------------
    def base(self):
        """One commit carrying the infrastructure, a ledger row owned by lane C, and prose."""
        self.write(ROWS, "| id | note |\n| --- | --- |\n| %s | base wording |\n" % CONTESTED)
        self.write("docs/notes/shared.md", "shared prose, base\n")
        self.commit("base")
        return self

    def branch_then_merge(self, *, side_edits, main_edits, merge_flags=("--no-ff", "--no-commit")):
        """A real two-parent merge, left IN PROGRESS. Returns the merge's exit code."""
        self.git("checkout", "-q", "-b", "side")
        for rel, text in side_edits.items():
            self.write(rel, text)
        self.commit("side")
        self.git("checkout", "-q", "main")
        for rel, text in main_edits.items():
            self.write(rel, text)
        self.commit("main")
        return self.git("merge", *merge_flags, "side", check=False).returncode


def clean_merge(root: Path) -> Fixture:
    """Two branches touching DIFFERENT files: git auto-resolves, zero unmerged entries."""
    f = Fixture(root).base()
    rc = f.branch_then_merge(side_edits={"docs/notes/side-only.md": "added by side\n"},
                             main_edits={"docs/notes/main-only.md": "added by main\n"})
    assert rc == 0, f"fixture wanted a CLEAN merge, git returned {rc}"
    assert f.git("ls-files", "--unmerged").stdout == "", "fixture wanted zero unmerged entries"
    return f


def foreign_conflict(root: Path) -> Fixture:
    """Both branches rewrite the SAME line carrying lane C's row: a genuine content conflict."""
    f = Fixture(root).base()
    rc = f.branch_then_merge(
        side_edits={ROWS: "| id | note |\n| --- | --- |\n| %s | SIDE wording |\n" % CONTESTED},
        main_edits={ROWS: "| id | note |\n| --- | --- |\n| %s | MAIN wording |\n" % CONTESTED})
    assert rc != 0, "fixture wanted a real conflict, git merged cleanly"
    assert "<<<<<<<" in f.read(ROWS), "fixture wanted conflict markers in the working tree"
    assert f.git("ls-files", "--unmerged").stdout != "", "fixture wanted unmerged entries"
    return f


def digest_worktree(root: Path) -> str:
    """Every tracked-or-not path outside .git, name and bytes. `.git` is excluded on purpose: the
    reconstruction WRITES loose tree objects -- that is what `--write-tree` means -- and the claim
    under test is about the INDEX and the WORKING TREE, which are digested separately."""
    h = hashlib.sha256()
    for p in sorted(root.rglob("*"), key=lambda q: q.as_posix()):
        rel = p.relative_to(root).as_posix()
        if rel == ".git" or rel.startswith(".git/"):
            continue
        h.update(rel.encode() + b"\0")
        if p.is_file() and not p.is_symlink():
            h.update(hashlib.sha256(p.read_bytes()).digest())
    return h.hexdigest()


def digest_index(f: Fixture) -> str:
    p = Path(f.git("rev-parse", "--git-path", "index").stdout.strip())
    if not p.is_absolute():
        p = f.root / p
    return hashlib.sha256(p.read_bytes()).hexdigest()


class CleanMergeGateTests(unittest.TestCase):
    """End-to-end: the gate is run as a subprocess, exactly as merge_guard.sh runs it."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="wr-clean-merge-test-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def new(self, name: str) -> Path:
        d = self.tmp / name
        d.mkdir(parents=True)
        return d

    # ---- THE CRITICAL NEGATIVE ------------------------------------------------------------------
    def test_hand_resolved_foreign_conflict_is_not_a_pass(self):
        """Refused, then resolved by hand and staged. The index is now clean; the answer is still no.

        This is the laundering path the cheap fix opens, run for real: `git diff --diff-filter=U` is
        EMPTY at the moment of the second run, so anything that reads only the index sees a clean
        merge and passes. The reconstruction does not read the index.
        """
        f = foreign_conflict(self.new("critical"))

        refused = f.gate("--conflicts", "--lane", LANE)
        self.assertEqual(refused.returncode, 1, f"wanted the FOREIGN refusal first\n{refused.stdout}")
        self.assertIn(CONTESTED, refused.stdout)
        self.assertIn("route to its author", refused.stdout)

        f.write(ROWS, "| id | note |\n| --- | --- |\n| %s | HAND-RESOLVED by lane B |\n" % CONTESTED)
        f.git("add", ROWS)
        self.assertEqual(f.git("diff", "--name-only", "--diff-filter=U").stdout, "",
                         "the premise of this test is that the index now looks clean")

        after = f.gate("--conflicts", "--lane", LANE)
        self.assertNotEqual(after.returncode, 0,
                            "A HAND-RESOLVED FOREIGN CONFLICT WAS PASSED. This is the hole the "
                            f"clean-merge path must not open.\n{after.stdout}\n{after.stderr}")
        self.assertEqual(after.returncode, 2, after.stdout)
        self.assertIn("RECONSTRUCTION-CONFLICTED", after.stdout)
        self.assertIn(ROWS, after.stdout, "the refusal must name the path that conflicts")

    def test_checkout_theirs_resolution_is_not_a_pass(self):
        """The other resolution an operator actually types. Same verdict, and it must be, because
        `--theirs` is a CHOICE about another lane's row -- the choice the gate refuses."""
        f = foreign_conflict(self.new("theirs"))
        self.assertEqual(f.gate("--conflicts", "--lane", LANE).returncode, 1)
        f.git("checkout", "--theirs", "--", ROWS)
        f.git("add", ROWS)
        r = f.gate("--conflicts", "--lane", LANE)
        self.assertNotEqual(r.returncode, 0, r.stdout)
        self.assertEqual(r.returncode, 2, r.stdout)
        self.assertIn("RECONSTRUCTION-CONFLICTED", r.stdout)

    # ---- THE POSITIVE -------------------------------------------------------------------------
    def test_genuine_clean_merge_passes_and_prints_its_measurement(self):
        f = clean_merge(self.new("clean"))
        head = f.git("rev-parse", "HEAD").stdout.strip()
        mh = (f.root / ".git/MERGE_HEAD").read_text().strip()
        r = f.gate("--conflicts", "--lane", LANE)
        self.assertEqual(r.returncode, 0, f"{r.stdout}\n{r.stderr}")
        self.assertIn("CLEAN MERGE VERIFIED", r.stdout)
        # THE PARENTS, in full, so the pass names the object it measured.
        self.assertIn(head, r.stdout)
        self.assertIn(mh, r.stdout)
        # THE SCOPE, so "no conflict" is a measurement. side-only.md is what the merge brings in.
        self.assertIn("docs/notes/side-only.md", r.stdout)
        self.assertIn("scope inspected:   1 path(s)", r.stdout)
        # And the two trees are named AND equal, which is the whole claim.
        trees = re.findall(r"-> ([0-9a-f]{40})|staged tree:       ([0-9a-f]{40})", r.stdout)
        flat = [t for pair in trees for t in pair if t]
        self.assertEqual(len(flat), 2, r.stdout)
        self.assertEqual(flat[0], flat[1], "the pass printed two DIFFERENT trees")

    def test_a_clean_merge_with_nothing_incoming_still_names_its_parents(self):
        """A merge whose other side changes nothing this side lacks: scope may legitimately be
        empty, and the pass must still print the parents rather than an empty measurement."""
        f = Fixture(self.new("empty-scope")).base()
        # side does something and then undoes it, so its TIP TREE equals the base's while side is
        # still not an ancestor of main -- the merge is real, and it brings in nothing.
        f.git("checkout", "-q", "-b", "side")
        f.write("docs/notes/transient.md", "here\n")
        f.commit("side adds")
        (f.root / "docs/notes/transient.md").unlink()
        f.commit("side removes it again")
        f.git("checkout", "-q", "main")
        f.write("docs/notes/main-only.md", "added by main\n")
        f.commit("main")
        self.assertEqual(f.git("merge", "--no-ff", "--no-commit", "side", check=False).returncode, 0)
        r = f.gate("--conflicts", "--lane", LANE)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("scope inspected:   0 path(s)", r.stdout)
        self.assertIn(f.git("rev-parse", "HEAD").stdout.strip(), r.stdout)

    # ---- THE NEGATIVES -------------------------------------------------------------------------
    def test_unresolved_foreign_conflict_still_refuses_with_1(self):
        """The pre-existing refusal path, unchanged: exit 1, the author named, no clean-merge text."""
        f = foreign_conflict(self.new("unresolved"))
        r = f.gate("--conflicts", "--lane", LANE)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("REFUSED", r.stdout)
        self.assertIn("C — PET", r.stdout)
        self.assertNotIn("CLEAN MERGE VERIFIED", r.stdout)

    def test_the_row_owner_merging_their_own_row_still_passes_with_0(self):
        """The other pre-existing exit 0, unchanged. Without this the suite could not tell a repair
        from a regression that refuses everything."""
        f = foreign_conflict(self.new("own-row"))
        r = f.gate("--conflicts", "--lane", "C")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("every contested row is yours", r.stdout)

    def test_no_merge_in_progress_is_2(self):
        f = Fixture(self.new("no-merge")).base()
        r = f.gate("--conflicts", "--lane", LANE)
        self.assertEqual(r.returncode, 2, r.stdout)
        self.assertIn("NO-MERGE-IN-PROGRESS", r.stdout)
        self.assertIn("CANNOT CHECK", r.stdout)

    def test_enumeration_failure_is_2(self):
        """A real git failure, not a simulated one: the gate is run where there is no repository,
        so `git diff --diff-filter=U` exits 128 and the gate cannot enumerate anything."""
        d = self.new("not-a-repo")
        f = Fixture(d, git_init=False)
        self.assertFalse((d / ".git").exists())
        r = f.gate("--conflicts", "--lane", LANE)
        self.assertEqual(r.returncode, 2, f"{r.stdout}\n{r.stderr}")
        self.assertIn("could not enumerate unmerged files", r.stdout)
        self.assertNotIn("CLEAN MERGE VERIFIED", r.stdout)

    def test_staged_unrelated_drift_is_not_a_pass(self):
        """A genuinely clean merge plus one extra staged edit. Nothing about the merge changed; what
        would be COMMITTED did, and the trees say so."""
        f = clean_merge(self.new("drift"))
        self.assertEqual(f.gate("--conflicts", "--lane", LANE).returncode, 0,
                         "premise: this merge passes before the drift is staged")
        f.write("docs/notes/shared.md", "shared prose, EDITED while merging\n")
        f.git("add", "docs/notes/shared.md")
        r = f.gate("--conflicts", "--lane", LANE)
        self.assertNotEqual(r.returncode, 0, r.stdout)
        self.assertEqual(r.returncode, 2, r.stdout)
        self.assertIn("TREE-MISMATCH", r.stdout)

    def test_a_staged_edit_that_only_reverts_the_merge_is_also_refused(self):
        """Drift in the other direction -- undoing what the merge brought in, which a bare
        `git status` after `git add` shows as nothing at all."""
        f = clean_merge(self.new("drift-revert"))
        (f.root / "docs/notes/side-only.md").unlink()
        f.git("add", "-A")
        r = f.gate("--conflicts", "--lane", LANE)
        self.assertEqual(r.returncode, 2, r.stdout)
        self.assertIn("TREE-MISMATCH", r.stdout)

    def test_octopus_merge_is_not_a_pass(self):
        """Three parents, clean, zero unmerged entries -- and not reconstructible by a two-parent
        facility, so it is not verifiable and therefore not a pass."""
        f = Fixture(self.new("octopus")).base()
        for name in ("s1", "s2"):
            f.git("checkout", "-q", "-b", name, "main")
            f.write(f"docs/notes/{name}.md", f"added by {name}\n")
            f.commit(name)
        f.git("checkout", "-q", "main")
        f.write("docs/notes/main-only.md", "added by main\n")
        f.commit("main")
        self.assertEqual(f.git("merge", "--no-commit", "s1", "s2", check=False).returncode, 0)
        self.assertEqual((f.root / ".git/MERGE_HEAD").read_text().split().__len__(), 2)
        r = f.gate("--conflicts", "--lane", LANE)
        self.assertEqual(r.returncode, 2, r.stdout)
        self.assertIn("NOT-A-TWO-PARENT-MERGE", r.stdout)

    def test_unrelated_histories_clean_merge_is_not_a_pass(self):
        """`git merge --allow-unrelated-histories` can be CLEAN while the reconstruction refuses to
        run at all (`merge-tree` exits 128, "refusing to merge unrelated histories"). An inability
        is not a verdict, so this is a 2 -- and it is the case that shows condition 2 carrying
        weight on its own rather than being implied by condition 3."""
        f = Fixture(self.new("unrelated")).base()
        f.git("checkout", "-q", "--orphan", "orphan")
        f.git("rm", "-q", "-rf", ".")
        f.write("docs/notes/orphan.md", "unrelated history\n")
        f.commit("orphan")
        f.git("checkout", "-q", "main")
        self.assertEqual(f.git("merge", "--allow-unrelated-histories", "--no-ff", "--no-commit",
                               "orphan", check=False).returncode, 0)
        self.assertEqual(f.git("ls-files", "--unmerged").stdout, "")
        r = f.gate("--conflicts", "--lane", LANE)
        self.assertEqual(r.returncode, 2, r.stdout)
        self.assertIn("RECONSTRUCTION-UNAVAILABLE", r.stdout)

    def test_naming_files_explicitly_cannot_reach_the_clean_merge_path(self):
        """The clean-merge state requires the gate's OWN enumeration to have returned zero. A named
        file set is a question about those files, and it answers as it always did."""
        f = clean_merge(self.new("named"))
        r = f.gate("--conflicts", "--lane", LANE, ROWS)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("NO ATTRIBUTABLE ROWS", r.stdout)
        self.assertNotIn("CLEAN MERGE VERIFIED", r.stdout)

    def test_query_mode_on_a_clean_merge_is_untouched(self):
        """Without --lane this is a query, and an empty answer was always a fine answer. The repair
        must not have changed it -- a behaviour change here would be an unrequested one."""
        f = clean_merge(self.new("query"))
        r = f.gate("--conflicts")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("no unmerged files; nothing to attribute  (query mode: 0 files, 0 rows)",
                      r.stdout)
        self.assertNotIn("CLEAN MERGE VERIFIED", r.stdout)

    def test_an_empty_lane_is_still_fatal(self):
        """BEN-117's gate-that-cannot-fail. A clean merge must not have given `--lane ""` a door."""
        f = clean_merge(self.new("empty-lane"))
        r = f.gate("--conflicts", "--lane", "")
        self.assertEqual(r.returncode, 2)
        self.assertIn("FATAL", r.stderr)
        self.assertNotIn("CLEAN MERGE VERIFIED", r.stdout)

    # ---- ISOLATION, measured ---------------------------------------------------------------------
    def test_the_gate_writes_neither_the_index_nor_the_working_tree(self):
        """"It does not touch your merge" is a measurement here. Digested before and after, on the
        PASSING path -- the one that runs every git invocation in the function."""
        f = clean_merge(self.new("isolation"))
        before_wt, before_idx = digest_worktree(f.root), digest_index(f)
        scratch_before = set(os.listdir(tempfile.gettempdir()))
        r = f.gate("--conflicts", "--lane", LANE)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertEqual(digest_worktree(f.root), before_wt, "the working tree was modified")
        self.assertEqual(digest_index(f), before_idx, "the real index was written")
        left = [n for n in set(os.listdir(tempfile.gettempdir())) - scratch_before
                if n.startswith("whose_row-mergecheck-")]
        self.assertEqual(left, [], f"scratch directories left behind: {left}")

    def test_isolation_holds_on_a_refusing_path_too(self):
        f = foreign_conflict(self.new("isolation-refuse"))
        f.write(ROWS, "| id | note |\n| --- | --- |\n| %s | hand |\n" % CONTESTED)
        f.git("add", ROWS)
        before_wt, before_idx = digest_worktree(f.root), digest_index(f)
        self.assertEqual(f.gate("--conflicts", "--lane", LANE).returncode, 2)
        self.assertEqual(digest_worktree(f.root), before_wt)
        self.assertEqual(digest_index(f), before_idx)


class MergeGuardWrapperTests(unittest.TestCase):
    """`merge_guard.sh` is the only interpreter of these exit codes (BEN-163), so the codes are
    checked THROUGH it as well as at the gate. It runs the gate's self-test and ledger arm first,
    so these three cases also prove the repair did not break either."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="wr-guard-test-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def new(self, name: str) -> Path:
        d = self.tmp / name
        d.mkdir(parents=True)
        return d

    def test_missing_lane_is_3(self):
        f = clean_merge(self.new("no-lane"))
        r = f.guard()
        self.assertEqual(r.returncode, 3, f"{r.stdout}\n{r.stderr}")
        self.assertIn("no lane given", r.stdout)

    def test_a_clean_merge_passes_through_the_wrapper_as_0(self):
        f = clean_merge(self.new("guard-clean"))
        r = f.guard(LANE)
        self.assertEqual(r.returncode, 0, f"{r.stdout}\n{r.stderr}")
        self.assertIn("CLEAN MERGE VERIFIED", r.stdout)
        self.assertIn("PASS", r.stdout)

    def test_the_hand_resolved_conflict_passes_through_the_wrapper_as_2(self):
        f = foreign_conflict(self.new("guard-laundered"))
        f.write(ROWS, "| id | note |\n| --- | --- |\n| %s | hand |\n" % CONTESTED)
        f.git("add", ROWS)
        r = f.guard(LANE)
        self.assertNotEqual(r.returncode, 0, r.stdout)
        self.assertEqual(r.returncode, 2, r.stdout)
        self.assertIn("CANNOT CHECK", r.stdout)


class VerdictReasonTests(unittest.TestCase):
    """The reason token per state, called as a unit against the same REAL repositories.

    Asserting the token is not decoration. Section 2 of the 2026-09-08 ruling is that "the guard
    refused" withholds the field that decides what to do next; and one condition here -- zero
    unmerged entries -- CANNOT change an exit code on its own, because an index with unmerged
    entries cannot produce a tree and condition 4 would refuse anyway. Its whole contribution is
    naming the cause, so the only test that can hold it is a test that reads the name.
    """

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="wr-verdict-test-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def new(self, name: str) -> Path:
        d = self.tmp / name
        d.mkdir(parents=True)
        return d

    def test_a_verified_clean_merge_reports_every_field_it_measured(self):
        v = clean_merge(self.new("ok")).verdict()
        self.assertTrue(v.ok, v)
        self.assertEqual(v.reason, "CLEAN-MERGE-VERIFIED")
        self.assertRegex(v.head, r"^[0-9a-f]{40}$")
        self.assertRegex(v.merge_head, r"^[0-9a-f]{40}$")
        self.assertEqual(len(v.bases), 1)
        self.assertEqual(v.reconstructed_tree, v.staged_tree)
        self.assertEqual(v.unmerged, 0)
        self.assertEqual(v.scope, ("docs/notes/side-only.md",))

    def test_unresolved_conflict_names_the_unmerged_entries_not_a_downstream_inability(self):
        v = foreign_conflict(self.new("unmerged")).verdict()
        self.assertFalse(v.ok)
        self.assertEqual(v.reason, "UNMERGED-ENTRIES-PRESENT", v.detail)
        self.assertEqual(v.unmerged, 3)      # stages 1, 2, 3 of the one conflicted path

    def test_hand_resolved_conflict_names_the_reconstruction(self):
        f = foreign_conflict(self.new("hand"))
        f.write(ROWS, "| id | note |\n| --- | --- |\n| %s | hand |\n" % CONTESTED)
        f.git("add", ROWS)
        v = f.verdict()
        self.assertFalse(v.ok)
        self.assertEqual(v.reason, "RECONSTRUCTION-CONFLICTED", v.detail)
        self.assertEqual(v.unmerged, 0, "the index really is clean; that is the point")

    def test_no_merge_in_progress(self):
        v = Fixture(self.new("none")).base().verdict()
        self.assertFalse(v.ok)
        self.assertEqual(v.reason, "NO-MERGE-IN-PROGRESS", v.detail)

    def test_a_non_repository_is_a_git_failure_not_a_pass(self):
        v = WR.verify_clean_merge(self.new("bare-dir"))
        self.assertFalse(v.ok)
        self.assertEqual(v.reason, "GIT-FAILURE", v.detail)

    def test_staged_drift_names_the_two_trees(self):
        f = clean_merge(self.new("mismatch"))
        f.write("docs/notes/shared.md", "edited\n")
        f.git("add", "docs/notes/shared.md")
        v = f.verdict()
        self.assertFalse(v.ok)
        self.assertEqual(v.reason, "TREE-MISMATCH", v.detail)
        self.assertNotEqual(v.staged_tree, v.reconstructed_tree)
        self.assertIn(v.staged_tree, v.detail)
        self.assertIn(v.reconstructed_tree, v.detail)

    def test_an_unstaged_worktree_edit_does_not_change_the_verdict(self):
        """A DOCUMENTED LIMIT, pinned so it is a decision rather than an oversight. The operand is
        the INDEX, because that is what `git commit` records for a merge. An unstaged edit is not a
        resolution of anybody's row -- resolving a conflict requires staging, and until it is staged
        the unmerged entries are still there and condition 5 refuses. `git commit -a` would commit
        something this gate did not verify; the exit-0 message says so."""
        f = clean_merge(self.new("unstaged"))
        (f.root / "docs/notes/shared.md").write_text("edited but NOT staged\n", encoding="utf-8")
        v = f.verdict()
        self.assertTrue(v.ok, v.detail)
        r = f.gate("--conflicts", "--lane", LANE)
        self.assertEqual(r.returncode, 0)
        self.assertIn("git commit -a", r.stdout)


if __name__ == "__main__":
    unittest.main()
