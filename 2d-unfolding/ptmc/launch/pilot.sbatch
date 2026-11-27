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
set -o pipefail
R=/pscratch/sd/j/josephrb/ptmc-20261128; O=$R/tool/2d-unfolding/ptmc
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
[ -e $R/stage/ready ] && [ ! -e $R/units ] || { echo "REFUSED: the stage is not ready, or units exists"; exit 2; }
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate "$HOME/.conda/envs/root_6_28" || exit 2
export TMPDIR=$R/tmp PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=64 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
mkdir -p $TMPDIR $R/units
ROWS=$R/stage/oofvc_rows.npz; JOIN=$R/stage/join.json; SHA=$(cat $R/stage/rows.sha256)
echo "[ptmc_pilot] start $(date -u +%FT%TZ) job=$SLURM_JOB_ID nodes=$SLURM_JOB_NODELIST"
pids=""
for u in p_off_c p_R_c p_off_b1 p_R_b1 p_off_b2 p_off_b3 p_off_b4 p_off_b5; do
  ( srun --exclusive -N1 -n1 -c 64 --mem=110G --job-name=$u /usr/bin/time -v -o $R/logs/$u.time \
      $PY -B $O/ptmc_run.py --tree $R/deploy --rows $ROWS --rows-sha256 $SHA --join-record $JOIN \
      --out $R/units --unit $u > $R/logs/$u.log 2>&1 ) &
  pids="$pids $!"
done
rcs=""; for p in $pids; do wait $p; rcs="$rcs $?"; done
echo "[ptmc_pilot] done $(date -u +%FT%TZ) rcs:$rcs"
for r in $rcs; do [ "$r" = 0 ] || { echo "[ptmc_pilot] FAIL: a unit returned $r"; exit 6; }; done
exit 0
