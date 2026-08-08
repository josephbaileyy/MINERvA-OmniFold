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
> **An estimator shortfall remains, this criterion does not absorb it, and it is now LOCATED rather than
> merely unexplained (corrected 2026-08-08 after independent re-derivation).** Of the original `0.2531` gap
> to `0.80`, `0.0714` (**28.2%**) is the estimator's own deficiency — it reaches `88.45%` of the ceiling.
> But that deficiency is **~98% per-cell DISPERSION charged by the criterion's absolute value, not response
> quality**: of the `0.086355` between ceiling and measured, the scatter penalty is `0.084433` (**97.8%**)
> and the signed response deficit is `0.001922` (2.2%). So the signed response sits essentially *at*
> ceiling. What remains genuinely unexplained is why the dispersion is that large — and it is not reducible
> by budget, seed or iteration count. Tracked as a separate open item; must not be read as retired by this
> re-specification, and must not be described as "estimator response quality".

---

## 3. What this document does not do

- It does not promote CLM-012 past `VERIFIED-NUMERIC`. Condition (d) requires one independent
  re-derivation first, and by this campaign's own rule worker agreement is not verification.
- It does not touch any threshold in code. `recovery_min = 0.80` is untouched in
  `closure_powered_truth_reweight.py`; a re-specification lands only after the delegate reports and Joseph
  rules.
- It does not decide Gate-4. §1 fixes the branches; the re-run picks one.

---

## 4. AMENDMENT 2026-08-08T13:00Z — the blind delegate's pick, and three conditions I had missed

The delegated blind pick (condition (a)) has reported. **It chose `f = 0.80` independently**, with no repo
access and no sight of the measured recovery, the ceiling, or §2. It reached it from the same anchor —
`residual_over_gap_max = 0.20` was always a tolerance on *estimator error* and only its denominator was
defective — and put the point more precisely than I did:

> *"`0.20` was a tolerance on estimator error accidentally denominated in estimator-error-plus-impossibility.
> Rebasing it onto `gap * ceiling(k)` restores the meaning the threshold was written to have."*

**What that agreement is and is not worth.** One delegate agreeing with me is not verification — this
campaign's own rule, and it applies to me. What makes it informative is narrower and specific: the delegate
could not see the answer, so the agreement rules out the one failure mode the predeclaration was written to
guard against, namely that `0.80` was reverse-engineered from `0.8845`. It does not make `0.80` correct.

### It sharpened the rejection of f = 0.90 beyond my version

I rejected 0.90 as a *category error* (a noise budget reused as an estimator budget). The delegate identified
it as a **units error**: `floor_over_gap_max` is denominated in `gap` while `f` is denominated in
`gap * ceiling`, so netting one against the other is a units mismatch dressed as a derivation — and the floor
is **already checked separately**, so folding it into `f` double-counts it. That is a better statement of the
same objection and is the correct one to carry forward.

### And it produced a refinement worth its own decision

> *"If the sampling floor is judged to belong anywhere in this criterion, it belongs in the CEILING:
> `recovery >= f * (ceiling(k) - floor/gap)`, since the floor is a second irreducible loss that is
> pre-computable from the sample without running the estimator."*

That is a genuinely better idea than anything in §2 and it **leaves `f = 0.80` either way**. Recorded as a
**separate, deferred decision for Joseph** — it would tighten the criterion (ceiling `0.618228 → 0.572352`
at `floor/gap = 0.045876`, threshold `0.494582 → 0.457882`), and adopting it in the same edit as the
reference-point repair would be the two-changes-at-once error this document exists to avoid.

### Three adoption conditions, two of which I had not stated

1. **`k` and the acceptances entering `ceiling(k)` must be pinned BEFORE the estimator's output is looked
   at** — because `ceiling(k)` rises with `k`, so the bar rises with `k`, which is self-consistent only if
   `k` is *declared* rather than *selected*. **Verified satisfied, not assumed:** `k = 3` is
   `NOMINAL_SEED_POLICY["niter"]` (`train_fullevent_nominal.py:51`) and `validate_pet_nominal_gate4.py:804`
   compares the artifact's policy against `FROZEN`, rejecting drift; and the acceptances come from the
   committed map, which pins the dump at `fa6b346316024216…`. So neither `k` nor `a_b` is selectable after
   the fact. I had stated `k = 3` without stating that it must not be selectable — the delegate was right
   to raise it.
2. **`ceiling(k)` and the RAW recovery must be reported next to every pass/fail.** After this change the
   criterion certifies *"the estimator realised 80% of the recovery this observable's acceptance permits,"*
   **not** *"the estimator recovered 80% of the injected distortion."* A low ceiling is itself a finding
   about the information content of the measurement and belongs in the note as a caveat — **not absorbed
   into a denominator where it silently makes a gate easier.** This is the same protection Joseph asked for
   around the 28.2% shortfall, arrived at independently, and it is now part of the criterion.
3. **`f` must remain a declared constant**, never data-dependent; measured quantities belong on the target
   side (`ceiling`), computed from MC acceptances rather than from the estimator's own output, so the
   criterion stays pre-registerable.
4. **ADDED 2026-08-08 from the independent re-derivation: the INJECTION must be pinned alongside `k` and the
   acceptances.** The ceiling is a property of (detector × injection × weighting), not of the detector: the
   same 285 cells give `0.609475` truth-mass-weighted through `0.776110` uniform, and re-injections at
   amplitude `−0.35 / +0.35 / +0.70` give `0.611760 / 0.628361 / 0.642253` — **±2 pp with the injected
   shape**. A criterion whose bar is computed from the probe must recompute the ceiling per injection and
   declare the injection with it, or the bar becomes probe-dependent. This is a governance condition on the
   re-specification, and it is Joseph's to weigh: it is the strongest argument *against* re-specifying
   against a computed ceiling at all.

`gap_min = 0.15` and `floor_over_gap_max = 0.10` stay untouched and stay denominated in `gap`: they are
preconditions on whether the *test* is informative, not claims about estimator performance, so the
reference-point defect does not reach them. That is the delegate's reasoning and I agree with it.

**Still outstanding before CLM-012 moves past `VERIFIED-NUMERIC`:** the independent re-derivation of the
four numbers (condition (d)) has not reported yet. Nothing here promotes the claim.

