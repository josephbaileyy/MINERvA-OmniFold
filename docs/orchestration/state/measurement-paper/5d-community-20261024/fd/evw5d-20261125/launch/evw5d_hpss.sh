#!/bin/bash
# EVW5D: the HPSS copy, on a Perlmutter login node, after the post. GENCMP E2's pattern
# (fd/gencmp-e2/rerun1/receipts/x_e2_hpss.sh), with an acceptance gate. Arguments: $1 the private /dev/shm copy of this
# script (deleted at exit), $2 the bound sha256 of $OUT/evw5d/SHA256SUMS (taken from the post and recorded in the
# director's binding of this step). It archives only when:
#   - $OUT and $OUT/evw5d are real directories reached through no link;
#   - SHA256SUMS's digest is the bound one, and evw5d.accepted(out, bound) is true, run from the tool clone in the
#     deploy's environment (the same consumer check as the fetch);
# and then archives exactly the verified set: the products SHA256SUMS lists, SHA256SUMS and evw5d.done, and nothing
# else (the listing must equal it). htar with CRC verify, hsi hashcreate/hashverify, and a retrieval of EVERY archived
# file to a private /dev/shm directory, each compared with its PINNED digest (SHA256SUMS's, or the bound one, or
# evw5d.done's as read before archiving). Receipts under $OUT/hpss, tarred to $OUT/hpss.tar.gz. Nothing on CFS.
SELF=$1; BOUND=$2
P=/pscratch/sd/j/josephrb; R=evw5d-20261125; OUT=$P/$R; E=$OUT/evw5d
H=/home/j/josephrb/mnv-evw5d-20261125; TAR=$H/evw5d-20261125.tar
O=$OUT/hpss
set -o noclobber
export LC_ALL=C
bail() { echo "STOP: $*"; rm -f -- "$SELF"; exit 9; }
case "$BOUND" in [0-9a-f]*) [ ${#BOUND} -eq 64 ] || bail "the bound digest is not 64 hex";; *) bail "no bound digest";; esac
for d in "$OUT" "$E"; do
  [ -d "$d" ] && [ ! -L "$d" ] && [ "$(cd "$d" && pwd -P)" = "$d" ] || bail "$d is not a real directory"
done
for f in "$O" "$OUT/hpss.tar.gz"; do [ ! -e "$f" ] && [ ! -L "$f" ] || bail "$f exists"; done
[ "$(sha256sum "$E/SHA256SUMS" | cut -d' ' -f1)" = "$BOUND" ] || bail "SHA256SUMS is not the bound one"
mkdir "$O" || bail "mkdir"
exec > "$O/hpss.log" 2>&1
umask 077
echo "node $(hostname) $(date -u +%FT%TZ) hpss sha256 $(sha256sum "$SELF" | cut -d' ' -f1) bound $BOUND"
cp "$SELF" "$O/evw5d_hpss.sh"
acc=$( set +o noclobber; source "$OUT/deploy/setup_salloc_env.sh" > "$O/env.log" 2>&1 || exit 96
       PYTHONDONTWRITEBYTECODE=1 python3 -B -c "import sys; sys.path.insert(0, '$OUT/toolclone/nd-unfolding/evw5d')
import evw5d; ok = evw5d.accepted('$E', '$BOUND'); print('ACCEPTED' if ok else 'REFUSED'); sys.exit(0 if ok else 1)" )
arc=$?; echo "accepted(): $acc rc=$arc"
[ "$arc" -eq 0 ] && [ "$acc" = ACCEPTED ] || bail "evw5d.accepted() refused the products (rc $arc)"
# the exact verified set, with each file's pinned digest
done_sha=$(sha256sum "$E/evw5d.done" | cut -d' ' -f1)
{ sed 's|^\([0-9a-f]\{64\}\)  |\1  '"$R"'/evw5d/|' "$E/SHA256SUMS"
  echo "$BOUND  $R/evw5d/SHA256SUMS"; echo "$done_sha  $R/evw5d/evw5d.done"; } | sort -k2 > "$O/pinned.sha256"
cut -c67- "$O/pinned.sha256" > "$O/htar_files.txt"
( cd "$P" && find "$R/evw5d" \( -type f -o -type l \) | sort ) > "$O/listing.txt"
cmp -s "$O/htar_files.txt" "$O/listing.txt" || bail "the directory holds files outside the verified set"
echo "files: $(wc -l < "$O/htar_files.txt")"; cat "$O/pinned.sha256"
hpssquota > "$O/quota-before.txt" 2>&1
cd "$P" || bail "cd"
hsi -q "mkdir -p $H" 2>&1
hsi -q "ls $TAR" > /dev/null 2>&1 && bail "$TAR exists"
htar -Hcrc -Hverify=1 -cvf "$TAR" -L "$O/htar_files.txt" > "$O/htar.log" 2>&1; r=$?; echo "htar rc=$r"; tail -3 "$O/htar.log"
[ $r = 0 ] || bail "htar rc $r"
hsi -q "hashcreate $TAR" > "$O/hashcreate.log" 2>&1; hc=$?; echo "hashcreate rc=$hc"
hsi -q "hashverify $TAR" > "$O/hashverify.log" 2>&1; hv=$?; echo "hashverify rc=$hv"; cat "$O/hashverify.log"
hsi -q "ls -l $TAR ${TAR}.idx" 2>&1 | tail -2
T=$(mktemp -d /dev/shm/jrb-evw5d-retrieve.XXXXXX) || bail "mktemp"
cd "$T" || bail "cd $T"
bad=0
n=0
while read -r want f; do
  htar -xf "$TAR" "$f" < /dev/null > /dev/null 2>&1
  n=$((n + 1))
  got=$(sha256sum "$T/$f" 2>/dev/null | cut -c1-64)
  if [ -n "$got" ] && [ "$got" = "$want" ]; then echo "retrieved equal to its pin: $f $got"; else echo "RETRIEVE MISMATCH: $f"; bad=1; fi
  rm -f "$T/$f"
done < "$O/pinned.sha256" > "$O/retrieve.log" 2>&1
cat "$O/retrieve.log"; cd /; rm -rf "$T"
nf=$(wc -l < "$O/pinned.sha256"); ne=$(grep -c '^retrieved equal to its pin: ' "$O/retrieve.log")
echo "retrieved and equal: $ne of $nf"
[ "$ne" -eq "$nf" ] || bad=1
[ "$hv" -eq 0 ] && [ "$hc" -eq 0 ] || bad=1
hpssquota > "$O/quota-after.txt" 2>&1
grep "HPSS" "$O/quota-before.txt" "$O/quota-after.txt"
echo "hpss rc=$bad $(date -u +%FT%TZ)"
tar czf "$OUT/hpss.tar.gz" -C "$OUT" hpss
rm -f -- "$SELF"
exit $bad
