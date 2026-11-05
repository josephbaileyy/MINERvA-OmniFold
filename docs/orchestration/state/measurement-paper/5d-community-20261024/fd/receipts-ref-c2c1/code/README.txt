REF-C2C1 code receipt (REF-C2C1-BINDING-1.md ruling 3: the code lane writes the code §4 lists, with tests and a
mutation harness, for coverage-5b-audit and step two). limitations-catalog, 2026-11-05, on a detached worktree of
origin/main 2e17de39f (#784). Nothing ran on the cluster; no analysis input was read.

files.sha256    sha256 of the six files the runs below used, taken before and after both runs (identical).
tests.txt       test_ref_c2c1.py -v  ->  Ran 21 tests, OK (skipped=1), exit 0. The skip is the C-ROO test, which needs
                libRooUnfold.so (REF_C2C1_ROOUNFOLD); RooUnfold is on the cluster only (preconditions, #779).
harness.txt     ref_c2c1_mutation.py  ->  MUTATION CHECK :: PASS (32 mutations), exit 0: a mutant per control, per
                reading bar, per pairing key and the rank rule, each killed by its named test.

Environment: Python 3.13.7, numpy 2.4.4, scipy 1.18.1, LightGBM 4.7.0, scikit-learn 1.9.1,
ROOT 6.36.000 (Homebrew), matplotlib for compare_to_paper_fullcov's import; OMP_NUM_THREADS=1,
PYTHONDONTWRITEBYTECODE=1 and -B, and no __pycache__ was left.

Revision 2 (the code audit, #787: K1-K3 upheld by the director, 2026-11-05):
- K1: C-SIM goes through the full chain (IBU on the MC's own reco expectation, the seam's per-event factors, the
  driver's fill and recorded extraction) against the MC's FULL-truth cross section (the driver's hOFTruthDenom2D
  through the same normalisation with unit completeness), 1e-9 at every K on every covered cell; it kills the
  efficiency applied twice. A mis-indexed factor is invisible at the fixed point (every factor is 1 there; the test
  asserts that premise), so C-FILL, on every c2 unit, compares the driver's own hXSec2D with the recorded extraction
  of IBU's unfolded vector at 1e-12 on the data, and kills the factor read from the neighbouring bin (the director
  accepted this placement).
- K2: C-IN reads the CV omnifile and the flux file through O_NOATIME and checks them against config's pins before the
  driver opens them; main() refuses (rc 4), a missing file included; each unit records the verified digests and the
  reader requires them.
- K3: er and c1 bin the driver's refined weights on the way into its own OmniFold call; the read requires c2's
  measured histogram to equal er's per bin at 1e-8 (per event is not available across processes).
- run_tests.sh: the RooUnfold test run (all 21, C-ROO must run, none skipped), for limitation-resolver's 0-node-h
  login-node connect with the cluster's libRooUnfold.so (the director's ruling); its failure path was checked here
  with a dummy library (RUN FAIL, C-ROO errors).
Each change has a test and a mutant.

Revision 3 (the audit's check of revision 2 and the director's rulings, 2026-11-05):
- C-FILL's tolerance is 1e-9 relative (rounding of the per-event fill grows with a truth bin's event count; a
  mis-indexed factor moves cells by O(1)); each c2 unit records its measured max_rel. Its loosened-tolerance mutant
  loosens to 1e-6 and is killed by a 1e-7 perturbation.
- Every driver unit records its CPU count and refuses unless it is E_R's 64 (re2/run/partb_runs.tsv row ER), like for
  like as RE2-DECLARATION.md:42 and :166 require; the read's C-CPUS requires it of er, c2_central and c1_central.
- Every driver unit records OMP_NUM_THREADS, MKL_NUM_THREADS and OPENBLAS_NUM_THREADS and refuses unless they are
  E_R's 64, 1, 1 (re2/run/launch/re2_env.sh:31; RE2-DECLARATION.md:166); C-CPUS requires them too.

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
