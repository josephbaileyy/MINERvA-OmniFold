#!/bin/bash
# Build the two test C programs in the archived MAT environment of ../build.sh.
# Run in the scratch directory that holds the staged sources (see batch.sh).
set -eo pipefail
base=/pscratch/sd/j/josephrb/ibuchi-evloop-20261123
source /pscratch/sd/j/josephrb/MINERvA-OmniFold/setup_salloc_env.sh >/dev/null
sha256sum -c staged.sha256
for prog in measure truth; do
    "$CXX" -O2 -std=c++17 $(root-config --cflags) -I"$base/src" -I"$MINERVA_PREFIX/include" \
        "$prog.cpp" -o "$prog" -L"$MINERVA_PREFIX/lib" -lMAT-MINERvA -lMAT $(root-config --libs) -lGeom -lGenVector
done
sha256sum measure truth > built.sha256
cat built.sha256
