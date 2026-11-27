#!/bin/bash
# test_connect_start.sh: the connect's startup and cleanup handoff (step 9 and its finish/traps), cut from
# rpd_d2s0_connect.sh and run locally against a stub runner, with real processes and signals.
# usage: bash test_connect_start.sh
# The cut is the connect's preamble (umask through the three traps) and step 9, re-rooted into a temp directory; the
# runner heredoc is replaced by a copy of a stub runner. setsid is a PATH stub that calls setsid(2) and execs (macOS has
# no setsid command); nice -n 19 is passed to /usr/bin/nice; PY is this machine's python3, which runs the connect's
# SIGINT-reset launch wrapper as on the node. The connect's 30 s pid wait is cut to 2 s. Stub modes:
#   normal    writes runner.pid ("$$ host ticks time"), waits for handoff.ok, records it, exits
#   silent    writes no runner.pid, starts a background child that ignores TERM (only the group KILL stops it), and
#             sleeps (a delayed startup)
#   wrongpid  writes a runner.pid naming another pid and sleeps
# Mutants then weaken the connect; each must fail at least one case.
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
CONNECT="$HERE/../rpd_d2s0_connect.sh"
ROOT=/pscratch/sd/j/josephrb/rpd-reco-d2s0e1-20261127
SHM=/dev/shm/limres-rpd-flux1
T=$(mktemp -d) || exit 9
trap 'pkill -KILL -f "$T/" 2>/dev/null; rm -rf -- "$T"' EXIT
mkdir -p "$T/bin"
cat > "$T/bin/setsid" <<'EOF'
#!/bin/bash
exec python3 -I -c 'import os, sys; os.setsid(); os.execvp(sys.argv[1], sys.argv[1:])' "$@"
EOF
printf '#!/bin/bash\nexec shasum -a 256 "$@"\n' > "$T/bin/sha256sum"
chmod +x "$T/bin/"*
export PATH="$T/bin:$PATH"
cat > "$T/stub-runner.sh" <<'EOF'
#!/bin/bash
R=$(cd "$(dirname "$0")" && pwd)
echo "$$" > "$R/started.pid"
case "$STUB_MODE" in
  normal)
    echo "$$ $(hostname) 777 2026-11-23T10:00:00Z" > "$R/runner.pid.partial" && mv "$R/runner.pid.partial" "$R/runner.pid"
    for _ in $(seq 1 50); do [ -e "$R/handoff.ok" ] && break; sleep 0.1; done
    [ -e "$R/handoff.ok" ] && echo "got handoff: $(cat "$R/handoff.ok")" > "$R/stub.out"
    exit 0 ;;
  silent) (trap '' TERM; exec sleep 40) & echo "$!" > "$R/child.pid"; sleep 40 ;;
  wrongpid) echo "1 $(hostname) 777 2026-11-23T10:00:00Z" > "$R/runner.pid"; sleep 40 ;;
esac
EOF
ORIG=$(cat "$CONNECT")

cut() {  # cut CONNECT_TEXT -> the preamble and step 9, re-rooted, with the stub runner
  python3 -I -c '
import sys
t, root, shm, tmp, py = sys.argv[1:]
lines = t.splitlines(keepends=True)
a = next(i for i, l in enumerate(lines) if l == "umask 077\n")
b = next(i for i, l in enumerate(lines) if l.startswith("trap ") and l.rstrip().endswith(" HUP"))
c = next(i for i, l in enumerate(lines) if l == "echo \"== 9. the runner\"\n")
d = next(i for i, l in enumerate(lines) if i > c and l.rstrip("\n") == "finish 0")
pre, step = "".join(lines[a : b + 1]), "".join(lines[c : d + 1]).rstrip("\n") + "\n"
h0 = step.index("cat > " + root + "/rpd_d2s0_runner.sh <<\x27RUNNER\x27\n")
h1 = step.index("\nRUNNER\n", h0) + len("\nRUNNER\n")
step = step[:h0] + "cp " + tmp + "/stub-runner.sh " + root + "/rpd_d2s0_runner.sh\n" + step[h1:]
assert step.count("seq 1 150") == 1
step = step.replace("seq 1 150", "seq 1 10")
pre = pre.replace("SELF=$1\n", "").replace("made=0\n", "")
assert pre.count("\nPY=") == 1
pre = "\n".join(("PY=" + py) if l.startswith("PY=") else l for l in pre.split("\n"))
out = "SELF=" + tmp + "/self.sh\nmade=1\n" + pre + step
print(out.replace(root, tmp + "/r").replace(shm, tmp + "/shm"), end="")' "$1" "$ROOT" "$SHM" "$T" "$(command -v python3)"
}

prepare() { pkill -KILL -f "$T/r/" 2>/dev/null; rm -rf -- "$T/r" "$T/shm"; mkdir -p "$T/r" "$T/shm/repo"; : > "$T/self.sh"; }

run() {  # run CONNECT_TEXT MODE [signal]: the connect's output, its rc, the runner's fate, /dev/shm
  cut "$1" > "$T/connect.sh"
  local out r spid
  if [ "${3:-}" = term ]; then
    STUB_MODE=$2 bash "$T/connect.sh" > "$T/out" 2>&1 &
    local cpid=$!
    for _ in $(seq 1 30); do [ -s "$T/r/started.pid" ] && break; sleep 0.1; done
    sleep 0.5; kill -TERM "$cpid"; wait "$cpid"; r=$?
  else
    STUB_MODE=$2 bash "$T/connect.sh" > "$T/out" 2>&1; r=$?
  fi
  cat "$T/out"; echo "rc=$r"
  sleep 0.3
  if [ "$2" = normal ]; then for _ in $(seq 1 30); do [ -e "$T/r/stub.out" ] && break; sleep 0.1; done; fi
  spid=$(cat "$T/r/started.pid" 2>/dev/null)
  if [ -n "$spid" ] && kill -0 "$spid" 2>/dev/null && ! ps -o stat= -p "$spid" | grep -q Z; then echo "runner: alive"; else echo "runner: gone"; fi
  cpid=$(cat "$T/r/child.pid" 2>/dev/null)
  if [ -n "$cpid" ]; then kill -0 "$cpid" 2>/dev/null && echo "child: alive" || echo "child: gone"; fi
  [ -e "$T/shm" ] && echo "shm: present" || echo "shm: removed"
  [ -e "$T/r/handoff.ok" ] && echo "handoff.ok: present" || echo "handoff.ok: absent"
  cat "$T/r/stub.out" 2>/dev/null
  pkill -KILL -f "$T/r/" 2>/dev/null
}

check() {  # check NAME OUTPUT LINE...
  local name=$1 out=$2 ok=1
  shift 2
  for want in "$@"; do printf '%s\n' "$out" | grep -qF -- "$want" || ok=0; done
  if [ "$ok" = 1 ]; then [ "$Q" = 1 ] || echo "ok   $name"; else
    [ "$Q" = 1 ] || { echo "FAIL $name: want [$*]"; printf '%s\n' "$out" | sed 's/^/     /'; }
    fails=$((fails + 1))
  fi
}

cases() {  # cases CONNECT_TEXT
  prepare
  check "normal: pid checked, handoff.ok written, the runner owns /dev/shm, rc 0" "$(run "$1" normal)" "rc=0" \
    "handed over" "handoff.ok: present" "got handoff: " "shm: present"
  prepare
  check "a delayed startup (no pid in time): the runner's group is stopped, /dev/shm removed, rc 8" "$(run "$1" silent)" \
    "STOP: the runner wrote no pid" "stopped the runner" "rc=8" "runner: gone" "child: gone" "shm: removed" \
    "handoff.ok: absent"
  prepare
  check "runner.pid names another process: stopped, /dev/shm removed, rc 8" "$(run "$1" wrongpid)" \
    "STOP: runner.pid names 1, not the started process" "rc=8" "runner: gone" "shm: removed" "handoff.ok: absent"
  prepare
  check "SIGTERM to the connect while it waits: the runner is stopped, /dev/shm removed, rc 8" "$(run "$1" silent term)" \
    "STOP: the connect got SIGTERM" "stopped the runner" "rc=8" "runner: gone" "child: gone" "shm: removed"
}

fails=0; Q=0
cases "$ORIG"
echo "CONNECT-START-TESTS :: $([ "$fails" -eq 0 ] && echo PASS || echo "FAIL ($fails)")"
[ "$fails" -eq 0 ] || exit 1

TAB=$(printf '\t')
MUTANTS="runner-not-stopped${TAB}if [ -n \"\$p\" ] && [ \"\$started\" -eq 0 ]; then${TAB}if false; then
pid-mismatch-allowed${TAB}[ \"\$rpid\" = \"\$spid\" ] ||${TAB}true ||
term-untrapped${TAB}trap 'echo \"STOP: the connect got SIGTERM\"; finish 8' TERM${TAB}:
no-handoff${TAB}echo \"\$rpid \$(date -u +%FT%TZ)\" > ${ROOT}/handoff.ok.partial && mv -- ${ROOT}/handoff.ok.partial ${ROOT}/handoff.ok ||${TAB}true ||
shm-kept${TAB}if [ \"\$made\" -eq 1 ] && [ \"\$started\" -eq 0 ]; then${TAB}if false; then
process-only-kill${TAB}kill -KILL -- -\"\$p\" 2>/dev/null; kill -KILL \"\$p\" 2>/dev/null${TAB}kill -KILL \"\$p\" 2>/dev/null"
Q=1; killed=0; total=0
while IFS="$TAB" read -r name old new; do
  [ -n "$name" ] || continue
  total=$((total + 1))
  n=$(python3 -I -c 'import sys; print(sys.argv[1].count(sys.argv[2]))' "$ORIG" "$old")
  [ "$n" = 1 ] || { echo "MUTANT $name: old text occurs $n times"; continue; }
  M=$(python3 -I -c 'import sys; t, a, b = sys.argv[1:]; print(t.replace(a, b, 1), end="")' "$ORIG" "$old" "$new")
  fails=0; cases "$M"
  if [ "$fails" -gt 0 ]; then killed=$((killed + 1)); echo "KILLED   $name ($fails cases)"; else echo "SURVIVED $name"; fi
done <<< "$MUTANTS"
echo "CONNECT-START-MUTANTS :: $killed/$total killed"
[ "$killed" -eq "$total" ]
