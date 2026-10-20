# MP-5 preparation: the truth muon-angle axis (a) and the generator W convention (b), read out like MP3-A

**By** the measurement session, 2026-10-19. **Status: PREPARED, NOT RUN.** No batch job has been submitted. The job
runs on the director's GO. **Spec:** `BINDING-PHASE1-ADDENDUM-1.md` §3 (origin/main `b8207c7a`), the M4-W record
(`2d-closeout/stageF/methods/M4-W-RECORD.md`, origin/main), and the director's MP-5(a) amendment, sent by message and to
be added to the record. **Tree:** branch `measurement-paper/phase1-20261019` at `a30a1292`. Code is in
`measurement-paper/phase1/mp5/`, staged read-only at `/pscratch/sd/j/josephrb/measurement-paper/phase1/mp5/{code,inputs}`.
Descriptive throughout, with no gate. Results will appear in `REPORT-draft.md`.

## 1. Estimands and exact formulas

Fine grid: 14×16×7×7×6 (pT, p∥, E_avail, q3, W). The 109 J cells are `s5p_stage1_inspect.coarse_map(J_EDGES, supported)`
with `supported` from `s5c/contract.json`. U and μ_G = `s5p_joint.prediction` are as in MP3-A.

**(a) Analysis truth content about each axis**, per analysis-MC truth event e (MnvTune v1 `w_truth`; MeV; the MAT
semantics are cited in §3):
- l = `mc_primFSLepton[0:3]`, E_l = `mc_primFSLepton[3]`, E_ν = `mc_incomingE`, k = `mc_incomingPartVec[0:3]`.
- θ_b = Theta(RotateX(−0.05887)·l) = atan2(√(x²+y²), z): the analysis convention.
- θ_ν = atan2(|l×k|, l·k): the generators' convention.
- For θ ∈ {θ_b, θ_ν}:
  - pT = |l|/1000·sin θ and p∥ = |l|/1000·cos θ.
  - W = √(M² + 2M(E_ν−E_l) − 4E_νE_l sin²(θ/2))/1000, where M = M_n, M_p or (1.5M_n+M_p)/2.5 by `mc_targetNucleon`. W is NaN when W² < 0.
  - E_avail and q3 are the stored truth values; they do not depend on the axis.
- The gate is `collect_truth_denom_nd`'s: all five values finite, 0 ≤ w < 1e4, and `in_truth_phase_space(pT, p∥)` (pT ∈ [0, 4.5], p∥ ∈ [1.5, 60], θ < 20°).
  - The gate is applied separately for each axis.
  - The weight is w = `w_truth`·pot_scale.
- T_axis(f) = Σ_e w over the gated events, binned with `np.histogramdd`. T_axis(c) is the sum over the fine cells f in cell c.
- **R_c = T_beam(c) / T_ν(c).** Both T are recomputed from the MAD branches by the same code, so they differ only in the axis.
  - The flux is constant in pT (`of_inputs_5d.flux` = 6.2433e-4 in all 14 bins), so the ratio of contents is the ratio of cross sections.
  - R_stored uses the stored truth for T_beam and is reported beside R_c.
- MC error: sd(R_c) = √(Σ_out w² + Σ_in w²)/T_ν(c). It runs over the events whose J cell differs between the two axes.
- **Proxy:** Δ_c = μ_G(c)·(R_c − 1) for G ∈ {GENIE CV, GENIE MEC, NuWro 21.09, GiBUU 2019}.
- MnvTune v1: Δ = 0 by construction (§3).

**(a) GENIE CV check.** μ_G,beam = U·x_beam. x_beam is the frozen GENIE CV chain (< 50 GeV main plus 50–100 GeV
supplement) with each event's lepton rotated into the beam frame:
- p_beam = R(n_e)·p_gst, where R(n) is the rotation by α = atan2(√(n_x²+n_y²), n_z) about u = (−n_y, n_x, 0)/√(n_x²+n_y²). This maps ẑ onto n (Rodrigues formula; p is unchanged when n = ẑ).
- n_e is drawn from the analysis MC's ν direction in the MAT frame, n = RotateX(−0.05887)·k̂, within the event's E_ν bin (§2).
- pT, p∥, the phase-space decision and W change with the rotation. W = `gen_to_xsec_eavailW.w_true(ν, (E_l, p_beam))` keeps the generator's fixed M = 0.939565 and W = 0 when W² ≤ 0.
- E_avail, q3, r(E), A, B, S_50_100 and N_pop are unchanged.
- **Criterion (descriptive):** d_c = (μ_G,beam(c) − μ_G(c)R_c)/σ_c(a). If |d_c| > 0.2 in any cell, the proxy is labelled **UNRELIABLE** for GENIE MEC, NuWro and GiBUU.
  - The readout of the GENIE-native Δ = μ_G,beam − μ_G is reported beside it.
  - d_c is also given in units of its own MC noise, √(Var_GENIE migration + μ_G² sd(R_c)²).

**(b) W convention.** Δ_c = μ_G(c)·s_c for GENIE CV and NuWro. s_c is the record's own per-cell shift,
`m4-w/probe_gen.json` → `<gen>/per_cell_rel_weighted` (μ_c(analysis W)/μ_c(fixed M_n) − 1, flux-fix weighted, 109 cells).
- **Checked now (local, sha256 `ce4d7a7d…`, = MANIFEST):** the per-cell values reproduce the record's own summaries exactly.
  - GENIE CV: median |s| 0.13192%, max 1.5721% (J240), 66 cells > 1e-3.
  - NuWro: median 0.087268%, max 2.1933% (J91), 51 cells > 1e-3.
  - The per-cell Δ is carried, so the producer is not re-run. The eval re-asserts this match.
- Assumption (stated, not tested): s_c is measured on the < 50 GeV sample. It is applied to the full product, supplement included.

**Readout, for every Δ** (MP3-A §3.3, §4.1; `s5p_joint`/`s5p_inference` frozen copies):
- **Δ_c/σ_c** in three readings:
  - (a) SD (ddof 1) of the J-cell result over G's frozen null ensemble (`s5p_joint.ensemble`). PRIMARY.
  - (b) √diag W.
  - (c) SD of the null residual f − (μ + ε).
- **ΔᵀW⁻¹Δ** = `stat_total(μ+Δ, μ, W⁻¹)`, with the frozen W = V + diag Var μ_G on the test domain. PRIMARY. GiBUU uses the 72 cells with p∥ < 6.
- The shape form at the data's Jacobian, (Δq)ᵀVs⁻¹(Δq).
- The null T at c = 0: median, 95th percentile and SD, recomputed and checked against `joint-evaluate.json`.
- DESCRIPTIVE only, not a re-grade: the observed T with μ_G → μ_G + Δ, and its change in null-SD units.

**Proxy assumption (to be stated in the report).** The beam-axis vs ν-axis migration is a kinematic smearing of the muon
direction by about 1 mrad, the event-by-event ν direction spread, and is nearly independent of the interaction model. So a
ratio measured on Tune v1 (GENIE 2.12.6 + MnvTune v1) transfers to other generators' predictions. The GENIE CV check
tests this for one model only.

## 2. Declaration (fixed before the run)

`measurement-paper/phase1/mp5/mp5_declaration.json`, **sha256 `3806fc58282f04ed29681bbc8ede148d5f5efb347764619c4b2696ca5a941a99`**.
The job refuses (exit 4) if the staged copy differs.
- **Seed:** `numpy.random.default_rng(520261019)`, one stream.
  - First u_main = `rng.random(N_main)`: one draw per entry of the < 50 GeV GENIE CV gst, in entry order, CC or not.
  - Then u_supp = `rng.random(N_supp)` for the 50–100 GeV supplement.
- **E_ν bins (GeV):** [0, 3), [3, 5), [5, 8), [8, 15), [15, 30), [30, ∞). The GENIE event uses gst `Ev`; the pool event uses `mc_incomingE`/1000.
- **Pool:** every G2 FPS `mc_truth_denom` row (ν_μ CC, tracker fiducial, any muon angle, finite w in [0, 1e4)), joined to its MAD Truth entry.
  - Pool order: playlists 1A…1P, rows in tree order.
  - Draw: k = `searchsorted(cumsum(w_b)/Σw_b, u, 'right')`. This is a `w_truth`-weighted draw from the bin's empirical (n_x, n_y, n_z).
- **Rotation:** as in §1. The twist about n has no physical effect, because GENIE's lepton azimuth about ν is uniform.

## 3. Population, join, and the MnvTune claim (code verified at `a30a1292`)

**MnvTune v1's Δ is zero by construction: verified from code.** The chain:
1. The prediction is `s5p_mc_truth_pred.py` (sha256 `e4518d0a…` = the product's `meta.code_sha256`). At :38-56 it is `extract_cross_section_nd(unf, unf/denom_nd, flux, POT, N, edges)` on `of_inputs_5d.npz` (`07fccc1a…`). That is xs = denom_nd·1e4/(flux·N·POT·vol) wherever unf > 0 (`xsec_nd.py:54-83`), so the prediction is the truth denominator itself.
2. denom_nd is the `histogramdd` of `mc_truth_denom` (MC, MC_pz, MC_eavail, MC_q3, MC_W) at w_truth·pot_scale (`nn_dump_inputs.py:78-90`), gated at `unfold_nd_omnifold_unbinned.py:333-337`.
3. Those branches are `GetMuonPTTrue/PzTrue` and `GetTrueExperimentersW` (`runEventLoopOmniFold.cpp:587-595`). These are |l|·sin/cos(GetThetalepTrue) (`CVUniverse.h:71-79`) and the θ-dependent W (`CVUniverse.h:396-410`).
4. `GetThetalepTrue` = RotateX(−0.05887) l, Theta (MAT `TruthFunctions.h:21-27`, `PlotUtilsPhysicalConstants.h:44`, sha256 `e6df3503…`/`386979d5…` on the cluster MAT-MINERvA `50d76314`).

So the MnvTune v1 prediction uses the analysis (beam-axis) convention, and Δ_MnvTune ≡ 0. Control T3 checks this from the bytes.

**The generators' θ is about their ν axis:**
- GENIE: `pt = hypot(pxl, pyl)`, `pz = pzl` (`gen_to_xsec5d.py:146-147`). The job asserts pxv = pyv = 0 for every entry.
- NuWro: `nuwro_to_flat_5d.C:59-60`.
- GiBUU: `gen_to_xsec5d.py:282`.

**Population.**
- The 5D analysis omnifile's `mc_truth_denom` (32,849,103 rows) has no identity.
- The G2 FPS production (`g2_fullevent/final/runEventLoopOmniFold_G2_FPS_<pl>.root`, `MNV101_FULL_PHASE_SPACE` + `MNV101_DUMP_POINTCLOUD`) writes the same rows plus the out-of-phase-space ones. It also writes `mc_run/mc_subrun/mc_nthEvtInFile` and the MAT-frame muon.
- Rows are joined by `event_identity.pack_identity` to the MasterAnaDev `Truth` entries of the G2 receipts' MC manifests (488 files, 11.8 TB; read via a 60 MB/file branch subset).
- The FPS rows give the ν-axis inflow across the phase-space edge.
- Four G2 playlists (1D, 1E, 1F, 1P) have recovery receipts, valid only for builders that enforce their retained domain. Those rows enter only through the same gates. T1 is the binding evidence for the analysis rows.

**Measured during prep (login node, small reads):**
- **Alignment probe.** The first 200,000 5D rows equal the G2 1A rows restricted to the kinematic phase space, **bitwise in all six columns** (MC, MC_pz, MC_eavail, MC_q3, MC_W, w_truth).
  - G2 `mu_true_*` = the MAT-frame muon: |pT − 1000·MC| ≤ 9e-13 MeV.
- **Join smoke test (P1).** One 1L MAD file (run 113000, 533,702 Truth entries, 135,274 after the loose prefilter, read in 7.2 s): all 95,256 G2 rows matched, with unique keys.
  - mu_true vs RotateX(l): ≤ 1.5e-11 MeV.
  - Recomputed beam-axis pT, p∥, W and q3 equal the stored truth **bitwise** (max |Δ| = 0), with the same NaN-W pattern.
  - α(ν vs MAT axis): median 1.04 mrad, 68% [0.51, 1.95] (M4-W: 1.03, [0.51, 1.92]).
- **GENIE path smoke test (P2).** On the 50–100 GeV supplement gst, the rotation code path with n = ẑ reproduces `extract_genie`'s arrays bitwise (pt, pz, E_avail, q3, W, is_mec). ν is along +z.
- **Eval smoke test.** `mp5_eval.py` was run end to end on a synthetic design (local, scratchpad) with all four nulls and the GiBUU domain.

## 4. Controls (evaluated first; a failure stops the job and nothing after it is read)

| id | step | control | stop rule |
|---|---|---|---|
| T0 | tune | sha256 of the 5D omnifile (`b6d2651c…`, M4-W), `of_inputs_5d.npz` (`07fccc1a…`), `mnvtune_v1_xsec5d.npz` (`bf7bd278…`). G2 ROOTs and manifests are compared with their receipts (reported) | binding three mismatch |
| T1 | tune | the G2 rows in the kinematic phase space, per playlist, concatenated in a discovered playlist order, equal **all** 32,849,103 5D `mc_truth_denom` rows **bitwise** | any row differs |
| T2 | tune | every G2 row joins to exactly one MAD Truth entry. MAD duplicate keys keep the first occurrence, and differing duplicate content is counted. mu_true = RotateX(l) to ≤ 1e-6 MeV | any unmatched row |
| **T3** | tune | **the beam-axis truth content of the analysis MC reproduces the MnvTune v1 frozen prediction:** T_beam(stored) = `denom_nd` (max rel ≤ 1e-12, bitwise expected). The restated s5p_mc_truth_pred extraction with the frozen denom_nd reproduces `mnvtune_v1_xsec5d.npz` bitwise, and with T_beam to ≤ 1e-12. The eval adds the J level: U·x(T_beam) vs `s5p_joint.prediction(MnvTune)` | fail → STOP |
| T4 | tune | the recomputed beam-axis pT, p∥ and W reproduce the stored truth (≤ 1e-9 GeV, same NaN pattern). J-cell T_beam(rec) vs T_beam(stored) ≤ 1e-6 relative | fail → STOP |
| **G1** | genie | **the GENIE CV rebuild through the rotation path with n = ẑ (θ about the ν axis) reproduces `extract_genie`'s event arrays and the frozen `genie_cv_xsec5d.npz` and `genie_cv_xsec5d_full.npz` bitwise (xsec and sumw2)**, before the rotated build is computed | fail → STOP |
| E1 | eval | per null, T_obs, null medians and SDs, B and k at c = 0 against `joint-evaluate.json` (bitwise flag reported; k and B exact, ≤ 1e-9 rel) | fail → STOP |
| E2 | eval | U·x_unrot = μ_G(CV). The record's s_c reproduce its own summaries. The record's cells = the contract's | reported |

## 5. Flagged choices (computed both ways where it costs nothing)

1. R_c uses recomputed T for both axes (T4 shows the recompute is the stored truth). R_stored is beside it.
2. The ν-axis W keeps the analysis M and NaN rule, so (a) isolates the axis. The beam-axis GENIE W keeps the generator's fixed M and its W = 0 clamp, so the check does not mix in (b).
3. The pool uses all fiducial CC events, not only the signal phase space. The ν direction is a property of the flux and vertex. The α summary is also given on the signal gate.
4. The pool uses w_truth weights. Ties in w are irrelevant to the draw.
5. GiBUU is read out on its declared domain (72 cells). The other generators use 109 cells.
6. σ_c uses ddof 1. The null-T SD uses ddof 0, as `s5p_joint.py:246`.

## 6. Staged copies (`/pscratch/sd/j/josephrb/measurement-paper/phase1/mp5/`, read back with `sha256sum` after transfer; dirs made read-only)

| staged | sha256 | source |
|---|---|---|
| code/mp5_tune.py | `8ab4504377093046a223441da1b5f732f7f40f766121731c16a21901eaf5c396` | measurement-paper/phase1/mp5/ |
| code/mp5_genie.py | `371e03b3d6c9020330178ad852ecb7b77cba849c29a826b473881ef6e53cd274` | measurement-paper/phase1/mp5/ |
| code/mp5_eval.py | `f991073b1a52fb15b9d89340b2099f1287ef2758c061db9f9c154347b4e75548` | measurement-paper/phase1/mp5/ |
| code/mp5_job.sh | `bb4a5d16c37e76609a0fc47a94dc3dfc43fc49a0fcb62ed22a60970ab1336d1d` | measurement-paper/phase1/mp5/ |
| code/mp5_declaration.json | `3806fc58282f04ed29681bbc8ede148d5f5efb347764619c4b2696ca5a941a99` | measurement-paper/phase1/mp5/ |
| code/gen5d_flux_reweight.py | `89863318015d27f0e19513a8156cd04de26f593f00a89dd3c013045ad9106fc5` | 3d-unfolding/genie/ (= the product build's copy, = MP3-A) |
| code/gen5d_flux_supplement.py | `ff7a2d0e0013533a7fa6b76a7a71f2bc55dabd60b7bb43dc37402e34feceae61` | 3d-unfolding/genie/ (= MP3-A) |
| code/s5p_joint.py | `2cd98235a4ad1c544cad7b3340b4b385c0904236351a04dc53d3f3c22e308bf9` | nd-unfolding/ (`git diff 4f5a613f HEAD` empty) |
| code/s5p_inference.py | `55239135b2a729cca478b661f59ad9ca00deccf27f96d9bac5974616280cf62c` | nd-unfolding/ (idem) |
| code/s5p_stage1_inspect.py | `26569afc0da46f21167e0908014712cd800c1e14ac63a4b245a0b493c76d3d71` | nd-unfolding/ (idem) |
| code/xsec_nd.py | `454001f3c9ac3aa6485d184aadb8aba65dd71dba124816962b9c3b6344920fa5` | nd-unfolding/ (last changed `21f2a003`, 2026-06-03) |
| code/event_identity.py | `b921abf0f2a940e70d2ea27968701b83908af03fc889d550b1c741c88f9d8c31` | nd-unfolding/pet/ |
| inputs/design.json | `404446eb2a770dc4412012c5e182e57a77afa2edd332c75de399a9281f536285` | state/s5p/prod/design.json |
| inputs/s5c_contract.json | `d54fd7c9641901736e58430e666db1ee782a54d9c95bf4439541872567c39c93` | state/s5c/contract.json |
| inputs/joint-evaluate.json | `b9604502b1aa263508ba46f0be91846d7a2106f6f2fd0ba5c172b87ee256dd11` | state/s5p/stage7/joint/joint-evaluate.json |
| inputs/m4w_probe_gen.json | `ce4d7a7d2a6c6e65439700e9773f7a18e788aaad813b1a029d01be1f4588e080` | origin/main `…/methods/m4-w/probe_gen.json` (= its MANIFEST) |

`gen_to_xsec5d.py` is imported from the frozen export `s5p-20260926/gen5d/code/tree` via `gfr.load_g5`, as in MP3-A.
Every step prints and records `module.__file__` and the module's sha256. A login-node import check printed all five
modules from `mp5/code/`.

## 7. Submission (on GO)

```
ssh saul.nersc.gov 'cd /pscratch/sd/j/josephrb/measurement-paper/phase1/mp5 && sbatch code/mp5_job.sh'
```
`-A m3246 -C cpu -q shared -c 32 -t 01:30:00`, one job with three steps:
1. `python3 code/mp5_tune.py out/tune run/pool 32 inputs/s5c_contract.json`
2. `python3 code/mp5_genie.py out/genie run/pool code/mp5_declaration.json inputs/s5c_contract.json`
3. `python3 code/mp5_eval.py --design inputs/design.json --s5c-contract inputs/s5c_contract.json --v …/stage3/V/V-s3v.npz --frozen-eval inputs/joint-evaluate.json --tune out/tune/mp5_tune.npz --genie out/genie/mp5_genie.npz --m4w-gen inputs/m4w_probe_gen.json --declaration code/mp5_declaration.json --out out/eval`

The environment is `root_6_28`, OMP/OPENBLAS = 4 (as frozen), no `set -u`. Writes go only under `mp5/`. The pool
(about 1.6 GB of `.npy`) stays in `run/pool` and is not fetched. Afterwards: `sacct -X -P -j <id> -o
JobID,State,ExitCode,ElapsedRaw,AllocTRES,QOS,Account`. Fetch `out/` and the log, then compare sha256 on both sides.

## 8. Estimated charge

The estimate is built from these measured rates:
- One MAD file reads in 7.2 s single-process. 488 files over 32 workers take about 3–6 min with I/O contention.
- G2 and 5D reads take about 3 min.
- Hashing 119 GB in parallel takes about 1–2 min.
- `of_inputs_5d` and the histograms take about 3 min.
- The GENIE builds (×2 plus the reference) take about 5 min.
- The eval of 4 nulls (about 5,800 calibration products) takes about 3 min.

Expected wall time is about 25–35 min at billing 32: **≈ 0.05–0.08 CPU node-h** (= ElapsedRaw × 32/256/3600). The
ceiling at the 1:30 limit is 0.19 node-h, under the 1 node-h expectation and the phase-1 grant. No GPU.

## 9. Prep actions on the cluster (all read-only on inputs)

- **Login-node reads:** tree schemas of three omnifiles; 200k-row alignment probe; Truth-tree branch metadata of one MAD file; G2 receipts; smoke tests P1 and P2 (16.6 s, 0.7 GB RSS).
- **Writes:** only under `mp5/prep/` and `mp5/{code,inputs,logs}`.
- **Correction.** The first three probe scripts were briefly written to `phase1/receipts/` and moved to `mp5/prep/` within minutes. `receipts/` now holds only its original file.
- **Jobs.** The six pending `sf1-*` jobs of the methods lane (m3246, e.g. `60017066`–`60017074`) were seen and not touched. No sbatch/srun/salloc.

## 10. UNCONFIRMED before the run

- Whether T1 holds for all 32.8M rows. The 200k-row probe holds; the playlist order of the merged file is discovered, not assumed.
- Whether NuWro's and GiBUU's frozen statistics reproduce bitwise in this env. MP3-A showed it for CV and MEC.
- The R_c proxy for MEC, NuWro and GiBUU rests on the stated assumption, checked on GENIE CV only.
- (b) carries the record's < 50 GeV shift onto the supplement-inclusive product.

## 11. Amendment at GO (2026-10-19, before submission of 60017887)

The coordinator's GO set a new rule: if E1 fails for NuWro or GiBUU, report the generators whose frozen statistic
reproduces and STOP only the others. The staged `mp5_eval.py` stopped every readout on any E1 failure, so it was
changed to stop per null. **The new sha256 is `08a0bc4c2846373441c96e29a3bfcb1d8339b4ce5459d3827038911cd48120b3`**
(it was `f991073b…`).

What changed:
- A null failing E1 is removed and listed in `E1_stopped_nulls`.
- The GENIE CV check, and (b) for a stopped null, are marked STOPPED.
- If both GENIE nulls fail, the eval stops as before.
- A partial result exits 5.

Nothing else changed: formulas, readouts, thresholds, the declaration (`3806fc58…`, re-verified on the cluster) and every
other staged file (re-verified against §6 by `sha256sum` after restaging). The edit was tested on the synthetic design,
both with all nulls passing and with NuWro forced to fail. The staged copy equals the worktree file.
