# Rank deficiency and covariance inversion: what a consumer of the ND covariance must know

**Status:** prose, not code. Item 3 of the narrow freeze lift, 2026-08-10.

**One-line answer to the question that prompted it:** *no currently quoted significance is wrong.*
The 2D numbers that are published use a documented pseudo-inverse against a covariance that is
effectively full-rank, and every ND significance is explicitly **withheld**. But the `ndf`
convention the note states as a general definition becomes wrong by a factor of ~40 the moment it
meets the ND covariance, and the ND covariance is exactly what this lane is producing.

---

## 1. The fact

The standard-P4 5D candidate covariance is **numerically rank-deficient**, independently measured by
the product audit (`runs/standard-p4-verifier/20260810T0600Z-product-audit-5d-verdict.json`):

| | |
|---|---|
| dimension | 10 694 reported bins |
| **effective positive rank** | **263** |
| numerical nulls | 10 431 |
| condition number | numerically infinite |

The projected 4D object shows the same structure (4D leg: raw κ₂ `3.49e36`, numerical κ₂ infinite).

**This is not a defect.** It is what the object is: ~45 systematic bands, each a two-endpoint MAT
construction contributing very low rank, plus stat and ML blocks. A sum of ~45 low-rank outer
products cannot have rank 10 694. Both audit legs returned `CORRECT` with this present.

## 2. Two consequences a reader will not derive unaided

### 2a. The matrix cannot be inverted

Any χ², likelihood, or pull calculation using this covariance needs an **explicit pseudo-inverse or
regularisation, stated at the point of use.** `np.linalg.inv` on it is meaningless; it will not
raise, it will return numerical noise amplified by ~1e36. A naive inverse against a rank-deficient
covariance is the classic route to a confident wrong answer, because the smallest retained
eigenvalues dominate the quadratic form and they are precisely the least determined directions.

### 2b. The meaningful degrees of freedom are ~263, not ~10 694

A χ²/ndf quoted against the **bin count** for this covariance is wrong by a factor of **~40**. The
quadratic form `Δᵀ C⁺ Δ` with a rank-263 `C⁺` is a sum over 263 directions; dividing it by 10 694
divides by the wrong number and makes any tension look ~40× smaller than it is.

## 3. What is actually quoted today, checked rather than assumed

Every χ²/ndf in `docs/analysis-note/` was enumerated and traced to its covariance.

| value | location | covariance | inverse | verdict |
|---|---|---|---|---|
| `3.661` (paper-only), `1.481` (paper+ours) | `app_statmethods:613`, `sec_systematics:183` | 2D, 205 bins | `np.linalg.pinv`, documented at eq. (chi2) and §sec:invert | **safe** |
| `3.66` tension anatomy | `sec_results:114` | 2D, 205 bins | same | **safe** |
| `750.49` shape / `3.60` Jacobian shape-only | `app_statmethods:934`, `:966` | 2D | same | **safe** |
| `252`, `76.7` | `app_statmethods:793`, `:824` | 2D, diagnostic | explicitly labelled "naive pseudo-inverse", used to *demonstrate* a regularisation problem | **safe — it is the illustration, not a result** |
| `1.42` (73 dirs), `2.79` (139 dirs) | `app_statmethods:953` | 2D | explicit `pinv`-rcond scan | **safe — this is the robustness check** |
| `4.98` | `sec_3d:81` | **published 2D paper covariance** | — | **safe**, and explicitly hedged: "not a calibrated goodness-of-fit statistic" |

**The `ndf = 205` denominator is defensible in 2D**, and the note contains the evidence for that
without drawing the conclusion: the rank-truncation scan at `app_statmethods:953` rises *smoothly*
`0.69 (r=50) → 2.35 (100) → 3.30 (180) → 3.66 (205)` with no late jump. A covariance whose effective
rank were far below 205 would show a cliff or a plateau there. It does not, so in 2D the bin count
and the meaningful dimension are close enough that `ndf = n_reported` is not a material error.

### And no ND significance is quoted at all

- `sec_3d:278`: *"Historical 3D χ² values are **not quoted** pending the corrected covariance
  projection."*
- `ND_OMNIFOLD_STATUS.md`: the `(E_avail,W)` excess is recorded as *"exact significance **withheld**"*.
- The generator comparisons (GENIE CV, GENIE+Valencia MEC, NuWro, GiBUU) in `sec_eavailw` are quoted
  as **data/generator ratios and deficit fractions**, not as χ² or σ. Nothing there inverts a
  covariance.

**So the 40× hazard is not currently realised anywhere.** That is the honest answer, and it is a
better one than "the significances are fine" — they are fine *because the ND ones do not exist yet*.

## 4. Where it becomes live, and why it will be silent

The note states the convention **generally**, not as a 2D-specific choice
(`app_statmethods.tex:589`):

```
ndf = n_reported = 205,    χ²/ndf = χ²/205
```

`n_reported` is a variable. The corrected ND covariance projection — the thing this lane exists to
produce, and the thing `sec_3d:278` is waiting on — will supply `n_reported = 4825` or `10694`, and
the convention will carry across without anyone editing a line. **The failure mode is a
substitution, not a mistake**: the definition is correct in the regime it was written for and wrong
in the regime it is about to be used in, and nothing in the text marks the boundary.

**Required before any ND significance is quoted:**

1. State the inverse explicitly at the point of quotation — pseudo-inverse with its rcond, or the
   truncation rank, not merely a reference to the appendix.
2. **Use the retained rank as `ndf`, not the bin count.** For the current object that is ~263, and
   the exact number depends on the rcond chosen, so it must be reported with it.
3. Run the rank-truncation scan as in 2D and show it, because in ND it will *not* be smooth — the
   2D scan's smoothness is the evidence that made `ndf = 205` acceptable, and that evidence will not
   transfer.
4. Say which covariance: the 5D candidate, the projected 4D, or the published 2D. They have
   different ranks and different conventions apply.

## 5. Coordination

This touches both lanes and should not be duplicated. `docs/STATVAL_REPAIR.md` already carries the
matching requirement from the PET/statistics side — it calls the rank-deficient covariance plus
"truncated-spectral / pseudoinverse treatment" an *already-disclosed concern* (§ line 160) and
requires a **PREDECLARED rank/pseudoinverse cut** for the difference statistics (lines 170, 192,
207, 214). That is the same rule as §4.2 above, arrived at independently.

**What is new here** and is not in `STATVAL_REPAIR.md`: the measured rank of the *actual* standard-P4
covariance (263 of 10 694), the enumeration in §3 showing no currently quoted number is affected,
and the observation in §4 that the note's `ndf` definition is a general one that will silently
follow the covariance into a regime where it is wrong.

**Owner boundary:** the predeclared rank cut for the ND difference statistics is a statistics
decision and belongs with `STATVAL_REPAIR.md`, not with this lane. This document supplies the
measurement and the hazard; it does not choose the cut.
