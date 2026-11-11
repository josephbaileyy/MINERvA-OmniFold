# ENS1 A1 stage-2 dry run: the receipt (job 61004211, 2026-11-08)

**Recorded by** the rounding-instability lane (`director-helper-3`). The run was made under `ENS1-BINDING-2.md`
(addendum A1) at M_A1 = `f4d2d7f3833834390b7b031df61ba1a5765e9900`. The director released stage 2 after stage 1 read
STAB_PASS (`../stage1-a1-analysis/`, #940), and gave a go on each connect's sha256.

**Result: the job COMPLETED, and the POST-RUN connect read PASS.**
- **Tasks:** all 7 dry tasks ended with rc 0, and every product exists.
- **The determinism control:** A7 MnvTune at k = 1 is bitwise identical to nominal at k = 1, on both `xsec_flat` and
  `xtrue_flat` (§3.2).
- **The truth vectors:** each truth's `xtrue_flat` is bitwise identical across its k: nominal k = 1–4, and W1 k = 1–2.
- **Moved rows:** every product and every task log records 0 moved rows.
- **The charge:** 0.1958 node-h, so stage 2 has now spent 0.1958 of its 46.0 cap.
- **The timing readout:** see the table below. The projection verdict is the director's.

**CITABLE FOR:**
- the dry run's execution: the connects' checks, the reference copies, the job and its charge;
- the determinism control and the truth-vector checks at the dry run;
- the timing readout that the director's projection gate (declaration §8) reads.

**NOT CITABLE FOR:**
- any bias reading, any stage-2 verdict or any product value. The products are listed by sha256 and stay on pscratch,
  unread here beyond the post-run's checks.
- the projection verdict. That gate is the director's, and this receipt records only its inputs.

## The SUBMIT connect (`connect/`)

**The scripts and their rcs:**
- `ens1_a1_s2_dry_submit.sh` is the copy the connect wrote, sha256 `5e140929…`.
- The launcher is `ens1_a1_s2_dry_submit_launch.sh`, `75e1388a…`.
- The launcher rc and ssh rc were both 0, read unpiped (`launch-submit.out.txt`).

**`connect-s2-dry.log.txt`** (login36, 2026-11-08T17:10:21Z–17:10:47Z, rc 0):
- **Its preconditions:** stage 1's analysis done file read 0, and `ens1_stage1.json` was at `7f5a9ce4…` with verdict
  STAB_PASS.
- **iris** (`iris.txt`): m3246 had charged 18,301.7 of its 20,000.0 allocation, so `balance_node_h=1698.3`. Half the
  balance is 849.1, and ENS1's and RS1's combined caps of 109.0 are below it. The director accepted these unchanged
  caps without a reprice.
- **The fence:** pass. `squeue-before.txt` is empty.
- **Stage 2's ceiling** (`sacct-before.txt`): no `ens1_a1_s2*` job since 2026-11-07, so stage 2 had spent 0. The dry
  run's 0.75 is within the 46.0 cap.
- **The shared inputs, unchanged since the records-only stat** (`../stage1-a1-analysis/stage2-inputs/`):
  - `inputs-identity.txt` lists type|inode|nlink|size|mtime|path for the npz, the bkg, `bank_sweep_5d_bkgaware/` and
    `bank_detector/`. Its 738 lines hash to `f533a9ad…`, the digest derived from that listing, with no stat errors.
  - Atime and ctime are excluded from the hash. The npz's and the bkg's atimes read 2026-11-08 15:42:54Z, from the
    stage-1 tasks' reads.
- **The pv-ladder ratio** `prep/ratios/L-5D-PV/nuwro.json`: the closure_nuwro truth's alternative, read through
  `--closure-ratio-dir`.
  - **The records-only stat for ruling 4 left this file out.** The director accepted adding it as a pinned input.
  - It was copied once with `dd iflag=noatime`. Its sha256 is `38e47eb6…`, the pin
    `fd_f0_regrade.RATIO["closure_nuwro"]`, and its atime was unchanged (1793889922, 2026-11-05).
  - The copy stays on pscratch and is not committed.
- **The deploy:**
  - HEAD is `f4d2d7f3` with 0 modified tracked files before and after.
  - 12 blobs and 7 sha256s were checked, with 0 mismatches.
  - Stage 1's 20 control-jitter copies are as at the dry connect.
- **FD-STAB's references for stage 2** (the director's rulings 3 and 5): 50 files were copied with `dd iflag=noatime`
  into `refs/runs/control/`:
  - the control base `stab_control_b-_j-.npz`;
  - the 31 jitters j21–j51;
  - the 18 closure lines §3.2 names. A7_mnvtune, the determinism duplicate of nominal, is copied and not judged by the
    analysis.

  The checks on them:
  - Each source's stat line (inode|nlink|size|mtime|atime|ctime) is in `refs-stat-before.txt` and
    `refs-stat-after.txt`, and the two files are identical.
  - Each source's atime was unchanged around its `dd`, and each copy is at its line in FD-STAB's SHA256SUMS
    (`e2c35e55…`).
  - `refs-SHA256SUMS` lists all 70 copies: stage 1's 20 plus these 50.
- **The copy window** (for ruling 5): 2026-11-08T17:10:26.364Z to 17:10:28.090Z.
- **The environment:** python 3.11.14, lightgbm 4.6.0, scipy 1.16.3, numpy 1.26.4.
- **The stage-2 queue:** the bound probe's `tasks --stage 2` wrote it.
  - `dry.tsv` is `b55370da…` with 7 tasks. It is copied here as `dry.tsv`.
  - shard0–5 hold 136/136/136/135/135/135 tasks, 813 tasks and 1,626 unfolds in all.
  - All seven files match `queue-sha256.expected`. Those digests were computed before the launch, by the same method
    that reproduces stage 1's seven cluster digests exactly.
- **The submission:**
  - sbatch rc 0, job 61004211.
  - The parsed `TimeLimit` was 00:45:00, as declared.

## The job (`log-dry/`, `connect/job-poll.txt`)

- **`sacct`** (`post/sacct-61004211.txt`): COMPLETED 0:0 on 1 node with 256 CPUs, nid004330, from 17:10:53Z to
  17:22:38Z. ElapsedRaw was 705 s, so the charge is **0.1958 node-h**.
- **`log-dry/DONE`:**
  - mode dry, stage 2, 7 tasks, 7 ended, rc 0;
  - job 61004211, pin `f4d2d7f3…`, teardown "".
  - There is no FAILED, `.failed` or `.teardown`, and no `runs-teardown/`. <!-- absence-ok: the run's own filesystem records, not a claim about a result -->
- **Lanes:** the job ran 8 lanes (`connect/ens1_a1_s2_dry_61004211.out.txt`). The job script started at 17:11:55Z, and all seven tasks
  started together at 17:11:57.5Z (`.start`).
- **Environment warnings:** `log-dry/env.log.txt` shows the same two missing `setup.sh` warnings as stage 1's.
- **`log-dry/SHA256SUMS`:** written at the job's end. It lists every file under `runs/` at that moment: stage 1's 2,017
  and these 7, so 2,024 in all.

| task | product (under `runs/closure/`) | sha256 |
|---|---|---|
| ens1_nominal_k001 | `nominal/ens1_nominal_k001_s991000.npz` | `12f92980fe6c1c46ff8dfbddc549700ea8e31d2f9978172dedf04eb3fca24aea` |
| ens1_nominal_k002 | `nominal/ens1_nominal_k002_s991000.npz` | `c7ecabde44bc779e436f5b8d637ef0a526d7dde21efa744de1ccdab811d59fb6` |
| ens1_nominal_k003 | `nominal/ens1_nominal_k003_s991000.npz` | `b5acd2ab45443f838738e8b3aa8afabeaaf7c347b73de75a89cb2f84ee09f1bd` |
| ens1_nominal_k004 | `nominal/ens1_nominal_k004_s991000.npz` | `59109e4344545d25f8963e8ab3860e9e7df928f338d4a48cf4d58e96f30b9cb5` |
| ens1_W1_k001 | `W1/ens1_W1_k001_s991000.npz` | `3ed1646efa82d880aacf566f55b79f5777ca13f083709d629ecc6ae577438031` |
| ens1_W1_k002 | `W1/ens1_W1_k002_s991000.npz` | `6163a96efa7f9e784c21021c8f65c84b0285e6c0529f823192278d7b56ed2abd` |
| ens1_A7_mnvtune_k001 | `A7_mnvtune/ens1_A7_mnvtune_k001_s991000.npz` | `8efd6c562f5db4872ed5937ba25cebdb7fc17917528d489eef82b388910a6b2a` |

The products stay at `/pscratch/sd/j/josephrb/ens1-a1-20261108/runs/closure/`. None is committed.

## The POST-RUN connect (`post/`)

**The scripts and their rcs:**
- `ens1_a1_s2_dry_postrun.sh` is the copy the connect wrote, sha256 `f6d16c50…`.
- The launcher is `ens1_a1_s2_dry_postrun_launch.sh`, `f0f7eedf…`.
- The launcher rc and ssh rc were both 0 (`launch-postrun.out.txt`).
- `connect-postrun.log.txt` ran on login21, 2026-11-08T17:25:53Z–17:26:18Z, rc 0.

**The checks:**
- **The fence:** pass, and the job was out of the queue.
- **sacct:** COMPLETED on 1 node, under its name `ens1_a1_s2_dry`. The charge is 0.1958 node-h, within the 46.0 cap.
- **DONE:** as above. The deploy is unmodified, and the probe is at sha256 `807c40d3…`.
- **The products:** all 7 paths came from the bound probe's `expect` (`expect-*.txt`, `products.txt`), and each is at
  its line in `log-dry/SHA256SUMS`.
- **`read.py`** (sha256 `f0a57137…`), run under the sourced environment (Python 3.11.14), wrote `s2-dry-read.json`
  (sha256 `b5f7127f…`) with the verdict **PASS** and no failures. It imports the bound probe from the deploy for its
  `SCHEMA`, `INTERNAL_BASE`, `DETERMINISM` and `DRY2`.
  - **The blocks:** each product's meta `ens1` block has:
    - schema `ens1-ensemble-estimator/1`, mode `closure`, its k, internal seed 10000 + k and its truth;
    - `moved_rows` 0 in all four classes;
    - `code_sha256` equal to the probe's `807c40d3…`;
    - `closure_dtype_requested` recorded as `float32` ×7. This is the dtype the runner asks for. The bound rebinding fits
      in float64 (declaration §2, bound in §9).
  - **The products' own meta:**
    - every product has pseudo seed 991000, expectation true and MC fraction half;
    - every hypothesis is at sha256 `ceea00e7…`;
    - W1's alternative is at `2a208df9…`, the `fd_f0_regrade.RATIO["W1"]` pin;
    - each k's coordinate digest is the same across truths, as the internal jitter depends only on k.
  - **The logs:** each task log has exactly one `[ens1] grid membership moved rows {…}` line, all zero. Each also has
    exactly one runner line `{"out", "rc", "seconds"}`, naming its product, with rc 0.
  - **The determinism control:** A7_mnvtune k = 1 against nominal k = 1. `xsec_flat` and `xtrue_flat` are float64, shape
    (65856,), on both sides, and **bitwise identical**.
  - **The truth vectors:** `xtrue_flat` is **bitwise identical** across nominal k = 1–4 and across W1 k = 1–2.

**The timing readout** for the director's projection gate. Declaration §8 requires 34 × t + 300 s ≤ 6.75 h, which
means t ≤ 705 s.
- The closure runner logs its time as `seconds` (`s5p_nullexp.py:354`). The product's meta records the same value as
  `seconds_unfold`, measured from the runner's `t0`, so it includes the build.
- The two are equal for every task here.
- The task wall runs from `.start` to `.end`.

| task | runner seconds | meta seconds_unfold | task wall (s) |
|---|---|---|---|
| ens1_nominal_k001 | 572.788 | 572.788 | 603.2 |
| ens1_nominal_k002 | 514.646 | 514.646 | 544.1 |
| ens1_nominal_k003 | 523.244 | 523.244 | 553.8 |
| ens1_nominal_k004 | 503.558 | 503.558 | 533.1 |
| ens1_W1_k001 | **603.117** | **603.117** | **634.5** |
| ens1_W1_k002 | 533.075 | 533.075 | 564.9 |
| ens1_A7_mnvtune_k001 | 487.760 | 487.760 | 517.3 |

- **The gate reads meta `seconds_unfold`** (the director's ruling). Its maximum is **603.117 s**. The projected shard
  wall is 34 × 603.117 + 300 s = **5.779 h**.
- **The largest of the three numbers** is the task wall, 634.5 s. The same projection with the wall in place of t gives
  **6.076 h**.
- The verdict on these inputs is the director's.
- Stage 1's full run had a slow tail: its maximum seconds_unfold was 779.9 s, against 537.9 s at its dry run
  (`../stage1-a1/`). Seven dry tasks cannot show a tail of that kind.

## The ledger and renames

**The ledger:** `fd/LEDGER.tsv` has three rows for this run: the SUBMIT connect, the job and the POST-RUN connect.

**Renames:** git ignores `*.log`, `*.out` and `*.err`, so those files carry a `.txt` suffix here. Their contents are
unchanged.

**Empty files:** `connect/squeue-before.txt`, `connect/inputs-identity.err.txt` and `post/squeue-before.txt` are empty,
as they were on pscratch.

**Next:** the full stage 2 needs this receipt, the director's projection verdict and a further go. The director rules
the full-run fence allowances with that go.
