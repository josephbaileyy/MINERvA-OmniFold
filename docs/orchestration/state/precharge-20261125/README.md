# MINOS reconstructed charge before the ME-FHC sign cut

## Observed and predicted yields

Counts use all 12 playlists at the full data exposure. The baseline folds the published spectrum with the all-selected efficiency convention. The comparison uses our upstream AnaTuples and production CV code.

| Reconstructed longitudinal momentum (GeV/c) | Negative data | Negative fold | Positive data | Positive fold | Both signs, data minus fold |
|---|---:|---:|---:|---:|---:|
| 20–40 | 137,785 | 137,449.7 | 13,047 | 10,528.7 | +2,853.6 |
| 40–60 | 20,355 | 19,416.3 | 1,480 | 1,167.7 | +1,250.9 |
| 60–80 | 2,495 | 1,497.1 | 228 | 192.8 | +1,033.0 |
| ≥80 | 415 | 348.4 | 147 | 115.2 | +98.4 |

Above 60 GeV/c the negative deficit in the fold is 1,064.5. Reassigning its entire positive prediction of 308.1 events to the negative sign would still leave 756.4 missing negative tracks and no positive prediction for the 375 observed. Both signs together leave 1,131.4 missing events before the charge requirement.

The signed curvature distribution locates the excess away from zero. For reconstructed longitudinal momentum ≥60 GeV/c and |q/p| < 0.005 (GeV/c)⁻¹ the observed negative and positive counts are 12 and 6, against 11.9 and 7.7 predicted. At |q/p| ≥1/60 (GeV/c)⁻¹ they are 935 and 79, against 278.1 and 26.5 predicted. These two outer tails account for about 709 of the 1,131 excess tracks. MINOS fitted curvature and the beam-frame reconstructed longitudinal momentum are separate recorded quantities.

Among negative tracks above 60, 2,306 data events pass the curvature precision requirement |σ(q/p)/(q/p)| < 0.30, against 1,214.1 predicted. The complementary counts are 604 and 631.4. The positive-side good-precision counts are 129 and 97.9. In simulation, muon-antineutrino CC interactions contribute 31.6% of the positive prediction at 60–80 and 18.4% at ≥80. Interaction flavor alone cannot identify the matched track's true charge.

## Changing the charge decision

The single fitted relative simulation threshold was q/p < 0.025078 (GeV/c)⁻¹. It yielded 10,918.1 negative events for 10,918 observed at 40–60 in the training playlists. The data kept the nominal q/p < 0 classification. The predictions below use the other six playlists, the same threshold, and their individual exposure ratios.

| Reco (GeV/c) | Negative data | Shifted negative | Positive data | Shifted positive |
|---|---:|---:|---:|---:|
| 20–40 | 64,059 | 63,849.5 | 6,187 | 4,938.7 |
| 40–60 | 9,437 | 9,540.4 | 681 | 80.0 |
| 60–80 | 1,181 | 778.7 | 104 | 0.0 |
| ≥80 | 192 | 217.0 | 68 | 0.0 |

## Positive-sign predictions from the earlier negative-sign fits

The two variations use the negative-only training amplitudes frozen before this charge control. The true-tail variation adds events with true longitudinal momentum ≥60 GeV/c. The migration variation adds events that originated in a lower truth bin and reconstructed upward. Each variation transfers its source's simulated charge distribution.

| Held-out reco (GeV/c) | Positive data | Baseline | Extra true tail | Extra upward migrants |
|---|---:|---:|---:|---:|
| 20–40 | 6,187 | 4,938.7 | 4,938.7 | 4,938.7 |
| 40–60 | 681 | 561.4 | 561.4 | 572.4 |
| 60–80 | 104 | 89.9 | 90.4 | 105.8 |
| ≥80 | 68 | 54.1 | 54.4 | 59.7 |

The positive data-to-baseline ratio at 20–40 is 1.253. Applying that single neighbor ratio as a shape diagnostic gives 181.4 positive overflow tracks for the true-tail transfer and 207.4 for the migration transfer, compared with 172 observed. The absolute predictions are 144.8 and 165.5. The neighbor rescaling illustrates sensitivity to the sign-specific normalization. The positive interaction mixture itself varies with reconstructed momentum.

## What would separate a truth-rate change from a momentum-response change

The sign-summed discrepancy is present before the charge decision. A momentum-dependent curvature bias can still move tracks between reconstructed momentum bins. To locate the first difference against MINERvA production, obtain one original weighted event-count table per POT in fine true transverse and longitudinal bins, with true longitudinal overflow explicitly subdivided. The row must include the generated denominator, missed tracks and selected destinations by reconstructed momentum and both fitted charge signs. Record the same selected cells with truth and reconstruction weights, and separate signal and background origins. The generated row totals determine the truth rate, the selected fractions determine efficiency, and the relative signed destinations determine migration. An independent momentum reference would additionally be needed to establish a physical calibration bias in data.

[Replay and definitions](REPLAY.md) · [Signed curvature spectrum](signed-curvature.pdf) · [Machine-readable signed cells](signed-qp.csv) · [Quality split](merged-quality.csv) · [MC interaction origins](merged-origin.csv) · [Negative-branch closure](negative-closure.csv)
