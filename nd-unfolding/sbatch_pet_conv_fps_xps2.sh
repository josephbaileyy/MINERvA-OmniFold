#!/bin/bash
#SBATCH --job-name=pet_conv_fps_xps2
#SBATCH --account=m3246
#SBATCH --constraint=gpu
#SBATCH --qos=regular
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=4
#SBATCH --gpus-per-node=4
#SBATCH --cpus-per-task=32
#SBATCH --gpu-bind=none
#SBATCH --time=04:00:00
#SBATCH --array=0-5
#SBATCH --output=pet_conv_fps_xps2_%A_%a.out
#SBATCH --error=pet_conv_fps_xps2_%A_%a.err
# Step 4 (Tier-2 retraining-response, b-lite / CONVERGENCE-CURVE check only -- NOT a
# per-universe PET covariance; see HANDOFF_fps_step3/HANDOFF.md 2026-07-06 scope
# correction). 6 seed replicas of PET training on random GLOBAL subsamples of the xps2
# full-stats point cloud (4 at 10M events, 2 at 5M events), same NITER=5/EPOCHS=8 recipe
# as the xps2 headline train (products/pet/pet_weights_fps_xps2.npz), varying only
# --seed (drives the --max-events subsample draw; network init/dropout/shuffle are
# already TF-unseeded) and --max-events. Submitted as ONE job array so all 6 tasks share
# a single queue-wait episode instead of paying it per job.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
export ROOT628_PREFIX=/global/homes/j/josephrb/.conda/envs/root_6_28
source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"
module load tensorflow/2.15.0

SEEDS=(101 102 103 104 201 202)
EVENTS=(10000000 10000000 10000000 10000000 5000000 5000000)
TAGS=(10M_s101 10M_s102 10M_s103 10M_s104 5M_s201 5M_s202)

i=${SLURM_ARRAY_TASK_ID}
SEED=${SEEDS[$i]}
NEVT=${EVENTS[$i]}
TAG=${TAGS[$i]}
OUT="products/pet/pet_weights_fps_xps2_conv_${TAG}.npz"

[[ -s "${OUT}" ]] && { echo "[conv] task ${i}: skip (exists) ${OUT}"; exit 0; }

echo "[conv] task ${i}: seed=${SEED} max-events=${NEVT} -> ${OUT}  $(date -u '+%F %T UTC')"
srun -u python3 pet/minerva_pet_dataloader.py --inputs of_inputs_pc_fps_xps2.npz \
    --mode pointcloud --model pet --niter 5 --epochs 8 --max-events "${NEVT}" \
    --seed "${SEED}" --reweight-all --smoke --save-weights "${OUT}" \
    --memmap-dir of_inputs_pc_fps_xps2_npy
echo "[conv] task ${i} done -> ${OUT}  $(date -u '+%F %T UTC')"
