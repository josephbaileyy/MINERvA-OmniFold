# H2 reporting definition and C_model,5D: declaration (2026-10-24, session "2d test")

**Status: a draft for the director's review.**
- The cell definition is an estimand choice, so Joseph approves it before it is bound.
- Nothing is built. No (e) data product has been opened in this pipeline.

**Assignment.** The director's request of 2026-10-24, which followed S2 (PR #332, main `b485ef45`). It applies the
director's ruling on item 2 of `DECISION-20261024-joseph-5d-community-standard-route.md`:
- **(a)** A rule using only MC and generator-truth quantities chooses any merge, restriction or split of the H2 cells.
  The rule is declared and committed before anyone computes an H2-level quantity from an (e) data product in this
  pipeline.
- **(b)** The rule may not use h, the s_k, or any width or shape derived from data.
- **(c)** The declaration lists the earlier reads.

**Summary.**
- **The merge rule is MC purity below 0.1, merged into the purest neighbouring box.** It turns H2's 27 reported cells
  into **16 reporting cells**, so H2 changes.
- **GiBUU's shift is carried as measured, with a label.**
- **C_model,5D is S2 §2's construction on the 16 cells.**
- **The PC is graded on the 27 base H2 cells,** because the 16 cannot power the declared rule (§3.3). That point needs
  the director's agreement.

## 0. Earlier reads of (e) data results (the ruling's clause c)

The definition below does not use any of these. They are listed because they were read before it.

| when | what | where |
|---|---|---|
| 2026-09-26 | s5p Stage 1: data-bootstrap widths of R on the H2 cells (`sigma_boot_data_R`) | `state/s5p/stage1/stage1_inspect.json` |
| 2026-09-27 | s5p Stage 2, study P: R's data-shift widths on H2 under D1–D5. h median 9.6 %, p90 22.5 %, GiBUU dominant in 13 of 27 cells | `RECORD-20260927-s5p-stage2-exit.md` §4 |
| 2026-10-22 | RE-1's P5, configuration (e)'s 5D data central value (`k1_p5_rerun.npz`) | `methods-paper/re1-20261022/` |
| 2026-10-24 | Stage 0: the h medians on H2 including the D1 data unfolds (9.603 % with D1, 4.277 % without), and 0b's usefulness on H2, which uses C_stat(e) (u* 7.45 %) | `state/measurement-paper/5d-design-20261023/STAGE0-REPORT.md` §2 |
| 2026-10-24 | The PV ladder's L-5D-PV (e) readouts on the 39 EW, 109 J and 205 (p_T, p_∥) cells | `state/measurement-scoping/pv-ladder/REPORT.md`; `readouts/L-5D-PV_e.json` |

S2 opened no data product. The ladder's committed readouts have no H2 space.

## 1. The merge rule

### 1.1 The rule, applied mechanically

The rule is implemented in `nd-unfolding/pv-ladder/h2_definition.py`, whose `merge()` gives it as code:

1. **Start** from the 32 H2 cells (`s5p_stage1_inspect.H2_EDGES`), each its own box.
2. **Test.** A box is *low-purity* if two things hold:
   - it is reported under s5p's support rule: expected reco-level signal and truth-selected weight at data POT both
     ≥ 1000;
   - its MC purity is below **τ = 0.1**.

   Purity is reco-and-truth-in-the-same-box weight over reco-in-the-box weight, as `s5p_stage1_inspect.mc_properties`
   defines it.
3. **Merge.** While a low-purity box exists:
   - take the one with the lowest purity (ties go to the lowest first H2 index);
   - among the boxes it can join into a box (equal on four axes and complementary on the fifth), take the one whose
     union has the highest purity (ties go to the lowest axis, then the lowest first H2 index);
   - merge the two, and test again.

   A low-purity box with no partner is kept and flagged. None was flagged.
4. **Report** the boxes that are reported after the merges, ordered by their lowest H2 index.

**What the rule uses:** purity, the support sums and n_eff, all additive over a box's MC rows. They come from a
32 × 32 reco–truth migration matrix of the simulation.

**What it does not use:** closure bias, the truth departure and generator ranges, although the ruling allows them.
Above all it uses no data. `h2_definition.py` loads only the npz keys `MCgen`, `MCreco`, `pass_reco`, `pass_truth`,
`w_truth` and `w_reco`. It never loads `measured` or `measured_weights`, and it opens no unfold product.

**Where τ = 0.1 comes from.** It is the threshold S2 used to name the candidate cells, which the director carried into
this request. It was not tuned: the rule ran once.

### 1.2 Provenance of the run

- **The rule was committed before its run.** The commit is `7cb80cc2`, and `h2_definition.py` has sha256
  `44848eb12805d362d0c3e6f90fb8c9ba4f527f2f11672fe069be11e578642ea2`. It ran once, on login node `saul`, on
  2026-10-24.
- **Environment and cost:** Python 3.11 from `setup_salloc_env.sh`. The run took 35 s wall-clock with 5.5 GB peak
  memory, at 0 node-h.
- **Inputs:**
  - the 5D npz `/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz`, sha256
    `07fccc1abc7204bc29349b4ba96850986fe91e909e83fc54e8d1a6b3922a649f`, checked by the script;
  - s5p's Stage-1 receipt, sha256 `def4c67cfb59f5ae917f86d2745416b172be6aca3764eba11f3d116db4621d9d`;
  - `s5p_stage1_inspect.py`, sha256 `26569afc…3d71`, which is the receipt's own `code_sha256`.
- **Output:** `nd-unfolding/pv-ladder/readouts/h2_definition.json`, sha256
  `b67907615fe2e903e60ae6caa1c141fa007676c0a1b3ae9f42490d331bfdda89`. A copy and the run log are in
  `/pscratch/sd/j/josephrb/h2def-20261024/`.
- **Control:** the 32 single-cell boxes reproduce the Stage-1 receipt's purity, stability, n_eff, expected reco signal,
  truth-selected weight and reported flags with a maximum relative difference of 0. The script refuses at 1e-9.
- **Tests:** `test_pvl.H2Definition` tests the procedure on toy migration matrices. It checks that a leaking cell joins
  its purest neighbour into a box, that a grid with no low-purity cell is unchanged, and the box and join logic.

### 1.3 The resulting cells

The rule made 12 merges, in this order:

| step | box (purity) | joins | axis | union purity |
|---:|---|---|---|---:|
| 1 | 25 (0.0069) | 24 | W | 0.584 |
| 2 | 11 (0.0117) | 15 | E_avail | 0.446 |
| 3 | 9 (0.0281) | 8 | W | 0.846 |
| 4 | 1 (0.0349) | 0 | W | 0.714 |
| 5 | 21 (0.0369) | 23 | q₃ | 0.695 |
| 6 | 3 (0.0409) | 7 | E_avail | 0.715 |
| 7 | 27 (0.0512) | 31 | E_avail | 0.780 |
| 8 | 26 (0.0655) | 30 | E_avail | 0.312 |
| 9 | 29 (0.0740) | 28 | W | 0.476 |
| 10 | 18 (0.0750) | 16 | q₃ | 0.510 |
| 11 | 19 (0.0793) | 17 | q₃ | 0.080 |
| 12 | 17, 19 (0.0799) | 21, 23 | E_avail | 0.719 |

**The 16 reporting cells.** Cell index is 16·i_pT + 8·i_p∥ + 4·i_E + 2·i_q₃ + i_W. In the box column, "all" means
the box spans that axis's whole range.

| cell | H2 cells | box: p_T / p_∥ / E_avail / q₃ / W | purity | stability | MC n_eff |
|---|---|---|---:|---:|---:|
| R00 | 0, 1 | <0.7 / <4.5 / <0.8 / <2 / all | 0.714 | 0.800 | 2,934,519 |
| R01 | 3, 7 | <0.7 / <4.5 / all / ≥2 / ≥1.8 | 0.715 | 0.775 | 3,739,551 |
| R02 | 4 | <0.7 / <4.5 / ≥0.8 / <2 / <1.8 | 0.392 | 0.185 | 855,718 |
| R03 | 5 | <0.7 / <4.5 / ≥0.8 / <2 / ≥1.8 | 0.274 | 0.289 | 486,035 |
| R04 | 8, 9 | <0.7 / ≥4.5 / <0.8 / <2 / all | 0.846 | 0.814 | 3,930,993 |
| R05 | 11, 15 | <0.7 / ≥4.5 / all / ≥2 / ≥1.8 | 0.446 | 0.632 | 864,734 |
| R06 | 12 | <0.7 / ≥4.5 / ≥0.8 / <2 / <1.8 | 0.455 | 0.162 | 720,780 |
| R07 | 13 | <0.7 / ≥4.5 / ≥0.8 / <2 / ≥1.8 | 0.306 | 0.283 | 331,614 |
| R08 | 16, 18 | ≥0.7 / <4.5 / <0.8 / all / <1.8 | 0.510 | 0.610 | 1,388,929 |
| R09 | 17, 19, 21, 23 | ≥0.7 / <4.5 / all / all / ≥1.8 | 0.719 | 0.675 | 4,069,981 |
| R10 | 20 | ≥0.7 / <4.5 / ≥0.8 / <2 / <1.8 | 0.383 | 0.217 | 844,187 |
| R11 | 22 | ≥0.7 / <4.5 / ≥0.8 / ≥2 / <1.8 | 0.319 | 0.260 | 590,325 |
| R12 | 24, 25 | ≥0.7 / ≥4.5 / <0.8 / <2 / all | 0.584 | 0.699 | 2,094,675 |
| R13 | 26, 30 | ≥0.7 / ≥4.5 / all / ≥2 / <1.8 | 0.312 | 0.472 | 880,862 |
| R14 | 27, 31 | ≥0.7 / ≥4.5 / all / ≥2 / ≥1.8 | 0.779 | 0.787 | 3,953,897 |
| R15 | 28, 29 | ≥0.7 / ≥4.5 / ≥0.8 / <2 / all | 0.476 | 0.251 | 1,138,930 |

**Coverage:**
- **Unreported boxes:** 2, 6, 10 and 14.
  - Cells 2, 10 and 14 are empty.
  - Cell 6 has MC n_eff 1 and 0.17 of truth weight.
- **R09 absorbs H2 cell 17**, which s5p left unreported (MC n_eff 5,678, 0.01 % of the prior), because 19 and 17 joined
  first.
- **The 16 cells hold 100.0 % of the prior's truth weight in the grid, to within 3e-8.**
- **The smallest reporting cell by expected reco signal is R11, at 25,155.** Under H2, cell 21 was the smallest at
  1,999.

**Descriptive, simulation only, not used by the rule.** These are from
`nd-unfolding/pv-ladder/h2_definition_describe.py` (sha256 `e509e2f7…7991`), written to
`readouts/h2_definition_describe.json` (sha256 `da7edae080a201bec17e877348629ec0756e688e2b33299b77d5567ab32416ec`).
They come from L-5D-PV's frozen reweights and its two closure unfolds.

| cell | prior share | d GENIE+MEC / NuWro / GiBUU | GiBUU r = 1, p∥ ≥ 10 | step-adjacent | NuWro closure bias |
|---|---:|---|---:|---:|---:|
| R00 | 11.3 % | +7.0 % / +3.3 % / +6.7 % | 0 % | 100 % | −0.21 % |
| R01 | 11.8 % | −4.3 % / +9.0 % / −2.8 % | 0 % | 97 % | +0.66 % |
| R02 | 2.4 % | −3.0 % / −14.1 % / −39.3 % | 0 % | 100 % | +1.19 % |
| R03 | 1.3 % | −5.6 % / −0.4 % / −29.5 % | 0 % | 100 % | −6.83 % |
| R04 | 17.7 % | +6.9 % / +4.6 % / +11.5 % | 7 % | 99 % | −0.09 % |
| R05 | 3.0 % | −3.7 % / +10.3 % / −7.7 % | 17 % | 82 % | −0.80 % |
| R06 | 2.3 % | −2.4 % / −14.3 % / −32.9 % | 7 % | 100 % | +2.32 % |
| R07 | 1.0 % | −5.2 % / −3.0 % / −23.6 % | 8 % | 97 % | −4.02 % |
| R08 | 4.1 % | +0.9 % / −0.9 % / +2.2 % | 0 % | 99 % | +1.27 % |
| R09 | 12.9 % | −4.5 % / −6.3 % / +5.5 % | 0 % | 99 % | +0.95 % |
| R10 | 2.4 % | −3.3 % / −10.7 % / −17.1 % | 0 % | 100 % | −3.31 % |
| R11 | 1.7 % | −3.7 % / −3.9 % / +10.9 % | 0 % | 100 % | −4.99 % |
| R12 | 6.9 % | +1.8 % / +1.5 % / +2.9 % | 8 % | 93 % | +1.04 % |
| R13 | 2.8 % | −2.9 % / −3.4 % / +10.8 % | 11 % | 95 % | −2.41 % |
| R14 | 14.8 % | −2.4 % / −1.5 % / −2.8 % | 38 % | 77 % | −0.16 % |
| R15 | 3.6 % | −3.9 % / −12.5 % / −15.1 % | 9 % | 98 % | −0.01 % |

- **Closure floor** (`_closure_tune_v1`): at most 3.2e-5 on every cell.
- **The large closure biases have moved.** Every merged cell but R13 (−2.4 %) has |bias| ≤ 1.3 %. The largest are in
  cells the rule left alone, at purity 0.27–0.38 and stability 0.22–0.29: R03 −6.8 %, R11 −5.0 %, R07 −4.0 % and R10 −3.3 %.
- **Low stability remains** in R02, R06, R10 and R15 (0.16–0.25). The rule uses purity only. A stability criterion
  would be a second rule, so I do not add one. If the director or Joseph wants one, it has to be declared before the
  build.

## 2. GiBUU at high p_∥: carry the shift as measured, with a label

**The choice.** s_GiBUU goes into C_model,5D as measured on all 16 cells. It carries the label "GiBUU's shape applied on
p_∥ < 10 GeV/c; above it the prior is unchanged". The p_∥ = 10 split is not taken.

**What the restriction leaves.** Seven reporting cells hold prior weight that GiBUU leaves at r = 1 above
10 GeV/c: R04, R05, R06, R07, R12, R13 and R15 hold 7–17 %, and R14 holds 38 %.

**Why the split is not taken:**
- **It does not recover GiBUU above 10 GeV/c.** GiBUU has no prediction there. It would only isolate cells where
  GiBUU's mode is identically unweighted, so its shift there would be migration alone.
- **It would change the base partition.** The upper p_∥ bin becomes two, and the rule of §1 would have to run again on
  48 cells. That is a different estimand from the H2 Joseph chose.
- **The label is the honest statement.** In the affected cells s_GiBUU is a partial-range shift. It measures GiBUU's
  shape below 10 GeV/c, not GiBUU's full dependence.

## 3. C_model,5D: the construction (S2 §2, on the 16 cells)

### 3.1 Shifts and the matrix

- **Cell integral:** X_k,c = Σ_{f ∈ c} x_k,f · vol_f over the 65,856 fine cells f whose reporting cell is c. Here x_k
  is `xsec_flat` of `L-5D-PV_e_<k>`, and fine cells are assigned by centre through `coarse_map` and then
  `h2_to_reporting_cell`.
- **Shift:** s_k,c = X_k,c / X_0,c − 1 for k ∈ {GENIE+MEC, NuWro, GiBUU}, with X_0 from `L-5D-PV_e_tune_v1`.
- **The matrix:**
  - S is 3 × 16, and C_model,5D = SᵀS with κ = 1. It is fractional.
  - The outer products are summed elementwise in a fixed order, as `build_cmodel.cmodel()` does, so the matrix sha256
    does not depend on the platform.
  - Each vertex is one fully correlated mode, and the three are summed as if independent.
- **C_abs** = diag(x) C_model diag(x), with x = X_0. X_0 is (e)'s central value on these cells, because
  `L-5D-PV_e_tune_v1` equals P5 bitwise.
- **What is committed:** S, √diag, the rank and singular values, the per-vertex trace shares, the coverage counts of
  §3.3 and both matrices' sha256 go in a JSON, as `cmodel_2d.json` does. The npz stays on pscratch.
- **Labels:**
  - "generator-shape model dependence; not a calibrated bound";
  - the GiBUU label of §2;
  - the step-adjacent caveat (§3.4);
  - the decision's stated limitation that coverage was not validated.
    <!-- absence-ok: a label the paper must carry, quoting DECISION-20261024-joseph-5d-community-standard-route.md item 3, not a claim about the record -->
- **The reweights are not re-applied.** The products carry L-5D-PV's frozen r_k from run pin `ee299e10`. The builder
  reads only `xsec_flat`, plus `xtrue_flat` for the closures.
- **No new noise gate.** The 5 % gate was applied once, on the fine grid (S2 §2.4).

### 3.2 NC, required

- (a) `L-5D-PV_e_tune_v1`'s `xsec_flat` is `array_equal` to P5's on the full grid. The ladder recorded this as
  `bitwise_full_grid: true`; the builder repeats the check.
- (b) X_0 equals P5's integrals on the 16 cells, bitwise.
- (c) The cell integrals by `pvl_lib.integrated` equal those by `s5p_stage1_inspect.fine_volume`. S2 measured 0 on the
  closure truths.
- (d) The builder's internal checks:
  - SᵀS reproduces C_model;
  - h = max_k |s_k|;
  - the definition's sha256 is `b6790761…da89` and its fine-map sha256 is `930326a3…e18c`.

  The builder refuses otherwise.

### 3.3 PC at NuWro: the declared rule, graded on the 27 base H2 cells

**The rule is unchanged** (`pv2d_lib.positive_control`). It compares the data shift s_NuWro with minus the closure bias
of `L-5D-PV_e_closure_nuwro` against its truth. It needs at least 20 cells with |bias| > 1 %, corr ≥ 0.7, and a slope
in [0.67, 1.5].

**Where it is graded: on the 27 reported H2 cells,** the partition the reporting cells are built from.
- **The 16 cells cannot power it.** Only 9 of the 16 have |bias| > 1 %, measured from simulation. On them the rule would
  return NOT_POWERED, and its ρ² fallback needs the same 20 cells.
- **The 27 base cells can.** S2 measured 21 of 27 with |bias| > 1 %.
- **This choice is the director's to accept.** The alternative is to grade on the 16 cells and label C_model,5D
  "positive control not powered".

**A known risk, with the rule unchanged.** The margin on the 27 cells is thin: 5 of the 21 cells have |bias| between
1.04 % and 1.21 % (H2 cells 4, 7, 16, 23 and 24). The bias is fixed, so the count cannot move at the build. But a
criticism that the control is barely powered is fair.

**Reported, ungraded, on the 16 cells:** `pv2d_lib.linear_response` of s_NuWro against minus the bias.

**Descriptive coverage, as for C_model,2D, on the PC cells of the 27-cell grading:** counts where |s_NuWro| ≥ |bias|,
where √(s_GENIE+MEC² + s_GiBUU²) ≥ |bias|, and where √diag C ≥ |bias|. The last includes the bias's own vertex, so it
is not evidence of coverage.

**If the PC fails,** C_model,5D is still written, labelled "positive control failed: not evidence". No total is formed
until the director rules.

### 3.4 The step-adjacent caveat

It applies to every reporting cell. In each cell, 77–100 % of the prior weight lies beside a gate- or cut-drawn step in
r > 0.1 (§1.3 table). It goes on C_model,5D as a whole.

### 3.5 Cost and order

- **Cost:** 0 node-h. It is numpy on a laptop or the login node, in seconds, plus a builder and tests modelled on
  `build_cmodel.py`.
- **Order:**
  1. this declaration is approved by Joseph and bound by the director;
  2. then the builder reads the four data products, once.

  Nothing H2-level is computed from an (e) data product before step 1.

## 4. Products to read, by sha256

All are under `/pscratch/sd/j/josephrb/pv-ladder-20261024/` unless the row says otherwise.

| product | sha256 | role |
|---|---|---|
| `products/L-5D-PV_e_tune_v1.npz` | `dbe9a95e746fba127811182e9a352f6dc243d78ff699e803611b5deedbcb0f4f` | X_0 and x |
| `products/L-5D-PV_e_genie_mec.npz` | `bdff9193b04f17c4aa9d97e7d9c26221b03dc8c9b0d2376cd775e6b195b749c5` | s_GENIE+MEC |
| `products/L-5D-PV_e_nuwro.npz` | `caf6eee726ddb128d26cf74fad2a2b4e69273607a2a0e1e4a48750766bddc66f` | s_NuWro; PC data side |
| `products/L-5D-PV_e_gibuu.npz` | `bdf331570daeb3dc56d6096e2c39ca3e7a6091339680eb58034ee9a14c82f3c3` | s_GiBUU |
| `products/L-5D-PV_e_closure_nuwro.npz` | `fff9030e7fd63c538b27c58f2a35417b5d28c3d2f6de2880219b181812215182` | PC bias |
| `products/L-5D-PV_e_closure_tune_v1.npz` | `eb3e218866dd36e093c85e85a791f8dd8de1491f4ad0694924644b01c8e55f08` | closure floor |
| `/pscratch/sd/j/josephrb/methods-paper/re1-20261022/out/5d/k1_p5_rerun.npz` (P5) | `e36f3b25459e068cec9dba941f7b3aea8f48c6e22c931fde7c9d315e7b1e8de2` | NC target |
| `nd-unfolding/pv-ladder/readouts/h2_definition.json` (git) | `b67907615fe2e903e60ae6caa1c141fa007676c0a1b3ae9f42490d331bfdda89` | the cells |
| `docs/orchestration/state/s5p/stage1/stage1_inspect.json` (git) | `def4c67cfb59f5ae917f86d2745416b172be6aca3764eba11f3d116db4621d9d` | the 27 base cells (PC) |

## 5. What S1 needs from this definition

1. **The cells.**
   - Use `h2_definition.json`'s `h2_to_reporting_cell` on top of `s5p_stage1_inspect.coarse_map(H2_EDGES)`, which
     assigns fine cells by centre.
   - Check the expanded fine map against `fine_map_sha256_int32le` = `930326a3a7c0852d4047b5468d8ea3b63d046b896e4a4de1557e29f95102e18c`.
     That is the sha256 of the 65,856-entry little-endian int32 map, with −1 meaning not reported.
2. **The order:** R00–R15, as the table above gives them.
3. **The integral convention:** cell integrals Σ x_f · vol_f of the fine-grid differential cross section.
   - C_model,5D is fractional, so it does not depend on the convention.
   - S1's covariance must be on the same 16 integrals, or on the same cells converted by the same diagonal, so that
     C_abs and the (e) covariance add.
4. **The estimator and central value:** configuration (e), with x = P5. The decision's item 5 asks for central value and
   covariance from the same estimator.
5. **Coverage:**
   - the unreported boxes 2, 6, 10 and 14 are excluded;
   - H2 cell 17 is included, inside R09;
   - S1's support masks must follow the fine map, not s5p's 27-cell `reported` flags.

## 6. Retention

- The build needs the ≈ 18 MB that S2 named, plus P5. The director carries that on the re-raise list due before
  2026-11-20.
- To re-run §1 needs the 5D npz in the project area, which is the project's main input, not this lane's.
- This lane's own copy of the run is `/pscratch/sd/j/josephrb/h2def-20261024/`: code copies, the output and the logs,
  under 1 MB.

**MEASURES:** the definition's MC purity, stability and support, and simulation-only descriptions of its cells.
**CANNOT AUTHORIZE:** the reporting definition (Joseph approves it, and the director binds it), C_model,5D, the PC's
grading population, or any claim.
