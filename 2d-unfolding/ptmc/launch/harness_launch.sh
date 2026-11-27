#!/bin/bash
# Harness for ptmc_launch.sh's local gates (no ssh is reached in any case here).
set -u
L=$(cd "$(dirname "$0")" && pwd)
pass=0; fail=0
ok() { if [ "$1" = 0 ]; then pass=$((pass+1)); echo "ok   $2"; else fail=$((fail+1)); echo "FAIL $2"; fi; }
T=$(mktemp -d); cp "$L/ptmc_launch.sh" "$L/ptmc_remote.sh" "$T/"
d() { mktemp -d; }
out=$(bash "$T/ptmc_launch.sh" setup "$(d)" login04 2>&1); rc=$?
[ "$rc" = 9 ] && printf '%s' "$out" | grep -q 'not filled in'; ok $? "an unfilled sha: STOP 9"
sed -i.bak "s/__REMOTE_SHA256__/$(shasum -a 256 "$T/ptmc_remote.sh" | cut -d' ' -f1)/" "$T/ptmc_launch.sh"
x=$(d); : > "$x/f"; out=$(bash "$T/ptmc_launch.sh" setup "$x" login04 2>&1); rc=$?
[ "$rc" = 9 ] && printf '%s' "$out" | grep -q 'not a new empty directory'; ok $? "a non-empty session dir: STOP 9"
out=$(bash "$T/ptmc_launch.sh" setup "$(d)" bogus 2>&1); rc=$?
[ "$rc" = 9 ] && printf '%s' "$out" | grep -q 'not a login node'; ok $? "a bad node name: STOP 9"
out=$(bash "$T/ptmc_launch.sh" nonsense "$(d)" login04 2>&1); rc=$?
[ "$rc" = 9 ] && printf '%s' "$out" | grep -q 'STOP: mode'; ok $? "an unknown mode: STOP 9"
echo "# changed" >> "$T/ptmc_remote.sh"; out=$(bash "$T/ptmc_launch.sh" pilot "$(d)" login04 2>&1); rc=$?
[ "$rc" = 8 ] && printf '%s' "$out" | grep -q 'not the approved one'; ok $? "a changed remote script: STOP 8"
echo "pass $pass fail $fail"; [ "$fail" = 0 ]
