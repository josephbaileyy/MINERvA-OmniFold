#!/bin/bash
#SBATCH --job-name=pet_nom_bkgsub
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=32
#SBATCH --time=06:00:00
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=pet/pet_nom_bkgsub_%j.out --error=pet/pet_nom_bkgsub_%j.err
# ============================================================================
# QUARANTINED RECOIL-ONLY CROSS-CHECK LAUNCHER — NOT a publication path.
# Routes through the recoil loader `minerva_pet_dataloader.py` on the recoil
# bkgsub input (of_inputs_pc_fullcloud_bkgsub_5d.npz = purity target, no muon /
# background clouds). It CANNOT produce a full-event publication nominal. The
# full-event PET publication nominal uses `fullevent_fps_dataloader.py`
# (bkg_mode=negweight-refined, G2 full-schema input) and MUST pass
# `fullevent_fps_dataloader.assert_publication_config` (estimator fingerprint
# pet-fullevent-fps-v1 + negweight-refined + G2 markers + background inventory).
# Do not repurpose this script for publication (KNOWN_ISSUES #19 / F7).
# ============================================================================
# PHASE 2: corrected NOMINAL 5D PET estimator on the background-subtracted
# target. ONE unbootstrapped training at the ADOPTED per-train config (the same
# config the corrected C_stat replicas and C_ml ensemble reuse, so the floor,
# C_stat, C_ml, and systematic blocks all reference THIS nominal):
#   input       = of_inputs_pc_fullcloud_bkgsub_5d.npz  (Phase-1 validated)
#   train events = 2,000,000   iters = 2   epochs = 8
#   model = PET   estimator seed = 42   subsample/split seed = 0
#   --reweight-all: push weights evaluated on the FULL 32.8M gen cloud
# Then extract the 5D cross section (PyROOT, via root_6_28). ~1 h on 1 GPU.
set -eo pipefail
export HOME=/global/homes/j/josephrb          # school-account HOME fix
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
cd "${REPO}/nd-unfolding"

INPUTS="${PET_INPUTS:-of_inputs_pc_fullcloud_bkgsub_5d.npz}"
WSOURCE="${PET_W_SOURCE:-of_inputs_5d.npz}"
TRAIN_EVENTS="${PET_TRAIN_EVENTS:-2000000}"
NITER="${PET_NITER:-2}"
EPOCHS="${PET_EPOCHS:-8}"
ESTIMATOR_SEED="${PET_ESTIMATOR_SEED:-42}"
SUBSAMPLE_SEED="${PET_SUBSAMPLE_SEED:-0}"
OUTDIR="${PET_NOM_OUTDIR:-products/pet/bkgsub}"
# PET_NOM_TAG=nominal (default) for Phase 2; =floor for the Phase-3 GPU
# nondeterminism repeat (SAME seeds/config, new output name -> GPU jitter floor).
TAG="${PET_NOM_TAG:-nominal}"
WEIGHTS="${OUTDIR}/pet_${TAG}_bkgsub_5d_weights.npz"
XSEC="${OUTDIR}/pet_${TAG}_bkgsub_5d_xsec.npz"
mkdir -p "${OUTDIR}"

[[ -s "$INPUTS" ]]  || { echo "[FAIL] missing $INPUTS" >&2; exit 2; }
[[ -s "$WSOURCE" ]] || { echo "[FAIL] missing $WSOURCE" >&2; exit 2; }

if [[ "${FORCE_RETRAIN:-0}" != "1" && -s "$WEIGHTS" ]]; then
  echo "[nom] weights ${WEIGHTS} already present; skip training (FORCE_RETRAIN=1 to redo)."
else
  module load tensorflow/2.15.0
  python3 -c "import tensorflow as tf; print('TF',tf.__version__,'GPU',tf.config.list_physical_devices('GPU'))"
  echo "[nom] train $(date -u +%FT%TZ): input=${INPUTS} train=${TRAIN_EVENTS} niter=${NITER} epochs=${EPOCHS} est_seed=${ESTIMATOR_SEED} sub_seed=${SUBSAMPLE_SEED}"
  python3 pet/minerva_pet_dataloader.py \
    --inputs "$INPUTS" --mode pointcloud --model pet --smoke --reweight-all \
    --max-events "$TRAIN_EVENTS" --niter "$NITER" --epochs "$EPOCHS" \
    --seed "$SUBSAMPLE_SEED" --estimator-seed "$ESTIMATOR_SEED" \
    --save-weights "$WEIGHTS"
  echo "[nom] trained -> ${WEIGHTS} $(date -u +%FT%TZ)"
fi

# Extraction needs PyROOT (TF-module python has none): source the analysis env
# and call its python by ABSOLUTE path (KNOWN_ISSUES #17). The extractor also
# self-reexecs through this env as belt-and-braces.
export ROOT628_PREFIX="${ROOT628_PREFIX:-/global/homes/j/josephrb/.conda/envs/root_6_28}"
source "${REPO}/setup_salloc_env.sh"
ROOTPY="${ROOT628_PREFIX}/bin/python3"
echo "[nom] extract $(date -u +%FT%TZ)"
"$ROOTPY" pet/extract_nominal_bkgsub.py \
  --pc "$INPUTS" --w-source "$WSOURCE" --weights "$WEIGHTS" --out "$XSEC"
echo "[nom] done $(date -u +%FT%TZ)"
ls -lh "$WEIGHTS" "$XSEC" "${XSEC%.npz}.summary.json" 2>/dev/null || true
