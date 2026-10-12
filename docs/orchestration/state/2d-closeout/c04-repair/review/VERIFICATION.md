# Independent verification: C04+X01-repaired 2D covariance (grant AUTHORIZATION-20261012-2d-closeout-fluxrepair)

**Verifier:** a fresh, read-only session that wrote its own code. I did not open, copy or run the builder's
scripts (`build_repair.py`, `run_repair.sh`, `make_sigma_json.py`; I only hashed them) or the Stage-B
verifier's scripts. From the Stage-B verifier I read only `verify_c04.json`, as data, to compare input digests.
**Same-model caveat:** I am the same model family as the builder (Claude). This is an independent
implementation, not an independent reasoner.
**Date:** 2026-10-12. **Repo:** origin/main `09c8bae0` (grant sha256 `1b079177…2c75`, which matches the
REPORT). **NERSC:** saul login05 only. No Slurm: `sacct -X -u josephrb --starttime 2026-10-12` returns its
header and no rows. **MAT source:** `MINERvA101/MAT` at `35097b65ab1680db8058f9ede18fecffdc3a1ea3`.

## Verdict table

| # | Claim | Verdict | Mine | Builder |
|---|---|---|---|---|
| 1 | Input pins (E_U, VL172 rollup, VL170 boot, ML, flux band, constraint) | CONFIRMED | all 6 match, full sha below | same |
| 1 | 24 per-playlist flux files, 187 universe outputs | CONFIRMED | 30/30 equal to the Stage-B verifier's digests. Concatenated shas: Flux `39eca81f…dcdc7f`, MINOS `519b2b43…dc763`, all 187 `8e22297e…3c88` (case-sensitive sort, no separator). build.json: 31/31 inputs equal mine | same |
| 2 | Repaired Flux block = weighted CalcCovMx | CONFIRMED, **bitwise** | max\|Δ\|/max\|C\| = 0.0 | — |
| 2 | Rescaled MINOS outputs | CONFIRMED | 3.1e-16 vs `minos_rescaled.npz:x_rescaled`; scale factors 4.4e-16 | — |
| 2 | MINOS block | CONFIRMED (not bitwise) | 5.3e-15 | — |
| 2 | Universe total (repaired) | CONFIRMED (not bitwise) | 4.2e-16. The same against my fully-from-raw total | — |
| 2 | hCov_combined (repaired) | CONFIRMED (not bitwise) | 4.2e-16 | — |
| 2 | Export `universe_plus_boot` / `ml` / block sum | CONFIRMED | upb = repaired-file hCov_combined **bitwise**; vs mine 4.2e-16; `ml` = ML hCov2D_reported **bitwise**; block sum vs mine 4.2e-16 | — |
| 3 | Other 42 bands + normalization byte-identical to adopted | CONFIRMED | 43/43 `np.array_equal`. Changed keys: exactly Flux, MINOS, total, combined, and the two hSigma maps. Extra key: `hReportedCells` only (equals E_U>0); none missing | same |
| 3 | Control file reproduces adopted total and combined | CONFIRMED, **bitwise** | 0.0 / 0.0; no hCov key differs | same |
| 4 | MAT weighted Flux (`SetUnivWgts`, `GetSysErrorMatrix`/`GetTotalErrorMatrix`) | CONFIRMED | 1.099e-15 | 1.10e-15 |
| 4 | MAT unweighted Flux vs stored adopted block | CONFIRMED | 8.40e-16 | 8.4e-16 |
| 4 | MAT rescaled MINOS vs repaired block | CONFIRMED | 6.48e-17 | 6.5e-17 |
| 4 | MAT whole repaired universe (44 vert bands, Flux weighted) vs repaired total − norm | CONFIRMED (≤1e-12); **number differs** | 4.24e-16 (5.3e-17 vs my raw-built total) | 2.1e-16 |
| 4 | MAT whole adopted universe vs adopted total − norm | CONFIRMED | 5.22e-17 | 5.2e-17 |
| 5 | Flux per-cell median | CONFIRMED | 4.9930 → 3.6549 % | 4.993 → 3.655 |
| 5 | Flux integral σ | CONFIRMED | 4.8932 → 3.5569 % | 4.893 → 3.557 |
| 5 | MINOS median / integral | CONFIRMED | 2.3049 → 2.2810 % / 0.1130 → 0.3675 % | 2.305 → 2.281 / 0.113 → 0.367 |
| 5 | Block-sum per-cell median | CONFIRMED | 6.87066 → 6.08980 % | 6.8707 → 6.0898 |
| 5 | Block-sum integral σ | CONFIRMED | 5.3912 → 4.2303 % | 5.391 → 4.230 |
| 5 | Every budget.json field (45 bands + 5 blocks × median/p84/min/max/integral, adopted and repaired) | CONFIRMED | worst relative difference 2.4e-12 (MINOS min, repaired); all others ≤1.0e-15 | — |
| 5 | Φ_MINOS,u/Φ_CV | CONFIRMED | 1.0004186 / 0.9953532, flat in pT (spread 0.0); per playlist within 6e-7 | same |
| 5 | Weights Σw, n_eff | CONFIRMED | 211.012, 19.0605; range 1.0565e-5–26.953; identical in all 12 playlists; equal to constraint idx 0–99 (max diff 0.0) | 211.01, 19.06 |
| 5 | χ²/ndf combined, log-N, stat-subtracted | CONFIRMED | 0.9143 → 0.9942; 0.9324 → 1.0138; 4.1279 → 5.8027 | 0.914 → 0.994; 0.932 → 1.014; 4.128 → 5.803 |
| 5 | χ² values | CONFIRMED | 187.44 → 203.81; 846.22 → 1189.56 | same |
| 5 | Pull mean/RMS (std; substat) | CONFIRMED | 0.041/0.386 → 0.048/0.406; 0.035/0.425 → 0.041/0.447 | same |
| 5 | Paper-cov χ²/ndf | CONFIRMED | 2.6542 (log-N 2.6937) | 2.654 |
| 5 | Fig. 6/7 E_U Total p∥ / pT | CONFIRMED | 5.881 → 4.843; 6.215 → 5.310 | same |
| 5 | Fig. 6/7 E_U Flux p∥ / pT | CONFIRMED | 4.901 → 3.543; 4.889 → 3.552 | same |
| 5 | All 16 curve medians and maxima, per summary (EU_adopted, EU_repaired, control_EC_adopted) | CONFIRMED | 48/48 equal at printed precision | — |
| — | Control: adopted path reproduces VL173 | CONFIRMED | builder `chi2/{adopted,control}_{std,lognormal,substat}.txt` equal the committed `chi2_lgbm42{,_lognormal,_substat}.txt` line by line except path and ROOT-warning lines; my own numbers agree | — |
| — | Control: VL172 | CONFIRMED | 6.8707 % is the per-cell block-sum median **with E_U**. With the exact-split E_C it is 6.827 %. The Fig. 6/7 control `control_EC_adopted_summary.txt` (E_C) equals the committed VL172 summary apart from the header. My EC Fig. 6/7: 5.900 / 6.220 | — |
| — | Committed export `f04f496a…` = adopted hCov_combined + ML | CONFIRMED, **bitwise** (both keys). The builder's `cov2d_blocks_205_control.npz` has the same sha256 | — |
| 6 | CFS copy | CONFIRMED, with one count note | `sha256sum -c` passes on all **61** entries (not 58: the σ JSON, `make_sigma_json.py` and `inputs/remote_reduce.json` were added at 09:08). 61/61 equal the pscratch files. CFS SHA256SUMS = pscratch SHA256SUMS; its sha is `ccb0230d…b34c`. Every pscratch file in build/chi2/fig67/inputs/logs/scripts is listed | REPORT says 61 |
| 7 | Construction review | No defect found | see §Concerns | — |
| 8 | REPORT.md numbers | CONFIRMED except two minor differences | see §REPORT check | — |

## Controls (my code on adopted inputs)

- My mean-centred blocks from the raw sweep, summed with the stored normalization, match the adopted
  `hCov_universe_total` to 5.2e-17.
- With `analyze_universes.py`'s exact formula (Δ = X − E_U, then mean-centre, 1/N), all **44/44** stored
  blocks reproduce **bitwise**. My plain mean-centring of raw X gives up to 1.4e-6 on MaNCEL, a cancellation
  effect of my formula, not of theirs.
- The adopted total equals its stored blocks summed in analyze_universes order (sorted bands, then the
  normalization): **bitwise**. hCov_combined = total + boot: **bitwise**.
- The normalization block equals (0.014·E_U)(0.014·E_U)ᵀ **bitwise**, so the adopted rollup was built with E_U
  as its CV. Against E_C the difference would be 5.3 %.
- The sweep's own CV file `universe_sweep_fluxfix/…_CV.root` is bitwise equal to E_U.
- Flux integral, POT-combined: weighted mean/CV = 0.99968 against unweighted 1.04892; σ = 3.526 % weighted
  and 5.157 % unweighted. `hFluxCV`/`hFluxUniv` match my combination to 3.5e-16 / 4.6e-16.

## Construction review (task 7)

**Weight ↔ universe alignment.** Verified three ways:
1. *Source code.* The weight branch index is the position in the band vector
   (`runEventLoopOmniFold.cpp:344-350@09c8bae0`). The flux-integral band hist u is the PPFX universe u
   (`FluxReweighter.cxx:1343-1356@35097b65`).
2. *Weights against flux histograms.* `GetUnivWgts()` is read on the same band whose hist u, POT-combined,
   equals `hFluxUniv` column u to 4.6e-16.
3. *Outputs against flux columns.* The sweep's Flux_u divided by the pre-rescale `uq/…_Flux_u.root` equals
   Φ_CV/hFluxUniv[:,u] to 2.2e-16. Shifting by one universe gives 1.1e-3.

A statistical check agrees. The weighted cross-section universe mean/CV (median over cells) is 1.0015
aligned, against 0.9565 unweighted. Under 2000 random permutations of the weights, none comes as close to
1; the median |dev| is 4.4 %.

**CV centring.** It does not matter for the weighted block: MAT centres on the weighted universe mean
(`MnvVertErrorBand.cxx:260-305` weighted mean, `:363-391` weighted covariance normalised by Σw), and the CV cancels.
For information, CV-centring with the weights gives a Flux median of 3.693 % instead of 3.655 %, because the
weighted mean sits only 0.15 % from the CV.

**X01 direction, axis and index.**
- *Direction and axis.* The cross section divides by Φ per pT bin, the x-axis
  (`unfold_2d_omnifold_unbinned.py:1252-1260`). Only Flux swaps Φ (`:1709-1715`), so MINOS outputs divided by
  Φ_CV. Multiplying by Φ_CV/Φ_MINOS,u therefore yields ÷Φ_MINOS,u, which is the right direction. Factors:
  0.99958 (u0) and 1.00467 (u1).
- *The axis is moot.* Φ is flat in pT (spread 0.0).
- *Index.* MAT pushes −1σ first (`MuonSystematics.cxx:50-51`) and maps nsigma<0 to flux universe 0
  (`:180`, `:198`). The integrated-flux band takes `GetHist(u)` (`FluxReweighter.cxx:1379-1386`). So output
  u ↔ Φ_MINOS,u.
- *Which Φ_CV.* The outputs' `hFlux_pt` equals `runEventLoopMC_MEFHC.root`'s flux bitwise and my
  POT-combined CV to 1.7e-16. The combination rule matches `build_flux_universe_band.py:15,67-75`.

**Nothing else changed.** See task 3 above. Boot and ML are untouched inputs.

**Export form for Fig. 1.**
- *Form.* The keys (`universe_plus_boot`, `ml`), shapes (205×205) and dtype match the 2026-10-11 export, and
  the cell order is C-order over E_U>0, equal to the paper mask. `make_fig1_lgbm42.py:46` consumes exactly
  `universe_plus_boot + ml`, so the object is right.
- *As committed, the maker rejects it.* With the unchanged committed `remote_reduce.json` (`2ecfc243…`),
  the maker's total-σ assertion (`make_fig1_lgbm42.py:50-51`) **fails** on this export; I emulated it. With
  `sigma_abs_205_repaired.json` it passes. The repaired export's diagonal matches the quadrature to 2.37e-16;
  the boot and ml vectors are bitwise equal to `remote_reduce.json`; the universe σ matches √diag of the
  repaired total exactly. The builder discloses this.
- *Symmetry.* The repaired `universe_plus_boot` is not bitwise symmetric: 2.64e-17, against exactly
  symmetric for the committed export. Disclosed.

## Concerns (none blocks the claim)

1. **A provenance string names a missing file.** The two MINOS outputs record `fluxSource =
   …/baseline_flux/runEventLoopMC_MEHFC.root` (note "MEHFC"), and no such file exists now. The stored
   `hFlux_pt` equals the existing `runEventLoopMC_MEFHC.root` flux bitwise, so the rescale is numerically
   unaffected. REPORT line 61 does not mention the stale name.
2. **The MAT library build is not verified.** I checked the MAT *source* commit, not that
   `opt/lib/libMAT.so` was built from it. I used the same library as the builder, so the MAT agreement is
   agreement with that library.
3. **The weighted band rests on n_eff = 19.06**, roughly ±16 % on σ. Disclosed.
4. **The E_C/E_U distinction matters for the 6.87 % control.** 6.8707 % holds against E_U. Against the
   exact-split central the adopted per-cell block-sum median is 6.827 % (repaired 6.058 %). The VL172
   Fig. 6/7 file uses E_C. The REPORT keeps the two controls separate (lines 104 and 106); the task brief
   phrased them as one.

## REPORT.md check (`…-closeout-c04repair-20261012/docs/orchestration/state/2d-closeout/c04-repair/REPORT.md`)

Every number on lines 6, 33-41, 43, 58, 61, 66, 84-91, 100-106, 110-112, 114, 124-130, 133, 140-144, 153-159,
170, 176, 180, 188, 195-199, 206, 210-211, 218 and 226 agrees with my results:
- lines 124-130: all 35 table cells, including the √tr C values;
- line 226: published flux block from the release ROOT file, 4.013 % median and 4.002 % integral;
- line 206: 61 files and SHA256SUMS sha `ccb0230d…`;
- line 213: all 30 files in the c04-repair directory match `SHA256SUMS.nersc` by hash;
- line 43: build.json has 76 checks, 76 pass.

Discrepancies:

| line | REPORT | mine | note |
|---|---|---|---|
| 113 | whole repaired universe block vs MAT: 2.1e-16 | 4.24e-16 against the repaired total − norm (5.3e-17 against my raw-built total) | Both are ≪ 1e-12. The exact figure does not reproduce, probably a different operand or normaliser. |
| 193 | quadrature vs √diag of export: 2.2e-16 | 2.37e-16 (max element-wise relative) | Minor; the `rtol=1e-12` test passes. |
| 94 | libMAT.so "built from MAT 35097b65" | NOT CHECKED | Source HEAD is 35097b65; library provenance not measured. |
| 8 / 220-222 | "independent verification in §8" / "Pending" | — | Expected: this report fills it. |

## Code paths read (file:line@sha)

- `2d-unfolding/compare_to_paper_fullcov.py@09c8bae0`:
  - `:95-108` (mask diag>0, pinv, ndf = n_keep);
  - `:111-129` (log-normal);
  - `:132-164` (embedding at the reported mask);
  - `:227-251` (`--subtract-stat`: total − stat; combined);
  - `:256-259`, `:284` (pull on the combined diagonal, population std).
- `2d-unfolding/uq/plot_uncertainty_fig6_7_style.py@09c8bae0`:
  - `:123-144` (grouping; normalization included);
  - `:178-218` (P, central projection, fractional σ);
  - `:293-308` (boot into Statistical; ML into the total).
- `2d-unfolding/uq/analyze_universes.py@09c8bae0`:
  - `:67-97` (categories);
  - `:242-260` (Δ, mean-centred 1/N);
  - `:273-279` (normalization);
  - `:329` (combined).
- `2d-unfolding/unfold_2d_omnifold_unbinned.py@09c8bae0`: `:1207-1260` and `:1700-1726`.
- `2d-unfolding/uq/build_flux_universe_band.py@09c8bae0`: `:15` and `:67-75`.
- `MINERvA101/MINERvA-101-Cross-Section/runEventLoopOmniFold.cpp@09c8bae0`: `:344-350`.
- `docs/orchestration/receipts/2d-lgbm42-20261011/make_fig1_lgbm42.py@09c8bae0`: `:44-53`.
- MAT `35097b65`:
  - `MnvVertErrorBand.cxx:260-390` and `:579-597`;
  - `MnvH1D.cxx:1363-1398` and `:2125-2156`;
  - `FluxReweighter.cxx:997-1030` and `:1340-1398`;
  - `MAT-MINERvA/universes/MuonSystematics.cxx:50-51`, `:170-204`.
- The committed producers in `$NS/repo` are byte-identical to origin/main:
  - `compare_to_paper_fullcov.py`: `05075acb…1215`;
  - `plot_uncertainty_fig6_7_style.py`: `4e1aafd5…c9e7`.
  I re-ran both unchanged on the repaired file. `repaired_lognormal.txt` and `EU_repaired_summary.txt` are
  identical to the builder's, apart from path and wrote lines.

## Input sha256 (re-measured)

| input | sha256 |
|---|---|
| E_U `uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root` | `4f5a1b6d44b9e7212b233650bb00bfb626ae65461e3bf8033cd67866dbd7eb2c` |
| E_C `2d_crossSection_omnifold_MEFHC_5iter.root` | `142a45b0efc753d91e95376c28ac3f6a477d582014a919e49d6d71079a127fd5` |
| adopted rollup | `077912e3e7a53376c6df89ee1af4a2a504fe1f49423bab88780204beccd952f5` |
| bootstrap VL170 | `71a75821ceeb658710adca30243e39e7184e33f868f58ea56cffe63ba8db0115` |
| ML | `3b6b48ec89207ae29dc7bb0ddc5a41836c359c4805877d663731694b828d5db9` |
| `flux_integral_universes_MEFHC.root` | `5eecae84509ba8ededbe8fdee63508d8e36cd057cc0547a940383f80248580eb` |
| `runEventLoopMC_MEFHC.root` | `d40aea69235cdc98644e1bb3e622e579d6b81904c004c83fe50465079989f316` |
| constraint file | `e38ad7d28354d071577113a18c8c569f88b6239f7fb193d20285273f172fc0c2` |
| paper release ROOT | `6c6dce72050bb8f128fab8e286349b250bc60d1c767e162bf15a0f009f3573e3` |
| runEventLoopMC_1A / _1P | `d54d2a2c…1107` / `3d98169a…77f3` |
| pre-rescale `uq/…_Flux_{0..99}.root` (concatenated) | `b8ef1247…0f20` |
| builder repaired rollup | `da92c5d2567647e8613bb3a6522176dbd9a287970082b45ac9e83e24684b1948` |
| builder control rollup | `eba9f4bed606c5fef6de5fec6e9c18c4f994a2f9f8c9e4a25c16a0ca97cc4637` |
| builder export | `c2606f9095c61e3b0d56bbb72d4c6948b5662461da51563858ce3c8ae18824f8` |
| builder control export = committed export | `f04f496aa7ad04b76a5879e495bb18dbf44816f5f45412d8e444a983677317dc` |
| builder `minos_rescaled.npz` | `8912376ef2a6cfce8bed515cc945d9d5778cf5c838154a685435c3c7ce25416d` |
| builder `sigma_abs_205_repaired.json` | `4e48f6392c9e84a5ad2f9b32bf01ac854f5b63ce2003d3b366a1956b8ee80ef8` |

## My scripts and outputs (`/pscratch/sd/j/josephrb/2d-closeout-c04repair-20261012/verify/`; the scripts are also in the local scratch dir)

| file | sha256 |
|---|---|
| `vrep.py`: main rebuild, MAT, budgets, χ², Fig. 6/7 | `f7ed03d9b180c5023def683df0d24fcaa9335304fcfca989bee0be9b49c9310e` |
| `vcmp.py`: comparison with budget.json, chi2/*.txt, fig67 summaries, build.json | `76e2a60cad5cae7b21232a24e3eaf4ca6c016d2cb3ff832c9422bd3360e37ede` |
| `vsig.py`: σ JSON and Fig. 1 maker assertions | `161776ae8eb6fed442943a36cba5986d81df7d5d9d580e9af7326f51149f91be` |
| `vextra.py`: REPORT-specific checks | `6857bc8a9cb9cf5995ada5c48101724bce4f0ec2c3bad5890c5ab9c56a577f09` |
| `vrep.json` / `vcmp.json` / `vextra.json` | `e0c18e2c…f041` / `1d5dbd61…bb67` / `21275d55…6eda13` |

## State after verification

- The builder's pscratch tree passes `sha256sum -c SHA256SUMS` (0 failures), so it is unchanged.
- Nothing was written to CFS or to any repo.
- The main checkout is at `e25abfd5`, with the same 3 modified and the same untracked files as at session
  start.
- No commits, pushes or Slurm jobs.
