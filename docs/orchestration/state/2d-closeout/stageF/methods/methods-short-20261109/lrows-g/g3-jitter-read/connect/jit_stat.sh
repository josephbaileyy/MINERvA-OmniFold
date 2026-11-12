#!/bin/bash
# G3 (referee6 major 7), step 1: STAT ONLY of I0's 21 data-jitter products (the base and j1..j20,
# FD-1B-INV-DECLARATION.md:131-133). No file is opened or read; stat moves no atime. Named paths only; no directory is
# listed. Login node only. Launched from a /dev/shm copy of itself ($1), which it deletes.
SELF=$1
D=/pscratch/sd/j/josephrb/s5p-20260926/runs/s2/num/data
case "$(hostname)" in login*) ;; *) echo "STOP: not a login node: $(hostname)"; rm -f -- "$SELF"; exit 9 ;; esac
echo "node $(hostname) $(date -u +%FT%TZ)"
echo "script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
n=0; m=0
for j in - 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20; do
  f="$D/data_b-_j$j.npz"
  if out=$(stat -c 'stat|%n|size=%s|mtime=%Y|atime=%X' "$f" 2>&1); then echo "$out"; n=$((n + 1)); else echo "MISSING|$f|$out"; m=$((m + 1)); fi
done
echo "present $n of 21; missing $m"
rm -f -- "$SELF"
[ "$m" -eq 0 ]
