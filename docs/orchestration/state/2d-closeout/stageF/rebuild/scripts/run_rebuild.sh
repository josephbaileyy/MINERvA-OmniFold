#!/bin/bash
# Stage F rebuild phase 1, cluster part (SPEC §2–§7): step A, the step-B equivalence, step C and the cluster
# figures of step D. Login node, root_6_28, 0 node-h. Fig. 1 is drawn separately (SPEC §6 environment control).
#   bash run_rebuild.sh <NS>
# <NS>/a1 = `git archive 40e1265d` (spec freeze), <NS>/a2 = `git archive 01f70c37` (step B). Writes only under <NS>.
# No `set -u`: it aborts the root_6_28 activation.
set -o pipefail
NS=${1:?namespace}
A1=$NS/a1; A2=$NS/a2
C=/global/cfs/cdirs/m3246/josephrb
R=/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding
V=/pscratch/sd/j/josephrb/2d-closeout-c04repair-20261012/build
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate $HOME/.conda/envs/root_6_28
export TMPDIR=$NS/tmp MPLCONFIGDIR=$NS/tmp/mpl XDG_CACHE_HOME=$NS/tmp/xdg
mkdir -p "$TMPDIR" "$MPLCONFIGDIR" "$XDG_CACHE_HOME" "$NS/logs"
RUN=$NS/RUN.txt
: > "$RUN"
echo "archive a1 $(cat $A1/.commit) ; archive a2 $(cat $A2/.commit)" >> "$RUN"
python3 -c "import sys, matplotlib, numpy; print('python', sys.version.split()[0], 'matplotlib', matplotlib.__version__, 'numpy', numpy.__version__)" >> "$RUN"

# run <archive> <script relative to archive> <log> args...   (SPEC §1 invocation; records argv and exit code)
run() {
  local A=$1 S=$2 LOG=$3; shift 3
  python3 -I -B -c "import sys, runpy; A = sys.argv[1]; S = A + '/' + sys.argv[2]; sys.path[:0] = [A + '/2d-unfolding/uq', A + '/2d-unfolding', A]; print('sys.path', sys.path[:3]); sys.argv = [S] + sys.argv[3:]; runpy.run_path(S, run_name='__main__')" "$A" "$S" "$@" > "$LOG" 2>&1
  local rc=$?
  echo "rc=$rc  $(basename $A)  $S  $*  > $(basename $LOG)" >> "$RUN"
  return $rc
}

ST=$A1/docs/orchestration/state/2d-closeout
OUTA=$NS/outA
# ---- step A (archive 1)
run "$A1" docs/orchestration/state/2d-closeout/stageF/rebuild/scripts/build_q_products.py "$NS/logs/stepA.log" \
  --repo "$A1" \
  --s5-npz "$C/2d-closeout-stageC-production-20261015/results/s5/production_cov.npz" \
  --s5-root "$C/2d-closeout-stageC-production-20261015/results/s5/uq_production_covariance.root" \
  --s5-json "$ST/stageC/production/evidence/production/results/s5.json" \
  --playlist-npz "$C/2d-closeout-playlist-term-20261016/playlist_term.npz" \
  --q-npz "$C/2d-closeout-playlist-combination-20261017/s5_plus_playlist.npz" \
  --combination-json "$ST/playlist-term/outputs/combination/combination.json" \
  --eu "$R/uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root" \
  --ec "$R/2d_crossSection_omnifold_MEFHC_5iter.root" \
  --paper-anc "$R/minerva_paper_anc/cov_ptpl_minerva_inclusive_6GeV.root" \
  --vl175-rollup "$V/uq_universe_covariance_c04x01.root" \
  --vl175-boot "$R/uq/bootstrap_MEFHC_300_vl170/uq_covariance_boot300.root" \
  --vl175-ml "$R/uq/seedscan_lgbm_ml/uq_covariance_ml.root" \
  --vl175-blocks "$ST/c04-repair/products/cov2d_blocks_205.npz" \
  --vl175-budget "$ST/c04-repair/products/budget.json" \
  --vl175-group-medians "$ST/stageB/diagnostics/c04-grouped/group_medians.json" \
  --outdir "$OUTA" || { echo "STEP A FAILED"; tail -3 "$NS/logs/stepA.log"; exit 2; }

CV=$R/uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root
EC=$R/2d_crossSection_omnifold_MEFHC_5iter.root
ADOPTED=$R/uq/universe_stage2_MEFHC_full_matcorr_fluxfix_vl170/uq_universe_covariance_full_matcorr_fluxfix.root
BOOT=$R/uq/bootstrap_MEFHC_300_vl170/uq_covariance_boot300.root
ML=$R/uq/seedscan_lgbm_ml/uq_covariance_ml.root
PAPER=$R/minerva_paper_anc/cov_ptpl_minerva_inclusive_6GeV.root
REPAIRED=$V/uq_universe_covariance_c04x01.root
CONTROL=$V/uq_universe_covariance_control.root
CMP=2d-unfolding/compare_to_paper_fullcov.py
F67=2d-unfolding/uq/plot_uncertainty_fig6_7_style.py

# ---- step B equivalence: archive 1 (unpatched) vs archive 2 (patched), VL175 run_repair.sh invocations
for arch in a1 a2; do
  A=$NS/$arch; mkdir -p "$NS/eq/$arch"
  for tag in adopted control repaired; do
    case $tag in adopted) U=$ADOPTED;; control) U=$CONTROL;; repaired) U=$REPAIRED;; esac
    for mode in std lognormal substat; do
      extra=(); [ $mode = lognormal ] && extra=(--log-normal); [ $mode = substat ] && extra=(--subtract-stat)
      run "$A" $CMP "$NS/eq/$arch/${tag}_${mode}.txt" --ours "$CV" --out-prefix "$NS/eq/$arch/${tag}_${mode}" \
        --omnifold-cov "$U:hCov_combined" --omnifold-cov "$ML:hCov2D_reported" "${extra[@]}"
    done
  done
  run "$A" $F67 "$NS/eq/$arch/f67_control.log" --xsec-root "$EC" --universe-root "$ADOPTED" --bootstrap-root "$BOOT" \
    --ml-root "$ML" --paper-root "$PAPER" --out-prefix "$NS/eq/$arch/control_EC_adopted"
  run "$A" $F67 "$NS/eq/$arch/f67_EU_adopted.log" --xsec-root "$CV" --universe-root "$ADOPTED" --bootstrap-root "$BOOT" \
    --ml-root "$ML" --paper-root "$PAPER" --out-prefix "$NS/eq/$arch/EU_adopted"
  run "$A" $F67 "$NS/eq/$arch/f67_EU_repaired.log" --xsec-root "$CV" --universe-root "$REPAIRED" --bootstrap-root "$BOOT" \
    --ml-root "$ML" --paper-root "$PAPER" --out-prefix "$NS/eq/$arch/EU_repaired"
done

# ---- step C (archive 2): chi2 with Q, and the ours-only chi2
mkdir -p "$NS/chi2"
for mode in std lognormal substat; do
  extra=(); [ $mode = lognormal ] && extra=(--log-normal); [ $mode = substat ] && extra=(--subtract-stat)
  run "$A2" $CMP "$NS/chi2/chi2_Q_${mode}.txt" --ours "$CV" --out-prefix "$NS/chi2/chi2_Q_${mode}" \
    --omnifold-cov "$OUTA/uq_adopted_covariance.root:hCov_Q" "${extra[@]}"
done
OO=2d-unfolding/uq/_ours_only_chi2.py
run "$A2" $OO "$NS/chi2/ours_only_universe.txt" --ours "$CV" --universe-cov "$OUTA/uq_adopted_covariance.root" --universe-hist hCov_universe_total
run "$A2" $OO "$NS/chi2/ours_only_universe_plus_stat.txt" --ours "$CV" --universe-cov "$OUTA/uq_adopted_covariance.root" --universe-hist hCov_universe_total --bootstrap-cov "$OUTA/block_stat.root"
run "$A2" $OO "$NS/chi2/ours_only_Q.txt" --ours "$CV" --universe-cov "$OUTA/uq_adopted_covariance.root" --universe-hist hCov_Q

# ---- step D, cluster figures (archive 2)
mkdir -p "$NS/fig67" "$NS/stat"
run "$A2" $F67 "$NS/logs/fig67_Q.log" --xsec-root "$CV" --universe-root "$OUTA/uq_adopted_covariance.root" \
  --bootstrap-root "$OUTA/block_stat.root" --ml-root "$OUTA/block_c08.root" --include-ml always --ml-label "Training seed" \
  --extra-block "$OUTA/block_playlist.root:hCov2D_reported:Run period" --paper-root "$PAPER" \
  --out-prefix "$NS/fig67/MEFHC_fig6_7_uncertainty" --projections-json "$NS/fig67/fig67_projections.json"
run "$A2" 2d-unfolding/uq/plot_bootstrap_figs.py "$NS/logs/stat_figs.log" --cov "$OUTA/block_stat.root" --outdir "$NS/stat"
echo "RUN COMPLETE" >> "$RUN"
echo "RUN COMPLETE"
