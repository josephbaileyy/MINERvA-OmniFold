#!/bin/bash
# 1B binding 3, step 1's merge (A2.1 §11 stage 2): fd_1b_c2.py c2check-merge of the two per-truth gate records into
# the one gate record binding 3 pins. On a login node at nice 19, single-threaded, 0 node-h, in the environment the
# 1B jobs use, under 1B's guarded launcher (fd_1b_noatime_guard.py --declared). M = a47cfb4b, where fd_1b_c2 is
# 522d7edd, the code both parts were read by. Each part is named by its sha256 (arguments 1 and 2: G18's, then
# AR23's, from stage 1's committed receipts), which c2check-merge checks before reading it. A fresh clone at M in a new
# pscratch directory; writes only under $W. Not under set -u, which aborts the root_6_28 activation.
# Run detached: setsid nohup bash connect-merge.sh SHA_G18 SHA_AR23 >/dev/null 2>&1 </dev/null &
set -o pipefail
SHA_G18=$1; SHA_AR23=$2
M=a47cfb4b9410cbf0cc8e34bee98e73c3e110f171
P=/pscratch/sd/j/josephrb; W=$P/fd-1b-b3-merge; DD=$W/deploy
G18=$P/fd-1b-b3-c2check-g18/gate-g18.json; AR23=$P/fd-1b-b3-c2check-ar23/gate-ar23.json
stop() { echo "STOP $*"; echo "end=$(date -u +%FT%TZ)"; exit 2; }
for s in "$SHA_G18" "$SHA_AR23"; do
  case "$s" in [0-9a-f][0-9a-f]*) [ ${#s} = 64 ] || { echo "STOP a part digest is not 64 hex: '$s'"; exit 2; } ;;
    *) echo "STOP a part digest is not 64 hex: '$s'"; exit 2 ;; esac
done
[ -e "$W" ] && { echo "STOP $W exists"; exit 2; }
mkdir -p "$W/logs" || exit 2
exec >> "$W/logs/connect-merge.log" 2>&1
echo "host=$(hostname) start=$(date -u +%FT%TZ) pid=$$"
git clone --quiet https://github.com/josephbaileyy/MINERvA-OmniFold "$DD" && git -C "$DD" checkout --quiet --detach "$M" || stop clone
n=$(git -C "$DD" status --porcelain | wc -l); h=$(git -C "$DD" rev-parse HEAD); echo "deploy porcelain_lines=$n head=$h"
[ "$n" = "0" ] && [ "$h" = "$M" ] || stop "deploy not clean at M"
cat > "$W/bound.sha256" <<SUMS
522d7edd71643df61d0c5ef5a7488834e664eb36d20c3e0c0b46e10a5808f02f  nd-unfolding/fd_1b_c2.py
062628b69976f730d9d394e64ecf6f93d9952654306471ac0119542c6b07dd67  nd-unfolding/fd_1b_mc.py
ee20534c20504aa1335bad4e75be067c0465c7faaa60d2a14a47abb81e22f60c  nd-unfolding/fd_1b_noatime_guard.py
SUMS
(cd "$DD" && sha256sum -c "$W/bound.sha256") || stop "bound blobs differ"
echo "sourcing $DD/setup_salloc_env.sh sha256 $(sha256sum "$DD/setup_salloc_env.sh" | cut -d' ' -f1)"
source "$DD/setup_salloc_env.sh" > "$W/logs/env.log" 2>&1
case "$(python3 -V 2>&1)" in *3.11*) ;; *) stop "environment did not activate ($(python3 -V 2>&1))" ;; esac
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
cd "$W" || stop cd
/usr/bin/time -v nice -n 19 python3 -B "$DD/nd-unfolding/fd_1b_noatime_guard.py" --declared -- "$DD/nd-unfolding/fd_1b_c2.py" c2check-merge \
  --part "$G18" --expect-part-sha256 "$SHA_G18" --part "$AR23" --expect-part-sha256 "$SHA_AR23" \
  --out "$W/gate.json" > "$W/merge.out" 2> "$W/merge.time"
rc=$?
echo "c2check-merge rc=$rc"
cat "$W/merge.out"
grep -E "fd_1b_noatime_guard|Elapsed|Maximum resident|Exit status" "$W/merge.time"
sha256sum "$W/gate.json" "$W/merge.out" 2>/dev/null
echo "end=$(date -u +%FT%TZ)"
