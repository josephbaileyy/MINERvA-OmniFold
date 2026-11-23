# Cutdown, methods-study framing renames: log

**Under** Joseph's decision of 2026-11-16 (DECISION-20261116-joseph-paper-batch.md at main `99aefd3f0`, sixth answer,
item 29: "Framing: a methods study. This decides OI-205") and the editor's brief, which assigns the framing renames to
this branch.

**What is renamed.** Where the note called one of its own outputs a "measurement", the word becomes "result" (or,
for the act, "the data unfolding" / "the unfolding"). The published MINERvA measurement keeps the word. No number,
claim or limit changes; each row replaces one phrase and nothing else on its line. Line numbers are those of the
tree just before the renames (after this branch's cuts); the base is `8342963c1`.

| id | file:line | old | new |
|---|---|---|---|
| R1 | app_negweight.tex:4 | `Its agreement with the binned correction is quantified on the 2D measurement below.` | `Its agreement with the binned correction is quantified on the 2D result below.` |
| R2 | app_negweight.tex:68 | `\subsection{Comparison on the 2D measurement}` | `\subsection{Comparison on the 2D result}` |
| R3 | app_statmethods.tex:39 | `describes the measurement's block construction` | `describes the result's block construction` |
| R4 | app_statmethods.tex:82 | `\caption{Variance-source procedures for the 2D measurement (` | `\caption{Variance-source procedures for the 2D result (` |
| R5 | sec_3d.tex:4 | `We extend the measurement to $d^{3}\sigma` | `We extend the unfolding to $d^{3}\sigma` |
| R6 | sec_3d.tex:79 | `the 1D projection of the 3D measurement.` | `the 1D projection of the 3D result.` |
| R7 | sec_3d.tex:83 | `\subsection{Validation against the 2D measurement}` | `\subsection{Validation against the 2D result}` |
| R8 | sec_5d.tex:52 | `rebuild per-bin purity weights as in the measurement.` | `rebuild per-bin purity weights as in the data unfolding.` |
| R9 | sec_method.tex:182 | `so closure exercises the same code path as the measurement.` | `so closure exercises the same code path as the data unfolding.` |
| R10 | sec_method.tex:221 | `or coverage for this measurement.` | `or coverage for this result.` |
| R11 | sec_results.tex:32 | `the sum of the published covariance and that of this measurement.` | `the sum of the published covariance and that of this result.` |
| R12 | sec_results.tex:35 | `With the covariance of this measurement alone,` | `With the covariance of this result alone,` |
| R13 | sec_results.tex:58 | `\caption{Agreement of this measurement with the published measurement` | `\caption{Agreement of this result with the published measurement` |
| R14 | sec_results.tex:168 | `with both the published data and this measurement.` | `with both the published data and this result.` |
| R15 | sec_results.tex:168 | `and $31.3$ for this measurement (` | `and $31.3$ for this result (` |
| R16 | sec_results.tex:173 | `\caption{Projections of this measurement (red circles)` | `\caption{Projections of this result (red circles)` |
| R17 | sec_systematics.tex:310 | `model completeness for the $\Eavail$ and $W$ measurement.` | `model completeness for the $\Eavail$ and $W$ results.` |
| R18 | sec_validation.tex:1 | `\section{Validation of the two-dimensional measurement}` | `\section{Validation of the two-dimensional result}` |

**Re-pin:** records-move-ledger.md row L-thin-C18 pinned the caption of R4 by its text; its N: probe now reads the
renamed caption. Context only.

**Left as they are, on purpose.**
- "the measurement phase space", "the published measurement", "MINERvA measurement-dimensionality survey": they refer
  to the published measurement or its signal definition.
- "Publication as a measurement remains unresolved" and "Whether it is ready for publication as a measurement has
  not been established" (executive summary): statements about a measurement claim that is not made.
- "neither a covariance nor a physical measurement", "excludes a physical measurement", "Neither tier is a completed
  measurement", "not a measured cross section": negations.
- "Reporting definitions for a five-dimensional measurement" (§9.4) and "that a measurement would require" (App. B):
  they describe what a measurement would need, which is their point.
- "Four measurements limit what the covariance supports" (§9.6) and App. G's "Limiting measurements": measurements of
  a sensitivity, not of a cross section.
- "Identified after the measurement, these 52 cells …" (§4.6): a statement of timing; "result" does not fit the
  sentence, and rewording it is not a rename.
- Section titles "Results" and "Comparison to the published measurement".
