# COV2D addendum A5: the tests in the cluster environments, at the A5 code head (2026-11-07)

**By** the `cov2d` session, for PR #900. This is the cluster receipt `../README.md` names.

**H5 = `b25918fbd1fa0207ad65b830c57104d42d66152e`** (A5's code head). The comparison base is the readout's
**M = `ac25b66533788ceb18b1d4e5add259c53b216669`**.

- **MEASURES:**
  - whether A5's tests pass on Linux in root_6_28, with and without MAT, and in omnifold_py310;
  - whether the bound suites still pass at H5;
  - whether the two suites whose code A5 changes outside the driver fail in the same tests at H5 as at M, in each
    environment. Those suites are 1B's `test_fd_1b_mc` and `test_cov2d_readouts`.
- **CANNOT AUTHORIZE:** G18's phase S rerun, which waits for coverage-5b-audit's audit and A5's M line. It is not the
  code audit.

## Result

- **Every A5 test ran and passed in every environment it was run in.**
- **Before and after:** `SAME-FAILURES` in all four comparisons. The failing tests at H5 are exactly those at M:

  | env | module | failing at H5 = at M |
  |---|---|---|
  | R (root_6_28, numpy 1.26.4) | `test_fd_1b_mc` | none: 67 ran at H5, 61 at M, 0 errors at either |
  | R | `test_cov2d_readouts` | `CrossTermsCLI…first_order_histogram` (`uproot` absent in root_6_28) |
  | P (omnifold_py310, numpy 2.2.6) | `test_fd_1b_mc` | the same 7 errors: numpy 2's scalar repr (`could not convert string to float: 'np.float64(…)'`) |
  | P | `test_cov2d_readouts` | none: 12 OK at both |

  1B's `test_fd_1b_mc` runs whole and clean in root_6_28 at H5, so 1B's default is unchanged there.
- **`TESTS-SUMMARY 11 ok of 16 suite runs`.** The five that are not ok:
  - `test_cov2d_readouts` in RM, R and R-M: the `uproot` error above, in every root_6_28 run, at H5 and at M alike;
  - `test_fd_1b_mc` in P and P-M: the same 7 numpy-2 errors at H5 and at M.
- **The suites at H5:**

  | env | module | ran | failures | errors | skipped |
  |---|---|---:|---:|---:|---:|
  | RM | test_cov2d_readout | 42 | 0 | 0 | 0 |
  | RM | test_cov2d_score | 12 | 0 | 0 | 0 |
  | RM | test_cov2d_readouts | 12 | 0 | 1 (uproot) | 0 |
  | RM | test_cov2d_blocks | 26 | 0 | 0 | 0 |
  | RM | test_cov2d_null | 5 | 0 | 0 | 0 |
  | RM | test_cov2d | 35 | 0 | 0 | 11 (needs PyROOT and uproot; the same 11 as in `../../a4/cluster_tests/`) |
  | R | test_cov2d_readout | 42 | 0 | 0 | 0 |
  | R | test_cov2d_score | 12 | 0 | 0 | 0 |
  | R | test_fd_1b_mc | 67 | 0 | 0 | 0 |
  | R | test_cov2d_readouts | 12 | 0 | 1 (uproot) | 0 |
  | P | test_fd_1b_mc | 61 | 0 | 7 (numpy 2 repr) | 0 |
  | P | test_cov2d_readouts | 12 | 0 | 0 | 0 |

  `guarded_reads=0` in every suite run.

- **The A5-TEST lines.**
  - **Ran ok:** all 6 `test_fd_1b_mc.CholeskyTolerance` tests in R and P, and 5 of the 6 `test_cov2d_readout` A5 tests in
    RM and R (`A5-TEST RAN-OK`).
  - **Printed NOT-OK in RM and R, though the test passed:**
    `test_kappa_1e12_in_both_C_T_and_C_T_minus_grades_under_a5`.
    - That test has a docstring, so unittest's verbose output puts its `... ok` on the following line, after the
      docstring's first line, and the check's `^<name> .* ok$` pattern cannot match it.
    - The logs show it passed: `logs/RM_test_cov2d_readout.log.txt:14-15`, `logs/R_test_cov2d_readout.log.txt:5-6`
      (`Both matrices full rank at kappa ~ 1e12 ... ok`).
    - Its suite reports 42 run, 0 failures, 0 errors in both environments.
    - The fault is in the receipt's pattern, not the test. This is recorded here rather than repaired, because this
      connect has run.

## The connect

- **The script:** `connect-a5t.sh`, sha256 `6b487cddc04569d3fc15252a0fd4f81360fb470b12d39f6d2448617e819db8ae`.
  - Its base is `../../a4/cluster_tests/connect-a4t.sh`; the diff is `connect-a4t-to-a5t.diff.txt`.
  - It adds a second worktree at M (`deploy-m`), runs `test_fd_1b_mc` and `test_cov2d_readouts` at H5 and at M in R and
    in P (the logs prefixed `R-M_` and `P-M_`), and compares their `ERROR:`/`FAIL:` sets.
  - It prints the code diffstat M..H5 and checks that `cov2d.py`, `cov2d_blocks.py` and `cov2d_null.py` are unchanged
    (all three UNCHANGED).
- **The launcher:** `launch-s5.sh` (`ed3e8c6c…`) adds the `a5t` case. Its diff from the launcher receipted in
  `../../readout/G18/phase-s-1-invalid/` (`2c9a5de8…`) is `launch-s5-a5t.diff.txt`.
- **The fence (`fence.txt`):** clear at 2026-11-07T19:45:58Z on login02, with squeue empty.
- **Staging:** DIGEST_MATCH (`staged_sha.txt`). Launched at 19:46:16Z (`launch.txt`).
- **The run:** a fresh clone at H5 in `/dev/shm`, HEAD = H5, worktree at M, porcelain 0 before and after. nice 19,
  taskset -c 8-11, threads 1. The MAT pin passed (`{"mat_setup_scripts": 6, "mismatches": 0}`, dictionary true). Ended
  19:58:44Z.
- **Removal:**
  - The connect removed `deploy-m`, `deploy` (1.3 G), `tmp` and the runner, rc 0.
  - The launcher hashed and fetched 19 files (19 MATCH, `launch-a5t.out.txt`), then removed the staged script and the
    directory, each with rc 0 (`removal.log.txt`).
  - `logs/SHA256SUMS` was written on the node, and every log checks against it. The logs carry `.txt` because `*.log` is
    gitignored.
- **0 node-h:** a login node, no job.

## Files

- `connect-a5t.sh`, `connect-a4t-to-a5t.diff.txt`, `launch-s5-a5t.diff.txt`, `launch-a5t.out.txt`;
- `fence.txt`, `staged_sha.txt`, `launch.txt`, `removal.log.txt`, `connect-a5t.log.txt`;
- `logs/`: one `<env>_<module>.log.txt` per suite run (`R-M_` and `P-M_` are the runs at M), `blobs.txt` and
  `SHA256SUMS`.
