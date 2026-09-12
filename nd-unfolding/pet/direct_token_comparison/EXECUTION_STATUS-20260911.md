# Current state: second technical failure; execution stopped

## 2026-09-13 — single compatibility/calibration attempt authorized

Joseph approved `21c0d163` and its bound proposal.
[Exact authorization](COMPATIBILITY_AUTHORIZATION-20260913.md): one A100,
32 reserved CPUs, 56 GiB, 110 minutes total, with 20-minute preflight and
90-minute calibration caps. Both prior attempts remain charged. The full matrix
requires GPU compatibility, complete paired calibration, integrity and all
existing 20% headroom gates. No automatic retry or criterion change is covered.
Deployment and direct scheduler checks precede the single submission.


## 2026-09-13 — compatibility repair prepared; no new allocation

Local deterministic packing validation and a stronger two-arm GPU preflight are
recorded in [the repair](COMPATIBILITY_REPAIR-20260913.md). The
[110-minute smoke/calibration proposal](COMPATIBILITY_PROPOSAL-20260913.md) is
pending explicit approval. Both previous attempts remain terminal failures;
partial pooled outputs are excluded from comparisons. GPU compatibility and
paired calibration remain unverified. No full matrix or real-data run is released.


Retry `58201775` passed the Linux tests, package pins and A100 operation check.
The pooled calibration arm saved three artifacts; the direct-token arm failed
at deterministic GPU `DenseBincount` during model construction. The paired
calibration is incomplete, so no headroom pass or full-matrix launch is possible.
No third attempt was submitted. [Exact retry result and accounting](RETRY_RESULT-20260912.md).

The two Slurm parent allocations total 190 seconds: 0.052778 GPU-hours and
1.688889 reserved CPU-hours. Partial artifacts and failure evidence are preserved.
No learning-performance conclusion or change of scientific scope follows.

# First calibration — historical terminal record

**Job 58198332 FAILED before GPU validation or training. No retry and no full
campaign jobs were submitted.** The approved no-retry stop is in force.

The [resource amendment was authorized](RESOURCE_AUTHORIZATION-20260911.md), and
calibration executed from clean isolated commit
`106ba9a872989e2617a68f48333e7c831f94c67e`. Canonical Perlmutter main remained at
`32e403b84e9e8f9d9bc435028749f896653c7a43`; freshness passed before submission.
The original occupied checkouts and remote `pet-prong-semantics` were untouched.

[Exact terminal evidence](execution_runs/20260911-calibration/terminal.json)
binds the Slurm accounting, logs, imports, local correction check and preserved
payload. Slurm recorded `FAILED`, `1:0`, **79 seconds**, **one A100 / 32 CPUs /
56 GiB**: **0.021944 GPU-hours and 0.702222 reserved CPU-hours**. Batch MaxRSS was
**1,031,876 KiB**; it includes the CPU test process and is not training memory.
The measured new cluster paths occupy **4.961057 GiB** of allocated blocks
(runtime, isolated checkout, deployment bundles, scratch and CFS). Local
development environments/evidence copies are outside that storage measurement.
No extrapolated training throughput, headroom pass or learning result exists.

The guarded Linux rehearsal passed **49 tests and 10 subtests in 39.64 seconds**.
The next process failed at `importlib.metadata.version('numpy')`. The guard's
replacement `PathFinder` exposes no `find_distributions` hook. A local read-only
probe reproduces missing metadata while the guarded NumPy import reports
`1.26.4`. This is an instrumentation compatibility failure, not evidence that
NumPy is absent or that either representation learns poorly. No GPU operation
validation, fit, prediction, weight artifact or source access occurred.

The correction reads `__version__` from each actually imported module through
the unchanged guard. Its local version-only check confirms NumPy 1.26.4,
TensorFlow 2.16.2, Keras 3.15.1, SciPy 1.16.3 and pytest 9.1.1. The guard and
scientific runner/model bytes are unchanged. Linux/A100 operation remains
unverified. The prepared headroom evaluator rejects the closed failed receipt
before attempting extrapolation; its positive resource gate has not been run.

All **13 closed output files / 51,619 bytes** were copied to
`/global/cfs/cdirs/m3246/josephrb/pet-routing-comparison/20260911-calibration-58198332/payload`.
Source-before, source-after and destination inventories match file-by-file;
the local copy and its committed `preserved/payload.tar.gz` archive were each
independently read and matched to the same hashes. The unmodified raw receipt
is historical; [its code binding](execution_runs/20260911-calibration/execution-revision-binding.json)
uses the exact executed revision, not the corrected working-tree file.
The [preservation receipt](execution_runs/20260911-calibration/preserved/preservation.json)
is the evidence, not the path alone.

A [single 118-minute retry is prepared](RETRY_PROPOSAL-20260911.md), requiring an
explicit exception to the no-retry stop. It counts the failed 79 seconds and fits
inside the existing aggregate GPU/CPU ceilings even if all 24 full jobs reach
their 12-hour caps. Its authorization remains pending. No scientific criterion
or scope restriction changes. Synthetic results, if eventually obtained, cannot
establish real-data representation performance or authorize adoption, covariance
or Gate-6 work.

# Historical preflight record — superseded by the terminal result above

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
