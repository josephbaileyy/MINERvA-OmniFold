#!/bin/bash
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --no-requeue
#SBATCH --export=ALL,HOME=/global/homes/j/josephrb
# gpu-timing-20261023 (ASSIGNMENT.md): run lines <first>..<last> of tools/tasks.tsv CONCURRENTLY on one node, each
# through the pinned deploy's s5c_array.sh (pinned-sha refusal, guarded run, inventory, resume skip unchanged) as one
# srun step, as the recorded s5p allocation 58911473 did (s5c_steps.sh: srun --exact -c 32 --mem 56G per step).
# Account, QOS, constraint, GPUs and time limit are given on the sbatch command line (RUN.md).
#   sbatch ... sbatch_timing_packed.sh <deploy> <pin> <table> <out dir> <cpus per task> <mem per task> <first> <last> \
#          <step gres: none|inherit> [<probe script>]
# With a probe script (G1 only), it first runs the one-line LightGBM device probe for "cuda" and for "gpu", each as
# its own step with one GPU, to completion, before any timed step starts.
set -o pipefail   # NOT set -u
D="${1:?deploy}"; PIN="${2:?pin}"; TABLE="${3:?table}"; OUT="${4:?out}"; CPT="${5:?cpus}"; MEM="${6:?mem}"
FIRST="${7:?first}"; LAST="${8:?last}"; GRES="${9:?none|inherit}"; PROBE="${10:-}"
mkdir -p "${OUT}"
stamp() { date -u +%FT%T.%3NZ; }
echo "[timing] $(stamp) job=${SLURM_JOB_ID} host=$(hostname) deploy=${D} pin=${PIN} lines=${FIRST}..${LAST} cpt=${CPT} mem=${MEM} gres=${GRES}"
lscpu | grep -E '^(Model name|Socket|Core|Thread|CPU\(s\))' | sed 's/^/[timing] lscpu /'
if [ -n "${PROBE}" ]; then
  for dev in cuda gpu; do
    srun -n1 -c 8 --mem=8G --gpus=1 --job-name="probe_${dev}" \
      env -u PYTHONPATH /global/homes/j/josephrb/.conda/envs/root_6_28/bin/python3 -I -X faulthandler "${PROBE}" "${dev}" \
      > "${OUT%/}/probe_${dev}-${SLURM_JOB_ID}.log" 2>&1
    echo "[timing] $(stamp) probe ${dev} rc=$?"
  done
fi
step_gres=()
[ "${GRES}" = none ] && step_gres=(--gres=none)
pids=()
for i in $(seq "${FIRST}" "${LAST}"); do
  echo "[timing] $(stamp) launch line ${i}"
  srun --exact -n1 -c "${CPT}" --mem="${MEM}" "${step_gres[@]}" --job-name="line${i}" \
    env SLURM_ARRAY_TASK_ID="${i}" bash "${D}/nd-unfolding/s5c_array.sh" "${D}" "${PIN}" "${TABLE}" "${OUT}" \
    > "${OUT%/}/line${i}-${SLURM_JOB_ID}.log" 2>&1 &
  pids+=($!)
done
rc=0; for p in "${pids[@]}"; do wait "$p" || rc=1; done
echo "[timing] $(stamp) lines ${FIRST}..${LAST} done rc=${rc}"
exit ${rc}
