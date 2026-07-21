#!/bin/bash
# Orchestrate the 4D unified throw inside the held interactive allocation (54190938),
# per the /goal (sbatch backlogged). 8 parallel srun --overlap workers, each
# OMP_NUM_THREADS=16 so LightGBM (n_jobs=-1) sees 16 cores -> no oversubscription
# (8x16=128). Monitor by the slab npzs. Phases: throws -> block -> combine.
set -uo pipefail
cd /pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding
JID=54190938
S=uq_4d/uthrow_slabs_4d
run() { srun --jobid=$JID --overlap -n1 --cpus-per-task=16 --export=ALL,OMP_NUM_THREADS=16,MKL_NUM_THREADS=16 "$@"; }

echo "[4dthrow] PHASE 1 throws $(date -u +%T)"
for w in 0 1 2 3 4 5 6 7; do
  off=$((w*20))
  run python3 unified_throw_cov.py --throws 20 --throw-offset $off --seed 1000       --bank bank_uthrow_4d --iters 5 --out $S/uthrow4d_slab_$w.npz       > $S/throw_$w.log 2>&1 &
done
wait
echo "[4dthrow] PHASE 1 done $(date -u +%T); slabs: $(ls $S/uthrow4d_slab_*.npz 2>/dev/null | wc -l)"

echo "[4dthrow] PHASE 2 block units $(date -u +%T)"
KN=("2p2h,CCQEPauliSupViaKF" "FrAbs_pi,FrElas_N" "HighQ2,LowQ2" "MaCCQE,MaRES" "MFP_N,MvRES" "Rvn2pi,Rvp2pi")
for t in 0 1 2 3 4 5; do
  run python3 unified_throw_cov.py --blockunits --bank bank_uthrow_4d --iters 5 --seed 1000       --block-knobs "${KN[$t]}" --out $S/block4d_$t.npz > $S/block_$t.log 2>&1 &
done
run python3 unified_throw_cov.py --blockunits --bank bank_uthrow_4d --iters 5 --seed 1000     --block-knobs none --block-flux 0-5 --out $S/block4d_f0.npz > $S/block_f0.log 2>&1 &
run python3 unified_throw_cov.py --blockunits --bank bank_uthrow_4d --iters 5 --seed 1000     --block-knobs none --block-flux 6-11 --out $S/block4d_f1.npz > $S/block_f1.log 2>&1 &
wait
echo "[4dthrow] PHASE 2 done $(date -u +%T); blocks: $(ls $S/block4d_*.npz 2>/dev/null | wc -l)"

echo "[4dthrow] PHASE 3 combine $(date -u +%T)"
run python3 unified_throw_cov.py --combine "$S/uthrow4d_slab_*.npz" --expected-throws 0-159     --block-slabs "$S/block4d_*.npz" --bank bank_uthrow_4d --iters 5 --null     --out-root uq_4d/unified_throw_cov_4d.root > uq_4d/uthrow4d_combine.log 2>&1
echo "[4dthrow] ALL DONE $(date -u +%T)"
