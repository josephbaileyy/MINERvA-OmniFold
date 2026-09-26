#!/bin/bash
# PET final-design launcher: runs the rows of a run manifest that are not COMPLETE, through the
# predecessor's validated per-run path (improvement_campaign/confirm: run_replicate.py under
# mnv_guarded_run.py, flock ownership per run directory, bit-exact per-iteration resume, scoring in
# the job). Differences from the predecessor's sbatch_confirm_chain.sh:
#   * WORKER SLOTS: SLOTS_PER_GPU workers per GPU (default 1); each worker repeatedly claims the
#     next open row and runs it until the allocation's deadline, so a long allocation (e.g. a
#     4-hour gpu_interactive srun) keeps every GPU busy across many rows;
#   * CHAIN=1 (default under sbatch): queue the next round at the start (afterany), as the
#     predecessor did; CHAIN=0 (use under srun --qos=interactive): no successor.
#
#   env: MINE MINE_COMMIT OUT MANIFEST (relative to improvement_campaign/confirm/)
#        [SLOTS_PER_GPU=1] [CHAIN=1] [CHAIN_QOS=debug] [CHAIN_TIME=00:30:00] [MAX_ROUNDS=24]
#        [DEADLINE_MARGIN=240] [ITER_ESTIMATE=800] [SCORE=1]
#        [BANKS=<banks.npz>] [BANK_MANIFEST=<json>]  (design_lib.sh; see its header)
#SBATCH --account=m3246_g
#SBATCH --constraint=gpu
#SBATCH --qos=debug
#SBATCH --nodes=1
#SBATCH --gpus=4
#SBATCH --ntasks=1
#SBATCH --time=00:30:00
#SBATCH --job-name=pfd-chain
set -eo pipefail
: "${MINE:?}" ; : "${MINE_COMMIT:?}" ; : "${OUT:?}" ; : "${MANIFEST:?}"
case "$(realpath -m "$OUT")" in
  /pscratch/sd/j/josephrb/pet-final-design-20260925/*) ;;
  *) echo "OUT must be under the study namespace" >&2; exit 2;;
esac
[[ "$(git -C "$MINE" rev-parse HEAD)" == "$MINE_COMMIT" ]]
[[ -z "$(git -C "$MINE" status --porcelain)" ]]
mkdir -p "$OUT"
scontrol show job -o "$SLURM_JOB_ID" > "$OUT/allocation-$SLURM_JOB_ID.txt"
source "$MINE/nd-unfolding/pet/improvement_campaign/confirm/jobs/confirm_lib.sh"
# The study runner (final_design/runner/run_design.py: bank draws BANK:<bank>:<stage>:<rep>,
# null distortion, bootstrap members, study arms) replaces run_replicate.py in run_row when the
# pinned checkout carries design_lib.sh; predecessor-style rows (<pool>:<rep>, historical) keep
# byte-identical inputs through it.
DESIGN_LIB="$MINE/nd-unfolding/pet/final_design/jobs/design_lib.sh"
if [[ -f "$DESIGN_LIB" ]]; then source "$DESIGN_LIB"; fi
setup_env
require_coherent_flock
# Population targets are whole-pool aggregate spectra; this study computes none over the predecessor
# pools (they contain final-bank rows). Scores use the replicate's own pseudodata truth; a
# predecessor target copied into $OUT/targets beforehand is used if present.
ensure_target() { return 0; }
SELF="$MINE/nd-unfolding/pet/final_design/jobs/pfd_worker_chain.sh"
IFS=, read -r -a DEVS <<< "${CUDA_VISIBLE_DEVICES:-}"
if (( ${#DEVS[@]} == 0 )); then mapfile -t DEVS < <(seq 0 $(( $(nvidia-smi -L | wc -l) - 1 ))); fi
END_UNIX=$(date -d "$(squeue -h -j "$SLURM_JOB_ID" -o %e)" +%s)
DEADLINE=$(( END_UNIX - ${DEADLINE_MARGIN:-240} ))
mapfile -t ROWS < <(manifest_rows)
LOG="$OUT/chain-$SLURM_JOB_ID.txt"

[[ "${SCORE:-1}" == 1 ]] && for ROW in "${ROWS[@]}"; do score_row "$ROW"; done
unfinished() { local r; for r in "${ROWS[@]}"; do is_complete "$(row_name "$r")" || echo x; done; }
mapfile -t UNF < <(unfinished)
if (( ${#UNF[@]} == 0 )); then echo "all COMPLETE" > "$LOG"; exit 0; fi

NEXT=""
if [[ "${CHAIN:-1}" == 1 ]] && (( $(ls "$OUT"/chain-*.txt 2>/dev/null | wc -l) < ${MAX_ROUNDS:-24} )); then
  # CHAIN_EXTRA: extra sbatch arguments for the successor, e.g. "--gpus=1 -c 32" for a gpu_shared
  # chain (the #SBATCH header describes a whole debug node)
  # shellcheck disable=SC2086
  NEXT=$(sbatch --parsable -q "${CHAIN_QOS:-debug}" -t "${CHAIN_TIME:-00:30:00}" ${CHAIN_EXTRA:-} \
    --dependency="afterany:$SLURM_JOB_ID" -o "$OUT/slurm-%j.out" --export=ALL "$SELF" 2>&1) || {
    echo "$(date -u +%FT%TZ) job $SLURM_JOB_ID could NOT queue its successor: $NEXT" >> "$OUT/exit-codes.txt"
    NEXT=""; }
fi
echo "job $SLURM_JOB_ID slots ${SLOTS_PER_GPU:-1}/gpu x ${#DEVS[@]} gpus, deadline $DEADLINE, next ${NEXT:-none}" >> "$LOG"

next_open_claim() {   # claim the next open row into CLAIMED_ROW (no subshell: the flock fd must
  local row name       # stay open in THIS worker), or return 1
  CLAIMED_ROW=""
  for row in "${ROWS[@]}"; do
    name=$(row_name "$row")
    is_complete "$name" && continue
    held_by_other "$name" && continue
    if claim "$name"; then CLAIMED_ROW=$row; return 0; fi
  done
  return 1
}

worker() {   # SLOT DEVICE
  local slot=$1 dev=$2 row name rc=0
  while :; do
    (( $(date +%s) + ${ITER_ESTIMATE:-800} * 11 / 10 + 150 < DEADLINE )) || break
    next_open_claim || break
    row=$CLAIMED_ROW; name=$(row_name "$row")
    echo "$(date -u +%FT%TZ) slot $slot gpu $dev -> $name" >> "$LOG"
    is_complete "$name" || run_row "$row" "$dev" "$DEADLINE" || rc=1
    if is_complete "$name"; then [[ "${SCORE:-1}" == 1 ]] && score_row "$row"; fi
    # the claim's fd stays open in this worker: release it by closing every lock fd we took
    for fd in "${LOCK_FDS[@]}"; do exec {fd}>&- 2>/dev/null || true; done
    LOCK_FDS=()
    is_complete "$name" || break     # stopped at the deadline (or crashed): no new row
  done
  return $rc
}

status=0; pids=()
NSLOT=$(( ${#DEVS[@]} * ${SLOTS_PER_GPU:-1} ))
for (( s = 0; s < NSLOT; s++ )); do
  worker "$s" "${DEVS[$(( s % ${#DEVS[@]} ))]}" & pids+=($!)
  sleep 5
done
for pid in "${pids[@]}"; do wait "$pid" || status=1; done
[[ -z "$(git -C "$MINE" status --porcelain)" ]] || status=1
mapfile -t UNF < <(unfinished)
if (( ${#UNF[@]} == 0 )) && [[ -n "$NEXT" ]]; then
  [[ "$(squeue -h -j "$NEXT" -o '%u %j' 2>/dev/null)" == "$USER pfd-chain" ]] && scancel "$NEXT"
  echo "all COMPLETE; cancelled $NEXT" >> "$LOG"
elif (( status != 0 )) && [[ -n "$NEXT" ]]; then
  [[ "$(squeue -h -j "$NEXT" -o '%u %j' 2>/dev/null)" == "$USER pfd-chain" ]] && scancel "$NEXT"
  echo "a run exited non-zero (exit-codes.txt); cancelled $NEXT" >> "$LOG"
fi
echo "status $status" >> "$LOG"
exit $status
