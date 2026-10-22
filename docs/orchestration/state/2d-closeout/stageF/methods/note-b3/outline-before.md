# Reverse outline, before (origin/main b603f9cf)

One sentence per printed paragraph. Ids are used by `ledger.md` and `changes.md`.

## sec_5d.tex — §9 Five-dimensional estimator: validation and uncertainty

- **5.0** Roadmap of §9.1–9.6, the joint tests (§10) and App. C.
### §9.1 sec:val-fiveaxis
- **5.1a** Prior reweighting, response mismatch, finite capacity/iterations and calibration are separate mechanisms; background refinement repairs nominal recovery but signal-only departure failures show subtraction is not the whole residual.
- **5.1b** The 2D closures are signal-only, leaving background subtraction untested.
- **5.1c** Table 9.x lists the article's validation studies; all use the simulated detector response except the test calibration; letters refer to the estimator matrix. (Table unchanged.)
### §9.2 sec:val-negweight
- **5.2a** Background subtraction: purity pseudo-experiments give highest-W column 3.5–4.1% low and corner 1.7% high (0.22% without background; 0.36–1.07 sd); bias from purity, in no covariance, unknown on data; negweight-refined (deterministic LightGBM variant) gives 0.11–0.24% and 0.24% over 60 experiments; joint cells up to 1.0% high (14 se) vs −0.2%; mechanism unknown; on data median 0.36%, max 1.4%; method sensitivity not bias; not used for quoted central values.
- **5.2b** Generator-sized change: no recovery of the GiBUU/GENIE Eavail reweighting (0.70–1.33); GENIE flux "later found" mis-sampled, so a known-truth deformation not a measured difference; residuals median 9.7%, up to 74% (cell 0.8–1.5 GeV, W≥3, share not recorded), several percent in largest cells; q3 deformation up to 37%; signal-only reproduces both, so an estimator property (5 iterations, GBDT config); bias in no quoted uncertainty.
### §9.3 sec:val-departure
- **5.3a** Both steps behave as intended (reco match; 0.5% weight sums), yet the fold-back is worse than the true model; >99% of reco signal recovered, residuals median 5–11%, up to 74%; imprint small but significant.
- **5.3b** 30 iterations reduce the Eavail residual by 26% and it keeps falling slowly; q3 grows; a larger classifier and removing the missed-event regression do not help; no single cause; no change within the rules meets the predeclared recovery requirement.
- **5.3c** Comparison with exact binned unfolding: J cells, D1/W1/W3/q3 pooled with W2; IBU setup (exact efficiency, 10,499 cells, nominal prior); medians at 5 iterations; 15 of 144 tree-dominated, 2 identified, 0.014; 121 weakly constrained (CR >10%, median 31%); long iteration D1/W1/W3/q3 values; no convergence (9–34 of 109); scope (binned, signal-only, noise-free, fixed response, development truths, 376/232/144, 38%, muon projection uninformative); stacked list of non-claims; conclusion; records pointer.
- **5.3d** Higher-capacity refinement: underfitting causes the residual bias; candidate passes closure on 40 (2.7 se) and pooled pull 1.02 (not every functional); fails predeclared stability (0.8/2.6; baseline 0.8/2.5; family); explains the driver–development difference (≤1.2%); "a later study found" rounding spread inside the bootstrap (0.23%, 37%, <0.1 of total); reproducible only to that size; paired study addresses containment only for this candidate.
- **5.3e** Unfolding-model dependence on withheld shapes: median 2–6%, max 16–31%, within total in 20 of 42; nothing from it used for quoted results.
### §9.4 sec:gbdt-model-dependence
- **5.4a** The scalar estimator uses production LightGBM.
- **5.4b** No bias–variance tradeoff is established; three different quantities measured; benchmarks [Brenner]; regularization bias and intervals [Kuusela]; no literature result supplies the missing variance.
- **5.4c** Noise-free study setup (no background; 100/8, 400/31); repeat experiments with R; seed 42, 40 + 5×20, Poisson, MC splits; samples "have since informed development", no fresh validation.
- **5.4d** Fine-grid outputs integrated into J/H2/EW (109/27/39); H2 not nested; unsupported cells in the full-domain rate; "historical" interval assessment keeps 42 EW incl. three excluded by the "later" support rule.
- **5.4e** Label table (unchanged except one cell).
- **5.4f** Truth labels D1, W1, W2, W3 predate the flux repair; removing D1 leaves the rest uncorrected; q3 stress amplitude 0.3; response retained.
- **5.4g** Recovery: traces "without extension beyond the committed iteration ranges"; D1/W1 improve slowly; W3 J median 5.57→6.57%, max 32.9→44.8%; H2 3.42/3.68%; finite-scan disclaimer; q3 EW 4.99→6.42%; capacity at affordable k=5 lowers the proxy by 3% (J) and 8% (H2) against the required 20%; **iteration rule printed unscoped** ("only if they reduced the model dependence; none did"); no reporting definition qualified; no 5D measurement; "These outcomes stand."
- **5.4h** Reporting definitions RD1–RD3: envelope medians 12.0/9.6/13.4% (90th 38.6/22.5/39.2), GiBUU dominant; total-width target unattainable in RD1/RD3 alone and RD2 with 1.4% (≥11.0%); linear addition; model and recovery targets fail (≤5%; ≥75%, proxy ≤0.25 vs 0.31–0.63); RD3 fallback fails; no definition can meet the targets within the rules and budget; prior dependence 10–13%; joint tests "were pursued instead".
- **5.4i** Fig. gbdt-recovery caption ("scalar-5D", "partial checkpoints", "historical proxy").
- **5.4j** Variability: EW29 23.67%/0.56%, EW7 −6.81%/0.30%; small spread ≠ small bias; coarser cells estimate different integrals; no repeat ensembles at longer iterations/capacity.
- **5.4k** Fig. bias-spread caption.
- **5.4l** Historical intervals from 100 replicas of one experiment; EW41 15/40 (37.5%, [22.7, 54.2]); pooled pass cannot qualify; "a later" 160-experiment check with six widths; replica noise; no total coverage.
- **5.4m** Fig. coverage caption ("development reuse", 0 of 20, 16.8%).
- **5.4n** Paired perturbation study: 0.228% vs 0.368%; ratio 1.02; share 0.37; no double counting; does not change the stability failure, coverage, or transfer to the covariance.
- **5.4o** Prior sensitivity: correlation 0.92; 71/52/54%; envelopes 12.0/9.6/13.4 and without D1 11.2/4.3/9.9; no probabilities/covariance/bounds; truth not shown inside.
- **5.4p** Fig. prior caption.
- **5.4q** "A decisive next measurement"; separate tasks; physical nuisances; "No new ensemble enters this synthesis"; objective unmet.
### §9.5 sec:coverage-5d
- **5.5a** Independent-truth test (1,200 over three truths) failed futility at nominal and the rate reduction; no coverage claimed.
- **5.5b** Interval definition (divide by 1+β; se of β in quadrature).
- **5.5c** Failure threshold (UCB < 0.66 / 0.94); the second truth ("labelled the Eavail tilt in the records") and its weight 0.900–0.906.
- **5.5d** Under the change 51 of 153 fail at 68% (as low as 0.060), 42 at 95%; at nominal 2 fail at 95% (lowest 0.850).
- **5.5e** Why the intervals miscover: rate recovered (−9.58 vs −9.56%, 0.74); not too narrow (1.15σ; 0.06–0.22); purity removes the absolute background (60 of 3.2M); residual W-graded bias (0.2/0.4/0.7–1.1%, 1.3–2.6 sd, 0.16–0.43%); removal restores 0.62–0.82/0.92–0.99; inferred by Gaussian fit (EW17 +1.04/+1.05%); source not established (0.111 f_bkg); deciding test not run.
- **5.5f** Pointer paragraph "A scoped response-information diagnostic" (content already merged into 5.3c).
### §9.6 sec:eavailw-construction
- **5.6a** Status: cv variant, 42-cell projection, checksums in records; used although it fails its specification; null bound required before production, "production had already taken place", metadata says not passing / not to be used; use limited to this file, not the two companions; the superseded direct block sum is quoted nowhere (records pointer).
- **5.6b** Construction: M C M^T of the corrected statistical covariance; corrected endpoints; re-selected event loops bound migrations; Eqs. zassembly, zinflation.
- **5.6c** Definitions of v_blk and v_uni^cv; g=1 "pins by declaration"; V/R/A disjoint over 45 bands; sweep-block transfer "made conditional (2026-07)"; PSD, never below baseline; rank-N swap not PSD.
- **5.6d** Centering: MAT mean-centered blocks; CV-centered inflation; Eq. zcentering; CV keeps the mean shift; deliberate; mean variant 7.13% lower; "must be read and checked in its metadata, never inferred from its path".
- **5.6e** Projection: C_EW = M C_Z M^T, 42×N; bin-width entries; integration; 7×6 C order; no dropped cell; symmetric; masks byte-identical; "We pair ... by checksum identity"; same bytes; numerical agreement corroborates.
- **5.6f** Conditioning: λ extremes, 2.9e-15, 3.4e14; no negative eigenvalue but at noise floor; sign uninformative; rank depends on cutoff; 26/36/41/42; bold "A bare rank 36 should not be quoted"; inverse requires declared regularization.
- **5.6g** What the covariance supports: four measurements (items 1, 2, 4 companions; 3 this file). Item 1 seed sensitivity vs limit (set 2026-09-18, 5.6% precision, tolerance not threshold, diagonal legs pass). Item 2 not resampling noise (40/80/160; floor; exponent; three limits; maximum over offsets). Item 3 five pinned bands. Item 4 central-value shifts.
- **5.6h** Seed magnitude criterion not computed for this covariance; companions' outcomes are not its outcomes.

## app_statmethods_nd.tex — App. B

- **B.0** Contents of the appendix.
- **B.1a** 2D justification does not transfer; an earlier 5D covariance (10,694 bins, rank 263, infinite condition; 4825-bin projection rank 263); ~45 bands cannot span; no defect; 40×/18× understatement.
- **B.1b** ndf rule and declarations (i)–(v); records pointer rank-inversion.
- **B.1c** "Why declaration (v), and why it does not yet mandate a correction": (i)–(iv) omit ensemble sizes; inverse biased upward; factors (N−p−2)/(N−1), (N−p−2)/N; N=160, p=100, 0.363, 2.76; inflates χ².
- **B.1d** No generic correction; sum of rank-one blocks; assumptions; "to be decided ... once declaration (v) has recorded".
- **B.2a** "The methodological synthesis" uses saved products; integration conventions; J and H2 boundaries; units; support rule (≥1000); 109/27/39; EW11, EW36, EW37 "omitted only from the later" summaries.
- **B.2b** r, mean, s definitions; truth varies with split; RMS; t and χ² intervals; no simultaneous claim; deterministic traces carry no band.
- **B.2c** "Historical" interval diagnostic (100 replicas of experiment 700000); ±σ, ±1.96σ; table contents; no finite-replica propagation; no pooling; EW7 and "the previously identified failing corner" EW41.
- **B.2d** Rounding study (half a float32 ulp; 20 jitters, 50 pairs; s_base, s_boot, s_pair); ratio, share; √2; predeclared containment ([0.7,1.4], 95%); all cells meet; no coverage proof.
- **B.2e** Prior sensitivity d, h; no probability model; **reduction package** (per-cell values, identities, exclusions, "metadata-free checkpoint prefixes", "committed ranges", "the analyst numerically cross-checked", "no fresh independent scientific review ... is claimed").
- **B.3** Extended-fiducial band and pull fractions (unchanged).
- **B.4a–c** Inference from unfolded events (unchanged except two sentences: "with no new validation result here"; "not replace the decision to use it").
- **B.5** FWER derivation (moved verbatim from the article; unchanged).

## app_negweight.tex — App. C

- **C.0** Purity weight; negative-weight injection is the unbinned version; agreement quantified; Canelli; extended-fiducial.
- **C.0s** "Scope of the numbers": no quoted uncertainty; "Every result in this note uses the binned purity weight"; equivalence study; no production path, no default change; ratios are diagnostics; two provenance limits; records pointers.
- **C.1a** Estimator: step 1 classifier, r*, the two ρ₁ choices (Eqs.).
- **C.1b** The two differ within a bin; agree on bin masses under the sieve; bin-integrated estimand, not the continuous one (records pointer "superseded values"); support identical.
- **C.1c** The floor: max(0,·) vs bounded output; ill-posed; Stay Positive then zero clip; classifier-dependent.
- **C.1d** Histogram backend agreement \nwMedianBin; backend differs from LightGBM and exact-split; transfer assumed.
- **C.1e** Raw signed weights destabilize exact-split (×\nwSpRawMax); clipped refinement recovers \nwSpMedian (\nwSpWithin within 5%); robust across estimators.
- **C.2a–d** Binned limit derivation (Eqs.), failure where D<B, literature, consistency check.
- **C.3** Closed-form toy.
- **C.4** 2D comparison, table, figure.
- **C.5a–b** Propagation through systematics and statistics; conclusion, purity default, designated extended-fiducial baseline.
- **C.6a** Validation does not make the choice arbitrary.
- **C.6b** Standard chain uses purity (169 + 18 + 10 unfolds); identified differently for existing and current production.
- **C.6c** **"Existing endpoint unfolds from 2026-07 are identified by elimination"** (job scripts, default, log signature, predate); current production pins (bkg-mode-pins); explicit option; recorded; provenance not physics.
- **C.6d** **"This is a recorded choice, not a silent default"**: two grounds; "That consequence decided the choice; cost did not"; obligation to revisit before submission; "nothing in this subsection meets that obligation".
- **C.6e** The quoted σ_ext used purity (records pointer); 2026-06-10 battery; ten endpoint unfolds purity controls; no refined production; ledger check; remains σ_ext.
- **C.6f** Extended-fiducial designated negative-weight + Stay-Positive; code fixes it; check stops the run; "We claim an internally consistent ... Uniformity ... not claimed."
- **C.7a** Measured size (1–2%; operands of the two ratios; real-data totals).
- **C.7b** Displacement across universes (~0.1%).
- **C.7c** Scope: 2D only; not a theorem (records pointer); no continuous/5D equivalence; spot check only.
- **C.7d** Limits of the 5D evidence: no 187-universe 5D comparison; spot check numbers; supports quoting purity; not irrelevance; LightGBM safe, not immaterial.
- **C.8a** Pointer to the five-axis validation (§9.1).
- **C.8b** Purity bias 8–12 sd; within-bin shape term measurable; "direct evidence for the obligation"; cheapest estimate.
- **C.8c** Refined subtraction (3e-6, 0.01–0.05%, 1.66→0.24%, closure fails, sign pattern, does not follow Eavail, no coverage test; obligation open).
- **C.8d** Refinement capacity (4%→1.7%, >80%, 20 + 40 pass; halves not the cause).
- **C.8e** **"Background treatment chosen, its obligation not yet met; covariance choice separate."** Nothing selects a covariance; re-selected lateral component built; one covariance used under the exception; "Neither fact follows from or is needed by this appendix"; independent; removes one blocking decision (p4-verifier).
