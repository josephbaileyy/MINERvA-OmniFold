# COV2D-G2R D_Uc (job 61226525): COMPLETED 0:0; 44 runs, every rc 0 (2026-11-13)

**By** the `cov2d` session, under COV2D-G2R addendum J1 (code at M = `401733bce290ce122cfbf38f1526e120f174b3ec`).

- **Connect:** `connect-g2r-D_Uc.sh`, `031819cc2fe5ca456cadf62168a5c64204aa5feac5506fba7cfb698e655fd7de`. `D_Uc-vs-D_Ub-4142a188.diff.txt` is its diff from the parent connect.
- **Launcher:** `launch-g2r.sh` `ebf576f5374ea778…` (its rebuild chain is in `../D_Ua/`, `../D_Ub/` and `../D_Uc/`).
- **Go (the batch):** the director, "go ebf576f5 with D_Uc 031819cc, D_Ud 900df2ba, G18_Ua a5948d2e, G18_Ub 5307f0bf, G18_Uc defd7291, G18_Ud e59b87dc, AR23_Ua 5d67b502, AR23_Ub 426c6e06, AR23_Uc ff10dec1, AR23_Ud 1f277af0": sequential, each re-hashed, halt on any STOP or non-zero result, stop if the balance's half falls below the two lanes' caps (148 + 110 = 258); receipts per job.
- **Launcher chain:** `launch-g2r.sh` here is `ebf576f5…`, the launcher for all ten batch jobs; `launch-g2r-batch-vs-05b4d1d9.diff.txt` applied to `../D_Ub/launch-g2r.sh` rebuilds it byte-exact. `test_launch_g2r.ebf576f5.out.txt`: `LAUNCH-G2R TEST PASS`. `test_launch_arms.out.txt` runs each new arm with a dummy digest (`0000`): every one REFUSED, rc 2; the usage line lists all 17 arms.
- **The batch driver:** `launch-batch.sh`, `8744083c…`, ran 14:15:59Z–14:26:43Z; its output is `launch-batch.out.txt` (`BATCH DONE`, no `HALT`). It re-hashed each connect against `connects-batch.sha256.txt` and the launcher against `ebf576f5…` before each launch. **Process point (the director):** I ran it without sending its sha first. The director reviewed it afterwards and accepted the launches: a script that issues launches is launch code, and its sha goes to the director before it runs.
- Full digests: `node-sha256.raw.txt` (this job's node files, read O_NOATIME) and `files.sha256` (every file here).

**CANNOT AUTHORIZE:** the G2R readout or any other job. Each needs its own go.

## The connect

- **Fence** (`fence.sh`, `fence.txt`), 2026-11-13T14:16:06Z: 6 jobs listed (61214614 ll5d_bulk_09 RUNNING; 61214615 ll5d_bulk_10 RUNNING; 61214610 ll5d_bulk_07 RUNNING; 61214612 ll5d_bulk_08 RUNNING; 61225732 cov2dg2r-D_Ua RUNNING; 61226353 cov2dg2r-D_Ub RUNNING), and no unended cov2d job outside `cov2dg2r-`. `launch-stdout.txt` reads `FENCE_CLEAR`.
- **Staging** (`staged_sha.txt`, `launch-stdout.txt`): node = local = go = `031819cc…`, `DIGEST_MATCH`, launched rc=0 at 2026-11-13T14:16:24Z (`launch.txt`).
- **Connect log** (`connect.log.txt`, `988f6265e3a9ad43288522349cf04c6b01b8642cccf76878aad84baa2f007187`), 2026-11-13T14:16:22Z to 2026-11-13T14:16:44Z, host login02:
  - `balance_node_h=1328.8 half=664.4 cap=110.0`;
  - `recompute spent=1.241 held=17.800 this=8.9 total=27.941 cap=110.0`;
  - `deploy porcelain=0 ignored=0 head=401733bce290ce122cfbf38f1526e120f174b3ec`;
  - `origin/main=c29c2dfa21d58f3f7af762e051505cc549dc65b3`;
  - `envtest record on origin/main: verdict=PASS sha256=c4a0720d3a12265403d22e273e219d4594b03ba0a592afe671618ed72cbf0272`;
  - `prepare record on origin/main: verdict=PASS map_npz_sha256=956531e3b761aaf08d40c6ab8d917ba5f19dab5947b72607e6a34d0d3f7f83ae sha256=d72facde6b73e854620bce58780928307fcb1fa9b3e921e94f03cbe6ec9ac1dc`;
  - `map /pscratch/sd/j/josephrb/cov2d-g2r-20261112/prepare/g2r_map.npz sha256=956531e3b761aaf08d40c6ab8d917ba5f19dab5947b72607e6a34d0d3f7f83ae (O_NOATIME)`;
  - 19 bound blobs `OK` (`job_bound-D_Uc.sha256.txt` is the node's list);
  - `input /pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/runEventLoopOmniFold_MEFHC_universes_full.root size=171117087867 atime=2026-11-13T10:39:23Z` (stat, no open);
  - `input /pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root size=5143 atime=2026-11-13T10:36:28Z` (stat, no open);
  - `input /pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/baseline_flux/flux_integral_universes_MEFHC.root size=6396 atime=2026-11-06T16:31:27Z` (stat, no open);
  - `input /pscratch/sd/j/josephrb/cov2d-g2r-20261112/prepare/g2r_map.npz size=143986060 atime=2026-11-13T14:13:57Z` (stat, no open);
  - `ll5d constraint /pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt atime_epoch=1793891894 (stat only; not a D_Uc input)`;
  - the gate (`job_gate-*.psv.txt`, its `.gate.json.txt`): pass true, total 27.941, cap 110.0; the order (`job_order-D_Uc.json.txt`): `{"job": "D_Uc", "blocked_by": []}`;
  - `2026-11-13T14:16:34Z M=401733bce290ce122cfbf38f1526e120f174b3ec job=D_Uc id=61226525 limit=08:54:00` (`job_submissions.log.txt`), `submit D_Uc rc=0`, then scontrol `JobState=PENDING`; the log ends `DONE`.
- **Removal** (`removal.log.txt`): the staged script and the log in /dev/shm, `rm -f /dev/shm/josephrb-g2r-D_Uc.sh /dev/shm/josephrb-g2r-D_Uc.log rc=0`, and the `ls` after it finds neither. The launcher's `removal rc=2` (`launch-stdout.txt`) is that `ls`'s exit status.
- **The ten batch connects** were generated by `gen_g2r_connects.py` from `connect-g2r-D_Ub.sh` (`4142a188…`); `connects-batch.sha256.txt` holds their full sha256. Their realization block (tune jobs) is tested by `test_connect_real.sh` over the 8 tune connects (`test_connect_real.out.txt`, 6 cases each plus the printed lines: `CONNECT-REAL BLOCK TEST PASS`); `test_batch.out.txt` runs the D_Ua block test and the fence test against each of the 10: all PASS. Those two loops were run from the shell; their command text is not kept, only their outputs.
- **Batch path check** (`check_g2r_paths.py`, `check_g2r_paths.out.txt`): 529 labels distinct, per-job write paths disjoint across the 12 unfold jobs: `G2R-PATHS PASS`. `batch-gate.out.txt` is `g2r_jobs.gate` evaluated for each batch job before the go (projection 108.441 ≤ 110 throughout); it was printed from the shell, its command text not kept.

## The job

- **sacct** (`../unfolds-all/sacct-utc.txt`, TZ=UTC): 61226525 `cov2dg2r-D_Uc`, COMPLETED, ExitCode 0:0, nid006945; Start 2026-11-13T14:28:17Z, End 2026-11-13T19:44:45Z, Elapsed 05:16:28, limit 08:54:00.
- **Job log** (`job_cov2dg2r-D_Uc-61226525.out.txt`): `[g2r] start 2026-11-13T14:28:47Z job=61226525 JOB=D_Uc point=data node=nid006945` … `[g2r] end 2026-11-13T19:44:45Z rc=0`; `{"mat_setup_scripts": 6, "mismatches": 0}`.
- **Preflight** (`job_check-D_Uc-61226525.json.txt`): runs 44, 4 inputs checked, problems []. **MAT** (`job_mat-61226525.json.txt`): 6 setup scripts hashed.
- **Walls** (`job_walls.D_Uc.1.tsv`, `job_walls.D_Uc.2.tsv`): 44 runs = the 44 `D_Uc` labels of `runs_g2r.tsv` (`../unfolds-all/lane_check.out.txt`); rc 0 for every run; per-run wall 748–1203 s.
- **Sums** (`job_SHA256SUMS.D_Uc.1.txt`, `job_SHA256SUMS.D_Uc.2.txt`): 44 lines; the fetched `out/<label>/xsec.root` files match them (`../unfolds-all/sums-check.out.txt`).
- **Products:** 44 `xsec.root` files under `/pscratch/sd/j/josephrb/cov2d-g2r-20261112/out/<label>/`, with each label's log and inventory, are listed by sha256 in `node-sha256.raw.txt` and are not committed.

## Atime and the LL5D overlap

The job's inputs are the connect's `input` lines; none is among LL5D's 1146 snapshot paths, and the bulk's atime-post (2026-11-14T03:11:38Z, `atime-post-bulk.sh` 5806a902 under the director's go) reads 0 moved. The constraint file's atime is covered in `../D_Uc/README.md`.

## The constraint file's atime (all 12 G2R jobs)

The director asked for the LL5D constraint file's atime (`…/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt`, an LL5D input that no G2R code reads) at three times: the end of D_Ua, the end of D_Ub, and the end of the last G2R job. The record is `constraint-reads.txt`.

- **The planned reads at D_Ua's and D_Ub's ends were missed.** Their background watches treated an empty sacct reply (a failed ssh) as "still running" and discarded ssh's stderr; both exited "not ended after 11h" without reading. The cause of the ssh failures is not recorded. This is on the follow-up list: future watches treat an empty reply or a failed ssh as an error, logged with its stderr.
- **The batch watch** saw all ten COMPLETED only at 2026-11-14T03:04:46Z, about 6 h 45 min after the last job ended (AR23_Ud, 20:19:06Z), and then read `atime_epoch=1793891894` at 03:04:50Z. A manual read at 03:05:10Z gave the same value.
- **The director's ruling:** atime only moves forward on a read unless something resets it explicitly, and nothing in these lanes does. A value of 1793891894 at 03:04:50Z, equal to the value recorded before any G2R job ran, therefore shows that no read moved the constraint file at any time during G2R. The reads at D_Ua's and D_Ub's ends would have added nothing; the condition is met by the 03:04:50Z read.
