# s5p (`OI-193`): owner ruling on A7, the κ = 3 "robust to the sub-fine residual" label (2026-09-29)

**CITABLE FOR:** the specification owner's ruling on ambiguity A7 of the Stage-6 recomputation, its timing, and how the
reported label is derived. **NOT CITABLE FOR:** any claim, decision or change of the primary claim rule, the stopping
rule, a terminal status or a production job (none changes).

## The ruling (Joseph, verbatim)

> For A7, I choose the full Holm rerun at κ = 3. For each hypothesis rejected by the primary κ = 2 procedure, report
> "robust to the sub-fine residual" only if it is also rejected by the κ = 3 procedure; otherwise report "not robust."
> Non-rejected hypotheses get "not applicable."
>
> This is report-only and does not change the primary claims, stopping rules or production jobs.

This is ruling R7, alternative (a), of `CLARIFICATION-20260928-s5p-recompute-A6-A8.md`. Alternative (b), the per-test
comparison at the rejecting step's threshold, is **preserved** as a non-adopted reading. The recomputation may compute
it as a labelled diagnostic, but it is not the reported label.

## Timing (actual)

- **Ruling received:** in the campaign session at about 2026-09-29T01:22Z.
- **Recorded:** at the commit that adds this file.
- **What existed then, measured at 01:23:55Z:**
  - Production had been running since 2026-09-28T16:11Z, and its calibration and power products were visible.
  - The only status files were the five B = 0 looks, which carry no statistic, p-value or decision.
  - `stage7/joint/` did not exist, so the evaluator had never run.
- So the ruling was made after production outputs became visible, but before any observed claim p-value, decision or
  robustness result had been computed by the campaign.
- It was made after the recomputation lane raised the ambiguity and after the campaign's clarification. The owner chose
  between the two readings as stated there, without any observed result.

## Implementation: the calculation is unchanged; only the reported label is new

**Unchanged: the statistical calculation, which is the frozen evaluator.**
- `nd-unfolding/s5p_joint.py` at `4f5a613f` is not modified.
- The robust claim p of each test is the largest p over the claim variants ∪ {F ± 3δ_M1}, keeping the ±2δ_M1 members
  ("retain"). This is an IMPLEMENTATION FACT (`s5p_joint.py:233, 252-260`), not ruled; see the correction below.
- `decisions_robust_kappa` = `holm_determined` over the ten robust claim p-values.
- The ruling fixes the procedure (a full Holm re-run at κ = 3) and the labels. It does not fix the variant set, which
  is open as A7-VS.

**Correction (2026-09-29T03:10Z).** The first version of this file said the frozen set was "exactly the ruled 'κ = 3
procedure'". That overstated the ruling.
- **What the ruling says:** Joseph's words choose "the full Holm rerun at κ = 3" and the labels. They name no variant
  set.
- **What the governing records say** (`4f5a613f`): amendment 7 says "at kappa = 3"; `m1_shift` and the design say
  "kappa_robust 3"; the pre-freeze tool says "3 M1 (the robustness variant)". None of them decides whether the ±2δ_M1
  members are kept.
- **Who raised it:** the recompute lane (`origin/s5p-parallel-recompute-20260928` at `78194f9b`) flagged it as
  **A7-VS: OPEN**.
- **What is needed:** an owner ruling before final verification.
  - **retain** (the frozen implementation): robust p = max over {c·S} ∪ {±2δ} ∪ {±3δ}. It is already
    `decisions_robust_kappa`, and `s5p_robust_labels.py` applies to it as written.
  - **replace**: robust p = max over {c·S} ∪ {±3δ}. `holm_determined` is re-run on those p's. They can be taken from the
    evaluator's stored per-variant leaves (`tests.<null>.variants.*` and `robustness_variants.*`, each with p, k and
    B), so no statistic is recomputed. This needs a small extension of the label step, not of `s5p_joint.py`.
- **Consequences under either choice:** report only. No primary claim, stop, status or job changes. The recompute lane
  reports that the label change between the two sets has no guaranteed direction (the campaign has not verified this).
  Until it is ruled, that lane reports any test on which the sets differ as UNRESOLVED, and its verdict as INCOMPLETE.
- **Timing:** this was raised after production outputs became visible, and before any observed claim p-value. At
  03:10Z the only status files were the five B = 0 looks.

**New: the output label, derived in a separate step.**
- The script is `nd-unfolding/s5p_robust_labels.py`, with tests in `tests/test_s5p_robust_labels.py`.
- It reads the evaluator's `joint-evaluate.json` and never modifies it. It writes its own file, which records the
  input's sha256, the ruling path and the frozen field verbatim.
- The label for each test is:
  - "robust to the sub-fine residual" if `decisions[t]` is 'rejected' and `decisions_robust_kappa[t]` is 'rejected';
  - "not robust" if `decisions[t]` is 'rejected' and `decisions_robust_kappa[t]` is anything else;
  - "not applicable" otherwise, i.e. `decisions[t]` is 'not rejected' or 'undetermined' (including a null not calibrated
    at B = 0).

**The change of output labels (documented separately, as required).** The frozen field
`robust_to_the_sub_fine_residual` stays in the evaluator output, unchanged, as a boolean for all ten tests: whether the
two decision labels are equal.
- **Primary rejections:** `true` corresponds to "robust to the sub-fine residual" and `false` to "not robust". The
  information is the same; only the wording changes.
- **Non-rejections:** the boolean has a value (for example `true` when both runs say 'not rejected'), but under the ruling
  it is not a flag. The reported label is "not applicable".
- **Reporting:** results and deliverables report the ruled label from the separate file, never the boolean.

**Output route:** `/pscratch/sd/j/josephrb/s5p-20260926/stage7/joint/robust-labels.json`, with a committed copy at
`docs/orchestration/state/s5p/stage7/joint/robust-labels.json`. It is produced by
`PYTHONPATH=nd-unfolding python3 nd-unfolding/s5p_robust_labels.py --evaluate <joint-evaluate.json> --out <route>` after
the evaluation.

## Preserved alternatives and open items

- **A7(b):** the per-test reading, kept as above.
- **A6:** union (the frozen code and the campaign's textual reading) vs the cross-product ruling R6.
- **A8:** the 99.5% look precision (the frozen code and text) vs the optional 95% reading R8.

A6 and A8 stay as recorded in the clarification, pending the independent reviewer's assessment from the governing
records. The owner has not ruled on either.
