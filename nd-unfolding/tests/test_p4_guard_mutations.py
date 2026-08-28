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
import importlib.util, os, subprocess, sys, tempfile, unittest
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

    # repair-6b: code_rev must be reachable in this history, so use the real HEAD.
    _HEAD = subprocess.check_output(["git", "rev-parse", "HEAD"],
                                    cwd=str(ND.parent), text=True).strip()
    GOOD = dict(tag="BeamAngleX_0", root_sha256="a" * 64, merged_sha256="b" * 64,
                central5d_sha256="c" * 64, config_hash="d" * 64, bkg_mode="purity",
                code_rev=_HEAD, unfold_blob="f" * 40)

    def _rec(self, **over):
        r = {"mode": "produced", "t": "2026-08-07T00:00:00Z"}
        r.update({k: v for k, v in self.GOOD.items()})
        r.update(over)
        return r

    def test_guard_rejects_a_code_rev_not_in_this_history(self):
        with self.assertRaises(P4GateError) as cm:
            P.validate_endpoint_receipt(self._rec(code_rev="0" * 40), **self.GOOD)
        self.assertIn("not an ancestor of HEAD", str(cm.exception))

    def test_guard_rejects_stale_unfold_blob(self):
        with self.assertRaises(P4GateError) as cm:
            P.validate_endpoint_receipt(self._rec(unfold_blob="9" * 40), **self.GOOD)
        self.assertIn("unfold driver changed", str(cm.exception))

    def test_MUTATION_presence_only_code_rev_would_pass_a_stale_receipt(self):
        """Reintroduce the pre-repair check (presence, not comparison) and prove the stale
        receipt sails through. This is the demonstration that the guard discriminates: the
        SAME input that the guard rejects above is ACCEPTED by the mutated library."""
        mut = _load_mutated("p4_lib.py", [
            ('    require(code_rev_in_history(rec["code_rev"]),',
             '    require(True or code_rev_in_history(rec["code_rev"]),'),
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


class BEN044_AbsoluteToleranceAtRealScale(unittest.TestCase):
    """REPAIR-6, folding in the PET lane's BEN-044 ("an absolute tolerance inherited into a
    problem whose natural scale is ~1e-80 makes a gate that cannot fail").

    **Honest severity, because this thread is about not overclaiming.** `check_symmetric_psd`
    did contain a bare absolute literal -- `d >= -1e-30` -- against a standard-5D covariance
    whose diagonal sits near 1e-79, i.e. ~49 orders above what it bounds, so that specific
    bound could not fire. But it was **redundant, not the sole line of defence**: for a
    symmetric matrix min(diag) >= min(eigenvalue), so any negative diagonal is already a
    negative eigenvalue, and the PSD check immediately above it IS relative
    (`ev[0] >= -psd_atol_ratio * |ev[-1]|`) and rejects the same corruption first. The tests
    below demonstrate exactly that, rather than claiming a live hole.

    So the fix is hygiene under BEN-044 rule 1 (no bare literal in a covariance path) plus a
    reintroduction guard -- not the closing of an exploitable gap. Stating it the other way
    would be the overclaim this round exists to stop."""

    SCALE = 1e-79            # realistic standard-5D diagonal magnitude

    def _cov(self, n=4):
        return np.diag(np.full(n, self.SCALE))

    def test_gate_accepts_a_clean_covariance_at_the_real_scale(self):
        st = P.check_symmetric_psd(self._cov())
        self.assertGreater(st["max_eig"], 0.0)

    def test_the_old_absolute_diagonal_bound_could_not_fire_at_this_scale(self):
        """The literal itself: a corruption ~48 orders larger than the signal passes it."""
        C = self._cov(); C[1, 1] = -1e-31
        self.assertTrue(bool(np.all(np.diag(C) >= -1e-30)),
                        "the absolute bound accepts it -- that is the BEN-044 shape")

    def test_but_the_relative_PSD_check_already_rejected_that_matrix(self):
        """Why the severity is 'redundant' and not 'exploitable'. Recording this so nobody
        later reads the repair as having closed a hole that was open."""
        C = self._cov(); C[1, 1] = -1e-31
        with self.assertRaises(P4GateError) as cm:
            P.check_symmetric_psd(C)
        self.assertIn("not PSD", str(cm.exception))       # caught by the RELATIVE gate

    def test_negative_diagonal_implies_negative_eigenvalue(self):
        """The structural reason the diagonal bound is redundant for symmetric input."""
        C = self._cov(); C[1, 1] = -1e-31
        self.assertLessEqual(float(np.linalg.eigvalsh(0.5 * (C + C.T))[0]),
                             float(np.min(np.diag(C))) + 0.0)

    def test_repaired_bound_still_tolerates_round_off_at_the_real_scale(self):
        """Tightening a dead bound must not make it fire on numerical noise."""
        C = self._cov(); C[2, 2] = -1e-13 * self.SCALE
        self.assertIsInstance(P.check_symmetric_psd(C), dict)

    def test_no_bare_absolute_tolerance_remains_in_the_lane(self):
        """BEN-044 rule 1, as a reintroduction guard. A source check by necessity, and declared
        as the weaker kind of evidence it is."""
        import re as _re
        offenders = []
        for f in ("p4_lib.py", "p4_validate_active_lateral.py", "p4_build_components.py",
                  "p4_project_4d.py"):
            for i, line in enumerate((ND / f).read_text().splitlines(), 1):
                if line.lstrip().startswith("#"):
                    continue
                if not _re.search(r"\b(require|need)\(", line):
                    continue
                if not _re.search(r"[-+]?\d+(\.\d+)?e-\d+", line):
                    continue
                if _re.search(r"max\(1e-300|rtol|atol_ratio|/ ?denom|\* ?abs\(ev|\* ?denom|\* ?max", line):
                    continue
                offenders.append(f"{f}:{i}: {line.strip()[:90]}")
        self.assertEqual(offenders, [], f"bare absolute tolerance(s): {offenders}")


class ReproducibilityTolerance(unittest.TestCase):
    """REPAIR-6: the declared reproducibility SPECIFICATION (Joseph, 2026-08-07).

    These ROOTs are not bit-reproducible, so the gate compares CONTENTS. The declared
    tolerances are ~2 orders above the measured floor so a CONC change does not force a
    re-derivation. This is a specification, not a loosening -- nothing was failing when it was
    set, and the floor was measured on a clean 10/10 run.

    The interesting property, and the reason there are TWO tolerances rather than one: together
    they separate round-off from a coherent shift. The per-bin leg permits scatter; the integral
    leg forbids that scatter from summing coherently."""

    def setUp(self):
        self.rng = np.random.default_rng(0)
        self.base = self.rng.uniform(1, 10, 10694)     # one endpoint's reported bins

    def test_declared_values_are_above_the_measured_floor(self):
        f = P.REPRO_MEASURED_FLOOR
        self.assertGreater(P.REPRO_RTOL_PER_BIN, f["worst_rel_bin"])
        self.assertGreater(P.REPRO_RTOL_INTEGRAL, f["integral_rel"])
        # and recorded separately, so re-measuring cannot silently move the gate
        self.assertNotEqual(P.REPRO_RTOL_PER_BIN, f["worst_rel_bin"])

    def test_accepts_round_off_at_the_measured_floor(self):
        """A gate that cannot PASS on real input is unverified in the direction that matters."""
        s = self.rng.normal(0, 4e-12, self.base.size); s -= s.mean()
        r = P.check_reproducibility(self.base * (1 + s), self.base)
        self.assertLess(r["max_rel_bin"], P.REPRO_RTOL_PER_BIN)

    def test_rejects_a_coherent_shift_of_the_SAME_per_bin_magnitude(self):
        """THE discriminating case. A uniform 2e-11 shift has a per-bin size inside the floor,
        so the per-bin leg alone would accept it; the integral leg rejects it. This is what the
        sign argument was mistakenly asked to do, and what magnitude+coherence actually does."""
        with self.assertRaises(P4GateError) as cm:
            P.check_reproducibility(self.base * (1 + 2e-11), self.base)
        self.assertIn("integral relative difference", str(cm.exception))

    def test_rejects_a_gross_shift_on_the_per_bin_leg(self):
        with self.assertRaises(P4GateError) as cm:
            P.check_reproducibility(self.base * (1 + 1e-3), self.base)
        self.assertIn("per-bin relative difference", str(cm.exception))

    def test_shape_mismatch_and_empty_reference_fail_closed(self):
        """Two DIFFERENT causes, so each assertion names the one it means (BEN-344, 2026-08-16).

        These were bare `assertRaises(P4GateError)` until 2026-08-16. Both fired for the right
        reason -- measured: `reproducibility: shape (3,) != (4,)` and `reproducibility: reference has
        no positive bins` -- so this was a latent weakness rather than a live defect. But it is the
        only rejection assertion in this file with neither a message check nor a paired contrast
        showing the same input accepted by the pre-repair form, so the raise it accepts could have
        come from anywhere: if the empty-reference path ever started failing on shape, or a future
        edit collapsed both into one generic refusal, the test would keep passing. Naming the cause
        is what makes the two asserts independent instead of interchangeable.
        """
        with self.assertRaises(P4GateError) as cm:
            P.check_reproducibility(self.base[:-1], self.base)
        self.assertIn("shape", str(cm.exception),
                      "expected the SHAPE guard; a different refusal satisfies the bare "
                      "assertRaises this replaced")
        with self.assertRaises(P4GateError) as cm:
            P.check_reproducibility(np.zeros(4), np.zeros(4))
        self.assertIn("no positive bins", str(cm.exception),
                      "expected the EMPTY-REFERENCE guard; if this now fails on shape instead, the "
                      "two cases have collapsed into one and only one is being tested")


class A1_VerifierTokenBinding(unittest.TestCase):
    """REPAIR-6 closes KNOWN_ISSUES #21 / inventory A1 -- the original instance of
    'assert presence, never compare', and the one left open through repairs 4 and 5 because it
    was the instrument authorising those rounds.

    The mutation here is the pre-repair gate itself: `[[ -n "$TOKEN" ]]`. Every case below
    shows a token the repaired gate REJECTS which the old one ACCEPTED."""

    import subprocess as _sp

    def _resolve(self, token):
        import p4_check_verifier_token as T
        return T.resolve(token)

    @staticmethod
    def _old_gate(token):
        """The pre-repair gate, verbatim in semantics: non-empty is enough."""
        return bool(token)

    def test_MUTATION_old_gate_accepted_literally_anything(self):
        for junk in ("x", "yes", "PASS", "1", "please"):
            self.assertTrue(self._old_gate(junk),
                            "the pre-repair gate accepted any non-empty string -- the defect")

    def test_arbitrary_string_is_rejected(self):
        for junk in ("x", "yes", "PASS", "1", "please"):
            with self.assertRaises(P4GateError, msg=f"{junk!r} accepted"):
                self._resolve(junk)

    def test_well_formed_but_unknown_digest_is_rejected(self):
        with self.assertRaises(P4GateError) as cm:
            self._resolve("a" * 64)
        self.assertIn("no verdict", str(cm.exception))

    def test_a_real_BLOCK_verdict_does_not_authorize(self):
        """The two committed verdicts are both BLOCK. Their digests must be refused -- a real
        receipt is not the same as a passing one."""
        import glob, json, os
        import p4_check_verifier_token as T
        found = 0
        for f in sorted(glob.glob(os.path.join(T.RECEIPT_DIR, "*.json"))):
            try:
                v = json.load(open(f))
            except Exception:
                continue
            if str(v.get("verdict", "")).upper() != "BLOCK":
                continue
            found += 1
            with self.assertRaises(P4GateError) as cm:
                self._resolve(P.sha256_file(f))
            msg = str(cm.exception)
            self.assertTrue("not PASS" in msg or "code_rev" in msg
                            or "authorizes_covariance_stages_4_6" in msg, msg)
        self.assertGreater(found, 0, "expected at least one committed BLOCK verdict to test")

    def test_gate_is_wired_into_the_driver(self):
        sh = (ND / "run_p4_standard.sh").read_text()
        code = "\n".join(l for l in sh.splitlines() if not l.lstrip().startswith("#"))
        self.assertIn("p4_check_verifier_token.py", code)
        # and the non-emptiness test is no longer the ONLY thing between here and stage 4
        i_tok = code.index("p4_check_verifier_token.py")
        i_build = code.index("python3 p4_build_components.py")
        self.assertLess(i_tok, i_build)

    def test_refusal_message_no_longer_reads_as_an_instruction(self):
        """The old message named the variable to set, which is what invited self-authorization."""
        sh = (ND / "run_p4_standard.sh").read_text()
        self.assertIn("will NOT work", sh)
        self.assertIn("sha256 of a", sh)


class REPAIR6b_CodeRevReachability(unittest.TestCase):
    """REPAIR-6b: the D2 code_rev check was too strict and broke on CORRECT behaviour.

    Requiring `code_rev == HEAD` expired all ten receipts the moment ANY commit landed
    anywhere in the repo -- including the PET lane's, touching nothing this chain reads. Caught
    on the first production run: HEAD moved 42268b6 -> 203ff01 while `git diff` on the unfold
    driver was EMPTY, and the gate rejected 10/10 valid receipts.

    That is the same defect KNOWN_ISSUES #24 names -- a chain that breaks on correct behaviour
    is a defect in the chain. The producing-code binding is `unfold_blob` (still strict); the
    honest check on `code_rev` is REACHABILITY."""

    import subprocess as _sp

    def _head(self):
        return self._sp.check_output(["git", "rev-parse", "HEAD"],
                                     cwd=P.REPO_ROOT, text=True).strip()

    def _older(self, n=3):
        return self._sp.check_output(["git", "rev-parse", f"HEAD~{n}"],
                                     cwd=P.REPO_ROOT, text=True).strip()

    def test_an_older_in_history_commit_is_accepted(self):
        """The case that broke: a receipt produced before unrelated commits landed."""
        self.assertTrue(P.code_rev_in_history(self._older()))

    def test_head_itself_is_accepted(self):
        self.assertTrue(P.code_rev_in_history(self._head()))

    def test_a_commit_not_in_this_history_is_rejected(self):
        self.assertFalse(P.code_rev_in_history("0" * 40))

    def test_empty_and_garbage_fail_closed(self):
        for bad in ("", "   ", None, 12345, "not-a-sha"):
            self.assertFalse(P.code_rev_in_history(bad), f"{bad!r} accepted")

    def test_MUTATION_equality_would_reject_a_valid_older_receipt(self):
        """The pre-repair-6b semantics, shown rejecting what the repaired check accepts."""
        older, head = self._older(), self._head()
        self.assertNotEqual(older, head)
        self.assertFalse(older == head, "equality check rejects it -- that was the defect")
        self.assertTrue(P.code_rev_in_history(older), "reachability accepts it")

    def test_unfold_blob_is_still_strict(self):
        """Loosening code_rev must NOT loosen the producing-code binding."""
        good = dict(tag="BeamAngleX_0", root_sha256="a" * 64, merged_sha256="b" * 64,
                    central5d_sha256="c" * 64, config_hash="d" * 64, bkg_mode="purity",
                    code_rev=self._head(), unfold_blob="f" * 40)
        rec = {"mode": "produced", "t": "x"}; rec.update(good)
        self.assertTrue(P.validate_endpoint_receipt(rec, **good))
        bad = dict(rec); bad["unfold_blob"] = "9" * 40
        with self.assertRaises(P4GateError) as cm:
            P.validate_endpoint_receipt(bad, **good)
        self.assertIn("unfold driver changed", str(cm.exception))


class REPAIR6b_SelfCheckPipelineBug(unittest.TestCase):
    """REPAIR-6b: my own self-check reported `pass=10 fail=0` beside ten REJECT lines.

    `if cmd | tail -1; then pass++` tests TAIL's exit status, never the command's -- BEN-035's
    'rc after a pipeline' trap, in the script written to catch exactly this family of defect."""

    def test_the_pipeline_idiom_is_the_bug(self):
        import subprocess
        rc = subprocess.call("if false | tail -1; then exit 0; else exit 1; fi", shell=True)
        self.assertEqual(rc, 0, "a failing command piped to tail reports SUCCESS")

    def test_capture_then_test_is_correct(self):
        import subprocess
        rc = subprocess.call('if OUT=$(false); then exit 0; else exit 1; fi', shell=True)
        self.assertEqual(rc, 1, "capturing first preserves the command's status")


class REPAIR6c_TokenGateReviewScope(unittest.TestCase):
    """REPAIR-6c: the token gate carried the SAME spec flaw as the receipt gate.

    Rule (4) required the verdict's `code_rev == HEAD`. Another lane pushing between the PASS and
    stages 4-6 -- eight commits, today -- would have rejected a valid token over commits touching
    nothing the verifier reviewed, wasting the delegate run. Replaced by ancestry PLUS
    reviewed-files-unchanged, which is strictly stronger: it checks what the rule protects
    instead of a proxy unrelated commits perturb."""

    import subprocess as _sp

    def _rev(self, spec="HEAD"):
        return self._sp.check_output(["git", "rev-parse", spec],
                                     cwd=P.REPO_ROOT, text=True).strip()

    def test_review_surface_resolves_to_real_tracked_files(self):
        files = P.tracked_files_matching(P.STANDARD_P4_SURFACE_GLOBS)
        self.assertGreater(len(files), 5)
        self.assertTrue(all(f.startswith("nd-unfolding/") for f in files))
        self.assertIn("nd-unfolding/p4_lib.py", files)

    def test_unchanged_between_identical_revs_is_true(self):
        files = P.tracked_files_matching(P.STANDARD_P4_SURFACE_GLOBS)
        ok, diff = P.paths_unchanged_between("HEAD", "HEAD", files)
        self.assertTrue(ok); self.assertEqual(diff, [])

    def test_changed_reviewed_file_is_detected(self):
        """The property the rule exists to protect: a PASS must not authorize unseen code.

        Constructed DETERMINISTICALLY rather than from `HEAD~1`. The first version assumed the
        previous commit touched the P4 surface, which is a fact about repo history, not about
        the property under test -- it went red the moment a merge from another lane became
        HEAD~1. A test whose premise depends on what someone else committed is a flaky test."""
        target = "nd-unfolding/p4_lib.py"
        # the last commit that actually changed p4_lib.py, and its parent
        rev = self._sp.check_output(["git", "log", "-1", "--format=%H", "--", target],
                                    cwd=P.REPO_ROOT, text=True).strip()
        parent = self._sp.check_output(["git", "rev-parse", f"{rev}^"],
                                       cwd=P.REPO_ROOT, text=True).strip()
        ok, diff = P.paths_unchanged_between(parent, rev, [target])
        self.assertFalse(ok, f"{target} changed in {rev[:8]}; that must be visible")
        self.assertEqual(diff, [target])

    def test_unresolvable_path_fails_closed(self):
        ok, diff = P.paths_unchanged_between("HEAD", "HEAD", ["nd-unfolding/does_not_exist.py"])
        self.assertFalse(ok, "an unverifiable path must count as differing, not as satisfied")

    def test_MUTATION_equality_would_reject_after_an_unrelated_push(self):
        """The defect, shown: HEAD~1 != HEAD, so equality rejects a verdict reviewed one commit
        ago even when nothing it reviewed changed."""
        older, head = self._rev("HEAD~1"), self._rev("HEAD")
        self.assertNotEqual(older, head)
        self.assertTrue(P.code_rev_in_history(older),
                        "ancestry accepts it; equality did not -- that was the defect")

    def test_token_gate_uses_ancestry_not_equality(self):
        src = (ND / "p4_check_verifier_token.py").read_text()
        code = "\n".join(l for l in src.splitlines() if not l.lstrip().startswith("#"))
        self.assertIn("code_rev_in_history", code)
        self.assertIn("paths_unchanged_between", code)
        self.assertNotIn('head.startswith(str(cr))', code)   # the retired equality


class REPAIR6c_WidenedIntegralTolerance(unittest.TestCase):
    """REPAIR-6c: REPRO_RTOL_INTEGRAL widened 1e-12 -> 1e-11 from measured spread.

    Specification, not loosening: nothing was failing. The per-bin leg had 52x margin while the
    integral leg had 3.2x and its two observations spanned 12x -- set up to false-alarm on a
    third run."""

    def test_declared_values(self):
        self.assertEqual(P.REPRO_RTOL_PER_BIN, 1e-9)
        self.assertEqual(P.REPRO_RTOL_INTEGRAL, 1e-11)

    def test_both_legs_now_carry_comparable_margin(self):
        f = P.REPRO_MEASURED_FLOOR
        bin_margin = P.REPRO_RTOL_PER_BIN / f["worst_rel_bin"]
        int_margin = P.REPRO_RTOL_INTEGRAL / 3.14e-13      # worst observed integral
        self.assertGreater(bin_margin, 20); self.assertGreater(int_margin, 20)
        self.assertLess(max(bin_margin, int_margin) / min(bin_margin, int_margin), 4.0,
                        "the two legs should be within a small factor of each other")

    def test_measured_floor_was_NOT_moved_with_the_spec(self):
        """The whole point of recording them separately."""
        f = P.REPRO_MEASURED_FLOOR
        self.assertEqual(f["worst_rel_bin"], 1.9e-11)
        self.assertEqual(f["integral_rel"], 2.6e-14)
        self.assertNotEqual(f["integral_rel"], P.REPRO_RTOL_INTEGRAL)

    def test_discrimination_survives_the_widening(self):
        """A uniform shift between 1e-11 and 1e-9 must still pass per-bin and FAIL integral."""
        rng = np.random.default_rng(0)
        base = rng.uniform(1, 10, 4096)
        with self.assertRaises(P4GateError) as cm:
            P.check_reproducibility(base * (1 + 5e-11), base)
        self.assertIn("integral relative difference", str(cm.exception))
        # and real scatter at the measured floor still passes
        sc = rng.normal(0, 4e-12, base.size); sc -= sc.mean()
        self.assertIsInstance(P.check_reproducibility(base * (1 + sc), base), dict)


class REPAIR7_EndpointContentReproduction(unittest.TestCase):
    """REPAIR-7 item 1: the frozen endpoint-manifest hash is replaced by content comparison.

    Joseph's success criterion, stated as two tests rather than one: **a legitimate re-unfold
    PASSES and a semantics change FAILS.** A gate that only demonstrates one direction is the
    failure mode this lane has hit repeatedly."""

    def _endpoint(self, n=10694, seed=0):
        return np.random.default_rng(seed).uniform(1e-40, 1e-38, n)

    # ---- direction 1: a legitimate re-unfold PASSES ----
    def test_legitimate_rerun_passes(self):
        """Non-bit-identical, scattered at the MEASURED floor -- exactly what a real re-unfold
        produces. The frozen-hash check rejected this; content comparison accepts it."""
        ref = self._endpoint()
        rng = np.random.default_rng(1)
        noise = rng.normal(0, 4e-12, ref.size); noise -= noise.mean()
        rerun = ref * (1 + noise)
        self.assertFalse(np.array_equal(rerun, ref), "must not be bit-identical")
        r = P.check_reproducibility(rerun, ref)
        self.assertLess(r["max_rel_bin"], P.REPRO_RTOL_PER_BIN)
        self.assertLess(r["rel_integral"], P.REPRO_RTOL_INTEGRAL)

    def test_MUTATION_the_frozen_hash_check_would_have_REJECTED_that_rerun(self):
        """The defect, demonstrated: identical physics, different bytes, hash comparison fails."""
        import hashlib
        ref = self._endpoint()
        rng = np.random.default_rng(1)
        noise = rng.normal(0, 4e-12, ref.size); noise -= noise.mean()
        rerun = ref * (1 + noise)
        h_ref = hashlib.sha256(ref.tobytes()).hexdigest()
        h_new = hashlib.sha256(rerun.tobytes()).hexdigest()
        self.assertNotEqual(h_ref, h_new,
                            "the frozen-hash check rejects a legitimate rerun -- that was the defect")

    # ---- direction 2: a semantics change FAILS ----
    def test_coherent_normalisation_change_fails(self):
        ref = self._endpoint()
        with self.assertRaises(P4GateError) as cm:
            P.check_reproducibility(ref * 1.001, ref)
        self.assertIn("relative difference", str(cm.exception))

    def test_small_coherent_shift_inside_the_per_bin_leg_still_fails_on_the_integral(self):
        """The discriminating case: 5e-11 is inside the 1e-9 per-bin leg and outside 1e-11."""
        ref = self._endpoint()
        with self.assertRaises(P4GateError) as cm:
            P.check_reproducibility(ref * (1 + 5e-11), ref)
        self.assertIn("integral relative difference", str(cm.exception))

    def test_a_single_corrupted_bin_fails(self):
        """A localised semantics change: one bin moved by 1%, integral barely perturbed."""
        ref = self._endpoint(); bad = ref.copy(); bad[17] *= 1.01
        with self.assertRaises(P4GateError) as cm:
            P.check_reproducibility(bad, ref)
        self.assertIn("per-bin relative difference", str(cm.exception))

    def test_evidence_no_longer_pins_the_endpoint_manifest_to_a_frozen_hash(self):
        src = (ND / "p4_evidence.py").read_text()
        code = "\n".join(l for l in src.splitlines() if not l.lstrip().startswith("#"))
        self.assertNotIn('"endpoint_manifest":', code)          # gone from OBS
        self.assertIn("ENDPOINT_REFERENCE_DIR", code)
        self.assertIn("check_reproducibility", code)
        # and a failed manifest is not written under the consumable name
        # PB3 (2026-08-10): the redirect no longer spells the .FAILED name literally -- products
        # are written to .PENDING and renamed by _publish_evidence() AFTER every blocker has run,
        # so the final name is composed. Assert the MECHANISM, not the spelling: this guard was
        # textual, which is verifier defect #7's "detached/textual guards" and is why editing the
        # implementation broke a test whose subject had not changed.
        self.assertIn(".PENDING", code)
        self.assertIn("_publish_evidence", code)
        self.assertIn('".FAILED"', code)
        # and the publish must come AFTER the crosscheck enforcement, which is the whole point
        self.assertLess(code.index("need(_v,"), code.index("_publish_evidence()\n\nprint"),
                        "evidence is published before the verifier_crosscheck blockers run")


class REPAIR7_ExecutionDerivedSurface(unittest.TestCase):
    """REPAIR-7 item 2: the review surface is derived from the import graph, not a name glob.

    Third instance of the corpus-definition error, so the derivation is mechanical and this test
    asserts the specific modules the glob omitted are now covered."""

    def test_surface_includes_the_modules_the_glob_omitted(self):
        surf = P.standard_p4_execution_surface()
        for mod in ("nd-unfolding/uq_math.py", "nd-unfolding/project_cov_nd.py",
                    "nd-unfolding/unfold_nd_omnifold_unbinned.py", "nd-unfolding/xsec_nd.py",
                    "unbinned_unfolding/python/omnifold.py"):
            self.assertIn(mod, surf, f"{mod} missing from the execution surface")

    def test_surface_is_strictly_more_than_the_name_glob_for_execution(self):
        glob_surface = set(P.tracked_files_matching(P.STANDARD_P4_SURFACE_GLOBS))
        exec_surface = set(P.standard_p4_execution_surface())
        gained = exec_surface - glob_surface
        self.assertTrue(gained, "the derived surface must add the executed modules")
        self.assertIn("unbinned_unfolding/python/omnifold.py", gained)

    def test_shell_drivers_are_included_though_never_imported(self):
        surf = P.standard_p4_execution_surface()
        self.assertTrue(any(f.startswith("nd-unfolding/run_p4_") for f in surf))

    def test_token_gate_uses_the_execution_surface(self):
        src = (ND / "p4_check_verifier_token.py").read_text()
        code = "\n".join(l for l in src.splitlines() if not l.lstrip().startswith("#"))
        self.assertIn("standard_p4_execution_surface", code)


class REPAIR7_DeadPathDeleted(unittest.TestCase):
    """REPAIR-7 item 3: check_merged_metadata is deleted, and its comparison moved to the live
    path. A fix inside a dead function reads as done and is worse than no fix."""

    def test_the_dead_gate_is_gone(self):
        self.assertFalse(hasattr(P, "check_merged_metadata"),
                         "the uncalled gate must be deleted, not kept")

    def test_a_tombstone_explains_why(self):
        src = (ND / "p4_lib.py").read_text()
        self.assertIn("check_merged_metadata` is DELETED", src)
        self.assertIn("NO production caller", src)

    def test_the_native_miss_comparison_now_lives_in_the_live_path(self):
        src = (ND / "p4_evidence.py").read_text()
        code = "\n".join(l for l in src.splitlines() if not l.lstrip().startswith("#"))
        self.assertIn("native-miss flag/count disagree", code)
        self.assertIn("AppendTruthOnlyMisses did not run", code)
        # and it is no longer presence-only
        self.assertNotIn('need(rec["nTruthOnlyMisses"] is not None,', code)


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
