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

## Addendum, 2026-10-06: KI-84 (VL170) adoption, confirmed in this session

A peer session (`reviewer`, Joseph's personal session) relayed that Joseph had decided to adopt VL170, the rebuilt
2D statistical band, as the quoted 2D statistical band. The publication lane asked Joseph directly in this session.
The question, verbatim:

> "Your personal session relays that you want VL170, the rebuilt 2D statistical band, adopted as the quoted band,
> with the change carried downstream. Do you confirm, and who should do the work?"

**Joseph's answer (option selected):** "Adopt; 2D lane rebuilds (Recommended)".

The selected option's text, verbatim: "Confirm adoption. The 2D lane (which built VL170) records VL170 ADOPTED /
VL162 superseded, rebuilds the 6.87% rollup, the χ² and the figures, and updates the note appendices with the note
owners. The publication lane updates only the article's 2D paragraph, once the rollup and the VL169-toy rescoring
are committed."

**Binds:**
- the publication lane changes only the article's 2D-uncertainty paragraph, and only after the 2D lane's rebuilt
  rollup and its descriptive VL169-toy rescoring are committed;
- the ledger, rollup, χ², figures and note-appendix updates are the 2D lane's.

## Addendum, 2026-10-06: Fig. 2 scope without the response-mismatch closure (paper-wide R10(b)), asked in this session

The question, verbatim:

> "The article's joint (E_avail, W) central-value statement (Fig. 2) has no response-mismatch closure, which has never
> been run (paper-wide row R10b). As now written it is descriptive only, has no significance, states that no closure
> was run, names the region of largest regularization bias, and is out of the abstract. May it stand in the article
> without the closure?"

**Joseph's answer (option selected):** "Stands as written (Recommended)".

The option's text: "Record: 'The descriptive (E_avail,W) statement and Fig. 2 stand in the article without the
response-mismatch closure, as written at f5787b32: descriptive, no significance, the absent closure and the
largest-bias region stated, not in the abstract.'"

**Binds:** the article's Fig. 2 statement as written at `f5787b32`. Any strengthening (a significance, a
localization claim, or the statement in the abstract) would need the closure or a new decision.

## Addendum, 2026-10-06: package inputs 1 and 2 approved (this session, Joseph's own words)

> "okay I agree with the AI use and author details but I want to work on pushing everything to main and doing the
> reorg plan before doing another pass over the paper"

**Binds:**
- **The AI-use disclosure:** the text proposed in `docs/publication/submission/AI-DISCLOSURE-PROPOSED.md` is
  approved, with placement in the Acknowledgments and a pointer from the method section, as proposed.
- **The author details:** approved as currently in `main_paper.tex`: Joseph Bailey (Stanford Physics) and Benjamin
  Nachman (Stanford Particle Physics and Astrophysics; SLAC). ORCIDs and funding were not supplied.
- **Sequencing (Joseph):** the main push and the reorganization come first. The disclosure goes into the article in
  the next paper pass, not before.

Package inputs 3–6 (coauthor review, deposit, tag and submission, cover-letter specifics) remain open.
