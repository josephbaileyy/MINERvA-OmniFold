#!/bin/bash
set -eo pipefail
base=/pscratch/sd/j/josephrb/ibuchi-evloop-20261123
source /pscratch/sd/j/josephrb/MINERvA-OmniFold/setup_salloc_env.sh >/dev/null
"$CXX" -O2 -std=c++17 $(root-config --cflags) -I"$base/src" -I"$MINERVA_PREFIX/include" measure.cpp -o measure -L"$MINERVA_PREFIX/lib" -lMAT-MINERvA -lMAT $(root-config --libs) -lGeom -lGenVector
