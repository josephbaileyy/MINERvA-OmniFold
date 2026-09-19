# AMENDMENT — `SPEC` §6.4, a candidate-specific null clause, exhausted by one use

**EXECUTED 2026-09-18** on Joseph's ruling: *"the NULL row resolves to the §6.4 exception, and you
may now execute it — after SRC_COV, not before."* Approved as drafted in
`DECISION-PACKET-20260918-scalar5d-publication-blockers.md` §12.1 and held unexecuted until now.

**This amends `SPEC` §6.4 and nothing else. It does not revise `SPEC`, which is FROZEN at rev. 22.**
It adopts nothing, grades nothing, and moves no count.

---

## 1. HOW THE ROUTE RESOLVED — the prior rule firing, not a later convenience

`SPEC` §6.4's order was **P0 → if needed P2 → only if bitwise identity is unreachable, the
exception.**

**P0 is self-contained and was completed at `1405caad`**; `58524334` measured its subject.
`PACKET-20260918-scalar5d-completion-inventory-and-null-route.md` **§2.4 predeclared both
branches before the measurement existed**:

> *"if it is like-for-like, the pinned design does **not** deliver determinism within a single
> process and the arm-7 experiment would fail — **so P2's cost (repriced to `9.00`–`12.00`) should
> not be spent until P0 returns.**"*

**P0 returned the like-for-like branch.** First checkpoint divergence at **call 0** (`3.27e-16`);
endpoint not identical; `x_cv` differing **across invocations** at `5.33e-15`. The pair is
like-for-like, so the predeclared consequence applies as written: **the pinned design does not
deliver determinism within a single process, the arm-7 experiment would fail, and P2 is not run.**

> **P2 IS NOT AUTHORIZED and its `9.00`–`12.00` CPU task-hours are NOT spent.** This is the
> predeclared branch resolving, recorded so it is visibly the prior rule firing.

⚠ **WHAT WAS SHOWN, AND WHAT WAS NOT.** An earlier version of this record said bitwise identity is
**unreachable**. That is **overclaimed and is withdrawn.** The probe tested the **historical
unpinned configuration**; it does not establish that the **pinned** configuration fails. P0's
outcome licensed **deferring P2** — which is what §2.4 predeclared and what was done — not proving
impossibility.

**The premise this clause rests on, restated as what the evidence supports:** every route to a
**predeclared** `ε` is closed *for an object already built*, because the tolerance form requires a
bound fixed before production; and the route that would sidestep `ε` by demonstrating bitwise
identity is **not available on the evidence in hand**, because the only configuration measured is
the historical unpinned one and the pinned alternative requires the estimator change Joseph
reserves. **"Not demonstrated on the evidence in hand" is weaker than "impossible", and the weaker
statement is the true one.**

## 2. THE AMENDMENT

**§6.4 is unchanged in form and in requirement.** Z's fixed-seed null bound remains scale-relative
and required to be fixed before production, its value justified by precision and sensitivity
controls established before implementation and not selected from a favourable production result.
**The G precedent is unchanged.**

**ADDED — a candidate-specific clause, exhausted by one use.** For the single product
`sha256 3d7465f66fbe66b0dfcf09b6fc51249f227fb33e97ae40bc78dda90275e918c5`
(`uq_5d/z_pilot_20260916_a5/z-cv.npz`, `variant: "cv"`) only:

**(a)** `M(i)` remains **`UNRESOLVED`**, with `reject_conditions` retaining **`4c`** and
`branch = None`. The recorded reason remains the **predeclaration failure**. *This clause is not
altered by (b) or (c), and no later act erases it.*

**(b)** A retrospective scale-relative **assessment** may be recorded. **It carries no grade
token.** G's `1.31e-12` is **context for scale only and is not a threshold**; Z's value being
smaller is **not a pass**.

> **THE MEASUREMENT, PER BIN — REPORTED WITH NO COMPARATOR.** On the persisted `x_cv` / `x_cv2`
> and the support predicate, 10694 reported bins, zero new compute:
>
> | | |
> |---|---|
> | global `r_null = ‖x₂−x₁‖/‖x₁‖` | `4.452000e-14`, reproducing the historical value exactly |
> | **max per-bin `\|Δx\|/x`** | **`1.755272e-12`** |
> | 99.9th percentile / median | `1.318750e-12` / `6.341524e-14` |
> | bins above `1e-10` / above `1e-11` | **0** / **0** |
>
> **SMALL BINS ARE SYSTEMATICALLY LESS STABLE, and that is stated rather than worked around.**
> Spearman `ρ(x_cv, rel) = −0.3103`, `p = 2.5e-237`. Median `rel` by size decile runs
> `1.325e-13 → 3.378e-14` from smallest to largest and max `rel` runs `1.755e-12 → 2.848e-13`; the
> **worst bin in the product sits at the 5.4th percentile of bin size.** ⚠ *The trend is clear but
> **not monotone**: decile 3 exceeds decile 2 and decile 7 exceeds decile 6. Described as a trend,
> which is what the data supports.*
>
> ⚠ **STRUCK — a claim of mine that was false.** An earlier version said *"the smallest reported bin
> is among the most stable."* It is at the **41.3rd percentile**, with **4419 of 10694 bins strictly
> more stable**. The number quoted beside it was right and the adjective was not, and citing the
> single smallest bin as reassurance drew a point from the **least-stable end** of a trend I had not
> yet measured. Nobody intended it; it is the shape of selecting the favourable point.
>
> **THE CONCERN IS CLOSED BY MAGNITUDE, NOT BY ABSENCE.** The feared shape was `rel ≈ 4.4e2` in one
> small bin — the case a global L2 ratio cannot exclude. The worst bin observed anywhere is
> `1.755e-12`: **14.4 orders of magnitude below it**, with **zero bins above `1e-11`.** That rebuts
> the block without denying the trend and without resting on any single bin.
>
> ⚠ **NO COMPARATOR IS ATTACHED, DELIBERATELY, AND TWO WERE TRIED AND WITHDRAWN.** First `δ = 5%` —
> invalid, since `r_null` is a relative change in the CV **vector** and `δ` bounds movement of an
> estimated **σ**. Then *"five significant figures at which central values are quoted"* — **also
> withdrawn, and worse: it is the BARRED route.** `SPEC` §6.8's `D2` row states it verbatim,
> *"applying the printed median's precision to it is a new tolerance choice, not a consequence of
> that summary's formatting"*, and `D1` records the half-display-unit rule as **factually wrong**
> and withdrew the thresholds it produced (`SPEC:3909`, `:2131`, `:2124`). **Three withdrawn numbers
> in this campaign already trace to that rule.** So the distribution is reported and nothing is
> compared to it. **This exception is bound to one digest and generalizes to nothing; it does not
> need an acceptance boundary, and attaching one would re-open "how much movement is scientifically
> acceptable" — the question `θ` was closed on and which remains open.**
>
> **The measurement is itself stable:** `4.4311e-14` against the historical `4.4520e-14`, ratio
> **`0.9953`**.
>
> **THEN THE REASON THE CRITERION IS UNRESOLVABLE.** Its **predeclared-tolerance form cannot be
> constructed for an object already built** — a bound fixed *before* production cannot be fixed
> *after* it — **not because reproducibility is in doubt.** Stated in this order deliberately: the
> unresolvability is a defect in the criterion's applicability to this object and must not be read
> as a reservation about the object's reproducibility.

**(c)** **Adoption of this digest may proceed notwithstanding (a)** if and only if the remaining
required evidence is complete and independently verified. **(c) is a permission to decide, not a
decision, and not evidence.**

## 3. SCOPE — one digest, and nothing generalizes

The clause names **one digest**. Any other product — **including a future rebuild of the same
object** — is governed by §6.4 unamended. **The clause cannot be cited for a second product**, and
there is nothing here for a later lane to inherit. Digest scoping is what prevents generalization:
the exception attaches to bytes, not to a decision type.

`null_epsilon` **remains WITHHELD** in `z_contract.py`. This clause makes it **moot for the required
path; it does not supply it.** A later product needing §6.4 satisfied still needs `ε`.

## 4. WHAT THIS DOES NOT DO

- It **does not adopt**. Adoption is Joseph's act and remains conditional on the remaining required
  evidence and its independent verification.
- It **does not edit the candidate's metadata.** `adoptable: false` and
  `scientific_acceptance: NON-PASSING` continue verbatim into every product's receipt.
- It **is not a force flag.** `project_cov_nd.py --adoption-exception` requires a record containing
  the **measured** sha256 of the source; `--force`, `--no-verify`, `--skip-adoption` and
  `MNV_FORCE` are absent from the module, asserted by test.
- The resulting class is the distinct token **`publication-under-exception`**, so no reader can
  mistake such a product for one projected from an adoptable trunk. **The exception unblocks the
  route; it does not supply the evidence.**

**`AGENTS.md:29` summary, carrying no authorizing force:** the corrected scalar 5D candidates remain
`QUARANTINED`; one named digest additionally carries a candidate-specific §6.4 clause recorded here,
which does not release the row and does not alter the quarantine for anything else.
