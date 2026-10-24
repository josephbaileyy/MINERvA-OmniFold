#!/bin/bash
#SBATCH --account=m3246
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
# R10 (ii): the tuple-extraction pass, one srun step through mnv_guarded_run.py (OI-136) from a clean deploy at <pin>:
#   sbatch --qos=<debug|regular> --time=<limit> --job-name=r10_<k> --output=<OUT>/logs/%x_%j.out \
#          sbatch_r10_extract.sh <deploy> <pin> <OUT> <nproc> [playlists, comma-separated; default all twelve]
set -o pipefail   # NOT set -u (the environment's activation aborts under it)
D="${1:?deploy}"; PIN="${2:?pin}"; OUT="${3:?out}"; NPROC="${4:?nproc}"; PLS="${5:-}"
head_sha=$(git -C "$D" rev-parse HEAD 2>/dev/null)
dirty=$(git -C "$D" status --porcelain --untracked-files=no 2>/dev/null | wc -l)
if [ "$head_sha" != "$PIN" ] || [ "$dirty" -ne 0 ]; then
    echo "[r10] refusing: deploy HEAD=$head_sha (pinned $PIN), $dirty modified tracked files" >&2
    exit 2
fi
PY="$HOME/.conda/envs/omnifold_py310/bin/python3"   # uproot and awkward (MP-2 S1's environment)
"$PY" -c "import uproot, awkward, numpy" || { echo "[r10] refusing: $PY lacks uproot/awkward" >&2; exit 2; }
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export TMPDIR="$OUT/tmp"; mkdir -p "$TMPDIR" "$OUT/inventory" "$OUT/extract"
R="$D/docs/orchestration/state/measurement-scoping/r10"
extra=(); [ -n "$PLS" ] && extra=(--playlists "$PLS")
cd "$D" || exit 2
srun -n1 -c "$(nproc)" --job-name=r10_extract \
    "$PY" "$D/nd-unfolding/mnv_guarded_run.py" --expect-root "$D" --inventory "$OUT/inventory/extract-${SLURM_JOB_ID}.jsonl" \
    --label "r10:extract" -- "$R/r10_extract.py" --config "$R/config.json" --out "$OUT/extract" --nproc "$NPROC" "${extra[@]}" \
    > "$OUT/logs/task-extract-${SLURM_JOB_ID}.log" 2>&1
rc=$?
echo "[r10] extract rc=$rc"
exit $rc
