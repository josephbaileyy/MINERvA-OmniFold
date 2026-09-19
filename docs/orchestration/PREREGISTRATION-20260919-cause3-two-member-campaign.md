# PREREGISTRATION 2026-09-19 — `(cause 3, Z)` `M(ii)`, two-member estimator-seed campaign

**CITABLE FOR:** the declared design, boundaries, pass rule, member set and reservations of the
campaign this record precedes.
**NOT CITABLE FOR:** any result. **No job of this campaign has been submitted when this is
committed**, and nothing here grades, adopts or authorizes anything beyond what Joseph's standing
authorization `A1`–`A6` already grants. Gate 2 remains **FAIL**; no scalar-5D covariance is adopted.

The machine-readable form the grader reads is
[`PREREGISTRATION-20260919-cause3-two-member-campaign.json`](PREREGISTRATION-20260919-cause3-two-member-campaign.json).
`z_grade` **requires** it — `--preregistration` has no default — and refuses any `--declared-K`,
graded offset or builder revision that disagrees with it.

## 1. Why this exists and what it binds

`R8`: *"Only a product whose production follows the preregistration commit may be graded PASS or
put forward for adoption, and its null `r_null` must be measured in its own production."* A
declared offset set chosen after seeing the members' offsets is a description, not a
predeclaration, so `K`, the graded offset and the builder revision are fixed here and enforced by
the grader rather than by intention.

| field | value |
|---|---|
| **builder revision** | **`d64257c3947a239f33ad7b33869286f6aab07194`** |
| **declared offset set `K`** | **`{0, 1200}`** |
| **graded offset** | **`0`** — the anchor, at each group's own pinned baseline seed |
| **`S`** | **`1e-3`** (Joseph, `R2`) |
| **`ε`** | **`1e-9`** (`z_contract.null_epsilon`, declared at `43fd8bc5`) |
| **leg set `L`** | **`{s_agg, s_med, s_proj}`**, bounds `0.05` each |
| **pass rule** | branch **3** from `assess()` **and** `r_null ≤ ε` measured in the graded product's own production |
| **digest to be graded** | **deliberately not named** — it does not exist yet, and naming one that did would preregister a result |

## 2. `K = {0, 1200}` — every predicate run, not assumed

| predicate | result |
|---|---|
| pairwise aliasing, `check_offset_grid({g1: 42, g2: 1000}, [0, 1200])` | **`[]`** over **4** checked pairs — non-vacuous |
| clean-offset, `assert_offsets_are_clean` | **passes** |
| sort-safety, `assert_offsets_are_sort_safe` | **passes** |

## 3. The members

### 3a. `k = 0` — the anchor, and the GRADED product

`mii/member_k000000`: seven arms already complete under jobids `57753239` `57753243` `57753244`
`57753245` `57753246` `57753247` `57753248` — **374 / 374 `COMPLETED`, `ExitCode 0:0`**,
re-verified from `sacct` rather than from a launch plan. **All 185 slabs** carry
`(est_seed_offset_declared = 1, est_seed_offset = 0)` with seeds `1000` for group 2 and `42` for
group 1, i.e. each group's own pinned baseline plus zero: *"ran hooked, at the archive anchor,
deliberately."*

**Its combine is re-run at the builder revision**, because its original deploy `7ac0edec` predates
the null-operand writer `d3b6ae2b` and never wrote `hCvExecution{0,1}` / `hCvSupportMask` —
measured, **0 hits against a 2-hit `C_unified` positive control**. The second CV execution is
computed *inside* the combine from the shared bank, so re-running that one task supplies the null
operands `R8` requires without touching a slab.

⚠ **The existing `unified_throw_cov_5d.root` is MOVED ASIDE, never deleted**, with its digest
recorded, on the 2026-08-30 precedent for this same namespace.

### 3b. `k = 1200` — the comparison member

All seven arms, fresh, `MNV_EST_SEED_OFFSET=1200`, at the builder revision.

## 4. Why the `k = 0` arms are NOT re-run, and why that is not a choice

**It is what the campaign's own admission check permits, measured today, not a preference.**

| option | reservation | `r5_meter check` |
|---|---:|---|
| this campaign (`k=1200` fresh + `k=0` combine re-run) | `337.00` CPU / `158.25` GPU | **`rc 0` ADMITTED** |
| both members fresh | `672.00` CPU / `316.50` GPU | **`rc 5` REFUSED — would reach a ceiling** |

R5 headroom at declaration: **`379.31` CPU / `481.48` GPU** of the `500` / `500` ceilings; stop date
`2026-09-30`, not fired. Joseph's `A1` grants `600` CPU / `400` GPU, but `A1` also says *"route
campaign admission normally"*, and **R5 is the binding ceiling** — so two fresh members are not
available at any price this campaign may pay.

**And the confound that reuse leaves behind is stated, with its direction.** The `k = 0` slabs were
produced three weeks before the `k = 1200` slabs will be. Any environment drift between them enters
the comparison and **inflates** the measured spread — it pushes toward an unfavourable result, not
toward a pass. What is *not* left to inference is the code: the numerical path is **measured
identical** (§3a), and **both members' combines run at the same revision**, so the step that
computes `C_unified`, `C_blocksum` and both CV executions is the same code for both.

## 5. Reservations, priced as enforced cap × tasks

| arm | tasks | enforced cap | observed max at `k = 0` | reservation |
|---|---:|---:|---:|---:|
| `boot5dG` | 100 | `0.50` h | `0.18` h | `50.00` GPU |
| `sweep5dBKGrun` | 169 | `0.50` h | `0.18` h | `84.50` GPU |
| `det5dBKG` | 19 | `1.25` h | `0.76` h | `23.75` GPU |
| `ssplit5d` | 24 | `0.75` h | `0.48` h | `18.00` CPU |
| `uthrow5d_runF` | 40 | `4.25` h | `2.67` h | `170.00` CPU |
| `uthrow5d_block` | 21 | **`7.00` h** | **`4.82` h** | `147.00` CPU |
| `uthrow5d_combF` | 1 | `1.00` h | `0.58` h | `1.00` CPU |
| **`k = 1200` total** | **374** | | | **`336.00` CPU / `158.25` GPU** |
| `k = 0` combine re-run | 1 | `1.00` h | `0.58` h | `1.00` CPU |

⚠ **`uthrow5d_block` is capped at `7.00` h and NOT at the packet's recommended `3.00` h.** One of
the `k = 0` member's 21 block tasks ran **`4.82` h** — the next longest was `2.27` h — so the
recommended cap would foreseeably spend the campaign's single corrective resubmission on the first
timeout, and a second slow task **ends the campaign with no member assembled**. `7.00` h is `1.45×`
the observed maximum. Spending more to remove a foreseeable campaign-ending failure is the
direction Joseph's decision rule authorizes.

## 6. What happens after production

1. Both members' downstream stages — the stage-2 universe covariance, the stat and ML covariances,
   the active lateral candidate — then `z_build` per member.
2. `z_grade` with this preregistration, both members, `--graded-offset 0`, and the graded member's
   **own** persisted null operands.
3. Whatever the verdict, it is recorded **once**. `B` in Joseph's terms — an assessable FAIL or a
   null over `ε` — permits **no retries, re-seeding or reconfiguration**.

## 7. What may not change from here

Per Joseph's reservations, once **any** production output of this goal exists: no declared boundary
value, criterion, threshold, reject condition, `S` or `ε` may change. The grader, the boundaries and
this preregistration are all committed **before** the first job is submitted, which is what makes
that promise checkable rather than asserted.

**Co-Authored-By: Claude Opus 5 (1M context)**
