#!/bin/bash
# Remote adler32 of the current public MINERvA open-data ME-FHC MC AnaTuples, as reported by dCache
# (`xrdfs query checksum`). Metadata only; nothing is downloaded. Read-only on every input.
#
#   bash remote_adler.sh LIST OUT
#
# LIST: one path per line relative to .../MC/StandardMC (e.g. Playlist1B/<file>).
# OUT:  TSV, one row appended per query: relpath, adler32 (or -), status OK|ERR, utc, host, raw reply.
# Resumable: a relpath that already has an OK row is skipped; ERR rows are retried on the next run.
# A timeout or any reply that is not "adler32 <8 hex>" is an ERR, never a checksum.
eval "$(/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda shell.bash hook)"
conda activate "$HOME/.conda/envs/root_6_28"
set -o pipefail
LIST=$1; OUT=$2
B=/pnfs/fnal.gov/usr/minerva/persistent/OpenData/MediumEnergy_FHC/MC/StandardMC
EP=root://fndca1.fnal.gov:1095
H=$(hostname)
echo -e "#run-start\t$(date -u +%FT%TZ)\t$H\t$$" >> "$OUT"
while IFS= read -r rel; do
  [ -n "$rel" ] || continue
  if awk -F'\t' -v r="$rel" '$1==r && $3=="OK" {f=1} END {exit !f}' "$OUT"; then continue; fi
  reply=$(timeout 90 xrdfs "$EP" query checksum "$B/$rel" 2>&1); rc=$?
  reply=$(printf '%s' "$reply" | tr '\t\n' '  ')
  if [ $rc -eq 0 ] && [[ $reply =~ ^adler32\ ([0-9a-f]{8})\ *$ ]]; then
    printf '%s\t%s\tOK\t%s\t%s\t%s\n' "$rel" "${BASH_REMATCH[1]}" "$(date -u +%FT%TZ)" "$H" "$reply" >> "$OUT"
  else
    printf '%s\t-\tERR\t%s\t%s\trc=%s %s\n' "$rel" "$(date -u +%FT%TZ)" "$H" "$rc" "$reply" >> "$OUT"
  fi
done < "$LIST"
echo -e "#run-end\t$(date -u +%FT%TZ)\t$H\t$$" >> "$OUT"
