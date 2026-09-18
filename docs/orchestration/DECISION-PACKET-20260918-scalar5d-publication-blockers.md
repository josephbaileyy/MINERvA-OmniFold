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

---

## 8. TARGETED CORRECTIONS AND THE RECOMMENDED §6.4 RULING — 2026-09-18

### 8.1 ⭐ THE §6.4 RULING — RECOMMENDED: retrospective assessment, predeclaration failure preserved. **New production is NOT necessary on this ground.**

**The requirement, verbatim (`SPEC` §6.4):** Z's fixed-seed null uses a **scale-relative** bound,
**fixed before production**, its value *"justified by precision and sensitivity controls established
before implementation and **not** chosen from a favourable production result."*

**The predeclaration failure is real, and it is preserved, not cured.** No scale-relative bound was
fixed before Z's production. `M(i)` therefore **cannot be graded for this object, and never will be.**
That entry stays on the record permanently, and **new production would not cure it either** — it
would produce a *different* object that could be bounded prospectively.

**WHY A RETROSPECTIVE ASSESSMENT IS AVAILABLE: §6.4 performs one ITSELF, for G, and names the
principle.** Verbatim: *"**This does not retrospectively regrade G**, and it is not a finding that G's
null is bad: G's measured value is `5.8223e-50`, `1.31e-12` of the sqrt-trace — genuinely small
*relative* to the scale. **The defect is in the guard, not in the product.**"*

So §6.4 already (i) separates the guard's defect from the product's standing, and (ii) demonstrates
the admissible retrospective statistic: **`null_norm / √tr`**.

**Z on §6.4's own normalizer, with §6.4's own comparison figure:**

| | `null_norm` | `√tr` | `null_norm / √tr` |
|---|---|---|---|
| **G** (§6.4's assessed value) | `5.8223e-50` | `4.4445e-38` *(implied)* | **`1.31e-12`** — *"genuinely small relative to the scale"* |
| **Z** (`fixed_seed_null_norm` / `sqrt_tr_unified`, read from the product) | `1.4301832847122437e-50` | `4.4436736505643117e-38` | **`3.218e-13`** |

**Z is `4.07×` SMALLER than the value §6.4 itself calls genuinely small, on the same statistic, at
essentially the same scale** (`√tr` agrees to 4 significant figures, so the comparison is
like-for-like and not a rescaling).

⚠ **THIS IS NOT A TOLERANCE DERIVED FROM Z'S OBSERVED NULL.** No threshold is proposed and none is
needed: the comparison figure `1.31e-12` was fixed in §6.4 **independently of Z**, for a different
product, before Z's null was known. The assessment is *"Z's null is smaller than the one already
assessed as small"* — an ordering against an external, pre-existing datum, not a bound placed to
obtain a verdict.

⚠ **AND FAILED BITWISE IDENTITY IS NOT EVIDENCE OF SCIENTIFIC INADEQUACY.** D-CVDIV-1 established
non-identity; it did not establish inadequacy, and I must not conflate them. The divergence begins at
`3.27e-16` relative — the double-precision last bit — and the endpoint `r_null = 4.43e-14` is
**`200.5 ×` machine epsilon** accumulated across a 10,694-element norm and five OmniFold iterations.
**Bit-exactness and scientific adequacy are different properties**, and the relative magnitude is the
one that bears on adequacy.

**RECOMMENDED RULING — amend the requirement as follows:**

1. **`M(i)` is `NOT GRADED` for this candidate**, with the reason recorded as a **predeclaration
   failure**: no scale-relative bound existed before production. Permanent; not erasable by any later
   act.
2. **A RETROSPECTIVE SCIENTIFIC ASSESSMENT is admitted and reported as such**, using §6.4's own
   statistic `null_norm/√tr`, with the value `3.218e-13` and the `4.07×` ordering against G's
   already-assessed `1.31e-12`. Labelled **retrospective assessment, not a grade**, travelling with
   the product per §3.7d Answer (a)'s style.
3. **No tolerance is declared, now or later, for this object.** Any future prospective bound applies
   only to a future object.
4. **New production is NOT required on this ground.** It would not cure (1), and (2) already places
   the existing candidate below the only figure §6.4 has assessed.

**What this does NOT resolve, and is Joseph's separate call:** whether a publication may rest on a
covariance whose `M(i)` leg is permanently ungraded. That is a *sufficiency* judgement about the
acceptance chain, not a question about the null's size.

### 8.2 C6 COMPLETE — ⚠ my own condition was UNSATISFIABLE

**The check ran. Both artifacts carry exactly ONE key and no sidecar:**

    uq_cov_stat_5d.root     891,732,011 B   keys: ['hCov_stat5d_reported']    receipt: absent
    uq_cov_mlsplit_5d.root  892,078,834 B   keys: ['hCov_mlsplit5d_reported'] receipt: absent
    all nine fingerprint fields: ABSENT from both

⚠ **So §6.4's conditional I wrote — *"REUSE iff every one of the nine fields equals…"* — is
UNSATISFIABLE for these artifacts.** It cannot be met by any act short of regeneration. **That is the
same defect class as D4's registry rule, which I identified in someone else's work and then
reproduced in my own.** Withdrawn.

**PROVENANCE RECOVERED before proposing regeneration — and it is substantial:**

| what | established | source |
|---|---|---|
| **identity** | `sha256 6580016f…` / `27b2e456…`, `891,732,011` / `892,078,834` B | `SPEC:504`, `PUBLICATION-READINESS-20260822:490`, and **matching the pilot manifest's declared `sources.stat`/`sources.ml`** |
| **producer** | `sbatch_finalize_5d_bkgaware_gpu.sh:167`/`:168`; mtime `2026-07-13 18:04/18:05` | `RUNBOOK-20260822-b1-lift-preflight:290` |
| **concordance** | **three concordant invocations, no disagreement found** | `PROVENANCE-20260822:150-151` (`run_budget_5d.sh:15,17`, `sbatch_combine_5d_budget.sh:14,16`) |
| **invariance, declared by the producer** | *"C_stat/C_ML are #13-invariant → reuse existing…"* | `sbatch_finalize_5d_bkgaware_gpu.sh:8-10` |
| **`N` (ensemble size)** | **UNRECOVERABLE, and established as such by a prior covering search** — *"no key that could carry `N`, and no receipt in this tree reads [them] for one"* | `PROVENANCE-20260822:153-157` |

**AND `SPEC` §2.6b HAS ALREADY RULED**, titled *"WITHDRAWN — reuse of `C_stat`/`C_ML` is not evidence
of incompleteness"*: *"the launcher proves **reuse**, and reuse of an invariant input is not
incompleteness. **Fresh scalar replica generation needs a stated scientific rationale, and this lane
does not have one.**"*

**REVISED DISPOSITION: REUSE, with the `N` gap declared as permanently unrecoverable for these two
artifacts.** The compatibility that actually matters for `C_Z = D(ΣV)D + ΣR + ΣA + C_stat + C_ML` is
shape, support mask and row order — and the pilot **already evidenced it**: `z_build.py` requires
`np.array_equal(mask, null_mask)`, reads both at the trunk's shape, and its `G1_closure_identity`
and `G3_g_reconstruction` residuals are **exactly `0.0`** at `rtol 1e-9`. **Regeneration has no
stated scientific rationale and is not recommended.**

### 8.3 FUNCTIONAL DIMENSIONS — CORRECTED

⚠ **§6.3 wrote *"the all-ones vector over the 42"* and `w_R` over the 42 destination cells. Both are
dimensionally wrong as functionals on `C_Z`.** `C_Z` is `10,694 × 10,694`, so every `u` in `s_proj`'s
set is a **`10,694`-vector**.

The correct construction, from `vᵀ (M C_Z Mᵀ) v = (Mᵀ v)ᵀ C_Z (Mᵀ v)`:

    a destination-space weight v (dimension 42)  ->  the C_Z functional  u = M^T v   (dimension 10,694)

    U  =  { M^T e_i        for i = 1..42 }      <- per-cell;  e_i is the 42-dim unit vector
       U  { M^T 1_42 }                          <- the total over the 42 quoted cells
       U  { M^T w_R        per declared integral R }   <- w_R is 42-dim bin-volume weights

`M` has shape `[42, 10694]` (recorded in the M1 receipt), so `Mᵀ v` is `10,694`-dimensional. **`|U| =
44 + (number of declared integrals)`**, each a `10,694`-vector. The rows of `M` *are* `Mᵀ e_i`, so
that part of §6.3 was right; the all-ones and integral entries were not.

### 8.4 PROJECTIONS RECONCILED WITH THE DELIVERABLE LIST

Joseph's deliverable is *"the **required** verified projections with correctly paired central
values"* — plural. Reconciled:

| map | in the deliverable list? | why | paired central | status |
|---|---|---|---|---|
| **M1** `(E_avail,W)` | **YES — quoted** | the only map any quoted uncertainty comes from | `hCV_marginal = M x_5D` | diagnostic produced & verified; **publication run pending adoption** |
| **M2** `(pt,pz,E_avail,q3)` | **YES — required, and I had mis-scoped it** | it *"supports reported central values"*, and those central values are **reported**, so its covariance is a required verified projection | frozen 4D CV, via `--dst-cv` | `p4_project_4d.py` instrumented; readback receipt `RECEIPT-20260816-hrowindex4d-readback.json` PASS, 4825 labels exact |
| M3 `E_avail` | no | marginal anchor, nothing quoted from it | — | diagnostic only |
| M4 5D→3D | no | marginal anchor | — | diagnostic only |

⚠ **Correction: my §6.3 called M1 *"the only quoted map"* and left M2 off the required list. M2's
central values ARE reported, so its projected covariance is required.** `s_proj`'s functional set must
therefore include **M2's rows as well** — `|U|` grows by 10,976 per-cell functionals, which is
arithmetic on already-resident matrices (`SPEC` §3.7d prices `s_proj` at *"seconds"* with **zero
incremental I/O**), so the cost does not change materially.

### 8.5 TOLERANCE — the ensemble-resolution justification is WITHDRAWN; here is an honest proposal

⚠ **Withdrawn.** `√(2/(N−1))` assumes iid normal draws; the 160 throws are systematic-parameter
throws, not iid samples of one quantity. I had attached that caveat and then used the number anyway
as the *ground*. **A justification I have already undermined is not a justification** — and it was my
second attempt to derive `δ` from a construction rather than propose it.

**HONEST PROPOSAL, offered as a scientific judgement about acceptable movement in a published
uncertainty — not derived:**

> **`δ = 5%` direct relative movement**, for `s_proj`, `s_agg`, and `s_med`'s per-bin leg.

**The ground is what it means, stated plainly, not a derivation.** At `δ = 5%` a quoted corner
uncertainty of `5.81%` could have read `5.52%`–`6.10%` depending on an arbitrary estimator seed.
**My judgement is that a ±5% ambiguity in the third significant figure of a quoted uncertainty is
acceptable and would not change any use of the number**; that `10%` (`5.23%`–`6.39%`) begins to move
the second significant figure and is not; and that anything above `10%` would make an arbitrary seed
choice a visible feature of a published uncertainty.

**This is a judgement, it is mine, and `δ` remains Joseph's to set.** What I can assert without
judgement is only the consequence table:

| `δ` | a quoted `5.81%` could instead read |
|---|---|
| `3%` | `5.64%` – `5.98%` |
| **`5%` (proposed)** | **`5.52%` – `6.10%`** |
| `10%` | `5.23%` – `6.39%` |

**`s_med`'s coverage fraction:** 100% on bins entering a quoted projection; ≥99% on the full reported
support with every failing bin enumerated. Same status — a proposal, not a derivation.

### 8.6 CAMPAIGN — ⚠ THE ENFORCED RESERVATION EXCEEDS THE CEILING AT **N = 1**

⚠ **My §6.2 priced the campaign at `164.7` GPU / `259.6` CPU per three members. Those are MEASURED
ACTUALS. The enforced reservation is the wall cap × tasks, and it is far larger. This is the third
time I have made this exact substitution in one session, and this is the largest item.**

Read from the seven launchers' own `#SBATCH` directives:

| arm | unit | wall cap | tasks | **RESERVATION** | measured actual | ratio |
|---|---|---:|---:|---:|---:|---:|
| `boot5dG` | GPU | 3.0 h | 100 | **300.0** | 14.86 | 20.2× |
| `sweep5dBKGrun` | GPU | 1.5 h | 169 | **253.5** | 26.28 | 9.6× |
| `det5dBKG` | GPU | 4.0 h | 19 | **76.0** | 13.76 | 5.5× |
| `uthrow5d_block` | CPU | 12.0 h | 21 | **252.0** | 31.01 | 8.1× |
| `uthrow5d_runF` | CPU | 6.0 h | 40 | **240.0** | 49.11 | 4.9× |
| `ssplit5d` | CPU | 3.0 h | 24 | **72.0** | 5.83 | 12.3× |
| `uthrow5d_combF` | CPU | 3.0 h | 1 | **3.0** | 0.58 | 5.2× |
| **per member** | | | | **`629.5` GPU / `567.0` CPU** | `54.90` / `86.53` | |

**FRESH ADMISSION, measured `2026-09-18T13:57:22Z`:** CPU `97.2939` of `500`, headroom **`402.7061`**;
GPU `16.0117` of `500`, headroom **`483.9883`**; 136 tasks, 2,019 attempts; stop date `2026-09-30`,
not fired. **Outstanding reservations: 1** — `58526214 pet-eavail-charact`, PENDING, `--time=30:00`,
another lane's.

**The meter's verdict for ONE member at enforced caps, run rather than argued:**

    r5_meter.py check --cpu-task-hours 567.0 --gpu-task-hours 629.5
    -> rc 5   "R5 proposal would reach or exceed a ceiling"

**So the campaign is NOT ADMISSIBLE at N = 1, let alone N = 3.** `629.5` GPU exceeds the `500`
ceiling outright.

**THE REMEDY IS INSIDE THIS LANE'S REACH AND IS A DESIGN FIX, NOT A CEILING REQUEST.** `SPEC` §5.8e
item 4 already names it: *"A hold-style dispatch charges to its timeout… That is a hazard to design
out, not a price to plan on — and it is a **design** hazard, so it is inside this lane's reach."*
Re-capping `--time` per arm from measured per-task actuals, indicatively at ≈2× the per-task mean:

    boot5dG        0.149 h/task -> cap 0.5 h  ->  50.0 GPU      uthrow5d_runF  1.228 -> 2.5 h -> 100.0 CPU
    sweep5dBKGrun  0.156        -> cap 0.5    ->  84.5 GPU      uthrow5d_block 1.477 -> 3.0   ->  63.0 CPU
    det5dBKG       0.724        -> cap 1.5    ->  28.5 GPU      ssplit5d       0.243 -> 0.75  ->  18.0 CPU
                                                                uthrow5d_combF 0.580 -> 1.5   ->   1.5 CPU
    per member re-capped:  163.0 GPU / 182.5 CPU
      N=1 ->  163.0 / 182.5   fits            N=2 -> 326.0 / 365.0   fits CPU at 90% of headroom
      N=3 ->  489.0 / 547.5   CPU EXCEEDS headroom 402.71

⚠ **These re-cap figures are a PROPOSAL and are not yet defensible as caps.** They use the per-task
**mean** (total ÷ tasks); a cap must survive the per-task **maximum**, which I have not read, and
`SPEC` §5.8e records a measured **±60% single-arm swing**. **Reading the per-task maxima from `sacct`
is the prerequisite for any re-cap, and it is a zero-compute read** — but it is a *new* action and I
am not taking it without direction.

**REVISED RECOMMENDATION: the affordable member count under enforced-cap pricing is `1`, or at most
`2` after a verified re-cap. `N = 3` does not fit the CPU headroom even re-capped.** My earlier
`N = 3` recommendation is withdrawn as unaffordable.

### 8.7 THE OFFSET CONCLUSION — LIMITED TO THE TESTED FAMILY

Whatever member count is approved, the cause-3 conclusion is bounded as follows, and this wording
should travel with the grade:

> A `(cause 3, Z)` result over `N` offsets states that **`s_proj`, `s_agg` and `s_med` did not exceed
> `δ` across the `N` tested offsets of the DIAGONAL family with group assignment
> `{arms 1–4: 42, arms 5–7: 1000}` held fixed at its archive values.** It is **not** a statement about
> the 2-D grid (`D1`; the inter-module split is invariant under `k` and unresolvable within this
> family), **not** about untested offsets, **not** about other estimator families, and — at `N ≤ 2` —
> **not a variance estimate at all**, since two offsets give one difference. With `N = 1` there is no
> comparison and the leg is descriptive only.

⚠ **This matters more now than when I wrote `N = 3`:** at the affordable `N = 1`–`2`, the cause-3
correlation leg **cannot** support a spread statement. **That is a scientific consequence of the
ceiling, and it belongs in the §6.4-style sufficiency judgement, not buried in a cost table.**

---

## 9. BOUNDED RESULTS — 2026-09-18, read-only planning

### 9.1 PER-TASK MAXIMA, and one additional member IS admissible

⚠ **§8.6's "not admissible at N = 1" was itself wrong.** It applied a uniform `1.5×`/`2.0×` margin to
each arm's per-task **maximum**, which over-caps a long-tailed arm. With the distributions read, the
conclusion reverses.

Read-only `sacct -X -D`, `TZ=UTC`, `2026-08-25`→`09-05` — **both complete rounds pooled**, so each
maximum is over more tasks than one round declares:

| arm | unit | tasks | cap now | **per-task max** | ratio cap/max |
|---|---|---:|---:|---:|---:|
| `boot5dG` | GPU | 100 | 3.00 h | **0.179 h** | 16.8× |
| `sweep5dBKGrun` | GPU | 169 | 1.50 h | **0.177 h** | 8.5× |
| `det5dBKG` | GPU | 19 | 4.00 h | **0.758 h** | 5.3× |
| `uthrow5d_runF` | CPU | 40 | 6.00 h | **2.671 h** | 2.2× |
| `ssplit5d` | CPU | 24 | 3.00 h | **0.481 h** | 6.2× |
| `uthrow5d_combF` | CPU | 1 | 3.00 h | **0.576 h** | 5.2× |
| **`uthrow5d_block`** | CPU | 21 | 12.00 h | **8.639 h** | **1.4×** |

**`uthrow5d_block` is the binding arm, and its maximum is ONE OUTLIER IN 38:**
`min 0 s`, **`p50 1.22 h`**, **`p90 1.97 h`**, `max 8.64 h`; **4 of 38 above 2 h, 1 of 38 above 6 h.**
So its enforced reservation is set entirely by a single task, and the cap is a **trade between
reserved headroom and an expected timeout**:

| `block` cap | block reservation | **CPU total** | % of `402.70` headroom | observed tasks exceeding |
|---:|---:|---:|---:|---|
| 2.25 h | 47.2 | **236.2** | 59% | ~1 of 38 |
| **3.00 h (recommended)** | **63.0** | **252.0** | **63%** | **1 of 38** |
| 6.00 h | 126.0 | 315.0 | 78% | 1 of 38 |
| 8.75 h | 183.8 | 372.8 | 93% | **0 of 38** |

CPU total = block + `runF` @1.5× (`4.25 h × 40 = 170.0`) + `ssplit` @1.5× (`18.0`) + `combF` @1.5×
(`1.0`). **GPU at 1.5× margin is `158.2` of `483.96` = 33%, not binding in any variant.**

**PROPOSED CAPS (one additional member):** `boot5dG 0.50`, `sweep5dBKGrun 0.50`, `det5dBKG 1.25`,
`uthrow5d_runF 4.25`, `ssplit5d 0.75`, `uthrow5d_combF 1.00`, **`uthrow5d_block 3.00`** →
**`158.2` GPU / `252.0` CPU enforced reservation.**

**FRESH ADMISSION, measured `2026-09-18T14:12:16Z`:** CPU `97.2953` of `500`, headroom **`402.7047`**;
GPU `16.0386` of `500`, headroom **`483.9614`**; 139 tasks; stop date `2026-09-30`, not fired;
**outstanding reservations 1** (`58526214 pet-eavail-charact`, another lane's). Meter run, not
argued:

    check --cpu 252.0 --gpu 158.2  -> rc 0   ADMITTED   (recommended)
    check --cpu 236.2 --gpu 158.2  -> rc 0   ADMITTED   (2.25 h block cap)
    check --cpu 372.8 --gpu 167.8  -> rc 0   ADMITTED   (8.75 h, zero expected timeout)

**All three admit.** The `3.00 h` variant is recommended: it covers 37 of 38 observed block tasks,
leaves 37% of CPU headroom, and its one expected exceedance returns for a decision under the
no-automatic-requeue rule rather than retrying silently. **Not launched.**

⚠ The caps are proposals from **observed** maxima over two rounds; they are not guarantees. `SPEC`
§5.8e's measured **±60% single-arm swing** applies to arm totals and is not bounded by a per-task cap.

### 9.2 MEMBER COUNTING — CORRECTED. The archive IS a member

⚠ **I mis-counted.** `k = 0` is the **archive and Z's own build** — it is already a member of the
family. So **one additional offset gives a two-member set and a real comparison.**

And the criterion is **maximum movement over a finite predeclared set**, not a population variance:
§3.7d defines `s_proj` as *"the **maximum** relative change in `√(uᵀ C_Z u)` over a PREDECLARED set"*.
**A maximum over a two-element set is well defined and is what the criterion asks for.** My §8.7
claim that *"two offsets give one difference"* and *"at `N ≤ 2` not a variance estimate at all"*
imported a statistical frame the criterion does not use. **Withdrawn.**

**THE SMALLEST CAMPAIGN: one additional member at one declared offset `k`.** Family diagonal, group
assignment `{arms 1–4: 42, arms 5–7: 1000}` fixed at archive values, seeds **not** unified. Cost as
§9.1. **Its conclusion, stated exactly and as narrowly as it deserves:**

> A `(cause 3, Z)` result over `{k = 0, k = k₁}` states that the **maximum** relative change in
> `√(uᵀ C u)` over the predeclared functional set `U`, and in `s_agg` and `s_med`, **between those
> two members**, did not exceed `δ`. It is a statement about **one offset pair**. It is **not** a
> spread, a variance, a bound over untested offsets, or evidence about the 2-D grid (`D1`: the
> inter-module split is invariant under `k` and unresolvable within this family). A second member
> tests whether the statistics move **at all** between two points of the family — which is the
> question cause 3 asks — and nothing about how far they could move over the family as a whole.

### 9.3 C6 — compatibility from PRODUCER CONFIGURATION and physical provenance, not closure

⚠ **Withdrawn: my §8.2 cited the pilot's exactly-`0.0` `G1`/`G3` closure residuals as evidence of
mask and row-order compatibility. They are not independent proof.** Those are identities **among the
assembled object's own parts** — they would hold under a *consistent* mis-ordering, and they are not
a test of `C_stat`'s row order against the trunk's. Removed from the argument.

**The argument, from the producer's committed invocation** —
`sbatch_finalize_5d_bkgaware_gpu.sh:422-423`:

    combine_cov_nd.py --glob .../res_boot_*.npz  --expected-ids 1-100 --cv "${CV}" --tag stat5d
    combine_cov_nd.py --glob .../res_split_*.npz --expected-ids 1-24  --cv "${CV}" --tag mlsplit5d

| property | how the producer establishes it | citation |
|---|---|---|
| **row order** | `rep = cv > 0`; `rows = flatnonzero(rep)` in **C order**, taken from the `--cv` product. **Not re-derived and not inherited from a sibling** | `combine_cov_nd.py:48,58` |
| **support mask** | the same `cv > 0`, from the same `${CV}`, so identical **by construction** — and the trunk's predicate is the same: `CV_SUPPORT_PREDICATE = "x_cv > 0"` | `combine_cov_nd.py:48`; `unified_throw_cov.py:330` |
| **one CV for both** | **both invocations pass the same `${CV}` shell variable**, so `C_stat` and `C_ML` share a row basis with each other and with the launcher's declared central | `:422-423` |
| **normalization** | `C = (Zᵀ Z)/(N−1)`, **mean-centered over members**, unbiased — and explicitly **not** the MAT `1/N` joint-throw convention, which belongs to a different ensemble | `combine_cov_nd.py:48` |
| **member counts** | **`N = 100`** (bootstrap) and **`N = 24`** (seed-split), declared on the command line and passed as an **expected set** to `load_replica_manifest(paths, set(range(lo, hi+1)))`, so a missing replica is caught at load | `:422-423`, `combine_cov_nd.py:44-46` |
| **reuse rationale** | *"C_stat/C_ML are #13-invariant → reuse existing…"* — the producer's own declaration | `sbatch_finalize_5d_bkgaware_gpu.sh:8-10` |

⚠ **`N` IS RECOVERABLE AFTER ALL — from the producer's configuration, not from the artifact.** My
§8.2 called it "unrecoverable"; that was true of the *file* and false of the *record*. Corrected.

**THE REMAINING GAP, PRECISELY: it is TRACEABILITY, not COMPATIBILITY.** A consumer opening
`uq_cov_stat_5d.root` sees one `TH2D` and can verify none of the six rows above from the file —
the provenance lives in the launcher and the run records. **Compatibility is established;
self-attestation is absent.** That gap is not a reason to regenerate: regeneration would add the
fields, but the properties they would record are already established by a committed invocation, and
`SPEC` §2.6b holds that *"fresh scalar replica generation needs a stated scientific rationale, and
this lane does not have one."* **Disposition unchanged: REUSE.** The traceability gap is closed for
**future** products by the writer's new fields, and is recorded as a permanent property of these two.

### 9.4 §6.4 — THE EXACT PUBLICATION-SUFFICIENCY AMENDMENT

**Using the existing vocabulary.** `CRITERIA` §0's grade set is **`MET` / `OPEN` / `UNRESOLVED`**,
and `z_validator.py:14-20` records that an unassessable run is *"a REJECT, NOT A FOURTH GRADE
TOKEN"*, producing `assessable=False` with `4c` in `reject_conditions` and `branch is None`.
⚠ **So my §8.1's "`M(i)` is `NOT GRADED`" invented a token. Withdrawn — the correct token is
`UNRESOLVED`.**

**PROPOSED AMENDMENT, in three separable clauses. Joseph may grant 1 and 2 without 3.**

> **Clause 1 — the historical failure, preserved.** `(cause 3, Z)`'s `M(i)` leg remains
> **`UNRESOLVED`** for the existing candidate, with `reject_conditions` retaining **`4c`** and
> `branch = None`. The recorded reason is a **predeclaration failure**: no scale-relative bound
> existed before this object's production, as §6.4 requires. This clause is permanent and is not
> altered by clauses 2 or 3.
>
> **Clause 2 — PERMISSION TO ASSESS RETROSPECTIVELY.** A retrospective, scale-relative
> **assessment** of the existing candidate's fixed-seed null may be computed and recorded, using
> §6.4's own statistic `null_norm / √tr`. It is recorded as an **assessment**, carries **no grade
> token**, and does not change clause 1. Measured: **`1.4301832847122437e-50 / 4.4436736505643117e-38
> = 3.218e-13`**.
>
> **Clause 3 — PERMISSION TO RELY ON IT FOR PUBLICATION.** Separately, and only if Joseph so rules:
> the assessment in clause 2 may be cited as the publication's account of fixed-seed
> reproducibility, provided the receipt carries clause 1's `UNRESOLVED` status and the
> predeclaration failure in the same place the assessment appears.

**G's value is CONTEXT, not a transferred threshold.** §6.4 characterizes G's `1.31e-12` as
*"genuinely small relative to the scale"*. That is **the only magnitude §6.4 has characterized**, and
it is offered here **solely as context for what order of magnitude has previously been judged small**.
⚠ **No threshold is transferred, `1.31e-12` is not a bound, and Z's `3.218e-13` being smaller is NOT
a pass.** §8.1's *"4.07× smaller than the figure §6.4 calls genuinely small"* read as a pass-like
comparison and is **withdrawn as framing**; the ratio is reported as context only.

**And non-identity is not inadequacy.** D-CVDIV-1 established that two executions differ; it
established nothing about scientific adequacy. The first divergence is `3.27e-16` — the
double-precision last bit — and the endpoint `4.43e-14` is `200.5×` machine epsilon over a
10,694-element norm and five iterations.

**New production is not required by clause 1**, which new production would not cure for this object.

### 9.5 THE 5% LIMIT — retained as a proposal only

**`δ = 5%`, a proposed direct relative movement limit on `s_proj`, `s_agg`, and `s_med`'s per-bin
leg. Joseph's to set.**

⚠ **Removed:** the significant-figure justification, and the assertion that `5%` *"would not change
any use of the number"*. **I cannot support either.** I do not know every use a quoted uncertainty
will be put to, and a digit-position argument is the display-derived reasoning `SPEC` rev. 16
withdrew in another form.

**What remains asserted is only the consequence, which is arithmetic:**

| `δ` | a quoted corner uncertainty of `5.81%` could instead read |
|---|---|
| `3%` | `5.64%` – `5.98%` |
| **`5%` (proposed)** | **`5.52%` – `6.10%`** |
| `10%` | `5.23%` – `6.39%` |

`5%` is offered as the value this lane would propose. **No derivation is claimed and no use is
excluded.**
