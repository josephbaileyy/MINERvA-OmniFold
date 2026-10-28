r"""usage: python3 -I apply_b2_fixes.py ANALYSIS_NOTE_DIR -- r19 b2: fixes for the b2 review (scratchpad REVIEW-b2.md,
ADOPT-AFTER-FIXES).
- B1: O1 had deleted the out-of-scope sentence, which DECISION-20261023-joseph-5d-a-and-register-round.md item 3(b)
  keeps because d-id/REPORT.md sec. 11 requires its limits to accompany the outcome. The old scope paragraph is
  restored verbatim. O1 keeps only a compressed first sentence; the counts and Table III stay in the note.
- S1: the restored "Within that scope, the residual is consistent with ..." is singular again, as the base had it.
  The compressed sentence had extended the claim to every stable residual.
- S2: the first sentence regains "the truth changes used to develop the estimator".
- S3: "thus" goes from the normalization sentence, whose premise, "The rate change itself is recovered", moved to
  the note under O2.
- S4: the CLAIM-ADDITION comment describes the block as it now is.
- NITs: the count sentence follows the warning directly, so "Under that change" refers back one sentence. O3's
  parenthetical pointer goes, because the paragraph's closing pointer names the iteration and capacity tests.
Every edit is an exact old -> new pair, whitespace-tolerant, that must match exactly once."""
import re, sys
D = sys.argv[1]
def pat(s): return re.compile(r"\s+".join(re.escape(w) for w in s.split()))
p = f"{D}/paper_body.tex"; t = open(p, encoding="utf-8").read()
E = [
 ("B1/S1/S2",
  r"In a binned, signal-only and noise-free diagnostic on the \jtNcells{} joint cells, with the detector response fixed at the simulation's, an exact binned iterative unfolding with five iterations leaves about the same median residual as the boosted-tree estimator, and the residuals whose diagnosis is stable under the truth resolution (\SI{38}{\percent} of the joint-cell residuals above \SI{2}{\percent}) are consistent with the regularization of the inverse problem at this binning and prior, rather than with the tree approximation of the classifiers (\nsec{sec:val-departure}).",
  r"In a binned, signal-only and noise-free diagnostic on the \jtNcells{} joint cells and the truth changes used to develop the estimator, with the detector response fixed at the simulation's, an exact binned iterative unfolding with five iterations leaves about the same median residual as the boosted-tree estimator.  It covers only the residuals whose diagnosis is stable under the truth resolution (\SI{38}{\percent} of the joint-cell residuals above \SI{2}{\percent}).  What unbinned information could recover, the coverage failure, and the validity of any interval lie outside its scope.  Within that scope, the residual is consistent with the regularization of the inverse problem at this binning and prior, rather than with the tree approximation of the classifiers (\nsec{sec:val-departure})."),
 ("S4",
  r"Every number in the paragraph and in Table III prints in the note, sec_5d.tex sec:val-departure, paragraph",
  r"Register round r19 (variant B, O1; DECISION-20261028-joseph-r19-variant-b-and-moves.md): the paragraph's counts and Table III moved to the note; the paragraph keeps a compressed first sentence and, verbatim, the scope sentences that item 3b keeps. Every number of the former paragraph and of the former Table III prints in the note, sec_5d.tex sec:val-departure, paragraph"),
 ("S3", r"Agreement in the marginal normalizations thus coexists with substantial residual bias under the tested deformations.",
  r"Agreement in the marginal normalizations coexists with substantial residual bias under the tested deformations."),
 ("NIT order",
  r"most strongly when the true signal rate is lowered by about \SI{10}{\percent}.  The end-to-end test unfolds 400 pseudo-experiments per truth.  Under that change, 51 of the 153 reported cell and projection integrals have a 68\% coverage whose upper confidence bound lies below the acceptance threshold of 0.66, with coverage as low as 0.06.",
  r"most strongly when the true signal rate is lowered by about \SI{10}{\percent}.  Under that change, 51 of the 153 reported cell and projection integrals have a 68\% coverage whose upper confidence bound lies below the acceptance threshold of 0.66, with coverage as low as 0.06.  The end-to-end test unfolds 400 pseudo-experiments per truth."),
 ("NIT O3 pointer", r"persists over the tested iteration numbers and classifier capacities (\nsec{sec:val-departure}).",
  r"persists over the tested iteration numbers and classifier capacities."),
]
for k, old, new in E:
    m = list(pat(old).finditer(t))
    if len(m) != 1: sys.exit(f"{k}: {len(m)} matches")
    t = t[:m[0].start()] + new + t[m[0].end():]
open(p, "w", encoding="utf-8").write(t); print("b2 fixes applied: %d edits" % len(E))
