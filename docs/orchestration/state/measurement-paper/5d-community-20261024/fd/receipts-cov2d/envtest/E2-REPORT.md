# COV2D connect E2: the cluster-env test receipt, rerun with unittest. **E2 INVALID**: killed (2026-11-03)

**By** the `cov2d` session, under `COV2D-BINDING-1.md` (merged at `95e371700ec57546c459ba029a8e8a616d8ccdee`).
**MEASURES:** the two omnifold_py310 test files on the cluster, descriptively. **CANNOT AUTHORIZE:** anything. No
verdict line was reached, and the three root_6_28 files never completed.

## The run

- **Script:** `connect-e2.sh`, sha256 `5629549239f189993496a62460f24403503e538043855e092c22480e603f86d4`, sent to the
  director before it ran and approved. The copy on the node had the same digest.
- **Where and when:** login02, started 2026-11-03T19:32:30Z (pid 1194687), killed 23:25:01Z. A login node, no job.
- **What it read and wrote:** a fresh clone at M = `c96c97f392f7402791e921ccdac952e74d454cee` (#726's merge) in
  `/dev/shm/josephrb-cov2d-e2`, with TMPDIR and every log under it. No pscratch or CFS path was read or written.
- **What it tests:** the code as bound at `dec97852` (#723), with the tests at M.

## What it found before the kill

- **The checkout:** porcelain 0 lines before, HEAD = M. Bound blobs 5 of 5 at M (`e2_bound.blobs.txt`).
- **The preflight passed in both envs:**
  - omnifold_py310: Python 3.10.19, numpy 2.2.6, uproot 5.6.9, no ROOT, and both test modules import;
  - root_6_28: Python 3.11.14, numpy 1.26.4, ROOT 6.28/12, lightgbm 4.6.0, sklearn 1.8.0, no uproot, and the three
    test modules import.
- **omnifold_py310, descriptive only** (the director's ruling):
  - `test_cov2d`: rc 0, "Ran 27 tests", "OK (skipped=11)", 16 ok, and the 11 skipped tests are exactly the expected
    Receipt tests;
  - `test_cov2d_writer`: rc 0, "Ran 10 tests", "OK (skipped=7)", 3 ok, and the 7 skipped tests are exactly the expected
    File tests;
  - no fail flags (`fail.flags` was empty at the kill).
- **root_6_28:** `test_re2_data_file` was still in its first test, `test_absent_flag_equals_pre_hook`, after 3 h 47 m.
  Its log holds only that test's name line. `test_re2_driver` and `test_null205` never started.

## Why it was killed (the director's instruction)

- **The cause:** LightGBM ran unpinned on a shared login node.
  - `test_re2_driver.py:4` (at M) says LightGBM "sizes its thread pool from the CPU affinity and ignores
    OMP_NUM_THREADS, so run it pinned: taskset -c 8-11 …". The tests set `OMP_NUM_THREADS=1` (:134), but E2 used no
    taskset.
  - The live driver child measured 244 threads (nproc 244), 3151 % CPU and 18.3 CPU-hours in 35 min. The node's load
    average was 150.
- **The projection:** each driver run took about 1 h, against about 22 s locally. The two files make about 28 driver
  runs, so about 30 h in all, against the 12 h cap. It was also loading a shared login node, which NERSC's policy does
  not allow.
- **The fault is my preparation.** The suite documents its own run condition, and I had not read the docstring.
- **A separate error of mine, in watching the run:** my wait loop reported the job finished twice while it was still
  alive. The first time, the ssh ControlMaster re-pinned to login39. The second time, one ssh poll came back empty.
  Neither touched the run.

## The kill and the removals

- **The kill** (`e2_kill.log.txt`), login02, 23:25:01Z:
  - before it, `ps` showed the script (1194687) and its two subshells, the unittest child (1419544) and the driver
    child (541124), all in process group 1194687;
  - `kill -TERM -- -1194687` gave rc 0;
  - 10 s later, `ps -g 1194687` listed nothing;
  - a `pgrep -f` check then matched its own command line and triggered `kill -KILL`, which answered "No such process";
  - the closing `ps -u josephrb` at 23:25:22Z shows only systemd, sd-pam, the check's own sshd and shell. No process of
    E2 remained.
- **The removals** (`e2_removal.log.txt`), login02, 23:26:00Z:
  - `/dev/shm/josephrb-cov2d-e2` (1.2G): `rm -rf` rc 0;
  - `/dev/shm/josephrb-cov2d-e2.sh` (sha256 `5629549…`, checked before removal): `rm -f` rc 0;
  - `ls` then shows neither.
- **Two other files remain** in login02's `/dev/shm`, `josephrb_connect_c1.sh` and `josephrb_connect_c2.sh` (Nov 2).
  They are not E2's, and they are left as found, for the director.

## The next run

E3, approved in principle:
- the three root_6_28 files as an sbatch job on one regular CPU node, CPU only, under 12 h, nothing to CFS;
- each file under `taskset -c` with 4 cores, and each live driver child's affinity mask or thread count recorded;
- the py310 part on the login node as before;
- all of E2's guards kept.

Its sha and the projected node-h go to the director before submission.

## Files

These are the node's files, renamed `.txt` because the repository ignores `*.out`. The contents are unchanged, and
the node's sha256 of each log is in `e2_node_listing.txt`; the copies here match.

| file | from the node's |
|---|---|
| `connect-e2.sh` | the script as run |
| `connect-e2.log.txt` | `connect-e2.log` |
| `e2_ut_test_cov2d.txt`, `e2_ut_test_cov2d_writer.txt` | `ut_test_cov2d.log`, `ut_test_cov2d_writer.log` |
| `e2_ut_test_re2_data_file.txt` | `ut_test_re2_data_file.log`, cut off by the kill |
| `e2_bound.blobs.txt` | `bound.blobs` |
| `e2_node_listing.txt` | the directory listing and sha256s, taken after the kill |
| `e2_kill.log.txt`, `e2_removal.log.txt` | the kill's and the removal's own output |
