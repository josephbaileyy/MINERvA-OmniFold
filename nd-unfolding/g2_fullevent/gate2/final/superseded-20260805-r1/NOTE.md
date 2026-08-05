# Gate-2 run r1 (job 56342333, 2026-08-05, PASS) -- superseded within the hour

A genuine PASS, archived only because its receipt pins loader
`4c3a001cb5b6a52a3e2a1f04be4aabe9ea4666b86ef550623508a56d049af0c4`, which the audit repairs in
2cef7e6 replaced with `57f33f87...`. The loader diff was confined to the `mc-only` branch and to
comments, so this target is almost certainly bit-identical to its replacement -- but "the change was
semantically inert" is the reasoning hash pins exist to reject, so the gate was re-run instead.

## What it established (all reproduced by the replacement run)

* `R = 1.1240802949941018`, denominator `sum(w_reco[pass_reco])` -- D1 in force.
* `R_if_reco_leg_used_w_truth = 1.103260884167167`;
  `R_shift_factor_vs_legacy_w_truth = 1.018870795770713`, matching the value measured directly off
  the dump to twelve digits by an independent code path.
* B-4 `resolved=True`, differing on all 20,573,521 `pass_reco` rows, gate did not block.
* `occupied_cells = 231` (15 pT x 18 p||) against the pre-fix degenerate 1/285 -- the units repair
  confirmed by the gate's own independent binned check rather than by inspection.
* `refinement_is_learned_production = True`, backend `u2d.refine_stay_positive`.

## Note on sizes

This target is 18,723,004 bytes -- byte-for-byte the same SIZE as the 2026-07-19 target it replaced,
with a completely different digest. Any provenance check that binds an array by size alone cannot
tell these two apart.
