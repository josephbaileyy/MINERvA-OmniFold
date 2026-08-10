# Criteria that answer a subtly different question than the one asked

**Four instances in four days, none of them an arithmetic error.** Every one is a correctly-computed
quantity compared against a requirement that belongs to a *different* quantity. That is the common form,
and it is the most transferable thing this campaign has produced — because none of the four is findable by
checking the arithmetic, reading the code for bugs, or adding tests of the kind already present.

Joseph named the pattern on 2026-08-09 after the third instance. The fourth is mine and was found the next
day, which is the best evidence that naming it works.

## The four

### 1. A bar computed in the wrong SCOPE — CLM-012, error 0.190187

The D2 recovery criterion scores a **ratio of L1 sums over cells**, so the achievable ceiling is the
displacement-weighted mean of per-cell dilutions, `E_d[φ(a)] = 0.618228`. The retired bar was built from
`φ(E[a]) = 1-(1-0.42351622)^3 = 0.808415` — the dilution of an *aggregate* acceptance. Both are correct
arithmetic on the same acceptance map; they are different functionals. `φ` is concave, so Jensen makes the
scalar form **overstate for every possible acceptance map**, with equality iff acceptance is uniform.

*How it was found:* by computing the achievable range at all. Nothing in the criterion, its tests, or its
history hinted the ceiling was a different functional from the bar.

### 2. A bar that could never PASS — the retired `recovery >= 0.80`

`0.80 > 0.618228`, so no estimator, however good, could satisfy it. It was measuring the acceptance and
reporting the answer as an estimator verdict. This is the **mirror of the BEN-070/071 family** (a
threshold beyond reach so a gate can never FIRE) with the inequality reversed.

*How it was found:* by comparing the bar to the achievable range rather than to the measured value.

### 3. A criterion evaluated at the wrong POINT, outside its domain of validity

The step-1 repair criterion (iteration-2 correct sign **and** `ach/req >= 0.90`) tests the **increment**.
For the annealed arm, push was already `1.121393` (dev **−0.24%**) after iteration 1, so the required
correction was `1.002396` — *do essentially nothing*. Delivering a slightly-below-1 factor scores as
"wrong sign" while the **end state** is the best of any arm (`−1.17%` vs the baseline's `−34.46%`).

**Joseph's framing, which is the correct one and narrower than mine was:** the criterion has a **DOMAIN OF
VALIDITY**, and this arm falls outside it. When `push ≈ R` the required correction goes to 1, sign stops
discriminating, and `ach/req` becomes hypersensitive to a correction that no longer matters. For that arm
the criterion returns **NO INFORMATION**, not "fail." **It stands unmodified everywhere it
discriminates.** No predeclaration was overridden and none needed to be.

That framing is what makes this a specification finding rather than motivated reasoning: **it applies
identically to a bad arm that happened to land near target.** Such an arm would also be scored
"no information," and would then have to be judged on its end state — where it would fail. The finding is
independent of which arm wins, which is the test any re-reading of a criterion by an interested party
should have to pass.

### 4. A metric comparing a first-leg average against an end-to-end requirement — MINE

`step1_increment_trajectory.py` reported `ach/req = mean_w(r1) / (R / mean_w(push_prev))`. The numerator is
the **average of the step-1 multiplier**; the denominator asks what factor carries `mean_w(push_prev)` to
`R` — an **end-to-end** requirement. Reaching it via `r1` also passes through two legs the numerator omits:

    mean_w(push_prev) = 1.121393
      × r1 (mean 0.898016)          product of means      = 1.007029
      + Cov_w(push_prev, r1)        = +0.042511  (+4.22%)
    mean_w(pull)                                          = 1.049540
      + step-2 RE-ESTIMATION        = +0.061361  (+5.85%)
    mean_w(push_2)                                        = 1.110901

So the realized end-to-end factor is `1.110901/1.121393 = 0.990644`, and the like-for-like score is
`0.990644/1.002396 = 0.988276` — which **passes the 0.90 leg** and fails only on sign, by 1.2% on a
required move of 0.24%. My reported `0.895869` compared quantities separated by a +4.2% covariance term
and a +5.9% re-estimation term.

*Consequence, checked:* re-scoring my own trajectory end-to-end leaves the verdict
`CORRECT_AT_ITER0_DEGRADES_LATER` **unchanged** (sign correct at iteration 0, wrong at 1 and 2). One
characterization was wrong: I reported iteration 0 as "slightly **overshoots**, ach/req 1.0974"; end-to-end
it slightly **undershoots** at 0.9721. The sign — the load-bearing claim — holds either way.

*How it was found:* Joseph could not reconstruct one number from the other and said so. **The detection
was a consistency check between two reported quantities, not a review of either.**

## The common form, and why it evades normal review

> **A correctly-computed quantity compared against a requirement belonging to a different quantity.**

Each instance passes every check that operates *within* a quantity: the arithmetic is right, the code does
what it says, the tests test what they claim, and the numbers reproduce. What is wrong is the *pairing*.
No amount of care inside either side detects a mismatch between them.

Three of the four also share a **degeneracy structure**: the mismatch is invisible in the regime the
criterion was calibrated in, and only opens up elsewhere — at non-uniform acceptance (1), above the
ceiling (2), near target (3). A criterion validated on one operating point can be silently uninformative
at another.

## Detection heuristics, in rough order of yield

1. **Compare the bar to the ACHIEVABLE RANGE, not just to the measured value.** Compute the best any
   correct implementation could do. If the bar is outside it, the criterion is measuring the apparatus.
   Found (1) and (2).
2. **Check that achieved and required are the SAME quantity.** Write both as explicit functions of the
   same inputs and confirm the units, population, and *number of legs* match. Found (4).
3. **Ask where the criterion STOPS discriminating.** Take the limit as the system approaches target: if
   `required → 1`, a sign test degenerates and a ratio test goes hypersensitive. Declare the domain of
   validity in the criterion itself. Found (3).
4. **Reconstruct any reported number two ways.** Joseph found (4) purely by failing to derive one
   published quantity from another. Publishing enough numbers that they *can* disagree is what made it
   findable — a report that had shown only `ach/req` would have hidden it.
5. **When a criterion and a raw measurement disagree, suspect the pairing before the measurement.** In
   (3) and (4) the raw numbers were right in both readings; only the comparison was wrong.

## What follows for this campaign

- Criteria should carry a **stated domain of validity** alongside their threshold. `FROZEN`'s D2 block now
  carries the scope, weighting and injection pins for exactly this reason; the increment criterion should
  gain the `push ≈ R` caveat.
- **Report the ingredients, not only the verdict.** Instance (4) was findable because the receipt carried
  `push_prev`, `r1`, `pull` and `push` separately. A verdict-only receipt is unfalsifiable.
- This is the inverse of BEN-070/071 (gates that cannot fail) and BEN-076 (a liveness probe that cannot
  distinguish alive from dead). The unifying defect across all of them is **a check whose output does not
  depend on the thing it is supposed to be measuring**, over some part of its input range.
