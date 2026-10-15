#!/bin/bash
#SBATCH --account=m3246
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --output=/pscratch/sd/j/josephrb/2d-closeout-period-unfold-20261014/logs/%x_%j.out
#SBATCH --error=/pscratch/sd/j/josephrb/2d-closeout-period-unfold-20261014/logs/%x_%j.err
# Period-unfold test job (2026-10-14). NOT TO BE SUBMITTED before the director's compute grant record is on main.
# Submitted only by launch.py, which passes --job-name/--qos/--cpus-per-task/--mem/--time from jobs.tsv.
# The job refuses unless its name is exactly one jobs.tsv row and the granted allocation (QOS, CPUs, TimeLimit,
# billing) equals that row. Every path is absolute: sbatch runs a COPY of this script.
# Config = the Stage C closeout config (stageC/pilot/DESIGN.md §2-§3, sbatch_pilot.sh): production driver
# 74a4ed69 with L0's argv (--iters 5 --use-weights --estimator lgbm --bkg-mode purity), 64 CPUs on the shared
# QOS, OMP_NUM_THREADS=64, MKL/OPENBLAS/NUMEXPR=1, LOKY_MAX_CPU_COUNT unset, --branch-select all.
# Only the omnifile, the flux file, --seed and --bootstrap-seed change per row. No `set -u` before the
# root_6_28 activation.
set -eo pipefail
NS=/pscratch/sd/j/josephrb/2d-closeout-period-unfold-20261014
REPO=$NS/code/repo                                  # git archive of main c67dbdda (read only)
TSV=$NS/code/record/scripts/jobs.tsv
NAME=${SLURM_JOB_NAME:?no job name}

# ---- pins ---------------------------------------------------------------------------------------------------------
JOBS_SHA=c2283eb37343780b1b4d3754f8e5dc323480b102ddf9a9d0c13d858b237f5421   # jobs.tsv
PROD_SHA=74a4ed69c3fa9c4ae5b6866f36343212b8d3f903fddde6c7bd40c382c1167d56
HELPER=/pscratch/sd/j/josephrb/MINERvA-OmniFold/unbinned_unfolding/python/omnifold.py   # hard-coded import, :2059-2062
HELPER_SHA=e96234124a31edd7a8dd61fdb16cb48a5b28cbd1b90202f59b0095868378227a
declare -A OMNI_SHA=(
  [ALL]=a7a4bcb359ddb4764e0baf9922ab35e6bfbb3e4e2fd9b03d152514f02ea6b3e9
  [PA]=1d2f5b3712169c2eeca0739a9e391ea05b547153444a23a06a0b7cffa93ac948
  [PB]=200fd1dd18df3f907443caf1217ffbfe580b24e638cbbfff333d39cecfc85004
  [PC]=eedbb5dc0f8bf6d1314e36ccc8f08760f2e59687988db55974ee54d377cc9224
)
declare -A FLUX_SHA=(
  [ALL]=e3dc9e63bc8db07ab545cee6d8b227cdaa7f8249c657cc1a60119020dd6a86de
  [PA]=927f5af214b15935c1093b83c7e703730b8a5993b5e8f43f60a56eb8f07963fe
  [PB]=c64637d58961c4681f83611ab79f057f741329398cde00df175fac28dad15f0d
  [PC]=95c45a5f91f1fc356bfde74b463e1a24a70d698d8693a766773a6a37c3bdfafc
)

# ---- this job's row and its allocation ----------------------------------------------------------------------------
echo "$JOBS_SHA  $TSV" | sha256sum -c -
ROW=$(awk -F'\t' -v n="$NAME" 'NR>1 && $1==n' "$TSV")
[ "$(printf '%s\n' "$ROW" | grep -c .)" = 1 ] || { echo "REFUSE: '$NAME' is not exactly one jobs.tsv row"; exit 4; }
IFS=$'\t' read -r R_NAME R_PERIOD R_SEED R_BSEED R_QOS R_CPUS R_MEM R_TIME R_BILL R_ENF R_EXP R_WHAT <<< "$ROW"
JOBINFO=$(scontrol show job "$SLURM_JOB_ID")
G_QOS=$(grep -o 'QOS=[^ ]*' <<< "$JOBINFO" | head -1 | cut -d= -f2)
G_CPUS=$(grep -o 'NumCPUs=[^ ]*' <<< "$JOBINFO" | head -1 | cut -d= -f2)
G_TIME=$(grep -o 'TimeLimit=[^ ]*' <<< "$JOBINFO" | head -1 | cut -d= -f2)
G_BILL=$(grep -o 'AllocTRES=[^ ]*' <<< "$JOBINFO" | grep -o 'billing=[0-9]*' | head -1 | cut -d= -f2)
[ "$G_QOS" = "$R_QOS" ] || { echo "REFUSE: QOS $G_QOS != $R_QOS"; exit 4; }
[ "$G_CPUS" = "$R_CPUS" ] || { echo "REFUSE: NumCPUs $G_CPUS != $R_CPUS"; exit 4; }
[ "$G_BILL" = "$R_BILL" ] || { echo "REFUSE: billing '$G_BILL' != $R_BILL"; exit 4; }
WANT_TIME=$R_TIME; [ -f "$NS/retries/$NAME.time" ] && WANT_TIME=$(cat "$NS/retries/$NAME.time")
[ "$G_TIME" = "$WANT_TIME" ] || { echo "REFUSE: TimeLimit $G_TIME != $WANT_TIME"; exit 4; }

OMNI=$NS/inputs/runEventLoopOmniFold_${R_PERIOD}.root
FLUX=$NS/flux/runEventLoopMC_${R_PERIOD}.root
OUT=$NS/out/$NAME
[ -e "$OUT/xsec.root" ] && { echo "REFUSE: $OUT/xsec.root exists"; exit 3; }
mkdir -p "$OUT"
[ -z "$(ls -A "$OUT")" ] || { echo "REFUSE: $OUT is not empty"; exit 3; }

source /pscratch/sd/j/josephrb/MINERvA-OmniFold/setup_salloc_env.sh
export TMPDIR=$NS/tmp; mkdir -p "$TMPDIR"
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=64 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
unset LOKY_MAX_CPU_COUNT
echo "[pu] $NAME period=$R_PERIOD seed=$R_SEED bseed=$R_BSEED node=$(hostname) job=$SLURM_JOB_ID qos=$G_QOS cpus=$G_CPUS limit=$G_TIME start=$(date -u +%FT%TZ)"
echo "[pu] affinity cpus: $(python3 -c 'import os; print(len(os.sched_getaffinity(0)))')"
echo "$PROD_SHA  $REPO/2d-unfolding/unfold_2d_omnifold_unbinned.py" | sha256sum -c -
echo "$HELPER_SHA  $HELPER" | sha256sum -c -
echo "${OMNI_SHA[$R_PERIOD]:?unknown period}  $OMNI" | sha256sum -c -
echo "${FLUX_SHA[$R_PERIOD]:?unknown period}  $FLUX" | sha256sum -c -

ARGS=(--omnifile "$OMNI" --mcfile "$FLUX" --iters 5 --use-weights --estimator lgbm --bkg-mode purity
      --seed "$R_SEED" --branch-select all --out "$OUT/xsec.root")
[ "$R_BSEED" != "-" ] && ARGS+=(--bootstrap-seed "$R_BSEED" --bootstrap-streams both)
cd "$REPO/2d-unfolding"
echo "[pu] argv: ${ARGS[*]}"
python3 unfold_2d_omnifold_unbinned.py "${ARGS[@]}"
sha256sum "$OUT/xsec.root"
chmod a-w "$OUT/xsec.root"
echo "[pu] done $NAME $(date -u +%FT%TZ)"
