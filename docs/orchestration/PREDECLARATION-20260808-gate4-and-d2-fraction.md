# Predeclaration: Gate-4's disposition branches, and the D2 fraction-of-ceiling

**Posted 2026-08-08T12:45Z.** Job `56445883` (the nominal re-run) is RUNNING with ~11h of wall and projects
to finish **~17:55Z**, so this is written **before the result exists**. That is the entire point of the
document: Joseph's instruction was *"predeclare the branch now, before the re-run lands, so the disposition
isn't fitted to the result."*

**Recorded state at posting time**, so a later reader can confirm nothing here was informed by the outcome:

    56445883   RUNNING on nid002172, 38:42 elapsed at 12:35:54Z, 11:21:18 wall remaining
    artifact clock  0 of 6 checkpoint pkls; iter0_step1.weights.h5 present
    *_final.weights.h5   0 present  (they only appear after Unfold() returns)
    Gate A/B on the SUPERSEDED artifact: A bit-exact, B(ii) exact, B(i) FAILED at max rel dev 0.866

---

## 1. Gate-4 disposition — the three branches, fixed now

Neither Joseph nor I decide Gate-4 today. These are the branches, and whichever fires is the disposition:

| branch | condition | Gate-4 disposition |
|---|---|---|
| **A** | Gate B(i) **passes** on the re-run's artifact and D2 recovery is the **only** remaining red leg | Gate-4's disposition is decided by §2 — a re-specified D2 criterion either clears it or does not. No separate judgement. |
| **B** | Gate B(i) **also fails** on the re-run | Gate-4 stays **red on grounds independent of D2**, and §2 becomes **moot for this purpose** — the checkpoint provenance is broken again and no criterion argument can rescue it. |
| **C** | either of the above, always | **No product is quoted while any leg is red.** |

Branch B is the one worth naming explicitly: if the BEN-043 fix did not take, the correct response is *not*
to fall back on the D2 re-specification as a way to get a green gate. That would be exactly the
fitted-to-the-result reasoning this document exists to prevent.

**What "B(i) passes" means, pinned:** `gate_ab_push_provenance.py` reports `Bi_pass: true` at its default
`--tol-onshell 1e-6`, on a receipt written to a **run-specific path** so the 56381674-era receipt survives.
The tolerance is not to be raised; if the deviation lands between 1e-6 and 1e-3 that is branch B with a
note, not a pass.

---

## 2. The D2 fraction of the acceptance-limited ceiling

### 2.1 The choice, and the argument that produced it

**Predeclared fraction: `f = 0.80`. Criterion: `recovery >= 0.80 x ceiling(k)`.**
At `k = 3` the ceiling is `0.618228`, so the threshold is **`0.494582`**.

**The argument, stated without reference to the measured value.** The defect identified in CLM-012 is in
*what the bar is a fraction of*, not in *how stringent the campaign chose to be*. The existing criterion
declares two budgets:

    residual_over_gap_max = 0.20     how much of the gap may be lost to the ESTIMATOR
    floor_over_gap_max    = 0.10     how much of the gap may be attributed to SAMPLING

Re-referencing the **estimator** budget — 0.20, i.e. `f = 0.80` — to the achievable ceiling changes exactly
one thing: the reference point. It preserves the stringency the campaign actually chose, and it is the
minimal repair. Any other fraction changes two things where one is warranted, and the second would be
unanchored.

**The alternative I considered and rejected: `f = 0.90`,** on the argument that the estimator should come
within the same 10% of its ceiling that the criterion already allows sampling. **Rejected as a category
error:** `floor_over_gap_max = 0.10` bounds *noise*, not estimator quality. Borrowing a noise budget to
bound an estimator is precisely the kind of cross-unit reuse BEN-042/044/045/071 are about. For the record
it would give a threshold of `0.556405`.

### 2.2 The honesty limit of this predeclaration, stated because it is real

**A genuinely blind predeclaration was no longer available to me.** I already knew the measured ratio
(0.884549) when I wrote §2.1, so I cannot claim the fraction was chosen without knowledge of the answer.
What I can do, and have:

- the argument in §2.1 references only the criterion's own two published budgets, never 0.8845;
- every candidate fraction is tabulated below so the choice is auditable rather than asserted;
- and the blind pick is **delegated**: the independent re-derivation required by condition (d) is being
  asked to choose the fraction from the principled question alone, **without being shown the measured
  recovery, the ceiling, or this section.** If that delegate picks a fraction the estimator fails, that is
  the answer and this section is superseded.

| f | threshold | vs measured 0.546853 |
|---|---|---|
| 0.80 | 0.494582 | PASS by +0.052271 |
| 0.85 | 0.525494 | PASS by +0.021359 |
| **0.90** | **0.556405** | **FAIL by −0.009552** |
| 0.95 | 0.587317 | FAIL by −0.040464 |
| 0.9541 (`1 − floor/gap`) | 0.589866 | FAIL by −0.043013 |

The crossover sits between 0.85 and 0.90 — i.e. **at the measured value itself**, which is exactly why the
fraction had to come from an argument and why the delegate's blind pick matters more than mine.

### 2.3 Criterion text, meeting conditions (b) and (c)

> **D2 powered-closure recovery (re-specified 2026-08-08).** Require
> `recovery >= 0.80 x ceiling(k)`, where `ceiling(k)` is the acceptance-limited reference computed by
> `nd-unfolding/pet/d2_acceptance_oracle.py` as the **tilt-weighted** per-cell dilution response
> `E_w[1-(1-a_b)^k]` with `w_b = |h_target − h_prior|`, from
> `products/pet/fullevent_fps/acceptance_map_fullevent_fps.json`'s
> `acceptance_cells_pt_major`. At `k = 3`, `ceiling = 0.618228` and the threshold is `0.494582`.
>
> **The weighting is part of the definition, not an implementation detail.** The same per-cell curve reads
> `0.633208` tilt-weighted and `0.609475` truth-mass-weighted (the map's own
> `ideal_recovery_percell_truthmass_weighted_by_k`) — a 3.7% difference. An unpinned criterion inherits
> BEN-045.
>
> **This is a specification correction, not a statement of impossibility.** The dilution curve assumes step
> 2 resolves cells independently; `omnifold.py:218-220` evaluates the truth classifier on all `pass_gen`
> rows, so a smooth learner can transport the injected `f(pT)` across cells and **exceed** this curve —
> BEN-038 measured the top acceptance band overshooting at `E_w[r] = 1.0333`. The curve is therefore a
> **reference this estimator operates below** (measured mean response `0.631286` against the curve's
> `0.633208`), **not a bound**, and reaching the original `0.80` absolute would require a cross-cell
> transport gain that **has never been demonstrated here**. The re-specification does not claim `0.80` is
> unreachable; it claims `0.80` was set against the wrong reference.
>
> **An unexplained estimator shortfall remains, and this criterion does not absorb it.** Of the original
> `0.2531` gap to `0.80`, `0.0714` (**28.2%**) is the estimator's own deficiency — it reaches `88.45%` of
> the ceiling and the missing `11.55%` is **not explained** by acceptance, sampling, iteration count,
> training budget or seed. It is tracked as a separate open item and must not be read as retired by this
> re-specification.

---

## 3. What this document does not do

- It does not promote CLM-012 past `VERIFIED-NUMERIC`. Condition (d) requires one independent
  re-derivation first, and by this campaign's own rule worker agreement is not verification.
- It does not touch any threshold in code. `recovery_min = 0.80` is untouched in
  `closure_powered_truth_reweight.py`; a re-specification lands only after the delegate reports and Joseph
  rules.
- It does not decide Gate-4. §1 fixes the branches; the re-run picks one.
