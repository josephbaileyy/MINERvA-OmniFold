#!/bin/bash
# RPD-RECO d2-predict and step0 (rpd_d2s0, generated from P0's fetch), the fetch: reads what the detached runner left under the literal root /pscratch/sd/j/josephrb/rpd-reco-d2s0-20261124, on a login
# node. It writes nothing on the cluster beyond its own /dev/shm copy, which it deletes.
#   - a well-formed chain.rc (no NUL byte, one line "rc=N cause=C end=T", C of [A-Za-z0-9_.-], T a real UTC time) is
#     authoritative,
#     from any login node, with or without runner.pid: DONE if rc 0, otherwise STOP. A malformed chain.rc: exit 9,
#     nothing sent;
#   - no chain.rc, on the runner's node: RUNNING (exit 10, run it again later) only if /proc/<pid> shows the start time
#     recorded in runner.pid and /proc/<pid>/cmdline is byte for byte "bash\0/pscratch/sd/j/josephrb/rpd-reco-d2s0-20261124/rpd_d2s0_runner.sh\0", and chain.rc
#     is still absent after the probe. Otherwise chain.rc is read again (the runner may have finished in between) and, if
#     still absent, the runner is gone without chain.rc (an uncatchable kill): exit 11, with the cleanup of /dev/shm/limres-rpd-flux1 reported
#     as unverified;
#   - no chain.rc and no runner.pid, or no chain.rc on another node: exit 9 (cannot tell).
# When DONE, STOP or gone, it prints the records and sends a base64 tar of them: runner.pid, runner.out,
# runner-steps.txt, chain.rc, handoff.ok, stat-d2s0.txt, inputs-check.txt, fence-overlap.txt, rpd_d2s0_runner.sh,
# production-config.ready.json, sup-*.json and every *.json directly in dry/ and run/ (the step records and any
# refusal record). The staged copies stay. Exits 0 (DONE), 12 (STOP), 11 (gone), 10 (running), 9 (cannot tell), 14 (the
# tar failed). umask 077. Launched from a /dev/shm copy of itself ($1), which it deletes.
umask 077
SELF=$1
R=/pscratch/sd/j/josephrb/rpd-reco-d2s0-20261124
finish() { echo "== rpd-d2s0-fetch rc=$1 $(date -u +%FT%TZ)"; rm -f -- "$SELF"; exit "$1"; }
[ -d "$R" ] || { echo "STOP: $R does not exist"; rm -f -- "$SELF"; exit 9; }
cd "$R" || finish 9
echo "node $(hostname) $(date -u +%FT%TZ); fetch script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
terminal() {  # sets state from a well-formed chain.rc; returns 1 if there is no chain.rc
  [ -f chain.rc ] || return 1
  LC_ALL=C tr -d '\000' < chain.rc | cmp -s - chain.rc || { echo "CANNOT TELL: chain.rc contains NUL bytes"; finish 9; }
  local line lines code end
  lines=$(wc -l < chain.rc | tr -d ' ')
  line=$(cat chain.rc)
  echo "chain.rc: $line"
  [ "$lines" = 1 ] && [[ $line =~ ^rc=([0-9]+)\ cause=[A-Za-z0-9_.-]+\ end=([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z)$ ]] || { echo "CANNOT TELL: chain.rc is malformed"; finish 9; }
  code=${BASH_REMATCH[1]}
  end=${BASH_REMATCH[2]}
  [ "$(date -u -d "$end" +%Y-%m-%dT%H:%M:%SZ 2>/dev/null)" = "$end" ] || { echo "CANNOT TELL: chain.rc's end time $end is not a real UTC time"; finish 9; }
  [ "$code" = 0 ] && state=DONE || state=STOP
  return 0
}
rpid=
if [ -s runner.pid ]; then
  read -r rpid rhost rticks rstart < runner.pid
  echo "runner pid $rpid host $rhost start ticks $rticks start $rstart"
else
  echo "no runner.pid"
fi
if ! terminal; then
  [ -n "$rpid" ] || { echo "CANNOT TELL: no chain.rc and no runner.pid (the connect did not start the runner)"; finish 9; }
  [ "$(hostname)" = "$rhost" ] || { echo "CANNOT TELL: no chain.rc, and the runner ran on $rhost; fetch from $rhost"; finish 9; }
  alive=0
  if st=$(cat "/proc/$rpid/stat" 2>/dev/null); then
    set -f; fields=(${st##*) }); set +f  # no here-string: it could spool to a temp file outside the root
    [ "${fields[19]}" = "$rticks" ] && cmp -s "/proc/$rpid/cmdline" <(printf 'bash\0%s\0' "$R/rpd_d2s0_runner.sh") && alive=1
  fi
  if [ "$alive" -eq 1 ] && [ ! -f chain.rc ]; then
    echo "RUNNING: runner $rpid is alive (start ticks $rticks, bash $R/rpd_d2s0_runner.sh)"
    [ -f runner-steps.txt ] && sed 's/^/step: /' runner-steps.txt
    finish 10
  fi
  if ! terminal; then
    echo "STOP: the runner $rpid is gone and wrote no chain.rc (an uncatchable kill); the cleanup is unverified"
    [ -e /dev/shm/limres-rpd-flux1 ] && echo "/dev/shm/limres-rpd-flux1 still exists on $(hostname)"
    state=GONE
  fi
fi
echo "== state $state"
echo "== the root (mode, bytes, path), staged copies by count only"
find . -path ./dry/staged -prune -o -path ./run/staged -prune -o -path ./clone -prune -o -printf '%M %s %P\n' | sort -k3
for d in dry/staged run/staged; do [ -d "$d" ] && echo "$d: $(find "$d" -type f | wc -l | tr -d ' ') files"; done
send=()
for f in runner.pid runner.out runner-steps.txt chain.rc handoff.ok stat-d2s0.txt inputs-check.txt fence-overlap.txt rpd_d2s0_runner.sh production-config.ready.json sup-*.json dry/*.json run/*.json; do
  [ -f "$f" ] && send+=("$f")
done
total=0
for f in "${send[@]}"; do total=$(( total + $(stat -c %s "$f") )); done
echo "send files ${#send[@]}, bytes $total"
[ "$total" -le 67108864 ] || { echo "STOP: the send list exceeds 64 MiB"; finish 9; }
for f in runner-steps.txt chain.rc; do [ -f "$f" ] && { echo "== $f"; cat "$f"; }; done
for f in "${send[@]}"; do echo "sha256 $(sha256sum "$f" | cut -d' ' -f1) $f"; done
echo "== TAR BEGIN"
tar -cf - "${send[@]}" | base64 -w 76
ps=("${PIPESTATUS[@]}"); trc=${ps[0]}; brc=${ps[1]}
echo "== TAR END tar rc=$trc base64 rc=$brc"
[ "$trc" -eq 0 ] && [ "$brc" -eq 0 ] || { echo "TAR FAILED: tar rc=$trc, base64 rc=$brc; the record stream is incomplete"; finish 14; }
case $state in DONE) finish 0 ;; STOP) finish 12 ;; *) finish 11 ;; esac
