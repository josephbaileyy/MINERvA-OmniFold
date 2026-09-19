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

237 tests pass (re-measured 2026-09-19). `ALL BINDINGS INTACT`.

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

## 3. Cost: diagnosed, repaired, and now inside the ceiling

Three revisions. The first fixed a model that was wrong in two directions and gave
≈170 GPU-h. The second measured both arms **in one framework** — the question the
campaign actually asks — and found the port costing **23.9×** our incumbent, a
**≈933 GPU-h** campaign against a 600 ceiling, with every training cell but one out
of memory. The third, `COST_UPDATE3-20260919.md`, found out **why**, and the cause
was ours.

**One defect.** Every dense projection was written `tf.einsum("...i,oi->...o")`,
whose gradient materialises the per-example outer product instead of lowering to two
GEMMs. **58 of 60 OOM tracebacks** land in `einsum_op_impl.h`, at shapes up to
22.2 GB for a 32,768-number weight. The backward pass was 85 % of the step and 6.9×
the forward; the optimizer was 0.6 %.

| | µs/example | peak | campaign |
|---|---:|---:|---:|
| baseline, 12 tokens / 512 | 935.5 | 16.9 GiB | 924 ✗ |
| + projection rewrite | 396.7 | 12.6 GiB | 418 ✓ |
| + XLA | 156.6 | 2.1 GiB | 183 ✓ |
| **his intended 33 / 2048, optimised + XLA** | **377.7** | **21.7 GiB** | **434 ✓** |

**The complete pretrained comparison now costs ≈434 GPU-h at the configuration we
intend to run — ≈547 under the larger data leg — against 600 with ≈18 consumed.**
The two bitwise rewrites that looked obvious bought nothing, measured twice. XLA is
the larger lever and is a compile flag. Both the repaired and the bitwise-exact
paths fit; the latter costs 40 % more.

**The port survived every repair**: P-1…P-6 re-run after each rewrite and again
under XLA, all six holding every time, no verdict ever moving, and under XLA no
tensor exceeding its own round-off floor.

## 4. What is blocked, and on whom

| id | blocker | owner | blocks |
|---|---|---|---|
| **R2** | `best_model_pretrain_{s,m}.pt`, sha256, licence, from CFS **m4567** | **Gregor** | the objective — and now explicitly the pretrained arm's **tuning and variance pilot**, not only its final runs |
| ~~R-1~~ | ~~three event-key branches~~ | ~~Agent A~~ | **DELIVERED 2026-09-19**, verified 12/12, with the correction that the triple is a GATE key on `data` and the join needs `occurrence` |
| **R4** | authorization to read 21 typed branches at scale (A1 covers blob/prong **counts**, not values) | **Joseph** | the representation half |
| **T1** | ratification of the **single threshold policy** — `f = 0.80`, `δ = 0.02`, `δ_switch = 0.04`, regional floor 0.60 | **Joseph** | freezing the design |
| **T2** | **F10**: whether the execution path keeps the projection rewrite (round-off, not bitwise) or the bitwise-exact port at a **40 % premium**. Both fit the ceiling | **Joseph** | freezing the execution path |

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

Still **not compute**, and there is now a second small one beside the first. The eleven open decisions of `DECISION_PACKET-20260919.md`
were collapsed into **one** in `FREEZE_PROPOSAL-20260919.md` §2, and that single
threshold policy is the ask: `f = 0.80`, `δ = 0.02`, `δ_switch = 0.04`, regional
floor 0.60. Within it only **δ** is a genuine scientific judgement — it accepts
**0.27 % more truth mass in the wrong bin** to keep the incumbent, and it enters
the sample size as `1/δ²`. The scoring domain is no longer open: the 1-D `E_avail`
primary score stands, with the regional safeguard on the `(pT, p‖)` cells carrying
the protection that a 2-D score was being considered for.

Everything else on the implementation side runs without anyone's permission;
everything else on the science side waits on **R2**.

Two cheap things would also close real gaps and need nobody's permission: running
33 / 2048 once on a 40 GB card (the 21.7 GiB figure is inferred from a peak counter
on an 80 GB card), and reading the fullevent data leg, since 547 against 600 is thin
enough that the 1.2615 factor should be measured rather than inherited from a
neighbouring product.
