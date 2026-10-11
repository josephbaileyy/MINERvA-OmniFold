# High-E_avail / high-W discrepancies and inelastic physics: research memo

**Date 2026-10-11. Owner: this session (inelastic-high-region lane). Base: remote `main` `3892e769`. Frozen plan
[`PLAN.md`](PLAN.md), committed as `60d1405f` before any reduction, with two descriptive amendments (§8 there).
Reviewed once (fresh, read-only) with one correction pass applied; see [`REVIEW.md`](REVIEW.md). This memo authorizes
nothing, adopts nothing and contacted no one. Joseph owns the scientific decision.**

Evidence labels used throughout: **[M]** measured here or in a cited committed receipt; **[D]** deduced
analytically from [M] and stated definitions; **[A]** assumption; **[L]** literature, opened by the owner unless
marked *(agent-read)*, meaning the delegated literature agent read it and the owner did not re-open it.

## 1. Verdict: INCONCLUSIVE under the frozen rule; GO not reached

**Supported statement.**
- After separating rate, energy coverage, detector response and estimator effects, the high-E_avail / high-W
  region (A ≡ E_avail ≥ 0.8 GeV, W ≥ 1.8 GeV; "region C") carries a small normalization-removed residual against
  the complete-support external generators **[M]**:
  - ρ_C − 1 = +2.85% (GENIE 2.12.10 CV), +6.65% (GENIE + MEC) and +0.62% (NuWro 21.09).
  - A coherent ±4% recoil-response scale moves ρ_C by 3.7–4.0%.
- **No single decomposition factor holds two thirds of the residual for any of the three [M].**
  - The muon-shape step is the largest common component: +1.7% to +2.9%, with response sensitivity ±0.2%.
  - The final-state-partition step is comparable for GENIE CV (+0.8% against a net +2.8%) and larger than the net
    for NuWro (+1.7% against +0.6%).
- The residual reverses sign inside C: −2.7% in the non-overflow cells and +9.4% in the overflow cells
  (GENIE CV, linear) **[M]**.

**Frozen rule outcome (PLAN §6).** Inputs as the plan defines them **[M]**:
- S_C = 0.040, the largest linear ±4% shift of ρ_C over G (0.038–0.040). The target effect is 0.0025, so the response
  shift sets S_C.
- B_C = 0.031, the s5n regularization aggregate (0.025) plus the s5c background aggregate (0.007).
- **NO-GO is not reached**, because GENIE + MEC's 0.067 exceeds S_C (1.7×).
- **GO is not reached** on any criterion:
  - magnitude: 0.029 and 0.006 < 2 S_C = 0.079;
  - localization;
  - candidate.
- The result is **INCONCLUSIVE**. The verdict is the same with the pre-review values (S_C = 0.037, B_C = 0.025).

**Bounded recommendation.**
1. The present evidence does not motivate developing or fitting a new inelastic model from this region. That is a
   recommendation, not the rule outcome.
2. The only independently constrained existing inelastic change found is the GENIE v3 H/D tune G18_02a_02_11b.
   - It has the right sign at 1.4 ≤ W < 1.8 GeV. That band holds the largest normalization-independent feature,
     robust to the one coherent response scale tested.
   - A first-order emulation on GENIE 2.12 events does not pass our Δ-region check (§6.1). It lowers the 1.1–1.4 GeV
     prediction by 24% where GENIE CV already matches, and it raises the rate deficit.
   - The emulation applies v3 parameters to GENIE 2.12's Rein–Sehgal resonances (v3 uses Berger–Sehgal). It also
     omits W_cut and M_A^RES. **It is not a test of the tune itself.**
3. The cheapest decision-relevant next step is not a model. It is a species-dependent recoil-response family
   propagated on the data side, costed in §8.
4. GO would have authorized no compute. INCONCLUSIVE authorizes none either.

**Post-hoc observation, outside the rule [D].** GENIE + MEC's larger ρ_C comes from MEC's added strength in the
normalizing total: +4.0% of the total, 90% of it at A < 0.8 (review). Its corner ratio (1.139) equals GENIE CV's
(1.142). This observation is recorded for interpretation. It does not change the rule's inputs.

**What this memo does not claim.** It assigns no significance. It does not use the adopted 5D covariance, any
quarantined significance or any s5p p-value as a test of a mechanism. It does not read generator channel labels as
observed mechanisms. It does not claim that flux explains the rate difference.

## 2. Scope, roles, budget and baseline

- **Roles.** Owner: this session. Literature: one delegated read-only web agent. Review: one fresh read-only
  subagent at the frozen commit, followed by one correction pass ([`REVIEW.md`](REVIEW.md)). Same model family;
  this is not independent domain validation.
- **Budget [M].** Aggregate cap 7,200 core-s, enforced by [`code/budget.py`](code/budget.py); ledger
  [`logs/budget_ledger.jsonl`](logs/budget_ledger.jsonl). Owner reductions used **1,092.1 core-s**, of which
  **900 core-s** is one crashed cluster run charged its full cap by the conservative rule (§10). After review and the correction pass the ledger total is **1,100.9 core-s of 7,200**: the owner
  1,093.6 (including a 1.5 core-s digest verification in the correction pass) and the reviewer 7.3 ([`REVIEW.md`](REVIEW.md)).
- **Not done.** No GPU, generation, detector simulation, fit, unfolding, covariance, adoption or contact.
- **Baseline.**
  - Remote `main` `3892e769` was fetched and checked out in the isolated worktree on branch
    `study/inelastic-high-region-20261011`.
  - The predecessor memo (`docs/research/MINERVA-MODEL-IMPROVEMENT-MEMO-20261011.md`, local, uncommitted) is preserved
    byte-identical (SHA-256 `4f3da639…`).
  - The Valencia feasibility pilot (`study/valencia-feasibility-20261011`, `d75987e1`) tested the low-A multinucleon
    predecessor only. It is not re-run and does not bear on region C. Its corrected model has no public implementation.

## 3. What is compared (pinned)

| Label | Version / configuration | Target | Flux and energy support | Role |
|---|---|---|---|---|
| Data | Production 5D LightGBM, 5 iterations, purity background; `xsec_5d_MEFHC_5iter_lgbm.root` `630306e2…` | tracker CH (per nucleon) | ν-e-constrained PPFX CV, data-POT-weighted over 12 ME FHC playlists (`README-gen5d-fluxfix.md`: `flux_reweighter(..., nuE=true, 100)`) | measured central value; no covariance used |
| Tune v1 | GENIE 2.12.6 + MINERvA Tune v1 (analysis MC truth, `w_truth`); `mnvtune_v1_xsec5d.npz` `bf7bd278…` | detector MC | analysis flux | **unfolding prior**; descriptive map only |
| GENIE CV | GENIE 2.12.10 Default (no MEC events); `genie_cv_xsec5d_full.npz` `cfa42210…` | C12/H1 mass 0.9225/0.0775 | flux-reweighted 0–50 GeV + 50–100 GeV supplement | external |
| GENIE + MEC | same + Valencia 2011 MEC (`Default+CCMEC`), no MINERvA enhancement; `c179855d…` | as above | as above | external |
| NuWro | 21.09 (`v21_09_1`), installation-default physics, `res_dis_cut` 1.6 GeV *(agent-read)*; `475a2871…` | C12 | 0.5–50 + 50–100 GeV supplement | external |
| GiBUU | 2019 jobcard (`DIScutW1/W2 = 1.55/1.65` GeV, `includeDIS = T`); `48917692…` | C12 | **E_ν ≤ 20 GeV only** | external, support-limited |

The signal is inclusive ν_μ CC, θ_μ < 20°, 1.5 < p_∥ < 60 GeV/c, p_T < 4.5 GeV/c, with no hadron veto. E_ν > 100 GeV
is absent from every prediction **[M]** (receipts). The data's truth W uses the struck-nucleon mass. The external
products use a fixed M_n. That difference moves 16 of 68,124 supplement events across a W edge **[M]**
(gen5d meta).

## 4. Question 1: what remains after separating rate, shape and coverage

### 4.1 Controls [M]

`code/reduce_r1.py` reproduces, to ≤ 2×10⁻¹⁵, every one of these:
- the released (A,W) arrays (`fig_arrays.npz` `72394a2b…`);
- VL156 (corner 1.142 / 1.139 / 1.160 / 1.607) and VL157 (totals);
- the paper's Tune v1 shares: 67.215% of the positive cell-integrated difference at A ≥ 0.8; 83.172% of that at
  W ≥ 1.8; 21.947% in the single catch cell EW41.

The data total is 3.06993×10⁻³⁸ and the corner 1.34975×10⁻³⁸ cm²/nucleon. **The corner is 44.0% of the measured
cross section, not a sparse tail [M].**

### 4.2 Rate, corner, intermediate W [M]

ρ_X = R_X / R_total, where R_X is data/prediction over X. M is the intermediate-W band 1.4 ≤ W < 1.8 GeV.

| Prediction | R_total | R_C | ρ_C | R_M | ρ_M | R_C/R_notC | f_C (pred) | MC rel. err. C |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Tune v1 (prior) | 1.1346 | 1.1911 | 1.0497 | 1.0056 | 0.8863 | 1.089 | 0.419 | 0.03% |
| GENIE CV | 1.1105 | 1.1421 | 1.0285 | 0.9142 | 0.8232 | 1.051 | 0.428 | 0.38% |
| GENIE + MEC | 1.0676 | 1.1386 | 1.0665 | 0.8945 | 0.8379 | 1.119 | 0.412 | 0.39% |
| NuWro | 1.1529 | 1.1601 | 1.0062 | 1.1146 | 0.9667 | 1.011 | 0.437 | 0.34% |
| GiBUU (≤ 20 GeV) | 1.3859 | 1.6070 | 1.1595 | 1.3739 | 0.9913 | 1.285 | 0.379 | 0.28% |

**The rate.**
- **[M]** The rate difference is the dominant effect: R_total − 1 = 7–15% for the complete-support predictions.
- **[M]** The published 2D measurement, which involves no hadronic axis, already shows it against Tune v1.
  Released `paper_v` / `tune_v1_v` gives **1.118** overall; this analysis's 2D gives 1.130 (ours/paper 1.011).
  The ratio rises with p_T. The normalization-removed ρ goes from 0.74 at p_T < 0.07 GeV/c (0.84 at 0.07–0.15) to
  1.10 at 1.25–1.5 GeV/c, and is 1.07 for p_T > 0.85 GeV/c, where paper/Tune v1 = 1.195
  (`code/a1b_published_rate.py`).
- **[D]** Normalizing shapes removes this rate by construction. That is a diagnostic. It does not show that flux
  explains the rate.
- **[M]** The analysis flux is already the ν-e-constrained flux, and data and predictions share it.
- **[M]/[L]** GENIE 2.12.10's own splines give σ_CC/E per isoscalar C12 nucleon of 0.718 / 0.703 / 0.693 / 0.690
  ×10⁻³⁸ cm²/GeV at 6.5 / 10 / 16 / 20 GeV (`r5_genie_events.json`). World data:
  - NOMAD Table 3 (arXiv:0711.1183): 0.763 ± 0.038 (6.5), 0.716 ± 0.034 (9.5), 0.705 ± 0.025 (11.5),
    0.698 ± 0.025 (16.2);
  - MINOS Table III (arXiv:0910.2201): 0.708 ± 0.032 (5.89), 0.708 ± 0.020 (16.42), 0.689 ± 0.016 (19.87).
- **[D]** GENIE therefore matches world inclusive σ/E within 1–2% above 9 GeV. At 6–6.5 GeV the two data sets
  bracket it: GENIE is 5.9% below NOMAD (1.2σ) and 1.4% above MINOS at 5.9 GeV. An
  ~11% increase of the inclusive inelastic cross section at 5–20 GeV would conflict with those data.
- The rate difference is therefore **not** a motivation for an inelastic change. Its origin (flux normalization,
  efficiency, target count, or the inclusive cross section below 5 GeV) is **unresolved here**.

### 4.3 Overflow cells and the support-complete domain [M]

**Overflow.** C splits into non-overflow cells (A < 3, W < 3) and overflow cells (A ≥ 3 or W ≥ 3). The overflow
cells hold 43–50% of each prediction's C.

| Prediction | R_C, non-overflow | R_C, overflow only | shape-normalized Δσ in C (10⁻⁴⁰), all / overflow | shape-normalized Δσ in M (10⁻⁴⁰) |
|---|---:|---:|---:|---:|
| Tune v1 | 1.164 | 1.221 | +6.40 / +4.65 | −7.28 |
| GENIE CV | 1.080 | 1.215 | +3.74 / +5.68 | −12.19 |
| GENIE + MEC | 1.078 | 1.210 | +8.42 / +7.74 | −10.98 |
| NuWro | 1.173 | 1.147 | +0.84 / −0.34 | −1.95 |
| GiBUU | 1.434 | 1.839 | +18.6 / +16.3 | −0.50 |

**[D]** Against GENIE, the whole normalization-independent corner surplus is in the overflow cells. The non-overflow
corner lies below the normalized prediction. In cell-integrated terms GENIE's M overshoot is 3× its corner surplus.

**Support-complete domain S20.** These are the cells whose kinematic E_ν bound is below 20 GeV:
E_ν ≤ (p_T,hi² + p_∥,hi² + m_μ²)^½ + (W_hi² + q3,hi² + m_μ²)^½ − M (§5.1). S20 holds 49.5% of the data total, but
only **6.0% of C** and 76.4% of M.

| | Tune v1 | GENIE CV | GENIE + MEC | NuWro | GiBUU |
|---|---:|---:|---:|---:|---:|
| R_total on S20 | 1.086 | 1.091 | 1.015 | 1.151 | **1.290** |
| ρ_C on S20 ∩ C | 1.077 | 0.899 | 0.982 | 0.799 | **1.381** |
| ln ρ_M on S20 | −0.123 | −0.204 | −0.161 | −0.017 | +0.123 |

**[M]** On its complete support the data still exceed GiBUU 2019 by 29% overall and 78% in S20 ∩ C, i.e. GiBUU is
22% and 44% below the data. Its
deficit is therefore **not only** the 20 GeV cap (VL161 had attributed its *extra corner* shortfall to the cap).

**[L]** *(agent-read)* GiBUU's 2025 paper (arXiv:2507.20539, §IV, Fig. 5a) introduces a two-pion background and
reports the variant without it about 30% low against MINERvA LE inclusive. Whether the 2019 jobcard lacks that
background is **not verified**: the jobcard has no such switch, and we did not inspect GiBUU's code. No other
generator's tail is used as a correction.

### 4.4 Conditional shapes [M]

| Quantity | Data | Tune v1 | GENIE CV | GENIE + MEC | NuWro | GiBUU |
|---|---:|---:|---:|---:|---:|---:|
| P(W ≥ 1.8 \| A ≥ 0.8) | 0.7556 | 0.7426 | 0.7314 | 0.7287 | 0.7552 | 0.7471 |
| P(A ≥ 0.8 \| W ≥ 1.8) | 0.9250 | 0.9182 | 0.9130 | 0.9119 | 0.9053 | 0.8853 |

Both conditionals differ from the complete-support predictions by ≤ 3.7%. Full 7×6 conditional arrays are in
`results/R1_rate_shape.json`.

## 5. Question 2: inclusive current or final-state energy partition?

### 5.1 From the weak current to the binned observables [D]

The charged-current amplitude, with J^α = V^α − A^α, is

$$\mathcal M_X=\frac{G_F V_{ud}}{\sqrt2}\,\bar u_\mu(k')\gamma_\alpha(1-\gamma_5)u_\nu(k)\,\langle X|J^\alpha(q)|A\rangle ,\qquad q=k-k'.$$

Squaring and summing over every final state gives the inclusive cross section:

$$\frac{d^2\sigma}{dE_\mu\,d\Omega_\mu}=\frac{G_F^2|V_{ud}|^2}{4\pi^2}\,\frac{|\mathbf k'|}{|\mathbf k|}\,L_{\alpha\beta}(k,k')\,W^{\alpha\beta}(\omega,|\mathbf q|),$$

$$W^{\alpha\beta}=\overline{\sum_X}\langle A|J^{\alpha\dagger}|X\rangle\langle X|J^\beta|A\rangle\,\delta^4(P_A+q-P_X).$$

Normalization conventions differ between papers. The structure, not the constants, is used below.
- **The hadronic tensor depends only on q**, for a nucleus at rest, after the final-state sum.
- **The lepton tensor separates the VV, AA and VA parts.** The antisymmetric ε^{αβρσ}k_ρk'_σ term flips sign for
  antineutrinos.
- **In DIS variables** (massless lepton, x = Q²/2Mω, y = ω/E_ν):
  d²σ/dx dy ∝ x y² F₁ + (1 − y − Mxy/2E_ν) F₂ + x y(1 − y/2) F₃.

**Analysis W and q3 are lepton-only functions.** With ω = E_ν − E_μ, Q² = −q², Q̃² = 4E_νE_μ sin²(θ/2) and
W² = M² + 2Mω − Q̃²,

$$(M+\omega)^2 = W^2 + q_3^2 - (Q^2-\tilde Q^2),\qquad Q^2-\tilde Q^2 = 2E_\nu(E_\mu-p_\mu)\cos\theta - m_\mu^2 \ \ge\ -m_\mu^2 .$$

So (q3, W) bound ω from above, ω ≤ (W² + q3² + m_μ²)^½ − M. Q² − Q̃² is not small at high y, so (q3, W) do not fix ω
exactly. With the muon cell this bounds E_ν, which is the S20 bound used above.

Two consequences follow:
1. **Truth W and q3 are inclusive variables.** At fixed incident energy, the distribution of (p_T, p_∥, q3, W) is
   fixed by the flux and the inclusive tensor W^{αβ} alone. Hadronization and transport cannot change it.
2. **Only E_avail involves the final state.** For final state f (after transport kernel K(f|X)):

$$P(A\mid E_\nu,k')=\frac{\sum_X\sum_f L_{\alpha\beta}\,\langle A|J^{\alpha\dagger}|X\rangle\langle X|J^\beta|A\rangle\,K(f\mid X)\,\delta\!\left(A-A(f)\right)}{L_{\alpha\beta}W^{\alpha\beta}} .$$

  This conditional still depends on the lepton tensor through which tensor components are weighted. "At fixed
  transfer" therefore means at fixed (E_ν, k′), which the 5D cell (m, t) approximates.

**Where the transferred energy goes.** Energy conservation with the repository's definition (Eq. 1 of
`docs/EAVAIL_DEFINITION.md`) gives

$$\omega = A + \sum_n T_n + 0.135\,N_{\pi^\pm} + E_{\rm other} + \varepsilon_B ,$$

up to the 4.6 MeV per charged pion between 135 and 139.57 MeV. Here ε_B is separation, residual excitation and recoil.

| Process | Effect on A at fixed ω | Effect on the inclusive rate |
|---|---|---|
| π⁰ → π± charge exchange, or a different hadronization charge ratio | −135 MeV per pion | none |
| More energy to neutrons, or more binding | lowers A | none |
| Changing the inclusive tensor | moves (q3, W) | moves the rate |

**The detector side.** The reconstructed A_r is 1.17 × calorimetric blob energy. ω_r for q3 and W is the separate
calibrated recoil. A response error therefore moves A_r and ω_r together. Its leading effect on W_r is
∂W_r/∂ω_r = (M − a)/W_r, with a = E_μ − p_μ cosθ (predecessor memo Eq. 3).

**Actual invariant mass versus analysis W.** For a moving, off-shell struck nucleon of four-momentum p_N:

$$W_{\rm gen}^2-W^2 = (p_N^2-M^2) + 2(E_N-M)\,\omega - 2\,\mathbf p_N\!\cdot\!\mathbf q + (\tilde Q^2-Q^2).$$

With |p_N| ≈ 0.22 GeV and q3 ≈ 2–3 GeV, the −2 p_N·q term smears W² by ~0.5–0.8 GeV², i.e. σ_W ≈ 0.15 GeV at W ≈ 2.
GENIE's own W_gen confirms this **[M]**. Of GENIE's analysis-W region C, 3.8% has W_gen in 1.4–1.7 GeV, 4.0% in
1.7–1.8 GeV and 1.1% below 1.4 GeV. Of analysis-W M, 15.7% has W_gen < 1.4 GeV, 10.0% has 1.7–1.8 and 5.2% has
1.8–2.2. The analysis W edges at 1.4/1.8 GeV are therefore not GENIE's model boundaries (W_cut = 1.7 GeV).

### 5.2 Decomposition at fixed muon kinematics and transfer [M]

Write σ(m, a, t) = σ(m) P(t|m) P(a|m,t), with m = (p_T, p_∥), t = (q3, W) and a = A. Substituting the data's
factors into each prediction one at a time splits ln R_C into four steps:
1. rate;
2. muon shape (inclusive);
3. transfer | muon (inclusive tensor × flux shape at fixed muon);
4. A | transfer (final-state partition plus response).

Code: `code/reduce_r3.py`. For the complete-support predictions and Tune v1, the two substitution orders agree to
≤ 0.0045 in every step. GiBUU differs by up to 0.022 (C_overflow partition). MC-statistical spreads from 200 `sumw2`
replicas are ≤ 0.0045 per step, and 0.0056 for GiBUU. Prediction-empty (m, t) cells hold ≤ 0.06% of the data, except GiBUU
(4.6%, its cap).

| ln ρ_C split (inclusive-first) | muon shape | transfer \| muon | A \| transfer | ln ρ_C |
|---|---:|---:|---:|---:|
| Tune v1 | +0.028 | +0.015 | +0.006 | +0.049 |
| GENIE CV | +0.017 | +0.004 | +0.008 | +0.028 |
| GENIE + MEC | +0.029 | +0.028 | +0.008 | +0.064 |
| NuWro | +0.024 | −0.034 | +0.017 | +0.006 |
| GiBUU, full domain (support-contaminated) | +0.015 | +0.094 | +0.039 | +0.148 |
| GENIE CV, non-overflow C | −0.007 | −0.035 | +0.014 | −0.028 |
| GENIE CV, overflow C | +0.044 | +0.046 | +0.001 | +0.090 |
| GENIE CV, **M** | −0.010 | **−0.184** | 0 (by construction) | **−0.195** |
| *S20 ∩ C, the plan's GiBUU domain (6% of C):* | | | | |
| Tune v1 | −0.024 | +0.081 | +0.018 | +0.074 |
| GENIE CV | −0.015 | −0.121 | +0.030 | −0.106 |
| GENIE + MEC | −0.023 | −0.034 | +0.038 | −0.019 |
| NuWro | −0.040 | −0.229 | +0.045 | −0.225 |
| GiBUU | +0.015 | +0.240 | +0.068 | +0.323 |

**Per-W profile [M]** (amendment A1-a, `code/reduce_r4b.py`). Entries are ln ρ per analysis W bin, with all A
included, and the ±4% recoil shift of the same quantity.

| W bin (GeV) | data fraction | Tune v1 | GENIE CV | NuWro | ±4% recoil shift |
|---|---:|---:|---:|---:|---|
| < 1.1 | 0.157 | +0.095 | +0.197 | +0.006 | ∓0.068 |
| 1.1–1.4 | 0.183 | −0.051 | +0.026 | +0.072 | −0.019 / +0.016 |
| 1.4–1.8 | 0.185 | −0.121 | **−0.195** | −0.034 | −0.011 / +0.009 |
| 1.8–2.2 | 0.150 | +0.031 | **−0.086** | −0.091 | −0.013 / +0.010 |
| 2.2–3 | 0.195 | −0.005 | +0.011 | −0.020 | +0.036 / −0.046 |
| ≥ 3 | 0.130 | +0.128 | +0.152 | +0.088 | +0.078 / −0.068 |

See [`results/fig_contrast_by_W.png`](results/fig_contrast_by_W.png).

**What the decomposition shows.**
1. **[M]** The partition step in full C is +0.008 to +0.017 for the complete-support predictions (Tune v1 +0.006). It
   is order-independent and positive for every prediction. No single step holds two thirds of ln ρ_C for every G.
   - For GENIE CV the steps are muon 59%, partition 27% and transfer 13%.
   - For NuWro the muon (+0.024) and partition (+0.017) steps are offset by the transfer step (−0.034).
   - On S20 ∩ C (the low-ω corner) the partition steps are larger, +0.030 to +0.045. There all complete-support ρ_C
     are below 1.
2. **[M]** The response-robust component is the **muon-shape step**: +0.017 to +0.029, with response sensitivity
   ±0.002.
   - **[D]** It is inherited from the (p_T, p_∥) distribution, which the published measurement already shows
     (§4.2: ρ rises with p_T).
   - **[L]** *(agent-read)* Ruterbories et al. (PRD 104, 092007, §VI) describe their high-p_T (> 0.85 GeV/c)
     region as "dominated by the 'True DIS' process" for p_∥ > 6 GeV/c.
   - So this component is an inclusive muon-kinematics (Q²/y) shape discrepancy that was already published, not a
     new hadronic-axis finding.
3. **[M]** The transfer step is the response-degenerate one. ±4% recoil moves ln ρ_C's transfer step by ±0.033,
   and ln ρ_W≥3 by ±0.07.
   - The W ≥ 3 excess (+0.09 to +0.15) is at most twice that shift.
   - **[M]** In GENIE, 46% of the W ≥ 3 cross section comes from E_ν ≥ 20 GeV (mean 22 GeV). The high-energy
     flux-tail *shape* is therefore a further competitor there.
4. **[M]** The largest normalization-independent feature is outside C. GENIE overshoots at 1.4–2.2 GeV (ln ρ −0.19
   and −0.09); Tune v1 overshoots at 1.4–1.8 only (−0.12). It moves only ±0.01 under the one coherent ±4% recoil scale
   tested. Species-dependent response and prior leakage into the unfolded (q3, W) were not tested.
   - **[D]** That a W-only region's residual "sits in the transfer step" holds by construction: its partition step is
     identically zero.
   NuWro shows it only at 1.8–2.2 GeV.

**Partition at fixed transfer, W ≥ 1.8 [M].** At W ≥ 1.8 the data put fewer events at A < 0.8 than GENIE CV
(A|t step −0.03 to −0.11) and Tune v1 (−0.05 to −0.09). These cells hold 3.7% of the data. The other A bins differ
by ≤ +0.012. The ±4% response shift of these entries is ±0.014–0.023. NuWro differs strongly in the opposite sense:
A|t −0.31 to −0.41 below 0.4 GeV and +0.24 at 0.8–1.5 GeV.
- **[D]** The sign means the data have *more visible energy per unit transfer* than GENIE and Tune v1. The candidate
  causes are less energy to neutrons or binding, a higher π⁰ share, or an under-modeled recoil response.
- That conclusion is subject to §5.3.

### 5.3 Response, estimator and background limits [M]

| Effect on region C | Size | Source |
|---|---:|---|
| ±4% coherent recoil scale (data side, estimator R) | Δ ln ρ_C = +0.037 / −0.038 | W2B unfolds; `reduce_r3.py` |
| Estimator R vs production estimator | Δ ln ρ_C = 0.001 | same |
| Numerical jitter floor (3 jitters) | ≤ 0.0012 | same |
| s5n C4: regularization residual under a generator-sized A-shape departure (F2), data-weighted | +2.5% over C; **+8.0% non-overflow / −3.3% overflow**; max cell 74% | `state/s5n/stage1/dev_receipt.json` |
| s5n C5: (A,W) movement induced by a q3 departure | +0.8% (−3.8% / +5.6%) | same |
| s5c D1: purity background bias, production estimator, nominal truth | +0.66% (max cell 3.9%) | `state/s5c/d1/d1_summary.json` |
| C-only vs CH per-nucleon target effect on ρ_C | −0.25% | `r5_genie_events.json` |

**[D] Partition is not testable with this estimator.**
- The estimator does not follow generator-sized A-shape departures: up to 74% residual, recorded and independently
  reproduced (VL151, KI 77).
- The real-data prior-shift envelope is 13.4% median in the (A,W) cells (VL155).
- So the 5–10% A|t differences at W ≥ 1.8 lie inside the estimator's own scale. They are pulled toward the Tune v1
  prior.
- **A measured partition discrepancy at high W is not established.**

**[D] The ±4% scale is about one standard deviation of a species-weighted response.**
- **[M]** GENIE's A in C is carried 51% by π±, 33% by π⁰/γ and 15% by protons.
- **[L]** *(agent-read)* MINERvA's toolkit default response uncertainties (`ParticleResponseDefaults.h`) are π± 5%,
  EM 3%, protons 3.5%. Test-beam agreement is "within 4%" up to 1 GeV (arXiv:1501.06431).
- A fully correlated combination is ≈ 4.1%. ±4% is a one-standard-deviation-sized probe, not a bound.
- **[M]** The test varied neither the null, nor species, nor neutrons, nor resolution (W2B §1).

### 5.4 GENIE model decomposition (model labels, not observed mechanisms) [M]

`code/r5_genie_events.py`, GENIE 2.12.10 CV, 1,006,265 events in phase space. Control: the rebuild matches the
full product to 7.6×10⁻¹³.

| Region | QE / RES / DIS / COH | E_ν mean; share ≥ 20 GeV | ⟨A⟩/⟨ω⟩ | ω shares: p / π± / π⁰+γ / n / other | H share |
|---|---|---|---:|---|---:|
| total | 0.14 / 0.26 / 0.59 / 0.01 | 8.8 GeV; 7.0% | 0.745 | 0.15 / 0.36 / 0.23 / 0.11 / 0.13 | 5.3% |
| C | 0.01 / 0.02 / 0.96 / 0.01 | 11.8; 14.3% | 0.785 | 0.12 / 0.40 / 0.26 / 0.08 / 0.10 | 5.6% |
| C, non-overflow | 0.02 / 0.03 / 0.93 / 0.01 | 7.4; 1.9% | 0.723 | 0.15 / 0.37 / 0.20 / 0.15 / 0.10 | 5.5% |
| C, overflow | 0.00 / 0.00 / 0.99 / 0.01 | 16.9; 28.9% | 0.807 | 0.11 / 0.42 / 0.28 / 0.06 / 0.10 | 5.7% |
| M | 0.00 / 0.51 / 0.47 / 0.02 | 6.7; 1.6% | 0.693 | 0.26 / 0.26 / 0.17 / 0.19 / 0.13 | 4.8% |

The "DIS" label in M includes GENIE's non-resonant background below W_cut = 1.7 GeV. The C's E_ν ≥ 20 GeV share
(14.3%) reproduces VL161 (14.30%).

## 6. Question 3: does existing physics offer a constrained test?

### 6.1 Explanation (i): inelastic rate and RES–SIS–DIS matching

**The tune [L], opened by the owner.** Tena-Vidal et al., arXiv:2104.09179v2 (PRD 104, 072009). Table VI, G18_02a:

| Parameter | 02_11b | GENIE v2 default (their Table III) |
|---|---:|---:|
| W_cut | 1.81 | 1.7 |
| R^νp_CC1π | 0.008 | 0.10 |
| R^νp_CC2π | 0.94 | 1.00 |
| R^νn_CC1π | 0.03 | 0.30 |
| R^νn_CC2π | 2.3 | 1.00 |
| S_RES | 0.84 | — |
| S_DIS | 1.06 | 1.032 |

- §VI.B: the tune gives "a decrease of both νµ and ν̄µ CC inclusive cross section in the 0.5–10 GeV region", and at
  higher energies the cross section "has barely changed".
- *(agent-read)* Every later official GENIE 3.x tune checked (AR23, AR25, N24, G24) carries these inelastic values.
- *(agent-read)* Bodek–Yang–Xu 2021 (arXiv:2108.09240, preprint) raises ν σ/E by about +2.7% at 40 GeV, mostly at
  low Q².

**First-order emulation on our events [M]** (amendment A1-d: `code/r5b_tune_emulation.py`,
`code/reduce_a1d.py`). Method:
- Reweight the existing GENIE CV events: RES × 0.84; DIS × 1.062/1.032. The 1.062 is the code value 1.062213
  *(agent-read, GENIE `CommonParam.xml`)*; Table VI gives 1.06 ± 0.01.
- Non-resonant (DIS, W_gen < 1.7) multiplicity-2 and multiplicity-3 events × R_new/R_old, by struck nucleon. Of the
  ni = 2 non-resonant events, 99.2% have exactly one primary pion.
- W_cut and RES-M_A are not reweightable and are omitted.

| | prediction × | ln ρ nominal → emulated |
|---|---:|---|
| total | 0.941 | (R_total 1.110 → 1.180) |
| W 1.1–1.4 (Δ) | **0.763** | +0.026 → **+0.235** |
| M (1.4–1.8) | 0.881 | −0.195 → −0.129 |
| W 1.8–2.2 | 1.026 | −0.086 → −0.172 |
| W ≥ 3 | 1.029 | +0.152 → +0.063 |
| C | 1.030 | +0.028 → **−0.062** |

**[D] What the emulation shows.**
- The 02_11b direction is right where GENIE overshoots (M) and at W ≥ 3.
- It is wrong at 1.8–2.2 GeV.
- It over-suppresses the Δ region by about 21%, where GENIE CV and the data agree within 3%.
- It enlarges the rate deficit.
- It flips C's contrast negative. **Our own corner and Δ data do not prefer it at first order.**
- Caveats: the omitted W_cut move (1.7 → 1.81) shifts strength from DIS into RES + NRB in 1.7–1.81 GeV, partly
  offsetting the W 1.8–2.2 change. The tune was fitted to H/D, not CH; nuclear effects on the Δ (absorption, which
  Tune v1 handles through its own ×0.57 non-resonant reduction) are outside it.
- The resonance model differs: G18_02a uses Berger–Sehgal resonances, GENIE 2.12.10 uses Rein–Sehgal. S_RES = 0.84 is
  defined relative to the v3 model, so ×0.84 applied to Rein–Sehgal is not equivalent. M_A^RES (1.09 in Table VI
  against 1.12 in Table III) is also omitted.
- **This is a sign-and-size check on GENIE 2.12 events, not a GENIE v3 prediction. It cannot falsify the tune.**

**Sign expectations and overshoot risks [D].**
- A pure DIS scale raises C, the total and, through NRB = DIS × R_ij, also W < W_cut. It therefore worsens GENIE's M
  overshoot.
- Lowering RES or R^1π fixes M but removes Δ-region strength.
- Moving W_cut redistributes strength across the 1.7–1.8 GeV edge, which W smearing (σ_W ≈ 0.15 GeV) spreads into
  both M and C.
- Muon correlation: a DIS change at high Q² raises the high-p_T muon region (the right direction for §4.2's
  ρ(p_T)). A low-Q² change (BYX) lowers ⟨p_T⟩.

### 6.2 Explanation (ii): hadronization and nuclear energy partition / FSI

- **[D]** Transport and hadronization charge ratios change A at fixed (q3, W) and leave the inclusive rate and the
  (m, t) distribution unchanged (§5.1). They can therefore only act through the A|t step.
- **[M]** In C that step is +0.6% to +1.7%, and not testable (§5.3).
- **[L]** *(agent-read)* Existing developments include:
  - the AGKY retune (arXiv:2106.05884), which fits charged multiplicities only and reports an incompatible π⁰ rise;
  - GENIE G24 FSI scale changes (arXiv:2404.08510);
  - hadron-transport benchmarks (arXiv:2609.22662, preprint), whose E_vis matches our A construction.
- No paper found quantifies the fraction of ω going to neutrons or binding at ω ≈ 1–5 GeV on carbon.
- **[D] Signs.** Weaker absorption, a longer formation zone, a lower neutron share or more π⁰ all raise A/ω. That is
  the sign of the small W ≥ 1.8, A < 0.8 deficit in §5.2.
- **The double-counting risk is with detector response.** A 3–5% A-response error produces the same signature. Tuning
  FSI against it would absorb a detector effect into physics.

### 6.3 Explanation (iii): response and estimator (competing explanation)

**[D]** In size, this explanation matches every part of the C residual that is not muon-shape **[M]**:
- the transfer step: ±0.033 at 4%;
- the W ≥ 3 excess: ±0.07;
- the partition differences: estimator scale 10–74%.

It does not reconcile the predictions with one another. A data-side coherent scale shifts the transfer step by the
same ±0.033 for every G, while the transfer steps differ across G by 0.062 (+0.004, +0.028, −0.034). It is too small
for GENIE's 1.4–2.2 GeV overshoot (±0.01) and for the muon-shape step (±0.002).

### 6.4 MINERvA SIS and DIS selections and overlap [L]

**SIS (opened by the owner).** Lozano et al., arXiv:2503.20043v1 (PRD 114, 072001 per INSPIRE, *(agent-read)*).
- Same ME exposure: 1.06×10²¹ POT ν.
- Active tracker, 5.48 t fiducial.
- 2 < E_μ < 20 GeV, θ < 20°, 1.5 < W_reco < 2 GeV; definition II adds Q² ≥ 1 GeV². No pion requirement.
- "The underpredictions of Tune v2 compared to data are significant and growing" with Q² and p_T (§VII.1.2). Tune v2
  "without the nonresonant pion reduction" describes high Q² considerably better.
- **[D]** Its sample is a W slice of the same exposure and muon selection. It is not independent of ours, and any joint
  use needs a shared-event covariance.

- **[D] Sign comparison.** Lozano's preferred direction (less reduction of non-resonant pions, at 1.5 < W < 2 GeV and
  Q² ≥ 1 GeV²) is opposite to 02_11b's near-removal of the 1π non-resonant background. The two cover different
  kinematics, on CH versus H/D. Even so, an existing constrained inelastic change does not agree with the
  same-exposure SIS measurement in direction.

**DIS (agent-read).** Mousseau et al. (LE, PRD 93, 071101, Table I) fit a high-W / low-Q² sideband at ×1.57 against
×0.94 at low W. That is the same sign pattern on a different exposure, but it is a reco-template fit.

### 6.5 Ranking and selection

| Rank | Explanation | Reach for C | Independent constraints | Identifiability now | Verdict |
|---|---|---|---|---|---|
| 1 | (iii) Response / estimator / flux-tail shape | sufficient in size for the non-muon part of C | test beam (p, π, e only), ν-e flux | high: one measured family exists; species family is the missing input | **leading competitor** |
| 2 | (i) RES–SIS–DIS matching (02_11b family) | right sign in M and W ≥ 3, wrong at 1.8–2.2 and Δ in a first-order emulation on GENIE 2.12 events | H/D bubble chamber; NOMAD/MINOS σ/E | needs a real GENIE v3 prediction (W_cut, Berger–Sehgal RES); same-exposure SIS prefers the opposite NRB direction | **the one constrained candidate, motivated by M, not by C; not selected for development** |
| 3 | (ii) Partition / FSI / hadronization | only through A\|t (≤ 1.7%) | hadron–nucleus data, e-scattering knockout | not identifiable with this estimator | none |

**Selection.** None is selected as a GO candidate for region C. If Joseph wants one physics test, it is explanation
(i), evaluated through the official GENIE v3 02_11b configuration rather than a new model. It would test M and the W
profile, not C (§8).

## 7. Proposed falsification tests (written after the data were seen; thresholds tied to tabulated values; none is a fit)

Any decision from these tests needs a new frozen rule, like PLAN §6. The outcomes below are proposals, not
pre-declared verdicts.

1. **Response degeneracy of C.** If one-standard-deviation species-dependent recoil variations (π± 5%, EM 3%, p 3.5%,
   n 10–25%) move ln ρ_W≥3 by at least the observed per-G values (GENIE CV 0.152, GENIE + MEC 0.191,
   NuWro 0.088), or ln ρ_C by at least the observed per-G values (0.028, 0.064, 0.006), then the high-region residual
   is response-degenerate. That would argue against a high-region model.
2. **02_11b family.** A real GENIE v3 G18_02a_02_11b CH prediction on the analysis flux is falsified for this
   measurement if it overshoots the Δ bin (|ln ρ_W1.1–1.4| > 0.10) or worsens R_total by more than 3%. It passes the
   intermediate-W test if it reduces |ln ρ_M| below 0.10 without either.
3. **Muon-shape component.** Any inclusive change offered for C must reproduce the published ρ(p_T) rise
   (ρ 0.74 → 1.10 across p_T) without changing the Δ region. A low-Q² change predicts the opposite p_T trend.
4. **Partition.** A claimed FSI/hadronization change must predict the A|t pattern at W ≥ 1.8 and leave the muon and
   transfer steps unchanged. It cannot be evaluated until an estimator follows A-shape departures (§5.3).

## 8. Missing inputs and a costed validation proposal (not authorized)

**Missing inputs.**
1. A species-dependent recoil-response family propagated on the data side, and ideally in the null.
2. A GENIE v3 02_11b (and AR23_20i) CH prediction on the analysis flux to 100 GeV.
3. An estimator that follows generator-sized E_avail departures. s5c, s5n and s5e are closed, and this memo does not
   propose reopening them.
4. GiBUU support above 20 GeV and its two-pion-background configuration.
5. A measured high-energy flux-shape uncertainty for E_ν > 20 GeV in the W ≥ 3 cells.

**Roles, frozen before any fit.**

| Role | What fills it | How it may be used |
|---|---|---|
| Development | H/D bubble-chamber inclusive/exclusive and NOMAD/MINOS σ/E | Already absorbed by the official tune. **No refit.** |
| Validation (not fitted) | This analysis's 5D W profile (normalization removed); the published 2D ρ(p_T) | Read the frozen tests of §7 |
| Withheld from fitting | Region C and the Δ bin | Already inspected, so **not blind** |
| Reviewers | One generator developer outside the GENIE tune authors; one independent statistician for the response family | Review only |
| Decision | Joseph | Per stage |

**Stages.**

| Stage | Work | Cost basis | Decision it answers |
|---|---|---|---|
| V1 | 8 data-side species variations (4 species × ±1σ) through the W2B machinery and estimator R | measured W2B: 1.898 billed CPU node-h for 3 variants → **≈ 5 CPU node-h** for 8 [M→A] | test 1: is C response-degenerate? A positive answer would argue against a high-region model, under a new frozen rule |
| V2 | GENIE v3.06.02 G18_02a_02_11b and AR23_20i, CH mixture, 1M + 0.1M (50–100 GeV) events each, through the existing converter | GENIE v3 throughput unmeasured here; **assumed** 5–50 ms/event → 1.5–15 core-h per configuration. A 10⁴-event pilot (≤ 0.2 core-h) measures it first. Official splines assumed usable [A] | tests 2–3 |
| V3 | Only if V1 is negative and V2 passes: review and Joseph's decision on any implementation | — | — |

## 9. Limitations

- The data are a single estimator's central value. No uncertainty construction is used, and per-cell statistical
  errors are not quantified here.
- The 2D statistical band is ~0.5% per bin (VL170), small against these effects, but 5D cell errors are larger and
  unmeasured.
- The Tune v1 comparisons are prior-coupled. The ±4% response test is data-side only.
- The recorded estimator biases are pseudo-experiment means at development scale. The s5n A-shape departure inherited
  the KI 83 flux defect; it remains a valid estimator stress, but it is not physically anchored.
- The GENIE decomposition is one model's labels.
- The emulation omits W_cut and RES-M_A.
- Literature items marked *(agent-read)* were not re-opened by the owner.

## 10. Reproduction and budget

**Inputs.** Product inputs were copied read-only to a session scratch directory and checked against the §3 digests
by `code/common.py`. Cluster work ran in `/pscratch/sd/j/josephrb/inelastic-high-region-20261011/` through
`code/run_remote.sh` (root_6_28), importing the s5p flux-fix code unchanged.

**Commands** (inputs dir `IN`):

```bash
python3 -I code/budget.py run --id R1   --cap-s 120 -- python3 -I code/reduce_r1.py  $IN results/R1_rate_shape.json
python3 -I code/budget.py run --id R3R4 --cap-s 300 -- python3 -I code/reduce_r3.py  $IN results/R3R4_decomposition.json
python3 -I code/budget.py run --id R4b  --cap-s 200 -- python3 -I code/reduce_r4b.py $IN docs/orchestration/state results/R4b_recorded_and_profiles.json
python3 -I code/budget.py run --id A1b  --cap-s 60  -- python3 -I code/a1b_published_rate.py $IN results/A1b_published_rate.json
# on Perlmutter (results copied back): r5_genie_events.py, r5b_tune_emulation.py
python3 -I code/budget.py run --id A1d-red --cap-s 60 -- python3 -I code/reduce_a1d.py $IN <r5b_tune_emulation.npz> results/A1d_tune_emulation_contrasts.json
python3 -I code/make_figure.py results results/fig_contrast_by_W.png
```

**Digests.** After the review, `code/common.py` pins every input (14), including the W2B unfolds
(manifests), the frozen estimator-R central (`fb5cc679…`) and the three jitters (recorded on first read). They are
verified in ledger entry `COR-verify`. The amendments, their results and the memo landed together in `f0352ea4`.
The "after R1/R3" ordering of the amendments is stated, not git-evidenced.

**Emulation array.** `r5b_tune_emulation.npz` (SHA-256 `4139c4e9…`, 1.05 MB) stays in the cluster scratch
directory and is not committed. Its reduction is committed.

**Budget.** The first R5 attempt crashed on an RVec conversion and was charged its full 900 core-s cap. Its log was overwritten by the rerun's (same path); the ledger keeps its rc = 255 entry. The rerun used
39.3 core-s, the hydrogen-code fix 39.5 core-s and the emulation 35.7 core-s.

**Budget [M]: 1,092.1 core-s of 7,200 before review; 1,100.9 after review (7.3) and correction (1.5)** (19.4 core-s of it reran five local reductions only to key their digests by canonical path; no number changed).
