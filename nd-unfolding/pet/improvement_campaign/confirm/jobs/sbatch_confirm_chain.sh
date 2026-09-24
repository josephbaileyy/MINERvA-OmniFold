#!/bin/bash
# V1 batch launcher: run every row of a run manifest (confirm/runs/*.tsv) that is not COMPLETE,
# four runs per node (one per GPU), each run checkpointed per OmniFold iteration by B2's loop;
# at its deadline the job RESUBMITS ITSELF (default gpu_debug, 30 min) until every row is
# COMPLETE (never after a round in which a run crashed). Resume is bit-exact (B2's per-step
# seeding), so a chained run is the same computation as an uninterrupted one. COMPLETE runs are
# scored in the job (`score_replicate.py`) against the replicate target and, for pool rows, the
# population target (computed once per (pool, distortion) into $OUT/targets/ by
# `population_target.py`).
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
case "$(realpath -m "$OUT")" in /pscratch/sd/j/josephrb/campaign-20260920*) echo "refusing historical output dir" >&2; exit 2;; esac
[[ "$(git -C "$MINE" rev-parse HEAD)" == "$MINE_COMMIT" ]]
[[ -z "$(git -C "$MINE" status --porcelain)" ]]
mkdir -p "$OUT"

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
source "$MINE/nd-unfolding/pet/improvement_campaign/confirm/jobs/confirm_lib.sh"
setup_env
SELF="$V/jobs/sbatch_confirm_chain.sh"
IFS=, read -r -a DEVS <<< "${CUDA_VISIBLE_DEVICES:-}"
if (( ${#DEVS[@]} == 0 )); then mapfile -t DEVS < <(seq 0 $(( $(nvidia-smi -L | wc -l) - 1 ))); fi
END_UNIX=$(date -d "$(squeue -h -j "$SLURM_JOB_ID" -o %e)" +%s)
DEADLINE=$(( END_UNIX - ${DEADLINE_MARGIN:-240} ))
mapfile -t ROWS < <(manifest_rows)

open_rows() {   # not COMPLETE and not being worked on by another running job
  local row name
  for row in "${ROWS[@]}"; do
    name=$(row_name "$row")
    is_complete "$name" || held_by_other "$name" || printf '%s\n' "$row"
  done
}

# score rows a previous round completed but could not score before its time limit
for ROW in "${ROWS[@]}"; do score_row "$ROW"; done
mapfile -t UNFINISHED < <(for r in "${ROWS[@]}"; do is_complete "$(row_name "$r")" || echo x; done)
if (( ${#UNFINISHED[@]} == 0 )); then echo "all COMPLETE" > "$OUT/chain-$SLURM_JOB_ID.txt"; exit 0; fi
# queue the next round NOW (it starts when this one ends), so a round killed at its limit still
# chains and no queue wait falls between rounds; cancelled below if it turns out not to be needed
NEXT=""
if (( $(ls "$OUT"/chain-*.txt 2>/dev/null | wc -l) < ${MAX_ROUNDS:-16} )); then
  NEXT=$(sbatch --parsable -q "${CHAIN_QOS:-debug}" -t "${CHAIN_TIME:-00:30:00}" \
    --dependency="afterany:$SLURM_JOB_ID" -o "$OUT/slurm-%j.out" --export=ALL "$SELF" 2>&1) || NEXT=""
fi
echo "job $SLURM_JOB_ID next round queued: ${NEXT:-none}" >> "$OUT/chain-$SLURM_JOB_ID.txt"
cancel_next() {
  [[ -n "$NEXT" && "$(squeue -h -j "$NEXT" -o '%u %j' 2>/dev/null)" == "$USER pv1-chain" ]] && scancel "$NEXT"
  echo "cancelled queued next round $NEXT: $1" >> "$OUT/chain-$SLURM_JOB_ID.txt"
}
mapfile -t TODO < <(open_rows)
if (( ${#TODO[@]} == 0 )); then echo "nothing open (held by others)" >> "$OUT/chain-$SLURM_JOB_ID.txt"; exit 0; fi
echo "job $SLURM_JOB_ID deadline $DEADLINE open ${#TODO[@]}" >> "$OUT/chain-$SLURM_JOB_ID.txt"

work_on() {   # ROW DEVICE (already claimed): run, score, release
  local name; name=$(row_name "$1")
  local rc=0
  is_complete "$name" || run_row "$1" "$2" "$DEADLINE" || rc=1
  if is_complete "$name"; then [[ "${SCORE:-1}" == 1 ]] && score_row "$1"; cancel_pending_copy "$name"; fi
  release "$name"
  return $rc
}

status=0
pids=(); i=0
for ROW in "${TODO[@]}"; do
  (( i >= ${#DEVS[@]} )) && break       # one row per GPU per round
  claim "$(row_name "$ROW")" || { echo "skip $(row_name "$ROW") (held)" >> "$OUT/chain-$SLURM_JOB_ID.txt"; continue; }
  work_on "$ROW" "${DEVS[$i]}" & pids[$i]=$!
  i=$(( i + 1 ))
done
for pid in "${pids[@]}"; do wait "$pid" || status=1; done
runs_failed=$status        # a run that stops at the deadline exits 0 (INCOMPLETE); a crash does not
[[ -z "$(git -C "$MINE" status --porcelain)" ]] || status=1

mapfile -t UNFINISHED < <(for r in "${ROWS[@]}"; do is_complete "$(row_name "$r")" || echo x; done)
if (( ${#UNFINISHED[@]} == 0 )); then cancel_next "all COMPLETE"
elif (( runs_failed != 0 )); then cancel_next "a run exited non-zero (exit-codes.txt); fix and resubmit"
fi
echo "status $status" >> "$OUT/chain-$SLURM_JOB_ID.txt"
exit $status
