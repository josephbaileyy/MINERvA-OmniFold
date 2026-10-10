#!/bin/bash
#SBATCH --job-name=sb1_cv
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=64
#SBATCH --time=00:40:00
#SBATCH --no-requeue
# SB1 C: one CV-file replica as 59410433_1 (shared 64, OMP_NUM_THREADS=64, --bootstrap-seed 1
# --seed 1) under the phase-timing wrapper, then the CV pattern's loader identity on the same file.
set -eo pipefail
source "${SB1_RUN_ENV:?submit with sb1_submit.sh}"
D="${SB1_OUT}/C"
mkdir "${D}"
sb1_check_env
source "${SB1_ENV_SETUP}"
export PYTHONUNBUFFERED=1
cd "${D}"
echo "[sb1] C job=${SLURM_JOB_ID:-} node=$(hostname) start $(date -u +%FT%TZ)"
"${SB1_PY}" "${SB1_CODE}/${SB1_PKG}/sb1_admit.py" expect --admission "${SB1_ADMISSION}" \
  --hashes "${SB1_OUT}/H0/hashes.json" --omnifile "${SB1_CV}" --out "${D}/expect.json"
guarded() {  # guarded TAG MODE sb1_run-arguments...  (common options precede any `--`)
  local tag="$1" mode="$2"; shift 2
  "${SB1_PY}" "${SB1_CODE}/nd-unfolding/mnv_guarded_run.py" --expect-root "${SB1_CODE}" \
    --inventory "${D}/inventory_${tag}.jsonl" --label "sb1-C-${tag}" -- \
    "${SB1_CODE}/${SB1_PKG}/sb1_run.py" "${mode}" --label "sb1-C-${tag}" \
    --expect "${D}/expect.json" --require-provenance --input-hashes "${SB1_OUT}/H0/hashes.json" "$@"
}
export OMP_NUM_THREADS=64      # as 59410433 (OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK})
guarded unfold unfold --arm all --receipt "${D}/receipt.json" -- \
  --omnifile "${SB1_CV}" --mcfile "${SB1_MC}" --iters 5 --use-weights --estimator lgbm \
  --bootstrap-seed 1 --seed 1 --out "${D}/2d_xsec_C.root"
export OMP_NUM_THREADS=1
guarded loaders_all loaders --arm all --omnifile "${SB1_CV}" \
  --receipt "${D}/loaders_all.json"
guarded loaders_selective loaders --arm selective --omnifile "${SB1_CV}" \
  --receipt "${D}/loaders_selective.json" --compare-digests "${D}/loaders_all.json"
echo "[sb1] C done $(date -u +%FT%TZ)"
