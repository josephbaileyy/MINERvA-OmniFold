# COV2D-G2R D_Ua (job 61225732): COMPLETED 0:0; 44 runs, every rc 0 (2026-11-13)

**By** the `cov2d` session, under COV2D-G2R addendum J1 (code at M = `401733bce290ce122cfbf38f1526e120f174b3ec`).

- **Connect:** `connect-g2r-D_Ua.sh`, `46005adee216d712bede1c8fdd4ed376423b8c6e08ff2f1cda57dfb276e573f1`. `D_Ua-vs-prepare-233f8cd2.diff.txt` is its diff from the parent connect.
- **Launcher:** `launch-g2r.sh` `60a1860335511feb…` (its rebuild chain is in `../D_Ua/`, `../D_Ub/` and `../D_Uc/`).
- **Go:** the director, "go 46005ade 60a18603": re-hash both, run the fence, launch once; a non-PASS goes back unrepaired; report the first `--miss-map` runs before D_Ub.
- **Launcher chain:** `launch-g2r.sh` here is `60a18603…`, the copy that ran. `launch-g2r-D_Ua-vs-60b624c6.diff.txt` applied to `../envtest/launch-g2r.sh` (`60b624c6…`) rebuilds it byte-exact; `test_launch_g2r.60a18603.out.txt` is `../envtest/test_launch_g2r.sh` (unchanged, `5e3faf85…`) run against it: `LAUNCH-G2R TEST PASS`.
- Full digests: `node-sha256.raw.txt` (this job's node files, read O_NOATIME) and `files.sha256` (every file here).

**CANNOT AUTHORIZE:** the G2R readout or any other job. Each needs its own go.

## The connect

- **Fence** (`fence.sh`, `fence.txt`), 2026-11-13T13:22:22Z: 6 jobs listed (61214607 ll5d_bulk_05 RUNNING; 61214609 ll5d_bulk_06 RUNNING; 61214614 ll5d_bulk_09 RUNNING; 61214615 ll5d_bulk_10 RUNNING; 61214610 ll5d_bulk_07 RUNNING; 61214612 ll5d_bulk_08 RUNNING), and no unended cov2d job outside `cov2dg2r-`. `launch-stdout.txt` reads `FENCE_CLEAR`.
- **Staging** (`staged_sha.txt`, `launch-stdout.txt`): node = local = go = `46005ade…`, `DIGEST_MATCH`, launched rc=0 at 2026-11-13T13:22:40Z (`launch.txt`).
- **Connect log** (`connect.log.txt`, `ba023990213a98ce1268b34283fcbb5f5c64e1f4ae61c0e34c6283cb7e5e364b`), 2026-11-13T13:22:38Z to 2026-11-13T13:23:04Z, host login02:
  - `balance_node_h=1335.9 half=668.0 cap=110.0`;
  - `recompute spent=1.241 held=0.000 this=8.9 total=10.141 cap=110.0`;
  - `deploy porcelain=0 ignored=0 head=401733bce290ce122cfbf38f1526e120f174b3ec`;
  - `origin/main=c29c2dfa21d58f3f7af762e051505cc549dc65b3`;
  - `envtest record on origin/main: verdict=PASS sha256=c4a0720d3a12265403d22e273e219d4594b03ba0a592afe671618ed72cbf0272`;
  - `prepare record on origin/main: verdict=PASS map_npz_sha256=956531e3b761aaf08d40c6ab8d917ba5f19dab5947b72607e6a34d0d3f7f83ae sha256=d72facde6b73e854620bce58780928307fcb1fa9b3e921e94f03cbe6ec9ac1dc`;
  - `map /pscratch/sd/j/josephrb/cov2d-g2r-20261112/prepare/g2r_map.npz sha256=956531e3b761aaf08d40c6ab8d917ba5f19dab5947b72607e6a34d0d3f7f83ae (O_NOATIME)`;
  - 19 bound blobs `OK` (`job_bound-D_Ua.sha256.txt` is the node's list);
  - `input /pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/runEventLoopOmniFold_MEFHC_universes_full.root size=171117087867 atime=2026-11-13T10:39:23Z` (stat, no open);
  - `input /pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root size=5143 atime=2026-11-13T10:36:28Z` (stat, no open);
  - `input /pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/baseline_flux/flux_integral_universes_MEFHC.root size=6396 atime=2026-11-06T16:31:27Z` (stat, no open);
  - `input /pscratch/sd/j/josephrb/cov2d-g2r-20261112/prepare/g2r_map.npz size=143986060 atime=2026-11-13T12:39:35Z` (stat, no open);
  - `ll5d constraint /pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt atime_epoch=1793891894 (stat only; not a D_Ua input)`;
  - the gate (`job_gate-*.psv.txt`, its `.gate.json.txt`): pass true, total 10.141, cap 110.0; the order (`job_order-D_Ua.json.txt`): `{"job": "D_Ua", "blocked_by": []}`;
  - `2026-11-13T13:22:52Z M=401733bce290ce122cfbf38f1526e120f174b3ec job=D_Ua id=61225732 limit=08:54:00` (`job_submissions.log.txt`), `submit D_Ua rc=0`, then scontrol `JobState=PENDING`; the log ends `DONE`.
- **Removal** (`removal.log.txt`): the staged script and the log in /dev/shm, `rm -f /dev/shm/josephrb-g2r-D_Ua.sh /dev/shm/josephrb-g2r-D_Ua.log rc=0`, and the `ls` after it finds neither. The launcher's `removal rc=2` (`launch-stdout.txt`) is that `ls`'s exit status.
- **Held note (the director):** the header of `connect-g2r-D_Ua.sh`, line 10, still says "this job's 2.0". The operative value is `this=8.9` in the recompute line above. The script was not edited after the go.
- **The connect's realization-free block test** (`test_connect_dua.sh`, `test_connect_dua.out.txt`): `CONNECT-DUA BLOCK TEST PASS`.

## The job

- **sacct** (`../unfolds-all/sacct-utc.txt`, TZ=UTC): 61225732 `cov2dg2r-D_Ua`, COMPLETED, ExitCode 0:0, nid004524; Start 2026-11-13T13:40:05Z, End 2026-11-13T18:41:50Z, Elapsed 05:01:45, limit 08:54:00.
- **Job log** (`job_cov2dg2r-D_Ua-61225732.out.txt`): `[g2r] start 2026-11-13T13:40:38Z job=61225732 JOB=D_Ua point=data node=nid004524` … `[g2r] end 2026-11-13T18:41:49Z rc=0`; `{"mat_setup_scripts": 6, "mismatches": 0}`.
- **Preflight** (`job_check-D_Ua-61225732.json.txt`): runs 44, 4 inputs checked, problems []. **MAT** (`job_mat-61225732.json.txt`): 6 setup scripts hashed.
- **Walls** (`job_walls.D_Ua.1.tsv`, `job_walls.D_Ua.2.tsv`): 44 runs = the 44 `D_Ua` labels of `runs_g2r.tsv` (`../unfolds-all/lane_check.out.txt`); rc 0 for every run; per-run wall 719–1216 s.
- **Sums** (`job_SHA256SUMS.D_Ua.1.txt`, `job_SHA256SUMS.D_Ua.2.txt`): 44 lines; the fetched `out/<label>/xsec.root` files match them (`../unfolds-all/sums-check.out.txt`).
- **Products:** 44 `xsec.root` files under `/pscratch/sd/j/josephrb/cov2d-g2r-20261112/out/<label>/`, with each label's log and inventory, are listed by sha256 in `node-sha256.raw.txt` and are not committed.
- **First `--miss-map` runs** (`first-runs_node-sha256.raw.txt`, read O_NOATIME on login11 at 13:55:25Z while the job ran): `A_2p2h_0` and `A_AGKYxF1pi_1` rc 0, with their `xsec.root` sha256 `021a56ef…` and `c8cba4cf…`. The director accepted them before D_Ub's go. The final `node-sha256.raw.txt` lists the same two products with the same sha256.
- **Informational comparison, not a gate** (`dua-vs-partb-2p2h0.py`, `dua-vs-partb-2p2h0.out.txt`): `A_2p2h_0` against part B's `U_2p2h_0` (`60a9094e…`). runConfig differs only in `miss_map` and `out`; hXSec2D changed in 205 of 205 cells, max |a/b−1| 1.288e-2, median 1.398e-3. The two paths it prints are local copies of the fetched files and are not committed.

## Atime and the LL5D overlap

The job's inputs are the connect's `input` lines; none is among LL5D's 1146 snapshot paths, and the bulk's atime-post (2026-11-14T03:11:38Z, `atime-post-bulk.sh` 5806a902 under the director's go) reads 0 moved. The constraint file's atime is covered in `../D_Uc/README.md`.
