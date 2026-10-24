# Round r16: the five passages the P1 raters still flagged (2026-10-23)

**Governed by** `DECISION-20261023-joseph-5d-targets-and-paper-round-2.md` ("another round for the paper"), under the
r15 standard. The writer's records are here: `outline.md`, `ledger.md`, `check_ledger.py`, `changes.md` and
`density.md`. The director committed this report from the writer's replies, the review and the pairwise result.

## What changed

All five targets stay in the paper. Each one either discloses a choice or carries a fact fixed by a decision. They
are rewritten in plain physics language:

| target | change |
|---|---|
| 1. The rerun pseudo-experiments | A rewording of Joseph's §5 disposition (`DECISION-20261005…` §5). "None" now names the calibration draws, the only ones compared with the observed statistic (`RECORD-20261006…` §2, k_rec = 0). |
| 2. "Descriptive … do not re-grade" | "The evaluations are descriptive. The decisions of Table IV … stand." The note keeps "do not re-grade", as DECISION-20261020 requires. |
| 3. The five-iteration rule | Reworded; the rule's values print in the note. |
| 4. The seed panels | Kept as a disclosure (commit `a6b9c705`; `sec:gbdt-model-dependence`). |
| 5. The budget extension | Kept as a disclosure: "after the observed p values had become visible" (DECISION-20261004 §3). The error-control sentence is supported by `sec:joint5d-frozen`. |

Other changes:
- the κ scan "probes that one direction";
- "The error control applies to the decisions, not separately to the point estimates";
- a non-sequitur "therefore" is dropped;
- one sentence is split.

No number, pointer, label or protected text changed. The note, primer and PET note print as before. r16 supersedes
r15 ledger rows G9, G10, G26, G27, C4, P73, P114, P124, P149, P223 and P224 (see `changes.md`).

## Review: ADOPT-AFTER-FIXES, all fixed

- Targets 1 and 5 were checked against their records and are true; neither is stronger than its record.
- Two wording fixes were made: "become visible", and a full stop in target 2.
- The records' "truth fix" label is corrected to "a rewording of the §5 disposition".
- **For Joseph:** the paper does not state that A2 also requires the losses to be independent of their outcomes. The
  note says this has not been shown. The omission predates r16, and the clause was not added.

## Blind pairwise comparison

**NEW wins 4 of 4, with no order flip.**

| | revision | blinded copy sha256 |
|---|---|---|
| OLD | `927f40bf` | `034bdabd…` |
| NEW | `6c4091be` | `3ef2703c…` |

- **Strengths:** sol2 gave 1 and 1; gemini gave 2 and 2.
- **What the raters cited against OLD:**
  - "re-grade the decisions";
  - "the rule's measure";
  - "carry no separate validity claim";
  - the non-sequitur "therefore".

**P1 (sol2): 3.0, 3.0, 3.0, unchanged.** The justifications cite:
- the post hoc rescoring of the earlier band. This text is bound by Table I and `check_sec4_receipts.py`.
- the budget-extension disclosure;
- the design-fixed-before-statistic sentence;
- "is being moved to the refined estimator". The wording comes from the decision, and the sentence goes away when
  RE-2 lands.

Several of the raters' suggested rewrites change facts, so none is adopted.

## Director's reading

- The pairwise margin is now thin: sol2 gave strength 1 in both orders.
- P1 has stayed at 3.0 through both rounds.
- What still holds the score down is bound by gates, by decisions, or by the RE-2 status sentence.
- Further model-scored rounds before RE-2 lands are unlikely to pay. The next step is the human read.
