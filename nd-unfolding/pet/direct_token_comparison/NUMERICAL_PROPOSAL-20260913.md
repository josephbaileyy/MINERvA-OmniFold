# Pooled embedding numerical diagnostic: proposed single allocation

**Prepared; not authorized. Calibration and the full matrix remain blocked.**
This proposal replaces neither the scientific criteria nor any precision policy.
It requests one diagnostic of the pooled CPU/GPU mismatch in job `58240587`.
The three previous allocations and partial artifacts remain preserved and excluded
from performance comparisons. Remaining budget alone supplies no execution grant.

## Fixed question and evidence

Determine where the pooled encoder first differs across CPU and A100, whether
that difference originates locally or propagates from earlier operations, and
whether toggling TF32 changes it. A TF32 setting alone does not prove a particular
kernel used TF32. No numerical outcome automatically selects a precision mode,
changes tolerance, validates direct tokens or releases training.

Use only the four-event synthetic fixture saved by `58240587`. Its archived bytes
and archive hash are verified before use. The historical weights were not saved:
reconstruct them once on CPU from the pinned seed-1701 recipe, save the complete
ordered arrays and model configuration, then copy those identical bytes into every
arm/process. Label them as reconstructed, not verified historical weights. A
failure to reproduce the original maximum error is a result to report, not a
reason to search other seeds.

Run the following fixed sequence in separate guarded Python processes:

1. Prepare one CPU bundle, including exact fixture, reconstructed weights and config.
2. Capture TF32 **on-0, off-0, off-1, on-1**, in that order, in four fresh processes.
   Each captures the original CPU pooled model and repaired GPU pooled model with
   three same-device repetitions, exact copied weights, unchanged masks and counts.
3. Reduce the saved traces and close all evidence. Report both within-process and
   cross-process repeatability, CPU/GPU differences and on/off differences.

Capture normalization subtraction/division, each Dense matrix product, bias, ReLU,
masking and family pooling. Save operands, outputs, device/dtype, elementwise signed,
absolute and relative errors, the unchanged `atol=1e-5, rtol=1e-4` thresholds and
failing indices. Instrumentation must exactly match the unchanged model on its
own device. Replay each primitive using the *same CPU operands* to separate local
rounding from propagated error. Compare each operation with float64 arithmetic on
its exact operands and compare the propagated MLP/pool chain with a float64 chain
anchored to CPU prepared float32 features and float32 weights.

Full-significand FP32 error envelopes are illustrative diagnostics with explicit
no-overflow/underflow assumptions. They are not TF32 bounds, proofs of correct
implementation, replacement tolerances or scientific acceptance criteria. The
propagated chain starts after feature preparation; preparation has separate local
comparisons. The process performs no optimizer updates and invokes no training.

## One bounded allocation

- **One A100, 32 reserved Slurm CPUs, 56 GiB RAM, 20 minutes total.** Limit application
  affinity to eight CPUs; account all 32 reserved CPUs. No concurrent PET job.
- New reservation ceiling: **0.333333 GPU-hours / 10.666667 reserved CPU-hours**.
  Count the existing conservative **290 seconds** first (0.080556 GPU-hours /
  2.577778 reserved CPU-hours), increasing it if scheduler remeasurement requires.
  Prior plus this maximum: **0.413889 GPU-hours / 13.244444 reserved CPU-hours**,
  excluding separately accounted preparation. Existing aggregate ceilings remain
  290 GPU-hours / 9,296 reserved CPU-hours / 200 GiB storage.
- New diagnostic output at most **1 GiB**, plus at most **1 GiB** independently
  read-back durable copy, within the existing working/durable ceilings. Meter
  output every five seconds. Slurm enforces memory and wall time. Internal capture
  deadline is 19 minutes, leaving one minute for closure/cleanup; it does not
  extend the 20-minute allocation. Meter preparation CPU time separately.
- One attempt only. No retry, calibration, full-matrix job or automatic continuation.
  Numerical mismatch is a diagnostic measurement and does not stop later fixed
  captures. Invalid instrumentation, modified inputs/code, wrong runtime/device,
  missing artifacts, source access or resource failure stops dependent processing
  and retains the partial evidence.

## Execution and terminal verification

Before submission, record a new authorization naming this decision and bind the
bytes of `numerical-manifest.json`; the pending template cannot authorize a run.
Verify clean local/remote execution revision, every manifest file, canonical
Perlmutter live-state freshness, direct scheduler state, prior accounting and
free storage. Use a new standalone execution checkout, output directory and the
existing immutable Linux GPU runtime/dependency lock. No edits to failed attempts,
guard, package pins or scientific sources. Linux Python 3.11; NumPy 1.26.4,
TensorFlow 2.16.2, Keras 3.15.1, SciPy 1.16.3 and pytest 9.1.1 remain required.

Prepared launcher: `sbatch_numerical_diagnostic.sh CHECKOUT RUNTIME NEW_OUTPUT
EXPECTED_COMMIT APPROVAL_JSON APPROVAL_SHA256`. Scheduler test-only admission
must be checked before the actual submission. The launcher requires a distinct
`pooled-numerical-diagnostic-only` authorization and cannot call calibration.

After exit, check scheduler terminal/exit code, each of the six guard receipts,
source/input/weight identities, operation devices, exact instrumentation and
same-device repeatability. Verify worker manifests before reduction. Archive and
independently read back *all* outputs and logs, including numerical or technical
failures, then write a final closed-file manifest after guard/accounting writers
finish. The reducer's internal inventory is provisional while its own log/guard
writers are still open; it is not the final preservation receipt.

A complete capture is `COMPLETE_DIAGNOSTIC`, never a compatibility or scientific
PASS. Any integrity failure is `INSTRUMENT_INVALID` or `TECHNICAL_FAILURE`. Neither
state authorizes another allocation. Report the first differing operation, exact
failing elements and denominators, local versus propagated errors, TF32 effects,
and any unresolved alternatives. Propose a justified repair or precision-policy
amendment only after measurement; do not widen tolerances after observing results.

No real-source reads/training, producer correspondence, normalization, covariance,
uncertainty coverage, publication adoption, central/statistical pairing or Gate-6
work is included. PET remains diagnostic and method-development.
