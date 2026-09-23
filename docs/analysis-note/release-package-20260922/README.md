# Appendix F result package — assembled 2026-09-22, IN-REPO, **NOT SHIPPED**

**CITABLE FOR:** the identity, contents and self-checks of this package.
**NOT CITABLE FOR:** publication readiness, any grade, or any claim that the scalar-5D adoption is
qualified differently than its adoption record says.

⚠ **THIS HAS NOT BEEN RELEASED.** `docs/analysis-note/app_release.tex` specifies an **external**
release. Assembling it in the repository is packaging work and is authorized; **uploading,
publishing, or sending it to any external service, host or collaborator is reserved to Joseph** and
has **not** happened. There is still **no release tag and no release manifest** — measured
2026-09-22 at `origin/main`, unchanged from the appendix's own census.

| | |
|---|---|
| built at | `origin/main = 9e78a8cf`, on Perlmutter under `mnv_guarded_run.py` (1 checkout root) |
| corrected at | this README has been corrected repeatedly; **a single sha here goes stale on the next correction and did** (it read `0d913d43`, four corrections behind). Authoritative history: `git log -- docs/analysis-note/release-package-20260922/README.md`. Mirrored to the standalone note repository. |
| builder | `docs/orchestration/probes/probe-20260922-build-appendix-f-package.py` (committed at `38836db7`). ⚠ This row read `nd-unfolding/build_appendixF.py`, which **exists at no commit** (`git log --all --oneline -- <path>` is empty). ⚠ The committed copy is **not runnable from its committed location**: it inserts its own directory on `sys.path` and does `import project_cov_nd`, which lives in `nd-unfolding/`. Run it with `PYTHONPATH=nd-unfolding`. |
| source trunk | `sha256 3d7465f66fbe66b0dfcf09b6fc51249f227fb33e97ae40bc78dda90275e918c5` |
| projection | `sha256 835828bf3e25bbd9f279088e5cc89b8b325d727446fec9fabbbc92fd7e71a54e` |

## 1. ⚠ THE FOUR MEASUREMENTS TRAVEL WITH THIS PACKAGE

Appendix F schema item 10 requires them **in** the package, *"since the package is what a reader
will quote from."* Stated, not referenced. Source:
`docs/orchestration/DECISION-20260920-joseph-adopts-z-cv-under-the-6.4-exception.md` §4.

- **M1 — `s_proj = 6.145%` against a `5%` bound fixed before production.** `(cause 3, Z)`'s `M(ii)`
  graded **branch 5, NOT MET — PER-BIN** on a fully valid campaign. `s_agg = 0.471%` and
  `s_med = 0.485%` were inside the bound; `s_proj`, the only correlation-sensitive leg, was not.
  **This is why no generator significance is quoted anywhere.**
- **M2 — the effect is flat in `N` over the tested `40`–`160`** (`6.04% ± 0.39%`, exponent
  `p = 0.000`) while the same-seed resampling floor falls `20.91% → 7.57%` (`p = 1.467`), **so the
  failing leg is not reporting its own resampling noise.** ⚠ **The corollary *"a larger ensemble
  would not reduce it"* is WITHDRAWN**: the `40`- and `80`-throw points are **nested subsets of one
  160-throw ensemble at ONE seed pair**, so larger `N` and the seed-pair width are **unmeasured**.
  ⚠ **The direction of the unmeasured remainder is not known either**, and the `± 0.39%` is scatter
  across throw SUBSETS at one seed pair — **the width of the seed-pair distribution HAS NOT BEEN
  MEASURED.** ⚠ **AND THE FAILING LEG CAN ONLY GET WORSE WITH MORE PAIRS:** `s_proj` is a
  **maximum over the declared offset set**, so *"more pairs can only raise it"*. Restored
  2026-09-22 — a second independent reviewer found this clause still missing after a first repair
  claimed to have restored the dropped M2/M3/M4 text, and it is the most adverse of them all.
- **M3 — five bands (`BeamAngleX`, `BeamAngleY`, `MuonResolution`, `Muon_Energy_MINERvA`,
  `Muon_Energy_MINOS`) are seed-pinned and contribute zero movement by construction**, carrying
  `26.0%` of `√Tr C_Z` and `6.75%` of the trace **out of the ~45 MAT bands** — so this is a
  statement about five bands of that set and not about the covariance as a whole. ⚠ **The *"lower bound"* reading is WITHDRAWN**:
  `s_proj` is a **maximum** over the functional set, not a sum of nonnegative magnitudes, so
  releasing a held-fixed PSD component can move the total **either way**.
- **M4 — the estimator seed moves the CENTRAL VALUES too.** On the 43 `M1` projection functionals:
  median `0.104%`, max `0.761%`; against relative uncertainties of median `10.1%` that is median
  `1.06%` and max `6.02%` of the quoted `σ`; **the all-ones "total rate" functional moves by `1.13%` of its OWN `σ`** (movement `0.096%` against an uncertainty of `8.47%`). ⚠ **Re-corrected 2026-09-22: a first restoration wrote this as *"a total rate of `1.13%`"*, which reads as a rate rather than the σ-fraction it is.** ⚠ **Per individual 5D bin it is much larger: median
  `3.77%` of `σ`, p90 `13.6%`, max `49.8%`.** Aggregation suppresses it, so a statement about one
  5D bin carries the larger number and a projection does not. **The same-seed control is
  `9.4e-13`, ten orders below, so the movement is real and not a reproducibility artefact**; the **`0.761%`
  maximum movement** occurs **at index 2, the same functional that failed `s_proj`** (its own
  σ-fraction is `5.91%`).

**The adoption is publication-under-exception, not a pass.** The product's own fields still read
`scientific_acceptance: NON-PASSING` and `adoptable: false`, and they are carried here unedited.
**Cause 3 is NOT discharged.**

## 2. ⚠ ONE FIELD IS CARRIED VERBATIM AND MUST NEVER BE DEFAULTED

    acceptance_question: UNDECLARED

Whether an acceptance correction is owed at the destination binning **was not decided** when the
projection was built. Read back out of the product's own `acceptanceQuestion` key on 2026-09-22 and
reproduced above. **A silent default here is a scientific choice made by a data format.**

## 3. What is here

| file | bytes | `sha256` | contents |
|---|---:|---|---|
| `central_values_5d.npz` | 109,836 | `6773530647f66103…` | `hXSecND_flat_dense` (65,856 dense cells) and `reported_index` (10,694, C order) |
| `masks_5d.npz` | 22,372 | `2c02f47f13448a61…` | `support_mask` `(65,856,)` over the **dense** grid, sum `10,694`; `pinned_mask` `(10,694,)` over the **reported** rows — ⚠ **identically zero in this package**, and it is `z_assembly.compute_g`'s pinning (bins where `v_blk == 0` and `g` was pinned to exactly 1), **NOT** M3's five *seed-pinned* bands, which are a different thing entirely and are **not** represented by this array; `producer_row_index_5d` `(10,694,)`. ⚠ **Both masks ship as `float64`, not `bool`** (`support_mask` unique `[0., 1.]`; `pinned_mask` unique `[0.]`). Schema item 5 also asks for an **unreported-cell mask**: it is not shipped as its own array; it is `~support_mask.astype(bool)` on the dense grid — **55,162** cells (`65,856 − 10,694` ✓). ⚠ This read `~support_mask`, which **raises `TypeError`** on the shipped float64 bytes (`ufunc 'invert' not supported`); the `.astype(bool)` is required, and boolean indexing such as `x[support_mask]` needs it too. |
| `projection_matrix_M_eavailW.npz` | 21,306 | `3b81f42bdc75613f…` | `M` as COO (`rows`, `cols`, `values`, `shape`); dense shape `42 × 10694` |
| `covariance_eavailW.npz` | 10,079 | `94679d6dcdf1ff25…` | `C_eavailW` (42×42), `row_index` (42), `cv_marginal` (42) |
| `_build_report.json` | — | — | every number below, machine-readable |

`M` is stored sparse because it **is** sparse by construction: each source cell maps to exactly one
destination cell, so there are exactly 10,694 nonzeros in 42 × 10,694. Its entries are the **dropped
axes' bin-width products**, which is why the destination is a **density** in `(E_avail, W)`.

### Bin edges, all five axes, in physical units

| axis | unit | edges | bins |
|---|---|---|---:|
| `pt` | GeV/c | 0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55, 0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50 | 14 |
| `pz` | GeV/c | 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 6, 7, 8, 9, 10, 15, 20, 40, 60 | 16 |
| `eavail` | GeV | 0, 0.1, 0.2, 0.4, 0.8, 1.5, 3.0, 100 | 7 |
| `q3` | GeV | 0, 0.2, 0.4, 0.6, 0.8, 1.2, 2.0, 100 | 7 |
| `W` | GeV | 0, 1.1, 1.4, 1.8, 2.2, 3.0, 100 | 6 |

The last bin on `eavail`, `q3` and `W` is a **catch bin to 100 GeV**. Dense grid
`14×16×7×7×6 = 65,856` in **C order**; `10,694` reported.

## 4. What is NOT here, and why

- **Per-object provenance** (schema item 8: *"for each object, the producing revision, the
  producing job, and the digest of the bytes as read back out of the closed file"*). ⚠ **NOT
  CARRIED.** `_build_report.json` records digests of the shipped files but **no producing revision
  and no producing job for any object**. This omission was not disclosed here until the eighth
  independent review measured it; the earlier §4 enumerated only items 4, 7 and 3.
- **The pairing digest `0f04abce…`**, which `VL143` calls **binding** for the note figure, is not
  carried in the package or the build report. It is reproducible from the shipped bytes with this
  repo's own convention: `z_receipt.sha256_array(central_values_5d.npz["hXSecND_flat_dense"])`
  → `0f04abceccb5330b1a5ee84a1f943c2b7d1eaa3d32ae854aaecb91bc5c0d9baa`. So the package ships the
  right bytes without shipping the digest that binds them.

- **`C_Z`, the adopted five-axis covariance itself.** `890,500,272` bytes; it cannot go in a git
  repository. It is identified by digest, which is what the appendix specifies. It lives at
  `/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/uq_5d/z_pilot_20260916_a5/z-cv.npz`.
- **Generator predictions** (schema item 7) — the four truth-level `(E_avail,W)` arrays plus the
  MINERvA Tune v1 ancillary, each needing its generator version, configuration, target and flux.
  **Not assembled here**; that is packaging still owed.
- **Central values for every projection quoted** (schema item 3) — only the five-axis array and the
  `(E_avail,W)` marginal are here.

## 5. Self-checks — the appendix's own worked example, EXECUTED at build time

Not asserted; run. **The build-time rows are all from `_build_report.json`**; ⚠ **the cross-machine re-measurement in the `y = M x_reported` row is NOT in that file (⚠ this said *"the first row"*, whose two values ARE in it)** — it was produced on a second host (numpy `1.26.4`, macOS/Accelerate, 2026-09-22) and reproduced independently by a third reviewer.

| check | result |
|---|---|
| dense size is 65,856 and reported is 10,694 | ✅ both |
| the derived reported mask (`x > 0`) equals the producer's own `hRowIndex5D` | ✅ `true` — two independent statements of one fact, required to agree |
| `M` rebuilt independently reproduces the receipt's content digest | ✅ `64fec490e3e0a6ee…`, **matches** |
| the destination row index reproduces the receipt's readback digest | ✅ `9eb9d21600526db7…`, **matches** |
| the row index equals the receiving-cells mask | ✅ `true` |
| `src_cells_dropped` | ✅ `0` |
| `y = M x_reported` against the product's own `hCV_marginal` | ⚠ **`0.0` ON THE BUILD HOST ONLY — see the warning below.** Re-measured on a different machine (numpy `1.26.4`, different BLAS): **max abs `5.22e-54`, max relative `3.56e-16`, 25 of 42 elements differing.** The agreement is at float64 rounding, not bitwise |
| **C-order vs F-order control** | ✅ the F-order reshape disagrees with the C-order one by a max **relative** `7.82e5`. ⚠ **This is a different statistic from the appendix's *"relative 1.0"*** — here it is `max\|y_C − y_F\| / \|y_C\|` per cell, which is unbounded where `y_C` is small. The conclusion is the same and stronger: the orderings are nowhere near equal, so C order is **established, not assumed** |
| `√Tr C_EW` | ✅ `4.4551809735306645e-39` |
| symmetry `max\|C − Cᵀ\|` | ✅ **exactly `0.0`** |
| `λ_min`, `λ_max`, ratio | computed, **not a check**: `+4.359103608788691e-92`, `1.4882151297784383e-77`, `2.929e-15` (build host, Perlmutter, from `_build_report.json`). ⚠ **`λ_min`'s SIGN IS NOT MEANINGFUL.** The governing measurement for this matrix, `PLAN-20260918-scalar5d-publication-completion.md` §16.1a, rules that the smallest eigenvalues *"sit at the floating-point noise floor … so their sign is not meaningful and 'positive' is not evidence that anything was cured"* (condition number `≈ 3.4e14`), and that `n_negative = 0` *"is not a demonstration that the source's 5,214 negative directions were handled"*. This row previously carried a ✅ beside *"`λ_min` is **positive**"*, and a cross-host caveat I added later went further and called *"the **sign** of `λ_min` … the citable content"* — the opposite of §16.1a, and inconsistent with this README's own *DO NOT INVERT* note two paragraphs down. Both withdrawn. **Cross-host:** re-measured from the shipped bytes on macOS/Accelerate with numpy 1.26.4, `λ_min = 4.3591116699293156e-92` (agreeing on only **5 significant digits**, `4.35910…` vs `4.35911…`, relative difference `1.85e-6`; an earlier revision said *6*, from a common string prefix that counted the decimal point) and `λ_max = 1.4882151297784372e-77`, agreeing on 15. **Citable from this row: `λ_max`, and the ratio's order of magnitude. Not citable: `λ_min`'s sign or its trailing digits.** |

⚠ **THE `0.0` ABOVE IS A PROPERTY OF THE BUILD HOST, NOT OF THESE BYTES — corrected 2026-09-22
by an independent reviewer who ran this README's own recipe and got `AssertionError`.**
`hCV_marginal` was produced by the same `M @ x` on the same machine that built this package, so the
two agreed bit-for-bit *there*. `M @ x` is a 10,694-term sum whose rounding depends on BLAS
summation order, so a reader on different hardware gets `5.22e-54` instead — which is
**agreement at the double-precision floor**, and is in fact the same `5.220244e-54` the C-order
pairing check already records in `VALIDATION_LEDGER.md` `VL143`. **Compare with a tolerance, never
with `==`.** Build host: Perlmutter CPU, numpy `1.26.4`, ROOT `6.28/12`.

⚠ **DO NOT CHECK A RANK.** The spectrum decays smoothly over ~15 orders with no plateau, so the
retained count is set by whatever cutoff is used — `26` at `1e-6`, `36` at the `1e-12` the projector
hardcodes, `41` at `numpy.linalg.matrix_rank`'s default, `42` at none
(`docs/orchestration/state/CUTOFF-SCAN-20260922-publication-42x42.json`, ledger `VL145`). **A reader
following a "rank should be 36" instruction with NumPy defaults would get 41 and wrongly conclude
this package is corrupt.** Check `λ_min/λ_max ≈ 2.9e-15` and `λ_min > 0`, and treat the object as
ill-conditioned rather than as having a definite rank.

⚠ **DO NOT INVERT `C_EW`** without a declared regularization. Its spectrum runs continuously down to
the double-precision noise floor, so the inverse is set by the regularizer rather than by the data.
That, and M1, are why **no significance is computed from it at all**.

## 6. Reading the package

```python
import numpy as np
cv   = np.load("central_values_5d.npz")
mask = np.load("masks_5d.npz")
Mz   = np.load("projection_matrix_M_eavailW.npz")
cov  = np.load("covariance_eavailW.npz")

x   = cv["hXSecND_flat_dense"]          # 65856, C order on 14x16x7x7x6
rep = cv["reported_index"]              # 10694
M   = np.zeros(tuple(Mz["shape"]))      # 42 x 10694
M[Mz["rows"], Mz["cols"]] = Mz["values"]

y = M @ x[rep]                          # 42, density in (E_avail, W)
# TOLERANCE, NOT EQUALITY: M @ x is a 10694-term sum and its rounding is BLAS-dependent.
# On the build host this difference is exactly 0.0; elsewhere it is ~5e-54 (rel ~3.6e-16).
assert np.max(np.abs(y - cov["cv_marginal"]) / np.abs(cov["cv_marginal"])) < 1e-15
y_map = y.reshape(7, 6, order="C")      # C ORDER. The F-order reshape is the control.
```

Converting cell `r` to an integrated cross section requires multiplying by that cell's own
`ΔE_avail · ΔW` — **and the catch bins make that factor large.**

**Co-Authored-By: Claude Opus 5 (1M context)**
