# b1 notes (Secs. I, II, III): choices a reviewer should know

Revised after the reviewer's ADOPT-AFTER-FIXES verdict. All the requested fixes are applied (listed at the end).

## Reordering and merges

- **Sec. II ¶2 (the observables).** The truth-level sentence now also gives the muon momentum components. The
  $q_3$ and $W$ definitions are one sentence, and the available energy is introduced as "We define the available
  energy as" Eq. (1), so the paragraph no longer runs five "The X is" sentences. After the equation sentence, the
  order is: the 135 MeV constant ("This constant is inherited ..."), its consistent use, the sums, and then "All
  other final-state particles ...". I moved "This constant" up so that it follows the equation.
- **Sec. III, paragraph order.** I moved outline ¶5 (the estimators and the Table I pointer) ahead of ¶4 (shared
  settings), so that "Both estimators use five OmniFold iterations" follows their introduction (R9). ¶3 (F096,
  trained on the full sample) closes the settings paragraph. ¶6 stays its own paragraph, followed by Table I.
- **Sec. III A.** ¶1 and ¶2 are merged, so the note pointer (F124) closes the paragraph (R7).

## Ruled on

- **"We call this requirement the support rule."** (Sec. II ¶5) The director kept it. The note defines one support
  rule: expected reconstructed signal and selected truth weight both at least 1000
  (app_statmethods_nd.tex, `sec:gbdt-diagnostic-definitions`), and the code's `SUPPORT_MIN = 1000` is the same
  threshold.

## Wording chosen to fit an atom

- F011: I wrote "has been demonstrated on a public simulated T2K near-detector sample", without the fact column's
  "only". F012 (measurements on data reach three dimensions) carries the contrast.
- F024: "are reported for the sixteen-cell result in Secs. ...", because `sec:fd16` lies in Sec. IV.
- F042: "The analysis uses $4.12$ million selected data events."
- F075: "Unlike the analysis definitions, ...". The contrast rests on F052 (struck-nucleon mass) and F066 (fixed
  beam axis).
- F094 (reviewer fix 7): the row is now two sentences, "... $D(x)-B(x)$ pointwise." and "A classifier refinement
  ... before the first iteration." Its `after` therefore spans those two consecutive sentences, which the checker
  reports by name. That is the only two-sentence `after` in b1.
- F103 and reviewer fix 10: LightGBM is first named inside the F103 atom ("uses LightGBM at seed~42"), so the
  citation follows the atom: "uses LightGBM at seed~42~\cite{Ke:2017lightgbm} with ...". The later
  `\cite{Pedregosa:2011sklearn,Ke:2017lightgbm}` stays, because the F097 atom contains it.
- F130: its atom begins lowercase, so it follows an opener: "In forming the cells, each supported box ...".

## Atom-forced deviations from the APS conventions (accepted by the director: atoms win)

- No serial comma: F027 "the data, the simulation and the observables"; F129 "$\pPar$ \fvval{h2-mid-pz} and $q_3$
  ...".
- British spelling: "neighbour" (F130).
- Numerals and spelled-out counts as the atoms give them: "16 cells" (F127) beside "sixteen cells" elsewhere;
  "twenty-four $Z$+jets observables" (F009); "7 $\Eavail$, 7 $q_{3}$, and 6 $W$ bins" (F080).
- A semicolon inside an atom: F083 "\jtNcells{} pass; these are the joint cells". It joins a count to a
  definition, not a result to a caveat.
- F025 (Scope) prints verbatim, because it is probed verbatim. R1's positive rewrite of the scope is therefore not
  possible.
- Repeats required by the rows: F019 and F061 (reconstructed $W$ is fixed by the other three), and F026 and F029
  (pointers to `sec:limitations`).
- More note pointers than R7's "about one per subsection": three in Sec. II, five in Sec. III, and one in III A.
  Each is a row.

## Floats and structure

- Table I is copied from F111–F116, with the caption, then the label, then the tabular. On `\centering\scriptsize`:
  the ledger does not show it. F111's base text is `\begin{table}[tb] \caption{Estimators.`, with nothing between
  the two, and F115's base text is cut at 60 characters before the tabular. I left it for assembly, as instructed.
- Eq. (1) is F053 verbatim, in an `equation` environment, with `\label{eq:eavail}`.
- Registry, for the director: the F105 phrase and the F116 row text print verbatim, but their line numbers will
  differ from the ALIASES/ATTRIBUTION citations.

## Reviewer fixes applied

| fix | where now |
|---|---|
| BLOCKER, envelope sentence | "To include model dependence, a dedicated study defines the envelope of a cell as ..., and adds it linearly to the probabilistic half-width." Later uses of "the study" (F121, F124) refer back to it. |
| MAJOR, estimator qualifier | "... into 27 cells, the same estimator's envelope alone does not exceed it, ..." |
| 1 | "on assessing the bias and uncertainty of the unfolding procedure" |
| 2 | "... as an end-to-end test of the unfolding, and we also give three- and four-observable central values." |
| 3 | "The data come from the twelve ... run periods, corresponding to $1.057\times10^{21}$ protons on target, with an average neutrino energy near \SI{6}{GeV}~\cite{MINERvA:2021owq}." The F033 atom keeps "with an average neutrino energy near" as the separate clause. |
| 4 | "tracker fiducial volume ($5980<z<\SI{8422}{mm}$, inside a hexagon of apothem \SI{850}{mm})" |
| 5 | $q_3$ and $W$ in one sentence; see Reordering above |
| 6 | "This constant is inherited ...", moved to follow the equation sentence |
| 7 | F094 split as given |
| 8, 9 | "This estimator removes most of the bias ... (Sec.~\ref{sec:validation}), and the note's simulation-calibrated tests use the same estimator." |
| 10 | `\cite{Ke:2017lightgbm}` at the first naming (see F103 above) |
| 11 | Caption: "the refinement classifier of the two-observable estimator is seeded at the estimator seed plus three" |

## Checks

`check_batch.py b1 --build` (in this directory, run with `python3 -I -B`) rebuilds `b1-ledger.md` and runs checks
(a)–(d). It replaces `check_b1.py`. The checks are the same, extended to b2, and the GATE count now also uses an
any-value pattern. A smoke compile of b1 and b2 in a minimal two-column `article` driver exits 0. Its only overfull
boxes are in the verbatim floats.
