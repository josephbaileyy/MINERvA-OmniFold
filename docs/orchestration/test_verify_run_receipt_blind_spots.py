"""Fail-closed arms for the F-8(b) linter, whose central property is that IT CANNOT PASS.

The arms that matter are the ones in the direction the guard ACTS, so every refusal here has a
paired silent-on-good arm, and the transclusion arm is the opposite-direction case an obvious
implementation misses: all four spots ARE present and it must still refuse.

The arm this file exists for, though, is `TheLinterHasNoGreen`. The independent §10.1 readiness
review ruled the previous `rc=0` a fail-open gate, so "returns 0 on good prose" is no longer a
property to test -- it is the defect. `test_no_input_whatsoever_can_produce_exit_zero` is the
encoded form of that ruling.

The two recorded adversarial examples are read FROM THE GRADER'S OWN VERDICT FILE and its digest is
asserted, so this suite also enforces their preservation. One of the two does not reproduce; see
`TheRecordedBreaksAsMeasured`, which records what each actually returns rather than what the verdict
says it returned.
"""
from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import pathlib
import re
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location(
    "vrrbs", HERE / "verify_run_receipt_blind_spots.py")
V = importlib.util.module_from_spec(_spec)
sys.modules["vrrbs"] = V
_spec.loader.exec_module(V)

VERDICT_REL = "runs/agy-capacity-probe/20260826-f8b-VERDICT.md"
VERDICT_SHA256 = "cab5b89636f8396c0e04cd526c6316ae84e82458b387d2cf1f1c7f0fcb8c084c"

# A compliant section: all four concepts, in wording that is nobody's copy.
GOOD = """## Blind spots this run could not see

Four things stayed outside what the guard measured, and none of them is closed by this run.

First, namespace packages. When a portion has no `__init__.py` the loader hands back a spec whose
origin is None, so `spec.origin` never reaches the root comparison and a portion resolving from a
foreign checkout is waved through. Narrow, because a real module later on the path outranks a
portion -- but unmeasured here.

Second, whatever was already resident in `sys.modules` at the moment `install(` ran. The wrapper's
own imports were resolved by the unwrapped finder and the guard is structurally blind to them.

Third, any further subprocess. A child interpreter is a fresh process and nothing it imports is
visible to this one.

Fourth, the `.sh` route. Nothing measured here speaks to shell-side resolution at all.
"""

MISSING_SHELL = GOOD.replace(
    "Fourth, the `.sh` route. Nothing measured here speaks to shell-side resolution at all.", "")
MISSING_NAMESPACE = GOOD.replace("namespace packages", "package layout").replace(
    "origin is None", "loader returns early").replace(
    "`spec.origin` never reaches the root comparison", "the comparison never runs")

SOURCE = """### 1.6 P-5 — THE BLIND SPOTS, IN MY OWN WORDS

The inventory cannot see four things, and none of them is closed here. Namespace packages, because
`spec.origin` is None for them and `find_spec` returns before the checkout root is reached, so a
namespace portion resolving from the wrong checkout is not refused. Modules already in `sys.modules`
when `install(` runs, which were imported before the guard existed and are invisible to it. Anything
in a further subprocess, which is a separate interpreter entirely. And the `.sh` route, B-5, about
which nothing in this receipt speaks at all.

### 1.7 Something else
"""

# A keyword stuffer that DOES satisfy every concept group -- the recorded BREAK 1 does not, see
# below. One line, no content, and the old instrument returned 0 for it (measured).
STUFFER_THAT_WORKS = ("# blind spots\n"
                      "namespace origin is none sys.modules install( child process .sh\n")


def wrap(section_body: str) -> str:
    return "# Run receipt\n\n## Environment\n\nstuff\n\n" + section_body + "\n## Next section\n\nx\n"


def recorded_break_texts():
    """The two adversarial texts, read from the grader's verdict file, digest asserted.

    Read rather than copied: a copy in this file could drift from the evidence, and the
    authorization requires the originals be preserved. If the verdict file is edited or removed,
    these arms fail loudly, which is the intended coupling.
    """
    p = HERE / VERDICT_REL
    raw = p.read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    if got != VERDICT_SHA256:
        raise AssertionError(
            "the preserved F-8(b) verdict file changed: %s has sha256 %s, expected %s. The two "
            "adversarial examples must be preserved verbatim." % (VERDICT_REL, got, VERDICT_SHA256))
    text = raw.decode("utf-8")
    blocks = re.findall(r"^  ```\n(.*?)^  ```\n", text, re.S | re.M)
    assert len(blocks) == 2, "expected exactly 2 fenced break texts, found %d" % len(blocks)
    return ["\n".join(ln[2:] if ln.startswith("  ") else ln for ln in b.split("\n"))
            for b in blocks]


class TheLinterHasNoGreen(unittest.TestCase):
    """The §10.1 ruling, encoded. A green result is the defect, not the success case."""

    def test_no_exit_constant_in_the_module_is_zero(self):
        names = [n for n in dir(V) if n.endswith("_EXIT")]
        self.assertGreaterEqual(len(names), 5, names)
        for n in names:
            self.assertNotEqual(getattr(V, n), 0,
                                "%s is 0; the linter must have no passing status" % n)

    def test_no_input_whatsoever_can_produce_exit_zero(self):
        inputs = [
            ("good prose", wrap(GOOD), SOURCE),
            ("no section", wrap("## Results\n\nall fine\n"), SOURCE),
            ("empty section", wrap("## Blind spots\n\n"), SOURCE),
            ("missing a spot", wrap(MISSING_SHELL), SOURCE),
            ("missing another", wrap(MISSING_NAMESPACE), SOURCE),
            ("full paste", wrap("## Blind spots\n\n" + V.extract_section(SOURCE, "BLIND SPOTS")),
             SOURCE),
            ("no source section", wrap(GOOD), "# nothing\n"),
            ("keyword stuffer", STUFFER_THAT_WORKS, SOURCE),
            ("empty receipt", "", SOURCE),
        ] + [("recorded break %d" % (i + 1), t, SOURCE)
             for i, t in enumerate(recorded_break_texts())]
        seen = set()
        for label, receipt, source in inputs:
            rc, notes, _ = V.lint(receipt, source)
            self.assertNotEqual(rc, 0, "%s produced exit 0: %s" % (label, notes))
            seen.add(rc)
        self.assertIn(V.REVIEW_REQUIRED_EXIT, seen, "no arm reached REVIEW_REQUIRED; suite is blind")
        self.assertGreaterEqual(len(seen), 4, "arms did not separate the outcome codes: %s" % seen)

    def test_the_best_possible_outcome_is_REVIEW_REQUIRED(self):
        rc, notes, facts = V.lint(wrap(GOOD), SOURCE)
        self.assertEqual(rc, V.REVIEW_REQUIRED_EXIT, notes)
        self.assertEqual(facts["spots_unaddressed"], [], facts)

    def test_the_review_required_report_denies_being_a_pass(self):
        with tempfile.TemporaryDirectory() as d:
            r = pathlib.Path(d) / "receipt.md"
            s = pathlib.Path(d) / "source.md"
            rep = pathlib.Path(d) / "report.json"
            r.write_text(wrap(GOOD), encoding="utf-8")
            s.write_text(SOURCE, encoding="utf-8")
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = V.main(["--receipt", str(r), "--source", str(s), "--report", str(rep)])
            self.assertEqual(rc, V.REVIEW_REQUIRED_EXIT)
            self.assertIn("NOT A PASS", buf.getvalue())
            report = json.loads(rep.read_text(encoding="utf-8"))
            self.assertEqual(report["status"], "REVIEW_REQUIRED")
            self.assertIn("NOT compliance with F-8(b)", report["this_is_not_a_pass"])
            self.assertIn("verify_f8b_attestation.py", report["this_is_not_a_pass"])

    def test_the_report_binds_the_exact_receipt_bytes(self):
        with tempfile.TemporaryDirectory() as d:
            r = pathlib.Path(d) / "receipt.md"
            s = pathlib.Path(d) / "source.md"
            rep = pathlib.Path(d) / "report.json"
            body = wrap(GOOD)
            r.write_text(body, encoding="utf-8")
            s.write_text(SOURCE, encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                V.main(["--receipt", str(r), "--source", str(s), "--report", str(rep)])
            report = json.loads(rep.read_text(encoding="utf-8"))
            self.assertEqual(report["receipt_sha256"],
                             hashlib.sha256(body.encode("utf-8")).hexdigest())
            # and it MOVES when the receipt does: a binding that never changes binds nothing
            r.write_text(body + "\ntrailing edit\n", encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                V.main(["--receipt", str(r), "--source", str(s), "--report", str(rep)])
            self.assertNotEqual(json.loads(rep.read_text(encoding="utf-8"))["receipt_sha256"],
                                report["receipt_sha256"])


class TheRecordedBreaksAsMeasured(unittest.TestCase):
    """What the two recorded examples ACTUALLY return. One of them contradicts the verdict file.

    The grader's verdict records `rc=0` for both. Measured here: BREAK 2 did return 0 on the old
    instrument, BREAK 1 never did -- its stuffing string contains neither `namespace` nor any
    already-imported alternate, so the old instrument refused it as INCOMPLETE. The keyword-stuffing
    CLASS is nonetheless real: `STUFFER_THAT_WORKS` adds the two missing words and nothing else, and
    the old instrument returned 0 for it. These arms hold that distinction in place so the record
    cannot re-acquire the wrong claim.
    """

    def test_recorded_break_1_is_refused_as_INCOMPLETE_contrary_to_the_verdict(self):
        b1 = recorded_break_texts()[0]
        rc, notes, facts = V.lint(b1, SOURCE)
        self.assertEqual(rc, V.INCOMPLETE_EXIT, notes)
        self.assertEqual(sorted(facts["spots_unaddressed"]),
                         ["already-imported-modules", "namespace-packages"], facts)

    def test_recorded_break_2_the_moral_paste_reaches_only_REVIEW_REQUIRED(self):
        b2 = recorded_break_texts()[1]
        rc, notes, facts = V.lint(b2, SOURCE)
        self.assertEqual(rc, V.REVIEW_REQUIRED_EXIT, notes)
        self.assertNotEqual(rc, 0, "the demonstrated fail-open must no longer be green")
        self.assertLess(facts["longest_shared_span"], V.TRANSCLUSION_SPAN,
                        "control: this text must genuinely slip under the span threshold, "
                        "otherwise the arm proves nothing about the fail-open mode")

    def test_a_working_keyword_stuffer_reaches_only_REVIEW_REQUIRED(self):
        rc, notes, facts = V.lint(STUFFER_THAT_WORKS, SOURCE)
        self.assertEqual(rc, V.REVIEW_REQUIRED_EXIT, notes)
        self.assertEqual(facts["spots_unaddressed"], [],
                         "control: the stuffer must satisfy every concept group, else it is not "
                         "an instance of the fail-open class at all")


class TheRefusalsStayDISTINCT(unittest.TestCase):
    """Absent, incomplete and copied are different defects. Collapsing them hides which fired."""

    def test_a_receipt_with_NO_blind_spots_section_is_NO_SECTION(self):
        rc, notes, _ = V.lint(wrap("## Results\n\nall fine\n"), SOURCE)
        self.assertEqual(rc, V.NO_SECTION_EXIT, notes)
        self.assertIn("NO SECTION", " ".join(notes))

    def test_an_EMPTY_section_is_NO_SECTION_not_an_empty_set_of_blind_spots(self):
        rc, notes, _ = V.lint(wrap("## Blind spots\n\n"), SOURCE)
        self.assertEqual(rc, V.NO_SECTION_EXIT, notes)

    def test_a_MISSING_blind_spot_is_INCOMPLETE_and_is_NAMED(self):
        rc, notes, facts = V.lint(wrap(MISSING_SHELL), SOURCE)
        self.assertEqual(rc, V.INCOMPLETE_EXIT, notes)
        self.assertIn("shell-route", facts["spots_unaddressed"])

    def test_a_SECOND_missing_spot_is_caught_too_so_the_first_is_not_a_fluke(self):
        rc, notes, facts = V.lint(wrap(MISSING_NAMESPACE), SOURCE)
        self.assertEqual(rc, V.INCOMPLETE_EXIT, notes)
        self.assertIn("namespace-packages", facts["spots_unaddressed"])

    def test_the_four_refusal_codes_are_pairwise_distinct(self):
        codes = [V.REVIEW_REQUIRED_EXIT, V.CANNOT_CHECK_EXIT, V.NO_SECTION_EXIT,
                 V.INCOMPLETE_EXIT, V.TRANSCLUDED_EXIT]
        self.assertEqual(len(set(codes)), len(codes), codes)


class TheOppositeDirectionArm(unittest.TestCase):
    """All four spots present AND still refused. An obvious implementation misses this."""

    def test_a_TRANSCLUDED_section_is_refused_even_though_all_four_are_present(self):
        pasted = "## Blind spots\n\n" + V.extract_section(SOURCE, "BLIND SPOTS")
        precheck, _, _ = V.lint(wrap(pasted), "### nothing here\n")
        self.assertEqual(precheck, V.CANNOT_CHECK_EXIT,
                         "control: with no source section the transclusion arm must not run")
        rc, notes, _ = V.lint(wrap(pasted), SOURCE)
        self.assertEqual(rc, V.TRANSCLUDED_EXIT, notes)
        self.assertIn("TRANSCLUDED", " ".join(notes))

    def test_the_transclusion_arm_survives_reflowing_and_case(self):
        body = V.extract_section(SOURCE, "BLIND SPOTS")
        mangled = body.replace("\n", "  ").upper()
        rc, notes, _ = V.lint(wrap("## Blind spots\n\n" + mangled), SOURCE)
        self.assertEqual(rc, V.TRANSCLUDED_EXIT, notes)


class TheCheckCannotPassWhenItCannotLook(unittest.TestCase):
    def test_an_unreadable_receipt_is_CANNOT_CHECK(self):
        rc = V.main(["--receipt", str(HERE / "no_such_receipt_xyz.md")])
        self.assertEqual(rc, V.CANNOT_CHECK_EXIT)

    def test_a_source_without_the_section_is_CANNOT_CHECK(self):
        rc, notes, _ = V.lint(wrap(GOOD), "# a source with no such heading\n")
        self.assertEqual(rc, V.CANNOT_CHECK_EXIT, notes)
        self.assertIn("CANNOT CHECK", " ".join(notes))


class TheRootIsDerivedNotHardcoded(unittest.TestCase):
    """OI-136. A hardcoded checkout root is the defect this campaign exists around."""

    def test_no_absolute_cluster_root_literal_appears_in_the_instrument(self):
        for name in ("verify_run_receipt_blind_spots.py", "verify_f8b_attestation.py"):
            src = (HERE / name).read_text(encoding="utf-8")
            root = "/" + "/".join(("pscratch", "sd", "j", "josephrb"))
            self.assertNotIn(root, src, "%s hardcodes a cluster root" % name)
            self.assertIn("parents[2]", src, "%s must DERIVE the repo root from __file__" % name)


if __name__ == "__main__":
    unittest.main(verbosity=2)
