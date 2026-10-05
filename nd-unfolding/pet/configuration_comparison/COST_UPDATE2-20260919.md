# Conditional cost, revision 2: the port is correct and not yet affordable

**CITABLE FOR:** framework-matched per-example throughput on one A100 in production
precision, and campaign costs projected from it under a stated budget.
**NOT CITABLE FOR:** any performance, recovery or adoption claim.

Supersedes `COST_UPDATE-20260919.md`, whose ≈170 GPU-h was measured **across
frameworks** and is now known to have been measuring the wrong thing for this
purpose.

---

## 1. The headline, stated first because it changes the plan

Both arms now run in **one framework** on one GPU, so the ratio is the architecture
and the recipe and nothing else. At the only training configuration that runs:

| | µs/example, train | µs/example, inference |
|---|---:|---:|
| our incumbent, 12 tokens, batch 512 | **38.97** | 18.15 |
| ported PET2, same cell | **929.84** | 134.86 |
| **ratio** | **23.9×** (25.3× at step 2) | **7.4×** |

The cross-framework measurement gave **2.70×**. So **the Keras port costs about
8.8× what his own PyTorch implementation of the same network costs.** The port is
his network — P-1…P-6 hold, gated on mutant controls — but it is not yet a viable
way to *run* his network.

**And every other training cell ran out of memory — on a 40 GB card.** Slurm
allocated an **A100-SXM4-40GB** for this job (`GPU-ed84aae5…`), not the 80 GB card
the earlier calibrations got. So the ported arm trains only at 12 tokens and batch
512 **on 40 GB**; whether the other cells fit in 80 GB is **unmeasured**, and I am
not going to assume either way:

| tokens | batch | ported training |
|---:|---:|---|
| 12 | 512 | runs |
| 12 | 2048 | **OOM** |
| 33 | 512 | **OOM** |
| 33 | 2048 | **OOM** |

Inference runs in all four. The completion configuration — 33 tokens, batch 2048 —
**cannot be trained by the port as written on a 40 GB card**, and re-running the
three missing training cells on an 80 GB card is the first thing to do; it is a
few GPU-minutes.

**The throughput finding does not depend on the card.** Both arms were timed on
the *same* GPU in the same job, so the 23.9× is a fair ratio whatever the card;
and our arm's absolute throughput here (38.97 µs/example) agrees to within 5 %
with the 80 GB measurement (37.12–38.24), so the card is not what makes the port
slow. Comparing this ratio against the cross-framework 2.70 does cross cards, and
the ported arm is more bandwidth-bound than our small PET, so **"about 8.8×"
carries that qualification** — but not enough of one to explain a factor of nine.

## 2. What that does to the campaign

At the corrected budget (153.6 M training and 50.4 M inference presentations per
evaluation) and the one measurable training cell:

| arm | fit | inference | per evaluation |
|---|---:|---:|---:|
| our incumbent | 1.66 | 0.25 | **1.92** |
| ported, degraded inputs | 39.67 | 1.89 | **41.56** |
| his complete arm | 40.06 | 1.90 | **41.97** |

| | per pair | 17 pairs | +25 % retries |
|---|---:|---:|---:|
| with his complete arm | 43.88 | 746 | **≈933 GPU-h** |

**That is over the 600-hour ceiling by 55 %, at the cheaper token count, and the
33-token configuration does not run at all.** The campaign as currently
implementable is not affordable, and I am not going to present a number that
pretends otherwise.

## 3. Why, and what would fix it

The port was written for **correctness**: explicit einsum attention with a single
packed `in_proj_weight`, an additive mask, and arithmetic written out rather than
delegated. That is what made checkpoint transfer a copy, made the float64 checks
possible, and caught `tf.nn.gelu` and Keras' AdamW. It also means **no fused
attention kernel** — PyTorch's `scaled_dot_product_attention` fuses what this
materialises, which is both the ~9× and the OOM, since the unfused path keeps
every intermediate alive for the tape.

The heavy path is specifically `LocalEmbeddingBlock`: it reshapes to
`(batch × tokens, K, dim)` and runs two attention blocks there, so at batch 2048
and 33 tokens the leading dimension is 67,584 before heads.

Three routes, and they are not equivalent:

| route | keeps the port checks? | keeps the recipe? | effort |
|---|---|---|---|
| **optimise the port** — fused attention where the mask allows, avoid the `(B×N)` materialisation | must **re-pass P-1…P-6**, which is the point of having them | yes | days, bounded, and the checks make it safe |
| **gradient accumulation** — batch 512 × accum 4 | yes | **yes**: same effective batch, same update count, so a repair not a recipe change | hours; fixes OOM, not the 8.8× |
| **run his arm in PyTorch** | port becomes unnecessary for the comparison | yes | requires OmniFold's two-step loop in torch |

**Recommendation: do the optimisation pass, with gradient accumulation as the
immediate unblock for memory, and re-run P-1…P-6 afterwards.** The port checks
exist exactly so that a performance rewrite can be shown not to have changed the
network; using them for that is what they are for.

## 4. What the previous number got wrong, and what it got right

≈170 GPU-h assumed his arm cost 3.55× ours per example. That was measured honestly
**across frameworks** and is the right figure for "how expensive is his
architecture", but the wrong one for "how expensive is our campaign", because our
campaign runs his architecture through *our* engine. The cross-framework ratio
answers a question about his network; the matched ratio answers the question about
our plan.

Still conditional, and unchanged by this measurement: `n_data`. The corrected
budget makes our arm's evaluation **1.92 GPU-h** against the feature contract's
independently measured **1.1–1.3 GPU-h** for a nominal train. Those still
disagree, so the absolute hours here carry that factor of uncertainty and the
**ratios do not**.

## 5. Spend

| job | purpose | GPU-h |
|---|---|---:|
| 58551348 | recalibration at the paper flags | 0.024 |
| 58551477 | native-batch repair timing | 0.027 |
| 58552592 | matched timing, **FAILED** on a fatal TF OOM at 4:49 | 0.081 |
| 58552755 | matched timing, per-cell isolated, 31/40 cells, A100-40GB | 0.55 |
| 58552758 | region census (CPU, 0:32) | — |
| **cumulative campaign** | | **≈16.9 of 600** |

One failed submission, and it produced the per-cell isolation and the OOM finding.

**Two cancellations before they started**, both mine: I submitted, then realised
the timing would not have noticed a NaN, and then that it priced the degraded arm
rather than the one we intend to run. No compute was spent on either. A third
mistake did cost something — I moved the deployed checkout while the CPU census
was PENDING, which is the exact failure I have been bitten by before; it was
caught and resubmitted before the HEAD check could fail it.
