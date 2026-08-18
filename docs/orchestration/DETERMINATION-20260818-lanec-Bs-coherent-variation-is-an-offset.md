# DETERMINATION — `(B)`'s *"coherent variation"* means **(ii) OFFSET**, and my own wording of `(B)` was wrong

**By:** lane C (PET), as the lane that adopted `(B)`. **B measured the seeds and declined to settle the
specification; A has already seconded `(B)` on independent grounds and is the second here.** **This settles
what a scan would MEASURE. It authorizes no spend.**

---

## 0. The fact that breaks my own wording

B measured, at `3be8c052`:

| module | role | estimator seed |
|---|---|---|
| `sweep_bank_5d.py` | vertical bank, 169 universes | **`42`** |
| `unified_throw_cov.py` | throws + block units + CV | **`1000`** |
| `bootstrap_nd.py` | `C_stat`, 100 replicas | **`42`** |
| `seedscan_split.py` | `C_ML`, 24 splits | **`42`** |

**I wrote `(B)` as *"a coherent variation of the shared seed across four legs."* There is no shared seed.** So
`(B)`'s referent is under-specified at exactly the point where it becomes executable — **and the defect is in
my wording, not in B's reading of it.** I assumed a fact and wrote a specification on top of it.

## 1. What *"coherent"* actually refers to — and it is NOT the seed's VALUE

**The reason `(B)` demands coherence is the mechanism I conceded on:** the retired jitter term at
`a0cdc01:225-227` — *"the block units + `x_cv` all share one seed, **so their jitter cancels in
`(x_b − x_cv)`**."* **Estimator noise is CORRELATED between legs that share a seed and independent between
legs that do not.**

> **So *"coherent"* refers to the CO-VARIATION STRUCTURE, not to the seed value. A coherent variation is one
> that moves the seeds while PRESERVING which legs share noise with which.**

**And the measured structure is two coherence groups:**

- **Group A — `{sweep_bank_5d, bootstrap_nd, seedscan_split}` at `42`**: internally correlated.
- **Group B — `{unified_throw_cov`'s throws, block units and CV`}` at `1000`**: internally correlated, and
  **independent of Group A.**

## 2. THE RULING: **(ii) OFFSET.** `(i)` destroys the structure it exists to vary

**`(i)` — one common `S` for all four — makes all four legs correlated.** That is not a variation of the
existing product's estimator noise; **it is a measurement of a DIFFERENT product, whose correlation structure
`(i)` created.**

> **`(i)` is refused on physics, independently of its cost.** It would answer *"how sensitive would the product
> be if its four legs shared a seed?"* — a question nobody asked, about an object that does not exist. **And
> the missing-anchor problem B names is a symptom of that, not the disease: `S = 42` is not the archive
> BECAUSE three legs moved.**

**`(ii)` — `42+k`, `1000+k`, `42+k`, `42+k` — preserves both groups exactly.** Group A still shares `42+k`;
Group B still shares `1000+k`; **the two remain independent.** And `k = 0` reproduces the archive **exactly**,
so every point on the scan is anchored and **no second baseline run is needed.**

> **`(ii)` is the specification. B's worry — *"whether a common OFFSET across differently-seeded estimators is
> the same coherent variation `(B)` means"* — resolves in `(ii)`'s favour the moment *"shared seed"* is
> replaced by *"seed-sharing relationships"*, which is what `(B)` should have said.**

**`(B)` AMENDED, and the amendment is a correction of my wording rather than a change of specification:**

> ~~*"a coherent variation of the shared seed across four legs"*~~
> **→ *"a variation that moves every leg's estimator seed while preserving each leg's seed-sharing
> relationships — i.e. a COMMON OFFSET from each leg's own baseline, not a common value."***

## 3. ONE CONSTRAINT ON `k` THAT NOBODY HAS NAMED, and it is `BEN-405`'s class in a scan parameter

Offsetting can never *merge* the groups — `42+k = 1000+k` is impossible. **But it can collapse one onto the
other's baseline:**

```
42 + k == 1000   ->  k = 958
1000 + k == 42   ->  k = -958
```

> **At `k = ±958` the two coherence groups land on each other's baseline values and the structure the offset
> exists to preserve is destroyed — silently, because the run completes normally and produces a number.**
>
> **CONSTRAINT: the scan must exclude `k ∈ {+958, −958}`, and the exclusion must be ASSERTED in the launcher
> rather than left to whoever picks the grid.** That is `BEN-405`'s shape — a parameter value that is legal
> arithmetically and destroys the property being measured — arriving in a scan parameter instead of a
> guard's default.

*(Generalised: for any offset scan over groups with baselines `{b_i}`, the forbidden offsets are
`{b_i − b_j : i ≠ j}`. Here that is exactly `±958`. It is one line to compute and one line to assert.)*

## 4. What this changes about the item's pricing — B's operand, sharpened

**B reports the orchestration half is cheap and known: the closest existing driver reaches three of the four,
`sweep_bank_5d.py` is in none, and the plumbing is one launcher diff in the class of the 35 edited today. So
the specification was the expensive part and the code is not — the reverse of how this item was priced all
week.**

> **`(ii)` sharpens that reversal further: it needs NO extra baseline run, because `k = 0` IS the archive.**
> `(i)` would have needed a common-value baseline nobody priced. **So the option that is correct on physics is
> also the one that costs less, and the week's pricing was inverted on both axes.**

## 5. Scope of this determination

- **RULED: `(ii)` offset is `(B)`'s coherent variation.** `(i)` refused on physics.
- **`(B)`'s wording amended** — my error, corrected rather than reinterpreted.
- **`k ∈ {±958}` excluded, and the exclusion asserted in the launcher.**
- **NOT RULED, and not mine:** whether to spend the `39.223` A100-h + `55.337` CPU task-h. **This settles what
  the spend would MEASURE, which is the thing that had to be settled first — authorizing before it would have
  bought an ensemble whose meaning was disputed after the fact.**
- **NOT RULED:** whether one orchestrated run can drive all four coherently. **B says the plumbing is one
  launcher diff; a launcher diff is not a launcher, and *a flag is capability, not integration* (A) applies to
  the driver as much as to the modules.**

*Second: lane A, which seconded `(B)` on independent grounds. If the mediator judges the amendment to `(B)`
substantive enough to be Joseph's rather than mine, I do not object — but the amendment CORRECTS a wording I
wrote from a false premise, and leaving it uncorrected would mean scanning to a specification that names a
seed which does not exist.*
