# ENS1 A1 stage-2 full run: the receipt (jobs 61004986–61004991, 2026-11-08)

**Recorded by** the rounding-instability lane (`director-helper-3`). The run was made under `ENS1-BINDING-2.md`
(addendum A1) at M_A1 = `f4d2d7f3833834390b7b031df61ba1a5765e9900`.
- The director gave a go on the SUBMIT connect's sha256 after the stage-2 dry run's receipt (`../stage2-dry-a1/`,
  #942) and the projection verdict. Both rulings are quoted verbatim below.
- The director gave a separate go on the POST-RUN connect's sha256.

**Result: all six shard jobs COMPLETED, and the POST-RUN connect read PASS.**
- **Tasks:** 813 tasks (1,626 unfolds) ended. Every shard's DONE reads rc 0.
- **Products:** all 1,626 shard products and the dry run's 7 exist, so stage 2 has 1,633 closure products.
  `runs/` holds 3,650 files, and stage 1's 2,017 are unchanged.
- **Gate E5:** every closure product records 0 moved rows on all four inputs.
- **One teardown:** task `ens1_stage0c_gibuu_k057` (shard 1). It exited 129 after both its products were written. The
  guard moved them aside, the task re-ran with exit 0, and the re-run's products are the ones used. The details are
  below.
- **The charge:** 32.9389 node-h, so stage 2 has now spent 33.1347 of its 46.0 cap.

**CITABLE FOR:**
- the full run's execution: the SUBMIT connect's checks, the six jobs and their charge;
- each shard's completion record and product digests;
- gate E5 over all 1,633 closure products;
- the one teardown and its record;
- the timing readout.

**NOT CITABLE FOR:**
- any ENS1 reading: the stage-2 verdict belongs to the ANALYSIS connect and is receipted in
  `../stage2-a1-analysis/`;
- any product value. The products are listed by sha256 and stay on pscratch, unread here beyond the post-run's checks
  of their meta blocks.

## Director's rulings before launch

The supervisor noted that the projection verdict and the go existed only in correspondence. The director asked for both
to be quoted here verbatim. The msg ids `5c33ef65` and `0c37f5ee` are the director's ids for these messages. The
receive times are the lane's transcript timestamps. The SUBMIT connect started at 2026-11-08T17:54:34Z
(`connect/connect-s2-full.log.txt`), after both.

**1. The projection verdict and the fence ruling** (director's msg `5c33ef65`, received 2026-11-08T17:43:09.058Z):

> director: ENS1, the stage-2 dry run reads PASS. I'm merging #942 on CI now.
>
> **The projection gate: PASS.** The max meta seconds_unfold is 603.117 s, so 34 × 603.117 + 300 = 5.779 h, inside the
> 6.75 h line. Even the task wall gives 6.076 h.
>
> Your ×1.45 tail caveat is noted, and here's how I read it. A lane's wall is the sum of its 34 unfolds, and stage 1's
> shards landed within 2% of the dry-run projection from t, even with that tail. So with 7:30:00, the margin is
> adequate.
>
> If any shard times out, the stage is INCOMPLETE. It comes to me unrepaired, with no resume, per §8.
>
> **Fence ruling for the full SUBMIT and its POST-RUN: unchanged, rs1_\*/ens1_\* only.** Nothing else is allowed.
> - Band-diagnosis P0, which is stat-only, expects to find its in-place inputs shared with yours: of_inputs_5d.npz, the
>   s5c bkg_dump and bank_detector. So its P1–P3 are sequenced after your stage-2 full ends.
> - FD-PRR (prr_\*) also comes after you.
> - LL5D (ll5d_\*) has no code bound yet.
> - So no other family enters the queue during your window. If that changes, I'll tell you before it happens.
>
> Draft the full SUBMIT with that fence and send me its sha and path.

**2. The go on the SUBMIT connect** (director's msg `0c37f5ee`, received 2026-11-08T17:54:25.141Z):

> director: ENS1, **go for the stage-2 full SUBMIT**: `ens1_a1_s2_full_submit.sh`
> 47d9f91460aae9933f868821c9f946b064f4105c4787a1dcc7f3e8084fae5e67, launcher 05ab441d…. My local shas match
> (13,523 B), and TLIMIT is 7:30:00 / 07:30:00.
> - The fence is as ruled. The all-or-none sbatch with scancel is good.
> - The ceiling is 45.1958 ≤ 46.0.
> - Send me the POST-RUN connect's sha before the shards end. A timeout or INCOMPLETE comes to me unrepaired.
> - **For your window:** band-diagnosis P0 read BRANCH SHARED on all 34 of its in-place sources, so it runs after you.
>   No fd1b_bdg_, ll5d_ or prr_ job will be queued until your post-run is done.

## The SUBMIT connect (`connect/`)

**The scripts and their rcs:**
- `ens1_a1_s2_full_submit.sh`, sha256 `47d9f914…` (13,523 B). The copy the connect wrote to `logs-s2/` on pscratch is
  byte-identical.
- The launcher is `ens1_a1_s2_full_submit_launch.sh`, `05ab441d…`.
- The ssh rc was 0, read unpiped (`launch-submit.out.txt`).

**`connect-s2-full.log.txt`** (login36, 2026-11-08T17:54:34Z–17:54:45Z, rc 0):
- **Refusals:** none fired. The stage-2 dry DONE is at `7da1740a…` (job 61004211, 7/7 rc 0, teardown ""). The dry
  post-run's done is 0, and `s2-dry-read.json` is `b5f7127f…`, verdict PASS.
- **iris, the actual reading** (`iris-full.txt`): m3246 had charged 18,302.9 of its 20,000.0 allocation, so
  `balance_node_h=1697.1`. Half the balance is 848.5, and the combined caps of 109.0 are below it.
- **The fence:** pass. `squeue-before-full.txt` is empty.
  - The line reads "0 jobs; none outside rs1_*, no ens1_*": that is the script's wording for an empty queue.
- **The charge ceiling** (`sacct-stage2-before.txt`):
  - sacct read exactly the dry run's `61004211|ens1_a1_s2_dry|COMPLETED|705|1`.
  - Stage 2 had spent 0.1958 node-h. Adding six 7.5-hour limits gives 45.1958, within the 46.0 cap.
  - `sacct-before-full.txt` is the wider history read, with every earlier job of the window.
- **The shared inputs** (stat only):
  - `inputs-identity-full.txt` has 738 lines with sha256 `f533a9ad…`, the value sent. `inputs-identity-full.err.txt`
    is empty.
  - The pv-ladder `nuwro.json` is at its pin `38e47eb6…`. Its atime is the same before and after the one noatime copy.
- **The deploy (re-checked):**
  - HEAD is `f4d2d7f3` with 0 modified tracked files before and after.
  - 12 blobs and 7 sha256s were checked, with 0 mismatches.
  - The 70 reference copies match the dry connect's (`refs-SHA256SUMS-full`).
  - `deploy-status-full.txt` records the 2 `porcelain --ignored` lines: the two `__pycache__/` directories.
- **The stage-2 queue:**
  - `dry.tsv` and shard0–5 match `queue-sha256-full.expected` (`queue-sha256-full.txt`).
  - The shards hold 136/136/136/135/135/135 tasks.
- **The submission:** six sbatch calls at 17:54:39Z, each rc 0 (`submit-s2-full-*.out.txt`). Each job's parsed
  `TimeLimit` is 07:30:00, as declared. `s2-full.jobids` lists the six.

  | shard | job |
  |---|---|
  | 0 | 61004986 |
  | 1 | 61004987 |
  | 2 | 61004988 |
  | 3 | 61004989 |
  | 4 | 61004990 |
  | 5 | 61004991 |

**The poll** (`job-poll.txt`): a read-only sacct every 15 minutes.
- All six were PENDING at 17:55:10Z and RUNNING by 18:10:14Z.
- Five had COMPLETED at 23:27:06Z.
- All six had COMPLETED at 23:42:10Z.

## The jobs (`jobs/`, `log-shard*/`)

- **`sacct`** (`post/sacct-full.txt`): all six ended COMPLETED 0:0 on 1 node with 256 CPUs.
  - sacct prints Start and End in cluster-local time (UTC−8), so the UTC times in the table are those plus 8 h.
  - The job `.out` files print their own UTC start and queue-end lines.

  | shard | job | node | start (UTC) | end (UTC) | ElapsedRaw (s) | node-h |
  |---|---|---|---|---|---|---|
  | 0 | 61004986 | nid004676 | 17:55:13Z | 23:26:25Z | 19,872 | 5.5200 |
  | 1 | 61004987 | nid004710 | 17:55:13Z | 23:27:01Z | 19,908 | 5.5300 |
  | 2 | 61004988 | nid004715 | 17:55:13Z | 23:23:26Z | 19,693 | 5.4703 |
  | 3 | 61004989 | nid004720 | 17:55:13Z | 23:19:32Z | 19,459 | 5.4053 |
  | 4 | 61004990 | nid004732 | 17:55:13Z | 23:24:06Z | 19,733 | 5.4814 |
  | 5 | 61004991 | nid004747 | 17:55:13Z | 23:27:08Z | 19,915 | 5.5319 |

  - The sum is 118,580 s, or **32.9389 node-h**.
- **`log-shard*/DONE`:** each reads mode shard, stage 2, its own shard number and job, pin `f4d2d7f3…`, ended = tasks
  and rc 0.
  - Shards 0 and 2–5 have teardown "".
  - Shard 1 has teardown "ens1_stage0c_gibuu_k057 ", which matches its one `.teardown` record (below).
- **Lanes:** each job ran 8 lanes (`jobs/*.out.txt`).
- **Environment warnings:** `log-shard*/env.log.txt` shows the same two missing `setup.sh` warnings as the dry run's,
  then `lightgbm 4.6.0 numpy 1.26.4 python 3.11.14`. All six files are identical.
- **`log-shard*/SHA256SUMS`:** each is written at shard end and lists every file under `runs/` at that moment.
  - The counts are 3,648 / 3,649 / 3,644 / 3,633 / 3,646 / 3,650.
  - Shard 5 ended last. Its list holds all 3,650 files and is byte-identical to the post-run's `post/runs-SHA256SUMS`
    (`ad6b364c…`).
- **The task logs:** the 813 tasks' `.log`, `.time`, `.start` and `.end` files, plus the teardown task's one
  `.time.rerun`, stay on pscratch under `stage2/log-shard*/`. That is 3,253 files. `log-index/task-logs-SHA256SUMS`
  (`e759f50c…`) lists them by sha256.
  - That list was computed on pscratch. Unlike stage 1's, it was not cross-checked against a pulled copy.
  - The post-run read every task's `.log`, `.start` and `.end` (below). It did not read the `.time` files.

The products stay at `/pscratch/sd/j/josephrb/ens1-a1-20261108/runs/`. None is committed.

### The teardown: `ens1_stage0c_gibuu_k057` (shard 1)

The guard is `nd-unfolding/sbatch_ens1.sh:49-79` at `f4d2d7f3` (RS1-BINDING-2 addendum A1, the director's ruling 5 for
ENS1).
- **What the guard does:** a task whose process exits non-zero after every product it declares exists is a "teardown
  crash".
  - Its products move to `runs-teardown/<id>/`, and it is re-run once.
  - The re-run's products are used.
  - A comparison of `xsec_flat` and `xtrue_flat` between the two runs is recorded.
  - A second crash, or a crash before every product exists, writes `<id>.failed`.

**The task's record:**
- **The task:** the GiBUU truth (`stage0c_gibuu`), k = 57 and 58. The GiBUU readout is descriptive under the
  declaration's §5.3 (printed and used by no criterion), but its products are counted among the 1,633.
- **The director's ruling on it:** accepted under the director's teardown ruling (ruling 5). The re-run's products are the
  ones used, and the moved copies stay in `runs-teardown/` as evidence.
- **The first run:** it started at 19:27:47Z (`.start`).
  - The GNU time record `tasks/ens1_stage0c_gibuu_k057.time` (on pscratch) reads "Command exited with non-zero status
    129", wall 23:20.90. The file is dated 19:51:08Z.
  - Both products had been written before that, at 19:40Z and 19:49Z (the mtimes of the moved files).
- **The record:** `log-shard1/ens1_stage0c_gibuu_k057.teardown` reads:

  ```
  exit=129 after all 2 products were written
  ens1_stage0c_gibuu_k057_s991000.npz bitwise_identical
  ens1_stage0c_gibuu_k058_s991000.npz bitwise_identical
  ```

  - "bitwise_identical" means the guard found `xsec_flat` and `xtrue_flat` equal, array for array
    (`sbatch_ens1.sh:73-79`). It is not a whole-file comparison.
  - The whole files differ. The moved copies are `26a1f767…` and `adf52382…` (`post/runs-teardown-SHA256SUMS`). The
    re-run's products in `runs/` are `46282870…` and `e0eb36c7…` (`post/runs-SHA256SUMS`).
- **The re-run:** `tasks/ens1_stage0c_gibuu_k057.time.rerun` reads exit status 0, wall 19:33.72. The task's `.end` is
  20:10:53Z.
  - Its wall from `.start` to `.end`, 2,586.3 s, covers both runs. It is the run's maximum task wall.
  - The task log holds 4 runner lines, 2 per run. Its last two name both products with rc 0.
- GNU time reports 129 as the command's exit status ("exited with non-zero status"), not as termination by a signal,
  and its "Signals delivered" line reads 0. The lane has not investigated the cause and makes no claim about it.
- No `.failed` file exists in any shard. <!-- absence-ok: the post-run's check of the shard log directories (read.py "odd" list), not a claim about a result -->
- **The teardown does not bear on the verdict.** The re-run's `xsec_flat` and `xtrue_flat` equal the first run's
  array for array, so the products the ANALYSIS reads are the same whichever run produced them.

### The GiBUU truths and the stage-2 verdict

`stage0c_gibuu` is the one truth at which the ANALYSIS (separate receipt, `../stage2-a1-analysis/`) read E₉₆ worse.
The director confirmed that the GiBUU truths are judged by "no worse", on these two sentences:
- `ENS1-DECLARATION.md` §5.3 (`:220`, `:225-226`): "**PASS:** no worse at all 17 truths." and "**The GiBUU
  readout** (A7 GiBUU and Stage 0c GiBUU biases, per estimator) is printed and used by no criterion (FD-STAB §5.3)."
- `FD-STAB-DECLARATION.md` §5.3 (`:206-209`): "**Neither the bias criterion beyond "no worse", nor any other
  criterion, nor the tie-break may use them**".

So "no worse" judges both GiBUU truths, and only their bias magnitudes are descriptive. The declaration states the
familywise rate of a false "worse" over 17 truths × 2 metrics (`ENS1-DECLARATION.md:216-217`): "about 0.5 % with
correctly estimated SDs, at most about 4.5 % if both are underestimated by their full factors."

## The POST-RUN connect (`post/`)

**The scripts and their rcs:**
- `ens1_a1_s2_full_postrun.sh` is the copy the connect wrote, sha256 `b725acce…`.
- The launcher is `ens1_a1_s2_full_postrun_launch.sh`, `6eda72d6…`.
- The launcher rc and ssh rc were both 0 (`launch-postrun.out.txt` holds the ssh rc line).
- `connect-postrun.log.txt` ran on login38, 2026-11-08T23:43:27Z–23:43:56Z, rc 0. It ran after all six jobs were
  COMPLETED in sacct (23:42:10Z poll).

**The checks:**
- **The fence:** pass (`squeue-before.txt` is empty), and none of the six jobs was queued.
- **sacct:** each job COMPLETED on 1 node under its own name `ens1_a1_s2_<i>`.
  - The charge is 0.1958 + 32.9389 = 33.1347 node-h, within the 46.0 cap.
- **The deploy and the receipted files:**
  - HEAD is `f4d2d7f3` with 0 modified tracked files.
  - The probe is at sha256 `807c40d3…`.
  - The stage-2 dry run's DONE is at `7da1740a…`, and its SHA256SUMS is at `893865c7…`, the receipted file.
  - Stage 1's final listing is at `e96d07da…`.
  - These checks print one line together when they pass.
- **`runs-teardown/`:** it exists, with the 2 files listed in `runs-teardown-SHA256SUMS`.
- **`read.py`** (sha256 `911649bd…`), run under the sourced environment (Python 3.11.14), wrote `s2-full-read.json`
  with the verdict **PASS** and no failures.
  - **The JSON stays on pscratch** at `/pscratch/sd/j/josephrb/ens1-a1-20261108/post-s2-full/s2-full-read.json`,
    sha256 `b0dcdb271c1823f5213a4efc4cd815f39101e7b42aa2d6214bfd1c4115083168`. It is not committed, on the director's
    ruling (option C).
    - **Why:** its per-task `timing` map is keyed by task id, and the `ens1_closure_nuwro_k###` ids match
      `results_index.py`'s "closure" token. The index would have read 144 timing values as closure results.
    - `read.py` and the connect script are committed here, so the file can be regenerated.
  - **Its printed summary**, verbatim from `connect-postrun.log.txt`:

    ```
    {"verdict": "PASS", "failures": [], "n_failures": 0, "products": {"read": 1633, "moved_rows_nonzero": 0, "block_mismatch": 0, "code_mismatch": 0, "dtype_unrecorded": 0}, "n_files": 3650, "n_stage1": 2017, "teardowns": ["ens1_stage0c_gibuu_k057"], "runs_teardown_files": 2, "timing": {"unfolds": 1626, "runner_lines": 1628, "seconds_max": 792.827, "seconds_median": 523.771, "meta_seconds_unfold_n": 1626, "meta_seconds_unfold_max": 792.827, "meta_seconds_unfold_median": 523.6510000000001, "meta_seconds_unfold_over_705": 42, "task_wall_max": 2586.3, "shard_wall_s_max": 19915, "shard_wall_h_max": 5.532, "projected_h_from_dry": 5.779, "limit_h": 7.5}, "shards": {"0": {"tasks": 136, "job": "61004986", "elapsed_raw": 19872}, "1": {"tasks": 136, "job": "61004987", "elapsed_raw": 19908}, "2": {"tasks": 136, "job": "61004988", "elapsed_raw": 19693}, "3": {"tasks": 135, "job": "61004989", "elapsed_raw": 19459}, "4": {"tasks": 135, "job": "61004990", "elapsed_raw": 19733}, "5": {"tasks": 135, "job": "61004991", "elapsed_raw": 19915}}}
    ```

  - **What it checked:**
  - **The DONEs:** each shard's DONE equals its expected record, and its teardown list matches its `.teardown` files.
    There are no `FAILED`, `STOP` or `.failed` files.
  - **The products:**
    - Every expected product (from the bound probe's `expected_outputs`) is at its line in its own shard's SHA256SUMS,
      unchanged now.
    - The dry run's seven are at their lines in the receipted dry SHA256SUMS, unchanged.
    - The queues' products are exactly the 1,633 declared: 17 truths × k = 1–96, plus `A7_mnvtune` k = 1.
    - Stage 1's 2,017 products are all at their lines in stage 1's final listing.
    - `runs/` holds exactly those 3,650 files.
  - **E5 in the products:** each of the 1,633 closure products' meta `ens1` blocks has
    `moved_rows == {MCgen: 0, MCreco: 0, measured: 0, bkg_reco: 0}`.
    - Each block's schema, mode, k, internal seed and truth match its name.
    - Each block's `code_sha256` is the probe's `807c40d3…`.
    - Each block records `closure_dtype_requested`.
    - The counts are `moved_rows_nonzero 0`, `block_mismatch 0`, `code_mismatch 0` and `dtype_unrecorded 0`.
  - **E5 in the logs:** each task log has exactly one `[ens1] grid membership moved rows {…}` line per unfold, all zero.
    For the teardown task, one or two per unfold are allowed.
  - **The runner lines:** each task's last `{"out", "rc", "seconds"}` lines name its products with rc 0. That is 1,626
    final lines, out of 1,628 in all (the teardown task's first run adds 2).
  - **The teardown:** the record names both products as bitwise_identical. No `.failed` file sits beside it. The 2
    files in `runs-teardown/` are exactly its products.

**The timing readout** (from the printed summary above; the director's projection was 34 × 603.117 + 300 s = 5.779 h):
- **meta seconds_unfold over the 1,626 shard products:** median 523.651 s, **max 792.827 s**. 42 exceeded 705 s.
- **Runner-line seconds over all 1,628 lines:** min 403.704 s, median 523.771 s, p90 642.0 s, p99 727.4 s, max
  792.827 s (`ens1_closure_nuwro_k069`, shard 1).
  - The lines over 705 s fall 7 / 8 / 8 / 8 / 7 / 4 across shards 0–5.
  - The lane computed these figures from the per-task `timing` in its pulled copy of the JSON (`b0dcdb27…`). They
    are not in the printed summary.
- **Max task wall:** 2,586.3 s, the teardown task across both its runs.
- **Max shard wall (ElapsedRaw):** 19,915 s = **5.532 h**, under both the 5.779 h projection and the 7.5 h limit.
- The dry run's maximum was 603.117 s. The per-unfold excess shows only as a spread in task time. No shard approached
  its limit.

## The ledger and renames

**The ledger:** `fd/LEDGER.tsv` has eight rows for this run: the SUBMIT connect, the six jobs and the POST-RUN connect.

**Renames:** git ignores `*.log`, `*.out` and `*.err`, so those files carry a `.txt` suffix here. Their contents are
unchanged.

**Empty files:** `connect/squeue-before-full.txt`, `connect/inputs-identity-full.err.txt` and `post/squeue-before.txt`
are empty, as they were on pscratch.

**Next:** the director gave the go on this readout for the ANALYSIS connect (`ens1_a1_s2_analysis.sh`, `c5ee4378…`). Its
receipt is `../stage2-a1-analysis/` (verdict BIAS_WORSE, worse at `stage0c_gibuu`).
