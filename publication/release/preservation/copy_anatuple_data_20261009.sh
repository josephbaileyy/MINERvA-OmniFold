#!/usr/bin/env bash
# Durable CFS copy of the analysed older-production data AnaTuples and their flux/parameter files (corrections record
# G4; Joseph approved the copy 2026-10-09, within his 3 TB CFS rule). The simulation AnaTuples (10.5 TB) are NOT
# copied. Run on a NERSC data-transfer node (dtn01.nersc.gov), which mounts both file systems.
#
#   bash copy_anatuple_data_20261009.sh list     # select the files from the committed checksum manifest
#   bash copy_anatuple_data_20261009.sh copy     # rsync -a them (the sources are only read)
#   bash copy_anatuple_data_20261009.sh verify   # re-hash every destination file against the manifest
#
#   bash copy_anatuple_data_20261009.sh add-list YYYYMMDD     # files hashed since an earlier list (2026-10-10:
#   bash copy_anatuple_data_20261009.sh add-copy YYYYMMDD     #   the 6 OST-61 data files) go to a separate list,
#   bash copy_anatuple_data_20261009.sh add-verify YYYYMMDD   #   DATA-SHA256SUMS-ADD-YYYYMMDD; earlier lists stay as made
#
# The file set is every row of ANATUPLE-SHA256.tsv under Data/, MATFluxAndReweightFiles/ or MParamFiles/. A file
# without a checksum is therefore never touched; that excludes the 6 data files whose pscratch objects hang (OST 61,
# follow-up record section 3a), which a later run can add once they are hashed. Nothing is moved or deleted.
set -euo pipefail
export LC_ALL=C

HERE=$(cd "$(dirname "$0")" && pwd)
MANIFEST=${MANIFEST:-$HERE/ANATUPLE-SHA256.tsv}   # a copy of anatuple-checksums/ANATUPLE-SHA256.tsv beside this script
# On the DTN /pscratch is a symlink to /global/pscratch, and rsync's sender refuses a symlinked path component.
SRC=${SRC:-/global/pscratch/sd/j/josephrb/minerva/minerva_large_files}                                  # overridable
DEST=${DEST:-/global/cfs/cdirs/m3246/josephrb/prd-release-preservation-20261008/anatuple-data-20261009}  # for tests only
WANT='^(Data|MATFluxAndReweightFiles|MParamFiles)/'

check_header() {
  head -1 "$MANIFEST" | grep -q $'^sha256\tbytes\tmtime_utc\tpath_under_/pscratch/sd/j/josephrb/minerva/minerva_large_files$' \
    || { echo "unexpected manifest header" >&2; exit 4; }
}
ADD=$DEST/DATA-SHA256SUMS-ADD-${2:-}

case "${1:-}" in
  list)
    [ ! -e "$DEST/DATA-SHA256SUMS" ] || { echo "list exists; refusing to overwrite" >&2; exit 5; }
    mkdir -p "$DEST"
    check_header
    tail -n +2 "$MANIFEST" | awk -F'\t' -v w="$WANT" '$4 ~ w' > "$DEST/.data-rows.tsv"
    awk -F'\t' '$1 !~ /^[0-9a-f]{64}$/ {bad=1} END {exit bad}' "$DEST/.data-rows.tsv" \
      || { echo "a selected row has no valid sha256" >&2; exit 4; }
    cut -f4 "$DEST/.data-rows.tsv" > "$DEST/.data-rel.txt"
    awk -F'\t' '{print $1"  "$4}' "$DEST/.data-rows.tsv" > "$DEST/DATA-SHA256SUMS"
    echo "list: $(wc -l < "$DEST/.data-rel.txt") files, $(awk -F'\t' '{s+=$2} END{print s}' "$DEST/.data-rows.tsv") bytes"
    ;;
  copy)
    # size + mtime are preserved (-a); a file whose size or mtime no longer matches the manifest is caught by verify
    nice -n 19 ionice -c3 rsync -a --files-from="$DEST/.data-rel.txt" "$SRC/" "$DEST/"
    echo "copy: rsync rc 0"
    ;;
  verify)
    ( cd "$DEST" && nice -n 19 ionice -c3 sha256sum --quiet --strict -c DATA-SHA256SUMS ) \
      && echo "verify: all $(wc -l < "$DEST/DATA-SHA256SUMS") destination files match the checksum manifest"
    ;;
  add-list)
    [[ ${2:-} =~ ^[0-9]{8}$ ]] || { echo "usage: $0 add-list YYYYMMDD" >&2; exit 2; }
    [ -s "$DEST/DATA-SHA256SUMS" ] || { echo "no earlier list in $DEST" >&2; exit 4; }
    [ ! -e "$ADD" ] || { echo "$ADD exists; refusing to overwrite" >&2; exit 5; }
    check_header
    shopt -s nullglob; lists=("$DEST"/DATA-SHA256SUMS "$DEST"/DATA-SHA256SUMS-ADD-*); shopt -u nullglob
    # every row of an earlier list must still be in the manifest, digest and path unchanged
    tail -n +2 "$MANIFEST" | awk -F'\t' '{print $1"  "$4}' | sort > "$DEST/.add-$2-manifest-sums"
    sort "${lists[@]}" | comm -23 - "$DEST/.add-$2-manifest-sums" > "$DEST/.add-$2-drift"
    [ ! -s "$DEST/.add-$2-drift" ] || { echo "an earlier list row is not in the manifest: $DEST/.add-$2-drift" >&2; exit 4; }
    cut -c67- "${lists[@]}" > "$DEST/.add-$2-listed.txt"   # the path, after 64 hex digits and two spaces
    tail -n +2 "$MANIFEST" | awk -F'\t' -v w="$WANT" '$4 ~ w' \
      | awk -F'\t' 'NR==FNR {listed[$0]=1; next} !($4 in listed)' "$DEST/.add-$2-listed.txt" - > "$DEST/.add-$2-rows.tsv"
    [ -s "$DEST/.add-$2-rows.tsv" ] || { echo "nothing to add: every selected manifest row is already listed" >&2; exit 6; }
    awk -F'\t' '$1 !~ /^[0-9a-f]{64}$/ {bad=1} END {exit bad}' "$DEST/.add-$2-rows.tsv" \
      || { echo "a selected row has no valid sha256" >&2; exit 4; }
    cut -f4 "$DEST/.add-$2-rows.tsv" > "$DEST/.add-$2-rel.txt"
    awk -F'\t' '{print $1"  "$4}' "$DEST/.add-$2-rows.tsv" > "$ADD"
    echo "add-list: $(wc -l < "$DEST/.add-$2-rel.txt") files, $(awk -F'\t' '{s+=$2} END{print s}' "$DEST/.add-$2-rows.tsv") bytes -> $ADD"
    ;;
  add-copy)
    [ -s "$ADD" ] || { echo "usage: $0 add-copy YYYYMMDD (after add-list)" >&2; exit 2; }
    nice -n 19 ionice -c3 rsync -a --files-from="$DEST/.add-$2-rel.txt" "$SRC/" "$DEST/"
    echo "add-copy: rsync rc 0"
    ;;
  add-verify)
    [ -s "$ADD" ] || { echo "usage: $0 add-verify YYYYMMDD (after add-list)" >&2; exit 2; }
    ( cd "$DEST" && nice -n 19 ionice -c3 sha256sum --quiet --strict -c "$(basename "$ADD")" ) \
      && echo "add-verify: all $(wc -l < "$ADD") added destination files match the checksum manifest"
    ;;
  *) echo "usage: $0 list|copy|verify|add-list|add-copy|add-verify" >&2; exit 2 ;;
esac
