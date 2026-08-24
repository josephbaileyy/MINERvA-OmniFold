#!/bin/bash
set -eo pipefail
REPO="/pscratch/sd/j/josephrb/MINERvA-OmniFold"; PET="${REPO}/nd-unfolding/pet"
ANN="${PET}/fullevent_nominal_annealed"; W=/pscratch/sd/j/josephrb/oi126_r1r3_work
module load tensorflow/2.15.0
export MNV_REPO="$REPO"
export PYTHONPATH="${REPO}/omnifold_nn:${REPO}/nd-unfolding:${PET}${PYTHONPATH:+:$PYTHONPATH}"
cd "$PET"
srun -A m3246_g -q interactive -C gpu -N1 -n1 -c32 --gpus=1 -t 60 \
  python3 -u $W/r5_c2_discriminator.py \
    --nominal-artifact "${ANN}/pet_fullevent_nominal_weights.npz" \
    --replicas-root "${PET}/fullevent_cstat_n50/replicas" \
    --member 29 --c1-seed 12345 --c2-seed 987654321 \
    --sweep-json $W/OI126_R5_SWEEP.json \
    --json $W/OI126_R5_C2.$(date -u +%Y%m%dT%H%M%SZ).json
