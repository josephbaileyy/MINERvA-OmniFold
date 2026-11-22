# 2D covariance fix: inventory of what already exists (cov2d, 2026-11-22, origin/main 7d5a98361)

Paths are under docs/orchestration/ unless they start otherwise. FD = state/measurement-paper/5d-community-20261024/fd.
All numbers are copied from the named record. Nothing was recomputed.

## 1. Records the director named

**T2A split** (FD/tier2-20261110/READING-T2-20261110.md; records t2a/t2a_{AR23,G18}.json)

| | AR23 | G18 |
|---|---|---|
| mean χ²/ndf | 16.55 | 24.17 |
| mean-error part ēᵀC⁺ē per ndf | 13.61 (82 % of the mean χ²) | 20.97 (87 %) |
| spread part tr(C⁺S) per ndf | 2.94 | 3.21 |
| mean-error share beyond rank 73 | 77 % | 87 % |
| mean-error share in the top 32 directions | 0.7 % | 0.9 % |
| mean spread per component, ranks 1–73 / 74–139 / ≥140 | 1.6 / 3.0 / 4.4 | 1.5 / 3.6 / 4.7 |
| joint test truncated to rank 73 or 139 | 0 / 0 of 300 | 0 / 0 of 300 |

The fluctuation is under-described too, not only the bias. The spread exceeds C_T's prediction even in ranks 1–73,
and the excess grows toward the small modes.

**G2R regrade** (FD/receipts-cov2d/g2r/readout/README.md; adopted in DECISION-20261114-joseph-d1-g2r-adopted.md)
- Under the rebuilt C_T′ the coverage is identical to COV2D's: G18 0/300 (cell 29); AR23 0/300 (cells 29, 56); every
  flag is bias-driven.
- At the data, ε against C_rep is 25.833 on 205 directions (5.999 on the top 73).

**10-05 fixed-truth coverage FAIL** (OUTCOME-20261005-2d-fixed-truth-coverage-fail.md; KNOWN_ISSUES.md row 84)
- Nominal truth, Poisson data plus the MC bootstrap stream, per-bin z against the stat band VL162:
  - C1 0.679 (nominal);
  - C2 0.912 against the window [0.928, 0.972]: FAIL;
  - pull RMS 1.6, pull mean consistent with 0.
- It was attributed in part to the bootstrapped completeness. That was fixed, and band VL170 was adopted on 10-06.
- **VL170 has not been re-tested.** The post hoc rescoring is circular in the MC part: C1 0.781, C2 0.977. A re-test
  needs non-circular MC (KNOWN_ISSUES 85). The test was per-bin, never in eigenmodes, and covered only the stat band.

**11-11 consult and (a+)** (state/2d-closeout/stageF/methods/secondary-results/consult-sol-2dregrade-20261111/README.md)
- The consult was gpt-6.1-sol. It recommended (a+): the consistent universe rebuild, plus C_T rebuilt at both tunes, plus
  the regrade. It judged a reversal unlikely but not excluded. The director declared (a+), which became G2R.

**COV2D itself** (OUTCOME-20261108-cov2d-both-tunes-under-cover.md; COV2D-DECLARATION.md §4)
- UNDER-COVERS at both tunes: joint 0 of 300 (k_J 190 and 192); χ²/ndf 16.55 ± 0.17 and 24.17 ± 0.37.
- Bias |ē|/σ_c median 0.114 and 0.092 (max 1.04 and 0.96). The spread alone, against C_T without C_model, gives a
  median p̂ of 0.67 and 0.65.

## 2. What a1, c1 and c2 became (methods-scoping SCOPING.md §a/§c → REGRADE)

- a1 and c1 were declared together as **REGRADE** (FD/regrade-crep-20261121/REGRADE-DECLARATION.md rev 2.1;
  REGRADE-BINDING-NOTE.md; amendment 1 for the A0(b) tolerance, κ-scaled).
- **The 2D half ran** locally (cov2d) against C′ = C_T + C_run(T), fractional carry:
  - AR23: run2d/regrade_2d.json, code 058bca19;
  - G18: run2d-g18/regrade_2d_g18.json, code 479e03cc, after amendment 1. The first G18 run stopped at A0(b): 1.73e-8
    against the flat 1e-9 (κ₂ ≈ 9.5e11).

| | AR23 | G18 |
|---|---|---|
| M′ (SE) | 16.350 (0.170) | 22.776 (0.351) |
| mean-error / spread part | 13.469 / 2.881 | 19.644 / 3.132 |
| τ = tr(C′⁺C_run)/ndf | 0.0098 | 0.0098 |
| M_full | 16.360 | 22.786 |
| reading | under-describes on average | under-describes on average |
| descriptive regrade | 0/300 (k′ 190) | 0/300 (k′ 192) |

  The run-period block changes essentially nothing. The absolute-carry sensitivity case gives M_full 16.351 at AR23.
- **The 16-cell half also ran** (run16/, read once): R-χ² "under-describes on average" at all four. M_full is 1.82
  (g18) and 2.54 (ar23). Descriptive joint counts are 75, 76, 20 and 27 against k′ 193. This is 5D context only.
<!-- absence-ok: scoping statement about studies not yet run or not run as scoped, each routed to its record -->
- **c2 did not run as scoped.** The projection of T2A's mean error onto C_run's two directions was never computed.
  The regrade's τ, the trace contribution, is the related quantity and is 0.0098 per ndf.

## 3. The review's matrix: what is measured

<!-- absence-ok: scoping statement about studies not yet run or not run as scoped, each routed to its record -->
| cell | measured? | record | gives | gap |
|---|---|---|---|---|
| 1. nominal truth, data Poisson only | **No**, not against the current Q_R | IBUKT A2 nominal: 5 draws, residuals only; noise-free nominal max residual 1.708 % (OUTCOME-20261119-ibukt-a2.md) | no covariance comparison | a ≥ 300-toy ensemble against C_stat's data stream, in eigenmodes |
| 2. nominal truth, data + MC fluctuations | **Only on a superseded band**, per-bin | 10-05: FAIL on VL162; VL170 untested (KI 84/85) | stat band only | an eigenmode test against the current C_stat with non-circular MC streams |
| 3. coherent nuisances | **Not at nominal truth.** At the tunes, yes (inside cell 5) | COV2D draws all 38 systematic bands per toy, on reco and truth | — | a nominal-truth nuisance ensemble against C_syst |
| 4. alternative truth, fixed response | **Bias only, no covariance** | IBUKT A2: 7 truths (nominal, genie_mec, nuwro, bump, tilt, within±) × 5 Poisson draws, nominal response; b1 projected its mean residual on Δ in V_pub's modes. C_model's shifts (PV2D maps) are this cell by construction. | b at 7 truths, at 5-draw noise | b bᵀ against C in Q_R's modes; enough draws to separate b from noise |
| 5. alternative truth, perturbed response | **Yes** | COV2D/G2R at G18 and AR23 (300 toys each; data Poisson + 38 bands); T2A; REGRADE | the split above | the toys never drew sim-statistics (MC) fluctuation, estimator seed (C08), C_PL/C_run or C_model |

Never drawn anywhere: the simulation-statistics fluctuation of the response, the estimator seed, and the run-period
blocks. The last has no generative law (SCOPING a3) and can only enter as covariance.

## 4. Truths available for unseen validation

- **G18 and AR23 are seen.** COV2D, T2A, G2R, REGRADE and the 5D LL5D/F0b chain all read them, so they can build or
  calibrate a construction but cannot validate it.
- **C_model's generators are building blocks of Q_R:** GENIE 2.12 + MEC, NuWro, GiBUU, and the PV2D ratio maps
  genie_mec, nuwro, gibuu, tune_v1 and their _sq variants.
- **A2's synthetic truths are seen:** bump, tilt, within±.
- **No other generator sample or tune is committed.** But F1 generated both GENIE v3 tunes itself for a total of
  1.3275 node-h, with event generation plus the bridged ratio (FD-F1-REPORT.md:143). New, never-read tunes can
  therefore be generated cheaply as the unseen validation set.

## 5. Costs on record

- COV2D: 112.74 node-h for 600 toys plus pilots (FD/receipts-cov2d/a2/bulk/README.md), so about 0.19 node-h per toy.
- G2R: cap 110, 98.3 held at the last gate.
- F1: 1.3275 node-h for two tunes.
- The REGRADE 2D half: 0.

<!-- absence-ok: an inventory of which studies exist, each routed to its record -->
