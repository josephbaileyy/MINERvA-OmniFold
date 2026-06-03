#!/bin/bash
#SBATCH --job-name=unfold3d_seedscan
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=128
#SBATCH --time=01:00:00
#SBATCH --array=1-10
#SBATCH --output=unfold3d_seedscan_%a_%A.out
#SBATCH --error=unfold3d_seedscan_%a_%A.err

# ML-stochasticity (C_ML) seedscan for the 3D campaign. Each array task is a CV
# unfold of the 3D CV omnifile with a DIFFERENT GBDT random seed (--seed N),
# identical data/MC/weights otherwise (no --universe, no --bootstrap-seed). The
# spread across the 10 trials is the OmniFold GBDT stochasticity covariance,
# block-summed into the budget as the third term C_syst + C_stat + C_ML.
#
# Mirrors the 2D seedscan_lgbm/run_seedscan_lgbm_interactive.sh, but as an sbatch
# array (no interactive alloc needed). The CV omnifile (2.84 GB) makes each trial
# fast (~15-20 min at 128 threads), well within the 1 h limit.
#
# Output: seedscan_3d/3d_xsec_MEFHC_5iter_lgbm_seed<N>.root
# C_ML:   python uq_3d/build_bootstrap_cov_3d.py --label ml3d \
#             --replicas 'seedscan_3d/3d_xsec_*_seed*.root' --out-root uq_cov_ml_3d.root
# NOTE: seed=1 is the canonical CV (xsec_3d_MEFHC_5iter_lgbm.root was --seed 1),
#       so trial seed1 reproduces it; the cov is the mean-centered spread over all 10.

set -eo pipefail
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-128}

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
D3="${REPO}/3d-unfolding"
OMNIFILE="${D3}/runEventLoopOmniFold_MEFHC_3D.root"          # CV omnifile (not universes)
FLUX_MC="${REPO}/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root"
OUTDIR="${D3}/seedscan_3d"
SEED="${SLURM_ARRAY_TASK_ID}"
OUT="${OUTDIR}/3d_xsec_MEFHC_5iter_lgbm_seed${SEED}.root"

if [[ ! -s "${OMNIFILE}" ]]; then
  echo "[sbatch] FAIL: CV omnifile ${OMNIFILE} missing/empty." >&2
  exit 2
fi
if [[ -s "${OUT}" ]]; then
  echo "[sbatch] SKIP: ${OUT} already on disk"
  exit 0
fi

source "${REPO}/setup_salloc_env.sh"
mkdir -p "${OUTDIR}"
cd "${D3}"

echo "[sbatch] node=$(hostname) jobid=${SLURM_JOB_ID} seed=${SEED}"
echo "[sbatch] OMP_NUM_THREADS=${OMP_NUM_THREADS}"
echo "[sbatch] start: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "[sbatch] out: ${OUT}"

python unfold_3d_omnifold_unbinned.py \
  --omnifile  "${OMNIFILE}" \
  --mcfile    "${FLUX_MC}" \
  --iters     5 \
  --use-weights \
  --estimator lgbm \
  --seed      "${SEED}" \
  --out       "${OUT}"

echo "[sbatch] done: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
