# REPORT F0b: F0's re-grade against C^(T) + C_resp, and the HPSS copy of cresp.npz (2026-10-26)

**By** the measurement session.

**Under** [`FD-F0b-AND-G-BINDING.md`](FD-F0b-AND-G-BINDING.md) (PR #376, main `659363d5`), which binds
[`FD-F0b-DECLARATION.md`](FD-F0b-DECLARATION.md) §§2.1–2.3 at deploy pin `c4396756`.

**MEASURES:** the (e) estimator's fake-data bias at F0's 18 truths on R00–R15, graded against C^(T) + C_resp, beside
F0's grades against C^(T); and the HPSS copy of `cresp.npz`.

**CANNOT AUTHORIZE:** Stage G's run, which the binding orders after this report is merged; any reading of these
numbers; a claim, printed wording, or a conclusion on limitations or publishability, which are Joseph's.

**CITABLE FOR:** the counts, χ² and p below, each beside its matrix; the equality of control 7 and the model-only
grades with F0's; and the HPSS copy's verification.

**NOT CITABLE FOR:**
- any data-against-generator quantity, since F0b reads only fake-data products;
- coverage, held-out truths or the detector response, exactly as for F0 (`FD-F0-REPORT.md`);
- any reading of the difference between the two columns.

**Outcome:**
- **The order was kept,** with every step exiting 0 on login37 at 0 node-h. No step names a CFS path:
  1. deploy and tests;
  2. the HPSS copy;
  3. the re-grade.
- **HPSS:** PASS by hashverify and by retrieval. The tar is `8d791bed…`, 20,480 B, at
  `/home/j/josephrb/mnv-5d-cresp-20261026`.
- **The re-grade:** exit 0 in 70 s. The readout is `b9db935a…`, and the per-experiment table is `7384c651…`,
  byte-identical to F0's table.
- **The binding's §2 item 3 condition holds** (§3): control 7's χ²₁₆ and all 18 model-only grades equal F0's
  committed readout exactly.
- **Control 7 failed again,** as expected and as in F0. Row 6 is descriptive and ungraded.

## 1. The steps

| step | host | start (UTC) | end | rc | wall | result |
|---|---|---|---|---:|---:|---|
| §2.1 deploy and tests | login37 | 09:43:21 | 09:49:42 | 0 | 381 s | HEAD `c4396756…`; porcelain 0 before and after; every §8 digest matches, and the declaration's is `f2727f38…`, the binding's; `tests rc=0`, "Ran 69 tests in 345.214s", OK |
| §2.2 HPSS copy | login37 | 09:50:01 | 09:50:05 | 0 | 4 s | **Before:** HPSS 422.79 of 512.00 GiB used (89.21 GiB free, at least the 1 GiB required); `hsi ls -d` returned HPSS_ENOENT. **The copy:** inventory verified (1 file), tar `8d791bede67effb1f0c4b43ee4e7962f0073c07773fb80341b148d2f56955333`, put, `(md5) OK` from hashverify, the retrieved copy equal by sha256, `PASS` |
| §2.3 re-grade | login37 | 09:50:28 | 09:51:38 | 0 | 70 s | readout `b9db935a3187646ba2accaf3865cf4aa26ad72676063c58e7f5e6220224ef17b`; table `7384c6518aa0f59bd4964170fcc9b652f1c31958f422f1e1b597cd3e59219ad9`; `f0b.err` empty |

All on 2026-10-26.

**Each step was run by a script,** committed under `fd/receipts-f0b/`, that carries the declaration's commands
verbatim:
- `step1.sh` refuses if `$B` exists and ends `STEP1-DONE`. It was launched detached at 09:43:21
  (`step1-launch.txt`); `deploy.log`'s first stamp, 09:43:53, follows the clone.
- `step2.sh` adds the binding's quota and ENOENT checks, refuses if `$B/preserve` exists, and refuses unless step 1
  printed `tests rc=0`. Its stdout, `step2-stdout.txt`, prints `hpss_free_gib 89.21`.
  - The guard checks only `tests rc=0`. The binding's other step 1 conditions (HEAD, porcelain, digests, "Ran 69
    tests") were read from `deploy.log` before step 2 was launched, by hand, not by the guard.
  - In the script, the variable named `used` holds the free GiB.
- `step3.sh` refuses unless `preserve.out` ends `rc=0`, and refuses if the readout exists. Its stdout is
  `step3-stdout.txt`.

The scripts sat in `$P/fd-f0b-launch-20261026/`, outside `$B`, because `$B` had to be absent before step 1. That
location is from the session's run, not a receipt; the scripts' own paths are in them.

**The HPSS directory after the copy** (`hsi_ls_l.txt`): `INVENTORY.sha256` (119 B), `stage0-inputs.tar` (20,480 B)
and `stage0-inputs.tar.sha256` (133 B).
- As declared, the script names its tar `stage0-inputs.tar`. The directory name identifies this copy.
- After PASS, only `$B/preserve/stage0-inputs.tar` was deleted. The listing of `$B/preserve` and a fresh sha256 of
  `cresp.npz`, `4d8b5797…a8a20a`, are in `step2-post.txt`.
- `hpssquota` printed the same 422.79 GiB after the copy as before. The 20 kB copy is below its two-decimal
  resolution.

**`$B` after the run** (`post-run.txt`):
- the deploy clone;
- `fd_f0b_readout.json` (88,532 B) and `fd_f0b_experiments.npz` (1,068,642 B);
- `logs/`, `preserve/` and `tmp/`;
- 573 MB in all.

No step script names a path under F0's `$P/fd-f0-20261025`, or any CFS path.

## 2. Controls

| control | outcome |
|---|---|
| 0 | PASS: the 80 `f4` products match their D16 sha256 |
| 1 | PASS: 8,545 products and **9** records match, the ninth being `cresp.npz` against `--extra-block-sha256` |
| 2, 3 | PASS, as in F0 |
| 4 | PASS on all 23 checks: F0's 19, and for C_resp a finite 16 × 16 matrix, symmetric, PSD, and C_total + C_resp positive definite |
| 5 | PASS: the closure bias equals `cmodel_5d.json` |
| 6 | PASS: the closure floor max |bias| is 3.217964e-05, the recorded value |
| 7 | **FAIL, as in F0:** χ²₁₆ = 245.742, p below 10⁻³⁰. As declared, it gates row 6 only, so row 6 is descriptive and ungraded |
| 8 | PASS: every truth integral is positive on all 16 cells |

## 3. The binding's §2 item 3 condition: equality with F0, to a relative 10⁻¹²

This was checked by [`receipts-f0b/summarize_f0b.py`](fd/receipts-f0b/summarize_f0b.py) against the committed
`fd/readout/fd_f0_readout.json`. Its output is [`receipts-f0b/summary.txt`](fd/receipts-f0b/summary.txt).

| quantity | F0 | F0b | equal |
|---|---|---|---|
| control 7 χ²₁₆ | 245.7422835730337 | 245.7422835730337 | yes, exactly; the whole `controls` record is identical |
| model-only grades (χ², z, p), 18 truths | — | — | 18 of 18 equal; all 18 records identical |
| bias, noise σ, B_eff, graded, per truth | — | — | identical for all 18 |
| per-experiment table | `7384c651…` | `7384c651…` | byte-identical |

**The condition holds, so Stage G is not held by it.**

## 4. Trigger counts by group (FD-F0b §7 item 4)

The denominators and Gaussian references are F0's. The counts are read by group, never pooled (ruling 2).

| group | cells \|z\| > 2, against C^(T) (F0) | against C^(T) + C_resp (F0b) | Gaussian ref | truths p < 0.01, against C^(T) (F0) | against C^(T) + C_resp (F0b) | ref |
|---|---:|---:|---:|---:|---:|---:|
| vertex-family | 4 of 128 | 4 of 128 | 5.82 | 3 of 8 | 1 of 8 | 0.08 |
| non-vertex | 0 of 32 | 0 of 32 | 1.46 | 1 of 2 | 1 of 2 | 0.02 |
| prior | 0 of 32 | 0 of 32 | 1.46 | 0 of 2 | 0 of 2 | 0.02 |
| denominators | 4 of 192 | 4 of 192 | 8.74 | 4 of 12 | 2 of 12 | 0.12 |

**By vertex family:**
- NuWro (4 truths): 0 and 0 cells; p < 0.01 in 1 truth (F0) and 0 (F0b).
- GENIE+MEC (2): 0 and 0 cells; 0 and 0 truths.
- GiBUU (2): 4 and 4 cells; 2 and 1 truths.

## 5. Listed truths

A truth is listed if it has a cell with |z| > 2 or p < 0.01 against its grade matrix.

| truth | F0, against C^(T): cells \|z\| > 2; p < 0.01 | F0b, against C^(T) + C_resp |
|---|---|---|
| W3 | none; yes | **not listed** (p 0.0141) |
| q3 | none; yes | none; yes |
| Stage 0c GiBUU | R06; yes | R06; **no** (p 0.0621) |
| A7 GiBUU | R02, R06, R07; yes | R02, R06, R07; yes |

**Truths whose listing changes between F0 and F0b:**
- **W3** is listed in F0 and not in F0b.
- **Stage 0c GiBUU** is listed in both. Its p < 0.01 entry is yes in F0 and no in F0b, and its cell R06 is in both.
- No truth is listed in F0b only.

## 6. Per truth: χ² / p

ndf is 16, and 8 for the eight-cell variant. "<1e-30" marks `p_below_floor`.
- **The F0 column's matrices:** the grade is against C^(T); the in-sample matrix is C_total with every vertex; the
  sensitivity matrix leaves out the declared vertex; the eight-cell matrix is the grade matrix on R00–R03, R08–R11.
- **The F0b column's matrices** are the same, each + C_resp.
- **The model-only matrix,** C_stat + C_model with the own vertex left out, is the same in both, and so is its χ².
- Rows 6 (P1r–P3g) are **ungraded and descriptive** in both, since control 7 failed.

| truth | row | group | grade, F0 | grade, F0b | in-sample, F0 | in-sample, F0b | sensitivity, F0 | sensitivity, F0b | model-only (both) | 8-cell, F0 | 8-cell, F0b |
|---|---:|---|---|---|---|---|---|---|---|---|---|
| nominal | 1 | prior | 0.00 / 1 | 0.00 / 1 | – | – | – | – | 0.39 / 1 | – | – |
| W1 | 1 | vertex-family | 5.69 / 0.991 | 5.01 / 0.996 | 5.69 / 0.991 | 4.99 / 0.996 | – | – | 1647.66 / <1e-30 | – | – |
| W2 | 1 | vertex-family | 0.77 / 1 | 0.57 / 1 | 0.42 / 1 | 0.35 / 1 | – | – | 117.49 / 1.66e-17 | – | – |
| W3 | 1 | vertex-family | 36.19 / 0.00273 | 30.83 / 0.0141 | 34.82 / 0.00421 | 28.82 / 0.0252 | – | – | 5552.98 / <1e-30 | – | – |
| q3 | 1 | non-vertex | 59.83 / 5.59e-07 | 53.42 / 6.44e-06 | – | – | 61.24 / 3.23e-07 | 54.57 / 4.18e-06 | 11642.59 / <1e-30 | – | – |
| Stage 0c GiBUU | 2 | vertex-family | 35.75 / 0.00313 | 25.46 / 0.0621 | 29.30 / 0.022 | 23.05 / 0.113 | – | – | 7990.52 / <1e-30 | 20.93 / 0.00734 | 12.42 / 0.133 |
| closure NuWro | 3 | vertex-family | 13.08 / 0.667 | 11.60 / 0.771 | 13.03 / 0.671 | 11.59 / 0.772 | – | – | 2890.73 / <1e-30 | – | – |
| A7 MnvTune | 4 | prior | 0.01 / 1 | 0.01 / 1 | – | – | – | – | 0.20 / 1 | – | – |
| A7 GENIE CV | 4 | non-vertex | 17.37 / 0.362 | 16.14 / 0.443 | – | – | 18.29 / 0.307 | 17.04 / 0.383 | 1794.19 / <1e-30 | – | – |
| A7 GENIE+MEC | 4 | vertex-family | 16.18 / 0.44 | 14.54 / 0.558 | 11.86 / 0.753 | 11.00 / 0.809 | – | – | 1006.75 / <1e-30 | – | – |
| A7 NuWro | 4 | vertex-family | 29.96 / 0.0182 | 24.92 / 0.0713 | 29.23 / 0.0224 | 24.78 / 0.0738 | – | – | 3028.41 / <1e-30 | – | – |
| A7 GiBUU | 4 | vertex-family | 246.75 / <1e-30 | 175.13 / 7.96e-29 | 180.99 / 5.32e-30 | 142.62 / 2.21e-22 | – | – | 24824.55 / <1e-30 | 197.77 / <1e-30 | 133.91 / 4.38e-25 |
| P1r | 6 | vertex-family | 50.64 / 1.81e-05 | 44.55 / 0.000163 | 47.43 / 5.84e-05 | 39.68 / 0.000866 | – | – | 1686.44 / <1e-30 | – | – |
| P2r | 6 | vertex-family | 40.73 / 0.000609 | 37.04 / 0.00207 | 31.34 / 0.0122 | 29.55 / 0.0205 | – | – | 4309.11 / <1e-30 | – | – |
| P3r | 6 | vertex-family | 2.96 / 1 | 2.50 / 1 | 2.66 / 1 | 2.15 / 1 | – | – | 69.81 / 1.08e-08 | – | – |
| P1g | 6 | vertex-family | 85.50 / 1.67e-11 | 82.48 / 5.93e-11 | 80.27 / 1.49e-10 | 77.57 / 4.55e-10 | – | – | 2988.64 / <1e-30 | – | – |
| P2g | 6 | vertex-family | 39.38 / 0.000959 | 37.97 / 0.00153 | 32.74 / 0.008 | 31.86 / 0.0104 | – | – | 5171.70 / <1e-30 | – | – |
| P3g | 6 | vertex-family | 24.83 / 0.0728 | 23.25 / 0.107 | 22.63 / 0.124 | 21.31 / 0.167 | – | – | 1174.19 / <1e-30 | – | – |

**The matrix names in the F0b readout** are "C_total + C_resp", or "C_total minus genie_mec / nuwro / gibuu + C_resp".
The sensitivity matrices are "C_total minus nuwro + C_resp" (q3) and "C_total minus genie_mec + C_resp" (A7 GENIE CV).

Each model-only record carries F0's label: descriptive, with no threshold, and without the interaction, flux,
detector, lateral and normalization blocks (`MODEL_ONLY_LABEL`).

## 7. Per-cell relative σ, in % (median, min, max)

From the readout's `relative_sigma_summary_percent` (F0's matrices) and
`relative_sigma_plus_C_resp_summary_percent`.

| matrix | F0 | + C_resp (F0b) |
|---|---|---|
| C_e | 6.45, 4.05, 8.47 | 6.84, 4.11, 8.73 |
| C_total | 6.74, 4.14, 13.69 | 7.29, 4.20, 14.00 |
| C_total minus GENIE+MEC | 6.74, 4.14, 13.69 | 7.25, 4.20, 14.00 |
| C_total minus NuWro | 6.74, 4.09, 13.49 | 7.20, 4.15, 13.81 |
| C_total minus GiBUU | 6.46, 4.11, 8.78 | 6.97, 4.17, 9.17 |
| C_resp alone (`extra_block.relative_sigma`) | — | 2.14, 0.70, 3.71 |

C_total + C_resp's row (7.29, 4.20, 14.00) and C_resp's (2.14, 0.70, 3.71) equal `CRESP-REPORT.md` §2's.

## 8. What is committed

- **The readout:** [`fd/readout/fd_f0b_readout.json`](fd/readout/fd_f0b_readout.json), sha256 `b9db935a…`,
  schema `fd-f0b-readout/1`.
  - It passed the leak guard before it was written: no f, no absolute cell value, no f − g.
  - `code_sha256` names `fd_f0_regrade.py` `37427d9d…`, as pinned.
- **Receipts:** [`fd/receipts-f0b/`](fd/receipts-f0b/), with a `SHA256SUMS`:
  - the deploy log and test log;
  - `preserve.out`, `preserve.log`, `paths.list` and `stage0-inputs.tar.sha256`;
  - `hpssquota` before and after, the ENOENT check, `hsi_ls_l.txt`;
  - the start, end and post-run stamps;
  - `f0b.out` and `f0b.err`;
  - the three step scripts, their stdout (`step1.out`, which is empty, `step1-launch.txt`, `step2-stdout.txt`,
    `step2-post.txt` and `step3-stdout.txt`);
  - `summarize_f0b.py` and `summary.txt`.
- **The results index:** this branch's first commit adds the readout and the index regenerated from it
  (`RESULTS-INDEX.tsv`, `RESULTS-POPULATION.tsv`, `records_results_index.tex`), by `tools/registry/results_index.py
  --write`, under the director's ruling. F0's report commit (`28c4870f`) went through the shared 13-check hook, and the
  director regenerated the index after it (`7dfbaa6b`). That gap is why this one is regenerated in-branch.
- **The ledger:** three rows in `fd/LEDGER.tsv`, one per step, as binding §4 item 8 asks. Declaration §2.3 said two
  rows; the deploy row is the third.
- **Pre-binding receipts** (binding §4 item 9), in `fd/receipts-prebinding/`, added to its `SHA256SUMS`. They are
  receipts of the tests only, not of any run:
  - Stage G's test logs at `7fd3688d` (38 tests), `d1b12bdb` (46) and `bc811bf8` (46), run on login37 by the
    session's own record (the logs do not print a host);
  - the test logs at `885ad0eb`, Stage G (49) and F0/F0b (69).
  - The scratch clones behind them are removed after this report merges.
- **Stays on pscratch:** the table `fd_f0b_experiments.npz`, on the retention list re-raised before 2026-11-20.

## 9. Next, by the binding's order

1. This report is merged.
2. Then Stage G runs: deploy at `c4396756` with "Ran 49 tests", then the comparison with the five `--extra-block`
   arguments of binding §3 item 1, role `adopted`.

## Not changed

F0's readout, report and receipts; the S1 covariance; C_model,5D; C_resp; R00–R15; κ = 1; the route decision. Every
claim, all printed wording and publication are Joseph's.
