#!/bin/bash
#SBATCH --job-name=evid_audit
#SBATCH --account=m3246
#SBATCH --qos=shared
#SBATCH --constraint=cpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=48G
#SBATCH --time=06:00:00
#SBATCH --output=evid_audit_%j.out
#SBATCH --error=evid_audit_%j.err
#
# Event-identity uniqueness audit over the 12 per-playlist G2 full-event ROOTs and the merged
# MEFHC ROOT. READ-ONLY: opens ROOTs for reading and writes one JSON receipt under AUDIT_DIR.
# It touches nothing under the G2 production tree and submits no further work.
#
# Playlist order below is the MERGE INPUT ORDER declared in
# nd-unfolding/g2_fullevent/merged/G2_MEFHC_MERGE_RECEIPT.json `ordered_inputs`. It is NOT a
# directory listing and must not be re-sorted: the merged file's row -> playlist assignment is
# derived from it, and an alphabetical re-ordering yields a plausible, wrong answer with no
# symptom. It happens to coincide with alphabetical order today; that is a coincidence to
# re-check against the receipt, not a rule to rely on.
#
# Paths are explicit rather than derived from BASH_SOURCE: sbatch executes a COPY of this script
# from the Slurm spool, so BASH_SOURCE does not name this file at run time.
set -euo pipefail

REPO="${MNV_CODE_ROOT:-/pscratch/sd/j/josephrb/MINERvA-OmniFold}"
AUDIT_DIR="${AUDIT_DIR:-/pscratch/sd/j/josephrb/event-identity-audit}"
G2_FINAL="${REPO}/nd-unfolding/g2_fullevent/final"
G2_MERGED="${REPO}/nd-unfolding/g2_fullevent/merged/runEventLoopOmniFold_G2_FPS_MEFHC.root"
PLAYLISTS=(1A 1B 1C 1D 1E 1F 1G 1L 1M 1N 1O 1P)

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

ARGS=()
for PL in "${PLAYLISTS[@]}"; do
  F="${G2_FINAL}/runEventLoopOmniFold_G2_FPS_${PL}.root"
  [[ -s "${F}" ]] || { echo "[evid] FAIL: missing ${F}" >&2; exit 2; }
  ARGS+=(--root "${PL}=${F}")
done
[[ -s "${G2_MERGED}" ]] || { echo "[evid] FAIL: missing ${G2_MERGED}" >&2; exit 2; }

echo "[evid] start $(date -u '+%F %T UTC')"
python3 "${AUDIT_DIR}/audit_event_identity.py" \
  "${ARGS[@]}" \
  --merged "${G2_MERGED}" \
  --out "${AUDIT_DIR}/EVENT_IDENTITY_AUDIT_MEFHC.json"
RC=$?
echo "[evid] done rc=${RC} $(date -u '+%F %T UTC')"
exit ${RC}
