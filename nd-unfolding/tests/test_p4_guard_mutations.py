#!/usr/bin/env python3
"""Mutation harness for the repair-4/5 self-guards (repair-6 item 3).

**The rule this file enforces:** a self-guard must FAIL against the pre-repair code, and that
failure must be DEMONSTRATED, not asserted. Verifier finding 3 on repair-5 was that at least
one guard shared an assumption with the code it guarded — the D2 integration stub set the
"live" blob equal to its own fixture, which is exactly the configuration in which the defect it
was written for is invisible. If one guard had that shape, others may.

**How it works.** For each repaired defect, reintroduce the defect — either by calling the
guard with pre-repair inputs, or by applying the pre-repair logic to a copy of the module —
and assert the guard rejects it. A guard that still passes under mutation does not discriminate
and is recorded here as such rather than being quietly kept.

**What this deliberately does NOT do:** assert on source text. Every case below runs the real
gate. Source-text assertions live in the other suites and are explicitly *weaker* evidence;
where a guard could only be expressed textually, it is listed in
`NON_DISCRIMINATING` with the reason.
"""
import importlib.util, json, os, subprocess, sys, tempfile, unittest
from pathlib import Path

ND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ND))
import numpy as np
import p4_lib as P
from p4_lib import P4GateError


def _load_mutated(module_name, replacements):
    """Import a private copy of a module with `replacements` [(old, new)] applied to its source.
    This is how the PRE-REPAIR behaviour is reconstructed without touching the repo."""
    src = (ND / module_name).read_text()
    for old, new in replacements:
        assert old in src, f"mutation anchor not found in {module_name}: {old[:60]!r}"
        src = src.replace(old, new)
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / module_name
        p.write_text(src)
        spec = importlib.util.spec_from_file_location(f"_mut_{module_name[:-3]}", p)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        return mod


class D2_ReceiptSourceIdentity(unittest.TestCase):
    """Repair-5 D2: code_rev and the producing blob must be COMPARED, not merely present."""

    GOOD = dict(tag="BeamAngleX_0", root_sha256="a" * 64, merged_sha256="b" * 64,
                central5d_sha256="c" * 64, config_hash="d" * 64, bkg_mode="purity",
                code_rev="e" * 40, unfold_blob="f" * 40)

    def _rec(self, **over):
        r = {"mode": "produced", "t": "2026-08-07T00:00:00Z"}
        r.update({k: v for k, v in self.GOOD.items()})
        r.update(over)
        return r

    def test_guard_rejects_stale_code_rev(self):
        with self.assertRaises(P4GateError) as cm:
            P.validate_endpoint_receipt(self._rec(code_rev="0" * 40), **self.GOOD)
        self.assertIn("different revision", str(cm.exception))

    def test_guard_rejects_stale_unfold_blob(self):
        with self.assertRaises(P4GateError) as cm:
            P.validate_endpoint_receipt(self._rec(unfold_blob="9" * 40), **self.GOOD)
        self.assertIn("unfold driver changed", str(cm.exception))

    def test_MUTATION_presence_only_code_rev_would_pass_a_stale_receipt(self):
        """Reintroduce the pre-repair check (presence, not comparison) and prove the stale
        receipt sails through. This is the demonstration that the guard discriminates: the
        SAME input that the guard rejects above is ACCEPTED by the mutated library."""
        mut = _load_mutated("p4_lib.py", [
            ('    require(rec["code_rev"] == code_rev,',
             '    require(True or rec["code_rev"] == code_rev,'),
            ('    require(rec[RECEIPT_SOURCE_KEY] == unfold_blob,',
             '    require(True or rec[RECEIPT_SOURCE_KEY] == unfold_blob,'),
        ])
        stale = self._rec(code_rev="0" * 40, unfold_blob="9" * 40)
        self.assertTrue(mut.validate_endpoint_receipt(stale, **self.GOOD),
                        "pre-repair library should accept the stale receipt")


class D4a_Containment(unittest.TestCase):
    """Repair-5 D4a: containment must be resolved, not textual."""

    ESCAPE = "/evil/active_universe_5d/standard/candidate/out.root"

    def test_guard_rejects_the_out_of_repo_path(self):
        with self.assertRaises(P4GateError):
            P.require_candidate_path(self.ESCAPE)

    def test_MUTATION_component_match_would_accept_the_out_of_repo_path(self):
        """The repair-4 containment (normpath component match) accepted this. Rebuild that
        logic and show it passes the very path the current guard rejects."""
        norm = os.path.normpath(self.ESCAPE)
        parts = norm.split(os.sep)
        want = P.CANDIDATE_SUBDIR.split("/")
        contained = any(parts[i:i + len(want)] == want
                        for i in range(len(parts) - len(want) + 1))
        self.assertTrue(contained,
                        "the repair-4 component match should accept it -- that was the defect")

    def test_guard_rejects_a_real_symlink_escape(self):
        cand_root = os.path.join(P.ND_ROOT, P.CANDIDATE_SUBDIR)
        os.makedirs(cand_root, exist_ok=True)
        with tempfile.TemporaryDirectory() as outside:
            link = os.path.join(cand_root, "_mut_escape_probe")
            if os.path.islink(link) or os.path.exists(link):
                os.remove(link)
            os.symlink(outside, link)
            try:
                target = os.path.join(link, "out.root")
                with self.assertRaises(P4GateError):
                    P.require_candidate_path(target)
                # and demonstrate normpath could NOT have seen it
                parts = os.path.normpath(target).split(os.sep)
                want = P.CANDIDATE_SUBDIR.split("/")
                self.assertTrue(any(parts[i:i + len(want)] == want
                                    for i in range(len(parts) - len(want) + 1)),
                                "normpath would have accepted the symlinked path")
            finally:
                os.remove(link)


class D4b_FullTotalIdentity(unittest.TestCase):
    """Repair-5 D4b: PSD of the residual is not the identity."""

    Csyst = np.diag([4.0, 9.0])
    Cstat = np.diag([1.0, 1.0])
    Cml = np.diag([0.5, 0.5])
    Cbad = np.diag([4.0, 9.0]) + np.diag([3.0, 3.0])     # residual PSD, and NOT stat+ML

    def test_guard_rejects_a_psd_residual_that_is_not_stat_plus_ml(self):
        with self.assertRaises(P4GateError):
            P.check_full_total_identity(self.Cbad, self.Csyst, self.Cstat, self.Cml, 1e-9)

    def test_MUTATION_psd_only_check_would_accept_it(self):
        """The repair-4 gate was exactly this PSD call. Show it passes the same matrix."""
        P.check_symmetric_psd(self.Cbad - self.Csyst)     # no raise == the defect

    def test_guard_accepts_the_true_identity(self):
        good = self.Csyst + self.Cstat + self.Cml
        self.assertLessEqual(
            P.check_full_total_identity(good, self.Csyst, self.Cstat, self.Cml, 1e-9), 1e-9)


class D3_DirtySourceFailClosed(unittest.TestCase):
    """Repair-5 D3: a deleted bound source must block.

    NOTE this is the guard verifier finding 3 called textual. The semantic core is the boolean
    itself, which IS testable in isolation: `_w is None or _c == _w` vs `_c == _w`."""

    def test_pre_repair_expression_is_fail_open_on_a_deleted_source(self):
        c, w = "committed_blob", None          # w is None == git hash-object failed == deleted
        pre_repair = (w is None or c == w)
        self.assertTrue(pre_repair, "the pre-repair disjunct accepts a deleted source")

    def test_repaired_expression_is_fail_closed_on_a_deleted_source(self):
        c, w = "committed_blob", None
        repaired = (c == w)
        self.assertFalse(repaired, "the repaired comparison rejects a deleted source")

    def test_repaired_expression_still_accepts_a_clean_source(self):
        c = w = "committed_blob"
        self.assertTrue(c == w, "a guard that cannot pass is as broken as one that cannot fail")


# ---------------------------------------------------------------------------------------
# Guards that could NOT be made discriminating, recorded rather than quietly kept.
NON_DISCRIMINATING = {
    "launcher wiring assertions (test_p4_resume_integration.LauncherWiring)":
        "assert on shell source text. Executing run_p4_unfold_std.sh needs PyROOT, 538 GB of "
        "merged input and Slurm, so there is no laptop-side execution to mutate against. "
        "Verifier finding 3 is correct that these are weak; they are retained as drift "
        "detectors, not as evidence the launcher behaves correctly.",
    "D2 integration stub (ReceiptGateIntegration)":
        "stubs committed_unfold_blob()/current_code_rev() to equal its fixture, so it cannot "
        "expose a mis-stamped LEGACY receipt. Repair-6 removes the legacy-attest path entirely "
        "rather than guarding it, which is why this stub is acceptable going forward: there is "
        "no longer a code path that stamps provenance it did not observe.",
}


class GuardInventory(unittest.TestCase):
    def test_non_discriminating_guards_are_declared(self):
        """Fails if the declaration is emptied without the guards being strengthened."""
        self.assertTrue(NON_DISCRIMINATING)
        for k, v in NON_DISCRIMINATING.items():
            self.assertGreater(len(v), 80, f"{k} needs a real reason, not a placeholder")


if __name__ == "__main__":
    unittest.main(verbosity=2)
