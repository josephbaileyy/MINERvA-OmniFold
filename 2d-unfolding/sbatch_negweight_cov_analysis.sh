#!/bin/bash
#SBATCH --job-name=nw_cov_analysis
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=24G
#SBATCH --time=02:00:00
#SBATCH --output=nw_cov_analysis_%j.out
#SBATCH --error=nw_cov_analysis_%j.err
set -uo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
export ROOT628_PREFIX=/global/homes/j/josephrb/.conda/envs/root_6_28
# The root_6_28 binutils conda-activate hook references $ADDR2LINE unguarded,
# which trips `set -u` (nounset) and aborts before the analysis runs. Relax
# nounset only around env sourcing, then restore it.
set +u
source "${REPO}/setup_salloc_env.sh"
set -u
bash "${REPO}/2d-unfolding/HANDOFF_bkg_negweight/run_negweight_covariance_analysis.sh"
