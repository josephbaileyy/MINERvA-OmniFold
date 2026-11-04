# COV2D connect E3: the cluster-env test receipt, pinned. **E3 PASS** (2026-11-03)

**By** the `cov2d` session, under `COV2D-BINDING-1.md` (merged at `95e371700ec57546c459ba029a8e8a616d8ccdee`), ruling 4.
**MEASURES:** the five test files in the cluster's environments, at M. **CANNOT AUTHORIZE:** a toy or a block run.

## The run

- **Script:** `connect-e3.sh`, sha256 `0f8976b5ad123b14d74334f75732763da081c98bf0a7bc66e2a32d66357b082c`, sent to the
  director before it ran and approved. The copy on login02 had the same digest.
- **Where:** binding ruling 4 asks for a login node and no job. After E2 (killed, INVALID; `E2-REPORT.md`), the director
  approved a departure: the root_6_28 files run as an sbatch job on one regular CPU node, and the py310 files stay on
  the login node.
- **Login part:** login02, 2026-11-03T23:35:21Z to 23:35:51Z, 0 node-h.
  - It made a fresh clone at M = `c96c97f392f7402791e921ccdac952e74d454cee` in /dev/shm and checked porcelain and the 5
    bound blobs.
  - It ran the py310 preflight and both py310 files, then removed its clone (1.2G, rc 0) and submitted the job.
- **Job:** 60768505, nid006907, -A m3246 -q regular -C cpu -N 1 -t 01:30:00.
  - It ran 23:39:28Z to 23:51:17Z, 11 m 49 s, COMPLETED with exit 0:0. That is about 0.2 node-h, inside the pilot's
    reserve.
  - It made its own fresh clone at M on the compute node's /dev/shm and checked porcelain and the 5 bound blobs. It ran
    the root_6_28 preflight, then the three root files one after another, each under `taskset -c 8-11`
    (`test_re2_driver.py:4`'s own instruction).
- **Writes:** logs went to /pscratch/sd/j/josephrb/cov2d-e3 (92K); nothing was written to CFS.

## What it found

| file | env | rc | Ran | last line | ok | skipped (exactly the expected set) |
|---|---|---|---|---|---|---|
| `test_cov2d` | omnifold_py310 (3.10.19, numpy 2.2.6, uproot 5.6.9) | 0 | 27 | OK (skipped=11) | 16 | 11 Receipt |
| `test_cov2d_writer` | omnifold_py310 | 0 | 10 | OK (skipped=7) | 3 | 7 File |
| `test_re2_data_file` | root_6_28 (3.11.14, numpy 1.26.4, ROOT 6.28/12, lightgbm 4.6.0, sklearn 1.8.0) | 0 | 4 | OK | 4 | none |
| `test_re2_driver` | root_6_28 | 0 | 9 | OK | 9 | none |
| `test_null205` | root_6_28 | 0 | 3 | OK | 3 | none |

- **E2's guards, all kept:** the import preflight STOP, one interpreter per file, a signal exit as FAIL, unittest's
  "Ran N" and last line, rc 0, the ok count, the skipped set by name, and no other status. Fail flags: 0.
- **The pinning, sampled from /proc every 5 s:**
  - `test_re2_data_file`: 15 samples, 3 of a driver child;
  - `test_re2_driver`: 16 samples, 5 of a driver child;
  - every sample showed `Cpus_allowed_list` 8-11, and the driver children peaked at 4 threads;
  - `test_null205` ran no driver and finished in 4.7 s without a sample.
  - The preflight printed `Cpus_allowed_list: 8-11` under taskset.
- **The checkout:** porcelain 0 lines before and after, in both parts. The bound blobs were 5 of 5 at M, in both parts.
- **Not covered here:** the 18 tests that need PyROOT and uproot together skip in omnifold_py310 and run in no cluster
  environment. They ran locally only, under conda-forge ROOT 6.28/12 with uproot 5.6.9.

## A cosmetic defect (the director's ruling: cosmetic)

The sampler's `< /proc/PID/cmdline` redirection printed "No such file or directory" 22 times in
`e3_connect-e3-root.log.txt`, each time for a process that exited mid-scan. The `2>/dev/null` sat on `tr`, not on the
redirection, so the shell's own error reached the log. `|| continue` skipped each such process, so no sample and no
verdict was affected. The next harness that reuses the sampler suppresses the redirection's stderr.

## A harmless environment carry-over

`e3_slurm-60768505.txt` holds two Slurm lines at 23:39:32: "Unable to create TMPDIR [/dev/shm/josephrb-cov2d-e3/tmp]"
and "Setting TMPDIR to /tmp".
- **Why:** sbatch passes the submitting environment by default. The login part had exported TMPDIR (its own /dev/shm
  path) before calling sbatch, and that path did not exist on the compute node at job start.
- **Why it did not matter for the tests:** the job script made its own `$W/tmp` and exported TMPDIR to it after the
  clone and before the preflight and every test. So no test ran with TMPDIR at /tmp. The `git clone` ran with Slurm's
  /tmp, writing into the clone's own directory under `$W`. Whether git put anything in /tmp was not measured.
- **For the next harness:** submit with `--export=NONE`, or unset the variables before calling sbatch.
<!-- absence-ok: one job's runtime facts, not a result: the TMPDIR line is Slurm's own logged error (e3_slurm-60768505.txt), and "not measured" scopes this receipt -->



## Removals

- **Compute node, the job's EXIT trap, 23:51:17Z:** `/dev/shm/josephrb-cov2d-e3` (1.2G), `rm -rf` rc 0, absent after.
- **Login part, 23:35:48Z:** its clone (1.2G), rc 0, absent after.
- **pscratch, 23:51:51Z** (`e3_removal.log.txt`): `/pscratch/sd/j/josephrb/cov2d-e3` (92K), rc 0, after every file was
  fetched and its sha256 matched (`e3_node_listing.txt`).
- **login02's script** `/dev/shm/josephrb-cov2d-e3.sh` (sha256 `0f8976b5…`, checked first): rc 0.
  - `ps -u josephrb` then shows no process of E3.
  - An earlier `grep -c cov2d-e3` count of 2 was the check matching its own command line; the listing is appended to
    the log.
- **A stray copy** (`e3_removal-login23-stray-copy.log.txt`): my first scp landed on login23, because the ssh master had
  re-pinned there. That copy (sha256 `0f8976b5…`) was removed, rc 0, and E3 ran from login02 as told to the director.
- **Two leftovers from Nov 2** (`e3_removal-c1-c2-leftovers.log.txt`, login02, 23:35:16Z):
  - `josephrb_connect_c1.sh` and `josephrb_connect_c2.sh` matched the committed `clip/connect-c1.sh` (`a8df2a8f…`) and
    `clip/connect-c2.sh` (`4dbdc3b2…`), so they were mine. The director said to remove them.
  - Both `rm -f` rc 0.

## Files

The node's files, renamed `.txt` because the repository ignores `*.out`, with their contents unchanged. The sha256 of
each, as listed on pscratch, is in `e3_node_listing.txt`, and the copies here match.

| file | from |
|---|---|
| `connect-e3.sh` | the script as run (both parts) |
| `e3_connect-e3-login.log.txt`, `e3_connect-e3-root.log.txt` | `connect-e3-login.log`, `connect-e3-root.log` |
| `e3_slurm-60768505.txt` | the job's Slurm output, `e3-60768505.out` |
| `e3_ut_<module>.txt` | `ut_<module>.log`, five files |
| `e3_affinity_<module>.txt` | `affinity_<module>.log`, three files |
| `e3_bound.blobs.login.txt`, `e3_bound.blobs.root.txt` | `bound.blobs.login`, `bound.blobs.root` |
| `e3_node_listing.txt` | the pscratch listing and sha256s, before removal |
| `e3_removal*.txt` | the removals' own output |
