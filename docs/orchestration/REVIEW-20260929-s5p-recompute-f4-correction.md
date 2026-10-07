# s5p Stage-6 recompute lane: independent read-only review of the s5p-F4 correction (2026-09-29)

**CITABLE FOR:** the independent reviewer's findings on the calibration-ensemble correction (finding s5p-F4) in
`nd-unfolding/s5p_recompute.py` and its regression tests, `1bfd8910..04a1d313`, quoted verbatim below; the
verification of the responses is quoted in Round 2. **NOT CITABLE FOR:** any repair (the responses are in
`HANDOFF-20260928-s5p-recompute.md` §5.6), any p-value, decision or verification result.

- Requested under the correction handoff `HANDOFF-20260929-s5p-recompute-seed-gap-correction.md` §5 (origin/main
  `04b9c6b9`).
- Reviewer: a fresh independent agent with no authorship of the reviewed code.
- Worktree: the read-only detached worktree `../MINERvA-OmniFold-s5p-recompute-review-f4` at `04a1d313`, left clean
  (`git status --short` and `--ignored` empty).
- The reviewer did not read the production evaluator bodies (`s5p_joint.py`, `s5p_inference.py`, `s5p_seqstop.py`).
- The first reviewer turn stalled (no progress for 600 s) and was resumed with its context; the report is from the
  resumed turn.

## Round 1 (verbatim)

# Review of s5p-F4 correction: `1bfd8910..04a1d313 -- nd-unfolding/`

**Commit reviewed:** `04a1d313` (branch `s5p-parallel-recompute-20260928`), in the detached worktree `/Users/josephbailey/local-research/MINERvA-OmniFold-s5p-recompute-review-f4`. The baseline is `1bfd8910`.

**Verdict: CHANGES REQUIRED.** The ensemble correction itself is right. The change also rewrote the sequential look loop, and that new loop has a MEDIUM defect: in two failure modes it misses the final looks, which the old loop did not. Everything else found is LOW or NOTE.

Scratch scripts are in `/private/tmp/claude-501/-Users-josephbailey-local-research-MINERvA-OmniFold/c08e8191-491e-4178-a878-a2d92898fc97/scratchpad/review-f4/`:
- `matrix/` holds 8 module × toy × test version combinations.
- `mut/` holds 5 mutants of the new module.
- `scenarios.py`, `control.py`, `loopcmp.py` and `identity.py` are the probes.

I did not open the code of `s5p_joint.py`, `s5p_inference.py` or `s5p_seqstop.py`.

---

## Answers to the six questions

**Q1. Is F4 real, is the new A13 faithful, and is the old reading preserved?** Yes to all three.
- The frozen text (amendment 7 `calibration.sequential_rule`) reads "evaluates both claim p-values on the finished products (partials excluded)". It has no seed range.
- I ran the 1bfd8910 module on the handoff's world: seeds `base…base+399`, with no product at +5, +17 and +203, a partial at +17, and final B = 397. It gives:
  - `products_used 394`
  - `seeds_outside_final_range [1200397, 1200398, 1200399]`
  - `count_matches_final_B False`
  - power `B_null 394`
  - looks `[198, 394, 394, 394, 394, 394, 394, 394, 394, 394]`: nine duplicate looks, only the first paired with a status file.

  This matches the handoff's consequences 1–3, and the defect was loud rather than a false agreement, as the handoff said.
- The new code, in the same world, gives `B 397`, looks `[198, 397]` (both paired), and `B_null 397`.
- The new `A13_calibration_set` (`s5p_recompute.py:109-115`) matches the frozen text. The old reading is kept as `A13_withdrawn_20260929` (`:116-121`), dated, with the finding ID and the timing ("after production outputs were visible"). Comparing the two `AMBIGUITIES` dicts, the only keys changed or added are `['A13_calibration_set', 'A13_withdrawn_20260929']`.
- The handoff's claims about production code (`product_files` line 135, `B = len(files)`, the evaluator's refusal on a count mismatch) are not verifiable under the reading bar. I relied only on the frozen text.

**Q2. Is the new code correct?** The ensemble, partial exclusion, calibration record and power are correct. `verify_sequential` is not: see F1 and F2.

**Q3. Is the change confined?** Confirmed.
- I ran `evaluate()` from both versions on three gap-free toy worlds:
  - terminal: 3 batches, a rule stop, and a power set;
  - non-terminal;
  - a budget stop at B = 0.
- After removing `ambiguities`, `nulls.*.calibration` and the two new sequential lists, the outputs are identical in all three: `terminal/nonterminal/budget0 identical after strip: True`.
- `git diff --quiet 1bfd8910 04a1d313 -- nd-unfolding/s5p_recompute_compare.py` gives rc = 0, so the comparer is unchanged.
- The comparer has 0 occurrences of `calibration`, `sequential`, `seed_gaps`, `count_mismatch`, `count_matches`, `missing_seeds`, `status_files`, `batches_adding`, `ambiguities` or `A13`. It does not import `s5p_recompute`; its only imports are hashlib, json, re and pathlib.

**Q4. Does the regression coverage work?** Mostly yes.
- **Against the old module:** running the new tests on 1bfd8910 (matrix `m-old-toynew-testnew`) gives 7 failed, 58 passed. All the SeedGaps end-to-end tests go red; some of that is only KeyErrors on the new fields.
- **Against mutants of the new code:**

  | Mutant | Change | Tests that go red |
  |---|---|---|
  | m1 | partial rule reverted to `.partial-` | 1 (`test_any_partial_name_is_excluded`) |
  | m2 | look loop stops one batch early (`range(1, n_batches)`) | 4 |
  | m3 | duplicate-look skip removed | 1 |
  | m4 | batch count always inferred from products | 2 |
  | m5 | `count_matches_final_B` hard-wired to True | 1 (only the pre-existing `test_incomplete_products…`) |

- **Faithfulness of the mutation control:** on the SeedGaps world, `withdrawn_a13_selection` reproduces the 1bfd8910 selection exactly: B 394, k/p for both tests, unshifted k, `B_null` 394, power count and decisions. It differs from 1bfd8910 only in the look list, because the control runs the new loop (see F5).
- **Brute force:** it uses the toy's loop-based `jint`, numpy Cholesky and the 1.4 % normalization from the specification, so it is independent of the evaluator. It discriminates: it asserts 0 < k < B, and B alone separates 394 from 397.
- **What the brute-force substitution does not establish:**
  - It checks only the unshifted `total` test, with surrogates, Var(mu) and the prediction residual all zeroed.
  - It shows that the recompute agrees with the specification on the toy. It does **not** show that the recompute agrees with frozen `s5p_joint` on the same files: not the partial rule, not the product selection, not the statistic.

  That agreement is left to the comparer on real outputs. Given the reading bar, the substitution is adequate for F4, a selection defect, but it does not meet the handoff's literal requirement.

**Q5. Does the toy change weaken anything?** It weakens nothing, but it hides a new dependence.
- The old tests with the new toy on the old module (`m-old-toynew-testold`) give 58 passed.
- Two pre-existing tests changed:
  - `test_incomplete_products_are_reported_and_partials_excluded`: 58 → 59 products (seed +75 is now kept), a `count_mismatch` of 60 vs 59, and the gap span becomes one batch. Each change follows from the revised A13.
  - `test_draws_are_keyed_by_seed`: signature change only.
- The new module *needs* the B0 file. With the old toy, the new module fails the pre-existing `test_sequential_looks_pair_with_status_and_respect_min_B` (matrix `m-new-toyold-testold`: 3 failed). See F2.

**Q6. Full suite.** `python3 -m pytest -q -p no:cacheprovider nd-unfolding/tests/test_s5p_recompute.py` printed **`65 passed in 26.43s`**, rc = 0.

---

## Findings

### F1 — MEDIUM — `verify_sequential` misses the last looks after a whole-batch loss (introduced by this change)

**Location:** `s5p_recompute.py:919-920` (`by_looks`, `n_batches = by_looks if files else by_products`) together with `:944` (`for b in range(1, n_batches + 1)`).

**Mechanism:**
- The loop is now bounded by the number of distinct `<null>-B<B>.json` files with stop false.
- A batch that adds no product makes the next look repeat the previous B. Under the frozen rule, the same products give the same decision, so that look continues too, and it writes to the *same* file name.
- Each such collision therefore removes one batch from the count, and the loop ends that many looks early.

The docstring (`:931-934`) says a batch "lost whole" gets no look of its own. In fact it also removes the final look.

**Evidence** (`loopcmp.py`: the 1bfd8910 loop fed the corrected full ensemble, compared with the 04a1d313 loop):

| Scenario | 1bfd8910 loop, full ensemble | 04a1d313 |
|---|---|---|
| A: batch 1 lost whole; stop "rule met" at 600 | looks 200, 200, 400, 600; first stop 600; `consistent` | looks 200, 400; first stop None; **`INCONSISTENT`** (false alarm) |
| B: batches 1 and 2 lost whole; "batches exhausted" at 600, where the rule would stop | looks 200, 200, 200, 400, 600; first stop 600 | looks **200 only**; verdict `consistent` |

**Why it matters:**
- With a single collision the result is a false INCONSISTENT, or a missing look.
- With two collisions, a production failure to stop at a missed intermediate look would be reported as `consistent`: a silent false agreement.
- The missing look is flagged only indirectly:
  - `status_files_without_a_look` catches it only if the controller also writes a B-file at the stop;
  - `seeds_outside_submitted_batches` lists 200 seeds that were in fact submitted (`scenarios.py` S1/S1b/S2b).
- No field states "final B not looked at".

**Likelihood:** whole-batch loss is improbable; the records show 1–7 lost seeds per batch. It depends on the naming by B, which the campaign records support (`GENIE_2_12_10_MEC-B193.json`, `<null>-B0.json`).

**Fix:**
- Do not bound the loop by the look-file count. Iterate until `edge ≥ base + nmax` or `len(sub) > horizon`, keeping the duplicate skip; or use `max(by_looks, by_products)`.
- Add a flag for whether the last look's B equals `B_final`.
- Add a test with a lost middle batch.

### F2 — LOW — The final look now depends on a B = 0 file existing

**Location:** same lines as F1.
- With B-files for 200 and 400 and a stop at 600, but no `-B0.json`, the new code gives looks [200, 400] and `INCONSISTENT` (loopcmp C; scenarios S3). The 1bfd8910 loop gives [200, 400, 600], `consistent`.
- Campaign records (`CLARIFICATION-20260928-s5p-recompute-A6-A8.md:12`, `HANDOFF-20260929-s5p-campaign-cold-start.md:102`) say all five B0 files exist in production, so this is LOW.
- The toy change makes every test world have a B0 file, so this dependence is invisible in the suite. The F1 fix removes it.

### F3 — LOW — A budget-refused batch is counted as "submitted"

**Location:** `seed_gap_report` `:919`, and the budget subtest in `test_a_batch_adding_no_product_gets_no_look` (test file `:500-518`).
- A look with stop false followed by a meter refusal launches no batch, yet it is counted as one.
  - Scenario S4, a budget stop at 0 with a stop-false B0 file: `batches_submitted 1`, 200 "missing" seeds.
- The subtest also overwrites the toy's stop-true `B198` file back to stop false so that its assertion `batches_submitted == 2` holds. That departs from the toy's own model of the controller, and it enshrines the miscount.
- This affects diagnostics only; the ensemble and the looks are unaffected.

### F4 — LOW — A seed below `base` enters every look

**Location:** `verify_sequential` `:946`, `sub = [p for p in prods if p.seed < edge]`.
- A stray product below `base` enters every look: S5 gives looks [(201, unpaired)] and `INCONSISTENT`.
- This is loud: `count_mismatch` and `seeds_outside_submitted_batches` both report it. It is arguably consistent with a `len(files)` rule. Noted only.

### F5 — NOTE — The mutation control's look list is not 1bfd8910's

- The control asserts `look B [198, 394]`. That is the new loop over the old selection.
- 1bfd8910 actually produced [198] followed by 394 nine times. The selection is reproduced exactly, so the control is valid for A13, but it does not model the old loop.

### F6 — NOTE — Brute force does not cover production agreement

- Covered in Q4: it does not establish agreement with frozen `s5p_joint`.
- The `.partial` vs `.partial-` alignment to production is taken from the handoff and cannot be checked here.

---

## Not checked, or could not be checked

- Any claim about production code bodies (reading barred): product selection, `B = len(files)`, the refusal on a count mismatch, and whether the controller writes a B-file at a stop or after a budget refusal, and with what `stop` value.
- Real production outputs, cluster state, and whether any whole-batch loss has actually happened (no ssh).
- The `shape` test's brute-force agreement, and surrogate, Var(mu) and residual paths under gaps.
- A world at the 1999 cap: I reasoned from the code that `hi = base + 1999` and that look 10 has edge `base + 1999`, but did not run it.
- The docs changes in the commit (the handoff, `MANIFEST.tsv`, `REVIEW-20260929-…-comparer.md`) were outside scope.

## Worktree hygiene

- The first suite run wrote `nd-unfolding/__pycache__` and `nd-unfolding/tests/__pycache__`. Both are gitignored, and their timestamps showed my run created them; I deleted them. All later runs used `PYTHONDONTWRITEBYTECODE=1` on scratch copies.
- I ran `git fetch -q` once in the main checkout `/Users/josephbailey/local-research/MINERvA-OmniFold`. That updates the shared remote-tracking refs; no working tree was touched.
- Final `git -C /Users/josephbailey/local-research/MINERvA-OmniFold-s5p-recompute-review-f4 status --short` printed nothing (rc = 0). With `--ignored` it is also empty. HEAD is `04a1d3136f0299d29cf8ddb985558841ccb026d6`.

## Round 2: verification of `0142a228` (verbatim)

**Fixes verified at 0142a228: YES.** The change reviewed is `git diff 04a1d313 0142a228 -- nd-unfolding/`, which touches `s5p_recompute.py` and `tests/test_s5p_recompute.py`. `git diff --quiet` gives rc = 0 for the toy and for `s5p_recompute_compare.py`, so neither changed. I found no new defect at MEDIUM or above. I did not read any production code bodies, used no ssh, and wrote scratch files only under `scratchpad/review-f4/`.

### Status of each round-1 finding

- **F1 (MEDIUM): fixed.**
  - The loop now runs `for b in range(1, -(-nmax // batch) + 1)`, which is 10 batches for max = 1999, and no longer uses the look-file count.
  - It stops when a look would exceed the horizon, when a repeated B has already seen every product, or at the cap or once every product has been looked at.
  - Re-running `loopcmp_r2.py` against 0142a228:
    - **A** (batch 1 lost whole, "rule met" at 600): looks 200, 400, 600; first stop 600; `consistent`. At 04a1d313 this was looks 200, 400 and `INCONSISTENT`.
    - **B** (batches 1 and 2 lost whole): looks 200, 400, 600. At 04a1d313 this was 200 only.
  - Scenarios S1, S1b, S2 and S2b now reach the final B (`final_look_is_final_B True`), and the missed look is gone even when no B-file is written at the stop.
- **F2 (LOW): fixed.** With no B0 file (scenarios C and S3), the looks are 200, 400, 600, all paired, and the verdict is `consistent`.
- **F3 (LOW): resolved as documented.**
  - The caveat is now in the `seed_gap_report` docstring (`:904-906`).
  - The budget subtest writes `-final.json` directly and no longer rewrites the look file.
  - The diagnostic still counts a refused batch as submitted (S4 lists 200 missing seeds), but this is now stated, and the ensemble and the looks do not use it.
- **F4, F5, F6: unchanged, as intended.**
  - S5 (a seed below base and one far beyond) is still loud: `count_mismatch`, `INCONSISTENT`, and now also `final_look_is_final_B False`.
  - The control's comment now says that 1bfd8910 repeated B = 394 nine times.

### Edge cases checked against the new loop (`edge_r2.py`, each run separately)

| Case | Result |
|---|---|
| Non-terminal, batch 1 running with 50 products (S6) | looks [198]; `final_look_is_final_B None`; `not terminal` |
| Only the B0 look, batch 0 running with 80 products | looks []; nothing listed |
| B = 0 budget stop (S4) | looks []; `no_new []`; `final_look_is_final_B True` (0 == 0 with no look; NOTE, acceptable) |
| Lost batch 0 | looks 200, 400; `batches_adding_no_product [0]`; both paired |
| Count mismatch, fewer products (final 400, 399 products) | looks 200, 399 (the second unpaired); `status_files_without_a_look [400]`; `count_mismatch`; final look `False` |
| Count mismatch, more products (final 399, 400 products) | the look stops at the horizon; `without_look [399]`; `count_mismatch`; final look `False` |
| Late product in batch 0 (status 199, sees 200) | look unpaired; `without_look [199, 399]`; `count_mismatch` |
| **1999 cap, actually run** (10 batches, 3 lost seeds, plus a product at seed base + 1999) | 10 looks at B 199 … 1996, last edge = base + 1999, all paired; `final_look_is_final_B True`; the base + 1999 product stays in the ensemble (B 1997), is listed outside the span, and raises `count_mismatch`; about 7 s |

Every case is either correct or loud. Some verdicts in these worlds read `INCONSISTENT`; that is because my synthetic controller continued past a look where the rule, with min_B = 0 and truth data, would stop. It is not a code defect.

### Gap-free identity against 1bfd8910

This still holds. The comparison strips `ambiguities`, `calibration`, the two sequential lists and the new `final_look_is_final_B` field. On that basis the outputs are identical (`identical after strip: True`) for all three worlds: terminal with a power set, non-terminal, and a B = 0 budget stop.

### Tests

- The three new tests fail on the 04a1d313 module: `3 failed, 64 deselected`.
  - `test_a_batch_lost_whole_keeps_every_later_look`: `[200, 400] != [200, 400, 600]`
  - `test_looks_do_not_need_the_b0_file`: `[200, 400] != [200, 400, 600]`
  - `test_a_trailing_batch_without_products_gets_no_look`: `[1] != []`
- They pass on 0142a228: `3 passed`.
- The second half of the lost-whole test covers the double collision that could hide a failure to stop; it expects first stop 600 and `INCONSISTENT` at final B 800.
- The full suite in the worktree (`PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider nd-unfolding/tests/test_s5p_recompute.py`) printed **`67 passed in 31.78s`**, rc = 0.

### New findings

None at LOW or above. One NOTE: at a B = 0 budget stop, `final_look_is_final_B` is `True` even though no look ran. That is harmless, but it could be `None` or documented.

### Not checked

- Production controller behaviour: B-file naming at a stop, or after a meter refusal (reading barred).
- Real production outputs.

### Worktree

HEAD is `0142a228b637e4a7e88dba70ddc7744a2fd23c19`. `git -C /Users/josephbailey/local-research/MINERvA-OmniFold-s5p-recompute-review-f4 status --short` printed nothing (rc = 0), and `--ignored` is also empty, so no `__pycache__` was written.

**Final reviewed commit (F4 correction): `0142a228`.**
