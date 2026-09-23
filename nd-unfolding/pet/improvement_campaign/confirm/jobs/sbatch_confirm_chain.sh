#!/bin/bash
# V1 batch launcher: run every row of a run manifest (confirm/runs/*.tsv) that is not COMPLETE,
# four runs per node (one per GPU), each run checkpointed per OmniFold iteration by B2's loop;
# at its deadline the job RESUBMITS ITSELF (default gpu_debug, 30 min) until every row is
# COMPLETE. Resume is bit-exact (B2's per-step seeding), so a chained run is the same computation
# as an uninterrupted one. COMPLETE runs are scored in the job (`score_replicate.py`) against the
# replicate target and, for pool rows, the population target (computed once per (pool,
# distortion) into $OUT/targets/ by `population_target.py`).
#
#   env: MINE MINE_COMMIT OUT MANIFEST   (MANIFEST relative to confirm/, e.g. runs/x.tsv)
#        [SCORE=1] [CHAIN_QOS=debug CHAIN_TIME=00:30:00 MAX_ROUNDS=16 DEADLINE_MARGIN=240]
#        [ITER_ESTIMATE=800] [RACE_DIR]  (set by submit_confirm.sh; see there)
#
# Manifest columns (tab-separated, '#' comments): name, config (confirm/configs/), config_hash,
# selection ('historical' or POOL:REPLICATE), distortion, reference_run ('-' or a B2 run dir),
# extra driver args ('-' for none).
#SBATCH --account=m3246_g
#SBATCH --constraint=gpu
#SBATCH --qos=debug
#SBATCH --nodes=1
#SBATCH --gpus=4
#SBATCH --time=00:30:00
#SBATCH --job-name=pv1-chain
set -eo pipefail
: "${MINE:?}" ; : "${MINE_COMMIT:?}" ; : "${OUT:?}" ; : "${MANIFEST:?}"
INPUTS=/global/cfs/cdirs/m3246/josephrb/minerva-shutdown-stage/g2_input/G2_FPS_MEFHC_P12.npz
SIDECAR=/pscratch/sd/j/josephrb/event-identity-audit/G2_FPS_MEFHC_P12.identity.npz
POOLS=/pscratch/sd/j/josephrb/pet-improvement-20260922/pools/pools.npz
POPULATIONS=/pscratch/sd/j/josephrb/pet-improvement-20260922/phaseB1/prep/populations.npz
case "$(realpath -m "$OUT")" in /pscratch/sd/j/josephrb/campaign-20260920*) echo "refusing historical output dir" >&2; exit 2;; esac
[[ "$(git -C "$MINE" rev-parse HEAD)" == "$MINE_COMMIT" ]]
[[ -z "$(git -C "$MINE" status --porcelain)" ]]
mkdir -p "$OUT/targets"

# ---- race (first round only): the first of the submitted copies to start wins -------------
if [[ -n "${RACE_DIR:-}" ]]; then
  if mkdir "$RACE_DIR/winner" 2>/dev/null; then
    echo "$SLURM_JOB_ID" > "$RACE_DIR/winner/job"
    for f in "$RACE_DIR"/submitted-*; do
      other=${f##*submitted-}
      [[ "$other" == "$SLURM_JOB_ID" ]] && continue
      # only a copy this submission created (its id was recorded at submission), still ours
      if [[ "$(squeue -h -j "$other" -o '%u %j' 2>/dev/null)" == "$USER pv1-chain" ]]; then
        scancel "$other" && echo "cancelled $other" >> "$RACE_DIR/winner/log"
      fi
    done
  elif [[ "$(cat "$RACE_DIR/winner/job" 2>/dev/null)" != "$SLURM_JOB_ID" ]]; then
    # (a requeued winner -- a preempted copy -- finds its own id and carries on)
    echo "job $SLURM_JOB_ID lost the race to $(cat "$RACE_DIR/winner/job" 2>/dev/null)" >> "$RACE_DIR/losers.txt"
    exit 0
  fi
  RACE_DIR=""; export RACE_DIR
fi

scontrol show job -o "$SLURM_JOB_ID" > "$OUT/allocation-$SLURM_JOB_ID.txt"
export PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 TF_FORCE_GPU_ALLOW_GROWTH=true
export TF_DETERMINISTIC_OPS=1 CUBLAS_WORKSPACE_CONFIG=:4096:8 NVIDIA_TF32_OVERRIDE=0
module load tensorflow/2.15.0
C="$MINE/nd-unfolding/pet/improvement_campaign"
V="$C/confirm"
SELF="$V/jobs/sbatch_confirm_chain.sh"
GUARD="$MINE/nd-unfolding/mnv_guarded_run.py"
IFS=, read -r -a DEVS <<< "${CUDA_VISIBLE_DEVICES:-}"
if (( ${#DEVS[@]} == 0 )); then mapfile -t DEVS < <(seq 0 $(( $(nvidia-smi -L | wc -l) - 1 ))); fi
END_UNIX=$(date -d "$(squeue -h -j "$SLURM_JOB_ID" -o %e)" +%s)
DEADLINE=$(( END_UNIX - ${DEADLINE_MARGIN:-240} ))
mapfile -t ROWS < <(grep -v '^#' "$V/$MANIFEST" | grep -v '^[[:space:]]*$')

remaining() {
  local row name
  for row in "${ROWS[@]}"; do
    name=${row%%$'\t'*}
    [[ "$(cat "$OUT/$name/status.txt" 2>/dev/null)" == COMPLETE ]] || printf '%s\n' "$row"
  done
}
target_path() { echo "$OUT/targets/${1}-${2}.json"; }

# ---- population targets, once per (pool, distortion), in the background --------------------
tpids=()
for row in "${ROWS[@]}"; do
  IFS=$'\t' read -r name cfg hash selection distortion ref extra <<< "$row"
  [[ "$selection" == historical ]] && continue
  pool=${selection%%:*}; T=$(target_path "$pool" "$distortion")
  [[ -s "$T" ]] && continue
  mkdir "$T.lock" 2>/dev/null || continue
  ( python "$GUARD" --expect-root "$MINE" --inventory "$OUT/targets/guard-$pool-$distortion-$SLURM_JOB_ID.json" \
      --label "V1-target-$pool-$distortion" -- "$V/population_target.py" --pool "$pool" \
      --distortion "$distortion" --inputs-npz "$INPUTS" --pools-npz "$POOLS" \
      --manifest "$C/pools/POOL_MANIFEST.json" --populations "$POPULATIONS" --output "$T" \
      >> "$OUT/targets/$pool-$distortion-$SLURM_JOB_ID.log" 2>&1 || echo "target $pool-$distortion exit $?" >> "$OUT/exit-codes.txt"
    rmdir "$T.lock" ) &
  tpids+=($!)
done

mapfile -t TODO < <(remaining)
if (( ${#TODO[@]} == 0 )); then echo "nothing left" > "$OUT/chain-$SLURM_JOB_ID.txt"; wait; exit 0; fi
echo "job $SLURM_JOB_ID deadline $DEADLINE todo ${#TODO[@]}: $(printf '%s ' "${TODO[@]%%$'\t'*}")" >> "$OUT/chain-$SLURM_JOB_ID.txt"

run_one() {
  local ROW=$1 GPU=$2 name cfg hash selection distortion ref extra RUN SEL
  IFS=$'\t' read -r name cfg hash selection distortion ref extra <<< "$ROW"
  RUN="$OUT/$name"; mkdir -p "$RUN"
  if [[ "$selection" == historical ]]; then SEL=(--historical-halves)
  else SEL=(--pool "${selection%%:*}" --replicate "${selection##*:}" --pools-npz "$POOLS" \
            --manifest "$C/pools/POOL_MANIFEST.json"); fi
  [[ "$extra" == "-" ]] && extra=""
  CUDA_VISIBLE_DEVICES=${DEVS[$GPU]} python "$GUARD" --expect-root "$MINE" \
    --inventory "$RUN/guard-$SLURM_JOB_ID.json" --label "V1-$name" \
    -- "$V/run_replicate.py" --config "$V/configs/$cfg" --config-hash "$hash" --repo "$MINE" \
    --out "$RUN" --inputs-npz "$INPUTS" --identity-sidecar "$SIDECAR" \
    --populations "$POPULATIONS" "${SEL[@]}" --distortion "$distortion" \
    --deadline-unix "$DEADLINE" --first-iteration-estimate-s "${ITER_ESTIMATE:-800}" $extra \
    >> "$RUN/run-$SLURM_JOB_ID.log" 2>&1 || { echo "$name exit $?" >> "$OUT/exit-codes.txt"; return 1; }
}

score_one() {
  local ROW=$1 name cfg hash selection distortion ref extra RUN ARGS
  IFS=$'\t' read -r name cfg hash selection distortion ref extra <<< "$ROW"
  RUN="$OUT/$name"
  [[ "$(cat "$RUN/status.txt" 2>/dev/null)" == COMPLETE && ! -s "$RUN/scores.json" ]] || return 0
  ARGS=()
  if [[ "$selection" != historical ]]; then
    T=$(target_path "${selection%%:*}" "$distortion"); [[ -s "$T" ]] && ARGS+=(--population-target "$T")
  fi
  [[ "$ref" != "-" ]] && ARGS+=(--reference-run "$ref")
  python "$GUARD" --expect-root "$MINE" --inventory "$RUN/guard-score-$SLURM_JOB_ID.json" \
    --label "V1-score-$name" -- "$V/score_replicate.py" --run "$RUN" "${ARGS[@]}" \
    >> "$RUN/score-$SLURM_JOB_ID.log" 2>&1 || echo "$name score exit $?" >> "$OUT/exit-codes.txt"
}

status=0
pids=(); i=0
for ROW in "${TODO[@]}"; do
  GPU=$(( i % ${#DEVS[@]} ))
  if (( i >= ${#DEVS[@]} )); then wait "${pids[$GPU]}" || status=1; fi
  run_one "$ROW" "$GPU" & pids[$GPU]=$!
  i=$(( i + 1 ))
done
for pid in "${pids[@]}"; do wait "$pid" || status=1; done
for pid in "${tpids[@]}"; do wait "$pid" || status=1; done
if [[ "${SCORE:-1}" == 1 ]]; then for ROW in "${ROWS[@]}"; do score_one "$ROW"; done; fi
[[ -z "$(git -C "$MINE" status --porcelain)" ]] || status=1

mapfile -t LEFT < <(remaining)
ROUNDS=$(ls "$OUT"/chain-*.txt 2>/dev/null | wc -l)
if (( ${#LEFT[@]} > 0 )) && (( ROUNDS < ${MAX_ROUNDS:-16} )); then
  NEXT=$(sbatch --parsable -q "${CHAIN_QOS:-debug}" -t "${CHAIN_TIME:-00:30:00}" \
    -o "$OUT/slurm-%j.out" --export=ALL "$SELF" 2>&1) || NEXT="resubmit failed: $NEXT"
  echo "resubmitted: $NEXT (left: ${#LEFT[@]})" >> "$OUT/chain-$SLURM_JOB_ID.txt"
elif (( ${#LEFT[@]} > 0 )); then
  echo "NOT resubmitting: round cap ${MAX_ROUNDS:-16} reached (left: ${#LEFT[@]})" >> "$OUT/chain-$SLURM_JOB_ID.txt"
fi
echo "status $status" >> "$OUT/chain-$SLURM_JOB_ID.txt"
exit $status
