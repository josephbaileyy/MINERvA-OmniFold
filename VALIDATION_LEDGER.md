# MINERvA-OmniFold Validation Ledger

## 2026-07-12 uncertainty-remediation quarantine

The entries below preserve the exact historical record, but the old 4D/5D/FPS
unified-throw adoptions, PET statistical/total budgets and precision
comparisons, `(E_avail,W)` covariance, and every significance derived from
those objects are **SUPERSEDED AND UNQUOTABLE**. Their construction used one or
more of: one-sided endpoint interpolation, CV centering, varying estimator
seeds, scalar jitter subtraction, frozen PET weights, incomplete statistical
projection, or CV-support-limited lateral selection.

Corrected 5D GBDT non-lateral/support-limited candidate products are recorded
immediately below, but final adoption waits for the selection-complete lateral
replacement. The recoil-PET budget is quarantined pending a joint
nuisance--retraining construction and selection-complete detector samples. The
4D/FPS replacements and covariance-dependent generator significances remain
quarantined. Central cross
sections, closure tests, dimensional anchors, and the finalized Phase-18.2 2D
result were never invalidated by this quarantine.

## 2026-07-14 corrected 5D GBDT covariance — CANDIDATE; final lateral replacement pending

- The full background-aware re-quote contains 169 vertical universes, 18
  detector/lateral universes, and one matched CV. Relative to the
  background-frozen build, `C_syst` changes by **+0.14%** in sqrt-trace and the
  combined systematic+statistical+ML covariance by **+0.30%**. This closes
  KNOWN_ISSUES #13 as a numerically negligible refinement, not a central-value
  change.
- On 10,694 reported 5D bins, the corrected block sum has systematic
  sqrt-trace **4.3515e-38** and median relative uncertainty **13.235%**; after
  adding corrected statistical and split-ML blocks the corresponding values are
  **4.3578e-38** and **13.359%**.
- The corrected unified-throw candidate uses actual asymmetric endpoints,
  one fixed estimator seed, throw-mean centering, MAT `1/N`, exact manifests,
  and no scalar jitter subtraction. The candidate mean-centered covariance is PSD
  with sqrt-trace **5.8077e-38**. The joint mean shift has norm **1.654e-38** and
  is reported separately. The CV-centered PSD variant, sqrt-trace
  **6.2367e-38**, is retained as a conservative alternative rather than the
  headline.
- Artifacts:
  `nd-unfolding/uq_5d/universe_stage2_5d_bkgaware/uq_universe_5d_covariance_combined_bkgaware{,_uthrow,_uthrow_cvcentered}.root`
  and `uq_universe_5d_summary.txt`. The dedicated estimator-only seed scan is an
  auxiliary robustness check and is not part of this candidate budget.

## 2026-07-14 recoil-PET 5D uncertainty campaign — QUARANTINED

- All five blocks share the exact corrected background-subtracted PET nominal,
  10,550-bin reported mask, and CV. The final PSD block sum has sqrt-trace
  **3.8777e-38** and median relative uncertainty **15.103%**. Its width-weighted
  4D marginal is PSD on 4,790 bins with median relative uncertainty **12.365%**.
- Component `(sqrt-trace, median relative uncertainty)` values are:
  `C_syst` (**2.9704e-38**, **7.584%**), `C_retrain`
  (**2.1896e-38**, **4.181%**), `C_ML` (**8.0364e-39**, **2.348%**),
  `C_stat` (**7.4390e-39**, **7.851%**), and `C_lateral`
  (**4.6902e-39**, **2.111%**).
- The predeclared six-band targeted retraining test found all six material.
  `C_retrain` is rank six and the identical-seed null response is only **0.008%**
  of the CV norm. However, decomposing the full endpoint shift into
  `x_frozen-CV` and `x_retrain-x_frozen` does not make their covariances
  independent. Adding the two covariance matrices omits both cross terms. The
  reported total is therefore a historical diagnostic, not a publication
  covariance.
- The detector block propagates shifted detector weights/observables through the
  corrected nominal point-cloud sample with the PET map frozen. It is therefore
  a detector-response block for the completed campaign, not a claim of
  per-universe PET retraining or shifted-cloud membership regeneration.
- The current statistical block contains 20 coherent replicas. This is complete
  for the present campaign, but the pre-publication plan is to increase it to
  100 replicas; that expansion has **not** been run.
- Artifacts and exact checks:
  `nd-unfolding/products/pet/bkgsub/pet_ctotal_bkgsub_5d_final.summary.json` and
  `pet_cretrain_bkgsub_5d.summary.json`; array products use the matching `.npz`
  names. These artifacts close the historical recoil-only campaign but are not
  quotable uncertainties. The full-event replacement requires joint
  varied+retrained endpoint shifts, a fresh statistical/ML budget, and
  selection-complete per-lateral samples.

Validation pass started 2026-06-06. Scope: whole repository, with priority on
technote-cited active results. Criterion: recompute from existing ROOT/NPZ/text
outputs where possible; rerun heavy production only when a check fails and the
smallest required rerun is clear.

## Delta pass 2026-07-02 (backfill of undocumented 2026-06-14 → 2026-07-01 work)

Numbers below are read directly from the saved artifacts (no rerun). This
pass backfills documentation for the PET capstone campaign, the truth-cloud
coverage fix, the 5D GBDT systematic covariance, and the PET 5D uncertainty
comparison — all of which had landed on disk but were never written up.

- **Truth-cloud coverage fix, full-spectrum projection (2026-06-28/29,
  commits 8cc54e9/8e79ebf/ddf4a7d)**: **PASS**.
  `nd-unfolding/products/pet/fullcloud/pointcloud_projection_summary.json`:
  event census N=**32,849,103** (pass_truth_and_reco 20,404,292,
  truth_only_miss 12,444,811); **has_cloud 32,848,929 / empty_cloud 174**
  (99.9995% coverage, up from ~72.6% pre-fix). E_avail truth-cloud
  projection vs the published unfold: frac_within **0.98784** (98.78%), RMS
  **0.08222**. W projection: frac_within **0.19694** (19.7%), RMS
  **3.23862** GeV — the cloud is NOT usable for a W projection (12-hadron
  truncation is fine for E_avail, not for W). Saturated
  (exactly-12-hadron) rows: **frac_saturated 0.023074** (2.31%,
  757,968/32,848,929 events), median E_avail bias in saturated rows
  **−0.035493**.
- **5D GBDT systematic covariance campaign (completed 2026-06-29)**:
  **PASS**. `nd-unfolding/uq_5d/universe_stage2_5d/uq_universe_5d_summary.txt`
  (written 2026-06-29): reported bins **10694/65856**; total systematic
  **sqrt-trace 4.3391e-38, median 13.298%/bin**; combined (+stat+ML)
  **sqrt-trace 4.3460e-38, median 13.433%/bin**. Per-band-group
  sqrt-trace sums: Models **9.013e-38**, Hadronic response 3.885e-38,
  Muon reconstruction 2.742e-38, Normalization 4.507e-39, **Flux
  3.875e-39**. Adding the W axis flips the dominant systematic group from
  Flux (2D/3D/4D) to GENIE Models/2p2h — Flux is now sub-dominant by more
  than an order of magnitude in trace. Coda: the 5D unified-throw check
  subsequently landed and was ADOPTED 2026-07-01/02 (jitter-corrected
  trace ratio **1.539**, far milder than 4D's 2.01); adopted covariance
  `uq_5d/universe_stage2_5d/uq_universe_5d_covariance_combined_uthrow.root`,
  adopted median per-bin fraction **13.69%** over the 10550 bins PET also
  reports (per `products/pet/unified5d/pet_vs_gbdt_uncertainty_5d_summary.json`).
- **PET 5D vs GBDT uncertainty comparison (2026-06-29/30) — INDICATIVE,
  2M-train anchor**: **PASS (comparison recomputed from saved
  covariances)**.
  `nd-unfolding/products/pet/pet_vs_gbdt_uncertainty_5d_summary.json`
  (block-sum, both engines): on the **10550** common 5D bins (GBDT reports
  144 extra), median per-bin fractional uncertainty **14.8%** (PET
  headline: clean block-sum C_syst+C_stat+C_ML + PET-native shifted-W
  lateral) vs **13.3%** (GBDT); median ratio **1.1921**; PET tighter in
  only **38.4%** of bins; vertical-only (no lateral) PET reads **14.7%**
  (not lateral-driven). **VERDICT: WORSE** — contrast the 4D verdict,
  COMPARABLE (11.8% vs 13.4%, ratio 0.9496, PET tighter in 53.6% of 4796
  bins; `pet_vs_gbdt_uncertainty_summary.json`). Both PET covariance is
  anchored to the 2M-train reweight (`pet_weights_full.npz`), which still
  carries the PET-vs-GBDT CV training gap, so this comparison is
  indicative of the method, not a final full-stats uncertainty.
  **FLAGGED, NOT ADOPTED**:
  `products/pet/pet_5d_covariance_combined_unified_wlat_summary.json`
  reports PET's own unified-throw study (160 throws, frozen reweighter)
  gives sqrt-tr unified **1.5933e-37** vs sqrt-tr block **2.7897e-38** —
  **unified/block ratio 5.711** (median per-bin sigma ratio 1.216), far
  larger than the GBDT-side 5D ratio (1.539) or the qualitative 4D
  precedent. This is a frozen-reweighter lower bound (omits the
  retraining-response nonlinearity) and is explicitly not adopted into any
  published PET 5D uncertainty pending investigation of why it is so much
  larger than the GBDT-side check.

## Delta pass 2026-06-09 (post-06-06 results, for the analysis note)

All results that landed after the 2026-06-06 pass, recomputed from saved
artifacts on the login node. All PASS; no rerun required.

- **(E_avail,W) W-resolved lateral covariance (2026-06-13, interactive job
  54391533)**: **KNOWN_ISSUES #4 CLOSED.** Rebuilt the 42-bin (E_avail,W)
  covariance with the lateral block computed DIRECTLY from the 18-universe 5D
  detector sweep (9 bands × ±1σ: Muon_Energy_MINERvA/MINOS, MuonResolution,
  MinosEfficiency, BeamAngleX/Y, GEANT_Neutron/Pion/Proton) + matched CV,
  re-inferred on the five-axis grid — replacing the 4D-marginalised transfer.
  W-resolved lateral median **2.36%/bin** (√tr 9.52e-40) vs transferred
  **1.80%** (7.99e-40): the proper block is LARGER, so adopted. C_total √tr
  8.667e-39, median **14.9%/bin**; sweep-CV vs frozen-CV marginal
  max|ratio−1|=**0.007** (validation gate). Full-cov generator significances
  (published transferred → W-resolved): full plane GENIE-CV 16.7→**19.3**σ,
  +MEC 16.1→19.0, NuWro 31.2→35.9, GiBUU >37→>40; high-W DIS corner (12 bins)
  GENIE 9.0→**8.9**, +MEC 9.2→9.2, NuWro 10.5→**15.6**, GiBUU 18.2→**22.4**σ.
  The W-resolved covariance DEEPENS the DIS-corner deficit for NuWro/GiBUU and
  leaves GENIE essentially unchanged — the physics conclusion strengthens.
  Technote (`sec_eavailw`, `sec_execsummary`) + table
  updated and rebuilt (64 pp, clean). Artifact
  `products/5d/eavailW_covariance_wlat.root` (pre-fix file untouched).
- **Merged 5D omnifile integrity**: **PASS**.
  `nd-unfolding/runEventLoopOmniFold_5D_MEFHC_universes_full.root` (133 GB) has
  no ROOT recovery flag and all four trees match the sum over the 12
  per-playlist inputs exactly (`mc_truth_denom`/`mc_signal_reco` 32,849,103;
  `mc_background` 658,227; `data` 4,119,797). The cancelled `hadd5d_uni` job
  54221741 (2026-06-09, 0s elapsed) was a duplicate submission, not a failure.
- **4D unified-throw adoption**: **PASS**. `uq_4d/unified_throw_cov_4d.root`:
  160 throws, sqrt-tr unified `3.3924e-38` vs block `1.6858e-38`, ratio
  **2.012** (documented ~2.01). Adopted combined covariance
  `uq_4d/universe_stage2_4d/uq_universe_4d_covariance_combined_uthrow.root`:
  4830 reported bins, exactly symmetric, PSD (min eig at numerical zero,
  −2.3e−16 of max), stored `sqrt_tr_new=3.8529e-38` equals the recomputed
  sqrt-trace; `sqrt_tr_old=2.0996e-38` matches the pre-adoption block sum.
- **(E_avail,W) covariance**: **PASS**. `products/5d/eavailW_covariance.root`:
  42 bins (7×6), median rel sigma **14.79%**/bin; sqrt-traces C_syst
  `8.578e-39`, C_stat `7.912e-40`, C_lateral `7.992e-40`, C_total `8.652e-39`.
  CV cross-check vs the frozen 5D product: E_avail marginal max rel diff
  **0.080%**, W marginal max **0.118%** (the "~0.1%" claim).
- **(E_avail,W) generator significances**: **PASS**. Recomputed from the saved
  covariance + generator files: high-W DIS corner (E_avail≥0.4, W≥1.8 GeV, 12
  bins) z = **8.99 / 9.20 / 10.52 / 18.22** for GENIE-CV / GENIE+MEC / NuWro /
  GiBUU (documented 9.0/9.2/10.5/18.2). Data integrated sigma `3.070e-38`;
  GiBUU integral **2.223e-38** = most deficient (regenerated GiBUU, array
  54190920).
- **PET absolute milestone**: **PASS**. PET absolute total `2.7958e-38` vs
  GBDT 4D total `3.0665e-38`, ratio **0.9117**; the `_hi` retrain gives
  `2.7507e-38` (0.8970), both as documented in `ND_OMNIFOLD_RUN_LOG.md`.
  Gate-3 closure recovered/truth **0.9884** is taken from the run log (its
  denominator is the MC-truth total, which requires the full dump; not
  recomputed here).
- **PET 4D combined budget**: **PASS**.
  `products/pet/pet_4d_covariance_combined.root` median frac per reported bin:
  C_syst 18.31%, C_stat 4.18%, C_ML 3.32%, C_lateral (transferred) 4.03%,
  **C_total 23.02%** (the "23.0% total").
- **Control plots / migration figures (new, 2026-06-09)**: generated by
  `nd-unfolding/make_control_plots.py` from the CV 5D omnifile
  (`runEventLoopOmniFold_5D_MEFHC.root`, POT scale 0.212405). Reco-level
  data/MC(sig+bkg) = **1.1203** uniformly across all five axes (rising with
  pT from 0.88 to ~1.2) — consistent with the truth-level Tune-v1 deficit.
  Truth→reco diagonal purity medians: pt 0.583, pz 0.590, eavail 0.591,
  q3 0.614, W 0.595. Products: `products/5d/control_plots.png`,
  `products/5d/migration_resolution.png`.
- **FPS pilot (new, 2026-06-09)**: full-phase-space 1A pilot chain (jobs
  54232749/54232780/54233015) — see `nd-unfolding/FPS_PILOT.md`. Driver
  regression smoke **PASS** (default path untouched). **Anchor PASS**: FPS
  unfold restricted to the published-PS block reproduces the control to
  integral 0.9995, median per-cell 1.0005, median |Δ| 0.65% (185 cells).
  Acceptance: 33.6% of fiducial CC truth rate outside published cuts
  (22.4% p∥<1.5, 11.2% θ>20°); eff<2% cells carry 27.7%. Prior swap
  (tune vs bare GENIE, after the exact 1/pot_scale no-weights correction):
  published cells median 3.0%, new cells median 5.1% / p90 22.7%.
  KNOWN QUIRK: no-`--use-weights` driver mode is globally low by pot_scale
  (unscaled MC weights into OmniFold vs scaled binning weights) — corrected
  in `fps_pilot_compare.py`, flagged as code debt.
- **FPS MEFHC battery (2026-06-10, job 54244120)**: full-statistics campaign
  stage — **anchor gate PASS**: FPS unfold restricted to the published-PS
  block vs control: integral 0.9994, per-cell median 1.0013, median |Δ|
  0.57% (185 cells). Control unfold total 3.073e-38 = the frozen production
  2D number exactly. **FPS total cross section 4.502e-38 cm²/nucleon** over
  the full tracker-fiducial muon phase space (+46% vs restricted). MEFHC
  acceptance fractions match the 1A pilot (66.4% inside, 22.3% p∥<1.5,
  11.3% θ>20°; dead-cell share 27.7%). Prior swap (corrected): published
  cells median 2.86%/p90 7.5%; extension cells median 6.27%/p90 25.4%/max
  42%. Plain closure on the extended grid: recovered/truth = 1.0000 in every
  cell (no bookkeeping/normalization bias; degenerate self-closure — the
  informative extrapolation tests are the prior swap + injected closures).
  UQ stage launched on this gate (array 54254627 → merge 54254628).
- **FPS 3-prior envelope (2026-06-10, job 54244178)**: totals MnvTune
  4.502e-38 / NuWro-shaped 4.475e-38 / bare-GENIE (corrected) 4.367e-38 —
  total spread ±1.5%. Per-cell half-spread/mean: published-PS cells median
  **2.91%** (p90 14.3%); extension cells median **7.88%**, p90 **62%**, max
  81% — large spread confined to the dead cells (catch rows/columns, lowest
  p∥ strip), the quantitative basis for tier-2 flagging.
  `products/5d/fps_prior_envelope_MEFHC.png`.
- **FPS coverage toys (2026-06-12, array 54326694 + analysis 54351540)**:
  **PASS — the FPS campaign's last validation gate.** 200 closure+bootstrap
  toys (`coverage_toy_nd.py`, npz 2D-recipe mirror) over 266 reported bins:
  mean coverage **68.93%** (target 68.27%), median 69.00%, ⟨|r|⟩ **0.792**
  (target 0.798), signed r −0.005, 16 bins <65%. Region split: published
  185 bins mean **68.46%** (14 <65%); extension 81 bins mean **70.01%**
  (slightly conservative, 2 <65%). The bootstrap band is correctly
  calibrated in BOTH regions — together with the hidden-variable closure
  PASS, the extension region is validated for two-tier reporting.
- **Ascencio fine-grid stage-1 comparison (2026-06-12, jobs 54351853 +
  `compare_ascencio_fine.py`)**: dedicated re-unfold on the UNION of their
  44-cell edges (13 E_avail × 7 q3 incl. catch bins; their per-column
  binnings tile it exactly; 4D integral 3.07e-38 = frozen anchor). All 44
  cells compared (pz<20 muon gate): ours/theirs median **1.077** (consistent
  with the super-grid 1.09/1.06), per-cell pulls vs THEIR errors median
  +0.99 with **5/44 beyond 2σ** (worst −3.2σ), diag-only χ²/ndf 81.9/44.
  Their-cov-only full χ² (6064/44) is an uninterpretable upper bound: their
  strong correlations amplify the coherent ~8% offset that OUR covariance
  absorbs (super-grid full-cov χ²/ndf 1.68/2 stands as the quantitative
  consistency statement). Stage 2 (sweep on this binning) required before
  quoting a fine-grid χ². Artifacts:
  `products/4d/xsec_4d_MEFHC_ascencio_fine.root`,
  `products/4d/ascencio_fine_compare.png`.
- **FPS combined covariance + unified-throw adoption (2026-06-12, jobs
  54314362/54325576-79, throws 54314368-71)**: the full-phase-space UQ stage
  is COMPLETE. Block-sum: C_syst median 7.27%/bin (rank 144/266, √tr
  8.027e-39; per-bin medians Flux-led at 5.01%, but the TRACE is dominated by
  Muon_Energy_MINERvA √tr 7.0e-39 — the energy scale moving the large low-p∥
  extension cross section, an FPS-specific feature); + norm 1.4% + C_stat
  0.669% (100 bootstraps) + C_ML 0.357% (24 splits) → combined median
  7.33%/bin, rank 222/266, √tr 8.040e-39. Unified throw (160 joint throws on
  the validated miss-pinned bank): √tr ratio unified/block **1.301 raw /
  1.295 jitter-corrected** (vs ×2.01 in 4D); cross-term 83.2% of block;
  jitter floor ×10 below signal. **ADOPTED** (4D-style per-bin max()
  σ-inflation onto the sweep's vertical block): median g=1.000, 39.5% of
  bins inflated, max g=5.93; final covariance **median 8.19%/bin**, √tr
  9.724e-39 (×1.209), PSD exact (0 negative eigenvalues). Artifacts:
  `uq_fps/universe_stage2_fps/uq_universe_fps_covariance_combined[_uthrow].root`,
  `uq_fps/unified_throw_cov_fps.root`.
- **PET-bank reassessment (2026-06-12, jobs 54330164/54330166)**: **KNOWN_ISSUES
  #12 PET residual CLOSED.** `bank_uthrow` regenerated from the merged 5D file
  with the post-fix dump (miss-row rhos pinned to 1.0); alignment gate PASS
  (w_truth bit-identical over all 32,849,103 rows). `pet_systematics.py` re-run,
  everything else unchanged: C_syst median **18.31% → 8.24%** (the old bank's
  mangled miss-row ratios had inflated it ×2.2); C_stat 4.18% and C_ML 3.32%
  IDENTICAL to the published file (bank-independent blocks = control); clean
  C_total **11.66%** vs published 23.02% (rebank file carries no lateral block;
  adding the transferred 4.03% lateral ⇒ ≈12.3%). Direction: the published
  budget was conservative (over-covered) — no result invalidated, but the
  technote PET-budget numbers should be revised to the rebank values.
  Artifact `products/pet/pet_4d_covariance_combined_rebank.root` (published
  file untouched).
- **LE→ME beam-evolution shape comparison (2026-06-11, qualitative)**:
  `compare_le_evolution.py`, shapes only (fluxes differ — no χ²). Filkins
  2002.12496 vs our 4D-product marginals: LE/ME shape ratio median 1.196
  (pT, 13/13 bins) and 1.265 (p∥, 12/12 bins) — the ME shape is harder in
  p∥, as expected from ⟨Eν⟩ 3.5→6 GeV. Rodrigues 1511.05944 (E_avail,q3)
  rebinned onto our coarse grid (edges nest exactly; strict coverage mask):
  per-bin LE/ME shape ratios 0.89/1.14/0.94 (q3 0.4–0.6, LE-covered
  E_avail<0.4) and 0.73/0.97/1.11/0.90 (q3 0.6–0.8, full 0–0.8) — LE softer
  at low E_avail in the highest-q3 slice. q3<0.4 has too little complete LE
  coverage after rebinning to compare. Data: `nd-unfolding/reference_le/`;
  figure `products/4d/le_evolution_compare.png`.
- **FPS hidden-variable closure (2026-06-11, job 54326695)**: **PASS.**
  Gaussian truth bump injected in true E_avail (A=0.3, c=0.3 GeV, s=0.15 GeV;
  injected mean factor 1.0360) on closure pseudo-data; the 2D FPS unfold
  (extended grid, blind to E_avail) recovers it per cell
  (hXSecND/hClosureRefND): published-PS cells (185) median |dev| **0.17%**,
  p90 0.65%, max 2.93%; extension cells (81 nonzero of 100) median **0.77%**,
  p90 3.04%, max **4.05%** — both regions well inside the tier-2 3-prior band
  (medians 2.9%/7.9%). Whole-grid closure median 1.0011, max|dev| 4.05%.
  Driver hidden-axis mode + `fps_extension_validation.py` region split;
  artifact `products/5d/closure_2d_FPS_hidden_eavail_MEFHC.root`.
- **Ascencio bin-identical cross-check (2026-06-10)**: **PASS (consistent)**.
  Supplemental data found in the public arXiv source tarball of 2110.13372
  (44 cells + full covariance → `3d-unfolding/genie/
  ascencio_2110.13372_supplemental.txt`, cov exactly symmetric).
  `compare_ascencio_fullcov.py`: maximal common grid = 2 super-cells
  (Eavail<0.4 in q3 [0.4,0.6) and [0.6,1.2)); ours/Ascencio = 1.092 and
  1.063 (pulls 1.29σ, 0.86σ); full-cov χ²/ndf = **1.68/2, p = 0.432**
  (diag-only 2.40/2). Our side: frozen 4D product + adopted unified-throw
  combined covariance, (pT,pz)-marginalised with pz<20 GeV mirroring the
  Ascencio muon gate. Caveats recorded in the script header (shared MINERvA
  systematics treated as independent; pμ≈pz at the 20 GeV edge).
  `products/4d/ascencio_fullcov_compare.png`.
- **Driver no-weights normalization fix verification (2026-06-10, job
  54271042)**: **PASS — KNOWN_ISSUES #1 closed.** Driver now always passes
  the POT-scaled weights to OmniFold (no-`--use-weights` mode previously fed
  unit weights, letting the classifier absorb the normalization gap while
  the binning re-applied pot_scale → globally low by pot_scale). Both
  bare-GENIE FPS unfolds re-run with the fixed driver and the 1/pot_scale
  corrections REMOVED from `fps_pilot_compare.py`/`fps_prior_envelope.py`:
  1A anchor 0.9995/0.65% reproduced; MEFHC tune/genie totals 4.502e-38 /
  4.369e-38 (was 4.367e-38 corrected — ML-jitter level); envelope medians
  2.90% published / 7.86% extension (was 2.91%/7.88%). The ledger entries
  above describing the correction are historical records of the pre-fix
  pipeline; post-fix artifacts need no correction.
- **PET-native lateral band (2026-06-10, job 54284039)**: cross-check of the
  GBDT-transferred lateral block in the PET 4D budget, via the event-aligned
  5D join (`pet_lateral_band.py`; PC↔5D row alignment asserted over all
  32.85M rows, 4 truth columns + w_truth exact; CV-path consistency 0).
  18 detector universes, frozen PET push weights, miss rows pinned to CV
  (KNOWN_ISSUES #12), reco-weight ratio in the completeness numerator.
  **Native lateral median 1.74%/bin vs transferred 4.03%; total budget
  22.5% vs published 23.0%.** Band ordering: MinosEfficiency (sqrt-tr
  2.7e-39) > Muon_Energy_MINOS (3.4e-40) > GEANT_Neutron (5.6e-40 — same
  order) > GEANT_Proton/Pion > BeamAngle/MuonResolution (≲5e-42). The
  frozen-push scheme cannot carry per-universe retraining response, so the
  native band is the optimistic bound and the published transfer the
  conservative one — **the published 23.0% budget stands**; the true
  lateral lies in [1.74%, 4.03%].
  `products/pet/pet_4d_covariance_combined_wlat.root`.
- **Standing checks rerun**: **PASS**. `xsec_nd.py` self-tests all pass;
  `check_4d_anchors.py` reproduces 0.38%/0.64%/1.68% medians and 4D/3D
  integral ratio 0.9960; `check_5d_anchors.py` 5D/4D total 1.0011, W marginal
  PASS; `compare_3d_fullcov.py` reproduces the historical candidate's
  sqrt-trace 5.724e-39, rank 247/1431, and Tune-v1/GiBUU ordering. These
  covariance-dependent numbers are quarantined pending the final 5D-to-3D
  projection.

## Environment And Test Harness

- `python -m pytest unbinned_unfolding/test -q`: **BLOCKED**. The active
  `root_6_28` Python does not have `pytest` installed.
- `python 3d-unfolding/xsec_3d.py`: **PASS**. Eavail marginal recovers 2D
  cross section to max relative difference `3.84e-16`; 1D projections integrate
  to the same total.
- `python nd-unfolding/xsec_nd.py`: **PASS**. N-D extraction reproduces frozen
  `xsec_3d.py` to `<1e-12`; 4D q3 marginal recovers 3D cross section to max
  relative difference `3.8e-16`; all 1D projections integrate to the same total.

## Known Audit Findings

- Point-cloud PET: **REFRESHED AS A SHAPE/METHOD CROSS-CHECK**. The stale
  `ExtraEnergyClusters_*` PET artifact was replaced after confirming
  `CVUniverse::GetRecoClusters()` reads `cluster_energy`, `cluster_pos`,
  `cluster_z`, and filters `cluster_isMuontrack`. The corrected point-cloud
  chain rebuilt `runEventLoopOmniFold_PC_MEFHC.root` and `of_inputs_pc.npz`,
  then PET training job 54033990 and comparison job 54033991 completed with
  exit `0:0`. The regenerated `pet_vs_gbdt.png` reports area-normalized
  PET-vs-GBDT median shape differences of 3.86% (pT), 2.36% (pz), 2.63%
  (Eavail), and 2.33% (q3). This remains a shape-only comparison because the
  PET run uses a 2M-event subsample.
- Ascencio low-q3 data: **STAGED ONLY** unless a gated data file is supplied.
  Local scripts can produce our-side spectra and synthetic checks, but the real
  2110.13372 numerical overlay is not complete from public in-session data.

## Active 2D Result

- `compare_to_paper_fullcov.py` with the frozen 2D result and paper covariance:
  **PASS**. Recomputed paper full-covariance chi2/ndf is `3.661` on 205 bins.
- Combined paper+ours check: **PASS** when using
  `uq_universe_covariance_full_matcorr_fluxfix.root:hCov_combined` plus
  `uq_covariance_ml.root:hCov2D_reported`. Recomputed combined chi2/ndf is
  `1.481`; log-normal combined chi2/ndf is `1.468`; pull mean/RMS is
  `0.051/0.409`.
- Covariance-file contract: `hCov_combined` already includes the bootstrap
  covariance. Adding `uq_covariance_boot300.root:hCov2D_reported` separately
  double-counts bootstrap and changes the combined chi2/ndf to `1.341`.

## Active 3D And 4D Results — central anchors valid; covariance products gated

- `compare_3d_fullcov.py` with GENIE, Tune v1, NuWro, and GiBUU reproduces the
  historical candidate: sqrt-trace `5.724e-39`, hard rank `247/1431`, and the
  same generator ordering. **DIAGNOSTIC ONLY** — the final quotable 3D
  covariance and generator comparison require the adopted selection-complete
  5D-to-3D projection.
- `check_4d_anchors.py`: **PASS**. 4D total is `3.0665e-38`; 4D/3D
  2D-marginal integral ratio is `0.9960`; median projection differences are
  `0.38%` for pT, `0.64%` for pz, and `1.68%` for Eavail.
- `compare_ascencio_q3.py`: **PASS for our-side spectra only**. It produces
  `d sigma/dq3` and low-q3 `Eavail` slices; no real Ascencio chi2 is computed
  without the external gated data file.
- `compare_mlsplit_combined.py`: **PASS as a historical-component diagnostic**.
  Train/test-split ML band is `1.24x` the seed-only band, but the historical
  combined 3D sqrt-trace moves only `+0.04%`; final adoption remains gated.

## Validation Diagnostics

- `bottom_line_test.py --dim 2 --mode closure`: **PASS**. Feature-bin residual
  is `1.6875%` vs injected `17.202%`, ratio `0.0981`.
- `bottom_line_test.py --dim 3 --mode closure`: **PASS**. Feature-bin residual
  is `1.8408%` vs injected `18.061%`, ratio `0.1019`.
- `classifier_calibration.py --n 200000`: **PASS**. GBDT AUC/Brier
  `0.5374/0.2486`; MLP AUC/Brier `0.5338/0.2500`; binned ratio recovery
  median `4.72%` for GBDT and `20.90%` for MLP; GBDT/MLP binned correlation
  `0.9159`.
- `unbinned_gof.py` using stored 3D weights with `--max-per-class 200000`:
  **DESCRIPTIVE DIAGNOSTIC ONLY**. Prior acc/AUC `0.5196/0.5314`; unfolded
  acc/AUC `0.5013/0.5022`. The historical analytic `z` and `p` values are not
  calibrated because the OmniFold weights were not cross-fitted and the null
  does not repeat the full pipeline.
- Same-ensemble pull diagnostic: **REPRODUCED 2026-06-11** (the 200-toy
  ROOTs were missing from the checkout). Regen arrays 54273493/54273495 rebuilt
  all 200 toys in `2d-unfolding/uq/coverage/`; `uq/coverage_toys.py` reproduces
  the historical result exactly: fraction with $|r|\leq1$
  `68.71%`, median `68.50%`, `<|r|> = 0.794` (target 0.798), signed residual
  `+0.006 +/- 0.082`, `97.56%` of the 205 reported bins above the 65% target
  (same 5 bins below). Because the same toys determine and are scored by their
  standard deviation, these are Gaussianity/pull checks, not coverage.

### 2026-07-16 — Corrected 4D UQ (P6-4D), non-lateral core (support-limited lateral)

These supersede the quarantined June `uq_4d/` products for the NON-LATERAL contract. The
FINAL adopted 4D covariance additionally needs the unified-throw inflation + Agent A's
selection-complete standard lateral block (both pending); numbers below are the corrected
combined (block-sum) covariance and validations.
- 4D throw bank (from-5D reconstruction, `assemble_bank_4d_from5d.py`) CV reproduces the
  frozen 4D central: reported bins `4830` (mask identical), total `3.0679e-38` vs central
  `3.0664e-38` (rel `4.8e-4`), per-bin median `0.65%`. PASS. [pilot_cv_check_4d.py]
- Corrected combined 4D covariance (reported bins 4830; symmetric, finite, PSD min-eig/max
  `-2.8e-16`): C_syst √tr `2.0931e-38` (median `13.37%`/bin, rank 142); +norm 1.4%; +C_stat
  √tr `1.2117e-39` (median `0.92%`); +C_ML √tr `1.0499e-39` (median `0.74%`); COMBINED √tr
  `2.0992e-38` (median `13.47%`/bin, rank 264). [uq_4d/corrected/universe_stage2_4d/
  uq_universe_4d_covariance_combined.root; summary .../uq_universe_4d_covariance_combined.summary.json]
- P7 5D→4D marginal (DRY-RUN candidate on the current committed adopted 5D; NOT a
  publication number — final gated): 4830-bin PSD projection, √tr `2.41e-38`, 5 orphan
  4D-reported bins receive no 5D source (flagged). [project_cov_nd.py]

### 2026-07-16 — Statistical-validation repair (Agent C WS1 coverage; integrated into the note by Agent D)

Coverage audit and FPS split-sample truth-containment diagnostic
(Gaussian nominal 68.27%). Reuse-only on the existing toy stacks
(`coverage_valid_nd.py`, estimator seed 42):
- 2D: **NO COVERAGE NUMBER.** The 200 ROOT toys fluctuate stored
  `hTruthXSec2D` through the MC bootstrap; all 205 reported bins vary, with a
  maximum relative range of 1.048 across toys. The attempted 68.80% result used
  their all-toy mean and is withdrawn because that is not an independent fixed
  truth. A valid independent reference or redesigned ensemble is required.
  [`2d-unfolding/uq/coverage_valid_2d_audit.json`]
- FPS: **68.67%** of evaluation bin--toy cells (200 cov_fps toys split 100/100,
  266 bins). Variant-A independent `C_stat` band contains **77.6%** of closure
  bin--toy cells and is wider than the closure-toy spread. The estimator seed is
  fixed, so these diagnose the statistical closure-toy stream rather than the
  full adopted band.
  [`nd-unfolding/uq_fps/corrected/coverage_valid_fps.json`]
- The OLD same-ensemble "coverage" (2D `68.71%` / FPS `68.9%`, ⟨|r|⟩≈`0.794` vs √(2/π)=`0.798`,
  `97.6%` bins ≥65%) is a standardized-pull/Gaussianity self-consistency diagnostic, NOT
  frequentist coverage → RELABELED, retained under that label. No aggregate
  binomial uncertainty is quoted because bins within each toy are correlated
  and the calibration widths are estimated.

C2ST (WS2): analytic p-values (`z=1.4, p=0.17`; `p≈5e-244`) and "statistically indistinguishable"
REMOVED from the note; retained as a descriptive held-out-AUC drop (≈0.535→≈0.501); no calibrated
p-value (valid null = hundreds of cross-fitted OmniFold pipelines, unaffordable; unbinned GoF open).
WS3: ours-vs-paper χ² (`\chiPaper` 3.66 / `\chiCombined` 1.481) relabeled an INDICATIVE distance
(shared systematics + no OmniFold↔paper cross-covariance → not a calibrated GoF); Ascencio kept
shape-level/descriptive; generator significances remain gated until the selection-complete
higher-dimensional covariance is adopted and the values are recomputed.
Agent C's full WS2/WS3 RUN_LOG/STATUS + the paired-C_delta OF-vs-IBU test land under their commit gate.

FPS P4/P6 (2026-07-18, 2nd fail-closed repair round): the ten FPS active-endpoint unfolds are PURITY
CONTROLS (both launchers omitted --bkg-mode → unfold default `purity`), quarantined and NOT publication
inputs; the selected footing is `negweight-refined`. No covariance was built or adopted. The negweight
preflight is hardened: a hash-bound v2 publication manifest requiring the canonical 266/285 reported-mask
fingerprint (23b2a2f4…, recomputed not trusted) + full merged-input SHA256 (reused from the validated
orchestrator receipt p4-merged-20260718, no re-hash) + a PASS receipt bound at every covariance
transition; mandatory hJointMeanShift; transactional endpoint launchers. 41/41 ROOT-free gate tests
PASS. Production remains gated on an `fps-adopt-verifier` PASS of this patch; no physics numbers change.

FPS P4/P6 (2026-07-18, repair-3): the chain is now mutually executable + hash-recomputing. Every
consumer runs its manifest/receipt/hash gates BEFORE importing ROOT (login-safe) and RECOMPUTES every
referenced artifact hash (strict lowercase 64-hex; canonical paths for unfold/input/config/source/
launcher/central/audit) — a substituted same-size ROOT, non-hex hash, or missing path fails. P4 gating
is unconditional; a schema-versioned hash-bound receipt chain (component_build → p4_validation →
active_adoption → unified_adoption) binds each predecessor artifact; two-field PASS objects are rejected.
Unified adoption requires the production CV sha + canonical 266/285 mask from the manifest and
hJointMeanShift(expected_dim=n) with its hash bound. Both endpoint launchers sit behind one strict
validator (fps_endpoint_receipt.py) that attributes the launcher actually used. Tests: 49/49 ROOT-free
unit + 9/9 REAL-CLI integration negatives PASS. ND_OMNIFOLD_STATUS.md remains a pre-existing PG0 dirty
file with no durable writer receipt (not repaired here). Production gated on fps-adopt-verifier PASS.

## 2026-07-18 G2 full-event extended-FPS dump — playlist-1A runtime smoke VERIFIED

First runtime validation of the G2 full-event point-cloud dump. Binary
`runEventLoopOmniFold` sha256 `61d7dfbf7ee38f39e51c656b48702056c773c3d1c5d1b2d9bf08a6da42d2e19b`,
built from source `486e53e` (G2 source byte-identical through HEAD `53de3f4`).
Playlist-1A, canonical manifests (`1A_Data.txt` sha256 `b74d8965…`, `1A_MC.txt`
sha256 `4100dca4…`), env `MNV101_DUMP_POINTCLOUD=1 MNV101_FULL_PHASE_SPACE=1`.
Validator PASS **50/50, 0 failed**:
- `mc_truth_denom == mc_signal_reco = 4,073,230` (Phase-18.2 completeness c-invariant, exact by construction)
- `mc_background = 44,900`; `data = 360,123`; native truth-only misses = `1,596,619`
- `mcPOTUsed = 4.0692592418996086e20`; `dataPOTUsed = 8.972756120489268e19`
- schema `petSchemaVersion=g2-fullevent-v1`, `hasFullEventSchema=1`, `fullPhaseSpace=1`
- native misses: `sim_pass=0`, reco muon/vertex `-9999` sentinels, empty reco clouds, valid cached truth id/muon
- distinct data/reco/truth schemas; no forbidden truth-detector/data-truth counterparts; equal E/pos/z/view/time cloud lengths; bkg cloud + `w_bkg` present; `cluster_view/time` + `ev_run/ev_subrun/ev_gate` populated

Published ROOT `nd-unfolding/pet/g2_smoke/runEventLoopOmniFold_G2_FPS_1A.root`
(9,419,026,130 B, sha256 `51e46fddd061cae37704c64604f73df8bb3d739cd5420bfd21cb0d2c89db320f`);
receipt `nd-unfolding/pet/g2_smoke/G2_1A_VALIDATION_RECEIPT.json` (sha256
`0aae83d84af77b2520dec83439e7a061176debc5e0d81e18019ac43a5a697867`); validation
receipt v2 sha256 `776addeb3453445bcb1e6fa45f81ed41ffe7f713a1cb2da0eac729eccf007b25`.
INTERFACE/INFRASTRUCTURE validation only — NOT a cross-section result. 12-playlist
production launcher staged, NOT submitted.

## 2026-07-19 G2 retained-domain recovery — playlists 1D and 1E VERIFIED (conditional)

Two full-event production loops completed but the 20,000-row sampled validator
encountered native upstream-corrupt muons outside the declared extended-FPS
retained domain. Exact source-AnaTuple comparisons confirmed that the G2 writer
copied the corrupt values faithfully. An additive exhaustive validator, accepted
by the persistent independent Gemini verifier after three fail-closed repairs,
composed the base structural suite and bound every excluded row.

- 1D: PASS, 2,643 out-of-domain rows bound; recovered ROOT 14,150,286,041 B,
  sha256 `06be7e6875f357af91b7e9d8d875e9b9759118c5c59002f5ac1fd205dc282b56`.
- 1E: PASS, 2,162 out-of-domain rows bound; recovered ROOT 11,651,881,243 B,
  sha256 `6ab0ac90d75aa843e99f33d8a817dab27b418273cbef298f641e7344724394dc`.
- Both publications returned rc=0, used the unchanged canonical binary/base
  validator/production launcher hashes, and passed independent post-publication
  SHA-256 checks.

This is interface/input evidence, not a physics result. It is valid only if the
next full-schema builder enforces `0<=pT<=30 GeV` and
`0<=p_parallel<=120 GeV` before training. All twelve array pairs and that
downstream exclusion still require their own committed gates. Canonical receipt:
`docs/orchestration/state/g2-domain-recovery-20260719.json`.

## 2026-07-19 G2 retained-domain recovery — playlists 1F and 1P VERIFIED (conditional)

The same committed, independently verified exhaustive recovery gate was applied
to two later sampled-validator failures without rerunning their completed event
loops. All non-superseded structural checks passed, and every excluded row was
identity/value-bound.

- 1F: PASS, 3,183 out-of-domain rows bound; recovered ROOT 16,299,560,962 B,
  sha256 `b5e7c28f40325015841e12c0f3e11987389eed61979e103effbf6f70473190fc`.
- 1P: PASS, 985 out-of-domain rows bound; recovered ROOT 4,631,598,593 B,
  sha256 `e986dab2bc64fb801eac0532df2a1539b7c409d3ccb46d8e6364feabc779ef4f`.
- Both no-clobber publications returned rc=0 and independently recomputed final
  ROOT hashes matched their receipt hashes.

This remains conditional interface/input evidence, not a physics result. The
next full-schema builder must enforce `0<=pT<=30 GeV` and
`0<=p_parallel<=120 GeV`; all twelve pairs still require one terminal committed
Gate-1 reconciliation. Canonical receipt:
`docs/orchestration/state/g2-domain-recovery-r4-20260719.json`.

## 2026-07-19 G2 Gate 1A — all 12 full-schema playlist pairs VERIFIED

Independent terminal validation of the complete per-playlist production set:

- 12/12 canonical playlist ROOT/receipt pairs PASS; zero validation failures.
- Total ROOT bytes: **113,500,285,444**; every ROOT SHA-256 recomputed and matched.
- `mc_truth_denom = mc_signal_reco = 49,906,108` exactly.
- `mc_background = 566,036`; `data = 4,119,797`; native truth-only misses =
  `20,361,799`.
- `mcPOTUsed = 4.978198462880827e21`; `dataPOTUsed = 1.057394261158926e21`.
- Eight normal production receipts passed 50/50 sampled validation. Four
  recovery receipts (1D/1E/1F/1P) bind exhaustive finite out-of-domain censuses,
  zero fatal/non-superseded failures, and the exact reviewed recovery chain.
- The same persistent Gemini verifier returned PASS and authorized commit.

This closes the per-playlist Gate 1A interface/input subgate, not Gate 1B or a
physics result. The merged ROOT and aligned three-inventory full-schema NPZ are
still required, and the downstream reader must enforce
`0<=pT<=30 GeV`, `0<=p_parallel<=120 GeV` before training. Canonical summary:
`docs/orchestration/state/g2-gate1-all12-validation-20260719.json` (sha256
`23b652d69460d61f2c347d0ec50c883043df83e0aa3fab3eda56b18b7364911f`).
