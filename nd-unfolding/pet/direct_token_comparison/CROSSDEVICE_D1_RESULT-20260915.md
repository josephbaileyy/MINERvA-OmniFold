# Cross-device diagnostic D1/D1b: result and the decision it forces

**CITABLE FOR:** the measured decomposition of job `58354898`'s failure, and the
measured token geometry of the frozen matrix's production fixture.
**NOT CITABLE FOR:** any learning, closure or compute-efficiency claim; any statement
that either routing is scientifically better or worse; any released gate change.

Executed under [the predeclared specification](CROSSDEVICE_DIAGNOSTIC_SPECIFICATION-20260915.md).
Receipts: [crossdevice-d1.json](local_validation/20260915-amended-failure/crossdevice-d1.json),
re-derivable with [diagnose_crossdevice.py](diagnose_crossdevice.py); the single-device
probe is [probe_padding_invariance.py](probe_padding_invariance.py). No GPU allocation
was used for any of it.

## Headline

**There is no code defect, and no implementation fix is available.** The divergence
is Adam amplifying ordinary float32 cross-device gradient rounding in a
small-gradient parameter. The rounding itself scales with the attention sequence
length, which is the defining property of the direct route rather than a bug.

**And the case that failed is a preflight stress fixture that the frozen learning
matrix never produces.** The production fixture has uniform multiplicity and zero
padding — the `nominal` geometry, which passed on GPU for both routes.

## What the branch rule returned, including where my own threshold was wrong

| case | branch | why |
|---|---|---|
| `nominal/pooled` | A | computation agrees |
| `nominal/direct` | A | computation agrees |
| `variable/pooled` | A | computation agrees |
| `variable/direct` | **B** | query-kernel gradient disagreement `4.30e-06` exceeded my predeclared `1e-6` |

**My Branch B threshold was miscalibrated, and its label is not supported.** I set
`1e-6` absolute on gradients. The gate's own criterion is `np.allclose(atol=1e-5,
rtol=1e-4)`, which scales with element magnitude — and under *that* criterion **zero
gradients fail, at either step**. So Branch B fired on a stricter rule of my own
making, while B's stated interpretation ("materially different computation... a
probable code defect") is contradicted by every subsequent measurement. I am
recording this rather than quietly re-deriving to Branch A, because the rule was
predeclared and it should be visible that the rule, not the code, was at fault.

The correct reading is Branch A's *mechanism* with a larger input: gradients agree at
the gate's tolerance, and Adam amplifies what remains.

## The measurements

### Adam amplification is the mechanism, and the pattern is unambiguous

`variable/direct`, from the preserved arrays:

| tensor | role | gradient diff | post-Adam weight diff | amplification | weight scale |
|---|---|---|---|---|---|
| `weight_18` | `typed_projection/kernel` | **1.34e-05** (largest) | **7.8e-08** (negligible) | ~0× | 0.355 |
| `weight_24` | `attention/query/kernel` | 4.30e-06 | **1.55e-04** (the failure) | **36×** | 0.308 |
| `weight_27` | `attention/key/bias` (exempt) | 1.53e-07 | 1.10e-04 | **716×** | 1.09e-04 |

The tensor with the **largest** gradient disagreement has **negligible** weight
disagreement, and the tensor with the **smallest** has the largest. That is exactly
Adam's signature: the step is `m̂ / (sqrt(v̂) + eps)`, so it is scale-free and gradient
noise is amplified by roughly `1 / |gradient|`. A logic error would not invert the
ordering this way. The already-approved key bias sits at the extreme of the same
curve — a near-zero parameter (scale `1.09e-04`) amplifying `716×`.

The divergence is also stable rather than growing: `weight_24` moves `1.443e-04` →
`1.549e-04` between steps 1 and 2, and its gradient difference `4.16e-06` →
`4.30e-06`.

### Adam itself is device-stable; the trajectories are re-derivable

- **Identical-operand replay**: replaying Adam from one frozen initial state with one
  origin's captured gradients on both devices agrees to **2.98e-08** — in every case,
  for every weight and every optimizer slot. The arithmetic is not the problem.
- **float64 bracketing holds in all four cases**: each native float32 trajectory is
  reproduced by a float64 replay driven by its own gradients, within the unchanged
  tolerance.
- **Same-device repeatability was already exact** (the preflight's `exact=True`
  repeated-trace check passed for both devices before the failure).
- **Predictions agree** at `8.34e-07` in the failing case — the same value as the
  passing `nominal/direct`. The forward pass is unaffected.

### The driver is attention sequence length, not padding

D1's correlation with token geometry conflated real objects and padded slots, so D1b
separated them on a single device: append masked slots, which must contribute nothing,
and recompute with the same weights.

| route | geometry natural → widened | gradients bitwise identical | worst gradient change |
|---|---|---|---|
| `pooled` | `[4, 3]` → `[4, 3]` | **yes** | **0** |
| `direct` | `[4, 96]` → `[4, 192]` | no | **1.19e-07** |

Doubling the padding changes direct's gradients by only `1.19e-07`, roughly **100×
smaller** than the `1.34e-05` cross-device difference. So padding handling is not the
driver, and the candidate fix F1 from the specification would buy nothing measurable.
F1 is therefore **withdrawn, not deferred** — the evidence says it targets the wrong
quantity. The pooled control being bitwise identical confirms the probe itself is sound.

What does track the divergence is the attention sequence length, holding the objects
fixed. Both rows below process the same 90-blob event:

| case | attention positions per row | worst gradient diff |
|---|---|---|
| `variable/pooled` | 3 | 1.33e-06 |
| `variable/direct` | 96 | 1.31e-05 |

Same input objects, same encoder work, ~10× the cross-device gradient rounding, from
attending over 96 positions instead of 3. Longer float32 reductions on different
CPU and GPU kernels diverge more. That is a property of the representation being
tested, not a defect in it — and it is emphatically **not** evidence that individual
tokens are scientifically worse.

## The fact that changes the decision: the frozen matrix has no padding

Measured directly from `run_typed_token_comparison.make_fixture`, which is what all 24
frozen jobs call:

| route | presence shape (8 rows) | positions | active | padded |
|---|---|---|---|---|
| `pooled` | `[8, 3]` | 24 | 24 | **0** |
| `direct` | `[8, 4]` | 32 | 32 | **0** |

Every event carries exactly one photon, one blob and two prongs, with every token mask
true. The production geometry is therefore the **`nominal`** case — which **passed the
GPU preflight for both routes** — and the learning matrix never constructs a
variable-multiplicity or padded batch at all. `select_inputs` rebases segments without
dropping objects, so minibatches keep the same uniform shape.

The amended preflight nonetheless requires all eight case/routing pairs, so a stress
geometry the experiment never runs is currently blocking the experiment.

## Why there is no implementation fix

Each candidate was considered against the requirement to preserve the intended
comparison:

- Zero padded positions after projection (F1): measured ceiling `1.19e-07`. Withdrawn.
- Shorten the attention sequence: that *is* the direct representation.
- Change reduction order or accumulate in higher precision on GPU only: makes the
  validated arithmetic differ from the arithmetic that trains, and TF32 is already off
  with determinism on.
- Raise the model to float64: changes the bound `precision_policy`, and would validate
  arithmetic the production run does not use.

So the remaining routes are all changes to acceptance criteria or scope, which the
grant reserves. **No GPU allocation was spent reaching this conclusion, and spending
one now would hit the same wall**, so nothing further is submitted pending the decision.

## Scope limits of this diagnostic

- Four cases is a small population, and the geometry relationship rests on four
  points plus one single-device manipulation. It is a consistent account, not a
  demonstrated scaling law.
- Two Adam steps are not training. Whether a `1.55e-04` weight difference after two
  steps grows, washes out, or is irrelevant over a 3-iteration, 5-epoch, one-million-row
  run is **not** measured here, and the paired design would make device noise
  common-mode to both arms in any case.
- Nothing here measures learning, closure or compute cost. Those come only from the
  matrix.
