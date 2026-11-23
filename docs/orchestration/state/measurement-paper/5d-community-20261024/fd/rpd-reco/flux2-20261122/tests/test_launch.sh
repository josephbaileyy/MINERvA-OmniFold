#!/bin/bash
# test_launch.sh: rpd_flux2_launch.sh's exit status and cert check, against stubs only.
# usage: bash test_launch.sh
# A copy of the launcher runs in a throwaway git repository beside DUMMY connect and fetch scripts. Its two pinned shas
# are re-pointed at the dummies, so the real connect can never run. ssh, ssh-keygen and sha256sum are PATH stubs:
# - ssh runs the remote command locally, with /dev/shm/ mapped to a temp directory;
# - ssh-keygen prints a cert end time the case chooses, so the real cert is never read.
# Nothing is contacted.
# Each case states the launcher's expected rc. The mutants then put back the flux1 tail (the echo last) and drop the
# cert check, and each must fail a case.
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
LAUNCH="$HERE/../rpd_flux2_launch.sh"
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
chmod +x "$T/bin/ssh" "$T/bin/ssh-keygen" "$T/bin/sha256sum"
export SHM="$T/shm" PATH="$T/bin:$PATH"

# setup LAUNCHER_TEXT: a fresh repo with the launcher copy and dummies exiting $CONNECT_RC and 10
setup() {
  rm -rf -- "$T/repo"; mkdir -p "$T/repo"; git -C "$T/repo" init -q
  printf '#!/bin/bash\necho "dummy connect"; rm -f -- "$1"; exit %s\n' "$CONNECT_RC" > "$T/repo/rpd_flux2_connect.sh"
  printf '#!/bin/bash\necho "NOT FINISHED (dummy fetch)"; rm -f -- "$1"; exit 10\n' > "$T/repo/rpd_flux2_fetch.sh"
  c=$(shasum -a 256 "$T/repo/rpd_flux2_connect.sh" | cut -d' ' -f1)
  f=$(shasum -a 256 "$T/repo/rpd_flux2_fetch.sh" | cut -d' ' -f1)
  printf '%s' "$1" | sed -E "s/(connect\) S=.*SHA=)[0-9a-f]{64}/\1$c/; s/(fetch\)   S=.*SHA=)[0-9a-f]{64}/\1$f/" \
    > "$T/repo/rpd_flux2_launch.sh"
  [ "$(grep -c -e "$c" -e "$f" "$T/repo/rpd_flux2_launch.sh")" = 2 ] || { echo "SETUP: shas not re-pointed"; exit 9; }
}

in_hours() { date -u -v+"$1"H +%Y-%m-%dT%H:%M:%S; }
in_minutes() { date -u -v+"$1"M +%Y-%m-%dT%H:%M:%S; }

# launch MODE [SESSION_DIR] -> prints "rc=N" last; the session dir is new and empty
launch() {
  d=${2:-$(mktemp -d "$T/session.XXXX")}
  out=$(bash "$T/repo/rpd_flux2_launch.sh" "$1" "$d" login01 2>&1); r=$?; echo "$out"; echo "rc=$r"
}

check() {  # check NAME EXPECTED_RC EXPECTED_LINE OUTPUT
  rc=$(printf '%s\n' "$4" | sed -n 's/^rc=//p' | tail -1)
  if [ "$rc" = "$2" ] && printf '%s\n' "$4" | grep -qF -- "$3"; then [ "$QUIET" = 1 ] || echo "ok   $1 (rc $rc)"
  else [ "$QUIET" = 1 ] || { echo "FAIL $1: rc [$rc], want $2 and [$3]"; printf '%s\n' "$4" | sed 's/^/     /'; }
       fails=$((fails + 1)); fi
}

cases() {  # cases LAUNCHER_TEXT
  CERT_TO=$(in_hours 20); export CERT_TO
  CONNECT_RC=3; setup "$1"
  check "connect script exits 3: launcher exits 3" 3 "script rc=3" "$(launch connect)"
  CONNECT_RC=0; setup "$1"
  check "connect script exits 0: launcher exits 0" 0 "script rc=0" "$(launch connect)"
  check "fetch unfinished (exit 10): launcher exits 10" 10 "script rc=10" "$(launch fetch)"
  CERT_TO=$(in_minutes 10); export CERT_TO
  sd=$(mktemp -d "$T/session.XXXX"); out=$(launch connect "$sd")
  [ -e "$sd/session.out" ] && out="$out
ssh was called"
  check "cert ends in 10 minutes: STOP before ssh" 9 "STOP: the cert ends within 30 minutes" "$out"
  printf '%s\n' "$out" | grep -q "ssh was called" && fails=$((fails + 1))
  CERT_TO=""; export CERT_TO
  check "cert end time unreadable: STOP" 9 "STOP: cannot read the cert's end time" "$(launch connect)"
  CERT_TO=$(in_hours 20); export CERT_TO
  CONNECT_RC=0; setup "$1"; echo "# tampered" >> "$T/repo/rpd_flux2_connect.sh"
  check "fence mode (cov2d_fence.sh rev 1 calls squeue): refused" 9 "STOP: fence mode is not used for rpd_flux2" "$(launch fence)"
  check "connect script not the pinned one: STOP 8" 8 "STOP: the local connect script is not the approved one" "$(launch connect)"
}

TEXT=$(cat "$LAUNCH")
fails=0; QUIET=0
cases "$TEXT"
echo "LAUNCH-TESTS :: $([ "$fails" -eq 0 ] && echo PASS || echo "FAIL ($fails)")"
[ "$fails" -eq 0 ] || exit 1

OLD_TAIL='bash \"\$f\" \"\$f\"; echo \"script rc=\$?\"'
NEW_TAIL='bash \"\$f\" \"\$f\"; rc=\$?; echo \"script rc=\$rc\"; exit \$rc'
QUIET=1; killed=0; total=0
for name in echo-last cert-check-dropped; do
  total=$((total + 1))
  case $name in
    echo-last) M=$(python3 -I -c 'import sys; t, a, b = sys.argv[1:]; assert t.count(a) == 1; print(t.replace(a, b), end="")' "$TEXT" "$NEW_TAIL" "$OLD_TAIL") ;;
    cert-check-dropped) M=$(printf '%s\n' "$TEXT" | grep -v -e '^to=' -e '^to_s=' -e 'the cert ends within' -e '^echo "cert valid') ;;
  esac
  [ "$M" != "$TEXT" ] || { echo "MUTANT $name: not applied"; continue; }
  fails=0; cases "$M"
  if [ "$fails" -gt 0 ]; then killed=$((killed + 1)); echo "KILLED   $name ($fails cases)"; else echo "SURVIVED $name"; fi
done
echo "LAUNCH-MUTANTS :: $killed/$total killed"
[ "$killed" -eq "$total" ]
