#!/usr/bin/env python3
"""Write VARIANTS.txt, the readers' file, from build_cases.py's passages.json. No internal names may print.

usage: write_variants.py <passages.json> <VARIANTS.txt>   (exit 1 if a passage is missing or a banned term prints)
"""
import json
import re
import sys
from pathlib import Path

HEAD = """PRE-WRITTEN OUTCOME CASES OF THE MANUSCRIPT

Some results in the manuscript have not come in yet. Where the manuscript shows "[PENDING: ...]", the text for each
possible outcome is already written, and one version will print when the result arrives. This file gives each
version as it would print, under a plain-language label for its outcome.

How the text was made: the manuscript was built once per outcome, and each passage below was copied from that build.

Square brackets mark placeholders. Any text in square brackets, such as "[cells R03, R11]" or "[falls / rises / does
not change]", is a made-up stand-in for a value that does not exist yet. It is not a result.

The manuscript and its Supplement accompany this file. Apart from Table 1 (Part 4), no sentence that is not shown
here changes with these outcomes.
"""

PR2B = "[falls / rises / does not change]"


def ibu_sentence(s):
    """The second clause of each IBU sentence is its own reading, with three forms; show it as a bracketed choice."""
    s = s.replace("and its retention does not change with longer iteration;",
                  f"and its retention {PR2B} with longer iteration;")
    return s.replace("and its retention does not change.", f"and its retention {PR2B}.")


def main(argv):
    res = json.loads(Path(argv[1]).read_text())
    P = lambda case, p: res[case]["passages"][p]  # noqa: E731
    out = [HEAD]

    out.append("""
======================================================================================================================
PART 1. THE ABSTRACT: THE SENTENCE ON THE FIVE-OBSERVABLE COVERAGE TEST
======================================================================================================================

It follows this sentence, which prints in every outcome: "The procedure's two-dimensional covariance, rebuilt at each
of two held-out generator tunes, under-covers at both; coverage of the reported five-observable intervals is not
established."
""")
    for lab, case in (("A1. The test covers at both tunes", "cov-both-cover"),
                      ("A2. The test under-covers at one of the two tunes", "cov-one-under-cells"),
                      ("A3. The test under-covers at both tunes", "cov-both-under-joint"),
                      ("A4. The test is invalid by its own controls", "cov-invalid"),
                      ("A5. The test stopped before any pseudo-experiment ran", "cov-gate-failed")):
        out.append(f"{lab}\n\n    {P(case, 'abstract-coverage')}\n")
    out.append("""In A1 to A4, "covers" and "under-covers" refer to the test's primary variant, the one without the two GEANT4
bands (section 6.3).
""")

    out.append("""
======================================================================================================================
PART 2. SECTION 6.3, "A LIKE-FOR-LIKE FIVE-OBSERVABLE COVERAGE TEST": THE RESULT
======================================================================================================================

The text below follows the section's fixed paragraph, which ends "...and neither outcome bears on the reported
intervals at the data or on the ensemble average." It ends the section. G18_10a_02_11b and AR23_20i_00_000 are the
two held-out tunes. "Without the two bands" is the test's primary variant.

The test ran to a result:
""")
    for lab, case in (("B1. Both tunes covered, in both variants", "cov-both-cover"),
                      ("B2. One tune under-covers in some cells; the other covers (both variants alike)", "cov-one-under-cells"),
                      ("B3. Both tunes under-cover, jointly and in some cells (both variants alike)", "cov-both-under-joint"),
                      ("B4. The test is invalid by its own controls (both tunes, both variants)", "cov-invalid"),
                      ("B5. The primary variant covers at both tunes; the variant with the bands under-covers in some cells at one tune",
                       "cov-mixed-primary-covers")):
        out.append(f"{lab}\n\n    {P(case, 'sec-coverage')}\n")
    out.append("""The abstract prints A1 in case B5.

The test stopped before any pseudo-experiment ran (the abstract prints A5 in each of these):
""")
    for lab, case in (("B6. Stopped at a gate", "cov-gate-failed"),
                      ("B7. Stopped when a check of the clipping offset exceeded its bound", "cov-to-joseph"),
                      ("B8. Stopped at another stopping point", "cov-stop")):
        out.append(f"{lab}\n\n    {P(case, 'sec-coverage')}\n")

    out.append("""
======================================================================================================================
PART 3. THE STUDY OF WHAT CHANGES THE RETAINED PRIOR: THE BINNED ITERATIVE UNFOLDING (IBU) AGAINST THE ESTIMATOR
======================================================================================================================

Each case is shown at both flagged truths, the GiBUU hybrid truth and the q3 tilt. The two truths are read separately,
so they can differ. Within each sentence, "[falls / rises / does not change]" is a separate reading with three
pre-written forms.
""")
    for lab, case in (("C1. The IBU retains less of the prior than the estimator", "ibu-less"),
                      ("C2. The IBU retains as much of the prior as the estimator", "ibu-same"),
                      ("C3. The IBU retains more of the prior than the estimator", "ibu-more")):
        out.append(f"{lab}\n\n  Abstract:\n\n    {P(case, 'abstract-ibu')}\n\n  Section 5.3, end of the section:\n\n"
                   f"    {ibu_sentence(P(case, 'sec-ibu'))}\n")
    out.append("""In C1, the last two sentences print because, by the study's rule fixed in advance, a lower retention for the IBU
means its readings are consistent with a share specific to the implementation. In C2 and C3, those sentences print
only if another reading of the study gives the same label.
""")

    out.append("""
======================================================================================================================
PART 4. OTHER SENTENCES
======================================================================================================================

No sentence of the Discussion and conclusions (section 7), and no other sentence of the manuscript's prose, changes
with the outcomes shown here. Table 1's rows for these two studies also change with them; they are not part of this
read. Two other pending results have their own pre-written text, which is not part of this read either: the other
readings of the prior-retention study (section 5.3), and a per-cell validity rule (section 5.4).
""")
    text = "\n".join(out)
    banned = [r"\bLL5D\b", r"\bFD-PRR\b", r"\bPRR\b", r"\bV-HALF\b", r"\bVHALF\b", r"\bCOV2D\b", r"\bENS1\b",
              r"minus2", r"\\fv", r"\b(prr|ll5d|vhalf)-", r"[Jj]oseph", r"director", r"\bPR-[123]",
              r"under-cells|under-joint|gate-failed|not-graded|both-cover|one-under|both-under", r"\?\?"]
    bad = [b for b in banned if re.search(b, text)]
    if bad:
        sys.exit(f"write_variants: banned terms print: {bad}")
    Path(argv[2]).write_text(text)
    print(f"wrote {argv[2]}: {len(text.split())} words")


if __name__ == "__main__":
    main(sys.argv)
