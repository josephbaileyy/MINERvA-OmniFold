#!/bin/bash
#SBATCH --account=m3246
#SBATCH --constraint=cpu
#SBATCH --qos=regular
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
# EVW5D: configuration (e)'s central per-event weights (evw5d.py). Submitted only by the lane's connect:
#   sbatch --job-name=evw5d --time=00:30:00 sbatch_evw5d.sh <deploy at the code pin> <code pin> <OUT> <tool clone> <tool pin>
# The job refuses unless its name is evw5d, its Slurm limit 30:00, the deploy a clean clone at the code pin, the tool
# clone a clean clone at the tool pin, and <OUT>/evw5d absent. It sources the deploy's setup_salloc_env.sh (root_6_28 by
# prefix), then runs evw5d.py as ONE step of 32 CPUs (srun --exact), as the producer's step and the ESS run did
# (sbatch_ess.sh). evw5d.py stages the shared inputs through O_NOATIME into /dev/shm and removes them; it writes only
# under <OUT>/evw5d. This script writes only <OUT>/logs/{job-env,evw5d-run}-<job>.log and <OUT>/logs/DONE-<job>.
set -o pipefail   # NOT set -u: it kills setup_salloc_env.sh
D="${1:?deploy}"; PIN="${2:?pin}"; OUT="${3:?out}"; TC="${4:?tool clone}"; TPIN="${5:?tool pin}"
L="$OUT/logs"
J="${SLURM_JOB_ID:?not a Slurm job}"
refuse() { echo "[evw5d] refusing: $*" >&2; echo "{\"rc\": 2, \"job\": \"$J\", \"refused\": \"$*\"}" > "$L/DONE-$J"; exit 2; }
[ "$SLURM_JOB_NAME" = evw5d ] || refuse "job name $SLURM_JOB_NAME"
tl=$(squeue -h -j "$J" -o %l 2>/dev/null)
[ "$tl" = "30:00" ] || refuse "TimeLimit $tl is not 30:00"
head_sha=$(git -C "$D" rev-parse HEAD 2>/dev/null)
dirty=$(git -C "$D" status --porcelain --ignored 2>/dev/null | wc -l)
[ "$head_sha" = "$PIN" ] && [ "$dirty" -eq 0 ] || refuse "deploy HEAD=$head_sha (pinned $PIN), $dirty porcelain --ignored lines"
t_sha=$(git -C "$TC" rev-parse HEAD 2>/dev/null)
t_dirty=$(git -C "$TC" status --porcelain --ignored 2>/dev/null | wc -l)
[ "$t_sha" = "$TPIN" ] && [ "$t_dirty" -eq 0 ] || refuse "tool HEAD=$t_sha (pinned $TPIN), $t_dirty porcelain --ignored lines"
[ ! -e "$OUT/evw5d" ] || refuse "$OUT/evw5d exists"
[ ! -e "/dev/shm/evw5d-$J" ] || refuse "/dev/shm/evw5d-$J exists"
echo "[evw5d] job=$J host=$(hostname) start=$(date -u +%FT%TZ) pin=$PIN tool=$TPIN"
source "$D/setup_salloc_env.sh" > "$L/job-env-$J.log" 2>&1
echo "[evw5d] setup_salloc_env.sh rc=$? python3=$(command -v python3)"
[ "$(command -v python3)" = "$HOME/.conda/envs/root_6_28/bin/python3" ] || refuse "python3 is not root_6_28's"
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
srun --ntasks=1 --cpus-per-task=32 --mem=160G --exact \
    python3 -B "$TC/nd-unfolding/evw5d/evw5d.py" --deploy "$D" --out "$OUT/evw5d" --out-root "$OUT" \
    --stage-dir "/dev/shm/evw5d-$J" > "$L/evw5d-run-$J.log" 2>&1
rc=$?
left=$([ -e "/dev/shm/evw5d-$J" ] && echo true || echo false)
n=$(git -C "$D" status --porcelain --ignored | wc -l)
tn=$(git -C "$TC" status --porcelain --ignored | wc -l)
echo "{\"rc\": $rc, \"job\": \"$J\", \"deploy_porcelain_ignored_after\": $n, \"tool_porcelain_ignored_after\": $tn, \"stage_dir_left\": $left}" > "$L/DONE-$J"
echo "[evw5d] done rc=$rc end=$(date -u +%FT%TZ)"
exit $rc
