# DECISION 2026-10-28 — Joseph: decisions on the final draft (d): T1; the abstracts rewritten to typical form; independent reviewers choose the wording options and the flux band; F1's shorter paragraph; typical data release first

**Recorded by** the paper-tighten lane, as director.

**What led to it.**
- The paper rewrite lane assembled the final draft (d) as one decision packet,
  `state/2d-closeout/stageF/methods/fived16/FINAL-DRAFT.md` (#413 at `9457beab`), with built PDFs.
- The director checked it and put it to Joseph under `DECISION-20261027-joseph-5d-integration-then-second-scope-review.md`
  item 2.

Joseph's answer, verbatim:

> decisions title: I like T1, abstracts: I think its work considering rewriting the abstracts so they reflect typical lengths and also don't report metatext nor more qualifications/limitations than typical. How much compute would it take to address the coverge limitation again? Recall I have both perlmutter and ncsa delta compute hours. The wording alignment choices should be up to independent PRD reviewers for now. flux band: this should go to independent reviewers too. f1: I like the shorter alternative but again, how much compute would it take to address this limitation? data and release: doesn't hurt to release more than typical, but lets do what is typical for these types of papers first as a draft wording pairs and questions: take the options that are preferred by independent reviewers first

sha256 of the text plus a final newline begins `2eee907a56544916`.

## What is decided

1. **The title is T1:** "Simultaneous measurement of the ν_μ charged-current inclusive cross section on hydrocarbon in
   five observables from MINERvA open data".
2. **Both abstracts are rewritten to the typical form of the genre,** as drafts for Joseph:
   - typical length;
   - no metatext;
   - no more qualifications or limitations than comparable published abstracts carry.

   The guardrail still holds. A qualifier stays where omitting it would make a printed sentence false, so reducing
   limitations means removing sentences from the abstract, not weakening the ones that stay. No fact leaves both
   documents, so a limitation dropped from an abstract must still print in the body.
3. **The wording-alignment choices go to independent PRD reviewers** for now. That covers §3.4's three wordings of the
   coverage limitation.
4. **The flux band** (§4: replace the α = 0.1 sentence, or keep both) **goes to independent reviewers.**
5. **F1:** IV H takes the shorter alternative (PRD read r6, sol2 r2's form, 154 words).
6. **Data and release:** "do what is typical for these types of papers first as a draft". Releasing more than is
   typical may follow.
7. **The wording pairs and questions** (§7 and the other open options in the packet) take the options that independent
   reviewers prefer.
8. **Joseph asked what it would take to address the coverage limitation, and F1's.** The director answered with
   LIMITATION-PLAN's costing of 1B and 1B′. This decision grants no compute. A coverage test needs Joseph's go-ahead
   and a grant, since `DECISION-20261027-joseph-limitation-plan-f1-bias-test-and-flux-bootstrap.md` item 4 deferred it.

## Not changed

- The abstracts' final wording, the claims, KI-85, `\pubhold`, Data Availability and the release text stay Joseph's.
  Every item above returns to him as a draft before #413 merges.
- Nothing is submitted, deposited or tagged.
