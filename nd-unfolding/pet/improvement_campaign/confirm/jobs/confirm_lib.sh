# Sourced by sbatch_confirm_chain.sh and sbatch_confirm_single.sh (not executable on its own).
#
# A run directory is worked on by at most one job at a time: `claim` takes $RUN/.lock (mkdir is
# atomic) and records the job id; a lock whose job is no longer RUNNING is stale and is taken
# over (a job killed at its time limit cannot release it). The debug chain and the single-GPU
# gpu_shared copy of a run therefore RACE: whichever gets the lock works on the run (resume is
# bit-exact, so the two can alternate), the other skips it; when a run is COMPLETE its pending
# gpu_shared copy is cancelled (only a job this campaign recorded in $RUN/shared_job, and only if
# it is still this user's pending pv1-single job).
INPUTS=/global/cfs/cdirs/m3246/josephrb/minerva-shutdown-stage/g2_input/G2_FPS_MEFHC_P12.npz
SIDECAR=/pscratch/sd/j/josephrb/event-identity-audit/G2_FPS_MEFHC_P12.identity.npz
POOLS=/pscratch/sd/j/josephrb/pet-improvement-20260922/pools/pools.npz
POPULATIONS=/pscratch/sd/j/josephrb/pet-improvement-20260922/phaseB1/prep/populations.npz
C="$MINE/nd-unfolding/pet/improvement_campaign"
V="$C/confirm"
GUARD="$MINE/nd-unfolding/mnv_guarded_run.py"

setup_env() {
  export PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 TF_FORCE_GPU_ALLOW_GROWTH=true
  export TF_DETERMINISTIC_OPS=1 CUBLAS_WORKSPACE_CONFIG=:4096:8 NVIDIA_TF32_OVERRIDE=0
  module load tensorflow/2.15.0
}

manifest_rows() { grep -v '^#' "$V/$MANIFEST" | grep -v '^[[:space:]]*$'; }
row_name() { printf '%s' "${1%%$'\t'*}"; }
is_complete() { [[ "$(cat "$OUT/$1/status.txt" 2>/dev/null)" == COMPLETE ]]; }
target_path() { echo "$OUT/targets/${1}-${2}.json"; }

held_by_other() {   # 0 if $OUT/$1 is locked by another RUNNING job
  local holder
  holder=$(cat "$OUT/$1/.lock/job" 2>/dev/null) || return 1
  [[ -n "$holder" && "$holder" != "$SLURM_JOB_ID" ]] || return 1
  [[ "$(squeue -h -j "$holder" -o %T 2>/dev/null)" == RUNNING ]]
}

claim() {
  local RUN="$OUT/$1"; mkdir -p "$RUN"
  if mkdir "$RUN/.lock" 2>/dev/null; then echo "$SLURM_JOB_ID" > "$RUN/.lock/job"; return 0; fi
  held_by_other "$1" && return 1
  echo "$SLURM_JOB_ID" > "$RUN/.lock/job"          # stale (or our own, requeued): take over
  echo "$(date -u +%FT%TZ) job $SLURM_JOB_ID took over the lock" >> "$RUN/lock-history.txt"
}

release() {
  [[ "$(cat "$OUT/$1/.lock/job" 2>/dev/null)" == "$SLURM_JOB_ID" ]] && rm -rf "$OUT/$1/.lock"
  return 0
}

cancel_pending_copy() {   # the run is COMPLETE: its gpu_shared copy is the loser
  local j
  j=$(cat "$OUT/$1/shared_job" 2>/dev/null) || return 0
  [[ -n "$j" && "$j" != "$SLURM_JOB_ID" ]] || return 0
  if [[ "$(squeue -h -j "$j" -o '%u %j %T' 2>/dev/null)" == "$USER pv1-single PENDING" ]]; then
    scancel "$j" && echo "$(date -u +%FT%TZ) job $SLURM_JOB_ID cancelled pending copy $j" \
      >> "$OUT/$1/lock-history.txt"
  fi
  return 0
}

run_row() {   # ROW DEVICE DEADLINE
  local ROW=$1 DEV=$2 DL=$3 name cfg hash selection distortion ref extra RUN SEL
  IFS=$'\t' read -r name cfg hash selection distortion ref extra <<< "$ROW"
  RUN="$OUT/$name"; mkdir -p "$RUN"
  if [[ "$selection" == historical ]]; then SEL=(--historical-halves)
  else SEL=(--pool "${selection%%:*}" --replicate "${selection##*:}" --pools-npz "$POOLS" \
            --manifest "$C/pools/POOL_MANIFEST.json"); fi
  [[ "$extra" == "-" ]] && extra=""
  extra=${extra//\{C\}/$C}
  CUDA_VISIBLE_DEVICES=$DEV python "$GUARD" --expect-root "$MINE" \
    --inventory "$RUN/guard-$SLURM_JOB_ID.json" --label "V1-$name" \
    -- "$V/run_replicate.py" --config "$V/configs/$cfg" --config-hash "$hash" --repo "$MINE" \
    --out "$RUN" --inputs-npz "$INPUTS" --identity-sidecar "$SIDECAR" \
    --populations "$POPULATIONS" "${SEL[@]}" --distortion "$distortion" \
    --deadline-unix "$DL" --first-iteration-estimate-s "${ITER_ESTIMATE:-800}" $extra \
    >> "$RUN/run-$SLURM_JOB_ID.log" 2>&1 || { echo "$name exit $? (job $SLURM_JOB_ID)" >> "$OUT/exit-codes.txt"; return 1; }
}

ensure_target() {   # POOL DISTORTION (serialized by a lock directory)
  local T; T=$(target_path "$1" "$2")
  [[ -s "$T" ]] && return 0
  mkdir -p "$OUT/targets"
  if ! mkdir "$T.lock" 2>/dev/null; then
    for _ in $(seq 1 60); do [[ -s "$T" ]] && return 0; sleep 10; done; return 1
  fi
  python "$GUARD" --expect-root "$MINE" --inventory "$OUT/targets/guard-$1-$2-$SLURM_JOB_ID.json" \
    --label "V1-target-$1-$2" -- "$V/population_target.py" --pool "$1" --distortion "$2" \
    --inputs-npz "$INPUTS" --pools-npz "$POOLS" --manifest "$C/pools/POOL_MANIFEST.json" \
    --populations "$POPULATIONS" --output "$T" >> "$OUT/targets/$1-$2-$SLURM_JOB_ID.log" 2>&1 \
    || echo "target $1-$2 exit $?" >> "$OUT/exit-codes.txt"
  rmdir "$T.lock"
}

score_row() {
  local ROW=$1 name cfg hash selection distortion ref extra RUN ARGS T
  IFS=$'\t' read -r name cfg hash selection distortion ref extra <<< "$ROW"
  RUN="$OUT/$name"
  is_complete "$name" && [[ ! -s "$RUN/scores.json" ]] || return 0
  ARGS=()
  if [[ "$selection" != historical ]]; then
    ensure_target "${selection%%:*}" "$distortion" || true
    T=$(target_path "${selection%%:*}" "$distortion"); [[ -s "$T" ]] && ARGS+=(--population-target "$T")
  fi
  [[ "$ref" != "-" ]] && ARGS+=(--reference-run "$ref")
  python "$GUARD" --expect-root "$MINE" --inventory "$RUN/guard-score-$SLURM_JOB_ID.json" \
    --label "V1-score-$name" -- "$V/score_replicate.py" --run "$RUN" "${ARGS[@]}" \
    >> "$RUN/score-$SLURM_JOB_ID.log" 2>&1 || echo "$name score exit $?" >> "$OUT/exit-codes.txt"
}
