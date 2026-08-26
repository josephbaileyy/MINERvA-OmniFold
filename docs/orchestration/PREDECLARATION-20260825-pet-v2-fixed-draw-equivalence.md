# PET-v2 fixed-draw weighted-versus-literal equivalence predeclaration — 2026-08-25

## Status and compute decision

**Proposal complete; compute held.** This is a no-launch PET diagnostic and method-development
contract. It specifies the scientific comparison, numeric operational thresholds, same-arm and
determinism controls, guarded future operands, and a scheduler-measured resource ceiling. It does
not implement or hash-bind the future target, training, evaluation, validation, or submission
entrypoints. Therefore it is deliberately `launchable: false` and the present compute decision is
`HOLD_FOR_JOSEPH_AND_EXECUTABLE_IMPLEMENTATION`.

The CPU-only prerequisite fixture passed `PASS_MACHINERY_VALIDATION_ONLY` in
[`pet-v2-fixed-draw-equivalence-fixture-result-20260825.json`](state/pet-v2-fixed-draw-equivalence-fixture-result-20260825.json).
That validates bookkeeping and positive/negative controls, not PET estimator equivalence.

No Slurm job, `srun`, GPU operation, PET training, uncertainty construction, note edit, publication
change, or primary-checkout operation was performed while preparing this contract.

## Fresh state and evidence boundary

The live-state freshness check was run before this continuation. It returned:

```text
STALE :: Git: 06efa653, HEAD 10ad530d, HEAD^ 0c08d317
```

No field from that stale generated view is used. Direct `./alloc_run.sh --status` showed no
allocation; direct `squeue -u josephrb` showed no PET or analysis job, only unrelated cron job
`57575105` on `login33`. Direct `sinfo` showed both `hbm40g` and `hbm80g` A100 nodes, so hardware
class is an explicit control below.

The governing sources are the exact `OI-123`, `OI-125`, `OI-126`, and `OI-138` records in
[`OPEN_ITEMS.md`](../OPEN_ITEMS.md), the current route in [`CURRENT_WORK.md`](../CURRENT_WORK.md),
[`ND_OMNIFOLD_STATUS.md`](../../nd-unfolding/ND_OMNIFOLD_STATUS.md),
[`PET_UQ_REMEDIATION_STATUS.md`](../../nd-unfolding/PET_UQ_REMEDIATION_STATUS.md), the original
[Gate-6 predeclaration](PREDECLARATION-20260813-gate6-member-trajectories.md), the exact
[Gate-6 result](state/gate6-member-trajectories-result-56847059.json), and the
[fixed-policy floor result](state/gate6-floor-replication-result-56863958.json).

The old family remains `BLOCK_GATE6_ML_ENSEMBLE`. Its exact receipt prohibitions remain live:

```text
do_not_select_passing_subset
do_not_construct_C_ML
do_not_move_central
do_not_start_leg_2
do_not_retry_unchanged
```

This comparison is not an `OI-126` containment or localization probe. That row is ruled and closed;
none of its completed target-factor, extraction, occupancy, tail, or region-finding work is repeated.
The three response regions below are inherited from the approved PET-v2 fixture, not selected from a
new outcome.

## Question and frozen draw

The only scientific question is:

> For one fixed coherent Poisson draw and one frozen PET-v2 training policy, does carrying the
> integer multiplicity as a sample-weight factor while retaining zero-weight rows produce materially
> different event-level pushes or extracted projections from literal deletion and duplication?

The draw is seed `50000`, the first member of the predeclared Gate-5 range `50000..50049`. It is
chosen by index, not by its outcome. Its source G2 object has SHA-256
`fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625` and size
`9,897,374,636` bytes, first routed by
[`gate5-source-npz-verified-20260813.json`](state/gate5-source-npz-verified-20260813.json) and the
target-family promotion receipt. The current weighted target has SHA-256
`13d46574b8f8e904aee0d544b33ce0f4fcd3fd5a119b0a2fd64071c70c650c03`, recorded for
`replica_00` in the committed Gate-5 training-family validation artifact.

The deterministic audit
[`derive_pet_v2_equivalence_predeclaration.py`](derive_pet_v2_equivalence_predeclaration.py)
replays the current first-party three-stream RNG and exact array-hash contract under source-hash
guards. It measures:

| stream | inventory rows | factor sum | zero factors | maximum | SHA-256 |
|---|---:|---:|---:|---:|---|
| data | 4,116,128 | 4,118,323 | 1,513,511 | 9 | `d151dd197c9662da4604c9609d761887d38437d510484efdf851c8de1028ca37` |
| signal | 49,152,885 | 49,143,888 | 18,087,975 | 10 | `892d1531b7db788a9782ce2dad470b1514b13c1f1f393af9a0f84f32ea68642f` |
| background | 564,591 | 564,471 | 207,687 | 8 | `9e967dc2ff1a977c4940b83171204a41deb200e5d7c6ecb819c63c15c335e84e` |

The data digest independently agrees with the first committed redraw in
[`gate5-promotion-evidence-rescue-20260814.json`](state/gate5-promotion-evidence-rescue-20260814.json).
Agreement is traced to that measurement and is not counted as independent worker evidence.

## Arms and causal intervention

| arm | sampling representation | process role |
|---|---|---|
| `W_A` | keep every unique row; multiply its physical sample weight by integer `k`, including retained `k=0` rows | current weighted arm |
| `W_B` | bit-identical policy, target, split, inputs and seeds to `W_A`, in a fresh independent process | same-arm resolution and determinism control |
| `L` | delete `k=0`; make exactly `k` copies for `k>0`, with each copy carrying the original physical weight | literal intervention |

Unique-event train/validation membership is assigned and hash-bound before any duplication. Every
literal descendant inherits its source membership; no unique event may cross partitions. The signal
MC subsample selects the same two million unique IDs under subsample seed `0` before literalization;
the global coherent factor is still drawn before that subset. This avoids materializing all
49,152,885 signal rows while preserving the production draw order.

The weighted arm stages the exact existing seed-50000 target read-only into a new isolated namespace.
The literal arm rebuilds the Stay-Positive target exactly once with the same data and background
draw, representing every multiplicity literally throughout refinement. It must not copy the weighted
target and call that a literal target. The pre-representation class-ratio operands must reproduce
`R = 1.1253110723074478` exactly in all three arms; a mismatch is invalid, not a scientific effect.

Both representations retain the current physical sample weights and the audited
`reduce_mean(weight * binary_cross_entropy)` loss. The intervention is allowed to change row count,
batches and optimizer updates per epoch, gradient order, validation reductions, and Adam state. Those
are causal consequences under test and must not be equalized after the fact.

## Frozen PET-v2 policy

The current policy is deliberately held at the audited `3 × 8` baseline. This test occurs before
the proposed fewer-epochs/more-iterations experiment; combining representation and convergence
changes would destroy causal attribution.

| operand | required value |
|---|---|
| estimator / subsample seed | `42 / 0` |
| unique signal training IDs | `2,000,000` |
| OmniFold iterations | `3` |
| reco / truth epochs | `8 / 8` |
| numeric batch size | `512` rows |
| train fraction | `0.8` |
| early-stop patience | `10`; it cannot fire within eight epochs |
| LR | `1e-4` at iteration 0; `1e-5` at iterations 1–2 |
| optimizer state | a new Adam instance at every fit |
| model state | separate reco/truth models, warm-started across OmniFold iterations |
| checkpoint policy | persist both best-validation and final in-memory tiers for every fit; never mix them silently |
| features and masks | current full-event reco/truth feature, normalization, padding, KNN-coordinate, truth-domain and reporting-mask contract, all digest-bound |

Full train/validation histories, best/final epoch, LR, update counts, early-stop state, checkpoint
digests, per-iteration pushes, response/calibration summaries, reco/truth effective sample size,
weight quantiles, maximum and cap occupancy are mandatory diagnostics. Their absence makes the run
incomplete. They are not additional unregistered success gates.

## Determinism and same-arm controls

Before the Python interpreter starts, every arm must receive exactly:

```text
PYTHONHASHSEED=42
TF_DETERMINISTIC_OPS=1
CUBLAS_WORKSPACE_CONFIG=:4096:8
```

Before model creation, the in-process diagnostic driver must call
`tf.config.experimental.enable_op_determinism()` and `tf.keras.utils.set_random_seed(42)`, and apply
deterministic options to every `tf.data` dataset. This follows TensorFlow's
[author-maintained determinism API](https://www.tensorflow.org/api_docs/python/tf/config/experimental/enable_op_determinism).
An unsupported nondeterministic operation, missing environment value, or attempted silent fallback is
`INVALID_OR_NOISY`; the run stops without retry.

All arms require one `NVIDIA A100-SXM4-80GB` and identical TensorFlow, CUDA, cuDNN, driver class,
conda lock, immutable code commit, sources and inputs. A 40/80-GB mixture is invalid even if all jobs
say “A100.” UUID and node may differ and are recorded.

`W_A` and `W_B` remain required even with deterministic operations. They run as fresh independent
processes because deterministic mode is a new PET-v2 diagnostic policy, not evidence that every
operation is bitwise deterministic and not a retroactive statement about the old Gate-6 estimator.

## Primary measured quantities

For positive scalar results define

```text
symrel(a,b) = 2 |a-b| / (|a|+|b|).
```

It is zero when both operands are zero and two when exactly one is zero.

For event-level push factors `p_i`, compare models on the same canonical unique signal IDs:

```text
D_push(A,B) = Σ_i a_i |p_i^A-p_i^B|
              -----------------------------------------
              Σ_i a_i (|p_i^A|+|p_i^B|)/2
```

Here `a_i` is the nonnegative raw truth analysis weight times the fixed signal multiplicity and
reporting mask, applied exactly once. Literal copies may be used for training, but inference is on
the canonical unique rows; any duplicate-to-source mapping discrepancy is invalid.

Extracted projection sums use the same fixed POT, flux, acceptance/native-miss treatment, truth
domain, extraction constants, and reporting mask in all arms. Apply `symrel` to the global total and
each predeclared region:

- `p_parallel < 6 GeV`;
- `6 GeV <= p_parallel <= 20 GeV`; and
- `p_parallel > 20 GeV`.

For every primary metric `D`, compute:

```text
D_same      = D(W_A, W_B)
D_cross_max = max(D(W_A,L), D(W_B,L))
D_cross_min = min(D(W_A,L), D(W_B,L))
```

No cell-level search, post-hoc mask, passing subset, or alternate norm may replace these operands.

## Numeric operational thresholds

The first artifact is the fixed-policy floor receipt. At iteration 2 it measures
`F_sd_ddof1 = 0.02506515073050877`, `F_range = 0.06452911345365375`, and an inherited one-effect
minimum-detectable-effect annotation of `0.0695920150567661`. That receipt calls the result
`FLOOR_INTERMEDIATE` and licenses nothing.

This contract derives:

```text
S = ceil(F_sd_ddof1 × 10,000) / 10,000 = 0.0251  (2.51%)
M = 2 S                                  = 0.0502  (5.02%)
```

`S` is the maximum allowed same-arm discrepancy. `M` is the cross-arm operational materiality
margin. Neither is a coverage level, confidence bound, physics uncertainty, nor a new convergence
gate. The source floor measured a no-draw global scalar, not regional push or extraction variation;
therefore its transfer is conditional on `W_A` versus `W_B` satisfying `S` for every primary metric.
The older `0.069592` MDE is recorded as a sensitivity annotation only and does not override this
paired fixed-draw classification.

## Terminal classification

Validity and same-arm control are evaluated before any cross-arm interpretation.

1. **`INVALID_OR_NOISY`:** any source, root, input, draw, target, split, class-ratio, determinism,
   hardware, checkpoint, mapping, finite-output, or receipt guard fails; or any primary `D_same >
   0.0251`. This authorizes only diagnosis and a changed proposal—never automatic or unchanged retry.
2. **`EQUIVALENT_AT_5P02_PERCENT_OPERATIONAL_RESOLUTION`:** every control is valid, every primary
   `D_same <= 0.0251`, and every primary `D_cross_max <= 0.0502`.
3. **`MATERIALLY_DIFFERENT_IN_THIS_FIXED_DRAW`:** controls are valid and at least one primary metric
   has both `D_cross_min > 0.0502` and `D_cross_min > 2 D_same`, so the literal arm differs from both
   independent weighted executions.
4. **`MIXED_OR_UNRESOLVED`:** every other valid outcome. Conflict never defaults to equivalence.

The equivalence label is intentionally scoped to one draw, one estimator policy, and one operational
resolution. It is not equivalence of all bootstrap draws, all regions, all hyperparameters, or any
interval procedure.

## Guarded executable operands

`OI-136` proves that `PYTHONPATH` and a clean deployment hash are insufficient when an entrypoint
inserts another checkout at `sys.path[0]`. Every Python process that imports science modules must
itself run through [`mnv_guarded_run.py`](../../nd-unfolding/mnv_guarded_run.py); wrapping only a
parent that starts an unguarded child is invalid because the import guard does not cross a subprocess
boundary.

The future command prefix is:

```text
${PETV2_PYTHON} ${PETV2_CODE_ROOT}/nd-unfolding/mnv_guarded_run.py \
  --expect-root ${PETV2_CODE_ROOT} --
```

`PETV2_CODE_ROOT` is mandatory, has no default, names a clean immutable checkout at the approved
implementation commit, and may not be the primary checkout. The diagnostic materializer, trainer,
evaluator, and validator must either run their science code in that guarded interpreter or be
individually guarded. `OI-123` and `OI-138` forbid a silent frozen-tree default and require the
supplier to be explicit.

`PETV2_PYTHON` is also mandatory and has no default; preflight binds its resolved path, Python and
package versions, and environment lock. The G2 source and weighted seed-50000 target likewise arrive
through mandatory explicit staged paths outside the primary checkout and are content-verified before
use. No current primary-checkout path may act as an implicit artifact supplier.

These future operands and their exact argument contracts are required:

| operand | measured action | mandatory arguments | current state |
|---|---|---|---|
| `materialize_pet_v2_equivalence_target.py` | build literal seed-50000 target and split manifest | code/input/factor hashes, draw seed, unique-ID split hash, output/receipt paths | not implemented or hash-bound |
| `train_pet_v2_equivalence.py` | train exactly one of `W_A`, `W_B`, `L` in-process | arm, target/split hashes, frozen policy JSON, isolated output, deterministic env assertions | not implemented or hash-bound |
| `evaluate_pet_v2_equivalence.py` | unique-ID push and fixed-projection readback | three arm receipts/checkpoints, input/mask/extraction hashes, output receipt | not implemented or hash-bound |
| `validate_pet_v2_equivalence_result.py` | read-only guards and terminal classification | proposal receipt, all outputs/markers, no artifact mutation | not implemented or hash-bound |
| `submit_pet_v2_equivalence.sh` | preflight and eventual Slurm submission only after authorization | mandatory code root, exact HEAD, authorization token, output root, every script/source hash | not implemented or hash-bound |

The machine-readable operand surface is
[`pet-v2-fixed-draw-equivalence-proposal-20260825.json`](state/pet-v2-fixed-draw-equivalence-proposal-20260825.json).
It currently contains `sha256: null` for all five future operands and therefore fails closed with
`launchable: false`. This is deliberate: naming a planned script is not claiming executable parity.

Every future output uses a new isolated per-arm namespace; refuses a pre-existing nonempty target;
shares no checkpoint/history path; writes atomically; and binds completion markers to result size,
SHA-256, and terminal status. Receipts must include code HEAD, clean-tree assertion, every current and
new source hash, G2/target/factor/split hashes, realized policy, LR and update schedule, GPU identity,
process identity, and loaded-checkout inventory. The submit controller must require a literal Joseph
authorization token bound to the final contract and implementation hashes; absent or mismatched
authorization exits before `sbatch`.

## Measured resource estimate

Direct read-only `sacct -X` accounting was remeasured for the completed Gate-5 target and training
arrays. The exact 100 elapsed-second records and queries are preserved in the machine-readable
proposal.

| historical stage | completed | allocation each | min | median | mean | max |
|---|---:|---|---:|---:|---:|---:|
| targets `56857232` | 50 | 36 CPU, 64G, one node | 38m27s | 39m23.5s | 39m49.1s | 46m10s |
| training `56857233` | 50 | one A100, 32 CPU, 57,472M | 2h58m48s | 3h00m55s | 3h01m24.6s | 3h11m05s |

The proposal uses the historical maximum training time, multiplies by `1.25` as an explicit design
allowance for deterministic kernels and literal batching, and adds 14 minutes of inference/extraction
per arm:

```text
3 × (3.18472 h × 1.25) + 3 × (14/60 h) = 12.6427 A100 h
rounded expected envelope                         = 13 A100 h
```

The `1.25` is a conservative planning assumption, not a measured speed ratio. If later authorized,
the request ceiling is:

- one literal-target CPU job: 36 CPU, 64G, two-hour walltime;
- three training/evaluation jobs: one `A100-SXM4-80GB`, 32 CPU, 57,472M, six-hour walltime each;
- expected envelope: 13 A100-hours; allocation ceiling: 18 A100-hours;
- CPU ceiling: two node-hours; and
- queue-excluded critical path with parallel arms: about 6.21 hours, target then slowest arm.

The weighted target is staged read-only by exact digest into the isolated run namespace. Nothing
writes in or executes from the primary checkout. A timeout, memory failure, deterministic-op failure,
or provenance failure stops the proposal; it does not authorize an unchanged retry. These resources
are for three diagnostic arms, not a statistical ensemble. They authorize no suggested pseudoexperiment
count, coverage campaign, `C_stat`, or `C_ML` family.

## Success, failure, and non-authorization

An equivalence result would support choosing one frozen sampling representation for subsequent
PET-v2 method development. A material difference would establish only that representation is a
causal estimator choice for this fixed draw; Joseph would still need to choose or redesign PET-v2
before any convergence tuning. A mixed or noisy result would leave sampling semantics unresolved.

Every terminal result—valid, invalid, equivalent, different, or mixed—leaves existing Gate 6 blocked
and cannot:

- select a passing subset;
- construct `C_ML`, adopt `C_stat`, or construct/adopt any PET total covariance;
- move or adopt a central value;
- start Leg 2;
- retry the old family unchanged;
- loosen, reclassify, or retroactively reinterpret the old Gate-6 rule or any old member;
- establish training convergence, ordinary closure beyond the fixed projections, interval coverage,
  or valid PET uncertainty;
- generalize beyond seed 50000 and this exact PET-v2 policy;
- edit the note, change a publication claim, or change PET's diagnostic/method-development scope; or
- authorize a coverage campaign, a larger family, the 6×4 convergence screen, or any further compute.

## Decision requested from Joseph before compute

The current decision is **do not authorize A100 compute yet**. Please decide whether to authorize
implementation and CPU-only testing of the five isolated, fail-closed operands above. If that is
approved, their committed hashes, tests, immutable checkout HEAD, exact authorization-token shape,
and final `launchable` preflight must return for a compute decision. No implementation approval is a
Slurm or GPU authorization.
