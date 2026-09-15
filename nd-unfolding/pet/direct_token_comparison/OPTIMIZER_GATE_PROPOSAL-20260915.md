# Proposed optimizer equivalence amendment — not active

The captured failure is in a parameter that cancels from attention's represented
function, while the same-gradient CPU/GPU optimizer check passes. A blanket
increase of the weight tolerance would obscure the distinction. No acceptance
criterion or scientific model has been changed by this proposal.

## Exact proposed gate

Keep all existing packing, feature, mask, membership, parameter-count, initial
weight equality, forward/loss/gradient, prediction, determinism and checkpoint
checks. Keep their `atol=1e-5, rtol=1e-4` and exact CPU criteria unchanged.

Before any cross-device numerical assertion, persist initial weights, parameter
names/order, inputs, both steps' gradients, Adam state and updated weights. Seed
reconstruction must execute the original construction/checkpoint sequence and
freeze its initial arrays once; the current diagnostic's build-all-first sequence
cannot serve as a historical reproduction bundle.

For both CPU-derived and GPU-derived gradient sequences, require two-step fresh
Adam replays on common initial weights and identical gradient operands on CPU/GPU
to pass the existing tolerance for every model weight and optimizer slot. Require
native-device replay to reproduce the instrumented weights exactly, and require
instrumentation parity with the unchanged native preflight execution. Fail on
missing tensors, nonfinite values, disconnected or forbidden masked gradients,
unexpected parameter inventories, or missing replay evidence.

Retain the raw post-update CPU/GPU weight comparison as a gate for **every
parameter except the single attention key bias** identified structurally by its
layer role and frozen `(4, 8)` shape, not by an arbitrary path substring or failed
coordinate. Continue to record that bias's raw discrepancies. For it, require
both gradient comparisons and both native weight trajectories to agree with
independent float64 Adam replays at the existing tolerance; require the common-
operand replay gate above and all unchanged model prediction checks. Its
exemption rests on exact softmax shift invariance, not on exceeding the observed
1.42e-5 discrepancy. Do not exclude query bias, other biases or optimizer slots,
and do not change training gradients, freeze parameters or alter Adam epsilon.

Validate the amendment with adversarial tests: non-key weight failures still
reject; a substituted key-bias identity/shape rejects; altered common operands,
optimizer slots, native replay, predictions, missing case or nonfinite evidence
reject. The current archive illustrates the proposed measurements but does not
constitute a full amended preflight or fresh-process reload PASS.

## Authority and execution

This is a change to a frozen acceptance rule, so it needs explicit approval
before activation. It is not covered by a diagnostic PASS. After approval,
implement and locally validate the gate, then perform one separately authorized
bounded GPU compatibility/calibration attempt on a clean bound revision. Prior
charges are at least 742 seconds and must be remeasured. Recalculate resource
headroom under the unchanged aggregate ceilings; do not reuse the old 395-second
budget arithmetic. Full-matrix continuation requires every unchanged remaining
scientific and resource gate, including successful fresh-process reload.

The alternative is to retain raw equality of this redundant coordinate as a
hard gate; then the present captured result remains a failure. Removing the
parameter or altering the optimizer would instead change the experimental model
and requires a separately specified comparison. No such change is proposed here.
