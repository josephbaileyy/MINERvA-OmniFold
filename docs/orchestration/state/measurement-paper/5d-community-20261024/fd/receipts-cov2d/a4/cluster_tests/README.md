# COV2D addendum A4: the tests in the cluster environments, at the A4 code head (2026-11-07)

**By** the `cov2d` session, for PR #875. This is the cluster receipt that `../README.md` lists as owed: A4's tests in
root_6_28 on Linux, which is the environment the driver runs in (`../../../COV2D-ADDENDUM-A4.md` §3).

**Code head H4 = `7177d0f83120a70373057adc6a64a2c84985e867`.** M = `a60547692df5f963e428cdfe4661fc51ab785b7b`.

- **MEASURES:** whether `test_cov2d_readout` and the bound suites of the modules the driver imports pass at H4, on
  Linux, in root_6_28 with and without the pinned MAT environment, and `test_cov2d_readouts` in omnifold_py310.
- **CANNOT AUTHORIZE:** a bulk read, phase N or phase S; those wait for the director's binding of A4. It is not the code
  audit.

**Result: `TESTS-SUMMARY 10 ok of 10 suite runs`.** No failures or errors. `guarded_reads=0` in every suite.

## The connect

- **The script:** `connect-a4t.sh`, sha256 `69e2e3f02b3a432c792b663c0c5c5282421cc06ac04bd76953230b40cea3a4d4`.
- **Its base:** the approved A2 connect `../../a2/cluster_tests/connect-a2tests-2.sh`. The diff is
  `connect-a2tests-2-to-a4t.diff.txt`.
  - Kept: the suite runner, its audit hook, the porcelain lines and the removal.
  - Dropped: A2's rerun deploy and quota check.
  - Changed: the head is H4; the environments run RM first, then R, then P; the suite lists.
  - Added:
    - a sha256 check of `cov2d_readout.py` against the value in `../README.md`;
    - a `BOUND-UNCHANGED` check, `git diff --quiet M H4`, of the five bound modules;
    - `O_NOATIME` in each `ENV` line;
    - a `GUARD-TEST` line for each of five guard tests in RM and R.
- **The launcher:** `launch-s5.sh` from `../../a2/stage5-control95/`, with an `a4t` case added. The diff is
  `launch-s5-a4t.diff.txt`. Its output is in `launch-a4t.out.txt`.
- **The fence (`fence.txt`):** clear at 2026-11-07T08:27:27Z on login02. squeue was empty, and no cov2d job was unended
  in sacct.
- **Staging (`staged_sha.txt`):** the node digest equalled the local one (DIGEST_MATCH).
- **The run:** launched 08:27:46Z (`launch.txt`) on login02 under nice 19, taskset -c 8-11, threads 1. 0 node-h, no job.
  - It started at 08:27:44Z as a fresh clone at H4 in `/dev/shm`. It does not run on pscratch, because cov2d_blocks'
    open audit guards /pscratch.
  - Before: porcelain 0, `--ignored` 0. `READOUT-SHA OK`. `BOUND-UNCHANGED` for all five of `cov2d.py`,
    `cov2d_blocks.py`, `cov2d_null.py`, `cov2d_score.py` and `cov2d_readouts.py`.
  - The MAT setup check passed: `{"mat_setup_scripts": 6, "mismatches": 0}`, with the PlotUtils MnvH1D dictionary present.
  - After: porcelain 0, `--ignored` 0. It ended at 08:35:57Z.
- **Removal:**
  - The connect removed its clone, tmp and runner, logging rc 0 and the clone's size of 1.2 G.
  - The launcher then hashed and fetched the 13 files and removed the staged script and the whole
    `/dev/shm/josephrb-cov2d-a4t` directory, every removal with rc 0 (`removal.log.txt`).
  - Each fetched file's sha256 equals the node's (13 MATCH, `launch-a4t.out.txt`).
  - `logs/SHA256SUMS` was written on the node, and every log here checks against it.
  - The logs carry a `.txt` suffix because `*.log` is gitignored.

## The environments (`ENV` lines)

| env | python | numpy | ROOT | uproot | `os.O_NOATIME` |
|---|---|---|---|---|---|
| RM: root_6_28 + pinned MAT | 3.11.14 | 1.26.4 | 6.28/12 | absent | 262144 |
| R: root_6_28 by prefix | 3.11.14 | 1.26.4 | 6.28/12 | absent | 262144 |
| P: omnifold_py310 | 3.10.19 | 2.2.6 | absent | 5.6.9 | 262144 |

## Suites

| env | module | ran | failures | errors | skipped | seconds |
|---|---|---:|---:|---:|---:|---:|
| RM | test_cov2d_readout | 36 | 0 | 0 | 0 | 122.3 |
| RM | test_cov2d_blocks | 26 | 0 | 0 | 0 | 17.1 |
| RM | test_cov2d_null | 5 | 0 | 0 | 0 | 13.8 |
| RM | test_cov2d_score | 12 | 0 | 0 | 0 | 27.9 |
| RM | test_cov2d | 35 | 0 | 0 | 11 | 1.6 |
| R | test_cov2d_readout | 36 | 0 | 0 | 0 | 124.1 |
| R | test_cov2d_blocks | 26 | 0 | 0 | 0 | 17.1 |
| R | test_cov2d_null | 5 | 0 | 0 | 0 | 15.4 |
| R | test_cov2d_score | 12 | 0 | 0 | 0 | 26.7 |
| P | test_cov2d_readouts | 12 | 0 | 0 | 0 | 76.6 |

- **The 11 skips in `test_cov2d`** are all "needs PyROOT and uproot", and no environment has both. A2's run at M skipped
  the same 11 in P and in RM (`../../a2/cluster_tests/connect-a2tests.log.txt`).
- **On Linux `os.O_NOATIME` is real.** So `test_cov2d_readout` leaves `Run.watch` live (`test_cov2d_readout.py:289-290`
  stubs it only where O_NOATIME is absent). The end-to-end phase N and phase S tests therefore passed the real atime
  guard here, which the Mac run in `../README.md` could not test.
- **The guard tests ran, ok, not skipped, in both RM and R (`GUARD-TEST RAN-OK`):**
  - `test_null_passes_at_both_truths_and_opens_no_toy`
  - `test_score_completes_after_the_gate`
  - `test_a_plain_toy_open_in_phase_n_is_refused_by_the_audit`
  - `test_a_noatime_toy_read_in_phase_n_stops`
  - `test_atime_moved_stops_and_unmoved_does_not`

## Files

- `connect-a4t.sh`, `connect-a2tests-2-to-a4t.diff.txt`, `launch-s5-a4t.diff.txt`, `launch-a4t.out.txt`;
- `fence.txt`, `staged_sha.txt`, `launch.txt`, `removal.log.txt`;
- `connect-a4t.log.txt`;
- `logs/`: one `<env>_<module>.log.txt` per suite run, `blobs.txt` (`git ls-tree` of `2d-unfolding/cov2d` at H4), and
  `SHA256SUMS`.
