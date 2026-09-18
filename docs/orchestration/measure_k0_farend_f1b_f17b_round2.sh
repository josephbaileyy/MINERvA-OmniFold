#!/bin/bash
# ============================================================================================
# ROUND-2 PARAMETERIZATION of measure_k0_farend_f1b_f17b.sh for
# k0-7ac0edec-20260830T000215Z.
#
# Derived from the tested, run-specific implementation at sha256
# ad1a8b6405e55094afbaa9cab00b0a2b7afb0fa52835653d147dad6e92b84775. This shim does not
# copy or reimplement that instrument's guards. It verifies the source bytes, substitutes only
# the five run-specific assignments and two run-specific digest annotations into an ephemeral
# copy, and executes the resulting script. The source instrument's refusal arms therefore remain
# byte-for-byte the implementation exercised here.
#
# Changed for round 2, and only because these are properties of the new rehearsal:
#   * WANT_SHA and CODE_ROOT subject: deployed tree detached at 7ac0edec...;
#   * RUN and JOBS: the round-2 run root and its seven submitted job ids;
#   * BASELINE: the declaration's 7ac0edec source-manifest, never the run-local copy;
#   * printed baseline/run-manifest digest annotations;
#   * TOOLS_ROOT: the canonical cluster checkout, which is a real git checkout;
#   * F-17(b) publication target: ephemeral scratch, because this invocation takes the combined
#     instrument but this filing covers F-1(b) only and does not producer-file or grade F-17(b).
#
# The --measure path additionally invokes the same deployed mnv_source_manifest.py once with all
# five fail-closed --require-* flags, --compare, and --write to print the exact A-2(a)-(g) values
# used in the producer filing. That output is scratch-only and is removed on exit.
#
# DOES NOT COVER: any grade or gate movement; Gate-2 disposition; quarantine discharge; adoption;
# authorization to submit anything; leg 6; any M(ii) leg; the unavailable F-17(b) comparison to
# the pre-submission prose document; or any publication claim. Gate 2 remains FAIL.
# ============================================================================================

MODE="${1:---dry-run}"
SOURCE_INSTRUMENT="${MNV_F1B_BASE_INSTRUMENT:-$(cd "$(dirname "$0")" && pwd)/measure_k0_farend_f1b_f17b.sh}"
SOURCE_SHA=ad1a8b6405e55094afbaa9cab00b0a2b7afb0fa52835653d147dad6e92b84775

export K0R2_CODE_ROOT=/pscratch/sd/j/josephrb/k0r2/clean
export K0R2_WANT_SHA=7ac0edecf45bf95ce0d2e2b6c2f8130a95b3994b
export K0R2_BASELINE=/pscratch/sd/j/josephrb/k0r2/declarations/7ac0edec/source-manifest.json
export K0R2_RUN=/pscratch/sd/j/josephrb/k0r2/runs/k0-7ac0edec-20260830T000215Z
export K0R2_JOBS=57753239,57753243,57753244,57753245,57753246,57753247,57753248
export MNV_TOOLS_ROOT=/pscratch/sd/j/josephrb/MINERvA-OmniFold
export GIT_OPTIONAL_LOCKS=0
export PYTHONDONTWRITEBYTECODE=1

PY=/global/u2/j/josephrb/.conda/envs/root_6_28/bin/python3
BASELINE_FILE_SHA=ca6a8f2b0c8b73be9d69b6f8d2f97e5f63b1697571954d2db8f9227c8d11a032
RUN_MANIFEST_FILE_SHA=713deabb2ed35d147b102ae97af270e6229d3f1da319af7a0a7f566247df11a3

if [ "$MODE" != "--dry-run" ] && [ "$MODE" != "--measure" ]; then
  echo "REFUSE: mode must be --dry-run or --measure; got $MODE"
  exit 2
fi

if [ ! -f "$SOURCE_INSTRUMENT" ]; then
  echo "REFUSE: tested source instrument is absent: $SOURCE_INSTRUMENT"
  exit 11
fi
SOURCE_ACTUAL=$(/usr/bin/sha256sum "$SOURCE_INSTRUMENT" | /usr/bin/awk '{print $1}')
if [ "$SOURCE_ACTUAL" != "$SOURCE_SHA" ]; then
  echo "REFUSE: source instrument digest differs: expected=$SOURCE_SHA actual=$SOURCE_ACTUAL"
  exit 13
fi

if [ ! -f "$K0R2_BASELINE" ] || [ ! -f "$K0R2_RUN/source-manifest.json" ]; then
  echo "REFUSE: the declared baseline or the round-2 run manifest is absent"
  exit 11
fi
BASELINE_FILE_ACTUAL=$(/usr/bin/sha256sum "$K0R2_BASELINE" | /usr/bin/awk '{print $1}')
RUN_MANIFEST_FILE_ACTUAL=$(/usr/bin/sha256sum "$K0R2_RUN/source-manifest.json" | /usr/bin/awk '{print $1}')
if [ "$BASELINE_FILE_ACTUAL" != "$BASELINE_FILE_SHA" ]; then
  echo "REFUSE: baseline file digest differs: expected=$BASELINE_FILE_SHA actual=$BASELINE_FILE_ACTUAL"
  exit 13
fi
if [ "$RUN_MANIFEST_FILE_ACTUAL" != "$RUN_MANIFEST_FILE_SHA" ]; then
  echo "REFUSE: run-manifest file digest differs: expected=$RUN_MANIFEST_FILE_SHA actual=$RUN_MANIFEST_FILE_ACTUAL"
  exit 13
fi

require_one() {
  needle="$1"
  count=$(/usr/bin/grep -cF "$needle" "$SOURCE_INSTRUMENT")
  if [ "$count" -ne 1 ]; then
    echo "REFUSE: expected exactly one parameterization target, found $count: $needle"
    exit 13
  fi
}

require_one 'CODE_ROOT=/pscratch/sd/j/josephrb/k0r2/clean'
require_one 'WANT_SHA=aa67c426afaa9b6ca91c9996637a6bade950da9a'
require_one 'BASELINE=/pscratch/sd/j/josephrb/k0r2/declarations/aa67c426/source-manifest.json'
require_one 'RUN=/pscratch/sd/j/josephrb/k0r2/runs/k0-aa67c426-20260824T145751Z'
require_one 'JOBS=57527866,57527869,57527870,57527872,57527873,57527874,57527875'
require_one '(expect 622ddc0a)'
require_one '(b46e4f57; built 9s pre-submission)'

SCRATCH_PARENT="${TMPDIR:-/tmp}"
WORK=$(/usr/bin/mktemp -d "$SCRATCH_PARENT/k0r2-f1b-round2.XXXXXX") || exit 14
case "$WORK" in
  "$SCRATCH_PARENT"/k0r2-f1b-round2.*) ;;
  *) echo "REFUSE: mktemp returned an unexpected path: $WORK"; exit 14 ;;
esac
cleanup() {
  case "$WORK" in
    "$SCRATCH_PARENT"/k0r2-f1b-round2.*) /bin/rm -rf -- "$WORK" ;;
    *) echo "REFUSE: not removing unexpected scratch path: $WORK" >&2 ;;
  esac
}
trap cleanup EXIT HUP INT TERM
export TMPDIR="$WORK"
export MNV_F17B_RECORD_PATH="$WORK/f17b-k0-7ac0edec-20260830T000215Z.json"
PARAMETERIZED="$WORK/measure_k0_farend_f1b_f17b_round2.parameterized.sh"

/usr/bin/sed \
  -e 's|^CODE_ROOT=.*$|CODE_ROOT="${K0R2_CODE_ROOT}"|' \
  -e 's|^WANT_SHA=.*$|WANT_SHA="${K0R2_WANT_SHA}"|' \
  -e 's|^BASELINE=.*$|BASELINE="${K0R2_BASELINE}"|' \
  -e 's|^RUN=.*$|RUN="${K0R2_RUN}"|' \
  -e 's|^JOBS=.*$|JOBS="${K0R2_JOBS}"|' \
  -e 's|(expect 622ddc0a)|(expect ca6a8f2b)|' \
  -e 's|(b46e4f57; built 9s pre-submission)|(713deabb; built before round-2 submission)|' \
  "$SOURCE_INSTRUMENT" > "$PARAMETERIZED"

echo "### ROUND-2 PARAMETERIZATION"
echo "  source instrument: $SOURCE_INSTRUMENT"
echo "  source sha256    : $SOURCE_ACTUAL"
echo "  baseline sha256  : $BASELINE_FILE_ACTUAL"
echo "  run manifest sha256: $RUN_MANIFEST_FILE_ACTUAL"
echo "  scratch-only F-17(b) record: $MNV_F17B_RECORD_PATH"

/bin/bash "$PARAMETERIZED" "$MODE"
rc=$?
if [ "$rc" -ne 0 ]; then
  exit "$rc"
fi

if [ "$MODE" = "--measure" ]; then
  echo
  echo "### ROUND-2 A-2(a)-(g) CONSOLIDATED READBACK"
  MEASUREMENT_JSON="$WORK/f1b-round2-a2.json"
  TOOL="$K0R2_CODE_ROOT/nd-unfolding/mnv_source_manifest.py"
  TOOL_PRE=$(/usr/bin/sha256sum "$TOOL" | /usr/bin/awk '{print $1}')
  "$PY" "$TOOL" \
    --repo "$K0R2_CODE_ROOT" \
    --compare "$K0R2_BASELINE" \
    --write "$MEASUREMENT_JSON" \
    --require-clean \
    --require-checkout \
    --require-no-nested-checkout \
    --require-not-nested \
    --require-readonly \
    --label 'F-1(b) producer far-end measurement, round 2, 2026-09-01'
  readback_rc=$?
  TOOL_POST=$(/usr/bin/sha256sum "$TOOL" | /usr/bin/awk '{print $1}')
  echo "  consolidated readback rc=$readback_rc"
  echo "  source-manifest tool sha256 pre=$TOOL_PRE post=$TOOL_POST"
  if [ "$TOOL_PRE" != "$TOOL_POST" ]; then
    echo "REFUSE: source-manifest tool changed across the consolidated readback"
    exit 13
  fi
  if [ "$readback_rc" -ne 0 ]; then
    echo "REFUSE: consolidated A-2(a)-(g) readback failed"
    exit "$readback_rc"
  fi
  "$PY" - "$MEASUREMENT_JSON" "$K0R2_BASELINE" <<'PY'
import hashlib
import json
import pathlib
import sys

live_path = pathlib.Path(sys.argv[1])
baseline_path = pathlib.Path(sys.argv[2])
live = json.loads(live_path.read_text())
baseline = json.loads(baseline_path.read_text())
constitution = live["constitution"]
print("  a.head =", live["head"])
print("  b.dirty_count =", live["dirty_count"])
print("  c.is_checkout =", json.dumps(constitution["is_checkout"]))
print("  c.markers =", json.dumps(constitution["markers"], sort_keys=True))
print("  d.nested_checkouts =", json.dumps(constitution["nested_checkouts"]))
print("  e.enclosing_checkout =", json.dumps(constitution["enclosing_checkout"]))
print("  f.file_count =", live["file_count"])
print("  f.listing_sha256 =", live["listing_sha256"])
print("  f.baseline_file_sha256 =", hashlib.sha256(baseline_path.read_bytes()).hexdigest())
print("  f.baseline_file_count =", baseline["file_count"])
print("  f.baseline_listing_sha256 =", baseline["listing_sha256"])
print("  g.mode_writable =", json.dumps(constitution["mode_writable"]))
print("  g.uid_writable =", json.dumps(constitution["uid_writable"]))
print("  g.other_writable =", json.dumps(constitution["other_writable"]))
PY
  echo "### ROUND-2 MEASUREMENT COMPLETE"
  echo "  F-17(b) record above was scratch-only and will be removed; this invocation does not file it."
fi
