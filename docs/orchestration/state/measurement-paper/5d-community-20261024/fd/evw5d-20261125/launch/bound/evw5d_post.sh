#!/bin/bash
# EVW5D: the post, on a Perlmutter login node, in the foreground, after the job has left the queue. ESS's post
# (fd/receipts-ess/cluster/ess_post.sh), adapted. Read-only outside $OUT/post: it stats the three shared inputs again
# (stat does not move atime), reads sacct, re-checks the products against their SHA256SUMS in place, and copies the
# job's receipts and the small products (everything but weights.npz and the driver's product npz) into $OUT/post,
# tarred to $OUT/post.tar.gz for the lane's scp. The receipts are always written, for diagnosis; the exit status says
# whether the products verified: 0 = SHA256SUMS present and every product equal to it, 5 = not (VERIFY=FAIL in the
# log). It does not judge the verdict: the HPSS copy and the fetch each run evw5d.accepted() with the bound digest.
# $OUT must be a real directory reached through no link; every destination is created exclusively. It submits and
# cancels nothing. Launched from a private /dev/shm copy of itself, whose path is $1; it deletes that copy at exit.
SELF=$1
OUT=/pscratch/sd/j/josephrb/evw5d-20261125
P=$OUT/post
E=$OUT/evw5d
NPZ=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz
BKG=/pscratch/sd/j/josephrb/s5c-20260924/runs/p2/bkg_dump.npz
REF=/pscratch/sd/j/josephrb/s5p-20260926/runs/s2/num/data/data_b-_j-.npz
set -o noclobber
bail() { echo "STOP: $*"; rm -f -- "$SELF"; exit 9; }
[ -d "$OUT" ] && [ ! -L "$OUT" ] && [ "$(cd "$OUT" && pwd -P)" = "$OUT" ] || bail "$OUT is not a real directory"
[ -s "$OUT/logs/evw5d.jobid" ] && [ ! -L "$OUT/logs" ] || bail "no evw5d.jobid"
for f in "$P" "$OUT/post.tar.gz"; do [ ! -e "$f" ] && [ ! -L "$f" ] || bail "$f exists"; done
job=$(cat "$OUT/logs/evw5d.jobid")
case "$job" in *[!0-9]*|"") bail "jobid '$job'";; esac
st=$(squeue -h -j "$job" -o %T 2>/dev/null)
[ -z "$st" ] || bail "job $job is still $st"
mkdir "$P" || bail "mkdir"
exec > "$P/post.log" 2>&1
echo "node $(hostname) $(date -u +%FT%TZ) post sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$P/evw5d_post.sh"
sacct -j "$job" -n -P -o JobID,JobName,State,ExitCode,ElapsedRaw,NNodes,Start,End,MaxRSS > "$P/sacct.txt" 2>&1
echo "sacct rc=$?"; cat "$P/sacct.txt"
awk -F'|' -v j="$job" '($1 "") == (j "") {printf "%.4f\n", $5 * $6 / 3600}' "$P/sacct.txt" > "$P/charge_node_h.txt"
echo "charge_node_h=$(cat "$P/charge_node_h.txt")   (the allocation's line only: JobID compared as a string)"
stat -c '%n|%s|%X|%Y|%i' "$NPZ" "$BKG" "$REF" > "$P/stat-post.txt"; cat "$P/stat-post.txt"
mkdir "$P/logs" "$P/evw5d"
for f in "$OUT"/logs/*; do [ -f "$f" ] && [ ! -L "$f" ] && cp -p "$f" "$P/logs/"; done
verify=FAIL
EXPECT="constants.json
constants.npz
product/data_b-_j-.npz
run.json
weights.npz"                      # evw5d.PRODUCTS: SHA256SUMS must list exactly these, each a regular unlinked file
if [ -d "$E" ] && [ ! -L "$E" ] && [ -f "$E/SHA256SUMS" ] && [ ! -L "$E/SHA256SUMS" ]; then
  listed=$(LC_ALL=C cut -c67- "$E/SHA256SUMS" | LC_ALL=C sort)
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
for f in evw5d.done run.json constants.json constants.npz SHA256SUMS STOP.json FAILED.json; do
  [ -f "$E/$f" ] && [ ! -L "$E/$f" ] && cp -p "$E/$f" "$P/evw5d/"
done
ls -la "$E" "$E/product" > "$P/listing.txt" 2>&1
[ -f "$E/SHA256SUMS" ] && echo "SHA256SUMS sha256 $(sha256sum "$E/SHA256SUMS" | cut -d' ' -f1)   (the digest to bind)"
for c in "$OUT/deploy" "$OUT/toolclone"; do
  s=$(git -C "$c" status --porcelain --ignored 2>&1); r=$?
  echo "$c HEAD $(git -C "$c" rev-parse HEAD) status rc=$r lines=$(printf '%s' "$s" | grep -c .)"
done
( cd "$P" && find . -type f ! -path ./SHA256SUMS ! -path ./post.log | sort | xargs sha256sum > SHA256SUMS )
echo "files $(wc -l < "$P/SHA256SUMS")"
rc=0; [ "$verify" = PASS ] || rc=5
echo "post rc=$rc $(date -u +%FT%TZ)"
tar czf "$OUT/post.tar.gz" -C "$OUT" post
rm -f -- "$SELF"
exit $rc
