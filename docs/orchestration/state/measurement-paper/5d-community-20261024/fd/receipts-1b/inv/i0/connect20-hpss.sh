V=/pscratch/sd/j/josephrb/fd-1b-inv-20261101; H=fd-1b-inv-20261101/i0.tar
echo "host=$(hostname) start=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
stop() { echo "STOP: $*"; exit 2; }
[ -e $V/i0.tar ] && stop "i0.tar already exists"
tar -cf $V/i0.tar -C $V i0 logs || stop tar
ls -l $V/i0.tar; sha256sum $V/i0.tar | tee $V/i0.tar.sha256
hsi -q "mkdir -p fd-1b-inv-20261101" 2>&1 | tail -2
hsi -q "put $V/i0.tar : $H" 2>&1 | tail -3
hsi -q "hashcreate $H" 2>&1 | tail -3
hsi -q "hashverify $H" > $V/logs/hpss-i0-hashverify.log 2>&1; echo "hashverify rc=$?"; tail -2 $V/logs/hpss-i0-hashverify.log
hsi -q "ls -l $H" 2>&1 | tail -2
hsi -q "get $V/i0-retrieved.tar : $H" 2>&1 | tail -2
cmp $V/i0.tar $V/i0-retrieved.tar && echo "retrieval cmp: identical" || stop "retrieved copy differs"
rm -f $V/i0-retrieved.tar
echo "done $(date -u +%Y-%m-%dT%H:%M:%SZ)"
