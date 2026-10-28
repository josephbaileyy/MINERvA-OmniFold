r"""usage: python3 -I apply_n.py ANALYSIS_NOTE_DIR -- r19 variant B: the note additions N1-N4 (r19/move-pass.md; the
director's rulings of 2026-10-28 under DECISION-20261028-joseph-r19-variant-b-and-moves.md item 3).

The additions:
- N1 (sec_joint.tex, after the section's first paragraph): the paper's joint-test lead argument (P1-P3) and Sec. I's
  definitions (P6, P7), in the paper's reviewed wording. The note calls this part a section ("This section describes
  ..."), so the paper's "this section" is kept.
- N2 (sec:joint5d-frozen): P4's sentence, after the familywise-error statement.
- N3 (app_codebase.tex, the note's last appendix, at its end): the paper's Fig. 4 with its caption (P5), a new label
  fig:coverage-5d-paper, and a pointer to it from sec:coverage-5d. The note numbers figures globally, and the last
  float takes the last number, so no existing figure number changes.
- N4 (sec_5d.tex): "noise-free" on the 26% and larger-classifier results. The source is
  DIAGNOSIS-20260926-s5e-oi192-estimator.md:115 ("Noise-free (D4, asimov_same, B0, K = 30)"), :137 (the 26%) and :140
  ("One-factor probes (D5, noise-free)", the capacity probe).

These land before the paper-side deletions of VI, K1 and K13, so no fact is absent from both documents at any commit.
Every edit is an exact old -> new pair that must match exactly once."""
import re, sys

D = sys.argv[1]

N1 = (r"% Register round r19 (variant B, N1; DECISION-20261028-joseph-r19-variant-b-and-moves.md item 3): moved from the methods paper, in its reviewed wording (paper Sec. I's definition of test calibration and the lead paragraph of its former joint-test section), so that these facts print in the note when the paper's joint-test section leaves it (r19/move-pass.md, P1-P3, P6, P7)." "\n"
      r"Two properties must be distinguished.  The coverage of unfolded intervals is the rate at which they contain the true cross section.  The calibration of a test is the rate at which it rejects a true hypothesis.  Calibration can be obtained without validated intervals by simulating the whole analysis chain at the hypothesis, so that the estimator's bias enters the simulated null distribution.  A calibration obtained in this way is valid to the extent that the simulated chain reproduces the analysis of the data.  Unfolded results can be compared with any prediction at truth level without simulating each generator through the detector; for hypothesis tests the advantage is smaller.  A test at reconstruction level would avoid the regularization bias, but it would still need the same response model.  Each external prediction would have to be folded through the analysis simulation's response, which is the hybrid construction of \S\ref{sec:joint5d-design}, with the same composition below the fine grid.  The tests of this section instead calibrate the unfolded statistic in simulation, so that the bias enters the null distribution rather than the decision.  We have not compared their power with that of a reconstruction-level test.")

FIG = r"""% Register round r19 (variant B, N3; director's ruling 2026-10-28): the methods paper's Fig. 4 and its caption, moved here when the paper's coverage figure left it (r19/move-pass.md, P5). Placed at the end of the last appendix so that no existing figure number of the note changes; pointed to from sec:coverage-5d. Third truth: OUTCOME-20260925-s5c-tier-s-futility-fail.md sec. 3; nd-unfolding/s5c_pseudo.py:56-60. Source: methods-m3 REPORT, Figure 3 (interim_400.json; evaluator nd-unfolding/s5c_coverage.py:147-174; bounds re-derived with scipy.stats.beta to 2e-16). Reproduced: 51, 0.060 (J224), 42; 2 (EW36, J161), 0.850 (EW36).
\begin{figure}[tbp]
\centering
\includegraphics[width=\linewidth]{paper_fig_coverage}
\caption{Empirical coverage of statistical intervals for the 153 reported cell and projection integrals, corrected for nominal-truth bias (\S\ref{sec:coverage-5d}). The study uses a deterministic LightGBM estimator with purity-based subtraction and 400 pseudo-experiments at a truth with an approximately \SI{10}{\percent} lower signal rate and a weak $\Eavail$ slope.  At nominal truth (not drawn) none lies below the 0.66 threshold, and two lie below the 0.94 threshold.  Circles: 68\% intervals; squares: 95\% intervals.  Bars are one-sided Clopper--Pearson lower and upper bounds, each at level $0.05/459$, a Bonferroni correction over the 153 integrals and the three truths of the study.  The third truth, a change of the $q_{3}$ dependence at fixed $(\Eavail,W)$, is omitted because its reweighting does not implement the intended change; the test's verdict does not depend on it. Solid lines mark the nominal coverage and dashed lines the acceptance thresholds 0.66 and 0.94; filled markers have an upper bound below the threshold.  The integrals are ordered as the $(\Eavail,W)$ projection (cells 0--41 and their sum), the \jtNcells{} coarse joint cells (labelled by their index in the $3^{5}$ grid), and the total.}
\label{fig:coverage-5d-paper}
\end{figure}
"""

E = {
 "sec_joint.tex": [
  ("N1", "\n\n\\subsection{Hypotheses, grid and statistics}\n\\label{sec:joint5d-design}",
   "\n\n" + N1 + "\n\n\\subsection{Hypotheses, grid and statistics}\n\\label{sec:joint5d-design}"),
  ("N2", "That rate is the probability of falsely rejecting at least one true hypothesis among them.",
   "That rate is the probability of falsely rejecting at least one true hypothesis among them. The error control applies to the decisions, not separately to the point estimates $(k+1)/(B+1)$."),
 ],
 "sec_5d.tex": [
  ("N3 pointer", "No frequentist coverage is therefore claimed for any five-dimensional interval.",
   "No frequentist coverage is therefore claimed for any five-dimensional interval. Figure~\\ref{fig:coverage-5d-paper} shows the coverage of each reported integral under the rate reduction."),
  ("N4", "Thirty iterations reduce the $\\Eavail$ residual by \\SI{26}{\\percent};",
   "In these noise-free studies, thirty iterations reduce the $\\Eavail$ residual by \\SI{26}{\\percent};"),
 ],
}
for f, edits in E.items():
    p = f"{D}/{f}"; t = open(p, encoding="utf-8").read()
    for k, old, new in edits:
        if t.count(old) != 1:
            sys.exit(f"{f} {k}: {t.count(old)} matches")
        t = t.replace(old, new, 1)
    open(p, "w", encoding="utf-8").write(t)
p = f"{D}/app_codebase.tex"; t = open(p, encoding="utf-8").read()
if "fig:coverage-5d-paper" in t:
    sys.exit("N3 already applied")
open(p, "w", encoding="utf-8").write(t.rstrip("\n") + "\n\n" + FIG)
print("N1-N4 applied")
