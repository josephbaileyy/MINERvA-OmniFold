REF-C2C1 code receipt (REF-C2C1-BINDING-1.md ruling 3: the code lane writes the code §4 lists, with tests and a
mutation harness, for coverage-5b-audit and step two). limitations-catalog, 2026-11-05, on a detached worktree of
origin/main 2e17de39f (#784). Nothing ran on the cluster; no analysis input was read.

files.sha256    sha256 of the eight files the runs below used, taken before and after both runs (identical).
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

Revision 4 (the cluster test run of 2026-11-05 read RUN FAIL with all 21 tests OK, 0 skipped: RooUnfoldBayes printed
to stdout between the C-ROO test's name and its "ok", so run_tests.sh's one-line grep counted C-ROO as not run; the
director's ruling): run_tests.sh now decides from unittest's result object. run_suite.py runs the suite with a
recording TextTestResult and writes per-test outcomes to JSON; its `check` requires 21 run, no skip, fail or error, and
C-ROO "ok". RooUnfold's stdout stays in the log.
- test_run_suite.txt   test_run_suite.py -v -> 5 tests OK: on a fixture whose C-ROO-named test writes to fd 1 mid-run,
                       the runner counts it, the OLD grep misses it on the same output (the fixture reaches the
                       defect), and the verdict fails on any skip, failure, error, class-level error or short count.
- run_tests-dummy-lib.txt   run_tests.sh end to end here with a dummy libRooUnfold.so: 21 ran, C-ROO "error",
                       RUN FAIL, decided from the outcomes JSON.
- ref_c2c1.py, ref_c2c1_read.py, test_ref_c2c1.py and ref_c2c1_mutation.py are unchanged from 5666f58c8 (their
  sha256 in files.sha256 equal the earlier receipt's), so tests.txt and harness.txt stand.

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

Revision 5 (the director's ruling of 2026-11-05: the staging root, #787's last code item before step two). E_R's
driver opens $CV and $MC with ROOT.TFile.Open, which cannot take O_NOATIME, so the driver reads only copies staged
under a staging root by an O_NOATIME DTN step:
- config.json: inputs.CV_source and MC_source name the CFS copies (the pscratch $MC is no longer read);
  inputs.staging gives the root (null until step two binds it) and the two staged names. staging_root() refuses
  while the root is null; check_inputs() refuses any input path not under the root, then reads it through O_NOATIME
  against CV_sha256 / MC_sha256; resolve_argv() substitutes $CV and $MC with the staged paths.
- run_driver() wraps ROOT.TFile.Open for the driver's whole run: any open for reading of a path outside the staging
  root raises GateFailure, so a unit stops (writes are not refused: the output is RECREATEd elsewhere).
- Test: Driver.test_reads_outside_the_staging_root_are_refused, on RE-2's fixture files: an unbound root is refused;
  a staged name resolving outside the root is refused by check_inputs; the driver opening --mcfile outside the root
  is refused by the guard; and the same driver run is silent once every file it opens is under the root.
- Two REQUIRED mutants: the guard disabled ("the driver's reads outside the staging root admitted") and the root
  check disabled ("a staged input outside the root admitted"); both killed by that test.
- tests.txt         22 tests, OK (skipped=1: C-ROO, no libRooUnfold.so here), exit 0.
- harness.txt       MUTATION CHECK :: PASS (34 mutations), exit 0; every mutant killed by its named test.
- test_run_suite.txt  5 tests OK (run_suite.py and test_run_suite.py unchanged since revision 4).
- run_tests-dummy-lib.txt  run_tests.sh (EXPECT now 22) with a dummy library: 22 ran, C-ROO "error", RUN FAIL.
- files.sha256      the files the runs used, identical before and after.
- Not covered here: the guard sees only ROOT.TFile.Open. A read by another route (uproot, or C++ that opens a file
  without TFile::Open) would not be refused; the #787 closure grep records every read route of the driver's closure.

Revision 6 (the director's ruling of 2026-11-05 on the #787 closure grep's two findings, before limitation-resolver's
test connect):
- R1, the reader's plain reads. ref_c2c1_read.read now runs under ref_c2c1.read_guards for its whole run:
  - every file outside the run directory, the read directory, the cells file and the checkout (E_R's central xsec.root,
    its replica xsec.roots, the publication's ROOT file) is copied once through O_NOATIME into <read dir>/inputs/
    (Staged; the directory must not exist, so a re-run reads into a new one), its sha256 taken in the same pass;
    C-IN and the publication's pin are checked on those digests; every ROOT open reads the copy. The readout and
    STOP.json record staged_sha256. write_cells stages the publication the same way into <cells>-inputs/;
  - an audit hook on Python opens (event "open", which carries the open's flags) refuses a read of a path under
    /pscratch or /global/cfs outside the allowed roots without O_NOATIME;
  - the TFile guard (now one function, tfile_guard, shared with the driver's staging guard) refuses a ROOT read
    outside the allowed roots;
  - C-FILL reads the unit's own hXSec2D through own_hxsec, which refuses a path outside the run or staging root
    (a symlink resolving outside included).
  The run's own products are read in place (the director's ruling).
- R2: noatime_flag() refuses where the platform has no O_NOATIME (the getattr(os, "O_NOATIME", 0) fallback is gone).
  The tests substitute the flag explicitly (O_NONBLOCK, inert on a regular file's open), the same on every platform.
- Tests (6 new, class Reads): O_NOATIME absent is refused and no copy is made; the audit hook fires on np.load, open,
  sha256 and read_bytes of a protected path and is silent on an O_NOATIME read, a write, an allowed root, an
  unprotected path and outside the block; the reader's TFile guard fires outside its roots and is silent inside; a
  full read with E_R's files and the publication as the protected set passes, stages each of them once with its
  digest, and a re-run into the same directory is refused; a wrong publication pin is refused on the copy; C-FILL
  refuses a path outside the run and staging roots.
- REQUIRED mutants (7 new): the O_NOATIME fallback restored, the audit hook disabled, the reader's TFile guard not
  installed, the read opening E_R's original, the publication's pin unchecked on the copy, a re-run reusing the
  staged directory, and C-FILL's path check disabled; each killed by its named test. The staging-guard and C-IN
  mutants follow their lines' new text.
- closure-reads.tsv   the #787 closure grep at this revision: 41 hits in the 11 files of closure-files.txt (patterns:
                      open(, np.load, read_text, read_bytes, mmap, TFile, uproot.open, TChain, RDataFrame,
                      pickle.load, loadtxt, genfromtxt, fromfile, .Open(), each with its function and disposition.
                      The grep at cab13dbe8 had 39 hits and the two findings above. The 41 here differ by the fix's
                      own lines (open_noatime, copy_noatime, the shared tfile_guard and two docstrings that name
                      TFile.Open, own_hxsec) and by moved line numbers; the other nine files are unchanged.
- tests.txt         28 tests, OK (skipped=1: C-ROO), exit 0.
- harness.txt       MUTATION CHECK :: PASS (41 mutations), exit 0.
- test_run_suite.txt  5 tests OK.
- run_tests-dummy-lib.txt  run_tests.sh (EXPECT 28) with a dummy library: 28 ran, C-ROO "error", RUN FAIL.
- files.sha256      identical before and after.

Revision 7 (coverage-5b-audit's note on #787's delta and the director's ruling of 2026-11-05: the TFile guard
hardened before step two binds; limitation-resolver's attempt 2 PASSed at 0e001f3c, and attempt 3 re-runs the
cluster suite at this head):
- tfile_guard(readable, writable, what): a TFile::Open mode that reads (any but RECREATE, NEW, CREATE; UPDATE
  included) is refused outside the readable roots, and a mode that writes (any but READ and
  READ_WITHOUT_GLOBALREGISTRATION; an unknown mode counts as both) outside the writable roots. Before, only "READ" and
  "" were checked, and writes were not.
  - the driver: reads only under the staging root, writes only in its --out's directory (the run directory);
  - the reader: reads under the run directory, the read directory, the cells file and the checkout; writes only in
    the read directory.
- Test: Reads.test_the_tfile_guard_confines_reads_and_writes_by_mode, with real ROOT files, both ways: READ and
  READ_WITHOUT_GLOBALREGISTRATION outside the readable roots, READ in a write-only root, UPDATE in a read-only and in
  a write-only root, RECREATE and NEW outside the writable roots are each refused (and NEW creates nothing); READ,
  READ_WITHOUT_GLOBALREGISTRATION, RECREATE and UPDATE each in their allowed roots succeed.
- REQUIRED mutants (2 new): reads gated only on "READ", and the write check dropped; both killed by that test. The
  driver's staging mutant and the reader's TFile-guard mutant follow their lines' new text.
- tests.txt         29 tests, OK (skipped=1: C-ROO), exit 0.
- harness.txt       MUTATION CHECK :: PASS (43 mutations), exit 0.
- test_run_suite.txt  5 tests OK.
- run_tests-dummy-lib.txt  run_tests.sh (EXPECT 29) with a dummy library: 29 ran, C-ROO "error", RUN FAIL.
- files.sha256      identical before and after.
- closure-reads.tsv   regenerated at this revision (42 hits: ref_c2c1.py gains the mode constant; its line numbers moved; the guard's row states the new rule).
