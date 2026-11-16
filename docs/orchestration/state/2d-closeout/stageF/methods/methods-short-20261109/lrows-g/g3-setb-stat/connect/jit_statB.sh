#!/bin/bash
# G3 set B (the director, 2026-11-12): STAT ONLY of s5p study N's jitter-free replicas data_b{1..100}_j-.npz
# (S1-DECLARATION.md:66 names "set B (100, no jitter)"; only b1 and b2 are in a committed inventory). No file is
# opened or read; stat moves no atime. Named paths only; no directory is listed. Login node only. Launched from a
# /dev/shm copy of itself ($1), which it deletes. rc 0 only if all 100 exist.
SELF=$1
D=/pscratch/sd/j/josephrb/s5p-20260926/runs/s2/num/data
case "$(hostname)" in login*) ;; *) echo "STOP: not a login node: $(hostname)"; rm -f -- "$SELF"; exit 9 ;; esac
echo "node $(hostname) $(date -u +%FT%TZ)"
echo "script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
n=0; m=0
for b in $(seq 1 100); do
  f="$D/data_b${b}_j-.npz"
  if out=$(stat -c 'stat|%n|size=%s|mtime=%Y|atime=%X' "$f" 2>&1); then echo "$out"; n=$((n + 1)); else echo "MISSING|$f"; m=$((m + 1)); fi
done
echo "present $n of 100; missing $m"
rm -f -- "$SELF"
[ "$m" -eq 0 ]
