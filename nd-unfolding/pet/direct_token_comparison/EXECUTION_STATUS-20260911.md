# Current authorization

The [resource amendment is now authorized](RESOURCE_AUTHORIZATION-20260911.md).
Calibration is the next action; the following preflight history remains intact.
No result from the new allocation is yet claimed. The calibration driver records
Python call-profile timings so the headroom calculation can separate training
and inference. Profiling wraps the unchanged scientific runner and adds no
training operation; its overhead is retained in the conservative cost estimate.

# Execution status: stopped at scheduler preflight

**Calibration NOT STARTED; full matrix NOT STARTED. Zero training allocations
submitted and zero GPU-hours consumed by this campaign.**

The original grant was recorded and the reviewed preparation committed and
pushed on `pet-direct-token-comparison` at
`9d598c083bca742944e30b4079c7390ece2be9d1`; all 12 repository commit checks passed.
The reviewed preparation file hashes still match. The occupied
`pet-prong-semantics` checkout and remote branch were not altered.

Perlmutter canonical main was observed at
`32e403b84e9e8f9d9bc435028749f896653c7a43`; its freshness checker returned FRESH.
The scheduler was observed directly and had no jobs for the account. This
freshness result validates only the view's freshness, not any scientific gate.

Read-only admission tests prove the approved reservation cannot be submitted:
1 GPU / 8 CPUs / 64 GiB is adjusted to 38 CPUs and rejected by the shared-GPU
queue's requirement of 32 CPUs per GPU. A reduced-memory eight-CPU control is
also rejected. One GPU / 32 CPUs / 56 GiB passes the scheduler test. Exact evidence
is in [the preflight records](execution_runs/20260911-preflight/).
The test output's prospective job identifier is not an allocation. No scientific
run failed, and no scientific result or closure verdict exists.

The [resource amendment](RESOURCE_AMENDMENT-20260911.md) requests 32 reserved CPUs,
56 GiB RAM and a 9,296 CPU core-hour total ceiling, with the 290 GPU-hour ceiling
and all scientific settings unchanged. The amendment is not authorized by the
original eight-CPU grant. Execution is held pending that specific correction;
there is no automatic resource escalation or retry.

The existing source-audit environment was also inspected through package
metadata: it contains `tensorflow-cpu==2.16.2`, not the GPU distribution. A
separate GPU runtime is installed with the same requested TensorFlow, NumPy and
Keras versions. Dependency consistency passes (`pip check`); the resolved lock,
installer download hashes and log are preserved beside these preflight records.
This is software preparation, not training or source access.
Calibration must still verify an actual A100 and successful GPU operation.

## Guarded test preparation

The first local attempt to run the full test suite under the unchanged import
guard exposed NumPy testing's optional `lscpu` SVE-capability probe. The guard
refused this unmodeled child, as it did in the earlier source-audit interruption.
This was a local preparation test, not a GPU allocation or scientific run.

The test-only driver now declines to launch that optional probe and invokes
NumPy's existing `OSError` fallback. This is restricted to x86_64 (where ARM SVE
is inapplicable) or a platform where `lscpu` is absent. Every other subprocess
call still reaches the original guard, and the temporary adapter is removed
before the tests run. No leaf is added to the guard, no forbidden child is
executed and no guard exception is suppressed. The scientific runner does not
use this adapter. The subsequent local test used the specified SciPy 1.16.3;
the older local preparation environment had SciPy 1.17.1, which eagerly imports
NumPy testing in fresh TensorFlow processes and is outside the execution pin.

One existing fresh-process reload test itself called `np.testing`, causing the
same optional probe in its child. It now uses `np.array_equal` on the finite
saved/reloaded arrays, retaining exact value and shape equality. The guarded
local suite then passed **62 tests and 10 subtests**. This is software evidence,
not an A100 runtime check or a learning result.

The cluster rehearsal runs the five descriptor/model/prong suites. The sixth,
legacy source-smoke suite remains local validation only: it imports the two
receipt-bound `dump_pointcloud_inputs.py` and `fullevent_fps_dataloader.py`
readers, whose hardcoded cluster search paths can resolve another checkout on
Perlmutter. They are excluded from repair by
[`AUTHORIZATION-20260903-oi136-failopen-repair.md` §2](../../../docs/orchestration/AUTHORIZATION-20260903-oi136-failopen-repair.md).
Neither those readers nor the guard is changed or repinned. The isolated
synthetic runner imports neither reader. Local source-smoke success does not
establish that those legacy readers are safe to launch on the cluster. The
optional `--include-source-smoke-tests` flag reproduces the full local scope;
the cluster launcher deliberately does not request it.

The final five-suite local rehearsal passed **49 tests and 10 subtests** in
23.57 seconds, with no cluster search paths in any of its four guard records.
The final full local suite passed **62 tests and 10 subtests** in 21.29 seconds.
Logs, child/parent guard records, prior failure logs, package versions and file
hashes are preserved in [the validation receipt](execution_runs/20260911-preflight/local-validation.json).
Black, Ruff, strict mypy (Linux target), shell syntax and whitespace checks pass.
These local results do not replace the pending Linux/A100 runtime validation.
