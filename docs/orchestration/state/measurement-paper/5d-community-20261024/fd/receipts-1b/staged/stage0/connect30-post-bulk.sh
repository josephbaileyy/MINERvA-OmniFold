# 1B staged, stage 0, after the bulk (jobs 60683107-08): ledger, lanes, products, atime, the readout (rule K) on
# login37, then the HPSS copies with every hsi call time-limited.
P=/pscratch/sd/j/josephrb; W=$P/fd-1b-staged-20261102; DD=$W/deploy; V=$P/fd-1b-inv-20261101
RC=$DD/docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-1b/inv
PY="env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I"
WANT_D0=a97f366cc15afc553d3f4407ec6406205a04c51b839963b7133129a4f6d5c6b9
echo "host=$(hostname) start=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
stop() { echo "STOP: $*"; exit 2; }
echo "== sacct"; sacct -j 60683107,60683108 -n -P -o JobID,JobName,State,ExitCode,Elapsed,NNodes,Start,End,MaxRSS | tee $W/logs/bulk-sacct.psv
echo "== lanes"; for j in 60683107 60683108; do echo "job $j: f1-lane rc!=0 lines: $(grep -h '\[f1-lane\].*rc=' $W/stage0/lanes/line*-$j.log | grep -vc ' rc=0 ')  rc=0 lines: $(grep -h '\[f1-lane\].*rc=0 ' $W/stage0/lanes/line*-$j.log | wc -l)"; done
grep -l -i "refusing\|Traceback" $W/stage0/lanes/*.log $W/stage0/lanes/logs/*.log 2>/dev/null | head
echo "== products: $(ls $W/stage0/unf/fd1b_d_*.npz | wc -l) of 104; partials: $(ls $W/stage0/unf/ | grep -c partial)"
echo "== walls of the bulk"; $PY - "$W" <<'PYEOF'
import glob, json, sys, numpy as np
W = sys.argv[1]; s, r = [], []
for p in glob.glob(f"{W}/stage0/unf/fd1b_d_*.npz"):
    m = json.loads(str(np.load(p, allow_pickle=False)["meta"])); s.append(m["seconds_unfold"]); r.append(m["peak_rss_kib"])
print(f"n={len(s)} seconds_unfold median {np.median(s):.1f} max {max(s):.1f}; peak_rss_kib max {max(r)}")
PYEOF
echo "== atime sidecars"; $PY - "$W" <<'PYEOF'
import glob, json, sys
W = sys.argv[1]; fs = glob.glob(f"{W}/stage0/unf/atime-*.json"); moved = []
for f in fs: moved += json.load(open(f))["moved"]
print(f"sidecars={len(fs)} moved={sorted(set(moved))}")
PYEOF
xargs -a $W/logs/stage0-sources.txt stat -c '%X %Y %s %n' > $W/logs/bulk-stat-after.txt
if cmp -s $W/logs/bulk-stat-before.txt $W/logs/bulk-stat-after.txt; then echo "sources atime/mtime/size: UNCHANGED ($(wc -l < $W/logs/bulk-stat-after.txt))"
else echo "DEVIATION: stat changed:"; diff $W/logs/bulk-stat-before.txt $W/logs/bulk-stat-after.txt | head -20; fi
echo "== readout"; [ -e $W/stage0/readout.json ] && stop "readout.json exists"
t0=$(date +%s)
nice -n 19 $PY $DD/nd-unfolding/fd_1b_moded.py readout --staged $V/i0/in --unfolds $W/stage0/unf --i2-unfolds $V/i2/unf \
  --i2 $RC/i2/i2.json --i0 $RC/i0/i0.json --definition $DD/nd-unfolding/pv-ladder/readouts/h2_definition.json \
  --tag fd1b_d --out $W/stage0/readout.json > $W/logs/readout.log 2>&1
echo "readout rc=$? wall_s=$(( $(date +%s) - t0 ))"; grep -v "UserWarning\|warnings.warn" $W/logs/readout.log | tail -4
ls -l $W/stage0/readout.json 2>&1; sha256sum $W/stage0/readout.json 2>&1
xargs -a $W/logs/stage0-sources.txt stat -c '%X %Y %s %n' > $W/logs/readout-stat-after.txt
cmp -s $W/logs/bulk-stat-before.txt $W/logs/readout-stat-after.txt && echo "after readout: sources UNCHANGED" || echo "DEVIATION after readout: stat changed"
echo "== HPSS"; [ -e $W/stage0.tar ] && stop "stage0.tar exists"
tar -cf $W/stage0.tar -C $W stage0 tables logs || stop tar
sha256sum $W/stage0.tar | tee $W/stage0.tar.sha256
out=$(timeout 90 hsi -q "ls -d fd-1b-inv-20261101" 2>&1); rc=$?; echo "$out" | tail -1; echo "probe rc=$rc"
if echo "$out" | grep -q Maintenance || [ "$rc" != "0" ]; then echo "HPSS: not available; both tars stay on pscratch"; echo "end=$(date -u +%Y-%m-%dT%H:%M:%SZ)"; exit 0; fi
[ "$(sha256sum $W/stage0-d0.tar | cut -d' ' -f1)" = "$WANT_D0" ] || stop "stage0-d0.tar's digest changed"
hpssquota 2>&1 | grep -i "HPSS"
timeout 300 hsi -q "mkdir -p fd-1b-staged-20261102" 2>&1 | tail -1
for t in stage0-d0 stage0; do
  H=fd-1b-staged-20261102/$t.tar
  timeout 900 hsi -q "put $W/$t.tar : $H" 2>&1 | tail -1
  timeout 600 hsi -q "hashcreate $H" 2>&1 | tail -1
  timeout 600 hsi -q "hashverify $H" > $W/logs/hpss-$t-hashverify.log 2>&1; echo "$t hashverify rc=$?"; tail -1 $W/logs/hpss-$t-hashverify.log
  timeout 900 hsi -q "get $W/$t-retrieved.tar : $H" 2>&1 | tail -1
  cmp $W/$t.tar $W/$t-retrieved.tar && echo "$t retrieval cmp: identical" || stop "$t retrieved copy differs"
  rm -f $W/$t-retrieved.tar
done
echo "end=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
