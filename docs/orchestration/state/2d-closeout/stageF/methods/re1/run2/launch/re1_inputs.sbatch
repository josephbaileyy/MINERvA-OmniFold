#!/bin/bash
#SBATCH --job-name=re1-inputs
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --time=01:52:00
#SBATCH --output=/pscratch/sd/j/josephrb/methods-paper/re1-20261022/logs/%x-%j.out
# RE-1 run 2, job 1: the cached 2D arrays and the 3D/4D npz inputs with their background dumps, three
# chains at once. Projected 1.5 h; the limit is 1.25x the projection.
set -eo pipefail
source "$C/docs/orchestration/state/2d-closeout/stageF/methods/re1/run2/launch/re1_env.sh"
re1_preflight
mkdir -p "$O/2d" "$O/3d" "$O/4d" "$O/inventory"
for p in "$OMNI2D $OMNI2D_SHA" "$FLUX $FLUX_SHA" "$OMNI3D $OMNI3D_SHA" "$OMNI4D $OMNI4D_SHA"; do re1_check $p; done
echo "[re1] start $(date -u +%FT%TZ) job=$SLURM_JOB_ID node=$(hostname)"
srun -n1 -c 16 --exact --cpu-bind=cores bash -c "$(declare -f re1_py); C=$C O=$O; re1_py dump2d 2d-unfolding/re1/re1_2d.py dump \
    --omnifile $OMNI2D --mcfile $FLUX --expect-omnifile-sha256 $OMNI2D_SHA --expect-mcfile-sha256 $FLUX_SHA \
    --out $O/2d/cache.npz" > "$O/2d/dump.log" 2>&1 &
p2=$!
for d in 3 4; do
    omni=OMNI${d}D; axes=$([ $d = 3 ] && echo eavail || echo eavail,q3)
    srun -n1 -c 16 --exact --cpu-bind=cores bash -c "$(declare -f re1_py); C=$C O=$O; set -e; \
        re1_py dump${d}d nd-unfolding/nn_dump_inputs.py --omnifile ${!omni} --mcfile $FLUX --axes $axes \
            --out $O/${d}d/of_inputs_${d}d.npz; \
        re1_py bkg${d}d nd-unfolding/s5c_dump_bkg.py --omnifile ${!omni} --npz $O/${d}d/of_inputs_${d}d.npz \
            --out $O/${d}d/bkg_${d}d.npz" > "$O/${d}d/dump.log" 2>&1 &
    eval "p$d=\$!"
done
rc=0
for d in 2 3 4; do pid=p$d; wait ${!pid} || { echo "[re1] chain ${d}D rc=$?"; rc=1; }; done
(cd "$O" && sha256sum 2d/cache.npz 3d/of_inputs_3d.npz 3d/bkg_3d.npz 4d/of_inputs_4d.npz 4d/bkg_4d.npz > SHA256SUMS.inputs) || rc=1
echo "[re1] end $(date -u +%FT%TZ) rc=$rc"
exit $rc
