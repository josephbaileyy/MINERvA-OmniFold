# PET v2 source-audit interruption and runtime repair

**INCOMPLETE — no source acceptance verdict.** The authorized attempt used
`588328438e096680a2295bebc7cc93ad9fccc3ed`, with authorization committed in
`82707fd6`. Its original preparation SHA-256 is
`58e3043b43c446a5b7e057815fc1bfbf8edec782335ce412b09da9f996f91b59`.
The frozen authorization and original embedded preparation are preserved;
they are not rebound to the repaired checker.

## Preserved attempt

The evidence directory is [source_audit_runs/20260910](source_audit_runs/20260910/).
`interrupted-audit/progress.jsonl` records attempted and captured data entry 0.
Both source metadata records, the raw data row and its observations survive.
There is no MC payload archive, completed typed shard, `receipt.json` or
`accounting.json`. The initial interruption marker remains `INCOMPLETE` and
`mapping=NOT_TESTED`; it is not a reconstructed terminal receipt. No mapping,
semantic, release or object-family acceptance is inferred from the partial row.

`preflight/source-guard.jsonl` and the original `stderr.log` record a refused
`['lscpu']` child launch, exit 3, with no repository imports outside the pinned
checkout. `dependency-inspection.json` binds the installed NumPy utility source:
importing `numpy.testing` evaluates `check_support_sve()`, which invokes
`subprocess.run('lscpu', ...)`. The checker first requested NumPy testing
assertions during mapping after saving the raw row and observations. This
source-level trace explains the refusal; the original log has no Python stack.
The guard remains unchanged, including its child-process policy.

`scheduler.txt` is a direct scheduler re-observation during recovery. Allocation
`58164405` is `COMPLETED`, elapsed `00:07:23`, with six allocated CPUs. Source
step `.2` is `FAILED`, exit `3:0`; allocation completion is not audit success.
The allocation was released by the original session. Recovery launched no new
allocation and opened no ROOT source. `remote-artifact-hashes.json` was freshly
measured from the terminated output directory; all eight local audit files match
its byte counts and SHA-256 values, including the empty stdout log.

`recovery-manifest.json` binds the preserved files. It is a recovery inventory,
not the missing runtime accounting or a scientific validation receipt. Preflight
live-state snapshots are historical views and must not guide another run.

## Software repair and its limits

Runtime mapping, provenance and C0 checks now use `np.array_equal`; forward
agreement uses explicit shape equality and `np.allclose` with the existing
`rtol=1e-5`, `atol=1e-6`. Raw dtype/byte checks, finite-output requirements,
source identities, branch list, entry interval and resource limits are unchanged.
Exact array checks reject shape differences rather than broadcasting.

The complete two-source fake-reader test and the synthetic Keras forward test
now reject any access by the checker to `numpy.testing`. The regression run
passed 111 tests and 10 subtests; its sole failure was the test-file binding
awaiting refresh. After refreshing that binding, the remaining preparation test
passed. Thus all 112 tests and 10 subtests pass across those runs. Black and Ruff
pass on both changed Python files; targeted mypy passes on the two audit source
modules. These are software checks, not source validation.

A separate fresh-process local guarded synthetic probe progressed to forward
adapter imports but was also refused on `lscpu`. Its exact script, guard record
and log are preserved under `local-synthetic/`. This is a distinct local runtime
observation, not evidence that the Linux runtime has the same dependency path.
It establishes that removing the checker's testing assertions alone does not
certify guarded forward initialization. The isolated probe used only synthetic
inputs; no ROOT data, fitting or training was involved.

The revised preparation digest is
`7a7404367a98ab234c282dae94b6bdeaa8ee46c7ad42801a8f766f42a716b120`.
The preparation-only launcher check passes and still reports
`execution_authorized=false`.

## Next action

First establish a compatible fresh-process forward initialization using only
synthetic inputs under the unchanged guard and resource limits in the proposed
Linux environment. Any additional cluster resource request needs a concrete
budget and authorization. Do not preload around, suppress or widen the guard to
obtain a passing result. A further real-source attempt then needs a new grant
bound to the repaired code commit, preparation digest, environment, resource
ceiling and a new output directory. The original one-attempt grant is exhausted.

Normalization still requires its selection sidecar and pooling implementation;
scientific training is a separate stage. OI-126's pairing remains declined and
the existing `C_stat` construction remains unverified. No PET total covariance
is adopted. The five exact Gate-6 prohibitions in the execution authorization
remain in force; this repair supplies no Gate-6 result or permission.

## Subsequent synthetic runtime investigation

The later synthetic-only grant produced the results in
[SOURCE_AUDIT_RUNTIME-20260910.md](SOURCE_AUDIT_RUNTIME-20260910.md). Imports now
pass in the candidate Linux runtime, but its original thread and numerical
criteria fail. This does not complete or replace the interrupted source attempt.
