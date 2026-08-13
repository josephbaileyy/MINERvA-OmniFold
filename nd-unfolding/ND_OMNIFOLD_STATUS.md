# N-D OmniFold (4D q3 / 5D W / PET / FPS) — Status

**Last updated**: 2026-08-13. Narrative lives in `ND_OMNIFOLD_RUN_LOG.md`,
verified numbers in `../VALIDATION_LEDGER.md`, bugs in `../KNOWN_ISSUES.md`,
and work remaining in `../docs/OPEN_ITEMS.md`.

**Gate 6 PET ML ensemble is measured, not promoted; the no-training convergence control is
predeclared.** Array `56834281_[1-5]` completed `0:0` in all five predeclared members with all
persisted realized seed pairs confirmed. The literal comparison passes, but does not establish that
Gate 6 resolved estimator variation. The preserved PET owner returned
`BLOCK_FOR_PREDECLARED_CONTROL`: keep the nominal central, construct no `C_ML`, and apply one uniform
numeric iteration-trajectory rule to all five members. Every isolated three-iteration checkpoint
inventory is complete; execution is defined in
`../docs/orchestration/PREDECLARATION-20260813-gate6-member-trajectories.md`. Gate 4's estimator-arm
disposition remains an independent user decision. Canonical numbers: `../VALIDATION_LEDGER.md`;
exact result receipt: `../docs/orchestration/state/gate6-ml-ensemble-result-56834281.json`.

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
| Standard 5D endpoint set | Ten lateral endpoints re-unfolded and published (job `56495756`); reproduce the 07-18 reference 10/10 (worst per-bin 1.83e-11, worst integral 2.87e-12). Packet B PB1-PB5 **PASS** on real-state/code evidence at `1440b58`, including production resume closure and explicit-null fail-closure. The mechanical field sweep now captures the two unquoted-value PB2 receipt fields. The candidate still **self-declares non-adoptable**; Packet B PASS is not adoption | `active_universe_5d/standard/unfolds/`, `.../evidence/`, `../docs/orchestration/state/p4-packetb-final-pass-20260811.json` |
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

- Branch C annealed checkpoint trajectory: the four-GPU interactive twin `56693776` failed before
  producing any control or treatment receipt because a bare `srun` inherited four tasks; three ranks
  failed Horovod GPU selection and the remaining rank was terminated after entering ARM 1. This is
  **NO SCIENTIFIC VERDICT**. The committed one-task batch twin `56691812` was the sole valid
  route with terminal coverage. ARM 2 remains unread unless ARM 1 reproduces the committed anchors;
  the verdict uses only `end_to_end_achieved_over_required`, and any `|required-1| < 0.02` is
  predeclared UNRESOLVED. The launcher now refuses multi-rank steps before TensorFlow or output setup.
  **LANDED 2026-08-11 — this bullet is no longer in flight, and is banner-corrected rather than
  rewritten so the "is RUNNING" claim above is visible as the stale one it became.** `56691812`
  COMPLETED `0:0` in 21:45. ARM 1 reproduced the committed `56445883` anchors bit-exact
  (`rel_dev = 0.000e+00`), so ARM 2 was read. Both predeclared release conditions held: the verdict was
  taken from `end_to_end_achieved_over_required` only, and `|required-1|` was 0.1241 / 0.0992 / 0.0319,
  all above the 0.02 floor, so the UNRESOLVED guard did **not** fire. Control e2e ach/req
  0.9721 / 0.8608 / 0.6554 with iterations 1-2 wrong-signed; annealed 1.1101 / 1.0329 / 0.9644, all
  correct-signed. **Predeclared branch REPAIRED**: the defect does not survive the fit-time LR anneal.
  Numbers are the receipts' own (`STEP1_TRAJECTORY.control-prenneal.slurm-56691812.json`,
  `STEP1_TRAJECTORY.slurm-56691812.json`), not the arms' stored verdict strings — ARM 2's label reads
  `UNDER_ACHIEVES_AT_ITER0_SAME_SIGN`, which is direction-blind and must not be quoted
  (`docs/orchestration/FINDING-20260811-trajectory-label-is-direction-blind.md`). Full entry:
  `VALIDATION_LEDGER.md` §2026-08-11. This does **not** lift Branch C and promotes no cross section.
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
  iteration dynamics. **LABEL AND MAGNITUDE RETIRED 2026-08-10/11, kept here as the record.** That
  label was retired in `step1_increment_trajectory.py`'s own `verdict_label_history` and the "within
  9.74%" reading is the first-leg field now named
  `r1_achieved_over_required_FIRST_LEG_ONLY_NOT_LIKE_FOR_LIKE`. End-to-end, iteration 0 **undershoots**
  by 2.8% (0.9721), so `CORRECT` overstated it and the first-leg field inverted the sign of the
  deviation. **The wrong-sign claim at iterations 1-2 survives end-to-end; the magnitudes do not.**
  Corrected label `RIGHT_SIGN_AT_ITER0_INVERTS_LATER`, measured by `56691812` above; see
  `docs/orchestration/INDEX-retracted-and-superseded-values.md`. Three full-input controls are ready in isolated namespaces: warm/fresh split,
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
  no-training finalizer job `56562169` completed `0:0`: all 31 authoritative powered-closure checks
  and all 47 total checks pass, with maximum spectrum re-derivation difference `5.898e-12` versus
  `1e-9`. Exact hashes, disjoint split, Gate-2 identity, source provenance, six fit-time LR records,
  and both quarantine rejection conditions pass. Branch C, shared engine, thresholds, and promotion
  status remain unchanged. The next gate is Joseph's explicit promotion/remediation disposition.

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
- Annealed production nominal attempt `56563092` was scientifically null: the
  completed pre-anneal canonical artifact triggered the correct no-clobber
  guard before any fit. Changed job `56563761` completed `0:0`; nominal/floor
  deviations are `-0.035608971` / `-0.035482196`, outside the predeclared
  reproduction window with only `0.000126775` scatter. Optimizer readback proves
  the anneal ran, so the frozen verdict is a systematic code-path disagreement.
  Baseline remains unchanged; no downstream action or promotion occurred. The
  exact next experiment/disposition is blocked on Joseph.

## Presentation rule

Use central values, closure, anchors, and shape-level observations normally.
Use a corrected uncertainty or significance only if it has a committed ledger
entry and passed all gates. Otherwise label it preliminary/support-limited or
omit the number. Never substitute the quarantined historical value.

Execution details and live jobs: `CORRECTED_UQ_PRODUCTION_STATUS.md`.
