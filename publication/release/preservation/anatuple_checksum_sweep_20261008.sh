#!/usr/bin/env bash
# sha256 identity sweep of the analysed older-production AnaTuples (corrections record G4, option A; Joseph
# authorized the full sweep 2026-10-08). Run on a NERSC data-transfer node. It only READS the AnaTuples.
#
#   bash anatuple_checksum_sweep_20261008.sh <inventory.tsv> <outdir>      # resumable
#
# <inventory.tsv> is docs/publication/corrections-20261008/anatuple-inventory-20261008.tsv (header + rows of
# path-under-BASE, bytes, mtime_utc). For each file the size and mtime are checked against the inventory before
# AND after hashing; any difference is written to <outdir>/MISMATCH.tsv and the file gets no checksum. I/O is
# controlled: two concurrent streams (STREAMS), each under nice -n 19 and ionice idle class. A watchdog bounds each
# file: if its stat/hash does not finish in WATCHDOG_BASE + bytes/WATCHDOG_RATE seconds (Lustre objects on pscratch hung
# intermittently on 2026-10-09), the file goes to <outdir>/DEFERRED.tsv unhashed and the worker moves on; a later
# resume retries every file that is not yet hashed. SKIP=<file of paths> defers known-hung files without trying them.
set -euo pipefail
INV=$1; OUT=$2
BASE=${BASE:-/pscratch/sd/j/josephrb/minerva/minerva_large_files}   # overridable for tests only
STREAMS=${STREAMS:-2}
WATCHDOG_BASE=${WATCHDOG_BASE:-600}      # seconds allowed per file, plus
WATCHDOG_RATE=${WATCHDOG_RATE:-50000000} # one second per 50 MB (a 21 GB file gets about 17 min; the measured rate is ~1 GB/s)
mkdir -p "$OUT"
touch "$OUT/SHA256.part" "$OUT/MISMATCH.tsv" "$OUT/DEFERRED.tsv"

one() {  # one inventory row -> one line in SHA256.part, MISMATCH.tsv or DEFERRED.tsv
  local rel=$1 bytes=$2 mtime=$3 tmp pid limit waited=0
  tmp=$(mktemp "$OUT/.w.XXXXXX")
  (  # the stat/hash work runs in a child so a hung Lustre object cannot stall this worker (watchdog below)
    f="$BASE/$rel"
    s0=$(stat -c %s "$f"); m0=$(TZ=UTC date -u -d @"$(stat -c %Y "$f")" +%Y-%m-%dT%H:%M:%SZ)
    if [ "$s0" != "$bytes" ] || [ "$m0" != "$mtime" ]; then
      printf 'M\t%s\tbefore\t%s\t%s\t%s\t%s\n' "$rel" "$bytes" "$s0" "$mtime" "$m0" > "$tmp.res"; exit 0
    fi
    h=$(nice -n 19 ionice -c3 sha256sum "$f" | cut -d' ' -f1)
    s1=$(stat -c %s "$f"); m1=$(TZ=UTC date -u -d @"$(stat -c %Y "$f")" +%Y-%m-%dT%H:%M:%SZ)
    if [ "$s1" != "$s0" ] || [ "$m1" != "$m0" ]; then
      printf 'M\t%s\tduring\t%s\t%s\t%s\t%s\n' "$rel" "$s0" "$s1" "$m0" "$m1" > "$tmp.res"; exit 0
    fi
    printf 'H\t%s\t%s\t%s\t%s\n' "$h" "$bytes" "$mtime" "$rel" > "$tmp.res"
  ) &
  pid=$!
  limit=$((WATCHDOG_BASE + bytes / WATCHDOG_RATE))   # seconds: a generous floor rate per file
  while kill -0 "$pid" 2>/dev/null; do
    sleep 5; waited=$((waited + 5))
    if [ "$waited" -ge "$limit" ]; then
      printf '%s\t%s\t%s\ttimeout_%ss\n' "$rel" "$bytes" "$mtime" "$waited" >> "$OUT/DEFERRED.tsv"
      return 0   # the hung child is left behind (uninterruptible I/O); its late result is ignored
    fi
  done
  if [ -s "$tmp.res" ]; then
    case "$(cut -c1 "$tmp.res")" in
      H) cut -f2- "$tmp.res" >> "$OUT/SHA256.part" ;;
      M) cut -f2- "$tmp.res" >> "$OUT/MISMATCH.tsv" ;;
    esac
  else
    printf '%s\t%s\t%s\tno_result\n' "$rel" "$bytes" "$mtime" >> "$OUT/DEFERRED.tsv"
  fi
  rm -f "$tmp" "$tmp.res"
}
export -f one; export BASE OUT WATCHDOG_BASE WATCHDOG_RATE

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
echo "end $(date -u +%Y-%m-%dT%H:%M:%SZ): $(($(wc -l < "$OUT/ANATUPLE-SHA256.tsv") - 1)) hashed, $(wc -l < "$OUT/MISMATCH.tsv") mismatches, $(wc -l < "$OUT/DEFERRED.tsv") deferral records"
