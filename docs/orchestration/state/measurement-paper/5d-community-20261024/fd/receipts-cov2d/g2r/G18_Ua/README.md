# COV2D-G2R G18_Ua (job 61226562): COMPLETED 0:0; 44 runs, every rc 0 (2026-11-13)

**By** the `cov2d` session, under COV2D-G2R addendum J1 (code at M = `401733bce290ce122cfbf38f1526e120f174b3ec`).

- **Connect:** `connect-g2r-G18_Ua.sh`, `a5948d2e3205b54429dd8b29e22ca61e6453e636b8c5a6c686071df8c4f63555`. `G18_Ua-vs-D_Ub-4142a188.diff.txt` is its diff from the parent connect.
- **Launcher:** `launch-g2r.sh` `ebf576f5374ea778…` (its rebuild chain is in `../D_Ua/`, `../D_Ub/` and `../D_Uc/`).
- Full digests: `node-sha256.raw.txt` (this job's node files, read O_NOATIME) and `files.sha256` (every file here).

**CANNOT AUTHORIZE:** the G2R readout or any other job. Each needs its own go.

## The connect

- **Fence** (`fence.sh`, `fence.txt`), 2026-11-13T14:18:09Z: 8 jobs listed (61226525 cov2dg2r-D_Uc PENDING; 61226543 cov2dg2r-D_Ud PENDING; 61214614 ll5d_bulk_09 RUNNING; 61214615 ll5d_bulk_10 RUNNING; 61214610 ll5d_bulk_07 RUNNING; 61214612 ll5d_bulk_08 RUNNING; 61225732 cov2dg2r-D_Ua RUNNING; 61226353 cov2dg2r-D_Ub RUNNING), and no unended cov2d job outside `cov2dg2r-`. `launch-stdout.txt` reads `FENCE_CLEAR`.
- **Staging** (`staged_sha.txt`, `launch-stdout.txt`): node = local = go = `a5948d2e…`, `DIGEST_MATCH`, launched rc=0 at 2026-11-13T14:18:27Z (`launch.txt`).
- **Connect log** (`connect.log.txt`, `93e5cf4b64ae948a1f9cbd0738bb942884e72c070711db5a3881cac5327d8ba1`), 2026-11-13T14:18:25Z to 2026-11-13T14:18:47Z, host login02:
  - `balance_node_h=1328.8 half=664.4 cap=110.0`;
  - `recompute spent=1.241 held=36.000 this=8.9 total=46.141 cap=110.0`;
  - `deploy porcelain=0 ignored=0 head=401733bce290ce122cfbf38f1526e120f174b3ec`;
  - `origin/main=c29c2dfa21d58f3f7af762e051505cc549dc65b3`;
  - `envtest record on origin/main: verdict=PASS sha256=c4a0720d3a12265403d22e273e219d4594b03ba0a592afe671618ed72cbf0272`;
  - `prepare record on origin/main: verdict=PASS map_npz_sha256=956531e3b761aaf08d40c6ab8d917ba5f19dab5947b72607e6a34d0d3f7f83ae sha256=d72facde6b73e854620bce58780928307fcb1fa9b3e921e94f03cbe6ec9ac1dc`;
  - `map /pscratch/sd/j/josephrb/cov2d-g2r-20261112/prepare/g2r_map.npz sha256=956531e3b761aaf08d40c6ab8d917ba5f19dab5947b72607e6a34d0d3f7f83ae (O_NOATIME)`;
  - 19 bound blobs `OK` (`job_bound-G18_Ua.sha256.txt` is the node's list);
  - `input /pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/runEventLoopOmniFold_MEFHC_universes_full.root size=171117087867 atime=2026-11-13T10:39:23Z` (stat, no open);
  - `input /pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root size=5143 atime=2026-11-13T10:36:28Z` (stat, no open);
  - `input /pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/baseline_flux/flux_integral_universes_MEFHC.root size=6396 atime=2026-11-06T16:31:27Z` (stat, no open);
  - `input /pscratch/sd/j/josephrb/cov2d-g2r-20261112/prepare/g2r_map.npz size=143986060 atime=2026-11-13T14:13:57Z` (stat, no open);
  - `input /pscratch/sd/j/josephrb/cov2d-run-20261104/pseudo/G18/b/data_5721000.root size=51455930 atime=2026-11-06T17:01:38Z` (stat, no open);
  - `ll5d constraint /pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt atime_epoch=1793891894 (stat only; not a G18_Ua input)`;
  - the realization check (connect-g2r-G18_Ua.sh's block): `realization /pscratch/sd/j/josephrb/cov2d-run-20261104/pseudo/G18/b/data_5721000.root sha256=82c33320ceb9ce96967850148f97cbf873654609f0f8e1ac31b1491d5dd72eee (O_NOATIME) step-B record G18 sha256=82c33320ceb9ce96967850148f97cbf873654609f0f8e1ac31b1491d5dd72eee`;
  - the gate (`job_gate-*.psv.txt`, its `.gate.json.txt`): pass true, total 46.141, cap 110.0; the order (`job_order-G18_Ua.json.txt`): `{"job": "G18_Ua", "blocked_by": []}`;
  - `2026-11-13T14:18:37Z M=401733bce290ce122cfbf38f1526e120f174b3ec job=G18_Ua id=61226562 limit=08:54:00` (`job_submissions.log.txt`), `submit G18_Ua rc=0`, then scontrol `JobState=PENDING`; the log ends `DONE`.
- **Removal** (`removal.log.txt`): the staged script and the log in /dev/shm, `rm -f /dev/shm/josephrb-g2r-G18_Ua.sh /dev/shm/josephrb-g2r-G18_Ua.log rc=0`, and the `ls` after it finds neither. The launcher's `removal rc=2` (`launch-stdout.txt`) is that `ls`'s exit status.

## The job

- **sacct** (`../unfolds-all/sacct-utc.txt`, TZ=UTC): 61226562 `cov2dg2r-G18_Ua`, COMPLETED, ExitCode 0:0, nid004554; Start 2026-11-13T14:34:18Z, End 2026-11-13T19:38:43Z, Elapsed 05:04:25, limit 08:54:00.
- **Job log** (`job_cov2dg2r-G18_Ua-61226562.out.txt`): `[g2r] start 2026-11-13T14:34:43Z job=61226562 JOB=G18_Ua point=G18 node=nid004554` … `[g2r] end 2026-11-13T19:38:42Z rc=0`; `{"mat_setup_scripts": 6, "mismatches": 0}`.
- **Preflight** (`job_check-G18_Ua-61226562.json.txt`): runs 44, 5 inputs checked, problems []. **MAT** (`job_mat-61226562.json.txt`): 6 setup scripts hashed.
- **Walls** (`job_walls.G18_Ua.1.tsv`, `job_walls.G18_Ua.2.tsv`): 44 runs = the 44 `G18_Ua` labels of `runs_g2r.tsv` (`../unfolds-all/lane_check.out.txt`); rc 0 for every run; per-run wall 723–1277 s.
- **Sums** (`job_SHA256SUMS.G18_Ua.1.txt`, `job_SHA256SUMS.G18_Ua.2.txt`): 44 lines; the fetched `out/<label>/xsec.root` files match them (`../unfolds-all/sums-check.out.txt`).
- **Products:** 44 `xsec.root` files under `/pscratch/sd/j/josephrb/cov2d-g2r-20261112/out/<label>/`, with each label's log and inventory, are listed by sha256 in `node-sha256.raw.txt` and are not committed.

## Atime and the LL5D overlap

The job's inputs are the connect's `input` lines; none is among LL5D's 1146 snapshot paths, and the bulk's atime-post (2026-11-14T03:11:38Z, `atime-post-bulk.sh` 5806a902 under the director's go) reads 0 moved. The constraint file's atime is covered in `../D_Uc/README.md`.
