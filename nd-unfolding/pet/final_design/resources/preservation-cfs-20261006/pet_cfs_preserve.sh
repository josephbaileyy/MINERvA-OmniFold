#!/bin/bash
#SBATCH -q xfer
#SBATCH -A m3246
#SBATCH -t 48:00:00
#SBATCH -J pet-cfs-preserve
#SBATCH -o /global/cfs/cdirs/m3246/josephrb/pet-studies-20261006/_preserve/logs/preserve_%j.out
#SBATCH -e /global/cfs/cdirs/m3246/josephrb/pet-studies-20261006/_preserve/logs/preserve_%j.err

# COPY + VERIFY ONLY. This script never deletes or modifies anything on pscratch.
# Joseph's instruction (2026-10-06): preserve the PET studies on CFS (his rule: stay under 3 TB there).
# For each item listed in items.txt (a top-level name under $SRC):
#   1. a sha256 manifest of every regular file and a list of every symlink (path -> target), taken from the SOURCE
#      before the copy;
#   2. rsync -a into $DEST (symlinks are copied as links, byte-for-byte; nothing is dereferenced);
#   3. the same manifest and link list taken from the COPY, compared with the source's; an item is marked verified
#      only when both are identical and rsync exited 0.
# Resume guard: an item counts as done only through its verified marker, never because the copy exists.
set -uo pipefail
export LC_ALL=C

SRC=${PRESERVE_SRC:-/pscratch/sd/j/josephrb}                                   # overridable only for the self-test
DEST=${PRESERVE_DEST:-/global/cfs/cdirs/m3246/josephrb/pet-studies-20261006}
WORK=$DEST/_preserve
OK=$WORK/verified
mkdir -p "$OK" "$WORK/manifests" "$WORK/logs"

mapfile -t ITEMS < "$WORK/items.txt"
echo "[$(date -u +%FT%TZ)] start on $(hostname): ${#ITEMS[@]} items declared"

manifest() {   # manifest <root> <item> <out-prefix>
  local root=$1 item=$2 out=$3
  ( cd "$root" && find "$item" -type f -print0 | xargs -0 -r -P 8 -n 64 sha256sum ) | sort -k2 > "$out.sha256"
  local s1=${PIPESTATUS[0]}
  ( cd "$root" && find "$item" -type l -printf '%p\t%l\n' ) | sort > "$out.links"
  return "$s1"
}

for item in "${ITEMS[@]}"; do
  [[ -n "$item" ]] || continue
  if [[ -f "$OK/$item.ok" ]]; then echo "SKIP_VERIFIED $item"; continue; fi
  if [[ ! -e "$SRC/$item" ]]; then echo "MISSING_SOURCE $item"; continue; fi
  m=$WORK/manifests/$item
  manifest "$SRC" "$item" "$m.src" || { echo "SRC_MANIFEST_FAILED $item"; continue; }
  rsync -a "$SRC/$item" "$DEST/"
  rc=$?
  if [[ $rc -ne 0 ]]; then echo "RSYNC_FAILED $item rc=$rc"; continue; fi
  manifest "$DEST" "$item" "$m.dst" || { echo "DST_MANIFEST_FAILED $item"; continue; }
  nf=$(wc -l < "$m.src.sha256"); nl=$(wc -l < "$m.src.links")
  if cmp -s "$m.src.sha256" "$m.dst.sha256" && cmp -s "$m.src.links" "$m.dst.links"; then
    touch "$OK/$item.ok"
    echo "OK $item files=$nf links=$nl manifest=$(sha256sum < "$m.src.sha256" | cut -c1-16)"
  else
    echo "MISMATCH $item files=$nf links=$nl"
  fi
  echo "[$(date -u +%FT%TZ)] progress: $(ls -1 "$OK" | wc -l)/${#ITEMS[@]} verified"
done

NOK=$(ls -1 "$OK" | wc -l)
echo "[$(date -u +%FT%TZ)] done: $NOK/${#ITEMS[@]} verified"
if [[ "$NOK" -eq "${#ITEMS[@]}" ]]; then
  echo "RESULT COPY_VERIFY_COMPLETE_PASS"
else
  echo "RESULT COPY_VERIFY_INCOMPLETE (rerun this same script to resume)"
fi
du -sh "$DEST" 2>/dev/null | tail -1
echo "NOTE: nothing was removed from pscratch."
