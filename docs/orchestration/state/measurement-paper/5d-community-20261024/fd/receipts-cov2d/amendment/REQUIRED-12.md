# COV2D: the REQUIRED mutants grow from 10 to 12 (the director's rulings (a) and (i), 2026-11-05)

**By** the `cov2d` session, 2026-11-05. **MEASURES:** the amendment's suites and mutants at `fe1c7af9`. **CANNOT
AUTHORIZE:** any job. The director's addendum to COV2D-BINDING-2.md records the change.

**Why.** Rollup's `flux_weights` opens the flux constraint with a plain `open()` (re2c_rollup.py:221 at `cb31611c`).
In COV2D its only caller is cov2d_blocks' control95 main. That main first copies every rollup input through O_NOATIME
and repoints the rollup at the copies (`noatime_inputs`, cov2d_blocks.py:152–173, called at :371), under the open
audit. The director ruled (a) that two mutants are REQUIRED for the bulk: "open audit off", and a new one that drops the
`noatime_inputs` call. The new mutant survived the first run, because no test ran control95's main. The director ruled
(i): add an end-to-end test of that main.

**The test.** `test_cov2d_blocks.Control95Main.test_main_reads_every_rollup_input_through_noatime_copies`, commit
`fe1c7af9`, blob `e3682f8d5da47cbcf39a513850c781a1a7a20cd0`.
- **What it runs:** the real `main` and the real `re2c_rollup.flux_weights`, including line 221, on a fixture.
- **The fixture:** every rollup input (the constraint, build.json, the MINOS npz, the MEFHC flux file, each playlist's
  MC and data file, and part B's ER and two MINOS products) sits in a tmp tree. The open audit's guarded prefix points
  at that tree.
- **Stubbed:** the MAT environment, `ROOT.TFile.Open` (the flux MnvH1D's error bands), and part B's arithmetic
  (`Cells`, `x01`, `section_9_5`, `c_model`).
- **It asserts:**
  - the audit refused nothing;
  - the inputs record holds each pinned input's sha256 and the 2 × playlists baseline-flux copies;
  - none of the rollup's opens touched the guarded tree;
  - where O_NOATIME exists, the verdict is PASS. On macOS, which has none, the only stop allowed is "atime moved".
- **Applied by hand,** the new mutant fails by `cov2d.Refusal: open audit: TFile.Open(<tmp>/guarded/bf/runEventLoopMC_1A.root) is not a pinned O_NOATIME copy`.
- **Job code:** none changed. Between M (`cb31611c`) and `fe1c7af9`, the only file that differs under `2d-unfolding` is
  this test file, so the deploy at M is unaffected.

**The receipts at `fe1c7af9`,** in one local environment holding PyROOT, uproot and numpy (ROOT 6.28/12, uproot 5.6.9):
- **Suites:** 156 tests, 0 skipped, all pass (`suites_fe1c7af9.txt`). This is the 155 of `suites_5c0e02a2.txt` plus
  the new test, and blocks now has 26.
- **Mutants:** 65, all killed, harness exit 0 (`mutation_amendment.txt`). The new mutant is "blocks without
  noatime_inputs before the rollup".
- **The 12 REQUIRED, all killed:**
  - "F2 bulk despite REPRICE"
  - "F2 no REPRICE list read as none"
  - "F1 order ignores M"
  - "F1 a dirty deploy admitted"
  - "F1 the pseudo record without M"
  - "F1 the pilot record without M"
  - "F3 the deploy's own binding read"
  - "F3 the binding's name check skipped"
  - "F3 a failed fetch admitted"
  - "F3 M matched anywhere in the binding"
  - "open audit off"
  - "blocks without noatime_inputs before the rollup"
- The suites and mutants ran on the working tree before the commit. The committed test file and harness have the
  sha256s recorded before the run, and `git diff HEAD -- 2d-unfolding` was empty after the commit.
