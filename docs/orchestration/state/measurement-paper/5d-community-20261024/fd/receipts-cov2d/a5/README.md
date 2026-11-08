# COV2D-BINDING-2 addendum A5: the code, its tests and mutants, run locally (2026-11-07)

**By** the `cov2d` session. This implements COV2D-BINDING-2 addendum A5 (#889), the Cholesky cross-check's tolerance
at full rank, and the director's extension of 2026-11-07 to the leave-out-MEC grade. It is the local test and mutation
receipt. The cluster receipts are `cluster_tests/` (at the A5 code head `b25918fb`) and `cluster_tests-2/` (at the
head with the A5-C1 tests), each a separate commit.

- **MEASURES:** whether the A5 change does what A5 rules, whether its tests kill the declared mutants, and whether 1B's
  default is unchanged.
- **CANNOT AUTHORIZE:** G18's phase S rerun. That waits for coverage-5b-audit's audit and A5's M line. It is not a code
  audit.

## The rule, as implemented

1. **1B's grade** (`nd-unfolding/fd_1b_mc.py`, `grade`) takes `chol_tol: float = 1e-9` and `chol_out: dict | None`.
   - At full rank it compares the non-null χ² with the Cholesky χ² to the relative `chol_tol`.
   - The default and the refusal's message (`"the non-null chi2 and the Cholesky chi2 differ"`) are 1B's, unchanged.
   - The compared values (`ndf`, `max_rel_diff`, `tol`) go to `chol_out` when given, and onto a refusal as
     `.compared`. Below full rank, `chol_out` gets `max_rel_diff: None`.
2. **The passthroughs.** `cov2d_score.score` and `cov2d_readouts.leave_out_mec` pass both arguments to 1B's grade. Their
   defaults are 1B's.
3. **The driver** (`cov2d_readout.phase_score`):
   - Right after the §9.7 gate, before any toy is read, it records `cholesky_check` = `cholesky_tol(C_T)` and
     `cholesky_check_minus` = `cholesky_tol(C_T⁻)`.
   - Each is `{"rule": "max(1e-9, 10 kappa_2(C_T) eps)", "kappa2": λ_max/λ_min, "eps": float64 eps, "tol": ...}`, from
     `eigvalsh` of that matrix alone (A5 ruling 1, and the director's ruling (i)).
   - It passes `tol` to the C_T grade and `tol⁻` to the leave-out-MEC grade of C_T⁻, and records each grade's compared
     values.
4. **A refusal from either grade** (A5 ruling 2, and the director's ruling (ii)):
   - writes `score_<T>.invalid.json` through `Run.finish` (atime and open audit included), with
     `grade_refusal: {"grade": "C_T"|"C_T_minus", "text", "compared"}`, the compared values under that grade's
     `cholesky_check*`, and `controls_failed` naming the grade;
   - sets `verdict` INVALID;
   - prints `COV2D-SCORE <T> INVALID (grade refused, <grade>: <text>)`;
   - exits with status 3.

**Why a keyword on 1B's grade, not a wrapper** (accepted by the director). A wrapper in `cov2d_readout.py` cannot change
the tolerance without either copying grade's statistics into cov2d, so that "exactly as 1B grades"
(COV2D-AMENDMENT-1:27) would rest on a copy, or monkeypatching a bound module.

**The cost: a bound blob changes.** `fd_1b_mc.py` goes from blob `74aa8dac` (sha256 `1a2f825f…`) to blob `66662196`
(sha256 `936e1957…`).
- `74aa8dac` is pinned by COV2D-AMENDMENT-1:27, COV2D-BINDING-2:17 and FD-1B-STAGED-BINDING-2:20,28. 1B's stage-1
  connect (`connect32-s1-0.sh`) and `mutation_mc.out` pin its sha256.
- `nd-unfolding/tests/test_fd_1b_mc.py` also changes. 1B's `mutation_mc.out` pins its sha256 `e786b4d9…`.
- Those records pin the files at their own M and stay true there. A rerun of a 1B stage would run at 1B's M, not at
  main.
- A5's M binds the new blobs. With the default `chol_tol`, 1B's behaviour is unchanged. The cluster receipt checks this:
  the failing tests at A5's head equal those at the readout's M, in each environment.

## The files exercised (sha256)

| file | sha256 |
|---|---|
| `nd-unfolding/fd_1b_mc.py` | `936e1957d330e24d3eaab5f6c53d30b5be42a96f76daac07d527be97c0af30e2` |
| `2d-unfolding/cov2d/cov2d_score.py` | `6616e14ef32699ac38297382372cb697185212449963b96aed4f40be0b21fe8c` |
| `2d-unfolding/cov2d/cov2d_readouts.py` | `a288592ff0a726d6a726809f18c50fbadbfdbc1c9e1f10d22e560122f712474b` |
| `2d-unfolding/cov2d/cov2d_readout.py` | `0c3ad137be128691cce7bbe3ec72493b76791e761e6cd897f75aaf0a4fc7444f` |
| `2d-unfolding/cov2d/tests/test_cov2d_readout.py` | `b9e04c6fc31608d29700e499f8506a818db53513e7eded4c0c13ca700fa65ff3` |
| `2d-unfolding/cov2d/tests/test_cov2d_readouts.py` | `e78b722438e2b6d49137b2b5792b7a4863d91ff48348e162402c76578de09a19` |
| `nd-unfolding/tests/test_fd_1b_mc.py` | `22b0fddf1e5926620d9329900b4878a9bc7711e79176f4039fdc282f29ebff8f` |
| `mutation_a5.py` | `2d7310c2c110b8e23e4ae59e7c243f36860cf91e4c0214fa12e14ba1964ea6d0` |

**Interpreter:** Python 3.13.7, ROOT 6.36, numpy 2.4.4, on Joseph's Mac.

## The tests

- **`test_fd_1b_mc.CholeskyTolerance`** (6 tests) uses a 16×16 full-rank C with κ ≈ 6.7e11. On it:
  - 1B's default is 1e-9 and refuses there, with its message unchanged;
  - A5's tolerance passes, and the compared values sit between 1e-9 and tol;
  - a wrong Cholesky, scaled by 1.01 or transposed, refuses at A5's tolerance;
  - below full rank the check is skipped and reported so;
  - a well-conditioned grade is unchanged by the argument.
- **`test_cov2d_readout.CholeskyTolPure`** (2 tests): the formula, and the 1e-9 floor.
- **`test_cov2d_readout.CholeskyA5`** (6 tests):
  - each tolerance is computed from its own matrix before any toy is opened, passed to its own grade, and recorded;
  - κ ≈ 1e12 in both C_T and C_T⁻ (205×205, full rank, the null record re-pinned to the new blocks): both grades pass
    under A5, with compared values above 1e-9;
  - a refusal of the C_T grade, and a refusal of the C_T⁻ grade, each write the invalid record naming the grade, finish
    Run, uninstall the open audit, and print the distinct line;
  - **the catch's other direction** (coverage-5b-audit's A5-C1): a COV2D `Refusal` raised inside the scoring `try`
    stays a plain refusal (status 2, `score_G18.refused.json` with its own text, no invalid record, no score
    record), and any other exception raised there propagates with nothing written. Mutants V11 and V12 below.
- **`test_cov2d_readouts.LeaveOutMEC`:** one existing mock of 1B's grade now accepts the new keywords (`**kw`).
- **Results** (`tests.seed{0,1,12345}.txt`, rerun with the A5-C1 tests): at PYTHONHASHSEED 0, 1 and 12345,
  `test_cov2d_readout`, `test_cov2d_score` and `test_cov2d_readouts.LeaveOutMEC` ran 60 OK, and `test_fd_1b_mc.CholeskyTolerance` and `Grading` ran 12 OK.
- **Run whole on the Mac:**
  - `test_cov2d_readout` 44 OK and `test_cov2d_score` 12 OK.
  - `test_cov2d_readouts` has 1 error and `test_fd_1b_mc` 7. They are the same tests that error on unmodified main on
    the Mac: absent uproot, and numpy 2's scalar repr.
  - The cluster receipt runs them whole in root_6_28 and omnifold_py310.

## The mutants (`mutation_a5.run2.txt`)

**`BASELINE ok`, then killed 24 of 24, harness rc 0.**
- All 17 REQUIRED mutants are among them, including the director's "leave_out_mec drops the C_T- passthrough" and
  coverage-5b-audit's A5-C1 pair: "catch widened to Exception (auditor V11)" and "catch widened to cov2d's Refusal too
  (auditor V12)". Both survived the tests of run 1.
- `mutation_a5.run1.txt` is run 1 (22 of 22, before V11 and V12), kept as run.
- Every mutant's text matched exactly once.
- Each mutant runs the test sets named in `mutation_a5.py`: the classes the change touches. That way an environment-only
  error elsewhere in a module cannot count as a kill. The unmutated tree must pass them first.

## Files

- `mutation_a5.py`, `mutation_a5.run1.txt`, `mutation_a5.run2.txt`;
- `tests.seed0.txt`, `tests.seed1.txt`, `tests.seed12345.txt`.
