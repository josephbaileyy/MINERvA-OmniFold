# FINDING 2026-07-30 — `build_event_features` has no non-finite guard; a single NaN kills step 2

*Found by execution, not review: NCSA Delta job 20599606 died on it after 49m45s.*
*Status: CONFIRMED. Touches a Gate-2-bound file → fix is a receipt re-issue, not an edit.*
*Severity: latent today, blocking the moment the event block widens.*

## Claim

`fullevent_fps_dataloader.build_event_features` applies no non-finite handling to the continuous
event-feature block. The cloud path does (`_scale_clean` → `np.nan_to_num`, `:88-91`); the scalar
path does not. One non-finite value anywhere in a selected column therefore poisons that column's
normalization statistic, turns the **entire** column NaN for **every** row, and trains step 2 to
`Last val loss nan`.

## Evidence

`truth_scalars` col 3 (`q3`) carries **14 non-finite values among `pass_truth` rows** in a
400,000-row uniform subsample of `of_inputs_pc_fps_xps2.npz` (0.0035%; scales to **~1,700** in the
full 49,152,885-row inventory). Measured on Delta:

```
truth_scalars (over pass_truth: 399978 rows)
  col0 pt         min=0.001403  max=4.818   std=0.3755  nonfinite=0
  col1 pparallel  min=4.509e-05 max=87.62   std=4.241   nonfinite=0
  col2 eavail     min=0         max=85.08   std=3.389   nonfinite=0
  col3 q3         min=nan       max=nan     std=nan     nonfinite=14
reco_scalars col3 q3  min=0.0113 max=176.8  std=3.632   nonfinite=0
```

The mechanism is `:168-172`:

```python
rsub = reco_scalars[rmask][:, cols]; tsub = truth_scalars[tmask][:, cols]
tmu = tsub.mean(0); tsd = tsub.std(0) + 1e-6
event_truth = _event_block(truth_scalars, feature_names, (tmu, tsd)); event_truth[~tmask] = 0.0
```

`tsd`/`tmu` are NaN, so every row of that column is NaN after `_event_block` — including the
399,964 perfectly good rows. `_event_block` (`:136-144`) has no clip and no `nan_to_num`.

**Observed signature** (job 20599606, arm `q3` seed 101): step 1 trains normally at
`Last val loss 4.8119707107543945`, because the **reco** leg's `q3` is clean; step 2 then reports
`Last val loss nan` and the run exits 1. Step-1-fine / step-2-NaN is diagnostic of a truth-leg-only
non-finite, and is worth recognising directly — the error message names neither the column nor the
cause.

## Why the existing guards do not catch it

`assert_no_truth_leakage` (`:182-196`) asserts `event_reco` is **not** `allclose` to a truth block
built with the reco normalization. NaN compares unequal to everything, so the assertion **passes**.
The guard is designed to detect similarity, and NaN is maximally dissimilar. Nothing else inspects
the block for finiteness.

## Why production is not currently broken

The adopted schema is `DEFAULT_EVT_FEATURES = ("pt", "pparallel")` = cols 0,1, both of which are
clean on both legs. The defect is **latent** and becomes live the moment the event block widens —
which is exactly what `FULL_EVENT_FEATURE_CONTRACT.md:98-101` requires for the publication
estimator (`px,py,pz,E,phi`, charge, MINOS, vertex, view/timing). A new column arriving from the
full-event C++ dump with a single unset entry reproduces this immediately.

This matters for how the G2 extension is planned: the extension's cost is not only the dump and the
regeneration, it includes making the event-feature path fail *loudly* on non-finite input first.

## Recommended fix (Gate-2 re-issue, not an edit)

`fullevent_fps_dataloader.py` is bound by the Gate-2 canonical runtime receipt, so this rides the
`RESTORE-2026-08-03.md` Step 2 re-issue rather than being patched in place. Two changes:

1. **Fail closed, do not silently clean.** Compute the normalization over
   `finite & mask` rows and **raise** with the offending column name and count if any selected
   column has non-finite entries among in-mask rows. A `nan_to_num` here would be wrong: the cloud
   uses 0 as its pad/mask sentinel, but 0 in a z-scored event feature is the *block mean*, so
   quietly filling would place undefined events at the centre of the distribution and bias the
   conditioning rather than announce a bad dump.
2. **Assert finiteness in `assert_no_truth_leakage`** (or a sibling guard) so the existing
   step-1 gate cannot pass on an all-NaN block.

Add a regression test with one NaN in one truth column asserting the loader raises and names the
column.

## Interim handling in the unbound driver

`feature_rank_arms.median_fill_nonfinite` fills non-finite scalar entries with the finite in-mask
column median and reports the count. **Median fill, not row dropping**, because dropping rows would
change the row set and make already-completed arms incomparable — reintroducing the confound those
arms exist to remove. A median-filled row lands at z-score ≈ 0 after normalization, the same
neutral position the loader already gives `!pass` rows at `:171-172`. This is a workaround in an
unbound file for a methodology run, **not** a substitute for the fail-closed fix above, and it is
deliberately loud.

Note the fill touches col 3 only, so the `base` (cols 0,1) and `eavail` (cols 0,1,2) arms from job
20599606 are bit-unaffected and remain comparable with the arms from job 20601059 — which is why
only the four missing runs were re-executed rather than all nine.

## Open question worth one query at restore

Why does `truth_scalars` `q3` have non-finite entries at all when `reco_scalars` `q3` does not, and
`truth_scalars` `eavail` does not? `q3` is a derived three-momentum-transfer quantity, so a
division or a `sqrt` of a small negative is the likely origin upstream in the C++ dump. 14 rows in
400k is small enough to be a genuine edge case rather than a systematic failure, but it is an
upstream data defect independent of this loader bug, and the same rows should be checked in the
full-schema dump.
