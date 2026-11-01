# 1B investigation, after the I2 bulk (jobs 60658473-76): ledger, lanes, products, atime, i2 on login37, HPSS
P=/pscratch/sd/j/josephrb; V=$P/fd-1b-inv-20261101; DD=$V/deploy; H=fd-1b-inv-20261101/i2.tar
PY="env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I"
R=$DD/docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-1b/stage2/run/score/gate-d.json
echo "host=$(hostname) start=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
stop() { echo "STOP: $*"; exit 2; }
echo "== sacct"; sacct -j 60658473,60658474,60658475,60658476 -X -n -P -o JobID,JobName,State,ExitCode,Elapsed,NNodes,Start,End | tee $V/logs/i2-sacct.psv
echo "== lanes"; for j in 60658473 60658474 60658475 60658476; do echo "job $j: s5c rc!=0 lines: $(grep -h '\[s5c\] task=.* rc=' $V/i2/lanes/line*-$j.log | grep -vc ' rc=0 ')  rc=0 lines: $(grep -h '\[s5c\] task=.* rc=0 ' $V/i2/lanes/line*-$j.log | wc -l)"; done
grep -h "\[f1-lane\].*rc=" $V/i2/lanes/line*-6065847[3-6].log | grep -v " rc=0 " | head
grep -l -i "refusing\|Traceback" $V/i2/lanes/*.log $V/i2/lanes/logs/*.log 2>/dev/null | head
echo "== products: $(ls $V/i2/unf/fd1b_inv_*.npz | wc -l) of 204; partials: $(ls $V/i2/unf/ | grep -c partial)"
echo "== walls of the bulk"; $PY - "$V" <<'PYEOF'
import glob, json, sys, numpy as np
V = sys.argv[1]
s, r = [], []
for p in glob.glob(f"{V}/i2/unf/fd1b_inv_*.npz"):
    m = json.loads(str(np.load(p, allow_pickle=False)["meta"])); s.append(m["seconds_unfold"]); r.append(m["peak_rss_kib"])
print(f"n={len(s)} seconds_unfold median {np.median(s):.1f} max {max(s):.1f}; peak_rss_kib max {max(r)}")
PYEOF
echo "== atime sidecars"; $PY - "$V" <<'PYEOF'
import glob, json, sys
V = sys.argv[1]; fs = glob.glob(f"{V}/i2/unf/atime-*.json"); moved = []
for f in fs: moved += json.load(open(f))["moved"]
print(f"sidecars={len(fs)} moved={sorted(set(moved))}")
PYEOF
xargs -a $V/logs/i2-sources.txt stat -c '%X %Y %s %n' > $V/logs/i2-stat-after.txt
if cmp -s $V/logs/i2-stat-before.txt $V/logs/i2-stat-after.txt; then echo "sources atime/mtime/size: UNCHANGED ($(wc -l < $V/logs/i2-stat-after.txt))"
else echo "DEVIATION: stat changed:"; diff $V/logs/i2-stat-before.txt $V/logs/i2-stat-after.txt | head -20; fi
echo "== i2"; [ -e $V/i2/i2.json ] && stop "i2.json exists"
t0=$(date +%s)
nice -n 19 $PY $DD/nd-unfolding/fd_1b_inv.py i2 --staged $V/i0/in --unfolds $V/i2/unf --gate-d $R --i0 $V/i0/i0.json \
  --out $V/i2/i2.json > $V/logs/i2.log 2>&1
echo "i2 rc=$? wall_s=$(( $(date +%s) - t0 ))"; grep -v "UserWarning\|warnings.warn" $V/logs/i2.log | tail -4
ls -l $V/i2/i2.json 2>&1; sha256sum $V/i2/i2.json 2>&1
echo "== HPSS"; [ -e $V/i2.tar ] && stop "i2.tar exists"
tar -cf $V/i2.tar -C $V i2 tables logs || stop tar
ls -l $V/i2.tar; sha256sum $V/i2.tar | tee $V/i2.tar.sha256
hpssquota 2>&1 | grep -i "HPSS"
hsi -q "put $V/i2.tar : $H" 2>&1 | tail -2
hsi -q "hashcreate $H" 2>&1 | tail -2
hsi -q "hashverify $H" > $V/logs/hpss-i2-hashverify.log 2>&1; echo "hashverify rc=$?"; tail -1 $V/logs/hpss-i2-hashverify.log
hsi -q "get $V/i2-retrieved.tar : $H" 2>&1 | tail -1
cmp $V/i2.tar $V/i2-retrieved.tar && echo "retrieval cmp: identical" || stop "retrieved copy differs"
rm -f $V/i2-retrieved.tar
echo "end=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
