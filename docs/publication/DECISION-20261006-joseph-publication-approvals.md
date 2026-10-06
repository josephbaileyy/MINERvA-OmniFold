# Joseph's approvals of the publication decision packet (2026-10-06)

**CITABLE FOR:** what Joseph approved, deferred and clarified in response to
`PACKET-20261005-publication-decision.md` §7, and what each item authorizes the publication lane to do.
**NOT CITABLE FOR:** any physics result. It also authorizes no public deposit, release tag, submission, external
message or additional scientific work beyond W1 and W2 as specified.

**Source:** Joseph's own message to the publication lane (session `pub`), received 2026-10-06 (the lane read
`origin/main` `391b666a` at 04:05Z). It answers packet §7 at branch head `cb65c4e4`. It is transcribed verbatim
below.

## Verbatim

> I approve items 1, 2, 3, 4, and 6. Defer item 5, with these clarifications:
>
> 1. Scope and journal: Proceed with the specialist-article scope, using PRD as the working target. Also assess PRX
> briefly against its scientific importance criteria and include a recommendation when the manuscript is ready. Do
> not expand the campaign solely to pursue a journal.
>
> Completion of the separate full measurement uncertainty product is not a prerequisite for this article. This
> modifies the September 1 prerequisite for this article only. Preserve the measurement branch’s NOT ADMITTED
> state, s5p’s recorded NOT READY status, and every artifact grade and exception condition. Assess this article’s
> readiness separately.
>
> 2. Hold and parallel work: Keep the numerical headline on hold until the remaining recovery, independent
> cross-check, my disposition, Stage-7 wording, and coverage-record dependencies are satisfied.
>
> This hold applies to this article’s headline, not to other sessions. PET and other work may continue under their
> existing authorizations and budgets. Keep publication work in its own branch and isolated worktree; do not freeze
> main or modify another session’s worktree. Coordinate shared-source changes with their owners. PET remains
> diagnostic and method-development.
>
> 3. W1: Approved as specified: existing products only, report-only, at most 2 CPU core-hours, after the required
> dependencies. Preserve its narrow comparison with matched coarse projections and its stopping rule.
>
> 4. W2: Accept ±4% solely as the labelled exploratory sensitivity, not as a validated uncertainty prescription.
> Approve W2a, including independent review and costing, within 1 CPU node-hour.
>
> To avoid another routine approval, W2b may proceed automatically if independent review clears the implementation
> and measured costing shows that W2a plus W2b fit within the combined 8 CPU node-hour ceiling. This replaces the
> separate W2b approval requirement. Apply the specified control and stopping rules. A failed gate stops the study;
> it does not authorize a larger budget or additional variations.
>
> 5. Collaborator question: Defer sending it.
>
> 6. Manuscript work: Proceed with drafting, figures, release preparation, builds, and corresponding source
> synchronization on coordinated branches. Resolve routine choices autonomously, consume the existing workers’
> committed handoffs, and batch material questions into one recommendation with exact proposed wording.
>
> Bring me the recovery interpretation when my scientific disposition is needed, then the finished submission
> package. Public deposit, release tagging, submission, and any additional scientific work remain separately
> authorized.

## What each item binds (the lane's reading; the verbatim text governs)

| item | authorizes | does not authorize |
|---|---|---|
| 1 | A PRD-class article as the working target. The full measurement-uncertainty product is no longer a prerequisite **for this article only**. A brief PRX importance assessment comes with the finished manuscript. | Expanding any campaign to pursue a journal. Any change to NOT ADMITTED, NOT READY, or any grade or exception. |
| 2 | The numerical headline stays on hold until D2 (recovery and cross-check), D3 (Joseph's disposition), D4 (Stage-7 wording) and D5 (coverage record) are satisfied. | Holding other sessions, freezing main, or touching another session's worktree. |
| 3 | W1 as specified in packet §6: existing products, report-only, ≤ 2 CPU core-hours, run after D1 and D2 with its criterion applied after D3. | Any other projection or comparison. |
| 4 | ±4% as a **labelled exploratory sensitivity**, not a validated uncertainty prescription. W2a (code, independent review, one-playlist costing) within ≤ 1 CPU node-hour. **W2b proceeds automatically** if the review clears the implementation **and** the measured costing shows W2a + W2b ≤ 8 CPU node-hours. Packet §6's control and stopping rules apply, and W2b runs after D2. | A larger budget, another δ, or any additional variation. A failed gate stops the study. |
| 5 | — (deferred) | Sending the collaborator question. |
| 6 | Drafting, figures, release preparation, builds, and source synchronization on coordinated branches. Routine choices are the lane's. Material questions are batched into one recommendation. | Public deposit, release tag, submission, additional scientific work. |

**Next deliverables owed to Joseph:**
- the recovery interpretation, when his D3 disposition is needed;
- the finished submission package, including the PRX recommendation.
