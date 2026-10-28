r"""usage: python3 -I apply_b3.py ANALYSIS_NOTE_DIR -- r19 batch b3: Sec. V and the deletion of Sec. VI (variant B;
r19/outline.md; the director's rulings; DECISION-20261028-joseph-r19-variant-b-and-moves.md).

The edits:
- V A, new: the result table tab:result16 (Q5: one sigma column, C_total + C_resp, with a pointer to the note's
  tab:fived16-cells for the split), with DECISION-20261028-joseph-result-table-and-deposit-package.md item 1 applied:
  the uncertainty labelled marginal; quantitative comparisons need the full covariance (the note's correlation matrix);
  cell integrals, not differential densities; the largest edges explained as the analysis grid's outer edges (the data
  product's labels.units), not replaced by infinity. Every entry is an existing \fvval key, which make_values_fived16.py takes from
  fd_data_product.json (b79556f0, asserted against S1). Q8 is untouched. The block is FIVED16-marked, so a hand-typed
  numeral fails fived16 rule 7.
- V B lead, T4: the former Sec. VI lead's first sentence, so that "what makes the two-dimensional result reusable ..."
  stays in the paper (agy-b1n Q6; move-pass B58).
- V B, N6: the fake-data pointer goes to sec:fd16.
- Sec. VI is removed: its lead, VI A-D and Table VI, with the seven labels Q2's B ruling allows. Every fact prints in
  the note (r19/move-pass.md; N1-N4).
- K8: the null displacement stays as one clause, with a note pointer.
- K9: the Discussion's FWER sentence leaves. The Limitations paragraph's hybrid-null sentences become two sentences
  about the note's tests, with their conditions (review S4: the protected abstract still states the rejections).
- K13: the checklist's "tests can still be calibrated" sentence leaves (N1 carries the general lesson).
- K14: the Limitations paragraph's section range, and its fake-data pointer to sec:fd16.
- The checklist's "Secs. IV B and IV" becomes "Sec. IV" (review N6).

Every edit is an exact old -> new pair, whitespace-tolerant, that must match exactly once."""
import re, sys

D = sys.argv[1]
def pat(s): return re.compile(r"\s+".join(re.escape(w) for w in s.split()))
P = "paper_body.tex"
t = open(f"{D}/{P}", encoding="utf-8").read()

# Sec. VI, whole
a = t.find("\\section{Simulation-calibrated tests of generator predictions}")
z = t.find("\\section{Discussion and conclusions}")
if a < 0 or z < a or t.count("\\section{Simulation-calibrated tests") != 1:
    sys.exit("Sec. VI bounds not found")
vi = t[a:z]
for lab in ("sec:joint", "sec:hypotheses", "sec:calibration", "sec:conditions", "sec:response", "sec:joint-results", "tab:joint"):
    assert "\\label{%s}" % lab in vi, lab
t = t[:a] + t[z:]

rows = "\n".join(
    "    R%02d & \\fvval{box-R%02d-pt} & \\fvval{box-R%02d-pz} & \\fvval{box-R%02d-eavail} & \\fvval{box-R%02d-q3} & "
    "\\fvval{box-R%02d-W} & \\fvval{f-R%02d} & \\fvval{sig-C_total_resp-R%02d} \\\\" % ((c,) * 8) for c in range(16))
RESULT = (
    "\\subsection{Result}\n\n"
    "Table~\\ref{tab:result16} gives the sixteen-cell cross section: for each cell R00--R15, its box in the five observables, "
    "the cell-integrated cross section $f$, and its marginal relative uncertainty under the reported covariance "
    "$C_{\\mathrm{total}}+C_{\\mathrm{resp}}$ of Sec.~\\ref{sec:cov16}. The cells are correlated, so quantitative "
    "comparisons need the full covariance, whose correlation matrix is given in Ref.~\\cite{AnalysisNote2026}, "
    "Table~\\ref*{N-tab:fived16-corr}; Table~\\ref*{N-tab:fived16-cells} there gives the uncertainties under "
    "$C_{\\mathrm{total}}$ and $C_{\\mathrm{resp}}$ separately.\n\n"
    "% FIVED16-BEGIN (r19 b3: the result table; every entry is \\fvval{key} from values_fived16.tex, which make_values_fived16.py takes from fd_data_product.json b79556f0, asserted against S1; director Q5: one sigma column; the lead paragraph above holds no number, and its \\ref* to note labels sits outside the block, whose numeral check does not strip \\ref*)\n"
    "\\begin{table}[tb]\n"
    "  \\caption{The sixteen-cell cross section: each cell's box ($\\pT$, $\\pPar$ and $q_{3}$ in GeV/$c$; $\\Eavail$ and $W$ in GeV), "
    "the cell-integrated cross section $f$ (an integral over the box, not a differential density) in units of "
    "$\\fvval{f-unit}\\,\\si{cm^2/nucleon}$, and its marginal relative uncertainty $\\sigma/f$ (\\%), the square root of the "
    "diagonal of $C_{\\mathrm{total}}+C_{\\mathrm{resp}}$ over $f$. The largest edge on each axis is the outer edge of the "
    "analysis grid, so a box that reaches it holds every signal event above its lower edge on that axis. Quantitative "
    "comparisons need the full covariance (Sec.~\\ref{sec:cov16}).}\n"
    "  \\label{tab:result16}\n"
    "  \\centering\\scriptsize\\setlength{\\tabcolsep}{3pt}\n"
    "  \\begin{tabular}{@{}lcccccrr@{}}\n"
    "    \\toprule\n"
    "    cell & $\\pT$ & $\\pPar$ & $\\Eavail$ & $q_{3}$ & $W$ & $f$ & marginal $\\sigma/f$ \\\\\n"
    "    \\midrule\n" + rows + "\n"
    "    \\midrule\n"
    "    median & \\multicolumn{6}{c}{} & \\fvval{sigmed-C_total_resp} \\\\\n"
    "    \\bottomrule\n"
    "  \\end{tabular}\n"
    "\\end{table}\n"
    "% FIVED16-END\n\n")
anchor = "\\section{The sixteen-cell cross section}\n\\label{sec:result16}\n\n"
if t.count(anchor) != 1:
    sys.exit("Sec. V anchor not found once")
t = t.replace(anchor, anchor + RESULT, 1)

T4 = ("Unfolded results can be compared with any prediction at truth level without simulating each generator through the "
      "detector, which is what makes the two-dimensional result reusable, the higher-dimensional central values usable for "
      "qualitative comparison, and the sixteen-cell result usable for the comparisons below. ")
E = [
 ("T4", r"Table~\ref{tab:gen16} compares the sixteen-cell result of Sec.~\ref{sec:result16} with five predictions",
  T4 + r"Table~\ref{tab:gen16} compares the sixteen-cell result of Sec.~\ref{sec:result16} with five predictions"),
 ("N6 V B", r"The reported uncertainty does not cover the fake-data bias at the GiBUU-like truths (Sec.~\ref{sec:result16}).",
  r"The reported uncertainty does not cover the fake-data bias at the GiBUU-like truths (Sec.~\ref{sec:fd16})."),
 ("K8", r"The third is the upward displacement of the external nulls by the estimator's pull toward its prior, which the calibration of Sec.~\ref{sec:joint-results} reproduces.",
  r"The third is the upward displacement of the external null distributions of the note's calibrated tests by the estimator's pull toward its prior, which the calibration reproduces (\nsec{sec:joint5d-results})."),
 ("K9a", r" The calibrated tests illustrate inference with a biased estimator: the decision rule controls the familywise error rate at 5\% provided the calibration is exact.", ""),
 ("K13", r"  When intervals cannot be validated, tests can still be calibrated by simulating the analysis chain at the hypothesis, as in Sec.~\ref{sec:joint}.", ""),
 ("checklist refs", r"The studies of Secs.~\ref{sec:repro2d} and~\ref{sec:validation} show what must be checked",
  r"The studies of Sec.~\ref{sec:validation} show what must be checked"),
 ("K14", r"stated with the results they qualify, in Secs.~\ref{sec:repro2d}--\ref{sec:joint}.",
  r"stated with the results they qualify, in Secs.~\ref{sec:method}--\ref{sec:result16}."),
 ("K14 fd16", r"whose coverage is not validated; Sec.~\ref{sec:result16} reports the fake-data tests of the estimator's bias.",
  r"whose coverage is not validated; Sec.~\ref{sec:fd16} reports the fake-data tests of the estimator's bias."),
 ("K9b", r"The generator tests reject hybrid nulls, conditionally on the simulation's hadronic response.  The rejections carry over to the generator predictions themselves only under a bound on the residual below the fine grid, which has not been shown (Sec.~\ref{sec:conditions}).  Their calibration is valid to the extent that the simulated chain reproduces the analysis of the data (Sec.~\ref{sec:calibration}).",
  r"The note's calibrated tests reject hybrid nulls, conditionally on the simulation's hadronic response, and the rejections carry over to the generator predictions themselves only under a bound on the residual below the fine grid, which has not been shown.  Their calibration is valid to the extent that the simulated chain reproduces the analysis of the data (\nsec{sec:joint5d-conditions})."),
]
for k, old, new in E:
    m = list(pat(old).finditer(t))
    if len(m) != 1:
        sys.exit(f"{k}: {len(m)} matches")
    t = t[:m[0].start()] + new + t[m[0].end():]
open(f"{D}/{P}", "w", encoding="utf-8").write(t)
print("b3 applied: Sec. VI removed, V A added, %d edits" % len(E))
