#!/bin/bash
set -eo pipefail
output=$1
scontrol show job -o "$SLURM_JOB_ID" > "$output/allocation.txt"
if ! grep -q ' NumCPUs=6 ' "$output/allocation.txt"; then
  echo 'Refusing allocation outside the six-CPU ceiling' >&2
  exit 1
fi
for setting in 1 0; do
  arm="$output/onednn-$setting"
  mkdir "$arm"
  if srun --ntasks=1 --cpus-per-task=2 bash "$output/run_compute.sh" \
      /pscratch/sd/j/josephrb/pet-runtime-numerics-20260910 \
      /pscratch/sd/j/josephrb/pet-v2-source-audit-runtime "$arm" "$setting" \
      > "$arm/compute.log" 2>&1; then
    status=0
  else
    status=$?
  fi
  echo "onednn=$setting exit=$status" | tee -a "$output/outcomes.txt"
done
exit "$status"
