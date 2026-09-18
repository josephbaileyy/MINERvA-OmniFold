# DRAFT CONTRACT — the consumer that turns the adopted trunk into the deferred significance

**Status: DRAFT FOR APPROVAL. Nothing here is adopted, no significance is computed, no historical
significance is reinstated, and neither existing consumer was run.** Rank 6 of the audit
`ebba67ab`. Milestone `M-O` of `PLAN-20260918-scalar5d-publication-completion.md`.

**CITABLE FOR:** §1's prespecification finding and §2's measured defects, both source-dated.
**NOT CITABLE FOR:** any significance, any tolerance, or any claim that the contract is approved.

**The claim this exists to support**, verbatim from `main_paper.tex:49-51` — the only
covariance-dependent claim in the twenty-source note/primer/paper corpus:

> *"They recover the established low-recoil discrepancy and **localize a generator deficit in the
> joint high-available-energy, high-mass region**. The latter is a central-value result; its
> significance awaits adoption of a common five-dimensional covariance."*

---

## 1. ⚠ The region is HALF prespecified and HALF data-selected, and the record says so

This is the finding that most changes what the contract has to contain, and it is dated from the
repository rather than argued.

| Element | First recorded | Relative to the data |
|---|---|---|
| **"Open question 6"** — the high-`E_avail` DIS-tail excess, as a *question* | **2026-06-03**, `de84c61e`, *"Design doc: higher-dim OmniFold…; record pre-pub items"* | **Before** the W axis existed |
| The W axis and the first `(E_avail, W)` excess test | **2026-06-07**, `95ce2950`, *"Workstream F: (E_avail, W) excess test"* | — |
| **The high-W corner as a region**, and `W >= 1.8` in code | **2026-06-09**, `b64cf582` | **Two days after** the excess test |
| `E_avail >= 0.8` in code | **2026-06-09**, `b64cf582` | Same commit |

And `HIGHER_DIM_OMNIFOLD_DESIGN.md:167-169` states the mechanism in its own words: the W axis
*"recovers the frozen 4D to 0.11%, and **it localizes open question 6 to the high-W DIS corner**."*

**So the `E_avail` question was prespecified and the `W ≥ 1.8` boundary was localized from the data.**
A *localization* claim — which is what the paper actually makes — is honest at central-value level.
Converting it to a **significance on the same boundary that the data chose** is what needs
selection-aware treatment.

⚠ **Scope of this dating, stated because the instrument is limited.** `git log -S` dates the
**commit**, not when an analyst formed an intention, so the strict claim is that **no record of
`W ≥ 1.8` exists before 2026-06-09**. Absence of an earlier record is not proof that the choice was
post-hoc. What upgrades it from absence to affirmative evidence is the design document's own verb:
*"localizes"*. That is a statement that the region came out of the measurement.

### 1.1 And the two existing consumers do not use the same region

- `eavail_generator_significance.py:106` — `E_avail >= 0.8`, described at `:15` as *"the DIS tail"*.
  Selects **3 of 7** `E_avail` bins.
- `eavailW_covariance.py:547` — `E_avail >= 0.4` **and** `W >= 1.8`. Selects **4 of 7** `E_avail`
  bins and **3 of 6** `W` bins: a **12-of-42** corner.

**Two different regions are both called "high-`E_avail`", and they differ by a whole bin of
`E_avail`.** Whichever is intended must be named before a number is produced, because the two are
not the same hypothesis.

⚠ **A small independent defect, flagged because it will mislead a reader:**
`eavailW_covariance.py:545`'s comment says *"W >= 1.8 GeV (bins 2..5)"*, but `W`'s lower edges are
`[0, 1.1, 1.4, 1.8, 2.2, 3.0]`, so `>= 1.8` selects indices **3, 4, 5** — three bins, not the four
the comment describes. The **code is right and the comment is wrong**; a reader checking the region
against the comment would believe it extends down to `W = 1.4`.

---

## 2. What the existing consumers actually do — measured, not inferred

Neither was run. Both are **source** findings at main `c147459b`.

| # | Finding | Evidence |
|---|---|---|
| 1 | `pinv` is called with **no explicit `rcond`**, so the retained subspace is whatever the default gives and is never declared | `eavail_generator_significance.py:107-108`; `eavailW_covariance.py:544,549` |
| 2 | The author already knew the hazard: *"can be near-singular -> pinv amplifies shape directions"* | `eavail_generator_significance.py:99` |
| 3 | Degrees of freedom are the **bin count**, not a retained rank — the printed header is literally `chi2/ndf(all7)` | `eavail_generator_significance.py:117-118` |
| 4 | Eigenvalues are **printed** but no retained-rank declaration, truncation scan or null calibration is implemented | audit rank 6, confirmed |
| 5 | Neither consumes the 5D trunk. `eavailW_covariance.py` builds its **own** component sum and obtains the detector part by marginalising 4D lateral bands to `E_avail`, taking the per-`E_avail` variance as fractional and spreading it over `W` — self-documented at `:445-448` as *"flat-in-W fractional — documented approximation"* | source |
| 6 | The product of that path is **`QUARANTINED` and unquotable** by the front door, so it cannot be repaired into the claim by re-pointing an input | `AGENTS.md:30` |

**Consequence.** The replacement consumer is new code against the adopted trunk, not a patch. And
`C_Z` is heavily rank-deficient — `λ_min = −1.275e-90` with 5,214 negative eigenvalues of 10,694 —
so items 1–3 are not pedantry: an undeclared `rcond` on a rank-deficient matrix chooses the
hypothesis silently.

---

## 3. The eight declarations the contract must fix, before any number

Each is stated as what must be **declared**, with the reason it cannot be deferred.

1. **Residual and null.** The residual is `data − generator` on the declared region; the null is the
   generator being tested. Both generators and the data pairing must be named, because `--gens`
   defaults to a list of files and a missing file currently prints *"not yet generated"* and
   continues.
2. **Covariance product and its central pairing.** `C = M1 C_Z M1ᵀ` with `M1` the declared
   `5D → (E_avail, W)` map, paired with `M1 x_5D` — the **marginalised** central value, **not** an
   independently unfolded 2D estimator. The two differ by ~3% by construction and that difference
   is not an error.
3. **Retained subspace.** An explicit `rcond`, the retained rank it yields, **and** a truncation
   scan showing the significance as a function of it. A single undeclared `pinv` is not a
   specification. **The retained rank is the ndf candidate; the bin count is not.**
4. **Degrees of freedom.** Declared from the retained rank, with the justification. ⚠ The audit's
   prohibition stands: **do not apply a generic Hartlap factor**, and **do not call rank alone a
   calibrated ndf** — a rank is a property of the matrix, a calibrated ndf is a property of the
   null distribution, and `C_Z` is a sum of band outer products plus stat and ML blocks to which no
   single-ensemble factor applies (`OI-137`, with two withdrawn attempts on the record).
5. **Region, and its selection treatment.** Name the region — `0.8` or `0.4` (§1.1) — and state its
   prespecification status per §1. If the `W ≥ 1.8` boundary is retained, the calibration must be
   selection-aware or the claim must stay at central-value level.
6. **Fitted parameters and data reuse.** Any normalisation or shape parameter fitted to the same
   data reduces the effective ndf. Declare what is fitted, on what data, and whether the same events
   entered the unfolding.
7. **Finite-ensemble conventions per block.** The stat and ML blocks are mean-centred with `N−1`;
   the joint-throw ensemble enters as **diagonal inflation** at MAT `1/N` and is **not** a fourth
   covariance block. These are different conventions on different objects and must not be pooled —
   `combine_cov_nd.py` now records `n_members` and the divisor **in the artifact**, so the consumer
   can read them rather than assume.
8. **What a terminal result cannot authorize.** Per `AGENTS.md`'s next-action discipline, the
   specification states in advance what a computed significance would *not* establish: coverage of
   the reported band, validity of any other projection, or promotion of any historical number.

---

## 4. What this needs from Joseph — one new judgment, and it is not a routing request

**`τ`'s threshold (D3) remains as recommended.** Unchanged by this draft.

⚠ **NEW — D5, surfaced by §1 and genuinely unavoidable: the intended claim's region is partly
data-selected, so one of three must be chosen.**

| Option | What it costs | What it yields |
|---|---|---|
| **(a)** Selection-aware calibration for the `W` boundary | A calibration design, and it is the only option needing new methodology | The joint claim at a defensible significance |
| **(b)** Quote the significance on the **prespecified `E_avail`** region only; keep the `W` localization at central-value level | Nothing new — and it is close to what the paper already says | A clean claim on a narrower region |
| **(c)** Argue `W ≥ 1.8` was prespecified | — | **Not supported by the record**; the design doc says *"localizes"* |

**Recommended: (b).** It is the only option that requires no new methodology, it keeps the strongest
part of the claim, and the paper's existing wording already separates the localization from the
significance. **This is a scientific judgment about claim scope, not an engineering choice** — which
is why it is yours; the publication claim affected is the single deferred one.

**Also needed, and smaller:** resolve `E_avail ≥ 0.8` versus `≥ 0.4` (§1.1). Recommended: **`≥ 0.8`**,
the boundary the design document's *"DIS tail"* language and the older consumer both use.
