#!/bin/bash
# EVW2D: the cleanup, on a Perlmutter login node, in the foreground, only after the post passed and the director's GO
# for it. It requires $LANE/post.pass, which the post publishes last and only on PASS, to name this job, the bound
# config digest and the current products' SHA256SUMS digest. It runs `evw2d.py cleanup --out $LANE/out` (the declaration's §7): evw2d.py refuses unless the product is
# accepted and bound to this config digest, and each staged name is the file the run verified with the pinned digest;
# only then it deletes the two staged copies, appending a row per file to $LANE/deletions.tsv. What is removed, exactly:
# $LANE/stage/runEventLoopOmniFold_MEFHC.root and $LANE/stage/runEventLoopMC_MEFHC.root, the two names evw2d.py's
# staged() builds from the bound config.json, each only if it is the file run.json's "staged" record verified (inode,
# size, mtime, mode) with the pinned digest. No glob; never the products, nothing under $LANE/out, and no directory.
# This script itself removes nothing. It writes only $LANE/cleanup (created exclusively) and $LANE/cleanup.tar.gz; it
# submits and cancels nothing. Launched from a private /dev/shm copy of itself, whose path is $1 (only read); the
# launcher's wrapper deletes that copy after it exits.
SELF=$1
LANE=__LANE_ROOT__
CFG_SHA=__CONFIG_SHA256__
K=$LANE/cleanup
DM=$LANE/deploy_M
DC=$LANE/deploy_C
set -o noclobber
bail() { echo "STOP: $*"; exit 9; }
case "$CFG_SHA" in *__*) bail "the config digest is not filled in";; esac
[ -d "$LANE" ] && [ ! -L "$LANE" ] && [ "$(cd "$LANE" && pwd -P)" = "$LANE" ] || bail "$LANE is not a real directory"
PP=$LANE/post.pass
[ -f "$PP" ] && [ ! -L "$PP" ] || bail "no post.pass: the post did not pass"
job=$(cat "$LANE/logs/evw2d.jobid" 2>/dev/null)
case "$job" in *[!0-9]*|"") bail "jobid '$job'";; esac
sums=$(sha256sum "$LANE/out/SHA256SUMS" 2>/dev/null | cut -d' ' -f1)
want=$(printf 'job=%s\nconfig_sha256=%s\nproducts_SHA256SUMS_sha256=%s' "$job" "$CFG_SHA" "$sums")
[ -n "$sums" ] && [ "$(cat "$PP")" = "$want" ] || bail "post.pass does not name this job, config and products"
ST=$LANE/stage   # evw2d.py resolves the staging root, so this script first requires it to be the real directory
[ -d "$ST" ] && [ ! -L "$ST" ] && [ "$(cd "$ST" && pwd -P)" = "$ST" ] || bail "$ST is not the real staging directory"
for f in "$ST/runEventLoopOmniFold_MEFHC.root" "$ST/runEventLoopMC_MEFHC.root"; do
  [ -f "$f" ] && [ ! -L "$f" ] || bail "$f is not a regular file at its exact path"
done
for f in "$K" "$LANE/cleanup.tar.gz" "$LANE/cleanup.tar.gz.partial"; do [ ! -e "$f" ] && [ ! -L "$f" ] || bail "$f exists"; done
q=$(squeue --me -h -o '%j') || bail "squeue did not answer"
[ -z "$(printf '%s\n' "$q" | grep -E '^evw2d$')" ] || bail "an evw2d job is queued or running"
mkdir "$K" || bail "mkdir"
exec > "$K/cleanup.log" 2>&1
echo "node $(hostname) $(date -u +%FT%TZ) cleanup sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$K/evw2d_cleanup.sh"
ls -la "$LANE/stage" > "$K/stage-before.txt" 2>&1
( set +o noclobber   # the setup runs as in the job; this script's own redirects stay exclusive outside it
  source "$DM/setup_salloc_env.sh" > "$K/env.log" 2>&1 || exit 96
  [ "$(command -v python3)" = "$HOME/.conda/envs/root_6_28/bin/python3" ] || exit 98
  cd "$K" || exit 95
  PYTHONDONTWRITEBYTECODE=1 python3 -B "$DC/2d-unfolding/evw2d/evw2d.py" --config-sha256 "$CFG_SHA" cleanup \
    --out "$LANE/out" > "$K/cleanup.json" 2> "$K/cleanup.err" )
rc=$?
echo "evw2d.py cleanup rc=$rc"; cat "$K/cleanup.json" "$K/cleanup.err"
ls -la "$LANE/stage" > "$K/stage-after.txt" 2>&1
if [ -f "$LANE/deletions.tsv" ] && [ ! -L "$LANE/deletions.tsv" ]; then
  cp -p "$LANE/deletions.tsv" "$K/" || { echo "FAILED: copying deletions.tsv"; [ "$rc" = 0 ] && rc=5; }
elif [ "$rc" = 0 ]; then
  echo "FAILED: evw2d.py cleanup returned 0 and there is no deletions.tsv"; rc=5
fi
( cd "$K" && find . -type f ! -path ./SHA256SUMS ! -path ./cleanup.log | sort | xargs sha256sum > SHA256SUMS ) || { echo "FAILED: the manifest"; [ "$rc" = 0 ] && rc=5; }
echo "cleanup rc=$rc $(date -u +%FT%TZ)"
tar czf "$LANE/cleanup.tar.gz.partial" -C "$LANE" cleanup && mv -- "$LANE/cleanup.tar.gz.partial" "$LANE/cleanup.tar.gz" \
  || { echo "FAILED: the archive"; [ "$rc" = 0 ] && rc=5; }
exit $rc
