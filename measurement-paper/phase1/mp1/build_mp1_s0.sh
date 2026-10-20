#!/bin/bash
# MP1-A S0: build two event-loop binaries in a private namespace from IDENTICAL copies of the canonical
# MINERvA-101-Cross-Section source tree (mirrors publication/w2/build_w2.sh, with W2 review F9 closed):
#   base: the copy as-is;
#   mod:  the copy + measurement-paper/phase1/mp1/src/event/SpeciesResponseUniverse.h + the MP1 patch.
# Nothing in the canonical checkout is written. Run on a Perlmutter login node (as W2 was built):
#   bash <deploy>/measurement-paper/phase1/mp1/build_mp1_s0.sh <deploy> <namespace>
# <deploy> holds the reviewed files at their repository paths plus DEPLOY.sha256 (made where they were written;
# the files are not yet committed, so their digests stand in for a commit). <namespace> must be under
# /pscratch/sd/j/josephrb/measurement-paper/phase1/mp1/ and have no build/ yet. Every input and output is hashed
# into <namespace>/build/MANIFEST.sha256.
set -o pipefail   # NOT set -u: conda activation references unset variables under nounset
DEPLOY="${1:?usage: build_mp1_s0.sh <deploy> <namespace>}"
NS="${2:?usage: build_mp1_s0.sh <deploy> <namespace>}"
CANON=/pscratch/sd/j/josephrb/MINERvA-OmniFold
CANON_SRC="${CANON}/MINERvA101/MINERvA-101-Cross-Section"
OPT="${CANON}/MINERvA101/opt"
MP1="${DEPLOY}/measurement-paper/phase1/mp1"
ROOT_NS=/pscratch/sd/j/josephrb/measurement-paper/phase1/mp1/

case "${NS}" in "${ROOT_NS}"?*) ;; *) echo "[build] ABORT: namespace must be under ${ROOT_NS}"; exit 2 ;; esac
[[ -e "${NS}/build" ]] && { echo "[build] ABORT: ${NS}/build exists; use a fresh namespace"; exit 2; }
(cd "${DEPLOY}" && sha256sum --quiet -c DEPLOY.sha256) || { echo "[build] ABORT: deploy digests do not match"; exit 2; }
echo "[build] deploy ${DEPLOY} DEPLOY.sha256 $(sha256sum "${DEPLOY}/DEPLOY.sha256" | cut -d' ' -f1) host $(hostname) $(date -u +%FT%TZ)"

# Canonical inputs, pinned: the four tracked files equal origin/main 46d1ec5a's blobs (b7e1edbc, 04906da5, 91e7fce4,
# 4401b2d9); the two untracked compiled inputs (W2 review F9) were read 2026-10-19.
declare -A PIN=(
  [runEventLoopOmniFold.cpp]=57792e42fe3f5a663016f94b91a5631fc50349135c92b35a08eaefcb85812be3
  [event/CVUniverse.h]=900d7368d6184d503399bd99c0fd30085212df0327b8be374182495b85a3677d
  [cuts/MaxPtMu.h]=ae4adeb3a5ff0e2f8cab46a4dd9dc40d7b42da6b936311d776fdb7612e2d73ca
  [CMakeLists.txt]=d77791ad0e866704d70ab5cf3db0c0c3c7a5aed0218c144c20f86081ad6814b0
  [cuts/MaxPzMu.h]=c50f6b5ae4e95e85de3f7a50b704232ead767231c1604951a597e9faafb3e56c
  [systematics/Systematics.h]=1bdfa4f028e7e5f3d4e39a60d2cadc0c05b366fd12ff345d5183177a9b555086
)
for f in "${!PIN[@]}"; do
  a=$(sha256sum "${CANON_SRC}/${f}" | cut -d' ' -f1)
  [[ "$a" == "${PIN[$f]}" ]] || { echo "[build] ABORT: canonical ${f} is ${a}, pinned ${PIN[$f]}"; exit 3; }
done

source "${CANON}/setup_salloc_env.sh" >/dev/null 2>&1
mkdir -p "${NS}/build" || exit 4
MAN="${NS}/build/MANIFEST.sha256"
{ echo "# deploy DEPLOY.sha256 $(sha256sum "${DEPLOY}/DEPLOY.sha256" | cut -d' ' -f1)"
  sha256sum "${MP1}/src/event/SpeciesResponseUniverse.h" "${MP1}/src/runEventLoopOmniFold-species-response.patch" \
            "${MP1}/build_mp1_s0.sh"
  sha256sum "${OPT}"/lib/*.so                       # the installed MAT/UnfoldUtils libraries the binaries link
} > "${MAN}" || exit 4

for v in base mod; do
  SRC="${NS}/build/src_${v}"
  rsync -a --exclude 'build' --exclude 'build.*' "${CANON_SRC}/" "${SRC}/" || { echo "[build] ABORT: rsync ${v}"; exit 5; }
  if [[ "${v}" == mod ]]; then
    cp "${MP1}/src/event/SpeciesResponseUniverse.h" "${SRC}/event/" || exit 5
    (cd "${SRC}" && patch -p1 --forward < "${MP1}/src/runEventLoopOmniFold-species-response.patch") \
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
  (cd "${SRC}" && find . -type f ! -path './.git/*' -print0 | sort -z | xargs -0 sha256sum) \
    | sed "s|  \./|  src_${v}/|" >> "${MAN}"
  sha256sum "${BLD}/runEventLoopOmniFold" >> "${MAN}"
  md5sum "${BLD}/runEventLoopOmniFold" >> "${MAN}"
done

# The two trees may differ ONLY by the header and the patched event loop; base must equal canonical.
cmp -s "${NS}/build/src_base/runEventLoopOmniFold.cpp" "${CANON_SRC}/runEventLoopOmniFold.cpp" \
  || { echo "[build] ABORT: base source differs from canonical"; exit 9; }
DIFFS=$(diff -rq "${NS}/build/src_base" "${NS}/build/src_mod" | sort)
EXPECT=$(printf '%s\n' "Files ${NS}/build/src_base/runEventLoopOmniFold.cpp and ${NS}/build/src_mod/runEventLoopOmniFold.cpp differ" \
                       "Only in ${NS}/build/src_mod/event: SpeciesResponseUniverse.h" | sort)
[[ "${DIFFS}" == "${EXPECT}" ]] || { echo "[build] ABORT: unexpected source differences:"; echo "${DIFFS}"; exit 9; }
echo "[build] base == canonical; mod differs only by the header and the patch"
echo "[build] manifest ${MAN} ($(wc -l < "${MAN}") lines); done"
