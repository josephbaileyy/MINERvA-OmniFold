#!/bin/bash
#SBATCH --job-name=evid_export
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=96G
#SBATCH --time=08:00:00
#SBATCH --output=evid_export_%j.out
#SBATCH --error=evid_export_%j.err
#
# Write the row-aligned event-identity SIDECAR for the merged G2 full-event inventory NPZ.
#
# It writes ONE new file (${OUT}) and modifies nothing else: the inventory NPZ, its digests and
# every receipt bound to them are untouched. The exporter refuses to write unless it re-derives
# the inventory's own stored order hashes from the same ROOT, so a sidecar that does not belong
# to ${TARGET_NPZ} cannot be produced by accident.
#
# REQUIRES the audit receipt: it supplies the verified row -> playlist map for the merged file
# and the measured uniqueness verdict the sidecar records. Run sbatch_event_identity_audit.sh
# first. Paths are explicit, not derived from BASH_SOURCE (sbatch runs a COPY of this script).
set -euo pipefail

REPO="${MNV_CODE_ROOT:-/pscratch/sd/j/josephrb/MINERvA-OmniFold}"
AUDIT_DIR="${AUDIT_DIR:-/pscratch/sd/j/josephrb/event-identity-audit}"
OMNIFILE="${REPO}/nd-unfolding/g2_fullevent/merged/runEventLoopOmniFold_G2_FPS_MEFHC.root"
TARGET_NPZ="${REPO}/nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz"
AUDIT_JSON="${AUDIT_DIR}/EVENT_IDENTITY_AUDIT_MEFHC.json"
OUT="${AUDIT_DIR}/G2_FPS_MEFHC_P12.identity.npz"

for F in "${OMNIFILE}" "${TARGET_NPZ}" "${AUDIT_JSON}"; do
  [[ -s "${F}" ]] || { echo "[evid] FAIL: missing ${F}" >&2; exit 2; }
done
[[ -e "${OUT}" ]] && { echo "[evid] FAIL: ${OUT} exists; no-clobber" >&2; exit 2; }

cd "${REPO}"
# `set -u` MUST be off across the source. root_6_28's conda activation runs
# activate.d/activate-binutils_linux-64.sh, which reads $ADDR2LINE unbound -- under `set -u`
# that aborts the job in 5 s with exit 1 and BOTH Slurm logs at 0 bytes, which is
# indistinguishable from "never started". Measured on 58552413: `set -e` alone survives, `set -u`
# alone dies 127, `set -eu` dies 1. stderr is NOT redirected here, so a different sourcing
# failure stays visible rather than silent.
set +u
# shellcheck disable=SC1091
source setup_salloc_env.sh >/dev/null
set -u
# The postcondition, not the source's exit code, is what decides the environment is usable.
python3 -c 'import ROOT' >/dev/null 2>&1 \
  || { echo "[evid] FAIL: no PyROOT after env setup" >&2; exit 2; }

echo "[evid] start $(date -u '+%F %T UTC')"
# --production-pet-dir names the checkout whose selection built ${TARGET_NPZ}. It is the
# PRODUCTION tree, not this launcher's directory: the exporter may be deployed anywhere, but the
# retention predicates must be the ones that retained the rows we are labelling. The exporter
# fails closed if the import resolves elsewhere, and records the resolved path + sha256.
python3 "${AUDIT_DIR}/export_event_identity.py" \
  --omnifile "${OMNIFILE}" \
  --target-npz "${TARGET_NPZ}" \
  --identity-audit "${AUDIT_JSON}" \
  --production-pet-dir "${REPO}/nd-unfolding/pet" \
  --out "${OUT}"
RC=$?
echo "[evid] done rc=${RC} $(date -u '+%F %T UTC')"
exit ${RC}
