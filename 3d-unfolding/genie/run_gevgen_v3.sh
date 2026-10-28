#!/bin/bash
# run_gevgen_v3.sh MODE ... -- the GENIE v3 truth samples of F1
# (state/measurement-paper/5d-community-20261024/FD-F1-DECLARATION.md section 2).
#
#   run_gevgen_v3.sh reduce TUNE SPLDIR           C12 + H1 splines of the tune's gxspl-NUsmall.xml -> SPLDIR/TUNE_CH.xml.gz
#   run_gevgen_v3.sh genie  TUNE SPLDIR N SEED WORKDIR FLUXFILE
#   run_gevgen_v3.sh graphs TUNE SPLDIR OUTFILE   gspl2root of the reduced splines for C12 and H1 to 100 GeV
#
# genie: run_gen5d_supplement.sh's gevgen/gntpc lines with the v3 setup: the same CH target mix, nu_mu, the
#   laconic messenger and seed = run number; --tune TUNE and the tune's own event-generator list (Default);
#   -e 0,100 with FLUXFILE,flux_numu,NOWIDTH (content = phi_t x width, gen5d_v3.py make-flux), so phi_t is sampled
#   directly and no flux reweight follows. NOWIDTH is required: v3.04.00's gEvGen.cxx otherwise multiplies a
#   variable-width histogram by its widths; gevgen writes what it samples to input-flux.root (gen5d_v3.py flux-check).
# reduce: reduce_splines.sh's awk filter, verbatim, on the tune's gxspl-NUsmall.xml.
set -eo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODE=$1; shift

case "$MODE" in
  reduce)
    TUNE=$1; SPLDIR=$2
    case "$TUNE" in
      G18_10a_02_11b)  Q=G1810a0211b-k250-e1000 ;;
      AR23_20i_00_000) Q=AR2320i00000-k250-e1000 ;;
      *) echo "unknown tune $TUNE" >&2; exit 2 ;;
    esac
    SRC=/cvmfs/larsoft.opensciencegrid.org/products/genie_xsec/v3_04_00/NULL/$Q/data/gxspl-NUsmall.xml
    OUT="$SPLDIR/${TUNE}_CH.xml"
    [ ! -e "$OUT.gz" ] || { echo "refusing to overwrite $OUT.gz" >&2; exit 2; }
    mkdir -p "$SPLDIR"
    awk '
      /<spline / { insp=1; buf=$0;
                   keep=($0 ~ /tgt:1000060120/ || $0 ~ /tgt:1000010010/); next }
      insp       { buf=buf ORS $0;
                   if ($0 ~ /<\/spline>/) { if (keep) print buf; insp=0 } next }
                 { print }
    ' "$SRC" > "$OUT"
    echo "[v3] reduce $TUNE: kept $(grep -c '<spline ' "$OUT") splines from $SRC"
    gzip -n "$OUT"
    sha256sum "$SRC" "$OUT.gz"
    ;;
  genie)
    TUNE=$1; SPLDIR=$2; N=$3; SEED=$4; WORK=$5; FLUX=$6
    set +e; source "$HERE/setup_genie_v3.sh" "$TUNE" "$SPLDIR"; RC=$?; set -e
    [ $RC -eq 0 ] || { echo "setup_genie_v3.sh failed rc=$RC" >&2; exit 1; }
    [ ! -e "$WORK/genie_v3.gst.root" ] || { echo "refusing to overwrite $WORK/genie_v3.gst.root" >&2; exit 2; }
    mkdir -p "$WORK"; cd "$WORK"
    MSG="$GENIE/config/Messenger_laconic.xml"
    echo "[v3] genie $TUNE N=$N seed=$SEED flux=$FLUX start $(date -u '+%F %T UTC')"
    gevgen \
      -n "$N" \
      -e 0,100 \
      -p 14 \
      -t '1000060120[0.9225],1000010010[0.0775]' \
      -f "${FLUX},flux_numu,NOWIDTH" \
      --tune "$TUNE" \
      --cross-sections "$GENIE_SPLINES_V3" \
      --seed "$SEED" \
      -r "$SEED" \
      ${MSG:+--message-thresholds "$MSG"} \
      > gevgen.log 2>&1
    echo "[v3] gevgen rc=$? $(date -u '+%F %T UTC')"
    gntpc -i "gntp.${SEED}.ghep.root" -f gst -o genie_v3.gst.root 2>&1 | tail -200 > gntpc.log
    echo "[v3] gntpc done $(date -u '+%F %T UTC')"
    rm -f "gntp.${SEED}.ghep.root"   # the gst is the product; the GHEP is reproducible from the seed
    [ -s input-flux.root ] || { echo "no input-flux.root from gevgen" >&2; exit 1; }
    ;;
  graphs)
    TUNE=$1; SPLDIR=$2; OUT=$3
    set +e; source "$HERE/setup_genie_v3.sh" "$TUNE" "$SPLDIR"; RC=$?; set -e
    [ $RC -eq 0 ] || exit 1
    [ ! -e "$OUT" ] || { echo "refusing to overwrite $OUT" >&2; exit 2; }
    gspl2root -f "$GENIE_SPLINES_V3" --tune "$TUNE" -p 14 -t 1000060120,1000010010 -e 100 -o "$OUT" \
      > "${OUT%.root}.log" 2>&1
    echo "[v3] gspl2root rc=$? -> $OUT"
    ;;
  *) echo "unknown mode $MODE" >&2; exit 2 ;;
esac
