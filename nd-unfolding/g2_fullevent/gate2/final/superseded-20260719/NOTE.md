# Superseded Gate-2 products (published 2026-07-19, archived 2026-08-04)

Moved here, not deleted, so the 2026-07-19 target remains available and every record that names it
still resolves.

## Why they were superseded

Two independent reasons, both established 2026-08-04:

1. **The receipt's "independent binned check" was vacuous.** A stray `/1000.0` collapsed 231/285
   occupied bins into 1/285 while both guards reported success -- the domain check tests range
   membership and both grids start at 0.0, and the metrics scale both histograms identically, so they
   agreed while being equally wrong. Scale-invariance of sums and ratios is why it looked healthy.
2. **It predates the B-4 gate.** The PASS was obtained under a validator that wrote B-4 into a note
   whose own text said not to freeze R yet, while emitting `status: PASS`. Every consumer reads
   `status`, not a note.

## What changed in the re-issue

* **D1 (B-4).** Step 1 consumes `w_reco`, step 2 `w_truth`. R's denominator is
  `pot_scale*sum(w_reco[pass_reco])`, which moves R by +1.887% against these archived products.
  Measured: `w_reco` differs from `w_truth` on all 20,573,521 `pass_reco` rows, and the ratio is a
  reco-only MINOS efficiency factor in [0.931, 0.998].
* **D2.** The nominal now consumes the published target instead of silently rebuilding it (J04).

So the target in this directory is **not** the D1 estimator's target. It is a valid record of what
Gate-2 produced on 2026-07-19 under the pre-D1 definition, and nothing more.

## Provenance

The archived receipt records its own hashes; `superseded-20260719/` adds no metadata of its own
beyond this note. The hand-authored construction attestation
`docs/orchestration/state/g2-gate2-construction-20260719.json` was separately marked SUPERSEDED on
2026-08-04 (decision D3) and points at the runtime receipt lineage.
