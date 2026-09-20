#!/usr/bin/env python3
"""The unsigned adoption draft must be REFUSED as written, and ACCEPTED after Joseph's one edit.

WHY A TEST AND NOT A SENTENCE. The draft's whole safety property is that a script cannot read it as
an executed adoption. A claim to that effect is worth nothing without the script's own patterns
applied to the draft's own bytes -- and the campaign has the shape on record: a control that was
never run reported what its author expected.

⚠ THE PATTERNS ARE EXTRACTED FROM `run_m1_projection.sh`, NOT RETYPED. A rule retyped is a second
implementation that does not change when the first is corrected. If the launcher's sentinel or
negation regex is edited, these tests read the new one -- and the extraction itself is asserted, so
a launcher that stops carrying them fails here rather than silently testing nothing.
"""
import re
import subprocess
import sys
import unittest
from pathlib import Path

ND = Path(__file__).resolve().parents[1]
REPO = ND.parent
LAUNCHER = ND / "run_m1_projection.sh"
DRAFT = REPO / "docs" / "orchestration" / \
    "DRAFT-ADOPTION-20260919-z-cv-under-the-6.4-exception.md"
EXECUTED = REPO / "docs" / "orchestration" / \
    "DECISION-20260920-joseph-adopts-z-cv-under-the-6.4-exception.md"
DIGEST = "3d7465f66fbe66b0dfcf09b6fc51249f227fb33e97ae40bc78dda90275e918c5"


def _ere_to_python(pattern):
    """POSIX ERE -> Python re. Only the class names the launcher actually uses."""
    return pattern.replace("[[:space:]]", r"\s")


def launcher_patterns():
    """The two regexes the adoption guard runs, read out of the launcher."""
    text = LAUNCHER.read_text(encoding="utf-8")
    sentinel = re.search(r"grep -nE '([^']+)' \"\$ADOPTION\"", text)
    negation = re.search(r"grep -qiE '([^']+)'", text)
    assert sentinel, "the launcher no longer carries a sentinel grep -- this test is now blind"
    assert negation, "the launcher no longer carries a negation grep -- this test is now blind"
    return (re.compile(_ere_to_python(sentinel.group(1))),
            re.compile(_ere_to_python(negation.group(1)), re.IGNORECASE))


def verdict(text):
    """Reproduce the launcher's three-step decision over a record's text."""
    sentinel_re, negation_re = launcher_patterns()
    lines = [ln for ln in text.splitlines() if sentinel_re.search(ln)]
    if not lines:
        return "REFUSED: no sentinel"
    if any(negation_re.search(ln) for ln in lines):
        return "REFUSED: negated, provisional or held"
    if not any(DIGEST in ln for ln in lines):
        return "REFUSED: does not name the measured digest"
    return "ACCEPTED"


ADOPT_EDIT = "ADOPTS-SHA256: DRAFT -- NOT SIGNED -- ", "ADOPTS-SHA256: "


class TheDraftCannotBeUsedAsAnAdoption(unittest.TestCase):
    def setUp(self):
        self.assertTrue(DRAFT.is_file(), f"{DRAFT} is missing")
        self.text = DRAFT.read_text(encoding="utf-8")

    def test_the_extraction_itself_works(self):
        """POSITIVE CONTROL on the instrument: a blind test reports what its author expected."""
        sentinel_re, negation_re = launcher_patterns()
        self.assertTrue(sentinel_re.search("ADOPTS-SHA256: " + DIGEST))
        self.assertTrue(negation_re.search("ADOPTS-SHA256: DRAFT -- x"))
        self.assertFalse(negation_re.search("ADOPTS-SHA256: " + DIGEST))

    def test_the_draft_as_written_is_REFUSED(self):
        self.assertEqual(verdict(self.text), "REFUSED: negated, provisional or held")

    def test_it_carries_EXACTLY_ONE_sentinel_line(self):
        """A second, un-negated sentinel anywhere in the file would be an adoption by accident."""
        sentinel_re, _ = launcher_patterns()
        hits = [ln for ln in self.text.splitlines() if sentinel_re.search(ln)]
        self.assertEqual(len(hits), 1, f"expected one sentinel line, got {hits}")

    def test_it_names_the_right_digest(self):
        self.assertIn(DIGEST, self.text)
        self.assertEqual(self.text.count(DIGEST), 3,
                         "the digest appears in the sentinel, the exception scope and the "
                         "identity table -- change this count deliberately, not by accident")

    def test_ONE_EDIT_makes_it_an_adoption_and_nothing_else_is_needed(self):
        """The other direction, which is what makes this a draft rather than a refusal."""
        edited = self.text.replace(*ADOPT_EDIT)
        self.assertNotEqual(edited, self.text, "the documented edit did not apply")
        self.assertEqual(verdict(edited), "ACCEPTED")

    def test_the_edit_documented_in_section_7_is_the_edit_that_works(self):
        """§7 tells Joseph to delete the four words before the digest. Measured, not described."""
        line = next(ln for ln in self.text.splitlines() if "ADOPTS-SHA256" in ln)
        before = line.split("ADOPTS-SHA256:", 1)[1].strip()
        words = before.split(DIGEST)[0].split()
        self.assertEqual(words, ["DRAFT", "--", "NOT", "SIGNED", "--"],
                         "§7 says four words; keep the text and the file in agreement")

    def test_a_record_with_no_sentinel_is_refused(self):
        self.assertEqual(verdict("# a record that says nothing"), "REFUSED: no sentinel")

    def test_a_sentinel_naming_another_digest_is_refused(self):
        self.assertEqual(verdict("ADOPTS-SHA256: " + "a" * 64),
                         "REFUSED: does not name the measured digest")


class TheDraftIsRegisteredAndSaysWhatItIs(unittest.TestCase):
    def test_it_is_in_the_manifest_overrides(self):
        rows = (REPO / "docs" / "orchestration" / "MANIFEST-overrides.tsv").read_text()
        self.assertIn(DRAFT.name, rows,
                      "an unregistered doc is invisible to the router")

    def test_it_states_that_it_adopts_nothing_as_it_stands(self):
        text = DRAFT.read_text(encoding="utf-8")
        self.assertIn("ADOPTS NOTHING AS IT STANDS", text.upper())
        self.assertIn("UNRESOLVED", text)
        self.assertIn("NON-PASSING", text)

    def test_it_does_not_claim_the_exception_generalises(self):
        text = DRAFT.read_text(encoding="utf-8")
        self.assertIn("and nothing else", text)


class TheEXECUTEDRecordIsAcceptedAndCarriesWhatItMust(unittest.TestCase):
    """Joseph adopted on 2026-09-20. The draft's refusal was the safety property; THIS file's
    ACCEPTANCE is the other half, and it is asserted with the launcher's own patterns rather than
    by reading the file and believing it."""

    def setUp(self):
        self.assertTrue(EXECUTED.is_file(), f"{EXECUTED} is missing")
        self.text = EXECUTED.read_text(encoding="utf-8")

    def test_the_launcher_would_ACCEPT_it(self):
        self.assertEqual(verdict(self.text), "ACCEPTED")

    def test_the_draft_STILL_refuses_so_both_directions_are_live(self):
        self.assertEqual(verdict(DRAFT.read_text(encoding="utf-8")),
                         "REFUSED: negated, provisional or held")

    def test_it_carries_exactly_one_sentinel_line(self):
        sentinel_re, _ = launcher_patterns()
        hits = [ln for ln in self.text.splitlines() if sentinel_re.search(ln)]
        self.assertEqual(len(hits), 1, f"expected one sentinel, got {hits}")

    def test_it_names_ONLY_the_adopted_digest_in_that_line(self):
        sentinel_re, _ = launcher_patterns()
        line = next(ln for ln in self.text.splitlines() if sentinel_re.search(ln))
        self.assertEqual(re.findall(r"[0-9a-f]{64}", line), [DIGEST])

    def test_the_defect_travels_with_the_decision(self):
        """DECISION-PACKET 10.2: the UNRESOLVED status in the same place as the adoption."""
        for token in ("UNRESOLVED", "4c", "NON-PASSING", "predeclared, not computed"):
            self.assertIn(token, self.text, f"{token!r} missing from the adoption record")

    def test_all_four_measurements_are_present_with_their_numbers(self):
        """Joseph: measurements, not caveats -- so each must carry its figure."""
        for token in ("6.145%", "6.04% ± 0.39%", "p = 0.000", "p = 1.467",
                      "26.0%", "6.75%", "0.761%", "6.02%", "49.8%"):
            self.assertIn(token, self.text, f"measurement {token!r} missing")

    def test_it_states_the_seed_pair_width_is_unmeasured(self):
        self.assertIn("UNMEASURED", self.text)
        self.assertIn("one seed pair", self.text.lower())

    def test_it_does_not_extend_the_exception_to_the_campaign_digests(self):
        for other in ("361090f9", "7e4636a3"):
            self.assertIn(other, self.text, "the excluded digests must be named to be excluded")
        self.assertIn("and nothing else", self.text)

    def test_it_withholds_the_analysis_note_push(self):
        self.assertIn("analysis-note push", self.text)


if __name__ == "__main__":
    unittest.main()
