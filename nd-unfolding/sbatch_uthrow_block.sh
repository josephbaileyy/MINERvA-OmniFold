#!/bin/bash
#SBATCH --job-name=uthrow_blk
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --array=0-5
#SBATCH --output=uq_4d/uthrow_slabs/blk_%A_%a.out
#SBATCH --error=uq_4d/uthrow_slabs/blk_%A_%a.err

# Block-sum producer, balanced 6 tasks x (2 knobs + 2 flux) = 12 knobs + 12 flux.
# cgroup-limited to 16 cores so LightGBM does NOT oversubscribe (the failure mode of
# unconstrained interactive multi-proc runs). ~4 units/task x ~9 min = ~36 min/task.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
cd "${REPO}/nd-unfolding"
mkdir -p uq_4d/uthrow_slabs
T=${SLURM_ARRAY_TASK_ID}
KNOBS=("2p2h,CCQEPauliSupViaKF" "FrAbs_pi,FrElas_N" "HighQ2,LowQ2" "MaCCQE,MaRES" "MFP_N,MvRES" "Rvn2pi,Rvp2pi")
FLUX=("0-1" "2-3" "4-5" "6-7" "8-9" "10-11")
echo "[blk] task=$T knobs=${KNOBS[$T]} flux=${FLUX[$T]} $(date -u '+%F %T UTC')"
python3 unified_throw_cov.py --blockunits --bank bank_uthrow --iters 5 --seed 1000 \
    --block-knobs "${KNOBS[$T]}" --block-flux "${FLUX[$T]}" \
    --out "uq_4d/uthrow_slabs/blocknode_${T}.npz"
echo "[blk] task=$T done $(date -u '+%F %T UTC')"
