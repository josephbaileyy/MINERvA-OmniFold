#!/bin/bash
#SBATCH --job-name=sb1_unfold
#SBATCH --account=m3246
#SBATCH --qos=regular
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=128
#SBATCH --time=00:50:00
#SBATCH --no-requeue
# SB1 UL (--arm all) and SL (--arm selective): the 55677843 universe-unfold argv on the lateral
# universe, at the reference's node shape and 128 OpenMP threads, through the OI-136 guard with
# strict provenance. SL compares each loader's bytes with UL's receipt and stops before training
# on a difference (exit 4). sb1_submit.sh passes --time=00:30:00 for SL.
set -eo pipefail
source "${SB1_RUN_ENV:?submit with sb1_submit.sh}"
JOB="${SB1_JOB:?UL or SL}"
ARM="${SB1_ARM:?all or selective}"
D="${SB1_OUT}/${JOB}"
mkdir "${D}"
sb1_source_env
export OMP_NUM_THREADS=128 PYTHONUNBUFFERED=1
cd "${D}"
echo "[sb1] ${JOB} arm=${ARM} job=${SLURM_JOB_ID:-} node=$(hostname) start $(date -u +%FT%TZ)"
"${SB1_PY}" "${SB1_CODE}/${SB1_PKG}/sb1_admit.py" expect --admission "${SB1_ADMISSION}" \
  --hashes "${SB1_OUT}/H0/hashes.json" --omnifile "${SB1_UNI}" --out "${D}/expect.json"
CMP=()
[[ "${ARM}" == "selective" ]] && CMP=(--compare-digests "${SB1_OUT}/UL/receipt.json")
"${SB1_PY}" "${SB1_CODE}/nd-unfolding/mnv_guarded_run.py" --expect-root "${SB1_CODE}" \
  --inventory "${D}/inventory.jsonl" --label "sb1-${JOB}" -- \
  "${SB1_CODE}/${SB1_PKG}/sb1_run.py" unfold --arm "${ARM}" --receipt "${D}/receipt.json" \
  --label "sb1-${JOB}" --expect "${D}/expect.json" --require-provenance \
  --input-hashes "${SB1_OUT}/H0/hashes.json" "${CMP[@]}" -- \
  --omnifile "${SB1_UNI}" --mcfile "${SB1_MC}" --iters 5 --use-weights --estimator lgbm \
  --universe "${SB1_LATERAL}" --seed 42 --out "${D}/2d_xsec_${JOB}.root"
echo "[sb1] ${JOB} done $(date -u +%FT%TZ)"
