#!/usr/bin/env python3
"""Every scripted edit of note round n4, by batch. Each (id, file, old, new) must match its file exactly once.

usage: apply_n4.py <worktree> <batch> [--check]
  batch C: the six interval-sense "calibration" sites and the main-result sentence (outline sec. 2, director's
           rulings of 2026-10-28: 2a, 2b);
  --check: apply nothing; exit 0 only if every edit of the batch is already applied (new text present once, old
           text absent).

check_ledger.py imports REL (the app_release.tex pairs) to pin its allowance; that list is empty until the director
rules on the release claim table (outline sec. 3)."""
import sys
from pathlib import Path

C = [
    # 2b. N1 (sec_5d.tex sec:val-fiveaxis) gives "calibration" to tests and "coverage" to intervals.
    # The record calls this the candidate's "calibration" test (OUTCOME-20260926-s5e-oi192-diagnosis-and-candidate.md
    # row A2: pooled pull SD 1.023, pooled coverage 0.680 / 0.942, "a pooled pass, not per-functional calibration").
    # agy read three forms (agy/c, c2, c3; REPORT.md). C1 drops the adjective, since the test measured pulls, coverage
    # and a Mahalanobis distance (agy c Q1, c2 Q1); C3 drops it too (c2 Q3 SAME). C2 and C4 name coverage and width,
    # because "coverage" alone narrows the interval sense of "calibration" (agy c3 Q2, Q4, both runs).
    ("C1", "sec_5d.tex", "and a pooled calibration test of its statistical intervals (pull width 1.02).",
     "and a pooled test of its statistical intervals (pull width 1.02)."),
    ("C2", "sec_5d.tex", "The pooled test does not establish calibration for every functional.",
     "The pooled test does not establish coverage and width for every functional."),
    ("C3", "sec_5d.tex", "so a pooled calibration pass cannot qualify this cell.",
     "so a pooled pass cannot qualify this cell."),
    ("C4", "sec_validation.tex", "checks neither interval calibration nor the adequacy of the physical model.",
     "checks neither the coverage and width of the intervals nor the adequacy of the physical model."),
    # The PET rule that H2S1T24 fails is its frozen coverage rule, C1 and C4 FAIL; C5 and C6 use the rule's name (agy c3 Q5, c4 Q6)
    # (nd-unfolding/pet/final_design/DECISION_RECORD-pet-final-design.md:47, :49).
    ("C5", "sec_pet_campaigns.tex", "H2S1T24 fails interval calibration and L128S1T24 fails B2",
     "H2S1T24 fails the frozen coverage rule and L128S1T24 fails B2"),
    ("C6", "sec_pet_campaigns.tex", "and the measured PET procedure failed calibration.",
     "and the measured PET procedure failed the frozen coverage rule."),
    # The cited paper's own title: "Confidence intervals for functionals in constrained inverse problems"
    # (technote.bib Stanley:2025functionals).
    ("C7", "app_statmethods_nd.tex", "Recent work constructs calibrated intervals for selected functionals",
     "Recent work constructs confidence intervals for selected functionals"),
    # 2a. The note abstract (main_note.tex:72) opens with the measurement; the paper's printed Conclusions
    # (paper_body.tex:355) say "The principal result is the sixteen-cell cross section of Sec.~\ref{sec:result16},
    # with its covariance and generator comparison." That sentence, retargeted, replaces the note's two
    # "The main results are the validation findings" sentences. "They hold" in the ES would then refer to that
    # result alone, so it names the results.
    ("M1", "sec_execsummary.tex",
     "The main results are the validation findings. They hold for this implementation,",
     "The principal result is the sixteen-cell cross section of \\S\\ref{sec:fived16}, with its covariance and "
     "generator comparison. The results hold for this implementation,"),
    ("M2", "sec_summary.tex",
     "The main results are the validation findings, within the scope stated in \\S\\ref{sec:intro}.",
     "The principal result is the sixteen-cell cross section of \\S\\ref{sec:fived16}, with its covariance and "
     "generator comparison. The results hold within the scope stated in \\S\\ref{sec:intro}."),
]
# Batch R: app_release.tex, released by DECISION-20261028-joseph-protections-n4-release-retrospective.md item 3, under
# the director's rulings on note-n4/release-claims.md (2026-10-28): A, R2-R4 apply, R1 does not (FALSE as read: the
# closure and bias numbers are of configurations (c)-(e)); B, the four FALSE claims' truth fixes; C, "NERSC project
# storage"; D, \depositsnapshot stays. R2-R4 are d2's declared pairs, imported, not retyped.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "fived16" / "d2"))
import options as _d2  # noqa: E402
assert _d2.R14["site"] == "app_release.tex" and len(_d2.R14["pairs"]) == 4
REL = [("R2", "app_release.tex", *_d2.R14["pairs"][1]),
       ("R3", "app_release.tex", *_d2.R14["pairs"][2]),
       ("R4", "app_release.tex", *_d2.R14["pairs"][3]),
       # RL-21: the article cites no note figure; RC7 was built for an earlier version of the article; neither document
       # now prints the projections (release-claims.md).
       ("RL21", "app_release.tex",
        "It also regenerates, from packaged arrays, figures that the article cites from this note: the $(\\Eavail,W)$ excess map "
        "(Fig.~\\ref{fig:eavailWexcess}), the null distributions of the joint tests (Fig.~\\ref{fig:joint5d-nulls}), and the "
        "one-dimensional generator projections.",
        "It also regenerates, from packaged arrays, figures drawn for the earlier version of the article for which it was "
        "assembled: the $(\\Eavail,W)$ excess map, which this note prints as Fig.~\\ref{fig:eavailWexcess}, the null "
        "distributions of the joint tests, which it prints as Fig.~\\ref{fig:joint5d-nulls}, and one-dimensional generator "
        "projections, which neither this note nor the article now prints."),
       ("RL27", "app_release.tex", "the arrays behind the article's figures;", "the arrays behind the figures drawn for that earlier version;"),
       ("RL39", "app_release.tex", "for the article's Figs.~1--3 themselves, the check is that the three figure files are produced.",
        "for Figs.~1--3 of that earlier version themselves, the check is that the three figure files are produced."),
       # RL-59: re-measured at the n4 head from ANATUPLE-SHA256.tsv (sha256 913e004d..., the record's): 2,374 rows, of
       # which 1,818 data and 489 simulation AnaTuples (2,307) and 67 others (58 MATFluxAndReweightFiles, 9 MParamFiles).
       ("RL59", "app_release.tex", "identifies all 2,374 inventoried AnaTuple input files by SHA256 checksum",
        "identifies all 2,374 inventoried input files (2,307 AnaTuples and 67 flux, reweight and parameter files) by SHA256 checksum"),
       # Line 45: the copies are in /global/cfs/cdirs/m3246/josephrb (RECORD-20261010-ost61-hashed-and-data-addition.md sec. 3).
       ("RL45", "app_release.tex", "on collaboration storage;", "on NERSC project storage;")]
BATCHES = {"C": C, "R": REL}


def main():
    wt, batch = Path(sys.argv[1]).resolve(), sys.argv[2]
    check = "--check" in sys.argv
    D = wt / "docs/analysis-note"
    texts, bad = {}, []
    for eid, f, old, new in BATCHES[batch]:
        t = texts.setdefault(f, (D / f).read_text())
        if check:
            if t.count(new) != 1 or old in t:
                bad.append(f"{eid}: not applied ({f}: new x{t.count(new)}, old x{t.count(old)})")
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
    print(f"batch {batch}: {len(BATCHES[batch])} edits {'verified' if check else 'applied'} in {len(texts)} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
