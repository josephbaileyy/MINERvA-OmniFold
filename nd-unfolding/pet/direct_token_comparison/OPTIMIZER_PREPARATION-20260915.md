# Optimizer diagnostic preparation

The separate capture-first diagnostic leaves the preflight and scientific model
unchanged. Final guarded CPU rehearsal completed all eight pairs with exact
same-device final weights and predictions against the unchanged preflight.
The frozen guarded suite passed 69 tests plus 10 subtests; two new unit tests
check asymmetric tolerance reporting and the float64 Adam implementation against
closed-form constant-gradient moments. Black, Ruff, strict mypy and shell syntax
checks pass. These are local CPU checks, not GPU compatibility evidence.

All 278 rehearsal files were archived and independently read back; see
[validation and file hashes](local_validation/20260915-optimizer/validation.json).
The final diagnostic and four test guard records report zero outside-checkout
repository origins and no violations. Raw measurements are retained before
comparisons; production acceptance thresholds are unchanged.

[The user's authorization and concrete resource limits](OPTIMIZER_AUTHORIZATION-20260915.md)
cover one new 20-minute diagnostic allocation. `optimizer-manifest.json` and
`optimizer-authorization.json` bind the exact executable files. Runtime discovery
matches the complete prior Linux/CUDA lock. No allocation has been launched at
this preparation point, and no calibration or full-matrix continuation follows
from a diagnostic result.
