#!/bin/bash
#SBATCH --job-name=uthrow5d_dump
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=8 --mem=110G --time=06:00:00
#SBATCH --array=0-7
#SBATCH --output=uthrow5d_dump_%a_%A.out --error=uthrow5d_dump_%a_%A.err
# Dump the 5D unified-throw ratio bank (bank_uthrow_5d) from the regenerated 142GB
# 5D universes_full omnifile: per-event Flux(100)+12-knob truth/reco/denom RATIOS
# (group 0 also writes cv.npz with MCgen/MCreco/measured 5 cols + edges_0..4 +
# td_pt/pz/ea/q3/W). unified_throw.py do_dump is axis-general via --axes.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"
python3 unified_throw.py --dump --group ${SLURM_ARRAY_TASK_ID} --ngroups 8 \
  --omnifile "${REPO}/nd-unfolding/runEventLoopOmniFold_5D_MEFHC_universes_full.root" \
  --axes eavail,q3,W \
  --bankdir "${REPO}/nd-unfolding/bank_uthrow_5d"
