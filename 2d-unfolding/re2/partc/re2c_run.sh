#!/bin/bash
# RE-2 part C, on a Perlmutter login node (no Slurm), from a clean deploy of the bound commit (RE2-DECLARATION-C.md §4):
#     bash re2c_run.sh purity  <deploy> <outdir>    the K1-roll: every copy and producer on the purity inputs; then
#                                                   re2c_k1roll.py compares each output with its committed original
#     bash re2c_run.sh refined <deploy> <outdir>    the refined chain on part B's products, in the same order
# Each step's argv, exit status and wall time go to <outdir>/logs/steps.tsv, and any nonzero exit stops the run. In
# the refined arm each product's sha256 is the next step's pin (chain.json: chain of custody). <outdir> must not
# exist. The purity arm reads no refined product (RE2-DECLARATION-C.md §4.1: the opened-file list is recorded with
# strace by the caller). No `set -u`: it aborts the root_6_28 activation.
set -o pipefail
ARM=$1; D=$(cd "$2" && pwd); O=$3
case "$ARM" in purity|refined) ;; *) echo "arm: purity or refined"; exit 2;; esac
[ ! -e "$O" ] || { echo "$O exists"; exit 2; }
[ -z "$(git -C "$D" status --porcelain)" ] || { echo "deploy $D is not clean"; exit 2; }
P=$D/2d-unfolding/re2/partc
ST=$D/docs/orchestration/state/2d-closeout
A=/pscratch/sd/j/josephrb/MINERvA-OmniFold
R2D=$A/2d-unfolding
B=/pscratch/sd/j/josephrb/2d-closeout-re2-20261023
EU=$R2D/uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root
ER=$B/partb/out/ER/xsec.root
EC=$R2D/2d_crossSection_omnifold_MEFHC_5iter.root
ANC=$R2D/minerva_paper_anc/cov_ptpl_minerva_inclusive_6GeV.root
V=/pscratch/sd/j/josephrb/2d-closeout-c04repair-20261012/build
CFSC=/global/cfs/cdirs/m3246/josephrb
RB=$CFSC/2d-closeout-stageF-rebuild-20261018
P3=/pscratch/sd/j/josephrb/methods-paper/re1-20261022/out/f/new/xsec_3d_p3.root
PU_PURITY=/pscratch/sd/j/josephrb/2d-closeout-period-unfold-20261014/out
mkdir -p "$O"/{logs,tmp,mpl,results,s5,work_cov,periods,periods_ns/tmp,chi2,fig67,stat,receipts/figs,figs,threeD}
source "$A/setup_salloc_env.sh" > /dev/null 2>&1
export TMPDIR=$O/tmp MPLCONFIGDIR=$O/mpl XDG_CACHE_HOME=$O/tmp PYTHONDONTWRITEBYTECODE=1 MNV_REPO=$A
STEPS=$O/logs/steps.tsv
printf 'step\trc\tseconds\tcwd\targv\n' > "$STEPS"
echo "arm=$ARM deploy=$D head=$(git -C "$D" rev-parse HEAD) host=$(hostname) start=$(date -u +%FT%TZ)" > "$O/logs/run.txt"

# step <name> <cwd> <stdout file> <script> args...: the run_rebuild.sh invocation (python -I, the deploy's
# 2d-unfolding/uq, 2d-unfolding and root on sys.path), with its argv, status and time recorded; a failure stops.
step() {
    local name=$1 cwd=$2 out=$3 script=$4 t0 rc; shift 4
    t0=$(date +%s)
    (cd "$cwd" && python3 -I -B -c "import sys, runpy; D, S = sys.argv[1], sys.argv[2]; \
sys.path[:0] = [D + '/2d-unfolding/uq', D + '/2d-unfolding', D]; sys.argv = [S] + sys.argv[3:]; \
runpy.run_path(S, run_name='__main__')" "$D" "$script" "$@") > "$out" 2>&1
    rc=$?
    printf '%s\t%s\t%s\t%s\t%s\n' "$name" "$rc" "$(( $(date +%s) - t0 ))" "$cwd" "$script $*" >> "$STEPS"
    [ "$rc" = 0 ] || { echo "STEP $name rc=$rc (see $out)"; exit 10; }
}
sha() { sha256sum "$1" | cut -d' ' -f1; }
L=$O/logs

if [ "$ARM" = purity ]; then
    # ---- C0, the K1-roll (RE2-DECLARATION-C.md §4.1): the copies on the purity inputs
    for item in c0 s3 s4ii s1 s2 s4i; do
        step "analyze_$item" "$O" "$L/analyze_$item.log" "$P/re2c_analyze.py" "$item" "$O/results/$item.json"
    done
    step rollup "$O" "$L/rollup.log" "$P/re2c_rollup.py" --out "$O/s5" --results "$O/results"
    step export_cov "$O" "$L/export_cov.log" "$P/re2c_export_cov.py" "$O/work_cov/work_cov.npz" \
        "$O/work_cov/cov_controls.json"
    step periods_selftest "$O" "$L/periods_selftest.log" "$P/re2c_analyze_periods.py" --ns "$O/periods_ns" \
        selftest "$O/periods/selftest.json"
    step periods_control "$O" "$L/periods_control.log" "$P/re2c_analyze_periods.py" control "$PU_PURITY" \
        "$O/periods/control.json"
    step periods_roles "$O" "$L/periods_roles.log" "$P/re2c_analyze_periods.py" roles "$PU_PURITY" \
        "$O/periods/roles.json"
    step periods_analyze "$O" "$L/periods_analyze.log" "$P/re2c_analyze_periods.py" analyze "$O/periods/roles.json" \
        "$O/periods/analysis.json" "$O/periods/analysis.txt"
    step playlist "$O" "$L/playlist.log" "$P/re2c_playlist_term.py" "$O/periods/analysis.json" "$O/playlist"
    step combine "$O" "$L/combine.log" "$P/re2c_combine.py" "$O/periods/analysis.json" \
        "$O/playlist/playlist_term.npz" "$O/s5/production_cov.npz" "$O/combination"
    # build_q on run_rebuild.sh's own inputs (the committed S5 json and the CFS products it pinned)
    step build_q "$O" "$L/build_q.log" "$P/re2c_build_q.py" --repo "$D" \
        --s5-npz "$CFSC/2d-closeout-stageC-production-20261015/results/s5/production_cov.npz" \
        --s5-root "$CFSC/2d-closeout-stageC-production-20261015/results/s5/uq_production_covariance.root" \
        --s5-json "$ST/stageC/production/evidence/production/results/s5.json" \
        --playlist-npz "$CFSC/2d-closeout-playlist-term-20261016/playlist_term.npz" \
        --q-npz "$CFSC/2d-closeout-playlist-combination-20261017/s5_plus_playlist.npz" \
        --combination-json "$ST/playlist-term/outputs/combination/combination.json" \
        --eu "$EU" --ec "$EC" --paper-anc "$ANC" --vl175-rollup "$V/uq_universe_covariance_c04x01.root" \
        --vl175-boot "$R2D/uq/bootstrap_MEFHC_300_vl170/uq_covariance_boot300.root" \
        --vl175-ml "$R2D/uq/seedscan_lgbm_ml/uq_covariance_ml.root" \
        --vl175-blocks "$ST/c04-repair/products/cov2d_blocks_205.npz" \
        --vl175-budget "$ST/c04-repair/products/budget.json" \
        --vl175-group-medians "$ST/stageB/diagnostics/c04-grouped/group_medians.json" --outdir "$O/outA"
    X=$EU; QROOT=$RB/outA/uq_adopted_covariance.root; QDIR=$RB/outA
else
    # ---- the refined chain (RE2-DECLARATION-C.md §4.2)
    for item in c0 s3 s4ii s1 s4i; do
        step "analyze_$item" "$O" "$L/analyze_$item.log" "$P/re2c_analyze.py" --arm refined "$item" \
            "$O/results/$item.json"
    done
    step rollup "$O" "$L/rollup.log" "$P/re2c_rollup.py" --arm refined --out "$O/s5" --results "$O/results"
    step export_cov "$O" "$L/export_cov.log" "$P/re2c_export_cov.py" "$O/work_cov/work_cov.npz" \
        "$O/work_cov/cov_controls.json" --arm refined
    WC=$O/work_cov/work_cov.npz; WC_SHA=$(sha "$WC")
    PA=(--arm refined --work-cov "$WC" "$WC_SHA" --ns "$O/periods_ns")
    step periods_selftest "$O" "$L/periods_selftest.log" "$P/re2c_analyze_periods.py" "${PA[@]}" \
        selftest "$O/periods/selftest.json"
    step periods_control "$O" "$L/periods_control.log" "$P/re2c_analyze_periods.py" "${PA[@]}" \
        control "$B/partb/out" "$O/periods/control.json"
    step periods_roles "$O" "$L/periods_roles.log" "$P/re2c_analyze_periods.py" "${PA[@]}" \
        roles "$B/partb/out" "$O/periods/roles.json"
    step periods_analyze "$O" "$L/periods_analyze.log" "$P/re2c_analyze_periods.py" "${PA[@]}" \
        analyze "$O/periods/roles.json" "$O/periods/analysis.json" "$O/periods/analysis.txt"
    AN_SHA=$(sha "$O/periods/analysis.json")
    step playlist "$O" "$L/playlist.log" "$P/re2c_playlist_term.py" "$O/periods/analysis.json" "$O/playlist" \
        --arm refined --analysis-sha "$AN_SHA" --work-cov "$WC" "$WC_SHA" --ns "$O/periods_ns"
    PL_SHA=$(sha "$O/playlist/playlist_term.npz"); PLJ_SHA=$(sha "$O/playlist/playlist_term.json")
    S5_SHA=$(sha "$O/s5/production_cov.npz")
    step combine "$O" "$L/combine.log" "$P/re2c_combine.py" "$O/periods/analysis.json" \
        "$O/playlist/playlist_term.npz" "$O/s5/production_cov.npz" "$O/combination" --arm refined \
        --pins "$AN_SHA" "$PL_SHA" "$S5_SHA" --playlist-json "$O/playlist/playlist_term.json" "$PLJ_SHA" \
        --work-cov "$WC" "$WC_SHA" --ns "$O/periods_ns"
    python3 -c "import json, sys; json.dump(dict(zip(sys.argv[2::2], sys.argv[3::2])), open(sys.argv[1], 'w'), indent=1)" \
        "$O/pins_q.json" s5_npz "$S5_SHA" s5_root "$(sha "$O/s5/uq_production_covariance.root")" \
        s5_json "$(sha "$O/s5/s5.json")" playlist_npz "$PL_SHA" q_npz "$(sha "$O/combination/s5_plus_playlist.npz")" \
        combination_json "$(sha "$O/combination/combination.json")"
    step build_q "$O" "$L/build_q.log" "$P/re2c_build_q.py" --repo "$D" --arm refined --pins-json "$O/pins_q.json" \
        --eu-control "$EU" --s5-npz "$O/s5/production_cov.npz" --s5-root "$O/s5/uq_production_covariance.root" \
        --s5-json "$O/s5/s5.json" --playlist-npz "$O/playlist/playlist_term.npz" \
        --q-npz "$O/combination/s5_plus_playlist.npz" --combination-json "$O/combination/combination.json" \
        --eu "$ER" --ec "$EC" --paper-anc "$ANC" --vl175-rollup "$V/uq_universe_covariance_c04x01.root" \
        --vl175-boot "$R2D/uq/bootstrap_MEFHC_300_vl170/uq_covariance_boot300.root" \
        --vl175-ml "$R2D/uq/seedscan_lgbm_ml/uq_covariance_ml.root" \
        --vl175-blocks "$ST/c04-repair/products/cov2d_blocks_205.npz" \
        --vl175-budget "$ST/c04-repair/products/budget.json" \
        --vl175-group-medians "$ST/stageB/diagnostics/c04-grouped/group_medians.json" --outdir "$O/outA"
    X=$ER; QROOT=$O/outA/uq_adopted_covariance.root; QDIR=$O/outA
fi

# ---- run_rebuild.sh steps C and D, on X (E_U or E_R) and its Q
CMP=$D/2d-unfolding/compare_to_paper_fullcov.py
for mode in std lognormal substat; do
    extra=(); [ $mode = lognormal ] && extra=(--log-normal); [ $mode = substat ] && extra=(--subtract-stat)
    step "chi2_$mode" "$R2D" "$O/chi2/chi2_Q_$mode.txt" "$CMP" --ours "$X" --out-prefix "$O/chi2/chi2_Q_$mode" \
        --omnifold-cov "$QROOT:hCov_Q" "${extra[@]}"
done
OO=$D/2d-unfolding/uq/_ours_only_chi2.py
step oo_universe "$R2D" "$O/chi2/ours_only_universe.txt" "$OO" --ours "$X" --universe-cov "$QROOT" \
    --universe-hist hCov_universe_total
step oo_universe_plus_stat "$R2D" "$O/chi2/ours_only_universe_plus_stat.txt" "$OO" --ours "$X" \
    --universe-cov "$QROOT" --universe-hist hCov_universe_total --bootstrap-cov "$QDIR/block_stat.root"
step oo_Q "$R2D" "$O/chi2/ours_only_Q.txt" "$OO" --ours "$X" --universe-cov "$QROOT" --universe-hist hCov_Q
step fig67 "$R2D" "$L/fig67_Q.log" "$D/2d-unfolding/uq/plot_uncertainty_fig6_7_style.py" --xsec-root "$X" \
    --universe-root "$QROOT" --bootstrap-root "$QDIR/block_stat.root" --ml-root "$QDIR/block_c08.root" \
    --include-ml always --ml-label "Training seed" --extra-block "$QDIR/block_playlist.root:hCov2D_reported:Run period" \
    --paper-root "$ANC" --out-prefix "$O/fig67/MEFHC_fig6_7_uncertainty" --projections-json "$O/fig67/fig67_projections.json"
step stat_figs "$R2D" "$L/stat_figs.log" "$D/2d-unfolding/uq/plot_bootstrap_figs.py" --cov "$QDIR/block_stat.root" \
    --outdir "$O/stat"

# ---- the published comparison and the figures that read the central value (P12; make_figures.sh:35-42)
R=$O/receipts
step agreement "$R2D" "$L/agreement.log" "$D/2d-unfolding/agreement_windows_receipt.py" --ours "$X" \
    --out "$R/RECEIPT-agreement-windows.json"
step chi2_paperonly "$R2D" "$R/chi2_paperonly.txt" "$CMP" --ours "$X" --out-prefix "$R/paperonly"
step tune "$R2D" "$R/tune.log" "$D/2d-unfolding/receipt_model_chi2_2d.py" --ours "$X" --out "$R/receipt_model_chi2.json"
step models "$R2D" "$R/figs/models.log" "$D/2d-unfolding/compare_to_models.py" --ours "$X" \
    --out-prefix "$R/figs/model_comp"
step tension "$R2D" "$R/figs/tension.log" "$D/2d-unfolding/diagnose_tension.py" --ours "$X" \
    --out-prefix "$R/figs/tension"
step fig13 "$R2D" "$L/fig13.log" "$D/2d-unfolding/plot_2d_threeway_fig13.py" --infile "$X" --paper "$ANC" \
    --out "$O/figs/MEFHC_5iter_fig13.png"
step paper_slices "$R2D" "$L/paper_slices.log" "$D/2d-unfolding/plot_2d_paper_comparison.py" --infile "$X" \
    --prefix "$O/figs/MEFHC_5iter_xsec_paper"
step xsec_proj "$R2D" "$L/xsec_proj.log" "$D/2d-unfolding/plot_2d_cross_section.py" --infile "$X" \
    --prefix "$O/figs/MEFHC_5iter_xsec"
step pull_full "$R2D" "$L/pull_full.log" "$CMP" --ours "$X" --out-prefix "$O/figs/MEFHC_5iter"

# ---- the numbers against the central value; then, refined only, Fig. 1's reduction, C_model and the table
if [ "$ARM" = purity ]; then
    step numbers "$O" "$L/numbers.log" "$P/re2c_numbers.py" --arm purity --central "$EU" --eu "$EU" --ec "$EC" \
        --p3 "$P3" --out "$O/partc_numbers.json"
    step values "$D" "$L/values.log" "$P/re2c_values.py" --repo "$D" --spec "$P/re2c_values_spec.tsv" \
        --out-tsv "$O/values_table.tsv" --out-json "$O/values_table.json"
    step k1roll "$D" "$L/k1roll.log" "$P/re2c_k1roll.py" --repo "$D" --dry "$O" --out "$O/k1roll.json"
else
    Q2=$O/outA/cov2d_Q_205.npz; Q2_SHA=$(sha "$Q2")
    step reduce "$O" "$L/reduce.log" "$P/re2c_reduce.py" --ec "$EC" --eu "$EU" --er "$ER" \
        --remote-reduce "$ST/../next-preparation-20261009/two-d-path/operands/remote_reduce.json" --out "$O/reduce.json"
    step numbers "$O" "$L/numbers.log" "$P/re2c_numbers.py" --arm refined --central "$ER" --eu "$EU" --ec "$EC" \
        --p3 "$P3" --q-npz "$Q2" --q-sha "$Q2_SHA" --out "$O/partc_numbers.json"
    mkdir -p "$O/cmodel"
    step cmodel "$O" "$L/cmodel.log" "$P/re2c_cmodel.py" --cmodel-json "$D/2d-unfolding/pv2d/cmodel/cmodel_2d.json" \
        --q-purity "$RB/outA/cov2d_Q_205.npz" --q-refined "$Q2" --q-refined-sha "$Q2_SHA" \
        --area-npz "$O/s5/production_cov.npz" --area-npz-sha "$S5_SHA" --out-npz "$O/cmodel/cmodel_R.npz" \
        --out-json "$O/cmodel/cmodel_R.json"
    step values "$D" "$L/values.log" "$P/re2c_values.py" --repo "$D" --spec "$P/re2c_values_spec.tsv" \
        --refined-dir "$O" --out-tsv "$O/values_table.tsv" --out-json "$O/values_table.json"
    python3 -c "import json, sys; json.dump(dict(zip(sys.argv[2::2], sys.argv[3::2])), open(sys.argv[1], 'w'), indent=1)" \
        "$O/chain.json" work_cov "$WC_SHA" analysis_json "$AN_SHA" playlist_npz "$PL_SHA" playlist_json "$PLJ_SHA" \
        production_cov "$S5_SHA" cov2d_Q_205 "$Q2_SHA" s5_plus_playlist "$(sha "$O/combination/s5_plus_playlist.npz")"
fi
echo "end=$(date -u +%FT%TZ)" >> "$O/logs/run.txt"
(cd "$O" && find . -type f ! -path './tmp/*' ! -path './mpl/*' ! -name SHA256SUMS -print0 | LC_ALL=C sort -z \
    | xargs -0 sha256sum) > "$O/SHA256SUMS"
echo "RUN COMPLETE ($ARM)"
