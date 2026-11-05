# COV2D amendment, rolling audit part 2: the §6 readouts (b336e80d)

**Auditor:** the `coverage-5b-audit` session, 2026-11-04, read-only, from a fresh detached worktree. Its report,
received by SendMessage, is copied verbatim below. The answers and fixes are in `ANSWERS.md` (this directory).

---

COV2D audit part 2 (the §6 readouts at b336e80d): no verdict-affecting defect. The cross-terms test is vacuous, and the leave-out-MEC wording departs from 1B §5.4. Details below.

How I checked: a fresh detached worktree. Both suites pass (22 tests, uproot 5.6.2). I ran 17 mutants of my own, each against both suites, with the unmutated pair passing first: 6 KILLED and 11 SURVIVED. Afterwards there were 0 .pyc and a clean status.

**Findings, most severe first**

**R1 (medium; RUN): the cross-terms CLI test pins almost nothing.**
- The test is test_cov2d_readouts.py:116, "...matches_a_hand_first_order_histogram". It makes no hand comparison: it asserts only n = 300 per tune, atime_moved == [], and max_abs > 0.
- All five of my cross-term mutants survive:
  - the background tree skipped;
  - the product without r_T;
  - the unit F instead of √F;
  - AR23 using G18's draws;
  - **product composition replaced by first order × 1.001.**
- What would close it: on the fixture, F and P for one draw per truth equal a hand computation; the per-cell z equals (P − F)/√F; and AR23's draws are not G18's.

**R2 (low-medium; RUN): the GENIE + MEC reading isn't 1B's text.**
- §6 says the variant is "read exactly as 1B §5.4 fixes it", which is fd_1b_mc.py:803–808.
- Two cases differ. I ran each, patching grade's output:

| case | cov2d's reading | 1B's reading |
|---|---|---|
| C_T⁻ flags only jointly | "its coverage in cells [] rests on the GENIE + MEC shift" | "…cells [...] (and jointly) rests on…" |
| nothing flags under C_T⁻ | no reading key | "covers without the GENIE + MEC shift" |

- Also, when C_T under-covers, 1B prints "printed; no reading (the tune under-covers under C_T)", and cov2d is silent.
- The trigger condition itself equals 1B's.
- Two mutants survive here:
  - "newly ignores C_T's flags": the test's C_T grade has no flags;
  - "the C_T⁻ null at fd_1b_null's default seed": nothing checks the seed.

**R3 (low; reading): the C_T⁻ null is built inside the readout, from the call that holds E (cov2d_readouts.py:72).**
- 1B builds both nulls, C_T and C_T_minus_mec, in its null step, before any toy error is read (fd_1b_mc.py:740).
- The value doesn't depend on E and is seeded, so nothing is contaminated. But it moves §5.2's "before any toy error is read" for the variant.
- What would close it: build C_T⁻'s null beside C_T's in null_at_T, and have the readout take it as input.

**R4 (low; RUN): four §6(ii) outputs are untested.** These mutants survive:
<!-- absence-ok: added by the cov2d session, not the auditor: the auditor's claim rests on the mutants it ran, listed here -->
- the coherent offset on the identity instead of C_T;
- the coherent offset without x_true;
- the outlier's max reported as its median;
- a missing R_c entering the medians as 0.

The fixture uses a constant R, so medians and maxima can't separate.

**R5 (low; reading): clipping_residual trusts the row order.**
- cells.npz carries `seeds` (cov2d_pseudo.py savez), but clipping_residual never compares cells_npz["seeds"][toy_index] with TOY_SEEDS[truth].
- x_true's rows are assumed to follow the same order.
- Failure scenario: a caller passes toy_index in a different order from x_true's rows. Each R_c is then scaled by another toy's truth, with no refusal.

**R6 (low; reading): the outlier cell is skipped if 216 ∉ rep (:116).** §5.2 requires its reading "whatever it is", so this should refuse, as for the scorer (part 1).

**R7 (note; RUN): uncounted all-NaN cells.** The CLI test prints "RuntimeWarning: All-NaN slice" at :209. Cells with F ≤ 0 in every draw get a NaN median, and (cell, draw) pairs with F ≤ 0 are excluded without a count. What would close it: record the count, as (ii) does for its missing values.

**R8 (note): --no-pins isn't recorded.** It is documented as "tests only", but the output record doesn't say whether pins were checked.

**Your four choices**
- **(i) Product composition:** this is C2's definition (clip_probe2.py:16–17, :276–288): zero where a_CV ≤ 0 or any drawn a_uj ≤ 0, otherwise a_CV ∏ (a_uj/a_CV). C2 applied it to the truth tree only, so extending it to the reco histogram is yours, which is fine.
  - $UNI is opened once for both truths.
  - The unit is √(that draw's first-order count). That's defensible, but the report should say so, with F ≤ 0 counted (R7).
- **(ii) Missing R_c as 0 in R:** acceptable, since the count is recorded. Setting a missing value to 0 can only shrink the coherent offset, so also report it over the toys with no missing cell.
- **The predicted offset over the 38 bands:** correct. It is 1B's formula and sign (fd_1b_mc.py:814), and the lateral surrogate is centred, so it adds nothing.
- **Leave-out-MEC on its own null:** right, as 1B does, and the trigger matches 1B's. The text doesn't (R2).

Verified with no finding:
- S_reco: reco_cell already returns −1 for unkept rows, so the unused kept_r in the test hides nothing. My mutant dropping the mask was killed.
- Spread alone is against C_T − C_model_abs, as 1B's C_e.
- m_seen/S (the C1 erratum) and the background over S_reco are each pinned by a killed mutant.

Part 1 (null and scorer) follows when my last mutant finishes. Part 3 (the job scripts) is in the next message. I'll audit part 4 (the pilot) next.
