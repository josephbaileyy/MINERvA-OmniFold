#!/bin/bash
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
#SBATCH -t 00:45:00
#SBATCH -J oofvc_units
#SBATCH -o /pscratch/sd/j/josephrb/oofvc-20261126/logs/units_%j.out
#SBATCH -e /pscratch/sd/j/josephrb/oofvc-20261126/logs/units_%j.err
# OOFVC step 2 on one node: the join (a STOP writes no rows, and no unit runs), then the four units concurrently, each
# in its own srun step of 64 CPUs (Tier 1's t1.sbatch form, E_R's thread environment). Writes only under $R.
set -o pipefail
R=/pscratch/sd/j/josephrb/oofvc-20261126; O=$R/tool/2d-unfolding/oofvc
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
SPLIT=$R/tool/docs/orchestration/state/ibu-chi2-20261123/oflow/split.json
[ ! -e $R/join ] && [ ! -e $R/units ] || { echo "REFUSED: join or units exists"; exit 2; }
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate "$HOME/.conda/envs/root_6_28" || exit 2
export TMPDIR=$R/tmp PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=64 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
mkdir -p $TMPDIR
echo "[oofvc_units] start $(date -u +%FT%TZ) job=$SLURM_JOB_ID node=$(hostname) nproc=$(nproc)"
srun -n1 -c 64 --mem=200G /usr/bin/time -v -o $R/logs/join.time $PY -B $O/oofvc_join.py \
  --omnifile $R/stage/runEventLoopOmniFold_MEFHC.root --dump-dir $R/dump --split $SPLIT --out $R/join \
  > $R/logs/join.log 2>&1
rc=$?; echo "[oofvc_units] join rc=$rc $(date -u +%FT%TZ)"; tail -3 $R/logs/join.log
[ $rc = 0 ] || exit 8
ROWS=$R/stage/oofvc_rows.npz
cp $R/join/oofvc_rows.npz $ROWS && chmod a-w $ROWS || exit 3
SHA=$(sha256sum < $ROWS | cut -d' ' -f1)
[ "$SHA" = "$($PY -c "import json,sys; print(json.load(open(sys.argv[1]))['rows_sha256'])" $R/join/join.json)" ] \
  || { echo "REFUSED: the staged rows are not the join's"; exit 3; }
pids=""
for u in off/er off/c2_central R/er R/c2_central; do
  tag=${u/\//-}
  ( srun --exclusive -n1 -c 64 --mem=110G --job-name=$tag /usr/bin/time -v -o $R/logs/$tag.time \
      $PY -B $O/oofvc_run.py --tree $R/deploy --rows $ROWS --rows-sha256 $SHA --out $R/units --unit $u \
      > $R/logs/$tag.log 2>&1 ) &
  pids="$pids $!"
done
rcs=""; for p in $pids; do wait $p; rcs="$rcs $?"; done
echo "[oofvc_units] units done $(date -u +%FT%TZ) rcs:$rcs"
sha256sum $R/units/*/* $R/units/pins_*.json $R/join/* 2>/dev/null
for r in $rcs; do [ "$r" = 0 ] || { echo "[oofvc_units] FAIL: a unit returned $r"; exit 6; }; done
exit 0
