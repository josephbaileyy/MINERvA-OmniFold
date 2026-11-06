REF-G1 ADDENDUM A1 code receipt (REF-G1-ADDENDUM-A1.md; the director's A1 items of 2026-11-05). limitations-catalog,
2026-11-05, on a detached worktree of origin/main 72e27f76 (#795). Nothing ran on the cluster; no analysis input was
read.

files.sha256    sha256 of nd-unfolding/ref_g1/{ref_g1.py, ref_g1_read.py, test_ref_g1.py, ref_g1_mutation.py,
                config.json}, taken before and after the two runs below (identical) and equal to the files committed.
tests.txt       python3 -B nd-unfolding/ref_g1/test_ref_g1.py -v  ->  Ran 40 tests, OK, exit 0 (revision 2).
harness.txt     python3 -B nd-unfolding/ref_g1/ref_g1_mutation.py  ->  MUTATION CHECK :: PASS (42 mutations, 2 expected
                survivors; revision 2), exit 0. The two expected survivors are the bound ones (the jitter step skipped; the IBU
                replica's jitter seed), each run against the whole suite.

Environment: Python 3.14.6, numpy 2.4.4, scipy 1.18.1 (a scratch venv; no ROOT), macOS arm64; PYTHONDONTWRITEBYTECODE=1
and -B. macOS has no O_NOATIME: the suite substitutes it explicitly (os.O_NONBLOCK, inert on a regular file's open),
the same on every platform, so no test exercises a real O_NOATIME open. The real flag is exercised at run time, at
the first staged copy of A1's first connect.

What changed (A1 §1-§4):
- §1 gibu1_environment also requires OMP/OPENBLAS/MKL_NUM_THREADS = "1" and a CPU affinity of 2 (config.json
  gibu1_environment.thread_env and .cpus, with their sources); the unit records both. config.json gains gibu1_product
  {path, sha256} (null; pinned from the re-run's done-marker), and the reader's G-IBU1 reads that product, not
  <run>/gibu1.npz; the read refuses while it is null.
- §2 open_noatime / copy_noatime / Staged: every declared input is copied once through O_NOATIME into a new staging
  directory, its sha256 taken in the same pass and compared with its pin where one exists; every later read uses the
  copy. Units: of_inputs_5d.npz and bkg_dump.npz (run_units), cv.npz (bank_cv), a universe's weight files (staged
  under their tag, removed after the unit), the flux-universe file, the ratios. Reader: every (e) product, D_N.npz,
  s1_assembly.npz, the flux constraint, the gibu1 product; Paired.digest takes the (e) digests from the copy pass.
  read_guards: an audit hook on Python opens refuses a read under /pscratch or /global/cfs outside the allowed roots
  without O_NOATIME; a TFile guard refuses ROOT.TFile.Open in any mode outside the allowed roots (nothing is patched
  where ROOT cannot be imported). The bars, the readout and STOP.json record staged_sha256.
- §4 `ref_g1_read.py reads` prints the gibu1 unit's and the reader's staged set (unit_reads, reader_reads).

Tests added (8) and changed: Reads (O_NOATIME absent refused, no copy made; the audit hook fires on np.load, mmap,
open, sha256 and read_bytes of a protected path and is silent on a staged read, a write, an allowed root, an
unprotected path and outside the block; the TFile guard refuses every mode outside its roots, through a stand-in
ROOT module; a staging directory is new; the reader stages exactly reader_reads' set with each file's digest, and
products_digest equals the digest bound at M; the units hand ibu1.load_inputs the copies; the constraint is read as a
copy; the read refuses until gibu1_product is pinned). Units.test_gibu1_runs_only_in_ibu1s_environment adds the
thread and CPU cases; the detector-universe and vertex tests run under the guard with their inputs protected and
check the staged set against unit_reads; the reader fixture runs bars and read under the guard with the (e)
products, D_N and s1_assembly protected.

REQUIRED mutants added (15), each killed by its named test (harness.txt): gibu1 in another thread environment; at
another CPU count; the O_NOATIME fallback restored; the audit hook disabled; the TFile guard admitting opens outside
its roots; a staging directory reused; D1 cv.npz, D2 the weights, D3 the constraint, D5 the units' inputs, D6 a
ratio, D8 the (e) central and D8 D_N.npz each read in place; the gibu1 product's pin unchecked; the read without the
gibu1 product pinned. Two bound mutants follow their lines' new text (G-IBU1's pin, G-pair's pins), and the realized-
Delta mutant now reads the (e) central through the staged copy, so the guard cannot kill it for the wrong reason.
Not covered by a local test: D7, the flux-universe file (it needs ROOT and a Flux bank fixture; no Flux universe
re-runs under A1).

The closure grep (A1 §2.4):
- closure-files.txt     the 28 files of REF-G1's import closure (revision 2; see below).
- closure-reads-at-M.tsv  the grep at M 609d8f24 (git grep at that commit): 99 hits, each with its function
                        and disposition; the 15 DECLARED rows are A1's D1-D8.
- closure-reads.tsv     the grep at A1's revision: 108 hits, each with its function and disposition, produced by
                        closure_dispositions.py from
                          xargs grep -nE "open\(|np\.load|read_text|read_bytes|mmap|TFile|uproot\.open" < closure-files.txt
- closure-trace.txt     python3 -B closure_trace.py <repo> closure-reads.tsv closure-trace.txt: the suite under
                        sys.monitoring LINE events; a "not reached" hit counts as REACHED only when a ref_g1.py or
                        ref_g1_read.py frame is on the stack. Result: 40 tests OK; 0 of 74 "not reached" hits executed
                        from the run path; 1 fixture-only (pvl_lib.sha256_path, called by the test's own
                        pvl_ratios.write_ratio). The trace sees only what the fixtures exercise.
- closure-trace-control.txt  the same run with ibu1.py:55 and s5p_universe.py:94 (both on the run path) relabelled "not
                        reached": both REACHED, exit 1. The check has power.

Revision 2 (coverage-5b-audit's review of #806 at a8e14aa9 and the director's rulings of 2026-11-06). Every file above
is replaced by this revision's run; the counts below supersede the ones above.
- B1 (blocking): the bars record config_sha256, and A1's first order merged the gibu1 pin into config.json between
  the bars and the read, so the read would have refused. The director ruled option (a): config.json carries no
  gibu1_product; `ref_g1_read.py read` takes --gibu1-product PATH --gibu1-sha256 SHA (from the re-run's done-marker,
  committed with bars.json in connect 1's receipt); G-IBU1 checks the product on its staged copy; the readout and
  STOP.json record both. Test Reads.test_bars_then_the_pin_merge_then_the_read: bars, then the pin committed beside
  them, then the read, which forms a reading; and the same read refused once config.json is changed between the two.
  Reads.test_the_read_refuses_until_the_gibu1_product_is_given replaces the config-pin test.
- L1: the closure is 28 files, derived from the code (every repository module reached by an import anywhere in
  ref_g1.py, ref_g1_read.py and the path-loaded did.py, stdlib names excluded); it adds the five modules imported
  only inside uncalled functions. The grep: 99 hits at M (closure-reads-at-M.tsv; the 10 new ones are in the five
  modules, each in a function REF-G1 does not call), 108 at this revision (closure-reads.tsv).
- L2: read_guards(protected, allowed, root). The TFile guard is installed only for a unit set with a Flux universe
  (needs_root); otherwise ROOT is not imported for it, and the block fails if anything imports ROOT. The gibu1 unit
  and the reader run with root=False. Test Reads.test_a_block_without_the_tfile_guard_refuses_a_root_import; REQUIRED
  mutant "a ROOT import admitted without the TFile guard".
- L3: environment() records threadpoolctl.threadpool_info() where threadpoolctl can be imported, else says so, and
  root_loaded.
- tests.txt     40 tests, OK, exit 0.
- harness.txt   MUTATION CHECK :: PASS (42 mutations, 2 expected survivors), exit 0.
- closure-trace.txt   40 tests OK; 0 of 74 "not reached" hits executed from the run path; 1 fixture-only
                      (pvl_lib.sha256_path).
- closure-trace-control.txt   ibu1.py:55 and s5p_universe.py:94 relabelled: both REACHED, exit 1.
- files.sha256  identical before and after the runs, and to the files committed.
Follow-up list (deferred under the director's freeze; changed only if a run STOPs): none raised against REF-G1 at
this revision beyond D7's missing local test (above).
