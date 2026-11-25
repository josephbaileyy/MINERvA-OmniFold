#!/bin/bash
#SBATCH --account=m3246
#SBATCH --constraint=cpu
#SBATCH --qos=regular
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
#SBATCH --time=00:30:00
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
# EVW2D: one run of E_R's driver with the per-event weight writer (evw2d.py run). Submitted only by the lane's connect:
#   sbatch --job-name=evw2d --time=00:30:00 sbatch_evw2d.sh <lane root> <deploy_M> <M> <deploy_C> <C> \
#          <evw2d.py sha256> <config.json sha256>
# Before its first write it requires <lane root> and <lane root>/logs to be real directories (no link on the path) and
# every per-job file it will write to be absent; each is then created exclusively (noclobber). It refuses, with a
# recorded reason in logs/DONE-<job>, unless:
#   - the job is named evw2d, is not an array task, and the batch shell's SLURM_JOB_NUM_NODES is 1;
#   - scontrol shows this job with TimeLimit 00:30:00 (the cap) and NumNodes 1 (a pending job prints 1-1; both pass);
#   - deploy_M is a clean checkout at M and deploy_C a clean checkout at C (each git command must itself succeed);
#   - evw2d.py and config.json in deploy_C are the bound bytes, and <lane root>/out is absent;
#   - setup_salloc_env.sh from deploy_M returns 0 and python3 is root_6_28's;
#   - a first, print-only srun step (1 CPU) records SLURM_JOB_NUM_NODES, SLURM_STEP_NUM_NODES, SLURM_STEP_ID and the
#     host in logs/probe-<job>.log, and SLURM_JOB_NUM_NODES there is exactly 1 (evw2d.py's own gate, unchanged).
# Then it runs evw2d.py as ONE step of 64 CPUs in E_R's thread environment (Tier 1's step: srun --exclusive -n1 -c 64).
# evw2d.py writes only under <lane root>/out. This script writes only logs/{job-env,probe,evw2d-run}-<job>.log and
# logs/DONE-<job>.
set -o pipefail   # NOT set -u: it kills setup_salloc_env.sh
set -o noclobber  # every redirect below creates its file exclusively
LANE="${1:?lane root}"; DM="${2:?deploy_M}"; M="${3:?M}"; DC="${4:?deploy_C}"; C="${5:?C}"
WSHA="${6:?evw2d.py sha256}"; CSHA="${7:?config.json sha256}"
L="$LANE/logs"
J="${SLURM_JOB_ID:?not a Slurm job}"
TLIMIT=00:30:00
[ -d "$LANE" ] && [ ! -L "$LANE" ] && [ "$(cd "$LANE" && pwd -P)" = "$LANE" ] || { echo "[evw2d] refusing: lane $LANE" >&2; exit 2; }
[ -d "$L" ] && [ ! -L "$L" ] && [ "$(cd "$L" && pwd -P)" = "$L" ] || { echo "[evw2d] refusing: logs $L" >&2; exit 2; }
for f in "$L/DONE-$J" "$L/job-env-$J.log" "$L/probe-$J.log" "$L/evw2d-run-$J.log"; do
  [ ! -e "$f" ] && [ ! -L "$f" ] || { echo "[evw2d] refusing: $f exists" >&2; exit 2; }
done
refuse() { echo "[evw2d] refusing: $*" >&2; printf '{"rc": 2, "job": "%s", "refused": "%s"}\n' "$J" "$*" > "$L/DONE-$J"; exit 2; }
field() { printf '%s\n' "$1" | tr ' ' '\n' | sed -n "s/^$2=//p" | head -1; }   # one key=value token of scontrol -o
[ "$SLURM_JOB_NAME" = evw2d ] || refuse "job name $SLURM_JOB_NAME"
[ -z "${SLURM_ARRAY_JOB_ID:-}" ] && [ -z "${SLURM_ARRAY_TASK_ID:-}" ] || refuse "an array task"
[ "${SLURM_JOB_NUM_NODES:-}" = 1 ] || refuse "batch shell SLURM_JOB_NUM_NODES=${SLURM_JOB_NUM_NODES:-unset}, not 1"
sj=$(scontrol -o show job "$J" 2>/dev/null) || refuse "scontrol show job $J failed"
tl=$(field "$sj" TimeLimit); nn=$(field "$sj" NumNodes)
[ "$tl" = "$TLIMIT" ] || refuse "scontrol TimeLimit=$tl, not $TLIMIT"
printf '%s' "$nn" | grep -Eq '^1(-1)?$' || refuse "scontrol NumNodes=$nn, not 1"
clean_at() {   # clean_at <checkout> <pin>: HEAD is the pin and status succeeds with no line (each git call checked)
  local h st
  h=$(git -C "$1" rev-parse HEAD 2>/dev/null) || return 1
  st=$(git -C "$1" status --porcelain --ignored 2>/dev/null) || return 1
  [ "$h" = "$2" ] && [ -z "$st" ]
}
clean_at "$DM" "$M" || refuse "deploy_M is not a clean checkout at $M"
clean_at "$DC" "$C" || refuse "deploy_C is not a clean checkout at $C"
W="$DC/2d-unfolding/evw2d/evw2d.py"
CFG="$DC/2d-unfolding/evw2d/config.json"
for f in "$W" "$CFG"; do [ -f "$f" ] && [ ! -L "$f" ] || refuse "$f is not a plain file"; done
wgot=$(sha256sum "$W" | cut -d' ' -f1); [ "$wgot" = "$WSHA" ] || refuse "evw2d.py sha256 $wgot is not the bound $WSHA"
cgot=$(sha256sum "$CFG" | cut -d' ' -f1); [ "$cgot" = "$CSHA" ] || refuse "config.json sha256 $cgot is not the bound $CSHA"
[ ! -e "$LANE/out" ] && [ ! -L "$LANE/out" ] || refuse "$LANE/out exists"
echo "[evw2d] job=$J host=$(hostname) start=$(date -u +%FT%TZ) M=$M C=$C TimeLimit=$tl NumNodes=$nn"
set +o noclobber   # the setup runs as REF-C2C1's and Tier 1's did; only this script's own redirects are exclusive
source "$DM/setup_salloc_env.sh" > "$L/job-env-$J.log" 2>&1
src_rc=$?
set -o noclobber
echo "[evw2d] setup_salloc_env.sh rc=$src_rc python3=$(command -v python3)"
[ "$src_rc" -eq 0 ] || refuse "setup_salloc_env.sh returned $src_rc"
[ "$(command -v python3)" = "$HOME/.conda/envs/root_6_28/bin/python3" ] || refuse "python3 is not root_6_28's"
# the print-only step: the format of the node count inside an srun step goes on record before the wrapper runs
srun --exclusive -n1 -c 1 --mem=1G bash -c 'echo "host=$(hostname)"; for v in SLURM_JOB_NUM_NODES SLURM_STEP_NUM_NODES SLURM_STEP_ID SLURM_NNODES; do echo "$v=${!v-<unset>}"; done' \
  > "$L/probe-$J.log" 2>&1
prc=$?
cat "$L/probe-$J.log"
[ "$prc" -eq 0 ] || refuse "the print-only step returned $prc"
pnn=$(sed -n 's/^SLURM_JOB_NUM_NODES=//p' "$L/probe-$J.log")
[ "$pnn" = 1 ] || refuse "the srun step's SLURM_JOB_NUM_NODES is '$pnn', not 1 (see probe-$J.log)"
export OMP_NUM_THREADS=64 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
srun --exclusive -n1 -c 64 --mem=200G \
    python3 -B "$W" --config-sha256 "$CSHA" run --out "$LANE/out" > "$L/evw2d-run-$J.log" 2>&1
rc=$?
n=$(git -C "$DM" status --porcelain --ignored | wc -l | tr -d ' '); clean_at "$DM" "$M" || n="unclean"
cn=$(git -C "$DC" status --porcelain --ignored | wc -l | tr -d ' '); clean_at "$DC" "$C" || cn="unclean"
printf '{"rc": %s, "job": "%s", "deploy_M_porcelain_ignored_after": "%s", "deploy_C_porcelain_ignored_after": "%s"}\n' \
  "$rc" "$J" "$n" "$cn" > "$L/DONE-$J"
echo "[evw2d] done rc=$rc end=$(date -u +%FT%TZ)"
exit $rc
