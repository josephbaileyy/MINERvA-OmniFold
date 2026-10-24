#!/bin/bash
# RE-2 part B preflight, on a DTN (dtn01.nersc.gov; no Slurm charge):  bash re2b_dtn_hash.sh <deploy> <declared sha>
# 1. Stages the CV omnifile and the 10 active laterals from CFS to $O/inputs: a compute node reads CFS through DVS
#    at ~10 MB/s (RE2-J0-REPORT.md D1), a DTN at ~1.5 GB/s. Each copy is hashed and must equal its declared digest
#    (the CFS file's own), so the copy holds the declared bytes; it is then made read-only.
# 2. Hashes the 171 GB universe omnifile in place: the full hash before J2 (part A §3).
# It writes $O/preflight/inputs.stat ("sha256 size mtime inode path", one row per input the jobs stat-check), with
# each stat taken before and after its hash and required to agree. It refuses an existing record or staged copy.
set -eo pipefail
C=$(cd "$1" && pwd); RE2_SHA=$2
[ "$(git -C "$C" rev-parse HEAD)" = "$RE2_SHA" ] && [ -z "$(git -C "$C" status --porcelain)" ] \
    || { echo "deploy $C is not a clean checkout at $RE2_SHA"; exit 2; }
source "$C/docs/orchestration/state/2d-closeout/stageF/methods/re2/run/launch/re2b_env.sh"
case "$(hostname)" in dtn*) ;; *) echo "run on a DTN, not $(hostname)"; exit 2 ;; esac
mkdir -p "$O/preflight"
[ ! -e "$STATS" ] || { echo "$STATS exists; a new record needs the director"; exit 3; }
[ ! -e "$O/inputs" ] || { echo "$O/inputs exists; a new staging needs the director"; exit 3; }
re2_check "$CFS_ACT/SHA256SUMS" "$LAT_SUMS_SHA"
[ "$(re2b_lateral_sha runEventLoopOmniFold_5D_MEFHC_active_BeamAngleX_0.root)" = "$LATBAX0_SHA" ] \
    || { echo "SHA256SUMS disagrees with part A's BeamAngleX_0 digest"; exit 5; }
mkdir -p "$ACT"
list=("$CFS_CV $CV $CV_SHA" "- $UNI ${UNI_SHA_OF[uni]}")      # source (- = hashed in place), path, digest
for lat in $LATERALS; do
    f=runEventLoopOmniFold_5D_MEFHC_active_$lat.root
    want=$(re2b_lateral_sha "$f"); [ ${#want} = 64 ] || { echo "no SHA256SUMS row for $f"; exit 5; }
    list+=("$CFS_ACT/$f $ACT/$f $want")
done
echo "[re2b-dtn] start $(date -u +%FT%TZ) host=$(hostname) inputs=${#list[@]}"
one() {  # one <source or -> <path> <want>: stage if asked, hash, and print the record row (or fail, rc 4)
    local src=$1 path=$2 want=$3 before after got
    if [ "$src" != - ]; then
        cp "$src" "$path.partial" && mv "$path.partial" "$path" || { echo "copy of $src failed" >&2; return 4; }
    fi
    before=$(stat -c '%s %Y %i' "$path")
    got=$(sha256sum "$path" | cut -d' ' -f1)
    after=$(stat -c '%s %Y %i' "$path")
    [ "$before" = "$after" ] || { echo "$path changed while hashed" >&2; return 4; }
    [ "$got" = "$want" ] || { echo "$path sha256 $got != $want" >&2; return 4; }
    [ "$src" = - ] || chmod a-w "$path"
    echo "$got $before $path"
}
tmp=$O/preflight/inputs.stat.partial; : > "$tmp"
pids=(); i=0
for item in "${list[@]}"; do   # four at a time: sha256sum is CPU-bound near 0.5 GB/s; CFS gives > 1 GB/s here
    set -- $item
    one "$1" "$2" "$3" > "$O/preflight/part.$i" & pids+=($!); i=$((i + 1))
    if [ $(( i % 4 )) = 0 ]; then for p in "${pids[@]}"; do wait "$p" || exit 4; done; pids=(); fi
done
for p in "${pids[@]}"; do wait "$p" || exit 4; done
for j in $(seq 0 $((i - 1))); do cat "$O/preflight/part.$j"; rm "$O/preflight/part.$j"; done > "$tmp"
[ "$(grep -c . "$tmp")" = "${#list[@]}" ] || { echo "record has $(grep -c . "$tmp") rows, not ${#list[@]}"; exit 4; }
mv "$tmp" "$STATS"; chmod a-w "$STATS"
echo "[re2b-dtn] end $(date -u +%FT%TZ)"; sha256sum "$STATS"; du -sh "$O/inputs"
