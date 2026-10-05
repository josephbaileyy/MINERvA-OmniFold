# Calibration retry: second technical failure, execution stopped

**The retry did not complete. No full-matrix job and no third attempt were
submitted.** This applies the explicit stop condition in Joseph's
[retry authorization](RETRY_AUTHORIZATION-20260911.md).

Job `58201775` ran from clean isolated commit
`46fe3d7cd3c88570d7449a884adc4f8ffc44f041` on 11 September 2026, 11:01:49–11:03:40
in the scheduler's Pacific timestamps. This terminal report was verified on
12 September UTC. [Machine-readable result](execution_runs/20260911-retry1/terminal.json).

## What passed, and where it stopped

* The unchanged guarded Linux suite passed **49 tests and 10 subtests in 38.80 s**.
* All five package versions matched; the A100-SXM4-40GB was visible, and the
  recorded matrix operation executed on `/device:GPU:0`.
* The **pooled calibration arm** produced its reconstructed and truth model
  files plus an NPZ with training weights and held-out predictions.
* The **direct-token arm** then failed during its initial two-row model call,
  before its training. Its `RaggedTensor.from_value_rowids` invokes GPU
  `DenseBincount`; TensorFlow 2.16.2 raised `UnimplementedError` because that GPU
  operation does not support the required deterministic mode in this runtime.

The pooled artifact saves precede construction of the direct model in the
frozen runner. Thus this was **partial pooled training followed by a direct-arm
initialization failure**, not a failure before all training. The initial status
reply saying that training never started was too broad and was corrected after
checking the arm-specific path and saved files.

No complete paired receipt or timing profile was written. The resource/headroom
gates therefore cannot be evaluated, and the full matrix cannot proceed.
Determinism was not disabled, scientific code was not changed, and no third
allocation was attempted. This runtime incompatibility and the partial pooled
artifacts provide **no evidence of relative learning performance**. Calibration
is excluded from the eight-seed comparison in any case.

## Measured resources

| Quantity | First allocation | Retry | Total / interpretation |
|---|---:|---:|---|
| Slurm parent elapsed | 79 s | 111 s | **190 s** across two one-A100 allocations |
| GPU reservation | 0.021944 h | 0.030833 h | **0.052778 GPU-hours** |
| Reserved CPU time (32 CPUs) | 0.702222 h | 0.986667 h | **1.688889 CPU-hours** |
| Batch MaxRSS | 1,031,876 KiB | 1,371,956 KiB | Process-family peak; not a full-job memory extrapolation |

The retry's overlapping `extern` cleanup step reports 114 seconds, three longer
than its parent. Steps are not added to the same allocation again. A conservative
sum using each attempt's longest reported step is **193 seconds**, or
**0.053611 GPU-hours / 1.715556 reserved CPU-hours**. Both accounting views count
the first failure and remain far inside the grant; neither supplies a resource
gate pass. Local preparation CPU time is outside these Slurm measurements.

The [storage read](execution_runs/20260911-retry1/storage-measurement.json)
measures **5.037973 GiB** of allocated blocks across the named new
cluster runtime, both checkouts, deployment bundles, scratch and CFS copies.
Local development environments/evidence and pre-existing shared Git objects are
outside that measurement. This is a measured footprint, not projected matrix storage.

## Preservation and scientific scope

All **19 output files / 511,304 bytes**, including partial pooled artifacts,
were copied to
`/global/cfs/cdirs/m3246/josephrb/pet-routing-comparison/20260911-retry1-58201775/payload`.
Source-before, source-after and destination inventories match. The committed
archive retains their original bytes and supports independent readback;
[the preservation receipt](execution_runs/20260911-retry1/preserved/preservation.json)
lists every size and SHA-256. The executed code is bound to its exact revision.

PET remains diagnostic and method-development. No real-source access/training,
publication adoption, covariance construction or Gate-6 action occurred. Source
semantics remain unresolved. No synthetic routing winner has been established,
and no real-data representation-performance conclusion follows.
