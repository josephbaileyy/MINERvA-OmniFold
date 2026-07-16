# Agent A handoff — #16 standard active-universe chain (P0/P2/P3S/P4)

Live as of 2026-07-15. Owner: Publication Agent A (integration lead). This is a
working handoff, not a results claim. Verified numbers belong in the ledger; this
file points to state and the completion recipe.

## Completed + committed
- **P0 (reconciliation):** committed only Agent A's own interface; left all other
  concurrent-session dirty files untouched (07-13 corrected-UQ/negweight batch,
  the live 07-15 `OPEN_ITEMS.md`/`ND_OMNIFOLD_STATUS.md` doc edits, Agent D's
  `tests/test_uq_remediation.py`). Ownership inventory in the job tmp.
- **P2 (#16 interface validation): DONE, committed+pushed `2e8c214`.** Rebuilt +
  installed `runEventLoopOmniFold` from current source
  (md5 `e63c74961d699313ef155065fc790ff1`, 383448 B, 9 ACTIVE_UNIVERSE strings).
  All gates pass on the 1A smoke: 20/20 unit tests; invalid band/index fail
  closed; CV smoke zero census; `BeamAngleX:0` endpoint isLateral=1, reco
  migration entrants/exits 21/21 (truth 0/0); completeness 1.000000; native
  misses rebuilt; point-cloud branches complete on all 4 trees under
  `MNV101_DUMP_POINTCLOUD=1` (incl. new background `part_reco_*`); FPS distinct
  (×1.52). Record: `active_universe_5d/INTERFACE_VALIDATION.md` + `interface_smoke/`.

## In progress
- **P3S (standard active event loops, 5 bands × 2 endpoints × 12 playlists = 120):**
  ~39/120 done (see `active_universe_5d/standard/<BAND>_<EP>/`). Running via
  `run_active_laterals_interactive.sh` on a CPU-interactive salloc at MAX=40.
  **Throughput is blocked by global /pscratch (Lustre) contention** — all four
  agents (B PET, C FPS, D 4D, A) do heavy I/O concurrently. Each output is
  ~6.7 GB (point clouds required for Agent B's P5). Measured: ~0 completions/hr at
  BOTH MAX=12 and MAX=40; loops progress at only ~20–40 MB/min toward 6.7 GB, so
  the current in-flight batch needs ~3 h to yield its first completions and full
  P3S is many hours out. Loops are progressing (state D, I/O-wait), NOT broken.
  Fully resumable: skip-if-exists on the FINAL path.

## Remaining dependencies
- P3S must reach 120/120 before P4. P4 (this agent) and P5 (Agent B, shifted
  clouds) both consume the P3S outputs. Full 5-band coverage is the publication
  gate (#16); the presentation is closed and does not require it.

## How to finish P3S (relaunch on wall/preempt)
Interactive walls are 4 h and preemptible; on exit, relaunch (skip-if-exists resumes):
```
MAX=40 salloc -N2 -C cpu -q interactive -A m3246 -t 04:00:00 \
  bash nd-unfolding/run_active_laterals_interactive.sh
```
(GPU variant: `-C gpu -q interactive --gpus=8`, orchestrator srun already uses
`--gres=none`.) A non-preemptible CPU **batch** array
`sbatch_evloop_array_5d_active_laterals.sh` exists but CPU-shared fairshare is
depleted (`--test-only` start weeks out); do not run it AND the interactive
orchestrator to the same dir (shared workdir names → writer race).
Concurrency does not help under contention — the real unblock is B/C/D draining
their I/O, or writing outputs to node-local tmpfs (untried optimization).

## P4 completion recipe (fire when 120/120 land)
1. `bash nd-unfolding/merge_active_endpoints.sh` (inside a compute alloc) →
   `active_universe_5d/standard/merged/runEventLoopOmniFold_5D_MEFHC_active_<BAND>_<EP>.root`
   (hadd_universes_full.py, 12 playlists each, skip-if-exists).
2. `MAX=8 salloc … bash nd-unfolding/run_active_lateral_unfolds_interactive.sh` →
   `active_universe_5d/standard/unfolds/5d_xsec_MEFHC_5iter_lgbm_uni_full_<BAND>_<EP>.root`
   (nominal 5D unfold per merged endpoint, NO `--universe`, `--seed 42` on both
   endpoints so the MAT ±pair cancels CV).
3. `cd nd-unfolding && python3 analyze_universes_5d.py --cv products/5d/xsec_5d_MEFHC_5iter_lgbm.root
   --glob 'active_universe_5d/standard/unfolds/5d_xsec_MEFHC_5iter_lgbm_uni_full_*_?.root'
   --outdir active_universe_5d/standard/covariance --out-root active_scalar_lateral_5d_cov.root`
   → `hCov_universe5d_total` = selection-complete scalar lateral block (10694 mask).
4. `python3 p3s_manifest_summary.py --mode standard` (receipt) and
   `python3 p4_validate_active_lateral.py --active active_universe_5d/standard/covariance/active_scalar_lateral_5d_cov.root:hCov_universe5d_total
   --support uq_5d/universe_stage2_5d/uq_universe_5d_covariance_combined.root
   --merged-dir active_universe_5d/standard/merged
   --out active_universe_5d/standard/covariance/p4_active_lateral_summary.json`
   (PSD/symmetry/finite-diag + support-limited-vs-active comparison + migration accounting).
5. Commit gate (P3S then P4): launcher/merge/unfold/cov/validate code + exact
   120-file manifest + summary + ledger + ND RUN_LOG + ND STATUS together. Do not
   overwrite the support-limited block; leave old adopted covariances quarantined.
   Downstream: standard → final 5D adoption (`adopt_unified_5d.py` re-run), 4D
   projection, P5.

## Coordination — do NOT touch (other agents)
- B: `55963058` (claude-hold / orchestrate_gpu_node, PET), `pet_boot_arr`.
- C: `ev5d_active_fp` (P3F FPS via this launcher, FPS=1), `bootfpsC`/`sspfpsC`.
- D: `p6_4d_rep` / `boot4dC` / `ssp4dC` / `cv4dpilot` (corrected 4D UQ).
- Namespaces off-limits: `products/pet/*`, `uq_fps/corrected/`,
  `active_universe_5d/fps/`, `uq_4d/corrected/`.
