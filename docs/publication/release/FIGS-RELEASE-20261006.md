# Release of the arrays behind the article's Figs. 1–3 (2026-10-06; local, NOT released)

**CITABLE FOR:**
- the identities of the inputs behind the article's Figs. 1–3 and their quoted numbers;
- the exported arrays;
- the standalone regeneration and number-check results.

**NOT CITABLE FOR:**
- a release, deposit or tag;
- any 2D uncertainty (VL162 superseded, VL170 rebuild pending; not exported).

**Paper-wide rows addressed:** R1, R3, R9 (partly), R10, R11. R8 is not covered (§4).

**Authority:** Joseph item 6, release preparation.
**Lane:** release-figs, branch `release/article-figures-20261006`.
**Cost:** login node only (export 9.7 s wall, 250 MB RSS); no allocation.

## 1. Files (`publication/release/figs/`)

| file | role |
|---|---|
| `export_fig_arrays.py` | Cluster exporter. It imports the committed producers' own loaders (`compare_to_paper_fullcov`, `compare_to_models`, `agreement_windows_receipt.bin_areas`, `overlay_eavailW_band`, `excess_eavail_W`, `xsec_nd`) from a clean clone, and refuses any other import origin (OI-136). |
| `_data/fig_arrays.npz` (+ `.manifest.json`, `export.txt`) | The exported arrays, sha256 `72394a2b4eff9f14b01903ff97525bcb690c2adee58ccaf573a8d95139b415b8` (640 KB). Exported from clone `556d6dde`. |
| `fig_numbers.py` | numpy only: recomputes every number the article quotes from Figs. 1–3 and checks each against its printed value, at half a unit of the last printed digit |
| `make_figs.py` | numpy and matplotlib only: regenerates Figs. 1–3 (same quantities; not pixel-identical) |

## 2. Source identities (re-hashed on the cluster 2026-10-06; all in the manifest)

| source | sha256 | used for |
|---|---|---|
| `2d-unfolding/2d_crossSection_omnifold_MEFHC_5iter.root` (`hXSec2D`) | `142a45b0…` | Fig. 1 (our 2D result) |
| `2d-unfolding/minerva_paper_anc/cov_ptpl_minerva_inclusive_6GeV.root` | `6c6dce72…` | Fig. 1 (published σ, Total and StatOnly covariances) |
| `…/model_ptpl_minerva_inclusive_6GeV_MINERvA_Tune_v1.txt` | `22231752…` | Fig. 1 (Tune v1) |
| `nd-unfolding/products/5d/excess_eavail_W.root` | `751bb859…` | Figs. 2–3 (`hData2D`, `hGenCV2D`, `hExcess2D`). It matches the s5p harness lane pin. |
| `nd-unfolding/products/5d/xsec_5d_MEFHC_5iter_lgbm.root` | `630306e2…` | cross-check only |
| Stage-7 `genie_cv/genie_mec/nuwro_cv/gibuu_cv_xsec_eavailW.root` | `debaf83e…` / `1098e912…` / `d7d46a0c…` / `b430ddc6…` | Fig. 3. They match the generator-context receipt sidecars, which carry each prediction's flux-repaired 5D source and code digest. |
| `s5p-20260926/gen5d/mnvtune_v1_xsec5d.npz` | `bf7bd278…` | cross-check only |

**Generator versions** (repository records, paper-wide table §2):
- GENIE 2.12.10 on CH, without MEC, and with Valencia 2p2h (Default+CCMEC);
- NuWro 21.09 on C;
- GiBUU 2019 on C, which lacks E_ν > 20 GeV;
- GENIE and NuWro use the repaired flux (KNOWN_ISSUES 83).

**Comparator identity** (R10a): the Fig. 2 comparator `hGenCV2D` is `mc_truth_denom` × `w_truth`, i.e. MINERvA
Tune v1 (the OmniFold prior), although the producer labels it "GENIE CV".

## 3. Results

**Cross-checks (report-only, in the manifest):**
- `hData2D` re-projected from the 5D product with the producer's own functions: **bitwise equal** (max relative
  difference 0.0).
- The Fig. 2 comparator against the s5p MnvTune v1 5D prediction projected to (E_avail, W): ratio 1 within 4e-16.
  This independently confirms that the comparator is Tune v1.
- `hExcess2D` = (data − comparator) × cell area, to within 3e-55 (the cell-integrated cross section is of order
  1e-39).

**Numbers** (`fig_numbers.py`, at the printed precision):

| quantity | recomputed | printed | result |
|---|---|---|---|
| \sigTwoD | 3.0733e-38 | 3.073e-38 | ok |
| \sigTwoDpaper | 3.0390e-38 | 3.039e-38 | ok |
| \ratioTot | 1.01129 | 1.011 | ok |
| \binsTen | 94.15 | 94.1 | ok |
| \pullMean | 0.0889 | 0.089 | ok |
| \pullRMS | 0.5981 | 0.598 | ok |
| \chiPaper | 3.6609 | 3.66 | ok |
| data vs Tune v1 χ²/ndf | 33.039 | 33.04 | ok |
| ours vs Tune v1 χ²/ndf | 26.491 | 26.49 | ok |
| integrated data/prediction ratios | 1.0676–1.3859 | 1.07–1.39 | ok |
| 2.2 ≤ W < 3.0 ratios (GENIE, NuWro) | 1.1108–1.1299 | 1.11–1.13 | ok |
| integrated ratios (GENIE, NuWro) | 1.0676–1.1529 | 1.07–1.15 | ok |
| corner ratios (GENIE, NuWro) | 1.1386–1.1601 | 1.14–1.16 | ok |
| GiBUU corner / overall | 1.6070 / 1.3859 | 1.61 / 1.39 | ok |
| corner within 7% of integrated | max 6.65% | ≤ 7% | ok |
| reported bins | 205 | 205 | ok |
| **\uqPaper** | **6.852** (√diag/published σ) or 6.847 (√diag/our σ) | **6.86** | **DISCREPANCY** |

**The \uqPaper discrepancy, reported as found and not adjusted:**
- Printed: 6.86% ("Paper TotalCov (for reference) … 6.86 %", `2d-unfolding/2D_OMNIFOLD_STUDY_STATUS.md:102`). No
  committed producer was found.
- The median of √diag(TotalCov) over the 205 reported bins gives 6.852% relative to the published σ, and 6.847%
  relative to our σ.
- The difference is 0.01 percentage points, so the inset's "6.86" would print as "6.85" under either definition.
- Owner disposition needed: either identify the original definition, or correct the printed value. It is
  independent of the VL170 rebuild (it is the published covariance).

The note-only shares (not quoted in the article) are reproduced as 67.2% and 83.2%, against the note's 67% and 83%.

## 4. Not covered

- The article's "higher energies carry 14–15% of this region's cross section and 7% of the total" and "1.37
  against 1.29" (GiBUU with the share supplied). These come from VL161 (the E_ν ≥ 20 GeV shares), not from these
  arrays. Covering them needs the per-E_ν generator predictions.
- R8, the "within 10% of" Ascencio comparison on (E_avail, q3): not exported.
- The 2D uncertainty numbers (6.87% "This work" median; combined χ²): VL170 rebuild pending.
- The 5D central values are already in `release-package-20260922` (R9).
- Fig. 3 is also regenerated, bitwise apart from PDF metadata, by the s5p reproduction harness at tier B
  (`reproduction/s5p/scope.py` FIGURE_RUNS `eavailW_band`). It pins `eavailW_band.pdf` `555c5f1e…` and the paper
  crop `paper_eavailW_generators.pdf` `db10ba41…`. This package does not duplicate that.

## 5. Joining RC1

RC2 should add `_data/fig_arrays.npz` (+ manifest), `fig_numbers.py` and `make_figs.py` to RC1's `data/` and
`code/`, plus a `verify_rc.py` step that runs `fig_numbers.py`. That step currently exits 1 until \uqPaper is
dispositioned. The publication lane assembles RC2.
