#!/bin/bash
# Generic guarded task for the PET final-design study: runs ONE entry point of a clean checkout
# pinned at MINE_COMMIT through nd-unfolding/mnv_guarded_run.py (OI-136), writing the guard
# inventory beside the outputs. Simulation only; the entry point enforces its own scope.
#   env: MINE (pinned checkout) MINE_COMMIT OUT LABEL ; args: <entry.py relative to MINE> [args...]
#   Submit with the QOS/constraint on the sbatch command line, e.g.
#   sbatch -A m3246 -C cpu -q debug -N 1 -t 00:30:00 --export=ALL,MINE=..,MINE_COMMIT=..,OUT=..,LABEL=.. \
#          sbatch_guarded_task.sh nd-unfolding/pet/final_design/diagnostics/build_row_features.py --inventory ...
#SBATCH --job-name=pfd-task
set -eo pipefail
: "${MINE:?}" ; : "${MINE_COMMIT:?}" ; : "${OUT:?}" ; : "${LABEL:?}"
case "$(realpath -m "$OUT")" in
  /pscratch/sd/j/josephrb/pet-final-design-20260925/*) ;;
  *) echo "OUT must be under the study namespace" >&2; exit 2;;
esac
[[ "$(git -C "$MINE" rev-parse HEAD)" == "$MINE_COMMIT" ]] || { echo "checkout not at $MINE_COMMIT" >&2; exit 2; }
[[ -z "$(git -C "$MINE" status --porcelain)" ]] || { echo "checkout not clean" >&2; exit 2; }
mkdir -p "$OUT"
export PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
module load tensorflow/2.15.0
ENTRY="$MINE/$1"; shift
echo "$(date -u +%FT%TZ) job ${SLURM_JOB_ID:-none} host $(hostname) entry $ENTRY commit $MINE_COMMIT" >> "$OUT/task-${LABEL}.log"
/usr/bin/time -v python "$MINE/nd-unfolding/mnv_guarded_run.py" --expect-root "$MINE" \
  --inventory "$OUT/guard-${LABEL}-${SLURM_JOB_ID:-none}.json" --label "$LABEL" -- \
  "$ENTRY" "$@" >> "$OUT/task-${LABEL}.log" 2>&1
echo "$(date -u +%FT%TZ) exit 0" >> "$OUT/task-${LABEL}.log"
