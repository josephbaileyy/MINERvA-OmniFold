# Reverse outline (before): §§6-8 at origin/main 8f2df745

One sentence per printed paragraph, caption or table. Ids are used by `ledger.md` and `changes.md`.

## §6 Results (`sec_results.tex`)

- **R0** (intro). The unfolded points of Fig. 7 carry the histogram bin errors (`hXSec2D`, `hXSec_pt`, `hXSec_pz`), not the §4 covariance; the published points carry the diagonal of the published statistical covariance; the budget is in Fig. uqbands / Table uq; Figs. ptslices-pzslices are statistical only "as their captions specify".
- **R1** (§6.1). Fig. 7 shows the 2D cross section and projections; total sigma is \sigTwoD (published \sigTwoDpaper).
- **R2**. The pT and p∥ shapes are explained by Q² scale and the NuMI ME flux peak; the theta<20° acceptance empties the high-pT, low-p∥ corner (19 unreported cells).
- **F-xsec** (caption). Unfolded 2D (Fig. 13 style) and projections; peak positions explained.
- **R3** (§6.2). The two results share data and systematics with no cross-covariance, so every chi² and standardized difference "here" is descriptive, "for orientation only; none is" a calibrated test.
- **R4**. Total within 1.1 % (ratio), median bin ratio, 5 % / 10 % bin fractions; indicative chi²/bin with paper covariance and combined covariance.
- **R5** (chi² caveat). Combined chi² double-counts shared flux/GENIE/MINOS; ours-only chi² is computed in the well-constrained subspace with a truncated pseudo-inverse; "we therefore quote" pulls, truncated result "and, as history", the exact-split regularization scan on an earlier covariance, rather than an unconstrained pseudo-inverse as GOF on its own (App. A.4).
- **R6**. Standardized differences are centred (mean, RMS 0.56); Figs. ptslices-pzslices compare with simulated truth in the published panel format; published data do not enter.
- **T-compare** (table + caption). Agreement quantities; standardized differences sub-1 sigma; chi² descriptive.
- **F-pull** (caption). Standardized difference map; descriptive, not a pull between independent results.
- **F-ptslices** (caption). Unfolded vs Tune v1 simulated truth sliced; histogram construction; "differ only by data versus MC prior; no published measurement is read"; only the panel format follows Fig. 13; statistical errors only, entering a descriptive per-panel chi²; where comparisons to published data are.
- **F-pzslices** (caption). The same sliced the other way; statistical errors only; no published measurement.
- **R7** (§6.3). Budget comparable to published: per-bin median 6.45 vs 6.85, integral 4.75 vs 4.61; flux largest band; universe block 0.87 / 0.83 shares; run-period raises median 6.04 -> 6.45; "its per-bin median is smaller ... and its integral larger" (repeat); flux band 3.75 vs 4.01 with origin undetermined, "leading hypothesis, not established" FHC-only file; flux band carries constraint weights (records citation, protected); stat + ML under a tenth of sqrt(Tr C).
- **R8**. Every block uses the LightGBM central-value estimator; relative uncertainties divide by the seed-42 central value of the universe sweep; relative to exact-split, median 6.410 %.
- **T-uq** (table + caption). Budget rows; caption: C and sqrt(Tr C); flux carries MAT's constraint weights; 43 bands of July sweep (44 bands, 187 universes) plus normalization; ML 5 seed settings; run period 3; combined 6.448 below published.
- **R9** (§6.4). Pull RMS (diagonal chi² 0.32) vs full 2.65: 8x in off-diagonal structure; shape not normalization (0.06 vs 544); eigenmodes (4-5 magnitude, 9.5 %, two of five, 73 directions -> 0.81, highest-p∥ modes poorly determined 4e-9, moderate-lambda at low pT, no band > 15 %); estimator band ~1 unit (3.66, 2.70±0.04, 2.64-2.75); exact-split distributed differently (5-6, 3 %, 1.42); 5->10 iterations +0.01; pointer to App. tension.
- **F-tension**, **F-tensionmodes** (captions). Spectrum and map; leading modes.
- **R10** (§6.5). Tune v1 under-predicts by ~9 % (0.91) in the low-pT peak; ancillary prediction vs both results; chi²/ndf 33.0, 29.8, 26.5; our unfold tracks data far more closely; published analysis compares NuWro, GiBUU, NEUT; OmniFold ensemble projections without re-unfolding; a new observable is a new unfold (§7).
- **F-model** (caption). Ours on published; Tune v1 dips below in the peak.
- **F-modelmaps** (caption). Ratio maps ours/Tune and data/Tune, scale 0.7-1.3, "(only this caption labels the panels; they have no printed titles)"; "neither map uses published data as its denominator or is flat near unity"; same deficit; close maps meaning; direct comparison pointers.

## §7 Higher-dimensional extensions (`sec_3d.tex`)

- **D0** (intro). Unbinned OmniFold adds a classifier column, no migration matrix; dimensional cost in training, coverage, sparsity, UQ; no practical IBU analog is the motivation; extend to d³sigma.
- **D1**. MINERvA binned triple-differential results incl. LE/ME QE-like (proton KE definition) differ from ours; distinction is the unbinned simultaneous CC-inclusive scalar formulation in 3-5 observables, not multidimensionality.
- **F-landscape** (caption).
- **D2** (§7.1). Truth Eavail "follows the code"; truth accessor `GetEAvailableTrue()` implements Eq.; species list; reco Eavail Eq. in `NewEavail()`; "the code applies no final non-negative clamp".
- **D3**. Both inherited from MAT-MINERvA; agreement is a "defence of the inherited position, not its provenance"; no unique definition; Rodrigues (4 of 5 species, excludes e±), Ascencio (open list), Henry/Su KE vs minerva-ml total energy; "we therefore do not claim generically to match".
- **D4** (paper-cited). 135 MeV not 139.57; "this was not corrected"; measured, not assessed against the 5D covariance projection; "materiality is not established, and this note does not call it immaterial".
- **D5** (Pipeline and binning). Event loop evaluates accessors over 12 playlists; "2D driver uses a three-column feature stack"; 3D Jacobian; flux per pT "broadcast"; Eavail binning with catch bin; completeness 1.0000.
- **D6** (§7.2). dsigma/dEavail falls from 2.19e-38 to 6.8e-41; most rate below 0.8 GeV.
- **F-eavail** (caption).
- **D7** (§7.3). Marginalizing must reproduce 2D; normalization +0.95 %, median ratio 1.0016; shape chi² 4.98 vs 2D values from ~4.4 % scatter; not a calibrated GOF.
- **F-eavail-marg** (caption).
- **D8** (§7.4). Reweight closure: +30 % Gaussian bump (0.3, 0.15) recovered: 1.048 vs 1.0485; marginal residual median 0.9999, SD 0.0006; per-3D-bin 3.2 %; 70x tighter than 4.4 %; norm < 1 %; metric 1.84 % vs 18.1 % (0.102), "no acceptance threshold fixed before the test is recorded, so it is not graded".
- **D9** ("What closes, stated exactly"). One shape (repeated parameters), same response; method neither manufactures nor destroys; supports reading scatter as data-MC structure; does not exclude other-deformation bias or test response mismatch; hidden-variable closure exceeds threshold at largest amplitude.
- **D10** (§7.5). GBDT vs NN; calibrated posterior requirement; reliability, Brier 0.25, AUC 0.537; MLP cross-check: 1.0078, 0.7-1.4 %; result not specific to classifier family.
- **F-calibration** (caption).
- **D11** (§7.6). Ancillary has only 2D model histograms; truth-level generation needed; samples generated; no digitized spectra.
- **D12** (list). GENIE 2.12.10 CV (gevgen, CH, DefaultPlusValenciaMEC splines but default list: no 2p2h; no MINERvA reweights; flux-reweighted); Tune v1 from event-loop truth (0.01 %); NuWro 21.09 on C; GiBUU 2019 on C, "built and run natively on the compute system without a container".
- **D13**. NEUT not included; each prediction normalized by its own flux-averaged total CC cross section.
- **D14** (Flux repair). "initially generated" from un-PPFX 50 GeV flux; densities sampled by content; suppression (flux-repair tag); repaired by exact per-event reweighting 0-100 GeV with 50-100 GeV supplements; FSI-dial, departure ratio, NuWro-shaped prior retain unrepaired; GiBUU reweight 0.9966; stops at 20 GeV; "rebuilt with unchanged figure producers on repaired inputs" (superseded values); Tune v1 unaffected.
- **D15**. Totals ordering GiBUU < NuWro < Tune < GENIE < data; 10-28 %; same order without catch bin; pT/p∥ shapes tracked; Eavail discriminates; NuWro and Tune suppress lowest bin; data above all four in the dip (lowest bin GiBUU reaches); excess invisible in 2D.
- **F-3dmodels** (caption). No error bars because the 3D covariance is not used.
- **D16**. Integrated (no catch bin) 7.2, 9.5, 12.8, 22.2 % below; no 3D covariance/chi²/p/significance quoted since projection computed but not used.
- **D17** (§7.7). Candidate model changes, generated and reweighted; central values only; no mechanism identified; low-recoil history (Rodrigues); tune built to absorb it; predictions fall short.
- **D18** (FSI). grwght1p reweight of 2M events; FrInel_pi <= 0.74 %, FrAbs_pi <= 0.82 %; pre-repair sample, cancels, not recomputed; integrated +-0.02-0.03 %; footnote (commented out of registry; 2026 confirmation; degeneracy); <1 % knob cannot bridge 8-36 %; limited to these dials; other models / proton FSI not excluded; QE-like FSI hint, different signal.
- **D19** (missing 2p2h). No MEC events (`mec=0`, 1.48e6, modes 11/22/66/0.9 %, supplement MEC-free); must be added; mode decomposition gaps in the dip; 70 % at <= 0.4 GeV; 45 % of QE (68-71 %), compared with sub-percent FSI.
- **D20** (Valencia). Default+CCMEC, 2M; MEC absent from gspl2root graph; normalization by non-MEC count, f_MEC 2.87 %; closes 52 % / 63 % (-7.2 -> -2.6 %); still short at [0.10,0.20); integral closer than Tune v1; Tune layers enhancement + RPA; consistent with, does not establish.
- **D21**. 2p2h leaves [1.5,3.0) unchanged; data/CV 1.09; exceed Tune v1; localized in §8.
- **D22**. "These comparisons do not identify a nuclear mechanism" (repeat of D17); NEUT two-body currents; 2p2h category is not a two-body current; dependence on primary interaction and transport.
- **D23**. Ascencio low-recoil deficit; our extension integrates q3: shape and direction only; consistent, descriptive; bin-identical values in §7.8.
- **F-modedecomp**, **F-mec** (captions).
- **D24** (§7.8). q3 chosen for its (Eavail,q3) plane and Ascencio comparability; `Getq3True()`, `RecoQ3()`; "both accessors run"; lateral shifts change q3, not Eavail, "so the event loop must store"; feature stack; q3 binning; 10 976 bins (4830 populated).
- **D25** (Marginalization check). Reproduces 3D spectrum and excess; ratios 1.21, 1.01, 1.16-1.23, 1.13; Tune v1 vs untuned GENIE; 4D->3D analog of 3D->2D.
- **D26** (What q3 adds). Structure in (Eavail,q3): q3-marginal 1.03-1.19; ratio rises with q3 in the dip; over-predicts low-q3 moderate-Eavail (0.66); excess at low Eavail and high q3; projections do not resolve; Tune v1 prior (q3-excess tag); no per-cell significances without corrected 4D covariance.
- **D27** (Why no 4D uncertainty). Requirements of a corrected 4D covariance (endpoints, 1/N blocks, seed, mean-centred throws, no jitter subtraction); single-pass outputs only for CV-selected events, re-selected loops "must bound" migration; no 4D magnitude or unified/block ratio.
- **D28** (Bin-identical comparison). 44-cell supplement with covariance; common grid; p∥ < 20 GeV/c restriction mirroring Ascencio "muon gate"; two super-cells; 9.2 % and 6.3 % above; no pulls/chi²; shared systematics treated as independent; "gate" differs by <~6 %; Eavail definitions differ: 11.0 % out of lowest bin; sign/location of residual; aggregate uncomputed; "unexcluded alternative explanation, not a refutation"; neither refutes nor validates at 10 %; 44-cell comparison "remains future work" requiring re-unfolding ("trivial") and sweep.
- **F-ascencio**, **F-q3excess** (captions).

## §8 Fifth axis (`sec_eavailw.tex`)

- **E0** (intro). Valencia closes half the low-recoil gap, leaving a high-Eavail excess over Tune v1 where 2p2h contributes nothing and FSI dials cannot reach it (covariance qualifications §9.x); external comparisons model-dependent: GiBUU 1.59 / 1.37; GENIE CV matches [0.8,1.5), low in [1.5,3.0) (1.09); W maps where the excess lies, no mechanism; model-dependence study establishes no bias-variance tradeoff or new total uncertainty.
- **E1** (§8.1, paper-cited). Truth W formula, struck-nucleon M (`GetTrueExperimentersW()`); reco W from q0, Q², average mass (`RecoW()`); external predictions use neutron mass and put W²<=0 in lowest bin vs analysis excluding them; 0.14-0.15 % change W bin; GENIE CV / NuWro without supplements: 0.1 % median, 2.2 % max, <= ~1 MC SE; not evaluated for GENIE+MEC; cannot be evaluated for GiBUU; W not invariant under lateral shifts, "the event loop stores" shifted W per universe "mirroring" q3; trees carry hadronic diagnostics; W edges; "passes the marginalization checks"; 0.11 % (1.0011), 0.3-1.5 %; dsigma/dW finite and non-negative in six bins.
- **E2** (§8.2). Table of implemented definitions "as used by the article"; symbols; exact Q² vs massless-muon Q² with beam-axis theta.
- **T-observables** (table).
- **E3**. W_reco exact function of (pT,p∥,q3) apart from the W²=0 clamp (1.5 %).
- **E4**. Truth W fixed only up to the 58.87 mrad beam-axis tilt (~1 mrad per event) and M: ±2 MeV (68 %), -49/+67 MeV (99.9 %), 0.25 % change bin, 0.15 % no real solution; five inputs share information; five simultaneous observables, not five independent measurements; article distinguishes inputs/support/observables; only reco W fixed; reco Eavail separate.
- **E5** (paper-cited). Near-degenerate directions of the joint-test metric consistent with this redundancy; origin not shown; information added by W not measured.
- **E6** (paper-cited). Negative truth W² excluded (4.9e-5); generators measure pT about their own neutrino axis: ±4 MeV (68 %); net cell effect not measured.
- **E7** (§8.3). Table of generator predictions; per nucleon of target; same fine-grid-to-cell map.
- **T-generators** (table).
- **E8**. Hydrogen lacks QE/2p2h/coherent; per-nucleon normalization leaves target difference; GENIE C-only vs CH +8.3 % (W<1.1), -2.2 % (1.1-1.4), +5.6 / -4.6 % normalization removed; NuWro/GiBUU contain such a difference not corrected in §10 as run; §10.x re-evaluates with correction.
- **E9** (§8.4). Projection minus Tune v1 shows excess mostly at high Eavail and high W, cell-integrated "(descriptive)"; no mechanism; regularization bias largest there; prediction is the OmniFold prior with full tune weight; untuned GENIE is separate; 57 %, 67 %, 83 %, 22 %; secondary at W<1.1, deficit 1.4-1.8; central values under nominal response; seed shifts small but share seed sensitivity not measured; response-mismatch closure designed, no result.
- **F-eavailWexcess** (caption).
- **E10** (§8.5). All four below data in the corner; spline-normalized flux-repaired predictions (flux-repair tag); one 5D histogram per generator; GENIE CV 2.76e-38 in both; GENIE+MEC uses the 3D normalization convention (superseded values).
- **E11**. Corner ratios 1.14, 1.14, 1.16, 1.61; integrated 1.11, 1.07, 1.15; contrast 1-7 % vs 16 % GiBUU (1.39, 2.22e-38 vs 3.07e-38); GiBUU 20 GeV limit; >20 GeV share 14.3-14.8 % corner, 6.8-7.4 % overall; removing them 9-16 %; supplying GiBUU 1.37 / 1.29; no distinct corner deficit; GiBUU lower everywhere.
- **E12**. Valencia leaves corner unchanged (1.142 -> 1.139); [2.2,3.0) ratios 1.12, 1.11, 1.13, 1.34; 1.4-1.8: GENIE 9.4-11.8 % above data; central-value ratios, no compatibility metric (§9 item 1).
- **E13**. Localization relative to Tune v1; data exceed all four overall and in the corner.
- **F-eavailWband** (caption).
- **E14**. SIS measurements context, not confirmation; location descriptive; future significance must account for selection; Ascencio cross-check 9.2 / 6.3 %, no covariance-based metric.
