#!/bin/bash
#SBATCH --job-name=uthfpsC
#SBATCH --account=m3246_g
#SBATCH --qos=shared --constraint=gpu --nodes=1 --ntasks=1 --gpus-per-task=1 --cpus-per-task=32 --time=06:00:00
#SBATCH --array=0-39%16
#SBATCH --nice=10000
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
#SBATCH --output=uq_fps/corrected/logs/uthfpsC_%a_%A.out --error=uq_fps/corrected/logs/uthfpsC_%a_%A.err
# CORRECTED FPS unified-throw slabs (Agent C / P6-FPS). 40 tasks x THROWS_PER=4 = 160
# joint throws (all 12 knobs asymmetric-interp + 1 sampled flux universe, re-unfold),
# seed 1000, one FIXED estimator seed (default 42 inside _xsec_for_weights). The current
# unified_throw_cov.py STAMPS the estimator seed in every slab; the June uthrow_slabs_fps
# slabs carried NO seed stamp so the corrected combine rejects them -> regenerated here.
# THROWS_PER=4 finishes well inside the 6h wall (5D lesson: size tasks so a wall-kill
# loses <=1 slab; incremental _atomic_savez keeps completed throws). High --nice yields
# to PET(B)/4D(D). Non-destructive: uq_fps/corrected/uthrow_slabs_fps_neutral/.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; source "${REPO}/setup_salloc_env.sh"
export PYTHONUNBUFFERED=1; cd "${REPO}/nd-unfolding"; mkdir -p uq_fps/corrected/uthrow_slabs_fps_neutral
THROWS_PER="${THROWS_PER:-4}"
OFF=$(( SLURM_ARRAY_TASK_ID * THROWS_PER ))
OUT="uq_fps/corrected/uthrow_slabs_fps_neutral/uthrowfps_slab_${SLURM_ARRAY_TASK_ID}.npz"
[[ -s "${OUT}" ]] && { echo "skip (exists) ${OUT}"; exit 0; }
echo "[uthrowfpsC] task=${SLURM_ARRAY_TASK_ID} throws ${OFF}..$((OFF+THROWS_PER-1)) $(date -u '+%F %T UTC')"
python3 unified_throw_cov.py --throws "${THROWS_PER}" --throw-offset "${OFF}" \
    --seed 1000 --bank bank_uthrow_fps --iters 5 --invalid-ratio neutral --out "${OUT}"
echo "[uthrowfpsC] task=${SLURM_ARRAY_TASK_ID} done $(date -u '+%F %T UTC')"
