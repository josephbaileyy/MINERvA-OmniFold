#!/bin/bash
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
#SBATCH -t 00:50:00
#SBATCH -J ibuchi_t1
#SBATCH -o /pscratch/sd/j/josephrb/ibuchi-evloop-20261123/logs/t1_%j.out
#SBATCH -e /pscratch/sd/j/josephrb/ibuchi-evloop-20261123/logs/t1_%j.err
# Tier 1: er and c2_central on OLD and paper (E) pT edges, four concurrent units at 64 CPUs (REF-C2C1's centrals form).
# Reads tier1/stage and the deploys; writes only under tier1/units_* and tier1/logs.
set -o pipefail
R=/pscratch/sd/j/josephrb/ibuchi-evloop-20261123; T=$R/tier1; PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
for d in old e; do [ ! -e $T/units_$d ] || { echo "REFUSED: units_$d exists"; exit 2; }; done
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate "$HOME/.conda/envs/root_6_28" || exit 2
export TMPDIR=$T/tmp PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=64 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
mkdir -p $TMPDIR $T/logs
echo "[t1] start $(date -u +%FT%TZ) job=$SLURM_JOB_ID node=$(hostname) nproc=$(nproc)"
pids=""
for d in old e; do for u in er c2_central; do
  ( cd $T/deploy_$d && srun --exclusive -n1 -c 64 --mem=110G --job-name=${u}_$d \
      /usr/bin/time -v -o $T/logs/${u}_$d.time $PY -B 2d-unfolding/ref_c2c1/ref_c2c1.py --unit $u --out $T/units_$d \
      > $T/logs/${u}_$d.log 2>&1 ) &
  pids="$pids $!"
done; done
rcs=""; for p in $pids; do wait $p; rcs="$rcs $?"; done
echo "[t1] done $(date -u +%FT%TZ) rcs:$rcs"
for d in old e; do for u in er c2_central; do echo "$d $u: $(cat $T/units_$d/$u.done 2>/dev/null)"; done; done
sha256sum $T/units_*/* 2>/dev/null
