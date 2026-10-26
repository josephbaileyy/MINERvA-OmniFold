# REPORT G-FOLLOWUP: a per-cell look at R04 and the correlation sensitivity of Stage G's χ² (2026-10-26)

**By** the measurement session.

**Under** [`FD-G-FOLLOWUP-BINDING.md`](FD-G-FOLLOWUP-BINDING.md) (PR #389, main `3df55f5e`).
- It binds [`FD-G-FOLLOWUP-DECLARATION.md`](FD-G-FOLLOWUP-DECLARATION.md) with its amendment 1, at deploy pin
  `02bf756a`.
- The report follows the binding's §3 item 4.

**MEASURES:**
- **G-R04:** for R04 and the cells that load with it in G-DIAG's committed top modes (R00, R01, R07, R08, R09, R10 and
  R14):
  - the definition's geometry;
  - f's relative σ by block;
  - R04's correlations;
  - Stage G's per-cell values;
  - a key search of the pinned products.
- **G-SENS:** Stage G's reported χ² with one family of covariance groups shrunk toward the diagonal, keeping their
  variances.

**CANNOT AUTHORIZE:**
- an alternative to Stage G's reported χ² or covariance;
- a p value on any shrunk comparison;
- any reading of these numbers, a claim or printed wording, which are Joseph's.

**CITABLE FOR:** the numbers below, as `fd/readout/fd_g_followup_readout.json` holds them.

**NOT CITABLE FOR:**
- an interpretation;
- a shrunk χ² as a result. Every G-SENS record is labelled "descriptive sensitivity of the reported χ², not an
  alternative result".

**Outcome:**
- **Both steps exited 0** on login33 at 0 node-h, with no Slurm job.
  - **The deploy:** "Ran 148 tests … OK".
  - **The run:** it took about 1 s. G-DIAG's D0–D5 and F0, R1–R4 and S0–S2 passed (37 lines), and `followup.err` is
    empty.
- **Stage G was reproduced.** D5 matched it with worst relative difference 0.0. S0 found α = 0 equal to Stage G's
  reported χ² for every family and prediction, to 1.3 × 10⁻¹⁴ relative at worst.
- **The shrinkage was the declared one** (S2):
  - every shrunk diagonal was bit-identical;
  - every off-diagonal was exactly (1 − α) times the original;
  - every block outside the family was bit-identical, normalization included.
- **Every shrunk M is positive definite** (S1). The smallest λ_min of any M is 1.95 × 10⁻⁵, relative to f.
- **No record is flagged unstable.** The largest relative difference of the mode-sum or least-squares χ² from
  Cholesky is 1.7 × 10⁻¹⁴ (1.9 × 10⁻¹⁴ pairwise across all three). The largest ridge change is 9.0 × 10⁻⁹.
- **Item 2's σ** reproduce S1's committed readout to 2.0 × 10⁻¹⁶ (R2). S1's seed group is 0 on every cell, as
  committed.
- **The readout** is `cd82517afdfb1dc8383580c8a4c57e82d9b87864e75d28528cb35c4455f6e379`, schema
  `fd-g-followup-readout/1`, 155,395 bytes, with no non-finite values and no key `p`.

## 1. The steps

| step | host | start (UTC) | end | rc | wall | result |
|---|---|---|---|---:|---:|---|
| §2.1 deploy and tests | login33 | 18:36:24 | 18:37:50 | 0 | 86 s | `$B=/pscratch/sd/j/josephrb/fd-g-followup-20261026` absent before; HEAD `02bf756a…`; porcelain 0 before and after; every §8 digest matches (`fd_g_followup.py` `820b67c2…`, tests `6697e63d…`, `fd_g_diag.py` `241bfd02…`, the Stage G readout `75a9ddee…`, the G-DIAG readout `680dc5ef…`), and the declaration's is `7fd1c807…`, the binding's; `tests rc=0`, "Ran 148 tests in 55.279s", OK |
| §2.2 the run | login33 | 18:38:07 | 18:38:08 | 0 | 1 s | D0–D5, F0, R1–R4 and S0–S2 PASS (37 lines); readout written; `followup.err` empty |

All on 2026-10-26.

- **The start time:** the deploy start, 18:36:24, is the local stamp when the script was sent (`f1-launch.txt`).
  `deploy.log`'s first stamp, 18:36:51, follows the clone.
- **The scripts:**
  - `f1.sh` is §2.1 verbatim, with `set -u`, the variable definitions, a guard that refuses if `$B` exists, an end
    stamp appended to `deploy.log`, and a closing `cat`/`grep`.
  - `f2.sh` is §2.2 verbatim, with guards that refuse unless the deploy shows `tests rc=0` and if the readout exists,
    plus start and end stamps, and a closing `cat`/`grep`/`tail`/`ls`.
  - **No launch stamps were recorded** for `f2.sh` or for `post-run.txt`. Both ran by `ssh saul.nersc.gov bash -s` /
    a one-line `ssh` (`echo` stamp, `ls -la $B`, `du -sh $B`), and each output carries its own start stamp.
  - Neither names a CFS path.
- **`$B` after the run:** the deploy clone, `logs/`, `tmp/` and the readout, 576 MB in all (`post-run.txt`).
- **The copies:** the readout and the five logs were copied back. Their local digests (`SHA256SUMS`) equal the
  cluster-side `sha256sum` taken afterwards (`cluster-sha256.txt`, 18:48:16Z).

**The run's own control lines** beyond D0–D5 (`followup.out`):

```text
PASS control F0 the G-DIAG readout is pinned and ran on this Stage G readout, extra block and comparison
PASS control R1 the listed cells are reporting cells R00-R15, reported
PASS control R1 each cell's box is the bounding box of its H2 boxes, which fill it
PASS control R1 the fine-bin counts are U's nonzero entries
PASS control R1 the counts and the unreported fine bins cover the fine grid
PASS control R2 S1's readout carries every group's and total's relative sigma and median
PASS control R2 every group's and total's relative sigma, and item 2's median of it, is S1's committed one (worst 2.0e-16)
PASS control R2 the three vertices' variances sum to S1's C_model variance (worst 3.7e-16)
PASS control R2 sigma of C_total + C_resp is Stage G's reported sigma_total_over_f (worst 0.0e+00)
PASS control R3 every correlation is within [-1, 1]
PASS control R3 the blocks rebuild the correlations of C_total + C_resp (worst 4.4e-16)
PASS control R4 every reported pull is -(g/f - 1)/sqrt(sigma_total^2 + sigma_Vg^2) (worst 1.5e-13)
PASS control S0 alpha = 0 reproduces Stage G's reported chi2 for every family and prediction to 1e-10 (worst 1.3e-14)
PASS control S1 every shrunk M is positive definite
PASS control S2 every shrunk group's diagonal, and every shrunk M's, is the unshrunk one bit for bit
PASS control S2 every shrunk group's off-diagonal is (1 - alpha) times the unshrunk one (worst 0.0e+00)
PASS control S2 every block outside the family is unchanged bit for bit
```

**G-DIAG reproduces from its own deploy.** `fd_g_diag.py` changed by the declaration's §6.1 refactor, from
`7c161280…` to `241bfd02…`. The committed identity receipt shows identical outputs on six synthetic trees
(`fd/receipts-g-followup/declaration/refactor_identity.log`). G-DIAG's bound bytes and its readout `680dc5ef…` remain
reproducible from its deploy at `d02ce2f2`.

## 2. G-R04

### 2.0 Provenance: the cells in G-DIAG's top modes

G-DIAG's reported comparison, relative to f, for the four 16-cell predictions. The columns give each top mode's
number, σ, χ² fraction, R04's rank by |loading|, and the eight cells' loadings. Mode numbers index that matrix's
eigenvalues in descending order. The predictions' labels:

| prediction | label (the readout's, verbatim) |
|---|---|
| genie_cv | GENIE 2.12.10 CV, no MEC; CH |
| genie_mec | GENIE 2.12.10 + Valencia MEC; CH |
| nuwro | NuWro 21.09; C12 target; no correction to CH applied |
| gibuu | GiBUU 2019; C12 target; no correction to CH applied; no events above E_nu = 20 GeV (KNOWN_ISSUES 82), so it is compared on the eight p_parallel < 4.5 cells only and not shown above p_parallel 4.5 (FD-DIRECTOR-RULINGS.md section 5) |
| mnvtune_v1 | MINERvA Tune v1, the analysis MC truth: prior (not an independent prediction) |

| prediction | mode | sigma % | fraction % | R04 rank | R04 | R00 | R01 | R07 | R08 | R09 | R10 | R14 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| genie_cv | 7 | 3.15 | 40.6 | 16 | -0.02 | -0.04 | +0.17 | -0.10 | +0.10 | +0.11 | -0.27 | -0.19 |
| genie_cv | 13 | 1.14 | 19.1 | 1 | +0.45 | +0.32 | -0.36 | -0.29 | -0.42 | +0.30 | -0.16 | -0.33 |
| genie_cv | 12 | 1.21 | 11.5 | 14 | +0.08 | -0.33 | -0.23 | -0.09 | +0.10 | +0.53 | +0.12 | +0.20 |
| genie_mec | 13 | 1.15 | 45.5 | 1 | +0.45 | +0.30 | -0.37 | -0.30 | -0.42 | +0.33 | -0.15 | -0.32 |
| genie_mec | 7 | 3.17 | 22.3 | 16 | -0.01 | -0.04 | +0.17 | -0.10 | +0.10 | +0.11 | -0.27 | -0.19 |
| genie_mec | 15 | 0.67 | 15.6 | 1 | +0.72 | -0.35 | +0.13 | +0.07 | +0.13 | -0.27 | -0.27 | -0.02 |
| nuwro | 15 | 0.61 | 31.3 | 1 | +0.63 | -0.34 | +0.11 | +0.05 | +0.18 | -0.22 | -0.37 | -0.03 |
| nuwro | 10 | 1.98 | 11.5 | 11 | +0.12 | +0.22 | -0.33 | -0.28 | +0.15 | -0.14 | +0.04 | +0.57 |
| nuwro | 5 | 6.60 | 10.7 | 8 | +0.16 | +0.40 | +0.08 | -0.38 | +0.58 | -0.02 | +0.08 | -0.07 |
| mnvtune_v1 | 13 | 0.97 | 47.9 | 1 | +0.54 | +0.26 | -0.22 | -0.28 | -0.38 | +0.05 | -0.05 | -0.41 |
| mnvtune_v1 | 7 | 3.01 | 16.4 | 16 | -0.02 | -0.05 | +0.16 | -0.08 | +0.11 | +0.10 | -0.28 | -0.21 |
| mnvtune_v1 | 14 | 0.63 | 13.6 | 1 | +0.60 | -0.24 | +0.23 | +0.26 | -0.09 | -0.39 | +0.31 | +0.15 |

### 2.1 Item 1: the definition

The box edges are in GeV. Neighbours share a face on the 2⁵ H2 grid, and the axis
named is the one along which they touch.

| cell | H2 boxes | p_T | p_par | E_avail | q3 | W | fine bins | neighbours (axis) |
|---|---|---|---|---|---|---|---|---|
| R04 | 8, 9 | 0–0.7 | 4.5–60 | 0–0.8 | 0–2 | 0–100 | 11520 | R00 (pz), R05 (q3), R06 (eavail), R07 (eavail), R12 (pt), unreported H2 box 10 (q3) |
| R00 | 0, 1 | 0–0.7 | 1.5–4.5 | 0–0.8 | 0–2 | 0–100 | 6912 | R01 (q3), R02 (eavail), R03 (eavail), R04 (pz), R08 (pt), R09 (pt), unreported H2 box 2 (q3) |
| R01 | 3, 7 | 0–0.7 | 1.5–4.5 | 0–100 | 2–100 | 1.8–100 | 1008 | R00 (q3), R03 (q3), R05 (pz), R09 (pt), unreported H2 box 2 (W), unreported H2 box 6 (W) |
| R07 | 13 | 0–0.7 | 4.5–60 | 0.8–100 | 0–2 | 1.8–100 | 4320 | R03 (pz), R04 (eavail), R05 (q3), R06 (W), R15 (pt) |
| R08 | 16, 18 | 0.7–4.5 | 1.5–4.5 | 0–0.8 | 0–100 | 0–1.8 | 3024 | R00 (pt), R09 (W), R10 (eavail), R11 (eavail), R12 (pz), R13 (pz), unreported H2 box 2 (pt) |
| R09 | 17, 19, 21, 23 | 0.7–4.5 | 1.5–4.5 | 0–100 | 0–100 | 1.8–100 | 5292 | R00 (pt), R01 (pt), R03 (pt), R08 (W), R10 (W), R11 (W), R12 (pz), R14 (pz), R15 (pz) |
| R10 | 20 | 0.7–4.5 | 1.5–4.5 | 0.8–100 | 0–2 | 0–1.8 | 1944 | R02 (pt), R08 (eavail), R09 (W), R11 (q3), R15 (pz) |
| R14 | 27, 31 | 0.7–4.5 | 4.5–60 | 0–100 | 2–100 | 1.8–100 | 1260 | R05 (pt), R09 (pz), R12 (q3), R13 (W), R15 (q3) |

### 2.2 Item 2: f's relative σ, by block (%)

√diag(B)/f. A vertex's is |s_j|.

| block | R04 | R00 | R01 | R07 | R08 | R09 | R10 | R14 | median of 16 |
|---|---|---|---|---|---|---|---|---|---|
| stat | 0.14 | 0.20 | 0.23 | 0.30 | 0.22 | 0.18 | 0.25 | 0.16 | 0.24 |
| interaction | 0.58 | 0.98 | 1.18 | 5.08 | 1.52 | 1.85 | 5.53 | 1.22 | 2.19 |
| flux | 3.47 | 3.93 | 3.58 | 3.90 | 3.74 | 3.52 | 3.42 | 3.73 | 3.55 |
| detector | 1.31 | 1.56 | 2.14 | 1.76 | 2.17 | 2.18 | 2.42 | 2.14 | 1.89 |
| lateral | 0.57 | 5.01 | 4.85 | 1.75 | 0.77 | 1.08 | 0.43 | 1.34 | 2.38 |
| normalization | 1.40 | 1.40 | 1.40 | 1.40 | 1.40 | 1.40 | 1.40 | 1.40 | 1.40 |
| seed | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| C_model:genie_mec | 0.25 | 0.11 | 0.12 | 0.41 | 1.04 | 0.03 | 0.19 | 0.03 | 0.36 |
| C_model:nuwro | 0.67 | 0.17 | 0.04 | 1.59 | 1.26 | 2.40 | 0.95 | 0.48 | 0.81 |
| C_model:gibuu | 0.51 | 0.38 | 0.66 | 3.04 | 0.03 | 2.17 | 3.91 | 0.66 | 2.79 |
| C_resp | 0.70 | 2.07 | 2.35 | 1.55 | 3.58 | 2.26 | 2.69 | 1.82 | 2.14 |
| C_e | 4.05 | 6.77 | 6.66 | 7.02 | 4.86 | 4.87 | 7.10 | 4.87 | 6.45 |
| C_model | 0.88 | 0.43 | 0.67 | 3.45 | 1.63 | 3.24 | 4.03 | 0.82 | 3.34 |
| C_total | 4.14 | 6.79 | 6.69 | 7.82 | 5.13 | 5.84 | 8.16 | 4.94 | 6.74 |
| C_total + C_resp | 4.20 | 7.10 | 7.10 | 7.98 | 6.25 | 6.26 | 8.59 | 5.27 | 7.29 |

### 2.3 Item 3: R04's correlation with each cell

B_ij/√(B_ii B_jj). The rank of each matrix is written beside it.
- A rank-one block (each vertex; normalization) gives ±1 by construction.
- The seed block is zero, so its correlations are null.
- The last four rows are each 16-cell prediction's reported Stage G matrix. GiBUU is not compared on R04 in Stage G.

| matrix | rank | R00 | R01 | R07 | R08 | R09 | R10 | R14 |
|---|---|---|---|---|---|---|---|---|
| C_total + C_resp | 16 | +0.546 | +0.443 | +0.470 | +0.811 | +0.724 | +0.402 | +0.709 |
| stat | 16 | +0.108 | -0.060 | +0.068 | +0.001 | -0.080 | -0.169 | -0.187 |
| interaction | 16 | +0.623 | -0.332 | +0.147 | +0.245 | +0.220 | -0.253 | +0.098 |
| flux | 16 | +0.978 | +0.998 | +0.972 | +0.983 | +0.993 | +0.979 | +0.982 |
| detector | 4 | +0.978 | +0.985 | +0.722 | +0.987 | +0.994 | +0.953 | +0.736 |
| lateral | 5 | -0.835 | -0.951 | -0.142 | +0.017 | +0.988 | +0.773 | +0.907 |
| normalization | 1 | +1.000 | +1.000 | +1.000 | +1.000 | +1.000 | +1.000 | +1.000 |
| seed | 0 | null | null | null | null | null | null | null |
| C_model:genie_mec | 1 | -1.000 | -1.000 | -1.000 | +1.000 | +1.000 | -1.000 | -1.000 |
| C_model:nuwro | 1 | -1.000 | +1.000 | +1.000 | +1.000 | +1.000 | -1.000 | -1.000 |
| C_model:gibuu | 1 | -1.000 | +1.000 | -1.000 | -1.000 | +1.000 | -1.000 | -1.000 |
| C_resp | 4 | +0.959 | -0.829 | -0.702 | +0.996 | -0.910 | +0.640 | -0.883 |
| C_e | 16 | +0.555 | +0.528 | +0.601 | +0.902 | +0.901 | +0.557 | +0.886 |
| C_model | 3 | -0.884 | +0.565 | -0.192 | +0.756 | +0.960 | -0.757 | -0.928 |
| C_total | 16 | +0.529 | +0.526 | +0.509 | +0.887 | +0.846 | +0.393 | +0.821 |
| C_total + C_resp + V_g (genie_cv) | — | +0.544 | +0.442 | +0.463 | +0.808 | +0.721 | +0.400 | +0.699 |
| C_total + C_resp + V_g (genie_mec) | — | +0.544 | +0.442 | +0.464 | +0.808 | +0.721 | +0.400 | +0.699 |
| C_total + C_resp + V_g (nuwro) | — | +0.545 | +0.442 | +0.464 | +0.809 | +0.722 | +0.401 | +0.702 |
| C_total + C_resp + V_g (mnvtune_v1) | — | +0.546 | +0.443 | +0.469 | +0.811 | +0.724 | +0.402 | +0.709 |

### 2.4 Item 4: Stage G's reported comparison at each cell

Read from the Stage G readout (`75a9ddee…`). The matrix is C_total + C_resp + V_g. The MC event count is Stage G's
`n_mc_events_in_cells`. GiBUU is compared only on its eight p_∥ < 4.5 cells, so it is not compared on R04, R07 or R14,
and no value is formed there.

#### genie_cv (C_total + C_resp + V_g)

Label: GENIE 2.12.10 CV, no MEC; CH

| cell | g/f − 1 % | pull | sigma_total/f % | sigma_Vg/f % | MC events |
|---|---|---|---|---|---|
| R04 | -8.39 | +1.99 | 4.20 | 0.29 | 164963 |
| R00 | -10.57 | +1.49 | 7.10 | 0.25 | 123175 |
| R01 | -11.24 | +1.58 | 7.10 | 0.33 | 123873 |
| R07 | +2.42 | -0.30 | 7.98 | 1.17 | 11477 |
| R08 | -17.39 | +2.77 | 6.25 | 0.38 | 47861 |
| R09 | -6.38 | +1.02 | 6.26 | 0.33 | 135156 |
| R10 | -7.37 | +0.86 | 8.59 | 0.53 | 30144 |
| R14 | -16.89 | +3.17 | 5.27 | 0.81 | 121550 |

#### genie_mec (C_total + C_resp + V_g)

Label: GENIE 2.12.10 + Valencia MEC; CH

| cell | g/f − 1 % | pull | sigma_total/f % | sigma_Vg/f % | MC events |
|---|---|---|---|---|---|
| R04 | +2.56 | -0.61 | 4.20 | 0.30 | 181633 |
| R00 | -0.86 | +0.12 | 7.10 | 0.27 | 133887 |
| R01 | -11.05 | +1.56 | 7.10 | 0.34 | 121390 |
| R07 | -0.90 | +0.11 | 7.98 | 1.15 | 10949 |
| R08 | -13.84 | +2.21 | 6.25 | 0.39 | 48954 |
| R09 | -6.11 | +0.97 | 6.26 | 0.33 | 132664 |
| R10 | -6.32 | +0.73 | 8.59 | 0.54 | 29883 |
| R14 | -15.51 | +2.91 | 5.27 | 0.83 | 120616 |

#### nuwro (C_total + C_resp + V_g)

Label: NuWro 21.09; C12 target; no correction to CH applied

| cell | g/f − 1 % | pull | sigma_total/f % | sigma_Vg/f % | MC events |
|---|---|---|---|---|---|
| R04 | -9.11 | +2.17 | 4.20 | 0.25 | 230973 |
| R00 | -13.34 | +1.88 | 7.10 | 0.21 | 167786 |
| R01 | -6.31 | +0.89 | 7.10 | 0.28 | 183102 |
| R07 | +12.81 | -1.59 | 7.98 | 1.12 | 17550 |
| R08 | -23.96 | +3.83 | 6.25 | 0.31 | 61990 |
| R09 | -15.55 | +2.48 | 6.26 | 0.27 | 171478 |
| R10 | -19.61 | +2.28 | 8.59 | 0.42 | 36764 |
| R14 | -20.91 | +3.94 | 5.27 | 0.70 | 156894 |

#### gibuu (C_total + C_resp + V_g)

Label: GiBUU 2019; C12 target; no correction to CH applied; no events above E_nu = 20 GeV (KNOWN_ISSUES 82), so it is compared on the eight p_parallel < 4.5 cells only and not shown above p_parallel 4.5 (FD-DIRECTOR-RULINGS.md section 5)

| cell | g/f − 1 % | pull | sigma_total/f % | sigma_Vg/f % | MC events |
|---|---|---|---|---|---|
| R04 | not compared | | | | |
| R00 | -16.34 | +2.26 | 7.10 | 1.32 | 137626 |
| R01 | -28.83 | +4.06 | 7.10 | 0.29 | 95422 |
| R07 | not compared | | | | |
| R08 | -18.59 | +2.80 | 6.25 | 2.23 | 94205 |
| R09 | -15.72 | +2.51 | 6.26 | 0.38 | 82098 |
| R10 | -38.13 | +4.40 | 8.59 | 1.15 | 35704 |
| R14 | not compared | | | | |

#### mnvtune_v1 (C_total + C_resp + V_g)

Label: MINERvA Tune v1, the analysis MC truth: prior (not an independent prediction)

| cell | g/f − 1 % | pull | sigma_total/f % | sigma_Vg/f % | MC events |
|---|---|---|---|---|---|
| R04 | -2.49 | +0.59 | 4.20 | 0.05 | 5772542 |
| R00 | -6.02 | +0.85 | 7.10 | 0.05 | 4060485 |
| R01 | -13.09 | +1.85 | 7.10 | 0.04 | 3798081 |
| R07 | -13.71 | +1.72 | 7.98 | 0.15 | 360147 |
| R08 | -20.26 | +3.24 | 6.25 | 0.07 | 1483408 |
| R09 | -11.63 | +1.86 | 6.26 | 0.04 | 4223666 |
| R10 | -16.70 | +1.94 | 8.59 | 0.09 | 895241 |
| R14 | -19.37 | +3.68 | 5.27 | 0.04 | 4147782 |

### 2.5 Item 5: data or reco event counts, or an efficiency, in the pinned products

**The declared search found no data event count and no efficiency.** It matched the keys tabled below. None of them
is a data event count or an efficiency, and the definition's per-cell matches are simulated.
<!-- absence-ok: scoped to the run's declared search (item 5): the last key of every key path of the 12 pinned products, whole-word, case-insensitive, pattern in the readout, run 2026-10-26T18:38Z at 02bf756a, plus the substring cross-check on the five committed JSON products below -->

**What the search found:**
- **Per-cell counts,** all simulated:
  - the definition's `expected_reco_signal`, `truth_selected` and `mc_neff_truth`, with purity and stability. The
    definition is `simulation_only: true`.
  - Stage G's `n_mc_events_in_cells`.
- **Fine-grid counts:** the predictions' `nevt_flat`, which Stage G sums into `n_mc_events_in_cells`.
- **The other matches** are matched by name and listed in the readout. Their values were not opened or reported:
  - S1's `meta / inputs_sha256 / data_b*_j*.npz`, whose path places them as file names keyed to digests;
  - `meta / flux_weights / n_eff`;
  - G-DIAG's `stability` records;
  - the prediction npz's JSON `meta_json` entries.
- **The pinned s5p manifest** lists one file name, `runs/s2/num/data/data_b-_j-.npz`. It was not opened, so no new data
  tuple was read.
- **The search's limits** (binding §3 item 4):
  - It searches key names only. A field whose name does not say what it is would be missed.
  - The whole-word rule also misses a word inside a compound name, such as `MinosEfficiency`.
  - String values, and the contents of non-string npz members, are not searched.
- **The substring cross-check.** Outside the run, a plain substring re-search of the five committed JSON products'
  key names (`substring_crosscheck.py`, output `substring_crosscheck.txt`) finds three names the whole-word rule
  skipped:
  - `S1_MinosEfficiency_0.npz` and `S1_MinosEfficiency_1.npz`, under S1's `meta.inputs_sha256`: file names keyed to
    digests;
  - `records` in `cmodel_5d.json`.

  It was not run on the seven npz products, which are on the cluster. In the run itself, S1's npz gave the same 21
  whole-word matches as S1's readout.
  <!-- absence-ok: a scoping statement about where this session's cross-check was run, not a claim that a result does not exist -->

| product | keys searched | matches |
|---|---|---|
| definition | 43 | 12 |
| s1_json | 350 | 21 |
| cmodel_json | 118 | 0 |
| g_readout | 85 | 1 |
| g_diag_readout | 216 | 3 |
| s1_npz | 359 | 21 |
| extra_block | 42 | 0 |
| prediction:genie_cv | 166 | 10 |
| prediction:genie_mec | 167 | 10 |
| prediction:nuwro | 173 | 8 |
| prediction:gibuu | 166 | 9 |
| prediction:mnvtune_v1 | 16 | 1 |

The definition's matching per-cell fields (simulation):

| field | R04 | R00 | R01 | R07 | R08 | R09 | R10 | R14 | median of 16 |
|---|---|---|---|---|---|---|---|---|---|
| purity | 0.846 | 0.714 | 0.715 | 0.306 | 0.510 | 0.719 | 0.383 | 0.779 | 0.465 |
| stability | 0.814 | 0.800 | 0.775 | 0.283 | 0.610 | 0.675 | 0.217 | 0.787 | 0.541 |
| expected_reco_signal | 817,895 | 483,627 | 356,726 | 44,059 | 125,051 | 255,508 | 34,118 | 525,459 | 127,898 |
| truth_selected | 1,020,374 | 654,151 | 681,343 | 59,093 | 235,968 | 747,633 | 139,316 | 854,759 | 190,932 |
| mc_neff_truth | 3,930,993 | 2,934,519 | 3,739,551 | 331,614 | 1,388,929 | 4,069,981 | 844,187 | 3,953,897 | 1,009,896 |

## 3. G-SENS

Every record below is a **descriptive sensitivity of the reported χ², not an alternative result.** No p value is
computed.
- **The shrinkage:** each group C_g in the family becomes D^½[(1 − α)ρ + αI]D^½.
- **The families:**
  - `interaction` (primary);
  - `c_e_systematic` (second): interaction, flux, detector and lateral, jointly.
- **Unchanged:** stat, seed, normalization, the three C_model vertices, C_resp and V_g.
- **Columns:**
  - λ_min and σ are relative to f.
  - The top mode carries the largest χ² contribution, and its index is in that matrix's own eigen-order.
  - Leading cells are the three largest |loading|.
- **The predictions' labels:**

| prediction | label (the readout's, verbatim) |
|---|---|
| genie_cv | GENIE 2.12.10 CV, no MEC; CH |
| genie_mec | GENIE 2.12.10 + Valencia MEC; CH |
| nuwro | NuWro 21.09; C12 target; no correction to CH applied |
| gibuu | GiBUU 2019; C12 target; no correction to CH applied; no events above E_nu = 20 GeV (KNOWN_ISSUES 82), so it is compared on the eight p_parallel < 4.5 cells only and not shown above p_parallel 4.5 (FD-DIRECTOR-RULINGS.md section 5) |
| mnvtune_v1 | MINERvA Tune v1, the analysis MC truth: prior (not an independent prediction) |

#### interaction (primary), genie_cv, ndf 16

| α | χ² | condition | λ_min | modes 50/90/99 % | top mode σ % | its fraction % | leading cells |
|---|---|---|---|---|---|---|---|
| 0 | 109.35 | 1.18e+03 | 4.37e-05 | 2/7/13 | 3.15 | 40.6 | R06 +0.77, R05 -0.41, R10 -0.27 |
| 0.1 | 96.25 | 823 | 6.28e-05 | 2/6/12 | 3.23 | 46.8 | R06 +0.76, R05 -0.38, R10 -0.34 |
| 0.25 | 87.15 | 687 | 7.55e-05 | 3/8/13 | 3.41 | 31.9 | R03 +0.51, R06 -0.50, R02 -0.36 |
| 0.5 | 78.97 | 580 | 8.99e-05 | 3/7/12 | 3.46 | 26.7 | R06 +0.53, R05 -0.45, R12 -0.36 |
| 1 | 72.97 | 510 | 0.000103 | 3/8/13 | 3.62 | 35.6 | R06 +0.56, R12 -0.48, R05 -0.43 |

#### interaction (primary), genie_mec, ndf 16

| α | χ² | condition | λ_min | modes 50/90/99 % | top mode σ % | its fraction % | leading cells |
|---|---|---|---|---|---|---|---|
| 0 | 272.12 | 1.15e+03 | 4.47e-05 | 2/4/10 | 1.15 | 45.5 | R04 +0.45, R08 -0.42, R01 -0.37 |
| 0.1 | 245.60 | 814 | 6.35e-05 | 2/4/10 | 1.22 | 36.5 | R08 +0.59, R00 -0.49, R04 -0.32 |
| 0.25 | 222.06 | 680 | 7.62e-05 | 2/4/10 | 1.34 | 36.8 | R08 +0.60, R00 -0.56, R01 +0.28 |
| 0.5 | 195.79 | 575 | 9.07e-05 | 2/5/11 | 0.95 | 34.2 | R04 +0.92, R00 -0.23, R09 -0.23 |
| 1 | 171.20 | 506 | 0.000104 | 2/6/12 | 1.02 | 41.9 | R04 +0.94, R09 -0.18, R08 -0.17 |

#### interaction (primary), nuwro, ndf 16

| α | χ² | condition | λ_min | modes 50/90/99 % | top mode σ % | its fraction % | leading cells |
|---|---|---|---|---|---|---|---|
| 0 | 188.03 | 1.38e+03 | 3.73e-05 | 3/9/13 | 0.61 | 31.3 | R04 +0.63, R10 -0.37, R00 -0.34 |
| 0.1 | 159.94 | 863 | 5.98e-05 | 2/9/13 | 0.77 | 38.1 | R04 +0.86, R00 -0.32, R09 -0.29 |
| 0.25 | 141.30 | 713 | 7.26e-05 | 2/5/10 | 0.85 | 37.7 | R04 +0.90, R00 -0.28, R09 -0.26 |
| 0.5 | 123.29 | 598 | 8.71e-05 | 2/6/11 | 0.93 | 35.5 | R04 +0.92, R00 -0.23, R09 -0.23 |
| 1 | 107.83 | 524 | 0.000101 | 2/8/13 | 1.00 | 31.8 | R04 +0.94, R09 -0.18, R08 -0.17 |

#### interaction (primary), gibuu, ndf 8

| α | χ² | condition | λ_min | modes 50/90/99 % | top mode σ % | its fraction % | leading cells |
|---|---|---|---|---|---|---|---|
| 0 | 58.46 | 142 | 0.0003 | 2/5/6 | 13.54 | 26.8 | R11 +0.79, R10 +0.36, R00 +0.30 |
| 0.1 | 57.59 | 120 | 0.000357 | 2/4/6 | 13.50 | 27.8 | R11 +0.79, R10 +0.35, R00 +0.30 |
| 0.25 | 56.63 | 108 | 0.000398 | 2/4/6 | 13.46 | 28.9 | R11 +0.78, R10 +0.34, R00 +0.31 |
| 0.5 | 55.46 | 99.6 | 0.000436 | 2/4/6 | 13.39 | 30.6 | R11 +0.77, R00 +0.32, R10 +0.32 |
| 1 | 54.34 | 92.3 | 0.000479 | 2/4/7 | 13.31 | 32.6 | R11 +0.75, R00 +0.34, R08 +0.32 |

#### interaction (primary), mnvtune_v1, ndf 16

| α | χ² | condition | λ_min | modes 50/90/99 % | top mode σ % | its fraction % | leading cells |
|---|---|---|---|---|---|---|---|
| 0 | 329.72 | 2.64e+03 | 1.95e-05 | 2/5/9 | 0.97 | 47.9 | R04 +0.54, R14 -0.41, R08 -0.38 |
| 0.1 | 299.42 | 980 | 5.27e-05 | 2/4/9 | 1.12 | 45.5 | R08 +0.56, R00 -0.46, R04 -0.33 |
| 0.25 | 266.01 | 783 | 6.61e-05 | 2/4/10 | 1.27 | 42.0 | R08 +0.59, R00 -0.54, R12 -0.30 |
| 0.5 | 226.91 | 645 | 8.07e-05 | 2/5/10 | 0.90 | 37.7 | R04 +0.92, R00 -0.23, R09 -0.22 |
| 1 | 183.85 | 562 | 9.38e-05 | 2/6/9 | 0.97 | 42.7 | R04 +0.94, R09 -0.18, R08 -0.17 |

#### c_e_systematic (second), genie_cv, ndf 16

| α | χ² | condition | λ_min | modes 50/90/99 % | top mode σ % | its fraction % | leading cells |
|---|---|---|---|---|---|---|---|
| 0 | 109.35 | 1.18e+03 | 4.37e-05 | 2/7/13 | 3.15 | 40.6 | R06 +0.77, R05 -0.41, R10 -0.27 |
| 0.1 | 70.68 | 230 | 0.000222 | 1/6/12 | 3.50 | 55.5 | R06 +0.70, R10 -0.39, R05 -0.36 |
| 0.25 | 55.78 | 112 | 0.000451 | 3/7/12 | 3.98 | 25.5 | R05 +0.57, R06 -0.45, R01 -0.43 |
| 0.5 | 45.84 | 60.3 | 0.000825 | 3/8/13 | 3.74 | 21.4 | R14 +0.77, R09 -0.45, R12 -0.28 |
| 1 | 45.47 | 31.6 | 0.00155 | 2/6/11 | 4.80 | 29.3 | R14 +0.85, R06 -0.46, R05 -0.17 |

#### c_e_systematic (second), genie_mec, ndf 16

| α | χ² | condition | λ_min | modes 50/90/99 % | top mode σ % | its fraction % | leading cells |
|---|---|---|---|---|---|---|---|
| 0 | 272.12 | 1.15e+03 | 4.47e-05 | 2/4/10 | 1.15 | 45.5 | R04 +0.45, R08 -0.42, R01 -0.37 |
| 0.1 | 133.31 | 229 | 0.000223 | 2/4/13 | 3.51 | 39.1 | R06 +0.70, R10 -0.39, R05 -0.38 |
| 0.25 | 87.57 | 112 | 0.000452 | 3/6/12 | 2.13 | 25.3 | R04 +0.94, R08 -0.23, R09 -0.22 |
| 0.5 | 61.09 | 60.2 | 0.000825 | 3/8/13 | 4.07 | 23.0 | R06 +0.71, R05 -0.32, R15 -0.31 |
| 1 | 45.33 | 31.6 | 0.00155 | 2/8/14 | 4.81 | 30.4 | R14 +0.85, R06 -0.46, R05 -0.17 |

#### c_e_systematic (second), nuwro, ndf 16

| α | χ² | condition | λ_min | modes 50/90/99 % | top mode σ % | its fraction % | leading cells |
|---|---|---|---|---|---|---|---|
| 0 | 188.03 | 1.38e+03 | 3.73e-05 | 3/9/13 | 0.61 | 31.3 | R04 +0.63, R10 -0.37, R00 -0.34 |
| 0.1 | 90.41 | 233 | 0.000219 | 3/9/12 | 6.73 | 22.1 | R08 +0.57, R00 +0.42, R07 -0.39 |
| 0.25 | 66.48 | 113 | 0.000448 | 2/7/11 | 6.91 | 29.6 | R08 +0.54, R00 +0.44, R07 -0.39 |
| 0.5 | 55.61 | 60.5 | 0.000822 | 3/9/14 | 7.18 | 33.8 | R00 +0.49, R08 +0.47, R03 -0.38 |
| 1 | 69.24 | 31.7 | 0.00155 | 3/8/12 | 7.03 | 25.2 | R07 +0.56, R01 -0.52, R00 -0.44 |

#### c_e_systematic (second), gibuu, ndf 8

| α | χ² | condition | λ_min | modes 50/90/99 % | top mode σ % | its fraction % | leading cells |
|---|---|---|---|---|---|---|---|
| 0 | 58.46 | 142 | 0.0003 | 2/5/6 | 13.54 | 26.8 | R11 +0.79, R10 +0.36, R00 +0.30 |
| 0.1 | 50.51 | 62.7 | 0.000671 | 2/4/6 | 13.28 | 34.0 | R11 +0.79, R10 +0.37, R00 +0.30 |
| 0.25 | 48.89 | 35.1 | 0.00118 | 2/4/7 | 12.86 | 39.8 | R11 +0.79, R10 +0.37, R00 +0.30 |
| 0.5 | 53.32 | 21 | 0.00194 | 2/4/7 | 12.13 | 42.5 | R11 +0.79, R10 +0.38, R00 +0.29 |
| 1 | 89.88 | 13.4 | 0.00297 | 3/6/7 | 7.06 | 27.1 | R10 +0.71, R01 +0.65, R09 +0.16 |

#### c_e_systematic (second), mnvtune_v1, ndf 16

| α | χ² | condition | λ_min | modes 50/90/99 % | top mode σ % | its fraction % | leading cells |
|---|---|---|---|---|---|---|---|
| 0 | 329.72 | 2.64e+03 | 1.95e-05 | 2/5/9 | 0.97 | 47.9 | R04 +0.54, R14 -0.41, R08 -0.38 |
| 0.1 | 146.34 | 240 | 0.000212 | 2/4/10 | 1.46 | 35.3 | R04 +0.93, R09 -0.26, R08 -0.19 |
| 0.25 | 93.46 | 114 | 0.000442 | 3/7/11 | 2.10 | 29.4 | R04 +0.94, R08 -0.23, R09 -0.22 |
| 0.5 | 66.64 | 60.9 | 0.000815 | 3/7/10 | 3.97 | 24.4 | R06 +0.73, R05 -0.35, R15 -0.33 |
| 1 | 67.59 | 31.8 | 0.00154 | 4/10/13 | 4.73 | 20.0 | R14 +0.84, R06 -0.50, R05 -0.18 |

**Across all 50 records:**
- **No record is flagged unstable.** The largest relative difference of the mode-sum or least-squares χ² from Cholesky
  is 1.7 × 10⁻¹⁴, and the largest ridge change is 9.0 × 10⁻⁹.
- **The shrunk groups' smallest eigenvalues,** relative to f, are non-positive only at α = 0 in `c_e_systematic`, which
  is the unshrunk group:
  - detector, −2.6 × 10⁻¹⁹ (GiBUU −3.5 × 10⁻¹⁹);
  - lateral, −1.3 × 10⁻¹⁸ (GiBUU −7.4 × 10⁻¹⁹).

  Item 3 gives these blocks ranks 4 and 5 over the 16 cells. All other values are positive.

## 4. Records

- **The readout:** `fd/readout/fd_g_followup_readout.json`, `cd82517a…`.
- **The readout's pointers:** `fd/readout/fd_g_followup_readout/` holds 20 relative symlinks to S1's tracked `data_b*_j*.npz`, with a README. This is the director's ruling (a): item 5's matches name those files by key path, and the links let `verify_receipt_artifacts.py` resolve them through its own companion-directory rule, without widening the gate or duplicating data.
- **The receipts,** under `fd/receipts-g-followup/`:
  - `f1.sh`, `f1-launch.txt`, `f1-stdout.txt`, `deploy.log`, `deploy-tests.log`;
  - `f2.sh`, `f2-stdout.txt`, `followup-start.txt`, `followup.out`, `followup.err`;
  - `post-run.txt`;
  - `summarize_g_followup.py` and its output `summary.txt`, from which every table above is copied;
  - `substring_crosscheck.py` and `substring_crosscheck.txt`, and `cluster-sha256.txt`;
  - `SHA256SUMS`.

  The declaration's own receipts are under `declaration/`.
- **The ledger:** two rows in `fd/LEDGER.tsv`.
- **Storage:** `$B` (576 MB) is kept on pscratch (binding §3 item 6). No tracked retention-list file exists, so the
  retention is recorded here. Nothing went to HPSS or CFS.
- **The results index:** unchanged. `results_index.py --population` classes the readout `excluded-no-metric`, so
  nothing is regenerated.

## Not changed

- Stage G's and G-DIAG's readouts and reports, S1's covariance, C_model,5D, C_resp, R00–R15, κ = 1 and the route
  decision.
- No GPU and no premium QOS.
- The reading of these numbers, claims, printed wording and publication are Joseph's.
