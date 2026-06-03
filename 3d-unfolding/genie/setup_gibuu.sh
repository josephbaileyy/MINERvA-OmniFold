#!/bin/bash
# Native GiBUU 2019 (NOvA CVMFS build) on Perlmutter -- NO container needed.
#
# GiBUU.x is dynamically linked against ROOT (libCore/libRIO/libTree/...) and the
# old Fortran runtime libgfortran.so.3. We resolve:
#   - ROOT from the conda root_6_28 env (its libstdc++.so.6 is new enough to
#     satisfy ROOT's GLIBCXX_3.4.29/30 + CXXABI_1.3.15 requirements), and
#   - libgfortran.so.3 from the larsoft gcc v6_3_0 product.
# ORDER MATTERS: the conda lib dir (new libstdc++) MUST precede the old gcc lib
# dir, or the stale gcc libstdc++ wins and ROOT fails to load. Verified: with
# this order `ldd GiBUU.x` resolves cleanly and the binary starts.
#
# Usage:  source setup_gibuu.sh   (then run "$GIBUU_BIN" < jobcard)
GIBUU_HOME=/cvmfs/nova.opensciencegrid.org/externals/gibuu/v2019/Linux64bit+2.6-2.12-e15/GiBUU
export GIBUU_BIN="$GIBUU_HOME/bin/GiBUU.x"
export GIBUU_INPUT="$GIBUU_HOME/buuinput2019"
export GIBUU_FLUX="$GIBUU_INPUT/neutrino/MINERvA_MEflux.dat"   # MINERvA medium-energy nu flux (0.25-94.75 GeV)

CONDA_ROOTLIB=/global/homes/j/josephrb/.conda/envs/root_6_28/lib
GCC3LIB=/cvmfs/larsoft.opensciencegrid.org/products/gcc/v6_3_0/Linux64bit+3.10-2.17/lib64
export LD_LIBRARY_PATH="$CONDA_ROOTLIB:$GCC3LIB:$GIBUU_HOME/lib:$LD_LIBRARY_PATH"

if [ ! -x "$GIBUU_BIN" ]; then echo "[setup_gibuu] FAIL: $GIBUU_BIN missing" >&2; return 1 2>/dev/null || exit 1; fi
echo "[setup_gibuu] GiBUU.x = $GIBUU_BIN"
echo "[setup_gibuu] input   = $GIBUU_INPUT"
echo "[setup_gibuu] flux    = $GIBUU_FLUX"
