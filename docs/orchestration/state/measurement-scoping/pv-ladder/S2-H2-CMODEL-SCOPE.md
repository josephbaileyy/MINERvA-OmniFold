# S2: can C_model,5D on the H2 cells be built from L-5D-PV's products? (2026-10-24, session "2d test")

**Assignment.** The director's S2, 2026-10-24, under `DECISION-20261024-joseph-5d-community-standard-route.md` item 7.
It is scoping only: 0 node-h, no new unfolds, and nothing is built. The method below waits for the director's binding.

**Answer: yes, exactly, at 0 node-h.**
- The four L-5D-PV data unfolds hold configuration (e)'s cross section on the full 5D fine grid.
- Every H2 edge is a fine edge, so each H2 cell is an exact sum of fine cells.
- The build is arithmetic on six files of about 0.1 MB each. It runs on a laptop in seconds.

**What this record does not do:**
- **It did not open the data products.** The nominal and vertex unfolds are (e)'s data result. Item 2 of the decision
  lets cells be merged or restricted only if that is declared before any such result is read. The data products were
  hashed, not loaded.
- **It does not say whether a refined-estimator data result on H2 has already been read.** s5p's Stage 2 has read
  one; see §5. That ruling is the director's.

Everything quoted below comes from simulation: the frozen reweights, the two closure unfolds and s5p's Stage-1
receipt. The numbers are in `nd-unfolding/pv-ladder/readouts/s2_h2_scope.json` (sha256
`1d25434a3e9c4440a7abc4ab0a72a4d5de3df4526e608c372ab83f0284c1da93`). They were written by
`nd-unfolding/pv-ladder/s2_h2_scope.py` (sha256 `7e282185ab17f4e95bc09f6d660fd9b97ff99dd4532a37c8853e1ba7aa288d64`).
The run took 0.5 s on a laptop. `test_pvl.H2Scope` checks the H2 aggregation against closed-form cell volumes.

## 1. Inputs

**H2.** H2 is `s5p_stage1_inspect.H2_EDGES`, a 2⁵ partition with these edges:

| axis | edges |
|---|---|
| p_T | 0, 0.7, 4.5 |
| p_∥ | 1.5, 4.5, 60 |
| E_avail | 0, 0.8, 100 |
| q₃ | 0, 2.0, 100 |
| W | 0, 1.8, 100 |

- **Cell index:** 16·i_pT + 8·i_p∥ + 4·i_E + 2·i_q₃ + i_W.
- **Reported cells:** the 27 of 32 that s5p's Stage-1 receipt marks reported (`state/s5p/stage1/stage1_inspect.json`,
  `mc.H2.reported`). They are cells 0, 1, 3–5, 7–9, 11–13, 15, 16 and 18–31.
- **Unreported cells:**
  - cells 2, 10 and 14 are empty;
  - cell 6 has MC n_eff 1;
  - cell 17 has MC n_eff 5,678.
- **Fine cells to H2:** `coarse_map` assigns each fine cell to an H2 cell by its centre. It raises if any coarse edge
  is not a fine edge.

**Files.** Each was checked by sha256 on 2026-10-24, against `receipts/SHA256SUMS` for the products and against
`nd-unfolding/pv-ladder/prep-SHA256SUMS` for the reweights.

| file (under `/pscratch/sd/j/josephrb/pv-ladder-20261024/`) | sha256 | bytes | mtime (cluster time) | S2 use |
|---|---|---:|---|---|
| `products/L-5D-PV_e_tune_v1.npz` | `dbe9a95e746fba127811182e9a352f6dc243d78ff699e803611b5deedbcb0f4f` | 95,831 | 10-24 02:41 | zero of the shifts; central value x |
| `products/L-5D-PV_e_genie_mec.npz` | `bdff9193b04f17c4aa9d97e7d9c26221b03dc8c9b0d2376cd775e6b195b749c5` | 95,841 | 10-24 04:31 | s_GENIE+MEC |
| `products/L-5D-PV_e_nuwro.npz` | `caf6eee726ddb128d26cf74fad2a2b4e69273607a2a0e1e4a48750766bddc66f` | 95,849 | 10-24 04:31 | s_NuWro; PC data side |
| `products/L-5D-PV_e_gibuu.npz` | `bdf331570daeb3dc56d6096e2c39ca3e7a6091339680eb58034ee9a14c82f3c3` | 95,807 | 10-24 04:32 | s_GiBUU |
| `products/L-5D-PV_e_closure_nuwro.npz` | `fff9030e7fd63c538b27c58f2a35417b5d28c3d2f6de2880219b181812215182` | 188,455 | 10-24 04:32 | PC bias (opened) |
| `products/L-5D-PV_e_closure_tune_v1.npz` | `eb3e218866dd36e093c85e85a791f8dd8de1491f4ad0694924644b01c8e55f08` | 188,532 | 10-24 04:29 | closure floor (opened) |
| `prep/ratios/L-5D-PV/ratios.json` | `925cbd8d7655d3f7c407488dd3157cc6dbe5ded934a37927b678cf5e4b923c58` | (dir 17 MB) | | prior truth weight, labels |
| `prep/ratios/L-5D-PV/{genie_mec,nuwro,gibuu}.json` | `8d0e0f42…4f`, `38e47eb6…6e`, `52438000…4e` | | | r_k (opened) |

The NC target lives in RE-1's area: `/pscratch/sd/j/josephrb/methods-paper/re1-20261022/out/5d/k1_p5_rerun.npz`
(P5). Its sha256 is `e36f3b25459e068cec9dba941f7b3aea8f48c6e22c931fde7c9d315e7b1e8de2`, as `config.json` records; it
is 95,311 bytes with mtime 10-22 20:50.

**What the products hold.** Each holds `xsec_flat`, the differential cross section on the 65,856 fine cells, with its
provenance meta. The closures also hold the truth, `xtrue_flat`. There are no per-event weights, and none are needed:
the fine-grid cross section aggregates onto H2 exactly.

## 2. The method, for binding (the same form as C_model,2D)

### 2.1 Shifts and the matrix

- **H2 integral:** X_k,c = Σ_{f ∈ c} x_k,f · vol_f, where x_k is `xsec_flat` of `L-5D-PV_e_<k>` and vol_f is the fine
  cell's volume. These are `pvl_lib.integrated`, then a bincount on `coarse_map`.
- **Shift:** s_k,c = X_k,c / X_0,c − 1 on the 27 reported cells, where X_0 comes from `L-5D-PV_e_tune_v1`. This is
  `pvl_analyze`'s `rel_shift`, as on EW, J and (p_T, p_∥).
- **Matrix:**
  - S is 3 × 27 (GENIE+MEC, NuWro, GiBUU), and C_model,5D = SᵀS with κ = 1. It is fractional.
  - The outer products are summed elementwise in a fixed order, as in `build_cmodel.cmodel()`, so the matrix sha256
    does not depend on the platform.
  - C_abs = diag(x) C_model diag(x), with x = X_0. X_0 is (e)'s central value on H2, because `L-5D-PV_e_tune_v1`
    equals P5 bitwise.
- **What waits on S1:** C_model,5D and C_abs can be built now. The sum with (e)'s statistical and systematic covariance
  waits for that covariance (S1), because a 5D (e) covariance does not exist yet.
  <!-- absence-ok: restates the recorded absence at DECISION-20261024-joseph-5d-community-standard-route.md item 5, which S1 re-checks -->
- **What is committed:** S, the per-cell √diag, the rank and singular values, and the coverage counts of §2.5 go in a
  JSON, as `cmodel_2d.json` does. The npz stays on pscratch, because `*.npz` is ignored in git.

### 2.2 Applying the reweight

Nothing is re-applied. The reweights are L-5D-PV's frozen r_k on the 5D fine grid, from run pin `ee299e10`. They
entered each unfold through `pvl_lib.prior_inputs`, with the binned-denominator rescale and the r-constancy guard,
which passed at a tolerance of 1e-9. The build reads only the unfolded `xsec_flat`.

### 2.3 GiBUU's p_∥ < 10 GeV/c restriction

**How L-5D-PV handles it.** GiBUU's r is defined only on fine cells whose p_∥ upper edge is at most 10, and r = 1
above. `pvl_ratios` sets `pz_max_cells = 10`. So above 10 GeV/c the prior keeps Tune v1's shape for GiBUU.

**What it does to H2.** H2 splits p_∥ at 4.5, so the 14 reported high-p_∥ cells mix reweighted and unreweighted
prior.
- Within those 14 cells, the prior weight at p_∥ ≥ 10 with GiBUU's r = 1 has a median of 11 % and a maximum of 39 %.
  The maximum is cell 31, which holds 13.9 % of the whole prior.
- Eight cells are above 10 %: 11, 15, 25, 26, 27, 29, 30 and 31.
- Over the 27 cells, 8.7 % of the prior weight is untouched by GiBUU for this reason.

**Proposal.** Carry s_GiBUU as measured, and label it: "GiBUU's shape applied on p_∥ < 10 GeV/c; above it the prior
is unchanged". In those cells s_GiBUU is a partial-range shift, and it does not measure GiBUU's
full-range dependence there.

**Alternative.** Split H2's upper p_∥ bin at 10, which is a fine edge. That is also exact from the same products at
0 node-h. It changes the reporting cells, though, so under item 2 it must be declared before the data are read. I do
not recommend it: it adds cells where GiBUU's mode is identically unweighted.

### 2.4 The noise gate

**No new gate.** The 5 % gate was applied once, on the 5D fine grid, when the reweights were built: stat_max 0.05,
J-coarse pooling, and otherwise r = 1. Gating again on H2 would need new reweights and new unfolds.

On the 27 reported cells, the median share of each cell's prior weight in each tier is:

| tier | GENIE+MEC | NuWro | GiBUU |
|---|---:|---:|---:|
| own ratio | 14 % | 17 % | 0 % |
| J-coarse pooled | 59 % | 59 % | 67 % |
| r = 1 | 7 % | 5 % | 18 % |

GiBUU's mode on H2 is therefore mostly its J-coarse shape. The J edges do not nest in H2's (p_T 0.55, 0.85 against
0.7), so pooled ratios straddle H2 cells. That does not affect exactness, because r is constant on each fine cell.

### 2.5 Controls I would require

**NC, the nominal reproduced bitwise:**
- (a) `L-5D-PV_e_tune_v1`'s `xsec_flat` is `array_equal` to P5 on the full grid. The ladder's NC already recorded this
  (`readouts/L-5D-PV_e.json`, `bitwise_full_grid: true`); the build re-runs it.
- (b) X_0 equals P5's H2 integrals, bitwise.
- (c) The H2 integral by `pvl_lib.integrated` equals the integral by `s5p_stage1_inspect.fine_volume`. On both closure
  truths the difference is 0.
  - This is a check on the volume code only. Both routes use s5p's own `coarse_map`; `test_pvl.H2Scope` checks that
    map against closed-form cell volumes.
- (d) The builder's internal checks: SᵀS reproduces C_model; h = max_k |s_k|; the PC bias has one entry per cell.

**PC at NuWro, under the rule already declared and unchanged** (`pv2d_lib.positive_control`):
- **The test:** the data shift s_NuWro against minus the closure bias (`L-5D-PV_e_closure_nuwro` against its truth) on
  the 27 cells.
- **The bar:** at least 20 cells with |bias| > 1 %, corr ≥ 0.7, and a slope in [0.67, 1.5].
- **Power:** it is powered with 21 of 27 cells, measured here from simulation only.
  - The margin is thin: 5 of the 21 have |bias| between 1.04 % and 1.21 % (cells 4, 7, 16, 23, 24).
  - The bias is fixed, so the count cannot change at the build, and the ρ² fallback (tasks `F`, never run) is not
    needed.
    <!-- absence-ok: checked 2026-10-24: receipts/SHA256SUMS lists no *_sq product, and the 30 files in the run's products/ on pscratch include none; tasks.tsv puts the fallbacks in job F, which never ran -->
- **Closure bias on the reported cells:** median 2.0 %, maximum 8.3 %.
- **Closure floor** (`_closure_tune_v1`): at most 3.2e-5, so the floor is negligible.
- **If the PC fails,** the build still writes C_model,5D, labelled "positive control failed on H2: not evidence". It
  stops short of any total until the director rules.
- **Descriptive coverage, as for C_model,2D:** on the PC cells, counts where |s_NuWro| ≥ |bias|, where
  √(s_GENIE+MEC² + s_GiBUU²) ≥ |bias|, and where √diag C ≥ |bias|. The last includes the bias's own vertex, so it is
  not evidence of coverage.

### 2.6 Cost

- The build costs 0 node-h.
- It needs the four data products (≈ 0.38 MB) and P5 copied to scratch, then numpy on a laptop or the login node, in
  seconds.
- Writing it means a builder and tests modelled on `build_cmodel.py`: about a session's work, with no compute.

### 2.7 Which cells the step-adjacent tail caveat affects: all 27

PV-2D REPORT §5 found the large-shift tail in cells beside a step in r greater than 0.1 drawn by the gate or a cut.

**On H2,** the share of each cell's prior weight in such fine cells (the union over the vertices) has a **minimum of
73.5 % and a median of 98.7 %**.

**By vertex,** the gate-drawn share has these medians:

| vertex | gate-drawn share (median) | why |
|---|---:|---|
| GENIE+MEC | 2 % | its r is smooth; its departures are at most 7 % |
| NuWro | 91 % | |
| GiBUU | 84 % | |

**What follows:**
- The with/without split of PV-2D §5 cannot be made on H2, because there are no H2 cells without the caveat.
- It applies to every cell, through the NuWro and GiBUU modes.
- The caveat should go on C_model,5D as a whole, as C_model,2D's caveat states it.

## 3. What is not available (no blocking item)

- **Per-event weights:** not retained, and not needed.
- **The ρ² PC fallback for L-5D-PV:** never run. It would take two new unfolds of about the J5 size (J5 was 0.23
  node-h for 5 steps, so this is an *estimate* of ≈ 0.1 node-h). It is not needed, because the PC is powered.
  <!-- absence-ok: checked 2026-10-24: receipts/SHA256SUMS lists no *_sq product, and the 30 files in the run's products/ on pscratch include none; tasks.tsv puts the fallbacks in job F, which never ran -->
- **GiBUU above 10 GeV/c:** GiBUU's prediction is defined only below 10 GeV/c (its ratio file's label). No product
  can supply it.
- **Other cells:** any cells drawn on fine edges can be built from the same products at 0 node-h, provided they are
  declared before the read. That covers a merge of H2 cells, a p_∥ split at 10, or the J cells.

## 4. Is H2 a poor support for the model term?

1. **GiBUU's range:** see §2.3. 14 cells are partial for GiBUU, and 8 of them have more than 10 % of their weight
   outside GiBUU's range.
2. **Low-purity cells concentrate the prior dependence.** These figures are from s5p's Stage-1 receipt (MC).
   - **The cells:** 11 of the 27 reported cells have purity below 0.1. They are cells 1, 3, 9, 11, 18, 19, 21, 25, 26,
     27 and 29, and together they hold 4.8 % of the prior weight.
   - **The worst:** five are below 0.04 (cells 1, 9, 11, 21 and 25). Cell 25 is at 0.007.
   - **Their closure bias is larger:**
     - the median |bias| is 3.6 % in these cells, against 1.2 % in the rest;
     - the rank correlation of purity with |bias| is −0.67.
   - **What to expect:** the largest s_k in these cells. Under item 2 they are the natural candidates for merging by
     simulation support, and that has to be decided before the data are read.
3. **Too few events: none in simulation.** The smallest reported cell has an MC n_eff of 12,030 (cell 25). Its
   expected reconstructed signal is 2,059.
4. **Concentration.** Here d_k is the truth-level departure the reweight puts on each cell (simulation only):
   d_k = Σ p r_k / Σ p − 1.
   - **It is spread, not concentrated:** the top 3 of 27 cells carry 30 % (GENIE+MEC), 42 % (NuWro) and 40 % (GiBUU)
     of Σ d², against 11 % if it were uniform.
   - **Its median |d| on the reported cells:** 3.7 % for GENIE+MEC, 6.0 % for NuWro and 12.0 % for GiBUU.
   - **Its maximum:** 7.2 %, 19.5 % and 39.3 %.
   - **The data shifts:** their concentration is unread. The build reports it.
5. **Coarseness averages.** Opposite-sign fine-cell shifts cancel inside an H2 cell. s5p's record has H2's h median
   at 9.6 % against J's 12.0 % (`RECORD-20260927-s5p-stage2-exit.md:126-131`; R, vertices D1–D5). This is a property
   of the definition, not a defect in the build. It matters for the 8.6 % bar, which is now descriptive.

## 5. Data-read discipline: a ruling for the director

- **What I read:** I read no (e) data product on H2. The ladder's committed readouts have no H2 space; they cover EW,
  J and (p_T, p_∥) only.
- **What s5p read:** s5p Stage 2, study P, already read R's data shifts on H2 under the MC prior reweighted to D1–D5,
  on 2026-09-27. Candidate R is configuration (e).
  - That gives the h median of 9.6 % and the p90 of 22.5 %.
  - Its record says: "No observed-data central value was compared with any prediction. The data shifts in study P
    are widths." (`RECORD-20260927-s5p-stage2-exit.md`, header).
- **The open question:** whether those widths count as "a refined-estimator data result" under item 2, and so close
  the window for declaring merges of H2 cells. That question is the director's, or Joseph's.
- **My recommendation:** bind the cell list first, the 27 or any merge from §4.2. Then the build reads the four data
  products once.

## 6. Retention

**What S2 needs kept** until C_model,5D is built and its inputs are committed by sha256, and then for as long as the
5D measurement may need it re-derived:
- the four L-5D-PV data products;
- the two closures;
- `prep/ratios/L-5D-PV/` (17 MB);
- P5 in RE-1's `out/5d/`.

That is about 18 MB of the ladder's 876 MB, plus one 95 KB file of RE-1's.

S2 does not need the rest of the ladder's products: the EW, 3D and 4D rungs and their logs.

**Re-raise date:** this goes into the retention item due before 2026-11-20 (`RUN.md` §6).

**MEASURES:** the H2 geometry, the reweights' simulation-level departures and tiers on H2, and the closure bias and
floor on H2. **CANNOT AUTHORIZE:** the H2 cell list, C_model,5D, any claim, or any change to the declared PC.
