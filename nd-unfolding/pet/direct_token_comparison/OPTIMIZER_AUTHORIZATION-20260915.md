# Authorized optimizer diagnostic — 15 September 2026

User instruction, verbatim:

> Fix that and I authorize another GPU allocation

This grants one new allocation following `58301971`. The concrete diagnostic
uses one A100, 32 reserved CPUs, 56 GiB and at most 20 minutes, with eight
application CPUs and a 1 GiB output stop. No automatic retry or concurrent PET
job. Prior conservative charges are 523 seconds; including the entire allocation
would be 1,723 seconds, 0.478611 GPU-hours and 15.315556 reserved CPU-hours,
before separately accounted preparation. Existing aggregate 290 GPU-hour,
9,296 CPU-hour and 200 GiB storage ceilings remain unchanged. This diagnostic
alone cannot release calibration or the full matrix.

The repair is capture-first numerical evidence. The scientific preflight,
models, packing, frozen CPU oracle, precision policy and all tolerances remain
byte-identical to `be1fadef`. A separate diagnostic saves all eight pairs'
initial weights, inputs, eager/repeated/traced derivatives, model and Adam states
after each update, and predictions before cross-device comparisons. It compares
its final weights and predictions exactly with the unchanged preflight on each
device. Any instrumentation mismatch makes causal interpretation unverified.
All initial pairs are built in the preflight's original order before additional
diagnostic operations. Historical failing weights were not saved; this is a
reconstructed seed recipe, not recovered historical bytes.

Fresh Adam instances replay each device's two saved gradient sets on identical
initial operands on CPU and GPU. An independent float64 NumPy implementation of
the pinned Adam formula supplies a higher-precision reference; it is neither a
new optimizer nor a justified acceptance/error budget. Every coordinate remains
available in the arrays; summaries record the unchanged absolute/relative
criterion, failed count, maximum error/budget ratio and worst coordinate.
Numerical discrepancies are diagnostic outcomes, not permission to train.
Unexpected execution failures preserve partial files and stop this allocation.

Use a new clean pushed standalone checkout and new output, verify all manifest
hashes and the unchanged pinned Linux/CUDA runtime, canonical-main freshness
(only its own HEAD), scheduler queue, prior accounting, storage and scheduler
admission. Invoke `sbatch_optimizer_diagnostic.sh` with checkout, runtime, new
output, expected commit, authorization JSON and its SHA-256. The import guard
covers execution. Preserve closed outputs to CFS and independently read back
all artifact hashes locally before quoting results.

No real-source access, source normalization/training, producer correspondence,
publication adoption, covariance, central pairing or Gate-6 action is included.
