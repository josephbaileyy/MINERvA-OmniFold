#!/bin/bash
# Stat-only atime-post for the LL5D bulk (ll5d-bulk-r1). It reads the atime of each of the 1146 paths in the bulk's own
# atime-pre.tsv, /pscratch/sd/j/josephrb/ll5d-bulk-r1/atime-pre.tsv (sha256 908d3922..., 1146 lines), pinned below.
# stat opens no listed file, so it moves no listed atime. It works from the list rather than a find (the pilot r2
# atime-post's find took 78 min; this list's stat took 1 s around the G2R envtest). Output: one
# "atime_seconds<TAB>path" line per listed path, sorted by path in the C locale, then a closing summary line. The
# comparison with atime-pre is done locally on the fetched output, not here.
# Run on a login node:  ssh saul.nersc.gov 'bash -s' < atime-post-bulk.sh > <out>
L=/pscratch/sd/j/josephrb/ll5d-bulk-r1/atime-pre.tsv
WANT=908d3922e81fa25eff7e61932ed690fc55a1cd8f04c5b26dbc1905c5b0da04f3
echo "host=$(hostname) utc=$(date -u +%FT%TZ)"
have=$(sha256sum "$L" | cut -c1-64)
[ "$have" = "$WANT" ] || { echo "STOP the list's sha256 is $have, not $WANT"; exit 3; }
n=$(wc -l < "$L" | tr -d " ")
t0=$(date +%s)
xargs -d '\n' -a <(cut -f2 "$L" | LC_ALL=C sort) stat --printf '%X\t%n\n'; rc=$?
echo "stat_rc=$rc n_list=$n seconds=$(( $(date +%s) - t0 )) end_utc=$(date -u +%FT%TZ)"
