#!/bin/bash
# W2a: build two event-loop binaries in a private namespace from IDENTICAL copies of the canonical
# MINERvA-101-Cross-Section source tree:
#   base: the copy as-is (its tracked files must equal this commit's tracked copies);
#   mod:  the copy + publication/w2/src/event/RecoilResponseUniverse.h + the W2 patch.
# Nothing in the canonical checkout is written. Run on a Perlmutter login node:
#   bash publication/w2/build_w2.sh <W2-repo-checkout> <namespace>
# The checkout must be a clean clone of study/w2-recoil-response-20261006.
set -o pipefail   # NOT set -u: conda activation references unset variables under nounset
REPO_W2="${1:?usage: build_w2.sh <W2 repo checkout> <namespace>}"
NS="${2:?usage: build_w2.sh <W2 repo checkout> <namespace>}"
CANON=/pscratch/sd/j/josephrb/MINERvA-OmniFold
CANON_SRC="${CANON}/MINERvA101/MINERvA-101-Cross-Section"
OPT="${CANON}/MINERvA101/opt"

[[ -z "$(git -C "${REPO_W2}" status --porcelain)" ]] || { echo "[build] ABORT: ${REPO_W2} is not clean"; exit 2; }
echo "[build] W2 commit $(git -C "${REPO_W2}" rev-parse HEAD)"

# The canonical tree's tracked files must equal the W2 commit's tracked copies (which equal main's).
for f in runEventLoopOmniFold.cpp event/CVUniverse.h cuts/MaxPtMu.h CMakeLists.txt; do
  a=$(sha256sum "${CANON_SRC}/${f}" | cut -d' ' -f1)
  b=$(sha256sum "${REPO_W2}/MINERvA101/MINERvA-101-Cross-Section/${f}" | cut -d' ' -f1)
  [[ "$a" == "$b" ]] || { echo "[build] ABORT: ${f} differs between canonical (${a}) and the W2 commit (${b})"; exit 3; }
done

source "${CANON}/setup_salloc_env.sh" >/dev/null 2>&1
mkdir -p "${NS}/build"
for v in base mod; do
  SRC="${NS}/build/src_${v}"
  [[ -e "${SRC}" ]] && { echo "[build] ABORT: ${SRC} exists; use a fresh namespace"; exit 4; }
  rsync -a --exclude 'build' --exclude 'build.*' "${CANON_SRC}/" "${SRC}/"
  if [[ "${v}" == mod ]]; then
    cp "${REPO_W2}/publication/w2/src/event/RecoilResponseUniverse.h" "${SRC}/event/"
    (cd "${SRC}" && patch -p1 --forward < "${REPO_W2}/publication/w2/src/runEventLoopOmniFold-recoil-response.patch") \
      || { echo "[build] ABORT: patch failed"; exit 5; }
  fi
  BLD="${NS}/build/bld_${v}"; PREFIX="${NS}/build/opt_${v}"
  mkdir -p "${BLD}" && cd "${BLD}" || exit 6
  cmake "${SRC}" -DCMAKE_INSTALL_PREFIX="${PREFIX}" \
    -DMAT_DIR="${OPT}/lib/cmake/MAT" -DMAT-MINERvA_DIR="${OPT}/lib/cmake/MAT-MINERvA" \
    -DUnfoldUtils_DIR="${OPT}/lib/cmake/UnfoldUtils" -DGENIEXSecExtract_DIR="${OPT}/lib/cmake/GENIEXSecExtract" \
    > cmake.log 2>&1 || { echo "[build] ABORT: cmake ${v} failed (see ${BLD}/cmake.log)"; exit 7; }
  make -j 8 runEventLoopOmniFold > make.log 2>&1 || { echo "[build] ABORT: make ${v} failed (see ${BLD}/make.log)"; exit 8; }
  echo "[build] ${v}: ${BLD}/runEventLoopOmniFold md5 $(md5sum "${BLD}/runEventLoopOmniFold" | cut -d' ' -f1)"
done
diff -q "${NS}/build/src_base/runEventLoopOmniFold.cpp" "${CANON_SRC}/runEventLoopOmniFold.cpp" && echo "[build] base source == canonical"
echo "[build] done"
