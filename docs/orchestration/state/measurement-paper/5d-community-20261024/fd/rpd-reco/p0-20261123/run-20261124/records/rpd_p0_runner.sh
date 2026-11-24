#!/bin/bash
# rpd_p0 runner, written by rpd_p0_connect.sh and started detached on the login node (setsid, nohup, nice 19). After
# the connect's handoff (handoff.ok, within 60 s, or it cleans up and stops), it runs pins --dry-run and p0 --dry-run
# into /pscratch/sd/j/josephrb/rpd-reco-p0-20261123/dry, then pins and p0 into /pscratch/sd/j/josephrb/rpd-reco-p0-20261123/run, with the config's expected interpreter and threads 1.
# Each step runs under tools/p0_supervise.py: the worker in its own session and group, the supervisor outside it, and
# one monotonic deadline, 7200 s after the handoff, for the whole chain (TERM to the group 30 s before it, KILL at
# it), checked again before each step and after the last. The supervisor's record (sup-<step>.json) gives the worker's
# rc, the ending signal, whether a deadline signal was delivered or the worker outlived the deadline, whether a group
# member was left over and whether the group is gone, and the peak RSS. A STOP follows a deadline (rc 7), an outside
# kill, a nonzero rc, a leftover, a surviving group, an unreadable RSS or one over 8000000000 B (rc 4), before the next
# step starts. If the supervisor leaves no record (killed itself), the step's group, from sup-<step>.json.pgid, is
# killed and awaited before cleanup. A TERM or INT to the runner is forwarded as TERM to the supervisor (or, in the
# instant before its pid is recorded, to $!), which forwards it to the step's group and reaps it.
# On every exit it can catch, it kills a live step group and waits for it; it removes /dev/shm/limres-rpd-flux1 and checks that it is gone
# (rc 6 if a clean run cannot remove it), unless the group survived, when it keeps /dev/shm/limres-rpd-flux1; and it publishes p0.rc (rc,
# cause and a checked UTC time), last; a failed publication is reported (rc 6 if clean). HUP is ignored. An uncatchable kill writes no p0.rc; the fetch then reports the
# runner gone and the /dev/shm cleanup unverified. runner.pid holds the pid, host, /proc start time and UTC time.
umask 077
R=/pscratch/sd/j/josephrb/rpd-reco-p0-20261123
PY=/global/homes/j/josephrb/.conda/envs/omnifold_py310/bin/python3
REPO=/dev/shm/limres-rpd-flux1/repo
CFG=/dev/shm/limres-rpd-flux1/production-config.ready.json
CFG_SHA=3b2afde495d630cc44df730e3e1acf12e0c332953e9fa298fa979f2e2e39b057
SUP=/pscratch/sd/j/josephrb/rpd-reco-p0-20261123/tools/p0_supervise.py
WALL=7200
RSS_CAP=8000000000
for k in OMP_NUM_THREADS OPENBLAS_NUM_THREADS MKL_NUM_THREADS NUMEXPR_NUM_THREADS VECLIB_MAXIMUM_THREADS; do export "$k=1"; done
cause=exit
finished=0
sup=
launching=0
cur=
group_alive() {  # group_alive PGID: true if the group has a member. ESRCH: none. EPERM: a member that cannot be
  # signalled, so alive, except on macOS (Darwin), where EPERM is a zombie-only group (the supervisor's rule). Any
  # other error counts as alive everywhere, so /dev/shm is kept unless the group is confirmed absent.
  local err
  err=$(LC_ALL=C kill -0 -- -"$1" 2>&1) && return 0
  case $err in
    *"No such process"*) return 1 ;;
    *"Operation not permitted"*) [ "$(uname -s)" = Darwin ] && return 1 ;;
  esac
  return 0
}
fin() {
  [ "$finished" -eq 1 ] && exit "$1"
  finished=1
  trap '' TERM INT
  local rc=$1 pg survived=0 when
  if [ -n "$cur" ] && pg=$(cat "$cur" 2>/dev/null) && [[ $pg =~ ^[1-9][0-9]+$ ]]; then  # never 0 or 1 (own group, all)
    kill -KILL -- -"$pg" 2>/dev/null && echo "killed the step's group $pg"
    for _ in $(seq 1 50); do group_alive "$pg" || break; sleep 0.2; done
    if group_alive "$pg"; then
      survived=1
      echo "STOP: the step's group $pg survived; /dev/shm/limres-rpd-flux1 is kept, since a live member may still use it"
      [ "$rc" -eq 0 ] && { rc=6; cause=group-survived; }
    fi
  fi
  if [ "$survived" -eq 0 ]; then
    rm -rf -- /dev/shm/limres-rpd-flux1
    if [ -e /dev/shm/limres-rpd-flux1 ]; then
      echo "STOP: /dev/shm/limres-rpd-flux1 could not be removed"
      [ "$rc" -eq 0 ] && { rc=6; cause=cleanup-failed; }
    else
      echo "removed /dev/shm/limres-rpd-flux1"
    fi
  fi
  if ! { when=$(date -u +%FT%TZ) && [[ $when =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$ ]]       && echo "rc=$rc cause=$cause end=$when" > "$R/p0.rc.partial" && mv -- "$R/p0.rc.partial" "$R/p0.rc"; }; then
    echo "STOP: p0.rc could not be published (rc=$rc cause=$cause)"
    [ "$rc" -eq 0 ] && rc=6
  fi
  exit "$rc"
}
on_signal() {  # on_signal NAME RC: forward TERM to the supervisor (it forwards to the step's group and reaps it), stop
  # TERM for both: bash starts the supervisor with SIGINT ignored, so an INT sent before its handler exists is lost,
  # while a TERM then ends it before it has forked a worker. The runner still exits 130 for INT.
  cause=signal-$1
  local p=$sup
  [ -z "$p" ] && [ "$launching" -eq 1 ] && p=$!
  if [ -n "$p" ]; then kill -TERM "$p" 2>/dev/null; wait "$p" 2>/dev/null; fi
  fin "$2"
}
trap '' HUP
trap 'on_signal TERM 143' TERM
trap 'on_signal INT 130' INT
trap 'r=$?; [ "$finished" -eq 1 ] || { cause=exit-trap; fin "$r"; }' EXIT
st=$(cat /proc/$$/stat) || { cause=proc-stat; fin 9; }
set -f; fields=(${st##*) }); set +f  # no here-string: it could spool to a temp file outside the root
echo "$$ $(hostname) ${fields[19]} $(date -u +%FT%TZ)" > "$R/runner.pid.partial" && mv -- "$R/runner.pid.partial" "$R/runner.pid"
echo "== rpd_p0 runner $$ on $(hostname) $(date -u +%FT%TZ), nice $(nice)"
[ "$(nice)" = 19 ] || { echo "STOP: the runner is not at nice 19"; cause=nice; fin 9; }
for _ in $(seq 1 300); do [ -e "$R/handoff.ok" ] && break; sleep 0.2; done
[ -e "$R/handoff.ok" ] || { echo "STOP: no handoff.ok from the connect within 60 s"; cause=no-handoff; fin 8; }
echo "handoff.ok: $(cat "$R/handoff.ok")"
DEADLINE=$("$PY" -I -B -c "import time; print(repr(time.monotonic() + $WALL))") || { cause=deadline; fin 9; }
echo "deadline (monotonic) $DEADLINE, $WALL s from now"
past_deadline() {  # rc 0 if the deadline has passed, 1 if not; a failed probe is its own STOP (rc 4), not a wall cap
  # The probe answers 10 (passed) or 11 (not passed), so a Python failure (rc 1 or 2) cannot pass for either.
  "$PY" -I -B -c "import sys, time; sys.exit(10 if time.monotonic() >= $DEADLINE else 11)"
  case $? in
    10) return 0 ;;
    11) return 1 ;;
    *) echo "STOP: the deadline check failed"; cause=clock-check; fin 4 ;;
  esac
}
step() {  # step LABEL RUNDIR [--dry-run]: LABEL is pins, p0, pins-dry or p0-dry
  local label=$1 dir=$2
  shift 2
  past_deadline && { echo "STOP: the wall cap was reached before $label"; cause=wall-cap; fin 7; }
  echo "== $label start $(date -u +%FT%TZ)"
  cur="$R/sup-$label.json.pgid"
  launching=1
  ( cd "$REPO" && exec "$PY" -I -B "$SUP" "$DEADLINE" "$R/sup-$label.json" -- \
      "$PY" -B nd-unfolding/fd_rpd_reco.py "${label%%-*}" --config "$CFG" --config-sha256 "$CFG_SHA" --run "$dir" "$@" ) &
  sup=$!
  launching=0
  wait "$sup"
  local src=$?
  sup=
  local v rc sig dl fw rss left gone
  v=$("$PY" -I -B -c 'import json, sys; d = json.load(open(sys.argv[1])); print(d["rc"], d["signal"] or "-", int(d["deadline_signalled"] or d["past_deadline"]), d["forwarded"] or "-", d["peak_rss_bytes"], int(d["leftover_group_killed"]), int(d["group_gone"]))' "$R/sup-$label.json" 2>/dev/null)
  read -r rc sig dl fw rss left gone <<< "$v"
  echo "$label supervisor_rc=$src rc=${rc:-unknown} signal=${sig:-unknown} deadline=${dl:-unknown} leftover_killed=${left:-unknown} group_gone=${gone:-unknown} peak_rss_bytes=${rss:-unknown} end=$(date -u +%FT%TZ)" | tee -a "$R/runner-steps.txt"
  if [ -z "$v" ] && past_deadline; then
    echo "STOP: $label left no supervisor record and the deadline has passed (supervisor rc $src)"; cause=wall-cap; fin 7
  fi
  [ -n "$v" ] || { echo "STOP: $label left no supervisor record (supervisor rc $src); its group is killed before cleanup"; cause=no-record-$label; fin 4; }
  [ "$dl" = 0 ] || { echo "STOP: $label reached the deadline (a deadline signal was delivered, or the worker outlived it)"; cause=wall-cap; fin 7; }
  [ "$gone" = 1 ] || { echo "STOP: $label's group was still alive after the supervisor's KILL"; cause=group-survived-$label; fin 4; }
  [ "$sig" = - ] || { echo "STOP: $label was ended by $sig from outside the supervisor"; cause=killed-$label; fin 4; }
  [ "$rc" = 0 ] || { echo "STOP: $label rc=$rc"; cause=step-$label; fin 4; }
  [ "$left" = 0 ] || { echo "STOP: $label left processes in its group (killed)"; cause=leftover-$label; fin 4; }
  [[ "$rss" =~ ^[0-9]+$ ]] || { echo "STOP: $label peak RSS unreadable"; cause=rss-unread; fin 4; }
  [ "$rss" -le "$RSS_CAP" ] || { echo "STOP: $label peak RSS $rss B exceeds $RSS_CAP B"; cause=rss-cap; fin 4; }
  [ "$src" -eq 0 ] || { echo "STOP: $label supervisor rc=$src"; cause=supervisor-$label; fin 4; }
  cur=
}
mkdir -m 700 "$R/dry" "$R/run" || { cause=mkdir; fin 9; }
step pins-dry "$R/dry" --dry-run
step p0-dry "$R/dry" --dry-run
step pins "$R/run"
step p0 "$R/run"
past_deadline && { echo "STOP: the chain ended at or after the deadline"; cause=wall-cap; fin 7; }
echo "== P0 DONE $(date -u +%FT%TZ)"
fin 0
