#!/bin/bash
#SBATCH --job-name=pet_train
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=gpu --nodes=1 --ntasks=1 --gpus=1 --cpus-per-task=32 --time=04:00:00
#SBATCH --output=pet_train_%j.out --error=pet_train_%j.err
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; cd "${REPO}/nd-unfolding"
FORCE_PET_REBUILD="${FORCE_PET_REBUILD:-0}"
if [[ "${FORCE_PET_REBUILD}" == "1" && -e pet_weights.npz ]]; then
  stamp="$(date -u +%Y%m%dT%H%M%SZ)"
  mv -v pet_weights.npz "pet_weights.npz.stale_${stamp}"
fi
module load tensorflow/2.15.0
python3 -c "import tensorflow as tf; print('TF',tf.__version__,'GPU',tf.config.list_physical_devices('GPU'))"
echo "[pet] real point-cloud MultiFold $(date -u +%T)"
python3 minerva_pet_dataloader.py --inputs of_inputs_pc.npz --mode pointcloud \
    --model pet --niter 2 --epochs 8 --max-events 2000000 --smoke --save-weights pet_weights.npz
echo "[pet] done $(date -u +%T)"
