# Reverse outline, batch b8, before (origin/main 5fb31c7e)

One sentence per paragraph (or list item). Ids are used in `ledger.md` and `changes.md`.

## Abstract (`main_note.tex`, abstract environment)

- A1. OmniFold on MINERvA open data reproduces the published 2D integral within about 1%, with a correlated shape
  difference, and the uncertainty scale.
- A2. That uncertainty uses the central value's own learner and seed; whether it describes the central value has not
  been measured.
- A3. Adding Eavail, q3, W gives 3/4/5-observable unbinned unfolds passing marginal-normalization checks to 1-2%;
  binned MINERvA already reaches triple-differential; the feature is five related observables unfolded together.
- A4. Generators under-predict at low Eavail (low-recoil region); descriptive excess over Tune at high Eavail, high W,
  where external generators also under-predict by about their overall shortfall (GiBUU energy limit, C vs CH);
  a fifth in the widest overflow cell, extends to low W in ratio, regularization bias largest there; no mechanism.
- A5. Background-inclusive closures show purity bias; negative-weight treatment largely removes it, used only for the
  generator tests; central values keep purity and its bias of up to 4% in the highest-W cells.
- A6. Generator-sized truth reweighting leaves a residual bias, interpreted as regularization bias, in no quoted
  uncertainty; coverage and estimator-seed studies show limitations: statistical intervals miscover at tested truths.
- A7. Under a five-deformation envelope no tested reporting definition meets the predeclared 10% criterion.
- A8. As an application, calibrated joint tests reject the hybrid nulls of all five predictions (total, shape) at 5%
  familywise under the stated calibration assumptions; not exclusions; NuWro total not robust to CH; valid only under
  stated conditions; recover known discrepancies, no discriminating power beyond matched coarse projections; no
  recoil-response uncertainty; fine-grid convergence not shown.
- A9. A scalar study removes the truth-level muon cuts; PET is future work, no PET result used.

## Executive summary (`sec_execsummary.tex`)

- E0. OmniFold on MINERvA ME data; the validation findings are the main results (scoped); the generator tests are an
  application illustrating calibrated inference with a biased estimator.
- E1 (Reproduction). Integral within about 1%, shape difference, ratioTot, binsTen%, uncertainty comparable
  (medians, integrals); flux band carries the nu-e and IMD constraint weights; same LightGBM estimator for central value
  and uncertainty, changed from exact-split after both comparisons were known; chi2/ndf vs published covariance,
  descriptive, source unidentified.
- E2 (3D/4D/5D). Marginal-normalization checks 1-2%; binned MINERvA reaches 3D; 3D/4D closures (0.10, 1.1%) have no
  threshold on record; W fixed by (pT, ppar, q3); 135 MeV inherited constant.
- E3 (Low Eavail). Four truth-level generators under-predict the dip (0.1-0.4 GeV), the low-recoil region; FSI dials
  and Valencia 2p2h comparisons are central-value comparisons and identify no mechanism.
- E4 (High Eavail, W). Positive difference from Tune mostly at Eavail >= 0.8, much at W >= 1.8; map locates no
  mechanism; a fifth in widest overflow cell; largest regularization bias; extends to low W in ratio; external
  generators short by about their overall shortfall (GiBUU 20 GeV); C vs CH; covariance used though it failed its
  acceptance criteria, seed sensitivity (companions) above limit, so central values only.
- E5 (Joint tests). Hybrid nulls for five predictions, total and shape, all ten rejected under six conditions, FWER 5%
  under the calibration assumptions, size averaged over nuisance priors; closest margins 1.11 and 1.30; not exclusions;
  coarse projections reject too; no recoil-response band; robustness variant; lost pseudo-experiments rerun, none
  changes a decision; CH correction moves both toward data, NuWro total not robust; hypothesis tests, not an
  uncertainty.
- E6 (Methodological finding). Standard covariance omits cross-source response terms; unified-throw test perturbs all
  reweightable sources together, joint mean shift separate.
- E7 (Extended fiducial). Removing truth-muon cuts: about 6% of the rate in new acceptance-supported cells (tier 1),
  about 28% in low/zero-efficiency cells (tier 2).
- E8 (PET). Future work, documented separately; no result depends on it.
- E9 (Table caption). Construction, tests and interpretation of each scalar result are distinct; pointers; PET none.
- E10 (Not claimed: coverage). Earlier 2D band undercovers in tails (C2 vs 0.954); rebuilt band not re-tested
  independently; quoted block (a different ensemble) not tested.
- E11 (Not claimed: 5D coverage). No 5D frequentist coverage; one test miscovers; under the 10% rate reduction the
  rate is recovered and a residual W-growing bias, inferred, source not established, causes it.
- E12 (Not claimed: regularization bias). Partial recovery of a generator-sized Eavail change (fixed-size, not a
  measured generator difference), up to 74% in the highest-W column, with or without background; interpreted as
  regularization bias (persists over tested iterations and capacities), no remedy, in no uncertainty; negative-weight
  removes most purity bias, about 1% left in some joint cells; central values keep purity (up to 4%); refinement used
  only for the generator tests.
- E13 (Not claimed: stability). The tested candidate fails the predeclared data-stability criterion, as does its
  baseline (up to 2.6 sigma under rounding-level changes); spread contained in the refit-per-replica bootstrap
  (about 37%); central value reproducible only to that size.
- E14 (Not claimed: mechanism). Descriptive; no mechanism; FSI dials exclude no other transport effects.
- E15 (Not claimed: 5D measurement). Envelope (sensitivity diagnostic, median about 10-13%); no reporting definition
  meets the predeclared 10% criterion under the prescription within the study's rules and budget.
- E16 (Not claimed: 5D covariance). Four measurements, led by the seed sensitivity (companions), limit every result
  built from the covariance; no other corrected 5D covariance replaces it.
- E17 (Not claimed: extended fiducial). Tier 2 prior-dominated extrapolation; no extended-fiducial covariance.
- E18 (Not claimed: PET). No PET result or uncertainty.

## Introduction (`sec_intro.tex`)

- I1. MINERvA: NuMI, upstream of MINOS, ~decade to 2019, LE/ME, FHC/RHC; cross sections a leading oscillation
  systematic; few-GeV regime; we use the public ME FHC CC-inclusive product.
- I2. The published 2D cross section (Ruterbories et al., IBU); we reproduce it with unbinned OmniFold.
- I3. ML has enabled unbinned unfolding: reweighting (OmniFold most adopted) and generative families; both lift the
  binned-response limitations of IBU, SVD, TUnfold.
- I4. Prior OmniFold applications: H1, LHCb, ATLAS; Canelli et al. practice; three practices appear in our budget.
- I5. Background practice: H1 cut, LHCb per-track, ATLAS left <0.25% and identified negative weights; guide
  recommends; OmniFold-HI and generative unfolding treat backgrounds; prescriptions differ.
- I6. Huang et al. (T2K mock data); two findings; our differences: real data, absolute normalization, "complete" 2D
  budget with the central value's learner, GBDTs, validation against a published measurement.
- I7. Why unbinned: three bullets (binning after unfolding, purity exception; observables as features; regularization
  by capacity and iteration, method comparison).
- I8. Analysis strategy: 2D validation, extensions, tests, FPS, PET future work, §9 and §10 follow the central values.
- I9. Where to find it: meta text and the roadmap table (13 rows + records row).

## §11 Extended fiducial phase space (`sec_fps.tex`)

- F1. Preliminary scalar central value, three-prior envelope, hidden-variable closure, 200-toy containment; no
  covariance; signal unchanged; truth-muon cuts removed, MINOS selection unchanged; extended fiducial, not
  unrestricted.
- F2. Published cuts exclude a third; 66.4/22.3/11.3%; acceptance corrected natively; event-loop switch 32.8M -> 49M;
  extrapolation through the step-1 miss regressor; validation tests quantify the prior cost.
- F3. Fig. fpsacc caption (efficiency ~0.65, dead region 27.7%).
- F4. Validation battery lead: four results establish the extension.
- F5-F8. Published-region check; closure (self and hidden-variable); three-prior envelope (NuWro prior not rebuilt);
  containment diagnostic.
- F9-F10. Fig. fpscmp and fpsenv captions.
- F11. Central value (purity, not the designated negative-weight treatment), fpsAbove% above; two-tier reporting
  (6%, 28%); no uncertainty beyond the envelope (no re-selected-band covariance).

## §12 Summary and outlook (`sec_summary.tex`)

- S0. Meta lead: the executive summary lists results; validation findings are the main results; tests an application.
- S1. 2D: integral within 1% and uncertainty scale; shape difference chiPaper, learner-dependent; same estimator,
  chosen after comparisons; coverage failure, rebuilt band post hoc, quoted block untested.
- S2. 3D-5D: checks 1-2%; closures 0.10, 1.1%, no threshold; W redundancy; data above "all four external
  generators at low Eavail"; above Tune at high Eavail, W; generators' shortfall; C vs CH; fifth; low W; bias; no
  mechanism.
- S3. Purity bias up to 4% kept; refinement "used only for the generator tests"; partial recovery = regularization
  bias; envelope 10-13%, no definition meets 10%; miscoverage, residual bias inferred; "the one five-axis covariance
  ... has an estimator-seed sensitivity above the limit" so no significance.
- S4. Joint tests (hybrid, six conditions, FWER, not exclusions, known discrepancies, no gain, no recoil band, no
  uncertainty, NuWro CH).
- S5. PET future work.
- S6 (Outlook). FPS central value, 6%/28%; PET; 5D covariance used though not passing; no 5D measurement meeting the
  criteria (restates S3); NEUT, 44-cell Ascencio; flux-muon-energy posterior.
- S7 (Reusing). ATLAS release, omnifold_publication; a MINERvA release should specify ...; App. G records fixed
  identities; candidate package exists, no release tagged or deposited; rebuilding reproduces no result; projections
  need their own checks; release design does not affect the covariance choice.
