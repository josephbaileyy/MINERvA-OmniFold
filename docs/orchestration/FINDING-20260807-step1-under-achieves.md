# Step 1 genuinely under-achieves: the pull weight misses R by 32%, and iteration 2's step 1 is where it goes wrong

**Date:** 2026-08-07 · **Tool:** `nd-unfolding/pet/step1_pull_push_decomposition.py` · **Job:** `56445667`
(GPU, 4m38s) · **Receipt:** `nd-unfolding/pet/fullevent_nominal/STEP1_DECOMPOSITION.json` ·
**Verdict:** `STEP1_UNDER_ACHIEVES` · **Cross-stream:** CLM-010 (i)

This answers memo item 5. The reading was predeclared in code before the arm ran (BEN-038), and the
**second** branch fired — not the one I expected from the leg-mismatch result.

## 1. The measurement

`R = 1.1240802949941018`. All means are reco-leg-weighted over `pass_reco`, on the artifact's own
normalization, which is the functional step 1 is fitted to.

| quantity | `mean_w_reco \| pass_reco` | dev vs R | `mean_w_truth \| pass_gen` |
|---|---|---|---|
| `push_stored` (the run's own weights) | 0.746483 | −0.3359 | 0.888234 |
| `push_final` (model2 @ iter2) | 0.746407 | −0.3360 | 0.884253 |
| **`pull_final`** (what step 1 normalizes) | **0.765031** | **−0.3194** | 0.934530 |
| `push_prev` (model2 @ iter1) | 0.936383 | −0.1670 | 1.006938 |
| `increment1` (classifier1 @ iter2 alone) | 0.751119 | −0.3318 | 0.894941 |

## 2. What it means: step 1 is the failure, not the leg choice

Step 1 trains data against reco MC with MC weights `weights_push * mc_weight_reco * pass_reco` and data
weights `data.weight * data.pass_reco` (`omnifold.py:189-190`). The loader normalizes the MC side to 1e6
and the target to `1e6 * R`. So a step 1 that achieved what it is fitted to would satisfy

    mean_w_reco(pull_final | pass_reco) == R

exactly — this is not an identity imported from elsewhere, it is step 1's own objective. It measures
**0.765031 against 1.124080**, i.e. step 1 delivers only **68.1%** of the reweighting it is asked for.

**So the fold-forward failure is not an artifact of reading a step-2 quantity against a reco-leg
identity.** `leg_mismatch.py` had shown the leg accounts for ~19% (truth-leg 0.888 vs reco-leg 0.746), and
the open question was whether the remainder was step 1 or step 2 transport. It is step 1: the quantity step
1 itself normalizes misses its own target by 32%.

## 3. Where in the iteration it goes wrong — and it is not monotone convergence

Tracing the chain (`omnifold.py:200`: `weights_pull = weights_push * new_weights`, with `weights_push`
being the *previous* iteration's):

    iter1 step2   push_prev    0.936383     dev −0.167
    iter2 step1   pull_final   0.765031     dev −0.319      <- largest single drop, and it is step 1's
    iter2 step2   push_final   0.746407     dev −0.336

**Step 1's final iteration moves the normalization further from R, not toward it** — 0.936 → 0.765. Step
2's final iteration then loses a further 0.765 → 0.746. Nothing in the sequence moves toward R.

Note the means do not simply multiply: `0.936383 × 0.751119 = 0.703` against a measured `pull_final` of
`0.765031`, so `push_prev` and `increment1` are positively correlated. The chain is stated as measured
values, not as a product.

**A second, independent signal in the truth-leg column.** Step 2 trains gen against gen with class totals
`sum(w)` and `sum(w * pull)` over `pass_gen`, so its output should reproduce
`mean_w_truth(pull | pass_gen)`:

- at iteration 1, `push_prev` gives **1.006938** — within 0.7% of 1.0, which is what a well-fitted step 2
  looks like when its two classes have nearly equal totals;
- at iteration 2, `push_final` gives **0.884253** where its target `pull_final` gives **0.934530** — step 2
  under-shoots its own target by **5.4%**.

So both steps lose, step 1 loses much more, and iteration 2 is where both go wrong.

## 4. The caveat, and how far it is bounded

Gate B(i) failed (`FINDING-20260807-checkpoint-is-not-the-trained-model.md`, BEN-043): the saved
checkpoints are not bit-faithful to the models that produced the stored weights, so every number here is a
**checkpoint-based reconstruction**. The harness refuses to run without Gate A and stamps
`reconstruction_is_checkpoint_based: true` into its receipt, so the caveat travels with the number.

**But the caveat is bounded by measurement rather than left open.** The one quantity that exists both ways
agrees to 1e-4:

    push_stored (the run's own)   0.746483
    push_final  (from checkpoint) 0.746407

So at the aggregate level this reconstruction tracks the run's own weights to ~1e-4, which is three orders
below the effect being reported (32%). Both legs are also reconstructed identically, so the *comparison*
is sound by construction. What cannot be claimed is that 0.765031 is bit-exactly the run's own
`pull_final` — only that it is the same quantity to within an error that is negligible against the finding.

One asymmetry worth stating: `push_prev` comes from `iter1_step2`, whose history has
`argmin(val_loss)` at epoch 8 of 8 (`BEST_IS_LAST=True`), so that checkpoint **is** faithful.
`increment1` comes from `iter2_step1`, whose argmin is epoch 6 of 8, so it is not. The 0.936 → 0.765 drop
therefore mixes one faithful and one unfaithful checkpoint, and is the number most exposed to the caveat.

## 5. What this does not establish

- It does not identify *why* step 1 under-achieves. **Two candidates are now excluded, both for free:**

  | candidate | status |
  |---|---|
  | F3 logit cap biting asymmetrically | **EXCLUDED by measurement.** `cap_saturation_frac = 0.0`; implied logits span `[-3.141, +1.366]` against a cap of `±30`. Nothing is near it. |
  | biased train/validation split | **EXCLUDED by code.** `data.take(N)/.skip(N)` (`omnifold.py:370-371`) is a *positional* split, which on an unshuffled `[MC; data]` concatenation would have made the validation set almost pure label-1. But `:341-345` shuffles the index and applies it to the concatenation first, so the split is random. |
  | reco-leg under-training / non-convergence | **open, and now the leading candidate.** A converged weighted-BCE classifier on classes with totals `1e6` and `1e6*R` has optimum `exp(logit) = w_1/w_0`, which *includes* the `R` factor — so a correctly converged step 1 would return `R` by construction. Missing it by 32% is a convergence statement. |
  | `pass_reco`-only update × acceptance | open (`omnifold.py:198-199`) |

  Worth noting as a pointer rather than a conclusion: the implied logit range is strongly **asymmetric**,
  reaching −3.14 downward but only +1.37 upward. Since `push = exp(logit)`, the estimator is far more
  willing to suppress than to enhance — consistent with a genuine downward bias rather than a clipping
  artifact, and consistent with the under-achievement being in the direction it is.

- **No budget ladder has ever been run against the fold-forward ratio.** The ep8/ep16/ep32 ladder varied
  the *closure* driver's budget and was read on D2 recovery. If Joseph takes option (1) in
  `FINDING-20260807-checkpoint-is-not-the-trained-model.md` §6, that re-run can carry a higher-epoch arm and
  answer the convergence question in the same GPU spend, since both need a nominal re-train anyway.
- It does not contradict the acceptance-dilution picture for D2. That is a different criterion on a
  different quantity; this is the reco-space normalization.
- It does not license a repair. The step-1 diagnosis is now specific enough to act on, but which action
  depends on Joseph's answer on the checkpoint options, since any re-run lands both.

---

## 7. RE-MEASURED 2026-08-08 ON BIT-FAITHFUL CHECKPOINTS — the caveat is gone, and step 2 is EXONERATED

The §4 caveat is retired. Job `56445883` re-trained under the BEN-043 fix, Gate B(i) is **bit-exact**
(`max_rel_dev 0.0`, `GATE_AB_PASSED`), and the harness now records
`reconstruction_is_checkpoint_based: false`. Per-step batch sizes corrected to the engine's own values
(step 1 → 1000 per `omnifold.py:199`, step 2 → 512 per `:219`; BEN-072), and the last iteration's
`*_final.weights.h5` used where the driver wrote them.

**The internal check that says the reconstruction is faithful:**

    push_stored   0.736746        <- the run's own weights, straight from the artifact
    push_final    0.736746        <- reconstructed from the checkpoint
                  IDENTICAL to all printed digits

On the superseded artifact these differed (`0.746483` vs `0.746407`). They no longer do, so every number
below is the run's own, not a reconstruction of it.

| quantity | `mean_w_reco \| pass_reco` | dev vs R | `mean_w_truth \| pass_gen` |
|---|---|---|---|
| `push_stored` | 0.736746 | −0.3446 | 0.876675 |
| `push_final` | 0.736746 | −0.3446 | 0.876675 |
| **`pull_final`** (what step 1 normalises) | **0.658944** | **−0.4138** | 0.880522 |
| `push_prev` (model2 @ iter1) | 0.967659 | −0.1392 | 1.010853 |
| `increment1` (classifier1 @ iter2) | 0.648331 | −0.4232 | 0.851573 |

### Step 1 delivers 58.6% of its own objective

`mean_w_reco(pull_final | pass_reco) = 0.658944` against `R = 1.124080`. That comparison is step 1's own
fitted objective, so the verdict `STEP1_UNDER_ACHIEVES` stands and is sharper than the 68.1% the earlier,
unfaithful reconstruction of a *different* run suggested. (The two runs are not directly comparable
piece-by-piece — different weights throughout — which is why the conclusion, not the individual numbers,
is what carries across.)

### Step 2 is exonerated, and that is the new information

Step 2 trains gen-vs-gen with class totals `sum(w)` and `sum(w·pull)` over `pass_gen`, so it should
reproduce `mean_w_truth(pull | pass_gen)`:

    target  pull_final truth-leg   0.880522
    achieved push_final truth-leg  0.876675      undershoot 0.44%
    and at iteration 1, push_prev truth-leg = 1.010853  -- within 1.1% of 1.0

**A 0.44% undershoot is step 2 doing its job.** On the superseded run this read 5.4% and step 2 looked
partly implicated; on faithful checkpoints it is not. The failure is squarely step 1's.

### The chain is NOT monotone, and step 2 partially RECOVERS

    iter1 step2   push_prev    0.967659    dev −0.139
    iter2 step1   pull_final   0.658944    dev −0.414     <- step 1's increment, a collapse
    iter2 step2   push_final   0.736746    dev −0.345     <- step 2 claws some back

This inverts the earlier reading. On the superseded run the chain fell monotonically (0.936 → 0.765 →
0.746) and I described step 2 as losing a further increment. Here `push_prev` is only 13.9% below `R`, step
1's increment drops it to 41.4% below, and step 2 then *improves* it to 34.5% below.

### The sharpest statement: step 1's correction has the wrong SIGN

`increment1`'s reco-weighted mean is **0.648331**. To carry `push_prev`'s 0.967659 up to `R = 1.124080`
the increment needs to average ≈1.16. **Step 1 applies a ~35% reduction where a ~16% increase is
required** — the direction is wrong, not merely the magnitude. That is a much more specific defect than
"under-achieves", and it is the first time the sign has been established on weights that are provably the
run's own.

(Means do not multiply — `0.967659 × 0.648331 = 0.6275` against a measured `pull_final` of `0.658944`, so
`push_prev` and `increment1` are positively correlated. The chain above is measured values, not a product.)

### What this does and does not settle

- It **does** localise the failure to step 1's final-iteration increment, with step 2 exonerated at 0.44%.
- It **does not** explain why. The four candidates in §5 stand, with the F3 cap and the biased split still
  excluded; reco-leg non-convergence remains the leading one, and the wrong-sign finding is new evidence
  that bears on it — a non-converged classifier would be expected to *under*-correct toward 1, not to
  correct in the opposite direction.
- Receipt: `nd-unfolding/pet/fullevent_nominal/STEP1_DECOMPOSITION.slurm-56445883.json`.

---

## 8. DEFINITIVE TRAJECTORY 2026-08-09 — correct at iteration 0, degrades later

Job `56525829` measured every Step-1 increment on the BEN-043-corrected nominal and reproduced
`increment1`, `push_prev`, and `push_final` from the committed decomposition receipt **bit-exactly**.
The artifact verdict `CORRECT_AT_ITER0_DEGRADES_LATER` was independently re-derived:

| iteration | prior push | achieved r1 | required r1 | achieved/required | sign |
|---:|---:|---:|---:|---:|---|
| 0 | 1.000000 | **1.233512** | **1.124080** | **1.09735** | correct |
| 1 | 1.092736 | **0.915166** | **1.028684** | **0.88965** | wrong |
| 2 | 0.967659 | **0.648331** | **1.161650** | **0.55811** | wrong |

This retires the earlier ambiguity. At iteration 0 there is no feedback and Step 1 meets the
predeclared within-10% criterion with the correct sign. The sign flips only after feedback exists.
The failure is therefore in **iteration dynamics**, not a class-normalization/training defect already
present at push=1. Cap saturation is zero at every iteration.

The script's generic checkpoint caveat is also non-binding here. History minima for Step 1 iterations
0 and 1 are epoch 8/8, so their files named best-epoch are the actual last-epoch models. Iteration 2
uses the explicit BEN-043 final checkpoint. The complete Step-1 trajectory is last-epoch-faithful.

A static audit narrows the next split: `MultiFold.cache()` reuses feature tensors and the shuffled
index after iteration 0, but it rebuilds the label/weight dataset from the current arrays on every
call. Stale cached labels or weights are excluded. The distinct remaining mechanisms are (a) reuse of
the fixed train/test split/order and (b) warm-starting the Step-1 network across changing weighted
classification problems. They require controlled arms; this result does not choose between them.

Artifact: `nd-unfolding/pet/fullevent_nominal/STEP1_TRAJECTORY.slurm-56525829.json`, sha256
`032f548f1b7b85fe672d0e7bf640299a720d0d1ecca95bbad23c4037ca16e9bb`.
