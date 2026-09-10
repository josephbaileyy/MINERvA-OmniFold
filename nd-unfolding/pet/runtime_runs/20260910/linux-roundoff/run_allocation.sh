#!/bin/bash
set -eo pipefail
checkout=$1
runtime=$2
output=$3
scontrol show job -o "$SLURM_JOB_ID" > "$output/allocation.txt"
allocation=$(cat "$output/allocation.txt")
if [[ ! "$allocation" =~ NumCPUs=([0-9]+) ]] || (( BASH_REMATCH[1] > 6 )); then
  echo 'Refusing allocation outside the six-CPU ceiling' >&2
  exit 1
fi
exec srun --ntasks=1 --cpus-per-task=2 bash "$output/run_compute.sh" \
  "$checkout" "$runtime" "$output" 1
