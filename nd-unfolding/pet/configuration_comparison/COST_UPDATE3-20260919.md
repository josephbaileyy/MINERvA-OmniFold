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

His complete arm, 12 tokens, batch 512, one A100-40GB (job 58565265):

| | baseline | optimised | |
|---|---:|---:|---:|
| forward | 134.5 | **75.6** | 1.78× |
| backward | 795.7 | **315.8** | 2.52× |
| optimizer apply | 5.6 | 5.6 | — |
| **full step** | **935.5** | **396.7** | **2.36×** |
| peak device memory | 16.9 GiB | **12.6 GiB** | −25 % |
| inference | 134.1 | **75.5** | 1.78× |

Against our incumbent measured in the **same job on the same card**, the training
ratio falls from **27.3× to 11.6×** and inference from 7.6× to 4.3×.

The `broadcast` variant reproduces the negative result independently — 935.4
against baseline's 935.5, 16.9 GiB both, the same three OOM cells — so "the two
bitwise rewrites do nothing" is measured twice, not once.

### 5.1 Two cells are still out of memory, and one variant is discarded

**33 tokens still OOMs at batch 512** even with the fix: 12.6 GiB at 12 tokens does
not fit at 33 on a 40 GB card, and every 40 GB allocation this lane has been given
is the same physical A100-SXM4-40GB. `hbm80g` is an available Slurm constraint
(256 + 64 nodes) and the 33-token cells are measured there separately.

**Every XLA cell is discarded**, and the reason is worth stating plainly rather than
in a footnote. `_time` did not force a device read inside the timed region. GPU
execution is asynchronous; with hundreds of unfused ops the queue back-pressures and
the timing self-syncs — which is why the unfused numbers above stand, and this job's
baseline agrees with independently synced job 58552755 to **0.6 %**. A single fused
XLA kernel has no back-pressure, and the XLA forward cell reported **2.4
µs/example**, which is **41.1 TFLOPS on a card whose float32 peak without TF32 is
19.5**. That needed no second measurement to reject, only the hardware's limit.
`_time` now reads the value inside the timed region and a `sync_probe` bounds what
that read costs.

This is the second instrument defect this decomposition has produced, and the second
caught by a control rather than by care: the first made a backward pass look free,
this one made a forward pass look faster than the silicon.

## 5.2 On an 80 GB card, and with the timer repaired: XLA changes the answer

Job 58566629, an **A100-SXM4-80GB** (`--constraint=gpu&hbm80g`), with the device
sync inside the timed region. Our incumbent is measured in the same job and comes
out at 35.3 µs/example against the 40 GB card's 34.3 — 3 %, so the two cards are
comparable and the ratios below are in-job anyway.

| variant | tokens / batch | µs/example | peak | vs our incumbent |
|---|---|---:|---:|---:|
| baseline `einsum`, eager | 12 / 512 | 935.5 | 16.9 GiB | 27.3× |
| optimised, eager | 12 / 512 | 396.7 | 12.6 GiB | 11.6× |
| **`einsum` + XLA** | 12 / 512 | **218.9** | **2.1 GiB** | 6.2× |
| **optimised + XLA** | 12 / 512 | **156.6** | **2.1 GiB** | **4.4×** |
| optimised, eager | 33 / 512 | *killed* | — | — |
| optimised, eager | 33 / 2048 | **OOM on 80 GB** | — | — |
| **optimised + XLA** | 33 / 512 | **387.9** | **5.4 GiB** | 11.0× |
| **optimised + XLA** | **33 / 2048** | **377.7** | **21.7 GiB** | **10.7×** |

Three things follow, and the third is a decision rather than a measurement.

**XLA is the larger lever, and it is a compile flag.** On the unmodified port it is
worth **4.3×** (935.5 → 218.9); on top of the projection rewrite, **2.53×**
(396.7 → 156.6). It also collapses memory by **6×**, which is what makes the rest
possible.

**The intended configuration runs.** 33 tokens at his native batch 2048 trains at
377.7 µs/example in **21.7 GiB** — under XLA, eager cannot do it on 80 GB at all.
21.7 GiB is comfortably inside a 40 GB card, so the campaign does **not** need the
80 GB constraint and does **not** need gradient accumulation at this configuration.
That should be confirmed on a 40 GB card before anything is launched; it is an
inference from a peak counter, not a run.

**The projection rewrite is worth 1.40× on top of XLA, and it is the only change to
his network that is not bitwise.** `broadcast_xla` — the untouched `einsum` port
plus XLA — is 218.9 against the rewritten 156.6. So the bitwise-exact port is
available at a **40 % cost premium**, and that is a choice to be made rather than
one for me to make silently. §8 prices both.

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

Computed by `project_campaign.py` from the receipt, not by arithmetic in prose: 17
arm pairs from `COST_UPDATE-20260919.md` §4, plus 25 % retries, against the 600
GPU-hour ceiling. **At 12 tokens, batch 512:**

| arm state | per pair | campaign | with the 5-D product's data leg |
|---|---:|---:|---:|
| baseline (pre-optimisation) | 43.50 | **924** ✗ | **1,166** ✗ |
| optimised, native batch 512 | 19.69 | **418** ✓ | **528** ✓ |
| optimised, accumulated to his virtual 2048 | 20.23 | **430** ✓ | **542** ✓ |

**The optimisation moves the campaign from 2.2× over the ceiling to inside it**, and
it stays inside even under the larger data leg — with 58 hours of headroom in the
worst case, against ~17 already consumed.

### 8.1 At the intended configuration, with XLA

Our incumbent at its own cap and batch (12 tokens, 512) against his complete arm at
his (33 tokens, 2048), both measured in job 58566629:

| configuration | per pair | campaign | with the larger data leg |
|---|---:|---:|---:|
| **optimised + XLA, 33 / 2048 — the intended pair** | 20.41 | **434** ✓ | **547** ✓ |
| optimised + XLA, 33 / 512 | 20.87 | 444 ✓ | 560 ✓ |
| bitwise `einsum` port + XLA, 12 / 512 | 11.28 | 240 ✓ | 302 ✓ |
| optimised + XLA, 12 / 512 | 8.62 | 183 ✓ | 231 ✓ |

**The complete pretrained comparison at the configuration we actually intend to run
costs ≈434 GPU-h, or ≈547 under the larger data leg, against a 600-hour ceiling with
≈18 consumed.** It fits, and under the larger data leg it fits with about 35 hours
to spare — which is thin enough that the fullevent data leg should be read before
the final runs rather than after.

**The 12-token rows are not an alternative campaign**, they are the same measurement
at the cheaper token count, and they show what the cap costs: going from 12 to 33
tokens for his arm roughly doubles the campaign.

### 8.2 What is NOT in these numbers

* **XLA now HAS passed a port check**, which it had not when §8.1 was first
  written. `port_checks.py --jit` runs every check through
  `tf.function(jit_compile=True)`: P-1…P-6 all hold, no verdict moved, and **zero
  tensors exceed their own round-off floor**. The scope is narrow and stated in
  `KERAS_PATH_VALIDATION-20260919.md` — it validates XLA's *transformations* on the
  CPU backend, not XLA-GPU's *kernels*, and no float64 check available here can
  reach those.
* 21.7 GiB at 33 / 2048 is **inferred** to fit a 40 GB card from a peak counter on
  an 80 GB card. It has not been run there.
* The fullevent data leg is still unread; the 1.2615 factor comes from a
  neighbouring product.
* Fixture build, normalization and serialization are still outside the model, as
  `RESIDUAL_OVERHEAD_CAVEAT` has said since the first costing.

## 9. Spend

| job | purpose | GPU-h |
|---|---|---:|
| 58563735 | port profile, **cancelled at 2:53** — its backward section measured the forward | 0.048 |
| 58564110 | port profile, **cancelled at 24:49** once the decomposition and the accumulation cell had landed | 0.414 |
| 58565179 | superseded before it started; bundled before the variant it existed to add | 0.000 |
| 58565265 | port profile, all variants, **cancelled at 33:35** once the XLA cells were known to be untimed | 0.559 |
| 58566629 | the 33-token cells and XLA, on an **A100-SXM4-80GB**, with the timer repaired | 0.252 |
| **cumulative campaign** | | **≈18.2 of 600** |

Three cancellations, all mine, and all cheap relative to what they bought: the first
stopped a bad decomposition from becoming a receipt, the second stopped 80 minutes of
XLA cells at a commit whose successor measures the same thing better, the third
stopped a block of XLA cells that a broken timer had already made unusable. One
submission (58565179) was withdrawn before it started because I had bundled the
branch before making the edit it existed to test.

## 10. What I would do next, in order

1. **Run P-1…P-6 under `--jit`.** The 434 GPU-h figure is XLA's graph and the port
   checks have only ever seen the eager one. This is local, costs no allocation, and
   it is the difference between recommending XLA and assuming it.
2. **Confirm 33 / 2048 on a 40 GB card.** One cell, a few GPU-minutes. If it holds,
   the campaign needs neither the `hbm80g` constraint nor gradient accumulation.
3. **Decide the projection rewrite.** The bitwise-exact port costs 40 % more. That is
   a scientific preference about how much exactness is worth, not an engineering
   call, and §5.2 prices it.
4. **Read the fullevent data leg.** 547 against 600 is thin enough that the factor
   should be measured rather than inherited from a neighbouring product.
