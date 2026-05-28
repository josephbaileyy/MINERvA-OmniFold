#!/bin/bash
#SBATCH --job-name=bend_bench
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=128
#SBATCH --time=08:00:00
#SBATCH --output=backend_smoke/bench_MEFHC_%j.out
#SBATCH --error=backend_smoke/bench_MEFHC_%j.err

# UQ plan, stage 1: backend benchmark on full MEFHC, 5 iter, --use-weights.
# Runs hist / xgb / lgbm sequentially on a 128-CPU node, captures wall time
# and peak RSS for each, writes per-backend output ROOTs into
# backend_smoke/. Excludes 'exact' — its baseline (~19h, single-threaded
# regressor) is already documented in AGENTS.md and is not interesting to
# re-measure.

set -eo pipefail
export PYTHONUNBUFFERED=1

REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"
DOCS="${REPO}/2d-unfolding"
OMNIFILE="${DOCS}/runEventLoopOmniFold_MEFHC.root"
FLUX_MC="${DOCS}/baseline_flux/runEventLoopMC_MEFHC.root"

source "${REPO}/setup_salloc_env.sh"
cd "${DOCS}"
mkdir -p backend_smoke

echo "[sbatch] node=$(hostname) jobid=${SLURM_JOB_ID}"
echo "[sbatch] start: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"

for est in hist xgb lgbm; do
  out="backend_smoke/MEFHC_5iter_${est}.root"
  log="backend_smoke/MEFHC_5iter_${est}.log"
  tlog="${log}.time"

  echo "[sbatch] ===== backend: ${est} ====="
  /usr/bin/time -f "[TIME] ${est} wall=%e s, max_rss=%M kB" -o "${tlog}" \
    python -u unfold_2d_omnifold_unbinned.py \
      --omnifile "${OMNIFILE}" \
      --mcfile   "${FLUX_MC}" \
      --iters 5 --use-weights --seed 1 \
      --estimator "${est}" --device cpu \
      --out "${out}" > "${log}" 2>&1
  echo "[sbatch] backend ${est} exit=$?"
  tail -n 1 "${tlog}"
done

echo "[sbatch] done: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "[sbatch] summary:"
for est in hist xgb lgbm; do
  tail -n 1 "backend_smoke/MEFHC_5iter_${est}.log.time" 2>/dev/null || true
done
