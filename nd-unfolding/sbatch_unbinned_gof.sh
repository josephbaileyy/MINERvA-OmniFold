#!/bin/bash
#SBATCH --job-name=of_gof
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=04:00:00
#SBATCH --output=of_gof_%j.out
#SBATCH --error=of_gof_%j.err

# Unbinned goodness-of-fit (Classifier Two-Sample Test) on the frozen 3D inputs.
# Runs the validated GBDT OmniFold loop to get converged weights, then the C2ST
# between data reco and OmniFold-reweighted MC reco (prior/CV baseline + unfolded).
# ROOT-free (lgbm). prepub item #3.

set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1
cd "${REPO}/nd-unfolding"

echo "[gof] start $(date -u '+%F %T UTC')"
python3 unbinned_gof.py --inputs of_inputs_3d.npz --kind lgbm --iters 5 \
    --max-per-class 600000 --save-weights of_weights_3d.npz
echo "[gof] done  $(date -u '+%F %T UTC')"
