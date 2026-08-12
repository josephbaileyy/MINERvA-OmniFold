# CLM-011 claim detail

## Original claim cell

The extended-FPS cross section must NOT be divided by a reco efficiency. `extract_cross_section_nd`'s `completeness` argument means coverage of the truth denominator by the OmniFold input (`unfold_nd_omnifold_unbinned.py:992-999`, `of_in/denom_nd`); this extractor has no separate truth denominator -- the declared fiducial domain IS `pass_truth` -- so coverage is 1 BY CONSTRUCTION, and `counts` is already acceptance-corrected because `MultiFold.RunStep2` assigns nu_k to truth-only-miss rows (`omnifold.py:218-220`). Dividing again inflated the integral by 122.6x (cell-by-cell, so Jensen; not 1/<a> = 2.36x) and the worst cell by 807x. **This sets the published normalization.**

## Status history

VERIFIED-CODE

## Evidence artifact

source legs verified independently in three sessions; magnitudes recomputed from `products/pet/fullevent_fps/acceptance_map_fullevent_fps.json`; GBDT corroboration `globalCompleteness = 1.0000000000000002`, 266/266 nonzero bins at 1.000000

## Data/config hash

acceptance map pins the G2 dump `fa6b3463…`

## Commit

this commit

## Slurm job(s)

—

## Independent verifier

fresh-context claude-school opus x3 (found it, quantified it, and reviewed the fix pre-commit)

## Residual history

Coverage=1 is now GUARDED (`assert_truth_denominator_coverage`) rather than assumed, but the dump carries no independent truth-denominator array to cross-check against, so the guard checks finiteness/population only. The reported domain is set entirely by `comp > 0`, which is a floor and NOT the acceptance-supported vs model-dependent tiering decision (open, `OPEN_ITEMS:430-438`). No run has yet used the corrected extractor.
