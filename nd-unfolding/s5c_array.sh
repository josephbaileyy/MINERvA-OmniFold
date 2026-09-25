#!/bin/bash
# s5c campaign array task: run line ${SLURM_ARRAY_TASK_ID} of a committed task table.
#
# Submitted only through nd-unfolding/s5c_meter.py, which sets the job name, account, QOS, time
# limit, array range and --no-requeue. Usage (as the sbatch script):
#   s5c_array.sh <deploy_tree> <pinned_sha> <task_table.tsv> <out_dir>
# A task-table line is: <task_name><TAB><entrypoint relative to nd-unfolding/><TAB><args...>
# The literal token {OUT} in args is replaced by <out_dir>/<task_name>.npz.
#
# Refuses (exit 2) unless the deploy tree is a clean checkout at exactly <pinned_sha>, so the
# executing bytes are the committed bytes. Every python entrypoint runs under mnv_guarded_run.py
# (OI-136: imports must resolve inside the deploy tree), with a per-task inventory record.
# An existing product is never overwritten; a task whose product exists exits 0 as a resume skip.

DEPLOY=${1:?deploy tree}
PIN=${2:?pinned sha}
TABLE=${3:?task table}
OUT=${4:?out dir}
TASK=${SLURM_ARRAY_TASK_ID:?not an array task}

head_sha=$(git -C "$DEPLOY" rev-parse HEAD 2>/dev/null)
dirty=$(git -C "$DEPLOY" status --porcelain --untracked-files=no 2>/dev/null | wc -l)
if [ "$head_sha" != "$PIN" ] || [ "$dirty" -ne 0 ]; then
    echo "[s5c] refusing: deploy HEAD=$head_sha (pinned $PIN), $dirty modified tracked files" >&2
    exit 2
fi

line=$(grep -v '^#' "$TABLE" | grep -v '^[[:space:]]*$' | sed -n "$((TASK + 1))p")
if [ -z "$line" ]; then
    echo "[s5c] refusing: no task line $TASK in $TABLE" >&2
    exit 2
fi
name=$(printf '%s' "$line" | cut -f1)
entry=$(printf '%s' "$line" | cut -f2)
args=$(printf '%s' "$line" | cut -f3- | tr '\t' ' ')
mkdir -p "$OUT/inventory" "$OUT/logs"
product="$OUT/$name.npz"
if [ -e "$product" ]; then
    echo "[s5c] $name: product exists, resume skip"
    exit 0
fi
args=${args//\{OUT\}/$product}

# Environment first, never under set -u, never piped (a piped source runs in a subshell).
source "$DEPLOY/setup_salloc_env.sh" > "$OUT/logs/$name.env.log" 2>&1
case "$(python3 -V 2>&1)" in
    *3.11*) ;;
    *) echo "[s5c] refusing: environment did not activate ($(python3 -V 2>&1))" >&2; exit 2 ;;
esac
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

cd "$DEPLOY" || exit 2   # repo-relative task arguments resolve against the pinned tree
echo "[s5c] task=$TASK name=$name job=${SLURM_JOB_ID} host=$(hostname) start=$(date -u +%FT%TZ)"
set -f   # task arguments may carry quoted globs meant for the program (e.g. --combine 'dir/*.npz')
# shellcheck disable=SC2086
python3 "$DEPLOY/nd-unfolding/mnv_guarded_run.py" --expect-root "$DEPLOY" \
    --inventory "$OUT/inventory/$name.jsonl" --label "s5c:$name" -- \
    "$DEPLOY/nd-unfolding/$entry" $args
rc=$?
echo "[s5c] task=$TASK name=$name rc=$rc end=$(date -u +%FT%TZ)"
exit $rc
