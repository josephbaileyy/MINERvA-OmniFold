# `build_q_products.py`: Stage F rebuild, step A and §3

The script implements [`../SPEC.md`](../SPEC.md) §2 (the Q products) and §3 (`budget_Q.json` and its controls). Every
check is a STOP. A STOP raises, prints one `[STOP] …` line to stderr, exits with code 2, and, once the output
directory exists, writes `STOPPED.txt` there. A passing run ends with
`build_q_products: ALL <n> STOPS AND CONTROLS PASSED`.

## Invocation

Run it on a login node in root_6_28 (never under `set -u`), with `<A>` the deployed `git archive` (SPEC §1):

```sh
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate $HOME/.conda/envs/root_6_28
A=<archive>                      # e.g. /pscratch/sd/j/josephrb/tmp-2d-rebuild-20261018/<archive-1-dir>
OUT=<new directory>              # must not exist; its parent must
C=/global/cfs/cdirs/m3246/josephrb
R=/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding
V=/pscratch/sd/j/josephrb/2d-closeout-c04repair-20261012/build
ST=$A/docs/orchestration/state/2d-closeout
python3 -I -c "import sys, runpy; A='$A'; sys.path[:0] = [A + '/2d-unfolding/uq', A + '/2d-unfolding', A]; sys.argv = ['build_q_products.py', '--repo', A,
 '--s5-npz', '$C/2d-closeout-stageC-production-20261015/results/s5/production_cov.npz',
 '--s5-root', '$C/2d-closeout-stageC-production-20261015/results/s5/uq_production_covariance.root',
 '--s5-json', '$ST/stageC/production/evidence/production/results/s5.json',
 '--playlist-npz', '$C/2d-closeout-playlist-term-20261016/playlist_term.npz',
 '--q-npz', '$C/2d-closeout-playlist-combination-20261017/s5_plus_playlist.npz',
 '--combination-json', '$ST/playlist-term/outputs/combination/combination.json',
 '--eu', '$R/uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root',
 '--ec', '$R/2d_crossSection_omnifold_MEFHC_5iter.root',
 '--paper-anc', '$R/minerva_paper_anc/cov_ptpl_minerva_inclusive_6GeV.root',
 '--vl175-rollup', '$V/uq_universe_covariance_c04x01.root',
 '--vl175-boot', '$R/uq/bootstrap_MEFHC_300_vl170/uq_covariance_boot300.root',
 '--vl175-ml', '$R/uq/seedscan_lgbm_ml/uq_covariance_ml.root',
 '--vl175-blocks', '$ST/c04-repair/products/cov2d_blocks_205.npz',
 '--vl175-budget', '$ST/c04-repair/products/budget.json',
 '--vl175-group-medians', '$ST/stageB/diagnostics/c04-grouped/group_medians.json',
 '--outdir', '$OUT']; runpy.run_path(A + '/docs/orchestration/state/2d-closeout/stageF/rebuild/scripts/build_q_products.py', run_name='__main__')"
echo "exit=$?"
```

Every input is checked against its full sha256 from SPEC §1 before anything is written. `--repo` must be the
archive: the script refuses unless `reported_cells`, `plot_uncertainty_fig6_7_style`, `analyze_universes` and
`rederive_flux_muonE_cross` all import from under it. Importing the fig6/7 module also imports matplotlib.
`MPLCONFIGDIR` and `XDG_CACHE_HOME` are pointed at `<OUT>/_mplcache`, which is deleted before `SHA256SUMS` is
written. Set `TMPDIR` inside the run directory as well. The step-D inputs `fig_arrays.npz`, `remote_reduce.json` and
`make_figs.py` are not read here, so they are not pinned here.

Run time is about 10 s.

## Outputs

`uq_adopted_covariance.root`, `block_stat.root`, `block_c08.root`, `block_playlist.root`, `cov2d_Q_205.npz` and
`.json`, `budget_Q.json` and `SHA256SUMS`, as SPEC §2 lists them. `budget_Q.json` also records every check and
control, `sys.path`, argv, and the digests of the script, the imported modules and the inputs.

The receipt field names follow `build_repair.py`, so the SPEC §3a names map to them like this:

| SPEC §3a name | `budget_Q.json` field |
|---|---|
| `budget_Q.Q.median` | `Q.median_pct` |
| `budget_Q.Q.integral` | `Q.integral_sigma_pct` |
| projections | `pt_sigma_pct`, `pz_sigma_pct` (full precision) |
| `budget_Q.*_vs_EC` | `Q_vs_EC`, `S5_total_vs_EC`, `universe_plus_stat_vs_EC` |
| `budget_Q.bands.Flux.*` | `bands.Flux.*` and `flux.*` |

The same pattern holds for `groups`, `block_shares`, `ranks`, `paper_ratios` and `s5_copied`.

The condition number at threshold t is λmax divided by the smallest retained eigenvalue, where "retained" means
λ > t·λmax. Eigenvalues come from (C + Cᵀ)/2.

## Deviations from the spec and items not implemented

1. **combination.json projections are compared at 4 decimals.** The file stores `pt_rel_sigma_pct` and
   `pz_rel_sigma_pct` rounded to 4 decimals. They are compared after rounding this script's values to 4 decimals and
   must be equal. This follows the director's clarification of 2026-10-18. Every other combination.json value (cell
   median, p84 and max, the integral, `median_cell_sigma_ratio_to_VL175`, and the two C_PL shares) is held to 1e-12
   relative.
2. **The flux leading-mode variance share is not computed.** No committed producer of the note's "99.6 %" was found.
   - It entered in `b635f032` (2026-06-03) as a RUN_LOG statement ("computed") with no script.
   - `stageB/evidence/local-verify-c04/paper_flux.py` computes λmax/Tr, but on the *paper's* flux covariance, which
     is a different object.

   `budget_Q.flux.leading_mode_variance_share` is therefore `null`, with the reason recorded.
3. **`\rhoFluxMuon` does not depend on Q.** Its producer is `2d-unfolding/uq/rederive_flux_muonE_cross.py`, route A:
   ρ = min(ρ_cs, 1), with ρ_cs = (f̂ᵀ T ê)/√((f̂ᵀ T f̂)(êᵀ T ê)), computed from the paper ancillary's Total, Flux and
   MuonEnergyScale covariances only. It is reproduced as 0.900424, against the VL175 value 0.900 at printed
   precision. No matrix of ours enters, so the Q value is the VL175 value by construction. Route B's
   `corr(flux-mode, muon-E-mode)` inside our own matrix is a different statistic and is not computed.
4. **group_medians.json is reproduced only in part.** Its `repaired` section is reproduced: `grouped_current`, the
   statistical medians, `bands`, `universe_total`, `combined`, and the two max-abs-rel diagnostics. Two parts are
   not:
   - `grouped_legacy` uses `group_medians.py`'s own legacy map, not the fig6/7 map that SPEC names.
   - The `adopted` (VL172) section's input is not pinned in SPEC §1.
5. **The s5.json ensemble counts are not all fields.** s5.json has no explicit replica-count or triplet-count field.
   The fields that are copied verbatim, with their paths, are `checks.universe_bands_43_plus_norm`,
   `checks.july_44_bands_187_universes`, `numbers.c08.{dof,rank}`, `numbers.stat.ensemble_rel_se_of_sigma` and
   `numbers.x02.dof`. The counts 300 replicas and 5 triplets are counted from `inputs.production_outputs` keys and
   are labelled `derived_counts_not_copied`.
6. **Extra consistency controls (STOP), beyond the spec:**
   - s5.json's `{universe,stat,c08,total}_summary` to 1e-12, and its ranks at 1e-10;
   - combination.json `ranks_rcond_1e-10`;
   - the VL175 row of combination.json;
   - `cov2d_blocks_205.npz` equal to the c04x01 `hCov_combined` and to the ml block.
7. **Step-D hazard resolved:** the universe + stat sum is named `hCov_sum_universe_stat`, which the fig. 6/7 script
   does not read as a band; the review measured the step-D Total = `Q` to 4e-16.
