#!/bin/bash
# Stand-in run of bsel_read.sh inside a Debian container (Dockerfile.txt). Stubs: sacct (logs its call), and sha256sum
# (sha256sum_stub.py: a planted file holding "STANDIN-PIN:<pin>" hashes to its pin; anything else is hashed for real).
# squeue is a stub that records any call. Everything else is the real script and the real tools (dd, stat, tar).
# Usage (in the container): standin.sh <ok | missing | pin_bad | out_exists | window_ended | fence_running>
V=${1:?variant}
OUT=/pscratch/sd/j/josephrb/bsel-20261124
mkdir -p /stub
cp /standin/sha256sum_stub.py /stub/sha256sum; chmod +x /stub/sha256sum
ROWS="99|cov2d_x|COMPLETED"; [ "$V" = fence_running ] && ROWS="99|rpd_reco_p1|RUNNING"
printf '#!/bin/bash\necho "sacct $*" >> /tmp/calls.log\nprintf "%%s\\n" "%s" "100|ibub_run|RUNNING" "101|s2r_run|COMPLETED"\n' "$ROWS" > /stub/sacct
printf '#!/bin/bash\necho "squeue was called" >> /tmp/calls.log; exit 99\n' > /stub/squeue
chmod +x /stub/sacct /stub/squeue
export PATH=/stub:$PATH
: > /tmp/calls.log
# the planted sources: the connect's own list, each holding its pin's text
sed -n "/^SOURCES='/,/'$/p" /connect/bsel_read.sh | sed "s/^SOURCES='//; s/'$//" > /tmp/sources.txt
i=0; while read -r pin src; do
  [ -n "$src" ] || continue; i=$((i + 1)); mkdir -p "$(dirname "$src")"
  p=$pin; [ "$V" = pin_bad ] && [ "$i" -eq 3 ] && p=$(printf '0%.0s' $(seq 64))
  printf 'STANDIN-PIN:%s\n' "$p" > "$src"
done < /tmp/sources.txt
[ "$V" = missing ] && rm -f /pscratch/sd/j/josephrb/pv-ladder-20261024/products/L-5D-PV_e_closure_nuwro.npz
[ "$V" = out_exists ] && mkdir -p $OUT
WEND=$(( $(date +%s) + 900 )); [ "$V" = window_ended ] && WEND=$(( $(date +%s) - 1 ))
sleep 1; touch /tmp/after-plant
cp /connect/bsel_read.sh /dev/shm/bselc.1.sh
bash /dev/shm/bselc.1.sh /dev/shm/bselc.1.sh $WEND cov2d,rpd_,d2s0,covfix; rc=$?
echo "=== script rc=$rc; /dev/shm copy left: $([ -e /dev/shm/bselc.1.sh ] && echo yes || echo no)"
echo "=== $OUT/logs/connect-bsel.log"; cat $OUT/logs/connect-bsel.log 2>/dev/null
if [ -f $OUT/fetch-bsel.tar ]; then mkdir /tmp/x && tar -C /tmp/x -xf $OUT/fetch-bsel.tar && ( cd /tmp/x/fetch-bsel && sha256sum -c --strict --quiet RECORDS.SHA256SUMS ) && echo "=== tar RECORDS.SHA256SUMS: OK ($(grep -c . /tmp/x/fetch-bsel/RECORDS.SHA256SUMS) lines, $(ls /tmp/x/fetch-bsel | grep -vc RECORDS) files)"; fi
echo "=== stub calls"; cat /tmp/calls.log
echo "=== written under /pscratch outside $OUT (newer than the planting):"; find /pscratch -newer /tmp/after-plant ! -path "$OUT" ! -path "$OUT/*" | grep -v '^/pscratch/sd/j/josephrb$' | head
