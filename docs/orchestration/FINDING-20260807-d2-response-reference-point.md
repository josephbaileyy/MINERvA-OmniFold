# D2's miss is 81% coherent under-application, not 97.8% scatter — and both terms alone fail the bar

**Date:** 2026-08-07 · **Tool:** `nd-unfolding/pet/d2_response_decomposition.py` (gated; reproduces every
published number before printing anything) · **Cross-stream:** CLM-010 (i) · **Ledger:** BEN-042

> **The standing conclusion does not change.** `FINDING-20260806-niter4-decision.md` 2b concluded that a
> perfect-bias estimator still fails the 0.80 bar, and that `niter` is not the lever. **Both hold.** What
> changes is *why*, what the dominant term is, and therefore which remedies were ever in scope. One of the
> two corrections below makes the conclusion **stronger** than its published argument.

## 1. The one-line correction

`FINDING-20260807-d2-underfitting-probe.md` and 2b report the D2 shortfall as **"97.8% per-bin scatter,
not bias"**. That number is correct, and it is measured **against the dilution ideal 0.63321**. The 0.80
bar is not. The bar compares against full recovery, and against that reference the same numbers read:

| | value | share of the miss |
|---|---|---|
| total miss `E_w[|1-r|]` = 1 − recovery | 0.453147 | 100% |
| **coherent under-application** `|1-E_w[r]|` | **0.368714** | **81.4%** |
| dispersion (published "scatter penalty") | 0.084433 | 18.6% |

**Plain statement of the failure: the estimator applies 63.1% of the injected tilt.** That is the whole
of the dominant term. "97.8% scatter" and "81.4% coherent" are the same two numbers divided by different
denominators — 2b's denominator presupposes the under-application is unavoidable, which is exactly the
thing 2b's own refutation paragraph says is not established (the top acceptance band overshoots at
`E_w[r] = 1.0333`, so 0.6332 is a reference curve, not a bound).

Verified two ways that agree to `9.2e-06`: in response space as `|1-E_w[r]|`, and independently in
spectrum space as the pt-marginal L1 over the gap. The injection is a function of pt alone, so the part
of the miss that survives marginalising over p∥ *is* the part coherent with what is being measured. The
two constructions are algebraically the same object whenever `sign(h_target − h_prior)` is constant
across a pt row, which holds here because the tilt is monotone in pt — so their agreement is a check on
the construction rather than a second result.

## 2. The published penalty is not the cost of the dispersion — and I nearly filed a false refutation

2b's argument runs: *"the scatter penalty alone (0.08443) exceeds the entire residual headroom
(`residual_budget_abs` = 0.046854)"*. Two defects.

**(a) Units.** The penalty is weight-normalised — a fraction of the gap. `residual_budget_abs` is an
absolute L1, `0.20 × gap`. In consistent units the penalty is **2.37× *inside* the headroom**, both ways
of making them consistent agreeing:

    absolute:   0.084433 × 0.234270 = 0.019780   vs  0.046854      inside by 2.37x
    normalised: 0.084433                vs  0.20            inside by 2.37x

**(b) But the penalty is the wrong quantity, and fixing (a) alone inverts the conclusion falsely.** With
`x_b = 1 − r_b`:

    actual cost        E_w[|x|]                    = 0.453147   (= 1 − recovery)
    published penalty  E_w[|x|] − |E_w[x]|         = 0.084433
    perfect-mean cost  E_w[|x − E_w[x]|]  (a MAD)  = 0.369794

The second is **not** the third: `|·|` is nonlinear under a shift, so if every `x_b` shared a sign the
penalty would be 0 while the spread was unchanged. Measured, **MAD/penalty = 4.38**. The honest
counterfactual — every cell's response shifted so the mean is exactly 1, every cell's deviation left as
measured — gives **recovery 0.6302, FAIL**, and the dispersion **exceeds** the headroom by 1.85×.

**So 2b's conclusion is right, by a route its own arithmetic did not take, and the corrected number
supports it more strongly.** This is recorded because I got as far as a written "the finding is refuted
on a unit error" before computing the counterfactual. Correcting (a) without noticing (b) produces a
confident, wrong reversal of a load-bearing conclusion; the next agent to spot the unit mismatch will be
one step from the same mistake, which is why `d2_response_decomposition.py` computes the MAD in the same
breath as the unit check.

## 3. Each term alone fails. That is what closes the remedy question.

| arm | ep | recovery | `E_w[r]` | coherent | MAD | perfect mean, measured dispersion | zero dispersion, measured mean |
|---|---|---|---|---|---|---|---|
| 56381674 gate | 8 | 0.546853 | 0.63129 | 0.368714 | 0.369794 | 0.630206 **FAIL** | 0.631286 **FAIL** |
| ctl8 | 8 | 0.548769 | 0.63250 | 0.367501 | 0.366439 | 0.633561 **FAIL** | 0.632499 **FAIL** |
| ep16 | 16 | 0.536695 | 0.56324 | 0.436756 | 0.346135 | 0.653865 **FAIL** | 0.563244 **FAIL** |

**No single-axis remedy passes D2.** Specifically:

- **Seed-ensembling cannot reach the bar for any N.** Averaging over estimator seeds reduces dispersion
  and leaves the mean response alone, so its ceiling is the last column: **0.6313**, for N = 2 or N =
  10 000. Against the memo's sizing of "N ~ 16–25 seeds, 30–50 GPU-h", the arm cannot buy a pass.
  Even reaching the headroom on the dispersion term *alone* needs only N ≳ 3.4 under an optimistic
  independent-`1/√N` model — and would still leave recovery at 0.6313.
- **More iterations cannot either**, which is section 2's existing point and is untouched here: the
  dilution ideal is 0.6629 at k=4 and 0.6929 at k=6, so even zero dispersion fails at every tabulated k.
- The two terms are **comparable in size** (0.3687 and 0.3698). No prior framing showed that: 2b's
  denominator made dispersion look like 97.8% of a small residual, and the marginal view alone makes the
  coherent term look like 81.4% of a large one. Both distortions come from the reference point.

## 4. The budget ladder moved the *coherent* term, and the memo's pre-registration is falsified in advance

The ladder was armed "read on the scatter axis". Read that way it reports a triumph that did not happen:

    ctl8 (ep8) -> ep16 (ep16)
      recovery                   0.548769 -> 0.536695   (-2.20%)
      mean response E_w[r]       0.63250  -> 0.56324    (-0.06925)
      coherent under-application 0.367501 -> 0.436756   (+18.8%)
      dispersion, MAD            0.366439 -> 0.346135   (-5.5%)
      published scatter penalty  0.083729 -> 0.026549   (-68.3%)   <- not a dispersion measure

The penalty collapsed 68% while the actual spread moved 5.5%, because the penalty depends on how many
cells' responses straddle `r = 1` and 2× budget pushed 38 of 86 overshooting cells back under. **Doubling
the budget made the under-application worse and the spread slightly better; recovery fell because the
first effect is larger.**

**This falsifies the pre-registration Joseph's memo asked for, in the opposite direction, and the
falsifying arm had already landed.** The memo's hypothesis was *"4× budget overfits the finite training
half harder ⇒ MORE per-cell scatter ⇒ recovery worse again"*. Recovery did get worse, but dispersion went
**down** on both measures, so the mechanism is wrong even where the direction is right. Registering it
now, with ep16 in hand, would be pre-registration in name only.

### Pre-registration for ep32 (`56431651`), written while it is still `PENDING`

Submitted 2026-08-06T18:54:02, still `PENDING` at 2026-08-07T11:20Z (~16.4 h queued), so nothing below is
informed by its result. Predictions, in the metric this finding establishes:

1. **`E_w[r]` falls again**, below ep16's 0.56324; predicted band **[0.48, 0.56]**.
2. **MAD falls again but only slightly**, below ep16's 0.346135; predicted band **[0.31, 0.346]**.
3. **Recovery falls again**, below ep16's 0.536695; predicted band **[0.49, 0.537]**.
4. **Verdict FAIL**, and `is_nominal_configuration: false`.

**Falsifiers, stated so this can lose.** If `E_w[r]` *rises* above 0.56324, the monotone-in-budget reading
of the coherent term is wrong and the ep8→ep16 move was scatter, not trend. If MAD *rises*, then budget
does increase dispersion after all and the memo's mechanism is right at 4× even though it is wrong at 2×.
If recovery rises above 0.548769 (better than either ep8 arm), the entire "budget makes it worse" reading
collapses and the two ep8 points plus ep16 were a fluctuation larger than the ~0.35% GPU band suggests.

## 5. What this does not show

- It does not lower or question the 0.80 bar, and no threshold was touched. The bar is quoted from
  `criteria.recovery_min` in the reports.
- It does not show the coherent term is *fixable*. It shows it is the dominant term and that it is not
  proven unavoidable — 2b's refutation of the dilution ceiling as a bound is what leaves that open.
- The zero-dispersion column is a counterfactual on the *measured* mean response, not a bound on what a
  different estimator class could achieve. The sampling-only oracle (`d2_oracle.py`, commit `151db63`)
  scores 0.9542, so the criterion has headroom; nothing here contradicts that, and nothing here promises
  a real estimator can use it.
- Two ep8 arms and one ep16 arm is a three-point read on a two-point trend. ep32 is the third budget
  point and its reading is pre-registered above.

## 6. Consequences

- **Do not buy the seed ensemble as a remedy.** Its ceiling is 0.6313 by construction. It remains a
  legitimate *diagnostic* of whether the dispersion is seed-structured, but that answer changes no
  decision now that the coherent term alone fails the bar — so the recommendation is **not to spend the
  GPU-hours**, and this is Joseph's call to overrule.
- **Any future D2 remedy discussion has to name which term it moves.** Dispersion has 0.20 of headroom
  and currently costs 0.3698; the mean response needs to go from 0.631 to ≳0.80 in the same estimator.
- `FINDING-20260806-niter4-decision.md` 2b and `FINDING-20260807-d2-underfitting-probe.md` both carry a
  dated pointer to this file rather than being rewritten, since the numbers in them are correct and it is
  the framing and one arithmetic step that needed amending.
