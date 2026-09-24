#!/usr/bin/env python3
"""KNOWN_ISSUES #61 and #62 -- two P4 member/scope defects, each with a negative control.

#61  `p4_lib.standard_p4_execution_surface()` resolved the `.py` scripts a shell driver INVOKES
     but never a shell file it `source`s, so `nd-unfolding/lib_member_resume.sh` (sourced by
     `run_p4_unfold_std.sh`; supplies `mr_declared`, the baseline-overwrite guard's predicate) and
     `setup_salloc_env.sh` (sourced by `run_p4_standard.sh`) were off the surface, and a PASS token
     stayed valid across edits to them. Tested END TO END: the live gate, in a throwaway git repo,
     must refuse a token after a committed edit to a sourced library -- and the pre-fix surface
     (source leg removed) must accept the identical token.

#62  The shell convention (`lib_member_resume.sh`) scopes by DECLARED-NESS: unset -> baseline paths,
     an explicit `0` -> `member_k000000`. `p4_evidence._member_scope` scoped by VALUE, so an
     explicit 0 returned the baseline path. Both implementations are RUN here at offsets unset, 0,
     N and -N and must agree byte-for-byte; the shell side is the canonical one (its header: "THE
     ANCHOR IS NOT AN EXCEPTION").
"""
import os
import subprocess
import sys
import unittest
from pathlib import Path

ND = Path(__file__).resolve().parents[1]
REPO = ND.parent
sys.path.insert(0, str(ND))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p4_lib as P                                                        # noqa: E402
from test_p4_token_gate_scope_and_rev import (                            # noqa: E402
    LIB_REL, _SandboxCase, _mutated_lib)

SOURCED_LEG = ("    shell += sorted(_shell_sourced_scripts(shell, tracked) - set(shell))",
               "    shell += []")
DRIVER_REL = "nd-unfolding/run_p4_ki61_probe.sh"
SOURCED_REL = "nd-unfolding/lib_ki61_probe.sh"
NESTED_REL = "lib_ki61_nested.sh"


# ------------------------------------------------------------------------------------------ #61
class KI61_SourcedShellLibrariesAreOnTheSurface(unittest.TestCase):

    def test_the_live_sourced_libraries_are_on_the_surface(self):
        surf = P.standard_p4_execution_surface()
        for rel in ("nd-unfolding/lib_member_resume.sh", "setup_salloc_env.sh"):
            self.assertIn(rel, surf, f"{rel} is sourced by a run_p4_* driver but is off the surface")

    def test_each_is_really_sourced_by_a_driver_on_the_surface(self):
        """Guards against passing because the surface grew for an unrelated reason."""
        drivers = {p: (REPO / p).read_text() for p in P.standard_p4_execution_surface()
                   if p.startswith("nd-unfolding/run_p4_") and p.endswith(".sh")}
        self.assertIn('source "${ND}/lib_member_resume.sh"',
                      drivers["nd-unfolding/run_p4_unfold_std.sh"])
        self.assertIn('source "${REPO}/setup_salloc_env.sh"',
                      drivers["nd-unfolding/run_p4_standard.sh"])

    def test_the_resolver_invents_nothing_and_ignores_prose(self):
        tracked = set(subprocess.check_output(["git", "ls-files"], cwd=str(REPO),
                                              text=True).splitlines())
        drivers = [p for p in tracked if p.startswith("nd-unfolding/run_p4_") and p.endswith(".sh")]
        found = P._shell_sourced_scripts(drivers, tracked)
        self.assertTrue(found <= tracked, f"invented paths: {sorted(found - tracked)}")
        self.assertIn("nd-unfolding/lib_member_resume.sh", found)

    def test_MUTATION_prefix_surface_OMITS_the_sourced_libraries(self):
        mut = _mutated_lib([(LIB_REL, *SOURCED_LEG)])
        surf = mut.standard_p4_execution_surface()
        self.assertNotIn("nd-unfolding/lib_member_resume.sh", surf,
                         "pre-fix surface should omit it -- that was KNOWN_ISSUES #61")
        self.assertNotIn("setup_salloc_env.sh", surf)


class KI61_AnEditToASourcedLibraryVoidsTheToken(_SandboxCase):
    """The property #61 is about, driven through the real gate: a verdict with no declared scope,
    then a committed edit to a library that a run_p4_* driver sources -- TRANSITIVELY, one hop
    further -- must be refused by rule 4b."""

    def _sourced_lib_drift(self, mutations=(), edit=SOURCED_REL):
        sb = self._sandbox(mutations)
        (sb.dir / DRIVER_REL).write_text(
            '#!/bin/bash\nND="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"\n'
            '# shellcheck source=lib_ki61_probe.sh\nsource "${ND}/lib_ki61_probe.sh"\n'
            'mr_declared || echo baseline\n')
        (sb.dir / SOURCED_REL).write_text(
            '. "${ND}/../lib_ki61_nested.sh"\n'
            'mr_declared() { [[ -n "${MNV_EST_SEED_OFFSET:-}" ]]; }\n')
        (sb.dir / NESTED_REL).write_text('nested_helper() { :; }\n')
        base = sb.commit("sources")
        tok = sb.write_verdict(code_rev=base)
        sb.commit("verdict")
        p = sb.dir / edit
        p.write_text(p.read_text().rstrip("\n")
                     + "\nmr_declared() { true; }   # silences the baseline guard\n")
        sb.commit("another lane edits a sourced library after the PASS")
        return sb, tok

    def test_a_committed_edit_to_a_sourced_library_is_refused(self):
        sb, tok = self._sourced_lib_drift()
        rc, out = sb.run_gate(tok)
        self.assertEqual(rc, 1, out)
        self.assertIn("have CHANGED at HEAD", out)
        self.assertIn(SOURCED_REL, out)

    def test_a_committed_edit_to_a_TRANSITIVELY_sourced_library_is_refused(self):
        sb, tok = self._sourced_lib_drift(edit=NESTED_REL)
        rc, out = sb.run_gate(tok)
        self.assertEqual(rc, 1, out)
        self.assertIn("have CHANGED at HEAD", out)
        self.assertIn(NESTED_REL, out)

    def test_MUTATION_prefix_gate_ACCEPTS_the_sourced_library_edit(self):
        """THE NEGATIVE CONTROL: without the source leg the identical drift is authorized."""
        sb, tok = self._sourced_lib_drift(mutations=[(LIB_REL, *SOURCED_LEG)])
        rc, out = sb.run_gate(tok)
        self.assertEqual(rc, 0, f"pre-fix gate should have authorized this: {out}")
        self.assertIn("TOKEN-OK", out)


# ------------------------------------------------------------------------------------------ #62
_UNSET = object()
PATHS = ("/repo/nd-unfolding/active_universe_5d/standard/unfolds",
         "/repo/nd-unfolding/active_universe_5d/standard/evidence")


def _shell_scope(path, offset):
    env = {k: v for k, v in os.environ.items() if k != "MNV_EST_SEED_OFFSET"}
    if offset is not _UNSET:
        env["MNV_EST_SEED_OFFSET"] = str(offset)
    r = subprocess.run(["bash", "-c", 'source "$1"; _mr_insert "$2"', "_",
                        str(ND / "lib_member_resume.sh"), path],
                       env=env, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return r.stdout


# The pre-fix VALUE branch, rebuilt: `default=0`, and "declared" meaning "non-zero".
PREFIX_VALUE_BRANCH = [
    ('_ap.add_argument("--est-seed-offset", type=int, default=None,',
     '_ap.add_argument("--est-seed-offset", type=int, default=0,'),
    ("EST_SEED_OFFSET_DECLARED = _ARGS.est_seed_offset is not None",
     "EST_SEED_OFFSET_DECLARED = _ARGS.est_seed_offset != 0"),
]


def _evidence_scope(path, offset, mutations=()):
    """p4_evidence's OWN argv -> path mapping, executed: its argparse block and `_member_scope`
    are cut from the live file (it imports ROOT at the top, so it cannot be imported here) and run
    with the argv the orchestrator/probe would pass."""
    src = (ND / "p4_evidence.py").read_text()
    for old, new in mutations:
        assert src.count(old) == 1, f"mutation anchor gone stale: {old[:60]!r}"
        src = src.replace(old, new)
    start = src.index("_ap = argparse.ArgumentParser(")
    stop = src.index("UDIR = _member_scope(")
    argv = ["p4_evidence.py"] + ([] if offset is _UNSET else ["--est-seed-offset", str(offset)])
    ns = {"P": P, "argparse": __import__("argparse")}
    old = sys.argv
    sys.argv = argv
    try:
        exec(compile(src[start:stop], "p4_evidence.py[argv+scope]", "exec"), ns)
    finally:
        sys.argv = old
    return ns["_member_scope"](path)


class KI62_ShellAndPythonMemberScopingAgree(unittest.TestCase):

    CASES = ((_UNSET, None), (0, "member_k000000"), (1200, "member_k001200"),
             (-5, "member_kneg000005"))

    def test_both_implementations_agree_at_unset_zero_and_N(self):
        for offset, member in self.CASES:
            for path in PATHS:
                with self.subTest(offset=offset, path=path):
                    sh, py = _shell_scope(path, offset), _evidence_scope(path, offset)
                    self.assertEqual(sh, py, f"shell and Python disagree at offset {offset!r}")
                    want = path if member is None else path.replace(
                        "/nd-unfolding/", f"/nd-unfolding/mii/{member}/", 1)
                    self.assertEqual(py, want)

    def test_the_library_twin_matches_the_shell_on_relative_paths_too(self):
        for offset, _member in self.CASES:
            with self.subTest(offset=offset):
                arg = None if offset is _UNSET else offset
                self.assertEqual(P.member_scope_path("uq_5d/x.npz", arg),
                                 _shell_scope("uq_5d/x.npz", offset))

    def test_the_k0_member_candidate_root_is_the_member_root_not_the_baseline(self):
        """The downstream half: a member_k000000 manifest must write its candidate under the
        member tree, and a baseline candidate path must be REFUSED for it."""
        member = f"{P.ND_ROOT}/mii/member_k000000/{P.CANDIDATE_SUBDIR}/c.root"
        base = f"{P.ND_ROOT}/{P.CANDIDATE_SUBDIR}/c.root"
        self.assertTrue(P.member_declared_in_path(member))
        self.assertFalse(P.member_declared_in_path(base))
        P.require_candidate_path(member, expected_offset=0, declared=True)
        with self.assertRaises(BaseException):
            P.require_candidate_path(base, expected_offset=0, declared=True)
        P.require_candidate_path(base, expected_offset=0)          # legacy default unchanged
        with self.assertRaises(BaseException):
            P.require_candidate_path(member, expected_offset=0)

    def test_MUTATION_the_value_branch_DISAGREES_at_zero_and_only_there(self):
        """THE NEGATIVE CONTROL: rebuild the pre-fix value-based form and run the same matrix.
        It must disagree with the shell at an explicit 0 -- the #62 measurement -- and agree at
        unset and N, so this test cannot be green because everything disagrees."""
        for offset, _member in self.CASES:
            for path in PATHS:
                with self.subTest(offset=offset, path=path):
                    sh = _shell_scope(path, offset)
                    old = _evidence_scope(path, offset, mutations=PREFIX_VALUE_BRANCH)
                    if offset == 0:
                        self.assertNotEqual(sh, old)
                        self.assertEqual(old, path, "pre-fix Python read the BASELINE at 0")
                    else:
                        self.assertEqual(sh, old)


if __name__ == "__main__":
    unittest.main(verbosity=2)
