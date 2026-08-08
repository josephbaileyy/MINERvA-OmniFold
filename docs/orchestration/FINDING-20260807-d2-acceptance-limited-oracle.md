# The acceptance-limited oracle: 72% of D2's shortfall is specification; the other 28% is
# per-cell dispersion charged by the L1, not estimator response

> *Title corrected 2026-08-08: the original read "28% is the estimator", which invited exactly
> the reading BEN-038 forbids. The signed response sits within 0.19 pp of ceiling; 97.8% of the
> ceiling-to-measured gap is the scatter penalty. See
> `REVIEW-20260808-clm012-independent-rederivation.md`.*

**Date:** 2026-08-07 · **Tool:** `nd-unfolding/pet/d2_acceptance_oracle.py` (double-gated) ·
**Claim:** CLM-012 · **Ledger:** BEN-045 · **Commissioned by** Joseph, 2026-08-07: *"there's one
measurement left, and it's the one that decides."*

## 1. The number

At the nominal `k = 3`, scored with the criterion code unmodified:

| quantity | value | what it bounds |
|---|---|---|
| the bar | **0.80** | — |
| statistical oracle (`d2_oracle.py`, 151db63) | 0.954204 | sampling only |
| **acceptance-limited oracle, per-event** | **0.618228** | acceptance + sampling |
| acceptance-limited oracle, spectrum-space | 0.633208 | acceptance only |
| measured estimator (56381674) | 0.546853 | — |

**Decomposition of the shortfall:**

    total          0.80 − 0.5469 = 0.2531
    SPECIFICATION  0.80 − 0.6182 = 0.1818   71.8%   <- no estimator choice removes this
    ESTIMATOR      0.6182 − 0.5469 = 0.0714  28.2%
    the estimator reaches 88.5% of the ceiling acceptance permits

**Which ceiling, and why this one (added 2026-08-08 after review flagged the bracket).** The decomposition
uses the **per-event** `0.618228` because the criterion computes `recovery` with the A/B sampling difference
*inside it* — `h_unfolded` from half B against `h_target` from half A — and the per-event oracle is built the
same way, so it is the **matched** ceiling. The sampling-free `0.633208` would give **65.9% / 34.1%**; that
comparison is unmatched (a sampling-charged measurement against a sampling-free ceiling) and understates the
specification share. The review was right that advertising a bracket and silently using one end is a pattern
to flag; the fix is to justify the end, which is what this paragraph does.

**And the 28.2% is NOT "estimator response quality" — it is ~98% the L1 charging dispersion.** Of the
`0.086355` between ceiling and measured, the scatter penalty is `0.084433` = **97.8%**, leaving a signed
response deficit of `0.001922` = 2.2%. So the signed response is essentially *at* ceiling and the loss is
per-cell dispersion. BEN-038's rule is to split signed response from scatter before diagnosing; this section
originally did not.

And no iteration count rescues it — the oracle by `k`: 0.4236, 0.5642, **0.6182**, 0.6441, 0.6592,
0.6691 for k = 1…6. The best value at k = 6 is still 0.13 below the bar.

## 2. Construction, and why it is the right one

OmniFold learns in reco space and transports to truth space. A truth cell `b` with acceptance `a_b`
has only the fraction `a_b` of its events visible in reco, so one iteration corrects at most that
fraction; after `k` the corrected fraction is `r_b = 1 − (1 − a_b)^k`. An estimator limited by exactly
that and nothing else applies, per **event**:

    push_event = 1 + r_{cell(event)} · (tilt_event − 1)

Scored through `unit_spectrum`/`l1` — the same functions the gate uses — so the number carries the
criterion's per-cell absolute value and its A/B sampling difference. A mean-response figure like
0.63321 carries neither.

**Bracketed, not single-construction.** The spectrum-space variant applies the same per-cell response
directly to the histograms and so is sampling-free: 0.633208. The 0.014980 difference is consistent with a
sampling term (see the correction below for why that is weaker than the original claim).

**CORRECTED 2026-08-08 after independent review — see `REVIEW-20260808-clm012-independent-rederivation.md`.**
The spectrum-space value equals the tilt-weighted mean response to **0.0e+00** exactly, and the derivation
takes **two** steps, not one: (i) spectrum-space recovery `= 1 − E_w[|1−r|]` for *any* per-cell response, by
L1 factorisation through `w_b`; (ii) one-sidedness (`r_dil = 1 − (1−a_b)^k ≤ 1` for `a_b ∈ [0,1]`, which is
algebraically guaranteed rather than discovered) then collapses that to `E_w[r]`.

**A sentence previously here was false and has been removed.** It claimed this identity explained why
`d2_response_decomposition.py`'s "zero dispersion" column (0.6313) and the dilution ideal (0.63321) agree.
It does not: that column is `1 − |1 − E_r|` with `E_r` the **estimator's** mean response, so it *is*
0.631286, and the dilution ideal is a different object. Their agreement is the **empirical −0.001922 bias**,
which §4 relies on as evidence — so calling it an identity double-counted it as both trivial and
significant. The identity holds *within* a construction only.

The per-event value is *lower* because introducing two-sided sampling scatter makes the `|·|` bite; the
0.014980 difference **is consistent with** a sampling term rather than demonstrated to be one — the per-k
offsets (0.0144, 0.0117, 0.0150, 0.0188, 0.0216, 0.0238) are roughly stable but not constant.

## 3. Joseph's comparison, verified from the artifacts rather than from his mail

He asked for this explicitly and it holds:

| quantity | recomputed here | as he stated it |
|---|---|---|
| `E_w[r]`, signed mean response | **0.631286** | 0.63129 ✓ |
| dilution ideal, tilt-weighted | **0.633208** | 0.63321 ✓ |
| bias, measured − ideal | **−0.001922** | −0.0019 ✓ |

**But the weighting is load-bearing and he named the right one.** The committed acceptance map carries
*two* per-cell curves at `k = 3`: tilt-weighted **0.633208** and truth-mass-weighted **0.609475** (the
latter reproducing the map's own `0.6094746703987659`, the CLM-011 number). They differ by 0.0237, a
**3.7%** error if quoted against each other. BEN-038's 0.63129 is tilt-weighted, so 0.63321 is its
correct partner. Filed as BEN-045.

## 4. What this does NOT prove — the caveat is real and it is load-bearing

`(1 − a_b)^k` assumes step 2 resolves cells **independently**. `omnifold.py:218-220` evaluates the
truth classifier on all `pass_gen` rows, so a smooth learner can transport the injected `f(pT)` from
high-acceptance cells into low-acceptance ones and **beat** this curve; BEN-038 measured the top
acceptance band overshooting at `E_w[r] = 1.0333`. So **this is a reference curve, not a proof of
impossibility, and 0.80 is not shown to be unreachable.**

**BOTH of my original arguments for calling this decision-grade were corrected on 2026-08-08 by the
independent review, and they are weaker than I claimed. The caveat above is correspondingly STRONGER.**

1. ~~The empirical bridge — no *net* transport gain, so the curve is where the estimator operates.~~
   **True but analytically empty.** Per-cell, transport gain is *large and measured*: the two lowest
   acceptance bands carry **29.5% of the displacement weight** and beat their own dilution ceiling by
   **+0.1443** and **+0.1859** — the lowest by a factor of **18.6×** (0.1525 against 0.0082). Weighted
   `E_w|r_est − r_dil| = 0.1949` against a signed mean difference of 0.0019, i.e. the aggregate agreement is
   **100× smaller than the typical per-cell deviation**. Gain and a −0.25/−0.10 mid-band undershoot cancel at
   ep8 in this weighting, via a cancellation with no reason to be stable. So the curve is **demonstrably
   violated on 30% of the weight**, not merely "not a bound" — which BEN-038 had already recorded and I
   under-used.
2. ~~The model has one confirmed non-trivial prediction (0.19 pp).~~ **Budget-contingent, and my own ladder
   is the counterexample.** `E_w[r]` is 0.63129 (ep8 gate), 0.63250 (ctl8), **0.56324** (ep16) and ~**0.5235**
   (ep32) — so it moves 6.9 pp on doubling the budget and ~11 pp at 4×. The model predicts a *ceiling*; the
   agreement is between that ceiling and a *contingent* estimator value that happens to sit at it at ep8
   only. That is agreement at one point of a curve whose shape the model does not predict, not a confirmation.

Reaching 0.80 still requires the estimator to **substantially exceed** the acceptance-limited reference
through cross-cell transport — but note that at low acceptance it demonstrably *already does*, and what
prevents 0.80 is the mid-band undershoot plus the dispersion penalty, not an inability to transport.

## 5. My opinion, since Joseph asked for one

**The bar does not measure what the estimator can observe, and that is a specification defect.**

The criterion asks for 80% recovery of an injected truth-space shape change. Truth-weighted global
acceptance is 0.4235; the tilt-weighted recoverable fraction at `k = 3` is 0.633. So 0.80 sits above
the observable range, and the gap is not attributable to estimator response quality. As written,
`recovery ≥ 0.80` conflates two questions — *is the estimator good?* and *can cross-cell transport beat
acceptance dilution?* — and only the first is what a closure test should be asking.

**CORRECTED 2026-08-08: "it reads as a round number" was wrong, and the truth is better for this finding.**
`1 − (1 − 0.42351622)^3 = 0.808415`, i.e. **0.0084 above the bar** — too close to be coincidence. The likely
history is that 0.80 *was* derived from an achievability argument: the **scalar-scope** one at global
acceptance, which the acceptance map itself flags as overstating differential recovery by +19.9 pp
(`recovery_field_scope_note`; CLM-011's Jensen finding). So the defect is not that nobody derived the bar, it
is that **the bar was derived with a Jensen error** — and the corollary matters: *under the scalar reading
the bar sits below the ceiling and this claim is false.* Everything here therefore hinges on the per-cell
Jensen correction, which makes that correction the finding's real contribution.

**And `0.633208` is not a detector fact.** It is a property of (detector × injection × weighting). The same
285 cells give truth-mass 0.609475, prior-mass 0.609523, untilted-mass 0.609625, tilt-displacement 0.633208,
uniform-over-live 0.776110; and re-injections at amplitude −0.35 / +0.35 / +0.70 give 0.611760 / 0.628361 /
0.642253. For any re-specification the injection must be pinned alongside `k` and the acceptances.

**Recommendation: re-specify the criterion as recovery relative to the acceptance-limited reference,
with a predeclared fraction, and keep a separate absolute floor** so a genuinely broken estimator still
fails. Under that framing this estimator scores **88.5%** of what acceptance permits, which is a number
that reflects the estimator and can be defended in a technote.

**Why this is not tolerance-loosening, stated plainly because the constraint is explicit.** The
prohibition is on moving a bar so a failing product passes. This changes *what the bar measures* —
from absolute recovery to recovery of the observable part — which is a different act, and the
distinction is Joseph's to make; he made it on 2026-08-07. It also cuts against my own convenience: it
leaves the estimator with a visible 11.5% deficit and 28.2% of the original shortfall still owned by
the estimator, rather than excusing all of it.

**What I am not recommending.** Not `k = 4` (buys 0.026 of ceiling, still fails, and costs a pin
cascade). Not seed-ensembling (its ceiling is the signed response, 0.6313, for any N — and §2's
identity now explains *why* that ceiling is exactly the mean response). Not more epochs: the budget
ladder shows the coherent term worsening monotonically, +18.8% then +29.7% across 8→16→32.

## 6. Reproducing it

    python3 nd-unfolding/pet/d2_acceptance_oracle.py

Double-gated and fails closed: Gate 1 reproduces the committed report's gap/floor/residual/recovery
(≤2.2e-9, plus an exact population check on 1999920/1999941); Gate 2 reproduces both published numbers
in §3. Neither the oracle nor the verdict prints if either gate fails. No loader re-run — the halves
come from the artifact's own `dump_rows_a`/`dump_rows_b`, the same footing as `d2_oracle.py`.
