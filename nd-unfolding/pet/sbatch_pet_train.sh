#!/bin/bash
#SBATCH --job-name=pet_train
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=gpu --nodes=1 --ntasks=1 --gpus=1 --cpus-per-task=32 --time=06:00:00
#SBATCH --output=pet_train_%j.out --error=pet_train_%j.err
# Real point-cloud PET MultiFold. Trains on a tractable subsample (--max-events) then
# (with --reweight-all) evaluates the FINAL gen model on the FULL 32.8M gen cloud so the
# downstream absolute cross section (sbatch_pet_xsec.sh) uses full statistics.
# Env knobs: NITER, EPOCHS, TRAIN_EVENTS, SAVE_WEIGHTS, CLOSURE=1 (pseudo-data=MC reco),
#            FORCE_PET_REBUILD=1 (archive an existing weights file first).
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; cd "${REPO}/nd-unfolding"

NITER="${NITER:-2}"; EPOCHS="${EPOCHS:-8}"; TRAIN_EVENTS="${TRAIN_EVENTS:-2000000}"
EXTRA=""
if [[ "${CLOSURE:-0}" == "1" ]]; then
  EXTRA="--closure"
  SAVE_WEIGHTS="${SAVE_WEIGHTS:-products/pet/pet_weights_closure.npz}"
fi
SAVE_WEIGHTS="${SAVE_WEIGHTS:-products/pet/pet_weights_full.npz}"

if [[ "${FORCE_PET_REBUILD:-0}" == "1" && -e "${SAVE_WEIGHTS}" ]]; then
  stamp="$(date -u +%Y%m%dT%H%M%SZ)"
  mv -v "${SAVE_WEIGHTS}" "${SAVE_WEIGHTS}.stale_${stamp}"
fi

module load tensorflow/2.15.0
python3 -c "import tensorflow as tf; print('TF',tf.__version__,'GPU',tf.config.list_physical_devices('GPU'))"
echo "[pet] real point-cloud MultiFold (train=${TRAIN_EVENTS}, reweight-all on full stats) ${EXTRA} $(date -u +%T)"
python3 pet/minerva_pet_dataloader.py --inputs of_inputs_pc.npz --mode pointcloud \
    --model pet --niter "${NITER}" --epochs "${EPOCHS}" --max-events "${TRAIN_EVENTS}" \
    --reweight-all --smoke --save-weights "${SAVE_WEIGHTS}" ${EXTRA}
echo "[pet] wrote ${SAVE_WEIGHTS}; done $(date -u +%T)"
