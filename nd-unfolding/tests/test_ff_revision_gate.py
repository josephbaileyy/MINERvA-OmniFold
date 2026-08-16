"""G0's revision gate must REFUSE a stale tree — and the old check must be shown to accept it.

`BEN-301`: a digest pin authenticates content against an expectation stored in the same tree, so it is
blind to the tree being stale; both sides go stale together and agree perfectly. Measured on 2026-08-16,
cluster wrapper `ee269b09` against a cluster literal `ee269b09` — **G0 would have PASSED** with the
checkout 663 commits behind.

EVERY CASE HERE IS A DEMONSTRATED REFUSAL, not an asserted success (`BEN-314`). The axis each control
licenses is named in its own docstring (`BEN-342`).

BUILT AGAINST THROWAWAY REPOSITORIES, NEVER THE LIVE TREE (`BEN-332`: a check whose result depends on
local git state). Each test constructs its own repo in a temp dir, so the suite's verdict cannot change
because someone staged a file in the real checkout. Mutations are applied to the **working tree the gate
reads**, never to the index — repair-10's staged-copy trap, where a check read staged content and
therefore could not see the mutation it was given.
"""
import os
import shutil
import subprocess
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GATE = os.path.join(ROOT, "pet", "ff_revision_gate.py")


def git(repo, *args, **kw):
    env = dict(os.environ,
               GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
               GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    p = subprocess.run(("git", "-C", repo) + args, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, env=env)
    if kw.get("check", True) and p.returncode != 0:
        raise AssertionError(f"git {args} failed: {p.stderr.decode()}")
    return p.stdout.decode().strip()


class _Repo:
    """A throwaway checkout with two commits: v1 (old) and v2 (new), each with a matching literal."""

    def __init__(self):
        self.dir = tempfile.mkdtemp(prefix="ffrev-")
        git(self.dir, "init", "-q")
        git(self.dir, "config", "user.email", "t@t")
        git(self.dir, "config", "user.name", "t")
        self.path = os.path.join(self.dir, "pinned.py")
        self.write("VERSION = 1\n")
        git(self.dir, "add", "-A")
        git(self.dir, "commit", "-q", "-m", "v1")
        self.v1 = git(self.dir, "rev-parse", "HEAD")
        self.sha_v1 = self.sha()
        self.write("VERSION = 2  # the change a stale tree would miss\n")
        git(self.dir, "add", "-A")
        git(self.dir, "commit", "-q", "-m", "v2")
        self.v2 = git(self.dir, "rev-parse", "HEAD")
        self.sha_v2 = self.sha()

    def write(self, text):
        with open(self.path, "w") as fh:
            fh.write(text)

    def sha(self):
        import hashlib
        with open(self.path, "rb") as fh:
            return hashlib.sha256(fh.read()).hexdigest()

    def checkout(self, rev):
        git(self.dir, "checkout", "-q", rev)

    def close(self):
        shutil.rmtree(self.dir, ignore_errors=True)


def run_gate(repo, rev, files=None, literals=None):
    argv = ["python3", GATE, "--repo", repo, "--rev", rev]
    for f in (files or []):
        argv += ["--file", f]
    for p, s in (literals or {}).items():
        argv += ["--literal", f"{p}={s}"]
    p = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.returncode, (p.stdout + p.stderr).decode()


class RevisionGateTest(unittest.TestCase):
    def setUp(self):
        self.r = _Repo()
        self.addCleanup(self.r.close)

    # ---- axis: fail-closed-on-ABSENCE ------------------------------------------------------------
    def test_an_ABSENT_rev_is_refused(self):
        """A gate that passes when nobody supplies its expectation is satisfiable by absence.

        This is the property the whole design rests on, and the campaign has already paid for the other
        shape: BEN-317's `fold_forward_composed_with_annealed_arm` was True on EMPTY input.
        """
        rc, out = run_gate(self.r.dir, "", files=[self.r.path])
        self.assertNotEqual(rc, 0)
        self.assertIn("REQUIRED and has no default", out)

    def test_a_gate_with_nothing_to_check_is_refused(self):
        """Axis: an empty file list would otherwise 'pass' vacuously."""
        rc, out = run_gate(self.r.dir, self.r.v2, files=[])
        self.assertNotEqual(rc, 0)
        self.assertIn("not a gate", out)

    # ---- axis: VACUITY, i.e. repair-9's defect cannot recur here ---------------------------------
    def test_SYMBOLIC_revisions_are_refused_because_they_resolve_against_the_stale_tree(self):
        """repair-9: "a symbolic code_rev passed it for every file, forever."

        `HEAD` resolves to the stale tree's OWN head, so every blob matches its own working file and the
        gate passes on exactly the configuration it exists to refuse. Abbreviations are equally
        symbolic: a 12-hex prefix is resolvable.
        """
        for rev in ("HEAD", "main", "master", "@", "HEAD~0", "HEAD^{}", "refs/heads/main",
                    self.r.v2[:12], self.r.v2[:39], self.r.v2.upper()):
            rc, out = run_gate(self.r.dir, rev, files=[self.r.path])
            self.assertNotEqual(rc, 0, f"{rev!r} was accepted; that is repair-9's vacuity")
            self.assertIn("not a literal 40-hex commit sha", out)

    # ---- axis: EXISTENCE -------------------------------------------------------------------------
    def test_a_wellformed_sha_that_is_not_a_commit_here_is_refused(self):
        rc, out = run_gate(self.r.dir, "0" * 40, files=[self.r.path])
        self.assertNotEqual(rc, 0)
        self.assertIn("not a commit in", out)

    # ---- axis: BEN-301 STALENESS -- the axis no co-located literal can reach ----------------------
    def test_A_STALE_TREE_IS_REFUSED(self):
        """THE POINT OF THE WHOLE FILE. Tree checked out at v1, expectation names v2.

        This is the cluster's measured state in miniature: the checkout is behind, its own files are
        internally consistent, and nothing in the tree knows it.
        """
        self.r.checkout(self.r.v1)
        rc, out = run_gate(self.r.dir, self.r.v2, files=[self.r.path])
        self.assertNotEqual(rc, 0)
        self.assertIn("THIS IS THE BEN-301 CASE", out)

    def test_AND_THE_OLD_COLOCATED_LITERAL_CHECK_ACCEPTS_THAT_SAME_TREE(self):
        """THE CONTROL THAT LICENSES ITEM 3. Without it, "the new gate is stronger" is unfalsifiable.

        In the identical stale state, the pre-fix check -- compare the working file against a literal
        stored beside it in the same tree -- PASSES, because both went stale together. Demonstrated by
        executing that comparison, not by reasoning about it.

        Same standard as test_A_GLOBALLY_WRONG_BASE_RATE_IS_CAUGHT_HERE_AND_NOT_BY_THE_SIBLING: a claim
        that one guard beats another is worth exactly the case where they disagree (BEN-318 §2).
        """
        self.r.checkout(self.r.v1)
        # the pre-fix gate, in full: a literal that travelled with the tree
        literal_in_this_tree = self.r.sha_v1
        self.assertEqual(self.r.sha(), literal_in_this_tree,
                         "the OLD check PASSES on the stale tree -- both sides are stale and agree")
        # and the new gate refuses the same state
        rc, _ = run_gate(self.r.dir, self.r.v2, files=[self.r.path])
        self.assertNotEqual(rc, 0)

    # ---- axis: UNCOMMITTED DRIFT -----------------------------------------------------------------
    def test_a_dirty_working_file_is_refused_and_the_mutation_is_in_the_WORKING_TREE(self):
        """repair-10's staged-copy trap: a check that reads staged content cannot see the mutation.

        The edit here is deliberately NOT `git add`ed, so a gate reading the index would pass. Any
        __pycache__ is cleared so a stale bytecode copy cannot answer for the source either.
        """
        shutil.rmtree(os.path.join(self.r.dir, "__pycache__"), ignore_errors=True)
        with open(self.r.path, "a") as fh:
            fh.write("# uncommitted drift\n")
        self.assertIn("pinned.py", git(self.r.dir, "status", "--porcelain"),
                      "the fixture must actually be dirty in the WORKING TREE")
        rc, out = run_gate(self.r.dir, self.r.v2, files=[self.r.path])
        self.assertNotEqual(rc, 0)
        self.assertIn("uncommitted drift", out)

    # ---- axis: the literal is CROSS-CHECKED, never authoritative ----------------------------------
    def test_a_literal_disagreeing_with_the_blob_is_refused(self):
        rc, out = run_gate(self.r.dir, self.r.v2, files=[self.r.path],
                           literals={self.r.path: "f" * 64})
        self.assertNotEqual(rc, 0)
        self.assertIn("disagrees with the blob", out)

    def test_the_REVISION_wins_over_a_literal_that_merely_looks_right(self):
        """A literal naming the OLD content, on a tree correctly at the NEW revision, is still refused.

        Axis: nobody can re-introduce the co-located expectation as the authority by updating a literal.
        """
        rc, out = run_gate(self.r.dir, self.r.v2, files=[self.r.path],
                           literals={self.r.path: self.r.sha_v1})
        self.assertNotEqual(rc, 0)
        self.assertIn("REVISION is authoritative", out)

    # ---- axis: a file outside the repo, or absent at that revision --------------------------------
    def test_a_file_absent_at_that_revision_is_refused(self):
        extra = os.path.join(self.r.dir, "added_later.py")
        with open(extra, "w") as fh:
            fh.write("x = 1\n")
        rc, out = run_gate(self.r.dir, self.r.v2, files=[extra])
        self.assertNotEqual(rc, 0)
        self.assertIn("does not exist at", out)

    def test_a_file_outside_the_repo_is_refused(self):
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as fh:
            fh.write(b"x = 1\n")
            outside = fh.name
        self.addCleanup(os.unlink, outside)
        rc, out = run_gate(self.r.dir, self.r.v2, files=[outside])
        self.assertNotEqual(rc, 0)
        self.assertIn("no revision can describe it", out)

    # ---- axis: the gate is not simply always-refusing --------------------------------------------
    def test_a_clean_tree_at_the_named_revision_PASSES(self):
        """Without this the suite is satisfied by a gate that refuses everything."""
        rc, out = run_gate(self.r.dir, self.r.v2, files=[self.r.path],
                           literals={self.r.path: self.r.sha_v2})
        self.assertEqual(rc, 0, out)
        self.assertIn("tree is AT", out)
        self.assertIn("not a co-located literal", out)

    def test_the_passing_case_PRINTS_the_digest_it_checked(self):
        """A gate whose log does not carry what it checked leaves the run unreadable afterwards.

        BEN-317: G0's printed digests are the only reason arm 1's provenance survived a later pin move.
        """
        rc, out = run_gate(self.r.dir, self.r.v2, files=[self.r.path])
        self.assertEqual(rc, 0, out)
        self.assertIn(self.r.sha_v2, out)


class LauncherWiringTest(unittest.TestCase):
    """The launcher must actually USE the gate, and must not have quietly kept the old check alone."""

    LAUNCHER = os.path.join(ROOT, "pet", "sbatch_foldforward_instrumented_closure.sh")

    def setUp(self):
        with open(self.LAUNCHER) as fh:
            self.src = fh.read()
        # CODE ONLY, comments stripped. The first version of this class matched the raw file and
        # therefore failed on the launcher's own comment WARNING against `${FF_EXPECT_REV:-HEAD}` --
        # i.e. the guard was defeated by the documentation telling readers not to do the thing. A test
        # that a comment can trip is measuring the wrong text. Approximate (a `#` inside a string would
        # be stripped too), which is acceptable here because every assertion below is about the
        # presence or ordering of executable constructs, not about prose.
        self.code = "\n".join(ln.split("#", 1)[0] for ln in self.src.splitlines())

    # assertTrue with a short message rather than assertIn: a failing assertIn prints the ENTIRE
    # launcher as the container, which buried the four real failures in 55 KB of output while these
    # tests were being written.
    def test_the_launcher_requires_FF_EXPECT_REV_with_no_default(self):
        self.assertTrue("FF_EXPECT_REV" in self.code, "launcher never uses FF_EXPECT_REV in code")
        # `:-}` (default to EMPTY) is included deliberately, even though the following `-n` test would
        # refuse an empty value, so it is not itself a vacuity hole. The launcher uses `set -eo
        # pipefail` and NOT `set -u`, so no `:-` is needed at all -- which makes "FF_EXPECT_REV never
        # appears with `:-`" a bright line. "An empty default is fine" is an arguable line, and the next
        # reader arguing it is how `:-HEAD` gets added.
        for bad in (":-HEAD}", ":-main}", ":=HEAD}", ":-}"):
            self.assertFalse(f"FF_EXPECT_REV{bad}" in self.code,
                             f"FF_EXPECT_REV has a default ({bad}) IN CODE; a default IS the "
                             f"vacuity hole (a mention in a comment is fine and is why this "
                             f"assertion reads self.code, not self.src)")

    def test_the_launcher_invokes_the_revision_gate(self):
        self.assertTrue("ff_revision_gate.py" in self.code, "launcher does not reference the gate in code")

    def test_the_launcher_authenticates_the_HELPER_before_running_it(self):
        """The bootstrap level the preamble closes; the residue is stated in the predeclaration."""
        i = self.code.find("REVGATE_WANT")
        j = self.code.find('"$REVGATE" --repo')
        self.assertGreater(i, 0, "no digest check on the helper before invocation")
        self.assertGreater(j, 0, "the launcher never invokes the helper via $REVGATE")
        self.assertLess(i, j, "the helper must be authenticated BEFORE it is invoked")

    def test_train_fullevent_nominal_is_now_pinned(self):
        """BEN-312 axis: closure_powered_truth_reweight.py:224 imports NOMINAL_SEED_POLICY from it
        unconditionally, so it is a runtime configuration source and belongs in the pin set."""
        self.assertTrue("NOMINAL_POLICY" in self.code, "no NOMINAL_POLICY entry in the pin set")
        self.assertTrue("train_fullevent_nominal.py" in self.code,
                        "train_fullevent_nominal.py is not named in the launcher's CODE")


if __name__ == "__main__":
    unittest.main()
