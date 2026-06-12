#!/bin/bash
#SBATCH --job-name=uthfps_blk
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=16 --mem=64G --time=04:00:00
#SBATCH --array=0-5
#SBATCH --output=uq_fps/uthrow_slabs_fps/blk_%A_%a.out
#SBATCH --error=uq_fps/uthrow_slabs_fps/blk_%A_%a.err

# FPS block-sum units from the SAME bank (apples-to-apples comparison object for the
# unified throw): 6 tasks x (2 knobs + 2 flux) = 12 knobs + 12 flux. Mirrors 4D.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"; mkdir -p uq_fps/uthrow_slabs_fps
T=${SLURM_ARRAY_TASK_ID}
KNOBS=("2p2h,CCQEPauliSupViaKF" "FrAbs_pi,FrElas_N" "HighQ2,LowQ2" "MaCCQE,MaRES" "MFP_N,MvRES" "Rvn2pi,Rvp2pi")
FLUX=("0-1" "2-3" "4-5" "6-7" "8-9" "10-11")
[[ -s "uq_fps/uthrow_slabs_fps/blockfps_${T}.npz" ]] && { echo "skip (exists)"; exit 0; }
echo "[blkfps] task=$T knobs=${KNOBS[$T]} flux=${FLUX[$T]} $(date -u '+%F %T UTC')"
python3 unified_throw_cov.py --blockunits --bank bank_uthrow_fps --iters 5 --seed 1000 \
    --block-knobs "${KNOBS[$T]}" --block-flux "${FLUX[$T]}" \
    --out "uq_fps/uthrow_slabs_fps/blockfps_${T}.npz"
echo "[blkfps] task=$T done $(date -u '+%F %T UTC')"
