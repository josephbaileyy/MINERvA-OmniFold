#!/bin/bash
#SBATCH -q xfer
#SBATCH -A m3246
#SBATCH -t 48:00:00
#SBATCH -J p3f-hpss-to-cfs
#SBATCH -o /global/cfs/cdirs/m3246/josephrb/p3f-move-20260818/logs/move_%j.out
#SBATCH -e /global/cfs/cdirs/m3246/josephrb/p3f-move-20260818/logs/move_%j.err

# COPY + VERIFY ONLY. This script never deletes from HPSS.
# Verification is against the md5s HPSS stored at write time (240/240 present),
# i.e. an independent pre-existing digest, not one computed from the copy.
set -uo pipefail

SRC=mnv-p3f-pet-fullevent-final
BASE=/global/cfs/cdirs/m3246/josephrb
DEST=$BASE/mnv-p3f-pet-fullevent-final
WORK=$BASE/p3f-move-20260818
OKDIR=$WORK/verified
CHUNK=6                      # hsi segfaults above ~36 path args; 6 is the repo's rule

mkdir -p "$DEST" "$OKDIR" "$WORK/logs"
cd "$WORK" || exit 1

mapfile -t ALL < "$WORK/p3f_files.txt"
echo "[$(date -u +%FT%TZ)] start: ${#ALL[@]} files declared"

# Resume guard validates COMPLETENESS (a verified-md5 marker), never existence (BEN-023).
TODO=()
for f in "${ALL[@]}"; do
  [[ -f "$OKDIR/$f.ok" ]] || TODO+=("$f")
done
echo "[$(date -u +%FT%TZ)] ${#TODO[@]} files still to fetch; $(( ${#ALL[@]} - ${#TODO[@]} )) already verified"

fetch_and_verify() {
  local -a batch=("$@")
  local f
  # a partial fetch must not look complete: pull into a staging dir, rename on verify
  local stage="$WORK/stage.$$"
  mkdir -p "$stage"
  hsi -q "lcd $stage; cd $SRC; mget ${batch[*]}" >> "$WORK/logs/hsi.log" 2>&1
  for f in "${batch[@]}"; do
    if [[ ! -f "$stage/$f" ]]; then
      echo "MISSING_AFTER_GET $f"; continue
    fi
    local want got
    want=$(awk -v n="$f" '$2==n{print $1}' "$WORK/p3f_md5.txt")
    got=$(md5sum "$stage/$f" | awk '{print $1}')
    if [[ -n "$want" && "$want" == "$got" ]]; then
      mv -f "$stage/$f" "$DEST/$f" && touch "$OKDIR/$f.ok"
      echo "OK $f $got"
    else
      echo "MISMATCH $f want=${want:-NONE} got=$got"
      rm -f "$stage/$f"
    fi
  done
  rmdir "$stage" 2>/dev/null
}

for (( i=0; i<${#TODO[@]}; i+=CHUNK )); do
  fetch_and_verify "${TODO[@]:i:CHUNK}"
  echo "[$(date -u +%FT%TZ)] progress: $(ls -1 "$OKDIR" | wc -l)/${#ALL[@]} verified"
done

NOK=$(ls -1 "$OKDIR" | wc -l)
echo "[$(date -u +%FT%TZ)] done: $NOK/${#ALL[@]} verified against stored HPSS md5s"
if [[ "$NOK" -eq "${#ALL[@]}" ]]; then
  echo "RESULT COPY_VERIFY_COMPLETE_PASS"
else
  echo "RESULT COPY_VERIFY_INCOMPLETE — rerun this same script to resume"
fi
echo "NOTE: nothing has been removed from HPSS. Deletion is a separate, authorized step."
