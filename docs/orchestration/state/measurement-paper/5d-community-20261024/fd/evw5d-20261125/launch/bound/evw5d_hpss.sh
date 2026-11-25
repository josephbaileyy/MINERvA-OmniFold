#!/bin/bash
# EVW5D: the HPSS copy, on a Perlmutter login node, after the post. GENCMP E2's pattern
# (fd/gencmp-e2/rerun1/receipts/x_e2_hpss.sh), with an acceptance gate. Arguments: $1 the private /dev/shm copy of this
# script (deleted at exit), $2 the bound sha256 of $OUT/evw5d/SHA256SUMS (taken from the post and recorded in the
# director's binding of this step). It archives only when:
#   - $OUT and $OUT/evw5d are real directories reached through no link;
#   - the tool clone's evw5d.py (the checker) is the approved bytes;
#   - a private snapshot of SHA256SUMS and evw5d.done is taken; SHA256SUMS's digest is the bound one; and
#     evw5d.accepted(out, bound) is true, run in the deploy's environment (the same consumer check as the fetch).
# Every pin and the file list come from the snapshot: the products SHA256SUMS lists, SHA256SUMS and evw5d.done, and
# nothing else (the directory listing must equal it). htar with CRC verify and hsi hashcreate/hashverify; then the
# WHOLE archive is retrieved to a private /dev/shm directory, every file compared with its pin and the count with the
# list, and evw5d.accepted() run on the retrieved bundle; the scratch manifest and marker must still equal the
# snapshot. Any miss makes the exit 1. Receipts under $OUT/hpss, tarred to $OUT/hpss.tar.gz. Nothing on CFS.
SELF=$1; BOUND=$2
EVW_SHA=f6f5bbb5ea1c0c7a704dfcd64e1f214c587db1e64db3d9c9ae4e943ac01ad990
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
# the checker: the tool clone's evw5d.py must be the approved bytes (evw5d.py checks ess_capture.py's itself)
W=$OUT/toolclone/nd-unfolding/evw5d/evw5d.py
case "$EVW_SHA" in *__*) bail "the approved evw5d.py sha256 is not filled in";; esac
[ -f "$W" ] && [ ! -L "$W" ] && [ "$(sha256sum "$W" | cut -d' ' -f1)" = "$EVW_SHA" ] || bail "the checker is not the approved bytes"
# a private snapshot of the manifest and the marker: every pin and the file list come from it
mkdir "$O/snapshot" || bail "mkdir snapshot"
cp -p "$E/SHA256SUMS" "$E/evw5d.done" "$O/snapshot/" || bail "snapshot"
[ "$(sha256sum "$O/snapshot/SHA256SUMS" | cut -d' ' -f1)" = "$BOUND" ] || bail "the snapshot manifest is not the bound one"
done_sha=$(sha256sum "$O/snapshot/evw5d.done" | cut -d' ' -f1)
checker() {   # checker <bundle dir>: evw5d.accepted(dir, BOUND) in the deploy's environment
  ( set +o noclobber; source "$OUT/deploy/setup_salloc_env.sh" > "$O/env-$2.log" 2>&1 || exit 96
    PYTHONDONTWRITEBYTECODE=1 python3 -B -c "import sys; sys.path.insert(0, sys.argv[1]); import evw5d
ok = evw5d.accepted(sys.argv[2], sys.argv[3]); print('ACCEPTED' if ok else 'REFUSED'); sys.exit(0 if ok else 1)" \
      "$(dirname "$W")" "$1" "$BOUND" )
}
acc=$(checker "$E" scratch); arc=$?; echo "accepted() on scratch: $acc rc=$arc"
[ "$arc" -eq 0 ] && [ "$acc" = ACCEPTED ] || bail "evw5d.accepted() refused the products (rc $arc)"
[ "$(sha256sum "$E/evw5d.done" | cut -d' ' -f1)" = "$done_sha" ] || bail "the marker changed during the check"
{ sed 's|^\([0-9a-f]\{64\}\)  |\1  '"$R"'/evw5d/|' "$O/snapshot/SHA256SUMS"
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
htar -xf "$TAR" < /dev/null > "$O/retrieve-htar.log" 2>&1; xr=$?; echo "htar -xf rc=$xr"
bad=0; [ "$xr" -eq 0 ] || bad=1
( cd "$T" && sha256sum --strict -c "$O/pinned.sha256" ) > "$O/retrieve.log" 2>&1 || bad=1
cat "$O/retrieve.log"
nf=$(wc -l < "$O/pinned.sha256"); ne=$(grep -c ': OK$' "$O/retrieve.log"); nall=$(cd "$T" && find "$R" -type f | wc -l)
echo "retrieved and equal to their pins: $ne of $nf; files retrieved: $nall"
[ "$ne" -eq "$nf" ] && [ "$nall" -eq "$nf" ] || bad=1
racc=$(checker "$T/$R/evw5d" retrieved); rr=$?; echo "accepted() on the retrieved bundle: $racc rc=$rr"
[ "$rr" -eq 0 ] && [ "$racc" = ACCEPTED ] || bad=1
cd /; rm -rf -- "${T:?}"
[ "$hv" -eq 0 ] && [ "$hc" -eq 0 ] || bad=1
for f in SHA256SUMS evw5d.done; do
  cmp -s "$E/$f" "$O/snapshot/$f" || { echo "the scratch $f changed during the archive"; bad=1; }
done
hpssquota > "$O/quota-after.txt" 2>&1
grep "HPSS" "$O/quota-before.txt" "$O/quota-after.txt"
echo "hpss rc=$bad $(date -u +%FT%TZ)"
tar czf "$OUT/hpss.tar.gz" -C "$OUT" hpss
rm -f -- "$SELF"
exit $bad
