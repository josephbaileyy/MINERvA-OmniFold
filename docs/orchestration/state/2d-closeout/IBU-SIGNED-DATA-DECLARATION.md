# Signed-target binned IBU on the recorded 2D data (draft for review)

## Question and scope

At fixed REF-C2C1 response, prior, efficiency, extraction, iteration count and publication covariance, measure how binned IBU's real-data result changes when its reco target is the binwise signed data-minus-background histogram. Run at K=5 and K=10. The historical refined-target IBU distances are 0.83 and 1.03 respectively, and the recorded OmniFold E_R distance is 2.27. All distances are descriptive χ²/ndf against the published result and its covariance. [REF-C2C1 outcome](../../OUTCOME-20261106-ref-c2c1-read.md)

This is a separate real-data comparison. It measures the change under one target substitution at two fixed K values. It cannot resolve the OmniFold–IBU shape difference by itself, identify a more accurate estimator, validate the target treatment on known truth, or change the paper or note.

## Pinned inputs and methods

| Input | SHA-256 |
|---|---|
| CV omnifile used by E_R and REF-C2C1 | `43f8cc16ab2688200d3e2e0ebb48012b23ada6d7882b8c68ecfc51c609aeb8df` |
| Baseline flux ROOT file | `d40aea69235cdc98644e1bb3e622e579d6b81904c004c83fe50465079989f316` |
| Recorded E_R `xsec.root` | `a5c13fc38d64242bc9ee459fac87568a2f97fddf7a3ac97cc6f91eb4c2a31cef` |
| Recorded REF-C2C1 `c2_central.npz` | `929d0e78011ead72e9677a05bad06eec80e914e181c8d02f94bbdea1c43b76f4` |
| Published precision ROOT file | `6c6dce72050bb8f128fab8e286349b250bc60d1c767e162bf15a0f009f3573e3` |
| RooUnfold library | `0b34e1e39102b0dddc5923dad7f69e59c70cd6a2fcbcef07728b72cf2933fefd` |

Use the REF-C2C1 central production driver and binned response convention from commit `77d76cfc2d621f8faa010b75006811868494652a`. The driver SHA-256 is `938c53c5a018d20f5b148f6bdc2949e987a60085c5d0b7913ccdd5bb438b5a3b` and the C2 module SHA-256 is `285dd138363d090a4ce5dea3361be81fada8680bd782b918e9d95198d1b5d6ea`. Use the publication distance convention from REF-C2C1's read at `af70e9c4685acdf2d64e30d812942bea1e7ccb0c`. Record the exact runtime, input digests, implementation commit and script digests in the execution binding before running. Verify availability by digest and stage from approved copies through `O_NOATIME`.

1. Read the recorded E_R `hMeasSub2D` and verify the signed data-minus-POT-scaled-background identity against `hDataReco2D - hBkgReco2D`. Retain the historical background/fakes convention and report underflow and overflow. Use the complete in-grid 14×16 histogram as the IBU operand. Keep the 205 reporting cells and pT-major order, with a common mask and published `TotalCovariance` for the distance calculation. Require the published statistical and total positive-diagonal masks to agree index by index for that comparison.
2. Build T and M from the pinned CV signal trees with the REF-C2C1 truth/reco flags, POT scale, weights, binning and flow rules. Apply the same completeness, flux, nucleon, POT and area normalization. First use the archived binned refined `y` in `c2_central.npz` on that response and compare reconstructed K=5 and K=10 cross sections to the recorded C2 arrays at relative `1e-8` on reported cells. Recompute the rounded C2 distances and the E_R full-precision reference `465.41527219152636 / 205` as identity checks. No refinement fit is required for this step.
3. Before unfolding the signed histogram, refuse a negative or nonfinite value in any in-grid reco cell, a nonzero target in a row with zero support, or a reported truth cell with nonpositive truth/efficiency. Record the offending cells and original contents and stop. This design preserves signed bin contents without clipping, dropping or merging bins. For admissible input, run RooUnfoldBayes and the NumPy D'Agostini implementation at both K values and require relative agreement within `1e-9` in the reported cross-section vectors.
4. Preserve the signed and archived refined target vectors, the response and prior identities, ordered selected cells, both signed and refined IBU cross-section vectors, and the E_R vector. Report each χ², ndf, and χ²/ndf with the publication covariance and the difference in those distances. At each K, report the signed-minus-refined IBU shift in every reported cell, and put the two per-cell differences E_R minus IBU-signed and E_R minus IBU-refined side by side. Report the quadratic distance, χ² and χ²/ndf, for each E_R–IBU difference under the same published covariance. These latter distances describe separation between the recorded estimates under one metric, with no sampling or significance interpretation.

   For both K values also report the signed-minus-refined shift on the fixed 14 cells that failed run c's refined-target nominal control. These are zero-based `(ipt, ipz) = (0–11, 15)`, `(8, 0)` and `(9, 1)`. Report each shift, their signed median, and their maximum absolute shift with its cell. This subset was chosen from a prior control, so its readout is descriptive and carries no causal interpretation. Report both K values regardless of the results. A failed identity or missing input yields STOP and no signed-target distance.

## Outcome licenses and execution

A smaller or larger signed-target distance records movement toward or away from the published cross section at that K under the declared covariance. If the two K values move differently, report both movements. A small movement is a measured sensitivity for this substitution, with no equivalence threshold. In all cases any relationship to the previous measured shape difference is descriptive. No uncertainty, significance of improvement, publication adoption or causal claim follows. Negative targets or failed controls identify which signed-target path was inadmissible and yield no comparison.

The proposed execution is one bounded login-node session with CPU histogramming, two binned unfoldings and verification, at zero allocated node-hours. Use staged copies and fresh scratch-only output, with no CFS writes. Preserve receipts and STOP evidence. If the guarded histogramming does not fit the reviewed login envelope, stop with the observed resource use and price a separately authorized CPU execution. The director reviews the declaration and exact code before any launch and supplies a stage-specific go with fresh fence acknowledgments.
