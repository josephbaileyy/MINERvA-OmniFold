# Staged rollout: full-event PET over the extended-FPS domain (fe-fps-campaign)

2026-07-16. Campaign-level plan reconciling the P5A verification (CLAIMS.md CLM-001..008),
the pilot slice (CLM-006, jobs 56010587/56010588), and the concurrent workstreams. The
P5B *execution* contract stays canonical in `nd-unfolding/pet/FULL_EVENT_FEATURE_CONTRACT.md`
and `docs/PUBLICATION_COMPLETION_RUNBOOK.md` (packet P5B); this file adds only ordering,
gates, and ownership discovered by this campaign. One home per fact — pointers, not copies.

## Stage 0 — verified base (DONE this campaign)

P5A engineering VERIFIED (CLM-001/002/005), closures reproduced with archived evidence
(CLM-003/004), pilot input repaired (CLM-007: fail-closed `measured_scalars` + aligned data
scalars from the 5D xps2 npz; worktree patch `MINERvA-OmniFold-fe`, PATCHES.md). Sieve
reduction proof committed to the note appendix (89ecc79) and pushed to Overleaf.

## Stage 1 — pilot slice verdict (DONE 2026-07-17: PASS, CLM-006 promoted)

Jobs fe5p_pilot 56010587 (purity target) + fe5p_ablat1 56010588 (legacy-matched all-ones),
both COMPLETED (~1h17m each, shared GPU). All predeclared §P-slice gates pass on both arms:
outputs finite on all 49.15M rows, unit check bit-exact, miss neutrality exact, Tier-1
per-cell median |FE/recoil-only−1| = 4.25% (purity) / 4.37% (ones) vs the ≤10% tolerance
(GBDT comparator correctly refused — no committed xps2 GBDT central). Numbers + caveats in
CLAIMS.md CLM-006. Products stay in the campaign worktree; nothing promotes to the shared
tree until the upstream CLM-007 fix is adopted by Agent B's file (Stage 2 item 1).

## Stage 2 — hand-back to the publication runbook (updated 2026-07-17)

1. ~~Upstream the CLM-007 fix~~ **DONE** (Agent B, aa3f44c: fail-closed +
   row-count gate + regression tests; verified in-tree by this campaign).
2. **CLM-008**: F9/F10 **FIXED** (4043e3f/220c970, GPU-validated); F2/F3/F7/F8
   dispositioned with written fix specs in the feature contract — implementation due at
   the P5B engine build. F7/F8 remain HARD gates for C_stat and horovod.
3. **G2 (C++ full-event dump) + G3 (P3F endpoints)** — SCHEMA FINDING (2026-07-17
   coordination pass): the in-flight P3F campaign (55972324) uses the pre-full-event
   binary; its ROOTs are scalar-FPS schema (no muon four-vector/vertex/view/timing/
   residual-E branches, no stable event keys). They close scalar FPS P4/P6 but NOT
   full-event P5B laterals. Decision assigned to Agents B+C: (a) compact full-event
   sidecar rerun reusing P3F clouds, acceptable ONLY with exact fail-closed row-alignment
   proofs (fe_pilot CRC-join methodology) + added stable event keys; or (b) full endpoint
   regeneration after the C++ branches land. "P3F merged > 0" is NOT sufficient to open
   P5B.

### Coordination takeover log (2026-07-17, user-authorized)

Orchestrator assumed cross-agent coordination: (i) Agent A stood down from FPS P4
post-processing (Agent C sole owner; A = standard-only) before the FPS array completes;
(ii) Agent C given commit-gate GO for validated P6-FPS non-lateral + STATVAL results
(scoped staging only); (iii) Agent B given the P5B schema-gating correction above;
(iv) Agent D's dead 4D corrected chain repaired by the orchestrator: comb4dCc 55971617
failed on 15 missing throws — root cause partial uthrow slabs (31, 34–39; 1–3 throws
instead of 4) from an earlier interrupted multinode run passing `skip (exists)`; partials
moved to `uthrow_slabs_4d/partial_20260716_interrupted/`, regen array 56025478
(tasks 31,34-39) → combine 56025481 → adopt 56025483; dead adopt 55971619 cancelled.

### P5B launch gates (adopted 2026-07-17 from external gate review; adjudication in
`MINERvA-OmniFold-fe/orchestration_runs/coordination/P5B_GATE_REVIEW_20260717.md`)

1. No P5B nominal until F2 (masking, loader-supplied mask preferred) and F3 are committed
   and GPU-validated. F3 must be the logit-space form — `w = exp(clipped_logit)`,
   fail-closed on non-finite logits, predeclared cap + saturation telemetry +
   cap-sensitivity check, identical across nominal/replicas/universes/extraction — NOT the
   provisional posinf-cap patch.
2. No C_stat until F7 is complete (coherent global Poisson draw over the FULL inventories
   before subset selection; persisted factors/seeds; same MC draw at extraction).
3. No Horovod for P5B: nominal/replicas/universes run as independent single-rank GPU jobs
   (chunked rank-0 reweight-all). F8 becomes moot; if Horovod is ever retained it reverts
   to a hard gate with the full equivalence-test battery.
4. No publication laterals from reduced-schema P3F sidecars. Lateral source = (b) fresh
   full-schema P3F regeneration after the C++ branches land; the reduced {pT,p‖} sidecar
   is a cross-check only. Reduced and full schemas get DIFFERENT estimator fingerprints
   (`pet-fullevent-fps-v1` reserved for full schema only).
5. CLM-007 stays closed, but any separate data-feature join still requires an exact
   alignment/provenance proof (fe_pilot CRC-join pattern).
6. **No publication P5A nominal or P5B production on a purity-only target.** The
   pre-migration negweight campaign records the user's locked 2026-07-11 decision:
   FPS/N-D/PET use `negweight-refined`, and PET uses Option A literal background-cloud
   injection plus Stay-Positive. See
   `2d-unfolding/HANDOFF_bkg_negweight/bkg_negweight_state.md` under “USER DECISIONS
   locked.” Purity is a matched regression control only.

## Stage 2.5 — publication background-treatment gate (HARD; before P5A/P5B)

The migration handoff incorrectly left negweight as an optional post-baseline arm. That
ordering is superseded by the already-locked user decision above. Before training the
publication nominal, the full-event dump/input must carry aligned background reco clouds,
muon/event scalars and `w_bkg`; the measured side must be constructed as data at positive
weight plus background MC at negative POT-scaled weight; and Stay-Positive must produce a
finite non-negative refined target with exact signed-target normalization/provenance and a
frozen estimator fingerprint. The coherent F7 bootstrap must cover the full data, signal-MC,
and background-MC inventories, apply the background draw before refinement, and reuse each
MC draw wherever that inventory participates. Refinement is rebuilt per replica rather than
copying nominal refined weights.

The gate closes only with focused alignment/signed-target/refinement/bootstrap tests, a
small full-event negweight-refined pilot, a matched purity control, and a committed manifest.
Do not launch the expensive nominal or any UQ ensemble merely to make this decision—the
decision is already made, and the implementation/provenance proof is the remaining gate.

## Stage 3 — P5B production (per the contract's launch order)

Negweight-refined nominal → GPU floor → C_stat (coherent, fixed seeds) → C_ML (crossed) → end-to-end JOINT
vertical/flux universes (NO additive C_syst+C_retrain) → P3F selection-complete laterals →
C_total on one estimator fingerprint → projections/two-tier reporting + 3-prior envelope.
Estimator ID `pet-fullevent-fps-v1` reserved for this stage; the pilot is
`pet-fullevent-fps-pilot0` and none of its weights/covariances transfer.

## Stage 4 — background-treatment arm (superseded ordering tombstone)

This arm moved to the hard Stage-2.5 gate because the user had already selected it as the
publication default. Retain the convention-matched purity comparison and the pre-registered
prediction that full-event conditioning helps where B≈D, but never build a purity publication
UQ chain first. Theory anchor: note App. B sieve-reduction subsection (CLM-009,
VERIFIED-NUMERIC).

## Stage 5 — representation refinements (optional, after Stage 3 baseline)

Gregor four-way pilot (`docs/GREGOR_FOUNDATION_MODEL_REFERENCE.md`): recoil-only vs
full-event-random-init vs OmniLearned-pretrained vs MINERvA-fine-tuned encoder, identical
events/weights/seeds/budgets, judged by the campaign gates (incl. omitted-muon stress at
real scale + high-W slice). PyTorch port cost is the main budget item. Only the winner
enters the expensive UQ campaign.
