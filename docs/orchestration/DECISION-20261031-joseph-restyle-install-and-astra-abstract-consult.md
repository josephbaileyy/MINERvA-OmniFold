# DECISION 2026-10-31 (night) — Joseph: install the restyled figures; an astra consult on the abstracts and coverage

**Recorded by** the paper-tighten lane, as director.

**What led to it.**
- **The abstracts.** Joseph asked how feasible validating coverage is
  (`DECISION-20261031-joseph-three-covariance-files-and-1b-diagnosis.md` item 3), and the director answered. The
  question went back to him with the Sonnet referee's four additions.
- **The figures.** Amendment 2's bound rerun passed (PR #624, `RUN-A2-REPORT.md`). Its eleven review sheets went to
  him for a third look.

> Given that coverage can't be validated in general (and 1B's best case is 'no undercoverage detected at two GENIE v3 truths'), approve the abstracts with the referee's four additions? The lane is checking the fake-data exceedance against the with-block covariance and will bring a plain sentence for the thresholds; you approve the final whole abstracts.

Joseph's answer, verbatim:

> can you ask an astra session with access to the repo what it would recommend in order to sound the same as other PRD papers but also not underreport or qualify too much? maybe it has some idea of how to resolve the coverage issue

sha256 of the text plus a final newline begins `22bdbe8c63b94127`.

> Restyle, third look: the A2 sheets (red circles for This work, blue step 'GENIE 2.12.6 + MINERvA Tune v1', black squares for Published, grey tension curves) are in ~/MINERvA-OmniFold-reads/fig-restyle-review-a2-20261031/. All checks passed (data bit-for-bit identical, names uniform, text 5.0-5.9 pt). OK to install into the note?

Joseph's answer, verbatim:

> Install them

sha256 of the text plus a final newline begins `56dadf9293ea89de`.

## What is decided

1. **The restyled figures are installed.** The paper rewrite lane runs the install round: Step 4 part 2, and the
   caption sites of `fig-restyle-20261031/AMENDMENT-2.md` §6.
   - The eleven PDFs come from `figs-a2/`.
   - The eleven `G` rows are re-pointed, with `DIGESTS.tsv`.
   - The note, primer and paper are rebuilt with every gate.
   - The 4.0 pt and raw-ASCII checks are re-run on the built PDFs.
2. **The abstracts wait for an independent consult.**
   - **The consult:** `gpt-6-astra` on codex-school, read-only, in a checkout detached at PR #619's head `039596e0`.
   - **What it is asked:** a diagnosis of both abstracts against the PRD register; whole proposed abstracts, with every
     number sourced; what PRD papers say about coverage; and any feasible way to resolve or reduce the coverage issue.
   - **What it is not shown:** the Sonnet referee's view, so that its read is independent.
   - **What follows:** it is committed as a record, then put to Joseph beside the Sonnet referee's and the director's
     recommendations. He approves the whole abstracts.

## Not changed

- PR #619's text, every number, and the 1B protocol. Nothing is submitted, deposited or tagged.
