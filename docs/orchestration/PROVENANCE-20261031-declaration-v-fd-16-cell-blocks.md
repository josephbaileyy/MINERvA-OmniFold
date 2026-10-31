# PROVENANCE — declaration (v) for the 16-cell reported 5D covariance, block by block, with a recommendation to Joseph

**Filed 2026-10-31 by the session `coverage-5b-audit`, as the "scalar-5D adoption/statistics owner"** that Ruling 7
names. The director designated it under
[`DECISION-20261031-joseph-oi51-oi137-ud002.md`](DECISION-20261031-joseph-oi51-oi137-ud002.md) item 2, on Joseph's
answer "Yes, designate one (Recommended)". The work is `OI-137`'s item (v): it is read-only, it needs no compute, and it
ends in a recommendation to Joseph (§6).

**Measured at** `origin/main` = `4ede47e34505d65f09ef655d152bbd24a2bbb92a`. Every `file:line` below is at that commit,
and each code file's sha256 prefix is in §7.

> **Ruling 7, verbatim** ([`DECISION-20260822-joseph-b1-lift-and-clause-c.md`](DECISION-20260822-joseph-b1-lift-and-clause-c.md)
> `:186-200`): *"For OI-137, declaration (v) has already landed. Assign the remaining candidate-specific work to the
> scalar-5D adoption/statistics owner. Do not apply a blanket Hartlap correction to the summed covariance. Require each
> sample-covariance block to declare its ensemble size, normalization convention, effective inversion dimension, and
> finite-ensemble treatment, and return a recommendation before any uncertainty-model change."*

**MEASURES:** the four fields of Ruling 7 for each block of the 16-cell reported covariance, plus each block's estimand
and estimator, each read from committed code and committed readouts; and every site that inverts a matrix containing
that covariance, with the dimension inverted.

**CANNOT AUTHORIZE:**
- any uncertainty-model change, any correction factor, and any change to a covariance, readout or cell. Ruling 7 requires
  the recommendation first, and Ruling 11 forbids a blanket Hartlap factor on the sum;
- any change to the note or the paper. §6 recommends one to Joseph, for the paper lane;
- any register edit. `OI-137`'s row and the backlog are the close-items session's to change.

**CITABLE FOR:**
- each block's six fields, as read here;
- the inversion sites and the dimension each inverts;
- the fact that the 10,694-bin family's declaration is [`PROVENANCE-20260822-declaration-v-scalar5d-blocks.md`](PROVENANCE-20260822-declaration-v-scalar5d-blocks.md),
  not this record.

**NOT CITABLE FOR:**
- the size of any finite-ensemble bias. No factor is computed here, on any matrix;
- a coverage or calibration statement;
- C_PL,5D's own label limits (§3.10): a validated size, a cause or a "right" period.

**What was done.** No covariance was loaded, built, decomposed or inverted. No eigendecomposition and no Hartlap or
other debiasing number was computed, on any matrix. Where a rank bound appears, it is labelled *algebra*: it follows from
the construction, not from a measurement. Numbers quoted from readouts were already recorded there, and §7 lists the
readouts.

---

## 1. Which object, and what this record does not redo

**The object is the 16-cell reported covariance of the 5D result**, as the data product names it
(`fd/data-product/fd_data_product.json`, `b79556f0…`, `labels.covariance`):

> C_total + C_resp = C_e + C_model_abs + C_resp, the data's reported covariance … from S1's assembly and C_resp's, in
> S1's absolute units.

The note and the paper report this matrix now (`docs/analysis-note/sec_fived16.tex:43`). Its revised form with the
run-period block, C_total + C_resp + C_PL,5D, is in `fd/with-cpl/` (`fd_data_product_cpl.json`, `d6752d2c…`), under
`FD-CT-5B-ADDITION-REPORT.md`. Both are declared here, and each row says which matrix it belongs to.

**The 10,694-bin scalar-5D family is not redone.** Its declaration (v) landed on 2026-08-22, block by block, in
[`PROVENANCE-20260822-declaration-v-scalar5d-blocks.md`](PROVENANCE-20260822-declaration-v-scalar5d-blocks.md) (the
standard-P4 lane, under Ruling 10). That record stands, and nothing here re-derives or amends it. It covers different
blocks on a different binning: C_syst, C_stat (N = 100), C_ML (N = 24) and the 160 joint throws. Its own §2 shows the
10,694-bin families differ in their (v) fields. **The 16-cell object did not exist in August**, so no earlier record
covers it.
<!-- absence-ok: dated scoping statement: the 16-cell object's definition and assembly were first committed on 2026-10-24 (`nd-unfolding/pv-ladder/readouts/h2_definition.json` at 5c440914, `nd-unfolding/s1_assemble.py` at 6dbc8d20; DECISION-20261024-joseph-h2-16-cell-definition.md) -->

**The note's declaration (v)** is `docs/analysis-note/app_statmethods_nd.tex:12`. For each sample block in the sum, it
requires:
- the ensemble size N;
- the biased 1/N or unbiased 1/(N−1) normalization;
- the effective inverted dimension p after truncation;
- the finite-ensemble treatment, or that none is applied.

This record adds two fields the director asked for, each block's estimand and its estimator. Whether a correction
applies is a judgement, so it is in §6, not in the tables.

## 2. The ownership clause, read as the director ruled it

`OI-137`'s row says the role "must not go to the measurement lane or the PET C_stat lane". Its owner cell names that
lane as **"the OI-137 measurement lane"**, which declined in August on ownership grounds. Its work is on branch
`worktree-oi137-finite-n-exposure`, and its brief is
[`BRIEF-20260822-oi137-finite-N-precision-bias-exposure.md`](BRIEF-20260822-oi137-finite-N-precision-bias-exposure.md).

**The director ruled (2026-10-31, in session)** that the clause means that August lane, not any session called a
"measurement session". This session's handoffs call it one (`HANDOFF-20261029-coverage-session.md`: "the measurement session `coverage`"). The director's
designation is this session. The reading is recorded here because the words fit both.

## 3. Declaration (v), per block

Six fields per block:
- **estimand:** what the block estimates;
- **estimator:** how it is built, with its line;
- **norm.:** the normalization convention;
- **N:** the ensemble size;
- **p:** the dimension inverted downstream (§4 gives the sites);
- **treatment:** the finite-ensemble treatment.

**p is the same for every block, by §4:**
- every consumer inverts the whole matrix it is handed, at its full size, with no truncation;
- that size is **n = 16** (**n = 8** for GiBUU's eight p∥ < 4.5 cells, and for the F0b/F1 and cheap-tier `gibuu8` sets);
- the shape-only χ² inverts the same 16 × 16 (8 × 8) matrix with 100 f fᵀ added, and quotes ndf n − 1.

Unlike August (p = "—", since no 5D χ² existed), p is answerable here.

### 3.1 The reported matrix's sample blocks: C_stat and the Flux band

| field | **C_stat** (in C_e) | **Flux** (in C_e) |
|---|---|---|
| estimand | the sampling covariance of configuration (e)'s 16 cell integrals under data fluctuation | the covariance from the PPFX flux uncertainty, under the ν-e + IMD constraint |
| estimator | the sample covariance of 50 refit-per-replica data bootstrap replicas with jitter, `s1_assemble.py:316-321` (`np.cov(R, rowvar=False, ddof=1)`) | MAT `CalcCovMx`, weighted, mean-centred on the weighted mean, `s1_assemble.py:125-130`, applied with the constraint weights at `:323-329` |
| norm. | **unbiased 1/(N−1)** (`ddof=1`, `:321`) | **biased, weighted:** divided by the weight sum Σw (`:130`), the weighted analogue of 1/N |
| N | **50** (`STAT_REPLICAS`, `:54`; `meta.stat_replicas` = 50 in `s1/readout/s1_assembly.json`, `81e5ef3f…`) | **100** universes (`EXPECT`, `:60`); **effective n_eff = 19.06**, with Σw = 211.012 (`meta.flux_weights`, from `:374`; `S1-REPORT.md:288`) |
| p | 16 (8) | 16 (8) |
| treatment | **none applied** | **none applied to the block.** The flux bootstrap measured the estimation scatter of Stage G's χ² from estimating this block (`FD-FLUX-BOOT-REPORT.md`, readout `b7b5652c…`). That is a measurement, not a correction, and it moves no number (§3.12) |
| rank, *algebra* | ≤ min(N − 1, 16) = 16 | ≤ min(99, 16) = 16 |

**This record does not compare n_eff = 19.06 with p = 16 as a factor.** The relation between them, and why no single
factor applies, is in §6.

### 3.2 2p2h (in C_e)

| field | value |
|---|---|
| estimand | the 2p2h model uncertainty |
| estimator | MAT `CalcCovMx`, unweighted, mean-centred, `s1_assemble.py:125-130,329` |
| norm. | biased 1/N |
| N | **3** universes (`EXPECT`, `:60`) |
| p | 16 (8) |
| treatment | **none applied.** As in August §4a, whether the three universes are random draws is not classified, so "none applicable" is *not* claimed |
| rank, *algebra* | ≤ 2 |

### 3.3 The 36 two-universe bands (in C_e)

These are the 32 model bands of `MODEL_BANDS_2` (`s1_assemble.py:61-65`) and the 4 detector bands of `DETECTOR_BANDS`
(`:57`).

| field | value |
|---|---|
| estimand | each band's one-knob model or detector uncertainty |
| estimator | MAT `CalcCovMx` over the band's two universes (`:329`). Mean-centred over two points, it is ¼ Δ Δᵀ, with Δ the difference of the two universes |
| norm. | biased 1/N, N = 2 |
| N | **2** each (`EXPECT`, `:60,65`) |
| p | 16 (8) |
| treatment | **none.** A two-point form has no ensemble to correct. Treating these as deterministic shifts follows August §4a's census of the same bands by name; it is not re-measured on S1's bank |
| rank, *algebra* | ≤ 1 each |

### 3.4 The five lateral bands (in C_e)

BeamAngleX, BeamAngleY, MuonResolution, Muon_Energy_MINERvA and Muon_Energy_MINOS (`s1_assemble.py:56`).

| field | value |
|---|---|
| estimand | each band's reconstructed-kinematics shift uncertainty |
| estimator | mean-centred over the band's two endpoints (`:333-341`), so no CV enters: ¼ Δ Δᵀ (`S1-DECLARATION.md` row 3). Muon_Energy_MINOS is first rescaled per p_T bin (`:338`) |
| norm. | biased 1/N, N = 2 |
| N | **2** endpoints each |
| p | 16 (8) |
| treatment | **none, and none applicable.** The endpoints are ±1σ shifts, not draws |
| rank, *algebra* | ≤ 1 each |

### 3.5 C_norm (in C_e)

| field | value |
|---|---|
| estimand | the 1.4 % normalization uncertainty |
| estimator | (0.014 f)(0.014 f)ᵀ, `s1_assemble.py:343` |
| norm., N | n/a: a deterministic outer product, not an ensemble |
| p | 16 (8) |
| treatment | none, and none applicable |
| rank, *algebra* | 1 |

### 3.6 C_seed (in C_e): measured as exactly zero

| field | value |
|---|---|
| estimand | the estimator-seed main effect (2D's C08) |
| estimator | the sample covariance over seeds of the per-seed mean of bootstrap replicas 1–20, `s1_assemble.py:246-248,344-352` |
| norm. | unbiased 1/(N−1) (`ddof=1`, `:248`) |
| N | **5** seeds (42, 45, 48, 51, 54; `SEEDS`, `:52`), each the mean of 20 replicas (`SEED_REPLICAS`, `:53`) |
| p | 16 (8) |
| treatment | **none applied, and none can act: the block is exactly zero in every cell.** The 80 seed products are bitwise equal to seed 42's (`S1-REPORT.md:34`, §7; `sec_fived16.tex:43`). A zero block adds nothing to any matrix that is inverted |
| rank, *algebra* | ≤ 4 by construction. Measured: 0 |

### 3.7 C_model_abs (in C_total)

| field | value |
|---|---|
| estimand | the model dependence of the unfolded result: one fully correlated component per alternative generator |
| estimator | C_model = Σ_k s_k s_kᵀ, with s_k = X_k / X_0 − 1, over k ∈ (GENIE + MEC, NuWro, GiBUU). It is unscaled (κ = 1), not centred, and a sum, not a mean (`pv-ladder/build_cmodel5d.py:7-10,47,159-162,220-223`; `2d-unfolding/pv2d/cmodel/build_cmodel.py:64-74`). C_model_abs = diag(f) C_model diag(f) (`s1_assemble.py:251-252,361`) |
| norm. | **none:** a sum of three outer products, with no 1/N or 1/(N−1) |
| N | **3** generator vertices (`VERTICES`, `build_cmodel5d.py:47`). These are chosen models, not draws from a distribution |
| p | 16 (8) |
| treatment | **none.** A sample-covariance debiasing factor does not apply, since the vertices are not independent realizations |
| rank, *algebra* | ≤ 3 |

### 3.8 C_resp

| field | value |
|---|---|
| estimand | the calorimetric hadronic-response uncertainty of four species (proton, meson, em, other) |
| estimator | per species, the half-span outer product d dᵀ with d = (x(+1) − x(−1)) / 2 (`build_cresp.py:111-113`), summed over the four primary species (`:187`). Cross-talk is built and not summed (`:36-37`) |
| norm. | biased 1/N, N = 2 (the two-endpoint mean-centred form) |
| N | **2** endpoints per species, 4 species |
| p | 16 (8) |
| treatment | **none, and none applicable:** each species is a ±1 shift, not a draw |
| rank, *algebra* | ≤ 4, and enforced: the build refuses otherwise (`:191-192`) |

### 3.9 Not included in the 16-cell covariance

These are absent by declaration, so there is nothing to declare for them: inflation D, C_ML, the bounded envelope h, and
Rvp1pi (`meta.not_included` in `s1_assembly.json`; `s1_assemble.py:23`).

### 3.10 C_PL,5D: the revised product only (`fd/with-cpl/`), not the reported matrix

| field | value |
|---|---|
| estimand | the run-period dependence of the result, relative to each cell |
| estimator | k Σ_P e_P g_P g_Pᵀ, where g_P = r_P / m̄ − 1, m̄ = Σ_P e_P r_P, r_P the period's double ratio and e_P its exposure share, with k = V₂ / (1 − V₂) and V₂ = Σ_P e_P² (`fd_ct_periods.py:396,421-426`). That is 2D's DESIGN section 2. C_PL,5D,abs = diag(f) P diag(f) (`fd_cpl_addition.py`, block `d9aa32fd…`) |
| norm. | **exposure-weighted, with the reliability-weight factor k = V₂ / (1 − V₂).** This is the weighted analogue of 1/(N−1), not 1/N |
| N | **3** periods (PA, PB, PC; `fd_ct_periods.py:55`). The readout's label records "about 1.83 effective dof" (`fd_ct_5b_periods.json`, `a5b17895…`, `C_PL5D.label`) |
| p | 16 (8), inside C_total + C_resp + C_PL,5D (+ V_g) in the with-block arm |
| treatment | **none applied.** The same construction on pure bootstrap noise (10 replicas per period) is computed and recorded beside it (`:427-428`; `noise_floor_sigma_rel`, `sigma_ratio_to_noise_floor`), and it is not subtracted |
| rank, *algebra* | ≤ 2, and enforced (`:429-435`, Q5). Recorded rank 2 |

**Its label travels with every use** (`FD-CT-5B-ADDITION-DECLARATION.md` §2). It is built from the observed offsets, so
it contains them by construction. It is not citable for a validated size, the cause of a period difference, or which
period is right.

### 3.11 V_g: not in the reported product, inside every matrix Stage G inverts

| field | value |
|---|---|
| estimand | the variance of each prediction's cell integral from the generator's finite MC sample |
| estimator | V_g = diag(Σ_f sumw2_f vol_f²), `fd_g_compare.py:9,335-338`: the sum of squared event weights of the weighted sum, per cell, diagonal |
| norm. | **none in the 1/N sense:** a Poisson-type variance of a weighted sum (Σ w²), with no division by an ensemble size |
| N | the MC events in each cell, recorded per prediction as `n_mc_events_in_cells` in `fd_g_readout.json` (`75a9ddee…`). The smallest recorded per prediction is 11,477 (GENIE CV), 10,949 (GENIE + MEC), 17,550 (NuWro), 18,112 (GiBUU, 8 cells) and 360,147 (MINERvA Tune v1) |
| p | 16 (8): V_g is diagonal, so it is full rank on its cells wherever every cell has events |
| treatment | **none applied** |

**Where it sits:**
- V_g is not in the data product. The data product's `labels.covariance` says "V_g is not in this product".
- Every Stage G χ² inverts C_total + C_resp + V_g (`fd_g_compare.py:151`), and so do G-DIAG, G-FOLLOWUP, G-SENS2 and the
  flux bootstrap, which all reuse that comparison (§4).

### 3.12 What the flux bootstrap already measured

The flux bootstrap is the one block-specific finite-ensemble measurement on record for this object
(`FD-FLUX-BOOT-REPORT.md` §2.1, readout `b7b5652c…`):
- **What it did:** it rebuilt the Flux block from 2,000 bootstrap replicates of the 100 weighted universes.
- **What it recorded:** each prediction's χ² band beside Stage G's χ̂. **Every offset, median − χ̂, is positive:**
  +0.25, +1.22, +0.75, +0.16 and +3.12 on χ̂ = 109.35, 272.12, 188.03, 58.46 and 329.72 (correlation variant, total χ²).
- **Its labels govern:** "estimation uncertainty, not sensitivity". It is not an interval, and it is not citable for the
  χ² being insensitive to the flux correlations.

Those numbers are copied from the report and are not recomputed. They are quoted as the measurement that exists, not as
a correction to anything.

## 4. Every inversion site, with the dimension it inverts

**The search:**
- `git grep -nE 'cholesky|linalg\.inv|pinv|lstsq|linalg\.solve'` over `nd-unfolding/fd_*.py`;
- the same pattern over every `*.py` that names `s1_assembly`, `C_total_plus_C_resp`, `fd_data_product`,
  `import s1_assemble` or the C_resp npz.

The second search adds only review probes and simulations under `receipts-*` and `limitation-plan/`, which are not
production consumers. A reader that reaches the matrix by some other name would be missed: the claim is scoped to these
two searches.

**No production site truncates.** Each inverts the whole matrix it builds, by Cholesky (which refuses a matrix that is
not positive definite) or by a full inverse. So p = n at every site. Some sites also compute a least-squares or
eigen-mode χ² as a cross-check (G-DIAG). That cross-check uses NumPy's default `rcond`, machine precision × n, and the
reported χ² is the Cholesky one.

| consumer | site | matrix inverted | method | p (recorded field) |
|---|---|---|---|---|
| Stage G, the reported generator χ² | `fd_g_compare.py:147-162` (Cholesky `:158`, solve `:159`) | total: C_total + C_resp + V_g. Shape-only: the same + 100 f fᵀ | Cholesky, no ridge or floor | **16** (8 for GiBUU): `predictions[].total.matrix_rank` and `.shape_only.matrix_rank` in `fd_g_readout.json`, all 16 or 8; ndf 16/15 (8/7) |
| G-DIAG | `fd_g_diag.py:98-105` (`chol_chi2`). Cross-checks at `:115-117`: mode sum, and `lstsq` with `rcond=None` | the Stage G matrix | Cholesky; cross-checks recorded as `rel_*_vs_cholesky` | 16 (8): ndf = n (`:202`); `condition` recorded per prediction (`fd_g_diag_readout.json`, `680dc5ef…`) |
| G-FOLLOWUP, G-SENS2 | `fd_g_followup.py:248-262` (`sens_record` → `D.chi2_ways`) | the sum of the blocks, with one family shrunk by α | as G-DIAG | 16 (8): `ndf = len(d)` (`:260`) |
| flux bootstrap (3D) | `fd_flux_boot.py:151-156` → `G.compare` | C_total + C_resp + (C − C₀) + V_g | as Stage G | 16 (8): `bands.*.*.ndf` in `fd_flux_boot_readout.json` |
| F0b, F1 (fake data) | `fd_f0_regrade.py:225-232` (`grade`) | (C + N)[idx]: C a reported-family matrix (relative), N the ratio-estimator variance of the weighted mean over the fake experiments (`:215-222`) | Cholesky | 16 (8): `truths[].ndf` in `fd_f0b_readout.json` (`b9db935a…`) and `fd_f1_readout.json` (`cbe411a9…`) |
| cheap-tier readers | `fd_ct_readers.py:151-154` (`quad`), `:356-359` | C_e and C_total_resp, per cell set (all16, gibuu8) | Cholesky | 16 (8): `truths.*.matrices.*.*.ndf` in `fd_ct_chi2.json` |
| 1B coverage scoring | `fd_1b_score.py:322-329` (`chi2_values`) | the 4A matrix M_d, and the transferred reported matrix | Cholesky, "no ridge or floor" (`:323`) | n of the cells scored |
| 5B periods and audit | `fd_ct_periods.py:409-410`; `fd_ct_5b_audit.py:197-202,543` | M = (C_total + C_resp) / (f fᵀ) | `np.linalg.inv`, or Cholesky whitening | 16 |

**Two further finite-ensemble terms sit inside some of these matrices** and are not blocks of the reported covariance:
- **V_g** (§3.11), in Stage G and everything that reuses it;
- **N in F0b and F1,** the variance of the mean over the fake experiments. Its effective size is recorded per truth as
  `B_eff`.

Both are named here because they share the matrix being inverted. F0b's and F1's grading is the fake-data study's own
construction, already declared in `FD-F0b-DECLARATION.md` and `FD-F1-DECLARATION.md`.

## 5. What the artifacts cannot satisfy, and what would change it

| # | not satisfiable from the artifacts | why | what would change it |
|---|---|---|---|
| 1 | per-band N for C_e on the assembly npz | `meta` records `stat_replicas`, `seeds` and the Flux weights' n_eff, but no per-band universe count. The counts here are the code's `EXPECT` set (`s1_assemble.py:60,65`), which `universe_bands` enforces exactly (`:169-191`): it refuses any other count | nothing needed: the enforced constant is the count of the inputs used. A per-band key in `meta` would make it readable from the artifact alone |
| 2 | whether 2p2h's three universes are random draws | the same gap as August §4a, row 6 | read the three universe names from the bank |
| 3 | whether the 36 two-universe bands are deterministic, from S1's own bank | classified by name from August's census, not re-read here | read S1's bank listing (`S1-DECLARATION.md` §1) |
| 4 | per-block contributed rank in the 16-dimensional sum | it would need an eigendecomposition, which this record does not do | not proposed: §6 does not depend on it |

## 6. Recommendation to Joseph

**This section is the recommendation Ruling 7 requires before any uncertainty-model change. It authorizes nothing.** It
is bounded by Ruling 11:
- no blanket Hartlap factor on the summed covariance;
- the disclosure uses the mixed-block rationale;
- the finite-N blocks' trace share is not used as a reason.

**Recommendation: disclose, do not correct, for the 16-cell matrix as for the 10,694-bin one.** Apply no factor to
C_total + C_resp (or to + C_PL,5D), and make no covariance change.

**Why, without using trace share.** The matrix inverted is a sum of unlike terms (§3):
- **Two sample blocks with a real ensemble:**
  - C_stat, N = 50, unbiased;
  - Flux, N = 100 weighted to n_eff = 19.06, normalized by the weight sum.
- **Small or deterministic terms:**
  - 2p2h, N = 3;
  - 41 two-point shift terms (36 bands and 5 laterals);
  - C_resp's four shifts;
  - C_norm;
  - C_model, three chosen models, a sum with no normalization;
  - C_seed, measured as exactly zero.
- **Model-chosen or MC-statistics terms:**
  - C_PL,5D, three exposure-weighted periods, revised product only;
  - V_g, a diagonal Σ w² term.

The standard factor (N − p − 2)/(N − 1) is derived for one unweighted sample covariance over N independent Gaussian
realizations. **None of the terms here is the whole matrix,** and the weighted ensembles (Flux, and C_PL,5D in the revised product) do not have the
unweighted form the factor assumes. So no single factor is valid for the sum. That is the mixed-block leg of Ruling 11,
and it holds here as stated.

**One leg of Ruling 11's rationale does not carry over, and Joseph should know.** Ruling 11's disclosure also rests on
the *data-dependent truncation* argument: the standard factor assumes a truncation dimension chosen independently of
the data, and every truncation in the 10,694-bin family is an `rcond` or a scan. **The 16-cell χ² has no truncation**
(§4): every site inverts the full 16 × 16 (8 × 8) matrix, so p = n is fixed in advance and does not depend on the data.
That leg is therefore unavailable for this object. The recommendation rests on the mixed-block leg alone, plus the
measured flux bootstrap (§3.12). The disclosure must not borrow the truncation sentence for the 16-cell χ².

**The direction is the note's own** (`app_statmethods_nd.tex:16`). A noisy sample-covariance inverse is biased upward.
- **For a fixed residual,** it inflates χ², so tension is overstated, not hidden.
- **What it would make over-optimistic** is a confidence region drawn from the same matrix. The paper states that
  interval coverage has not been validated (`paper_body.tex:19`).
  <!-- absence-ok: a quotation of the paper's own sentence at paper_body.tex:19, not a claim made here -->
- **For the Flux block, the one measurement on record points the same way:** every flux-bootstrap offset is positive
  (§3.12).

The offsets are estimation scatter under the bootstrap, not a debiasing factor, and they are not to be converted into
one.

**A note-side gap, for the paper lane, which Joseph may want closed.**
- **What the protocol requires:** declaration (v) at `app_statmethods_nd.tex:12` says every N-D χ² must state, *where it
  is quoted*, items (i)–(v).
- **What is quoted:** the 16-cell χ² is quoted at `sec_fived16.tex:182-196` (the generator table) and in the fake-data
  tables (`sec_fived16.tex:117`; `paper_body.tex:168`), with ndf 16 (8).
- **What a search found:** for `ensemble`, `declaration`, `n_eff`, `Cholesky`, `inverse` and `rank` over
  `sec_fived16.tex` and `paper_body.tex`, no (v) statement for these χ² at those sites. The claim is scoped to that
  search.
- **A minimal disclosure would state:**
  - the inverse (full, Cholesky, no truncation; p = ndf = 16, or 8);
  - C_stat's N = 50 (1/(N−1));
  - Flux's 100 universes with n_eff = 19.06 (weight-sum normalization);
  - that C_seed is zero, and that the remaining terms are deterministic shifts or chosen models;
  - that no finite-ensemble correction is applied;
  - a pointer to the flux bootstrap and to this record.
- **Who decides:** whether, and in what words, is the paper lane's, through its truth and register checks. This record
  writes no note text.

**Options Joseph could choose instead, not recommended now.**
- **(b)** A declared resampling study of C_stat's 50 replicas, on the flux bootstrap's pattern. It would measure the
  estimation scatter of the χ² from C_stat, as 3D did for Flux. It needs its own declaration and binding, and it moves
  no number. It is not recommended because no quoted result depends on it: no p-value is printed (`fd_flux_boot.py:32`),
  and coverage is declared not validated.
- **(c)** Any correction factor. Not recommended, for the reason above, and Ruling 11 forbids the blanket form.

## 7. Evidence route

| claim | evidence (at `4ede47e3`) |
|---|---|
| Ruling 7, verbatim; Rulings 10, 11 | `DECISION-20260822-joseph-b1-lift-and-clause-c.md` `:186-200`, Ruling 10, Ruling 11 |
| the designation | `DECISION-20261031-joseph-oi51-oi137-ud002.md` item 2 |
| the 10,694-bin declaration | `PROVENANCE-20260822-declaration-v-scalar5d-blocks.md` |
| the reported matrix and its components | `fd/data-product/fd_data_product.json` `b79556f0…` `labels.covariance`; `sec_fived16.tex:43` |
| the revised matrix | `fd/with-cpl/data-product/fd_data_product_cpl.json` `d6752d2c…`; `fd/with-cpl/block/cpl_block.npz` `d9aa32fd…` |
| C_e's blocks and their estimators | `nd-unfolding/s1_assemble.py` (`b157250a…`) `:23,52-65,125-130,246-252,316-353,361,374` |
| S1's recorded meta | `s1/readout/s1_assembly.json` `81e5ef3f…` `meta.stat_replicas`, `meta.seeds`, `meta.flux_weights`, `meta.blocks`, `meta.not_included` |
| C_seed is zero | `S1-REPORT.md:34`, §7; `docs/analysis-note/sec_fived16.tex:43` |
| C_model | `nd-unfolding/pv-ladder/build_cmodel5d.py` (`aaa81575…`) `:7-10,47,159-162,220-223`; `2d-unfolding/pv2d/cmodel/build_cmodel.py:64-74` |
| C_resp | `nd-unfolding/build_cresp.py` (`fe1aec8b…`) `:10,36-37,111-113,187,191-192` |
| C_PL,5D | `nd-unfolding/fd_ct_periods.py` (`ec6bc7f5…`) `:55-61,396,421-435`; `fd/readout/fd_ct_5b_periods.json` `a5b17895…` `C_PL5D` |
| V_g | `nd-unfolding/fd_g_compare.py` (`0a3c09cd…`) `:9-11,147-172,335-338`; `fd/readout/fd_g_readout.json` `75a9ddee…` |
| the inversion sites | `fd_g_compare.py:158-159`; `fd_g_diag.py` (`241bfd02…`) `:98-117,202`; `fd_g_followup.py` (`ec8cbc68…`) `:248-262`; `fd_flux_boot.py` (`d5b4bb09…`) `:151-156`; `fd_f0_regrade.py` (`0dfa722c…`) `:215-232`; `fd_ct_readers.py` (`f4cc51c8…`) `:151-154,356-359`; `fd_1b_score.py` (`507fb2ac…`) `:322-329`; `fd_ct_periods.py:409-410`; `fd_ct_5b_audit.py` (`d969d1ff…`) `:197-202,543` |
| the flux bootstrap | `FD-FLUX-BOOT-REPORT.md` §1–§2.1; `fd/readout/fd_flux_boot_readout.json` `b7b5652c…` |
| the note's protocol and direction | `docs/analysis-note/app_statmethods_nd.tex:12,16,19` |
| the 16-cell χ² quotes | `docs/analysis-note/sec_fived16.tex:117,182-196`; `docs/analysis-note/paper_body.tex:19,168` |

Paths beginning `fd/`, `s1/` or naming an `FD-`/`S1-` record are under
`docs/orchestration/state/measurement-paper/5d-community-20261024/`.

**What expires this record:**
- a change to any cited code file (its digest above);
- a change to the reported matrix or to the S1 assembly;
- the paper lane adopting C_PL,5D into the reported matrix, which moves §3.10 from "revised product only" to the
  reported one.
