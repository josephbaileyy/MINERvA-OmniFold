# r22 Step 2, paper round: two-direction review of `paper_body.tex`

Reviewer: an independent, read-only agent. Base `f47b1b4a`, compared with the uncommitted worktree `wt-con`
(`git diff f47b1b4a --word-diff=plain -- docs/analysis-note/paper_body.tex`). `main_paper.tex` and `main_note.tex`
are byte-identical to the base (`git diff --quiet`). Line numbers are for the worktree's `paper_body.tex`. Note
sources are quoted from the unchanged note `.tex` files in the worktree.

Not re-checked (machine-checked already): probe strings, GATE phrases, the FROZEN sentence, labels, numerals, the
23 held sentences, and the other files.

**Counts:** LOST 2, WEAKENED 1, MOVED-AWAY 0, AMBIGUOUS 2, ADDED 2. Total 7.

## Findings

### R-1 (LOST, serious). The cut "The low stability of four of the sixteen cells is stated only here."

- **Base (Sec. VI A):** "The limitations of these results are stated with the results they qualify, in
  Secs.~\ref{sec:method}--\ref{sec:result16}, and those of the calibrated tests in the companion note. The low
  stability of four of the sixteen cells is stated only here. The principal ones are these."
- **New (:279):** "… and those of the calibrated tests in the companion note. The principal ones are these."
- **Why:**
  - The cut sentence was the one exception to the held sentence's general claim. The four low-stability cells print
    nowhere else in the paper: `\fvval{h2-lowstab-…}` occurs only in item 2 (:283).
  - The note does not print them either. `h2-lowstab` occurs in no note source except `values_fived16.tex`.
    Protections inventory C18: "Prints now: nowhere", and Joseph's decision (`h2-16-cell-definition.md:42-43`) places
    the disclosure "in the paper's limitations".
  - So the held sentence now reads as a universal claim that is false for this limitation (B1 guardrail).
  - The #522 move fails its first condition, since the note does not print the fact. The ledger calls it CUT-PAPER
    (P-24) and gives no `N:` probe, although `gaps.tsv` requires one for G1:paper-s-10 ("pointer and probe
    required").
- **Fix:** restore the base sentence verbatim, between the held sentence and "The principal ones are these."
  Report G1:paper-s-10 and G1b:paper-s-15 as skipped for this sentence: the held sentence plus C18's decided home
  leave no compliant place to move it. The "reconstruction stability" wording of item 2 can stay.

### R-2 (ADDED, with an ambiguity). "The \jtNcells{} coarse cells that meet it, the joint cells, are the populated cells of the five-observable grid."

- **Base:** "Of the coarse cells, \jtNcells{} pass; these are the joint cells."
- **Why:**
  - "populated" is a gloss that neither the base nor the note states for this rule. The note uses "populated" only
    for other grids (`sec_3d.tex:194`, `app_negweight.tex:77`).
  - The gloss is also misleading. The support rule is a threshold of 1000 events, and the very next sentence says the
    other cells "hold \SI{0.47}{\percent} of the expected signal". They are populated, just below the threshold.
  - "the five-observable grid" does not say which grid. The paragraph defines two five-observable grids, the fine
    grid and the coarse $3^{5}$ grid.
- **Fix:** "The \jtNcells{} coarse cells that meet it are the joint cells."

### R-3 (AMBIGUOUS). "… and the coverage of the sixteen-cell total uncertainties is not validated, their fake-data tests in Sec.~\ref{sec:fd16} assessing the estimator's bias."
<!-- absence-ok: quotes printed limitations of the paper under review; not a claim that a result is absent -->

- **Base (item 3):** "The sixteen-cell result also has total uncertainties, whose coverage is not validated;
<!-- absence-ok: quotes printed limitations of the paper under review; not a claim that a result is absent -->
  Sec.~\ref{sec:fd16} reports the fake-data tests of the estimator's bias."
- **Why:**
  - The absolute phrase "their fake-data tests" makes the tests belong to the total uncertainties. It can be read as
    saying that the uncertainties were tested, which undercuts "not validated" in the same clause.
  - The base said plainly that the tests are of the estimator's bias, which is the qualifier C12 needs.
  - The rest of the merged item keeps every fact of the three base items, and both `% Search` lines still follow it.
- **Fix:** "… and the coverage of the sixteen-cell total uncertainties is not validated (the fake-data tests of
<!-- absence-ok: quotes printed limitations of the paper under review; not a claim that a result is absent -->
  Sec.~\ref{sec:fd16} assess the estimator's bias)."

### R-4 (WEAKENED). "The joint-test estimator is sensitive to perturbations of its inputs within floating-point rounding."

- **Base:** "The joint-test estimator is unstable at the level of rounding."
- **Why:**
  - The r21 ledger marks the base sentence HONESTY (F258), and "unstable" is its verdict. "sensitive" states a
    property without that verdict.
  - The next sentence still says the estimator "fails a data-stability requirement", so nothing becomes false. But the
    topic sentence of the section is softer than the base.
  - "within floating-point rounding" is supported: `sec_5d.tex:90` says "input perturbations within floating-point
    rounding move functionals …" and "place this instability in the estimator".
- **Fix:** "The joint-test estimator is unstable under perturbations of its inputs within floating-point rounding."
  This keeps the verdict word, makes the perturbation precise (the gap's request), and no longer collides with the
  cells' "reconstruction stability".

### R-5 (AMBIGUOUS). "The scale is applied to proton, meson, electromagnetic and other deposits. It does not cover neutron or muon deposits, …"

- **Base:** "The response term $C_{\mathrm{resp}}$ is the response … in the simulation, for protons, mesons,
  electromagnetic and other deposits, but it does not cover neutron or muon deposits, … and it enters only this
  result …"
- **Why:**
  - In the base, the subject of "does not cover" is $C_{\mathrm{resp}}$. In the new text, "It" refers back to "The
    scale". C17 (keep) protects the scope of $C_{\mathrm{resp}}$ itself, and "the scale does not cover … effects beyond
    a scale" is circular.
  - "applied to proton, meson, … deposits" can also be read as one common scale. The note says it is applied
    separately: `sec_fived16.tex:48`, "scaled by one standard deviation separately for four deposit categories".
- **Fix:** "… in the simulation. The scale is applied to proton, meson, electromagnetic and other deposits.
  $C_{\mathrm{resp}}$ does not cover neutron or muon deposits, nor species, energy-dependence or resolution effects
  beyond a scale. It enters only this result, its fake-data tests and its comparison in Sec.~\ref{sec:gen16}."
  - Optional, and supported by the note line above: "applied separately to".

### R-6 (LOST, low; a ledger mislabel). "With the joint-test estimator, the envelope alone exceeds the target for the \jtNcells{} coarse joint cells and for the 39 supported $(\Eavail,W)$ cells."

- **Base:** "… and for the fallback definition, the 39 supported $(\Eavail,W)$ cells."
- **Why:**
  - The 39-cell definition's role, as the selection procedure's fallback, has left the paper. This is a fact about
    the study, not wording.
  - It is not one of the brief's #522 moves, but B2 is met: `sec_5d.tex:146` says "The selection procedure then takes
    RD3 as the fallback", and RD3 is "the 39 EW cells".
  - The ledger labels P-10 REWORDED. Since a fact left the paper, it is a cut.
  - No result depends on the role, and G1b:paper-s-09 asks for it to go.
- **Fix:** relabel P-10 as CUT-NOTE, keeping its existing `N:` probe, and have the director accept the cut. If it is
  not accepted, restore "and for the fallback definition, the 39 supported $(\Eavail,W)$ cells".

### R-7 (ADDED, low). "… and it fits its full number of trees with each class at its own total weight (\nsec{sec:method-algo})."

- **Base:** "… without a held-out or cross-fitted split, early stopping, or class balancing (\nsec{sec:method-algo})."
- **Why:**
  - "fits its full number of trees" is a general-knowledge gloss for "no early stopping". It is correct, but neither
    the base nor the note says it. The note says "and no early stopping".
  - "each class at its own total weight" stands close to the note, which says "The two classes keep their physical
    weights, with no class balancing" (`sec_method.tex:15`).
  - The not-held-out qualifier survives: "so no held-out or cross-fitted split is used".
- **Fix (note wording):** "Each classifier is trained on the full sample whose weights it then sets, so no held-out or
  cross-fitted split is used; it is trained without early stopping, and the two classes keep their physical weights
  (\nsec{sec:method-algo})."

## Rulings on the specified points

| Point | Ruling | Reason |
|---|---|---|
| "it fits its full number of trees with each class at its own total weight"; is "so no held-out or cross-fitted split is used" still the not-held-out qualifier? | **FIX** (R-7) | The qualifier is kept: "so" is a valid consequence of training on the full sample. "full number of trees" is an unsourced gloss. Use the note's words (`sec_method.tex:15`). |
| "sensitive to … within floating-point rounding"; heading "Sensitivity to input rounding"; is "floating-point" supported? | **FIX** (R-4) for "sensitive"; "floating-point" **OK** | "floating-point" is supported by `sec_5d.tex:90`. The heading is OK; "Sensitivity to rounding-level input changes" would match Sec. VI's checklist wording, but this is optional. |
| "the joint cells, are the populated cells of the five-observable grid" | **FIX** (R-2) | "populated" is unsourced and misleading, and the grid is ambiguous. |
| "\fvval{f0b-nungraded} further truths, given in the note, are descriptive and not judged against these criteria" | **OK** | `sec_fived16.tex:146` says "the six power alternatives built on that correction are therefore descriptive and not judged against the failure criteria". `f0b-nungraded` is 6, and `sec_fived16.tex:113` defines those criteria as the paper's listing condition ("A truth is listed as failing when $p<…$ or when any cell has $|z|>…$"). |
| "where each null takes the simulation's event composition"; "a rejection extends … only if … is bounded, and no such bound has been shown" | **OK** | `sec_joint.tex:19` says "Below that grid, the null truth has the MINERvA Tune~v1 simulation's event composition". The paper's own hybrid-truth definition (Sec. IV H) supports it too. The conditional and the "not shown" are equivalent to the base, and "hybrid nulls" and "conditionally on …" are kept. |
| "the calibration, which simulates the whole analysis chain," | **OK** | `sec_joint.tex:14` says "Calibration can be obtained … by simulating the whole analysis chain at the hypothesis". Item 3 of the limitations already says "the simulated chain". |
| "the miscoverage of Sec.~\ref{sec:coverage}" for "the coverage failure" | **OK** | `sec_5d.tex:83` says "the coverage failure of \S\ref{sec:coverage-5d}". The paper's Sec. coverage cites that section and calls it "the miscoverage". C11 keeps its three items. Moving it after "Within that scope …" detaches nothing, and "does not address" is the note's own verb. |
| Removed "The coverage of unfolded intervals is the rate at which they contain the true cross section." | **OK** | Coverage is defined in the paper at :81 ("Coverage, how often intervals contain their target over repeated experiments, …"). The cut sentence prints verbatim in the note (`sec_joint.tex:14`). The intro's "a coverage test" now comes before the definition; PRD readers will not need it. |
| Fig. 1 caption: "is the four-block covariance of Sec. …, without $C_{\mathrm{model}}$" | **OK** | The blocks and the learner-dependence omission print in Sec. IV C at the covariance's definition: "(187 universes, including the normalization)" and "The covariance omits … the learner dependence of Sec.~\ref{sec:repro2d-pub}". The base caption's omission list was already partial (it left out the fail-reconstruction approximation and the regularization). "is from the four-block covariance" would be more exact than "is", but this is optional. |
| The three limitation items merged into one | **FIX** (R-3) | All facts are kept. "their fake-data tests" ties the tests to the uncertainties. |
| "The other configurations used below, and their results, are described in …" | **OK** | "used below" is true: the development variant (Fig. 2, Sec. IV G), purity-based subtraction (Sec. IV F) and the earlier purity-subtracted value (Fig. 3) are each labelled where they are used. `sec_method.tex:28` says sec:method-config "gives the configuration behind each result". The development status is no longer stated in this sentence, but it is stated at every use. |
| "a reconstruction stability of" and "robustness to training seeds" | **OK** | The term is defined in place by the colon clause, and the qualifier separates it from the input sensitivity (G1:paper-s-07). "robustness to" is a synonym of "stability under". |
| (not listed) cut "This constant is inherited from the analysis framework's definition." | **OK** | This is a #522 move. `sec_3d.tex:40` says "Both definitions are inherited from MAT-MINERvA rather than chosen for this analysis", and `:42` says "subtracts the inherited constant \SI{135}{MeV}". The observable stays defined in the paper. |
| (not listed) cut "The limitations are listed in Sec.~\ref{sec:limitations}." and the Scope run-in | **OK** | The roadmap (:16) already says "Sec.~\ref{sec:limitations} summarizes the principal limitations". The held Scope sentence prints unchanged. |
| (not listed) cut "The low stability … is stated only here." | **FIX** (R-1) | See R-1. |

## `pairs.md`

- **G1:paper-s-06 (A4): OK.**
  - The `before` occurs once in `main_paper.tex`, and the `after` occurs once in `main_note.tex`, identical to the
    approved note abstract (:72).
  - The pin `bbb99991e62f584b` recomputes.
  - The three `\fvval` macros are identical on both sides.
  - "compared only on the 8 cells its sample covers" is supported by the paper body (Sec. V B): "GiBUU's sample stops
    at … so GiBUU is compared on the 8 cells with $\pPar<…$ only".
  - The GiBUU value is not given a number of degrees of freedom, on either side.
- **G1:paper-s-09 (A1): OK.**
  - The `before` occurs once, and the pin `083bfb80f9fac8fd` recomputes.
  - "candidate", "not yet deposited", `\SI{16}{MB}` and the three dependencies are kept.
  - "are regenerated by" makes the same capability claim as the base's "regenerates". Nothing new is said to exist,
    be deposited or be reproduced.
  - Optional: a reader could take the passive "are regenerated by" as the provenance of the printed figures.
    `app_release.tex:37` says that for the figures "the check is that their files are produced". "can be regenerated
    by" would rule that reading out, but is not required.
