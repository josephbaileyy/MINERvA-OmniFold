#!/bin/bash
# setup_genie.sh -- set up GENIE 2.12.10c from CVMFS for truth-event generation
# on Perlmutter (SLES15). SOURCE this (do not execute).
#
# GENIE on CVMFS is built for SL7 (Linux64bit+3.10-2.17, glibc 2.17); Perlmutter
# is SLES15 (glibc 2.38). UPS refuses the flavor, so we force it with -H, and
# glibc forward-compat runs the binaries. Three SL7/SL6 system libs are missing
# on the host (libpcreposix, libpcre, libssl.so.10, libcrypto.so.10); we shim
# ONLY those from the MINERvA SL6 container (never its libc) into a compat dir.
#
# Feasibility proven 2026-05-30: gevgen generates events end-to-end this way.
#
# Usage:  source setup_genie.sh   (from a shell; it scrubs the analysis conda
#         env first so GENIE uses its own UPS ROOT, not root_6_28).

# --- scrub the MINERvA-OmniFold analysis env (conda ROOT clashes with UPS ROOT)
conda deactivate >/dev/null 2>&1 || true
unset ROOTSYS PYTHONPATH PYTHONHOME
export LD_LIBRARY_PATH=""
export PATH=/usr/bin:/bin

# --- pinned CVMFS locations -------------------------------------------------
export GENIE_UPS=/cvmfs/larsoft.opensciencegrid.org/products
export GENIE_FLAVOR="Linux64bit+3.10-2.17"          # SL7 build (run via fwd-compat)
export GENIE_VER=v2_12_10c                            # closest CVMFS ver to MINERvA 2.12.6
export GENIE_QUAL=e15:prof
export GENIE_XSEC_VER=v2_12_10
export GENIE_TUNE=DefaultPlusValenciaMEC              # MINERvA base config (Tune v1 = this + reweights)
export GENIE_SPLINES_FULL=${GENIE_UPS}/genie_xsec/${GENIE_XSEC_VER}/NULL/${GENIE_TUNE}/data/gxspl-FNALbig.xml.gz
# Prefer the reduced C12+H1 spline (reduce_splines.sh) -- loads in seconds vs
# ~30 min for the full ~850 MB file. Falls back to the full file if absent.
_GENIE_DIR_SH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$_GENIE_DIR_SH/gxspl_CH.xml.gz" ]; then
  export GENIE_SPLINES="$_GENIE_DIR_SH/gxspl_CH.xml.gz"
else
  export GENIE_SPLINES="$GENIE_SPLINES_FULL"
fi

# MINERvA ME FHC numu flux shape. MUST be the plain-TH1D copy produced by
# make_flux_for_genie.py -- the CVMFS source is a PlotUtils::MnvH1D, which GENIE
# reads with integral=0 (flux sampling then fails). Run make_flux_for_genie.py
# once (analysis env) to create flux_mefhc_numu.root.
export GENIE_FLUX="${_GENIE_DIR_SH:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}/flux_mefhc_numu.root"
export GENIE_FLUX_HIST=flux_numu

MINERVA_CONTAINER=/cvmfs/minerva.opensciencegrid.org/minerva/containers/sl6_fnal_python3

# --- compat-lib shim (only the missing OS libs; NEVER the container libc) ----
export GENIE_COMPAT=${GENIE_COMPAT:-$HOME/.genie_compatlibs}
mkdir -p "$GENIE_COMPAT"
for l in usr/lib64/libpcreposix.so.0 usr/lib64/libpcreposix.so.0.0.0 \
         lib64/libpcre.so.0 lib64/libpcre.so.0.0.1 \
         usr/lib64/libssl.so.10 usr/lib64/libcrypto.so.10; do
  base=$(basename "$l")
  if [ -e "$MINERVA_CONTAINER/$l" ]; then
    ln -sf "$MINERVA_CONTAINER/$l" "$GENIE_COMPAT/$base"
  fi
done

# --- UPS setup --------------------------------------------------------------
source "${GENIE_UPS}/setup" 2>/dev/null
setup -H "${GENIE_FLAVOR}" genie "${GENIE_VER}" -q "${GENIE_QUAL}"
setup -H "${GENIE_FLAVOR}" genie_xsec "${GENIE_XSEC_VER}" -q "${GENIE_TUNE}"
export LD_LIBRARY_PATH="${GENIE_COMPAT}:${LD_LIBRARY_PATH}"

# --- sanity -----------------------------------------------------------------
if [ -z "$GENIE" ] || ! command -v gevgen >/dev/null 2>&1; then
  echo "[setup_genie] ERROR: GENIE not set up (GENIE=$GENIE)" >&2
  return 1 2>/dev/null || exit 1
fi
echo "[setup_genie] GENIE=$GENIE"
echo "[setup_genie] gevgen=$(command -v gevgen)"
echo "[setup_genie] splines=$GENIE_SPLINES"
echo "[setup_genie] compat libs: $(ls "$GENIE_COMPAT" | tr '\n' ' ')"
