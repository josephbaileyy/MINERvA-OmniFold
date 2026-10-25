# REPORT F0: re-grade of the existing (e) fake-data products on the 16 H2 cells (2026-10-25)

**By** the measurement session, for the director.

**Under** [`FD-F0-BINDING.md`](FD-F0-BINDING.md) (PR #358, main `890666b7`). That binding binds
[`FD-F0-DECLARATION.md`](FD-F0-DECLARATION.md) (sha256 `f60336d4…`) at deploy pin `7fad6e83`.

**MEASURES:**
- the declaration's §2 steps, as bound, with their receipts;
- every control's outcome;
- the readout's counts, with their denominators and Gaussian references;
- each truth's grade and its labelled variants.

**CANNOT AUTHORIZE, and draws no conclusion on:**
- a limitation, a paper statement or publishability, which the director proposes to Joseph;
- any claim or printed wording;
- Stage G, F1, F1-W or any merge.

**CITABLE FOR:** what F0 computed on the declared inputs, and that every refusing control passed.

**NOT CITABLE FOR:**
- the coverage of C_total, which is not a gate (DECISION-20261024 route item 3);
- any held-out-truth statement;
- anything about the detector response's model dependence, which no truth here probes;
- any reading of the data against a generator.

**Values:**
- Every number below is a relative quantity, a χ², a p-value or a count, copied from the guarded readout.
- There is no f, no absolute cell value and no f − g.
- The readout passed the tool's leak guard before it was written (declaration §5.3). The rounded copies here can only
  be coarser.

## 0. Summary

- **Cost:** 0 node-h. Both steps ran on login37, with no Slurm job. Nothing went to CFS.
- **The HPSS copy** of the 80 `f4` products passed in 5 s, with hashverify and a retrieval check (§2).
- **The re-grade** exited 0 in 44 s (§3).
  - Controls 0–6 and 8 passed.
  - **Control 7, the offset control, failed:** χ²_16 = 245.74, with p below 10⁻³⁰. As declared and bound, row 6 (P1r,
    P2r, P3r, P1g, P2g, P3g) is therefore **descriptive and ungraded**. The graded set is 12 truths and 192 cells.
- **Triggers** (ruling 2: |z| > 2 per cell, p < 0.01 per truth, against the grade matrix), by group:

  | group | truths | cells \|z\| > 2 | Gaussian ref. | truths p < 0.01 | Gaussian ref. |
  |---|---:|---:|---:|---:|---:|
  | vertex-family | 8 | 4 of 128 | 5.82 | 3 of 8 | 0.08 |
  | — NuWro | 4 | 0 of 64 | | 1 of 4 | |
  | — GENIE MEC | 2 | 0 of 32 | | 0 of 2 | |
  | — GiBUU | 2 | 4 of 32 | | 2 of 2 | |
  | non-vertex | 2 | 0 of 32 | 1.46 | 1 of 2 | 0.02 |
  | prior | 2 | 0 of 32 | 1.46 | 0 of 2 | 0.02 |
  | all graded: ruling 2's denominator line, "read by group, never pooled" | 12 | 4 of 192 | 8.74 | 4 of 12 | 0.12 |

  - The Gaussian references are context only, because b is a deterministic bias.
  - The per-family references are not in the readout. They are 16 × truths × 0.0455 and truths × 0.01.
- **The truths listed by the triggers:**
  - W3, by p;
  - q3, by p;
  - Stage 0c GiBUU, by p and cell R06;
  - A7 GiBUU, by p and cells R02, R06 and R07.

## 1. Deploy and tests (declaration §2.1, binding §4 item 1)

**What ran:** a clone of `7fad6e8335003dd1466b78517478f88b80eea487` into `$B/deploy/7fad6e83`, with
`B=/pscratch/sd/j/josephrb/fd-f0-20261025`, on login37 at 2026-10-25T21:54:22Z. The receipts are
[`fd/receipts/deploy.log`](fd/receipts/deploy.log) and `deploy-tests.log`.

**Every bound condition held:**
- HEAD is the pin.
- `git status --porcelain --ignored` printed 0 lines before the tests and 0 after.
- All seven §8 digests match: `05f9161c…`, `ef2cacd7…`, `b157250a…`, `26569afc…`, `b6790761…`, `27ccc04a…`,
  `c3c245cf…`. The declaration is `f60336d4…`, which the binding names.
- `test_fd_f0_regrade`, `test_s1_assemble` and `test_s1_scripts_isolated`, run with `-B` and `TMPDIR=$B/tmp` on
  `root_6_28`, gave `tests rc=0` and "Ran 60 tests … OK".
- `$B` did not exist before this step.

## 2. The HPSS copy of the `f4` products (declaration §2.2, binding §4 item 2)

**Before:** `hpssquota` read 422.78 of 512.00 GiB used, so 89.22 GiB was free, against the bound minimum of 1 GiB
(`receipts/hpssquota-before.txt`).

**What ran:** the unchanged `stage0_preserve.sh` (`27ccc04a…`) over `fd/F4-PRESERVE-INVENTORY.sha256`. It ran
detached under `timeout 1500` on login37, from 21:59:24Z to 21:59:29Z. The receipts are `receipts/preserve.out`,
`preserve.log`, `paths.list` and `stage0-inputs.tar.sha256`.

**The steps:**
- **Control 0, shell form:** "inventory verified: 80 files".
- **The tar:** sha256 `14e2957facea180051cd086b11ad8a7075a50385e3909ede95ac56db3aeb0ead`, 14,888,960 B.
  - tar printed "Removing leading `/' from hard link targets". That is tar's wording for stripping the leading `/` from
    member names. It does not mean a hard link was archived.
- **`hsi put`, `hashcreate`, and the two side files put.**
- **hashverify:** "(md5) OK".
- **The retrieval:** `hsi get`, compared by sha256 and equal. The last lines are "PASS: HPSS copy verified by
  hashverify and by retrieval (14e2957f…)" and `rc=0`.

`hsi ls -l /home/j/josephrb/mnv-5d-fd-f4-20261025` (`receipts/hsi_ls_l.txt`):

```text
-rw-r-----    1 josephrb  josephrb       12640 Oct 25 14:59 INVENTORY.sha256
-rw-r-----    1 josephrb  josephrb    14888960 Oct 25 14:59 stage0-inputs.tar
-rw-r-----    1 josephrb  josephrb         132 Oct 25 14:59 stage0-inputs.tar.sha256
```

**After:**
- **Names, as the declaration stated:** the tar is called `stage0-inputs.tar` and the inventory copy
  `INVENTORY.sha256`. The HPSS directory name identifies this copy.
- **Cleanup:** as declared, `$B/preserve/stage0-inputs.tar` was deleted after PASS, and the retrieve directory is empty.
  The 80 products are untouched.
- **Quota:** `hpssquota` after the copy still reads 422.78 GiB, which is below its display resolution
  (`receipts/hpssquota-after.txt`).
- **The FD-PLAN §6 purge row for `f4`** ("HPSS copy: **no**") is now discharged.

## 3. The re-grade (declaration §2.3, binding §4 item 3)

**What ran:** the exact bound argv, under `timeout 1125` on login37, from 21:59:49Z to 22:00:33Z. It took 44 s
against the 15-minute projection.
- It exited 0 (`receipts/f0.out`, last line `rc=0`). `receipts/f0.err` is empty.
- It wrote `$B/fd_f0_readout.json` (sha256 `6e7d718bd393dd0600e974d0ce9b5c389486890cb7112550b22289008d6d312b`,
  84,840 B), committed as [`fd/readout/fd_f0_readout.json`](fd/readout/fd_f0_readout.json) and re-measured equal.
- It wrote `$B/fd_f0_experiments.npz` (sha256 `7384c6518aa0f59bd4964170fcc9b652f1c31958f422f1e1b597cd3e59219ad9`,
  1,068,642 B). That equals the readout's `table_sha256`. It stays on pscratch (§6).

### 3.1 Controls

| # | outcome | detail (verbatim lines in `receipts/f0.out`) |
|---|---|---|
| 0 | PASS | the 80 `f4` products match their D16 sha256 |
| 1 | PASS | 8,545 products and 8 records match their recorded sha256 |
| 2 | PASS | every product was made by (e) at its declared truth |
| 3 | PASS | counts as declared: 8,544 products in the graded and calibration sets (1,368 graded, 7,176 for the offset control), plus the floor |
| 4 | PASS | all 19 matrix checks: U, f > 0, the 46-block sum, C_total, C_model_abs, S bitwise, SᵀS, σ(C_total); σ from the npz against the JSONs, and the FD-PLAN §2.1 row, for each of the five matrices; C_stat,rel full rank |
| 5 | PASS | the closure's bias equals `cmodel_5d.json` `reporting16.bias_cells` to 10⁻¹² |
| 6 | PASS | the closure floor's max \|bias\| is 3.217964e-05, which reproduces the recorded value (readout 3.217964049651023e-05, against 3.2179640496732276e-05 recorded; a difference of 2 × 10⁻¹⁷). Reported first, not graded |
| 7 | **FAIL, as a gate on row 6 only** | χ²_16 = 245.742, p below 10⁻³⁰. Row 6 is descriptive and ungraded |
| 8 | PASS | every truth integral is positive on all 16 cells |

**Control 7 in detail** (readout `controls.offset_control_7`):
- **The gating pair** is O_MnvTune − O_GENIE CV: χ² = 245.74 with ndf 16, and p below 10⁻³⁰.
- **B_eff of the calibration sets:** MnvTune 272.7, GENIE CV 243.9, GENIE MEC 246.0, NuWro 320.8, GiBUU 262.8.
- **`row4_noise_trace_share`** (row 4's share of each offset's noise trace): MnvTune 0.006, GENIE CV 0.007, GENIE MEC
  0.011, NuWro 0.026, GiBUU 0.034.
  - The rank-15 row-4 part that declaration §7 item 11 flagged is 0.6–3.4 % of each offset's noise trace.
  - The upward lean of about n/(n − 17) from the calibration part is about 6–7 % at these B_eff **(arithmetic)**.
- **The nine descriptive pairs:**

  | pair | χ²_16 | p |
  |---|---:|---:|
  | MnvTune − GENIE MEC | 158.32 | 1.8e-25 |
  | MnvTune − NuWro | 439.25 | < 10⁻³⁰ |
  | MnvTune − GiBUU | 126.42 | 3.2e-19 |
  | GENIE CV − GENIE MEC | 126.96 | 2.5e-19 |
  | GENIE CV − NuWro | 538.79 | < 10⁻³⁰ |
  | GENIE CV − GiBUU | 205.00 | < 10⁻³⁰ |
  | GENIE MEC − NuWro | 419.82 | < 10⁻³⁰ |
  | GENIE MEC − GiBUU | 230.09 | < 10⁻³⁰ |
  | NuWro − GiBUU | 228.99 | < 10⁻³⁰ |

## 4. The covariances on R00–R15

Per-cell relative σ, as the readout prints it (median / min / max, %). Each row reproduces FD-PLAN §2.1 exactly
(control 4):

| matrix | median | min | max |
|---|---:|---:|---:|
| C_e | 6.45 | 4.05 | 8.47 |
| C_total | 6.74 | 4.14 | 13.69 |
| C_total without GENIE+MEC | 6.74 | 4.14 | 13.69 |
| C_total without NuWro | 6.74 | 4.09 | 13.49 |
| C_total without GiBUU | 6.46 | 4.11 | 8.78 |

## 5. Per-truth grades

**How to read the tables:**
- The grade is against the matrix named in the "matrix" column, with ndf 16.
- The in-sample, sensitivity, model-only and eight-cell variants are **descriptive** and carry no trigger.
  - "In-sample" includes the truth's own vertex: not evidence.
  - "Model-only" is C_stat + C_model without the own vertex. It drops the interaction, flux, detector, lateral and
    normalization blocks, so it is a lower bound on C_model's reach.
- "max |b|" is the largest per-cell relative bias, and "max σ_N" the largest per-cell noise of the mean.
- A p shown as "< 1e-30" is written in the readout as 0.0 with `p_below_floor` true.

### 5.1 Graded truths (12)

| truth (row) | group, own vertex | n | matrix | grade χ² | p | cells \|z\| > 2 | in-sample χ² (p) | sensitivity or 8-cell χ² (p) | model-only χ² (p) | max \|b\| | max σ_N |
|---|---|---:|---|---:|---:|---|---|---|---|---:|---:|
| nominal (1) | prior | 40 | C_total | 0.00 | 1.00 | — | — | — | 0.39 (1.00) | 0.0007 | 0.0004 |
| A7 MnvTune (4) | prior | 16 | C_total | 0.01 | 1.00 | — | — | — | 0.20 (1.00) | 0.0005 | 0.0006 |
| q3 (1) | non-vertex | 20 | C_total | 59.83 | 5.6e-07 | — | — | sens. −NuWro: 61.24 (3.2e-07) | 11,642.59 (< 1e-30) | 0.1287 | 0.0009 |
| A7 GENIE CV (4) | non-vertex | 16 | C_total | 17.37 | 0.362 | — | — | sens. −GENIE+MEC: 18.29 (0.307) | 1,794.19 (< 1e-30) | 0.0306 | 0.0006 |
| W1 (1) | vertex, NuWro | 20 | −NuWro | 5.69 | 0.991 | — | 5.69 (0.991) | — | 1,647.66 (< 1e-30) | 0.0420 | 0.0008 |
| W3 (1) | vertex, NuWro | 20 | −NuWro | 36.19 | 0.0027 | — | 34.82 (0.0042) | — | 5,552.98 (< 1e-30) | 0.0885 | 0.0010 |
| closure at NuWro (3) | vertex, NuWro | 1 | −NuWro | 13.08 | 0.667 | — | 13.03 (0.671) | — | 2,890.73 (< 1e-30) | 0.0683 | 0 |
| A7 NuWro (4) | vertex, NuWro | 16 | −NuWro | 29.96 | 0.0182 | — | 29.23 (0.0224) | — | 3,028.41 (< 1e-30) | 0.1050 | 0.0014 |
| W2 (1) | vertex, GENIE MEC | 20 | −GENIE+MEC | 0.77 | 1.00 | — | 0.42 (1.00) | — | 117.49 (1.7e-17) | 0.0097 | 0.0007 |
| A7 GENIE MEC (4) | vertex, GENIE MEC | 16 | −GENIE+MEC | 16.18 | 0.440 | — | 11.86 (0.753) | — | 1,006.75 (< 1e-30) | 0.0257 | 0.0007 |
| Stage 0c GiBUU (2) | vertex, GiBUU | 20 | −GiBUU | 35.75 | 0.0031 | R06 | 29.30 (0.022) | 8-cell: 20.93 (0.0073) | 7,990.52 (< 1e-30) | 0.1056 | 0.0008 |
| A7 GiBUU (4) | vertex, GiBUU | 16 | −GiBUU | 246.75 | < 1e-30 | R02, R06, R07 | 180.99 (5.3e-30) | 8-cell: 197.77 (< 1e-30) | 24,824.55 (< 1e-30) | 0.3604 | 0.0014 |

**Cells with |z| > 2 under each descriptive variant** (readout `cells_abs_z_gt_2`):

| truth | in-sample | 8-cell | model-only |
|---|---|---|---|
| Stage 0c GiBUU | none | none | R00, R02, R03, R06, R07, R08, R10, R12, R15 |
| A7 GiBUU | R02, R06 | R02 | R00–R03, R06–R08, R10, R12, R13, R15 |
| W1 | | | R12 |
| W3 | | | R10, R12 |
| q3 | | | R00, R07, R08, R10, R12, R15 |
| closure at NuWro | | | R12 |
| A7 GENIE MEC | | | R12 |
| A7 NuWro | | | R06, R07, R12 |

Every truth not listed above, and every blank cell, has none.

### 5.2 Row 6: descriptive and ungraded (control 7 failed)

- **What these numbers are:** first-order offset-corrected, b = b̃_T − O_ref, with ref MnvTune for P·r and GENIE CV
  for P·g.
- **What they are not:** they enter no count or denominator.
- **Why:** the offset correction they rest on did not pass its control.

| truth | own vertex | n | B_eff | χ² (p), C_total minus own | cells \|z\| > 2 | in-sample χ² (p) | model-only χ² (p) | max \|b\| | max σ_N |
|---|---|---:|---:|---|---|---|---|---:|---:|
| P1r | NuWro | 193 | 32.5 | 50.64 (1.8e-05) | — | 47.43 (5.8e-05) | 1,686.44 (< 1e-30) | 0.1046 | 0.0154 |
| P2r | NuWro | 195 | 49.7 | 40.73 (6.1e-04) | — | 31.34 (0.0122) | 4,309.11 (< 1e-30) | 0.1545 | 0.0154 |
| P3r | GENIE MEC | 195 | 40.4 | 2.96 (1.00) | — | 2.66 (1.00) | 69.81 (1.1e-08) | 0.0468 | 0.0171 |
| P1g | NuWro | 199 | 39.1 | 85.50 (1.7e-11) | — | 80.27 (1.5e-10) | 2,988.64 (< 1e-30) | 0.1178 | 0.0182 |
| P2g | NuWro | 193 | 39.1 | 39.38 (9.6e-04) | R07 | 32.74 (0.0080) | 5,171.70 (< 1e-30) | 0.1710 | 0.0177 |
| P3g | GENIE MEC | 172 | 33.1 | 24.83 (0.0728) | — | 22.63 (0.124) | 1,174.19 (< 1e-30) | 0.0425 | 0.0206 |

Every per-cell value (b, σ_N and z for each variant) is in the committed readout.

## 6. The per-experiment table

- **The binding's advance ruling (§3)** applied only if the receipt-artifacts check required the table. The check was
  run on this report's commit (§8): it does not flag `fd_f0_experiments.npz`.
- **So the table stays on pscratch,** as declared: `$B/fd_f0_experiments.npz`, sha256 `7384c651…`, equal to the
  readout's `table_sha256`.
- It holds relative residuals, seeds and flux indices only, and the leak guard passed over it.

## 7. Receipts and ledger

**`fd/receipts/`:**
- `deploy.log`, `deploy-tests.log`;
- `hpssquota-before.txt`, `hpssquota-after.txt`;
- `preserve-start.txt`, `preserve.out`, `preserve.log`, `paths.list`, `stage0-inputs.tar.sha256`, `hsi_ls_l.txt`;
- `f0-start.txt`, `f0.out`, `f0.err`.

`deploy-tests.log` holds the synthetic tests' own output lines, which carry fixture values only.

**[`fd/LEDGER.tsv`](fd/LEDGER.tsv)** has two rows:

| step | host | wall | rc | node-h |
|---|---|---|---|---|
| the HPSS copy | login37 | 5 s | 0 | 0 |
| the re-grade | login37 | 44 s | 0 | 0 |

**State on pscratch:**
- `$B` holds the deploy, the logs, the readout and the table;
- the scratch test clones are in `$P/fd-f0-testcheck-20261025/`;
- nothing else was written.

## 8. Checks on this report's commit

Run after the commit:
- `generate_manifest.py --check --at-sha HEAD`;
- `verify_hash_bindings.py`;
- `.githooks/pre-commit`;
- `tools/registry/absence_claims.py --base origin/main`;
- `verify_receipt_artifacts.py`.

Their exit codes are in the PR.

## 9. Not changed

- **Unchanged:** the S1 covariance, C_model,5D, R00–R15, κ = 1, the route decision and FD-PLAN's statistics.
- **Not approved:** Stage G, F1, F1-W and any merge. No generator prediction was read.
- **Rules:** no GPU and no premium QOS.
- **Not proposed here:** a limitation, a paper statement or a publishability conclusion. Those are for the director to
  propose to Joseph.
