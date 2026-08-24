#!/bin/bash
#SBATCH -A m3246_g
#SBATCH -q shared
#SBATCH -C gpu
#SBATCH -n 1
#SBATCH -c 32
#SBATCH --gpus-per-task=1
#SBATCH -t 01:30:00
#SBATCH -J c_perm_ens_29
#SBATCH --output=/pscratch/sd/j/josephrb/oi126_r1r3_work/c_perm_ens.%j.log
# sbatch, NOT srun: an srun client dies with the shell that launched it, and this session's ssh
# connection is not a place to hold a 30-minute run. The prior r5/c2 launchers were srun wrappers
# with no #SBATCH directives and had to be EXECUTED, never sbatch'd; this one is the opposite and
# the directives above are why.
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; PET="${REPO}/nd-unfolding/pet"
ANN="${PET}/fullevent_nominal_annealed"; W=/pscratch/sd/j/josephrb/oi126_r1r3_work

# STAMP BEFORE THE WORK, so a job that never started is distinguishable from one that ran and
# failed. A validator that only ever sees the artifact cannot tell those apart.
echo "[stamp] job=${SLURM_JOB_ID} host=$(hostname) started_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "[stamp] producer md5=$(md5sum $W/c_perm_ensemble.py | cut -d' ' -f1)"
echo "[stamp] cluster checkout HEAD=$(git -C $REPO rev-parse --short HEAD 2>/dev/null || echo UNKNOWN)"

module load tensorflow/2.15.0
export MNV_REPO="$REPO"
export PYTHONPATH="${REPO}/omnifold_nn:${REPO}/nd-unfolding:${PET}${PYTHONPATH:+:$PYTHONPATH}"
cd "$PET"

# MNV_REPO IS SET HERE, exactly as the r5 and c2 launchers set it. Recorded because OI-126's
# numbers being reproduced were produced under the same setting, and because the loaded-checkout
# inventory below does NOT currently report it -- that gap is the open item (6).
echo "[stamp] MNV_REPO=${MNV_REPO}  (SET by this launcher, not derived)"

# Routed through the OI-136 guard per AGENTS.md. --expect-root is DELIBERATELY the hardcoded
# cluster root: this run reproduces three published dL values that were produced from that tree
# (its run log recorded roots ['/pscratch/sd/j/josephrb/MINERvA-OmniFold']), so importing from
# anywhere else would invalidate the controls. The guard here CONFIRMS the tree; it is not being
# used to change it.
python3 -u "${REPO}/nd-unfolding/mnv_guarded_run.py" \
  --expect-root "${REPO}" \
  -- $W/c_perm_ensemble.py \
    --nominal-artifact "${ANN}/pet_fullevent_nominal_weights.npz" \
    --replicas-root "${PET}/fullevent_cstat_n50/replicas" \
    --members 29 \
    --n-perms 200 --seed-base 700000 --thr-confirm 2.4e-3 \
    --json $W/OI126_C_PERM_ENS.job${SLURM_JOB_ID}.json
rc=$?
echo "[stamp] child rc=${rc} ended_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
exit $rc
