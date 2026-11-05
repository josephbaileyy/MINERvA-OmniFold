REF-C2C1 code on the cluster, attempt 2: the test run with RooUnfold at #787's final head
0e001f3cc025305653006452e5182ccad4553b8d (the director's ruling of 2026-11-05; attempt 1's RUN FAIL by the old text
parser is ../attempt-1/, #793). Run by limitation-resolver on login04, 2026-11-05T20:03:46Z-20:05:09Z, 0 node-h, with
the connect the director approved (refc2c1_tests_login.sh as copied here, sha256 72f6ea72...; 588fcfa2 is void).
Copied with dd iflag=noatime from /pscratch/sd/j/josephrb/ref-c2c1-20261105/tests-0e001f3c/. Full sha256 of each
file: SHA256SUMS.txt.

OUTCOME: RUN PASS (rc 0). run_tests.sh's own line, printed by run_suite.py check from unittest's result object
(test.log line 910): "RUN PASS: 28 tests, none skipped, failed or errored; Ibu.test_roounfold_bayes_is_the_same_update
ok". unittest: "Ran 28 tests in 26.434s", "OK"; the outcomes record (lines 873-909) lists all 28 as "ok",
was_successful true.
- Environment (test.log lines 1-20): a fresh clone at H, porcelain --ignored 0 before and 0 after; run_tests.sh sha256
  e5919d91527f761967ed68950d335363c90b2724f4d9bbf39abf9e4a9b757977 with EXPECT=28, and the eight files of
  2d-unfolding/ref_c2c1/ by blob, 0 mismatches; libRooUnfold.so sha256
  0b34e1e39102b0dddc5923dad7f69e59c70cd6a2fcbcef07728b72cf2933fefd, rdict .pcm c0c995d7..., .rootmap fa15007e...
  (O_NOATIME copies); root_6_28: python 3.11.14, numpy 1.26.4, ROOT 6.28/12, lightgbm 4.6.0, scikit-learn 1.8.0,
  matplotlib 3.10.8; taskset -c 0-7, nice 19; TMPDIR under the run directory.
- COV2D fence (#798): no cov2d-* job in squeue at 20:03:46Z (the connect refuses before writing anything otherwise).
  watch-before.txt and watch-after.txt are `stat -c '%X %n'` (no read) of 303 COV2D inputs, the flux constraint file,
  E_R's ER/xsec.root and 300 S1_*/xsec.root, and the publication's covariance file; they are byte-identical, so no
  watched atime moved during the run.
- The step-two staging sources on CFS (the director's request: O_NOATIME needs the running user to own the file), by
  `stat -c '%U %a %X'`, no read (test.log lines 5-6): $CV runEventLoopOmniFold_MEFHC.root: owner josephrb, mode 440,
  atime 2026-10-23T15:52:50Z; $MC runEventLoopMC_MEFHC.root: owner josephrb, mode 640, atime 2026-07-21T04:16:41Z.
  Both are owned by josephrb.
- test.done (rc 0), clone.log (empty), and the connect as run.
