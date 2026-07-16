# PET Publication Agent B — session state

## ⚠ SCOPE CHANGE 2026-07-16 — recoil-only PAUSED; full-event PET remediation (KNOWN_ISSUES #19)
User directive: the current PET estimator is **recoil-only** (reco = non-muon recoil
clusters; truth = hadrons with muon removed; muon/scalar arrays used only for selection +
post-hoc binning), so the learned weight is w(recoil) and the conditional muon distribution
is left at the MC prior = omitted-variable flaw. **New task:** design/implement/validate a
FULL-EVENT PET interface (distinguished muon + recoil tokens + truth tokens + global context
+ corrected neighbor geometry), stopping at the production decision gate until the feature
contract + omitted-variable stress closure pass. Do NOT launch full production yet.

**SAFE-STOP done (2026-07-16 ~09:5x UTC):** cancelled MY recoil-only orchestrator alloc
`55970263` (scancel; my job only). Shared array 55933666 already finished/cancelled. NO other
agent's job touched. **39 recoil-only replicas (ids 21-46, 88-100) + interim 42-rep C_stat are
PRESERVED as "recoil-only cross-check"** — NOT deleted, NOT promoted through the publication
gate. Old P5 shifted-cloud retrains are NOT started (paused with the recoil-only campaign).

**Findings so far (code audit):**
- `omnifold_nn/omnifold/net.py` num_evt DEAD WIRE: `PET.__init__` builds `Model(inputs=inputs_part)`
  in BOTH branches (lines ~92-97) — event features never fed even when num_evt>0. FIX:
  `Model(inputs=[inputs_part, inputs_evt], ...)`.
- `net.py` neighbor geometry: `PET_body` line ~131 `points=inputs_part[:,:,:2] #assume eta-phi`
  — KNN uses first 2 feature cols as coords, but tensors start with E + position. Padding mask
  (~line 128) keys off col-0==0. FIX: explicit coord columns (view-aware reco / angular truth) +
  explicit padding mask input.
- `nd-unfolding/pet/minerva_pet_dataloader.py` build_loaders has NO event-features path at all
  (DataLoaders carry only reco/gen clouds); `_load_pointcloud` DROPS the truth PDG column
  (gate wants it as categorical embedding) and removes muon from both reco+gen. num_evt never
  passed to the model (defaults 0).
- Step-A feature-availability audit DONE (see `pet/FULL_EVENT_INTERFACE_REQUEST.md`).
  **Verdict: the interface + stress-closure GATE can pass NOW with existing data** — muon
  pT/p‖ are already in the npz (reco/truth/measured `_scalars` cols 0,1) as the minimal
  distinguished-muon event feature; truth PDG present (`part_gen` col 4, loader drops it); W
  + `MC_hadangle` recoverable from ROOT. GENUINELY NEW (Agent A branches; getters exist, only
  `tree->Branch` fills): muon full 4-vec/φ/charge/MINOS-quality, reco/data vertex, recoil
  view-ID/timing, residual-energy tokens. Those are production-completeness items, NOT gate
  blockers. Plan: implement+validate the paired (cloud,evt) interface + omitted-variable
  stress closure + ablation using muon pT/p‖ NOW; the full muon object folds into the frozen
  feature contract + production launch once A's branches land.

### P5A PROGRESS (full-event-FPS interface, fresh namespace) — 2026-07-16
Contracts: full-event rep + extended-FPS domain (both mandatory); PET trains UNBINNED on
CONTINUOUS features, extended (pT,p‖) edges used ONLY for domain/reporting/covariance/validation
(NOT classifier inputs/bins). Three schemas (event_reco==event_data observable; event_truth
distinct; MINOS reco-only; no truth leakage). P5A NOT declared "passed" on the reduced muon set.

NEW Agent-B code (fresh namespace; net.py/dataloader.py/omnifold.py are backward-compat engine repairs):
- `omnifold_nn/omnifold/net.py`: fixed num_evt DEAD-WIRE (multi-input Model) + explicit KNN
  `coord_idx` (no accidental first-2-column geometry).
- `omnifold_nn/omnifold/dataloader.py`: optional paired `reco_evt`/`gen_evt` (strided).
- `omnifold_nn/omnifold/omnifold.py`: paired path through cache()/reweight()/RunStep1/2/LoadStart.
- `pet/fullevent_fps_dataloader.py`: full-event FPS adapter — recoil cloud (coord (1,2)), truth
  cloud (E,px,py,pz,pdg,theta,phi; coord (5,6) angular; PDG kept), event_reco/data/truth
  (continuous muon pT,p‖), FPS edge guard (fail closed), no-truth-leakage assertion.
- `pet/fps_census.py`, `pet/smoke_fullevent_tf.py`, `pet/stress_closure_muon.py`,
  `tests/test_fullevent_fps.py`, `pet/FULL_EVENT_INTERFACE_REQUEST.md`,
  `pet/FULL_EVENT_FEATURE_CONTRACT.md`.

VALIDATION RESULTS:
- Pure-function tests (login): 9/9 PASS (FPS guard accepts canonical/rejects paper+reorder;
  cloud builders + coords; 3-schema; no-truth-leakage detector).
- TF engine smoke (GPU alloc 55973913): ALL PASS — event features CHANGE output (max|Δ|=0.056,
  num_evt dead-wire fixed); recoil-only single-input intact; coord_idx changes k-NN neighborhood;
  paired MultiFold e2e (cache/train/reweight both steps); save/reload identical.
- FPS census (xps2 scaffolding): alignment PASS (MC 49.15M / data 4.12M rows); extended-edge
  PASS; overall eff 0.424; native misses 57.6% (FPS-admitted); **Tier-1 71.9% / Tier-2 dead
  28.1%** (matches FPS_PILOT ~28%). Domain integrity ok (NOT a coverage claim).
- Omitted-muon stress closure (alloc 55973942): PASS. Per-stratum L1(data) median: PRIOR
  0.582, RECOIL-ONLY 0.581 (blind), FULL-EVENT 0.043 (recovers). Decisive: recoil-only cannot
  recover the omitted muon variable; full-event does. (= FE-D + recoil-vs-combined ablation.)

BLOCKERS (documented, not gate-passable now): full muon object/vertex/view/timing branches +
FPS-CV regeneration with the full-event dump (C++ owner; request filed, not editing while P3S
runs); P3F FPS active endpoints (Agent C) for selection-complete laterals (P5B). P5A is
"interface validated + contract frozen + blockers documented", NOT "publication estimator ready".

---

**Original P1/P5 (recoil-only) record retained below for provenance / cross-check labeling.**

---

**Owner:** Publication Agent B (school account). Live tracker for THIS session's
P1/P5 execution: job IDs, decisions, gates, recovery. Durable results land in
VALIDATION_LEDGER / ND RUN_LOG / ND STATUS at the commit gate. Do NOT edit other
agents' paths (Agent A C++/active-universe/standard, Agent C FPS, Agent D 4D/shared UQ).

## Window opened 2026-07-15 (12h autonomous)

### P1 — corrected PET stat replicas 21-100 (#15) — IN PROGRESS
Goal: enlarge C_stat inventory from 20 -> 100 coherent replicas, then build a NEW
100-replica C_stat candidate. Replicas 1-20 are FROZEN (validated, reused unchanged).

**Config (identical to frozen 1-20; launcher constants):**
- payload = committed `pet/sbatch_pet_bootstrap_replica.sh` -> `minerva_pet_dataloader.py`
  (train, --reweight-all, coherent data+MC Poisson via --bootstrap-seed=RID) +
  `pet/extract_bootstrap_replica.py` (PETxsec5D, PyROOT self-reexec).
- PET_INPUTS=of_inputs_pc_fullcloud_bkgsub_5d.npz (corrected bkgsub; NOT the
  launcher's unsubtracted default), PET_W_SOURCE=of_inputs_5d.npz,
  PET_BOOT_OUTDIR=products/pet/bkgsub/bootstrap_replicas.
- train 2M events, niter 2, epochs 8, estimator seed 42, subsample seed 0.
- n_events(full MC)=32,849,103. 5D grid (14,16,7,7,6)=65856 bins; 10550 reported.

**Verified 1-20 (2026-07-15):** 5D+4D manifests PASS (finite, correct shapes,
ids 1-20); coherent-draw contract PASS on weights 1/10/20 (bootstrap seed +
ordered full mc_indices + canonical mc_bootstrap_factor). Frozen 20-rep C_stat:
per-bin rel median 7.851%, sqrt-tr 7.439e-39, 8620x floor.

**Launcher (new, Agent-B owned):** `pet/sbatch_pet_bootstrap_array.sh` — thin array
wrapper delegating to the committed single-replica payload verbatim. Routes to GPU:
`--account=m3246_g --qos=shared --constraint=gpu` (auto-maps to gpu_shared; CPU
account m3246 lost plain `shared` QOS = CPU hours exhausted). School HOME fix:
`--export=ALL,HOME=/global/homes/j/josephrb`. Logs: pet/logs/pet_boot_arr_%A_%a.{out,err}.

**Combiner (new, Agent-B owned):** `pet/combine_cstat_bkgsub_100rep.py` — strict
1-100 manifest + per-replica coherent-draw revalidation + replica-mean covariance +
gate battery (symmetry, PSD via small Gram spectrum, finite diagonal, mask==20rep,
floor comparison). Smoke-tested on 1-20: reproduces frozen product exactly
(7.851%, √tr 7.439e-39, PSD PASS, mask identical). Never overwrites the 20-rep file.

**Jobs submitted 2026-07-15:**
- 55933623  array task 21  (pilot; validates GPU-account+HOME plumbing) — COMPLETED 1h08m.
- 55933666  array 22-100%16 (79 tasks, throttle 16 concurrent; ArrayTaskThrottle=16 verified).
- Queue congested (~961->1546 pending shared_gpu); Agents C (bootfpsC/sspfpsC) + D
  (boot4dC/ssp4dC/cv4dpilot/proj54dC/budget4dC) also on gpu_shared — shared josephrb
  fairshare -> ~2 of my replicas run concurrently.

**PROGRESS 2026-07-15 ~19:45 PDT (~14h in, window over):** 22 replicas landed = ids 21-42,
ZERO failures. Total available = 42 replicas (1-42). Array tasks 43-100 (58) still PENDING
(Priority) at %16, draining. At ~2 concurrent x ~1.2h, reaching 100 needs ~another ~35h —
well beyond the window; the next session/continued drain finishes to 100.

**INTERIM 42-rep C_stat BUILT + VALIDATED (handoff checkpoint, NOT the #15 final):**
`products/pet/bkgsub/pet_cstat_bkgsub_5d_interim_42rep.npz` (+summary). Gates ALL PASS:
manifest 1-42 exact/finite; coherent-draw revalidated on ALL 42 weight files (ordered full
mc_indices + canonical mc_bootstrap_factor, n=32,849,103); symmetry 0.0; PSD (Gram min eig
-5.8e-94); finite diagonal; mask identical to 20-rep. per-bin rel median **7.927%** (20-rep
was 7.851% -> STABLE/converged), sqrt-tr 7.246e-39, 8703x floor. The frozen 20-rep product
is UNTOUCHED. When ids reach 100: rerun `combine_cstat_bkgsub_100rep.py --expected-ids 1-100
--out .../pet_cstat_bkgsub_5d_100rep.npz` for the true #15 deliverable, then the commit gate.

**ACCELERATION (2026-07-15 ~20:45 PDT, user authorized CPU+GPU / interactive+batch):**
Shared-batch fairshare (3-way with C/D) gave only ~2 concurrent. Diagnostics: sbatch to
gpu_interactive REJECTED (salloc-only); full-node `regular` batch ~10 DAYS out; `shared`
QOS caps at 0.5 node (4-GPU disallowed, 2-GPU ok but fairshare-neutral). Real lever =
INTERACTIVE QOS (separate reserved pool, grants in ~20s). Split remaining IDs disjointly:
- Shared array 55933666 reduced to `[43-70]` (kept aged priority; `[71-100]` scancel'd, 0 waste).
- Interactive 4-GPU orchestrator on `[100->71]` top-down: `pet/orchestrate_gpu_node.sh`
  (NGPU=4, 4 replicas/wave pinned via CUDA_VISIBLE_DEVICES, STAGGER 150s, skip-if-exists,
  delegates to the committed single-replica payload). Launched via
  `salloc --qos=interactive -C gpu -N1 --gpus=4 -t 03:55 srun --ntasks=1 --gpus=4 bash orchestrate_gpu_node.sh 100..71`.
  Alloc 55963301 on nid001009; id=100 training on GPU0 (seed=100 verified), no OOM.
  ~4 replicas/~1.4h wave -> ~10-12 per 3h55m alloc; RELAUNCH same cmd when the wall kills it
  (skip-if-exists resumes). Disjoint from shared [43-70] => no double-train.
Probe 55963222 validated the mechanism (4x A100-40GB, srun placement, ~20s grant).

**2026-07-16 ~07:46 UTC — orch alloc 1 (55963301) done: delivered ids 89-100 (12);
wave 4 (86-88) wall-killed (no NPZ; redone via skip-if-exists). Landed 36/80 (21-44,89-100).**
UPGRADED orchestrator to MULTI-NODE (8 GPU): `orchestrate_gpu_node.sh` now partitions IDs
round-robin by `SLURM_NODEID` (node k does ids[k::NNODES]), each node running 4-GPU waves;
NNODES=1 => single-node (unchanged). 2-node probe 55970239 validated (NODEID 0/1, 4 GPUs each).
- Shared array 55933666 reduced to just 45,46 (pending [47-70] scancel'd -> given to orch).
- 8-GPU orch alloc **55970263** on nid[001189,001192] running ids `88..47` (42 IDs):
  `salloc --qos=interactive -N2 --gpus=8 -t3:55 srun --ntasks=2 --nodes=2 --gpus-per-task=4 bash orchestrate_gpu_node.sh 88..47`.
  ~8 replicas/~1.2h wave -> ~24/4h alloc -> ~2 allocs (~8h) to finish. RELAUNCH same cmd on
  wall-kill (skip-if-exists resumes). Next relaunch range = whatever of 47-88 is still missing.

**COMMIT STATUS:** NOT committed. #15 is INCOMPLETE (42/100) so the result commit gate does
not fire (runbook P0: do not claim incomplete #15). New code (launcher/combiner/test) +
interim product summary + this state file are staged-ready in PET-owned paths. Shared docs
(ND_STATUS, OPEN_ITEMS) are dirty with other agents' edits -> not touched. Commit only on
user direction (CLAUDE.md), together with the final 100-rep product.

**Output product (planned):** products/pet/bkgsub/pet_cstat_bkgsub_5d_100rep.npz
(+ .summary.json). Frozen 20-rep pet_cstat_bkgsub_5d.npz kept as cross-check.

**Plumbing VALIDATED on the live GPU run (2026-07-15):** pilot 21 + task 22 ran on
`m3246_g`/gpu_shared with the corrected bkgsub input, coherent seed-21/22 draw, fixed
estimator seed 42 — log-confirmed. Both COMPLETED, wrote valid 5d NPZs. No failures.

**THROUGHPUT CONTINGENCY:** josephrb fairshare is 3-way contended (B/C/D) on a congested
GPU system -> only ~2 of my replicas run concurrently (~26% share). At ~1.2h/replica the
full 80 will NOT finish in a 12h window; expect a PARTIAL set. The array 55933666 keeps
draining (throttle %16 is not the limiter; system contention is). Jobs age -> priority
rises, so the rate may improve later. Plan: DO NOT emit an intermediate C_stat named
`_100rep`. Only build the true 100-rep product when all 80 (21-100) land. If the window
ends first, build a clearly count-labeled partial candidate (e.g. `_Nrep`) as a handoff
artifact and leave the array draining for the next session to complete to 100.
At each wake: scan `sacct -j 55933666,55933623` for FAILED/TIMEOUT and resubmit those IDs.

### P5 — PET shifted-cloud processing + retraining (#16) — GATED / BLOCKED
Prerequisite: Agent A commits the standard active-universe point-cloud inventory
(P3S: `active_universe_5d/standard/{BAND}_{IDX}/*.root` + `standard/merged/`) AND P4's
standard endpoint/migration manifest. As of window open only `active_universe_5d/
interface_smoke/` exists — NO `standard/` tree. A not running. Do NOT cross the gate.

**Scope:** 5 kinematic bands (BeamAngleX, BeamAngleY, MuonResolution,
Muon_Energy_MINERvA, Muon_Energy_MINOS) x 2 endpoints (idx 0,1) = 10 endpoints.
Weight-only bands (MinosEfficiency/GEANT) are NOT support-limited (already clean in
`pet_clateral_bkgsub_5d.npz`); P5 replaces ONLY the kinematic-band sub-block.

**Turnkey per-endpoint pipeline (all NEW glue — none exists yet):**
1. Merge the 12-playlist endpoint ROOTs with the large-tree-safe merger
   `2d-unfolding/uq/hadd_universes_full.py` (NOT bare hadd) ->
   `active_universe_5d/standard/merged/..._active_{BAND}_{IDX}.root`.
   Verify metadata `activeUniverseBand/Index`, `hasActiveUniverse`, `isLateral`,
   migration TParameters (Truth/Reco Entrants/Exits) resolve to the single endpoint.
2. `pet/dump_pointcloud_inputs.py --omnifile <merged> --out active_lateral/{BAND}_{IDX}/of_inputs_pc_active_{BAND}_{IDX}.npz`
   -> endpoint shifted cloud (signal+data+background clouds, 4D scalars/edges; W spliced later).
3. Endpoint bkgsub target + W source (endpoint-specific analog of
   `build_bkgsub_pointcloud_input.py`): the measured target is the ENDPOINT's own
   max(0,data-bkg)/data purity (from the active tree's data/mc_background), NOT the CV
   target. Alignment proof per endpoint (event-by-event data-scalar equality; MC CRC;
   weights finite/[0,1]). This is the "do not copy CV measured weights onto shifted
   rows without endpoint-specific alignment+bkgsub proof" gate. NEW builder needed.
4. RETRAIN (design: NOT phase7 r_u injection). P5 retrain = plain NOMINAL-config train
   on the endpoint shifted cloud: `minerva_pet_dataloader.py --inputs <endpoint_bkgsub_npz>
   --mode pointcloud --model pet --reweight-all --max-events 2000000 --niter 2 --epochs 8
   --seed 0 --estimator-seed 42 --save-weights active_lateral/{BAND}_{IDX}/weights.npz`
   (GPU). The shifted cloud/selection/bkg-target IS the systematic input; no ratio inject.
5. Extract frozen-vs-retrained via `PETxsec5D` on the endpoint cloud + endpoint W source
   (adapt `phase7_extract_compare.py`; W-source alignment gate: w_truth bit-identical).
6. Assemble MAT mean-centered (biased 1/N) selection-complete kinematic C_lateral over the
   10 endpoints on the corrected-nominal 10550 mask/cv; PSD/symmetry/finite-diag + exact
   5D->4D projection; predeclared materiality vs the frozen support-limited block.
   Output: `products/pet/bkgsub/active_lateral/pet_clateral_active_5d.npz` + response summary.

**Artifacts to BUILD (do not exist):** active-lateral endpoint builder (steps 1-3 glue),
endpoint retrain launcher (step 4, ~= nominal launcher repointed), endpoint extract+compare
(step 5, adapt phase7), C_lateral assembler (step 6, ~= pet_lateral_band_5d kinematic sub +
MAT centering). Reused unchanged: `PETxsec5D`, `dump_pointcloud_inputs.py`, materiality rule.

Preparing schema-independent pieces + this plan while blocked; NOT crossing the gate.

**2026-07-16 gate status (from Agent A handoff `active_universe_5d/AGENT_A_HANDOFF.md`,
commit `d258780 #16 P3S/P4 ... (Agent A, IN PROGRESS)`):** P5 STILL GATED.
- P3S ~39/120 done (5 bands x 2 endpoints x 12 playlists). NOT complete, no standard/merged/.
- Blocked by global /pscratch Lustre I/O contention across all 4 agents (~6.7GB/output,
  ~0 completions/hr); "full P3S many hours out." Resumable (skip-if-exists on final path).
- P4 (A) fires at 120/120: `merge_active_endpoints.sh` -> `standard/merged/
  runEventLoopOmniFold_5D_MEFHC_active_<BAND>_<EP>.root`; then unfolds+covariance.
- **P5 plan REFINEMENT:** consume A's MERGED endpoints directly (I do NOT merge raw
  playlists). Per endpoint: `dump_pointcloud_inputs.py --omnifile standard/merged/...active_<BAND>_<EP>.root`
  -> endpoint shifted cloud; then endpoint bkgsub target + retrain + extract + MAT C_lateral
  (steps 2-6 of the P5 pipeline below). Gate opens when A commits 120/120 P3S + merged.
- My PET orchestrator footprint on Lustre is LIGHT (reads one 6.2GB input, page-cached per
  node after wave 1; small writes) => not materially worsening A's P3S contention.

## Recovery / rewake notes
- Resubmit a single missing ID: `sbatch --array=<ID> --export=ALL,HOME=/global/homes/j/josephrb pet/sbatch_pet_bootstrap_array.sh`
- Build 100-rep C_stat when all land (background; weight-check ~10 min):
  `combine_cstat_bkgsub_100rep.py --expected-ids 1-100 --out .../pet_cstat_bkgsub_5d_100rep.npz`
- Before any scheduler action: squeue -u josephrb; never cancel A/C/D jobs.
