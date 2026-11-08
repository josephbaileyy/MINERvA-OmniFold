# ENS1 A1 stage-1 full run: the receipt (jobs 60995093–60995098, 2026-11-08)

**Recorded by** the rounding-instability lane (`director-helper-3`). The run was made under `ENS1-BINDING-2.md`
(addendum A1) at M_A1 = `f4d2d7f3833834390b7b031df61ba1a5765e9900`.
- The director gave a go on the SUBMIT connect's sha256 after the dry rerun's receipt (`../stage1-dry-a1/`, #932) and
  the projection verdict.
- The director gave a separate go on the POST-RUN connect's sha256.

**Result: all six shard jobs COMPLETED, and the POST-RUN connect read PASS.**
- **Tasks:** 1,004 tasks (2,008 unfolds) ended with rc 0.
- **Products:** all 2,016 stability products and the F₆₄ product exist, so `runs/` holds 2,017 files.
- **Gate E5:** every product records 0 moved rows on all four inputs.
- **Teardowns:** none.
- **The charge:** 38.4544 node-h, so stage 1 has now spent 38.9166 of its 55.0 cap.

**CITABLE FOR:**
- the full run's execution: the SUBMIT connect's checks, the six jobs and their charge;
- each shard's completion record and product digests;
- gate E5 over all 2,017 products;
- the absence of any teardown;
- the timing readout.

**NOT CITABLE FOR:**
- any ENS1 reading: the stage-1 verdict (STAB_PASS / STAB_FAIL / UNINFORMATIVE) belongs to the ANALYSIS connect, which
  has not run; <!-- absence-ok: a workflow status (the next connect is not yet launched), not a claim about a result -->
- any product value. The products are listed by sha256 and stay on pscratch, unread here beyond the post-run's checks
  of their meta blocks.

## The SUBMIT connect (`connect/`)

**The scripts and their rcs:**
- `ens1_a1_full_submit.sh`, sha256 `7ec3dd9e…`. The copy the connect wrote to `logs/` on pscratch is byte-identical.
- The launcher is `ens1_a1_full_submit_launch.sh`, `4d0f0c92…`.
- The ssh rc was 0, read unpiped (`launch-submit.out.txt`).
- `after-submit.txt` is the read-only look at the root taken right after the connect.

**`connect-a1-full.log.txt`** (login12, 2026-11-08T09:14:13Z–09:14:22Z, rc 0):
- **Refusals:** none fired. The dry DONE is at `96bffd62…` (job 60993979, 9/9 rc 0, teardown "").
- **iris, the actual reading** (`iris-full.txt`): m3246 had charged 18,253.9 of its 20,000.0 allocation, so
  `balance_node_h=1746.1`. Half the balance is 873.0, and the combined caps of 109.0 are below it.
- **The fence:** pass. `squeue-before-full.txt` is empty.
  - The line reads "0 jobs, none outside rs1_*": that is the script's wording for an empty queue.
- **The charge ceiling** (`sacct-stage1-before.txt`):
  - sacct read exactly attempt 1's `60983221|ens1_dry1|FAILED|571|1` and the rerun's `60993979|ens1_a1_dry|COMPLETED|1093|1`.
  - Stage 1 had spent 0.4622 node-h. Adding six 9-hour limits gives 54.4622, within the 55.0 cap.
- **The stat:** 23 files, 0 missing. The npz, the bkg, attempt 1's F₆₄ and j1–j20 each have size, mtime and atime
  recorded.
- **The deploy (re-checked):**
  - HEAD is `f4d2d7f3` with 0 modified tracked files before and after.
  - 12 blobs and 7 sha256s were checked, with 0 mismatches.
  - The 20 control-jitter copies match the dry connect's (`refs-SHA256SUMS-full`).
  - `deploy-status-full.txt` records the 2 `porcelain --ignored` lines the dry job left behind: the two `__pycache__/`
    directories.
- **The stage-1 queue:**
  - `dry.tsv` and shard0–5 match `queue-sha256-full.expected` (`queue-sha256-full.txt`).
  - The shards hold 168/168/167/167/167/167 tasks.
- **The submission:** six sbatch calls at 09:14:16Z, each rc 0 (`submit-a1-full-*.out.txt`). Each job's parsed
  `TimeLimit` is 09:00:00, as declared.

  | shard | job |
  |---|---|
  | 0 | 60995093 |
  | 1 | 60995094 |
  | 2 | 60995095 |
  | 3 | 60995096 |
  | 4 | 60995097 |
  | 5 | 60995098 |

**The poll** (`job-poll.txt`): a read-only sacct every 15 minutes.
- All six were RUNNING by 09:29:54Z.
- Four had COMPLETED at 15:46:59Z.
- All six had COMPLETED at 16:02:02Z.

## The jobs (`jobs/`, `log-shard*/`)

- **`sacct`** (`post/sacct-full.txt`): all six ended COMPLETED 0:0 on 1 node with 256 CPUs.
  - sacct prints Start and End in cluster-local time (UTC−8), so the UTC times in the table are those plus 8 h.
  - The job `.out` files print their own UTC start and queue-end lines.

  | shard | job | node | start (UTC) | end (UTC) | ElapsedRaw (s) | node-h |
  |---|---|---|---|---|---|---|
  | 0 | 60995093 | nid006396 | 09:21:24Z | 15:48:15Z | 23,211 | 6.4475 |
  | 1 | 60995094 | nid006419 | 09:21:24Z | 15:46:44Z | 23,120 | 6.4222 |
  | 2 | 60995095 | nid006755 | 09:22:26Z | 15:44:22Z | 22,916 | 6.3656 |
  | 3 | 60995096 | nid006773 | 09:22:26Z | 15:46:01Z | 23,015 | 6.3931 |
  | 4 | 60995097 | nid006814 | 09:22:26Z | 15:43:10Z | 22,844 | 6.3456 |
  | 5 | 60995098 | nid004447 | 09:22:26Z | 15:51:16Z | 23,330 | 6.4806 |

  - The sum is 138,436 s, or **38.4544 node-h**. The per-shard column is rounded, so it sums to 38.4546.
- **`log-shard*/DONE`:** each reads mode shard, stage 1, its own shard number and job, pin `f4d2d7f3…`, ended = tasks,
  rc 0, and teardown "". There is no FAILED, `.failed` or `.teardown`, and `runs-teardown/` does not exist. <!-- absence-ok: the run's own filesystem records (DONE teardown "", the post-run's existence check), not a claim about a result -->
- **Lanes:** each job ran 8 lanes (`jobs/*.out.txt`).
- **Environment warnings:** `log-shard*/env.log.txt` shows the same two missing `setup.sh` warnings as the dry run's,
  then `lightgbm 4.6.0 numpy 1.26.4 python 3.11.14`.
- **`log-shard*/SHA256SUMS`:** each is written at shard end and lists every file under `runs/` at that moment.
  - The counts are 2,013 / 2,011 / 2,009 / 2,010 / 2,007 / 2,017.
  - Shard 5 ended last. Its list holds all 2,017 files and is byte-identical to the post-run's `post/runs-SHA256SUMS`
    (`e96d07da…`).
- **The task logs:** the 1,004 tasks' `.log`, `.time`, `.start` and `.end` files (4,016 files, about 10 MB) stay on
  pscratch under `stage1/log-shard*/`. `log-index/task-logs-SHA256SUMS` lists them by sha256.
  - That list was computed on pscratch. The lane's pulled copy matches it file for file.
  - The post-run read every task's `.log`, `.start` and `.end` (below). It did not read the `.time` files.

The products stay at `/pscratch/sd/j/josephrb/ens1-a1-20261108/runs/`. None is committed.

## The POST-RUN connect (`post/`)

**The scripts and their rcs:**
- `ens1_a1_full_postrun.sh` is the copy the connect wrote, sha256 `10ea53cb…`.
- The launcher is `ens1_a1_full_postrun_launch.sh`, `22708c9d…`.
- The launcher rc and ssh rc were both 0 (`launch-postrun.out.txt` holds the ssh rc line).
- `connect-postrun.log.txt` ran on login33, 2026-11-08T16:02:18Z–16:02:32Z, rc 0.

**The checks:**
- **The fence:** pass (`squeue-before.txt` is empty), and none of the six jobs was queued.
- **sacct:** each job COMPLETED on 1 node under its own name `ens1_a1_s1_<i>`.
  - The charge is 0.4622 + 38.4544 = 38.9166 node-h, within the 55.0 cap.
- **The deploy:**
  - HEAD is `f4d2d7f3` with 0 modified tracked files.
  - The probe is at sha256 `807c40d3…`.
  - The dry run's DONE is at `96bffd62…`, and its SHA256SUMS is at `20491b0c…`, the receipted file.
  - These three checks print nothing when they pass. The log reaching the next step is their record.
- **`read.py`** (sha256 `7990940c…`), run under the sourced environment (Python 3.11.14), wrote `a1-full-read.json`
  (sha256 `daee5538…`) with the verdict **PASS** and no failures:
  - **The DONEs:** each shard's DONE equals its expected record, and its teardown list matches its `.teardown` files.
    Both are empty.
  - **The products:**
    - Every expected product (from the bound probe's `expected_outputs`) is at its line in its own shard's SHA256SUMS,
      unchanged now.
    - The dry run's nine are at their lines in the receipted dry SHA256SUMS, unchanged.
    - `runs/` holds exactly the 2,017 expected files.
  - **E5 in the products:** each of the 2,017 products' meta `ens1` blocks has
    `moved_rows == {MCgen: 0, MCreco: 0, measured: 0, bkg_reco: 0}`.
    - Each block's mode, k and protocol seed match its name.
    - Each block's `code_sha256` is the probe's `807c40d3…`.
    - The counts are `moved_rows_nonzero 0`, `block_mismatch 0` and `code_mismatch 0`.
  - **E5 in the logs:** each task log has exactly one `[ens1] grid membership moved rows {…}` line per unfold, all zero.
  - **The unfold lines:** each task log has exactly one `{"out", "rc", "seconds_unfold"}` line per unfold, naming its
    products, with rc 0. That is 2,008 lines.
  - **Teardowns:** none, and `runs-teardown/` is absent (`runs-teardown-SHA256SUMS` is empty).

**The timing readout** (from `a1-full-read.json`; the dry-run projection was 42 × 537.935 + 300 s = 6.359 h on
seconds_unfold and 6.799 h on task wall):
- **seconds_unfold over the 2,008 unfolds:** min 394.9 s, median 498.0 s, p90 602.6 s, p99 685.3 s, **max 779.908 s**
  (`ens1_k043_b-_j1`, shard 5).
- 17 unfolds exceeded 687 s, the per-unfold t that declaration §8's 42 × t + 300 s ≤ 8.1 h implies: 3 in shard 0, 2 in
  shard 1, 1 in shard 3, 2 in shard 4 and 9 in shard 5. The dry run's maximum was 537.935 s.
- **Max task wall:** 1,498.1 s, for a 2-unfold task in shard 5.
- **Max shard wall (ElapsedRaw):** 23,330 s = **6.481 h**, under both the 6.799 h projection and the 9.0 h limit.
- The per-unfold excess shows only as a spread in task time. No shard approached its limit.

## The ledger and renames

**The ledger:** `fd/LEDGER.tsv` has eight rows for this run: the SUBMIT connect, the six jobs and the POST-RUN connect.

**Renames:** git ignores `*.log` and `*.out`, so those files carry a `.txt` suffix here. Their contents are unchanged.

**Empty files:** `connect/squeue-before-full.txt`, `post/squeue-before.txt` and `post/runs-teardown-SHA256SUMS` are
empty, as they were on pscratch.

**Next:** the ANALYSIS connect (`ens1_a1_s1_analysis.sh`, `2691cf9c…`) waits for the director's go on this readout.
Stage 2 runs only on STAB_PASS and a further go.
