# s5p (`OI-193`): owner decisions 2026-10-05 — comparer extension before recording; report-only lost-seed recovery

**CITABLE FOR:**
- the owner's two decisions after the independent recompute's final report, as the questions and the selected
  answers;
- what each decision authorizes and what it does not.

**NOT CITABLE FOR:**
- the joint result, which is still unrecorded;
- any change to a frozen claim, statistic, stopping rule, terminal status, seed, batch, estimator setting or primary
  decision;
- any submission before the reviewed procedure in §2 exists.

**Context:** `REPORT-20261005-s5p-recompute-final-verification.md` (branch `s5p-parallel-recompute-20260928`,
`80edc4d6`) found 0 discrepancies in 712 of 712 compared rows. Its reviewed comparer returned INCOMPLETE, NOT AGREE,
because of 20 layout items and 713 unmapped leaves. `RECORD-20261005-s5p-terminal-evaluation-pending-verification.md`
§3 gives the missing-seed sensitivity: every test reads "can change", and no rejection is certified.

## 1. Decision 1: verification before recording (Joseph, 2026-10-05, campaign session)

> **Question:** "The independent recompute found 0 discrepancies, but its reviewed comparer says INCOMPLETE (not
> AGREE) because 20 items are in a different layout and 713 fields aren't mapped. Does that satisfy amendment 7's
> independent-recomputation requirement for recording the joint result?"
>
> **Selected:** "Extend, review, then record (Recommended)". The recompute lane writes a comparer mapping extension,
> which gets its own bounded independent review; compare is rerun and the result recorded only on AGREE.

**Consequence:**
- The joint result is recorded only after the extended, independently reviewed comparer returns AGREE on the
  unchanged production outputs (the sha256 in the pending record).
- The extension maps fields; it changes no recompute arithmetic and no production output.
- A disagreement is resolved by the recompute lane's handoff routes, never by changing a reading to match.

## 2. Decision 2: missing-seed sensitivity (Joseph, 2026-10-05, campaign session)

> **Question:** "Every rejection reads 'can change' under the missing-seed sensitivity: if all the time-limit-killed
> draws had exceeded the observed statistic, nothing would be rejected, and no rejection is certified. How should
> this enter the claims?"
>
> **Selected:** "Recover lost seeds (Recommended)". Rerun the 277 lost seeds as a report-only resolution, from the
> verification/repair reserve: about 8–12 CPU node-hours and half a day to a day, after first confirming on about 10
> completed seeds that a rerun reproduces the same statistic. Primary decisions unchanged; if the recovered draws are
> below the observed statistic, the rejections become certified. Needs a reviewed procedure before any submission.

**What it authorizes:**
- A report-only recovery of exactly the lost seeds: 224 calibration (111 interrupted, 113 never started) and 53 power,
  as classified in `seed-states.json` and agreed by the recompute lane.
- **Seeds and settings:** each seed rerun with its frozen table's arguments. Only `--out` changes, to a separate
  recovery directory, plus the task packing (seeds per task).
- **Budget:** CPU from the `verification_repair` stage (68.287 node-h, untouched), with an estimate of about 8–12
  billed node-h (measured mean 696 s per seed).

**What it does not authorize:**
- **Changing the frozen products.** Recovered products never enter the production directories or the frozen
  calibration globs, so the frozen evaluator's B, p-values and primary decisions are unchanged.
- **Rescuing anything.** The recovered outcomes are reported as the resolution of the missing-seed sensitivity, never
  as a revised primary decision.
- **Any submission before both preconditions are met:**
  1. a written procedure has had an independent review;
  2. a determinism check on about 10 already-completed seeds shows that a rerun reproduces the original statistic,
     under a criterion fixed in the procedure before the check runs.

  If determinism fails, recovery stops and the owner is told; the alternative wording then returns to the owner.
- **More hours.** Further increases require the owner's decision.

## 3. Unchanged

- Budget revision 7 (production 234.647, verification/repair 68.287, ceiling 376.52) and the concurrency cap.
- The outstanding A6 (R6) and A8 (R8) rulings, which are not ruled here.
- CHECKLIST-20261001 §4: the measurement branch is NOT ADMITTED, there is no new reportable uncertainty, and
  publication readiness is NOT READY.

## 4. Addendum: two follow-up rulings for the comparer extension (Joseph, 2026-10-05, campaign session)

The recompute lane, while implementing decision 1, raised an unruled ambiguity (its A16) and a scope question. The
campaign checked the A16 premise from production's own output: in `joint-evaluate.json`, `median_shift_in_null_sd`
equals (shifted null-T median − unshifted null-T median) / the unshifted null-T SD (population, ddof 0), with residual
0 on 36 of 36 leaves.

> **Question:** "Two descriptive fields (82 leaves) have no formula in the frozen text, and the two codes read them
> differently: production uses population SD (ddof 0) and 'shift of medians / SD'; the recompute uses sample SD and
> 'median of per-draw shifts / SD'. They feed no p-value, decision or label. How should the verification treat
> them?"
>
> **Selected:** "Rule a clarification (Recommended)". This is a report-only clarification, like A7-VS: the descriptive
> null-T SD is ddof 0, and median_shift_in_null_sd is the shift of medians over it. The comparer checks against that
> reading, and the recompute still reports its own reading alongside.

> **Question:** "About 100 of the 713 unmapped leaves are quantities the recompute never output (per-variant null-T
> medians/SDs, CP intervals, implied size, classical Holm-adjusted p). May the extension add these as new recompute
> OUTPUT fields, with no existing number changing and the reviewer checking byte-identity of every existing field?"
>
> **Selected:** "Allow new output fields (Recommended)". The recompute computes and emits them with its own code;
> every existing field stays byte-identical to 0142a228, which the reviewer checks.

**Effect:**
- The A16 clarification defines two descriptive quantities that the frozen text left without a formula. It feeds no
  p-value, decision, label or stopping rule, and changes no production output.
- The recompute's own reading is still reported as a labelled alternative.
