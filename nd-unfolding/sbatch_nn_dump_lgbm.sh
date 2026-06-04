#!/bin/bash
#SBATCH --job-name=nn_dump_lgbm
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --time=04:00:00
#SBATCH --output=nn_dump_lgbm_%A.out
#SBATCH --error=nn_dump_lgbm_%A.err

# NN-vs-GBDT cross-check, leg 1 (CPU/ROOT env): dump the 3D OmniFold inputs to a
# ROOT-free .npz, then run the GBDT baseline through the SAME loop on that .npz so
# the only difference vs the NN leg (sbatch_nn_gpu.sh) is the classifier.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
cd "${REPO}/nd-unfolding"

NPZ="of_inputs_3d.npz"
echo "[leg1] dump start $(date -u +%H:%M:%S)"
python3 nn_dump_inputs.py \
    --omnifile ../3d-unfolding/runEventLoopOmniFold_MEFHC_3D.root \
    --axes eavail --out "${NPZ}"
echo "[leg1] lgbm run start $(date -u +%H:%M:%S)"
python3 nn_run_from_npz.py --npz "${NPZ}" --kind lgbm --iters 5 --out res_lgbm_3d.npz
echo "[leg1] done $(date -u +%H:%M:%S)"
