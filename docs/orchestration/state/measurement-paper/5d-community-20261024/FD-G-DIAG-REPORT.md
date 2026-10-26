# REPORT G-DIAG: a descriptive breakdown of Stage G's χ² (2026-10-26)

**By** the measurement session.

**Under** [`FD-G-DIAG-BINDING.md`](FD-G-DIAG-BINDING.md) (PR #381, main `efb81d29`).
- It binds [`FD-G-DIAG-DECLARATION.md`](FD-G-DIAG-DECLARATION.md) with its amendment 1, at deploy pin `d02ce2f2`.
- The report follows the binding's §3 item 4 and the director's rulings 1, 2 and 7.

**MEASURES:** for each of Stage G's five comparisons, under the reported matrix C_total + C_resp + V_g and the variant
C_total + V_g:
- the eigenmode breakdown of Stage G's total χ²;
- the block shares of its three largest modes;
- the χ² with each block removed in turn;
- float64 stability.

**CANNOT AUTHORIZE:**
- an alternative to Stage G's reported χ²;
- any reading of these numbers, a claim or printed wording, which are Joseph's;
- splitting S1's groups or C_resp's species, which is the director's follow-up to decide.

**CITABLE FOR:** the numbers below, as `fd/readout/fd_g_diag_readout.json` holds them.

**NOT CITABLE FOR:**
- an interpretation;
- the removal χ² as results: they are a breakdown;
- a ridge-sensitive χ² as an artefact (ruling 7). None is flagged here.

**Outcome:**
- **Both steps exited 0** on login37 at 0 node-h, with no Slurm job.
  - **The deploy:** "Ran 90 tests … OK".
  - **The breakdown:** it took about 1 s, and controls D0–D7 passed (22 lines).
- **Stage G was reproduced.** D5 matched it exactly, with the worst relative difference 0.0. D7 found every
  breakdown's own χ² equal to Stage G's committed total, to 1.3 × 10⁻¹⁴ at worst.
- **The blocks rebuild M** to 3.7 × 10⁻¹⁶ (D6).
- **No comparison, in either unit, is flagged.**
  - `methods_disagree`, the numerical-artefact signal: largest spread 4.2 × 10⁻¹⁴, against a threshold of 10⁻⁸.
  - `ridge_sensitive`, conditioning sensitivity: largest ridge change 1.0 × 10⁻⁸, against 10⁻³.
- **No block removal** leaves a matrix that is not positive definite or is ill-conditioned (230 removal records in
  both units).
- **The readout** is `680dc5ef9c40b1ab006657ce020c6acac7e891c68ce36850cf7a7dd2df278d88`, schema
  `fd-g-diag-readout/1`, with no non-finite values.

## 1. The steps

| step | host | start (UTC) | end | rc | wall | result |
|---|---|---|---|---:|---:|---|
| §2.1 deploy and tests | login37 | 12:29:20 | 12:30:36 | 0 | 76 s | `$B=/pscratch/sd/j/josephrb/fd-g-diag-20261026` absent before; HEAD `d02ce2f2…`; porcelain 0 before and after; every §8 digest matches (`fd_g_diag.py` `7c161280…`, tests `870564f5…`, `fd_g_compare.py` `0a3c09cd…`, the Stage G readout `75a9ddee…`), and the declaration's is `8cf8f160…`, the binding's; `tests rc=0`, "Ran 90 tests in 38.105s", OK |
| §2.2 the breakdown | login37 | 12:30:42 | 12:30:43 | 0 | 1 s | D0–D7 PASS (22 lines); readout written; `diag.err` empty |

All on 2026-10-26.

- **The start time:** the deploy start, 12:29:20, is the local stamp when the script was sent (`d1-launch.txt`).
  `deploy.log`'s first stamp, 12:29:54, follows the clone.
- **The scripts:** `d1.sh` is §2.1 verbatim, with a guard that refuses if `$B` exists. `d2.sh` is §2.2 verbatim, with
  guards that refuse unless the deploy shows `tests rc=0` and if the readout exists, plus start and end stamps.
  Neither names a CFS path.
- **`$B` after the run:** the deploy clone, `logs/`, `tmp/` and the readout, 569 MB in all (`post-run.txt`).

**The control lines for D5, D6 and D7** (`diag.out`):
- D5: the Stage G readout used this extra block, key, name and role.
- D5: Stage G's total and shape-only χ² and pulls reproduce to 10⁻¹⁰ relative (worst 0.0e+00).
- D6: the blocks rebuild every comparison's M to 10⁻¹² relative in both units (worst 3.7e-16).
- D7: every stable breakdown's χ² is Stage G's committed total χ² to 10⁻¹⁰ (worst 1.3e-14).

**S1's groups** (`blocks.s1_blocks_per_group`): stat 1 block, interaction 33, flux 1, detector 4, lateral 5,
normalization 1, seed 1.

## 2. Overview, relative to f (ruling 1)

**The columns:**
- **χ²:** Stage G's total χ².
- **total − shape-only:** Stage G's total χ² less its shape-only χ², the normalization's share (ruling 2).
- **cond:** M's condition number.
- **modes 50/90/99 %:** the fewest modes, in χ² order, carrying that fraction of the χ².
- **top mode:** its share of the χ², its relative σ √λ, and the block with the largest share vᵀBv/λ.
- **The two flags:** `ridge_sensitive` is conditioning sensitivity, and `methods_disagree` is the numerical-artefact
  signal (ruling 7).

| prediction | comparison | matrix | chi2/ndf | total - shape-only | cond | rank | modes 50/90/99 % | top mode: % of chi2, sigma, dominant | ridge_sensitive | methods_disagree |
|---|---|---|---|---:|---:|---:|---|---|---|---|
| genie_cv | reported | C_total + C_resp + V_g | 109.35/16 | 0.85 | 1.18e+03 | 16 | 2/7/13 | 40.6 %, 3.15 %, interaction | False | False |
| genie_cv | variant | C_total + V_g | 160.62/16 | 1.92 | 1.27e+03 | 16 | 3/7/11 | 23.9 %, 1.15 %, interaction | False | False |
| genie_mec | reported | C_total + C_resp + V_g | 272.12/16 | 14.05 | 1.15e+03 | 16 | 2/4/10 | 45.5 %, 1.15 %, interaction | False | False |
| genie_mec | variant | C_total + V_g | 318.26/16 | 13.00 | 1.24e+03 | 16 | 2/5/10 | 33.3 %, 1.12 %, interaction | False | False |
| nuwro | reported | C_total + C_resp + V_g | 188.03/16 | 0.03 | 1.38e+03 | 16 | 3/9/13 | 31.3 %, 0.61 %, V_g | False | False |
| nuwro | variant | C_total + V_g | 298.69/16 | 0.05 | 1.47e+03 | 16 | 2/6/11 | 34.3 %, 0.59 %, V_g | False | False |
| gibuu | reported | C_total + C_resp + V_g | 58.46/8 | 30.77 | 142 | 8 | 2/5/6 | 26.8 %, 13.54 %, flux | False | False |
| gibuu | variant | C_total + V_g | 68.44/8 | 32.29 | 166 | 8 | 2/5/6 | 29.1 %, 12.95 %, flux | False | False |
| mnvtune_v1 | reported | C_total + C_resp + V_g | 329.72/16 | 18.53 | 2.64e+03 | 16 | 2/5/9 | 47.9 %, 0.97 %, interaction | False | False |
| mnvtune_v1 | variant | C_total + V_g | 360.79/16 | 19.50 | 3.17e+03 | 16 | 2/5/7 | 46.4 %, 1.15 %, interaction | False | False |

## 3. Stability (ruling 7)

Each cell is relative to f / absolute.
- `methods_disagree` uses the mode sum against Cholesky and least squares against Cholesky. Its threshold is 10⁻⁸.
- `ridge_sensitive` uses the ridge change. Its threshold is 10⁻³.
- `unstable` is either flag, or a Cholesky failure.

| prediction | comparison | rel ridge change | rel mode-sum vs Cholesky | rel lstsq vs Cholesky | unstable |
|---|---|---|---|---|---|
| genie_cv | reported | 2.6e-09 / 7.4e-09 | 1.2e-14 / 4.2e-14 | 1.7e-15 / 0.0e+00 | False / False |
| genie_cv | variant | 3.3e-09 / 1.0e-08 | 8.1e-15 / 1.4e-14 | 3.5e-15 / 2.5e-15 | False / False |
| genie_mec | reported | 6.2e-09 / 6.1e-09 | 7.5e-15 / 2.0e-14 | 1.5e-15 / 4.8e-15 | False / False |
| genie_mec | variant | 4.8e-09 / 7.6e-09 | 1.1e-14 / 4.6e-15 | 1.8e-16 / 1.8e-15 | False / False |
| nuwro | reported | 9.0e-09 / 8.3e-09 | 2.9e-15 / 5.4e-15 | 1.1e-15 / 4.5e-15 | False / False |
| nuwro | variant | 8.9e-09 / 7.9e-09 | 1.8e-14 / 1.9e-14 | 2.1e-15 / 5.7e-16 | False / False |
| gibuu | reported | 8.7e-10 / 8.8e-10 | 2.9e-15 / 7.7e-15 | 1.7e-15 / 2.4e-16 | False / False |
| gibuu | variant | 1.1e-09 / 8.1e-10 | 5.0e-15 / 2.9e-15 | 4.2e-16 / 2.1e-16 | False / False |
| mnvtune_v1 | reported | 8.0e-09 / 5.7e-09 | 1.7e-14 / 5.5e-15 | 3.4e-15 / 1.2e-15 | False / False |
| mnvtune_v1 | variant | 6.5e-09 / 7.5e-09 | 1.3e-14 / 7.9e-15 | 1.9e-15 / 2.8e-15 | False / False |

## 4. Per prediction: the top three modes, the removals, and the absolute decomposition

**In each table:**
- **% of χ²** and **σ (rel)** are the mode's share of the χ² and √λ, relative to f.
- **The share columns** are vᵀBv/λ for each block. They sum to 1.
  - **The C_e groups:** stat, int (interaction), flux, det (detector), lat (lateral), norm (normalization), seed.
  - **The C_model,5D vertices:** vMEC, vNuWro, vGiBUU.
  - **C_resp**, in the reported comparison only.
  - **V_g**, the prediction's finite MC.
- **Mode numbers** index the eigenvalues in descending order. Mode 0 has the largest λ.
- **Loadings** are signed so that the largest-|loading| cell is positive. Only the pattern is meaningful.

### 4.1 GENIE CV

#### reported: C_total + C_resp + V_g

| mode | % of chi2 | sigma (rel) | dominant | stat | int | flux | det | lat | norm | seed | vMEC | vNuWro | vGiBUU | C_resp | V_g |
|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 7 | 40.6 | 3.15 % | interaction | 0.014 | 0.377 | 0.079 | 0.004 | 0.025 | 0.001 | 0.000 | 0.306 | 0.000 | 0.016 | 0.090 | 0.088 |
| 13 | 19.1 | 1.14 % | interaction | 0.025 | 0.394 | 0.147 | 0.143 | 0.017 | 0.008 | 0.000 | 0.008 | 0.001 | 0.000 | 0.011 | 0.246 |
| 12 | 11.5 | 1.21 % | interaction | 0.033 | 0.379 | 0.132 | 0.117 | 0.081 | 0.001 | 0.000 | 0.002 | 0.004 | 0.002 | 0.021 | 0.229 |

**Loadings** (cells with |v| ≥ 0.25):

- mode 7: R05 -0.41, R06 +0.77, R10 -0.27
- mode 13: R00 +0.32, R01 -0.36, R04 +0.45, R07 -0.29, R08 -0.42, R09 +0.30, R14 -0.33
- mode 12: R00 -0.33, R02 +0.35, R09 +0.53, R15 -0.53

**Each block removed in turn** (descriptive breakdown, not an alternative result; χ², ndf and the condition number of M − B; no p-value):

| removed | chi2/ndf | condition | positive definite | ill-conditioned |
|---|---:|---:|---|---|
| stat | 111.08/16 | 1.22e+03 | True | False |
| interaction | 260.58/16 | 2.17e+03 | True | False |
| flux | 133.91/16 | 1.36e+03 | True | False |
| detector | 134.39/16 | 1.61e+03 | True | False |
| lateral | 157.20/16 | 1.17e+03 | True | False |
| normalization | 109.49/16 | 1.18e+03 | True | False |
| seed | 109.35/16 | 1.18e+03 | True | False |
| C_model:genie_mec | 123.40/16 | 1.51e+03 | True | False |
| C_model:nuwro | 109.78/16 | 1.21e+03 | True | False |
| C_model:gibuu | 109.40/16 | 798 | True | False |
| C_resp | 160.62/16 | 1.27e+03 | True | False |
| V_g | 121.57/16 | 2.74e+03 | True | False |

**The same χ² decomposed in absolute units (different modes):** chi2 109.35; modes 50/90/99 % 2/8/12; cond 5.16e+03; top modes: mode 12 29.0 % dominant interaction (0.38); mode 11 28.6 % dominant interaction (0.45); mode 5 11.4 % dominant interaction (0.42)

#### variant: C_total + V_g

| mode | % of chi2 | sigma (rel) | dominant | stat | int | flux | det | lat | norm | seed | vMEC | vNuWro | vGiBUU | V_g |
|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 12 | 23.9 | 1.15 % | interaction | 0.030 | 0.491 | 0.173 | 0.006 | 0.075 | 0.001 | 0.000 | 0.007 | 0.005 | 0.001 | 0.211 |
| 6 | 23.7 | 3.08 % | interaction | 0.012 | 0.366 | 0.072 | 0.073 | 0.340 | 0.000 | 0.000 | 0.021 | 0.023 | 0.001 | 0.091 |
| 7 | 18.6 | 3.00 % | C_model:genie_mec | 0.016 | 0.278 | 0.127 | 0.010 | 0.148 | 0.002 | 0.000 | 0.302 | 0.013 | 0.009 | 0.096 |

**Loadings** (cells with |v| ≥ 0.25):

- mode 12: R01 -0.34, R04 +0.34, R08 -0.29, R09 +0.60, R15 -0.40
- mode 6: R01 -0.28, R03 -0.31, R05 +0.41, R06 +0.62, R07 +0.37
- mode 7: R01 +0.37, R05 -0.55, R06 +0.60

**Each block removed in turn** (descriptive breakdown, not an alternative result; χ², ndf and the condition number of M − B; no p-value):

| removed | chi2/ndf | condition | positive definite | ill-conditioned |
|---|---:|---:|---|---|
| stat | 164.27/16 | 1.34e+03 | True | False |
| interaction | 588.02/16 | 2.2e+03 | True | False |
| flux | 198.73/16 | 1.6e+03 | True | False |
| detector | 183.36/16 | 1.72e+03 | True | False |
| lateral | 215.52/16 | 1.19e+03 | True | False |
| normalization | 160.93/16 | 1.27e+03 | True | False |
| seed | 160.62/16 | 1.27e+03 | True | False |
| C_model:genie_mec | 169.85/16 | 1.59e+03 | True | False |
| C_model:nuwro | 163.83/16 | 1.28e+03 | True | False |
| C_model:gibuu | 163.46/16 | 806 | True | False |
| V_g | 187.38/16 | 3.31e+03 | True | False |

**The same χ² decomposed in absolute units (different modes):** chi2 160.62; modes 50/90/99 % 2/8/13; cond 5.27e+03; top modes: mode 12 35.6 % dominant interaction (0.45); mode 11 15.3 % dominant interaction (0.45); mode 9 9.4 % dominant C_model:genie_mec (0.28)

### 4.2 GENIE+MEC

#### reported: C_total + C_resp + V_g

| mode | % of chi2 | sigma (rel) | dominant | stat | int | flux | det | lat | norm | seed | vMEC | vNuWro | vGiBUU | C_resp | V_g |
|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 13 | 45.5 | 1.15 % | interaction | 0.025 | 0.412 | 0.146 | 0.126 | 0.018 | 0.007 | 0.000 | 0.007 | 0.001 | 0.000 | 0.012 | 0.245 |
| 7 | 22.3 | 3.17 % | interaction | 0.014 | 0.373 | 0.079 | 0.004 | 0.026 | 0.001 | 0.000 | 0.303 | 0.000 | 0.016 | 0.088 | 0.096 |
| 15 | 15.6 | 0.67 % | V_g | 0.035 | 0.284 | 0.068 | 0.087 | 0.021 | 0.005 | 0.000 | 0.061 | 0.004 | 0.001 | 0.026 | 0.408 |

**Loadings** (cells with |v| ≥ 0.25):

- mode 13: R00 +0.30, R01 -0.37, R04 +0.45, R07 -0.30, R08 -0.42, R09 +0.33, R14 -0.32
- mode 7: R05 -0.42, R06 +0.77, R10 -0.27
- mode 15: R00 -0.35, R04 +0.72, R09 -0.27, R10 -0.27

**Each block removed in turn** (descriptive breakdown, not an alternative result; χ², ndf and the condition number of M − B; no p-value):

| removed | chi2/ndf | condition | positive definite | ill-conditioned |
|---|---:|---:|---|---|
| stat | 279.13/16 | 1.2e+03 | True | False |
| interaction | 599.02/16 | 2.09e+03 | True | False |
| flux | 325.02/16 | 1.33e+03 | True | False |
| detector | 444.45/16 | 1.57e+03 | True | False |
| lateral | 350.79/16 | 1.14e+03 | True | False |
| normalization | 274.38/16 | 1.15e+03 | True | False |
| seed | 272.12/16 | 1.15e+03 | True | False |
| C_model:genie_mec | 308.57/16 | 1.48e+03 | True | False |
| C_model:nuwro | 273.84/16 | 1.18e+03 | True | False |
| C_model:gibuu | 272.41/16 | 780 | True | False |
| C_resp | 318.26/16 | 1.24e+03 | True | False |
| V_g | 314.29/16 | 2.74e+03 | True | False |

**The same χ² decomposed in absolute units (different modes):** chi2 272.12; modes 50/90/99 % 2/7/13; cond 5.15e+03; top modes: mode 12 29.3 % dominant interaction (0.38); mode 11 25.7 % dominant interaction (0.45); mode 9 17.6 % dominant detector (0.31)

#### variant: C_total + V_g

| mode | % of chi2 | sigma (rel) | dominant | stat | int | flux | det | lat | norm | seed | vMEC | vNuWro | vGiBUU | V_g |
|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 13 | 33.3 | 1.12 % | interaction | 0.030 | 0.298 | 0.162 | 0.258 | 0.014 | 0.008 | 0.000 | 0.001 | 0.002 | 0.000 | 0.228 |
| 12 | 19.7 | 1.15 % | interaction | 0.030 | 0.484 | 0.175 | 0.006 | 0.075 | 0.001 | 0.000 | 0.007 | 0.006 | 0.001 | 0.215 |
| 11 | 16.8 | 1.42 % | interaction | 0.019 | 0.434 | 0.057 | 0.015 | 0.037 | 0.000 | 0.000 | 0.019 | 0.007 | 0.000 | 0.412 |

**Loadings** (cells with |v| ≥ 0.25):

- mode 13: R00 +0.54, R04 +0.37, R08 -0.32, R14 -0.38, R15 +0.33
- mode 12: R01 -0.33, R04 +0.33, R08 -0.28, R09 +0.60, R15 -0.41
- mode 11: R00 -0.29, R02 -0.36, R03 +0.46, R05 +0.52, R07 -0.35, R14 -0.29

**Each block removed in turn** (descriptive breakdown, not an alternative result; χ², ndf and the condition number of M − B; no p-value):

| removed | chi2/ndf | condition | positive definite | ill-conditioned |
|---|---:|---:|---|---|
| stat | 326.30/16 | 1.3e+03 | True | False |
| interaction | 815.99/16 | 2.12e+03 | True | False |
| flux | 376.09/16 | 1.56e+03 | True | False |
| detector | 491.05/16 | 1.68e+03 | True | False |
| lateral | 374.20/16 | 1.16e+03 | True | False |
| normalization | 320.36/16 | 1.24e+03 | True | False |
| seed | 318.26/16 | 1.24e+03 | True | False |
| C_model:genie_mec | 373.21/16 | 1.55e+03 | True | False |
| C_model:nuwro | 327.69/16 | 1.25e+03 | True | False |
| C_model:gibuu | 324.89/16 | 786 | True | False |
| V_g | 376.44/16 | 3.31e+03 | True | False |

**The same χ² decomposed in absolute units (different modes):** chi2 318.26; modes 50/90/99 % 2/7/12; cond 5.24e+03; top modes: mode 12 43.8 % dominant interaction (0.44); mode 9 15.8 % dominant interaction (0.28); mode 11 10.5 % dominant interaction (0.45)

### 4.3 NuWro

#### reported: C_total + C_resp + V_g

| mode | % of chi2 | sigma (rel) | dominant | stat | int | flux | det | lat | norm | seed | vMEC | vNuWro | vGiBUU | C_resp | V_g |
|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 15 | 31.3 | 0.61 % | V_g | 0.032 | 0.335 | 0.046 | 0.064 | 0.029 | 0.002 | 0.000 | 0.068 | 0.004 | 0.000 | 0.018 | 0.401 |
| 10 | 11.5 | 1.98 % | interaction | 0.008 | 0.313 | 0.029 | 0.285 | 0.052 | 0.001 | 0.000 | 0.201 | 0.013 | 0.000 | 0.001 | 0.097 |
| 5 | 10.7 | 6.60 % | C_resp | 0.002 | 0.333 | 0.008 | 0.029 | 0.031 | 0.001 | 0.000 | 0.006 | 0.036 | 0.006 | 0.538 | 0.009 |

**Loadings** (cells with |v| ≥ 0.25):

- mode 15: R00 -0.34, R04 +0.63, R10 -0.37, R12 -0.26
- mode 10: R01 -0.33, R02 -0.27, R07 -0.28, R12 -0.45, R14 +0.57
- mode 5: R00 +0.40, R07 -0.38, R08 +0.58, R12 +0.30

**Each block removed in turn** (descriptive breakdown, not an alternative result; χ², ndf and the condition number of M − B; no p-value):

| removed | chi2/ndf | condition | positive definite | ill-conditioned |
|---|---:|---:|---|---|
| stat | 196.08/16 | 1.43e+03 | True | False |
| interaction | 424.15/16 | 2.66e+03 | True | False |
| flux | 196.82/16 | 1.51e+03 | True | False |
| detector | 418.56/16 | 1.82e+03 | True | False |
| lateral | 284.05/16 | 1.42e+03 | True | False |
| normalization | 188.03/16 | 1.38e+03 | True | False |
| seed | 188.03/16 | 1.38e+03 | True | False |
| C_model:genie_mec | 189.75/16 | 1.83e+03 | True | False |
| C_model:nuwro | 193.33/16 | 1.42e+03 | True | False |
| C_model:gibuu | 197.16/16 | 929 | True | False |
| C_resp | 298.69/16 | 1.47e+03 | True | False |
| V_g | 247.21/16 | 2.74e+03 | True | False |

**The same χ² decomposed in absolute units (different modes):** chi2 188.03; modes 50/90/99 % 1/7/13; cond 6.06e+03; top modes: mode 9 67.4 % dominant detector (0.33); mode 15 5.1 % dominant V_g (0.52); mode 0 5.1 % dominant flux (0.65)

#### variant: C_total + V_g

| mode | % of chi2 | sigma (rel) | dominant | stat | int | flux | det | lat | norm | seed | vMEC | vNuWro | vGiBUU | V_g |
|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 15 | 34.3 | 0.59 % | V_g | 0.039 | 0.356 | 0.059 | 0.045 | 0.026 | 0.002 | 0.000 | 0.051 | 0.002 | 0.000 | 0.420 |
| 9 | 17.9 | 2.01 % | interaction | 0.013 | 0.326 | 0.029 | 0.108 | 0.108 | 0.000 | 0.000 | 0.323 | 0.018 | 0.000 | 0.076 |
| 11 | 17.7 | 1.40 % | interaction | 0.019 | 0.439 | 0.060 | 0.015 | 0.036 | 0.000 | 0.000 | 0.027 | 0.010 | 0.000 | 0.393 |

**Loadings** (cells with |v| ≥ 0.25):

- mode 15: R00 -0.40, R04 +0.62, R10 -0.35, R12 -0.29
- mode 9: R01 -0.47, R07 -0.29, R08 +0.48, R12 -0.30, R14 +0.33
- mode 11: R00 -0.32, R02 -0.35, R03 +0.47, R05 +0.51, R07 -0.36, R14 -0.28

**Each block removed in turn** (descriptive breakdown, not an alternative result; χ², ndf and the condition number of M − B; no p-value):

| removed | chi2/ndf | condition | positive definite | ill-conditioned |
|---|---:|---:|---|---|
| stat | 314.70/16 | 1.54e+03 | True | False |
| interaction | 786.26/16 | 2.78e+03 | True | False |
| flux | 326.09/16 | 1.77e+03 | True | False |
| detector | 499.04/16 | 1.92e+03 | True | False |
| lateral | 558.74/16 | 1.43e+03 | True | False |
| normalization | 298.70/16 | 1.47e+03 | True | False |
| seed | 298.69/16 | 1.47e+03 | True | False |
| C_model:genie_mec | 321.48/16 | 1.9e+03 | True | False |
| C_model:nuwro | 298.72/16 | 1.49e+03 | True | False |
| C_model:gibuu | 300.97/16 | 933 | True | False |
| V_g | 455.18/16 | 3.31e+03 | True | False |

**The same χ² decomposed in absolute units (different modes):** chi2 298.69; modes 50/90/99 % 2/5/12; cond 6.4e+03; top modes: mode 9 31.5 % dominant interaction (0.28); mode 12 28.3 % dominant interaction (0.46); mode 10 25.2 % dominant interaction (0.38)

### 4.4 GiBUU

#### reported: C_total + C_resp + V_g

| mode | % of chi2 | sigma (rel) | dominant | stat | int | flux | det | lat | norm | seed | vMEC | vNuWro | vGiBUU | C_resp | V_g |
|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 26.8 | 13.54 % | flux | 0.001 | 0.171 | 0.334 | 0.131 | 0.007 | 0.054 | 0.000 | 0.002 | 0.075 | 0.120 | 0.099 | 0.007 |
| 5 | 24.7 | 4.83 % | C_resp | 0.002 | 0.111 | 0.088 | 0.062 | 0.190 | 0.013 | 0.000 | 0.005 | 0.016 | 0.025 | 0.429 | 0.059 |
| 0 | 19.1 | 20.63 % | C_model:gibuu | 0.000 | 0.010 | 0.062 | 0.012 | 0.169 | 0.009 | 0.000 | 0.001 | 0.000 | 0.717 | 0.019 | 0.001 |

**Loadings** (cells with |v| ≥ 0.25):

- mode 1: R00 +0.30, R08 +0.26, R10 +0.36, R11 +0.79
- mode 5: R00 -0.54, R03 +0.29, R08 -0.37, R09 +0.63, R10 +0.25
- mode 0: R02 +0.65, R03 +0.56, R11 -0.39

**Each block removed in turn** (descriptive breakdown, not an alternative result; χ², ndf and the condition number of M − B; no p-value):

| removed | chi2/ndf | condition | positive definite | ill-conditioned |
|---|---:|---:|---|---|
| stat | 58.71/8 | 144 | True | False |
| interaction | 73.55/8 | 307 | True | False |
| flux | 103.19/8 | 156 | True | False |
| detector | 75.26/8 | 143 | True | False |
| lateral | 67.62/8 | 214 | True | False |
| normalization | 61.88/8 | 141 | True | False |
| seed | 58.46/8 | 142 | True | False |
| C_model:genie_mec | 58.73/8 | 143 | True | False |
| C_model:nuwro | 60.96/8 | 149 | True | False |
| C_model:gibuu | 149.76/8 | 76.2 | True | False |
| C_resp | 68.44/8 | 166 | True | False |
| V_g | 69.53/8 | 204 | True | False |

**The same χ² decomposed in absolute units (different modes):** chi2 58.46; modes 50/90/99 % 2/5/6; cond 623; top modes: mode 4 36.1 % dominant interaction (0.50); mode 0 25.8 % dominant flux (0.43); mode 3 14.3 % dominant C_model:gibuu (0.74)

#### variant: C_total + V_g

| mode | % of chi2 | sigma (rel) | dominant | stat | int | flux | det | lat | norm | seed | vMEC | vNuWro | vGiBUU | V_g |
|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 29.1 | 12.95 % | flux | 0.001 | 0.146 | 0.422 | 0.158 | 0.024 | 0.067 | 0.000 | 0.002 | 0.064 | 0.109 | 0.007 |
| 6 | 27.9 | 2.25 % | interaction | 0.007 | 0.504 | 0.036 | 0.040 | 0.101 | 0.001 | 0.000 | 0.004 | 0.083 | 0.001 | 0.223 |
| 0 | 15.6 | 20.46 % | C_model:gibuu | 0.000 | 0.009 | 0.056 | 0.010 | 0.174 | 0.008 | 0.000 | 0.002 | 0.000 | 0.740 | 0.001 |

**Loadings** (cells with |v| ≥ 0.25):

- mode 1: R00 +0.32, R01 +0.32, R10 +0.33, R11 +0.74
- mode 6: R00 +0.68, R01 -0.36, R02 -0.43, R10 +0.40
- mode 0: R02 +0.64, R03 +0.56, R11 -0.43

**Each block removed in turn** (descriptive breakdown, not an alternative result; χ², ndf and the condition number of M − B; no p-value):

| removed | chi2/ndf | condition | positive definite | ill-conditioned |
|---|---:|---:|---|---|
| stat | 68.92/8 | 170 | True | False |
| interaction | 85.51/8 | 494 | True | False |
| flux | 115.18/8 | 191 | True | False |
| detector | 89.10/8 | 168 | True | False |
| lateral | 93.01/8 | 367 | True | False |
| normalization | 72.08/8 | 165 | True | False |
| seed | 68.44/8 | 166 | True | False |
| C_model:genie_mec | 68.45/8 | 168 | True | False |
| C_model:nuwro | 69.35/8 | 196 | True | False |
| C_model:gibuu | 180.50/8 | 94.3 | True | False |
| V_g | 79.13/8 | 277 | True | False |

**The same χ² decomposed in absolute units (different modes):** chi2 68.44; modes 50/90/99 % 1/3/6; cond 675; top modes: mode 4 58.3 % dominant interaction (0.43); mode 0 22.3 % dominant flux (0.43); mode 6 12.8 % dominant interaction (0.75)

### 4.5 MnvTune v1 (the prior)

#### reported: C_total + C_resp + V_g

| mode | % of chi2 | sigma (rel) | dominant | stat | int | flux | det | lat | norm | seed | vMEC | vNuWro | vGiBUU | C_resp | V_g |
|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 13 | 47.9 | 0.97 % | interaction | 0.034 | 0.349 | 0.219 | 0.332 | 0.019 | 0.017 | 0.000 | 0.001 | 0.000 | 0.000 | 0.023 | 0.006 |
| 7 | 16.4 | 3.01 % | interaction | 0.015 | 0.421 | 0.084 | 0.006 | 0.024 | 0.001 | 0.000 | 0.331 | 0.000 | 0.017 | 0.100 | 0.001 |
| 14 | 13.6 | 0.63 % | interaction | 0.054 | 0.495 | 0.247 | 0.097 | 0.031 | 0.018 | 0.000 | 0.000 | 0.002 | 0.001 | 0.043 | 0.013 |

**Loadings** (cells with |v| ≥ 0.25):

- mode 13: R00 +0.26, R04 +0.54, R07 -0.28, R08 -0.38, R14 -0.41
- mode 7: R05 -0.40, R06 +0.77, R10 -0.28
- mode 14: R04 +0.60, R07 +0.26, R09 -0.39, R10 +0.31, R15 -0.33

**Each block removed in turn** (descriptive breakdown, not an alternative result; χ², ndf and the condition number of M − B; no p-value):

| removed | chi2/ndf | condition | positive definite | ill-conditioned |
|---|---:|---:|---|---|
| stat | 341.07/16 | 2.74e+03 | True | False |
| interaction | 1541.88/16 | 1.78e+04 | True | False |
| flux | 443.03/16 | 3.63e+03 | True | False |
| detector | 812.90/16 | 3.37e+03 | True | False |
| lateral | 561.88/16 | 3.34e+03 | True | False |
| normalization | 332.92/16 | 2.62e+03 | True | False |
| seed | 329.72/16 | 2.64e+03 | True | False |
| C_model:genie_mec | 374.09/16 | 3.81e+03 | True | False |
| C_model:nuwro | 335.91/16 | 2.72e+03 | True | False |
| C_model:gibuu | 335.47/16 | 1.76e+03 | True | False |
| C_resp | 360.79/16 | 3.17e+03 | True | False |
| V_g | 330.81/16 | 2.74e+03 | True | False |

**The same χ² decomposed in absolute units (different modes):** chi2 329.72; modes 50/90/99 % 2/5/9; cond 1.3e+04; top modes: mode 9 28.0 % dominant detector (0.40); mode 12 25.5 % dominant interaction (0.42); mode 11 24.9 % dominant interaction (0.49)

#### variant: C_total + V_g

| mode | % of chi2 | sigma (rel) | dominant | stat | int | flux | det | lat | norm | seed | vMEC | vNuWro | vGiBUU | V_g |
|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 11 | 46.4 | 1.15 % | interaction | 0.037 | 0.738 | 0.103 | 0.031 | 0.054 | 0.003 | 0.000 | 0.026 | 0.002 | 0.000 | 0.005 |
| 13 | 24.2 | 0.94 % | interaction | 0.038 | 0.398 | 0.181 | 0.330 | 0.026 | 0.013 | 0.000 | 0.006 | 0.000 | 0.000 | 0.008 |
| 14 | 9.8 | 0.60 % | interaction | 0.064 | 0.450 | 0.288 | 0.127 | 0.034 | 0.020 | 0.000 | 0.003 | 0.001 | 0.000 | 0.012 |

**Loadings** (cells with |v| ≥ 0.25):

- mode 11: R00 +0.42, R01 -0.29, R02 +0.37, R03 -0.31, R04 +0.30, R05 -0.42, R08 -0.30
- mode 13: R03 -0.27, R04 -0.45, R05 -0.28, R07 +0.31, R08 +0.27, R14 +0.46
- mode 14: R00 -0.26, R04 +0.65, R09 -0.44, R10 +0.28, R15 -0.29

**Each block removed in turn** (descriptive breakdown, not an alternative result; χ², ndf and the condition number of M − B; no p-value):

| removed | chi2/ndf | condition | positive definite | ill-conditioned |
|---|---:|---:|---|---|
| stat | 372.41/16 | 3.32e+03 | True | False |
| interaction | 1959.02/16 | 2.1e+04 | True | False |
| flux | 463.69/16 | 4.36e+03 | True | False |
| detector | 873.12/16 | 3.52e+03 | True | False |
| lateral | 564.80/16 | 3.55e+03 | True | False |
| normalization | 364.26/16 | 3.16e+03 | True | False |
| seed | 360.79/16 | 3.17e+03 | True | False |
| C_model:genie_mec | 430.77/16 | 4.08e+03 | True | False |
| C_model:nuwro | 375.74/16 | 3.23e+03 | True | False |
| C_model:gibuu | 360.79/16 | 1.99e+03 | True | False |
| V_g | 362.05/16 | 3.31e+03 | True | False |

**The same χ² decomposed in absolute units (different modes):** chi2 360.79; modes 50/90/99 % 2/6/12; cond 1.51e+04; top modes: mode 12 33.4 % dominant interaction (0.56); mode 9 21.3 % dominant C_model:genie_mec (0.37); mode 8 15.2 % dominant interaction (0.54)

## 5. What is committed

- **The readout:** [`fd/readout/fd_g_diag_readout.json`](fd/readout/fd_g_diag_readout.json), sha256 `680dc5ef…`.
  - Its `code_sha256` names `fd_g_diag.py` `7c161280…`.
  - Its absolute-unit breakdown carries absolute projections and eigenvalues, as Stage G's unguarded readout does.
- **Receipts:** [`fd/receipts-g-diag/`](fd/receipts-g-diag/), with a `SHA256SUMS`:
  - the deploy log and test log;
  - `diag.out`, `diag.err` and the start/end stamps;
  - `post-run.txt`;
  - the two step scripts and their stdout;
  - `summarize_g_diag.py` and its output `summary.txt`. It reads only the G-DIAG readout and the committed Stage G
    readout, the latter for total − shape-only, and every table above is from it.
- **The ledger:** two rows in `fd/LEDGER.tsv`.
- **Pre-binding receipts** (binding §3 item 6), in `fd/receipts-prebinding/` with its `SHA256SUMS`: the login37 test
  logs at `bbce3d77` (89 tests) and `91001a35` (90 tests). They are receipts of the tests only. The scratch clones
  behind them are removed after this report merges.
- **The results index:** this branch's first commit adds the readout and the regenerated index, under the director's
  standing ruling (a) of 2026-10-26. The PR body gives the scope.

## Not changed

Stage G's readout and report; the S1 covariance, C_model,5D, C_resp, R00–R15 and κ = 1. No group or species is split.
The reading of these numbers, any claim, printed wording and publication are Joseph's.
