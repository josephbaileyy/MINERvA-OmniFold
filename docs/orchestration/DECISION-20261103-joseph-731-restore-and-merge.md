# DECISION 2026-11-03 — Joseph: the targeted round (#731) restores two statements, then merges

**Recorded by** the paper-tighten lane, as director.

## What led to it

**The round.** #731 is the paper lane's targeted round under `DECISION-20261103-joseph-retire-density-gate.md`
item 3, at head `b9849126`. Its records are in `state/2d-closeout/stageF/methods/targeted-round-paper-20261103/`.
- It tightened six over-qualified passages (T1–T6) and moved three sections whole to the note (T7–T9).
- The ledger has 9 rows and 72 probes, with 0 failures. No fact left both the paper and the note.
- The paper went from 12 to 11 pages.

**The PRD-referee read (Gemini)** of the round's printed diff goes beside the REPORT in #731 as
`PRD-REVIEW-GEMINI-{PROMPT,ANSWER}.txt`.
- It calls the text "considerably tighter" and approves the three moves.
- It asks for two restorations:
  - the run-period block's 68% interval on the ratio of its true to its estimated size, since "poorly determined"
    alone "hides essential quantitative information";
  - an explicit statement that no finite-ensemble correction is applied.
- Both reverse the earlier read (`rp9-reprice-97e30dda/PRD-REVIEW-RP9-GEMINI-ANSWER.txt`), which had listed them as
  over-qualification.

## Joseph's answer, verbatim

Asked how the targeted round should proceed:

> Restore both, then merge (Recommended)

sha256 of the text plus a final newline begins `f9f48208d3755d05`.

The option as put to him: put the run-period block's 0.73–2.56 interval and the 'no finite-ensemble correction'
clause back in the paper; keep every other change; merge once the lane's checks pass, then re-sync Overleaf.

## What is decided

1. **The paper lane revises #731.**
   - The run-period block prints "poorly determined" with its 68% interval (`pl-sigratio-lo`–`pl-sigratio-hi`).
   - The paper states that no finite-ensemble correction is applied.
   - Every other change of `b9849126` stays.
   - The REPORT records both restorations, before and after.
2. **#731 is merged** through the CI-gated merge once the lane's checks pass: the ledger, the receipts check, values,
   and local CI. The Overleaf standalone is then re-synced under the sync record's procedure.
3. **The density re-measure** at the merged head is informational, under the retired gate.

Nothing is submitted, deposited or tagged.
