#!/bin/bash
# RS1 full run, connect 2: the submission (RS1-BINDING-2.md rulings 2-4; RS1-DECLARATION.md §7 items 1-3). Runs on a
# login node from a /dev/shm copy of itself whose path is $1; it deletes that copy at exit. Preconditions: the dry run's
# receipt (#891) and coverage-5b-audit's tie-invariance reading, then the director's go on this script's sha256.
# In order:
#   the COV2D fence, recorded (RS1 reads no COV2D input; a failed squeue is a stop);
#   iris: stop if the 8.0 node-h cap is above half of m3246's remaining balance;
#   the dry run, from its own files: DONE at pin M with 9 of 9 tasks, no FAILED or STOP, all 9 ends present, its
#     SHA256SUMS equal to the one committed in #891, job 60970044 COMPLETED with ElapsedRaw 944 on 1 node (0.2622
#     node-h), and queue.tsv / dry.tsv still at the digests sent;
#   the projection gate (§7 item 2): the committed figure, 4.08 h, is at most min(7.25, 0.9 x (8.0 - 0.2622)) = 6.964 h,
#     and the remaining charge ceiling, 7.25 node-h, fits in 8.0 - 0.2622;
#   a stat of both inputs (the job reads them through the production loaders);
#   a fresh clone at M into $OUT/deploy-full (the dry run's $OUT/deploy is not touched): clean, the bound blobs, the
#     declaration's and binding 1's sha256;
#   the environment pre-check (0 node-h);
#   one sbatch: sbatch_rs1.sh full, --time=07:15:00, from the plain login environment; scontrol's TimeLimit must read
#     07:15:00, or the job is cancelled at once and the connect stops.
# Writes only under $OUT (deploy-full, logs/*-full*, and the job's own log-full and runs). No set -u. Any stop is final.
SELF=$1
M=e306087e68fd497541d32b440848a40f7f29611e
OUT=/pscratch/sd/j/josephrb/rs1-20261106
D=$OUT/deploy-full
PRICE=8.0
DRY_JOB=60970044
DRY_CHARGE=0.2622                                                # 944 s x 1 node / 3600 (#891, sacct-60970044.txt)
PROJECTED_H=4.082                                                # #891 projection.out.txt
TLIMIT=07:15:00
NPZ=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz
BKG=/pscratch/sd/j/josephrb/s5c-20260924/runs/p2/bkg_dump.npz
S=docs/orchestration/state/measurement-paper/5d-community-20261024
QUEUE_SHA=58c213a24da0366ef27194ecea9fb247c6698819c5eb374f538e85e0df2fd22b
DRY_SHA=5579ea8c2b228b13df33b77d71018a14a347c26e2b6d25b5e17ce7ace2b5e8d6
DRY_SUMS_SHA=e3cc597cdc1cdb0a3bfea0095130b9a2f99a3578c63ce1541c2a893092ab2935                            # sha256 of log-dry/SHA256SUMS as committed in #891
bail() { rm -f -- "$SELF"; exit 9; }
[ -n "$SELF" ] && [ -f "$SELF" ] || exit 9
[ -d "$OUT/logs" ] || bail
for x in log-full deploy-full logs/connect-full.log logs/connect-full.done log-dry/STOP log-dry/FAILED; do [ ! -e "$OUT/$x" ] || bail; done
[ -z "$(squeue --me -h -n rs1_dry,rs1_full -o %i)" ] || bail
LOG=$OUT/logs/connect-full.log
exec > "$LOG" 2>&1
finish() { echo "rs1 full submit rc=$1"; date -u +%FT%TZ; echo "$1" > "$OUT/logs/connect-full.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$OUT/logs/rs1_full_submit.sh"

# ---- the COV2D fence, recorded
echo "== COV2D fence"
squeue -u josephrb -h -o '%i|%j|%T|%M|%l' > "$OUT/logs/squeue-before-full.txt" 2>&1 || { echo "STOP: squeue failed"; finish 9; }
hits=$(awk -F'|' '$2 ~ /^cov2d-/' "$OUT/logs/squeue-before-full.txt")
if [ -n "$hits" ]; then echo "FENCE: cov2d jobs present (recorded; RS1 reads no COV2D input):"; printf '%s\n' "$hits"
else echo "FENCE: no cov2d-* job queued or running"; fi
echo "squeue lines: $(wc -l < "$OUT/logs/squeue-before-full.txt")"

# ---- the balance
echo "== iris"; timeout 120 iris < /dev/null > "$OUT/logs/iris-full.txt" 2>&1; head -2 "$OUT/logs/iris-full.txt"
row=$(grep -E '^m3246 ' "$OUT/logs/iris-full.txt" | head -1); echo "$row"
bal=$(echo "$row" | awk 'NF>=5 {printf "%.1f", $5-$4}')
[ -n "$bal" ] || { echo "STOP: could not read the m3246 balance"; finish 9; }
echo "balance_node_h=$bal half=$(awk -v b="$bal" 'BEGIN{printf "%.1f", b/2}') price=$PRICE"
awk -v b="$bal" -v c=$PRICE 'BEGIN{exit !(c <= b/2)}' || { echo "STOP: the price $PRICE is above half the balance $bal"; finish 9; }

# ---- the dry run, from its own files
echo "== the dry run"
cat "$OUT/log-dry/DONE"
python3 -c '
import json, sys
d = json.load(open(sys.argv[1]))
ok = d.get("mode") == "dry" and d.get("tasks") == 9 and d.get("ended") == 9 and d.get("rc") == 0 \
    and d.get("job") == sys.argv[2] and d.get("pin") == sys.argv[3]
sys.exit(0 if ok else 1)' "$OUT/log-dry/DONE" "$DRY_JOB" "$M" || { echo "STOP: the dry DONE is not 9/9 rc 0 at M"; finish 4; }
n=0; for id in $(grep -v '^#' "$OUT/dry.tsv" | cut -f1); do [ -e "$OUT/log-dry/$id.end" ] && n=$((n + 1)); done
echo "dry ends present: $n of 9"
[ "$n" -eq 9 ] || { echo "STOP: a dry end is missing"; finish 4; }
sums=$(sha256sum "$OUT/log-dry/SHA256SUMS" | cut -d' ' -f1)
echo "log-dry/SHA256SUMS sha256 $sums (committed $DRY_SUMS_SHA)"
[ "$sums" = "$DRY_SUMS_SHA" ] || { echo "STOP: the dry SHA256SUMS is not the committed one"; finish 4; }
( cd "$OUT" && sha256sum -c --quiet log-dry/SHA256SUMS ) || { echo "STOP: a dry product changed since its SHA256SUMS"; finish 4; }
echo "dry products: all 18 at their SHA256SUMS lines"
sa=$(sacct -j "$DRY_JOB" -X -n -P -o State,ElapsedRaw,NNodes | head -1); echo "dry job $DRY_JOB: $sa"
[ "$sa" = "COMPLETED|944|1" ] || { echo "STOP: the dry job's sacct is not the receipt's"; finish 4; }
qs=$(sha256sum "$OUT/queue.tsv" | cut -d' ' -f1); ds=$(sha256sum "$OUT/dry.tsv" | cut -d' ' -f1)
echo "queue.tsv $qs; dry.tsv $ds"
[ "$qs" = "$QUEUE_SHA" ] && [ "$ds" = "$DRY_SHA" ] || { echo "STOP: the queue changed"; finish 4; }

# ---- the projection gate and the cap
lim=$(awk -v c=$PRICE -v d=$DRY_CHARGE 'BEGIN{l = 0.9 * (c - d); if (l > 7.25) l = 7.25; printf "%.3f", l}')
echo "projected full wall ${PROJECTED_H} h; limit $lim h; charge ceiling 7.25 + dry $DRY_CHARGE against cap $PRICE"
awk -v p=$PROJECTED_H -v l="$lim" -v d=$DRY_CHARGE -v c=$PRICE 'BEGIN{exit !(p <= l && 7.25 + d <= c)}' \
  || { echo "STOP: the projection or the cap fails: to the director"; finish 4; }

# ---- stat: the inputs
echo "== stat"
miss=0
for f in "$NPZ" "$BKG"; do stat -c '%n size=%s mtime=%y atime=%x' "$f" || miss=$((miss + 1)); done
[ "$miss" -eq 0 ] || { echo "STOP: an input is missing"; finish 9; }

# ---- the deploy: a fresh clone at M, clean, the bound blobs
git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "$D" > "$OUT/logs/clone-full.log" 2>&1 || { echo "STOP: clone"; finish 3; }
git -C "$D" -c advice.detachedHead=false checkout -q "$M" || { echo "STOP: checkout"; finish 3; }
[ "$(git -C "$D" rev-parse HEAD)" = "$M" ] || { echo "STOP: HEAD is not M"; finish 9; }
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "HEAD $M; porcelain --ignored lines before: $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy is not clean"; finish 9; }
bad=0
while read -r b p; do
  [ "$(git -C "$D" rev-parse "$M:$p")" = "$b" ] && [ "$(git -C "$D" hash-object "$p")" = "$b" ] || { echo "MISMATCH $p"; bad=$((bad + 1)); }
done <<BLOBS
8465d84f08e99ad12f2c4fb3afca2ea7efbe485b nd-unfolding/rounding_mechanism_probe.py
d58c241eff687a96bda94812d145a90d9f4790ed nd-unfolding/rounding_mechanism_analyze.py
9ad7dece80ba4ca7a6a0548c02c07bae4c947d2b nd-unfolding/sbatch_rs1.sh
8c35d8ca69913e901918945483fd40b9ad100999 nd-unfolding/tests/test_rounding_mechanism.py
ac69daf63d14af940650966a3b4e8ba1009db7db nd-unfolding/tests/rounding_mechanism_mutation.py
BLOBS
decl=$(sha256sum "$D/$S/fd/rounding-stability-20261106/RS1-DECLARATION.md" | cut -d' ' -f1)
b1=$(sha256sum "$D/$S/fd/rounding-stability-20261106/RS1-BINDING-1.md" | cut -d' ' -f1)
echo "bound blobs: 5 checked, $bad mismatches; declaration sha256 $decl; binding 1 sha256 $b1"
[ "$bad" -eq 0 ] && [ "$decl" = dbfb0c941b2ad6999b2edb3b8bf77ca735b2f01f86ca593425e44c2ad5c91e76 ] \
  && [ "$b1" = 947fd2750343ead7aff5281af8bfb03a137f76346071a84233b62ebf12744255 ] || { echo "STOP: bound bytes"; finish 9; }

# ---- the environment the job will source
( source "$D/setup_salloc_env.sh" > "$OUT/logs/env-precheck-full.log" 2>&1
  python3 -B -c "import lightgbm, scipy, numpy, sys; print('python', sys.version.split()[0], 'lightgbm', lightgbm.__version__, 'scipy', scipy.__version__, 'numpy', numpy.__version__)" ) \
  || { echo "STOP: the environment lacks lightgbm/scipy"; finish 7; }

# ---- the submission, from the plain login environment
date -u +%FT%TZ
cd "$OUT" || finish 9
sbatch --time=$TLIMIT --job-name=rs1_full --output="$OUT/logs/%x_%j.out" \
  "$D/nd-unfolding/sbatch_rs1.sh" full "$D" "$M" "$OUT" > "$OUT/logs/submit-full.out" 2>&1
rc=$?; echo "sbatch rc=$rc"; cat "$OUT/logs/submit-full.out"
[ $rc = 0 ] || { echo "STOP at sbatch (final)"; finish $rc; }
job=$(sed -n 's/^Submitted batch job \([0-9][0-9]*\)$/\1/p' "$OUT/logs/submit-full.out")
[ -n "$job" ] || { echo "STOP: no job id"; finish 9; }
echo "full run job $job"; echo "$job" > "$OUT/logs/full.jobid"
tl=$(scontrol show job "$job" | sed -n 's/.*TimeLimit=\([^ ]*\).*/\1/p' | head -1)
echo "scontrol TimeLimit=$tl (declared $TLIMIT)"
if [ "$tl" != "$TLIMIT" ]; then
  scancel "$job"; echo "STOP: TimeLimit $tl is not $TLIMIT; job $job cancelled (rc $?)"; sleep 5
  sacct -j "$job" -X -n -P -o JobID,State,Elapsed; finish 6
fi
sleep 5
squeue -j "$job" -h -o "%i %j %T %M %l %D %q %a"; scontrol show job "$job" | grep -E 'JobState|TimeLimit|NumNodes|QOS|Account|Partition'
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "porcelain --ignored lines after: $n"
[ "$n" -eq 0 ] || { echo "the deploy changed after the submission (the job is queued; reported, not cancelled)"; finish 8; }
finish 0
