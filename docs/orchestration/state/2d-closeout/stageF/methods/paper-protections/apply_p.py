#!/usr/bin/env python3
"""Every scripted edit of the four paper protection edits (DECISION-20261028-joseph-protections-remade-and-r21.md
items 1-4), by item. Each (id, file, old, new) must match its file exactly once.

usage: apply_p.py <worktree> <item> [--check]
  item 1: the four low-stability cells in the Limitations subsection (DECISION-20261024-joseph-h2-16-cell-definition.md
          item 3); the numbers are make_values_fived16.py's h2-lowstab-* keys, generated from the pinned H2 definition.
  item 2: Data Availability (ruling (b)); item 34: the duplicate limitations and the Scope wording.
  --check: apply nothing; exit 0 only if every edit of the item is already applied."""
import sys
from pathlib import Path

ITEM1 = [
    ("L1", "paper_body.tex",
     "The sixteen-cell result also has total uncertainties, whose coverage is not validated; Sec.~\\ref{sec:fd16} reports the fake-data tests of the estimator's bias.",
     "The sixteen-cell result also has total uncertainties, whose coverage is not validated; Sec.~\\ref{sec:fd16} reports the fake-data tests of the estimator's bias.  "
     "Four of the sixteen cells, \\fvval{h2-lowstab-cells}, have a stability of \\fvval{h2-lowstab-min}--\\fvval{h2-lowstab-max}: of the "
     "simulated signal events generated in such a cell and reconstructed, only that fraction is reconstructed in the same cell."),
]
# Item 2 (the director's ruling (b), 2026-10-28): the CC0 and input-file sentences stay; the package sentences become
# one, narrowed to what the package regenerates (release-claims.md: RL-19, RL-21; the note's Figs. eavailWexcess and
# joint5d-nulls); the false "numbers quoted in Sec. central" clause and the stale "except the multiplier scan" (the
# paper quotes no multiplier scan) go; the reproducibility sentence stays (agy run1 Q5), as "The paper's quoted numbers", since the package regenerates figures and none of the paper's numbers (agy run2 Q5);
# \pubhold is untouched. The package's other facts print in app_release.tex (ledger rows D*). Pinned in check_ledger.
ITEM2 = [
    ("DA1", "main_paper.tex",
     "A candidate release package of about \\SI{16}{MB}, not yet deposited, requires only numpy, scipy, and matplotlib.  It "
     "recomputes every $p$ value, decision, robustness result, and power figure of the joint tests and the numbers quoted in "
     "Sec.~\\ref{sec:central}, and it regenerates the analysis note's figures of the joint-test null distributions and the "
     "$(\\Eavail,W)$ map.  The other quoted numbers, except the multiplier scan, and the event-level processing require the "
     "archived analysis products, the open-data AnaTuples, and the generator samples produced for this analysis; "
     "\\napp{app:release} states what each part of the release does and does not reproduce.",
     "A candidate release package of about \\SI{16}{MB}, not yet deposited, requires only numpy, scipy, and matplotlib, and "
     "regenerates the analysis note's figures of the joint-test null distributions and the $(\\Eavail,W)$ map.  The paper's "
     "quoted numbers and the event-level processing require the archived analysis products, the open-data AnaTuples, and "
     "the generator samples produced for this analysis; \\napp{app:release} states what each part of the release does "
     "and does not reproduce."),
]
# Items 3 and 4 (the director's rulings, 2026-10-28): the body home keeps the evidence; Sec. VI (Limitations) is the one
# numbered home; Sec. I keeps "Interval coverage has not been validated."; the abstract is untouched.
ITEM34 = [
    # Sec. I: the fake-data, E1 (F1) and flux copies go; their homes are sec:fd16 and sec:gen16.
    ("S1", "paper_body.tex",
     "The result has three limitations, each stated with it. Interval coverage has not been validated. At two held-out "
     "GENIE~v3 truths, a bias test finds the estimator's bias below the reported uncertainty in every cell, but does not "
     "test interval widths. In a fake-data study at \\fvval{f0b-all-truths} truths, the reported uncertainty does not cover "
     "the estimator's bias at the GiBUU-like truths or at a synthetic $q_{3}$ tilt (Sec.~\\ref{sec:fd16}). The generator "
     "$\\chi^{2}$ depends on the flux correlations: weakening only them by \\fvval{sens-alpha-pct}\\,\\% lowers the "
     "$\\chi^{2}$ of the sixteen-cell predictions by \\fvval{sens-flux-fall-lo}--\\fvval{sens-flux-fall-hi}\\,\\% "
     "(Sec.~\\ref{sec:gen16}).",
     "Interval coverage has not been validated. The bias tests, the fake-data study and the dependence of the generator "
     "$\\chi^{2}$ on the flux correlations are given with the result (Secs.~\\ref{sec:fd16} and~\\ref{sec:gen16})."),
    # Scope: its positive scope and one pointer; the coverage and joint-test copies are Sec. VI's.
    ("S2", "paper_body.tex",
     " The three- and four-observable results are central values without intervals of validated coverage: the output of "
     "the joint-test estimator of Sec.~\\ref{sec:method}, with the observable definitions, simulated detector response, "
     "background treatment, and regularization given there. The sixteen-cell result of Sec.~\\ref{sec:result16} also has "
     "total uncertainties, whose coverage is not validated. The companion note also gives simulation-calibrated tests of "
     "the generator predictions; they test hybrid null hypotheses, are calibrated within the implemented simulation "
     "model, and are not physical exclusions of the generators. They show no evidence of additional discrimination beyond "
     "matched coarse projections.",
     " The limitations are listed in Sec.~\\ref{sec:limitations}."),
    # Two joint-test caveats printed only in Scope; they move to Sec. VI so that no fact leaves the paper.
    ("S3", "paper_body.tex",
     "Their calibration is valid to the extent that the simulated chain reproduces the analysis of the data "
     "(\\nsec{sec:joint5d-conditions}).",
     "Their calibration is valid to the extent that the simulated chain reproduces the analysis of the data "
     "(\\nsec{sec:joint5d-conditions}).  They are not physical exclusions of the generators, and they show no evidence of "
     "additional discrimination beyond matched coarse projections."),
    # sec:gen16: the fake-data copy goes (home sec:fd16).
    ("S4", "paper_body.tex",
     " The reported uncertainty does not cover the fake-data bias at the GiBUU-like truths (Sec.~\\ref{sec:fd16}).", ""),
    # sec:departure: the C_model label clause goes (home sec:cov16); its pointer stays.
    ("S5", "paper_body.tex",
     "For the sixteen-cell result, the model term of its reported covariance is the change in the unfolded data when the "
     "prior is reweighted to each generator (GENIE + MEC, NuWro, GiBUU), unscaled and not a calibrated bound; "
     "Sec.~\\ref{sec:fd16} reports the fake-data tests of the estimator's bias.",
     "For the sixteen-cell result, Sec.~\\ref{sec:fd16} reports the fake-data tests of the estimator's bias."),
]
ITEMS = {"1": ITEM1, "2": ITEM2, "34": ITEM34}


def main():
    wt, item = Path(sys.argv[1]).resolve(), sys.argv[2]
    check = "--check" in sys.argv
    D = wt / "docs/analysis-note"
    texts, bad = {}, []
    for eid, f, old, new in ITEMS[item]:
        t = texts.setdefault(f, (D / f).read_text())
        if check:
            if (new and t.count(new) != 1) or (old in t and old not in new):   # a deletion: old must be gone
                bad.append(f"{eid}: not applied ({f}: new x{t.count(new) if new else '-'}, old x{t.count(old)})")
            continue
        if t.count(old) != 1:
            bad.append(f"{eid}: old text matches {f} {t.count(old)} times")
            continue
        texts[f] = t.replace(old, new)
    if bad:
        print("\n".join(bad)); return 1
    if not check:
        for f, t in texts.items():
            (D / f).write_text(t)
    print(f"item {item}: {len(ITEMS[item])} edits {'verified' if check else 'applied'} in {len(texts)} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
