# Stage F rebuilds R1–R4 from the adopted Q: frozen specification (phase 1, products and computations)

**Owner:** the paper-tighten lane, as director (Stage F). Written 2026-10-18, after Joseph adopted
Q = S5 total + C_PL ([`DECISION-20261017-joseph-2d-adopt-s5-plus-playlist.md`](../../../../DECISION-20261017-joseph-2d-adopt-s5-plus-playlist.md)).
**Revision 1** (before freeze) applies a fresh read-only review: APPROVE WITH CHANGES, 7 MATERIAL and 8 MINOR, all
applied (§9).

**CITABLE FOR:** how every deliverable quantity that depends on the 2D covariance is recomputed from Q or declared
not recomputed, and the checks each computation must pass.
**NOT CITABLE FOR:** any number (none is computed when this is written), any text change in a deliverable, a claim,
or an outward act. The deliverable text is phase 2, a separate record, which takes its numbers only from this
phase's committed receipts. R5 (the claims map) waits on J3.

The consumer inventory (read-only, `main` `669d9694`) is mapped site by site in §3a. Phase 1 produces a receipt
field for every site, or the site is listed as not recomputed with its reason.

## 1. Inputs (full digests are constants in the scripts)

| input | sha256 | path (cluster unless noted) |
|---|---|---|
| S5 `production_cov.npz` | `6689d2fc2a795a72e66ee953a32d94c7906dd81a866771979f379c5f163a9ddc` | CFS `m3246/josephrb/2d-closeout-stageC-production-20261015/results/s5/` |
| S5 `uq_production_covariance.root` | `34cf33f96cd688e2c00064f314ff76d294b0d012b0bed5a4560cb1c2e3fc0df8` | same; equals `/pscratch/sd/j/josephrb/2d-closeout-stageC-production-20261015/tmp/SHA256SUMS.pscratch` |
| S5 `s5.json` | `8c815149517857302af4b3a64b0db4148a13515b8182bd6eebb2f89c57d92510` | committed `stageC/production/evidence/production/results/s5.json` |
| `playlist_term.npz` | `c1723cb5e185ae7a6176fbbe523432ab87877c8cddcfe721eaed71f0a43b9476` | CFS `m3246/josephrb/2d-closeout-playlist-term-20261016/` |
| `s5_plus_playlist.npz` (Q) | `8ccb4d723c3dbf737a7fb1d5236e5e25409c41b42b64ac55dccbbc12f595600e` | CFS `m3246/josephrb/2d-closeout-playlist-combination-20261017/` |
| `combination.json` | `050e256023277ec9da492ffa7b9d129275c3afa2bfc6c47091999d88de5bf18d` | committed `playlist-term/outputs/combination/` |
| `E_U` | `4f5a1b6d44b9e7212b233650bb00bfb626ae65461e3bf8033cd67866dbd7eb2c` | `/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root` |
| `E_C` (exact-split, for the 6.058%-type denominator only) | `142a45b0efc753d91e95376c28ac3f6a477d582014a919e49d6d71079a127fd5` | `/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/2d_crossSection_omnifold_MEFHC_5iter.root` |
| paper ancillary | `6c6dce72050bb8f128fab8e286349b250bc60d1c767e162bf15a0f009f3573e3` | `/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/minerva_paper_anc/cov_ptpl_minerva_inclusive_6GeV.root` (the scripts' `ANC_DIR`; `$HOME/MINERvA-OmniFold` is a symlink to it) |
| `fig_arrays.npz` | `72394a2b4eff9f14b01903ff97525bcb690c2adee58ccaf573a8d95139b415b8` | `/pscratch/sd/j/josephrb/pub-release-20261006/figs/fig_arrays.npz` (only copy found) |
| `remote_reduce.json` | `2ecfc243ab4a6c508a69df0e231676019106f3ad86f34e3ac3423f7bd2bca9ce` | committed `state/next-preparation-20261009/two-d-path/operands/` |
| `make_figs.py` | `9c4dbf24d5e19161034fbdf6f84834f578fbde3a1b879961ef7c25a739301c7c` | committed `publication/release/figs/` |
| VL175 controls | universe+boot `c04x01.root` `da92c5d2567647e8613bb3a6522176dbd9a287970082b45ac9e83e24684b1948`; `boot300.root` `71a75821ceeb658710adca30243e39e7184e33f868f58ea56cffe63ba8db0115`; `ml.root` `3b6b48ec89207ae29dc7bb0ddc5a41836c359c4805877d663731694b828d5db9`; `cov2d_blocks_205.npz` `c2606f9095c61e3b0d56bbb72d4c6948b5662461da51563858ce3c8ae18824f8`; `budget.json` `aab8a24ebd61df54e7277999d49300c3bdaa045710835bfa05adf3bfc71dd8fa`; `group_medians.json` `7927c51ef7549601020517aee397748e10fc7603da7a847f9f833f789200900f` | `/pscratch/sd/j/josephrb/2d-closeout-c04repair-20261012/build/`; `2d-unfolding/uq/…`; committed c04-repair and `stageB/diagnostics/c04-grouped/` |

**Environment and invocation.** Login node, root_6_28, 0 node-h. Each script runs as
`python3 -I -c "import sys, runpy; sys.path[:0] = [<A>/2d-unfolding/uq, <A>/2d-unfolding, <A>]; sys.argv = [...]; runpy.run_path(<script>, run_name='__main__')"`,
where `<A>` is the deployed archive, because `-I` drops the script's own directory from `sys.path` and two named
scripts import siblings. RUN.txt records `sys.path`, every argv, every exit code and every input and output digest. The runner adds `-B`
and exports `TMPDIR`, `MPLCONFIGDIR` and `XDG_CACHE_HOME` inside the run directory, so nothing (matplotlib caches,
`/tmp/mplconfig`, `__pycache__`) is written outside it.

**Archives (two).** Archive 1 is a `git archive` of the commit that freezes this spec and the step-A/§3 scripts
(steps A, §3, B-before). Archive 2 is the step-B commit (B-after, C, D). Both go to new directories under
`/pscratch/sd/j/josephrb/tmp-2d-rebuild-20261018/`; RUN.txt records both shas. No output is written outside that
directory: every producer is given an explicit output flag (§5, §6).

## 2. Step A: the Q products (`scripts/build_q_products.py`)

**Writes:**
1. `uq_adopted_covariance.root`: `hCov_Q`, `hCov_S5total`, `hCov_universe_total`, the 44 `hCov_universe_<band>`
   (43 bands + `__Normalization_flat`), `hCov_stat`, `hCov_c08`, `hCov_playlist`, `hCov_sum_universe_stat` (not prefixed `hCov_universe_`, which the
   fig. 6/7 script reads as a band), and
   `hReportedCells`, all in the S5 ROOT's `hCov_combined` bin layout.
2. `block_stat.root`, `block_c08.root`, `block_playlist.root`: each one block as `hCov2D_reported`, plus
   `hReportedCells`. `block_stat.root` also holds `hRel2D` = √diag(stat)/`E_U` on the 14 × 16 grid, which
   `plot_bootstrap_figs.py` reads (so its colorbar "std/mean" means σ/`E_U`: a phase-2 caption item).
3. `cov2d_Q_205.npz` (+ `.json`): `Q`, `s5_total`, `universe`, `stat`, `c08`, `C_PL`, `cells` =
   `flatnonzero(E_U > 0)` as global ids `pt*16 + pz`, and `x` = `E_U` on them.
4. `budget_Q.json`: §3.

**STOP checks:**
- A0 every input digest equals its pin.
- A1 cell sets: S5 ROOT `hReportedCells` = nonzero `E_U` = playlist `cells` = the paper `StatOnly` positive diagonal.
- A1′ value-anchored cell order (KI-90's hazard): `cells` strictly ascending; npz `cells_x_EU` = `E_U[cells]`
  exactly; playlist `x` = `E_U[playlist cells]` exactly.
- A2 storage: S5 ROOT `hCov_combined` = npz `total`; each `hCov_universe_<band>` = npz `band_<band>`; their sum =
  `universe`, to 1e-12 of the matrix max. (`s5_rollup.py` writes both files from the same arrays, so A2 checks
  storage, not order; order rests on A1′ and step B.)
- A3 `s5_total + C_PL` = Q `total_plus_C_PL` to 1e-12; Q `C_PL` = playlist `C_PL` exactly.
- A4 every written histogram re-read equals its source exactly.
- A5 symmetry 1e-12; PSD at `PSD_TOL` 1e-10 for Q and each block.

## 3. The numbers (`budget_Q.json`)

Relative σ is σ/`E_U` in percent. The integral and the 30 projections use S5's F and `area`, as COMBINATION-REPORT
§2; **the integral σ is also the "width-weighted total σ"** of the note.

For each of Q, S5 total, universe, stat, c08, C_PL, universe + stat, and each of the 44 bands: per-cell median, p84,
min, max; integral σ; 14 p_T and 16 p_∥ projection σ; √Tr. Also:
- the same medians against `E_C` for Q, S5 total and universe + stat (the exact-split-denominator figures);
- grouped medians: `plot_uncertainty_fig6_7_style.py`'s band-to-category map, plus statistical, training-seed (c08)
  and run-period (C_PL) groups;
- each block's per-cell variance share (median) and integral variance share;
- **ranks and condition numbers** for universe, universe + stat, S5 total and Q, at both eigenvalue thresholds 1e-10
  and 1e-12 of λmax of (C+Cᵀ)/2 (`s5_rollup.py:478` and the note's convention);
- the paper's √Tr(TotalCovariance) and √Tr(StatOnly) on the 205 cells, and the ratios √Tr(stat)/√Tr(StatOnly),
  √Tr(Q)/√Tr(TotalCovariance), and the per-cell median of σ_stat/σ_StatOnly;
- the flux-block numbers: `band_Flux` median and integral. (Amended after implementation: the leading-mode share
  "99.6%" has no committed producer and is **not computed**; `\rhoFluxMuon` comes from
  `uq/rederive_flux_muonE_cross.py`, which reads only the paper ancillary file, so it does **not depend on Q**; the
  script reproduces 0.900 as a control only.)
- copied verbatim, with the field path, from `s5.json`: the stat-block centring offset, the MAT agreement check, the
  ensemble counts (bands, universes; the replica and seed-triplet counts are not `s5.json` fields and are
  counted from its `inputs.production_outputs` keys, labelled as derived).

**Controls (STOP):**
- the metric functions on VL175's inputs reproduce `budget.json`'s summary fields (median, p84, min, max, integral,
  √Tr) to 1e-12 relative;
- the grouped medians on VL175's inputs reproduce `group_medians.json`;
- the Q, S5 and C_PL rows reproduce `combination.json`'s cell median, p84, max and integral to 1e-12, and its
  projections (stored rounded to 4 decimals) exactly after rounding to 4 decimals.
These show the code reproduces the values it replaces; they do not prove it is the same code.

## 3a. Consumer → receipt map

| consumer site (inventory) | receipt field, or status |
|---|---|
| `\uqMedian`; Fig. 1 inset | `budget_Q.Q.median` |
| `\fluxBand`; flux prose (sec_systematics, sec_results, paper_body) | `budget_Q.bands.Flux.*` |
| flux leading-mode share "99.6%" (sec_systematics) | **not recomputed**: no committed producer; phase 2 removes it or labels it historical |
| `\rhoFluxMuon` | **not affected** by Q (paper ancillary only); reproduced as a control |
| `\chiCombined`, `\chiCombinedLog`, `\chiCombinedSubStat` | §5 logs (standard, log-normal, subtract-stat) |
| combined pull mean/RMS (app_statmethods 624–627, 1060–1063) | §5 **standard-form** log |
| tab:uq, tab:combine, tab:variance-sources, tab:band-medians, group medians | `budget_Q` per-block, per-band and grouped rows (block list changes: universe, stat, c08, C_PL) |
| "before ML" / universe + stat median; `E_C`-denominator medians | `budget_Q.universe_plus_stat`, `budget_Q.*_vs_EC` |
| ranks, conditions, direct-inverse χ² (app_statmethods 681–713, 808–837) | `budget_Q.ranks`; `_ours_only_chi2.py` logs (§5) |
| ratios to the paper's √Tr and StatOnly (sec_systematics 77–83, app_statmethods 574, 715, 739) | `budget_Q.paper_ratios` |
| stat centring (paper_body 264–270), MAT agreement, ensemble counts | `budget_Q.s5_copied` |
| width-weighted total σ (app_statmethods 532) | `budget_Q.Q.integral` |
| Fig. 1; Figs. 6/7; `uq_spread_2d`, `uq_corr_2d` | §6 |
| **regularization scan** (app_statmethods 784–788) | **not recomputed**: no committed producer found; the text labels it exact-split. Phase 2 keeps it labelled as a historical diagnostic or removes it |
| **VL169 coverage macros** (values 97–119), the post-hoc rescoring (97.7/78.1), `\pullFrac` family, the audit-table C2 row | **not recomputed; not a property of Q**: they describe the superseded VL170 statistical band. S5's stat block is a different ensemble and is untested (KI-85). Treatment is phase 2 under J3/J4 |
| seed-scan figures and ML-block prose | **not recomputed**: C08 replaces the seed scan; phase 2 decides history or removal |
| paper-σ-only quantities (`\chiPaper`, `\chiPaperExact*`, paper pulls, tension, model χ²) | **not affected** by Q |
| app_history errata rows | phase 2 adds a VL175 → Q row from `budget_Q` |
| `fig_arrays.npz.manifest.json` producer digest (KI-90) | §4 |

## 4. Step B: KI-90's two consumers (archive 2; own commit, reviewed)

Apply structure REPORT §5's patch (`state/next-preparation-20261009/structure/REPORT.md`):
- `compare_to_paper_fullcov.py:load_omnifold_cov`: after opening, `reported_cells.read_cells(f, mean_fallback="hMean2D")`;
  if a set is returned, `require_same_cells` against the paper `StatOnly` set and print one pass line naming the
  source; on mismatch `SystemExit`; with no set, keep the count check and print one `[WARN] … count only` line.
- `uq/plot_uncertainty_fig6_7_style.py`: replace the `WARN` at `:106-108` with the same comparison of `xsec > 0`
  against each loaded covariance file's set; refuse on mismatch.

Also, in `plot_uncertainty_fig6_7_style.py` only:
- an optional repeatable `--extra-block ROOT:HIST:LABEL`, added to the total and drawn as its own group (its label is
  added to `draw_one`'s `order` and `STYLE`);
- an optional `--ml-label` (default `ML`, so unchanged without it).
Labels used in phase 1 ("Training seed", "Run period") are provisional; legend wording is phase 2/J4.

`fig_arrays.npz.manifest.json`: `export_fig_arrays.py` uses only `flatten_th2d`, `tmatrix_to_numpy` and
`flatten_ours` from `compare_to_paper_fullcov.py`. Step B records that those three functions are byte-identical
before and after, and updates the manifest's producer digest with that note; the arrays are not re-exported.

**Equivalence (STOP)**, archive 1 vs archive 2, on VL175's `run_repair.sh` χ² invocations (adopted, control,
repaired × three forms), replacing REPORT §5's "rollup steps (3) and (5)":
- after normalizing absolute paths, the logs are identical except for the expected added lines (amended from the
  code review's measurement): every run gains an ml pass line (`ml.root` passes via `hMean2D`); the adopted runs
  also gain one warning (the VL172 universe file has no stored set); the control runs (`…_control.root`) and the
  repaired runs (`c04x01`) also gain a universe pass line (`hReportedCells`). The χ² and Summary lines are
  identical;
- fig. 6/7: `summary.txt` identical with and without the patch, on the VL175 inputs without `--extra-block`.

## 5. Step C: χ² and pulls (archive 2)

- `compare_to_paper_fullcov.py --ours <E_U> --omnifold-cov uq_adopted_covariance.root:hCov_Q --out-prefix <run>/chi2_Q_<form>`
  in the three forms. Each log must show the cell-identity pass line on `hReportedCells`. That is KI-90's "verify
  they ran" (CHECKLIST K3).
- `_ours_only_chi2.py --ours <E_U>`, three runs: `--universe-cov uq_adopted_covariance.root --universe-hist hCov_universe_total`;
  the same plus `--bootstrap-cov block_stat.root`; and `--universe-hist hCov_Q` alone. (Its algebra takes a single
  matrix; the review confirmed no hidden bootstrap assumption.)

## 6. Step D: figures (archive 2)

- **Fig. 1:** `make_fig1_q.py`, from `make_fig1_vl175.py`, with `cov_ours` = `Q` from `cov2d_Q_205.npz`, and with
  `--sigma` and the `universe_plus_boot`/`ml`/`boot_vl170` checks replaced by:
  - npz `cells` = `remote_reduce` `cells` gids;
  - diag(Q) = diag(s5_total) + diag(C_PL), read from the two CFS npz files (not from step A's outputs);
  - √diag(Q)/`ours_v` on the 205 cells reproduces `combination.json`'s S5 + C_PL median, p84 and max to 1e-12.
  The inset value comes through `--values` pointing at a temporary file containing only `\uqMedian` =
  `budget_Q.Q.median` at the printed precision (2 decimals); its digest goes in RUN.txt. The script refuses unless
  `make_figs.py`'s regex finds exactly one `\uqMedian` and it equals the pinned `budget_Q.json` value to 2 decimals,
  and unless `--cov` and `--budget` are listed in step A's `SHA256SUMS` with their measured digests.
  **Environment control (STOP):** before drawing Q, `make_fig1_vl175.py` in the chosen environment must reproduce
  `docs/analysis-note/figures/paper_fig1_validation.pdf` (`49766e26…`) byte for byte. VL175 used matplotlib 3.11.2 and
  numpy 2.5.4; the local default is 3.10.1/1.26.4, so a pinned venv may be needed. If no environment reproduces it,
  stop and record.
- **Figs. 6/7:** `--xsec-root <E_U> --universe-root uq_adopted_covariance.root --bootstrap-root block_stat.root
  --ml-root block_c08.root --include-ml always --ml-label "Training seed" --extra-block block_playlist.root:hCov2D_reported:"Run period"
  --paper-root <anc> --out-prefix <run>/MEFHC_fig6_7_uncertainty --projections-json <run>/fig67_projections.json`.
  STOP: in `fig67_projections.json` the Total equals `budget_Q.Q`'s projections, Training seed equals c08's and Run
  period equals C_PL's, to 1e-12 (`summary.txt` stays at its 3-decimal format, which §4 needs unchanged).
- **Statistical-block figures:** `plot_bootstrap_figs.py --cov block_stat.root --outdir <run>/stat`.
- `make_figures.sh` lines 54 and 57 still regenerate fig. 6/7 and `uq_spread`/`uq_corr` from VL170 inputs; phase 2
  must update them, or a note rebuild reverts these figures.

## 7. Step E: functionals (R4, control only)

`F · E_U` and `area · E_U` reproduce the central-value macros (`\sigTwoD` etc.) at their printed precision. A
mismatch is reported, not fixed here.

## 8. Order and review

1. Freeze: this spec, `build_q_products.py` and the §3 metric code are committed, after a fresh read-only review of
   the scripts.
2. Run A, §3, B-before (archive 1). Commit the step-B patch and `make_fig1_q.py` after their review; run B-after, C,
   D, E (archive 2). Commit the receipts (json, logs, `summary.txt`, `RUN.txt`, figures); ROOT and npz products go to
   CFS with `SHA256SUMS`.
3. A fresh verifier recomputes `budget_Q.json` and the three χ² with its own code from the pinned npz files and the
   paper ancillary file.
4. Phase 2 record: the text changes, from these receipts only.

## 9. Review record

Pre-freeze review 2026-10-18: APPROVE WITH CHANGES. MATERIAL: M1 `-I` sys.path; M2 missing output/denominator flags
that would have written into the shared checkout or used `E_C`; M3 `hRel2D`; M4 circular Fig. 1 check and unpinned
inputs; M5 completeness (§3a); M6 two archives; M7 an equivalence that could not pass as written. MINOR: A2's scope,
control pins, rank definition, the manifest digest, fig. 6/7 labels and STOP, paths, `make_figures.sh`, exit codes.
All applied above. The reviewer measured that every A1–A5 condition holds on today's inputs.

Pre-freeze code review 2026-10-18 (`build_q_products.py`, the step-B patch, `make_fig1_q.py`): APPROVE WITH CHANGES,
2 MATERIAL (Fig. 1's inset value was unchecked; §4's expected log lines were wrong) and 9 MINOR, all applied. The
reviewer measured: step A passes all 76 STOPs and controls; A1′ refuses four reorderings; both KI-90 guards refuse a
moved cell and pass the good inputs; the fig. 6/7 default output is byte-identical without the new options; the nine
VL175 χ² runs keep every χ² and Summary line; step D's Total equals Q to 4e-16.

**Same-model caveat:** the director and the verifiers are Claude Opus 5.5 on the claude-school account.
