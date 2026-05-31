#!/bin/bash
# reduce_splines.sh -- extract just the C12 + H1 (CH target) splines from the
# full GENIE spline file into a small local file that loads in ~minutes instead
# of ~30 min. Run ONCE; setup_genie.sh then prefers the reduced file.
#
# The full gxspl-FNALsmall.xml is ~856 MB (every FNAL isotope); parsing it
# dominates every gevgen startup. The CH subset is ~1000 splines.
set -eo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC=${SRC:-/cvmfs/larsoft.opensciencegrid.org/products/genie_xsec/v2_12_10/NULL/DefaultPlusValenciaMEC/data/gxspl-FNALsmall.xml}
OUT="$HERE/gxspl_CH.xml"

echo "[reduce_splines] extracting C12(1000060120)+H1(1000010010) from $(basename "$SRC")"
# Stream once: print header/footer (non-spline lines) verbatim; print a
# <spline>...</spline> block only if its name line targets C12 or H1.
awk '
  /<spline / { insp=1; buf=$0;
               keep=($0 ~ /tgt:1000060120/ || $0 ~ /tgt:1000010010/); next }
  insp       { buf=buf ORS $0;
               if ($0 ~ /<\/spline>/) { if (keep) print buf; insp=0 } next }
             { print }
' "$SRC" > "$OUT"

NKEPT=$(grep -c '<spline ' "$OUT" || true)
echo "[reduce_splines] kept $NKEPT splines -> $OUT ($(du -h "$OUT" | cut -f1))"
gzip -f "$OUT"
echo "[reduce_splines] wrote ${OUT}.gz ($(du -h "${OUT}.gz" | cut -f1)) -- setup_genie.sh will prefer it"
