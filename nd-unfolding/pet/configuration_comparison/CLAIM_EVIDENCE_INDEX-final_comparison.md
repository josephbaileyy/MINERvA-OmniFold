# Claim-to-evidence index: final comparison

Every claim the deck makes, and the artifact that settles it. Generated with the
deck from the same report, so the two cannot drift.

| claim | evidence |
|---|---|
| paired effect -0.1129, CI [-0.1471, -0.0786], n=8 | `campaign_report.json` -> `interval`; computed by `score_campaign.t_interval`, whose quantiles are checked against published tables in `test_score_campaign.py` |
| the pilot is excluded from that interval | `campaign_report.json` -> `pilot_excluded`; enforced by `score_campaign.score_campaign`, which raises if pilot rows are passed as campaign scores |
| absolute adequacy per arm | `campaign_report.json` -> `absolute_adequacy`; floor is `THRESHOLDS["adequacy_fraction_of_reference"]` x the reference in `provenance.aggregate_reference` |
| regional floors are per region | `campaign_report.json` -> `regional_safeguard.floor_by_region`; references from `characterize_regions.regional_reference` |
| regions are cells, not marginal bins | `characterize_regions.region_labels_for_events`, tested against `np.histogram2d` in `test_regions.py` |
| safeguard coverage | `campaign_report.json` -> `regional_coverage.off_grid_truth_fraction` |
| low-acceptance mass, displacement and per-arm recovery | `campaign_report.json` -> `low_acceptance` |
| step 2 is identical across arms | `frozen_design.STEP_SCOPE`; `run_arm_evaluation.evaluate` builds `model_gen` from `OURS_INCUMBENT` for both arms |
| the three declared differences | `build_theirs_inputs.DECLARED_DIFFERENCES`, with tests in `test_build_theirs_inputs.py` |
| the twelve-category component comparison | `CONFIGURATION_COMPARISON-20260918.md`; extracted by `make_final_deck.component_comparison`, which fails unless exactly 12 are found |
| verdict and recommendation | `selection_rule.decide`, applied in `score_campaign.score_campaign` with thresholds from `frozen_design.THRESHOLDS` |
| provenance | commit `68cf9d29f8ab`, closure sha256 `fa6b346316024216`, ? truth rows |

**Scope.** PET is diagnostic method development. Nothing indexed here is a
publication adoption, a covariance, a systematic, a central-value change or a
Gate-6 action.
