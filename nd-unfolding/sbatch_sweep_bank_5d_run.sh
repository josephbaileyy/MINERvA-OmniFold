#!/bin/bash
#SBATCH --job-name=banksweep5d
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=16 --mem=48G --time=01:30:00
#SBATCH --array=1-175%48
#SBATCH --output=banksweep5d_%a_%A.out --error=banksweep5d_%a_%A.err
# Stage-2 5D unfold of each VERTICAL universe from the bank (skip-if-exists). The 6
# GEANT universes already produced by sbatch_unfold_5d_detector.sh are skipped, so this
# effectively fills the 169 missing Flux+GENIE vertical universes.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"
U=$(sed -n "${SLURM_ARRAY_TASK_ID}p" uq_4d/vertical_universes.txt)
[[ -z "$U" ]] && exit 0
python3 sweep_bank_5d.py --run --universe "$U" \
  --bankdir "${REPO}/nd-unfolding/bank_sweep_5d" \
  --outdir "${REPO}/nd-unfolding/uq_5d/universe_sweep" --iters 5
