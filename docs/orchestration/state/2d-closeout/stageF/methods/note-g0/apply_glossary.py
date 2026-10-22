#!/usr/bin/env python3
"""Apply the batch-0 glossary (GLOSSARY.md) to the analysis note, as explicit, asserted edits.

usage: apply_glossary.py <worktree> [--dry-run]

Every edit is (file, old, new, terms, allow). The script reads each file from the BASE commit (git show BASE:path),
never from the working tree, so a rerun gives the same result. For each edit it asserts, and stops on failure:

  1. `old` matches exactly once in the file as it stands after the previous edits to that file (whitespace in `old`
     matches any run of whitespace, so line breaks in the source do not matter; a LaTeX comment inside the span makes
     the match fail, which is intended -- an edit never crosses a comment);
  2. `old` is not a substring of `new` (the ledger's absence probe depends on it), except for a pure insertion
     ("insert" in `allow`), whose ledger row then carries only the presence probe;
  3. the multiset of numbers is unchanged, unless "num" is in `allow` (the reason is stated with the edit);
  4. the multiset of \\ref/\\eqref/\\cite targets is unchanged, unless "ref" is in `allow`;
  5. the multiset of value macros (every \\newcommand of values.tex and values_inference.tex) is unchanged -- always;
  6. the count of negation words (not, no, nor, neither, never, cannot, without, none, nothing, unmeasured,
     undetermined) does not decrease, unless "neg" is in `allow`;
  7. the edit does not touch a protected span: the verbatim specification quote of sec_joint.tex, the verbatim
     GiBUU label of sec_joint.tex (checked byte for byte against the base after all edits), the release
     paragraph of sec_summary.tex, and everything in main_note.tex outside the abstract.

It then writes the files to <worktree>/docs/analysis-note/ and the ledger (ledger.md, next to this script): one row per
edit with file:line in the base, before, after, and the probes `N:<file>::<after>` (must print) and
`X:<file>::<before>` (must no longer print), which check_ledger.py runs.
"""
from __future__ import annotations

import collections
import re
import subprocess
import sys
from pathlib import Path

BASE = "38a53a53"
HERE = Path(__file__).resolve().parent
NOTE = "docs/analysis-note"

E = []  # the edits, in file order


def ed(f, old, new, terms, allow=(), why=""):
    E.append(dict(file=f, old=old, new=new, terms=terms, allow=set(allow), why=why))


# ---------------------------------------------------------------------------------------------------------------
# main_note.tex: the abstract only
ed("main_note.tex",
   r"satisfies the adopted 10\% criterion.",
   r"satisfies the predeclared 10\% criterion.",
   "adopt*", why="the criterion was fixed before the study (sec:gbdt-model-dependence; exec. summary)")

# ---------------------------------------------------------------------------------------------------------------
# sec_execsummary.tex
ed("sec_execsummary.tex",
   r"Under an in-effect \SI{10}{\percent} signal-rate reduction (recorded as an ``$\Eavail$ tilt'') the rate is recovered",
   r"Under a truth change that is in effect a \SI{10}{\percent} signal-rate reduction (labelled an ``$\Eavail$ tilt'') the rate is recovered",
   "in-effect; record label")
ed("sec_execsummary.tex",
   r"limit every result built from the five-dimensional covariance in use (\S\ref{sec:eavailw-adopted}); no other corrected candidate is used in its place.",
   r"limit every result built from the five-dimensional covariance used in this note (\S\ref{sec:eavailw-adopted}); no other corrected five-dimensional covariance is used in its place.",
   "in use; candidate")

# ---------------------------------------------------------------------------------------------------------------
# sec_intro.tex
ed("sec_intro.tex",
   r"shortened account whose omitted detail lives in these homes.",
   r"shortened account whose omitted detail is in these sections.",
   "homes")
ed("sec_intro.tex", r"Topic & Home \\", r"Topic & Section \\", "homes")
ed("sec_intro.tex",
   r"The five-axis covariance in use and its four measurements",
   r"The five-axis covariance used in this note and its four measurements",
   "in use")

# ---------------------------------------------------------------------------------------------------------------
# sec_experiment.tex
ed("sec_experiment.tex",
   r"MnvTune central-value weight. Universe-complete",
   r"MINERvA Tune~v1 central-value weight. The systematic-universe trees",
   "MnvTune; universe-complete", allow={"num"}, why="'MINERvA Tune~v1' adds the 1 of the generator tune's name")
ed("sec_experiment.tex",
   r"variants also carry all systematic-universe weights and laterally-shifted observables (\S\ref{sec:systematics}). Two invariants keep the result truth-tree authoritative:",
   r"also carry every universe's weight and each lateral band's shifted observables (in MAT's terms, a lateral band shifts reconstructed kinematics and a vertical band reweights events; \S\ref{sec:systematics}). Two conditions make the truth tree the complete reference for the simulated signal:",
   "lateral (defined); truth-tree authoritative; invariants")
ed("sec_experiment.tex",
   r"the more-than-\SI{100}{GB} universe dumps.",
   r"the trees with per-universe content, which exceed \SI{100}{GB}.",
   "dumps")
ed("sec_experiment.tex",
   r"Selected data exceed the POT-scaled MnvTune-v1 prediction",
   r"Selected data exceed the POT-scaled MINERvA Tune~v1 prediction",
   "MnvTune")
ed("sec_experiment.tex",
   r"data normalization excess over MnvTune v1",
   r"data normalization excess over MINERvA Tune~v1",
   "MnvTune")

# ---------------------------------------------------------------------------------------------------------------
# sec_method.tex
ed("sec_method.tex",
   r"larger. It is not adopted, and the quoted extended-fiducial value does not use it (App.~\ref{app:negweight}).",
   r"larger. The quoted central values and uncertainties, including the extended-fiducial value, do not use it (App.~\ref{app:negweight}).",
   "adopt*", allow={"neg"},
   why="'not adopted' meant not used for the quoted results; the refined form IS used by the generator tests, so "
       "'not used for any result' would be false. The two clauses merge, so their two negations become one "
       "('do not use it')")
ed("sec_method.tex",
   r"(seed~42; its file and digest are in App.~\ref{app:provenance}, \texttt{2d-central-value})",
   r"(seed~42; its file name and checksum are listed in App.~\ref{app:provenance}, \texttt{2d-central-value})",
   "digest")
ed("sec_method.tex",
   r"and a receipted regeneration with the current driver reproduces it to the same level.",
   r"and a regeneration with the current driver, with its run configuration recorded, reproduces it to the same level.",
   "receipted")
ed("sec_method.tex",
   r"costed in the design record;",
   r"costed in the analysis design;",
   "design record")
ed("sec_method.tex",
   r"(its production launcher passed no seed, and the driver revision it ran had no seed option,",
   r"(its production job script passed no seed, and the driver version it ran had no seed option,",
   "launcher")
ed("sec_method.tex",
   r"It was selected before the joint-test design was frozen (\S\ref{sec:joint5d});",
   r"It was selected before the joint-test design was fixed (\S\ref{sec:joint5d});",
   "frozen")
ed("sec_method.tex",
   r"including MnvTune reweighting.",
   r"including MINERvA Tune~v1 reweighting.",
   "MnvTune", allow={"num"}, why="the 1 of the tune's name")
ed("sec_method.tex",
   r"is self-tested to reproduce frozen lower-dimensional extractions",
   r"is self-tested to reproduce stored lower-dimensional reference extractions",
   "frozen")
ed("sec_method.tex",
   r"truncating the top edge would break the marginalization anchors of",
   r"truncating the top edge would break the marginalization checks of",
   "anchor")
ed("sec_method.tex",
   r"Neither a profiled estimator nor its uncertainty is adopted here.",
   r"Neither a profiled estimator nor its uncertainty is used here.",
   "adopt*")

# ---------------------------------------------------------------------------------------------------------------
# sec_systematics.tex
ed("sec_systematics.tex",
   r"The five lateral bands are taken from selection-complete re-unfolds at the same seed. The rollup drops Rvp1pi,",
   r"The five lateral bands are taken from re-unfolds of re-selected universes (event loops that re-apply the selection to each universe's shifted kinematics; \S\ref{sec:uq-higherdim}) at the same seed. The band sum drops Rvp1pi,",
   "selection-complete (defined as re-selected); rollup", allow={"ref"}, why="adds the pointer to where the term is explained")
ed("sec_systematics.tex",
   r"App.~\ref{app:history-vl175} (App.~\ref{app:provenance}, \texttt{coverage-fixed-truth}, gives the label under which it is recorded there).",
   r"App.~\ref{app:history-vl175} (its repository label is listed in App.~\ref{app:provenance}, \texttt{coverage-fixed-truth}).",
   "App. G tag sentence")
ed("sec_systematics.tex",
   r"that the statistical band in use when it ran, before that rebuild, undercovered",
   r"that the statistical band quoted when it ran, before that rebuild, undercovered",
   "in use")
ed("sec_systematics.tex",
   r"takes its lateral bands from selection-complete re-unfolds (\S\ref{sec:uq-universes}).",
   r"takes its lateral bands from re-unfolds of re-selected universes (\S\ref{sec:uq-universes}).",
   "selection-complete")
ed("sec_systematics.tex",
   r"Dump-all shifted branches are limited to CV event-loop support. For the five kinematic bands (BeamAngleX/Y, MuonResolution, and Muon\_Energy\_MINERvA/MINOS), selection-complete active-universe event loops are the production migration gate. They supply the lateral block of the five-axis covariance in use; higher-dimensional products using dump-all lateral branches remain candidates. Replacing the support-limited lateral block by the selection-complete one moves that block's square-root trace by",
   r"Two event-loop modes supply the lateral bands. The single-pass event loop, which writes every universe in one pass, stores each lateral universe's shifted observables only for events that pass the selection at the central value, so it omits events that the shift moves into the selection. Re-selected event loops re-run the selection with one lateral universe active at a time. For the five kinematic bands (BeamAngleX/Y, MuonResolution, and Muon\_Energy\_MINERvA/MINOS), production treats selection migration with the re-selected event loops. They supply the lateral-band block of the five-axis covariance used in this note. Higher-dimensional products built from the single-pass shifted observables are not used for any quoted uncertainty. Replacing the single-pass lateral-band block by the re-selected one moves that block's square-root trace by",
   "dump-all; CV support; selection-complete; active-universe; migration gate; in use; candidates; support-limited",
   why="'remain candidates' = not adopted; restated as 'not used for any quoted uncertainty' (no 3D, 4D or "
       "extended-fiducial covariance is quoted, and the 5D one used is built from re-selected event loops)")
ed("sec_systematics.tex",
   r"the per-bin ratio of active to support standard deviation runs",
   r"the per-bin ratio of re-selected to single-pass standard deviation runs",
   "active / support")
ed("sec_systematics.tex",
   r"within the top \SI{1}{\percent} of bins by support variance",
   r"within the top \SI{1}{\percent} of bins by single-pass variance",
   "support")
ed("sec_systematics.tex",
   r"\paragraph{Scope of the selection-complete replacement.}",
   r"\paragraph{Scope of the re-selected replacement.}",
   "selection-complete")
ed("sec_systematics.tex",
   r"dominates the band in use over effects of the particular train/test partition.",
   r"dominates the band used in this note over effects of the particular train/test partition.",
   "in use")
ed("sec_systematics.tex",
   r"An earlier 5D candidate used both mean-centered and CV-centered unified throws",
   r"An earlier 5D covariance construction used both mean-centered and CV-centered unified throws",
   "candidate")
ed("sec_systematics.tex",
   r"neither is used. The covariance in use is a later, separate \texttt{cv}-variant build",
   r"neither is used. The covariance used in this note is a later, separate build in which the unified-throw covariance is centered on the central value (variant \texttt{cv})",
   "in use; cv label")
ed("sec_systematics.tex",
   r"and the covariance \emph{in use} by \SI{0.18}{\percent},",
   r"and the covariance \emph{used in this note} by \SI{0.18}{\percent},",
   "in use")

# ---------------------------------------------------------------------------------------------------------------
# sec_validation.tex
ed("sec_validation.tex",
   r"Membership and completeness invariants; no recovery or coverage claim",
   r"Membership and completeness conditions; no recovery or coverage claim",
   "invariants")
ed("sec_validation.tex",
   r"defines a complementary record-only $\Eavail$ response-mismatch closure and a more complete leading-nucleon follow-up.",
   r"defines a complementary response-mismatch closure that rescales only the reconstructed $\Eavail$ of the pseudo-data, and a more complete leading-nucleon follow-up.",
   "record-only")
ed("sec_validation.tex",
   r"This test asks whether the 2D statistical band in use when it ran (App.~\ref{app:history}, under the label listed in App.~\ref{app:provenance}, \texttt{coverage-fixed-truth}) covers",
   r"This test asks whether the 2D statistical band quoted when it ran (App.~\ref{app:history}; its repository label is listed in App.~\ref{app:provenance}, \texttt{coverage-fixed-truth}) covers",
   "in use; App. G tag sentence")
ed("sec_validation.tex",
   r"(lgbm, five iterations, fixed training seed)",
   r"(LightGBM, five iterations, fixed training seed)",
   "lgbm")
ed("sec_validation.tex",
   r"(its undercoverage branch was written after the pilot pulls had been seen)",
   r"(its rule for the undercoverage outcome was written after the pilot pulls had been seen)",
   "branch")
ed("sec_validation.tex",
   r"HistGBT and exact-GBT agree on total $\sigma$ to",
   r"the histogram-based and exact-split backends agree on total $\sigma$ to",
   "exact-GBT")

# ---------------------------------------------------------------------------------------------------------------
# sec_results.tex
ed("sec_results.tex",
   r"carry the bin errors stored with the unfolded histogram (\texttt{hXSec2D}; in the projections, \texttt{hXSec\_pt} and \texttt{hXSec\_pz}); they are not drawn",
   r"carry the bin errors stored with the unfolded histogram and its projections (\texttt{hXSec2D}, \texttt{hXSec\_pt}, \texttt{hXSec\_pz}); they are not drawn",
   "hXSec (code identifiers kept as one parenthetical)", allow={"num"},
   why="the digit 2 of hXSec2D is unchanged; the token split differs only by punctuation")
ed("sec_results.tex",
   r"ML noise (lgbm training-seed settings) &",
   r"ML noise (LightGBM training-seed settings) &",
   "lgbm")

# ---------------------------------------------------------------------------------------------------------------
# sec_3d.tex
ed("sec_3d.tex",
   r"In MeV, \texttt{CVUniverse::GetEAvailableTrue()} implements",
   r"In MeV, the truth accessor (\texttt{CVUniverse::GetEAvailableTrue()}) implements",
   "CVUniverse:: (kept as parenthetical)")
ed("sec_3d.tex",
   r"implemented by \texttt{CVUniverse::NewEavail()}; the code applies",
   r"implemented in the reconstruction accessor (\texttt{CVUniverse::NewEavail()}); the code applies",
   "CVUniverse:: (kept as parenthetical)")
ed("sec_3d.tex",
   r"against the projection of the scalar-5D covariance in use.",
   r"against the projection of the five-dimensional covariance used in this note.",
   "in use", allow={"num"}, why="'scalar-5D' -> 'five-dimensional': the digit 5 becomes the word")
ed("sec_3d.tex",
   r"our validation anchor in the absence of",
   r"our validation reference in the absence of",
   "anchor")
ed("sec_3d.tex",
   r"Data have no error bars because the quotable 3D covariance is not in use (App.~\ref{app:history}).",
   r"Data have no error bars because the 3D covariance that would be quoted is not used for any result in this note (App.~\ref{app:history}).",
   "quotable; in use")
ed("sec_3d.tex",
   r"the quotable 3D covariance is the exact projection of the 5D covariance in use, and that projection is constructed but not in use (App.~\ref{app:history}).",
   r"the 3D covariance that would be quoted is the exact projection of the five-dimensional covariance used in this note, and that projection has been computed but is not used for any result in this note (App.~\ref{app:history}).",
   "quotable; in use; constructed but not in use", allow={"num"}, why="'5D' -> 'five-dimensional'")
ed("sec_3d.tex",
   r"because the 3D covariance that would be quoted is not yet in use (App.~\ref{app:history}).",
   r"because the 3D covariance that would be quoted is not yet used for any result in this note (App.~\ref{app:history}).",
   "in use")
ed("sec_3d.tex",
   r"because the 3D covariance that would be quoted is not in use (App.~\ref{app:history}).",
   r"because the 3D covariance that would be quoted is not used for any result in this note (App.~\ref{app:history}).",
   "in use")
ed("sec_3d.tex",
   r"Lateral systematic shifts change $q_{3}$ but leave $\Eavail$ invariant, requiring per-universe shifted-$q_{3}$ dumps instead of central-value reuse.",
   r"Lateral systematic shifts change $q_{3}$ but leave $\Eavail$ invariant, so the event loop must store a shifted $q_{3}$ for each lateral universe instead of reusing the central value.",
   "dumps")
ed("sec_3d.tex",
   r"\paragraph{Marginal anchor (4D$\to$3D).}",
   r"\paragraph{Marginalization check (4D$\to$3D).}",
   "anchor")
ed("sec_3d.tex",
   r"3D$\to$2D Jacobian anchor (\S\ref{sec:3d-anchor}).",
   r"3D$\to$2D marginalization check (\S\ref{sec:3d-anchor}).",
   "anchor")
ed("sec_3d.tex",
   r"Because dump-all lateral branches are CV-support-limited, selection-complete active-universe event loops must bound migration effects.",
   r"Because the single-pass shifted observables exist only for events selected at the central value, re-selected event loops (\S\ref{sec:uq-higherdim}) must bound migration effects.",
   "dump-all; support-limited; selection-complete; active-universe", allow={"ref"},
   why="adds the pointer to where the two event-loop modes are explained")
ed("sec_3d.tex",
   r"4D covariance that would be quoted is not in use (App.~\ref{app:history}); the",
   r"4D covariance that would be quoted is not used for any result in this note (App.~\ref{app:history}); the",
   "in use")

# ---------------------------------------------------------------------------------------------------------------
# sec_eavailw.tex
ed("sec_eavailw.tex",
   r"so the event loop dumps shifted-$W$ lateral universes per universe, mirroring the $q_{3}$ treatment (\S\ref{sec:4d}); the dump also carries truth hadronic diagnostics",
   r"so the event loop stores a shifted $W$ for each lateral universe, mirroring the $q_{3}$ treatment (\S\ref{sec:4d}); these trees also carry truth hadronic diagnostics",
   "dumps")
ed("sec_eavailw.tex",
   r"passes its predecessors' marginalization anchors. Integrating over $W$ recovers the frozen 4D normalization to",
   r"passes the marginalization checks against the lower-dimensional results. Integrating over $W$ recovers the reported 4D normalization to",
   "anchor; frozen")
ed("sec_eavailw.tex",
   r"recorded tests of \S\ref{sec:joint5d} do not correct; \S\ref{sec:joint5d-ch} gives replays with the correction.",
   r"tests of \S\ref{sec:joint5d}, as run, do not correct; \S\ref{sec:joint5d-ch} re-evaluates them with the correction.",
   "replay")

# ---------------------------------------------------------------------------------------------------------------
# sec_5d.tex
ed("sec_5d.tex",
   r"of the one five-axis covariance in use (\S\ref{sec:eavailw-construction}).",
   r"of the one five-axis covariance used in this note (\S\ref{sec:eavailw-construction}).",
   "in use")
ed("sec_5d.tex",
   r"It comes from the purity footing (\S\ref{app:negweight}),",
   r"It comes from the purity-based subtraction (\S\ref{app:negweight}),",
   "footing")
ed("sec_5d.tex",
   r"or transfer to the five-axis covariance in use.",
   r"or transfer to the five-axis covariance used in this note.",
   "in use")
ed("sec_5d.tex",
   r"\subsection{The five-axis covariance in use and its $(\Eavail,W)$ projection}",
   r"\subsection{The five-axis covariance used in this note and its $(\Eavail,W)$ projection}",
   "in use")
ed("sec_5d.tex",
   r"The five-axis covariance in use, variant \texttt{cv}, has an $(\Eavail,W)$",
   r"The five-axis covariance used in this note, the variant centered on the central value (\texttt{cv}), has an $(\Eavail,W)$",
   "in use; cv label")
ed("sec_5d.tex",
   r"their SHA-256 digests in App.~\ref{app:release-identities}.",
   r"their SHA-256 checksums in App.~\ref{app:release-identities}.",
   "digest")
ed("sec_5d.tex",
   r"so that requirement cannot be met for this object, and the object's own metadata records it",
   r"so that requirement cannot be met for this covariance, and the file's own metadata records it",
   "this object")
ed("sec_5d.tex",
   r"Selection-complete active-universe event loops now bound migrations omitted by the CV-support-limited dump-all sample (\S\ref{sec:uq-higherdim}).",
   r"Re-selected event loops now bound the selection migrations that the single-pass shifted observables omit (\S\ref{sec:uq-higherdim}).",
   "selection-complete; active-universe; support-limited; dump-all")
ed("sec_5d.tex",
   r"$A$ (active lateral)",
   r"$A$ (re-selected lateral)",
   "active lateral")
ed("sec_5d.tex",
   r"Inflation in variant \texttt{cv} uses",
   r"Inflation in the CV-centered variant uses",
   "cv label")
ed("sec_5d.tex",
   r"Retaining it is deliberate: the variant in use is \texttt{cv}. The mean-centered sibling's $\sqrt{\Tr C}$ is \SI{7.13}{\percent} lower. The variant must be read and checked in product metadata, never inferred from a path",
   r"Retaining it is deliberate: the variant used is the CV-centered one. The $\sqrt{\Tr C}$ of the mean-centered variant (\texttt{mean}) is \SI{7.13}{\percent} lower. Which variant a file holds must be read and checked in its metadata, never inferred from its path",
   "in use; sibling; cv label; product metadata")
ed("sec_5d.tex",
   r"byte-identical in \texttt{cv} and \texttt{mean}. We pair this covariance with the central values in Fig.~\ref{fig:eavailWexcess} \emph{by digest identity} rather than numerical agreement.",
   r"byte-identical in the two variants. We pair this covariance with the central values in Fig.~\ref{fig:eavailWexcess} \emph{by checksum identity} rather than numerical agreement.",
   "cv label; digest")
ed("sec_5d.tex",
   r"only item three describes these bytes.",
   r"only item three describes this file.",
   "these bytes")
ed("sec_5d.tex",
   r"\emph{has not been computed} for this object.",
   r"\emph{has not been computed} for this covariance.",
   "this object")
ed("sec_5d.tex",
   r"and their outcomes are not outcomes for this object (App.~\ref{app:provenance}, \texttt{z-cv-record}).",
   r"and their outcomes are not outcomes for this covariance (App.~\ref{app:provenance}, \texttt{z-cv-record}).",
   "this object")

# ---------------------------------------------------------------------------------------------------------------
# sec_joint.tex (the verbatim specification quote is protected)
ed("sec_joint.tex",
   r"and do not re-qualify the five-axis covariance in use of \S\ref{sec:eavailw-adopted}, which they do not use.",
   r"and do not validate the five-axis covariance used elsewhere in this note (\S\ref{sec:eavailw-adopted}), which they do not use.",
   "re-qualify; in use")
ed("sec_joint.tex",
   r"refinement classifier, chosen before the design was frozen).",
   r"refinement classifier, chosen before the design was fixed).",
   "frozen")
ed("sec_joint.tex",
   r"\subsection{Multiplicity, stopping rule and the frozen design}",
   r"\subsection{Multiplicity, stopping rule and the predeclared design}",
   "frozen")
ed("sec_joint.tex",
   r"every input were frozen before any production pseudo-experiment",
   r"every input were fixed before any production pseudo-experiment",
   "frozen")
ed("sec_joint.tex",
   r"had seen descriptive per-cell residuals before it was frozen,",
   r"had seen descriptive per-cell residuals before it was fixed,",
   "frozen")
ed("sec_joint.tex",
   r"to let the sequential rule reach its frozen stop rather than a budget stop.",
   r"to let the sequential rule reach the stop set by its predeclared rule rather than a budget stop.",
   "frozen")
ed("sec_joint.tex",
   r"The frozen design takes the step in a proxy",
   r"The predeclared design takes the step in a proxy",
   "frozen")
ed("sec_joint.tex",
   r"and the report-only robustness check at",
   r"and the robustness check, for reporting only (outside the decision rule), at",
   "report-only")
ed("sec_joint.tex",
   r"the frozen stop (1400 submitted per null, NuWro 1800; the rest were lost to time limits and recovered report-only, \S\ref{sec:joint5d-lost}),",
   r"the stop set by the predeclared rule (1400 submitted per null, NuWro 1800; the rest were lost to time limits and later recovered for reporting only, \S\ref{sec:joint5d-lost}),",
   "frozen; report-only")
ed("sec_joint.tex",
   r"A report-only scan along the frozen direction $\delta_{\mathrm{fine}}$~\cite{JointTestKappa2026} found all ten decisions to remain determinate rejections at every sampled multiplier up to 5.25 in the frozen ensembles.",
   r"A scan along the predeclared direction $\delta_{\mathrm{fine}}$~\cite{JointTestKappa2026}, for reporting only, found all ten decisions to remain determinate rejections at every sampled multiplier up to 5.25 in the calibration ensembles used for the decisions.",
   "report-only; frozen")
ed("sec_joint.tex",
   r"These come from the frozen sets, each of which lost",
   r"These come from the power sets as evaluated for the decisions, each of which lost",
   "frozen")
ed("sec_joint.tex",
   r"Against the frozen null ensembles, the complete power sets",
   r"Against the null ensembles used for the decisions, the complete power sets",
   "frozen")
ed("sec_joint.tex",
   r"The lost seeds were therefore rerun, report-only, under a procedure",
   r"The lost seeds were therefore rerun, for reporting only, under a procedure",
   "report-only")
ed("sec_joint.tex",
   r"batches the frozen rule would have stopped",
   r"batches the predeclared rule would have stopped",
   "frozen")
ed("sec_joint.tex",
   r"covers only the reading with the frozen variant shifts;",
   r"covers only the reading with the variant shifts of the primary evaluation;",
   "frozen")
ed("sec_joint.tex",
   r"reproduced only by a standalone replay of the same code,",
   r"reproduced only by a standalone rerun of the same code,",
   "replay")
ed("sec_joint.tex",
   r"the earlier-stop decisions rest on the campaign's self-validated re-application of the sequential rule.",
   r"the earlier-stop decisions rest on the calibration run's own re-application of the sequential rule, which only that run has checked.",
   "campaign's; self-validated")
ed("sec_joint.tex",
   r"The recovery is report-only: the primary decisions are those of the frozen evaluation, at the frozen $B$.",
   r"The recovery is for reporting only: the primary decisions are those of the evaluation before recovery, at the $B$ at which its rule stopped.",
   "report-only; frozen")
ed("sec_joint.tex",
   r"both with the frozen variant shifts and with the shifts",
   r"both with the variant shifts of the primary evaluation and with the shifts",
   "frozen")
ed("sec_joint.tex",
   r"and the frozen tests are re-evaluated against the frozen null distributions.",
   r"and the predeclared tests are re-evaluated against the null distributions used for the decisions.",
   "frozen")
ed("sec_joint.tex",
   r"the frozen decisions, with every claim $p$ value",
   r"the recorded decisions, with every claim $p$ value",
   "frozen")
ed("sec_joint.tex",
   r"from their frozen values,",
   r"from their recorded values,",
   "frozen")
ed("sec_joint.tex",
   r"These replays correct the two predictions to CH and re-evaluate their tests against the frozen null distributions.",
   r"This study corrects the two predictions to CH and re-evaluates their tests against the null distributions used for the decisions.",
   "replay; frozen")
ed("sec_joint.tex",
   r"run through the frozen conversion, flux-repair and binning chain,",
   r"run through the unchanged conversion, flux-repair and binning chain,",
   "frozen")
ed("sec_joint.tex", r"\paragraph{Replays.}", r"\paragraph{Re-evaluated tests.}", "replay")
ed("sec_joint.tex",
   r"Under the frozen metric, NuWro's total statistic",
   r"Under the predeclared metric, NuWro's total statistic",
   "frozen")
ed("sec_joint.tex",
   r"At its frozen Holm position (threshold 0.005)",
   r"At its original Holm position (threshold 0.005)",
   "frozen")
ed("sec_joint.tex",
   r"the report-only $\kappa=\jtMoneKappaRobust$ family",
   r"the $\kappa=\jtMoneKappaRobust$ family, which is for reporting only,",
   "report-only")
ed("sec_joint.tex",
   r"0.74 null standard deviations above its frozen boundary.",
   r"0.74 null standard deviations above its decision boundary.",
   "frozen")
ed("sec_joint.tex",
   r"both tests stay rejected at their frozen positions,",
   r"both tests stay rejected at their original Holm positions,",
   "frozen")
ed("sec_joint.tex",
   r"The GiBUU replay carries the label",
   r"The GiBUU re-evaluation carries the label required for it,",
   "replay", why="review B1: the label itself is protected (verbatim by ruling, BINDING-PHASE1-ADDENDUM-7 ruling 3)")
ed("sec_joint.tex",
   r": the sampling-closure check failed on the hydrogen sample, and a bias check of its premise, declared before it was computed, moves the CH prediction by about $5\times10^{-4}$ of $\sigma_{c}$, the standard deviation of the cell over the frozen null.",
   r": the sampling-closure check failed on the hydrogen sample, and a post hoc bias check of that check's premise, declared before it was computed, met its criterion of at most $0.1\,\sigma_{c}$: it moves the CH prediction by about $5\times10^{-4}$ of $\sigma_{c}$, the standard deviation of the cell over the null distribution used for the decisions.",
   "frozen; label explained", allow={"num"},
   why="review B1: restates the label's 0.1 criterion in words (the 0.1 acceptance is in mp3c/REPORT.md sec. 1)")
ed("sec_joint.tex",
   r"A further caveat applies to the GiBUU replay:",
   r"A further caveat applies to the GiBUU re-evaluation:",
   "replay")

# ---------------------------------------------------------------------------------------------------------------
# sec_fps.tex
ed("sec_fps.tex",
   r"\item \textbf{Anchor.} In the published sub-block,",
   r"\item \textbf{Published-region check.} In the published sub-block,",
   "anchor")
ed("sec_fps.tex",
   r"(MnvTune~v1, bare GENIE, and NuWro-shaped)",
   r"(MINERvA Tune~v1, bare GENIE, and NuWro-shaped)",
   "MnvTune")
ed("sec_fps.tex",
   r"This probes the statistical closure-toy stream, not the full band in use.",
   r"This probes the statistical closure-toy stream, not the full quoted band.",
   "in use")
ed("sec_fps.tex",
   r"(a)~anchor ratio in the published sub-block (median $1.0013$), (b)~MnvTune/bare-GENIE prior-swap ratio,",
   r"(a)~ratio to the control in the published sub-block (median $1.0013$), (b)~MINERvA Tune~v1/bare-GENIE prior-swap ratio,",
   "anchor; MnvTune", allow={"num"}, why="the 1 of 'Tune~v1'")
ed("sec_fps.tex",
   r"rather than the designated negative-weight footing (App.~\ref{app:negweight}), is",
   r"rather than the negative-weight treatment designated for the extended-fiducial analysis (App.~\ref{app:negweight}), is",
   "footing")
ed("sec_fps.tex",
   r"has not been constructed with selection-complete lateral support under the contract of \S\ref{sec:uq-combine}.",
   r"has not been constructed with re-selected lateral bands under the procedure of \S\ref{sec:uq-combine}.",
   "selection-complete; contract")

# ---------------------------------------------------------------------------------------------------------------
# sec_summary.tex (the release paragraph is protected)
ed("sec_summary.tex",
   r"The statistical band in use when the fixed-truth coverage test ran",
   r"The statistical band quoted when the fixed-truth coverage test ran",
   "in use")
ed("sec_summary.tex",
   r"tested truths; under an in-effect \SI{10}{\percent} signal-rate reduction the cause",
   r"tested truths; under a truth change that is in effect a \SI{10}{\percent} signal-rate reduction the cause",
   "in-effect")
ed("sec_summary.tex",
   r"The one five-axis covariance in use has an",
   r"The one five-axis covariance used in this note has an",
   "in use")
ed("sec_summary.tex",
   r"A selection-complete scalar five-dimensional covariance is in use although it has",
   r"A scalar five-dimensional covariance with re-selected lateral bands is used in this note although it has",
   "selection-complete; in use")

# ---------------------------------------------------------------------------------------------------------------
# app_guide.tex: the table of repository labels (no float, no caption, so no table number moves)
ed("app_guide.tex",
   r"arguments (App.~\ref{app:history}). These are reference material; a physics reading can skip them. \end{itemize}",
   "arguments (App.~\\ref{app:history}). These are reference material; a physics reading\n        can skip them.\n"
   "\\end{itemize}\n\n"
   "\\paragraph{Labels used in the repository.}\n"
   "The body describes each object in words. Where a repository label is needed to find the object, it is given once\n"
   "in parentheses at first use, or here.\n"
   "\\begin{center}\n\\small\n"
   "\\begin{tabular}{@{}p{0.27\\textwidth}p{0.67\\textwidth}@{}}\n\\toprule\n"
   "Label & Meaning in this note \\\\\n\\midrule\n"
   "\\texttt{lgbm}, \\texttt{exact}, \\texttt{hist} & the learner backends: LightGBM (the quoted central values and their\n"
   "  uncertainty ensembles; also the joint-test estimator), the scikit-learn exact-split estimator (the exact-split cross-check), and the scikit-learn histogram\n"
   "  estimator (\\S\\ref{sec:method-config}) \\\\\n"
   "\\texttt{purity}, \\texttt{negweight}, \\texttt{negweight-refined} & the values of the drivers' background-mode\n"
   "  option (\\texttt{-{}-bkg-mode}): purity-based subtraction, negative-weight injection, and refined negative-weight\n"
   "  subtraction\n"
   "  (\\S\\ref{sec:method-algo}, App.~\\ref{app:negweight}) \\\\\n"
   "\\texttt{cv}, \\texttt{mean} & the two variants of the five-axis covariance, with the unified-throw covariance\n"
   "  centered on the central value or on the throw mean; this note uses \\texttt{cv}\n"
   "  (\\S\\ref{sec:eavailw-construction}) \\\\\n"
   "\\texttt{MNV101\\_ACTIVE\\_UNIVERSE} & the event-loop mode that re-applies the selection with one lateral universe\n"
   "  active (``re-selected'' universes, \\S\\ref{sec:uq-higherdim}) \\\\\n"
   "July sweep, May sweep & the two productions of 2D systematic-universe re-unfolds; the quoted universe block uses\n"
   "  the July sweep (\\S\\ref{sec:uq-2d-construction}) \\\\\n"
   "J28 & the audit finding that the $N$-dimensional code divided every flux universe by the central-value flux;\n"
   "  ``flux-corrected'' and ``(J28)'' products are those repaired for it (App.~\\ref{app:negweight},\n"
   "  App.~\\ref{app:history}) \\\\\n"
   "VL170, VL172, VL175 & validation-ledger rows: the rebuilt 300-replica 2D statistical band, and the two earlier 2D\n"
   "  covariances built with it, before and after the flux-band repair; their values are kept in\n"
   "  App.~\\ref{app:history} \\\\\n"
   "\\bottomrule\n\\end{tabular}\n\\end{center}",
   "labels table (new)", allow={"num", "ref", "insert"},
   why="new table: moves repository labels out of the prose; adds numbers only inside labels (J28, VL170/172/175, "
       "MNV101) and pointers to the sections that use them")

# ---------------------------------------------------------------------------------------------------------------
# app_statmethods.tex
ed("app_statmethods.tex",
   r"(the superseded Stage-1 bootstrap, App.~\ref{app:history}). The Stage-2 bootstrap ($N=300 > 205$) is full-rank.",
   r"(the superseded 50-replica bootstrap, App.~\ref{app:history}). The 300-replica bootstrap ($N=300 > 205$) is full-rank.",
   "Stage-1/Stage-2", allow={"num"},
   why="review S7: the stage labels are replaced by the replica counts, N=50 and N=300 (app_history.tex:114-118)")
ed("app_statmethods.tex",
   r"Full $5$-iteration MEFHC \texttt{lgbm} unfolds (the backend",
   r"Full $5$-iteration ME~FHC LightGBM unfolds (the backend",
   "lgbm")
ed("app_statmethods.tex",
   r"The event loop dumps truth and reco weights per (band $B$, universe $u$); each $(B,u)$ is re-unfolded with a fixed seed against a matched CV job (same omnifile, backend, seed, iteration count and flux, so ML noise cancels);",
   r"The event loop writes truth and reco weights per (band $B$, universe $u$); each $(B,u)$ is re-unfolded with a fixed seed against a matched CV job (same event-loop output file, backend, seed, iteration count and flux, so ML noise cancels);",
   "dumps; omnifile")
ed("app_statmethods.tex",
   r"July sweep: $187$ universes, $44$ bands; rollup $43$ bands $+$ norm",
   r"July sweep: $187$ universes, $44$ bands; band sum $43$ bands $+$ norm",
   "rollup")
ed("app_statmethods.tex",
   r"(205 bins, MEFHC \texttt{lgbm}, seed~42)",
   r"(205 bins, ME~FHC LightGBM, seed~42)",
   "lgbm")
ed("app_statmethods.tex",
   r"the quoted rollup drops Rvp1pi (\texttt{KNOWN\_ISSUES.md} 92) and holds",
   r"the quoted band sum drops Rvp1pi (App.~\ref{app:provenance}, \texttt{rvp1pi}) and holds",
   "rollup; KNOWN_ISSUES", allow={"num", "ref"},
   why="tracker row 92 is App. G tag rvp1pi (app_provenance.tex, tracker table): same record, routed form")
ed("app_statmethods.tex",
   r"require selection-complete \texttt{MNV101\_ACTIVE\_UNIVERSE} event loops (weight-only bands: \S\ref{sec:uq-higherdim}); the quoted universe block takes those five from selection-complete re-unfolds.",
   r"require re-selected event loops, run with one universe active at a time (\texttt{MNV101\_ACTIVE\_UNIVERSE}; weight-only bands: \S\ref{sec:uq-higherdim}); the quoted universe block takes those five from re-unfolds of re-selected universes.",
   "selection-complete")
ed("app_statmethods.tex",
   r"its adopted five-axis use is in \S\ref{sec:eavailw-adopted}",
   r"its use in the five-axis covariance of this note is in \S\ref{sec:eavailw-adopted}",
   "adopt*")
ed("app_statmethods.tex",
   r"the lateral bands from selection-complete re-unfolds and Rvp1pi dropped)",
   r"the lateral bands from re-unfolds of re-selected universes and Rvp1pi dropped)",
   "selection-complete")
ed("app_statmethods.tex",
   r"That statement covers the $\pm1\sigma$ band estimator only. The adopted five-axis covariance deliberately retains",
   r"That statement covers the $\pm1\sigma$ band estimator only. The five-axis covariance used in this note deliberately retains",
   "adopt*")
ed("app_statmethods.tex",
   r"Our rollup was verified against MAT byte-for-byte:",
   r"Our band sum was verified against MAT byte-for-byte:",
   "rollup")
ed("app_statmethods.tex",
   r"comparing \texttt{MnvH1D::GetTotalErrorMatrix} with our \texttt{-{}-add-norm 0} rollup gives",
   r"comparing \texttt{MnvH1D::GetTotalErrorMatrix} with our band sum without the normalization band (\texttt{-{}-add-norm 0}) gives",
   "rollup")
ed("app_statmethods.tex",
   r"(\texttt{KNOWN\_ISSUES.md} 95). The quoted Flux band now uses them.",
   r"(App.~\ref{app:history-errata}). The quoted Flux band now uses them.",
   "KNOWN_ISSUES", allow={"num", "ref"},
   why="tracker row 95 is cited, with the struck values it caused, in the errata table of App. J (app_history.tex)")
ed("app_statmethods.tex",
   r"it is included in the headline but numerically negligible.",
   r"it is included in the quoted total but numerically negligible.",
   "headline")
ed("app_statmethods.tex",
   r"quote the blocks of the adopted covariance (\S\ref{sec:systematics}).",
   r"give the blocks of the quoted 2D covariance (\S\ref{sec:systematics}).",
   "adopt*", allow={"num"}, why="adds '2D' to say which covariance")
ed("app_statmethods.tex",
   r"tests whether the headline tension comes from the boundary",
   r"tests whether the main tension comes from the boundary",
   "headline")
ed("app_statmethods.tex",
   r"exact-split cross-check's $1.47$, against the earlier (VL172) covariance, alone is not evidence against them",
   r"exact-split cross-check's $1.47$, against an earlier covariance built before the flux-band repair, alone is not evidence against them",
   "VL id", allow={"num"},
   why="VL172 is the pre-flux-repair rollup (app_history.tex errata rows: 1.472 is the VL172 value; VL175 is the repair)")
ed("app_statmethods.tex",
   r"(paper TotalCov $+$ the adopted covariance of \S\ref{sec:systematics})",
   r"(paper TotalCov $+$ the quoted 2D covariance of \S\ref{sec:systematics})",
   "adopt*", allow={"num"}, why="adds '2D'")
ed("app_statmethods.tex",
   r"(VL175 $0.048$ and $0.406$; before the flux-constraint repair",
   r"(the earlier construction of App.~\ref{app:history-vl175}: $0.048$ and $0.406$; before the flux-constraint repair",
   "VL id", allow={"num", "ref"}, why="VL175 is the construction App. J.x (label app:history-vl175) is titled after")
ed("app_statmethods.tex",
   r"The split-bootstrap test of the earlier (VL170) bootstrap",
   r"The split-bootstrap test of the earlier rebuilt bootstrap",
   "VL id", allow={"num"}, why="VL170 is the rebuilt 300-replica band (app_provenance.tex, coverage-fixed-truth)")
ed("app_statmethods.tex",
   r"was run on the earlier (VL170) bootstrap;",
   r"was run on the earlier rebuilt bootstrap;",
   "VL id", allow={"num"}, why="as above")
ed("app_statmethods.tex",
   r"(not recomputed for the adopted covariance)",
   r"(not recomputed for the quoted covariance)",
   "adopt*")
ed("app_statmethods.tex",
   r"The 2D headline therefore retains the block sum, with the cross term diagnostic.",
   r"The quoted 2D covariance therefore remains the block sum, with the cross term as a diagnostic.",
   "headline")
ed("app_statmethods.tex",
   r"not a publication headline or validation statistic.",
   r"not a quoted result or validation statistic.",
   "headline")
ed("app_statmethods.tex",
   r"weighted as MAT weights it (\texttt{KNOWN\_ISSUES.md} 95; the",
   r"weighted as MAT weights it (App.~\ref{app:history-errata}; the",
   "KNOWN_ISSUES", allow={"num", "ref"}, why="as above")
ed("app_statmethods.tex",
   r"The per-band rollup is MAT-conformant,",
   r"The per-band sum is MAT-conformant,",
   "rollup")
ed("app_statmethods.tex",
   r"July sweep ($187$ universes; $43$ bands in the rollup),",
   r"July sweep ($187$ universes; $43$ bands in the band sum),",
   "rollup")
ed("app_statmethods.tex",
   r"(for Q, rank $197$ above",
   r"(for the quoted covariance, rank $197$ above",
   "Q")
ed("app_statmethods.tex",
   r"exact-GBT, 5 iter (cross-check;",
   r"exact-split, 5 iter (cross-check;",
   "exact-GBT")
ed("app_statmethods.tex",
   r"carries a $\sim1$-unit band}: the exact-GBT cross-check",
   r"carries a $\sim1$-unit band}: the exact-split cross-check",
   "exact-GBT")
ed("app_statmethods.tex",
   r"ML noise (lgbm training-seed settings, $n=5$)",
   r"ML noise (LightGBM training-seed settings, $n=5$)",
   "lgbm")
ed("app_statmethods.tex",
   r"All use 1A lgbm 5-iteration unfolds.",
   r"All use playlist-1A LightGBM 5-iteration unfolds.",
   "lgbm")
ed("app_statmethods.tex",
   r"& lgbm training-seed settings, $5\times20$ replicas \\",
   r"& LightGBM training-seed settings, $5\times20$ replicas \\",
   "lgbm")

# ---------------------------------------------------------------------------------------------------------------
# app_statmethods_nd.tex
ed("app_statmethods_nd.tex",
   r"The pre-adoption standard-P4 5D candidate, distinct from adopted $C_Z$, has",
   r"An earlier 5D covariance from the standard production chain, built before $C_Z$ was chosen for use and distinct from it, has",
   "adopt*; standard-P4; candidate", allow={"num"}, why="the digit 4 of the production label P4 is dropped with the label")
ed("app_statmethods_nd.tex",
   r"since the 5D candidate, 4D projection and published 2D block differ in rank;",
   r"since that earlier 5D covariance, its 4D projection and the published 2D block differ in rank;",
   "candidate")
ed("app_statmethods_nd.tex",
   r"The superseded unified-throw 5D candidate has $N=160$,",
   r"The superseded unified-throw 5D covariance has $N=160$,",
   "candidate")
ed("app_statmethods_nd.tex",
   r"inverse actually adopted, once declaration (v) makes its operands exist.",
   r"inverse actually used, once declaration (v) has recorded the quantities the treatment needs.",
   "adopt*")
ed("app_statmethods_nd.tex",
   r"The frozen design defines containment",
   r"The predeclared design defines containment",
   "frozen")
ed("app_statmethods_nd.tex",
   r"Prefixes use only committed ranges reproducing the original receipt;",
   r"Prefixes use only committed ranges that reproduce the originally recorded values;",
   "receipt")
ed("app_statmethods_nd.tex",
   r"Any such benchmark would supplement the required scalar-5D uncertainty construction, not replace its adoption.",
   r"Any such benchmark would supplement the required scalar-5D uncertainty construction, not replace the decision to use it.",
   "adopt*")

# ---------------------------------------------------------------------------------------------------------------
# app_negweight.tex
ed("app_negweight.tex",
   r"No number here is a publication uncertainty product;",
   r"No number here is a quoted uncertainty;",
   "product")
ed("app_negweight.tex",
   r"subtraction, not uncertainty products.",
   r"subtraction, not quoted uncertainties.",
   "product")
ed("app_negweight.tex",
   r"The \texttt{hist} backend differs from both the \texttt{lgbm} estimator of the quoted 2D central value and its ensembles, and the \texttt{exact} cross-check (\S\ref{sec:method}).",
   r"This histogram backend (\texttt{hist}) differs from both the LightGBM estimator of the quoted 2D central value and its ensembles, and the exact-split cross-check (\S\ref{sec:method}).",
   "lgbm/exact/hist")
ed("app_negweight.tex",
   r"Raw signed weights destabilize an \emph{exact} (tree-boosted) classifier,",
   r"Raw signed weights destabilize an exact-split boosted-tree classifier,",
   "exact")
ed("app_negweight.tex",
   r"Unbinned subtraction reproduces the adopted binned correction wherever it is well determined.",
   r"Unbinned subtraction reproduces the binned correction used for the results wherever it is well determined.",
   "adopt*")
ed("app_negweight.tex",
   r"\subsection{Which footing each production chain stands on}",
   r"\subsection{Which background treatment each production chain uses}",
   "footing")
ed("app_negweight.tex",
   r"$18$ detector unfolds and $10$ active-lateral endpoint unfolds. Its footing is positively identified,",
   r"$18$ detector unfolds and $10$ endpoint unfolds of the re-selected lateral bands. Its background treatment is positively identified,",
   "active-lateral; footing")
ed("app_negweight.tex",
   r"Neither possible launcher passes \texttt{-{}-bkg-mode}; the driver defaults to \texttt{purity} and announces its mode only on negative-weight branches. The lateral logs contain the purity branch's signature line and no mode announcement. The flag and announcements predate the files, making that absence informative without a version gap. Current production pins the footing in a configuration object that rejects every other mode",
   r"Neither of the two possible job scripts sets the driver's background-mode option (\texttt{-{}-bkg-mode}); the driver defaults to purity and announces its mode only on its negative-weight code paths. The logs of the lateral-band unfolds contain the purity code path's signature line and no mode announcement. The option and announcements predate the files, making that absence informative without a version gap. Current production fixes the background treatment in a configuration object that rejects every other mode",
   "launcher; --bkg-mode; branch; footing")
ed("app_negweight.tex",
   r"The canonical launcher passes \texttt{-{}-bkg-mode} explicitly from that pinned configuration rather than inheriting the default, and the value is stamped into every endpoint receipt as it is written. Asserting the previous default changes provenance without changing physics. Its effect is that a future component's footing is provable from the component instead of from the absence of a flag.",
   r"The standard job script passes the option explicitly from that configuration rather than inheriting the default, and the value is written into the record of every endpoint unfold as it is produced. Stating the previous default explicitly changes the provenance without changing the physics. Its effect is that a future component's background treatment is provable from the component instead of from the absence of an option.",
   "launcher; --bkg-mode; receipt; footing")
ed("app_negweight.tex",
   r"First, mixing footings inside one covariance is worse than either consistent choice: dropping a negative-weight-footed lateral block into a purity-footed central and vertical set is a footing mismatch, not an upgrade. Second, switching required rerunning every unfold above and would have invalidated the flux-corrected (J28) covariance adopted immediately beforehand.",
   r"First, mixing background treatments inside one covariance is worse than either consistent choice: inserting a lateral-band block built with negative-weight subtraction into a central and vertical set built with purity subtraction is a mismatch, not an upgrade. Second, switching required rerunning every unfold above and would have invalidated the flux-corrected covariance (corrected for audit finding J28) chosen for use immediately beforehand.",
   "footing; J28; adopt*")
ed("app_negweight.tex",
   r"obligation to revisit the footing before submission. It is recorded as such, and nothing in this subsection discharges it.",
   r"obligation to revisit the background treatment before submission. It is recorded as such, and nothing in this subsection meets that obligation.",
   "footing; discharge")
ed("app_negweight.tex",
   r"It comes from the FPS ME~FHC battery of 2026-06-10, before the negative-weight driver.",
   r"It comes from the extended-fiducial ME~FHC battery of 2026-06-10, run before the driver supported negative-weight subtraction.",
   "FPS")
ed("app_negweight.tex",
   r"Negweight-refined FPS production has not run. The ledger-verified central value from that gated battery remains",
   r"No extended-fiducial production with refined negative-weight subtraction has been run. The central value from that battery, recorded in the validation ledger with its passed published-region check against the control, remains",
   "negweight-refined; FPS; ledger; gated",
   why="review S8: the battery's gate is the ledger's 'anchor gate PASS' (VALIDATION_LEDGER.md:1611-1612), the published-region check of sec:fps")
ed("app_negweight.tex",
   r"\paragraph{The published pair has different footings.} The extended-fiducial lane designates negative-weight injection with Stay-Positive refinement as its publication footing. Code pins it (App.~\ref{app:provenance}, \texttt{bkg-mode-pins}) and a gate fails closed if any endpoint's recorded mode differs or is missing.",
   r"\paragraph{The extended-fiducial measurement and its control are designated different background treatments.} The extended-fiducial analysis designates negative-weight injection with Stay-Positive refinement as its background treatment for publication. The code fixes it (App.~\ref{app:provenance}, \texttt{bkg-mode-pins}), and a check stops the run if any endpoint's recorded mode differs or is missing.",
   "footing; lane; gate")
ed("app_negweight.tex",
   r"We claim internally consistent footings for each side of the measurement and matched-control pair.",
   r"We claim an internally consistent background treatment for each side of the measurement and matched-control pair.",
   "footing")
ed("app_negweight.tex",
   r"\subsection{Measured size of the footing choice and its scope}",
   r"\subsection{Measured size of the background-treatment choice and its scope}",
   "footing")
ed("app_negweight.tex",
   r"At full statistics with the adopted estimator on 2D ME~FHC, the covariance difference is one to two percent.",
   r"At full statistics with LightGBM, the estimator of the quoted 2D central value, on 2D ME~FHC, the covariance difference is one to two percent.",
   "adopt*", allow={"num"},
   why="review S10/Q1: the covariance ratios are the Phase D lgbm runs (values.tex:375); '2D' is repeated in the apposition")
ed("app_negweight.tex",
   r"Real-data totals agree to \SI{\nwPctTot}{\percent},",
   r"Real-data totals (histogram backend) agree to \SI{\nwPctTot}{\percent},",
   "backend attribution",
   why="review S10: the totals are the hist runs (values.tex:363-364, nwSigPur/nwSigNeg '(hist)')")
ed("app_negweight.tex",
   r"Switching footing produces a measured net per-universe displacement",
   r"Switching background treatment produces a measured net per-universe displacement",
   "footing")
ed("app_negweight.tex",
   r"It is not a theorem that the two footings give the same covariance,",
   r"It is not a theorem that the two background treatments give the same covariance,",
   "footing")
ed("app_negweight.tex",
   r"There is no full five-dimensional $187$-universe both-footing comparison at the publication configuration ($5$ iterations, \texttt{lgbm}). The spot check uses one iteration and \texttt{hist} on the on-disk five-dimensional universe file. Under both footings",
   r"There is no full five-dimensional $187$-universe comparison of the two background treatments at the publication configuration ($5$ iterations, LightGBM). The spot check uses one iteration and the histogram backend on the stored five-dimensional universe file. Under both treatments",
   "footing; lgbm/hist")
ed("app_negweight.tex",
   r"this supports quoting the standard chain on purity and stating its footing. It does not support calling footing irrelevant in five dimensions;",
   r"this supports quoting the standard chain with purity subtraction and stating its background treatment. It does not support calling the background treatment irrelevant in five dimensions;",
   "footing")
ed("app_negweight.tex",
   r"Raw negative weights destabilize \texttt{exact} (\S\ref{sec:negweight-estimator}), while the standard chain uses \texttt{lgbm}. Neither footing risks that pathology here,",
   r"Raw negative weights destabilize the exact-split backend (\S\ref{sec:negweight-estimator}), while the standard chain uses LightGBM. Neither treatment risks that pathology here,",
   "exact/lgbm; footing")
ed("app_negweight.tex",
   r"\subsection{Five-dimensional pseudo-experiments on both footings}",
   r"\subsection{Five-dimensional pseudo-experiments with both background treatments}",
   "footing")
ed("app_negweight.tex",
   r"reports end-to-end tests of both footings: purity bias in the highest-$W$ column at nominal truth, its reduction with \texttt{negweight-refined}, the data difference, and the refinement-capacity candidate, which is not adopted.",
   r"reports end-to-end tests of both background treatments: purity bias in the highest-$W$ column at nominal truth, its reduction with refined negative-weight subtraction, the data difference, and the estimator with higher refinement capacity, which is not used for the quoted central values.",
   "footing; negweight-refined; candidate; adopt*",
   why="the raised-capacity configuration is the joint-test estimator's (Table estimators-matrix, row e), so it IS "
       "used for the generator tests; 'not adopted' therefore means not used for the quoted central values")
ed("app_negweight.tex",
   r"It is direct evidence for the obligation in \S\ref{sec:negweight-footing} to revisit footing before submission. Comparing five-dimensional purity with \texttt{negweight-refined} on data",
   r"It is direct evidence for the obligation in \S\ref{sec:negweight-footing} to revisit the background treatment before submission. Comparing five-dimensional purity with refined negative-weight subtraction on data",
   "footing; negweight-refined")
ed("app_negweight.tex",
   r"\paragraph{Refined footing.}",
   r"\paragraph{Refined negative-weight subtraction.}",
   "footing")
ed("app_negweight.tex",
   r"With either footing, the estimator does not follow",
   r"With either treatment, the estimator does not follow",
   "footing")
ed("app_negweight.tex",
   r"The footing obligation therefore remains open;",
   r"The obligation to revisit the background treatment therefore remains open;",
   "footing")
ed("app_negweight.tex",
   r"Stay-Positive classifier underfitting causes the refined footing's residual nominal bias.",
   r"Stay-Positive classifier underfitting causes the residual nominal bias of the refined subtraction.",
   "footing")
ed("app_negweight.tex",
   r"\paragraph{The footing was chosen, not discharged; the adoption gate is separate.} Nothing here adopts any five-dimensional covariance. The selection-complete active-lateral component is built, with five bands and ten endpoint unfolds carrying distinct digests bound in the adopted product's receipt. One five-axis covariance is adopted under a digest-bound exception (\S\ref{sec:eavailw-adopted}). Neither fact follows from or is needed by this appendix. Footing choice and adoption are independent; the choice removes one blocking decision while leaving every other component precondition intact",
   r"\paragraph{Background treatment chosen, its obligation not yet met; covariance choice separate.} Nothing here selects any five-dimensional covariance for use. The lateral-band component from re-selected event loops is built, with five bands and ten endpoint unfolds whose distinct checksums are listed in the record of the product used in this note. One five-axis covariance is used in this note under an exception limited to the file with its checksum (\S\ref{sec:eavailw-adopted}). Neither fact follows from or is needed by this appendix. The choice of background treatment and the choice of covariance are independent; the former removes one blocking decision and leaves every other precondition for using a component in place",
   "footing; discharged; adoption gate; adopt*; selection-complete; active-lateral; digest; receipt")

# ---------------------------------------------------------------------------------------------------------------
# app_response_mismatch.tex
ed("app_response_mismatch.tex",
   r"\paragraph{Record-only test implemented in the pipeline.}",
   r"\paragraph{Reconstruction-only test implemented in the pipeline.}",
   "record-only")
ed("app_response_mismatch.tex",
   r"The implementation refuses real-data mode, truth reweighting, bootstrapping, or a non-five-dimensional axis list, and marks every output \texttt{NONQUOTABLE-DIAGNOSTIC}.",
   r"The implementation refuses to run on real data, with truth reweighting, with bootstrapping, or with any axis list other than the five observables, and labels every output as a diagnostic that must not be quoted.",
   "NONQUOTABLE")
ed("app_response_mismatch.tex",
   r"The record-only arm is intentionally cheap",
   r"The reconstruction-only arm is intentionally cheap",
   "record-only")
ed("app_response_mismatch.tex",
   r"unless the record-only test shows material bias",
   r"unless the reconstruction-only test shows material bias",
   "record-only")
ed("app_response_mismatch.tex",
   r"response-mismatch artifact has been produced or pass threshold adopted. The test leaves the frozen central value and current covariance construction unchanged.",
   r"response-mismatch output has been produced and no pass threshold has been set. The test leaves the quoted central value and the current covariance construction unchanged.",
   "adopt*; frozen")

# ---------------------------------------------------------------------------------------------------------------
# Comment-only edits. They print nothing, so they carry no ledger row; they exist because swallowed_text.py flags a
# phrase that printed in the base and now survives only in a comment. Asserted the same way (exactly one match).
COMMENT_EDITS = [
    ("sec_systematics.tex",
     '% "the statistical band in use when it ran", as in sec:coverage.',
     '% "the statistical band quoted when it ran", as in sec:coverage (batch-0 glossary: "in use" became "quoted").'),
]

NEG = re.compile(r"\b(?:not|no|nor|neither|never|cannot|without|none|nothing|unmeasured|undetermined)\b|n't", re.I)
NUM = re.compile(r"\d+(?:\.\d+)?")
REF = re.compile(r"\\(?:ref|eqref|cite|pageref)\{([^{}]*)\}")
LABELARG = re.compile(r"\\(?:ref|eqref|cite|label|pageref)\{[^{}]*\}")


def value_macros(wt: Path) -> set[str]:
    names = set()
    for f in ("values.tex", "values_inference.tex"):
        src = subprocess.run(["git", "-C", str(wt), "show", f"{BASE}:{NOTE}/{f}"], capture_output=True, text=True,
                             check=True).stdout
        names |= set(re.findall(r"\\newcommand\{?\\([A-Za-z]+)\}?", src))
    return names


def macros(s: str, names: set[str]) -> collections.Counter:
    return collections.Counter(m for m in re.findall(r"\\([A-Za-z]+)", s) if m in names)


def flex(old: str) -> re.Pattern:
    return re.compile(r"\s+".join(re.escape(t) for t in old.split()))


B3_LABEL = ("``B3 (sampling closure) failed on hydrogen; a\n"
            "post-hoc bias check of its premise passed at $\\le0.1\\,\\sigma_{c}$''")


def protected_spans(name: str, text: str) -> list[tuple[int, int]]:
    spans = []
    if name == "sec_joint.tex":
        a, b = text.index("\\begin{quote}"), text.index("\\end{quote}")
        spans.append((a, b))
    if name == "sec_joint.tex":  # review B1: the GiBUU label is verbatim by ruling (BINDING-PHASE1-ADDENDUM-7 ruling 3)
        a = text.find(B3_LABEL)
        # if an earlier edit already broke the label, the whole file counts as protected so the next edit fails loudly
        spans.append((a, a + len(B3_LABEL)) if a >= 0 else (0, len(text)))
    if name == "sec_summary.tex":
        spans.append((text.index("\\paragraph{Reusing the unbinned result.}"), len(text)))
    if name == "main_note.tex":
        a, b = text.index("\\begin{abstract}"), text.index("\\end{abstract}")
        spans += [(0, a), (b, len(text))]
    return spans


def collapse(s: str) -> str:
    s = "\n".join(re.sub(r"(?<!\\)%.*", "", l) for l in s.splitlines())
    return re.sub(r"\s+", " ", s).strip()


def md(s: str) -> str:
    return s.replace("|", "\\|")


def main(argv: list[str]) -> int:
    wt = Path(argv[1]).resolve()
    dry = "--dry-run" in argv
    names = value_macros(wt)
    base, cur = {}, {}
    errors = []
    rows = []
    for i, e in enumerate(E, 1):
        f = e["file"]
        if f not in base:
            base[f] = subprocess.run(["git", "-C", str(wt), "show", f"{BASE}:{NOTE}/{f}"], capture_output=True,
                                     text=True, check=True).stdout
            cur[f] = base[f]
        old, new, allow = e["old"], e["new"], e["allow"]
        rx = flex(old)
        hits = list(rx.finditer(cur[f]))
        if len(hits) != 1:
            errors.append(f"E{i} {f}: old text matches {len(hits)} times: {old[:90]!r}")
            continue
        m = hits[0]
        bh = list(rx.finditer(base[f]))
        line = base[f].count("\n", 0, bh[0].start()) + 1 if len(bh) == 1 else "?"
        for a, b in protected_spans(f, cur[f]):
            if m.start() < b and m.end() > a:
                errors.append(f"E{i} {f}: edit touches a protected span")
        if "insert" not in allow and collapse(old) in collapse(new):
            errors.append(f"E{i} {f}: old text is a substring of new text")
        o2, n2 = LABELARG.sub(" ", old), LABELARG.sub(" ", new)
        if "num" not in allow and collections.Counter(NUM.findall(o2)) != collections.Counter(NUM.findall(n2)):
            errors.append(f"E{i} {f}: numbers changed {sorted(NUM.findall(o2))} -> {sorted(NUM.findall(n2))}")
        if "ref" not in allow and collections.Counter(REF.findall(old)) != collections.Counter(REF.findall(new)):
            errors.append(f"E{i} {f}: refs changed {REF.findall(old)} -> {REF.findall(new)}")
        if macros(old, names) != macros(new, names):
            errors.append(f"E{i} {f}: value macros changed {macros(old, names)} -> {macros(new, names)}")
        if "neg" not in allow and len(NEG.findall(new)) < len(NEG.findall(old)):
            errors.append(f"E{i} {f}: negations decreased {NEG.findall(old)} -> {NEG.findall(new)}")
        cur[f] = cur[f][:m.start()] + new + cur[f][m.end():]
        rows.append((f"G{i:03d}", f"{f}:{line}", e["terms"], collapse(old), collapse(new), f, e["why"],
                     "insert" in allow))
    for f, old, new in COMMENT_EDITS:
        n = cur[f].count(old)
        if n != 1:
            errors.append(f"comment edit {f}: matches {n} times: {old!r}")
        elif not old.lstrip().startswith("%") or not new.lstrip().startswith("%") or "\n" in old + new:
            errors.append(f"comment edit {f}: not a single comment line")
        else:
            cur[f] = cur[f].replace(old, new)
    if errors:
        print("APPLY :: FAIL")
        for x in errors:
            print("  " + x)
        return 1
    # every after-probe must be unique enough to be found, and every before-probe gone, in the final text
    for rid, loc, terms, before, after, f, why, ins in rows:
        final = collapse(cur[f])
        if after not in final:
            errors.append(f"{rid} {loc}: after text not in final file (a later edit overwrote it?)")
        if not ins and before in final:
            errors.append(f"{rid} {loc}: before text still prints")
    if "sec_joint.tex" in cur and (cur["sec_joint.tex"].count(B3_LABEL) != 1 or base["sec_joint.tex"].count(B3_LABEL) != 1):
        errors.append("sec_joint.tex: the verbatim B3 label is not present byte for byte, exactly once, as in the base")
    if errors:
        print("APPLY :: FAIL (post-check)")
        for x in errors:
            print("  " + x)
        return 1
    if not dry:
        for f, text in cur.items():
            (wt / NOTE / f).write_text(text)
        led = HERE / "ledger.md"
        out = ["# Fact ledger, batch 0 (glossary): note at origin/main 38a53a53 -> worktree `wt-note1`", "",
               "One row per changed sentence, generated by `apply_glossary.py` from its edit list. `file:line` is the",
               "line in the base file where the changed text starts. Probes: `N:<file>::<text>` must occur in the",
               "comment-stripped, whitespace-collapsed printed text of that note file after the edit; `X:<file>::<text>`",
               "must no longer occur. `check_ledger.py <worktree> ledger.md` runs every probe. The meaning of each row",
               "(nothing lost, nothing strengthened, status kept) was checked by reading; the `note` column gives the",
               "reasoning where the rewording is not a one-for-one term swap.", "",
               "| id | file:line | terms | before | after | probe | note |", "|---|---|---|---|---|---|---|"]
        for rid, loc, terms, before, after, f, why, ins in rows:
            probe = f"`N:{f}::{after}`" + ("" if ins else f" && `X:{f}::{before}`")
            out.append(f"| {rid} | {loc} | {md(terms)} | {md(before)} | {md(after)} | {md(probe)} | {md(why)} |")
        led.write_text("\n".join(out) + "\n")
    print(f"APPLY :: PASS ({len(rows)} edits and {len(COMMENT_EDITS)} comment-only edit(s) in {len(cur)} files{'; dry run, nothing written' if dry else ''})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
