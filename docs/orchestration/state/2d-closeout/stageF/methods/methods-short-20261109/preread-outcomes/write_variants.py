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

Square brackets mark placeholders. Any text in square brackets, such as "[cells R03, R11, with their coverage
fractions]" or "[the failed control]", is a made-up stand-in for a value that does not exist yet. It is not a result.

The manuscript and its Supplement accompany this file. No sentence that is not shown here changes with these
outcomes (Part 3 lists the other pending text).
"""

RULE = "=" * 118
COV = [
    ("No under-coverage detected, in both variants at both tunes", "cov-all-cover"),
    ("As CV1, with some passes weakened by clipping, in both variants, and some over-coverage", "cov-all-cover-qualified"),
    ("Primary variant: no under-coverage at either tune. With the bands: under-coverage in some cells at one tune", "cov-bands-under-one"),
    ("Primary: none at either tune. With the bands: under-coverage at both tunes, in cells at one and jointly and in cells at the other",
     "cov-bands-under-both"),
    ("Primary: none at either tune. With the bands: invalid at one tune, by a numerical check of the grade", "cov-bands-invalid-one"),
    ("Primary: none at either tune. With the bands: invalid at both tunes", "cov-bands-invalid-both"),
    ("Primary: under-coverage in some cells at one tune. With the bands: none at either tune", "cov-primary-under-bands-cover"),
    ("Primary: invalid at both tunes. With the bands: none at either tune", "cov-primary-invalid-bands-cover"),
    ("Both variants: under-coverage in some cells, not jointly, at one tune; none at the other", "cov-one-under-cells"),
    ("As CV9, where the flags meet the condition for a possible clipping artefact", "cov-one-under-clip"),
    ("Both variants: joint under-coverage, with no cell flagged, at one tune; none at the other", "cov-one-under-joint-only"),
    ("Cell and joint outcomes that differ by tune and by variant", "cov-mixed-cell-joint"),
    ("Both variants: under-coverage jointly and in some cells at both tunes", "cov-both-under-joint"),
    ("Both variants: invalid at one tune; no under-coverage at the other", "cov-invalid-one-covers"),
    ("Both variants: invalid at one tune; under-coverage in some cells at the other", "cov-invalid-one-under"),
    ("Invalid at both tunes, in both variants", "cov-invalid-all"),
    ("The test went on after its clipping-offset check exceeded its bound; then no under-coverage anywhere", "cov-proceeded-cover"),
    ("The test went on after its clipping-offset check exceeded its bound; then under-coverage in some cells at one tune",
     "cov-proceeded-under"),
    ("An earlier run stopped, and the test ran with a repair; then no under-coverage anywhere", "cov-repaired-cover"),
    ("An earlier run stopped, and the test ran with a repair; then under-coverage jointly and in cells at both tunes",
     "cov-repaired-under"),
    ("Stopped at a gate before any pseudo-experiment ran", "cov-gate-failed"),
    ("Stopped by a decision made after the clipping-offset check exceeded its bound", "cov-offset-stopped"),
    ("Stopped at another check before any pseudo-experiment ran", "cov-stop"),
]
IBU = [
    ("At both flagged truths, the IBU retains less of the prior than the estimator", "ibu-less"),
    ("At both, the IBU's retention differs from the estimator's by less than the bar", "ibu-same"),
    ("At both, the IBU retains more of the prior than the estimator", "ibu-more"),
    ("At both, the retained fraction is undefined, so no comparison is made", "ibu-undefined"),
    ("Split: less at the GiBUU hybrid truth; a difference below the bar at the q3 tilt", "ibu-split-less-same"),
    ("Split: a difference below the bar at the GiBUU hybrid truth; more at the q3 tilt", "ibu-split-same-more"),
]


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
    out.append(part("PART 1. THE FIVE-OBSERVABLE COVERAGE TEST: EACH CASE IN THE ABSTRACT, SECTION 6.3 AND TABLE 1",
                    'The test has two variants: a primary one, without two bands of the detector simulation\'s uncertainties (the\n'
                    '"GEANT4 neutron and proton bands"), and one with them. G18_10a_02_11b and AR23_20i_00_000 are the two\n'
                    "held-out tunes. In the abstract, each case's sentence follows this one, which prints in every outcome: \"The\n"
                    "procedure's two-dimensional covariance, rebuilt at each of two held-out generator tunes, under-covers at both;\n"
                    "coverage of the reported five-observable intervals is not established.\" In section 6.3, each case's text follows\n"
                    'the section\'s fixed paragraph, which ends "...shares its 2p2h model family with one of the generators of Cmodel."\n'
                    "Table 1's caption defines the status words.\n"))
    for n, (lab, case) in enumerate(COV, 1):
        out.append(f"CV{n}. {lab}\n\n  Abstract:\n\n    {P(case, 'abstract-coverage')}\n\n  Section 6.3:\n\n    {P(case, 'sec-coverage')}\n\n"
                   f"  Table 1 row:\n\n    {P(case, 'table-coverage')}\n")
    out.append(part("PART 2. THE STUDY OF WHAT CHANGES THE RETAINED PRIOR: THE BINNED ITERATIVE UNFOLDING (IBU) AGAINST THE ESTIMATOR",
                    "The two flagged truths, the GiBUU hybrid truth and the q3 tilt, are read separately, so they can differ; the split\n"
                    "cases show that. The clause on longer iteration (\"and its retention ...\") is a separate reading with four forms; each\n"
                    "case shows one of them, and any form can go with any case. Where the IBU retains less at a truth, that truth's\n"
                    "sentence \"the readings are consistent with a share specific to the implementation\" prints, by the study's rule fixed in\n"
                    "advance. Several such labels can hold at once, and each prints its own sentence; none takes precedence over\n"
                    "another. Labels that depend on other readings of the study are not shown.\n"))
    for n, (lab, case) in enumerate(IBU, 1):
        out.append(f"IB{n}. {lab}\n\n  Abstract:\n\n    {P(case, 'abstract-ibu')}\n\n  Section 5.3, end of the section:\n\n"
                   f"    {P(case, 'sec-ibu')}\n")
    out.append(part("PART 3. OTHER SENTENCES",
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
    src = "".join((wt / "docs/analysis-note" / f).read_text() for f in ("paper_body.tex", "main_paper.tex", "values_fived16.tex"))
    stand_in = " ".join(re.findall(r"\[[^]]*\]", " ".join(v for c in res.values() for v in c["passages"].values())))
    for case in res.values():                       # every word of every passage is in the source, or in a stand-in
        for p in case["passages"].values():
            for w in re.findall(r"[A-Za-z][A-Za-z-]+", p):
                if w not in src and w not in stand_in:
                    bad.append(f"a word not in the source: {w}")
    if bad:
        sys.exit(f"write_variants: banned terms or class names print: {bad}")
    Path(argv[3]).write_text(text)
    print(f"wrote {argv[3]}: {len(text.split())} words")


if __name__ == "__main__":
    main(sys.argv)
