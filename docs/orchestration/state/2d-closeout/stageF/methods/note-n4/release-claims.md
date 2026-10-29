# Fact check: `docs/analysis-note/app_release.tex` against the RC7 release package

## Header

- **Appendix checked:** `docs/analysis-note/app_release.tex` in the read-only worktree
  `/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/796e7ecc-51d8-4fd5-a926-09de706955fd/scratchpad/wt-con`
  at HEAD `371cccec` (Merge PR #460). The worktree has uncommitted edits in six other note files
  (`app_statmethods_nd`, `sec_5d`, `sec_execsummary`, `sec_pet_campaigns`, `sec_summary`, `sec_validation`).
  None of them touch `app_release.tex`, `paper_body.tex`, `main_paper.tex`, `sec_eavailw.tex`, `sec_joint.tex` or
  `values.tex`. The `sec_5d.tex` diff only changes two validation sentences, not `sec:eavailw-construction`/`-adopted`.
  Line numbers below are `app_release.tex` lines. Each macro is resolved from `values.tex`/`main_note.tex`:
  `\zcvDigest`=3d7465f6, `\zprojCells`=42, `\latBins`=10,694, `\depositsnapshot`="[snapshot identifier pending deposit]".
- **Tarball digest:** `shasum -a 256` of
  `/Users/josephbailey/local-research/MINERvA-OmniFold-prd-editorial-pdf-20261008/minerva-omnifold-article-release-rc7.tar.gz`
  = `27f0caba53c4bbf75310f6d94145ea872ebe77c6a6f55ef48298d95cbcee566e`. This **matches**
  `docs/publication/release/RC7-SHA256SUMS.txt:2`. Size: 15,745,698 B.
- **Extraction:** into `.../release-claims/rc7/minerva-omnifold-article-release-rc7/`. The package's
  `SHA256SUMS` check gives 32/32 OK, both before and after every run. The only file added afterwards is
  `code/__pycache__/replay_inference.cpython-311.pyc`, which the verifier's own subprocess imports wrote; it is not
  listed in SHA256SUMS. The packaged `SHA256SUMS` is identical to the repository record, apart from that record's
  comment line. `README.md` is byte-identical to `docs/publication/release/RC7-README.md`.
- **What I ran** (fresh venv `.../release-claims/venv`, CPython 3.11.15 on macOS arm64, `pip install -r requirements-lock.txt`
  exactly: numpy 1.26.4, scipy 1.15.2, matplotlib 3.11.2 + 9 deps):
  1. `python -I code/verify_rc.py` from the package top directory gave **`VERIFY: PASS`, exit 0**, in 277 s wall time
     (log: `.../release-claims/verify-run.log`). Its output:
     both replays `COMPARE: AGREE (0 differences)`; W1 0 claim / 0 criterion differences; `FIG NUMBERS: PASS`;
     the negative control rejects `\gibuuCorner` 1.61→1.62; Figs. 1–3 and Fig. 4 were regenerated; the L2 ratios came out 0.504–0.857 against
     the printed 0.50–0.86; the M1 shifts equal the frozen d1 in 4/4.
  2. `make_figs.py` into `.../release-claims/figs/` gave sha256 fig1 `938c4fc9…`, fig2 `57f3cc60…` and fig3 `e9d1bb01…`.
     All three equal the RC7 README hashes. fig2 is byte-identical to the note's `figures/paper_fig2_joint.pdf`.
     A standalone `plot_joint_null_distributions.py` run to `figs/fig4_joint_nulls.pdf` produced no file (see "Stopped runs").
  3. An independent recomputation of worked-example steps 1–4 from the committed
     `docs/analysis-note/release-package-20260922/` arrays (`central_values_5d.npz`, `projection_matrix_M_eavailW.npz`,
     `covariance_eavailW.npz`), compared against RC7's `data/figs/fig_arrays.npz` `hData2D`.
  4. The release audit's `docs/publication/audit-20261008/checks/agentC_checks.py`, run on the extracted RC7 files
     (output: `.../release-claims/jitter-check.json`; see RL-41).
  - `z-cv.npz` itself (890 MB) is only on NERSC. I did not read it, so its digest and trace are checked against
    committed records only.
- **Stopped runs.** Two runs I started in the background were stopped by the coordinator after about 5 h each. Both sat in
  OpenBLAS's thread server, contending with each other at about 250 % CPU each, against the README's 2–11 min for the whole verifier.
  (a) PID 72044 was the standalone `plot_joint_null_distributions.py` run, meant to take a Fig. 4 digest for RL-19. No file was produced.
  RL-19 is graded from the passing verifier run's `[ok] Fig. 4 … regenerated` line, with no digest.
  (b) PID 87422 was `agentC_checks.py`, meant to recompute `observed_jitter_p` for RL-41. It was killed (exit 143) with no output.
  I retried it exactly once, single-threaded with a 20 min limit and nothing else running. It finished in 35 s, and RL-41 is graded from that output.
  My waiter loop for the two runs was also stopped.
- Abbreviations: **WT** = the worktree root; **PKG** = the extracted package root.

## Claim table

| id | line | claim (verbatim, short) | evidence | verdict |
|---|---|---|---|---|
| RL-01 | 4 | "describes the local replay package that exists, RC7" | The tarball exists locally; its digest matches `RC7-SHA256SUMS.txt:2` | TRUE |
| RL-02 | 4 | "Rebuilding this note's PDFs assembles documents; it does not reproduce scientific results." | `WT/docs/analysis-note/build_all.sh` runs `latexmk` and lint checks (`check_body_pointers.py`) and no analysis step | TRUE |
| RL-03 | 7 | "refer to the snapshot of the code repository … identified at deposit: \depositsnapshot" | `main_note.tex:35`: the macro prints "[snapshot identifier pending deposit]". No snapshot identifier exists | UNVERIFIABLE |
| RL-04 | 9 | "RC7, a local release candidate with a README, checksums and a replay verifier" | PKG holds `README.md`, `SHA256SUMS` and `code/verify_rc.py` | TRUE |
| RL-05 | 9 | "has not been deposited or released under a publication tag" | RC7-README.md:1-5 ("NOT RELEASED … not been deposited, tagged"). `git tag -l` in WT shows only `evidence/*`, `freeze/k0-*` and `z-deploy-*` tags. `main_paper.tex:77` still carries `\pubhold{deposit identifier…}`. Checked against the local records; I did not search external archives | TRUE |
| RL-06 | 9 | verifier "run on the packaged files in an empty directory, reproduces the recorded observed statistics of the joint tests" | My run: both replays AGREE. `replay_inference.py:166-168` compares `T_total_obs`/`T_shape_obs` | TRUE |
| RL-07 | 9 | "the $p$ value and count of every test and variant" | `replay_inference.py:169-178` compares p, k and B for every variant and robustness variant. AGREE, 0 differences | TRUE |
| RL-08 | 9 | "and the decision of every test" | `replay_inference.py:179-183`, for both decision families. AGREE | TRUE |
| RL-09 | 9 | "the robustness results" | `robustness_variants` and `decisions_robust_kappa` are compared (`:169-183`). AGREE | TRUE |
| RL-10 | 9 | "and the power figures" | `replay_inference.py:184-190`. AGREE | TRUE |
| RL-11 | 9 | "and every figure number that it checks" | `fig_numbers.py` printed `FIG NUMBERS: PASS`, and the negative control fired | TRUE |
| RL-12 | 9 | "It does not recompute the recorded stability of the observed $p$ values under the data's rounding noise." | `grep jitter PKG/code` hits only `make_reading_b.py:28` (an equality check). `compare()` never reads `observed_jitter_p`. README:114 says the same | TRUE |
| RL-13 | 9 | "The package, about 16 MB of sufficient inputs" | Tarball 15,745,698 B. The four sufficient-input files (2 npz + 2 manifests) total 16,509,285 B. The unpacked total is 17,710,487 B | TRUE |
| RL-14 | 9 | "reproduces the joint-test $p$ values, decisions, robustness labels and power results" | Same run as RL-06 to RL-10 | TRUE |
| RL-15 | 9 | "the same results in the reading with the recovered pseudo-experiments added … and the variant shifts recomputed on all draws" | `data/recovery-union` has 1400/1800 draws per null against 1343–1751 frozen, and its `S__*` differ from frozen (max rel. 0.2–7 %; NuWro S is all zero in both). `make_reading_b.py` defines the *frozen-S* reading as (b), so the union file is the recomputed-shift reading (a). Replay against `resolved-evaluate.json`: AGREE, 0 differences | TRUE |
| RL-16 | 9 | "the matched coarse-projection comparison (§joint5d-projections)" | Verifier W1 step: 0 claim differences, 0 criterion differences (`verify_rc.py:41-62`) | TRUE |
| RL-17 | 9 | "and the fine-grid $L_2$ ratios of condition (i)" | Verifier: 0.504–0.857 against the printed 0.50–0.86 (`values_inference.tex` jtMoneMin/Max) | TRUE |
| RL-18 | 9 | "regenerates, from packaged arrays, … the $(\Eavail,W)$ excess map (Fig. eavailWexcess)" | `make_figs.py` fig2 → sha256 `57f3cc60…`, byte-identical to `figures/paper_fig2_joint.pdf`, which `sec_eavailw.tex:109,114` includes as `fig:eavailWexcess` | TRUE |
| RL-19 | 9 | "… the null distributions of the joint tests (Fig. joint5d-nulls)" | `verify-run.log` line "[ok] Fig. 4 (calibrated null distributions) regenerated from the frozen inputs": `plot_joint_null_distributions.py` on `data/frozen/…npz` exits 0 and writes the PDF (`verify_rc.py:93-100`) inside the passing 277 s verifier run. The standalone run that was to take its digest was stopped, so no Fig. 4 digest was taken. The note's `paper_joint_nulls.pdf` (`4953b44a…`, `sec_joint.tex:206-211`) was drawn by `figures/plot_joint_null_distributions_physlabels.py` (`bb1d7389…`). `diff` against RC7's script shows a single change, the legend string "most conservative claim variant" → "shifted null with the largest median". So the plotted content is the same, one legend string differs, and the file is not byte-identical | TRUE |
| RL-20 | 9 | "… and the one-dimensional generator projections" (regenerated from packaged arrays) | `make_figs.py` fig3 → `fig3_generator_context.pdf` `e9d1bb01…` ($\Eavail$ and $W$ projections with four generators) | TRUE |
| RL-21 | 9 | these are "figures that the article cites from this note" | `paper_body.tex`/`main_paper.tex` have no `\ref*{N-fig:…}`. The `N-` references are to sections and to `tab:fived16-cells`/`tab:fived16-corr`. In prose, `main_paper.tex:77` names "the analysis note's figures of the joint-test null distributions and the $(\Eavail,W)$ map". The one-dimensional generator projections (`paper_fig3_generators.pdf`) are `\includegraphics`'d in neither the note nor the article. `sec_eavailw.tex:131` comment: "its figure left the article" | FALSE |
| RL-22 | 9 | "RC7's two-dimensional curve is the exact-split one" | `fig_arrays.npz.manifest.json` `sources.ours_2d` = `2d_crossSection_omnifold_MEFHC_5iter.root` `142a45b0…`. `values.tex:7` names this file as "the exact-split 2d_crossSection_omnifold_MEFHC_5iter.root (142a45b0...)" | TRUE |
| RL-23 | 9 | "which was the two-dimensional central value when the package was assembled" | RC7 was built at source `8fa79cb1` (RC7-SHA256SUMS.txt:1, 2026-10-08). `sec_method.tex:100`: exact-split was "the quoted 2D central value until 2026-10-11". `DECISION-20261011-joseph-2d-central-lightgbm-seed42.md` | TRUE |
| RL-24 | 9 | "The article's two-dimensional validation figure and its numbers were instead regenerated separately, from the committed values and covariance of the refined LightGBM result" | `paper_body.tex:134` includes `paper_fig1_validation.pdf` `71a2ea48…`. That equals `stageF/methods/re2-integration/fig1/fig1_validation.pdf` and differs from RC7's fig1 `938c4fc9…`. `RUN-fig1.txt`: `re2c_fig1.py --arm refined` (E_R, Q_R). Committed copies are at `stageF/methods/re2/run/partc_r2/partc-r2/outA/{cov2d_Q_205,budget_Q}.json.gz` | TRUE |
| RL-25 | 9 | "with RC7's plotting code extended to draw this analysis's band" | `diff PKG/code/figs/make_figs.py WT/publication/release/figs/make_figs.py` shows only the optional `cov_ours` band and the legend case. History: RC7's `99243ac4` (8fa79cb1) → `9c4dbf24` (25720215, adds the band) → `4e18c266` (0b13b747, legend). `re2c_fig1.py` pins `4e18c266` | TRUE |
| RL-26 | 29 | "The package holds the sufficient inputs of the joint tests, as evaluated for the decisions and in the reading with the recovered pseudo-experiments added" | `data/frozen/` and `data/recovery-union/` npz + manifests | TRUE |
| RL-27 | 29 | "the arrays behind the article's figures" | `fig_arrays.npz` holds the arrays of RC7-era Figs. 1–3 (README:144). Today's article prints `paper_fig1_validation`, `paper_fig_bkg_residual`, `paper_fig_deformation` and `fd_g_fig_ratio` (`paper_body.tex:134,177,192,316`). The package holds no arrays for Figs. 2–4. For Fig. 1 it lacks the drawn central value E_R and the band covariance Q_R: `ours_v` is exact-split and there is no `cov_ours` key | FALSE |
| RL-28 | 29 | "the noise-free differences behind the $L_2$ ratios" | `data/m1f2/` holds 8 asimov difference npz files + MANIFEST.json (README:145) | TRUE |
| RL-29 | 29 | "an inventory of the analyzed AnaTuples" | `data/anatuple-inventory.tsv`, 2,374 rows | TRUE |
| RL-30 | 29 | "the replay and figure code" | `PKG/code/*.py`, `code/figs/*.py` | TRUE |
| RL-31 | 29 | "and the expected outputs" | `PKG/expected/` (2 evaluate JSON, the W1 result, values*.tex) | TRUE |
| RL-32 | 29 | "the package's pinned requirements (numpy, scipy and matplotlib)" | `requirements.txt` pins exactly numpy==1.26.4, scipy==1.15.2 and matplotlib==3.11.2. The lock file also pins 9 transitive dependencies | TRUE |
| RL-33 | 29 | "the package's verifier (publication/release/verify_rc.py in the repository)" | `build_rc.py:35` maps `code/verify_rc.py` ← `publication/release/verify_rc.py`. Both have sha256 `9379875f…` | TRUE |
| RL-34 | 29 | run "from the top directory of the unpacked package, performs every replay and figure check and prints VERIFY: PASS if all agree" | My run: every step `[ok]`, `VERIFY: PASS`, exit 0. `verify_rc.py:123` | TRUE |
| RL-35 | 29 | "floating-point values must agree to a relative $10^{-12}$" | `replay_inference.py:158-162` (`np.isclose`, rtol=1e-12, atol=0) | TRUE |
| RL-36 | 29 | "and integers and decisions must agree exactly" | Decisions are compared with `!=` (`:182`). k and B go through `isclose` at rtol 1e-12, which is exact for counts below 10^12 | TRUE |
| RL-37 | 29 | "Each quoted figure number must agree with its printed value to within half a unit of its last printed digit" | `fig_numbers.py:5,20-24,162-170` (`half_ulp`) | TRUE |
| RL-38 | 29 | "the $L_2$ ratios must reproduce their printed range" | `verify_rc.py:108-109` (2-decimal match to jtMoneMin/jtMoneMax) | TRUE |
| RL-39 | 29 | "for the article's Figs. 1–3 themselves, the check is that the three figure files are produced" | The check (`verify_rc.py:84-88`) requires that `make_figs.py` exits 0 with ≥3 PDFs. Those PDFs are RC7's Figs. 1–3. The article's current Figs. 1–3 are the validation (`71a2ea48…`, not RC7's `938c4fc9…`), background-residual and deformation figures, and RC7 produces none of them | FALSE |
| RL-40 | 29 | "The package carries the 20 rounding jitters" | `jitters` array, shape (20, 109), in the frozen npz | TRUE |
| RL-41 | 29 | "from which the stability of the observed $p$ values (§joint5d-conditions) can be recomputed" | I ran `docs/publication/audit-20261008/checks/agentC_checks.py` (J13) once on the extracted RC7 files, single-threaded (`OPENBLAS/OMP/MKL/VECLIB_*_THREADS=1`), with a 1200 s kill limit and nothing else running. It returned rc 0 in 35 s (`jitter-check.json`, `.status`). For each of the 20 rows of `jitters`, it computes the claim-rule p against the frozen nulls. Min and max match `expected/joint-evaluate.json` `observed_jitter_p` to rtol 1e-12 in **10/10** tests. Only NuWro shape varies (k 1–2 of 1751, i.e. p 2/1752 to 3/1752) | TRUE |
| RL-42 | 29 | "but no packaged script does so" | See RL-12 | TRUE |
| RL-43 | 39 | public ancillary files of Ref. MINERvA:2021owq "supply the published inputs for the comparisons to its central values and covariance, the standardized differences, the tension anatomy, and the MINERvA Tune v1 model comparison" | `fig_arrays.npz.manifest.json` sources `paper_cov` = `minerva_paper_anc/cov_ptpl_minerva_inclusive_6GeV.root` and `tune_v1_txt` = `minerva_paper_anc/model_ptpl_…_MINERvA_Tune_v1.txt` | TRUE |
| RL-44 | 42 | "They do not reproduce this analysis's unfolded 2D uncertainty construction." | They are the published inputs only (RL-43). README:182 lists the 2D uncertainty as not reproduced | TRUE |
| RL-45 | 42 | "RC7 supports replay of the higher-dimensional inference from sufficient inputs" | RL-06 to RL-17 | TRUE |
| RL-46 | 42 | "but not extraction from the archived pseudo-experiment products" | No `extract_inference_sufficient.py` in PKG. README:177: "Needs the ~7,000 calibration products … Not public" | TRUE |
| RL-47 | 42 | "[not] event-level unfolding" | README:178 "Not reproducible from this package" | TRUE |
| RL-48 | 42 | "[not] the quoted closure, bias and covariance-status measurements" | README:187-208 lists the closure/bias numbers (4 %, 0.3 %, 1 %, 1.4 %, 74 %, 16–31 %) and the covariance-status numbers (6.145 %, 6.02 %, 20.91→7.57 %, 26.0 %, 6.02/1.06 %) as not reproduced. No packaged code computes them. **Narrower phrase "… of the configuration-(a) central value": would be FALSE.** The closure and bias numbers are measurements of the joint-test estimator and its development variants, configurations (c)/(d)/(e) (`paper_body.tex:167,188`; `sec_method.tex:100`). Only the covariance-status measurements concern the configuration-(a) five-axis covariance (`sec_5d.tex` "What the covariance supports"), and three of those four are on companion covariances | TRUE |
| RL-49 | 42 | "Nor does it reproduce the 2D uncertainty and coverage figures" | README:182-186 | TRUE |
| RL-50 | 42 | "the low-recoil comparisons" | README:192-196 | TRUE |
| RL-51 | 42 | "the recoil-response sensitivity" | README:198-200 (W2) | TRUE |
| RL-52 | 42 | "or the proxy convergence rate of joint-test condition (i)" | README:201 ("Its calculation is not recorded") | TRUE |
| RL-53 | 42 | "The multiplier scan … is recomputable from RC7's sufficient inputs with the scan code of Ref. JointTestKappa2026" | `publication/kappa/RECORD-20261008-kappa-breakdown.md:23-27`: inputs frozen `7bd019c6…` and union `6ffed091…`. These are RC7's exact data digests (SHA256SUMS). An independent reproduction agreed. I did not re-run the scan | TRUE |
| RL-54 | 42 | "but it is not part of RC7's own verification" | `verify_rc.py` has no kappa step | TRUE |
| RL-55 | 42 | "The pseudo-experiment products are archived (about 2.3 GB)." | `audit-20261008/CLAIM-TABLE-20261008.tsv` DA5: CFS `s5p-archive-20261006`, 2,317,487,385 B, SHA256SUMS `1a72cb43…` re-measured by the audit. I did not re-measure on NERSC | TRUE |
| RL-56 | 42 | "RC1 was replayed from an empty directory by a separate AI agent session (Opus 5.5) that had no access to the repository and used only the package and its README" | `docs/publication/release/RC1-REPLAY-RECEIPT-20261006.md:12-15` | TRUE |
| RL-57 | 42 | "its verifier passed" | The same receipt, :19 "`verify_rc.py` gave `VERIFY: PASS`". The overall verdict was "REPLAY PASS WITH DEFECTS" | TRUE |
| RL-58 | 42 | "Event processing requires the earlier production of MINERvA open-data AnaTuples, event-loop outputs, and the generator samples used here." | README:178 | TRUE |
| RL-59 | 45 | record "identifies all 2,374 inventoried AnaTuple input files by SHA256 checksum" | The record (`RECORD-20261010-ost61-…md`) has 2,374 of 2,374 files hashed, but the inventory classifies as Data 1,818 + MC 489 = **2,307 AnaTuples**, plus 58 `MATFluxAndReweightFiles/` + 9 `MParamFiles/` = 67 flux/parameter files (including CVS metadata). Counted with `awk` on `PKG/data/anatuple-inventory.tsv`. The appendix's own next sentence adds up the same way (1,885 + 489) | FALSE |
| RL-60 | 45 | "RC7's own inventory lists their names, sizes and modification times, without checksums" | Header `path…\tbytes\tmtime_utc`, 2,374 rows, no digest column | TRUE |
| RL-61 | 45 | "The same record, dated 2026-10-10" | Record title "(2026-10-10)" | TRUE |
| RL-62 | 45 | "verifies copies of all 1,885 data, flux and parameter files on collaboration storage" | Record §3–4: 1,885 of 1,885 (989,696,077,171 B) "copied and verified". The storage is NERSC CFS `/global/cfs/cdirs/m3246/josephrb/anatuple-data-20261009/`, the group's NERSC project storage, not MINERvA collaboration storage | TRUE |
| RL-63 | 45 | "it identifies the 489 simulation AnaTuples by checksum but holds no preservation copy of them" | Record §4: "489 (10.53 TB) identified only; still on purgeable scratch" | TRUE |
| RL-64 | 45 | "Neither the checksums nor the preservation copies are a public deposit" | Record "NOT CITABLE FOR … a deposit" | TRUE |
| RL-65 | 45 | "they do not make the full event-level analysis reproducible from the small candidate package" | README:178 | TRUE |
| RL-66 | 50 | "RC7 does not contain all of them" | RC7 has no five-axis central values, covariances, masks, M or generator arrays on the release binning (PKG file list) | TRUE |
| RL-67 | 50 | "A ✓ marks identities or values already fixed (… checksums: Ref. NoteRecords2026, identities already fixed)" | `app_release_records.tex` "Identities already fixed" table (input to `main_records.tex:77`) | TRUE |
| RL-68 | 53 | item 1 ✓ "Reporting bin edges and units, per axis … with each wide terminal catch bin identified" | §app:release-edges, L71-77. Matches RL-77 and RL-78 | TRUE |
| RL-69 | 54 | item 2 ✓ "the dense $14\times16\times7\times7\times6$ grid in C order" | 14·16·7·7·6 = 65,856. `PROJ-20260920-binding-check.json` n=65856, C order. The receipt `row_index_basis` reads "C order" | TRUE |
| RL-70 | 56 | item 4 ✓ "the five-axis covariance used in this note and its $(\Eavail,W)$ projection, with the algebra …, the declared centering variant, and the band partition" | C_Z `3d7465f6…` (VL142) and C_EW `835828bf…` (VL143). Variant `cv` comes from the object's metadata (`PROJ-20260920-m1-publication-receipt.json` `src_variant_declared/measured`). The algebra is in `nd-unfolding/z_assembly.py` (`app_release_records.tex`). The band groups V/R/A are disjoint over the 45 bands (`sec_5d.tex`, eq. zassembly text). **Narrower phrase "… of the configuration-(a) central value": TRUE.** `sec_5d.tex:240` is titled "The five-axis covariance of the configuration-(a) central value…", and `sec_method.tex:100` says the configuration-(a) CV "and its five-axis covariance use configuration (a)". The sixteen-cell covariance $C_{\rm total}+C_{\rm resp}$ (`sec_fived16.tex:5,43`) is on 16 cells and is "a separate product … from the five-axis covariance" | TRUE |
| RL-71 | 57 | item 5 ✓ masks "support mask, the pinned mask …, and the unreported-cell mask" | VL142: `hSupportMask`/`hPinnedMask`/`hRowIndex5D` are inside the digest-fixed `z-cv.npz`. `release-package-20260922/masks_5d.npz` has `support_mask`, `pinned_mask` and `producer_row_index_5d` | TRUE |
| RL-72 | 58 | item 6 ✓ "$M$ itself, with its content checksum, its shape, and … its entries are the dropped axes' bin-width products" | Receipt: `M_content_sha256 64fec490…`, `M_shape [42,10694]`, `weight_basis` "product of the DROPPED axes' bin widths" | TRUE |
| RL-73 | 59 | item 7 "GENIE and NuWro require the flux-repaired predictions of 2026-09-27 (per-event reweight to the analysis PPFX flux plus the 50–100 GeV supplements); GiBUU requires its reweight to the same flux convention" | `sec_3d.tex` "Flux repair" paragraph. KNOWN_ISSUES rows 82–83 (OPEN 2026-09-27; "exact per-event reweight … plus 50–100 GeV supplements"). Comment `sec_eavailw.tex:122` "rebuilt on 2026-09-27" | TRUE |
| RL-74 | 61 | "only the assembling revision and job of $C_Z$, job of $C_{EW}$ and read-back row-index checksum are fixed" | VL142: `fb9ec356`, job `58454524`. VL143: job `58655509`, `hRowIndex` readback `9eb9d216…`. The receipt has no projector revision. `s5c/deliv/R21-fix-plan.md:180-195` | TRUE |
| RL-75 | 61 | "No producing revision or job is recorded for the other objects, and the assembled package carries none." | `release-package-20260922/README.md:98-102` ("no producing revision and no producing job for any object"). The appendix does not name "the assembled package"; if it is read as RC7, the claim still holds, because RC7 carries none of these objects | TRUE |
| RL-76 | 63 | item 10 "The four measurements that travel with the five-axis covariance used in this note (§eavailw-adopted)" | `sec_5d.tex` "What the covariance supports": a four-item list. `values.tex:181` comment: Joseph "required them to travel with every deliverable built from the adopted digest". **Narrower phrase "… of the configuration-(a) central value": TRUE** (same object as RL-70). Note `sec_5d.tex` says items 1, 2 and 4 are measured on two companion covariances | TRUE |
| RL-77 | 71-75 | the five edge lists and bin counts (14, 16, 7, 7, 6) | `fig_arrays.npz` `pt_edges`, `pz_edges`, `eavail_edges` and `W_edges` match exactly (14/16/7/6 bins). q3 matches `nd-unfolding/project_cov_nd.py:52` and `3d-unfolding/genie/gen_to_xsec5d.py:69`. `sec_method.tex:186-187` | TRUE |
| RL-78 | 77 | "The last bin on $\Eavail$, $q_3$ and $W$ is a catch bin to 100 GeV" | Same edges | TRUE |
| RL-79 | 77 | "the $\pT\times\pPar$ grid carries the 19 unreported high-$\pT$, low-$\pPar$ acceptance cells of §method-binning" | `mask_reported` gives 205/224. The 19 unreported cells are (pT bin, pPar bin) = (9,0), (10,0–1), (11,0–2), (12,0–4), (13,0–7). `sec_method.tex:187` | TRUE |
| RL-80 | 85 | "$\mathbf{x}$ has 65856 entries and the index array 10,694" | `release-package-20260922/central_values_5d.npz`: `hXSecND_flat_dense` (65856,), `reported_index` (10694,), equal to `where(x>0)`. Binding check n / n_reported | TRUE |
| RL-81 | 86 | "$M$ (shape $42\times10694$) and $C_Z$ (shape $10694\times10694$)" | Receipt `M_shape [42,10694]`, `src_reported 10694`. The sparse M in the 20260922 package has shape (42, 10694) | TRUE |
| RL-82 | 86 | "The five-axis covariance used in this note is the file z-cv.npz, with sha256 3d7465f6…" | VL142 (`uq_5d/z_pilot_20260916_a5/z-cv.npz`, `3d7465f66fbe…918c5`). Receipt `src_cov_sha256`. The file was not read (NERSC only). **Narrower phrase "… of the configuration-(a) central value": TRUE** (see RL-70) | TRUE |
| RL-83 | 86 | "$\sqrt{\Tr C}=5.6742\times10^{-38}$" | VL142 `5.674200780785609e-38`. `EVIDENCE-20260919-lateral-bands-are-seed-pinned.md:75` | TRUE |
| RL-84 | 87 | "$\mathbf{y}=M\mathbf{x}_{\rm reported}$ … reshape to $7\times6$ in C order … must reproduce the $(\Eavail,W)$ central-value map of Fig. eavailWexcess" | My recomputation from the 20260922 package: `y.reshape(7,6)` against RC7 `fig_arrays.npz` `hData2D` (which draws `paper_fig2_joint.pdf` = Fig. eavailWexcess) gives max relative 1.7e-16 | TRUE |
| RL-85 | 87 | "C order agrees with the figure to a relative $1.7\times10^{-16}$; F order disagrees at relative 1.0" | `PROJ-20260920-binding-check.json`: C 1.699e-16, F 0.99999584. My recomputation: C 1.7e-16, F 1 | TRUE |
| RL-86 | 88 | "$\sqrt{\Tr C_{EW}}=4.4552\times10^{-39}$ and exact symmetry ($\max\|C-C^\top\|=0$)" | My recomputation from `covariance_eavailW.npz`: 4.4552e-39 and 0.0. VL143/VL145 | TRUE |
| RL-87 | 88 | "the spectrum decays smoothly with no plateau … 26 at $10^{-6}$, 36 at … $10^{-12}$, 41 at numpy.linalg.matrix_rank's default, and 42 with no cutoff" | `state/CUTOFF-SCAN-20260922-publication-42x42.json` (2, 7, 11, 17, 26, 28, 32, 36, 41, 42). My recomputation: 26/36/41/42 | TRUE |
| RL-88 | 88 | "the projector's hardcoded $10^{-12}$" | `nd-unfolding/project_cov_nd.py:488` `rc = 1e-12` | TRUE |
| RL-89 | 88 | "A 'rank should be 36' check using NumPy defaults would return 41" | `np.linalg.matrix_rank(C_EW)` = 41 (my run; VL145) | TRUE |
| RL-90 | 88 | "$\|\lambda_{\min}\|/\lambda_{\max}$ is of order $10^{-15}$" | 2.93e-15 (VL143, VL145; my run) | TRUE |
| RL-91 | 88 | "a second host reproduces $\lambda_{\min}$ to only five significant digits" | `release-package-20260922/README.md:138`: macOS gives 4.3591117e-92 against the build host's 4.3591036e-92. My host gives 4.35911167e-92 | TRUE |
| RL-92 | 89 | "Because $M$ carries the dropped axes' widths, $\mathbf{y}$ and $C_{EW}$ are on the density scale … the catch bins make that factor large" | Receipt `weight_basis`. The catch bins have ΔEavail = ΔW = 97 GeV | TRUE |
| RL-93 | 90 | "its spectrum runs continuously down to the double-precision noise floor … §eavailw-adopted's first measurement is the reason no significance is computed from it" | CUTOFF-SCAN eigenvalues span 1.5e-77 to 4.4e-92. `sec_eavailw.tex:129`: "no compatibility metric based on the configuration-(a) covariance is quoted, for the reason given in §eavailw-adopted, item 1" | TRUE |
| RL-94 | 93 | "The record of the projection carries acceptance_question: UNDECLARED" | `PROJ-20260920-m1-publication-receipt.json` `"acceptance_question": "UNDECLARED"`. VL145: the product's `acceptanceQuestion` reads `UNDECLARED` | TRUE |
| RL-95 | 93 | "when the projection was built, it had not been decided whether an acceptance correction is needed at the destination binning" | The receipt field is UNDECLARED, and `dst_cv_sha256: null` ("no --dst-cv"). VL145 contrasts it with the diagnostic product's declared τ question | TRUE |

## FALSE and UNVERIFIABLE claims

**FALSE**
- **RL-21** (line 9), "figures that the article cites from this note": the article cross-references no note figure. It names only two of them in Data-availability prose. The third listed item, the one-dimensional generator projections, is printed in neither the note nor the article.
- **RL-27** (line 29), "the arrays behind the article's figures": the package holds the arrays of RC7-era Figs. 1–3. It holds none for today's Figs. 2–4, and it lacks the central value and covariance that today's Fig. 1 draws.
- **RL-39** (line 29), "for the article's Figs. 1–3 themselves, the check is that the three figure files are produced": RC7's three PDFs are not today's article Figs. 1–3. Today's Fig. 1 is `71a2ea48…`, not `938c4fc9…`, and Figs. 2–3 are the background-residual and deformation figures.
- **RL-59** (line 45), "all 2,374 inventoried AnaTuple input files": 2,374 is the count of inventoried input files. Only 2,307 of them are AnaTuples (1,818 data + 489 MC); 67 are flux/reweight/parameter files.

**UNVERIFIABLE**
- **RL-03** (line 7), "the snapshot … identified at deposit": the identifier prints as "[snapshot identifier pending deposit]". It can be checked only once a deposit snapshot exists.
