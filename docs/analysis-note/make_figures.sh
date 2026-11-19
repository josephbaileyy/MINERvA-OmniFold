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
#   bash docs/analysis-note/make_figures.sh
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
# 2026-10-11 (docs/publication/DECISION-20261011-joseph-2d-central-lightgbm-seed42.md): the quoted 2D
# central value is the LightGBM seed-42 matched universe CV; the exact-split file is a cross-check. The
# figures below that show the central value read CV42 explicitly (the producers' defaults still name the
# exact-split file). The efficiency figure does not depend on the central value.
CV42=uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root
# RE-2 integration: CV42 is E_U, no longer the quoted central value. The installed figures of these lines are E_R's,
# from RE-2 part C ("2D figures from RE-2 part C", below); these lines would draw the purity versions.
run MEFHC_5iter_fig13.png            2d-unfolding  python plot_2d_threeway_fig13.py --infile "$CV42"
run MEFHC_5iter_eff_fig5.png         2d-unfolding  python plot_efficiency_fig5_style.py
run MEFHC_5iter_xsec_paper_pt_slices.png 2d-unfolding python plot_2d_paper_comparison.py --infile "$CV42"
run MEFHC_5iter_xsec_proj_pt.png     2d-unfolding  python plot_2d_cross_section.py --infile "$CV42" --prefix MEFHC_5iter_xsec
run MEFHC_5iter_pull_full.png        2d-unfolding  python compare_to_paper_fullcov.py --ours "$CV42"
run ../docs/analysis-note/figures/negweight_ratio_2d.pdf 2d-unfolding python plot_negweight_ratio.py
run model_comp_projections.png       2d-unfolding  python compare_to_models.py --ours "$CV42"
run tension_spectrum.png             2d-unfolding  python diagnose_tension.py --ours "$CV42"

echo "== 2D uncertainty =="
# 2026-10-18 (Stage F rebuild phase 2): the quoted 2D covariance is Q = S5 total + C_PL
# (docs/orchestration/DECISION-20261017-joseph-2d-adopt-s5-plus-playlist.md). Its Fig. 6/7 and statistical-block
# figures (and the article's Fig. 1) are NOT drawn here: they were drawn on the cluster by
# docs/orchestration/state/2d-closeout/stageF/rebuild/scripts/run_rebuild.sh (Fig. 1 locally by make_fig1_q.py),
# and are installed below, after the sync loop, by a digest-checked copy from rebuild/outputs/. That is the
# regeneration recipe; rerunning this script cannot reinstall the VL170/VL172-era figures. The VL172 recipe lines
# that stood here (plot_uncertainty_fig6_7_style.py on the *_vl170 rollup, plot_bootstrap_figs.py on
# bootstrap_MEFHC_300_vl170) were removed.
run nn_vs_gbdt_full.png  nd-unfolding  python plot_nn_vs_gbdt_full.py --gbdt res_lgbm_3d.npz --nn res_nn_3d.npz --out nn_vs_gbdt_full.png
# The ten-seed scan figure (fig:seedscan) left the note on 2026-10-18 (PHASE2 Q6); its producer line is kept,
# commented out:
# run seedscan_lgbm/seedscan_spread_2d.png  2d-unfolding  python seedscan/analyze_seedscan.py --glob "$REPO/2d-unfolding/seedscan_lgbm/2d_xsec_MEFHC_5iter_lgbm_seed*.root" --outdir "$REPO/2d-unfolding/seedscan_lgbm"

echo "== 3D generators =="
# 2026-10-03: fig:3dmodels, fig:modedecomp, fig:mec (and fig:ascencio, below) drew uncertainties from
# superseded covariances. Until a 3D/4D covariance is adopted the body shows them as central values
# only, drawn by the note-owned redraw_central_only.py on the Stage-7 flux-repaired inputs (it refuses
# other bytes) and written straight to figures/<name>_central.pdf. The superseded versions stay at
# figures/<name>.pdf for App. H (reproduction/s5p/scope.py pins three of them) and are no longer
# regenerated; their producer lines are kept, commented out. Their default inputs are pre-repair.
S7G="/pscratch/sd/j/josephrb/s5p-20260926/stage7/genfig/3d-unfolding"
# RE-1 integration (DECISION-20261023 item 3; DECISION-20261020 item 1): the 3D/4D central values are configuration
# (e). This figure is drawn from P3/P4 by docs/orchestration/state/2d-closeout/stageF/methods/re1/run2/launch/re1_f2.sbatch
# (the regeneration recipe) and installed below, after the sync loop, by a digest-checked copy from re1/run2/f/new/.
# The configuration-(a) run that stood here is kept, commented out; rerunning it would overwrite the (e) figure.
# run figures/generators_vs_unfolded_band_central.png docs/analysis-note  python redraw_central_only.py --genfig "$S7G" --outdir figures --only generators
# run figures/mode_decomp_eavail_central.png          docs/analysis-note  python redraw_central_only.py --genfig "$S7G" --outdir figures --only modedecomp
# run figures/compare_mec_eavail_central.png          docs/analysis-note  python redraw_central_only.py --genfig "$S7G" --outdir figures --only mec
# run generators_vs_unfolded_band.png  3d-unfolding/genie  python overlay_generators_band.py --unfolded ../xsec_3d_MEFHC_5iter_lgbm.root --cov uq_3d/universe_stage2_3d/uq_universe_3d_covariance.root:hCov_combined3d_total --syst-cov uq_3d/universe_stage2_3d/uq_universe_3d_covariance.root:hCov_universe3d_total --band uq_3d/stat_band_3d.root --generator GENIE-CV:genie_cv_xsec3d.root --generator Tune-v1:model_tunev1_xsec3d.root --generator NuWro:nuwro_cv_xsec3d.root --generator GiBUU:gibuu_cv_xsec3d.root --out generators_vs_unfolded_band
run compare_3d_fullcov.png           3d-unfolding/genie  python compare_3d_fullcov.py --data ../xsec_3d_MEFHC_5iter_lgbm.root --cov uq_3d/universe_stage2_3d/uq_universe_3d_covariance.root:hCov_combined3d_total --generator GENIE-CV:genie_cv_xsec3d.root --generator Tune-v1:model_tunev1_xsec3d.root --generator NuWro:nuwro_cv_xsec3d.root --generator GiBUU:gibuu_cv_xsec3d.root --out compare_3d_fullcov
# run compare_mec_eavail.png           3d-unfolding/genie  python compare_mec_eavail.py --plot compare_mec_eavail.png
# run mode_decomp_eavail.png           3d-unfolding/genie  python mode_decomp_eavail.py --gst genie_mefhc_cv_ALL.gst.root --plot mode_decomp_eavail.png

echo "== (Eavail,W) + q3 =="
run products/5d/excess_eavail_W.png  nd-unfolding  python excess_eavail_W.py
run eavailW_band.png                 3d-unfolding/genie  python overlay_eavailW_band.py --data ../../nd-unfolding/products/5d/excess_eavail_W.root --gen GENIE-CV:genie_cv_xsec_eavailW.root --gen GENIE+MEC:genie_mec_xsec_eavailW.root --gen NuWro:nuwro_cv_xsec_eavailW.root --gen GiBUU:gibuu_cv_xsec_eavailW.root --png eavailW_band.png --out eavailW_band.root
run q3_excess_projection.png         nd-unfolding  python q3_excess_projection.py

echo "== PET =="
# PET point-cloud INPUT figures (former KNOWN_ISSUES #18, RESOLVED 2026-07-10 and
# dropped from the index at 1f714b7f; its text survives at
# evidence/prepublication-2026-08-20-0b329e8a:KNOWN_ISSUES-ARCHIVE-2026-08.md:23): one invocation writes
# pet_event_displays + the muon-bearing pet_event_displays_energy_angle +
# pet_cardinality_{real,withremnant} + pet_truncation_retention.
# Reads the coverage-FIXED of_inputs_pc_fullcloud.npz (the pre-06-28 of_inputs_pc.npz
# left truth clouds empty on miss rows -> spurious cardinality-0 spike). TECHNOTE_DARK=1
# regenerates the deck versions. The end-of-file sync distributes the .pdf twins.
run products/pet/pet_event_displays_energy_angle.png nd-unfolding \
  python pet/plot_event_displays.py --npz of_inputs_pc_fullcloud.npz \
  --outdir products/pet --energy-angle --with-muon
run products/pet/pet_vs_gbdt.png          nd-unfolding  python pet/pet_vs_gbdt.py --pet products/pet/pet_weights.npz --pc of_inputs_pc.npz --gbdt products/4d/xsec_4d_MEFHC_5iter_lgbm.root --out products/pet/pet_vs_gbdt.png
run products/pet/pet_vs_gbdt_absolute.png nd-unfolding  python pet/pet_vs_gbdt.py --absolute --pet products/pet/pet_weights.npz --pc of_inputs_pc.npz --gbdt products/4d/xsec_4d_MEFHC_5iter_lgbm.root --out products/pet/pet_vs_gbdt_absolute.png
# PET vs GBDT per-bin uncertainty comparison -> pet_vs_gbdt_uncertainty_{overlay,ratiomap,ratiohist}.png
# (method-comparison figures: no MINERvA sample tag, existing PET/GBDT labels kept)
run products/pet/pet_vs_gbdt_uncertainty_overlay.png nd-unfolding  python pet/pet_vs_gbdt_uncertainty.py
# PET truth point-cloud reweight-then-project demo ->
# products/pet/fullcloud/pet_cloud_projection_{validation,xsec}.png.
# Use the coverage-fixed full-cloud sample and its matched weights/ROOT; the
# defaults are the pre-fix diagnostic inputs whose miss rows lack truth clouds.
# (validation panel is MC-only -> untagged; xsec panels are data-bearing -> minerva_tag)
run products/pet/fullcloud/pet_cloud_projection_xsec.png nd-unfolding env \
  PCPROJ_PC="$REPO/nd-unfolding/of_inputs_pc_fullcloud.npz" \
  PCPROJ_WEIGHTS="$REPO/nd-unfolding/products/pet/pet_weights_fullcloud.npz" \
  PCPROJ_OMNI="$REPO/nd-unfolding/runEventLoopOmniFold_PC_MEFHC_fullcloud.root" \
  PCPROJ_OUTDIR="$REPO/nd-unfolding/products/pet/fullcloud" \
  python pet/pointcloud_projection.py

echo "== full phase space =="
run products/5d/fps_pilot_compare_MEFHC.png  nd-unfolding  python fps_pilot_compare.py --fps-tune products/5d/xsec_2d_FPS_MEFHC_tune.root --fps-genie products/5d/xsec_2d_FPS_MEFHC_genie.root --ctrl products/5d/xsec_2d_CTRL_MEFHC.root --omnifile runEventLoopOmniFold_5D_FPS_MEFHC.root --out-png products/5d/fps_pilot_compare_MEFHC.png
run products/5d/fps_acceptance_MEFHC.png     nd-unfolding  python fps_acceptance.py --omnifile runEventLoopOmniFold_5D_FPS_MEFHC.root --out-png products/5d/fps_acceptance_MEFHC.png
run products/5d/fps_prior_envelope_MEFHC.png nd-unfolding  python fps_prior_envelope.py

echo "== 3D sec figures (from saved products; raw banks were cleaned up) =="
# RE-1 integration (DECISION-20261023 item 3; DECISION-20261020 item 1): the 3D/4D central values are configuration
# (e). This figure is drawn from P3/P4 by docs/orchestration/state/2d-closeout/stageF/methods/re1/run2/launch/re1_f2.sbatch
# (the regeneration recipe) and installed below, after the sync loop, by a digest-checked copy from re1/run2/f/new/.
# The configuration-(a) run that stood here is kept, commented out; rerunning it would overwrite the (e) figure.
# (This (a) run also wrote 3d-unfolding/eavail_spectrum.pdf, which the sync loop below would copy over the (e) figure.)
# run eavail_spectrum.png  3d-unfolding  python plot_eavail_spectrum.py --infile xsec_3d_MEFHC_5iter_lgbm.root --out eavail_spectrum.png
run ../3d-unfolding/eavail_marginal_vs_paper_pull_full.png  2d-unfolding  python compare_to_paper_fullcov.py --ours ../3d-unfolding/xsec_3d_MEFHC_5iter_lgbm.root --out-prefix "$REPO/3d-unfolding/eavail_marginal_vs_paper"
run universe_stage2_3d/uq_universe_3d_band_eavail.png  3d-unfolding/uq_3d  python plot_universe_3d_bands.py --cv ../xsec_3d_MEFHC_5iter_lgbm.root --cov universe_stage2_3d/uq_universe_3d_covariance.root --outdir universe_stage2_3d

echo "== control / migration / ascencio / landscape =="
run products/5d/control_plots.png        nd-unfolding  python make_control_plots.py
run products/5d/control_corner.png       nd-unfolding  python plot_control_corner.py
# 2026-10-03: central values only, as for the 3D generators above (our bars and the chi^2 came from
# the superseded unified-throw 4D covariance; the published points keep the published covariance).
# RE-1 integration (DECISION-20261023 item 3; DECISION-20261020 item 1): the 3D/4D central values are configuration
# (e). This figure is drawn from P3/P4 by docs/orchestration/state/2d-closeout/stageF/methods/re1/run2/launch/re1_f2.sbatch
# (the regeneration recipe) and installed below, after the sync loop, by a digest-checked copy from re1/run2/f/new/.
# The configuration-(a) run that stood here is kept, commented out; rerunning it would overwrite the (e) figure.
# run figures/ascencio_fullcov_compare_central.png docs/analysis-note  python redraw_central_only.py --xsec4d "$REPO/nd-unfolding/products/4d/xsec_4d_MEFHC_5iter_lgbm.root" --supplemental "$REPO/3d-unfolding/genie/ascencio_2110.13372_supplemental.txt" --outdir figures --only ascencio
# run products/4d/ascencio_fullcov_compare.png nd-unfolding  python compare_ascencio_fullcov.py
# 2026-11-13: --print-style draws the note's print style (note_print_style.py); the installed PDF is the committed
# note-figstyle-20261113 copy (below, after the sync loop).
run minerva_unfolding_landscape.png      3d-unfolding  python plot_minerva_landscape.py --print-style

echo
echo "==================== SUMMARY ===================="
echo "PASS: ${#PASS[@]}    FAIL: ${#FAIL[@]}"
[ ${#FAIL[@]} -gt 0 ] && printf 'FAILED: %s\n' "${FAIL[@]}"
rm -f /tmp/fig_$$.log

echo
echo "== sync into docs/analysis-note/figures/ =="
# The note is PDF-only (preamble.tex \DeclareGraphicsExtensions{.pdf}); every
# plotting script writes a .pdf next to its .png via technote_style's savefig
# twin, so we sync the vector .pdf by basename.  A figure must already exist in
# figures/ to be refreshed (this is an update-in-place sync, not an installer).
FIGDIR="$REPO/docs/analysis-note/figures"
for fig in "$FIGDIR"/*.pdf; do
  base=$(basename "$fig")
  src=$(find "$REPO/2d-unfolding" "$REPO/3d-unfolding" "$REPO/nd-unfolding" \
        -name "$base" -newer "$fig" 2>/dev/null | head -1)
  if [ -n "$src" ]; then
    cp "$src" "$fig"; echo "  synced $base"
  fi
done

echo
echo "== Q figures from the Stage F rebuild receipts (digest-checked copy) =="
# Runs after the sync loop so that no older product under $REPO/2d-unfolding can overwrite them. Each source is
# a committed phase-1 output; the digests are those of rebuild/outputs/SHA256SUMS.cfs (Fig. 1: RUN-fig1.txt).
RB="$REPO/docs/orchestration/state/2d-closeout/stageF/rebuild/outputs"
sha256_of() { if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" | cut -d' ' -f1; else shasum -a 256 "$1" | cut -d' ' -f1; fi; }
install_receipt_fig() {  # install_receipt_fig <source under $RB> <figure basename> <sha256>
  local src="$RB/$1" dst="$FIGDIR/$2" want="$3"
  if [[ "$(sha256_of "$src")" != "$want" ]]; then
    echo "REFUSE install: $src does not have sha256 $want" >&2; exit 1
  fi
  cp "$src" "$dst"
  if [[ "$(sha256_of "$dst")" != "$want" ]]; then
    echo "REFUSE install: $dst differs from $src after the copy" >&2; exit 1
  fi
  echo "  installed $2 ($want)"
}
# RE-2 integration: the four Q figures that stood here (Figs. 6/7 and the statistical-block figures, drawn from E_U and
# Q) are no longer installed; their E_R and Q_R versions are installed below from RE-2 part C. The superseded lines:
# install_receipt_fig fig67/MEFHC_fig6_7_uncertainty_pt.pdf MEFHC_fig6_7_uncertainty_pt.pdf c12f37d5d8a39dfc16f38897ce708ff24f4428257a1fbdb644791a7020222d46
# install_receipt_fig fig67/MEFHC_fig6_7_uncertainty_pz.pdf MEFHC_fig6_7_uncertainty_pz.pdf e3bfb7273609d0c9399c28591da0fc01e706ce3769b11ea722fceb2541d5f323
# install_receipt_fig stat/uq_spread_2d.pdf               uq_spread_2d.pdf                79d6b35fe81fe71c71738996090b27c2fded2d990bb9bbae670927fbf253a7cb
# install_receipt_fig stat/uq_corr_2d.pdf                 uq_corr_2d.pdf                  42ea035f77b767b3d2d0dc3d2cbd57c9537f957e2ae39aef936a9eb373fc0d97
# Fig. 1 is no longer installed from the rebuild (82665808..., drawn from E_U and Q): RE-2 integration installs the
# refined redraw below.

echo
echo "== Fig. 1 from COV2D-G2R's RE-2-shapes route A (E_R and C_new; digest-checked copy) =="
# Source: #1168's redraw on the adopted 2D covariance (D1: COV2D-G2R's C_new), drawn by re2c_fig1.py 2aadeac8... on
# route A's outputs (fd/receipts-cov2d/g2r/re2shapes/fig1/route-a/RUN-fig1.txt). Before D1: RE-2 part C amendment 3's
# redraw, re2-integration/fig1/fig1_validation.pdf 71a2ea48....
RE2F="$REPO/docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-cov2d/g2r/re2shapes/fig1/route-a"
src="$RE2F/fig1_validation.pdf"; want=1ead58a2223ecf88f3de505d7cbcca76ab306af49814ea7c9d50ec0f2c373e0c
if [[ "$(sha256_of "$src")" != "$want" ]]; then echo "REFUSE install: $src does not have sha256 $want" >&2; exit 1; fi
cp "$src" "$FIGDIR/paper_fig1_validation.pdf"
if [[ "$(sha256_of "$FIGDIR/paper_fig1_validation.pdf")" != "$want" ]]; then
  echo "REFUSE install: $FIGDIR/paper_fig1_validation.pdf differs from $src after the copy" >&2; exit 1
fi
echo "  installed paper_fig1_validation.pdf ($want)"

echo
echo "== 2D figures from RE-2 part C (E_R and Q_R; digest-checked copy) =="
# Every 2D figure the note, paper or primer includes whose producer reads the central value or its covariance
# (RE2-DECLARATION-C.md sec. 7). Drawn on Perlmutter by 2d-unfolding/re2/partc/re2c_run.sh with --ours E_R and Q_R
# (re2/run/partc_r2/partc-r2/logs/steps.tsv: fig67, stat_figs, fig13, paper_slices, xsec_proj, pull_full, models,
# tension), fetched read-only from /pscratch/sd/j/josephrb/2d-closeout-re2-20261023/partc-r2 and committed beside the records; each digest is that file's line in
# re2/run/partc_r2/partc-r2/SHA256SUMS. The efficiency heat map is xsec_proj's, drawn from E_R (hEff2D equals E_U's:
# RE2-PARTB-REPORT.md PB-ER-eff). These installs run after the sync loop and after the E_U run lines above, which they
# override; rerunning those lines does not reproduce these files.
RE2G="$REPO/docs/orchestration/state/2d-closeout/stageF/methods/re2-integration/figs"
install_re2_fig() {  # install_re2_fig <basename under $RE2G and in $FIGDIR> <sha256>
  local src="$RE2G/$1" dst="$FIGDIR/$1" want="$2"
  if [[ "$(sha256_of "$src")" != "$want" ]]; then
    echo "REFUSE install: $src does not have sha256 $want" >&2; exit 1
  fi
  cp "$src" "$dst"
  if [[ "$(sha256_of "$dst")" != "$want" ]]; then
    echo "REFUSE install: $dst differs from $src after the copy" >&2; exit 1
  fi
  echo "  installed $1 ($want)"
}
# install_re2_fig MEFHC_fig6_7_uncertainty_pt.pdf        6055be9534cfaa1e149d59ec54cde0be7bc28272cbe584bafb5aab9751b97cd3   # G2R (2026-11-15): replaced by the print-style install below, drawn from RE-2-shapes run 2
# install_re2_fig MEFHC_fig6_7_uncertainty_pz.pdf        ef0de3504fcbfb49d83073f0cf59ef7af5abf00ce1bda22fe5943a49bb0e6f62   # G2R (2026-11-15): replaced by the print-style install below, drawn from RE-2-shapes run 2
install_re2_fig uq_spread_2d.pdf                       a51bc4ee186a2c3bba942f6de6cd4bed74b8de7508e763e0b0bc698a0a78e9de
install_re2_fig uq_corr_2d.pdf                         fea063cc6eeba9925bef2ac7c096118fdd23a7f443aea8afde4392de214c75b1
# install_re2_fig MEFHC_5iter_fig13.pdf                  4924917e903b5e4ee6133f5e37b91aa11f301d7ea7242561680ea1ba10a4fb3b
# install_re2_fig MEFHC_5iter_pull_full.pdf              3d108335117afd57b14f4bf1661ac8e06ffdbfdfb1ceb17903fa00724b40396f
# install_re2_fig MEFHC_5iter_xsec_eff_heatmap.pdf       1008a7e9e0832c1607bfce9bd38ee52b5af86baed4fb868171fdc56ab5df24ab   (note palette, 2026-11-18: installed below with its ledger row)
# install_re2_fig MEFHC_5iter_xsec_paper_pt_slices.pdf   8836d7b56b75131c6affa81a2a752655208c40e01ff53270ebd7acfd306f04a8
# install_re2_fig MEFHC_5iter_xsec_paper_pz_slices.pdf   6f7a11aff1da1c84c8c7cd211dc8e5714fa15334eafbd83ae0ef4c45f0a84d8f
# install_re2_fig MEFHC_5iter_xsec_proj_pt.pdf           ea2c1dce31ba543d059dab3c5a844990928a45c03bd3675d3b094ae441626249
# install_re2_fig MEFHC_5iter_xsec_proj_pz.pdf           e728d02ecb66077dc0b7de68c9d8bf32b87c7e844bf5d6d8e1ccfe70bdf61db8
# install_re2_fig model_comp_projections.pdf             2c39fe21ed16fc31d5c08d7012cf6248a3aae575f5dc162081b1e79929ebf8d8
# install_re2_fig model_comp_ratio_maps.pdf              266c856435e8944cf5cbf654e9dfe455d6318c6a6000acc89e25c3bd6fafc343
# install_re2_fig tension_chi2_map.pdf                   30a3598db8b99ebacc41dd8d2b48ec6861e5d80524ab48ad551b4e56e869155a
# install_re2_fig tension_mode_maps.pdf                  adf5bf3feb8732553c64dfc9aa795eeee91f07dbe2d096fc725b9f9a8492667d
# install_re2_fig tension_spectrum.pdf                   295b17cd6c26cb741e23baec3cfd8d5a930b76246cec200e69fb60fc53e3c5d3
# 2026-11-01: the eleven figures above that the 2D figure restyle redrew (fig-restyle-20261031/DECLARATION.md section 5;
# BINDING.md, BINDING-A1.md, BINDING-A2.md; Joseph's "Install them" after his third look) are no longer installed from
# RE-2 part C; their lines above stay as comments. They are installed below from fig-restyle-20261031/figs-a2/, the
# bound rerun's "after" PDFs (run-a2/after/SHA256SUMS); DIGESTS.tsv there gives each figure's RE-2 and restyled
# digests. The figure data are RE-2's, bit for bit (compare.py's data-only hash, run-a2/CHECKS.txt).
RSG="$REPO/docs/orchestration/state/2d-closeout/stageF/methods/fig-restyle-20261031/figs-a2"
install_restyle_fig() {  # install_restyle_fig <basename under $RSG and in $FIGDIR> <sha256>
  local src="$RSG/$1" dst="$FIGDIR/$1" want="$2"
  if [[ "$(sha256_of "$src")" != "$want" ]]; then
    echo "REFUSE install: $src does not have sha256 $want" >&2; exit 1
  fi
  cp "$src" "$dst"
  if [[ "$(sha256_of "$dst")" != "$want" ]]; then
    echo "REFUSE install: $dst differs from $src after the copy" >&2; exit 1
  fi
  echo "  installed $1 ($want)"
}
# install_restyle_fig MEFHC_5iter_fig13.pdf                 a5530bfc0c3220a0a522dfcaa52f143752dd67465c525237acb0ad8cf722237f   (font-only pass, 2026-11-14: installed below)
# install_restyle_fig MEFHC_5iter_xsec_proj_pt.pdf          bfff6d0b8034436f6bd46d92a9d67e029812fb545f38a36eeb30ca5cbad157c2   (font-only pass, 2026-11-14: installed below)
# install_restyle_fig MEFHC_5iter_xsec_proj_pz.pdf          ff27c7d477af3c4099631c39e462972842b9fe805264c507876b8b40570f9e58   (font-only pass, 2026-11-14: installed below)
# install_restyle_fig MEFHC_5iter_pull_full.pdf             fd84d992f3b212be3be6da06badbe3dfb5123f160f34f10e81d7f65cc80afd3d   (font-only pass, 2026-11-14: installed below)
# install_restyle_fig MEFHC_5iter_xsec_paper_pt_slices.pdf  ed6fb4162bdf84f6c57fedde39912fff13d0f387e5e5bc6d7a028af3ecdb2cdd   (font-only pass, 2026-11-14: installed below)
# install_restyle_fig MEFHC_5iter_xsec_paper_pz_slices.pdf  18252c59b3a0572d490c63770df1ec2e38b8989bf3be8165985cbac799d6daf4   (font-only pass, 2026-11-14: installed below)
# install_restyle_fig tension_spectrum.pdf                  5de8157fb9831a9b6b895f231ac771488e1eef1334c0bef7e19885e676b83c5d   (font-only pass, 2026-11-14: installed below)
# install_restyle_fig tension_chi2_map.pdf                  7161ded1a2a6666de6c04d55652c00bf2435a72a38e8ef0e422a6105c002ef08   (font-only pass, 2026-11-14: installed below)
# install_restyle_fig tension_mode_maps.pdf                 7ea2d004150d1633b7e92b655d9664f7d183444a46fd48830b43f7592cfc2c71   (font-only pass, 2026-11-14: installed below)
# install_restyle_fig model_comp_projections.pdf            44f2a7b7800b5c59821e0bda87e12c137237f1bed89fe9fae87a2a4aa15294c0   (font-only pass, 2026-11-14: installed below)
# install_restyle_fig model_comp_ratio_maps.pdf             838e5fc4669cf4d58b20f81dbda29f5131c1a57a9d34202948b9830ab51648bd   (font-only pass, 2026-11-14: installed below)

echo
echo "== 3D/4D configuration-(e) figures from RE-1 run 2 F2 (digest-checked copy) =="
# Also after the sync loop, so that an older (a) product under $REPO/3d-unfolding (eavail_spectrum.pdf) cannot
# overwrite them. Sources: the committed F2 outputs; digests: re1/run2/f/SHA256SUMS.f2 and RE1-REPORT-2.md sec. 4.
# Recipe: re1/run2/launch/re1_f2.sbatch. The F2 PDFs are installed as they are; F2 wrote no .png beside them here.
RE1F="${RE1F:-$REPO/docs/orchestration/state/2d-closeout/stageF/methods/re1/run2/f/new}"
install_re1_fig() {  # install_re1_fig <basename under $RE1F and in $FIGDIR> <sha256>
  local src="$RE1F/$1" dst="$FIGDIR/$1" want="$2"
  if [[ "$(sha256_of "$src")" != "$want" ]]; then
    echo "REFUSE install: $src does not have sha256 $want" >&2; exit 1
  fi
  cp "$src" "$dst"
  if [[ "$(sha256_of "$dst")" != "$want" ]]; then
    echo "REFUSE install: $dst differs from $src after the copy" >&2; exit 1
  fi
  echo "  installed $1 ($want)"
}
install_re1_fig eavail_spectrum.pdf                     d2ae66c4149c8f33a7cc5e3635cc86e4e839e20045c3752c8bf87ff4e3aadf49
install_re1_fig generators_vs_unfolded_band_central.pdf 48210da26e8e84bd8cae0d83df1de85a5996c005d78f2a959225efd24e44e3b1
install_re1_fig mode_decomp_eavail_central.pdf          009a26be4dc3b1a8ec7bfc51ee1e038c74b6a62e6490e027ece08b63f4febc12
install_re1_fig compare_mec_eavail_central.pdf          09e2b824cfa10671f3bbab33764778424493011081e40ea507073e3307fd63f4
install_re1_fig ascencio_fullcov_compare_central.pdf    9bd4316e8bd94ecd6b0681ef955579fbf0e867847a6f43274fda64349584d2a5

echo
echo "== note print style (2026-11-13; digest-checked copy) =="
# The methods paper's figure style for the note's figures (director, 2026-11-13; note_print_style.py): serif CM text at
# the paper's sizes, each canvas at its printed width. Producers run with --print-style; the plotted data are the
# committed outputs', bit for bit (note-figstyle-20261113/README.md: three arms, capture_any.py / compare_any.py).
# Recipes: nd-unfolding/gbdt_model_dependence/analyze.py --print-style --out <dir> (its package results/ stay in the
# default style), and plot_minerva_landscape.py --print-style (run above). Also after the sync loop.
NPS="$REPO/docs/orchestration/state/2d-closeout/stageF/methods/note-figstyle-20261113/figs"
install_printstyle_fig() {  # install_printstyle_fig <basename under $NPS and in $FIGDIR> <sha256>
  local src="$NPS/$1" dst="$FIGDIR/$1" want="$2"
  if [[ "$(sha256_of "$src")" != "$want" ]]; then
    echo "REFUSE install: $src does not have sha256 $want" >&2; exit 1
  fi
  cp "$src" "$dst"
  if [[ "$(sha256_of "$dst")" != "$want" ]]; then
    echo "REFUSE install: $dst differs from $src after the copy" >&2; exit 1
  fi
  echo "  installed $1 ($want)"
}
# install_printstyle_fig gbdt_recovery.pdf                62bf4a8337115ffa4ca4227bf15d2883c6a74771583f672122ca5b14dcf69e11   (note palette, 2026-11-17: installed below)
# install_printstyle_fig gbdt_bias_spread.pdf             f1786f4862eea1a3439b79ef7af2132969e95f7fb087bddcf9661802cf6310c2   (note palette, 2026-11-17: installed below)
# install_printstyle_fig gbdt_coverage.pdf                422ef3f7c8e53b47d371cbeee68742a869ec372394c81a8324a121c18a10fd54   (note palette, 2026-11-17: installed below)
# install_printstyle_fig gbdt_prior_response.pdf          445374318044846a72b8a71da3a474d3d63820e8f5491ac6d5eb06a42745a2d3   (note palette, 2026-11-17: installed below)
install_printstyle_fig minerva_unfolding_landscape.pdf  bf1f14eae609fdf06f01a248674a175a1df72bd0ed1b4c8f269b860e66b78372
# Group C, family 1 (2026-11-14): drawn locally with --from-arrays --print-style from the dumps of one cluster pass
# (note-figstyle-20261113/runs/family1/dumps/; recipe: make_control_plots.py / plot_control_corner.py --from-arrays <dump> --print-style).
install_printstyle_fig migration_resolution.pdf         7ea7fd45dd7276b193f2ca4554a8247c6ee528a2e59acace4666e9486af8cc9b
install_printstyle_fig control_corner.pdf               09f291027d63f4f018e651d66be1e6e53aa95ee3ba8c028905621fd2ff0aa477
# Family 1b (2026-11-14): Fig. 1 from the extended-display dump of one cluster pass (runs/family1b/dumps/), with
# --from-arrays <dump> --extended-display --print-style.
# install_printstyle_fig control_plots.pdf                dcea96fa289c03a4c204804c2852242d4236ff96330d28877bbd0ac1e3a94602   (note palette, 2026-11-17: installed below)
# Family 2, group R (2026-11-14): the eleven 2D figures of 10-31 in the paper fonts (restyle_2026_10 --print-font,
# font family and mathtext only), from one login-node pass (note-figstyle-20261113/runs/family2/). Data, colours and
# styles bit-equal to the restyle (compare.py COMPARE :: PASS); the restyle install lines above are now comments.
# install_printstyle_fig MEFHC_5iter_fig13.pdf                 d9bb9a951ef13b6d6a6146f7de2a7b83ef07c425a9c2572d1069a3ec1056551e   (note palette, 2026-11-17: installed below)
# install_printstyle_fig MEFHC_5iter_xsec_proj_pt.pdf          a770d7477cad9aabe25faf1f0694654a67606a7977028898ca7bed8c1332bacc   (note palette, 2026-11-17: installed below)
# install_printstyle_fig MEFHC_5iter_xsec_proj_pz.pdf          52a0724ee3e9d25d007c116d92969e6641ca2e2a73a32a21db7818b1414654dd   (note palette, 2026-11-17: installed below)
# install_printstyle_fig MEFHC_5iter_pull_full.pdf             a9510fb997ba90577a95b6bead042781bbc882abee0c34baa736516619793add   (note palette, 2026-11-17: installed below)
# install_printstyle_fig MEFHC_5iter_xsec_paper_pt_slices.pdf  c97195af5d71d1401782446bf9ac1260d4f07bf081b344052dafc4c47661713f   (note palette, 2026-11-17: installed below)
# install_printstyle_fig MEFHC_5iter_xsec_paper_pz_slices.pdf  9c18ea23b4525375b76eca054d4db6db4e64c902326607e313b3c41e60ed73a9   (note palette, 2026-11-17: installed below)
# install_printstyle_fig tension_spectrum.pdf                  d358068b707b8b677cbe2c1f0304427621df76d2da03c9f051822cb38371fdd7   (note palette, 2026-11-17: installed below)
# install_printstyle_fig tension_chi2_map.pdf                  dfc675ac425b90c94890e386b2630482e48d55867839100bc242bcbc64381ed5   (note palette, 2026-11-17: installed below)
# install_printstyle_fig tension_mode_maps.pdf                 049647417c6aaaf889a885a573f311b61d2e6819cdf4bbe174894a5e1e376996   (note palette, 2026-11-17: installed below)
# install_printstyle_fig model_comp_projections.pdf            ae7f5a54efd234e80388c9f6990721d022dc5df0278637d190b78b2f4938ec19   (note palette, 2026-11-17: installed below)
# install_printstyle_fig model_comp_ratio_maps.pdf             49f0d76c0eb17dc9e22522a472baa28fd5e436d9b2863bb9be3a6e59135b7307   (note palette, 2026-11-17: installed below)
# Families 3-6, group C (2026-11-15): drawn locally with --print-style from the dumps of one cluster pass per family
# (note-figstyle-20261113/runs/family3..family6/); the four RE-1 central redraws by tools/restyle_family4.py from their
# pinned figure pickles; eavailW_band is a new matplotlib rendering of the ROOT figure (numerical check, runs/family5/).
# Each one's drawn data equal its cluster off arm's (the README gives the checks and their one environmental exception).
install_printstyle_fig uq_spread_2d.pdf                      41347061d6064aaae142895cbfeaf5d5c2449cdd9c72f8a4b6f153cd9fbf5031
install_printstyle_fig uq_corr_2d.pdf                        f202c729700676096b4274be73ab5d30ffa31d94823c070c3d3491b4784d0b02
# install_printstyle_fig eavail_spectrum.pdf                   906a6473311775703dc4ff92ee52bdd61deb7b1173b7998c41331fbe1723723e   (note palette, 2026-11-17: installed below)
# install_printstyle_fig generators_vs_unfolded_band_central.pdf9ee744b3a36761ae2e854e7ddce23aa35633f636a532fd751c798bebea459884   (note palette, 2026-11-17: installed below)
# install_printstyle_fig mode_decomp_eavail_central.pdf        35498b2d0e92d61ac056bbef1e0d432716546bf627a7fee662f7770631961568   (note palette, 2026-11-17: installed below)
# install_printstyle_fig compare_mec_eavail_central.pdf        a43a2499d84c1c95c096fa0edd4d941ed088c664489cb28304503a50de896005   (note palette, 2026-11-17: installed below)
# install_printstyle_fig ascencio_fullcov_compare_central.pdf  ae1e5e59d641c3457a0db11c826c1a064fd1f1ae96e282657750a6b49aa50a4a   (note palette, 2026-11-17: installed below)
# install_printstyle_fig q3_excess_projection.pdf              1b86a31b2fc2ae2000e451c22253be5d207146a66cf8663f09e0e80ae02fd85b   (note palette, 2026-11-17: installed below)
install_printstyle_fig fps_acceptance_MEFHC.pdf              ab63256c62c14945aa111333fca73edefcca57b2d3a9a98283d7cfe26b1219c8
install_printstyle_fig fps_pilot_compare_MEFHC.pdf           a910ccca6084b5f652df0840e65a0d95117a154b22f22a87d519d85f26e5181f
install_printstyle_fig fps_prior_envelope_MEFHC.pdf          55b3aeeb06e3fffcdcbfd7b0d30450378cee91fdc1e885095f677a6e873e68de
# install_printstyle_fig eavailW_band.pdf                      c9e7fcdbefa35e609272ec56616a449c85896cadc6e18b7b2f6366384722144a   (note palette, 2026-11-17: installed below)
install_printstyle_fig paper_joint_nulls.pdf                 66888ffc0f3e8e9d41b78e4962063cbc67f2649af6cdef82532c26313d5865bb
# fig6/7 (family 7; the director's approval of 2026-11-15): plot_uncertainty_fig6_7_style.py --from-projections on RE-2-shapes
# run 2's fig67_projections.json (main d58d0d18, #1167) --print-style; identity: note-figstyle-20261113/runs/family7/
install_printstyle_fig MEFHC_fig6_7_uncertainty_pt.pdf      031b12a1c0c52f59baf8c14360d652c87b000232a3294a131c11f71068f8624f
install_printstyle_fig MEFHC_fig6_7_uncertainty_pz.pdf      b1cfd7ccf1ca2f563f1c684422aefc915c011db041cd09d9deb03dd2164ba9f4

echo "== note palette (2026-11-17; digest-checked copy) =="
# The note's figure palette (Joseph, 2026-11-17; COMBINED-PLAN.md section 5; note_palette.py and its test): the paper's
# colours, #CC79A7 for GENIE CV, this work in red in every figure. Each figure is drawn locally by its recipe in
# note-figstyle-20261117/README.md; its arm 0 reproduces the installed print-style file (bytes apart from the creation
# date), and its arm 1's data artists equal arm 0's, with each colour as recolour.tsv and palette.tsv map it
# (fig-restyle-20261031/tools/compare.py --recolour --palette --styles --restyle). The print-style lines above stay
# as comments. Also after the sync loop.
NPAL="$REPO/docs/orchestration/state/2d-closeout/stageF/methods/note-figstyle-20261117/figs"
install_palette_fig() {  # install_palette_fig <basename under $NPAL and in $FIGDIR> <sha256>
  local src="$NPAL/$1" dst="$FIGDIR/$1" want="$2"
  if [[ "$(sha256_of "$src")" != "$want" ]]; then
    echo "REFUSE install: $src does not have sha256 $want" >&2; exit 1
  fi
  cp "$src" "$dst"
  if [[ "$(sha256_of "$dst")" != "$want" ]]; then
    echo "REFUSE install: $dst differs from $src after the copy" >&2; exit 1
  fi
  echo "  installed $1 ($want)"
}
# Family 4 (Figs. 19-22): tools/palette_family4.py on the pinned pickles (matplotlib 3.10.8); runs/family4/.
install_palette_fig generators_vs_unfolded_band_central.pdf  1563f52b347938593bc4033fcaff22fa32cd33eb463f23d8b1ff9533e5252b7d
install_palette_fig mode_decomp_eavail_central.pdf           270237928effabf36fa59be7de86d6a8c4023bc9187b8a7c8978ee2b6090cf31
install_palette_fig compare_mec_eavail_central.pdf           2e81a44506e958fda4f063c5b88350a4d3eb6f00d4d02c4906c34bb94e39a2aa
install_palette_fig ascencio_fullcov_compare_central.pdf     0d65baa9b139a7b45da54e54042b6b18c3a08b2d3c82fd05d64629d86452a1ab
install_palette_fig eavailW_band.pdf                         ded40ea27702a8654d99d96d53336d037292424c718fa4427fb9ef8764408584
# install_palette_fig q3_excess_projection.pdf                 8a3a5bb5d44156432b249d7165e56cbcfed464b6c7ff69d0bd37ee2e94df3d88   (figure pass, 2026-11-19: installed below)
install_palette_fig eavail_spectrum.pdf                      457fa20edec3de6520de49e99b04f4c989e7cc175289edc4b96d62383807dac1
install_palette_fig control_plots.pdf                        9bfd50652a470a7f2edf5d6bd7fd30b20983b3f0264dfe44444c4768088af4ab
install_palette_fig gbdt_recovery.pdf                        215f740a4b25a46519cc7b2bad5240730aa90aec4cb0d4cc7f1d0f3e3f8c191e
install_palette_fig gbdt_bias_spread.pdf                     625b9452d4c28299c4a6a38eda3e14fa40670ffeccde9fa67ab154cbedff033e
install_palette_fig gbdt_coverage.pdf                        511817bdc1e17211141c812f56057ab5f04bbd8ede171978010c1a75a82a87fe
install_palette_fig gbdt_prior_response.pdf                  aa0b997e73a7babc002b6c4ca4bca23d7c004004f317c9d52e5eb8428c6bfb7e
install_palette_fig paper_fig_coverage.pdf                   247239f0fec1ca9446195a6a11c2457a66c3041d20d35e4710e678fc05dd088e
# install_palette_fig paper_fig_bkg_residual.pdf               3cac32b105aa9617706bf38d4398fb2ddc9e1d24c5cab65690d726ddfbf72c4d   (2026-11-18: the W-edge label fixed, installed below)
install_palette_fig model_comp_projections.pdf               2b60883a3fab04edba0fb36a7bd61ca7d59317028c4863486da6a1440af35029
install_palette_fig model_comp_ratio_maps.pdf                0c10ff269536b2aa3bd7bead06fc17af1c6d8a9d380c24afd5c7d0ce39ff90e0
install_palette_fig tension_spectrum.pdf                     98d7ce2c9765275be579ef8345fde17f50a8b24b0e2f26846475d6998a163661
install_palette_fig tension_chi2_map.pdf                     4f18c35be762355f16410bb8798ceae8f303e640e33bda985c90dbfdee23236a
install_palette_fig tension_mode_maps.pdf                    f4d8a4197aa0318fd9704ab7c0d0011c9a85425e12398966bb552a1b79c80412

echo "== note-newfigs-20261118 (digest-checked copy) =="
# Two figures from committed records (cov2d, the director's request of 2026-11-18; the readability read's additions,
# approved by Joseph): the sixteen-cell headline figure and the run-period graphic. Recipe and checks:
# note-newfigs-20261118/README.md (python3 -I make_fig_fived16_headline.py; python3 -I make_fig_runperiod_steps.py; each
# pins its records' sha256 and asserts the plotted numbers equal them). Also after the sync loop.
NNF="$REPO/docs/orchestration/state/2d-closeout/stageF/methods/note-newfigs-20261118"
install_newfig() {  # install_newfig <basename under $NNF and in $FIGDIR> <sha256>
  local src="$NNF/$1" dst="$FIGDIR/$1" want="$2"
  if [[ "$(sha256_of "$src")" != "$want" ]]; then
    echo "REFUSE install: $src does not have sha256 $want" >&2; exit 1
  fi
  cp "$src" "$dst"
  if [[ "$(sha256_of "$dst")" != "$want" ]]; then
    echo "REFUSE install: $dst differs from $src after the copy" >&2; exit 1
  fi
  echo "  installed $1 ($want)"
}
install_newfig fived16_headline.pdf   69833f108f946b9b51c6795b10f1bdce941971ebf683482623735728e3059e6f
install_newfig runperiod_steps.pdf    1088ae36889bffeea33182c3940bbf1ace4032dab1ff06e91000443618c12606
install_palette_fig MEFHC_5iter_fig13.pdf                    0c451b833ce7fff455cb526ff172c27b9e8ed8fa9ff8a422d097116d28691aef
install_palette_fig MEFHC_5iter_xsec_paper_pt_slices.pdf     180b87866305bf9ededbb94a7ba8aa796a49b3a629bdc219910fb077b1bc4233
install_palette_fig MEFHC_5iter_xsec_paper_pz_slices.pdf     e64b65ffbf6bae236cc7ee7c1f65f434497b0a8dc5ca0214039a7e4dd1aa941e
install_palette_fig MEFHC_5iter_xsec_proj_pt.pdf             9f6911d470fe7044c9c7801e59a1d55389960d6e246b423727a9115b78234a75
install_palette_fig MEFHC_5iter_xsec_proj_pz.pdf             56e1e99de5cfe08684a7b8288c04ecb830b14b79ffa8c10500f1815b86ca2a5d
install_palette_fig MEFHC_5iter_pull_full.pdf                35c31c49a9311920b57d45d716417d468d1de857d316f22e4a7a3f3a5055ec00
# Fig. 6 (2026-11-18): the efficiency map in the paper's fonts (tier 2, runs/xsec_proj/). Its re2-integration ledger G row
# is re-pointed to this record (fig-restyle ruling 1: re-point, do not replace), and check_ledger.py requires that row's
# figure to be installed as "install_restyle_fig <basename> <sha256>" from the row's copy directory, so RSG names it.
RSG="$REPO/docs/orchestration/state/2d-closeout/stageF/methods/note-figstyle-20261117/figs"
install_restyle_fig MEFHC_5iter_xsec_eff_heatmap.pdf       049fbf9096da5382d0fc3572849ed29636836d6390f71cd1cdb909f651b1d082
# Fig. 34 (2026-11-18): its x label ends the W edges at the 100 GeV catch-bin edge, as m3_common.W_EDGES and the note's
# binning (sec_method.tex:207) do (it printed infinity; text_fixes.tsv; runs/bkg5d/). figs/ is immutable once
# committed, so the corrected file is in figs-r2/.
RSG="$REPO/docs/orchestration/state/2d-closeout/stageF/methods/note-figstyle-20261117/figs-r2"
install_restyle_fig paper_fig_bkg_residual.pdf             193cc23653aaed3c86af3cdd405a2a82ca12eea29810749bc86dd6bf4f7e4e83

echo "== note-figpass-20261119 (digest-checked copy) =="
# The figure pass (cov2d, the director's request of 2026-11-19): figures drawn at their printed size and laid out again,
# presentation only. Recipe and checks: note-figpass-20261119/README.md (tools/arms_layout.sh; arm 0 reproduces the
# installed file, arm 1's data, colours, styles and drawn strings equal arm 0's). Also after the sync loop.
NFP="$REPO/docs/orchestration/state/2d-closeout/stageF/methods/note-figpass-20261119/figs"
install_layout_fig() {  # install_layout_fig <basename under $NFP and in $FIGDIR> <sha256>
  local src="$NFP/$1" dst="$FIGDIR/$1" want="$2"
  if [[ "$(sha256_of "$src")" != "$want" ]]; then
    echo "REFUSE install: $src does not have sha256 $want" >&2; exit 1
  fi
  cp "$src" "$dst"
  if [[ "$(sha256_of "$dst")" != "$want" ]]; then
    echo "REFUSE install: $dst differs from $src after the copy" >&2; exit 1
  fi
  echo "  installed $1 ($want)"
}
install_layout_fig q3_excess_projection.pdf                 32084e6044ae80181b5f627d499012b16197b67f762d02a8a7c6ac9ee1ca47ef

echo
echo "== paper-only vector crops =="
# These are lossless crops of validated source figures, not new measurements.
# The validation crop keeps only the standardized-residual map and removes the
# covariance-distance histogram; the generator crop removes the ROOT canvas's
# large unused margin.
assert_pdf_page_size() {
  local source_pdf="$1"
  local expected_size="$2"
  local actual_size
  if command -v pdfinfo >/dev/null 2>&1; then
    actual_size=$(pdfinfo "$source_pdf" | awk '/^Page size:/ {print $3 " x " $5; exit}')
  elif command -v gs >/dev/null 2>&1; then
    # NERSC's TeX Live module supplies pdfcrop but not Poppler's pdfinfo.
    # Query the first-page MediaBox with the system Ghostscript instead.
    actual_size=$(gs -q -dNOSAFER -dNODISPLAY -sSourcePDF="$source_pdf" -c \
      'SourcePDF (r) file runpdfbegin /mb 1 pdfgetpage /MediaBox get def
       mb 2 get mb 0 get sub =only ( x ) print
       mb 3 get mb 1 get sub =only quit')
  else
    echo "REFUSE paper crop: neither pdfinfo nor gs is available to verify $source_pdf" >&2
    exit 1
  fi
  if [[ "$actual_size" != "$expected_size" ]]; then
    echo "REFUSE paper crop: $source_pdf is $actual_size pts, expected $expected_size pts" >&2
    exit 1
  fi
}

# Absolute panel crops are intentionally coupled to these source canvases.
# Refuse rather than silently select the wrong panel after upstream regeneration.
# 2026-11-17 (the note palette, tier 2): Fig. 8 is drawn at its 0.70 \textwidth slot, 4.55 x 2.3 in
# (note-figstyle-20261117/resize.tsv), so its page and the left-panel crop change with it. The crop keeps the map and
# its colour bar: their right edge is at x = 171.3 pt and the histogram's y label begins at 174.0 pt (pdftotext -bbox).
assert_pdf_page_size "$FIGDIR/MEFHC_5iter_pull_full.pdf" "327.6 x 165.6"
assert_pdf_page_size "$FIGDIR/excess_eavail_W.pdf" "1152 x 331.2"

pdfcrop --bbox '0 0 172.5 165.6' \
  "$FIGDIR/MEFHC_5iter_pull_full.pdf" \
  "$FIGDIR/paper_validation_residual.pdf"
pdfcrop --margins '4 4 4 4' \
  "$FIGDIR/eavailW_band.pdf" \
  "$FIGDIR/paper_eavailW_generators.pdf"
pdfcrop --bbox '400 0 1152 331.2' \
  "$FIGDIR/excess_eavail_W.pdf" \
  "$FIGDIR/paper_joint_localization.pdf"
