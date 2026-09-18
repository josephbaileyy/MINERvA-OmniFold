# `D-RESOURCE` — STANDING AUTHORIZATION, the required scalar-5D deliverable path

**This is the record `SPEC` §4 row 19 names and says does not exist** (*"`D-RESOURCE` — an exact
resource authorization naming a Z run (`R5`)… **NO — it does not exist**"*), cited again at
`SPEC:1901`, `:2814`, `:3103`, `:3707`, `:3813`, and required by `D3`'s fourth prerequisite. It
exists now. **Authority: Joseph, 2026-09-18, in his own turn.**

**CITABLE FOR:** the objective, the compute posture, and the nine rulings below.
**NOT CITABLE FOR:** adoption, publication submission, any optional claim, or any threshold not
stated here.

---

## 0. THE OBJECTIVE — written here so no lane re-derives it from a packet

> An **adopted scalar-5D covariance**; the **required verified projections with correctly paired
> central values**; **synchronized note / primer / paper**. **Submission is Joseph's act.**

Every ruling below serves that and nothing else.

## 1. COMPUTE POSTURE

**Pre-approved for anything on the required deliverable path** (the §2 blocker table of
`DECISION-PACKET-20260918-scalar5d-publication-blockers.md`): **run it, record it, report
afterward. Do not pause to ask for an allocation on that path.**

**Optional work still requires a separate ask.** This is deliberately not a blanket approval.

Unchanged and binding: `R5`'s ceilings (`500` GPU / `500` CPU task-hours, `t0 2026-09-02T13:44:27Z`,
stop `2026-09-30`); per-submission accounting and admission via `r5_meter.py`; reservations priced as
**enforced cap × tasks**, never a measured actual; one corrective resubmission per stage after a
diagnosed defect, verified repair and fresh admission; automatic requeue disabled.

## 2. THE RULINGS

| # | ruling |
|---|---|
| **1** | **SCOPE AMENDMENT — APPROVED.** The required deliverable set **excludes the generator significance**; the significance is a separate, later, **optional** claim. `main_paper.tex:49-51` already defers it. Deferred with it and **not** on the required path: `y_gen`, `N`σ, the 12-cell χ², the retained-subspace rule, `rcond`, any pseudoinverse, the first-order statistic, and the conclusion-flip `τ`. |
| **2** | **CAMPAIGN — `k₁` DECLINED. The `158.25` GPU / `262.00` CPU reservation is NOT approved and is RELEASED.** Nothing required needs `N`, and `N` is what that campaign buys. **Not to be re-proposed as part of the required path.** |
| **3** | **`SPEC` §3.7d — RULING (b). ADD `s_proj`.** Answer (a) withholds the licence for marginalization and projection, and projections are a required deliverable, so (a) was never available. **It stays a requirement, not a caveat.** |
| **4** | **FUNCTIONAL SET — APPROVED:** the rows of `project_cov_nd.py`'s `M`, plus the all-ones vector. It **dissolves** the region question rather than answering it. The earlier corner-integral criterion is a strictly weaker special case. |
| **5** | **δ = 5% — APPROVED.** `δ_proj = δ_med = δ_agg = 5%`, a **direct movement bound, never quadrature**. Ground: a drift below the `~5.6%` precision the 160-throw ensemble already imposes on `σ` is not resolvable against the number it would modify; at `10%` the arbitrary seed would be `1.78×` the ensemble's own smearing. **Coverage:** 100% on bins entering a quoted projection, **≥99%** on the full reported support, **every failing bin enumerated in the receipt and never absorbed.** |
| **6** | **CAUSES — C1, C2, C4, C5, C6, C7 APPROVED as recommended; R5 approved as documentation and verification with no recomputation.** Detail in §3. |
| **7** | **§6.4 NULL ROUTE — P0 first; P2 not before P0 returns; the exception is APPROVED AS DRAFTED AND HELD, not executed.** Order: **P0 → if needed P2 → only if bitwise identity is unreachable, the exception.** |
| **8** | **PINNING — RESERVED, reaffirmed.** Do **not** apply `deterministic` / `force_row_wise` / `num_threads` to `make_estimators`. A material estimator change. **Not to be routed around because the null row is live.** |
| **9** | **ORDER FIXED:** C1–C7 complete → NULL resolved → **ADOPT (Joseph's act)** → PROJ re-run on the adopted trunk with `--run-class publication` → DOCS re-verified. **No step waits on anything optional.** |

**Throughout: no assembly of incomplete members. 20 of 21 block tasks is not a member.**

## 3. THE CAUSE DISPOSITIONS, as ruled

- **C1** — tolerance-free **disclosure**, `≈0.03` CPU task-h. On the required path, so authorized.
- **C2** — wording is *"inherits a tolerance with a stated derivation and an owner"*, **not**
  *"not chosen"*. Create `cause2_f7_margin` **withheld**; the margin comes back to Joseph.
- **C4** — amend `SPEC:1237` from *"condition 4"* to *"condition 3"*, then the print.
- **C5** — **closed as not-falsified, scoped to the 15 traced modules.**
- **C6** — **REUSE**, with the accepted risk named: **"inputs consistent but unproven."** Both
  withdrawals stand: observed inventory is not proven producing inputs, and **absence of a scheduler
  record is not proof of interactive execution** — the honest statement is that the producing act has
  no scheduler record I could find. Regeneration would not recover this object's provenance.
- **C7** — **closed as sufficient**, on the twice-measured 45-band partition.
- **R5** — amend `ESTIMATOR_REGISTRY:29` to the **consumed** file and record **both** `√tr`.

## 4. ANSWER TO THE QUESTION BACK (§8) — and P0 IS ALREADY DONE

**P0 was executed at `1405caad`, before this exchange.** Source only, zero compute, no payload. I am
reporting it rather than re-running it.

**P0's RESULT — the unfavourable branch of its two outcomes:**

> **The pair IS like-for-like.** `unified_throw_cov.py:846` takes `base = x_cv[rep]`; `:1011` calls
> `_xsec_for_weights(d, edges, w_truth, w_reco, td_cv, args.iters, args.estimator_seed)` — **identical
> arguments, same function, same process.** There is no argument difference for the deviation to come
> from, so `4.452e-14` is **genuine within-process nondeterminism**. The launcher's *"--null repeats
> CV at the identical seed and must be zero"* is **not mis-stated — it is VIOLATED.**
>
> **And the guard cannot fire.** `:1019`'s `tol = 1e-12 * max(‖base‖, 1.0)` clamps to an **absolute**
> `1e-12` against an absolute difference norm on a vector of order `1e-37`: **slack `2.25e38×`.** The
> check that exists to refuse a non-deterministic re-unfold **cannot fail on this object**, which is
> why a violated assertion reached production unremarked.
>
> **What P0 does NOT establish:** any cause. It establishes that the pair is like-for-like, the
> deviation is therefore real, and the guard cannot see it.

**IS P0 SELF-CONTAINED? YES.** It read preserved receipts and source only. **It does not depend on
`58524334` in any way** — that probe is *downstream* of P0, not an input to it, and P0 completed
before the probe was written.

**BUT THE NULL RULING IS NOT SELF-CONTAINED, AND MY TABLE DID NOT SHOW IT.** The dependency, drawn:

    NULL ruling
      |
      +-- route 1: a tolerance `epsilon`        -> CLOSED, all five candidate routes (packet 2.1)
      |
      +-- route 2: BITWISE IDENTITY
            |
            +-- is the deviation real?          -> P0.  SELF-CONTAINED. DONE: yes, and the guard is blind.
            |
            +-- is bitwise identity REACHABLE?  -> 58524334.  THE UNDISCLOSED EDGE.
                  |
                  +-- within one process, real bank, historical config -> MEASURED: NO.
                  |     r_null = 4.4311e-14 reproduces the historical 4.4520e-14 (ratio 0.9953);
                  |     first observed checkpoint divergence at call 0, 3.27e-16 relative.
                  +-- across allocations -> P2 would have tested this. See below.

**So: P0 is self-contained; the NULL *ruling* depends on `58524334` for route 2.** That edge is now
in the record.

**`58524334` HAS COMPLETED** — `ExitCode 0:0`, `2184 s`, `0.607` CPU task-h actual against a `2.00`
reservation.

**CONSEQUENCE FOR P2, following the ordering rule itself.** P2 tests determinism **across
allocations**. Non-identity is now measured **within a single process on the real bank**. Spending
`9.00`–`12.00` CPU task-h on the wider envelope while the narrower one already fails measures the
wrong thing, and a *"not identical"* result would be uninterpretable — **which is exactly the
reasoning P0 produced, and it still holds.** **Recommendation: P2 is not needed.** Not requested.

**WHAT THAT LEAVES.** Under the configuration space permitted here — pinning reserved — **bitwise
identity is unreachable without a material estimator change that is Joseph's.** That is the precise
statement, and it is the condition the order names for the exception becoming live. **Pinning is not
proposed as the remedy and §8 is not routed around.**

⚠ **Not established by any of the above:** a mechanism. `58524334` does not separate thread
scheduling from memory layout, library dispatch, or reduction order, and call 0 is the first
*observed* checkpoint rather than the first arithmetic difference.

## 5. THE PROPAGATION TEST — the defect was real, one layer further on

**The question:** does `publication-under-exception` propagate into the output metadata of the M1
projection, or only the source's?

1. **Into M1's own output: YES.** `project_cov_nd.py` writes `runClass`, `runClassStatus` and
   `acceptanceQuestion` as objects **inside the ROOT product**, so the token is in the file and
   survives a rename. Asserted by test.
2. **A DEFECT WAS FOUND AND FIXED.** `_source_metadata` returned `{}` for **every non-npz source**,
   so a projection *of* a projection lost everything: the `adoptable: false` guard did not fire, the
   receipt's `src_metadata` was empty, and a marker-carrying product could be re-declared at higher
   standing. It now reads the ROOT markers back, and a **standing rule** refuses any derived product
   that claims more standing than its source (`diagnostic 0 < UNDECLARED 1 < candidate 2 <
   publication-under-exception 3 < publication 4`). A marker-free ROOT file returns `{}` and is
   unconstrained, so no pre-existing caller breaks.
3. ⚠ **THE SPECIFIC CHAIN NAMED DOES NOT GO THROUGH THIS PROJECTOR, and the real gap was at the
   CONSUMER.** `project_cov_nd.py` requires a source on the 5D `AXIS_EDGES` grid with an
   `hXSecND_flat` CV; M1's output is a 42-cell object with `hCV_marginal`. So M1 → 2D/3D is not a
   path here. **The gap was in `rank6_significance.py`, which never read the covariance's class at
   all** — its `status` was the hardcoded string *"CANDIDATE — nothing here is approved"*, referring
   to **itself**, never to its input. A significance computed from an excepted covariance would have
   produced a receipt with **no trace of the exception**. That is *"a downstream consumer sees a
   clean covariance"*, located. **Closed:** the consumer now reads `runClass`, records
   `input_run_class` in its receipt, derives its `status` from it, and **refuses (`rc 8`)** to present
   an unqualified result from a non-`publication` input unless the caller acknowledges it
   explicitly — a criterion, liftable by declaration, not a prohibition. **An absent class counts as
   unacknowledged: absence of a claim is not a claim of adoptability.**

**74 tests across the three suites. Mutation-verified both halves:** restoring `_source_metadata`'s
blindness fails the read-back test; disabling the consumer's refusal fails two.
⚠ Adding `rc 8` broke **all 15** existing consumer tests at once — the guard-fires-on-every-correct-run
signature — but the guard is right and the fixtures were making an unqualified claim by omission.
**Defaulting the field to `publication` would have asserted adoptability by omission**, which is the
defect `rc 8` exists to stop. The fixtures now declare their class.

## 6. RELEASED

The `158.25` GPU / `262.00` CPU one-additional-member reservation is **released**. It was never
submitted, so nothing is cancelled; it is struck from the required path and will not be re-proposed
there.
