# Does the 2D covariance cover the playlist spread? (2026-10-14)

**Answer: PARTLY COVERED.**

The quoted 2D covariance is VL175: central value E_U, 205 cells. It is compared here with three shifts:
- the J36 mix error;
- the bias on the combined result if one block of playlists is mis-modelled;
- the shift against a 1A–1E reference.

| shift | bin by bin | with correlations |
|---|---|---|
| J36 | covered | covered |
| 1N–1P bias | covered | covered |
| 1G–1M bias | covered | covered in p_T; **not covered in p_∥ shape** |
| 1A–1E-reference shift | covered | covered in p_T; **not covered in p_∥ shape** |

No band reproduces either block as a playlist difference. The per-playlist values stay inconsistent after the bands
are added.

**CITABLE FOR:**
- per-band and total fractional uncertainty of VL175, per cell and per marginal bin (§1);
- the size of each shift against VL175, bin by bin and with the correlations, at the stated mappings (§2);
- which bands can and cannot make the block shapes, at reco level and in the unfolded universe outputs (§3);
- the per-playlist consistency χ² of the proxy total, with and without the bands (§4);
- the corrected location of the 1G–1M step, 8 GeV/c (§2.1).

**NOT CITABLE FOR:**
- an unfolded or OmniFold per-playlist result. The shifts are reco-level proxy ratios placed on true-variable cells;
- which block is right, or the cause of either block;
- the full-2D χ² values as tests. The 205-cell matrix has condition number 9.1e11, so use the marginal χ² values;
- a covariance change, a new band, or a paper change.

| field | content |
|---|---|
| `Context` | It answers the question that [`../REPORT.md`](../REPORT.md) left open: does the 2D systematic covariance already cover the playlist spread? That report is at `0b387886`, read at `ad0b19e8`. Joseph approved this check on 2026-10-14: "yes you can do the playlist spread check". Under [`../../../../DECISION-20261014-joseph-2d-endpoint-and-open-items.md`](../../../../DECISION-20261014-joseph-2d-endpoint-and-open-items.md) §2, a result that is not covered goes to Joseph as a construction question before Stage F |
| `Who` | Measured by a Claude Opus 5.5 subagent of the paper-tighten lane (director). The director checked the following on 2026-10-14. **Inputs:** VL175's per-cell median 6.0898 %, integral 4.230 %, and p_∥ and p_T marginal medians 4.843 % and 5.310 % (`VALIDATION_LEDGER.md`, row VL175). **Step location:** re-read from `../outputs/ref_shape.json`. **Independent recomputation of the p_∥ marginal χ²** from `work_cov.npz`, with the director's own projection and shift construction: bias s_B × (q_pz − 1), with the proxy marginal mapped by bin centre. It reproduced all 16 p_∥ marginal σ values exactly. It gave χ² = 24.8 for 1G–1M, against the subagent's 25.6 (`sep`), and 2.1 for 1N–1P, against 1.9. The director wrote this REPORT from the subagent's text |
| `Compute` | No Slurm job; 0 node-h. Login node `login29` only. The largest single process used 194 CPU-s, and all processes together about 20 CPU-min (`outputs/compute_record.json`). Scratch: `/pscratch/sd/j/josephrb/tmp-playlist-coverage-20261014/`, which includes the director's check in `director/` |
| `Evidence` | [`scripts/`](scripts/) and [`outputs/`](outputs/). `coverage.txt`/`.json` hold Q1–Q3 at the unfolded level. `reco_universes.txt`/`.json` hold Q3 at reco level and Q4. `cov_controls.json` holds the input hashes and controls. The text outputs are identical when the scripts run on the cluster and locally. Code is cited at `ad0b19e8`. The work files `work_cov.npz`, `work_proxy.npz` and `work_uni*/` are on cluster scratch only, since `.npz` is gitignored. The driver `run_universe_samples.sh` is also on scratch only |

## 1. The quoted covariance and its bands

**Which covariance is quoted.** VL175 has been the quoted 2D covariance since 2026-10-12 (`VALIDATION_LEDGER.md:19,23`;
`docs/publication/DECISION-20261012-joseph-adopt-2d-c04-repair.md`; [`../../c04-repair/REPORT.md`](../../c04-repair/REPORT.md)).
It is built in three steps:
1. start from the VL172 rollup;
2. rebuild two blocks: Flux, now MAT-weighted, and Muon_Energy_MINOS, now divided by its own flux;
3. add the VL170 bootstrap and C_ML.

**Where it comes from.**
- The chain is described in `2d-unfolding/2D_OMNIFOLD_REFERENCE.md:236-259`.
- The universe files come from `sbatch_unfold_2d_MEFHC_5iter_universes_full.sh`, which runs the producer
  `unfold_2d_omnifold_unbinned.py` (sha256 `74a4ed69…7d56`, re-measured). Its universe swap is at `:642-662`.

**Inputs.** All sha256 values were re-measured and match their pins:
- the rollup `/pscratch/sd/j/josephrb/2d-closeout-c04repair-20261012/build/uq_universe_covariance_c04x01.root`
  (`da92c5d2…`);
- `uq_covariance_ml.root` (`3b6b48ec…`);
- `2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root` (`4f5a1b6d…`);
- 187 unfolded universe outputs in `universe_sweep_fluxfix/`, with Muon_Energy_MINOS taken from the c04 rescale.

**Controls.**
- The block-sum per-cell median is 6.089795 %, against 6.0898 % for VL175.
- The Flux block, recomputed from the 100 universes with the ν-e+IMD weights, matches exactly (max difference 0.0;
  Σw 211.01, n_eff 19.06).
- The MINOS block matches to 3.2e-17.
- The 45 blocks sum to the total to 2.1e-16.
- All 16 group medians of `fig67/EU_repaired_summary.txt` reproduce.
- Marginals use the covariance-exact projection (`uq/plot_uncertainty_fig6_7_style.py:178-218`). Groups follow
  `uq/analyze_universes.py:77-97`.

**Per-cell fractional σ [%].** The grid is 14 × 16, with 205 reported cells.

| group / band | cell median | cell max | integral | p_∥ marginal | p_T marginal |
|---|---:|---:|---:|---|---|
| Total (block sum) | 6.09 | 23.1 | 4.23 | 4.24–14.88 (median 4.84) | 4.28–7.25 (median 5.31) |
| Flux | 3.66 | 13.4 | 3.56 | 3.44–5.76 | 3.50–4.76 |
| Muon reconstruction | 3.42 | 21.3 | 1.80 | 1.84–14.37 | 1.91–4.86 |
| Models | 1.48 | 12.1 | 0.17 | 0.15–1.10 | 0.15–0.43 |
| Normalization (flat) | 1.40 | 1.40 | 1.40 | 1.40 | 1.40 |
| Hadronic response | 0.76 | 5.4 | 0.06 | 0.08–1.63 | 0.19–3.00 |
| Statistical (bootstrap) | 0.67 | 17.9 | 0.06 | 0.14–0.70 | 0.19–1.01 |
| ML | 0.17 | 1.3 | 0.005 | 0.02–0.61 | 0.03–0.11 |
| MinosEfficiency | 1.47 | 3.27 | 1.74 | 1.33–2.29 | 1.37–2.03 |
| Muon_Energy_MINOS | 2.28 | 8.95 | 0.37 | 0.10–4.97 | 0.23–3.99 |
| Muon_Energy_MINERvA | 1.29 | 20.0 | 0.28 | 0.01–13.28 | 0.26–3.23 |

Total σ by marginal bin [%]:
- p_∥, from 1.5 to 60 GeV/c: 14.88, 6.14, 5.32, 4.66, 4.53, 4.34, 4.25, 4.24, 4.78, 5.72, 6.16, 5.07, 4.40, 4.72,
  4.91, 7.67;
- p_T: 5.66, 5.15, 5.38, 5.35, 5.16, 5.26, 5.51, 4.46, 4.28, 4.48, 5.15, 6.22, 5.85, 7.25.

Every band's values are in `outputs/coverage.json` (`Q1_bands`, `Q1_groups`).

**What the band set holds and lacks.** It has 44 universe bands plus the flat 1.4 % normalization.
- It has no reconstruction or tracking-efficiency band.
- It has no separate horn or focusing component, only PPFX `Flux` (100 universes) and `BeamAngleX/Y`.
- MaNCEL, NormNCRES and EtaNCEL do not touch the CC signal.

## 2. Coverage

### 2.1 Mapping and bias definitions

- **The grids nest.** Every edge of the proxy grid is an edge of the analysis grid, and the script checks this.
- **Three mappings bracket the in-cell shape:**
  - `sep` (main): q_pT × q_p∥ / q_tot;
  - `interp`: the marginals interpolated linearly between proxy-bin centres, which smooths the step;
  - `bin`: the per-bin ratio where both samples have at least 50 data events, otherwise `sep`. It is noisy.
- **Migration is ignored.** A reco-level ratio is placed on true-variable cells.
- **The block bias (b)** in each cell is s_B × (q_B − 1). Here s_B is the block's share of the MC signal in the
  per-playlist mix. Its median is 0.294 for 1G–1M and 0.162 for 1N–1P; the data-POT shares are 0.2923 and 0.1732.
  This assumes block B alone is wrong.
- **The J36 error (a)** is the IBU production-mix to per-playlist-mix ratio minus 1, on the truth grid
  (`../outputs/mix_bias.json`).
- **The 1G–1M step is at 8 GeV/c, not 6.** The 1G–1M p_∥ ratio is 0.954–0.989 below 8 GeV/c, then 1.022–1.025 at 8–15
  GeV/c. Measured as r[8,15)/r[1.5,8) − 1, the step is +6.10 %. The earlier REPORT §2.2 put it one bin too low and has
  been corrected. Its 1N–1P description was right.

### 2.2 Results

The comparison is against the VL175 block sum. "Noise" is the mean χ² over 200 toys that fluctuate D, S and B in each
proxy bin and playlist.

| shift (mapping) | integral | p_∥ marginal | p_T marginal | cell z max | p_∥ z max | p_T z max | χ² p_∥ (16) [noise] | χ² p_T (14) [noise] | χ² 205 [noise] |
|---|---:|---|---|---:|---:|---:|---|---|---|
| (a) J36 IBU | +0.18 % | +0.09…+0.32 % | −0.03…+0.20 % | 0.07 | 0.05 | 0.04 | 0.03 | 0.01 | 2.2 |
| (b) 1G–1M, `sep` | −0.81 % | −1.40…+0.79 % | −1.13…+1.02 % | 0.37 | 0.33 | 0.25 | **25.6** [1.0] | 2.3 [0.8] | 159 [13] |
| (b) 1G–1M, `interp` | −0.82 % | −1.40…+0.77 % | −1.13…+1.02 % | 0.37 | 0.33 | 0.25 | **18.7** [0.7] | 1.7 [0.6] | 124 [9] |
| (b) 1N–1P, `sep` | +0.77 % | +0.34…+1.25 % | +0.63…+1.34 % | 0.30 | 0.25 | 0.19 | 1.9 [0.5] | 0.35 [0.4] | 18.7 [5.9] |
| (b) 1N–1P, `interp` | +0.75 % | +0.34…+1.23 % | +0.63…+1.41 % | 0.29 | 0.25 | 0.19 | 1.1 [0.3] | 0.22 [0.3] | 11.7 [4.2] |
| (c) all vs 1A–1E, `sep` | −0.13 % | −1.06…+2.00 % | −0.71…+2.27 % | 0.49 | 0.39 | 0.31 | **28.3** [3.1] | 3.0 [2.5] | 222 [38] |
| (c) all vs 1A–1E, `interp` | −0.17 % | −1.07…+1.92 % | −0.72…+2.37 % | 0.47 | 0.38 | 0.33 | **20.3** [2.2] | 3.1 [1.8] | 189 [26] |

z is |shift|/σ. With the `bin` mapping the largest cell z values are 0.94, 0.47 and 0.89.

- **Bin by bin, all three are covered.** No cell or marginal bin exceeds 1σ.
- **With correlations:**
  - J36 and 1N–1P are covered;
  - 1G–1M and the 1A–1E reference are covered in p_T but not in p_∥.
- **Where the p_∥ excess sits.** The five largest eigenmodes of the quoted p_∥ covariance have per-bin rms 0.55–4.4 %;
  the rest are 0.29 % or less. The large modes carry only 0.46–0.76 of the 18.7–28.3. The covariance allows a 4–5 %
  normalization but almost no bin-to-bin step at 8 GeV/c.
- **The p_T tail depends on the mapping.** The reference shift in the p_T tail at 2.5–4.5 GeV/c is +2.27 % with `sep`
  and +1.16 % with `bin`.

## 3. Can any band make the block shapes?

### 3.1 Unfolded level

This uses the 187 universe outputs and E_U.

- **The Flux band carries no p_∥ step.** Its step has sd 0.17 % and range −0.40 to +1.17 %. The 1G–1M step (+6.10 %)
  is 35 band-σ. Its leading eigenmode, 73 % of the variance, is flat at +3.53 %.
- **Muon_Energy_MINOS has a large step but the wrong shape.** Its step sd is 3.03 %, which puts 1G–1M at 2.0σ. But
  its universes tilt the p_∥ marginal, −5.1 % at 1.5–2 GeV/c and +3.9 % at 7–8 GeV/c, rather than stepping at 8 GeV/c.
  The best cos² against the 1G–1M shape is 0.25.
- **A broad +5 % (1N–1P), compared with each band:**

  | band | integral sd | σ needed for +5.02 % | cos² with the 1N–1P shape |
  |---|---:|---:|---:|
  | Flux | 3.56 % | 1.4 | 0.88 |
  | MinosEfficiency | 1.74 % | 2.9 | 0.77 |
  | Muon_Energy_MINOS | 0.37 % | 13.7 | n/a |
  | Muon_Energy_MINERvA | 0.28 % | 18.0 | n/a |

  The Flux match is almost entirely normalization. The MinosEfficiency shift falls with p_∥, while the 1N–1P ratio
  rises.

### 3.2 Reco level, per-playlist universe files

**The files and the sample.**
- The files `/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/runEventLoopOmniFold_<PL>_universes_full.root`
  exist (`ls -d`).
- Their data counts, CV background and POT equal the May CV inputs in all 12 playlists.
- The sample is the first 500k `mc_signal_reco` entries per playlist, which is 12–100 % of its passing signal, plus all
  background.
- Lateral universes use the shifted reco kinematics (`unfold_2d_omnifold_unbinned.py:501-527`).

**Pooled proxy.**
- Flux universes move the pooled step with sd 2.77 % (largest 8.77 %). Five flux modes fit the 1G–1M p_∥ shape with
  residual 0.12, at 3.3σ.
- Muon_Energy_MINOS fits the 1N–1P p_∥ shape, mean removed, with residual 0.28 at 0.5σ. Its normalization sd is only
  0.56 %.
- MinosEfficiency needs 3.1σ to reach +5.02 %.

**As playlist differences, every band acts alike in all playlists:**

| block / 1A–1E ratio | Flux | Muon_Energy_MINOS | all bands, quadrature | observed |
|---|---|---|---|---|
| 1G–1M total | sd 0.09 % | sd 0.08 % | 0.15 % | −2.61 % |
| 1G–1M step | sd 0.10 %, largest 0.33 % | sd 0.21 % | 0.40 % | +6.10 % |
| 1N–1P total | sd 0.03 % | n/a | 0.10 % | +5.02 % |
| 1N–1P step | n/a | n/a | 0.24 % | +1.36 % |

**What this means.**
- A flux-shape change can make a step the size of 1G–1M, but only as a shift common to all playlists, and only at reco
  level. Nothing in the band is specific to 1G–1M, and the unfolded Flux block has no p_∥ step.
- No detector band makes a broad 4–6 % shift at 1σ.

## 4. Per-playlist consistency χ²

The fit is y = ln R_p with a GLS mean, 11 dof. The per-playlist statistical error is 0.13–0.46 % from data and
0.06–0.23 % from MC. The POT-weighted rms of ln R_p is 2.54 %.

| treatment | χ²/11 | p |
|---|---:|---:|
| (i) statistics only | 1968 | ~0 |
| (ii) + every band as an identical shift in all playlists, + 1.4 % norm | 1968 | ~0 |
| (iii) + every band with its measured per-playlist response | 1266 | 1e-264 |
| (iii) without Flux | 1348 | 2e-282 |
| (v) + detector bands only, uncorrelated per playlist | 33.4 | 4.5e-4 |
| (vi) + detector bands only, correlated within run period only | 69.2 | 1.8e-10 |
| (iv) + every band uncorrelated per playlist (not physical) | 0.97 | 1.0 |

- **Case (ii) equals case (i)** by construction: a common shift cancels.
- **The playlist-dependent part of all bands is small.** It totals 0.11 % of R_p in quadrature, against the 2.54 %
  spread.
- **That part is also at the sample's noise level.** Split samples differ by up to 0.10 % per universe, so case (iii)
  is an upper estimate.
- **Not computed:** a per-bin χ² and an unfolded per-playlist χ².

## 5. Limits

- **Proxy, not unfold.** Migration would smear the 8 GeV/c step. The `interp` mapping is a partial check of this.
- **The reference is assumed.** Model (b) takes one block as wrong, and model (c) takes 1A–1E as right. The data
  cannot tell which is true.
- **Conditioning.** The full-2D matrix has condition number 9.1e11. The marginal matrices have 5.7e6 (p_∥) and 2.0e6
  (p_T).
- **The p_∥ verdict rests on fine-shape modes** with per-bin rms 0.06–0.29 %. Their own accuracy was not tested.
- **VL175 still carries the open Stage B defects** (KI 93/94, C05a, G1, G2, P07, KI 85). A later covariance may change
  §1–§2.
- **The universe sample is not random.** It is the first rows of each file.
- **Mixed checkouts.** The cluster checkout's HEAD is `32e403b8`. Code was cited from `ad0b19e8`, and only
  hash-checked data products were read on the cluster.
- **Two reruns.** `export_cov.py` failed after writing (a JSON bool) and `proxy_hists.py` failed on a Lustre write
  (errno 108). Both were rerun (`outputs/compute_record.json`).
