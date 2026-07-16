# Full-event PET feature contract + P5A validation (KNOWN_ISSUES #19)

Owner: Publication Agent B (PET). Draft frozen for the P5A interface milestone, 2026-07-16.
This is the feature contract the production estimator (P5B) must satisfy. It records the
exact schemas, units, normalization, masks, truncation policy, unavailable counterparts,
required new branches, cost estimate, and the recoil-only products quarantined as cross-checks.

Naming: **full-event PET over the declared extended-FPS fiducial phase space** (NOT
"full phase space"). Two independent mandatory changes vs the recoil-only campaign:
(1) full-event representation; (2) trained/reported over the extended FPS measurement.

## Architecture (user directive 2026-07-16)
PET trains UNBINNED on CONTINUOUS features. The extended (pT,p‖) EDGES are used ONLY for
domain retention, reporting, covariance construction, and validation — never as classifier
inputs or training bins. Guarded by `assert_extended_fps_edges` (fail closed on paper grid).

## Estimator ID + configuration fingerprint (single contract for central + ALL covariance)
**Estimator ID:** `pet-fullevent-fps-v1`. Every P5B component (central, C_stat, C_ml, vertical/
flux, laterals, total) MUST use this identical contract; recoil-only PET UQ is NEVER attached.
- **inputs:** FPS CV full-event point-cloud npz built with `MNV101_FULL_PHASE_SPACE=1` + the
  finalized full-event dump (scaffolding today = `of_inputs_pc_fps_xps2.npz`, recoil-only
  tensors → must be regenerated for the real central; see blockers).
- **features:** reco cloud (E,pos,z; KNN coord (pos,z)); truth cloud (E,px,py,pz,pdg,theta,phi;
  KNN coord (theta,phi)); `event_reco`/`event_data` = continuous reco muon {pT,p‖} (+ full
  px,py,pz,φ,E,charge,MINOS + reco vertex + residual summaries once branches land); `event_truth`
  = continuous truth muon {pT,p‖}. Edges are reporting/covariance/validation only, never inputs.
- **preprocessing:** cloud ÷1000 (MeV→GeV, mm→m), non-finite→0 (pad/mask sentinel); event
  features z-normalized over pass_reco (reco/data) / pass_truth (truth), !pass rows zeroed.
- **backend:** vendored `omnifold_nn` PET (multi-input Model, explicit `coord_idx`, FiLM event
  conditioning) + MultiFold; niter 2, epochs 8, batch 1024, Adam lr 1e-4, train subsample 2M.
- **seed policy:** estimator seed 42 FIXED for central + vertical/end-to-end universes + C_stat
  (so C_stat varies only the coherent data+MC Poisson replica id); C_ml varies subsample/split
  seed × TF estimator seed (predeclared crossed design), no Poisson.
- **nominal product / phase space:** `products/pet/fullevent_fps/pet_fullevent_fps_nominal_*` (P5B);
  extended-FPS canonical (pT,p‖) grid (this file's CANONICAL_* edges).
- **fingerprint recipe (computed at P5B nominal build, stored in the product summary):**
  `sha256(git_commit(net.py,omnifold.py,dataloader.py,fullevent_fps_dataloader.py) ||
  feature_list || preprocessing || edges || seed_policy || input_npz_sha)`. Every covariance
  component summary must carry the SAME fingerprint or it is rejected at assembly.

## Measurement domain
- Source only FPS CV event loops from `MNV101_FULL_PHASE_SPACE=1` (drops the 4 truth-muon
  kinematic cuts, keeps tracker fiducial, grows the native-miss set). Pass `--full-phase-space`
  wherever the truth gate is reconstructed; consumers without the flag must verify embedded
  FPS provenance and fail closed.
- Canonical extended reporting grid (EXACT; `fullevent_fps_dataloader.CANONICAL_*`):
  - pT   (16 edges): 0,0.07,0.15,0.25,0.33,0.4,0.47,0.55,0.7,0.85,1.0,1.25,1.5,2.5,4.5,30.0
  - p‖   (20 edges): 0,0.75,1.5,2,2.5,3,3.5,4,4.5,5,6,7,8,9,10,15,20,40,60,120
- Two-tier reporting (FPS_PILOT.md): Tier-1 acceptance-supported (eff≳2%), Tier-2
  prior-dominated dead cells (~28% of rate) carry a prior-dependence band. Muon features
  cannot turn zero-efficiency cells into measured cells.
- Scaffolding only (recoil-only tensors, NOT publication inputs): `of_inputs_pc_fps.npz`
  (standard gate), `of_inputs_pc_fps_xps.npz` (angular cut only). `of_inputs_pc_fps_xps2.npz`
  has the right gate+edges but recoil-only tensors → used for alignment/provenance scaffolding;
  the representation is REBUILT.

## Feature schemas (three explicit schemas; no manufactured counterparts)

### reco cloud (step-1 detector) / measured (data) — SAME observable contract
| feature | col | unit | normalization | notes |
|---|---|---|---|---|
| recoil token E | 0 | GeV | ÷1000 (MeV→GeV) | energy>0 = valid-token / pad mask |
| recoil token pos | 1 | m | ÷1000 (mm→m) | transverse position in cluster's view |
| recoil token z | 2 | m | ÷1000 | KNN coord |
KNN neighborhood coords = **(pos, z) = cols (1,2)** (detector geometry), set via PET `coord_idx`.
Padding: zero-pad/truncate to num_part=12 (loader top-N by energy).

### truth cloud (step-2)
| feature | col | unit | norm | notes |
|---|---|---|---|---|
| FS-hadron E,px,py,pz | 0–3 | GeV | ÷1000 | muon±13 & ν removed at source |
| pdg | 4 | — | raw | **retained** (recoil-only loader dropped it); learned embedding = production refinement |
| theta,phi | 5,6 | rad | raw | appended angular direction; **KNN coords = (theta,phi)=(5,6)** |

### event_reco / event_data (continuous, SAME observable schema) — the distinguished muon
- ADOPTED NOW (reduced): `[muon_pT, muon_p‖]` (reco_scalars / measured cols 0,1), z-normalized
  with the RECO-MC statistic (data uses the reco norm → no truth statistic touches it).
- REQUIRED for production (needs new C++ branches, getters exist — FULL_EVENT_INTERFACE_REQUEST.md):
  muon `px,py,pz,E,phi`, `charge/qp`, `MINOS match/range/curvature quality` (step-1 detector
  context, reco+data ONLY), reco vertex `x,y,z`, residual-energy summary tokens
  (unclustered/detector-region), recoil `view ID` + `timing`.
- Detector/MINOS features are step-1 ONLY. NEVER a truth counterpart.

### event_truth (DISTINCT schema, own normalization)
- ADOPTED NOW: `[truth_muon_pT, truth_muon_p‖]` (truth_scalars cols 0,1), z-normalized with
  the TRUTH-MC statistic. NO MINOS/range/quality/vertex-detector counterparts; no sentinels.
- Production may add truth event quantities (truth vertex into event_truth only, truth W).

### masks / types
- Padding mask: token energy (col 0) == 0. (An explicit boolean mask input is a production
  option; the energy-mask convention is documented and tested.)
- Muon is a distinguished EVENT feature (FiLM conditioning), so cloud tokens are all recoil;
  a muon/recoil/view type embedding is only needed if muon becomes a cloud token (production
  option). Detector view distinction awaits the `part_reco_view` branch.

## REDUCTION JUSTIFICATION (explicit, per user directive)
The P5A INTERFACE milestone is validated with the reduced distinguished-muon set
`{pT, p‖}` — the dominant muon kinematics the recoil-only estimator is blind to. This is
sufficient to (a) prove the paired continuous-feature interface works end-to-end and (b)
close the omitted-muon stress test. It is **NOT** a publication-ready feature set: P5A is
NOT declared "passed" on this reduced set. The full schema above is required before the
production nominal (P5B), and needs the C++ full-event dump + FPS-CV regeneration (blocked
on the active-universe C++ owner; branch request filed, not edited while P3S runs).

## Data-semantics note — reco-muon SENTINELS for FPS misses (found in P5A FPS smoke)
In the FPS scaffolding, `reco_scalars` muon (pT,p‖) = **-9999** for every non-pass_reco event
(28.6M/49.2M misses have no reconstructed muon; pass_reco muon is clean, mean 0.734). The
full-event adapter therefore normalizes reco features over pass_reco events ONLY (truth over
pass_truth ONLY) and zeroes the undefined (!pass_reco) rows post-normalization (they are masked
by pass_reco in the step-1 loss). The production full-event input build MUST preserve this
handling; a naive normalization over all rows pollutes the muon scale (was mean -5732 before
the fix). This is a genuine reco/data-vs-truth alignment subtlety the recoil-only estimator
never exposed (it fed no scalars).

## Unavailable counterparts (documented, not sentinel-filled)
- Truth MINOS/range/match-quality: DO NOT EXIST (detector-only) → absent from event_truth.
- Muon full 4-vector/charge/vertex/view/timing at reco/data: pending C++ branches.
- Nuclear-remnant truth token: not dumped (GetTruthFSHadrons keeps mc_FSPart* minus μ/ν).

## Required new branches / event loops
See `FULL_EVENT_INTERFACE_REQUEST.md`. Summary: add muon object + vertex + recoil view/timing
+ residual-energy branches (getters exist) under `MNV101_DUMP_POINTCLOUD`, then regenerate the
FPS CV point-cloud loops with BOTH `MNV101_FULL_PHASE_SPACE=1` AND the full-event dump. P3F
active-universe FPS endpoints (Agent C, `active_universe_5d/fps/`) supply selection-complete
laterals; P3S standard endpoints are regression controls only.

## Estimated cost (from recoil-only campaign timings, scaled for 49.2M FPS MC)
- Nominal full-event train (2M subsample, niter2/epochs8, +continuous evt features): ~1.1–1.3h
  /1 GPU (event-feature overhead is small; reweight-all on 49.2M ≈ +15% vs 32.8M).
- GPU floor: 1 identical repeat (~1.2h).
- C_stat coherent replicas: ~1.2h each; 100 replicas ≈ as the recoil P1 (8-GPU orchestrator
  ≈ 12/4h-alloc → ~3–4 alloc-days wall, or a batch array).
- PET-specific C_ML crossed ensemble: ~12 trains (~15 GPU-h).
- Vertical/flux END-TO-END joint universes (physical variation + retrain together, per
  correction): ~1 retrain per material endpoint; predeclared dominant set first (~6–8 GPU
  trains), expand per the §6 materiality gate. NOT an additive frozen-map + retrain sum.
- Selection-complete FPS laterals: consume Agent C P3F endpoints (CPU dump/extract) + ~10
  endpoint retrains.
- Total new full-event FPS UQ campaign ≈ recoil campaign + ~15–20% (larger FPS sample).

## Quarantined recoil-only cross-checks (NOT promoted)
`products/pet/bkgsub/` recoil-only nominal/floor/C_stat(20+interim42)/C_ml/C_syst/C_retrain/
C_lateral/C_total + replicas 21-46,88-100. Retained as labeled recoil-only cross-checks;
NO covariance component or weight transfers automatically to the full-event estimator.

## P5A validation status (this milestone)
- Engine paired-input repair: net.py multi-input Model + explicit coord_idx; DataLoader
  reco_evt/gen_evt; MultiFold cache/reweight/steps/LoadStart. Backward-compatible. TF smoke
  PASS (event features change output; coord_idx changes neighborhood; paired MultiFold e2e;
  save/reload). Pure-function tests PASS (FPS guard, cloud builders, 3 schemas, no-truth-leakage).
- Omitted-muon stress closure (GPU, alpha=1.2 per-stratum muon tilt, recoil marginal fixed):
  PASS. L1(data) median per stratum: PRIOR 0.582, RECOIL-ONLY 0.581 (unchanged -> blind to
  muon), FULL-EVENT 0.043 (recovers ~93% of the gap; 13.6x better than recoil-only). Also the
  decisive recoil-vs-combined ablation (FE-E); muon-only arm = completeness, not run.
- FPS census (xps2 scaffolding): alignment PASS (MC 49.15M/data 4.12M); extended-edge PASS;
  overall eff 0.424; native misses 57.6%; Tier-1 71.9% / Tier-2 dead 28.1% (matches pilot).
- Ordinary self-consistency closure (GPU): PASS. Pseudo-data=MC reco -> push median 1.059
  (~1), (pT,p‖) marginal L1(truth, reweighted-gen) = 0.0021 (recovers MC truth to 0.2%). With
  the stress closure this brackets the estimator: moves when it should, not when it should not.
- Anchor, prior-envelope, publication coverage: DEFERRED to P5B (need the production full-event
  nominal + full extraction + complete replica manifests; P5A coverage is stress/closure only).

## P5B production launch plan (PRODUCTION DECISION GATE — DO NOT LAUNCH here)
Prerequisites (ALL required before any P5B launch):
  G1. P5A committed (this interface + tests + contract + census + stress closure).
  G2. Full-event C++ dump branches added by the active-universe C++ owner (request filed) AND
      FPS CV point-cloud loops REGENERATED with `MNV101_FULL_PHASE_SPACE=1` + the full-event
      dump → the publication full-event FPS nominal input (replaces the xps2 scaffolding).
  G3. Agent C's P3F FPS active endpoints (`active_universe_5d/fps/`) committed + gate-passed
      (for selection-complete FPS laterals). P3S standard = regression controls only.
  G4. Feature contract frozen (this file) with any reduction explicitly justified.
No recoil-only covariance component or weight transfers to the full-event estimator.

Launch order (each on the frozen full-event FPS nominal, same mask/order/edges):
  1. NOMINAL: `fullevent_fps_dataloader.build_fullevent_loaders` → MultiFold (2M subsample,
     niter2/epochs8, est-seed 42, reweight-all on full 49.2M) → PETxsec over extended-FPS grid.
     GPU ~1.1–1.3h. Freeze the reported-bin mask/cv/order here.
  2. GPU FLOOR: 1 identical-seed repeat; record before interpreting C_stat/C_ML.
  3. C_stat: coherent data+MC Poisson replicas (fixed est/split seed), replica-mean covariance,
     strict manifest. 8-GPU orchestrator (`orchestrate_gpu_node.sh`, proven) or a batch array.
  4. C_ML: PET-specific crossed (subsample-seed × TF-seed) ensemble, no Poisson.
  5. VERTICAL/FLUX SYSTEMATICS — CORRECTED END-TO-END (JOINT) CONTRACT (2026-07-16 directive):
     for each universe u / asymmetric ±endpoint that can CHANGE THE LEARNED MAPPING, apply the
     FULL physical input variation AND retrain the PET estimator TOGETHER, then
         delta_u = x_u(varied inputs + retrained estimator) - x_CV,
     and build the band covariance DIRECTLY from these complete joint shifts (declared
     experiment convention; MAT mean-centered with a separate mean-shift diagnostic). This
     already contains the nuisance/retraining interaction. DO **NOT** form
     `C_syst_fixed_model + C_retraining` — those terms share the nuisance and would require the
     cross-covariance (double count); and do NOT add a separate retraining covariance for a
     nuisance already carried by a joint end-to-end universe. Targeted-endpoint → full-per-
     universe gate per PET_UQ_REMEDIATION_STATUS.md §6 (retrain the predeclared dominant set
     first; expand only if material). A nuisance that provably CANNOT change the mapping (pure
     reweight/normalization) may use the frozen-map response, documented as such with its
     justification. (The recoil-only campaign's additive C_syst+C_retrain is a QUARANTINED
     cross-check, never transferred.)
  6. SELECTION-COMPLETE LATERALS: from Agent C's committed P3F FPS endpoints (dump→endpoint
     full-event input→JOINT retrain+extract→MAT mean-centered C_lateral). NEVER P3S standard.
  7. C_total = C_syst(end-to-end joint) + C_stat + C_ml + C_lateral on ONE mask/cv/order with
     the IDENTICAL estimator fingerprint on every component (reject on mismatch). NO separate
     additive C_retrain term (retraining lives inside the joint universes). Document each
     component's nuisance ownership + independence/coupling BEFORE summing; supply mean shifts.
     PSD/symmetry/finite-diagonal; exact 5D→4D marginal consistency; extended-edge assertion.
  8. PROJECTIONS + COMPARISONS: two-tier reporting (Tier-1 measured vs Tier-2 prior-band);
     PET-vs-scalar only after both are on the SAME extended-FPS domain. Coverage + 3-prior
     envelope on the extension regions. Report candidate vs final products separately.
Est. total ≈ recoil campaign + ~15–20% (49.2M vs 32.8M). CPU for dumps/extraction/census/tests;
GPU (shared + interactive) for trainings.
