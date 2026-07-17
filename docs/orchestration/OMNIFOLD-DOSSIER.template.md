# OmniFold full-phase-space dossier

## Objective

Graduate the current OmniFold implementation from `[CURRENT_OBSERVABLE_SET]` to `[OPERATIONAL_DEFINITION_OF_FULL_PHASE_SPACE]`.

Background document: `[PATH]`

## Authoritative inputs

| item | path/URI | version or hash | owner | notes |
|---|---|---|---|---|
| collision data | | | | |
| detector-level simulation | | | | |
| truth-level simulation | | | | |
| selections and matching | | | | |
| current baseline | | | | |

## Exact algorithmic contract

Document the two classification/reweighting steps, weight update equations, normalization convention,
iteration semantics, preprocessing, architecture, optimizer, stopping rule, clipping/regularization,
and how event weights flow into each subsequent step. Link every statement to code.

## Meaning of full phase space

Specify the event representation and everything intentionally excluded. Address variable-length objects,
ordering/permutation symmetry, padding and masks, angular periodicity, categorical features, missing values,
selection boundaries, detector acceptance, and whether the representation is sufficient for the claimed
observable family.

## Frozen data partitions

Define train/validation/test partitions and grouping keys. State how leakage through duplicate events,
generator ancestry, preprocessing fits, hyperparameter selection, iterations, and checkpoint selection is prevented.

## Acceptance gates

- Synthetic known-truth closure.
- MC closure on a held-out sample.
- Data closure or a precise statement of why it is unavailable.
- Prior/model dependence across genuinely different generators.
- Stability across seeds and finite-sample replicas.
- Weight normalization, tail, clipping, maximum-weight, and effective-sample-size diagnostics.
- Performance versus phase-space sparsity and dimensionality.
- Iteration-selection and hyperparameter-selection bias audit.
- Uncertainty propagation through all iterations.
- Recovery of the established small-observable baseline.
- Resource, checkpoint/restart, and deterministic-reproduction checks.

For every gate, define the metric, reference, tolerance, and failure action before reading the result.

## Current claims and open questions

List stable claim IDs from `CLAIMS.md`. Do not use prose such as “looks good” as a verdict.

## Collision map

Record active agents, branches/worktrees, Slurm jobs, manifests, datasets, and output paths that this
campaign must not modify. Give this campaign a unique branch, worktree, job-name prefix, and output root.

