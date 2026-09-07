# PROPOSAL — Z sensitivity criteria mapped to the publication's actual covariance consumers

**Authored 2026-09-08 by the Z spec/implementation lane, under `RZ`, at the coordinator's request.
NOTHING HERE IS ADOPTED.** An independent reviewer assesses this; only an explicit decision adopts
it. All four scientific boundaries remain **WITHHELD** and this document declares no tolerance value.

**⚠ REV. 2 (2026-09-08) — SIX REVIEWER FINDINGS, ALL SUSTAINED, ALL FIXED IN PLACE.** Rev. 1
overreached in five places and repeated one error it had itself criticised. Every correction is
carried in the section it affects rather than in a changelog, because a caveat at the end of a long
document is not a caveat. The rev. 1 claims that were **withdrawn**:

| # | rev. 1 claimed | withdrawn because |
|---|---|---|
| 1 | `s_proj` is dominated by large eigenvalues | **false in general.** A `u` aligned with a small eigenvector measures that mode. Rev. 2 replaced this with a proposed check, which rev. 3 also withdrew — see row 7. The question is left OPEN (§2b) |
| 2 | C-2 gives "complete correlation coverage" | **false.** `diag(1,4)` and `diag(4,1)` share every eigenvalue and condition number, yet for `d = (1,0)` give `chi2` of `1` and `1/4`. Eigenvectors matter (§3 C-2) |
| 3 | a relative `chi2` tolerance is a tolerance on the quoted significance | **false.** The map is `chi2.sf` then `norm.isf`, strongly nonlinear. C-1 is now defined on the significance itself (§3 C-1) |
| 4 | an unpinned `rcond` makes a rank change an "artifact" | **two errors.** A fixed cutoff policy is not a fixed retained subspace, and a rank discontinuity is a **sensitivity of the stated procedure**, to be reported, not dismissed (§4c) |
| 5 | two printed decimals justify a tolerance | **that is the `D1c` error, committed by me.** Rounding granularity bounds what COULD matter; it never establishes what DOES (§4a) |
| 6 | `BEN-381` is why this lane proposes no number | **the withdrawn misreading again.** Proposing is not adopting. The real reason is absent evidence (§5) |

**⚠ REV. 3 (2026-09-08) — FOUR FURTHER FINDINGS, ALL SUSTAINED.** Rev. 2's own repairs introduced
two new overclaims and left two others standing:

| # | rev. 2 claimed | withdrawn because |
|---|---|---|
| 7 | a §2b overlap test would settle `s_proj`'s sufficiency | **the test was dimensionally incoherent.** Rows of `M` live in INPUT space; eigenvectors of `M C Mᵀ` live in OUTPUT space. It also pointed at the modes `pinv` DISCARDS rather than the small modes it RETAINS, and an overlap would not prove a perturbation bound in any case. **Test removed; coverage left unresolved** (§2b) |
| 8 | a criterion looser than the printed precision is "certainly vacuous" | **false.** Printing precision sets no scientific floor and no ceiling. The retained "floor" was the same formatting error in smaller form (§4a) |
| 9 | the consumed form is "dominated by" the smallest retained eigenvalues | **too strong.** It CAN be sensitive to small retained modes, and only where `d` has overlap with them (§2a) |
| 10 | C-2 is a necessary precondition for interpreting C-1; pinning `rcond` reduces variation | **neither.** C-1 measures the reported quantity and is interpretable on its own terms. And the default `rcond` is ALREADY a policy — recording it improves reproducibility and removes no within-run variation (§3 C-2, §4c) |

---

## CITABLE FOR / NOT CITABLE FOR — read this before quoting anything below

**CITABLE FOR**

- what the publication path **intends** to consume from the assembled covariance (§1), and the
  explicit distinction between that and a **validated current path** (§1b);
- the structural argument in §2a that `s_agg`, `s_med` and `s_eig` cannot bound an inverse-quadratic
  consumer;
- that `s_proj`'s coverage over the declared functional set is **UNRESOLVED**, with no method offered
  (§2b) — cite the open state, not a direction;
- the three candidates and their claim limits (§3);
- what evidence would justify a tolerance and what does not exist (§4, §5).

**NOT CITABLE FOR**

- any tolerance value, or any claim that a criterion is adopted or ready for adoption.
- any claim that `s_proj` is *inherently* blind to shape directions. It is not (§2b).
- any claim about a **current** significance number. The ones in the tree are **GATED** (§1b).
- the equivalence of the two projection-matrix builders (§6) — an unresolved premise, not a result.

---

## 1. THE CONSUMER

### 1a. What the publication intends to consume

`PUBLICATION-READINESS-20260822.md:885-888` (`PR-G10`, path CRITICAL):

> Rebuild exact 2D, 3D, 4D, `(E_avail,W)` and declared FPS marginals with explicit projection
> matrices; validate `M C Mᵀ` against direct block sums; recompute generator comparisons and
> **significances only from the governing adopted covariance**.

and `sec_summary.tex:35`, quoted at `:924`: *"no significance is quoted without a corrected projected
covariance."*

The displayed 5D summaries are not that consumer. Measured against the build graph at `:149-163`:
`paper_body.tex` contains no `\input`, and `gbdtFive` / `sqrt` / `e-38` each count **0** in it, while
**12** covariance-dependent claims remain. **The external paper quotes no 5D covariance magnitude at
all.** So `D1`'s question is answered by the artifact rather than by anyone's judgement: the
displayed summaries are not printed, and the intended scientific use is the projection.

### 1b. ⚠ THE CODE BELOW IS A NAMED INSTANCE OF THE MAP, NOT A VALIDATED CURRENT PATH

`eavail_generator_significance.py` shows what this class of consumer **computes**. It is **not**
evidence about any current number, and this proposal does not present it as one:

- `INTEGRATION_CHECKLIST.md:37`: *"**The covariance-dependent significances remain GATED**"*.
- Its covariance is quarantine **cause 6**, `PUBLICATION-READINESS-20260822.md:892`, `KNOWN_ISSUES`
  #36 (HIGH, OPEN): the `(E_avail,W)` covariance *"has not been rebuilt after fixing its
  per-universe flux normalization"*, and `VL67` records cause 6 as **OPEN and furthest** — no
  `(E_avail,W)` product has been rebuilt at all.
- `SPEC §…:2354` names `eavail_generator_significance.py:83-89` as a validated instance of the
  **projection map**, which is a narrower statement than validation of its significances.

**What it is cited for here: the FORM of the consumption.** `:107,132`:

```python
Cinv = np.linalg.pinv(C_y)            # C_y is the PROJECTED covariance
chi2 = float(d @ Cinv @ d)            # d = data - generator
```

with the significance following through `stats.chi2.sf` and `norm.isf` (`:110-114`). **The consumed
quantity is a quadratic form in the pseudo-inverse of the projected covariance.** That form is what
the criteria below must bound; whether any particular current output is trustworthy is a different
question with a different owner, and it is gated.

The module states the hazard in its own comment at `:98-101`:

> a highly-correlated systematic covariance (flux is a coherent normalization) can be near-singular
> -> **pinv amplifies shape directions** and inflates chi^2

and prints the spectrum and condition number at `:102-105` so a reader can tell a significance from
a numerical artifact.

---

## 2. WHAT A CRITERION MUST BOUND, AND WHICH CANDIDATES CANNOT

### 2a. The structural half, which stands

`dᵀ (M C Mᵀ)⁺ d` **can be strongly sensitive to the smallest RETAINED modes of the projected
covariance — and only where `d` has overlap with them.** ⚠ Rev. 2 said "is dominated by"; that is too
strong, and the qualifier is not cosmetic: if `d` is orthogonal to the small retained modes they do
not matter, so the sensitivity is a property of the (covariance, `d`) pair rather than of the
covariance alone. Note also that modes BELOW `pinv`'s cutoff are **discarded**, not amplified; the
amplified ones are the small modes just above it.

- **`s_agg`** is a relative change in `√Tr C`. A trace is a **sum** of eigenvalues, so a near-null
  mode contributes negligibly to it while dominating the inverse. A perturbation can move the
  inverse arbitrarily and `Tr C` immeasurably.
- **`s_med`** is the **median of the diagonal** — a summary of per-bin variances, carrying no
  information about the directions the inverse amplifies.
- **`s_eig`** measures the **leading** eigenvalue, explicitly and by construction the wrong end.

**These three cannot bound the consumed quantity, and that argument does not depend on any property
of the declared functional set.**

### 2b. ⚠ `s_proj` IS NOT INHERENTLY BLIND, AND ITS SUFFICIENCY IS LEFT UNRESOLVED

`s_proj` measures `√(uᵀ C u)`. **If `u` is aligned with a small eigenvector, that is a mode the
inverse can amplify, and `s_proj` sees it.** The statistic is not the problem, and rev. 1's claim
that it was is withdrawn.

Whether `s_proj` over the **declared, finite** functional set suffices to bound the consumed
quantity is **open, and this proposal does not attempt to settle it.**

**⚠ REV. 2 PROPOSED A TEST FOR THIS AND THE TEST WAS WRONG. IT IS REMOVED RATHER THAN REPAIRED.**
It asked for the overlap of each declared `u` with the eigenbasis of `M C Mᵀ`. Three independent
defects: the rows of `M` are vectors in **input** space while the eigenvectors of `M C Mᵀ` are in
**output** space, so the overlap is not even dimensionally defined; it pointed at the modes below
`pinv`'s cutoff, which are **discarded** rather than amplified; and an overlap figure would not
constitute a perturbation bound even if both spaces matched. **No replacement test is offered here.**
Establishing coverage for `s_proj` over the declared set is real work with a real method, and
inventing a second wrong one in the same document would be worse than leaving the question open.

### 2c. And a bound on the spectrum alone is not a bound on the consumer

From the reviewer, and it corrects rev. 1's C-2: `diag(1, 4)` and `diag(4, 1)` have identical
eigenvalues, identical smallest eigenvalue and identical condition number. For `d = (1, 0)` they
give `chi2 = 1` and `chi2 = 1/4`. **Eigenvalues do not determine the quadratic form; eigenvectors and
their alignment with `d` do.** Any candidate expressed purely in spectral summaries inherits this
limit, C-2 included.

---

## 3. CANDIDATE CRITERIA

Five fields each — statistic, denominator, assumptions, correlation coverage, claim supported. **No
tolerances.**

### C-1 — sensitivity of the quoted significance itself *(primary candidate)*

- **Statistic.** `s_sig = max over the declared offset set of |Nsigma_k − Nsigma_0|`, per
  (generator, projection) pair the publication quotes. **An ABSOLUTE difference in a quantity
  already expressed in sigma units.**
- **Why absolute, and why on `Nsigma` rather than `chi2` — ⚠ REV. 1 GOT THIS WRONG.** A relative
  `chi2` tolerance is **not** a tolerance on the significance: the map is `chi2.sf` composed with
  `norm.isf` and is strongly nonlinear, so one relative `chi2` change produces different `Nsigma`
  movements depending on `chi2` and `ndf`. Defining the statistic on the reported quantity removes
  the mapping question instead of hiding it. It also **removes the `chi2_0 = 0` denominator
  problem** rev. 1 had: there is no denominator. (`Nsigma` is `inf` when `p = 0`; the statistic is
  undefined for such a pair and must be **reported as undefined**, never as zero movement.)
- **Denominator.** None. Where a relative form is wanted for `chi2` as a secondary diagnostic, the
  denominator is `chi2_0`, Z's own `k = 0` member per `D1b`, and it is undefined at `chi2_0 = 0`.
- **Assumptions.** The declared offset set is the population of interest, so the **max** is exact and
  no distributional inference is made (`D1a`'s own ground); and the `pinv` cutoff **policy** and the
  retained **rank** are both recorded per member (§4c).
- **Correlation coverage.** Complete **for the pairs measured** — it evaluates the published number,
  so no blindness survives *within that set*. It says nothing about pairs not in the declared set.
- **Claim supported.** *"No declared estimator-baseline offset moves any quoted generator
  significance, among the declared (generator, projection) pairs, by more than the declared
  tolerance."*
- **Cost.** Zero incremental production: arithmetic over members `D3` would produce and a projection
  the note already builds.
- **Limit.** It is a criterion on a **reported procedure**, so it inherits every modelling choice in
  that procedure — the `pinv` cutoff, the `DIS ≥ 0.8` sub-block, the generator set. Those become
  part of the declared criterion rather than free parameters, and the criterion must be re-derived
  if the procedure changes.

### C-2 — the conditioning diagnostic *(companion; ⚠ NOT coverage)*

- **Statistic.** Relative change in the smallest retained eigenvalue of `M C Mᵀ`, in the condition
  number, and **in the retained rank** — the numbers `:102-105` already prints, plus the rank.
- **Denominator.** The `k = 0` member's own value for each.
- **Correlation coverage.** ⚠ **NOT complete, and rev. 1's claim that it was is withdrawn.** §2c's
  counterexample shows a spectral summary cannot determine the quadratic form. This is a
  **diagnostic on the operator**, not a bound on the consumer.
- **Claim supported.** *"The projected covariance's conditioning and retained rank are stable under
  the declared offsets."* ⚠ Rev. 2 called this a **precondition** for interpreting C-1; that is
  withdrawn. C-1 measures the reported quantity directly and is interpretable on its own terms.
  C-2 is **informative context** — if conditioning or rank moves, that is worth knowing beside a
  stable `s_sig` — and it is not mathematically necessary for C-1 to mean what it says.
- **Limit.** Says nothing about central values, and by §2c nothing about the consumed form.

### C-3 — `s_proj` over the real functionals *(retained; scope now honest)*

- **Statistic.** `z_statistics.s_proj` — **already implemented at `z_statistics.py:198`; do not
  reimplement** — over the rows of the production projection matrix rather than synthetic ones.
- **Denominator.** `√(uᵀ C⁽⁰⁾ u)` per functional.
- **Correlation coverage.** Sees off-diagonal structure **along the declared `u`**. Whether that
  reaches the inverse-relevant directions is **unresolved** (§2b) — neither a settled negative nor a
  demonstrated sufficiency. C-3 must therefore be quoted for its projected-bin claim only.
- **Claim supported.** *"Projected bin uncertainties are stable under the declared offsets."* A real,
  reportable property, and **not** a significance claim.
- **Wiring gap, measured 2026-09-08.** `s_proj`, `s_corr` and `s_eig` are implemented and called
  **only from tests** (`test_z_validator.py:138-147`); `s_proj` is exercised only over a hand-written
  `U = [[1,1],[1,-1]]` at `:139`. `z_validator` supports a correlation leg (`Leg.sees_correlations`;
  `correlation_leg_present` at `:224`) but no declared leg set outside tests contains one. **The gap
  is the functionals and the leg declaration, not the statistic.**

---

## 4. WHAT EVIDENCE COULD JUSTIFY A TOLERANCE

### 4a. ⚠ WHAT CANNOT: THE PRINTED PRECISION. REV. 1 MADE THE `D1c` ERROR IT CRITICISED.

Rev. 1 argued that a movement unable to change the second decimal of a printed `Nsigma` is no
movement, and called this "use-based, not formatting". **It is a formatting argument wearing a
use-based label, and it is exactly the reasoning `D1c` was withdrawn for.** Two independent defects,
both of which `D1c` also had:

- **it errs in both directions at a rounding boundary** — `2.4499` and `2.4501` print differently
  and are indistinguishable scientifically, while `2.451` and `2.549` print the same at one decimal
  and are not;
- **it presumes the decision depends on the printed digits**, when it depends on the **margin** to
  whatever threshold the claim rests on.

**Printed granularity establishes nothing scientific, in either direction.** ⚠ Rev. 2 retained it
"as a floor — a criterion looser than the printing is certainly vacuous". That is withdrawn too, and
it was the same error one size smaller: printing precision sets no scientific floor and no ceiling.
A display choice constrains no tolerance.

### 4b. WHAT COULD: THE DECISION MARGIN

If a quoted significance supports a claim that a generator is or is not disfavoured at some
threshold, the justified tolerance is the one that cannot move `Nsigma` across the **margin** between
its value and that threshold — a margin, not a rounding step. **That threshold is a scientific
choice and it is not in this tree.** It is the one input that must come from the analysis.

### 4c. ⚠ A PREREQUISITE, RESTATED AFTER TWO REVIEWER CORRECTIONS

`np.linalg.pinv` is called with **no `rcond`** (measured: zero occurrences of `rcond` in that
module), so its cutoff is relative to the largest singular value and moves with each member.

Rev. 1 concluded "pin it, and a rank change is otherwise an artifact". **Both halves were wrong:**

- **A fixed cutoff policy is not a fixed retained subspace.** Pinning `rcond` does not pin the rank:
  an eigenvalue crossing a *fixed* threshold between members changes the retained subspace anyway.
  Pinning removes one source of variation, not the phenomenon.
- **A rank discontinuity is a sensitivity of the stated procedure, not automatically an artifact.**
  If the declared criterion is "the significance this procedure reports", then a member whose rank
  differs *is* a member on which the procedure behaves differently, and that is a finding.

**So the requirement is REPORTING, not suppression:** record the cutoff actually applied and the
retained rank per member, and treat a rank change as a **reportable event that blocks a bare pass** —
the criterion must state what it does when rank moves, rather than averaging over it.

⚠ Rev. 2 said pinning `rcond` is "a reduction in variation". Withdrawn: **the default is already a
policy**, deterministic given the matrix. Recording it explicitly improves reproducibility and
auditability; it removes no within-run variation, because there was none to remove.

---

## 5. WHAT REMAINS UNAVAILABLE, AND WHY NO NUMBER IS PROPOSED

- **§4b's threshold does not exist in this tree.** No artifact states what decision any quoted
  significance supports at what margin. **This is the reason no tolerance is proposed:** a number
  without it would have a derivation and no purpose.
- **The members do not exist.** `D3` records `N = 5` as a planning proposal rather than demonstrated
  capacity, with no `D-RESOURCE`. These criteria are **specifiable now and measurable only later** —
  the honest state, and not an argument for a cheaper criterion that measures the wrong thing.
- **`s_proj`'s sufficiency over the declared functional set is unresolved** (§2b), and this
  proposal offers no method for settling it.

**⚠ REV. 1 GAVE A SECOND REASON AND IT WAS WRONG.** It said supplying a number would collapse
`BEN-381`'s drafting/grading separation. **Proposing a tolerance is neither adopting nor grading it**
— `SPEC §7 item 3` withdraws that exact misreading, and rev. 1 reproduced it after being corrected on
it once. `BEN-381` bars this lane from **grading** these legs and bars nothing else. The absence of
evidence is a sufficient reason on its own and is the only one claimed.

---

## 6. UNRESOLVED PREMISE, CARRIED EXPLICITLY: WHICH `M`?

**Two projection-matrix builders exist and this proposal does not assume they agree.**

- `p4_lib.build_projection_M` (`p4_lib.py:1353`) — executed by `p4_project_4d.py:141`; carries a
  bidirectional coverage check and an **independent reconstruction by a deliberately different
  algorithm** (`:1455`, vectorised `unravel_index`/`ravel_multi_index`/`searchsorted` against a
  per-column Python loop), kept free of the first's helpers so the comparison means something.
- `project_cov_nd.build_projection` (`project_cov_nd.py:79`) — width-weighted marginalisation.
  **`s_proj`'s own docstring names this one** (`z_statistics.py:202`).

They share `AXIS_EDGES` — `p4_project_4d.py:46` calls it a canonical drift-guarded mirror — **and
nothing more.** No artifact establishes that they produce the same `M`.

**What equivalence evidence would be required** — bounded, a check rather than a study:

1. Both builders instantiated on the same edges, masks and drop axis, and `M₁ − M₂` compared
   elementwise to zero at float64 tolerance, for **every** projection the publication quotes — not
   one exemplar, since they may agree on the 4D case and differ where support masks bite.
2. If they differ, the **consumer's** builder wins by definition, and `s_proj`'s docstring is wrong
   and must be corrected rather than reinterpreted.
3. If they agree, record a measured agreement with both shas — not an assumption retired.

Until (1) is run, **every `M` above reads as "the consumer's `M`, builder unidentified"**, which is
weaker than it looks and is deliberately not smoothed over.

---

## 7. WHAT THIS PROPOSAL ASKS FOR

Nothing to be adopted. Four things to be **decided or run by whoever owns them**:

1. Whether the acceptance target is the **quoted significance** (C-1) rather than a covariance
   summary. §1 and §2a are the evidence; the judgement is not this lane's.
2. The threshold and margin in §4b — the one input that cannot come from the code.
3. Whether the §6 builder comparison is authorized as Tier-2 work. It is code, not compute, and it
   changes the proposal's own conclusions if it comes out the other way. **`s_proj`'s coverage
   question (§2b) is NOT included here**: it needs a method this proposal does not have, and asking
   for authorization to run an unspecified check would be asking for a blank cheque.
4. Whether the `pinv` cutoff **policy** should be pinned and the retained **rank** reported per
   member (§4c). It changes no estimator default.

**No criteria owner exists.** `docs/orchestration/control-plane/owners.tsv` has twelve rows and none
is scientific acceptance criteria; the nearest register fit is `lane_c` (rulings / schema / launcher
policy) and every other row escalates to Joseph. Recorded because a proposal with no assigned adopter
is how a recommendation becomes a decision by default.
