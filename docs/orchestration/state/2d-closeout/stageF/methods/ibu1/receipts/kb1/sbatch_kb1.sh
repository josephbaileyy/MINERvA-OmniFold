#!/bin/bash
#SBATCH --account=m3246
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
# IBU-1 control K-B1 (BINDING-C.md ruling 2): recompute one kept B1 seed of each partial line with the bound code
# into a scratch products directory, through the same guard and deploy as job C.
set -o pipefail
D=/pscratch/sd/j/josephrb/ibu1-20261022/deploy/7ea30e3d; PIN=7ea30e3dbb98cfff67ef07314fcfe04fded81e4c
K=/pscratch/sd/j/josephrb/ibu1-20261022/kb1
[ "$(git -C "$D" rev-parse HEAD)" = "$PIN" ] && [ "$(git -C "$D" status --porcelain --untracked-files=no | wc -l)" -eq 0 ] || { echo refusing; exit 2; }
source "$D/setup_salloc_env.sh" > "$K/logs/env-${SLURM_JOB_ID}.log" 2>&1
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export TMPDIR="$K/tmp"; mkdir -p "$TMPDIR" "$K/inventory" "$K/products"
NPZ=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz
BKG=/pscratch/sd/j/josephrb/s5c-20260924/runs/p2/bkg_dump.npz
cd "$D" || exit 2
pids=()
for spec in N_nominal_val:300285 N_gibuu:301100; do
    unit=${spec%%:*}; seed=${spec##*:}
    srun --exclusive -n1 -c 2 --mem=11G --job-name="kb1_$unit" \
        python3 "$D/nd-unfolding/mnv_guarded_run.py" --expect-root "$D" --inventory "$K/inventory/$unit.jsonl" \
        --label "ibu1:kb1:$unit" -- "$D/nd-unfolding/ibu1/ibu1.py" --npz "$NPZ" --bkg "$BKG" --out "$K/products" \
        --unit "$unit" --seeds "$seed:$seed" > "$K/logs/task-kb1_$unit-${SLURM_JOB_ID}.log" 2>&1 &
    pids+=($!)
done
rc=0; for p in "${pids[@]}"; do wait "$p" || rc=1; done
echo "[kb1] done rc=$rc"; exit $rc
