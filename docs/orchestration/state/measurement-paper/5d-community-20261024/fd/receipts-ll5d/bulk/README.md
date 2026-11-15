# LL5D bulk (ll5d_bulk_01–10) and the rc-129 rerun (2026-11-13/14)

**By** the `cov2d` session, under LL5D-DECLARATION.md §11 step 6, at M = `4231b14de5ea693e92cb31b1358a816b5c2f6625`.
This receipt records the bulk's ten jobs, the declared atime deviation in 65 of their calls, the one call that crashed
(rc 129) and its rerun, and the evidence for each. The null and the readout that graded these products are
`../null/` and `../readout/`. The lane draws no outcome.

**CANNOT AUTHORIZE:** the HPSS copy of `$U` (B2: after the readout, with its own go), or any reading of a verdict.

## The jobs

- **Go:** the director, "go 163c6269 30570e73, conditional on all three" (the pilot's records, clipcheck and the audit's
  acknowledgement).
- **The package:**
  - connect `package/connect-bulk.sh` `163c6269`, which ran (`run/staged_sha.txt`);
  - the pinned partition `package/bulk-lanes.tsv` (`315f004b`);
  - the launcher `package/launch-ll5d.sh` `30570e73`, which is `../pilot-r2/launch-ll5d.sh` `4cd22193` plus
    `launch-ll5d-30570e73-vs-4cd22193.diff.txt`;
  - the remaining `package/*.diff.txt` are the drafting diffs kept in the lane's working directory.
- **The connect** (`run/connect.log.txt`, 2026-11-13T06:09Z): atime-pre 1146 files at 06:10:24Z, sha256 `908d3922…`;
  ten sbatch, each 1 node at 8:00:00.
- **sacct** (`run/sacct-bulk-utc.txt`, TZ=UTC):

| job | id | state | exit | start → end (UTC) |
|---|---|---|---|---|
| 01 | 61214597 | FAILED | 8:0 | 07:08:55 → 11:54:15 |
| 02 | 61214601 | FAILED | 8:0 | 07:09:28 → 12:25:25 |
| 03 | 61214604 | FAILED | 8:0 | 08:08:48 → 13:21:02 |
| 04 | 61214605 | FAILED | 8:0 | 08:08:48 → 13:21:33 |
| 05 | 61214607 | FAILED | 8:0 | 08:58:16 → 14:14:50 |
| 06 | 61214609 | FAILED | 8:0 | 08:58:16 → 13:42:54 |
| 07 | 61214610 | FAILED | 8:0 | 09:47:58 → 14:45:49 |
| 08 | 61214612 | FAILED | 8:0 | 09:47:58 → 14:45:32 |
| 09 | 61214614 | FAILED | 129:0 | 10:16:07 → 15:16:24 |
| 10 | 61214615 | COMPLETED | 0:0 | 10:16:07 → 15:14:22 |

- **Fetched** O_NOATIME (`node/node-sha256.raw.txt`, 271 files; `node/fetch_bulk.py`):
  - the job logs (`node/logs/`), every lane's `.out` (`node/lanes/*.out.txt`), and each lane's stderr with the
    repeated sklearn feature-name warning lines removed (`node/lanes/*.time.extract.txt`); the originals are listed by
    sha256 in the node list;
  - the bulk's 86 atime sidecars in `$U` are listed there by sha256, not committed. The evidence below quotes them.
- **Call return codes:** 86 calls; 20 returned rc 0, 65 rc 8 and 1 rc 129. Every call printed an `out` line for every
  item it was given: 1649 lines for 1649 items.

**My own miss, recorded:** six of these jobs (01-06) had already failed before the G2R batch launched at
2026-11-13T14:15:59Z. I had read only squeue, which no longer listed them, so the failures went unreported until
2026-11-14T03:05Z. The standing rule now is that a lane's status comes from sacct over its ids.

## The 65 rc-8 calls: the declared deviation (LL5D-DECLARATION.md:672-673)

Every rc-8 call printed `[ll5d-b] DEVIATION: atime moved on […/ll5d-bulk-r1/deploy/docs/orchestration/state/2d-closeout/stageF/methods/sf1/manifest/inputs-sha256.txt]`
(65 lines across `node/lanes/*.time.extract.txt`). The evidence, in `evidence/evidence_node.out.txt`
(`evidence_node.py`, read-only, O_NOATIME):

- **(a)** The manifest in the bulk's own deploy: its sha256 equals the bound `3a50f502…`. Its atime is
  2026-11-13T10:16:13Z.
- **(b)** Every atime "now" in the sidecars is one of 08:08:54, 08:58:19, 09:48:03 and 10:16:13Z. Each is 3-6 s after a
  job pair's sacct Start (above). Each job's start check, `sha256sum -c bound.sha256` in the shared deploy, lists that
  manifest and reads it plainly.
- **(c)** `ll5d_b` reads `--manifest` only through `fd_1b_inv.open_noatime` (O_NOATIME; `ll5d.py`:234, :259;
  `fd_1b_inv.py`:96-104).
- **(d)** `bound.sha256` (`7540b2de…`) lists the manifest.
- **(e)** Across the 86 sidecars, the only path that moved is that manifest (65 moves). No move is earlier than
  08:08:54Z, and the 16 calls on nodes 09-10, which started last, show none. coverage-5b-audit's tally of the moves is
  8 + 8 + 16 + 16 + 17.
- **(f)** `$U` holds 1662 npz. The 1649 out lines each have a file. The 13 extras are the pilot's, by name and sha256:
  `evidence/extras-vs-pilot-r2.out.txt`, against `../pilot-r2/ll5d_pilot_61184880.out.txt`.
- **(g)** Node 09 lane 4's 20 products, with their sha256 and mtimes.

**The mechanism:** a later job's start check moved the shared deploy manifest's atime while earlier jobs' calls,
watching it, were running.

**The director's ruling (accepting coverage-5b-audit's verdict):** the 65 rc-8 calls are the declared deviation of
:672-673, and their products are gradable. The manifest's atime is never restored. Multi-job submissions on a shared
deploy now need the B1 fix first.

**A defect in the evidence script, noted:** the "utc" on the first line of `evidence/evidence_node.out.txt` is +8 h
wrong, because python3.6's `utcnow().timestamp()` reads the time as local. No other field uses it.

## The rc-129 call and its rerun (`rerun129/`)

- **The crash:** node 09 lane 4 (AR23 toy all_4761060…079) wrote all 20 products, then ROOT segfaulted at Python exit
  (`node/lanes/node09-lane4.time.extract.txt`: `*** Break *** segmentation violation`, a stack through
  `Py_FinalizeEx`), and exited 129. A crash is INVALID.
- **The rerun:** the director ruled one unchanged rerun under :70. It ran as one job of 4 lanes of 5 on a fresh deploy
  and a fresh out directory:
  - connect `rerun129/package/connect-rerun129.sh` `0fb2f282`, revised from `bcf1c552` at the director's request; job
    `d45cdf2f`; launcher `7b106d44`; audited against criteria (a)-(f) (`AUDIT-CRITERIA.txt`);
  - job 61255888: COMPLETED 0:0, 05:57:32-07:12:46Z (`rerun129/post/sacct-61255888-utc.txt`);
  - `RERUN-EXIT clean rc=0`, with all four lanes rc 0; the sidecars show moved [].
- **The comparison:** `compare_rerun.py` (`8c9da6ff`) applies the director's rule (d). The allow-list was fixed before
  the run (slurm_job, seconds_unfold, peak_rss_kib and refinement/seconds), and the tests `rerun129/tests/` include
  the mutants.
  - It reads `COMPARE-RERUN EQUAL (20 names)` (`rerun129/post/compare_rerun.out.txt` `c010d9bc…`): 100 numeric members
    byte-equal, and meta equal outside the allow-list.
  - q6: the 20 originals equal their (g) sha256 (`q6_and_sidecars.out.txt`).
  - The rerun's atime-post reads SAME-SET-NONE-MOVED.
- **The director's ruling:** the comparison is accepted, and the readout grades `$U` as it stands. The 20 originals
  are the gradable products, and this rerun is their evidence.

## Atime across the bulk, and X1

- **The bulk's atime-post** (`atime-post/`): `atime-post-bulk.sh` `5806a902`, under the director's go, is the
  `../../receipts-cov2d/g2r/envtest/atime-stat-list.sh` (`346656a7`) pattern pointed at this bulk's list. It ran on
  login10 at 2026-11-14T03:11:38Z and reads 1146 paths, moved 0 (`compare.out.txt`).
- **X1 (closed by the director):** baseline atimes of of_inputs_5d.npz and bkg_dump.npz (1794546256) reflect E96D
  61202343's recorded plain reads (fd/e96-data-20261110/receipts/a1-run-20261112/README.md:147).

## Left for removal by Joseph

- the bulk's namespace `/pscratch/sd/j/josephrb/ll5d-bulk-r1/` (with its deploy clone);
- the rerun's namespace `/pscratch/sd/j/josephrb/ll5d-rerun129-r1/` and its out directory
  `/pscratch/sd/j/josephrb/ll5d-unfolds-rerun129-r1/` (the 20 rerun products and 4 sidecars), all after this merges.

`$U` itself (`ll5d-unfolds-r2`) stays: it holds the graded products, and the HPSS copy comes after the readout.
