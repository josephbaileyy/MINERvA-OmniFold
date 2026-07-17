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

## Stage 1 — pilot slice verdict (IN FLIGHT)

Jobs fe5p_pilot (purity target) + fe5p_ablat1 (legacy-matched all-ones). Gates in
OMNIFOLD-DOSSIER.md §P-slice. Products stay in the campaign worktree; nothing promotes to
the shared tree until gates pass AND the upstream CLM-007 fix is adopted by Agent B's file.

## Stage 2 — hand-back to the publication runbook (BLOCKING ITEMS, in order)

1. **Upstream the CLM-007 fix** into `nd-unfolding/pet/fullevent_fps_dataloader.py`
   (Agent B's file): fail-closed missing-`measured_scalars` + explicit data-scalar/weights
   arguments, with the two regression tests from the campaign worktree. Owner: Agent B (or
   user decision to let this campaign commit it). Without this, ANY future data-side xps2
   run silently trains on MC sentinels.
2. **Fix-or-waive each CLM-008 item before P5B production** (explicit written waiver per
   item): FiLM pad-shift + unmasked classifier attention (F2 — affects every full-event
   train); posinf→1 reweight clamp (F3 — affects strong reweights; also gates any negweight
   arm); bootstrap-draw-after-subsample (F7) + rank-slicing misalignment (F8) — HARD gates
   for C_stat and horovod; trained-model reload test (F9); truth-KNN phi periodicity (F10).
3. **G2 (C++ full-event dump) + G3 (P3F endpoints)** per the feature contract; the
   interface request to Agent A is filed. The pilot deliberately does NOT wait for these.

## Stage 3 — P5B production (per the contract's launch order)

Nominal → GPU floor → C_stat (coherent, fixed seeds) → C_ML (crossed) → end-to-end JOINT
vertical/flux universes (NO additive C_syst+C_retrain) → P3F selection-complete laterals →
C_total on one estimator fingerprint → projections/two-tier reporting + 3-prior envelope.
Estimator ID `pet-fullevent-fps-v1` reserved for this stage; the pilot is
`pet-fullevent-fps-pilot0` and none of its weights/covariances transfer.

## Stage 4 — background-treatment arm (gated separately)

Negweight full-event arm once (a) the bkgcloud dump chain lands (user-owned
`sbatch_evloop_array_pointcloud_fps_bkgcloud.sh` products: background reco clouds + muon
scalars in the measured stream), (b) the scalar negweight validation + user sign-off flip
the FPS default (bkg_negweight workstream). Convention-matched comparison vs the step-3a
negweight GBDT central. Pre-registered prediction (user, 2026-07-16): full-event
conditioning should help negweight specifically where B≈D by localizing the background in
muon coordinates. Stability pre-check required: F2 + F3 above (signed class-1 weights).
Theory anchor: note App. B sieve-reduction subsection (CLM-009, VERIFIED-NUMERIC).

## Stage 5 — representation refinements (optional, after Stage 3 baseline)

Gregor four-way pilot (`docs/GREGOR_FOUNDATION_MODEL_REFERENCE.md`): recoil-only vs
full-event-random-init vs OmniLearned-pretrained vs MINERvA-fine-tuned encoder, identical
events/weights/seeds/budgets, judged by the campaign gates (incl. omitted-muon stress at
real scale + high-W slice). PyTorch port cost is the main budget item. Only the winner
enters the expensive UQ campaign.
