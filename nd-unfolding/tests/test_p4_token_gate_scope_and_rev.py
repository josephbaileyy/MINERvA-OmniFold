#!/usr/bin/env python3
"""repair-9 -- the token gate's `code_rev` must be a LITERAL sha and its scope must be a UNION.

Subject: the two critical defects the repair-8 verdict
(`docs/orchestration/runs/standard-p4-verifier/20260815T232546Z-repair8-verdict.json`) named as
the reason for its BLOCK, and told the lane to fix together because they compound:

  #5  a SYMBOLIC `code_rev` made the gate's own staleness check VACUOUS. `code_rev: "HEAD"`
      passes rule 4a (`git merge-base --is-ancestor HEAD HEAD` succeeds) and rule 4b then
      compares HEAD against HEAD and finds zero differing files -- for every file, forever.
      Second half: rule 4b compares two COMMITS, so an uncommitted edit to a reviewed file was
      invisible to the gate, while the chain executes the WORKING TREE.
  #4  the declared `review_scope` was trusted VERBATIM, so a verdict could declare one unrelated
      file and satisfy 4b trivially; and the fallback surface omitted the scripts the shell
      drivers INVOKE (`p3s_manifest_summary.py`).

**Why this file is shaped the way it is.** BEN-314: a suite passed 18 tests and mutation-tested
two guards while being structurally unable to catch the bug it existed to prevent. So every
positive assertion here has a committed NEGATIVE CONTROL -- a `test_MUTATION_*` that rebuilds the
PRE-FIX form of the very line under test and shows the same input is ACCEPTED. If a mutation
anchor ever stops matching, the mutation asserts rather than silently passing.

Two further rules, both from this chain's own history:

  * the gate is driven END TO END, as a subprocess, against a REAL git repository -- a throwaway
    one holding a byte-identical copy of the live gate. Nothing here asserts on source text, and
    nothing hand-assembles a verdict to match a reader (BEN-040 was that inversion).
  * every rejection is asserted by its SPECIFIC reason, never by a nonzero exit. Repair-7's
    defect #6 is exactly a test that would have been green on "it errored".
"""
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ND = Path(__file__).resolve().parents[1]
REPO = ND.parent
sys.path.insert(0, str(ND))
import p4_lib as P                                                        # noqa: E402

GATE_REL = "nd-unfolding/p4_check_verifier_token.py"
LIB_REL = "nd-unfolding/p4_lib.py"
RECEIPT_REL = "docs/orchestration/runs/standard-p4-verifier"

# ---- pre-fix reconstructions. Each is the line as it stood at the reviewed revision. ----
PREFIX_NO_LITERAL_SHA_CHECK = [
    # rule 4a had no literal-sha requirement at all ...
    (GATE_REL, "    if not P.is_literal_commit_sha(cr):", "    if False:"),
    # ... and the library helper guarded only non-emptiness, which is the verbatim pre-fix line.
    (LIB_REL, "    if not is_literal_commit_sha(rev):\n        return False",
     "    if not (isinstance(rev, str) and rev.strip()):\n        return False"),
]
PREFIX_VERBATIM_SCOPE = [
    (GATE_REL, "    paths = sorted(set(surface) | set(declared))",
     "    paths = sorted(set(declared)) if declared else sorted(set(surface))"),
]
PREFIX_NO_WORKTREE_CHECK = [
    (GATE_REL, "    ok_wt, dirty = P.paths_unchanged_vs_worktree(cr, paths)",
     "    ok_wt, dirty = True, []"),
]


def _sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


class Sandbox:
    """A throwaway git repository containing a copy of the LIVE gate and library.

    Needed because rule (2) requires the verdict to be TRACKED and identical to its committed
    blob, and rules 4a/4b/4c are statements about commits and the working tree. Those cannot be
    exercised against the real repository without committing a forged PASS verdict into the real
    ledger, which is precisely the act the gate is designed to make visible. The gate resolves
    `REPO_ROOT` from `p4_lib.py`'s own location, so a copied tree is a complete environment for
    it -- and the copy is byte-identical to the tracked file unless a mutation is requested.
    """

    def __init__(self, mutations=()):
        self.dir = Path(tempfile.mkdtemp(prefix="p4tokengate-"))
        (self.dir / "nd-unfolding").mkdir(parents=True)
        (self.dir / RECEIPT_REL).mkdir(parents=True)
        for rel in (LIB_REL, GATE_REL):
            src = (REPO / rel).read_text()
            for mrel, old, new in mutations:
                if mrel != rel:
                    continue
                assert old in src, f"mutation anchor not found in {rel}: {old[:70]!r}"
                assert src.count(old) == 1, f"ambiguous mutation anchor in {rel}: {old[:70]!r}"
                src = src.replace(old, new)
            (self.dir / rel).write_text(src)
        # an in-scope-but-not-on-the-surface file, so a narrow declared scope has somewhere to hide
        (self.dir / "docs").mkdir(exist_ok=True)
        (self.dir / "docs" / "unrelated.md").write_text("a doc no execution surface contains\n")
        self._git("init", "-q")
        self._git("config", "user.email", "repair9@test.invalid")
        self._git("config", "user.name", "repair9 sandbox")

    # -- git plumbing -------------------------------------------------------
    def _git(self, *args):
        return subprocess.check_output(["git", *args], cwd=str(self.dir), text=True,
                                       stderr=subprocess.STDOUT).strip()

    def commit(self, msg):
        self._git("add", "-A")
        self._git("commit", "-q", "-m", msg)
        return self._git("rev-parse", "HEAD")

    def touch_lib(self, committed, msg="drift"):
        """Append a comment to the copied p4_lib.py -- a real, harmless byte change to a file on
        the execution surface. Committed or left dirty depending on which rule is under test."""
        p = self.dir / LIB_REL
        p.write_text(p.read_text() + "\n# repair-9 sandbox drift marker\n")
        return self.commit(msg) if committed else None

    # -- the artifact under authorization ----------------------------------
    def write_verdict(self, **fields):
        v = {"receipt_kind": "standard-p4-verifier verdict", "verdict": "PASS",
             "authorizes_covariance_stages_4_6": True}
        v.update(fields)
        blob = (json.dumps(v, indent=2, sort_keys=True) + "\n").encode()
        (self.dir / RECEIPT_REL / "20260816T000000Z-sandbox-verdict.json").write_bytes(blob)
        return _sha256_bytes(blob)

    def run_gate(self, token):
        r = subprocess.run([sys.executable, str(self.dir / GATE_REL), "--token", token],
                           cwd=str(self.dir / "nd-unfolding"), capture_output=True, text=True)
        return r.returncode, (r.stdout + r.stderr).strip()

    def close(self):
        shutil.rmtree(self.dir, ignore_errors=True)


class _SandboxCase(unittest.TestCase):
    """Scenario builders. Each returns (sandbox, token) with the repo in the state under test."""

    def _sandbox(self, mutations=()):
        sb = Sandbox(mutations)
        self.addCleanup(sb.close)
        return sb

    def _clean_pass(self, mutations=(), **verdict_fields):
        """A verdict that SHOULD be honoured: literal sha, nothing changed since, clean tree."""
        sb = self._sandbox(mutations)
        base = sb.commit("sources")
        tok = sb.write_verdict(code_rev=base, **verdict_fields)
        sb.commit("verdict")
        return sb, tok

    def _symbolic_rev(self, rev, mutations=()):
        sb = self._sandbox(mutations)
        sb.commit("sources")
        tok = sb.write_verdict(code_rev=rev)
        sb.commit("verdict")
        return sb, tok

    def _narrow_scope_then_surface_drift(self, mutations=()):
        """The #4 scenario: the declared scope is a file that did NOT change; a file on the
        EXECUTION SURFACE did."""
        sb = self._sandbox(mutations)
        base = sb.commit("sources")
        tok = sb.write_verdict(code_rev=base, review_scope=["docs/unrelated.md"])
        sb.commit("verdict")
        sb.touch_lib(committed=True, msg="another lane changes p4_lib.py after the PASS")
        return sb, tok

    def _dirty_worktree(self, mutations=()):
        """The #5 second-half scenario: the reviewed file is edited but NOT committed, so both
        sides of the commit-to-commit comparison are identical and only the tree differs."""
        sb = self._sandbox(mutations)
        base = sb.commit("sources")
        tok = sb.write_verdict(code_rev=base)
        sb.commit("verdict")
        sb.touch_lib(committed=False)
        return sb, tok


class TheGateStillHonoursAValidPass(_SandboxCase):
    """The control that keeps the rest honest: a fix that rejected everything would 'pass' every
    test below. It must not. Both the bare form and the wider-scope form are accepted."""

    def test_a_wellformed_pass_is_accepted(self):
        sb, tok = self._clean_pass()
        rc, out = sb.run_gate(tok)
        self.assertEqual(rc, 0, out)
        self.assertIn("TOKEN-OK", out)

    def test_a_declared_scope_WIDER_than_the_surface_is_accepted(self):
        """A verifier may review MORE than the chain executes; the union must not punish that."""
        sb, tok = self._clean_pass(review_scope=["docs/unrelated.md", LIB_REL])
        rc, out = sb.run_gate(tok)
        self.assertEqual(rc, 0, out)
        self.assertIn("TOKEN-OK", out)

    def test_a_genuinely_stale_pass_is_still_rejected(self):
        """The pre-existing property 4b protects, re-asserted so this repair cannot have loosened
        it: a surface file changed after the PASS and no scope is declared."""
        sb, tok = self._clean_pass()
        sb.touch_lib(committed=True)
        rc, out = sb.run_gate(tok)
        self.assertEqual(rc, 1)
        self.assertIn("have CHANGED at HEAD", out)
        self.assertIn(LIB_REL, out)


class Defect5_SymbolicCodeRev(_SandboxCase):
    """#5: `code_rev` must name ONE immutable object, or the staleness check checks nothing.

    Measured in the repair-8 verdict: `code_rev_in_history` returned True for each of 'HEAD',
    'main', 'HEAD~0' and 'HEAD~3', and `paths_unchanged_between('HEAD', HEAD, surface)` returned
    ok=True with 0 differing files."""

    SYMBOLIC = ("HEAD", "main", "HEAD~0", "HEAD~3", "@", "refs/heads/main")

    def test_every_symbolic_rev_is_rejected_for_being_symbolic(self):
        for rev in self.SYMBOLIC:
            with self.subTest(rev=rev):
                sb, tok = self._symbolic_rev(rev)
                rc, out = sb.run_gate(tok)
                self.assertEqual(rc, 1, out)
                # the SPECIFIC reason: not "some ancestry check failed"
                self.assertIn("is not a literal 40-hex commit sha", out)
                self.assertNotIn("is not an ancestor of HEAD", out)

    def test_an_abbreviated_sha_is_rejected(self):
        """Both producers stamp `git rev-parse HEAD`, so a short id is hand-written provenance."""
        sb = self._sandbox()
        base = sb.commit("sources")
        tok = sb.write_verdict(code_rev=base[:12])
        sb.commit("verdict")
        rc, out = sb.run_gate(tok)
        self.assertEqual(rc, 1, out)
        self.assertIn("is not a literal 40-hex commit sha", out)

    def test_the_library_helper_refuses_symbolic_revs_too(self):
        """Not only the gate: `validate_endpoint_receipt` calls `code_rev_in_history` on a
        receipt's own `code_rev`, and would have accepted 'HEAD' for the same vacuous reason."""
        for rev in self.SYMBOLIC:
            self.assertFalse(P.code_rev_in_history(rev), f"{rev!r} accepted as a code_rev")
            self.assertFalse(P.is_literal_commit_sha(rev))
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(REPO),
                                       text=True).strip()
        self.assertTrue(P.is_literal_commit_sha(head))
        self.assertTrue(P.code_rev_in_history(head), "a real full sha must still be accepted")

    def test_MUTATION_prefix_gate_ACCEPTS_a_symbolic_code_rev(self):
        """THE NEGATIVE CONTROL for #5. Rebuild the pre-fix form -- no literal-sha rule in the
        gate, non-emptiness only in the helper -- and show `code_rev: "HEAD"` is AUTHORIZED. This
        is the defect, executed: the same verdict the fixed gate refuses opens stages 4-6."""
        sb, tok = self._symbolic_rev("HEAD", mutations=PREFIX_NO_LITERAL_SHA_CHECK)
        rc, out = sb.run_gate(tok)
        self.assertEqual(rc, 0, f"pre-fix gate should have authorized this: {out}")
        self.assertIn("TOKEN-OK", out)
        self.assertIn("code_rev=HEAD", out)

    def test_MUTATION_prefix_helper_reports_every_symbolic_rev_in_history(self):
        """The measurement the verdict recorded, reproduced against the pre-fix helper.

        `'main'` WAS IN THIS TUPLE UNTIL 2026-08-16 AND IS DELIBERATELY OUT OF IT (BEN-343).
        `code_rev_in_history` asks whether a rev is an ANCESTOR of `HEAD`. In a git worktree on a
        feature branch, `main` resolves fine and is *not* necessarily an ancestor -- so this test
        failed for anyone running the suite from a worktree whose branch was behind `main`, which on
        this campaign is most lanes for most of the day (`CONVENTION-lane-worktrees.md`). Measured
        when it fired: `HEAD e07b986`, `main 6e05985`, `merge-base --is-ancestor main HEAD` false,
        one commit ahead, because another lane had pushed mid-edit. It cleared on rebase.

        DROPPING IT COSTS NO COVERAGE, which is why this is a fix and not a weakening. The property
        under test is that the pre-fix helper calls SYMBOLIC names in-history, and `HEAD`, `HEAD~0`
        and `HEAD~3` are all symbolic and all in-history *by construction from any checkout*.
        `'main'` was the only element whose truth depended on the runner's git position, and a test
        whose result depends on where you are standing is reporting that, not the code (`BEN-332`'s
        shape, with the dependency moved from untracked caches to the branch pointer).

        If a BRANCH-NAME case is ever wanted specifically -- a fair thing to want, since a branch
        name is a different kind of symbolic ref from `HEAD~n` -- create one here rather than
        borrowing the repository's:
            subprocess.run(["git", "branch", "-f", "ben343-probe", "HEAD"], cwd=REPO, check=True)
        """
        mut = _mutated_lib([(LIB_REL, *PREFIX_NO_LITERAL_SHA_CHECK[1][1:])])
        for rev in ("HEAD", "HEAD~0", "HEAD~3"):
            self.assertTrue(mut.code_rev_in_history(rev),
                            f"pre-fix helper should call {rev!r} in-history")
        ok, differing = mut.paths_unchanged_between("HEAD", "HEAD",
                                                    mut.standard_p4_execution_surface())
        self.assertTrue(ok)
        self.assertEqual(differing, [], "HEAD vs HEAD differs in nothing -- that is the defect")


class Defect5b_WorkingTreeIsWhatExecutes(_SandboxCase):
    """#5 second half: 4b compares two COMMITS. Rule (2) compares the working tree against the
    committed blob, but only for the VERDICT FILE, never for the code it reviewed."""

    def test_an_uncommitted_edit_to_a_reviewed_file_is_refused(self):
        sb, tok = self._dirty_worktree()
        rc, out = sb.run_gate(tok)
        self.assertEqual(rc, 1, out)
        self.assertIn("IN THE WORKING TREE", out)
        self.assertIn(LIB_REL, out)

    def test_the_helper_fails_closed_on_a_path_it_cannot_resolve(self):
        ok, differing = P.paths_unchanged_vs_worktree("HEAD", ["nd-unfolding/does_not_exist.py"])
        self.assertFalse(ok, "an unverifiable path must count as differing, not as satisfied")
        self.assertEqual(differing, ["nd-unfolding/does_not_exist.py"])

    def test_the_helper_agrees_with_a_clean_tree(self):
        """The other polarity: a clean tree must be reported clean, or 4c refuses everything.

        Constructed in a sandbox whose state this test owns, NOT against the live checkout: a
        lane with any uncommitted edit on the surface -- including the lane that repairs the
        surface -- would otherwise turn this red for a reason that is not the property. A test
        whose premise depends on someone else's working tree is a flaky test."""
        sb = self._sandbox()
        base = sb.commit("sources")
        surface = P.standard_p4_execution_surface()
        in_sandbox = [p for p in surface if (sb.dir / p).is_file()]
        self.assertEqual(sorted(in_sandbox), sorted([GATE_REL, LIB_REL]))
        for rev in (base, "HEAD"):
            ok, differing = _in_dir(sb.dir, P.paths_unchanged_vs_worktree, rev, in_sandbox)
            self.assertTrue(ok, f"clean tree reported dirty at {rev}: {differing}")

    def test_MUTATION_prefix_gate_ACCEPTS_an_uncommitted_edit(self):
        """THE NEGATIVE CONTROL for #5's second half: with rule 4c removed, the identical dirty
        tree is authorized, and the two commit-to-commit rules see nothing at all."""
        sb, tok = self._dirty_worktree(mutations=PREFIX_NO_WORKTREE_CHECK)
        rc, out = sb.run_gate(tok)
        self.assertEqual(rc, 0, f"pre-fix gate should have authorized this: {out}")
        self.assertIn("TOKEN-OK", out)


class Defect4_ScopeIsAUnionNotASubstitute(_SandboxCase):
    """#4: a declared `review_scope` may only ADD to the execution surface, never replace it."""

    def test_a_narrow_scope_cannot_hide_drift_on_the_execution_surface(self):
        sb, tok = self._narrow_scope_then_surface_drift()
        rc, out = sb.run_gate(tok)
        self.assertEqual(rc, 1, out)
        self.assertIn("have CHANGED at HEAD", out)
        self.assertIn(LIB_REL, out)
        self.assertIn("NOT in the declared review_scope", out)

    def test_a_scope_entry_that_is_not_a_path_is_refused(self):
        """A scope in a form the gate cannot read must fail closed, not be silently ignored."""
        sb = self._sandbox()
        base = sb.commit("sources")
        tok = sb.write_verdict(code_rev=base, review_scope=[{"file": LIB_REL}])
        sb.commit("verdict")
        rc, out = sb.run_gate(tok)
        self.assertEqual(rc, 1, out)
        self.assertIn("not a path", out)

    def test_the_accepted_token_REPORTS_the_scope_it_enforced(self):
        """An authorization that does not ship the scope it checked is unfalsifiable (BEN-077).

        Asserted on the gate's OUTPUT, not on its source text: `run_p4_standard.sh:99` echoes this
        line, so this is what a reader of the run log actually gets. With two declared paths, one
        of which is already on the sandbox surface, exactly one is beyond it -- so the counts can
        contradict each other if the union is ever computed wrongly."""
        sb, tok = self._clean_pass(review_scope=["docs/unrelated.md", LIB_REL])
        rc, out = sb.run_gate(tok)
        self.assertEqual(rc, 0, out)
        self.assertIn("UNION of the standard-P4 EXECUTION surface (2 tracked paths)", out)
        self.assertIn("declared review_scope (2 declared, 1 beyond the surface)", out)

    def test_MUTATION_prefix_gate_ACCEPTS_the_narrow_scope(self):
        """THE NEGATIVE CONTROL for #4. Restore verbatim-scope semantics -- declared list wins,
        surface consulted only when nothing is declared -- and the identical verdict, whose
        p4_lib.py demonstrably changed after the PASS, is AUTHORIZED."""
        sb, tok = self._narrow_scope_then_surface_drift(mutations=PREFIX_VERBATIM_SCOPE)
        rc, out = sb.run_gate(tok)
        self.assertEqual(rc, 0, f"pre-fix gate should have authorized this: {out}")
        self.assertIn("TOKEN-OK", out)


class Defect4b_ShellInvokedScriptsAreOnTheSurface(unittest.TestCase):
    """#4 second half: the surface walked the IMPORT graph and then added only `run_p4_*.sh`, so
    a module a shell driver INVOKES was reached by neither leg. Measured by repair-8: the fallback
    surface was 18 modules and `p3s_manifest_summary.py` was not among them."""

    SHELL_INVOKED = ("nd-unfolding/p3s_manifest_summary.py",
                     "2d-unfolding/uq/hadd_universes_full.py")

    def test_the_shell_invoked_scripts_are_in_the_surface(self):
        surf = P.standard_p4_execution_surface()
        for mod in self.SHELL_INVOKED:
            self.assertIn(mod, surf, f"{mod} is invoked by a shell driver but is off the surface")

    def test_each_named_script_is_really_invoked_by_a_tracked_driver(self):
        """Guards against the test passing because the surface grew for an unrelated reason: the
        claim is that a DRIVER names it, so read the drivers."""
        drivers = {p: (REPO / p).read_text()
                   for p in P.standard_p4_execution_surface() if p.endswith(".sh")}
        self.assertTrue(drivers)
        for mod in self.SHELL_INVOKED:
            base = os.path.basename(mod)
            self.assertTrue(any(base in t for t in drivers.values()),
                            f"{base} is named by no tracked run_p4_* driver")

    def test_the_resolver_invents_nothing(self):
        """Every path it returns is tracked; an unresolvable token is dropped, not guessed."""
        tracked = set(subprocess.check_output(["git", "ls-files"], cwd=str(REPO),
                                              text=True).splitlines())
        drivers = [p for p in P.standard_p4_execution_surface() if p.endswith(".sh")]
        found = P._shell_invoked_scripts(drivers, tracked)
        self.assertTrue(found)
        self.assertTrue(found <= tracked, f"invented paths: {sorted(found - tracked)}")

    def test_MUTATION_prefix_surface_OMITS_the_shell_invoked_scripts(self):
        """THE NEGATIVE CONTROL for #4's second half: with the shell-scan leg removed, the surface
        is the 18-module set repair-8 measured and the named module is absent."""
        mut = _mutated_lib([(LIB_REL,
                             "    roots += sorted(_shell_invoked_scripts(shell, tracked) "
                             "- set(roots))",
                             "    roots += []")])
        surf = mut.standard_p4_execution_surface()
        self.assertEqual(len(surf), 18, f"repair-8 measured 18; got {len(surf)}: {surf}")
        for mod in self.SHELL_INVOKED:
            self.assertNotIn(mod, surf, "pre-fix surface should omit it -- that was the defect")
        self.assertLess(len(surf), len(P.standard_p4_execution_surface()))


def _in_dir(root, fn, *args):
    """Run a `p4_lib` helper against `root` instead of this checkout, and restore the roots.

    The helpers resolve paths through the module-level `REPO_ROOT`, so this is the seam; nothing
    about the function under test is rewritten. Restored in a `finally` so a failure here cannot
    leak into another test -- repair-8 triaged one real case of test-order pollution in this
    suite directory and it took an isolation run to see it."""
    old_root, old_path = P.REPO_ROOT, P.REPO_ROOT_PATH
    P.REPO_ROOT, P.REPO_ROOT_PATH = str(root), Path(root)
    try:
        return fn(*args)
    finally:
        P.REPO_ROOT, P.REPO_ROOT_PATH = old_root, old_path


def _mutated_lib(mutations):
    """Import a private copy of p4_lib.py with `mutations` applied, still pointed at THIS repo.

    `REPO_ROOT` is derived from the module file's own location, so a copy in a temp directory
    would otherwise resolve to a non-repository and silently take the git-unavailable fallback
    path -- i.e. the mutation would be tested against the wrong code. The two roots are therefore
    restored explicitly after import."""
    src = (REPO / LIB_REL).read_text()
    for _rel, old, new in mutations:
        assert old in src, f"mutation anchor not found in p4_lib.py: {old[:70]!r}"
        assert src.count(old) == 1, f"ambiguous mutation anchor: {old[:70]!r}"
        src = src.replace(old, new)
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "p4_lib.py"
        p.write_text(src)
        spec = importlib.util.spec_from_file_location("_mut_p4_lib_repair9", p)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
    mod.REPO_ROOT = str(REPO)
    mod.REPO_ROOT_PATH = Path(REPO)
    return mod


if __name__ == "__main__":
    unittest.main(verbosity=2)
