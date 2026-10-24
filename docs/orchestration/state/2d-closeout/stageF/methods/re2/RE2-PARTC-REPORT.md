# RE-2 part C report: the refined post-processing, its published comparison and C_model (2026-10-24, re-1 lane)

**Status.** Part C ran as bound by `RE2-BINDING-C.md`, amendment 1 and amendment 2.
- **The products.** The refined chain ran end to end: 36 steps at rc 0, from a clean deploy of `903fb78b`. It
  produced `Q_R`, its blocks, the published comparison on `E_R` and `Q_R`, C_model beside `Q_R`, and the values
  table.
- **Determinism.** The rerun's products equal the stopped run's. The verdict came from the **amendment-2 comparator
  (`d108286c`) over the `903fb78b` products**: PASS, 66 of 66.
- **Fig. 1** was drawn on the laptop in the recorded environment.
- **HPSS.** The run's products and records are on tape, with recovery tested.

**MEASURES:** the refined 2D covariance `Q_R` and its blocks; the published comparison on `E_R` and `Q_R`; C_model
beside `Q_R`; the regenerated value of every printed number whose control reproduced.

**CANNOT AUTHORIZE, and this report makes none of these:**
- an adoption statement: adopting `E_R` and `Q_R` is Joseph's decision;
- a claim change;
- folding C_model into `Q_R`;
- any printed wording;
- an edit to `docs/analysis-note/`;
- a coverage statement about `Q_R`.

Every number below is a measured value of the products named. None is a claim.

Paths: `$B` = `/pscratch/sd/j/josephrb/2d-closeout-re2-20261023`. The records are in [`run/partc_r2/`](run/partc_r2/) and,
for the stopped run, [`run/partc_stopped/`](run/partc_stopped/) (`RE2-PARTC-STOP.md`).

## 1. The runs and the digest checks

| run | deploy (HEAD, clean) | digest check before C1 | outcome |
|---|---|---|---|
| the bound run, `$B/partc` | `e079ff05447cd36e754654f94b166a6481d3005a` | the declaration's §12: **25/25 OK** | C1–C12 at rc 0; **stopped at C13** (row `s2-bkg-share`), reported; amendment 1 |
| the rerun, `$B/partc-r2` | `903fb78b941a2f889bfcc5092e41ce27f5add898` | amendment 1's 29 rows: **29/29 OK** ([`preflight.log`](run/partc_r2/partc-r2_preflight/preflight.log)) | **36 steps at rc 0**, 16:17:41–16:19:35Z, login12 |
| determinism, first | the rerun's deploy (`903fb78b`) | — | **FAIL**: 6 of 66 differed; reported; amendment 2 |
| determinism, bound | `d108286c43091b06f5c8321265041c9460c4c27a` | `$B/partc-r2`'s own `SHA256SUMS`: **128/128 OK**; amendment 2's 29 rows: **29/29 OK** ([`determinism-amend2.log`](run/partc_r2/partc-r2_preflight/determinism-amend2.log)) | **PASS**, 66 of 66 |

**The 15-minute stop never came close:** the chain took 114 s, and its longest step was 8 s.

**The charge** was 0 node-h, on a login node with no Slurm job. RE-2's grant room stays **36.8162 node-h**.

**Storage:** nothing was written to CFS.

### 1.1 Determinism: three verdicts, all kept

1. **The first verdict, the amendment-1 comparator: FAIL**
   ([`determinism.json`](run/partc_r2/partc-r2_preflight/determinism.json), `b7085a8b…`).
   - 66 files compared: 60 equal, 6 differ, 0 one-sided.
   - Every differing value was a recorded sha256 of a ROOT file, or of a path-bearing record that was itself equal
     after the path pairs.
   - **The 6 differences:**

     | file | the differing values |
     |---|---|
     | `s5/s5.json` | the S5 ROOT's digest |
     | `pins_q.json` | the s5_root, s5_json and combination_json digests |
     | `outA/budget_Q.json` | 7 input-pin digests of the same three |
     | `playlist/playlist_term.json` | `inputs.analysis_json.sha256` |
     | `combination/combination.json` | `inputs.analysis_json.sha256` |
     | `outA/SHA256SUMS` | 4 ROOT files, `budget_Q.json` and `cov2d_Q_205.json` |

     No measured value differed. RE2-PARTC-STOP §6 has the field-by-field diff.
2. **The dry check, a disclosed record and not the verdict**
   ([`determinism_dry_amend2.json`](run/partc_r2/determinism_dry_amend2.json)).
   - It was the amendment-2 comparator, run before binding. It wrote only `$B/review/det-dry/`.
   - PASS: 66 of 66, 27 learned pairs in 4 iterations.
3. **The bound verdict: the amendment-2 comparator from a clean deploy of `d108286c`, over the `903fb78b` products:
   PASS** ([`determinism-amend2.json`](run/partc_r2/partc-r2_preflight/determinism-amend2.json), `5e6a89be…`).
   - **66 of 66 compared files equal.** 0 one-sided, 0 untabled ROOT.
   - **27 learned digest pairs, in 4 fixpoint iterations:**
     - 5 `root-twin`;
     - 2 `json-rule` (the two receipts' run-context fields);
     - 20 `equal`.
   - **Skipped, each named:** 22 PDFs, 29 logs and caches, 5 ROOT files, 10 tmp scratch files, and the 2 values-table
     files.
   - **Both before and after the comparison,** `sha256sum -c` of `$B/partc-r2/SHA256SUMS` gave 128 of 128 OK. Nothing
     was written into `$B/partc-r2` except, afterwards, C10's `fig1/` (§9).

## 2. The steps, and the chain of custody

All 36 steps of [`steps.tsv`](run/partc_r2/partc-r2/logs/steps.tsv) are below, with their argv abbreviated. The full
argv is in the file.

| step | rc | s | argv (abbreviated: $D = the deploy, $P = 2d-unfolding/re2/partc, $O = $B/partc-r2) |
|---|---|---|---|
| analyze_c0 | 0 | 2 | `$P/re2c_analyze.py --arm refined c0 $O/results/c0.json` |
| analyze_s3 | 0 | 2 | `$P/re2c_analyze.py --arm refined s3 $O/results/s3.json` |
| analyze_s4ii | 0 | 2 | `$P/re2c_analyze.py --arm refined s4ii $O/results/s4ii.json` |
| analyze_s1 | 0 | 2 | `$P/re2c_analyze.py --arm refined s1 $O/results/s1.json` |
| analyze_s4i | 0 | 2 | `$P/re2c_analyze.py --arm refined s4i $O/results/s4i.json` |
| rollup | 0 | 7 | `$P/re2c_rollup.py --arm refined --out $O/s5 --results $O/results` |
| export_cov | 0 | 3 | `$P/re2c_export_cov.py $O/work_cov/work_cov.npz $O/work_cov/cov_controls.json --arm refined` |
| periods_selftest | 0 | 7 | `$P/re2c_analyze_periods.py --arm refined --work-cov $O/work_cov/work_cov.npz 00a05fefa67f787786fa2f2bf0de54fec9d1d149af8c099c3bbaef8c7efc9f34 --ns …` |
| periods_control | 0 | 1 | `$P/re2c_analyze_periods.py --arm refined --work-cov $O/work_cov/work_cov.npz 00a05fefa67f787786fa2f2bf0de54fec9d1d149af8c099c3bbaef8c7efc9f34 --ns …` |
| periods_roles | 0 | 1 | `$P/re2c_analyze_periods.py --arm refined --work-cov $O/work_cov/work_cov.npz 00a05fefa67f787786fa2f2bf0de54fec9d1d149af8c099c3bbaef8c7efc9f34 --ns …` |
| periods_analyze | 0 | 8 | `$P/re2c_analyze_periods.py --arm refined --work-cov $O/work_cov/work_cov.npz 00a05fefa67f787786fa2f2bf0de54fec9d1d149af8c099c3bbaef8c7efc9f34 --ns …` |
| playlist | 0 | 3 | `$P/re2c_playlist_term.py $O/periods/analysis.json $O/playlist --arm refined --analysis-sha 2ce5d5dab3e566590504ba0f186a90b0334e7e691dbda011403fc99a…` |
| combine | 0 | 2 | `$P/re2c_combine.py $O/periods/analysis.json $O/playlist/playlist_term.npz $O/s5/production_cov.npz $O/combination --arm refined --pins 2ce5d5dab3e5…` |
| build_q | 0 | 6 | `$P/re2c_build_q.py --repo $D --arm refined --pins-json $O/pins_q.json --eu-control $A/2d-unfolding/uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root --s…` |
| chi2_std | 0 | 4 | `$D/2d-unfolding/compare_to_paper_fullcov.py --ours $B/partb/out/ER/xsec.root --out-prefix $O/chi2/chi2_Q_std --omnifold-cov $O/outA/uq_adopted_cova…` |
| chi2_lognormal | 0 | 3 | `$D/2d-unfolding/compare_to_paper_fullcov.py --ours $B/partb/out/ER/xsec.root --out-prefix $O/chi2/chi2_Q_lognormal --omnifold-cov $O/outA/uq_adopte…` |
| chi2_substat | 0 | 4 | `$D/2d-unfolding/compare_to_paper_fullcov.py --ours $B/partb/out/ER/xsec.root --out-prefix $O/chi2/chi2_Q_substat --omnifold-cov $O/outA/uq_adopted_…` |
| oo_universe | 0 | 2 | `$D/2d-unfolding/uq/_ours_only_chi2.py --ours $B/partb/out/ER/xsec.root --universe-cov $O/outA/uq_adopted_covariance.root --universe-hist hCov_unive…` |
| oo_universe_plus_stat | 0 | 2 | `$D/2d-unfolding/uq/_ours_only_chi2.py --ours $B/partb/out/ER/xsec.root --universe-cov $O/outA/uq_adopted_covariance.root --universe-hist hCov_unive…` |
| oo_Q | 0 | 2 | `$D/2d-unfolding/uq/_ours_only_chi2.py --ours $B/partb/out/ER/xsec.root --universe-cov $O/outA/uq_adopted_covariance.root --universe-hist hCov_Q` |
| fig67 | 0 | 4 | `$D/2d-unfolding/uq/plot_uncertainty_fig6_7_style.py --xsec-root $B/partb/out/ER/xsec.root --universe-root $O/outA/uq_adopted_covariance.root --boot…` |
| stat_figs | 0 | 3 | `$D/2d-unfolding/uq/plot_bootstrap_figs.py --cov $O/outA/block_stat.root --outdir $O/stat` |
| check_rebuild | 0 | 0 | `$P/re2c_check_rebuild.py $O` |
| agreement | 0 | 2 | `$D/2d-unfolding/agreement_windows_receipt.py --ours $B/partb/out/ER/xsec.root --out $O/receipts/RECEIPT-agreement-windows.json` |
| chi2_paperonly | 0 | 3 | `$D/2d-unfolding/compare_to_paper_fullcov.py --ours $B/partb/out/ER/xsec.root --out-prefix $O/receipts/paperonly` |
| tune | 0 | 2 | `$D/2d-unfolding/receipt_model_chi2_2d.py --ours $B/partb/out/ER/xsec.root --out $O/receipts/receipt_model_chi2.json` |
| models | 0 | 4 | `$D/2d-unfolding/compare_to_models.py --ours $B/partb/out/ER/xsec.root --out-prefix $O/receipts/figs/model_comp` |
| tension | 0 | 4 | `$D/2d-unfolding/diagnose_tension.py --ours $B/partb/out/ER/xsec.root --out-prefix $O/receipts/figs/tension` |
| fig13 | 0 | 5 | `$D/2d-unfolding/plot_2d_threeway_fig13.py --infile $B/partb/out/ER/xsec.root --paper $A/2d-unfolding/minerva_paper_anc/cov_ptpl_minerva_inclusive_6…` |
| paper_slices | 0 | 7 | `$D/2d-unfolding/plot_2d_paper_comparison.py --infile $B/partb/out/ER/xsec.root --prefix $O/figs/MEFHC_5iter_xsec_paper` |
| xsec_proj | 0 | 7 | `$D/2d-unfolding/plot_2d_cross_section.py --infile $B/partb/out/ER/xsec.root --prefix $O/figs/MEFHC_5iter_xsec` |
| pull_full | 0 | 3 | `$D/2d-unfolding/compare_to_paper_fullcov.py --ours $B/partb/out/ER/xsec.root --out-prefix $O/figs/MEFHC_5iter` |
| reduce | 0 | 2 | `$P/re2c_reduce.py --ec $A/2d-unfolding/2d_crossSection_omnifold_MEFHC_5iter.root --eu $A/2d-unfolding/uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root …` |
| numbers | 0 | 2 | `$P/re2c_numbers.py --arm refined --central $B/partb/out/ER/xsec.root --eu $A/2d-unfolding/uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root --ec $A/2d-u…` |
| cmodel | 0 | 1 | `$P/re2c_cmodel.py --cmodel-json $D/2d-unfolding/pv2d/cmodel/cmodel_2d.json --q-purity /global/cfs/cdirs/m3246/josephrb/2d-closeout-stageF-rebuild-2…` |
| values | 0 | 0 | `$P/re2c_values.py --repo $D --spec $P/re2c_values_spec.tsv --refined-dir $O --out-tsv $O/values_table.tsv --out-json $O/values_table.json` |

**The chain of custody** ([`chain.json`](run/partc_r2/partc-r2/chain.json)). Each product's sha256 was the next step's
pin.

| record | sha256 |
|---|---|
| `work_cov/work_cov.npz` | `00a05fefa67f787786fa2f2bf0de54fec9d1d149af8c099c3bbaef8c7efc9f34` |
| `periods/analysis.json` | `2ce5d5dab3e566590504ba0f186a90b0334e7e691dbda011403fc99a8c8d92cd` |
| `playlist/playlist_term.npz` (C_PL_R) | `dbb067aa3c1085b2c40b89c5ace165eadb5721148d72eb1496edc14c3a5a7b1e` |
| `playlist/playlist_term.json` | `a952adda441e1fa7d29eb44e064b11991a09ded3682c2530193222e45164ed26` |
| `s5/production_cov.npz` (S5_R) | `631cf255fff43b5cb35acd9cefdcee99e5ee95b85dc2f30d8e0aca513095eea1` |
| `combination/s5_plus_playlist.npz` (`Q_R`) | `b57d6c96fb143952f82f6466c36f017ad17327983618f837eff97364c8c33440` |
| `combination/combination.json` | `c663eadb168835bdf965644f1e65531b3dc5eaea9b8d08fc72fa161b6a3009ea` |
| `outA/cov2d_Q_205.npz` (`Q_R` and its blocks on the 205 cells) | `7153b194b95c27f80db5997bdde35fe2475f2b1c40c9ff456edd409850cf47d2` |
| `outA/budget_Q.json` | `bbe13622656e9f43978d9cb022ac74ca4ba059b1cf56fed9e082bfb3b1be03aa` |
| `reduce.json` (Fig. 1's central values) | `823f16b1b694477b053e71cc8a1fdc13cebf9ee51a99df3f88752c1447f4184e` |

## 3. Every refined product's digest

- **All 128 files the run wrote:** [`run/partc_r2/partc-r2/SHA256SUMS`](run/partc_r2/partc-r2/SHA256SUMS), sha256
  `bf259be46ef1c4ddf8e6a18bfd49e1626b04f9a284e42a4024403e66ed60e25b`. It was checked 128 of 128 OK, before and
  after the determinism comparison. Besides the chain above, it holds `cmodel/cmodel_R.npz` (`bb0405f9…`), the
  ROOT files, the figures, the receipts and the printouts.
- **Fig. 1's outputs** are digested in its `RUN-fig1.txt` (§9).
- **The JSON and text records** are committed in [`run/partc_r2/partc-r2/`](run/partc_r2/partc-r2/). The npz, ROOT
  and figure files are on pscratch and on HPSS (§10).
- **Three records are committed gzipped,** as `stageF/rebuild/outputs/outA/` commits its own: `outA/budget_Q.json`,
  `outA/cov2d_Q_205.json` and `s5/s5.json`.
  - They name the binary products by bare filename, and the repository's receipt-artifact check requires a named file
    to be tracked beside the record.
  - `gunzip -c` of each gives the digest `SHA256SUMS` lists: `bbe13622…`, `ef4c67d2…` and `ec4a407b…`. All three were
    checked.

## 4. The values table

**The run's table** ([`values_table.tsv`](run/partc_r2/partc-r2/values_table.tsv), `.json`) has 250 rows:
- **241 regenerated** after their positive controls reproduced the printed value; 199 of them change at their printed
  precision;
- **8 new products**, with no printed value and so no control;
- **1 declared failure**, **`\fpsAbove` (46)**, not regenerated. 4.502/3.0730 − 1 = 46.50 %, so its definition is not
  established. Integration finds its source or rewords the sentence (RE2-BINDING-C).
- **0 unexpected.**

**Sites for integration by hand:** [`re2c_values_unmatched.tsv`](../../../../../../../2d-unfolding/re2/partc/re2c_values_unmatched.tsv)
lists 25 rows, each with its reason. 22 are sites integration handles by hand:
- numbers printed as words or bounds;
- numbers with no source field;
- D2's movement against `E_U`;
- published-side numbers;
- `sec_systematics.tex:101`'s S2 diagnostic (§11).

The other 3 are exact-split sites classified as unchanged.

**The macros.** Each is regenerated once, at its `values.tex` definition, which covers all of its uses. Every row, with
its purity control value, is in the Appendix.

## 5. The published comparison, on `E_R` and `Q_R`

These come from the same producers as before (P12), with `--ours E_R`, and `Q_R` where they use it. The left column
is the value printed now, which the control reproduced from its purity source.

| printed quantity | printed now (`E_U`, Q) | regenerated (`E_R`, `Q_R`) |
|---|---|---|
| `\sigTwoD`, the 2D total (cm²/nucleon) | 3.073e-38 | 3.069e-38 |
| `\ratioTot`, ours/published total | 1.011 | 1.010 |
| "to 1.1 %" (`sec_results.tex:57`) | 1.1 | 1.0 |
| `\medianBinRatio` | 1.008 | 1.005 |
| `\binsFive` / `\binsTen` / `\binsTwenty` (% of bins within 5/10/20 %) | 82.9 / 95.6 / 99.0 | 86.8 / 95.1 / 99.0 |
| `\pullMean` / `\pullRMS` / `\pullRMSr` | 0.074 / 0.564 / 0.56 | 0.060 / 0.535 / 0.54 |
| `\chiPaper`, χ²/ndf against the published covariance | 2.65 | 2.27 |
| `\chiCombined` / `\chiCombinedLog` / `\chiCombinedSubStat` (published + `Q_R`) | 0.964 / 0.987 / 6.01 | 0.929 / 0.945 / 6.72 |
| tension: diagonal-only χ²/ndf; χ²_norm; χ²_shape | 0.32; 0.06; 544 | 0.29; 0.04; 465 |
| tension: share in the 10 smallest modes (%); the 73 best modes' χ²/ndf; largest band share (%) | 9.5; 0.81; 15 | 9.6; 0.66; 15 |
| Tune v1: ours vs tune, χ²/ndf (data vs tune stays 33.0) | 29.8 | 31.3 |
| `\uqMedian`, `Q_R`'s per-cell median (%) | 6.45 | 6.41 |
| `\uqIntegral`, `Q_R`'s width-weighted total σ (%) | 4.75 | 4.76 |
| `\uqSFiveMedian`, S5_R total (%) | 6.04 | 5.98 |
| `\fluxBand` (%) | 3.75 | 3.71 |
| 3D P3 marginal against the 2D central value: total change (%); median ratio; scatter (%) | 0.001; 1.0000; 3.5 | 0.141; 1.0010; 3.7 |
| learner: median and max of \|x/E_C − 1\| (%) | 0.98; 12.2 | 1.03; 17.6 |

**Unchanged:**
- the published-side values;
- the exact-split comparators;
- the purity coverage history;
- the negative-weight study;
- the 5D and joint-test numbers.

**The wording is Joseph's.** That covers:
- the reworded comparison with MINERvA's published result, including `\chiPaper`'s comparison sentence;
- the three sentences saying the covariance omits the unfolding-model dependence (`paper_body.tex:415-418`,
  `sec_systematics.tex:379-382`, `primer_body.tex:294-296`).

## 6. RE2-PLAN §5.3's readouts ([`partc_numbers.json`](run/partc_r2/partc-r2/partc_numbers.json))

**`E_R − E_U` in `Q_R`'s σ, per cell over the 205 cells:**

| statistic | value |
|---|---|
| median \|d\|/σ | 0.0605 |
| p84 | 0.141 |
| max | 0.478 |
| mean signed | −0.0083 |

**`E_R` against `E_U`:** an integral change of −0.139 %, with \|E_R/E_U − 1\| at a median of 0.440 % and a maximum of
10.13 %.

**Per block, the per-cell ratio of the refined relative σ to the purity one** (σ_R/E_R over σ_U/E_U):

| block | p16 | median | p84 | min | max |
|---|---|---|---|---|---|
| Q | 0.948 | 0.992 | 1.021 | 0.728 | 1.159 |
| S5 total | 0.948 | 0.991 | 1.025 | 0.729 | 1.157 |
| universe | 0.947 | 0.990 | 1.024 | 0.681 | 1.162 |
| stat (S1) | 0.956 | 1.001 | 1.044 | 0.676 | 1.154 |
| C08 (seed) | 0.485 | 0.865 | 1.804 | 0.120 | 5.529 |
| C_PL | 0.872 | 0.998 | 1.090 | 0.492 | 2.505 |

C08 is a rank-4 sample covariance over 5 seed triplets. Its relative standard error is √(2/4) ≈ 0.71 (s5.json
`c08.gaussian_rel_se_of_variance`), which bounds how far a per-cell ratio of two such estimates can be read.

## 7. C_model beside `Q_R` ([`cmodel_R.json`](run/partc_r2/partc-r2/cmodel/cmodel_R.json))

**Label, verbatim:** "generator-shape model dependence; not a calibrated bound".
**Headline, verbatim:** "Q_R; this file's total is the secondary users' total Q_R + C_model, reported beside it".
**Form, verbatim:** "C_model = sum_k s_k s_k^T (M2), kappa = 1, fractional; C_abs = diag(x_R) C_model diag(x_R),
x_R = Q_R's x = E_R".

**Controls, both passed before the refined numbers:**
1. C_model's matrix sha256 is `11fe68188bd31a35103f5eb4708bd6a7cdab8965164680caa6671c509dcd3470`.
2. With the purity Q (`771e49a5…`), C_abs's matrix sha256 is `b11b10a0…2d77`, and the per-cell Q + C_model summary
   equals `cmodel_2d.json`'s exactly (median 7.95 %).

| relative σ | per-cell median | p84 | p90 | max | integral |
|---|---|---|---|---|---|
| `Q_R` | 6.41 % | 8.97 % | 10.20 % | 23.63 % | 4.759 % |
| C_model | 3.71 % | 7.10 % | 8.50 % | 21.10 % | 0.029 % |
| **`Q_R` + C_model, the secondary users' total** | **7.90 %** | 12.32 % | 13.74 % | 24.49 % | 4.759 % |

**What is not in `Q_R`.** `Q_R` is read and not modified, and nothing named Q contains C_model. The matrices'
sha256 are:
- C_abs_R: `5db1955b…9c23`;
- the total: `d4f2b960…9e2c`.

**Caveat, verbatim from the product** (copied from `cmodel_2d.json`): "kappa = 1, unscaled. Not a per-cell bias
bound: on the 127 PV-2D positive-control cells (|bias| > 1 %, the NuWro closure bias of configuration (a)), the
refined arm's NuWro |shift| reaches |bias| in 67, and sqrt(s_GENIE+MEC^2 + s_GiBUU^2), which leaves the bias's own
vertex out, in 72. sqrt(diag C_model) reaches it in 116, but that includes the NuWro shift the bias was made from, so
it is not evidence of coverage. The cells beside a step in r drawn by the noise gate or a cut (PV-2D REPORT §5, post
hoc) go in as measured; they carry most of the large shifts."

**The tail caveat** (`tail_caveat_post_hoc`, verbatim from `cmodel_2d.json`):
- the 52 step-adjacent cells hold 59.4 % of tr C_model;
- its "σ_Q" and total fields are the C_model report's, made with the purity Q.

## 8. RO-FPS (RE2-DECLARATION-B §7.4)

`E_R`'s `hXSec2D.Integral("width")` at 4 significant figures is **3.069e-38**, against the extended-fiducial control's
3.073e-38. **It does not reproduce.** The two values differ by −0.14 %.

The reference is printed as "`VALIDATION_LEDGER.md:1614-1615`, no committed digest". The positive control, `E_U`,
gives 3.073e-38 and reproduces (row `ro-fps`).

## 9. Fig. 1 ([`RUN-fig1.txt`](run/partc_r2/partc-r2/fig1/RUN-fig1.txt))

**How it ran:** `bash re2c_fig1_local.sh refined <workdir> <venv python> $B/partc-r2`, on the laptop, at 16:36:44Z.
- **The environment:** python 3.12.2, matplotlib 3.11.2, numpy 2.5.4.
- **The commit:** `d108286c`, clean.
- **The script:** `re2c_fig1.py` `9d7eb177…`.
- **The inputs:** each read from `chain.json` by digest (`RUN-fig1.txt` lists all of them).

**Its checks passed:**
- cells;
- diag Q_R = diag S5_R + diag C_PL_R;
- per-cell σ against `combination.json`.

**Outputs:** `fig1_validation.pdf` `cabbbbc3db31810a0c000f10cf346a7b5f01e1035f7860bd34d54a8fb0b537ca`. Its inset prints
`Q_R`'s median, 6.41 %, and the residuals mean 0.060, RMS 0.535. It was copied into `$B/partc-r2/fig1/`, as C10
declares, after the determinism comparison.

**Joseph reviews Fig. 1 visually** before integration (ruling Q3).

## 10. HPSS (C14; RE2-DECLARATION-B §8)

**The argv, exactly** ([`hpss.argv`](run/partc_r2/partc-r2_preflight/hpss.argv)):
`bash $B/deploy-d108286c/docs/orchestration/state/2d-closeout/stageF/methods/re2/run/launch/re2_hpss.sh re2-2d-rebuild-partc-20261024 $B 0 partc-r2 partc-r2_preflight partc_preflight`.
- The script is the bound `re2_hpss.sh`, `3db768d5…`.
- Part C writes no unfold outputs, so 0 `xsec.root` files are expected.

**The archive:**
- **Directory:** `/home/j/josephrb/mnv-re2-2d-rebuild-partc-20261024/`.
- **Bundle:** `re2-2d-rebuild-partc-20261024.tar`, 73,994,240 B, sha256
  `f4a14015e0f831cb1fe52284160c499b2e8c173053f354231b4535e610ebd5fa`.
- **Manifest:** `members.sha256`, 153 members, sha256 `b648b858…`. It covers `partc-r2/` with Fig. 1, its preflight
  records, and the stopped run's `partc_preflight/` with its 128-file digest list.

**The steps** ([`run/partc_r2/hpss/re2-2d-rebuild-partc-20261024/logs/`](run/partc_r2/hpss/re2-2d-rebuild-partc-20261024/logs/), all rc 0 in
`rc.tsv`):
- put with `-c on`, then migrate;
- `ls -V`: every object fully at the tape level (73,994,240 / 15,476 / 100 bytes);
- `hashverify -R`: OK on 3 of 3, and the set equals `hashlist`'s;
- recovery into fresh directories:
  - the bundle sha256 matched;
  - every member re-hashed;
  - the path sets agree both ways, 153 and 153, in per-call set files (`6-got.recovery.set`), which the controls no
    longer overwrite;
  - all 6 ROOT files opened;
- the four negative controls each fired (exit 4, 4, 6, 3);
- `du`: 3 files and 74,009,816 bytes, equal to the three objects.

**Caveats:**
- **The quota.** `hpssquota` read 353.98 GiB of 512 both before and after this copy and the earlier one. The quota
  cross-check therefore stays open for both receipts.
- **An incomplete member.** The bundle's `partc-r2_preflight/hpss.out` is that log as it stood when the bundle was
  made, which is before the copy finished. The full log is committed here.

**The pscratch copies** are kept.

## 11. S2: what `Q_R` lacks, and what `sec_systematics.tex:101` becomes (amendment 1, condition 3)

**The purity Q total did not include the S2 term.**
- S5's total is universe + stat + C08: `C_tot = C_univ + C_stat + C08`
  (`stageC/production/s5_rollup.py:473`).
- The docstring says "Reported, not added: the bkg-only separable term (S2)" (`s5_rollup.py:18-20`).
- S2's matrix was saved under the npz key `bkg_separable` (`:497`) and reported as a σ ratio,
  `sigma_bkg_over_sigma_stat_median` = **0.2631** (s5.json, `numbers.bkg_separable`, line 912).
- Q = S5 total + C_PL, so Q does not contain it.
- **So `Q_R` lacks nothing that Q contained.**

**What S2 measured is still inside both stat blocks.** As `sec_systematics.tex:101` says, the separable
background-only term "is contained in the statistical block".
- S1 resamples the background in both arms: `--bootstrap-streams three`, with the refined replicas'
  `re2Refinement.background_stream` true.
- The refined arm's own S2 (J5) was not run. <!-- absence-ok: J5's status is RE2-BINDING-B's (not bound); the refined s5.json records bkg_separable as not computed -->

**What changes at integration.** `sec_systematics.tex:101`'s "a median 0.26 of the statistical σ" is a purity-estimator
diagnostic with no refined value. Integration either cites it as the purity estimator's history or drops the number.
The wording is Joseph's; this report only lists the site, which is also in `re2c_values_unmatched.tsv`.

## 12. The ROOT twins

A ROOT file records its creation time, so the determinism stop compares each ROOT product through the npz written
from the same arrays:
- **The adopted covariance and the blocks.** `outA/uq_adopted_covariance.root`, `block_stat.root`, `block_c08.root`
  and `block_playlist.root` are tied to `outA/cov2d_Q_205.npz`'s `Q`, `stat`, `c08` and `C_PL`.
  - They are written from those arrays at `re2c_build_q.py:704-706`, and the npz at `:713-715`.
  - build_q's read-back (A4, `:678-692`, `:710`) stops unless each ROOT matrix equals its array **exactly**.
  - `block_stat.root`'s `hRel2D` is √diag(stat)/x of the same arrays.
- **The S5 ROOT.** `s5/uq_production_covariance.root` is tied to `s5/production_cov.npz`. build_q's A2 checks
  (`:387-393`) compare its total, universe and every band to the npz **to 1e-12 of the matrix maximum**, not
  exactly.

**In both runs** all five twins were byte-equal, and the five ROOT digest pairs were learned only on that basis
(`root-twin` in `determinism-amend2.json`).

## 13. Every `run/` path named here is tracked

`python3 -I 2d-unfolding/re2/partc/re2c_tracked.py RE2-PARTC-REPORT.md`, output at commit:

```
docs/orchestration/state/2d-closeout/stageF/methods/re2/RE2-PARTC-REPORT.md: 19 run/ paths
  tracked  run/
  tracked  run/partc_r2/
  tracked  run/partc_r2/determinism_dry_amend2.json
  tracked  run/partc_r2/hpss/re2-2d-rebuild-partc-20261024/logs/
  tracked  run/partc_r2/partc-r2/
  tracked  run/partc_r2/partc-r2/SHA256SUMS
  tracked  run/partc_r2/partc-r2/chain.json
  tracked  run/partc_r2/partc-r2/cmodel/cmodel_R.json
  tracked  run/partc_r2/partc-r2/fig1/RUN-fig1.txt
  tracked  run/partc_r2/partc-r2/logs/steps.tsv
  tracked  run/partc_r2/partc-r2/partc_numbers.json
  tracked  run/partc_r2/partc-r2/values_table.json
  tracked  run/partc_r2/partc-r2/values_table.tsv
  tracked  run/partc_r2/partc-r2_preflight/determinism-amend2.json
  tracked  run/partc_r2/partc-r2_preflight/determinism-amend2.log
  tracked  run/partc_r2/partc-r2_preflight/determinism.json
  tracked  run/partc_r2/partc-r2_preflight/hpss.argv
  tracked  run/partc_r2/partc-r2_preflight/preflight.log
  tracked  run/partc_stopped/
all tracked
```

## Appendix: the values table, every row with its purity control value

The rows come from [`values_table.json`](run/partc_r2/partc-r2/values_table.json). "printed" is the value printed now.
"purity control value" is the unrounded purity source the control reproduced. "changes" says whether the
regenerated value differs at the printed precision.

| id | printed at | printed | purity control value | regenerated | changes |
|---|---|---|---|---|---|
| `m-sigTwoD` | `N/values.tex:\sigTwoD` | 3.073e-38 | 3.07302e-38 | 3.069e-38 | yes |
| `m-ratioTot` | `N/values.tex:\ratioTot` | 1.011 | 1.01119 | 1.010 | yes |
| `lit-ratioTot-pct` | `N/sec_results.tex:57` | 1.1 | 1.01119 | 1.0 | yes |
| `m-medianBinRatio` | `N/values.tex:\medianBinRatio` | 1.008 | 1.0081 | 1.005 | yes |
| `m-binsFive` | `N/values.tex:\binsFive` | 82.9 | 82.9 | 86.8 | yes |
| `m-binsTen` | `N/values.tex:\binsTen` | 95.6 | 95.6 | 95.1 | yes |
| `m-binsTwenty` | `N/values.tex:\binsTwenty` | 99.0 | 99 | 99.0 | no |
| `m-pullMean` | `N/values.tex:\pullMean` | 0.074 | 0.074 | 0.060 | yes |
| `m-pullRMS` | `N/values.tex:\pullRMS` | 0.564 | 0.564 | 0.535 | yes |
| `m-pullRMSr` | `N/values.tex:\pullRMSr` | 0.56 | 0.564 | 0.54 | yes |
| `m-chiPaper` | `N/values.tex:\chiPaper` | 2.65 | 2.654 | 2.27 | yes |
| `m-chiCombined` | `N/values.tex:\chiCombined` | 0.964 | 0.964 | 0.929 | yes |
| `m-chiCombinedLog` | `N/values.tex:\chiCombinedLog` | 0.987 | 0.987 | 0.945 | yes |
| `m-chiCombinedSubStat` | `N/values.tex:\chiCombinedSubStat` | 6.01 | 6.012 | 6.72 | yes |
| `m-uqMedian` | `N/values.tex:\uqMedian` | 6.45 | 6.4479 | 6.41 | yes |
| `m-uqIntegral` | `N/values.tex:\uqIntegral` | 4.75 | 4.75498 | 4.76 | yes |
| `m-uqSFiveMedian` | `N/values.tex:\uqSFiveMedian` | 6.04 | 6.04056 | 5.98 | yes |
| `m-fluxBand` | `N/values.tex:\fluxBand` | 3.75 | 3.74674 | 3.71 | yes |
| `m-fpsAbove` | `N/values.tex:\fpsAbove` | 46 | 3.07302e-38 | not regenerated | — |
| `ro-fps` | `VALIDATION_LEDGER.md:1614` | 3.073e-38 | 3.07302e-38 | 3.069e-38 | yes |
| `new-QR-plus-Cmodel-median` | `(new product)` | — |  | 7.90 | new |
| `new-QR-plus-Cmodel-p84` | `(new product)` | — |  | 12.32 | new |
| `new-QR-plus-Cmodel-integral` | `(new product)` | — |  | 4.76 | new |
| `new-Cmodel-median` | `(new product)` | — |  | 3.71 | new |
| `new-QR-median-check` | `(new product)` | — |  | 6.41 | new |
| `new-ER-minus-EU-in-QR-sigma-median` | `(new product)` | — |  | 0.060 | new |
| `new-ER-minus-EU-in-QR-sigma-max` | `(new product)` | — |  | 0.478 | new |
| `new-ER-integral-change-pct` | `(new product)` | — |  | -0.139 | new |
| `lit-3d-total-change` | `N/sec_3d.tex:152` | 0.001 | 0.00141156 | 0.141 | yes |
| `lit-3d-median-ratio` | `N/sec_3d.tex:153` | 1.0000 | 0.999976 | 1.0010 | yes |
| `lit-3d-scatter` | `N/sec_3d.tex:155` | 3.5 | 0.0351596 | 3.7 | yes |
| `lit-3d-scatter-187` | `N/sec_3d.tex:187` | 3.5 | 0.0351596 | 3.7 | yes |
| `lit-learner-median-180` | `N/sec_systematics.tex:180` | 0.98 | 0.983 | 1.03 | yes |
| `lit-learner-max-181` | `N/sec_systematics.tex:181` | 12.2 | 12.18 | 17.6 | yes |
| `lit-learner-median-377` | `N/sec_systematics.tex:377` | 0.98 | 0.983 | 1.03 | yes |
| `lit-learner-max-377` | `N/sec_systematics.tex:377` | 12.2 | 12.18 | 17.6 | yes |
| `res-univ-cellshare` | `N/sec_results.tex:155` | 0.87 | 0.87081 | 0.87 | no |
| `res-univ-intshare` | `N/sec_results.tex:156` | 0.83 | 0.828472 | 0.83 | no |
| `res-q-vs-ec` | `N/sec_results.tex:181` | 6.410 | 6.41045 | 6.462 | yes |
| `tabuq-c08-trace` | `N/sec_results.tex:195` | 1.99e-41 | 1.98871e-41 | 1.35e-41 | yes |
| `tabuq-c08-median` | `N/sec_results.tex:195` | 0.057 | 0.0571922 | 0.048 | yes |
| `tabuq-stat-trace` | `N/sec_results.tex:196` | 1.98e-40 | 1.98401e-40 | 1.89e-40 | yes |
| `tabuq-stat-median` | `N/sec_results.tex:196` | 0.684 | 0.684334 | 0.676 | yes |
| `tabuq-univ-trace` | `N/sec_results.tex:197` | 2.73e-39 | 2.73486e-39 | 2.69e-39 | yes |
| `tabuq-univ-median` | `N/sec_results.tex:197` | 5.969 | 5.96863 | 5.935 | yes |
| `tabuq-cpl-trace` | `N/sec_results.tex:198` | 8.34e-40 | 8.34373e-40 | 8.31e-40 | yes |
| `tabuq-cpl-median` | `N/sec_results.tex:198` | 2.137 | 2.13685 | 2.087 | yes |
| `tabuq-q-trace` | `N/sec_results.tex:199` | 2.87e-39 | 2.86626e-39 | 2.82e-39 | yes |
| `tabuq-q-median` | `N/sec_results.tex:199` | 6.448 | 6.4479 | 6.414 | yes |
| `tabuq-paper-trace` | `N/sec_results.tex:200` | 2.68e-39 | 2.67609e-39 | 2.68e-39 | no |
| `tabuq-caption-q-median` | `N/sec_results.tex:212` | 6.448 | 6.4479 | 6.414 | yes |
| `tens-diag-only` | `N/sec_results.tex:220` | 0.32 | 0.324 | 0.29 | yes |
| `tens-chi2-norm` | `N/sec_results.tex:223` | 0.06 | 0.06 | 0.04 | yes |
| `tens-chi2-shape` | `N/sec_results.tex:224` | 544 | 544.13 | 465 | yes |
| `tens-ten-smallest` | `N/sec_results.tex:227` | 9.5 | 0.095 | 9.6 | yes |
| `tens-73-modes` | `N/sec_results.tex:228` | 73 | 73 | 73 | no |
| `tens-73-chi2` | `N/sec_results.tex:229` | 0.81 | 0.806 | 0.66 | yes |
| `tens-max-band-share` | `N/sec_results.tex:234` | 15 | 0.147 | 15 | no |
| `model-tune-ratio` | `N/sec_results.tex:275` | 0.91 | 0.9124 | 0.91 | no |
| `model-tune-deficit` | `N/sec_results.tex:275` | 9 | 0.9124 | 9 | no |
| `model-data-vs-tune` | `N/sec_results.tex:279` | 33.0 | 33.039 | 33.0 | no |
| `model-ours-vs-tune` | `N/sec_results.tex:279` | 29.8 | 29.755 | 31.3 | yes |
| `tabvs-c08-median` | `N/app_statmethods.tex:86` | 0.057 | 0.0571922 | 0.048 | yes |
| `tabvs-stat-median` | `N/app_statmethods.tex:90` | 0.684 | 0.684334 | 0.676 | yes |
| `tabvs-univ-median` | `N/app_statmethods.tex:94` | 5.969 | 5.96863 | 5.935 | yes |
| `tabvs-cpl-median` | `N/app_statmethods.tex:98` | 2.137 | 2.13685 | 2.087 | yes |
| `tabvs-mat-check` | `N/app_statmethods.tex:102` | 3.4 | 3.4286e-16 | 1.3 | yes |
| `tabvs-q-median` | `N/app_statmethods.tex:106` | 6.448 | 6.4479 | 6.414 | yes |
| `c08-rank` | `N/app_statmethods.tex:130` | 4 | 4 | 4 | no |
| `c08-integral` | `N/app_statmethods.tex:132` | 0.0025 | 0.00245526 | 0.0010 | yes |
| `c08-median-a` | `N/app_statmethods.tex:132` | 0.057 | 0.0571922 | 0.048 | yes |
| `c08-trace` | `N/app_statmethods.tex:133` | 1.989 | 1.98871e-41 | 1.351 | yes |
| `s1-integral` | `N/app_statmethods.tex:168` | 0.061 | 0.0610174 | 0.061 | no |
| `s1-median-a` | `N/app_statmethods.tex:169` | 0.684 | 0.684334 | 0.676 | yes |
| `s1-p84` | `N/app_statmethods.tex:169` | 1.712 | 1.7118 | 1.602 | yes |
| `s1-relse-a` | `N/app_statmethods.tex:170` | 4.1 | 0.040893 | 4.1 | no |
| `band-minos-e` | `N/app_statmethods.tex:275` | 2.390 | 2.38986 | 2.358 | yes |
| `band-minerva-e` | `N/app_statmethods.tex:276` | 1.376 | 1.37618 | 1.435 | yes |
| `band-minoseff` | `N/app_statmethods.tex:277` | 1.578 | 1.57793 | 1.505 | yes |
| `band-flux` | `N/app_statmethods.tex:278` | 3.747 | 3.74674 | 3.712 | yes |
| `band-mares` | `N/app_statmethods.tex:279` | 0.600 | 0.599751 | 0.627 | yes |
| `band-mvres` | `N/app_statmethods.tex:280` | 0.374 | 0.374077 | 0.362 | yes |
| `band-maccqe` | `N/app_statmethods.tex:281` | 0.368 | 0.368435 | 0.336 | yes |
| `band-univ-median` | `N/app_statmethods.tex:283` | 5.969 | 5.96863 | 5.935 | yes |
| `band-univ-trace` | `N/app_statmethods.tex:283` | 2.735 | 2.73486e-39 | 2.689 | yes |
| `grp-muonreco` | `N/app_statmethods.tex:296` | 3.455 | 3.45481 | 3.437 | yes |
| `grp-models` | `N/app_statmethods.tex:296` | 1.581 | 1.58118 | 1.401 | yes |
| `grp-flux` | `N/app_statmethods.tex:297` | 3.747 | 3.74674 | 3.712 | yes |
| `grp-hadronic` | `N/app_statmethods.tex:297` | 0.799 | 0.799311 | 0.743 | yes |
| `grp-stat` | `N/app_statmethods.tex:297` | 0.684 | 0.684334 | 0.676 | yes |
| `grp-norm` | `N/app_statmethods.tex:298` | 1.400 | 1.4 | 1.400 | no |
| `grp-seed` | `N/app_statmethods.tex:298` | 0.057 | 0.0571922 | 0.048 | yes |
| `grp-runperiod` | `N/app_statmethods.tex:298` | 2.137 | 2.13685 | 2.087 | yes |
| `tabcomb-c08-trace` | `N/app_statmethods.tex:455` | 1.989 | 1.98871e-41 | 1.351 | yes |
| `tabcomb-c08-median` | `N/app_statmethods.tex:455` | 0.057 | 0.0571922 | 0.048 | yes |
| `tabcomb-stat-trace` | `N/app_statmethods.tex:456` | 1.984 | 1.98401e-40 | 1.886 | yes |
| `tabcomb-stat-median` | `N/app_statmethods.tex:456` | 0.684 | 0.684334 | 0.676 | yes |
| `tabcomb-univ-trace` | `N/app_statmethods.tex:457` | 2.735 | 2.73486e-39 | 2.689 | yes |
| `tabcomb-univ-median` | `N/app_statmethods.tex:457` | 5.969 | 5.96863 | 5.935 | yes |
| `tabcomb-cpl-trace` | `N/app_statmethods.tex:458` | 8.344 | 8.34373e-40 | 8.314 | yes |
| `tabcomb-cpl-median` | `N/app_statmethods.tex:458` | 2.137 | 2.13685 | 2.087 | yes |
| `tabcomb-q-trace` | `N/app_statmethods.tex:460` | 2.866 | 2.86626e-39 | 2.821 | yes |
| `tabcomb-q-median` | `N/app_statmethods.tex:460` | 6.448 | 6.4479 | 6.414 | yes |
| `tabcomb-paper-trace` | `N/app_statmethods.tex:463` | 2.676 | 2.67609e-39 | 2.676 | no |
| `comb-q-median-prose` | `N/app_statmethods.tex:472` | 6.448 | 6.4479 | 6.414 | yes |
| `comb-q-vs-ec` | `N/app_statmethods.tex:477` | 6.410 | 6.41045 | 6.462 | yes |
| `comb-univ-plus-stat` | `N/app_statmethods.tex:480` | 6.040 | 6.03978 | 5.982 | yes |
| `ndf-trunc-50` | `N/app_statmethods.tex:548` | 0.41 | 0.41 | 0.39 | yes |
| `ndf-trunc-100` | `N/app_statmethods.tex:548` | 1.29 | 1.294 | 1.04 | yes |
| `ndf-trunc-180` | `N/app_statmethods.tex:548` | 2.07 | 2.073 | 1.76 | yes |
| `ndf-trunc-205` | `N/app_statmethods.tex:548` | 2.65 | 2.654 | 2.27 | yes |
| `worked-q-integral` | `N/app_statmethods.tex:560` | 4.75 | 4.75498 | 4.76 | yes |
| `worked-q-median` | `N/app_statmethods.tex:561` | 6.448 | 6.4479 | 6.414 | yes |
| `pull-comb-mean` | `N/app_statmethods.tex:684` | 0.042 | 0.042 | 0.034 | yes |
| `pull-comb-rms` | `N/app_statmethods.tex:685` | 0.398 | 0.398 | 0.388 | yes |
| `rank-univ-1e12` | `N/app_statmethods.tex:743` | 137 | 137 | 138 | yes |
| `cond-univ-1e12` | `N/app_statmethods.tex:745` | 4.93 | 4.93218e+11 | 9.78 | yes |
| `rank-univ-1e10` | `N/app_statmethods.tex:749` | 123 | 123 | 124 | yes |
| `cond-univ-1e10` | `N/app_statmethods.tex:749` | 9.93 | 9.92638e+09 | 9.45 | yes |
| `rank-univ-1e12-b` | `N/app_statmethods.tex:760` | 137 | 137 | 138 | yes |
| `cond-paperV` | `N/app_statmethods.tex:765` | 1.5 | 1.47e+12 | 1.5 | no |
| `rank-paperV` | `N/app_statmethods.tex:765` | 204 | 204 | 204 | no |
| `rank-univstat-1e12` | `N/app_statmethods.tex:767` | 205 | 205 | 205 | no |
| `cond-univstat-1e12` | `N/app_statmethods.tex:768` | 8.17 | 8.17153e+11 | 7.91 | yes |
| `stat-vs-statonly-a` | `N/app_statmethods.tex:776` | 0.428 | 0.427717 | 0.407 | yes |
| `stat-trace-a` | `N/app_statmethods.tex:777` | 1.984 | 1.98401e-40 | 1.886 | yes |
| `statonly-trace-a` | `N/app_statmethods.tex:778` | 4.639 | 4.6386e-40 | 4.639 | no |
| `oo-univstat` | `N/app_statmethods.tex:781` | 23.57 | 23.566 | 22.29 | yes |
| `oo-q` | `N/app_statmethods.tex:782` | 23.23 | 23.233 | 21.77 | yes |
| `stat-vs-statonly-b` | `N/app_statmethods.tex:805` | 0.428 | 0.427717 | 0.407 | yes |
| `stat-vs-statonly-median` | `N/app_statmethods.tex:806` | 0.435 | 0.434922 | 0.425 | yes |
| `stat-trace-b` | `N/app_statmethods.tex:856` | 1.984 | 1.98401e-40 | 1.886 | yes |
| `stat-vs-statonly-c` | `N/app_statmethods.tex:857` | 0.428 | 0.427717 | 0.407 | yes |
| `statonly-trace-b` | `N/app_statmethods.tex:858` | 4.639 | 4.6386e-40 | 4.639 | no |
| `rank-q-1e10` | `N/app_statmethods.tex:888` | 197 | 197 | 197 | no |
| `tens-app-inflation` | `N/app_statmethods.tex:903` | 8 | 8.2 | 8 | no |
| `tens-app-ten-smallest` | `N/app_statmethods.tex:904` | 9.5 | 0.095 | 9.6 | yes |
| `cfg-lgbm42-chi2` | `N/app_statmethods.tex:1000` | 2.654 | 2.654 | 2.270 | yes |
| `cfg-lgbm42-pullrms` | `N/app_statmethods.tex:1000` | 0.564 | 0.564 | 0.535 | yes |
| `audit-pull-mean` | `N/app_statmethods.tex:1113` | 0.042 | 0.042 | 0.034 | yes |
| `audit-pull-rms` | `N/app_statmethods.tex:1113` | 0.398 | 0.398 | 0.388 | yes |
| `audit-c08-median` | `N/app_statmethods.tex:1116` | 0.057 | 0.0571922 | 0.048 | yes |
| `audit-pull-rms-b` | `N/app_statmethods.tex:1135` | 0.398 | 0.398 | 0.388 | yes |
| `audit-q-median` | `N/app_statmethods.tex:1137` | 6.448 | 6.4479 | 6.414 | yes |
| `sys-band-minos-e` | `N/sec_systematics.tex:42` | 2.39 | 2.38986 | 2.36 | yes |
| `sys-band-minoseff` | `N/sec_systematics.tex:42` | 1.58 | 1.57793 | 1.50 | yes |
| `sys-band-minerva-e` | `N/sec_systematics.tex:43` | 1.38 | 1.37618 | 1.44 | yes |
| `sys-minos-integral` | `N/sec_systematics.tex:74` | 0.31 | 0.306416 | 0.30 | yes |
| `sys-rho-flux-muon` | `N/sec_systematics.tex:84` | 0.90 | 0.900424 | 0.90 | no |
| `s1-relse-b` | `N/sec_systematics.tex:106` | 4.1 | 0.040893 | 4.1 | no |
| `s1-nested` | `N/sec_systematics.tex:107` | 1.001 | 1.0012 | 1.000 | yes |
| `s1-centring-sem` | `N/sec_systematics.tex:109` | 4.43 | 4.42777 | 4.37 | yes |
| `s1-centring-sigma` | `N/sec_systematics.tex:110` | 0.26 | 4.42777 | 0.25 | yes |
| `s1-vs-statonly-sys` | `N/sec_systematics.tex:113` | 0.428 | 0.427717 | 0.407 | yes |
| `c08-rank-sys` | `N/sec_systematics.tex:167` | 4 | 4 | 4 | no |
| `c08-median-sys` | `N/sec_systematics.tex:168` | 0.057 | 0.0571922 | 0.048 | yes |
| `c08-relse` | `N/sec_systematics.tex:171` | 71 | 0.707107 | 71 | no |
| `c08-vs-tenseed` | `N/sec_systematics.tex:172` | 0.30 | 0.30419 | 0.27 | yes |
| `x02-share-of-c08diag` | `N/sec_systematics.tex:175` | 0.685 | 0.685369 | 0.763 | yes |
| `x02-interaction` | `N/sec_systematics.tex:175` | 0.076 | 0.0758177 | 0.072 | yes |
| `pl-step` | `N/sec_systematics.tex:300` | 6.94 | 0.0694268 | 6.89 | yes |
| `pl-step-sigma` | `N/sec_systematics.tex:300` | 0.41 | 0.00413492 | 0.46 | yes |
| `pl-bias-zmax` | `N/sec_systematics.tex:301` | 0.7 | 0.680895 | 0.7 | no |
| `pl-bias-chi2` | `N/sec_systematics.tex:302` | 33.8 | 33.7789 | 34.4 | yes |
| `pl-bias-noise` | `N/sec_systematics.tex:302` | 1.8 | 1.77515 | 2.0 | yes |
| `cpl-median` | `N/sec_systematics.tex:313` | 2.14 | 2.13685 | 2.09 | yes |
| `cpl-p84` | `N/sec_systematics.tex:313` | 3.31 | 3.30791 | 3.34 | yes |
| `cpl-max` | `N/sec_systematics.tex:313` | 5.69 | 5.6943 | 6.48 | yes |
| `cpl-pz-min` | `N/sec_systematics.tex:314` | 1.24 | 1.2416 | 1.17 | yes |
| `cpl-pz-max` | `N/sec_systematics.tex:314` | 3.36 | 3.3644 | 3.36 | no |
| `cpl-integral` | `N/sec_systematics.tex:314` | 1.97 | 1.96837 | 1.97 | no |
| `cpl-effect-median` | `N/sec_systematics.tex:316` | 5.4 | 5.36721 | 5.8 | yes |
| `cpl-effect-max` | `N/sec_systematics.tex:316` | 34.5 | 34.5295 | 39.1 | yes |
| `cpl-effect-integral` | `N/sec_systematics.tex:316` | 9.9 | 9.85447 | 9.9 | no |
| `cpl-effect-functional` | `N/sec_systematics.tex:317` | 21 | 21.1625 | 21 | no |
| `cpl-share-cell` | `N/sec_systematics.tex:318` | 9.9 | 0.0992816 | 10.6 | yes |
| `cpl-share-integral` | `N/sec_systematics.tex:318` | 17.1 | 0.171363 | 17.1 | no |
| `cpl-sref-median` | `N/sec_systematics.tex:319` | 1.45 | 1.45381 | 1.38 | yes |
| `cpl-sref-integral` | `N/sec_systematics.tex:320` | 1.09 | 1.09322 | 1.09 | no |
| `cpl-raw-vs-s5` | `N/sec_systematics.tex:329` | 34.8 | 34.8113 | 34.8 | no |
| `cpl-raw-vs-q` | `N/sec_systematics.tex:329` | 1.97 | 1.96602 | 2.59 | yes |
| `centring-min-rel` | `N/sec_systematics.tex:408` | 0.12 | 0.120727 | 0.10 | yes |
| `centring-max-rel` | `N/sec_systematics.tex:408` | 0.50 | 0.504764 | 0.55 | yes |
| `centring-min-sig` | `N/sec_systematics.tex:409` | 0.08 | 0.0804711 | 0.09 | yes |
| `centring-max-sig` | `N/sec_systematics.tex:409` | 2.26 | 2.2577 | 2.85 | yes |
| `x03-mares-seed` | `N/sec_systematics.tex:428` | 1.28 | 1.27569 | 1.13 | yes |
| `x03-flux23-seed` | `N/sec_systematics.tex:428` | 1.29 | 1.28975 | 1.23 | yes |
| `pool-integral` | `N/sec_systematics.tex:449` | 0.084 | -0.0840712 | 0.076 | yes |
| `pool-pz-max` | `N/sec_systematics.tex:452` | 0.57 | 0.5725 | 0.39 | yes |
| `pool-pt-max` | `N/sec_systematics.tex:453` | 0.17 | 0.1711 | 0.33 | yes |
| `pool-cell-min` | `N/sec_systematics.tex:454` | -1.79 | -1.79317 | -1.83 | yes |
| `pool-cell-max` | `N/sec_systematics.tex:454` | 3.13 | 3.13299 | 3.78 | yes |
| `pool-cell-zmax` | `N/sec_systematics.tex:454` | 0.28 | 0.277963 | 0.31 | yes |
| `x02-interaction-b` | `N/sec_systematics.tex:478` | 0.076 | 0.0758177 | 0.072 | yes |
| `x03-seed-min` | `N/sec_systematics.tex:482` | 1.24 | 1.24333 | 1.08 | yes |
| `x03-seed-max` | `N/sec_systematics.tex:482` | 1.33 | 1.33156 | 1.36 | yes |
| `x03-2p2h-shift` | `N/sec_systematics.tex:487` | 0.114 | 0.113718 | 0.097 | yes |
| `x03-2p2h-sd` | `N/sec_systematics.tex:488` | 0.235 | 0.234577 | 0.192 | yes |
| `x03-maccqe-shift` | `N/sec_systematics.tex:488` | 0.266 | 0.265706 | 0.239 | yes |
| `x03-maccqe-sd` | `N/sec_systematics.tex:489` | 0.220 | 0.21965 | 0.210 | yes |
| `pap-findings-integral` | `N/paper_body.tex:93` | 1 | 1.01119 | 1 | no |
| `pap-findings-3d` | `N/paper_body.tex:95` | 0.001 | 0.00141156 | 0.141 | yes |
| `pap-rank-paperV` | `N/paper_body.tex:364` | 205 | 205 | 205 | no |
| `pap-cond-paperV` | `N/paper_body.tex:364` | 1.5 | 1.47e+12 | 1.5 | no |
| `pap-max-band-share` | `N/paper_body.tex:367` | 15 | 0.147 | 15 | no |
| `pap-pl-step` | `N/paper_body.tex:430` | 7 | 0.0694268 | 7 | no |
| `pap-cpl-integral` | `N/paper_body.tex:435` | 2.0 | 1.96837 | 2.0 | no |
| `pap-s1-median` | `N/paper_body.tex:445` | 0.684 | 0.684334 | 0.676 | yes |
| `pap-closure-3d` | `N/paper_body.tex:475` | 0.001 | 0.00141156 | 0.141 | yes |
| `pri-max-band-share` | `N/primer_body.tex:252` | 15 | 0.147 | 15 | no |
| `exec-3d` | `N/sec_execsummary.tex:44` | 0.001 | 0.00141156 | 0.141 | yes |
| `hist-q-median` | `N/app_history.tex:68` | 6.448 | 6.4479 | 6.414 | yes |
| `hist-q-median-2` | `N/app_history.tex:68` | 6.45 | 6.4479 | 6.41 | yes |
| `hist-flux` | `N/app_history.tex:69` | 3.747 | 3.74674 | 3.712 | yes |
| `hist-flux-2` | `N/app_history.tex:69` | 3.75 | 3.74674 | 3.71 | yes |
| `hist-chicomb` | `N/app_history.tex:70` | 0.964 | 0.964 | 0.929 | yes |
| `hist-chicomblog` | `N/app_history.tex:70` | 0.987 | 0.987 | 0.945 | yes |
| `hist-chisubstat` | `N/app_history.tex:70` | 6.01 | 6.012 | 6.72 | yes |
| `hist-q-integral` | `N/app_history.tex:71` | 4.75 | 4.75498 | 4.76 | yes |
| `hist-pull-mean` | `N/app_history.tex:72` | 0.042 | 0.042 | 0.034 | yes |
| `hist-pull-rms` | `N/app_history.tex:72` | 0.398 | 0.398 | 0.388 | yes |
| `hist-univ-median` | `N/app_history.tex:73` | 5.969 | 5.96863 | 5.935 | yes |
| `hist-univ-trace` | `N/app_history.tex:73` | 2.735 | 2.73486e-39 | 2.689 | yes |
| `hist-q-trace` | `N/app_history.tex:73` | 2.866 | 2.86626e-39 | 2.821 | yes |
| `hist-univstat` | `N/app_history.tex:73` | 6.040 | 6.03978 | 5.982 | yes |
| `hist-q-vs-ec` | `N/app_history.tex:73` | 6.410 | 6.41045 | 6.462 | yes |
| `hist-band-minos-e` | `N/app_history.tex:74` | 2.390 | 2.38986 | 2.358 | yes |
| `hist-band-minerva-e` | `N/app_history.tex:74` | 1.376 | 1.37618 | 1.435 | yes |
| `hist-band-minoseff` | `N/app_history.tex:74` | 1.578 | 1.57793 | 1.505 | yes |
| `hist-band-mares` | `N/app_history.tex:74` | 0.600 | 0.599751 | 0.627 | yes |
| `hist-band-mvres` | `N/app_history.tex:74` | 0.374 | 0.374077 | 0.362 | yes |
| `hist-band-maccqe` | `N/app_history.tex:74` | 0.368 | 0.368435 | 0.336 | yes |
| `hist-grp-muonreco` | `N/app_history.tex:75` | 3.455 | 3.45481 | 3.437 | yes |
| `hist-grp-models` | `N/app_history.tex:75` | 1.581 | 1.58118 | 1.401 | yes |
| `hist-grp-hadronic` | `N/app_history.tex:75` | 0.799 | 0.799311 | 0.743 | yes |
| `hist-stat-median` | `N/app_history.tex:76` | 0.684 | 0.684334 | 0.676 | yes |
| `hist-stat-trace` | `N/app_history.tex:76` | 1.984 | 1.98401e-40 | 1.886 | yes |
| `hist-q-median-b` | `N/app_history.tex:202` | 6.448 | 6.4479 | 6.414 | yes |
| `meth-s1-centring` | `N/sec_method.tex:112` | 4.43 | 4.42777 | 4.37 | yes |
| `mat-check-b` | `N/app_statmethods.tex:389` | 3.4 | 3.4286e-16 | 1.3 | yes |
| `floor-stat-vs-statonly` | `N/app_statmethods.tex:625` | 0.428 | 0.427717 | 0.407 | yes |
| `floor-rank-univ` | `N/app_statmethods.tex:637` | 137 | 137 | 138 | yes |
| `floor-rank-filled` | `N/app_statmethods.tex:637` | 205 | 205 | 205 | no |
| `floor-oo-univstat` | `N/app_statmethods.tex:638` | 23.57 | 23.566 | 22.29 | yes |
| `hist-pull-mean-b` | `N/app_history.tex:171` | 0.042 | 0.042 | 0.034 | yes |
| `hist-pull-rms-b` | `N/app_history.tex:171` | 0.398 | 0.398 | 0.388 | yes |
| `mainpap-integral` | `N/main_paper.tex:76` | 1 | 1.01119 | 1 | no |
| `summ-3d` | `N/sec_summary.tex:34` | 0.001 | 0.00141156 | 0.141 | yes |
| `lit-learner-median-pb373` | `N/paper_body.tex:373` | 0.98 | 0.983 | 1.03 | yes |
| `lit-learner-max-pb374` | `N/paper_body.tex:374` | 12.2 | 12.18 | 17.6 | yes |
