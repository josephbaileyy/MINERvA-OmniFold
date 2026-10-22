#!/bin/bash
#SBATCH --job-name=re1-nd
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --time=00:56:00
#SBATCH --output=/pscratch/sd/j/josephrb/methods-paper/re1-20261022/logs/%x-%j.out
# RE-1 run 2, job 2: six data unfolds at once, each deterministic LightGBM at 32 threads (num_threads fixed),
# estimator seed 42: K1 (P5 rerun), P5c, P3, P3c, P4, P4c. Projected 0.75 h; the limit is 1.25x.
set -eo pipefail
source "$C/docs/orchestration/state/2d-closeout/stageF/methods/re1/run2/launch/re1_env.sh"
re1_preflight
for p in "$NPZ5D $NPZ5D_SHA" "$BKG5D $BKG5D_SHA" "$P5 $P5_SHA"; do re1_check $p; done
(cd "$O" && sha256sum -c SHA256SUMS.inputs)
sha() { sha256sum "$1" | cut -d' ' -f1; }
mkdir -p "$O/5d"
echo "[re1] start $(date -u +%FT%TZ) job=$SLURM_JOB_ID node=$(hostname)"
run() {  # run <label> <dim> <npz> <bkg> <e|c>
    local label=$1 d=$2 npz=$3 bkg=$4 arm=$5
    local args="--npz $npz --bkg $bkg --expect-npz-sha256 $(sha $npz) --expect-bkg-sha256 $(sha $bkg) --data \
        --estimator-seed 42 --threads 32 --iters 5 --out $O/${d}d/$label.npz"
    if [ "$arm" = e ]; then
        srun -n1 -c 42 --exact --cpu-bind=cores bash -c "$(declare -f re1_py); C=$C O=$O; \
            re1_py $label nd-unfolding/s5e_candidate.py --candidate R -- $args --bkg-mode negweight-refined" \
            > "$O/${d}d/$label.log" 2>&1 &
    else
        srun -n1 -c 42 --exact --cpu-bind=cores bash -c "$(declare -f re1_py); C=$C O=$O; \
            re1_py $label nd-unfolding/s5n_pseudo.py $args --bkg-mode purity" > "$O/${d}d/$label.log" 2>&1 &
    fi
}
run k1_p5_rerun 5 "$NPZ5D" "$BKG5D" e; pids="$!"
run p5c 5 "$NPZ5D" "$BKG5D" c;        pids="$pids $!"
for d in 3 4; do
    run p${d} $d "$O/${d}d/of_inputs_${d}d.npz" "$O/${d}d/bkg_${d}d.npz" e;  pids="$pids $!"
    run p${d}c $d "$O/${d}d/of_inputs_${d}d.npz" "$O/${d}d/bkg_${d}d.npz" c; pids="$pids $!"
done
rc=0
for pid in $pids; do wait "$pid" || rc=1; done
(cd "$O" && sha256sum 5d/k1_p5_rerun.npz 5d/p5c.npz 3d/p3.npz 3d/p3c.npz 4d/p4.npz 4d/p4c.npz > SHA256SUMS.nd) || rc=1
echo "[re1] end $(date -u +%FT%TZ) rc=$rc"
exit $rc
