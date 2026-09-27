# s5p independent review, round 1 (Stage-2 exit and amendment 5)

**CITABLE FOR:** the independent reviewer's findings on the Stage-2 exit and the amendment-5 joint-test design,
verbatim. **NOT CITABLE FOR:** any repair, disposition or grade; the campaign's responses are in the repair
amendment and the state file.

- reviewer: independent session (general-purpose agent, no authorship of the reviewed code or records), read-only
  worktree `../MINERvA-OmniFold-s5p-review1` detached at `75746779`; left clean (`git status --porcelain` empty)
- scratch: `/pscratch/sd/j/josephrb/s5p-20260926/review1/` (scripts and one output file listed below; nothing
  submitted to Slurm)
- received 2026-09-27; F1 re-measured by the campaign before acting (GENIE-CV / MnvTune p∥ ratio 0.62 (8–9),
  0.14 (10–15), 0.09 (15–20), 0.04 (20–40 GeV/c); flux file bin widths 0.1–10 GeV with density-like contents;
  `make_flux_for_genie.py` copies `flux_E_unweighted` contents; `run_gevgen.sh` generates `-e 0,50`;
  `genie_to_xsec3d.flux_avg_sigma_cc_per_nucleon` sums contents without widths); `KNOWN_ISSUES.md` 83

## Report (verbatim)

# s5p Stage-2 / amendment-5 independent review (reviewer 1, worktree `75746779`)

The Stage-2 numbers reproduce and the measurement-branch disposition holds. The joint-test design is not ready for production ensembles: three of its five null predictions carry a flux-input defect, and its size calibration cannot detect the known differences between the real-data and pseudo-experiment processes.

## Verdict table

| # | Item | Verdict |
|---|---|---|
| 1a | Study N (rounding spread, paired-replica consistency, J cells) | CONFIRMED |
| 1b | Study C (pull SDs, single vs mean-of-six σ) | CONFIRMED (the cause is overstated: LOW) |
| 1c | Study P (envelope h) | CONFIRMED (not in the receipt: LOW) |
| 1d | Study K (noise-free T2 proxy) | CONFIRMED |
| 2 | Measurement-branch disposition | CONFIRMED, rules applied mechanically (three LOW caveats) |
| 3/4 | Generator predictions built from a mis-sampled flux | **FINDING, HIGH** |
| 3 | Null truth uses MnvTune's within-cell shapes | **FINDING, HIGH (magnitude unmeasured)** |
| 3 | Size check cannot detect data-vs-pseudo differences, and has low assurance | FINDING, MEDIUM |
| 3 | Half-MC pseudo bias differs from the full-MC bias | FINDING, MEDIUM |
| 3 | Ledoit-Wolf shrinkage not standardized (code contradicts its docstring) | FINDING, MEDIUM (costs power only) |
| 3 | Power definition vs Holm; response-model conditioning | FINDING, LOW–MEDIUM |
| 3 | B = 1999 meets T7; dropped shape cell; −eps treatment; GiBUU domain | CONFIRMED (details below) |

## 1. Reproduction with my own code

I used my own cell maps: edges from the input npz, J cells from the s5c contract, H2 support flags from the Stage-1 receipt.

- **(a) Study N, data, J cells:**
  - Rounding spread median 0.228% (max 0.60%); bootstrap σ 0.368%.
  - Consistency ratio 1.018 (bootstrap 68% range 0.98–1.09); bootstrap variance ≥ rounding variance in 100% of cells; absorption 0.37.
  - H2: 0.176% / 0.96. EW: 0.152% / 1.05.
  - The jitter noise is nearly uncorrelated across cells (median |corr| 0.20 against 0.18 expected by chance at n = 20), so the diagonal rounding surrogate is adequate.
- **(b) Study C, 160 nominal experiments:**

  | functional | pull SD, single σ | pull SD, mean-of-six σ |
  |---|---:|---:|
  | EW41 | 1.406 | 1.188 |
  | J206 | 1.444 | 1.065 |
  | J215 | 1.522 | 1.079 |

  The exact numbers match the receipt.
- **(c) Study P, reference d0 (d0 equals CV to 2e-16 at cell level):**
  - h median: J 12.02%, H2 9.60%, EW 13.44%.
  - Dominant vertex D1 in 60/109, 13/27 and 29/39 cells.
- **(d) Study K:**

  | truth | k | J | H2 |
  |---|---:|---:|---:|
  | W3 | 5 | 0.626 | 0.311 |
  | W3 | 20 | 0.650 | 0.398 |
  | GiBUU | 5 | 0.455 | 0.314 |
  | GiBUU | 20 | 0.410 | 0.244 |

  My J integrals match `fn_true`/`fn_push` to 1e-15.

## 2. Disposition (Q2)

No configuration 2 or 3, RD1/RD2 failing T2 and RD3 failing T1 all follow mechanically from the frozen rules. I found no weakening or strengthening. The disposition survives all of the following:

- **T2 on J and H2 rests on W3 alone.** W3's recovery ratio is above 0.25 at every k (0.311 on H2 at k = 5), independent of h and of the q3 choice.
- **RD3's T1 failure is robust.** Without D1, EW h is still 9.9% median. The adopted C_EW total σ is already 8.4%.

LOW caveats:

- **Provenance.** The record says every number comes from the receipt or forecast, but the h values (12.0 / 9.6 / 13.4%) are in neither.
- **T2 list.** T2 was evaluated through M's alternative list (the unanchored q3 at a = 0.3, no W2). Amendment 1's T2 list names W2 and the anchored D5 instead.
- **"Slightly conservative bound" is too strong.** I checked D1/D2 linearity post-repair myself (the receipt has none):
  - correlation 0.93–0.97 and slope 0.94–1.26;
  - but per-cell |shift + bias| / |bias| median is 0.30–0.52, and |shift| ≥ |bias| in only 52–78% of cells;
  - D4 on H2 has slope 0.66;
  - the data truth being inside the vertex hull is assumed, not shown.

  h is adequate as evidence that T1/T2 fail, but not as a per-cell bias bound.
- **Study C cause.**
  - The experiment-to-experiment σ CV of 13.9% is mostly replica noise: about 10.7% is expected from 40–100 replicas alone.
  - EW41 stays under-covered with every one of the six σ estimates (pull SD 1.06–1.41, mean 1.19, 3.4 SE above 1), right at T4's "material" 19% level.
  - Also, the real-data interval uses one experiment's own σ, and that construction was not checked.

## 3–4. Findings

**F1 (HIGH, result-changing): the GENIE CV, GENIE MEC and NuWro predictions sample the flux wrongly.**

- **Evidence that the flux file stores densities.** `make_flux_for_genie.py` copies MINERvA's `flux_E_unweighted` bin contents into a variable-width TH1D. The contents are continuous across width changes (for example 7.15e-7 in a 0.5 GeV bin, then 6.61e-7 in the next 1 GeV bin at 20 GeV), so they are densities.
- **How that corrupts the predictions.** Both gevgen/NuWro (beam_type 5) and `flux_avg_sigma_cc_per_nucleon` weight by the raw bin content, so wide high-energy bins are under-weighted by their width.
- **Generator/MnvTune ratio collapses at high p∥.** The ratio of p∥ spectra falls to:

  | p∥ (GeV/c) | ratio |
  |---|---:|
  | 9–10 | 0.30 |
  | 10–15 | 0.13 |
  | 20–40 | 0.04 |

  GiBUU, which reads its own flux file, stays at 0.82–0.86 up to 10 GeV/c.
- **Width reweighting restores it.** Weighting the GENIE events by their flux-bin width brings the ratio back to 0.79 (10–15) and 0.67 (20–40). The rest is plausibly the 50 GeV generation cap (in `run_gevgen.sh`) and the use of the non-PPFX flux.
- **Effect on the nulls.**
  - Supported J cells with p∥ ≥ 6 carry 28% of the cross section; there these three generators sit at 0.55–0.61 of MnvTune.
  - Cell (2,2,2,2,2), with 7.2% of the cross section, has ρ = 0.09–0.10.
  - These tests would reject an input artefact.
- **Knock-on effects.**
  - GENIE/MnvTune is 0.51 at E_avail > 3 GeV, which inflates the D1 GiBUU/GENIE vertex that dominates h.
  - It probably contributes to the paper's "generators 19–28% below data" and "every generator below the data at high E_avail/W" statements. The committed 3D and (E_avail, W) predictions share the inputs (the 5D build reproduces them bitwise).
  - The ratio-based P1–P3 largely cancel it.
- **Caveat.** I inferred GENIE's content-proportional sampling from behaviour and did not read its source. The p∥ restoration test is strong evidence.
- **Disposition:** file a KNOWN_ISSUE. Regenerate or reweight GENIE/NuWro with density × width, PPFX flux and no 50 GeV cap, and re-derive gen5d, the ratios and D1 before any calibration ensemble. Re-examine VL35–VL38.

**F2 (HIGH, unmeasured): the null truth is MnvTune reweighted per J cell, so within-cell shapes are MnvTune's.**

- H0(G) as stated is composite over within-cell shapes, and R's J-cell bias depends strongly on the fine truth:
  - recovery varies 0.29–0.63 across truths;
  - joint purity median is 0.14.
- NuWro/GiBUU differ from the null's within-cell shape by a total-variation distance of 0.12/0.12 median (p90 0.31/0.27). The expected bias mismatch is far above the 0.2–0.4% statistical σ.
- **Disposition:** before production, run noise-free k = 5 unfolds at the fine-ratio truth G/MnvTune and at the coarse-ratio truth (about 0.2 node-h each) and compare J-cell outputs in the metric. Prefer a null built on the generator's own fine shape, or narrow the claim.

**F3 (MEDIUM): the size check is uninformative and has low assurance.**

- Calibration and validation ensembles are iid draws from the same pseudo process, so the rank test's size is exactly 0.05 by construction. The check cannot see any data-vs-pseudo difference, despite amendment 5 citing exactly that non-exchangeability.
- At true size 0.05 and n = 300, P(upper bound ≤ 0.08) = 0.67 per check and about 0.2 for all four checks. T6's "simultaneous" bound (Bonferroni) gives 0.016.
- Amendment 5 silently drops "simultaneous".
- **Disposition:** re-specify the check. For example, use n ≥ ~450 per check, or replace it with process-sensitivity checks (F2, F4).

**F4 (MEDIUM): the pseudo process has a different bias from the full-MC process.**

- s5e pseudo-ensemble mean residuals against the full-MC asimov bias at k = 5:

  | truth | slope | median difference | χ²/cell |
  |---|---:|---:|---:|
  | W3 | 1.004 | 0.12% | 5.6 |
  | GiBUU | 1.006 | 0.20% | 17.8 |

- The difference is coherent and about 0.3–0.5 σ_stat per cell.
- It mixes half-MC, background/refinement and noise effects, so "conservative in that respect" is not established.

**F5 (MEDIUM, power only): `s5p_joint.ledoit_wolf` does not standardize.**

- The docstring says "on standardized data", but the code shrinks toward (mean variance) × I while cell variances span a factor of 1.5e5.
- On the 160 nominal experiments: diagonal inflation median 2.2×, 24% of cells inflated > 10× (max 251×).
- The non-centrality of a uniform ±3% shift drops 2.9× against the standardized version.
- **Disposition:** fix it before `build-v`.

**F6 (LOW–MEDIUM):**

- **Power vs the decision rule.** Power is defined at raw α = 0.05, but rejection claims use Holm (first step at 0.005). Report power at the Holm thresholds too.
- **Response-model conditioning.** GENIE response-model (efficiency/migration) variations are excluded because "the null fixes the signal physics". The null fixes only the 5D truth, so the tests are conditional on MnvTune's per-event response. Add response-only universe reweights or state the condition in every claim.
- **Lateral surrogates.** The Δ_b are built from data endpoints that each carry about 0.23% rounding noise. This inflates the null (conservative, costs power).

**Confirmed:**

- **B = 1999 meets T7.** An exact Clopper-Pearson scan over k shows no violations; at p = 0.01 the interval is [0.0057, 0.0148]. Holm thresholds between 0.005 and 0.0083 fall in the one-sided-bound zone. The procedure stays valid, but the "undetermined" rule should name those thresholds.
- **Dropped shape cell.** The statistic is invariant to which cell is dropped (numerical replica check, rank n−1).
- **−eps and metric.** Simulated residuals get −eps and the observed does not, with the same fixed W: correct. For the MnvTune null, eps is correlated with the prior in reality; treating it as independent is conservative.
- **GiBUU domain.** Selecting pz index ≤ 1 is correct. E_ν > 20 GeV contributes about 0.8% of the pz < 6 cross section (width-fixed GENIE), concentrated in the high-ν cells (LOW).
- **P1–P3** lie outside the MnvTune null, which is the only null their power is measured against.

## Scratch created (`/pscratch/sd/j/josephrb/s5p-20260926/review1/`)

- **Scripts:** `r1_cells.py`, `r1_stage2.py`, `r1_t7.py`, `r1_size.py`, `r1_lw.py`, `r1_within.py`, `r1_eavail.py`, `r1_plin.py`, `r1_shape_check.py`, `r1_genie_enu.py`, `r1_flux.py`, `r1_flux2.py`, `r1_genie_fix.py`.
- **Output:** `r1_stage2_out.json`.
- **Input copies:** `stage1_inspect.json`, `s5c_contract.json`, `s5p_stage1_inspect.py` (sha256 matches the receipt), plus a `__pycache__/`.

Nothing was submitted to Slurm and no repository was edited. `git -C /Users/josephbailey/local-research/MINERvA-OmniFold-s5p-review1 status --porcelain` printed nothing; HEAD is `75746779`.