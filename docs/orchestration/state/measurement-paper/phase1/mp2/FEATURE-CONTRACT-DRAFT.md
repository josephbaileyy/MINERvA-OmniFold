# MP-2 S2/S3 feature contract: DRAFT for the director's review

**By** the measurement session, 2026-10-20, under [`BINDING-PHASE1-20261019.md`](../../BINDING-PHASE1-20261019.md) §2
and [`PLAN.md`](../../PLAN.md) §3.3. Machine-readable form:
[`measurement-paper/phase1/mp2/feature_contract_draft.json`](../../../../../../measurement-paper/phase1/mp2/feature_contract_draft.json).
Code citations are at worktree HEAD `a32bd350`.

**CITABLE FOR:** nothing yet. It is a draft. On acceptance, its JSON sha256 is asserted by every S2 and S3 job.
**NOT CITABLE FOR:** any result. No fit, and no job, is authorized by it. Nothing fits until after
`maintenance_20261021`.

## 0. What S0 contributed (condition 2)

S0 informed this contract. The S0 receipt is `s0_fit.json`, sha256 `618823cb…`; the jobs were 60045652 and 60045657.
S0 was descriptive: NuWro on C12 against Tune v1 with hydrogen removed, with uncapped weights.
**V1–V5 are not changed because of it.**

| S0 number used | value | used for |
|---|---|---|
| AUC Tune vs NuWro, 5 scalars / full | 0.649 / 0.777 | motivation only |
| AUC gap vs NuWro-split | +0.151 / +0.275 | motivation only |
| split-control AUC (NuWro, scalars / full; Tune, scalars / full) | 0.498 / 0.502; 0.500 / 0.500 | V1 control design (§6) |
| split-control best iteration | 1, 1, 2, 19 | V1 control is capacity-matched |
| Kish ESS / ESS(w_truth), 5 scalars / full | 0.630 / 0.116 | a fallback set is declared (§3) |
| Kish ESS / N, 5 scalars / full / Tune-split | 0.536 / 0.099 / 0.851 | V4's N reading (§6) |
| max w / ⟨w⟩, 5 scalars / full | 311 / 1700 | the no-cap decision (§4) |
| Var log w, total and within fine cells, 5 scalars | 0.292, 0.185 | motivation (64% within cells) |
| Var log w, total and within fine cells, full | 1.43, 1.18 | motivation (82% within cells) |
| full fit: best iteration, time, training rows, threads | 1246, 34.5 s, 1.63M, 64 | costing (§8) |
| 5-scalar fit: best iteration, time | 496, 11.3 s | costing (§8) |
| prediction time | 2.43 s per 1.30M rows | costing (§8) |
| S0 Tune sample: share of non-carbon nuclei | 3.8% | target rule (§2) |

**The fallback is not chosen to pass V4.** S0 shows that the full feature set would fail V4 by a wide margin
(ESS/N 0.10 against 0.3; maximum weight 1700 against 50). The fallback feature set (§3) is chosen on response grounds,
and it is not tuned to S0's V4 numbers. If the declared configuration still fails V4 for some G, the event-level
null for that G is **"not established"**.

## 1. Generators: samples and per-event weight chains

The weights are the frozen gen5d chain's own. In each case r(E_ν) = (φ_t/Φ_t)/φ_s, from
`gen5d_flux_reweight.flux_weights` / `r_of` (`3d-unfolding/genie/gen5d_flux_reweight.py:440-456`).

**GENIE CV (2.12.10, CH)**
- Samples: `3d-unfolding/genie/genie_mefhc_cv_ALL.gst.root`, the < 50 GeV sample of 2,000,000 entries; and
  `gen5d_fluxfix/supp/genie_cv/genie_supp_cv.gst.root`, the 50–100 GeV supplement.
- Weight: r × A/B, with A = ⟨σ_CC⟩_t,<50 from the (C12 + H1)/13 graphs and B = Σ_allCC r (`:726-738`). The
  supplement uses a constant r (`gen5d_flux_supplement.py:165-212`).
- Frozen product: `gen5d_fluxfix/genie_cv_xsec5d_full.npz`.

**GENIE MEC (2.12.10 + Valencia, CH)**
- Samples: `genie_mefhc_mec_ALL.gst.root` and `supp/genie_mec/genie_supp_mec.gst.root`.
- Weight: r × ⟨σ_CC⟩_t,<50 / Σ_non-MEC CC r, the 3D-converter convention (`:726-738`).

**GENIE hydrogen.** The GENIE CH samples contain their own H events, gst `tgt == 2212` (C12 is `tgt == 1000060120`;
`mp3a/REPORT.md:22-25`).

**NuWro-CH (21.09, MP3-B primary (A), kaskada_on = 1)**
- C12 samples:
  - `work_nuwro_p{1..8}/nuwro_p{1..8}.root`, 8 × 250k events, N_total 2,000,000;
  - row-aligned to `gen5d/nuwro_flat5d_p{1..8}.root` (S0 control N1);
  - the supplement `gen5d_fluxfix/supp/nuwro/nuwro_supp.root`.
- H samples, the MP3-B free-proton chunks:
  - `phase1/mp3b/runA/gen/H_main/c01..c25/a<k>/nuwro.root`, 25 × 10k events;
  - `H_supp/c01..c05/a<k>/`, 5 × 5k events;
  - attempt k is the one named in each chunk's `RESULT` (`ok <k> <seed>`); aborted attempts are excluded.
- Weight:
  - C12: e.weight × r / N_total,C12 × 12/13;
  - H: e.weight × r / N_total,H × 1/13;
  - r on [0.5, 50] GeV, and the supplement's constant r = 4.8375e-4 (`gen5d_flux_supplement.py:177, :262`).
- S0 control N0 rebuilt the frozen C12 product bitwise with this chain.

**GiBUU-CH (2019)**
- Every readout carries **MP3-C's label**: "B3 (sampling closure) failed on hydrogen; a post-hoc bias check of its
  premise passed at ≤ 0.1 σ_c".
- C12 samples: `3d-unfolding/genie/work_gibuu_arr/task{1..80}/FinalEvents.dat`.
- H samples: `phase1/mp3c/prod/task{1001..1080}/FinalEvents.dat`.
- Weight: perweight × r / M × 1e-38, with C12 × 12/13 and H × 1/13 (`measurement-paper/phase1/mp3c/mp3c_build.py:4-9, :57`).
  The frozen r(E) is used, not the post-hoc alternative.
- E_ν ≤ 20 GeV only (KNOWN_ISSUES 82).

**Tune v1 (analysis MC)**
- All 32,849,103 s5p MCgen rows, through the admitted S1 dump (`s1_receipt.json`, sha256 `d240b41a…`).
- Weight: `w_truth`.
- The particles are rotated by RotateX(−0.05887) into the MAT beam frame.

## 2. Nuclear targets (condition 3)

- **Rule: train only on C and H rows, on both sides.**
  - Tune v1 side: the rows with `mc_targetZ ∈ {1, 6}`, i.e. 30,028,386 C rows and 1,632,529 H rows (S1 C3).
  - Generator side: G on CH, i.e. its C12 and free-proton events at 12/13 : 1/13 per nucleon.
  - The target is never a feature.
- **Other nuclei.** These are 1,188,188 rows: O, N, Al, Si, Cl, Ti and 174 rows with Z = 0. They keep A7's hybrid
  weight r_h at Tune v1's composition. **This is a limitation, stated in every readout.**
- **Justification.**
  - No C12 or CH generator sample contains those nuclei, so each such row is a pure target-identity signal. S0's
    sample carried 3.8% of them.
  - The H share is a physics difference between the models (σ_H/σ_C), not a target mismatch, because both sides are CH.
- **H events per generator:** GENIE, the gst's own `tgt == 2212` events; NuWro, the MP3-B chunks; GiBUU, the MP3-C tasks.

## 3. Harmonized features (conditions 4 and 5)

**Convention: the analysis convention for every generator event, as MP-5 did.**
- **The ν direction is drawn.**
  - Pool: MP-5's ν-direction pool, `phase1/mp5/run/pool/pool_b0..5.npy`, with sha256 in `mp5_tune.json`
    (`direction_pool`). It holds the analysis-MC ν direction in the MAT frame, with w_truth.
  - E_ν bins: 0, 3, 5, 8, 15, 30, ∞ GeV.
  - The w_truth-weighted CDF draw of `mp5_declaration.json` (`draw`).
  - `default_rng(seed_G)` gives one uniform per generator event, in the declared file order: C12 main, C12
    supplement, H main, H supplement.
  - seed_G: 2026102131 (GENIE CV), …32 (GENIE MEC), …33 (NuWro-CH), …34 (GiBUU-CH).
- **The whole event is rotated.** The Rodrigues rotation R(n), with R ẑ = n (`mp5_declaration.json` `rotation`), is
  applied to the lepton **and to every final-state particle**. The generator ν is asserted to lie along +z.
- **Muon variables.** pT and p∥ come from R p_μ. The phase-space decision is `in_truth_phase_space` on them.
- **W.** W follows `GetTrueExperimentersW` (`gen_to_xsec5d.py:123-131`; `CVUniverse.h:396-410`):
  - θ is measured from the beam axis;
  - M is the struck nucleon's mass: 939.565 MeV for n, 938.272 MeV for p, otherwise (1.5 M_n + M_p)/2.5;
  - **W is NaN where W² < 0, and that event is outside the grid**, exactly as Tune v1's NaN-W rows (MCgen −9999).
- **Struck nucleon:** GENIE gst `hitnuc`; NuWro `in[1].pdg`; GiBUU the single perweight-0 nucleon row, by its charge,
  otherwise the default mass (*UNSETTLED for 2p2h events*).
- **q3** comes from `gen_to_xsec5d.q3_true` (`:114-120`) and does not depend on the axis.
- **E_avail** is MAT's `GetEAvailableTrue` (`CVUniverse.h:361-374`) over the harmonized list, on both sides. S1's
  control C3 shows that it reproduces `MC_eavail` bitwise for Tune v1.
- **Harmonized products.** Each G's fine 5D CH product is rebuilt from these events with its frozen normalization.
  These products are used by V2 and by the reference hybrid H_CH,an (§7).

**Particles.**
- Excluded: |pdg| ∈ {11, 12, 13, 14, 16}, pdg ≥ 1e9 (nuclei and remnants), and GENIE pseudo-particles.
- KE = E − √max(E² − |p|², 0).
- Thresholds: p KE > 100 MeV; n KE > 50 MeV; π± KE > 50 MeV; γ E > 10 MeV; π⁰ and "other" none.
- GiBUU IDs are mapped to PDG codes by ID and charge: 1 to p/n, 101 to π, 102 to η, 110/111 to K, 32 to Λ,
  33 to Σ, and negative IDs to antiparticles.

**F_primary (18 features).**
- The 5 scalars: pT, p∥, E_avail, q3, W.
- E_ν.
- Species energy sums: Σ p KE, Σ π± KE, Σ_EM E (π⁰ and γ), Σ n KE, E_other.
- Multiplicities: n_p and n_π±.
- Leading particles: proton KE and cos θ, π± KE and cos θ, neutron KE. A missing leading particle is NaN, which
  LightGBM treats as missing.

**F_fallback (11 features)**
- The features: the 5 scalars, E_ν, and the five species energy sums.
- **Grounds.** MINERvA's simulated response depends on the per-species visible energy (the proton, meson, EM and
  other bands of BINDING D1) and on the neutron energy. Leading angles and multiplicities act mainly through tracking
  and containment.
- **Use.** There is one fallback only. It is used only if F_primary fails V1–V4 for that G, and only before S3.

**V3 held-out features (not in either F)**
- neutron multiplicity at KE > 10 MeV;
- the per-neutron KE spectrum;
- proton multiplicity at KE > 20 MeV;
- π⁰ count.

**Support (condition 5)**
- **E_ν.** Training stays inside G's E_ν range:
  - GENIE: 0–100 GeV, main sample plus supplement;
  - NuWro: 0.5–100 GeV;
  - GiBUU: 0–20 GeV.
  Tune rows outside that range keep r_h. Their w_truth share is reported per J cell.
- **Fine cells.** In a G-only fine cell, Tune C+H has fewer than 20 rows (FINE_N_MIN, `nd-unfolding/s5p_truths.py:151`)
  while G has rate there. Event weights cannot populate such a cell, and **that rate is not redistributed**.
  - Reported per G: its share of G's in-grid rate, and the amount per J cell in σ_c (MP3-B reading (a)).
  - Tune-only cells: the w_G there is reported.
- **Feature space.** Reported: the share of G's held-out events with p > 0.99, the share of Tune rows with
  w > 50⟨w⟩, and the J cells they fall in.
- **No per-cell anchoring.** w_G is not renormalized cell by cell, which would make V2 trivial. There is only one
  global constant (§4).

## 4. Model

- **Family and settings.**
  - LightGBM 4.6.0 binary classifier, in the root_6_28 environment.
  - learning rate 0.05, 63 leaves, min_child_samples 200, at most 3000 trees, early stopping after 200 rounds.
  - bagging: subsample 0.8 with frequency 1, so that the seeds matter for V5.
  - deterministic, force_row_wise.
- **Validation.** 10% of each model's training rows, by weighted binary logloss.
- **Class weights.** Each class sums to half its split's row count, as in S0.
- **Tune subsample per model.** At most 4,000,000 Tune training rows are drawn uniformly, with a seed per model.
  Prediction covers all of the held-out fold.
- **No weight cap.**
  - A cap would bias the null.
  - A cap at or below 50 would satisfy V4's maximum-weight bound by construction, which would loosen V4.
  - The only clip, p ∈ [1e-9, 1 − 1e-9], is numerical.
  - V4 is evaluated on uncapped weights.
- **Normalization.** w_G = c · p/(1 − p). The constant c is fixed so that the in-grid C+H content Σ w_truth w_G
  equals its value under H_CH,an. The rate is then the generator's rate as the hybrid imposes it.

## 5. Folds and seeds (condition 6)

**What the code does.**
- r_h is computed once over all MCgen rows (`nd-unfolding/s5p_nullexp.py:299`).
- Each experiment draws its own A/B split, `half_mask(n, split_key_for(seed))` (`s5p_nullexp.py:318-320`;
  `s5c_pseudo.py:44-51, :278-281`).
- So no single fold structure can be nested inside every experiment's split.

**Declared: two-level folds.**
- Half: h(i) = `half_mask(n, split_key_for(ASIMOV_SEED = 520261101))`.
- Fold within a half: f(i) = (splitmix64(i ⊕ fold_key_k) ≫ 1) mod 5. This is half_mask's mixer, using the bits above
  its parity bit.
- G events get folds independently, keyed by fold_key_k + 1.
- Model (k, h, f) is trained on the Tune rows of half h outside fold f, and on the G events outside G-fold f. It
  predicts the rows of half h, fold f.
- **For the S3 Asimov split, the weights are nested.**
  - No row is weighted by a model trained on it.
  - No pseudo-data-source row is weighted by a model that saw the unfolding half.
- **For S4's per-experiment splits, the weights are cross-fitted only. This is unsettled (§9).**

**Seeds.**
- K = 5 classifier replicas; fold_key_k = 2026102100 + k; LightGBM random_state_k = 2026102110 + k.
- Tune subsample seed = 2026102120 + 100k + 10h + f.
- V1 split seed 2026102140; G-vs-G split seed 2026102141; rotation seeds as in §3.
- Δ_hyb is the mean over the replicas. V5 is their spread.

## 6. Gates V1–V5, as drafted (condition 1)

**V1. Held-out two-sample test.**
- Samples: the pooled held-out Tune C+H rows (at most 4M, weighted w_truth·w_G) against G's held-out events.
- A fresh classifier with §4's settings is trained on 50% and its AUC measured on the other 50%.
- **Pass: AUC ≤ AUC(G vs G split) + 0.005.**
- The control is trained on G halves of the same sizes, with the tree count **fixed** at the V1 classifier's best
  iteration (capacity-matched). S0's controls stopped after 1–19 iterations.

**V2. Closure against G's harmonized CH product.**
- Compared: the fine 5D and J marginals of the reweighted Tune C+H truth, within the summed sumw2.
- **Pass: χ²/ndf ≤ 1.5 over the fine cells with at least 20 entries on both sides, and no J cell beyond 3σ.**

**V3. Closure on the four held-out distributions of §3.**
- *The draft has no threshold.* **Proposed, flagged: the same as V2.**

**V4. Effective sample size and maximum weight, uncapped.**
- **Pass: Kish ESS(w_truth·w_G) ≥ 0.3 N, with N the number of Tune C+H in-grid rows (the strict reading), and
  max w_G / ⟨w_G⟩_w_truth ≤ 50.**
- ESS/ESS(w_truth) is also reported. S0's Tune-split control had ESS/N = 0.851.

**V5. Seed stability, at S3.**
- **Pass: per J cell, SD_k(Δ_hyb) ≤ 0.2 |mean Δ_hyb|, or ≤ 0.1 δ_fine(c).**
- δ_fine is |δ_M1| from the frozen `m1_shift` declaration (`nd-unfolding/s5p_joint.py:227-234`). *This reading is
  flagged for the director.*

**Order.**
- V1–V4 are evaluated in S2 on F_primary.
- If they fail, F_fallback is tried once, before S3.
- If it fails again, the event-level null for that G is "not established" and A7's hybrid result stands.
- If V5 fails, that G is "not established".
- No tuning is allowed after any S3 or S4 output.

## 7. S3 readout and the replay rule (condition 6)

- **Asimov.** For each G, the noise-free unfolded J cells at `split_key_for(ASIMOV_SEED)`:
  - code path: `s5p_nullexp --expectation --no-nuisance` (`s5p_nullexp.py:31-35, :240-241`);
  - the frozen estimator configuration;
  - one unfolding per event-level replica k, and one per reference hybrid.
- **Two references.** **Primary H_CH,an:** the frozen `fine_ratio` (`s5p_truths.py:165-205`) built from G's harmonized CH product. It
  isolates the effect of hybridization from the target and convention effects.
  **Secondary H_A7:** the frozen r_h. It gives the total change of the null.
- **Δ_hyb(G, c)** = J_event − J_hyb, averaged over the replicas. It is reported in units of σ_c (MP3-B readings
  (a), (b), (c)) and as ΔᵀW⁻¹Δ.
- **Replay, as the κ scan and MP3-B did** (`mp3b_eval.py:166-169`; `publication/kappa/RECORD-20261008-kappa-breakdown.md`).
  - Each of G's null ensembles is shifted, F → F + Δ_hyb, together with every declared shift variant.
  - The statistics come from `s5p_joint.statistics` (`:147`) and `s5p_inference.mc_pvalue` (`:52`). The claim p is
    the largest across the variants.
  - Decisions use Holm with determinacy (`s5p_inference.py:127`) over the frozen family of ten tests. Each
    established G is replaced; the others stay frozen.
  - The replay is repeated at κ = 3.
- **Identity control first.** Δ_hyb = 0 must return A7's decisions exactly.
- **Status.** It is reported beside A7, never as a re-grade (D6).

## 8. Cost (CPU node-h)

| item | basis | estimate |
|---|---|---:|
| S2 harmonization and features | S1 + S0 features measured 0.10 | 0.2–0.4 |
| S2 fits: 4 G × 5 replicas × 2 halves × 5 folds = 200 models | S0: 17 ns per row-iteration at 64 threads; ≤ 6M rows × ~1,500 iterations ≈ 150 s, plus prediction at 1.9 µs per row; packed 4 per node | 0.7–1.2 |
| V1–V4 (8 V1 classifiers, histograms) | as above | ~0.1 |
| fallback, if used | the same again, for the affected G | ≤ 1 |
| S3: 4 G × (5 + 2) Asimov unfolds and the replay | 0.03–0.06 each (`W2A-REPORT-20261006.md:29`); replay ~1 core-h | 0.8–1.7 |
| **S2 + S3** | | **~2–3.5** |

- This is above PLAN §3.4 (S2 ≤ 1, S3 1–2). The two-level folds and the K = 5 replicas roughly double the fits.
- **S4 (about 110–225 CPU node-h)** runs only inside the combined campaign of PLAN §6, under its own contract and
  grant, and only after the S4 nesting question is settled.

## 9. Open caveats and decisions for the director

1. **The 50–100 GeV supplements.** GENIE and NuWro use theirs in training at their constant r. GiBUU stops at 20 GeV.
   Tune rows outside a generator's range keep r_h.
2. **Particle harmonization.** The pseudo-particles, remnants, de-excitation photons, thresholds and the GiBUU ID map
   are declared but not yet verified on all four samples. An S2 preflight lists them, report only. The struck
   nucleon for GiBUU 2p2h events is unsettled.
3. **The split-control early stop.** V1 handles it by capacity matching. S0's own controls stay weak.
4. **S4 nesting.** The folds are nested for the S3 split only. For S4's per-experiment splits the choices are to
   accept cross-fitting or to refit per split, which is not affordable.
5. **V3's threshold** is not in the draft; V2's rule is proposed.
6. **V4's N** is read as the row count, the strict reading.
7. **V5's δ_fine** is read as |δ_M1|.
8. **The primary Δ_hyb reference** is H_CH,an rather than A7's r_h.
9. **Other nuclei** keep r_h (§2).
