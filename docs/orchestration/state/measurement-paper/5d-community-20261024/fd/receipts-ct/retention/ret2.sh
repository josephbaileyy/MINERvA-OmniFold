set -u
P=/pscratch/sd/j/josephrb
echo "host=$(hostname) date=$(date -u +%FT%TZ)"
for d in lateral unf merged evloop evloop/* dump-run unfold-run; do echo "== w2b/$d"; ls -la --time-style=+%F $P/w2-recoil-20261006/w2b/$d 2>&1 | head -30; done
echo "== HPSS top"
hsi -q "ls -l /home/j/josephrb" 2>&1 | head -120
echo "== hpssquota"; hpssquota 2>&1 | tail -5
echo "== pscratch usage"; myquota 2>&1 | tail -6
