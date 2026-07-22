#!/bin/bash
#SBATCH --job-name=pet_train_fps_delta
#SBATCH --account=bhvk-delta-gpu
#SBATCH --partition=gpuA100x4
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --gpus-per-node=4
#SBATCH --cpus-per-task=64
#SBATCH --mem=200g
#SBATCH --time=12:00:00
#SBATCH --output=pet_train_fps_delta_%j.out
#SBATCH --error=pet_train_fps_delta_%j.err
# ============================================================================
# NCSA Delta (Apptainer/NGC) port of sbatch_pet_train_fps_hvd.sh -- full-stats
# 4-GPU horovod PET MultiFold on the cloud-fixed FPS point cloud, run on Delta
# A100x4 during the 2026-07-22..08-03 Perlmutter maintenance.
#
# WHY A CONTAINER: Delta's squirrel env is TF 2.21 / py3.12 with no horovod, and
# horovod 0.28.1 won't build against TF 2.21. The NGC TF container carries TF
# 2.14 + horovod 0.28.1 + CUDA/NCCL, close to Perlmutter's TF 2.15 baseline.
# This Delta run is the during-shutdown result; the authoritative TF-2.15 nominal
# is retrained on Perlmutter post-restore under the Gate-4 gate. Record TF 2.14 +
# Delta A100 in RUNS.tsv provenance.
#
# WHY horovodrun -np 4 (not srun -n4): the container horovod has MPI but no Gloo
# (horovodrun --check-build). One srun task launches horovodrun, whose own
# OpenMPI spawns 4 local ranks over shared memory + NCCL/NVLink -- no host-MPI
# bootstrap. minerva_pet_dataloader.py reads OMPI_COMM_WORLD_* for striding.
#
# ONE-TIME SETUP (see PET_TRAINING_ON_DELTA.md; do before sbatch):
#   1. git clone the repo to $HOME/MINERvA-OmniFold
#   2. apptainer pull $HOME/tf215.sif docker://nvcr.io/nvidia/tensorflow:24.01-tf2-py3
#   3. omnifold deps missing from the image -> install to a host dir with the
#      container's OWN pip (py-version match), added to PYTHONPATH below:
#        apptainer exec --nv $HOME/tf215.sif pip install --target=$HOME/petpkgs "matplotlib<3.9" "numpy<2" PyYAML
#      (pin numpy<2: the image is numpy 1.x for TF 2.14; latest matplotlib would
#      drag numpy 2.x into petpkgs and shadow/break the container's TF)
#   4. Globus the npz to $DATA; build the memmap once (in-container, see runbook).
# ============================================================================
set -eo pipefail

# ---- EDIT to your Delta layout ----
REPO="${REPO:-$HOME/MINERvA-OmniFold}"
DATA="${DATA:-/work/nvme/bhvk/$USER/pet_inputs}"       # staged npz (not backed up)
SIF="${SIF:-$HOME/tf215.sif}"
PKGS="${PKGS:-$HOME/petpkgs}"                           # matplotlib/PyYAML installed here
cd "${REPO}/nd-unfolding"

# ---- training recipe (matches the Perlmutter headline) ----
NITER="${NITER:-5}"
EPOCHS="${EPOCHS:-8}"
TRAIN_EVENTS="${TRAIN_EVENTS:-40000000}"               # full stats; 10000000 for a fast check
NP="${NP:-4}"                                           # GPUs = MPI ranks
INPUTS="${INPUTS:-of_inputs_pc_fps_xps2.npz}"          # Gate-4 nominal input
MEMMAP_DIR="${MEMMAP_DIR:-of_inputs_pc_fps_xps2_npy}"
SEED="${SEED:-101}"
SAVE_WEIGHTS="${SAVE_WEIGHTS:-products/pet/pet_weights_fps_xps2_delta_s${SEED}.npz}"
mkdir -p products/pet

# stage the npz into cwd so the relative --inputs name resolves
[ -e "${INPUTS}" ] || ln -sf "${DATA}/${INPUTS}" "${INPUTS}"
[ -s "${INPUTS}" ] || { echo "[pet-fps] MISSING ${INPUTS} (Globus it to ${DATA})"; exit 1; }
[ -d "${MEMMAP_DIR}" ] || { echo "[pet-fps] MISSING memmap ${MEMMAP_DIR}; build it once (in-container):"; \
    echo "  apptainer exec --nv --bind $REPO,$DATA --env PYTHONPATH=$REPO/omnifold_nn:$PKGS $SIF \\"; \
    echo "    python3 pet/npz_to_npy.py --inputs ${INPUTS} --out ${MEMMAP_DIR}"; exit 1; }

echo "[pet-fps] $(date -u +%FT%TZ) np=${NP} niter=${NITER} epochs=${EPOCHS} train=${TRAIN_EVENTS} seed=${SEED} inputs=${INPUTS}"
srun --gpu-bind=none apptainer exec --nv \
    --bind "${REPO}","${DATA}" \
    --env PYTHONPATH="${REPO}/omnifold_nn:${PKGS}" \
    "${SIF}" \
    horovodrun -np "${NP}" python3 pet/minerva_pet_dataloader.py --inputs "${INPUTS}" \
        --mode pointcloud --model pet --niter "${NITER}" --epochs "${EPOCHS}" \
        --max-events "${TRAIN_EVENTS}" --seed "${SEED}" --reweight-all --smoke \
        --save-weights "${SAVE_WEIGHTS}" --memmap-dir "${MEMMAP_DIR}"
echo "[pet-fps] wrote ${SAVE_WEIGHTS}; done $(date -u +%FT%TZ)"
