# COV2D-G2R environment test (job 61220039): `envtest.json` reads verdict PASS, after r1, r2 and diag-tune (2026-11-13)

**By** the `cov2d` session, under COV2D-G2R addendum J1 (§2, §4; code at M = `401733bce290ce122cfbf38f1526e120f174b3ec`,
PRE_M = `a60547692df5f963e428cdfe4661fc51ab785b7b`). Four connects ran, each under its own go from the director:

| run | connect (sha256) | launcher (sha256) | go | where it ended |
|---|---|---|---|---|
| r1 | `connect-g2r-envtest.sh` `1b392259…` | `4a88370d…` | "1b392259 4a88370d" | STOP at the suite gate, 06:06:37Z; no job |
| r2 | `connect-g2r-envtest-r2.sh` `2ef9ce12…` | `8a35418a…` | "go 2ef9ce12 8a35418a", 06:49Z | STOP at the suite gate, 07:00:04Z; no job |
| diag-tune | `connect-g2r-diag-tune.sh` `84af1613…` | `a7ffe394…` | "go 84af1613 a7ffe394", 07:12Z | diagnostic only, 07:19:10Z; no job |
| r3 | `connect-g2r-envtest-r3.sh` `08ef6212…` | `60b624c6…` | "go 08ef6212 60b624c6", 09:32Z | suites passed; job 61220039 submitted 09:41:52Z |

Full digests: `node-sha256.raw.txt` (the node's files), `files.sha256` (every file here), and the `*_staged_sha.txt`
files (each staged connect's node-side sha256, which equals the committed connect).
- `launch-g2r.sh` here is r3's launcher (`60b624c6…`).
- `launch-chain.sh` rebuilds the earlier launchers from it and the four committed diffs, in reverse. Its output,
  `launch-chain.out.txt`, reads 60b624c6 → a7ffe394 → 8a35418a → 468f1992 → 4a88370d, then `LAUNCH-CHAIN PASS`.
  468f1992 is the launcher the director approved for the prepare (the prepare arm). It was on disk between r1 and r2,
  but no connect ran under it.
- `test_launch_g2r.sh` against `60b624c6…`: `test_launch_g2r.60b624c6.out.txt`, `LAUNCH-G2R TEST PASS`.

**CANNOT AUTHORIZE:** the prepare or any unfold job. Each needs its own go (J1 §2).

## The job (r3's submission)

- **sacct:** 61220039 `cov2dg2r-envtest`, COMPLETED, ExitCode 0:0, nid006712, TimelimitRaw 64.
  - Start 2026-11-13T02:35:40 and End 02:49:50, Perlmutter local time (PST): 10:35:40Z to 10:49:50Z.
  - Elapsed 00:14:10.
- **Job log** (`job_cov2dg2r-envtest-61220039.out.txt`):
  - `{"mat_setup_scripts": 6, "mismatches": 0}`;
  - `[g2r] start 2026-11-13T10:36:13Z job=61220039 envtest node=nid006712 pre=a6054769… M=401733bc…`;
  - the two products' sha256 lines;
  - `G2R-ENVTEST PASS`, then `[g2r] end 2026-11-13T10:49:49Z rc=0`.
- **`job_walls.tsv`:** both lanes started at epoch 1794566173 (10:36:13Z).
  - E_post_MaRES_0 ended at 1794566947 (774 s), rc 0.
  - E_pre_MaRES_0 ended at 1794566979 (806 s), rc 0.
- **The products** are in `/pscratch/sd/j/josephrb/cov2d-g2r-20261112/envtest/`. They are not committed.
  - `E_pre_MaRES_0.root`: `69a5db504bbebbad2cd91e0285f1dd91c5ebd965b711f8440a7ae86364c2a98b`.
  - `E_post_MaRES_0.root`: `2d43db0a724724457868d616ee01950e36925e9a56655280b56457b5c89bf987`.
  - These are the job's own sha256 lines, and an O_NOATIME read on login28 at 10:55:07Z gave the same values.

## `envtest.json`: held out of this commit, pending the director's ruling

`envtest.json` is `c4a0720d3a12265403d22e273e219d4594b03ba0a592afe671618ed72cbf0272`, the node's copy, read
O_NOATIME. J1 §2 names this directory as its committed place: `g2r_jobs.order` reads
`fd/receipts-cov2d/g2r/envtest/envtest.json` on origin/main before it lets the prepare go (`g2r_jobs.py:68` and
`:224-226` at M).
- With the file staged here, `verify_receipt_artifacts.py` failed with 1 MISSING. It reads the `set_aside` entry
  `runConfig.out`, a key name, as a bare `.out` file citation.
- Without the file, the same check reads 0 missing.
- The file is the job's record and is not edited. The shared checker is not a lane's to change. The director rules
  how the file lands.

Its fields, as written:
- `schema` cov2d-g2r-envtest-2, `tol` 1e-08, `verdict` PASS, `problems` [];
- 16 histograms, 10 named, 7 parameters;
- `rule` "RE-2 le per cell: max|a/b-1| over b!=0 (re2_k1.compare); b=0 cells |a|<=tol*max|b|".
- `all_bitwise` false.
  - Not bitwise: `hUnfold2D`, `hXSec2D`, `hXSec_pt`, `hXSec_pz` and `named:re2Refinement`. Every other entry in
    `bitwise` is true.
  - `hist_rel_diff` is 0.0 for the 12 bitwise histograms. For the other four it is:

| histogram | hist_rel_diff |
|---|---:|
| hUnfold2D | 1.332012278254524e-11 |
| hXSec2D | 1.3320233804847703e-11 |
| hXSec_pt | 4.543143639068603e-12 |
| hXSec_pz | 2.910005569844998e-12 |

- `set_aside`: driverFile, driverSha256, omnifoldHelperFile, runArgv, runConfig.out, runConfig.miss_map (null).

**Records listed by sha256 only, and not committed:**
- `check-envtest-61220039.json` (`94dc52b280a2e7df4510aab60f8458bd0382a9c78b4345b9e6730c9f21230220`): `runs` 2,
  3 inputs checked, `problems` [].
- `mat-61220039.json` (`447f07927853ef47fcb7b308fc21f0f1bf9e0228abd85d59a06bb33e9610777b`):
  `plotutils_mnvh1d_dictionary` true.
- `gate-envtest-20261113T094151Z.psv.gate.json` (`e65d973cd8101003fa34ca150b71f7b1bbe6bb88d82c14bbb7b361bb1aa66522`):
  `pass` true, `projection` 110.26666666666667, `total` 1.0666666666666667, `cap` 110.0.
- `order-envtest.json` (`d7d7304b4df4aa91b2b30eb8139273fdd505cf59435bb72e7d09da8d9693a249`): `blocked_by` [].

The first two carry path → digest maps. Each record's lines are quoted in `r3_connect.log.txt` or in this README.

## r1 (06:01Z to 06:08Z): the timing, then a STOP

**The timing, as it happened.** The director's order was: E96D's full job, then helper-2's post-full stat, then
`atime-around.sh pre`, then the envtest, then `atime-around.sh post` once the envtest ended.
- 06:01:05Z: helper-2's post-full stat arrived.
- 06:01:21Z: `pre` was taken on login30. It read 1146 paths, `stat_rc=0` (`r1_atime-pre.raw.txt`, `b0b29f38…`).
- 06:01:34Z: the launcher's fence was clear (`r1_fence.txt`).
- 06:02:04Z: the launch (`r1_launch.txt`).
- 06:05:08Z: the director's message reached this session's queue: hold `pre` and the envtest for about 15 minutes,
  because helper-2's E96D analyze step (a login node, 0 node-h) reads `data_b-_j-.npz` plainly. With it came
  helper-2's question: is that file in the 1146-path list? Both were read at 06:07:08Z, after the connect had
  returned. So `pre` and the connect overlapped analyze, which ended at 06:05:31Z.
- **analyze's file,** `/pscratch/sd/j/josephrb/s5p-20260926/runs/s2/num/data/data_b-_j-.npz`, is not in the list.
  The list has one `data_b-_j-` path, `/pscratch/sd/j/josephrb/fd-1b-inv-20261101/i0/in/jitter-data/data_b-_j-.npz`.
- 06:08:11Z: `post` was taken on login25 (`r1_atime-post.raw.txt`, `d7dc3d1c…`). It read NONE-MOVED: the 1146 atime
  lines are identical to pre's, and only the trailer line (seconds, end time) differs.
- The director's ruling 1: no harm; record it as it happened.

`atime-around.sh` (`cc28788f…`) and `atime-stat-list.sh` (`346656a7…`) are committed. Their test output is in
`test_atime_around.out.txt`: `ATIME-AROUND TEST PASS`, and mutants m1–m3 killed.

**The STOP** (`r1_connect.log.txt`, `217bed77…`, login02, 06:02:02Z to 06:06:37Z).
- The connect printed:
  - `balance_node_h=1384.0 half=692.0 cap=110.0`;
  - deploy porcelain 0 at M, with 19 bound sums OK;
  - the deploy-pre at PRE_M;
  - `suites env: python numpy ROOT = 3.11.14 1.26.4 6.28/12`.
- Suite results: `test_g2r` 27 OK, `test_re2_miss_map` 11 OK and `test_g2r_jobs` 58 OK. `test_g2r_glue` read
  `rc=1 Ran 11 tests … FAILED (errors=13)`, followed by `STOP the suites under the jobs' environment (rc 1)`. No sbatch
  was reached.
- The glue log is `r1_suite-test_g2r_glue.log.txt` (`f6373541…`). Its refusals are all the open audit's
  (`cov2d_blocks.GUARDED` = /global/cfs, /pscratch):
  - 4 opens of committed files in the /pscratch deploy (3 × `blocks_AR23.npz`, 1 × `E_AR23.npz`);
  - 9 opens of the suites' TMPDIR files under `$O`;
  - 13 `os.open` calls on the suites' temporary directories under `$O`.

**r1's local record was deleted twice and rebuilt** (`r1_RECOVERED.txt`). After r1, `test_launch_g2r.sh` removed the
launcher's record directory, which sat beside the test, between 06:26Z and about 06:28Z. The files were rebuilt from
the launcher's stdout in the session transcript.
- `r1_connect.log.txt` is byte-exact: its sha256 `217bed77…` equals the node-side sha256 in `r1_removal.log.txt`.
- `r1_removal.log.txt`, `r1_fence.txt`, `r1_staged_sha.txt` and `r1_launch.txt` are rebuilt and not byte-verified.
- The test now runs the launcher from a copy in its temporary directory (`test_launch_g2r.sh`, `5e3faf85…`).
- The node's r1 files (`r1_suite-*.log.txt`, `r1_bound.sha256.txt`, `r1_pre.sha256.txt`) were not touched, and their
  sha256 values are in `node-sha256.raw.txt`.

## r2 (06:51Z to 07:00Z): a STOP

- **The change** (`envtest-r2-vs-1b392259.diff.txt`, `a94f6609…`): the suites run in a `git clone --shared` of the
  deploy at M, under a fresh `mktemp -d` in /dev/shm. TMPDIR is inside that place, and the place is refused if it is
  under a guarded tree, `$O` or `$C`. The clone's HEAD, porcelain and 19 bound sums are checked. The place is
  removed on exit, and the removal is logged.
- **The test:** `test_envtest_r2_tmpdir.sh` (`acf3adbe…`, with `test_envtest_r2_tmpdir.py`, `396cfa54…`) runs the
  block verbatim in the cluster's layout. A local stand-in for /pscratch holds both `$O` and the deploy.
  `test_envtest_r2_tmpdir.vs-r2.out.txt` has 8 cases PASS, including the two controls. Under r1's layout, the controls
  fail as r1 did (Ran 11, errors=13). With only TMPDIR moved, they fail with Ran 14, errors=11.
- **The run** (`r2_connect.log.txt`, `e60bfbcc…`):
  - `suites place=/dev/shm/josephrb-g2r-suites.toyD3P … bound sums 19 OK`;
  - `test_g2r` 27 OK, `test_re2_miss_map` 11 OK and `test_g2r_jobs` 58 OK;
  - `test_g2r_glue rc=1 Ran 18 tests in 333.447s FAILED (failures=1)`;
  - the clone had porcelain 0 after the suites, and the place was removed with `left=no`; then the STOP. No sbatch.
- **The failure** (`r2_suite-test_g2r_glue.log.txt`): `PhaseTune.test_the_regrade_reproduces_the_committed_reading`
  fails with `AssertionError: 'STOP' != 'UNDER-COVERS'`.

## diag-tune (07:13Z to 07:19Z): the cause

`connect-g2r-diag-tune.sh` uses r2's fence, deploy check and place block. It embeds `diag_phasetune.py`
(`DIAG-SHA OK 4558b490…` in the log), which runs `PhaseTune.setUpClass` and prints the record (`diag_connect.log.txt`,
`6ea8e2c1…`; the node's copy is `diag_diag.log.txt`). The record read:
- `verdict` STOP and `verdict_graded` UNDER-COVERS;
- `stop` ["atime moved on 170 inputs"], with `atime_checked` 175;
- every moved path a test stand-in under the place's TMPDIR;
- `open_audit`: 538 opens, `refused` [], `guarded_opens_total` 0;
- every module imported from the clone.

**The mechanism.** `test_g2r_glue` patches `os.O_NOATIME` to 0 with `create=True` (`test_g2r_glue.py:256, 314, 387,
501` at M), so the stand-ins are read plainly, on Linux too. On tmpfs (/dev/shm, relatime, coarse timestamps), the
read that hashes a just-written file leaves atime ≤ mtime, so the read after `Run.watch` moves atime.

**The measurement,** `atime-probe-login13-20261113.txt`, login13, 2026-11-13T07:21:10Z: `/dev/shm moved 39 of 40`,
and `/global/homes/j/josephrb moved 0 of 40`.
- Each probe file was written, read, left 10 ms, stat'ed, read again and stat'ed again.
- The file was rebuilt from the session transcript.
- Its heredoc follows the same pattern as r3's in-connect probe but is not the same bytes.

The director put the test-side fix (patch only where `os` lacks `O_NOATIME`) on the post-paper list. It needs a new
commit and a new binding.

## r3 (09:33Z to 09:42Z): the suites on $HOME, then the submission

- **The change** (`envtest-r3-vs-2ef9ce12.diff.txt`, `d612bdeb…`):
  - the place's base moves to `/global/homes/j/josephrb/g2r-suites-place` (GPFS, not a guarded tree);
  - the record directory moves to `$O/logs/envtest-r3`;
  - an atime probe runs before the suites: 40 files in `$TMPDIR/atprobe`, and the connect exits 10 if any atime
    moved;
  - the place block is byte-identical to r2's.
- **The test:** `test_envtest_r2_tmpdir.sh` against r3: `test_envtest_r2_tmpdir.vs-r3.out.txt`, 8 of 8 PASS.
- **The run** (`r3_connect.log.txt`, `ec7f47a6…`, login02):
  - the fence listed only `ll5d_bulk_01`–`10`. Six were RUNNING and four PENDING. The director's ruling 4 lets G2R
    overlap the bulk under the audited static fence;
  - `balance_node_h=1373.6 half=686.8 cap=110.0`, and `recompute spent=0.000 held=0.000 this=1.067 total=1.067`;
  - deploy porcelain 0 at M, 19 bound sums OK, and the deploy-pre at PRE_M;
  - `suites place=/global/homes/j/josephrb/g2r-suites-place/josephrb-g2r-suites.HDZRrZ … bound sums 19 OK`;
  - `atime probe: moved 0 of 40`;
  - `test_g2r` 27 OK, `test_re2_miss_map` 11 OK, `test_g2r_glue rc=0 Ran 18 tests in 327.851s OK` and `test_g2r_jobs`
    58 OK;
  - the clone had porcelain 0 after the suites, and the place was removed with `left=no`. Deploy porcelain was 0
    after the suites;
  - the gate: `projection` 110.267 and `pass` true. Its sacct snapshot is `r3_gate-envtest-20261113T094151Z.psv.txt`;
  - `2026-11-13T09:41:52Z M=401733bc… job=envtest id=61220039 limit=01:04:00`, `sacct lists 61220039`,
    `submit envtest rc=0`, and scontrol showed JobState PENDING.

## Removals

- **/dev/shm on login02:** each launch staged its connect and log there and removed them after the run, with `rm -f`
  rc 0 and the closing `ls` finding neither file (`r1_`, `r2_`, `diag_`, `r3_removal.log.txt`).
  - Each log's node-side sha256 equals the committed `*_connect.log.txt`.
  - For diag-tune, the committed connect log is the launcher's capture. The node's log is `diag_diag.log.txt`.
- **The suites' places** were removed by the connect's EXIT trap, each logged as `left=no`: r2 and diag-tune in
  /dev/shm, and r3 in `~/g2r-suites-place`. After r3, `~/g2r-suites-place` was empty, and login02's /dev/shm held no
  `josephrb` file.
- **The atime probes:** login13's two probe directories were removed, rc 0 (in the probe file). r3's `atprobe`
  directory was removed by `rmdir` inside the connect.

## Files

The node's files carry a `.txt` suffix here, and their contents are unchanged. Each matches its line in
`node-sha256.raw.txt` (read O_NOATIME on login28, 2026-11-13T10:55:07Z).

| prefix | what |
|---|---|
| `r1_`, `r2_`, `diag_`, `r3_` | per run: the launcher's capture (`connect.log`, `fence`, `staged_sha`, `launch`, `removal.log`) and the node's suite logs, `bound.sha256` and `pre.sha256` |
| `job_` | job 61220039's log, the two driver logs and `walls.tsv` |
| `connect-g2r-*.sh`, `launch-g2r.sh`, `*.diff.txt` | the scripts that ran, and the diffs between them |
| `test_*.sh`, `test_*.py`, `test_*.out.txt` | the tests named above, with their outputs |
| `atime-*.sh`, `r1_atime-*.raw.txt` | the r1 bracket and its two readings |
