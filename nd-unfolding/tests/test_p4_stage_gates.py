"""REPAIR-12: every covariance stage gates itself, and the gated set is DERIVED, not listed.

THE DEFECT. `P4_VERIFIER_PASS` was a property of ONE CALL PATH. The hard gate lived only in
`run_p4_standard.sh`; `p4_build_components.py`, `p4_validate_active_lateral.py` and
`p4_project_4d.py` are individually executable and were individually ungated. Invoking them
directly -- the only way to run stages 4-6 without re-running 1-3, which is exactly what "run
stages 4-6" asks for -- bypassed the token completely. Lane B found that route by executing the
instruction literally, and declined to use it.

That is `KNOWN_ISSUES #21` one layer out. #21 was *any non-empty string opens the stages*; this was
*not going through the wrapper opens the stages*. The #21 repair strengthened the predicate and left
it in the same single location, which is why the same class recurred against a stronger check.

WHY THE SET IS DERIVED AND NOT WRITTEN DOWN. The failure being repaired is OMISSION -- a fourth
stage module that nobody remembers to gate. A hand-written tuple of three names cannot detect its
own incompleteness, so it would pass forever while the hole reopened. The set is therefore read out
of `run_p4_standard.sh`: every `python3 <module>.py` the wrapper invokes AFTER its own token gate.
That definition is the property we actually want -- *everything downstream of the gate must itself
gate* -- rather than a list that happens to be right today. Predeclared as `C2` in
`docs/orchestration/PREDECLARATION-20260816-repair12-verifier-pass.md` before this repair existed.

WHY `ast` AND NOT `grep` (BEN-335). "Does this module call the gate" is a question about the
program, not about its text. A grep for the gate's name matches docstrings, comments and the
sentence describing its absence -- measured at `13f9e0a`, a grep for `build_projection_M` inside the
function that deliberately avoids it returned 2, both docstring mentions, and reporting it would
have inverted repair-11's verdict. These tests walk the AST.

WHY EXECUTION AND NOT SOURCE INSPECTION (`R11-1`). A source-level `assertIn` accepts a commented-out
call as evidence of wiring -- the same text-for-behaviour substitution with the polarity reversed.
The bypass is therefore demonstrated by RUNNING the modules the way the bypass runs them.

WHAT MAKES THIS DEMONSTRABLE AT ALL. ROOT is lazy-imported inside functions in all three modules, so
a gate at the top of `main()` fires before any ROOT import. These tests therefore run wherever the
suite runs, with no `setup_salloc_env.sh` and no ROOT. A control that needs a special environment to
demonstrate is a control most readers will never see fire.
"""
import ast
import os
import re
import subprocess
import sys
import unittest
from pathlib import Path

ND = Path(__file__).resolve().parents[1]
WRAPPER = ND / "run_p4_standard.sh"
GATE_FN = "require_verifier_token"
ENV_VAR = "P4_VERIFIER_PASS"


def stage_modules_after_the_gate(text=None):
    """The gated set, DERIVED: every `python3 <mod>.py` the wrapper invokes after its token gate.

    Returns [] if the gate line cannot be found, so a caller can refuse rather than silently
    treating "no gate" as "nothing to gate" -- an empty derived set must never read as success.
    """
    src = WRAPPER.read_text() if text is None else text
    lines = src.splitlines()
    gate_at = next((i for i, l in enumerate(lines)
                    if "p4_check_verifier_token.py" in l and "--token" in l), None)
    if gate_at is None:
        return []
    mods = []
    for l in lines[gate_at + 1:]:
        if l.lstrip().startswith("#"):
            continue
        for m in re.finditer(r"python3\s+([A-Za-z0-9_]+\.py)", l):
            if m.group(1) not in mods:
                mods.append(m.group(1))
    return mods


def main_calls_gate(module_filename):
    """True iff that module's `main()` contains a CALL to the gate. AST, never text (BEN-335)."""
    tree = ast.parse((ND / module_filename).read_text())
    fn = next((n for n in ast.walk(tree)
               if isinstance(n, ast.FunctionDef) and n.name == "main"), None)
    if fn is None:
        return False
    return any(GATE_FN in ast.unparse(n.func) for n in ast.walk(fn) if isinstance(n, ast.Call))


def run_module_directly(module_filename, env_token=None, args=()):
    """Invoke the module the way the BYPASS invokes it: `python3 <mod>.py` from nd-unfolding."""
    env = dict(os.environ)
    env.pop(ENV_VAR, None)
    if env_token is not None:
        env[ENV_VAR] = env_token
    return subprocess.run([sys.executable, module_filename, *args], cwd=str(ND), env=env,
                          capture_output=True, text=True, timeout=180)


class TheGatedSetIsDerived(unittest.TestCase):
    def test_the_wrapper_yields_a_non_empty_set(self):
        mods = stage_modules_after_the_gate()
        self.assertTrue(mods, "derived no stage modules from the wrapper; an empty set must not "
                              "read as 'nothing needs gating'")
        # Reported, not asserted as a literal: pinning the membership here would recreate the
        # hand-list this test exists to replace.
        print(f"\n[repair-12] derived gated set: {mods}")

    def test_MUTATION_a_wrapper_with_no_gate_derives_NOTHING(self):
        """Negative control on the DERIVATION. If the wrapper's gate line vanished, the deriver
        must return [] and the test above must fail -- not silently gate an empty set."""
        text = WRAPPER.read_text().replace("p4_check_verifier_token.py", "some_other_script.py")
        self.assertEqual(stage_modules_after_the_gate(text), [])

    def test_MUTATION_an_added_stage_script_enters_the_set(self):
        """Negative control the hand-list could not pass: a NEW stage invoked after the gate is
        picked up automatically. This is the omission the derived set exists to catch."""
        text = WRAPPER.read_text().rstrip() + "\nrun python3 p4_a_brand_new_stage.py --x 1\n"
        self.assertIn("p4_a_brand_new_stage.py", stage_modules_after_the_gate(text))


class EveryDerivedStageGates(unittest.TestCase):
    def test_each_derived_module_calls_the_gate_in_main(self):
        mods = stage_modules_after_the_gate()
        self.assertTrue(mods)
        for m in mods:
            with self.subTest(module=m):
                self.assertTrue(main_calls_gate(m),
                                f"{m} is invoked after the wrapper's token gate but its main() "
                                f"does not call {GATE_FN}; invoking it directly bypasses the token")

    def test_MUTATION_a_commented_out_call_does_NOT_count(self):
        """The whole point of using AST. A source-level `assertIn` would accept this; R11-1 did."""
        src = (ND / "p4_project_4d.py").read_text()
        commented = src.replace(f"    _tok.{GATE_FN}(", f"    # _tok.{GATE_FN}(")
        self.assertNotEqual(commented, src, "mutation changed nothing")
        tree = ast.parse(commented)
        fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "main")
        self.assertFalse(
            any(GATE_FN in ast.unparse(n.func) for n in ast.walk(fn) if isinstance(n, ast.Call)),
            "a commented-out gate call still registered as a call")
        self.assertIn(GATE_FN, commented, "...while the TEXT is still present, which is exactly "
                                          "why a text-level check cannot do this job")


class TheBypassIsClosed(unittest.TestCase):
    """C3: demonstrated by EXECUTION, on lane B's actual route, in both directions."""

    def test_direct_invocation_with_NO_token_is_refused(self):
        for m in stage_modules_after_the_gate():
            with self.subTest(module=m):
                r = run_module_directly(m)
                out = r.stdout + r.stderr
                self.assertNotEqual(r.returncode, 0, f"{m} ran without a token")
                self.assertIn(ENV_VAR, out)
                self.assertNotIn("usage:", out.lower(),
                                 f"{m} reached argparse before the gate; the gate must be first")

    def test_direct_invocation_with_a_NON_RESOLVING_token_is_refused_DIFFERENTLY(self):
        """The other direction, and the one that proves the gate RESOLVES rather than sniffs.

        A 64-hex token that matches no receipt must be refused by the digest machinery, with a
        DIFFERENT message from the unset case. If both refusals were identical the gate would be
        indistinguishable from an emptiness check -- which is KNOWN_ISSUES #21 relocated.
        """
        for m in stage_modules_after_the_gate():
            with self.subTest(module=m):
                r = run_module_directly(m, env_token="0" * 64)
                out = r.stdout + r.stderr
                self.assertNotEqual(r.returncode, 0)
                # It must fail AT THE GATE, not later. Without this the test passes on the
                # PRE-REPAIR form, where the module runs ungated and dies at argparse -- nonzero,
                # no unset-message, and entirely the wrong reason. Observed doing exactly that
                # during the power test, and this line is why it no longer can.
                self.assertNotIn("usage:", out.lower(),
                                 f"{m} reached argparse; this refusal is argparse's, not the gate's")
                self.assertIn("sha256", out.lower(),
                              "refusal did not come from the digest machinery")
                self.assertNotIn(f"{ENV_VAR} = the sha256", out,
                                 "a set-but-invalid token produced the UNSET message; the gate is "
                                 "testing emptiness, not resolving the digest")

    def test_a_passphrase_is_refused_as_not_a_digest(self):
        r = run_module_directly("p4_project_4d.py", env_token="please-let-me-through")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("sha256", (r.stdout + r.stderr).lower())

    def test_POSITIVE_a_resolving_token_passes_the_gate(self):
        """Unit-level and labelled as such. No live PASS token can exist here by construction:
        repair-12 edits the surface, so rule 4b invalidates the standing verdict -- which is what
        `C4` predeclared. The resolution path is therefore exercised with `resolve` substituted, so
        the gate is shown to RETURN as well as to raise. Without this the suite would only ever
        observe refusals, and a gate that always refuses is not a gate either.
        """
        sys.path.insert(0, str(ND))
        import p4_check_verifier_token as tok
        real, seen = tok.resolve, {}

        def fake_resolve(t):
            seen["token"] = t
            return "receipts/fake-verdict.json", {"verdict": "PASS"}

        tok.resolve = fake_resolve
        try:
            os.environ[ENV_VAR] = "a" * 64
            rel, v = tok.require_verifier_token("unit")
        finally:
            tok.resolve = real
            os.environ.pop(ENV_VAR, None)
        self.assertEqual(rel, "receipts/fake-verdict.json")
        self.assertEqual(v["verdict"], "PASS")
        self.assertEqual(seen["token"], "a" * 64, "the gate did not pass the token to resolve()")


if __name__ == "__main__":
    unittest.main()
