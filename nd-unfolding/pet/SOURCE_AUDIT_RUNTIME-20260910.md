# PET source-audit runtime compatibility

**PASS — complete local and Linux synthetic runtime preflight. Real-source execution remains blocked.**

The locally passing synthetic runtime uses NumPy 1.26.4, SciPy 1.16.3,
TensorFlow 2.16.2 and Keras 3.15.1. Installation pins are in
`source_audit_runtime_requirements.txt`. Linux additionally uses the activated
ROOT 6.28/12 environment. This is a compatibility configuration for this bounded
audit, not a general dependency recommendation or a scientific validation.

## Diagnosis and repair

The local SciPy 1.17.1 traceback follows TensorFlow's import of `scipy.sparse`
into SciPy's array API compatibility layer. Its `clone_module("numpy", ...)`
enumerates NumPy attributes, accesses `numpy.testing`, and consequently requests
`lscpu`. The unchanged import guard refuses that child. SciPy 1.16.3 uses
`from numpy import *` in that location instead; the fresh-process synthetic
forward check succeeds. Exact local failing and passing logs are preserved in
`runtime_runs/20260910/`. The prior direct use of NumPy testing assertions in the
audit itself was already removed in `48a3b956`.

`check_source_audit_runtime.py`, committed in `f59d8170`, exercises the complete
8,192-row fake-reader audit with the actual fixed-weight NumPy/Keras forward
checks and serialization. Its two JSON fixture rows are synthetic, including
sentinel combinations. It does not open ROOT sources, fit normalization or train
a model. `--with-root` imports ROOT only to exercise library coexistence.
Linux installs the original audit process limits; a local macOS pass explicitly
reports that those Linux limits were not enforced.

Loaded modules supply the dependency versions in the receipt. Package metadata
lookup under this guard returned no distributions in the first local trial;
that empty field was corrected before the committed probe. It is not interpreted
as an absent dependency or silently copied from the requirement pins.

## Measured outcomes

| Run | Result | Qualification |
|---|---|---|
| Local SciPy 1.17.1 | Guard refused `lscpu` during TensorFlow dependency imports | Trace identifies SciPy's NumPy attribute enumeration. |
| Local SciPy 1.16.3, `f59d8170` | All 8,192 fake rows and 512 forward/serialization chunks complete | No Linux resource acceptance and no ROOT import. |
| Linux allocation `58168872`, `f59d8170` | First forward chunk fails NumPy/Keras comparison | Imports pass; the original probe did not sample resources after a failed forward. |
| Linux allocation `58174544`, `10deb714`, oneDNN=1 | Numerical mismatch and four observed threads | Original numerical and two-thread ceilings fail. |
| Same allocation/commit, oneDNN=0 | Same numerical mismatch and four observed threads | Disabling oneDNN does not resolve either condition. |

Both numerical arms report row 0, output column 51: NumPy `-0.02375269`,
Keras `-0.023749307`, absolute difference `3.3825636e-6`, allowed difference
`1.2375269e-6`, with eight mismatched values in the 16-row chunk. These are
synthetic diagnostic values, not MINERvA measurements. The thread check runs in
`finally`, so its resource exception retains the original numerical exception
in the traceback. Neither is hidden by the other.

The independent local float64 `math.fsum` dot/tanh/pool calculation for that
synthetic coordinate gives `-0.023751626420102034`, between the two float32
values. It supports investigating rounding and cancellation; it does not prove
which runtime operation caused the discrepancy or adopt an error tolerance.
`rounding-diagnostic.json` records linear-operation error bounds only, explicitly
excluding a certified end-to-end activation/reduction bound.

The numerical arms observed four threads and approximately 744 MB RSS at the
post-forward sampling boundary. The hard process limits remained installed;
the failure is not acceptance under an expanded thread ceiling. All three
Linux processes terminated before a completed typed chunk. Both allocations
are terminal, and no new source audit was attempted.

The source-audit unit suite passes all 60 tests after the diagnostic changes.
Black, Ruff and targeted mypy pass on the changed source modules. The guard and
comparison tolerance remain unchanged.

## Authorized follow-up and numerical criterion

The user approved four observed process threads with two CPUs per step and one
configured worker in each TensorFlow/native pool. Memory, CPU-time, wall-time,
output and import-guard limits are unchanged. The revised preparation invalidates
any authorization bound to an earlier preparation digest.

The candidate comparison checks prepared feature arrays and copied kernel/bias
arrays for exact equality on every chunk. Each backend's token projections and
pooled outputs are then checked separately against a float64 oracle. Event
columns, object counts and C0 remain exact checks. The first chunk's hashes,
maximum absolute errors and fractions of the budget are included in the runtime
summary. This is a synthetic numerical acceptance contract, not physics evidence.

For float32 unit roundoff `u = 2^-24`, a dot of width `n` uses the conservative
`gamma_(2n+2) = (2n+2)u / (1-(2n+2)u)` bound, multiplied by
`sum(abs(x_i*w_i)) + abs(bias)`. This covers separate products, arbitrary-order
summation and bias addition; fused operations need no larger allowance.
The calculation also includes float64 oracle roundoff and float32 underflow
allowances. Applying monotonic `tanh` to both interval endpoints propagates
this error while preserving saturation. The original `1e-6` absolute allowance
is retained for each elementary activation, whose range is bounded by one;
it is not a vendor-certified transcendental accuracy guarantee. Pooling adds
the token bounds and `gamma_m * sum(abs(oracle_token) + token_bound)` for `m`
tokens. Both backend results must fall within that independently calculated
interval. There is no tolerance chosen from the observed final discrepancy.

The activation allowance is tested against scalar float64 `math.tanh` on
20,004 synthetic inputs spanning saturation, zero and both signs. The float64
matrix oracle is separately checked against `math.fsum` products and scalar
`tanh` for all coordinates of the first fixture row. Fault tests reject altered
features, weights, token outputs and values outside the computed budget.
These checks support the bounded synthetic runtime contract; they do not prove
a universal error guarantee for arbitrary hardware or transcendental libraries.

The revised local fake-reader run completes all 8,192 rows and 512 chunks under
the unchanged import guard, with no foreign-checkout imports observed. Prepared
features and weights agree exactly. The first-chunk maximum pooled absolute
errors are `2.424e-6` for NumPy and `2.200e-6` for Keras; every individual
comparison is inside its calculated budget. On the activation grid, maximum
absolute errors are `5.885e-8` for NumPy and `2.385e-7` for TensorFlow, below the
unchanged elementary activation allowance. These are development measurements
from the uncommitted preparation, not committed Linux acceptance evidence.

The audit suite passes 67 tests. Black, Ruff and strict targeted mypy pass on
the changed source modules. An initial local invocation accidentally used the
older SciPy 1.17.1 environment and reproduced the recorded guarded-import
failure; the complete runs use the compatible SciPy 1.16.3 environment.

Linux job `58178592` runs the clean preparation commit `ca34a03a` with
ROOT 6.28/12, NumPy 1.26.4, SciPy 1.16.3, TensorFlow 2.16.2 and Keras 3.15.1.
It completes all 8,192 rows and 512 typed chunks with no exceptions, all six
receipt checks passing, exact operand agreement and zero ROOT source opens.
The first-chunk maximum pooled absolute errors are `2.424e-6` for NumPy and
`2.320e-6` for Keras, both within their calculated per-output budgets. The
TensorFlow activation-grid error is at most `2.717e-7`; NumPy is `5.885e-8`.

The scheduler rounds the request for two CPUs and 8 GiB memory to six reserved
CPUs, within the existing reservation ceiling. Step `.0` uses exactly two CPUs.
Both the allocation and step are `COMPLETED`, exit `0:0`; allocation elapsed
is 5 minutes 11 seconds. The audit's wall measurement is 268.56 seconds, its
peak observed process thread count is four, and its peak observed process RSS
is 993,112,064 bytes (947.11 MiB). Scheduler step MaxRSS is 1,945,916 KiB;
that separate step-level measurement is also below the 8 GiB ceiling. Process
boundary samples do not claim continuous monitoring of transient threads/RSS.
The recorded artifact bytes excluding logs and receipt are 173,658,980.

The unchanged guard reports zero repository origins outside the expected
checkout and `child-systemexit:0`. Closed receipt, guard and summary digests
match after transfer. The exact compressed JSON bytes, scripts, scheduler and
checkout records are preserved under `runtime_runs/20260910/linux-roundoff/`,
with its own `preservation-manifest.json` and `verification.json`. Historical
failed receipts retain their original criteria and are not relabeled as passing.

This preflight exercises the fake-reader audit, process budget, forward checks
and shard serialization. It does not execute `RootAuditReader` or the real
launcher's final `accounting.json` writer. Synthetic resource observations are
in `runtime-summary.json`; they are not a substitute for the real-source
accounting required by the runbook. No source mapping, release, normalization,
training or scientific acceptance follows from this synthetic pass.

## Reproduction

Use a clean checkout of the probe commit and a separately created environment
installed from the requirements file. On Linux, activate the ROOT environment
before invoking its isolated Python interpreter. Place outputs outside the
checkout, in a new directory. The guard inventory must also have a new path.

```bash
python nd-unfolding/mnv_guarded_run.py \
  --expect-root "$PWD" --inventory ../pet-runtime-guard.json \
  -- nd-unfolding/pet/check_source_audit_runtime.py \
  --with-root --output ../pet-runtime-synthetic
```

Omit `--with-root` for the macOS compatibility check. Check both the guard
inventory and `runtime-summary.json`; inspect `receipt.json` for completion of
both fake sources and their 16-row chunks. The script reports synthetic mapping
acceptance only. Its semantic telemetry comes from invented fixture rows, not
MINERvA source observations.

The local and Linux compressed receipts preserve their original JSON bytes.
The preservation manifest binds those receipts, logs, guard records and runtime
summaries. Synthetic raw archives and NPZ chunks remain reproducible test output
and are not publication evidence. The original real-source attempt and its
partial artifacts remain separately frozen under `source_audit_runs/20260910/`.

## Scientific boundary

The synthetic grant is recorded in
`SOURCE_AUDIT_RUNTIME_AUTHORIZATION-20260910.md`. It does not authorize another
real-source audit. That later decision must name the code commit, preparation
digest, compatible runtime, resource budget and new output directory. The
original audit remains incomplete; source mapping, release applicability,
normalization and scientific training have not been established by this work.
OI-126 and all five Gate-6 prohibitions remain unchanged.
