# Publication PET UQ remediation status and ordered DAG

**Scope:** the publication full-event PET estimator
`pet-fullevent-fps-v1`. Current completion remains indexed in
`../docs/OPEN_ITEMS.md` and `ND_OMNIFOLD_STATUS.md`; verified numbers belong
only in `../VALIDATION_LEDGER.md`; chronology belongs in
`ND_OMNIFOLD_RUN_LOG.md`.

This file is an execution gate, not proof that a node passed. The exact feature
schema and joint-UQ definition are in
`pet/FULL_EVENT_FEATURE_CONTRACT.md`; the packet/commit contract is in
`../docs/PUBLICATION_COMPLETION_RUNBOOK.md`.

## STATUS 2026-08-14 — P5A annealed extraction is REPAIRED and UNSUBMITTED; `56978466`'s push payload survives and is reused

`56978466` FAILED `6:0` at `00:12:57` on `ModuleNotFoundError: No module named 'ROOT'` — **not** a physics
or identity fault: `G0`–`G5` all passed and the reweight had already completed `49152885/49152885`
(subsample agreement `2.554e-05` vs `1e-3`). `pet/sbatch_p5a_fullevent_nominal_extract.sh` now runs the
two-environment split proven at 50/50 by `pet/sbatch_gate5_replica_extract_array.sh` (read as a template
only; it is receipt-hash-bound), with `G6` reusing the surviving push payload by sha pin
(`a1debdb7…bb9c9`) and `G7` preflighting the ROOT import **before any GPU time**. `G0`–`G5` byte-identical.
**No job submitted; the mediator's go is pending. Promotion is NOT authorized** — outputs remain in
`pet/fullevent_nominal_annealed_extraction_unpromoted/` under `MARK=P5A-ANNEALED-UNPROMOTED` with
`NOT_CANONICAL.json`, and this product is **not** the canonical P5A central or reported-bin mask. `BEN-280`.

## STATUS 2026-08-14 — Gate 6 Leg 0 is BUILT and UNSUBMITTED; the tier gap is still unmeasured

`--checkpoint-tier {auto,best-epoch,final}` is on `pet/step1_increment_trajectory.py` (default `auto` =
prior behaviour, zero callers changed) and the new pin is in `pet/sbatch_gate6_leg0_tier_calibration_array.sh`,
which needs a `G6_LEG0_CODE_REPO` checkout that is **not** `gate6-reconcile-56834281`. **No job submitted; no
Gate-6 prohibition cleared; member 3 not promoted, selected or removed; the family still blocks on 2, 4 and
5.** The PLAN's "only a new launcher pin" is wrong — three launchers pin that file and two are receipt-frozen
(`BEN-270`), leaving a sync-time landmine (`OI-123`). Preparation receipt:
[`gate6-leg0-tier-calibration-prepared-20260814.json`](../docs/orchestration/state/gate6-leg0-tier-calibration-prepared-20260814.json).

## STATUS 2026-08-11 — the Branch C iteration-dynamics defect does NOT survive the LR anneal

Job `56691812` (predeclared `831043d`, no training, 21:45): the annealed nominal `56563761` is
**correct-signed at all three iterations**, end-to-end `ach/req` **1.1101 / 1.0329 / 0.9644**, against the
pre-anneal control's **0.9721 / 0.8608 / 0.6554** with iterations 1-2 wrong-signed — reproduced
bit-exactly from the committed anchors in the same job. `push dev` goes from a monotonic divergence
(−2.79% → −13.92% → −34.46%) to a damped oscillation (+11.01% → +3.29% → −3.56%). **Predeclared branch
REPAIRED**, and the domain-of-validity guard the predeclaration called the most likely outcome did **not**
fire (`|required − 1|` = 0.1241 / 0.0992 / 0.0319, all discriminating). So the defect belongs to the
**retired full-LR policy**, not to iterating. Numbers: `../VALIDATION_LEDGER.md` §2026-08-11.

This does **not** lift Branch C (a quotability state, not a number), discharges no cause, and is not a
promotion. Unexplained and new: the annealed arm's **+11.01%** overshoot at iteration 0. The emitted
verdict *label* on that arm is direction-blind and must not be quoted
(`evidence/prepublication-2026-08-20-0b329e8a:docs/orchestration/FINDING-20260811-trajectory-label-is-direction-blind.md`).

## STATUS 2026-08-11 — cause 5's binding half is the JOINT CONSTRUCTION, not the samples

The 120 selection-shifted **full-event** lateral endpoint ROOTs exist, are `g2-fullevent-v1`, and were
promoted `GATE3_PROMOTED_PASS` on **2026-07-20** (120/120 receipts `PASS`, 1.1 TB, now being archived to
HPSS by job `56692312`: **240/240** objects (120 ROOTs plus 120 Gate-3 receipts) have matching local and
server-side HPSS MD5 plus size readback, with zero missing entries). So the *selection-complete detector
samples* half of quarantine cause 5 is satisfied **and protected off purgeable scratch**, while the **joint nuisance/retraining construction is the
binding half** — it does not exist in any form, and the construction that does exist is the additive
`C_syst + C_retrain` that cause 5 names as the defect, measured this session to **overstate** the joint
covariance by `1.786`× on the knob bands with a negative cross term in every universe. Cause 5 remains
**OPEN**; a written discharge criterion for it now exists (there was none anywhere):
`../docs/orchestration/DETERMINATION-20260811-cause5-binding-half.md`.

Archive terminal receipt:
`../docs/orchestration/state/hpss-protect-p3f-complete-56692312.json`. The digest-based resume guard
found no unverified object, so no archive retry is authorized or needed.

Do not read `KNOWN_ISSUES.md` #19 as "no full-event anything exists". No full-event **product** exists;
the full-event **inputs** do.

## Legacy boundary

The completed recoil-only PET nominal, floor, ensembles, and covariance are a
non-publication representation cross-check. Existing recoil inputs and scalar
purity-weight targets are not inputs to this DAG. Optional legacy replica work
uses its own namespace and cannot satisfy, feed, or delay any gate below. Do not
rerun completed legacy products to repair documentation.

The reduced full-event interface estimator `pet-reduced-fps-cross` is likewise
an interface/stress-closure cross-check. It cannot provide a central value,
lateral endpoint, or covariance component for `pet-fullevent-fps-v1`.

## Gate 0 — durable controls and ownership

Before any publication PET compute:

1. The locked background decision, full-event contract, dependency map, and
   runbook are committed and independently verified.
2. G2 has a named C++ owner. Existing event-loop jobs using the current binary
   have drained, the owner has handed off the source, and only one coordinated
   installed-binary rebuild is planned.
3. Output namespaces distinguish reduced/recoil controls, purity controls,
   full-schema candidates, and adopted products.
4. Every launch has an interactive-versus-batch decision based on live queue,
   resource, dependency, remaining-wall, and output-ownership evidence. No two
   jobs may write one namespace.

**Gate:** scoped control commit and independent publication-plan PASS.

## Gate 1 — G2 full-schema FPS CV input

**Current (2026-07-19): Gate 1 PASS.** Gate 1A per-playlist production and the
Gate-1B merged ROOT/full-schema NPZ are complete. Recovery job `56120687`
published the receipt-last P=12 NPZ; an independent validator recomputed its
SHA-256, all 42 member headers, three inventory identities, retained-domain
predicates, miss sentinels, extended edges, POT relationship, and source/code
bindings with zero failures. All twelve hash-bound ROOT/receipt pairs passed one
terminal validation, including exhaustive retained-domain receipts for recovered
1D/1E/1F/1P. Aggregate truth and signal rows are exactly equal at 49,906,108.
The no-clobber MEFHC merge passed exhaustive validation and binds 21,797 finite
out-of-domain rows for exclusion; the independently reviewed dumper enforces
`[0,30] x [0,120]` GeV before inventory construction. Gate-1B inventories are
49,152,885 signal, 4,116,128 data, and 564,591 background rows. Evidence:
`nd-unfolding/g2_fullevent/merged/G2_MEFHC_MERGE_RECEIPT.json` and
`docs/orchestration/state/g2-gate1b-npz-validation-20260719.json`. Next: Gate 2
literal `negweight-refined` target construction only; PET training remains blocked.

Regenerate the FPS CV point-cloud event loops and derived inputs with the exact
`pet-fullevent-fps-v1` schema. The source must include aligned data, signal MC,
truth MC, and background MC clouds plus event scalars/features, event keys,
masks/types, POT/weights, native misses, extended-FPS edges, and schema/binary
provenance.

Required proofs:

- `MNV101_FULL_PHASE_SPACE=1` and the declared full-event dump are embedded and
  verified;
- data/reco observable schema parity and distinct truth schema;
- event-key and row alignment, uniqueness, denominator/miss consistency, and
  reconstructed-selection identity;
- exact extended-FPS edges and reported-bin order;
- no truth-only feature enters step 1;
- background clouds carry the same reco schema needed for data-side injection,
  along with aligned `w_bkg`; and
- full-schema fingerprint differs from the reduced/recoil fingerprints.

**Gate:** committed G2 roots/inputs, content summary, interface tests, ledger,
RUN_LOG, and STATUS evidence. Present `xps2` recoil tensors remain scaffolding.

## Gate 2 — literal `negweight-refined` target

**Current (2026-08-13): RE-ISSUED, PASSED, AND FULLY PROMOTED under D1/D2. Both promotion
requirements are closed.**

- **Requirement 2** (ledger + RUN_LOG + STATUS) — closed by **Session C**, the paragraph below.
- **Requirement 1** (independent receipt review) — **PASS**, **Session D**, `V21` in
  `docs/orchestration/VERDICTS-20260811-session-D.md`, committed `dfc716f`. Hashes re-verified in D's
  own tree rather than taken from C; every published binned number re-derived from the receipt's own
  operands; `b4_gated` power-tested seven ways rather than read as prose.
- **The one link D could not close, closed by Session A** — the target `.npy` digest lives on
  `/pscratch` and D has no cluster access, so it rested on the lane that promoted the gate, which is
  what requirement 1 exists to prevent. Measured by Session A (not C), 2026-08-13:
  `G2_NEGWEIGHT_REFINED_EXACT_NORMALIZED.npy` = `544b2f6a2451480abfe867aede35d31a07178d518754428f43b00b26793d54c9`,
  **18,723,004 B** — matching the receipt's own `.step1_feed.weights.sha256` and `.size_bytes`
  exactly. **So no link in the promotion chain rests on the promoting lane.**
- Corroboration from a second instrument, D's: `(18,723,004 − 128) / 4 = 4,680,719` exactly, so the
  file is float32 with a 128-byte npy header — the size confirms the dtype independently of any
  header read.

**Still NOT authorized by this promotion:** promotion of any PET nominal to canonical. Gate 4's
estimator disposition is answered (the **annealed** arm —
`docs/orchestration/AUTHORIZATION-20260813-gate4-estimator-disposition.md`). Branch C stays closed.

> **CORRECTION 2026-08-13, against Session A, which wrote the sentence this replaces.** The prior text
> said *"`nominal_pet_training_allowed` stays **false**"*. **That is false and I propagated it from prose
> rather than reading the gate.** Measured: `nominal_pet_training_allowed` is **`True` in all four
> Gate-4 code-gate receipts** — `…-20260810.json`, `…-20260810b.json`, `…-20260810c.json`, and the newest
> `…-20260812.json` — and has been since 2026-08-10. `evidence/prepublication-2026-08-20-0b329e8a:KNOWN_ISSUES-ARCHIVE-2026-08.md` already recorded
> this correction on 2026-08-11. **The flag was never the blocker.** What Gate 4 needs is a PROMOTION
> decision, and the annealed production nominal (`56563761`, complete, `.done`-marked) carries
> `.predeclared_reproduction.*.verdict = FINDING_CODE_PATHS_DISAGREE`, `artifact_promoted: False`,
> `recovery_evaluated: False`, and `.status COMPLETE_PREDECLARED_FINDING_CODE_PATHS_DISAGREE_NO_DOWNSTREAM`
> — fold-forward `dev = -0.0356090` against the predeclared PASS window `[-0.021724, -0.001724]`,
> computed with the predeclaration's own `(push/R) - 1`. **That is with Joseph.** Read the gate receipt,
> not this file, if they ever disagree again.

**This paragraph replaced a line dated 2026-08-04 that read "RE-ISSUE REQUIRED; no current Gate-2
PASS" and stayed there for eight days after the run that passed.** It was the receipt's own
promotion requirement 2 (ledger + RUN_LOG + STATUS) left unmet, and on 2026-08-12 it caused a lane
to be assigned a week of D1/D2 implementation work that had already landed. A status field is
transition-written, not sampled, so a stale one reads exactly like a true one (BEN-098). **Read the
receipt, not this line, if they ever disagree again.**

- **Run:** job `56344268` (`g2reissue2`), COMPLETED `00:55:32` on `nid004178`, ended
  `2026-08-05T05:16:22Z`. `status: PASS`,
  `verdict: GATE2_CANONICAL_RUNTIME_PASS_INDEPENDENT_PROMOTION_PENDING`,
  `pet_training_started: false`.
- **Product:** `nd-unfolding/g2_fullevent/gate2/final/G2_NEGWEIGHT_REFINED_EXACT_NORMALIZED.npy`,
  4,680,719 rows / 18,723,004 B, sha256
  `544b2f6a2451480abfe867aede35d31a07178d518754428f43b00b26793d54c9` — re-verified on the cluster
  2026-08-13 against the receipt.
- **D1 is GATED, not merely implemented.** `b4_gated: true`,
  `b4_resolution: D1-2026-08-04-reco-leg-uses-w-reco`, `R = 1.1240802949941018` with denominator
  `pot_scale * sum(w_reco[pass_reco])`. A reco leg fed anything but `w_reco`, an absent `w_reco`, or
  a missing telemetry block all `die()` before the receipt is written, so a PASS *asserts* the
  denominator is the reco leg. Implementation landed at `ed4ca72`.
- **D2:** the nominal consumes the target via `assert_target_provenance` in
  `pet/train_fullevent_nominal.py` — receipt-owned, verdict must be PASS, sha256 and size must
  match, with an explicit no-fallback branch naming audit finding J04. The MC-only closure path is
  `bkg_mode='mc-only'` in the loader (`data=None`, no measured target, no ROOT import, rejected by
  `assert_publication_config` for publication runs).
- **The r1 run is bit-identical.** Job `56342333` produced the same target digest and was superseded
  only because its receipt pinned a loader hash later moved by audit repairs — direct evidence that
  edit was semantically inert here.
- **All four sources the receipt pins are byte-identical to HEAD** as of 2026-08-13: loader
  `57f33f87…`, `omnifold_nn/omnifold/dataloader.py` `bed9e0b3…`, validator `13fa4853…`, canonical
  u2d `8ebe0277…`. The product is therefore still bound to the code in the tree.

**Test evidence, and the loader boundary is now covered ON-CLUSTER.** Off-cluster: 92 passed
(`test_d1_dual_leg_weights` + `test_b1_normalization_fix`), and separately 12 + 153 passed / 1
skipped across the dual-leg mutation suite, nominal launcher, B4 gating, B1 normalization and
full-event schema. The mutation tests are two-sided by construction — each perturbation asserts a
movement *and* a non-movement, and a third control perturbs `w_reco` only outside `pass_reco` to
prove `R` sums the mask.

`tests/test_fullevent_gate2.py` and `tests/test_gate2_target_runtime.py` **cannot** run off-cluster
(hardcoded `/pscratch` paths, an `omnifold.dataloader` import) and they are precisely the
end-to-end loader-boundary tests — the surface D1 and D2 meet at — so off-cluster green never
covered the thing most worth covering. **Run on Perlmutter under `tensorflow/2.15.0`: 32 passed in
1.87 s.**

That green means something only because the cluster tree is a fork (at `683bdcc`, with 728
uncommitted files), so the four relevant files were checked byte-identical between local `main` and
the cluster before the result was accepted — cluster halves measured by the orchestrator lane, local
halves re-measured here:

| file | sha256 (first 16) |
|---|---|
| `tests/test_fullevent_gate2.py` | `b1c3c29f1ed183f5` |
| `tests/test_gate2_target_runtime.py` | `3782e096adb0047a` |
| `pet/fullevent_fps_dataloader.py` | `57f33f87b07e0c6b` |
| `pet/train_fullevent_nominal.py` | `5fda80df43dfe334` |

Had they differed, the on-cluster green would have validated the fork and said nothing about `main`.

**Promotion requirement 1 is CLOSED** — independent receipt review, Session D, `V21`. It was
deliberately not self-performed: a lane cannot review the gate it is promoting (`CLAUDE.md`: worker
agreement is not verification).

**I published three places where my own evidence was thinnest, and all three are now closed by
measurement rather than by argument. Recording them closed, with who closed them, because a caveat
that quietly disappears is worse than one that was never raised.**

(i) `b4_gated: true` — I flagged that the claim *"every `die()` path precedes the receipt write"* was
read from the receipt's own prose, not verified in `gate2_target_runtime.py`. **Closed by Session D in
`V21`**, by reading the control flow and power-testing the predicate seven ways rather than trusting
the prose. (ii) `normalized_sum` 1,124,080.5876521247 against target 1,124,080.2949941019 agree to
2.6e-7 — agreement, not identity, and I could not find the governing tolerance. **Closed by Session D
in `V21`**: the tolerance governs at 5.4% of budget and the residual is consistent with float32.
(iii) — **closed against myself, below.**

I wrote that the `mc-only` path was read statically and never executed. **It was executed.** The
powered closure driver `pet/closure_powered_truth_reweight.py` (pinned `a45fae7c…` in job `56552326`'s
receipt, resolving to that file at HEAD) calls `build_fullevent_loaders(..., bkg_mode="mc-only")` at
`:262` and raises `SystemExit("[powered] mc-only returned a measured loader; wrong build path")` at
`:264`. So D2's MC-only construction ran with a fail-closed assertion rather than being a code reading.
Its completion is also runtime evidence for the no-ROOT claim: the job ran under `tensorflow/2.15.0`,
and no interpreter on Perlmutter carries both ROOT and TensorFlow
(`evidence/prepublication-2026-08-20-0b329e8a:docs/orchestration/FINDING-20260804-step3-closure-needs-root-and-tf-in-one-interpreter.md`), so an `mc-only` build that
imported ROOT could not have completed there.

**Feature-schema equivalence is likewise PINNED rather than inferred** (`docs/OPEN_ITEMS.md` OI-23).
Neither the closure nor the nominal driver passes `feature_names`/`truth_feature_names`, both drivers
are pinned by digest, the engine `3a2022b0…` = `omnifold_nn/omnifold/omnifold.py` is the *same object*
in both receipts, and the loader supplying the defaults is pinned `57f33f87…`. Those defaults —
`DEFAULT_EVT_FEATURES` (13) and `DEFAULT_TRUTH_EVT_FEATURES` (2) — compare **equal** to this receipt's
`configuration.features` and `configuration.truth_features`. So the target construction, the closure
and the nominal all select the same 13/2 columns. This matters because feature selection is a choice
made *over* an input: a shared NPZ digest bounds what could be selected and does not pin what was.

**A SECOND, STRONGER MECHANISM on the nominal side — found by Session D, verified here.** Derivation
from pins says the wrong feature set was not selected; a runtime refusal says it *cannot* be. The
nominal driver carries two fail-closed guards, and neither is a branch: `train_fullevent_nominal.py:388`
refuses if the loader's `meta` widths disagree with the blocks actually built, and **`:393` raises
`SystemExit` if the loader built `REDUCED_EVT_FEATURES`** — the 2-column {pT, p‖} schema that
`pet/FULL_EVENT_FEATURE_CONTRACT.md` marks *"CROSS-CHECK ONLY — never a publication lateral/central
source"* — because stamping the publication fingerprint over it is AUDIT-FINDINGS-20260731 J01. So the
exact failure the residual described, a run selecting a different feature set while claiming the
publication estimator, is **refused at runtime, not merely made improbable.** Derivation from pins and
a runtime refusal are different instruments; the guard covers the nominal, the pins cover the closure.

**Naming trap for any reviewer:** `D1`/`D2` in this file and in
`DECISION-20260804-B4-STEP3-RECEIPTS.md` are the B-4 weight repair and the RESTORE Step-3 target
ownership decision. `D1`/`D2` in the powered-closure work are *different things* — commits such as
`f2c5b7d "Powered closure n=3: D2 pass"` are the closure criterion. Confirming the wrong one looks
like a complete review.

**What this does NOT certify.** Construction of the measured target only. Not quotable as a cross
section. Gate 4 must separately prove the nominal consumes this exact array (J04) and cannot PASS
until the powered recovery closure exists.

Canonical decision: `docs/orchestration/DECISION-20260804-B4-STEP3-RECEIPTS.md`. Numbers:
`VALIDATION_LEDGER.md` VL76–VL90 (2026-08-05 entry). Chronology:
`nd-unfolding/ND_OMNIFOLD_RUN_LOG.md` 2026-08-05. Live receipt:
`nd-unfolding/g2_fullevent/gate2/final/G2_GATE2_TARGET_RUNTIME_RECEIPT.json`. Superseded 07-19
evidence: `docs/orchestration/state/g2-gate2-runtime-independent-validation-20260719.json`,
`docs/orchestration/state/g2-gate2-verifier-20260719.json`.

Build the measured-side training inventory from:

- aligned data events with their positive data weights; and
- aligned background clouds with negative POT-scaled `w_bkg`.

Apply the Stay-Positive refinement to that complete signed inventory. Do not
copy scalar purity weights, silently downweight only the data rows, or reuse a
nominal refined target in a bootstrap replica.

The target summary records:

- ordered data and background manifests and event-key alignment;
- POT scale and raw positive/negative sums;
- refinement configuration/fingerprint;
- refined normalization and clipping/floor telemetry;
- finite/non-negative post-refinement weights; and
- estimator ID, feature schema, extended edges, input hashes, and target mode
  `negweight-refined`.

**Gate:** an end-to-end fixture reaches training and extraction; signed and
refined targets reproduce their independently constructed binned checks; all
invalid/missing/misaligned background inputs fail closed.

## Gate 3 — committed full-schema P3F-PET source inventory

**Current (2026-07-20): Gate 3 PROMOTED PASS.** Slurm array `56169838`
(`0-119%16`) reached terminal state with all 120 elements COMPLETED/0:0.
Independent reconciliation confirmed the ownership bijection (120 receipt
JobIDRaw == 120 sacct JobIDRaw, no foreign/missing writer), all 120 PASS
ROOT/receipt pairs (superseded muon-validity checks confined to the frozen
validator's allowed set on playlists 1D/1E/1F/1P), on-disk validator/launcher
hashes matching the bindings, and complete per-task locks/logs/DONE markers.
The complete aggregate manifest
(`docs/orchestration/state/p3f-pet-gate3-source-manifest-56169838.json`,
sha256 `306e5459`) is committed PASS and independently verified by the
owner-neutral agy verifier (rc=0, VERDICT PASS, concurring with the
orchestrator audit). Promotion receipt:
`docs/orchestration/state/p3f-pet-gate3-promotion-56169838.json`.
Nominal PET (Gate 4) remains prohibited pending its own launch-code gate and
explicit user authorization.

Before the publication nominal, regenerate and validate the complete
selection-shifted source inventory under the G2 full schema: five declared
kinematic bands by two endpoints by twelve playlists. Require exact event,
cloud, and background joins; selection/migration census; native-miss and
denominator evidence; source/input hashes; schema and estimator identity;
endpoint/playlist completeness; atomic content validation; and the scoped
commit receipt.

P3S standard endpoints, scalar-FPS purity unfolds, reduced-schema P3F, and
uncommitted full-schema files are controls only. This gate produces validated
shifted inputs, not endpoint-trained covariance. The latter follows the nominal
at Gate 8.

## Gate 4 — nominal and GPU floor

**2026-08-10 one-liner.** The `niter=3` launch-code gate is re-issued with zero binding mismatch, but
`nominal_pet_training_allowed: false` still holds. CLM-012 retired the stale absolute 0.80 recovery
bar: the adopted D2 criterion is `0.80 * 0.618228 = 0.494582`. The full-LR powered closure recovery
`0.546853` therefore passes. The isolated annealed-LR candidate was independently re-derived by CPU
finalizer `56562169`: 31/31 authoritative and 47/47 total checks pass, recovery `0.512603276` passes
the adopted PRIMARY criterion by `0.018020876`, but lies `0.034249724` below the full-LR baseline and
therefore triggers the SECONDARY TRADE-OFF/ARM-REJECTED reading. That predeclared disagreement is the
finding. No engine edit or promotion was authorized; Gate 4 remains blocked on Joseph's explicit
estimator disposition and subsequent nominal-launch authorization. Branch C stays closed.

**Historical status (2026-08-04): launch-code re-issue required; training NOT launched.**
The live code-only receipt predates decisions D1/D2. The present nominal still rebuilds the
Gate-2 target in process, and the ordinary closure builds then discards that measured target;
neither can produce the required evidence as written. The adopted repair is a mandatory,
hash-verified precomputed-target path for the nominal plus an MC-only TF closure path and a
separate powered injected-reweight closure. No combined ROOT/TF publication environment or
two-process closure handoff. See the canonical decision record above.

**Historical launch-code state (2026-07-21): PASS_CODE_ONLY; training was not launched.**
The publication full-event PET nominal launcher
(`nd-unfolding/pet/sbatch_pet_fullevent_nominal.sh` + driver
`train_fullevent_nominal.py`), the Gate-4 validator
(`validate_pet_nominal_gate4.py`), and their tests are built, hash-bound, and
frozen: the launcher/driver route through `fullevent_fps_dataloader`, call
`assert_publication_config` (fingerprint `pet-fullevent-fps-v1`,
`bkg_mode=negweight-refined`, G2 full-schema markers + background inventory,
Gate-2 target `G2_FPS_MEFHC_P12.npz` sha `fa6b3463`, Gate-3 manifest bound),
fail closed on mismatch, and never auto-submit (require `SLURM_JOB_ID`).
`nominal_pet_training_allowed` stays **false** — the training LAUNCH is a
separate post-restore user decision (the 2026-07-22 shutdown precludes a long
GPU job now).

**RE-ISSUED 2026-07-31, AND TWICE MORE SINCE.** The live receipt is
`docs/orchestration/state/p3f-pet-gate4-launch-code-gate-20260801b.json`
(J01/J02/J05 full-event schema). The chain is 20260721 -> 20260731 (Step 2b,
below) -> 20260801 (J35/J10) -> **20260801b (LIVE)**; every earlier one carries
`"status": "SUPERSEDED"` and its hashes under `files_at_issue`. Check that field
rather than trusting a date in prose --- this paragraph named 20260731 as the
receipt for two days after it stopped being one. The B1 §2d patch had voided all five bindings,
and the re-issue was also the window for the audit-B2 validator defects: the
CLI evaluated **none** of its four physics checks (`marginal`, `normalization`,
`saturation_frac`, `closure` were never passed and the report builder silently
skipped any component whose argument was `None`), self-compared four of its six
freeze checks (`frozen_observed` was built out of `FROZEN`), and never populated
`central_vector` / `reported_bin_mask` at all — so it returned `verdict PASS,
0 failed` on `|N(1,0.3)|` noise. Now: absent evidence emits a failing
`<component>:evidence_supplied` check, every value compared against `FROZEN` is
read from the artifact, the two closure reports are required CLI arguments, and
the measured-target provenance (including
`refinement_is_learned_production`) is gated. The legacy truth-level
`check_normalization` primitive is retired. Tests: 13+1s launcher / 62 validator
/ 80 B1 / 93 frozen regressions. **Not independently reviewed** — unlike the
07-21 issue, no second agent verified this; and B-2's agy citation was checked
and found unrecoverable, so it is not carried forward. Four items remain owed —
the measured `fold_forward_ratio_dev_max`, the `stress_closure_muon.py` run
(blocked by TF 2.16/Keras 3 on the local host), the ordinary closure receipt,
and the Gate-2 re-issue.

Train and extract one unbootstrapped publication nominal from the Gate-2 target
using the frozen estimator fingerprint. Freeze its central vector, reported-bin
mask/order, phase-space edges, seed/config policy, and extraction normalization.

Run one matched repeat to bound GPU nondeterminism before interpreting either
statistical or ML ensembles.

Required validation includes ordinary closure, the omitted-muon stress closure,
finite full-coverage weights, strict MC index/order, cap-sensitivity telemetry,
normalization, exact lower-dimensional marginals, and the acceptance-supported
versus prior-dominated reporting split.

**Gate:** committed nominal and floor packets. No UQ component may use a
different central/mask/order/fingerprint.

## Gate 5 — F7 coherent statistical replicas

**Update 2026-08-14 10:02 UTC — ORIGINAL EXTRACTION MANIFEST BLOCKED 0/50.** Original after-any
validator `56935553` completed its intended fail-closed path: accounting is `FAILED/1:0` because the
marked report verdict is `GATE5_EXTRACTION_FAMILY_BLOCKED`, not because publication failed. The marker
matches the 19,393-byte report exactly and stderr is empty. Members 1-49 lack all four original
extraction products. Member 0 is also rejected: changed r2 task 0 had already published repaired products
into the shared member namespace, and the original validator correctly detects its r2 job, HEAD and code
bindings rather than misattributing them to `56935552`. The original family is terminal and unpromoted;
no subset or unchanged retry is permitted, and `C_stat` remains null. Changed array `56936015` continues
under its existing terminal watch. Receipt:
[`state/gate5-extraction-manifest-block-56935553.json`](../docs/orchestration/state/gate5-extraction-manifest-block-56935553.json).

**Update 2026-08-14 09:47 UTC — FIRST EXTRACTION ARRAY BLOCKED; CHANGED CONTINUATION ACCEPTED.**
The emitted error wake corrected its own aggregate-terminal claim: task 0 had failed, task 1 was still
running, and tasks 2-49 were pending. Replica 0's full ordered 49,152,885-row push and atomic marker are
valid, but the xsec stage defaulted the flux path into immutable code worktree `7dc8c34`, where the
off-repository ROOT does not exist. This is a launcher/data-root defect, not a factor, refinement, push,
or science failure. The exact array was canceled so the remaining tasks could not repeat the unchanged
failure. Original after-any validator `56935553` and its watch remain intact and must truthfully BLOCK the
partial family. The changed path passes 184/184 tests, requires an explicit canonical data-root `--mcfile`,
and reuses a push only after its completion marker revalidates. No subset is selected and `C_stat` is null.
Receipt: [`state/gate5-extraction-failure-56935552.json`](../docs/orchestration/state/gate5-extraction-failure-56935552.json).
The repaired code and evidence landed at `2f65a36`; changed array `56936015_[0-49]` now depends
`afterany:56935552`, so no replacement can overlap the predecessor. Changed manifest `56936016` depends
after-any on that array. Both new terminal watches are armed, while original manifest/watch `56935553`
remain preserved. At submission only replica 0 had a reusable complete push; all final products remained
absent. Active receipt:
[`state/gate5-extraction-r2-active-56936015.json`](../docs/orchestration/state/gate5-extraction-r2-active-56936015.json).

**Update 2026-08-14 09:14 UTC — FULL-INPUT EXTRACTION IMPLEMENTATION ACCEPTANCE PASS.** A dedicated
replica adapter leaves the Gate-4-pinned nominal extractor byte-unchanged and calls its engine
reweight, coverage checks and xsec arithmetic. It independently replays the full signal/background
factors, applies the signal factor to both truth counts and completeness/reporting-mask construction,
and publishes a receipt last. The after-any terminal validator requires exactly 50/50 and never
selects a subset. The actual TensorFlow-runtime battery is 181/181 PASS; replica 0's 49,152,885-row
signal draw replays exactly. `C_stat` remains null. Implementation receipt:
[`state/gate5-extraction-implementation-20260814.json`](../docs/orchestration/state/gate5-extraction-implementation-20260814.json).
The first submit call then created no job: explicit 64 GiB raised the request to 38 billed cores against
the queue's 32-core/A100 cap. The changed retry removes that request and uses the same default-memory
footing as accepted Gate-5 training; receipt:
[`state/gate5-extraction-submit-prestart-refused-20260814.json`](../docs/orchestration/state/gate5-extraction-submit-prestart-refused-20260814.json).
Changed submission is active: extraction array `56935552_[0-49]` (A100, `%10`, 2h) writes only
member-scoped `extraction/` namespaces, and CPU job `56935553` runs the 50/50 terminal validator
after any aggregate result. Both terminal watches are armed. `C_stat` remains null. Launch receipt:
[`state/gate5-extraction-active-56935552.json`](../docs/orchestration/state/gate5-extraction-active-56935552.json).

**Update 2026-08-14 08:57 UTC — TRAINING FAMILY PROMOTED PASS after the independent NPZ gate.**
Read-only job `56933831` completed `0:0` with empty stderr. Its full-strength family replay is
byte-identical to the already committed `ca99effa…` report, and the distinct artifact validator returned
`GATE5_TRAINING_ARTIFACTS_PASS`: 50 members present, 50 passing, zero failed member checks, and 111/111
family checks. Its hash-bound promotion marker re-derives the family, artifact, and 50-row accounting
digests. This promotes the complete training family, **not `C_stat`**; full-input extraction and a complete
50-member manifest precede centering on the replica mean. Receipt:
[`state/gate5-training-family-promotion-56933831.json`](../docs/orchestration/state/gate5-training-family-promotion-56933831.json).

**Active 2026-08-13:** target array `56857232_[0-49]` is terminal at 50/50 `COMPLETED/0:0`; all 50
collision-isolated target/receipt/marker quartets are present and a same-turn structural pass reports
50/50 target checks passing. Read-only validator `56872614` failed before validation when its mutable
receipt-writing worktree advanced across the pending interval; no report was produced. Changed job
`56873858` ran from immutable detached HEAD `70be58a` and returned `TARGETS_COMPLETE_PASS`: exact
9.9 GB source hash, 50 targets, and all 150 data/signal/background factor redraws match, with zero
target or family failures. **The target stage is promoted PASS.** Task-correlated training array
`56857233_[0-49]` remains the sole training
writer with its terminal watch armed. The declared ensemble remains invalid until the independent
target verdict and all 50 training receipts pass; the target verdict is now satisfied, while the
training condition is not. No subset or `C_stat` is permitted. Promotion
receipt: [`state/gate5-target-family-promotion-56873858.json`](../docs/orchestration/state/gate5-target-family-promotion-56873858.json).

**Update 2026-08-14 ~06:30 PDT — `OI-122` EXECUTED: the `N=100` predeclaration is RETIRED IN PLACE.**
Joseph's verbatim **"Yes I authorize it"**, committed at `4d28e78` **before** the act per `BEN-082(v)`. I had
declined this an hour earlier on three grounds — the row assigns ratification to Joseph, the act overrides a
committed verdict clause and so is scientific not clerical, and lane B had already declined it — and **all
three held**. **Purely additive: 65 insertions, 0 deletions**, no digest of the file's bytes anywhere
(`BEN-158` checked first), classified `ARCHIVAL` + `superseded` + `canonical_successor` and **deliberately
not `DEAD`**, because a deleted predeclaration is not a predeclaration. **Grounded in AUTHORITY** — the
file's `:10` forbids launching and §4 condition 4 says *"This file is not that authorization"* — **not** in
"50 is precise enough". The header **defuses** the `:73` `INSUFFICIENT` clause (its trigger is *at assembly*
and no assembly occurred under this file) rather than leaving that trap armed, and records that the
document's **quality** branches were **met** by the successor: `SEED LEAK` passes on measurement (50/50 at
`estimator_seed: 42`, `:275` fail-closing), `CENTRING ERROR` passes (replica mean). `INSUFFICIENT` is the
only branch that differs, so the conflict was about inventory size alone. `CSTAT-R7` (action 2) already
carried the `N=50` → **10.1%** disclosure obligation.

**Update 2026-08-14 ~06:10 PDT — `BEN-232` REFUTED BY ME: THE NETWORK IS SEEDED, `C_stat` IS CORRECTLY NAMED.**
The estimator seed is **pinned at 42 on all 50 members and enforced per member** (`:275` fail-closes);
measured from all 50 weights artifacts, one `seed_policy`. My `grep set_seed` **could not match
`set_random_seed`** — the search was structurally incapable of refuting the claim I drew from its silence
(`BEN-235`, and worse than `BEN-234` because a null `grep` feels like a measurement). Refutation applied
everywhere the claim was: `BEN-232` row, its long-form, `SPEC` §8, the contract, and **`OI-92` CLOSED — no
Joseph turn needed.** What survives is `OI-94`, and it is now **DECOMPOSED**: family **4.478%** =
**18.35%** measured process non-determinism (`VL130`, the floor surviving a full seed pin — relabelled by B)
+ **81.65%** unexplained residual (**4.046%**, 82.1× Poisson), shares summing to 100.00% and every figure
re-derived independently. `cap_saturation_frac = 0.0` rules out logit clipping. The residual is plausibly
the learned map's response to the draw — **the legitimate content of `C_stat`** — which neither B nor I
assert. **~18% of the component's variance is non-determinism, not data statistics, and that belongs in the
receipt.** Caveats: 2M-subsample numerator, independence assumed, `n=4` at 40.8% per sd. **`CSTAT-O2a`
RELEASED** with a better shape — it now pins the **with-draw** floor against Leg F's no-draw baseline, so
the difference *is* the map response — **sequenced after `56936015` drains, `nice`d.** **`CSTAT-D4`** writes the `C_stat`+`C_ML` disjointness proof that genuinely was
missing. **`BEN-236`**: the training mask is not constant (`257/258/259`) and its 259 is a **different set**
from the extraction intersection's 259 — a matching count is not a matching set. **`CSTAT-R7`** requires the
`N=50` → **10.1%** precision disclosure in the receipt.

**Update 2026-08-14 ~06:40 PDT — ONE BUILDER (Joseph), AND §3.1 RULED: BOTH FORMS WITH THE REDUCTION CHECKED.**
Joseph: *"Okay yeah drop the second builder."* **The spec now makes no independence claim anywhere** — and the
sharpest reason is self-indicting: the spec pins `dof`, `centring`, `ravel_order` and member selection, i.e.
the only decisions two builders could have differed on. **§3.1 ruled as decider:** emit `C`
`(n_reported, n_reported)` **and** `C_full` `(285,285)` **and** the `(285,)` `reported_mask`, with
`C == C_full[np.ix_(mask, mask)]` asserted **bit-identically** — full-only leaves the error-prone reduction
verified by nobody, reduced-only loses the fixed dimension. **The common mask is the FPS `266`, not this
family's `262`**, because `assemble_ctotal_bkgsub.py:104-107` fails closed on a mask mismatch; nesting verified
**three ways** (D `b9d0803`, B independently, and C from a third artifact leaving exactly the 19 implied
zeros). Census on 266: 259 always + 3 flickering + 4 identically zero, the four declared by index.
**Correction:** those four had been justified via `n_cells_masked_zero_acceptance = 4`; measured over 18
members that field is **{2,3,4,5,6}** — a per-replica draw — so the nesting stands but the "two artifacts
agree" phrasing does not. **`CSTAT-D0e`:** `n_reported` from the mask, never from `diag` — the trap is live at
`p4_validate_active_lateral_fps.py:72`, whose neighbour `:70` is a negativity test that passes a rank-49
matrix silently; both now in `KNOWN_ISSUES.md`. `max_abs_asymmetry` and `member_xsec_sha256` promoted to
REQUIRED, plus `CSTAT-R3f` constant `slurm_array_job_id` — because the **failed** r1 array shares the live r2
output root. `C_stat` still not constructed; `56936015` at 18/50.

**Update 2026-08-14 ~06:00 PDT — `OI-91` (rank) CLOSED BY REFERENCE: IT WAS DISPOSITIONED BEFORE LAUNCH.**
The `N=50` predeclaration (`6bd3707`, 2026-08-12 23:29) already settled rank — *"rank is not the criterion …
the rank-deficient GoF treatment is already disclosed under `OI-29`"* — with Joseph's **"sounds good, get
N=50 up and running."** Mine was the **fourth** approach to that closed question (`OI-122` records two more);
`SPEC` §7 now cites the predeclaration first so the next agent hits the disposition in a document it must
read anyway. The measurement is kept, the escalation withdrawn. **Best result this round: `CSTAT-D1`/`D2`
turn out to be the ALREADY-ADOPTED convention** — `combine_cstat_bkgsub.py:57-58` is replica-mean-centred
with `1/(N-1)` — so the builders' output composes with the existing chain **without a translation step**.
That file also shows production masks on the **central value** (`rep = cv > 0`), which is replica-independent
and immune to `BEN-231` by construction; **a quotable nominal full-event extraction would retire `BEN-231`
outright.** Added `OI-93`: **Hartlap** (a truncation chosen for tractability still carries finite-`N` bias
and it makes χ² too **small**) and **Peelle's Pertinent Puzzle** (`+ norm 1.4%` is present; PPP looks like a
*good* fit), both predeclared before any number exists, all external citations labelled **UNVERIFIED**.
`CSTAT-N1`: **there is no separate diagonal data-statistical term** in the PET chain — `C_total = C_syst +
C_stat + C_ml + C_retrain` — so rank in the total is a **budget** from summed low-rank blocks, not a rescue.
`C_stat` still not constructed; extraction `56936015` still short of 50/50.

**Update 2026-08-14 ~05:00 PDT — `C_stat` SPEC COMMITTED (`OI-121`). TWO BLOCKERS RAISED. NOTHING CONSTRUCTED.**
`OI-121` authorized as **two independent builders from one written spec**; **lane C is the spec author and
not a builder.** **AMENDED-BY-REFERENCE 2026-08-15 — READ THIS BEFORE READING THE CONTRACT.** Lane C (PET), holding
the contract **by designation** and not by continuity (`BEN-324`), ruled that a **reduced-`n` diagnostic is
COHERENT** under it as a non-quotable arm on five conditions, and that comparing such an arm's spread to the
family's is licensed for **description only** —
`../docs/orchestration/RULING-20260815-lanec-reduced-n-diagnostic-coherence.md`. **The ruling is NOT in the
contract and CANNOT BE:** `state/gate5-cstat-spec-measurements-20260814.json` hash-pins both the machine
contract and the prose spec, so an additive amendment breaks a committed receipt's provenance and was
reverted rather than repinned (`BEN-238`, `OI-123`). **This paragraph exists because a contract reader has
no other way to learn the ruling exists** — `CSTAT-O1`'s re-opened-four-times failure, one level up.

`SPEC-20260814-gate5-cstat-construction-v1.md` + `pet/gate5_cstat_contract.json` pin the
covaried key (`xsec`), the **`15 × 19 = 285`** grid (**not** `AGENTS.md`'s 224-cell paper grid — the dump is
extended-FPS), the flattening string, replica ordering, **centring on the replica mean** (nominal-centring
measured at **6.013×** the trace, the excess being exactly the bias offset, and the only nominal artifact is
named `NONQUOTABLE-DIAGNOSTIC`), `1/(N-1)`, and the reporting domain. **Two items return to Joseph and both
gate publication rather than build:** `OI-91` — rank ≤ 49 against **262** reported cells, singular by
**5.35×**, no inversion treatment declared; and `OI-92` — the spread is **4.478%** where counting predicts
**0.0493%** and `set_seed` appears **nowhere**, so the object is `C_stat + C_train`, inseparable from this
family (`BEN-232`). D's replica-dependent mask hazard **measured and confirmed**: 3 flickering cells in 14
members, one reported in 9 of 14 (`BEN-231`). Extraction array `56936015` was **14/50** — nothing
constructed, and the spec was written during the wait so nothing is. Receipt
[`state/gate5-cstat-spec-measurements-20260814.json`](../docs/orchestration/state/gate5-cstat-spec-measurements-20260814.json),
25 internal-consistency checks, 0 failed.

**Update 2026-08-14 ~01:45 PDT — GATE 5 FAMILY 50/50, `FAMILY_COMPLETE_PASS` AT FULL STRENGTH. `C_stat` still not constructed.**
Both arrays terminal with **zero failures at any point**; queue drained. The run was full strength — no
`--skip-replay`, `--source-npz` supplied, so the ~49M-variate three-stream re-draw actually ran — and
parity was verified **in the same turn, before the run** (2 of 2 `CURRENT`, repo `d2bc94b`). Verdict is
the **bare** `FAMILY_COMPLETE_PASS`: `weakened_axes []`, `is_full_strength true`, 50/50 targets and 50/50
trainings passing, zero name mismatches, zero family failures, **58 checks per target row** (50 at the
pre-repair promotion, 54 after R1–R4 with replay skipped). 50-of-50 distinct on target digests, all three
factor streams and weights digests; 50 distinct `R` straddling the nominal. **`BEN-230`'s check ran and
agreed on 50 of 50** — its first exercise on the full family — with its length-and-sum limit restated.
Evidence rescued off scratch immediately and the verdict **re-derived from the committed copy**
(`ca99effa…`, 277,601 B). **`C_stat` is null and was not constructed:** this is the
completeness-and-coherence gate, and extraction plus centring on the replica mean is the next step and a
separate reviewable action. `OI-60` is not closed. Receipt
[`state/gate5-family-complete-pass-20260814.json`](../docs/orchestration/state/gate5-family-complete-pass-20260814.json).

**Update 2026-08-13 ~18:40 PDT — the repaired reconciler is DEPLOYED and parity is MEASURED; still `PARTIAL` at 25 of 50.**
Parity both directions in one turn: BEFORE `STALE_BUT_COMMITTED` + `atomic_write.py` **MISSING** (exit
3), AFTER **2 of 2 CURRENT** (exit 0), with cluster and local `sha256sum` agreeing independently of the
parity tool. **The fail-loud import was tested on the real deployment** — reconciler copied first with
`atomic_write.py` absent gives exit 3 and no report, which is R2's refusal to degrade, exercised rather
than asserted. First live run of R1–R4: **50/50 targets passing, 25/25 trainings passing**, 10
`IN_PROGRESS`, 15 `NOT_STARTED`, only failure `trainings_present 25 != 50`. **The new checks were
confirmed to have RUN, not merely not failed**: 54 checks per target row (was 47), 24 per training row,
six training invariants each resolving to one group, zero `invariant_path_resolves` failures.
`weakened_axes = ['REPLAY_SKIPPED','SOURCE_UNHASHED']`, `is_full_strength` false — the run does not
claim more than it did. A promotion pass still needs 50/50 **at full strength** (no `--skip-replay`,
`--source-npz` supplied) **and parity re-checked at that moment**. Receipt
[`state/gate5-reconciler-deployment-20260813.json`](../docs/orchestration/state/gate5-reconciler-deployment-20260813.json).

**Update 2026-08-13 ~18:05 PDT — BEN-157 R3+R4 landed: ALL SEVEN audit items repaired in code. Promotion still unauthorised, and not because of the code.**
**R3:** absent *tool inputs* downgrade the verdict with a named token (`SOURCE_UNHASHED`,
`NOMINAL_UNCHECKED`, joining `REPLAY_SKIPPED`) and are reported as `weakened_axes` + `is_full_strength`
so nobody parses a string; absent *required receipt fields* **fail the member** instead
(`R_published_by_receipt`, `R_operand_published[...]`). Two treatments because a downgrade would blame
the tool when the receipt is what is incomplete. This exposed **six of my own tests asserting full
strength for runs that skipped two checks**; a new test proves the bare `FAMILY_COMPLETE_PASS` is still
reachable. **R4:** the name-pin test now opens `sbatch_gate5_replica_train_array.sh` instead of
comparing against a copy of its own string, and the parse is power-tested against a tampered launcher.
**Verified live before landing: all 50 target receipts publish `step1_class_ratio` and all four
operands**, so the fail-closed checks do not reject the family. **73 → 104 tests.** Three residuals
recorded and not closed: `is_complete`'s whole-second `mtime`, no receipt hashed against anything, and
`completion_marker_valid` being a producer literal (`OI-66`). **What still blocks promotion is that the
repaired tool has never run against the campaign** — that needs a deployment (`OI-64`), which must now
also copy `atomic_write.py`. A 50/50 pass from an unverified copy is not evidence. Receipt
[`state/gate5-reconciler-r3-r4-repair-20260813.json`](../docs/orchestration/state/gate5-reconciler-r3-r4-repair-20260813.json).

**Update 2026-08-13 ~17:20 PDT — BEN-157 R2 landed; R3/R4 open, promotion still BLOCKED.**
One treatment for audit items 2–5, not four patches. The training stage now hashes the **canonical**
artifact path and tests the receipt's path claim against it (`artifact_path_is_canonical`), so codex's
rename-plus-matching-receipt attack — an **exact pass** before — now fails; it reads its own `.done`
markers, where it previously read none; `atomic_write.is_complete` is **called** rather than
re-implemented, with one hand-rolled check retained for the thing the primitive cannot do (a marker
naming another replica's file); and **all three** code digests are read, re-hashed from disk where the
path resolves, and required constant across the family — constancy rather than a pin, because the driver
digests float by design and a pin matches every member equally. **Verified against the live family
before landing: 150 real markers, `is_complete` false for 0**; real `artifact.path` canonical; all three
code paths resolving. `completion_marker_valid` is deliberately **not** required — the producer writes
the literal `True`, so it would be a check that cannot fail (`OI-66`); I drafted that check and removed
it. **One invariant of mine could not fail and its own power test caught it** (values at the row's top
level, so every member resolved to `None` and one group read as unanimous); `constant_across_family` now
reports whether the path resolved, which also covers the twelve pre-existing target invariants. 90 → 100
tests; full suite 1297/4, down from 7 failures. **New deployment constraint: `atomic_write.py` must be
copied beside the reconciler**, and the import is fail-loud rather than degrading. Receipt
[`state/gate5-reconciler-r2-repair-20260813.json`](../docs/orchestration/state/gate5-reconciler-r2-repair-20260813.json).

**Update 2026-08-13 ~16:10 PDT — BEN-157 R1 landed; promotion still BLOCKED pending R2/R3/R4.**
`DECLARED_INVENTORY = 50` is pinned in the tool and bound by import-time assertion to `SEED_POLICY`,
which already named it. `--n` is an **assertion only**, checked before any artifact is read, and a
disagreeing value writes **no report at all**. Measured both ways: `--n 0` on an empty root went from
**rc=0 with the exact `FAMILY_COMPLETE_PASS`** to **rc=3 with no report**, while the honest run still
returns rc=2 `PARTIAL` with `targets_present 0 want 50`. Usage is exit **3** rather than 2 — correcting
my own proposal, since 2 already meant *incomplete* here and reusing it would have collapsed "could not
look" into "looked and found it short". **The suite was de-idiomed in the same commit** (73 → 90 tests;
`_run_main` no longer takes a size; complete-family tests build `DECLARED_INVENTORY`; three unit-level
fixtures deliberately left small). The report now carries `declared_inventory_is_pinned_in_tool`, so a
pass at 50/50 is distinguishable **in the artifact** from one at a caller-chosen size — which is what
made the old pass unfalsifiable rather than wrong. **R1 closes the headline, not the class:** items 2–7
are untouched and `OI-65` holds them. New tool sha `85ca74f3…`; all three deployed copies are now
deliberately stale and re-deployment is a separate verified step (`OI-64`, `BEN-156`). Receipt
[`state/gate5-reconciler-r1-repair-20260813.json`](../docs/orchestration/state/gate5-reconciler-r1-repair-20260813.json).

**Update 2026-08-13 ~15:50 PDT — PROMOTION BLOCKED: codex's audit found seven defects in the reconciler and all seven are confirmed.**
The verifier this lane wrote cannot currently tell a complete family from an empty one. `--n` is
caller-supplied with no floor, so **`--n 0` on an empty directory returns rc=0 and the exact
`FAMILY_COMPLETE_PASS`**, and a real 3-member family passes at `--n 3` while `PARTIAL` at `--n 50` with
the artifacts unchanged. Training `PRESENT` is receipt-only and **`completion_marker_valid` is never
read anywhere in the tool**; the `NAME_MISMATCH` guard is blind to a receipt that *agrees* with a wrong
file; the `.done` check omits `mtime` and **no receipt is hashed against anything**; the verifier checks
a HEAD *claim* where the producer records three content digests and the launcher checks all three; R
checks evaporate on a null `R` (43 passed / 0 failed, `R_recorded: null`); and the name-pin test asserts
against duplicated literals rather than opening the launcher — a claim I had made to a peer in the
opposite form and withdraw here. **73 tests could not have found any of it: they are written in the
tool's own idiom.** No emitted verdict is invalidated — every campaign run used the default `n=50` and
returned `PARTIAL` — but **Gate 5 does not advance to extraction or centering until the verifier is
repaired and retested, and no promotion pass will be run on the current tool even at 50/50.** One
invariant, not seven patches: derive from the filesystem and pinned constants, never from the receipt's
account of itself; required inputs fail closed rather than disappear. `BEN-157`, `OI-65`; receipt
[`state/gate5-reconciler-audit-confirmation-20260813.json`](../docs/orchestration/state/gate5-reconciler-audit-confirmation-20260813.json).

**Update 2026-08-13 15:12 PDT — deployment parity checked and clean; still `PARTIAL` at 23 of 50.**
Family state unchanged (50/50 targets, 23 training receipts, 23 weights `.npz`, `C_stat` null), so the
reconciler was deliberately **not** re-run — the count has not moved, and a re-run costs ~23 × 49M-variate
replays to reproduce the 15:02 artifact. What was checked instead is the thing no receipt covers:
**whether the file that executes is the file that was committed.** A peer's `ac540d5` extension of
`reconcile_gate5_family.py` had not reached the scratch copy running it, the second instance today of
`OI-57`'s class. All three deployed copies (located by `find`, two of them peers') are now `CURRENT`
against HEAD `4e88a13`. The fix is executable — `nd-unfolding/pet/verify_executing_copy_is_committed.py`,
20 tests both directions, `STALE_BUT_COMMITTED` as a distinct state because the naive *"is it in the
repo?"* check passes on exactly the stale file it must reject. Power-tested on `e536540d`, the file that
was actually executing at 14:55. **It has no caller yet: `OI-64`.** `BEN-156`; receipt
[`state/gate5-deployment-parity-20260813.json`](../docs/orchestration/state/gate5-deployment-parity-20260813.json).

**Update 2026-08-13 14:55 PDT — target leg COMPLETE, training leg throttled by the cluster.**
**Targets `56857232`: 50 of 50 COMPLETED and all 50 pass all 29 reconciliation checks** — all 50 target
digests and all three factor-hash families distinct, none equal to the Gate-2 nominal, and all 50 `R`
values distinct and straddling the nominal `1.1240802949941018`. Training `56857233`: **23 COMPLETED,
23 receipts, all 23 passing all 11 training-stage checks** — their first exercise against live data,
including the binding that each member trained on its own replica's target — with the `NAME_MISMATCH`
guard silent, which is the half that proves it is a check and not an alarm. **Per-member training time is
now MEASURED: mean `3:00:30` (min `2:58:21`, max `3:04:48`, n=23), retiring the earlier 2.94 h and 3.03 h
projections** — the pre-completion per-step method landed 0.6% high and inside the measured range.
**Throughput collapsed from 10 concurrent to 2 at 12:34 PDT and the cause is external:**
`shared_gpu_ss11` has essentially zero idle capacity (1631 nodes `alloc`, `208768/0/0/208768`). The
reported `Reason=JobArrayTaskLimit` is misleading — 2 running against `ArrayTaskThrottle=10` (`BEN-153`).
A latent second constraint: QOS `MaxJobsAccruePU=2`, both slots held by lane B's `g6_floor`, leaving
Gate 5 at `AGE=0`. **Remaining 25 members are ~7.5 h at 10 concurrent and ~37.6 h at 2; the ETA is
external and is reported as bounds, not a time.** Walltime is not at risk (8 h requested, ~3 h used).
Receipt: [`state/gate5-throughput-collapse-20260813.json`](../docs/orchestration/state/gate5-throughput-collapse-20260813.json).

**Reconciliation, 2026-08-13 05:50 PDT — verdict `PARTIAL`, owner lane C.** First full pass with
`nd-unfolding/pet/reconcile_gate5_family.py` (50 tests, every check power-tested both directions;
it contains no covariance code, so it cannot be talked into centring a partial family):
**16 of 50 target receipts present and all 16 pass all 29 checks; 0 of 50 training receipts.** No
failures in either array. Target digests, and all three factor-hash families, are **distinct across
the family and none equals the Gate-2 nominal** — the reassuring failure (identical targets reading
as a *small* `C_stat` rather than a broken draw) did not occur. All shared invariants are constant
across the 16, and **all three coherent Poisson streams were re-drawn independently and match 16/16**,
which closes the data-factor stream that no stage verifies (`BEN-151`, `OI-60`). Per-member training
duration, previously unmeasured, is **~2.94 h** from measured per-step cadence against a predeclared
budget of 6:00:36 — ratio 2.05, `BEN-152` — putting the family at **~19:20–20:10 PDT 2026-08-13**.
Receipt: [`state/gate5-family-reconciliation-20260813.json`](../docs/orchestration/state/gate5-family-reconciliation-20260813.json).
**Source identity rests on one independent check only** (`OI-58`): quoting `inputs_sha256` out of a
replica artifact as verified provenance is blocked; cite
[`state/gate5-source-npz-verified-20260813.json`](../docs/orchestration/state/gate5-source-npz-verified-20260813.json).

For every replica, in this exact order:

1. Enumerate complete, ordered data, signal-MC, and background-MC inventories
   before any training subset. Each replica is an independent single-rank job;
   Horovod and distributed rank slicing are prohibited.
2. Draw one coherent Poisson factor per inventory member from a persisted,
   replayable replica seed policy.
3. Apply data factors to data weights, signal factors everywhere signal MC is
   used, and background factors to the negative background injection.
4. Run a fresh Stay-Positive refinement for that replica after applying the
   background factors.
5. Select the training subset without redrawing, shortening, or reindexing the
   full factors.
6. Reuse the exact applicable signal/background factors during full extraction
   and completeness/count construction.

Persist full inventory hashes, seeds, factor hashes or replayable factors,
subset indices, train/extract identity checks, target/refinement telemetry, and
completion status. A missing unit invalidates the replica; a missing replica
invalidates the declared ensemble manifest. Center `C_stat` on the accepted
replica mean.

Run a small pilot only to validate the machinery. Declare the publication
replica inventory before viewing its covariance and compare its spread with the
Gate-4 floor.

## Gate 6 — PET-specific ML ensemble

Use the nominal target with no Poisson fluctuation. Vary only the predeclared
crossed training/subsample/split and estimator seeds. Persist all seeds and
completed extractions; center on the ensemble mean and compare with the GPU
floor. Scalar GBDT ML ensembles do not substitute for this component.

## Gate 7 — targeted joint systematic retraining decision

Publication vertical/flux systematics are joint end-to-end variations. For a
nuisance `u` that can change the learned mapping:

```text
delta_u = x_u(varied physical input + universe-specific background refinement
              + retrained estimator) - x_CV
```

The component is constructed directly from the declared joint shifts. Do not
build or add separate frozen-map and retraining covariances for the same
nuisance; they share the nuisance and would omit/corrupt their cross term.

First run a predeclared targeted set spanning dominant model, flux, and
kinematic behaviors. Compare the joint retrained displacement with the matched
frozen-map diagnostic only to decide expansion. Declare trace and tail
materiality thresholds before looking at results and bound the GPU floor.

- If the learned-map response is immaterial for a documented nuisance, a
  frozen-map-only treatment is allowed only with the proof and bound in its
  component summary.
- If material for selected bands, expand those complete bands/endpoints.
- If broadly material, expand to the full applicable universe inventory.

This gate controls cost, not estimator definition: every adopted endpoint is
still a complete joint variation, and every universe repeats the literal
background injection plus Stay-Positive construction.

## Gate 8 — full-schema selection-complete laterals

Consumes only the committed Gate-3 P3F-PET source manifest. For every declared
lateral endpoint, carry its shifted selection, event membership, background
target, native misses, and full-event input into joint background refinement,
retraining, and extraction.

P3S standard endpoints, scalar-FPS purity unfolds, and reduced-schema P3F
artifacts are controls only. Every accepted endpoint must share the nominal
estimator fingerprint and differ only by the declared physical variation.
Build the lateral component from the complete asymmetric endpoint inventory
under the experiment's declared centering convention, with a separate mean
shift record.

## Gate 9 — adoption and exact projections

Declare nuisance ownership and independence/coupling before covariance
assembly. On one matched central/mask/order/fingerprint, assemble only:

```text
C_total = C_stat + C_ML + C_syst_joint + C_lateral_joint
```

There is no separate additive `C_retrain`. Require exact component/block
reconstruction, common central and ordering, symmetry, PSD/eigen diagnostics,
finite diagonal, mean-shift diagnostics, extended-edge validation, and exact
5D-to-4D covariance projection.

Adoption also requires acceptance-supported/prior-dominated tier outputs,
coverage and prior-envelope controls, scalar/PET comparison only on a common
measurement domain, tracked product summary, and ledger/RUN_LOG/STATUS entries
in the same commit.

Until Gate 9 lands, label outputs by component and candidate fingerprint; do
not call them the final PET budget.

## Reuse/rerun matrix

| Item | Disposition |
|---|---|
| Recoil-only PET products and copied scalar purity targets | `QUARANTINE` cross-check; no transfer |
| Reduced full-event interface/stress products | `QUARANTINE` interface cross-check; no transfer |
| Extended-edge and reporting conventions | `REUSE` after exact contract/hash validation |
| Raw source AnaTuple inputs and per-playlist manifests | `REUSE` after provenance/availability checks |
| Existing FPS event-loop roots lacking full schema/background clouds | Insufficient for G2; do not relabel |
| G2 full-schema FPS CV roots/NPZ | `BUILD` once after binary drain/ownership gate |
| Literal signed/refined nominal target | `BUILD` from G2 inventories |
| Publication nominal and GPU floor | `BUILD` under one fingerprint |
| `C_stat` | `BUILD` with F7 full data/signal/background draws |
| PET `C_ML` | `BUILD` independently with no Poisson |
| Vertical/flux systematic component | `BUILD` from adopted joint end-to-end universes |
| P3F-PET source inventory | `BUILD` and commit after G2, before nominal |
| P3F-PET endpoint retraining/laterals | `BUILD` after nominal from Gate-3 inputs |
| Full per-universe retraining | `GATED` by targeted materiality, never assumed unnecessary |

## Atomicity and scheduler gate

Every unit writes a unique temporary artifact, runs its content validator, and
atomically renames only on success. Resume logic checks manifest completeness,
schema/fingerprint, and content—not file size. Partial artifacts are
quarantined.

Before each launch, inspect existing allocations and queues. Use an owner-held
interactive node for single-node work that fits its remaining wall; queue
dependency-safe arrays, long/GPU jobs, or work that must outlive the shell early.
Never duplicate a queued/running writer, and never cancel another worker's job
or allocation.
