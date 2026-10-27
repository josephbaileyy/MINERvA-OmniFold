# DECISION 2026-10-27 — Joseph: integrate the 5D result first, then a second independent scope review

**Recorded by** the paper-tighten lane, as director.

**What led to it.**
- The independent gpt-6-astra consult (`state/2d-closeout/stageF/methods/secondary-results/astra-consult-20261027/REPORT.md`,
  PR #407) recommended moving the paper's calibrated hybrid-null joint-test programme (§VII B–E, Table IV) to the note,
  with its abstract headline.
- The director reported it to Joseph. The abstract, Table I and Sec. I are framed around that programme.

Joseph's answer, verbatim:

> I think that recommendation is one to seriously consider, maybe we try another independent review once the 5d integration is done

sha256 of the text plus a final newline begins `77d0cc6e2dc38c8d`.

## What is decided

1. **The recommendation is seriously considered, not adopted.** Nothing moves yet.
2. **The 5D result is integrated into the paper and the note first.** The scope is:
   - the 16-cell result and its reported covariance;
   - the fake-data study;
   - the generator comparison, presented per `DECISION-20261026-joseph-5d-generator-comparison-presentation.md` and
     `DECISION-20261027-joseph-chi2-table-format.md`;
   - the F0 limitation, from `state/2d-closeout/stageF/methods/5d-fd-presentation/DRAFT.md`.

   **How it runs:**
   - The paper rewrite lane drafts it, after the note consolidation PR.
   - Every number comes from a committed readout, and agy checks every passage.
   - The printed wording comes to Joseph before it merges, because the 5D S1 integration and its wording are his.
3. **After the integration, a second independent scope review runs** under the first's rules:
   - an allowed account;
   - read-only;
   - only the integrated paper, the note's front matter and table of contents, and no internal ranking or
     recommendation.

   Its model is the one Joseph names, or gpt-6-astra high again by default. Its advice comes to Joseph with the first's.
4. **The paper's secondary-results decision follows** the second review.

## Not changed

- Claims, KI-85, `\pubhold`, data-availability and release text are Joseph's. Nothing is submitted, deposited or
  tagged.
