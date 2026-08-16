#!/bin/bash
# Lane B, 2026-08-16: standard-P4 stages 4-6 under the repair-11 PASS token.
#
# STEP 0 IS A FAIL-CLOSED PRECONDITION, not a courtesy. Stage 4 opens its output "RECREATE"
# (p4_build_components.py:177) and the live std_final5_candidate.root is the audited object of
# 20260810T0600Z-product-audit-5d-verdict.json, with its digest bound in two manifests. So the
# chain does not start until THIS script has independently recomputed the preserved copy's
# sha256 and matched it to that audited digest. A backup asserted in a message is not a backup.
set -o pipefail
REPO=/pscratch/sd/j/josephrb/MINERvA-OmniFold
PRES=/pscratch/sd/j/josephrb/PRESERVE-p4-candidate-20260816
LOGDIR=/pscratch/sd/j/josephrb/p4-stages456-20260816
AUDITED=602bbcf26606844941b8a6295f47e080507c20097a80f42cdf202bd8c567f037
TOKEN=90dc017530c0c5ed2bb25b317be7ca491d9f369fd7fb3ea11b4011d4b6502207
mkdir -p "$LOGDIR"
LOG="$LOGDIR/run.log"

{
echo "[laneB] ===== start $(date -u +%FT%TZ) on $(hostname) ====="
echo "[laneB] python: $(python3 -V 2>&1)"
echo
echo "[laneB] ---- STEP 0: verify the preserved copy against the AUDITED digest ----"
[[ -s "$PRES/COPY_COMPLETE" ]] || { echo "[laneB] ABORT: no COPY_COMPLETE marker in $PRES"; exit 10; }
[[ -s "$PRES/std_final5_candidate.root" ]] || { echo "[laneB] ABORT: preserved candidate missing"; exit 10; }
echo "[laneB] hashing 39.4 GiB, expect a few minutes of silence..."
GOT=$(sha256sum "$PRES/std_final5_candidate.root" | awk '{print $1}')
echo "[laneB] preserved sha256 = ${GOT}"
echo "[laneB] audited   sha256 = ${AUDITED}"
if [[ "$GOT" != "$AUDITED" ]]; then
  echo "[laneB] ABORT: preserved copy does NOT match the audited digest."
  echo "[laneB]        Refusing to let stage 4 RECREATE the only remaining copy."
  exit 11
fi
echo "[laneB] STEP 0 PASS -- the audited object survives independently of this run."
echo
echo "[laneB] ---- STEP 1: sizes of the five artifacts this run will overwrite (pre-state) ----"
for f in "$REPO/nd-unfolding/active_universe_5d/standard/candidate/std_final5_candidate.root" \
         "$REPO/nd-unfolding/active_universe_5d/standard/candidate/std_component_manifest.json" \
         "$REPO/nd-unfolding/active_universe_5d/standard/candidate/p4_standard_validation.json" \
         "$REPO/nd-unfolding/active_universe_5d/standard/candidate/std_proj4d_candidate.root" \
         "$REPO/nd-unfolding/active_universe_5d/standard/candidate/std_proj4d_candidate_projmanifest.json"; do
  [[ -e "$f" ]] && printf '[laneB]   %14s  %s  %s\n' "$(stat -c '%s' "$f")" "$(date -u -d @$(stat -c '%Y' "$f") +%F)" "$(basename "$f")"
done
echo
echo "[laneB] ---- STEP 2: the chain, STOP_AFTER=project ----"
cd "$REPO/nd-unfolding" || { echo "[laneB] ABORT cd"; exit 9; }
echo "[laneB] git HEAD = $(git rev-parse HEAD)"
STOP_AFTER=project P4_VERIFIER_PASS="$TOKEN" bash run_p4_standard.sh
rc=$?
echo
echo "[laneB] ===== chain rc=${rc}  end $(date -u +%FT%TZ) ====="
exit $rc
} > "$LOG" 2>&1
echo "$?" > "$LOGDIR/rc.txt"
