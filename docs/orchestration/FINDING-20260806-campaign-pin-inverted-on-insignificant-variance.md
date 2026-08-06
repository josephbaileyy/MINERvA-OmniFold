# FINDING 2026-08-06 — a campaign pin was inverted on a variance estimate that was never significant

*Found because the user asked "Has agy really not helped with the niter 2 vs 3 decision?" — the answer
was that it had, and the record said otherwise.*
*Status: CONFIRMED by recomputation and independently by a second provider account (agy, effort high),
which reproduced the test statistic and interval.*
*Severity: produced a wrong recommendation that the user APPROVED, cost ~5 h of campaign time, and came
within one commit of freezing the wrong seed policy and raising a tolerance that did not need raising.*
*Outcome: corrected. `niter` 2 → 3 with `fold_forward_ratio_dev_max` held at 0.05.*

## Claim

On 2026-08-05 at 19:25Z this campaign recorded that a 16-seed measurement showed the per-seed spread
`sd` **"GREW 56%"** at `niter=3`, and used that to invert an advisor's ranking, discard its Rank 1
(`niter 2→3`, keep `tol = 0.05`), and recommend instead `niter=2` + `tol 0.05→0.055` — a tolerance
raise. The user approved that recommendation at 19:47Z.

**The 56% growth was never statistically significant.** It was two noisy 16-seed variance estimates
being differenced and reported as a fact.

## The numbers

Reported at 19:25Z, from 16 seeds (7–22), same `N`, same epochs, only `niter` changed:

    niter=2  sd = 0.7477%      niter=3  sd = 1.1703%      ratio 1.565x   -> reported as "sd GREW 56%"

The test that was not run at the time:

    F = (1.1703/0.7477)^2 = 2.4498      df = (15, 15)      two-sided p = 0.093
    95% CI for the true sd ratio  =  [0.925, 2.648]

That interval **contains 1.0** — no change — and it also **contains the eventual answer**. With 32 more
seeds per arm (48 total, identical seed sets 7–54):

    niter=2  sd = 0.8153%      niter=3  sd = 0.8444%      ratio 1.036x   <- essentially equal

The advisor's discarded assumption was `sd ≈ 0.81%` at `k=3`. Measured: **0.8444%, off by 4.2%.** Its
projected clearance of `F + 3.5σ` measures `F + 3.35σ`. It was right, and the measurement that
"refuted" it did not have the resolution to do so.

## Why it happened — three compounding causes

1. **A point estimate was reported as a fact.** "sd GREW 56%" is a claim about the estimator; the data
   supported only "the point estimate is 1.57 with a 95% CI of [0.93, 2.65]". No interval was computed
   before the number was used to overturn a design decision and was put in front of the user.
2. **The wrong test would have been used even if one had been run.** Both arms use the *same seeds*, so
   the design is **paired**. An independent two-sample F-test is not the right instrument, and here it
   is conservative in the wrong direction — pairing makes the observed fluctuation *less* meaningful,
   not more. (Contributed by agy; the local analysis had missed it.)
3. **The advisor's assumption was discarded rather than tested.** The question asked was "does the new
   measurement differ from what agy assumed?" The question that mattered was "does the new measurement
   *exclude* what agy assumed?" It did not.

## The second-order failure: escalation order

The user's standing instruction (2026-08-05 13:12Z, reinforced 15:18Z: use a *different account*) is to
route a held decision through a second LLM **before** escalating it. That was done for the first cut of
the data — and then **not done** for the 48-seed pooled data, whose recommendation was mailed to the
user first and reviewed afterwards. A second opinion on superseded numbers is not a second opinion on
the decision. When agy was finally given the pooled data it confirmed all four claims, reproduced the
F-test and interval, and added the paired-design point and a Fisher's exact test nobody had run.

## A related vacuity that let a stale operating point survive this long

`nd-unfolding/tests/test_b1_normalization_fix.py ::
test_tolerance_has_power_against_the_defect_and_admits_the_floor` — the test whose *job* is to prove
the tolerance has power — hardcoded `R, acc, k = 1.135, 0.621, 2` and bounded the tolerance above by the
defect signal `(R-1)/R`. It passed continuously while proving nothing:

* `0.621` is the **recoil-only** acceptance. Full-event FPS expands the truth denominator 32.8M → 49.2M
  while the reco population stays ~20.5M, so `a = 0.4186` and the structural floor more than doubles
  (1.71% → 3.73% at `k=2`). The floor bound was being checked against a campaign this estimator does
  not run.
* The real upper bound is **not** the defect signal. The parameter-free leg of `check_fold_forward_ratio`
  is algebraically `dev < C = (R-1)/(2R)`, exactly half the defect signal. **Any tolerance ≥ C is
  inert** — the parameter-free leg always binds first. Bounding by `(R-1)/R` admitted an entire range of
  tolerances that do nothing.

Repaired in the 2026-08-06 re-issue: it now reads `R` and the acceptance from the tracked Gate-2 runtime
receipt and `niter` from `FROZEN`, asserts the soundness condition `2(1-a)^k < 1`, and pairs every PASS
with a must-FAIL mutation.

## What actually decided it

Not the gaussian tail estimates on either side. **Realized exceedance of the existing tolerance:**

    tol = 0.05, 48 seeds each:   niter=2  ->  6/48 (12.5%)      niter=3  ->  0/48
    Fisher's exact test on that 2x2:  p ~ 0.026

and two structural facts the closed form gives for free: `niter=2`'s max sits **0.1428 pp** below the
immovable ceiling `C` and **grew +0.2291 pp** going 16 → 48 seeds, while `niter=3`'s max **did not move
at all** over the same expansion and sits 1.2441 pp below `C`.

Note what this means: the closed-form window test cannot discriminate the two options — `0.05` is
admissible at both `k=2` and `k=3`. Only realized exceedance separates them. A decision about a
threshold should be argued on realized exceedance, not on a model's tail.

## Prescriptions

1. **Never report "X changed by N%" from sample statistics without an interval or a test**, and never
   escalate such a claim to the user as a fact. If it is load-bearing enough to overturn a decision, it
   is load-bearing enough to need the test.
2. **Spread claims need real `n`.** At `n = 16` the 95% CI on an sd *ratio* spans roughly `[0.6x, 1.6x]`
   — wide enough that a 1.5x point estimate is indistinguishable from noise. Either get `n ≳ 48` or
   report the interval alongside the estimate.
3. **Paired designs get paired tests.** If both arms share seeds, say so and choose the instrument
   accordingly.
4. **To overturn a quantitative assumption, show the new data EXCLUDES it** — not merely that the point
   estimates differ.
5. **Route the FINAL data through the second account.** Re-review after every material data change, not
   once per question.
6. **Threshold decisions rest on realized exceedance**, with the model tail as colour, not as the
   argument. Report the non-parametric bound too (0 of 48 bounds a rate only below ~6% at 95%).
7. **Never hardcode an operating point in a test that guards an operating-point-dependent bound.** Read
   it from the owning receipt. A test that hardcodes a superseded constant passes forever and guards
   nothing — and it will not announce that it has stopped working.
8. **Guard the binding bound, not the loosest one.** For the fold-forward check that is
   `C = (R-1)/(2R)`, and a guard asserting `tol < C` is what makes the tolerance non-inert. Add the
   assertion when you discover the bound; the absence of it is why this went unnoticed.

## Cost, and the one thing that went right

Cost: ~5 h of campaign time on the wrong branch, a recommendation the user approved on figures later
shown ~6x optimistic, and job `56355818` (the D2 powered closure, ~21.5 h queued) cancelled 5:18 into
its 12 h run because it was executing the superseded `niter=2`.

What went right: **the decision rule was written down before the data existed**, every time. That is the
only reason each reversal reads as a result rather than a rationalisation, and it is why the error was
recoverable at the cost of 5 minutes of GPU rather than 12 hours. Keep predeclaring.

See also: [`B1-NORMALIZATION-FIX-DESIGN.md`](B1-NORMALIZATION-FIX-DESIGN.md) §2d,
[`RESTORE-2026-08-03.md`](RESTORE-2026-08-03.md) Step 2b, and the re-issue
[`state/p3f-pet-gate4-launch-code-gate-20260806.json`](state/p3f-pet-gate4-launch-code-gate-20260806.json)
(`seed_policy_change.measurement.corrected_earlier_claim`). Ledger row: **BEN-025**.
