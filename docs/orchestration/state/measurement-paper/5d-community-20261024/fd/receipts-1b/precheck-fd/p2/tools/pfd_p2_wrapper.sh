#!/bin/bash
# 1B pre-check Part 1, the P2/P3 job script (the director's choice (i)): one in-lane thread probe step, then the
# committed packer unchanged. It carries no #SBATCH directives. The packer's own directives (--nodes=1 --exclusive
# --no-requeue --export=ALL,HOME=/global/homes/j/josephrb) and section 7's account, QOS, constraint and limit are on the
# sbatch command line in the connect.
#   sbatch ... pfd_p2_wrapper.sh <deploy> <pin> <table> <lanes dir> <first> <last> <probe script>
# The probe is one srun step with the lanes' exact shape (srun --exact -n1 -c 32 --mem 56G --gres=none, as the packer
# runs each line with gres "none"), after the same setup_salloc_env.sh source as s5c_array.sh, writing only to
# <lanes dir>/threadprobe-<job>.log. A probe failure is recorded and the lines still run. Then the packer runs
# lines <first>..<last> of <table> with 32 CPUs and 56G per line and gres "none".
set -o pipefail   # NOT set -u (the setup script reads unset variables)
D="${1:?deploy}"; PIN="${2:?pin}"; TABLE="${3:?table}"; OUT="${4:?lanes dir}"; FIRST="${5:?first}"; LAST="${6:?last}"
PROBE="${7:?probe script}"
stamp() { date -u +%FT%T.%3NZ; }
mkdir -p "${OUT}"
echo "[pfd-wrapper] $(stamp) job=${SLURM_JOB_ID} host=$(hostname) deploy=${D} pin=${PIN} table=${TABLE} lines=${FIRST}..${LAST}"
echo "[pfd-wrapper] submitting-shell thread variables: OMP_NUM_THREADS=${OMP_NUM_THREADS-<unset>} OPENBLAS_NUM_THREADS=${OPENBLAS_NUM_THREADS-<unset>} MKL_NUM_THREADS=${MKL_NUM_THREADS-<unset>} NUMEXPR_NUM_THREADS=${NUMEXPR_NUM_THREADS-<unset>}"
srun --exact -n1 -c 32 --mem=56G --gres=none --job-name=threadprobe \
  bash -c 'source "$1/setup_salloc_env.sh" > /dev/null 2>&1; cd "$1" || exit 2; python3 "$2"' threadprobe "${D}" "${PROBE}" \
  > "${OUT%/}/threadprobe-${SLURM_JOB_ID}.log" 2>&1
prc=$?
echo "[pfd-wrapper] $(stamp) probe rc=${prc}$( [ "${prc}" -eq 0 ] || echo ' (recorded; the lines still run; the in-lane record may be missing)')"
bash "${D}/docs/orchestration/state/gpu-timing-20261023/tools/sbatch_timing_packed.sh" \
  "${D}" "${PIN}" "${TABLE}" "${OUT}" 32 56G "${FIRST}" "${LAST}" none
rc=$?
echo "[pfd-wrapper] $(stamp) packer rc=${rc}"
exit ${rc}
