#!/bin/bash
# 1B A2.1, the CV denominator read (S3 (d1), the director's ruling): fd_1b_cvdenom.py on a login node at nice 19,
# 0 node-h, in omnifold_py310 (uproot). It reads mc_truth_denom's six branches from the bank's source omnifile through
# O_NOATIME, checks (A)-(D), and writes the bank rows' CV weight only on PASS. A fresh clone at M in a new pscratch
# directory; writes only under $W. No draw is read and nothing of C2's reading is computed.
# Run detached: setsid nohup bash connect-cvdenom.sh >/dev/null 2>&1 </dev/null &
set -o pipefail
M=fe74696293a80c843ca333540a94dfe846cb6b3a
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
echo "f982085bc9ee91e26b44c81b867a76981122ed604f5e2f187e6e5da2742af402  nd-unfolding/fd_1b_cvdenom.py" > "$W/bound.sha256"
(cd "$DD" && sha256sum -c "$W/bound.sha256") || stop "bound blob differs"
"$PY" -c "import numpy, uproot; print('numpy', numpy.__version__, 'uproot', uproot.__version__)" || stop env
cd "$W" || stop cd
/usr/bin/time -v nice -n 19 "$PY" -B "$DD/nd-unfolding/fd_1b_cvdenom.py" \
  --root "$ND/runEventLoopOmniFold_5D_MEFHC_universes_full_bkgaware.root" \
  --npz "$ND/of_inputs_5d.npz" --expect-npz-sha256 07fccc1abc7204bc29349b4ba96850986fe91e909e83fc54e8d1a6b3922a649f \
  --bank "$ND/bank_sweep_5d_bkgaware" --detector-dir "$P/s5p-20260926/bank_detector" \
  --pins "$P/fd-1b-20261030/pins.json" --expect-pins-sha256 5adcd576eb46f443fe4133b05044cd315c0eeb0f281e21acee5f2318b4bab248 \
  --out "$W/cvdenom.json" > "$W/cvdenom.out" 2> "$W/cvdenom.time"
rc=$?
echo "cvdenom rc=$rc"
cat "$W/cvdenom.out"
grep -E "Elapsed|Maximum resident|File system inputs|Percent of CPU|Exit status" "$W/cvdenom.time"
sha256sum "$W"/cvdenom.json "$W"/cvdenom.out "$W"/cvdenom.time $( [ -e "$W/cvdenom.npy" ] && echo "$W/cvdenom.npy" )
echo "end=$(date -u +%FT%TZ)"
