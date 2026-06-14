#!/bin/bash
# run_fsi_reweight.sh GHEP [DIAL] [NTWK] [MIN] [MAX] [OUT] [NEV]
#
# GENIE single-parameter reweighting (grwght1p) on a GHEP file for one GSyst
# dial -- by default the pion inelastic FSI knob FrInel_pi, the FSI parameter
# that redistributes hadronic energy (hence Eavail) and that MAT-MINERvA leaves
# commented out (technote App B open question #2). FSI reweighting is a
# truth-level operation on the *same* CV events -- no regeneration needed.
#
# Scans NTWK tweak-dial values evenly in [MIN,MAX] sigma (NTWK forced odd and
# >=3 by GENIE; the middle value is 0 == CV). Writes a TTree named <DIAL> with
# branches eventnum / weights[NTWK] / twkdials[NTWK]; eventnum == gst `iev`, so
# fsi_variation_xsec3d.py aligns weights to events per row.
set -eo pipefail

GHEP=${1:?usage: run_fsi_reweight.sh GHEP [DIAL NTWK MIN MAX OUT NEV]}
DIAL=${2:-FrInel_pi}
NTWK=${3:-3}
MIN=${4:--1}
MAX=${5:-1}
OUT=${6:-$(dirname "$GHEP")/weights_${DIAL}.root}
NEV=${7:-}
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# clean-env GENIE setup (scrubs analysis conda ROOT); UPS is not set -e safe.
set +e
source "$HERE/setup_genie.sh"
SETUP_RC=$?
set -e
[ $SETUP_RC -eq 0 ] || { echo "[fsi] setup_genie.sh failed rc=$SETUP_RC" >&2; exit 1; }

[ -f "$GHEP" ] || { echo "[fsi] no GHEP file: $GHEP" >&2; exit 1; }
MSG="$GENIE/config/Messenger_laconic.xml"
mkdir -p "$(dirname "$OUT")"
echo "[fsi] grwght1p f=$GHEP s=$DIAL t=$NTWK range=[$MIN,$MAX] ${NEV:+n=$NEV} -> $OUT"
echo "[fsi]   $(date -u '+%F %T UTC')"

grwght1p \
  -f "$GHEP" \
  -s "$DIAL" \
  -t "$NTWK" \
  --min-tweak "$MIN" \
  --max-tweak "$MAX" \
  -p 14 \
  -o "$OUT" \
  ${NEV:+-n "$NEV"} \
  ${MSG:+--message-thresholds "$MSG"} \
  > "${OUT%.root}.log" 2>&1
echo "[fsi] grwght1p rc=$? log=$(wc -l < "${OUT%.root}.log") lines"
grep -iE "ERROR|FATAL" "${OUT%.root}.log" | head -3 || true
ls -la "$OUT"
echo "[fsi] done $(date -u '+%F %T UTC')"
