# MP3-A: the GENIE CH vs carbon-only target effect over the 109 reported J cells

**By** the measurement session, 2026-10-19, under the frozen specification MP3-A
([`PLAN.md`](../../PLAN.md) §4.2 route 1, §4.3; frozen by
[`BINDING-PHASE1-20261019.md`](../../BINDING-PHASE1-20261019.md) §2). **Tree:** branch
`measurement-paper/phase1-20261019` from `da43e98d`. Code: `measurement-paper/phase1/mp3a/`.
Outputs, receipt and ledger rows are in this directory.

**CITABLE FOR:** GENIE 2.12.10's own size and sign of the C-vs-CH target effect per reported J cell
(CV and MEC), and that shift in units of each generator's frozen null spread and under the frozen metric.
**NOT CITABLE FOR:** any re-grade of A7 or any s5p decision (D6: beside A7, labelled, replacing nothing); NuWro's or
GiBUU's target effect (MP3-B/C); any test (descriptive, no threshold); any claim (Joseph's).

## 1. Estimand and construction

Per reported J cell c and G ∈ {GENIE 2.12.10 CV, GENIE 2.12.10 + Valencia MEC}:

- **μ_CH(c)** is the frozen s5p prediction: `U · xsec_flat` of `gen5d_fluxfix/<G>_xsec5d_full.npz`, i.e.
  `s5p_joint.prediction` (`nd-unfolding/s5p_joint.py:78-80`). It is the < 50 GeV flux-fixed product
  (`gen5d_flux_reweight.build_genie`, σ_CC = (C12 + H1)/13, `:173-191`) plus the 50–100 GeV supplement
  (`gen5d_flux_supplement.cmd_supplement`).
- **μ_C(c)** uses the same events, the same per-event weights and the same normalization constants, restricted to
  gst `tgt == 1000060120`, times 13/12: the carbon-only cross section per C12 nucleon. This is r5's normalization
  (`inelastic-high-region-20261011/code/r5_genie_events.py:140-141`).
- **f_H(c)** is the `tgt == 2212` share of μ_CH(c).
- **r_c = μ_C/μ_CH = (13/12)(1 − f_H − f_other)**, and its shape-normalized form **r̃_c = (μ_C/Σμ_C)/(μ_CH/Σμ_CH)**,
  where Σ runs over the 109 cells.
- **Δ_c = μ_C(c) − μ_CH(c)**, divided by σ_c. σ_c is the SD (ddof 1) over G's frozen calibration ensemble of the
  J-cell result as `s5p_joint.ensemble` forms it: `Model.apply(U x)`, with the recorded lateral z, the 1.4%
  normalization z and the 0x4A01 rounding-noise draw (`s5p_joint.py:115-121, 141-144`). Ensemble sizes are
  B = 1366 (CV) and 1343 (MEC), the frozen final B.
- **Metric norms** of Δ are computed under W = V + diag Var(μ_G) (V = `V-s3v.npz`, sha256 `35979ef7…`), using
  `s5p_inference.stat_total`, `stat_shape` and `shape_parts`. They are reported beside the null's T at c = 0, which
  is recomputed here with `s5p_joint.statistics` and its frozen surrogate seeds.

The J map is `s5p_stage1_inspect.coarse_map(J_EDGES, supported)` (fine cells assigned by centre; `:45-46, :77`).
The 109 supported cells come from `state/s5c/contract.json`. Every statistic is computed by the frozen modules
themselves: copies byte-identical to `4f5a613f`, imported from the job's code directory, with `__file__` asserted.

## 2. Provenance and controls

| control | result |
|---|---|
| input digests | gst CV/MEC and both supplement gst files match the products' meta sha256; product npz sha256 `cfa42210…` (CV full), `c179855d…` (MEC full) as `gen5d-fluxfix-2.json`; design `404446eb…`, V `35979ef7…`, `joint-evaluate.json` `b9604502…` |
| code | `gen5d_flux_reweight.py` / `gen5d_flux_supplement.py` are sha-identical to the copies that built the products (`gen5d_fluxfix/code/`); `gen_to_xsec5d.py` was imported from the frozen export `gen5d/code/tree` (81d94a95), sha `1608acd5…` = worktree; `s5p_joint/inference/stage1_inspect` are identical to 4f5a613f. Every staged file's `git hash-object` equals the worktree blob (`RECEIPT.txt`) |
| normalization constants recomputed | A = ⟨σ_CC⟩_t,<50 = 4.1828971877817583e-38 cm² and B = Σr (CV 1603635.4178695625, MEC 1572065.7855758413) are **bitwise** the products' |
| **CONTROL: frozen 5D prediction rebuilt** | < 50 GeV product **bitwise** (xsec and sumw2); full product **bitwise** (xsec and sumw2), CV and MEC |
| **CONTROL: J-cell prediction** | U·(rebuild) = `s5p_joint.prediction` **bitwise**, CV and MEC |
| target split closure | C12 + H1 + other = CH to 1.1e-14 (fine), 2.7e-15 (J) relative: floating-point summation order only |
| frozen statistic reproduced | T_total_obs, T_shape_obs, null medians, null SDs and k at c = 0 equal `joint-evaluate.json` **bitwise** for both nulls (CV 1812.660 / 1086.145, null median 527.741 / 582.445; MEC 1647.124 / 868.585, 406.013 / 449.625; = `W2B-REPORT-20261006.md:108-114`, rounded) |
| r5 cross-check | per fine W bin over the whole grid, C-only/CH per nucleon and the H (+ other) share reproduce `r5_genie_events.json` to ≤ 9e-16 (W0 1.08285, W1 0.97789) |

**Target codes in phase space.** CV: C12 888,072 + 64,364 (supplement), H 50,068 + 3,752, code 11 (ν–e) 1 + 8. MEC:
C12 911,423 + 64,481, H 48,705 + 3,607, code 11 0 + 16. Every H event has hitnuc = 2212. All 41,799 in-phase-space MEC
events are on carbon. The code-11 events carry zero weight in all 109 reported cells (f_other = 0 there).

## 3. Results

### 3.1 Summary over the 109 cells

| | GENIE CV | GENIE MEC |
|---|---|---|
| Σμ_C / Σμ_CH (all 109) | 1.0255 | 1.0283 |
| f_H, integrated (all 109) | 0.0533 | 0.0508 |
| r_c min / median / max | 0.950 / 1.034 / 1.083 | 0.964 / 1.034 / 1.083 |
| r̃_c min / median / max | 0.926 / 1.008 / 1.056 | 0.938 / 1.005 / 1.054 |
| f_H min / median / max | 0.000 / 0.046 / 0.124 | 0.000 / 0.046 / 0.110 |
| **Δ/σ (σ = null SD of result)** min / median / max | **−0.57 / +0.43 / +1.36** | **−0.48 / +0.42 / +1.37** |
| cells with Δ/σ > 1 / < 0 / \|Δ/σ\| > 0.5 | 4 / 11 / 47 | 4 / 10 / 45 |
| Σ_c (Δ/σ)² (diagonal, ignores correlations) | 31.5 | 32.4 |
| shape Δ/σ (Δq over SD of F/ΣF) min / median / max | −1.85 / +0.16 / +1.69 | −1.58 / +0.07 / +1.83 |
| for scale: null bias (F̄ − μ_CH)/σ, median (range) | +0.49 (−6.1 … +3.8) | +0.52 (−2.7 … +3.5) |

r_c = 13/12 = 1.0833 exactly where the sample has no hydrogen event (f_H = 0: five cells, W < 1.4 GeV,
E_avail < 0.4 GeV, p_T ≥ 0.85 GeV/c). r_c < 1 where f_H peaks (0.11–0.12; W < 1.4 GeV, E_avail 0.4–1.5 GeV, e.g. J90, J144); reading that as the
Δ(1232) π⁺p channel of free-proton CC is an interpretation, not tested here. The per-cell MC error of
r_c (delta method, C and H independent) has median 0.0037. The median |r_c − 1| is 9.4 (CV) / 8.9 (MEC) times its MC
error, and the smallest ratio is 0.3, so a few near-1 cells are not resolved by the sample.

The largest |Δ/σ| are all at **E_avail < 0.4 GeV, W 1.4–2.2 GeV**, mostly p_∥ ≥ 3.5 GeV/c. In descending order these
are J142, J136, J55, J28, J109 for CV (Δ/σ 1.36, 1.21, 1.10, 1.04, 0.96) and J136, J55, J28, J109, J139 for MEC (1.37,
1.21, 1.20, 1.16, 0.99). In these cells f_H ≈ 0.01–0.02, so r ≈ 1.06–1.07, and the null spread is small. The CV and MEC
Δ/σ maps correlate at 0.84.

### 3.2 Regions (J W bins and J E_avail bins; per-region Σμ ratios and per-cell Δ/σ ranges)

| region | n | CV r (Σ) | CV f_H (Σ) | CV r̃ (Σ) | CV Δ/σ min/med/max | MEC r (Σ) | MEC f_H (Σ) | MEC r̃ (Σ) | MEC Δ/σ min/med/max |
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
| W < 1.4 | 32 | 1.022 | 0.057 | 0.997 | −0.57 / +0.28 / +0.84 | 1.029 | 0.051 | 1.000 | −0.48 / +0.43 / +0.85 |
| W 1.4–2.2 | 52 | 1.030 | 0.049 | 1.004 | +0.08 / +0.51 / +1.36 | 1.030 | 0.049 | 1.002 | +0.15 / +0.43 / +1.37 |
| W ≥ 2.2 | 25 | 1.024 | 0.055 | 0.998 | −0.56 / +0.38 / +0.73 | 1.026 | 0.053 | 0.998 | +0.08 / +0.38 / +0.93 |
| E_avail < 0.4 | 42 | 1.046 | 0.034 | 1.020 | +0.20 / +0.67 / +1.36 | 1.050 | 0.031 | 1.021 | +0.27 / +0.69 / +1.37 |
| E_avail 0.4–1.5 | 49 | 1.017 | 0.061 | 0.992 | −0.57 / +0.27 / +0.86 | 1.020 | 0.058 | 0.992 | −0.48 / +0.33 / +0.72 |
| E_avail ≥ 1.5 | 18 | 1.021 | 0.058 | 0.995 | −0.03 / +0.19 / +0.43 | 1.022 | 0.057 | 0.994 | −0.08 / +0.21 / +0.38 |

**W0/W1-like regions.** r5's W0 (W < 1.1) and W1 (1.1–1.4) are fine W bins that both sit inside J's W < 1.4 bin, where
they partly cancel. Restricted to the fine cells of the 109 reported cells, C-only/CH per nucleon is as follows (the
value relative to the reported total is in brackets, which is the shape-normalized form):

| fine W bin | CV | MEC |
|---|---|---|
| W0 [0, 1.1) | 1.0829 (1.0559), f_H 0.0004 | 1.0828 (1.0530), f_H 0.0005 |
| W1 [1.1, 1.4) | 0.9779 (0.9535), f_H 0.0973 | 0.9902 (0.9630), f_H 0.0859 |
| W2–W5 | 1.023–1.031 (0.998–1.005) | 1.025–1.032 (0.996–1.004) |

These agree with C3/C4 (+8.3% / −2.2% per nucleon, +5.6% / −4.6% in shape, CV), now on the reported cells. The J
partition merges W0 and W1, so the J-cell effect at W < 1.4 is smaller (r̃ 0.997 integrated, cells 0.926–1.056).

### 3.3 Metric norms of the shift, beside the null T distribution (c = 0, recomputed bitwise as frozen)

| quantity | GENIE CV | GENIE MEC |
|---|---:|---:|
| **Δᵀ W⁻¹ Δ** (frozen W = V + diag Var μ_CH) [PRIMARY total] | **80.6** | **74.9** |
| Δᵀ W_C⁻¹ Δ (W_C = V + diag Var μ_C) | 77.4 | 72.4 |
| Δᵀ V⁻¹ Δ (V alone) | 297.7 | 237.4 |
| null T_total: median / 95th pct / SD | 527.7 / 630.7 / 58.4 | 406.0 / 476.2 / 38.7 |
| frozen observed T_total | 1812.7 | 1647.1 |
| **shape form at the data's Jacobian**, (q_C − q_CH)ᵀ Vs(f_data)⁻¹ (q_C − q_CH) [PRIMARY shape] | **81.0** | **68.6** |
| stat_shape(f = μ_C, μ = μ_CH, W) | 54.0 | 55.5 |
| stat_shape(f = μ_CH, μ = μ_C, W) | 63.8 | 63.1 |
| null T_shape: median / 95th pct / SD | 582.4 / 756.2 / 95.0 | 449.6 / 563.8 / 67.7 |
| frozen observed T_shape | 1086.1 | 868.6 |

**DESCRIPTIVE, not a re-grade (D6; A7 stands).** These are the observed statistics with μ_CH replaced by μ_C, under the
frozen W:

| | CV T_total | CV T_shape | MEC T_total | MEC T_shape |
|---|---:|---:|---:|---:|
| frozen (μ_CH) | 1812.7 | 1086.1 | 1647.1 | 868.6 |
| with μ_C (frozen W) | 2315.0 | 1460.6 | 2091.4 | 1146.3 |
| with μ_C (W_C) | 2207.7 | 1395.2 | 1986.6 | 1098.0 |
| change / null SD (frozen W) | +8.6 | +3.9 | +11.5 | +4.1 |

The total change decomposes exactly as T(μ_C) − T(μ_CH) = −2 rᵀW⁻¹Δ + ΔᵀW⁻¹Δ, which is 421.8 + 80.6 = 502.3 for CV and
369.4 + 74.9 = 444.3 for MEC. The cross term dominates. Its sign means the data residual r = f_data − μ_CH points against
Δ: in the frozen metric, the data lie on the far side of the CH prediction from the carbon-only one. This describes
GENIE's model only. It says nothing about the sign for NuWro or GiBUU, whose residuals differ.

**How to read §3.3.** A deterministic shift's norm is not a draw of T. The null T is strongly non-central (A7's
pre-freeze λ: 450 CV, 318 MEC), so the shift is best read as an addition to the non-centrality of the order of 75–80
(√ ≈ 9 in whitened units). That is about a sixth of the null median, and 1.4 (CV) to 1.9 (MEC) null T SDs.

## 4. Flagged decisions (computed both ways, labelled; nothing picked silently)

1. **σ_c has three defensible readings.** (a) The SD of the J-cell result over the null ensemble is PRIMARY: these are
   the spec's words, and the table uses it. (b) √diag W, the metric's own scale. (c) The SD of the simulated residual
   f − (μ + ε), with ε the statistic's own keyed prediction-MC draw. They agree at the median (b/a 1.00 CV / 1.02 MEC;
   c/a 1.02 / 1.02) but differ by up to 3.2–3.5× in a few cells. The Δ/σ ranges are (b) CV −0.57…+1.05, MEC −0.51…+1.22
   and (c) CV −0.57…+1.01, MEC −0.47…+1.18. All three are in the csv (`z_*`, `z_sqrtdiagW_*`, `z_resid_*`).
2. **The shape norm depends on where the Jacobian is taken.** The frozen T_shape takes it at the data (PRIMARY: 81.0 / 68.6).
   `stat_shape` with the shift as its argument puts it at μ_C or μ_CH (54.0–63.8 / 55.5–63.1). The total norm depends on
   whether the metric's prediction-MC term is μ_CH's (frozen, PRIMARY) or μ_C's: a 4% difference. V alone, without the
   prediction-MC term, gives 3–4× larger norms. That is not the frozen metric; it is shown only because the brief wrote
   "Δμᵀ V⁻¹ Δμ".
3. **Interpreter.** The job ran in `root_6_28` (Python 3.11.14, numpy 1.26.4, scipy 1.16.3), not `omnifold_py310`. That is
   the env that built the gen5d products and ran the frozen evaluation (`s5p_terminal_run.sh:86-88`), and the split
   needs ROOT RDataFrame as the product build used it. Thread counts were OMP/OPENBLAS = 4, as frozen. The bitwise
   controls are the evidence that this choice changed nothing.
4. **The code-11 (ν–e) events** are excluded from C-only, as the spec reads, and are kept in μ_CH, as frozen. r5 counted
   them with H. They are zero in every reported cell, so the choice is immaterial here.
5. **σ_c uses ddof 1.** The null-T SD in §3.3 is `np.std` (ddof 0), as `s5p_joint.py:246` reports it.

## 5. Jobs and charge

| job | QOS | State | ExitCode | ElapsedRaw | AllocTRES | charge (CPU node-h) |
|---|---|---|---|---:|---|---:|
| 60005151 | shared (m3246, cpu) | COMPLETED | 0:0 | 106 s | billing=8,cpu=8,energy=57614,mem=15240M,node=1 | **0.000920** |

Charge = ElapsedRaw × billing/256/3600 (total for MP3-A; brief cap 0.5, PLAN ≤ 0.1; 0 GPU). Writes only under `/pscratch/sd/j/josephrb/measurement-paper/phase1/mp3a/`, none to CFS; no other job touched (SF-1 `60004676` seen pending, left alone). The row is landed in [`../LEDGER.tsv`](../LEDGER.tsv). Reviewed by the measurement session before commit; step-1 result reported to the director 2026-10-19.

## 6. UNCONFIRMED

- **No independent recompute**; the controls are self-consistency against frozen bytes.
- **C-only is the carbon subset of the CH run** ×13/12, not a separate C12-target GENIE run (equal in expectation if GENIE
  draws per-nucleus interactions independently; untested). B sums r over all CC events, H included, as frozen.
- **MC error of Δ is not propagated** into Δ/σ; r_c's MC error is in the csv (`sd_r_mc_*`); a few near-1 cells are unresolved.
- **The null-SD unit is a per-cell Gaussian proxy**; correlations enter only the norms (Σ(Δ/σ)² ≈ 32 vs ΔᵀW⁻¹Δ ≈ 75–81).
- **Nothing transfers to NuWro or GiBUU** (MP3-B/C; NuWro probe f_H 5.1% vs GENIE 5.3%). E_ν > 100 GeV absent, as frozen.

## 7. Files

`out/eval/mp3a_cells.csv` (per cell: index, J name, all edges; f_H, r, its MC error, r̃, Δ/σ in the three readings and
shape Δ/σ, CV and MEC); `out/eval/mp3a_results.json` (all per-cell arrays, controls, regions, norms, null T, descriptive
T); `out/build/mp3a_build.json` (build controls, target counts, r5 cross-check); `out/build/mp3a_fine_genie_{cv,mec}.npz`
(fine C12/H1/other parts, rebuilt CH); `logs/mp3a-60005151.out`; `RECEIPT.txt`; `out_sha256.txt`. (`out/build/` and `logs/*.out` match generic `.gitignore` rules and are force-added as evidence.)

## 8. Per-cell table (Δ/σ: σ = null SD of the J-cell result, reading (a); r̃ = shape-normalized r)

| # | cell | p_T | p_∥ | E_avail | q_3 | W | f_H CV | r CV | r̃ CV | Δ/σ CV | f_H MEC | r MEC | r̃ MEC | Δ/σ MEC |
|---:|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | J0 | 0–0.55 | 1.5–3.5 | 0–0.4 | 0–1.2 | 0–1.4 | 0.057 | 1.021 | 0.996 | +0.20 | 0.050 | 1.030 | 1.001 | +0.30 |
| 1 | J1 | 0–0.55 | 1.5–3.5 | 0–0.4 | 0–1.2 | 1.4–2.2 | 0.012 | 1.070 | 1.043 | +0.79 | 0.014 | 1.069 | 1.039 | +0.85 |
| 2 | J4 | 0–0.55 | 1.5–3.5 | 0–0.4 | 1.2–2 | 1.4–2.2 | 0.026 | 1.055 | 1.029 | +0.55 | 0.023 | 1.058 | 1.029 | +0.59 |
| 3 | J7 | 0–0.55 | 1.5–3.5 | 0–0.4 | 2–100 | 1.4–2.2 | 0.055 | 1.023 | 0.998 | +0.20 | 0.040 | 1.040 | 1.012 | +0.38 |
| 4 | J8 | 0–0.55 | 1.5–3.5 | 0–0.4 | 2–100 | 2.2–100 | 0.040 | 1.040 | 1.014 | +0.33 | 0.032 | 1.049 | 1.020 | +0.38 |
| 5 | J9 | 0–0.55 | 1.5–3.5 | 0.4–1.5 | 0–1.2 | 0–1.4 | 0.085 | 0.992 | 0.967 | -0.07 | 0.071 | 1.006 | 0.978 | +0.06 |
| 6 | J10 | 0–0.55 | 1.5–3.5 | 0.4–1.5 | 0–1.2 | 1.4–2.2 | 0.061 | 1.017 | 0.992 | +0.18 | 0.051 | 1.028 | 1.000 | +0.32 |
| 7 | J13 | 0–0.55 | 1.5–3.5 | 0.4–1.5 | 1.2–2 | 1.4–2.2 | 0.052 | 1.027 | 1.001 | +0.25 | 0.049 | 1.031 | 1.002 | +0.30 |
| 8 | J16 | 0–0.55 | 1.5–3.5 | 0.4–1.5 | 2–100 | 1.4–2.2 | 0.042 | 1.038 | 1.012 | +0.36 | 0.039 | 1.041 | 1.013 | +0.41 |
| 9 | J17 | 0–0.55 | 1.5–3.5 | 0.4–1.5 | 2–100 | 2.2–100 | 0.050 | 1.030 | 1.004 | +0.27 | 0.045 | 1.035 | 1.006 | +0.32 |
| 10 | J25 | 0–0.55 | 1.5–3.5 | 1.5–100 | 2–100 | 1.4–2.2 | 0.065 | 1.013 | 0.988 | +0.14 | 0.058 | 1.021 | 0.993 | +0.23 |
| 11 | J26 | 0–0.55 | 1.5–3.5 | 1.5–100 | 2–100 | 2.2–100 | 0.060 | 1.019 | 0.993 | +0.18 | 0.061 | 1.018 | 0.990 | +0.18 |
| 12 | J27 | 0–0.55 | 3.5–6 | 0–0.4 | 0–1.2 | 0–1.4 | 0.053 | 1.026 | 1.000 | +0.37 | 0.045 | 1.035 | 1.007 | +0.54 |
| 13 | J28 | 0–0.55 | 3.5–6 | 0–0.4 | 0–1.2 | 1.4–2.2 | 0.016 | 1.066 | 1.040 | +1.04 | 0.011 | 1.072 | 1.042 | +1.20 |
| 14 | J31 | 0–0.55 | 3.5–6 | 0–0.4 | 1.2–2 | 1.4–2.2 | 0.025 | 1.056 | 1.030 | +0.74 | 0.020 | 1.062 | 1.033 | +0.88 |
| 15 | J34 | 0–0.55 | 3.5–6 | 0–0.4 | 2–100 | 1.4–2.2 | 0.027 | 1.054 | 1.028 | +0.69 | 0.038 | 1.042 | 1.013 | +0.51 |
| 16 | J35 | 0–0.55 | 3.5–6 | 0–0.4 | 2–100 | 2.2–100 | 0.041 | 1.039 | 1.014 | +0.40 | 0.027 | 1.054 | 1.025 | +0.59 |
| 17 | J36 | 0–0.55 | 3.5–6 | 0.4–1.5 | 0–1.2 | 0–1.4 | 0.085 | 0.991 | 0.967 | -0.10 | 0.066 | 1.011 | 0.983 | +0.17 |
| 18 | J37 | 0–0.55 | 3.5–6 | 0.4–1.5 | 0–1.2 | 1.4–2.2 | 0.057 | 1.022 | 0.996 | +0.33 | 0.054 | 1.025 | 0.997 | +0.39 |
| 19 | J40 | 0–0.55 | 3.5–6 | 0.4–1.5 | 1.2–2 | 1.4–2.2 | 0.049 | 1.031 | 1.005 | +0.44 | 0.050 | 1.029 | 1.000 | +0.43 |
| 20 | J43 | 0–0.55 | 3.5–6 | 0.4–1.5 | 2–100 | 1.4–2.2 | 0.037 | 1.043 | 1.017 | +0.64 | 0.038 | 1.042 | 1.013 | +0.67 |
| 21 | J44 | 0–0.55 | 3.5–6 | 0.4–1.5 | 2–100 | 2.2–100 | 0.043 | 1.037 | 1.011 | +0.47 | 0.050 | 1.029 | 1.001 | +0.37 |
| 22 | J52 | 0–0.55 | 3.5–6 | 1.5–100 | 2–100 | 1.4–2.2 | 0.064 | 1.014 | 0.989 | +0.21 | 0.063 | 1.015 | 0.987 | +0.23 |
| 23 | J53 | 0–0.55 | 3.5–6 | 1.5–100 | 2–100 | 2.2–100 | 0.061 | 1.017 | 0.992 | +0.26 | 0.063 | 1.016 | 0.988 | +0.26 |
| 24 | J54 | 0–0.55 | 6–60 | 0–0.4 | 0–1.2 | 0–1.4 | 0.048 | 1.032 | 1.006 | +0.52 | 0.043 | 1.037 | 1.008 | +0.63 |
| 25 | J55 | 0–0.55 | 6–60 | 0–0.4 | 0–1.2 | 1.4–2.2 | 0.017 | 1.065 | 1.038 | +1.10 | 0.016 | 1.066 | 1.036 | +1.21 |
| 26 | J58 | 0–0.55 | 6–60 | 0–0.4 | 1.2–2 | 1.4–2.2 | 0.041 | 1.039 | 1.013 | +0.68 | 0.029 | 1.052 | 1.023 | +0.94 |
| 27 | J63 | 0–0.55 | 6–60 | 0.4–1.5 | 0–1.2 | 0–1.4 | 0.075 | 1.002 | 0.977 | +0.03 | 0.056 | 1.022 | 0.994 | +0.36 |
| 28 | J64 | 0–0.55 | 6–60 | 0.4–1.5 | 0–1.2 | 1.4–2.2 | 0.055 | 1.023 | 0.998 | +0.37 | 0.052 | 1.026 | 0.998 | +0.43 |
| 29 | J67 | 0–0.55 | 6–60 | 0.4–1.5 | 1.2–2 | 1.4–2.2 | 0.047 | 1.033 | 1.007 | +0.54 | 0.051 | 1.028 | 0.999 | +0.45 |
| 30 | J70 | 0–0.55 | 6–60 | 0.4–1.5 | 2–100 | 1.4–2.2 | 0.025 | 1.056 | 1.030 | +0.85 | 0.063 | 1.015 | 0.987 | +0.19 |
| 31 | J71 | 0–0.55 | 6–60 | 0.4–1.5 | 2–100 | 2.2–100 | 0.061 | 1.018 | 0.992 | +0.24 | 0.049 | 1.031 | 1.002 | +0.50 |
| 32 | J80 | 0–0.55 | 6–60 | 1.5–100 | 2–100 | 2.2–100 | 0.064 | 1.014 | 0.989 | +0.17 | 0.060 | 1.018 | 0.990 | +0.19 |
| 33 | J81 | 0.55–0.85 | 1.5–3.5 | 0–0.4 | 0–1.2 | 0–1.4 | 0.014 | 1.069 | 1.042 | +0.65 | 0.010 | 1.073 | 1.043 | +0.70 |
| 34 | J85 | 0.55–0.85 | 1.5–3.5 | 0–0.4 | 1.2–2 | 1.4–2.2 | 0.013 | 1.069 | 1.042 | +0.70 | 0.015 | 1.067 | 1.038 | +0.73 |
| 35 | J88 | 0.55–0.85 | 1.5–3.5 | 0–0.4 | 2–100 | 1.4–2.2 | 0.024 | 1.057 | 1.031 | +0.63 | 0.035 | 1.045 | 1.016 | +0.52 |
| 36 | J89 | 0.55–0.85 | 1.5–3.5 | 0–0.4 | 2–100 | 2.2–100 | 0.026 | 1.055 | 1.029 | +0.73 | 0.033 | 1.048 | 1.019 | +0.66 |
| 37 | J90 | 0.55–0.85 | 1.5–3.5 | 0.4–1.5 | 0–1.2 | 0–1.4 | 0.124 | 0.950 | 0.926 | -0.40 | 0.104 | 0.971 | 0.944 | -0.25 |
| 38 | J91 | 0.55–0.85 | 1.5–3.5 | 0.4–1.5 | 0–1.2 | 1.4–2.2 | 0.067 | 1.010 | 0.985 | +0.08 | 0.051 | 1.028 | 1.000 | +0.26 |
| 39 | J93 | 0.55–0.85 | 1.5–3.5 | 0.4–1.5 | 1.2–2 | 0–1.4 | 0.093 | 0.983 | 0.958 | -0.13 | 0.100 | 0.975 | 0.948 | -0.19 |
| 40 | J94 | 0.55–0.85 | 1.5–3.5 | 0.4–1.5 | 1.2–2 | 1.4–2.2 | 0.053 | 1.026 | 1.001 | +0.23 | 0.052 | 1.027 | 0.999 | +0.25 |
| 41 | J97 | 0.55–0.85 | 1.5–3.5 | 0.4–1.5 | 2–100 | 1.4–2.2 | 0.033 | 1.047 | 1.021 | +0.51 | 0.036 | 1.045 | 1.016 | +0.52 |
| 42 | J98 | 0.55–0.85 | 1.5–3.5 | 0.4–1.5 | 2–100 | 2.2–100 | 0.045 | 1.034 | 1.009 | +0.46 | 0.043 | 1.037 | 1.008 | +0.53 |
| 43 | J106 | 0.55–0.85 | 1.5–3.5 | 1.5–100 | 2–100 | 1.4–2.2 | 0.062 | 1.016 | 0.991 | +0.19 | 0.064 | 1.014 | 0.986 | +0.17 |
| 44 | J107 | 0.55–0.85 | 1.5–3.5 | 1.5–100 | 2–100 | 2.2–100 | 0.056 | 1.023 | 0.997 | +0.31 | 0.056 | 1.023 | 0.994 | +0.32 |
| 45 | J108 | 0.55–0.85 | 3.5–6 | 0–0.4 | 0–1.2 | 0–1.4 | 0.016 | 1.066 | 1.040 | +0.84 | 0.015 | 1.067 | 1.038 | +0.85 |
| 46 | J109 | 0.55–0.85 | 3.5–6 | 0–0.4 | 0–1.2 | 1.4–2.2 | 0.014 | 1.068 | 1.042 | +0.96 | 0.012 | 1.070 | 1.041 | +1.16 |
| 47 | J111 | 0.55–0.85 | 3.5–6 | 0–0.4 | 1.2–2 | 0–1.4 | 0.013 | 1.069 | 1.042 | +0.79 | 0.022 | 1.060 | 1.031 | +0.72 |
| 48 | J112 | 0.55–0.85 | 3.5–6 | 0–0.4 | 1.2–2 | 1.4–2.2 | 0.016 | 1.066 | 1.040 | +0.94 | 0.016 | 1.066 | 1.036 | +0.98 |
| 49 | J115 | 0.55–0.85 | 3.5–6 | 0–0.4 | 2–100 | 1.4–2.2 | 0.026 | 1.056 | 1.029 | +0.79 | 0.035 | 1.046 | 1.017 | +0.67 |
| 50 | J116 | 0.55–0.85 | 3.5–6 | 0–0.4 | 2–100 | 2.2–100 | 0.036 | 1.045 | 1.019 | +0.65 | 0.031 | 1.050 | 1.021 | +0.70 |
| 51 | J117 | 0.55–0.85 | 3.5–6 | 0.4–1.5 | 0–1.2 | 0–1.4 | 0.123 | 0.950 | 0.926 | -0.57 | 0.105 | 0.969 | 0.943 | -0.37 |
| 52 | J118 | 0.55–0.85 | 3.5–6 | 0.4–1.5 | 0–1.2 | 1.4–2.2 | 0.054 | 1.025 | 0.999 | +0.29 | 0.055 | 1.023 | 0.995 | +0.31 |
| 53 | J120 | 0.55–0.85 | 3.5–6 | 0.4–1.5 | 1.2–2 | 0–1.4 | 0.075 | 1.002 | 0.977 | +0.02 | 0.087 | 0.989 | 0.962 | -0.10 |
| 54 | J121 | 0.55–0.85 | 3.5–6 | 0.4–1.5 | 1.2–2 | 1.4–2.2 | 0.051 | 1.028 | 1.002 | +0.33 | 0.052 | 1.027 | 0.998 | +0.33 |
| 55 | J124 | 0.55–0.85 | 3.5–6 | 0.4–1.5 | 2–100 | 1.4–2.2 | 0.034 | 1.047 | 1.021 | +0.63 | 0.041 | 1.039 | 1.011 | +0.58 |
| 56 | J125 | 0.55–0.85 | 3.5–6 | 0.4–1.5 | 2–100 | 2.2–100 | 0.046 | 1.034 | 1.008 | +0.49 | 0.054 | 1.025 | 0.997 | +0.37 |
| 57 | J133 | 0.55–0.85 | 3.5–6 | 1.5–100 | 2–100 | 1.4–2.2 | 0.064 | 1.014 | 0.988 | +0.19 | 0.062 | 1.016 | 0.988 | +0.23 |
| 58 | J134 | 0.55–0.85 | 3.5–6 | 1.5–100 | 2–100 | 2.2–100 | 0.056 | 1.022 | 0.997 | +0.31 | 0.056 | 1.023 | 0.995 | +0.33 |
| 59 | J135 | 0.55–0.85 | 6–60 | 0–0.4 | 0–1.2 | 0–1.4 | 0.017 | 1.064 | 1.038 | +0.68 | 0.017 | 1.065 | 1.036 | +0.72 |
| 60 | J136 | 0.55–0.85 | 6–60 | 0–0.4 | 0–1.2 | 1.4–2.2 | 0.013 | 1.069 | 1.042 | +1.21 | 0.010 | 1.073 | 1.043 | +1.37 |
| 61 | J139 | 0.55–0.85 | 6–60 | 0–0.4 | 1.2–2 | 1.4–2.2 | 0.025 | 1.056 | 1.030 | +0.93 | 0.021 | 1.061 | 1.032 | +0.99 |
| 62 | J142 | 0.55–0.85 | 6–60 | 0–0.4 | 2–100 | 1.4–2.2 | 0.019 | 1.062 | 1.036 | +1.36 | 0.035 | 1.045 | 1.016 | +0.87 |
| 63 | J143 | 0.55–0.85 | 6–60 | 0–0.4 | 2–100 | 2.2–100 | 0.034 | 1.046 | 1.020 | +0.65 | 0.017 | 1.064 | 1.035 | +0.93 |
| 64 | J144 | 0.55–0.85 | 6–60 | 0.4–1.5 | 0–1.2 | 0–1.4 | 0.119 | 0.954 | 0.930 | -0.57 | 0.110 | 0.964 | 0.938 | -0.48 |
| 65 | J145 | 0.55–0.85 | 6–60 | 0.4–1.5 | 0–1.2 | 1.4–2.2 | 0.060 | 1.018 | 0.993 | +0.25 | 0.054 | 1.025 | 0.997 | +0.37 |
| 66 | J147 | 0.55–0.85 | 6–60 | 0.4–1.5 | 1.2–2 | 0–1.4 | 0.071 | 1.006 | 0.981 | +0.06 | 0.080 | 0.996 | 0.969 | -0.04 |
| 67 | J148 | 0.55–0.85 | 6–60 | 0.4–1.5 | 1.2–2 | 1.4–2.2 | 0.054 | 1.025 | 1.000 | +0.35 | 0.050 | 1.029 | 1.001 | +0.42 |
| 68 | J151 | 0.55–0.85 | 6–60 | 0.4–1.5 | 2–100 | 1.4–2.2 | 0.025 | 1.056 | 1.029 | +0.85 | 0.067 | 1.011 | 0.983 | +0.18 |
| 69 | J152 | 0.55–0.85 | 6–60 | 0.4–1.5 | 2–100 | 2.2–100 | 0.113 | 0.961 | 0.937 | -0.56 | 0.031 | 1.050 | 1.021 | +0.72 |
| 70 | J160 | 0.55–0.85 | 6–60 | 1.5–100 | 2–100 | 1.4–2.2 | 0.050 | 1.029 | 1.004 | +0.43 | 0.067 | 1.011 | 0.983 | +0.17 |
| 71 | J161 | 0.55–0.85 | 6–60 | 1.5–100 | 2–100 | 2.2–100 | 0.067 | 1.011 | 0.985 | +0.13 | 0.071 | 1.007 | 0.979 | +0.08 |
| 72 | J162 | 0.85–4.5 | 1.5–3.5 | 0–0.4 | 0–1.2 | 0–1.4 | 0.000 | 1.083 | 1.056 | +0.45 | 0.000 | 1.083 | 1.054 | +0.49 |
| 73 | J165 | 0.85–4.5 | 1.5–3.5 | 0–0.4 | 1.2–2 | 0–1.4 | 0.004 | 1.079 | 1.052 | +0.64 | 0.003 | 1.080 | 1.050 | +0.69 |
| 74 | J174 | 0.85–4.5 | 1.5–3.5 | 0.4–1.5 | 1.2–2 | 0–1.4 | 0.085 | 0.991 | 0.966 | -0.06 | 0.086 | 0.990 | 0.963 | -0.06 |
| 75 | J175 | 0.85–4.5 | 1.5–3.5 | 0.4–1.5 | 1.2–2 | 1.4–2.2 | 0.051 | 1.028 | 1.002 | +0.19 | 0.050 | 1.029 | 1.001 | +0.22 |
| 76 | J178 | 0.85–4.5 | 1.5–3.5 | 0.4–1.5 | 2–100 | 1.4–2.2 | 0.031 | 1.050 | 1.024 | +0.46 | 0.030 | 1.051 | 1.022 | +0.49 |
| 77 | J179 | 0.85–4.5 | 1.5–3.5 | 0.4–1.5 | 2–100 | 2.2–100 | 0.045 | 1.035 | 1.009 | +0.43 | 0.042 | 1.037 | 1.009 | +0.48 |
| 78 | J187 | 0.85–4.5 | 1.5–3.5 | 1.5–100 | 2–100 | 1.4–2.2 | 0.063 | 1.015 | 0.990 | +0.16 | 0.064 | 1.014 | 0.987 | +0.15 |
| 79 | J188 | 0.85–4.5 | 1.5–3.5 | 1.5–100 | 2–100 | 2.2–100 | 0.053 | 1.026 | 1.000 | +0.33 | 0.051 | 1.028 | 1.000 | +0.38 |
| 80 | J189 | 0.85–4.5 | 3.5–6 | 0–0.4 | 0–1.2 | 0–1.4 | 0.000 | 1.083 | 1.056 | +0.57 | 0.000 | 1.083 | 1.054 | +0.61 |
| 81 | J192 | 0.85–4.5 | 3.5–6 | 0–0.4 | 1.2–2 | 0–1.4 | 0.002 | 1.082 | 1.055 | +0.70 | 0.003 | 1.081 | 1.051 | +0.72 |
| 82 | J193 | 0.85–4.5 | 3.5–6 | 0–0.4 | 1.2–2 | 1.4–2.2 | 0.012 | 1.070 | 1.043 | +0.78 | 0.009 | 1.074 | 1.044 | +0.81 |
| 83 | J195 | 0.85–4.5 | 3.5–6 | 0–0.4 | 2–100 | 0–1.4 | 0.000 | 1.083 | 1.056 | +0.64 | 0.000 | 1.083 | 1.054 | +0.64 |
| 84 | J196 | 0.85–4.5 | 3.5–6 | 0–0.4 | 2–100 | 1.4–2.2 | 0.021 | 1.060 | 1.034 | +0.66 | 0.022 | 1.060 | 1.030 | +0.67 |
| 85 | J197 | 0.85–4.5 | 3.5–6 | 0–0.4 | 2–100 | 2.2–100 | 0.031 | 1.049 | 1.023 | +0.63 | 0.028 | 1.053 | 1.024 | +0.68 |
| 86 | J198 | 0.85–4.5 | 3.5–6 | 0.4–1.5 | 0–1.2 | 0–1.4 | 0.008 | 1.074 | 1.048 | +0.61 | 0.012 | 1.070 | 1.040 | +0.58 |
| 87 | J201 | 0.85–4.5 | 3.5–6 | 0.4–1.5 | 1.2–2 | 0–1.4 | 0.082 | 0.995 | 0.970 | -0.04 | 0.078 | 0.999 | 0.971 | -0.01 |
| 88 | J202 | 0.85–4.5 | 3.5–6 | 0.4–1.5 | 1.2–2 | 1.4–2.2 | 0.054 | 1.025 | 0.999 | +0.21 | 0.052 | 1.027 | 0.999 | +0.24 |
| 89 | J204 | 0.85–4.5 | 3.5–6 | 0.4–1.5 | 2–100 | 0–1.4 | 0.051 | 1.028 | 1.003 | +0.17 | 0.054 | 1.025 | 0.997 | +0.16 |
| 90 | J205 | 0.85–4.5 | 3.5–6 | 0.4–1.5 | 2–100 | 1.4–2.2 | 0.027 | 1.054 | 1.027 | +0.51 | 0.029 | 1.051 | 1.023 | +0.50 |
| 91 | J206 | 0.85–4.5 | 3.5–6 | 0.4–1.5 | 2–100 | 2.2–100 | 0.041 | 1.039 | 1.013 | +0.48 | 0.046 | 1.034 | 1.005 | +0.44 |
| 92 | J214 | 0.85–4.5 | 3.5–6 | 1.5–100 | 2–100 | 1.4–2.2 | 0.062 | 1.016 | 0.991 | +0.17 | 0.060 | 1.018 | 0.990 | +0.19 |
| 93 | J215 | 0.85–4.5 | 3.5–6 | 1.5–100 | 2–100 | 2.2–100 | 0.050 | 1.029 | 1.004 | +0.37 | 0.051 | 1.028 | 1.000 | +0.36 |
| 94 | J216 | 0.85–4.5 | 6–60 | 0–0.4 | 0–1.2 | 0–1.4 | 0.000 | 1.083 | 1.056 | +0.52 | 0.000 | 1.083 | 1.054 | +0.60 |
| 95 | J219 | 0.85–4.5 | 6–60 | 0–0.4 | 1.2–2 | 0–1.4 | 0.004 | 1.079 | 1.052 | +0.65 | 0.005 | 1.077 | 1.048 | +0.68 |
| 96 | J220 | 0.85–4.5 | 6–60 | 0–0.4 | 1.2–2 | 1.4–2.2 | 0.003 | 1.080 | 1.053 | +0.92 | 0.016 | 1.066 | 1.036 | +0.80 |
| 97 | J222 | 0.85–4.5 | 6–60 | 0–0.4 | 2–100 | 0–1.4 | 0.000 | 1.083 | 1.056 | +0.58 | 0.000 | 1.083 | 1.054 | +0.70 |
| 98 | J223 | 0.85–4.5 | 6–60 | 0–0.4 | 2–100 | 1.4–2.2 | 0.019 | 1.063 | 1.036 | +0.68 | 0.043 | 1.037 | 1.008 | +0.41 |
| 99 | J224 | 0.85–4.5 | 6–60 | 0–0.4 | 2–100 | 2.2–100 | 0.014 | 1.069 | 1.042 | +0.47 | 0.049 | 1.030 | 1.002 | +0.27 |
| 100 | J225 | 0.85–4.5 | 6–60 | 0.4–1.5 | 0–1.2 | 0–1.4 | 0.022 | 1.059 | 1.033 | +0.47 | 0.017 | 1.064 | 1.035 | +0.53 |
| 101 | J228 | 0.85–4.5 | 6–60 | 0.4–1.5 | 1.2–2 | 0–1.4 | 0.081 | 0.995 | 0.970 | -0.04 | 0.080 | 0.997 | 0.970 | -0.02 |
| 102 | J229 | 0.85–4.5 | 6–60 | 0.4–1.5 | 1.2–2 | 1.4–2.2 | 0.059 | 1.019 | 0.994 | +0.19 | 0.050 | 1.029 | 1.001 | +0.29 |
| 103 | J231 | 0.85–4.5 | 6–60 | 0.4–1.5 | 2–100 | 0–1.4 | 0.065 | 1.013 | 0.988 | +0.10 | 0.066 | 1.012 | 0.984 | +0.09 |
| 104 | J232 | 0.85–4.5 | 6–60 | 0.4–1.5 | 2–100 | 1.4–2.2 | 0.026 | 1.056 | 1.029 | +0.59 | 0.028 | 1.054 | 1.025 | +0.56 |
| 105 | J233 | 0.85–4.5 | 6–60 | 0.4–1.5 | 2–100 | 2.2–100 | 0.038 | 1.042 | 1.016 | +0.40 | 0.036 | 1.045 | 1.016 | +0.42 |
| 106 | J240 | 0.85–4.5 | 6–60 | 1.5–100 | 2–100 | 0–1.4 | 0.081 | 0.996 | 0.971 | -0.03 | 0.087 | 0.989 | 0.962 | -0.08 |
| 107 | J241 | 0.85–4.5 | 6–60 | 1.5–100 | 2–100 | 1.4–2.2 | 0.059 | 1.019 | 0.994 | +0.22 | 0.065 | 1.013 | 0.985 | +0.15 |
| 108 | J242 | 0.85–4.5 | 6–60 | 1.5–100 | 2–100 | 2.2–100 | 0.057 | 1.022 | 0.997 | +0.17 | 0.049 | 1.031 | 1.002 | +0.23 |
