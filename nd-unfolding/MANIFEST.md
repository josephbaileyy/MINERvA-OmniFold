# `nd-unfolding/` evidence-derived routing manifest

This is a **ROUTER derived from citation evidence**, not a declaration that similarly named files are disposable. It does not authorize deleting, moving, or renaming anything. Filenames are load-bearing provenance. When evidence is absent, stale, or tied, this file says so; when in doubt, read `ND_OMNIFOLD_RUN_LOG.md` before launching.

Scope: all 185 shell files directly in `nd-unfolding/` at `34b32b6` (2026-08-12). Evidence order is: recorded-result citation; current-campaign git history (2026-08-01 onward); shell/Python reference. A current-window touch in `069c3b8` was a repo-wide resume-guard repair, so it is `RECENT-GUARD`, not proof that the launcher produced a current result.

Evidence abbreviations: `RUN` = `ND_OMNIFOLD_RUN_LOG.md`; `STATUS` = `ND_OMNIFOLD_STATUS.md`; `CORR` = `CORRECTED_UQ_PRODUCTION_STATUS.md`; `PET` = `PET_UQ_PRODUCTION_STATUS.md`; `P6` = `uq_4d/corrected/P6_4D_CORRECTED_STATUS.md`; `LEDGER` = `../VALIDATION_LEDGER.md`; `STATE:name` = `../docs/orchestration/state/name`. Dates identify the most recent citation found. `RECENT:<commit>` means no admissible result citation was found. `CODE:<file>` is weaker still. `UNREFERENCED` means no result citation, current-window touch, or shell/Python caller was found.

`CLEAR` means the cited evidence itself selects an entry point or positively supersedes its competitors. `AMBIGUOUS` means at least two candidates have live citations, or no candidate in a multi-file family has a result citation. `UNREFERENCED` is the route verdict for a singleton with no recorded launcher result (even if it has a weak recent/code signal). Resource variants are not treated as interchangeable unless the evidence says they are.

## Current controlled routes

### Intent — run the standard selection-complete 5D endpoint pipeline

Candidates/evidence: `run_p4_standard.sh` — **CITED-STATUS** (2026-08-11, `active_universe_5d/standard/P4_STANDARD_STATUS.md`, which calls it the canonical driver); its stages `run_p4_merge_audit_std.sh` — **RECENT** (`d5bd5da`, also called by the driver), `run_p4_unfold_std.sh` — **CITED-STATE** (2026-08-11, `p4-packetb-sweep-extractor-fix-20260811.json`), `merge_active_endpoints.sh` — **CITED-RUN** (2026-07-18), and `sbatch_merge_active_array.sh` — **RECENT-GUARD** (`069c3b8`, called by the merge stage). Historical alternatives `run_active_laterals_interactive.sh`, `run_active_lateral_unfolds_interactive.sh` — both **CITED-RUN** (2026-07-18) — are explicitly called an unsafe superseded route in that same RUN entry. Recommendation: **CLEAR — enter through `run_p4_standard.sh`; obey its stop/evidence gates.** The stage scripts remain provenance-bearing.

### Intent — produce, merge, unfold, or adopt active-lateral FPS endpoints

Candidates/evidence: producers `sbatch_evloop_array_5d_active_laterals_fps.sh`, `sbatch_evloop_array_5d_active_laterals_fps_cpu.sh` — **RECENT-GUARD** (`069c3b8`), the first also code-referenced by both hadd scripts; mergers `sbatch_hadd_active_fps.sh`, `sbatch_hadd_active_fps_cpu.sh` — **RECENT-GUARD** (`069c3b8`); unfolds `run_active_fps_unfolds_interactive.sh` — **CODE** (`fps_build_{control,publication}_manifest.py`), `sbatch_unfold_active_fps.sh` — **CITED-RUN** (2026-08-07); adoption chain `sbatch_fps_active_lateral_chain.sh` — **CITED-RUN** (2026-08-07). Recommendation: **AMBIGUOUS.** The two cited scripts cover different downstream scopes, while CPU/GPU producer and merger variants have no result citation. A human must choose control vs publication manifest and the already-owned output namespace before selecting a resource route.

### Intent — run the standard active-lateral event loop only

Candidates/evidence: `sbatch_evloop_array_5d_active_laterals.sh` — **CITED-RUN** (2026-07-15); `run_active_laterals_interactive.sh` — **CITED-RUN** (2026-07-18, later explicitly superseded as a standalone standard route). Recommendation: **CLEAR — the batch array is the result-backed producer; for the full standard chain use `run_p4_standard.sh`.**

### Intent — reproduce or inspect the J28/footing/stamp adoption chain

Candidates/evidence: `sbatch_j28_adopt_5d.sh` — **CITED-CORR** (2026-08-11); `sbatch_readopt_5d_bkgaware_footing.sh` — **CITED-RUN** (2026-08-11); `sbatch_stamp_verify.sh` — **CITED-STATE** (2026-08-11, `ben106-stamp-verify-complete-56695424.json`). Recommendation: **CLEAR SEQUENCE, not substitutes:** J28 construction -> footing re-adoption -> stamp verification. The live state says the stamped candidate is not adopted, so this sequence is evidence/audit routing, not publication authorization.

## Event-loop, merge, and central-unfold intents

### Intent — run the central 4D event loop

Candidates/evidence: `sbatch_evloop_array_4d.sh` — **UNREFERENCED**. Recommendation: **UNREFERENCED**; inspect RUN history and intended output before launch.

### Intent — build the 4D full-universe ROOT and unfold universes

Candidates/evidence: `sbatch_evloop_array_4d_universes_full.sh` — **CITED-RUN** (2026-06-06); `sbatch_hadd_4d_universes_full.sh` — **CODE** (called by that array); `sbatch_unfold_4d_universes_full.sh` — **RECENT-GUARD** (`069c3b8`, called by `sweep_bank.py`); `sbatch_unfold_4d_validate_universe.sh` — **UNREFERENCED**. Recommendation: **AMBIGUOUS overall.** The production/merge entry is result-backed, but no evidence selects the unfold/validation launcher for a new result.

### Intent — run or rerun the 4D central unfold

Candidates/evidence: `sbatch_hadd_unfold_4d.sh`, `sbatch_unfold_4d_rerun.sh` — **UNREFERENCED**; `sbatch_unfold_4d_lateral.sh` — **CITED-RUN** (2026-06-04), but it is a universe/lateral launcher, not evidence for the central pair. Recommendation: **AMBIGUOUS.** A human must decide whether the input needs merging, a central anchor rerun, or a lateral universe; no citation resolves the central pair.

### Intent — run the central 5D event loop and central unfold

Candidates/evidence: `sbatch_evloop_array_5d.sh` — **CODE** (`sbatch_evloop_1A_fps.sh`, `sbatch_evloop_array_5d_fps.sh`, `sbatch_hadd_unfold_5d.sh`); `sbatch_hadd_unfold_5d.sh` — **UNREFERENCED**. Recommendation: **AMBIGUOUS / no recorded result citation.** The call graph shows ordering, not canonicality.

### Intent — build the 5D full-universe ROOT

Candidates/evidence: `sbatch_evloop_array_5d_universes_full.sh` — **CITED-RUN** (2026-06-08); `sbatch_hadd_5d_universes_full.sh` — **UNREFERENCED**. Recommendation: **AMBIGUOUS overall.** The producer is result-backed, but the merge launcher has no live citation.

### Intent — build the background-aware 5D event-loop ROOT

Candidates/evidence: `sbatch_evloop_array_5d_bkgaware_gpu.sh` — **RECENT-GUARD** (`069c3b8`); `evloop_bkgaware_packed_loop.sh` — **CITED-CORR** (2026-07-12); `run_merge_bkgaware.sh` — **CITED-CORR** (2026-07-12); `run_task13_interactive.sh` — **UNREFERENCED**. Recommendation: **AMBIGUOUS producer.** The packed loop and merge produced a recorded result; the GPU array has only a guard touch, and the all-in-one task-13 script has no citation. A human must choose batch vs packed ownership and confirm the merge input set.

### Intent — run the background-aware vertical sweep and finalize corrected 5D

Candidates/evidence: `sbatch_sweep_bank_5d_dump_bkgaware_gpu.sh` — **CITED-CORR** (2026-07-14); `sbatch_sweep_bank_5d_run_bkgaware_gpu.sh` — **CITED-CORR** (2026-07-14); `sweep_run_bkgaware_packed_loop.sh` — **CITED-CORR** (2026-07-14); `sbatch_unfold_5d_detector_bkgaware_gpu.sh` — **CITED-CORR** (2026-07-14); `sbatch_finalize_5d_bkgaware_gpu.sh` — **CITED-LEDGER** (2026-08-11). Recommendation: **CLEAR SEQUENCE for the recorded corrected chain.** Dump -> run (GPU or cited packed executor) -> detector endpoints -> finalizer; GPU-vs-packed execution remains a resource choice, not two scientific contracts.

### Intent — run a non-background-aware 5D sweep/detector endpoint

Candidates/evidence: `sbatch_sweep_bank_5d_dump.sh`, `sbatch_sweep_bank_5d_run.sh` — **UNREFERENCED**; `sbatch_unfold_5d_detector.sh` — **CITED-RUN** (2026-06-10); `sbatch_eavailW_cov_wlat.sh` — **CITED-STATE** (2026-08-11, `p4-sweep-snapshots.json`) and calls the detector launcher. Recommendation: **AMBIGUOUS.** The detector and W-lateral wrapper both have result citations for different products; the sweep dump/run pair has none. Human decision: detector covariance vs `(E_avail,W)` projection, and corrected vs historical footing.

### Intent — run a baseline `sweep_bank.py` campaign (q3/4D-style)

Candidates/evidence: `run_q3_sweep_interactive.sh` — **CITED-RUN** (2026-06-04); `sbatch_sweep_bank_array.sh`, `sbatch_sweep_bank_dump.sh`, `sbatch_sweep_bank_run.sh` — **UNREFERENCED**. Recommendation: **AMBIGUOUS overall.** The q3 interactive campaign is result-backed, but no citation selects a generic dump/run/array route.

### Intent — build point-cloud event-loop inputs

Candidates/evidence: `run_pc_evloop_interactive.sh` — **CITED-RUN** (2026-06-04); `sbatch_evloop_array_pointcloud.sh` — **CODE** (`sbatch_evloop_array_pointcloud_fps.sh`, `pet/sbatch_refresh_pet_vs_gbdt.sh`); `sbatch_evloop_array_pointcloud_fps.sh` — **CITED-RUN** (2026-06-29); `sbatch_hadd_pc_fps.sh` — **CITED-RUN** (2026-06-30); `sbatch_hadd_pc_fullcloud.sh` — **UNREFERENCED**. Recommendation: **AMBIGUOUS.** Base, FPS, and full-cloud products are different schemas; a human must choose the target schema before selecting the cited chain.

### Intent — build FPS central or full-universe event-loop inputs

Candidates/evidence: `sbatch_evloop_1A_fps.sh` — **CODE** (`sbatch_fps_pilot.sh`); `sbatch_evloop_array_5d_fps.sh` — **CODE** (`sbatch_fps_mefhc.sh`, point-cloud FPS wrapper); `sbatch_evloop_array_5d_fps_universes_full.sh`, `sbatch_hadd_5d_fps_universes_full.sh` — **UNREFERENCED**; `sbatch_unfold_fps_universes_full.sh` — **RECENT-GUARD** (`069c3b8`). Recommendation: **AMBIGUOUS.** No candidate has a recorded-result citation; choose 1A vs MEFHC and central vs universe-full before launch.

### Intent — run the FPS pilot/MEFHC central/envelope chain

Candidates/evidence: `sbatch_fps_pilot.sh`, `sbatch_fps_mefhc.sh` — **CODE** (they call each other/stages); `sbatch_fps_envelope.sh` — **CITED-RUN** (2026-06-10); `sbatch_fps_genie_refix.sh` — **UNREFERENCED**. Recommendation: **AMBIGUOUS.** The envelope has a result citation, but the central entry points do not, and the refix has no live evidence. Human decision: reproduce the cited prior envelope or construct a central product.

### Intent — run FPS closure, mask, or acceptance/coverage controls

Candidates/evidence: `sbatch_fps_hidden_closure.sh` — **CITED-RUN** (2026-06-11); `sbatch_fps_mask.sh` — **CODE** (`fps_build_control_manifest.py`); `sbatch_coverage_fps.sh` — **RECENT-GUARD** (`069c3b8`); `sbatch_fps_coverage_analysis.sh` — **UNREFERENCED**. Recommendation: **AMBIGUOUS overall.** Only the historical hidden-closure subtask is result-backed; mask/coverage is unresolved.

### Intent — rerun FPS under 5D/xps/xps2 priors

Candidates/evidence: `sbatch_fps_reunfold_5d.sh`, `sbatch_fps_reunfold_5d_xps.sh`, `sbatch_fps_reunfold_5d_xps2.sh` — **UNREFERENCED**. Recommendation: **AMBIGUOUS**; the filename variants encode different inputs and no result citation selects one.

### Intent — run the Ascencio fine-bin unfold

Candidates/evidence: `sbatch_unfold_ascencio_fine.sh` — **RECENT-GUARD** (`069c3b8`). Recommendation: **UNREFERENCED** as a result-producing route; the singleton has only a guard touch.

## Bootstrap, split-seed, covariance, and adoption intents

### Intent — generate corrected 4D bootstrap and split-seed replicas

Candidates/evidence: GPU `sbatch_bootstrap_4d_corrected_gpu.sh`, `sbatch_seedscan_split_4d_corrected_gpu.sh` — **CITED-P6** (2026-07-15); CPU `sbatch_bootstrap_4d_corrected_cpu.sh`, `sbatch_seedscan_split_4d_corrected_cpu.sh` — **RECENT-GUARD** (`069c3b8`); packed/multinode `run_4d_replicas_packed.sh`, `run_4d_replicas_multinode.sh` — **CITED-P6** (2026-07-15); combined interactive helper `run_4dstatml_interactive.sh` — **RECENT-GUARD** (`069c3b8`). Historical `sbatch_bootstrap_4d.sh`, `sbatch_seedscan_split_4d.sh` — **CITED-RUN** (2026-06-04). Recommendation: **AMBIGUOUS.** P6 first names GPU, then records packed/multinode use and a CPU pivot without an exact CPU-basename result citation. A human must select the surviving output namespace and resource footing; the June pair is explicitly pre-remediation in P6.

### Intent — combine/analyze corrected 4D covariance

Candidates/evidence: `sbatch_combine_4d_corrected_gpu.sh` — **CITED-P6** (2026-07-15); `sbatch_combine_4d_corrected_cpu.sh` — **UNREFERENCED**; `sbatch_analyze_4d_cov.sh`, `sbatch_combine_4d_statml.sh`, `run_budget_4d.sh` — **UNREFERENCED**; `sbatch_combine_4d_budget.sh` — **CODE** (`sbatch_fps_budget.sh`). Recommendation: **AMBIGUOUS overall.** P6 backs the corrected GPU combine, but no evidence selects among generic/CPU budget routes.

### Intent — generate and combine corrected 4D unified throws

Candidates/evidence: GPU `sbatch_uthrow_cov_4d_corrected_gpu.sh`, `sbatch_uthrow_block_4d_corrected_gpu.sh`, `sbatch_uthrow_combine_4d_corrected_gpu.sh` — **CITED-P6** (2026-07-15); CPU `sbatch_uthrow_cov_4d_corrected_cpu.sh`, `sbatch_uthrow_block_4d_corrected_cpu.sh` — **RECENT-GUARD** (`069c3b8`), `sbatch_uthrow_combine_4d_corrected_cpu.sh` — **UNREFERENCED**; packed `run_4d_throws_packed.sh` — **CITED-P6** (2026-07-15); `run_4d_throws_multinode.sh`, `run_4d_throws_interactive.sh` — **UNREFERENCED**; older `sbatch_uthrow_cov_4d.sh`, `sbatch_uthrow_block_4d.sh`, `sbatch_uthrow_combine_4d.sh` — **CODE** (`sbatch_assemble_4d.sh`). Recommendation: **AMBIGUOUS.** Multiple live P6 citations and an uncited later CPU route exist. Human decision: resume the exact P6 inventory/namespace and choose its surviving executor.

### Intent — assemble/adopt/check/project a 4D covariance

Candidates/evidence: `sbatch_assemble_4d.sh` — **CITED-RUN** (2026-06-08); `sbatch_adopt_4d_corrected_cpu.sh` — **CITED-P6** (2026-07-15); `sbatch_pilot_cv_check_4d_gpu.sh`, `sbatch_project_5d_to_4d_candidate_gpu.sh` — **CITED-P6** (2026-07-15). Recommendation: **CLEAR by subtask, not interchangeable:** assemble historical bank; adopt corrected candidate; pilot-check; project candidate. P6 says final 4D adoption remains gated.

### Intent — generate 5D bootstrap replicas

Candidates/evidence: `sbatch_bootstrap_5d.sh` — **CITED-RUN** (2026-06-29); `sbatch_bootstrap_5d_gpu.sh`, `boot5d_packed_loop.sh` — **CITED-CORR** (2026-07-12); `sbatch_boot5d_gpu_interactive.sh` — **RECENT** (`62eab87`). Recommendation: **AMBIGUOUS executor.** CORR records both GPU batch and packed interactive work on the same inventory; confirm existing completeness and writer ownership before choosing.

### Intent — generate 5D split-seed replicas and combine the budget

Candidates/evidence: `sbatch_seedscan_split_5d.sh` — **CITED-RUN** (2026-06-29); `sbatch_combine_5d_budget.sh`, `run_budget_5d.sh` — **CITED-CORR** (2026-07-12). Recommendation: **CLEAR SEQUENCE:** split-seed production -> cited budget combiner (batch or its cited interactive wrapper according to resource ownership).

### Intent — run 5D unified throws

Candidates/evidence: `sbatch_uthrow_run_5d_fast.sh` — **CITED-RUN** (2026-08-07); `sbatch_uthrow_combine_5d_fast.sh` — **CITED-RUN** (2026-08-06); non-fast `sbatch_uthrow_run_5d.sh` — **CODE** (called by fast/4D wrappers), `sbatch_uthrow_block_5d.sh`, `sbatch_uthrow_combine_5d.sh` — **UNREFERENCED**. Recommendation: **CLEAR for the recorded regeneration: fast run -> fast combine.** No result citation supports the non-fast block/combine pair.

### Intent — adopt a corrected 5D covariance

Candidates/evidence: `run_adopt_5d.sh` — **CITED-CORR** (2026-07-12); `sbatch_adopt_5d.sh` — **UNREFERENCED**. Recommendation: **CLEAR — `run_adopt_5d.sh` is the only result-cited candidate.**

### Intent — generate the AI1 estimator-only scan and combine it

Candidates/evidence: `sbatch_ai1_estimator_scan.sh`, `ai1_packed_loop.sh`, `run_ai1_combine.sh` — **CITED-CORR** (2026-07-14). Recommendation: **CLEAR SEQUENCE:** scan (batch or cited packed executor) -> combine; STATUS says this auxiliary scan is not an independent covariance block.

### Intent — generate FPS bootstrap or split-seed replicas

Candidates/evidence: `sbatch_bootstrap_fps.sh`, `sbatch_bootstrap_fps_corrected_cpu.sh`, `sbatch_bootstrap_fps_corrected_gpu.sh`, `sbatch_seedscan_split_fps.sh`, `sbatch_seedscan_split_fps_corrected_cpu.sh`, `sbatch_seedscan_split_fps_corrected_gpu.sh` — all **RECENT-GUARD** (`069c3b8`) with no result citation. Recommendation: **AMBIGUOUS.** Human decision: historical vs corrected contract and CPU vs GPU; recency does not resolve scientific footing.

### Intent — combine FPS stat/ML or budget components

Candidates/evidence: `sbatch_combine_boot_fps.sh`, `sbatch_combine_boot_fps_corrected_cpu.sh`, `sbatch_combine_boot_fps_corrected_gpu.sh`, `sbatch_combine_split_fps.sh`, `sbatch_combine_split_fps_corrected_cpu.sh`, `sbatch_combine_split_fps_corrected_gpu.sh` — **UNREFERENCED**; `sbatch_fps_budget.sh`, `sbatch_fps_cov.sh` — **CITED-RUN** (2026-06-11); `sbatch_fps_budget_corrected_cpu.sh`, `sbatch_fps_budget_corrected_gpu.sh` — **UNREFERENCED**. Recommendation: **AMBIGUOUS.** Only historical FPS budget/cov launchers have result citations; corrected variants have none, and STATUS says no corrected FPS replacement is implied.

### Intent — run/adopt FPS unified throws

Candidates/evidence: `sbatch_uthrow_cov_fps.sh`, `sbatch_uthrow_cov_fps_corrected_cpu.sh`, `sbatch_uthrow_cov_fps_corrected_gpu.sh`, `sbatch_uthrow_block_fps.sh`, `sbatch_uthrow_block_fps_corrected_cpu.sh`, `sbatch_uthrow_block_fps_corrected_gpu.sh` — **RECENT-GUARD** (`069c3b8`); `sbatch_uthrow_combine_fps.sh`, `sbatch_uthrow_combine_fps_corrected_cpu.sh`, `sbatch_uthrow_combine_fps_corrected_gpu.sh` — **UNREFERENCED**; `sbatch_adopt_fps.sh` — **CITED-RUN** (2026-06-11); `sbatch_adopt_fps_corrected_cpu.sh`, `sbatch_adopt_fps_corrected_gpu.sh` — **UNREFERENCED**. Recommendation: **AMBIGUOUS.** The only cited adoption is historical; no corrected chain has a result citation, and STATUS says FPS has no implied replacement.

### Intent — use generic dimension-unspecified replica/throw helpers

Candidates/evidence: `sbatch_seedscan_split.sh`, `sbatch_bootstrap_4d.sh` (4D-specific, **CITED-RUN** 2026-06-04), `sbatch_unified_throw.sh`, `sbatch_uthrow_dump.sh`, `sbatch_uthrow_run.sh`, `sbatch_uthrow_cov.sh`, `sbatch_uthrow_block.sh`, `sbatch_uthrow_combine.sh` — all except the 4D bootstrap **UNREFERENCED**. Recommendation: **UNREFERENCED** for the generic helpers. Determine dimensionality and output contract first.

## PET, neural-network, and input-conversion intents

### Intent — dump scalar NN/FPS inputs or run the scalar NN

Candidates/evidence: `sbatch_nn_dump_5d.sh`, `sbatch_nn_dump_fps_5d.sh`, `sbatch_nn_dump_fps_5d_xps.sh`, `sbatch_nn_dump_fps_5d_xps2.sh` — **RECENT-GUARD** (`069c3b8`); `sbatch_dump_fps_inputs.sh` — **RECENT-GUARD** (`069c3b8`); `sbatch_nn_dump_lgbm.sh` — **UNREFERENCED** but calls `sbatch_nn_gpu.sh`; `sbatch_nn_gpu.sh` — **CODE** (called by dump-lgbm). Recommendation: **AMBIGUOUS.** Choose scalar schema and backend first; no result citation selects a dumper/runner.

### Intent — convert point-cloud ROOT/NPZ inputs for PET

Candidates/evidence: `sbatch_npz_pc_fps.sh` — **CITED-RUN** (2026-06-30); `sbatch_npz_pc_fps_xps.sh`, `sbatch_npz_pc_fps_xps2.sh` — **CODE** (called by their NN dump wrappers); `sbatch_npz_fullcloud.sh` — **UNREFERENCED**. Recommendation: **AMBIGUOUS.** FPS, xps, xps2, and fullcloud are distinct schemas; only the older FPS path has a result citation.

### Intent — train recoil-only PET FPS controls

Candidates/evidence: `sbatch_pet_train_fps_hvd.sh` — **CITED-RUN** (2026-06-30); `sbatch_pet_train_fps_delta.sh` — **UNREFERENCED** but calls the HVD launcher; `sbatch_pet_conv_fps_xps2.sh` — **RECENT-GUARD** (`069c3b8`, code-referenced by `pet_conv_check_5d.py`). Recommendation: **AMBIGUOUS overall.** Only the historical HVD control is result-backed; Delta/xps2 is unresolved. PET remediation status says recoil-only products cannot satisfy the publication full-event DAG.

### Intent — run PET lateral/detector corrections

Candidates/evidence: `sbatch_pet_lateral.sh` — **CITED-RUN** (2026-06-08); `sbatch_pet_lateral_5d.sh`, `sbatch_pet_lateral_band.sh` — **UNREFERENCED**. Recommendation: **AMBIGUOUS.** The cited launcher and the uncited 5D/band variants target different products; inspect the desired covariance dimensionality and corrected-target requirement.

### Intent — build/rebuild PET systematic banks or covariances

Candidates/evidence: `sbatch_pet_rebank.sh` — **CITED-RUN** (2026-06-11); `sbatch_uthrow_dump_rebank.sh` — **CITED-RUN** (2026-06-11); `run_rebank_bkgaware.sh` — **CITED-PET** (2026-07-14); `sbatch_uthrow_dump_5d.sh` — **CODE** (called by bkg-aware rebank); `sbatch_pet_systematics.sh`, `sbatch_pet_systematics_5d.sh`, `sbatch_pet_uthrow_5d.sh` — **UNREFERENCED**. Recommendation: **AMBIGUOUS overall.** The corrected bank rebuild is result-backed through `run_rebank_bkgaware.sh`, but no citation selects its PET covariance consumer. The two June scripts are recorded historical provenance.

### Intent — run PET/FPS unified-throw dumps not covered above

Candidates/evidence: `sbatch_uthrow_dump_fps.sh` — **UNREFERENCED**. Recommendation: **UNREFERENCED.**

### Intent — run the PET xps2 convergence check

Candidates/evidence: `sbatch_pet_conv_fps_xps2.sh` — **RECENT-GUARD** (`069c3b8`). Recommendation: **UNREFERENCED** as a result-producing route; the singleton has only a guard touch.

## Physics summaries and diagnostics

### Intent — build `(E_avail,W)` covariance

Candidates/evidence: `run_eavailW_5d.sh` — **CITED-CORR** (2026-07-12); `sbatch_eavailW_cov.sh` — **UNREFERENCED**; `sbatch_eavailW_cov_wlat.sh` — **CITED-STATE** (2026-08-11, `p4-sweep-snapshots.json`). Recommendation: **AMBIGUOUS.** Two candidates have live citations for different covariance footings; STATUS quarantines the historical `(E_avail,W)` covariance. Human must specify corrected projection vs lateral-inclusive historical reconstruction.

### Intent — calculate Eavail/W excess or generator significance

Candidates/evidence: `sbatch_eavail_sig.sh`, `sbatch_excess_eavail_W.sh` — **UNREFERENCED**. Recommendation: **AMBIGUOUS / no recorded route**; STATUS withholds dependent exact significance.

### Intent — dump transverse-dynamics q3 or smoke-test W

Candidates/evidence: `sbatch_td_q3.sh` — **CITED-RUN** (2026-06-08); `smoke_W.sh` — **CITED-RUN** (2026-06-06). Recommendation: **CLEAR by distinct diagnostic intent; they are not alternatives.**

### Intent — run unbinned GoF

Candidates/evidence: `sbatch_unbinned_gof.sh` — **UNREFERENCED** (the Python result is cited in STATUS, but the launcher basename is not). Recommendation: **UNREFERENCED** launcher route.

### Intent — run FPS budget-only coverage analysis

Candidates/evidence: `sbatch_fps_coverage_analysis.sh` — **UNREFERENCED**; `sbatch_coverage_fps.sh` — **RECENT-GUARD** (`069c3b8`). Recommendation: **AMBIGUOUS.**

### Intent — inspect environment setup on a batch node

Candidates/evidence: `rootenv_sbatch.sh` — **UNREFERENCED**. Recommendation: **UNREFERENCED**; `setup_salloc_env.sh` remains the documented environment entry point, but that does not prove this helper's canonicality.

## Explicitly unresolved families

These gaps are intentional: active-FPS CPU/GPU production/merge; background-aware event-loop batch vs packed; central 4D and 5D unfold wrappers; point-cloud schema choice; FPS central/full-universe chains; corrected 4D CPU/GPU/packed replica and throw executors; 5D batch vs packed bootstrap; every corrected FPS replica/throw/adoption family; generic unified-throw helpers; PET NPZ schema and Delta/HVD/xps2 routes; PET lateral/systematics consumers; and `(E_avail,W)` historical vs corrected footing. Each needs a human choice about output namespace, scientific contract, or resource ownership that the citation record does not supply.

## Near-duplicate clusters

- **`unified_throw_cov.py` wrappers (25 scripts):** 4D/FPS/generic `cov`, `block`, and `combine` stages plus interactive/packed executors. What varies is dimensional input/bank/output, expected IDs or block slice, corrected-contract paths, and CPU/GPU/Slurm directives; these are not filename-only aliases.
- **`unfold_nd_omnifold_unbinned.py` wrappers (19 scripts):** central, universe, detector, active-FPS, closure, Ascencio, and P4-standard unfolds. What varies is dimension/edges, omnifile, active universe, target/background footing, closure/prior flags, and output namespace.
- **`bootstrap_nd.py` wrappers (16 scripts):** 4D/5D/FPS/AI1 plus packed and interactive forms. What varies is dimension, replica range, estimator/split seed policy, output directory, concurrency, and resource directives.
- **`combine_cov_nd.py` wrappers (13 scripts):** stat, ML-split, budget, AI1, and FPS/4D/5D combines. What varies is component inventory, expected IDs, CV/mask, added systematic/norm blocks, and output.
- **`seedscan_split.py` wrappers (12 scripts):** generic/4D/5D/FPS and corrected CPU/GPU forms. What varies is dimension/input/output, split/estimator seed policy, task range, and Slurm resources.
- **`hadd_universes_full.py` wrappers (11 scripts):** standard, background-aware, FPS, active-lateral, and P4 audit merges. What varies is manifest/input completeness checks, output namespace, receipt/audit production, and CPU/GPU directives; not merely `#SBATCH` lines.
- **Purest resource near-duplicates:** corrected CPU/GPU 4D and FPS bootstrap/seedscan/throw wrappers share their Python driver and scientific-looking flags, but differ in partitions, CPU/GPU requests, concurrency and sometimes output/resume guards. Because exact result citations do not consistently follow the later CPU pivot, this cluster remains `AMBIGUOUS` rather than being resolved by suffix.

## Coverage summary

All **185/185** flat-root shell scripts are named above. Script evidence classes: **68 CITED**, **35 RECENT-only** (mostly the `069c3b8` guard sweep), **18 CODE-only**, and **64 UNREFERENCED**. Across **45 task-intent families**, the route verdicts are **10 CLEAR**, **28 AMBIGUOUS**, and **7 UNREFERENCED**. Evidence counts are not endorsements; the family verdicts deliberately preserve unresolved ties.
