# DECISION 2026-10-30 — Joseph: r22's protected gaps: sol2's ten allowed; gemini's history allowed, the rest to an OpenAI review

**Recorded by** the paper-tighten lane, as director.

**What led to it.** r22 Step 1's report (PR #523) lists 84 gaps that would change protected text
([`state/2d-closeout/stageF/methods/r22/PROTECTED-CHOICES.md`](state/2d-closeout/stageF/methods/r22/PROTECTED-CHOICES.md)).
Ten are sol2's and 74 are gemini's. The director asked two questions.

> sol2 (our P1 rater) named 10 gaps that touch protected text. They split the long abstract sentences (no fact dropped), reword the Data Availability package sentence (access limits kept), and fold the note's run history into direct statements (disclosures kept, details moved to the ledger). Allow them?

Joseph's answer, verbatim:

> Allow all 10 (Recommended)

sha256 of the text plus a final newline begins `db06cb99103de2d8`.

> gemini named 74 protected gaps. Most would reframe or remove limitations and qualifiers (19 sentence-truth qualifiers, 3 claims, ~20 honesty disclosures) or drop run history from both documents (35). How should they be handled?

Joseph's answer, verbatim, typed as his own:

> get a openai model to review these, but allow history for sure at least

sha256 of the text plus a final newline begins `f9aca8b1d428a193`.

## What is decided

1. **sol2's ten protected gaps are allowed:** paper-s-09 (A1), B01-s-04, B01-s-10 and paper-s-06 (A4), and B02-s-01,
   B02-s-02, B03-s-01, B06-s-04, B09-s-01 and B15-s-02 (B2).
   - The option offered read: "Each still passes the truth guardrail and the fact ledger. The abstract and Data
     Availability edits come to you as before/after pairs before adoption."
   - So the abstract and Data Availability edits come to Joseph as pinned before/after pairs before they are adopted.
2. **gemini's run-history gaps are allowed** where the internal ledger keeps the fact (#521, #522). That means the 35 in
   group B2, each with its ledger home named and probed. A B2 gap that would drop a limitation, disclosure, qualifier or
   reported number from both documents is not history, and goes to item 3.
3. **gemini's other protected gaps go to an independent OpenAI review.**
   - The model runs on an allowed account (codex-school2, falling back to codex-school), read-only, with no history of
     the text.
   - For each gap it gets the quoted sentence, gemini's change, the protection's text and the classifiers' reasons.
   - For each, it recommends ALLOW or KEEP, with a one-sentence reason, judged on two questions: does the change bring
     the text closer to the register of published PRD papers, and would it make any sentence false or withhold from
     readers something they need to judge the result.
   - Its recommendations come to Joseph with the director's view. Nothing in this group changes before he answers.

## Not changed

- The truth guardrail and every claim and number. Nothing is submitted, deposited or tagged.
