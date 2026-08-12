# Known issues, bugs, and code debt — INDEX

One line per issue, pointer to the canonical home for detail. **This file is an
index, not a copy** — update the pointer target, not this file, when an issue
evolves. Add new issues here the moment they are found, so they never get
buried in run-log prose.

## Live issues

| id | severity | status | one-sentence failure | detail | updated |
|---|---|---|---|---|---|
| J | HIGH | OPEN | The 2026-07-31 four-account audit retains unresolved publication and provenance findings. | [audit detail](docs/orchestration/AUDIT-FINDINGS-20260731.md) | 2026-08-01 |
| 5 | MEDIUM | OPEN | The low-p_parallel MINOS sum-ratio gradient persists after the matching fix and is not explained by official muon-quality cuts. | [2D reference](2d-unfolding/2D_OMNIFOLD_REFERENCE.md) | 2026-06-10 |
| 8 | HIGH | OPEN | Merged TParameters can corrupt intensive values, flags, and ratios derived from separately valid extensive totals. | [merge-semantics finding](docs/orchestration/FINDING-20260809-tparameter-merge-semantics.md) | 2026-08-09 |
| 16 | HIGH | OPEN | Bank-derived lateral covariances remain support-limited until the promoted-universe migration bound is adopted. | [open remediation gate](docs/OPEN_ITEMS.md) | 2026-07-14 |
| 19 | BLOCKER | OPEN | No quotable full-event FPS PET result exists because the Branch-C measurement-domain and inference gates remain unmet. | [cause-5 determination](docs/orchestration/DETERMINATION-20260811-cause5-binding-half.md) | 2026-08-12 |
| 20 | HIGH | OPEN | The standard-P4 chain still requires its open attestation leg even though earlier construction and purity decisions are settled. | [GBDT closeout runbook](docs/orchestration/RUNBOOK-20260807-gbdt-closeout.md) | 2026-08-07 |
| 21 | CRITICAL | OPEN | The P4 verifier gate is advisory in practice and can be crossed without a human checkpoint. | [repair status](docs/orchestration/REPAIR4-DEFECT-STATUS-20260807.md) | 2026-08-07 |
| 23 | HIGH | OPEN | Re-running P4 evidence can misattribute old endpoint artifacts to the code and binary present now. | [verifier defect brief](docs/orchestration/followup-agent-A-standard-05.md) | 2026-08-07 |
| 24 | HIGH | OPEN | Endpoint SHA-256 binds storage identity rather than derivation identity and breaks on legitimate nondeterministic re-unfolds. | [ND run log](nd-unfolding/ND_OMNIFOLD_RUN_LOG.md) | 2026-08-07 |
| J36 | HIGH | OPEN | Global POT scaling discards per-playlist Data/MC ratios and skews the MC playlist mixture at eight live sites. | [merged-extensives finding](docs/orchestration/FINDING-20260809-derived-from-merged-extensives.md) | 2026-08-09 |
| 26 | MEDIUM | OPEN | The inherited 1.17 reconstructed-E_avail scale has recorded lineage but no upstream or local justification. | [open external-input item](docs/OPEN_ITEMS.md) | 2026-08-12 |
| 28 | LOW | OPEN | The engine labels the first validation loss as the last, concealing the actual final and best epochs. | [issue detail](docs/known-issues/ISSUE-28-last-val-loss-prints-first-epoch.md) | 2026-08-07 |
| 30 | MEDIUM | OPEN | The off-gate point-cloud projection repeats the reco-efficiency double correction and must be settled before promotion. | [issue detail](docs/known-issues/ISSUE-30-pointcloud-projection-double-completeness.md) | 2026-08-06 |
| 31 | MEDIUM | OPEN | The powered-closure driver persists no normalization or architecture contract for inference-only reproduction. | [issue detail](docs/known-issues/ISSUE-31-closure-inference-contract-missing.md) | 2026-08-06 |
| 32 | HIGH | OPEN | PET covariance summaries omit the estimator configuration needed to classify their footing after the estimator changes. | [issue detail](docs/known-issues/ISSUE-32-pet-covariance-estimator-stamp-missing.md) | 2026-08-06 |
| 33 | MEDIUM | OPEN | The stored step1_class_ratio is an input target whose name invites it to be misread as an achieved measurement. | [issue detail](docs/known-issues/ISSUE-33-step1-class-ratio-is-target.md) | 2026-08-07 |
| 34 | HIGH | OPEN | Load-bearing tests and a required module remain only on purgeable scratch and disappear from fresh-clone collection. | [issue detail](docs/known-issues/ISSUE-34-tests-on-purgeable-scratch.md) | 2026-08-07 |
| 36 | HIGH | OPEN | The E_avail-W covariance has not been rebuilt after fixing its per-universe flux normalization. | [issue detail](docs/known-issues/ISSUE-36-eavailw-flux-universe-normalization.md) | 2026-08-06 |
| 38 | HIGH | OPEN | The engine's per-iteration learning-rate anneal is dead code, so warm-started fits run at full learning rate. | [issue detail](docs/known-issues/ISSUE-38-dead-learning-rate-anneal.md) | 2026-08-09 |
| 39 | HIGH | WONTFIX | Resetting the step-1 model and refreshing its split together diverges even though either intervention alone helps. | [issue detail](docs/known-issues/ISSUE-39-cold-model-fresh-split-diverges.md) | 2026-08-09 |
| 40 | MEDIUM | WONTFIX | Powered-closure reports compute recovery_criteria_met against the retired bar rather than the authoritative Gate-4 criterion. | [superseded-value index](docs/orchestration/INDEX-retracted-and-superseded-values.md) | 2026-08-10 |
| 42 | CRITICAL | OPEN | A failed scrontab listing makes wakerctl install-cron replace the table with only its managed block. | [issue detail](docs/known-issues/ISSUE-42-wakerctl-install-cron-fail-open.md) | 2026-08-11 |
| 43 | LOW | WONTFIX | cron-tick.log records crashes rather than successful ticks, so its staleness means health and its growth means failure. | [issue detail](docs/known-issues/ISSUE-43-cron-tick-log-semantics.md) | 2026-08-11 |
| 45 | MEDIUM | OPEN | The Gate-3 queue-latency receipt pins a historical wakerctl revision and has no declared current disposition. | [issue detail](docs/known-issues/ISSUE-45-wakerctl-gate3-pin-lapsed.md) | 2026-08-11 |

## Resolved traps that WILL bite again if forgotten

| id | severity | status | one-sentence failure | detail | updated |
|---|---|---|---|---|---|
| 6 | TRAP | WONTFIX | Never bare-hadd a _universes_full omnifile because ROOT rollover can leave a partial merge without data and background trees. | [2D reference](2d-unfolding/2D_OMNIFOLD_REFERENCE.md) | 2026-08-12 |
| 7 | TRAP | WONTFIX | Never feed the event loop a combined MEFHC manifest because it applies the first playlist's flux to every playlist. | [2D reference](2d-unfolding/2D_OMNIFOLD_REFERENCE.md) | 2026-08-12 |
| 9 | TRAP | RESOLVED | Never compare pre-2026-04-25 event-loop outputs to paper numbers because they use the obsolete MINOS-match stub. | [2D reference](2d-unfolding/2D_OMNIFOLD_REFERENCE.md) | 2026-04-25 |
| 10 | TRAP | FIXED | Do not add a reco-pass completeness division after OmniFold step 2; the marginal self-validation gate must catch this double correction. | [ND run log](nd-unfolding/ND_OMNIFOLD_RUN_LOG.md) | 2026-06-09 |
| 11 | TRAP | FIXED | Do not use the stale mostly-empty PET ExtraEnergyClusters branches; the point-cloud chain uses CVUniverse::GetRecoClusters(). | [validation ledger](VALIDATION_LEDGER.md) | 2026-06-10 |
| 17 | TRAP | WONTFIX | Never extract PET cross sections in the TensorFlow-module Python because it lacks PyROOT. | [replica launcher](nd-unfolding/pet/sbatch_pet_bootstrap_replica.sh) | 2026-08-12 |
| 25 | TRAP | FIXED | Report writers must capture helper output instead of letting print-only results vanish from committed artifacts. | [model comparison receipt](2d-unfolding/receipt_model_chi2_2d.json) | 2026-08-11 |
| 27 | TRAP | FIXED | Resume guards must validate artifact completeness and integrity rather than existence alone. | [audit detail](docs/orchestration/AUDIT-FINDINGS-20260731.md) | 2026-08-01 |
| 29 | TRAP | FIXED | Cross-section extraction over all truth-pass rows must not divide again by reconstructed acceptance. | [archived resolution](KNOWN_ISSUES-ARCHIVE-2026-08.md) | 2026-08-06 |
| 35 | TRAP | FIXED | A fail-closed production guard may correctly reject a stale synthetic fixture rather than being over-strict. | [archived resolution](KNOWN_ISSUES-ARCHIVE-2026-08.md) | 2026-08-06 |
| 37 | TRAP | FIXED | Persist final-epoch checkpoints and round-trip them against stored push weights before permitting downstream extraction. | [BEN-043 resolution](nd-unfolding/ND_OMNIFOLD_RUN_LOG.md) | 2026-08-08 |
| 41 | TRAP | RETRACTED | Do not quote one-shot results from the unstable diagnostic wrapper family as estimator properties. | [retracted-value index](docs/orchestration/INDEX-retracted-and-superseded-values.md) | 2026-08-11 |
| 44 | TRAP | FIXED | Per-watch failures must be isolated and surfaced through watch_errors without making whole-scan failures look healthy. | [archived resolution](KNOWN_ISSUES-ARCHIVE-2026-08.md) | 2026-08-11 |
