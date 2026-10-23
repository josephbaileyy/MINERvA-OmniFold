#!/bin/bash
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
# gpu-timing-20261023 C1 (approved by the director 2026-10-23 by message): the same timed step as the other arms, run by
# sbatch_timing_packed.sh unchanged, with a CPU-frequency reading beside it. Before the step it records the cpufreq
# governor and limits (if the node exposes them), then samples /proc/cpuinfo "cpu MHz" of every CPU (all 256 values, in
# processor order) every 30 s until the step ends. The sampler reads files only and takes no srun step.
#   sbatch ... sbatch_c1_freq.sh <freq log> <sbatch_timing_packed.sh> <its arguments ...>
set -o pipefail   # NOT set -u
FLOG="${1:?freq log}"; PACKED="${2:?packed script}"; shift 2
{
  echo "host $(hostname) job ${SLURM_JOB_ID} $(date -u +%FT%TZ)"
  for f in scaling_governor scaling_driver cpuinfo_min_freq cpuinfo_max_freq scaling_min_freq scaling_max_freq; do
    echo "cpu0 ${f} $(cat /sys/devices/system/cpu/cpu0/cpufreq/${f} 2>&1)"
  done
  echo "boost $(cat /sys/devices/system/cpu/cpufreq/boost 2>&1)"
} > "${FLOG}"
( while :; do
    echo "sample $(date -u +%FT%TZ) $(awk '/^cpu MHz/{printf "%.0f ", $4}' /proc/cpuinfo)" >> "${FLOG}"
    sleep 30
  done ) &
SAMPLER=$!
bash "${PACKED}" "$@"
rc=$?
kill "${SAMPLER}" 2>/dev/null
echo "end $(date -u +%FT%TZ) rc ${rc}" >> "${FLOG}"
exit ${rc}
