#!/bin/bash
# Stat-only atime reading of LL5D's 1146 snapshot paths, around the G2R envtest (the director's empirical overlap check,
# 2026-11-13: if any listed path's atime moves, the overlap fence change is void and it is a STOP to the director).
# The list is column 2 of the pilot r2 atime-pre.tsv on pscratch, pinned by the sha256 that #1123's node-sha256.txt
# records. stat opens no listed file, so it moves no listed atime. It is a list, not a find (the r2 atime-post's find
# took 78 min). Output: one "atime_seconds<TAB>path" line per listed path, sorted by path in the C locale, then a closing
# summary line. Run on a login node:  ssh saul.nersc.gov 'bash -s' < atime-stat-list.sh > <out>
L=/pscratch/sd/j/josephrb/ll5d-pilot-r2/atime-pre.tsv
WANT=712ac1624d8a1527d360eaacb7cbd8255669c9bb9c7ca98f11ace9450598f92e
echo "host=$(hostname) utc=$(date -u +%FT%TZ)"
have=$(sha256sum "$L" | cut -c1-64)
[ "$have" = "$WANT" ] || { echo "STOP the list's sha256 is $have, not $WANT"; exit 3; }
n=$(wc -l < "$L" | tr -d " ")
t0=$(date +%s)
xargs -d '\n' -a <(cut -f2 "$L" | LC_ALL=C sort) stat --printf '%X\t%n\n'; rc=$?
echo "stat_rc=$rc n_list=$n seconds=$(( $(date +%s) - t0 )) end_utc=$(date -u +%FT%TZ)"
