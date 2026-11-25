#!/bin/bash
# EVW2D: the cleanup, on a Perlmutter login node, in the foreground, only after the post passed and the director's GO
# for it. It runs `evw2d.py cleanup --out $LANE/out` (the declaration's §7): evw2d.py refuses unless the product is
# accepted and bound to this config digest, and each staged name is the file the run verified with the pinned digest;
# only then it deletes the two staged copies, appending a row per file to $LANE/deletions.tsv. This script writes only
# $LANE/cleanup (created exclusively) and $LANE/cleanup.tar.gz; it submits and cancels nothing. Launched from a private
# /dev/shm copy of itself, whose path is $1; it deletes that copy at exit.
SELF=$1
LANE=__LANE_ROOT__
CFG_SHA=__CONFIG_SHA256__
K=$LANE/cleanup
DM=$LANE/deploy_M
DC=$LANE/deploy_C
set -o noclobber
bail() { echo "STOP: $*"; rm -f -- "$SELF"; exit 9; }
case "$CFG_SHA" in *__*) bail "the config digest is not filled in";; esac
[ -d "$LANE" ] && [ ! -L "$LANE" ] && [ "$(cd "$LANE" && pwd -P)" = "$LANE" ] || bail "$LANE is not a real directory"
[ -f "$LANE/post/verify.txt" ] && [ "$(cat "$LANE/post/verify.txt")" = PASS ] || bail "the post did not verify the products"
for f in "$K" "$LANE/cleanup.tar.gz"; do [ ! -e "$f" ] && [ ! -L "$f" ] || bail "$f exists"; done
q=$(squeue --me -h -o '%j') || bail "squeue did not answer"
[ -z "$(printf '%s\n' "$q" | grep -E '^evw2d$')" ] || bail "an evw2d job is queued or running"
mkdir "$K" || bail "mkdir"
exec > "$K/cleanup.log" 2>&1
echo "node $(hostname) $(date -u +%FT%TZ) cleanup sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$K/evw2d_cleanup.sh"
ls -la "$LANE/stage" > "$K/stage-before.txt" 2>&1
( source "$DM/setup_salloc_env.sh" > "$K/env.log" 2>&1 || exit 96
  cd "$K" || exit 95
  PYTHONDONTWRITEBYTECODE=1 python3 -B "$DC/2d-unfolding/evw2d/evw2d.py" --config-sha256 "$CFG_SHA" cleanup \
    --out "$LANE/out" > "$K/cleanup.json" 2> "$K/cleanup.err" )
rc=$?
echo "evw2d.py cleanup rc=$rc"; cat "$K/cleanup.json" "$K/cleanup.err"
ls -la "$LANE/stage" > "$K/stage-after.txt" 2>&1
[ -f "$LANE/deletions.tsv" ] && [ ! -L "$LANE/deletions.tsv" ] && cp -p "$LANE/deletions.tsv" "$K/"
( cd "$K" && find . -type f ! -path ./SHA256SUMS ! -path ./cleanup.log | sort | xargs sha256sum > SHA256SUMS )
echo "cleanup rc=$rc $(date -u +%FT%TZ)"
tar czf "$LANE/cleanup.tar.gz" -C "$LANE" cleanup
rm -f -- "$SELF"
exit $rc
