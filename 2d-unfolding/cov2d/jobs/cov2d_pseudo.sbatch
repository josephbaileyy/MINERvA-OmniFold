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
echo "[cov2d] start $(date -u +%FT%TZ) job=$SLURM_JOB_ID TRUTH=$TRUTH node=$(hostname)"
TMPDIR=$O/tmp/$SLURM_JOB_ID PYTHONDONTWRITEBYTECODE=1 "$PY310" -B "$C/2d-unfolding/cov2d/cov2d_pseudo.py" \
    --truth "$TRUTH" --out "$P/a" || { echo "[cov2d] step A rc=$?"; exit 5; }
cov2d_preflight                       # the pinned MAT environment for step B (its flux file is a MINERvA file)
python -B "$C/2d-unfolding/cov2d/cov2d_pseudo_write.py" --a "$P/a" --out "$P/b" || { echo "[cov2d] step B rc=$?"; exit 6; }
echo "[cov2d] end $(date -u +%FT%TZ)"
