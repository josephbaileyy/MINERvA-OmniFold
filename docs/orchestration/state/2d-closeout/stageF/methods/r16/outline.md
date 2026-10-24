# Reverse outline of the paragraphs register round r16 touched: before (origin/main 927f40bf) and after

**Method:** `register-method/HANDOFF.md` §3, step 3, restricted to the paragraphs that hold the five passages the r15
P1 raters still flagged (`r15/REPORT.md`, "What P1 still flags") and the other passages this round changed. Each
paragraph is reduced to one sentence. Paragraphs not listed are unchanged.

The r15 P1 runs on the r15 paper (three sol2 runs, all 3.0) quoted these passages:

| target | quoted by | paragraph |
|---|---|---|
| the rerun pseudo-experiments | runs 1, 2, 3 | Sec. VII C, ¶3 |
| "descriptive ... do not re-grade" | runs 1, 2, 3 | Sec. VII E, ¶1 |
| the five-iteration rule | runs 2, 3 | Sec. III, ¶4 |
| the seed panels | run 1 | Fig. 3 caption |
| the budget extension | run 3 | Sec. VII C, ¶3 |

## Before → after, one sentence per paragraph

**Sec. III, ¶4 (configurations).**
- Before: all configurations use five iterations and boosted trees, with the uses of (a) and (e), and a final clause
  that (e) "keeps five iterations under a rule fixed before the comparison", with "the rule's measure" defined in
  apposition.
- After: the same paragraph; the last sentence states the criterion, that it was fixed in advance, and what it
  measures, without the rule's internal name.

**Sec. IV B, ¶3 (the 2D statistical block).**
- Before: the quoted block; the earlier band and its pre-specified test; the post hoc rescoring; then "The
  two-dimensional central value is therefore reproducible ...", which does not follow from the band history.
- After: the same, with "therefore" dropped. The earlier-band history stays: `check_sec4_receipts.py` binds two of its
  values, and Table I lists "an earlier band failed coverage" as the 2D covariance's test (see REPORT, for the
  director).

**Sec. V A, ¶2 (closure with backgrounds, 2D).**
- Before: one 70-word sentence ending "; the two-dimensional result is being moved to the refined estimator".
- After: two sentences (R10); the second keeps the decision's wording.

**Fig. 3 caption.**
- Before: "panel (b) uses separate assessment seeds, which also entered its later development".
- After: "panel (b) separate seeds that were later also used in its development". The disclosure stays because it
  qualifies the caption's "not used while it was chosen".

**Sec. VII C, ¶2 (decision rule).**
- Before: Holm, the stopping rule, A1 and A2, the bound, the nuisance-averaged size, and "The point estimates
  (k+1)/(B+1) carry no separate validity claim."
- After: the same; the last sentence says that the error control applies to the decisions, not separately to the
  point estimates.

**Sec. VII C, ¶3 (what was data-informed, and the lost draws).**
- Before: design fixed before any observed statistic (reviewers had seen residuals); budget extended with p values
  visible, error control unaffected; lost draws "were rerun ... so no assignment of the lost outcomes changes any
  decision"; recomputation; pointer to "the design record and the rerun".
- After: the two data-informed elements stated as disclosures in plain terms (fixed design and what its reviewers saw;
  computing time increased after the p values had become visible, and why the error control does not depend on it); the lost
  draws stated as counts, then what the decisions use, then what the rerun found and what it implies; recomputation;
  pointer.

**Sec. VII E, ¶1 (results).**
- Before: every test rejected; the CH correction; "These target-corrected evaluations are descriptive and do not
  re-grade the decisions ..."; the multiplier scan, ending "the scan tests that one direction and bounds neither the
  actual residual nor the convergence"; the null locations; pointer.
- After: the CH correction's status said as its content (descriptive; the decisions concern each prediction on its
  generation target, and stand); the scan with "it probes that one direction"; its limits are stated in condition (i)
  and Sec. VIII A item 7.
