#!/bin/bash
#SBATCH --job-name=oi160-tol
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=36 --mem=64G
#SBATCH --time=01:05:00
#SBATCH --array=0-5
#SBATCH --no-requeue
# OI-160 tolerance run (DECLARATION.md beside this file). Submitted from the deploy clone as
#   sbatch --output=$T/logs/%A_%a.out --error=$T/logs/%A_%a.err --export=NONE,T=$T,D=$D run_array.sh
# Task 0: the fresh same-code control, seed 1, 07c18aee's bootstrap_nd.py twice.
# Tasks 1-5: one graded seed each (seeds.tsv), 07c18aee's then 07c18aee^'s bootstrap_nd.py.
# Reads the canonical checkout's input and stored replicas READ-ONLY; writes only under $T.
set -o pipefail
: "${T:?T (the run directory under pscratch) is required}"
: "${D:?D (the deploy clone at the pin) is required}"
: "${SLURM_ARRAY_TASK_ID:?an array task id is required}"
K=$SLURM_ARRAY_TASK_ID
N=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding
PY="env -u PYTHONPATH /global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3 -I -B"
H=$D/docs/orchestration/state/oi160-tolerance-20261029
R=$D/docs/orchestration/state/oi160-reproduction-20261029/repro_run.py
W=$T/work/t$K; L=$T/logs; O=$T/out
mkdir -p "$W/A" "$W/B" "$W/lib" "$L" "$O" "$T/tmp/t$K"
export TMPDIR=$T/tmp/t$K
LOG=$L/task$K.log
stop() { echo "STOP: $*" >> "$LOG"; exit 1; }

{ date -u +%FT%TZ; hostname; echo "job ${SLURM_ARRAY_JOB_ID}_$K cpus_per_task=$SLURM_CPUS_PER_TASK"
  git -C "$D" rev-parse HEAD; echo "porcelain_ignored_lines $(git -C "$D" status --porcelain --ignored | wc -l)"; } > "$LOG" 2>&1

# P0: the code (the first run's four files and wrapper), checked against their declared digests
git -C "$D" show 07c18aee:nd-unfolding/bootstrap_nd.py  > "$W/A/bootstrap_nd.py"
git -C "$D" show 07c18aee^:nd-unfolding/bootstrap_nd.py > "$W/B/bootstrap_nd.py"
git -C "$D" show 07c18aee:nd-unfolding/omnifold_nn_core.py > "$W/lib/omnifold_nn_core.py"
git -C "$D" show 07c18aee:nd-unfolding/xsec_nd.py          > "$W/lib/xsec_nd.py"
( cd "$W" && sha256sum -c "$H/code.sha256" ) >> "$LOG" 2>&1 || stop "P0 code digests"
echo "649b12916b4fe43df1626f9809d89817ba3e57ee04238be793918eaa968396ae  $R" | sha256sum -c >> "$LOG" 2>&1 \
  || stop "P0 repro_run.py digest"

# P1: the input both stored sets were made from
read -r size mtime < <(stat -c '%s %Y' "$N/of_inputs_5d.npz")
echo "input size=$size mtime_epoch=$mtime" >> "$LOG"
[[ "$size" == 1548438020 && "$mtime" == 1782610308 ]] || stop "P1 input size or mtime differs"

# P2: this task's stored replica is the pinned, unseen file (task 0 grades no stored replica)
if [[ $K -ne 0 ]]; then
  SEED=$(awk -F'\t' -v k="$K" 'NR>1 && $1==k {print $2}' "$H/seeds.tsv")
  [[ -n "$SEED" && "$SEED" != 1 ]] || stop "P2 no seed for task $K, or seed 1"
  ( cd "$N/boot_nd_5d" && grep "  res_boot_${SEED}.npz\$" "$H/stored.sha256" | sha256sum -c ) >> "$LOG" 2>&1 \
    || stop "P2 stored res_boot_${SEED}.npz digest"
fi

# P3: the allocation shape of the stored runs (36 CPUs, OMP unset)
[[ -z "${OMP_NUM_THREADS:-}" ]] || stop "P3 OMP_NUM_THREADS is set"
cpus=$($PY -c 'import os;print(len(os.sched_getaffinity(0)))'); echo "affinity_cpus=$cpus" >> "$LOG"
[[ "$cpus" == 36 ]] || stop "P3 affinity is $cpus, not 36"

run() {  # $1 label, $2 code dir, $3 seed
  echo "$1 start $(date -u +%FT%TZ)" >> "$LOG"
  ( cd "$W" && $PY "$R" --script "$W/$2/bootstrap_nd.py" --lib "$W/lib" \
      --forbidden-root /pscratch/sd/j/josephrb/MINERvA-OmniFold --provenance "$O/$1.provenance.json" \
      -- --npz "$N/of_inputs_5d.npz" --seed "$3" --iters 5 --out "$O/$1.npz" ) > "$L/$1.log" 2>&1
  rc=$?; echo "$1 rc=$rc end $(date -u +%FT%TZ)" >> "$LOG"
  [[ $rc == 3 ]] && stop "P4 $1 imported a module from the canonical checkout"
  [[ $rc == 0 ]] || stop "unfold $1 exited $rc"
}
if [[ $K -eq 0 ]]; then
  run control_A1 A 1; run control_A2 A 1
else
  run "s${SEED}_A" A "$SEED"; run "s${SEED}_B" B "$SEED"
fi
echo "done $(date -u +%FT%TZ)" >> "$LOG"
