#!/bin/bash
# test_sidecar_stat.sh: rpd_flux4_connect.sh's step 5b (amendment 1 section 8: the connect stats the sidecar first),
# cut from the connect itself and run against a stub GNU stat: the sidecar must be a regular file (not a symlink) of the
# probe's size, and is never opened. Then each mutant of the block against the same cases.
# usage: bash test_sidecar_stat.sh        (nothing is contacted; stat is a shell-function stub)
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
BLOCK=$(awk '/^echo "== 5b\. the true-energy sidecar/ {f=1} f && /^echo "== 6\. the job"/ {exit} f {print}' "$HERE/../rpd_flux4_connect.sh")
[ "$(printf '%s\n' "$BLOCK" | wc -l | tr -d ' ')" -eq 4 ] || { echo "SETUP: could not cut step 5b from the connect"; exit 9; }
printf '%s\n' "$BLOCK" | grep -qE '\b(cat|head|sha256sum|python|open|dd|cp)\b' && { echo "FAIL: step 5b reads the sidecar"; exit 1; }
printf '%s\n' "$BLOCK" | grep -q -- 'stat -L' && { echo "FAIL: step 5b follows symlinks"; exit 1; }
echo "ok   step 5b is cut from rpd_flux4_connect.sh; it only stats the sidecar, without following a link"

run() {  # run BLOCK STAT_OUTPUT STAT_RC -> output, then "rc=N" (0 if the block falls through)
  bash -c "
    finish() { echo \"rc=\$1\"; exit \"\$1\"; }
    stat() { [ \"\$1\" = -c ] && [ \"\$2\" = '%F|%s' ] || { echo 'unexpected stat args' >&2; return 9; }
             [ $3 -eq 0 ] && printf '%s\n' '$2'; return $3; }
    $1
    echo rc=0"
}
check() {  # check NAME EXPECTED_RC EXPECTED_LINE OUTPUT
  rc=$(printf '%s\n' "$4" | sed -n 's/^rc=//p' | tail -1)
  if [ "$rc" = "$2" ] && printf '%s\n' "$4" | grep -qF -- "$3"; then [ "$QUIET" = 1 ] || echo "ok   $1 (rc $rc)"
  else [ "$QUIET" = 1 ] || { echo "FAIL $1: rc [$rc], want $2 and [$3]"; printf '%s\n' "$4" | sed 's/^/     /'; }
       fails=$((fails + 1)); fi
}
cases() {
  check "a regular file of the probe's size: falls through" 0 "sidecar regular file|2364943114" "$(run "$1" 'regular file|2364943114' 0)"
  check "one byte short: STOP 3" 3 "not a regular file of 2364943114 bytes" "$(run "$1" 'regular file|2364943113' 0)"
  check "a symlink: STOP 3" 3 "not a regular file of 2364943114 bytes" "$(run "$1" 'symbolic link|80' 0)"
  check "a symlink whose size field equals the probe's: STOP 3" 3 "not a regular file" "$(run "$1" 'symbolic link|2364943114' 0)"
  check "a directory: STOP 3" 3 "not a regular file" "$(run "$1" 'directory|4096' 0)"
  check "stat fails (purged): STOP 3" 3 "cannot be stat'ed (purged or moved?)" "$(run "$1" 'regular file|2364943114' 1)"
  check "stat prints a matching line but fails: STOP 3" 3 "cannot be stat'ed" "$(run "$1" 'regular file|2364943114' 2)"
}
fails=0; QUIET=0
cases "$BLOCK"
echo "SIDECAR-STAT-TESTS :: $([ "$fails" -eq 0 ] && echo PASS || echo "FAIL ($fails)")"
[ "$fails" -eq 0 ] || exit 1
TAB=$(printf '\t')
MUTANTS="stat-rc-ignored${TAB}truthx_RDX_ALL.npz) || {${TAB}truthx_RDX_ALL.npz); true || {
size-unchecked${TAB}\"regular file|2364943114\" ]${TAB}\"regular file|\${sz#*|}\" ]
type-unchecked${TAB}\"regular file|2364943114\" ]${TAB}\"\${sz%%|*}|2364943114\" ]
check-dropped${TAB}[ \"\$sz\" = \"regular file|2364943114\" ] ||${TAB}true ||"
QUIET=1; killed=0; total=0
while IFS="$TAB" read -r name old new; do
  total=$((total + 1))
  n=$(python3 -I -c 'import sys; print(sys.argv[1].count(sys.argv[2]))' "$BLOCK" "$old")
  [ "$n" = 1 ] || { echo "MUTANT $name: old text occurs $n times"; continue; }
  M=$(python3 -I -c 'import sys; t, a, b = sys.argv[1:]; print(t.replace(a, b, 1), end="")' "$BLOCK" "$old" "$new")
  fails=0; cases "$M"
  if [ "$fails" -gt 0 ]; then killed=$((killed + 1)); echo "KILLED   $name ($fails cases)"; else echo "SURVIVED $name"; fi
done <<< "$MUTANTS"
echo "SIDECAR-STAT-MUTANTS :: $killed/$total killed"
[ "$killed" -eq "$total" ]
