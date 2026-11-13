#!/bin/bash
# E96D A1: a dummy test of the full submit's reservation-window parse, on a login node, from a /dev/shm copy of itself
# ($1), deleted at exit. Reads and writes nothing but its own /dev/shm temp file: no scontrol, no sbatch, no digest.
# It runs the full submit's loop, byte for byte (between "near=0" and "done"), on three dummy reservations and checks
# the local-time conversion on a fixed dummy instant. Exit 0 = PASS; 3 = FAIL.
SELF=$1; T=$(mktemp /dev/shm/e96d-restest.XXXXXX)
fin() { rm -f -- "$SELF" "$T"; exit "$1"; }
echo "restest host=$(hostname) utc=$(date -u +%FT%TZ) tz=$(date +%Z)"
fail=0
a=$(date -d '2026-01-01T00:00:00Z' +%Y-%m-%dT%H:%M:%S); b=$(date -d '2025-12-31T16:00:00' +%s)
echo "dummy: 2026-01-01T00:00:00Z in local time = $a; 2025-12-31T16:00:00 local = epoch $b"
[ "$a" = 2025-12-31T16:00:00 ] && [ "$b" = 1767225600 ] || { echo "FAIL: the local-time conversion"; fail=1; }
now=$(date -u +%s); WINDOW_S=$((15300 + 1800)); end=$((now + WINDOW_S))
lt() { date -d @$1 +%Y-%m-%dT%H:%M:%S; }
printf 'ReservationName=dummy_in StartTime=%s EndTime=x\nReservationName=dummy_late StartTime=%s EndTime=x\nReservationName=dummy_past StartTime=%s EndTime=x\n' \
  "$(lt $((now + 3600)))" "$(lt $((now + 36000)))" "$(lt $((now - 3600)))" > "$T"
cat "$T"
finish() { echo "loop exited $1"; fail=1; }
NEW_RES="$T"
near=0
for st in $(sed -n 's/.*StartTime=\([0-9T:-]*\).*/\1/p' "$NEW_RES"); do
  s=$(date -d "$st" +%s) || { echo "STOP: unparsable StartTime $st"; finish 9; }
  echo "reservation StartTime=$st (local) = $(date -u -d @$s +%FT%TZ)"
  [ "$s" -gt "$now" ] && [ "$s" -le "$end" ] && near=$((near + 1))
done
echo "near=$near (expected 1: dummy_in only)"
[ "$near" -eq 1 ] || { echo "FAIL: the window count"; fail=1; }
[ "$fail" -eq 0 ] && { echo "RESTEST PASS"; fin 0; }
echo "RESTEST FAIL"; fin 3
