#!/bin/bash
#SBATCH --job-name=nndump5d
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=8 --mem=110G --time=04:00:00
#SBATCH --output=nndump5d_%j.out --error=nndump5d_%j.err
# Lean 5D OmniFold-inputs npz (one 142 GB read) -> of_inputs_5d.npz, the substrate
# for the dimension-general C_stat (bootstrap_nd.py) and C_ML (seedscan_split.py).
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"
[[ -s of_inputs_5d.npz ]] && { echo "skip (of_inputs_5d.npz exists)"; exit 0; }
python3 nn_dump_inputs.py \
  --omnifile "${REPO}/nd-unfolding/runEventLoopOmniFold_5D_MEFHC_universes_full.root" \
  --axes eavail,q3,W --out of_inputs_5d.npz
