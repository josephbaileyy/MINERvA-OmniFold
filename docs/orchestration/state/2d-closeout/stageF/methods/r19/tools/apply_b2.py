r"""usage: python3 -I apply_b2.py ANALYSIS_NOTE_DIR -- r19 batch b2, Sec. IV (variant B; r19/outline.md; the director's
rulings; DECISION-20261028-joseph-r19-variant-b-and-moves.md).

The edits:
- K12: the validation design's clause on the tests' calibration goes; it prints in the note.
- IV B SHORTEN: the bin-agreement fraction and the band share go; both print in the note's sec_results.tex.
- IV C SHORTEN: the block-dominance sentence and C_model's normalization detail go; both print in the note.
- O5: the pointer to the superseded statistical bands goes.
- IV E:
  - O3: the iteration and capacity diagnosis leaves; the interpretation stays, with its note pointer.
  - O1: the binned diagnostic collapses to one sentence that keeps its scope ("binned, signal-only and
    noise-free", and the 38% of residuals it covers: KEEP list), inside its CLAIM-ADDITION markers. Table III goes.
  - The fake-data pointer goes to sec:fd16 (review N6).
- IV F:
  - O2: the Gaussian diagnosis's method and secondary findings leave; its result and the unestablished source stay.
  - O4: Fig. 4 goes. The warning sentence and the headline count (R4: the bound stays) stay, pointing to the note.
- IV G, T3: the rounding sentence is split (R10). Its consequence clause is the paper's own printed text (director,
  Q4). The pointer to the earlier covariance goes.
- IV H, T2: definition before claim (R9): the truths' status first, the reduced covariance named by Table IV's Cov.
  column, the ungraded truths last.
  K7: the hybrid truths are defined directly, now that the tests have left.

Every edit is an exact old -> new pair, whitespace-tolerant, that must match exactly once. Every fact that leaves
prints in the note, at a row of r19/ledger.md."""
import re, sys

D = sys.argv[1]
def pat(s): return re.compile(r"\s+".join(re.escape(w) for w in s.split()))
P = "paper_body.tex"
t = open(f"{D}/{P}", encoding="utf-8").read()

def cut_block(t, start, end_marker, what):
    """Remove from the line starting with START through the line holding END_MARKER, plus one following blank line."""
    i = t.find(start)
    if t.count(start) != 1:
        sys.exit(f"{what}: start found {t.count(start)} times")
    j = t.find(end_marker, i)
    if j < 0:
        sys.exit(f"{what}: end not found")
    j = t.index("\n", j) + 1
    while t[j:j + 1] == "\n":
        j += 1
    return t[:i] + t[j:]

# Table III (O1): from its \begin{table} line to its \end{table}
i = t.find("\\label{tab:binned}"); b = t.rfind("\\begin{table}", 0, i)
assert t.count("\\label{tab:binned}") == 1 and "Median absolute residual" in t[b:i]
t = t[:b] + t[t.index("\\end{table}", i) + len("\\end{table}"):].lstrip("\n")
# Fig. 4 (O4): from its \begin{figure*} to its \end{figure*}
i = t.find("\\label{fig:coverage}"); b = t.rfind("\\begin{figure*}", 0, i)
assert "paper_fig_coverage" in t[b:i]
t = t[:b] + t[t.index("\\end{figure*}", i) + len("\\end{figure*}"):].lstrip("\n")

E = [
 ("K12", r"Every study uses the analysis simulation's detector response, except the calibration of the tests, which also draws the detector bands.",
  r"Every study uses the analysis simulation's detector response."),
 ("IV B bins", r"  Of the 205 reported bins, \SI{\binsTen}{\percent} agree within \SI{10}{\percent}.", ""),
 ("IV B band", r"  No single $\pT$ or $\pPar$ band carries more than \SI{15}{\percent} of it.", ""),
 ("IV C dominance", r"  The systematic-universe block dominates it bin by bin and in the integral, and the run-period block raises the per-bin median from \SI{\uqSFiveMedian}{\percent} to \SI{\uqMedian}{\percent}.", ""),
 ("O5", r"  The block supersedes two earlier statistical bands, whose coverage studies are described in \nsec{sec:coverage}.", ""),
 ("IV C C_model", r"  Because the reweighting keeps the prior's normalization, $C_{\mathrm{model}}$ is a shape component.  It is \SI{\cmodelIntegral}{\percent} on the integrated cross section, which leaves the integrated uncertainty at \SI{\uqIntegral}{\percent}, and it does not test the model dependence of the normalization.", ""),
 ("O3", r"We interpret the residual as regularization bias because it persists over the tested iteration numbers and classifier capacities: in noise-free studies of that variant, thirty iterations reduce the $\Eavail$ residual by \SI{26}{\percent}, while a larger classifier improves the reconstruction-level fit without reducing it.",
  r"We interpret the residual as regularization bias, because it persists over the tested iteration numbers and classifier capacities (\nsec{sec:val-departure})."),
 ("N6", r"unscaled and not a calibrated bound; Sec.~\ref{sec:result16} reports the fake-data tests of the estimator's bias.",
  r"unscaled and not a calibrated bound; Sec.~\ref{sec:fd16} reports the fake-data tests of the estimator's bias."),
 ("IV E pointer", r"The deformation studies, the iteration and capacity tests, and the joint-test-estimator shapes are described in",
  r"The deformation studies, the iteration and capacity tests, the exact binned comparison and the joint-test-estimator shapes are described in"),
 ("O1",
  r"A diagnostic in simulation, summarized in Table~\ref{tab:binned}, bears on the first of these results.  On the same \jtNcells{} joint cells and the fixed truth changes used to develop the estimator, an exact binned iterative unfolding with the same simulation and five iterations leaves about the same median residual as the boosted-tree estimator.  Of the 144 cell-and-truth-change residuals above \SI{2}{\percent} whose diagnosis is stable under the truth resolution, pooled over five truth changes, the tree approximation dominates only 15.  Most of the 144 (121) lie in quantities that the binned response constrains weakly at the analysis exposure, with Cram\'er--Rao widths above \SI{10}{\percent}, so the regularization trades a large variance for the bias.  Longer noise-free exact iteration removes much of the residual for the GiBUU-to-GENIE change, but not for every change.  The long runs do not converge, so this rests on their last iterates.",
  r"In a binned, signal-only and noise-free diagnostic on the \jtNcells{} joint cells, with the detector response fixed at the simulation's, an exact binned iterative unfolding with five iterations leaves about the same median residual as the boosted-tree estimator, and the residuals whose diagnosis is stable under the truth resolution (\SI{38}{\percent} of the joint-cell residuals above \SI{2}{\percent}) are consistent with the regularization of the inverse problem at this binning and prior, rather than with the tree approximation of the classifiers (\nsec{sec:val-departure})."),
 ("O1 rest",
  r"The diagnostic is binned, signal-only and noise-free, with the detector response fixed at the simulation's.  It covers only the residuals whose diagnosis is stable under the truth resolution (\SI{38}{\percent} of the joint-cell residuals above \SI{2}{\percent}).  What unbinned information could recover, the coverage failure, and the validity of any interval lie outside its scope.  Within that scope, the residual is consistent with the regularization of the inverse problem at this binning and prior, rather than with the tree approximation of the classifiers (\nsec{sec:val-departure}).",
  ""),
 ("O4", r"The tested change reweights the true signal, without renormalization and with the background unchanged, and is in effect a \SI{10}{\percent} reduction of the signal rate with a weak $\Eavail$ slope. Figure~\ref{fig:coverage} shows that under that change, 51 of the 153 reported cell and projection integrals have a 68\% coverage whose upper confidence bound lies below the acceptance threshold of 0.66, with coverage as low as 0.06.",
  r"Under that change, 51 of the 153 reported cell and projection integrals have a 68\% coverage whose upper confidence bound lies below the acceptance threshold of 0.66, with coverage as low as 0.06."),
 ("O2", r"A diagnosis that fits a Gaussian bias and spread to each quantity's 68\% and 95\% coverage attributes the miscoverage to a residual bias that grows with $W$ and survives the nominal-truth bias correction.  The source of this residual bias has not been established.  The rate change itself is recovered, and, apart from a minor effect, the intervals are not too narrow. Agreement",
  r"A diagnosis attributes the miscoverage to a residual bias that grows with $W$ and survives the nominal-truth bias correction.  The source of this residual bias has not been established. Agreement"),
 ("T3", r"The joint-test estimator is unstable at the level of rounding: rounding-level input changes move its results by up to 2.6 statistical standard deviations, as they move those of its lower-capacity development variant (2.5), so it fails a data-stability requirement of at most 0.3 (median) and 1.0 (maximum) statistical standard deviations. This spread lies inside the data-bootstrap statistical uncertainty, but it limits how exactly the central values can be reproduced. The covariance of the earlier purity-subtracted five-observable central value, its status and its seed studies are given in \nsec{sec:eavailw-construction}.",
  r"The joint-test estimator is unstable at the level of rounding. Rounding-level changes of its inputs move its results by up to 2.6 statistical standard deviations, and those of its lower-capacity development variant by up to 2.5, so it fails a data-stability requirement of at most 0.3 (median) and 1.0 (maximum) statistical standard deviations. This spread lies inside the data-bootstrap statistical uncertainty, but it limits how exactly the central values can be reproduced."),
 ("T2", r"The truths are the simulation's prior; the five hybrid truths of the generator tests of Sec.~\ref{sec:joint}, each a prediction on the fine grid; NuWro shape changes in $\Eavail$ and in $(\pT,\pPar,\Eavail)$; a GENIE + MEC shape change in $(\Eavail,W)$; a GiBUU-to-GENIE $\Eavail$ ratio; a noise-free closure at the NuWro shape; and a synthetic tilt of the $q_3$ distribution at fixed $(\Eavail,W)$. A truth from a generator that contributes to $C_{\mathrm{model}}$ is compared with the covariance without that generator's component; \fvval{f0b-nungraded} further truths are ungraded (given in the note). A truth is listed when $p<\fvval{trig-p}$ or when a cell has $|z|>\fvval{trig-z}$. These are not held-out truths. Table~\ref{tab:fd16} gives the results under the reported covariance and under $C_{\mathrm{total}}$ alone.",
  r"The truths are not held out: they are the simulation's prior; five hybrid truths, each a generator prediction on the fine grid with the MINERvA Tune~v1 composition below it; NuWro shape changes in $\Eavail$ and in $(\pT,\pPar,\Eavail)$; a GENIE + MEC shape change in $(\Eavail,W)$; a GiBUU-to-GENIE $\Eavail$ ratio; a noise-free closure at the NuWro shape; and a synthetic tilt of the $q_3$ distribution at fixed $(\Eavail,W)$. For a truth from a generator that contributes to $C_{\mathrm{model}}$, the covariance omits that generator's component, as the Cov. column of Table~\ref{tab:fd16} shows. A truth is listed when $p<\fvval{trig-p}$ or when a cell has $|z|>\fvval{trig-z}$. Table~\ref{tab:fd16} gives the results under the reported covariance and under $C_{\mathrm{total}}$ alone; \fvval{f0b-nungraded} further truths are ungraded and given in the note."),
]
for k, old, new in E:
    m = list(pat(old).finditer(t))
    if len(m) != 1:
        sys.exit(f"{k}: {len(m)} matches")
    t = t[:m[0].start()] + new + t[m[0].end():]
# the emptied O1 paragraph leaves a blank pair; collapse only that run, between the D-ID markers
a = t.find("% CLAIM-ADDITION D-ID BEGIN"); z = t.find("% CLAIM-ADDITION D-ID END", a)
t = t[:a] + re.sub(r"\n{3,}", "\n\n", t[a:z]) + t[z:]
open(f"{D}/{P}", "w", encoding="utf-8").write(t)
print("b2 applied: %d edits, Table III and Fig. 4 removed" % len(E))
