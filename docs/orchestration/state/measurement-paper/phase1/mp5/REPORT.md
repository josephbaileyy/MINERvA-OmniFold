# MP-5: truth muon-angle axis (a) and generator W convention (b) over the 109 reported J cells

**By** the measurement session, 2026-10-20. **Spec:** `BINDING-PHASE1-ADDENDUM-1.md` §3, the M4-W record
(`state/2d-closeout/stageF/methods/M4-W-RECORD.md`), and the director's MP-5(a) amendment (by message, 2026-10-19).
**Prep:** [`PREP.md`](PREP.md), with the §11 amendment made at GO. **Job:** 60017887. This file was written by the
coordinating session from the agent's report text, because the agent's write was refused, and checked against
`out/eval/mp5_results.json`. One comparison in the agent's reading is corrected in §4.

**CITABLE FOR:** the per-J-cell size of the beam-axis vs ν-axis truth convention on the analysis MC (R_c); that shift
carried as a proxy to the four generator predictions; the W-convention shift; each of these in units of the generator's
frozen null spread and under the frozen metric; and that MnvTune v1's prediction uses the analysis convention.
**NOT CITABLE FOR:** any re-grade of A7 (the T replays are descriptive); a model-independent R_c (the GENIE CV proxy
check is labelled UNRELIABLE, §3.2); or GiBUU's W convention, which was not measured.

## 1. Construction (exact formulas in PREP §1)

- **R_c = T_beam(c) / T_ν(c).** The numerator is the MnvTune v1 analysis-MC truth content per J cell with θ_μ measured
  from the fixed MAT beam axis (RotateX(−0.05887)). The denominator is the same content with θ_μ measured from the true
  ν direction (`mc_incomingPartVec`).
  - Both axes recompute pT, p∥ and W. W uses the struck-nucleon M, and rows with NaN W are dropped.
  - E_avail and q3 do not depend on the axis.
  - Population: the G2 full-phase-space truth trees, 49,906,108 ν_μ CC fiducial events, joined by event identity to
    the MasterAnaDev Truth entries (488 files). Events that cross the phase-space edge under the ν axis are included.
- **(a) proxy (primary, labelled a proxy).** Δ_c = μ_G·(R_c − 1) for GENIE CV, GENIE MEC, NuWro and GiBUU.
  - Assumption: the beam-axis vs ν-axis migration is a kinematic smearing of the muon direction by about 1 mrad, nearly
    independent of the interaction model, so a ratio measured on Tune v1 transfers. The measured ν-to-beam angle has
    median 1.03 mrad, 68% interval [0.50, 1.92], and maximum 6.9.
- **(a) check.** GENIE CV is rebuilt with each lepton rotated into the beam frame by a ν direction drawn from the
  analysis MC within its Eν bin.
  - Seed 520261019; Eν bins at 0/3/5/8/15/30/∞ GeV; declaration sha256 `3806fc58…`, fixed before the run.
  - The result is compared cell by cell with μ_G·R_c. Rule: if any cell differs by more than 0.2 σ_c, the proxy is
    UNRELIABLE for the other generators.
- **(b).** Δ_c = μ_G·s_c, with s_c the M4-W record's own per-cell shift (`probe_gen.json`, `per_cell_rel_weighted`),
  for GENIE CV and NuWro.
  - Assumption, accepted at GO: s_c was measured on the < 50 GeV sample and is applied to the full product, including the
    50–100 GeV supplement.
- **Readout, as MP3-A.**
  - Δ/σ_c in three readings: (a) the SD over the frozen null ensemble (primary), (b) √diag W, (c) the null-residual SD.
  - ΔᵀW⁻¹Δ under the frozen W (primary); GiBUU on its 72-cell domain.
  - The shape form, with the Jacobian at the data.
  - The null T at c = 0, recomputed.
  - A descriptive replay of the observed T with μ_G + Δ.

## 2. Controls (all passed; none relaxed)

| id | result |
|---|---|
| T0 | Input digests match: 5D omnifile `b6d2651c…`, `of_inputs_5d.npz` `07fccc1a…`, `mnvtune_v1_xsec5d.npz` `bf7bd278…`; all 12 G2 ROOT files match their production receipts |
| T1 | The G2 rows inside the kinematic phase space equal **all 32,849,103** 5D `mc_truth_denom` rows **bitwise** (MC, MC_pz, MC_eavail, MC_q3, MC_W, w_truth), in playlist order 1A…1P |
| T2 | 49,906,108 of 49,906,108 G2 rows joined. The 289 duplicate MAD keys all have identical content. The stored beam-frame muon equals RotateX(l) to ≤ 2.9e-11 MeV |
| **T3** | **The beam-axis analysis truth reproduces the MnvTune v1 frozen prediction bitwise**: T_beam equals `denom_nd`; the extraction reproduces the product's xsec and sumw2; U·x equals `s5p_joint.prediction(MnvTune)` |
| T4 | Recomputed beam-axis pT, p∥, W and q3 equal the stored truth bitwise, with the same NaN-W pattern |
| **G1** | **The GENIE CV rebuild through the rotation path with n = ẑ** reproduces `extract_genie` (main and supplement) and the frozen `genie_cv_xsec5d.npz` and `_full.npz` **bitwise**. ν is along +z in every gst entry |
| E1 | T_obs, null medians, null SDs, B and k at c = 0 equal `joint-evaluate.json` **bitwise** for all four generators; no generator is stopped |
| E2 | U·x_unrot equals μ for GENIE CV bitwise. The M4-W per-cell s_c reproduce the record's own median, maximum, argmax and count above 1e-3 exactly |

**MnvTune v1's Δ is zero by construction, verified two ways.**
- In code: the prediction is `denom_nd` passed through the extraction. `denom_nd` is built from
  `GetMuonPTTrue`/`GetMuonPzTrue`/`GetTrueExperimentersW`, which use `GetThetalepTrue`, the beam axis.
- In bytes: T3 and T4 above.

## 3. Results

### 3.1 (a) R_c on the analysis MC, and the proxy

- **R_c over the 109 cells** is 0.99649 / 1.000008 / 1.00346 (min / median / max); median |R_c − 1| = 2.9e-4.
  Integrated over the cells it is 0.999995.
- **It is at the MC floor.** The MC error of R_c has median 4.7e-4, and |R_c − 1|/sd has median 0.81 (maximum 4.2), so
  most cells are not resolved.
- **Per event.**
  - pT(beam) − pT(ν) lies within ±4.2 MeV for 68% of events and ±11.6 MeV for 95%; W within ±2.5 MeV for 68%.
  - 3.1% of events (weighted) change fine pT bin, and 1.06% change J cell.
  - These figures agree with M4-W.

| (a) proxy, Δ = μ_G(R_c − 1) | GENIE CV | GENIE MEC | NuWro | GiBUU (72) |
|---|---:|---:|---:|---:|
| **Δ/σ_c (a)**, min / median / max | **−0.075 / 0.000 / +0.039** | −0.066 / 0.000 / +0.041 | −0.074 / 0.000 / +0.043 | −0.028 / 0.000 / +0.045 |
| Δ/σ_c (b), √diag W | −0.040 / 0.000 / +0.035 | −0.038 / 0.000 / +0.027 | −0.043 / 0.000 / +0.031 | −0.022 / 0.000 / +0.034 |
| Δ/σ_c (c), null-residual SD | −0.038 / 0.000 / +0.033 | −0.036 / 0.000 / +0.025 | −0.041 / 0.000 / +0.031 | −0.023 / 0.000 / +0.031 |
| cells with \|Δ/σ_c\| > 0.1 | 0 | 0 | 0 | 0 |
| **ΔᵀW⁻¹Δ** (frozen W) | **0.067** | **0.067** | **0.075** | **0.016** |
| shape form, Jacobian at the data | 0.082 | 0.077 | 0.100 | 0.027 |
| null T_total, median / 95th percentile / SD | 527.7 / 630.7 / 58.4 | 406.0 / 476.2 / 38.7 | 6323.9 / 6620.9 / 174.3 | 1791.4 / 1951.3 / 88.8 |
| null T_shape, median / 95th percentile / SD | 582.4 / 756.2 / 95.0 | 449.6 / 563.8 / 67.7 | 7110.3 / 8488.2 / 890.0 | 1975.0 / 2489.1 / 298.4 |
| DESCRIPTIVE ΔT_obs / null SD, total / shape | −0.025 / −0.014 | −0.038 / −0.022 | +0.034 / +0.009 | +0.019 / +0.014 |

### 3.2 The proxy check (GENIE CV): **UNRELIABLE** by the declared 0.2 σ_c rule

- **Result.** The largest |μ_G,beam − μ_G·R_c|/σ_c is **0.56, in J152**; the median is 0.019. Six cells exceed 0.2:
  J139, J143, J145, J152, J220 and J240. As declared, the proxy is therefore **UNRELIABLE for GENIE MEC, NuWro and
  GiBUU**.
- **Context, measured; it does not change the label.**
  - All six cells have p∥ ≥ 6 GeV/c. There the GENIE CV sample's own migration noise is 0.16–0.73 σ_c; nine cells have
    noise above 0.2 σ_c, and the median is 0.035.
  - In units of that noise, the check differences run from −1.97 to +2.17, with Σ(d/noise)² = 90 over 109 cells,
    which is consistent with noise.
  - So at 0.2 σ_c the check is limited by GENIE's MC statistics in those cells. It neither finds nor excludes a model
    dependence there.
- **GENIE's own beam-axis shift**, with MC noise included:
  - Δ/σ_c is −0.47 / 0.00 / +0.53, and ΔᵀW⁻¹Δ = 3.89, against ≈ 1.9 expected from noise alone on the diagonal.
  - DESCRIPTIVE: the observed T moves by +0.23 null SD (total) and +0.06 (shape).

### 3.3 (b) The generator W convention, from the record's own s_c

| Δ = μ_G·s_c | GENIE CV | NuWro |
|---|---:|---:|
| s_c min / max (from the record) | −1.57% (J240) / +1.53% | −2.19% (J91) / +1.21% |
| **Δ/σ_c (a)**, min / median / max | **−0.151 / 0.000 / +0.144** | **−0.237 / 0.000 / +0.143** |
| Δ/σ_c (b), √diag W | −0.162 / 0.000 / +0.167 | −0.165 / 0.000 / +0.173 |
| Δ/σ_c (c), null-residual SD | −0.149 / 0.000 / +0.142 | −0.232 / 0.000 / +0.139 |
| cells with \|Δ/σ_c\| > 0.1 / > 0.2 | 6 / 0 | 8 / 2 (J91, J118) |
| **ΔᵀW⁻¹Δ** | **2.46** | **2.77** |
| shape form, Jacobian at the data | 2.84 | 3.44 |
| DESCRIPTIVE ΔT_obs / null SD, total / shape | **−0.59** / −0.14 | +0.007 / +0.022 |

The largest (b) cells lie at the W = 1.4 GeV J boundary, as the record found.

## 4. Reading

- **(a) is negligible against every frozen scale.** It is ≤ 0.075 σ_c per cell, with ΔᵀW⁻¹Δ ≤ 0.075 against null
  medians of 406–6324, and it sits at the analysis MC's statistical floor.
  - Its transfer to MEC, NuWro and GiBUU carries the declared UNRELIABLE label, though the check that sets the label is
    itself noise-limited at p∥ ≥ 6.
  - Even GENIE's own shift, noise included, moves T by only 0.23 null SD.
- **(b) is the larger of the two:** at most 0.24 σ_c per cell, with ΔᵀW⁻¹Δ of 2.5–2.8.
- **Shifts against the decision-boundary margins.** The agent's text compared these with "A7's smallest decision margin,
  2.8 null SD". That is the superseded median-based figure (addendum 3 §2), and the director corrected it. Below, each
  descriptive ΔT, in null SD of that test's c = 0 null, sits beside the test's decision-boundary margin from
  [`../a7margins/RECEIPT.md`](../a7margins/RECEIPT.md), in the claim family and at κ = 3.
  - A negative ΔT moves T toward the boundary.
  - The share column is |ΔT| / (κ = 3 margin), given only when ΔT < 0.

| test | claim / κ = 3 margin | (a) proxy ΔT | (b) W convention ΔT | GENIE's own beam-axis shift ΔT | largest share of the κ = 3 margin |
|---|---|---:|---:|---:|---|
| GENIE CV **total** | 17.67 / 16.25 | −0.025 | **−0.59** | +0.23 | (b): 3.6% |
| GENIE CV **shape** | 1.30 / **0.67** | −0.014 | **−0.14** | +0.06 | **(b): 21%** |
| GENIE MEC total | 27.41 / 25.79 | −0.038 | — | — | (a): 0.1% |
| GENIE MEC shape | 2.79 / 2.01 | −0.022 | — | — | (a): 1.1% |
| NuWro total | 2.72 / 2.14 | +0.034 | +0.007 | — | none (away from the boundary) |
| NuWro shape | 1.11 / 1.01 | +0.009 | +0.022 | — | none (away from the boundary) |
| GiBUU total | 7.86 / 6.74 | +0.019 | — | — | none (away from the boundary) |
| GiBUU shape | 3.58 / 3.18 | +0.014 | — | — | none (away from the boundary) |

  - **(b) for GENIE CV shape is not negligible.** It is −0.14 null SD against the smallest boundary margin of all
    twenty, 0.67 at κ = 3: about a fifth of the margin, toward the boundary. It does not cross the boundary. Combined
    with other small definitional or target effects, it is the kind of shift the campaign contract should remove by
    rebuilding predictions in the analysis conventions.
  - (b) for GENIE CV total is −0.59, about 4% of its margin.
  - Every (a) shift toward a boundary is at most 2.1% of its κ = 3 margin (GENIE CV shape: 0.014 / 0.67).
- **For the combined-campaign contract (addendum §3).** Nothing here supports redefining the analysis truth about the
  ν axis. The beam-axis truth is the frozen MnvTune prediction itself (T3), and the axis difference is at the MC floor.
  The rebuilt predictions should use the analysis conventions.

## 5. Flagged decisions

1. R_c uses the recomputed beam axis for both T; the variant using the stored truth differs by ≤ 6.4e-14.
2. The W conventions are kept separate, so the two effects do not mix. The ν-axis W keeps the analysis M and NaN rule,
   so (a) isolates the axis. The check's beam-axis W keeps GENIE's fixed M and its W = 0 clamp, so (b) does not leak
   into the check.
3. The ν direction pool is all fiducial CC events, weighted by w_truth.
4. Before submission, `mp5_eval.py` was changed (PREP §11, sha256 `08a0bc4c…`) so that an E1 failure stops only the
   generator that fails, as the GO required. E1 passed for all four, so the change had no effect. The declaration was
   untouched.
5. The UNRELIABLE label follows the declared rule literally.

## 6. Job and charge

| job | QOS | State | ExitCode | ElapsedRaw | AllocTRES | CPU node-h |
|---|---|---|---|---:|---|---:|
| 60017887 | shared (m3246, cpu) | COMPLETED | 0:0 | 451 s | billing=32,cpu=32,energy=160001,mem=60960M,node=1 | **0.015660** |

- **Run:** 2026-10-20 04:29:48–04:37:19 PDT; no GPU.
- **Writes:** only under `/pscratch/…/phase1/mp5/`, nothing on CFS.
- **Outputs:** fetched, with sha256 matching on both sides (`out_sha256.txt`).

## 7. UNCONFIRMED

- No independent recompute was done; the controls are self-consistency checks against frozen bytes.
- The proxy's transfer is not established (UNRELIABLE by rule, and noise-limited at p∥ ≥ 6).
- For (b), the supplement is assumed to share the < 50 GeV shift. GiBUU's W convention was not measured.

## 8. Files

- `out/tune/mp5_tune.npz` and `out/genie/mp5_genie.npz`. **The two run receipts `mp5_tune.json` and `mp5_genie.json`
  are held out of git for now.** They cite the 1.6 GB direction-pool arrays (`pool_b0..5.npy`, cluster-only under
  `/pscratch/sd/j/josephrb/measurement-paper/phase1/mp5/run/pool/`) by bare name, and `verify_receipt_artifacts.py`
  classifies a bare citation as MISSING when the receipt's own directory is tracked, before it consults the declared
  off-area `direction_pool/dir`. Their sha256 are in `out_sha256.txt`, and both receipts are kept on pscratch and in
  the session worktree. Their controls are restated in `out/eval/mp5_results.json` (`controls`). This is raised with
  the director as a verifier-precedence question.
- `out/eval/mp5_results.json`
- `out/eval/mp5_cells.csv`
- `logs/mp5-60017887.out`
- `out_sha256.txt`
- [`PREP.md`](PREP.md)
- `prep/`

Code: `measurement-paper/phase1/mp5/`.
