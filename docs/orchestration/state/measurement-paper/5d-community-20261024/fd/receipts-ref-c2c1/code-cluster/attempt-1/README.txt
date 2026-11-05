REF-C2C1 code on the cluster, attempt 1: the test run with RooUnfold (the director's ruling of 2026-11-05 on #787), at
#787's head 5666f58c8231a1350439af3976bb5390f6b3880b. Run by limitation-resolver on login27, 2026-11-05T15:21:12Z-
15:22:21Z, 0 node-h, with the connect the director approved (refc2c1_tests_login.sh, sha256 1cd948a8...). Copied with
dd iflag=noatime from /pscratch/sd/j/josephrb/ref-c2c1-20261105/tests-5666f58c/. Full sha256 of each file:
SHA256SUMS.txt.

OUTCOME: RUN FAIL (rc 1), by the bound PASS rule; reported unrepaired. run_tests.sh's line: "RUN FAIL: the C-ROO test
did not run and pass". The director accepted the reading below and ruled it reported as FAIL; the fix (limitations-
catalog: unittest's result object in place of the text parser) and a rerun into a new directory are separate.
- Environment (test.log lines 1-16): a fresh clone at H, porcelain --ignored 0 before and after; run_tests.sh sha256
  ac786355a244f71e7146cd7a5ca2861a7514cd79964621aad12da5e0c3c4fa56 and the six files of 2d-unfolding/ref_c2c1/ by
  blob, 0 mismatches; libRooUnfold.so sha256 0b34e1e39102b0dddc5923dad7f69e59c70cd6a2fcbcef07728b72cf2933fefd,
  libRooUnfold_rdict.pcm c0c995d7fd55aa8b34756baf9830f1512c11ff58e408e6632712d2f0be93978f, libRooUnfold.rootmap
  fa15007eb266435e317f0a48a23bfd29d72bc6d43236fb6e422050d138938101 (O_NOATIME copies); root_6_28: python 3.11.14,
  numpy 1.26.4, ROOT 6.28/12, lightgbm 4.6.0, scikit-learn 1.8.0, matplotlib 3.10.8; taskset -c 0-7, nice 19.
- unittest's own account: "Ran 21 tests in 14.255s", then "OK"; 21 lines begin "test_", none reads "skipped".
- Why the rule failed: run_tests.sh counts the C-ROO test with
      grep -cE "^test_roounfold_bayes_is_the_same_update .*\.\.\. ok$"
  which needs the test's name and its "ok" on one line. test.log line 516 is "test_roounfold_bayes_is_the_same_update
  (__main__.Ibu.test_roounfold_bayes_is_the_same_update) ... Using response matrix priors"; RooUnfoldBayes's stdout
  (priors, "Iteration : N" and "Chi^2 of change" lines, "Calculating covariances due to number of measured events") follows, and the test's
  "ok" is the bare line 764. No other line between 516 and 764 begins "test_". The count was 0, so the rule printed
  RUN FAIL although the test ran and passed by unittest's account.
- test.done (rc 1), clone.log (empty), and the connect as run, refc2c1_tests_login.sh.
