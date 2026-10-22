#!/bin/bash
#SBATCH --job-name=re1-2d
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --time=02:11:00
#SBATCH --output=/pscratch/sd/j/josephrb/methods-paper/re1-20261022/logs/%x-%j.out
# RE-1 run 2, job 3: the 2D data unfolds (K1 purity, D2 refined) and the C2 pseudo-experiments, seeds 1-20,
# both arms each. Four streams of 64 CPUs; LightGBM's default thread count is the stream's affinity (64,
# as the XR L0 regeneration of E_U). Projected 1.75 h; the limit is 1.25x.
set -eo pipefail
source "$C/docs/orchestration/state/2d-closeout/stageF/methods/re1/run2/launch/re1_env.sh"
re1_preflight
(cd "$O" && sha256sum -c SHA256SUMS.inputs)
CACHE=$O/2d/cache.npz; CSHA=$(sha256sum "$CACHE" | cut -d' ' -f1)
export OMP_NUM_THREADS=64
echo "[re1] start $(date -u +%FT%TZ) job=$SLURM_JOB_ID node=$(hostname)"
stream() {  # stream <label> <commands...>: one srun step of 64 CPUs running its commands in order
    local label=$1; shift
    srun -n1 -c 64 --exact --cpu-bind=cores bash -c "$(declare -f re1_py); C=$C O=$O; set -e; $*" \
        > "$O/2d/$label.log" 2>&1 &
}
R2="re1_py"
D="2d-unfolding/re1/re1_2d.py"
stream s1 "$R2 k1_2d $D data --cache $CACHE --expect-cache-sha256 $CSHA --arm purity --out $O/2d/k1_data_purity.npz; \
           $R2 d2_2d $D data --cache $CACHE --expect-cache-sha256 $CSHA --arm refined --out $O/2d/d2_data_refined.npz; \
           $R2 c2_s1 $D pseudo --cache $CACHE --expect-cache-sha256 $CSHA --pseudo-seeds 1:4 --out $O/2d/c2"
pids="$!"
stream s2 "$R2 c2_s2 $D pseudo --cache $CACHE --expect-cache-sha256 $CSHA --pseudo-seeds 5:10 --out $O/2d/c2"; pids="$pids $!"
stream s3 "$R2 c2_s3 $D pseudo --cache $CACHE --expect-cache-sha256 $CSHA --pseudo-seeds 11:15 --out $O/2d/c2"; pids="$pids $!"
stream s4 "$R2 c2_s4 $D pseudo --cache $CACHE --expect-cache-sha256 $CSHA --pseudo-seeds 16:20 --out $O/2d/c2"; pids="$pids $!"
rc=0
for pid in $pids; do wait "$pid" || rc=1; done
(cd "$O" && sha256sum 2d/k1_data_purity.npz 2d/d2_data_refined.npz 2d/c2/nominal_s*.npz > SHA256SUMS.2d) || rc=1
echo "[re1] end $(date -u +%FT%TZ) rc=$rc"
exit $rc
