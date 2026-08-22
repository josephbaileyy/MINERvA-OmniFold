#!/bin/bash
# NEGATIVE CONTROL ON THE HARNESS ITSELF, run BEFORE any arm is believed.
#
# The failure this catches is the one the previous run hit: an extracted fragment that lost its
# `set -e` swallows a refusal and exits 0, so every negative control reads as "did not fire" -- or
# worse, a positive arm reads as a pass. Proving the fragment propagates a non-zero exit is the
# precondition for reading ANY arm's exit code as evidence.
set -uo pipefail
SEG="$1"
grep -q '^set -eo pipefail' "$SEG" || { echo "[selftest] FAIL: segment lost its set line"; exit 1; }
TMP="$(mktemp -d)"
# Same shape as the segment: the `set` line, then a command that FAILS, then an echo that must not run.
{ sed -n '/^set -eo pipefail/p' "$SEG"; echo 'false'; echo 'echo REACHED_THE_END'; } > "$TMP/neg.sh"
OUT="$(bash "$TMP/neg.sh" 2>&1)"; RC=$?
echo "[selftest] negative control rc=$RC output='${OUT}'"
if [[ "$RC" -eq 0 ]]; then
  echo "[selftest] FAIL: the extracted options line does NOT abort on a failed command."
  rm -rf "$TMP"; exit 1
fi
if [[ "$OUT" == *REACHED_THE_END* ]]; then
  echo "[selftest] FAIL: execution continued past the failure."
  rm -rf "$TMP"; exit 1
fi
rm -rf "$TMP"
echo "[selftest] PASS: the segment's own options line aborts on failure and does not reach the end."
