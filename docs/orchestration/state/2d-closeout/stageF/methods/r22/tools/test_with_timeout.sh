#!/usr/bin/env bash
# usage: bash test_with_timeout.sh -- tests gapjob.sh's with_timeout(), taken from gapjob.sh itself, in both directions:
# a hang (with a grandchild, and one that ignores TERM) must return 124 and leave no process; a fast exit must keep its
# status. Exits 1 on any failure.
cd "$(dirname "$0")"; eval "$(sed -n '/^with_timeout() {/,/^}/p' gapjob.sh)"
export TMPDIR=$(mktemp -d); fail=0
check() { if [ "$2" = "$3" ]; then echo "ok   $1: $2"; else echo "FAIL $1: got $2, want $3"; fail=1; fi; }
with_timeout 3 bash -c 'bash -c "exec -a r22tmo_hung sleep 60"'; check "hang -> 124" $? 124
sleep 1; check "hang survivors" "$(pgrep -f r22tmo_hung | wc -l | tr -d ' ')" 0
with_timeout 3 bash -c 'trap "" TERM; bash -c "exec -a r22tmo_stubborn sleep 60"'; check "TERM-ignoring hang -> 124" $? 124
sleep 1; check "TERM-ignoring survivors" "$(pgrep -f r22tmo_stubborn | wc -l | tr -d ' ')" 0
with_timeout 10 bash -c 'sleep 1; exit 0'; check "fast exit 0 kept" $? 0
with_timeout 10 bash -c 'exit 3'; check "fast exit 3 kept" $? 3
check "flag files left" "$(ls -A "$TMPDIR" | wc -l | tr -d ' ')" 0
rmdir "$TMPDIR"; exit $fail
