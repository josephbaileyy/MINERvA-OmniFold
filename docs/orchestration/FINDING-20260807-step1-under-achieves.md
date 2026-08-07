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

- It does not identify *why* step 1 under-achieves. Candidates not tested here: the classifier is
  under-trained on the reco leg specifically (the budget ladder tested step 2's effect on D2, not this);
  the F3 logit cap is biting asymmetrically; the data/MC class imbalance at `R = 1.124` is being partly
  absorbed as a constant the classifier cannot express; or the `pass_reco`-only update
  (`omnifold.py:198-199`) interacts with the acceptance structure. `cap_saturation_frac` is in the
  artifact and is the cheapest of these to check next.
- It does not contradict the acceptance-dilution picture for D2. That is a different criterion on a
  different quantity; this is the reco-space normalization.
- It does not license a repair. The step-1 diagnosis is now specific enough to act on, but which action
  depends on Joseph's answer on the checkpoint options, since any re-run lands both.
