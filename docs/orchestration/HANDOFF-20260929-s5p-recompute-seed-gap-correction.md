# s5p (`OI-193`) Stage 6: the recompute's seed-range restriction must be corrected before final verification (2026-09-29)

**For:** the independent recompute session (`s5p-parallel-recompute-20260928`, worktree
`../MINERvA-OmniFold-s5p-recompute`, last session name `gbdt independent`). Written by the campaign session because
no recompute session was live (ListAgents 07:08Z–16:40Z); the campaign does not edit that branch.

**CITABLE FOR:** a defect in the recompute's calibration-product selection, located at its reviewed commit; the
frozen definition it departs from; its consequences once seed numbering has gaps (it now does); the correction and the
regression check the recompute lane is asked to make; the re-review requirement. **NOT CITABLE FOR:** any p-value,
decision or verification result; any change to production, the frozen evaluator or a frozen rule (none is made or
needed); how the recompute lane implements the fix (its own choice, under its own review).

## 1. The defect

At `1bfd8910` (the reviewed deployment target; `git diff 1bfd8910 8a581f69 -- nd-unfolding/` is empty), in
`nd-unfolding/s5p_recompute.py`:

- `evaluate` (line 789) sets `hi = base + B_final` and calls `load_ensemble(spec["calibration_glob"], base, hi)`.
- `load_ensemble` (lines 614–620) keeps only finished products whose seed lies in `[base, base + B_final)`, and lists
  the others as `outside`.
- This is the lane's declared reading **A13** ("every finished product … whose seed lies in [seed0, seed0 + final
  B)").

**The frozen definition** (amendment 7 `calibration.sequential_rule`: *"evaluates both claim p-values on the finished
products (partials excluded)"*) is every finished product of the null's glob, with no seed-range restriction. The
frozen production code implements exactly that:
- `s5p_joint.product_files` (line 135) keeps every glob match whose name has no `.partial`;
- `s5p_seqstop.py` sets `B = len(files)`;
- `s5p_joint.calibration_count` takes the final status's `B`, and the evaluator refuses unless
  `len(product_files) == B`.

Both modules are byte-identical to `4f5a613f`.

**Why it now matters.** A task killed at its 2.0 h limit loses its interrupted and never-started seeds, and the frozen
rule does not retry them. On 2026-09-29, 20 batch-0/P1 tasks were killed, and seed numbering now has gaps in every
lane: 1–7 seeds per batch (`RECORD-20260929-s5p-lost-seed-runtime-diagnostic.md`).

## 2. Consequences if uncorrected

Take a null that stops after n batches with L seeds lost. Its seeds span `[base, base + 200 n)` and the final
`B = 200 n − L`.

1. **The final ensemble drops L valid products.** These are the ones with seeds in `[base + B, base + 200 n)`. The
   recompute's k and B then differ from production's, the comparer reports a disagreement that is an artefact, and
   `count_matches_final_B` is False.
2. **The sequential re-evaluation misses its final look.** `verify_sequential` builds each look from the already
   restricted ensemble. The last look sees fewer than `B_final` products, pairs with no status file, and the stop
   verdict can be wrong.
3. **Power is judged against the wrong null ensemble.** `power_of_set` selects the power products correctly (no range),
   but it compares them with the restricted MnvTune and GENIE CV null ensembles.
4. **The gap list is truncated.** `missing_seeds_in_range` is computed only inside the truncated range.

The lane's own outputs (`count_matches_final_B`, `seeds_outside_final_range`) would expose the mismatch, so this would
show up as a disagreement, not as a false agreement.

Minor, related: the recompute excludes `.partial-` and production excludes `.partial`. Align them to production's rule.

## 3. Required correction (the lane implements it; the campaign does not)

- **The ensemble.** The calibration ensemble is every finished product of the null's glob, under production's partial
  rule, with no seed-range restriction. B is its count.
- **The comparison with the final status.** Compare the count with the final status's `B`. Report a difference as a
  count mismatch (production's evaluator would refuse in that case); never repair it.
- **The gap report.** Report missing seeds as a diagnostic over the seed span of the submitted batches,
  `[base, base + 200 × batches)`, separately from the ensemble.
- **Seeds outside any batch.** Report a product whose seed lies outside every submitted batch; do not silently drop it.
- **Revise A13** to the frozen definition, keeping the old reading as a withdrawn, dated entry.

## 4. Regression check to add

Use the lane's toy world in the production file formats. It needs a null with two batches (seeds `base … base + 399`)
in which:
- seeds `base + 5`, `base + 17` and `base + 203` have **no** product;
- seed `base + 17` has a `.partial-<pid>.npz` file;
- the final status has `B = 397` and `stop: true`.

The check must assert all of the following:
- 397 products are used, including seeds `base + 397 … base + 399`, and `count_matches_final_B` is True;
- each look's B equals the status file's B (200 − 2 = 198 before batch 1; 397 at the end) and pairs with it;
- the missing-seed report is exactly `{base + 5, base + 17, base + 203}`, and the partial is excluded;
- the k, B and p agree with the frozen `s5p_joint` on the same files.

Keep one control that fails on the current `1bfd8910` code: its ensemble has 394 products (seeds `base + 397 … 399`
dropped), and the check must go red on it. Also keep a power set whose null has a gap, so the power path is covered.

## 5. Re-review requirement

- **Review the changed evaluator and comparer independently before the final verification.** A fresh read-only review,
  as the lane's rounds 1–3 were, must cover the change and the regression check, and must name a new final reviewed
  commit.
- **Deploy only that commit** for the final verification. The pin to `1bfd8910` in the "Commits" list of
  `HANDOFF-20260928-s5p-recompute.md` is superseded by that commit once it is recorded.
- **Record the timing.** The correction is made after production outputs became visible: the five batch-0 looks,
  k = 0 at every null. It is a definitional alignment with the frozen text and changes no production rule, but it must
  be recorded with its actual timing.
- **Keep the other readings.** Re-deriving A13 must not change any other reading (A1–A12, A14); A6 and A8 stay as
  assessed.

## 6. Contact and state

- **Contact:** the campaign session is `gbdt worker [dfdda9]` from 2026-09-29T07:08Z. Reply with SendMessage.
- **Production state:** see `docs/orchestration/state/s5p/campaign-state.json` (`incidents`, `jobs`). It is not
  terminal; the final verification is due when the campaign reports terminal.
