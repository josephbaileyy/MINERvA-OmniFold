# Step 4 part 2: agy's targeted read on the final text (STEP4-PLAN.md §3 item 3)

**Setup:**
- agy (gemini) saw each before/after pair of the note's changed text alone. The pairs come from
  `r22/tools/make_agy_pairs.py`, against base `70eaad8fc`, after the review's fixes (`review.md`).
- The prompt is Step 4's targeted one (`step4/agy2/prompt.txt`, copied to `agy/prompt.txt`): list every difference in
  meaning.
- The control copy plants one negation change in each of Q2–Q4 (`KEY.txt`).
- The primer's one-word change (T6) is outside the note batch. It is checked by the ledger (T6 rows: `N:`, `X:` and the
  palette `L:` probe) and by the review.
- A first read, of the text before the review's fixes, also passed. It is superseded by this one, which reads the final
  text.

| pair | change | differences listed (real read) | verdict |
|---|---|---|---|
| Q1 | C2, the body's error-bar paragraph | "statistical errors only" becomes "the same bin errors as the unfolded points" | pass |
| Q2 | C1, Fig. 7 | the vertical bars' meaning (weight statistics; the completeness ratio one by construction; neither the data's statistical uncertainty nor the covariance); the published bars; the horizontal bars | pass: C1, as fixed by the review |
| Q3 | C2, Figs. 9 and 10 | the slices' bars defined, with a cross-reference; Fig. 10 "with the same error bars" | pass |
| Q4 | C3 and T3, Figs. 13 and 14 | red circles; black squares; the Tune line's full name and "line"; "Uncertainties are not drawn"; (a), (b); the "no printed titles" clause dropped | pass: all declared |

**Control: 3 of 3 planted changes are listed.**
- Q2: "not available" becomes "available", named as a changed claim.
- Q3: "no published measurement" becomes "published measurement", named as a changed claim.
- Q4: "Uncertainties are drawn." is listed.
