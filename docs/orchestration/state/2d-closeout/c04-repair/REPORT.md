# 2D closeout — C04+X01-repaired 2D covariance (no re-unfold)

**Owner:** 2D closeout executor (2d closer), directed by the paper-tighten lane under
[`AUTHORIZATION-20261012-2d-closeout-delegation.md`](../../../AUTHORIZATION-20261012-2d-closeout-delegation.md).
**Grant:** [`AUTHORIZATION-20261012-2d-closeout-fluxrepair.md`](../../../AUTHORIZATION-20261012-2d-closeout-fluxrepair.md),
sha256 `1b079177756c68a99bf096c5124d7c2146111a27fae7da772783441a20ac2c75`, verified on `origin/main` `09c8bae0`
before any work.
**Date:** 2026-10-12. **Status:** BUILT AND INDEPENDENTLY VERIFIED (§8); NOT ADOPTED.

**CITABLE FOR:**
- The repaired construction and its numbers (§5), as a built and verified product that awaits Joseph's
  adoption.
- The controls (§4): on the same code path, the adopted construction reproduces VL172 and VL173 exactly.

**NOT CITABLE FOR:**
- A quoted 2D uncertainty. Nothing here is adopted. The quoted 6.87% (VL172) and the VL173 χ² values
  stand until Joseph adopts this product and the paper-tighten lane re-quotes (grant §3).
- Any other repair: KI 91–94, G1, G2, the July sweep, laterals, the statistical-ensemble recipe and C_ML
  are untouched and remain open (Stage B).
- Coverage, or a KI-85 lift.

## 1. Answer

Two blocks of the adopted covariance were rebuilt from the existing universe outputs:
- the Flux band, now MAT-weighted;
- the `Muon_Energy_MINOS` band, now on its own flux denominator.

The other 42 bands, the normalization block, the bootstrap and the ML block are byte-identical to the
adopted ones. No unfolding was re-run.

| quantity (E_U, 205 cells) | adopted (VL172/VL173) | repaired |
|---|---|---|
| block-sum per-cell median | **6.871 %** (6.8707) | **6.090 %** (6.0898) |
| block-sum integral σ | 5.391 % | **4.230 %** |
| Flux band per-cell median / integral | 4.993 % / 4.893 % | **3.655 % / 3.557 %** |
| `Muon_Energy_MINOS` per-cell median / integral | 2.305 % / 0.113 % | 2.281 % / 0.367 % |
| combined χ²/ndf against the paper | 0.914 | **0.994** |
| log-normal combined χ²/ndf | 0.932 | **1.014** |
| stat-subtracted diagnostic χ²/ndf | 4.128 | **5.803** |
| combined pull mean / RMS | 0.041 / 0.386 | **0.048 / 0.406** |
| paper-covariance χ²/ndf (depends on the central only) | 2.654 | 2.654 |

76 of 76 build checks pass. MAT agreement is at most 1.1e-15 relative, against a bound of 1e-12. Every
control reproduces its committed value exactly. Compute: login node only, 0 Slurm jobs, **0 node-h** of
the 1.0 granted.

## 2. Construction

Script: [`scripts/build_repair.py`](scripts/build_repair.py); wrapper: [`scripts/run_repair.sh`](scripts/run_repair.sh).

- **C04 (KI 95), Flux.** The block is MAT `MnvVertErrorBand::CalcCovMx` with universe weights:
  - C = Σ_u w_u (X_u − x̄_w)(X_u − x̄_w)ᵀ / Σ_u w_u, with x̄_w = Σ_u w_u X_u / Σ_u w_u.
  - It runs over the 100 existing flux-fixed Flux outputs (`uq/universe_sweep_fluxfix/`), each X_u
    being one universe's `hXSec2D` on the 205 reported cells.
  - The weights are the Flux band's `GetUnivWgts()` on `pTmu_reweightedflux_integrated`, read in all
    12 per-playlist flux files. They are identical across playlists and equal the first 100 `Flux`
    entries of `sorted_NuEConstraint_FHC_RHC_IMD.txt` exactly (maximum difference 0.0).
  - Σw = 211.012, range 1.06e-5 to 26.95, n_eff = 19.06.
  - Centring is on the weighted universe mean, as in MAT. The CV cancels from the covariance.
- **X01 (KI 96), Muon_Energy_MINOS.** Each of the two outputs had divided by Φ_CV, its own stored
  `hFlux_pt`; that equals `runEventLoopMC_MEFHC.root`'s flux exactly (difference 0.0). Their `fluxSource`
  string names `runEventLoopMC_MEHFC.root` (sic), a file that does not exist; the stored flux is
  bitwise that of the existing `MEFHC` file, so only the provenance string is stale (verifier, §8).
  - Each output is multiplied per pT bin (the `hXSec2D` x-axis) by Φ_CV(pT)/Φ_MINOS,u(pT). Φ is a
    pure divisor, so the rescale is exact.
  - Φ_MINOS,u is the data-POT-weighted combination of the band's universe u over the 12 playlists,
    by the same rule as `uq/build_flux_universe_band.py`.
  - Φ_MINOS,u/Φ_CV = **1.0004186** for u0 and **0.9953532** for u1, flat in pT.
  - The block uses the adopted formula: mean-centred, 1/N, N = 2.
- **Everything else** is copied from the adopted rollup (`077912e3…`), with a byte-identity check on
  each of the 43 blocks.
- **Totals.** The universe total is accumulated in `analyze_universes.py`'s order: sorted bands, then
  the normalization. Then hCov_combined = total + C_boot(VL170), and the block sum = hCov_combined + C_ML.
- **Output.** The repaired rollup is written in `analyze_universes.py`'s schema, so the committed
  producers run on it unchanged. It adds `hReportedCells`, from the committed `reported_cells.py`; the
  adopted file predates that object.
- **Producers.** The committed producers ran from a `git archive` of `09c8bae0` placed in the namespace,
  not from the shared NERSC checkout:
  - `compare_to_paper_fullcov.py` with `--ours E_U --omnifold-cov <rollup>:hCov_combined --omnifold-cov <ML>:hCov2D_reported`, in three modes: plain, `--log-normal` and `--subtract-stat`;
  - `uq/plot_uncertainty_fig6_7_style.py`.

## 3. Inputs (sha256 re-measured in this run; full list in [`products/build.json.gz`](products/build.json.gz))

| input | sha256 |
|---|---|
| E_U `uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root` | `4f5a1b6d44b9e7212b233650bb00bfb626ae65461e3bf8033cd67866dbd7eb2c` |
| adopted rollup (VL172) `uq/universe_stage2_MEFHC_full_matcorr_fluxfix_vl170/uq_universe_covariance_full_matcorr_fluxfix.root` | `077912e3e7a53376c6df89ee1af4a2a504fe1f49423bab88780204beccd952f5` |
| bootstrap (VL170) `uq/bootstrap_MEFHC_300_vl170/uq_covariance_boot300.root` | `71a75821ceeb658710adca30243e39e7184e33f868f58ea56cffe63ba8db0115` |
| ML `uq/seedscan_lgbm_ml/uq_covariance_ml.root` | `3b6b48ec89207ae29dc7bb0ddc5a41836c359c4805877d663731694b828d5db9` |
| combined flux band `baseline_flux/flux_integral_universes_MEFHC.root` | `5eecae84509ba8ededbe8fdee63508d8e36cd057cc0547a940383f80248580eb` |
| constraint file (MAT `35097b65` tree) | `e38ad7d28354d071577113a18c8c569f88b6239f7fb193d20285273f172fc0c2` |
| 187 universe outputs (44 bands): sha256 of the concatenated per-file sha256, in sorted band then index order | `8e22297eb18c68432ae9a5a1c734473bcafac5b945db65f2a118a3d33e113c88` |
| committed Fig. 1 export `receipts/2d-lgbm42-20261011/cov2d_blocks_205.npz` (control operand) | `f04f496aa7ad04b76a5879e495bb18dbf44816f5f45412d8e444a983677317dc` |

The 24 per-playlist flux files (MC and Data, 1A–1P) are hashed in `build.json`. MAT library:
`MINERvA101/opt/lib/libMAT.so`. The MAT source checkout beside it is at
`35097b65ab1680db8058f9ede18fecffdc3a1ea3`; that the library was built from that commit is not checked. The
builder and the verifier used the same library.

## 4. Checks and controls (all in [`products/build.json.gz`](products/build.json.gz); log [`logs/build.log`](logs/build.log))

| control | result |
|---|---|
| adopted `hCov_universe_total` = accumulation of its stored blocks | bitwise |
| adopted `hCov_combined` = that total + C_boot | bitwise |
| Flux and MINOS blocks recomputed from the sweep with `analyze_universes.py`'s formula vs stored | bitwise (both) |
| committed export (`f04f496a…`) vs the adopted hCov_combined and ML | bitwise. The control export the build writes has the same sha256, `f04f496a…`. |
| block-sum per-cell median on the adopted blocks | 6.870658 %: VL172's 6.8707 % |
| χ² family on the adopted rollup, and on the control rebuild (`uq_universe_covariance_control.root`) | identical to the committed VL173 receipts `chi2_lgbm42{,_lognormal,_substat}.txt` line by line, apart from paths and ROOT warnings. This covers 0.914, 0.932, 4.128, the pull mean/RMS 0.041/0.386 and the paper-cov 2.654. |
| Fig. 6/7 producer with VL172's own operands (exact-split central `2d_crossSection_omnifold_MEFHC_5iter.root`, adopted rollup) | summary identical to the committed VL172 summary (`state/ki84-adopt-20261006/products/…/MEFHC_fig6_7_uncertainty_summary.txt`), apart from path lines |

| MAT agreement (max\|diff\|/max\|C\|, bound 1e-12) | value |
|---|---|
| weighted Flux block vs MAT `GetTotalErrorMatrix` with `SetUnivWgts` | 1.10e-15 |
| unweighted Flux, MAT vs the stored adopted block | 8.4e-16 |
| rescaled MINOS block vs MAT | 6.5e-17 |
| whole repaired universe block (44 vertical bands on one MnvH1D, Flux weighted) vs repaired total − normalization | 2.1e-16 in the build; 4.2e-16 in the verifier's own MAT run |
| the same for the adopted universe block | 5.2e-17 |

Every repaired-file object was read back after writing and matches the in-memory matrix bitwise.

## 5. Results (NOT QUOTABLE until adopted)

### 5.1 Block-sum budget (E_U, 205 cells; integral = Σ x·area over the reported cells; full per-band table in [`products/budget.json`](products/budget.json))

| block | per-cell median % | p84 % | min % | max % | integral σ % | √tr C |
|---|---|---|---|---|---|---|
| Flux | 4.993 → **3.655** | 5.447 → 4.359 | 4.783 → 2.972 | 12.806 → 13.395 | 4.893 → **3.557** | 2.0702e-39 → 1.4999e-39 |
| Muon_Energy_MINOS | 2.305 → 2.281 | 4.160 → 3.985 | 0.010 → 0.006 | 9.193 → 8.951 | 0.113 → 0.367 | 1.0131e-39 → 1.0957e-39 |
| universe + normalization | 6.830 → 6.043 | 9.169 → 8.658 | 5.321 → 4.086 | 21.823 → 21.645 | 5.391 → 4.230 | 3.2143e-39 → 2.9102e-39 |
| bootstrap (VL170) | 0.674 (unchanged) | 1.658 | 0.229 | 17.928 | 0.058 | 1.9312e-40 |
| ML | 0.166 (unchanged) | 0.495 | 0.032 | 1.331 | 0.005 | 5.0605e-41 |
| universe + bootstrap (`hCov_combined`) | 6.869 → 6.084 | 9.482 → 9.005 | 5.332 → 4.099 | 23.438 → 23.103 | 5.391 → 4.230 | 3.2200e-39 → 2.9166e-39 |
| **block sum (+ ML)** | **6.871 → 6.090** | 9.497 → 9.024 | 5.332 → 4.100 | 23.441 → 23.106 | **5.391 → 4.230** | 3.2204e-39 → 2.9171e-39 |

The weighted Flux band is narrower in most cells but not in all: its per-cell maximum rises from 12.81% to
13.40%.

### 5.2 χ² family against the paper, central E_U ([`chi2/`](chi2/))

| statistic | adopted | repaired |
|---|---|---|
| paper covariance only | 2.654 | 2.654 |
| combined (paper + hCov_combined + ML) | 0.914 (χ² 187.44) | **0.994** (χ² 203.81) |
| combined, log-normal | 0.932 | **1.014** |
| combined, paper stat subtracted (diagnostic) | 4.128 (χ² 846.22) | **5.803** (χ² 1189.56) |
| combined pull mean / RMS | 0.041 / 0.386 | **0.048 / 0.406** |
| stat-subtracted pull mean / RMS | 0.035 / 0.425 | 0.041 / 0.447 |

ndf = 205; pinv as in the committed producer. The combined χ² rises because the repaired covariance is
smaller.

### 5.3 Fig. 6/7 projections (covariance-exact, E_U; [`fig67/`](fig67/))

| projection, group | E_U adopted median (max) % | E_U repaired median (max) % |
|---|---|---|
| p∥ Total | 5.881 (15.167) | **4.843** (14.876) |
| p∥ Flux | 4.901 (6.260) | **3.543** (5.757) |
| p∥ Muon reconstruction | 2.627 (14.276) | 2.634 (14.365) |
| pT Total | 6.215 (7.954) | **5.310** (7.249) |
| pT Flux | 4.889 (5.599) | **3.552** (4.758) |
| pT Muon reconstruction | 3.548 (5.034) | 3.659 (4.863) |
| published total (p∥ / pT) | 5.474 / 5.308 | 5.474 / 5.308 |

The Models, Normalization, Statistical, Hadronic response and ML groups are unchanged. The figures are
`fig67/EU_repaired_{pz,pt}.pdf`, with `fig67/EU_adopted_{pz,pt}.pdf` for comparison.
- VL172's quoted Fig. 6/7 numbers (Total 5.900% / 6.220%) used the exact-split central. The control
  reproduces them exactly.
- The E_U-adopted column is the bridge. It shows how much of the change is the central value and how
  much is the repair.

### 5.4 Fig. 1 export

[`products/cov2d_blocks_205.npz`](products/cov2d_blocks_205.npz), sha256 `c2606f90…24f8`, is in the form of
the 2026-10-11 export:
- `universe_plus_boot` = the repaired `hCov_combined`;
- `ml` = C_ML, unchanged.

The sidecar [`products/cov2d_blocks_205.json`](products/cov2d_blocks_205.json) names its source objects.
Its keys, shapes and dtype match the committed export; `ml` is bitwise equal.

Two properties for whoever re-makes Fig. 1:
- **The figure script will reject this export as it stands.**
  `receipts/2d-lgbm42-20261011/make_fig1_lgbm42.py:47-51` asserts that the export's diagonal equals the
  quadrature of the *adopted* per-cell σ in `remote_reduce.json` (`sigma_abs`: universe, boot_vl170, ml).
  For this export that assert fails by design, because the universe σ changed. The paper-tighten lane owns
  that script and operand and will add a repaired-operand check at re-quote; this build changed neither.
  For that check: [`products/sigma_abs_205_repaired.json`](products/sigma_abs_205_repaired.json), sha256
  `4e48f6392c9e84a5ad2f9b32bf01ac854f5b63ce2003d3b366a1956b8ee80ef8`, by
  [`scripts/make_sigma_json.py`](scripts/make_sigma_json.py).
  - It carries the per-cell absolute σ (universe incl. the repair, boot_vl170, ml), on the 205 cells in
    `remote_reduce.json`'s order (`2ecfc243…`).
  - It reads the same objects as `remote_reduce.json`: `hSigma_universe_total` of the repaired rollup, and
    `hStd2D` of the bootstrap and ML files.
  - Control: the same reader on the adopted rollup reproduces `remote_reduce.json`'s universe σ bitwise,
    and its boot and ml vectors are bitwise equal.
  - The quadrature of the three vectors matches √diag of the repaired export (`universe_plus_boot + ml`)
    to ≤ 2.4e-16 relative (2.2e-16 as |√diag/quadrature − 1|; the verifier measured 2.37e-16), well inside
  the script's own `rtol=1e-12` test.
  - Repaired/adopted universe σ per cell: median 0.877, range 0.717–1.031.
- **The weighted block is not bitwise symmetric.** The repaired `universe_plus_boot` is symmetric only to
  2.6e-17 relative (max\|C − Cᵀ\|/max\|C\|), a float rounding of the weighted product
  `(Zᵀ·w) Z`. The adopted export is exactly symmetric. The committed χ² producer uses pinv and is
  unaffected; a consumer that requires exact symmetry should take (C + Cᵀ)/2.

## 6. Products and locations

| location | content |
|---|---|
| `/pscratch/sd/j/josephrb/2d-closeout-c04repair-20261012/` | the run: `build/`, `chi2/`, `fig67/`, `logs/`, `scripts/`, `inputs/`, `repo/` (the `09c8bae0` archive) |
| `/global/cfs/cdirs/m3246/josephrb/2d-closeout-c04repair-20261012/` | durable copy of everything except `repo/` and `tmp/`. 61 files, after the σ JSON, its script and its cell-order input were added; `sha256sum -c SHA256SUMS` passes at the destination. The SHA256SUMS file itself has sha256 `ccb0230d…b34c`. |
| this directory | scripts; `products/` (budget, build record, export, σ vectors, MINOS rescale); χ² outputs; Fig. 6/7 summaries and PDFs; logs; [`SHA256SUMS.nersc`](SHA256SUMS.nersc) |

The two repaired ROOT rollups, about 14 MB each, live on pscratch and CFS only:
- `uq_universe_covariance_c04x01.root`, sha256 `da92c5d2567647e8613bb3a6522176dbd9a287970082b45ac9e83e24684b1948`;
- `uq_universe_covariance_control.root`, sha256 `eba9f4bed606c5fef6de5fec6e9c18c4f994a2f9f8c9e4a25c16a0ca97cc4637`.

Every file committed here matches its line in `SHA256SUMS.nersc`. The build record is committed gzipped (`gzip -n`) as `products/build.json.gz`, because the receipt gates read bare filenames in a tracked JSON as deliverables. The JSON inside has sha256 `dcc1331e8e510cc21a2abd95675cfc69acf92bae7ae3dfa43a3a94b9fdbe34dd`, its `SHA256SUMS.nersc` value.

**Hash-binding delta: one, enumerated and power-tested.** The σ JSON pins its cell-order operand,
`remote_reduce.json` (`2ecfc243…`, tracked and verified OK). That moves `verify_hash_bindings.py`'s receipt
inventory from 149 to 150 (digest `6a3787ea` → `f1736989`).
- The delta was enumerated from `receipt_inventory()` rows on `origin/main` `3921dec4` and on this branch:
  one ADDED, nothing removed or repointed.
- Power test: one flipped hex digit in that pin gives MISMATCH, rc 1.
- The constant moved with the delta written into its code comment, and the gate then reports ALL BINDINGS
  INTACT.

## 7. Compute

The run used saul login05 only, with no Slurm job, so the charge is **0 node-h** against the grant's 1.0.
The full run (build, nine χ² runs, three Fig. 6/7 runs) took 56 s of wall time and 4 min 49 s of user CPU.

## 8. Independent verification

A fresh read-only verifier wrote its own code. It did not open the builder's scripts, and it ran on the
login node only (no Slurm). Its report is [`review/VERIFICATION.md`](review/VERIFICATION.md), sha256
`8cb01c272de7c0824df96ccd21a37d395e75e84f670f687d02f816865a0476da`; it is identical to
`$NS/verify/VERIFICATION.md`. **Same-model caveat:** the verifier is the same model family as the builder.
It is an independent implementation, not an independent reasoner.

**Verdict.** Every claim is CONFIRMED, and no defect was found in the construction.

**What it reproduced from the raw inputs:**
- **Flux block:** bitwise.
- **Other repaired objects** (rescaled MINOS outputs, MINOS block, universe total, `hCov_combined`, block
  sum): ≤ 5.3e-15.
- **Untouched blocks:** the 43 other blocks are bitwise unchanged.
- **Control and exports:** the control file, the committed export and the repaired export all match
  bitwise.
- **MAT:** every MAT agreement figure is ≤ 1e-12.
- **Numbers:** every budget field (worst difference 2.4e-12), the χ² family, the pulls, all 48 Fig. 6/7
  summary values, Φ_MINOS,u/Φ_CV and the weights.
- **CFS copy:** 61 files pass `sha256sum -c`.
- **Committed producers:** it re-ran them on the repaired file and got identical outputs.

**Construction checks:**
- **Weight-to-universe alignment** holds by three tests:
  - code (`runEventLoopOmniFold.cpp:344-350`, `FluxReweighter.cxx:1346`);
  - the per-universe Φ ratio, which matches to 2.2e-16, versus 1.1e-3 when shifted by one;
  - the weighted mean, which none of 2,000 weight permutations approaches.
- **CV centring** would change the Flux median only from 3.655% to 3.693%.
- **The X01 direction, axis and index are right.** The rescale follows from
  `unfold_2d_omnifold_unbinned.py:1252-1260` and `:1709-1715`, and u0 = −1σ per
  `MuonSystematics.cxx:50-51`.
- **The normalization block** equals (0.014·E_U)(0.014·E_U)ᵀ bitwise.

**REPORT corrections** (all applied above):
- the whole-block MAT figure (its 4.2e-16 vs this build's 2.1e-16);
- the σ-quadrature figure (2.37e-16);
- the libMAT build provenance, which is not checked;
- the stale `MEHFC` provenance string.

**Noted, not blocking:**
- n_eff ≈ 19 (§9).
- The 6.8707% control is against E_U; against E_C the same blocks give 6.827%. The VL172 Fig. 6/7 control
  uses E_C, as recorded in §4.

This used one review out of the plan §5 budget (one review plus up to two focused re-reviews). The
corrections above are wording and provenance only, so no numerical re-review was run.

## 9. Disclosure points for the re-quote (grant §3; for the paper-tighten lane)

- **Published flux block.** It is 4.01% per-cell median and 4.00% integral (Stage B), above this
  repaired band's 3.655% / 3.557%. The reason is not established from the release. The leading
  inference is that the paper used the looser FHC-only ν-e constraint, whereas MAT `35097b65` loads the
  combined FHC+RHC+IMD file.
- **Few effective universes.** The weighted band rests on n_eff ≈ 19 universes, a rough ±16% relative
  sampling scatter on σ. That is MAT's convention, not a defect of this build.
- **Repaired total vs paper.** The repaired total median, 6.09%, is below the published 6.85%, and the
  combined χ²/ndf against the paper rises from 0.914 to 0.994.
- **Open items (Stage B).** These can move the construction in either direction:
  - G1 can bias the central value;
  - G2 affects completeness in the systematic universes;
  - the July sweep is provisional;
  - KI 91–94 remain open;
  - C07′ has no band.

## 10. Limits

- Only the two named defects are repaired. The universe outputs are the May flux-fixed sweep, the
  adopted inputs, which carry KI 93 (Stage B §2.5).
- The X01 fix uses MAT's correlated-flux universes. No paper-derived flux × muon-energy cross block is
  added; adding one would double-count (Stage B verification).
- The adopted rollup file is unchanged on disk. Nothing in a publication or deliverable namespace was
  written.
