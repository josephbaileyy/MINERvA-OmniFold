# High-E_avail / high-W discrepancies and inelastic physics: research memo

**Date 2026-10-11. Owner: this session (inelastic-high-region lane). Base: remote `main` `3892e769`. Frozen plan
[`PLAN.md`](PLAN.md), committed as `60d1405f` before any reduction, with two descriptive amendments (§8 there).
Reviewed once (fresh, read-only) with one correction pass applied; see [`REVIEW.md`](REVIEW.md). This memo authorizes
nothing, adopts nothing and contacted no one. Joseph owns the scientific decision.**

**Close-out (2026-10-11, on reviewed head `3e9e5188`).** Joseph asked for one bounded correction of interpretation and a
no-run feasibility section (§11). No number, input, rule or rule outcome changed, and nothing was run. The corrections
concern:
- what response degeneracy and the factor substitution can establish;
- the meaning of the S20 6.0%;
- the source of Tune v1's ×0.57;
- what arXiv:2609.22662 defines;
- FSI signs by channel;
- the status of the 4.1% response estimate and of world σ/E;
- the status of §7's central-value cutoffs.

**Proposal changes.** One change goes beyond interpretation. The V2 proposal (§8) now names G18_10a_02_11b and
AR23_20i at v3.04.00 in place of G18_02a_02_11b at v3.06.02, because the inventory found no G18_02a_02_11b splines
(§11.6).

The corrections were reviewed once more (targeted, read-only), and one correction pass followed (REVIEW.md, "Close-out
review"). Remote `main` had advanced to `d81f532b` (article and note edits only). None of this study's inputs changed.

Evidence labels used throughout: **[M]** measured here or in a cited committed receipt; **[D]** deduced
analytically from [M] and stated definitions; **[A]** assumption; **[L]** literature, opened by the owner unless
marked *(agent-read)*, meaning the delegated literature agent read it and the owner did not re-open it.

## 1. Verdict: INCONCLUSIVE under the frozen rule; GO not reached

**Supported statement.**
- After removing the rate and accounting for energy coverage, with the one tested coherent response scale and the
  recorded estimator biases as yardsticks (neither is separated as a cause), the high-E_avail / high-W
  region (A ≡ E_avail ≥ 0.8 GeV, W ≥ 1.8 GeV; "region C") carries a small normalization-removed residual against
  the complete-support external generators **[M]**:
  - ρ_C − 1 = +2.85% (GENIE 2.12.10 CV), +6.65% (GENIE + MEC) and +0.62% (NuWro 21.09).
  - A coherent ±4% recoil-response scale moves ρ_C by 3.7–4.0%.
- **No single decomposition factor holds two thirds of the residual for any of the three [M].**
  - The muon-shape step is the largest common component: +1.7% to +2.9%.
    - It moves by only ±0.2% under the one coherent ±4% recoil scale tested.
    - That is its only tested robustness. Muon-energy scale, angular resolution, flux shape and species-dependent
      response were not varied.
  - The final-state-partition step is comparable for GENIE CV (+0.8% against a net +2.8%) and larger than the net
    for NuWro (+1.7% against +0.6%).
  - **[D] The factor substitution is descriptive, not a causal separation.** It books the ratio into conditional
    factors of the data.
    - One physical change, such as a DIS scale, moves several factors at once.
    - Response, background or prior effects in the unfolded data can enter every factor.
    - A step's size therefore names where a difference appears, not what causes it.
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
   - No official GENIE v3 prediction exists that could test it without new generation (§11.6).
3. The next decision-relevant step is not a model. It is **two independent reviews, before any validation** (§11.7):
   - one by a MINERvA hadronic-response reviewer;
   - one by a nuclear-theory/generator reviewer.

   If they clear it, the order would be:
   - an official GENIE v3 prediction for the intermediate-W feature (V2, §8);
   - then the response-hypothesis study specified, but not executed, in §11.
   - Response degeneracy, meaning that the tested ±4% scale moves part of the residual by a comparable amount,
     **does not establish a detector cause and does not exclude interaction physics**. It shows only that this region
     cannot yet tell them apart.
   - The MC AnaTuples carry per-species visible energy, but none of our chain's stored products keeps it. Data have no
     truth species. A species-dependent family is therefore possible only on the simulated-response side, with a new
     event-loop pass (§11.1).
   - **Before any validation is designed in detail, an independent MINERvA hadronic-response reviewer and an
     independent nuclear-theory/generator reviewer should examine §11 and §6.**
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
  bracket it: GENIE is 5.9% below NOMAD (1.2σ) and 1.4% above MINOS at 5.9 GeV. A
  roughly uniform ~11% increase of the inclusive cross section at 5–20 GeV would conflict with those data.
- **[D] What σ/E does not constrain.** Those data constrain the rate σ(E_ν), integrated over final states and
  kinematics. They do not constrain:
  - redistributions at fixed σ(E_ν), in (x, y), (Q², W) or between RES, non-resonant and DIS strength, which can be
    many per cent in a sub-region;
  - target-dependent (CH versus Fe or C) effects;
  - the region below ~5 GeV at this precision.

  They limit a rate explanation, not a shape one.
- The overall rate difference alone is therefore **not** a motivation for an inelastic change. Its origin (flux
  normalization, efficiency, target count, or the inclusive cross section below 5 GeV) is **unresolved here**.

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
E_ν ≤ (p_T,hi² + p_∥,hi² + m_μ²)^½ + (W_hi² + q3,hi² + m_μ²)^½ − M (§5.1). S20 holds 49.5% of the measured total
cross section, but only **6.0% of the measured C cross section** and 76.4% of M.

**[D] What the 6.0% is and is not.**
- **It is a conservative sufficient condition.** Every event in an S20 cell has E_ν < 20 GeV, whatever the generator.
- **It is not GiBUU's physical coverage of C.** Cells outside S20 can still draw most of their cross section from
  E_ν < 20 GeV.
- **The generator-estimated shares are a different, model-dependent quantity [M].** E_ν > 20 GeV carries 14.3% of C
  in GENIE CV (§5.4). VL161 gives 14.30 / 14.46 / 14.82% of the corner and 6.79–7.43% overall for GENIE CV, GENIE + MEC
  and NuWro. On those models' own flux × cross section, about 85% of C comes from E_ν < 20 GeV.
- **The two numbers must not be substituted for each other.** The generator shares are not used here to correct
  GiBUU.

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
   fixed by the flux and the inclusive tensor W^{αβ} alone.
   - **[D]/[A] Scope of the invariance.** Hadronization and transport cannot change that distribution **when they act
     as a normalized post-vertex kernel**, Σ_f K(f|X) = 1, at fixed primary inclusive dynamics. That is the factorized
     cascade picture of GENIE, NuWro and the GiBUU collision term.
   - It is a property of that factorization, not a theorem about nature. In a full many-body treatment the struck
     system's final-state interaction is part of W^{αβ}: optical potentials and the spectral function shift and
     redistribute inclusive strength in ω, as in inclusive electron scattering.
   - The "primary versus FSI" split is then model-dependent.
   - Also, at reconstruction level, final-state changes alter the reconstructed recoil, so unfolded q3 and W can move
     through response and prior dependence (§5.3).
2. **Only E_avail involves the final state.** For final state f (after transport kernel K(f|X)):

$$P(A\mid E_\nu,k')=\frac{\sum_X\sum_f L_{\alpha\beta}\,\langle A|J^{\alpha\dagger}|X\rangle\langle X|J^\beta|A\rangle\,K(f\mid X)\,\delta\!\left(A-A(f)\right)}{L_{\alpha\beta}W^{\alpha\beta}} .$$

  This conditional still depends on the lepton tensor through which tensor components are weighted. "At fixed
  transfer" therefore means at fixed (E_ν, k′), which the 5D cell (m, t) approximates.

**Where the transferred energy goes.** Energy conservation with the repository's definition (Eq. 1 of
`docs/EAVAIL_DEFINITION.md`) gives

$$\omega = A + \sum_n T_n + 0.135\,N_{\pi^\pm} + E_{\rm other} + \varepsilon_B ,$$

up to the 4.6 MeV per charged pion between 135 and 139.57 MeV. Here ε_B is separation, residual excitation and recoil.

| Process | Effect on A at fixed ω | Effect on the inclusive rate (normalized post-vertex kernel, fixed primary dynamics) |
|---|---|---|
| π⁰ → π± charge exchange, or a different hadronization charge ratio | −135 MeV per pion | none |
| More energy to neutrons, or more binding | lowers A | none |
| Changing the inclusive tensor | moves (q3, W) | moves the rate |

The FSI channels are derived one by one in §6.2. Their signs differ.

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

**[D] Reading rule.** The split is a descriptive accounting identity, not a causal separation (§1). It also depends on
the order of substitution (shown below).

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
| *S20 ∩ C, the plan's GiBUU domain (cells holding 6.0% of the measured C; §4.3):* | | | | |
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
2. **[M]** The component least moved by the tested response scale is the **muon-shape step**: +0.017 to +0.029.
   - Under the one coherent ±4% recoil scale it moves by ±0.002.
   - Its robustness to muon-energy scale, angular resolution, flux shape and species-dependent response was not
     tested.
   - **[D]** It is inherited from the (p_T, p_∥) distribution, which the published measurement already shows
     (§4.2: ρ rises with p_T).
   - **[L]** *(agent-read)* Ruterbories et al. (PRD 104, 092007, §VI) describe their high-p_T (> 0.85 GeV/c)
     region as "dominated by the 'True DIS' process" for p_∥ > 6 GeV/c.
   - So this component is an inclusive muon-kinematics (Q²/y) shape discrepancy that was already published, not a
     new hadronic-axis finding.
3. **[M]** The tested scale moves the transfer step by an amount comparable to its size. ±4% recoil moves ln ρ_C's
   transfer step by ±0.033, and ln ρ_W≥3 by ±0.07.
   - **[D]** That is a degeneracy in size. It means response cannot be excluded as the cause, not that response is
     the cause.
   - Inclusive-tensor and flux-shape explanations remain equally admissible.
   - The W ≥ 3 excess (+0.09 to +0.15) is at most twice that shift.
   - **[M]** In GENIE, 46% of the W ≥ 3 cross section comes from E_ν ≥ 20 GeV (mean 22 GeV). The high-energy
     flux-tail *shape* is therefore a further competitor there.
4. **[M]** The largest normalization-independent feature is outside C. GENIE overshoots at 1.4–2.2 GeV (ln ρ −0.19
   and −0.09); Tune v1 overshoots at 1.4–1.8 only (−0.12). It moves only ±0.01 under the one coherent ±4% recoil scale
   tested. Species-dependent response and prior leakage into the unfolded (q3, W) were not tested.
   - NuWro shows the overshoot only at 1.8–2.2 GeV.
   - **[D]** That a W-only region's residual "sits in the transfer step" holds by construction: its partition step is
     identically zero.

**Partition at fixed transfer, W ≥ 1.8 [M].** At W ≥ 1.8 the data put fewer events at A < 0.8 than GENIE CV
(A|t step −0.03 to −0.11) and Tune v1 (−0.05 to −0.09). These cells hold 3.7% of the data. The other A bins differ
by ≤ +0.012. The ±4% response shift of these entries is ±0.014–0.023. NuWro differs strongly in the opposite sense:
A|t −0.31 to −0.41 below 0.4 GeV and +0.24 at 0.8–1.5 GeV.
- **[D]** The sign means the data have *more visible energy per unit transfer* than GENIE and Tune v1. Candidate
  causes include:
  - less energy to neutrons or binding;
  - a higher π⁰ share;
  - an under-modeled recoil response.
- FSI can contribute with either sign, depending on the channel (§6.2).
- That conclusion is subject to §5.3.

### 5.3 Response, estimator and background limits [M]

| Effect on region C | Size | Source |
|---|---:|---|
| ±4% coherent recoil scale (W2B "data side": simulated response scaled, real data re-unfolded, null fixed; estimator R) | Δ ln ρ_C = +0.037 / −0.038 | W2B unfolds; `reduce_r3.py` |
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

**[D] The ±4% scale is comparable in size to a species-weighted response estimate. It is not a calibrated band.**
- **[M]** GENIE's A in C is carried 51% by π±, 33% by π⁰/γ and 15% by protons.
- **[L]** *(agent-read)* MINERvA's toolkit default response uncertainties (`ParticleResponseDefaults.h`) are π± 5%,
  EM 3%, protons 3.5%. Test-beam agreement is "within 4%" up to 1 GeV (arXiv:1501.06431).
- **[A]** Weighting those defaults by GENIE's species shares and adding them **fully correlated** gives ≈ 4.1%. That is
  a size comparison only, **not a calibrated one-sigma nuisance band**:
  - the defaults were not re-opened by the owner;
  - their correlations and energy dependence are not specified;
  - neutron response and cross-talk are not included;
  - the test-beam basis stops at 2 GeV/c;
  - the species shares are one model's.
- ±4% is therefore a probe of plausible size, neither a bound nor a one-sigma variation.
- **[M]** The test varied neither the null, nor species, nor neutrons, nor resolution (W2B §1). MAT's per-particle
  response map is commented out in the event-loop source used (W2B §1).

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
- Caveats:
  - The omitted W_cut move (1.7 → 1.81) shifts strength from DIS into RES + NRB in 1.7–1.81 GeV. That partly offsets
    the W 1.8–2.2 change.
  - The tune was fitted to H/D, not CH. Nuclear effects on resonance production and pion transport are outside it.
  - **Corrected:** Tune v1's ×0.57 is not a Δ-absorption treatment. arXiv:2106.16210 §III (owner-opened) says: "Based
    on fits done in Ref. [36], we decrease the non-resonant pion production by 43%". Ref. [36] is Rodrigues, Wilkinson
    and McFarland, EPJC 76, 474 (2016), a fit to reanalyzed deuterium bubble-chamber single-pion data. It is an
    H/D-based non-resonant reduction of the same kind as 02_11b's R^1π change. It is applied on top of GENIE 2.12.6 and
    is not a nuclear correction.
  - **[D]** Tune v1 thus already carries a partial non-resonant reduction. That is consistent with its smaller M
    overshoot (ln ρ_M −0.12 against GENIE CV's −0.19), but it is not shown to cause it, since Tune v1 also differs in
    2p2h, RPA and GENIE version.
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

- **[D]** Treated as a normalized post-vertex kernel at fixed primary dynamics, transport and hadronization charge
  ratios change A at fixed (q3, W). They leave the truth inclusive rate and the (m, t) distribution unchanged (§5.1,
  where the scope of that statement is given).
  - Within that picture they act only through the A|t step.
  - Outside it, for example through nuclear potentials in the inclusive response or reconstruction-level migration,
    they can also move the other steps.
- **[M]** In C the A|t step is +0.6% to +1.7%, and not testable (§5.3).
- **[L]** Existing developments include:
  - *(agent-read)* the AGKY retune (arXiv:2106.05884), which fits charged multiplicities only and reports an
    incompatible π⁰ rise;
  - *(agent-read)* GENIE G24 FSI scale changes (arXiv:2404.08510);
  - a hadron–nucleus benchmark, arXiv:2609.22662v2 (preprint), described next.
- **[L] arXiv:2609.22662, corrected (owner-opened).** It is a single-hadron study:
  - probes π±, π⁰, p and n at T = 0.05–2 GeV on C, O, Ar and Fe, simulated with GENIE v3.4.2 using hA2018, hN2018,
    INCL++ and Geant4 Bertini;
  - Eq. (1) defines E_vis = Σ_p T_p + Σ_{i=π,K,γ} E_i, which uses **total** energies for all mesons, so π± count their
    rest mass and **kaons are included**;
  - our A (`docs/EAVAIL_DEFINITION.md`) uses **kinetic** energy for π± (rest mass removed, with the 135 MeV constant),
    total energy for π⁰, and excludes kaons and e±.
  - **Its E_vis is therefore not our E_avail.** Per charged pion they differ by 135 MeV, because A uses E_π± − 0.135.
    Kaons add their full total energy.
  - Its nucleon multiplicities use a 5 MeV-per-nucleon kinetic threshold, chosen to match DUNE's Phase-II near
    detector. Its Tables I–II comparisons with data use 30 MeV for p, d and n. Our A has no threshold.
  - Its reweighting tools address the spread between hadron-transport models. They are not a detector response.
  - Borrowing its templates for our A would need: re-deriving them with our species convention and no threshold; the
    neutrino-induced hadron spectra of region C (well above 2 GeV); and CH rather than its four targets. That is not
    possible from the paper's tables.
- No paper found quantifies the fraction of ω going to neutrons or binding at ω ≈ 1–5 GeV on carbon.

**[D] FSI signs by channel, for our A.**

*Definitions.*
- A counts Σ T_p + Σ (E_π± − 0.135) + Σ E_π⁰ + E_γ. It excludes neutrons, binding and kaons.
- Each FSI step conserves energy, E_in + Σ_removed (M − ε) = Σ_out E, where ε is the separation energy of the removed
  nucleons.
  - On ¹²C, S_p ≈ 16 MeV and S_n ≈ 18.7 MeV, so a single removal costs ε ≈ 16–19 MeV.
  - Removing a pn pair costs ε₂ ≈ 27 MeV. These are ground-state values, and deeper shells cost more.
  - The 8 MeV mean binding per nucleon is not the relevant quantity.
  - Recoil, the n–p mass difference and the 4.6 MeV π± constant offset are neglected.
- ΔA is the change of A relative to the same step not occurring.

| FSI step | ΔA | Sign |
|---|---|---|
| π⁰ absorption on a nucleon pair | −(Σ T_n + ε₂) | ≤ 0 always: the π⁰'s total energy is already counted |
| π± absorption → p p (π⁺ on a quasi-deuteron pn) | +0.135 − ε₂ ≈ **+0.11 GeV** | **> 0**: the uncounted rest mass becomes counted proton energy |
| π± absorption → p n | +0.135 − ε₂ − T_n | either sign: > 0 if T_n < 0.11 GeV |
| π± absorption → n n (π⁻ on pn) | −(E_π − 0.135) | < 0: the pion's whole contribution is lost |
| π⁺ n → π⁰ p (charge exchange) | +0.135 − S_n ≈ +0.12 GeV | > 0 |
| π⁻ p → π⁰ n | +0.135 − ε − T_n | either sign |
| π⁰ → π± (either target) | −0.135 − ε (− T_n) | < 0 |
| π or p transferring energy to a bound proton | −ε | ≈ 0 |
| … to a bound neutron | −ε − T_n | < 0 |
| a neutron (uncounted) knocking out a proton | +T_p | **> 0** |
| a proton producing a pion, N N → N N π± | −0.135 − ε − Σ T_n | < 0 |
| … producing a π⁰ | −ε − Σ T_n | ≤ 0 |
| a neutron producing a pion | +Σ T_p + E_π (− 0.135 for π±) | > 0 |
| de-excitation of the residual nucleus (evaporation or γ), against the excitation energy staying unemitted | +E_γ + Σ T_p(evap); evaporated neutrons 0 | ≥ 0 (the excitation energy itself was taken from counted particles by the preceding step, whose row carries that cost) |

**Consequences [D].**
- "Weaker absorption raises A" is **false as a general statement**. It holds for π⁰ absorption and for π± absorption
  into neutron-rich final states. For π± absorption into two protons the reverse holds: on N = Z carbon, π⁺
  absorption on pn pairs gives pp, so weaker absorption *lowers* A.
- Weaker FSI on primary neutrons, or less π± → π⁰ charge exchange, also lowers A.
- The net sign of a change in FSI strength depends on per-channel rates. These follow from the primary species mix
  (CC ν on CH produces mostly π⁺, protons and DIS-fragmentation neutrons) and from the model. **The net sign is not
  determined here.**
- GENIE's per-hadron fates exist in the gst files but were not tabulated in this study.
- The small W ≥ 1.8, A < 0.8 deficit (§5.2) is therefore not by itself evidence for weaker FSI.
- The formation-zone and neutron-share sign statements in LIT-REPORT B3 and its candidate table carry the same
  qualification.

**The double-counting risk is with detector response.** A 3–5% A-response error produces a similar A|t signature.
Tuning FSI against it would absorb a detector effect into physics, and vice versa.

### 6.3 Explanation (iii): response and estimator (competing explanation)

**[D]** In size, this explanation matches every part of the C residual that is not muon-shape **[M]**:
- the transfer step: ±0.033 at 4%;
- the W ≥ 3 excess: ±0.07;
- the partition differences: estimator scale 10–74%.

The tested scale does not reconcile the predictions with one another. A coherent scale applied on the response side
(W2B sense) shifts the transfer step by the same ±0.033 for every G, while the transfer steps differ across G by
0.062 (+0.004, +0.028, −0.034).

The tested coherent scale moves GENIE's 1.4–2.2 GeV overshoot by only ±0.01 and the muon-shape step by only ±0.002.
Whether an untested species-dependent family could move them more is open (§11).

**[D] What matching in size does and does not show.**
- That the tested response scale *can* move these quantities by their observed size is a degeneracy.
- It does not establish a detector cause, and it does not exclude interaction physics. Both remain admissible, and
  the region cannot currently discriminate between them.
- "Data-side" here follows W2B's usage. The simulated reconstructed recoil in the response model was scaled and the
  real data re-unfolded; the null ensembles were not changed (W2B §1).

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
| 1 | (iii) Response / estimator / flux-tail shape | comparable in size to the non-muon part of C (degeneracy, not an established cause) | test beam (p, π, e only, ≤ 2 GeV/c), ν-e flux | partial: one coherent family measured; a species family needs a new event-loop pass (MC tuples have the branches; our products do not) and is simulation-side only (§11.1) | **leading competitor, not an established cause** |
| 2 | (i) RES–SIS–DIS matching (02_11b family) | right sign in M and W ≥ 3, wrong at 1.8–2.2 and Δ in a first-order emulation on GENIE 2.12 events | H/D bubble chamber; NOMAD/MINOS σ/E | needs a real GENIE v3 prediction (W_cut, Berger–Sehgal RES); same-exposure SIS prefers the opposite NRB direction | **the one constrained candidate, motivated by M, not by C; not selected for development** |
| 3 | (ii) Partition / FSI / hadronization | only through A\|t (≤ 1.7%) in the factorized picture; sign channel-dependent (§6.2) | hadron–nucleus data, e-scattering knockout | not identifiable with this estimator | none |

**Selection.** None is selected as a GO candidate for region C. If Joseph wants one physics test, it is explanation
(i), evaluated through an official GENIE v3 02_11b-family configuration rather than a new model:
- G18_10a_02_11b or AR23_20i have ready splines;
- G18_02a_02_11b has none (§11.6).

It would test M and the W profile, not C (§8).

## 7. Proposed screening rules (central values only; written after the data were seen; not statistical falsification)

**Status.** These are **screening rules on central values**, not falsification tests:
- no uncertainty model enters;
- the cutoffs were chosen after the data were seen;
- region C, the Δ bin and the W profile have all been inspected, so none of them is blind.

A screen can only route a candidate to, or away from, a properly specified test (§11). It cannot reject a model. Any
decision needs a new frozen rule like PLAN §6, an uncertainty treatment, and samples not used to choose the rule.

1. **Response movability of C.** Ask whether a species-dependent response family moves ln ρ_W≥3 or ln ρ_C by at least
   the observed per-G values:
   - ln ρ_W≥3: GENIE CV 0.152, GENIE + MEC 0.191, NuWro 0.088;
   - ln ρ_C: 0.028, 0.064, 0.006.

   The family must be specified and reviewed first (§11). Placeholder sizes are π± 5%, EM 3%, p 3.5%, n 10–25%.

   If it does, the residual is *movable* by response at that size. **That does not rule out a high-region model or
   any physics explanation.** It means this region cannot discriminate between them without independent calibration
   (§11.4).
2. **02_11b family.** Apply this screen to a real GENIE v3 CH prediction on the analysis flux. Two kinds are possible:
   - **A ready-spline configuration** (G18_10a_02_11b or AR23_20i at v3.04.00, the V2 proposal). It also changes the
     nuclear model, so a result screens that whole configuration. It is not attributable to the inelastic tune alone,
     and it does not test the G18_02a values emulated in §6.1.
   - **G18_02a_02_11b itself.** This needs splines built first, at a cost not measured here.

   The screen applies to either:
   - It is *flagged* if it overshoots the Δ bin (|ln ρ_W1.1–1.4| > 0.10) or worsens R_total by more than 3%.
   - It *passes the intermediate-W screen* if it reduces |ln ρ_M| below 0.10 without either.
   - Neither outcome is a statistical statement.
3. **Muon-shape component.** Any inclusive change offered for C should reproduce the published ρ(p_T) rise (ρ 0.74 →
   1.10 across p_T) without changing the Δ region. A low-Q² change predicts the opposite p_T trend.
4. **Partition.** A claimed FSI or hadronization change must predict the A|t pattern at W ≥ 1.8, with its
   channel-dependent sign (§6.2), and leave the muon and transfer steps unchanged. It cannot be evaluated until an
   estimator follows A-shape departures (§5.3).

## 8. Missing inputs and a costed validation proposal (not authorized)

**Missing inputs.**
1. **A species-dependent recoil-response family.**
   - The MC AnaTuples carry per-species visible-energy and MAT shift branches, but no stored product of our chain
     keeps them (§11.1). A new event-loop pass is needed.
   - Data carry no truth species, so the variation is defined only on the simulated-response side.
   - A response-varied null is needed for any calibrated statement.
2. **Independent calibration constraints beyond the test beam**: neutrons, EM in situ, and energies above 2 GeV/c.
   None was found in the repository.
3. **An official GENIE v3 CH prediction on the analysis flux to 100 GeV.**
   - None exists in any usable form (§11.6).
   - Ready CVMFS splines exist for G18_10a_02_11b and AR23_20i, but not for G18_02a_02_11b.
4. **An estimator that follows generator-sized E_avail departures.** s5c, s5n and s5e are closed, and this memo does
   not propose reopening them.
5. **GiBUU support above 20 GeV** and its two-pion-background configuration.
6. **A measured high-energy flux-shape uncertainty** for E_ν > 20 GeV in the W ≥ 3 cells.
7. **Per-channel FSI fate tables for region C.** These are needed for the net FSI sign (§6.2).

**Roles, frozen before any fit.**

| Role | What fills it | How it may be used |
|---|---|---|
| Development | H/D bubble-chamber inclusive/exclusive and NOMAD/MINOS σ/E | Already absorbed by the official tune. **No refit.** |
| Non-blind consistency checks | This analysis's 5D W profile (normalization removed), region C, M, the Δ bin; the published 2D ρ(p_T) | **Already inspected, so not blind.** Screening only (§7); never a confirmation |
| Blind validation | Data not inspected in this study (e.g. ME RHC or LE FHC inclusive, with response correlation stated); independent calibration samples (§11.4) | Only under a new frozen rule |
| Withheld from fitting | Everything above | No fit is proposed |
| Reviewers, before any validation | An independent MINERvA hadronic-response reviewer; an independent nuclear-theory/generator reviewer (outside the GENIE tune authors); for any calibrated statement, an independent statistician | Review only (§11.7) |
| Decision | Joseph | Per stage |

**Stages.**

| Stage | Work | Cost basis | Decision it answers |
|---|---|---|---|
| R | The two independent reviews of §6.2 and §11 | zero compute | §11.7: whether, and in what form, V1/V2 are worth executing |
| V1 | **Sensitivity-only** species response: 8–12 simulated-response endpoints plus a control, through the W2B chain and estimator R, plus closure (§11.2 a, §11.3) | ≈ 6–9.5 + 1.5–2 billed CPU node-h, extrapolated from W2B's measured 1.898 for 3 endpoints (§11.5) [A]. **Not a total validation budget, not core-hours** | §7 rule 1 (movability) and §11.3 (hiding), as a screen |
| V1-matched | Response-varied null ensembles (§11.2 b) | order 10² billed CPU node-h (packet estimate ~200, unmeasured) [A] | any calibrated response statement |
| V2 | GENIE v3.04.00 G18_10a_02_11b and AR23_20i (ready splines), CH mixture, 1M + 0.1M (50–100 GeV) events each, through the existing converter | GENIE v3 throughput unmeasured here; **assumed** 5–50 ms/event → 1.5–15 core-h per configuration. A 10⁴-event pilot (≤ 0.2 core-h) measures it first [A]. The alternative, G18_02a_02_11b itself, needs splines built first, at an unmeasured cost | §7 screens 2–3 (M feature, Δ bin, rate) |
| V3 | Only if V1 and V2 are informative: review and Joseph's decision on any implementation | — | — |

## 9. Limitations

- The data are a single estimator's central value. No uncertainty construction is used, and per-cell statistical
  errors are not quantified here.
- The 2D statistical band is ~0.5% per bin (VL170), small against these effects, but 5D cell errors are larger and
  unmeasured.
- The Tune v1 comparisons are prior-coupled. The ±4% response test is data-side only in the W2B sense: the simulated response was varied and the real data
  re-unfolded; the null was not varied. (The figure legend's "data side" has the same meaning.)
- The recorded estimator biases are pseudo-experiment means at development scale. The s5n A-shape departure inherited
  the KI 83 flux defect; it remains a valid estimator stress, but it is not physically anchored.
- The GENIE decomposition is one model's labels.
- The emulation omits W_cut and RES-M_A.
- Literature items marked *(agent-read)* were not re-opened by the owner.
- The decomposition is descriptive bookkeeping, not a causal separation (§1, §5.2).
- Response degeneracy shows only that response cannot be excluded. It neither identifies a detector cause nor excludes
  interaction physics.
- The muon-shape step's robustness was tested against one coherent recoil scale only.
- The 4.1% species-weighted figure is an assumption-laden size comparison, not a calibrated band (§5.3).
- The FSI net sign is not determined (§6.2).
- §7's cutoffs are screening rules on central values.

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

**Close-out [M].**
- The close-out pass ran no reduction and added nothing to the ledger.
- Its read-only inventory listed branch names of one MC and one data AnaTuple, and the CVMFS spline directories, on a
  Perlmutter login node. That took seconds, read no values and is not metered by `budget.py`.
- The close-out reviewer's charges, if any, are in REVIEW.md.

## 11. Feasibility of a response-hypothesis validation (specification only; NOT executed)

**Status.** Nothing in this section was run. It authorizes no compute, and its costs are estimates from cited
records. The inventory was read-only:
- grep of `origin/main` `d81f532b`;
- branch-name listings of one MC and one data AnaTuple on Perlmutter;
- no values were read and no job was submitted.

That inventory was delegated to a read-only agent, and its key citations were re-opened by the owner (*(owner-checked)*).

**Precondition.** Before any part of this is executed, an independent MINERvA hadronic-response reviewer and an
independent nuclear-theory/generator reviewer should review the response family, the closure departures and §6.2.
Neither should be an author of this memo or of the GENIE tune. They should also judge whether the question is worth
the cost.

### 11.1 Inventory: what exists, what can be reused, what is missing

| Item | Status | Evidence |
|---|---|---|
| Per-species visible energy in the **MC AnaTuples** | **exists**: `blob_recoil_E_{tracker,ecal,…}_{p,meson,em,other,lown,midn,highn,xtalk,mu}` and MAT's per-species shift branches `part_response_recoil_allNonMuonClusters_*_{proton,meson,em,…}_err` | branch listing of a Playlist 1F MC AnaTuple (4,190 branches; agent-read, no receipt); the `blob_recoil_E_<subdetector>_<species>` family is in the committed receipt `nd-unfolding/pet/improvement_campaign/phase_a/receipts/feature_inventory.json` (`e39774e7`) *(owner-checked)* |
| Per-species information in **our stored products** (event-loop outputs, npz dumps) | **absent**. The event loop reads only the tracker/ECAL totals and `<tree>_recoil_E`; the dumps carry (p_T, p_∥, E_avail, q3, W) and weights only | `CVUniverse.h:185-209` *(owner-checked)*; `PACKET-20261005-publication-decision.md:277` *(owner-checked)* |
| Species branches in **data** tuples | names present; contents not read. **Data have no truth species labels in any case** | data AnaTuple branch listing |
| Response universes | 2D/3D: 187 universes. The only hadron-detector entries are `GEANT_{Neutron,Pion,Proton}` (interaction-rate weights). There is no calorimetric response universe, and MAT's response band is commented out at `/pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/MINERvA-101-Cross-Section/systematics/Systematics.h:87-89` (untracked; SHA-256 `1bdfa4f0…`; *owner-checked*). 5D: "no recoil-energy-scale band" (amendment 7). W2B: one coherent ±4% (`RecoilResponseUniverse.h`) | agent-read; W2B §1 *(owner-checked)* |
| Selection | **No reco cut reads the recoil**, so a response variation moves events across reco cells without changing selection | `runEventLoopOmniFold.cpp:1710-1715` (agent-read) |
| Background | Per-reco-cell purity weight max(0, data − bkg)/data. W2B scaled the background rows' reco observables with the signal's. The interaction with s5c D1's high-W purity bias (≤ 4%) is unrecorded | `unfold_nd_omnifold_unbinned.py:502-600` (agent-read) |
| Null / pseudo-experiments | Frozen s5p ensembles built with the nominal response. **No response-varied null exists** | W2B §1 |
| Independent calibration | Test beam, arXiv:1501.06431: p, π, e at 0.35–2.0 GeV/c, agreement better than 4%, **no neutrons**. Not found in the repository: Michel-electron or π⁰-mass EM calibration, in-situ proton dE/dx, any neutron-response measurement. A collaborator question on per-particle inputs was drafted and never sent | `app_statmethods.tex:385`; agent grep |
| Truth-level physics reweights usable as closure departures | **exist** in the analysis MC: GENIE `Fr*`/`MFP_*` FSI and cross-section universes among the 187; truth mode, W_gen and target fields | 2D universe list |

**[D] What the stored inputs permit.**
- **Species-dependent variations are possible only on the simulated-response side.** Each needs a new event-loop pass
  that reads the per-species branches. Roughly 50 lines extend `RecoilResponseUniverse`:
  - A_r = 1.17 Σ_s (1 + δ_s)(E_trk,s + E_ecal,s) − fuzz.
  - q0 is either shifted by MAT's per-species absolute shifts or scaled by the species fractions of `recoil_E`.
  - q3 and W are rebuilt as now.
- **No existing product can be reused for this**, because none stores species.
- **A data-side species variation is not defined per event**, since data carry no truth species. Applying
  simulation-derived species fractions per reco cell to data is model-dependent, and in effect a simulation-side
  variation anyway.
- **Checks before relying on the branches:**
  - the species pieces sum to the totals used now;
  - the `_mu` component and the muon-fuzz subtraction do not double count;
  - the q0 calibration convention is the one `recoil_E` uses.
- **Outputs the new pass must also write.** The closure (11.3) needs these fields in the 5D event outputs, which store
  only kinematics and weights today:
  - truth interaction mode, W_gen, struck-nucleon and target codes, and primary-hadron multiplicity;
  - the GENIE `Fr*`/`MFP_*` FSI reweight weights. Their availability in the 5D chain rests only on the 2D universe
    list and must be confirmed.

### 11.2 Response hypotheses and matched propagation

**Hypotheses H_k.** One-at-a-time species shifts at ±1 placeholder size, plus a δ = 0 control. The placeholder
sizes are MAT defaults (`ParticleResponseDefaults.h`, agent-read):
- meson 5%;
- EM 3%;
- proton 3.5%;
- neutron 25 / 10 / 20% (low / mid / high);
- other 20%.

That is 4–6 species × 2 signs. The final sizes and correlations are set by the response reviewer, **not** by this
memo, and cross-talk is excluded as MAT advises.

**Propagation, the same for every H_k.**
1. Apply the shift per simulated event, for signal and background rows: species-weighted A_r and q0, then q3_r and
   W_r. Truth, weights and selection are unchanged; this is checked by event-count identity against the δ = 0 control.
2. Recompute the purity background weights per reco cell from the shifted background rows.
3. Re-unfold the real data with estimator R, the W2B estimator, 3 numerical jitters per endpoint, through the same
   chain and the same frozen hyperparameters.
4. Compute exactly this memo's reductions: ρ_C, ρ_M, the per-W and per-A profiles and the decomposition steps,
   against the same predictions.

**What the intended inference requires.**
- **(a) Sensitivity / screening (§7 rule 1).** "Can H_k move the residual by its observed size?" Steps 1–4 suffice.
  The output is a set of shift vectors r_k, labelled exploratory as in W2B.
- **(b) Any calibrated statement**: an uncertainty, a significance, or "the residual survives response". This also
  requires a response-varied null, i.e. pseudo-data and null ensembles regenerated under each H_k (or under the
  reviewed band) with the same estimator. Without it, a shift is compared against a null built with the nominal
  response, which is the W2B limitation.
- The memo proposes only (a). (b) is costed so the difference is visible.

### 11.3 Closure: can response variation hide a known physics departure?

**Departures D_j.** Each is a fake data set built from the analysis MC at **nominal** response, with a truth-level
reweight of known form:
1. an emulated 02_11b-type re-partition (RES × 0.84, DIS × 1.06, NRB 1π reduced by struck nucleon), applied by truth
   mode and W_gen on the analysis MC;
2. an FSI change from the existing `Fr*` universes (pion absorption and charge exchange at ±1σ). Its A shift is
   channel-signed (§6.2);
3. a W-localized strength change of −15% at 1.4 ≤ W_gen < 1.8 GeV, matching the size of M's feature.

**Procedure.**
- Unfold each D_j under the nominal response and under every H_k.
- Form the departure signature d_j (the same reductions as §11.2 step 4) and the response shift vectors r_k.
- **Expected nominal non-closure.** The estimator does not follow generator-sized A-shape departures (§5.3: s5n C4,
  +2.5% over C, up to 74% per cell; C5 +0.8%). So D₂, and the A-dependent part of D₁, will not close against truth
  even at nominal response.
  - **Closure is therefore judged against the recorded bias, not against truth.**
  - At nominal response, d_j^nom (unfolded) must differ from the truth departure by no more than the recorded s5n/s5c
    scale for that region.
  - The test then compares each d_j^k (unfolded under H_k) with d_j^nom.
- **Hidden** means that the departure's unfolded signature d_j^nom lies within the span of {r_k}, at coefficients
  inside the reviewed band, to within a floor.
  - The floor is the jitter and seed spread on the δ = 0 control, **plus** the recorded estimator bias for the
    reductions concerned.
  - Hiding can therefore be claimed only for departures larger than that floor.
- **Reverse closure.** Fake data at nominal physics with a response shift H_k: does the reduction attribute it to a
  physics step?

**Validation samples.** The already-inspected W regions (C, M, the Δ bin, the per-W profile) are **non-blind**. They
may serve only as consistency checks, never as a confirmation. A blind check needs data not inspected in this study:
- for example ME RHC or LE FHC inclusive, with the response correlation to this sample stated;
- or the independent calibration samples of 11.1.

Lozano's SIS sample shares events with ours (§6.4) and is not independent.

### 11.4 Outcomes, defined before any execution

| Outcome | Condition | Reading |
|---|---|---|
| **Failure** | The δ = 0 control does not reproduce the nominal product within the jitter floor; a species-sum check fails; or, at nominal response, d_j^nom differs from the truth departure by more than the recorded s5n/s5c bias for that region | The study is uninformative. Fix or stop; nothing about physics |
| **Inconclusive** | The reviewed family moves ρ_C / ρ_M / the W profile by amounts comparable to the residual **and** closure shows that departures D_j can be hidden by it | The region cannot discriminate between response and the candidate physics. **No model is ruled out or in.** A movable residual is a degeneracy, not a refutation |
| **Useful (a)** | Closure shows the D_j are **not** hidden: d_j is outside span{r_k} within the band; and the family moves the observed residual by less than its size | That residual becomes a candidate physics constraint, subject to a new frozen rule, a response-varied null (11.2 b) and a blind sample |
| **Useful (b)** | Independent calibration narrows δ_s enough that the family's shifts fall below the residual | Same, with the calibration documented and reviewed |
| **Inconclusive (default)** | Any other combination, e.g. the family moves the residual comparably but the D_j are not hidden, or it moves the residual less but some D_j are hidden, or a departure is below the floor | No discrimination is claimed; record the combination and stop |

### 11.5 Cost: sensitivity-only versus matched validation

Units are **billed CPU node-hours** on Perlmutter (sacct ElapsedRaw × billing/256, W2B §6). They are not core-hours
and are not converted here: the W2B event loops ran at billing 10/256 of a node.

| Part | Basis | Estimate |
|---|---|---|
| Measured W2B, for reference | 3 endpoints (δ = 0, ±4%): 36 event loops 1.724, 3 lateral dumps 0.080, 3 unfolds 0.095; **1.898 for W2b, 1.997 including W2a** | measured [M] |
| **Sensitivity-only (11.2 a)** | ≈ 0.63 node-h per endpoint (W2B 1.898 / 3) × (8–12 endpoints + 1 control), plus 3 jitters per endpoint at 0.03 node-h | **≈ 6–9.5 node-h** [A, extrapolated] |
| Closure (11.3) | 3 departures + 1 reverse, each unfolded under each of 9–13 response endpoints at ≈ 0.03 node-h per unfold, reusing the event-loop outputs | **≈ 1.5–2 node-h** [A] |
| Code and review | ≈ 50 lines in `RecoilResponseUniverse`, species-sum checks, two reviewers | human time; not computed |
| **Matched validation (11.2 b)** | response-varied null ensembles per hypothesis or band; the packet's estimate for a calibrated re-production with a response band is **~200 node-h, "like s5p itself"** (`PACKET-20261005…:321`), unmeasured | **order 10² node-h** [A] |

The memo's earlier "≈ 5 CPU node-h" was this extrapolation (1.898 × 8/3) for **eight endpoints only**, "data-side" in
the W2B sense. It is not a total
validation budget, it omits the control, jitters, closure and any null, and it is not a core-hour figure. Every item
here is well above this study's 2 core-hour authorization, and none is authorized.

### 11.6 Existing official GENIE v3 predictions for the intermediate-W feature

**Result of a read-only inventory.** This was a delegated agent plus the owner's own CVMFS listing. **No existing
official GENIE v3 prediction tests the 1.4–1.8 GeV feature for ME FHC ν on CH without new generation.**

| Source | What exists | GENIE v3 configuration | Usable for a normalization-removed per-W ratio? |
|---|---|---|---|
| This repository and cluster space | only GENIE 2.12.10 gst (CV, MEC), NuWro and GiBUU products | none | no |
| CVMFS `genie_xsec` *(owner-listed)* | splines only, k250-e1000: `G1810a0211b` (v3_02_00, v3_04_00, v3_06_02_sbn2), `AR2320i` (v3_04_00, v3_06_00), `AR2520i`/`AR2522i` (v3_06_02_sbn1/2), `G1802a00000`; **no `G1802a0211b` in any version** | — | only by generating |
| Lozano et al. 2503.20043 (SIS, 1.5 < W < 2) | figure curves; no ancillary, HEPData or data-release tables | GENIE 3.0.6 G18_02a_02_11a, G18_10a_02_11a | no: one absolute W window, 02_11a, digitizing only |
| Ruterbories et al. 2106.16210 | ancillary model files | none (GENIE 2.12.6 / Tune variants, GiBUU, NEUT, NuWro) | no |
| Ascencio et al. 2110.13372 (E_avail–q3, q3 < 1.2) | figure curves; one χ² | G18_10a_02_11a | no |
| Bercellie et al. 2209.07852 (CC1π⁺) | ancillary W_exp table with **empty** GENIE v3 prediction rows | 02_11a family | no: W_exp < 1.4 and no numbers |
| Klustová et al. 2604.07091; Wolfs & Marshall 2509.22526 | figures | AR23, G18 | no: ν̄ or LE, no W |
| NUISANCE, HEPData | framework; no published ME W predictions | — | no |

All entries are agent-read unless marked; item-level verification status is in the agent's report, summarized here.

**[D] Consequence.**
- Testing the intermediate-W feature against GENIE v3 requires new generation (V2, §8).
- The cheapest official choices with ready splines are **v3.04.00 `G18_10a_02_11b` and `AR23_20i`**.
  - *(agent-read)* AR23's inelastic parameters come from G18_10a_02_11b.
  - Whether G18_10a's 02_11b inelastic values equal the G18_02a values emulated in §6.1 was **not checked**.
  - G18_10a also changes the nuclear model (LFG, Valencia QE, hN FSI). A difference from GENIE 2.12 is therefore
    not attributable to the inelastic tune alone.
- G18_02a_02_11b itself would need splines built first.

### 11.7 The next decision for Joseph (one, prioritized)

**Decision.** Whether to commission the two independent reviews named in the precondition above: one MINERvA
hadronic-response reviewer and one nuclear-theory/generator reviewer. They would cover:
- §6.2 (the FSI channel signs and the scope of the inclusive-invariance statement);
- §11.1–11.4 (the species response family, its propagation, the closure departures and the outcome table);
- whether a GENIE v3 V2 prediction is worth generating.

**Cost.**
- Zero compute.
- Two read-only review sessions, the reviewers' time, and no data access beyond this branch.
- Choosing reviewers outside the project may involve contact, which only Joseph can authorize.

**Why first.** Every execution path depends on choices this memo cannot make independently:
- the response sizes and correlations;
- whether the AnaTuple species branches mean what their names say;
- which physics departures are realistic;
- the FSI net sign.

The cheapest compute, V2 with ready AR23/G18_10a_02_11b splines (§8), is generation and needs its own authorization.
The sensitivity-only response study (≈ 6–9.5 billed CPU node-h plus closure) needs new event-loop code. Both should
follow review, not precede it.

**If the reviews clear it,** the recommended order is:
1. V2 first: a 10⁴-event throughput pilot, then two official configurations. It tests M directly and needs no
   detector code.
2. The §11 sensitivity study second. A matched validation (order 10² node-h) only if both are informative.
