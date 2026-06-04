#!/bin/bash
#SBATCH --job-name=pet_train
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=gpu --nodes=1 --ntasks=1 --gpus=1 --cpus-per-task=32 --time=04:00:00
#SBATCH --output=pet_train_%j.out --error=pet_train_%j.err
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; cd "${REPO}/nd-unfolding"
module load tensorflow/2.15.0
python3 -c "import tensorflow as tf; print('TF',tf.__version__,'GPU',tf.config.list_physical_devices('GPU'))"
echo "[pet] real point-cloud MultiFold $(date -u +%T)"
python3 minerva_pet_dataloader.py --inputs of_inputs_pc.npz --mode pointcloud \
    --model pet --niter 2 --epochs 8 --smoke
echo "[pet] done $(date -u +%T)"
