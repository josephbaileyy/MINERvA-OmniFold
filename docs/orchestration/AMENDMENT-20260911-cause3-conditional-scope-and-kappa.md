# Proposed amendment: cause 3's conditional scope, and `κ`'s package

**Owner:** `z-criteria-owner` lane. **Base:** `6f24fb00`. **Implementation pins:** `ec5f0b99`
(width-weighted rate functionals), `6d959ab3` (Rayleigh `κ` predicate) — **frozen pending review; not
revised here.**

> **NOT CITABLE FOR:** adoption, grading, gate movement, merge or compute. **Gate 2 FAIL.
> `cause3_corr` WITHHELD. Cause 3 non-passing.** This is a **PROPOSED** amendment and a **PROPOSED**
> `κ`. Nothing here discharges cause 3.

---

# PART A — CAUSE 3: the proposed amendment, five elements

## A.1 What estimator settings vary across the declared members

`MNV_EST_SEED_OFFSET` over the declared offset set `K` (explicit, non-trivial, containing `0`;
`z_build_path.declared_population` fails closed on all four vacuous shapes). The offset reaches the
estimator as the `random_state` of each learner — the pattern at `eavailW_covariance.py:288-289`,
`classifier1_params` / `classifier2_params` / `regressor_params` — and therefore **re-unfolds the
result**. Everything downstream of the unfolding is regenerated per member: `CV`, `SWEEP_GLOB`,
`COMB` (the systematic-universe combine, i.e. the bands), `UTHROW` (the unified-throw covariance),
`OUTD`.

## A.2 Which statistical/ML components remain fixed

**`C_stat` and `C_ML`, held DIGEST-identical across every member** — not path-identical.
`BuildPath(block_source="SHARED_DIGEST_BOUND")` requires both digests and
`MemberReceipt.verify_against` checks them **at runtime**, because a flag asserting `SHARED` is not
sharing. *(This campaign measured identical paths holding different bytes across the 2026-07-13
rebuild, which is why the binding is by digest.)*

⚠ **This configuration does not exist today.** `mr_declared()` is
`[[ -n "${MNV_EST_SEED_OFFSET:-}" ]]`, so one variable means both *"member of `K`"* and *"build your
own blocks"*, and `sbatch_finalize_5d_bkgaware_gpu.sh:416-424` builds **this member's own**
`C_stat`/`C_ML`. The decoupling is what creates the configuration; it is not a description of the
current launcher.

## A.3 What A-7 measures, and what passing it LICENSES

**Measures:** `s_proj` = the maximum, over the declared offsets `K` and the declared functionals
`U`, of the relative change in the **released projected uncertainty** —
`max_{k,i} |√(u_iᵀC_k u_i) − √(u_iᵀC_0 u_i)| / √(u_iᵀC_0 u_i)` — with `C_stat`, `C_ML` digest-fixed.

**Passing licenses exactly this:** *the released projected uncertainties of the declared projections
are determined by the declared construction, up to `δ_proj`, GIVEN the statistical and ML components
held fixed at their declared digests.*

## A.4 What it does NOT support — a licensing clause, in the contract's own template

⚠ **The contract already contains the amendment's form.** `cause3_corr` reads *"a MET result on them
licenses nothing about `C_Z`'s off-diagonal structure"* — a **licensing clause**, the file's own
template for naming what a leg does not establish. Following it:

> **A MET result on (cause 3, Z) under this build path states that the released projected
> uncertainties did not exceed their declared movement limit across the declared offsets, WITH THE
> STATISTICAL AND ML COMPONENTS HELD AT FIXED DIGESTS. It licenses NOTHING about:**
> **(i)** whether **regenerated** `C_stat`/`C_ML` would move the released bars under the same
> offsets — the components held fixed are exactly the ones not tested;
> **(ii)** the **finite-ensemble** contribution to those bars, which is common-mode under fixed
> digests and cancels in `C_k − C_0` by construction;
> **(iii)** `C_Z`'s off-diagonal structure beyond the directions the declared functionals probe —
> `s_proj` is a maximum over a **declared** set, not over all directions;
> **(iv)** calibration, coverage, or any frequentist property — the intended-use statement already
> disclaims all three;
> **(v)** any projection not in the declared set.

## A.5 ⚠ RELATION TO THE EXISTING REQUIREMENTS — and the objection, engaged

**The objection, stated as the reviewer put it rather than paraphrased:** cause 3's declared subject
is `C_Z` **whole and unconditioned**; `C_stat` and `C_ML` are **summands of it**; a test holding them
digest-identical measures a **proper subset** and is silent on whether regenerated blocks would move
under the same offsets. So a conditional result does not discharge cause 3 as written, and recording
it as discharging cause 3 would be the silent narrowing Joseph forbade.

> ## ⚠⚠ REV. 2 — THE "AMBIGUITY" FRAME IS WRONG ON THE DATES, AND THE GRAMMAR MATTERS
>
> **Measured, and I verified it rather than accepting the relay:** `MNV_EST_SEED_OFFSET` first
> appears in the tree at **2026-08-18**; `SPEC-20260906-…` was added at **2026-09-06** — **nineteen
> days later**. And the launcher at `6f24fb00` is **binary**: `:417` declared → own blocks, `:424`
> else → archive reuse. *(`git log -S` dates the commit, not the artifact — but both bounds point
> the same way here, so the ordering holds regardless.)*
>
> **So (a) and (b) were not two indistinguishable configurations — (b) DID NOT EXIST.** Only the
> total reading was producible, and the contract text was written **after** the binary machinery,
> against a world where the only expressible variation regenerates the blocks. **Its natural
> referent is (a) TOTAL, and the decoupling CREATES (b) rather than revealing a latent ambiguity.**
>
> **THEREFORE WHAT I AM ASKING FOR IS A NARROWING OF THE DECLARED SUBJECT — a contract change, and
> mine to argue.** The grammar is not cosmetic: *"which did you mean?"* invites a cheap answer and
> **puts the burden on Joseph's memory**, while *"may I narrow the declared quantity from the
> assembled `C_Z` to the estimator-attributable part, and here is why"* **puts it on the proposer,
> where a contract change belongs.** §A.6's pricing is that argument; only its framing was wrong.

**MY ANSWER: THE OBJECTION IS CORRECT AS AGAINST THE UNCONDITIONAL READING, and the two readings
below are what a narrowing would move between — NOT, as rev. 1 had it, two readings the contract
already failed to distinguish.** Verbatim at `6f24fb00`,
`z_contract.py:222-225`: *"how much **estimator-baseline sensitivity** is scientifically
acceptable"* — **unqualified**, with no statement of what is held fixed while it is measured. Two
readings both fit that sentence:

| | reading | what it asks | what discharges it |
|---|---|---|---|
| **(a) TOTAL** | how much does `C_Z` move when the estimator baseline is changed **as production changes it** | includes block regeneration, because today one switch does both | **per-member regeneration** of `C_stat`/`C_ML` — the 100 + 24 replica ensembles per member |
| **(b) ATTRIBUTABLE** | how much of `C_Z`'s movement is **attributable to the estimator-baseline choice** | isolates the estimator; block resampling is finite-ensemble noise, a different cause | the conditional test above |

**⚠ AND THE AMBIGUITY WAS INVISIBLE UNTIL THE DECOUPLING, which is why it has gone unnoticed:** with
one switch controlling both, (a) and (b) were **not distinguishable configurations**, so no wording
had to choose. Separating the controls is what makes the two readings different experiments — and
therefore what makes the ambiguity actionable rather than academic.

**WHAT I RECOMMEND, and it is a coherent amendment rather than a deferral:**

1. **Amend `cause3_agg`'s and `cause3_med`'s reasons to state what is held fixed** while
   estimator-baseline sensitivity is measured. Not a new boundary, not a changed statistic — the
   sentence currently omits a condition that changes what it means.
2. ⚠ **REV. 2 — THE CLAUSE'S DESTINATION IS CORRECTED, AND MY FIRST CHOICE WAS THE ONE PLACE I HAD
   MYSELF PROVEN UNREACHABLE.** Rev. 1 put it in `cause3_corr`'s `reason`. **My own Part I §I.1
   established by execution — with both positive controls passing — that that entry is INERT:**
   deleting it from `Z_BOUNDARIES` leaves `assess`'s `describe()` **byte-identical**, because a
   boundary is reached only at `z_validator.py:247` via `leg.boundary_key` and surfaced only at
   `:107-111` through the declared legs — and **`cause3_corr` is named by no leg, which is the
   entry's own stated premise.** So rev. 1 proposed recording the licensing consequence of a
   deferral **inside the very entry whose unreachability is what the deferral is about**: true,
   committed, and **invisible to every grade**. `z_validator.py:166-167` states the violated rule
   verbatim — *"the narrowing that must travel WITH the grade, not sit in a specification the
   grader may not open."*
   **⚠ AND `_DIAGONAL_ONLY_SCOPE` IS ALSO THE WRONG HOST**, though it is the obvious one: it keys
   on the presence of a **correlation-sensitive leg**, which is orthogonal to whether the blocks
   are held fixed. Attached there, the clause would appear when no corr leg is declared and vanish
   when one is — **the wrong trigger entirely.**
   **DESTINATION, IMPLEMENTED at `z_build_path.conditional_scope_statement`:** a separate emitted
   statement **derived from the build path's block source**, returned on **every** A-7 outcome —
   graded *and* refused — with **no parameter by which a caller could assert or suppress it**
   (verified by signature inspection, the same discipline as `sees_correlations` being derived from
   the legs). Shared blocks emit the conditional clause; per-member blocks emit the caveat that the
   measurement is the **sum** of two causes; a non-member run emits neither.
3. **Record reading (b) as what the conditional test discharges, and reading (a) as EXPLICITLY
   UNDISCHARGED** — named in the receipt, not omitted from it.

**WHAT THE AMENDMENT DOES NOT DO, stated so it cannot be read as more:** it does **not** make cause 3
passable. ⚠ **And rev. 1's stated mechanism was looser than the real one** — the same inertness the
destination correction turns on: **`cause3_agg` and `cause3_med` are what force non-passing**,
because legs name them; **`cause3_corr`, named by no leg, forces nothing.** All three remain
withheld, but only two are load-bearing, and saying "all three" implies a guard that is not there. It does **not** decide between (a) and
(b). It makes the conditional scope **statable** and the unconditional reading **visibly open**.

## A.6 ⚠ THE PRECISE SCIENTIFIC CHOICE, since one remains and it is Joseph's

> **May the declared subject of cause 3 be NARROWED from the assembled `C_Z` (reading (a), TOTAL)
> to the estimator-attributable part (reading (b))?**
>
> *Rev. 1 asked "which did you mean?". That was the wrong grammar: the contract's referent is (a),
> so there is nothing to recall — there is a change to authorise or refuse, and the burden of
> argument is mine.*

**Consequences, priced, because the branches differ by more than wording:**

- **(b) ATTRIBUTABLE** — the conditional test discharges it. Cost: one member set with shared
  blocks. **And it is the only branch in which A-7 can both bind and be satisfiable**, because under
  (a) the blocks are regenerated per member and their finite-ensemble noise enters `C_k − C_0`
  directly, which is the `B'` floor problem.
- **(a) TOTAL** — requires **per-member regeneration of 100 bootstrap replicas + 24 seedscan splits**
  (`sbatch_finalize_5d_bkgaware_gpu.sh:422-423`, `--expected-ids 1-100` / `1-24`, full-range on
  purpose so a partial member **refuses**). That is the dominant compute term, and it makes the
  measured quantity the **sum** of estimator sensitivity and finite-ensemble noise, with no route to
  separate them from that measurement alone.

**I recommend (b), and I am not treating the recommendation as the decision.** Ground: *"estimator-
baseline sensitivity"* most naturally names the sensitivity **to the estimator baseline**, and
reading (a) measures a quantity that is the sum of two causes the campaign already treats separately
— cause 3 (estimator baseline) and the finite-ensemble disclosure (A-6). **If (a) is intended, the
honest statement is that the conditional test discharges nothing and the pilot must be priced with
both dominant terms per member.**

---

# PART B — `κ`'s PACKAGE

**⚠ ASSESSMENT SCOPE, stated rather than inferred:** the predicate was implemented at **`6d959ab3`**
and is **frozen**. This Part B is **unassessed** at the time of writing. When the mathematical
reviewer returns, the record must read *assessed at pin X, revised since at pin Y, unassessed
delta = Z* — and if I revise in response, the assessment must not be represented as covering the
revision.

## B.1 Formula

> **A declared functional `u_i` is numerically resolvable iff
> `(u_iᵀ C_0 u_i) / ‖u_i‖² ≥ κ · λ_max(C_0)`.**

A **Rayleigh quotient** against the operand's largest eigenvalue. Evaluated **before** any PSD
assertion, and it names the **functional**, never the operand.

## B.2 ~~Proposed value: `κ = 1e-12`~~ — ⚠ **WITHDRAWN in rev. 2; a placeholder pending `λ_min_retained/λ_max`.** See the box in B.3.

## B.3 Numerical justification — ⚠ and scale invariance is NOT it

**Scale invariance made `κ` classifiable; it says nothing about which value is right.** The
justification is a **resolution** argument about this operand at this dimension.

`q/‖u‖²` is a Rayleigh quotient, so it lies in `[λ_min, λ_max]` and is computed as a sum of `n`
products. Its achievable resolution is therefore set by floating-point accumulation at `n = 10,694`:

| bound | value | is it what happens? |
|---|---|---|
| worst-case **linear** `n·eps` | `2.375e-12` | **No** — assumes sequential accumulation |
| **pairwise** `log₂(n)·eps` | `2.972e-15` | **Yes** — matches measurement |
| **MEASURED**, median relative error of a Rayleigh quotient whose exact value is 1 | `4.44e-16` | at `m = 1200` |
| **MEASURED**, worst of 12 trials | `1.78e-15` | at `m = 1200` |

**So the numerical floor is `~2e-15`, not `~2e-12`: the linear bound is three orders too
pessimistic**, because `einsum`/BLAS accumulate in blocks. *(Measured at `m = 1200` as a tractable
stand-in; the pairwise bound grows as `log₂`, so `n = 10,694` adds a factor `~1.2`, not `~9`.)*

**And the second half of the justification is the operand's rank structure, which is why the window
is wide.** `rank(C_Z) ≤ 265` of `10,694`: **~97.5% of directions are null by construction**, so a
declared functional either has genuine support — a quotient of order `λ/λ_max` for a real band
direction — or essentially none. **There is no dense continuum between the two**, which is exactly
what makes a resolution threshold the right instrument and a wide window safe.

> ## ⚠⚠ REV. 2 — B.2's VALUE IS WITHDRAWN. I MEASURED THE BEST CASE, NOT THE BINDING ONE.
>
> **The separation below uses a supported direction whose Rayleigh quotient is `1.000` — and a
> quotient of exactly 1 is the TOP EIGENVECTOR, the maximum attainable.** I measured `κ` against
> the **easiest** supported direction and reported the window as if it were general.
>
> **The binding edge is `λ_min_retained / λ_max`** — the weakest of the 265 retained modes, a
> genuinely supported direction carrying real variance. For an eigenvector `v_i`,
> `v_iᵀCv_i / ‖v_i‖² = λ_i` exactly, so that direction's quotient **is** `λ_min_ret/λ_max`. Hence
> the crossover sits at a **retained condition number of `1/κ`**:
>
> | retained cond | weakest retained quotient | verdict at `κ = 1e-12` |
> |---|---:|---|
> | `1e11` | `1.0e-11` | RESOLVED |
> | `1e12` | `1.0e-12` | RESOLVED |
> | **`1e13`** | `1.0e-13` | ⚠ **DEGENERATE — a REAL retained mode misclassified** |
>
> **⚠ AND UNDER JOSEPH'S ROLE TEST THAT IS `κ` ABSORBING SCIENTIFICALLY MEANINGFUL VARIATION,
> which returns the value to his ownership regardless of the Rayleigh fix.**
>
> **AND MY RANK ARGUMENT DOES NOT COVER IT.** *"~97.5% of directions are null, so there is no dense
> continuum"* establishes there is no continuum **between** the null space and the supported space.
> It says nothing about the **dynamic range WITHIN the retained 265** — different properties of the
> same spectrum. **A 265-dimensional subspace spanning twelve orders in eigenvalue has no continuum
> down to round-off and still has modes below `κ`.** The tree already names this as the quantity
> that matters: `RANK-AND-INVERSION-20260810.md:38-39`, *"the smallest retained eigenvalues dominate
> the quadratic form and they are precisely the least determined directions."*
>
> **And `1e12` is not a stretch for `C_Z`:** the note's quoted densities alone span `2.19e-38` to
> `6.8e-41`, a factor **322**, i.e. **~1e5 in variance from bin content before anything else** —
> before the band-magnitude spread across ~44 bands and the `97×` width weighting.
>
> ### ⚠ AND IT CORRECTS MY OWN CONCESSION AGAINST ME
> I said the one thing I could not close without the constructed `C_Z` was my **operand's SIZE**.
> **It is the SPECTRUM.** And the size concern runs the *other* way: measured on rank-265 operands
> with `u` from the exact null space, the accumulation floor **DECREASES** with dimension —
> `n=500` worst `2.25e-17` → `n=6000` worst `6.84e-18` — because `λ_max` normalisation grows faster
> than round-off. **So extrapolating from 1,200 to 10,694 is safe in the direction that matters, and
> my `~560×` margin understated my own case.** The reviewer reported that against the finding it
> went looking for, and I am recording it as such.
>
> ### THE ONE REQUIRED MEASUREMENT, AND ITS SCOPE — this is an authorization request, not a run
> **Measure `λ_min_retained / λ_max` on the constructed `C_Z`**, or on the standard-P4 5D candidate
> **stated as a proxy**, and state `κ`'s margin **below** it. If that ratio is at or under `κ`, `κ`
> is absorbing real support and the value is Joseph's.
>
> **⚠ SCOPED: NOT RECOVERABLE FROM EXISTING WORK. I checked before asking.**
> `RANK-AND-INVERSION-20260810.md:23` records the condition number as *"numerically infinite"* —
> that is the **full** matrix including the null space, **not** the retained-edge ratio. The
> `pinv`-rcond scan at `:57` is **2D only** (`app_statmethods:953`, 73 and 139 directions). And
> `:99` lists the **ND** scan as **still required** — *"run the rank-truncation scan as in 2D and
> show it, because in ND it will not be smooth."*
> **So the spectrum at the retained edge is unmeasured, and the measurement `κ` needs IS clause
> (iii)'s already-mandated rank-truncation scan** — `app_statmethods.tex:648-650`. **It is not a new
> requirement; `κ` rides on a deliverable the protocol already demands for any N-D χ².**
> **Cost: ONE eigendecomposition of the `k = 0` baseline — not one per member**, because the
> degeneracy predicate is evaluated on `C_0` alone. *(Scale reference, quoted as what it is:
> `z_statistics.s_eig`'s docstring gives `~1-3 min` at `10,694`, a LOCAL figure with runtime
> unestablished.)*
>
> **B.2's `1e-12` is therefore WITHDRAWN as a proposed value and retained only as a placeholder
> pending that ratio.** B.1's formula, B.3's floor and B.4's population handling stand.

**⚠ AND THE ROBUSTNESS WINDOW IS WIDER THAN I FIRST WROTE — measured, and I am correcting my own
understatement. ⚠ BUT READ THE REV. 2 BOX ABOVE FIRST: this window is measured against the TOP
eigenvector and is therefore the BEST case, not the binding one.** On a rank-4-of-40 operand the null direction's quotient is `8.86e-17` and a
supported direction's is `1.000`: **a separation of `6.1e17`**. Every `κ` from **`1e-14` to `1e-3`**
returns `DEGENERATE_FUNCTIONAL` on the null direction and `RESOLVED` on the supported one —
**seventeen orders, identical verdicts.**

**So `κ` is NOT a tuned number: it is any separator between round-off and support.** That is the
strongest thing I can say for it, and it is the same robustness property A-4's tolerance has.

**Why `1e-12` rather than the window's edge**, which is the only part of the choice that is a
judgement: the lower edge `1e-14` sits only **~5.5×** above the *worst* measured accumulation error
(`1.78e-15`), and that error was measured on a **1,200-dimensional stand-in**, not at `10,694`.
`1e-12` sits **~560×** above it. **I am buying margin against my own measurement's operand being
smaller than the real one** — which is the specific thing I cannot close without the constructed
`C_Z`.

## B.4 Failure outcomes — and ⚠ the acceptance population NEVER shrinks

**This is the sharper constraint and the answer is already the implemented behaviour, not a promise.**
A `DEGENERATE_FUNCTIONAL` verdict **refuses the entire evaluation**: `evaluate_a7` returns
`{"state": "DEGENERATE_FUNCTIONAL", "s_proj": None}` and **never** grades. The degenerate functional
is **not dropped from the max over `U`** and `s_proj` is **not** reported over a reduced set.

**Why that matters, in the campaign's own vocabulary:** dropping it would report `s_proj` over a
**different population than was declared** — the expected-count-selected-which-rows-I-kept shape —
and a PASS would mean less than it appears to. **So the population is preserved by REFUSING, not by
exclusion**, and the refusal is visible in the outcome rather than absorbed into it.

| outcome | trigger | reported |
|---|---|---|
| `DEGENERATE_FUNCTIONAL` | finiteness, structural (`q ≤ 0` exactly), or Rayleigh `< κ·λ_max` | the **offending functional indices**, `predicate` naming **which test decided**, `rayleigh` values. Routes to **branch 1**, `INCONCLUSIVE / WRONG FOOTING` |
| `KAPPA_UNDECLARED` | `κ` is `None` | refuses; **no default**. ⚠ Applies to **healthy** baselines too, so A-7 grades **nothing** until `κ` is declared |
| `GRADED` | every functional resolvable | `s_proj` with argmax offset **and** argmax functional |

**Every return carries the same key set** — a prior revision's branches did not, and
`out["predicate"]` raised `KeyError` on the structural path.

## B.5 Role, against Joseph's test

His test: *"do not use it to absorb support changes or scientifically meaningful variation."*

- **It cannot absorb a change of units.** The Rayleigh form is invariant under rescaling `u`;
  verified identical at `×1, ×10, ×100, ×10⁶`. The absolute form it replaced was **not**, and under
  it re-expressing P2's total from all-ones to width-weighted (`‖u‖²` changing ~1344×) could have
  moved a verdict with nothing numerical having changed.
- **It cannot absorb a support change.** A support change is classified by a **different**
  predicate, `classify_support_change`, which compares declared against observed masks and routes
  to `SUPPORT_DEFINITION_CHANGED`. `κ` is never consulted for it.
- **It cannot absorb scientifically meaningful variation**, because it gates the **baseline's own
  resolvability** before any member is compared — it is evaluated on `C_0` alone and has no access
  to the movement being graded.

**So `κ` is proposed as a NUMERICAL-VALIDITY SAFEGUARD, and the classification now rests on
properties of the predicate rather than on assertions about it.** ⚠ **If the reviewer finds any part
of it absorbing support change or meaningful variation, that part is Joseph's, not mine** — I am
proposing the role, not ruling on it.
