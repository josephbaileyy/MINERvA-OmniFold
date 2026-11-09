# LL5D ll5d_calib, run 2 (job 61037236): the step ended rc 0 and printed `verdict=CALIBRATED` (2026-11-09)

**By** the `cov2d` session, under LL5D BINDING 2. The director's go named `connect-calib-2.sh` `6d8e769b…` and
`launch-ll5d.sh` `aa907b91…`. This run follows run 1's INVALID crash (`../calib-1-invalid/`) and the A1a.1 fix
(PR #967, merged at `a95cc39f7437170af0b65ba042934fad079e0ee2`). Its line-by-line differences from run 1's connect are
in `run1-to-run2.diff.txt`.

- **The step's own result:** `calib rc=0` (`ll5d_calib_61037236.out.txt`), `Exit status: 0` (`calibration.time`), and
  the printed line `LL5D-CALIBRATION verdict=CALIBRATED` (`calibration.out.txt`). sacct reads COMPLETED, ExitCode 0:0,
  Elapsed 01:10:37 (`joblog.txt`, `watch.log.txt`). The job script now exits with ll5d.py's rc, so this time sacct's
  state is the step's.
- **The calibration record** is `calibration.json`, sha256
  `ea039893e8ec98a9cd3da15dd7811a82a99563da8fbb253e6fc0766eb960fb17`. Its companion `calibration.npz` (13,951,349 bytes)
  has sha256 `b31ddd12d050163396b4811705777fc1fa28f77757575af73c8dc5976b3c1a7c`. The npz is not committed, because
  the repository ignores `*.npz`. It stays at `/pscratch/sd/j/josephrb/ll5d-calib-2-20261109/calibration.npz`, and a
  copy whose sha256 matches is kept in the lane's working directory. Both digests are what the gate connect binds.
- **CANNOT AUTHORIZE:** the gate jobs. Each gate connect gets its own go on its own sha256.

## The record's fields, as written (`calibration.json`)

These fields are read straight from the record. This receipt draws no conclusion from them.

- `schema` `ll5d-calibration/1`, `verdict` `CALIBRATED`, `sets` 10000, `draws_per_set` 3000, `truths` g18 and ar23.
  `evaluations` are g18/minus2, g18/all, ar23/minus2 and ar23/all.
- **Rule:**
  - `rule.s` 0.9;
  - `rule.measured_jointly` true;
  - `rule.i_alone_exceeds` false;
  - `rule.thresholds` per evaluation: `ii_mean_log` and per-cell `sd_per_cell`, with `iii_alpha_multiple` 3.87.
- **Controls:** `control_law.holds` true and `control_linearisation.holds` true, each true for all four evaluations.
- **Power:** `power.meets` true, with `uniform_meets` true for all four evaluations.
- **Checks:** `checks.D1.passes` true (the six GEANT tdw digests, `differ` empty) and `checks.r_positive` passes for
  both truths (0 rows not positive).
- **Threads:** all four `threads` variables are "1". `code_sha256` has `ll5d.py`
  `b49f5d5f793265ef0cf569abe1912838cce9280e692f4dd61100d05c133aec1f` and `fd_1b_c2.py`
  `522d7edd71643df61d0c5ef5a7488834e664eb36d20c3e0c0b46e10a5808f02f`.
- **In-process atimes:** `atime.moved` is empty over the 715 files it tracks.
- **Timing:**
  - `timing.seconds` 4226.08;
  - `timing.set_seconds_measured` 4.214, with 64 workers;
  - `timing.projected_seconds` 2657.71 against `budget_seconds` 16200.

## The run

- **The launch** (`fence.txt`, `staged_sha.txt`, `launch.txt`, `removal.log.txt`):
  - the fence was clear at 2026-11-09T15:01:56Z on login02 (squeue empty, no cov2d job unended);
  - the staged connect's node sha256 matched the local file and the go, `6d8e769b98273e464a62bf3f3e2e00340ced1c0c430c7f499095ee843a8c71f8`;
  - it was launched detached at 15:02:31Z;
  - the staged copy `/dev/shm/josephrb-ll5d-calib2.sh` was then removed (`rm -f` rc 0, and the closing `ls` found nothing).
- **The connect** (`connect-calib-2.log.txt`):
  - iris: the m3246 balance was 1,643.8 node-h, half 821.9, against the cap 148.0;
  - the projection: charged 0.007, held 0.000, this job 5.0, total 5.007 against the cap 148.0;
  - the deploy: porcelain 0 at `a95cc39f7437170af0b65ba042934fad079e0ee2`, with all 14 bound blobs OK (this includes
    `s5e_candidate.py` and `s5e_deform.py`);
  - the job script's sha256 was `300c59103020e9242c6722f006385eb1858c7c445a7fdb73ed5c97ac1be5308c`, and this copy
    hashes to the same;
  - atime-pre: 749 files at 15:03:34Z;
  - submitted as job 61037236, with scontrol's TimeLimit 05:00:00.
- **The job** (`ll5d_calib_61037236.out.txt`):
  - it ran on nid004382 from 15:04:10Z to 16:14:46Z;
  - the deploy was clean and the 14 blobs OK;
  - every thread variable was 1;
  - CPU was 4594%, wall 1:10:29, max RSS 10,028,020 KiB in the timed process. sacct's batch MaxRSS is 156,331,324K
    across its workers.
  - `env-job.log.txt` records the same two `setup.sh: No such file or directory` lines that run 1 recorded.
- **Cost:** 01:10:37 on one node, about 1.18 node-h.
- **Atimes:** atime-post was taken stat-only on the same declared inputs at 16:15:51Z on login18
  (`atime-post.raw.txt`, `atime-post.tsv`). `atime-post.tsv` is byte-identical to `atime-pre.tsv` (`cmp` rc 0), so 0 of
  749 files moved.
- **The fetched files** match the node's sha256: `node-sha256.txt` has 10 files and `shasum -c` gives 10 OK. The
  `.log`/`.out` files carry a `.txt` suffix here because the repository ignores those extensions. The originals stay
  in `/pscratch/sd/j/josephrb/ll5d-calib-2-20261109/`.

## Files

`connect-calib-2.sh`, `launch-ll5d.sh`, `run1-to-run2.diff.txt`, `sbatch-ll5d-calib.sh`, `bound.sha256`,
`connect-calib-2.log.txt`, `ll5d_calib_61037236.out.txt`, `env-job.log.txt`, `calibration.json`, `calibration.out.txt`,
`calibration.time`, `atime-pre.tsv`, `atime-post.tsv`, `atime-post.raw.txt`, `node-sha256.txt`, `fence.txt`,
`staged_sha.txt`, `launch.txt`, `removal.log.txt`, `watch.log.txt`, `joblog.txt`.
