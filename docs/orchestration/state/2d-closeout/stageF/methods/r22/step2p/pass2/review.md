# r22 Step 2, paper pass 2: two-direction review of `paper_body.tex`

**Reviewer.** An independent, read-only agent with no history of the text. It compared the base `e33a1ab0` with the
worktree's `paper_body.tex` after the writer's pass, before the reverts that STEP2-PAPER.md §5 records. Line numbers
refer to that text.

**The rules it checked against:**
- STEP2-PAPER.md §5;
- the refused changes in `oos-changes.tsv`;
- the note sources.

**What it found:**
- None of the rewordings makes a change that `oos-changes.tsv` lists as refused.
- The three A7 sentences still match the base byte for byte.

**Counts:** LOST 1 serious (R2-1) and 1 minor (R2-2); WEAKENED 1 minor (R2-5); ADDED 1 minor (R2-3; R2-2 also
broadens); AMBIGUOUS 1 minor (R2-4). Three sentences SAME.

**Disposition** (STEP2-PAPER.md §5, "The text judged"):
- R2-1 is fixed by keeping the exception as a clause;
- R2-4 is fixed;
- R2-2, R2-3 and R2-5 are resolved by reverting those sentences to the merged text.

<!-- absence-ok: the review quotes printed paper sentences and their changes; not a claim that something has not been run -->

## R2-1: LOST, serious. The Limitations opener overstates where limitations are stated (:278)

- **Base:** "The limitations of these results are stated with the results they qualify, in Secs. III–V, and those of the
  calibrated tests in the companion note. The low stability of four of the sixteen cells is stated only here. The
  principal ones are these."
- **New:** the middle sentence is deleted.
- **Why it is lost.** The deleted sentence was the only exception to the general claim.
  - The reconstruction stability of R02, R06, R10 and R15 (0.16–0.25) prints only in Limitations item 2 (:283).
  - The note does not print it: no `sec_*.tex` or `app_*.tex` source has "reconstruction stability" or "lowstab".
  - As printed, the opener now says that this limitation is stated with the sixteen-cell result in Sec. V, and it is
    not.
- **Suggested fix:** keep the exception in physics wording, or state the cells' stability beside the Sec. V result as
  well.
- **Resolution:** "Apart from the low stability of four of the sixteen cells (below), the limitations of these
  results are stated with the results they qualify, …". The director accepted it as written.

## R2-2: LOST and ADDED, minor. The run-period check: "its own" made generic (:114)

- **Base:** "…its size is not validated and its own consistency check cannot fail."
- **New:** "…its size is not validated, and a consistency check that reuses those differences cannot fail."
  <!-- absence-ok: quotes the paper's printed run-period sentence, before and after; not a claim that something has not been run -->
- **Why.**
  - The indefinite article and the restrictive clause turn the sentence into a general principle. It no longer says
    that the analysis's own check is of this kind.
  - The note shows this only for one check (`sec_systematics.tex:170`).
- **Resolution:** reverted to the base.

## R2-3: ADDED, minor. A new definition of the residual proxy (:54)

- **New:** "…; the proxy is the median ratio of the absolute fractional residual to the fractional truth departure,
  for departures above \SI{1}{\percent}."
- **Why.**
  - The definition is new to the paper. It mostly matches `sec_5d.tex:161`, but it drops the absolute value of the
    denominator and "over cells".
  - The 1 % threshold is a new quantity. The numeral check passes only because a "1" token already prints elsewhere.
- **Resolution:** reverted to the base. The no-new-fact rule holds (the director).

## R2-4: AMBIGUOUS, minor. Which seed is 42 (:50)

- **New:** "…uses LightGBM~\cite{Ke} with negative-weight background subtraction, a refinement of 400 trees and 31
  leaves, and seed~42."
- **Why.** The sentence can be read as giving the refinement's seed. That reading contradicts Table I's caption ("the
  refinement classifier … is seeded at the estimator seed plus three") and `sec_method.tex:97`.
- **Resolution:** "uses LightGBM~\cite{Ke:2017lightgbm} at seed~42, with negative-weight background subtraction and a
  refinement of 400 trees and 31 leaves."

## R2-5: WEAKENED, minor. The Scope sentence loses its "one … one" count (:19)

- **New:** "The findings apply to the OmniFold implementation, data set, observables, configurations, and deformations
  tested here, not to multidimensional OmniFold in general."
- **Why.** "One implementation on one data set" becomes "the …", which can be read as OmniFold's implementation in
  general. The note keeps the count (`sec_intro.tex:32`).
- **Resolution:** reverted to the base.

## Checked and found SAME

- **The note pointer (:22).** Only the order changed. The citation and "cited below by section" stay.
- **The envelope target (:70).** It is equivalent given the target, and `sec_5d.tex:146` supports it. agy read it
  DIFFERS, so it is reverted.
- **"keeps" → "uses" (:54).** It is reverted with R2-3.
