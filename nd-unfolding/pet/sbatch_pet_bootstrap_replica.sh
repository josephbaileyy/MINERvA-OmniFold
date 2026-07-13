#!/bin/bash
#SBATCH --job-name=pet_boot_one
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=32
#SBATCH --time=06:00:00
#SBATCH --output=pet_boot_%j.out
#SBATCH --error=pet_boot_%j.err

# Produce ONE corrected PET statistical replica. Submit individual seeds (or a
# separately approved small array) with:  REPLICA_ID=1 sbatch this_script.sh
# The measured data and MC are Poisson-fluctuated, PET is retrained at a fixed
# estimator seed, the coherent full-event MC draw is applied in final binning,
# and strict 4D/5D cross-section NPZs are written atomically.
set -eo pipefail

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
cd "${REPO}/nd-unfolding"

RID="${REPLICA_ID:?set REPLICA_ID to the integer replica seed}"
INPUTS="${PET_INPUTS:-of_inputs_pc_fullcloud.npz}"
WSOURCE="${PET_W_SOURCE:-of_inputs_5d.npz}"
OUTDIR="${PET_BOOT_OUTDIR:-products/pet/bootstrap_replicas}"
TRAIN_EVENTS="${PET_TRAIN_EVENTS:-2000000}"
NITER="${PET_NITER:-2}"
EPOCHS="${PET_EPOCHS:-8}"
ESTIMATOR_SEED="${PET_ESTIMATOR_SEED:-42}"
WEIGHTS="${OUTDIR}/weights/pet_bootstrap_weights_${RID}.npz"

[[ "$RID" =~ ^[0-9]+$ ]] || { echo "[FAIL] REPLICA_ID must be a non-negative integer" >&2; exit 2; }
[[ -s "$INPUTS" ]] || { echo "[FAIL] missing PET inputs $INPUTS" >&2; exit 2; }
[[ -s "$WSOURCE" ]] || { echo "[FAIL] missing 5D W source $WSOURCE" >&2; exit 2; }
mkdir -p "${OUTDIR}/weights" "${OUTDIR}/4d" "${OUTDIR}/5d"

module load tensorflow/2.15.0
python3 pet/minerva_pet_dataloader.py \
  --inputs "$INPUTS" --mode pointcloud --model pet --smoke --reweight-all \
  --max-events "$TRAIN_EVENTS" --niter "$NITER" --epochs "$EPOCHS" \
  --seed 0 --estimator-seed "$ESTIMATOR_SEED" --bootstrap-seed "$RID" \
  --save-weights "$WEIGHTS"

# Extraction needs PyROOT: the TF-module python above has none, and a bare
# (unactivated) root_6_28 python segfaults in cling. Source the analysis env
# and call its python by ABSOLUTE path -- with the TF module loaded, PATH
# order after activation still resolves `python3` to the TF interpreter.
# (extract_bootstrap_replica.py also self-re-execs through this env as a
# belt-and-braces for job scripts snapshotted before this fix.)
export ROOT628_PREFIX="${ROOT628_PREFIX:-/global/homes/j/josephrb/.conda/envs/root_6_28}"
source "${REPO}/setup_salloc_env.sh"
ROOTPY="${ROOT628_PREFIX}/bin/python3"

"$ROOTPY" pet/extract_bootstrap_replica.py \
  --dimension 4 --seed "$RID" --pc "$INPUTS" --weights "$WEIGHTS" \
  --out "${OUTDIR}/4d/pet_bootstrap_4d_${RID}.npz"
"$ROOTPY" pet/extract_bootstrap_replica.py \
  --dimension 5 --seed "$RID" --pc "$INPUTS" --w-source "$WSOURCE" \
  --weights "$WEIGHTS" --out "${OUTDIR}/5d/pet_bootstrap_5d_${RID}.npz"

echo "[pet-bootstrap] completed corrected replica ${RID}"
