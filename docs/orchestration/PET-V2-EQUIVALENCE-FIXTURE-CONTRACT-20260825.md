# PET-v2 fixed-draw equivalence fixture contract — 2026-08-25

## Status and authority boundary

Joseph approved the sequence proposed in
[`PET-GATE6-STRATEGY-20260825.md`](PET-GATE6-STRATEGY-20260825.md): first freeze the PET-v2
analysis object needed for an equivalence comparison and validate its deterministic CPU machinery;
then return separately with a numeric materiality criterion and resource estimate before any full
fixed-draw comparison. This contract implements **only the first CPU-only stage**.

The current `OI-126` row is ruled and closed. Its earlier contingent subtest remains `NO-RUN /
NO-COMPUTE`; this is a new PET-v2 method-development contract and does not reactivate that row or
repeat its containment, localization, target-factor, extraction, or occupancy probes. Gate 6 and all
existing Gate-6 family results remain blocked.

No Slurm job, `srun`, GPU training, full PET fit, pseudoexperiment, `C_stat`, or `C_ML` construction
is authorized here.

## Object frozen for this stage

The word *estimand* is used narrowly: the comparison targets the same event-level push and the same
extracted projections on one reporting mask. Target construction, training, and stopping define the
estimator; an interval construction would be a third object and is not present in this fixture.

| axis | frozen fixture contract | boundary on a future full PET comparison |
|---|---|---|
| estimand | per-unique-event push contribution and extracted sums in `p_parallel < 6 GeV`, `6–20 GeV`, and `>20 GeV` | bind the production truth domain, acceptance/native-miss treatment, extraction constants, and reporting mask by digest before a run |
| target and draw | one explicit integer multiplicity vector over immutable unique event IDs | replay one coherent production draw over data, signal MC, and background MC; rebuild the per-draw Stay-Positive target exactly once and bind all three streams |
| sampling intervention | Arm W retains every unique row and multiplies its sample weight by `k`; Arm L deletes `k=0` and materializes `k` copies carrying the original event weight | no sampling-semantic choice is adopted by the CPU fixture; the scientific comparison must disposition the arms before convergence tuning |
| split | unique-event train/validation membership is assigned before duplication and copied to all descendants | bind membership by event-identity hash; no unique event may cross partitions |
| loss normalization | both arms use the audited form `reduce_mean(weight * binary_cross_entropy)`; Arm W therefore divides a batch contribution by retained row count while Arm L divides by materialized row count | use the same production loss function and numeric batch size; row count, batches per epoch, gradient sequence, and validation reductions are measured consequences of the intervention |
| optimization/stopping | a scalar NumPy/Adam positive control with fixed initialization, learning rate, moments, batch size, epochs, and deterministic per-epoch shuffle | it is not PET training; a full comparison must separately freeze reco/truth models, initialization, optimizer/reset state, LR schedules, epoch budgets, early stopping/restoration, warm starts, iteration count, and checkpoint tier |
| feature and mask contract | synthetic scalar features and explicit response regions, sufficient only to validate row identity and reducers | bind the current PET reco/truth features, normalization, point-cloud padding/masks, coordinate columns, architecture/pretraining state, and reporting mask before a full comparison |
| interval procedure | absent | equivalence does not measure coverage; any future interval procedure and coverage ensemble require their own contract and authorization |

The fixture is source-bound to the current audited hashes of
[`net.py`](../../omnifold_nn/omnifold/net.py),
[`omnifold.py`](../../omnifold_nn/omnifold/omnifold.py),
[`dataloader.py`](../../omnifold_nn/omnifold/dataloader.py),
[`fullevent_fps_dataloader.py`](../../nd-unfolding/pet/fullevent_fps_dataloader.py),
[`train_fullevent_replica.py`](../../nd-unfolding/pet/train_fullevent_replica.py), and
[`train_fullevent_nominal.py`](../../nd-unfolding/pet/train_fullevent_nominal.py). A changed hash
invalidates the fixture until the relevant path is re-audited; it does not invite an automatic
repin.

## Measured quantities and controls

The deterministic fixture
[`pet_v2_fixed_draw_equivalence_fixture.py`](pet_v2_fixed_draw_equivalence_fixture.py) measures:

- exact replay of the fixed multiplicity vector and deletion/duplication counts;
- retention of all zero-weight rows in Arm W and their deletion in Arm L;
- absence of unique-event train/validation leakage after duplication;
- per-event weighted-loss contribution identity after Arm L is aggregated back to unique IDs;
- synthetic push and extracted-projection identity in the three predeclared response regions;
- the two arms' full-row and finite-batch `reduce_mean` values; and
- a deterministic scalar Adam and validation-loss trace as a **positive mechanism control**.

The positive control must show different update and validation-monitor paths. That is not evidence
of a PET discrepancy: it demonstrates only that the fixture is capable of exposing the finite-batch,
Adam-state, validation, and stopping seam found in the production code audit. The fixture trains no
PET model and consumes no production event artifact.

Negative controls reject non-integer or negative multiplicities, a wrong duplicate count, changed
event identity, changed split membership after duplication, and any unique event appearing in both
partitions.

## Terminal interpretations

- **`PASS_MACHINERY_VALIDATION_ONLY`:** every identity, split, aggregation, projection, source-hash,
  and positive-control assertion passes. This licenses only drafting the separate full fixed-draw
  predeclaration with a numeric materiality rule and measured resource estimate.
- **`FAIL_INVALID_FIXTURE`:** any assertion fails. This licenses only repairing and revalidating the
  CPU machinery; it says nothing about weighted versus literal PET behavior.

The committed deterministic result is
[`pet-v2-fixed-draw-equivalence-fixture-result-20260825.json`](state/pet-v2-fixed-draw-equivalence-fixture-result-20260825.json).

Every terminal result—pass, failure, or mixed software diagnosis—cannot authorize:

```text
do_not_select_passing_subset
do_not_construct_C_ML
do_not_move_central
do_not_start_leg_2
do_not_retry_unchanged
```

It also cannot establish PET estimator equivalence, training convergence, ordinary closure, interval
coverage, a valid PET uncertainty, publication adoption, a full-run sample count, or any compute
launch.

## Decision that must return before full comparison

A later proposal must bind one production draw, the complete paired-arm PET policy, a numeric
material-equivalence criterion for event-level push and every predeclared projection, failure and
mixed interpretations, guarded source/output identities, and a measured CPU/GPU resource estimate.
Joseph must approve that proposal separately before any full fixed-draw comparison.

### Proposal returned

The proposal returned as
[`PREDECLARATION-20260825-pet-v2-fixed-draw-equivalence.md`](PREDECLARATION-20260825-pet-v2-fixed-draw-equivalence.md),
with its deterministic machine-readable operand receipt. It derives a `0.0251` same-arm validity cap,
a `0.0502` cross-arm operational margin, and a scheduler-measured 13 A100-hour expected envelope.
Joseph subsequently authorized its CPU and three-arm A100 work on 2026-08-26 conditional on every
guard working as specified. The five diagnostic/submit operands are implemented, CPU-tested, and
hash-bound, and that later contract is now `launchable: true` only through its full fail-closed
preflight. This does not retroactively turn the fixture into compute authorization or widen what its
`PASS_MACHINERY_VALIDATION_ONLY` result established.
