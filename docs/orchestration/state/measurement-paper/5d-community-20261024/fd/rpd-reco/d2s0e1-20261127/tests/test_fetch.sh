#!/bin/bash
# test_fetch.sh: rpd_d2s0_fetch.sh's state logic, send list and archive, against stubs only.
# usage: bash test_fetch.sh
# A copy of the fetch is re-rooted into a temp directory: the run root, /dev/shm/limres-rpd-flux1 and /proc are replaced,
# so a fake /proc/<pid>/{stat,cmdline} stands in for Linux's. GNU stat, find, sha256sum and base64 are PATH stubs for
# macOS, and date answers GNU's -d; a cat stub can publish chain.rc as the fetch reads /proc/<pid>/stat (a dead runner) and
# a cmp stub as it compares /proc/<pid>/cmdline (a live one): the races in codex-school2's P0 finding 7 and its rebuild
# read. The archive is decoded and its member list must equal the send list exactly. Mutants then weaken the fetch; each
# must fail at least one case.
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
FETCH="$HERE/../rpd_d2s0_fetch.sh"
ROOT=/pscratch/sd/j/josephrb/rpd-reco-d2s0e1-20261127
SHM=/dev/shm/limres-rpd-flux1
T=$(mktemp -d) || exit 9
trap 'rm -rf -- "$T"' EXIT
mkdir -p "$T/bin"
cat > "$T/bin/stat" <<'EOF'
#!/bin/bash
[ "$1" = -c ] && [ "$2" = %s ] && exec python3 -I -c 'import os,sys; print(os.path.getsize(sys.argv[1]))' "$3"
exec /usr/bin/stat "$@"
EOF
cat > "$T/bin/find" <<'EOF'
#!/bin/bash
case " $* " in
  *" -printf "*) exec python3 -I -c 'import os
for d, ds, fs in os.walk("."):
    ds[:] = [x for x in ds if os.path.join(d, x)[2:] not in ("dry/staged", "run/staged", "clone")]
    for f in fs:
        p = os.path.join(d, f)[2:]
        print("-rw-------", os.path.getsize(p), p)' ;;
  *) exec /usr/bin/find "$@" ;;
esac
EOF
cat > "$T/bin/cat" <<'EOF'
#!/bin/bash
if [ -n "${RACE_RC:-}" ] && [[ $1 == */proc/*/stat ]]; then
  echo "rc=0 cause=exit end=2026-11-23T10:00:00Z" > "$RACE_RC"; exit 1
fi
exec /bin/cat "$@"
EOF
cat > "$T/bin/cmp" <<'EOF'
#!/bin/bash
[ -n "${RACE_ALIVE_RC:-}" ] && echo "rc=4 cause=step-p0 end=2026-11-23T10:00:00Z" > "$RACE_ALIVE_RC"
exec /usr/bin/cmp "$@"
EOF
cat > "$T/bin/date" <<'EOF'
#!/bin/bash
if [ "$1" = -u ] && [ "$2" = -d ]; then  # GNU date -u -d TIME +FORMAT, for ISO times ending in Z
  exec python3 -I -c '
import datetime, sys
t = datetime.datetime.strptime(sys.argv[1], "%Y-%m-%dT%H:%M:%SZ")
print(t.strftime(sys.argv[2][1:]))' "$3" "$4"
fi
exec /bin/date "$@"
EOF
printf '#!/bin/bash\nexec shasum -a 256 "$@"\n' > "$T/bin/sha256sum"
printf '#!/bin/bash\n[ "$1" = -w ] && shift 2\nexec /usr/bin/base64 "$@"\n' > "$T/bin/base64"
chmod +x "$T/bin/"*
export PATH="$T/bin:$PATH"
ORIG=$(/bin/cat "$FETCH")
HOST=$(hostname)

rewrite() {  # rewrite FETCH_TEXT -> re-rooted
  python3 -I -c '
import sys
t, root, shm, tmp = sys.argv[1:]
for old, new in ((root, tmp + "/r"), (shm, tmp + "/shm"), ("/proc/", tmp + "/proc/")):
    assert t.count(old) >= 1, old
    t = t.replace(old, new)
print(t, end="")' "$1" "$ROOT" "$SHM" "$T"
}

prepare() {  # prepare -> a root with records, no runner.pid, no chain.rc, an empty fake /proc
  rm -rf -- "$T/r" "$T/proc" "$T/shm"; mkdir -p "$T/r/dry/staged" "$T/r/run/staged" "$T/proc"
  echo '{"step": "pins"}' > "$T/r/dry/pins.json"; echo '{"step": "p0"}' > "$T/r/run/p0.json"
  echo '{"rc": 0}' > "$T/r/sup-pins-dry.json"; echo "4242 x" > "$T/r/handoff.ok"
  echo "x" > "$T/r/dry/staged/big.npz"; echo "pins-dry rc=0" > "$T/r/runner-steps.txt"; echo out > "$T/r/runner.out"
  echo cfg > "$T/r/production-config.ready.json"; echo runner > "$T/r/rpd_d2s0_runner.sh"
  echo stat > "$T/r/stat-d2s0.txt"; echo inputs > "$T/r/inputs-check.txt"; echo fence > "$T/r/fence-overlap.txt"
}
pidfile() { echo "$1 $2 $3 2026-11-23T10:00:00Z" > "$T/r/runner.pid"; }      # pidfile PID HOST TICKS
proc() {  # proc PID TICKS CMDLINE...: a fake /proc entry
  mkdir -p "$T/proc/$1"
  printf '%s (bash) S %s %s 0\n' "$1" "$(seq -s' ' 1 18)" "$2" > "$T/proc/$1/stat"
  local pid=$1; shift 2; printf '%s\0' "$@" > "$T/proc/$pid/cmdline"
}

fetch() {  # fetch FETCH_TEXT -> output, "rc=N", "self: ...", "members: ..."
  rewrite "$1" > "$T/fetch.sh"; cp "$T/fetch.sh" "$T/self.sh"
  local out r
  out=$(bash "$T/fetch.sh" "$T/self.sh" 2>&1); r=$?
  printf '%s\n' "$out"; echo "rc=$r"
  [ -e "$T/self.sh" ] && echo "self: kept" || echo "self: removed"
  if printf '%s\n' "$out" 2>/dev/null | grep -qx '== TAR BEGIN'; then
    printf '%s\n' "$out" | awk '$0 == "== TAR BEGIN" {f=1; next} /^== TAR END / {f=0} f' | /usr/bin/base64 -D > "$T/a.tar"
    echo "members: $(tar -tf "$T/a.tar" | LC_ALL=C sort | paste -sd' ' -)"
  else
    echo "members: none"
  fi
}

check() {  # check NAME OUTPUT LINE...: each LINE is a substring of the output, or a whole line if it starts "members: "
  local name=$1 out=$2 ok=1
  shift 2
  for want in "$@"; do
    case $want in
      "members: "*) printf '%s\n' "$out" 2>/dev/null | grep -qxF -- "$want" || ok=0 ;;
      *) printf '%s\n' "$out" 2>/dev/null | grep -qF -- "$want" || ok=0 ;;
    esac
  done
  if [ "$ok" = 1 ]; then [ "$Q" = 1 ] || echo "ok   $name"; else
    [ "$Q" = 1 ] || { echo "FAIL $name: want [$*]"; printf '%s\n' "$out" | sed 's/^/     /'; }
    fails=$((fails + 1))
  fi
}

MEMBERS="chain.rc dry/pins.json fence-overlap.txt handoff.ok inputs-check.txt production-config.ready.json rpd_d2s0_runner.sh run/p0.json runner-steps.txt runner.out runner.pid stat-d2s0.txt sup-pins-dry.json"
members() { printf '%s\n' $1 | LC_ALL=C sort | paste -sd' ' -; }  # members "LIST" -> the C-sorted, space-joined list
SENT="members: $(members "$MEMBERS")"
NO_RC="members: $(members "${MEMBERS/chain.rc /}")"
RUNNER_CMD="$T/r/rpd_d2s0_runner.sh"

cases() {  # cases FETCH_TEXT
  local F=$1
  prepare; pidfile 4242 "$HOST" 777; echo "rc=0 cause=exit end=2026-11-23T10:00:00Z" > "$T/r/chain.rc"
  check "DONE: exit 0; the archive holds exactly the send list, no staged copy" "$(fetch "$F")" "== state DONE" "rc=0" \
    "self: removed" "$SENT" "dry/staged: 1 files"
  prepare; echo "rc=0 cause=exit end=2026-11-23T10:00:00Z" > "$T/r/chain.rc"
  check "DONE with no runner.pid: chain.rc is authoritative, exit 0" "$(fetch "$F")" "no runner.pid" "== state DONE" "rc=0" \
    "$(printf '%s\n' "$SENT" | sed 's/ runner.pid / /')"
  prepare; pidfile 4242 login99 777; echo "rc=4 cause=step-p0-dry end=2026-11-23T10:00:00Z" > "$T/r/chain.rc"
  check "STOP from another node: chain.rc rc 4, exit 12" "$(fetch "$F")" "== state STOP" "rc=12" "chain.rc: rc=4 cause=step-p0-dry"
  prepare; pidfile 4242 "$HOST" 777; echo "rc=0 cause=exit" > "$T/r/chain.rc"
  check "a malformed chain.rc (no end time): exit 9, nothing sent" "$(fetch "$F")" "CANNOT TELL: chain.rc is malformed" "rc=9" \
    "members: none"
  prepare; pidfile 4242 "$HOST" 777; printf 'rc=0 cause=exit end=2026-11-23T10:00:00Z\nrc=4 cause=x end=2026-11-23T10:00:00Z\n' > "$T/r/chain.rc"
  check "a two-line chain.rc: exit 9" "$(fetch "$F")" "CANNOT TELL: chain.rc is malformed" "rc=9" "members: none"
  prepare; pidfile 4242 "$HOST" 777; printf 'rc=0 cause=exit end=2026-11-23T10:00:00Z\n\n' > "$T/r/chain.rc"
  check "a chain.rc with a trailing blank line: exit 9" "$(fetch "$F")" "CANNOT TELL: chain.rc is malformed" "rc=9" "members: none"
  prepare; pidfile 4242 "$HOST" 777; printf 'rc=0 cause=ex\0it end=2026-11-23T10:00:00Z\n' > "$T/r/chain.rc"
  check "a NUL byte in chain.rc: exit 9" "$(fetch "$F")" "CANNOT TELL: chain.rc contains NUL bytes" "rc=9" "members: none"
  prepare; pidfile 4242 "$HOST" 777; echo "rc=0 cause=a b end=2026-11-23T10:00:00Z" > "$T/r/chain.rc"
  check "a cause with a space: exit 9" "$(fetch "$F")" "CANNOT TELL: chain.rc is malformed" "rc=9" "members: none"
  prepare; pidfile 4242 "$HOST" 777; echo "rc=0 cause=exit end=2026-02-30T10:00:00Z" > "$T/r/chain.rc"
  check "an impossible end time (February 30): exit 9" "$(fetch "$F")" "is not a real UTC time" "rc=9" "members: none"
  prepare; pidfile 4242 "$HOST" 777; proc 4242 777 bash "$RUNNER_CMD"
  check "RUNNING: the start time and exact command line match, exit 10, nothing sent" "$(fetch "$F")" "RUNNING: runner 4242" \
    "rc=10" "members: none"
  prepare; pidfile 4242 "$HOST" 777; proc 4242 778 bash "$RUNNER_CMD"
  check "a reused pid (another start time): gone, exit 11" "$(fetch "$F")" "== state GONE" "rc=11" "the cleanup is unverified"
  prepare; pidfile 4242 "$HOST" 777; proc 4242 777 vim "$RUNNER_CMD"
  check "another command naming the runner: gone, exit 11" "$(fetch "$F")" "== state GONE" "rc=11"
  prepare; pidfile 4242 "$HOST" 777; proc 4242 777 bash "$RUNNER_CMD.bak"
  check "a command line that only contains the runner's path: gone, exit 11" "$(fetch "$F")" "== state GONE" "rc=11"
  prepare; pidfile 4242 "$HOST" 777; proc 4242 777 bash "$RUNNER_CMD" ""
  check "the exact command line plus an empty argument: gone, exit 11" "$(fetch "$F")" "== state GONE" "rc=11"
  prepare; pidfile 4242 "$HOST" 777; mkdir -p "$T/shm"
  check "gone without chain.rc: exit 11, cleanup unverified, /dev/shm reported, records sent" "$(fetch "$F")" "== state GONE" \
    "rc=11" "still exists" "$NO_RC"
  prepare; pidfile 4242 "$HOST" 777; proc 4242 777 bash "$RUNNER_CMD"
  check "chain.rc published while the fetch probes a dead runner's /proc: the terminal record wins, DONE" \
    "$(RACE_RC="$T/r/chain.rc" fetch "$F")" "== state DONE" "rc=0" "chain.rc: rc=0 cause=exit"
  prepare; pidfile 4242 "$HOST" 777; proc 4242 777 bash "$RUNNER_CMD"
  check "chain.rc published while the fetch confirms a live runner: the terminal record wins, STOP" \
    "$(RACE_ALIVE_RC="$T/r/chain.rc" fetch "$F")" "== state STOP" "rc=12" "chain.rc: rc=4 cause=step-p0"
  prepare; pidfile 4242 login99 777
  check "no chain.rc, another node: exit 9, nothing sent" "$(fetch "$F")" "CANNOT TELL: no chain.rc, and the runner ran on login99" \
    "rc=9" "members: none"
  prepare
  check "no chain.rc and no runner.pid: exit 9" "$(fetch "$F")" "CANNOT TELL: no chain.rc and no runner.pid" "rc=9" "members: none"
  rm -rf -- "$T/r"
  check "no root: exit 9" "$(fetch "$F")" "does not exist" "rc=9" "self: removed"
}

fails=0; Q=0
cases "$ORIG"
echo "FETCH-TESTS :: $([ "$fails" -eq 0 ] && echo PASS || echo "FAIL ($fails)")"
[ "$fails" -eq 0 ] || exit 1

TAB=$(printf '\t')
MUTANTS="pidfile-required${TAB}  echo \"no runner.pid\"${TAB}  echo \"no runner.pid\"; finish 9
no-recheck${TAB}  if ! terminal; then${TAB}  if true; then
ticks-unchecked${TAB}[ \"\${fields[19]}\" = \"\$rticks\" ] && ${TAB}
cmdline-unchecked${TAB}cmp -s \"/proc/\$rpid/cmdline\" <(printf 'bash\\0%s\\0' \"\$R/rpd_d2s0_runner.sh\")${TAB}true
running-without-recheck${TAB}if [ \"\$alive\" -eq 1 ] && [ ! -f chain.rc ]; then${TAB}if [ \"\$alive\" -eq 1 ]; then
one-line-unchecked${TAB}[ \"\$lines\" = 1 ] && ${TAB}
cause-loose${TAB}cause=[A-Za-z0-9_.-]+${TAB}cause=.+
date-unchecked${TAB}[ \"\$(date -u -d \"\$end\" +%Y-%m-%dT%H:%M:%SZ 2>/dev/null)\" = \"\$end\" ] ||${TAB}true ||
malformed-accepted${TAB}|| { echo \"CANNOT TELL: chain.rc is malformed\"; finish 9; }${TAB}|| true
staged-sent${TAB}dry/*.json run/*.json; do${TAB}dry/*.json run/*.json dry/staged/*; do
dead-is-running${TAB}  alive=0${TAB}  alive=1
nul-unchecked${TAB}LC_ALL=C tr -d '\\000' < chain.rc | cmp -s - chain.rc ||${TAB}true ||"
Q=1; killed=0; total=0
while IFS="$TAB" read -r name old new; do
  total=$((total + 1))
  n=$(python3 -I -c 'import sys; print(sys.argv[1].count(sys.argv[2]))' "$ORIG" "$old")
  [ "$n" = 1 ] || { echo "MUTANT $name: old text occurs $n times"; continue; }
  M=$(python3 -I -c 'import sys; t, a, b = sys.argv[1:]; print(t.replace(a, b, 1), end="")' "$ORIG" "$old" "$new")
  fails=0; cases "$M"
  if [ "$fails" -gt 0 ]; then killed=$((killed + 1)); echo "KILLED   $name ($fails cases)"; else echo "SURVIVED $name"; fi
done <<< "$MUTANTS"
echo "FETCH-MUTANTS :: $killed/$total killed"
[ "$killed" -eq "$total" ]
