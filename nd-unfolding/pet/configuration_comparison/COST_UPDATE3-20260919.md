# Conditional cost, revision 3: the 23.9× has one cause, and it is not his architecture

**CITABLE FOR:** the decomposition of the ported arm's training step on one A100 in
production precision, the identified cause of its cost and its memory, what three
rewrites are worth, and campaign costs projected from those measurements under a
stated budget.
**NOT CITABLE FOR:** any performance, recovery or adoption claim. PET remains method
development; nothing here touches publication adoption, covariance, systematics,
central values or Gate 6, and nothing discharges `OI-71`.

`COST_UPDATE2-20260919.md`'s **measurements** stand — the port did cost 23.9× our
incumbent per example. Its **diagnosis** and its **remedy list** are replaced.

---

## 1. What the training step is made of

His complete arm, 12 tokens, batch 512, float32, one A100-40GB (job 58564110):

| section | µs/example | share of the step |
|---|---:|---:|
| forward | 134.2 | 14 % |
| backward | 795.3 | 85 % |
| optimizer apply | 5.4 | 0.6 % |
| **full step** | **934.6** | |

The backward pass is **6.9× the forward**. A backward is normally about twice a
forward, and that excess factor is the entire gap: 934.6 µs against our incumbent's
38.97.

## 2. The cause, named by the allocator rather than inferred

Every dense projection in the port was written `tf.einsum("...i,oi->...o", x, weight)`
— 29 layers of it — because it reads like the mathematics and made the checkpoint
transfer a copy. Its **gradient** does not lower to two GEMMs. It materialises the
per-example outer product and reduces afterwards.

**58 of the 60 OOM tracebacks in that job are in `einsum_op_impl.h`**, at shapes that
are exactly that outer product:

| shape | elements | float32 | for a weight of |
|---|---:|---:|---|
| `[2048, 38, 256, 128]` | 2.55 G | 10.2 GB | 32,768 numbers |
| `[128, 128, 24576, 10]` | 4.03 G | 16.1 GB | 16,384 numbers |
| `[256, 128, 16896, 10]` | 5.54 G | 22.2 GB | 32,768 numbers |

The remaining two are in `matmul_op_impl.h`.

**So the cost and the memory are one defect, and it is a formulation defect in our
transcription** — not his architecture, not our engine's attention, and not the
optimizer. The port was still *his network*: P-1…P-6 held then and hold now. It was
his network written in a way that made TensorFlow build a tensor five orders of
magnitude larger than the weight it was differentiating.

## 3. What I had guessed, and why the wrong guess is in the record

`COST_UPDATE2` §3 named three candidates and recommended **fused attention**. That
was a guess, and it was wrong.

A first CPU decomposition then appeared to put **96 % of the step in
`apply_gradients`**, and I wrote that into a commit message before checking it. It
was an artifact of my own instrument: the backward section returned
`loss + 0.0 * gradient`, Grappler folded the multiply, the gradient subgraph became
dead code, and the backward's whole cost landed in the apply *by subtraction*. A
direct probe puts the apply of all 176 variables at **6.06 ms** against **4.71 ms**
for stock Keras Adam — **1.29×**, not a bottleneck.

The receipt now carries `folded_backward_control` beside the real section.
`folded_over_forward` measures **1.00** on the GPU, which is what makes the honest
section trustworthy: the trap is shown firing next to the measurement that avoids
it, rather than being a thing I remembered to avoid.

## 4. What the three rewrites are worth

Each keeps its pre-optimisation path switchable, so its cost and its numerical price
are separable.

| rewrite | exact? | effect |
|---|---|---|
| broadcast the neighbourhood centre instead of tiling it | **bitwise** | **nothing** |
| broadcast the local key mask instead of materialising the pair mask | **bitwise** | **nothing** |
| flatten → matmul → reshape instead of `einsum` | round-off, not bitwise | *see §5* |

The first two are reported *because* they are negative. They were the obvious reading
of "unfused attention and a materialised `(B×N, K, dim)`", they cost a job to test,
and at 12 tokens / batch 512 they moved the step from 934.6 to 935.5 µs/example and
peak memory from 16.9 to 16.9 GiB. A negative result that is not written down gets
re-attempted.

**The third is the only change to his network that is not bitwise**, and it is
labelled that way everywhere. It reassociates a contraction: relative deviation
1e-15 in float64 and 6.5e-7 in float32, i.e. single-digit ulps. It is held to
`port_checks.FORWARD_TOLERANCE`, the 1e-5 the port check has used against upstream
torch since before this rewrite existed and therefore not a limit chosen by looking
at these numbers.

## 5. What the fix is worth, measured

*(job 58565265 — filled below)*

## 6. Gradient accumulation: measured, and free

His own `--grad_accum_steps`, transcribed from `src/scripts/train.py:2593-2615`.

| cell | µs/example | peak | optimizer steps |
|---|---:|---:|---:|
| native batch 512, 12 tokens | 935.5 | 16.9 GiB | 1 per 512 |
| native batch 2048, 12 tokens | **OOM on 40 GB** | — | — |
| **virtual batch 2048 = 512 × 4** | **947.8** | **17.0 GiB** | **1 per 2048** |

**1.3 % overhead, and the cell that cannot run natively runs.** The clip still sees
the full batch's global norm, the schedule still advances once per optimizer step,
and `max_steps` is still counted in optimizer steps, so the recipe is unchanged —
that is measured in float64 in `test_recipe.Accumulation`, not argued.

## 7. The budget moved the wrong way, and it is not my number to soften

`n_data` was assumed equal to `n_mc`. The 5-D point-cloud OmniFold input product
records its data leg three independent ways — `n_data_expected`,
`data_alignment_gate.n_rows_extracted` (exact, 0 mismatches) and `weight_gate.n` —
all **4,091,707**, and the event-identity export's 4,119,797 raw data rows sits
0.7 % above it, which is the right direction and about the right size for a
selection.

That is **2.05× n_mc**, so one evaluation presents **193.8 M** examples rather than
153.6 M: a factor **1.2615** on every absolute GPU-hour figure below and on none of
the ratios. It is a *neighbouring product* — this campaign runs the fullevent schema,
whose data leg has never been dumped at scale — so it **narrows the caveat and does
not discharge it**, and `rows_per_fit` still refuses to default `n_data`.

## 8. Campaign cost

*(filled below)*

## 9. Spend

| job | purpose | GPU-h |
|---|---|---:|
| 58563735 | port profile, **cancelled at 2:53** — its backward section measured the forward | 0.048 |
| 58564110 | port profile, **cancelled at 24:49** once the decomposition and the accumulation cell had landed | 0.414 |
| 58565179 | superseded before it started; bundled before the variant it existed to add | 0.000 |
| 58565265 | port profile, all variants | *pending* |

Two cancellations, both mine, and both cheap relative to what they bought: the first
stopped a bad decomposition from becoming a receipt, the second stopped 80 minutes of
XLA cells at a commit whose successor measures the same thing better.
