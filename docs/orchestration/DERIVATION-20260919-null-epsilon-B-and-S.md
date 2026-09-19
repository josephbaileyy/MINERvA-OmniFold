# DERIVATION — `B`, `S`, and `null_epsilon` for the scalar-5D null

**Step 2 of the goal, under Joseph's R2 and R3.** Read-only measurement; no production run.
**This derivation is committed BEFORE `ε` is declared and before any submission.**

## R2's gate, checked first — and it PASSES

R2 conditions `S = 1e-3` on `r_null` being *"a relative quantity comparable to that 5% bound"*, and
says to stop with **(C)** before production if it is not. Read from the code, not the docs:

`z_statistics.null_ratio` — **`r_null = ‖x_cv2 − x_cv‖ / ‖x_cv‖`**, both L2 norms of the **same
cross-section vector**, same units, same population. Its own docstring: *"the ratio is
**dimensionless by construction** rather than by assertion."* It also records why
`sqrt(Tr C_Z)` was **rejected** as a denominator — it would divide a central-value difference by an
uncertainty scale, letting a larger covariance license a less deterministic CV.

**So `r_null` is a dimensionless fractional change and is comparable to a 5% fraction. The gate
passes.**

⚠ **One distinction recorded rather than glossed**, because I withdrew a related comparison earlier
and Joseph accepted that withdrawal: `r_null` is a fractional change of the **CV vector**, while
cause 3's `5%` bounds movement of an estimated **σ**. They are **not the same quantity**. R2 does not
equate them — it uses `5%` as *the smallest movement ruled resolvable* and places `S` two orders
below it. That is a **scale** argument, which survives the distinction; a **ratio** of the two would
not.

## `S = 1e-3` — Joseph's, recorded as his

His ground, independent of `B`: a fixed-seed null violation must be negligible against the smallest
movement he has ruled resolvable, `cause3 = 5%` (`AUTHORIZATION-20260918` §2 ruling 5). **`1e-3` is
50× below it.**

## `B = 1e-12` — the operating-error bound, with its assumptions and its weakness stated

**Measured inputs.** Two independent executions on the same pinned inputs:

| | |
|---|---|
| probe `58524334` | `r_null = 4.4311e-14` |
| persisted pilot operands | `r_null = 4.4520e-14` |
| agreement | ratio **`0.995305`** — **0.47%** |
| first-checkpoint divergence | `3.27e-16` ≈ **1.47 ulp** at double precision |
| growth across the unfold | `4.452e-14 / 3.27e-16` ≈ **136×** |

**Mechanism:** floating-point non-associativity in threaded reductions. The per-call divergence is
~1.5 ulp and accumulates to `~4.5e-14` over the unfold.

> **`B = 1e-12`** — **22.5×** the largest observed `r_null`.

**Assumptions, stated:** that run-to-run variation stays within ~20× of the two observations, on the
existing unpinned configuration with these pinned inputs.

⚠ **CONFIDENCE, HONESTLY: `n = 2` IS NOT A CONFIDENCE INTERVAL and I will not dress it as one.** Two
observations cannot support a distributional claim. What carries the argument is **margin, not
statistics**: `ε = 1e-9` sits **4.4 orders of magnitude** above the observed `r_null`, so the claim
`B ≤ 1e-9` would survive a **22,000-fold** increase in run-to-run variation. The conclusion is
therefore **insensitive to the weakness of `n = 2`**, which is why further runs were **not**
purchased — they would refine a number the conclusion does not depend on.

## `ε = 1e-9` — inside `[B, S]`, and NOT chosen retrospectively

| | |
|---|---|
| `B ≤ S` | `1e-12 ≤ 1e-3` ✅ (9 orders) |
| `ε ∈ [B, S]` | `1e-12 ≤ 1e-9 ≤ 1e-3` ✅ — **1000× above `B`**, **10⁶ below `S`** |
| observed `r_null` vs `ε` | `4.45e-14` vs `1e-9` — **4.4 orders of headroom** |

⚠ **`ε = 1e-9` is the PRE-EXISTING proposal**, not a value invented now to fit:
`NAVIGATION-20260917:84` records *"`ε = 1e-9` is **PROPOSED and UNGRADED**, its falsifier
**UNEVALUATED**."* R3 anticipated exactly this — *"the existing 1e-9 proposal qualifies if `B ≤ 1e-9`
holds at the stated confidence"* — and `B = 1e-12 ≤ 1e-9` holds with three orders to spare.

**What this does NOT establish:** that the new build's `r_null` will fall below `ε`. That is what the
production run measures, and an exceedance is outcome **(B)**, recorded and not retried.
