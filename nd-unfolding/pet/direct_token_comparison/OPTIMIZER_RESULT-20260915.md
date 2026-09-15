# Optimizer diagnostic: captured discrepancy explained, full preflight blocked

Authorized job `58320923`, clean standalone revision `98fde50e`, completed with
Slurm `COMPLETED / 0:0` in 216 seconds (219 conservative seconds including extern
cleanup). All eight model/case pairs completed. Instrumented weights and final
predictions exactly match the unchanged preflight on each device; same-device
repeated derivatives and same-device common-gradient Adam replays are exact.
No calibration, learning matrix, retry or additional GPU allocation ran.

## What the saved tensors establish

Only two of the 32 attention **key-bias** components in the masked/direct case
fail the unchanged raw-weight comparison (`atol=1e-5, rtol=1e-4`). All other model
weights, both steps' cross-device gradients and all final predictions pass.
The failing tensor's maximum difference is `1.417681050952524e-5`.
At its worst coordinate (flat index 12), first-step gradients are
`+1.280568540096283e-8` on CPU and `-7.916241884231567e-9` on GPU; second-step
gradients are `+1.210719347000122e-8` and `-1.8923511646562474e-9`.
The final weights are `-9.563364983478095e-6` and `+4.613445526047144e-6`.

Replaying each device's saved gradients through fresh Adam state on that same
device reproduces every updated weight exactly. Replaying **identical** gradient
operands across CPU/GPU passes everywhere; maximum model/slot discrepancy is
`2.9802322387695312e-8`. Independent float64 Adam propagation of the two native
gradient sequences predicts a difference of `1.4176931335738391e-5` at the failing
coordinate, within `1.21e-10` of the measured difference. Across the entire
capture, float64 replay comparisons pass with maximum discrepancy
`1.0784128612328914e-7`. These measurements attribute this captured failure to
Adam amplifying inherited tiny gradient differences, rather than a discrepancy
in Adam execution on common operands. The float64 calculation is a reference,
not a new optimizer or an adopted rounding-error budget.

For attention logits, adding key bias gives
`q_i dot (k_j + b) = q_i dot k_j + q_i dot b`.
The added term is common to every allowed key for a query, so softmax cancels
it in exact arithmetic. Thus this bias is a redundant parameter of the represented
function; a nonzero computed gradient can be a floating-point cancellation
residual. This algebra applies to the shared finite-key masked attention operation,
and does not imply every small gradient in the network may be ignored.
A separate local CPU check restored each saved CPU/GPU weight set and replaced
only this key bias with zero or 0.125. All 32 checks pass, maximum prediction
change `6.556510925292969e-7`. Native CPU/GPU final prediction differences in
the GPU capture also all pass, maximum `7.748603820800781e-7`.

[Tensor analysis](execution_runs/20260915-optimizer/analysis.json),
[CPU invariance measurements](execution_runs/20260915-optimizer/key-bias-invariance.json)
and the archived raw arrays bind these statements. No model parameter has been
removed, frozen, zeroed in production, or excluded from the current gate.

## Historical reproduction limitation

The earlier `58301971` variable/pooled failure did **not** recur here. Its failing
weights were never saved. This diagnostic builds all initial model pairs before
additional diagnostic operations; the original preflight interleaves construction
with checkpoint save/reload. A local observation of the original full sequence
shows that its initial weights agree with the diagnostic only for the first
nominal/pooled pair; the following seven pairs differ. Consequently, matching
seed 1701 and model-build order does not reproduce the complete historical RNG
sequence. The preparation's reconstructed-seed wording must not be read as
historical weight equality. This captured masked/direct mechanism is established;
the exact cause of the historical variable/pooled failure remains unverified.
[Initialization sequence measurements](execution_runs/20260915-optimizer/seed-sequence-comparison.json)
and [archived guarded CPU checks](execution_runs/20260915-optimizer/local-followup-verification.json)
record this distinction. The archived nominal and variable input fixtures match
the prior failed run exactly; diagnostic CPU/GPU initial weights match each other
for all eight pairs. A future exact reproduction must first capture weights from the unchanged complete
initialization/checkpoint sequence, then use that fixed bundle for all devices.

## Integrity, accounting and next decision

All 284 closed output files (41,260,480 bytes) match CFS, archive and local member
readback. The capture receipt's hashes match, the import guard reports zero
outside-checkout repository origins and no violation, and the execution checkout
remains clean. Archive SHA-256:
`0c1d0944f970ba1d00c5eb55c6fc21923f18ae3d21dae867997ada7fa1db2337`.
CFS payload: `/global/cfs/cdirs/m3246/josephrb/pet-routing-comparison/20260915-optimizer-58320923/payload`.
[Preservation inventory](execution_runs/20260915-optimizer/preservation.json),
[local readback](execution_runs/20260915-optimizer/local-readback.json),
and [scheduler accounting](execution_runs/20260915-optimizer/terminal-accounting.txt).

The batch reserved one A100, 32 CPUs, 56 GiB and at most 20 minutes; peak RSS was
2,440,848 KiB and measured batch CPU time 188.342 seconds. All six allocations
now total **742 conservative seconds = 0.206111 GPU-hours / 6.595556 reserved
CPU-hours**, before separate preparation/accounting CPU. CFS preservation used
6.202106 CPU-seconds. The grant is consumed and no automatic retry follows.

[The concrete gate amendment](OPTIMIZER_GATE_PROPOSAL-20260915.md) is proposed,
not active. It separates common-operand optimizer correctness from differences
between trajectories, and treats the exact redundant key bias explicitly. It
requires a decision because the standing campaign freezes acceptance criteria;
a successful diagnostic cannot waive that rule. The existing preflight remains
blocked, tolerances unchanged. No learning-performance winner, real-source
normalization/training, publication adoption, covariance or Gate-6 conclusion follows.
