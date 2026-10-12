#!/bin/bash
# C04+X01 repaired 2D covariance: build, then the committed producers on the repaired and adopted files.
# Login node (saul). Grant AUTHORIZATION-20261012-2d-closeout-fluxrepair.md; no Slurm.
#   bash run_repair.sh <namespace>
# <namespace>/repo   = `git archive 09c8bae0` of the repo (producers run from here, not the shared checkout)
# <namespace>/inputs = the committed export cov2d_blocks_205.npz (control operand)
# No `set -u`: it aborts the root_6_28 activation (ADDR2LINE unbound).
set -eo pipefail
NS=${1:?namespace}
R=/pscratch/sd/j/josephrb/MINERvA-OmniFold
D=$R/2d-unfolding
REPO=$NS/repo
B=$NS/build
L=$NS/logs
mkdir -p "$B" "$L" "$NS/chi2" "$NS/fig67"
source $R/setup_salloc_env.sh >/dev/null 2>&1
export TMPDIR=$NS/tmp; mkdir -p "$TMPDIR"
export PYTHONDONTWRITEBYTECODE=1

python3 "$NS/scripts/build_repair.py" --out "$B" --repo "$REPO" --committed-export "$NS/inputs/cov2d_blocks_205.npz" \
    > "$L/build.log" 2>&1 || { echo "BUILD FAILED rc=$?"; tail -5 "$L/build.log"; exit 2; }

CV=$D/uq/2d_xsec_MEFHC_5iter_lgbm_uni_full_CV.root
EC=$D/2d_crossSection_omnifold_MEFHC_5iter.root
ADOPTED=$D/uq/universe_stage2_MEFHC_full_matcorr_fluxfix_vl170/uq_universe_covariance_full_matcorr_fluxfix.root
BOOT=$D/uq/bootstrap_MEFHC_300_vl170/uq_covariance_boot300.root
ML=$D/uq/seedscan_lgbm_ml/uq_covariance_ml.root
PAPER=$D/minerva_paper_anc/cov_ptpl_minerva_inclusive_6GeV.root
REPAIRED=$B/uq_universe_covariance_c04x01.root
CONTROL=$B/uq_universe_covariance_control.root

cd "$REPO/2d-unfolding"
for tag in adopted control repaired; do
  case $tag in adopted) U=$ADOPTED;; control) U=$CONTROL;; repaired) U=$REPAIRED;; esac
  for mode in std lognormal substat; do
    extra=""; [ $mode = lognormal ] && extra="--log-normal"; [ $mode = substat ] && extra="--subtract-stat"
    python3 compare_to_paper_fullcov.py --ours "$CV" --out-prefix "$NS/chi2/${tag}_${mode}" \
        --omnifold-cov "$U:hCov_combined" --omnifold-cov "$ML:hCov2D_reported" $extra \
        > "$NS/chi2/${tag}_${mode}.txt" 2>&1
  done
done

cd "$REPO/2d-unfolding/uq"
# control: the VL172 invocation (exact-split central E_C), then E_U adopted, then E_U repaired
python3 plot_uncertainty_fig6_7_style.py --xsec-root "$EC" --universe-root "$ADOPTED" --bootstrap-root "$BOOT" \
    --ml-root "$ML" --paper-root "$PAPER" --out-prefix "$NS/fig67/control_EC_adopted" > "$L/fig67_control.log" 2>&1
python3 plot_uncertainty_fig6_7_style.py --xsec-root "$CV" --universe-root "$ADOPTED" --bootstrap-root "$BOOT" \
    --ml-root "$ML" --paper-root "$PAPER" --out-prefix "$NS/fig67/EU_adopted" > "$L/fig67_EU_adopted.log" 2>&1
python3 plot_uncertainty_fig6_7_style.py --xsec-root "$CV" --universe-root "$REPAIRED" --bootstrap-root "$BOOT" \
    --ml-root "$ML" --paper-root "$PAPER" --out-prefix "$NS/fig67/EU_repaired" > "$L/fig67_EU_repaired.log" 2>&1
echo "RUN COMPLETE"
