# PET-v2 fixed-draw equivalence changed retry 1 — predeclaration

## Decision state

**Contract:** `PET-V2-FIXED-DRAW-EQUIVALENCE-CHANGED-RETRY1-20260826`

**State:** `AUTHORIZED_READY_CHANGED_RETRY`

**Launchable:** `true`, conditional on every frozen preflight and guard passing

This is a PET diagnostic and method-development proposal. It is not Gate 6, an uncertainty
construction, a central-value proposal, or an adoption action. The machine-readable contract is
[`pet-v2-fixed-draw-equivalence-changed-retry-proposal-20260826.json`](state/pet-v2-fixed-draw-equivalence-changed-retry-proposal-20260826.json).

The first authorized attempt is preserved in
[`pet-v2-fixed-draw-equivalence-attempt-57620796.json`](state/pet-v2-fixed-draw-equivalence-attempt-57620796.json).
Target job `57620796` passed the controller contract and then failed in 3 minutes 58 seconds when
the OI-136 runtime guard saw `pet_bootstrap` resolve from the primary checkout. It published no
target, measured no scientific quantity, and released no GPU dependency. The dependent training,
evaluation, and validation jobs were cancelled; A100 use was exactly zero.

The executed proposal said `retry_authorized: false` and `no_retry_path: true`, so that earlier
authorization remains exhausted. At `2026-08-26T18:43:31Z`, after this named changed-retry scope and
its preflight-before-submission sequence were restated, Joseph replied, **“I authorize it.”** This is
a new explicit authorization for this contract only. It becomes executable only after final tests,
hash bindings, a pushed clean commit, a clean detached non-primary checkout, direct scheduler
observation, and the controller's complete no-submit preflight all pass. It authorizes no further
retry.

## Measured failure and only change

At executed head `ed8244d3c9038c7f00dca3ddd6545266519ffd5a`,
`nd-unfolding/pet/fullevent_fps_dataloader.py` had SHA-256
`e1402370cdb8bd6349419ba6fbefa68817b799b3699cc97b673933f1f0220ce1`. It assigned the literal
primary-checkout path to `_REPO`, inserted its `nd-unfolding` directory at `sys.path[0]`, and later
made a lazy `pet_bootstrap` import. The guarded process refused when that import resolved outside
the immutable execution checkout.

The candidate preserves that receipt-bound loader byte-for-byte and changes only process-local
checkout-root handling:

- retry-specific target/training/evaluation entrypoints install a narrow `sys.path` list adapter;
- only the exact known primary root, or one of its lexical descendants, is remapped to the same
  relative path under the mandatory `PETV2_CODE_ROOT`;
- the normal OI-136 import finder remains installed and refuses every other checkout escape;
- the retry-specific controller and validator require a separate changed-retry authorization;
- change no target, sampling semantics, loss, training schedule, features, mask, extraction, random
  stream, threshold, or terminal classifier.

The preserved loader SHA-256 remains
`e1402370cdb8bd6349419ba6fbefa68817b799b3699cc97b673933f1f0220ce1`, so its Gate-2 receipt and
shell bindings remain intact.

## Question and measured quantity

The question is unchanged: for fixed Poisson draw seed `50000`, does retaining Poisson
multiplicities as sample weights—including zero-weight rows—produce an operationally equivalent
finite-batch trained estimator to literal deletion and duplication?

The three fresh-process arms remain:

- `W_A`: weighted multiplicities, zero-weight rows retained;
- `W_B`: identical same-arm control in an independent process;
- `L`: the same draw, delete `k=0` and materialize `k` copies for `k>0`.

For a push vector or extracted projection, define

```text
symrel(a,b) = 2 |a-b| / (|a|+|b|)
D_same      = D(W_A,W_B)
D_cross_max = max(D(W_A,L), D(W_B,L))
D_cross_min = min(D(W_A,L), D(W_B,L))
```

The event-push distance is the predeclared weighted symmetric relative L1 distance on the same
unique accepted signal IDs. Extracted comparisons remain the global reporting-mask total and the
three frozen regions `p_parallel < 6 GeV`, `6–20 GeV`, and `>20 GeV`. Mandatory diagnostics remain
all reco/truth loss histories, best/final checkpoints and predictions, realized schedules/update
counts, response/calibration, iteration pushes, ESS, weight quantiles, maxima, and cap occupancy.

## Numeric thresholds and terminal logic

The thresholds are unchanged and are not refit to attempt `57620796`, which produced no scientific
data:

```text
F_sd = 0.02506515073050877
S    = ceil(F_sd * 10000) / 10000 = 0.0251
M    = 2 S = 0.0502
```

The inherited single-effect MDE `0.0695920150567661` remains an annotation, not a gate.

Terminal order:

1. `INVALID_OR_NOISY` if any provenance, determinism, split, identity, finite-output, or
   same-arm condition fails, including any primary `D_same > 0.0251`.
2. `EQUIVALENT_AT_5P02_PERCENT_OPERATIONAL_RESOLUTION` only if all controls are valid and every
   primary `D_cross_max <= 0.0502`.
3. `MATERIALLY_DIFFERENT_IN_THIS_FIXED_DRAW` only if all controls are valid and at least one primary
   metric has both `D_cross_min > 0.0502` and `D_cross_min > 2 D_same`.
4. `MIXED_OR_UNRESOLVED` for every other valid result; there is no favorable default.

## Frozen controls

| operand | frozen value |
|---|---|
| G2 source | 9,897,374,636 bytes; SHA-256 `fa6b3463160242164a2c6506c787d09194d0715d2bd64e24dba771c8f2a29625` |
| draw | seed `50000`; exact data/signal/background factor hashes from the original proposal |
| required class ratio | `R = 1.1253110723074478` |
| estimator/subsample seeds | `42 / 0` |
| unique training inventory | `2,000,000` before literalization |
| split | fixed hash-bound unique-event 80/20 membership assigned before duplication |
| training | 3 OmniFold iterations; 8 reco and 8 truth epochs; batch 512 |
| stopping | patience 10; cannot fire within 8 epochs |
| LR | iteration 0 `1e-4`; iterations 1–2 `1e-5` |
| optimizer/model state | new Adam per fit; model weights warm-start across iterations |
| determinism | `PYTHONHASHSEED=42`, `TF_DETERMINISTIC_OPS=1`, `CUBLAS_WORKSPACE_CONFIG=:4096:8`, TensorFlow op determinism and random seed 42 before model creation |
| hardware | exactly one A100-SXM4-80GB per arm |
| same-arm control | `W_A` and `W_B` are independent processes with identical frozen inputs, hashes, seeds, and policy |
| only changed axis | process-local checkout-root remap before the frozen PET operands execute |

Determinism has no fallback. An unsupported deterministic operation is
`INVALID_OR_INCOMPLETE`; it does not license dropping `W_B`.

## Guarded executable operands

Any later authorized run must use one clean, detached, non-primary checkout and a new absent output
namespace. The failed attempt directory is evidence and must not be reused or altered. Every Python
science process remains wrapped by `mnv_guarded_run.py --expect-root <exact checkout> --`; no `srun`
or retry branch exists.

The five new retry-specific executable SHA-256 values are:

| path | SHA-256 |
|---|---|
| `materialize_pet_v2_equivalence_target_retry1.py` | `cab2328dae25adbfe510f38a1ff771962246929cfc1492f51fe1372b272b8b84` |
| `train_pet_v2_equivalence_retry1.py` | `02fd449f09a92095c965e756385cfa402b0f5c251529128690dd4327faf74d4e` |
| `evaluate_pet_v2_equivalence_retry1.py` | `4ec32e0adc9acb010172c72611148699d0b905fe134f6cb8474f4e5a27c36acd` |
| `validate_pet_v2_equivalence_result_retry1.py` | `9d0fa1ed168df93e074e11b38d840aa0121fa5fd37bd2742d33ace34f59b6ece` |
| `submit_pet_v2_equivalence_changed_retry.sh` | `135673741c89d3cc623813d02755d406fc1c4a645a10791f646f013384d692e2` |

The new remap support source is
`pet_v2_equivalence_root_remap.py` at
`646b857861d5102f041215e286e23d53247f8dd33ff957e8864a4fb4beba783c`; the frozen original
operands and all other required/support hashes are exact in the machine-readable proposal. Before
any later submission, rerun the guarded remap-plus-lazy-import regression, prove both production
loader bindings intact, run all original PET-v2 tests, the ROOT worker-shell check, frozen
source/input/flux checks, clean-checkout check, output-collision check, exact five prohibitions,
scheduler observation, and `gpu&a100&hbm80g` resource confirmation.

## Resource estimate

Attempt `57620796` used `0.0661111111111111` CPU node-hours (`2.38` CPU core-hours) and zero A100
hours. The unchanged measured estimate for a complete run is `12.642708333333331` A100-hours,
rounded up to `13`; the proposed ceiling remains `18` A100-hours and five CPU node-hours, with
three single-A100 arms able to run in parallel after the CPU target.

The unchanged ceiling for this one authorized attempt is `18` A100-hours and five CPU node-hours;
the first attempt consumed `0.0661111111111111` CPU node-hours and zero A100-hours. The numerical
envelope is not standing authorization and cannot carry forward to another attempt.

## Success and failure interpretations

A valid terminal result may classify only the fixed-draw push and extracted projections after the
same-arm control. `EQUIVALENT...` means no material representation effect was resolved at this
operational scale for seed `50000` and the frozen PET-v2 policy. `MATERIALLY_DIFFERENT...` means at
least one predeclared metric separates literalization from both weighted executions under the rule
above. `MIXED...` remains unresolved.

Any guard refusal, missing artifact, noisy same arm, non-finite output, or incomplete stage is
`INVALID_OR_INCOMPLETE`. It authorizes only diagnosis and redesign. It cannot authorize an
automatic, unchanged, or unapproved changed retry.

## What every terminal result cannot authorize

Every terminal result—including a valid equivalence result—preserves these exact prohibitions:

```text
do_not_select_passing_subset
do_not_construct_C_ML
do_not_move_central
do_not_start_leg_2
do_not_retry_unchanged
```

It also cannot establish interval coverage, valid PET uncertainty, or closure beyond the measured
projections; generalize beyond seed `50000` and this frozen policy; construct or adopt `C_stat`,
`C_ML`, a total covariance, or a central value; change the note, publication claims, or PET's
diagnostic scope; authorize convergence tuning, a larger family, Leg 2, coverage compute, or any
further compute; or erase/reinterpret the failed `57620796` receipt. Existing Gate-6 results remain
blocked regardless.

## Compute decision received

Joseph authorized `PET-V2-FIXED-DRAW-EQUIVALENCE-CHANGED-RETRY1-20260826` on 2026-08-26. The
authorization covers only the new CPU target, the three predeclared A100-80GB arms, CPU evaluation,
and read-only validation, within the 18 A100-hour/five CPU-node-hour ceiling and with no retry. It
does not cover Gate 6, convergence tuning, a family, coverage, `C_stat`, `C_ML`, central movement,
Leg 2, note changes, publication claims, or any later compute. Submission is conditional on every
guard and frozen preflight passing from a pushed clean non-primary checkout.
