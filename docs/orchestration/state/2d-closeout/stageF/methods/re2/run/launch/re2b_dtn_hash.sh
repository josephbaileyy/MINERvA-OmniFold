#!/bin/bash
# RE-2 part B preflight, on a DTN (dtn01.nersc.gov; no Slurm charge):  re2b_dtn_hash.sh <deploy> <declared sha>
# Hashes, once, every large input the jobs would otherwise hash over a compute node's slow CFS mount (RE2-J0-REPORT
# D1): the CV omnifile, the 10 active laterals and the 171 GB universe omnifile (the full hash before J2, part A
# §3). Each must equal its declared digest. It writes $O/preflight/inputs.stat ("sha256 size mtime inode path"),
# with the stat taken before and after each hash and required to agree, and refuses to overwrite a record.
set -eo pipefail
C=$(cd "$1" && pwd); RE2_SHA=$2
[ "$(git -C "$C" rev-parse HEAD)" = "$RE2_SHA" ] && [ -z "$(git -C "$C" status --porcelain)" ] \
    || { echo "deploy $C is not a clean checkout at $RE2_SHA"; exit 2; }
source "$C/docs/orchestration/state/2d-closeout/stageF/methods/re2/run/launch/re2b_env.sh"
case "$(hostname)" in dtn*) ;; *) echo "run on a DTN, not $(hostname)"; exit 2 ;; esac
mkdir -p "$O/preflight"
[ ! -e "$STATS" ] || { echo "$STATS exists; a new record needs the director"; exit 3; }
re2_check "$ACT/SHA256SUMS" 73775251f377a35b86c5d9433d1db63d65267525b9261f773064a1e9d17764f6
list=("$CV $CV_SHA" "$UNI ${UNI_SHA_OF[uni]}")
for lat in BeamAngleX_0 BeamAngleX_1 BeamAngleY_0 BeamAngleY_1 MuonResolution_0 MuonResolution_1 \
           Muon_Energy_MINERvA_0 Muon_Energy_MINERvA_1 Muon_Energy_MINOS_0 Muon_Energy_MINOS_1; do
    f=runEventLoopOmniFold_5D_MEFHC_active_$lat.root
    want=$(re2b_lateral_sha "$f"); [ ${#want} = 64 ] || { echo "no SHA256SUMS row for $f"; exit 5; }
    list+=("$ACT/$f $want")
done
[ "$(re2b_lateral_sha runEventLoopOmniFold_5D_MEFHC_active_BeamAngleX_0.root)" = "$LATBAX0_SHA" ] \
    || { echo "SHA256SUMS disagrees with part A's BeamAngleX_0 digest"; exit 5; }
tmp=$O/preflight/inputs.stat.partial; : > "$tmp"
echo "[re2b-dtn] start $(date -u +%FT%TZ) host=$(hostname) files=${#list[@]}"
hash_one() {  # hash_one <path> <want>: one record line, or a failure message on stderr and rc 4
    local before after got
    before=$(stat -c '%s %Y %i' "$1")
    got=$(sha256sum "$1" | cut -d' ' -f1)
    after=$(stat -c '%s %Y %i' "$1")
    [ "$before" = "$after" ] || { echo "$1 changed while hashed" >&2; return 4; }
    [ "$got" = "$2" ] || { echo "$1 sha256 $got != $2" >&2; return 4; }
    echo "$got $before $1"
}
pids=(); i=0
for item in "${list[@]}"; do   # four at a time: sha256sum is CPU-bound near 0.5 GB/s; CFS gives > 1 GB/s here
    set -- $item
    hash_one "$1" "$2" > "$O/preflight/part.$i" & pids+=($!); i=$((i + 1))
    if [ $(( i % 4 )) = 0 ]; then for p in "${pids[@]}"; do wait "$p" || exit 4; done; pids=(); fi
done
for p in "${pids[@]}"; do wait "$p" || exit 4; done
for j in $(seq 0 $((i - 1))); do cat "$O/preflight/part.$j"; rm "$O/preflight/part.$j"; done > "$tmp"
[ "$(grep -c . "$tmp")" = "${#list[@]}" ] || { echo "record has $(grep -c . "$tmp") rows, not ${#list[@]}"; exit 4; }
mv "$tmp" "$STATS"; chmod a-w "$STATS"
echo "[re2b-dtn] end $(date -u +%FT%TZ)"; sha256sum "$STATS"
