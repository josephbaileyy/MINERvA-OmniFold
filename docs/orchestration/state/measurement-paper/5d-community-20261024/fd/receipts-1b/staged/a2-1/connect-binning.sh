#!/bin/bash
# 1B A2.1, the director's items 3 and 4 (the binning offsets at the reporting level): fd_1b_binning.py on a login
# node at nice 19, single-threaded numpy, 0 node-h, in the environment the 1B jobs use (setup_salloc_env.sh; not under
# set -u, which aborts the root_6_28 activation). A fresh clone at M in a new pscratch directory; writes only under $W.
# It reads the (e2) CV read's PASS record, the inputs npz, S1's staged assembly, F1's two prep ratios, the declared
# draws' law and the bank universes' tdw at the 16 moved rows by seek. No draw is unfolded and nothing of C2's reading
# is computed. The director's limits: stopped at 45 min wall or 12 GB RSS, reported, not retried. The third run: the
# first (e7641a9b) refused at the float32-U check (a2-1/u-check-grep.txt); the second (663a7609) raised ValueError
# ratio_nd (truth_weight without s5e_deform's install); neither measured anything.
# Run detached: setsid nohup bash connect-binning.sh >/dev/null 2>&1 </dev/null &
set -o pipefail
M=917907aae6f3db5e299330c1ce78edfda72fb67f
P=/pscratch/sd/j/josephrb; W=$P/fd-1b-a21-binning3-20261103; DD=$W/deploy
ND=$P/MINERvA-OmniFold/nd-unfolding
CVD=$P/fd-1b-a21-cvdenom2-20261103/cvdenom.json
CVD_SHA=156b963d9efbe0b54c4602d263b3996fe8a1dbfbef068e4cff17382e54c679be
stop() { echo "STOP $*"; echo "end=$(date -u +%FT%TZ)"; exit 2; }
[ -e "$W" ] && { echo "STOP $W exists"; exit 2; }
mkdir "$W" || exit 2
exec >> "$W/connect-binning.log" 2>&1
echo "host=$(hostname) start=$(date -u +%FT%TZ) pid=$$ ppid=$PPID"
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold "$DD" && git -C "$DD" checkout --quiet --detach "$M" || stop clone
n=$(git -C "$DD" status --porcelain | wc -l); h=$(git -C "$DD" rev-parse HEAD); echo "deploy porcelain_lines=$n head=$h"
[ "$n" = "0" ] && [ "$h" = "$M" ] || stop "deploy not clean at M"
cat > "$W/bound.sha256" <<SUMS
69cd7bd37984db1deb0d103fb81808e88fc990cc679e9a4b0a6dea16d15b208d  nd-unfolding/fd_1b_binning.py
f7d196bdcbc4365187353624978a3284087dc12501c27ea07b9f4f6169b18f1c  nd-unfolding/fd_1b_c2.py
05150fb49c446ccaac70eebee22edc6214bfc9af1ebdb1a7dc72bedde0092a8b  nd-unfolding/fd_1b_mc.py
SUMS
(cd "$DD" && sha256sum -c "$W/bound.sha256") || stop "bound blobs differ"
echo "sourcing $DD/setup_salloc_env.sh sha256 $(sha256sum "$DD/setup_salloc_env.sh" | cut -d' ' -f1)"
source "$DD/setup_salloc_env.sh" > "$W/env.log" 2>&1
case "$(python3 -V 2>&1)" in *3.11*) ;; *) stop "environment did not activate ($(python3 -V 2>&1))" ;; esac
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
cd "$W" || stop cd
/usr/bin/time -v nice -n 19 python3 -B "$DD/nd-unfolding/fd_1b_binning.py" \
  --npz "$ND/of_inputs_5d.npz" --bank "$ND/bank_sweep_5d_bkgaware" --detector-dir "$P/s5p-20260926/bank_detector" \
  --pins "$P/fd-1b-20261030/pins.json" --expect-pins-sha256 5adcd576eb46f443fe4133b05044cd315c0eeb0f281e21acee5f2318b4bab248 \
  --flux-constraint "$P/MINERvA-OmniFold/MINERvA101/opt/etc/MParamFiles/data/FluxConstraints/sorted_NuEConstraint_FHC_RHC_IMD.txt" \
  --definition "$DD/nd-unfolding/pv-ladder/readouts/h2_definition.json" --staged "$P/fd-1b-inv-20261101/i0/in" \
  --prep "$P/fd-f1-20261027/f1b3/prep" --cvdenom "$CVD" --expect-cvdenom-sha256 "$CVD_SHA" \
  --out "$W/binning.json" > "$W/binning.out" 2> "$W/binning.time" &
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
echo "binning rc=$rc"
cat "$W/binning.out"
grep -E "Elapsed|Maximum resident|File system inputs|Percent of CPU|Exit status" "$W/binning.time"
sha256sum "$W"/binning.json "$W"/binning.out "$W"/binning.time
echo "end=$(date -u +%FT%TZ)"
