# N-D OmniFold (4D q3 / 5D W / PET / FPS) — Status

**Last updated**: 2026-08-10. Narrative lives in `ND_OMNIFOLD_RUN_LOG.md`,
verified numbers in `../VALIDATION_LEDGER.md`, bugs in `../KNOWN_ISSUES.md`,
and work remaining in `../docs/OPEN_ITEMS.md`.

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
| Standard 5D endpoint set | Ten lateral endpoints re-unfolded and published (job `56495756`); reproduce the 07-18 reference 10/10 (worst per-bin 1.83e-11, worst integral 2.87e-12). The covariance candidate built on them **self-declares non-adoptable** — no verifier PASS | `active_universe_5d/standard/unfolds/`, `.../evidence/` |
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

- Full-event diagnostic extraction job 56525297 is reconciled FAILED after its complete, validated
  GPU push: the combined launcher crossed into the ROOT-only stage while still in the TensorFlow
  environment. The preserved push is the sole input to a tested CPU/root_6_28 continuation; no GPU
  retry was run. CPU continuation 56527676 completed `0:0`, reused that exact push, and independently
  confirmed both publication-rejection conditions. The product remains permanently quarantined and
  non-quotable; Joseph's number-free completion mail was accepted locally. The dependency-ready focus
  is Step-1 trajectory job 56525829. Its one-hour queue event found it wholly prestart-pending with no
  output, so a tested detached A100 hedge was selected. The first `setsid` child did not persist, and
  the changed tmux-supervised request also exited before Slurm created a named allocation. The start
  deadline therefore closed the hedge without cancellation or compute: batch 56525829 remains
  PENDING on Priority, owned no output then, and remained the sole writer. It later completed `0:0`.
  Independent validation gives `CORRECT_AT_ITER0_DEGRADES_LATER`: iteration 0 is correct-sign and
  within 9.74% of exact R, while iterations 1 and 2 are wrong-signed. The failure is post-feedback
  iteration dynamics. Three full-input controls are ready in isolated namespaces: warm/fresh split,
  cold/fixed split, and cold/fresh split; together with the completed warm/fixed baseline they form a
  predeclared factorial over split reuse and Step-1 warm-start. Branch C remains and no publication
  cross section is promoted. The three arms are submitted as batch array `56531057` (`0-2%3`), each
  on one A100 with an isolated arm/job namespace; terminal and one-hour prestart queue watches are armed.
  A separately pinned fourth arm, warm/fixed with the engine's intended post-iteration `1e-5` learning
  rate made effective at fit time, is batch job `56531204`, initially PENDING Priority with an isolated
  namespace and terminal/queue-latency watches. It does not modify the shared engine or pending array.
  At the array's one-hour latency wake, all three tasks were still prestart-pending with absent outputs.
  Batch remains the sole writer: the closest full-input nominal took 6h00m44s, so no four-hour
  interactive replacement was safe or allocated. Terminal coverage remains armed.
  The separate annealed-LR job's one-hour wake reached the same evidence-backed decision: `56531204`
  remained prestart-clean with no output or alternative A100 allocation, so batch remains its sole
  writer. Both the array and single-job terminal watches remain armed.
  Array `56531057` then emitted a mixed error: tasks 0/1 failed before training with
  `ModuleNotFoundError: omnifold`, while task 2 remained pending; no result JSON exists and therefore
  no mechanism verdict is available. All scientific pins match. Changed r2 launchers add the missing
  `omnifold_nn` import path plus a fail-closed import preflight; unchanged retry is prohibited.
  The changed launchers were committed at `783e674`; only then were pending old task 2 and old LR job
  cancelled. Replacement array `56534116` and LR job `56534117` then completed `0:0` in isolated
  namespaces. The changed import preflights and every frozen code/data pin pass. No arm meets the
  predeclared iteration-2 gate (correct sign and achieved/required >=0.90): warm/fresh is wrong-sign
  at 0.663688; cold/fixed is correct-sign but 0.788382; cold/fresh is wrong-sign at 25.065410; and
  the effective `1e-5` annealed-LR arm is wrong-sign at 0.895869. Formally, no arm repairs and the
  predeclared route leaves intrinsic push feedback / representation-tail contraction. A concurrent
  end-state audit found the annealed push is only 1.17% low versus the frozen 5% normalization bar
  (29.39x better than baseline), because it was already 0.24% low after iteration 1; the increment
  criterion degenerates near target. This is a genuine disposition conflict, not a result mismatch:
  normalization repair does not establish shape. Both readings were mailed to Joseph. Branch C and
  every threshold remain unchanged. Joseph authorized the isolated powered-closure shape validation,
  but first attempt `56547490` failed before training: protocol and import preflights passed, then the
  diagnostic subclass hid the base constructor's `early_stop` signature and the driver raised
  `KeyError`. No recovery or LR proof exists, so neither predeclared shape reading was evaluated. The
  changed isolated-wrapper repair preserves the inherited signature and adds a fail-closed signature
  preflight; focused and live compute tests pass. The shared engine remains byte-identical and no
  promotion is authorized. Changed A100 batch attempt `56552326` completed training and persisted all
  six fits, report, and row/weight artifact, but exited `3:0` because the driver propagated its retired
  recovery>=0.80 self-check before manifest creation. Recomputed recovery is **0.512603276**: the
  PRIMARY adopted 0.494582400 criterion passes by 0.018020876, while the SECONDARY
  0.546853+/-0.02 band says TRADE-OFF/REJECT. The disagreement is the predeclared finding. A CPU-only,
  no-training finalizer job `56562169` is running on a shared CPU node to perform the authoritative
  dump/artifact re-derivation and independently verify the committed dual-rejection quarantine proof.
  Its terminal and queue-latency watches are armed. Branch C, shared engine, thresholds, and promotion
  status remain unchanged.

- The three 2026-08-04 full-event blockers now have one canonical decision record:
  `docs/orchestration/DECISION-20260804-B4-STEP3-RECEIPTS.md`. It fixes the estimator contract
  (`w_reco` Step 1, `w_truth` Step 2), target/closure architecture, and construction-receipt
  lifecycle. **D1, D2 and D3 are IMPLEMENTED and Gate-2 is RE-ISSUED as of 2026-08-05** (job
  56344268, PASS, R = 1.1240802949941018, occupied_cells 231/285, B-4 resolved on the reco leg;
  numbers in `../VALIDATION_LEDGER.md`). Every live Gate-2 pin is satisfied. **P5A training remains
  prohibited**, now for one stated reason rather than several: Gate-4 cannot PASS until the D2 powered
  injected-truth-reweight recovery closure has run, because the ordinary closure is an identity check
  that a constant estimator optimizes. The verifier's remaining 8 mismatches all come from
  `p3f-pet-gate4-launch-code-gate-20260801b.json` and resolve when Step 2b re-issues that gate.
- RESTORE Step 5 is closed: both Delta recoil-only `xps2` insurance products
  have a hash-verified durable CFS copy. Exact destination evidence is indexed
  by `../docs/orchestration/state/restore-step5-delta-durability-20260804.json`;
  this does not advance the full-event Gate-4/P5A result.
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
