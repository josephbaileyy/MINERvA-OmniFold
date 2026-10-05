# Pooled numerical diagnostic preparation

**Local preparation complete; no GPU allocation submitted.** Calibration and the
full matrix remain blocked after `58240587`. The [single 20-minute diagnostic
proposal](NUMERICAL_PROPOSAL-20260913.md) requires a new explicit grant. It has no
calibration or training continuation, even after complete numerical capture.

## Implementation and provenance

`numerical_diagnostic.py` saves the exact archived four-event fixture and one
reconstructed weight bundle, then captures normalization, token MLP primitives,
masking and pooling. `analyze_numerical_diagnostic.py` saves every elementwise
comparison, identifies the first unequal/over-tolerance operation, and compares
local versus propagated float64 references. The full-significand FP32 envelopes
are illustrative diagnostic components, not revised acceptance criteria.

The old GPU job did **not** save its weights. The bundle reconstructs the pinned
seed-1701 recipe; the input bytes are verified historical bytes, while the weights
are explicitly not independently verified historical bytes. Every CPU/target
comparison copies the same saved weights. The comparison has 17,329 parameters,
unchanged. The model, packing repair, normalization, scientific runner, import
guard and frozen scientific criteria have no changes in this preparation.

Each worker records TF32 requested/observed settings, determinism, global/layer
precision policies, build/version/environment information and per-operation
device/dtype. Common-operand replay isolates each primitive's own error. Three
repetitions per model and two independent processes per TF32 mode test exact
repeatability. Four workers run in on/off/off/on order. Numerical discrepancies
are saved without suppressing later predetermined captures. Instrumentation
parity and artifact integrity remain required for an interpretable diagnostic.

All worker files are sealed after closure; reduction rejects modified, missing
or extra files. The final archive includes closed guard logs and is independently
read back. Internal reducer inventories written while a guard/log is still open
are not final preservation receipts. The launcher's 20-minute cap includes all
four processes and reduction; it contains no calibration or submission path.

## Local measurements

[Source-bound validation](local_validation/20260913-numerical/validation.json),
[full numerical summary](local_validation/20260913-numerical/summary.json), and
[complete archive inventory and readback](local_validation/20260913-numerical/preservation.json).

| Check | Result |
|---|---|
| Diagnostic failure capture, references and tamper tests | 9 passed |
| Existing guarded regression suite | 60 tests + 10 subtests passed |
| Four CPU process cells | `COMPLETE_DIAGNOSTIC`; no integrity errors |
| CPU original versus repaired target | All 5,304 compared components per cell exact; max absolute error 0 |
| Identical-operand replay | 4,624 components per cell; 79 recorded primitives per trace |
| Same-device repeatability | 20 within/across-process comparisons exact |
| Black / Ruff / strict Linux-target mypy | Passed for all three new Python files |
| Shell syntax | Both launchers pass `bash -n` |

The component counts include intermediate tensors, prepared features and routed
values/masks/counts; they are not independent events or performance trials.
This run uses macOS arm64 CPU with the five pinned package versions. The full
resolved local environment is preserved in the archive. **TF32 has no supported
GPU to exercise here; these measurements do not establish GPU compatibility,
identify the earlier numerical cause, or validate a precision-policy change.**
Local preparation CPU consumption was not separately metered. No Slurm reservation
or new source read occurred.

During preparation, an optional NumPy SVE probe was refused by the guard; the new
scripts use the existing narrowly scoped missing-probe fallback without guard
changes. The shared temporary runtime had SciPy 1.17.1 and failed the pinned-version
check; final validation used a separate environment with SciPy 1.16.3. An earlier
rehearsal spanning a source edit was rejected for a cross-process source mismatch.
Those development runs are not the source-bound final validation above.

GPU diagnosis remains necessary. TensorFlow documents TF32 as enabled by default
on supported hardware and reduced-precision operation as shape dependent; this
motivates the controlled switch, not a finding about the failed job. [TensorFlow
TF32 API](https://www.tensorflow.org/api_docs/python/tf/config/experimental/enable_tensor_float_32_execution).

No tolerance was widened and no precision mode was adopted. No direct-token
learning result, real-source performance statement, covariance, publication
adoption or Gate-6 action follows from this preparation.
