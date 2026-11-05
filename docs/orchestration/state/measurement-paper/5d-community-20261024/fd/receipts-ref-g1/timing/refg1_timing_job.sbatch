#!/bin/bash
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
# REF-G1 step two, the timing unit (REF-G1-BINDING-2.md ruling 3): ONE universe unit, universe:Flux:0, by the bound
# driver at M from a fresh clean clone, with -B, under the exact interpreter ruling 2 names, 32 threads (config.json
# resources.max_threads_per_task). Porcelain, with --ignored, is recorded before and after. The unit's product goes to
# <O>/units, outside the deploy. Arguments: <deploy> <O>. Writes only under <O>.
set -o pipefail   # NOT set -u
C="${1:?deploy}"; O="${2:?out}"
M=609d8f24ea2229fa4b3540627aa8c31acfcc0a54
PY=/global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3
[ "$O" = /pscratch/sd/j/josephrb/ref-g1-20261105/timing ] || { echo "[refg1t] refusing: O is $O"; exit 2; }
[ "$(git -C "$C" rev-parse HEAD)" = "$M" ] || { echo "[refg1t] refusing: deploy HEAD is not M"; exit 2; }
nb=$(git -C "$C" status --porcelain --ignored | wc -l); echo "[refg1t] porcelain --ignored lines before: $nb"
[ "$nb" -eq 0 ] || { echo "[refg1t] refusing: the deploy is not clean"; exit 2; }
echo "[refg1t] start $(date -u +%FT%TZ) job=$SLURM_JOB_ID node=$(hostname) nproc=$(nproc)"
source "$C/setup_salloc_env.sh" > "$O/env.log" 2>&1   # root_6_28, as the s5p and RE-2 jobs source it
export TMPDIR=$O/tmp PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=32 MKL_NUM_THREADS=32 OPENBLAS_NUM_THREADS=32 NUMEXPR_NUM_THREADS=32
mkdir -p "$TMPDIR" "$O/units"
echo "[refg1t] interpreter $PY: $("$PY" -c 'import sys; print(sys.version.replace(chr(10), " "))')"
t0=$(date +%s.%N)
/usr/bin/time -v -o "$O/unit.time" "$PY" -B "$C/nd-unfolding/ref_g1/ref_g1.py" --unit universe:Flux:0 --out "$O/units" \
    --threads 32 > "$O/unit.log" 2>&1
rc=$?
t1=$(date +%s.%N)
echo "[refg1t] unit rc=$rc wall_s=$(awk -v a=$t0 -v b=$t1 'BEGIN{printf "%.1f", b-a}') end=$(date -u +%FT%TZ)"
grep -E 'Elapsed|Maximum resident|Exit status' "$O/unit.time"
tail -3 "$O/unit.log"
na=$(git -C "$C" status --porcelain --ignored | wc -l); echo "[refg1t] porcelain --ignored lines after: $na"
git -C "$C" status --porcelain --ignored | head -10
exit $rc
