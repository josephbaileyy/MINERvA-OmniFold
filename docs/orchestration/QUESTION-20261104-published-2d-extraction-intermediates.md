# QUESTION: intermediate products for the published 2D inclusive extraction

**Status: PREPARED, NOT SENT.** Joseph alone decides whether to send this question and to whom.
No contact has been made. This document requests factual inputs; it is not an interpretation,
a publication correction, an adoption decision or a request for scientific endorsement.

**Why it is needed.** The B-C inventory at repository baseline
`97f1ff8deddddecfad07352ebb5df16377dd8e3c` compares our adopted refined 2D extraction with
this repository's copy of the release associated with arXiv:2106.16210 / PRD 104, 092007.
The committed copy's README and file inventory provide final cross sections, bin mapping and
covariance components. They do not supply the intermediate numerical arrays needed to determine
at which extraction stage the two central results diverge. This is a statement about the inspected
copy, not about what the collaboration retains or has made available elsewhere.

Evidence route: [B-C accounting](state/2d-closeout/stageF/methods/secondary-results/component-accounting-20261104/REPORT.md),
its `RELEASE-INVENTORY.tsv`, `SOURCE-INVENTORY.tsv` and `SEARCHES.txt`. The primary precision
comparison reference is identified by the existing RE-2 agreement receipt:
`cov_ptpl_minerva_inclusive_6GeV.root`, sha256
`6c6dce72050bb8f128fab8e286349b250bc60d1c767e162bf15a0f009f3573e3`,
objects `pt_pl_cross_section` and `StatOnlyCovariance`.

## Factual questions for a knowledgeable custodian

Are matching intermediate products available for the same dataset, signal definition and 2D
binning as that published result? If so, could their location and processing version be supplied,
with the following ingredients where retained?

- Selected reconstructed data and predicted reconstructed signal on the joint muon-momentum grid;
  predicted background components and the resulting background-subtracted reco spectrum.
- The response/migration matrix, its row/column and missed/fake-event conventions, the truth prior,
  selected-signal efficiency numerator and full signal truth denominator.
- The unfolded event yield before efficiency/acceptance and flux/target/POT normalisation, with
  the regularisation/iteration setting and the numerical efficiency/acceptance correction used.
- The nominal flux spectrum and its integration range/units, playlist combination and exposure
  weights, the exact flux/constraint prescription, data and MC POT and target normalisation.
  A flux covariance alone does not specify these central-value ingredients.
- The exact truth/reconstruction selection and boundary conventions, beam-axis definition and
  processing/calibration release identifier needed to ensure a like-for-like comparison.
- The precise global-cell mapping and reported mask used for those intermediate arrays, together
  with an unrounded final reference if it differs from the precision file identified above.

If some products are not retained or not releasable, which of these comparisons can be reconstructed
from existing public material, and which would require a collaboration-side re-extraction?

## Scope boundary

No new collaboration production, simulation or calibration study is requested by this document.
A link to existing products or a description of what is retained would resolve the availability
question first. Any material new work or outward communication remains Joseph's decision.
No muon-calibration defect is inferred from this inventory; the processing identifier is requested
for provenance. C-R/d1 and d2 remain the limitation-resolver lane's work.
