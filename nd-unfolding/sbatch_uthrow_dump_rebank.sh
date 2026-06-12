#!/bin/bash
#SBATCH --job-name=uthrow_rebank
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=8 --mem=64G --time=06:00:00
#SBATCH --array=0-7
#SBATCH --output=uthrow_rebank_%a_%A.out --error=uthrow_rebank_%a_%A.err

# KNOWN_ISSUES #12 residual: regenerate bank_uthrow with the post-fix dump
# (miss-row rhos pinned to 1.0 = the post-fix event-loop CV proxies; the old
# bank carried garbage on the 12.35M appended miss rows, mangled by _clip to
# {1e-2,1,1e2} inside pet_systematics C_syst). Source = the merged 5D MEFHC
# file (NOT the 3D default: of_inputs_pc.npz row order is the 5D signal tree).
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"
python3 unified_throw.py --dump --group ${SLURM_ARRAY_TASK_ID} --ngroups 8 \
  --omnifile runEventLoopOmniFold_5D_MEFHC_universes_full.root \
  --axes "eavail,q3" --bankdir bank_uthrow
