# PLAN FD: the 5D fake-data test and generator comparisons on the 16 H2 cells (2026-10-25)

**By** the measurement session, for the director. This is the director's FD-PLAN assignment of 2026-10-25, given
under Joseph's approval of the scoping ("okay scope the fake data test"). The director is recording Joseph's words in a
decision record.
- **Scoping only:** 0 node-h. No job was submitted.
- **Cluster reads:** login37 (via `saul`), 2026-10-25 15:55–16:30 UTC. Only `ls`, `find -printf`, `du`,
  `sha256sum`, npz header and `meta` reads, `myquota` and `hpssquota`. The header reads touched about 90 product
  files and may have refreshed their access times.
- **Repo reads:** main at `771dfb39`.

**CITABLE FOR:**
- the inventory of fake-data evidence for (e) that exists on disk, with truths, priors, grids, configurations and
  sha256;
- whether each item can be re-graded on R00–R15 against S1's C_total from existing products;
- the leave-own-vertex-out covariances and their per-cell widths;
- the candidate truths outside the C_model vertex set, with what each would cost;
- the declared test statistics and what each is for;
- the generator predictions that exist on the 16 cells;
- unit costs with their sources, caps and storage.

**NOT CITABLE FOR:**
- any result of the tests: none was computed;
- any authorization. Any compute needs Joseph's approval, then a declaration and a binding;
- any reading of the data against a generator, which needs Joseph's explicit approval (§4);
- any claim, printed wording or conclusion about publishability, which are Joseph's.

## 0. Answer

**Four families of fake-data products for (e) already exist, 8,465 products in all.** Every product stores its
unfolded and its true cross section on the full 65,856-cell fine grid (`xsec_flat`, `xtrue_flat`). So every one can
be integrated onto R00–R15 and graded against S1's C_total (`db000707…`) from existing products only, at 0 node-h on
a login node (§1). The families are:
- the Stage 0 / s5e assessment ensembles: 140 pseudo-experiments at six truths;
- the L-5D-PV noise-free closures: 2, NuWro and the floor;
- the s5p joint-test (A7) calibration ensembles: 7,176 pseudo-experiments at five generator truths, with nuisances
  drawn per experiment;
- the A7 power ensembles: 1,147 at six alternatives.

None was ever graded on the 16 cells or against an (e) covariance. Stage 0 graded on J and the 27 base H2 cells, A7 on
J, and the closure on the 27 base cells.

**Circularity (§2).** Every existing generator-family truth shares its generator with a C_model,5D vertex.
- A7's GENIE MEC, NuWro and GiBUU nulls read **the same prediction files** as the vertices (`c179855d…`,
  `475a2871…`, `48917692…`).
- The leave-own-vertex-out C_total, C_e + Σ_{j≠k} diag(f) s_j s_jᵀ diag(f), can be built at 0 node-h from S1's npz and
  C_model,5D's S.
- Its median relative σ per cell is 6.46 % without GiBUU, against 6.74 % with all three vertices. Without NuWro or
  without GENIE+MEC the median is unchanged at 6.74 %. The largest cell falls from 13.69 % to 8.78 % without GiBUU
  **(arithmetic, §2.1)**.

**Truths outside the vertex set.**
- **On disk:**
  - A7's **GENIE 2.12.10 CV** null, 1,366 experiments. Its prediction is the vertices' reference, not a vertex.
  - s5e's synthetic **q3 | (E_avail, W) tilt**, 20 experiments.
  - The two closures at the prior: s5e nominal (40) and A7 MnvTune v1 (1,365).
- **Not on disk:**
  - any GENIE v3 tune. Splines exist on CVMFS for G18_10a_02_11b and AR23_20i; throughput is unmeasured;
  - any reco-level data-driven ("warped") truth, or any pre-registered truth warp;
  - NEUT, which is not openly available.
<!-- absence-ok: 'unmeasured' restates the record's status for GENIE v3 throughput and builds on Perlmutter (state/2d-closeout/stageD-inputs/REPORT.md:287, :377-378; state/inelastic-high-region-20261011/REPORT.md:754); no measurement was found or made by this scoping -->

**Tests (§3), declared before anything is read:**
- per-cell pulls of the bias, and χ² of the bias with the full 16 × 16 matrix, ndf 16. For a vertex-family truth the
  matrix leaves the vertex out;
- for the A7 ensembles, the spread of the nuisance-drawn experiments against C_e.
- **None is a coverage gate** (DECISION-20261024 route item 3). The outcomes that change something are:
  - a stated limitation;
  - the fake-data table as a paper statement;
  - possibly a cell merge.
- **The merge is probably foreclosed (§3.7).** The (e) data central value on R00–R15 has been printed on main since
  PR #340: `cmodel_5d.json` key `x` holds the 16 values, which equal S1's f. H2-level quantities have also been
  computed from (e) data products. So the director's substitute rule for item 2 may no longer admit a merge
  **(inference)**. That needs a ruling (§7, item 1).

**Generator comparisons (§4)** are a separate stage, G, that reads the data result.
- **Predictions:** all five 5D predictions exist on the fine grid, with their finite-MC `sumw2`. Integrating them
  onto the 16 cells costs 0 node-h.
- **GiBUU:** H2's p_∥ edge is 4.5, so A7's p_∥ < 6 domain cannot be reproduced. GiBUU is compared on the eight
  p_∥ < 4.5 cells only.
- **Order:** Stage G runs only after the fake-data stage reports, and only with Joseph's explicit approval to read
  the data.

**Cost (§5):**

| stage | what | cap, CPU node-h | expected |
|---|---|---:|---:|
| **F0** | the re-grade | 0 | 0 |
| **G** | the comparisons | 0 | 0 |
| **F1**, optional | two new GENIE v3 truths: pilot, generation, closures and 2 × 20 pseudo-experiments | **2.1** | 0.80–1.15, plus unmeasured generation overheads |
| **F1-W**, optional | one data-driven truth | 0.75 | about 0.36–0.6 |
<!-- absence-ok: 'unmeasured' restates the record's status for GENIE v3 throughput and builds on Perlmutter (state/2d-closeout/stageD-inputs/REPORT.md:287, :377-378; state/inelastic-high-region-20261011/REPORT.md:754); no measurement was found or made by this scoping -->

- Every job is regular QOS, under 12 h, with no GPU and no premium QOS.
- **Storage:** F0 and G write under 10 MB. F1 writes about 1.1 GB on pscratch, plus an HPSS copy; about 89 GiB of
  HPSS is free. Nothing goes to CFS.

## 1. Inventory of existing fake-data evidence for (e)

`$P` = `/pscratch/sd/j/josephrb`.
- **Estimator R:** OmniFold LightGBM 100/8, 5 iterations, estimator seed 42, `deterministic` with all-row binning;
  negative-weight-refined background, refinement 400/31 at seed + 3. This is configuration (e), as in the product
  meta read 2026-10-25.
- **Half A:** "half MC" means the products unfold with MC half A at weight × 2 and draw pseudo-data from half B
  (`nd-unfolding/s5p_nullexp.py:4-6`, which is `s5n_pseudo.build_pseudo`). The data result unfolds with all of the MC.

| # | item | truth | prior | graded before on | configuration as run | products, sha256 | re-gradable on R00–R15 at 0 node-h? |
|---|---|---|---|---|---|---|---|
| 1 | **Stage 0 / s5e assessment** (`state/s5e/contract-amendment-3-candidate-R-and-assessment.json`, `assessment`) | nominal (40, seeds 800000–800039); W1 NuWro/GENIE E_avail (20, 803000–); W2 GENIE MEC/CV (E_avail, W) (20, 804000–); W3 NuWro/GENIE (p_T, p_∥, E_avail), with 300 empty cells at ratio 1 and 36 clipped (20, 805000–); **q3**, `q3_given_eavail_w` at a = 0.3, a synthetic within-(E_avail, W) tilt that keeps that marginal (`nd-unfolding/s5c_pseudo.py:55-63`) (20, 802000–) | Tune v1 (MC CV) | J and **H2's 27 base cells** (Stage 0 0a and 0b; EW reported) | R, half A, Poisson pseudo-data with background and refinement, no nuisance draws (meta: `no_background` False, refinement ran) | `$P/s5e-20260925/runs/cand/assess/{nominal,W1,W2,W3,q3}/`; per file in `5d-design-20261023/stage0/INVENTORY.sha256` (checked at Stage 0 C1; W1 s803000 `03fc8dc9…` and q3 s802000 `9ad0cdc0…` re-measured equal) | **yes** |
| 2 | **Stage 0c GiBUU** | GiBUU/GENIE E_avail shape, a = 1, the flux-repaired ratio `c001dce8…` (20, 801000–801019) | Tune v1 | J and the 27 base H2 cells; c_F GiBUU **0.259** on H2 (`STAGE0-REPORT.md` §2) | as row 1 | `$P/5d-stage0-20261023/runs/new_gibuu/`; `stage0/receipts-A/products.sha256`. The 20 npz are also tracked in `receipts-A/`. s801000 `dd5805f5…` re-measured equal | **yes**. s5e's 801000–801019 under the superseded ratio (`assess/eavail_gibuu/`, contaminated per `KNOWN_ISSUES` 83) are not proposed |
| 3 | **L-5D-PV closure at NuWro** | `w_truth` × r_NuWro: the full-5D NuWro/GENIE-CV shape, gated, k-normalized, **the same r as the NuWro vertex** (`pv-ladder/DECLARATION.md` §2.2, §3.2) | Tune v1 | the PC on the **27 base cells**: PASS, n 21, corr 0.790, slope 0.683, thin margins. The **16-cell readout is NOT_POWERED** (n 9) (`BUILD-REPORT.md` §3) | (e) with **all** of the MC; noise-free and signal-only. Pseudo-data are the MC's own signal reco rows: no Poisson, no background, **the refinement does not run** (meta: "no negative weights (signal-only reference)") | `$P/pv-ladder-20261024/products/L-5D-PV_e_closure_nuwro.npz` `fff9030e…`; floor `…closure_tune_v1.npz` `eb3e2188…` (both re-measured) | **yes.** The bias on R00–R15 is already printed (`cmodel_5d.json`, `positive_control.reporting16.bias_cells`); no grade against C_total exists |
| 4 | **A7 calibration nulls** (`state/s5p/contract-amendment-7-production-admission.json`; `RECORD-20261005-s5p-joint-5d-inference-result.md`) | MnvTune v1 (1,365, ρ = 1); **GENIE 2.12.10 CV** (1,366); GENIE MEC (1,343); NuWro 21.09 (1,751); GiBUU 2019 (1,351). Each is a hybrid: G's fine-grid shape and rate on the 109 supported J cells, MnvTune v1 elsewhere (`state/s5p/ratios/nullsF/null-*-F.json`, numerators `cfa42210…`, `c179855d…`, `475a2871…`, `48917692…` over `bf7bd278…`) | Tune v1 | J only, through the joint test's T statistic; GiBUU on the 72 J cells with p_∥ < 6. **Never on H2** | R, half A, Poisson with background and refinement, plus **per-experiment nuisance draws** on the pseudo-data source: one flux universe of 100, drawn uniformly; every model band at one universe, **Rvp1pi included**; 4 detector bands at ±1. Lateral and normalization z are recorded only, not applied to `xsec_flat` (`s5p_nullexp.py:13-30`) | `$P/s5p-20260926/runs/prod/cal/<null>/` (counts measured; no `.partial`); every file in `state/s5p/archive/SHA256SUMS-s5p-archive-20261006.txt` (7,176 entries). Two re-measured equal: `4e766288…` (MnvTune s1200000) and `152616be…` (GENIE CV s1220000). HPSS `s5p-archive-20261006.tar`, 2,324,167,680 B (`state/2d-closeout/preservation-20261014/outputs/hsi_ls_lR.txt:204`) | **yes** |
| 5 | **A7 power alternatives** (amendment 7, `power`) | P1r = W3 (NuWro 3D shape), P2r = D5 (NuWro q3 \| (E_avail, W)), P3r = W2 (GENIE MEC (E_avail, W)), each at a = 1. They sit on the MnvTune null (193 / 195 / 195) and on the GENIE CV null (P1g 199, P2g 193, P3g 172) (`state/s5p/ratios/altR/`) | Tune v1 | J only (power, context) | as row 4 | `$P/s5p-20260926/runs/prod/pow/`; 1,147 entries in the same SHA256SUMS | **yes** |
| 6 | other | the s5e development seeds (`runs/cand/dev/k1_R`, `k2`, `k3`, 20 each; `sigma` 100); the Stage 0 vertex products `prior_R5fix_*` (these are real-data unfolds, not fake data); the L-EW / L-3D / L-4D closures (other features or rungs, so not (e) on 5D); the MP-2 full-event reweights (no generator was established: `phase1/mp2/S2-CLOSURE-SUMMARY.md`) | — | — | — | — | **not proposed.** The development seeds repeat rows 1–2 at the same truths, and the others are not (e) fake data on 5D |

**What a re-grade reads, besides the products:**
- the cell definition: `readouts/h2_definition.json` `b6790761…`, fine map `930326a3…`;
- S1's npz `$P/s1-20261024/s1_assembly.npz`, `db000707…` (re-measured), for C_e, its blocks and f;
- C_model,5D: `$P/cmodel5d-20261024/out/cmodel_5d.npz` `3008d8f6…` (re-measured), or S from the committed
  `cmodel_5d.json` `3cfdc6a5…`;
- the integration rule, Σ_f xsec_flat_f · vol_f, from `s1_assembly.json` `meta.integral`. The same rule applies to
  `xtrue_flat`.

**Volume:** about 1.6 GB. That is 1.3 GB of calibration nulls, 207 MB of power alternatives, 40 MB of s5e products
and 4.2 MB of Stage 0c products (`du`). A7's own evaluation read the same calibration products on a login node in
about 2 minutes (`state/s5p/campaign-state.json:527`).

## 2. Circularity

C_model,5D = Σ_k s_k s_kᵀ over three vertices: GENIE+MEC, NuWro and GiBUU, with trace shares 1.4 %, 9.5 % and 89.0 %
(`BUILD-REPORT.md` §4). There is one vertex per generator family, so leaving out a truth's own vertex leaves out its
whole family.

### 2.1 (a) Leave-own-vertex-out C_total

- **Form:**
  - C^(−k) = C_e,rel + Σ_{j≠k} s_j s_jᵀ, with C_e,rel = C_e ⊘ (f fᵀ);
  - in absolute units, C_e + Σ_{j≠k} diag(f) s_j s_jᵀ diag(f).
- **Built from existing products at 0 node-h:**
  - C_e and f come from `s1_assembly.npz`;
  - S comes from `cmodel_5d.npz` (or `.json`).
  - Each C^(−k) is C_e plus a rank-2 term, so it is full rank (C_e has rank 16; `s1_assembly.json` `eigen`).

**Per-cell relative σ on R00–R15:**
- **How it was computed:** from the committed `s1_assembly.json` (C_e relative σ) and `cmodel_5d.json` (S).
- **Check:** the all-vertex column reproduces S1's printed C_total σ to 2.8e-17.
- **No fake-data or data quantity enters.**

| covariance | median | min | max |
|---|---:|---:|---:|
| C_e alone | 6.45 % | 4.05 % | 8.47 % |
| C_total (all three vertices) | 6.74 % | 4.14 % | 13.69 % |
| without GENIE+MEC | 6.74 % | 4.14 % | 13.69 % |
| without NuWro | 6.74 % | 4.09 % | 13.49 % |
| without GiBUU | 6.46 % | 4.11 % | 8.78 % |

**Which covariance grades which truth:**

| truth (row of §1) | generator family | C_model,5D vertex it shares | graded against | in-sample variant |
|---|---|---|---|---|
| W1, W3 (1); A7 NuWro (4); P1r, P1g, P2r, P2g (5); closure at NuWro (3) | NuWro | NuWro: the same prediction `475a2871…`. The closure uses **the vertex's own r** | **C^(−NuWro)** | full C_total, labelled "includes the truth's own vertex: not evidence" |
| W2 (1); A7 GENIE MEC (4); P3r, P3g (5) | GENIE MEC | GENIE+MEC: the same prediction `c179855d…` | **C^(−GENIE+MEC)** | as above |
| Stage 0c GiBUU (2); A7 GiBUU (4) | GiBUU | GiBUU: the same prediction `48917692…` (A7), or its E_avail projection (Stage 0c) | **C^(−GiBUU)** | as above |
| A7 GENIE 2.12.10 CV (4) | none | none. Its prediction `cfa42210…` is the vertices' reference ρ_k = g_k / g_CV, not a vertex | **full C_total** | sensitivity C^(−GENIE+MEC). GENIE CV has no MEC events, and MnvTune v1 carries a tuned MEC, so the truth's departure is partly anti-aligned with the GENIE+MEC vertex **(inference)** |
| q3 tilt (1) | none (synthetic) | none | **full C_total** | sensitivity C^(−NuWro). DESIGN assigns q3 to the NuWro family through D5 (`DESIGN.md:205`, itself an inference). D5 is not a C_model,5D vertex |
| nominal (1); A7 MnvTune v1 (4); closure floor (3) | the prior | none | full C_total | — |

**A second circularity, in C_e.**
- A7's nuisances are drawn from the same weight bank and detector dump as S1's universe unfolds. So a spread test
  (§3.4) is a self-consistency check of how C_e was built, not an independent truth.
- The same holds for any truth made from bank knob universes: it lies inside C_e's interaction block.

### 2.2 (b) Candidate truths outside the vertex set

| candidate | exists? | path / record | cost to produce |
|---|---|---|---|
| **GENIE 2.12.10 CV**, untuned, no MEC | **yes**: A7 null, 1,366 experiments; prediction on the fine grid | row 4; `$P/s5p-20260926/gen5d_fluxfix/genie_cv_xsec5d_full.npz` `cfa42210…` (re-measured) | 0 |
| **q3 \| (E_avail, W) tilt**, synthetic | **yes**: 20 experiments | row 1 | 0 |
| **GENIE knob variations not used as vertices** (beyond ±1σ, or combinations) | **no**. The ±1σ universes exist in the bank, but they make up C_e's interaction block | bank `$P/MINERvA-OmniFold/nd-unfolding/bank_sweep_5d_bkgaware/{tag}_wt.npy` | a truth reweight from bank weights is login-node work. **Not recommended:** it sits inside C_e (§2.1) |
| **Pre-registered truth warps of the current bank** | **no**. Proposed and UNPRICED in the 2D Stage D inputs | `state/2d-closeout/stageD-inputs/REPORT.md:289` ("≈ 1 unfold per case at the measured unit; the design is not frozen") | as F1-W (§5) per warp, plus a frozen design. Same generator family, partial evidence (the same record) |
| **Reco-level data-driven reweight ("warped GENIE")** | **no** | — | §5, F1-W: building the reweight costs ≤ 0.25, then 1 closure and 20 pseudo-experiments. **It reads the data at reco level** (§7, item 4) |
| **GENIE v3**, G18_10a_02_11b or AR23_20i at v3.04.00 on CH | **no events.** The software and splines are on CVMFS. G18_02a_02_11b has no splines | `state/2d-closeout/stageD-inputs/REPORT.md:287`; `state/inelastic-high-region-20261011/REPORT.md:674-675, :754` | §5, F1. Generation is **unmeasured**: an assumed 5–50 ms/event gives 1.5–15 core-h per 1.1M-event configuration, and a 10⁴-event pilot of ≤ 0.2 core-h measures it first. It is also unverified whether the CVMFS v3 builds run here (`stageD-inputs/REPORT.md:377-378`). Then 5D conversion and a fine ratio (login), and the unfolds |
| **NEUT** | **no**: "not openly available" | `3d-unfolding/genie/README.md:234` | — |
| **Other NuWro or GiBUU configurations** | **no**. The existing samples are C12 defaults (`stageD-inputs/REPORT.md:268-269`) | — | generation is documented at 2 min per 100k events for NuWro on a login node (`stageD-inputs/REPORT.md:101`, not a receipt), then as F1. Same family as a vertex, so leave-own-out applies |
| **MP-2 full-event reweights** | built, **not established** for any generator | `phase1/mp2/S2-CLOSURE-SUMMARY.md` | not usable |
<!-- absence-ok: "no" rows rest on the Search line below and on the cluster listing of $P/s5p-20260926/gen5d{,_fluxfix} (login37, 2026-10-25T16:0xZ: genie_cv, genie_mec, nuwro_cv, gibuu_cv, mnvtune_v1 only); 'unmeasured' and 'unverified' restate state/2d-closeout/stageD-inputs/REPORT.md:287, :377-378 -->
Search: warp in *.py, *.json, docs/orchestration/*.md, docs/orchestration/state/**/*.md (excluding the PRD-study literature notes); NEUT|GENIE v3|G18|AR23 in docs/orchestration/*.md and docs/analysis-note/*.tex @ 771dfb39

## 3. Test statistics, declared before anything is read

### 3.1 Common definitions

- **Cells:** R00–R15 in the approved order (fine map `930326a3…`). Cell integrals of `xsec_flat` and `xtrue_flat`
  use S1's rule.
- **Per experiment i at truth T:** r_i = x̂_i / x_true,i − 1, per cell, with each product's own recorded truth.
  Under half A the truth is drawn from half B, so it varies slightly with the split.
- **Bias:** b_T = mean_i r_i, unweighted.
- **Noise:** N_T = Cov_i(r) / B_T. For the closure, b is the noise-free x_closure / x_true − 1 and N = 0.
- **Covariance:** C^(T) is §2.1's leave-own-vertex-out matrix for a vertex-family truth, and the full C_total
  otherwise.
- **The fractional C_e** uses f only to divide. **The tool prints no f and no absolute cell value** (§3.7, §7
  item 6).

### 3.2 S-1, per-cell pulls of the bias

z_T,c = b_T,c / √(C^(T)_cc + N_T,cc). Reported for every truth and cell, with the in-sample variant beside it for
vertex-family truths.

### 3.3 S-2, χ² of the bias with the full matrix

- **Form:** χ²_T = b_Tᵀ (C^(T) + N_T)⁻¹ b_T, with **ndf = 16**.
- **Reference p-value:** P(χ²_16 > χ²_T), reported but **descriptive**. b is a deterministic bias of the estimator
  at T, not a Gaussian draw from C^(T), so the χ²_16 reference describes its size against the reported uncertainty.
  It is not a probability **(inference)**.
- **Multiplicity:** there are 18 truths: rows 1–5, with the superseded GiBUU set excluded. All are reported. No
  family-wise statement is made.
- **The 16-cell χ² of the NuWro closure** uses the 16-cell bias as it stands. The positive control's NOT_POWERED label
  concerns the correlation rule, not this statistic.

### 3.4 S-3, the spread of nuisance-drawn experiments (A7 rows 4–5 only)

- **Form:** d_i = r_i − b_T. The spread of the d_i is compared with C_e′:
  - C_e′ = C_stat + C_flux + Σ the 33 model bands + C_Rvn1pi as a proxy for the Rvp1pi that A7 draws + the 4
    detector bands, all relative;
  - C_Rvn1pi stands in for Rvp1pi because `KNOWN_ISSUES` 92 says the two "encode the same shift";
  - excluded: lateral, normalization and seed, which A7 does not apply to `xsec_flat`.
- **Statistics:**
  - the weighted mean of d_iᵀ C_e′⁻¹ d_i, against 16;
  - the per-cell ratio √(S_cc / C_e′,cc).
  - Each experiment is weighted by the NuE-constraint weight of its drawn flux universe, S1's choice 10 (first 100
    entries of `sorted_NuEConstraint_FHC_RHC_IMD.txt`, `e38ad7d2…`), because A7 draws flux universes uniformly.
- **Known differences, which the readout states:**
  - A7 shifts the pseudo-data source, while S1 shifts the unfolding MC with the data fixed. They agree only to first
    order **(inference)**;
  - half A doubles the MC-statistical part. C_stat is a median 0.24 % of 6.45 % (`s1_assembly.json`), so the effect
    is small **(inference)**;
  - A7 condition 4 notes an MC-size shift of 0.02–0.075 % per cell (`RECORD-20261005-s5p-joint-5d-inference-result.md:74-77`).

### 3.5 Controls (each fails closed, before any statistic is written)

1. Every product and matrix re-hashes to its recorded sha256 (§1).
2. The counts equal the recorded B: 1,365 / 1,366 / 1,343 / 1,751 / 1,351, the power counts of §1, and 20 or 40 per s5e
   truth.
3. C_total rebuilt from S1's blocks reproduces `s1_assembly.json` `relative_sigma.C_total` to 1e-12. The leave-out
   diagonals reproduce §2.1.
4. The closure's 16-cell bias, recomputed from its product, equals `cmodel_5d.json`'s `bias_cells` to 1e-12.
5. The two prior closures and the closure floor are reported first, with no grade. The floor is ≤ 3.2e-5
   (`BUILD-REPORT.md` §3).
6. Every truth integral is positive on all 16 cells.

### 3.6 What each test is for, and the outcomes that would change something

**Not a coverage gate.** DECISION-20261024 item 3 makes validated coverage at held-out truths "not a requirement for
publishing this measurement". None of these truths is held out: rows 1–2 and 4–5 were inspected for Stage 0 and A7.
<!-- absence-ok: restates the route decision's item 3 and §1's "graded before on" column -->

| test | what it is for | the outcome that would change something (thresholds proposed for binding, §7 item 2) |
|---|---|---|
| S-1 / S-2 at a **vertex-family** truth, leave-own-out | does the uncertainty the paper reports, without the truth's own vertex, reach the estimator's bias at a truth like that generator? | **a stated limitation** naming the truths and cells where |z| > 2 or p < 0.01. **The fake-data table** as a paper statement, with Joseph's wording |
| S-1 / S-2 at a **non-vertex** truth (GENIE CV, q3) | the same, for a departure that C_model does not contain: the most informative case | as above |
| in-sample variants | descriptive only | **none.** A pass is not evidence |
| S-3 | does C_e, built from universe unfolds of the data, match the spread that the same nuisances produce through the estimator? | **a stated limitation on C_e** if the weighted mean χ² falls outside [12.8, 19.2], 16 × (1 ± 0.2), or the per-cell ratio exceeds 1.25 in any cell. **Nothing rescales C_e or C_model.** κ = 1 is decided (item 3); any change is Joseph's |
| any | — | **a cell merge**, only if the director rules it admissible (§3.7) |

### 3.7 Has any refined-estimator data central value on the 16 cells been read?

**f in S1's npz.** `s1_assembly.npz` `f` (db000707…) is not printed in any committed S1 file. `s1_assembly.json`
holds per-cell relative σ by component, trace shares and eigenvalue extremes of absolute matrices, but no cell value.
`receipts-S1/logs/G2.log` prints PASS lines only.
Search: `[0-9]e-(3[6-9]|4[0-2])` (cross-section magnitudes) in docs/orchestration/state/measurement-paper/5d-community-20261024/ @ 771dfb39: no hit

**The same 16 numbers are printed elsewhere.**
- **Where:** `nd-unfolding/pv-ladder/readouts/cmodel_5d.json` key `x` holds "P5's integrals on the reporting cells".
- **Why they are the same as f:** S1's gate G2 proved central = P5 bitwise, and S1's C_model check shows f = X_0 to
  10⁻¹² wherever C_model is non-zero (`S1-DECLARATION.md:68, :159-160`).
- **When:** the file was added in `3aadb536` and has been on main since PR #340 (merge `d5617470`,
  2026-10-24T22:02:43Z).
- **Who has looked:** no record says anyone read the values. This session did not print them **(observation of this
  session's own reads)**.

**Other refined-estimator data results on R00–R15 are printed and quoted:**
- the per-vertex data shifts s_k (`BUILD-REPORT.md` §4 table; `cmodel_5d.json` `S`, `shift_cells`);
- the 0.12 % width of the 16-cell integral, computed with x (`BUILD-REPORT.md` §4);
- S1's per-cell relative σ (`S1-REPORT.md`).

The earlier reads on the 27 base cells are disclosed in `DECISION-20261024-joseph-h2-16-cell-definition.md` ("What
led to it").

**No data-against-generator χ² exists on these cells.**
Search: `chi2|χ²|chisq` in nd-unfolding/pv-ladder/, state/measurement-scoping/pv-ladder/, state/measurement-paper/5d-community-20261024/ @ 771dfb39: no hit
- Stage 0's 0b Δχ² compared generator pairs' pseudo-experiment means, not data.
- A7 compared the data with all five predictions on J, and rejected every H0(G).

**What this means for merging.**
- **The two rules:**
  - Route item 2 allows a merge "provided it is declared before any refined-estimator data result is read".
  - The director replaced that clause with: simulation-only quantities, and "the rule is committed before any
    H2-level quantity is computed from an (e) data product in this pipeline" (the H2 decision, "What led to it").
- **What has happened since:** such quantities have been computed. The C_model,5D build ran 2026-10-24T21:44Z, and
  S1's assembly ran 2026-10-25T05:45Z.
- **The reading:** a merge prompted by these fake-data results would be simulation-only, but it would come after
  those computations. So the substitute rule, as written, may not admit it **(inference)**. §7, item 1.

## 4. Generator comparisons: a separate stage, G

**What exists.** Each prediction is on the 65,856-cell grid, with `xsec_flat`, `sumw2_flat` and `nevt_flat`
(headers read 2026-10-25; sha256 re-measured):

| prediction | file (under `$P/s5p-20260926/`) | sha256 | target, notes |
|---|---|---|---|
| GENIE 2.12.10 CV, no MEC | `gen5d_fluxfix/genie_cv_xsec5d_full.npz` | `cfa42210…` | CH; flux-repaired, with the 50–100 GeV supplement |
| GENIE 2.12.10 + Valencia MEC | `gen5d_fluxfix/genie_mec_xsec5d_full.npz` | `c179855d…` | CH |
| NuWro 21.09 | `gen5d_fluxfix/nuwro_cv_xsec5d_full.npz` | `475a2871…` | **C12**, not CH (`stageD-inputs/REPORT.md:268`) |
| GiBUU 2019 | `gen5d_fluxfix/gibuu_cv_xsec5d_fluxfix.npz` | `48917692…` | **C12**; **no events above E_ν = 20 GeV** (`KNOWN_ISSUES` 82) |
| MnvTune v1, the analysis MC | `gen5d/mnvtune_v1_xsec5d.npz` | `bf7bd278…` | **the prior, not an independent generator** (`stageD-inputs/REPORT.md:273-274`) |

- **Integration onto R00–R15** is Σ over the fine map: 0 node-h, login node. Nothing needs truth-only integration
  for these five. A new generator (F1) would need generation and conversion first (§5).
- **Finite MC:** V_g = diag(Σ_f sumw2_f · vol_f²) per cell. This is A7's condition 6 in diagonal form
  (`RECORD-20261005-s5p-joint-5d-inference-result.md:81`).

**Statistics, declared:**
- **Total:** χ²_G = (f − g)ᵀ (C_total + V_g)⁻¹ (f − g), with ndf 16.
- **Shape-only:** the same with a free normalization mode of variance 100, in relative units, added to the
  covariance, as in Stage 0's 0b (`STAGE0-PARTA-DECLARATION.md` §6). ndf 15.
- **Per-cell pulls.**
- **C_total includes all three C_model vertices** for every comparison. This is the measurement's reported total
  (route item 3), and no leave-out applies: the comparison is of the result against a prediction, not of a truth
  against its own vertex.

**GiBUU's domain** (`pv-ladder/H2-DEFINITION-ADDENDUM-GIBUU-DOMAIN.md`).
- **The cells:** H2's p_∥ edge is 4.5 GeV/c. Eight cells, R04–R07 and R12–R15, run from 4.5 to 60 GeV/c. The
  other eight, R00–R03 and R08–R11, are 1.5–4.5.
- **What GiBUU's sample is missing:** its E_ν > 20 GeV share. That is 0.83 % (GENIE CV) and 0.77 % (NuWro) of the
  cross section at 1.5–4.5, but 4.9–5.3 % at 6–10, 43–44 % at 10–20 and all of it at 20–60 (addendum §1).
- **The joint tests' domain:** A7 restricts GiBUU to p_∥ < 6 (`paper_body.tex:245-246`), at a J edge. No H2 edge
  sits at 6, so that domain cannot be reproduced on these cells.
- **Declared:** GiBUU is compared on **the eight p_∥ < 4.5 cells only**, with ndf 8 (7 shape-only). No 16-cell
  GiBUU χ² is computed. Alternatives are for the director (§7, item 5).
- **C_model,5D's GiBUU vertex** stays as built: p_∥ < 10, with its label. The label already names the paper's
  narrower 6.

**Order and approval.**
- **After F0:** Stage G runs only after the fake-data stage reports.
- **With Joseph's approval:** it reads the data result against predictions, which is unblinding. It needs Joseph's
  explicit approval, sought by the director after the F0 report.
- **What it may read until then:** nothing in F0 computes f − g.

## 5. Cost

### 5.1 Measured unit costs

| unit | value | source |
|---|---|---|
| s5e / Stage 0 pseudo-experiment: R, background and refinement, 32 CPUs, 8 lanes per node | 1,608–1,617 s per line of 4, about 404 s each. The node wall was 1,629 s for 8 lanes, so **0.0141 CPU node-h each** at 32 per node **(arithmetic)** | `STAGE0-REPORT.md` §1, job 60182677, 0.45250 node-h |
| A7 nuisance-drawn experiment, 1/8-node lanes | `seconds_unfold` median 545–641 s, max 1,896 (76 products sampled from three nulls); about 720 s mean per experiment on six-seed lines, so **about 0.025 node-h** **(arithmetic)** | product meta; amendment 7 `costs_and_reserves` |
| noise-free closure, one per lane | `closure_nuwro` `seconds_unfold` 732.6 s at 32 threads. J5 ran 5 such steps together in 811 s, so **≤ 0.045 node-h each** packed 5 per node **(arithmetic)** | product meta; `pv-ladder/LEDGER.tsv` (60206336, 0.2253) |
| (e) data-size unfold, 32 CPUs, 8 lanes | 7,129–7,227 s per 11 universes, about 650 s each, so **0.0226 node-h** **(arithmetic)** | `S1-REPORT.md` §3; `s1/LEDGER.tsv` (6.04167 in all) |
| GENIE v3 generation | **unmeasured.** Assumed 5–50 ms/event, 1.5–15 core-h per 1.1M-event configuration | `stageD-inputs/REPORT.md:287` |
<!-- absence-ok: 'unmeasured' restates the record's status for GENIE v3 throughput and builds on Perlmutter (state/2d-closeout/stageD-inputs/REPORT.md:287, :377-378; state/inelastic-high-region-20261011/REPORT.md:754); no measurement was found or made by this scoping -->

### 5.2 Stages and caps (proposed; nothing is authorized)

Every job runs on the regular QOS of m3246, never premium, on exclusive CPU nodes with `--no-requeue`, each under
12 h. Every job is ledgered from `sacct` and stopped past 1.25× its projected wall. No GPU. The caps are the enforced
reservation, nodes × limit.

| stage | what | node-h expected | cap | basis |
|---|---|---:|---:|---|
| **F0** re-grade | rows 1–5: 18 truths, 8,465 products; S-1, S-2, S-3 | 0 | **0** | login node, numpy, about 1.6 GB read (A7's evaluation precedent, §1). New code: one tool and its synthetic tests, then a declaration and a binding |
| **F1a** v3 throughput pilot (optional) | 10⁴ events × 2 configs, and a check that the build runs | ≤ 0.17 **(inference)** | 0.33 (1 node, 0:20) | `stageD-inputs/REPORT.md:287` |
| **F1b** v3 generation (optional, after F1a) | 2 × (1M + 0.1M at 50–100 GeV), then 5D conversion | 0.02–0.23 plus spline-load overhead **(arithmetic** from 3–30 core-h over 128 cores; overhead unmeasured) | 0.75 (1 node, 0:45) | **re-pricing rule:** if F1a's per-event time implies more than 0.45 h on 128 cores, re-price before binding F1b |
| **F1c** v3 fake-data unfolds (optional) | per config: 1 noise-free closure, built as a pv-ladder vertex, and 20 s5e-style pseudo-experiments (`ratio_nd`), packed 8 × 32 | 0.68–0.75 (lanes 0–1: one closure, then 4 pseudo-experiments; lanes 2–7: about 6 pseudo-experiments; about 2,450 s plus load) **(arithmetic)** | 1.0 (1 node, 1:00 ≥ 1.25 × 2,550 s) | units of §5.1 |
| **F1 total** | | **0.80–1.15** plus unmeasured overheads | **2.1** | |
| **F1-W** data-driven truth (optional, alternative or addition) | build the reweight; 1 closure and 20 pseudo-experiments | 0.36–0.6 | 0.75 (0.25 build + 0.5 unfolds) | units of §5.1; the build is unmeasured |
| **G** comparisons | 5 predictions × 16 cells (GiBUU on 8) | 0 | **0** | login node |
<!-- absence-ok: 'unmeasured' restates the record's status for GENIE v3 throughput and builds on Perlmutter (state/2d-closeout/stageD-inputs/REPORT.md:287, :377-378; state/inelastic-high-region-20261011/REPORT.md:754); the F1-W build is this plan's own unpriced step, stated as such -->

**Totals:**
- F0 and G: **0**.
- With F1: cap **2.1**.
- With F1 and F1-W: cap **2.85**.

**Storage:**
- **F0:** a per-truth readout JSON (under 1 MB, committed) and a 16-cell table per experiment (8,465 × 16 × 2,
  about 2 MB) on pscratch.
- **F1:** about 1.1 GB of GENIE v3 gst at the GENIE v2 sample's size per event (999,514,329 B for 2M events,
  `stageD-inputs/REPORT.md:266`; `3d-unfolding/genie/README.md:98-99`) **(inference)**. Plus 2 × 1.6 MB of 5D
  predictions and about 42 × 0.2 MB of products.
- **HPSS:** the F1 copy is about 1.1 GB. 422.78 of 512.00 GiB is used, so about 89 GiB is free (`hpssquota`,
  2026-10-25T16:28Z).
- **pscratch:** 16.99 of 20.00 TiB (84.9 %).
- **CFS:** nothing.

## 6. Risks

- **What a FAIL means under the community-standard route.**
  - A leave-own-out S-1 or S-2 failure is a cell or truth at which the reported uncertainty does not reach the
    estimator's bias.
  - Item 3 makes coverage "not a requirement for publishing", so under the decided route a FAIL is not a gate.
    It becomes a stated limitation and fake-data evidence in the paper, beside the existing label "not a calibrated
    bound" **(reading of item 3)**.
  - **What it would bear on:** whether that limitation is acceptable, or calls for a merge, a restriction or a
    different route. That is Joseph's decision, and this plan draws no conclusion about publishability.
  - **The most informative FAIL** would be at GENIE CV or q3: a bias in a direction that C_model does not contain.
- **An S-3 failure** would mean C_e, as built, misstates the spread its own nuisances produce. That would be a stated
  limitation on C_e. Nothing here rescales.
- **An in-sample pass is not evidence,** because the truth's own vertex is in the matrix. Most of the 18 truths are
  vertex-family truths.
- **These are not held-out truths.** Rows 1–2 and 4–5 were inspected for Stage 0 and A7, so a pass is reported
  information, not a validation.
- **The constructions differ from the data result:**
  - rows 1, 2, 4 and 5 unfold with half the MC;
  - the closure has no background and no refinement;
  - the A7 truths are hybrids, G's shape on the 109 supported J cells only, which do not nest with H2's edges (H2 p_T
    0.7 and p_∥ 4.5 are not J edges);
  - the s5e ensembles have 20 experiments, so N is not negligible there.
- **The A7 spread includes Rvp1pi,** which S1 drops for double counting, and flux universes drawn uniformly.
  §3.4's proxy and weights address both to first order **(inference)**.
- **The merge window may be closed** (§3.7). If a FAIL points to a merge that the rules no longer admit, the
  remaining outcomes are a limitation or a restriction, and those are Joseph's.
- **Unblinding.**
  - **Already printed:** f is in a committed JSON, and A7 already compared the data with the five predictions on J.
  - **What Stage G adds:** the first data-against-generator χ² on these cells.
  - **Why the order is kept:** to protect the fake-data stage from being read with the data in view.
- **Purge.** The oldest access times are 2026-10-21 for the A7 products and 2026-10-08 for the s5e products, so they
  are exposed from about 2026-12-16 and 2026-12-03 **(arithmetic, 8 weeks)**.
  - Both sets are on HPSS: `s5p-archive-20261006.tar`, and Stage 0's Part P tar for the 425 inventory files.
  - The L-5D-PV products and `cmodel_5d.npz` are on pscratch only. They are in the retention item due before
    2026-11-20 (`BUILD-REPORT.md` §6).
- **GENIE v3:**
  - the builds are unverified on Perlmutter;
  - throughput is unmeasured;
  - the configuration is a custodian's choice (`stageD-inputs/REPORT.md:287`, "configuration chosen by the custodian
    (§7)");
  - NuWro and GiBUU are on C12, so a CH comparison carries that difference.
<!-- absence-ok: 'unmeasured' restates the record's status for GENIE v3 throughput and builds on Perlmutter (state/2d-closeout/stageD-inputs/REPORT.md:287, :377-378; state/inelastic-high-region-20261011/REPORT.md:754); no measurement was found or made by this scoping -->

## 7. For the director

1. **Merging.** Under your substitute rule for item 2, may a merge prompted by simulation-only fake-data results still
   be declared, now that H2-level quantities have been computed from (e) data products (§3.7)? If not, the
   cell-merge outcome leaves §3.6.
2. **Thresholds** for the limitation outcome: |z| > 2 or p < 0.01 (S-1, S-2), and S-3's band [12.8, 19.2] with a 1.25
   per-cell ratio. Bind them, replace them, or rule that the readout is descriptive with no threshold.
3. **S-3.** Keep it, given its two proxies (Rvn1pi for Rvp1pi; flux weights), or drop it?
4. **New truths outside the vertex set.**
   - F1, GENIE v3: which configuration? That is a custodian's choice, and I take it to be Joseph's.
   - F1-W: does building a truth from the reco-level data distribution count as reading a data result?
   - Neither is needed for F0.
5. **GiBUU in Stage G:** the eight p_∥ < 4.5 cells, as declared, or all 16 with the deficit stated?
6. **Reading by construction.** F0 divides C_e by f fᵀ to make it fractional and prints no f. Does that count as
   reading? The values are already printed in `cmodel_5d.json`.

## 8. Unchanged

- No compute. No claim, target, endpoint or C_model,5D change.
- No GPU request.
- The S1 covariance and C_model,5D stand as built.
- Joseph's approval is needed for any compute here, and separately for Stage G's read of the data.
