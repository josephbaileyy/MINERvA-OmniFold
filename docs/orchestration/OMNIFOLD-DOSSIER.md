# OmniFold full-phase-space dossier (fe-fps-campaign)

Orchestrator: Fable (this campaign). Started 2026-07-16 ~16:45 PT. Method: `orchestration-guide.md`.
Canonical science docs are NOT restated here (one home per fact): the feature contract is
`nd-unfolding/pet/FULL_EVENT_FEATURE_CONTRACT.md`, the gate is `docs/OPEN_ITEMS.md` §PET
full-event + FPS measurement-domain gate (KNOWN_ISSUES #19), the packet assignments are
`docs/PUBLICATION_COMPLETION_RUNBOOK.md` (this campaign = Packet P5 verification + graduation slice).

## Objective

Graduate OmniFold from the small scalar observable set — 2D (pT,p‖) → 5D (pT,p‖,Eavail,q3,W),
recoil-only PET cross-check — to the **full available phase space**, operationally defined as
BOTH, per OPEN_ITEMS #19 (they are independent and both mandatory):

1. **Full-event representation**: classifier conditions on the whole observed event — recoil
   point cloud + distinguished muon event features (P5A reduced set = continuous muon {pT,p‖};
   production set = full muon 4-vec/charge/MINOS quality + vertex + view/timing + residual
   summaries, pending C++ branches) at reco/data; truth hadron cloud (with PDG) + truth muon at
   gen. Three schemas; detector-only features never at truth; no truth-only feature at step 1.
2. **Extended-FPS measurement domain**: truth gate `MNV101_FULL_PHASE_SPACE=1` (four muon cuts
   lifted, tracker fiducial retained), canonical extended (pT,p‖) edges incl. catch bins
   (fail-closed guard), two-tier reporting: Tier-1 acceptance-supported (eff≥2%, 71.9% of truth
   rate) vs Tier-2 prior-dominated (28.1%). Representation can never buy acceptance: dead cells
   stay a labeled, prior-dependent extrapolation tier.

"Full phase space" is NOT: a recoil-only cloud (that is a representation cross-check), nor a
truth-space expansion beyond the declared FPS fiducial, nor a claim about zero-efficiency cells.

Background doc: `docs/GREGOR_FOUNDATION_MODEL_REFERENCE.md` (informs P5B representation
refinements + pretrained-init pilot; not evidence of estimator validity).

## Authoritative inputs

| item | path | version/hash | owner | notes |
|---|---|---|---|---|
| P5A interface + rig | commits 9d353e1, 7d365be, 36ab84d, 2fa1308, b7ba96f (on main) | in git | Agent B (dormant) | engine repair + adapter + closures |
| FPS xps2 scaffolding npz | `nd-unfolding/of_inputs_pc_fps_xps2.npz` (9.0 GB, 2026-07-05) | sha256 → `fe_verify/logs/fe5v_input_sha256.txt` (job 56003372) | shared, read-only | right gate+edges, recoil-only tensors; muon {pT,p‖} in `_scalars` cols 0,1 |
| 5D scalar FPS xps2 npz | `nd-unfolding/of_inputs_5d_fps_xps2{,_wsource}.npz` | — | shared, read-only | scalar anchor chain |
| Recoil-only PET FPS weights | `products/pet/pet_weights_fps_xps2*.npz` | — | Agent B legacy | ablation comparison only; never promoted |
| Engine | `omnifold_nn/omnifold/{net,dataloader,omnifold}.py` @ HEAD 40f94ed | in git | shared | multi-input + coord_idx + paired path |
| My verification copies | `MINERvA-OmniFold-fe/nd-unfolding/fe_verify/fe_*.py` | `fe_verify/PROVENANCE_SHA256.txt` | me | seed/scale/path edits only |

## Frozen partitions / seeds

P5A rig: estimator seed 42 policy reserved for production (contract). My verification runs:
seed 0 = reproduction of B's numbers, seed 1 = robustness; closure at 12k (repro) and 48k
(scale). Pilot slice (task 5): subsample 2M with recorded seed, reweight-all over full 49.2M.

## Acceptance gates — campaign slices (declared before reading results)

**V-slice (P5A independent verification), promotes CLM-001..005:**
- V1 codex deep audit: no BLOCKER defect in engine/adapter/rig.
- V2 claude-school adversarial: no claim BROKEN; EVIDENCE-GAP allowed but must be recorded.
- V3 agy design critique: advisory input to pilot checklist (no gate).
- V4 my GPU re-runs (job 56003372): stress closure verdict PASS at BOTH seeds with
  recoil-only median ≥0.5×prior AND full-event median <0.5×recoil-only (B's predeclared
  thresholds); ordinary closure PASS at 12k seed0 AND 48k seed1 (L1<0.10, |median push−1|<0.15);
  census reproduces eff 0.424 / Tier-2 28.1% to 3 significant figures; tests 9/9.
- Failure action: defect goes to KNOWN_ISSUES-style record in CLAIMS.md as REFUTED + report to
  user; no silent fixes to Agent B's files.

**P-slice (end-to-end pilot, promotes CLM-006):** train full-event reduced-schema on xps2 2M
(niter 2, epochs 8), reweight-all 49.2M, extract extended-grid (pT,p‖) xsec, two-tier split.
Gates: finite push weights + ESS/max-weight recorded; extraction finite everywhere reported;
Tier-1 comparison vs GBDT FPS scalar central — predeclared tolerance: median |ratio−1| ≤ 10%
in Tier-1 (matches FPS anchor experience 0.65–1.03%, generous for a representation change and
2M train); recoil-only vs full-event ablation mapped (differences reported, no tolerance —
first measurement of the conditioning effect). NOT a publication result; estimator ID
explicitly `pet-fullevent-fps-pilot0` (never `pet-fullevent-fps-v1`).

## Claims index

`docs/orchestration/CLAIMS.md` (CLM-001..006 initialized this session).

## Collision map (2026-07-16 16:45 PT snapshot; re-check `squeue -u josephrb` before every submit)

| owner | Slurm | namespaces (READ-ONLY to this campaign) |
|---|---|---|
| Agent A — P3S standard active loops | `ev5d_active` 55985231 array (%4) | `nd-unfolding/active_universe_5d/standard/`, `nd-unfolding/logs_active/`, `nd-unfolding/evloop_work_5d_active_standard_*` |
| Agent C — P3F FPS active loops | `ev5d_active_fps` 55972324 array (%16) | `nd-unfolding/active_universe_5d/fps/`, `evloop_work_5d_active_fps_*` |
| Agent C/D — P6-4D corrected UQ | `uthr4dCc` 55971614 → `comb4dCc` 55971617 → `adopt4dCc` 55971619 (dependency chain) | `nd-unfolding/uq_4d/corrected/` |
| P6-FPS corrected UQ (staged) | none seen queued | `nd-unfolding/uq_fps/corrected/` + untracked `sbatch_*fps_corrected_*.sh` |
| Interactive session (claude personal, PID 1408359) | `claude-hold` 55994802 (in active use — steps running) | `2d-unfolding/uq/{negweight_uni,purity_newomni}/`, `2d-unfolding/ibu_omnifold_paired_cdelta.py`, `2d-unfolding/HANDOFF_bkg_negweight/` |
| Agent B — PET publication (dormant, handoff written) | none | `nd-unfolding/pet/*` untracked leftovers, `products/pet/bkgsub/`, session state `PET_P1_P5_SESSION_STATE.md` |
| Whole dirty working tree | — | 124 dirty/untracked paths owned by the above; I never edit/stage any of them |

**This campaign's disjoint namespace:** worktree `/pscratch/sd/j/josephrb/MINERvA-OmniFold-fe`
(branch `fe-fps-campaign` @ 40f94ed); Slurm job prefix `fe5*` (fe5v_* verification, fe5p_*
pilot); outputs under the worktree only; delegate prompts/outputs in
`MINERvA-OmniFold-fe/orchestration_runs/`; docs/orchestration/ NEW files only. I do NOT use
`alloc_run.sh`/`claude-hold` (another session's live allocation). GPU via `--qos=shared
--constraint=gpu` sbatch only.

**Deliberate deviations from the kit README (recorded):** no root `CLAUDE.md` creation and no
AGENTS.md template merge while four concurrent sessions read those files mid-campaign —
changing shared instruction files under running agents is an interference risk. Revisit at
campaign close.

## Meta / usage

Delegates per `orchestration-guide.md` §1, invocation forms verified for THIS machine
(`.bashrc`): codex `CODEX_HOME=$RH/codex-homes/{personal,school}`, claude-school
`HOME=$RH/claude-homes/school claude`, agy `$RH/.local/bin/agy` (RH=/global/homes/j/josephrb;
sessions run with redirected $HOME — always use absolute paths). codex-school exhausted until
~17:44 PT; claude-school ~68% used (resets ~16:56 PT); codex fresh; agy effectively uncapped
(BEN-017). Fable = coordination/verification only.
