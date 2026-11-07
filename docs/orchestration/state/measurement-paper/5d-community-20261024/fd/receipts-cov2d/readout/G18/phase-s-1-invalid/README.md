# COV2D addendum A4, phase S for G18, attempt 1: INVALID, crashed in the bound grade (2026-11-07)

**By** the `cov2d` session. This ran under COV2D-BINDING-2 addendum A4, with the director's go for `connect-s-G18.sh` at
the sha256 below. It went to the director unrepaired, with the mechanism named. Nothing has been rerun.

**M = `ac25b66533788ceb18b1d4e5add259c53b216669`.** `--null-digest` was
`ecdb4be2fbb18852d32c1a4f9fb3cbc4107310d72c5bdeb2eb3651996ed0c41f` (`../null_G18.json`, on main by #886).

- **MEASURES:** that phase S for G18 crashed, where, and why the bound check refused.
- **CANNOT AUTHORIZE:** any reading for G18, a rerun, or a change to the grade or its check. Those are the director's.
  - **There is no score record.** The driver wrote nothing to `out/` (`out_list.txt` is empty), printed no verdict
    line, and produced no reading.

**Result: `PHASE-S G18 INVALID (connect: rc=1, no matching verdict line)`.** The driver exited with status 1 after
8.95 s.

## What happened

1. **The fence** (`fence.txt`) was clear under the director's ruling (`../../AR23/README.md`) at 18:11:45Z on login02.
   It allowed `60970044 rs1_dry RUNNING` and found no unended cov2d job in sacct.
2. **Staging:** DIGEST_MATCH (`staged_sha.txt`). Launched at 18:12:14Z (`launch.txt`).
3. **The deploy:** a fresh clone at M in `/dev/shm`, porcelain 0, `READOUT-SHA OK`, `origin/main=7db5cb80…`. Then
   `NULL-ON-MAIN OK ecdb4be2…`: `git show origin/main:<null_G18.json>` hashed to the null digest.
4. **The driver's §9.7 gate passed** and phase S read the toys.
5. **The crash** came in `cov2d_score.score` (`cov2d_score.py:81`) → `fd_1b_mc.grade`, which raised
   `fd_1b_mc.Refusal: the non-null chi2 and the Cholesky chi2 differ` (`fd_1b_mc.py:667`; traceback in
   `score_G18.log.txt`).
   - `cov2d_readout.phase_score` catches exceptions only around the gate, so the Refusal went uncaught. The process
     exited with status 1 and wrote no `score_G18.json`.
   - `Run.finish` never ran, so this run's atime and open-audit results were never recorded.
6. **After the run:** porcelain 0, HEAD = M, blobs unchanged. The connect removed the clone and `tmp` (which held the
   toy copies), rc 0.
   - The launcher hashed and fetched the four files (4 MATCH), then removed the staged script and the directory, every
     removal with rc 0 (`removal.log.txt`).
   - `score_G18.log.txt` holds the preflight lines and the traceback, and no reading.

## The mechanism (from the bound code; no toy was used to find it)

- **The check.** `fd_1b_mc.grade` (`fd_1b_mc.py:662-667`) computes `chi2, ndf = fn.chi2_nonnull(E, C)` on the
  eigenvalues above `fd_1b_null.RANK_REL` = 1e-12 of the largest. If `ndf == C.shape[0]`, it also computes each row's
  Cholesky χ² and raises a Refusal if any row's relative difference exceeds 1e-9. COV2D-DECLARATION.md:253 states this
  check: "with the Cholesky equality checked if ndf = 205".
- **Why it ran at G18.** G18's C_T (`../blocks_G18.npz`) has a min/max eigenvalue of 1.0531e-12, just over the cut.
  So ndf = 205 (`../null_G18.json` §9.8) and the check runs, on a matrix with condition number 9.50e11.
- **Why it cannot pass there.** At that conditioning the two float64 computations differ by more than 1e-9 relative,
  whatever the errors are.
  - `cholesky_check_diagnostic.py` reads only the two committed blocks files and uses synthetic errors. Its output is
    `cholesky_check_diagnostic.out.txt`, run on the Mac with numpy 2.4.4.
  - G18, 300 rows of E ~ N(0, C_T): max |χ²/ref − 1| = 4.32e-8.
  - G18, 300 rows of independent N(0, σ_c): 3.73e-8.
  - Both are over 1e-9.
- **AR23 is not affected.** Its C_T has a min/max eigenvalue of 9.99e-13, so ndf = 204 and grade skips the check.
- **Why the tests did not catch it.** `test_cov2d_readout`'s synthetic C_T is well conditioned. Phase N's §9.8 had
  recorded G18's 1.05e-12, and the `cov2d` session did not connect it to grade's ndf = 205 branch before launch.

## For the director (open)

1. **How G18 is to be graded,** given that the bound check cannot pass at this C_T. This is a ruling on bound code or a
   declared rule.
2. **Whether the driver should catch a grade Refusal and write an INVALID score record,** rather than exit with none.
3. **Whether AR23's phase S runs before (1).**

## Files

- `connect-s-G18.sh` (sha256 `207c797c67b45386fffe4ad21cfe69d1084ad40e1ae51ef504a1156549b7aac2`), and
  `connect-n-G18-to-s-G18.diff.txt`, its diff from the phase N connect;
- `launch-s5-s.diff.txt` (the launcher's sG18/sAR23 cases; launcher sha256 `2c9a5de8…`), `launch-sG18.out.txt`;
- `fence.txt`, `staged_sha.txt`, `launch.txt`, `out_list.txt` (empty), `removal.log.txt`;
- `connect-s-G18.log.txt`, `score_G18.log.txt`, `blobs.before.txt`, `blobs.after.txt`;
- `cholesky_check_diagnostic.py`, `cholesky_check_diagnostic.out.txt`.
