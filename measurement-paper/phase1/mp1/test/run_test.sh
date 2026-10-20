#!/bin/bash
# Compile and run the SpeciesResponseUniverse unit test locally (no MAT/ROOT): the header against a mock
# CVUniverse, and the convention parser cut from the patched event loop.
#   bash measurement-paper/phase1/mp1/test/run_test.sh <repo root> <scratch dir>
set -o pipefail
REPO="${1:?usage: run_test.sh <repo root> <scratch dir>}"
TMP="${2:?usage: run_test.sh <repo root> <scratch dir>}"
MP1="${REPO}/measurement-paper/phase1/mp1"
CANON_SRC="${REPO}/MINERvA101/MINERvA-101-Cross-Section"
[[ -e "${TMP}/src" ]] && { echo "[test] ${TMP}/src exists; use a fresh scratch dir"; exit 2; }
mkdir -p "${TMP}/src" || exit 2
cp "${CANON_SRC}/runEventLoopOmniFold.cpp" "${TMP}/src/" || exit 2
(cd "${TMP}/src" && patch -p1 --forward --quiet < "${MP1}/src/runEventLoopOmniFold-species-response.patch") \
  || { echo "[test] patch failed"; exit 3; }
sed -n '/^inline bool ParseSpeciesResponseConventions/,/^}/p' "${TMP}/src/runEventLoopOmniFold.cpp" \
  > "${TMP}/parser_extracted.inc"
[[ -s "${TMP}/parser_extracted.inc" ]] || { echo "[test] parser not found in the patched source"; exit 3; }
mkdir -p "${TMP}/inc/event"
cp "${MP1}/src/event/SpeciesResponseUniverse.h" "${TMP}/inc/event/"
c++ -std=c++14 -Wall -Wextra -Werror -I "${MP1}/test/mock" -I "${TMP}/inc" -I "${TMP}" \
  "${MP1}/test/test_species_universe.cpp" -o "${TMP}/test_species_universe" || { echo "[test] compile failed"; exit 4; }
"${TMP}/test_species_universe" "${TMP}"
