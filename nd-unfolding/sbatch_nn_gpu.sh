#!/bin/bash
#SBATCH --job-name=nn_gpu
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=32
#SBATCH --time=04:00:00
#SBATCH --output=nn_gpu_%A.out
#SBATCH --error=nn_gpu_%A.err

# NN-vs-GBDT cross-check, leg 2 (GPU/TensorFlow env): run the keras-MLP OmniFold
# through the same loop on the .npz produced by leg 1. Uses the NERSC tensorflow
# module (matches the vendored repo's tensorflow>=2.15 requirement).
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
cd "${REPO}/nd-unfolding"

module load tensorflow/2.15.0
echo "[leg2] python: $(which python3)"
python3 -c "import tensorflow as tf; print('TF', tf.__version__, 'GPUs', tf.config.list_physical_devices('GPU'))"

NPZ="of_inputs_3d.npz"
echo "[leg2] nn run start $(date -u +%H:%M:%S)"
python3 nn_run_from_npz.py --npz "${NPZ}" --kind nn --iters 5 --out res_nn_3d.npz
echo "[leg2] done $(date -u +%H:%M:%S)"
