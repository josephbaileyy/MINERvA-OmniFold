# LL5D ll5d_gate_AR23 rerun (job 61078506): the step ended rc 0 and printed `verdict=PASS` (2026-11-12)

**By** the `cov2d` session. This is the A1a.2 section 6 rerun on R00-R15 that Joseph decided
(`DECISION-20261110-joseph-ll5d-rerun-16-cells.md`, #1018). The director's go named `connect-gate-2.sh` `e22d094c…`
(run with `ar23`) and `launch-ll5d.sh` `b86004df…` (case `gate2-ar23`), back to back with the G18 rerun. The calibration
is run 3's (`../calib-3/`).

- **The step's own result:**
  - the job log reads `gate rc=0`, and `gate.time` reads `Exit status: 0`;
  - the step printed `LL5D-GATE ar23 verdict=PASS` (`gate.out.txt`);
  - sacct reads COMPLETED, ExitCode 0:0, Elapsed 10:27:21.
- **CANNOT AUTHORIZE:** the pilot, the bulk, or any opening or summary of the sealed clipprep file. Each needs its own
  go from the director.

## The condition that set the verdict

`nd-unfolding/ll5d.py:1038` at `639ef907250a2a7909b7b9ba89b2e85e70c9b767` (sha256 `2b0224c6…`, the connect's `L5`) is
`ok = all(v == "option (1)" for v in rec["reads"].values()) and all(b["passes"] for b in back.values())`.
The record's fields, as written (all also in `gate-ar23.fields.txt`):

| evaluation | `reads` | `option_1_qualifies` | `option_3_applies` | `mismatch_bounded` | `gate_n.passes` | `backstop.passes` |
|---|---|---|---|---|---|---|
| ar23/all | option (1) | True | False | True | True | True |
| ar23/minus2 | option (1) | True | False | True | True | True |

- **`record.vi`:**
  - `largest_cell_unmatched_share` 0.0;
  - `signal_rows_unmatched` 0 of `signal_rows_in_phase_space` 32,846,302;
  - `truth_rows_unmatched` 2,801 of `truth_rows` 32,849,103.
- **Other recorded checks:**
  - `controls.denominator.passes` True;
  - `controls.r_positive.passes` True;
  - `gate_sample.first_300_bitwise` True;
  - `atime.moved` is empty, with 717 files tracked inside the job;
  - `calibration_sha256` is `e9584339098c98ff9059279299329b1e84efca4f81583f4ebc71417b2fdb571b`, and `calibration_npz_sha256` is
    `b31ddd12d050163396b4811705777fc1fa28f77757575af73c8dc5976b3c1a7c`. These equal `../calib-3/node-sha256.txt` lines 4-5 and the connect's
    `CALSHA` and `CALNPZSHA`.

## The outputs

- **`gate-ar23.json`** (the full gate record) has sha256 `35a20c471cb06f428c49daaaebfc6646babb7f7fb060039d4c63139da51d0a4c`. It is
  NOT committed, for the reason `../gate-ar23/README.md` gives (#687 precedent): the record names the sealed clipprep by
  bare filename, so `verify_receipt_artifacts.py` would report it MISSING. The record stays on pscratch, and a copy
  whose sha256 matches is in the lane's working directory.
- **`gate-ar23.fields.txt`** is the extract made by `extract_gate.py`. It is byte-identical to `../gate-ar23/extract_gate.py`
  and its header names the source sha256. It keeps every top-level key verbatim except three: `receipt` and `clip_prep`
  are omitted, and `atime` is reduced to `moved` and a file count.
- **`gate-ar23.receipt.npz`:** 154,995 bytes, sha256 `988b26d2fad83b6420f4912de4857449f0452bba4421666ff113e3ec4661ca64`. It is not
  committed, because the repository ignores `*.npz`.
- **SEALED:** `gate-ar23.clipprep.npz`, 535,686,808 bytes, sha256 `c567183d94d9b0be9b1d7ec1513cdb58db14bcffa5ef6eb630c7b77d4c5ff6d1`.
  These values come from the job's own stat and sha256sum line. The file was never opened, fetched or summarized.
- **Where the files stay:** all of them remain in `/pscratch/sd/j/josephrb/ll5d-gate-2-ar23-20261110/`.

## The run

- **The launch:**
  - `fence host=login02 utc=2026-11-10T07:51:10Z`, with G18 61078463 PENDING and no cov2d job unended (`fence.txt`);
  - before this launch, an independent squeue (login28, 07:50:54Z) showed G18 queued (`squeue-before-ar23.txt`), so the
    projection counts G18's 31.0 as held;
  - the staged connect's node sha256 matched the local file and the go (`staged_sha.txt`);
  - launched detached at 2026-11-10T07:51:27Z (`launch.txt`, `launch-stdout.txt`);
  - the `/dev/shm` copy was removed, with `rm -f` rc 0 and the closing `ls` finding nothing (`removal.log.txt`).
- **The connect** (`connect-gate-2-ar23.log.txt`):
  - `balance_node_h=1582.5 half=791.2 cap=148.0`;
  - `projection charged=24.257 held=31.000 this=31.0 total=86.257 cap=148.0`;
  - the deploy had porcelain 0 at `639ef907250a2a7909b7b9ba89b2e85e70c9b767`;
  - the job script sha256 was `77b4d88b424c94bfaf87d1fc9459689b55c96fd1056623b987396a155b6217b7`;
  - atime-pre: 1146 files at 2026-11-10T07:52:33Z;
  - TimeLimit=1-07:00:00.
- **The queue:** the job stayed PENDING from submission until 2026-11-11T23:40:34Z, across the Perlmutter maintenance of
  2026-11-11.
- **The job** (`ll5d_gate_AR23_61078506.out.txt`):
  - it ran on nid005310 from 2026-11-11T23:40:37Z; the closing line reads `end=2026-11-12T10:07:55Z`;
  - the deploy was clean, the 15 bound blobs OK, and every thread variable was 1;
  - wall 10:27:09, max RSS 285,632,864 KiB;
  - `env-job.log.txt` records the same two `setup.sh: No such file or directory` lines as the earlier runs.
- **Cost:** 10:27:21 on one node.
- **The fetched files** match the node's sha256 (login20, 2026-11-12T10:12:20Z). `node-sha256.txt` has 10 files, and all
  10 are OK. Eight of them are committed here; `gate-ar23.json` and `gate-ar23.receipt.npz` are listed by sha256 only.
  The `.log`/`.out` files carry a `.txt` suffix here because the repository ignores those extensions.

## Atimes

- atime-post was taken stat-only at 2026-11-12T13:11:45Z on login10 (`atime-post.raw.txt`), by `atime-post-2.sh`
  (`e75bebe9…`). Its `find` is the connect's atime-pre `find` (`connect-gate-2.sh:101-104`) without the closing
  redirect. find rc 0, 1146 files (`atime-post.tsv`). One reading serves both gates, because they share their inputs, and
  their two `atime-pre.tsv` files are byte-identical (`cmp` rc 0). It was taken after both gates had ended. The next job
  of ours, `rsn_J1` 61168780, started at 2026-11-12T13:14:40Z (sacct, read at 13:14:48Z).
- **The difference:** 2 of 1146 lines differ from `atime-pre.tsv`.

  | file | atime-pre | atime-post |
  |---|---|---|
  | `nd-unfolding/of_inputs_5d.npz` | 1794179838 | 1794384571 |
  | `s5c-20260924/runs/p2/bkg_dump.npz` | 1794179838 | 1794384571 |

- **Where that move comes from:** both values equal the E96D dry run's stat-only readings, recorded in its receipt (#1065):
  - before job e96data_dry 61137569, the cov2d session's stat-only reading at 2026-11-11T08:07:03Z showed both at
    1794179838, equal to atime-pre;
  - after that job (08:09:02-08:24:40Z), both read 1794384571 (2026-11-11T08:09:31Z), with mtime and size unchanged.

  That job ran while this gate was PENDING, before it started. The gate's own in-job ledger (`atime.moved`, 717 files)
  is empty.
- The other 1144 files, including `sorted_NuEConstraint_FHC_RHC_IMD.txt`, are unchanged.

## The watcher

`watch.log.txt` is shared by both gates. It was written by successive watcher scripts, the last being
`watch-gates2g.sh` (`64eb6059…`).
- It polled sacct every five minutes from 2026-11-10T07:53:01Z.
- 83 polls failed (rc=255) with the maintenance banner, from 2026-11-11T16:10:39Z to 23:40:57Z.
- 41 other polls failed (rc=255) without the banner.
- The gates read RUNNING from 2026-11-11T23:46:03Z.
- The terminal states were logged at 10:11:23Z (AR23) and 10:37:00Z (G18).

## The diffs

`gate2-vs-gate.diff.txt` diffs `connect-gate-2.sh` against `../gate-ar23/connect-gate.sh`.

## Files

`README.md`, `atime-post-2.sh`, `atime-post.raw.txt`, `atime-post.tsv`, `atime-pre.tsv`, `bound.sha256`,
`connect-gate-2-ar23.log.txt`, `connect-gate-2.sh`, `env-job.log.txt`, `extract_gate.py`, `fence.txt`,
`gate-ar23.fields.txt`, `gate.out.txt`, `gate.time`, `gate2-vs-gate.diff.txt`, `launch-ll5d.sh`, `launch-stdout.txt`,
`launch.txt`, `ll5d_gate_AR23_61078506.out.txt`, `node-sha256.txt`, `removal.log.txt`, `sbatch-ll5d-gate.sh`,
`squeue-before-ar23.txt`, `staged_sha.txt`, `watch.log.txt`.
