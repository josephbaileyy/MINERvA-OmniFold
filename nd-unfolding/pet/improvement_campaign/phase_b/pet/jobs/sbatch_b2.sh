#!/bin/bash
# Task B2: run one or more campaign configs, one per GPU, each through the OI-136 guard with NO
# --allow, from a clean checkout pinned to MINE_COMMIT. Submit with the QOS/GPU count on the
# command line (e.g. `sbatch -q shared --gpus=1 -c 32` or `-q regular -N 1 --gpus=4`).
#   MINE         clean checkout (git HEAD must equal MINE_COMMIT, tree clean before and after)
#   OUT          output dir; each config writes OUT/<config name>/
#   CONFIGS      space-separated config file names under phase_b/pet/configs/; a token may carry
#                per-run driver arguments after a '|' (e.g. "x.json|--step2-miss-mode=eff...")
#   DRIVER       script relative to improvement_campaign/ (default run_unfold.py; the B2 driver
#                phase_b/pet/b2_driver.py also gets --deadline-unix from the allocation end)
#   DRIVER_ARGS  extra arguments for the driver (optional)
#   SCORE        if 1, score each finished run with phase_b/pet/b2_score.py (optional)
#   POPULATIONS  B1's cached populations.npz (needed when SCORE=1)
#SBATCH --account=m3246_g
#SBATCH --constraint=gpu
#SBATCH --job-name=pb2
set -eo pipefail
: "${MINE:?}" ; : "${MINE_COMMIT:?}" ; : "${OUT:?}" ; : "${CONFIGS:?}"
DRIVER=${DRIVER:-run_unfold.py}
INPUTS=/global/cfs/cdirs/m3246/josephrb/minerva-shutdown-stage/g2_input/G2_FPS_MEFHC_P12.npz
SIDECAR=/pscratch/sd/j/josephrb/event-identity-audit/G2_FPS_MEFHC_P12.identity.npz
case "$OUT" in /pscratch/sd/j/josephrb/campaign-20260920*) echo "refusing historical output dir" >&2; exit 2;; esac
[[ "$(git -C "$MINE" rev-parse HEAD)" == "$MINE_COMMIT" ]]
[[ -z "$(git -C "$MINE" status --porcelain)" ]]
mkdir -p "$OUT"
scontrol show job -o "$SLURM_JOB_ID" > "$OUT/allocation-$SLURM_JOB_ID.txt"
nvidia-smi --query-gpu=index,uuid,name,memory.total --format=csv > "$OUT/gpu-$SLURM_JOB_ID.csv"
export PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 TF_FORCE_GPU_ALLOW_GROWTH=true
export TF_DETERMINISTIC_OPS=1 CUBLAS_WORKSPACE_CONFIG=:4096:8 NVIDIA_TF32_OVERRIDE=0
module load tensorflow/2.15.0
C="$MINE/nd-unfolding/pet/improvement_campaign"
B="$C/phase_b/pet"
# GPU slots: the devices Slurm handed this job (its CUDA_VISIBLE_DEVICES), else all visible ones.
IFS=, read -r -a DEVS <<< "${CUDA_VISIBLE_DEVICES:-}"
if (( ${#DEVS[@]} == 0 )); then mapfile -t DEVS < <(seq 0 $(( $(nvidia-smi -L | wc -l) - 1 ))); fi
NGPU=${#DEVS[@]}
# The B2 driver stops starting iterations 5 min before the allocation ends (resumable).
END_UNIX=$(date -d "$(squeue -h -j "$SLURM_JOB_ID" -o %e)" +%s)
DEADLINE=$(( END_UNIX - 300 ))
[[ "$DRIVER" == *b2_driver.py ]] && DRIVER_ARGS="$DRIVER_ARGS --deadline-unix $DEADLINE"
echo "job $SLURM_JOB_ID end $END_UNIX deadline $DEADLINE devices ${DEVS[*]} driver $DRIVER args $DRIVER_ARGS" >> "$OUT/launch-$SLURM_JOB_ID.txt"
read -r -a LIST <<< "$CONFIGS"
run_one() {  # $1 = config token ("file.json" or "file.json|extra args"), $2 = GPU index
  local TOKEN=$1 GPU=$2 CFG EXTRA NAME RUN
  CFG=${TOKEN%%|*}; EXTRA=""; [[ "$TOKEN" == *"|"* ]] && EXTRA=${TOKEN#*|}
  NAME=$(basename "$CFG" .json); RUN="$OUT/$NAME"; mkdir -p "$RUN"
  CUDA_VISIBLE_DEVICES=${DEVS[$GPU]} python "$MINE/nd-unfolding/mnv_guarded_run.py" --expect-root "$MINE" \
    --inventory "$RUN/guard-$SLURM_JOB_ID.json" --label "B2-$NAME" \
    -- "$C/$DRIVER" --config "$B/configs/$CFG" --repo "$MINE" --out "$RUN" \
    --inputs-npz "$INPUTS" --identity-sidecar "$SIDECAR" $DRIVER_ARGS $EXTRA \
    >> "$RUN/run-$SLURM_JOB_ID.log" 2>&1 || { echo "$NAME train exit $?" >> "$OUT/exit-codes.txt"; return 1; }
  if [[ "${SCORE:-0}" == 1 ]]; then
    python "$MINE/nd-unfolding/mnv_guarded_run.py" --expect-root "$MINE" \
      --inventory "$RUN/guard-score-$SLURM_JOB_ID.json" --label "B2-score-$NAME" \
      -- "$B/b2_score.py" --run "$RUN" --populations "${POPULATIONS:?}" \
      >> "$RUN/score-$SLURM_JOB_ID.log" 2>&1 || { echo "$NAME score exit $?" >> "$OUT/exit-codes.txt"; return 1; }
  fi
  echo "$NAME done $(date -u +%FT%TZ)" >> "$OUT/done-$SLURM_JOB_ID.txt"
}
status=0
pids=()
i=0
for CFG in "${LIST[@]}"; do
  GPU=$(( i % NGPU ))
  if (( i >= NGPU )); then wait "${pids[$GPU]}" || status=1; fi
  run_one "$CFG" "$GPU" & pids[$GPU]=$!
  i=$(( i + 1 ))
done
for pid in "${pids[@]}"; do wait "$pid" || status=1; done
[[ -z "$(git -C "$MINE" status --porcelain)" ]] || { echo "checkout dirtied" >&2; status=1; }
[[ $status == 0 ]] && echo COMPLETE > "$OUT/terminal-$SLURM_JOB_ID.txt" || echo FAILED > "$OUT/terminal-$SLURM_JOB_ID.txt"
exit $status
