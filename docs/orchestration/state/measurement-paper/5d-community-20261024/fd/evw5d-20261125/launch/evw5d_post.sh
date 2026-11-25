#!/bin/bash
# EVW5D: the post, on a Perlmutter login node, in the foreground, after the job has left the queue. ESS's post
# (fd/receipts-ess/cluster/ess_post.sh), adapted. Read-only outside $OUT/post: it stats the three shared inputs again
# (stat does not move atime), reads sacct, re-checks the products against their SHA256SUMS in place, and copies the
# job's receipts and the small products (everything but weights.npz and the driver's product npz) into $OUT/post,
# tarred to $OUT/post.tar.gz for the lane's scp. weights.npz is fetched separately, by sha (the launcher's
# fetch-products mode). It submits and cancels nothing. Launched from a /dev/shm copy of itself, whose path is $1; it
# deletes that copy at exit.
SELF=$1
OUT=/pscratch/sd/j/josephrb/evw5d-20261125
P=$OUT/post
E=$OUT/evw5d
NPZ=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz
BKG=/pscratch/sd/j/josephrb/s5c-20260924/runs/p2/bkg_dump.npz
REF=/pscratch/sd/j/josephrb/s5p-20260926/runs/s2/num/data/data_b-_j-.npz
bail() { echo "STOP: $*"; rm -f -- "$SELF"; exit 9; }
[ -s "$OUT/logs/evw5d.jobid" ] || bail "no evw5d.jobid"
[ ! -e "$P" ] && [ ! -e "$OUT/post.tar.gz" ] || bail "a post exists"
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
awk -F'|' -v j="$job" '$1 == j {printf "%.4f\n", $5 * $6 / 3600}' "$P/sacct.txt" > "$P/charge_node_h.txt"
echo "charge_node_h=$(cat "$P/charge_node_h.txt")   (the job's line; JobID compared as a string)"
stat -c '%n|%s|%X|%Y|%i' "$NPZ" "$BKG" "$REF" > "$P/stat-post.txt"; cat "$P/stat-post.txt"
mkdir "$P/logs" "$P/evw5d"
for f in "$OUT"/logs/*; do [ -f "$f" ] && cp -p "$f" "$P/logs/"; done
if [ -f "$E/SHA256SUMS" ]; then
  ( cd "$E" && sha256sum -c SHA256SUMS ) > "$P/sha256sum-c.txt" 2>&1; echo "sha256sum -c rc=$?"; cat "$P/sha256sum-c.txt"
fi
for f in evw5d.done run.json constants.json constants.npz SHA256SUMS STOP.json FAILED.json; do
  [ -f "$E/$f" ] && cp -p "$E/$f" "$P/evw5d/"
done
ls -la "$E" "$E/product" > "$P/listing.txt" 2>&1
for c in "$OUT/deploy" "$OUT/toolclone"; do
  echo "$c HEAD $(git -C "$c" rev-parse HEAD) porcelain --ignored $(git -C "$c" status --porcelain --ignored | wc -l)"
done
( cd "$P" && find . -type f ! -path ./SHA256SUMS ! -path ./post.log | sort | xargs sha256sum > SHA256SUMS )
echo "files $(wc -l < "$P/SHA256SUMS")"
tar czf "$OUT/post.tar.gz" -C "$OUT" post
echo "post.tar.gz sha256 $(sha256sum "$OUT/post.tar.gz" | cut -d' ' -f1)"
echo "post rc=0 $(date -u +%FT%TZ)"
rm -f -- "$SELF"
exit 0
