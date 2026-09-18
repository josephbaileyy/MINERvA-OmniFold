# DECISION PACKET — every remaining scalar-5D publication blocker

**CITABLE FOR:** the current blocker set and its recommended dispositions.
**NOT CITABLE FOR:** adoption, criterion approval, or any publication significance. Nothing here is
approved.

**Objective (Joseph's):** an **adopted scalar-5D covariance**; the **required verified projections
with correctly paired central values**; **synchronized note/primer/paper**. Submission is his act.

Supersedes the scattered decision lists in `PLAN-20260918-…` §2/§6/§17/§19 as the *current* view;
those retain the derivations.

---

## 1. ⚠ SCOPE AMENDMENT, PROPOSED EXPLICITLY — the generator significance is OPTIONAL and is not a prerequisite

`main_paper.tex:49-51` already states the deferred item as *"a central-value result; its significance
awaits adoption of a common five-dimensional covariance."* **So the paper's required content is the
localization at central-value level plus quoted uncertainties — not a significance.**

**Everything below that serves only a significance is therefore OPTIONAL and must not gate the
required deliverables:** `y_gen`, `N` (D3's threshold), the 12-cell χ², the retained-subspace rule,
`rcond`, any pseudoinverse, and the conclusion-flip `τ`.

⚠ **I had been treating these as prerequisites. That was a scope error and it lengthened the critical
path.** Proposed amendment, for Joseph's explicit ruling: **the required deliverable set excludes the
generator significance; the significance is a separate, later, optional claim.**

**What does NOT move into "optional":** the correlation-sensitive acceptance leg — see §2 row C3.

---

## 2. THE BLOCKER TABLE — required deliverables only

| # | Blocker | Governing requirement | Existing evidence | Recommended disposition | Smallest remaining action |
|---|---|---|---|---|---|
| **C3** | Cause 3 correlation-sensitive leg | **`SPEC` §3.7d, titled "IT IS A REQUIREMENT, NOT A CAVEAT".** Its Answer (a) states a MET result *"does **not** license the assembled covariance for marginalization, projection, coverage validation"* | §3.7d measured: `I₂` vs `[[1,.9],[.9,1]]` give identical `√Tr` and identical per-bin σ while the sd of their sum/difference move `+37.8%`/`−68.4%`. Both adopted legs return **exactly 0.0** | **ANSWER (b) — ADD `s_proj`.** Answer (a) is unavailable: it explicitly withholds the licence for projection, and projections are a **required** deliverable. `s_proj` is `SPEC`'s own first choice | **Joseph's ruling (a)/(b)**, then declare the functional set and `δ` (§3) |
| **C1** | Cause 1 endpoint-interpolation counterfactual | `z-receipt-cv.json` `causes.1 status UNRESOLVED` | requirement stated; `SPEC` §5.8b prices it at **`≈0.03` CPU task-h** | **Approve as priced** — tolerance-free, it is a disclosure | one bounded run, ~0.03 task-h |
| **C2** | Cause 2 F7 operands, `k` and its source | `causes.2 status UNRESOLVED`; `joint_mean_shift_sha256` present | `F7_FLOOR_MULTIPLE = 2.0` at `uq_math.py:138` is **chosen, with an owner**; both centering variants exist | **Approve**, wording *"inherits a tolerance with a stated derivation and an owner"* — **not** *"not chosen"* | D2: create `cause2_f7_margin`, withheld; declare the margin |
| **C4** | Cause 4 jitter print | `causes.4 status UNRESOLVED` | §2.4's four conditions; the guard enforces **condition 3** (§2.4 item 4's own prose) | **Approve**, and amend `SPEC:1237`'s *"condition 4"* to *"condition 3"* | text amendment; then the print, `≤ 0.5764` task-h |
| **C5** | Cause 5 §6.1 disposition | `SPEC:1238` | falsifier **NEGATIVE** across the 15 modules Z invokes, incl. `adopt_unified_5d.py` | **CLOSE as not-falsified, scoped to the 15 traced modules** | Joseph's ruling. No compute |
| **C6** | Cause 6 stat/ML reuse | audit: *"decide from compatibility evidence rather than assume reruns"* | `combine_cov_nd.py` now records all nine fingerprint fields + realized `n_members` | **REUSE** on one zero-compute footing check | read the nine fields; no compute |
| **C7** | Cause 7 sufficiency | `ESTIMATOR_REGISTRY:29` `#16` five-band **publication gate** | **measured twice, two files:** 45 bands, V 13 / R 27 / A 5, and all four weight-only bands **present in R**; receipt `G5_band_partition exhaustive: true` | **CLOSE as sufficient** | Joseph's ruling. No compute |
| **R5** | Two unified-throw ensembles; registry names a file the chain did not consume | `ESTIMATOR_REGISTRY:29` | **step 2 performed:** receipt records `parent.lineage_status: "UNVERIFIED"` and names the 08-11/12 object as `parent_candidate`, **not a component** | **Documentation + verification, no recomputation** | amend `:29` to the consumed file, record both `√tr` |
| **NULL** | `ε` / `null_epsilon` | `SPEC` §6.4 | every route closed (packet §2.1); receipt: `WITHHELD`, *"Neither B nor S is established"*; `r_null = 4.452e-14`; the guard's `max(‖base‖,1)` clamp makes it inert | **Joseph's §6.4 route ruling.** The §6.4 G precedent — *"the defect is in the guard, not in the product"* — is the live question | his ruling; `58524334` informs the remedy, not the requirement |
| **ADOPT** | Trunk adoption | Joseph's goal; `AGENTS.md` | candidate **exists and verifies** (3/3 digests); construction complete, `adoptable: false`, `NON-PASSING` **because criteria are absent, not because construction failed** — every closure identity exact | **his act**, after C1–C7 | — |
| **PROJ** | Verified projections, paired centrals | `AGENTS.md:27` / `:30` | **diagnostic M1 produced and verified**: `n_empty 0`, `src_cells_dropped 0`, exact symmetry, row order cross-checked, source binding carried | **re-run on the adopted trunk** with `--run-class publication` | one `0.25` task-h run after ADOPT |
| **DOCS** | Synchronized note/primer/paper | Joseph's goal | `RESULT :: PASS`, 26 `.tex`/`.bib` byte-identical, containment green across all three | **re-verify after PROJ's content edits** | one build |

**Nothing in this table requires `y_gen`, `N`, a χ², a pseudoinverse, or a rank choice.**

---

## 3. TOLERANCE RECOMMENDATIONS, DERIVED — not read off observed values

**One ground for all three cause-3 boundaries.** The estimator-seed choice must be a **negligible
contributor to any quoted uncertainty**. Treat a relative drift `δ` in a standard deviation as an
additional component in quadrature; it inflates a quoted `σ` by `√(1+δ²) − 1`:

    delta =  5%  ->  0.125%        delta = 14.2% ->  1.003%
    delta = 10%  ->  0.499%        delta = 20%   ->  1.980%

**RECOMMEND `δ = 10%` for `s_proj`, `s_agg` and the per-bin leg of `s_med`.** Ground: a 10% drift
inflates any quoted uncertainty by **0.50%**, which is negligible against every component in the
budget. ⚠ This is **not** display-derived — `SPEC` rev. 16 withdrew the format-derived `0.0861%` and
the half-display-unit rule, and this uses neither. It reads **no observed drift**, so it is
declarable before the members exist.
⚠ **Residual:** the `0.50%` target is a judgement. It is the *right kind* — a negligibility
threshold on the uncertainty budget — rather than a tolerance fitted to a result.

**`s_med`'s second number, the coverage fraction.** **RECOMMEND: 100% on bins entering any quoted
projection; ≥ 99% on the full reported support, with every failing bin enumerated in the receipt.**
Ground: a bin that enters a quoted number must satisfy the tolerance, while with 10,694 bins a
100% requirement over all of them makes the criterion hostage to one pathological bin — so failures
are **named and counted, never absorbed**.

**`s_proj`'s functional set.** **RECOMMEND `SPEC`'s own: the rows of `project_cov_nd.py`'s `M`, plus
the all-ones vector.** This **reconciles the region question and dissolves it**: the rows of `M` cover
all 42 `(E_avail,W)` cells, so the criterion does not depend on which region the *claim* uses. D5's
region choice affects only the optional significance. My earlier corner-integral criterion is
`s_proj` with a **single** functional — a special case, and strictly weaker.

---

## 4. WITHDRAWALS

1. **`rcond = 1e-5` / retained rank 6, and the first-order statistic, are PROPOSALS, not settled
   engineering choices.** They change the statistical prescription and are therefore scientific.
   **And they are not needed for any required deliverable:** `s_proj` is a **forward** quadratic form
   `√(uᵀ C u)` — **no inversion, no rank choice, no cutoff.** The whole rank/`rcond`/pseudoinverse
   apparatus belongs to the optional significance only.
2. **WITHDRAWN: that eigenvalue ratios of `1.8` and `1.7` establish indistinguishability.** They do
   not. Close eigenvalues make the *eigenvectors within that subspace* poorly determined; they do
   **not** make the eigenvalues unusable, nor the subspace ill-defined. I conflated eigenvalue
   proximity with numerical meaninglessness. The gap structure remains a fact; the inference from it
   does not.
3. **Any approximation must be validated against the exact restricted calculation first.** If the
   first-order statistic is ever wanted, compute the **exact** member-wise restricted `χ²` and
   compare; adopt the approximation only where they agree, and report the disagreement where they do
   not. **No approximation machinery before that comparison.**
4. Previously withdrawn and still withdrawn: the conclusion-flip `τ` as an acceptance criterion; the
   three causal branches for `58524334`; "rank 36" bare; "`M C Mᵀ` averages the negatives out"; and
   the three determinism inferences.

---

## 5. WHAT REMAINS

**Joseph's rulings:** §3.7d (a)/(b) — recommended **(b)**; `δ = 10%` and the coverage fractions;
`s_proj`'s functional set; C1/C2/C4/C5/C6/C7 dispositions; D2's key and margin; R5's registry
amendment; the §6.4 null route; the §1 **scope amendment**; then ADOPT.

**Running:** `58524334`, the CV-divergence probe. It informs the **reproduction-path remedy** — which
blocker NULL's ruling may rest on — and **no acceptance requirement in §2 depends on it.**

**No further diagnostics are proposed.** A successor experiment would need a specific unresolved
failure it must detect and a named unmet requirement it would resolve; an unexplained mechanism is
not by itself such a requirement.

---

## 6. CORRECTED ENTRIES — 2026-09-18, after Joseph's scope support

Joseph supports excluding optional generator-significance work from the required deliverables and
proceeding toward a correlation-sensitive leg based on the **required projection uses**. **No
numerical threshold and no adoption is approved.**

### 6.1 ⚠ THE TOLERANCE ARGUMENT WAS WRONG — quadrature withdrawn

**I wrote that `δ = 10%` "inflates any quoted uncertainty by 0.50%". That is false.** `s_proj` bounds
the **relative change in `√(uᵀ C u)`** — the estimated standard deviation itself. `δ = 10%` permits
the quoted standard deviation to **move by 10%**, full stop. My `√(1+δ²) − 1` step modelled the
seed-to-seed spread as an **independent additional error component added in quadrature**, and
**I gave no justification for that construction.** There is none available: the spread is an
**ambiguity in `σ`**, not a second error beside it. **Withdrawn.**

**THE CORRECT GROUND — how well is `σ` determined already?** Read from the product:
`n_throws = 160`. For an ensemble of that size the estimated variance carries a relative precision
of `√(2/(N−1)) = 11.22%`, so the estimated **standard deviation** carries about half that:

    the quoted sigma is itself determined only to about +/- 5.6% by the finite throw ensemble

**RECOMMEND `δ_proj = 5%`, as a DIRECT movement bound.** Ground: a seed-to-seed drift below `5%` is
**not resolvable against the `5.6%` precision the ensemble already imposes on `σ`**. It reads no
observed drift, uses no display format, and needs no quadrature construction.

**SCIENTIFIC CONSEQUENCE, stated directly.** On the measured corner median `σ/x = 5.81%`:

| `δ` | a quoted `5.81%` could instead read | `δ` ÷ ensemble precision |
|---|---|---|
| `3%` | `5.64%` – `5.98%` | 0.53 |
| **`5%` (recommended)** | **`5.52%` – `6.10%`** | **0.89** |
| `10%` (my earlier figure) | `5.23%` – `6.39%` | **1.78** |

At `δ = 5%` the seed choice stays **below** the ensemble's own smearing, so it is not a
distinguishable contributor to the quoted number. **At `δ = 10%` it is 1.78× the ensemble precision
— the arbitrary seed would become the DOMINANT ambiguity in a published uncertainty**, and a reader
comparing this uncertainty against another measurement's could be misled by an artifact of seed
choice. That is the consequence, and it is why `10%` is too loose.

⚠ **Residual, named:** `√(2/(N−1))` assumes iid normal draws. The 160 throws are
systematic-parameter throws, not iid samples of one quantity, so `5.6%` is an **order-of-magnitude
anchor for the ensemble's resolving power**, not an exact precision. The recommendation is that
`δ` sit below that anchor, not that `δ` equal any particular derived digit.

**`s_med`'s two numbers, on the same ground:** per-bin `δ = 5%`; coverage **100%** on bins entering
a quoted projection and **≥ 99%** on the full reported support, with every failing bin **enumerated**
in the receipt. **`s_agg` (`√Tr`): `δ = 5%`**, and noted as the weakest of the three — an aggregate
over 10,694 bins can hold large per-bin motion at fixed total, which is why it does not stand alone.

### 6.2 CAUSE-3 MEMBER PRODUCTION — RESTORED to the dependency chain

⚠ **My packet §2 omitted this and thereby understated the chain.** Cause 3 cannot be *evaluated*
without members, and `causes.3` requires *"build all members"*. **This is the largest remaining
compute item in the whole programme.**

| | |
|---|---|
| **Family** | **diagonal** (D1), group assignment `{arms 1–4: 42, arms 5–7: 1000}` **fixed at archive values**; offsets `k`. **Do NOT unify the seeds** — `sweep_bank_5d.py:354-356` names that as the trap and says it *"silently re-seeds one of the two"* |
| **Member count** | **RECOMMEND `N = 3` additional members**, not 4 |
| **Cost** | `SPEC` §5.8d, **TRANSFERRED** per-member actuals `54.90` GPU / `86.53` CPU task-h → **`164.7` GPU / `259.6` CPU** at `N = 3`; `219.6` / `346.1` at `N = 4` |
| **Why 3 and not 4** | headroom is `483.99` GPU / `403.31` CPU. `N = 4`'s `346.1` CPU is **86% of remaining CPU headroom before any contingency**, and `SPEC` §5.8e item 1 records a **measured ±60% single-arm CPU swing** (arm 5 went `30.94 → 49.11`). At `N = 4` that swing can break the ceiling; at `N = 3` it cannot |
| **Enforced reservation** | per member, the seven-arm envelope as ratified: arm 2 `8`, arm 5 `60`, arm 6 `40` CPU task-h etc. Reservation is the **enforced cap × tasks**, never a past actual |
| **Stopping conditions** | (i) R5 ceilings `500` GPU / `500` CPU — **hard**; (ii) **stop date `2026-09-30`**; (iii) per-arm ceilings; (iv) one corrective resubmission per stage; (v) **abort the campaign if any member's realized CPU exceeds its arm ceiling**, rather than continuing and re-pricing |
| ⚠ **Schedule risk, and it may bind before the ceiling** | the stop date is **12 days out**, and `SPEC` §5.8e item 6 records that the usable scheduling window was **`16 d 15 h` in two blocks, not the calendar span**. A 3-member campaign at `54.90` GPU task-h per member is feasible on ceiling and **not obviously feasible on the window** |

**Smallest remaining action:** Joseph approves `N = 3`, the family, and the per-arm envelope — then
one bounded campaign request with the accounting and admission already demonstrated.

### 6.3 REQUIRED PROJECTION MAPS AND QUOTED INTEGRALS — the functional set BOUND to them

From P1 (packet §4), with `weight_basis` as the M1 receipt states it: *"entries are the product of
the DROPPED axes' bin widths, so the destination is a DIFFERENTIAL DENSITY in the kept axes."*

| map | destination | cells | writer | quoted? | units of the projected object |
|---|---|---:|---|---|---|
| **M1** | `(E_avail, W)` | **42** | `project_cov_nd.py --keep-axes eavail,W` | **YES — the only quoted map** | `d²σ/dE_avail dW`, cm²/nucleon/GeV² |
| M2 | `(pt, pz, E_avail, q3)` | 10,976 | `p4_project_4d.py` | no — supports reported central values | 4-differential |
| M3 | `E_avail` | 7 | `project_cov_nd.py --keep-axes eavail` | no — marginal anchor | `dσ/dE_avail` |
| M4 | 5D → 3D | per keep-axes | `project_cov_nd.py` | no — marginal anchor | 3-differential |

**Quoted integrals.** Any integral over a set `R` of M1 cells uses **bin-volume weights**
`w_i = Δ(E_avail)_i · Δ(W)_i`, because the projected object is a density. The corner's `E_avail`
widths are `0.4, 0.7, 1.5, 97.0` GeV — differing by more than two orders — so omitting the volumes
is a **large** error, not a refinement.

**THE FUNCTIONAL SET, BOUND:**

    U  =  { the 42 rows of M1 }                        <- one per quoted cell; covers every cell
       U  { the all-ones vector over the 42 }           <- the total
       U  { w_R for each declared quoted integral R }   <- bin-volume weights, one per integral

This is `SPEC` §3.7d's own `s_proj` set (*"the rows of `project_cov_nd.py`'s `M`, plus the all-ones
vector"*) **plus** the integral functionals, which are the additional quoted objects. **It is bound
to the quoted maps, not chosen for convenience**, and it needs **no matrix inversion**.

**THE LIMITED CLAIM THESE CHECKS SUPPORT — and it is narrow:**

> A MET result on `s_proj` over `U` states that **the projected standard deviations of the quoted
> M1 cells, their total, and the declared quoted integrals** did not move by more than `δ` across
> the member family. **It is not evidence about `C_Z`'s full correlation structure** — `|U|` linear
> functionals constrain `|U|` directions of a `10,694²` matrix — **and it is not evidence about any
> significance**, which depends on `C⁻¹` contracted with a residual and weights the spectrum in the
> opposite direction. It licenses the quoted uncertainties and nothing further.

### 6.4 STAT/ML REUSE — CONDITIONAL on artifact compatibility evidence, with both branches

⚠ **"REUSE on a check" was too weak. The disposition is the conditional, with the branch stated.**

**Evidence required, per artifact** — the nine fingerprint fields `ESTIMATOR_REGISTRY:17-22`
mandates, which `combine_cov_nd.py` now records, **plus** the realized `n_members` and the `N−1`
divisor note:

    REUSE      iff  every one of the nine fields on C_stat and on C_ML equals the corresponding
                    field on the adopted central product, AND the realized n_members is present
                    and non-sentinel, AND the support mask and row order match the trunk's
    REGENERATE otherwise, and the regeneration is priced as a separate request

⚠ **An `UNDECLARED` sentinel is NOT a match.** Five of the eight default to `UNDECLARED`, and the
writer's design records that explicitly so a missing field reads as *"the writer was never told"*
rather than as *"not checked"*. **A field that cannot be compared has not passed.**
⚠ **And the PET `C_stat` 7.11% figure is a different object** (`VL132`/`CSTAT-R7`, 50 members); it
does not bear on the scalar-5D components. The live scalar-5D concern is separate: `--array=1-100%32`
is a **declared bracket**, so the realized count must be read, never inferred from the array spec.

**Smallest remaining action:** read the nine fields off both artifacts — zero compute — and the
branch resolves itself.

### 6.5 THREE DISTINCT STATES, which my packet §2 conflated

**Approval of a criterion, evidence that it passes, and adoption are three separate things**, and a
single "recommended disposition" column ran them together.

| cause | (i) criterion approved? | (ii) evidence it PASSES? | (iii) contributes to adoption? |
|---|---|---|---|
| **1** | criterion is tolerance-free — approve the *requirement* | **NOT YET** — the counterfactual has not run (`≈0.03` task-h) | after (ii) |
| **2** | needs D2's key **and margin** — **NOT APPROVED** | operands exist; the margin has no value | after (i) and (ii) |
| **3** | needs `δ_proj`, `δ_agg`, `δ_med` + coverage, and §3.7d (b) — **NOT APPROVED** | **NOT POSSIBLE — members do not exist** (§6.2) | after (i) and (ii) |
| **4** | approve, with `SPEC:1237`'s digit amended | print not yet produced | after (ii) |
| **5** | §6.1 disposition is the approval | **falsifier NEGATIVE across 15 traced modules — PASSES at that scope** | ready once (i) is ruled |
| **6** | the conditional in §6.4 **is** the criterion — approve it | **readable now, zero compute** | after (ii) |
| **7** | sufficiency ruling is the approval | **measured twice, two files — PASSES** | ready once (i) is ruled |

**Only causes 5 and 7 currently have passing evidence.** Causes 1, 2, 3, 4 have **no** pass evidence,
and cause 3 **cannot** have any until members are built. **Adoption requires (i) and (ii) for all
seven**, so adoption is behind cause-3 member production — the item §6.2 restores.

### 6.6 REMAINING EXECUTION SEQUENCE

**Zero-compute, needs only rulings — can proceed immediately in any order:**
1. §3.7d **(b)**; `δ = 5%` ×3 and the coverage fractions; the `U` set of §6.3.
2. Cause 5 §6.1 disposition; cause 7 sufficiency. **Both already have passing evidence.**
3. Cause 6: read the nine fields → §6.4's branch resolves (**mine to execute, no ruling needed**).
4. `SPEC:1237` digit; `ESTIMATOR_REGISTRY:29` file name + both `√tr`; D2's key created withheld.
5. The §1 **scope amendment**; the §6.4 null-route ruling.

**Then, small compute:** cause 1's counterfactual (`≈0.03`); cause 4's print (`≤ 0.5764`).

**Then the large one:** cause-3 member production, `N = 3`, `164.7` GPU / `259.6` CPU — **gated on
§6.2's approval and on the `2026-09-30` window, which may bind before the ceiling.**

**Then:** cause-3 evaluation on the members → adoption → M1 re-run with `--run-class publication`
(`0.25`) → note/primer/paper re-verification.

**Deferred and not on this path:** `y_gen`, `N`, the 12-cell χ², `rcond`/rank, any pseudoinverse, the
first-order statistic, P2, and the pinning decision.

---

## 7. STAGE D-CVDIV-1 RESULT — job `58524334`, at its measured scope

`COMPLETED`, `ExitCode 0:0`, `2184 s` (**`0.607` CPU task-h actual against a `2.00` reservation**),
`nid004087`. Bank digest **verified**; same seed both executions; `iters = 5`; 10 evaluations each.

### 7.1 The two observables, reported separately

**A — FIRST CHECKPOINT DIVERGENCE: call `0` — iteration 0, step 1, the very first classifier
evaluation.** `n = 20,404,292` elements, relative sum difference **`3.27e-16`**. Every subsequent
checkpoint also differs:

    call 0 (i0 s1)  3.268e-16      call 5 (i2 s2)  1.407e-15
    call 1 (i0 s2)  4.018e-16      call 6 (i3 s1)  2.836e-14
    call 2 (i1 s1)  1.815e-14      call 7 (i3 s2)  7.037e-15
    call 3 (i1 s2)  2.773e-14      call 8 (i4 s1)  1.536e-14
    call 4 (i2 s1)  2.930e-14      call 9 (i4 s2)  2.936e-14

**B — ENDPOINT: NOT bitwise identical.** `r_null = 4.4311e-14`, against the historical
`4.4520e-14` — **ratio `0.9953`. The discrepancy is REPRODUCED.**

**C — a third observation, unplanned and relevant.** This run's `cv_norm` is
`3.21245106927994448e-37` against the pilot's `3.21245106927996161e-37` — agreeing to 12 significant
figures and differing at **`5.33e-15` relative. So `x_cv` is not bitwise reproducible ACROSS
invocations either**, not only between the two executions inside one.

### 7.2 What this establishes, and what it does not

**ESTABLISHES, at measured scope:** under the **historical (unpinned)** configuration, on the real
bank, with identical operands and the same estimator seed, two CV executions in one process differ
**from the first classifier evaluation onward**, and the endpoint discrepancy reproduces the
historical `r_null` to `0.5%`. The first observed difference is at the **double-precision last-bit
level** (`3.3e-16` on a 20.4M-element reduction).

**DOES NOT ESTABLISH — and no mechanism is claimed:**
- **not** threading. Thread scheduling, memory layout, library dispatch, and reduction order are all
  consistent with `3.3e-16`, and this probe separates none of them.
- **not** that the first divergence is the first *arithmetic* difference. Call 0 is the **first
  observed** checkpoint; anything inside that fit is unobserved.
- **not** that pinning would fix it, and **not** that it would not.
- **not** anything about cross-node behaviour, which was not varied.

### 7.3 Which requirement this bears on — and the one justified successor

**It bears on the reproduction path** (Joseph's *"supported reproduction path"*, and blocker
**NULL**): **the historical configuration does not deliver bitwise identity.** Since §2.1 established
that every route to a *tolerance* `ε` is closed, and bitwise identity was the remaining route, **that
route is now measured shut for the historical configuration.** This is evidence for the §6.4 route
ruling, which is Joseph's.

**It bears on NO acceptance requirement in §2.** `s_proj`, `s_agg`, `s_med`, and all seven cause
dispositions are unaffected.

**The only successor with a named unmet requirement it would resolve:** test whether the **pinned**
configuration achieves bitwise identity on the real bank — which would establish whether a *forward*
reproduction path exists for a regenerated object. **Not proposed for launch here**, because it is
downstream of two of Joseph's open rulings (the §6.4 route, and whether pinning — a material
estimator change — is acceptable at all), and because `z_lgbm_overlay()` already records that pinning
is a **declared divergence from the historical chain**, so a positive result would describe a
different estimator than the one that made the existing products.

**No other successor is proposed.** Localising further inside call 0 would explain a mechanism and
resolve no named requirement.
