#!/bin/bash
# Task B2: run a batch of K-iteration configs as a CHAIN of short jobs (gpu_debug starts in
# minutes where gpu_regular stalled for hours). Each job runs the still-incomplete configs, one
# per GPU, until its own deadline, then RESUBMITS ITSELF if anything is left. The B2 driver
# checkpoints and resumes per OmniFold iteration and seeds each step from its own recipe, so a
# chained run is bit-identical to an uninterrupted one.
#   MINE MINE_COMMIT OUT CONFIGS [DRIVER_ARGS] [SCORE POPULATIONS] [CHAIN_QOS CHAIN_TIME]
#SBATCH --account=m3246_g
#SBATCH --constraint=gpu
#SBATCH --qos=debug
#SBATCH --nodes=1
#SBATCH --gpus=4
#SBATCH --time=00:30:00
#SBATCH --job-name=pb2-chain
set -eo pipefail
: "${MINE:?}" ; : "${MINE_COMMIT:?}" ; : "${OUT:?}" ; : "${CONFIGS:?}"
INPUTS=/global/cfs/cdirs/m3246/josephrb/minerva-shutdown-stage/g2_input/G2_FPS_MEFHC_P12.npz
SIDECAR=/pscratch/sd/j/josephrb/event-identity-audit/G2_FPS_MEFHC_P12.identity.npz
case "$OUT" in /pscratch/sd/j/josephrb/campaign-20260920*) echo "refusing historical output dir" >&2; exit 2;; esac
[[ "$(git -C "$MINE" rev-parse HEAD)" == "$MINE_COMMIT" ]]
[[ -z "$(git -C "$MINE" status --porcelain)" ]]
mkdir -p "$OUT"
scontrol show job -o "$SLURM_JOB_ID" > "$OUT/allocation-$SLURM_JOB_ID.txt"
export PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 TF_FORCE_GPU_ALLOW_GROWTH=true
export TF_DETERMINISTIC_OPS=1 CUBLAS_WORKSPACE_CONFIG=:4096:8 NVIDIA_TF32_OVERRIDE=0
module load tensorflow/2.15.0
C="$MINE/nd-unfolding/pet/improvement_campaign"
B="$C/phase_b/pet"
SELF="$B/jobs/sbatch_b2_chain.sh"
IFS=, read -r -a DEVS <<< "${CUDA_VISIBLE_DEVICES:-}"
if (( ${#DEVS[@]} == 0 )); then mapfile -t DEVS < <(seq 0 $(( $(nvidia-smi -L | wc -l) - 1 ))); fi
END_UNIX=$(date -d "$(squeue -h -j "$SLURM_JOB_ID" -o %e)" +%s)
DEADLINE=$(( END_UNIX - 240 ))
read -r -a LIST <<< "$CONFIGS"
remaining() {  # config tokens whose run is not COMPLETE yet
  local out=() t name
  for t in "${LIST[@]}"; do
    name=$(basename "${t%%|*}" .json)
    [[ "$(cat "$OUT/$name/status.txt" 2>/dev/null)" == COMPLETE ]] || out+=("$t")
  done
  printf '%s\n' "${out[@]}"
}
mapfile -t TODO < <(remaining)
TODO=("${TODO[@]:-}")
if [[ -z "${TODO[0]:-}" ]]; then echo "nothing left" > "$OUT/chain-$SLURM_JOB_ID.txt"; exit 0; fi
echo "job $SLURM_JOB_ID deadline $DEADLINE todo ${TODO[*]}" >> "$OUT/chain-$SLURM_JOB_ID.txt"
run_one() {
  local TOKEN=$1 GPU=$2 CFG EXTRA NAME RUN
  CFG=${TOKEN%%|*}; EXTRA=""; [[ "$TOKEN" == *"|"* ]] && EXTRA=${TOKEN#*|}
  NAME=$(basename "$CFG" .json); RUN="$OUT/$NAME"; mkdir -p "$RUN"
  CUDA_VISIBLE_DEVICES=${DEVS[$GPU]} python "$MINE/nd-unfolding/mnv_guarded_run.py" \
    --expect-root "$MINE" --inventory "$RUN/guard-$SLURM_JOB_ID.json" --label "B2-chain-$NAME" \
    -- "$B/b2_driver.py" --config "$B/configs/$CFG" --repo "$MINE" --out "$RUN" \
    --inputs-npz "$INPUTS" --identity-sidecar "$SIDECAR" --deadline-unix "$DEADLINE" \
    --first-iteration-estimate-s "${ITER_ESTIMATE:-800}" $DRIVER_ARGS $EXTRA \
    >> "$RUN/run-$SLURM_JOB_ID.log" 2>&1 || { echo "$NAME exit $?" >> "$OUT/exit-codes.txt"; return 1; }
  if [[ "${SCORE:-0}" == 1 && "$(cat "$RUN/status.txt" 2>/dev/null)" == COMPLETE ]]; then
    python "$MINE/nd-unfolding/mnv_guarded_run.py" --expect-root "$MINE" \
      --inventory "$RUN/guard-score-$SLURM_JOB_ID.json" --label "B2-score-$NAME" \
      -- "$B/b2_score.py" --run "$RUN" --populations "${POPULATIONS:?}" \
      >> "$RUN/score-$SLURM_JOB_ID.log" 2>&1 || echo "$NAME score exit $?" >> "$OUT/exit-codes.txt"
  fi
}
status=0
pids=(); i=0
for TOKEN in "${TODO[@]}"; do
  GPU=$(( i % ${#DEVS[@]} ))
  if (( i >= ${#DEVS[@]} )); then wait "${pids[$GPU]}" || status=1; fi
  run_one "$TOKEN" "$GPU" & pids[$GPU]=$!
  i=$(( i + 1 ))
done
for pid in "${pids[@]}"; do wait "$pid" || status=1; done
[[ -z "$(git -C "$MINE" status --porcelain)" ]] || status=1
mapfile -t LEFT < <(remaining)
LEFT=("${LEFT[@]:-}")
if [[ -n "${LEFT[0]:-}" ]]; then
  NEXT=$(sbatch --parsable -q "${CHAIN_QOS:-debug}" -t "${CHAIN_TIME:-00:30:00}" \
    -o "$OUT/slurm-%j.out" --export=ALL "$SELF" 2>&1) || NEXT="resubmit failed: $NEXT"
  echo "resubmitted: $NEXT (left: ${LEFT[*]})" >> "$OUT/chain-$SLURM_JOB_ID.txt"
fi
echo "status $status" >> "$OUT/chain-$SLURM_JOB_ID.txt"
exit $status
