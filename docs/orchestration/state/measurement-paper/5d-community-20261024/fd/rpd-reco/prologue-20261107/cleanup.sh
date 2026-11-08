hostname; date -u +%FT%TZ
find /dev/shm/limres-rpd-prologue-20261107 -maxdepth 1 -printf '%y %s %P\n' | sort -k3
sha256sum /dev/shm/limres-rpd-prologue-20261107/policy-config.json /dev/shm/limres-rpd-prologue-20261107/strace-probe.txt
rm -rf -- /dev/shm/limres-rpd-prologue-20261107
if [ -e /dev/shm/limres-rpd-prologue-20261107 ]; then echo "STILL PRESENT"; else echo "absent: /dev/shm/limres-rpd-prologue-20261107"; fi
ls /dev/shm | grep -c '^limres-prol' || true
