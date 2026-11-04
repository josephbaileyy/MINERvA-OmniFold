# COV2D binding-1 addendum A1: the writer leaves one cycle of `data` (2026-11-03)

**By** the `cov2d` session, at the director's ruling (b) on CONTROL-2A FAIL (`../control2a/CONTROL2A-REPORT.md`).
**For** the director to bind at this branch's merge. **MEASURES:** the writer change, its tests and mutants, locally.
**CANNOT AUTHORIZE:** the (2a) rerun, which is a new connect sent to the director first.

## Why

Control (2a), (c)'s first STOP:
- `cov2d_writer.write_data_file` (blob `2402ed4b`) wrote $CV's 4,119,797 rows bitwise equal, but the file held
  `data;2` and `data;3`;
- the bound exact-keys check (`cov2d_writer.py:105-107` at `2402ed4b`) refused them.

The director ruled: fix the writer, not the control. The exact-keys check is right, the toys' data files should
hold one clean cycle, and weakening the control would hide future writer drift.

**The cause.** The diagnosis ran under conda-forge ROOT 6.28/12; the cluster's root_6_28 is also 6.28/12 (step 2 of
the 2a run). The fix does not depend on AutoSave internals, but the evidence for the cause does.
- **Measured:** the bound writer at 4,119,797 rows gives `data;3`, `data;2` and `dataPOTUsed;1`. The tree's fAutoSave
  resolved to 1,939,140 entries (`../control2a/repro.txt`). `SetAutoSave(0)` gives `data;1` only, at 4,119,797 rows and
  under forced autosaves (`../control2a/semantics.txt`).
- **Inferred, not observed:** AutoSave fired during the fills, and the final Write added a cycle.
- **The review's independent run:** with ROOT's default of -300000000 bytes, the threshold reads 1,971,554 entries
  before the Write on a standalone 3-branch tree (item 1 of `REVIEW-SONNET.md`). The reviewer's account of when ROOT
  converts the byte threshold to an entry count is from memory.

## The change

`2d-unfolding/cov2d/cov2d_writer.py`, blob `2402ed4b` becomes `bb3892e5`:
- `t.SetAutoSave(0)` right after `ROOT.TTree("data", "data")`, so no intermediate cycle is written and the final Write
  is the tree's only key;
- the docstring's `write_data_file` bullet now says so.

**Why `SetAutoSave(0)` alone, not `kOverwrite`.** The director agreed.
- `Write("", kOverwrite)` deletes only the highest existing cycle. Three plain Writes followed by one kOverwrite Write
  leave `data;3`, `data;2` and `data;1` (`../control2a/semantics.txt`, E1).
- So kOverwrite gives one cycle here only because each AutoSave deletes its predecessor.
- With both lines, a mutant that drops `SetAutoSave(0)` would survive under kOverwrite.

## The tests

`2d-unfolding/cov2d/tests/test_cov2d_writer.py`, class `File`, which needs PyROOT and uproot:
- **`autosaving()`**, a context manager that forces the condition at fixture size:
  - It replaces `ROOT.TTree` with a factory that builds the real tree, sets `SetAutoSave(200)`, records the threshold as
    built, and wraps the instance's `Write` to record the threshold in force at Write. So the 2,345-row fixture reaches
    the autosaves that $CV's 4,119,797 rows reached.
  - It restores `ROOT.TTree` in a `finally`. `mock.patch.object` cannot restore it, because TTree is a lazy attribute of
    ROOT's facade and the exit's `delattr` fails. A Python subclass of TTree crashed cppyy, so `Write` is wrapped on the
    instance.
- **`test_one_cycle_when_autosave_would_fire`**, in this order:
  - the factory was used (`built == [200]`), so the test cannot pass without forcing;
  - the keys are exactly `["data;1", "dataPOTUsed;1"]`;
  - every branch is bitwise equal to the input;
  - AutoSave was off when the tree was written (`at_write == [0]`).
- **`test_control_passes_when_autosave_would_fire`:** `writer_control` passes under the forcing factory, and the factory
  was used.

**On the current blob `2402ed4b`** (`oldblob_writer_tests.txt`, in a scratch copy with the new test file), both fail, as
the cluster run did:
- the keys are `['data;11', 'data;12', 'dataPOTUsed;1']`;
- the control prints `FAILURE unexpected keys ['data;11', 'data;12']` and returns rc 3.

**On the fix** (`fixed_writer_tests.txt`): 12 of 12 pass.

## The mutants

Two were added to `../code/mutation_cov2d.py`:
- "A1: autosave left on": the line is deleted;
- "A1: autosave at ROOT's default": `SetAutoSave(-300000000)`.

The full harness kills 40 of 40 (`mutation_cov2d.txt`). The first version of the test, without the at-Write record, let
"autosave at ROOT's default" SURVIVE: at 2,345 rows a 300 MB threshold never fires, so the key check passes. That
setting is the one that failed on $CV, so the at-Write assertion was added to kill it. That earlier run's output was
overwritten by the rerun, so it is not kept here. The review reproduced the same survival independently (item 4: 1
failed, 11 passed, killed only by the at-Write assertion).

As the review notes, this mutant is killed by the stated threshold, not by observed behaviour. No small fixture can show
a 300 MB threshold firing.

## The other checks

- **Both test files, local env** (conda-forge ROOT 6.28/12, uproot 5.6.9, pytest 9.2.0): 39 passed, 2 subtests passed
  (`tests_cov2d.txt`).
- **Without ROOT** (venv, numpy 2.5.4), as omnifold_py310 runs them:
  - `test_cov2d`: Ran 27, OK (skipped=11);
  - `test_cov2d_writer`: Ran 12, OK (skipped=9) (`noroot_*.txt`).
  - **A changed expectation:** a cluster test receipt for the writer file must now expect 12 tests, 3 ok, 9 skipped (was
    10, 3, 7).
- **The fixed writer at full size** (`fixed_full.txt`, blob `bb3892e5`): 4,119,797 synthetic rows give
  `[('data', 1, 'TTree'), ('dataPOTUsed', 1, 'TParameter<double>')]`, with fAutoSave 0.
- **Other bound writers of TTrees in this campaign:** none. A grep at `c96c97f3` of `2d-unfolding/cov2d`, `re2_driver.py`,
  `fd_1b_null.py` and `fd/receipts-cov2d`, excluding tests and mutation scripts, finds `ROOT.TTree` only in
  `cov2d_writer.py`. `re2_driver.py` writes TParameters, TNamed and histograms (`:2543-2586`), and AutoSave applies
  only to TTrees. The amendment's planned pseudo-data writer calls `write_data_file`, so this fix covers it.
  Search: grep -n "TTree(\|\.Fill()\|SetAutoSave\|mktree\|uproot.recreate\|\.Write(" @ c96c97f3

## The review

`REVIEW-SONNET.md`: a fresh, read-only Sonnet check of the diff. It found no correctness defect.
- **Item 2:** the at-Write assertion came before the key check, so on the old code the key check was never reached. Now
  it comes last, and on the old code the test fails on the keys.
- **Item 5:** the docstring cites "addendum A1"; this document is that addendum.
- **The other items are caveats:**
  - `fgMaxTreeSize`'s change of file is from memory, at 100 GB;
  - AutoFlush wrote no key in a 12M-row run;
  - `ROOT.TTree` restoration was checked by reading;
  - the harness's `-x` reports only that a mutant was killed, not which test killed it.

## After the merge

- **The director binds A1:** the writer blob `bb3892e5` and the new tests. The other four bound blobs are unchanged.
- **(2a) reruns as a new connect:** M becomes A1's merge, and the writer blob check moves to `bb3892e5`. Its sha256 goes
  to the director first.

## Files

| file | what |
|---|---|
| `tests_cov2d.txt` | both test files on the fix, local env with ROOT and uproot |
| `fixed_writer_tests.txt` | `test_cov2d_writer`, unittest -v, on the fix |
| `oldblob_writer_tests.txt` | the same tests on blob `2402ed4b`, in a scratch copy |
| `mutation_cov2d.txt` | the mutation harness, 40 of 40 killed |
| `noroot_test_cov2d.txt`, `noroot_test_cov2d_writer.txt` | both files without ROOT |
| `fixed_full.txt` | the fixed writer on 4,119,797 rows |
| `REVIEW-SONNET.md`, `review_k2.py` | the fresh review and its script |
