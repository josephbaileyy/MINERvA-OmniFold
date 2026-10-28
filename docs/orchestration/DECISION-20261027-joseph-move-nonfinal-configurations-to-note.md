# DECISION 2026-10-27 — Joseph: the paper presents only the final estimator configurations; the non-final ones move to the note

**Recorded by** the paper-tighten lane, as director.

**What led to it.** During the 5D integration (draft PR #413), Joseph asked:

> Is there a reason that we still need (a) in the actual paper and not in just the note? Or other configurations too for that matter? I think it would be a lot easier to explain the situation that way right?

sha256 of the text plus a final newline begins `208fdab3cdb11927`.

The director answered:
- the final configurations are (f) for the 2D result and (e) for the 3D and 4D central values and the sixteen-cell 5D
  result;
- configuration (a), the purity-subtraction variant, carries the earlier five-observable central value and its
  covariance, the studies built on it, and the purity-against-negative-weight comparison;
- the exact-split cross-check and the other variants mostly support the 2D learner-dependence discussion;
- presenting only the final method is PRD practice, and most of the sentences the integration had to scope concern
  configuration (a).

He then asked the paper rewrite lane for a read-only inventory of the paper by configuration.

Joseph's answer, verbatim:

> okay yes lets do the move for the non final configurations

sha256 of the text plus a final newline begins `642d9edb8997aac4`.

## What is decided

1. **The paper presents the final configurations only:**
   - (f) for the 2D result;
   - (e) for the 3D and 4D central values and for the sixteen-cell 5D result.
2. **Every non-final configuration moves to the note,** with the results, tables, figures and caveats that rest on it.
   That covers (a)–(d), the exact-split cross-check and any other variant.
   - The paper keeps a one-line pointer where a reader needs one.
   - No fact leaves both documents. The note already prints most of this material.
3. **A methods finding measured with a non-final configuration may stay in the paper** where the inventory shows that
   the paper's argument needs it, for example the purity-against-negative-weight background result. It is then
   described in words, for example "with purity-based subtraction", not by a configuration letter.
   - The finding keeps its scope and every qualifier it needs to stay true.
4. **The order of work:**
   - the read-only inventory;
   - an outline of the move, to the director, before any edit;
   - the move, as further commits on the 5D integration branch (draft PR #413). Many of that PR's scoped sentences then
     fall away with their product;
   - the independent PRD-language review of the changed text, under
     `DECISION-20261027-joseph-prd-review-route-push-and-public-github.md`;
   - one final draft to Joseph;
   - the second independent scope review (`DECISION-20261027-joseph-5d-integration-then-second-scope-review.md`).
5. **The abstract and Table I** follow the move. They name methods in words, not configuration labels.

## Not changed

- The hybrid-null joint-test recommendation of the first scope consult is still "seriously considered", not adopted.
- Claims, KI-85, `\pubhold`, data-availability and release text are Joseph's. Nothing is submitted, deposited or
  tagged.
