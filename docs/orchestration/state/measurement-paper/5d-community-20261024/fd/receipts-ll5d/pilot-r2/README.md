# LL5D ll5d_pilot r2 (job 61184880): the step ended rc 0; walls `verdict=PASS`, controls PASS, clipcheck PROCEED; 13 of the 13 pilot items ran (2026-11-12)

**By** the `cov2d` session, under LL5D BINDING 3 and its addendum A1b.1 (M_A1b.1 `4231b14d…`). This is the rerun
after the r1 STOP (job 61181899, `../pilot-r1/`), with the director's go on:
- `connect-pilot.sh` `0945ba5fd63e12e0cb9ba61fb773c2c4c23824d01eb4d60596cd7d5c1a14ba10`, diff
  `pilot-r2-vs-177f4f4d.diff.txt` against r1's connect. The diff carries two changes:
  - the namespace moved to r2 (`W=$P/ll5d-pilot-r2`, `U=$P/ll5d-unfolds-r2`);
  - the lane loop reads its table on fd 3 (`read -r -u 3 … done 3< <(…)`), and its `srun` takes `< /dev/null`.
- `launch-ll5d.sh` `4cd22193a1dcce3c3b1666a24c52ef94422fe9303df0cdac020ba5e697aa7bf5`: the pilot's log path set to
  r2. Diff `launch-vs-d4155c14.diff.txt`.

The watcher was `watch-gates2h.sh` `8042e2b6…`, committed in `../pilot-r1/`.

- **The step's own result:**
  - the watcher's last sacct line reads COMPLETED, ExitCode 0:0, Elapsed 00:30:31 (1,831 s), Start
    2026-11-12T11:23:45 and End 11:54:16 (Perlmutter local time, PST);
  - the job log reads `walls rc=0` / `LL5D-WALLS verdict=PASS`, `controls rc=0` /
    `LL5D-CONTROLS verdict=PASS failed=[]`, and `clipcheck rc=0` / `LL5D-CLIPCHECK verdict=PROCEED`.
- **Routing:** reported to the director.
- **CANNOT AUTHORIZE:** the bulk. Its connect is filled from this receipt and goes to the director first.

## The lane-loop repair test

`test-lane-loop.sh` (`4ca3b313…`) runs each connect's own lanes table and its own `lane()` function, extracted
verbatim, against a stub `srun`. The stub reads its stdin, and any line it receives counts as a leak. Its output is in
`test-lane-loop.out.txt` (`a7843cd9…`):

| run | rows | missing | leaks | result |
|---|---:|---:|---:|---|
| r2 pilot connect `0945ba5f…` | 11 | 0 | 0 | PASS |
| bulk connect `49d0600c…` | 86 | 0 | 0 | PASS |
| r1 pilot connect `177f4f4d…` | 11 | 3 | 7 | FAIL |
| bulk draft `f64f4100…` | 86 | 6 | 79 | FAIL |

Its two mutants are killed for both connects:
- M1 removes `< /dev/null` and is killed by the leak check;
- M2 restores r1's loop and is killed by the rows check.

## What ran

- `pilot-lanes.tsv` (`0718aa23…`, the same as r1's) lists ll5d_b.PILOT's 13 items in 11 rows over 8 lanes. Lanes 0, 4
  and 5 carry two rows each, and lanes 6 and 7 hold two items in one row.
- The job log reads `lanes=8 items=13 unique=13 pilot=13`, and 11 `lane … rc=0` lines, one per table row.
- `lanes/lane{0-7}.out.txt` hold 13 product lines. Each of lanes 0, 4 and 5 holds two product lines and two `rc=0`
  lines.

## The walls

From `walls.json`, `seconds_unfold` and peak RSS per product:

| product | seconds_unfold | peak RSS (KiB) |
|---|---:|---:|
| data_control setA_b1 | 663.349 | 24,731,884 |
| data_control MaRES_0 | 676.679 | 18,433,300 |
| data_control Flux_0 | 668.948 | 18,375,716 |
| data_control GEANT_Pion_0 | 675.998 | 18,342,340 |
| g18 central T | 818.355 | 19,867,308 |
| ar23 central T | 817.027 | 19,769,212 |
| g18 clipmean minus2 | 891.582 | 21,365,648 |
| g18 clipmean all | 874.784 | 21,365,648 |
| ar23 clipmean minus2 | 889.193 | 21,218,632 |
| ar23 clipmean all | 871.763 | 21,398,648 |
| g18 toy minus2_4751000 | 903.057 | 20,027,368 |
| g18 toy all_4751000 | 906.743 | 19,929,036 |
| ar23 stat 1 | 687.214 | 24,760,140 |

`walls.json` also reads:
- `max_seconds_unfold` 906.743 against `unit_seconds` 1062.0;
- `max_peak_rss_kib` 24,760,140 against `rss_limit_kib` 44,040,192.

## The outputs

- **The step's three records are NOT committed:**
  - `walls.json` (`9377977cc9ea330522291363899e6a9a7f233ef71469f46fca184421bbe81e48`);
  - `controls.json` (`82cc5858263164d7f5dc5977730484c385d960a1bb135208bd5b1f208e9cf2ec`);
  - `clipcheck.json` (`9632540ecd0d25e2223eedb480b96078459a6e6d75128b4e4132ea1bf644d3aa`).

  The reasons are the same as r1's (#687, `../pilot-r1/`):
  - `walls.json` names products by bare filename;
  - the other two carry path and `_sha256` key pairs.

  These sha256 values are the job's own lines in `ll5d_pilot_61184880.out.txt`, and the fetched copies match them.
  Their three `.out` files are committed.
- **Their decisive fields, as written:**
  - `walls.json`: `verdict` PASS, every `rows` entry in the table above, `atime.moved` [].
  - `controls.json`: `verdict` PASS and `failed` []. Each of `setA_b1`, `MaRES_0`, `Flux_0` and `GEANT_Pion_0` reads
    `equal` True, `elements_differing` 0 and `max_abs_difference` 0.0. Each has shape [65856] and dtype `<f8` on both
    sides. `atime.moved` [].
  - `clipcheck.json`: `verdict` PROCEED, `delta_star` 0.667, `cells` [], and `cells_at_or_above_delta_star` [] for
    each of `g18/all`, `g18/minus2`, `ar23/all` and `ar23/minus2`. `clip_prep_sha256` reads g18 `76154b20…` and ar23
    `c567183d…`, and `atime.moved` is []. Its `sigma` field reads "S1's reported (fd_data_product
    C_total_plus_C_resp), a proxy for C_T".
- **The 13 products** in `/pscratch/sd/j/josephrb/ll5d-unfolds-r2/` are listed by sha256 in the job log. They are not
  committed, because the repository ignores `*.npz`.
- **The sealed clip-prep files** were read only inside `ll5d_b.read_clip_prep`. The connect log reads
  `clip_prep_sha256_matches=True` for both truths. They were not fetched.
- **The fetched files** match the node's sha256 (login12, 2026-11-13T00:32:39Z, `node-sha256.raw.txt`).
  - `node-sha256.txt` lists 29 files, and `shasum -c` reads all 29 OK.
  - 26 are committed here, and the three JSON records are listed by sha256 only.
  - The `.log` and `.out` files carry a `.txt` suffix here.

## r1's products (the director's ruling k6)

There is no HPSS step for r1's products in `/pscratch/sd/j/josephrb/ll5d-unfolds-r1/` and
`/pscratch/sd/j/josephrb/ll5d-pilot-r1/`. They are left to age out of scratch. `hpss-ll5d.sh` (`227407d6…`, not run
here) names neither `ll5d-pilot-r1` nor `ll5d-unfolds-r1`. Its `pilot` case names `ll5d-pilot-r2`, and its `bulk` case names `ll5d-bulk-r1` and
`ll5d-unfolds-r2`, the directory that holds this pilot's 13 products.

## The run

- **The launch** (`launch-stdout.txt`):
  - `fence host=login02 utc=2026-11-12T19:21:18Z`: squeue was empty and no cov2d job was unended (`fence.txt`);
  - the staged connect's node sha256 matched the local file and the go (`staged_sha.txt`);
  - it launched at 19:21:37Z (`launch.txt`);
  - the `/dev/shm` copy was removed, with `rm -f` rc 0 and the closing `ls` finding nothing (`removal.log.txt`).
- **The connect** (`connect-pilot.log.txt`):
  - `balance_node_h=1442.3 half=721.1 cap=148.0`;
  - `projection charged=46.115 held=0.000 this=1.0 total=47.115 cap=148.0`;
  - both gate records read verdict PASS, and their clip-prep digests match;
  - the deploy had porcelain 0 at `4231b14d…`, and all 22 bound blobs were OK;
  - `job script sha256 cd7e146a…`, which is the fetched `sbatch-ll5d-pilot.sh`'s sha256;
  - atime-pre: 1146 files at 19:22:37Z;
  - TimeLimit=01:00:00.
- **The job** (`ll5d_pilot_61184880.out.txt`): it started at 19:23:48Z on nid006887, and its closing line reads
  `end=2026-11-12T19:54:15Z`.
- **Cost:** 0.509 node-h (1,831 s on one node).

## Atimes

- atime-post was taken stat-only by `atime-post-2.sh` (`e75bebe9…`), the same script as r1's, on login26.
  - It started at 2026-11-12T23:14:20Z, and its `find` ended at 2026-11-13T00:32:03Z with `find_rc=0`.
  - The `find` took 78 minutes. r1's took about one minute. No cause has been established, and a timing line is on
    the follow-up list.
- It is identical to `atime-pre.tsv` (`diff` rc 0), so 0 of 1146 files moved. This `atime-pre.tsv` is also identical
  to r1's.
- E96D A1 full was held until this time was sent to director-helper-2.

## The watchers

- `watcher-exits.txt` holds `watch-gates2h`'s own output. It exited on `JOB-EVENT 2026-11-12T19:58:26Z … COMPLETED …
  0:0`.
- `watch.log.txt` holds the shared log's 8 lines for 61184880:
  - the first, at 19:23:01Z, reads PENDING;
  - from 19:28:04Z the job reads RUNNING;
  - the last, at 19:58:26Z, reads COMPLETED.

## Files

`README.md`, `atime-post-2.sh`, `atime-post.raw.txt`, `atime-post.tsv`, `atime-pre.tsv`, `bound.sha256`,
`clipcheck.out.txt`, `connect-pilot.log.txt`, `connect-pilot.sh`, `controls.out.txt`, `env-job.log.txt`, `fence.txt`,
`lanes/lane{0-7}.out.txt`, `lanes/lane{0-7}.time`, `launch-ll5d.sh`, `launch-stdout.txt`,
`launch-vs-d4155c14.diff.txt`, `launch.txt`, `ll5d_pilot_61184880.out.txt`, `node-sha256.raw.txt`, `node-sha256.txt`,
`pilot-lanes.tsv`, `pilot-r2-vs-177f4f4d.diff.txt`, `removal.log.txt`, `sbatch-ll5d-pilot.sh`, `staged_sha.txt`,
`test-lane-loop.out.txt`, `test-lane-loop.sh`, `walls.out.txt`, `watch.log.txt`, `watcher-exits.txt`.
