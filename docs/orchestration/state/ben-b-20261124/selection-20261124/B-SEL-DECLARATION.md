# (b) part 1: the frozen selection of R00–R15 (declaration, rev 1; tier3-design, 2026-11-24)

**Authority:**
- Joseph's (b) design, `~/codex-reports/note-measurement/b-design-20261124/B-SPEC-DRAFT.md`, sha256
  `2c735ebce02b49281561103311efca790ca1866d6c47036a2748a7ed5d157395`, §1;
- the director's assignment of 2026-11-24 (part 1);
- the director's ruling of 2026-11-24 that the estimator is frozen at E_R / B0 (S2R FAILED, `fd/s2r-20261124/run-20261124/`).

**This text is fixed before any input below is read for this purpose.** Its sha256 goes to the director before the
read connect, and nothing is tuned on the output.

**Disclosure.** The rule was introduced after the data were seen. It uses simulation only, and the spent truths
only: no seal, no sealed output and no data. Where the disclosure appears is Joseph's call, and no wording is proposed
here.

## 1. Population and inputs

**The truths, 14:**
- the 12 graded F0b truths: nominal, W1, W2, W3, q3, stage0c_gibuu, closure_nuwro, A7_mnvtune, A7_genie_cv,
  A7_genie_mec, A7_nuwro and A7_gibuu;
- the two spent F1 tunes: F1_genie_v3_g18 and F1_genie_v3_ar23, the 20-experiment ensembles.

**The estimator:** E_R (configuration R, LightGBM 100/8, 5 iterations, seed 42, the 400/31 refinement), frozen. Every
input below was produced by it (F0 control 2; F1 §"The estimator (e)").

**Committed inputs**, read at the binding's commit with these sha256:

| input | sha256 | used for |
|---|---|---|
| `fd/with-cpl/readout/fd_f0b_readout.json` | `5f542830561731b567f2b97d78e5e9677a9802a35ef9c21855828bf184e6f3d6` | b̂ and noise_sigma for the 12 F0b truths |
| `fd/readout/fd_f1_readout.json` | `cbe411a926a7392e4aa085c7beba6e1bda45aff55d937998c53e49f27e3516c7` | b̂ and noise_sigma for the 2 F1 tunes |
| `fd/receipts-prr/read/cluster/readout.json` | `9238f22bfe29685e33c1d5bb46da3938a3ebfdc93a54575a4fe99de3a7af9ead` | d_t = X_t/P − 1 at split 991000, for the F0b truths other than closure_nuwro |
| `fd/gencmp-e/rerun1/chain/chdefs/with/readout/fd_g_readout.json` | `a19009e0bd83b9bb8f9ad65fb65804e6f62c8953310103fbfe6fce5f84995875` | g on R00–R15 for GENIE CV, GENIE+MEC, NuWro, GiBUU and Tune v1 (CH, analysis definitions) |
| `nd-unfolding/pv-ladder/readouts/h2_definition.json` | `b67907615fe2e903e60ae6caa1c141fa007676c0a1b3ae9f42490d331bfdda89` | the cell matrix M16, through `estimator_stability_analyze.cell_matrix`, as FD-PRR and T3 use it |

The `fd/` paths are under `docs/orchestration/state/measurement-paper/5d-community-20261024/`.

**Inputs fetched by one bound login read connect** (O_NOATIME, each copy refused unless it is its pin):

| input | pin | used for |
|---|---|---|
| `/pscratch/sd/j/josephrb/fd-f0b-20261026/fd_f0b_experiments.npz` | `7384c6518aa0f59bd4964170fcc9b652f1c31958f422f1e1b597cd3e59219ad9` (retention SHA256SUMS) | per-experiment r for every graded set: the controls, and row 4's 16 per-split values |
| `/pscratch/sd/j/josephrb/fd-f1-20261027/grade/fd_f1_experiments.npz` | `997c7dae34ef9703291baece51eed05f3dd7d38a043630cac9667efaad2775bc` (same) | the F1 controls |
| `/pscratch/sd/j/josephrb/fd-f1-20261027/f1c/closure/f1_closure_genie_v3_g18.npz` | `198205b6466a4b7ab65555c15c3248b379830a4d6a376b1599fe51923aeb4c94` (`fd/receipts-f1/run/cluster/manifest/f1-products-SHA256SUMS`) | the G18 truth's cell integrals |
| `/pscratch/sd/j/josephrb/fd-f1-20261027/f1c/closure/f1_closure_genie_v3_ar23.npz` | `532a6ac014274e54f2c1fa82b46a3411ff0a62c803e108cf85fa6bcfe070e208` (same) | the AR23 truth's cell integrals |
| `/pscratch/sd/j/josephrb/pv-ladder-20261024/products/L-5D-PV_e_closure_tune_v1.npz` | `eb3e218866dd36e093c85e85a791f8dd8de1491f4ad0694924644b01c8e55f08` (`cmodel_5d.json` products_sha256) | the Tune v1 truth's cell integrals, on the same MC and pipeline as the F1 and NuWro closures |
| `/pscratch/sd/j/josephrb/pv-ladder-20261024/products/L-5D-PV_e_closure_nuwro.npz` | `fff9030e7fd63c538b27c58f2a35417b5d28c3d2f6de2880219b181812215182` (same) | the closure_nuwro truth's cell integrals |

- **If pscratch has purged a file,** it is retrieved by htar from its HPSS archive on a loginNN, never a DTN, and
  checked against the same pin.
- **The two experiment tables** hold relative residuals only. The four closure products hold simulation only, with no
  data.

## 2. Definitions

- **Cell integrals:** X = M16 · x for a product's `xtrue_flat` (the S1 rule).
- **Truth-relative bias:** r = X̂/X_true − 1 (F0 §4). b̂_{c,t} and its noise σ_{c,t} = √(N_t)_cc are the readout's
  `bias` and `noise_sigma`. For rows 1–2 and F1, N = Cov(r)/B over experiments that each draw Poisson pseudo-data and
  a fresh MC split (`s5n_pseudo`, `split_key_for(seed)`). For row 4 (the A7 truths), N is the same over 16 noise-free
  MC splits. closure_nuwro has N = 0.
- **The Tune v1 unit:** R_{c,t} = X_true,c,t / X_TuneV1,c.
  - For every F0b truth except closure_nuwro: R = 1 + d_{c,t}, with d from FD-PRR's readout (`table["B0/<t>/s991000"]["d"]`).
    There P is the nominal truth, the Tune v1 MC truth at split 991000. So R = 1 exactly for nominal and A7_mnvtune.
  - For closure_nuwro: R = X(L-5D-PV_e_closure_nuwro)/X(L-5D-PV_e_closure_tune_v1), from the fetched `xtrue_flat`.
  - For F1_genie_v3_g18 and F1_genie_v3_ar23: R = X(f1_closure_genie_v3_<tune>)/X(L-5D-PV_e_closure_tune_v1). The F1
    closures are the NuWro closure's `pvl_unfold.py` line (FD-F1-DECLARATION.md:182-184), so the MC and the pipeline
    are the same as the Tune v1 closure's.
  - **Disclosed approximation:** R is taken at one MC subset (split 991000, or the pvl closures' MC), while b̂ averages
    over splits. The effect is second order (b̂ times a split difference of the truth integrals) and is not corrected.
- **Bias in Tune v1 units:** β_{c,t} = b̂_{c,t} · R_{c,t}, and SE_{c,t} = σ_{c,t} · R_{c,t}.
- **Finite-MC split variation, counted once:**
  - rows 1–2, F1 and row 4 already carry it in N, so nothing is added;
  - closure_nuwro is a single-split estimate, so its SE² gets the pooled single-split variance added:
    s²_c = (1/5) Σ_{t ∈ A7} Var_s(r_{c,t,s} · R_{c,t}), with ddof 1 over row 4's 16 splits, from the F0b table.
- **The guarded bound:** U_{c,t} = |β_{c,t}| + 1.96 · SE_{c,t}.
- **The generator spread:** S_g,c = √((1/3) Σ_{a<b} ((g_a,c − g_b,c)/g_TuneV1,c)²), over a, b ∈ {GENIE CV, GENIE+MEC,
  NuWro}, with g the readout's `predictions[*].g`.
  - Tune v1 is the unit and is excluded from the panel, because it is the prior.
  - **The GiBUU-added sensitivity printout** is S_g^+,c, the same over the 4 generators (6 pairs). It is computed on
    the cells where GiBUU is supported (p∥ < 4.5: R00–R03 and R08–R11, FD-F0-DECLARATION.md:259). Elsewhere it is
    printed as "not defined".

## 3. The rule (κ = 1)

- **A cell c is measured** if and only if both hold:
  - max_{t ∈ T} U_{c,t} ≤ 1.0 · S_g,c, the worst of the 14 guarded bounds;
  - it does not flip (below).
- Otherwise it is exploratory.
- **Flip.** The supported MC splits are row 4's 16 noise-free splits at each of the five A7 truths. These are the
  population's only per-split estimates; rows 1–2 and F1 mix Poisson noise into each experiment.
  - For each A7 truth t and split s, recompute the label with U_{c,t} replaced by
    U_{c,t,s} = |r_{c,t,s} · R_{c,t}| + 1.96 · SE_{c,t}, every other truth unchanged.
  - The cell flips if any of these 80 labels differs from its label at the means.
  - A flipping cell is exploratory.
- **Discrimination flag.** A measured cell is flagged as able to tell generators apart if
  max_t U_{c,t} ≤ 0.5 · S_g,c. Otherwise it is "measured, not discriminating". A named model pair's own separation
  replaces 0.5 · S_g only when that pair defines a question, and no such pair is named here.
- **No absolute bias cap, and no minimum number of cells.** With k = 0 measured cells, there is no measured-set test.
- **Printed for every cell:**
  - S_g and S_g^+;
  - U_{c,t} for each truth, and the worst truth;
  - the label, the flip details, and the discrimination flag;
  - the label recomputed with S_g^+ in place of S_g. That one is a sensitivity printout, not a label.

## 4. Controls (each a STOP)

- **C-PIN:** every committed input is at its sha256 above, and every fetched copy at its pin.
- **C-TAB:** for each of the 14 truths, the table's own mean and Cov/B reproduce the readout's `bias` and `noise_sigma`
  to 1e-12 relative. closure_nuwro is checked as r with N = 0 against the readout, and the F1 table against the F1
  readout.
- **C-R:**
  - R > 0 everywhere, R = 1 exactly for nominal and A7_mnvtune, and the d vectors are the 12 FD-PRR truths at split
    991000;
  - the closures' X > 0 on all 16 cells;
  - descriptive only: X(closure_tune_v1) set against g_TuneV1 cell by cell.
- **C-SG:** S_g > 0 on all 16 cells. The three generators are present with 16 cells each.
- **C-SPLIT:** row 4 holds 16 distinct split seeds per A7 truth, 970000–970015 (F0 control 3).
- **C-LEAK:** the record holds no absolute cross section, only relative quantities, R and the labels, as in F0's leak
  guard.

## 5. Outputs, code and what this cannot authorize

- **Code:** `nd-unfolding/bsel/bsel_select.py`, with tests and mutants, and a line trace before any review. It is run
  locally on the fetched copies. The record (`selection.json` and `selection.txt` with their sha256) is committed
  under this directory and goes to the director first.
- **CAN:** the frozen measured/exploratory labels for R00–R15 and the discrimination flags, for the (b) amendment
  (rev 12 §4.4).
- **CANNOT:**
  - any statement about data;
  - any held-out claim;
  - any covariance validation;
  - any change of estimator;
  - any note wording.

The OmniFold-against-IBU printout (spec §2) is not part of this selection.
