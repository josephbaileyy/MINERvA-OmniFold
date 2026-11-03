# BINDING 1: campaign (c), held-out-tune method coverage of the 2D covariance (director, 2026-11-03)

**Binds** [`COV2D-DECLARATION.md`](COV2D-DECLARATION.md), sha256
`0328c916d2c763c4529d3541fe05f430f7b2e6e4937f7749660cb3da06c6fbb6`, as merged in PR #723 at
**M = `dec97852f8da840c855777fa3d2179d6548252ee`** (PR head `65c245ee`).

**Under:**
- `DECISION-20261102-joseph-quadrant-sentence-sec4-and-validations.md` item 3(c) (#690);
- `DECISION-20261102-joseph-1b-redesign.md` (#700), as the director ruled it applies to (c);
- `DECISION-20261103-joseph-coverage-clip-rule.md` (#718, with the director's clarification, #721).

**What this binds.** The design: §1–§10 and §12–§13. And the code of §11 by blob at M:

| file | blob at M |
|---|---|
| `2d-unfolding/re2/re2_driver.py` | `97f26a1d` (sha256 `938c53c5…`) |
| `2d-unfolding/cov2d/cov2d.py` | `7dafdd3f` (sha256 `0d852a69…`) |
| `2d-unfolding/cov2d/cov2d_receipt.py` | `d5718bf4` (sha256 `c085b51f…`) |
| `2d-unfolding/cov2d/cov2d_writer.py` | `2402ed4b` (sha256 `6a606b3c…`) |
| `nd-unfolding/fd_1b_null.py` | `1810161d` (sha256 `ec1402db…`) |

The toy, block, truth, null-input and scorer code are the amendment's, and binding 2's.

## What the director checked

- **The digests.** The declaration's sha256 at M is the one above. Each blob at M equals the lane's stated blob.
- **The audit.** A fresh Sonnet subagent, with prompt (sha256 `80be3fc9…`) and answer verbatim in
  `fd/receipts-cov2d/audit/`. Its verdict was "READY AFTER MINOR FIXES", with no BLOCKING finding. Each of its 12
  findings has a disposition in `fd/receipts-cov2d/audit/DISPOSITIONS.md`, and the director accepts them as given.
  Finding 2 is ruled below.
- **The clipping record.**
  - C1 carries its erratum (`fd/receipts-cov2d/clip/C1-ERRATUM.txt`).
  - C2's code and reading were committed before it ran, at `1a07b07c`. Its receipts are at `bc4965c4` and are now on
    main through #723.
  - §4.2 implements the per-tree rule of #718 as clarified in #721.

## Rulings

1. **The design is bound as declared**, with the order of §10:
   - control (2a) on a login node and staging from a DTN, next;
   - then the amendment and binding 2;
   - then the pilot, whose readout comes to the director before the bulk;
   - then the bulk.

   The director is told, with each connect script's sha256, before each connect and each submission.
2. **§14 item 2 (audit finding 2):**
   - **The substitute is accepted, labelled as a substitute.** It is C2's first-order residual R_c, taken per toy at
     the nature's expected counts, for the mean unfold that 2D cannot run.
   - **The 0.5 σ_c reading is kept as declared.** It was fixed in `fc2cd112` before any clipping probe ran.
     Replacing it after C2 predicted it would not fire would be a post-C2 choice.
   - **The report states C2's prediction beside it:** the largest median |R| is 0.043 / 0.042 σ_Q, so the 0.5 reading
     is not expected to fire.
   - R_c is counted as missing where S_c ≤ 0 or N_c ≤ 0, as declared.
3. **The price.**
   - The cap is **165.8 node-h** over both truths: 105.0–126.2 at the units, times 1.25, plus a 6.0 pseudo-data
     reserve and a 2.0 pilot reserve.
   - CPU only, regular QOS, every job under 12 h, nothing written to CFS from a job.
   - It is below half the last-read balance (1,025.5 of 2,050.9 at 2026-11-02T16:15Z), so it does not go back to
     Joseph for approval. The director reports it to Joseph with this binding, as §8 asks.
   - The scoping's price was 80–153 node-h. The cap is above that range because of the 1.25 factor and the reserves.
   - The REPRICE triggers of §8 stand.
4. **Tests in the cluster environment** (§11's "the binding re-runs them"). Before control (2a), from a fresh /dev/shm
   clone at M on a login node, with no pscratch or CFS reads, 0 node-h and no job:
   - Re-run `re2/tests/test_re2_data_file.py`, `test_re2_driver.py` and `cov2d/tests/test_null205.py` under
     `root_6_28`.
   - `root_6_28` has no uproot. So `test_cov2d.py` and `test_cov2d_writer.py`, which use it, run in the environment
     the receipt and C1/C2 ran in. Name that environment.
   - Commit the logs, the node and the porcelain before and after as a receipt. A failure is fixed and reported before
     any connect.
5. **The schedule of §10 is bound,** including its terminal branch: no `$UNI`-reading job submitted by 2026-12-01
   means no bulk and a report. No partial ensemble is graded.
6. **Retention and HPSS.** §7 is bound. Products go to HPSS after the deferral (#685, after 2026-11-06 17:00) under
   `RECORD-20261102-director-hpss-deferral.md`. Nothing goes to CFS.
7. **The paper and the note.**
   - §12 is bound: what each outcome must say, the clipping facts to the note in every outcome, and nothing to the
     paper beyond §12's sentences.
   - The paper lane drafts the text when a result lands. It goes through a PRD-referee read and to Joseph before merge.
   - §13's licence and its limits are bound, including the C_model shortfall of about 23% that a pass can hide, stated
     beside any pass.

Nothing is submitted, deposited or tagged.
