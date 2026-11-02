# 1B staged, stage 0, after D-0 (job 60678921): ledger, lanes, walls, the Dnom CV control, atime, HPSS
P=/pscratch/sd/j/josephrb; W=$P/fd-1b-staged-20261102; DD=$W/deploy; V=$P/fd-1b-inv-20261101; J=60678921
H=fd-1b-staged-20261102/stage0-d0.tar
PY="env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I"
echo "host=$(hostname) start=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
stop() { echo "STOP: $*"; exit 2; }
echo "== sacct"; sacct -j $J -n -P -o JobID,JobName,State,ExitCode,Elapsed,NNodes,Start,End,MaxRSS | tee $W/logs/d0-sacct.psv
echo "== lanes"; grep -h "\[f1-lane\].*rc=" $W/stage0/lanes/line*-$J.log 2>/dev/null | tail -12
grep -h -i "refusing\|Traceback" $W/stage0/lanes/*.log $W/stage0/lanes/logs/*.log 2>/dev/null | head -10
echo "== products: $(ls $W/stage0/unf/fd1b_d_*.npz 2>/dev/null | wc -l) of 8; partials: $(ls $W/stage0/unf/ | grep -c partial)"; ls $W/stage0/unf/
echo "== walls"; [ -e $W/stage0/walls-d0.json ] && stop "walls-d0.json exists"
nice -n 19 $PY $DD/nd-unfolding/fd_1b_moded.py walls --unfolds $W/stage0/unf --tag fd1b_d --out $W/stage0/walls-d0.json; echo "walls rc=$?"
echo "== the Dnom CV control and per-product meta (staged copy read with O_NOATIME)"
nice -n 19 $PY - "$W" "$V" "$DD" <<'PYEOF'
import glob, json, sys
import numpy as np
W, V, DD = sys.argv[1:4]
sys.path.insert(0, DD + "/nd-unfolding")
import fd_1b_inv as inv
ref = inv.load_npz(__import__("pathlib").Path(f"{V}/i0/in/derivation/fd1b_derivation_CV.npz"))["xsec_flat"]
for p in sorted(glob.glob(f"{W}/stage0/unf/fd1b_d_*.npz")):
    z = np.load(p, allow_pickle=False)   # this lane's own products
    meta = json.loads(str(z["meta"]))
    x = z["xsec_flat"]
    print(p.rsplit("/", 1)[1], "seconds_unfold", round(meta["seconds_unfold"], 1), "peak_rss_kib", meta["peak_rss_kib"],
          "finite", bool(np.all(np.isfinite(x))), "equals_derivation_CV", bool(np.array_equal(x, ref)),
          "code", meta["code_sha256"]["fd_1b_moded.py"][:16])
print("atime of the staged CV copy moved:", inv.atime_check() if hasattr(inv, "atime_check") else "n/a")
PYEOF
echo "== atime sidecars"; for f in $W/stage0/unf/atime-*.json; do $PY -c "import json,sys; d=json.load(open(sys.argv[1])); print(sys.argv[1].rsplit('/',1)[1], 'files', len(d['files']), 'moved', d['moved'])" $f; done
xargs -a $W/logs/stage0-sources.txt stat -c '%X %Y %s %n' > $W/logs/d0-stat-after.txt
if cmp -s $W/logs/stage0-stat-before.txt $W/logs/d0-stat-after.txt; then echo "sources atime/mtime/size: UNCHANGED ($(wc -l < $W/logs/d0-stat-after.txt))"
else echo "DEVIATION: stat changed:"; diff $W/logs/stage0-stat-before.txt $W/logs/d0-stat-after.txt | head -20; fi
echo "== HPSS"; [ -e $W/stage0-d0.tar ] && stop "stage0-d0.tar exists"
tar -cf $W/stage0-d0.tar -C $W stage0 tables logs || stop tar
ls -l $W/stage0-d0.tar; sha256sum $W/stage0-d0.tar | tee $W/stage0-d0.tar.sha256
hpssquota 2>&1 | grep -i "HPSS"
hsi -q "mkdir -p fd-1b-staged-20261102" 2>&1 | tail -1
hsi -q "put $W/stage0-d0.tar : $H" 2>&1 | tail -2
hsi -q "hashcreate $H" 2>&1 | tail -2
hsi -q "hashverify $H" > $W/logs/hpss-d0-hashverify.log 2>&1; echo "hashverify rc=$?"; tail -1 $W/logs/hpss-d0-hashverify.log
hsi -q "get $W/stage0-d0-retrieved.tar : $H" 2>&1 | tail -1
cmp $W/stage0-d0.tar $W/stage0-d0-retrieved.tar && echo "retrieval cmp: identical" || stop "retrieved copy differs"
rm -f $W/stage0-d0-retrieved.tar
echo "end=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
