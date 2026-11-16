#!/bin/bash
#SBATCH --account=m3246
#SBATCH --constraint=cpu
#SBATCH --qos=regular
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
# The ESS rerun of configuration (e)'s central data unfold (ess_capture.py). Submitted only by the lane's connect:
#   sbatch --job-name=ess_e --time=00:30:00 sbatch_ess.sh <deploy at the code pin> <code pin> <OUT> <tool dir>
# The job refuses unless its name is ess_e, its Slurm limit 30:00, the deploy a clean clone at the pin, and <OUT>/ess
# absent. It sources the deploy's setup_salloc_env.sh (root_6_28 by prefix), then runs ess_capture.py as ONE step of
# 32 CPUs (srun --exact), as the producer's step ran (s5c_steps.sh @ 8af5d746: --cpus-per-task 32, threads 32).
# ess_capture.py stages the shared inputs through O_NOATIME into /dev/shm and removes them; it writes only under
# <OUT>/ess. This script writes only <OUT>/logs/{job-env,ess-run}-<job>.log and <OUT>/logs/DONE-<job>.
set -o pipefail   # NOT set -u: it kills setup_salloc_env.sh
D="${1:?deploy}"; PIN="${2:?pin}"; OUT="${3:?out}"; T="${4:?tool dir}"
L="$OUT/logs"
J="${SLURM_JOB_ID:?not a Slurm job}"
refuse() { echo "[ess] refusing: $*" >&2; echo "{\"rc\": 2, \"job\": \"$J\", \"refused\": \"$*\"}" > "$L/DONE-$J"; exit 2; }
[ "$SLURM_JOB_NAME" = ess_e ] || refuse "job name $SLURM_JOB_NAME"
tl=$(squeue -h -j "$J" -o %l 2>/dev/null)
[ "$tl" = "30:00" ] || refuse "TimeLimit $tl is not 30:00"
head_sha=$(git -C "$D" rev-parse HEAD 2>/dev/null)
dirty=$(git -C "$D" status --porcelain --ignored 2>/dev/null | wc -l)
[ "$head_sha" = "$PIN" ] && [ "$dirty" -eq 0 ] || refuse "deploy HEAD=$head_sha (pinned $PIN), $dirty porcelain --ignored lines"
[ ! -e "$OUT/ess" ] || refuse "$OUT/ess exists"
[ ! -e "/dev/shm/ess-$J" ] || refuse "/dev/shm/ess-$J exists"
echo "[ess] job=$J host=$(hostname) start=$(date -u +%FT%TZ) pin=$PIN"
source "$D/setup_salloc_env.sh" > "$L/job-env-$J.log" 2>&1
echo "[ess] setup_salloc_env.sh rc=$? python3=$(command -v python3)"
[ "$(command -v python3)" = "$HOME/.conda/envs/root_6_28/bin/python3" ] || refuse "python3 is not root_6_28's"
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
srun --ntasks=1 --cpus-per-task=32 --mem=80G --exact \
    python3 "$T/ess_capture.py" --deploy "$D" --out "$OUT/ess" --out-root "$OUT" --stage-dir "/dev/shm/ess-$J" \
    > "$L/ess-run-$J.log" 2>&1
rc=$?
left=$([ -e "/dev/shm/ess-$J" ] && echo true || echo false)
n=$(git -C "$D" status --porcelain --ignored | wc -l)
echo "{\"rc\": $rc, \"job\": \"$J\", \"deploy_porcelain_ignored_after\": $n, \"stage_dir_left\": $left}" > "$L/DONE-$J"
echo "[ess] done rc=$rc end=$(date -u +%FT%TZ)"
exit $rc
