# High-E_avail / high-W inelastic investigation: frozen plan

**Date 2026-10-11. Owner: this session (inelastic-high-region lane). Base: remote `main` `3892e769`.**
Frozen before any scientific reduction. Changes after this commit are recorded as amendments with a reason
and never alter a decision rule after its inputs have been seen.

## 1. Decision this work answers

Do the high-available-energy, high-W discrepancies of the MINERvA ME-FHC 5D result motivate a
*physically constrained* inelastic-physics improvement, after normalization, energy coverage, detector
response and estimator effects are accounted for? Terminal outcomes are **GO** (one named candidate merits
a separately authorized validation), **NO-GO** (the region carries no discrepancy that needs a new inelastic
mechanism), or **INCONCLUSIVE** (a residual exists but cannot be separated from response, estimator or
missing inputs). "No new model" is a valid outcome. GO authorizes no compute, fit, adoption or contact.

The predecessor memo (`docs/research/MINERVA-MODEL-IMPROVEMENT-MEMO-20261011.md`, local, uncommitted,
preserved unmodified) and the Valencia feasibility pilot (`study/valencia-feasibility-20261011`, `d75987e1`)
address the low-E_avail multinucleon region. They do not explain the high region and are not re-run.

## 2. Roles, budget and stopping

- **Owner:** this session — plan, reductions, derivation, memo. **Reviewer:** one fresh, read-only subagent on
  the frozen report commit in a detached worktree, with no access to the owner's reasoning. This is not
  independent domain validation. **One** focused correction pass follows; no second review round.
- **Literature:** one delegated read-only web-research agent (no contact, no posting). Its claims enter the memo
  only after the owner opens the cited passage or marks them as unverified.
- **Budget:** at most **2 CPU core-hours (7,200 core-s)** in aggregate, for all reductions, review reruns and
  the correction pass. Enforced by `code/budget.py`: every scientific run goes through it, it refuses a launch
  whose declared cap would push the ledger total past 7,200 core-s, it applies `ulimit -t` to the run, and it
  charges the full cap when a run's CPU cannot be measured. Allocation: owner reductions ≤ 3,600 s; reviewer ≤
  1,800 s; correction pass ≤ 1,000 s; reserve 800 s. Pre-plan inspection (listing and hashing products) is
  charged as one conservative 30 core-s entry.
- **Forbidden:** event generation, GPU, paid resources, detector simulation, fits to our data, unfolding or
  retraining, covariance construction or use of the adopted 5D covariance for inference, quarantined
  significances, analysis/publication adoption, external contact, restarting closed campaigns, writes to any
  product or shared path other than a new scratch directory.
- **Stop** at the decision of §6, after the review and correction pass. No new questions are added after the
  reductions have been seen.

## 3. Inputs (read-only; digests must match before use)

| Role | Product | SHA-256 |
|---|---|---|
| Unfolded data, production 5D (LightGBM, 5 iterations) | `nd-unfolding/products/5d/xsec_5d_MEFHC_5iter_lgbm.root` | `630306e2…` |
| Tune v1 (analysis MC truth, unfolding prior) | `s5p-20260926/gen5d/mnvtune_v1_xsec5d.npz` | `bf7bd278…` |
| GENIE 2.12.10 CV, flux-repaired, 0–100 GeV | `gen5d_fluxfix/genie_cv_xsec5d_full.npz` | `cfa42210…` |
| GENIE 2.12.10 + Valencia MEC | `gen5d_fluxfix/genie_mec_xsec5d_full.npz` | `c179855d…` |
| NuWro 21.09 | `gen5d_fluxfix/nuwro_cv_xsec5d_full.npz` | `475a2871…` |
| GiBUU 2019 (E_ν ≤ 20 GeV) | `gen5d_fluxfix/gibuu_cv_xsec5d_fluxfix.npz` | `48917692…` |
| Released figure arrays (control) | `fig_arrays.npz` | `72394a2b…` |
| Estimator-R data unfolds, δ = 0, −4%, +4% recoil (W2B) | `w2b/unf/w2b_rr{zero,0,1}_b-_j-.npz` | per W2B manifests |
| Estimator-R frozen data central and numerical jitters | `s5p-20260926/runs/s2/num/data/data_b-_j{-,1,2,3}.npz` | recorded on read |
| Recorded estimator/background biases (per EW cell) | `state/s5n/stage1/dev_receipt.json`, `state/s5c/d1/d1_summary.json` | committed |
| GENIE CV events (event-level model decomposition only) | `genie_mefhc_cv_ALL.gst.root` + supplement, via the s5p flux-fix code | per `gen5d-fluxfix*.json` |

## 4. Definitions (frozen)

- Grid: the committed 5D grid (p_T 14, p_∥ 16, E_avail 7, q3 7, W 6 bins). Cell-integrated σ = density × bin
  volume. `A ≡ E_avail`. EW index = 6·i_A + i_W.
- **Region C** ("corner"): A ≥ 0.8 GeV and W ≥ 1.8 GeV, all q3, p_T, p_∥ (EW27–29, 33–35, 39–41). **Region M**
  (intermediate W): 1.4 ≤ W < 1.8 GeV. **Overflow cells**: any cell with A ∈ [3,100) or W ∈ [3,100).
- Ratios are data/prediction. ρ_X = R_X / R_total (normalization-removed contrast); f_X = σ_X/σ_total.
- **Support-complete domain S20:** cells whose kinematic upper bound on E_ν is below 20 GeV, where
  E_ν = E_μ + ω, E_μ ≤ (p_T,hi² + p_∥,hi² + m_μ²)^½ and ω ≤ (W_hi² + q3_hi² + m_μ²)^½ − M (derived in the memo
  from the analysis definitions of q3 and W). GiBUU is compared on S20 only, as the support-matched statement.
- **Hierarchical decomposition** (§5 R3). With muon cell m = (p_T, p_∥), transfer cell t = (q3, W) and A bin a,
  σ(m,t,a) = σ(m) P(t|m) P(a|m,t). Successive substitutions of the data's factors into a prediction give the
  corner-ratio steps: rate; muon shape; transfer given muon (inclusive response); A given transfer
  (final-state partition). Reported in both orders (inclusive-first and partition-first). Empty prediction
  conditionals fall back to the prediction's P(a|t) over all m, with the affected data fraction reported.

## 5. Reductions

- **R1 reproduction and rate/shape/coverage (Q1).** Project every product to the 42-cell (A,W) grid. Controls:
  VL156 (1.142/1.139/1.160/1.607), VL157 totals, the paper's Tune v1 shares (67.215%, 83.172%, 21.947%) and the
  released arrays. Report R_total, R_C, ρ_C, R_M, ρ_M, f_C for data and every prediction; cell-integrated
  differences raw and with the prediction normalized to the data total (a diagnostic, not evidence that flux
  explains the rate); overflow contributions explicitly; P(W | A band) and P(A | W band).
- **R2 support.** S20 cell set; ratios of all predictions on S20 ∩ C and S20; GENIE CV event-level E_ν bands
  (< 5, 5–10, 10–20, 20–50, 50–100 GeV) of C, as model information only — never as a correction to GiBUU.
- **R3 decomposition (Q2).** §4 decomposition for Tune v1 and the three complete-support external predictions,
  and for GiBUU on S20. MC-statistical spread by 200 Gaussian cell replicas from `sumw2` (seed 20261011).
- **R4 response and estimator sensitivity (competing explanation).** Estimator R: the ±4% recoil unfolds minus
  δ = 0 for R_C, ρ_C, ρ_M and the partition step; three numerical jitters minus central (floor); R central
  versus the production estimator. Recorded biases read, not recomputed: s5n C4 E_avail-shape regularization
  residual and s5c purity background bias, aggregated to C and M with data-cell weights.
- **R5 event-level GENIE CV model decomposition (labels are model labels, not observed mechanisms).** In C and M:
  QE/RES/DIS/COH fractions; H versus C target share and the C-only/CH per-nucleon ratio; E_avail carried by p,
  π±, π⁰+γ; visible fraction A/ω and neutron energy fraction; generator invariant mass W_gen against the
  analysis W estimator. Run on Perlmutter login nodes through the ledger with the s5p flux-fix reader.
- **R6 literature and derivation (Q3).** At most three explanations: (i) inelastic rate / RES–SIS–DIS matching;
  (ii) hadronization and nuclear energy partition / FSI; (iii) response/estimator. QFT-to-observable derivation
  from the hadronic tensor to the binned observables, with the expected sign pattern of each candidate in C, M,
  the total and the muon variables.

## 6. Decision rule (frozen before the reductions)

Let ρ_C^G be the normalization-removed corner contrast against each complete-support external prediction
G ∈ {GENIE CV, GENIE+MEC, NuWro}, and let the *computed sensitivity* S_C be the larger of (a) the ±4% recoil
shift of ρ_C and (b) the C-only versus CH target effect, each measured here. Let B_C be the recorded estimator
scale in C (s5n E_avail-shape regularization residual and s5c background bias, aggregated).

- **NO-GO** if |ρ_C^G − 1| ≤ S_C for all three G, *or* the signs of ρ_C^G − 1 disagree among them: the corner
  then carries no normalization-independent discrepancy that a new inelastic mechanism is needed for.
- **GO** only if all hold: |ρ_C^G − 1| > max(2 S_C, B_C) for all three G with one sign; the decomposition places
  ≥ 2/3 of the corner residual in the same factor (inclusive transfer *or* partition) in both orders and for all
  three G; and R6 identifies one existing, independently constrained mechanism with that sign pattern in C, M
  and the total, without double counting.
- **INCONCLUSIVE** otherwise, including a residual above S_C but not above B_C, unstable localization, or a
  missing input. The memo names the missing input.

The Tune v1 map is descriptive and prior-coupled (the data were unfolded with Tune v1 as prior); it informs but
does not enter the rule. GiBUU enters only on S20. Region M is reported with the same quantities and is used in
R6 as the intermediate-W overshoot check for any candidate.

## 7. Outputs

`REPORT.md` (the research memo), `REVIEW.md`, `code/`, `results/*.json`, `logs/budget_ledger.jsonl`, plus the
required CATALOG and MANIFEST rows. Task branch `study/inelastic-high-region-20261011`; not merged.

## 8. Amendments

**Amendment 1 (2026-10-11, after R1, R3/R4 had been seen; descriptive only, no change to §6).**
Reason: R1/R3 showed that region C mixes opposite-sign sub-regions (non-overflow versus overflow cells) and that
the largest normalization-independent feature is at 1.4 ≤ W < 2.2 GeV, outside C. To report that faithfully
without redefining C, three descriptive reductions are added. None enters the decision rule, whose inputs
(ρ_C^G, S_C, B_C) are unchanged.
- **A1-a** Per-W-bin and per-E_avail-bin (within W ≥ 1.8) profiles of the frozen R3 decomposition and of the ±4%
  recoil shifts (`reduce_r4b.py`), and the recorded biases split into C's non-overflow and overflow cells.
- **A1-b** The published 2D comparison as a rate check independent of the hadronic axes: released `paper_v`
  against `tune_v1_v` (total and p_T slices) from `fig_arrays.npz`.
- **A1-c** GENIE 2.12.10 inclusive σ_CC/E per nucleon from the committed spline graphs at 3–50 GeV (isoscalar C12
  and the CH mixture), for comparison with published NOMAD and MINOS σ/E tables opened by the owner.

**Amendment 2 (2026-10-11, after R1–R4 and the literature report; descriptive only, no change to §6).**
Reason: the only existing, independently (H/D) constrained inelastic change the literature identifies is the GENIE
v3 bare-nucleon tune G18_02a_02_11b (Tena-Vidal et al., PRD 104, 072009, Table VI, verified by the owner). Its
sign pattern in C, M and the total is needed for R6. **A1-d**: a first-order emulation by reweighting the existing
GENIE 2.12.10 CV events (no generation): RES × 0.84/1.0 (S_RES); DIS × 1.062/1.032 (S_DIS); nonresonant events
(DIS with generator W < 1.7 GeV) of primary hadronic multiplicity 2 or 3 × R_new/R_old with R = (νp: 0.008/0.10,
0.94/1.00; νn: 0.03/0.30, 2.3/1.00), as GENIE ReWeight's non-resonant-background dial does. The W_cut move to 1.81
GeV and the RES axial-mass change are not reweightable and are omitted; this is not a GENIE v3 prediction, is not
fitted, and is reported only as the candidate's approximate sign and size in C, M, the total and per W bin.
