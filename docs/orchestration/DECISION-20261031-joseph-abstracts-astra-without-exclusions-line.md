# DECISION 2026-10-31 (night, later) — Joseph: finalize astra's abstracts, without the generator-exclusions sentence

**Recorded by** the paper-tighten lane, as director.

**What led to it.** The gpt-6-astra consult proposed whole paper and note abstracts
(`state/2d-closeout/stageF/methods/secondary-results/astra-consult-abstracts-coverage-20261031/answer.txt` §2). They
went to Joseph beside the Sonnet referee's suggestions and the director's view. He first asked a question:

> Which abstracts should the lane finalize (it then runs its truth checks and brings you the final whole pair)?

Joseph's answer, verbatim:

> is it normal to say something like do not establish generator exclusions in the abstract for prd papers?

sha256 of the text plus a final newline begins `a7aa10122175b299`.

**The director answered from the repository's register study**
(`state/2d-closeout/stageF/methods/register-prd-study/REPORT.md`):
- of its twelve published reference abstracts, none states a limitation of the method (`:115-120`);
- each carries at most one scope, condition or status marker, and eight carry none (`:276-280`);
- its rewrite of an earlier abstract of ours moved "They are not physical exclusions" to the body (`:420-445`).

The body already states the point (`paper_body.tex:264` at `039596e09`), and the abstract's coverage sentence covers
the same caveat. The question was put again:

> Which abstracts should the lane finalize (it runs its truth checks and brings you the final whole pair)?

Joseph's answer, verbatim:

> astra's, minus exclusions (Recommended)

sha256 of the text plus a final newline begins `0b8d16cf4280d987`.

## What is decided

1. **The paper and note abstracts of PR #619 become astra's proposed abstracts** (`answer.txt` §2), with the
   sentence "These comparisons do not establish generator exclusions." removed from both. Its point stays in the body
   (`paper_body.tex:264`).
2. **What the abstracts keep:**
   - the run-period clause, without the 7.29 % number;
   - "predeclared" for the fake-data thresholds;
   - one coverage sentence, last: "The coverage of the reported uncertainty intervals has not been validated."
   <!-- absence-ok: quotes the approved abstract sentence; its sources are the 1B declaration and report -->
3. **The paper rewrite lane finalizes them.**
   - Every number goes through the values macros and the fact ledger, with the truth checks.
   - The lane confirms "predeclared" against `FD-DIRECTOR-RULINGS.md` §2 and the F0 report's time.
   - It runs the protections split's checks for an abstract.
   - Then the final whole pair comes back to Joseph for approval before #619 merges (A4).

## Not changed

- The body text, every number, the title and the protections. Nothing is submitted, deposited or tagged.
