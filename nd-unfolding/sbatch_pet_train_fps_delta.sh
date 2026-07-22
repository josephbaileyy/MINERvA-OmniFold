#!/bin/bash
#SBATCH --job-name=pet_train_fps_delta
#SBATCH --account=bhvk-delta-gpu
#SBATCH --partition=gpuA100x4
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=4
#SBATCH --gpus-per-node=4
#SBATCH --gpu-bind=none
#SBATCH --cpus-per-task=16
#SBATCH --mem=200g
#SBATCH --time=12:00:00
#SBATCH --output=pet_train_fps_delta_%j.out
#SBATCH --error=pet_train_fps_delta_%j.err
# ============================================================================
# NCSA Delta port of sbatch_pet_train_fps_hvd.sh -- full-stats 4-GPU horovod
# PET MultiFold on the cloud-fixed FPS point cloud, run on Delta A100x4 during
# the 2026-07-22..08-03 Perlmutter maintenance. A100 matches the Perlmutter
# training baseline (minimal GPU-nondeterminism change vs. an H100 port).
#
# ONE-TIME SETUP (see PET_TRAINING_ON_DELTA.md runbook, do these before sbatch):
#   1. git clone the repo to $HOME/MINERvA-OmniFold on Delta
#   2. source /projects/bhvk/setup.sh   (activates the squirrel conda env)
#   3. python -c "import horovod.tensorflow as hvd; print(hvd.__version__)"
#      -> if this fails, install horovod into the env (see runbook step 2);
#         this is the one genuinely platform-specific dependency.
#   4. pip install -e "$HOME/MINERvA-OmniFold/omnifold_nn" --no-deps  # puts
#      `omnifold` on the path without perturbing squirrel's TF/numpy (horovod is
#      only an extra; the hardcoded _REPO in the dataloader is thus sidestepped)
#   5. Globus the npz to $DATA (below); build the memmap once (step below).
#
# VERIFY ON FIRST LOGIN (values below are Delta defaults, confirm for your alloc):
#   - partition name: `sinfo -s | grep A100`  (gpuA100x4 / gpuA100x4-interactive)
#   - cores/node & mem: adjust --cpus-per-task / --mem to the A100x4 node
#   - `accounts` -> remaining GPU-hours before a ~8h x 4-GPU (=32 GPU-hr) run
# ============================================================================
set -eo pipefail

# ---- EDIT to your Delta layout ----
REPO="${REPO:-$HOME/MINERvA-OmniFold}"
DATA="${DATA:-/work/nvme/bhvk/$USER/pet_inputs}"   # staged npz lives here (not backed up)
cd "${REPO}/nd-unfolding"

# ---- environment ----
source /projects/bhvk/setup.sh                      # squirrel: tensorflow (+ horovod, see setup)
export PYTHONUNBUFFERED=1

# ---- training recipe (identical to the Perlmutter headline) ----
NITER="${NITER:-5}"
EPOCHS="${EPOCHS:-8}"
TRAIN_EVENTS="${TRAIN_EVENTS:-40000000}"            # full stats; use 10000000 for a fast check
INPUTS="${INPUTS:-of_inputs_pc_fps_xps2.npz}"       # the Gate-4 nominal input
MEMMAP_DIR="${MEMMAP_DIR:-of_inputs_pc_fps_xps2_npy}"
SEED="${SEED:-101}"                                 # estimator seed; matched repeat re-runs with same recipe
SAVE_WEIGHTS="${SAVE_WEIGHTS:-products/pet/pet_weights_fps_xps2_delta_s${SEED}.npz}"
mkdir -p products/pet

# stage the npz into cwd so the relative --inputs name resolves
[ -e "${INPUTS}" ] || ln -sf "${DATA}/${INPUTS}" "${INPUTS}"
[ -s "${INPUTS}" ] || { echo "[pet-fps] MISSING ${INPUTS} (Globus it to ${DATA})"; exit 1; }
[ -d "${MEMMAP_DIR}" ] || { echo "[pet-fps] MISSING memmap ${MEMMAP_DIR}; build it once:"; \
    echo "    python3 pet/npz_to_npy.py --inputs ${INPUTS} --out ${MEMMAP_DIR}"; exit 1; }

echo "[pet-fps] $(date -u +%FT%TZ) niter=${NITER} epochs=${EPOCHS} train=${TRAIN_EVENTS} ranks=${SLURM_NTASKS} seed=${SEED} inputs=${INPUTS}"
srun -u python3 pet/minerva_pet_dataloader.py --inputs "${INPUTS}" --mode pointcloud \
    --model pet --niter "${NITER}" --epochs "${EPOCHS}" --max-events "${TRAIN_EVENTS}" \
    --seed "${SEED}" --reweight-all --smoke --save-weights "${SAVE_WEIGHTS}" \
    --memmap-dir "${MEMMAP_DIR}"
echo "[pet-fps] wrote ${SAVE_WEIGHTS}; done $(date -u +%FT%TZ)"
