# COV2D-G2R D_Ud (job 61226543): COMPLETED 0:0; 45 runs, every rc 0 (2026-11-13)

**By** the `cov2d` session, under COV2D-G2R addendum J1 (code at M = `401733bce290ce122cfbf38f1526e120f174b3ec`).

- **Connect:** `connect-g2r-D_Ud.sh`, `900df2baf42a896c168e710595636bcc72195b7323f91ad9db60c4fc1a8b870e`. `D_Ud-vs-D_Ub-4142a188.diff.txt` is its diff from the parent connect.
- **Launcher:** `launch-g2r.sh` `ebf576f5374ea778…` (its rebuild chain is in `../D_Ua/`, `../D_Ub/` and `../D_Uc/`).
- Full digests: `node-sha256.raw.txt` (this job's node files, read O_NOATIME) and `files.sha256` (every file here).

**CANNOT AUTHORIZE:** the G2R readout or any other job. Each needs its own go.

## The connect

- **Fence** (`fence.sh`, `fence.txt`), 2026-11-13T14:17:06Z: 7 jobs listed (61226525 cov2dg2r-D_Uc PENDING; 61214614 ll5d_bulk_09 RUNNING; 61214615 ll5d_bulk_10 RUNNING; 61214610 ll5d_bulk_07 RUNNING; 61214612 ll5d_bulk_08 RUNNING; 61225732 cov2dg2r-D_Ua RUNNING; 61226353 cov2dg2r-D_Ub RUNNING), and no unended cov2d job outside `cov2dg2r-`. `launch-stdout.txt` reads `FENCE_CLEAR`.
- **Staging** (`staged_sha.txt`, `launch-stdout.txt`): node = local = go = `900df2ba…`, `DIGEST_MATCH`, launched rc=0 at 2026-11-13T14:17:26Z (`launch.txt`).
- **Connect log** (`connect.log.txt`, `725c9822a391aaa9bcfedcab06da007ea4a3ca12ccb3b296f0c69888a66ae3dd`), 2026-11-13T14:17:24Z to 2026-11-13T14:17:47Z, host login02:
  - `balance_node_h=1328.8 half=664.4 cap=110.0`;
  - `recompute spent=1.241 held=26.700 this=9.3 total=37.241 cap=110.0`;
  - `deploy porcelain=0 ignored=0 head=401733bce290ce122cfbf38f1526e120f174b3ec`;
  - `origin/main=c29c2dfa21d58f3f7af762e051505cc549dc65b3`;
  - `envtest record on origin/main: verdict=PASS sha256=c4a0720d3a12265403d22e273e219d4594b03ba0a592afe671618ed72cbf0272`;
  - `prepare record on origin/main: verdict=PASS map_npz_sha256=956531e3b761aaf08d40c6ab8d917ba5f19dab5947b72607e6a34d0d3f7f83ae sha256=d72facde6b73e854620bce58780928307fcb1fa9b3e921e94f03cbe6ec9ac1dc`;
  - `map /pscratch/sd/j/josephrb/cov2d-g2r-20261112/prepare/g2r_map.npz sha256=956531e3b761aaf08d40c6ab8d917ba5f19dab5947b72607e6a34d0d3f7f83ae (O_NOATIME)`;
  - 19 bound blobs `OK` (`job_bound-D_Ud.sha256.txt` is the node's list);
  - `input /pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/runEventLoopOmniFold_MEFHC_universes_full.root size=171117087867 atime=2026-11-13T10:39:23Z` (stat, no open);
  - `input /pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root size=5143 atime=2026-11-13T10:36:28Z` (stat, no open);
  - `input /pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/baseline_flux/flux_integral_universes_MEFHC.root size=6396 atime=2026-11-06T16:31:27Z` (stat, no open);
  - `input /pscratch/sd/j/josephrb/cov2d-g2r-20261112/prepare/g2r_map.npz size=143986060 atime=2026-11-13T14:13:57Z` (stat, no open);
  - `ll5d constraint /pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt atime_epoch=1793891894 (stat only; not a D_Ud input)`;
  - the gate (`job_gate-*.psv.txt`, its `.gate.json.txt`): pass true, total 37.241, cap 110.0; the order (`job_order-D_Ud.json.txt`): `{"job": "D_Ud", "blocked_by": []}`;
  - `2026-11-13T14:17:35Z M=401733bce290ce122cfbf38f1526e120f174b3ec job=D_Ud id=61226543 limit=09:18:00` (`job_submissions.log.txt`), `submit D_Ud rc=0`, then scontrol `JobState=PENDING`; the log ends `DONE`.
- **Removal** (`removal.log.txt`): the staged script and the log in /dev/shm, `rm -f /dev/shm/josephrb-g2r-D_Ud.sh /dev/shm/josephrb-g2r-D_Ud.log rc=0`, and the `ls` after it finds neither. The launcher's `removal rc=2` (`launch-stdout.txt`) is that `ls`'s exit status.

## The job

- **sacct** (`../unfolds-all/sacct-utc.txt`, TZ=UTC): 61226543 `cov2dg2r-D_Ud`, COMPLETED, ExitCode 0:0, nid005924; Start 2026-11-13T14:29:02Z, End 2026-11-13T19:56:44Z, Elapsed 05:27:42, limit 09:18:00.
- **Job log** (`job_cov2dg2r-D_Ud-61226543.out.txt`): `[g2r] start 2026-11-13T14:29:25Z job=61226543 JOB=D_Ud point=data node=nid005924` … `[g2r] end 2026-11-13T19:56:42Z rc=0`; `{"mat_setup_scripts": 6, "mismatches": 0}`.
- **Preflight** (`job_check-D_Ud-61226543.json.txt`): runs 45, 4 inputs checked, problems []. **MAT** (`job_mat-61226543.json.txt`): 6 setup scripts hashed.
- **Walls** (`job_walls.D_Ud.1.tsv`, `job_walls.D_Ud.2.tsv`): 45 runs = the 45 `D_Ud` labels of `runs_g2r.tsv` (`../unfolds-all/lane_check.out.txt`); rc 0 for every run; per-run wall 734–1212 s.
- **Sums** (`job_SHA256SUMS.D_Ud.1.txt`, `job_SHA256SUMS.D_Ud.2.txt`): 45 lines; the fetched `out/<label>/xsec.root` files match them (`../unfolds-all/sums-check.out.txt`).
- **Products:** 45 `xsec.root` files under `/pscratch/sd/j/josephrb/cov2d-g2r-20261112/out/<label>/`, with each label's log and inventory, are listed by sha256 in `node-sha256.raw.txt` and are not committed.

## Atime and the LL5D overlap

The job's inputs are the connect's `input` lines; none is among LL5D's 1146 snapshot paths, and the bulk's atime-post (2026-11-14T03:11:38Z, `atime-post-bulk.sh` 5806a902 under the director's go) reads 0 moved. The constraint file's atime is covered in `../D_Uc/README.md`.
