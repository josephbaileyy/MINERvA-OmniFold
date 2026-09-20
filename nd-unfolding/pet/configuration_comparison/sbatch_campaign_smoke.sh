#!/bin/bash
# Does an arm-pair evaluation START? Both arms, tiny, one iteration.
#
# WHY. `run_arm_evaluation.evaluate` has never been executed end to end. The
# campaign's first tuning task would be the first run of it, after hours of
# queue wait, and a crash in the loaders, the substitution, the gather or the
# model construction would cost a day to discover and another to re-queue. This
# is the same code path at a few thousand events.
#
# It is NOT a measurement. Too few events, one iteration, and its output goes to
# a scratch directory OUTSIDE the campaign tree so `report_campaign.discover`
# can never find it. Nothing here is scored and no recovery is computed.
#SBATCH --account=m3246_g
#SBATCH --constraint=gpu
#SBATCH --qos=shared
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --gpus=1
#SBATCH --mem=56G
#SBATCH --time=01:20:00
#SBATCH --job-name=pet-campaign-smoke
set -eo pipefail

checkout=${CHECKOUT:?}
output=${OUTPUT:?}
expected_commit=${COMMIT:?}
inputs=${INPUTS_NPZ:?}
index=${THEIRS_INDEX:?}
events=${MAX_EVENTS:-40000}
# Two disjoint halves must fit inside the subsample, so the smoke half is a
# quarter of it. The campaign's half size comes from the closure module.
# A stage owns as little as 0.20 of the draw, and needs TWO halves inside it,
# so the smoke half is a twelfth rather than a quarter.
half=${HALF_SIZE:-$((events / 12))}

cd "$checkout"
[[ "$(git rev-parse HEAD)" == "$expected_commit" ]]
[[ -z "$(git status --porcelain)" ]]
case "$output" in
  *campaign-20260920*) echo "refusing: smoke output must not sit in the campaign tree" >&2; exit 2;;
esac
mkdir -p "$output"
scontrol show job -o "$SLURM_JOB_ID" > "$output/allocation.txt"
nvidia-smi --query-gpu=uuid,name,memory.total --format=csv > "$output/gpu.csv"

export PYTHONUNBUFFERED=1 TF_FORCE_GPU_ALLOW_GROWTH=true
export TF_DETERMINISTIC_OPS=1 CUBLAS_WORKSPACE_CONFIG=:4096:8
export NVIDIA_TF32_OVERRIDE=0

IDENTITY_SIDECAR=${IDENTITY_SIDECAR:-/pscratch/sd/j/josephrb/event-identity-audit/G2_FPS_MEFHC_P12.identity.npz}
[[ -f "$IDENTITY_SIDECAR" ]] || { echo "identity sidecar missing: $IDENTITY_SIDECAR" >&2; exit 2; }


pre=nd-unfolding/pet/configuration_comparison/prematerialize_theirs.py
driver=nd-unfolding/pet/configuration_comparison/run_arm_evaluation.py
cache="$output/theirs-tuning.npz"
( module load tensorflow/2.15.0
  # Build his gather ONCE, exactly as the campaign will, so the smoke test
  # exercises the path the campaign takes rather than the fallback. Measured:
  # the in-process gather cost 15.5 minutes before his first training step.
  echo "===== prematerialize ====="
  timeout --kill-after=30s 1800s python "$pre" \
    --inputs-npz "$inputs" --theirs-index "$index" --out "$cache" \
    --identity-sidecar "$IDENTITY_SIDECAR" --stage tuning \
    --subsample-seed 0 --max-events "$events" --half-size "$half" \
    --report "$output/prematerialize.json" || echo "PREMATERIALIZE FAILED ($?)"

  for arm in ours theirs; do
    echo "===== $arm ====="
    timeout --kill-after=30s 900s python "$driver" \
      --arm "$arm" --seed 17 --stage tuning --learning-rate 1e-4 --niter 1 \
      --repo "$checkout" --inputs-npz "$inputs" --theirs-index "$index" \
      --max-events "$events" --half-size "$half" \
      --identity-sidecar "$IDENTITY_SIDECAR" \
      --theirs-cache "$cache" \
        --weights-folder "$output/$arm" \
      --output "$output/smoke-$arm.json" || echo "ARM $arm FAILED ($?)"
  done
) > "$output/smoke.log" 2>&1

for arm in ours theirs; do
  [[ -s "$output/smoke-$arm.json" ]] || { echo "NO RECEIPT for $arm" >> "$output/terminal.txt"; }
done
echo DONE >> "$output/terminal.txt"
