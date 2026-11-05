#!/bin/bash
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
#SBATCH --time=03:00:00
#SBATCH --output=/pscratch/sd/j/josephrb/cov2d-run-20261104/logs/%x-%j.out
# COV2D's pseudo-data job for $TRUTH (COV2D-DECLARATION.md sections 4.2, 8, 9.4, 9.6, 9.11): step A in omnifold_py310
# (one read of $UNI through O_NOATIME: counts, truths, records; section 9.6 and the director's R1 counts stop it before
# any count is written), then step B in the pinned MAT environment (root_6_28 + MAT: section 9.4 first, then the 301
# data files through the bound writer, each read back, and the truths). One node, 3 node-h reserved; above it is REPRICE.
set -eo pipefail
source "$C/2d-unfolding/cov2d/jobs/cov2d_env.sh"
P=$O/pseudo/$TRUTH
[ ! -e "$P" ] || { echo "[cov2d] $P exists: a pseudo-data rerun is a new connect"; exit 3; }
mkdir -p "$O/pseudo" "$O/logs"
[ "$(git -C "$C" rev-parse HEAD)" = "$M" ] && [ -z "$(git -C "$C" status --porcelain)" ] || { echo "[cov2d] deploy"; exit 2; }
info=$(scontrol show job "$SLURM_JOB_ID")
grep -q "QOS=regular" <<<"$info" && grep -q "TimeLimit=03:00:00 " <<<"$info" || { echo "[cov2d] QOS or TimeLimit"; exit 2; }
# the E3 resets before step A too (J4): nothing inherited from the submitting shell
export TMPDIR=$O/tmp/$SLURM_JOB_ID PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=64 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
mkdir -p "$TMPDIR"
"$PY310" -B "$CJ" uni-stat || { echo "[cov2d] \$UNI is not part B's file (J2)"; exit 4; }
echo "[cov2d] start $(date -u +%FT%TZ) job=$SLURM_JOB_ID TRUTH=$TRUTH node=$(hostname)"
"$PY310" -B "$C/2d-unfolding/cov2d/cov2d_pseudo.py" --truth "$TRUTH" --out "$P/a" || { echo "[cov2d] step A rc=$?"; exit 5; }
cov2d_preflight                       # the pinned MAT environment for step B (its flux file is a MINERvA file)
python -B "$C/2d-unfolding/cov2d/cov2d_pseudo_write.py" --a "$P/a" --out "$P/b" || { echo "[cov2d] step B rc=$?"; exit 6; }
echo "[cov2d] end $(date -u +%FT%TZ)"
