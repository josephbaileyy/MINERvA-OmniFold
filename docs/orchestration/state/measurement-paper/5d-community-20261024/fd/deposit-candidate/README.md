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

| file | contents |
|---|---|
| `cells.csv` | One row per cell, R00 to R15 in order. Columns: the cell's H2 boxes; its box (lower and upper edge on each of p_T, p∥, E_avail, q3 and W); `gibuu_subset`; `f_cm2_per_nucleon`; `sigma_cm2_per_nucleon` = sqrt of the covariance's diagonal |
| `covariance.csv` | The 16 × 16 reported covariance C_total + C_resp, in (cm²/nucleon)², rows and columns R00–R15. It is byte-identical to the data product's `fd_data_product_C_total_plus_C_resp.csv` |
| `correlation.csv` | Its correlation matrix. It is byte-identical to the data product's `fd_data_product_corr_C_total_plus_C_resp.csv` |
| `deposit.json` | Everything above in one file, plus the axes and their units, the four unreported H2 boxes with their bounds, the GiBUU subset, the labels below, the sha256 of each CSV, and the source digest |

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
  - It is symmetric to 2.2 × 10⁻¹⁶ of its largest entry. Fourteen off-diagonal pairs differ, each by at most 3.4 × 10⁻¹⁶
    of the entry, carried from S1's C_e (C_model_abs and C_resp are exactly symmetric). It is copied as committed.
  - `numpy.linalg.cholesky`, which Stage G uses, reads the lower triangle (`../receipts-deposit/probe_ulp_and_triangle.log`).

## Reproducing the paper's χ²

For a prediction g on its cells c (all sixteen, or GiBUU's eight), Stage G computes (`nd-unfolding/fd_g_compare.py`,
`compare()`):

    d = f − g,     M = C[c, c] + diag(V_g[c])
    total:       χ² = dᵀ M⁻¹ d,                           ndf = n
    shape-only:  χ² = dᵀ (M + 100 f fᵀ)⁻¹ d,  f on c,      ndf = n − 1

Here C is this package's covariance and **V_g is the prediction's own finite-MC variance**. **g and V_g are the
prediction's, not part of this package.** Stage G's readout carries them for its five predictions: `g`, and
`sigma_Vg_over_f`, from which V_g = (sigma_Vg_over_f · f)².

**What the check reproduced:** every Stage G χ², total and shape-only, for all five predictions, from this package plus
the readout's g and V_g, by Stage G's own `compare()` (`../receipts-deposit/`):
- **On login36, in Stage G's environment** (Python 3.11.14, numpy 1.26.4): every one of the ten matches **bit for bit**
  (`check-login36.log`).
- **On a macOS host** (Python 3.12.2, numpy 1.26.4): the totals match to 1.2 × 10⁻¹⁶–2.4 × 10⁻¹⁵ relative, and the
  shape-only values to 1.3 × 10⁻¹¹–5.7 × 10⁻¹¹ (`check-local.log`).
  - On that host, the shape-only values do not move at all under one-ulp changes of C or V_g, or under the other
    summation order of C's parts (`probe_ulp_and_triangle.log`). So the difference is between the two hosts'
    arithmetic, not in the inputs.

The CSVs carry every number as Python's shortest round-trip repr, so they read back as the same IEEE doubles.

## CITABLE FOR

- The 5D result's sixteen cells, measured vector and reported covariance, as committed in the data product
  `b79556f0`, in a deposit layout.
- Reproducing each of Stage G's ten χ² values from them, given the prediction's g and V_g. They reproduce bit for bit
  in Stage G's environment.

## NOT CITABLE FOR

- **A deposit, a release or a DOI.** None exists. The deposit, its citation and the data-availability wording are
  Joseph's (decision items 2 and 3).
- **Coverage.** This is the data product's `not_citable_for`.
  - The fake-data study of this estimator, graded against C_total + C_resp, is `FD-F0b-REPORT.md`, and its grades
    travel with this product.
  - The limitation's wording is Joseph's (`state/2d-closeout/stageF/methods/5d-fd-presentation/DRAFT.md`).
- **Any generator prediction.** No g or V_g is in this package.
- **The variant without C_resp.** Its covariance is not here.
- **Any reading, claim or paper text.**

## Rebuilding and checking

From the repository root:

    python3 -I -B nd-unfolding/fd_deposit_candidate.py build --data-product <fd>/data-product/fd_data_product.json --out-dir <new dir>
    python3 -I -B nd-unfolding/fd_deposit_candidate.py check --package <dir> \
        --data-product <fd>/data-product/fd_data_product.json --g-readout <fd>/readout/fd_g_readout.json

`build` refuses an existing file. `check` refuses (exit 1) unless controls P0–P5 hold (the script's docstring lists
them). The tests are `nd-unfolding/tests/test_fd_deposit_candidate.py`: 20 tests, one planted defect per control,
each asserting that control's clause. 15 of 15 source mutants are killed (`../receipts-deposit/mutants.log`).
