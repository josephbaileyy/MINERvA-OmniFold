# N-D OmniFold (4D q3 / 5D W / PET / FPS) — Status

**Last updated**: 2026-07-24. Narrative lives in `ND_OMNIFOLD_RUN_LOG.md`,
verified numbers in `../VALIDATION_LEDGER.md`, bugs in `../KNOWN_ISSUES.md`,
and work remaining in `../docs/OPEN_ITEMS.md`.

Gregor PET2 assessment (2026-07-23): isolated PyTorch backend passes the local
and complete Delta code-contract gates plus a bitwise two-job A100 smoke. The
truth-frozen matched synthetic, TensorFlow A/B, and bounded XPS2 pilots are
complete: no arm passed the absolute closure gate and no architecture or
representation promotion is authorized. Keep the PyTorch path experimental;
publication choice remains deferred to literal G2 validation.

Conditional-information continuation (2026-07-24): the original matrix is
reclassified as a baseline-sufficient null-feature test. The preregistered
five-family feature-conditional stress matrix completed as recovery array
`20441096` from exact `ba28bed` (safetensors 0.5.3 overlay); Delta `sacct`
confirms all 45 cells `COMPLETED 0:0`, and an independent local re-run of the
fail-closed aggregator reproduces the staged aggregate bitwise
(`d244c7b6…`, 90 arms). Result: `all_families_passed=false` — no family
(view/type/rich/muon-token/overflow) passed the channel-capacity gate. Each
enriched carrier was direction-favorable in all three seeds with ~27–28% push
RMSE improvement (parent ~0.431 → enriched ~0.31) but fell short of the ≥30% /
≤0.25 threshold; both negative controls (unity-sham, carrier-shuffle) passed.
This is `synthetic-fixture` channel-capacity evidence only; no feature adoption
or publication promotion is authorized. Post-result auditor review is COMPLETE
(contract ACCEPT, evidence PASS, no findings; 100k pilot-power dissent
preserved). Verified numbers live in `../VALIDATION_LEDGER.md`.

Publication execution is indexed, without duplicating scientific facts, in
[the dependency/rerun map](../docs/RESULT_DEPENDENCY_AND_RERUN_MAP.md) and
[the publication runbook](../docs/PUBLICATION_COMPLETION_RUNBOOK.md).
Post-freeze cleanup is gated by
[the reorganization plan](../docs/POST_PUBLICATION_REORG_PLAN.md). These are
instructions, not evidence that a run has occurred.

## Current quotable results

| Result | Current statement | Artifact |
|---|---|---|
| 4D central cross section | sigma=3.066e-38 cm2/nucleon; 4D/3D anchor 0.9960; closure PASS | `products/4d/xsec_4d_MEFHC_5iter_lgbm.root` |
| 5D central cross section | 5D/4D anchor 1.0011; injected-W closure PASS | `products/5d/xsec_5d_MEFHC_5iter_lgbm.root` |
| Corrected 5D GBDT covariance | background-aware block median 13.359%; adopted mean-centered sqrt-trace 5.8077e-38; CV-centered conservative variant 6.2367e-38 | `uq_5d/universe_stage2_5d_bkgaware/` |
| `(E_avail,W)` shape localization | Positive data-minus-generator excess is concentrated at high E_avail and high W; exact significance withheld | `products/5d/` |
| PET central-value milestone | Closure 0.9884; PET/GBDT central-total ratio 0.9117 is a training-configuration diagnostic, not a precision claim | `products/pet/` |
| Corrected PET 5D budget | five-component PSD sum: median 15.103%, sqrt-trace 3.8777e-38; 4D marginal median 12.365%; present campaign COMPLETE | `products/pet/bkgsub/pet_ctotal_bkgsub_5d_final.summary.json` |
| NN cross-check | keras-MLP/GBDT total ratio 1.0078 | `omnifold_nn_core.py` |
| Unbinned GoF | Prior z=33 to unfolded z=1.4, p=0.17, PASS | `unbinned_gof.py` |
| Reco/migration controls | Data/MC 1.12 uniform; diagonal purity about 0.6 per axis | `products/5d/control_plots.png`, `migration_resolution.png` |
| Truth-cloud coverage | 99.9995% after native-miss cloud fix; E_avail projection validated; W is not cloud-projectable | `products/pet/fullcloud/pointcloud_projection_summary.json` |

## Quarantined historical results

The old adopted 4D/5D/FPS unified covariances and all old PET uncertainty
budgets/precision comparisons, the `(E_avail,W)` covariance, and all dependent
generator significances are **unquotable**. Historical numbers remain in the
validation ledger for provenance but are not current results. The corrected 5D
GBDT and PET entries above supersede their respective historical products; no
replacement is implied for 4D/FPS or dependent significances. See
`KNOWN_ISSUES.md` #14-16.

## Remediation in flight

- P3F-scalar interface inventory is committed PASS: the complete 5-band x
  2-endpoint x 12-playlist (120/120) manifest is SHA- and producer-bound with
  zero failures. This is prerequisite evidence only; P3F-PET generation and PET
  training have not started.
- The corrected 5D GBDT chain is adopted. Its `C_ML` varies the train/test split
  at fixed estimator seed 42; the dedicated estimator-only scan is an auxiliary
  robustness check and is not added as an independent matrix.
- The current PET campaign is complete with 20 coherent data+MC statistical
  retrains, a 12-member crossed PET ML ensemble, vertical and detector blocks,
  and a material six-band targeted-retraining block. Before publication, expand
  the statistical inventory to 100 replicas; this has not yet been run. The old
  unit-weight replicas remain unsubtracted cross-checks only.
- `(E_avail,W)` will project the corrected full 5D statistical covariance as
  `M C_5D M^T` and use actual +/- mean-centered systematic endpoints.
- Presentation production is closed; no presentation-specific active-universe
  run remains. Bank results remain support-limited, and full five-band
  active-universe coverage remains the publication gate.
- The background-aware 12-playlist dump and full 188-entry re-quote are complete;
  the combined effect is below 0.3%. The code remains fail-closed against
  missing per-universe background columns.

## Presentation rule

Use central values, closure, anchors, and shape-level observations normally.
Use a corrected uncertainty or significance only if it has a committed ledger
entry and passed all gates. Otherwise label it preliminary/support-limited or
omit the number. Never substitute the quarantined historical value.

Execution details and live jobs: `CORRECTED_UQ_PRODUCTION_STATUS.md`.
