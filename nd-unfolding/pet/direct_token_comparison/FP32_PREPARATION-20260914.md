# Full-FP32 policy preparation

**Implemented and CPU-validated; no new GPU allocation submitted.** The
[110-minute compatibility/calibration proposal](FP32_PROPOSAL-20260914.md) requires
explicit approval of the policy, exact patch and bounded execution. The completed
numerical diagnostic is evidence for this policy, not authorization to run it.

The exact patch applies to `5de3b8de` with `git apply --unidiff-zero full-fp32.patch`.

## Changes and unchanged scientific footing

`run_typed_token_comparison.py` owns one small shared precision configuration:
TF32 disabled, deterministic operations enabled, float32 mixed-precision policy
and backend dtype required. The runner applies it before feature/model work.
Preflight (including fresh-process reload) and calibration call it before any
model/GPU operation. Results record and verify the observed settings at closure.
A conflicting mixed-precision policy is rejected rather than silently replaced.

Preflight receipts now bind both parent and reload policy. Calibration checks
those receipts; environment, run and resource records include the same policy.
The resource evaluator rejects any missing/inconsistent policy. Its expected
suite count changes to 69 tests plus 10 subtests. Its existing JSON-Lines guard
parser is unchanged: inspection of the actual writer confirmed that format,
including propagated-child records. No guard-parser repair was needed.

The four scientific execution files change only policy setup/verification,
receipt fields, test-count checking and two type annotations. The original
CPU oracle, model layers/parameters, deterministic packing, masks, raw object
membership, features, normalization, loss, optimizer, seed/minibatch conventions,
scientific run card and all numerical/resource acceptance thresholds are unchanged.
The new launcher requires a distinct authorization and precision-manifest hash;
previous authorizations cannot satisfy it.

## Local evidence

[Source-bound validation](local_validation/20260914-fp32/validation.json) and
[complete read-back archive](local_validation/20260914-fp32/preservation.json).

- **69 tests + 10 subtests passed**, including nine policy checks: stale parent
  policies, a wrong reload policy with a matching artifact hash, TF32 drift,
  mixed-precision rejection, setup before fixture construction, and wrong policies
  in each of calibration/environment/measurement receipts.
- **Eight CPU model/case comparisons** pass against the frozen original model:
  exact token routing, outputs/loss/gradients, updated weights and predictions.
  Nominal, 90-blob variable multiplicity, masked and empty cases are covered for
  both pooled and direct models; each performs eager and traced Adam updates.
- Same-process reload is exact in all eight cases; fresh-process reload passes
  all eight. Parent and reload record TF32 disabled, determinism enabled and
  float32 policy/dtype. Largest eager/traced difference: `2.980232238769531e-7`,
  within unchanged tolerance. Complete CPU preflight: 48.623758 seconds.
- Black, Ruff and strict Linux-target mypy pass for the four changed Python
  execution files; the test file passes Black/Ruff. New launcher passes `bash -n`.

These are macOS arm64 CPU checks with the pinned five package versions, not a
GPU result. The local preflight exercises two optimizer updates as software
validation; it is not calibration or a learning-performance comparison. Full
A100 two-arm forward/backward/update/reload compatibility remains unverified.

The prior diagnostic motivates full FP32 without tolerance widening: TF32-on
failed 112/192 pooled components, TF32-off failed 0/192, and the latter satisfied
the illustrative FP32 envelopes. That fixed fixture does not prove the full
GPU preflight, training throughput or representation superiority.

Local preparation CPU time was not separately metered; no new Slurm reservation
was consumed. Future execution must retain actual accounting and prior charges.
All four completed allocations remain charged at 395 conservative seconds.
No real-source, covariance, publication-adoption or Gate-6 work is included.
