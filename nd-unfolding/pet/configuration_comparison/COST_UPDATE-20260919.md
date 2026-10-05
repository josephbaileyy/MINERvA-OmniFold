# Cost of the complete pretrained comparison, re-measured at the paper configuration

**CITABLE FOR:** measured per-example throughput on one A100, the native-batch
diagnosis, and evaluation costs projected from them under a stated budget model.
**NOT CITABLE FOR:** any performance, recovery or adoption claim. Cost is cost; a
cheaper arm is not a better one.

Supersedes §3.2 of `ROUTE_TO_PRETRAINED_COMPARISON-20260918.md`, whose ≈207 GPU-h
was a conditional projection under a model that was wrong in two directions.

---

## 1. Why the previous number had to be redone

| defect | direction | size |
|---|---|---|
| his arm was built from `PET2`'s **class** defaults `use_int=True, local_int=True`; the V1-paper branches pass neither flag | **over**stated his cost — the interaction block is quadratic in token count | `r` 2.82 → 2.70 at 12 tokens, 4.30 → 4.18 at 33 |
| the projection was **fit-time only**; an evaluation also reweights every event every iteration and validates a fifth of every epoch | **under**stated both arms | +36 M forward presentations against 96 M trained |

Neither was a rounding issue in the sense that mattered: the first meant the ratio
was measured on a model we do not intend to run, and the second meant a whole
category of work was outside the model.

## 2. Measured, jobs 58551348 and 58551477, one NVIDIA A100-SXM4-80GB, both arms UUID-matched

Ours under `tensorflow 2.15.0`, his under `pytorch/2.6.0` with the upstream pinned
by source-tree digest `bd832627…`, `use_int=False, local_int=False`.

| tokens | ours µs/example | his µs/example (batch 512) | **r train** | r at his native 2048 | **r inference** |
|---:|---:|---:|---:|---:|---:|
| 12 | 38.24 | 103.42 | **2.70** | 2.45 | 1.88 |
| 33 | 56.07 | 234.59 | **4.18** | *see §3* | 2.44 |

**Run-to-run spread, from repeating the whole measurement in job 58551477:** `r` came
back 2.79 at 12 tokens and 4.15 at 33, against 2.70 and 4.18. So these ratios are
reproducible to about **3 % at 12 tokens and 1 % at 33**, and should be quoted to two
significant figures, not three. A single run's third digit is noise.

**`r` still grows with token count**, 2.70 → 4.18, so pricing the completion
configuration at our current 12-token cap would still understate it by about half.

**Inference is cheaper per example than training but not negligible in total**, and
its ratio is smaller than the training ratio — his architecture's relative penalty
is larger in the backward pass.

## 3. The 33-token native-batch failure: which action is needed

The question was whether his batch 2048 fails for a reason a **backend repair** can
fix, leaving his recipe intact, or whether it forces a **batch-size change**, which
alters his configuration and has to be declared as an adaptation.

| backend | 12 tokens @ 2048 | 33 tokens @ 2048 |
|---|---|---|
| default | runs | `CUDA error: invalid configuration argument` |
| memory-efficient | runs | same error |
| flash | `No available kernel` — flash does not support a non-null `attn_mask` | same |
| **math** | runs | **runs** |

Largest batch that runs at 33 tokens under the default backend: **1024**.

**The required action is a backend repair, and his recipe is preserved.** Forcing
the math SDPA kernel for his arm keeps batch 2048, `max_steps`, and the schedule
exactly as his job scripts set them. A batch-size change to 1024 would have doubled
his optimizer-step count at fixed example budget, which is a change to the thing
being compared.

**What the repair costs is a separate question, and the answer is not what I
expected.** The math backend materialises the full attention matrix rather than
fusing it, so I assumed it would be a penalty to be paid for keeping his recipe.
Measured, at 33 tokens it runs his native batch 2048 at **200.85 µs/example**,
against **234.59 µs/example** for the default kernel at the matched batch 512 —
about **14 % cheaper**, because the larger batch more than pays for the slower
kernel. Keeping his recipe is not a cost here; it is a saving.

`receipts/COST_RECALIBRATION2-20260919.json`,
`native_batch_diagnosis.repaired_native_throughput`.

## 4. Projected cost of one evaluation

Budget model, unchanged and stated: `niter` 3, 8 epochs, 2 M subsample, two fits
per iteration ⇒ **96 M training presentations**; plus `2 × niter` full reweight
passes and a `(1−0.8)/0.8` validation fraction ⇒ **36 M inference presentations**.

| tokens | ours | his | fit | inference | **arm pair** |
|---:|---:|---:|---:|---:|---:|
| 12 | 1.20 | 3.10 | 3.78 | 0.53 | **4.30** |
| **33** | **1.82** | **7.04** | 7.75 | 1.11 | **8.86** |

**A consistency check that was not available before.** Our arm's modelled
evaluation cost at 12 tokens is **1.20 GPU-h**, against the feature contract's
independently measured **1.1–1.3 GPU-h** for a nominal train. The model now
reproduces a number measured a different way, so the old ×1.24 overhead multiplier
is **not** applied on top — it would double-count what the inference leg now covers.
Residual work still outside the model — fixture build, normalization, serialization
— is small on this evidence, but "small on this evidence" is corroboration, not a
bound.

## 5. The complete pretrained comparison, at 33 tokens

Priced two ways, because his batch size is part of his configuration and the repair
makes both runnable. **The right one is the second**: batch 2048 is his recipe, and
§3 shows we can keep it.

| | matched batch 512 | **his native 2048 + math repair** |
|---|---:|---:|
| our fit | 1.51 | 1.51 |
| his fit | 6.26 | **5.36** |
| inference, both arms | 1.13 | 1.13 |
| **per arm pair** | 8.90 | **7.99** |
| `r` (train) | 4.15 | **3.55** |

| step | pairs | matched | **intended** |
|---|---:|---:|---:|
| tuning, 4 trials per arm | 4 | 35.6 | 32.0 |
| variance pilot, 4 paired seeds | 4 | 35.6 | 32.0 |
| controls (V2 fold-forward, V4, V5, V8, V9) | 1 | 8.9 | 8.0 |
| **final comparison, 8 paired seeds** | 8 | 71.2 | **63.9** |
| subtotal | 17 | 151.2 | 135.9 |
| retries at 25 % | | 37.8 | 34.0 |
| **total** | | ≈189 | **≈170 GPU-h** |

**Against the 600 GPU device-hour ceiling with ≈16.2 consumed, the complete
pretrained comparison costs ≈170 GPU-h at his intended batch and leaves ≈414 hours
of headroom.** Each further paired seed costs **8.0 GPU-h**, so 16 seeds would add
≈64 and still fit comfortably.

The ≈207 figure it replaces was not merely imprecise: it priced a model the paper
does not run, omitted a third of the work, and assumed his batch had to be reduced.

**This is a projection, and these are the conditions it holds under.**

* The headline number prices his **native batch under the math repair**, which is
  his recipe. The matched-batch column is kept because it is the like-for-like
  ratio — same batch, same tokens — and is the one that is not a batch artifact.
* It prices a **scratch** backbone. A pretrained checkpoint changes the initial
  weights, not the architecture, so per-step cost should carry over — an
  expectation from the architecture being identical, not a measurement.
* It is **device-matched and framework-unmatched**: ours is TensorFlow, his is
  PyTorch. The Keras port now exists, so a same-framework ratio is measurable and
  is the one the final costing should use.
* It excludes the checkpoints (unavailable), the typed-object export and the dump
  re-run (CPU).

## 6. Spend

| item | GPU-h |
|---|---|
| calibration 58527080 (2026-09-18) | 0.049 |
| recalibration 58551348 (00:01:25) | 0.024 |
| repair timing 58551477 (00:01:37) | 0.027 |
| **this milestone** | **0.051** |
| **cumulative campaign** | **≈16.2 of 600** |

Two GPU jobs, both COMPLETED, no failed submissions this milestone.
