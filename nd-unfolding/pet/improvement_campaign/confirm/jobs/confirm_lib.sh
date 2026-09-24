# Sourced by sbatch_confirm_chain.sh and sbatch_confirm_single.sh (not executable on its own).
#
# A run directory is worked on by at most one job at a time. OWNERSHIP IS AN flock(2) on
# $RUN/.flock, taken non-blocking by `claim` and held by an open file descriptor for the REST OF THE
# JOB (inherited by the driver process); the kernel/Lustre release it when the job's processes exit,
# including on SIGKILL at the time limit, so there is no stale lock and no takeover step. /pscratch
# is mounted with the cluster-coherent `flock` option (checked by `require_coherent_flock`; a node
# without it refuses to work). This replaces the mkdir/.lock/job scheme of `661cb5b9`-`e61ba86c`,
# which was NOT atomic (the owner file was written after the mkdir, and stale takeover raced; found
# by review 2026-09-24). A legacy `.lock/job` whose job is still RUNNING is also respected, for the
# transition. The debug chain and a run's gpu_shared copy race through this lock; the loser skips,
# and a completed run's pending copy is cancelled.
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

require_coherent_flock() {
  awk '$2 == "/pscratch" {print $4}' /proc/mounts | tr , '\n' | grep -qx flock || {
    echo "$(date -u +%FT%TZ) job $SLURM_JOB_ID on $(hostname): /pscratch not mounted with flock; refusing" >&2
    exit 3; }
}

legacy_holder_running() {   # 0 if an old-scheme .lock/job names another RUNNING job
  local holder
  holder=$(cat "$OUT/$1/.lock/job" 2>/dev/null) || return 1
  [[ -n "$holder" && "$holder" != "$SLURM_JOB_ID" ]] || return 1
  [[ "$(squeue -h -j "$holder" -o %T 2>/dev/null)" == RUNNING ]]
}

LOCK_FDS=()
claim() {   # take $OUT/$1/.flock for the rest of this job, or return 1 (someone holds it)
  local RUN="$OUT/$1" fd
  mkdir -p "$RUN"
  legacy_holder_running "$1" && return 1
  exec {fd}>>"$RUN/.flock"
  if ! flock -n "$fd"; then exec {fd}>&-; return 1; fi
  LOCK_FDS+=("$fd")
  echo "$(date -u +%FT%TZ) job $SLURM_JOB_ID on $(hostname) holds the flock" >> "$RUN/lock-history.txt"
}

held_by_other() {   # 0 if another job holds $OUT/$1 (probe: take and drop the lock at once)
  local fd
  [[ -e "$OUT/$1/.flock" ]] || { legacy_holder_running "$1"; return; }
  exec {fd}>>"$OUT/$1/.flock"
  if flock -n "$fd"; then flock -u "$fd"; exec {fd}>&-; legacy_holder_running "$1"; return; fi
  exec {fd}>&-; return 0
}

release() { return 0; }   # the flock is released when this job's processes exit

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
