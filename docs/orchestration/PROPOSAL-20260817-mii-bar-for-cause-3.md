# PROPOSAL — the bar for cause 3's `M(ii)`

**Lane B, 2026-08-17. FOR CONFIRM/DENY BY A SECOND LANE. No run has been made and none may be until this
is adjudicated** — a bar proposed and adjudicated by the same lane is the thing being avoided.

**Why a bar is needed at all:** `M(i)` carries `null 1.97e-50 << 1e-12`; cause 4's bound carries `<0.1%`
against a `−9.35%` reference; **`M(ii)` carries no threshold of any kind.** Its nominated source
(`\gbdtAiEstTrace`) was disqualified on footing, so `M(ii)` currently has neither a source nor a bar and
only the source is being replaced.

---

## THE PROPOSED BAR

> ### Primary form: **the unmeasured seed contribution must inflate a reported σ by ≤ 0.5 %.**
>
> ### Operational form: **`sd(block_sum across seeds) / block_sum ≤ 0.10`**
> ### Absolute form, pinned: **`sd(block_sum) ≤ 4.358e-39`** against block sum
> **`4.357790406860002e-38`**

**The primary form is the bar; the other two are its consequences at this block sum.** Stated that way on
purpose — see *"why the bar is not primarily a fraction"* below.

## DERIVATION

**Step 1 — what the quantity does to the result.** An uncertainty component omitted from a budget adds in
quadrature, so a seed contribution of fractional size `f` inflates the reported σ by
`√(1+f²) − 1`. This is the same algebra `VL130` uses for the replicate count (`δ_meas² = δ_phys² +
(f/√k)²`), so it is the campaign's own way of converting a noise fraction into a consequence:

| `f` | σ inflation |
|---|---|
| 3 % | 0.045 % |
| 5 % | 0.125 % |
| **10 %** | **0.499 %** |
| 14.1 % | 0.995 % |
| 20 % | 1.98 % |
| 30 % | 4.40 % |

**Step 2 — the tolerance, anchored to something this campaign has already accepted.** `VL130` records
that `k = 1` **inflates a σ by 5.40 %** on the bulk-90 domain and concludes *"`k = 1` is defensible on the
bins that carry the spectrum"*. So a 5.40 % σ inflation is the campaign's existing, argued-for tolerance
in the closest analogous situation (unmodelled run-to-run noise folded into a covariance).

**Step 3 — apply cause 4's PRINCIPLE, not its number.** Cause 4's bound is not an absolute preference; it
is stated *relative to the effect it must be negligible against* — *"three orders below the J28
correction's `−9.35%` and two below the footing effect"*. Taking the principle rather than the digits:
**an order below the tolerance the campaign has already accepted.** `5.40 % / 10 ≈ 0.5 %`.

**Step 4 — invert.** σ inflation ≤ 0.5 % ⟺ `f ≤ 10.0 %` ⟺ `sd(block_sum) ≤ 4.358e-39`.

## THE BAR MUST BE REACHABLE IN BOTH DIRECTIONS, AND IS

`BEN-344`'s standard applies to a bar as much as to a check: **a bar that cannot be met is as defective as
one that cannot fail.**

* **MET is attainable.** The only analogous measurement in the campaign — AI1's `1.306e-39 / 4.3578e-38 =
  **2.9969 %**` — sits well below 10 %.
* **UNMET is attainable.** 10 % is below the ~14 % where inflation reaches 1 %, and far below the 20–30 %
  band. If constructing over the universe sweep amplifies seed sensitivity, the bar can fail.

**AND A WARNING THAT MUST TRAVEL WITH THAT 2.9969 %: it is a DIFFERENT QUANTITY from the falsifier's.**
AI1's figure is `√Tr` of a *seed covariance*; the falsifier measures the **sd of a scalar** (the block sum)
across seeds. They are not the same number and need not be close. **Quoting 2.9969 % as "the expected
value" of the falsifier would repeat exactly the commensurability error that disqualified `\gbdtAiEstTrace`
in the first place.** It is used here only to show MET is *attainable*, never as a prior. **The expected
value of the falsifier's quantity is unmeasured — which is why `n` must follow from the bar rather than
from a prior.**

## WHY THE BAR IS NOT PRIMARILY A FRACTION

**A bar expressed as a fraction of a specific block sum silently re-points if that block sum is ever
re-rolled** — `BEN-380`'s definite-description problem applied to a threshold rather than to a product.
The block sum has already moved once (J28), and cause 3's whole difficulty is that a number outlived the
footing it was computed on.

So: **the bar is the 0.5 % σ-inflation statement, which survives a re-roll**, and the `0.10` / `4.358e-39`
forms are pinned to `4.357790406860002e-38` explicitly. If the block sum changes, the fraction is
recomputed from the primary form rather than inherited.

---

## WHAT I REJECTED, AND WHY

| rejected | why |
|---|---|
| **`0.1 %`, cause 4's number** | Imports the *digits* instead of the principle. Cause 4's bound is calibrated to a `−9.35 %` reference; the nearest analogue for a seed spread is ~3 %, so `0.1 %` is a bar that essentially **cannot be met**. Defective in the mirror direction to a bar that cannot fail. |
| **`1e-12`, `M(i)`'s** | `M(i)` is a numerical **identity null** (`1.97e-50`) and `1e-12` is a round-off tolerance. `M(ii)` measures a real physical spread. Importing it makes MET impossible **by construction**, which is not a strict bar but a broken one. |
| **`3 %`, AI1's own ratio** | Circular twice over: it sets the bar for the replacement using the number just disqualified on footing, **and** it is a different quantity from the falsifier's (see above). |
| **"orders below `−9.35 %`" by reference parity** | Gives ~`0.01 %`. Parity of *reference* rather than of *principle*, and unreachable. |
| **A bar on `√Tr(C_seed)` instead of `sd(block_sum)`** | More informative, and it is what AI1 measured — but the scoped falsifier measures the scalar, and a full per-seed covariance is a larger object than the staged run buys. **Noted as the better quantity if a later stage affords it, and flagged so the two are never conflated.** |
| **Deciding after seeing the number** | The thing this proposal exists to prevent, and the ground on which cause 4's `INAPPLICABLE` was denied. It cannot be denied there and waived here. |
| **A bar on the per-bin median (13.359 %) rather than the block sum** | Defensible, but it changes the object mid-criterion: `M(ii)` asks what seeds contribute to the *budget*, and the budget's scalar is the block sum. Recorded as considered. |

---

## WHAT THIS PROPOSAL DOES **NOT** DO

* **It does not authorize a run.** Step 3 is `n = 1` only, after this is confirmed.
* **It does not choose `n`.** `n` follows from this bar once the `n = 1` cost is measured: pick `n` so the
  spread's own uncertainty is narrow *relative to the bar*, by **realized exceedance rather than a fitted
  tail** (`BEN-025`). **12 inherited from a July scan with different purposes is a number, not a design.**
* **It does not admit any resulting number into the budget.** The ledger excluded AI1 from the budget, and
  **a commensurable replacement must not smuggle itself in by being commensurable.**
* **It does not settle the validity falsifier.** The per-seed outputs must be shown **mutually distinct,
  with digests recorded** — if the seed is not plumbed through, every block sum is identical and **the
  spread is zero for the wrong reason, which reads as the best possible result** (`BEN-181` + `BEN-344`).
  **At `n = 1` distinctness cannot be shown, so it is carried as a predeclared requirement for the `n > 1`
  stage.**
* **It says nothing about seed × draw interaction** (the draw is held fixed, deliberately), nothing about
  any other cause, and nothing about cause 3's other legs.
