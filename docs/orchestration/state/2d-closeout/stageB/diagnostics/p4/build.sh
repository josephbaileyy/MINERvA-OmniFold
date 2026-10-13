#!/bin/bash
# P4 G1 census: build an UNPATCHED and a PATCHED copy of runEventLoopOmniFold in the diagnostics namespace.
# Never touches the production build (MINERvA101/opt/build_MINERvA101) or opt/bin. Login node.
#   bash build.sh <p4 namespace> <path to patch.diff>
# No `set -u` before the root_6_28 activation (it aborts on ADDR2LINE).
set -eo pipefail
NS=${1:?p4 namespace}
PATCH=${2:?patch.diff}
REPO=/pscratch/sd/j/josephrb/MINERvA-OmniFold
SRC=$REPO/MINERvA101/MINERvA-101-Cross-Section
PROD_SHA=57792e42fe3f5a663016f94b91a5631fc50349135c92b35a08eaefcb85812be3
OPT=/global/homes/j/josephrb/MINERvA-OmniFold/MINERvA101/opt   # the production cache's *_DIR prefix

source $REPO/setup_salloc_env.sh >/dev/null 2>&1
echo "[build] $(date -u +%FT%TZ) host $(hostname)"
[ "$(sha256sum $SRC/runEventLoopOmniFold.cpp | cut -c1-64)" = "$PROD_SHA" ] || { echo "REFUSE: production source sha changed"; exit 2; }

for v in unpatched patched; do
  rm -rf "$NS/src/$v" "$NS/build/$v"
  mkdir -p "$NS/src/$v" "$NS/build/$v"
  # copy the source tree, not its build directories
  (cd "$SRC" && tar --exclude=./build --exclude=./build.standalone-shadow.bak -cf - .) | tar -xf - -C "$NS/src/$v"
done
(cd "$NS/src/patched" && patch -p1 --no-backup-if-mismatch -i /dev/stdin) < <(sed -e '1s|^--- a/MINERvA101/MINERvA-101-Cross-Section/|--- a/|' -e '1s| (.*||' -e '2s|^+++ b/runEventLoopOmniFold.cpp.*|+++ b/runEventLoopOmniFold.cpp|' "$PATCH")
sha256sum "$NS/src/unpatched/runEventLoopOmniFold.cpp" "$NS/src/patched/runEventLoopOmniFold.cpp" | tee "$NS/build/source.sha256"

for v in unpatched patched; do
  cmake -S "$NS/src/$v" -B "$NS/build/$v" \
      -DCMAKE_INSTALL_PREFIX="$NS/opt_$v" \
      -DMAT_DIR=$OPT/lib/cmake/MAT -DMAT-MINERvA_DIR=$OPT/lib/cmake/MAT-MINERvA \
      -DUnfoldUtils_DIR=$OPT/lib/cmake/UnfoldUtils -DGENIEXSecExtract_DIR=$OPT/lib/cmake/GENIEXSecExtract \
      > "$NS/build/cmake_$v.log" 2>&1
  start=$(date +%s)
  cmake --build "$NS/build/$v" --target runEventLoopOmniFold --parallel 8 > "$NS/build/make_$v.log" 2>&1
  echo "[build] $v: $(( $(date +%s) - start )) s; $(sha256sum "$NS/build/$v/runEventLoopOmniFold" | cut -c1-64)"
done
# same compiler and flags as the production build
for k in CMAKE_CXX_COMPILER:FILEPATH CMAKE_CXX_FLAGS:STRING CMAKE_BUILD_TYPE:STRING; do
  for c in $REPO/MINERvA101/opt/build_MINERvA101 "$NS/build/unpatched" "$NS/build/patched"; do
    printf '%s %s: %s\n' "$k" "$(basename $c)" "$(grep "^$k=" $c/CMakeCache.txt | cut -d= -f2-)"
  done
done | tee "$NS/build/flags.txt"
echo "[build] done $(date -u +%FT%TZ)"
