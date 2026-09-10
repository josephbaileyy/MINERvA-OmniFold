# PET source-audit runtime compatibility

**Import compatibility repaired; full Linux runtime acceptance remains blocked.**

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

## Contract decision still needed

The current preparation still caps **all observed process threads at two** and
uses `rtol=1e-5`, `atol=1e-6` for NumPy/Keras output agreement. Do not relax either
criterion merely to obtain a pass, or call the local result Linux readiness.

A concrete proposed resource revision is four total process threads while
retaining two allocated CPUs per step, one configured worker per TensorFlow
pool, the 8 GiB process ceiling and the same bounded synthetic input. This is
pending the user's answer; it has not been installed in the audit limits.

A numerical revision needs separate validation: compare identical prepared
features and weights, measure each backend against a higher-precision oracle,
and derive and power-test an error budget for the dot, activation and pooling
operations. The observed failing fixture alone cannot set a new tolerance.
Until that contract is supported, preserve the current FAIL and do not spend
more allocations repeating the unchanged oneDNN comparison.

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
