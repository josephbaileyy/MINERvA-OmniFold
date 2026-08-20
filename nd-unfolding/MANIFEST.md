# N-D launcher router

This file routes current work; it is not deletion authority and does not make a result adoptable.
Read `ND_OMNIFOLD_STATUS.md` and the governing open item before running anything.

## Evidence boundary

The complete pre-compaction launcher survey and every retired launcher are recoverable at
`evidence/prepublication-2026-08-20-0b329e8a:nd-unfolding/MANIFEST.md` and their original paths.
The evidence tag is the authority for historical job reconstruction; current `main` is the supported
surface.

Family 6 retired 47 launchers that the survey classified as unreferenced and a fresh consumer audit
confirmed had no surviving caller, test, receipt, status, publication citation, hash pin, or runtime
reader. The exact inventory below has SHA-256
`5ec9f1184d4bd6cfdcc2ef33e3bfb854ccb4a8c928713e532b6ab023ae6bded8`. Recover any member with:

```bash
git show evidence/prepublication-2026-08-20-0b329e8a:<old-path>
```

<details><summary>Retired family-6 paths (47)</summary>

- `nd-unfolding/rootenv_sbatch.sh`
- `nd-unfolding/run_4d_throws_multinode.sh`
- `nd-unfolding/run_budget_4d.sh`
- `nd-unfolding/run_task13_interactive.sh`
- `nd-unfolding/sbatch_analyze_4d_cov.sh`
- `nd-unfolding/sbatch_combine_4d_corrected_cpu.sh`
- `nd-unfolding/sbatch_combine_4d_statml.sh`
- `nd-unfolding/sbatch_combine_boot_fps.sh`
- `nd-unfolding/sbatch_combine_boot_fps_corrected_cpu.sh`
- `nd-unfolding/sbatch_combine_split_fps.sh`
- `nd-unfolding/sbatch_combine_split_fps_corrected_cpu.sh`
- `nd-unfolding/sbatch_eavailW_cov.sh`
- `nd-unfolding/sbatch_eavail_sig.sh`
- `nd-unfolding/sbatch_evloop_array_4d.sh`
- `nd-unfolding/sbatch_evloop_array_5d_fps_universes_full.sh`
- `nd-unfolding/sbatch_excess_eavail_W.sh`
- `nd-unfolding/sbatch_fps_budget_corrected_cpu.sh`
- `nd-unfolding/sbatch_fps_coverage_analysis.sh`
- `nd-unfolding/sbatch_fps_genie_refix.sh`
- `nd-unfolding/sbatch_hadd_5d_fps_universes_full.sh`
- `nd-unfolding/sbatch_hadd_5d_universes_full.sh`
- `nd-unfolding/sbatch_hadd_pc_fullcloud.sh`
- `nd-unfolding/sbatch_hadd_unfold_4d.sh`
- `nd-unfolding/sbatch_hadd_unfold_5d.sh`
- `nd-unfolding/sbatch_nn_dump_lgbm.sh`
- `nd-unfolding/sbatch_npz_fullcloud.sh`
- `nd-unfolding/sbatch_pet_lateral_5d.sh`
- `nd-unfolding/sbatch_pet_lateral_band.sh`
- `nd-unfolding/sbatch_pet_systematics.sh`
- `nd-unfolding/sbatch_pet_systematics_5d.sh`
- `nd-unfolding/sbatch_pet_uthrow_5d.sh`
- `nd-unfolding/sbatch_seedscan_split.sh`
- `nd-unfolding/sbatch_sweep_bank_5d_dump.sh`
- `nd-unfolding/sbatch_sweep_bank_array.sh`
- `nd-unfolding/sbatch_sweep_bank_dump.sh`
- `nd-unfolding/sbatch_sweep_bank_run.sh`
- `nd-unfolding/sbatch_unbinned_gof.sh`
- `nd-unfolding/sbatch_unfold_4d_rerun.sh`
- `nd-unfolding/sbatch_unfold_4d_validate_universe.sh`
- `nd-unfolding/sbatch_unified_throw.sh`
- `nd-unfolding/sbatch_uthrow_block.sh`
- `nd-unfolding/sbatch_uthrow_combine.sh`
- `nd-unfolding/sbatch_uthrow_combine_4d_corrected_cpu.sh`
- `nd-unfolding/sbatch_uthrow_cov.sh`
- `nd-unfolding/sbatch_uthrow_dump.sh`
- `nd-unfolding/sbatch_uthrow_dump_fps.sh`
- `nd-unfolding/sbatch_uthrow_run.sh`

</details>

## Current controlled routes

| Intent | Entry route | Governing evidence |
|---|---|---|
| Standard selection-complete P4 | `run_p4_standard.sh` | `active_universe_5d/standard/P4_STANDARD_STATUS.md`; its stop/evidence gates |
| Corrected background-aware 5D construction | `CORRECTED_UQ_PRODUCTION_STATUS.md` | Exact cited dump/run/detector/finalizer sequence; candidate remains quarantined |
| Recorded 5D unified-throw regeneration | `sbatch_uthrow_run_5d_fast.sh` then `sbatch_uthrow_combine_5d_fast.sh` | N-D status and current receipts |
| Corrected FPS uncertainty work | `uq_fps/corrected/FPS_UQ_CORRECTED_STATE.md` | Follow the exact CPU/GPU/packed route named for the surviving output namespace |
| Active-lateral FPS endpoints | `sbatch_fps_active_lateral_chain.sh` or the exact control path named by FPS status | Control and publication manifests are distinct; do not substitute them |
| PET full-event work | `PET_UQ_REMEDIATION_STATUS.md` | Follow its ordered DAG and reuse/rerun matrix; recoil-only products cannot satisfy it |
| Scalar 4D/5D central reproduction | `ND_OMNIFOLD_STATUS.md` | Select the dimensional contract and current canonical source before choosing a launcher |

## Safety boundary

A filename, an old citation, or a recent guard-only edit is not proof that a launcher is supported.
Do not infer interchangeability from CPU/GPU, corrected, FPS, 4D, or 5D suffixes. Exact masks, inputs,
seed roles, output namespaces, resource directives, and receipt contracts differ. If the current
status does not select one route, stop and resolve the ambiguity instead of reviving a tagged script.
