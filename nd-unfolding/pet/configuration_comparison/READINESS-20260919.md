# Readiness: implementation for the matched pretrained comparison

**CITABLE FOR:** what is implemented and tested, what each measurement is, and what
remains blocked.
**NOT CITABLE FOR:** any performance, recovery or adoption claim. PET remains method
development; nothing here touches publication adoption, covariance, systematics,
central values or Gate 6, and nothing discharges `OI-71`.

---

## 1. What is done

| item | evidence |
|---|---|
| **PET2-small Keras port** at the V1-paper setting | `pet2_keras_port.py`; 176 tensors, 2,758,702 parameters |
| **P-1…P-6** all hold; the receipt records **1,024 forward rows and 64 gradient rows** | `receipts/PORT_CHECKS-20260919.json` |
| **torch-faithful AdamW** | `torch_adamw.py`; matches `torch.optim.AdamW` to 4e-14 over 5 steps |
| **OI-125 fold-forward recorder** | `fold_forward_recorder.py`; end-of-run ratio recorded, not reconstructed |
| **OmniFold adapter**, both steps on the real engine | `receipts/OMNIFOLD_STEP_EXERCISE-20260919.json` |
| **cost re-measured** at the paper flags, with inference | `receipts/COST_RECALIBRATION-20260919.json`, job 58551348 |
| **33-token native-batch failure diagnosed** | same receipt; the action is a backend repair, not a batch change |
| **decision packet** | `DECISION_PACKET-20260919.md` (its eleven decisions are now one) |
| **training recipe**: equal-example budget, derived warmup/cosine, torch's clipping, realized-policy recording | `training_recipe.py`, `RECIPE_AND_TRANSFER-20260919.md` |
| **checkpoint transfer map**, tensor by tensor | `receipts/CHECKPOINT_TRANSFER-20260919.json` |
| **regional safeguard** on the `(pT, p‖)` cells, with `NO_SELECTION` on failure | `characterize_regions.py`, `selection_rule.regional_safeguard` |
| **configuration identity** enforced, not just documented | `configuration_identity.py` |
| **threshold policy** with every margin translated into misplaced truth mass | `threshold_translation.py`, `FREEZE_PROPOSAL-20260919.md` |
| **float32 limit** independent of the port | `port_checks.float32_verdict`, `KERAS_PATH_VALIDATION-20260919.md` |
| **requests ready, not sent** | `requests/DRAFT-agent-a-event-keys.md`, `requests/DRAFT-gregor-paper-configuration.md` |

190 tests pass. `ALL BINDINGS INTACT`.

## 2. The port checks, and what they caught

Three of the four defects found were mine, and the checks existed to find them.

| check | result | what it caught |
|---|---|---|
| P-1 | identical by name, shape, traversal order | — |
| P-2a float32, **unmodified** upstream (1,024 rows) | 3.7e-7 vs a 5.3e-7 limit taken from the REFERENCE's deviation alone | the old budget was `reference + ours`, which a float32 defect in the port would have WIDENED |
| P-2b float64 (1,024 rows) | 6.7e-16 vs a 1e-5 tolerance | `tf.nn.gelu(approximate=False)` is **not exact** — 4.1e-9 against torch, and the neighbourhood block divides by `sum(1e-9 + mask)`, carrying it to 1e-1 |
| P-3 gradients (64 rows) | 5.1e5× closer than a mutant port | upstream's hardcoded float32 in the neighbourhood denominator, which the port now reproduces deliberately |
| P-4 one AdamW step (64 rows) | 4.0e8× closer than stock Keras AdamW | **Keras' AdamW is not torch's**: epsilon inside the bias correction makes it 31.6× larger at step 1, moving every zero-initialised bias by 68 % of the update |
| P-5 masking (1,024 rows) | exactly 0; crowding begins only at coordinate magnitude ~1000 | the first two versions of the sweep measured nothing — one pushed pads further away, one probed a leak that masking makes impossible |
| P-6 | bitwise repeatable and reload-identical | — |

**Two findings are about upstream, not about the port.**

* `scaled_dot_product_attention` returns an **O(1) wrong answer** for a mask at
  lower precision than q/k/v. `layers.mask_outer` hardcodes `.float()`, so any
  float64 run of `PET2` is silently corrupted. float32, bf16 and fp16 are all
  unaffected, so **his runs and his AMP path are fine** — it only bites a
  double-precision reproduction, which is exactly what a port check is. P-2b
  declares a one-symbol repair and counts how often it fires.
* A query whose every key is masked: torch returns **zero**, a plain softmax
  returns NaN. The port NaN'd until it was fixed. This is reachable in production —
  the loader zeroes the event block of rows failing `pass_reco`, `PET2` zeroes every
  bias, so at the first training step `cond_embed(0)` is exactly 0 and an event with
  no recoil tokens has no unmasked key left.

**P-3 and P-4 are gated on mutant controls, not on tolerances.** Re-measuring a
floor until the check passes is how a port check becomes decorative. Round-off
floors are still measured three ways — row permutation, half-batch split, one-ulp
jitter — and reported; they corroborate, they do not decide.

## 3. Cost, updated twice — and the second time it changed the plan

See `COST_UPDATE2-20260919.md`. Two revisions today. The first fixed a model that
was wrong in two directions and gave **≈170 GPU-h**. The second measured both arms
**in one framework**, which is the question our campaign actually asks, and found
the Keras port costs **23.9×** our incumbent per example — about **8.8×** his own
PyTorch for the same network — with every training cell but one out of memory on
the 40 GB card allocated. That puts the campaign at **≈933 GPU-h against a 600
ceiling**.

The port is his network and is not yet a viable way to run it. The execution path
needs an optimisation pass, and P-1…P-6 are what make that pass safe.

## 4. What is blocked, and on whom

| id | blocker | owner | blocks |
|---|---|---|---|
| **R2** | `best_model_pretrain_{s,m}.pt`, sha256, licence, from CFS **m4567** | **Gregor** | the objective — and now explicitly the pretrained arm's **tuning and variance pilot**, not only its final runs |
| **R-1** | `ev_run`, `ev_subrun`, `ev_gate` on three trees | **Agent A** | the typed-object join |
| **R4** | authorization to read 21 typed branches at scale (A1 covers blob/prong **counts**, not values) | **Joseph** | the representation half |
| **U1–U11** | the scientific decisions in the packet | **Joseph** | freezing the design |

## 5. What is implemented but deliberately not done

* **his cosine schedule and clipping are now implemented**, with `max_steps`
  derived from the equal-example budget rather than copied. What is *not* fixed is
  the budget's absolute size, because `n_data` is a production quantity nobody has
  read yet.
* **the interaction blocks.** The port **refuses** `use_int`/`local_int` rather
  than guessing: their features are defined in LHC jet coordinates (eta, phi,
  log pT) and have no established mapping onto our token schema. The paper
  configuration does not use them, so nothing is lost — but inventing a mapping
  would have embedded a scientific choice inside a porting utility.
* **the k-NN tie census on real data.** Zero real-token coordinate ties in the
  synthetic fixture; ties make top-k ordering engine-defined, so this is a cheap
  CPU check to run before the comparison rather than a risk to carry.
* **no slide rebuild**, as instructed.

## 6. Smallest next authorization

Still **not compute**. It is ratification of U1–U11, and within that the one that
changes the most downstream work is **U3** — whether the scoring domain stays 1-D
`E_avail` or becomes 2-D. Everything else on the implementation side runs without
anyone's permission; everything else on the science side waits on R2.
