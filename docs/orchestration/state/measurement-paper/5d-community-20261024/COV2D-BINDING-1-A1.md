# BINDING 1, addendum A1: the pseudo-data writer writes one tree cycle (director, 2026-11-04)

**Binds** the writer fix of PR #737 as merged at **M_A1 = `c30f9ae216c1273a6c91cdfe3a9d13ddc8925c89`**:
`2d-unfolding/cov2d/cov2d_writer.py` at blob **`bb3892e5`**, replacing binding 1's `2402ed4b`. Its tests are in
`2d-unfolding/cov2d/tests/test_cov2d_writer.py`, and its records in `fd/receipts-cov2d/a1/`; `A1-REPORT.md` has
sha256 `03345f80…`.

**Under** [`COV2D-BINDING-1.md`](COV2D-BINDING-1.md) (#725). The other four bound blobs of binding 1 are unchanged at
M_A1: `re2_driver.py` `97f26a1d`, `cov2d.py` `7dafdd3f`, `cov2d_receipt.py` `d5718bf4` and `fd_1b_null.py`
`1810161d`.

## What led to it

- **Control (2a) FAILED,** the bound control's own verdict, rc 3 (`fd/receipts-cov2d/control2a/CONTROL2A-REPORT.md`,
  #736).
  - The content over $CV's 4,119,797 rows was bitwise equal, and the POT was equal.
  - The only failure was the extra keys `data;2` and `data;3`.
- **It is (c)'s first STOP,** under `COV2D-DECLARATION.md:358-359` via §2 :89 (the #700 source at :78). A second
  STOP ends (c) unless Joseph rules otherwise.
- **The cause was reproduced** with the bound writer at the real row count, under conda-forge ROOT 6.28/12; the
  cluster runs root_6_28, ROOT 6.28/12. The tree's AutoSave fired during the fills, and the final Write added a
  further cycle.

## What the director checked

- **The diff.** It touches only `cov2d_writer.py` (one line, `t.SetAutoSave(0)` after the TTree is built, plus the
  docstring), its test file, the mutation script and receipts.
- **The tests.** The two new tests force AutoSave at fixture size, with a guard that the forcing factory was used and
  an assertion that AutoSave is off at Write.
  - On `2402ed4b`, both FAIL with the cluster's symptom.
  - On the fix, they pass. Writer suite: 12 of 12 with ROOT and uproot.
- **The mutants.** The harness kills 40 of 40, including "autosave left on" and "autosave at ROOT's default".
- **The full-size run.** The fixed writer on 4,119,797 rows gives `data;1` and `dataPOTUsed;1` only.
- **The review.** A fresh Sonnet review of the diff found no correctness defect, and its one actionable point is
  applied (`a1/REVIEW-SONNET.md`).
- **No other bound writer** builds a TTree (`A1-REPORT.md`, with its search at `c96c97f3`).

## Rulings

1. **The writer is bound at `bb3892e5`.**
   - `kOverwrite` is not used. It deletes only the highest cycle, and alongside `SetAutoSave(0)` its line would be
     untestable.
2. **Control (2a) reruns as a new connect:**
   - M = M_A1, with the writer blob check at `bb3892e5`;
   - otherwise the approved design of `connect-2a.sh` (`b8c7656f…`), unchanged;
   - its sha256 comes to the director before it runs.
3. **Test counts:** any later cluster test receipt expects `test_cov2d_writer` at 12 total (3 ok, 9 skipped) where
   ROOT is absent.
4. **The STOP count stands at one.** This addendum does not reset it.

Nothing is submitted, deposited or tagged.
