# COV2D-G2R G18_Uc (job 61226663): COMPLETED 0:0; 44 runs, every rc 0 (2026-11-13)

**By** the `cov2d` session, under COV2D-G2R addendum J1 (code at M = `401733bce290ce122cfbf38f1526e120f174b3ec`).

- **Connect:** `connect-g2r-G18_Uc.sh`, `defd72911ba782fc461ca06bffa8c10447352c8dd4043c7f2f4523cffe0df13b`. `G18_Uc-vs-D_Ub-4142a188.diff.txt` is its diff from the parent connect.
- **Launcher:** `launch-g2r.sh` `ebf576f5374ea778…` (its rebuild chain is in `../D_Ua/`, `../D_Ub/` and `../D_Uc/`).
- Full digests: `node-sha256.raw.txt` (this job's node files, read O_NOATIME) and `files.sha256` (every file here).

**CANNOT AUTHORIZE:** the G2R readout or any other job. Each needs its own go.

## The connect

- **Fence** (`fence.sh`, `fence.txt`), 2026-11-13T14:20:38Z: 10 jobs listed (61226579 cov2dg2r-G18_Ub PENDING; 61226562 cov2dg2r-G18_Ua PENDING; 61226543 cov2dg2r-D_Ud PENDING; 61226525 cov2dg2r-D_Uc PENDING; 61214614 ll5d_bulk_09 RUNNING; 61214615 ll5d_bulk_10 RUNNING; 61214610 ll5d_bulk_07 RUNNING; 61214612 ll5d_bulk_08 RUNNING; 61225732 cov2dg2r-D_Ua RUNNING; 61226353 cov2dg2r-D_Ub RUNNING), and no unended cov2d job outside `cov2dg2r-`. `launch-stdout.txt` reads `FENCE_CLEAR`.
- **Staging** (`staged_sha.txt`, `launch-stdout.txt`): node = local = go = `defd7291…`, `DIGEST_MATCH`, launched rc=0 at 2026-11-13T14:20:58Z (`launch.txt`).
- **Connect log** (`connect.log.txt`, `b7e600449923af40a560b08ce1e04534a07968739888f45ef9f3ba333556e3d6`), 2026-11-13T14:20:56Z to 2026-11-13T14:21:20Z, host login02:
  - `balance_node_h=1328.8 half=664.4 cap=110.0`;
  - `recompute spent=1.241 held=53.800 this=8.9 total=63.941 cap=110.0`;
  - `deploy porcelain=0 ignored=0 head=401733bce290ce122cfbf38f1526e120f174b3ec`;
  - `origin/main=c29c2dfa21d58f3f7af762e051505cc549dc65b3`;
  - `envtest record on origin/main: verdict=PASS sha256=c4a0720d3a12265403d22e273e219d4594b03ba0a592afe671618ed72cbf0272`;
  - `prepare record on origin/main: verdict=PASS map_npz_sha256=956531e3b761aaf08d40c6ab8d917ba5f19dab5947b72607e6a34d0d3f7f83ae sha256=d72facde6b73e854620bce58780928307fcb1fa9b3e921e94f03cbe6ec9ac1dc`;
  - `map /pscratch/sd/j/josephrb/cov2d-g2r-20261112/prepare/g2r_map.npz sha256=956531e3b761aaf08d40c6ab8d917ba5f19dab5947b72607e6a34d0d3f7f83ae (O_NOATIME)`;
  - 19 bound blobs `OK` (`job_bound-G18_Uc.sha256.txt` is the node's list);
  - `input /pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/runEventLoopOmniFold_MEFHC_universes_full.root size=171117087867 atime=2026-11-13T10:39:23Z` (stat, no open);
  - `input /pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root size=5143 atime=2026-11-13T10:36:28Z` (stat, no open);
  - `input /pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/baseline_flux/flux_integral_universes_MEFHC.root size=6396 atime=2026-11-06T16:31:27Z` (stat, no open);
  - `input /pscratch/sd/j/josephrb/cov2d-g2r-20261112/prepare/g2r_map.npz size=143986060 atime=2026-11-13T14:19:50Z` (stat, no open);
  - `input /pscratch/sd/j/josephrb/cov2d-run-20261104/pseudo/G18/b/data_5721000.root size=51455930 atime=2026-11-06T17:01:38Z` (stat, no open);
  - `ll5d constraint /pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt atime_epoch=1793891894 (stat only; not a G18_Uc input)`;
  - the realization check (connect-g2r-G18_Uc.sh's block): `realization /pscratch/sd/j/josephrb/cov2d-run-20261104/pseudo/G18/b/data_5721000.root sha256=82c33320ceb9ce96967850148f97cbf873654609f0f8e1ac31b1491d5dd72eee (O_NOATIME) step-B record G18 sha256=82c33320ceb9ce96967850148f97cbf873654609f0f8e1ac31b1491d5dd72eee`;
  - the gate (`job_gate-*.psv.txt`, its `.gate.json.txt`): pass true, total 63.941, cap 110.0; the order (`job_order-G18_Uc.json.txt`): `{"job": "G18_Uc", "blocked_by": []}`;
  - `2026-11-13T14:21:08Z M=401733bce290ce122cfbf38f1526e120f174b3ec job=G18_Uc id=61226663 limit=08:54:00` (`job_submissions.log.txt`), `submit G18_Uc rc=0`, then scontrol `JobState=PENDING`; the log ends `DONE`.
- **Removal** (`removal.log.txt`): the staged script and the log in /dev/shm, `rm -f /dev/shm/josephrb-g2r-G18_Uc.sh /dev/shm/josephrb-g2r-G18_Uc.log rc=0`, and the `ls` after it finds neither. The launcher's `removal rc=2` (`launch-stdout.txt`) is that `ls`'s exit status.

## The job

- **sacct** (`../unfolds-all/sacct-utc.txt`, TZ=UTC): 61226663 `cov2dg2r-G18_Uc`, COMPLETED, ExitCode 0:0, nid004939; Start 2026-11-13T14:43:01Z, End 2026-11-13T19:54:26Z, Elapsed 05:11:25, limit 08:54:00.
- **Job log** (`job_cov2dg2r-G18_Uc-61226663.out.txt`): `[g2r] start 2026-11-13T14:43:20Z job=61226663 JOB=G18_Uc point=G18 node=nid004939` … `[g2r] end 2026-11-13T19:54:26Z rc=0`; `{"mat_setup_scripts": 6, "mismatches": 0}`.
- **Preflight** (`job_check-G18_Uc-61226663.json.txt`): runs 44, 5 inputs checked, problems []. **MAT** (`job_mat-61226663.json.txt`): 6 setup scripts hashed.
- **Walls** (`job_walls.G18_Uc.1.tsv`, `job_walls.G18_Uc.2.tsv`): 44 runs = the 44 `G18_Uc` labels of `runs_g2r.tsv` (`../unfolds-all/lane_check.out.txt`); rc 0 for every run; per-run wall 679–1098 s.
- **Sums** (`job_SHA256SUMS.G18_Uc.1.txt`, `job_SHA256SUMS.G18_Uc.2.txt`): 44 lines; the fetched `out/<label>/xsec.root` files match them (`../unfolds-all/sums-check.out.txt`).
- **Products:** 44 `xsec.root` files under `/pscratch/sd/j/josephrb/cov2d-g2r-20261112/out/<label>/`, with each label's log and inventory, are listed by sha256 in `node-sha256.raw.txt` and are not committed.

## Atime and the LL5D overlap

The job's inputs are the connect's `input` lines; none is among LL5D's 1146 snapshot paths, and the bulk's atime-post (2026-11-14T03:11:38Z, `atime-post-bulk.sh` 5806a902 under the director's go) reads 0 moved. The constraint file's atime is covered in `../D_Uc/README.md`.
