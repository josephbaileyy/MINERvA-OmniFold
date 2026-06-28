#!/bin/bash
#SBATCH --job-name=pet_train_fc
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=gpu --nodes=1 --ntasks=1 --gpus=1 --cpus-per-task=32 --time=06:00:00
#SBATCH --output=pet_train_fc_%j.out --error=pet_train_fc_%j.err
# Stage 4 (Tier 2): retrain PET on the fullcloud npz so step-2 sees the real
# miss-row truth clouds (previously empty). Same config as the production
# pet_weights_full.npz (2M train, niter 2, epochs 8, reweight-all on full stats)
# so the only change vs baseline is the now-populated miss clouds. New output
# name keeps the baseline weights intact. (--smoke is the real-run flag here.)
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
cd "${REPO}/nd-unfolding"
INPUTS="of_inputs_pc_fullcloud.npz"
SAVE="products/pet/pet_weights_fullcloud.npz"
[ -s "$INPUTS" ] || { echo "[pet] MISSING $INPUTS"; exit 1; }
module load tensorflow/2.15.0
python3 -c "import tensorflow as tf; print('TF',tf.__version__,'GPU',tf.config.list_physical_devices('GPU'))"
echo "[pet] fullcloud retrain (train=2M, reweight-all) $(date -u +%T)"
python3 pet/minerva_pet_dataloader.py --inputs "${INPUTS}" --mode pointcloud \
    --model pet --niter 2 --epochs 8 --max-events 2000000 \
    --reweight-all --smoke --save-weights "${SAVE}"
echo "[pet] wrote ${SAVE}; done $(date -u +%T)"
