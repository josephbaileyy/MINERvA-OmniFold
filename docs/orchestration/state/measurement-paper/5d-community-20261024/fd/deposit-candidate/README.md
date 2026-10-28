# The 5D sixteen-cell result: deposit candidate (prepared, not deposited)

**Status: a candidate, not deposited.** Nothing here has been uploaded, and no DOI has been minted. Joseph releases it,
after his review with Ben and the MINERvA collaboration review
(`DECISION-20261028-joseph-result-table-and-deposit-package.md` item 2). Until then, this directory is a record in
the analysis repository and nothing more.

**Prepared by** the measurement session, 2026-10-28, at the director's request.

## What it is

These are the 5D result's sixteen reporting cells, R00–R15, in a machine-readable form:
- the cell definitions;
- the measured vector f;
- the reported covariance C_total + C_resp;
- its correlation matrix.

Every number is copied from the committed data product, `fd/data-product/fd_data_product.json` (sha256
`b79556f0538c81942c0ddd3770ae55e5c6fe9ad53df47e470d306f727d7e7072`), by `nd-unfolding/fd_deposit_candidate.py build`.
`fd_deposit_candidate.py check` verifies them against it and against Stage G's readout (`fd/readout/fd_g_readout.json`,
sha256 `75a9ddee…`).

**Apart from the measurement,** `predictions-reference.json` holds the five predictions' g, copied from Stage G's
readout, and V_g recomputed from the `sigma_Vg_over_f` that the readout prints; with them, the paper's χ² is
reproduced. It is labelled "reference predictions used for the paper's χ²; not part of the
measurement". `deposit.json` does not name it, so the measurement stands without it.

| file | contents |
|---|---|
| `cells.csv` | One row per cell, R00 to R15 in order. Columns: the cell's H2 boxes; its box (lower and upper edge on each of p_T, p∥, E_avail, q3 and W); `gibuu_subset`; `f_cm2_per_nucleon`; `sigma_cm2_per_nucleon` = sqrt of the covariance's diagonal |
| `covariance.csv` | The 16 × 16 reported covariance C_total + C_resp, in (cm²/nucleon)², rows and columns R00–R15. It is byte-identical to the data product's `fd_data_product_C_total_plus_C_resp.csv` |
| `correlation.csv` | Its correlation matrix. It is byte-identical to the data product's `fd_data_product_corr_C_total_plus_C_resp.csv` |
| `deposit.json` | Everything above in one file, plus the axes and their units, the four unreported H2 boxes with their bounds, the GiBUU subset, the labels below, the sha256 of each CSV, and the source digest |
| `predictions-reference.json` | **Not part of the measurement.** For each of Stage G's five predictions (GENIE 2.12.10 CV; GENIE 2.12.10 + Valencia MEC; NuWro 21.09; GiBUU 2019; MINERvA Tune v1): its label, its source file and sha256 (as `fd_g_compare.PREDICTIONS` and the readout give them), its cells (GiBUU's eight, all sixteen for the others), g in cm²/nucleon, Stage G's `sigma_Vg_over_f`, V_g = (sigma_Vg_over_f · f)² in (cm²/nucleon)², and Stage G's total and shape-only χ² and ndf |

**A separate item for Joseph at release:** whether `predictions-reference.json` goes into the deposit is his call,
apart from the measurement.

## Conventions

- **Order:** every vector and matrix is in the cell order R00, R01, …, R15, which is `cells.csv`'s row order.
- **Units:**
  - **f:** each cell's integrated cross section, in cm²/nucleon. It is a **cell integral, not a differential
    density**: the sum over the cell's fine cells of the cross section times the fine cell's volume (S1's integration
    rule).
  - **Covariance:** in (cm²/nucleon)².
  - **Box edges:** p_T and p∥ in GeV/c; E_avail, q3 and W in GeV (`docs/analysis-note/app_release.tex`, release
    schema item 1).
- **The "100" edges:**
  - On E_avail, q3 and W, the upper edge 100 GeV is the analysis grid's last edge: the last bin on those axes is a
    catch bin to 100 GeV (`app_release.tex`, §"Bin edges"; `s5p_stage1_inspect.FINE`).
  - 4.5 GeV/c on p_T and 60 GeV/c on p∥ are the grid's outer edges too.
  - A cell's integral covers only its box inside the grid, and no edge stands for infinity.
- **The cells:**
  - Each cell is a box in the five variables. It is exactly the union of its H2 boxes, which the check verifies.
  - The H2 grid has two bins per axis, with edges p_T 0, 0.7, 4.5; p∥ 1.5, 4.5, 60; E_avail 0, 0.8, 100; q3 0, 2.0,
    100; W 0, 1.8, 100. Box indices run in C order over (p_T, p∥, E_avail, q3, W).
  - The sixteen cells cover 28 of the 32 H2 boxes. Boxes 2, 6, 10 and 14 are not reported and are in no cell; their
    bounds are in `deposit.json`.
  - Box 17, unsupported on its own, enters R09 through the purity merges.
- **GiBUU's subset:** GiBUU is compared on the eight cells with p∥ < 4.5 GeV/c only, R00–R03 and R08–R11
  (`gibuu_subset = 1`). Stage G forms no GiBUU value on the other eight cells.
- **The covariance:**
  - C_total + C_resp = C_e + C_model_abs + C_resp, the data's reported covariance (`DECISION-20261026-joseph-adopt-cresp.md`).
    Its parts are in the data product, not here.
  - It is not bit-exactly symmetric. Fourteen off-diagonal pairs differ, by up to 8 ulp: at most 1.45 × 10⁻¹⁵ of the
    entry itself, and 2.2 × 10⁻¹⁶ of the matrix's largest entry. They are among C_e's fifteen asymmetric pairs, from
    S1's assembly; C_model_abs and C_resp are exactly symmetric. The matrix is copied as committed.
  - `numpy.linalg.cholesky`, which Stage G uses, reads the lower triangle (`../receipts-deposit/probe_ulp_and_triangle.log`).

## Reproducing the paper's χ²

For a prediction g on its cells c (all sixteen, or GiBUU's eight), Stage G computes (`nd-unfolding/fd_g_compare.py`,
`compare()`):

    d = f − g,     M = C[c, c] + diag(V_g[c])
    total:       χ² = dᵀ M⁻¹ d,                           ndf = n
    shape-only:  χ² = dᵀ (M + 100 f fᵀ)⁻¹ d,  f on c,      ndf = n − 1

Here C is this package's covariance and **V_g is the prediction's own finite-MC variance**. g and V_g are the
prediction's, not part of the measurement. For Stage G's five predictions they are in `predictions-reference.json`,
where V_g = (sigma_Vg_over_f · f)² is recomputed from the `sigma_Vg_over_f` that Stage G's readout prints. With
it, every χ² below is reproduced.

**What the check reproduced:** every Stage G χ², total and shape-only, for all five predictions, from the package files
alone (`cells.csv`'s f, `covariance.csv`, and `predictions-reference.json`'s g and V_g), by Stage G's own `compare()`,
against `fd_g_readout.json` (`../receipts-deposit/`):
- **On login36, in Stage G's environment** (Python 3.11.14, numpy 1.26.4): every one of the ten matches **bit for bit**
  (`check-login36.log`).
- **On a macOS host** (Python 3.12.2, numpy 1.26.4): the totals match to 1.2 × 10⁻¹⁶–2.4 × 10⁻¹⁵ relative, and the
  shape-only values to 1.3 × 10⁻¹¹–5.7 × 10⁻¹¹ (`check-local.log`). The inputs are bit-identical to Stage G's (P2,
  P6), so the difference is the two hosts' arithmetic.

**How precisely the shape-only χ² can be reproduced** (`probe_ulp_and_triangle.log`, section iii):
- Its matrix C + V_g + 100 f fᵀ is dominated by the free-normalization term: the largest entry of 100 f fᵀ is
  2.3 × 10⁴–3.6 × 10⁴ times the largest entry of C + V_g, and the matrix's condition number is 2 × 10⁷–6 × 10⁸.
- So a one-ulp change of every C entry changes none of the matrix's entries; that change is lost in rounding. One ulp
  of one entry of f (R03, the one the probe perturbs) moves the shape-only χ² by 1.8 × 10⁻¹²–3.9 × 10⁻¹¹.
- An independent solver (`numpy.linalg.solve`, with 100 f fᵀ built entry by entry) reproduces Stage G's shape-only χ²
  to 1.3 × 10⁻¹¹–2.9 × 10⁻¹⁰ relative, and its total χ² to 1.1 × 10⁻¹⁶–4.0 × 10⁻¹⁵. Check P5's tolerance, 10⁻¹⁰, is
  defined on Stage G's own `compare()`. **Outside `compare()`, expect the shape-only χ² to about 3 × 10⁻¹⁰ and the
  total χ² to a few × 10⁻¹⁵.**

The CSVs carry every number as Python's shortest round-trip repr, so they read back as the same IEEE doubles.

## CITABLE FOR

- The 5D result's sixteen cells, measured vector and reported covariance, as committed in the data product
  `b79556f0`, in a deposit layout.
- Reproducing each of Stage G's ten χ² values from the package files, with `predictions-reference.json`'s g and V_g.
  They reproduce bit for bit in Stage G's environment.

## NOT CITABLE FOR

- **A deposit, a release or a DOI.** None exists. The deposit, its citation and the data-availability wording are
  Joseph's (decision items 2 and 3).
- **Coverage.** This is the data product's `not_citable_for`.
  - The fake-data study of this estimator, graded against C_total + C_resp, is `FD-F0b-REPORT.md`, and its grades
    travel with this product.
  - The limitation's wording is Joseph's (`state/2d-closeout/stageF/methods/5d-fd-presentation/DRAFT.md`).
- **Any generator prediction as a measurement.** `predictions-reference.json` is the reference Stage G compared
  against, copied from its readout; it measures nothing, and whether it is deposited is Joseph's call.
- **The variant without C_resp.** Its covariance is not here.
- **Any reading, claim or paper text.**

## Rebuilding and checking

From the repository root:

    python3 -I -B nd-unfolding/fd_deposit_candidate.py build --data-product <fd>/data-product/fd_data_product.json \
        --g-readout <fd>/readout/fd_g_readout.json --out-dir <new dir>
    python3 -I -B nd-unfolding/fd_deposit_candidate.py check --package <dir> \
        --data-product <fd>/data-product/fd_data_product.json --g-readout <fd>/readout/fd_g_readout.json
    python3 -I -B nd-unfolding/fd_deposit_candidate.py check --package <dir> \
        --data-product <fd>/data-product/fd_data_product.json --measurement-only

- `build` (which also takes `--g-readout`) refuses an existing file.
- `check` refuses (exit 1) unless controls P0–P7 hold; the script's docstring lists them. P7 requires every file to
  be what `build` writes from the pinned inputs: the CSVs byte for byte, and every field of both JSON files, value and
  JSON type, including labels, units, status and domains, except `code_sha256`.
- `check --measurement-only` checks the four measurement files alone (P0–P4 and P7), without
  `predictions-reference.json` or Stage G's readout, so the measurement can be checked if the reference file is not
  deposited (`../receipts-deposit/check-local-measurement-only.log`).
- The tests are `nd-unfolding/tests/test_fd_deposit_candidate.py`: 48 tests, with planted defects that each reach and
  assert their own control's clause.
- 32 of 32 source mutants are killed by a targeted test (`../receipts-deposit/mutants.log`). The test that compares
  the committed package with a fresh build is skipped for this count, because every file embeds the code's sha256 and
  that test fails on any source change.
