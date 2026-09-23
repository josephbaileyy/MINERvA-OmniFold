#!/bin/bash
#SBATCH --job-name=eavscale
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=96G
#SBATCH --time=06:00:00
#SBATCH --array=0-11
#SBATCH --output=/pscratch/sd/j/josephrb/eavail_scale_20260923/logs/eavscale_%A_%a.out
#SBATCH --error=/pscratch/sd/j/josephrb/eavail_scale_20260923/logs/eavscale_%A_%a.err

# KNOWN_ISSUES #26 / OI-31 sensitivity study. Plan (predeclared, committed before submission):
# docs/orchestration/PLAN-20260923-issue26-issue5-studies.md. Each task runs the UNMODIFIED
# production driver through nd-unfolding/eavail_scale_study.py, which multiplies reco E_avail by
# r = k/1.17 (MC: signal+background; data) after reading. Outputs are NONQUOTABLE diagnostics.
#
# Paths are ABSOLUTE on purpose: sbatch executes a COPY of this script, so BASH_SOURCE/$0 do not
# name the checkout. WT is the dedicated study worktree; DATA is the canonical tree that holds the
# (untracked) input ROOT files, read-only here.
set -eo pipefail
WT=/pscratch/sd/j/josephrb/MINERvA-OmniFold-eavailscale-20260923
DATA=/pscratch/sd/j/josephrb/MINERvA-OmniFold
OUT=/pscratch/sd/j/josephrb/eavail_scale_20260923
K1=0.8547008547008547   # 1.00/1.17 : the no-calibration extreme

source "${DATA}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-32}
export OPENBLAS_NUM_THREADS=${OMP_NUM_THREADS}

OMNI3D="${DATA}/3d-unfolding/runEventLoopOmniFold_MEFHC_3D.root"
OMNI5D="${DATA}/nd-unfolding/runEventLoopOmniFold_5D_MEFHC.root"
FLUX_MC="${DATA}/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root"

case "${SLURM_ARRAY_TASK_ID}" in
  0)  TAG=c3_ctrl;  DRV=3d; RMC=1;   RDATA=1 ;;
  1)  TAG=c3_rep;   DRV=3d; RMC=1;   RDATA=1 ;;
  2)  TAG=c3_k100;  DRV=3d; RMC=$K1; RDATA=$K1 ;;
  3)  TAG=c3_m10;   DRV=3d; RMC=0.9; RDATA=0.9 ;;
  4)  TAG=c3_p10;   DRV=3d; RMC=1.1; RDATA=1.1 ;;
  5)  TAG=c3_pow;   DRV=3d; RMC=1;   RDATA=$K1 ;;
  6)  TAG=c5_ctrl;  DRV=nd; RMC=1;   RDATA=1 ;;
  7)  TAG=c5_rep;   DRV=nd; RMC=1;   RDATA=1 ;;
  8)  TAG=c5_k100;  DRV=nd; RMC=$K1; RDATA=$K1 ;;
  9)  TAG=c5_m10;   DRV=nd; RMC=0.9; RDATA=0.9 ;;
  10) TAG=c5_p10;   DRV=nd; RMC=1.1; RDATA=1.1 ;;
  11) TAG=c5_pow;   DRV=nd; RMC=1;   RDATA=$K1 ;;
  *) echo "[sbatch] no task ${SLURM_ARRAY_TASK_ID}" >&2; exit 2 ;;
esac

ROOT_OUT="${OUT}/NONQUOTABLE-DIAGNOSTIC.eavscale.${TAG}.root"
LOG_OUT="${OUT}/NONQUOTABLE-DIAGNOSTIC.eavscale.${TAG}.json"
if [[ "${DRV}" == 3d ]]; then
  DARGS=(--omnifile "${OMNI3D}" --mcfile "${FLUX_MC}" --iters 5 --use-weights
         --estimator lgbm --seed 1 --out "${ROOT_OUT}" --verbose)
else
  DARGS=(--omnifile "${OMNI5D}" --mcfile "${FLUX_MC}" --axes eavail,q3,W --iters 5
         --use-weights --estimator lgbm --seed 42 --out "${ROOT_OUT}" --verbose)
fi

echo "[sbatch] task=${SLURM_ARRAY_TASK_ID} tag=${TAG} job=${SLURM_JOB_ID} node=$(hostname) start=$(date -u '+%F %T UTC')"
echo "[sbatch] worktree HEAD=$(git -C "${WT}" rev-parse HEAD)"
cd "${WT}/nd-unfolding"
# OI-136: refuse any import from a checkout other than the study checkout (the canonical tree is
# DATA only). The guard's resolved-origin inventory is kept beside the output.
python3 "${WT}/nd-unfolding/mnv_guarded_run.py" --expect-root "${WT}" \
    --inventory "${OUT}/NONQUOTABLE-DIAGNOSTIC.eavscale.${TAG}.oi136-inventory.jsonl" \
    --label "eavscale-${TAG}" -- \
  "${WT}/nd-unfolding/eavail_scale_study.py" --driver "${DRV}" \
    --scale-mc "${RMC}" --scale-data "${RDATA}" --log "${LOG_OUT}" -- "${DARGS[@]}"
sha256sum "${ROOT_OUT}" "${LOG_OUT}"
echo "[sbatch] done=$(date -u '+%F %T UTC')"
