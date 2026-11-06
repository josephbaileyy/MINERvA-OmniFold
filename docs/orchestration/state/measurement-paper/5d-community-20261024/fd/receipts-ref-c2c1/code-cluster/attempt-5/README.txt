REF-C2C1 code on the cluster, attempt 5: the test run and the mutation harness at #840's head
5938a1679e25f64e63ea1bbd4826008f43de4360 (C-PUB's operand at full precision, its source pinned and checked; the
director's ruling of 2026-11-06 on the 3b control STOP, REF-C2C1-BINDING-2.md). Run by limitation-resolver on login04,
2026-11-06T14:12:23Z-14:19:21Z, at 0 node-h, on the director's GO for refc2c1_tests_login.sh, sha256
ec6ba93f4c3b98fa04e8ea73251e8cd4835c020bd04b5c40b38020dd72043a7c. It was built from attempt 4 (edb96ee5); attempt4-to-5.diff
is the whole change. v08b80918-to-new.diff is the director's three conditions applied to the first build, 08b80918, which
did not run. Copied by O_NOATIME reads (pull_tar.py) from /pscratch/sd/j/josephrb/ref-c2c1-20261106/tests-5938a167/.
Full sha256 of each file: SHA256SUMS.txt.

OUTCOME: PASS (rc 0; test.done 0).
- THE SUITE (run_tests.sh, sha256 a8fbffd7..., EXPECT=33). unittest's own summary (test.log:879, :881):
  "Ran 33 tests in 30.060s", "OK". There's no skip, which would print "OK (skipped=1)". run_suite.py's line from
  unittest's result object (test.log:950): "RUN PASS: 33 tests, none skipped, failed or errored;
  Ibu.test_roounfold_bayes_is_the_same_update ok". run_tests.sh rc 0.
- THE HARNESS (ref_c2c1_mutation.py), after the suite and not beside it, 14:13:51Z-14:19:19Z: "MUTATION CHECK :: PASS (45
  mutations)", rc 0, with every mutant KILLED by its named test (test.log:955-999). The two new ones:
    C-PUB's reference restored to its rounded value  by Config.test_reference_constants_are_finer_than_their_tolerance
    C-PUB's source digests unchecked                 by Reads.test_c_pub_refuses_a_reference_from_other_inputs
  "C-PUB's tolerance loosened" is still killed, by Controls.test_each_control_stops_the_read. The harness's restore
  check now covers config.json as well as the two modules.
- THE ENVIRONMENT: root_6_28, python 3.11.14, numpy 1.26.4, ROOT 6.28/12, lightgbm 4.6.0, scikit-learn 1.8.0,
  matplotlib 3.10.8. libRooUnfold.so 0b34e1e3 (O_NOATIME copy). Each run's child printed, under the same
  `taskset -c 0-7 nice -n 19`:
    "child env: PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=None affinity=[6, 7] nice=19" (test.log:33, :954).
  - The affinity is [6, 7], not 0-7: the login node's own CPU set narrows taskset's request to two CPUs.
  - OMP_NUM_THREADS is unset in that probe. run_tests.sh sets OMP_NUM_THREADS=1 on the suite's command, and the
    harness sets it to 1 for its children (run()).
- THE DEPLOY: a fresh clone at H with porcelain --ignored 0 before, 0 after the suite and 0 at the end. The 8 blobs are
  pinned with 0 mismatches: config f27545e9, ref_c2c1 128b4e00 (unchanged), read 1baf74b5, test 4633f384, mutation
  a2ce6e48, run_suite f2711d4e, run_tests 1d3f971f, test_run_suite 990ec789.
- THE COV2D FENCE, a recorded line (the director's ruling for guarded readers; the tests read only their own temporary
  fixtures and the repository): the full squeue at 14:12:23Z is in test.log, with 18 cov2d-* jobs RUNNING. The 303 watched
  COV2D inputs, stat'd before the clone and after both runs, are byte-identical (watch-before.txt, watch-after.txt): no
  atime moved.
- The CFS staging sources, stat only: $CV owner josephrb, mode 440; $MC owner josephrb, mode 640.

Files: test.log (the full output), test.done, clone.log, the connect as run, the two watch snapshots, the two diffs, and
pull_tar.py.
