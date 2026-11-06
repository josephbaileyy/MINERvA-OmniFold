REF-C2C1 code on the cluster, attempt 4: the test run with RooUnfold at #810's head
9f593aa5abc5760e6ca96f22e0fc912ce93164a3 (step two's three config.json values: the replica set "reuse", the staging
root, the RooUnfold library's full sha256; and one test line). Run by limitation-resolver on login27,
2026-11-06T02:14:40Z-02:16:03Z, 0 node-h, under the director's standing rule for routine connects: built as attempt 3
(../attempt-3/, #805, connect af332432) with only H, P and the pin fields changed, run because the four checks held at
H, the diff is only those fields, the COV2D fence was clear and the cost is 0 node-h. The connect as run:
refc2c1_tests_login.sh, sha256 edb96ee5d34eb6b51ed6d3010669efd98c604fa7d95b61efae83a036abe5b361. Copied with dd
iflag=noatime from /pscratch/sd/j/josephrb/ref-c2c1-20261105/tests-9f593aa5/. Full sha256 of each file:
SHA256SUMS.txt.

OUTCOME: RUN PASS (rc 0). run_tests.sh's own line, printed by run_suite.py check from unittest's result object
(test.log line 913): "RUN PASS: 29 tests, none skipped, failed or errored; Ibu.test_roounfold_bayes_is_the_same_update
ok". unittest: "Ran 29 tests in 29.636s", "OK".
- The checks at H, before the build: run_tests.sh's sha256 is still a7dd2373... (EXPECT=29; 29 `def test_` methods in
  test_ref_c2c1.py); PASS is run_tests.sh's own line; test_ref_c2c1.py:37 still substitutes O_NOATIME, and the file
  names no /pscratch or /global path. `git diff 0d992845 H -- 2d-unfolding/ref_c2c1/` changes only config.json (the
  three values and the library note) and one line of test_ref_c2c1.py (the fixture unbinds replica_set.choice).
- attempt3-to-4.diff is `diff` of attempt 3's connect (af332432) against this one (edb96ee5): H, P and the blob pins of
  config.json (808a4135 -> 96dbbaa2) and test_ref_c2c1.py (bd13922e -> 0d2f1a24); nothing else.
- On the node: porcelain --ignored 0 before and 0 after; run_tests.sh sha256 a7dd2373... and 0 blob mismatches;
  libRooUnfold.so 0b34e1e3 (O_NOATIME copy); root_6_28; taskset -c 0-7, nice 19.
- COV2D fence: no cov2d-* job in squeue at 02:12:09Z (cov2d_fence.sh) and at 02:14:40Z (in the connect).
  watch-before.txt and watch-after.txt (stat only, 303 COV2D inputs) are byte-identical: no atime moved.
- The new staging root /pscratch/sd/j/josephrb/ref-c2c1-20261106/stage does not exist, nor does its parent, by stat
  at 02:12:12Z (before) and 02:17:03Z (after) (staging-root-stat-before.txt, -after.txt); this run did not create it.
- The CFS staging sources (stat only): $CV owner josephrb, mode 440; $MC owner josephrb, mode 640, as before.
- test.done (rc 0), clone.log (empty), and the connect as run.
