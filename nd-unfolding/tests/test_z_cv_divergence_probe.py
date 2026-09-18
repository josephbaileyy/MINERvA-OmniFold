#!/usr/bin/env python3
"""Tests for the CV divergence probe -- the production-faithful one.

Its job is to locate the FIRST divergence between two repeated production CV executions, so the
tests that matter are about the localisation logic and about the refusals that keep the input
honest. The heavy path (the real 2.94 GB bank, the real estimator) cannot run here and is not
mocked: `first_divergence` is pure and is tested directly, and `Tap` is tested against a stand-in
module object, which is exactly what it wraps.

⚠ THE REFUSAL ON AN UNVERIFIED BANK IS THE LOAD-BEARING ONE. A comparison run on an input whose
identity is unknown is a statement about an unknown object. The digest it requires is the
precursor receipt's own `extra.bank_cv_sha256`, so the probe and the receipt cannot drift apart
without the probe refusing.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
PROBE = REPO / "nd-unfolding" / "z_cv_divergence_probe.py"
sys.path.insert(0, str(REPO / "nd-unfolding"))

import z_cv_divergence_probe as P  # noqa: E402


def _rec(i, digest, total=1.0):
    return {"call": i, "digest": digest, "n": 10, "sum": total, "min": 0.0, "max": 1.0}


class FirstDivergenceLocalisation(unittest.TestCase):
    def test_identical_sequences_report_no_divergence(self):
        a = [_rec(i, f"d{i}") for i in range(10)]
        idx, detail = P.first_divergence(a, list(a))
        self.assertIsNone(idx)
        self.assertEqual(detail["identical_evaluations"], 10)

    def test_divergence_at_the_first_call_is_found(self):
        a = [_rec(i, f"d{i}") for i in range(10)]
        b = [_rec(i, f"d{i}") for i in range(10)]
        b[0] = _rec(0, "OTHER", total=1.5)
        idx, detail = P.first_divergence(a, b)
        self.assertEqual(idx, 0)
        self.assertEqual(detail["iteration"], 0)
        self.assertEqual(detail["step"], 1)
        self.assertEqual(detail["identical_evaluations_before"], 0)

    def test_divergence_mid_sequence_reports_iteration_and_step(self):
        a = [_rec(i, f"d{i}") for i in range(10)]
        b = [_rec(i, f"d{i}") for i in range(10)]
        b[5] = _rec(5, "OTHER", total=2.0)
        idx, detail = P.first_divergence(a, b)
        self.assertEqual(idx, 5)
        # call 5 -> iteration 2, step 2   (2*2+1 = 5)
        self.assertEqual(detail["iteration"], 2)
        self.assertEqual(detail["step"], 2)
        self.assertEqual(detail["identical_evaluations_before"], 5)
        self.assertAlmostEqual(detail["relative_sum_difference"], 1.0)

    def test_the_step_mapping_matches_the_loop_structure(self):
        """call 2*it is step 1, call 2*it+1 is step 2 -- omnifold_nn_core.py:248-269."""
        for it in range(5):
            self.assertEqual(P._stage_label(2 * it), {"iteration": it, "step": 1})
            self.assertEqual(P._stage_label(2 * it + 1), {"iteration": it, "step": 2})

    def test_different_call_counts_are_reported_as_such(self):
        """Two executions that made different numbers of evaluations is its own finding, not a
        digest mismatch."""
        a = [_rec(i, f"d{i}") for i in range(10)]
        idx, detail = P.first_divergence(a, a[:6])
        self.assertEqual(idx, 6)
        self.assertIn("DIFFERENT NUMBERS", detail["note"])
        self.assertEqual((detail["n_calls_a"], detail["n_calls_b"]), (10, 6))

    def test_a_later_difference_does_not_mask_an_earlier_one(self):
        a = [_rec(i, f"d{i}") for i in range(10)]
        b = [_rec(i, f"d{i}") for i in range(10)]
        b[3] = _rec(3, "X"); b[7] = _rec(7, "Y")
        idx, _ = P.first_divergence(a, b)
        self.assertEqual(idx, 3, "it must report the FIRST, not any")


class TheTapIsCaptureOnly(unittest.TestCase):
    """A wrapper that changed the value it measures would invalidate the whole comparison."""

    class _FakeCore:
        @staticmethod
        def _reweight(events, clf):
            return np.asarray(events, float) * 2.0

    def test_the_wrapper_returns_the_original_value_unchanged(self):
        core = self._FakeCore()
        original = core._reweight
        x = np.arange(5.0)
        expected = original(x, None)
        with P.Tap(core) as tap:
            got = core._reweight(x, None)
        np.testing.assert_array_equal(got, expected)
        self.assertEqual(len(tap.records), 1)

    def test_it_records_one_entry_per_call_in_order(self):
        core = self._FakeCore()
        with P.Tap(core) as tap:
            for k in range(4):
                core._reweight(np.full(3, float(k)), None)
        self.assertEqual([r["call"] for r in tap.records], [0, 1, 2, 3])
        self.assertEqual(len({r["digest"] for r in tap.records}), 4)

    def test_it_restores_the_original_on_exit(self):
        core = self._FakeCore()
        original = core._reweight
        with P.Tap(core):
            self.assertIsNot(core._reweight, original)
        self.assertIs(core._reweight, original)

    def test_it_restores_even_when_the_body_raises(self):
        core = self._FakeCore()
        original = core._reweight
        with self.assertRaises(ValueError):
            with P.Tap(core):
                raise ValueError("boom")
        self.assertIs(core._reweight, original)


class TheBankMustBeVerified(unittest.TestCase):
    def setUp(self):
        self.t = Path(tempfile.mkdtemp())

    def test_a_missing_cv_npz_refuses_and_says_bank_is_a_directory(self):
        r = subprocess.run([sys.executable, str(PROBE), "--bank", str(self.t),
                            "--estimator-seed", "1000", "--out", str(self.t / "o.json")],
                           capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("no cv.npz", r.stderr)
        self.assertIn("DIRECTORY", r.stderr)

    def test_a_wrong_digest_refuses_by_default(self):
        np.savez(self.t / "cv.npz", junk=np.arange(3))
        r = subprocess.run([sys.executable, str(PROBE), "--bank", str(self.t),
                            "--estimator-seed", "1000", "--out", str(self.t / "o.json")],
                           capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn(P.EXPECTED_BANK_CV_SHA256, r.stderr)
        self.assertIn("statement about an unknown object", r.stderr)

    def test_the_expected_digest_is_the_precursor_receipts_own(self):
        """Bound to the receipt, so the probe and the receipt cannot drift silently."""
        self.assertEqual(
            P.EXPECTED_BANK_CV_SHA256,
            "3c9bbd6283fcb157f3bc110a790ab45e9c499cb8c457dfcb9ad0193d951692bd")


class TheProbeDoesNotModifyProduction(unittest.TestCase):
    def test_it_does_not_apply_any_determinism_overlay(self):
        """Pinning would test a DIFFERENT estimator than production runs."""
        src = PROBE.read_text()
        for knob in ("deterministic", "force_row_wise", "num_threads", "z_lgbm_overlay"):
            self.assertNotIn(f"{knob}=", src)
        self.assertIn("UNPINNED", src)

    def test_it_uses_the_same_function_unified_throw_cov_calls(self):
        """⚠ THIS TEST ORIGINALLY ASSERTED THE DEFECT. It required
        `from compare_unified_throw import _xsec_for_weights` -- the binding the 5D monkeypatch
        never reaches -- so it was green while job 58510551 was doomed. What matters is that the
        kernel is resolved through the base module's globals at call time."""
        src = PROBE.read_text()
        self.assertIn("U._xsec_for_weights(d, edges", src)
        self.assertIn("U._load_bank", src)

    def test_both_executions_are_given_the_same_seed(self):
        """unified_throw_cov.py:840 and :1011 both pass args.estimator_seed. A probe that varied
        the seed would measure a different thing and would find a difference by construction."""
        src = PROBE.read_text()
        self.assertIn("the SAME seed for both executions", src)
        self.assertNotIn("estimator_seed + 1", src)
        self.assertNotIn("seed + 7", src)


if __name__ == "__main__":
    unittest.main()


class TheFiveDimensionalKernelMustBeTheOneCalled(unittest.TestCase):
    """HOW JOB 58510551 FAILED, as a regression test.

    `unified_throw_cov_5d.py:88` installs the 5D kernel with
    `base._xsec_for_weights = _xsec_for_weights_5d`, and its own docstring says why: the base
    kernel in `compare_unified_throw` stops at `td_q3` with no `td_W`, so "for len(edges)==5 it
    would feed 4 denom coords to a 5-edge histogramdd".

    I had written `from compare_unified_throw import _xsec_for_weights`, which binds the UNPATCHED
    name -- a separate binding the monkeypatch never reaches -- and the run died in exactly the way
    that docstring predicts, after 1011 s and a full bank load of 32,849,103 events.

    This is the inverse of the usual `from`-import defect. Usually a `from`-import makes a PATCH
    decorative; here it made the patch INVISIBLE to the caller.
    """

    def test_the_probe_does_not_from_import_the_base_kernel(self):
        """Anchored on a real import STATEMENT -- a bare substring search also matches the comment
        that explains the defect, which is how this test first failed on its own repair."""
        import re
        src = PROBE.read_text()
        offenders = [ln for ln in src.splitlines()
                     if re.match(r"\s*from\s+compare_unified_throw\s+import\s+_xsec_for_weights",
                                 ln)]
        self.assertEqual(offenders, [], f"live from-import present: {offenders}")

    def test_the_probe_imports_the_5d_wrapper_which_installs_the_patch(self):
        src = PROBE.read_text()
        self.assertIn("import unified_throw_cov_5d", src)

    def test_the_probe_resolves_the_kernel_through_base_globals_at_call_time(self):
        """`U._xsec_for_weights(...)`, not a name captured at import time."""
        src = PROBE.read_text()
        self.assertIn("U._xsec_for_weights(d, edges", src)

    def test_the_probe_asserts_the_patch_landed_before_computing(self):
        """A run that silently used the 4D kernel would burn the allocation to rediscover this."""
        src = PROBE.read_text()
        self.assertIn("is not u5._xsec_for_weights_5d", src)
        self.assertIn("the 5D kernel is not installed", src)

    def test_the_wrapper_really_does_install_it(self):
        """Read from the wrapper, so this cannot pass against a stale belief about it."""
        w = (REPO / "nd-unfolding" / "unified_throw_cov_5d.py").read_text()
        self.assertIn("base._xsec_for_weights = _xsec_for_weights_5d", w)
        self.assertIn('if len(edges) >= 5 and "td_W" in d:', w)

    def test_the_base_kernel_genuinely_lacks_td_W(self):
        """The premise of the whole repair, checked against the base module rather than assumed."""
        b = (REPO / "nd-unfolding" / "compare_unified_throw.py").read_text()
        self.assertIn("td_cols[:len(edges)]", b)
        self.assertNotIn("td_W", b)
