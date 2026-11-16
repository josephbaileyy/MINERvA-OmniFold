#!/bin/bash
# ESS rerun: the post, on a Perlmutter login node, in the foreground, after the job has left the queue. Read-only on
# everything outside $OUT: it stats the three shared inputs again (stat does not move atime), reads sacct, and copies
# the job's receipts from $OUT into $OUT/post, then tars them to $OUT/post.tar.gz for the lane's scp. It submits and
# cancels nothing. Launched from a /dev/shm copy of itself, whose path is $1; it deletes that copy at exit.
SELF=$1
OUT=/pscratch/sd/j/josephrb/ess-e-20261110
P=$OUT/post
NPZ=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz
BKG=/pscratch/sd/j/josephrb/s5c-20260924/runs/p2/bkg_dump.npz
REF=/pscratch/sd/j/josephrb/s5p-20260926/runs/s2/num/data/data_b-_j-.npz
bail() { echo "STOP: $*"; rm -f -- "$SELF"; exit 9; }
[ -s "$OUT/logs/ess.jobid" ] || bail "no ess.jobid"
[ ! -e "$P" ] && [ ! -e "$OUT/post.tar.gz" ] || bail "a post exists"
job=$(cat "$OUT/logs/ess.jobid")
case "$job" in *[!0-9]*|"") bail "jobid '$job'";; esac
st=$(squeue -h -j "$job" -o %T 2>/dev/null)
[ -z "$st" ] || bail "job $job is still $st"
mkdir "$P" || bail "mkdir"
exec > "$P/post.log" 2>&1
echo "node $(hostname) $(date -u +%FT%TZ) post sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$P/ess_post.sh"
sacct -j "$job" -n -P -o JobID,JobName,State,ExitCode,ElapsedRaw,NNodes,Start,End > "$P/sacct.txt" 2>&1
echo "sacct rc=$?"; cat "$P/sacct.txt"
awk -F'|' -v j="$job" '$1 == j {printf "%.4f\n", $5 * $6 / 3600}' "$P/sacct.txt" > "$P/charge_node_h.txt"
echo "charge_node_h=$(cat "$P/charge_node_h.txt")"
stat -c '%n|%s|%X|%Y|%i' "$NPZ" "$BKG" "$REF" > "$P/stat-post.txt"; cat "$P/stat-post.txt"
mkdir "$P/logs" "$P/ess" "$P/tool"
for f in "$OUT"/logs/*; do [ -f "$f" ] && cp -p "$f" "$P/logs/"; done
for f in ess.json STOP.json FAILED.json; do [ -f "$OUT/ess/$f" ] && cp -p "$OUT/ess/$f" "$P/ess/"; done
[ -f "$OUT/ess/product/data_b-_j-.npz" ] && { mkdir "$P/ess/product"; cp -p "$OUT/ess/product/data_b-_j-.npz" "$P/ess/product/"; }
cp -p "$OUT/tool/ess_capture.py" "$OUT/tool/sbatch_ess.sh" "$P/tool/"
echo "deploy HEAD $(git -C "$OUT/deploy" rev-parse HEAD) porcelain --ignored $(git -C "$OUT/deploy" status --porcelain --ignored | wc -l)"
( cd "$P" && find . -type f ! -name SHA256SUMS ! -name post.log | sort | xargs sha256sum > SHA256SUMS )
echo "files $(wc -l < "$P/SHA256SUMS")"
tar czf "$OUT/post.tar.gz" -C "$OUT" post
echo "post.tar.gz sha256 $(sha256sum "$OUT/post.tar.gz" | cut -d' ' -f1)"
echo "post rc=0 $(date -u +%FT%TZ)"
rm -f -- "$SELF"
exit 0
