# R2 is closed: the pretrained checkpoint was never unavailable

**CITABLE FOR:** the location, hashes and real tensor inventory of Gregor's
pretrained checkpoints, and what the reference loading policy does with the one we
intend to use.
**NOT CITABLE FOR:** any performance, recovery or adoption claim, or for the licence
under which the weights may be used — that is still unanswered.

---

## 1. What was wrong, and where the error was

`gregor-external-artifacts` recorded the pretrained initializations as **verified
unavailable**: `gregorkrz/HyperScale` returns 404 and the `portal.nersc.gov`
checkpoint URLs "time out consistently". The second half is false, and the way it is
false matters — **the probe ran from the wrong network.**

From a Perlmutter login node, 2026-09-19:

```
$ curl -sSI https://portal.nersc.gov/cfs/m4567/checkpoints/best_model_pretrain_s.pt
HTTP/2 200
content-length: 34605223
last-modified: Tue, 28 Oct 2025 06:27:58 GMT
```

And the file is directly readable on CFS without the portal at all.
`/global/cfs/cdirs/m4567` is `drwxr-s--x vmikuni` — **not listable, but
traversable**, so `ls` on the project root fails while an exact path succeeds. A
probe that tried to list the directory would conclude "unavailable"; a probe that
stats the path finds the file. All three checkpoints are `-rwxr-xr-x`.

**R2 was never an external blocker.** It was a search that did not cover the place
the artifact was.

## 2. What is pinned

| file | bytes | sha256 |
|---|---:|---|
| `best_model_pretrain_s.pt` | 34,605,223 | `7e8331b0953303502fcc64461e8e2332a7582184c8e3592db2e27d752612b1bc` |
| `best_model_pretrain_m.pt` | 633,540,135 | `07560b947c42c5d166785e4055901f5f33d22e6de761cc7743e14d7a840238e5` |

Source `/global/cfs/cdirs/m4567/www/checkpoints/`, mtime 2025-10-27, copied to
`/pscratch/sd/j/josephrb/pet-checkpoints-20260919/`. `best_model_pretrain_l.pt`
(4.67 GB) also exists and is not needed.

## 3. The real inventory, and the one thing the code settles

`best_model_pretrain_s.pt` holds nine top-level keys:

| key | content |
|---|---|
| `body` | **152 tensors, 1,494,320 parameters** |
| `ema_body` | 152 tensors, same names — an EMA copy |
| `classifier_head` | 28 tensors, 1,422,551 |
| `generator_head`, `ema_generator` | 35 tensors each |
| `optimizer`, `sched`, `epoch` (1000), `loss` (5.6656) | training state |

**`ema_body` exists and the reference loader does not use it.**
`load_pretrained_omnilearned` reads `checkpoint["body"]`. That is a question the code
answers, so it is not one to ask him.

## 4. The reference loading policy, executed

`receipts/CHECKPOINT_TRANSFER_REAL-20260919.json` — his `_filter_partial_state` and
his `PET2`, at the configuration F1 pins, against the actual file.

| part | loaded | parameters |
|---|---|---|
| body | **139 / 148 tensors** | 1,421,223 / 1,443,368 = **98.47 %** |
| classifier | **26 / 28 tensors** | 1,314,821 / 1,315,334 = **99.96 %** |

**Dropped because our model has no such module** (10): `interaction.mlp.*` ×4,
`time_embed.*` ×4, `MPFourier.freqs`, `MPFourier.phases`. The pretraining ran with
interactions and a diffusion time embedding; the paper's fine-tuning configuration
has neither.

**Reinitialized** (9 body, 2 classifier), and the distinction that matters is
whether each is *his* design or *our* deviation:

| tensor | checkpoint | model | whose choice |
|---|---|---|---|
| `add_embed.0.fc1.weight` | [256, **4**] | [256, **5**] | **his** — pretraining used 4 auxiliary features, `--ol-num-add` defaults to **5** |
| `pid_embed.0.weight` | [**9**, 128] | [**8**, 128] | **his** — `--ol-pid-dim` defaults to **8** |
| `local_physics.mlp.fc1.weight` | [256, **7**] | [256, **4**] | **his** — pretraining ran `local_int=True`; the V1-paper flags are off, so the 3 interaction features vanish |
| `cond_embed.0.*` (6) | absent | — | **his** — pretraining had no conditioning; MINERvA fine-tuning adds 16 globals |
| `out.weight`, `out.bias` | [210, 512] | [1, 512] | **his** — `_filter_partial_state` excludes `out.` by name; 210 pretraining classes, 1 output here |

**Every reinitialized tensor is reinitialized by his own pipeline at his own
defaults.** None is a deviation we introduced, which is the question that mattered:
our arm inherits exactly what his fine-tuning inherits.

## 5. What is still open, and it is not the weights

* **Licence / usage terms.** The files are world-readable on a NERSC portal with no
  licence statement. That is not permission, and it is the one item that still needs
  an answer from Gregor or Vinicius Mikuni (who owns `m4567`).
* **Which commit is the paper's**, and the E_avail definition and preprocessing.
* Nothing here discharges `OI-71`, and PET remains method development.
