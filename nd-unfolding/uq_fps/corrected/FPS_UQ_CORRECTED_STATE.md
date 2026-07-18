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

## COORDINATION + COMMIT (2026-07-17, fe-fps orchestrator directives)
- COMMIT LANDED: 14025ba (github/main) — P6-FPS non-lateral corrected UQ + STATVAL, scoped to 32
  Agent-C files only (heavy ROOTs gitignored+fingerprinted). User-endorsed gate.
- OWNERSHIP: Agent C is SOLE owner of P3F post-processing (P4-FPS + P6-FPS-final). Agent A stands
  down from FPS post-processing at 120/120. Run the merge/audit/unfold/lateral/adoption chain ONCE.
- P3F SCHEMA LABEL: the current P3F endpoint schema is **scalar-FPS / pre-full-event**. It does NOT
  by itself unblock Agent B's publication P5B full-event laterals: the installed binary predates the
  requested full-event branches and the trees write no stable event keys. B's options (coordinate):
  (a) compact full-event feature-sidecar rerun reusing existing P3F clouds — acceptable ONLY with an
  exact fail-closed row-alignment proof (row count, ordering, scalar/weight CRC vs multiple bitwise
  arrays, active-universe metadata, migration, bkg/data alignment; ref pattern:
  MINERvA-OmniFold-fe/nd-unfolding/fe_pilot/ CRC-byte-exact join); (b) full endpoint regen after the
  C++ feature branches land. Do NOT relabel scalar-FPS clouds as full-event.
- Do NOT resubmit in uq_4d/corrected/ (comb4dCc partial-slab repair 56025478->81->83 owned elsewhere).

## P4-FPS -> P6-FPS-FINAL CHAIN (run ONCE at P3F=120/120; all launchers ready, Agent-C namespace)
1. MERGE: `sbatch_hadd_active_fps.sh` (array 0-9) -> active_universe_5d/fps/merged/ (10 endpoint
   omnifiles, large-tree-safe SetMaxTreeSize; 12 playlists per band/endpoint).
2. AUDIT: verify each merged endpoint metadata (activeUniverseBand/Index/isLateral), migration census,
   native misses, POT add-up by playlist (per P2 gates); reject invalid sums.
3. UNFOLD: `sbatch_unfold_active_fps.sh` (array 0-9) -> fps/unfolds/fps2d_xsec_active_{BAND}_{IDX}.root
   (FPS 285-bin grid, seed 42, NO --universe).
4. LATERAL COV: build C_lateral_active = sum_b mat_covariance([x_b_0, x_b_1]) (MAT mean-centered) ->
   fps/covariance/active_scalar_lateral_fps_cov.root:hCov_..._total. [builder TBD at unfold-time]
5. VALIDATE: `p4_validate_active_lateral.py` (path-parametrized) active-vs-support-limited + gates.
6. FINAL ADOPT (P6-FPS close): replace the support-limited lateral block in
   uq_fps/corrected/universe_stage2_fps/uq_universe_fps_covariance_combined.root with C_lateral_active,
   re-run adopt -> the publishable corrected FPS covariance. Old uq_fps/ stays quarantined.

## P4-FPS CHAIN — SCRIPTED & READY (2026-07-17; "builder TBD" now RESOLVED)
P3F array 55972324 = 120/120 COMPLETE. Merge FIRED: **56041972** (`sbatch_hadd_active_fps_cpu.sh`,
CPU m3246 — hadd is pure I/O, no GPU; the GPU variant hit the 32-core/GPU shared-queue floor).
Downstream launchers/scripts all syntax-checked; run IN ORDER, each gated on the prior:
1. MERGE  -> `sbatch_hadd_active_fps_cpu.sh` (array 0-9) -> active_universe_5d/fps/merged/ 10 omnifiles
   `runEventLoopOmniFold_5D_FPS_active_<BAND>_<EP>_universes_full.root` (SetMaxTreeSize; 12 playlists).
2. AUDIT  -> `python3 audit_merged_fps.py --out active_universe_5d/fps/covariance/audit_merged_fps.json`
   Hard gates per merged endpoint: 4 unfold trees nonzero (mc_signal_reco/mc_background/data/
   mc_truth_denom), POT dataPOTUsed/mcPOTUsed>0 (TParameter<double> hadd-SUMMED), hasTruthOnlyMisses,
   identity band/idx/isLateral/hasActive (TParameter 'f'=kFirst so merged idx==EP not 12*EP),
   migration census (TParameter<long> hadd-SUMMED) nonzero. NO unfold until PASS.
3. UNFOLD -> `sbatch sbatch_unfold_active_fps.sh` (array 0-9, CPU). Output RENAMED to carry the
   `_uni_full_<BAND>_<EP>` token: `active_universe_5d/fps/unfolds/fps2d_xsec_MEFHC_5iter_lgbm_uni_full_<BAND>_<EP>.root`
   so analyze_universes_nd.py's UNI_RE groups the +/- endpoints by band. FPS 285-bin grid, seed 42,
   NO --universe. Gate: 10/10 unfolds present.
4. LATERAL COV (reuse canonical builder, N=2 -> MAT mean-centered +/-1sigma outer-product):
   `python3 analyze_universes_nd.py --cv uq_fps/universe_sweep/fps2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root
     --glob 'active_universe_5d/fps/unfolds/fps2d_xsec_MEFHC_5iter_lgbm_uni_full_*_?.root'
     --outdir active_universe_5d/fps/covariance --out-root active_scalar_lateral_fps_cov.root`
   -> hCov_universe4d_total (5 active bands) + per-band. (NO --add-norm / --bootstrap-cov: pure lateral.)
5. VALIDATE (my namespace; avoids editing Agent A's in-progress p4_validate_active_lateral.py):
   `python3 p4_validate_active_lateral_fps.py
     --active active_universe_5d/fps/covariance/active_scalar_lateral_fps_cov.root:hCov_universe4d_total
     --support uq_fps/corrected/universe_stage2_fps/uq_universe_fps_covariance_combined.root
     --out active_universe_5d/fps/covariance/p4_active_lateral_fps_summary.json`
   Hard gates finite/PSD/asym on active + active-vs-support (hCov_universe4d_<band>) sqrt-tr/per-bin.
6a. SWAP (PSD-safe SUM, not subtraction): `python3 adopt_active_lateral_fps.py`
   -> uq_fps/corrected/universe_stage2_fps/uq_universe_fps_covariance_combined_activelat.root
   (hCov_combined4d_total = SUM non-lateral universe4d bands + stat + ML + active lateral; all per-band
   blocks incl the 13 verticals copied through for the uthrow adopt; sum-vs-sub cross-check reported).
6b. FINAL uthrow adopt (reuse adopt_unified_4d.py, path-parametrized):
   `python3 adopt_unified_4d.py --uthrow uq_fps/corrected/unified_throw_cov_fps.root
     --combined uq_fps/corrected/universe_stage2_fps/uq_universe_fps_covariance_combined_activelat.root
     --prod uq_fps/universe_sweep/fps2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root
     --out uq_fps/corrected/universe_stage2_fps/uq_universe_fps_covariance_combined_uthrow_activelat.root`
   = PUBLISHABLE corrected FPS covariance (VERTICAL inflation + stat + ML + selection-complete lateral),
   superseding the pre-lateral ..._combined_uthrow.root. PSD-checked by construction.
Steps 2,4,5,6 are light ROOT ops (run via alloc_run or a tiny CPU batch); steps 1,3 are the arrays.
New files this session: audit_merged_fps.py, p4_validate_active_lateral_fps.py, adopt_active_lateral_fps.py.

## P4-FPS PROGRESS (2026-07-17)
- MERGE 56041972: DONE 10/10 (all COMPLETED 0:0). 10 endpoint omnifiles ~74GB each in fps/merged/.
- AUDIT (audit_merged_fps.py): **PASS 10/10** (active_universe_5d/fps/covariance/audit_merged_fps.json).
  Hard gates OK on all 10: 4 trees nonzero (sig 49.9M, bkg ~566k, data 4.12M, truthdenom 49.9M),
  POT hadd-summed data=1.057e21/mc=4.978e21 (identical across endpoints = same 12-playlist exposure),
  identity band/idx/isLateral=1/hasActive=1, hasTruthOnlyMisses present.
  6 WARNINGS (expected): MuonResolution/Muon_Energy_MINERvA/Muon_Energy_MINOS x{0,1} have ZERO
  selection-migration. **DURABLE FINDING (not a bug):** in FPS (muon truth cuts dropped, no reco
  momentum cut crossed at +/-1sigma) an energy/momentum lateral shift drives (pt,pz) BIN migration,
  not selection entrant/exit; only the ANGLE bands (BeamAngleX/Y, ~4800 each) cross the angle cut.
  Cheap decisive check confirmed ALL 5 shifts ARE applied (endpoints differ per-event, same event
  ordering: MuonRes sim_pz rel 1e-2, MINOS 3e-2 + w_reco, BeamAngleX 1.5e-4, MINERvA 4e-6 -- tiny
  because MINOS dominates forward-muon p||). So migration-census is a WARN, not a hard gate (matches
  canonical p4_validate_active_lateral.py); real applied-check = nonzero downstream covariance (step 5).
- UNFOLD 56057327 (batch array, shared QOS): stuck ~6.5h unscheduled on the depressed shared QOS
  -> CANCELLED. Migrated to fast INTERACTIVE QOS. NODE SWAP w/ Agent A (both holders named
  claude-hold -> my RUNNING-poll landed on A's): I run on **56076877** (nid004149, 3h wall
  ~08:32 UTC 07-18, timeleft ~2h @ 06:31), A takes my **56076881** (nid004178). Do NOT touch 56076881.
  squeue %S/%e are Pacific, %L absolute. Driver `run_active_fps_unfolds_interactive.sh` (NEW; mirrors
  sbatch_unfold_active_fps.sh exactly -- Agent A's run_active_lateral_unfolds_interactive.sh FPS=1
  is MIScONFIGured for FPS: standard _MEFHC_ filename + --axes eavail,q3,W, not FPS scalar-2D) runs
  the 10 unfolds as `srun --overlap` steps, CONC=5 CPT=24, skip-if-exists, detached (setsid),
  logs in fps/unfolds/unfold_<BAND>_<EP>.log + driver p4fps_unfold_driver.log. Wave 1 (5) RUNNING.
  One-node / 2-job interactive cap shared with Agent A's standard chain -- do NOT grab a 2nd node.
  RESUME if walled with stragglers: re-grab interactive (or regular-QOS) holder, rerun the driver
  with JOBID=<new id> (skip-if-exists resumes only missing endpoints).
- TRUNCATION GUARD (NEW fps_unfold_complete.py): a wall-killed unfold leaves a present-but-truncated
  .root (kRecovered / missing hXSecND_flat) that a naive -s skip would consume. The driver skip now
  VALIDATES COMPLETENESS via srun (login node has no ROOT): TFile opens & not kRecovered, hXSecND_flat
  285 bins all-finite sum>0, globalCompleteness finite. Fail -> rm + redo. Self-tested: wave-1 5/5 OK
  (sum ~5.4e-37 gc=1.0000). NB: the skip-check srun MUST `export ROOT628_PREFIX` before sourcing
  (school-acct conda trap) or the check errors on every file and wrongly redoes good outputs.
- WAVE STATUS @ 07:22 UTC: wave-1 5/5 complete+validated; wave-2 (MuonResolution_1, Muon_Energy_MINERvA
  _{0,1}, Muon_Energy_MINOS_{0,1}) running, 56076877 wall ~08:32 UTC -> last stragglers may truncate.
- 56076877 WALLED 08:32 as expected; wave-2 5 were cleanly ABSENT (not truncated -- they write only at
  the end). RESUMED @ 08:39 on FRESH holder **56080370** (nid004149, job-name claude-hold-cfps to avoid
  A's claude-hold on nid004178; poll by JOBID). fps_unfold_complete.py --all = 5 valid + 5 missing.
  Driver rerun (detached setsid, JOBID=56080370): validated+SKIPPED the 5 complete, RELAUNCHED the 5
  missing (all 5 concurrent, LightGBM training). 4h wall ~12:38 UTC -- ample for ~1.5h unfolds + chain.
  Log: fps/logs/p4fps_unfold_driver2.log. Next: when fps_unfold_complete.py --all==10/10 -> cov chain.
## 2026-07-18 FAIL-CLOSED REPAIR ROUND (purity controls quarantined; negweight-refined preflight repaired; production still gated on independent re-review)
BLOCKER (orchestrator reconciliation + Codex `fps-adopt-verifier` BLOCK): both FPS unfold launchers
omitted `--bkg-mode`, so the ten endpoint unfolds ran with the unfold DEFAULT `--bkg-mode=purity`.
They are **PURITY CONTROLS, not publication inputs**. Selected footing = `negweight-refined` (literal
bkg injection + Stay-Positive). No covariance/adoption ran (prior action turn 429'd before execution).
This turn: NO holder, NO covariance build, NO adoption, NO endpoint reruns -- repair + read-only audit only.
Delivered (all Agent-C-owned, ROOT-free where run):
- `fps_provenance.py` (NEW) -- fail-closed gate library (manifest inventory/fingerprints/footing;
  active-rollup 5-band + total identity; reported-mask binding; pure-sum-vs-subtraction residual;
  zero-block/nonzero-unified; path alias; final-adoption identity reconstruction; PSD). 24/24 ROOT-free
  tests pass (`tests/test_fps_provenance.py`, NEW).
- `fps_build_control_manifest.py` (NEW) -> read-only `active_universe_5d/fps/covariance/fps_control_manifest.json`
  (0444, label=**purity-control**, 10/10 SHA-bound, footing bkg_mode=purity recovered from launcher/source;
  publication gate REJECTS it). EVIDENCE-BLOCKED if any footing unprovable.
- HARDENED (gated producers, NOT run this turn): `build_active_lateral_fps.py` (NEW rollup, requires
  negweight-refined publication manifest + 5 nonzero bands + total==sum), `p4_validate_active_lateral_fps.py`
  (+manifest/mask/5+5 inventory/per-band-trace/total-identity/audit-fingerprint), `adopt_active_lateral_fps.py`
  (+HARD pure-sum==subtraction gate, superseded support blocks renamed `*__SUPERSEDED_support`, full source/code
  provenance, path-alias), `adopt_unified_fps.py` (NEW hardened uthrow wrapper: dim/order equality, reject
  zero-block<nonzero-unified, path-alias, C_final identity reconstruction, hJointMeanShift preserved+mean-centered).
- Launchers patched (`sbatch_unfold_active_fps.sh`, `run_active_fps_unfolds_interactive.sh`): explicit
  `--bkg-mode negweight-refined` guard, SEPARATE `unfolds_negweight_refined/` namespace, atomic tmp->mv,
  mode-stamped `.config.json`. Purity controls in `unfolds/` PRESERVED unchanged.
RESIDUAL EVIDENCE GAPS: (1) full SHA256 of the ten ~74GB merged inputs deferred (bounded head/tail
fingerprint + audit receipt used); (2) 285->266 reported-mask hash DEFERRED to ROOT rollup time (bound via
central_cv_sha256). PRODUCTION REMAINS GATED: next C turn (ten negweight-refined endpoints -> covariance ->
adoption) only after `fps-adopt-verifier` PASS on this patch. Proposed publication namespace:
`active_universe_5d/fps/unfolds_negweight_refined/`.

## (pre-reset) RESUME (next ping, after 56076877 walls): (1) grab a FRESH interactive holder (job-name claude-hold;
  poll by JOBID not name to avoid A's node); (2) `srun ... fps_unfold_complete.py --all` to see which of
  the 10 are complete; (3) rerun `JOBID=<new> bash run_active_fps_unfolds_interactive.sh` (validates +
  rm/redoes truncated, skips complete); (4) gate: require 10/10 `--all` PASS BEFORE cov; then
  LATERAL COV (analyze_universes_nd.py) -> validate -> swap -> adopt, all via srun into the fresh holder.
  Do NOT start cov/validate/swap/adopt until fps_unfold_complete.py --all == 10/10.
