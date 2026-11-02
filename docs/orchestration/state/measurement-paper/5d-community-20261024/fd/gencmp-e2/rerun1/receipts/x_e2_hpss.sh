#!/bin/bash
# GENCMP E2 (addendum E2 section 5, E2-A1 section 6): both run directories, without their deploy clones, to HPSS with an
# explicit list, htar's CRC verify, hsi hashcreate/hashverify, and a retrieval check. Receipts under the rerun's hpss/.
P=/pscratch/sd/j/josephrb; R1=gencmp-e2-20261102; R2=gencmp-e2a1-20261102
H=/home/j/josephrb/mnv-gencmp-e2-20261102; TAR=$H/gencmp-e2-20261102.tar
O=$P/$R2/hpss
[ -e "$O" ] && { echo "STOP: $O exists"; exit 2; }
mkdir -p "$O" || exit 2
hpssquota > "$O/quota-before.txt" 2>&1
cd "$P" || exit 9
find "$R1" "$R2" \( -path "$R1/deploy" -o -path "$R2/deploy" -o -path "$R2/hpss" \) -prune -o -type f -print | sort > "$O/htar_files.txt"
echo "files: $(wc -l < "$O/htar_files.txt")"
hsi -q "mkdir -p $H" 2>&1
hsi -q "ls $TAR" > /dev/null 2>&1 && { echo "STOP: $TAR exists"; exit 2; }
htar -Hcrc -Hverify=1 -cvf "$TAR" -L "$O/htar_files.txt" > "$O/htar.log" 2>&1; echo "htar rc=$?"
tail -3 "$O/htar.log"
hsi -q "hashcreate $TAR" > "$O/hashcreate.log" 2>&1; echo "hashcreate rc=$?"
hsi -q "hashverify $TAR" > "$O/hashverify.log" 2>&1; echo "hashverify rc=$?"; cat "$O/hashverify.log"
hsi -q "ls -l $TAR ${TAR}.idx" 2>&1 | tail -2
T=/dev/shm/jrb-e2-retrieve; rm -rf "$T"; mkdir -p "$T"; cd "$T"
for f in "$R2/chi2/e2.json" "$R2/unfold/unfold.json" "$R2/unfold/L-5D-PV_e_nuwro_carbon_R2.npz" "$R1/logs/ratios.log" "$R2/prep_ch/L-5D-PV/gibuu.json"; do
  htar -xf "$TAR" "$f" > /dev/null 2>&1
  a=$(sha256sum "$T/$f" | cut -c1-64); b=$(sha256sum "$P/$f" | cut -c1-64)
  [ "$a" = "$b" ] && echo "retrieved equal: $f $a" || echo "RETRIEVE MISMATCH: $f"
done > "$O/retrieve.log" 2>&1
cat "$O/retrieve.log"; cd /; rm -rf "$T"
hpssquota > "$O/quota-after.txt" 2>&1
grep "HPSS" "$O/quota-before.txt" "$O/quota-after.txt"
