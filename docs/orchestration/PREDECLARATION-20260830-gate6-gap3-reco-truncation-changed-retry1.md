# Predeclaration — Gate-6 GAP 3 reco truncation changed retry 1

**Contract ID:** `PET-G6-GAP3-RECO-TRUNCATION-20260830-CHANGED-RETRY1`

**Status:** authorized for exactly one changed CPU-only retry. The original authorization is
exhausted. An unchanged, automatic, or further retry is forbidden. Submission is allowed only after
this contract, its machine proposal, wrapper, reissued launcher, and tests are committed, pushed, and
hash-bound from a clean immutable checkout.

## Change and preserved evidence

The original predeclaration, launcher, launch receipt, and terminal receipt remain immutable. Their
required SHA-256 values are:

| artifact | SHA-256 |
|---|---|
| `PREDECLARATION-20260830-gate6-gap3-reco-truncation-audit.md` | `b69c296a1bd9be426c8acf78bd1232b780bd3c9e2b0b7924d09d241feb8260fc` |
| `nd-unfolding/pet/sbatch_gap3_reco_truncation_audit.sh` | `4c23d6a2e2ee770a424c92d8c9eda67ac56dc3c7b8265dfdc3add73fe4325cfe` |
| `state/gate6-gap3-reco-truncation-launch-57727806.json` | `ade8f8755fa8cab04934e3828c651a9b131fe0a029c144533b52a2b671acf8e9` |
| `state/gate6-gap3-reco-truncation-terminal-57727806.json` | `4fcb7a58102e2c3e9f41808bc9bb68e8884a24b4602eac79252476e3f42fbb80` |

The only execution change is the scheduler/resource contract: request and require 18 CPUs, use 18
ROOT audit threads, retain 32 GiB, reduce walltime to two hours, and request no GPU. This is an exact
36 CPU-hour allocation ceiling. The changed wrapper imports the original audit core at SHA-256
`671531dd6a43a03203d4a8024d5671a7b357edad6e1fa7ab9ad7e44a99ac1e1a`;
no scientific implementation is copied or edited.

## Frozen scientific question, source, and populations

The run measures only the fraction of reco clusters and deposited cluster energy discarded beyond
descending energy rank 12, in aggregate and versus the predeclared kinematics. It uses only:

- source `nd-unfolding/g2_fullevent/merged/runEventLoopOmniFold_G2_FPS_MEFHC.root`;
- size `113496440965` bytes;
- SHA-256 `9a16331f1c02103e3b5de5e6c00139aa39393ee11eb34881bea0b9a890344e2f`;
- merge receipt SHA-256
  `26ea5561f47599987ebacbf594c606309146a5f23c82af8dd0e2ca299b31efa7`;
- signal tree `mc_signal_reco`, original selection, expected rows `20,573,521`;
- data tree `data`, original selection, expected rows `4,116,128`; and
- background tree `mc_background`, original selection, expected rows `564,591`.

The runtime must recompute the full source SHA-256 before ROOT event I/O. The exact selections remain
those in the original audit core: signal uses `sim_pass != 0` with finite `sim,sim_pz` in
`[0,30] x [0,120]`; data uses `measured_pass != 0` with finite `measured,measured_pz` in that domain;
background uses `sim_background_pass != 0` with finite
`sim_background,sim_background_pz` in that domain.

## Frozen cluster and weighting operands

For each selected event, `E` is the complete `part_reco_E` vector after the source getter excludes
`cluster_isMuontrack != 0`. After stable descending-energy sorting:

- `N_all = len(E)`;
- `N_drop = max(N_all - 12, 0)`;
- `E_all = sum(E)`;
- `E_drop = sum(E[12:])`;
- `f_N = sum(N_drop) / sum(N_all)`;
- `f_E = sum(E_drop) / sum(E_all)`; and
- `f_cap = count(N_all > 12) / count(events)`.

Primary results remain unweighted micro-fractions for signal, data, background, and combined MC.
Secondary diagnostics remain weighted by `w_reco`, unit data weight, and `w_bkg`, respectively.
Non-finite or negative energy or weight values, a non-positive denominator, or a census mismatch make
the result `INVALID_OR_INCOMPLETE`; zero-energy clusters are counted and reported.

## Frozen kinematic dependence

Every bin retains all numerator and denominator operands, with null fractions for empty bins:

- reco `pT`: `[0, 0.07, 0.15, 0.25, 0.33, 0.4, 0.47, 0.55, 0.7, 0.85, 1.0, 1.25, 1.5, 2.5, 4.5, 30]` GeV;
- reco `p_parallel`: `[0, 0.75, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 6, 7, 8, 9, 10, 15, 20, 40, 60, 120]` GeV;
- reco `Eavail`: `[0, 0.1, 0.2, 0.4, 0.8, 1.5, 3, 100]` GeV;
- reco `q3`: `[0, 0.2, 0.4, 0.6, 0.8, 1.2, 2, 100]` GeV; and
- the Cartesian grid of the frozen reco `pT` and `p_parallel` edges.

Axis branches remain `sim,sim_pz,sim_eavail,sim_q3` for signal;
`measured,measured_pz,measured_eavail,measured_q3` for data; and
`sim_background,sim_background_pz,sim_background_eavail,sim_background_q3` for background.
No post-result search, adaptive binning, threshold selection, or materiality category is allowed.

## Execution and validation contract

- exactly one Slurm job, with a new output namespace;
- CPU constraint; 18 CPUs; 18 ROOT threads; two hours; 32 GiB; no GPU;
- allocation ceiling `18 x 2 = 36` CPU-hours;
- one source SHA-256 pass plus one streaming event pass per named tree;
- clean pushed immutable checkout and exact expected commit;
- authorization token
  `PET-G6-GAP3-RECO-TRUNCATION-20260830-CHANGED-RETRY1-ONE-SCAN`;
- positive and negative resource-guard tests before submission; and
- no collision, array, requeue, automatic retry, unchanged retry, or further retry.

Before submission, the preflight must validate ROOT import and helper JIT, the full source and receipt
hashes, original-artifact immutability, new artifact hashes, the exact Gate-6 receipt, positive and
negative resource guards, and the clean pushed checkout. The runtime repeats the applicable checks.

## Terminal readings and non-authorization

`PASS` requires exact provenance, schema, selected-row censuses, finite/non-negative energy and weight
domains, positive denominators, all aggregate/bin operands, result JSON, logs, and matching Slurm
accounting. Any failure is terminal `INVALID_OR_INCOMPLETE` and authorizes no retry.

Every terminal outcome leaves Gate 6 blocked and cannot:

- change the PET representation or token cap;
- move or adopt a central value;
- construct `C_ML`, another covariance, or an uncertainty;
- select a Gate-6 member or start Leg 2;
- establish equivalence, convergence, closure, or coverage;
- support a publication claim or edit a publication deliverable; or
- authorize any further compute.
