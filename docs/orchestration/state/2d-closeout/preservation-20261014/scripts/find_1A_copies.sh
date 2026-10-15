#!/bin/bash
# Search for any copy of the 41 1A MC AnaTuple basenames outside .../minerva_large_files/MC/StandardMC/Playlist1A.
# Metadata only (find by name). Run on dtn01.nersc.gov:  nohup bash find_1A_copies.sh NAMES OUTDIR > /dev/null 2>&1 &
NAMES=$1; OUTDIR=$2
args=(); while IFS= read -r n; do args+=(-name "$n" -o); done < "$NAMES"; unset 'args[${#args[@]}-1]'
for root in /global/pscratch/sd/j/josephrb /global/homes/j/josephrb /global/cfs/cdirs/m3246; do
  tag=$(echo "$root" | tr / _)
  t0=$(date -u +%FT%TZ)
  timeout 7200 find "$root" \( "${args[@]}" \) -printf '%p\t%s\t%y\n' > "$OUTDIR/find1A$tag.tsv" 2> "$OUTDIR/find1A${tag}_stderr.txt"
  echo -e "$root\tstart=$t0\tend=$(date -u +%FT%TZ)\trc=$?\thits=$(wc -l < "$OUTDIR/find1A$tag.tsv")\tstderr_lines=$(wc -l < "$OUTDIR/find1A${tag}_stderr.txt")" >> "$OUTDIR/find1A_summary.tsv"
done
echo done > "$OUTDIR/find1A.done"
