# 1B staged, stage 0: the D-0 HPSS copy, retried after connect 27's maintenance hang (director's ruling 1).
# Every hsi call is time-limited, so a maintenance hold ends the connect instead of hanging it.
P=/pscratch/sd/j/josephrb; W=$P/fd-1b-staged-20261102; H=fd-1b-staged-20261102/stage0-d0.tar
WANT=a97f366cc15afc553d3f4407ec6406205a04c51b839963b7133129a4f6d5c6b9
echo "host=$(hostname) start=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
stop() { echo "STOP: $*"; exit 2; }
out=$(timeout 90 hsi -q "ls -d fd-1b-inv-20261101" 2>&1); rc=$?; echo "$out" | tail -2; echo "probe rc=$rc"
echo "$out" | grep -q "Maintenance" && stop "HPSS maintenance has not cleared"
[ "$rc" = "0" ] || stop "hsi probe failed or timed out"
got=$(sha256sum $W/stage0-d0.tar | cut -d' ' -f1); echo "tar sha256 $got"; [ "$got" = "$WANT" ] || stop "the tar's digest changed"
hpssquota 2>&1 | grep -i "HPSS"
timeout 300 hsi -q "mkdir -p fd-1b-staged-20261102" 2>&1 | tail -1
timeout 900 hsi -q "put $W/stage0-d0.tar : $H" 2>&1 | tail -2
timeout 600 hsi -q "hashcreate $H" 2>&1 | tail -2
timeout 600 hsi -q "hashverify $H" > $W/logs/hpss-d0-hashverify.log 2>&1; echo "hashverify rc=$?"; tail -1 $W/logs/hpss-d0-hashverify.log
timeout 900 hsi -q "get $W/stage0-d0-retrieved.tar : $H" 2>&1 | tail -1
cmp $W/stage0-d0.tar $W/stage0-d0-retrieved.tar && echo "retrieval cmp: identical" || stop "retrieved copy differs"
rm -f $W/stage0-d0-retrieved.tar
echo "end=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
