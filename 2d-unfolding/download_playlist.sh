#!/bin/bash
# Download a MINERvA ME FHC OpenData playlist from FNAL via xrootd.
#
# Usage: ./download_playlist.sh <playlist>
#   playlist: one of 1A, 1B, 1C, 1D, 1E, 1F, 1G, 1L, 1M, 1N, 1O, 1P
#
# What it does:
#   1. Lists MC and Data directories on fndca1.fnal.gov via xrdfs ls.
#   2. xrdcp's each file to /pscratch/sd/j/josephrb/minerva/minerva_large_files/,
#      preserving the {MC/StandardMC/PlaylistX, Data/PlaylistX} directory tree.
#   3. Writes local-path manifests to /pscratch/sd/j/josephrb/MINERvA101/Doc_tmp/
#      named ${PLAYLIST}_MC.txt and ${PLAYLIST}_Data.txt for the event loop.
#
# Resumable: if the local file already exists and has non-zero size, skip it.
# (Size-vs-remote check is expensive over xrootd; re-downloading a truncated
# file is the pathological case. Pass --force to re-download everything.)

set -euo pipefail

PLAYLIST="${1:?usage: $0 <1A|1B|...|1P>}"
FORCE="${2:-}"

REMOTE_HOST="root://fndca1.fnal.gov:1095"
REMOTE_BASE="/pnfs/fnal.gov/usr/minerva/persistent/OpenData/MediumEnergy_FHC"
LOCAL_BASE="/pscratch/sd/j/josephrb/minerva/minerva_large_files"
MANIFEST_DIR="/pscratch/sd/j/josephrb/MINERvA101/Doc_tmp"

MC_REMOTE="${REMOTE_BASE}/MC/StandardMC/Playlist${PLAYLIST}"
DATA_REMOTE="${REMOTE_BASE}/Data/Playlist${PLAYLIST}"
MC_LOCAL="${LOCAL_BASE}/MC/StandardMC/Playlist${PLAYLIST}"
DATA_LOCAL="${LOCAL_BASE}/Data/Playlist${PLAYLIST}"

mkdir -p "${MC_LOCAL}" "${DATA_LOCAL}" "${MANIFEST_DIR}"

echo "[$(date -u '+%F %T UTC')] Starting download of playlist ${PLAYLIST}"
echo "  MC remote  : ${REMOTE_HOST}${MC_REMOTE}"
echo "  Data remote: ${REMOTE_HOST}${DATA_REMOTE}"
echo "  MC local   : ${MC_LOCAL}"
echo "  Data local : ${DATA_LOCAL}"

download_dir() {
    local kind="$1" remote_dir="$2" local_dir="$3" manifest="$4"
    echo "[$(date -u '+%F %T UTC')] === ${kind} ==="

    # xrdfs ls returns absolute remote paths, one per line.
    local filelist
    filelist=$(xrdfs "${REMOTE_HOST}" ls "${remote_dir}")
    local n_total
    n_total=$(echo "${filelist}" | grep -c '\.root$' || true)
    echo "  ${n_total} remote .root files"

    : > "${manifest}"
    local i=0
    local n_skipped=0
    local n_downloaded=0
    while read -r remote_path; do
        [[ "${remote_path}" == *.root ]] || continue
        i=$((i + 1))
        local fname
        fname=$(basename "${remote_path}")
        local local_path="${local_dir}/${fname}"

        if [[ -s "${local_path}" && "${FORCE}" != "--force" ]]; then
            n_skipped=$((n_skipped + 1))
        else
            # -f: force overwrite;  -N: no checksum
            # (omit --parallel: xrdcp picks a sensible default; -N speeds this up)
            xrdcp -f -N "${REMOTE_HOST}${remote_path}" "${local_path}"
            n_downloaded=$((n_downloaded + 1))
        fi

        echo "${local_path}" >> "${manifest}"

        # Progress heartbeat every 25 files
        if ((i % 25 == 0)); then
            echo "[$(date -u '+%F %T UTC')] ${kind}: ${i}/${n_total} "\
"(downloaded=${n_downloaded}, skipped=${n_skipped})"
        fi
    done <<< "${filelist}"

    echo "[$(date -u '+%F %T UTC')] ${kind}: done. "\
"downloaded=${n_downloaded}, skipped=${n_skipped}, total=${i}"
    echo "  manifest: ${manifest}"
}

download_dir "MC"   "${MC_REMOTE}"   "${MC_LOCAL}"   "${MANIFEST_DIR}/${PLAYLIST}_MC.txt"
download_dir "Data" "${DATA_REMOTE}" "${DATA_LOCAL}" "${MANIFEST_DIR}/${PLAYLIST}_Data.txt"

echo "[$(date -u '+%F %T UTC')] Playlist ${PLAYLIST} complete."
du -sh "${MC_LOCAL}" "${DATA_LOCAL}"
