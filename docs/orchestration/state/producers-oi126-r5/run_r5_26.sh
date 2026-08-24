#!/bin/bash
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; PET="${REPO}/nd-unfolding/pet"
ANN="${PET}/fullevent_nominal_annealed"; W=/pscratch/sd/j/josephrb/oi126_r1r3_work
module load tensorflow/2.15.0
export MNV_REPO="$REPO"
export PYTHONPATH="${REPO}/omnifold_nn:${REPO}/nd-unfolding:${PET}${PYTHONPATH:+:$PYTHONPATH}"
cd "$PET"
echo "[r5-26] single-member rescue run for replica_26 (the aggregation-ambiguity span)"
srun -A m3246_g -q interactive -C gpu -N1 -n1 -c32 --gpus=1 -t 120 \
  python3 -u $W/r5_sweep.py \
    --nominal-artifact "${ANN}/pet_fullevent_nominal_weights.npz" \
    --replicas-root "${PET}/fullevent_cstat_n50/replicas" \
    --members 26 --added-members 26 \
    --loss-domain heldout --thr-confirm 2.4e-3 --thr-opposite 2.4e-2 \
    --json $W/OI126_R5_SWEEP_26.json
