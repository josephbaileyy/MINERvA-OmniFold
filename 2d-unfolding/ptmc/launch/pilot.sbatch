#!/bin/bash
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=2
#SBATCH --exclusive
#SBATCH --no-requeue
#SBATCH -t 01:00:00
#SBATCH -J ptmc_pilot
#SBATCH -o /pscratch/sd/j/josephrb/ptmc-20261128/logs/pilot_%j.out
#SBATCH -e /pscratch/sd/j/josephrb/ptmc-20261128/logs/pilot_%j.err
# PTMC pilot (PTMC-DECLARATION.md sections 2.3 and 7): the 8 pilot units on 2 nodes, 4 lanes of 64 CPUs each, every
# unit its own named srun step (one unit per lane), E_R's thread environment. Writes only under $R/units and $R/logs.
# Every gate fails closed: an allocation other than 2 nodes, a failed activation, mkdir or read, or a unit's non-zero
# status is a refusal (2) or a failure (6). Every lane's status is collected and recorded.
set -u -o pipefail
R=/pscratch/sd/j/josephrb/ptmc-20261128; O=$R/tool/2d-unfolding/ptmc
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
ROWS_SHA=cbf34bd8cad0f4978dc1aea22713eb5057bf521118dc7ce8d10b93b30defcb03
UNITS="p_off_c p_R_c p_off_b1 p_R_b1 p_off_b2 p_off_b3 p_off_b4 p_off_b5"
refuse() { echo "[ptmc_pilot] REFUSED: $*"; exit 2; }
minutes() {  # a Slurm time limit ([D-]HH:MM:SS, MM:SS or MM) in whole minutes, rounded up; anything else fails
  local t=$1 d=0 h=0 m s=0
  case "$t" in *-*) d=${t%%-*}; t=${t#*-};; esac
  IFS=: read -r a b c <<< "$t"
  if [ -n "${c:-}" ]; then h=$a; m=$b; s=$c; elif [ -n "${b:-}" ]; then m=$a; s=$b; else m=$a; fi
  for v in "$d" "$h" "$m" "$s"; do case "$v" in ''|*[!0-9]*) return 1;; esac; done
  echo $(( 10#$d * 1440 + 10#$h * 60 + 10#$m + (10#$s > 0 ? 1 : 0) ))
}
[ "${SLURM_JOB_NUM_NODES:-}" = 2 ] || refuse "the allocation has '${SLURM_JOB_NUM_NODES:-}' nodes, not 2"
tl=$(squeue -h -j "${SLURM_JOB_ID:-}" -o %l) || refuse "squeue failed"
tm=$(minutes "$tl") || refuse "the job's time limit '$tl' does not parse"
[ "$tm" = 60 ] || refuse "the job's time limit is $tm minutes, not 60 (ptmc_remote.sh's -t 60)"
[ -e $R/stage/ready ] || refuse "the stage is not ready"
[ ! -e $R/units ] || refuse "units exists"
hook=$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook) \
  || refuse "the conda hook failed"
eval "$hook" || refuse "the conda hook did not evaluate"
conda activate "$HOME/.conda/envs/root_6_28" || refuse "conda activate"
export TMPDIR=$R/tmp PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=64 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
mkdir -p "$TMPDIR" || refuse "mkdir $TMPDIR"
mkdir $R/units || refuse "mkdir units"
REC=$R/logs/pilot-$SLURM_JOB_ID
mkdir $REC || refuse "mkdir $REC"
ROWS=$R/stage/oofvc_rows.npz; JOIN=$R/stage/join.json
SHA=$(cat $R/stage/rows.sha256) || refuse "rows.sha256 unreadable"
[ "$SHA" = "$ROWS_SHA" ] || refuse "rows.sha256 is not the pinned rows"
echo "[ptmc_pilot] start $(date -u +%FT%TZ) job=$SLURM_JOB_ID nodes=$SLURM_JOB_NODELIST"
declare -A pid_of
for u in $UNITS; do
  srun --exclusive -N1 -n1 -c 64 --mem=110G --job-name=$u /usr/bin/time -v -o $R/logs/$u.time \
    $PY -B $O/ptmc_run.py --tree $R/deploy --rows $ROWS --rows-sha256 $SHA --join-record $JOIN \
    --out $R/units --unit $u > $R/logs/$u.log 2>&1 &
  pid_of[$u]=$!
done
bad=0
for u in $UNITS; do
  wait "${pid_of[$u]}"; rc=$?
  echo "$u $rc" >> $REC/outcomes || { echo "[ptmc_pilot] FAIL: the outcome of $u could not be recorded"; bad=1; }
  [ "$rc" = 0 ] || bad=1
done
echo "[ptmc_pilot] done $(date -u +%FT%TZ)"
cat $REC/outcomes
n=$(awk '$2 == "0"' $REC/outcomes | wc -l) || n=-1
[ "$bad" = 0 ] && [ "$n" = 8 ] || { echo "[ptmc_pilot] FAIL: $n of 8 units succeeded"; exit 6; }
exit 0
