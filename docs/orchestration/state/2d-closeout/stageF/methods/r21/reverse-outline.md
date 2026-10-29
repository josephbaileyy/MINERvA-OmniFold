# Reverse outline: paper_body.tex at b70156a1

**Source:** `docs/analysis-note/paper_body.tex` at commit b70156a1. This outline says what each paragraph does, not
how it says it. The facts, with their exact atoms, are in `fact-ledger.md`. The PB ranges give each paragraph's base
sentences there.

**Out of scope (PROTECTED, in main_paper.tex, not outlined):** the title, the abstract, the acknowledgments with the AI
statement, Data Availability, and every `\pubhold`.

**Body preamble (PB0).** The file opens with three macro definitions: `\pcell` (a fixed-width table cell), and `\nsec`
and `\napp` (numbered pointers into the companion analysis note). Keep them.

Section numbers are as printed in `main_paper.pdf`. Subsections print as letters (IV A, IV B, and so on).

---

## I. Introduction (`\label{sec:intro}`)

1. (PB0–PB7) Motivates multidifferential unfolding. Contrasts binned iterative unfolding with OmniFold's unbinned,
   classifier-based reweighting. Places the work among earlier unbinned applications (collider data, and one simulated
   neutrino sample) and against the three-dimensional state of the art for neutrino measurements on data.
2. (PB8–PB11) States what the paper measures: a simultaneous five-observable charged-current inclusive cross section
   from MINERvA open data, in sixteen cells with a covariance, compared with five generators. Adds the reproduction of
   the published 2D result as an end-to-end test and the 3D and 4D central values. Notes that the five observables are
   not independent, because reconstructed W is fixed by the other three.
3. (PB12–PB14) Lists the validation studies, states the question they answer (is the result reliable when the
   simulation mismodels the truth by generator-sized amounts?), and defines coverage.
4. (PB15–PB16) Discloses that interval coverage has not been validated, and says where the bias tests, the fake-data
   study and the flux-correlation dependence of the generator χ² are reported.
5. (PB17–PB18) Scopes the findings to one implementation, one data set and the cases tested, and points to the
   Limitations subsection.
6. (PB19–PB22) Gives the roadmap of the sections and the role of the companion note, which is cited by section.
<!-- absence-ok: quotes printed limitation sentences of the paper as facts to restate; not a claim that a result does not exist -->

## II. Data, simulation, and observables (`\label{sec:data}`)

1. (PB23–PB34) Describes the data set, its exposure and the detector. Defines the signal, its fiducial and kinematic
   limits, and the background. Gives the selection, the flux treatment, the sample sizes and the simulation with its
   tune. States that the selection stays fixed as observables are added.
2. (PB35–PB42) Defines the five observables at truth level, including the displayed Eavail equation with its 135 MeV
   constant, and states how reconstructed Eavail, q3 and W are formed.
3. (PB43–PB50) Explains that reconstructed W is an exact function of the reconstructed (pT, ppar, q3), which inputs
   are and are not constrained this way, and the truth-level caveat that angles are measured from the beam axis. Points
   to the note.
4. (PB51–PB60) Defines the external generator predictions: their versions, targets, flux reweighting and the ways
   their definitions differ from the analysis's. Discloses the uncorrected carbon-versus-CH target difference and gives
   GENIE's estimate of its size.
5. (PB61–PB66) Defines the fine analysis grid, the coarse 3⁵ grid with its keep rule, and the joint cells.

## III. Cross-section extraction (`\label{sec:method}`)

1. (PB67–PB71) Describes one OmniFold iteration and how cross sections are formed from the reweighted truth,
   including how reconstruction inefficiency is handled.
2. (PB72–PB75) Defines the two background treatments (purity-based, and unbinned negative-weight with refinement) and
   states where their targets agree and where they differ.
3. (PB76) Discloses how the classifiers are trained: on the full sample, with no held-out split, early stopping or
   class balancing.
4. (PB77–PB81) States the settings both estimators share and how their capacity was chosen, with no tuning on data.
5. (PB82–PB86) Introduces the two estimators and the results that use each, and defines the joint-test estimator.
6. (PB87–PB88) Gives the reason the joint-test estimator keeps five iterations.
- **Table I** (`tab:estimators`, PB89–PB92), placed after ¶6.

### III A. Reporting definitions and the precision target (`\label{sec:uncertainty-status}`)

1. (PB92–PB98) Defines the model-dependence envelope and the 10% precision target. Reports that no tested
   five-observable reporting definition meets the target once the envelope is added, and gives the reason for each
   definition.
2. (PB99) States the envelope's typical size per cell and compares it with the generator differences a measurement
   would need to resolve.

### III B. Reporting cells (no label)

1. (PB100–PB102) Defines the sixteen reporting cells of the five-observable result: the box construction, the purity
   merge, the unreported boxes and the support rule. Points to the covariance.

## IV. Uncertainties and validation (`\label{sec:validation}`)

1. (PB103–PB107) Defines closure and pointwise coverage. States how the pseudo-data studies reweight the truth and
   the envelope reweights the prior, all with the simulation's detector response.

### IV A. The reported covariance (`\label{sec:cov16}`)

1. (PB108–PB114) Defines the reported covariance of the sixteen-cell result: C_total, which contains C_model, plus
   C_resp. Gives what each component covers and does not cover, and the median size of the covariance.

### IV B. Two-dimensional benchmark (`\label{sec:repro2d}`, `\label{sec:repro2d-pub}`)

1. (PB115–PB122) Reports the 2D reproduction: the ratio of integrated cross sections, the RMS of the pulls, and the
   descriptive χ² with its pseudo-inverse construction. Interprets the χ² as a shape difference whose source is
   unknown. Points to Fig. 1.
2. (PB123–PB126) Explains why LightGBM gives the central value. Discloses the estimator dependence and the
   post-selection, which make this a reproduction rather than an independent validation. Gives the size of the learner
   difference.
- **Fig. 1** (`fig:validation`, PB127–PB130).

### IV C. Two-dimensional covariance (`\label{sec:uq2d}`)

1. (PB130–PB136) Describes the four-block 2D covariance and compares its size with the publication's. Discloses the
   unexplained flux-uncertainty difference and what the covariance omits, and states that it is not independently
   validated.
2. (PB137–PB139) Describes the statistical block and states that no coverage has been tested or is claimed.
3. (PB140–PB144) Reports the inconsistency between run periods and how the run-period block absorbs it. Notes that
   the block's size cannot be validated.
4. (PB145–PB151) Defines the separate generator-shape covariance C_model and gives its size and status. Explains why
   the comparison with the published uncertainty leaves it out.

### IV D. Normalization and closure (`\label{sec:closure}`)

1. (PB152–PB153) Reports the only normalization comparison available for the joint-test estimator's results, and
   points to earlier checks.
2. (PB154–PB157) Reports the five-observable closure with backgrounds: the purity bias at high W, its reduction by
   negative-weight subtraction, and how much the two treatments differ on data. This paragraph holds four GATE phrases.
3. (PB158–PB160) Reports the 2D closure with backgrounds that motivates the refined estimator for the 2D result.
- **Fig. 2** (`fig:bkg-residual`, PB161–PB168).

### IV E. Generator-sized truth changes (`\label{sec:departure}`)

1. (PB168–PB175) Reports that a generator-sized change of the Eavail shape is only partly recovered, and how large
   the residual is. Explains why it is read as regularization bias. Gives the joint-test estimator's results for other
   shapes, with the caveat on the uncertainty they are compared with. Points to the fake-data tests and the note. This
   paragraph holds three GATE phrases.
- **Fig. 3** (`fig:deformation`, PB176–PB183).
2. (PB183–PB186) Reports the exact binned unfolding diagnostic: its population, its scope, and its conclusion within
   that scope.

### IV F. Coverage (`\label{sec:coverage}`)

1. (PB187–PB189) Reports, with counts, the coverage failure of the purity-based estimator's statistical intervals at
   the tested truths.
2. (PB190–PB193) Gives the diagnosis (a residual bias that grows with W) and discloses that its source is unknown.
   Notes that agreement of the normalizations does not mean the bias is small.

### IV G. Estimator stability (`\label{sec:cov5d}`)

1. (PB194–PB196) Discloses that the joint-test estimator is unstable at the level of rounding, and what this costs.

### IV H. Fake-data tests of the sixteen-cell result (`\label{sec:fd16}`)

1. (PB197–PB201) Describes the fake-data test of the sixteen-cell result: the truths, the rule for omitting a C_model
   component, the listing criterion, and what Table II shows.
- **Table II** (`tab:fd16`, PB202).
2. (PB202–PB203) Says which truths are listed. Concludes that the reported uncertainty does not cover the bias at the
   GiBUU-like truths or at the q3 tilt, while the other truths pass.
3. (PB204–PB213) Reports the tests at two held-out GENIE v3 tunes and their results. Gives the caveats: shared
   models, partial evidence, cell R11's dependence on C_model, and no probe of the detector response. States that the
   tests measure bias, not coverage.

## V. The sixteen-cell cross section (`\label{sec:result16}`)

### V A. Result (no label)

1. (PB214–PB215) Introduces Table III and states that quantitative comparisons need the full covariance. Points to
   the note's correlation and per-component tables.
- **Table III** (`tab:result16`, PB216–PB219).

### V B. Comparison on the sixteen reported cells (`\label{sec:gen16}`)

1. (PB219–PB224) Explains why truth-level results can be reused, and describes the χ² comparison with five
   predictions (Table IV, Fig. 4). Gives the GiBUU restriction, the target and prior caveats, and the fact that some
   covariance terms come from the generators being compared.
- **Fig. 4** (`fig:ratio16`, PB225–PB229) and **Table IV** (`tab:gen16`, PB229).
2. (PB229–PB234) Reports how sensitive the χ² is to the flux correlations and to the other correlation groups, and
   the bootstrap of the flux universes. States what the bootstrap bands mean and what they do not.

### V C. Descriptive comparison of the central values (`\label{sec:central}`)

1. (PB235–PB237) Gives the descriptive comparison of the 3D and 4D central values: every generator underpredicts at
   low Eavail. Points to the further comparisons in the note.
2. (PB238) Points to the note for the earlier five-observable (Eavail, W) map and its comparisons.

## VI. Discussion and conclusions (`\label{sec:conclusions}`; a bare `\label{sec:limits}` stands before ¶2)

1. (PB239) Names the principal result.
2. (PB240–PB244) Brings together two findings that show the result retains part of its prior. Ties the note's
   calibrated tests to the same effect, and leaves open whether the coverage failure has the same origin.
3. (PB245) Lists what must be checked before unfolded intervals are interpreted.

### VI A. Limitations (`\label{sec:limitations}`)

1. (PB246–PB254) Summarizes the principal limitations: the 2D covariance, the 3D and 4D central values, the coverage
   of the sixteen-cell result, the low-stability cells, and the conditions and scope of the note's calibrated tests.

---

## Figures, tables and the equation

| Float | Label | Placed in | Purpose (one sentence) | Referenced from |
|---|---|---|---|---|
| Table I | `tab:estimators` | III, after ¶6 | Lists the two estimators, their background treatment and refinement, and the results each one produces. | III ¶5 (PB82) |
| Fig. 1 | `fig:validation` | IV B | Compares the 2D result's pT and ppar projections with the published result, with per-bin pulls and an uncertainty summary. | IV B ¶1 (PB122) |
| Fig. 2 | `fig:bkg-residual` | IV D | Shows closure residuals at nominal truth with backgrounds, for purity versus negative-weight subtraction, in the (Eavail, W) cells and the joint cells. | IV D ¶2 (PB154); Fig. 3 caption (PB178) |
| Fig. 3 | `fig:deformation` | IV E | Shows recovery residuals under deformed truths: (a) the development variant at the GiBUU/GENIE Eavail shape; (b) the joint-test estimator at three held-out shapes. | IV E ¶1 (PB168); Table I contents ("Fig. 3b", in PB92) |
| Table II | `tab:fd16` | IV H | Gives the χ², p and flagged cells of each fake-data truth against C_total + C_resp and against C_total. | IV H ¶1 (PB199, PB201) |
| Table III | `tab:result16` | V A | The result: each cell's box, its cell-integrated cross section f, and its marginal σ/f, with the median. | V A ¶1 (PB214) |
| Fig. 4 | `fig:ratio16` | V B | Shows data over prediction, cell by cell, for the five predictions. | V B ¶1 (PB221) |
| Table IV | `tab:gen16` | V B | Gives the χ²/ndf and the shape-only χ²/ndf of each prediction against the sixteen-cell result. | V B ¶1 (PB220); Fig. 4 caption (PB225, PB229) |
| Eq. (1) | `eq:eavail` | II ¶2 | Defines available energy Eavail. | not `\ref`'d in the body |

The writer copies tables and figures verbatim. The captions are ledgered fact by fact, and each table's contents are
one STRUCTURE row.

## Structural observations (unchanged, for the writer and the director)

- `\label{sec:limits}` stands alone between ¶1 and ¶2 of Sec. VI, attached to no heading, so it resolves to Sec. VI.
  Nothing in the body refers to it.
- `\label{sec:cov5d}` labels "Estimator stability", and its name does not match the title.
- III B "Reporting cells" and V A "Result" have no labels.
- No `\ref` in the body points to `sec:intro`, `sec:closure`, `sec:cov5d`, `sec:limits` or `eq:eavail`. They must
  still survive, under paper-protections check 3.
- III B ¶1 says every reported cell "passes the support rule". The rule is defined in II ¶5 (PB63), but that paragraph
  never calls it the support rule.
