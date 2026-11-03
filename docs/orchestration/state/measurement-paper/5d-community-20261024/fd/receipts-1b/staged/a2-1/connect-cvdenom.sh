#!/bin/bash
# 1B A2.1, the CV denominator read (S3 (d1), the director's ruling): fd_1b_cvdenom.py on a login node at nice 19,
# 0 node-h, in omnifold_py310 (uproot). It reads mc_truth_denom's six branches from the bank's source omnifile through
# O_NOATIME, checks (A)-(D), and writes the bank rows' CV weight only on PASS. A fresh clone at M in a new pscratch
# directory; writes only under $W. No draw is read and nothing of C2's reading is computed.
# The director's limits: stopped at 45 min wall or 12 GB RSS (a watcher on /proc), reported, not retried.
# Run detached: setsid nohup bash connect-cvdenom.sh >/dev/null 2>&1 </dev/null &
set -o pipefail
M=435d8957f49fb8aad4a956eadc44e4a3f0b25d13
P=/pscratch/sd/j/josephrb; W=$P/fd-1b-a21-cvdenom-20261103; DD=$W/deploy
PY=/global/homes/j/josephrb/.conda/envs/omnifold_py310/bin/python
ND=$P/MINERvA-OmniFold/nd-unfolding
stop() { echo "STOP $*"; echo "end=$(date -u +%FT%TZ)"; exit 2; }
[ -e "$W" ] && { echo "STOP $W exists"; exit 2; }
mkdir "$W" || exit 2
exec >> "$W/connect-cvdenom.log" 2>&1
echo "host=$(hostname) start=$(date -u +%FT%TZ) pid=$$ ppid=$PPID"
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold "$DD" && git -C "$DD" checkout --quiet --detach "$M" || stop clone
n=$(git -C "$DD" status --porcelain | wc -l); h=$(git -C "$DD" rev-parse HEAD); echo "deploy porcelain_lines=$n head=$h"
[ "$n" = "0" ] && [ "$h" = "$M" ] || stop "deploy not clean at M"
echo "ef4c45730504dafc6f9934ab4cc07847adaae2d0a65a492172b6d7ce9e5378f7  nd-unfolding/fd_1b_cvdenom.py" > "$W/bound.sha256"
(cd "$DD" && sha256sum -c "$W/bound.sha256") || stop "bound blob differs"
"$PY" -c "import numpy, uproot; print('numpy', numpy.__version__, 'uproot', uproot.__version__)" || stop env
cd "$W" || stop cd
/usr/bin/time -v nice -n 19 "$PY" -B "$DD/nd-unfolding/fd_1b_cvdenom.py" \
  --root "$ND/runEventLoopOmniFold_5D_MEFHC_universes_full_bkgaware.root" \
  --npz "$ND/of_inputs_5d.npz" --expect-npz-sha256 07fccc1abc7204bc29349b4ba96850986fe91e909e83fc54e8d1a6b3922a649f \
  --bank "$ND/bank_sweep_5d_bkgaware" --detector-dir "$P/s5p-20260926/bank_detector" \
  --pins "$P/fd-1b-20261030/pins.json" --expect-pins-sha256 5adcd576eb46f443fe4133b05044cd315c0eeb0f281e21acee5f2318b4bab248 \
  --out "$W/cvdenom.json" > "$W/cvdenom.out" 2> "$W/cvdenom.time" &
TP=$!
LIMIT_S=2700; LIMIT_KB=12000000; t0=$(date +%s); why=""
while kill -0 "$TP" 2>/dev/null; do
  py=$(pgrep -P "$TP" | head -1)                     # /usr/bin/time's child: nice execs python in place
  kb=$( [ -n "$py" ] && awk '/^VmRSS/ {print $2}' "/proc/$py/status" 2>/dev/null || echo 0 ); kb=${kb:-0}
  el=$(( $(date +%s) - t0 ))
  if [ "$el" -gt "$LIMIT_S" ]; then why="wall ${el}s > ${LIMIT_S}s"; elif [ "$kb" -gt "$LIMIT_KB" ]; then why="rss ${kb}kB > ${LIMIT_KB}kB"; fi
  if [ -n "$why" ]; then echo "LIMIT $why: stopping"; pkill -TERM -P "$TP"; sleep 5; kill -TERM "$TP" 2>/dev/null; break; fi
  sleep 10
done
wait "$TP"; rc=$?
[ -n "$why" ] && echo "STOPPED BY LIMIT: $why"
echo "cvdenom rc=$rc"
cat "$W/cvdenom.out"
grep -E "Elapsed|Maximum resident|File system inputs|Percent of CPU|Exit status" "$W/cvdenom.time"
sha256sum "$W"/cvdenom.json "$W"/cvdenom.out "$W"/cvdenom.time $( [ -e "$W/cvdenom.npy" ] && echo "$W/cvdenom.npy" )
echo "end=$(date -u +%FT%TZ)"
