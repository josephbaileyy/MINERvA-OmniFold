"""Fail-closed arms for the F-8(b) blind-spots check.

The arms that matter are the ones in the direction the guard ACTS. A check that only proves it
passes on good input has not been shown to refuse anything, so every refusal here has a paired
silent-on-good arm, and the transclusion arm is the opposite-direction case an obvious
implementation misses: all four spots ARE present and it must still refuse.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys
import unittest

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location(
    "vrrbs", HERE / "verify_run_receipt_blind_spots.py")
V = importlib.util.module_from_spec(_spec)
sys.modules["vrrbs"] = V
_spec.loader.exec_module(V)

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


def wrap(section_body: str) -> str:
    return "# Run receipt\n\n## Environment\n\nstuff\n\n" + section_body + "\n## Next section\n\nx\n"


class TheGuardRefusesInTheDirectionItActs(unittest.TestCase):
    def test_a_receipt_with_NO_blind_spots_section_is_a_VIOLATION(self):
        rc, notes = V.check(wrap("## Results\n\nall fine\n"), SOURCE)
        self.assertEqual(rc, V.VIOLATION_EXIT, notes)
        self.assertIn("no blind-spots section", " ".join(notes))

    def test_an_EMPTY_blind_spots_section_is_a_VIOLATION_not_an_empty_set(self):
        rc, notes = V.check(wrap("## Blind spots\n\n"), SOURCE)
        self.assertEqual(rc, V.VIOLATION_EXIT, notes)

    def test_a_MISSING_blind_spot_is_named_not_merely_counted(self):
        rc, notes = V.check(wrap(MISSING_SHELL), SOURCE)
        self.assertEqual(rc, V.VIOLATION_EXIT, notes)
        self.assertIn("shell-route", " ".join(notes))

    def test_a_SECOND_missing_spot_is_caught_too_so_the_first_is_not_a_fluke(self):
        rc, notes = V.check(wrap(MISSING_NAMESPACE), SOURCE)
        self.assertEqual(rc, V.VIOLATION_EXIT, notes)
        self.assertIn("namespace-packages", " ".join(notes))


class TheOppositeDirectionArm(unittest.TestCase):
    """All four spots present AND still refused. An obvious implementation misses this."""

    def test_a_TRANSCLUDED_section_is_refused_even_though_all_four_are_present(self):
        pasted = "## Blind spots\n\n" + V.extract_section(SOURCE, "BLIND SPOTS")
        precheck, _ = V.check(wrap("## Blind spots\n\n" + V.extract_section(SOURCE, "BLIND SPOTS")),
                              "### nothing here\n")
        self.assertEqual(precheck, V.CANNOT_CHECK_EXIT,
                         "control: with no source section the transclusion arm must not run")
        rc, notes = V.check(wrap(pasted), SOURCE)
        self.assertEqual(rc, V.VIOLATION_EXIT, notes)
        self.assertIn("TRANSCLUDED", " ".join(notes))

    def test_the_transclusion_arm_survives_reflowing_and_case(self):
        body = V.extract_section(SOURCE, "BLIND SPOTS")
        mangled = body.replace("\n", "  ").upper()
        rc, notes = V.check(wrap("## Blind spots\n\n" + mangled), SOURCE)
        self.assertEqual(rc, V.VIOLATION_EXIT, notes)
        self.assertIn("TRANSCLUDED", " ".join(notes))


class TheGuardIsSilentOnGoodInput(unittest.TestCase):
    def test_an_authored_section_covering_all_four_PASSES(self):
        rc, notes = V.check(wrap(GOOD), SOURCE)
        self.assertEqual(rc, V.OK_EXIT, notes)

    def test_the_pass_states_what_it_does_NOT_prove(self):
        import io
        import contextlib
        tmp = HERE / "_f8b_fixture_receipt.md"
        src = HERE / "_f8b_fixture_source.md"
        tmp.write_text(wrap(GOOD), encoding="utf-8")
        src.write_text(SOURCE, encoding="utf-8")
        try:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = V.main(["--receipt", str(tmp), "--source", str(src)])
            self.assertEqual(rc, V.OK_EXIT)
            self.assertIn("NOT A DISCHARGE", buf.getvalue())
        finally:
            tmp.unlink(missing_ok=True)
            src.unlink(missing_ok=True)


class TheCheckCannotPassWhenItCannotLook(unittest.TestCase):
    def test_an_unreadable_receipt_is_CANNOT_CHECK_never_a_pass(self):
        rc = V.main(["--receipt", str(HERE / "no_such_receipt_xyz.md")])
        self.assertEqual(rc, V.CANNOT_CHECK_EXIT)

    def test_a_source_without_the_section_is_CANNOT_CHECK_never_a_pass(self):
        rc, notes = V.check(wrap(GOOD), "# a source with no such heading\n")
        self.assertEqual(rc, V.CANNOT_CHECK_EXIT, notes)
        self.assertIn("cannot locate", " ".join(notes))


class TheRootIsDerivedNotHardcoded(unittest.TestCase):
    """OI-136. A hardcoded checkout root is the defect this campaign exists around."""

    def test_no_absolute_cluster_root_literal_appears_in_the_instrument(self):
        src = (HERE / "verify_run_receipt_blind_spots.py").read_text(encoding="utf-8")
        root = "/" + "/".join(("pscratch", "sd", "j", "josephrb"))
        self.assertNotIn(root, src, "the instrument hardcodes a cluster root")
        self.assertIn("parents[2]", src, "the repo root must be DERIVED from __file__")


if __name__ == "__main__":
    unittest.main(verbosity=2)
