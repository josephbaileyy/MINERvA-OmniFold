# P6-4D corrected UQ — execution tracker (Publication Agent D)

Working-tree tracker for the corrected independent 4D (pt,pz,Eavail,q3) covariance.
Not a canonical doc; canonical entries go to VALIDATION_LEDGER / ND_OMNIFOLD_RUN_LOG /
ND_OMNIFOLD_STATUS at the commit gate. Started 2026-07-15.

## Scope (P6-4D, per PUBLICATION_COMPLETION_RUNBOOK.md + session brief)
Rebuild the 4D covariance under the corrected contract (actual asymmetric ± endpoints,
one fixed estimator seed, throw-mean centering with a separately stored mean shift,
MAT biased 1/N block comparator, zero fixed-seed null, no scalar jitter subtraction,
exact throw/block/replica manifests). Write ONLY to `uq_4d/corrected/`; keep the old
June `uq_4d/` + top-level `uq_cov_{stat,mlsplit}_4d.root` as quarantined provenance.
Final adoption (selection-complete lateral swap) GATED on Agent A's committed standard
lateral block. Do NOT rerun the 4D central event loop or central unfold.

## Inventory / reuse decisions (2026-07-15)
- **Central (FROZEN, reuse):** `products/4d/xsec_4d_MEFHC_5iter_lgbm.root` (Jun 4);
  reported bins = 4830 / 10976, C-order (pt14,pz16,Eavail7,q37).
- **Universe sweep (reuse):** `uq_4d/universe_sweep/` 187 files (44 knobs + Flux×100),
  Jun 4-5. Background-CV; KNOWN_ISSUES #13 proved background-CV is a <0.3% null-effect
  in 5D → reuse for C_syst. Muon-reco lateral bands are support-limited (label).
- **boot_nd_4d / seedscan_split_4d (REGENERATE):** archived to `*_prehm_20260711`
  (empty active dirs). The June replicas are pre-remediation: corrected `bootstrap_nd.py`
  (07c18ae) fixes the estimator seed at 42 (old code varied it with the bootstrap seed —
  KNOWN_ISSUES #14) and decorrelates the data/MC Poisson draws (rng_d=seed, rng_m=seed+1e7).
  → regenerate 100 boot + 24 ml-split into `uq_4d/corrected/`.
- **bank_uthrow_4d + 3D bank_uthrow + 4D universes-full omnifile: GONE.** Rebuilt the 4D
  throw bank from the surviving `bank_uthrow_5d` via `assemble_bank_4d_from5d.py`:
  5D bank is event-aligned to of_inputs_4d (w_truth/w_reco BYTE-IDENTICAL, pt/pz/Eavail
  cols identical, edges identical 14/16/7/7); the 372 per-event universe-ratio weight
  arrays are binning-independent → symlinked. q3 + measured_weights taken from
  of_inputs_4d (5D q3 has 1327 extra NaNs; measured target is per-dimension). Truth-denom
  td_* taken from the 5D bank (truth is dimension-agnostic; CV-reproduces-central pilot
  proves the binning). NO event loop needed.

## Pipeline (all outputs → uq_4d/corrected/)
1. C_stat: `sbatch_bootstrap_4d_corrected_gpu.sh` (100, seed=id, est-seed 42) → boot_nd_4d/
2. C_ML:   `sbatch_seedscan_split_4d_corrected_gpu.sh` (24, split-seed=id, est-seed 42) → seedscan_split_4d/
3. budget: `sbatch_combine_4d_corrected_gpu.sh` = combine_cov_nd (stat 1-100, ml 1-24, exact ids)
   + analyze_universes_nd (sweep block-sum + norm 0.014 + stat + ML) → universe_stage2_4d/uq_universe_4d_covariance_combined.root
4. unified throw: `sbatch_uthrow_cov_4d_corrected_gpu.sh` (160 throws, TPT=4, seed 1000)
   + `sbatch_uthrow_block_4d_corrected_gpu.sh` (124 units: 24 knob + 100 flux)
   + `sbatch_uthrow_combine_4d_corrected_gpu.sh` (--expected-throws 0-159 --null) → unified_throw_cov_4d.root
5. adopt (candidate, mean + cv-centered): `adopt_unified_4d.py` inflation-transfer on the
   sweep vertical block → universe_stage2_4d/uq_universe_4d_covariance_combined_uthrow{,_cvcentered}.root
   (support-limited lateral; FINAL lateral swap GATED on Agent A).

## P7 prep (candidate, not quoted until governing 5D cov is final)
- `project_cov_nd.py`: M C M^T marginalization, width-weighted M (density convention),
  reported-mask remap. Unit-validated ROOT-free. Covers 5D→4D (drop W), 4D→3D/2D/1D.
  Dry-run on the CURRENT committed adopted 5D → uq_4d/corrected/projections_candidate/.

## Jobs / gates (update as they land)
- (see bottom, appended chronologically)

## Dependency waits
- FINAL 4D adoption (lateral swap) waits for Agent A's committed selection-complete
  standard lateral block. All non-lateral components + candidate mean/cv adopted covs
  are built and validated without crossing that gate.
- P7 final projected numbers wait for Agents A–C committed governing covariances.

## Log
- 2026-07-15: replicas launched (boot4dC 55933683, ssp4dC 55933684, GPU host cores);
  budget4dC 55934187 queued afterok. Bank assembled + schema-checked.
- 2026-07-15: CV pilot 55933918 PASS -- bank CV reproduces central: reported mask
  IDENTICAL (4830), total 3.0679e-38 vs central 3.0664e-38 (rel 4.8e-4), per-bin
  median 0.65% (max 17% one tail bin). 4D throw bank VALIDATED for the unified throw.
- 2026-07-15: P7 dry-run proj54dC 55934370 queued (5D->4D marginal on committed adopted 5D).
- gpu_shared heavily fairshare-throttled (Agents B/PET + C/FPS + A/active-universe interactive
  competing). Sequencing: replicas->budget->combined FIRST (guaranteed core), then throws.
- 2026-07-15: P7 dry-run proj54dC PASS (validation, candidate, NOT quoted): 5D adopted
  (10694) -> 4D marginal (4830), 0 src cells leaked, PSD OK, sqrt-tr 2.41e-38, rank 263.
  Edge case flagged: 5/4830 4D-reported bins have no reported 5D source (all-W-slice
  unreported) -> zero marginal variance there (the sole cause of max|rel|=1.0; median
  marginal-vs-central 4.4%, consistent with known ~3% 5D<->4D central agreement). Final
  numbers await Agent A's committed final adopted 5D. project_cov_nd.py validated e2e.
- 2026-07-15 ~14:07: gpu_shared starved replicas (15/100, ~16/hr) -> escalated to a
  dedicated GPU interactive alloc 55936291 (nid001192, 128c, 4h) running
  run_4d_replicas_packed.sh (CONC=5, ~35/hr, resumable skip-if-exists). Cancelled the
  redundant gpu_shared boot4dC/ssp4dC/budget-dep (frees shared for Agents B/C). Trap
  hit+fixed: salloc has no --export (set HOME in the loop); no OUTER srun wrapper
  (nested-srun rc=192) -> salloc ... bash loop dispatches srun --overlap steps.
- 2026-07-15 ~19:00 (node PDT): interactive-GPU packing abandoned. Alloc 55938858
  (CONC=16) TIMED OUT at 4h wall producing only 12 ssp (memory-bandwidth/IO thrash with
  16-18 concurrent 32.8M-event unfolds; boot phase failed rc=1). Two prior interactive
  allocs also died. LESSON: this unfold saturates ~5 cores but packing many concurrent
  on one node thrashes on memory bandwidth; single-unfold-per-generous-cpuset (the
  gpu_shared 8.5-min config) is the only reliable footing.
- 2026-07-15 ~19:47 USER: normal CPU hours are BACK -> PIVOT to CPU sbatch (robust,
  resumable, fire-and-forget, no GPU contention with A/B/C). Full DAG submitted:
  boot4dCc 55961795 + ssp4dCc 55961803 -> budget4dCc 55961846(afterok) ; uthr4dCc 55961848
  + blk4dCc 55961849 -> comb4dCc 55961851(afterok). OMP pinned to the 16-core cpuset.
  Preserved: 15 boot + 12 ssp already produced (skip-if-exists).
- 2026-07-15 ~20:00: FULL non-lateral CPU DAG queued (unattended, afterok, resumable):
  * boot4dCc 55961795 (100) + ssp4dCc 55961803 (24) -> budget4dCc 55961846 -> combined
  * uthr4dCc 55961848 (160) + blk4dCc 55961849 (124) -> comb4dCc 55961851 -> unified_throw_cov_4d.root
  * adopt4dCc 55962692 (afterok budget+combine) -> candidate adopted mean + cv-centered
  CPU starting to cycle (boot task 4 ran). All queues (gpu_shared/interactive/CPU) are
  fairshare+Resources throttled today -> throughput is slow but the DAG drains on its own.
  COMMIT PLAN: RUN_LOG + VALIDATION_LEDGER are CLEAN (safe to append at gate); STATUS +
  OPEN_ITEMS are DIRTY with other-agent edits (leave; note STATUS line in handoff).

## COMMIT-READY BUNDLE (transcribe when products land; do NOT git add -A)
Throughput note: this unfold is MEMORY-BANDWIDTH-bound (~4-6 useful/node). Fix = MORE
NODES. 4-node interactive multinode (55963800, run_4d_replicas_multinode.sh, CONC=5/node,
20 concurrent) + CPU batch DAG both drive replicas; cooperate via skip-if-exists; budget
cascades (afterok) once the dir is full.

### git add paths (my P6-4D files only; leave other agents' dirty files):
  nd-unfolding/assemble_bank_4d_from5d.py nd-unfolding/project_cov_nd.py
  nd-unfolding/pilot_cv_check_4d.py nd-unfolding/adopt_unified_4d.py
  nd-unfolding/run_4d_replicas_multinode.sh nd-unfolding/run_4d_replicas_packed.sh
  nd-unfolding/run_4d_throws_packed.sh
  nd-unfolding/sbatch_bootstrap_4d_corrected_{gpu,cpu}.sh
  nd-unfolding/sbatch_seedscan_split_4d_corrected_{gpu,cpu}.sh
  nd-unfolding/sbatch_combine_4d_corrected_{gpu,cpu}.sh
  nd-unfolding/sbatch_uthrow_{cov,block,combine}_4d_corrected_{gpu,cpu}.sh
  nd-unfolding/sbatch_adopt_4d_corrected_cpu.sh
  nd-unfolding/sbatch_pilot_cv_check_4d_gpu.sh nd-unfolding/sbatch_project_5d_to_4d_candidate_gpu.sh
  nd-unfolding/uq_4d/corrected/*.summary.json  (compact summaries at commit time)
  + append to CLEAN docs only: nd-unfolding/ND_OMNIFOLD_RUN_LOG.md, VALIDATION_LEDGER.md
  (STATUS.md + docs/OPEN_ITEMS.md are DIRTY w/ other-agent edits -> DO NOT touch;
   flag the STATUS one-liner in handoff for the doc-owner.)

### RUN_LOG entry (draft): "P6-4D corrected UQ: reconstructed bank_uthrow_4d from the
  surviving 5D bank (no event loop; CV reproduces central to 4.8e-4, mask identical);
  regenerated corrected C_stat(100)/C_ML(24) [fixed est seed 42, coherent Poisson];
  built combined = sweep block-sum + norm + stat + ML (support-limited lateral labeled);
  unified-throw 160 joint throws + 124 blocks -> C_unified/C_blocksum; candidate adopt
  mean + cv-centered. project_cov_nd.py validated (5D->4D marginal dry-run). FINAL lateral
  swap + adoption GATED on Agent A standard lateral block."

### VALIDATION_LEDGER lines (fill sqrt-traces from budget/combine/adopt logs):
  - 4D CV reproduce (bank): reported bins 4830, total 3.0679e-38 vs central 3.0664e-38 (4.8e-4). PASS
  - 4D combined corrected: sqrt-tr <FILL> med rel <FILL>%  (uq_4d/corrected/universe_stage2_4d/...combined.root)
  - 4D unified-throw: sqrt_tr_unified <FILL> vs block <FILL>, joint_mean_shift_norm <FILL>, null <FILL>
  - 4D adopted mean/cv: sqrt-tr <FILL>/<FILL>, PSD OK  (candidate; support-limited lateral)
  - P7 5D->4D marginal (dry-run candidate): 4830 bins, PSD, sqrt-tr 2.41e-38 (NOT quoted; final gated)
- 2026-07-15 ~21:48: multinode CONFIRMED (+19 replicas/20min ~57/hr). C_ML DONE (24/24).
  Decoupled fragile afterok: cancelled redundant batch replica arrays + budget-dep +
  adopt-dep (multinode does replicas); batch now focused on throws/blocks -> comb4dCc
  (55961851, afterok uthr4dCc 55961848 + blk4dCc 55961849). Budget + adopt to be submitted
  MANUALLY at milestones (no-dep): budget when boot=100; adopt when combined + unified-throw
  both land. Throws/blocks on batch are SLOW (~40min/task, ~3 concurrent) -> may not finish
  in window; core (combined) is the guaranteed deliverable, unified-throw+adopt is enhancement.

## CORE LANDED + COMMITTED (2026-07-16 01:xx)
Combined 4D corrected covariance VALIDATED (ALL_OK): sqrt-tr 2.0992e-38, median 13.47%/bin,
PSD (min-eig/max -2.8e-16), rank 264/4830. Committed 1913122 -> github/main (code +
RUN_LOG + VALIDATION_LEDGER + summaries; heavy ROOTs gitignored). C_stat sqrt-tr 1.2117e-39,
C_ML 1.0499e-39, C_syst 2.0931e-38.
REMAINING: (a) unified-throw (uthr/blk multinode 55969168) -> comb -> candidate adopt
(mean+cv) = ENHANCEMENT; (b) FINAL adopted 4D = swap Agent A's selection-complete standard
lateral block (GATED). P7 5D->4D marginal code ready (dry-run only; final gated).

## ENHANCEMENT autonomous chain (2026-07-16, hands-off)
Unified-throw is 284 memory-bandwidth-bound unfolds -> won't finish in one alloc window.
Autonomous completion wired: batch uthr4dCc=55971614 + blk4dCc=55971615 (resumable, skip-if-exists)
-> comb4dCc=55971617 (afterok) -> adopt4dCc=55971619 (afterok; combined already present). Multinode
55969168 accelerates by filling slabs (batch tasks then skip-fast -> arrays complete).
When adopt lands: validate PSD + append ledger/RUN_LOG + commit (follow-up). FINAL 4D
adoption still needs Agent A's lateral swap (separate, gated).

## FINAL STATE (2026-07-16 ~01:40 PDT) — handoff
CORE COMMITTED (1913122): corrected combined 4D covariance (sqrt-tr 2.099e-38, med
13.47%/bin, PSD, 4830 bins) + C_stat/C_ML/C_syst + bank reconstruction + project_cov_nd
+ launchers + RUN_LOG + LEDGER. Heavy ROOTs gitignored (fingerprinted by summaries).
ENHANCEMENT (unified-throw + candidate adopt) = AUTONOMOUS via batch chain:
  uthr4dCc 55971614 (0-39) + blk4dCc 55971615 (0-25) -> comb4dCc 55971617 (afterok) ->
  adopt4dCc 55971619 (afterok; combined already present). Resumable, skip-if-exists,
  clean complete slabs (3h wall >> task time). Multinode killed (freed nodes; partial
  slabs from its wall CLEANED: throws=3/40 blocks=20/26 clean remain). Slow on CPU
  Resources-throttle -> completes overnight/next-session. WHEN adopt lands: validate PSD
  + append LEDGER/RUN_LOG + commit follow-up.
GATED (not crossed): FINAL 4D adoption = swap Agent A's committed selection-complete
standard lateral block into the combined (current lateral SUPPORT-LIMITED, labeled).
P7 final projected numbers gated on final adopted 5D (5D->4D marginal code ready; dry-run only).
TRAP LOGGED: kill-by-pattern self-matched the issuing shell (exit 144) -> always kill by
explicit PID, never pgrep-pattern the target string in the same command.

## 2026-07-16 ~07:45: ALL SLABS DONE — cascade pending
Throw slabs 40/40 + blocks 26/26 (multinode p6_4d_thr2 55977576 finished them at its 4h wall).
Remaining uthr4dCc/blk4dCc array tasks are pure skip-if-exists no-ops draining through the
Resources-throttled shared queue -> comb4dCc 55971617 -> adopt4dCc 55971619 (afterok, wired).
Pre-staged validate_adopted_4d.py (unified-throw + both adopted covs: PSD/symm/manifest +
JSON summary with all VALIDATION_LEDGER numbers). Session watcher wakes on adopt landing;
then: validate -> append LEDGER/RUN_LOG -> commit follow-up. Do NOT submit duplicate comb
(concurrent-write race on unified_throw_cov_4d.root).
