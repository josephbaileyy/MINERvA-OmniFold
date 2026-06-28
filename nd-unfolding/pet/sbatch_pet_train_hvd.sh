#!/bin/bash
#SBATCH --job-name=pet_train_hvd
#SBATCH --account=m3246
#SBATCH --constraint=gpu
#SBATCH --qos=regular
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=4
#SBATCH --gpus-per-node=4
#SBATCH --cpus-per-task=32
#SBATCH --gpu-bind=none
#SBATCH --time=06:00:00
#SBATCH --output=pet_train_hvd_%j.out
#SBATCH --error=pet_train_hvd_%j.err
# 4-GPU horovod PET MultiFold. The vendored omnifold divides steps_per_epoch by hvd.size()
# (omnifold.py:123-124,172,273), so 4 ranks run ~4x faster than the single-GPU
# sbatch_pet_train.sh. minerva_pet_dataloader.py wires size=hvd.size()/rank=hvd.rank() into
# MultiFold and guards reweight-all + save to rank 0. --gpu-bind=none keeps all 4 GPUs visible
# to every rank so omnifold's set_visible_devices(gpus[local_rank]) can pin one GPU per rank.
#
# Env knobs (identical to sbatch_pet_train.sh): NITER, EPOCHS, TRAIN_EVENTS, SAVE_WEIGHTS,
#   CLOSURE=1, FORCE_PET_REBUILD=1.
# Submit example (override --time once the probe sizes the run):
#   sbatch --time=08:00:00 --export=ALL,NITER=5,EPOCHS=8,TRAIN_EVENTS=20000000,\
#     SAVE_WEIGHTS=products/pet/pet_weights_cal20m_hvd.npz pet/sbatch_pet_train_hvd.sh
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; cd "${REPO}/nd-unfolding"

NITER="${NITER:-2}"; EPOCHS="${EPOCHS:-8}"; TRAIN_EVENTS="${TRAIN_EVENTS:-2000000}"
# Memmap dir (npz_to_npy.py output): each rank materializes only its 1/ntasks stride, so the
# full 32.8M cloud fits one 229 GB node. Set MEMMAP_DIR= (empty) to fall back to npz load.
MEMMAP_DIR="${MEMMAP_DIR-of_inputs_pc_npy}"
EXTRA=""
if [[ "${CLOSURE:-0}" == "1" ]]; then
  EXTRA="--closure"
  SAVE_WEIGHTS="${SAVE_WEIGHTS:-products/pet/pet_weights_closure.npz}"
fi
SAVE_WEIGHTS="${SAVE_WEIGHTS:-products/pet/pet_weights_hvd.npz}"

if [[ "${FORCE_PET_REBUILD:-0}" == "1" && -e "${SAVE_WEIGHTS}" ]]; then
  stamp="$(date -u +%Y%m%dT%H%M%SZ)"
  mv -v "${SAVE_WEIGHTS}" "${SAVE_WEIGHTS}.stale_${stamp}"
fi

module load tensorflow/2.15.0
echo "[pet-hvd] $(date -u +%T) niter=${NITER} epochs=${EPOCHS} train=${TRAIN_EVENTS} ranks=${SLURM_NTASKS} (reweight-all on full stats, rank-0 save)"
MEMMAP_ARG=""; [[ -n "${MEMMAP_DIR}" ]] && MEMMAP_ARG="--memmap-dir ${MEMMAP_DIR}"
srun -u python3 pet/minerva_pet_dataloader.py --inputs of_inputs_pc.npz --mode pointcloud \
    --model pet --niter "${NITER}" --epochs "${EPOCHS}" --max-events "${TRAIN_EVENTS}" \
    --reweight-all --smoke --save-weights "${SAVE_WEIGHTS}" ${MEMMAP_ARG} ${EXTRA}
echo "[pet-hvd] wrote ${SAVE_WEIGHTS}; done $(date -u +%T)"
