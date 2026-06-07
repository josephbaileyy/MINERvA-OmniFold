#!/bin/bash
#SBATCH --job-name=pet_smoke
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=32
#SBATCH --time=01:00:00
#SBATCH --output=pet_smoke_%A.out
#SBATCH --error=pet_smoke_%A.err

# Phase-2 point-cloud track: prove the vendored ViniciusMikuni/omnifold engine
# (DataLoader + MLP + PET + MultiFold) unfolds OUR data through the new
# minerva_pet_dataloader.py adapter. Scalar mode on the frozen 3D npz; a 1-iter,
# few-epoch MultiFold on a subsample is enough to exercise the full pipeline end
# to end on GPU. Also checks the pointcloud-mode actionable error fires.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
cd "${REPO}/nd-unfolding"

module load tensorflow/2.15.0
echo "[pet] python: $(which python3)"
python3 -c "import tensorflow as tf; print('TF', tf.__version__, 'GPUs', tf.config.list_physical_devices('GPU'))"

echo "==== build-only (loader shapes) ===="
python3 pet/minerva_pet_dataloader.py --inputs of_inputs_3d.npz --mode scalar

echo "==== smoke: vendored MLP MultiFold on our data ===="
python3 pet/minerva_pet_dataloader.py --inputs of_inputs_3d.npz --mode scalar \
    --model mlp --max-events 200000 --niter 1 --epochs 3 --smoke

echo "==== smoke: vendored PET MultiFold on our data (trivial 4-particle cloud) ===="
python3 pet/minerva_pet_dataloader.py --inputs of_inputs_3d.npz --mode scalar --num-part 4 \
    --model pet --max-events 120000 --niter 1 --epochs 3 --smoke

echo "==== pointcloud-mode actionable error (expected to list missing branches) ===="
python3 pet/minerva_pet_dataloader.py --inputs of_inputs_3d.npz --mode pointcloud || true

echo "[pet] done $(date -u +%H:%M:%S)"
