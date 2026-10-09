#!/usr/bin/env bash
# sha256 identity sweep of the analysed older-production AnaTuples (corrections record G4, option A; Joseph
# authorized the full sweep 2026-10-08). Run on a NERSC data-transfer node. It only READS the AnaTuples.
#
#   bash anatuple_checksum_sweep_20261008.sh <inventory.tsv> <outdir>      # resumable
#
# <inventory.tsv> is docs/publication/corrections-20261008/anatuple-inventory-20261008.tsv (header + rows of
# path-under-BASE, bytes, mtime_utc). For each file the size and mtime are checked against the inventory before
# AND after hashing; any difference is written to <outdir>/MISMATCH.tsv and the file gets no checksum. I/O is
# controlled: two concurrent streams (STREAMS), each under nice -n 19 and ionice idle class. SKIP=<file of paths>
# defers those files (e.g. ones whose Lustre object is hung); they stay unhashed until a later resume without SKIP.
set -euo pipefail
INV=$1; OUT=$2
BASE=/pscratch/sd/j/josephrb/minerva/minerva_large_files
STREAMS=${STREAMS:-2}
mkdir -p "$OUT"
touch "$OUT/SHA256.part" "$OUT/MISMATCH.tsv"

one() {  # one inventory row -> one line in SHA256.part, or one in MISMATCH.tsv
  local rel=$1 bytes=$2 mtime=$3 f s0 m0 h s1 m1
  f="$BASE/$rel"
  s0=$(stat -c %s "$f"); m0=$(TZ=UTC date -u -d @"$(stat -c %Y "$f")" +%Y-%m-%dT%H:%M:%SZ)
  if [ "$s0" != "$bytes" ] || [ "$m0" != "$mtime" ]; then
    printf '%s\tbefore\t%s\t%s\t%s\t%s\n' "$rel" "$bytes" "$s0" "$mtime" "$m0" >> "$OUT/MISMATCH.tsv"; return 0
  fi
  h=$(nice -n 19 ionice -c3 sha256sum "$f" | cut -d' ' -f1)
  s1=$(stat -c %s "$f"); m1=$(TZ=UTC date -u -d @"$(stat -c %Y "$f")" +%Y-%m-%dT%H:%M:%SZ)
  if [ "$s1" != "$s0" ] || [ "$m1" != "$m0" ]; then
    printf '%s\tduring\t%s\t%s\t%s\t%s\n' "$rel" "$s0" "$s1" "$m0" "$m1" >> "$OUT/MISMATCH.tsv"; return 0
  fi
  printf '%s\t%s\t%s\t%s\n' "$h" "$bytes" "$mtime" "$rel" >> "$OUT/SHA256.part"
}
export -f one; export BASE OUT

# resume: skip rows already hashed
cut -f4 "$OUT/SHA256.part" | LC_ALL=C sort > "$OUT/.done"
tail -n +2 "$INV" | LC_ALL=C sort -t$'\t' -k1,1 | join -t$'\t' -v1 - "$OUT/.done" > "$OUT/.todo" || true
if [ -n "${SKIP:-}" ]; then
  LC_ALL=C sort "$SKIP" > "$OUT/.skip"
  join -t$'\t' -v1 "$OUT/.todo" "$OUT/.skip" > "$OUT/.todo2" && mv "$OUT/.todo2" "$OUT/.todo"
  echo "deferred: $(wc -l < "$OUT/.skip") file(s) listed in $SKIP"
fi
echo "start $(date -u +%Y-%m-%dT%H:%M:%SZ): $(wc -l < "$OUT/.todo") to hash, $(wc -l < "$OUT/.done") already done, $STREAMS streams"
tr '\t' '\n' < "$OUT/.todo" | xargs -r -d '\n' -n 3 -P "$STREAMS" bash -c 'one "$0" "$1" "$2"'
{ printf 'sha256\tbytes\tmtime_utc\tpath_under_%s\n' "$BASE"; LC_ALL=C sort -t$'\t' -k4,4 "$OUT/SHA256.part"; } > "$OUT/ANATUPLE-SHA256.tsv"
echo "end $(date -u +%Y-%m-%dT%H:%M:%SZ): $(($(wc -l < "$OUT/ANATUPLE-SHA256.tsv") - 1)) hashed, $(wc -l < "$OUT/MISMATCH.tsv") mismatches"
