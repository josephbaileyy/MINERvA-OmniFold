# The saved step-2 checkpoint is not the model that produced the artifact's weights, and the last-epoch weights were never saved at all

**Date:** 2026-08-07 · **Tool:** `nd-unfolding/pet/gate_ab_push_provenance.py` · **Job:** `56445441`
(GPU, 5m43s) + controls `56445569` · **Receipt:**
`nd-unfolding/pet/fullevent_nominal/GATE_AB_PUSH_PROVENANCE.json` · **Ledger:** BEN-043

> **This blocks full-event PET extraction.** `extract_fullevent_fps.py`'s
> `check_subsample_agreement` (`:347`, default `tol=1e-3`, called unconditionally at `:609`) will
> **fail closed** on the nominal artifact: the measured max relative deviation is **0.866**. The gate is
> correct to fire and its tolerance must not be raised. Until this is resolved no full-event cross
> section can be produced.

## 1. What was measured

Built as memo item 5's two gates, in front of the step-1 pull/push decomposition, on the theory that a
decomposition resting on an unverified reconstruction is worth less than no number at all.

| gate | result |
|---|---|
| **A1** rebuilt `imc` vs stored `mc_indices` | **bit-exact**, 0 differing rows of 2,000,000 |
| **A2** rebuilt loader `truth_norm_mean/std` vs contract | **bit-exact** |
| **B(ii)** stored push `== 1.0` off `pass_gen`, untoleranced | **72/72 exact** |
| **B(i)** checkpoint-rebuilt push vs stored, on `pass_gen` | **FAIL** — max rel dev `8.663e-01` vs tol `1e-6` |

B(i) deviation distribution over the 1,999,928 `pass_gen` rows:

    median 8.340e-03    p90 1.676e-01    p99 4.206e-01    p99.9 5.663e-01    max 8.663e-01

**Gate A passing is what makes this interpretable.** The subsample is the same rows and the input space
is the same normalization, so B(i) is not a wrong-subsample failure and not the re-derived-normalization
failure `check_subsample_agreement`'s own docstring names. Something else is different, and it is the
weights.

## 2. The signature: two similarly-calibrated but different networks

    stored   mean 0.895408   min 0.043231   max 3.918736
    rebuilt  mean 0.891266   min 0.043628   max 3.935960

    fold-forward ratio from stored push       0.746483   (== the artifact telemetry, to 6 dp)
    fold-forward ratio from the CHECKPOINT    0.746407
    R (required)                              1.124080

Per-event the two disagree by up to 87%; in aggregate they agree to **1.0e-4**. That is not a broken
reconstruction — a wrong architecture or a failed `load_weights` gives an untrained network, whose
aggregate would not land within 1e-4. It is the signature of two networks trained to the same global
calibration on the same data, differing in their per-event decision surface.

## 3. Why: the last-epoch weights were never written to disk

    omnifold.py:272-275   ModelCheckpoint(model_name, save_best_only=True, save_weights_only=True)
    omnifold.py:266-268   EarlyStopping(patience=self.patience, restore_best_weights=True)
    omnifold.py:128       self.patience = early_stop           (engine default 10)
    omnifold.py:219-220   new_weights[pass_gen] = reweight(...); self.weights_push = new_weights

With `epochs=8` a patience-10 `EarlyStopping` can never fire, and Keras 2.15 restores best weights only
inside the `wait >= patience` stop branch — `on_train_end` merely prints. So the model **in memory** at
`reweight` time carries the **last** epoch, while `ModelCheckpoint(save_best_only=True)` has written the
**best-val-loss** epoch. `train_fullevent_nominal.py:497` stores `of.weights_push`, i.e. the last-epoch
output. `inference_contract["step2_checkpoint"]` — what `extract_fullevent_fps.py:253` loads — is the
best-epoch file.

The nominal's own histories confirm the two are different epochs for every checkpoint that matters:

| history | `argmin(val_loss)` | epochs | best | last |
|---|---|---|---|---|
| `w_nominal/..._iter2_step2.pkl` | **4** | 8 | 0.757173 | 0.757917 |
| `w_nominal/..._iter2_step1.pkl` | **6** | 8 | 0.104840 | 0.107209 |
| `w_floor/..._iter2_step2.pkl` | **6** | 8 | 0.751026 | 0.752517 |
| `w_floor/..._iter2_step1.pkl` | **7** | 8 | 0.099829 | 0.104159 |

A val-loss gap of ~0.1% between best and last is exactly consistent with §2's "same calibration,
different per-event surface".

**The sharpest statement of the defect: the weights that produced the published artifact do not exist on
disk.** `--step2-checkpoint` lets a caller point the extractor at a different file, but there is no
last-epoch file to point it at — `save_best_only=True` never wrote one. So the artifact's `weights_push`
is, as of now, unreproducible from the repository's own products.

## 4. Controls — what would have to be true for this to be my error instead

Two knobs belong to the harness rather than the pipeline, and both are excluded by measurement rather
than by argument (job `56445569`, both off one loader build):

- **Batch size.** `RunStep2` reweights at `MultiFold.BATCH_SIZE = 512`; the harness defaults to 1000, and
  float32 batching is non-associative. `--batch-size-control 512` measures how much of the 0.866 that
  accounts for.
- **A second, independent training.** `--extra-artifact` repeats Gate B on the matched floor run, which
  shares this subsample bit-exactly. Two independently trained runs showing the same
  large-per-event / tiny-aggregate signature makes it structural rather than a one-off.

### Control 1 — float32 batching non-associativity: EXCLUDED

    checkpoint @ batch 1000  vs  checkpoint @ batch 512      max rel dev  2.901e-06
    checkpoint @ batch 512   vs  STORED                      max rel dev  8.663e-01

Batching accounts for **0.0003%** of the Gate B(i) deviation. And the nominal's B(i) numbers came back
**bit-identical** across the two jobs (`8.663474e-01`, median `8.340066e-03`), so GPU nondeterminism is
excluded for free as well — the measurement is deterministic.

### Control 2 — an independent training shows the same signature: CONFIRMED

The matched floor run (`pet_fullevent_floor_weights.npz`), which shares this subsample bit-exactly:

| | nominal | floor |
|---|---|---|
| B(ii) off-shell `== 1.0` | 72/72 exact | 72/72 exact |
| B(i) max rel dev | 8.663e-01 | 8.643e-01 |
| B(i) p90 | 1.676e-01 | 1.650e-01 |
| B(i) median | 8.340e-03 | 2.434e-02 |
| stored / rebuilt mean | 0.895408 / 0.891266 | 0.886779 / 0.873206 |
| aggregate rel gap | 4.63e-03 | 1.53e-02 |

Two independently trained runs, same signature: enormous per-event disagreement, small aggregate
disagreement, off-shell rows exactly pinned. **This is structural, not a one-off.**

An unplanned corroboration: the floor run has the **larger** best-vs-last val-loss gap
(`0.751026 → 0.752517`, +0.00149, against the nominal's +0.00074) and also the **larger** aggregate
deviation (1.53e-02 against 4.63e-03). The ordering is what the mechanism predicts. I am claiming the
direction only — two points do not establish proportionality, and the ratios (2.0x in val gap, 3.3x in
deviation) are not equal.

### What survives

| candidate explanation | status |
|---|---|
| wrong subsample | excluded — A1 bit-exact |
| re-derived / wrong input normalization | excluded — A2 bit-exact |
| wrong architecture, or `load_weights` loading nothing | excluded — aggregate agrees to 1e-4 |
| float32 batching non-associativity | excluded — Control 1, 2.9e-06 |
| GPU nondeterminism | excluded — bit-identical across jobs |
| a one-off in this training | excluded — Control 2, floor run reproduces it |
| **best-epoch checkpoint vs last-epoch in-memory model** | **the only survivor** |


## 5. What this does and does not mean

- **It does not invalidate the nominal's central value.** `weights_push` in the artifact is the output of
  the model that actually trained; `central_vector` was computed from it in the same process. The artifact
  is self-consistent. What is broken is *reproducing* it from disk, and any downstream consumer that
  rebuilds from the checkpoint instead.
- **It does not change the fold-forward failure.** Both models give 0.7465 against R = 1.1241, agreeing to
  1e-4, so the normalization failure is a property of the estimator and not of which epoch was saved. The
  memo's step-1 decomposition is still the right next question.
- **It does not tell us which epoch *should* be used.** Best-val-loss is arguably the better regularized
  estimator, and last-epoch is what the published numbers used. Choosing between them is an estimator
  definition change and Joseph's call, not a bookkeeping fix.
- **It is not fixed by raising `--subsample-agreement-tol`.** The deviation is real; the gate is doing its
  job. Raising it would let a cross section be built from a different network than the one the artifact
  and every receipt describe.

## 6. The options, and what each costs

1. **Save the last-epoch weights** (`save_best_only=False`, or an explicit save after `Unfold`). Makes the
   checkpoint match what the artifact used. Requires a re-run to produce a consistent product set
   (~6 h GPU for nominal + matched floor), and changes no estimator definition.
2. **Make best-epoch the estimator** — let `EarlyStopping` restore, or reweight from the checkpoint inside
   the driver. Arguably better statistically, but it *redefines the nominal estimator*, so it needs a
   gate re-issue and invalidates the current central value rather than merely re-deriving it.
3. **Extract with the best-epoch checkpoint and accept the difference**, documenting that the published
   weights and the extracted cross section come from different epochs. **Not recommended** — it makes the
   artifact's `weights_push`, its `central_vector`, and the cross section mutually inconsistent, which is
   precisely what `check_subsample_agreement` exists to prevent.

Recommendation: **(1)**. It is the only option that makes the products consistent without redefining the
estimator, and the re-run cost is already sunk in the sense that Gate-4 is red and the product is
non-quotable regardless.
