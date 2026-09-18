# DRAFT — not sent. Questions for Gregor

**Status: DRAFT.** Nothing has been sent. Sending this is Joseph's call, and it should
probably come from Joseph rather than from an agent.

**Context to give Gregor:** we are evaluating whether to adopt your configuration for our
OmniFold PET estimator, as method development. We would rather compare against what you
actually published than against what we guessed from the repository.

---

## R1 — which commit and which model?

We have `gregorkrz/minerva-ml` at **`fc9a099d3c9c060f03cef293c294f9de4eb019cd`**
("small plotting fixes", 2026-07-20). There are no release tags, so we cannot tell
whether that commit produced arXiv:2604.12364.

From `plot_configs/V1Paper.json` we read the paper lineup as **OmniLearned-small**,
**OmniLearned-small-rw** and **OmniLearned-medium** (displayed "OL-medium-frozen"), with
Transformer-xsmall/small disabled. We had initially — and wrongly — taken the
`Transformer1` preset as your configuration.

1. Which commit corresponds to the paper?
2. Is that lineup right, and which of the three is the headline result?
3. `submit_train_jobs.py` gives batch 2048, `max_steps` 250k, lr 1e-4, weight decay 0.01,
   1000-step warmup then cosine, grad clip 1.0, and `--zero-cond-feature 2` on every arm.
   Are those the paper's settings?
4. **The interaction blocks.** `--ol-interaction` and `--ol-local-interaction` are
   `store_true` with `default=False`, and none of the `OLS`, `OLS_RW` or `OLM_FB`
   branches passes either, so we read the paper models as running with
   `use_int=False, local_int=False`. `PET2`'s own class defaults are `True`/`True`,
   and there is a separate `OLS_int` branch that switches them on. We have built our
   port to the flags-off reading — could you confirm it? It changes capacity by only
   0.14 %, but the interaction block is quadratic in token count, so it changes the
   cost comparison materially.
5. **Weight decay on norms and tokens.** `PET2.no_weight_decay()` returns
   `{"norm", "token"}`, and `train.py:2345` builds a single `AdamW` param group
   without consulting it, so those parameters are decayed. Was that intended? We
   are reproducing your optimizer exactly and would rather reproduce the decision
   than the accident.

## R2 — the pretrained checkpoints

`load_pretrained_omnilearned` fetches `best_model_pretrain_{s,m}.pt` from
`https://portal.nersc.gov/cfs/m4567/checkpoints`. Those URLs time out for us, and
`gregorkrz/HyperScale` returns 404. Since the code downloads silently when the file is
absent, a reproduction attempt fails at runtime rather than at configuration time.

**Exact deliverables, and what each unblocks:**

| deliverable | form | unblocks |
|---|---|---|
| `best_model_pretrain_s.pt` | the file, or a readable path under m4567 | the OmniLearned-small pretrained arm |
| `best_model_pretrain_m.pt` | same | the OmniLearned-medium frozen-backbone arm |
| sha256 of both | two hex strings | pinning them in our receipts; we will not run an unpinned checkpoint |
| licence for the weights | one line | whether we may use them at all |

**Dependency, stated plainly so the sequencing is visible:** these are not needed
only for the final runs. The pretrained arm's hyperparameter selection and its
seed-to-seed variance both have to be measured *on the pretrained arm*, because
fine-tuning a transferred representation is a different optimisation regime from
training from scratch and its seed spread is a property of the fixed starting
point. So the checkpoints gate tuning and the variance pilot as well.

Without them the pretrained arms are not runnable and we can only compare against
your from-scratch arm — which does not test the transfer claim your paper is about.

## R3 — the `E_avail` definition

We believe yours uses full charged-pion energy plus `K^±`, against our pion-kinetic-energy
definition, an offset of order 140 MeV per `π^±`. Could you confirm the exact definition
you regress? Any numeric comparison against your reported values needs it.

## Two things you may want from us

* Your PID embedding indexes `X[..., 4]` with 8 classes while padded rows are all-zero,
  so padding shares index 0 with the muon code. Your CLS-only readout and key-padding
  mask contain it, but it becomes live under any pooled readout.
* `preprocessing.py` counts charged-pion prongs for raw PID `{8, 9}` but the token map
  handles only 8, so a surviving PID-9 prong raises rather than getting a code.
* `layers.mask_outer` ends in `.float()`, so the additive attention mask is float32
  whatever the model dtype is. At float32 that matches and nothing happens. If
  anyone ever runs `PET2` in **float64**, PyTorch's
  `scaled_dot_product_attention` silently returns an O(1) wrong answer for a mask
  below the tensor precision — we measured 1.7 against a hand-rolled softmax over
  the same mask values. We hit it porting your model and checking it in double.
  float32, bfloat16 and float16 are all unaffected, so your runs and your AMP path
  are fine; it would only bite a double-precision reproduction.

None of these affects anything we are measuring; they are what we noticed while
reading.
