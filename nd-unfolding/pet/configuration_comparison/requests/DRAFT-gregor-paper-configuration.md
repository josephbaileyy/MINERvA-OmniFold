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

## R2 — the pretrained checkpoints

`load_pretrained_omnilearned` fetches `best_model_pretrain_{s,m}.pt` from
`https://portal.nersc.gov/cfs/m4567/checkpoints`. Those URLs time out for us, and
`gregorkrz/HyperScale` returns 404. Since the code downloads silently when the file is
absent, a reproduction attempt fails at runtime rather than at configuration time.

1. Could you share the two checkpoint files, or a path we can read under m4567?
2. Their **sha256**, so we can pin them.
3. What licence applies to the weights?

Without these, the pretrained arms are not runnable and we can only compare against your
from-scratch arm — which does not test the transfer claim your paper is about.

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

Neither affects anything we are measuring; they are just what we noticed while reading.
