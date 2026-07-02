#!/bin/bash
#SBATCH --job-name=pet_train_fps
#SBATCH --account=m3246
#SBATCH --constraint=gpu
#SBATCH --qos=regular
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=4
#SBATCH --gpus-per-node=4
#SBATCH --cpus-per-task=32
#SBATCH --gpu-bind=none
#SBATCH --time=10:00:00
#SBATCH --output=pet_train_fps_%j.out
#SBATCH --error=pet_train_fps_%j.err
# FPS headline, step 2c: full-stats 4-GPU horovod PET MultiFold on the cloud-fixed
# FULL-PHASE-SPACE point cloud (of_inputs_pc_fps.npz / of_inputs_pc_fps_npy memmap,
# built by sbatch_npz_pc_fps.sh). Same proven memmap+stride path as the 32.8M
# restricted-PS run (job 55186891, ~7.4h). Reweight-all pushes onto the full FPS
# gen cloud; rank-0 saves products/pet/pet_weights_fps.npz = the headline FPS weights
# that every downstream uncertainty study (3-prior envelope, Tier-2 retraining) builds on.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; cd "${REPO}/nd-unfolding"

NITER="${NITER:-5}"; EPOCHS="${EPOCHS:-8}"; TRAIN_EVENTS="${TRAIN_EVENTS:-40000000}"
INPUTS="${INPUTS:-of_inputs_pc_fps.npz}"
MEMMAP_DIR="${MEMMAP_DIR-of_inputs_pc_fps_npy}"
SAVE_WEIGHTS="${SAVE_WEIGHTS:-products/pet/pet_weights_fps.npz}"

[ -s "${INPUTS}" ] || { echo "[pet-fps] MISSING ${INPUTS}"; exit 1; }

module load tensorflow/2.15.0
echo "[pet-fps] $(date -u +%T) niter=${NITER} epochs=${EPOCHS} train=${TRAIN_EVENTS} ranks=${SLURM_NTASKS} inputs=${INPUTS} (reweight-all full FPS stats, rank-0 save)"
MEMMAP_ARG=""; [[ -n "${MEMMAP_DIR}" ]] && MEMMAP_ARG="--memmap-dir ${MEMMAP_DIR}"
srun -u python3 pet/minerva_pet_dataloader.py --inputs "${INPUTS}" --mode pointcloud \
    --model pet --niter "${NITER}" --epochs "${EPOCHS}" --max-events "${TRAIN_EVENTS}" \
    --reweight-all --smoke --save-weights "${SAVE_WEIGHTS}" ${MEMMAP_ARG}
echo "[pet-fps] wrote ${SAVE_WEIGHTS}; done $(date -u +%T)"
