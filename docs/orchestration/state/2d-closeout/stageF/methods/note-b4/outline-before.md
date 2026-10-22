# Reverse outline, before (origin/main 8f2df745)

One sentence per paragraph. Ids are used by `ledger.md` and `changes.md`. Line numbers are of the files in `before/`.

## §5 Validation of the two-dimensional measurement (`sec_validation.tex`)

- V1 (4-14) Defines truth, prior, response, closure, bias and coverage, and says numerical repetition checks neither calibration nor the physics model.
- V-T1 (16-35) Table of the four validation questions (closure, miss completeness, iteration stability, fixed-truth coverage) with targets, samples and conclusions.
- V2 (37-52) Three 1A/LightGBM/5-iteration closure families with residuals and thresholds; the A=0.30 hidden-variable arm exceeds its threshold.
- V3 (54-60) The 2D Gaussian-bump closure passes the unbinned-unfolding guide's recovery test (1.69% of 17.2%, ratio 0.098).
- V4 (62-66) The naive data-versus-prior chi2 gives truth > reco, as expected; the full-covariance comparison is elsewhere.
- V5 (68-71) Closure tests validate the estimator and assign no non-closure uncertainty; one would need a predeclared suite.
- V6 (73-76) No test uses a mismatched detector response; App. response-mismatch defines one, not run; the five-axis estimator is validated in sec:val-fiveaxis.
- V7 (78-90) A split-sample width check gives only conditional precision; validated total uncertainties for all 205 bins have no route with current inputs; what they would need; a limit of the evidence, not of 2D unfolding.
- V8 (97-106) §5.1: all closures keep the simulated MINERvA response; reweighting to another generator tests unfolding, not the detector; an ordinary closure is an identity check.
- V-T2 (108-171) Table of closure tests by what they change (2D to 5D, background, generator, hidden q3, response mismatch); the W row ends "Replaces an earlier null run".
- V9 (174-200) Why injected bumps close while generator-shaped tests fail: deformation, metric, iterations; the 5D W test passes only marginally and narrowly.
- V10 (215-217) §5.2: the test asks whether the band quoted when it ran covers a fixed truth; design fixed in advance.
- V11 (222-227) Toy construction: Poisson pseudo-data, production Poisson(1) MC bootstrap, the band's estimator at a fixed seed; T is the unfluctuated truth.
- V12 (229-234) Definition of z, C_k, the nominal windows and the interim stopping rule.
- V13 (236-247) Result: C1 nominal, C2 below its window, pull RMS; the band fails and the study stopped; independent recomputation reproduces it.
- V14 (249-250) Positive control at x0.7 and x1.3 is flagged in both directions.
- V15 (252-262) Post hoc per-bin pattern: too wide in some bins, too narrow in others; where the narrow bins are.
- V16 (264-274) The band's replicas divide by a bootstrapped completeness; the amended secondary analysis overcovers; attribution rule and its partiality; the term was removed on 2026-10-06 and the band rebuilt; the quoted block is a different 300-replica ensemble; result is for the earlier band.
- V17 (280-296) Post hoc rescoring against the rebuilt band: tail undercoverage removed, band wider than toy scatter; excess in the data-statistics part, cause unknown; single-toy diagnostic; held-out re-test not run; split-sample checks cannot establish coverage.
- V18 (310-320) Scope list of the coverage result.
- V19 (325-335) C2ST AUC 0.535 -> 0.501, descriptive only; no cross-fitting; calibrated unbinned GoF open.
- V20 (338-351) The 200-toy same-ensemble: construction; stored truth fluctuates so its mean is not an independent fixed truth.
- V21 (353-364) Pull definitions and results (68.71%, mean |r|, signed mean, 97.6% of bins above 65%): residuals approximately normal.
- V22 (366-369) With sigma from the scored toys these are not coverage; no coverage number; the fixed-truth test is the coverage statement.
- V23 (371-376) 5 vs 10 iterations, hist vs exact-split backends, efficiency reproduces published Fig. 5.
- V-F (377-384) Efficiency figure.

## Guide to the appendices (`app_guide.tex`)

- G1 (6-17) Three groups of appendices.
- G2 (18-21) Records are in a separate internal document cited by tag or heading.
- G3 (23-51) Labels used in the repository: lgbm/exact/hist, purity/negweight/negweight-refined, cv/mean, MNV101_ACTIVE_UNIVERSE, July/May sweep, J28.

## App. A Statistical methods and the 2D comparison (`app_statmethods.tex`)

- A1 (5) List of contents, pointers to App. statmethods-nd and §5, chi2 convention pointer.
- A2 (11) Eq. chi2 needs C^{-1}.
- A3 (14-24) Cholesky and the ridge jitter epsilon = 1e-12 Tr C / n.
- A4 (27-29) Rank at most N-1 for N <= n (superseded 50-replica bootstrap); 300 replicas full rank; systematic rank limited.
- A5 (32-54) Pseudo-inverse via SVD; np.linalg.pinv at default rcond 1e-15; the n sigma eps convention belongs to lstsq/MATLAB.
- A6 (59-62) Table of variance sources introduced.
- A-T1 (64-108) Variance-source table (training seed, bootstrap, universes, run period, MAT reference, block sum).
- A7 (112-127) Training-seed block from five seed settings x 20 replicas; values; the ten-seed scan it replaces is in the records.
- A8 (135-160) Coherent bootstrap: three sub-RNGs, Poisson(1), covariance Eq. bootcov; N=300 varies only the bootstrap seed.
- A9 (162-166) Bootstrap values: 0.061%, 0.684%, p84 1.712%, 4.1% relative SE.
- A10 (175-187) Multinomial -> Poisson limit.
- A11 (191-199) July sweep 187 universes/44 bands; Rvp1pi dropped; pair bands; re-selected event loops for the five kinematic bands.
- A12 (202-239) MAT mean-centred 1/N per-band covariance; pair reduces to rank 1; 1.4% norm rank-1; bands independent except Bashyal.
- A13 (241-249) Band sum is linear; OmniFold is not; unified throw; pointers.
- A-T2 (262-286) Top band medians.
- A14 (289-301) Grouped medians (Fig. 6/7 producer grouping); muon energy and MINOS efficiency dominate.
- A15 (306-335) ±1σ pair: mean-centred vs CV-centred; per-band blocks are mean-centred.
- A16 (338-341) Scope of mean-centring: the five-axis covariance keeps the CV-centred term.
- A17 (345-347) MAT defines the construction the paper leaves unspecified.
- A18 (350-372) What Ruterbories 2021 Sec. V says and does not say.
- A19 (375-392) MAT per band; byte-for-byte check (unweighted, before flux fix) and the weighted 3.4e-16 check of the quoted block.
- A20 (396-402) GetTotalErrorMatrix sums bands; no regularization; ranks 120 vs 137.
- A21 (404-416) Upstream references for band amplitudes.
- A22 (420-441) Block-sum combination of four blocks; C^ML negligible.
- A-T3 (443-464) Component traces and medians.
- A23 (465-475) Combined entries are read values; 6.410% for exact-split; blocks are LightGBM ensembles; 6.040%.
- A24 (483-486) The tables give the quoted blocks; pre-flux-fix predecessors retracted.
- A25 (491-492) §A.3 supports §results-compare.
- A26 (497-503) 205 of 224 cells reported; 19 suppressed.
- A27 (505-515) 185-bin strict-interior mask (origin in records); canonical metric is 205 bins.
- A28 (520-535) Eq. chi2 with pinv; options.
- A29 (540-548) ndf = 205 supported by the truncation scan; specific to 2D.
- A-T4 (550-562) Worked example table.
- A30 (565-572) Log-normal definition; only this one reproduces the value; alternatives.
- A31 (577-582) Adding the OmniFold budget lowers the distance; "That number is a descriptive distance ... Three things have to be said with it, and none of them is repaired by a disclaimer placed elsewhere."
- A32 (584-594) (i) Missing cross-covariance prevents calibration.
- A33 (596-602) (ii) A near-one realization is not evidence; the exact-split 1.47 is not evidence against.
- A34 (604-613) (iii) Coverage untouched; per-bin claims; log-normal depends on definition.
- A35 (618-622) External statistical floor of the quoted combined chi2 (StatOnlyCov; 0.428; power; declaration (v)).
- A36 (624-633) Trace share alone cannot justify this; without it 23.57; shared-systematics problem remains.
- A37 (635-657) Edge-bin sensitivity table (exact-split, paper covariance only).
- A38 (662-686) Pull distribution: 0.042/0.398; exact-split 0.051/0.405; RMS < 1 descriptive; paper-only values.
- A39 (691-723) Shape-only chi2 with Jacobian: 3.596; 1.0111 scale; 94% within 10%.
- A40 (728-761) Rank 137/205, cond; band count limits rank; paper systematic rank 120; with bootstrap rank 205.
- A41 (763-791) The obstruction is statistical: 0.428, 23.57/23.23; three candidate explanations; split bootstrap separated two from MC omission, not from the third.
- A42 (793-802) Resolution (data/MC split bootstrap): recorded in the records; 0.428/0.435; fixed-truth test cannot decide.
- A43 (806-810) Ours-only chi2 is regularizer-dependent; truncated-spectral convention of the 3D generator scan.
- A44 (812-839) Regularization scans (historical): no stable single number; report pulls and scan.
- A45 (841-855) Bootstrap/paper-stat double count; subtraction over-corrects; double-counted distance retained.
- A46 (857-872) Bashyal block rederived; preserves rank; collaboration confirmed the truncated-spectral convention (no published reference).
- A47 (874-886) What is reported.
- A48 (891-899) Tension derivation made for the exact-split cross-check (quoted until 2026-10-11); LightGBM differences.
- A49 (901-916) The paradox: diagonal chi2 0.366 vs 3.661.
- A50 (918-943) Eigenmode decomposition: broadly distributed.
- A51 (945-952) Shape contribution dominates.
- A52 (954-976) Where it lives (with the POT footnote).
- A53 (978-1008) Estimator and iteration: ~1 chi2 unit from the GBDT estimator; iteration negligible.
- A54 (1011-1020) Conclusion of the tension anatomy.
- A55 (1025-1035) Closure tests detect bias ("how much the unfold wobbles"); thresholds above the 0.166% floor of the ten-seed scan.
- A56 (1039-1046) Truth-reweight closure procedure; >=30x below threshold.
- A57 (1050-1067) Hidden-variable procedure; kappa_leak.
- A58 (1069-1081) Hidden-variable result: 0.113; A=0.30 exceeds; bound holds to A~0.26; open sensitivity.
- A59 (1085-1101) Alternative-model closure.
- A60 (1106-1110) Audit-trail summary.
- A-T5 (1115-1140) Audit trail of the combined distance.
- A61 (1144-1175) Standing assumptions (six items).
