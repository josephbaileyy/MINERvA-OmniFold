#!/bin/bash
# setup_genie_v3.sh TUNE -- set up GENIE v3_04_00 from CVMFS for the F1 truth samples
# (state/measurement-paper/5d-community-20261024/FD-F1-DECLARATION.md). SOURCE this (do not execute).
#
# TUNE is G18_10a_02_11b or AR23_20i_00_000. As setup_genie.sh does for v2, this scrubs the analysis
# conda env, forces the SL7 UPS flavour with -H (glibc forward-compat runs the binaries on SLES15) and puts
# the compat-lib shim first on LD_LIBRARY_PATH. Unlike setup_genie.sh it WRITES NOTHING: the shim directory
# must already hold libssl.so.10 and libcrypto.so.10 (setup_genie.sh made it), and the reduced CH spline file
# must already exist (run_gevgen_v3.sh reduce makes it in F1a).
#
#   source setup_genie_v3.sh G18_10a_02_11b <reduced spline dir>

_V3_TUNE=${1:?tune}
_V3_SPLDIR=${2:?reduced spline dir}

conda deactivate >/dev/null 2>&1 || true
unset ROOTSYS PYTHONPATH PYTHONHOME
export LD_LIBRARY_PATH=""
export PATH=/usr/bin:/bin

export GENIE_UPS=/cvmfs/larsoft.opensciencegrid.org/products
export GENIE_FLAVOR="Linux64bit+3.10-2.17"
export GENIE_VER=v3_04_00
export GENIE_QUAL=e20:prof
export GENIE_XSEC_VER=v3_04_00
case "$_V3_TUNE" in
  G18_10a_02_11b)  export GENIE_XSEC_QUAL=G1810a0211b:k250:e1000 ;;
  AR23_20i_00_000) export GENIE_XSEC_QUAL=AR2320i00000:k250:e1000 ;;
  *) echo "[setup_genie_v3] ERROR: unknown tune $_V3_TUNE" >&2; return 1 2>/dev/null || exit 1 ;;
esac
export GENIE_V3_TUNE="$_V3_TUNE"
export GENIE_SPLINES_V3="$_V3_SPLDIR/${_V3_TUNE}_CH.xml.gz"

export GENIE_COMPAT=${GENIE_COMPAT:-$HOME/.genie_compatlibs}
for _l in libssl.so.10 libcrypto.so.10; do
  if [ ! -e "$GENIE_COMPAT/$_l" ]; then
    echo "[setup_genie_v3] ERROR: $GENIE_COMPAT/$_l is missing (setup_genie.sh makes the shim)" >&2
    return 1 2>/dev/null || exit 1
  fi
done

source "${GENIE_UPS}/setup" 2>/dev/null
setup -H "${GENIE_FLAVOR}" genie "${GENIE_VER}" -q "${GENIE_QUAL}"
setup -H "${GENIE_FLAVOR}" genie_xsec "${GENIE_XSEC_VER}" -q "${GENIE_XSEC_QUAL}"
export LD_LIBRARY_PATH="${GENIE_COMPAT}:${LD_LIBRARY_PATH}"

if [ -z "$GENIE" ] || ! command -v gevgen >/dev/null 2>&1; then
  echo "[setup_genie_v3] ERROR: GENIE not set up (GENIE=$GENIE)" >&2
  return 1 2>/dev/null || exit 1
fi
if [ "${GENIE_XSEC_TUNE:-}" != "$_V3_TUNE" ]; then
  echo "[setup_genie_v3] ERROR: genie_xsec sets GENIE_XSEC_TUNE=${GENIE_XSEC_TUNE:-} for $_V3_TUNE" >&2
  return 1 2>/dev/null || exit 1
fi
echo "[setup_genie_v3] GENIE=$GENIE"
echo "[setup_genie_v3] gevgen=$(command -v gevgen)"
echo "[setup_genie_v3] tune=$GENIE_V3_TUNE xsec=${GENIEXSECPATH:-} splines=$GENIE_SPLINES_V3"
