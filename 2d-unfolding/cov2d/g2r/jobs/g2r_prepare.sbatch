#!/bin/bash
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
#SBATCH --output=/pscratch/sd/j/josephrb/cov2d-g2r-20261112/logs/%x-%j.out
# COV2D-G2R's prepare (declaration section 6 step 1; addendum J1): g2r_prepare.py in omnifold_py310 (uproot, as
# COV2D's step A read $UNI), on $UNI and P5's 12 per-playlist omnifiles, every read through O_NOATIME. It writes
# $O/prepare/g2r_map.npz and g2r_prepare.json. Its exit code passes through: 0 PASS, 5 INVALID, 7 the director's
# STOP (a per-playlist file missing), 8 an atime moved. 2 and 4 are this script's own refusals (deploy, Slurm, $UNI).
set -eo pipefail
source "$C/2d-unfolding/cov2d/g2r/jobs/g2r_env.sh"
JOBS=$O/tables/jobs_g2r.tsv
[ ! -e "$O/prepare" ] || { echo "[g2r] $O/prepare exists: a prepare rerun is a new connect"; exit 3; }
g2r_deploy_ok "$C" "$M" || { echo "[g2r] deploy $C is not a clean checkout at $M"; exit 2; }
g2r_slurm_ok "$(awk -F'\t' 'NR > 1 && $1 == "prepare" {print $7}' "$JOBS")"
export TMPDIR=$O/tmp/$SLURM_JOB_ID PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
mkdir -p "$TMPDIR" "$O/logs"
"$PY310" -B "$CJ" uni-stat || { echo "[g2r] \$UNI is not part B's file"; exit 4; }
"$PY310" -B -c "import numpy, uproot, sys; print('python', sys.version.split()[0], 'numpy', numpy.__version__, 'uproot', uproot.__version__)"
echo "[g2r] start $(date -u +%FT%TZ) job=$SLURM_JOB_ID prepare node=$(hostname)"
rc=0
# shellcheck disable=SC2086  # P5_BLOCKS is a space-separated list of fixed paths
"$PY310" -B "$C/2d-unfolding/cov2d/g2r/g2r_prepare.py" --omnifile "$UNI" --blocks $P5_BLOCKS --out "$O/prepare" || rc=$?
(cd "$O/prepare" && sha256sum g2r_map.npz g2r_prepare.json 2>/dev/null) || true
echo "[g2r] end $(date -u +%FT%TZ) rc=$rc"
exit $rc
