# GPU compatibility attempt 58240587: numerical gate failed, execution stopped

**The approved single attempt failed in GPU preflight. Calibration did not start,
and no full-matrix job or retry was submitted.** The fixed tolerance and all
scientific criteria remain unchanged. This exhausts the additional attempt in
[the authorization](COMPATIBILITY_AUTHORIZATION-20260913.md).

The job executed clean revision `7673b2de5210da0d2679ed98da62a4d0f2e042b2`, which
adds the authorization to the approved repair at `21c0d163`. All repair-manifest
files matched. The allocation ran on 12 September, **09:48:06–09:49:41 Pacific**
(13 September, 01:48:06–01:49:41 Asia/Seoul), with one A100, 32 reserved CPUs,
56 GiB and the approved 110-minute hard limit. The scheduler's earlier test-only
start estimate proved inaccurate; the real job started within minutes.
[Exact terminal receipt](execution_runs/20260913-compatibility/terminal.json).

## What ran and where it stopped

* The guarded Linux CPU regression suite passed **60 tests and 10 subtests in
  42.58 seconds**. Runtime versions and the full dependency lock matched the
  existing pinned environment; `pip check` found no broken requirements.
* TensorFlow created the **NVIDIA A100-SXM4-40GB** device. Repository-origin
  guard checks passed without allowances; these checks establish import origins,
  not model compatibility.
* Preflight reached the **nominal, pooled model's routed-embedding CPU/GPU
  comparison**, after constructing the original CPU and repaired GPU pooled
  models and copying their initial weights exactly. This case has four fixture
  events and, by the unchanged pooling shape contract, 4 × 3 × 16 = 192 embedding
  components. It is the pooled path, before direct-model validation.
* `np.allclose` failed with the frozen **atol 1e-5 / rtol 1e-4**. The log records
  **maximum absolute difference 0.0004892349243164062**. The actual tensor pairs
  and number of exceeding elements were not saved, so the log does not support
  an element-level or relative-error breakdown.
* The full-model gradient, Adam-update and reload checks were **not reached**;
  neither was direct-model GPU validation. No `preflight.json` PASS, calibration
  directory, paired calibration receipt or resource timing profile exists.
  The sole NPZ is the four-event **input fixture**, not a trained result.

The executed code calls `packing_checks` before saving that fixture or entering
this model comparison. Reaching the recorded failure therefore **implies through
control flow** that its low-level exact row-split/value/mask/packing-gradient
assertions completed, including empty and variable-multiplicity cases. Its
standalone numerical summary was not written because the whole preflight failed;
this is not a complete GPU compatibility receipt.

The numerical discrepancy's kernel/precision cause is **unresolved**. No new GPU
probe was run and no tolerance, determinism setting or model code was changed.
This result supplies no pooled/direct learning comparison and no evidence about
real-data representation performance. The earlier exact local CPU equivalence
measurements remain valid within their documented scope.

## Measured resources and preservation

[Accounting and footprint receipt](execution_runs/20260913-compatibility/resource-usage.json):

| Quantity | This allocation | All three attempts |
|---|---:|---:|
| Parent Slurm elapsed | **95 s** | **285 s** |
| GPU reservation | **0.026389 h** | **0.079167 h** |
| Reserved CPU time, 32 CPUs/allocation | **0.844444 h** | **2.533333 h** |
| Slurm TotalCPU consumption | **42.499 CPU-s** | **147.583 CPU-s** |
| Longest overlapping step per allocation | **97 s** | **290 s** |

The last row counts each allocation once using its longest reported step, not
by adding overlapping batch/extern steps. The conservative aggregate is therefore
**0.080556 GPU-hours / 2.577778 reserved CPU-hours**. Batch peak RSS was
**1,258,016 KiB**. Local preparation CPU consumption is outside these Slurm
measurements and was not separately metered.

Named new cluster storage measured **5.116897 GiB**, including the runtime,
three checkouts, all four deployment bundles, scratch outputs and verified CFS
copies. The receipt lists every measured path; local environments/evidence and
pre-existing shared Git objects are excluded. Remaining budget is not permission
for another allocation, and no headroom gate can be evaluated from this failure.

The failed job's **9 files / 58,406 bytes**, plus preallocation and terminal
observations, form **29 files / 76,082 bytes**. All were copied without changing
the sources to
`/global/cfs/cdirs/m3246/josephrb/pet-routing-comparison/20260913-compatibility-58240587/payload`.
Source-before, source-after and destination inventories agree. The committed
[archive and preservation manifest](execution_runs/20260913-compatibility/preserved/preservation.json)
were read back entry by entry. The [execution revision bindings](execution_runs/20260913-compatibility/execution-revision-binding.json)
preserve the exact code; archived raw guard receipts retain their original bytes.
Both earlier failed attempts and their partial pooled artifacts remain untouched
and excluded from performance comparisons.

Direct scheduler observation showed this PET allocation terminal; an unrelated
scalar-study job was left untouched. No terminal-resume service was installed
or left running. Execution is stopped under the grant: no automatic retry,
full matrix, source access, publication adoption, covariance or Gate-6 action.
