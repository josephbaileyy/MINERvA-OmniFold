REF-C2C1 code receipt (REF-C2C1-BINDING-1.md ruling 3: the code lane writes the code §4 lists, with tests and a
mutation harness, for coverage-5b-audit and step two). limitations-catalog, 2026-11-05, on a detached worktree of
origin/main 2e17de39f (#784). Nothing ran on the cluster; no analysis input was read.

files.sha256    sha256 of the five files the runs below used, taken before and after both runs (identical).
tests.txt       test_ref_c2c1.py -v  ->  Ran 17 tests, OK (skipped=1), exit 0. The skip is the C-ROO test, which needs
                libRooUnfold.so (REF_C2C1_ROOUNFOLD); RooUnfold is on the cluster only (preconditions, #779).
harness.txt     ref_c2c1_mutation.py  ->  MUTATION CHECK :: PASS (22 mutations), exit 0: a mutant per control, per
                reading bar, per pairing key and the rank rule, each killed by its named test.

Environment: Python 3.13.7, numpy 2.4.4, scipy 1.18.1, LightGBM 4.7.0, scikit-learn 1.9.1,
ROOT 6.36.000 (Homebrew), matplotlib for compare_to_paper_fullcov's import; OMP_NUM_THREADS=1,
PYTHONDONTWRITEBYTECODE=1 and -B, and no __pycache__ was left.

How the code meets the declaration, for the audit and step two:
- c2 and c1 run E_R's own driver (re2_driver.py, pinned) in-process with E_R's recorded argv; only one seam differs.
  c2 replaces the driver's single OmniFold call with binned D'Agostini IBU on the same arrays, returning per-event
  unfolded/prior so the driver's own fill and extraction give hXSec2D; the extraction call is recorded and re-applied
  at every K of the frozen scan. c1 merges s5c_unfold's four deterministic keys into every LightGBM the driver builds,
  the refinement classifier included, and records each construction (C-SET).
- The driver tests run on RE-2's own synthetic omnifile (re2/tests/test_re2_driver.py write_fixture) through the
  driver's real loaders, two OmniFold iterations.
- C-BKGSTREAM: a three-stream replica on the fixture is silent; with one planted signal fake the driver's own guard
  refuses ("fakes" in its message).
- A failed control stops the read: STOP.json, no difference formed, no reading written (the REF-G1 audit's C1, applied
  here from the start); a unit is skipped on a rerun only with a PASS done-marker.
- The replica set is a config switch, null until step two binds it from C-DRAW's verdict; units refuse while unbound.
- The pinned driver equals E_R's deploy blob dbdad2f9 but for the COV2D --data-file option, inert without that flag.
- verify_hash_bindings.py globs docs/ and nd-unfolding/ JSON only, so config.json's pins (2d-unfolding/) are not in
  its inventory; the code checks them itself before any run.
