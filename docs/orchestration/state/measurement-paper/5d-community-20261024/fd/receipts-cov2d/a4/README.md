# COV2D addendum A4: the driver's tests and mutants, run locally (2026-11-07)

**By** the `cov2d` session, for PR #875. This is the test and mutation receipt for `2d-unfolding/cov2d/cov2d_readout.py`
under `../../COV2D-ADDENDUM-A4.md` §8. The cluster receipt on root_6_28 is `cluster_tests/` (10 of 10 suite runs ok
at the code head `7177d0f83`).

- **MEASURES:** whether `test_cov2d_readout` passes, and whether it kills each declared mutant, on the files hashed below.
- **CANNOT AUTHORIZE:** a bulk read, phase N or phase S. Those wait for the director's binding of A4 (COV2D-BINDING-2
  addendum A4, with its new M). It is not a code audit; coverage-5b-audit holds that.

## The files exercised (sha256)

| file | sha256 |
|---|---|
| `2d-unfolding/cov2d/cov2d_readout.py` | `d1a3cff9768cb3913c9b95c9c6c1bb7402c5a14103f1dd22f5131c16aacda297` |
| `2d-unfolding/cov2d/cov2d_blocks.py` (unchanged from M) | `db14a30057b674e9e367dd442e62f9a159847abb857ee5787ce3b8860a585bca` |
| `2d-unfolding/cov2d/tests/test_cov2d_readout.py` | `6dfddd22558beed7a4eacc59adacdcccf3842e2bcf89a48c29ce4cbcf4f2427c` |
| `mutation_a4.py` | `8e4551e2c3538cb8ae45414310d7ffc4f7d9b524c2580d4ef9d372ceb748783a` |

Neither the test file nor the harness changed after the harness started. After it ended, each mutated source compared
byte-equal to the harness's backup, and `git diff HEAD` on both was empty.

**Interpreter:** Python 3.13.7, ROOT 6.36.000, numpy 2.4.4, on Joseph's Mac. This is not the cluster's environment
(root_6_28: ROOT 6.28/12, numpy 1.26.4); that run is `cluster_tests/README.md`.

## Results

- **Mutants (`mutation_a4.run1.txt`): killed 37 of 37, harness rc 0.** That is 36 on `cov2d_readout.py` plus "open audit
  off" on `cov2d_blocks.py`. All 19 REQUIRED mutants (§8 plus coverage-5b-audit's additions, the `REQUIRED` set in
  `mutation_a4.py`) are among them. Each mutant's text matched exactly once, so there is no NOMATCH.
- **Tests at three hash seeds:** `PYTHONHASHSEED` 0, 1 and 12345 (`test_cov2d_readout.seed*.txt`). Each ran 36 tests
  with result OK.
  - The null-record digest printed by the refusal test differs between runs. This is expected: the record carries
    `utc` and `seconds`. Phase S pins the committed file's digest and never recomputes it.

## Files

- `mutation_a4.py`, `mutation_a4.run1.txt`;
- `test_cov2d_readout.seed0.txt`, `test_cov2d_readout.seed1.txt`, `test_cov2d_readout.seed12345.txt`.
