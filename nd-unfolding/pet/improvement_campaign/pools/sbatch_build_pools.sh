#!/bin/bash
#SBATCH --account=m3246
#SBATCH --constraint=cpu
#SBATCH --qos=debug
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=00:30:00
#SBATCH --job-name=build_pools
set -eo pipefail

# Follow precedent of phase_a/jobs
: "${MINE:?}"
OUT="/pscratch/sd/j/josephrb/pet-improvement-20260922/pools_job_out"
mkdir -p "$OUT"

export PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
module load tensorflow/2.15.0

cd "$OUT"
python "$MINE/nd-unfolding/mnv_guarded_run.py" --expect-root "$MINE" \
  --inventory "$OUT/guard-audit.json" \
  -- "$MINE/nd-unfolding/pet/improvement_campaign/pools/build_pools.py" \
  > "$OUT/build.log" 2>&1 || { rc=$?; echo "exit $rc"; cat "$OUT/build.log"; exit $rc; }

echo "SUCCESS"
cat "$MINE/nd-unfolding/pet/improvement_campaign/pools/POOL_MANIFEST.json"
