r"""Round 3 of the PRD read, applied (handoff section 4 items 1 and 2; director, 2026-10-27): sol2's true forms of the
split items P02, P11, P14, P15, P19 and P25 (P02 keeps NEW's "the simulation mismodels the truth", after agy's check; P14 and P15 keep the phrases check_sec4_receipts.py binds: "by up to
... at high $W$" and "it is \SIrange ... in the most affected"), and the abstracts' limitation sentence split into its three sentences.
The truth column is in prd-read/REPORT.md ("Round 3"). Each edit is an exact old -> new pair, whitespace-tolerant, and
must match exactly once."""
import re, sys
D = sys.argv[1]
def pat(s): return re.compile(r"\s+".join(re.escape(w) for w in s.split()))
E = {
"paper_body.tex": [
("P02", r"The validation studies show how far the result can be trusted: the two-dimensional reproduction, the background subtraction, the recovery of generator-sized truth changes, a coverage test and a fake-data study of the estimator's bias. They ask whether the unfolding gives reliable multidimensional cross sections when the simulation mismodels the truth by generator-sized amounts.",
        r"The validation studies assess the result through the two-dimensional reproduction, background-subtraction tests, recovery of generator-sized truth changes, a coverage test and a fake-data study of estimator bias. They examine whether the unfolding gives reliable multidimensional cross sections when the simulation mismodels the truth by generator-sized amounts."),
("P11", r"The distance depends on the estimator (\nsec{sec:results-tension}), and the learner was chosen after the comparisons of LightGBM and of an exact-split learner with the publication were known, so the benchmark is a reproduction rather than an independent validation. The exact-split learner, with purity-based subtraction, differs from the central value by a per-bin median of \SI{1.03}{\percent} (maximum \SI{17.6}{\percent}). These comparisons are described in \nsec{sec:method-config}.",
        r"The distance depends on the estimator (\nsec{sec:results-tension}). The learner was selected after the LightGBM and exact-split comparisons with the published result, so this benchmark is a reproduction rather than an independent validation. The purity-subtracted exact-split result differs from the central value by a median of \SI{1.03}{\percent} per bin (maximum \SI{17.6}{\percent}); see \nsec{sec:method-config}."),
("P14", r"the $(\Eavail,W)$ cells unfolded with a development variant of the joint-test estimator, whose refinement has 100 trees and 8 leaves, deviate from it by several percent in the largest cells and by up to \SI{74}{\percent} at high $W$, in the cell $0.8\le\Eavail<\SI{1.5}{GeV}$, $W\ge\SI{3}{GeV}$.",
        r"the $(\Eavail,W)$ cells unfolded with a development variant of the joint-test estimator using a 100-tree, 8-leaf refinement deviate from it by several percent in the largest cells and by up to \SI{74}{\percent} at high $W$, in the cell $0.8\le\Eavail<\SI{1.5}{GeV}$, $W\ge\SI{3}{GeV}$."),
("P15", r"We interpret it as regularization bias, because it persists over the tested ranges of iteration number and classifier capacity: in noise-free studies of that variant, thirty iterations reduce the $\Eavail$ residual by \SI{26}{\percent}, and a larger classifier improves the reconstruction-level fit without reducing it.  For other fixed generator shapes, measured with the joint-test estimator, it is \SIrange{16}{31}{\percent} in the most affected $(\Eavail,W)$ cell and within the quoted total uncertainty in about half of those cells; that uncertainty is the covariance of an earlier purity-subtracted five-observable central value, which does not meet its specification's acceptance criteria (\nsec{sec:eavailw-adopted}).",
        r"We interpret the residual as regularization bias because it persists over the tested iteration numbers and classifier capacities: in noise-free studies of that variant, thirty iterations reduce the $\Eavail$ residual by \SI{26}{\percent}, while a larger classifier improves the reconstruction-level fit without reducing it.  For other fixed generator shapes tested with the joint-test estimator, it is \SIrange{16}{31}{\percent} in the most affected $(\Eavail,W)$ cell and lies within the quoted total uncertainty in about half of those cells. Those uncertainties come from an earlier purity-subtracted five-observable covariance that fails its specified acceptance criteria (\nsec{sec:eavailw-adopted})."),
("P19", r"\caption{Empirical coverage of the 153 reported cell and projection integrals for statistical intervals corrected for the nominal-truth bias, from a deterministic LightGBM estimator with purity-based subtraction, with 400 pseudo-experiments, at the truth with the signal rate lowered by about \SI{10}{\percent} and a weak $\Eavail$ slope (Sec.~\ref{sec:coverage}).",
        r"\caption{Empirical coverage of statistical intervals for the 153 reported cell and projection integrals, corrected for nominal-truth bias. The study uses a deterministic LightGBM estimator with purity-based subtraction and 400 pseudo-experiments at a truth with an approximately \SI{10}{\percent} lower signal rate and a weak $\Eavail$ slope (Sec.~\ref{sec:coverage})."),
("P25", r"The paper's result is the sixteen-cell cross section of Sec.~\ref{sec:result16}, with its covariance and its generator comparison; the validation findings summarized in Table~\ref{tab:findings} show how far it can be trusted.",
        r"The principal result is the sixteen-cell cross section of Sec.~\ref{sec:result16}, with its covariance and generator comparison; Table~\ref{tab:findings} summarizes the validation findings."),
],
"main_paper.tex": [
("LIM-A", r"The coverage of the intervals has not been validated; in a fake-data study, the reported uncertainty does not cover the estimator's bias at GiBUU-like truths or at a synthetic $q_{3}$ tilt; and the sixteen-cell $\chi^{2}$ values fall",
          r"The coverage of the intervals has not been validated. In a fake-data study, the reported uncertainty does not cover the estimator's bias at GiBUU-like truths or at a synthetic $q_{3}$ tilt. The sixteen-cell $\chi^{2}$ values fall"),
],
"main_note.tex": [
("LIM-B", r"The coverage of the result's intervals has not been validated; in a fake-data study, the reported uncertainty does not cover the estimator's bias at GiBUU-like truths or at a synthetic $q_{3}$ tilt; and the sixteen-cell $\chi^{2}$ values fall",
          r"The coverage of the result's intervals has not been validated. In a fake-data study, the reported uncertainty does not cover the estimator's bias at GiBUU-like truths or at a synthetic $q_{3}$ tilt. The sixteen-cell $\chi^{2}$ values fall"),
],
}
HDR = "% PRD read round 3 (director, 2026-10-27; prd-read/REPORT.md \"Round 3\"): the limitation sentence split into its three sentences, one per limitation, so that the 1A and 3D readouts can each replace one; the wording is otherwise unchanged. Both sol2 forms of this abstract were not applied (the truth column gives why)."
for f, edits in E.items():
    p = f"{D}/{f}"; t = open(p).read()
    for k, old, new in edits:
        m = list(pat(old).finditer(t))
        if len(m) != 1: sys.exit(f"{f} {k}: {len(m)} matches")
        t = t[:m[0].start()] + new + t[m[0].end():]
    if f != "paper_body.tex":
        if t.count("\\begin{abstract}\n% ") != 1: sys.exit(f"{f}: abstract marker")
        t = t.replace("\\begin{abstract}\n% ", "\\begin{abstract}\n" + HDR + " ", 1)  # joins the block's first comment line (reflow)
    open(p, "w").write(t)
print("round 3 applied")
