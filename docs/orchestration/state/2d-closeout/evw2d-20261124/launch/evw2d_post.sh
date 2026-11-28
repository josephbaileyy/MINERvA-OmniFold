#!/bin/bash
# EVW2D: the post, on a Perlmutter login node, in the foreground, after the job has left the queue. EVW5D's post,
# adapted. Before it writes anything:
#   - squeue (it must answer) lists this user's jobs, and the job id must not be among them;
#   - sacct (it must answer) gives exactly one allocation row for the job, in a terminal state. Without one (accounting
#     lag, or the job not ended) it stops and writes nothing, so it can simply be run again later.
# Then, read-only outside $LANE/post: it records sacct in full, re-checks the products against their SHA256SUMS in
# place, runs evw2d.accepted() on them (root_6_28, from deploy_C) and requires run.json's config digest to be the bound
# one and its slurm_job to be this job, records stat lines (atime, mtime, size) of the products and the staged copies after its last read, for the purge
# exposure (files unread for 8 weeks; the exposure is the atime plus 56 days, the declaration's §7), and copies the
# job's receipts and the small products (everything but weights.npz and denominator.npz) into $LANE/post, tarred to
# $LANE/post.tar.gz (written under a partial name, then renamed).
# PASS needs all of: the allocation COMPLETED with exit code 0:0 on one node; the product set exact and equal to its
# SHA256SUMS; evw2d.accepted() passing with the bound config digest; every receipt, stat line, manifest and the archive
# written. Only then, last, it publishes $LANE/post.pass (job, config digest, the products' SHA256SUMS digest) by
# rename; evw2d_cleanup.sh requires it. Exit 0 = PASS, 5 = not. It submits and cancels nothing. Launched from a private
# /dev/shm copy of itself, whose path is $1 (only read); the launcher's wrapper deletes that copy after it exits. This
# script removes nothing.
SELF=$1
LANE=__LANE_ROOT__
CFG_SHA=__CONFIG_SHA256__
P=$LANE/post
E=$LANE/out
DM=$LANE/deploy_M
DC=$LANE/deploy_C
ST=$LANE/stage
set -o noclobber
bail() { echo "STOP (nothing written): $*"; exit 9; }
case "$CFG_SHA" in *__*) bail "the config digest is not filled in";; esac
[ -d "$LANE" ] && [ ! -L "$LANE" ] && [ "$(cd "$LANE" && pwd -P)" = "$LANE" ] || bail "$LANE is not a real directory"
[ -s "$LANE/logs/evw2d.jobid" ] && [ ! -L "$LANE/logs" ] || bail "no evw2d.jobid"
for f in "$P" "$LANE/post.tar.gz" "$LANE/post.tar.gz.partial" "$LANE/post.pass" "$LANE/post.pass.partial"; do
  [ ! -e "$f" ] && [ ! -L "$f" ] || bail "$f exists"
done
job=$(cat "$LANE/logs/evw2d.jobid")
case "$job" in *[!0-9]*|"") bail "jobid '$job'";; esac
q=$(squeue --me -h -o '%i') || bail "squeue did not answer"
printf '%s\n' "$q" | grep -qx "$job" && bail "job $job is still queued or running"
acct=$(sacct -j "$job" -X -n -P -o JobID,State,ExitCode,NNodes,ElapsedRaw 2>&1) || bail "sacct did not answer: $acct"
row=$(printf '%s\n' "$acct" | awk -F'|' -v j="$job" '($1 "") == (j "")')
[ "$(printf '%s\n' "$row" | grep -c .)" = 1 ] || bail "sacct has no single allocation row for job $job yet: '$acct'"
state=$(printf '%s' "$row" | cut -d'|' -f2 | cut -d' ' -f1)          # "CANCELLED by 112498" -> CANCELLED
case "$state" in
  COMPLETED|FAILED|CANCELLED|TIMEOUT|OUT_OF_MEMORY|NODE_FAIL|PREEMPTED|BOOT_FAIL|DEADLINE) ;;
  *) bail "job $job is '$state' in sacct, not a terminal state";;
esac
mkdir "$P" || bail "mkdir $P"
exec > "$P/post.log" 2>&1
fail=0
need() { "$@" || { echo "FAILED: $*"; fail=1; }; }
echo "node $(hostname) $(date -u +%FT%TZ) post sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
need cp "$SELF" "$P/evw2d_post.sh"
sacct -j "$job" -n -P -o JobID,JobName,State,ExitCode,ElapsedRaw,NNodes,Start,End,MaxRSS > "$P/sacct.txt" || { echo "FAILED: sacct.txt"; fail=1; }
cat "$P/sacct.txt"
exitc=$(printf '%s' "$row" | cut -d'|' -f3); nnodes=$(printf '%s' "$row" | cut -d'|' -f4); el=$(printf '%s' "$row" | cut -d'|' -f5)
acct_ok=false
[ "$state" = COMPLETED ] && [ "$exitc" = "0:0" ] && [ "$nnodes" = 1 ] && acct_ok=true
echo "allocation $job: state=$state exit=$exitc nnodes=$nnodes elapsed_s=$el ACCOUNTING_OK=$acct_ok"
if printf '%s\n%s\n' "$el" "$nnodes" | grep -Evq '^[0-9]+$'; then
  echo "FAILED: the allocation's ElapsedRaw or NNodes is not an integer"; fail=1
else
  awk -v e="$el" -v n="$nnodes" 'BEGIN {printf "%.4f\n", e * n / 3600}' > "$P/charge_node_h.txt"
  echo "charge_node_h=$(cat "$P/charge_node_h.txt")   (the allocation's line only: JobID compared as a string)"
fi
need mkdir "$P/logs" "$P/out"
for f in "$LANE"/logs/*; do [ -f "$f" ] && [ ! -L "$f" ] && need cp -p "$f" "$P/logs/"; done
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
  ( set +o noclobber   # the setup runs as in the job; this script's own redirects stay exclusive outside it
    source "$DM/setup_salloc_env.sh" > "$P/env-accept.log" 2>&1 || exit 96
    [ "$(command -v python3)" = "$HOME/.conda/envs/root_6_28/bin/python3" ] || exit 98
    cd "$P" || exit 95
    PYTHONDONTWRITEBYTECODE=1 python3 -B -c "import json, sys
sys.path.insert(0, sys.argv[1]); import evw2d
from pathlib import Path
out = Path(sys.argv[2])
r = evw2d.accepted(out)
r['run_config_sha256'] = json.loads((out / 'run.json').read_text()).get('config_sha256')
r['config_bound'] = r['run_config_sha256'] == sys.argv[3]
r['run_slurm_job'] = json.loads((out / 'run.json').read_text()).get('slurm_job')
r['job_bound'] = str(r['run_slurm_job']) == sys.argv[4]
print(json.dumps(r, default=str)); sys.exit(0 if r['pass'] and r['config_bound'] and r['job_bound'] else 1)" \
      "$DC/2d-unfolding/evw2d" "$E" "$CFG_SHA" "$job" > "$P/accepted.json" 2> "$P/accepted.err" )
  arc=$?; echo "evw2d.accepted rc=$arc"; [ "$arc" -eq 0 ] && acc=true
fi
echo "ACCEPTED=$acc"
echo "== stat (name|bytes|atime|mtime|inode) after the last read: products and staged copies; exposure = atime + 56 days"
stat -c '%n|%s|%X|%Y|%i' "$E"/* "$ST"/* > "$P/stat-post.txt" || { echo "FAILED: stat-post.txt"; fail=1; }
cat "$P/stat-post.txt"
for f in evw2d.done run.json constants.json xsec.root SHA256SUMS; do
  [ -f "$E/$f" ] && [ ! -L "$E/$f" ] && need cp -p "$E/$f" "$P/out/"
done
ls -la "$E" "$ST" > "$P/listing.txt" 2>&1
sums=""
[ -f "$E/SHA256SUMS" ] && sums=$(sha256sum "$E/SHA256SUMS" | cut -d' ' -f1) && echo "SHA256SUMS sha256 $sums"
for c in "$DM" "$DC"; do
  s=$(git -C "$c" status --porcelain --ignored 2>&1); r=$?
  echo "$c HEAD $(git -C "$c" rev-parse HEAD) status rc=$r lines=$(printf '%s' "$s" | grep -c .)"
done
( cd "$P" && find . -type f ! -path ./SHA256SUMS ! -path ./post.log | sort | xargs sha256sum > SHA256SUMS ) || { echo "FAILED: the post manifest"; fail=1; }
echo "files $(wc -l < "$P/SHA256SUMS")"
pass=false
[ "$acct_ok" = true ] && [ "$verify" = PASS ] && [ "$acc" = true ] && [ "$fail" = 0 ] && [ -n "$sums" ] && pass=true
echo "POST: accounting=$acct_ok verify=$verify accepted=$acc receipts_ok=$([ "$fail" = 0 ] && echo true || echo false) PASS=$pass $(date -u +%FT%TZ)"
if tar czf "$LANE/post.tar.gz.partial" -C "$LANE" post && mv -- "$LANE/post.tar.gz.partial" "$LANE/post.tar.gz"; then
  echo "archive $LANE/post.tar.gz"
else
  echo "FAILED: the archive"; pass=false
fi
rc=5
if [ "$pass" = true ]; then
  printf 'job=%s\nconfig_sha256=%s\nproducts_SHA256SUMS_sha256=%s\n' "$job" "$CFG_SHA" "$sums" > "$LANE/post.pass.partial" \
    && mv -- "$LANE/post.pass.partial" "$LANE/post.pass" && rc=0
  [ "$rc" = 0 ] && echo "published $LANE/post.pass" || echo "FAILED: post.pass"
fi
echo "post rc=$rc"
exit $rc
