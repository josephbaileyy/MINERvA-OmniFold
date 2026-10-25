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
  | — NuWro | 4 | 0 of 64 | 2.91 | 1 of 4 | 0.04 |
  | — GENIE MEC | 2 | 0 of 32 | 1.46 | 0 of 2 | 0.02 |
  | — GiBUU | 2 | 4 of 32 | 1.46 | 2 of 2 | 0.02 |
  | non-vertex | 2 | 0 of 32 | 1.46 | 1 of 2 | 0.02 |
  | prior | 2 | 0 of 32 | 1.46 | 0 of 2 | 0.02 |
  | all graded: ruling 2's denominator line, "read by group, never pooled". It reads 192 and 12, not 288 and 18, because control 7 failed (declaration §7 item 5) | 12 | 4 of 192 | 8.74 | 4 of 12 | 0.12 |

  - The Gaussian references are context only, because b is a deterministic bias.
  - The per-family references are computed here, not read from the readout: 16 × truths × 0.0455, and truths ×
    0.01.
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
  <!-- absence-ok: the session's deploy script ran `ls -d $B` on login37 at 2026-10-25T21:53Z before mkdir, and it would have stopped had $B existed. That line is not in deploy.log, so the claim rests on the session record and on the declaration-time `ls -d` (2026-10-25), not on a committed receipt -->

## 2. The HPSS copy of the `f4` products (declaration §2.2, binding §4 item 2)

**Before:** `hpssquota` read 422.78 of 512.00 GiB used, so 89.22 GiB was free, against the bound minimum of 1 GiB
(`receipts/hpssquota-before.txt`).

**What ran:** the unchanged `stage0_preserve.sh` (`27ccc04a…`) over `fd/F4-PRESERVE-INVENTORY.sha256`. It ran
detached under `timeout 1500` on login37, from 21:59:24Z to 21:59:29Z. The receipts are `receipts/preserve.out`,
`preserve.log`, `paths.list` and `stage0-inputs.tar.sha256`.

**The steps:**
- **Control 0, shell form:** "inventory verified: 80 files".
- **The tar:** sha256 `14e2957facea180051cd086b11ad8a7075a50385e3909ede95ac56db3aeb0ead`, 14,888,960 B.
  - tar printed "Removing leading `/' from hard link targets". GNU tar prints this when it strips the leading `/` from
    names given with absolute paths. Each of the 80 inventoried files has link count 1 (`receipts/post-run.txt`), so
    no hard link was archived.
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
- **Cleanup:** as declared, `$B/preserve/stage0-inputs.tar` was deleted after PASS, and the retrieve directory is empty
  (`receipts/post-run.txt`, 22:16:40Z).
- **The 80 products are untouched:** the re-grade's control 0 ran after the copy and passed.
- **Quota:** `hpssquota` still reads 422.78 GiB, both right after the copy and 17 minutes later
  (`receipts/hpssquota-after.txt`, `post-run.txt`).
  - The three files total 14,901,732 B, about 0.014 GiB, so the display, with its 0.01 GiB step, should have moved.
  - The likelier reason is that HPSS quota accounting lags **(inference)**.
  - The copy itself is shown by hashverify, the retrieval check and `hsi ls -l`.
- **The FD-PLAN §6 purge row for `f4`** ("HPSS copy: **no**") is now discharged.

## 3. The re-grade (declaration §2.3, binding §4 item 3)

**What ran:** the exact bound argv, under `timeout 1125` on login37, from 21:59:49Z to 22:00:33Z. It took 44 s
against the 15-minute projection.
- It exited 0 (`receipts/f0.out`, last line `rc=0`). `receipts/f0.err` is empty.
- It wrote `$B/fd_f0_readout.json` (sha256 `6e7d718bd393dd0600e974d0ce9b5c389486890cb7112550b22289008d6d312b`,
  84,840 B), committed as [`fd/readout/fd_f0_readout.json`](fd/readout/fd_f0_readout.json) and re-measured equal.
- It wrote `$B/fd_f0_experiments.npz` (sha256 `7384c6518aa0f59bd4964170fcc9b652f1c31958f422f1e1b597cd3e59219ad9`,
  1,068,642 B, by `stat` in `receipts/post-run.txt`). That equals the readout's `table_sha256`. It stays on pscratch
  (§6).

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
  - The upward lean from the calibration part, about n/(n − 17) at these B_eff, is 5.6–7.5 %. For the gating pair it
    is 6.6 % (MnvTune) and 7.5 % (GENIE CV) **(arithmetic)**.
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

Every graded truth not listed above, and every blank cell, has none.

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

**Cells with |z| > 2 under row 6's other variants:**
- in-sample: P2g has R07;
- model-only:
  - P1r: R10;
  - P2r: R01, R07, R08, R12;
  - P1g: R01, R06, R10, R12;
  - P2g: R01, R07, R12;
  - P3r and P3g: none.

**A naming note on the readout.** For these ungraded truths the readout still fills the verdict-shaped fields inside
`grade`: `p_lt_0.01` is true for P1r, P2r, P1g and P2g, and `cells_abs_z_gt_2` holds R07 for P2g. Each is labelled
"descriptive and ungraded", has `listed` false, and appears in no `triggers` count. Read them with that label.

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
- `f0-start.txt`, `f0.out`, `f0.err`;
- `post-run.txt`: the `$B` listing, the table's size, the link counts of the 80 files, and the quota at 22:16:40Z.

**[`fd/receipts-prebinding/`](fd/receipts-prebinding/)** holds the pre-binding evidence: the control-2 meta probe (`metaprobe.py`, `metaprobe-40427c14.log`) and the cluster test runs at `7d7dac1d`, `dae47273` and `40427c14`, with a `SHA256SUMS` matching the pscratch originals. The `[F0]` count lines in the test logs come from the synthetic fixture, not from the real run.

`deploy-tests.log` holds the synthetic tests' own output lines, which carry fixture values only.

**[`fd/LEDGER.tsv`](fd/LEDGER.tsv)** has two rows:

| step | host | wall | rc | node-h |
|---|---|---|---|---|
| the HPSS copy | login37 | 5 s | 0 | 0 |
| the re-grade | login37 | 44 s | 0 | 0 |

**State on pscratch:**
- `$B` holds the deploy, the logs, the readout, the table, an empty `tmp/`, and `preserve/` (`paths.list`,
  `preserve.log`, the tar's `.sha256` and an empty `retrieve/`);
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

**One gate needs the director: the results index.**
- **The problem:** `.githooks/pre-commit`, run standalone at this commit, fails "results index fresh+complete". The
  committed readout is a result receipt (25 metric values), and `RESULTS-INDEX.tsv` has no row for it.
- **The fix it names:** `tools/registry/results_index.py --write`. That regenerates `RESULTS-INDEX.tsv` and
  `RESULTS-POPULATION.tsv`, and also `docs/analysis-note/records_results_index.tex`.
- **What that change contains:** in a scratch worktree at this commit, it adds 25 index rows and one population row.
  In the `.tex` file it changes the receipt and row counts and adds summary lines for the readout's unattributed
  `bias`, `bias_uncorrected` and `closure_floor_max_abs` keys. These are relative fake-data quantities only.
- **One thing to know before regenerating:** the regenerated `.tex` adds one `bias` summary row that pools all 18
  truths' biases, row 6 included, into a single min / median / max (−0.171 / 0.000177 / 0.3604). Ruling 2 says
  "never pooled", and row 6 is descriptive. That rendering is the generator's, not F0's.
- **Why I have not committed it:** `docs/analysis-note/**` is outside this session's edit scope. Regenerating it, or
  ruling otherwise, is for the director.
- **Why both commits printed "13 checks passed":** this worktree's `core.hooksPath` points at the shared checkout's
  `.githooks`. That `pre-commit` (`7b40aeaa…`) is older than this tree's (`1d03595e…`) and has no results-index check.
  The gate fails when the tree's own hook is run.

## 9. Not changed

- **Unchanged:** the S1 covariance, C_model,5D, R00–R15, κ = 1, the route decision and FD-PLAN's statistics.
- **Not approved:** Stage G, F1, F1-W and any merge. No generator prediction was read.
- **Rules:** no GPU and no premium QOS.
- **Not proposed here:** a limitation, a paper statement or a publishability conclusion. Those are for the director to
  propose to Joseph.

## 10. Review disposition

An independent read-only review of this report (`de6c1f10`) worked in both directions. It recomputed every number
from the readout and receipts and found all of them equal. It checked that no number is of cross-section magnitude:
the smallest non-zero in the readout is a p of 5.3e-30. It also checked that every element binding §4 item 6 requires
is present. It found nothing MATERIAL.

Its nine MINOR points are all accepted:
1. **The quota explanation.** It is now the inference of accounting lag.
2. **The lean range.** It is now 5.6–7.5 %.
3. **The "every truth" sentence.** It is now scoped to graded truths, and row 6's variant cells are listed.
4. **The denominator line.** It is now labelled 192 and 12, and the label says why.
5. **Claims without a receipt.** `receipts/post-run.txt` now records the tar deletion, the empty retrieve directory,
   the table size and the link counts of the 80 files (all 1). The `$B` absence waiver now says where its evidence
   is.
6. **The per-family Gaussian references.** They are now added.
7. **§8.** It now gives the hooksPath reason why the commits passed, and the pooled `bias` row in the regenerated
   `.tex`.
8. **The verdict-shaped fields on row 6.** They are now noted in §5.2.
9. **The pscratch listing.** It is now complete.
