#!/bin/bash
#SBATCH --job-name=boot4dC
#SBATCH --account=m3246_g
#SBATCH --qos=shared --constraint=gpu --nodes=1 --ntasks=1 --gpus-per-task=1 --cpus-per-task=32 --time=03:00:00
#SBATCH --array=1-100%32
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=uq_4d/corrected/logs/boot4dC_%a_%A.out --error=uq_4d/corrected/logs/boot4dC_%a_%A.err
# P6-4D corrected C_stat: coherent data+MC Poisson bootstrap at FIXED estimator
# seed 42 (bootstrap seed varies event weights only). Regenerates the corrected
# statistical replicas the archived June boot_nd_4d_prehm_* set predates: the
# corrected bootstrap_nd.py (07c18ae) fixes the estimator seed and decorrelates
# the data/MC Poisson draws (rng_d=seed, rng_m=seed+1e7) -- the June replicas
# varied the estimator seed with the bootstrap seed (KNOWN_ISSUES #14).
# CPU account m3246 is exhausted -> run the UNCHANGED bootstrap_nd.py (LightGBM,
# CPU code) on GPU-node HOST CORES (32 cpus/task), charged to m3246_g; the GPU
# is idle. --export HOME fixes the school-account conda-by-prefix trap.
# Writes ONLY to uq_4d/corrected/ (old boot_nd_4d is quarantined). skip-if-exists.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"; mkdir -p uq_4d/corrected/boot_nd_4d
OUT="uq_4d/corrected/boot_nd_4d/res_boot_${SLURM_ARRAY_TASK_ID}.npz"
[[ -s "${OUT}" ]] && { echo "skip (exists) ${OUT}"; exit 0; }
python3 bootstrap_nd.py --npz of_inputs_4d.npz --seed ${SLURM_ARRAY_TASK_ID} \
  --estimator-seed 42 --iters 5 --out "${OUT}"
