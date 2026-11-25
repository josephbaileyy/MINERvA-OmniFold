#!/bin/bash
#SBATCH --account=m3246
#SBATCH --constraint=cpu
#SBATCH --qos=regular
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
# EVW5D: configuration (e)'s central per-event weights (evw5d.py). Submitted only by the lane's connect:
#   sbatch --job-name=evw5d --time=00:30:00 sbatch_evw5d.sh <deploy at the code pin> <code pin> <OUT> <tool clone> \
#          <tool pin> <evw5d.py sha256>
# Before its first write it requires <OUT> and <OUT>/logs to be real directories (no link on the path) and every
# per-job file it will write to be absent; each is then created exclusively (noclobber). The job refuses unless its
# name is evw5d, its Slurm limit 30:00, the deploy a clean clone at the code pin and the tool clone a clean clone at the
# tool pin (each git command must itself succeed), evw5d.py's bytes equal the bound sha256, setup_salloc_env.sh returns
# 0, and <OUT>/evw5d is absent. It sources the deploy's setup_salloc_env.sh (root_6_28 by
# prefix), then runs evw5d.py as ONE step of 32 CPUs (srun --exact), as the producer's step and the ESS run did
# (sbatch_ess.sh). evw5d.py stages the shared inputs through O_NOATIME into /dev/shm and removes them; it writes only
# under <OUT>/evw5d. This script writes only <OUT>/logs/{job-env,evw5d-run}-<job>.log and <OUT>/logs/DONE-<job>.
set -o pipefail   # NOT set -u: it kills setup_salloc_env.sh
set -o noclobber  # every redirect below creates its file exclusively
D="${1:?deploy}"; PIN="${2:?pin}"; OUT="${3:?out}"; TC="${4:?tool clone}"; TPIN="${5:?tool pin}"; WSHA="${6:?evw5d.py sha256}"
L="$OUT/logs"
J="${SLURM_JOB_ID:?not a Slurm job}"
# the output root and its log directory: real directories, reached through no link, before the first write
[ -d "$OUT" ] && [ ! -L "$OUT" ] && [ "$(cd "$OUT" && pwd -P)" = "$OUT" ] || { echo "[evw5d] refusing: OUT $OUT" >&2; exit 2; }
[ -d "$L" ] && [ ! -L "$L" ] && [ "$(cd "$L" && pwd -P)" = "$L" ] || { echo "[evw5d] refusing: logs $L" >&2; exit 2; }
for f in "$L/DONE-$J" "$L/job-env-$J.log" "$L/evw5d-run-$J.log"; do
  [ ! -e "$f" ] && [ ! -L "$f" ] || { echo "[evw5d] refusing: $f exists" >&2; exit 2; }
done
refuse() { echo "[evw5d] refusing: $*" >&2; echo "{\"rc\": 2, \"job\": \"$J\", \"refused\": \"$*\"}" > "$L/DONE-$J"; exit 2; }
[ "$SLURM_JOB_NAME" = evw5d ] || refuse "job name $SLURM_JOB_NAME"
[ -z "${SLURM_ARRAY_JOB_ID:-}" ] && [ -z "${SLURM_ARRAY_TASK_ID:-}" ] || refuse "an array task"
[ "${SLURM_JOB_NUM_NODES:-}" = 1 ] || refuse "SLURM_JOB_NUM_NODES=${SLURM_JOB_NUM_NODES:-unset}, not 1"
tl=$(squeue -h -j "$J" -o %l 2>/dev/null)
[ "$tl" = "30:00" ] || refuse "TimeLimit $tl is not 30:00"
clean_at() {   # clean_at <checkout> <pin>: HEAD is the pin and status succeeds with no line (each git call checked)
  local h st
  h=$(git -C "$1" rev-parse HEAD 2>/dev/null) || return 1
  st=$(git -C "$1" status --porcelain --ignored 2>/dev/null) || return 1
  [ "$h" = "$2" ] && [ -z "$st" ]
}
clean_at "$D" "$PIN" || refuse "the deploy is not a clean checkout at $PIN"
clean_at "$TC" "$TPIN" || refuse "the tool clone is not a clean checkout at $TPIN"
W="$TC/nd-unfolding/evw5d/evw5d.py"
[ -f "$W" ] && [ ! -L "$W" ] || refuse "evw5d.py is not a plain file"
wgot=$(sha256sum "$W" | cut -d' ' -f1)
[ "$wgot" = "$WSHA" ] || refuse "evw5d.py sha256 $wgot is not the bound $WSHA"
[ ! -e "$OUT/evw5d" ] || refuse "$OUT/evw5d exists"
[ ! -e "/dev/shm/evw5d-$J" ] || refuse "/dev/shm/evw5d-$J exists"
echo "[evw5d] job=$J host=$(hostname) start=$(date -u +%FT%TZ) pin=$PIN tool=$TPIN"
source "$D/setup_salloc_env.sh" > "$L/job-env-$J.log" 2>&1
src_rc=$?
echo "[evw5d] setup_salloc_env.sh rc=$src_rc python3=$(command -v python3)"
[ "$src_rc" -eq 0 ] || refuse "setup_salloc_env.sh returned $src_rc"
[ "$(command -v python3)" = "$HOME/.conda/envs/root_6_28/bin/python3" ] || refuse "python3 is not root_6_28's"
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
srun --ntasks=1 --cpus-per-task=32 --mem=160G --exact \
    python3 -B "$W" --deploy "$D" --out "$OUT/evw5d" --out-root "$OUT" \
    --stage-dir "/dev/shm/evw5d-$J" > "$L/evw5d-run-$J.log" 2>&1
rc=$?
left=$([ -e "/dev/shm/evw5d-$J" ] && echo true || echo false)
n=$(git -C "$D" status --porcelain --ignored | wc -l); clean_at "$D" "$PIN" || n="unclean"
tn=$(git -C "$TC" status --porcelain --ignored | wc -l); clean_at "$TC" "$TPIN" || tn="unclean"
echo "{\"rc\": $rc, \"job\": \"$J\", \"deploy_porcelain_ignored_after\": \"$n\", \"tool_porcelain_ignored_after\": \"$tn\", \"stage_dir_left\": $left}" > "$L/DONE-$J"
echo "[evw5d] done rc=$rc end=$(date -u +%FT%TZ)"
exit $rc
