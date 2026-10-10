#!/bin/bash
#SBATCH --job-name=sb1_identity
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=64
#SBATCH --time=00:45:00
#SBATCH --no-requeue
# SB1 J1: the vertical pattern's loader identity on the universe file, no training. Four --arm all
# loader processes in parallel (one per tree, one thread each), then --arm selective per tree with
# --compare-digests, then two activation controls that must be refused (exit 5).
set -eo pipefail
source "${SB1_RUN_ENV:?submit with sb1_submit.sh}"
D="${SB1_OUT}/J1"
mkdir "${D}"
source "${SB1_ENV_SETUP}"
export OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1
cd "${D}"
echo "[sb1] J1 job=${SLURM_JOB_ID:-} node=$(hostname) start $(date -u +%FT%TZ)"
"${SB1_PY}" "${SB1_CODE}/${SB1_PKG}/sb1_admit.py" expect --admission "${SB1_ADMISSION}" \
  --hashes "${SB1_OUT}/H0/hashes.json" --omnifile "${SB1_UNI}" --out "${D}/expect.json"
run() {  # run TAG sb1_run-arguments...
  local tag="$1"; shift
  "${SB1_PY}" "${SB1_CODE}/nd-unfolding/mnv_guarded_run.py" --expect-root "${SB1_CODE}" \
    --inventory "${D}/inventory_${tag}.jsonl" --label "sb1-J1-${tag}" -- \
    "${SB1_CODE}/${SB1_PKG}/sb1_run.py" loaders --label "sb1-J1-${tag}" \
    --expect "${D}/expect.json" --require-provenance --input-hashes "${SB1_OUT}/H0/hashes.json" \
    --omnifile "${SB1_UNI}" --universe "${SB1_VERTICAL}" "$@"
}
TREES=(data mc_background mc_signal_reco mc_truth_denom)
PIDS=()
for t in "${TREES[@]}"; do
  run "all_${t}" --arm all --trees "${t}" --receipt "${D}/all_${t}.json" &
  PIDS+=($!)
done
for p in "${PIDS[@]}"; do wait "${p}"; done
for t in "${TREES[@]}"; do
  run "selective_${t}" --arm selective --trees "${t}" --receipt "${D}/selective_${t}.json" \
    --compare-digests "${D}/all_${t}.json"
done
set +e
run control_omit --arm selective --trees mc_signal_reco --receipt "${D}/control_omit.json" \
  --negative-control "omit:w_reco_Flux_0"
RC_OMIT=$?
run control_extra --arm selective --trees mc_signal_reco --receipt "${D}/control_extra.json" \
  --negative-control "extra:w_truth"
RC_EXTRA=$?
set -e
echo "[sb1] J1 controls exit omit=${RC_OMIT} extra=${RC_EXTRA} (5 required)"
[[ "${RC_OMIT}" == 5 && "${RC_EXTRA}" == 5 ]]
echo "[sb1] J1 done $(date -u +%FT%TZ)"
