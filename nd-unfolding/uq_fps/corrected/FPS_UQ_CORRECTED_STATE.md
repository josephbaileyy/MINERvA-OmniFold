# Corrected FPS UQ — live state (Agent C / P6-FPS)

Working-tree tracking doc for the FPS publication-completion workstream (Publication
Agent C). NOT a run receipt or a ledger. Verified numbers → `VALIDATION_LEDGER.md` at the
commit gate; chronology → ND RUN_LOG; bugs → KNOWN_ISSUES. Started 2026-07-15.

Owned: P3F FPS active event loops; FPS portion of P4 (selection-complete lateral); P6-FPS
corrected FPS UQ + adoption. Output namespaces: `active_universe_5d/fps/`, `uq_fps/corrected/`.

## Reported grid
FPS scalar covariance is the 2D (pt,p‖) **extended** grid: **285 flat bins = 15×19**.
(FPS point-cloud / PET-FPS + the model-dependence prior envelope are Agent-B PET scope,
not this scalar FPS covariance.)

## Reuse vs regenerate (validated read-only, 2026-07-15)
| Component | Verdict | Evidence |
|---|---|---|
| C_syst — `uq_fps/universe_sweep/` (CV+187) | **REUSE** | all universe unfolds + matched CV ran at `--seed 42` (sbatch_unfold_fps_universes_full.sh:49,65); `analyze_universes_nd` is MAT mean-centered |
| `bank_uthrow_fps/` (374 files, 37 GB) | **REUSE** | passes `_load_bank`-equiv schema: cv.npz + 72 knob endpoints + 100×3 flux, 15×19 grid (test PASS) |
| `of_inputs_fps.npz` | **REUSE** | all bootstrap/split fields present, 15×19 grid |
| C_stat — `boot_nd_fps/` (100) | **REGEN** | June `bootstrap_nd.py@621886c` used `seed=a.seed` for the ESTIMATOR (old contract, KNOWN_ISSUES #14) |
| C_ML — `seedscan_split_fps/` (24) | **REGEN** | June `seedscan_split.py@621886c` used `seed=args.split_seed` for the ESTIMATOR (old contract) |
| unified throw — `uq_fps/uthrow_slabs_fps/` (20+6) | **REGEN** | slabs carry NO estimator-seed stamp → corrected `unified_throw_cov.py --combine` rejects them (F2 guard); also block launcher had only 12 flux units (corrected combine needs all 100) |
| OLD `uq_fps/` covariance products | **QUARANTINE** | Jun 12–14, old contract (one-sided/CV-centered/varying seed) per KNOWN_ISSUES #14; preserved in place for provenance |

The corrected contract is enforced by the SHARED, already-committed corrected code
(`uq_math.py`, `unified_throw_cov.py`, `analyze_universes_nd.py`, `adopt_unified_4d.py`,
`combine_cov_nd.py`, `bootstrap_nd.py`, `seedscan_split.py`) — asymmetric ±1σ endpoints,
one fixed estimator seed 42, throw-mean centering with the mean shift stored separately
(`hJointMeanShift`), MAT biased 1/N, exact manifests, fixed-seed null (no jitter subtraction).

## Corrected launchers (new, Agent-C-owned; GPU-retargeted, high --nice, `uq_fps/corrected/`)
- `sbatch_bootstrap_fps_corrected_gpu.sh`     → C_stat 100 boot   → uq_fps/corrected/boot_nd_fps/
- `sbatch_seedscan_split_fps_corrected_gpu.sh`→ C_ML 24 split     → uq_fps/corrected/seedscan_split_fps/
- `sbatch_uthrow_cov_fps_corrected_gpu.sh`    → 160 throws (40×4) → uq_fps/corrected/uthrow_slabs_fps/
- `sbatch_uthrow_block_fps_corrected_gpu.sh`  → 124 block units (24 knob + 100 flux) → same dir
- `sbatch_combine_boot_fps_corrected_gpu.sh`  → uq_fps/corrected/uq_cov_stat_fps.root
- `sbatch_combine_split_fps_corrected_gpu.sh` → uq_fps/corrected/uq_cov_mlsplit_fps.root
- `sbatch_fps_budget_corrected_gpu.sh`        → uq_fps/corrected/universe_stage2_fps/…_combined.root
- `sbatch_uthrow_combine_fps_corrected_gpu.sh`→ uq_fps/corrected/unified_throw_cov_fps.root
- `sbatch_adopt_fps_corrected_gpu.sh`         → uq_fps/corrected/universe_stage2_fps/…_combined_uthrow.root
- `uq_fps/corrected/test_fps_corrected_uq.py` → FPS-specific contract test (ALL PASS 2026-07-15)

All: account m3246_g (CPU exhausted → GPU host cores for LightGBM CPU code), `--nice=1000000`
(strictly backfills; never displaces critical-path PET(B)/4D(D)/standard(A)), skip-if-exists,
`--export=ALL,HOME=/global/homes/j/josephrb` (school-acct conda trap).

## P3F active-universe launchers (PREPARED, GATED on Agent A's P2 commit)
- `sbatch_evloop_array_5d_active_laterals_fps.sh` — 120 loops (5 bands×2 endpoints×12 PL),
  MNV101_ACTIVE_UNIVERSE + MNV101_FULL_PHASE_SPACE=1 + MNV101_DUMP_POINTCLOUD=1; fail-closed
  on `MNV101_ACTIVE_BIN_SHA256` (fill from A's validated binary fingerprint). → active_universe_5d/fps/
- `sbatch_hadd_active_fps.sh` — 10 endpoint merges via the large-tree-safe merger → fps/merged/
Distinct FPS-owned files; Agent A's shared `sbatch_evloop_array_5d_active_laterals.sh` untouched.

## Resource strategy (2026-07-15)
Initial GPU-host-core run (m3246_g) validated the pipeline (boot 1,2 COMPLETED ~10min each;
totals 4.516e-38 / 4.500e-38) but competed with B(PET)/D(4D) on the shared GPU fairshare and
only trickled. **CPU hours restored (user, 2026-07-15) → migrated the whole FPS chain to CPU
`m3246`** (a SEPARATE fairshare pool from the GPU work → zero contention with B/D; uses the freed
hours). GPU FPS jobs cancelled; the 2 completed replicas kept (skip-if-exists). Per-unfold ≈10min
(285-bin grid) → throws safe at THROWS_PER=4 (≈40min ≪ 6h wall). CPU launchers = `*_corrected_cpu.sh`
(nice=0; GPU `*_gpu.sh` siblings retained for reference).

## Live jobs (CPU m3246, 2026-07-15)
- boot  55961841 (1-100, skip 1-2) — corrected C_stat
- split 55961842 (1-24)            — corrected C_ML
- throws 55961843 (0-39, TPT=4)    — corrected unified-throw slabs (160)
- blocks 55961844 (0-25)           — corrected block units (24 knob + 100 flux)
- P3F smoke 55961845 (task 0, 1A/BeamAngleX:0) — validates my P3F wrapper before the full 120

## Results landed (corrected, uq_fps/corrected/) — 2026-07-16
Reported grid = 266 bins (CV>0 of the 285 extended pt×pz cells).
- **C_stat** `uq_cov_stat_fps.root` — 100 coherent bootstrap replicas, √tr 4.339e-40, median 0.684%/bin.
- **C_ML** `uq_cov_mlsplit_fps.root` — 24 split-only replicas (fixed est seed 42), √tr 1.761e-40.
- **C_syst** (reused seed-42 187-univ sweep, MAT mean-centered) — √tr 8.027e-39, median 7.27%/bin,
  p84 18.11% (dominant: Muon_Energy_MINOS 2.47%, Muon_Energy_MINERvA 1.69%, MinosEfficiency 1.50%).
- **BLOCK-SUM COMBINED** `universe_stage2_fps/uq_universe_fps_covariance_combined.root` — syst+stat+ML,
  √tr **8.041e-39, median 7.33%/bin**, rank 222/266. Corrected contract (mean-centered, fixed seed 42,
  exact 100/24 manifests, MAT 1/N, norm 0.014). Supersedes the quarantined old FPS block-sum.
- **UNIFIED THROW + ADOPT DONE (2026-07-17, neutral policy, 160 seed-stamped throws + 124 block
  units in uthrow_slabs_fps_neutral/):** unified/block sqrt-trace ratio **0.999** (cross-term 3.5%
  of block; per-bin median 0.918) → the FPS block-sum is VALIDATED as a good approximation (unlike
  4D's ×2 nonlinearity), a measured fact now. Fixed-seed null 6.7e-52 ≪ tol. `unified_throw_cov_fps.root`
  written. Adopted (inflation transfer, g median 1.000/max 1.61, 82/266 bins>1): **pre-lateral
  corrected FPS covariance √tr 8.128e-39, median 7.49%/bin** (×1.011 vs block-sum 7.33%), PSD OK →
  `universe_stage2_fps/uq_universe_fps_covariance_combined_uthrow.root`. Autonomous supervisor
  exited cleanly. This completes the P6-FPS NON-LATERAL chain.
- P3F full campaign `55972324` LAUNCHED (120 loops ~4.75h each; multi-day). Smoke endpoint validated
  (BeamAngleX:0, isLateral=1, reco migration 241/177, 1.6M native misses, point-cloud complete).

## Invalid-ratio policy (DECLARED + VALIDATED 2026-07-16)
**Policy: `--invalid-ratio neutral`** on all FPS unified-throw + bank-block commands (matches the
committed 5D/4D decision). The FPS bank has **1803 non-positive/non-finite ratio rows across 9 files**
(GENIE negative-weight artifacts): LowQ2 +1σ (td 615, sig_r/t 437/437), HighQ2 +1σ (td 123, sig_r/t
94/94), MFP_N −1σ (1/1/1) — fraction **1.25e-5**. `neutral` holds these at CV=1 for the affected knob,
logs the count, then clips to (1e-2,1e2); post-fix 0 bad remain. Negligible, defensible, logged.
INCIDENT: my first throw/block launchers OMITTED `--invalid-ratio neutral` → default `error` aborted
every throw and the HighQ2/LowQ2 (block task 2) + MFP_N/MvRES (task 4) bank-block units. FIX: added
`--invalid-ratio neutral` to orchestrator + all throw/block/combine launchers; regenerating throws+blocks
into a CLEAN VERSIONED namespace `uq_fps/corrected/uthrow_slabs_fps_neutral/` (old dir preserved as the
failed-attempt provenance). The block-sum COMBINED covariance is UNAFFECTED (built from the sweep, not
bank blocks). Cancelled failing throw array 55961843 + redundant boot 55961841 / split 55961842 (outputs
already banked). Unified-throw result NOT claimed/committed until the neutral chain completes + validates.

## Gate order (non-lateral first; lateral is P2-gated)
1. boot=100 → combStat;  split=24 → combML
2. (reused sweep + norm 0.014 + combStat + combML) → budget → …_combined.root
3. throws=40 & blocks=26 → uthrow-combine → unified_throw_cov_fps.root
4. budget + uthrow → adopt → …_combined_uthrow.root  (VERTICAL+stat+ML adopted, pre-lateral)
5. **[P2→P3F→P4-FPS]** selection-complete FPS lateral block → FINAL adoption. GATED.

## P4-FPS plan (GATED on P3F merged endpoints; pattern confirmed 2026-07-15)
Reference (Agent A/D standard-P4 scaffolding, reuse path-parametrized): `p4_validate_active_lateral.py`
(matrix gates + active-vs-support sqrt-trace/per-bin comparison + migration census from the
endpoint `TParameter<long> activeUniverse{Truth,Reco}{Entrants,Exits}`), `run_active_lateral_unfolds_interactive.sh`.
FPS steps once `active_universe_5d/fps/merged/` exists:
1. Unfold the 10 merged FPS active endpoints (5 bands × {0,1}) on the 285-bin FPS grid via
   `unfold_nd_omnifold_unbinned.py --use-weights --estimator lgbm --seed 42 --full-phase-space
   --pt-edges <PT_EXT> --pz-edges <PZ_EXT>` (NO --universe: the endpoint IS the promoted universe)
   → `active_universe_5d/fps/unfolds/`.
2. Build C_lateral_active: per band `mat_covariance([x_b_0, x_b_1])` (MAT mean-centered, biased 1/N),
   sum 5 bands → `active_universe_5d/fps/covariance/active_scalar_lateral_fps_cov.root:hCov_..._total`.
3. Validate vs support-limited FPS lateral (sum of the 5 kinematic per-band covs in the corrected
   combined ROOT) + migration census via `p4_validate_active_lateral.py` (FPS paths/hist names).
4. FINAL adoption (P6-FPS close): replace the support-limited lateral block in the corrected FPS
   combined covariance with C_lateral_active, re-run the unified-throw inflation adopt → the
   publishable corrected FPS covariance. Old uq_fps/ stays quarantined.
NOTE: endpoint unfold invocation + merged-omnifile tree schema to be CONFIRMED against the first
P3F merged endpoint before scripting (point-cloud branches may change what the unfold reads).

## RESUME PROCEDURE (if the orchestrator/monitor is torn down by a session restart)
The dedicated-node orchestrator + login-node monitors do NOT survive a Claude process exit; the
detached `claude-hold` alloc + SLURM jobs DO (until the alloc walls). To resume the unified-throw:
1. `squeue --me --name=claude-hold` — if RUNNING and `ps -u josephrb | grep unified_throw` shows
   workers, the orchestrator is alive; just re-arm a monitor. If the alloc is GONE, relaunch:
   `cd $REPO && ./alloc_run.sh 'bash nd-unfolding/uq_fps/corrected/run_fps_uq_packed.sh'` (background).
   The orchestrator PRECLEANS partial throw/block slabs (n!=4 / wrong unit count) then resumes
   skip-if-exists at 10-wide (CORES_PER=12; memory-safe — 16-wide OOMs the 503GB node).
2. When `uthrow_slabs_fps_neutral/` has 40 throw slabs (each 4 throws) + 26 block slabs (verify
   completeness with numpy, NOT just file count), run the combine:
   `sbatch sbatch_uthrow_combine_fps_corrected_cpu.sh` (or via alloc_run) -> unified_throw_cov_fps.root.
3. Then adopt: `sbatch sbatch_adopt_fps_corrected_cpu.sh` -> ..._combined_uthrow.root (pre-lateral).
4. Lateral replacement + FINAL adoption: gated on P3F (55972324) merged endpoints (multi-day).
Env trap on alloc_run: the orchestrator self-sources with ROOT628_PREFIX; for ad-hoc alloc_run
commands prepend `export ROOT628_PREFIX=/global/homes/j/josephrb/.conda/envs/root_6_28; source setup_salloc_env.sh`.

## Dependencies / blockers
- P3F blocked on Agent A's committed P2 interface validation + A-validated binary fingerprint.
  No `active_universe_5d/` exists yet; A's C++ interface is coded but uncommitted (249-line WT diff).
- Commit gate (per campaign): launchers + exact manifests + compact summaries + ledger + ND
  RUN_LOG + ND STATUS together; never `git add -A`; do not overwrite other agents' dirty docs.
