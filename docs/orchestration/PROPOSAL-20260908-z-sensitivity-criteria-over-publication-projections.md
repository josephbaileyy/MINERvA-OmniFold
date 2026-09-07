# PROPOSAL — Z sensitivity criteria mapped to the publication's actual covariance consumers

**Authored 2026-09-08 by the Z spec/implementation lane, under `RZ`, at the coordinator's request.
NOTHING HERE IS ADOPTED.** `BEN-381` bars this lane from **grading** legs it drafted; it does not bar
this lane from **producing** a proposal — `SPEC-20260906-complete-scalar5d-successor-Z.md` §7 item 3
withdraws that misreading explicitly. An independent reviewer assesses this; only an explicit
decision adopts it. All four scientific boundaries remain **WITHHELD** and this document declares no
tolerance value.

---

## CITABLE FOR / NOT CITABLE FOR — read this before quoting anything below

**CITABLE FOR**

- what the publication path actually **consumes** from the assembled covariance, measured against
  code and the readiness record rather than inferred from the note's prose;
- the finding in §2, that **none of the four candidate statistics bounds the consumed quantity**;
- the mapping in §3 from each consumer to the statistic that *would* bound it;
- what evidence would justify a tolerance, and what evidence does not exist (§4, §5).

**NOT CITABLE FOR**

- any tolerance value. None is proposed, and §5 says why supplying one here would be a defect.
- any claim that a criterion is adopted, recommended for adoption, or ready for adoption.
- any claim about `C_Z`'s correctness. This is about what a criterion must *measure*, not about
  whether Z is right.
- the equivalence of the two projection-matrix builders (§6). That is an **unresolved premise**
  carried explicitly, not a result.

---

## 1. THE CONSUMER, MEASURED

`PUBLICATION-READINESS-20260822.md:885-888` (`PR-G10`, path CRITICAL) states what the covariance is
for:

> Rebuild exact 2D, 3D, 4D, `(E_avail,W)` and declared FPS marginals with explicit projection
> matrices; validate `M C Mᵀ` against direct block sums; recompute generator comparisons and
> **significances only from the governing adopted covariance**.

and `sec_summary.tex:35`, quoted at `:924`: *"no significance is quoted without a corrected projected
covariance."*

The displayed 5D summaries are **not** the consumer. Measured against the build graph at
`:149-163`: `paper_body.tex` contains no `\input`, the four `\gbdtFive*` magnitudes are reachable
only from `main_note.tex`, and `gbdtFive` / `sqrt` / `e-38` each count **0** in `paper_body.tex`.
**The external paper quotes no 5D covariance magnitude at all**, while retaining **12**
covariance-dependent claims (`grep -ciE covarian paper_body.tex`).

**So `D1`'s question — protect the displayed summaries, or scientific uses of the covariance? — is
already answered by the artifact: the displayed 5D summaries are not printed, and the scientific use
is the projection.** That is not this lane's judgement about what *should* matter; it is what the
build graph does.

### 1a. What the consumer computes, exactly

`eavail_generator_significance.py:107,132`:

```python
Cinv = np.linalg.pinv(C_y)            # C_y is the PROJECTED covariance
...
chi2 = float(d @ Cinv @ d)            # d = data - generator
```

with the significance following from `chi2` through `stats.chi2.sf`. **The published quantity is a
quadratic form in the PSEUDO-INVERSE of the projected covariance.**

The module says why this matters, in its own comment at `:98-101`:

> a highly-correlated systematic covariance (flux is a coherent normalization) can be near-singular
> -> **pinv amplifies shape directions** and inflates chi^2

and it prints the eigenvalue spectrum and condition number at `:102-105` precisely so a reader can
tell a significance from a numerical artifact.

---

## 2. THE FINDING: NONE OF THE FOUR CANDIDATES BOUNDS THAT QUANTITY

| statistic | where | what it measures | dominated by |
|---|---|---|---|
| `s_agg` | §3.7b | relative change in `√Tr C_Z` | the **largest** variances |
| `s_med` | §3.7b | relative change in the printed per-bin median `σ_i/x_i` | the **diagonal**, at its median |
| `s_proj` | `z_statistics.py:198` | relative change in `√(uᵀ C u)` over predeclared `u` | the **variance along each `u`** |
| `s_eig` | `z_statistics.py:256` | relative change in the **leading** eigenvalue | the **largest** eigenvalue |

The consumed quantity is `dᵀ (M C Mᵀ)⁺ d`. An inverse is dominated by the **smallest** retained
eigenvalues. Every statistic in the table is dominated by the large end of the spectrum — `s_eig`
explicitly so, by construction.

**Therefore a criterion built on any of the four can be satisfied while a quoted significance moves
arbitrarily.** The mechanism is not exotic and is not hypothetical: the covariance is
*deliberately* correlation-dominated because flux enters as a coherent normalization, so the small
eigenvalues are the shape directions, they carry tiny variance, and `pinv` amplifies exactly them.
A perturbation that leaves `Tr C`, the diagonal median, every predeclared `uᵀ C u` and the leading
eigenvalue within any tolerance can still move a near-null direction by a large *relative* amount —
and it is the relative movement of the small eigenvalues that propagates to `chi2`.

**This is the substantive result of the proposal, and it cuts against the cheapest option.** The
statistics that already exist and cost nothing are the ones that cannot bound the published claim.

---

## 3. CANDIDATE CRITERIA, MAPPED TO CONSUMERS

Each row states the statistic, its **denominator**, its **assumptions**, its **correlation
coverage**, and the **claim it would support** — the five fields `D1` requires. No tolerances.

### C-1 — direct sensitivity of the quoted statistic *(recommended as the primary candidate)*

- **Statistic.** `s_chi2 = max over the declared offset set of |chi2_k − chi2_0| / chi2_0`, for each
  (generator, projection) pair the publication actually quotes.
- **Denominator.** `chi2_0`, the `k = 0` as-built member's own value for that same pair — Z's own
  baseline, matching `D1b`'s rule that the denominator is Z's as-built member and never an external
  product.
- **Assumptions.** That the declared offset set is the population of interest (it is finite and
  declared, so the **max** is exact and no distributional inference is made — `D1a`'s own ground);
  and that `pinv`'s rank cutoff is held fixed across members. **The second is not currently pinned
  and must be** — see §4c.
- **Correlation coverage.** **Complete for the consumed quantity.** It measures the published number
  itself, so no correlation blindness survives.
- **Claim supported.** *"No declared estimator-baseline offset moves any quoted generator
  significance by more than the declared tolerance."* That is the statement the publication needs.
- **Cost.** Zero incremental production: it reuses the members `D3` would produce and the projection
  the note already builds. It is arithmetic on matrices that exist.
- **Limit.** It is a criterion on the *reported* statistic, so it inherits every modelling choice in
  `eavail_generator_significance.py`, including `pinv`'s cutoff and the `DIS ≥ 0.8` sub-block.
  Those become part of the declared criterion rather than free parameters.

### C-2 — the conditioning floor *(recommended as a companion, not a substitute)*

- **Statistic.** Relative change in the **smallest retained** eigenvalue of `M C Mᵀ`, and in the
  condition number, over the declared offsets — the two numbers `:102-105` already prints.
- **Denominator.** The `k = 0` member's own smallest retained eigenvalue.
- **Assumptions.** That "retained" is defined by the same cutoff the consumer uses. Same pin as C-1.
- **Correlation coverage.** Complete in the direction that matters for an inverse.
- **Claim supported.** *"The projected covariance's conditioning is stable under the declared
  offsets"* — which is the **precondition** for C-1 being interpretable rather than a second
  measurement of it. If conditioning is unstable, a stable `chi2` is luck.
- **Limit.** Says nothing about the central value; it is a stability statement about the operator.

### C-3 — `s_proj` over the *real* functionals *(retained, with its limit stated)*

- **Statistic.** `z_statistics.s_proj` (already implemented; **do not reimplement**) over the rows of
  the production projection matrix rather than synthetic ones.
- **Denominator.** `√(uᵀ C⁽⁰⁾ u)` per functional.
- **Correlation coverage.** Partial: it sees off-diagonal structure *along the declared `u`*, and is
  blind to the small-eigenvalue directions that drive C-1.
- **Claim supported.** *"Projected bin uncertainties are stable"* — a real and reportable property,
  and **not** a significance claim. It should not be described as covering one.
- **Wiring gap, measured 2026-09-08.** `s_proj`, `s_corr` and `s_eig` are implemented and are called
  **only from tests** (`test_z_validator.py:138-147`), and `s_proj` is exercised only over a
  hand-written `U = [[1,1],[1,-1]]` at `:139`. `z_validator` supports a correlation leg
  (`Leg.sees_correlations`; `correlation_leg_present` at `:224`) but **no declared leg set outside
  tests contains one.** The gap is the functionals and the leg declaration, not the statistic.

---

## 4. WHAT EVIDENCE COULD JUSTIFY A TOLERANCE

A tolerance on C-1 is justifiable from evidence that **already exists or is cheap**, and this is the
part `D1` has been missing:

**(a) The significance's own reporting granularity.** The publication quotes `Nsigma` to two
decimals (`:134`, `{z:7.2f}`). A movement that cannot change the second decimal of any quoted
`Nsigma` is, for the published claim, no movement at all. **This is a use-based argument, not a
formatting one** — the distinction `D1c` failed: the number is not "the format's resolution", it is
"the smallest change that could alter a reader's inference from the quoted result". It needs stating
as such and it needs the map from `chi2` movement to `Nsigma` movement, which is `stats.chi2.sf`
composed with `norm.isf` and is exact.

**(b) The decision the significance feeds.** If a quoted significance is used to say a generator is
or is not disfavoured, the tolerance is whatever cannot move it across the threshold that claim
rests on. That threshold is a scientific choice and it is **not in the tree** — it is the one input
that must come from the analysis, not from the code.

**(c) A pin that does not exist yet and must.** `np.linalg.pinv`'s default `rcond` is relative to
the largest singular value, so **the retained rank can differ between two members**. If it does,
`chi2_k` and `chi2_0` are quadratic forms on different subspaces and their difference is not a
sensitivity — it is an artifact. **Nothing currently pins it.** Pinning the cutoff is code, not
compute, and it is a prerequisite for C-1 and C-2 both.

---

## 5. WHAT REMAINS UNAVAILABLE, AND WHY NO NUMBER IS PROPOSED

- **(b) above is unavailable in this tree.** No artifact states what decision any quoted significance
  supports at what threshold. Without it a tolerance would be a number with a derivation and no
  purpose.
- **The members do not exist.** C-1 and C-2 are defined over a declared offset set; `D3` records
  that `N = 5` is a planning proposal and not demonstrated capacity, and that no run authorization
  (`D-RESOURCE`) exists. **These criteria are specifiable now and measurable only later.** That is
  the honest state and it is not an argument for adopting a cheaper criterion that measures the
  wrong thing.
- **Why this lane proposes no value.** A tolerance recommended here would be adopted with this
  lane's recommendation as its provenance, and this lane drafted the statistic. `BEN-381` permits
  the drafting and bars the grading; supplying the number would collapse the two.

---

## 6. UNRESOLVED PREMISE, CARRIED EXPLICITLY: WHICH `M`?

**Two projection-matrix builders exist in this tree and this proposal does not assume they agree.**

- `p4_lib.build_projection_M` (`p4_lib.py:1353`) — what `p4_project_4d.py:141` executes. It carries a
  bidirectional coverage check and an **independent reconstruction** by a deliberately different
  method (`:1455`), kept free of the first's helpers so the comparison means something.
- `project_cov_nd.build_projection` (`project_cov_nd.py:79`) — width-weighted marginalisation.
  **`s_proj`'s own docstring names this one** (`z_statistics.py:202`).

They share `AXIS_EDGES` — `p4_project_4d.py:46` calls it a canonical drift-guarded mirror — **and
nothing more**. No artifact in the tree establishes that the two produce the same `M`.

**Consequence for this proposal.** C-1 and C-2 are defined over `M C Mᵀ` for *the M the consumer
uses*, which is a fact about the publication path, not a free choice. C-3's functionals are named by
a docstring pointing at the *other* builder. Until equivalence is settled, "the projections" denotes
two objects and a criterion written over the phrase is measured against whichever one someone wires
in.

**What equivalence evidence would be required** — and it is bounded, a check rather than a study:

1. Both builders instantiated on the same edges, masks and drop axis, and `M₁ − M₂` compared
   elementwise to zero at float64 tolerance, for **every** projection the publication quotes — not
   one exemplar, since the builders may agree on the 4D case and differ where support masks bite.
2. If they differ, the **consumer's** builder wins by definition, and `s_proj`'s docstring is wrong
   and must be corrected rather than reinterpreted.
3. If they agree, record it as a measured agreement with both shas, not as an assumption retired.

Until (1) is run, **every use of `M` in §3 should be read as "the consumer's `M`, builder
unidentified"**, which is a weaker statement than it looks and is deliberately not smoothed over.

---

## 7. WHAT THIS PROPOSAL ASKS FOR

Nothing to be adopted. Three things to be **decided by whoever owns the decision**:

1. Whether the acceptance target is the **quoted significance** (C-1) rather than a covariance
   summary. §1 and §2 are the evidence; the judgement is not this lane's.
2. The threshold in §4(b) — the one input that cannot come from the code.
3. Whether the `pinv` cutoff pin in §4(c) is authorized as Tier-2 code work. It is a prerequisite
   for C-1 and C-2 and it changes no estimator default.

**No criteria owner exists.** `docs/orchestration/control-plane/owners.tsv` has twelve rows and none
of them is scientific acceptance criteria; the nearest register fit is `lane_c` (rulings / schema /
launcher policy) and every other row escalates to Joseph. That is a gap in the control plane, not a
gap in this proposal, and it is recorded here because a proposal with no assigned adopter is how a
recommendation becomes a de facto decision by default.
