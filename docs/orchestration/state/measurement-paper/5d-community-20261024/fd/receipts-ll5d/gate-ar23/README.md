# LL5D ll5d_gate_AR23 (job 61040235): the step ended rc 3 and printed `verdict=STOP` (2026-11-10)

**By** the `cov2d` session, under LL5D BINDING 2. The director's go named `connect-gate.sh` `21f0a573…` (run with
`gate-ar23`) and `launch-ll5d.sh` `aa907b91…`, back to back with the other truth's gate. The calibration is run 2's
(`../calib-2/`).

- **The step's own result:** the job log reads `gate rc=3`, and `gate.time` reads `Exit status: 3`. The step printed
  `LL5D-GATE ar23 verdict=STOP` (`gate.out.txt`). sacct reads FAILED, ExitCode 3:0, Elapsed 11:00:23; that is ll5d.py's
  `RC["STOP"]` = 3, passed through by the job's `exit $rc`. The record's `why` is `the gate or the backstop failed`.
- **Routing:** this STOP goes to the director and Joseph unrepaired (BINDING 2 ruling 5). Nothing was relaunched or
  changed.
- **CANNOT AUTHORIZE:** a rerun, a repair, the pilot or the bulk. The pilot and bulk need a PASS for the reading
  concerned (BINDING 3 ruling 4).

## The condition that set the verdict

`ll5d.py:1016` at `a95cc39f7437170af0b65ba042934fad079e0ee2` is
`ok = all(v == "option (1)" for v in rec["reads"].values()) and all(b["passes"] for b in back.values())`.
Recomputed on the full record `gate-ar23.json`, it gives False. The record's fields, as written (all also in
`gate-ar23.fields.txt`):

| evaluation | `reads` | `option_1_qualifies` | `option_3_applies` | `mismatch_bounded` | `gate_n.passes` | `backstop.passes` |
|---|---|---|---|---|---|---|
| ar23/all | option (3) | True | True | False | True | True |
| ar23/minus2 | option (3) | True | True | False | True | True |

- **Where `option_3_applies` comes from:** `fd_1b_c2.reading_1b`, the verbatim copy at 342c0ce5. It sets
  `opt3 = (...) or not bounded`, with `bounded = vi.largest_cell_unmatched_share <= cp2.MISMATCH_BOUND`, and
  `MISMATCH_BOUND = 0.05` in `clip_probe2.py:60`.
- **`record.vi`:**
  - `largest_cell_unmatched_share` 1.0;
  - `signal_rows_unmatched` 32,846,302 of `signal_rows_in_phase_space` 32,846,302;
  - `truth_rows_unmatched` 32,849,103 of `truth_rows` 32,849,103;
  - every one of the 16 per-cell shares is 1.0 (signal) and 1.0 (truth).
- **Other recorded checks:**
  - `controls.denominator.passes` True (D1, D2, D3);
  - `controls.r_positive.passes` True;
  - `gate_sample.first_300_bitwise` True;
  - `calibration_sha256` `ea039893e8ec98a9cd3da15dd7811a82a99563da8fbb253e6fc0766eb960fb17`, and `calibration_npz_sha256` `b31ddd12d050163396b4811705777fc1fa28f77757575af73c8dc5976b3c1a7c`.

This receipt states no mechanism for the vi record. A read-only diagnosis was requested separately by the director.

## The outputs

- **`gate-ar23.json`** (the full gate record) has sha256 `2fe1e99dafa1cb6dc3bd209e4fb0cf2c3793f3d5f6c12f6171e8a05a2cadb9de`. It is NOT committed. It names the sealed
  `gate-ar23.clipprep.npz` by bare filename, and `verify_receipt_artifacts.py` then fails (MISSING) on any
  tracked receipt directory that lacks that file. The sealed file cannot be tracked. This follows the director's
  earlier choice for such records (#687): keep them out of git, listed by sha256. The shared checker is unchanged.
  The record stays on pscratch, and a copy whose sha256 matches is in the lane's working directory.
- **`gate-ar23.fields.txt`** is an extract of that record, made by `extract_gate.py` (committed here). Its header
  names the source sha256. It keeps every top-level key verbatim except three: `receipt` (the descriptive
  per-row pass, about 708 KB) and `clip_prep` are omitted, and `atime` is reduced to `moved` and a file count.
- **`gate-ar23.receipt.npz`:** 154,995 bytes, sha256 `988b26d2fad83b6420f4912de4857449f0452bba4421666ff113e3ec4661ca64`. It is not committed, because the
  repository ignores `*.npz`.
- **SEALED:** `gate-ar23.clipprep.npz`, 535,686,808 bytes, sha256 `c567183d94d9b0be9b1d7ec1513cdb58db14bcffa5ef6eb630c7b77d4c5ff6d1`. These values come from the job's own stat
  and sha256sum line. The file was never opened, fetched or summarized (BINDING 2's seal, A1a section 5j).
- **Where the files stay:** all of them remain in `/pscratch/sd/j/josephrb/ll5d-gate-ar23-20261108/`.

## The run

- **The launch:**
  - `fence host=login02 utc=2026-11-09T16:28:38Z`, with no cov2d job unended (`fence.txt`);
  - the staged connect's node sha256 matched the local file and the go (`staged_sha.txt`);
  - launched detached at 2026-11-09T16:28:57Z (`launch.txt`, `launch-stdout.txt`);
  - the `/dev/shm` copy was removed, with `rm -f` rc 0 and the closing `ls` finding nothing (`removal.log.txt`).
- Before this launch, an independent squeue showed G18 queued (`squeue-before-ar23.txt`), as the director's order required, so this projection counts G18's 31.0 as held.
- **The connect** (`connect-gate-ar23.log.txt`):
  - `balance_node_h=1643.0 half=821.5 cap=148.0`;
  - `projection charged=1.184 held=31.000 this=31.0 total=63.184 cap=148.0`;
  - the deploy had porcelain 0 at `a95cc39f7437170af0b65ba042934fad079e0ee2`, with all 15 bound blobs OK;
  - the job script sha256 was `77b4d88b424c94bfaf87d1fc9459689b55c96fd1056623b987396a155b6217b7`;
  - atime-pre: 1146 files at 2026-11-09T16:29:56Z;
  - TimeLimit=1-07:00:00.
- **The job** (`ll5d_gate_AR23_61040235.out.txt`):
  - it ran on nid006874 from 2026-11-09T16:33:58Z; the closing line reads `end=2026-11-10T03:34:15Z`;
  - the deploy was clean, the blobs OK, and every thread variable was 1;
  - wall 11:00:08, max RSS 285,660,780 KiB;
  - `env-job.log.txt` records the same two `setup.sh: No such file or directory` lines as the calibration runs.
- **Cost:** 11:00:23 on one node.
- **Atimes:** atime-post was taken stat-only over the same declared inputs at 2026-11-10T04:18:09Z on login01
  (`atime-post.raw.txt`). It is byte-identical to `atime-pre.tsv` (`cmp` rc 0), so 0 of 1146 files moved.
- **The fetched files** match the node's sha256: `node-sha256.txt` has 10 files, and all 10 are OK. Eight of
  them are committed here; `gate-ar23.json` and `gate-ar23.receipt.npz` are listed by sha256 only. The `.log`/`.out`
  files carry a `.txt` suffix here because the repository ignores those extensions.
- **The watcher** (`watch.log.txt`, shared by both gates):
  - three single polls failed earlier, at rc=255;
  - its last read, at 2026-11-10T00:01:16Z, showed both jobs RUNNING;
  - from 00:11:18Z it logged rc=255 on every poll, because the ssh certificate had lapsed, until it was stopped;
  - the terminal states above were then read directly once the certificate was renewed.
- **The diffs:** `gate-vs-calib2.diff.txt` diffs the connect against `../calib-2/connect-calib-2.sh`.
  `gate-vs-preA1a1.diff.txt` diffs it against its pre-A1a.1 draft (M `e92e9467…`, ll5d.py `9dbf9cf4…`).

## Files

`atime-post.raw.txt`, `atime-post.tsv`, `atime-pre.tsv`, `bound.sha256`, `connect-gate-ar23.log.txt`, `connect-gate.sh`, `env-job.log.txt`, `extract_gate.py`, `fence.txt`, `gate-ar23.fields.txt`, `gate-vs-calib2.diff.txt`, `gate-vs-preA1a1.diff.txt`, `gate.out.txt`, `gate.time`, `launch-ll5d.sh`, `launch-stdout.txt`, `launch.txt`, `ll5d_gate_AR23_61040235.out.txt`, `node-sha256.txt`, `removal.log.txt`, `sbatch-ll5d-gate.sh`, `squeue-before-ar23.txt`, `staged_sha.txt`, `watch.log.txt`.
