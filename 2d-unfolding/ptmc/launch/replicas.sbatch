#!/bin/bash
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=5
#SBATCH --exclusive
#SBATCH --no-requeue
#SBATCH -J ptmc_reps
#SBATCH -o /pscratch/sd/j/josephrb/ptmc-20261128/logs/replicas_%j.out
#SBATCH -e /pscratch/sd/j/josephrb/ptmc-20261128/logs/replicas_%j.err
# PTMC replicas (PTMC-DECLARATION.md section 7): R replicas b = 2..200 on 5 nodes, 4 lanes of 64 CPUs each and up to 10
# units per lane in sequence, each unit its own named srun step. The time limit is set on the sbatch command line (L,
# from the pilot's post); none is written here. The job refuses (2) unless its allocation is exactly 5 nodes and its
# time limit is exactly the authorized L. A unit's failure does not stop its lane (the others are independent); every
# unit's outcome goes to this job's own record directory, and the job fails (6) unless all 199 are recorded as 0.
set -u -o pipefail
R=/pscratch/sd/j/josephrb/ptmc-20261128; O=$R/tool/2d-unfolding/ptmc
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
ROWS_SHA=cbf34bd8cad0f4978dc1aea22713eb5057bf521118dc7ce8d10b93b30defcb03
refuse() { echo "[ptmc_reps] REFUSED: $*"; exit 2; }
minutes() {  # a Slurm time limit ([D-]HH:MM:SS, MM:SS or MM) in whole minutes, rounded up; anything else fails
  local t=$1 d=0 h=0 m s=0
  case "$t" in *-*) d=${t%%-*}; t=${t#*-};; esac
  IFS=: read -r a b c <<< "$t"
  if [ -n "${c:-}" ]; then h=$a; m=$b; s=$c; elif [ -n "${b:-}" ]; then m=$a; s=$b; else m=$a; fi
  for v in "$d" "$h" "$m" "$s"; do case "$v" in ''|*[!0-9]*) return 1;; esac; done
  echo $(( 10#$d * 1440 + 10#$h * 60 + 10#$m + (10#$s > 0 ? 1 : 0) ))
}
[ "${SLURM_JOB_NUM_NODES:-}" = 5 ] || refuse "the allocation has '${SLURM_JOB_NUM_NODES:-}' nodes, not 5"
[ -e $R/pilot-post/PROCEED ] && [ -d $R/units ] || refuse "no PROCEED from the pilot's post"
L=$(cat $R/pilot-post/time_limit_minutes) || refuse "no authorized time limit"
case "$L" in ''|*[!0-9]*) refuse "the authorized time limit '$L'";; esac
tl=$(squeue -h -j "$SLURM_JOB_ID" -o %l) || refuse "squeue failed"
tm=$(minutes "$tl") || refuse "the job's time limit '$tl' does not parse"
[ "$tm" -ge 1 ] && [ "$tm" = "$L" ] || refuse "the job's time limit is $tm minutes; the authorized L is $L"
rk=$(cat $R/replicas-check/recheck.json) || refuse "no recheck record"  # the fresh recheck at submit, not only the file (B1)
[ "$rk" = "{\"recheck\": \"SAME\", \"time_limit_minutes\": $L}" ] || refuse "the recheck record does not authorize L = $L: $rk"
# one allocation per recheck (confirm-3 B1): this job claims it exclusively (noclobber is O_EXCL) before any lane starts
CLAIM=$R/replicas-check/recheck.claim
if ! ( set -C; printf '%s\n' "${SLURM_JOB_ID:-}" > "$CLAIM" ) 2>/dev/null; then
  held=$(cat "$CLAIM") || refuse "the recheck claim exists and cannot be read"
  [ "$held" = "${SLURM_JOB_ID:-}" ] || refuse "the recheck is claimed by job '$held'; this is job ${SLURM_JOB_ID:-}"
fi
hook=$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook) \
  || refuse "the conda hook failed"
eval "$hook" || refuse "the conda hook did not evaluate"
conda activate "$HOME/.conda/envs/root_6_28" || refuse "conda activate"
export TMPDIR=$R/tmp PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=64 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
mkdir -p "$TMPDIR" || refuse "mkdir $TMPDIR"
REC=$R/logs/replicas-$SLURM_JOB_ID
mkdir $REC || refuse "mkdir $REC"
ROWS=$R/stage/oofvc_rows.npz; JOIN=$R/stage/join.json
SHA=$(cat $R/stage/rows.sha256) || refuse "rows.sha256 unreadable"
[ "$SHA" = "$ROWS_SHA" ] || refuse "rows.sha256 is not the pinned rows"
echo "[ptmc_reps] start $(date -u +%FT%TZ) job=$SLURM_JOB_ID nodes=$SLURM_JOB_NODELIST limit=${tm}m L=${L}m"
# 20 lanes; lane l (0..19) takes b = 2 + l + 20 k for k = 0..9 while b <= 200 (199 units in all)
lane() {
  local l=$1 b k rc
  for k in 0 1 2 3 4 5 6 7 8 9; do
    b=$((2 + l + 20 * k)); [ "$b" -le 200 ] || break
    srun --exclusive -N1 -n1 -c 64 --mem=110G --job-name=p_R_b$b /usr/bin/time -v -o $R/logs/p_R_b$b.time \
      $PY -B $O/ptmc_run.py --tree $R/deploy --rows $ROWS --rows-sha256 $SHA --join-record $JOIN \
      --out $R/units --unit p_R_b$b > $R/logs/p_R_b$b.log 2>&1
    rc=$?
    echo "p_R_b$b $rc" >> $REC/lane_$l || return 3
  done
  return 0
}
LANES="0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19"  # literal: no substitution can leave a lane out
declare -A pid_of
for l in $LANES; do lane $l & pid_of[$l]=$!; done
bad=0
for l in $LANES; do
  wait "${pid_of[$l]}"; rc=$?
  echo "lane $l $rc" >> $REC/lanes || bad=1
  [ "$rc" = 0 ] || bad=1
done
echo "[ptmc_reps] done $(date -u +%FT%TZ)"
cat $REC/lanes $REC/lane_* 2>/dev/null
n=$(cat $REC/lane_* | awk '$2 == "0" {print $1}' | sort -u | wc -l) || n=-1
t=$(cat $REC/lane_* | wc -l) || t=-1
nl=$(awk '$1 == "lane" && $3 == "0" {print $2}' $REC/lanes | sort -u | wc -l) || nl=-1
[ "$bad" = 0 ] && [ "$n" = 199 ] && [ "$t" = 199 ] && [ "$nl" = 20 ] \
  || { echo "[ptmc_reps] FAIL: $n of 199 units succeeded ($t recorded), $nl of 20 lanes"; exit 6; }
exit 0
