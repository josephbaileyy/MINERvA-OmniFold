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
  was open as A7-VS until the owner ruled "replace" at about 04:33Z (see the A7-VS section below).

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

## A7-VS: owner ruling on the κ = 3 variant set (Joseph, verbatim)

> For A7-VS, I choose replacement: the κ = 3 robustness family retains the process-shift variants and replaces the M1
> ±2δ variants with ±3δ. Run the full Holm procedure on that family.
>
> Label each primary κ = 2 rejection "robust to the sub-fine residual" only if that hypothesis is also rejected in this
> κ = 3 rerun; otherwise "not robust." Primary non-rejections remain "not applicable."
>
> Record this as an explicit report-only clarification made now, with its actual timing—not as a recovered
> pre-production definition. Preserve the frozen boolean and the keep-both calculation as separately named diagnostics.
>
> Do not change primary p-values, primary decisions, stopping rules or production jobs.

**Status: an explicit report-only clarification made on 2026-09-29. It is NOT a recovered pre-production definition.**
The governing records at `4f5a613f` do not fix the set (see the correction above). The frozen code's keep-both set is
an implementation fact that no one ruled on.

**Timing (actual).**
- Received in the campaign session at about 2026-09-29T04:33Z; recorded at the commit that adds this section.
- At the time, production outputs were visible and only the five B = 0 looks existed. There was no observed claim
  p-value, and the evaluator had not run (last measured 04:14:55Z).

## The label step (current: `s5p-robust-labels/2`)

This supersedes the first version of the label step (`4a1d931c`, schema 1), which took the κ = 3 run to be the frozen
`decisions_robust_kappa`.

**What the script does.** `nd-unfolding/s5p_robust_labels.py`, tested by `tests/test_s5p_robust_labels.py`:
- It reads `joint-evaluate.json` and the design, and refuses if the output's `design_sha256` is not that design's.
- It writes a separate file and never modifies the evaluator output.
- **κ = 3 family (replace):** the process-shift variants c·S (`tests.<null>.variants` without the `m1±κ` members) plus
  F ± 3δ_M1 (`robustness_variants`). MnvTune has no M1, so its family is its c-variants. A null stopped at B = 0 gets
  p = 1 with k = B = 0.
- The robust claim p is the largest p over the family. `s5p_inference.holm_determined` is run on the ten values,
  giving the field `decisions_kappa3_replace`.
- **Labels:**
  - a primary rejection (`decisions[t]` = 'rejected') is "robust to the sub-fine residual" iff it is 'rejected' in
    `decisions_kappa3_replace`, else "not robust";
  - every other hypothesis is "not applicable".
- **Guard:** before the stored leaves are used, the primary claims and the keep-both robust claims are rebuilt from them.
  They must reproduce the evaluator's `decisions` and `decisions_robust_kappa` exactly, or the script refuses.
- **Diagnostics, never reported as the label:**
  - `diagnostics.frozen_boolean_robust_to_the_sub_fine_residual`, verbatim;
  - `diagnostics.keep_both`, the frozen claim variants ∪ F ± 3δ_M1, i.e. `decisions_robust_kappa`, with the labels it
    would give.

**What is unchanged: the statistical calculation.**
- `s5p_joint.py` (frozen `4f5a613f`) is not modified.
- Every per-variant p, k and B comes from the evaluator as written.
- The primary p-values and decisions (`decisions`) are unchanged, and so are the stopping rule and every job.

**What changes in the output (documented separately):**
1. **The reported robustness output becomes the label.** The frozen boolean says whether the two frozen runs give
   equal decision labels, for all ten tests. It stays in the evaluator output and in the diagnostics, but is not
   reported. For primary non-rejections the label is "not applicable" whatever the boolean says.
2. **The κ = 3 Holm run behind the label changes from keep-both to replace.** This is a new derived calculation in the
   label step: a Holm run over a different set of the SAME frozen per-variant p-values. It does not recompute any
   statistic.
   - The two can give different labels in either direction: removing a large κ = 2 leaf of another test changes the
     step-down order and thresholds.
   - A control test shows it: X is "not robust" under keep-both and "robust" under replace, because Y's k = 40 κ = 2
     leaf is dropped.
   - Where they differ, the reported label is the replace one, and the keep-both label stays in the diagnostics.

**Output route:** `/pscratch/sd/j/josephrb/s5p-20260926/stage7/joint/robust-labels.json`, with a committed copy at
`docs/orchestration/state/s5p/stage7/joint/robust-labels.json`. It is produced after the evaluation by:
`PYTHONPATH=nd-unfolding python3 nd-unfolding/s5p_robust_labels.py --evaluate <joint-evaluate.json> --design
docs/orchestration/state/s5p/prod/design.json --out <route>`

**Independent comparison.** The recompute lane owns its comparer (`origin/s5p-parallel-recompute-20260928`). The
campaign sends it this schema and the ruling, and does not edit that branch.

## Preserved alternatives and open items

- **A7(b):** the per-test reading, kept as above.
- **A6:** union (the frozen code and the campaign's textual reading) vs the cross-product ruling R6.
- **A8:** the 99.5% look precision (the frozen code and text) vs the optional 95% reading R8.

A6 and A8: the independent assessment (recompute lane `155d630a`) agrees that both are resolved by the frozen text
(union; the 99.5% look). The owner has not ruled on either. A7-VS is ruled above (replace). Keep-both stays a named
diagnostic.
