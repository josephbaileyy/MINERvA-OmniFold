#!/bin/bash
# run_gevgen.sh N SEED OUTTAG  -- generate base-GENIE-CV numu-on-CH truth events
# with the MINERvA ME FHC flux, then convert to the flat 'gst' tree.
#
# Produces (in $GENIE_WORK, default genie/work_<OUTTAG>):
#   gntp.<SEED>.ghep.root        (full GHEP records)
#   genie_mefhc_<OUTTAG>.gst.root (flat gst tree consumed by genie_to_xsec3d.py)
#
# CH target by mass fraction (C12 0.9225, H1 0.0775). Base tune
# DefaultPlusValenciaMEC == MINERvA Tune v1 *before* the MINERvA reweights.
set -eo pipefail

N=${1:-200000}
SEED=${2:-1}
OUTTAG=${3:-cv}
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "[run_gevgen] starting: N=$N seed=$SEED tag=$OUTTAG"

# clean-env GENIE setup (scrubs analysis conda ROOT). UPS scripts are not
# set -e safe, so disable errexit across the source.
set +e
source "$HERE/setup_genie.sh"
SETUP_RC=$?
set -e
[ $SETUP_RC -eq 0 ] || { echo "[run_gevgen] setup_genie.sh failed rc=$SETUP_RC" >&2; exit 1; }

GENIE_WORK=${GENIE_WORK:-$HERE/work_${OUTTAG}}
mkdir -p "$GENIE_WORK"; cd "$GENIE_WORK"

echo "[run_gevgen] N=$N seed=$SEED tag=$OUTTAG  cwd=$PWD  $(date -u '+%F %T UTC')"

# Flux: file.root,histname (this gevgen takes the species from -p 14; the
# histogram MUST be a plain TH1D -- see GENIE_FLUX note in setup_genie.sh).
# Energy capped at 50 GeV (ME FHC flux negligible above ~40). Laconic messaging
# keeps the log small.
MSG="$GENIE/config/Messenger_laconic.xml"
# Optional GEVGEN_LIST (env) -> --event-generator-list, e.g. Default+CCMEC to
# enable the Valencia 2p2h/MEC channel (the bare 'Default' list excludes it).
gevgen \
  -n "$N" \
  -e 0,50 \
  -p 14 \
  -t '1000060120[0.9225],1000010010[0.0775]' \
  -f "${GENIE_FLUX},${GENIE_FLUX_HIST}" \
  --cross-sections "$GENIE_SPLINES" \
  ${GEVGEN_LIST:+--event-generator-list "$GEVGEN_LIST"} \
  --seed "$SEED" \
  -r "$SEED" \
  ${MSG:+--message-thresholds "$MSG"} \
  > gevgen_${OUTTAG}.log 2>&1
echo "[run_gevgen] gevgen rc=$? log=$(wc -l < gevgen_${OUTTAG}.log) lines"
grep -iE "ERROR|FATAL" gevgen_${OUTTAG}.log | head -3 || true

GHEP=$(ls -t gntp.*.ghep.root 2>/dev/null | head -1)
[ -n "$GHEP" ] && [ -f "$GHEP" ] || { echo "[run_gevgen] ERROR: no gntp.*.ghep.root produced" >&2; exit 1; }
echo "[run_gevgen] generated $(ls -la "$GHEP" | awk '{print $5}') bytes -> converting to gst"

gntpc -i "$GHEP" -f gst -o "genie_mefhc_${OUTTAG}.gst.root" 2>&1 | tail -3
ls -la "genie_mefhc_${OUTTAG}.gst.root"
echo "[run_gevgen] done $(date -u '+%F %T UTC')"
