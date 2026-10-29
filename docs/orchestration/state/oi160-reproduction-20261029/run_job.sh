#!/bin/bash
#SBATCH --job-name=oi160-repro
#SBATCH --account=m3246
#SBATCH --qos=shared --constraint=cpu --nodes=1 --ntasks=1 --cpus-per-task=36 --mem=64G
#SBATCH --time=01:30:00
#SBATCH --no-requeue
# OI-160 one-replica reproduction (DECLARATION.md beside this file). Submitted from the deploy clone as
#   sbatch --output=$B/logs/%j.out --error=$B/logs/%j.err --export=NONE,B=$B,D=$D run_job.sh
# It reads the canonical checkout's input and stored replicas READ-ONLY, writes only under $B, and runs
# three unfolds: A1 and A2 with 07c18aee's bootstrap_nd.py, and B1 with 07c18aee^'s.
set -o pipefail
: "${B:?B (the run directory under pscratch) is required}"
: "${D:?D (the deploy clone at the pin) is required}"
N=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding
PY="env -u PYTHONPATH /global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3 -I -B"
H=$D/docs/orchestration/state/oi160-reproduction-20261029
W=$B/work; L=$B/logs; O=$B/out
mkdir -p "$W/A" "$W/B" "$W/lib" "$L" "$O" "$B/tmp"
export TMPDIR=$B/tmp   # nothing is written outside $B
stop() { echo "STOP: $*"; exit 1; }

{ date -u +%FT%TZ; hostname; echo "job $SLURM_JOB_ID cpus_per_task=$SLURM_CPUS_PER_TASK"; git -C "$D" rev-parse HEAD
  echo "porcelain_ignored_lines $(git -C "$D" status --porcelain --ignored | wc -l)"; } > "$L/job.log" 2>&1

# P0: the code, extracted from the clone's git objects and checked against the declared digests
git -C "$D" show 07c18aee:nd-unfolding/bootstrap_nd.py  > "$W/A/bootstrap_nd.py"
git -C "$D" show 07c18aee^:nd-unfolding/bootstrap_nd.py > "$W/B/bootstrap_nd.py"
git -C "$D" show 07c18aee:nd-unfolding/omnifold_nn_core.py > "$W/lib/omnifold_nn_core.py"
git -C "$D" show 07c18aee:nd-unfolding/xsec_nd.py          > "$W/lib/xsec_nd.py"
( cd "$W" && sha256sum -c "$H/code.sha256" ) >> "$L/job.log" 2>&1 || stop "P0 code digests"

# P1: the input is the one both stored replicas were made from (unchanged since 2026-06-27)
read -r size mtime < <(stat -c '%s %Y' "$N/of_inputs_5d.npz")
echo "input size=$size mtime_epoch=$mtime sha256=$(sha256sum "$N/of_inputs_5d.npz" | cut -d' ' -f1)" >> "$L/job.log"
[[ "$size" == 1548438020 && "$mtime" == 1782610308 ]] || stop "P1 input size or mtime differs from the declared one"

# P2: the stored replicas are the declared files
( cd "$N" && sha256sum -c "$H/stored.sha256" ) >> "$L/job.log" 2>&1 || stop "P2 stored replica digests"

# P3: the allocation shape both stored replicas were made with (36 CPUs, OMP unset)
[[ -z "${OMP_NUM_THREADS:-}" ]] || stop "P3 OMP_NUM_THREADS is set"
cpus=$($PY -c 'import os;print(len(os.sched_getaffinity(0)))')
echo "affinity_cpus=$cpus" >> "$L/job.log"; [[ "$cpus" == 36 ]] || stop "P3 affinity is $cpus, not 36"

run() {  # $1 label, $2 code dir
  echo "$1 start $(date -u +%FT%TZ)" >> "$L/job.log"
  ( cd "$W" && $PY "$H/repro_run.py" --script "$W/$2/bootstrap_nd.py" --lib "$W/lib" \
      --forbidden-root /pscratch/sd/j/josephrb/MINERvA-OmniFold --provenance "$O/$1.provenance.json" \
      -- --npz "$N/of_inputs_5d.npz" --seed 1 --iters 5 --out "$O/$1.npz" ) > "$L/$1.log" 2>&1
  rc=$?; echo "$1 rc=$rc end $(date -u +%FT%TZ)" >> "$L/job.log"
  [[ $rc == 3 ]] && stop "P4 $1 imported a module from the canonical checkout"
  return 0
}
run A1 A; run A2 A; run B1 B

$PY "$H/repro_compare.py" --a1 "$O/A1.npz" --a2 "$O/A2.npz" --b1 "$O/B1.npz" \
  --s-top "$N/boot_nd_5d/res_boot_1.npz" --s-pre "$N/boot_nd_5d_prehm_20260711/res_boot_1.npz" \
  --s-top-sha256 5e1c42d2607171e90c798811f5a9e07439c88fe8a20779c60180333b3ab69930 \
  --s-pre-sha256 2836ff561db044614ebb575574c108649e8f42f7cdd9378844682a87552e9c0f \
  --out "$O/readout.json" >> "$L/job.log" 2>&1; echo "compare rc=$?" >> "$L/job.log"
date -u +%FT%TZ >> "$L/job.log"
