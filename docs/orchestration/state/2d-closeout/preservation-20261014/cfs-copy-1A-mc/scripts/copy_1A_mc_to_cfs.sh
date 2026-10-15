#!/bin/bash
# Copy the 41 Playlist 1A MC AnaTuples (older processing, no longer public) from
# /pscratch to CFS, then verify every destination file by sha256 against
# ANATUPLE-SHA256.tsv (repo sha 913e004d...). Joseph approved 2026-10-14: "yes you can copy them".
set -o pipefail
W=/pscratch/sd/j/josephrb/tmp-1A-cfs-copy-20261014
SRC=/pscratch/sd/j/josephrb/minerva/minerva_large_files
DST=/global/cfs/cdirs/m3246/josephrb/mc-1A-preservation-20261014
cd "$W" || exit 3
date -u +%FT%TZ > start.txt
[ -e "$DST" ] && { echo "DST exists, refusing" > refused.txt; exit 4; }
mkdir -p "$DST/MC/StandardMC/Playlist1A"
cut -f4 1A_mc.sha256.tsv > relpaths.txt
# preserve mtimes; no deletion; source read-only
nice -n 19 ionice -c3 rsync -a --files-from=relpaths.txt "$SRC/" "$DST/" > rsync.out 2> rsync.err
echo "rsync_rc=$?" > rsync.rc
# verify: sha256 of destination bytes, sizes and mtimes
: > verify.tsv
while IFS=$'\t' read -r sha bytes mtime rel; do
  f="$DST/$rel"
  got=$(nice -n 19 ionice -c3 sha256sum "$f" | cut -d' ' -f1)
  b=$(stat -c %s "$f"); m=$(date -u -d @"$(stat -c %Y "$f")" +%FT%TZ)
  [ "$got" = "$sha" ] && [ "$b" = "$bytes" ] && [ "$m" = "$mtime" ] && v=OK || v=MISMATCH
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$v" "$got" "$b" "$m" "$rel" "$sha" >> verify.tsv
done < 1A_mc.sha256.tsv
echo "OK=$(grep -c '^OK' verify.tsv) MISMATCH=$(grep -c '^MISMATCH' verify.tsv)" > verify_summary.txt
du -s --block-size=1 "$DST" > dst_du.txt
chmod -R a-w "$DST"
date -u +%FT%TZ > done.txt
