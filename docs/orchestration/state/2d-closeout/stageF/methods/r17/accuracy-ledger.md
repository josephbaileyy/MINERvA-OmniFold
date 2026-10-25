# Fact ledger: the r17 accuracy fixes (unscored), against r17's scored text

Base: r17's scored commit `63f1d61b` (`paper_body.tex` sha256 `711b3e91…`). Check with
`check_ledger.py <worktree> --base 63f1d61b --ledger accuracy-ledger.md`. Approved by the director as
pre-existing accuracy issues found by r17's review (b2-R1, b3-R1, b3-R2). Each row adds or corrects one fact and
names its source.

| id | fact | before | disposition | after | probe |
|---|---|---|---|---|---|
| A1 | the earlier band's coverage criterion: nominal if its ratio to the true scatter lies in [0.9, 1.1] (PREREG-20261005-2d-fixed-truth-coverage.md:119-121) | (added) | KEEP (accuracy fix, added) | IV B | `P::A coverage test specified in advance scored an earlier version of the statistical band, distinct from the quoted block, on \covTwoDNtoy{} closure pseudo-experiments at a fixed truth. The band counts as nominal if its ratio to the true scatter lies in $[0.9,1.1]$. The band failed the test by undercovering in its tails` && `N:sec_validation.tex::The band counts as nominal if its ratio to the true scatter lies in $[0.9,1.1]$` |
| A2 | the bound phrase is unchanged | (protected) | KEEP | IV B | `P::against \SI{95.4}{\percent} nominal.` |
| A3 | the background pseudo-data are a Poisson draw from one half of a separate background sample, not from the source half (M2-AUDIT.md:15; s5n_pseudo.py:130, :135) | P278 | KEEP (accuracy fix, corrected) | VII B | `P::Poisson pseudo-data are drawn from the source half, and the background pseudo-data are a Poisson draw from one half of a separate background sample. The joint-test estimator unfolds the pseudo-data with the other half of the simulation.` && `N:sec_joint.tex::draws Poisson pseudo-data from one half of the simulation together with an independent background source` |
| A4 | A2 also requires the losses to be independent of their outcomes, which has not been shown | (added) | KEEP (accuracy fix, added) | VII C | `P::so their outcomes change no decision. A2 also requires that the pseudo-experiments were lost independently of their outcomes, which has not been shown. Independently written code` && `N:sec_joint.tex::A2 requires the lost pseudo-experiments to have been lost independently of their outcomes, which has not been shown` |
| A5 | the lost-draw and rerun sentences are unchanged | (unchanged) | KEEP | VII C | `P::calibration and \jtLostPow{} power pseudo-experiments, and the decisions use the completed ones. When rerun, none of the lost calibration pseudo-experiments reaches the observed statistic in any test or shifted null` |
