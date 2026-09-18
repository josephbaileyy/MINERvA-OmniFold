#!/usr/bin/env python3
"""Cause 4's re-added jitter print — SPEC §2.4, ruled approved 2026-09-18.

The print was recovered LINE FOR LINE from `a0cdc019:232-252`, which §2.4 names as the retired
source. **The retired code did not stop at a print**, and that is what these tests are mostly
about: it also computed

    tr_uni_corr = max(tr_uni - jit_trace, 0.0)
    st_uni_corr = float(np.sqrt(tr_uni_corr))

and printed a "jitter-corrected unified sqrt-trace" and a "corrected ratio". **That subtraction IS
cause 4's defect.** §2.4 condition 4 is *"the print is print-only, never subtracted"*, so the
QUANTITY and its PRINT come back and the CORRECTION does not.

`test_the_retired_SUBTRACTION_is_not_reintroduced` is the one that matters: a future edit that
"restores the rest of `a0cdc019`" reintroduces the exact defect, and it would look like a
faithfulness improvement.
"""
import hashlib
import re
import sys
import unittest
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / "nd-unfolding" / "unified_throw_cov.py"
sys.path.insert(0, str(REPO / "nd-unfolding"))


def code_only(path):
    """The source with COMMENTS and STRING LITERALS removed.

    ⚠ WHY THIS EXISTS. The bans below first fired on the module's own explanatory comment, which
    quotes `tr_uni_corr` and "jitter-corrected" precisely to record that they are NOT re-added. A
    substring ban cannot distinguish code from prose ABOUT the code -- and that is the second time
    in this session the same shape has caught me, the first being a ban that matched inside its own
    negation. Tokenising is the fix that actually separates the two.
    """
    import io
    import tokenize
    out = []
    with open(path, "rb") as fh:
        for tok in tokenize.tokenize(fh.readline):
            if tok.type in (tokenize.COMMENT, tokenize.STRING):
                continue
            out.append(tok.string)
    return "\n".join(out)


class TheQuantityMatchesTheRetiredSource(unittest.TestCase):
    def test_the_formula_is_the_retired_one(self):
        t = SRC.read_text()
        self.assertIn("jit_trace = float(np.sum((x_cv_jit[rep] - base) ** 2))", t)

    def test_the_jitter_seed_is_estimator_seed_plus_7(self):
        """`a0cdc019` used `args.seed + 7`; this module's operand is `estimator_seed`."""
        t = SRC.read_text()
        self.assertIn("args.estimator_seed + 7", t)

    def test_the_second_unfold_is_a_SEPARATE_one_from_the_null(self):
        """The null re-runs at the SAME seed (a determinism check); the jitter quantity needs a
        DIFFERENT seed. Reusing the null's `x_cv2` would measure zero by construction."""
        t = SRC.read_text()
        self.assertIn("args.estimator_seed).ravel", t)        # the null's, same seed
        self.assertIn("args.estimator_seed + 7).ravel", t)    # the jitter's, offset seed


class TheRetiredSubtractionStaysOut(unittest.TestCase):
    """§2.4 condition 4. THE LOAD-BEARING CLASS."""

    def test_the_retired_SUBTRACTION_is_not_reintroduced(self):
        t = code_only(SRC)          # comments and strings stripped -- see `code_only`
        for gone in ("tr_uni_corr", "st_uni_corr"):
            self.assertNotIn(gone, t,
                             f"{gone!r} is part of the retired CORRECTION, which is cause 4's "
                             f"defect. The print comes back; the subtraction does not.")

    def test_jit_trace_is_never_subtracted_from_a_trace(self):
        """A narrower form of the same rule, in case the names change.

        Checked on the parsed CODE rather than on text: an `ast` walk over every `BinOp` with a
        `Sub` operator, asking whether `jit_trace` is either operand. That cannot be fooled by a
        comment, a format spec, or a rewrap.
        """
        import ast
        tree = ast.parse(SRC.read_text())
        offenders = []
        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Sub):
                for side in (node.left, node.right):
                    if isinstance(side, ast.Name) and side.id == "jit_trace":
                        offenders.append(node.lineno)
        self.assertEqual(offenders, [],
                         f"jit_trace is an operand of a subtraction at line(s) {offenders} -- "
                         f"that is cause 4's defect, not its print")

    def test_the_print_declares_itself_print_only(self):
        """This one WANTS the prose: the emitted print string must say so to a log reader."""
        t = SRC.read_text()
        self.assertIn("PRINT-ONLY", t)
        self.assertIn("is NOT re-added", t)

    def test_no_corrected_trace_is_ever_PRINTED(self):
        """The retired code printed a "jitter-corrected" trace and a "corrected ratio".

        ⚠ Checked on the EMITTED PRINT STRINGS via `ast`, not on raw text: the module's own comment
        quotes both phrases in order to record that they are absent, so a text search finds them in
        the prose that exists to say they are gone. Third instance of that shape today.
        """
        import ast
        tree = ast.parse(SRC.read_text())
        emitted = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                    and node.func.id == "print":
                for a in node.args:
                    for sub in ast.walk(a):
                        if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
                            emitted.append(sub.value)
        blob = " ".join(emitted)
        for phrase in ("jitter-corrected", "corrected ratio"):
            self.assertNotIn(phrase, blob,
                             f"{phrase!r} is EMITTED by a print -- the retired correction is back")
        self.assertTrue(any("jitter floor" in e for e in emitted),
                        "the jitter print itself must still be emitted")


class TheConditionThreeGuard(unittest.TestCase):
    def test_the_guard_digests_the_covariance_before_and_after(self):
        t = SRC.read_text()
        self.assertIn('_pre = {"C_uni": _sha256_array(C_uni), "C_block": _sha256_array(C_block)}', t)
        self.assertIn('_post = {"C_uni": _sha256_array(C_uni), "C_block": _sha256_array(C_block)}', t)

    def test_the_guard_RAISES_rather_than_warning(self):
        t = SRC.read_text()
        m = re.search(r"if _pre != _post:\s*\n\s*raise SystemExit", t)
        self.assertIsNotNone(m, "the condition-3 guard must raise, not warn")

    def test_the_guard_names_both_conditions_in_its_message(self):
        t = SRC.read_text()
        self.assertIn("condition 3 requires", t)
        self.assertIn("condition 4 that", t)


class TheOperandsAndTheirDigests(unittest.TestCase):
    """§2.4 condition 2: the operands are THIS build's own, recorded by content digest."""

    def test_both_operands_are_digested(self):
        t = SRC.read_text()
        self.assertIn('"x_cv_sha256": _sha256_array(x_cv)', t)
        self.assertIn('"x_cv_jitter_sha256": _sha256_array(x_cv_jit)', t)

    def test_the_single_draw_nature_is_recorded(self):
        """§6.5 retains the single-draw referent deliberately, because the defect cause 4 names IS
        a single-draw subtraction."""
        t = SRC.read_text()
        self.assertIn("single_draw", t)
        self.assertIn("one-sample estimate of a variance", t)

    def test_the_digest_convention_matches_z_receipt_EXACTLY(self):
        """⚠ The convention is DUPLICATED, not imported -- `z_receipt` is Z-specific and this is a
        shared production module. A digest written under one convention and compared under another
        is a silent mismatch, so the equality is asserted against the real function."""
        sys.modules.setdefault("ROOT", type(sys)("ROOT"))
        import unified_throw_cov as U
        import z_receipt as R
        a = np.arange(12.0).reshape(3, 4)
        self.assertEqual(U._sha256_array(a), R.sha256_array(a))
        self.assertNotEqual(U._sha256_array(a), U._sha256_array(a.reshape(4, 3)),
                            "shape must be folded in, or a reshaped view collides")


class TheCostIsOptIn(unittest.TestCase):
    def test_it_is_behind_its_own_flag_and_not_on_null(self):
        """⚠ If this rode on `--null`, every existing caller's `--null` run would silently acquire
        another full CV unfold. SPEC §5.8b prices that at <= 0.5764 CPU task-h."""
        t = SRC.read_text()
        self.assertIn('"--jitter-print", action="store_true"', t)
        self.assertIn("if args.jitter_print:", t)

    def test_the_flag_help_states_the_cost(self):
        t = SRC.read_text()
        self.assertIn("0.5764", t)


if __name__ == "__main__":
    unittest.main()
