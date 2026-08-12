## The engine's "Last val loss" prints the FIRST epoch, not the last

`omnifold_nn/omnifold/omnifold.py:303` logs `hist.history['val_loss'][0]` under the label
`Last val loss`. Index 0 is **epoch 1**. Anyone judging convergence from the training log is reading the
first epoch of the fit.

Found 2026-08-06 by a fresh-context review of the D2 powered-closure FAIL (job 56381674), and it had
already done damage: two sessions independently proposed "the fit is optimization-limited, raise
`epochs`" without opening the history pickles. The pickles refute it -- step-2 train loss moves 3.2e-5
across 8 epochs in iteration 2, and that iteration's `val_loss` gets *worse* (0.829560 -> 0.829612, best
at epoch 1). A fit with no remaining gradient signal, mislabelled as a fit starved of steps.

Related, same file: `ModelCheckpoint(save_best_only=True)` (`:272-275`) writes **best-val** weights, while
`reweight` uses the **last-epoch in-memory** model. On-disk checkpoints are therefore not bit-identical to
what a run actually used -- calibrate before trusting an inference-only reproduction from them.

Fixing the label touches `omnifold.py`, which is hash-bound by the Gate-4 launch-code gate, so it must
ride a deliberate re-issue rather than a drive-by edit.

Extended 2026-08-07: the plateau is a property of **all six** trainings of `56381674`, not just iteration
2 (train loss moves 1.13e-3 across 8 epochs on the first, 3.0e-5 on the last; val argmin at {5,5,7,1,6,5}
of 8). Two consequences for anyone reading these logs. `EarlyStopping(patience=10)` **cannot fire** at
`epochs=8`, and Keras 2.15 restores best weights *only* inside its stop branch (`on_train_end` merely
prints) -- so every run on this campaign has used last-epoch weights, and the `ModelCheckpoint` mismatch
noted above is therefore the norm rather than an edge case. `ReduceLROnPlateau` is at `patience=1000`
(`:263-265`) and `get_optimizer` returns a bare Adam at a flat LR (`:376-380`, `num_steps` accepted and
unused), so no schedule ever engages either. Table and consequences:
`docs/orchestration/FINDING-20260807-d2-underfitting-probe.md` §1.

