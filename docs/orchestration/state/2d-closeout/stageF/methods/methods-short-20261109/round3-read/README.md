# Style round 3's paper items: meaning read and abstract read (2026-11-12)

**What changed:** paper_body.tex and main_paper.tex, from d42270ed's merge. `round3_batch.py` applies the director's
approved round-3 items 1–7, and the abstract's opening follows item 8.

**Meaning read on the body** (`pairs.txt`, 23 groups; an independent general-purpose subagent, read-only): 12 OK,
7 NOTE, 4 DEFECT. All four were fixed:
- **§5.3, a false statement.** "No tested level of a setting, and not IBU at five iterations, removes the bias flag at
  either truth" was wrong for IBU. The readout (fd/receipts-prr/read/cluster/readout.json, ibu/K5/q3/s991000) has the
  q3 tilt unflagged under IBU at five iterations. The class prr-pr3-ibu = not means not both. The sentence is now
  "Neither a tested level of a setting nor IBU at five iterations removes the bias flags at both truths."
- Table 4's second coverage test prints "Descriptive:" on its offset-proceeded and repaired routes, now that the status
  column is gone.
- §4.2's "``differ''" no longer refers to a removed status word.
- z's covariances are stated exactly: C in fractional form, each element divided by the product of the data result in
  its two cells; N the covariance of the mean fractional residual (nd-unfolding/fd_f0_regrade.py docstring :21 and
  :665).

**Body notes taken:**
- "Only playlist 1A predates";
- "It is built to contain these differences";
- Table 4's fake-data row "Bias flagged under the reported covariance";
- the bias-half row marked as a descriptive bias-screening rule;
- the §6.2 lead defines the joint region;
- §7's summary scopes closure to "background-inclusive closure meets the bias criteria on the sixteen cells".

**For the director:** FD-PRR-DECLARATION.md §5.3 (:308) fixes "clears / does not clear at these truths" as the PR-3
wordings. The plain "removes the bias flags" follows round 3's item 2, which you approved.

**Abstract read** (`abstract-pairs.txt`, three rendered cases): MINOR. Its four substitutions were applied:
- "testing its truth recovery, …" in place of "characterizing", which claimed an outcome;
- "held-out generator tunes" restored;
- "A corresponding test of the five-observable estimator's covariance" (the test uses the reported estimator, §6.2);
- "this five-observable output", so the illustration clause does not reach the two-dimensional benchmark.

In addition, "the five-observable result retains part of its prior" names its estimator, paid for by "rebuilt at two"
in place of "rebuilt at each of two". Every live case is at most 249 words, and no rendered case has a semicolon.
