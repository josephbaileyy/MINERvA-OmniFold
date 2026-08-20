# Active process-evidence index

The complete pre-freeze casebook and every long-form finding live at
`evidence/prepublication-2026-08-20-0b329e8a`. Recover an indexed row with:

```bash
git show evidence/prepublication-2026-08-20-0b329e8a:docs/orchestration/FINDINGS.md | rg '<BEN-ID>'
```

This file retains only BEN identifiers used by the active generated playbook. `PLAYBOOK.md` owns the
current operating rule and observable check; the tag owns the complete evidence and chronology.

The allocation table remains machine-readable because the merge guard derives ownership from it. Full
allocation rationale is frozen at the evidence tag; new allocations still require a fetched-remote
freeness check and a closed ten-block claimed with its first filing.

| lane | block |
|---|---|
| pre-block era | `001-089` |
| D — verifier | `090-099` |
| B — uncertainty | `100-129` |
| C — PET | `130-159` |
| D — verifier successor | `160-189` |
| A — orchestrator | `190-199` |
| repository infrastructure | `200-209` |
| A — orchestrator continued | `210-229` |
| C — PET continued | `230-239` |
| B — uncertainty continued | `240-249` |
| D — verifier continued | `250-259` |
| receipt repair | `260-269` |
| Gate-6 Leg 0 | `270-279` |
| P5A extraction repair | `280-289` |
| OI-120(c) repair | `290-299` |
| mediator | `300-309` |
| executor | `310-319` |
| propagation correction | `320-329` |
| OI-124 disposition | `330-339` |
| diagnostic review | `340-349` |
| PET verification | `350-359` |
| fold-forward closure | `360-369` |
| hook dispatch | `370-379` |
| quarantine provenance | `380-389` |
| seconding | `390-399` |
| C — PET third block | `400-409` |
| quarantine provenance second block | `410-419` |
| C — PET fourth block | `420-429` |
| mediator second block | `430-439` |
| seconding second block | `440-449` |
| D — verifier second block | `450-459` |
| C — PET fifth block | `460-469` |
| quarantine provenance third block | `470-479` |
| B — uncertainty third block | `480-489` |
| storage migration | `490-499` |
| fixture-decoy block — do not allocate without exact review | `500-509` |
| remedy-(A) verification | `510-519` |
| unallocated | `520+` |

## Long-form findings index

All pre-freeze long forms are indexed by the frozen `FINDINGS.md` at the evidence tag.

The following long forms remain in the live checkout because code, tests, or active records consume
them. Their full evidence rows remain in the frozen index.

| retained long form | route |
|---|---|
| `FINDING-20260730-event-feature-nonfinite.md` | Full evidence row at the evidence tag. |
| `FINDING-20260802-estimator-definition-vs-driver.md` | Full evidence row at the evidence tag. |
| `FINDING-20260802-extractor-pass-truth-mask.md` | Full evidence row at the evidence tag. |
| `FINDING-20260802-orchestration-tests-never-run.md` | Full evidence row at the evidence tag. |
| `FINDING-20260804-b4-is-active-gate2-cannot-be-reissued.md` | Full evidence row at the evidence tag. |
| `FINDING-20260804-gate2-units-resolved-gev.md` | Full evidence row at the evidence tag. |
| `FINDING-20260804-step3-closure-needs-root-and-tf-in-one-interpreter.md` | Full evidence row at the evidence tag. |
| `FINDING-20260804-step7b-corr-cosphi-pt-measured.md` | Full evidence row at the evidence tag. |
| `FINDING-20260806-campaign-pin-inverted-on-insignificant-variance.md` | Full evidence row at the evidence tag. |
| `FINDING-20260806-j28-reroll-exact.md` | Full evidence row at the evidence tag. |
| `FINDING-20260806-niter4-decision.md` | Full evidence row at the evidence tag. |
| `FINDING-20260807-checkpoint-is-not-the-trained-model.md` | Full evidence row at the evidence tag. |
| `FINDING-20260807-d2-acceptance-limited-oracle.md` | Full evidence row at the evidence tag. |
| `FINDING-20260807-d2-underfitting-probe.md` | Full evidence row at the evidence tag. |
| `FINDING-20260807-step1-under-achieves.md` | Full evidence row at the evidence tag. |
| `FINDING-20260809-derived-from-merged-extensives.md` | Full evidence row at the evidence tag. |
| `FINDING-20260809-stage6-central-gate-cannot-pass.md` | Full evidence row at the evidence tag. |
| `FINDING-20260809-tparameter-merge-semantics.md` | Full evidence row at the evidence tag. |
| `FINDING-20260811-promotion-by-move-silently-repoints-artifacts.md` | Full evidence row at the evidence tag. |
| `FINDING-20260811-trajectory-label-is-direction-blind.md` | Full evidence row at the evidence tag. |
| `FINDING-20260812-exit-contract-drifted-into-prose.md` | Full evidence row at the evidence tag. |
| `FINDING-20260812-nested-conflict-markers-false-pass.md` | Full evidence row at the evidence tag. |
| `FINDING-20260812-orchestrator-instrument-defects.md` | Full evidence row at the evidence tag. |
| `FINDING-20260812-session-health-metric-counts-its-own-subject.md` | Full evidence row at the evidence tag. |
| `FINDING-20260813-a-committed-hook-is-not-an-installed-hook.md` | Full evidence row at the evidence tag. |
| `FINDING-20260813-attribution-drift-has-no-natural-discoverer.md` | Full evidence row at the evidence tag. |
| `FINDING-20260813-colliding-in-a-namespace-you-just-warned-about.md` | Full evidence row at the evidence tag. |
| `FINDING-20260813-committed-is-not-deployed.md` | Full evidence row at the evidence tag. |
| `FINDING-20260813-local-git-config-is-not-lane-local.md` | Full evidence row at the evidence tag. |
| `FINDING-20260813-same-key-name-different-quantity.md` | Full evidence row at the evidence tag. |
| `FINDING-20260813-the-gate-was-relative-to-its-own-argument.md` | Full evidence row at the evidence tag. |
| `FINDING-20260813-unverified-stream-was-the-one-carrying-physics.md` | Full evidence row at the evidence tag. |
| `FINDING-20260814-a-decision-that-reached-its-own-record-and-nowhere-else.md` | Full evidence row at the evidence tag. |
| `FINDING-20260814-a-scalar-gate-cannot-answer-a-shape-question.md` | Full evidence row at the evidence tag. |
| `FINDING-20260814-a-sentinel-that-collided-with-a-result.md` | Full evidence row at the evidence tag. |
| `FINDING-20260814-ninety-times-counting-statistics.md` | Full evidence row at the evidence tag. |
| `FINDING-20260814-the-guards-most-reassuring-sentence-is-its-empty-one.md` | Full evidence row at the evidence tag. |
| `FINDING-20260815-a-consumer-is-not-a-file-extension.md` | Full evidence row at the evidence tag. |
| `FINDING-20260815-a-guard-that-cannot-tell-a-mention-from-a-consumer.md` | Full evidence row at the evidence tag. |
| `FINDING-20260815-a-guard-with-no-cell-for-what-it-cannot-see.md` | Full evidence row at the evidence tag. |
| `FINDING-20260815-a-restatement-is-not-a-second-measurement.md` | Full evidence row at the evidence tag. |
| `FINDING-20260815-a-share-of-total-without-bin-widths.md` | Full evidence row at the evidence tag. |
| `FINDING-20260815-an-arm-whose-answer-was-entailed-by-statement-order.md` | Full evidence row at the evidence tag. |
| `FINDING-20260815-the-quarantine-measured-a-different-run.md` | Full evidence row at the evidence tag. |
| `FINDING-20260815-true-when-written-then-copied-forward.md` | Full evidence row at the evidence tag. |
| `FINDING-20260816-a-recomputation-identity-cannot-validate-its-premise.md` | Full evidence row at the evidence tag. |
| `FINDING-20260816-the-gate-that-measures-blas-blocking-noise.md` | Full evidence row at the evidence tag. |
| `FINDING-20260817-a-seed-census-that-cannot-reach-the-product-it-grades.md` | Full evidence row at the evidence tag. |
| `FINDING-20260817-cause3-C-leg-does-not-cover-the-dominant-block.md` | Full evidence row at the evidence tag. |
| `FINDING-20260819-a-guard-forbade-what-a-pinned-producer-must-produce.md` | Full evidence row at the evidence tag. |

| id | frozen evidence |
|---|---|
| BEN-023 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-025 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-026 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-027 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-028 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-035 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-074 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-077 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-080 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-082 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-119 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-191 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-193 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-199 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-205 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-214 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-228 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-300 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-304 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-305 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-312 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-322 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-323 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-328 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-331 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-335 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-383 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-387 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-392 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-398 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-410 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-454 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-455 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-456 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-468 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-476 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-477 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-478 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-482 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-483 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
| BEN-484 | Pre-freeze `docs/orchestration/FINDINGS.md` at the evidence tag. |
