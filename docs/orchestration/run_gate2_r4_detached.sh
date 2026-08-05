#!/usr/bin/env bash
# Detached compute driver. Completion is signaled atomically for wakerctl.
set -eo pipefail

REPO=/pscratch/sd/j/josephrb/MINERvA-OmniFold
RUN_ID=gate2-target-r4
RUN_DIR=${REPO}/nd-unfolding/g2_fullevent/gate2/runtime/${RUN_ID}
RUNNER=${REPO}/nd-unfolding/pet/run_gate2_target_validator.sh
LOG=${RUN_DIR}/runtime.log
SENTINEL=${RUN_DIR}/terminal.txt
EXPECTED_RUNNER_SHA=d5b86c3639917ff82101f112df25d1ff51830223f834e1a689c8088a1156d062

fail() { echo "[gate2-r4-driver][FAIL] $*" >&2; exit 1; }
[[ -x "$RUNNER" ]] || fail "runner missing/not executable"
[[ "$(sha256sum "$RUNNER" | awk '{print $1}')" == "$EXPECTED_RUNNER_SHA" ]] || fail "runner hash mismatch"
mkdir -p "$RUN_DIR"
[[ ! -e "$LOG" && ! -e "$SENTINEL" ]] || fail "run namespace already occupied: $RUN_DIR"

rc=0
"${REPO}/alloc_run.sh" \
  "env GATE2_EXECUTION_ROUTE=interactive GATE2_RUN_ID=${RUN_ID} ${RUNNER}" \
  >"$LOG" 2>&1 || rc=$?

tmp=$(mktemp "${RUN_DIR}/.terminal.XXXXXX")
printf 'rc=%s\nrun_id=%s\nfinished_at_utc=%s\nlog=%s\n' \
  "$rc" "$RUN_ID" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$LOG" >"$tmp"
mv "$tmp" "$SENTINEL"
exit "$rc"
