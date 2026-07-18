#!/bin/bash
#SBATCH --job-name=hashP4inputs
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=03:00:00
#SBATCH --output=docs/orchestration/state/hash-p4-inputs-%j.out
#SBATCH --error=docs/orchestration/state/hash-p4-inputs-%j.err

# Owner-neutral, read-only full-file hashes for the immutable standard and FPS
# P4 merged inputs. The job publishes only a job-ID-scoped receipt directory;
# it never writes either producer's scientific namespace.
set -euo pipefail

REPO=/pscratch/sd/j/josephrb/MINERvA-OmniFold
STATE_DIR="${REPO}/docs/orchestration/state"
RESULT_ROOT="${STATE_DIR}/merged-input-hashes"
RESULT_KEY=p4-merged-20260718
RESULT_DIR="${RESULT_ROOT}/${RESULT_KEY}"
RUN_ID="${SLURM_JOB_ID:-manual-$$}"
TMP_DIR="${RESULT_ROOT}/.${RESULT_KEY}.${RUN_ID}.tmp"
LOCK_FILE="${RESULT_ROOT}/${RESULT_KEY}.lock"

cd "${REPO}"
mkdir -p "${RESULT_ROOT}"
exec 9>"${LOCK_FILE}"
if ! flock -n 9; then
  echo "[hash] another batch/interactive contender owns ${LOCK_FILE}; clean loser exit"
  exit 0
fi
if [[ -f "${RESULT_DIR}/COMPLETE" ]]; then
  echo "[hash] complete receipt already exists at ${RESULT_DIR}; clean skip"
  exit 0
fi
if [[ -e "${RESULT_DIR}" || -e "${TMP_DIR}" ]]; then
  echo "[hash] refusing incomplete or colliding receipt path for ${RUN_ID}" >&2
  exit 2
fi
mkdir "${TMP_DIR}"

hash_family() {
  local family=$1 directory=$2 pattern=$3
  local list="${TMP_DIR}/${family}.paths"
  local hashes="${TMP_DIR}/${family}.sha256"
  local inventory="${TMP_DIR}/${family}.inventory.tsv"
  local inventory_after="${TMP_DIR}/${family}.inventory.after.tsv"

  find "${directory}" -maxdepth 1 -type f -name "${pattern}" -print | LC_ALL=C sort > "${list}"
  local count
  count=$(wc -l < "${list}")
  if [[ "${count}" -ne 10 ]]; then
    echo "[hash] ${family}: expected exactly 10 inputs, found ${count}" >&2
    exit 3
  fi

  while IFS= read -r path; do
    stat --printf='%s\t%Y\t%n\n' "${path}"
  done < "${list}" > "${inventory}"
  xargs -d '\n' -n 1 -P 4 sha256sum < "${list}" | LC_ALL=C sort -k2,2 > "${hashes}"
  while IFS= read -r path; do
    stat --printf='%s\t%Y\t%n\n' "${path}"
  done < "${list}" > "${inventory_after}"

  if ! cmp -s "${inventory}" "${inventory_after}"; then
    echo "[hash] ${family}: input size/mtime changed while hashing" >&2
    exit 5
  fi
  rm "${inventory_after}"

  if [[ $(wc -l < "${hashes}") -ne 10 || $(wc -l < "${inventory}") -ne 10 ]]; then
    echo "[hash] ${family}: incomplete receipt" >&2
    exit 4
  fi
}

date -u '+[hash] start %Y-%m-%dT%H:%M:%SZ'
hash_family standard \
  nd-unfolding/active_universe_5d/standard/merged \
  'runEventLoopOmniFold_5D_MEFHC_active_*.root'
hash_family fps \
  nd-unfolding/active_universe_5d/fps/merged \
  'runEventLoopOmniFold_5D_FPS_active_*_universes_full.root'

{
  printf 'schema\tmerged-input-hashes.v1\n'
  printf 'run_id\t%s\n' "${RUN_ID}"
  printf 'completed_utc\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  printf 'standard_count\t10\n'
  printf 'fps_count\t10\n'
  printf 'launcher_sha256\t'
  sha256sum "$0" | awk '{print $1}'
} > "${TMP_DIR}/summary.tsv"
printf '%s\n' "${RUN_ID}" > "${TMP_DIR}/COMPLETE"

mv "${TMP_DIR}" "${RESULT_DIR}"
date -u '+[hash] complete %Y-%m-%dT%H:%M:%SZ'
printf '[hash] receipt %s\n' "${RESULT_DIR}"
