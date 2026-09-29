# s5p (`OI-193`): owner ruling on A7-VS, the κ = 3 robustness family (2026-09-29) — a report-only clarification

**CITABLE FOR:** the specification owner's choice of the κ = 3 variant family used for the "robust to the
sub-fine residual" report, its actual timing, and how the recomputation and the comparison implement it.
**NOT CITABLE FOR:**
- a pre-production definition: this is **not** recovered from the frozen records, which do not fix the family
  (`HANDOFF-20260928-s5p-recompute.md` §3.2);
- any change to a primary p-value, a primary decision, the stopping rule, a status file or a production job. None
  changes.

## The ruling (Joseph, verbatim, received in the recomputation lane's session)

> For A7-VS, I choose replacement: the κ = 3 robustness family retains the process-shift variants and replaces the M1
> ±2δ variants with ±3δ. Run the full Holm procedure on that family.
>
> Label each primary κ = 2 rejection "robust to the sub-fine residual" only if that hypothesis is also rejected in this
> κ = 3 rerun; otherwise "not robust." Primary non-rejections remain "not applicable."
>
> Record this as an explicit report-only clarification made now, with its actual timing—not as a recovered
> pre-production definition. Preserve the frozen boolean and the keep-both calculation as separately named diagnostics.
>
> Do not change primary p-values, primary decisions, stopping rules or production jobs. Update the production labeler
> and independent comparison consistently, with tests and committed provenance.

## Timing (actual)

- **Received:** in this session, immediately before `2026-09-29T04:33:56Z`, the local clock of the first command
  run after it.
- **Measured at 2026-09-29T04:33:57Z** (cluster clock):
  - `runs/prod/status/` held only the five `-B0.json` looks, which carry no statistic, p-value or decision.
  - `stage7/joint/` did not exist, so neither the production evaluator nor the labeler had run.
- This lane has inspected **no observed p-value**. Its batch-0 smoke outputs contain p-values at B = 27–47, and
  those fields have never been opened.
- **Sequence:**
  1. The recomputation raised A7 (2026-09-28).
  2. The owner ruled A7 (full Holm re-run, labels; `RULING-20260929-s5p-A7-robustness-flag.md`, ~01:22Z).
  3. The recomputation flagged the variant family as open (A7-VS, commit `78194f9b`).
  4. This ruling closes it.
- It was made after production outputs became visible and before any observed claim p-value, decision or
  robustness result existed.

## The ruled family and labels

- **κ = 3 robustness family, per test:** the process-shift variants {c·S : c ∈ 0, ½, 1} ∪ {F + 3δ_M1, F − 3δ_M1}.
  The ±2δ_M1 claim variants are **replaced**, not kept. MnvTune has no M1 variant, so its family is its
  process-shift variants and its robust claim equals its claim.
- **Robust claim:** the largest p (equivalently k) over that family, at the null's B.
- **Re-run:** `holm_determined` (with determinacy) over the ten robust claims.
- **Label:** a primary (κ = 2) rejection is "robust to the sub-fine residual" iff it is also rejected in this
  re-run, otherwise "not robust". Every primary non-rejection ('not rejected', 'undetermined', and a null not
  calibrated at B = 0) is "not applicable".

## Preserved, separately named diagnostics

| diagnostic | what it is | where |
|---|---|---|
| keep-both family | claim variants ∪ F ± 3δ_M1 (±2δ and ±3δ both kept), its Holm re-run and labels. This is the frozen evaluator's `decisions_robust_kappa` as the campaign reports the frozen code. | recompute `family.keep_both_kappa3_diagnostic` |
| frozen boolean | `robust_to_the_sub_fine_residual`: equal decision labels in the primary and the keep-both re-run, for all ten tests, as the frozen evaluator writes it (unchanged) | production `joint-evaluate.json`; recompute `family.frozen_boolean_equivalent_diagnostic` |
| A7(b) | the per-test reading (non-adopted) | recompute `family.kappa3.<set>.A7b_per_test_robust_diagnostic` |

## Implementation

- **Recomputation** (`nd-unfolding/s5p_recompute.py`, branch `s5p-parallel-recompute-20260928`):
  `family.robust_labels` and `family.holm_at_kappa_robust` are the ruled family.
  `family.kappa3.tests_where_the_sets_differ` lists the tests on which the ruled and keep-both labels differ,
  measured, not assumed.
- **Comparison** (`nd-unfolding/s5p_recompute_compare.py`):
  - `robust-labels.json` `labels` is compared with the ruled labels.
  - The frozen `decisions_robust_kappa` and `robust_to_the_sub_fine_residual` are compared with the keep-both and
    frozen-boolean diagnostics.
  - The labeler's other fields must be mapped or documented as excluded; otherwise the verdict is INCOMPLETE.
- **Production labeler** (`nd-unfolding/s5p_robust_labels.py`, owned by the campaign): **updated by the campaign,
  not by this lane.**
  - Commit `67eadf25`, verified an ancestor of origin/main `9dd32efe`; file sha256 prefix `e08b76083b7abd0a`.
  - Output schema `s5p-robust-labels/2`, per the campaign's description and its record
    `RULING-20260929-s5p-A7-robustness-flag.md` §"A7-VS":
    - `labels` and `decisions_kappa3_replace`, the ruled family;
    - `family_members`;
    - `diagnostics.frozen_boolean_robust_to_the_sub_fine_residual` and `diagnostics.keep_both.{family, labels}`;
    - provenance.
  - The campaign's record quotes the same ruling, omitting its final sentence (the request to update the labeler
    and the comparison).
  - This lane did not read the labeler's code. The comparer maps the fields as described; any field it cannot map
    stays unresolved.
  - The two implementations are checked against each other by the final comparison.
- **Two records of one ruling.** The campaign recorded it on origin/main (the section above); this file records it
  on the recomputation branch, where it was received. Both give ~04:33Z and "report-only, not a recovered
  pre-production definition".
