#!/bin/bash
#SBATCH --job-name=ai1est5d
#SBATCH --account=m3246_g
#SBATCH --qos=shared --constraint=gpu --nodes=1 --ntasks=1 --gpus-per-task=1 --cpus-per-task=32 --time=01:30:00
#SBATCH --array=1-12%1
#SBATCH --nice=5000
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=boot_nd_5d_ai1/ai1_%a_%A.out --error=boot_nd_5d_ai1/ai1_%a_%A.err
# AI1 estimator-only scan (backup-slide cross-check): fix data+MC draw (--fixed-data-seed 0),
# vary estimator seed (--seed=TASK) to isolate estimator/training stochasticity; combine ->
# compare sqrt-tr vs the ML-split band (1.493e-39). DEPRIORITIZED (--nice=1e6, %1) so PET's
# C_lateral rebuild (critical-path for the freeze) always schedules ahead. skip-if-exists.
set -eo pipefail
export HOME=/global/homes/j/josephrb
export ROOT628_PREFIX=/global/homes/j/josephrb/.conda/envs/root_6_28
export PYTHONUNBUFFERED=1 OMP_NUM_THREADS=12 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
REPO=/pscratch/sd/j/josephrb/MINERvA-OmniFold; source "$REPO/setup_salloc_env.sh"
cd "$REPO/nd-unfolding"
OUT="boot_nd_5d_ai1/res_ai1_${SLURM_ARRAY_TASK_ID}.npz"
[[ -s "$OUT" ]] && { echo "[ai1] skip ${SLURM_ARRAY_TASK_ID} (exists)"; exit 0; }
echo "[ai1] est-seed=${SLURM_ARRAY_TASK_ID} fixed-data-seed=0 start $(date -u +%T) on $(hostname)"
python3 bootstrap_nd.py --npz of_inputs_5d.npz --seed ${SLURM_ARRAY_TASK_ID} \
  --fixed-data-seed 0 --iters 5 --out "$OUT"
echo "[ai1] done ${SLURM_ARRAY_TASK_ID} $(date -u +%T)"
