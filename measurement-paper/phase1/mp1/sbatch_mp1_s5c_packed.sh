#!/bin/bash
#SBATCH --account=m3246
#SBATCH --qos=debug
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
#SBATCH --time=00:30:00
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
# MP1-A S1: run lines <first>..<last> of an s5c task table CONCURRENTLY on one node, each through the frozen deploy's
# s5c_array.sh (its pinned-sha refusal, guarded run, inventory and resume skip unchanged) as one srun step:
#   sbatch --job-name=mp1s1_<stage>_p<k> --output=<NS>/logs/%x_%j.out sbatch_mp1_s5c_packed.sh \
#          <deploy> <pinned sha> <table> <out dir> <cpus per task> <mem per task> <first> <last>
set -o pipefail   # NOT set -u
D="${1:?deploy}"; PIN="${2:?pin}"; TABLE="${3:?table}"; OUT="${4:?out}"; CPT="${5:?cpus}"; MEM="${6:?mem}"
FIRST="${7:?first}"; LAST="${8:?last}"
pids=()
for i in $(seq "${FIRST}" "${LAST}"); do
  srun --exclusive -n1 -c "${CPT}" --mem="${MEM}" --job-name="task${i}" \
    env SLURM_ARRAY_TASK_ID="${i}" bash "${D}/nd-unfolding/s5c_array.sh" "${D}" "${PIN}" "${TABLE}" "${OUT}" > "${OUT%/}-task${i}-${SLURM_JOB_ID}.log" 2>&1 &
  pids+=($!)
done
rc=0; for p in "${pids[@]}"; do wait "$p" || rc=1; done
echo "[s5c-pack] tasks ${FIRST}..${LAST} done rc=${rc}"
exit ${rc}
