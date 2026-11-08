# COV2D addendum A5: the tests in the cluster environments, at the A5-C1 head (2026-11-07)

**By** the `cov2d` session, for PR #900. This is the second cluster receipt `../README.md` names. It reruns
`../cluster_tests/` at the head that adds coverage-5b-audit's A5-C1 tests: run 1 ran at `b25918fb`, the commit before
those two tests were added. `../cluster_tests/` stays as run 1's record.

**H5 = `49e4202269ff3d3a6250b824f39c9347680f6b6e`.** The comparison base is the readout's
**M = `ac25b66533788ceb18b1d4e5add259c53b216669`**.
- No code file differs from run 1's head `b25918fb`. Between the two heads, `git diff --stat b25918fb 49e42022 -- '*.py' ':!*/tests/*' ':!docs/*'` is empty.
- The changed `.py` files are `test_cov2d_readout.py` (+22) and `mutation_a5.py`.

- **MEASURES:**
  - whether A5's tests pass, now including the two A5-C1 tests, on Linux in root_6_28 (with and without MAT) and in
    omnifold_py310;
  - whether the bound suites still pass at H5;
  - whether `test_fd_1b_mc` and `test_cov2d_readouts` fail in the same tests at H5 as at M, in each environment.
- **CANNOT AUTHORIZE:** G18's phase S rerun. That waits for coverage-5b-audit's audit and A5's M line. It is not the
  code audit.
- **Authorized by:** the director's go of 2026-11-07 for `connect-a5t.sh` sha256 `59db1180…` through `launch-s5.sh a5t`,
  on a login node at 0 node-h.

## Result

- **Every A5 test ran and passed in every environment it was run in.**
  - 28 `A5-TEST RAN-OK` lines (8 + 8 + 6 + 6) and none NOT-OK.
  - In RM and R: the 8 `test_cov2d_readout` A5 tests. These are the 6 of `CholeskyA5`, including
    `test_a_cov2d_refusal_inside_the_try_stays_a_refusal_not_a_grade_refusal` and
    `test_any_other_failure_inside_the_try_propagates_unrecorded`, and the 2 of `CholeskyTolPure`.
  - In R and P: the 6 `test_fd_1b_mc.CholeskyTolerance` tests.
- **Run 1's NOT-OK artifact is gone.** The ok-check now reads the first ` ... <status>` line at or after the test's own
  line, so a test with a docstring is read correctly.
  - `test_kappa_1e12_in_both_C_T_and_C_T_minus_grades_under_a5`, which printed NOT-OK in run 1 although it passed, now
    reads RAN-OK in RM and R.
  - Before the run, the check was tested against run 1's logs: the docstring test read as ok, and an absent test name as
    not ok. It was also tested on a fixture where a docstring test is marked FAIL, which read as not ok.
- **Before and after:** `SAME-FAILURES` in all four comparisons. The failing tests at H5 are exactly those at M, as in
  run 1:

  | env | module | failing at H5 = at M |
  |---|---|---|
  | R (root_6_28) | `test_fd_1b_mc` | none: 67 ran at H5, 61 at M |
  | R | `test_cov2d_readouts` | `CrossTermsCLI…first_order_histogram` (`uproot` absent in root_6_28) |
  | P (omnifold_py310) | `test_fd_1b_mc` | the same 7 numpy-2 scalar-repr errors (61 ran at H5, 55 at M) |
  | P | `test_cov2d_readouts` | none: 12 OK at both |

- **`TESTS-SUMMARY 11 ok of 16 suite runs`.** The five that are not ok are the same five as run 1:
  - `test_cov2d_readouts` in RM, R and R-M, with the `uproot` error;
  - `test_fd_1b_mc` in P and P-M, with the 7 numpy-2 errors.
- **The suites at H5:**

  | env | module | ran | failures | errors | skipped |
  |---|---|---:|---:|---:|---:|
  | RM | test_cov2d_readout | 44 | 0 | 0 | 0 |
  | RM | test_cov2d_score | 12 | 0 | 0 | 0 |
  | RM | test_cov2d_readouts | 12 | 0 | 1 (uproot) | 0 |
  | RM | test_cov2d_blocks | 26 | 0 | 0 | 0 |
  | RM | test_cov2d_null | 5 | 0 | 0 | 0 |
  | RM | test_cov2d | 35 | 0 | 0 | 11 (the same 11 as run 1) |
  | R | test_cov2d_readout | 44 | 0 | 0 | 0 |
  | R | test_cov2d_score | 12 | 0 | 0 | 0 |
  | R | test_fd_1b_mc | 67 | 0 | 0 | 0 |
  | R | test_cov2d_readouts | 12 | 0 | 1 (uproot) | 0 |
  | P | test_fd_1b_mc | 61 | 0 | 7 (numpy 2 repr) | 0 |
  | P | test_cov2d_readouts | 12 | 0 | 0 | 0 |

  - `test_cov2d_readout` ran 44 tests, run 1's 42 plus the two A5-C1 tests.
  - `guarded_reads=0` in every suite run.
  - `cov2d.py`, `cov2d_blocks.py` and `cov2d_null.py` are UNCHANGED from M.

## The connect

- **The script:** `connect-a5t.sh`, sha256 `59db1180e631dadae5199bdeb839893a1d8e57ee2465fdc998312f9ea3f8049f`. Its diff
  from run 1's script (`../cluster_tests/connect-a5t.sh`, `6b487cdd…`) is `connect-a5t-1-to-2.diff.txt`. Only three
  things change:
  - H5;
  - the two A5-C1 test names in the A5-TEST list;
  - the ok-check, now the `ranok` awk status read.
- **The fence ruling.** On 2026-11-07 the director extended the fence's allowance from RS1's jobs to RS1's and ENS1's.
  - Allowed: `rs1_*` and `ens1_*` (ENS1-BINDING-2). Neither reads COV2D input; ENS1 reads the 5D bank, the bkg dump and
    FD-STAB's references.
  - Still refused: any `cov2d-*` job and any name not recognised.
  - The earlier ruling named `rs1_dry` and `rs1_full` exactly. The director's update writes `rs1_*`, and the launcher now
    reads both as name prefixes. The running RS1 job `rs1_a1` needs that reading.
- **The launcher:** `launch-s5.sh` goes from `ed3e8c6c…` (run 1's, named in the go) to
  `314fa64d950770dd527fae1f01f1cf9efe6e6394b25f7d7ca00bd9f0ba74f26f`.
  - The diff, `launch-s5-ens1.diff.txt`, touches only the fence's comment and its two awk filters.
  - The new filters were tested on 11 synthetic fence outputs in `fence-ens1-test.txt`:
    - allowed: an empty queue; `rs1_a1` + `ens1_dry1`; `rs1_dry` + `rs1_full`; `ens1_full`;
    - refused: `cov2d-g18`; `ens1_dry1` + `cov2d-x`; `ens1x`; `rs1`; `xens1_a`; `interactive`; and an unended `cov2d-x`
      in sacct.
- **The fence (`fence.txt`):** clear at 2026-11-08T01:15:18Z on login02. squeue held `60982139 rs1_a1 RUNNING` and
  `60983221 ens1_dry1 RUNNING`, both allowed under the ruling (`FENCE_ALLOWED_RS1`, `FENCE_ALLOWED_ENS1` in
  `launch-a5t.out.txt`). There was no unended `cov2d-*` job in sacct.
- **Staging:** DIGEST_MATCH (`staged_sha.txt`). Launched at 01:15:38Z (`launch.txt`).
- **The run:**
  - a fresh clone at H5 in `/dev/shm`, with `head=49e42022…` and a worktree at M (`worktree-m=ac25b665…`);
  - porcelain 0 before and after;
  - nice 19, taskset -c 8-11, threads 1;
  - the MAT pin passed (`{"mat_setup_scripts": 6, "mismatches": 0}`);
  - start 01:15:36Z, end 01:28:48Z.
- **Removal:**
  - The connect removed `deploy-m`, `deploy` (1.3 G), `tmp` and the runner, rc 0.
  - The launcher hashed and fetched 19 files (19 MATCH, `launch-a5t.out.txt`). It then removed the staged script and the
    directory, 22 removals, each rc 0. Its final `/dev/shm` listing was empty (`removal.log.txt`).
  - Every log checks against `logs/SHA256SUMS`: 17 OK. The logs carry `.txt` because `*.log` is gitignored.
- **0 node-h:** a login node, no job.

## Files

- `connect-a5t.sh`, `connect-a5t-1-to-2.diff.txt`, `launch-s5-ens1.diff.txt`, `fence-ens1-test.txt`,
  `launch-a5t.out.txt`;
- `fence.txt`, `staged_sha.txt`, `launch.txt`, `removal.log.txt`, `connect-a5t.log.txt`;
- `logs/`: one `<env>_<module>.log.txt` per suite run (`R-M_` and `P-M_` are the runs at M), `blobs.txt` and
  `SHA256SUMS`.
