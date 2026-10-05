# Deterministic packing: one proposed smoke/calibration allocation

**PENDING APPROVAL — no allocation is authorized by this document.** The exception
for job 58198332 was consumed by failed retry 58201775. This requests exactly one
new attempt using the repair bound in `repair-manifest.json`; no automatic retry.
The [repair record](COMPATIBILITY_REPAIR-20260913.md) and exact
[patch](deterministic-packing.patch) are the review surface. The previous source
audit grant and both failed allocations remain exhausted and preserved.

## Prerequisites and executable sequence

1. Receive explicit approval of this proposal and its bound repair. Record that
   grant in a new authorization JSON derived from
   `compatibility-authorization.pending.json`; bind its bytes and this repair
   manifest. The two older authorization files cannot satisfy the new launcher.
2. Recheck canonical Perlmutter live-state freshness, scheduler, completed-job
   accounting, free storage, package pins and clean local/remote branch heads.
   Deploy a new isolated checkout at the approved repair revision. Do not change
   either failed attempt's execution checkout, runtime or preserved outputs.
   Require Linux Python 3.11 and the existing pinned runtime: TensorFlow 2.16.2,
   Keras 3.15.1, NumPy 1.26.4, SciPy 1.16.3, pytest 9.1.1; retain the full existing
   CUDA dependency lock. Guard every Python execution with `mnv_guarded_run.py`.
3. Submit **one A100 / 32 reserved Slurm CPUs / 56 GiB / 110 minutes**, no other
   simultaneous job during this allocation. The prepared launcher is
   `sbatch_compatibility_calibration.sh`; arguments are clean checkout, pinned
   runtime, new output directory, expected commit, new approval JSON, approval SHA.
   Scheduler test-only validation may precede submission after approval.
4. Within the first **20 minutes total**, run the 60-test / 10-subtest guarded CPU
   regression suite, then the GPU compatibility preflight and its fresh-process
   reload. Both models must construct, run forward, differentiate all parameters
   and floating inputs, and perform eager and traced Adam updates. Four cases per
   arm cover nominal, variable multiplicity (90 blobs), masked/disabled slots,
   and wholly empty typed collections. The full original CPU model is the oracle.
5. Only a complete hash-verified GPU PASS permits a **fresh separate calibration
   process, capped at 90 minutes**: unchanged 32,768 training / 8,192 test rows,
   seed 17, injected mode, one iteration, one epoch per fit, batch 1,024. It builds
   and trains both arms from the frozen seeds and writes the paired artifacts,
   timing profile and resource receipt. No smoke or failed-attempt weights enter
   calibration. Slurm's 110-minute total cap includes stage transitions/cleanup;
   the per-stage caps are not additive extensions of it.
6. After Slurm COMPLETED / ExitCode 0:0, verify all guard records (including the
   reload child), input/code hashes, paired initialization and closed artifact
   hashes. Evaluate `evaluate_calibration.py OUTPUT --allocation-seconds ACTUAL
   --prior-allocation-seconds 193 --output GATE.json`, increasing the prior charge
   if remeasurement requires it. Archive and read back every output, successful
   or partial. Calibration remains excluded from performance comparisons.

Approval of this proposal would reopen only this one smoke/calibration attempt
and the **already frozen synthetic full matrix conditional on its existing
integrity and 20% resource-headroom gates**. A successful smoke alone cannot
release that matrix. No resource or scientific criterion is relaxed. A failure
at any technical stage stops; no fourth allocation, replacement seed, runtime
change, relaxed tolerance or smaller campaign is covered.

## Resource bounds and measured accounting

The prior [terminal receipt](RETRY_RESULT-20260912.md) reports 190 parent-allocation
seconds (0.052778 GPU-hours / 1.688889 reserved CPU-hours). Use **193 seconds** for
budgeting, taking the longer overlapping cleanup step once: **0.053611 GPU-hours /
1.715556 reserved CPU-hours**. Do not sum overlapping Slurm steps. The most recent
named cluster footprint was **5.037973 GiB**, with its exclusions documented there;
remeasure before deployment and count the added checkout, receipts and durable copy.

| Reservation or bound | GPU-hours | Reserved CPU-hours |
|---|---:|---:|
| New smoke stage, at most 20 min | 0.333333 | 10.666667 |
| New calibration stage, at most 90 min | 1.500000 | 48.000000 |
| New allocation total, at most 110 min | **1.833333** | **58.666667** |
| Prior conservative charge + new allocation + all 24 full jobs at 12 h | **289.886944** | **9,276.382222** |
| Same total plus original 16 h preparation/accounting allowance | **289.886944** | **9,292.382222** |
| Unchanged aggregate ceilings | **290** | **9,296** |

Thus hard caps fit with 6.783333 GPU-minutes / 3.617778 CPU-hours of margin beyond
all maximum-duration allocations. This arithmetic is **not** the 20% gate: measured
extrapolations must separately pass every existing headroom criterion. The earlier
50–240 GPU-hour campaign planning range remains unbenchmarked; a complete paired
calibration is needed to replace it. At 32 CPUs that range is 1,600–7,680 reserved
CPU-hours, before the new allocation and prior charges. CPU reservation, application
CPU consumption and elapsed wall time will be reported separately.

Storage stays at ≤4 GiB per job, ≤100 GiB working footprint and ≤200 GiB including
the verified durable copy. Meter output at least every 30 seconds and aggregate
new storage before each submission/copy. Slurm enforces memory and time. The
prepared launcher cancels its whole allocation if output exceeds 4 GiB. No source
copies are permitted. Preserve failed artifacts and receipts, never overwrite them.

## Unchanged scientific matrix, gates and limits

The original `run-card.json` SHA-256 remains
`567e3eabe16b7c3fc79f597621880f882783d4caca00dff1beb54462b6f96284`.
If calibration passes, run all **24 paired jobs**: ordinary/injected/shuffle ×
seeds **17, 29, 43, 59, 71, 89, 101, 113**; each uses the same **1,000,000 train /
250,000 test rows**, three iterations, two steps, five epochs per fit and batch
1,024. Maximum two full jobs concurrently, each ≤12 h on the same allocation
profile. Preserve event/features/masks/selection/weights/truth, parameter arrays,
normalization and minibatch ordering. No pretraining, membership or framework
contrast is added. Only the bound deterministic packing compatibility patch
supersedes the original model source bytes.

The full [original acceptance criteria](EXECUTION_PROPOSAL.md#acceptance-and-statistical-precision)
remain operative: complete matrix; injected paired improvement ≥7/8 favorable
seeds with the two-sided 95% mean-improvement interval wholly above 5%; D RMSE
≤0.10 in every seed; ordinary/shuffle normalization within 2% and RMSE ≤0.10,
D deterioration ≤0.02; prescribed global/tail ESS ratios ≥0.90 and target ESS
agreement, projected closure and tail/cap-sensitivity bounds. All denominators,
iteration trajectories and failures must be reported. Scientific failure does not
suppress other declared seeds. Any technical failure cancels remaining work.

The additional compatibility gate demands **exact** integer boundaries, stored
slot order, masks, packing VJPs, copied initial arrays and repeated same-device
outputs/gradients. CPU old/new model equivalence must be exact. GPU versus CPU
floating outputs/gradients/updated weights use predeclared **atol 1e-5, rtol 1e-4**;
these allow float32 backend rounding, not scientific endpoint changes. Nonfinite
or disconnected gradients fail, masked input gradients must be zero, every model
must perform two optimizer updates and pass same-process and fresh-process reload.
A tolerance failure stops without post-hoc widening. The original 20% time, CPU,
host-memory and storage gates, provenance checks, loss/weight finiteness, absolute
log-odds ≤50, OOM and source-access stops remain unchanged.

No outcome authorizes real-source reads, source normalization, real-data training,
publication adoption, covariance construction or Gate 6. Exact release, four
object-family semantics and the five prong-time observations remain unresolved;
resolve them before any dependent real-data experiment. Synthetic compatibility
is not synthetic learning superiority, and neither establishes real-data
representation performance. Both failed allocations and their partial pooled
outputs remain excluded from every learning-performance comparison.
