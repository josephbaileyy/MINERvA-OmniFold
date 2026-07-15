#!/bin/bash
#SBATCH --job-name=pet_p7_retrain
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=32
#SBATCH --time=04:00:00
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=pet/pet_p7_%x_%j.out --error=pet/pet_p7_%x_%j.err
# PHASE 7: retrain the PET reweighter on ONE systematic universe's prior and
# compare the retrained-map universe estimate to the frozen-map one (C_syst).
#   UNIVERSE=MaRES:1   (band:endpoint 0|1)  or  UNIVERSE=flux:37
#   BANK (default bank_uthrow_5d = PRELIMINARY pre-fix; FINAL swaps the
#         GBDT background-aware/selection-complete bank once CPU restores it)
# GPU train (tensorflow/2.15.0, ~1 h) then PyROOT extract+compare (root_6_28).
# GPU-only per the campaign constraint (CPU allocation exhausted).
set -eo pipefail
export HOME=/global/homes/j/josephrb
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
cd "${REPO}/nd-unfolding"

UNIVERSE="${UNIVERSE:?set UNIVERSE=MaRES:1 or flux:37}"
BANK="${PET_P7_BANK:-bank_uthrow_5d}"
INPUTS="${PET_INPUTS:-of_inputs_pc_fullcloud_bkgsub_5d.npz}"
WSOURCE="${PET_W_SOURCE:-of_inputs_5d.npz}"
NOMW="${PET_NOM_WEIGHTS:-products/pet/bkgsub/pet_nominal_bkgsub_5d_weights.npz}"
TRAIN_EVENTS="${PET_TRAIN_EVENTS:-2000000}"
NITER="${PET_NITER:-2}"; EPOCHS="${PET_EPOCHS:-8}"
EST_SEED="${PET_ESTIMATOR_SEED:-42}"; SUB_SEED="${PET_SUBSAMPLE_SEED:-0}"
OUTDIR="${PET_P7_OUTDIR:-products/pet/bkgsub/p7}"; mkdir -p "${OUTDIR}"
TAG="${UNIVERSE/:/_}"
RETW="${OUTDIR}/pet_p7_${TAG}_weights.npz"
RESP="${OUTDIR}/pet_p7_${TAG}_response.npz"

[[ -s "$INPUTS" ]] || { echo "[FAIL] missing $INPUTS" >&2; exit 2; }
[[ -s "$NOMW"   ]] || { echo "[FAIL] missing nominal weights $NOMW" >&2; exit 2; }
[[ -d "$BANK"   ]] || { echo "[FAIL] missing bank $BANK" >&2; exit 2; }

if [[ "${FORCE_RETRAIN:-0}" != "1" && -s "$RETW" ]]; then
  echo "[p7] retrained weights ${RETW} present; skip training (FORCE_RETRAIN=1 to redo)."
else
  module load tensorflow/2.15.0
  python3 -c "import tensorflow as tf; print('TF',tf.__version__,'GPU',tf.config.list_physical_devices('GPU'))"
  echo "[p7] train $(date -u +%FT%TZ): universe=${UNIVERSE} bank=${BANK} events=${TRAIN_EVENTS} niter=${NITER} epochs=${EPOCHS} est_seed=${EST_SEED}"
  python3 pet/phase7_retrain_universe.py \
    --universe "$UNIVERSE" --inputs "$INPUTS" --bank "$BANK" --invalid-ratio neutral \
    --max-events "$TRAIN_EVENTS" --niter "$NITER" --epochs "$EPOCHS" \
    --seed "$SUB_SEED" --estimator-seed "$EST_SEED" --save-weights "$RETW"
  echo "[p7] trained -> ${RETW} $(date -u +%FT%TZ)"
fi

export ROOT628_PREFIX="${ROOT628_PREFIX:-/global/homes/j/josephrb/.conda/envs/root_6_28}"
source "${REPO}/setup_salloc_env.sh"
ROOTPY="${ROOT628_PREFIX}/bin/python3"
echo "[p7] extract+compare $(date -u +%FT%TZ)"
"$ROOTPY" pet/phase7_extract_compare.py \
  --universe "$UNIVERSE" --pc "$INPUTS" --w-source "$WSOURCE" \
  --nominal-weights "$NOMW" --retrained-weights "$RETW" --bank "$BANK" \
  --invalid-ratio neutral --out "$RESP"
echo "[p7] done $(date -u +%FT%TZ)"
ls -lh "$RETW" "$RESP" "${RESP%.npz}.summary.json" 2>/dev/null || true
