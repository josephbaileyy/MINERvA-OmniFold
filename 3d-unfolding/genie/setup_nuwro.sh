#!/bin/bash
# setup_nuwro.sh -- set up NuWro v21_09_1 from CVMFS for truth-event generation
# on Perlmutter (SLES15). SOURCE this (do not execute).
#
# Mirrors setup_genie.sh: UPS -H SL7-flavor override + glibc forward-compat +
# the compat-lib shim (the GENIE shim libs + libxxhash from conda). Two NuWro
# specifics learned during bring-up:
#  * use the e20:DEBUG build -- the e20:prof build segfaults inside the
#    flux-driven test-event phase on this platform (optimisation FP edge case);
#    debug runs clean.
#  * NuWro derives its data dir as <bin>/../data, but the UPS layout puts data a
#    level deeper, so we invoke via $NUWRO_HOME/bin/nuwro (a local symlink dir
#    with bin/nuwro + data/ pointing at the real locations).
#  * flux histogram x-axis MUST be in GeV (NuWro multiplies by GeV internally),
#    range-restricted to [0.5,50] GeV (flux_mefhc_numu_nuwro.root) to avoid a
#    crash on the extreme flux edges.

conda deactivate >/dev/null 2>&1 || true
unset ROOTSYS PYTHONPATH PYTHONHOME
export LD_LIBRARY_PATH=""
export PATH=/usr/bin:/bin

export NUWRO_UPS=/cvmfs/larsoft.opensciencegrid.org/products
export NUWRO_FLAVOR="Linux64bit+3.10-2.17"
export NUWRO_VER=v21_09_1
export NUWRO_QUAL=e20:debug

_NUWRO_DIR_SH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# compat shim: GENIE libs + libxxhash (from conda) -- never the container libc
export GENIE_COMPAT=${GENIE_COMPAT:-$HOME/.genie_compatlibs}
mkdir -p "$GENIE_COMPAT"
[ -e "$GENIE_COMPAT/libxxhash.so.0" ] || \
  ln -sf "$HOME/.conda/envs/root_6_28/lib/libxxhash.so.0" "$GENIE_COMPAT/libxxhash.so.0" 2>/dev/null

source "${NUWRO_UPS}/setup" 2>/dev/null
setup -H "${NUWRO_FLAVOR}" nuwro "${NUWRO_VER}" -q "${NUWRO_QUAL}"
export LD_LIBRARY_PATH="${GENIE_COMPAT}:${LD_LIBRARY_PATH}"
# header path so root macros (nuwro_to_flat.C) can resolve the event class
export ROOT_INCLUDE_PATH="${NUWRO_FQ_DIR}/nuwro-nuwro_21.09.1/src:${ROOT_INCLUDE_PATH}"

# local "nuwro home" (bin/nuwro + data symlinks) so the <bin>/../data lookup works
export NUWRO_HOME="${_NUWRO_DIR_SH}/nuwro_home_dbg"
mkdir -p "$NUWRO_HOME/bin"
ln -sf "${NUWRO_FQ_DIR}/bin/nuwro" "$NUWRO_HOME/bin/nuwro"
ln -sf "${NUWRO_FQ_DIR}/nuwro-nuwro_21.09.1/data" "$NUWRO_HOME/data"

export NUWRO_FLUX="${_NUWRO_DIR_SH}/flux_mefhc_numu_nuwro.root"   # GeV, [0.5,50]
export NUWRO_FLUX_HIST=flux_numu
export NUWRO_FLAT_MACRO="${_NUWRO_DIR_SH}/nuwro_to_flat.C"

if ! command -v "$NUWRO_HOME/bin/nuwro" >/dev/null 2>&1 && [ ! -x "$NUWRO_HOME/bin/nuwro" ]; then
  echo "[setup_nuwro] ERROR: nuwro not set up" >&2; return 1 2>/dev/null || exit 1
fi
echo "[setup_nuwro] nuwro=$NUWRO_HOME/bin/nuwro (debug build)"
echo "[setup_nuwro] flux=$NUWRO_FLUX"
