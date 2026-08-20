#!/bin/bash
#SBATCH -q xfer
#SBATCH -A m3246
#SBATCH -t 24:00:00
#SBATCH -J p3f-hpss-delete
#SBATCH -o /global/cfs/cdirs/m3246/josephrb/p3f-move-20260818/logs/delete_%j.out
#SBATCH -e /global/cfs/cdirs/m3246/josephrb/p3f-move-20260818/logs/delete_%j.err

# RE-VERIFY THEN DELETE. Deletion runs ONLY on a 240/240 re-verify in this same job,
# so the last check precedes the irreversible step by seconds, not by a day.
set -uo pipefail

SRC=mnv-p3f-pet-fullevent-final
BASE=/global/cfs/cdirs/m3246/josephrb
DEST=$BASE/$SRC
WORK=$BASE/p3f-move-20260818
CHUNK=6
Q=/global/common/software/nersc/bin/hpssquota

cd "$WORK" || exit 1
mapfile -t ALL < "$WORK/p3f_files.txt"
N=${#ALL[@]}
echo "[$(date -u +%FT%TZ)] re-verifying $N CFS objects against stored HPSS md5s"

echo "=== hpssquota BEFORE ==="; $Q -u "$USER" 2>&1

PASS=0; FAIL=0
: > "$WORK/reverify.txt"
for f in "${ALL[@]}"; do
  if [[ ! -f "$DEST/$f" ]]; then echo "ABSENT $f" >> "$WORK/reverify.txt"; ((FAIL++)); continue; fi
  want=$(awk -v n="$f" '$2==n{print $1}' "$WORK/p3f_md5.txt")
  got=$(md5sum "$DEST/$f" | awk '{print $1}')
  if [[ -n "$want" && "$want" == "$got" ]]; then
    echo "OK $f $got" >> "$WORK/reverify.txt"; ((PASS++))
  else
    echo "MISMATCH $f want=${want:-NONE} got=$got" >> "$WORK/reverify.txt"; ((FAIL++))
  fi
done
echo "[$(date -u +%FT%TZ)] re-verify: PASS=$PASS FAIL=$FAIL of $N"

if [[ "$PASS" -ne "$N" || "$FAIL" -ne 0 ]]; then
  echo "RESULT REVERIFY_FAILED — NOTHING DELETED. See $WORK/reverify.txt"
  exit 1
fi
echo "[$(date -u +%FT%TZ)] re-verify complete: $N/$N. Proceeding to HPSS deletion."

DEL=0
for (( i=0; i<N; i+=CHUNK )); do
  batch=("${ALL[@]:i:CHUNK}")
  hsi -q "cd $SRC; rm ${batch[*]}" >> "$WORK/logs/hsi_delete.log" 2>&1
  DEL=$((DEL+${#batch[@]}))
  echo "[$(date -u +%FT%TZ)] deletion issued for $DEL/$N"
done

echo "=== HPSS residual listing (expect empty) ==="
hsi -q "ls -l $SRC" 2>&1
echo "=== hpssquota AFTER ==="; $Q -u "$USER" 2>&1
echo "[$(date -u +%FT%TZ)] RESULT HPSS_DELETE_ISSUED for $DEL/$N objects; CFS copy retained at $DEST"
