#!/bin/bash
# geanttw_build.sh: login-node build of prefix-{pin,pat} and both runEventLoopOmniFold binaries;
# the §2 diff check and the libMAT identity/differ checks.
#   bash geanttw_build.sh <B> <deploy-at-M>
# Runs with nice -n 19.  Refuses unless B is the production path or GEANTTW_SMOKE_B is set
# and equals B.  Refuses if B/src, B/prefix-pin, B/prefix-pat or B/build-* exist.
# Tests put stub cmake/make on PATH and set GEANTTW_SMOKE_B, which alone unlocks the pin and patch-file
# overrides (GEANTTW_MAT_PIN, GEANTTW_MATMINERVA_PIN, GEANTTW_PATCH_COMMIT, GEANTTW_PATCH_FILES).
# URLs overridable by GEANTTW_MAT_URL / GEANTTW_MATMINERVA_URL.
set -euo pipefail
renice -n 19 $$ >/dev/null 2>&1 || true

B="${1:?usage: geanttw_build.sh <B> <deploy-at-M>}"
DEPLOY="${2:?usage: geanttw_build.sh <B> <deploy-at-M>}"

PROD_B=/pscratch/sd/j/josephrb/geanttw-20261124
say() { echo "[geanttw-build] $*" >&2; }

# --- path guard ---
if [[ "${B}" != "${PROD_B}" ]]; then
  [[ -n "${GEANTTW_SMOKE_B:-}" && "${GEANTTW_SMOKE_B}" == "${B}" ]] \
    || { say "REFUSE: B is ${B}, not ${PROD_B} and GEANTTW_SMOKE_B is not set or does not match"; exit 2; }
fi
for d in "${B}/src" "${B}/prefix-pin" "${B}/prefix-pat"; do
  [[ -e "${d}" ]] && { say "REFUSE: ${d} exists"; exit 2; }
done
for d in "${B}"/build-*; do
  [[ -e "${d}" ]] && { say "REFUSE: build dir ${d} exists"; exit 2; }
done

# --- pins (overridable only in the tests' smoke mode, where the fake repos have other shas) ---
MAT_PIN=35097b65ab1680db8058f9ede18fecffdc3a1ea3
MATMINERVA_PIN=50d7631416d1c93edd4db6886a2ca29da64fee60
PATCH_COMMIT=3e411c0d3a6f598aa2072c6729790e4701e4089d
if [[ -n "${GEANTTW_SMOKE_B:-}" ]]; then
  MAT_PIN="${GEANTTW_MAT_PIN:-${MAT_PIN}}"
  MATMINERVA_PIN="${GEANTTW_MATMINERVA_PIN:-${MATMINERVA_PIN}}"
  PATCH_COMMIT="${GEANTTW_PATCH_COMMIT:-${PATCH_COMMIT}}"
fi
PROD_OPT=/pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/opt
CANON_SRC=/pscratch/sd/j/josephrb/MINERvA-OmniFold/MINERvA101/MINERvA-101-Cross-Section
if [[ -n "${GEANTTW_SMOKE_B:-}" ]]; then
  PROD_OPT="${GEANTTW_PROD_OPT:-${PROD_OPT}}"
  CANON_SRC="${GEANTTW_CANON_SRC:-${CANON_SRC}}"
fi
CODE="${DEPLOY}/docs/orchestration/state/geanttw-20261124/code"

# --- the ROOT environment, activated as setup_salloc_env.sh does (never sourcing it) ---
ROOT628_PREFIX="${ROOT628_PREFIX:-$HOME/.conda/envs/root_6_28}"
ROOT628_CONDA="${ROOT628_CONDA:-/global/common/software/nersc/pe/conda/24.10.0/Miniforge3-24.7.1-0/bin/conda}"
[[ -x "${ROOT628_CONDA}" && -d "${ROOT628_PREFIX}" ]] \
  || { say "REFUSE: conda ${ROOT628_CONDA} or env ${ROOT628_PREFIX} is missing"; exit 2; }
# conda's activate.d scripts reference unset variables, so nounset is off for the hook and the activation
# (root_6_28's activate-binutils_linux-64.sh aborts on ADDR2LINE: rpd-reco/prologue-20261107/README.txt:14)
set +u
eval "$("${ROOT628_CONDA}" shell.bash hook 2>/dev/null)"
conda activate "${ROOT628_PREFIX}" || true
set -u
[[ "${CONDA_PREFIX:-}" == "${ROOT628_PREFIX}" ]] \
  || { say "REFUSE: conda activation did not give CONDA_PREFIX=${ROOT628_PREFIX}"; exit 2; }

MAT_URL="${GEANTTW_MAT_URL:-https://github.com/MinervaExpt/MAT.git}"
MATMINERVA_URL="${GEANTTW_MATMINERVA_URL:-https://github.com/MinervaExpt/MAT-MINERvA.git}"


# --- clone ---
mkdir -p "${B}/src"
say "cloning MAT at ${MAT_PIN}"
git clone --quiet "${MAT_URL}" "${B}/src/MAT"
git -C "${B}/src/MAT" -c advice.detachedHead=false checkout --quiet "${MAT_PIN}"

say "cloning MAT-MINERvA at ${MATMINERVA_PIN} (pin)"
git clone --quiet "${MATMINERVA_URL}" "${B}/src/MAT-MINERvA-pin"
git -C "${B}/src/MAT-MINERvA-pin" -c advice.detachedHead=false checkout --quiet "${MATMINERVA_PIN}"

say "creating MAT-MINERvA-pat by cherry-picking ${PATCH_COMMIT}"
git clone --quiet "${B}/src/MAT-MINERvA-pin" "${B}/src/MAT-MINERvA-pat"
git -C "${B}/src/MAT-MINERvA-pat" -c advice.detachedHead=false checkout --quiet "${MATMINERVA_PIN}"
# Add the upstream remote to fetch the commit for cherry-pick
git -C "${B}/src/MAT-MINERvA-pat" remote add upstream "${MATMINERVA_URL}"
git -C "${B}/src/MAT-MINERvA-pat" fetch --quiet upstream "${PATCH_COMMIT}"
git -C "${B}/src/MAT-MINERvA-pat" -c user.name=build -c user.email=build@build cherry-pick --no-edit "${PATCH_COMMIT}"

# --- CHECK DIFF_EQUALS_UPSTREAM (declaration §2): pin..pat equals the upstream commit's diff byte for byte, and
# touches exactly the two files 3e411c0d changes. A failure is recorded and the build STOPs before compiling. ---
PATCH_FILES="universes/GeantHadronSystematics.cxx weighters/GeantNeutronCVReweighter.h"
[[ -n "${GEANTTW_SMOKE_B:-}" ]] && PATCH_FILES="${GEANTTW_PATCH_FILES:-${PATCH_FILES}}"
mkdir -p "${B}/run/p0"
LOG="${B}/run/p0/build.log"
: > "${LOG}"
say "checking that the cherry-pick's diff equals the upstream diff and touches only: ${PATCH_FILES}"
our_diff=$(git -C "${B}/src/MAT-MINERvA-pat" diff "${MATMINERVA_PIN}..HEAD")
upstream_diff=$(git -C "${B}/src/MAT-MINERvA-pat" show "${PATCH_COMMIT}" --format=)
our_files=$(git -C "${B}/src/MAT-MINERvA-pat" diff --name-only "${MATMINERVA_PIN}..HEAD" | sort | tr '\n' ' ')
want_files=$(printf '%s\n' ${PATCH_FILES} | sort | tr '\n' ' ')
DIFF_OK=PASS
if [[ "${our_diff}" != "${upstream_diff}" ]]; then
  DIFF_OK=FAIL
  say "CHECK DIFF_EQUALS_UPSTREAM FAIL: diffs are not byte-identical"
elif [[ "${our_files}" != "${want_files}" ]]; then
  DIFF_OK=FAIL
  say "CHECK DIFF_EQUALS_UPSTREAM FAIL: changed files '${our_files}' are not '${want_files}'"
fi
if [[ "${DIFF_OK}" != PASS ]]; then
  echo "CHECK DIFF_EQUALS_UPSTREAM FAIL" >> "${LOG}"
  say "STOP: the patched source is not exactly 3e411c0d; nothing is built"
  exit 1
fi

# --- the production files' md5s, re-measured (declaration §4 P0.1; reported, not gated) ---
for f in "${PROD_OPT}/lib/libMAT-MINERvA.so" "${PROD_OPT}/bin/runEventLoopOmniFold"; do
  if [[ -f "${f}" ]]; then echo "PROD ${f} $(md5sum "${f}" | cut -d' ' -f1)" >> "${LOG}"
  else echo "PROD ${f} MISSING" >> "${LOG}"; fi
done

# --- CHECK SOURCE_PROVENANCE (declaration §2): M does not pin the event-loop source, so the canonical tree is synced
# into B and checked against MP-1 S0's committed src_base rows; a failure STOPs before compiling. ---
mkdir -p "${B}/src/evloop"
rsync -a --exclude 'build' --exclude 'build.*' "${CANON_SRC}/" "${B}/src/evloop/"
if python3 -I "${CODE}/geanttw_provenance.py" --manifest "${CODE}/S0-src_base.sha256" --tree "${B}/src/evloop" \
     --deploy "${DEPLOY}" >&2; then
  SRC_OK=PASS
else
  SRC_OK=FAIL
fi
echo "CHECK SOURCE_PROVENANCE ${SRC_OK}" >> "${LOG}"
[[ "${SRC_OK}" == PASS ]] || { say "STOP: the event-loop source is not MP-1 S0's; nothing is built"; exit 1; }

# --- build ---
mkdir -p "${B}/build-mat-pin" "${B}/build-mat-pat" \
         "${B}/build-matminerva-pin" "${B}/build-matminerva-pat" \
         "${B}/build-evloop-pin" "${B}/build-evloop-pat" \
         "${B}/prefix-pin/lib" "${B}/prefix-pin/bin" \
         "${B}/prefix-pat/lib" "${B}/prefix-pat/bin"

# The production data trees, read through symlinks (§2, §6): lib/data, etc/MParamFiles, etc/MATFluxAndReweightFiles
for pfx in "${B}/prefix-pin" "${B}/prefix-pat"; do
  mkdir -p "${pfx}/lib" "${pfx}/etc"
  ln -s "${PROD_OPT}/lib/data" "${pfx}/lib/data"
  ln -s "${PROD_OPT}/etc/MParamFiles" "${pfx}/etc/MParamFiles"
  ln -s "${PROD_OPT}/etc/MATFluxAndReweightFiles" "${pfx}/etc/MATFluxAndReweightFiles"
done


# Build MAT once — same commit in both builds, so install into both prefixes.
say "building MAT"
for build in pin pat; do
  cd "${B}/build-mat-${build}"
  cmake "${B}/src/MAT" -DCMAKE_INSTALL_PREFIX="${B}/prefix-${build}" > cmake.log 2>&1
  make -j4 > make.log 2>&1
  make install > install.log 2>&1
  cd "${B}"
done

# Build MAT-MINERvA-pin -> prefix-pin
say "building MAT-MINERvA pin"
cd "${B}/build-matminerva-pin"
cmake "${B}/src/MAT-MINERvA-pin" -DCMAKE_INSTALL_PREFIX="${B}/prefix-pin" \
  -DMAT_DIR="${B}/prefix-pin/lib/cmake/MAT" > cmake.log 2>&1
make -j4 > make.log 2>&1
make install > install.log 2>&1
cd "${B}"

# Build MAT-MINERvA-pat -> prefix-pat
say "building MAT-MINERvA pat"
cd "${B}/build-matminerva-pat"
cmake "${B}/src/MAT-MINERvA-pat" -DCMAKE_INSTALL_PREFIX="${B}/prefix-pat" \
  -DMAT_DIR="${B}/prefix-pat/lib/cmake/MAT" > cmake.log 2>&1
make -j4 > make.log 2>&1
make install > install.log 2>&1
cd "${B}"

# runEventLoopOmniFold from the synced, provenance-checked source against each prefix. UnfoldUtils and
# GENIEXSecExtract are REQUIRED by its CMakeLists.txt:56-60: their production cmake configs are READ here, not linked
# (the production binary NEEDs only libMAT-MINERvA, libMAT and ROOT; C0a/C0e confirm the runtime opens).
for build in pin pat; do
  say "building runEventLoopOmniFold (${build})"
  cd "${B}/build-evloop-${build}"
  cmake "${B}/src/evloop" \
    -DCMAKE_INSTALL_PREFIX="${B}/prefix-${build}" \
    -DMAT_DIR="${B}/prefix-${build}/lib/cmake/MAT" \
    -DMAT-MINERvA_DIR="${B}/prefix-${build}/lib/cmake/MAT-MINERvA" \
    -DUnfoldUtils_DIR="${PROD_OPT}/lib/cmake/UnfoldUtils" \
    -DGENIEXSecExtract_DIR="${PROD_OPT}/lib/cmake/GENIEXSecExtract" > cmake.log 2>&1
  make -j4 runEventLoopOmniFold > make.log 2>&1
  cp runEventLoopOmniFold "${B}/prefix-${build}/bin/runEventLoopOmniFold"
  # the prefix's own setup.sh: the production umbrella's settings for this prefix only (no UnfoldUtils, no default)
  cat > "${B}/prefix-${build}/bin/setup.sh" <<SETUP
# geanttw prefix-${build} environment (written by geanttw_build.sh). MINERVA_PREFIX must name this prefix.
[ "\${MINERVA_PREFIX}" = "${B}/prefix-${build}" ] || { echo "MINERVA_PREFIX is not ${B}/prefix-${build}" >&2; return 1; }
export PLOTUTILSROOT="${B}/prefix-${build}/lib"
export LD_LIBRARY_PATH="${B}/prefix-${build}/lib:\${LD_LIBRARY_PATH}"
export PATH="${B}/prefix-${build}/bin:\${PATH}"
export PLOTUTILSTYPE=STANDALONE
export PLOTUTILSVERSION=ROOT6
export ROOT_INCLUDE_PATH="${B}/prefix-${build}/include/PlotUtils:${B}/prefix-${build}/include:\${ROOT_INCLUDE_PATH}"
export MPARAMFILESROOT="${B}/prefix-${build}/etc/MParamFiles"
export MPARAMFILES="${B}/prefix-${build}/etc/MParamFiles/data"
export MATFLUXANDWEIGHTFILES="${B}/prefix-${build}/etc/MATFluxAndReweightFiles"
SETUP
  cd "${B}"
done

# --- write build.log ---
sha() { sha256sum "$1" | cut -d' ' -f1; }

# SO and BIN records
for build in pin pat; do
  pfx="${B}/prefix-${build}"
  for so in "${pfx}"/lib/*.so; do
    [[ -e "${so}" ]] || continue
    echo "SO ${build} ${so} $(sha "${so}")" >> "${LOG}"
  done
  bin="${pfx}/bin/runEventLoopOmniFold"
  [[ -e "${bin}" ]] && echo "BIN ${build} ${bin} $(sha "${bin}")" >> "${LOG}"
done

# RPATH records, and CHECK RPATH_CLEAN: every RPATH/RUNPATH entry of each binary is the conda ROOT env's lib or that
# build's own prefix lib (never the production opt, never the other prefix)
RPATH_OK=PASS
for build in pin pat; do
  bin="${B}/prefix-${build}/bin/runEventLoopOmniFold"
  [[ -e "${bin}" ]] || { RPATH_OK=FAIL; continue; }
  rp=$(readelf -d "${bin}" 2>/dev/null | grep -E 'RPATH|RUNPATH' | sed 's/.*\[\(.*\)\]/\1/' | tr '\n' ':' || true)
  rp="${rp%:}"
  echo "RPATH ${build} ${bin} ${rp:-NONE}" >> "${LOG}"
  IFS=':' read -r -a entries <<< "${rp}"
  for e in ${entries[@]+"${entries[@]}"}; do   # an empty RPATH is an empty array; bash 3.2 calls that unbound
    [[ -z "${e}" || "${e}" == "${ROOT628_PREFIX}/lib" || "${e}" == "${B}/prefix-${build}/lib" ]] && continue
    RPATH_OK=FAIL
    say "CHECK RPATH_CLEAN FAIL: ${build} has RPATH entry ${e}"
  done
done
echo "CHECK RPATH_CLEAN ${RPATH_OK}" >> "${LOG}"

# CHECK records
echo "CHECK DIFF_EQUALS_UPSTREAM ${DIFF_OK}" >> "${LOG}"

# CHECK LIBMAT_IDENTICAL: each of the two libMAT.so files must match the other
pin_mat_sha=$(sha "${B}/prefix-pin/lib/libMAT.so")
pat_mat_sha=$(sha "${B}/prefix-pat/lib/libMAT.so")
if [[ "${pin_mat_sha}" == "${pat_mat_sha}" ]]; then
  echo "CHECK LIBMAT_IDENTICAL PASS" >> "${LOG}"
  LIBMAT_OK=PASS
else
  echo "CHECK LIBMAT_IDENTICAL FAIL" >> "${LOG}"
  LIBMAT_OK=FAIL
fi

# CHECK LIBMATMINERVA_DIFFER: the two libMAT-MINERvA.so files must differ
pin_mm_sha=$(sha "${B}/prefix-pin/lib/libMAT-MINERvA.so")
pat_mm_sha=$(sha "${B}/prefix-pat/lib/libMAT-MINERvA.so")
if [[ "${pin_mm_sha}" != "${pat_mm_sha}" ]]; then
  echo "CHECK LIBMATMINERVA_DIFFER PASS" >> "${LOG}"
  LIBMM_OK=PASS
else
  echo "CHECK LIBMATMINERVA_DIFFER FAIL" >> "${LOG}"
  LIBMM_OK=FAIL
fi

say "build.log written to ${LOG}"
cat "${LOG}" >&2

# Exit nonzero if any CHECK fails
if [[ "${DIFF_OK}" != "PASS" || "${LIBMAT_OK}" != "PASS" || "${LIBMM_OK}" != "PASS" || "${RPATH_OK}" != "PASS" ]]; then
  say "FAIL: one or more CHECKs failed"
  exit 1
fi
say "all CHECKs passed"
