#!/bin/bash
# test_runner.sh: the runner the connect writes (rpd_p0_runner.sh), cut from rpd_p0_connect.sh and run locally with the
# real tools/p0_supervise.py and real processes and signals. The bound worker is a stub fd_rpd_reco.py.
# usage: bash test_runner.sh
# The copy is re-rooted into a temp directory: the run root, /dev/shm/limres-rpd-flux1 and the config's interpreter are
# replaced, and the /proc start-time read (Linux) by a fixed stat line. `nice` with no operands prints the niceness, as
# GNU nice does on the login node (a PATH stub; macOS nice does not). Each case starts the runner under nice 19 unless
# it says otherwise. The stub worker reads STUB_<label> (pass, fail, selfkill, spawn, sleep, killsup) and records its
# argv. A fake supervisor (tools/p0_supervise.py replaced in the temp root) writes records with FAKE_REC_<label>'s fields
# and sleeps FAKE_SLOW_<label> seconds after the worker, to reach the runner's own classification and deadline checks.
# The SIGINT case starts the runner with the connect's own launch wrapper (it resets SIGINT, which a background job
# without job control inherits as ignored). Mutants then weaken the runner; each must fail at least one case.
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
CONNECT="$HERE/../rpd_p0_connect.sh"
TOOL="$HERE/../tools/p0_supervise.py"
ROOT=/pscratch/sd/j/josephrb/rpd-reco-p0-20261123
SHM=/dev/shm/limres-rpd-flux1
PYTHON=$(command -v python3)
T=$(mktemp -d) || exit 9
trap 'chmod -R u+w "$T" 2>/dev/null; rm -rf -- "$T"' EXIT
mkdir -p "$T/bin"
cat > "$T/bin/date" <<'EOF'
#!/bin/bash
[ -n "${FAKE_DATE_FAIL:-}" ] && exit 1
exec /bin/date "$@"
EOF
cat > "$T/bin/uname" <<'EOF'
#!/bin/bash
[ -n "${FAKE_LINUX:-}" ] && [ "$1" = -s ] && { echo Linux; exit 0; }
[ -n "${FAKE_DARWIN:-}" ] && [ "$1" = -s ] && { echo Darwin; exit 0; }
exec /usr/bin/uname "$@"
EOF
cat > "$T/bin/nice" <<'EOF'
#!/bin/bash
[ $# -eq 0 ] && exec python3 -I -c 'import os; print(os.getpriority(os.PRIO_PROCESS, 0))'
exec /usr/bin/nice "$@"
EOF
chmod +x "$T/bin/"*
export PATH="$T/bin:$PATH"
PYCFG=$(python3 -I -c 'import json,sys; print(json.load(open(sys.argv[1]))["expected_environment"]["interpreter"])' "$HERE/../production-config.ready.json")
RUNNER=$(awk "/^cat > .*rpd_p0_runner.sh <<'RUNNER'\$/ {f=1; next} /^RUNNER\$/ {f=0} f" "$CONNECT")
[ "$(printf '%s\n' "$RUNNER" | grep -c '^step ')" = 4 ] || { echo "SETUP: could not cut the runner"; exit 9; }
STAT_LINE='st=$(cat /proc/$$/stat) || { cause=proc-stat; fin 9; }'
INTWRAP=$(python3 -I -c '
import re, sys
line = next(l for l in open(sys.argv[1]) if l.startswith("setsid nohup nice -n 19 \"$PY\" -I -B -c "))
print(re.search(r"-c \x27([^\x27]*)\x27 ", line).group(1))' "$CONNECT") || { echo "SETUP: no launch wrapper"; exit 9; }
cat > "$T/fake_sup.py" <<'EOF'
import json, os, subprocess, sys, time
result, cmd = sys.argv[2], sys.argv[4:]
label = os.path.basename(result)[len("sup-") : -len(".json")].replace("-", "_")
if os.environ.get("FAKE_EXIT2_" + label):  # the deadline passed before it could start a worker: exit 2, no record
    time.sleep(float(os.environ["FAKE_EXIT2_" + label]))
    sys.exit(2)
if os.environ.get("FAKE_PGID"):
    open(result + ".pgid", "w").write(os.environ["FAKE_PGID"] + "\n")
rc = subprocess.call(cmd)
if os.environ.get("FAKE_NORECORD"):
    sys.exit(137)
time.sleep(float(os.environ.get("FAKE_SLOW_" + label, "0")))
record = {"rc": rc, "signal": None, "deadline_signalled": False, "past_deadline": False, "forwarded": None,
          "peak_rss_bytes": 1000, "leftover_group_killed": False, "group_gone": True}
record.update(json.loads(os.environ.get("FAKE_REC_" + label, "{}")))
json.dump(record, open(result, "w"))
sys.exit(0 if rc == 0 else 1)
EOF

rewrite() {  # rewrite RUNNER_TEXT -> the runner re-rooted for this machine
  python3 -I -c '
import sys
t, root, shm, pycfg, py, statline, tmp = sys.argv[1:]
for old, new, n in ((root, tmp + "/r", None), (shm, tmp + "/shm", None), ("PY=" + pycfg, "PY=" + py, 1),
                    (statline, "st=\"$$ (bash) S 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 424242 0\"", 1),
                    ("umask 077\n", "umask 077\nkill() { if [ -n \"${FAKE_ALIVE_PG:-}\" ] && [ \"$*\" = \"-0 -- -$FAKE_ALIVE_PG\" ]; then return 0; fi; if [ -n \"${FAKE_EPERM_PG:-}\" ] && [ \"$*\" = \"-0 -- -$FAKE_EPERM_PG\" ]; then echo \"bash: kill: (-$FAKE_EPERM_PG) - Operation not permitted\" >&2; return 1; fi; if [ -n \"${FAKE_ODD_PG:-}\" ] && [ \"$*\" = \"-0 -- -$FAKE_ODD_PG\" ]; then echo \"bash: kill: (-$FAKE_ODD_PG) - Some unexpected error\" >&2; return 1; fi; builtin kill \"$@\"; }\n", 1)):
    k = t.count(old)
    assert k >= 1 and (n is None or k == n), (old, k)
    t = t.replace(old, new)
print(t, end="")' "$1" "$ROOT" "$SHM" "$PYCFG" "$PYTHON" "$STAT_LINE" "$T"
}

prepare() {  # prepare: a fresh root with the tool and handoff.ok, and a /dev/shm stand-in with the stub worker
  chmod -R u+w "$T/r" "$T/shm" 2>/dev/null; rm -rf -- "$T/r" "$T/shm"
  mkdir -p "$T/r/tools" "$T/shm/repo/nd-unfolding"
  cp "$TOOL" "$T/r/tools/p0_supervise.py"
  echo "4242 handed over" > "$T/r/handoff.ok"
  cat > "$T/shm/repo/nd-unfolding/fd_rpd_reco.py" <<'EOF'
import os, subprocess, sys, time
step, run = sys.argv[1], sys.argv[sys.argv.index("--run") + 1]
label = step + ("-dry" if "--dry-run" in sys.argv else "")
with open(os.environ["STUB_LOG"], "a") as log:
    log.write(f"{label} {os.getpid()} nice={os.getpriority(os.PRIO_PROCESS, 0)} {' '.join(sys.argv[1:])}\n")
mode = os.environ.get("STUB_" + label.replace("-", "_"), "pass")
if mode == "fail":
    sys.exit(4)
if mode == "selfkill":
    os.kill(os.getpid(), 9)
if mode == "spawn":
    subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
if mode == "sleep":
    open(os.environ["STUB_LOG"] + ".pid", "w").write(str(os.getpid()))
    time.sleep(float(os.environ.get("STUB_SLEEP", "8")))
if mode == "killsup":  # SIGKILL the supervisor (this worker's parent), then outlive it
    open(os.environ["STUB_LOG"] + ".pid", "w").write(str(os.getpid()))
    os.kill(os.getppid(), 9)
    time.sleep(20)
with open(os.path.join(run, label + ".json"), "w") as out:
    out.write('{"status": "PASS"}\n')
EOF
  : > "$T/log"
}

start() {  # start RUNNER_TEXT [plain]: run it (under nice 19 unless plain) in the background; sets RPID
  rewrite "$1" > "$T/r/rpd_p0_runner.sh"
  if [ "${2:-}" = plain ]; then
    STUB_LOG="$T/log" bash "$T/r/rpd_p0_runner.sh" > "$T/r/runner.out" 2>&1 &
  elif [ "${2:-}" = wrapped ]; then
    STUB_LOG="$T/log" /usr/bin/nice -n 19 python3 -I -B -c "$INTWRAP" "$T/r/rpd_p0_runner.sh" > "$T/r/runner.out" 2>&1 &
  else
    STUB_LOG="$T/log" /usr/bin/nice -n 19 bash "$T/r/rpd_p0_runner.sh" > "$T/r/runner.out" 2>&1 &
  fi
  RPID=$!
}

result() {  # result -> the facts a case checks
  wait "$RPID" 2>/dev/null; echo "exit=$?"
  echo "p0.rc: $(cat "$T/r/p0.rc" 2>/dev/null || echo absent)"
  [ -e "$T/shm" ] && echo "shm: present" || echo "shm: removed"
  echo "ran: [$(cut -d' ' -f1 "$T/log" | paste -sd' ' -)]"
  echo "steps: [$(cut -d' ' -f1 "$T/r/runner-steps.txt" 2>/dev/null | paste -sd' ' -)]"
  [ -e "$T/r/dry/pins-dry.json" ] && echo "pins-dry: completed" || echo "pins-dry: not completed"
  [ -e "$T/r/run/pins.json" ] && echo "pins: completed" || echo "pins: not completed"
  [ -s "$T/r/runner.pid" ] && echo "pidfile: $(cut -d' ' -f1,3 "$T/r/runner.pid")"
  grep -o 'nice=[0-9]*' "$T/log" | sort -u | tr '\n' ' '; echo
  grep '^STOP' "$T/r/runner.out"
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

cases() {  # cases RUNNER_TEXT
  local R0=$1 out
  prepare; start "$R0"; result > "$T/out.txt"; out=$(cat "$T/out.txt")
  check "all pass: dry then real, in order, at nice 19, rc 0, /dev/shm removed" "$out" "exit=0" "p0.rc: rc=0 cause=exit" \
    "shm: removed" "ran: [pins-dry p0-dry pins p0]" "steps: [pins-dry p0-dry pins p0]" "pidfile: $RPID 424242" "nice=19 "
  for label in pins-dry p0-dry pins p0; do
    prepare; eval "export STUB_${label//-/_}=fail"; start "$R0"; result > "$T/out.txt"; out=$(cat "$T/out.txt"); unset "STUB_${label//-/_}"
    check "$label fails: STOP rc 4 before the next step, /dev/shm removed" "$out" "exit=4" "cause=step-$label" "shm: removed" \
      "steps: [$(printf '%s\n' pins-dry p0-dry pins p0 | sed "/^$label\$/q" | paste -sd' ' -)]"
  done
  prepare; export STUB_p0_dry=selfkill; start "$R0"; result > "$T/out.txt"; out=$(cat "$T/out.txt"); unset STUB_p0_dry
  check "p0-dry killed by SIGKILL from outside the supervisor: killed-p0-dry, rc 4" "$out" "exit=4" "cause=killed-p0-dry" "shm: removed"
  prepare; export STUB_pins=spawn; start "$R0"; result > "$T/out.txt"; out=$(cat "$T/out.txt"); unset STUB_pins
  check "pins leaves a process in its group: killed, leftover-pins, rc 4" "$out" "exit=4" "cause=leftover-pins" "steps: [pins-dry p0-dry pins]"
  prepare; start "$(printf '%s' "$R0" | sed 's/^RSS_CAP=8000000000$/RSS_CAP=1000/')"; result > "$T/out.txt"; out=$(cat "$T/out.txt")
  check "peak RSS over the cap (a 1000 B cap): rss-cap, rc 4, after the first step" "$out" "exit=4" "cause=rss-cap" "steps: [pins-dry]"
  prepare; start "$(printf '%s' "$R0" | sed 's/^WALL=7200$/WALL=3/')"; result > "$T/out.txt"; out=$(cat "$T/out.txt")
  check "the wall cap (3 s, the supervisor's TERM lead 30 s): wall-cap, rc 7, no step finished" "$out" "exit=7" "cause=wall-cap" "shm: removed"
  prepare; rm -f "$T/r/handoff.ok"; start "$(printf '%s' "$R0" | sed 's/seq 1 300/seq 1 5/')"; result > "$T/out.txt"; out=$(cat "$T/out.txt")
  check "no handoff.ok from the connect: no-handoff, rc 8, no step run, /dev/shm removed" "$out" "exit=8" "cause=no-handoff" "ran: []" "shm: removed"
  prepare; start "$R0" plain; result > "$T/out.txt"; out=$(cat "$T/out.txt")
  check "not at nice 19: STOP rc 9, no step run" "$out" "exit=9" "cause=nice" "ran: []"
  prepare; export STUB_pins_dry=sleep STUB_SLEEP=8; start "$R0"
  for _ in $(seq 1 50); do [ -s "$T/log.pid" ] && break; sleep 0.1; done
  kill -TERM "$RPID" 2>/dev/null; result > "$T/out.txt"; out=$(cat "$T/out.txt"); unset STUB_pins_dry STUB_SLEEP
  local wpid; wpid=$(cat "$T/log.pid" 2>/dev/null); rm -f "$T/log.pid"
  kill -0 "$wpid" 2>/dev/null && out="$out
worker: alive" || out="$out
worker: gone"
  check "TERM to the runner mid-step: forwarded to the step's group, rc 143, worker gone, /dev/shm removed" "$out" "exit=143" \
    "cause=signal-TERM" "worker: gone" "pins-dry: not completed" "shm: removed"
  prepare; export STUB_pins=sleep STUB_SLEEP=8; start "$R0" wrapped
  for _ in $(seq 1 80); do [ -s "$T/log.pid" ] && grep -q '^pins ' "$T/log" && break; sleep 0.1; done
  kill -INT "$RPID" 2>/dev/null; result > "$T/out.txt"; out=$(cat "$T/out.txt"); unset STUB_pins STUB_SLEEP
  wpid=$(cat "$T/log.pid" 2>/dev/null); rm -f "$T/log.pid"
  kill -0 "$wpid" 2>/dev/null && out="$out
worker: alive" || out="$out
worker: gone"
  check "SIGINT to a runner started by the connect's wrapper: trapped and forwarded, rc 130, worker gone" "$out" \
    "exit=130" "cause=signal-INT" "worker: gone" "pins: not completed" "shm: removed"
  prepare; export STUB_pins_dry=killsup; start "$R0"; result > "$T/out.txt"; out=$(cat "$T/out.txt"); unset STUB_pins_dry
  wpid=$(cat "$T/log.pid" 2>/dev/null); rm -f "$T/log.pid"
  kill -0 "$wpid" 2>/dev/null && out="$out
worker: alive" || out="$out
worker: gone"
  check "the supervisor killed mid-step: no record, the step's group killed from its pgid file, rc 4" "$out" "exit=4" \
    "cause=no-record-pins-dry" "worker: gone" "shm: removed"
  prepare; cp "$T/fake_sup.py" "$T/r/tools/p0_supervise.py"; export FAKE_REC_pins_dry='{"past_deadline": true}'
  start "$R0"; result > "$T/out.txt"; out=$(cat "$T/out.txt"); unset FAKE_REC_pins_dry
  check "a record with past_deadline (no deadline signal): wall-cap, rc 7" "$out" "exit=7" "cause=wall-cap" "steps: [pins-dry]"
  prepare; cp "$T/fake_sup.py" "$T/r/tools/p0_supervise.py"; export FAKE_REC_p0_dry='{"group_gone": false}'
  start "$R0"; result > "$T/out.txt"; out=$(cat "$T/out.txt"); unset FAKE_REC_p0_dry
  check "a record whose group survived: group-survived-p0-dry, rc 4" "$out" "exit=4" "cause=group-survived-p0-dry"
  prepare; cp "$T/fake_sup.py" "$T/r/tools/p0_supervise.py"; export FAKE_SLOW_p0=7
  start "$(printf '%s' "$R0" | sed 's/^WALL=7200$/WALL=6/')"; result > "$T/out.txt"; out=$(cat "$T/out.txt"); unset FAKE_SLOW_p0
  check "the last step ends after the deadline (a 6 s chain, a 7 s last step): the final check STOPs, wall-cap, rc 7" "$out" "exit=7" \
    "cause=wall-cap" "steps: [pins-dry p0-dry pins p0]" "the chain ended at or after the deadline"
  prepare; cp "$T/fake_sup.py" "$T/r/tools/p0_supervise.py"; export FAKE_PGID=99999 FAKE_NORECORD=1 FAKE_ALIVE_PG=99999
  start "$R0"; result > "$T/out.txt"; out=$(cat "$T/out.txt"); unset FAKE_PGID FAKE_NORECORD FAKE_ALIVE_PG
  check "no record and the step's group still alive after KILL (a forced kill -0): /dev/shm kept, rc 4" "$out" "exit=4" \
    "cause=no-record-pins-dry" "is kept, since a live member" "shm: present"
  prepare; cp "$T/fake_sup.py" "$T/r/tools/p0_supervise.py"; export FAKE_PGID=99999 FAKE_NORECORD=1 FAKE_EPERM_PG=99999 FAKE_LINUX=1
  start "$R0"; result > "$T/out.txt"; out=$(cat "$T/out.txt"); unset FAKE_PGID FAKE_NORECORD FAKE_EPERM_PG FAKE_LINUX
  check "no record and kill -0 answering EPERM on Linux (a member it cannot signal): /dev/shm kept, rc 4" "$out" "exit=4" \
    "cause=no-record-pins-dry" "is kept, since a live member" "shm: present"
  prepare; cp "$T/fake_sup.py" "$T/r/tools/p0_supervise.py"; export FAKE_PGID=99999 FAKE_NORECORD=1 FAKE_ODD_PG=99999 FAKE_DARWIN=1
  start "$R0"; result > "$T/out.txt"; out=$(cat "$T/out.txt"); unset FAKE_PGID FAKE_NORECORD FAKE_ODD_PG FAKE_DARWIN
  check "no record and an unexpected kill -0 error on macOS: alive, /dev/shm kept, rc 4" "$out" "exit=4" \
    "is kept, since a live member" "shm: present"
  prepare; cp "$T/fake_sup.py" "$T/r/tools/p0_supervise.py"; export FAKE_EXIT2_pins_dry=3
  start "$(printf '%s' "$R0" | sed 's/^WALL=7200$/WALL=2/')"; result > "$T/out.txt"; out=$(cat "$T/out.txt"); unset FAKE_EXIT2_pins_dry
  check "the supervisor exits 2 without a record after the deadline passed: wall-cap, rc 7" "$out" "exit=7" "cause=wall-cap" \
    "no supervisor record and the deadline has passed"
  prepare; start "$(printf '%s' "$R0" | sed 's/^echo "deadline (monotonic) \$DEADLINE/DEADLINE=bogus; &/')"
  result > "$T/out.txt"; out=$(cat "$T/out.txt")
  check "the deadline probe itself fails (a bogus deadline): its own STOP, clock-check, rc 4, not a wall cap" "$out" \
    "exit=4" "cause=clock-check" "ran: []"
  prepare; export FAKE_DATE_FAIL=1; start "$R0"; result > "$T/out.txt"; out=$(cat "$T/out.txt"); unset FAKE_DATE_FAIL
  check "a clean run whose UTC time cannot be read: p0.rc not published, rc 6" "$out" "exit=6" "p0.rc: absent" \
    "could not be published"
  prepare; mkdir "$T/r/p0.rc.partial"; start "$R0"; result > "$T/out.txt"; out=$(cat "$T/out.txt")
  check "a clean run that cannot publish p0.rc: reported, rc 6" "$out" "exit=6" "p0.rc: absent" "could not be published"
  prepare; mkdir -p "$T/shm/locked/x"; chmod 500 "$T/shm/locked"; start "$R0"; result > "$T/out.txt"; out=$(cat "$T/out.txt"); chmod -R u+w "$T/shm"
  check "a clean run whose /dev/shm cannot be removed: rc 6, cleanup-failed" "$out" "exit=6" "cause=cleanup-failed" "shm: present"
}

fails=0; Q=0
cases "$RUNNER"
echo "RUNNER-TESTS :: $([ "$fails" -eq 0 ] && echo PASS || echo "FAIL ($fails)")"
[ "$fails" -eq 0 ] || exit 1

TAB=$(printf '\t')
MUTANTS="deadline-ignored${TAB}[ \"\$dl\" = 0 ] ||${TAB}true ||
outside-kill-ignored${TAB}[ \"\$sig\" = - ] ||${TAB}true ||
rc-ignored${TAB}[ \"\$rc\" = 0 ] ||${TAB}true ||
leftover-ignored${TAB}[ \"\$left\" = 0 ] ||${TAB}true ||
rss-cap-ignored${TAB}[ \"\$rss\" -le \"\$RSS_CAP\" ] ||${TAB}true ||
cleanup-unchecked${TAB}[ \"\$rc\" -eq 0 ] && { rc=6; cause=cleanup-failed; }${TAB}:
handoff-skipped${TAB}[ -e \"\$R/handoff.ok\" ] || { echo \"STOP: no handoff.ok${TAB}true || { echo \"STOP: no handoff.ok
nice-unchecked${TAB}[ \"\$(nice)\" = 19 ] ||${TAB}true ||
forward-dropped${TAB}kill -TERM \"\$p\" 2>/dev/null;${TAB}:;
eperm-is-gone${TAB}*\"Operation not permitted\"*) [ \"\$(uname -s)\" = Darwin ] && return 1 ;;${TAB}*\"Operation not permitted\"*) return 1 ;;
darwin-any-error${TAB}*\"Operation not permitted\"*) [ \"\$(uname -s)\" = Darwin ] && return 1 ;;${TAB}*) [ \"\$(uname -s)\" = Darwin ] && return 1 ;;
expired-no-record-as-rc4${TAB}if [ -z \"\$v\" ] && past_deadline; then${TAB}if false; then
probe-failure-as-not-passed${TAB}    *) echo \"STOP: the deadline check failed\"; cause=clock-check; fin 4 ;;${TAB}    *) return 1 ;;
survivor-tree-removed${TAB}if [ \"\$survived\" -eq 0 ]; then${TAB}if true; then
time-unchecked${TAB}when=\$(date -u +%FT%TZ) && [[ \$when =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z\$ ]]${TAB}when=\$(date -u +%FT%TZ); true
past-deadline-ignored${TAB}int(d[\"deadline_signalled\"] or d[\"past_deadline\"])${TAB}int(d[\"deadline_signalled\"])
gone-ignored${TAB}[ \"\$gone\" = 1 ] ||${TAB}true ||
final-deadline-dropped${TAB}past_deadline && { echo \"STOP: the chain ended${TAB}false && { echo \"STOP: the chain ended
orphan-group-kept${TAB}kill -KILL -- -\"\$pg\" 2>/dev/null && echo${TAB}: && echo
publish-unchecked${TAB}    [ \"\$rc\" -eq 0 ] && rc=6${TAB}    :
shm-kept${TAB}rm -rf -- /dev/shm/limres-rpd-flux1${TAB}:
dry-skipped${TAB}step pins-dry \"\$R/dry\" --dry-run${TAB}:"
Q=1; killed=0; total=0
while IFS="$TAB" read -r name old new; do
  total=$((total + 1))
  n=$(python3 -I -c 'import sys; print(sys.argv[1].count(sys.argv[2]))' "$RUNNER" "$old")
  [ "$n" = 1 ] || { echo "MUTANT $name: old text occurs $n times"; continue; }
  M=$(python3 -I -c 'import sys; t, a, b = sys.argv[1:]; print(t.replace(a, b, 1), end="")' "$RUNNER" "$old" "$new")
  fails=0; cases "$M"
  if [ "$fails" -gt 0 ]; then killed=$((killed + 1)); echo "KILLED   $name ($fails cases)"; else echo "SURVIVED $name"; fi
done <<< "$MUTANTS"
echo "RUNNER-MUTANTS :: $killed/$total killed"
[ "$killed" -eq "$total" ]
