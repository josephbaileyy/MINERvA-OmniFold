# LL5D ll5d_vicheck (job 61075015): the step ended rc 0 and printed `verdict=PASS` (2026-11-10)

**By** the `cov2d` session. This is step 1 of the rerun that Joseph decided (`DECISION-20261110-joseph-ll5d-rerun-16-cells.md`,
#1018), under amendment A1a.2 (bound in #1021; M_A1a.2 = `639ef907250a2a7909b7b9ba89b2e85e70c9b767`). The director's go
named `connect-vicheck.sh` `6f8b1e6f…` and `launch-ll5d.sh` `b86004df…`. The director ruled this preflight part of the
rerun #1018 authorizes.

- **The step's own result:** the job log reads `vicheck rc=0`, and `vicheck.time` reads `Exit status: 0`. The step
  printed `LL5D-VICHECK verdict=PASS` (`vicheck.out.txt`). sacct reads COMPLETED 0:0 with Elapsed 00:01:37 (`joblog.txt`).
- **Routing, as the director set it:** a PASS continues to step 2, the calibration (calib-3). That connect goes to
  the director with its sha256 for its own go.
- **CANNOT AUTHORIZE:** the calibration or the gates. Each needs its own go.

## The record's fields, as written (`vicheck.json`)

This receipt reports the fields and draws no coverage conclusion.

- **`verdict` PASS.** `mismatch_bound` is 0.05, and `vi.largest_cell_unmatched_share` is 0.0. All 16 per-cell shares
  are 0.0 on both sides.
- **`vi`** is the key the fixed gate uses (`ll5d.vi_inputs`, float32 on both sides):
  - signal_rows_unmatched is 0 of signal_rows_in_phase_space 32,846,302;
  - truth_rows_unmatched is 2,801 of truth_rows 32,849,103.
- **`vi_unrounded`** is the call the gates of 2026-11-10 made. It reads share 1.0: 32,846,302 of 32,846,302 signal rows
  and 32,849,103 of 32,849,103 truth rows unmatched. That is the gates' record, reproduced.
- **`terms`** (the 2,801 rows):

| term | rows |
|---|---|
| signal_rows | 32,849,103 |
| pass_truth | 32,849,103 |
| in_phase_space (pass_truth and in the 5D cells) | 32,846,302 |
| pass_truth_outside_cells | 2,801 |
| … of which outside on W alone | 1,474 |
| … of which outside on q3 alone | 1,327 |
| … on pT, pz or eavail alone, or on two or more axes | 0 |
| inside_cells_not_pass_truth | 0 |
| truth_rows | 32,849,103 |
| truth_rows_outside_cells | 2,801 |

- **The npz dtypes and float32 exactness:**
  - `npz_dtypes`: MCgen float32, td_pt float32, w_truth float64;
  - `float32_exact`: w_truth 0.0 and tdw_ref 1.0.
  - These are the dtypes the A1a.2 diagnosis inferred from the writers' code (`../gate-vi-diagnosis/`, section 3). Here
    they are read from the real files.
- **`d1.passes`** is true, and **`atime.moved`** is empty.

## The run

- **The launch** (`fence.txt`, `staged_sha.txt`, `launch.txt`, `launch-stdout.txt`, `removal.log.txt`):
  - the fence was clear on login02 at 2026-11-10T05:53:14Z (squeue empty, no cov2d job unended);
  - the staged connect's node sha256 matched the local file and the go, `6f8b1e6f7a0c8143344fc9c51a52ac182e884cf521f2705ce47ccb19a9d0be49`;
  - it was launched detached at 05:53:32Z;
  - `/dev/shm/josephrb-ll5d-vicheck.sh` was removed (`rm -f` rc 0, and the closing `ls` found nothing).
- **The connect** (`connect-vicheck.log.txt`):
  - `balance_node_h=1585.7 half=792.9 cap=148.0`;
  - `projection charged=23.060 held=0.000 this=1.0 total=24.060 cap=148.0`;
  - the deploy had porcelain 0 at `639ef907250a2a7909b7b9ba89b2e85e70c9b767`, with all 14 bound blobs OK;
  - the job script's sha256 was `a690d6df56dfa951612be9aa840cbb68f894c7e737a52f5adede85d6a9bdd4d3`;
  - atime-pre: 749 files;
  - submitted as job 61075015, with TimeLimit=01:00:00.
- **The job** (`ll5d_vicheck_61075015.out.txt`):
  - it ran on nid004635 from 05:58:42Z; the closing line reads `end=2026-11-10T06:00:13Z`;
  - every thread variable was 1;
  - wall 1:24.13, max RSS 11,238,108 KiB.
  - `env-job.log.txt` records the same two `setup.sh: No such file or directory` lines as the earlier LL5D jobs.
- **Cost:** 00:01:37 on one node, about 0.03 node-h. A1a.2 section 5 estimated about 0.3.
- **Atimes:** atime-post was taken stat-only over the same declared inputs at 06:01:25Z on login09 (`atime-post.raw.txt`).
  It is byte-identical to `atime-pre.tsv` (`cmp` rc 0), so 0 of 749 files moved.
- **The fetched files:** all 9 match the node's sha256 (`node-sha256.txt`). The `.log`/`.out` files carry a `.txt`
  suffix here because the repository ignores those extensions.
- **The diffs:** `vicheck-vs-calib2.diff.txt` diffs the connect against calibration run 2's.
  `launch-vs-aa907b91.diff.txt` diffs the launcher against its previous version.
