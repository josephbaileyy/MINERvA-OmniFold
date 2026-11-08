#!/bin/bash
# ENS1 stage-1 dry run, connect 1: the submission (ENS1-BINDING-2.md rulings 1-5; ENS1-DECLARATION.md §8). Runs on a
# login node from a /dev/shm copy of itself whose path is $1; it deletes that copy at exit. In order:
#   the COV2D fence, recorded (ENS1 reads no COV2D input; a failed squeue is a stop);
#   iris: stop unless ENS1's caps (55.0 + 46.0) and RS1's 8.0 together are at most half of m3246's remaining balance;
#   a stat of the inputs and of FD-STAB's 20 control jitters j1-j20;
#   a fresh clone at M into $NEW/deploy: clean, the bound blobs, the declaration's and binding 1's sha256;
#   the 20 control jitters copied with dd iflag=noatime into $NEW/refs/runs/control/stability/ (the analysis's --refs
#     layout); each original's atime unchanged and each copy at its line in FD-STAB's SHA256SUMS (e2c35e55);
#   the environment pre-check under the sourced environment (0 node-h);
#   the stage-1 queue from the bound probe's own `tasks --stage 1`, under the sourced environment: dry.tsv and the six
#     shards at the digests sent (9 dry tasks; 1,004 shard tasks, 2,008 unfolds);
#   one sbatch: sbatch_ens1.sh dry 1, --time=00:45:00, from the plain login environment; scontrol's TimeLimit must read
#     00:45:00, or the job is cancelled at once and the connect stops.
# Every module call runs under the sourced environment (setup_salloc_env.sh, Python 3.11), never the system python3
# (3.6). Writes only under $NEW (new; refused if it exists). No set -u. Any stop is final.
SELF=$1
M=53382844e72057d6eacb47f3bf8556cd47766a70
NEW=/pscratch/sd/j/josephrb/ens1-20261107
D=$NEW/deploy
CAPS=109.0                                                       # ENS1 55.0 + 46.0, and RS1's 8.0
TLIMIT=00:45:00
NPZ=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz
BKG=/pscratch/sd/j/josephrb/s5c-20260924/runs/p2/bkg_dump.npz
BANK=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/bank_sweep_5d_bkgaware
DET=/pscratch/sd/j/josephrb/s5p-20260926/bank_detector
PVL=/pscratch/sd/j/josephrb/pv-ladder-20261024
REFSRC=/pscratch/sd/j/josephrb/fd-stab-a1r-20261104/runs/control/stability
REFDST=$NEW/refs/runs/control/stability
S=docs/orchestration/state/measurement-paper/5d-community-20261024
E=$S/fd/rounding-stability-20261106/ensemble
SUMS=$S/fd/receipts-stab-a1r/full/SHA256SUMS
bail() { rm -f -- "$SELF"; exit 9; }
[ -n "$SELF" ] && [ -f "$SELF" ] || exit 9
[ ! -e "$NEW" ] || bail
[ -z "$(squeue --me -h -n ens1_dry1,ens1_shard1,ens1_dry2,ens1_shard2 -o %i)" ] || bail
mkdir "$NEW" && mkdir "$NEW/logs" && mkdir -p "$REFDST" || bail
LOG=$NEW/logs/connect-dry1.log
exec > "$LOG" 2>&1
finish() { echo "ens1 dry1 submit rc=$1"; date -u +%FT%TZ; echo "$1" > "$NEW/logs/connect-dry1.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$NEW/logs/ens1_dry1_submit.sh"

echo "== COV2D fence"
squeue -u josephrb -h -o '%i|%j|%T|%M|%l' > "$NEW/logs/squeue-before.txt" 2>&1 || { echo "STOP: squeue failed"; finish 9; }
hits=$(awk -F'|' '$2 ~ /^cov2d-/' "$NEW/logs/squeue-before.txt")
if [ -n "$hits" ]; then echo "FENCE: cov2d jobs present (recorded; ENS1 reads no COV2D input):"; printf '%s\n' "$hits"
else echo "FENCE: no cov2d-* job queued or running"; fi
cat "$NEW/logs/squeue-before.txt"

echo "== iris"; timeout 120 iris < /dev/null > "$NEW/logs/iris.txt" 2>&1; head -2 "$NEW/logs/iris.txt"
row=$(grep -E '^m3246 ' "$NEW/logs/iris.txt" | head -1); echo "$row"
bal=$(echo "$row" | awk 'NF>=5 {printf "%.1f", $5-$4}')
[ -n "$bal" ] || { echo "STOP: could not read the m3246 balance"; finish 9; }
echo "balance_node_h=$bal half=$(awk -v b="$bal" 'BEGIN{printf "%.1f", b/2}') caps=$CAPS"
awk -v b="$bal" -v c=$CAPS 'BEGIN{exit !(c <= b/2)}' || { echo "STOP: the caps are above half the balance"; finish 9; }

echo "== stat"
REFS=""; for s in $(seq 1 20); do REFS="$REFS stab_control_b-_j$s.npz"; done
miss=0
for f in "$NPZ" "$BKG"; do stat -c '%n size=%s mtime=%y atime=%x' "$f" || miss=$((miss + 1)); done
for r in $REFS; do stat -c '%n size=%s mtime=%y atime=%x' "$REFSRC/$r" || miss=$((miss + 1)); done
echo "stat: 22 files, $miss missing"
[ "$miss" -eq 0 ] || { echo "STOP: an input or reference is missing"; finish 9; }

echo "== the deploy"
git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "$D" > "$NEW/logs/clone.log" 2>&1 || { echo "STOP: clone"; finish 3; }
git -C "$D" -c advice.detachedHead=false checkout -q "$M" || { echo "STOP: checkout"; finish 3; }
[ "$(git -C "$D" rev-parse HEAD)" = "$M" ] || { echo "STOP: HEAD is not M"; finish 9; }
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "HEAD $M; porcelain --ignored lines before: $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy is not clean"; finish 9; }
bad=0
while read -r b p; do
  [ "$(git -C "$D" rev-parse "$M:$p")" = "$b" ] && [ "$(git -C "$D" hash-object "$p")" = "$b" ] || { echo "MISMATCH $p"; bad=$((bad + 1)); }
done <<BLOBS
d7ba60f50b5f2c8f37ff339d685cc7cf6b5c26d8 nd-unfolding/ensemble_estimator_probe.py
48287c9ffa55a9ca42081564b03972cb1020c4ac nd-unfolding/ensemble_estimator_analyze.py
b334872a59bcbe1b6852a066dc409776dc016513 nd-unfolding/sbatch_ens1.sh
8465d84f08e99ad12f2c4fb3afca2ea7efbe485b nd-unfolding/rounding_mechanism_probe.py
25179f9f704e61a920c9d0005283b4fcd357d825 nd-unfolding/estimator_stability_probe.py
0e4718902e1b156d340ba5a9848d522b5be0fc45 nd-unfolding/estimator_stability_analyze.py
fa4781edab2447793156fc92ec71aacbba2470cd nd-unfolding/s5p_numerics.py
14f7a01186bed708e8a673f7f42c82052b76373e nd-unfolding/s5p_nullexp.py
bdc79a29ad90e110413898f42c81178410f7269c $SUMS
BLOBS
decl=$(sha256sum "$D/$E/ENS1-DECLARATION.md" | cut -d' ' -f1); b1=$(sha256sum "$D/$E/ENS1-BINDING-1.md" | cut -d' ' -f1)
sums=$(sha256sum "$D/$SUMS" | cut -d' ' -f1)
echo "blobs: 9 checked, $bad mismatches; declaration $decl; binding 1 $b1; FD-STAB SHA256SUMS $sums"
[ "$bad" -eq 0 ] && [ "$decl" = e29877cd978d317038539d88de8d4bdc4741611f402171ddb3c9f2146b2e3589 ] \
  && [ "$b1" = cabff142a1c0ec881ce8ba1ee348c88f02b74d44b5052a7e6aae51afacfa4dfc ] \
  && [ "$sums" = e2c35e55402b809f522c86f597df20b058fc0c49596b9595448c4a944be333ee ] || { echo "STOP: bound bytes"; finish 9; }

echo "== the control jitters j1-j20 (dd iflag=noatime)"
bad=0
for r in $REFS; do
  a0=$(stat -c %X "$REFSRC/$r")
  dd if="$REFSRC/$r" iflag=noatime of="$REFDST/$r" bs=4M status=none || { echo "COPY FAILED $r"; bad=$((bad + 1)); continue; }
  a1=$(stat -c %X "$REFSRC/$r")
  want=$(awk -v n="runs/control/stability/$r" '$2 == n {print $1}' "$D/$SUMS")
  got=$(sha256sum "$REFDST/$r" | cut -d' ' -f1)
  [ "$a0" = "$a1" ] || { echo "ATIME MOVED $r ($a0 -> $a1)"; bad=$((bad + 1)); }
  [ -n "$want" ] && [ "$got" = "$want" ] || { echo "NOT PINNED $r ($got vs '$want')"; bad=$((bad + 1)); }
done
echo "control jitters: 20 copied, $bad problems"
( cd "$NEW/refs" && find runs -type f -print0 | sort -z | xargs -0 sha256sum ) > "$NEW/logs/refs-SHA256SUMS"
[ "$bad" -eq 0 ] || { echo "STOP: a control jitter"; finish 9; }

echo "== the environment (sourced)"
( source "$D/setup_salloc_env.sh" > "$NEW/logs/env-precheck.log" 2>&1
  python3 -B -c "import lightgbm, scipy, numpy, sys; print('python', sys.version.split()[0], 'lightgbm', lightgbm.__version__, 'scipy', scipy.__version__, 'numpy', numpy.__version__)" ) \
  || { echo "STOP: the environment lacks lightgbm/scipy (see env-precheck.log)"; finish 7; }

echo "== the stage-1 queue (sourced)"
( source "$D/setup_salloc_env.sh" > "$NEW/logs/env-tasks.log" 2>&1
  cd "$D" && PYTHONDONTWRITEBYTECODE=1 nice -n 19 python3 -B nd-unfolding/ensemble_estimator_probe.py tasks --stage 1 \
    --out-dir "$NEW/stage1" --runs "$NEW/runs" --npz "$NPZ" --bkg "$BKG" --bank "$BANK" --detector-dir "$DET" \
    --closure-ratio-dir "$PVL" --expect-npz-sha256 07fccc1abc7204bc29349b4ba96850986fe91e909e83fc54e8d1a6b3922a649f \
    --expect-bkg-sha256 2addac8f26055c5ed69862e7afe29e12ac51dbe23a8d6eeed79d71bec9d82955 ) || { echo "STOP: tasks"; finish 5; }
( cd "$NEW/stage1" && sha256sum dry.tsv shard0.tsv shard1.tsv shard2.tsv shard3.tsv shard4.tsv shard5.tsv ) > "$NEW/logs/queue-sha256.txt"
cat "$NEW/logs/queue-sha256.txt"
cat > "$NEW/logs/queue-sha256.expected" <<SUMS1
1f495b4ef841455608c0b9f91e48d5bd785eaec6572695c189f7eb78fc764054  dry.tsv
8959fba743832c1b4ccad6fd980a47b1a6cbc46a66e469ef3e8811eba9b722eb  shard0.tsv
e96bfc61fcc7baec3d63eaf510f2b22c2a14eee60385b8fb57f3c50bdec7b146  shard1.tsv
6bf5419a8cb83236aa01903e1fd693a7a1ffe85ec7fb60c69dcc2bde57e5796b  shard2.tsv
1d54057606d86bc0542f7b20f8862f4c0d06ae3514193913130bfedc6172e403  shard3.tsv
656a88112531f44749c66ae042db9e9ae7c2d153d50aefc2db3f64ff84ba73d0  shard4.tsv
9f06ff00755ba3adfe5c2798fd15b5329574ec9c4eeb57bdfc74e29de2668dc9  shard5.tsv
SUMS1
cmp -s "$NEW/logs/queue-sha256.txt" "$NEW/logs/queue-sha256.expected" || { echo "STOP: the queue is not the one sent"; finish 5; }
nd=$(grep -vc '^#' "$NEW/stage1/dry.tsv"); echo "dry tasks: $nd"
[ "$nd" -eq 9 ] || { echo "STOP: the dry run is not 9 tasks"; finish 5; }

date -u +%FT%TZ
cd "$NEW" || finish 9
sbatch --time=$TLIMIT --job-name=ens1_dry1 --output="$NEW/logs/%x_%j.out" \
  "$D/nd-unfolding/sbatch_ens1.sh" dry 1 "$D" "$M" "$NEW" > "$NEW/logs/submit-dry1.out" 2>&1
rc=$?; echo "sbatch rc=$rc"; cat "$NEW/logs/submit-dry1.out"
[ $rc = 0 ] || { echo "STOP at sbatch (final)"; finish $rc; }
job=$(sed -n 's/^Submitted batch job \([0-9][0-9]*\)$/\1/p' "$NEW/logs/submit-dry1.out")
[ -n "$job" ] || { echo "STOP: no job id"; finish 9; }
echo "dry run job $job"; echo "$job" > "$NEW/logs/dry1.jobid"
tl=$(scontrol show job "$job" | sed -n 's/.*TimeLimit=\([^ ]*\).*/\1/p' | head -1)
echo "scontrol TimeLimit=$tl (declared $TLIMIT)"
if [ "$tl" != "$TLIMIT" ]; then
  scancel "$job"; echo "STOP: TimeLimit $tl is not $TLIMIT; job $job cancelled (rc $?)"; sleep 5
  sacct -j "$job" -X -n -P -o JobID,State,Elapsed; finish 6
fi
sleep 5
squeue -j "$job" -h -o "%i %j %T %M %l %D %q %a"
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "porcelain --ignored lines after: $n"
[ "$n" -eq 0 ] || { echo "the deploy changed after the submission (the job is queued; reported, not cancelled)"; finish 8; }
finish 0
