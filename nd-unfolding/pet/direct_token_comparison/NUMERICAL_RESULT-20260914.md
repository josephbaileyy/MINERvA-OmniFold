# Pooled numerical diagnostic: TF32 isolates the reproduced discrepancy

**Job 58277208 completed the authorized diagnostic, exit 0:0, in 105 seconds.**
All four process cells and reduction completed. No calibration, direct-model GPU
validation or training ran. No precision policy or tolerance was changed in the
campaign. The diagnostic grant is consumed; it has no automatic continuation.

The controlled TF32 switch isolates the reproduced pooled discrepancy to
TF32-enabled execution on this fixture. Turning it off removes every fixed-
tolerance failure without changing weights, features, masks or model parameters.
This supports explicitly disabling TF32 in a future, separately bound compatibility
run. It is not a claim of direct-token superiority or full GPU compatibility.

## Measurements

[Machine-readable terminal and measurements](execution_runs/20260914-numerical/terminal.json),
[complete comparison summary](execution_runs/20260914-numerical/summary.json), and
[all saved tensors and closed-file hashes](execution_runs/20260914-numerical/preservation.json).
The fixed CPU/GPU tolerance remains `atol=1e-5, rtol=1e-4`.

| Pooled output, four events × three families × 16 channels | TF32 enabled | TF32 disabled |
|---|---:|---:|
| Components exceeding tolerance | **112 / 192** | **0 / 192** |
| Maximum absolute CPU/GPU difference | **0.0004892349243164062** | **0.0000002384185791015625** |
| First unequal primitive | photon first Dense matmul | prong first Dense matmul |
| First over-tolerance primitive | photon first Dense matmul | none |
| All captured CPU/GPU components exceeding tolerance | 2,813 / 5,304 | 0 / 5,304 |
| Common-operand primitive replay failures | 839 / 4,624 | 0 / 4,624 |

Both independent processes for each setting reproduced these results exactly.
All **20 within/across-process repeatability comparisons were exact**, as was
the CPU result across TF32 settings. Instrumentation matched each unchanged model
exactly on its own device. Masks, counts and copied weights agree. Component
counts include repeated intermediate representations; they are not independent
physics events or learning trials.

The original failed job's pooled maximum difference is reproduced **exactly**.
Its four-event input bytes are recovered and hash-verified. Its weights were not
saved: the diagnostic uses one explicitly labeled reconstruction from the pinned
seed recipe, copied to every process. Matching the old maximum does not establish
historical weight-byte identity. The experiment isolates the TF32 policy effect;
no kernel-instruction trace was collected to prove which tensor-core instruction
executed. This qualification does not erase the controlled on/off observation.

## Float64 and operation-local checks

Identical-operand replay already fails at the first photon Dense matrix product
with TF32 enabled. Thus the difference is not introduced only by later pooling
or inherited solely from an earlier normalization difference.

With TF32 enabled, GPU operation-local errors exceed the illustrative ordinary-
FP32 envelope for 1,257 / 4,624 components; propagated MLP/pool errors exceed it
for 2,784 / 4,288 components. With TF32 disabled, both counts are **zero**.
These envelopes assume full-significand FP32 arithmetic and no overflow/underflow;
they are illustrative diagnostics, not TF32 bounds or replacement acceptance gates.
The propagated reference starts from the exact CPU prepared float32 features and
copied float32 weights; normalization has separate local comparisons.

The pooling operation itself differs from a float64 sum of its own operands by
at most **5.960464477539063e-8** in either mode. The larger TF32-enabled pooled
error is inherited from the MLP. Against the propagated float64 reference, the
largest family-pool error is **0.0004891015005310528** with TF32 enabled and
**1.8606791440944903e-7** with TF32 disabled. No tolerance widening is justified or
needed by this fixture's full-FP32 result.

## Integrity, accounting and preservation

Executed clean standalone commit `6298efc2`, the authorization record atop approved
preparation `f43048b4`. Every approved manifest file matched before and after the
run. The complete runtime lock matched the prior immutable GPU runtime. Canonical
main freshness was FRESH for its own `32e403b8` HEAD, not a claim of upstream parity.
The queue was empty before submission and again after completion.

All **six guard receipts** report successful repository-origin inspection with
no allowances or violations. All five bundle/worker seals verify. These are
provenance/instrument checks, not independent scientific verification.

| Resource | Measured value |
|---|---:|
| This allocation, including all overlapping steps counted once | 105 s |
| This GPU / reserved CPU usage | 0.0291667 GPU-hours / 0.933333 reserved CPU-hours |
| All four allocations, conservative | **395 s; 0.109722 GPU-hours / 3.511111 reserved CPU-hours** |
| Slurm batch CPU consumption / peak RSS | 64.239 CPU-s / 1,093,600 KiB |
| Preserved diagnostic output | **6,257 files / 38,635,139 bytes** |
| Preservation helper CPU consumption | 21.951754 CPU-s |

Interactive preparation command CPU time was not separately metered; it is not
included in those Slurm or preservation measurements. The separate preparation
allowance is not a GPU reservation measurement. No resource-headroom gate for
training can be inferred from this small diagnostic.

All output files were copied to
`/global/cfs/cdirs/m3246/josephrb/pet-routing-comparison/20260914-numerical-58277208/payload`.
Source-before/source-after/destination inventories match. The compressed archive
was read back on the cluster and again after transfer; every listed file matches,
with no unlisted archive files. The closed Slurm log is preserved separately.
Archive SHA-256: `47040ea04bd6d9fb35f616c98f48ca2d1f47e4f8d2236ebe5400b1ab0f796445`.
The final preservation receipt supersedes the reducer's provisional inventory,
which was written while its own log and guard were still open. Scratch is retained.

## Recommended next step, not authorized by this result

Prepare an explicit **TF32-disabled precision policy**, applied before model work
in both arms and in every preflight, reload, calibration and eventual training
process. Record and verify its effective value, retain determinism and the current
tolerances, and bind the changed source hashes. Then seek a bounded compatibility/
calibration grant: full two-arm forward/backward/update/reload checks first,
paired calibration second, followed by the unchanged resource-headroom gate.
The full matrix stays blocked unless its required gates and authorization hold.

This diagnostic did not test direct-model GPU execution, gradients, optimizer
updates, reloads, training throughput or learning performance. Real-source semantic
prerequisites remain unresolved. No source access, covariance, publication adoption,
central/statistical pairing or Gate-6 action occurred or follows from the result.
