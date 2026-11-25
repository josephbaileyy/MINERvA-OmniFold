#!/bin/bash
# EVW2D: the post, on a Perlmutter login node, in the foreground, after the job has left the queue. EVW5D's post,
# adapted. Read-only outside $LANE/post: squeue answers only whether the job is still queued; sacct gives every
# outcome; it re-checks the products against their SHA256SUMS in place, runs evw2d.accepted() on them (in the
# root_6_28 environment, from deploy_C), records stat lines (atime, mtime, size) of the products and the staged copies
# for the purge exposure (files unread for 8 weeks; the exposure is the atime plus 56 days, the declaration's §7), and
# copies the job's receipts and the small products (everything but weights.npz and denominator.npz) into $LANE/post,
# tarred to $LANE/post.tar.gz for the lane's scp. The receipts are always written, for diagnosis; the exit status is
# 0 when the products verify and evw2d.accepted() passes, 5 when not (VERIFY=FAIL or ACCEPTED=false in the log).
# $LANE must be a real directory reached through no link; every destination is created exclusively. It submits and
# cancels nothing. Launched from a private /dev/shm copy of itself, whose path is $1; it deletes that copy at exit.
SELF=$1
LANE=__LANE_ROOT__
P=$LANE/post
E=$LANE/out
DM=$LANE/deploy_M
DC=$LANE/deploy_C
ST=$LANE/stage
set -o noclobber
bail() { echo "STOP: $*"; rm -f -- "$SELF"; exit 9; }
[ -d "$LANE" ] && [ ! -L "$LANE" ] && [ "$(cd "$LANE" && pwd -P)" = "$LANE" ] || bail "$LANE is not a real directory"
[ -s "$LANE/logs/evw2d.jobid" ] && [ ! -L "$LANE/logs" ] || bail "no evw2d.jobid"
for f in "$P" "$LANE/post.tar.gz"; do [ ! -e "$f" ] && [ ! -L "$f" ] || bail "$f exists"; done
job=$(cat "$LANE/logs/evw2d.jobid")
case "$job" in *[!0-9]*|"") bail "jobid '$job'";; esac
st=$(squeue -h -j "$job" -o %T 2>/dev/null)
[ -z "$st" ] || bail "job $job is still $st"
mkdir "$P" || bail "mkdir"
exec > "$P/post.log" 2>&1
echo "node $(hostname) $(date -u +%FT%TZ) post sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$P/evw2d_post.sh"
sacct -j "$job" -n -P -o JobID,JobName,State,ExitCode,ElapsedRaw,NNodes,Start,End,MaxRSS > "$P/sacct.txt" 2>&1
echo "sacct rc=$?"; cat "$P/sacct.txt"
awk -F'|' -v j="$job" '($1 "") == (j "") {printf "%.4f\n", $5 * $6 / 3600}' "$P/sacct.txt" > "$P/charge_node_h.txt"
echo "charge_node_h=$(cat "$P/charge_node_h.txt")   (the allocation's line only: JobID compared as a string)"
mkdir "$P/logs" "$P/out"
for f in "$LANE"/logs/*; do [ -f "$f" ] && [ ! -L "$f" ] && cp -p "$f" "$P/logs/"; done
verify=FAIL
BASE="constants.json
run.json
weights.npz
xsec.root"                        # evw2d.PRODUCTS; denominator.npz joins them only with the declared fallback
if [ -d "$E" ] && [ ! -L "$E" ] && [ -f "$E/SHA256SUMS" ] && [ ! -L "$E/SHA256SUMS" ]; then
  listed=$(LC_ALL=C cut -c67- "$E/SHA256SUMS" | LC_ALL=C sort)
  EXPECT=$BASE
  case "$listed" in *denominator.npz*) EXPECT=$(printf '%s\ndenominator.npz\n' "$BASE" | LC_ALL=C sort);; esac
  okset=1; [ "$listed" = "$EXPECT" ] || okset=0
  for f in $EXPECT; do [ -f "$E/$f" ] && [ ! -L "$E/$f" ] || okset=0; done
  echo "product set exact: $okset"
  if [ "$okset" = 1 ]; then
    ( cd "$E" && sha256sum --strict -c SHA256SUMS ) > "$P/sha256sum-c.txt" 2>&1 && verify=PASS
    cat "$P/sha256sum-c.txt"
  fi
fi
echo "VERIFY=$verify (the products against SHA256SUMS, in place)"
echo "$verify" > "$P/verify.txt"
acc=false
if [ "$verify" = PASS ]; then
  ( source "$DM/setup_salloc_env.sh" > "$P/env-accept.log" 2>&1 || exit 96
    cd "$P" || exit 95
    PYTHONDONTWRITEBYTECODE=1 python3 -B -c "import json, sys
sys.path.insert(0, sys.argv[1]); import evw2d
from pathlib import Path
r = evw2d.accepted(Path(sys.argv[2])); print(json.dumps(r, default=str)); sys.exit(0 if r['pass'] else 1)" \
      "$DC/2d-unfolding/evw2d" "$E" > "$P/accepted.json" 2> "$P/accepted.err" )
  arc=$?; echo "evw2d.accepted rc=$arc"; [ "$arc" -eq 0 ] && acc=true
fi
echo "ACCEPTED=$acc"
echo "== stat (name|bytes|atime|mtime|inode): products and staged copies; exposure = atime + 56 days"
stat -c '%n|%s|%X|%Y|%i' "$E"/* "$ST"/* > "$P/stat-post.txt" 2>&1; cat "$P/stat-post.txt"
for f in evw2d.done run.json constants.json xsec.root SHA256SUMS; do
  [ -f "$E/$f" ] && [ ! -L "$E/$f" ] && cp -p "$E/$f" "$P/out/"
done
ls -la "$E" "$ST" > "$P/listing.txt" 2>&1
[ -f "$E/SHA256SUMS" ] && echo "SHA256SUMS sha256 $(sha256sum "$E/SHA256SUMS" | cut -d' ' -f1)"
for c in "$DM" "$DC"; do
  s=$(git -C "$c" status --porcelain --ignored 2>&1); r=$?
  echo "$c HEAD $(git -C "$c" rev-parse HEAD) status rc=$r lines=$(printf '%s' "$s" | grep -c .)"
done
( cd "$P" && find . -type f ! -path ./SHA256SUMS ! -path ./post.log | sort | xargs sha256sum > SHA256SUMS )
echo "files $(wc -l < "$P/SHA256SUMS")"
rc=0; [ "$verify" = PASS ] && [ "$acc" = true ] || rc=5
echo "post rc=$rc $(date -u +%FT%TZ)"
tar czf "$LANE/post.tar.gz" -C "$LANE" post
rm -f -- "$SELF"
exit $rc
