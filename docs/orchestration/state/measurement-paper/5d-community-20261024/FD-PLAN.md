# PLAN FD: the 5D fake-data test and generator comparisons on the 16 H2 cells (2026-10-25)

**By** the measurement session, for the director, under
[`DECISION-20261025-joseph-scope-5d-fake-data-test.md`](../../../DECISION-20261025-joseph-scope-5d-fake-data-test.md)
(PR #350) item 1.
- **Scoping only:** 0 node-h. No job was submitted.
- **Cluster reads:** login37 (via `saul`), 2026-10-25 15:55–17:20 UTC. Only `ls`, `find -printf`, `du`, `sha256sum`,
  npz header and `meta` reads, `myquota` and `hpssquota`. The header reads touched about 100 product files and may
  have refreshed their access times.
- **Repo reads:** main at `771dfb39`, re-checked at `f0b26234`. The two commits between them add decision records
  only.
- **Review:** an independent read-only review found 7 material and 12 minor issues. All are addressed (§9).

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
- any authorization. Any compute needs Joseph's approval, then a declaration and a binding (decision item 3);
- any reading of the data against a generator, which needs Joseph's own approval (decision item 2; §4);
- any claim, printed wording or conclusion about publishability, which are Joseph's.

## 0. Answer

**Five sets of fake-data products for (e) exist, 8,545 of them proposed for use.** Each product stores its unfolded
and its true cross section on the 65,856-cell fine grid (`xsec_flat`, `xtrue_flat`). That rests on about 100 headers
read across every set; F0 checks every file (§3.5) **(inference for the rest)**. So each can be integrated onto
R00–R15 and graded against S1's C_total (`db000707…`) from existing products only, at 0 node-h on a login node (§1).
The sets are:
- the Stage 0 / s5e assessment ensembles: 140 pseudo-experiments at six truths;
- the L-5D-PV noise-free closure at NuWro, with its floor;
- the s5p joint-test (A7) truths in expectation mode (`s3r/f4`, half MC): 80, 16 at each of five generator truths.
  These are **the clean bias at those truths**;
- the A7 calibration ensembles: 7,176, with nuisances drawn per experiment;
- the A7 power ensembles: 1,147 at six alternatives.

None was graded on the 16 cells, or against S1's C_e or C_total. Stage 0 graded on J and the 27 base H2 cells, using
C_stat(e) and (a)'s z-cv; A7 graded on J; the closure was graded on the 27 base cells.

**The A7 nuisance draws shift the ensemble means.**
- A7 draws flux universes uniformly and model-band endpoints with probability ½. S1 instead weights flux by the NuE
  constraint and centres every band on its mean.
- The uniform flux mean is about 5 % off the CV, against about 0.3 % with the weights (§3.1, from S1's own flux
  products).
- So an unweighted A7 mean is not the estimator's bias. The bias at the five A7 truths is taken from the
  nuisance-free `f4` products.
- The power alternatives have no nuisance-free counterpart. They are graded after an offset correction that the
  calibration ensembles measure, and the correction comes with its own control (§3.1).

**Circularity (§2).** Every existing generator-family truth shares its generator with a C_model,5D vertex.
- A7's GENIE MEC, NuWro and GiBUU truths read **the same prediction files** as the vertices (`c179855d…`,
  `475a2871…`, `48917692…`).
- The Stage 0 truths share the family only. They are built from the older 3D samples, which predate the flux fix.
- The leave-own-vertex-out C_total, C_e + Σ_{j≠k} diag(f) s_j s_jᵀ diag(f), can be built at 0 node-h from S1's npz and
  C_model,5D's S.
- **Its median relative σ per cell** is 6.46 % without GiBUU, against 6.74 % with all three vertices. Without NuWro
  or without GENIE+MEC the median stays 6.74 %. The largest cell falls from 13.69 % to 8.78 % without GiBUU
  **(arithmetic, §2.1)**.

**Truths outside the vertex set.**
- **On disk:**
  - A7's **GENIE 2.12.10 CV** truth: 16 nuisance-free experiments and 1,366 calibration experiments. Its prediction
    is the vertices' reference, not a vertex.
  - s5e's synthetic **q3 | (E_avail, W) tilt**: 20 experiments.
- **Not on disk:**
  - any GENIE v3 tune. Splines exist on CVMFS for G18_10a_02_11b and AR23_20i; throughput is unmeasured;
  - any reco-level data-driven ("warped") truth, or any pre-registered truth warp;
  - NEUT, which is not openly available.
- **A limit of every one of these truths:** each is a truth-level reweight of the same MC under the nominal detector
  response. None probes the route decision's first recorded risk, that the detector response may depend on the
  model (§6).
<!-- absence-ok: 'unmeasured' restates the record's status for GENIE v3 throughput and builds on Perlmutter (state/2d-closeout/stageD-inputs/REPORT.md:287, :377-378; state/inelastic-high-region-20261011/REPORT.md:754); no measurement was found or made by this scoping -->

**Tests (§3), declared before anything is read:**
- **Grade:** per-cell pulls of the bias and χ² of the bias against C_total, 16 × 16, ndf 16. For a vertex-family
  truth the matrix leaves the vertex out.
- **Beside it, descriptive:** the same against C_model plus C_stat only. The flux, lateral and normalization parts of
  C_total can hide a bias that C_model misses, and this variant shows it.
- **The spread of the nuisance-drawn A7 experiments against C_e is not proposed.** A7's band draws keep the truth fixed
  and move only the response, while S1's band unfolds also move the prior. So the expected value cannot be fixed
  without a derivation (§3.4).
- **None is a coverage gate** (DECISION-20261024 route item 3). The outcomes that could change something are:
  - a limitation proposed for the paper;
  - the fake-data table as a paper statement, in Joseph's wording;
  - possibly a cell merge.
- **The merge is probably foreclosed (§3.7):**
  - **The data result is on main.** The (e) data central value on R00–R15 has been printed since PR #340
    (`cmodel_5d.json` key `x`, equal to S1's f). 285 (e) data unfolds on the fine grid have been on main since
    PR #348.
  - **The tests are not simulation-only.** They divide by covariances built from data unfolds.
  - **The cells are Joseph's.** R00–R15 is the definition Joseph approved.
  - So a merge needs Joseph, and a ruling (§7, item 1).

**Generator comparisons (§4)** are a separate stage, G, that reads the data result.
- **Predictions:** all five 5D predictions exist on the fine grid, with their finite-MC `sumw2`. Integrating them
  onto the 16 cells costs 0 node-h.
- **GiBUU:** H2's p_∥ edge is 4.5, so A7's p_∥ < 6 domain cannot be reproduced. GiBUU is compared on the eight
  p_∥ < 4.5 cells only.
- **Order:** Stage G runs only after the fake-data stage reports, and only with Joseph's own approval to read the
  data.

**Cost (§5):**

| stage | what | cap, CPU node-h | expected |
|---|---|---:|---:|
| **F0** | the re-grade | 0 | 0 |
| **G** | the comparisons | 0 | 0 |
| **F1**, optional | two new GENIE v3 truths: pilot, generation and prep, closures, 2 × 20 pseudo-experiments | **2.1** | 0.84–1.25, plus unmeasured generation overheads |
| **F1-W**, optional | one data-driven truth | 0.75 | about 0.36–0.6 |
<!-- absence-ok: 'unmeasured' restates the record's status for GENIE v3 throughput and builds on Perlmutter (state/2d-closeout/stageD-inputs/REPORT.md:287, :377-378; state/inelastic-high-region-20261011/REPORT.md:754); no measurement was found or made by this scoping -->

- Every job runs on regular QOS, under 12 h, with no GPU and no premium QOS.
- **Storage:**
  - F0 and G write under 10 MB.
  - F0 first pins and copies the unarchived `f4` products to HPSS: 14.7 MB, 0 node-h.
  - F1 writes about 1.1 GB on pscratch, plus an HPSS copy. About 89 GiB of HPSS is free.
  - Nothing goes to CFS.

## 1. Inventory of existing fake-data evidence for (e)

`$P` = `/pscratch/sd/j/josephrb`.
- **Estimator R:** OmniFold LightGBM 100/8, 5 iterations, estimator seed 42, `deterministic` with all-row binning,
  and negative-weight-refined background with refinement 400/31 at seed + 3. This is configuration (e).
- **How the products label it:** the A7 products record `config` "R". The s5e and Stage 0c products record `config`
  "deterministic" with `code_sha256.candidate` "R" and the 400/31 override. Their estimator and refinement parameters
  as built are S1's. The F0 meta check accepts both labels and compares the parameters.
- **Half A:** "half MC" means the products unfold with MC half A at weight × 2 and draw pseudo-data from half B
  (`nd-unfolding/s5p_nullexp.py:4-6`, which is `s5n_pseudo.build_pseudo`). The data result unfolds with all of the MC.

| # | item | truth | prior | graded before on | configuration as run | products, sha256 | proposed use in F0 |
|---|---|---|---|---|---|---|---|
| 1 | **Stage 0 / s5e assessment** (`state/s5e/contract-amendment-3-candidate-R-and-assessment.json`, `assessment`) | <ul><li>nominal (40, seeds 800000–800039);</li><li>W1, NuWro/GENIE E_avail (20, 803000–);</li><li>W2, GENIE MEC/CV (E_avail, W) (20, 804000–);</li><li>W3, NuWro/GENIE (p_T, p_∥, E_avail), with 300 empty cells at ratio 1 and 36 clipped (20, 805000–);</li><li>**q3**, `q3_given_eavail_w` at a = 0.3: a synthetic within-(E_avail, W) tilt that keeps that marginal (`nd-unfolding/s5c_pseudo.py:55-63`) (20, 802000–).</li></ul> The W ratios come from the 3D-study samples (`3d-unfolding/genie/*_xsec3d.root`, `*_eavailW.root`; `state/s5e/w2-…json`, `w3-…json`, `state/s5n/eavail-ratio-nuwro-over-genie.json`), which predate the flux fix (`KNOWN_ISSUES` 83) | Tune v1 (MC CV) | J and **H2's 27 base cells** (Stage 0 0a and 0b; EW reported) | R, half A; Poisson pseudo-data with background and refinement; no nuisance draws (meta: `no_background` False, refinement ran) | `$P/s5e-20260925/runs/cand/assess/{nominal,W1,W2,W3,q3}/`, 120 files, 22,072,674 B; each in `5d-design-20261023/stage0/INVENTORY.sha256` (checked at Stage 0 C1). W1 s803000 `03fc8dc9…` and q3 s802000 `9ad0cdc0…` re-measured equal | **graded** |
| 2 | **Stage 0c GiBUU** | GiBUU/GENIE E_avail shape at a = 1, ratio `c001dce8…`: GiBUU `gen5d/gibuu_cv_xsec5d.npz` `b183fcca…`, which was not rebuilt, over the repaired GENIE `cfa42210…` (`STAGE0-PARTA-DECLARATION.md` §3). Seeds 801000–801019 | Tune v1 | J and the 27 base H2 cells; c_F GiBUU **0.259** on H2 (`STAGE0-REPORT.md` §2) | as row 1 | `$P/5d-stage0-20261023/runs/new_gibuu/`, 20 files, 3,677,768 B, in `stage0/receipts-A/products.sha256`; also tracked in `receipts-A/`. s801000 `dd5805f5…` re-measured equal | **graded.** s5e's 801000–801019 under the superseded ratio (`assess/eavail_gibuu/`, contaminated per `KNOWN_ISSUES` 83) are not used |
| 3 | **L-5D-PV closure at NuWro** | `w_truth` × r_NuWro: the full-5D NuWro/GENIE-CV shape, gated and k-normalized. It is **the same r as the NuWro vertex** (`pv-ladder/DECLARATION.md` §2.2, §3.2) | Tune v1 | the PC on the **27 base cells**: PASS, n 21, corr 0.790, slope 0.683, with thin margins. The **16-cell readout is NOT_POWERED** (n 9). The leave-own-vertex-out C_model reach is 17 of 21 PC cells (`BUILD-REPORT.md` §3) | (e) with **all** of the MC; noise-free and signal-only. The pseudo-data are the MC's own signal reco rows: no Poisson, no background, and **the refinement does not run** (meta: "no negative weights (signal-only reference)") | `$P/pv-ladder-20261024/products/L-5D-PV_e_closure_nuwro.npz` `fff9030e…`; floor `…closure_tune_v1.npz` `eb3e2188…` (both re-measured) | **graded.** Its 16-cell bias is already printed (`cmodel_5d.json`, `positive_control.reporting16.bias_cells`); no grade against C_total exists. The floor is a control |
| 4 | **A7 truths, expectation mode** (`state/s5p/s3r-f4-tasks.tsv`; the D pairs of A7 condition 4) | the five A7 truths of row 5, with the same hypothesis files (meta `hypothesis.sha256` `ceea00e7`, `8c37f545`, `9033c952`, `9297a698`, `0080495c`) | Tune v1 | used for the MC-size shift D, never graded as bias | R, half A; **expectation**, so no Poisson and no nuisance draws (meta `development` {expectation: true, mc_fraction: half}). 16 split seeds 970000–970015 per truth | `$P/s5p-20260926/runs/s3r/f4/<truth>_half/`, 80 files, 14,738,583 B. **No per-file sha256 is recorded, and the files are not on HPSS**: F0 step 0 pins and archives them | **graded: the bias at the five A7 truths.** The `_quarter` set (80) measures MC size and is not used |
| 5 | **A7 calibration truths** (`state/s5p/contract-amendment-7-production-admission.json`; `RECORD-20261005-s5p-joint-5d-inference-result.md`) | MnvTune v1 (1,365, ρ = 1); **GENIE 2.12.10 CV** (1,366); GENIE MEC (1,343); NuWro 21.09 (1,751); GiBUU 2019 (1,351). Each is a hybrid: G's fine-grid shape and rate on all 109 supported J cells, p_∥ ≥ 6 included, and MnvTune v1 elsewhere (`state/s5p/ratios/nullsF/null-*-F.json`, numerators `cfa42210…`, `c179855d…`, `475a2871…`, `48917692…`, over `bf7bd278…`) | Tune v1 | J only, through the joint test's T statistic; GiBUU on the 72 J cells with p_∥ < 6. **Never on H2** | R, half A; Poisson with background and refinement, plus **nuisance draws** on the pseudo-data source: one flux universe of 100, uniform; every model band at one universe, **Rvp1pi included**, with the truth kept fixed in every fine cell; 4 detector bands at ±1. Lateral and normalization z are recorded but not applied to `xsec_flat` (`s5p_nullexp.py:13-30`) | `$P/s5p-20260926/runs/prod/cal/<truth>/`; every file in `state/s5p/archive/SHA256SUMS-s5p-archive-20261006.txt` (7,176 entries). Two re-measured equal: `4e766288…` (MnvTune s1200000) and `152616be…` (GENIE CV s1220000). HPSS `s5p-archive-20261006.tar`, 2,324,167,680 B (`state/2d-closeout/preservation-20261014/outputs/hsi_ls_lR.txt:204`) | **the offset control only** (§3.1). Not graded as bias |
| 6 | **A7 power alternatives** (amendment 7, `power`) | P1r = W3 (the NuWro 3D shape), P2r = D5 (NuWro q3 \| (E_avail, W)), P3r = W2 (the GENIE MEC (E_avail, W) shape), each at a = 1 and rebuilt from the repaired predictions. They sit on the MnvTune truth (193 / 195 / 195) and on the GENIE CV truth (P1g 199, P2g 193, P3g 172) (`state/s5p/ratios/altR/`) | Tune v1 | J only (power, context) | as row 5 | `$P/s5p-20260926/runs/prod/pow/`; 1,147 entries in the same SHA256SUMS | **graded after the offset correction** (§3.1), or descriptive if its control fails |
| 7 | other (A7 subsets listed by the review, then re-counted) | <ul><li>A7 lost-seed reruns, `recovery/recovery/{cal,pow}` (224, 53), plus `recovery/determinism`;</li><li>Stage 2 numerics `runs/s2/num/{c1,c2,c3,c4,nom,gibuu}` (160, 100, 40, 41, 101, 101);</li><li>the `s3v`/`s3r` pilots;</li><li>s5e `assess/a3` (4) and `dev/{k1_R,k1_B0,k2,k3,k4,sigma}`;</li><li>the Stage 0 vertex products `prior_R5fix_*`, which are real-data unfolds;</li><li>the L-EW / L-3D / L-4D closures;</li><li>the MP-2 full-event reweights (`phase1/mp2/S2-CLOSURE-SUMMARY.md`: no generator was established).</li></ul> | — | — | — | — | **not used.** <ul><li>The recovery set is report-only (`RECORD-20261006-s5p-lost-seed-recovery-resolution.md`), and rows 5–6 use the recorded B.</li><li>c1–c4, nom and gibuu are numerics studies: replicas of one draw, or nominal ensembles that rows 1 and 4 already cover.</li><li>Pilots and development runs repeat the same truths.</li><li>k1_B0 is not (e).</li><li>`prior_R5fix_*` are data, not fake data.</li><li>The other rungs are not (e) on 5D, and MP-2 is not established.</li></ul> |

**What a re-grade reads, besides the products:**
- the cell definition: `readouts/h2_definition.json` `b6790761…`, fine map `930326a3…`;
- S1's npz `$P/s1-20261024/s1_assembly.npz`, `db000707…` (re-measured), for C_e, its blocks and f;
- C_model,5D from `$P/cmodel5d-20261024/out/cmodel_5d.npz` `3008d8f6…` (re-measured), or S from the committed
  `cmodel_5d.json` `3cfdc6a5…`;
- the integration rule, Σ_f xsec_flat_f · vol_f, from `s1_assembly.json` `meta.integral`, applied to `xtrue_flat` as
  well;
- for the offset control, the NuE-constraint weights of S1's choice 10: the first 100 entries of
  `sorted_NuEConstraint_FHC_RHC_IMD.txt`, `e38ad7d2…`.

**Volume:** about 1.6 GB, mostly row 5's 1.3 GB and row 6's 207 MB. A7's own evaluation read the row 5 products on a
login node in about 2 minutes (`state/s5p/campaign-state.json:527`).

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
- **Check:** the all-vertex row reproduces S1's printed C_total σ to 2.8e-17.
- **No fake-data or data quantity enters.**

| covariance | median | min | max |
|---|---:|---:|---:|
| C_e alone | 6.45 % | 4.05 % | 8.47 % |
| C_total (all three vertices) | 6.74 % | 4.14 % | 13.69 % |
| without GENIE+MEC | 6.74 % | 4.14 % | 13.69 % |
| without NuWro | 6.74 % | 4.09 % | 13.49 % |
| without GiBUU | 6.46 % | 4.11 % | 8.78 % |

**Which covariance grades which truth:**

| truth (row of §1) | family | how it relates to the C_model,5D vertex | graded against | in-sample variant |
|---|---|---|---|---|
| W1, W3 (1); A7 NuWro (4); P1r, P1g, P2r, P2g (6); closure at NuWro (3) | NuWro | A7 and the power alternatives read **the vertex's prediction** `475a2871…`. The closure uses **the vertex's own r**. W1 and W3 share the family only (3D-study samples) | **C^(−NuWro)** | full C_total, labelled "includes the truth's own vertex: not evidence" |
| W2 (1); A7 GENIE MEC (4); P3r, P3g (6) | GENIE MEC | A7 and P3 read the vertex's prediction `c179855d…`. W2 shares the family only | **C^(−GENIE+MEC)** | as above |
| Stage 0c GiBUU (2); A7 GiBUU (4) | GiBUU | A7 reads the vertex's prediction `48917692…`. Stage 0c uses the unrebuilt `b183fcca…`, projected onto E_avail | **C^(−GiBUU)** | as above |
| A7 GENIE 2.12.10 CV (4) | none | its prediction `cfa42210…` is the vertices' reference in ρ_k = g_k / g_CV, not a vertex | **full C_total** | sensitivity C^(−GENIE+MEC). GENIE CV has no MEC events, and MnvTune v1 carries a tuned MEC, so the truth's departure is partly anti-aligned with the GENIE+MEC vertex **(inference)** |
| q3 tilt (1) | none (synthetic) | none | **full C_total** | sensitivity C^(−NuWro). DESIGN assigns q3 to the NuWro family through D5 (`DESIGN.md:205`, itself an inference). D5 is not a C_model,5D vertex |
| nominal (1); A7 MnvTune v1 (4) | the prior | none | **full C_total** | — |

**A second circularity, in C_e.**
- A7's nuisances come from the same weight bank and detector dump as S1's universe unfolds.
- Any truth built from bank knob universes lies inside C_e's interaction block.

### 2.2 (b) Candidate truths outside the vertex set

| candidate | exists? | path / record | cost to produce |
|---|---|---|---|
| **GENIE 2.12.10 CV**, untuned, no MEC | **yes**: 16 expectation-mode and 1,366 calibration experiments; prediction on the fine grid | rows 4–5; `$P/s5p-20260926/gen5d_fluxfix/genie_cv_xsec5d_full.npz` `cfa42210…` (re-measured) | 0 |
| **q3 \| (E_avail, W) tilt**, synthetic | **yes**: 20 experiments | row 1 | 0 |
| **GENIE knob variations not used as vertices** (beyond ±1σ, or combinations) | **no**. The ±1σ universes are in the bank, and they make up C_e's interaction block | bank `$P/MINERvA-OmniFold/nd-unfolding/bank_sweep_5d_bkgaware/{tag}_wt.npy` | a truth reweight from bank weights is login-node work. **Not recommended:** it sits inside C_e |
| **Pre-registered truth warps of the current bank** | **no**. They were proposed and left UNPRICED in the 2D Stage D inputs | `state/2d-closeout/stageD-inputs/REPORT.md:289` ("≈ 1 unfold per case at the measured unit; the design is not frozen") | as F1-W (§5) per warp, plus a frozen design. Same generator family, so partial evidence (the same record) |
| **Reco-level data-driven reweight ("warped GENIE")** | **no** | — | §5, F1-W: a reweight build capped at ≤ 0.25, then 1 closure and 20 pseudo-experiments. **It reads the data at reco level** (§7, item 4) |
| **GENIE v3**, G18_10a_02_11b or AR23_20i at v3.04.00 on CH | **no events.** The software and splines are on CVMFS. G18_02a_02_11b has no splines | `state/2d-closeout/stageD-inputs/REPORT.md:287`; `state/inelastic-high-region-20261011/REPORT.md:674-675, :754` | §5, F1. **Generation is unmeasured.** At an assumed 5–50 ms/event, a 1.1M-event configuration takes 1.5–15 core-h; a 10⁴-event pilot of ≤ 0.2 core-h measures it first. Whether the CVMFS v3 builds run here is unverified (`stageD-inputs/REPORT.md:377-378`). Then come 5D conversion, a fine ratio and the unfolds. **The chooser rule:** whoever chooses its configuration, seeds and amplitude "must not be a lane that tunes the recipe", and "the outcome stays uninspected until the recipe is frozen" (`stageD-inputs/REPORT.md:297`) |
| **NEUT** | **no**: "not openly available" | `3d-unfolding/genie/README.md:234` | — |
| **Other NuWro or GiBUU configurations** | **no**. The existing samples are C12 defaults (`stageD-inputs/REPORT.md:268-269`) | — | NuWro generation is documented at 2 min per 100k events on a login node (`stageD-inputs/REPORT.md:101`; not a receipt), then as F1. Same family as a vertex, so leave-own-out applies |
| **MP-2 full-event reweights** | built, **not established** for any generator | `phase1/mp2/S2-CLOSURE-SUMMARY.md` | not usable |
<!-- absence-ok: "no" rows rest on the Search line below and on the cluster listing of $P/s5p-20260926/gen5d{,_fluxfix} (login37, 2026-10-25T16:0xZ: genie_cv, genie_mec, nuwro_cv, gibuu_cv, mnvtune_v1 only); 'unmeasured' and 'unverified' restate state/2d-closeout/stageD-inputs/REPORT.md:287, :377-378 -->
Search: warp in *.py, *.json, docs/orchestration/*.md, docs/orchestration/state/**/*.md (excluding the PRD-study literature notes); NEUT|GENIE v3|G18|AR23 in docs/orchestration/*.md and docs/analysis-note/*.tex @ 771dfb39

## 3. Test statistics, declared before anything is read

### 3.1 Common definitions, and where the bias comes from

- **Cells:** R00–R15 in the approved order (fine map `930326a3…`). Cell integrals of `xsec_flat` and `xtrue_flat`
  use S1's rule.
- **Per experiment i at truth T:** r_i = x̂_i / x_true,i − 1 per cell, each with its product's own recorded truth.
  Under half A the truth comes from half B, so it varies slightly with the split.
- **Bias b_T:**
  - **rows 1, 2 and 4:** b_T = mean_i r_i, unweighted. These have no nuisance draws;
  - **row 3:** the noise-free x_closure / x_true − 1, with N = 0;
  - **row 6:** first-order offset-corrected, b_T = b̃_T − O_null (below).
- **Noise:** N_T = Cov_i(r) / B_T, with the effective size B_eff = (Σw)² / Σw² wherever weights enter.

**Why the A7 calibration means are not used as bias.**
- A7 draws one flux universe of 100, uniformly, and scales only the pseudo-data source's reco weights; the truth stays
  fixed (`s5p_nullexp.py:13-14`).
- S1 weights its flux block by the NuE constraint (choice 10). Over S1's own 100 flux unfolds, the recorded
  `flux_ratio_mean` averages 1.0489 uniformly and 0.9997 with the weights. `denom_over_cv_total` averages 1.0514 and
  0.9974 (product meta; review measurement, 2026-10-25).
- Each model band is drawn at either endpoint with probability ½, so its mean is the endpoints' midpoint. S1
  mean-centres the bands, so those offsets are not in C_e either.
- **So an unweighted A7 mean carries an offset of order several percent that is not estimator bias (inference).**

**The offset correction for row 6, and its control.**
- **The offset:** for each A7 truth G, O_G = b̃_G − b_G. Here b̃_G is the NuE-weighted mean of row 5 at G, and b_G is
  the nuisance-free bias from row 4.
- **The control:** the offset should not depend on the truth, to first order **(inference)**. Each pair O_G, O_G′
  must agree within 3 σ per cell, with σ from both ensembles' B_eff. If they do, row 6 uses
  b_T = b̃_T − O_MnvTune for P1r, P2r and P3r, and b̃_T − O_GENIE CV for P1g, P2g and P3g.
- **If the control fails,** row 6 is reported descriptive and ungraded, and the failure is reported.
- **Expected size:** B_eff is about 37 for a power set of 195 and about 260 for a calibration truth. That follows
  from the flux weights' n_eff of 19.06 out of 100 (`s1_assembly.json` `meta.flux_weights`) **(arithmetic, if
  uniform draws)**.

- **Covariance:** C^(T) is §2.1's leave-own-vertex-out matrix for a vertex-family truth, and the full C_total
  otherwise.
- **The fractional C_e** uses f only as a divisor. **The tool prints no f and no absolute cell value** (§7, item 6).

### 3.2 S-1, per-cell pulls of the bias

- **Grade:** z_T,c = b_T,c / √(C^(T)_cc + N_T,cc), for every truth and cell. For vertex-family truths, the
  in-sample variant is reported beside it.
- **Descriptive variant, the "model-only reach":** z^m_T,c = b_T,c / √(C^m(T)_cc + N_T,cc), with
  C^m(T) = C_stat,rel + Σ_{j ≠ own(T)} s_j s_jᵀ. The sum runs over all three vertices for a non-vertex truth.
  - **Why:** C_e's median 6.45 % is mostly flux (3.55 %), lateral (2.38 %) and normalization (1.4 %)
    (`s1_assembly.json`). Those parts can hide a bias that C_model misses.
  - **The precedent:** BUILD-REPORT's leave-out reach of 17 of 21 on the 27 base cells is the same idea, in cell
    counts.

### 3.3 S-2, χ² of the bias with the full matrix

- **Form:** χ²_T = b_Tᵀ (C^(T) + N_T)⁻¹ b_T, with **ndf = 16**. The model-only variant χ²^m_T uses C^m(T), which
  is full rank because C_stat is (inference, checked in control 3).
- **Reference p-value:** P(χ²_16 > χ²_T), reported but **descriptive**. b is a deterministic bias of the estimator
  at T, not a Gaussian draw from C^(T), so the χ²_16 reference describes its size against the reported uncertainty.
  It is not a probability **(inference)**.
- **Multiplicity:** there are 18 graded truths: 5 in row 1, 1 in row 2, 1 in row 3, 5 in row 4 and 6 in row 6. All
  are reported, with no family-wise statement.
- **GiBUU-family truths are graded on all 16 cells.** The truth is self-consistent: the unfold is graded against the
  truth it was given. A7's GiBUU truth carries GiBUU's E_ν < 20 GeV sample on all 109 J cells, so on R04–R07 and
  R12–R15 it is a less physical truth. The eight p_∥ < 4.5 cells are reported beside the 16, with ndf 8.
- **The 16-cell χ² of the NuWro closure** uses the 16-cell bias as it stands. The positive control's NOT_POWERED label
  concerns its correlation rule, not this statistic.

### 3.4 Not proposed: the spread of the nuisance-drawn experiments against C_e

- **What it would have tested:** whether C_e, built from universe unfolds of the data, matches the spread that the
  same nuisances produce through the estimator.
- **Why it is not proposed:**
  - A7's model-band draws keep the truth fixed in every fine cell and move only the response
    (`s5p_nullexp.py:15-24`). S1's band unfolds reweight the whole unfolding MC, prior included. So the A7 spread
    lacks the prior-dependence part of the interaction block by construction.
  - The flux mechanics also differ: A7 rescales the pseudo-data reco weights, while S1 unfolds the data with the
    universe's flux and denominator.
  - An expected value for the statistic would need a derivation first.
- **Not a reason:** Rvp1pi. A7 draws it beside Rvn1pi. `KNOWN_ISSUES` 92 finds the two bands' weights byte-identical,
  and `docs/analysis-note/sec_systematics.tex:232` says they "encode the same shift". So Rvn1pi's block would proxy it
  exactly to first order.
- **If the director wants it:** it needs a declared expected value before binding. §7, item 3.

### 3.5 Controls (each fails closed, before any statistic is written)

0. **Pin row 4.** F0 hashes the 80 `f4` half files into a committed list and copies them to HPSS before reading any
   cell value.
1. Every other product and matrix re-hashes to its recorded sha256 (§1).
2. **Meta:**
   - every product carries `xsec_flat` and `xtrue_flat` of length 65,856;
   - its estimator and refinement parameters equal S1's (100/8, 400/31, all-row binning, deterministic, seed 42);
   - its truth's hypothesis or ratio sha256 is the one §1 lists;
   - rows 4–6 record `config` "R", and rows 1–2 record "deterministic" with candidate "R".
3. **Counts:**
   - row 5: 1,365 / 1,366 / 1,343 / 1,751 / 1,351;
   - row 6: §1's counts;
   - row 4: 16 per truth;
   - row 1: 20 or 40 per truth.
4. **Matrices:**
   - C_total rebuilt from S1's blocks reproduces `s1_assembly.json` `relative_sigma.C_total` to 1e-12;
   - the leave-out diagonals reproduce §2.1;
   - C_stat,rel is checked to be full rank.
5. The closure's 16-cell bias, recomputed from its product, equals `cmodel_5d.json`'s `bias_cells` to 1e-12.
6. The closure floor (row 3) is reported first as a control and is not graded. It must be ≤ 3.2e-5
   (`BUILD-REPORT.md` §3).
7. The offset control of §3.1 runs before any row 6 grade.
8. Every truth integral is positive on all 16 cells.

### 3.6 What each test is for, and the outcomes that would change something

**Not a coverage gate.**
- **The decision:** DECISION-20261024 item 3 makes validated coverage at held-out truths "not a requirement for
  publishing this measurement".
- **No held-out truth exists here:** rows 1, 2, 4, 5 and 6 were inspected for Stage 0 or A7.
<!-- absence-ok: restates the route decision's item 3 and §1's "graded before on" column -->

| test | what it is for | the outcome that would change something (thresholds proposed for binding, §7 item 2) |
|---|---|---|
| S-1 / S-2 at a **vertex-family** truth, leave-own-out | does the uncertainty the paper reports, without the truth's own vertex, reach the estimator's bias at a truth like that generator? | **a limitation proposed to Joseph** naming the truths and cells with \|z\| > 2 or p < 0.01. **The fake-data table** as a paper statement, if Joseph wants it, in Joseph's wording |
| S-1 / S-2 at a **non-vertex** truth (GENIE CV, q3) | the same, for a departure that C_model does not contain: the most informative case | as above |
| the model-only variants | how much of C_total's reach comes from C_model | descriptive. They inform the limitation's wording, which is Joseph's |
| in-sample variants | descriptive only | **none.** A pass is not evidence |
| any | — | **a cell merge**, only with Joseph's decision, after a ruling on admissibility (§3.7) |

**Nothing here rescales C_e or C_model.** κ = 1 is decided (item 3), and any change is Joseph's.

### 3.7 Has any refined-estimator data central value on the 16 cells been read?

**f in S1's npz.**
- `s1_assembly.npz` `f` (db000707…) is not printed in any committed S1 file.
- `s1_assembly.json` holds per-cell relative σ by component, trace shares and eigenvalue extremes of absolute
  matrices, but no cell value.
- `receipts-S1/logs/G2.log` prints PASS lines only.
Search: `[0-9]e-(3[6-9]|4[0-2])` (cross-section magnitudes) in docs/orchestration/state/measurement-paper/5d-community-20261024/ @ 771dfb39: no hit outside .npz files

**f is derivable from committed files, and the same 16 numbers are printed elsewhere.**
- **`x` in `cmodel_5d.json`.** `nd-unfolding/pv-ladder/readouts/cmodel_5d.json` key `x` holds "P5's integrals on the
  reporting cells".
  - **Why they equal f:** S1's G2 proved central = `data_R` = P5 bitwise (`S1-REPORT.md:24`), and S1's C_model check
    shows f = X_0 to 10⁻¹² wherever C_model is non-zero (`S1-DECLARATION.md:68, :159-160`).
  - **Since when:** added in `3aadb536`, and on main since PR #340 (merge `d5617470`, 2026-10-24T22:02:43Z).
- **285 (e) data unfolds on the fine grid.** They have been on main since PR #348 (`4c7d705a`), in
  `s1/readout/s1_assembly/`: the `S1_*` universe unfolds, `data_b1…b20_j…`, `S1seed*` and `lat_*`. Each has a
  65,856-cell `xsec_flat` of the real data. The bootstrap means alone give f to about σ_stat/√20 **(inference)**.
- **The central value itself** is s5e's `assess/data/data_R.npz` from September, the same bytes. Its values on other
  cell sets were read in s5e and s5p.
- **Who has looked:** no record says anyone read the 16 values. This session did not print them **(observation of this
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
- **Why a merge would not be simulation-only:** the S-1 and S-2 grades divide by C_e, which is built from (e) data
  universe unfolds, by the data shifts s_k, and by f. A merge prompted by them would rest on data-derived
  quantities, after those computations. So the substitute rule, as written, does not appear to admit it
  **(inference)**.
- **Whose decision:** R00–R15 is the definition Joseph approved (H2 decision, item 1). Changing it is Joseph's
  decision, whatever the admissibility ruling.
- **Cost, if a merge were made:** S1's assembly and the C_model,5D build would be redone on the merged cells from
  existing products, on a login node at 0 node-h **(inference)**. The code and its review would be new. §7, item 1.

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

- **Integration onto R00–R15** sums over the fine map, at 0 node-h on a login node. None of these five needs
  truth-only integration. A new generator (F1) would need generation and conversion first (§5).
- **Finite MC:** V_g = diag(Σ_f sumw2_f · vol_f²) per cell. This is A7's condition 6 in diagonal form
  (`RECORD-20261005-s5p-joint-5d-inference-result.md:81`).

**Statistics, declared:**
- **Total:** χ²_G = (f − g)ᵀ (C_total + V_g)⁻¹ (f − g), with ndf 16.
- **Shape-only:** the same, with a free normalization mode of variance 100 in relative units added to the covariance,
  as in Stage 0's 0b (`STAGE0-PARTA-DECLARATION.md` §6). ndf 15.
- **Per-cell pulls.**
- **C_total includes all three C_model vertices** for every comparison. That is the measurement's reported total
  (route item 3). No leave-out applies: the comparison is of the result against a prediction, not of a truth against
  its own vertex.

**GiBUU's domain** (`pv-ladder/H2-DEFINITION-ADDENDUM-GIBUU-DOMAIN.md`).
- **The cells:** H2's p_∥ edge is 4.5 GeV/c. Eight cells, R04–R07 and R12–R15, run from 4.5 to 60 GeV/c; the other
  eight, R00–R03 and R08–R11, span 1.5–4.5.
- **What GiBUU's sample is missing** is its E_ν > 20 GeV share. That is 0.83 % (GENIE CV) and 0.77 % (NuWro) of the
  cross section at 1.5–4.5, but 4.9–5.3 % at 6–10, 43–44 % at 10–20 and all of it at 20–60 (addendum §1).
- **The joint tests' domain:** A7 restricts GiBUU to p_∥ < 6 (`paper_body.tex:245-246`), at a J edge. No H2 edge
  sits at 6, so that domain cannot be reproduced on these cells.
- **Declared:** GiBUU is compared on **the eight p_∥ < 4.5 cells only**, with ndf 8 (7 shape-only). No 16-cell GiBUU
  χ² is computed. The alternatives are for the director (§7, item 5).
- **C_model,5D's GiBUU vertex** stays as built: applied below p_∥ = 10, with its label, which already names the
  paper's narrower 6.

**Order and approval.**
- **After F0:** Stage G runs only after the fake-data stage reports.
- **With Joseph's approval:** it reads the data result against predictions, which is unblinding, so it needs
  Joseph's own approval after the F0 report (decision item 2).
- **What F0 computes:** nothing in F0 computes f − g.

## 5. Cost

### 5.1 Measured unit costs

| unit | value | source |
|---|---|---|
| s5e / Stage 0 pseudo-experiment: R, background and refinement, 32 CPUs, 8 lanes per node | 1,608–1,617 s per line of 4, about 404 s each. The node wall was 1,629 s for 8 lanes, so **0.0141 CPU node-h each** at 32 per node **(arithmetic)** | `STAGE0-REPORT.md` §1, job 60182677, 0.45250 node-h |
| A7 nuisance-drawn experiment, 1/8-node lanes | `seconds_unfold` median 545–641 s, max 1,896 (76 products sampled from three truths); about 720 s mean per experiment on six-seed lines, so **about 0.025 node-h** **(arithmetic)** | product meta; amendment 7 `costs_and_reserves` |
| noise-free closure, one per lane | `closure_nuwro` `seconds_unfold` 732.6 s at 32 threads. J5 ran 5 steps together in 811 s, so **about 0.045 node-h each** (0.0451) packed 5 per node **(arithmetic)** | product meta; `pv-ladder/LEDGER.tsv` (60206336, 0.2253) |
| ratio prep for the ladder's vertices | 318 s, 0.0883 node-h (debug QOS) | `pv-ladder/LEDGER.tsv` (60201984) |
| (e) data-size unfold, 32 CPUs, 8 lanes | 7,129–7,227 s per 11 universes, about 650 s each, so **0.0226 node-h** **(arithmetic)** | `S1-REPORT.md` §3; `s1/LEDGER.tsv` (6.04167 in all) |
| GENIE v3 generation | **unmeasured.** Assumed 5–50 ms/event, so 1.5–15 core-h per 1.1M-event configuration | `stageD-inputs/REPORT.md:287` |
<!-- absence-ok: 'unmeasured' restates the record's status for GENIE v3 throughput and builds on Perlmutter (state/2d-closeout/stageD-inputs/REPORT.md:287, :377-378; state/inelastic-high-region-20261011/REPORT.md:754); no measurement was found or made by this scoping -->

### 5.2 Stages and caps (proposed; nothing is authorized)

**Rules for every job:**
- regular QOS of m3246, never premium; the ladder's prep used debug QOS, and F1 puts its prep in a regular job;
- exclusive CPU nodes, `--no-requeue`, each under 12 h, no GPU;
- ledgered from `sacct`, and stopped past 1.25× its projected wall.
- **Caps** are the enforced reservation: nodes × limit.

| stage | what | node-h expected | cap | basis |
|---|---|---:|---:|---|
| **F0** re-grade | rows 1–4 and 6 graded: 18 truths and 8,545 products, row 5 for the offset control; S-1, S-2 and their variants | 0 | **0** | login node, numpy, about 1.6 GB read (A7's evaluation precedent, §1). New code: one tool with synthetic tests, then a declaration and a binding |
| **F1a** v3 throughput pilot (optional) | 10⁴ events × 2 configurations, and a check that the build runs | 0.05–0.17 **(inference)** | 0.33 (1 node, 0:20) | `stageD-inputs/REPORT.md:287` |
| **F1b** v3 generation and prep (optional, after F1a) | 2 × (1M + 0.1M at 50–100 GeV), 5D conversion, and the gated fine ratios as the ladder's prep built them | 0.02–0.24 for generation (3.1–30.6 core-h over 128 cores) plus about 0.09 prep: **0.11–0.33**, plus spline-load overhead, unmeasured **(arithmetic)** | 0.75 (1 node, 0:45) | **re-pricing rule:** if F1a's per-event time implies more than 0.45 h on 128 cores, re-price before binding F1b |
| **F1c** v3 fake-data unfolds (optional) | per configuration, 1 noise-free closure built as a pv-ladder vertex and 20 s5e-style pseudo-experiments (`ratio_nd`), packed 8 × 32 | 0.68–0.75. Lanes 0–1 run one closure, then 4 pseudo-experiments; lanes 2–7 run about 6 pseudo-experiments; about 2,450 s plus load **(arithmetic)** | 1.0 (1 node, 1:00 ≥ 1.25 × 2,550 s) | units of §5.1 |
| **F1 total** | | **0.84–1.25**, plus unmeasured overheads | **2.1** (2.08) | |
| **F1-W** data-driven truth (optional, instead of or with F1) | build the reweight, then 1 closure and 20 pseudo-experiments | 0.36–0.6 | 0.75 (0.25 build + 0.5 unfolds) | units of §5.1; the build is unmeasured |
| **G** comparisons | 5 predictions × 16 cells (GiBUU on 8) | 0 | **0** | login node |
<!-- absence-ok: 'unmeasured' restates the record's status for GENIE v3 throughput and builds on Perlmutter (state/2d-closeout/stageD-inputs/REPORT.md:287, :377-378; state/inelastic-high-region-20261011/REPORT.md:754); the F1-W build is this plan's own unpriced step, stated as such -->

**Totals:** F0 and G **0**; with F1, a cap of **2.1**; with F1 and F1-W, **2.85**.

**Storage:**
- **F0:**
  - a per-truth readout JSON, under 1 MB, committed;
  - a 16-cell table per experiment (8,545 × 16 × 2, about 2 MB) on pscratch;
  - the row 4 pin and its HPSS copy, 14.7 MB.
- **F1:**
  - about 1.1 GB of GENIE v3 gst, at the GENIE v2 sample's size per event (999,514,329 B for 2M events;
    `stageD-inputs/REPORT.md:266`; `3d-unfolding/genie/README.md:98-99`) **(inference)**;
  - 2 × 1.6 MB of 5D predictions;
  - about 42 × 0.2 MB of products.
- **HPSS:** the F1 copy is about 1.1 GB. 422.78 of 512.00 GiB is used, so about 89 GiB is free (`hpssquota`,
  2026-10-25T16:28Z).
- **pscratch:** 16.99 of 20.00 TiB (84.9 %).
- **CFS:** nothing.

## 6. Risks

- **What a FAIL would mean under the community-standard route:**
  - A leave-own-out S-1 or S-2 failure is a cell or truth where the reported uncertainty does not reach the
    estimator's bias.
  - Item 3 makes coverage "not a requirement for publishing", so under the decided route a FAIL is not a gate. It
    would be put to Joseph as a proposed limitation and as fake-data evidence, beside the existing label "not a
    calibrated bound" **(reading of item 3)**.
  - Whether the limitation is acceptable, or calls for a merge, a restriction or a different route, is Joseph's call.
    This plan draws no conclusion about publishability.
  - **The most informative FAIL** would be at GENIE CV or q3: a bias in a direction that C_model does not contain.
- **A PASS can be cheap.** C_total's flux, lateral and normalization parts can make |z| < 2 for a bias that C_model
  misses. The model-only variants show how much of the reach is C_model's (§3.2).
- **The detector response is not probed.**
  - Every truth here is a truth-level reweight of the same MC under the nominal response.
  - An independent generator with MINERvA's response is UNAVAILABLE (`stageD-inputs/REPORT.md:68`).
  - So F0, F1 and F1-W cannot test the route decision's first recorded risk, "the detector response may depend on the
    model in ways the five scalars do not capture" (`DECISION-20261024-joseph-5d-community-standard-route.md:76-77`).
    A pass says nothing about it.
- **An in-sample pass is not evidence,** because the truth's own vertex is in the matrix. Most of the 18 truths are
  vertex-family truths.
- **These are not held-out truths.** Every row was inspected for Stage 0 or A7, so a pass is reported information,
  not a validation.
- **The constructions differ from the data result:**
  - rows 1, 2, 4, 5 and 6 unfold with half the MC;
  - the closure has no background and no refinement;
  - the A7 truths are hybrids: G's shape on the 109 supported J cells, which do not nest with H2's edges. H2's p_T 0.7
    and p_∥ 4.5 are not J edges;
  - the s5e ensembles have 20 experiments, and row 4 has 16 split seeds, so N is not negligible there.
- **Row 6 rests on a first-order offset correction** (§3.1). If its control fails, row 6 is descriptive only.
- **The merge window appears closed,** and the cells are Joseph's (§3.7). If a FAIL points to a merge, the decision
  is Joseph's.
- **Unblinding:**
  - f is already printed in a committed JSON and derivable from 285 committed data unfolds;
  - A7 already compared the data with the five predictions on J;
  - Stage G would add the first data-against-generator χ² on these cells;
  - the order protects the fake-data stage from being read with the data in view.
- **Purge.** Pscratch files are exposed 8 weeks after their last access **(arithmetic)**:

  | products | oldest access, measured 2026-10-25 | exposed from | HPSS copy |
  |---|---|---|---|
  | A7 rows 5–6 | 2026-10-21 | about 2026-12-16 | yes, `s5p-archive-20261006.tar` |
  | proposed s5e products | 2026-10-24 | about 2026-12-19 | yes, Stage 0's Part P tar |
  | row 4 (`f4`) | 2026-10-08 | about 2026-12-03 | **no**, hence control 0 |
  | L-5D-PV products and `cmodel_5d.npz` | — | — | **no**; they are in the retention item due before 2026-11-20 (`BUILD-REPORT.md` §6) |

  Reads refresh access times, this plan's included.
- **GENIE v3:**
  - the builds are unverified on Perlmutter, and throughput is unmeasured;
  - its configuration, seeds and amplitude go to a chooser who must not tune the recipe, and the outcome stays
    uninspected (`stageD-inputs/REPORT.md:287, :297`);
  - NuWro and GiBUU are on C12, so a CH comparison carries that difference.
<!-- absence-ok: 'unmeasured' restates the record's status for GENIE v3 throughput and builds on Perlmutter (state/2d-closeout/stageD-inputs/REPORT.md:287, :377-378; state/inelastic-high-region-20261011/REPORT.md:754); no measurement was found or made by this scoping -->

## 7. For the director

1. **Merging.**
   - The S-1 and S-2 grades rest on data-derived covariances, and H2-level quantities have been computed from (e)
     data products (§3.7). Does your substitute rule for item 2 still admit any merge?
   - If it does, I take the merge itself to be Joseph's decision, because R00–R15 is the definition Joseph approved. If it
     does not, the cell-merge outcome leaves §3.6.
2. **Thresholds** for proposing a limitation: |z| > 2 or p < 0.01, against the leave-own-out C_total.
   - Bind them, or replace them.
   - Or rule that the readout is descriptive with no threshold.
   - Also say whether the model-only variant should carry the threshold instead.
3. **S-3**, the spread test, is not proposed (§3.4). Keep it out, or ask for a derivation of its expected value
   first?
4. **New truths outside the vertex set.**
   - **F1, GENIE v3:** which configuration, and who chooses? The chooser must not tune the recipe
     (`stageD-inputs/REPORT.md:297`). I take this to be Joseph's choice.
   - **F1-W:** does building a truth from the reco-level data distribution count as reading a data result?
   - Neither is needed for F0.
5. **GiBUU in Stage G:** the eight p_∥ < 4.5 cells, as declared, or all 16 with the deficit stated?
6. **Reading by construction.** F0 uses f only to make C_e fractional, and prints no f. Does that count as reading,
   given that the values are already printed in `cmodel_5d.json`?

## 8. Unchanged

- No compute. No claim, target, endpoint or C_model,5D change.
- No GPU request.
- The S1 covariance and C_model,5D stand as built.
- Joseph's approval is needed for any compute here, and separately for Stage G's read of the data.

## 9. Review dispositions

An independent read-only review (2026-10-25) checked every number, sha256, count and citation against the repo and
the cluster. It re-measured 14 sha256s, the counts, the leave-out σ table and the unit-cost arithmetic. Everything
not listed below was confirmed.

**MATERIAL, all accepted:**

| # | the finding | what changed |
|---|---|---|
| M1 | unweighted A7 means carry nuisance offsets (flux about +5 %, band midpoints) | the bias at the A7 truths now comes from the nuisance-free `f4` products (row 4). Row 6 is offset-corrected with a control (§3.1) |
| M2 | S-3 was centred wrongly, and A7's band draws are response-only | S-3 is withdrawn (§3.4) |
| M3 | the merge sentence contradicted §3.7, and the cells are Joseph's | §3.7 and §7 item 1 rewritten; the merge cost added |
| M4 | the 285 committed data unfolds and the data_R lineage were missing | added to §3.7 |
| M5 | existing ensembles were missing | rows 4 and 7 added, with uses and reasons |
| M6 | the detector-response risk was missing | added to §0 and §6 |
| M7 | grading against C_total alone can hide what C_model misses | the model-only variants added (§3.2–3.3); §7 item 2 |

**MINOR, all accepted:**
1. W1–W3 share the family, not the prediction file.
2. Stage 0c's numerator is `b183fcca…`.
3. The prior closures are graded; the floor is a control.
4. The Rvp1pi source is `sec_systematics.tex:232`, and KI 92 makes the proxy exact.
5. The s5e products' `config` label.
6. The product sizes.
7. The purge dates by set.
8. Rounding: 0.0451, and 30.6 core-h; F1a now has a lower bound, so F1 is 0.84–1.25.
9. The prep step and the chooser rule.
10. `xtrue_flat` is labelled an inference, with a control, and "never graded against an (e) covariance" is narrowed.
11. GiBUU-family fake-data truths are graded on all 16 cells, with the eight-cell variant beside.
12. Wording: "a limitation proposed to Joseph", and C_e′ removed with S-3.
