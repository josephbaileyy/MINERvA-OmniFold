#!/usr/bin/env bash
# ============================================================================
# make_figures.sh -- regenerate every figure used by the analysis note.
#
# All plotting scripts import ../technote_style.py, which (1) strips plot
# titles (information lives in the LaTeX caption) and (2) pins one sequential
# colormap (viridis), one diverging colormap (RdBu_r) and a fixed per-generator
# palette.  This manifest records the exact invocation for each figure so the
# set can be rebuilt reproducibly; run it from anywhere after sourcing the
# project environment.
#
#   source setup_salloc_env.sh   # root_6_28 conda env + MINERVA_PREFIX
#   bash docs/technote/make_figures.sh
# ============================================================================
set -u
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
PASS=(); FAIL=()

run () {  # run "<png>" <workdir> <command...>
  local png="$1"; local dir="$2"; shift 2
  ( cd "$REPO/$dir" && "$@" ) >/tmp/fig_$$.log 2>&1
  if [ $? -eq 0 ] && [ -e "$REPO/$dir/$png" ]; then
    PASS+=("$png"); printf '  OK    %s\n' "$png"
  else
    FAIL+=("$png"); printf '  FAIL  %s  (see log below)\n' "$png"; tail -4 /tmp/fig_$$.log | sed 's/^/        /'
  fi
}

echo "== 2D reproduction =="
run MEFHC_5iter_fig13.png            2d-unfolding  python plot_2d_threeway_fig13.py
run MEFHC_5iter_eff_fig5.png         2d-unfolding  python plot_efficiency_fig5_style.py
run MEFHC_5iter_xsec_paper_pt_slices.png 2d-unfolding python plot_2d_paper_comparison.py
run MEFHC_5iter_xsec_proj_pt.png     2d-unfolding  python plot_2d_cross_section.py --infile 2d_crossSection_omnifold_MEFHC_5iter.root --prefix MEFHC_5iter_xsec
run MEFHC_5iter_pull_full.png        2d-unfolding  python compare_to_paper_fullcov.py
run model_comp_projections.png       2d-unfolding  python compare_to_models.py
run tension_spectrum.png             2d-unfolding  python diagnose_tension.py

echo "== 2D uncertainty =="
UFLX="$REPO/2d-unfolding/uq/universe_stage2_MEFHC_full_matcorr_fluxfix"
run universe_stage2_MEFHC_full_matcorr_fluxfix/MEFHC_fig6_7_uncertainty_pt.png  2d-unfolding/uq  python plot_uncertainty_fig6_7_style.py --universe-root "$UFLX/uq_universe_covariance_full_matcorr_fluxfix.root" --bootstrap-root "$REPO/2d-unfolding/uq/bootstrap_MEFHC_300/uq_covariance_boot300.root" --out-prefix "$UFLX/MEFHC_fig6_7_uncertainty"
run 2d-unfolding/uq/classifier_calibration.png  .  python 2d-unfolding/uq/classifier_calibration.py --omni 2d-unfolding/runEventLoopOmniFold_MEFHC.root --out 2d-unfolding/uq/classifier_calibration.png
# bootstrap corr/spread: per-replica files were cleaned up; plot from the saved 300-replica product
run bootstrap_MEFHC_300/uq_corr_2d.png  2d-unfolding/uq  python plot_bootstrap_figs.py --cov bootstrap_MEFHC_300/uq_covariance_boot300.root --outdir bootstrap_MEFHC_300
run seedscan_lgbm/seedscan_spread_2d.png  2d-unfolding  python seedscan/analyze_seedscan.py --glob "$REPO/2d-unfolding/seedscan_lgbm/2d_xsec_MEFHC_5iter_lgbm_seed*.root" --outdir "$REPO/2d-unfolding/seedscan_lgbm"

echo "== 3D generators =="
run generators_vs_unfolded_band.png  3d-unfolding/genie  python overlay_generators_band.py --unfolded ../xsec_3d_MEFHC_5iter_lgbm.root --cov uq_3d/universe_stage2_3d/uq_universe_3d_covariance.root:hCov_combined3d_total --syst-cov uq_3d/universe_stage2_3d/uq_universe_3d_covariance.root:hCov_universe3d_total --band uq_3d/stat_band_3d.root --generator GENIE-CV:genie_cv_xsec3d.root --generator Tune-v1:model_tunev1_xsec3d.root --generator NuWro:nuwro_cv_xsec3d.root --generator GiBUU:gibuu_cv_xsec3d.root --out generators_vs_unfolded_band
run compare_3d_fullcov.png           3d-unfolding/genie  python compare_3d_fullcov.py --data ../xsec_3d_MEFHC_5iter_lgbm.root --cov uq_3d/universe_stage2_3d/uq_universe_3d_covariance.root:hCov_combined3d_total --generator GENIE-CV:genie_cv_xsec3d.root --generator Tune-v1:model_tunev1_xsec3d.root --generator NuWro:nuwro_cv_xsec3d.root --generator GiBUU:gibuu_cv_xsec3d.root --out compare_3d_fullcov
run compare_mec_eavail.png           3d-unfolding/genie  python compare_mec_eavail.py --plot compare_mec_eavail.png
run mode_decomp_eavail.png           3d-unfolding/genie  python mode_decomp_eavail.py --gst genie_mefhc_cv_ALL.gst.root --plot mode_decomp_eavail.png

echo "== (Eavail,W) + q3 =="
run products/5d/excess_eavail_W.png  nd-unfolding  python excess_eavail_W.py
run eavailW_band.png                 3d-unfolding/genie  python overlay_eavailW_band.py --data ../../nd-unfolding/products/5d/excess_eavail_W.root --gen GENIE-CV:genie_cv_xsec_eavailW.root --gen GENIE+MEC:genie_mec_xsec_eavailW.root --gen NuWro:nuwro_cv_xsec_eavailW.root --gen GiBUU:gibuu_cv_xsec_eavailW.root --png eavailW_band.png --out eavailW_band.root
run q3_excess_projection.png         nd-unfolding  python q3_excess_projection.py

echo "== PET =="
run products/pet/pet_vs_gbdt.png          nd-unfolding  python pet/pet_vs_gbdt.py --pet products/pet/pet_weights.npz --pc of_inputs_pc.npz --gbdt products/4d/xsec_4d_MEFHC_5iter_lgbm.root --out products/pet/pet_vs_gbdt.png
run products/pet/pet_vs_gbdt_absolute.png nd-unfolding  python pet/pet_vs_gbdt.py --absolute --pet products/pet/pet_weights.npz --pc of_inputs_pc.npz --gbdt products/4d/xsec_4d_MEFHC_5iter_lgbm.root --out products/pet/pet_vs_gbdt_absolute.png

echo "== full phase space =="
run products/5d/fps_pilot_compare_MEFHC.png  nd-unfolding  python fps_pilot_compare.py --fps-tune products/5d/xsec_2d_FPS_MEFHC_tune.root --fps-genie products/5d/xsec_2d_FPS_MEFHC_genie.root --ctrl products/5d/xsec_2d_CTRL_MEFHC.root --omnifile runEventLoopOmniFold_5D_FPS_MEFHC.root --out-png products/5d/fps_pilot_compare_MEFHC.png
run products/5d/fps_acceptance_MEFHC.png     nd-unfolding  python fps_acceptance.py --omnifile runEventLoopOmniFold_5D_FPS_MEFHC.root --out-png products/5d/fps_acceptance_MEFHC.png
run products/5d/fps_prior_envelope_MEFHC.png nd-unfolding  python fps_prior_envelope.py

echo "== 3D sec figures (from saved products; raw banks were cleaned up) =="
run eavail_spectrum.png  3d-unfolding  python plot_eavail_spectrum.py --infile xsec_3d_MEFHC_5iter_lgbm.root --out eavail_spectrum.png
run eavail_marginal_vs_paper_pull_full.png  2d-unfolding  python compare_to_paper_fullcov.py --ours ../3d-unfolding/xsec_3d_MEFHC_5iter_lgbm.root --out-prefix "$REPO/3d-unfolding/eavail_marginal_vs_paper"
run universe_stage2_3d/uq_universe_3d_band_eavail.png  3d-unfolding/uq_3d  python plot_universe_3d_bands.py --cv ../xsec_3d_MEFHC_5iter_lgbm.root --cov universe_stage2_3d/uq_universe_3d_covariance.root --outdir universe_stage2_3d

echo "== control / migration / ascencio / landscape =="
run products/5d/control_plots.png        nd-unfolding  python make_control_plots.py
run products/4d/ascencio_fullcov_compare.png nd-unfolding  python compare_ascencio_fullcov.py
run minerva_unfolding_landscape.png      3d-unfolding  python plot_minerva_landscape.py

echo
echo "==================== SUMMARY ===================="
echo "PASS: ${#PASS[@]}    FAIL: ${#FAIL[@]}"
[ ${#FAIL[@]} -gt 0 ] && printf 'FAILED: %s\n' "${FAIL[@]}"
rm -f /tmp/fig_$$.log
