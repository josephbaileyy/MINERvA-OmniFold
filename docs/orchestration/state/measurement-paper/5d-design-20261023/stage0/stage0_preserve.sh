#!/bin/bash
# 5D design Stage 0, Part P (STAGE0-DECLARATION.md): preserve the Stage 0 and 0c inputs on HPSS before the pscratch purge.
# Reads the 425 inventoried pscratch files; writes one uncompressed tar beside them, one HPSS copy, and a retrieval check.
# Runs on a Perlmutter login node (no Slurm job, no node-h). Never modifies or deletes an inventoried file.
#   bash stage0_preserve.sh <INVENTORY.sha256> <work dir on pscratch> <HPSS dir>
set -o pipefail   # NOT set -u
INV="${1:?inventory}"; WORK="${2:?work dir}"; HDIR="${3:?hpss dir}"
TAR="${WORK}/stage0-inputs.tar"; LOG="${WORK}/preserve.log"
mkdir -p "${WORK}" "${WORK}/retrieve"
stamp() { date -u +%FT%TZ; }
{
  echo "[P] $(stamp) start host=$(hostname)"
  # 1. every inventoried file still has its recorded sha256 (refuse otherwise)
  sha256sum --quiet -c "${INV}" || { echo "[P] STOP: an input no longer matches the inventory"; exit 3; }
  echo "[P] $(stamp) inventory verified: $(wc -l < "${INV}") files"
  # 2. one uncompressed tar of exactly the inventoried paths (absolute names kept, leading / stripped by tar)
  awk '{print $2}' "${INV}" > "${WORK}/paths.list"
  tar -cf "${TAR}" -T "${WORK}/paths.list" || { echo "[P] STOP: tar failed"; exit 4; }
  [ "$(tar -tf "${TAR}" | wc -l)" -eq "$(wc -l < "${INV}")" ] || { echo "[P] STOP: tar member count differs"; exit 4; }
  sha256sum "${TAR}" > "${TAR}.sha256"; echo "[P] $(stamp) tar $(cat "${TAR}.sha256") bytes=$(stat -c %s "${TAR}")"
  # 3. copy to HPSS, create its stored hash (hsi hashcreate, as earlier archives did), then verify the stored copy
  hsi -q "mkdir -p ${HDIR}" || true
  hsi -q "put ${TAR} : ${HDIR}/stage0-inputs.tar" || { echo "[P] STOP: hsi put failed"; exit 5; }
  hsi -q "hashcreate ${HDIR}/stage0-inputs.tar" || { echo "[P] STOP: hashcreate failed"; exit 6; }
  hsi -q "put ${TAR}.sha256 : ${HDIR}/stage0-inputs.tar.sha256" || { echo "[P] STOP: hsi put (sha) failed"; exit 5; }
  hsi -q "put ${INV} : ${HDIR}/INVENTORY.sha256" || { echo "[P] STOP: hsi put (inventory) failed"; exit 5; }
  hsi -q "hashverify ${HDIR}/stage0-inputs.tar" || { echo "[P] STOP: hashverify failed"; exit 6; }
  hsi -q "ls -l ${HDIR}"
  # 4. retrieve it back and compare byte for byte by sha256; then remove only the retrieved copy
  hsi -q "get ${WORK}/retrieve/stage0-inputs.tar : ${HDIR}/stage0-inputs.tar" || { echo "[P] STOP: hsi get failed"; exit 7; }
  a=$(cut -d' ' -f1 "${TAR}.sha256"); b=$(sha256sum "${WORK}/retrieve/stage0-inputs.tar" | cut -d' ' -f1)
  [ "${a}" = "${b}" ] || { echo "[P] STOP: retrieved copy differs (${b})"; exit 8; }
  rm -f "${WORK}/retrieve/stage0-inputs.tar"
  echo "[P] $(stamp) PASS: HPSS copy verified by hashverify and by retrieval (${a})"
} 2>&1 | tee -a "${LOG}"
exit "${PIPESTATUS[0]}"
