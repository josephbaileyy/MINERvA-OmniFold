# Reverse outline (before), batch b5: §2 `sec_experiment.tex`, §3 `sec_method.tex`, §4 `sec_systematics.tex`

Base: origin/main 551f9432. One sentence per paragraph. Ids are used by `ledger.md` and `changes.md`.

## §2 The MINERvA experiment, data and simulation samples

- **E1** (§2.1) MINERvA detector, MINOS spectrometer, ME FHC exposure, constrained flux identical to the published one.
- **E2** (§2.2) Twelve playlists, 1.057e21 POT, 4 119 797 selected data events.
- **E3** (§2.2) GENIE 2.12.6 + MINERvA Tune v1 via MAT reweighters; Geant4 simulation; 32 849 103 true signal events, POT-normalized.
- **E4** (§2.3) Signal definition and muon phase space follow the published analysis.
- **E5** (§2.3) Fiducial volume and its 3.2353e30 nucleons.
- **E6** (§2.3) Reconstructed selection; MINOS-match identifier in prose; background rate 0.35% vs the published 8655 (0.2%); definitions of backgrounds and fakes; both subtracted.
- **E7** (§2.4) Event loop writes four trees per playlist; lateral/vertical defined; two completeness conditions; per-playlist running; merger; flux histogram.
- **E8** (§2.5) Data exceed Tune v1 by ~12%; pT trend 0.88 to ~1.2; shapes described well.
- **E9** (§2.5) Shapes of each observable; background location; low-Eavail enhancement.
- **E10/E11** Figure captions (control plots, corner plot).

## §3 The unbinned OmniFold procedure

- **M1** (§3.1) OmniFold iteration: step 1, pull-back, misses, step 2; regularization by iterations and capacity.
- **M2** (§3.1, paper-pointed) Training details: full-sample fit, no held-out split, no early stopping, no class balancing or renormalization, clip, miss regressor, refinement weight, no effective sample size.
- **M3** (§3.1) Purity weight formula; ~3% effect.
- **M4** (§3.1) The one binned step; negative-weight alternative reproduces it (\nwPctTot, 2%); quoted results do not use it.
- **M5** (§3.2) Why GBDTs; all unfolds use them; implementation tests.
- **M6** (§3.2) "Since 2026-10-11" LightGBM for the 2D central value and its ensembles; seed 42; seed-1 comparison 0.18%/1.79%/0.30/1.28; regenerations.
- **M7** (§3.2) Seed-42 product lacks log; reruns 1.4e-11; over-dispersion 1.28/4.25; why seed 42 (cheaper costed route); three-stream band built since.
- **M8** (§3.2) "Until 2026-10-11" exact-split central value: seed not pinned, 7e-15, reseed 0.18%/1.6%, chi2 values, 0.98%/12.2%/1.32, no matched covariance, switch after comparisons, exact-split studies not recomputed, `hist` backend.
- **M9** (§3.2) "The note and the article use three configurations" list: nominal, joint-test (400/31; fifteen-fold bias reduction; selected before the joint-test design), exact-split.
- **M10** (§3.2) (a)–(e) of the article; all five iterations, nominal capacity; "deterministic"; not combined; central values keep purity subtraction (produced before the bias was found).
- **M11** Table estimators-matrix.
- **M12** (§3.2) Hyperparameters fixed a priori (sklearn defaults; LightGBM matched); no search on data; post-hoc validation list.
- **M13** (§3.2) n = 5 versus Huang et al.'s 45; justification (0.026%).
- **M14** (§3.3) Higher-dimensional driver conventions: masking, fake-free step 1, no extra efficiency division, closure mirrors production.
- **M15** (§3.4) Cross-section formula; completeness; constants; units; self-test <1e-12; flux universes.
- **M16** (§3.4) Higher-dimensional flux constant and nucleon count.
- **M17** (§3.5) Binning grids and catch bins; 205 cells; bin-mapping file.
- **M18** (§3.5) No under/overflow by construction.
- **M19** (§3.5) Migration summary, median purity ~0.6.
- **M20** (§3.5) Muon vs hadron migrations.
- **M21** Figure migration.
- **M22/M23** (§3.6) Profile OmniFold, SPINUP, AUSSIE; scope.

## §4 Uncertainty quantification

- **U0** Four blocks; independence assumed; LightGBM and seed 42; historical 3D budget pointer; 4D no magnitude; pointers.
- **U1** (§4.1) July sweep, 44 bands/187 universes; seed 42 against the central value "since 2026-10-11"; re-selected laterals; Rvp1pi dropped, 43 bands + normalization.
- **U2** (§4.1) MAT centering, 1/N; ±1σ pairs; PPFX.
- **U3** (§4.1) Top bands; figure projection.
- **U4** (§4.1) Flux 1/Φ: flux band, combined median; earlier values pointer; normalization 1.4%; MINOS universes own flux 0.31%.
- **U5** (§4.1) Flux rank ≈ 1; ρ with muon band; 0.87–0.90; cross block not included.
- **U6** (§4.2) Bootstrap: 300 replicas, seed 42, three streams, shared events not assessed, background term 0.26, single draw, seed pinning, 4.1%, 1.001, offset 4.43/0.26, ratio 0.428, no causal advantage, earlier rebuilt streams pointer, coverage test of the band quoted then.
- **U7** (§4.2) Rebuilt band post hoc only; quoted block untested; no held-out re-test or design; truth equals prior.
- **U8** (§4.3) ML block definition, rank 4, 0.057%; interaction share; 71%; 0.30 of the earlier block, 0.685; reported-not-added terms; learner dependence 0.98%/12.2% in no block; ten-seed mean 0.99%.
- **U9** (§4.3) Exact-split reseed 0.18%/1.6%; spread unmeasured (duplicate of M8).
- **U10** (§4.4) Review found defects of the earlier budget: May sweep truth mismatch; July sweep provenance, seven universes 1.4e-11.
- **U11** (§4.4) Rvn1pi/Rvp1pi double count, 0.088%; dropped.
- **U12** (§4.4) EtaNCEL and NormNCRES responses.
- **U13** (§4.4) Background-template statistics (60 of 205); background stream; re-selected laterals; single-seed laterals; flux index identity; flux weights; earlier budget unchanged.
- **U14** (§4.5) Block sum assumptions; unified throw procedure.
- **U15** (§4.5) Run-period block: status, observation, construction, size, alternatives, limits, sensitivity reading.
- **U16** (§4.5) Block sum is an approximation; decomposition for attribution.
- **U17** (§4.6) Status of the 2D result; what validation would need; no coverage claim; three omitted items.
- **U18** (§4.6) Conventions: centering, 0.12–0.50%, 0.08–2.26σ, normalization.
- **U19** (§4.6) Miss-row approximation: two universes, seeds 42/43, not resolved, bound; retraining 1.28–1.29.
- **U20** (§4.6) NormDISCC zero; POT counting inferred; global exposure ratio bias numbers.
- **U21** (§4.6) Consumers check the stored cell set; list of limitations by block.
- **U22** (§4.6) Seed terms reported, not added: 0.076; six universes 1.24–1.33; 2p2h:0, MaCCQE:0; inferences; not recomputed.
- **U23** (§4.7) Two event-loop modes; re-selected laterals in the five-axis covariance; trace move and per-bin ratios.
- **U24** (§4.7) Scope of the re-selected replacement.
- **U25** (§4.7) 5D ML ensemble (split seed); estimator-seed scan 87.5% of "the candidate split-varied band" / "the band used in this note" (Q11); ~3%.
- **U26** (§4.7) Earlier 5D construction; the covariance used is the CV-centered later build.
- **U27** (§4.7) Per-universe background subtraction 0.28%/0.18%; 4D and extended-fiducial lack covariances.
