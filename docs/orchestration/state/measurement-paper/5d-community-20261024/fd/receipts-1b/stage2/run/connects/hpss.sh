B=/pscratch/sd/j/josephrb/fd-1b-20261030; H=fd-1b-20261030/stage2.tar
echo "host=$(hostname) start=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
stop() { echo "STOP: $*"; exit 2; }
[ -e $B/stage2.tar ] && stop "stage2.tar already exists"
tar -cf $B/stage2.tar -C $B runs logs score quarantine pins.json || stop "tar"
ls -l $B/stage2.tar; sha256sum $B/stage2.tar | tee $B/stage2.tar.sha256
hsi -q "mkdir -p fd-1b-20261030" 2>&1 | tail -2
hsi -q "put $B/stage2.tar : $H" 2>&1 | tail -3; echo "put rc=${PIPESTATUS[0]}"
hsi -q "hashcreate $H" 2>&1 | tail -3
hsi -q "hashverify $H" > $B/logs/hpss-hashverify.log 2>&1; echo "hashverify rc=$?"; tail -3 $B/logs/hpss-hashverify.log
hsi -q "ls -l $H" 2>&1 | tail -2
hsi -q "get $B/stage2-retrieved.tar : $H" 2>&1 | tail -2
cmp $B/stage2.tar $B/stage2-retrieved.tar && echo "retrieval cmp: identical" || stop "retrieved copy differs"
sha256sum $B/stage2-retrieved.tar
echo "done $(date -u +%Y-%m-%dT%H:%M:%SZ)"
