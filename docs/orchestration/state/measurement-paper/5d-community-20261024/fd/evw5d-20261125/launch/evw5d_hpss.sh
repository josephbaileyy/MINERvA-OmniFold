#!/bin/bash
# EVW5D: the HPSS copy, on a Perlmutter login node, after the post and only for a PASS done marker. GENCMP E2's pattern
# (fd/gencmp-e2/rerun1/receipts/x_e2_hpss.sh): an explicit list (the evw5d products, SHA256SUMS and evw5d.done; no
# clone), htar's CRC verify, hsi hashcreate/hashverify, and a retrieval of EVERY listed file to /dev/shm, each
# compared by sha256 with its scratch copy. Receipts under $OUT/hpss, tarred to $OUT/hpss.tar.gz. Nothing on CFS.
# Launched from a /dev/shm copy of itself, whose path is $1; it deletes that copy at exit.
SELF=$1
P=/pscratch/sd/j/josephrb; R=evw5d-20261125; OUT=$P/$R
H=/home/j/josephrb/mnv-evw5d-20261125; TAR=$H/evw5d-20261125.tar
O=$OUT/hpss
bail() { echo "STOP: $*"; rm -f -- "$SELF"; exit 9; }
[ -e "$O" ] && bail "$O exists"
grep -q '"verdict": "PASS"' "$OUT/evw5d/evw5d.done" 2>/dev/null || bail "no PASS done marker"
mkdir -p "$O" || bail "mkdir"
exec > "$O/hpss.log" 2>&1
umask 077
echo "node $(hostname) $(date -u +%FT%TZ) hpss sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$O/evw5d_hpss.sh"
( cd "$OUT/evw5d" && sha256sum -c SHA256SUMS ) || bail "the products do not match SHA256SUMS"
hpssquota > "$O/quota-before.txt" 2>&1
cd "$P" || bail "cd"
find "$R/evw5d" -type f | sort > "$O/htar_files.txt"
echo "files: $(wc -l < "$O/htar_files.txt")"; cat "$O/htar_files.txt"
hsi -q "mkdir -p $H" 2>&1
hsi -q "ls $TAR" > /dev/null 2>&1 && bail "$TAR exists"
htar -Hcrc -Hverify=1 -cvf "$TAR" -L "$O/htar_files.txt" > "$O/htar.log" 2>&1; r=$?; echo "htar rc=$r"; tail -3 "$O/htar.log"
[ $r = 0 ] || bail "htar rc $r"
hsi -q "hashcreate $TAR" > "$O/hashcreate.log" 2>&1; echo "hashcreate rc=$?"
hsi -q "hashverify $TAR" > "$O/hashverify.log" 2>&1; echo "hashverify rc=$?"; cat "$O/hashverify.log"
hsi -q "ls -l $TAR ${TAR}.idx" 2>&1 | tail -2
T=/dev/shm/jrb-evw5d-retrieve.$$; rm -rf "$T"; mkdir -p "$T"; cd "$T" || bail "cd $T"
bad=0
while read -r f; do
  htar -xf "$TAR" "$f" > /dev/null 2>&1
  a=$(sha256sum "$T/$f" 2>/dev/null | cut -c1-64); b=$(sha256sum "$P/$f" | cut -c1-64)
  if [ -n "$a" ] && [ "$a" = "$b" ]; then echo "retrieved equal: $f $a"; else echo "RETRIEVE MISMATCH: $f"; bad=1; fi
  rm -f "$T/$f"
done < "$O/htar_files.txt" > "$O/retrieve.log" 2>&1
cat "$O/retrieve.log"; cd /; rm -rf "$T"
hpssquota > "$O/quota-after.txt" 2>&1
grep "HPSS" "$O/quota-before.txt" "$O/quota-after.txt"
echo "hpss rc=$bad $(date -u +%FT%TZ)"
tar czf "$OUT/hpss.tar.gz" -C "$OUT" hpss
rm -f -- "$SELF"
exit $bad
