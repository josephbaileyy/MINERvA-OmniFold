# COV2D-G2R prepare (job 61223390): `g2r_prepare.json` reads verdict PASS (2026-11-13)

**By** the `cov2d` session, under COV2D-G2R addendum J1 (§2 item 2; code at M = `401733bce290ce122cfbf38f1526e120f174b3ec`).

- **Connect:** `connect-g2r-prepare.sh`, `233f8cd2b7dd8ec1c7ee6b2db8a7c3aedf90f07232f5f6ff27833886dd629400`.
  It was templated from the envtest connect: `prepare-vs-envtest-1b392259.diff.txt` applied to
  `../envtest/connect-g2r-envtest.sh` (`1b392259…`) gives `233f8cd2…`.
- **Launcher:** `../envtest/launch-g2r.sh`, `60b624c6b31732ea732206ec63af027f09ba45c4329d7aa5c6c2275cc2919b95`
  (its `prepare` arm, unchanged since `468f1992…`; `../envtest/launch-chain.sh` rebuilds that chain).
- **Go:** the director, "go 233f8cd2 60b624c6", conditional on #1139 being merged on origin/main. #1139 merged as
  main `c78b1a16eba52b7524ec8128c5ff0a9dd76a8f6c`, and the director then confirmed the go was live.
- **Overlap:** the prepare ran beside the LL5D bulk under the audited overlap fence (the director's ruling: G2R may
  overlap the bulk; an unexplained move in the bulk's atime-post voids it).

Full digests: `node-sha256.raw.txt` (the node's files, read O_NOATIME) and `files.sha256` (every file here).

**CANNOT AUTHORIZE:** D_Ua or any other unfold job. Each needs its own go (J1 §2).

## The connect (login02)

- **Fence** (`fence.sh`, `fence.txt`), 11:19:48Z: only `ll5d_bulk_01`–`ll5d_bulk_10` RUNNING, no unended cov2d job.
  `launch-stdout.txt` reads `FENCE_CLEAR`.
- **Staging** (`staged_sha.txt`, `launch-stdout.txt`): node = local = go = `233f8cd2…`, `DIGEST_MATCH`, launched
  11:20:48Z (`launch.txt`).
- **Connect log** (`connect.log.txt`, `d079b2a627b93abda70c24caada209016339137dfc4bdb2a66ab0235b84138fe`), 11:20:46Z to 11:21:13Z:
  - `balance_node_h=1356.4 half=678.2 cap=110.0`;
  - `recompute spent=0.236 held=0.000 this=2.0 total=2.236 cap=110.0`;
  - `deploy porcelain=0 ignored=0 head=401733bc…`, and the 19 bound blobs `OK` (`job_bound-prepare.sha256.txt`);
  - `origin/main=c78b1a16…`, and the envtest record on origin/main `verdict=PASS sha256=c4a0720d…`;
  - a stat (no open) of the 13 inputs: `$UNI` (`/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/runEventLoopOmniFold_MEFHC_universes_full.root`,
    atime 10:39:23Z, from the envtest job 61220039) and P5's 12 per-playlist files (atimes 2026-10-14);
  - the gate (`job_gate-prepare-20261113T112100Z.psv.txt`, its `.gate.json.txt`): `pass` true, projection 109.436;
    the order (`job_order-prepare.json.txt`): `blocked_by` empty;
  - `2026-11-13T11:21:02Z M=401733bc… job=prepare id=61223390 limit=02:00:00` (`job_submissions.log.txt`),
    `submit prepare rc=0`, then scontrol `JobState=PENDING`.
- **Removal** (`removal.log.txt`): the staged script and the log in /dev/shm, `rm -f … rc=0`, and the `ls` after it
  finds neither. The launcher's `removal rc=2` (`launch-stdout.txt`) is that `ls`'s exit status.

## The job

- **sacct:** 61223390 `cov2dg2r-prepare`, COMPLETED, ExitCode 0:0, nid005845, MaxRSS 115165800K.
  - Start 2026-11-13T03:39:18 and End 04:39:36, Perlmutter local time (PST): 11:39:18Z to 12:39:36Z.
  - Elapsed 01:00:18.
- **Job log** (`job_cov2dg2r-prepare-61223390.out.txt`):
  - `UNI-STAT PASS`; `python 3.10.19 numpy 2.2.6 uproot 5.6.9`;
  - `[g2r] start 2026-11-13T11:39:32Z job=61223390 prepare node=nid005845`;
  - `G2R-PREPARE PASS`, the two products' sha256 lines, then `[g2r] end 2026-11-13T12:39:35Z rc=0`.
- **The record** (`g2r_prepare.json`, `d72facde6b73e854620bce58780928307fcb1fa9b3e921e94f03cbe6ec9ac1dc`), byte-identical
  to the node's copy. This is the path `g2r_jobs.PREPARE_RECORD` (g2r_jobs.py:69 at M) reads on origin/main.
  - `verdict` PASS, `stop` [];
  - `G5`: size 171117087867 = want, pass;
  - `G11`: Flux:0, Flux:87, MaRES:0 and VecFFCCQEshape:1 each `equal` true;
  - `atime`: checked 13, moved [];
  - 175 universes; `identity_universes` count 16 (its label: gates nothing);
  - `map_npz_sha256` `956531e3b761aaf08d40c6ab8d917ba5f19dab5947b72607e6a34d0d3f7f83ae`.
- **The map** is `/pscratch/sd/j/josephrb/cov2d-g2r-20261112/prepare/g2r_map.npz`, 143986060 B, not committed. Its
  sha256 in the record, in the job's own sha256 line, and from an O_NOATIME read on login38 at 12:41:39Z are the same.
- `$O/tmp/61223390` is empty.

## Atime and the LL5D overlap

The prepare read its 13 inputs through O_NOATIME, and its record reads `moved` []. None of the 13 is among LL5D's
1146 snapshot paths: `grep -c runEventLoopOmniFold ../envtest/r1_atime-pre.raw.txt` prints 0.

## The receipt checker

`verify_receipt_artifacts.py` read the record's 12 per-playlist input names (the files under
`/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/` that the connect log stats, named without a directory and
written by g2r_prepare.py `run()` into `blocks` and `map.blocks`) as bare file citations: 12 MISSING. The record is the
job's output and cannot be reworded. The director ruled (2026-11-13) that `EXEMPT_BARE` gets exactly these 12 pins at
this path and sha256 `d72facde…`, the same mechanism as #1139. With them the checker reads MISSING 0 and EXEMPT 13.
`test_verify_receipt_artifacts.py` binds each ruling's pins explicitly; emptying only the 12 gives 12 MISSING.
