#!/bin/bash
# test_launch.sh: rpd_d2s0_launch.sh's ack.txt guard, exit status and cert check, against stubs only (flux3's test, renamed;
# P0's launcher carries flux3's guard, which reads one snapshot of the ack file and writes those exact bytes into the session).
# usage: bash test_launch.sh
# A copy of the launcher runs in a throwaway git repository beside DUMMY connect and fetch scripts. Its two pinned shas
# are re-pointed at the dummies, so the real connect can never run. ssh, ssh-keygen and sha256sum are PATH stubs:
# - ssh runs the remote command locally, with /dev/shm/ mapped to a temp directory;
# - ssh-keygen prints a cert end time the case chooses, so the real cert is never read.
# Nothing is contacted. The ack cases follow the director's ruling of 2026-11-23: connect requires cov2d's ack file,
# first line "ACK-UTC <YYYY-MM-DDTHH:MM:SSZ>" at most 6 h old, then the ack text, copied into the session.
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
ack() {  # ack FILE FIRST_LINE [TEXT]
  printf '%s\n' "$2" > "$1"
  [ "$#" -ge 3 ] && printf '%s\n' "$3" >> "$1"
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
  ack "$A" "ACK-UTC $(utc_in -10M)" "cov2d -> LR: ACK for rpd_d2s0."
  check "fresh ack, connect script exits 3: launcher exits 3, ack copied" 3 "copied=yes" "$(launch connect "$A")"
  CONNECT_RC=0; setup "$1"
  check "fresh ack, connect exits 0: launcher exits 0" 0 "script rc=0" "$(launch connect "$A")"
  check "fetch needs no ack; unfinished: exit 10" 10 "script rc=10" "$(launch fetch)"
  check "connect without an ack file: STOP 9" 9 "STOP: connect needs cov2d's ack file" "$(launch connect)"
  check "connect with a missing ack path: STOP 9" 9 "STOP: connect needs cov2d's ack file" "$(launch connect "$T/none.txt")"
  ack "$A" "ACK-UTC $(utc_in -7H)" "old ack"
  check "ack 7 h old: STOP 9, and no ack copy is left in the session" 9 "copied=no" "$(launch connect "$A")"
  check "ack 7 h old: the reason" 9 "older than 6 h" "$(launch connect "$A")"
  printf 'ACK-UTC %s\ncov2d -> LR: ACK, no final newline' "$(utc_in -10M)" > "$A"
  check "ack without a final newline: accepted and copied byte for byte" 0 "copied=yes" "$(launch connect "$A")"
  printf 'ACK-UTC %s\ncov2d \000ACK\n' "$(utc_in -10M)" > "$A"
  check "ack with a NUL byte: STOP 9" 9 "contains NUL bytes" "$(launch connect "$A")"
  ack "$A" "ACK-UTC $(utc_in -5H)" "ack 5 h old"
  check "ack 5 h old: accepted" 0 "copied=yes" "$(launch connect "$A")"
  ack "$A" "ACK-UTC $(utc_in +2H)" "future ack"
  check "ack 2 h in the future: STOP 9" 9 "in the future" "$(launch connect "$A")"
  ack "$A" "ACK $(utc_in -10M)" "no UTC tag"
  check "first line without ACK-UTC: STOP 9" 9 "first line is not" "$(launch connect "$A")"
  ack "$A" "  ACK-UTC $(utc_in -10M)" "leading spaces"
  check "first line with leading spaces: STOP 9" 9 "first line is not" "$(launch connect "$A")"
  ack "$A" "ACK-UTC $(utc_in -10M) extra" "trailing words"
  check "first line with trailing words: STOP 9" 9 "first line is not" "$(launch connect "$A")"
  ack "$A" "ACK-UTC 2026-13-40T25:61:61Z" "not a real time"
  check "first line with an impossible time: STOP 9" 9 "ack.txt's time" "$(launch connect "$A")"
  ack "$A" "ACK-UTC $(date -u -v-10M +%Y-%m-%dT%H:%M):60Z" "seconds 60, which BSD date rolls into the next minute"
  check "first line with seconds 60 (parses, but not a real time): STOP 9" 9 "not a real UTC time" "$(launch connect "$A")"
  ack "$A" "ACK-UTC $(utc_in -10M)"
  check "ack with no text after its first line: STOP 9" 9 "no ack text" "$(launch connect "$A")"
  ack "$A" "ACK-UTC $(utc_in -10M)" "   "
  check "ack text only whitespace: STOP 9" 9 "no ack text" "$(launch connect "$A")"
  ack "$A" "ACK-UTC $(utc_in -10M)" "cov2d -> LR: ACK."
  rm -f "$T/clock.n"
  check "the clock read for the ack's age fails: STOP 9, no copy left" 9 "copied=no" "$(FAKE_CLOCK="$T/clock.n" launch connect "$A")"
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
ack-line-open-ended${TAB}:[0-9]{2}Z)\$ ]]${TAB}:[0-9]{2}Z) ]]
ack-time-roundtrip-dropped${TAB}[ \"\$(TZ=UTC date -j -r \"\$ack_s\" +%Y-%m-%dT%H:%M:%SZ)\" = \"\$when\" ] ||${TAB}true ||
ack-text-unchecked${TAB}[ \"\$(sed -n '2,\$p' \"\$A\" | grep -c '[^[:space:]]')\" -ge 1 ] ||${TAB}true ||
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
