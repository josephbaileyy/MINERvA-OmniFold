Do not use any tools, commands or files: everything you need is in this message. Answer directly, in text, in full.

You are a mathematical statistician expert in sequential Monte Carlo tests (Besag–Clifford, Gandy's sequential MC tests, Clopper–Pearson intervals) and multiple testing (Holm). Below are (1) an excerpt of the code implementing a batch-sequential Monte Carlo decision procedure for ten hypothesis tests calibrated with pseudo-experiments, (2) a derivation by an analyst claiming the familywise error rate of the decisions is at most 0.81α as coded, 0.844α for any stopping on the batch grid, and 0.89α for any stopping at all (≤1999 draws), assuming the calibrated tail probability p is super-uniform under the null, and (3) the script used to compute the numbers.

Check the argument rigorously. In particular:
1. Is the event inclusion {reject at threshold c} ⊆ ∪_{B≤1999} {U(k_B,B) < c} correct for this code (Holm with 'determinacy': reject if the 95% CP upper end < threshold, stop if lower end > threshold, 'undetermined' otherwise; steps ordered by (k+1)/(B+1))? Are there paths the inclusion misses (e.g. ordering by p-hat, ties, the 'undetermined' branch, shared stopping between total and shape tests, the max-p over shifted variants)?
2. Is the Holm reduction FWER ≤ m0·R(α/m0) valid without independence here, given that tests are ordered by p-hat rather than by U?
3. Is R(c) = ∫ P(E_c | p) dp the right quantity under super-uniform p, and is taking p uniform the worst case? (Note P(E_c|p) is decreasing in p?)
4. Do the numbers look right (order of magnitude check: for c=0.05 and B up to 1999 with a union over every B, is 0.89 plausible)?
5. State precisely the assumptions under which the replacement sentence in the derivation is true, and propose a corrected sentence if it overstates anything.
Give a verdict: CORRECT / CORRECT WITH CAVEATS / WRONG, with reasons.
