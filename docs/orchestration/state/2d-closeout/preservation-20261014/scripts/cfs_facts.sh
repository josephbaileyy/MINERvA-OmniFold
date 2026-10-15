#!/bin/bash
# CFS storage facts for draft A. Metadata only (du, find -printf); nothing is read, written or moved
# outside OUTDIR. Run on dtn01.nersc.gov:  nohup bash cfs_facts.sh OUTDIR > /dev/null 2>&1 &
OUTDIR=$1
C=/global/cfs/cdirs/m3246/josephrb
DEST=$C/prd-release-preservation-20261008/anatuple-data-20261009
{
  echo -e "du-start\t$(date -u +%FT%TZ)\t$(hostname)"
  du -s --block-size=1 "$C"; echo -e "du_rc\t$?"
  du -s --block-size=1G "$C"
  du -s --apparent-size --block-size=1 "$C"
  echo -e "du-end\t$(date -u +%FT%TZ)"
} > "$OUTDIR/cfs_du.txt" 2>&1
# every regular file in the data copy: path relative to DEST, bytes, mtime (UTC)
( cd "$DEST" && TZ=UTC find . -type f -printf '%P\t%s\t%TY-%Tm-%TdT%TH:%TM:%.2TSZ\n' | LC_ALL=C sort ) \
  > "$OUTDIR/cfs_datacopy_files.tsv" 2> "$OUTDIR/cfs_datacopy_find_stderr.txt"
echo -e "find_rc\t$?\t$(date -u +%FT%TZ)" >> "$OUTDIR/cfs_datacopy_find_stderr.txt"
# any 1A MC AnaTuple (run0011000x/0011001x/... names) anywhere under our CFS area
TZ=UTC find "$C" -name 'MasterAnaDev_mc_AnaTuple_run0011*' -printf '%p\t%s\n' \
  > "$OUTDIR/cfs_mc_anatuple_hits.tsv" 2> "$OUTDIR/cfs_mc_find_stderr.txt"
echo -e "find_rc\t$?\t$(date -u +%FT%TZ)" >> "$OUTDIR/cfs_mc_find_stderr.txt"
echo done > "$OUTDIR/cfs_facts.done"
