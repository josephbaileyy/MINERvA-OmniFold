# The paper's structure batch and the abstract: meaning and PRD reads (2026-11-12)

**What was read:**
- `pairs.txt`: 27 OLD/NEW paragraph pairs of paper_body.tex. OLD is journal-editor's 09ee8a25 and NEW is the working
  tree before the read's fixes. Comment lines are stripped.
- `abstract-pairs.txt`: four rendered abstract cases, before and after. RESPONSE.md section G, rows St1, Gs1–Gs10, G-rows
  and Stp, lists what the batch does.

Both readers were independent general-purpose subagents, read-only.

## The abstract (St1)

- **Meaning read** (MINOR), four DEFECTs, all fixed:
  - the shape clause now names the published shape ("but differs from the published shape more than a binned
    unfolding of the same inputs does");
  - "at both" became "at both truths";
  - "It continued/ran" became "The test continued/ran";
  - "The estimator" became "The five-observable estimator's results".
- **Notes taken:** "test" restored as the verb; the changes' referent given ("Under controlled truth changes … opposite
  to them"); the pending-test sentence split in two.
- **Result:** every live case is at most 249 words (check_round's abstract gate), no rendered case has a semicolon, and
  the worst case has 20.2 words per sentence.

## The body's structure batch

**First pass:** 10 OK, 6 NOTE, 11 DEFECT. All eleven were fixed:
- two comment lines had swallowed the sentences after them, so §6.2's restricted-test scope and the over-coverage
  sentence did not print. They are back on their own lines;
- the central value's rationale was restored;
- $C_{\mathrm{total}}=C_{\mathrm{e}}+C_{\mathrm{model}}$ is now stated unambiguously;
- the run-period interval's orientation caveat was kept in the pointer sentence;
- "The two-dimensional result's integrated cross section" replaced an ambiguous "Its";
- "Removing the 1G–1M group" is named, and the ± is called bootstrap noise;
- the Fig. 3 caption now matches the regenerated small multiples. The reader had seen the stale installed PNG, and the
  derivation is in S4.4;
- "retained fractions" replaced "projections";
- tab:stability gained the joint-cell row;
- a sentence before the B0 span keeps "the training-seed block" on the five-observable block;
- "cannot produce the pattern" was restored.

**Confirmation pass:** 12 OK, 2 DEFECT, both fixed:
- $C_{\mathrm{e}}$ now includes "its training-seed block", so B0's pointer has a five-observable target, as the
  Supplement's group table states;
- "By the per-cell flag rule applied the other way".

The PRD read for flow follows the sentence pass.
