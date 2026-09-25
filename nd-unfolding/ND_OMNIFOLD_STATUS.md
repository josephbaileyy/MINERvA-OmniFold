# N-D OmniFold (4D q3 / 5D W / PET / FPS) — Status

**PET improvement campaign complete, 2026-09-25:** a diagnosis with measured limits, not an adoption. On fresh simulated pool-F events (12 replicates) the efficiency-corrected step 2 at k = 10 recovers **0.786** of the injected E_avail displacement (lower 95 % 0.763) against the unchanged 0.556 floor, versus 0.316 for the historical recipe; iterations alone reach 0.505 and the reco-summary inputs 0.569. But on the predeclared stress set (pool T) that estimator **moves away from the target** under an identifiable proton-multiplicity change on both replicates, and the feature arm does so under neutron multiplicity, so **no candidate qualified for the coverage study and none was run**. The historical `NEITHER_ELIGIBLE / NO_SELECTION` verdict and thresholds stand; no real data unfolded. [Report](pet/improvement_campaign/REPORT-20260922.md) §11–12, [results](pet/improvement_campaign/confirm/CONFIRM_RESULTS.md), [deck](pet/improvement_campaign/slides/campaign_comparison_v2.pdf), draft PR #3. 268.3 GPU-h.

**PET recommendation delivered, 2026-09-18:** tail validation executed and stopped at its authorized limits -- 4 submissions, 0.773 of 1.5 GPU-hours -- with **10 of 13 widths released and no hard stop at any width**, covering 0 to 160 objects in a family. Three widths failed the finite-difference check alone, and that is a step-size artifact rather than a wrong gradient: at the worst coordinate the estimate converges on the analytic value as h falls (1.84e-2 at the frozen 1e-2, 3.14e-4 at 1e-3, rising again below), the signature of truncation. **The criterion was not relaxed**; releasing those widths needs an amended per-coordinate step rule, which is Joseph's call. Because the pilot was conditional on COMPLETE validation, it was not launched. [Recommendation for Ben](pet/direct_token_comparison/RECOMMENDATION-20260918.md): **keep family pooling** as a practical default -- no accuracy difference detected, cheaper, and flat in multiplicity where individual routing costs 1.244x at the operating point and 1.879x in the tail -- and **test aggregation before routing**, because production truncation discards a median 21-45% of cluster energy in 64-84% of events while aggregate overflow costs 1.007x. Also measured: where cross-device agreement fails at high multiplicity, pooled and individual fail equally. No adoption, no publication claim. Campaign total 16.0 of 290 GPU device-hours.

**PET tail-validation plan for approval, 2026-09-18:** Joseph chose GPU-only tail validation over restricting the study to low multiplicities, declined a blanket exemption, and held the pilot. [The plan](pet/direct_token_comparison/TAIL_VALIDATION_PLAN-20260918.md) names the one requirement that changes -- the CPU-vs-GPU comparison of post-Adam-step weights at `optimizer_equivalence.py:83-97` -- drops it as a requirement while **recording** it as a measurement, and replaces what it was protecting: a float64 Adam reference extended from one weight to all 42, finite-difference gradients, permutation invariance, arm-symmetry of the numerical residual, and overlap calibration where the cross-device gate still passes. What stays unprotected is an arm-symmetric systematic error, which cancels in a paired contrast but not in absolute closure, so absolute numbers keep a device-dependence caveat the contrasts do not. Checks run through the runner's own entry point and training refuses to start without a covering validation receipt. Allocation 0.8 GPU-h expected, **1.5 ceiling**, 4-submission cap, with receipt-less failures counted against the allocation. **Four interpretation corrections applied**: neither direction nor magnitude transfers automatically; noise-only generic inputs establish no upper bound; a null B-A does not retire C-B; and the 25.8-point scatter is a planning assumption, not this endpoint's power. Nothing launched.

**PET preparation measured, 2026-09-18:** A1, A2 route 1, A3 and A5 executed within their approved limits; no pilot and no Stage 2 launched. **The reco cap is not trimming a thin tail.** Pre-truncation non-muon clusters average 74.6 (data 1B) and 102.6 (MC 1A) against a cap of 12, the cap binds in 64.1% and 84.4% of events, and the discarded clusters carry a median 21% and 45% of cluster energy -- the note's 11.09 / 11.15 are POST-truncation means over a selected sample and saturate against the cap. Blobs average 11-12 per event (median 4-6, max 158), so pooling a family at production multiplicity sums 4-6 embeddings rather than the finished matrix's two. Measured GPU cost: arms A and D agree to 0.7% (identical token counts, so aggregate overflow costs nothing to buy), pooled typed objects are free within noise, and individual routing is the only priced arm at **1.244x** training / 1.257x inference at the operating point, rising to 1.879x in the tail. The cross-device gate passes to 18 objects in a family and fails from 24 up, with both controls landing; notably the FIRST failure hits the POOLED arm, so the discrepancy is not a property of individual-object routing. [Go/no-go packet](pet/direct_token_comparison/GO_NO_GO-20260918.md): go at the operating point, no-go on the measured tail. A4 awaits ratification of [the endpoint spec](pet/direct_token_comparison/ENDPOINT_SPECIFICATION-20260918.md). No learning result and no closure number.

**PET representation proposal and a correction, 2026-09-17:** the next comparison is *specified and unexecuted* — no compute requested or launched. Two measurements reframe it. (1) The finished matrix's treatment was **one token in sixteen**: the cloud is 1 event + 12 noise-only generic tokens + 3 pooled family tokens versus 4 object tokens, and pooling is a deep-sets sum over two `raw_pid`-distinguishable prongs, so its near-null result was structural rather than surprising. (2) **We already truncate.** The production estimator's clouds are energy-ranked and truncated to 12 tokens (`docs/analysis-note/sec_pet.tex:56-57` at `66d35706`); the truth leg is comfortable (mean 4.57, 2.31% at the cap) but the **reco leg sits at the cap** (mean 11.09 data / 11.15 MC). This **corrects** the earlier report claim that "our implementation applies no cap at all", which is true of `typed_token_comparison.py` and false of production; aggregate overflow is therefore a candidate repair for a truncation we already apply, not a compression we would have to introduce a cap for. [Bounded two-stage proposal, decision rule and 90 GPU-hour ceiling](pet/direct_token_comparison/COMPARISON_PROPOSAL-20260917.md); it is blocked on the variable-length cross-device gate and needs Joseph's and Ben's agreement before any execution. No new learning result. **Revision 2** replaces the arms after tracing production end to end: the cap that binds is on the **generic cluster cloud**, not on a typed family, so the arms are now four single-factor changes from the actual incumbent (generic-only truncated; +typed pooled; +typed individual; generic aggregate-overflow), with the endpoint, 10-point margin, equivalence band and t-based sizing on one scale, a diagnosis ladder in place of "invalidates the fixture", and cost remeasured at the proposed multiplicities -- pooling's step cost is flat in multiplicity (27.2 to 30.0 ms over an eightfold object increase) while individual routing's is not (27.8 to 65.1 ms). [Exact approvals needed](pet/direct_token_comparison/DECISION_PACKET-20260917.md).

**PET routing comparison complete, 2026-09-17:** the frozen 24-job paired matrix ran to completion (array `58397664`, all tasks `COMPLETED 0:0`, full integrity verified) and returns **NO_PASS** under the unchanged criteria. Individual-object attention shows a median **+9.7%** closure improvement over family pooling, six of eight seeds favourable, but a 95% interval of **[-20.7%, +22.4%]** and paired **p = 0.50** — **no measurable accuracy difference in either direction**. The design is underpowered for its own +5% criterion: ~**209** paired seeds would be needed against the observed 25.8-point seed scatter. Cost is clean on both sides: direct is **1.118x** pooled at training (Wilcoxon `p = 1.2e-07`) and **1.283x** at inference (job `58467879`, all five benchmark criteria passing). One safeguard (`shuffle-71` projections) failed marginally. This is synthetic method development on a uniform four-object fixture; it does **not** compare our pipeline against Gregor's and does **not** settle high-multiplicity overflow. [Report](pet/direct_token_comparison/REPORT_FOR_BEN.md). This supersedes the older execution posture below.

**PET comparison, 2026-09-16:** the amended GPU preflight and calibration both passed (job `58395631`, COMPLETED, 426 s). Seven of eight preflight pairs PASS; `variable/direct` is recorded as `FAILED-STRESS` under the [gate-scope decision](pet/direct_token_comparison/STRESS_SCOPE_AUTHORIZATION-20260916.md), which exempts that stress geometry for this frozen synthetic campaign only and pairs the exemption with a runtime check that every production batch uses the covered geometry. All seven 20% resource gates PASS, so the frozen 24-job matrix was released by its own gates and submitted as array `58396676` at `d98d94cc`. [Calibration evidence and released-matrix record](pet/direct_token_comparison/CALIBRATION_RESULT-20260916.md). **No learning winner is measured**, and the cross-device discrepancy is a float32 reproducibility property of longer attention sequences, not evidence that individual tokens are scientifically worse. This supersedes the older execution posture below.

**PET comparison terminal update, 2026-09-15:** the amended GPU preflight ran as job `58354898` and FAILED after three of the four reached case/routing pairs passed. `variable/direct` diverged at the attention `query/kernel` (`max_abs=1.55e-04`), a tensor the approved key-bias exemption does not and should not cover. Calibration never started: there is no headroom verdict, the frozen 24-job matrix stays unreleased, and the separately specified overflow contrast cannot execute because it is conditioned on measured calibration headroom. No retry is authorized; conservative charge is 1,021 seconds. [Terminal evidence and the untested reduction-order hypothesis](pet/direct_token_comparison/AMENDED_RESULT-20260915.md); [bound overflow specification](pet/direct_token_comparison/OVERFLOW_SPECIFICATION-20260915.md). No learning winner is measured. This supersedes the older execution posture below.

**PET comparison continuation, 2026-09-15:** the approved optimizer gate is implemented; complete CPU preflight, original initialization and fresh reload pass. The bounded GPU preflight/calibration is authorized but not yet launched. [Preparation](pet/direct_token_comparison/AMENDED_PREPARATION-20260915.md) and [continuation scope](pet/direct_token_comparison/BEN_COMPARISON_AUTHORIZATION-20260915.md). No learning winner is measured. This supersedes the older execution posture below.

**PET optimizer diagnostic, 2026-09-15:** job `58320923` completed. A captured masked/direct weight discrepancy is explained by Adam amplification of tiny gradients in redundant attention key bias; all prediction and common-operand optimizer checks pass. The prior variable/pooled failure is not reproduced because the initialization sequence differs. [Evidence and limitations](pet/direct_token_comparison/OPTIMIZER_RESULT-20260915.md). No gate change, calibration or learning matrix is released.

**PET terminal update, 2026-09-15:** full-FP32 job `58301971` failed an updated-weight CPU/GPU check after both nominal cases passed. Calibration and full matrix remain blocked; no retry was launched. [Verified result and limits](pet/direct_token_comparison/FP32_RESULT-20260915.md). This supersedes the older execution posture below.

**PET representation comparison, terminal update 2026-09-12:** retry `58201775` passed 49 tests plus 10 subtests and an A100 operation check. The pooled calibration arm saved artifacts; the direct arm failed during model construction because GPU `DenseBincount` does not support the required determinism. [Exact result](pet/direct_token_comparison/RETRY_RESULT-20260912.md). This second technical failure stops execution: no full jobs or third attempt, and no paired learning conclusion. Source semantics remain unresolved.

**PET typed-descriptor continuation, 2026-09-10:** reconstruction-side prong
definitions and their implementation implications are recorded in
[the semantic reference](pet/PRONG_BRANCH_SEMANTICS.md). The v2 prong contract
repair passes local synthetic software checks. The bounded
[source-validation and normalization protocol](pet/SOURCE_VALIDATION_NORMALIZATION_PROTOCOL.md)
has an implemented checker and bound launcher. The first authorized source
attempt was interrupted. The revised synthetic Linux runtime preflight passes all 8,192 rows and 512
chunks at `ca34a03a`, with four observed threads and a derived rounding budget; see
[the runtime record](pet/SOURCE_AUDIT_RUNTIME-20260910.md). The single authorized
repaired real-source audit (allocation `58186616`) is COMPLETE with `mapping=PASS`,
`semantic=DISCREPANCY` (five out-of-window prong times), `release=RELEASE_UNVERIFIED` and all
object families `UNRESOLVED`; see [the result record](pet/SOURCE_AUDIT_REPAIRED_RESULT-20260910.md).
Its grant is consumed. Preparation and synthetic-check details
are in [the source-audit runbook](pet/SOURCE_AUDIT_RUNBOOK.md). Normalization and training remain separately gated by
[the typed-descriptor status](pet/TYPED_DESCRIPTOR_STATUS.md#next-bounded-task).
PET remains diagnostic/method-development under `OI-126`; this documentation
supplies no new covariance, coverage evidence, or compute authorization. Older
PET execution narratives below do not define this continuation task.

**Last updated**: 2026-08-14. Narrative lives in `ND_OMNIFOLD_RUN_LOG.md`,
verified numbers in `../VALIDATION_LEDGER.md`, bugs in `../KNOWN_ISSUES.md`,
and work remaining in `../docs/OPEN_ITEMS.md`.

**Gate 5 coherent-replica training family is PROMOTED PASS at 50/50.** Job `56933831` independently
confirmed the bare full-strength `FAMILY_COMPLETE_PASS` and returned
`GATE5_TRAINING_ARTIFACTS_PASS`: 50/50 NPZ members, exact fixed subsample, 2+4 realized LR fits,
full/subset signal factors, full background factors, bindings, logs, accounting, and collision
isolation all pass with zero failed checks. `C_stat` remains null; the next action is full-input
per-replica extraction followed by a complete 50-member manifest. That dedicated extraction path is
now implemented and acceptance-tested (184/184 after the terminal repair, plus a real 49,152,885-row factor replay) without
editing the Gate-4-pinned nominal extractor. The first submission created no job because 64 GiB made
Slurm bill 38 cores against the 32-core/GPU queue cap; the changed launcher now uses the accepted queue
default. Array `56935552_[0-49]` then exposed a changed launcher defect: replica 0 finished its complete
49,152,885-row push but xsec lookup incorrectly rooted the off-repository flux file in the immutable code
worktree. No xsec/summary/receipt was published. The array was canceled before the remaining identical
failures; original after-any validator `56935553` and its watch are preserved to record the partial-family
BLOCK. That validator has now returned the expected atomically marked `GATE5_EXTRACTION_FAMILY_BLOCKED`
at 0/50: member 0's r2-bound final products are correctly rejected by original-family job/HEAD/code pins,
and members 1-49 have no original extraction products. A changed continuation explicitly binds the canonical data-root flux and reuses only atomically
complete pushes after validation. It is now submitted as array `56936015_[0-49]` from immutable HEAD
`2f65a36`, with changed after-any manifest `56936016`; both terminal watches are armed. Replica 0 is the
only pre-existing complete push. `C_stat` remains null. Exact active receipt:
`../docs/orchestration/state/gate5-extraction-r2-active-56936015.json`. Exact failure receipt:
`../docs/orchestration/state/gate5-extraction-failure-56935552.json`. Exact original-manifest BLOCK:
`../docs/orchestration/state/gate5-extraction-manifest-block-56935553.json`. Exact training promotion receipt:
`../docs/orchestration/state/gate5-training-family-promotion-56933831.json`.

**Gate 6 PET ML ensemble is BLOCKED by its predeclared no-training convergence control.** Array
`56847059_[1-5]` completed `0:0` in all five members with Gate A/B, reproduction, code pins, and the
archived target hash all verified. Applying only numeric `end_to_end_achieved_over_required`, member 1
passes; members 2–5 fail the required non-increasing absolute-deviation trajectory, and members 2, 4,
and 5 also end above `0.10`. The five-member family therefore fails as a unit. No passing subset is
selected, no `C_ML` is constructed, the nominal central is unchanged, Leg 2 is not started, and no
unchanged retry is allowed. Gate 4's estimator-arm disposition remains an independent user decision.
Canonical numbers: `../VALIDATION_LEDGER.md`; exact receipt:
`../docs/orchestration/state/gate6-member-trajectories-result-56847059.json`.
**The retry design is AUTHORIZED by Joseph (2026-08-14) and Gate 6 REMAINS BLOCKED; nothing in it is
executed by this authorization and it constructs no `C_ML`:**
`../docs/orchestration/PLAN-20260813-gate6-cml-retry-design.md`, recorded verbatim at
`../docs/orchestration/AUTHORIZATION-20260814-gate6-retry.md`. **All five prohibitions at `19585b7` remain
live and none is cleared** — `do_not_retry_unchanged` forbids an *unchanged* retry, so a changed retry was
never in its scope and there was nothing to lift; what the authorization supplies is the user go to spend
compute. **Leg 0 (inference-only, no training) comes first by the PLAN's forced ordering; Leg X remains
authorized-in-readout, held, and unsubmitted; `C_ML` still needs a separate decision Joseph has not made.**
The mediator sequences the legs, not a lane.
**LEG 0 IS SUBMITTED AS ARRAY `56993778_[1-5]` (2026-08-15T04:28:48Z, all five `PENDING` per `squeue -j … -r`;
job identity read from `squeue`, not from `sbatch`'s stdout) AND GATE 6 REMAINS BLOCKED.** `g6_leg0_tier`,
inference only, 01:00:00, 1 GPU, `qos=shared`. Code from `692c6bd`; runs from its own checkout
`/pscratch/sd/j/josephrb/gate6-leg0-fa14db5` (`HEAD fa14db5`, 0 dirty, `692c6bd` an ancestor) because **the
science repo cannot supply the commit** — `683bdcc`, 751 uncommitted paths, `692c6bd` absent (`OI-74`). Both
frozen trees re-verified byte-unchanged after the clone and `verify_hash_bindings.py` returned `ALL BINDINGS
INTACT` before and after; **nothing was re-pinned.** **Whatever it returns, member 3 is NOT promoted, selected
or excluded, the family still blocks on 2/4/5, and all five prohibitions stay live** — Leg 0 can only change
the fault description the retry must explain, from four real failures to three, and only if the measured tier
gap exceeds `0.0010978917643007513` (re-derived from the `56847059` receipt, not quoted). Three of the four member
failures are robust — member 3's sole failing margin is `+0.001098` at the one trajectory step that
compares a best-epoch checkpoint against a `_final` one (VL122–VL126), so **the family still blocks**.

**Leg F, the across-process floor at the fixed `(42,0)` policy, is RUNNING and has NO verdict.** Array
`56863958_[2-5]%2`: tasks 2 and 3 `COMPLETED 0:0` and pass all eight predeclared validity clauses,
tasks 4 and 5 are priority-starved on a contended partition. At `n=3` of 5 the branch
`FLOOR_SMALL_TRAJECTORY_IS_SEED_DETERMINED` is already unreachable, by monotonicity of `max−min` alone;
the other two branches are live. **Gate 6 is not unblocked by this leg and the five prohibitions at
`19585b7` are untouched** — it is a measurement at one fixed seed pair, which is why it proceeds under
`do_not_retry_unchanged`, and `C_ML` needs a separate decision from Joseph that he has not made. The
`{42,46}×{0,4}` 2×2 (Leg X) is authorized and deliberately **not** submitted until the floor completes.
Numbers VL127–VL129; receipt `../docs/orchestration/state/gate6-floor-replication-partial-56863958.json`.

**Leg X is predeclared and NOT submitted.** Joseph fixed the readout at **iteration 2 only**, one run per
cell, no replication — because Leg F measured the same-seed spread at 89.6% of the five-member spread at
iteration 0 against 15.1% at iteration 2, so **the restriction is what makes an unreplicated 2×2 sound
rather than a limitation of it**. Two of the four cells already exist (`member_1`, `member_5`) and are
read-only; only `(42,4)` and `(46,0)` would train. The threshold is `t_{0.975,4} × F_sd[2]` — fixed now,
`σ̂` substituted from the closed floor — and a null ships its MDE. `sbatch_pet_fullevent_legx_2x2_array.sh`
**refuses to start** until a Leg F receipt shows `n=5`, zero invalid draws and a terminal verdict, so
"floor first" is a mechanism rather than a promise. Rule:
`../docs/orchestration/PREDECLARATION-20260813-gate6-legX-2x2.md`.

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
  (`evidence/prepublication-2026-08-20-0b329e8a:docs/orchestration/FINDING-20260811-trajectory-label-is-direction-blind.md`). Full entry:
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
