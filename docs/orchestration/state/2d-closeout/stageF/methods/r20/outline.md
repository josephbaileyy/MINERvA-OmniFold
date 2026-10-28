# Register round r20, the paper's fourth and last: outline (2026-10-28)

**Status:** for the director's approval. Nothing is written.

**Under:**
- `DECISION-20261025-joseph-register-rounds-paper-rewrite.md`. This is round 4 of 4; after r20 the paper's register
  rounds are closed whatever P1 gives.
- The director's authorization of 2026-10-28:
  - targets only;
  - no section, label, table or figure change;
  - the (c) sentences byte-identical (the flux band, and the Sec. I limitations paragraph with its 1A slot);
  - Data Availability protected.

**Base:** #413 at `5841adce`, which is r19 as measured (`a1702535`) plus agy-b4's Q2 wording fix.

**Baseline copy for the pairwise:** r19's measured copy, `a1702535`, sha256 `76c6bfa3…`, 7,404 words. It differs from the
base only in that one sentence.

**Method, unchanged from r19:**
- one edit script;
- the r19 ledger and checker, extended (base `5841adce`);
- a scope guard for each changed scope sentence, with a planted strengthening;
- an independent two-direction review;
- agy with a control;
- pairwise in both orders with both models;
- P1 sol2 ×3.

The raters' own rewrites (`r19/measure/P1__r*`) are not fact-checked and are not applied. The drafts below are this
lane's, checked against the paper, the note and the KEEP list.

## The targets

| # | where | quoted in | now | proposed | facts kept | guards |
|---|---|---|---|---|---|---|
| R1 | Sec. III, the five-iteration sentence | 3 of 3 | "The joint-test estimator keeps five iterations because 10, 15, or 20 iterations did not reduce its model dependence, measured as the largest residual proxy over the truth changes used in its development. The comparison and its values are given in \nsec{sec:gbdt-model-dependence}." | "Ten, 15 or 20 iterations did not reduce the joint-test estimator's model dependence, measured as the largest residual proxy over the truth changes used in its development, so it keeps five (\nsec{sec:gbdt-model-dependence})." | the three alternatives; "did not reduce"; the metric; "the truth changes used in its development"; the pointer | new: "did not reduce" (plant "reduced") |
| R2 | VI A, the Limitations lead | 2 of 3 | "The limitations of these results are stated with the results they qualify, in Secs. III–V, and those of the calibrated tests in the companion note. The principal ones are these." | "The principal limitations, each stated in full with the result it qualifies (Secs. III–V; for the calibrated tests, the companion note), are these." | where each is stated; that this paragraph summarizes the principal ones (r18 S7) | B3-K14's probe re-pointed |
| R3 | Sec. I, the scope paragraph's first sentence | 1 of 3 | "\emph{Scope.} The findings are those of one OmniFold implementation on one data set, for the observables, configurations, and deformations tested, rather than of multidimensional OmniFold in general." | "\emph{Scope.} The findings apply to the OmniFold implementation, data set, observables, configurations and deformations studied here, not to multidimensional OmniFold in general." | the five scopes; "not to multidimensional OmniFold in general" (KEEP: the raters' form drops it) | G3 re-pointed: plant "not to multidimensional OmniFold in general" ⇒ "and to multidimensional OmniFold in general" |
| R4 | IV E, the binned-diagnostic first sentence | 1 of 3 | "In a binned, signal-only and noise-free diagnostic on the 109 joint cells and the truth changes used to develop the estimator, with the detector response fixed at the simulation's, an exact binned iterative unfolding with five iterations leaves about the same median residual as the boosted-tree estimator. It covers only …" | "An exact binned iterative unfolding with five iterations leaves about the same median residual as the boosted-tree estimator in a binned, signal-only and noise-free diagnostic on the \jtNcells{} joint cells and the truth changes used to develop the estimator, at the simulation's detector response. The diagnostic covers only …" | the result first (R4 form), then its scope; every KEEP qualifier; the rest of the paragraph, the out-of-scope sentence included (DECISION-20261023 item 3b), byte-identical | new: "binned, signal-only and noise-free" (plant: dropped); G22 unchanged |
| R5 | IV H, the listing rule | 1 of 3 | "A truth is listed when $p<…$ or when a cell has $\|z\|>…$. Table~\ref{tab:fd16} gives the results under the reported covariance and under $C_{\mathrm{total}}$ alone; … further truths are ungraded and given in the note." | "The bias at a truth is listed when $p<…$ or when a cell has $\|z\|>…$. Table~\ref{tab:fd16} gives the results under the reported covariance and under $C_{\mathrm{total}}$ alone. The note gives … further, ungraded truths." | the rule (the readout's trigger: P(χ²₁₆ > χ²) < p or a cell with \|z\| > z); the table's two covariances; the ungraded truths. "Listed" stays, as ¶297 uses it (Joseph's wording) | none new (no scope word) |
| R6 | VI, the note's-tests sentence | 1 of 3 | "The note's calibrated tests show the same pull: their null distributions for the external predictions are displaced upward by it, as the calibration reproduces (\nsec{sec:joint5d-results})." | "In the note's calibrated tests, the same pull displaces the null distributions of the external predictions upward, and the calibration reproduces it (\nsec{sec:joint5d-results})." | displaced upward; by the same pull; the calibration reproduces it (note: "the external nulls are displaced far upward by the estimator's pull toward its prior"; "the calibration reproduces the estimator's pull toward its prior") | none new |

**Not targeted, so unchanged:**
- **Data Availability's release-package sentence,** quoted in 2 of 3 runs. It is protected text and goes on the (d) list,
  with both raters' readings ("not yet deposited", placed last).
- **Everything else.**

**What this round can and cannot do.** The six passages were each quoted once to three times. r19 lifted the pairwise
but not P1. r20 may move P1, or it may not. The report will give the final P1 beside the published anchors' mean of
3.67, as measured.
