#!/bin/bash
#SBATCH -A m3246_g
#SBATCH -q shared
#SBATCH -C gpu
#SBATCH -n 1
#SBATCH -c 32
#SBATCH --gpus-per-task=1
#SBATCH -t 03:00:00
#SBATCH -J c_perm_ens5
#SBATCH --output=/pscratch/sd/j/josephrb/oi126_r1r3_work/c_perm_ens5.%j.log
# Five sequential invocations in ONE job. NOT `set -e` around them: one member failing must not
# discard the other four, so each rc is captured and the job's own status is decided at the end.
set -o pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; PET="${REPO}/nd-unfolding/pet"
ANN="${PET}/fullevent_nominal_annealed"; W=/pscratch/sd/j/josephrb/oi126_r1r3_work

echo "[stamp] job=${SLURM_JOB_ID} host=$(hostname) started_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "[stamp] producer md5=$(md5sum $W/c_perm_ensemble.py | cut -d' ' -f1)"
echo "[stamp] cluster HEAD=$(git -C $REPO rev-parse --short HEAD 2>/dev/null || echo UNKNOWN)"

module load tensorflow/2.15.0
export MNV_REPO="$REPO"
export PYTHONPATH="${REPO}/omnifold_nn:${REPO}/nd-unfolding:${PET}${PYTHONPATH:+:$PYTHONPATH}"
cd "$PET"
echo "[stamp] MNV_REPO=${MNV_REPO} (SET by this launcher)"

# ORDER IS DELIBERATE: 45 and 26 are the two members whose R5 row-set cells read
# THRESHOLD-INDETERMINATE at 4.40x and 3.74x the bar, i.e. the two this run exists to settle. They go
# FIRST so a wall-time overrun or a late failure costs the reassuring members, not the load-bearing
# ones. 29 is already done and is not repeated.
#            member  pub_a                   pub_b                   pub_c1
MEMBERS=(
  "45  3.1343936708524429e-02  4.1905347306676319e-02  4.0122424790736036e-02"
  "26  3.1159530322085752e-02  4.0134197413279504e-02  3.6594046809757114e-02"
  "49  5.1987684477000909e-03  6.8083070758372492e-03  6.9986100549278233e-03"
  "0   2.6487677076978917e-02  2.8785022068929342e-02  2.8025290174934749e-02"
  "43  2.3656075769052078e-02  2.4564329122162332e-02  2.2964960197946291e-02"
)
FAILED=""
for row in "${MEMBERS[@]}"; do
  set -- $row
  m=$1; pa=$2; pb=$3; pc=$4
  tag=$(printf "replica_%02d" "$m")
  echo ""
  echo "=============================================================================="
  echo "[stamp] ${tag} starting $(date -u +%H:%M:%SZ)  pub_a=${pa} pub_b=${pb} pub_c1=${pc}"
  echo "=============================================================================="
  python3 -u "${REPO}/nd-unfolding/mnv_guarded_run.py" \
    --expect-root "${REPO}" \
    -- $W/c_perm_ensemble.py \
      --nominal-artifact "${ANN}/pet_fullevent_nominal_weights.npz" \
      --replicas-root "${PET}/fullevent_cstat_n50/replicas" \
      --members "$m" \
      --pub-a "$pa" --pub-b "$pb" --pub-c1 "$pc" \
      --n-perms 200 --seed-base 700000 --thr-confirm 2.4e-3 \
      --json "$W/OI126_C_PERM_ENS5.job${SLURM_JOB_ID}.${tag}.json"
  rc=$?
  echo "[stamp] ${tag} rc=${rc} ended $(date -u +%H:%M:%SZ)"
  [ $rc -ne 0 ] && FAILED="${FAILED} ${tag}:${rc}"
done
echo ""
echo "[stamp] all members attempted. FAILED=[${FAILED:- none}] ended_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
[ -n "$FAILED" ] && exit 1
exit 0
