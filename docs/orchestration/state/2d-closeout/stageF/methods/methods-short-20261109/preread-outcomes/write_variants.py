#!/usr/bin/env python3
"""Write VARIANTS.txt, the readers' file, from build_cases.py's passages.json. No internal names may print.

usage: write_variants.py <worktree> <passages.json> <VARIANTS.txt>
       (exit 1 if a passage is missing, a banned term prints, or check_round's check 8 finds a class name)
"""
import importlib.util
import json
import re
import sys
from pathlib import Path

HEAD = """THE MANUSCRIPT'S PRE-WRITTEN CASES FOR RESULTS STILL TO COME

Some results in the manuscript have not come in yet. Where the manuscript shows "[PENDING: ...]", the text for each
possible outcome is already written, and one version will print when the result arrives. This file gives each
version as it would print, under a plain-language label for its outcome.

How the text was made: the manuscript was built once per outcome, and each passage below was copied from that build.

Square brackets mark placeholders. Any text in square brackets, such as "[cells R03, R11]" or "[the check]", is a
made-up stand-in for a value that does not exist yet. It is not a result.

The manuscript and its Supplement accompany this file. No sentence that is not shown here changes with these
outcomes (Part 5 lists the other pending text).
"""

RULE = "=" * 118


def part(title, intro):
    return f"\n{RULE}\n{title}\n{RULE}\n\n{intro}\n"


def main(argv):
    wt, res = Path(argv[1]), json.loads(Path(argv[2]).read_text())

    def P(case, p):
        try:
            return res[case]["passages"][p]
        except KeyError:
            sys.exit(f"write_variants: no passage {p} in case {case}")

    out = [HEAD]
    out.append(part("PART 1. THE ABSTRACT: THE SENTENCE ON THE FIVE-OBSERVABLE COVERAGE TEST",
                    'It follows this sentence, which prints in every outcome: "The procedure\'s two-dimensional covariance, rebuilt at each\n'
                    'of two held-out generator tunes, under-covers at both; coverage of the reported five-observable intervals is not\n'
                    'established." The test has two variants: a primary one, without two bands of the detector simulation\'s\n'
                    "uncertainties, and one with them.\n"))
    for lab, case in (
            ("AB1. Both tunes covered, in both variants", "cov-both-cover"),
            ("AB2. The primary variant covers at both tunes; with the bands, it under-covers at one", "cov-bands-under-one"),
            ("AB3. The primary variant covers at both tunes; with the bands, it under-covers at both", "cov-bands-under-both"),
            ("AB4. The primary variant covers at both tunes; with the bands, the test is invalid at one", "cov-bands-invalid-one"),
            ("AB5. The primary variant covers at both tunes; with the bands, the test is invalid at both", "cov-bands-invalid-both"),
            ("AB6. The primary variant under-covers at one tune", "cov-one-under-cells"),
            ("AB7. The primary variant under-covers at both tunes", "cov-both-under-joint"),
            ("AB8. The test is invalid at one tune, and the primary variant covers at the other", "cov-invalid-one-covers"),
            ("AB9. The test is invalid at one tune, and the primary variant under-covers at the other", "cov-invalid-one-under"),
            ("AB10. The test is invalid at both tunes", "cov-invalid-both"),
            ("AB11. The test stopped before any pseudo-experiment ran", "cov-gate-failed"),
            ("AB12. The test stopped after a check, before most of its pseudo-experiments ran", "cov-offset-stopped")):
        out.append(f"{lab}\n\n    {P(case, 'abstract-coverage')}\n")

    out.append(part('PART 2. SECTION 6.3, "A LIKE-FOR-LIKE FIVE-OBSERVABLE COVERAGE TEST": THE RESULT',
                    "The text below follows the section's fixed paragraph, which ends \"...shares its 2p2h model family with one of the\n"
                    'generators of Cmodel." It ends the section. G18_10a_02_11b and AR23_20i_00_000 are the two held-out tunes.\n'
                    '"Without the two bands" is the test\'s primary variant.\n\nThe test ran to a result:\n'))
    for lab, case in (
            ("SC1. Both tunes covered, in both variants", "cov-both-cover"),
            ("SC2. Both tunes covered, in both variants, with some passes weakened and some over-coverage", "cov-both-cover-qualified"),
            ("SC3. The primary variant covers at both tunes; with the bands, it under-covers in some cells at one", "cov-bands-under-one"),
            ("SC4. The primary variant covers at both tunes; with the bands, it under-covers at both", "cov-bands-under-both"),
            ("SC5. The primary variant covers at both tunes; with the bands, the test is invalid at one", "cov-bands-invalid-one"),
            ("SC6. The primary variant covers at both tunes; with the bands, the test is invalid at both", "cov-bands-invalid-both"),
            ("SC7. One tune under-covers in some cells; the other covers (both variants alike)", "cov-one-under-cells"),
            ("SC8. As SC7, where a flag may be an artefact of clipping", "cov-one-under-clip"),
            ("SC9. One tune under-covers jointly, with no single cell flagged; the other covers", "cov-one-under-joint-only"),
            ("SC10. Both tunes under-cover, jointly and in some cells (both variants alike)", "cov-both-under-joint"),
            ("SC11. The test is invalid at one tune; the other covers", "cov-invalid-one-covers"),
            ("SC12. The test is invalid at one tune; the other under-covers in some cells", "cov-invalid-one-under"),
            ("SC13. The test is invalid at both tunes", "cov-invalid-both"),
            ("SC14. Both tunes covered, after a check of the clipping offset exceeded its bound and the test went on",
             "cov-offset-proceeded"),
            ("SC15. Both tunes covered, after the test had stopped and was repaired", "cov-repaired")):
        out.append(f"{lab}\n\n    {P(case, 'sec-coverage')}\n")
    out.append("In SC14 and SC15 the abstract prints AB1; in SC7 to SC9, AB6; in SC10, AB7.\n\n"
               "The test stopped (the abstract prints AB11, or AB12 for SC17):\n")
    for lab, case in (("SC16. Stopped at a gate", "cov-gate-failed"),
                      ("SC17. Stopped after a check of the clipping offset exceeded its bound", "cov-offset-stopped"),
                      ("SC18. Stopped at another check", "cov-stop")):
        out.append(f"{lab}\n\n    {P(case, 'sec-coverage')}\n")

    out.append(part("PART 3. TABLE 1: THE ROW FOR THE FIVE-OBSERVABLE COVERAGE TEST",
                    'The row\'s "Result" and "Status" cells, for a selection of the cases above; the other cases follow the same pattern.\n'
                    'The table caption defines the status words.\n'))
    for lab, case in (("AB1 / SC1", "cov-both-cover"), ("AB2 / SC3", "cov-bands-under-one"), ("AB6 / SC7", "cov-one-under-cells"),
                      ("SC9", "cov-one-under-joint-only"), ("AB7 / SC10", "cov-both-under-joint"),
                      ("AB8 / SC11", "cov-invalid-one-covers"), ("AB10 / SC13", "cov-invalid-both"),
                      ("AB11 / SC16", "cov-gate-failed"), ("AB12 / SC17", "cov-offset-stopped"), ("AB11 / SC18", "cov-stop")):
        out.append(f"{lab}\n\n    {P(case, 'table-coverage')}\n")

    out.append(part("PART 4. THE STUDY OF WHAT CHANGES THE RETAINED PRIOR: THE BINNED ITERATIVE UNFOLDING (IBU) AGAINST THE ESTIMATOR",
                    "Each case is shown at both flagged truths, the GiBUU hybrid truth and the q3 tilt. The two truths are read\n"
                    "separately, so they can differ. The clause on longer iteration (\"and its retention ...\") is a separate reading\n"
                    "with four forms; each case below shows one of them, and any form can go with any case.\n"))
    for lab, case in (("C1. The IBU retains less of the prior than the estimator", "ibu-less"),
                      ("C2. The IBU's retention differs from the estimator's by less than the bar fixed in advance", "ibu-same"),
                      ("C3. The IBU retains more of the prior than the estimator", "ibu-more"),
                      ("C4. The retained share is undefined at a truth, so the comparison is not made", "ibu-undefined")):
        out.append(f"{lab}\n\n  Abstract:\n\n    {P(case, 'abstract-ibu')}\n\n  Section 5.3, end of the section:\n\n"
                   f"    {P(case, 'sec-ibu')}\n")
    out.append("In C1, the last two sentences print because, by the study's rule fixed in advance, a lower retention for the IBU\n"
               "means its readings are consistent with a share specific to the implementation. In C2 to C4, those sentences print\n"
               "only if another reading of the study gives the same label.\n")

    out.append(part("PART 5. OTHER SENTENCES",
                    "No sentence of the Discussion and conclusions (section 7), and no other sentence of the manuscript's prose,\n"
                    "changes with the outcomes shown here. Two other pending results have their own pre-written text, which is not part\n"
                    "of this read: the other readings of the prior-retention study (section 5.3 and its Table 1 row), and a per-cell\n"
                    "validity rule (section 5.4 and its Table 1 row)."))
    text = "\n".join(out)
    banned = [r"\bLL5D\b", r"\bFD-PRR\b", r"\bPRR\b", r"\bV-HALF\b", r"\bVHALF\b", r"\bCOV2D\b", r"\bENS1\b",
              r"minus2", r"\\fv", r"\b(prr|ll5d|vhalf)-", r"[Jj]oseph", r"director", r"\bPR-[123]", r"\?\?"]
    bad = [b for b in banned if re.search(b, text)]

    def load(path, name):
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    mv = load(wt / "docs/analysis-note/make_values_fived16.py", "mv")
    cr = load(Path(__file__).resolve().parent.parent / "check_round.py", "check_round")
    bad += cr.printed_class_names(text, mv)
    if bad:
        sys.exit(f"write_variants: banned terms or class names print: {bad}")
    Path(argv[3]).write_text(text)
    print(f"wrote {argv[3]}: {len(text.split())} words")


if __name__ == "__main__":
    main(sys.argv)
