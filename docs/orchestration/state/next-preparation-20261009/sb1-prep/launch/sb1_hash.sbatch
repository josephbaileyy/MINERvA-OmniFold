#!/bin/bash
#SBATCH --job-name=sb1_hash
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --time=00:45:00
#SBATCH --no-requeue
# SB1 H0 / H1: sha256 and stat of the three inputs; H1 then writes sacct and runs sb1_verify.py.
# Submitted only by sb1_submit.sh, which writes $SB1_RUN_ENV. sbatch runs a COPY of this file, so
# nothing here is derived from the script's own location.
set -eo pipefail
source "${SB1_RUN_ENV:?submit with sb1_submit.sh}"
STAGE="${SB1_STAGE:?H0 or H1}"
D="${SB1_OUT}/${STAGE}"
mkdir "${D}"
sb1_source_env
export OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1
echo "[sb1] ${STAGE} job=${SLURM_JOB_ID:-} node=$(hostname) start $(date -u +%FT%TZ)"
"${SB1_PY}" "${SB1_CODE}/${SB1_PKG}/sb1_hash.py" --out "${D}/hashes.json" \
  "${SB1_UNI}" "${SB1_CV}" "${SB1_MC}"
if [[ "${STAGE}" == "H1" ]]; then
  IDS="$("${SB1_PY}" -c 'import json,sys; print(",".join(json.load(open(sys.argv[1]))["jobs"].values()))' \
        "${SB1_OUT}/submission.json")"
  sacct -P --units=K -j "${IDS}" \
    -o JobID,JobName,State,ElapsedRaw,MaxRSS,MaxDiskRead,AllocTRES,ExitCode > "${D}/sacct.psv"
  REF=()
  [[ -n "${SB1_REF_UL:-}" ]] && REF+=(--reference-product "${SB1_REF_UL}")
  [[ -n "${SB1_REF_C:-}" ]] && REF+=(--cv-reference-product "${SB1_REF_C}")
  set +e
  "${SB1_PY}" "${SB1_CODE}/${SB1_PKG}/sb1_verify.py" verdict --outroot "${SB1_OUT}" \
    --admission "${SB1_ADMISSION}" --sacct "${D}/sacct.psv" "${REF[@]}" --out "${D}/verdict.json"
  echo "[sb1] verifier exit $?"
  set -e
fi
echo "[sb1] ${STAGE} done $(date -u +%FT%TZ)"
