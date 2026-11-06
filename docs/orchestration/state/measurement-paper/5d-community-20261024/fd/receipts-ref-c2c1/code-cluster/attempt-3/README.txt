REF-C2C1 code on the cluster, attempt 3: the test run with RooUnfold at #787's hardened head
0d992845aabb00163723fdf37edcb69549b384b6. Run by limitation-resolver on login27, 2026-11-06T00:34:19Z-00:35:40Z,
0 node-h, under the director's standing rule of 2026-11-05 for routine connects (Joseph: no serial approvals): built as
attempt 2 (../attempt-2/, #800, connect 72f6ea72) with only H, P, run_tests.sh's sha256 and EXPECT changed, run because
(1) the four checks held at H, (2) the diff is only those fields, (3) the COV2D fence was clear, (4) 0 node-h. The
connect as run: refc2c1_tests_login.sh, sha256 af332432c1881278a2a804d5e06328d3a074f89d988667478a80422ed9e1e5f3.
Copied with dd iflag=noatime from /pscratch/sd/j/josephrb/ref-c2c1-20261105/tests-0d992845/. Full sha256 of each
file: SHA256SUMS.txt.

OUTCOME: RUN PASS (rc 0). run_tests.sh's own line, printed by run_suite.py check from unittest's result object
(test.log line 913): "RUN PASS: 29 tests, none skipped, failed or errored; Ibu.test_roounfold_bayes_is_the_same_update
ok". unittest: "Ran 29 tests in 25.606s", "OK".
- The four checks at H, before the build: `git show H:2d-unfolding/ref_c2c1/run_tests.sh | sha256sum` is a7dd2373...,
  equal to the director's; run_tests.sh holds the line EXPECT=29 and test_ref_c2c1.py has 29 `def test_` methods; PASS
  is run_tests.sh's own line from run_suite.py check; test_ref_c2c1.py:37 still substitutes O_NOATIME, and the suite
  names no /pscratch or /global path. config.json is the same blob as attempt 2's (808a4135), so the watched inputs
  and staging sources are unchanged.
- attempt2-to-3.diff is `diff` of attempt 2's connect (72f6ea72) against this one (af332432). Every changed line
  carries one of the fields: H and P; run_tests.sh's sha256 (e5919d91 -> a7dd2373, in the check and the header);
  EXPECT and the PASS line's count (28 -> 29, in the check, its message, the PASS grep and the header); and five of
  the eight blob pins of 2d-unfolding/ref_c2c1/, which are H's own blobs of the same eight paths (`git ls-tree -r H`;
  config.json, run_suite.py and test_run_suite.py are unchanged).
- On the node: porcelain --ignored 0 before and 0 after; run_tests.sh sha256 a7dd2373... and 0 blob mismatches;
  libRooUnfold.so 0b34e1e3 (O_NOATIME copy); root_6_28; taskset -c 0-7, nice 19.
- COV2D fence: no cov2d-* job in squeue at 00:34:19Z (and at 00:32:10Z, before the build was launched).
  watch-before.txt and watch-after.txt (stat only, 303 COV2D inputs) are byte-identical: no atime moved.
- The CFS staging sources (stat only): $CV owner josephrb, mode 440, atime 2026-10-23T15:52:50Z; $MC owner josephrb,
  mode 640, atime 2026-07-21T04:16:41Z, unchanged from attempt 2.
- test.done (rc 0), clone.log (empty), and the connect as run.
