#!/bin/bash
# test_launch.sh: rpd_d2s0_launch.sh's three-lane ack.txt guard, exit status and cert check, against stubs only (flux3's
# test adapted; the director's acceptance of 2026-11-26: lines ACK-UTC <time> <lane> for cov2d, tier3-design and
# minerva-lib, in that order, each at most 6 h old, then the ack texts; adapted from the
# P0 package's test; flux3's guard reads one snapshot of the ack file and writes those exact bytes into the session).
# usage: bash test_launch.sh
# A copy of the launcher runs in a throwaway git repository beside DUMMY connect and fetch scripts. Its two pinned shas
# are re-pointed at the dummies, so the real connect can never run. ssh, ssh-keygen and sha256sum are PATH stubs:
# - ssh runs the remote command locally, with /dev/shm/ mapped to a temp directory;
# - ssh-keygen prints a cert end time the case chooses, so the real cert is never read.
# Nothing is contacted. The ack cases follow the director's acceptance of 2026-11-26: connect requires one ack file
# whose first three lines are "ACK-UTC <YYYY-MM-DDTHH:MM:SSZ> <lane>" for cov2d, tier3-design and minerva-lib, in that
# order, each at most 6 h old, then the ack texts, copied into the session byte for byte.
# Each case states the launcher's expected rc. The mutants then remove or weaken each guard, and each must fail a case.
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
LAUNCH="$HERE/../rpd_d2s0_launch.sh"
T=$(mktemp -d) || exit 9
trap 'rm -rf -- "$T"' EXIT
mkdir -p "$T/bin" "$T/shm"
cat > "$T/bin/ssh" <<'EOF'
#!/bin/bash
for last; do :; done
case $last in
  "ssh "*) exec bash -c "$last" ;;
  *) exec bash -c "${last//\/dev\/shm\//$SHM/}" ;;
esac
EOF
cat > "$T/bin/ssh-keygen" <<'EOF'
#!/bin/bash
[ -n "${CERT_TO:-}" ] && printf '        Valid: from 2026-11-22T00:00:00 to %s\n' "$CERT_TO"
exit 0
EOF
printf '#!/bin/bash\nexec shasum -a 256 "$@"\n' > "$T/bin/sha256sum"
cat > "$T/bin/date" <<'EOF'
#!/bin/bash
# The second `date -u +%s` call (the ack age; the first is the cert check) fails when FAKE_CLOCK is set.
if [ -n "${FAKE_CLOCK:-}" ] && [ "$*" = "-u +%s" ]; then
  n=$(( $(cat "$FAKE_CLOCK" 2>/dev/null || echo 0) + 1 )); echo "$n" > "$FAKE_CLOCK"
  [ "$n" -ge 2 ] && exit 1
fi
exec /bin/date "$@"
EOF
chmod +x "$T/bin/ssh" "$T/bin/ssh-keygen" "$T/bin/sha256sum" "$T/bin/date"
export SHM="$T/shm" PATH="$T/bin:$PATH"

setup() {  # setup LAUNCHER_TEXT: a fresh repo with the launcher copy and dummies exiting $CONNECT_RC and 10
  rm -rf -- "$T/repo"; mkdir -p "$T/repo"; git -C "$T/repo" init -q
  printf '#!/bin/bash\necho "dummy connect"; rm -f -- "$1"; exit %s\n' "$CONNECT_RC" > "$T/repo/rpd_d2s0_connect.sh"
  printf '#!/bin/bash\necho "NOT FINISHED (dummy fetch)"; rm -f -- "$1"; exit 10\n' > "$T/repo/rpd_d2s0_fetch.sh"
  c=$(shasum -a 256 "$T/repo/rpd_d2s0_connect.sh" | cut -d' ' -f1)
  f=$(shasum -a 256 "$T/repo/rpd_d2s0_fetch.sh" | cut -d' ' -f1)
  printf '%s' "$1" | sed -E "s/(connect\) S=.*SHA=)[0-9a-f]{64}/\1$c/; s/(fetch\)   S=.*SHA=)[0-9a-f]{64}/\1$f/" \
    > "$T/repo/rpd_d2s0_launch.sh"
  [ "$(grep -c -e "$c" -e "$f" "$T/repo/rpd_d2s0_launch.sh")" = 2 ] || { echo "SETUP: shas not re-pointed"; exit 9; }
}

utc_in() { date -u -v"$1" +%Y-%m-%dT%H:%M:%SZ; }  # utc_in +2H, -7H, ...
ack3() {  # ack3 FILE T1 T2 T3 [TEXT]: the three lanes in order with the given offsets
  { printf 'ACK-UTC %s cov2d\n' "$(utc_in "$2")"; printf 'ACK-UTC %s tier3-design\n' "$(utc_in "$3")"
    printf 'ACK-UTC %s minerva-lib\n' "$(utc_in "$4")"; } > "$1"
  [ "$#" -ge 5 ] && printf '%s\n' "$5" >> "$1"
  return 0
}

# launch MODE [ACK] -> prints "rc=N" last, then "copied=yes|no"; the session dir is new and empty
launch() {
  d=$(mktemp -d "$T/session.XXXX")
  out=$(bash "$T/repo/rpd_d2s0_launch.sh" "$1" "$d" login01 ${2:+"$2"} 2>&1); r=$?
  echo "$out"; echo "rc=$r"
  if [ -n "${2:-}" ] && [ -f "$d/ack.txt" ] && cmp -s "$2" "$d/ack.txt"; then echo "copied=yes"; else echo "copied=no"; fi
}

check() {  # check NAME EXPECTED_RC EXPECTED_LINE OUTPUT
  rc=$(printf '%s\n' "$4" | sed -n 's/^rc=//p' | tail -1)
  if [ "$rc" = "$2" ] && printf '%s\n' "$4" | grep -qF -- "$3"; then [ "$QUIET" = 1 ] || echo "ok   $1 (rc $rc)"
  else [ "$QUIET" = 1 ] || { echo "FAIL $1: rc [$rc], want $2 and [$3]"; printf '%s\n' "$4" | sed 's/^/     /'; }
       fails=$((fails + 1)); fi
}

cases() {  # cases LAUNCHER_TEXT
  CERT_TO=$(date -u -v+20H +%Y-%m-%dT%H:%M:%S); export CERT_TO
  A="$T/ack.txt"
  CONNECT_RC=3; setup "$1"
  ack3 "$A" -10M -12M -15M "cov2d, tier3-design, minerva-lib -> LR: ACK for rpd_d2s0."
  check "three fresh acks, connect script exits 3: launcher exits 3, ack copied" 3 "copied=yes" "$(launch connect "$A")"
  check "three fresh acks: each lane reported" 3 "minerva-lib ack" "$(launch connect "$A")"
  CONNECT_RC=0; setup "$1"
  check "three fresh acks, connect exits 0: launcher exits 0" 0 "script rc=0" "$(launch connect "$A")"
  check "fetch needs no ack; unfinished: exit 10" 10 "script rc=10" "$(launch fetch)"
  check "connect without an ack file: STOP 9" 9 "STOP: connect needs the three-lane ack file" "$(launch connect)"
  check "connect with a missing ack path: STOP 9" 9 "STOP: connect needs the three-lane ack file" "$(launch connect "$T/none.txt")"
  ack3 "$A" -10M -7H -10M "tier3-design's ack is stale"
  check "tier3-design's line 7 h old: STOP 9, no copy left" 9 "copied=no" "$(launch connect "$A")"
  check "tier3-design's line 7 h old: the reason" 9 "tier3-design's ack is older than 6 h" "$(launch connect "$A")"
  ack3 "$A" -7H -10M -10M "cov2d's ack is stale"
  check "cov2d's line 7 h old: STOP 9" 9 "cov2d's ack is older than 6 h" "$(launch connect "$A")"
  ack3 "$A" -10M -10M +2H "a future minerva-lib ack"
  check "minerva-lib's line 2 h in the future: STOP 9" 9 "minerva-lib's ack time is in the future" "$(launch connect "$A")"
  ack3 "$A" -5H -5H -5H "acks 5 h old"
  check "three acks 5 h old: accepted" 0 "copied=yes" "$(launch connect "$A")"
  { printf 'ACK-UTC %s tier3-design\n' "$(utc_in -10M)"; printf 'ACK-UTC %s cov2d\n' "$(utc_in -10M)"
    printf 'ACK-UTC %s minerva-lib\n' "$(utc_in -10M)"; echo "out of order"; } > "$A"
  check "lanes out of order: STOP 9" 9 "line 1 names 'tier3-design', not cov2d" "$(launch connect "$A")"
  { printf 'ACK-UTC %s cov2d\n' "$(utc_in -10M)"; printf 'ACK-UTC %s tier3-design\n' "$(utc_in -10M)"; echo "two acks only"; } > "$A"
  check "only two ACK-UTC lines: STOP 9" 9 "line 3 is not" "$(launch connect "$A")"
  { printf '  ACK-UTC %s cov2d\n' "$(utc_in -10M)"; printf 'ACK-UTC %s tier3-design\n' "$(utc_in -10M)"
    printf 'ACK-UTC %s minerva-lib\n' "$(utc_in -10M)"; echo "padded"; } > "$A"
  check "line 1 with leading spaces: STOP 9" 9 "line 1 is not" "$(launch connect "$A")"
  { printf 'ACK-UTC %s cov2d\n' "$(utc_in -10M)"; printf 'ACK-UTC %s tier3-design extra\n' "$(utc_in -10M)"
    printf 'ACK-UTC %s minerva-lib\n' "$(utc_in -10M)"; echo "trailing words"; } > "$A"
  check "line 2 with trailing words: STOP 9" 9 "line 2 is not" "$(launch connect "$A")"
  { printf 'ACK-UTC %s COV2D\n' "$(utc_in -10M)"; printf 'ACK-UTC %s tier3-design\n' "$(utc_in -10M)"
    printf 'ACK-UTC %s minerva-lib\n' "$(utc_in -10M)"; echo "uppercase lane"; } > "$A"
  check "an uppercase lane name: STOP 9" 9 "line 1 is not" "$(launch connect "$A")"
  { printf 'ACK-UTC %s cov2d\n' "$(utc_in -10M)"; printf 'ACK-UTC 2026-13-40T25:61:61Z tier3-design\n'
    printf 'ACK-UTC %s minerva-lib\n' "$(utc_in -10M)"; echo "impossible time"; } > "$A"
  check "line 2 with an impossible time: STOP 9" 9 "line 2's time" "$(launch connect "$A")"
  { printf 'ACK-UTC %s:60Z cov2d\n' "$(date -u -v-10M +%Y-%m-%dT%H:%M)"; printf 'ACK-UTC %s tier3-design\n' "$(utc_in -10M)"
    printf 'ACK-UTC %s minerva-lib\n' "$(utc_in -10M)"; echo "seconds 60"; } > "$A"
  check "line 1 with seconds 60 (parses, but not a real time): STOP 9" 9 "not a real UTC time" "$(launch connect "$A")"
  ack3 "$A" -10M -10M -10M
  check "no text after the three lines: STOP 9" 9 "no ack text" "$(launch connect "$A")"
  ack3 "$A" -10M -10M -10M "   "
  check "ack text only whitespace: STOP 9" 9 "no ack text" "$(launch connect "$A")"
  { printf 'ACK-UTC %s cov2d\n' "$(utc_in -10M)"; printf 'ACK-UTC %s tier3-design\n' "$(utc_in -10M)"
    printf 'ACK-UTC %s minerva-lib\n' "$(utc_in -10M)"; printf 'ACKs \000 here\n'; } > "$A"
  check "a NUL byte: STOP 9" 9 "contains NUL bytes" "$(launch connect "$A")"
  { printf 'ACK-UTC %s cov2d\n' "$(utc_in -10M)"; printf 'ACK-UTC %s tier3-design\n' "$(utc_in -10M)"
    printf 'ACK-UTC %s minerva-lib\n' "$(utc_in -10M)"; printf 'ACKs, no final newline'; } > "$A"
  check "no final newline: accepted and copied byte for byte" 0 "copied=yes" "$(launch connect "$A")"
  ack3 "$A" -10M -10M -10M "ACKs."
  rm -f "$T/clock.n"
  check "the clock read for the ack ages fails: STOP 9, no copy left" 9 "copied=no" "$(FAKE_CLOCK="$T/clock.n" launch connect "$A")"
  rm -f "$T/clock.n"
  check "the clock read fails: the reason" 9 "the clock could not be read" "$(FAKE_CLOCK="$T/clock.n" launch connect "$A")"
  rm -f "$T/clock.n"
  CERT_TO=$(date -u -v+10M +%Y-%m-%dT%H:%M:%S); export CERT_TO
  check "cert ends in 10 minutes: STOP 9" 9 "STOP: the cert ends within 30 minutes" "$(launch connect "$A")"
  CERT_TO=$(date -u -v+20H +%Y-%m-%dT%H:%M:%S); export CERT_TO
  check "fence mode: refused" 9 "STOP: fence mode is not used for rpd_d2s0" "$(launch fence)"
  setup "$1"; echo "# tampered" >> "$T/repo/rpd_d2s0_connect.sh"
  check "connect script not the pinned one: STOP 8" 8 "STOP: the local connect script is not the approved one" "$(launch connect "$A")"
}

TEXT=$(cat "$LAUNCH")
fails=0; QUIET=0
cases "$TEXT"
echo "LAUNCH-TESTS :: $([ "$fails" -eq 0 ] && echo PASS || echo "FAIL ($fails)")"
[ "$fails" -eq 0 ] || exit 1

# Mutants: NAME<TAB>OLD<TAB>NEW, each OLD occurring exactly once in the launcher.
TAB=$(printf '\t')
MUTANTS="ack-guard-skipped${TAB}if [ \"\$MODE\" = connect ]; then${TAB}if false; then
ack-file-unchecked${TAB}[ -n \"\$ACK\" ] && [ -f \"\$ACK\" ] ||${TAB}true ||
ack-stale-widened${TAB}[ \"\$age\" -le 21600 ]${TAB}[ \"\$age\" -le 86400 ]
ack-future-unchecked${TAB}[ \"\$age\" -ge -300 ] ||${TAB}true ||
ack-line-unanchored${TAB}=~ ^ACK-UTC${TAB}=~ ACK-UTC
ack-line-open-ended${TAB}([a-z0-9-]+)\$ ]]${TAB}([a-z0-9-]+) ]]
ack-lane-unchecked${TAB}[ \"\$who\" = \"\$lane\" ] ||${TAB}true ||
ack-two-lanes${TAB}for lane in cov2d tier3-design minerva-lib; do${TAB}for lane in cov2d tier3-design; do
ack-time-roundtrip-dropped${TAB}[ \"\$(TZ=UTC date -j -r \"\$ack_s\" +%Y-%m-%dT%H:%M:%SZ)\" = \"\$when\" ] ||${TAB}true ||
ack-text-unchecked${TAB}[ \"\$(sed -n '4,\$p' \"\$A\" | grep -c '[^[:space:]]')\" -ge 1 ] ||${TAB}true ||
ack-text-from-line-2${TAB}sed -n '4,\$p'${TAB}sed -n '2,\$p'
ack-copy-dropped${TAB}cp \"\$ACK\" \"\$A\" ||${TAB}touch \"\$A\" ||
ack-nul-unchecked${TAB}cmp -s - \"\$A\" || bad_ack${TAB}true || bad_ack
refusal-keeps-copy${TAB}bad_ack() { rm -f -- \"\$A\"; ${TAB}bad_ack() { 
clock-unchecked${TAB}now=\$(date -u +%s) && [[ \$now =~ ^[0-9]+\$ ]] || bad_ack \"the clock could not be read\"${TAB}now=\$(date -u +%s)
echo-last${TAB}bash \\\"\\\$f\\\" \\\"\\\$f\\\"; rc=\\\$?; echo \\\"script rc=\\\$rc\\\"; exit \\\$rc${TAB}bash \\\"\\\$f\\\" \\\"\\\$f\\\"; echo \\\"script rc=\\\$?\\\""
QUIET=1; killed=0; total=0
while IFS="$TAB" read -r name old new; do
  total=$((total + 1))
  n=$(python3 -I -c 'import sys; print(sys.argv[1].count(sys.argv[2]))' "$TEXT" "$old")
  [ "$n" = 1 ] || { echo "MUTANT $name: old text occurs $n times"; continue; }
  M=$(python3 -I -c 'import sys; t, a, b = sys.argv[1:]; print(t.replace(a, b, 1), end="")' "$TEXT" "$old" "$new")
  fails=0; cases "$M"
  if [ "$fails" -gt 0 ]; then killed=$((killed + 1)); echo "KILLED   $name ($fails cases)"; else echo "SURVIVED $name"; fi
done <<< "$MUTANTS"
echo "LAUNCH-MUTANTS :: $killed/$total killed"
[ "$killed" -eq "$total" ]
