#!/bin/bash
# 1B pre-check Part 1, after P4: fetch P4's own small records from $V/p4 for the receipt (coverage-5b-audit audits the
# stat and atime records). Login node, 0 node-h, read-only: it writes nothing on the cluster except its own /dev/shm
# copy, which it deletes. It reads only files the P4 connect wrote; no original, staged copy or product is opened.
# In order: the COV2D fence (rs1_* and ens1_* allowed; anything else refuses); a listing of $V/p4; the sha256 of each
# file in an explicit list; a base64 tar of that list.
SELF=$1
V=/pscratch/sd/j/josephrb/fd-1b-precheck-fd-20261107
finish() { echo "== pfd-p4-fetch rc=$1 $(date -u +%FT%TZ)"; rm -f -- "$SELF"; exit "$1"; }
case "$(hostname)" in login*) ;; *) echo "STOP: not a login node: $(hostname)"; finish 9 ;; esac
echo "node $(hostname) $(date -u +%FT%TZ)"
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
echo "== fence (allowed names: rs1_* and ens1_*; anything else refuses)"
out=$(squeue -u josephrb -h -o '%i|%j|%T|%M|%l'); frc=$?
printf '%s\n' "$out"
bad=$(printf '%s\n' "$out" | awk -F'|' 'NF && $2 !~ /^(rs1_|ens1_)/')
echo "squeue rc=$frc; refusing rows: [$bad]"
[ "$frc" -eq 0 ] && [ -z "$bad" ] || { echo "STOP: the fence is not clear"; finish 3; }
echo "== listing of $V/p4"
ls -l --time-style=+%FT%T "$V/p4"
list=(p4/readout.json p4/readout.stdout p4/readout.stderr p4/stage-atime-before.tsv p4/stage-atime-after-rehash.tsv
      p4/stage-atime-after-readout.tsv p4/stat-p4-before.txt p4/stat-p4-after.txt)
for f in "${list[@]}"; do
  [ -f "$V/$f" ] || { echo "STOP: $f is missing"; finish 5; }
  echo "sha256 $(sha256sum "$V/$f" | cut -d' ' -f1) $f"
done
echo "== TAR BEGIN"
tar -C "$V" -cf - "${list[@]}" | base64 -w 76
echo "== TAR END tar rc=${PIPESTATUS[0]}"
finish 0
