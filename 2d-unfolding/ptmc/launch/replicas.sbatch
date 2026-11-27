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
# from the pilot's post); none is written here, so a submit without -t is refused by the launcher, never defaulted.
# A unit's failure does not stop its lane (the others are independent); the lane's return codes are recorded.
set -o pipefail
R=/pscratch/sd/j/josephrb/ptmc-20261128; O=$R/tool/2d-unfolding/ptmc
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
[ -e $R/pilot-post/PROCEED ] && [ -d $R/units ] || { echo "REFUSED: no PROCEED from the pilot's post"; exit 2; }
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate "$HOME/.conda/envs/root_6_28" || exit 2
export TMPDIR=$R/tmp PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=64 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
ROWS=$R/stage/oofvc_rows.npz; JOIN=$R/stage/join.json; SHA=$(cat $R/stage/rows.sha256)
echo "[ptmc_reps] start $(date -u +%FT%TZ) job=$SLURM_JOB_ID nodes=$SLURM_JOB_NODELIST"
# 20 lanes; lane l (0..19) takes seeds 2 + l, 22 + l, ..., i.e. b = 2 + l + 20 k for k = 0..9 while b <= 200
lane() {
  local l=$1 b rc out=""
  for k in 0 1 2 3 4 5 6 7 8 9; do
    b=$((2 + l + 20 * k)); [ "$b" -le 200 ] || break
    srun --exclusive -N1 -n1 -c 64 --mem=110G --job-name=p_R_b$b /usr/bin/time -v -o $R/logs/p_R_b$b.time \
      $PY -B $O/ptmc_run.py --tree $R/deploy --rows $ROWS --rows-sha256 $SHA --join-record $JOIN \
      --out $R/units --unit p_R_b$b > $R/logs/p_R_b$b.log 2>&1
    rc=$?; out="$out b$b:$rc"
  done
  echo "lane $l:$out" > $R/logs/lane_$l.rcs
}
pids=""
for l in $(seq 0 19); do lane $l & pids="$pids $!"; done
for p in $pids; do wait $p; done
echo "[ptmc_reps] done $(date -u +%FT%TZ)"
cat $R/logs/lane_*.rcs
grep -q ':[1-9]' $R/logs/lane_*.rcs && { echo "[ptmc_reps] FAIL: a unit failed"; exit 6; }
exit 0
