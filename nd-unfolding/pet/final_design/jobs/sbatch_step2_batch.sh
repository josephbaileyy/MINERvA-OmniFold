#!/bin/bash
# Runs the step-2 fixed-target interventions listed in LIST (one argument line per run: OUTNAME
# followed by step2_fixed_target.py arguments), GPUS_PER_JOB at a time, one per GPU, each through
# mnv_guarded_run.py from the clean pinned checkout MINE. Simulation only.
#   env: MINE MINE_COMMIT OUT LIST (path relative to MINE)
#SBATCH --account=m3246_g
#SBATCH --constraint=gpu
#SBATCH --job-name=pfd-step2
set -eo pipefail
: "${MINE:?}" ; : "${MINE_COMMIT:?}" ; : "${OUT:?}" ; : "${LIST:?}"
case "$(realpath -m "$OUT")" in /pscratch/sd/j/josephrb/pet-final-design-20260925/*) ;; *) exit 2;; esac
[[ "$(git -C "$MINE" rev-parse HEAD)" == "$MINE_COMMIT" ]]
[[ -z "$(git -C "$MINE" status --porcelain)" ]]
mkdir -p "$OUT"
export PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 TF_FORCE_GPU_ALLOW_GROWTH=true
export TF_DETERMINISTIC_OPS=1 CUBLAS_WORKSPACE_CONFIG=:4096:8 NVIDIA_TF32_OVERRIDE=0
module load tensorflow/2.15.0
C=$MINE/nd-unfolding/pet/improvement_campaign
INPUTS=/global/cfs/cdirs/m3246/josephrb/minerva-shutdown-stage/g2_input/G2_FPS_MEFHC_P12.npz
SIDECAR=/pscratch/sd/j/josephrb/event-identity-audit/G2_FPS_MEFHC_P12.identity.npz
POOLS=/pscratch/sd/j/josephrb/pet-improvement-20260922/pools/pools.npz
POPULATIONS=/pscratch/sd/j/josephrb/pet-improvement-20260922/phaseB1/prep/populations.npz
NG=$(nvidia-smi -L | wc -l)
i=0; pids=()
while IFS= read -r line; do
  [[ -z "$line" || "$line" == \#* ]] && continue
  read -r name rest <<< "$line"
  [[ "$(cat "$OUT/$name/status.txt" 2>/dev/null)" == COMPLETE ]] && continue
  mkdir -p "$OUT/$name"
  dev=$(( i % NG ))
  ( CUDA_VISIBLE_DEVICES=$dev python "$MINE/nd-unfolding/mnv_guarded_run.py" --expect-root "$MINE" \
      --inventory "$OUT/$name/guard-$SLURM_JOB_ID.json" --label "step2-$name" -- \
      "$MINE/nd-unfolding/pet/final_design/diagnostics/step2_fixed_target.py" \
      --repo "$MINE" --out "$OUT/$name" --inputs-npz "$INPUTS" --identity-sidecar "$SIDECAR" \
      --populations "$POPULATIONS" --pools-npz "$POOLS" --manifest "$C/pools/POOL_MANIFEST.json" \
      ${rest//\{C\}/$C} > "$OUT/$name/run-$SLURM_JOB_ID.log" 2>&1 \
      || echo "$name exit $?" >> "$OUT/exit-codes.txt" ) &
  pids+=($!); i=$(( i + 1 ))
  if (( ${#pids[@]} == NG )); then wait "${pids[@]}"; pids=(); fi
done < "$MINE/$LIST"
wait
[[ -z "$(git -C "$MINE" status --porcelain)" ]]
