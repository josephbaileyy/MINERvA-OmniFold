# Predeclaration — Gate-6 GAP 3 reco-cloud truncation audit

**Contract ID:** `PET-G6-GAP3-RECO-TRUNCATION-20260830`

**Status:** conditionally authorized for one CPU-only scan on 2026-08-30. The scan may run only
after this contract, its streaming implementation, and its launcher are committed and hash-bound.
There is no retry authorization.

## Question and scope

The full-event PET reco cloud retains the twelve highest-energy non-muon-track calorimeter clusters.
This audit measures, from the variable-length source branches before truncation:

1. the fraction of clusters discarded beyond energy rank 12;
2. the fraction of deposited cluster energy discarded beyond energy rank 12; and
3. both fractions as functions of reconstructed event kinematics.

The result is representation diagnostics only. It may inform whether a separately proposed token-cap
study is worth considering. It cannot authorize a representation change, a central-value change,
covariance construction, a publication claim, training, or any further compute.

## Frozen source and population

The only allowed source is the committed Gate-1 merged full-event ROOT:

- repository-relative path:
  `nd-unfolding/g2_fullevent/merged/runEventLoopOmniFold_G2_FPS_MEFHC.root`;
- size: `113496440965` bytes;
- SHA-256: `9a16331f1c02103e3b5de5e6c00139aa39393ee11eb34881bea0b9a890344e2f`;
- merge receipt SHA-256:
  `26ea5561f47599987ebacbf594c606309146a5f23c82af8dd0e2ca299b31efa7`.

The runtime must recompute the ROOT SHA-256 before the event scan. The three selected populations
must reproduce the already committed P=12 input census exactly:

| population | tree | selection | expected rows |
|---|---|---|---:|
| signal MC reco | `mc_signal_reco` | `sim_pass != 0` and finite `sim,sim_pz` inside `[0,30] x [0,120]` GeV | 20,573,521 |
| data | `data` | `measured_pass != 0` and finite `measured,measured_pz` inside the same domain | 4,116,128 |
| MC background | `mc_background` | `sim_background_pass != 0` and finite `sim_background,sim_background_pz` inside the same domain | 564,591 |

A row-count mismatch makes the measurement `INVALID_OR_INCOMPLETE`; it does not license changing
the selection.

## Frozen cluster definitions

For each selected event, let `E` be the full `part_reco_E` vector written by
`CVUniverse::GetRecoClusters`, after its `cluster_isMuontrack != 0` exclusion. Sort finite values by
descending energy, matching the production P=12 loader. Define:

- `N_all = len(E)`;
- `N_drop = max(N_all - 12, 0)`;
- `E_all = sum(E)`;
- `E_drop = sum(E[12:])` after descending-energy sorting;
- aggregate cluster fraction `f_N = sum(N_drop) / sum(N_all)`;
- aggregate deposited-energy fraction `f_E = sum(E_drop) / sum(E_all)`; and
- cap-reaching event fraction `f_cap = count(N_all > 12) / count(events)`.

The primary results are unweighted micro-fractions, reported separately for signal MC, data, and MC
background and for signal-plus-background MC. Secondary analysis-weighted diagnostics use `w_reco`
for signal, unit weight for data, and `w_bkg` for background. They do not replace the primary values.

Non-finite or negative cluster energies, non-finite or negative analysis weights, a non-positive
energy denominator, or a selected-row mismatch make the corresponding measurement
`INVALID_OR_INCOMPLETE`. Zero-energy clusters are counted and reported because the source getter does
not remove them.

## Frozen kinematic dependence

Every bin reports selected-event count, cap-reaching events, total/discarded clusters, and
total/discarded energy, followed by fractions derived from those operands. Empty bins remain present
with null fractions.

- reco `pT` edges in GeV:
  `[0, 0.07, 0.15, 0.25, 0.33, 0.4, 0.47, 0.55, 0.7, 0.85, 1.0, 1.25, 1.5, 2.5, 4.5, 30]`;
- reco `p_parallel` edges in GeV:
  `[0, 0.75, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 6, 7, 8, 9, 10, 15, 20, 40, 60, 120]`;
- reco `Eavail` edges in GeV:
  `[0, 0.1, 0.2, 0.4, 0.8, 1.5, 3, 100]`;
- reco `q3` edges in GeV:
  `[0, 0.2, 0.4, 0.6, 0.8, 1.2, 2, 100]`; and
- the Cartesian canonical `(pT,p_parallel)` grid from the first two lists.

Signal uses `sim,sim_pz,sim_eavail,sim_q3`; data uses
`measured,measured_pz,measured_eavail,measured_q3`; background uses
`sim_background,sim_background_pz,sim_background_eavail,sim_background_q3`.

No post-result region search, adaptive rebinning, threshold selection, or categorical materiality
rule is authorized by this contract.

## Execution and resource contract

- exactly one Slurm job;
- CPU constraint, no GPU request or allocation;
- 8 CPUs for at most 4 hours: exactly 32 CPU-hours allocation ceiling;
- 32 GiB memory;
- one SHA-256 pass plus one streaming event pass over each of the three named trees;
- no materialization of the variable-length cloud inventory;
- unique result/log namespace outside the repository; and
- no automatic or unchanged retry.

The launcher must require an explicit clean code checkout, expected commit, data root, output root,
and authorization token. It must verify the committed audit, predeclaration, and guarded-run hashes,
the source receipt hash, Slurm CPU/time/GPU operands, and output non-collision before scanning.

## Terminal readings and non-authorization

`PASS` means the exact source, schema, selected populations, finite/non-negative energy and weight
domains, and every requested aggregate/bin operand were measured and persisted. Any failed condition
is `INVALID_OR_INCOMPLETE`.

Every terminal outcome, including `PASS`, leaves Gate 6 blocked and cannot:

- change the PET representation or token cap;
- move or adopt a central value;
- construct `C_ML`, another covariance, or a full-event uncertainty;
- select a Gate-6 member, start Leg 2, or retry an existing family;
- establish estimator equivalence, convergence, closure, or interval coverage;
- edit a publication deliverable or support a publication claim; or
- authorize another compute job.
