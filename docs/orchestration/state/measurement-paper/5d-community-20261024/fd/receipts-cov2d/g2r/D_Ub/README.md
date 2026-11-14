# COV2D-G2R D_Ub (job 61226353): COMPLETED 0:0; 44 runs, every rc 0 (2026-11-13)

**By** the `cov2d` session, under COV2D-G2R addendum J1 (code at M = `401733bce290ce122cfbf38f1526e120f174b3ec`).

- **Connect:** `connect-g2r-D_Ub.sh`, `4142a188d7fbed9ba3fe3e76d0db5002dd2f1a5eddc7031cc4dd480f8c75cda9`. `D_Ub-vs-D_Ua-46005ade.diff.txt` is its diff from the parent connect.
- **Launcher:** `launch-g2r.sh` `05b4d1d9fb29a19f…` (its rebuild chain is in `../D_Ua/`, `../D_Ub/` and `../D_Uc/`).
- **Go:** the director, "go 4142a188 05b4d1d9", with the fence ruling (G2R jobs may run concurrently; the connect fence admits `^cov2dg2r-`) and the pre-launch path condition below.
- **Launcher chain:** `launch-g2r.sh` here is `05b4d1d9…`, the copy that ran; `launch-g2r-D_Ub-vs-60a18603.diff.txt` applied to `../D_Ua/launch-g2r.sh` rebuilds it byte-exact. `test_launch_g2r.05b4d1d9.out.txt`: `LAUNCH-G2R TEST PASS`.
- Full digests: `node-sha256.raw.txt` (this job's node files, read O_NOATIME) and `files.sha256` (every file here).

**CANNOT AUTHORIZE:** the G2R readout or any other job. Each needs its own go.

## The connect

- **Fence** (`fence.sh`, `fence.txt`), 2026-11-13T14:03:11Z: 6 jobs listed (61214607 ll5d_bulk_05 RUNNING; 61214614 ll5d_bulk_09 RUNNING; 61214615 ll5d_bulk_10 RUNNING; 61214610 ll5d_bulk_07 RUNNING; 61214612 ll5d_bulk_08 RUNNING; 61225732 cov2dg2r-D_Ua RUNNING), and no unended cov2d job outside `cov2dg2r-`. `launch-stdout.txt` reads `FENCE_CLEAR`.
- **Staging** (`staged_sha.txt`, `launch-stdout.txt`): node = local = go = `4142a188…`, `DIGEST_MATCH`, launched rc=0 at 2026-11-13T14:03:30Z (`launch.txt`).
- **Connect log** (`connect.log.txt`, `aa1b49a022a5e2e79763cf9a498b5ab6c77713017387a8e27e9bdcceaf88fd56`), 2026-11-13T14:03:28Z to 2026-11-13T14:03:52Z, host login02:
  - `balance_node_h=1328.8 half=664.4 cap=110.0`;
  - `recompute spent=1.241 held=8.900 this=8.9 total=19.041 cap=110.0`;
  - `deploy porcelain=0 ignored=0 head=401733bce290ce122cfbf38f1526e120f174b3ec`;
  - `origin/main=c29c2dfa21d58f3f7af762e051505cc549dc65b3`;
  - `envtest record on origin/main: verdict=PASS sha256=c4a0720d3a12265403d22e273e219d4594b03ba0a592afe671618ed72cbf0272`;
  - `prepare record on origin/main: verdict=PASS map_npz_sha256=956531e3b761aaf08d40c6ab8d917ba5f19dab5947b72607e6a34d0d3f7f83ae sha256=d72facde6b73e854620bce58780928307fcb1fa9b3e921e94f03cbe6ec9ac1dc`;
  - `map /pscratch/sd/j/josephrb/cov2d-g2r-20261112/prepare/g2r_map.npz sha256=956531e3b761aaf08d40c6ab8d917ba5f19dab5947b72607e6a34d0d3f7f83ae (O_NOATIME)`;
  - 19 bound blobs `OK` (`job_bound-D_Ub.sha256.txt` is the node's list);
  - `input /pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/runEventLoopOmniFold_MEFHC_universes_full.root size=171117087867 atime=2026-11-13T10:39:23Z` (stat, no open);
  - `input /pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root size=5143 atime=2026-11-13T10:36:28Z` (stat, no open);
  - `input /pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/baseline_flux/flux_integral_universes_MEFHC.root size=6396 atime=2026-11-06T16:31:27Z` (stat, no open);
  - `input /pscratch/sd/j/josephrb/cov2d-g2r-20261112/prepare/g2r_map.npz size=143986060 atime=2026-11-13T13:53:34Z` (stat, no open);
  - `ll5d constraint /pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt atime_epoch=1793891894 (stat only; not a D_Ub input)`;
  - the gate (`job_gate-*.psv.txt`, its `.gate.json.txt`): pass true, total 19.041, cap 110.0; the order (`job_order-D_Ub.json.txt`): `{"job": "D_Ub", "blocked_by": []}`;
  - `2026-11-13T14:03:42Z M=401733bce290ce122cfbf38f1526e120f174b3ec job=D_Ub id=61226353 limit=08:54:00` (`job_submissions.log.txt`), `submit D_Ub rc=0`, then scontrol `JobState=PENDING`; the log ends `DONE`.
- **Removal** (`removal.log.txt`): the staged script and the log in /dev/shm, `rm -f /dev/shm/josephrb-g2r-D_Ub.sh /dev/shm/josephrb-g2r-D_Ub.log rc=0`, and the `ls` after it finds neither. The launcher's `removal rc=2` (`launch-stdout.txt`) is that `ls`'s exit status.
- **Fence test** (`test_fence_g2r.sh`, `test_fence_g2r.out.txt`, 11 cases over the connect's and the launcher's fences): `FENCE-G2R TEST PASS`. The connect block test against this connect (`test_connect_dua.D_Ub.out.txt`) is byte-identical to D_Ua's output: `CONNECT-DUA BLOCK TEST PASS`.
- **Pre-launch path check** (`check_dub_paths.py` `1f083854…`): `check_dub_paths.out.txt` reads `DUB-PATHS PASS` (labels disjoint; D_Ua and D_Ub write 184 paths each, shared []). Its first run (`check_dub_paths.first-run-regex-artifact.out.txt`) read `STOP` only because the regex took a trailing `;` into `$O/tmp/${SLURM_JOB_ID:-dry};`. The regex was fixed to exclude `;`; that first output is kept as it was.

## The job

- **sacct** (`../unfolds-all/sacct-utc.txt`, TZ=UTC): 61226353 `cov2dg2r-D_Ub`, COMPLETED, ExitCode 0:0, nid004633; Start 2026-11-13T14:13:18Z, End 2026-11-13T19:31:13Z, Elapsed 05:17:55, limit 08:54:00.
- **Job log** (`job_cov2dg2r-D_Ub-61226353.out.txt`): `[g2r] start 2026-11-13T14:13:43Z job=61226353 JOB=D_Ub point=data node=nid004633` … `[g2r] end 2026-11-13T19:31:10Z rc=0`; `{"mat_setup_scripts": 6, "mismatches": 0}`.
- **Preflight** (`job_check-D_Ub-61226353.json.txt`): runs 44, 4 inputs checked, problems []. **MAT** (`job_mat-61226353.json.txt`): 6 setup scripts hashed.
- **Walls** (`job_walls.D_Ub.1.tsv`, `job_walls.D_Ub.2.tsv`): 44 runs = the 44 `D_Ub` labels of `runs_g2r.tsv` (`../unfolds-all/lane_check.out.txt`); rc 0 for every run; per-run wall 757–1133 s.
- **Sums** (`job_SHA256SUMS.D_Ub.1.txt`, `job_SHA256SUMS.D_Ub.2.txt`): 44 lines; the fetched `out/<label>/xsec.root` files match them (`../unfolds-all/sums-check.out.txt`).
- **Products:** 44 `xsec.root` files under `/pscratch/sd/j/josephrb/cov2d-g2r-20261112/out/<label>/`, with each label's log and inventory, are listed by sha256 in `node-sha256.raw.txt` and are not committed.

## Atime and the LL5D overlap

The job's inputs are the connect's `input` lines; none is among LL5D's 1146 snapshot paths, and the bulk's atime-post (2026-11-14T03:11:38Z, `atime-post-bulk.sh` 5806a902 under the director's go) reads 0 moved. The constraint file's atime is covered in `../D_Uc/README.md`.
