# Scalar AUSSIE vs scalar OmniFold: matched robustness comparison (2026-09-25)

**DEVELOPMENT EVIDENCE: simulation only, DEV library, 2 replicates per case.** This is not a selection,
uncertainty or publication result. PET is diagnostic method development.

## Question and verdict

PROTOCOL-20260925 §5 says AUSSIE (arXiv:2602.24282) advances to a PET-backbone evaluation only if it
beats matched scalar OmniFold on robustness or stability. **Under the declared rule, AUSSIE does not
advance.** It loses on robustness and on stability in all 12 matched comparisons: 2 miss-handling pairs ×
2 truth-input sets × 3 OmniFold operating points. It has more moves-away cells, a lower worst-case
per-case R, and seed spreads 2 to 9 times larger. AUSSIE's only advantage is a higher mean R on the
cases close to the development tilt: `dev`, D1 ±0.35 and the unscaled D1 +0.35 control. That advantage
is not the robustness or stability criterion.

## Design (declared and committed in `matched_design.py` at 3808fe3e, before any number was computed)

- **Data.** The predecessor's PET STRESS/FINAL selections of family `confirm-historical-size-v1`:
  - T0/T1 (pool T, replicates 0 and 1): 600,130 prior and 600,111 pseudodata events each.
  - F0/F1 (pool F, replicates 0 and 1).
  - Extraction: `extract_selections.py`, job 58886797, 58 s. It read only simulation members, and every
    cross-check passed (`extract_receipt.json`). The weights come from `replicate_arrays.npz`, which the
    engine normalized in place by a constant factor of 2.4388 to 2.4419 relative to the inventory.
  - Scorer check: the oracle R that `scalar_scoring.py` computes matches the predecessor's PET
    `scores.json` to 1e-10 on all 14 PET runs.
- **Cases (16 units).**
  - F0/F1 with the `dev` tilt.
  - T0/T1 × {D1 −0.35, D2 bump 0.3, D4c p up, D4d n up, D5 NuWro, R1 ×1.05 + D1 +0.35}. R1 is applied as
    on the PET path: it scales the pseudodata's reco E_avail and stored-cluster ΣE and leaves q3
    unchanged.
  - T0/T1 × the derived unscaled D1 +0.35 control (the R1 case's own weights with no scaling). The
    predecessor has no PET run of this control.
- **Inputs.**
  - Reco: p_T, p‖, E_avail, q3, stored-cluster ΣE and count.
  - Truth: `truth4` (E_avail, p_T, p‖, q3), or `truth4_species`, which adds truncated-cloud counts of
    p, n, π±, π0 and other.
- **Normalization.** Engine normalization (1e6 on both step-1 legs) for every method.
- **Matched pairs.**
  - AUSSIE λ = 0 ↔ OmniFold efficiency-corrected.
  - AUSSIE λ = 1000 ↔ OmniFold carry-misses.
  - OmniFold is HistGradientBoosting (the predecessor's `HGBRatio`, sklearn 1.8.0), with k = 3 as the
    primary operating point and k = 10 and k_F0 as secondary ones.
- **Tuning.** Equal opportunity: a 4-point grid per method on F0 only, with `truth4` inputs, seeds 11 and
  12, and mean R as the criterion (OmniFold scored at k = 3).
  - The frozen choices are in `frozen_config.json`: OmniFold `h1` (the predecessor default) for both
    rules; AUSSIE `a1` (lr 1e-3) for λ = 0 and `a3` (lr 3e-4) for λ = 1000.
  - **Limitation:** AUSSIE's epochs axis (20 vs 50) had no effect because early stopping binds first,
    so AUSSIE had 2 effective grid points to OmniFold's 4.
- **Evaluation.** Seeds 1, 2 and 3, so each case has 2 replicates × 3 seeds = 6 cells. IBU is
  deterministic (2 cells per case).
- **Scoring.**
  - Historical seven-bin E_avail recovery R against the replicate's own pseudodata truth.
  - Moves away = residual L1 > injected L1.
  - Joint topology: E_avail × proton class and E_avail × neutron class, both against the pseudodata truth.
- **F0 caveat.** F0 was the tuning selection, so its `dev` numbers are partly in-sample. F1 is not.

## E_avail recovery R (mean over replicates × seeds; `truth4`; bold = moves away in n of N cells)

| case | IBU carry k3 | IBU eff k3 | OF carry k3 | AUSSIE λ=1000 | OF eff k3 | OF eff k10 | AUSSIE λ=0 | oracle | PET C@3 (predecessor) |
|---|---|---|---|---|---|---|---|---|---|
| dev (F0/F1) | 0.483 | 0.923 | 0.418 | 0.699 | 0.783 | 0.817 | 0.894 | 0.988 | 0.534 |
| D1_m0.350 | 0.393 | 0.835 | 0.355 | 0.534 | 0.780 | 0.805 | 0.899 | 0.979 | 0.407 |
| D2_bump_c0.3 | 0.535 | 0.468 | 0.359 | 0.340 | 0.525 | 0.540 | 0.494 | 0.946 | 0.252 |
| D4c_p_up | 0.232 | **−0.381** (1/2) | 0.236 | **−0.084** (5/6) | 0.449 | 0.475 | **−3.876** (6/6) | 0.823 | 0.131 |
| D4d_n_up | **−0.309** (2/2) | **−1.460** (2/2) | **−0.217** (6/6) | **−1.077** (6/6) | **−0.392** (6/6) | **−0.403** (6/6) | **−2.632** (6/6) | 0.543 | 0.017 |
| D5_nuwro | 0.492 | 0.085 | 0.481 | 0.403 | 0.458 | 0.534 | 0.364 | 0.949 | 0.238 |
| R1_x1.05+D1_p0.350 | 0.536 | 0.894 | 0.473 | 0.236 | 0.838 | 0.883 | **0.266** (2/6) | 0.987 | 0.842 |
| D1_p0.350 (derived control) | 0.473 | 0.891 | 0.415 | 0.697 | 0.734 | 0.743 | 0.869 | 0.987 | – |

With species-count truth inputs (`truth4_species`), R (moves away) is:

| case | OF carry k3 | AUSSIE λ=1000 | OF eff k3 | AUSSIE λ=0 |
|---|---|---|---|---|
| dev | 0.416 | 0.736 | 0.780 | 0.859 |
| D2_bump_c0.3 | 0.355 | 0.420 | 0.524 | 0.432 |
| D4c_p_up | 0.328 | 0.185 (2/6) | 0.482 | 0.248 (1/6) |
| D4d_n_up | −0.230 (6/6) | −0.985 (6/6) | −0.352 (6/6) | −0.735 (5/6) |
| D5_nuwro | 0.477 | 0.366 | 0.458 | 0.272 |
| R1_x1.05+D1_p0.350 | 0.470 | 0.360 | 0.845 | 0.269 (1/6) |

## Declared decision rule, library level (48 cells per method; OmniFold at k = 3)

| pair, inputs | moves-away cells A / OF | worst-case mean R A / OF | median seed SD A / OF | max seed SD A / OF | robustness win | stability win |
|---|---|---|---|---|---|---|
| λ=1000 vs carry, truth4 | 11 / 6 | −1.077 / −0.217 | 0.068 / 0.007 | 0.586 / 0.044 | no | no |
| λ=0 vs eff, truth4 | 14 / 6 | −3.876 / −0.392 | 0.066 / 0.033 | 1.985 / 0.191 | no | no |
| λ=1000 vs carry, species | 8 / 6 | −0.985 / −0.230 | 0.044 / 0.010 | 0.616 / 0.047 | no | no |
| λ=0 vs eff, species | 7 / 6 | −0.735 / −0.352 | 0.076 / 0.032 | 0.603 / 0.160 | no | no |

The outcome is the same at OmniFold k = 10 and k_F0 (k_F0 = 10, except 7 for eff with species inputs).
All numbers are in `results/SCALAR_AUSSIE_MATCHED-20260925.json` → `decision`.

## Findings

1. **AUSSIE's gain is on tilt-like cases and it is fragile elsewhere.**
   - λ = 0 beats efficiency-corrected OmniFold on `dev`, D1 −0.35 and the D1 +0.35 control (0.894 vs
     0.783, 0.899 vs 0.780, 0.869 vs 0.734).
   - It collapses under the hadron-content cases D4c (−3.876, every cell away; seed SD 1.62 on T0/T1) and
     D4d (−2.632).
   - Under R1 it moves away in 2 of 6 cells.
2. **R1 has a real response effect for AUSSIE and not for OmniFold.** Compare each method's R1 score with
   its unscaled D1 +0.35 control:
   - AUSSIE λ = 0: 0.266 vs 0.869; λ = 1000: 0.236 vs 0.697.
   - OmniFold eff: 0.838 vs 0.734.
   - IBU eff: 0.894 vs 0.891.
3. **Every scalar method moves away under D4d.**
   - D4d raises neutron multiplicity at fixed E_avail; the oracle R is only 0.543 there.
   - All three methods, under both miss rules, move away in every cell.
   - The predecessor's PET C@3 stays just positive (0.017).
4. **Species-count truth inputs help AUSSIE the most, but not enough.** For AUSSIE λ = 0, D4c improves
   from −3.876 to 0.248 and D4d from −2.632 to −0.735, and the joint E_avail × p recovery under D4c
   reaches 0.78. It still loses on worst case and on seed spread.
5. **Joint topology: nothing recovers the D4 hadron-class structure.** Every scalar method with `truth4`
   inputs has joint E_avail × p and E_avail × n recovery ≈ 0.00 to 0.02. AUSSIE λ = 0 is the exception
   and goes negative (D4c −0.13 / −0.65, moving away in 5 and 6 cells). On the other cases the joint
   recoveries follow E_avail R.
6. **Miss handling still dominates at scalar level.** It separates results more than the choice of
   method does (IBU eff k3 = 0.923 on `dev`), as the predecessor's Phase F concluded.
7. **Runtime** (seconds per run, M-series Mac with 3 threads, mean / max):

   | method | mean | max |
   |---|---|---|
   | AUSSIE | 14–20 | 40 |
   | OmniFold (10 iterations) | 25–38 | 79 |
   | IBU (10 iterations) | 4 | 5 |

   The full evaluation (416 tasks) took 3449 s wall time with 3 workers.

## Reproduction

The code is `nd-unfolding/pet/final_design/scalar/`. The steps are:

1. `extract_selections.py` on the cluster.
2. `run_matched.py --stage tune`, then `summarize_matched.py --freeze`.
3. `run_matched.py --stage eval`, then `summarize_matched.py`.

The per-task rows are in `results/matched_task_rows-20260925.jsonl.gz`. Tests are in
`test_scalar_matched.py`.
