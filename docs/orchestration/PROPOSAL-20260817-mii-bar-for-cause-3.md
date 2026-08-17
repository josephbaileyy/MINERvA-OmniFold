# PROPOSAL — the bar for cause 3's `M(ii)`

**Lane B, 2026-08-17. REVISION 2, after the `VL130` anchor was DENIED. FOR CONFIRM/DENY BY A SECOND LANE.
No run has been made and none may be until this is adjudicated.**

**Why a bar is needed:** `M(i)` carries `null 1.97e-50 << 1e-12`; cause 4's bound carries a measured
`<0.1 %`; **`M(ii)` carries no threshold of any kind.** Its nominated source (`\gbdtAiEstTrace`) was
disqualified on footing, so `M(ii)` had neither a source nor a bar and only the source was being replaced.

---

## ⚠ REVISION 1'S ANCHOR IS WITHDRAWN, AND THE WAY IT FAILED IS WORTH MORE THAN THE NUMBER

Revision 1 derived the bar from `VL130`'s **5.40 % σ inflation** at `k=1`, calling it *"the campaign's
existing argued-for tolerance in the closest analogous situation."* **That is wrong, and the row says so
in capitals:**

> `VL130`: *"**LABEL CORRECTED 2026-08-14: this is NOT seed-driven training noise.**"*

**`VL130` is the noise that REMAINS AFTER the seed is pinned** — `set_random_seed(42)`, subsample `0`,
*"the only differences between draws are process, node and GPU."* **`M(ii)` is the contribution of VARYING
the seed.** They are the two **disjoint halves of a decomposition**, and that row was relabelled nine days
ago specifically to stop being read the way I read it.

**I quoted `VL130`'s numbers out of the same row that contains that sentence.** Not a line I failed to
find — a line I had in front of me and read past, because it was adjacent to a figure that fit the
argument I was building. That is the shape this campaign keeps paying for: **the citation was true of the
row and false of the claim.**

**Three further defects, each fatal alone:**

1. **`5.40 %` was quoted without its domain.** The row restricts it: `k=1` is *"defensible on the bins that
   carry the spectrum"* — `5.40 %` bulk-90, `4.31 %` top quartile, **`281.9 %` thin quartile**, where 10 %
   would need `k≈1359`. **There is no global accepted `5.40 %` tolerance to anchor on.**
2. **`k=1` is accepted as a COST NECESSITY, not a tolerance** — *"no affordable `k` fixes the thin catch
   bins"*, *"401.7 GPU-h stands."* Using an affordability constraint as precedent for *what magnitude is
   tolerable* inverts its meaning.
3. **The anchor is `PROVISIONAL`, `SHAPE ONLY`, with `35.36 %` per-sd uncertainty and `k` a LOWER bound
   that *"understates the absolute noise."*** An anchor carrying 35 % uncertainty cannot support a 10×
   derivation.

**Superseded text retained above rather than deleted, per this directory's convention.**

---

## THE BAR — derived from PUBLISHED PRECISION, which needs no analogue

> ### **`M(ii)` is MET if the omitted seed contribution cannot change any published value at the precision it is printed to.**
>
> ### Operational form: **`sd(block_sum across seeds) / block_sum ≤ 0.027`**
> ### Absolute form, pinned: **`sd(block_sum) ≤ 1.177e-39`** against block sum **`4.357790406860002e-38`**

**This anchor is self-contained — there is no second situation to argue is similar, which is exactly how
revision 1 went wrong.** It is checkable by reading the note's own significant figures, it is immune to
`BEN-380` (a precision is not a definite description), and it is what the question means: *does omitting
this change what we publish?*

### Derivation

**Step 1 — what the quantity does.** An omitted component adds in quadrature, so a seed contribution of
fractional size `f` inflates a reported σ by `√(1+f²) − 1`.

**Step 2 — read the published precisions.** Measured from `docs/analysis-note/values.tex`:

| published quantity | printed | s.f. | half-unit in the last digit | as a relative change | ⇒ `f` bound |
|---|---|---|---|---|---|
| **`\gbdtFiveBlockMedian`** | **`13.36`** | **4** | `0.005` pp | **`0.0374 %`** | **`2.74 %`** |
| `\gbdtFiveAdoptTrace` | `5.81e-38` | 3 | `5e-41` | `0.0861 %` | `4.15 %` |
| `\gbdtFiveCVTrace` | `6.24e-38` | 3 | `5e-41` | `0.0801 %` | `4.00 %` |
| `\gbdtFiveMeanShift` | `1.65e-38` | 3 | `5e-41` | `0.3030 %` | `7.79 %` |

**Step 3 — the binding constraint is the tightest published quantity the contribution could move.** A
uniform relative inflation of the σ moves the median-per-bin percentage by the same relative amount, so
`13.36`'s four significant figures bind before the sqrt-trace's three: **σ inflation ≤ `0.0374 %`.**

**Step 4 — invert, and round DOWN so the bar sits strictly inside the invisibility threshold.**
`f ≤ 2.7361 %` → **stated as `f ≤ 2.7 %`**, i.e. `sd(block_sum) ≤ 1.177e-39`, inflation `0.0364 %`.

**Assumption stated, not buried:** step 3 assumes the seed contribution is roughly uniform across bins. If
it is instead concentrated, the median moves *less* than the total and the sqrt-trace bound (`4.15 %`)
would be the honest one. **Binding on the tightest is the conservative choice; a run that lands between
`2.7 %` and `4.15 %` should be reported as bar-dependent rather than as a clean UNMET.**

### The order-of-magnitude step is GONE, not restated

Revision 1's *"an order below the accepted tolerance"* claimed to inherit a principle from cause 4. **There
is no such principle to inherit: cause 4's `<0.1 %` is a MEASURED bound that happened to land three orders
below J28 — an observation, not a chosen tolerance.** So *"one order below"* was an unanchored choice
wearing the costume of a derivation. **Under the precision anchor it does not merely lose its support, it
becomes meaningless: a printed precision is not a tolerance you divide by ten.** Removed rather than
downgraded.

---

## THE NEW ANCHOR TIGHTENS THE BAR — it does not confirm revision 1's digits

| | revision 1 (withdrawn) | revision 2 |
|---|---|---|
| σ inflation | `≤ 0.5 %` | **`≤ 0.0374 %`** |
| `f` | `≤ 10 %` | **`≤ 2.7 %`** |
| `sd(block_sum)` | `≤ 4.358e-39` | **`≤ 1.177e-39`** |

**A factor of ~3.7 in `f`, and ~13 in inflation.** The prediction that `0.5 %` might survive unchanged does
not hold: **published precision is a much harder master than a borrowed tolerance.**

**And the consequence must be stated before any run, because it is the whole value of predeclaring:**
AI1's `1.306e-39` is `2.9969 %` of the block sum — **above the proposed bar.** So **if the candidate's seed
spread resembles the only analogous magnitude in the campaign, this criterion FAILS.** MET is not the
expected outcome. That is what a bar fixed before seeing the number is supposed to feel like, and it is a
reason to confirm the bar now rather than after.

## ATTAINABILITY IS NOW AN OBSERVATION AT `n=2`, NOT AN ARGUMENT

Revision 1 used AI1's `2.9969 %` as evidence that MET was attainable while barring it as a prior. **That
fails on the same ground twice** — `√Tr` of a seed covariance and `sd` of a scalar are not the same object
*in either role*, and **a quantity that cannot inform the expectation cannot bound the reachable range
either.** The argument is withdrawn.

**Replaced by a measurement, which the staged run already produces:** `n=1` fixes the per-seed cost; **`n=2`
gives the first commensurable spread estimate.** How many orders that estimate sits from the bar, in either
direction, settles reachability **at ~1/6 the cost of `n=12` and in the falsifier's own units.** Attainability
is therefore a **predeclared observation at `n=2`**, not a claim in this document.

## CROSS-CAUSE COMMENSURABILITY — attempted, and it reveals a real gap rather than closing one

Expressing this bar the way cause 4's is, against J28's `−9.35 %`: `2.7 % / 9.35 % = **28.9 %**`, versus
cause 4's `0.1 % / 9.35 % = **1.07 %**`. **The two bars are ~27× apart on that scale, so the causes are
NOT made commensurable by this exercise.**

**That is reported rather than smoothed over.** The reason is structural: cause 4 bounds a *retired
subtraction's residual effect* (a bias), while `M(ii)` bounds a *spread* (a variance contribution that
enters in quadrature). **A bias and a quadrature term are not comparable at the same threshold**, and
forcing agreement would manufacture a false parity. The precision anchor's virtue is that each cause is
self-anchored; the price is that they do not share a scale.

---

## CONFIRMED FROM REVISION 1 AND UNCHANGED

The **percentage-primary** form and its reason: **a bar expressed as a fraction of a specific block sum
silently re-points if that block sum is re-rolled** — `BEN-380`'s definite-description problem applied to a
**threshold** rather than a product, and not hypothetical, since the block sum has already moved once (J28).
The `0.027` and `1.177e-39` forms are pinned to `4.357790406860002e-38` and would be recomputed, not
inherited. **The seven rejections. The staged `n=1`. Both falsifiers, including distinctness-with-digests.
The not-an-admission-to-the-budget clause.**

**Also rejected, now:** `10 %` and the `0.5 %` inflation figure, on the grounds above — recorded so the
withdrawn number cannot be quoted from revision 1's text.

## WHAT THIS PROPOSAL STILL DOES NOT DO

* **Does not authorize a run.** `n=1` only, after confirm/deny.
* **Does not choose `n`.** `n` follows from the bar once the `n=1` cost is measured, by **realized
  exceedance rather than a fitted tail** (`BEN-025`). **12 inherited from a July scan with different
  purposes is a number, not a design.**
* **Does not admit any resulting number into the budget.** The ledger excluded AI1; **a commensurable
  replacement must not smuggle itself in by being commensurable.**
* **Does not settle the validity falsifier.** Per-seed outputs must be shown **mutually distinct, with
  digests recorded** — if the seed is not plumbed through, every block sum is identical and **the spread is
  zero for the wrong reason, which reads as the best possible result** (`BEN-181` + `BEN-344`). At `n=1`
  distinctness cannot be shown; carried as a predeclared requirement for `n ≥ 2`.
* **Says nothing** about seed × draw interaction (the draw is held fixed, deliberately), about any other
  cause, or about cause 3's other legs.
* **Products are tracked or preserved off scratch from the moment they exist** — `OI-130`.
