#!/bin/bash
# S1 assembly output and the complete logs to HPSS (S1-DECLARATION.md section 3.1: the npz stays on pscratch and HPSS),
# after the amendment-1 assembly. Same steps as products_hpss.sh, with its own tar name so that copy is not overwritten.
# hashcreate, hashverify, a retrieval compare; then the retrieved copy is removed. Login node, no Slurm job.
#   bash assembly_hpss.sh <B> <HPSS dir>
set -o pipefail
B="${1:?B}"; HDIR="${2:?hpss dir}"; W="$B/assembly-hpss"; TAR="$W/s1-assembly.tar"; LOG="$W/assembly-hpss.log"
mkdir -p "$W/retrieve"
stamp() { date -u +%FT%TZ; }
{
  echo "[H] $(stamp) start host=$(hostname)"
  ( cd / && find "$B/s1_assembly.npz" "$B/s1_assembly.json" "$B/logs" "$B/products_hpss.sh" "$B/products-hpss" -type f -not -name "s1-products.tar" | sort ) > "$W/paths.list" || { echo "[H] STOP: find failed"; exit 3; }
  xargs -d '\n' sha256sum < "$W/paths.list" > "$W/ASSEMBLY-INVENTORY.sha256" || { echo "[H] STOP: hashing failed"; exit 3; }
  echo "[H] $(stamp) inventory: $(wc -l < "$W/ASSEMBLY-INVENTORY.sha256") files, $(xargs -d '\n' stat -c %s < "$W/paths.list" | awk '{s+=$1} END {print s}') bytes"
  tar -cf "$TAR" -T "$W/paths.list" || { echo "[H] STOP: tar failed"; exit 4; }
  [ "$(tar -tf "$TAR" | wc -l)" -eq "$(wc -l < "$W/paths.list")" ] || { echo "[H] STOP: tar member count differs"; exit 4; }
  echo "[H] tar members: $(tar -tf "$TAR" | wc -l)"
  sha256sum --quiet -c "$W/ASSEMBLY-INVENTORY.sha256" || { echo "[H] STOP: a file changed while taring"; exit 3; }
  sha256sum "$TAR" > "$TAR.sha256"; echo "[H] $(stamp) tar $(cat "$TAR.sha256") bytes=$(stat -c %s "$TAR")"
  hsi -q "mkdir -p $HDIR" || true
  hsi -q "put $TAR : $HDIR/s1-assembly.tar" || { echo "[H] STOP: hsi put failed"; exit 5; }
  hsi -q "hashcreate $HDIR/s1-assembly.tar" || { echo "[H] STOP: hashcreate failed"; exit 6; }
  hsi -q "put $TAR.sha256 : $HDIR/s1-assembly.tar.sha256" || { echo "[H] STOP: hsi put (sha) failed"; exit 5; }
  hsi -q "put $W/ASSEMBLY-INVENTORY.sha256 : $HDIR/ASSEMBLY-INVENTORY.sha256" || { echo "[H] STOP: hsi put (inventory) failed"; exit 5; }
  hsi -q "hashverify $HDIR/s1-assembly.tar" || { echo "[H] STOP: hashverify failed"; exit 6; }
  hsi -q "ls -l $HDIR"
  hsi -q "get $W/retrieve/s1-assembly.tar : $HDIR/s1-assembly.tar" || { echo "[H] STOP: hsi get failed"; exit 7; }
  a=$(cut -d' ' -f1 "$TAR.sha256"); b=$(sha256sum "$W/retrieve/s1-assembly.tar" | cut -d' ' -f1)
  echo "[H] retrieved sha256 $b"
  [ "$a" = "$b" ] || { echo "[H] STOP: retrieved copy differs"; exit 8; }
  rm -f "$W/retrieve/s1-assembly.tar" || { echo "[H] STOP: rm of retrieved copy failed"; exit 9; }
  echo "[H] $(stamp) PASS: HPSS copy verified by hashverify and by retrieval ($a)"
} 2>&1 | tee -a "$LOG"
exit "${PIPESTATUS[0]}"
