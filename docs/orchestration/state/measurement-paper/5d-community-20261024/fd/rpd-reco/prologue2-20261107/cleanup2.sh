hostname; date -u +%FT%TZ
find /dev/shm/limres-rpd-prologue2-20261107 -maxdepth 1 -printf '%y %s %P\n' | sort -k3
rm -rf -- /dev/shm/limres-rpd-prologue2-20261107
if [ -e /dev/shm/limres-rpd-prologue2-20261107 ]; then echo "STILL PRESENT"; else echo "absent: /dev/shm/limres-rpd-prologue2-20261107"; fi
echo "launcher copies left: $(ls /dev/shm | grep -c '^limres-prol2')"
