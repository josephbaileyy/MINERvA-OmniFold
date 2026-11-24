#!/bin/bash
# ibuchi build (login node). Copies the event-loop source tree (no build dirs) into ROOT/src, puts the reviewed .cpp in
# place, configures against the installed MAT/MAT-MINERvA/UnfoldUtils (read-only), installs to ROOT/opt. Writes only ROOT.
set -eo pipefail
ROOT=/pscratch/sd/j/josephrb/ibuchi-evloop-20261123; REPO=/pscratch/sd/j/josephrb/MINERvA-OmniFold
S=$REPO/MINERvA101/MINERvA-101-Cross-Section; CPP=$ROOT/upload/runEventLoopOmniFold.cpp; PIN_CPP=$1
[ "$(sha256sum $CPP | cut -c1-64)" = "$PIN_CPP" ] || { echo "REFUSED: uploaded cpp sha differs"; exit 2; }
[ ! -e $ROOT/src ] || { echo "REFUSED: $ROOT/src exists"; exit 2; }
mkdir -p $ROOT/src $ROOT/build $ROOT/opt
rsync -a --exclude 'build' --exclude 'build.*' --exclude '.ipynb_checkpoints' $S/ $ROOT/src/
echo "canonical cpp sha $(sha256sum $ROOT/src/runEventLoopOmniFold.cpp | cut -c1-16) (expect 57792e42fe3f5a66)"
cp $CPP $ROOT/src/runEventLoopOmniFold.cpp
set +u; source $REPO/setup_salloc_env.sh; set -u 2>/dev/null || true
O=$REPO/MINERvA101/opt/lib/cmake
cmake -S $ROOT/src -B $ROOT/build -DCMAKE_INSTALL_PREFIX=$ROOT/opt -DMAT_DIR=$O/MAT -DMAT-MINERvA_DIR=$O/MAT-MINERvA -DUnfoldUtils_DIR=$O/UnfoldUtils > $ROOT/build/configure.log 2>&1
cmake --build $ROOT/build --target runEventLoopOmniFold --parallel 8 > $ROOT/build/build.log 2>&1
install -D -m 755 $ROOT/build/runEventLoopOmniFold $ROOT/opt/bin/runEventLoopOmniFold
echo "binary sha $(sha256sum $ROOT/opt/bin/runEventLoopOmniFold | cut -c1-64)"
grep -c -E 'warning|error' $ROOT/build/build.log || true
