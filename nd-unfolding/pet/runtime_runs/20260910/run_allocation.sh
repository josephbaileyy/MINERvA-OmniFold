#!/bin/bash
set -eo pipefail
output=$1
scontrol show job -o "$SLURM_JOB_ID" > "$output/allocation.txt"
if ! grep -q ' NumCPUs=6 ' "$output/allocation.txt"; then
  echo 'Refusing allocation outside the six-CPU ceiling' >&2
  exit 1
fi
exec srun --ntasks=1 --cpus-per-task=2 bash "$output/run_compute.sh" \
  /pscratch/sd/j/josephrb/pet-runtime-synthetic-20260910 \
  /pscratch/sd/j/josephrb/pet-v2-source-audit-runtime "$output"
