# The training recipe, and what the checkpoint actually transfers

**CITABLE FOR:** the derived training budget and schedule, and a tensor-by-tensor
account of checkpoint compatibility derived from architecture shapes.
**NOT CITABLE FOR:** any claim that a transfer succeeded. **No checkpoint file has
been read; none is reachable.**

---

## 1. The recipe is derived, not copied

| element | his reference run | what we run | why |
|---|---|---|---|
| batch | 2048 | **2048**, unchanged | part of his configuration, and one of the things being compared |
| `max_steps` | 250,000 | **derived** | 250k is his dataset's step count. Copied into an OmniFold fit it would give his arm a different number of passes over our data than ours gets. |
| warmup | 1,000 steps | **derived, fraction preserved** | 1,000/250,000 is 0.4 % of a run. Held at 1,000 inside a derived fit it becomes a different schedule wearing the same number. |
| lr / wd | 1e-4 / 0.01 | unchanged | his |
| clipping | `clip_grad_norm_`, 1.0 | **torch's formula, not Keras'** | Keras divides by `max(norm, clip)`, torch by `norm + 1e-6`. They differ exactly at the threshold, which is where a clip fires or does not — measured at 3.7e-7 relative, systematic. |
| schedule shape | linear warmup, cosine | transcribed, including the two details that look like bugs | `lr_lambda(0) = 0`, so his very first update has a learning rate of exactly zero; and `progress` is unclamped above 1. Both are his behaviour. |

**The fairness axis is example presentations.** Both arms present the same number
per fit; his batch 2048 against our 512 then buys him **4× fewer optimizer steps**,
which is a consequence of his configuration and is preserved rather than corrected.

### 1.1 A 1.6× error the realized-policy recorder caught

The first version computed the budget as `epochs × train_frac × train_events`.
The exercise then planned **7** optimizer steps and the engine took **12**.

`MultiFold` concatenates *both classes* before training, so `NTRAIN` is
`mc.nmax + data.nmax` at step 1 and `2 × mc.nmax` at step 2
(`omnifold.py:131-132`), and `fit` runs `int(train_frac × NTRAIN // batch)` steps
per epoch (`:297`). The budget was the MC leg alone — **1.6× too small**.

Nothing that compared a plan against a plan could see this. It was found because
the recorder reads the optimizer's own counters afterwards and refuses to agree
with the intention by assumption.

**One consequence is unresolved and must not be papered over.** `--max-events`
subsamples `imc`, which indexes the **MC arrays only**; the measured leg keeps its
full inventory. So `n_data` is a property of the production input, not a setting.
Taking `n_data = n_mc` puts our arm's projected evaluation at roughly **1.9 GPU-h**,
*above* the feature contract's independently measured **1.1–1.3 GPU-h** for a
nominal train. **Both cannot be right.** Until `mc.nmax` and `data.nmax` are read
off a production run, every absolute GPU-hour is conditional and only the ratio is
reliable.

---

## 2. What the checkpoint transfers, tensor by tensor

Running the port on synthetic arrays of some width proves the code executes. It
establishes nothing about loading a pretrained tensor into it, because that is a
question about shapes.

**What the loader does** (`omnilearned/utils.py:38-56`): filters each of `body`,
`classifier_head`, `generator_head` against the target's `state_dict()`, dropping a
key when the name contains `"out."`, the target lacks it, or the shapes differ —
then loads with `strict=False`. **It prints and continues.** A mismatched
configuration does not fail; it silently trains from scratch exactly where it
matters most.

### 2.1 His complete arm — the configuration we intend to run

| bucket | tensors | parameters |
|---|---:|---:|
| transferred | 148 | **1,443,368** |
| absent in target (diffusion time embedding) | 6 | 66,049 |
| replaced (`classifier.out`) | 2 | 513 |

**100 % of the classifier-usable backbone transfers, and the input interface is
intact.** The 6 absent tensors are `MPFourier` and `time_embed`: diffusion
machinery the pretraining objective needs and a classifier-mode model does not
build at all. `classifier.out` is replaced twice over — by the loader's `out.`
rule and by the task, since his head regresses `E_avail` and ours emits one
reweighting logit. The 330,378-parameter `generator_head` is not loaded because
`mode="classifier"` builds no generator.

### 2.2 The degraded arm that runs today — and why the percentage lies

| bucket | tensors | parameters |
|---|---:|---:|
| transferred | 139 | 1,403,939 |
| **reinitialised** | **4** | **4,100** |
| absent in target | 11 | 101,378 |

**97.3 % of the usable backbone transfers, and the transfer is still broken.**

The four reinitialised tensors are 0.3 % of the parameters and 100 % of the input
interface:

| tensor | checkpoint | ours (step 1 / step 2) |
|---|---|---|
| `embed.mlp.fc1.weight` | (256, 4) | (256, 5) / (256, 8) |
| `embed.norm.weight` | (4,) | (5,) / (8,) |
| `local_physics.mlp.fc1.weight` | (256, 4) | (256, 5) / (256, 8) |
| `cond_embed.0.fc1.weight` | (128, 16) | (128, 13) / (128, 2) |

`PET_body` is a sequential stack. Those four layers produce the token
representation and the conditioning token that every pretrained block downstream
consumes. Reinitialise them and the 1.4 M parameters that *did* load are reading a
coordinate system they have never seen.

Also absent: `pid_embed` and the four `add_embed` tensors — 35,329 pretrained
parameters unused, and two input channels his architecture was designed around,
missing entirely.

**So a parameter-count fraction is the wrong metric for transfer damage, and this
is why the export is not a nice-to-have.** `checkpoint_transfer` reports an
`input_interface_intact` verdict for exactly this reason, and
`configuration_identity.require_his_complete_arm` refuses to let the degraded arm
be described as his configuration.

### 2.3 What cannot be checked without the file

`cond_dim`, `add_dim`, `pid_dim` and `input_dim` are properties of the
**pretraining** dataset, not of the fine-tuning one, and OmniLearned pretrained on
something else. If they differ from his MINERvA settings, the corresponding
tensors silently fail to load **in his runs too**. This is a question for Gregor
and it is in the draft.
