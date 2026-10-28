# DECISION 2026-10-27 — Joseph: re-price F1 after its F1b STOP (option A, ceiling 2.5 node-h); run the second scope review now and the structural round r19 before the final draft

**Recorded by** the paper-tighten lane, as director.

**What led to it.**
- **F1.** `FD-F1-BINDING.md` (PR #429) priced F1 at 1.25 node-h, with a ceiling of 1.98.
  - F1a (job 60415571) completed in 6:17, and its gate said GO.
  - F1b (job 60417614) ended `OUT_OF_MEMORY` after 12:10. Batch MaxRSS was 499,490,432 K, the whole node, from 128 concurrent gevgen processes. Its contended time per event was about 3× the pilot's.
  - 0.3075 node-h is spent. The measurement session's receipts are on `fd/f1-report` at `183b31e4`.
  - The director put the re-pricing to Joseph, with option (A): re-pilot at production concurrency with the peak memory per process measured, then size F1b to at most 75 % of the node's memory. Expected total about 1.45–1.65 node-h, ceiling 2.5. The director declined option (C), halving the events, because it changes the bound design.
- **The paper.** A sol2 P1 re-score of #413 at `a55e2686` gave 3, 3, 3, against the published anchors' mean of 3.67.
  - The structure is not a measurement paper's. The 16-cell result is subsection V F. Table I, a findings table, sits in Sec. I, and none of the seven PRD measurement papers in `register-prd-study` has a table before Sec. 3.
  - The director recommended two changes of order:
    - run the second scope review (`DECISION-20261027-joseph-5d-integration-then-second-scope-review.md`) now, on the #413 draft, rather than after the merge;
    - run register round r19, a structural round, before the final draft.

Joseph's answers, verbatim, the options he selected. On F1:

> Approve (A), cap 2.5 (Recommended)

sha256 of the text plus a final newline begins `07c1d1d9128bdaa1`.

On the order of the paper work:

> Yes, both (Recommended)

sha256 of the text plus a final newline begins `2a32d5713613c806`.

## What is decided

1. **F1 continues under option (A),** through an amendment to `FD-F1-DECLARATION.md` and a re-binding.
   - **Before any new job:** the GENIE message "No Configuration available for genie::EventGeneratorListAssembler/Default" is explained, and each pilot's generator list and process mix is shown. If a tune ran with a list other than its own, that is a STOP back to the director.
   - **The re-pilot runs at production concurrency,** with the peak memory per process measured. The gate refuses any F1b plan above 75 % of the node's memory.
   - **The F1 ceiling is 2.5 node-h in total,** including the 0.3075 already spent. Every job stays under 12 h, on regular QOS, with no GPU and `--no-requeue`. A projection above the ceiling is a STOP.
   - The partial F1b output stays untouched as the STOP's evidence and is never read.
2. **The second independent scope review runs now, on the #413 draft.**
   - It is the review of `DECISION-20261027-joseph-5d-integration-then-second-scope-review.md`: gpt-6-astra, reasoning high, read-only, with no internal ranking.
   - It runs before the merge rather than after it.
3. **Register round r19, a structural round, runs before the final draft,** once the scope review has reported.
   - It runs under `DECISION-20261025-joseph-register-rounds-paper-rewrite.md`. It is round 3 of at most 4 for the paper. The method, adoption rule and stopping rule are unchanged.
   - Its aim is a measurement paper's order and the passages the raters quote. Restructuring and reordering are within that decision.
   - The paper rewrite lane runs it, and the director approves its outline before any writing.
4. **Step (c), the F1 and 3D sentences, continues in parallel.** The final draft (d) follows r19.

## Not changed

- F1 is a bias test, not a coverage test. Its grading, seeds and held-out group are as bound.
- The hybrid-null joint-test move is still only "seriously considered". The scope review informs it, and the move is Joseph's.
- Claims, KI-85, `\pubhold`, data-availability and release text, the abstracts' final wording and the title are Joseph's. Nothing is submitted, deposited or tagged.
