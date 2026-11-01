# 1B investigation, after I2-0 (job 60656806): ledger, lanes, walls, CV controls, atime, HPSS
P=/pscratch/sd/j/josephrb; V=$P/fd-1b-inv-20261101; DD=$V/deploy; J=60656806; H=fd-1b-inv-20261101/i2-0.tar
PY="env -u PYTHONPATH $HOME/.conda/envs/root_6_28/bin/python3 -I"
echo "host=$(hostname) start=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
stop() { echo "STOP: $*"; exit 2; }
echo "== sacct"; sacct -j $J -n -P -o JobID,JobName,State,ExitCode,Elapsed,NNodes,Start,End | tee $V/logs/i2-0-sacct.psv
echo "== lanes"; grep -h "rc=" $V/i2/lanes/line*-$J.log | grep -E "\[s5c\] task=.*rc=|\[f1-lane\]" | tail -20
grep -h -i "refusing\|Traceback\|Error" $V/i2/lanes/*.log $V/i2/lanes/logs/*.log 2>/dev/null | grep -v "UserWarning\|warnings.warn" | head -10
echo "== products"; ls $V/i2/unf/*.npz | wc -l; ls $V/i2/unf/
echo "== walls"; nice -n 19 $PY $DD/nd-unfolding/fd_1b_inv.py walls --unfolds $V/i2/unf --tag fd1b_inv --out $V/i2/walls-i2-0.json; echo "walls rc=$?"
echo "== CV controls (against the staged derivation CV copy)"
nice -n 19 $PY - "$V" <<'PYEOF'
import json, sys, numpy as np
V = sys.argv[1]
ref = np.load(f"{V}/i0/in/derivation/fd1b_derivation_CV.npz")["xsec_flat"]
for m in "ABC":
    z = np.load(f"{V}/i2/unf/fd1b_inv_{m}_CV.npz", allow_pickle=False)
    meta = json.loads(str(z["meta"]))
    print(m, "CV bitwise =", bool(np.array_equal(z["xsec_flat"], ref)), "seconds_unfold", meta["seconds_unfold"], "peak_rss_kib", meta["peak_rss_kib"],
          "code", meta["code_sha256"]["fd_1b_inv.py"][:16])
for p in ["A_MaRES_0", "B_MaRES_0", "C_MaRES_0", "A_2p2h_0", "A_LowQ2_1"]:
    z = np.load(f"{V}/i2/unf/fd1b_inv_{p}.npz", allow_pickle=False)
    print(p, "differs from CV:", not np.array_equal(z["xsec_flat"], ref), "finite:", bool(np.all(np.isfinite(z["xsec_flat"]))))
PYEOF
echo "== atime sidecars"; for f in $V/i2/unf/atime-*.json; do $PY -c "import json,sys; d=json.load(open(sys.argv[1])); print(sys.argv[1].rsplit('/',1)[1], 'files', len(d['files']), 'moved', d['moved'])" $f; done
xargs -a $V/logs/i2-0-sources.txt stat -c '%X %Y %s %n' > $V/logs/i2-0-stat-after.txt
if cmp -s $V/logs/i2-0-stat-before.txt $V/logs/i2-0-stat-after.txt; then echo "sources atime/mtime/size: UNCHANGED ($(wc -l < $V/logs/i2-0-stat-after.txt))"
else echo "DEVIATION: stat changed:"; diff $V/logs/i2-0-stat-before.txt $V/logs/i2-0-stat-after.txt | head -20; fi
echo "== HPSS"; [ -e $V/i2-0.tar ] && stop "i2-0.tar exists"
tar -cf $V/i2-0.tar -C $V i2 tables logs || stop tar
ls -l $V/i2-0.tar; sha256sum $V/i2-0.tar | tee $V/i2-0.tar.sha256
hpssquota 2>&1 | grep -i "HPSS"
hsi -q "put $V/i2-0.tar : $H" 2>&1 | tail -2
hsi -q "hashcreate $H" 2>&1 | tail -2
hsi -q "hashverify $H" > $V/logs/hpss-i2-0-hashverify.log 2>&1; echo "hashverify rc=$?"; tail -1 $V/logs/hpss-i2-0-hashverify.log
hsi -q "get $V/i2-0-retrieved.tar : $H" 2>&1 | tail -1
cmp $V/i2-0.tar $V/i2-0-retrieved.tar && echo "retrieval cmp: identical" || stop "retrieved copy differs"
rm -f $V/i2-0-retrieved.tar
echo "end=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
