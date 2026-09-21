# DECISION 2026-09-20 — Joseph ADOPTS `z-cv.npz` as publication-under-exception

**THIS RECORD ADOPTS.** It is the executed form of
[`DRAFT-ADOPTION-20260919-z-cv-under-the-6.4-exception.md`](DRAFT-ADOPTION-20260919-z-cv-under-the-6.4-exception.md),
on that draft's terms.

**Whose act this is.** Joseph, 2026-09-20, in his own words: *"ADOPT
`uq_5d/z_pilot_20260916_a5/z-cv.npz`, sha256 `3d7465f6…`, variant cv, as publication-under-exception,
on the draft adoption record's terms."* Recorded by the scalar-5D lane at his instruction. **The
decision is his; the transcription and the measurements are this lane's.**

**CITABLE FOR:** the adoption of the one digest named below, and the four measurements §4 attaches
to it. **NOT CITABLE FOR** any other candidate, any re-grade, or the analysis-note push.

---

## 1. The adoption

    ADOPTS-SHA256: 3d7465f66fbe66b0dfcf09b6fc51249f227fb33e97ae40bc78dda90275e918c5

**Subject:** `uq_5d/z_pilot_20260916_a5/z-cv.npz`, **890,500,272** bytes, `variant: "cv"`.

**Re-hashed on the cluster immediately before this record was written**, as instructed —
`sha256sum` returned `3d7465f6…` exactly, `size 890500272`, `mtime 2026-09-17T00:34:23-0700`, and
the variant `cv` was read **from the product's own metadata**, not from its path. The product's own
fields are unchanged and stay as they are: `scientific_acceptance: NON-PASSING`, `adoptable: false`,
assembling revision `fb9ec356`.

## 2. The defect, in the same place as the decision

Per `DECISION-PACKET-20260918` §10.2, and not in an appendix:

- **`(cause 3, Z)`'s `M(i)` is `UNRESOLVED`**, `reject_conditions` **`4c`**, `branch = None`, for a
  **predeclaration failure**. It is permanent, it applies to the criterion, and **this adoption does
  not regrade it.**
- **`C3` stays "predeclared, not computed"** — Joseph, 2026-09-20. The 2026-09-20 two-member
  campaign computed `M(ii)` for **`361090f9…` and `7e4636a3…`**, which are *different products*.
  For **this** digest, cause 3 remains predeclared and not computed.
- **`SPEC` §6.4 requires the null bound fixed before production**, and production has happened. The
  derivation step is unperformable for this product by anyone, which is why this is an exception and
  not a repair.

## 3. The exception, and its exhaustion

`AMENDMENT-20260918-spec-6.4-candidate-specific-null-exception.md`, **EXECUTED 2026-09-18**.

> **It attaches to BYTES.** It covers `3d7465f66fbe66b0dfcf09b6fc51249f227fb33e97ae40bc78dda90275e918c5`
> **and nothing else** — explicitly including `361090f9…` and `7e4636a3…`, the two products of the
> 2026-09-20 campaign, which are graded, recorded and **not** adopted. There is nothing here for a
> later lane to inherit.

## 4. ⚠ FOUR MEASUREMENTS THAT TRAVEL WITH THIS DIGEST

**Joseph's instruction: these are measurements, not caveats.** Every deliverable built from this
adoption carries them.

**M1. `s_proj = 6.145%` against a `5%` bound.** The 2026-09-20 two-member campaign graded
`(cause 3, Z)`'s `M(ii)` **branch 5, NOT MET — PER-BIN**, on a fully valid campaign (all nine
validity fields passed). `s_agg = 0.471%` and `s_med = 0.485%` were within the bound; `s_proj`, the
only correlation-sensitive leg, was **`6.145%`**. Receipt
[`state/GRADE-20260920-cause3-two-member.json`](state/GRADE-20260920-cause3-two-member.json).
Digests graded / compared: `361090f9…` / `7e4636a3…`.

**M2. That `6.145%` is a reproducible property of the estimator, not resolution noise.** Measured
with the throws held fixed and only the estimator seed changed, `s_proj = 6.04% ± 0.39%` at
**N = 40, 80 and 160** — **flat, scaling exponent `p = 0.000`** — while the same-seed resampling
floor falls steeply over the same range, `20.91% → 7.57%`, `p = 1.467`. Statistical noise must fall
with `N`; this does not.
⚠ **The `± 0.39%` is scatter across throw subsets at ONE seed pair (`1000` vs `2200`). The width of
the seed-pair distribution is UNMEASURED**, and `s_proj` is a **maximum** over the declared offset
set, so more pairs can only raise it.

**M3. Five bands are outside what the seed variation probes.** Five of `C_Z`'s 45 bands —
`BeamAngleX`, `BeamAngleY`, `MuonResolution`, `Muon_Energy_MINERvA`, `Muon_Energy_MINOS` — are
produced at a literal `--seed 42` the offset hook **cannot reach** (`MNV_EST_SEED_OFFSET` appears
**0** times in all six files of that chain). They carry **26.0% of `√Tr C_Z`, 6.75% of the trace**
and contribute **zero** movement by construction. **The seed variation therefore does not probe the
seed sensitivity of those five bands; its effect on the total covariance when they also vary has not
been measured.**

> ⚠ **CORRECTED 2026-09-20. This cell read *"It is a LOWER bound … Letting them vary could only
> add"*, and that inference does not follow.** Withdrawn on the third-lane verification's finding
> `P1` ([`VERDICT-20260920-third-lane-c5-c7-verification.md`](VERDICT-20260920-third-lane-c5-c7-verification.md)),
> and the withdrawal is recorded at [`CORRECTION-20260920-lower-bound-inference-withdrawn.md`](CORRECTION-20260920-lower-bound-inference-withdrawn.md).
> **`s_proj` is a MAXIMUM of `|Δ√(uᵀCu)| / √(uᵀCu)` over the functional set** (`z_statistics.py:203`),
> **not a sum of nonnegative component magnitudes.** Releasing a held-fixed PSD component changes the
> statistic's operands rather than appending samples to the same maximum, so it can move the total in
> the **opposite** direction and **lower** the measured movement. The verifier's one-dimensional
> counterexample, on strictly positive components: `V₀ = L₀ = 1`, `C₀ = 2`; with the lateral block held
> fixed `V₁ = 1.2`, `L₁ = 1` gives `C₁ = 2.2` and `s_proj = 4.880885%`; letting it vary to `L₁ = 0.8`
> gives `C₁ = 2` and `s_proj = 0`.
> **THE MEASUREMENT IS UNCHANGED AND STILL TRAVELS:** five bands, `26.0%` of `√Tr C_Z`, `6.75%` of
> the trace, zero movement by construction. What is withdrawn is the direction of the unmeasured
> remainder. **M1's `6.145%` FAIL is untouched** — it is measured directly against a `5%` bound and
> never rested on this inference.

**M4. The estimator seed also moves the CENTRAL VALUES — by at most `6.0%` of their own
uncertainty.** On the 43 `M1` projection functionals the central value moves by median `0.104%`,
max **`0.761%`** — at **index 2, the same functional that failed `s_proj`** — against relative
uncertainties of median `10.1%`. As a fraction of the quoted uncertainty: **median `1.06%`, max
`6.02%`**; total rate `1.13%`. The same-seed control is `9.4e-13`, so the movement is ten orders
above the reproducibility floor and unambiguously real.
⚠ **Per individual 5D bin it is larger:** median `3.77%` of `σ`, p90 `13.6%`, **max `49.8%`**.
**Statements about a single 5D bin carry that; the projections do not, because aggregation
suppresses it.**

## 5. Identity, by measurement and not by filename

| | |
|---|---|
| path | `/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/uq_5d/z_pilot_20260916_a5/z-cv.npz` |
| `sha256` | `3d7465f66fbe66b0dfcf09b6fc51249f227fb33e97ae40bc78dda90275e918c5` |
| bytes | `890,500,272` |
| declared variant | **`cv`**, from the product's own metadata, enforced by `project_cov_nd.py --expect-variant` |
| assembling revision | `fb9ec3560fd6d62295dffc81b5694c9e26667d5b` |
| producing job | `58454524`, `ExitCode 2:0` — **2 is this CLI's completion code for "construction ran, science NON-PASSING"**, not a failure |

## 6. What this authorizes, and what it does not

**Authorizes:** `run_m1_projection.sh --run-class publication` against this digest, with
`MNV_ADOPTION_EXCEPTION` naming the executed §6.4 amendment and `MNV_EXPECT_VARIANT=cv`; and the
note and primer builds that quote its projections carrying §4.

**Does NOT authorize:** the analysis-note push, which Joseph holds; adoption of any other digest;
any re-grade; any new or revised bound; or a seed-averaged rebuild.

**Co-Authored-By: Claude Opus 5 (1M context)**
