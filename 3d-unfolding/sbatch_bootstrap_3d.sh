#!/bin/bash
#SBATCH --job-name=unfold3d_boot
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=128
#SBATCH --time=01:00:00
#SBATCH --array=1-100%20
#SBATCH --output=uq_3d/boot3d_%a_%A.out
#SBATCH --error=uq_3d/boot3d_%a_%A.err

# 3D OmniFold MEFHC 5-iter Poisson-weight bootstrap (statistical-uncertainty
# band for the 3D result). Per replica: full 3D unfold with --bootstrap-seed N,
# ML random_state pinned via --seed 1 so the spread is pure Poisson (data+MC
# stat); ML-stochasticity is a separate (small) component, not double-counted
# here. Mirrors the validated 2D bootstrap campaign.
# Output: uq_3d/xsec_3d_boot${N}.root ; covariance: build_bootstrap_band_3d.py
set -eo pipefail
export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-128}

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
D3="${REPO}/3d-unfolding"
SEED=${SLURM_ARRAY_TASK_ID}
OUT="${D3}/uq_3d/xsec_3d_boot${SEED}.root"

source "${REPO}/setup_salloc_env.sh"
mkdir -p "${D3}/uq_3d"
cd "${D3}"
echo "[boot3d] node=$(hostname) task=${SEED} start=$(date -u '+%F %T UTC')"

python unfold_3d_omnifold_unbinned.py \
  --omnifile  "${D3}/runEventLoopOmniFold_MEFHC_3D.root" \
  --mcfile    "${REPO}/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root" \
  --iters 5 --use-weights --estimator lgbm \
  --seed 1 --bootstrap-seed "${SEED}" \
  --out "${OUT}"

echo "[boot3d] task=${SEED} done=$(date -u '+%F %T UTC')"
