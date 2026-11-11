#!/bin/bash
# Band diagnosis, the P2 job script. It carries no #SBATCH directives: the account, QOS, constraint, node count,
# exclusivity, requeue, export and limit are on the sbatch command line in the connect.
#   sbatch ... bdg_p2_wrapper.sh <deploy> <pin> <inputs table> <unfold table> <lanes dir> <probe script> <inputs json>
# In order, each step stamped to the millisecond:
#   1. the in-lane thread probe (Part 1's pfd_threadprobe.py, unchanged): one srun step with the lanes' exact shape
#      (--exact -n1 -c 32 --mem=56G --gres=none), after the same setup_salloc_env.sh source, writing only
#      <lanes dir>/threadprobe-<job>.log. A probe failure is recorded and the steps still run;
#   2. section 4.3's inputs step: the one line of <inputs table>, run by the committed s5c_array.sh in a step of the
#      same shape. Its rc is fd_1b_band_diag.py's: 0 EQUAL, 1 DIFFER, 8 a moved atime, 4 a refusal. Any rc other than 0
#      is a STOP: the job exits with that rc and no unfold runs;
#   3. only then, the committed packer runs lines 0..7 of <unfold table> with 32 CPUs and 56G per line and gres "none".
set -o pipefail   # NOT set -u (the setup script reads unset variables)
D="${1:?deploy}"; PIN="${2:?pin}"; ITABLE="${3:?inputs table}"; TABLE="${4:?unfold table}"; OUT="${5:?lanes dir}"
PROBE="${6:?probe script}"; IJSON="${7:?inputs json}"
stamp() { date -u +%FT%T.%3NZ; }
mkdir -p "${OUT}"
echo "[bdg-wrapper] $(stamp) start job=${SLURM_JOB_ID} host=$(hostname) deploy=${D} pin=${PIN}"
echo "[bdg-wrapper] submitting-shell thread variables: OMP_NUM_THREADS=${OMP_NUM_THREADS-<unset>} OPENBLAS_NUM_THREADS=${OPENBLAS_NUM_THREADS-<unset>} MKL_NUM_THREADS=${MKL_NUM_THREADS-<unset>} NUMEXPR_NUM_THREADS=${NUMEXPR_NUM_THREADS-<unset>}"
srun --exact -n1 -c 32 --mem=56G --gres=none --job-name=threadprobe \
  bash -c 'source "$1/setup_salloc_env.sh" > /dev/null 2>&1; cd "$1" || exit 2; python3 "$2"' threadprobe "${D}" "${PROBE}" \
  > "${OUT%/}/threadprobe-${SLURM_JOB_ID}.log" 2>&1
prc=$?
echo "[bdg-wrapper] $(stamp) probe rc=${prc}$( [ "${prc}" -eq 0 ] || echo ' (recorded; the steps still run)')"
echo "[bdg-wrapper] $(stamp) inputs step start (read window opens)"
srun --exact -n1 -c 32 --mem=56G --gres=none --job-name=inputs \
  env SLURM_ARRAY_TASK_ID=0 bash "${D}/nd-unfolding/s5c_array.sh" "${D}" "${PIN}" "${ITABLE}" "${OUT}" \
  > "${OUT%/}/inputs-${SLURM_JOB_ID}.log" 2>&1
irc=$?
echo "[bdg-wrapper] $(stamp) inputs step rc=${irc}"
if [ "${irc}" -ne 0 ] || [ ! -s "${IJSON}" ]; then
  echo "[bdg-wrapper] $(stamp) STOP: the inputs step did not read EQUAL (rc ${irc}); no unfold runs"
  exit "$([ "${irc}" -ne 0 ] && echo "${irc}" || echo 9)"
fi
echo "[bdg-wrapper] $(stamp) unfolds start"
bash "${D}/docs/orchestration/state/gpu-timing-20261023/tools/sbatch_timing_packed.sh" \
  "${D}" "${PIN}" "${TABLE}" "${OUT}" 32 56G 0 7 none
rc=$?
echo "[bdg-wrapper] $(stamp) packer rc=${rc} (read window closes)"
exit ${rc}
