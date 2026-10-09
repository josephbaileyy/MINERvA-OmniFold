#!/usr/bin/env bash
# Addition to the PRD release-audit preservation (2026-10-08, Joseph's follow-up authorization): the W2 recoil-scale
# event-loop, lateral and merged outputs (about 32 GB) that the first pass excluded, plus the two small W2 directories
# it missed (tables, unfold-run). Same method and destination as preserve_prd_evidence_20261008.sh, with its own
# inventory, checksum list and receipt (W2-*). Run on a NERSC data-transfer node (dtn01.nersc.gov), which mounts both file systems.
#
#   bash preserve_w2_outputs_20261008.sh inventory   # hash every source file -> $DEST/W2-SOURCE-INVENTORY.tsv
#   bash preserve_w2_outputs_20261008.sh copy        # rsync -a the inventoried files (sources are only read)
#   bash preserve_w2_outputs_20261008.sh verify      # re-hash every destination file against the inventory
#
# The RC4 tarball is copied separately from the publication session's local scratchpad with scp (see README.md).
# Nothing is moved or deleted; the sources stay where they are. Symlinks are recorded in SYMLINKS.tsv (link, target,
# resolved path), not copied; the inventory refuses unless every resolved target is itself preserved.
set -euo pipefail

P=/pscratch/sd/j/josephrb
M=$P/MINERvA-OmniFold
DEST=/global/cfs/cdirs/m3246/josephrb/prd-release-preservation-20261008

# The exact source set (directories taken whole).
SOURCES=(
  "$P/w2-recoil-20261006/w2b/evloop"
  "$P/w2-recoil-20261006/w2b/lateral"
  "$P/w2-recoil-20261006/w2b/merged"
  "$P/w2-recoil-20261006/w2b/tables"
  "$P/w2-recoil-20261006/w2b/unfold-run"
)

list_files() {  # absolute paths of every regular file in the source set, sorted
  local s
  for s in "${SOURCES[@]}"; do
    [ -e "$s" ] || { echo "MISSING SOURCE $s" >&2; exit 3; }
    find "$s" -type f
  done | LC_ALL=C sort
}

list_links() {  # every symlink: link<TAB>target<TAB>resolved. Links are recorded, not copied; each resolved target
  local s l t r    # must itself be a preserved regular file or directory, else the inventory refuses.
  for s in "${SOURCES[@]}"; do
    find "$s" -type l | LC_ALL=C sort | while IFS= read -r l; do
      t=$(readlink "$l"); r=$(readlink -f "$l"); r=${r/#\/global\/pscratch//pscratch}  # DTN mounts /pscratch via /global
      printf '%s\t%s\t%s\n' "$l" "$t" "$r"
    done
  done
}

case "${1:-}" in
  inventory)
    mkdir -p "$DEST"
    [ ! -e "$DEST/W2-SOURCE-INVENTORY.tsv" ] || { echo "inventory exists; refusing to overwrite" >&2; exit 5; }
    list_files > "$DEST/.w2-files.txt"
    list_links > "$DEST/W2-SYMLINKS.tsv"
    while IFS=$'\t' read -r l t r; do
      if [ -f "$r" ]; then grep -qxF "$r" "$DEST/.w2-files.txt" || { echo "link target not preserved: $l -> $r" >&2; exit 4; }
      elif [ -d "$r" ]; then grep -qF "$r/" "$DEST/.w2-files.txt" || { echo "link target dir not preserved: $l -> $r" >&2; exit 4; }
      else echo "dangling link: $l -> $t" >&2; exit 4; fi
    done < "$DEST/W2-SYMLINKS.tsv"
    printf 'sha256\tbytes\tmtime_utc\tsource_path\n' > "$DEST/W2-SOURCE-INVENTORY.tsv.part"
    while IFS= read -r f; do
      printf '%s\t%s\t%s\t%s\n' "$(sha256sum "$f" | cut -d' ' -f1)" "$(stat -c %s "$f")" \
        "$(date -u -d @"$(stat -c %Y "$f")" +%Y-%m-%dT%H:%M:%SZ)" "$f"
    done < "$DEST/.w2-files.txt" >> "$DEST/W2-SOURCE-INVENTORY.tsv.part"
    mv "$DEST/W2-SOURCE-INVENTORY.tsv.part" "$DEST/W2-SOURCE-INVENTORY.tsv"
    echo "inventory: $(($(wc -l < "$DEST/W2-SOURCE-INVENTORY.tsv") - 1)) files, $(awk -F'\t' 'NR>1{s+=$2} END{print s}' "$DEST/W2-SOURCE-INVENTORY.tsv") bytes"
    ;;
  copy)
    # Every file lands at DEST/<absolute source path without the leading slash>. On the DTN /pscratch is a symlink to
    # /global/pscratch and rsync's sender refuses a symlinked path component ("Too many levels of symbolic links"),
    # so the transfer root is /global/ and the listed paths start at pscratch/.
    tail -n +2 "$DEST/W2-SOURCE-INVENTORY.tsv" | cut -f4 | sed 's#^/##' > "$DEST/.w2-rel.txt"
    rsync -a --files-from="$DEST/.w2-rel.txt" /global/ "$DEST/"
    echo "copy: rsync rc 0"
    ;;
  verify)
    tail -n +2 "$DEST/W2-SOURCE-INVENTORY.tsv" | awk -F'\t' '{sub("^/","",$4); print $1"  "$4}' > "$DEST/W2-SHA256SUMS"
    ( cd "$DEST" && sha256sum --quiet -c W2-SHA256SUMS ) && echo "verify: all $(wc -l < "$DEST/W2-SHA256SUMS") destination files match the source inventory"
    ;;
  *) echo "usage: $0 inventory|copy|verify" >&2; exit 2 ;;
esac
