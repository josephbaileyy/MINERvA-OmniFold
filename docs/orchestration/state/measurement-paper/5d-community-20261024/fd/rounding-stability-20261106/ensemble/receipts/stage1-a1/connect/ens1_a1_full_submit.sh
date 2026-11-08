#!/bin/bash
# ENS1 stage-1 FULL run under addendum A1 (ENS1-BINDING-2 "addendum A1"; declaration §8): the submission of the six
# one-node shards, after the dry rerun (job 60993979, receipt #932 merged at cfbea4d6) and the director's projection
# gate PASS. Runs on a login node from a /dev/shm copy of itself whose path is $1; it deletes that copy at exit. In order:
#   refusals before anything is written: $NEW must exist with the dry rerun's DONE at its receipted sha256 and no
#     FAILED; no stage-1 shard log may exist; this connect's own log may not exist; no ens1_* job queued or running;
#   iris (read first): stop unless ENS1's caps (55.0 + 46.0) and RS1's 8.0 together are at most half of m3246's balance;
#   the fence, as before: the queue may hold only rs1_* and ens1_* jobs; a cov2d-* job or any other name is a stop;
#   the charge ceiling: stage 1's spend from sacct (attempt 1 60983221 at 571 s, the dry rerun 60993979 at 1,093 s, each
#     on 1 node and ended) plus 6 x 9.0 must be at most 55.0 (0.4622 + 54.00 = 54.46);
#   the inputs stat'ed (23 files, stat only);
#   the deploy $NEW/deploy re-checked: HEAD M_A1, 0 modified tracked files (sbatch_ens1.sh's own test), the 12 blobs and
#     7 sha256s of the dry connect; the 20 control-jitter copies under $NEW/refs at the dry connect's refs-SHA256SUMS;
#   the stage-1 queue as the dry connect wrote it: the seven files at the digests sent, shards 168/168/167/167/167/167;
#   six sbatch calls, shard 0..5: sbatch_ens1.sh shard 1 <i> at M_A1, --time=9:00:00, job name ens1_a1_s1_<i>, from the
#     plain login environment; each scontrol TimeLimit must read 09:00:00. Any failed sbatch, missing job id or wrong
#     TimeLimit cancels every shard this connect submitted and stops (all six or none).
# sbatch_ens1.sh itself refuses a shard without the stage-1 dry DONE at the same pin. Writes only under $NEW/logs (this
# connect's files). Attempt 1's root is not touched. Module calls: none (no Python is run here). No set -u.
SELF=$1
M=f4d2d7f3833834390b7b031df61ba1a5765e9900
NEW=/pscratch/sd/j/josephrb/ens1-a1-20261108
OLD=/pscratch/sd/j/josephrb/ens1-20261107
D=$NEW/deploy
SD=$NEW/stage1
CAPS=109.0                                                       # ENS1 55.0 + 46.0, and RS1's 8.0
STAGE_CAP=55.0
SHARD_H=9.0
TLIMIT_ARG=9:00:00
TLIMIT=09:00:00
DONE_SHA=96bffd6266f6e2bc2a60d11b3cc4839fb76b828106c9efd63c8966c63e37ba7a   # receipts/stage1-dry-a1/log-dry/DONE
NPZ=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz
BKG=/pscratch/sd/j/josephrb/s5c-20260924/runs/p2/bkg_dump.npz
REFSRC=/pscratch/sd/j/josephrb/fd-stab-a1r-20261104/runs/control/stability
S=docs/orchestration/state/measurement-paper/5d-community-20261024
E=$S/fd/rounding-stability-20261106/ensemble
SUMS=$S/fd/receipts-stab-a1r/full/SHA256SUMS
LOG=$NEW/logs/connect-a1-full.log
bail() { rm -f -- "$SELF"; exit 9; }
[ -n "$SELF" ] && [ -f "$SELF" ] || exit 9
[ -d "$NEW/logs" ] && [ -d "$D" ] && [ -d "$SD" ] || bail
[ ! -e "$LOG" ] && [ ! -e "$NEW/logs/a1-full.jobids" ] || bail
[ "$(sha256sum "$SD/log-dry/DONE" 2>/dev/null | cut -d' ' -f1)" = "$DONE_SHA" ] || bail
[ ! -e "$SD/log-dry/FAILED" ] || bail
for i in 0 1 2 3 4 5; do [ ! -e "$SD/log-shard$i" ] || bail; done
q0=$(squeue --me -h -o '%j') || bail
[ -z "$(printf '%s\n' "$q0" | grep -E '^ens1_')" ] || bail
exec > "$LOG" 2>&1
finish() { echo "ens1 a1 full submit rc=$1"; date -u +%FT%TZ; echo "$1" > "$NEW/logs/connect-a1-full.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$NEW/logs/ens1_a1_full_submit.sh"
echo "dry DONE sha256 $DONE_SHA: $(cat "$SD/log-dry/DONE")"

echo "== iris"; timeout 120 iris < /dev/null > "$NEW/logs/iris-full.txt" 2>&1; head -2 "$NEW/logs/iris-full.txt"
row=$(grep -E '^m3246 ' "$NEW/logs/iris-full.txt" | head -1); echo "$row"
bal=$(echo "$row" | awk 'NF>=5 {printf "%.1f", $5-$4}')
[ -n "$bal" ] || { echo "STOP: could not read the m3246 balance"; finish 9; }
echo "balance_node_h=$bal half=$(awk -v b="$bal" 'BEGIN{printf "%.1f", b/2}') caps=$CAPS"
awk -v b="$bal" -v c=$CAPS 'BEGIN{exit !(c <= b/2)}' || { echo "STOP: the caps are above half the balance"; finish 9; }

echo "== the fence (only rs1_* and ens1_* pass; cov2d-* or any other name stops)"
squeue -u josephrb -h -o '%i|%j|%T|%M|%l' > "$NEW/logs/squeue-before-full.txt" 2>&1 || { echo "STOP: squeue failed"; finish 9; }
cat "$NEW/logs/squeue-before-full.txt"
cov=$(awk -F'|' '$2 ~ /^cov2d-/' "$NEW/logs/squeue-before-full.txt")
other=$(awk -F'|' '$2 !~ /^(rs1_|ens1_)/' "$NEW/logs/squeue-before-full.txt")
ens=$(awk -F'|' '$2 ~ /^ens1_/' "$NEW/logs/squeue-before-full.txt")
[ -z "$cov" ] || { echo "FENCE STOP: cov2d jobs present:"; printf '%s\n' "$cov"; finish 9; }
[ -z "$other" ] || { echo "FENCE STOP: a job of another name is present:"; printf '%s\n' "$other"; finish 9; }
[ -z "$ens" ] || { echo "STOP: an ens1_* job is already queued or running:"; printf '%s\n' "$ens"; finish 9; }
echo "FENCE: pass ($(grep -c . "$NEW/logs/squeue-before-full.txt") jobs, none outside rs1_*)"

echo "== the charge ceiling (sacct)"
sacct -j 60983221,60993979 -X -n -P -o JobID,JobName,State,ElapsedRaw,NNodes > "$NEW/logs/sacct-stage1-before.txt" 2>&1 \
  || { echo "STOP: sacct failed"; finish 9; }
cat "$NEW/logs/sacct-stage1-before.txt"
want="60983221|ens1_dry1|FAILED|571|1
60993979|ens1_a1_dry|COMPLETED|1093|1"
[ "$(sort "$NEW/logs/sacct-stage1-before.txt")" = "$want" ] || { echo "STOP: stage 1's jobs in sacct are not the receipted ones"; finish 9; }
awk -F'|' -v cap=$STAGE_CAP -v sh=$SHARD_H '{s += $4 * $5} END {
  spent = s / 3600; ceil = spent + 6 * sh
  printf "stage 1 spent %.4f node-h; + 6 x %.1f = %.4f; cap %.1f\n", spent, sh, ceil, cap
  exit !(ceil <= cap)}' "$NEW/logs/sacct-stage1-before.txt" || { echo "STOP: the charge ceiling is above the cap"; finish 9; }

echo "== stat"
REFS=""; for s in $(seq 1 20); do REFS="$REFS stab_control_b-_j$s.npz"; done
miss=0
for f in "$NPZ" "$BKG" "$OLD/runs/F64/ens1_F64_b-_j0.npz"; do stat -c '%n size=%s mtime=%y atime=%x' "$f" || miss=$((miss + 1)); done
for r in $REFS; do stat -c '%n size=%s mtime=%y atime=%x' "$REFSRC/$r" || miss=$((miss + 1)); done
echo "stat: 23 files, $miss missing"
[ "$miss" -eq 0 ] || { echo "STOP: an input or a reference is missing"; finish 9; }

echo "== the deploy (re-checked)"
[ "$(git -C "$D" rev-parse HEAD)" = "$M" ] || { echo "STOP: HEAD is not M_A1"; finish 9; }
n=$(git -C "$D" status --porcelain --untracked-files=no | wc -l); echo "HEAD $M; modified tracked files: $n"
git -C "$D" status --porcelain --ignored > "$NEW/logs/deploy-status-full.txt"
echo "porcelain --ignored lines (recorded; untracked or ignored files the dry job left): $(grep -c . "$NEW/logs/deploy-status-full.txt")"
[ "$n" -eq 0 ] || { echo "STOP: the deploy has modified tracked files"; finish 9; }
bad=0
while read -r b p; do
  [ "$(git -C "$D" rev-parse "$M:$p")" = "$b" ] && [ "$(git -C "$D" hash-object "$p")" = "$b" ] || { echo "MISMATCH $p"; bad=$((bad + 1)); }
done <<BLOBS
a25490bf9d078e708696b9c9f534c731d72fcc61 nd-unfolding/ensemble_estimator_probe.py
2ac2fbe497b29f4754d0dacbe8decbc35cd4e1d5 nd-unfolding/ensemble_estimator_analyze.py
b334872a59bcbe1b6852a066dc409776dc016513 nd-unfolding/sbatch_ens1.sh
8465d84f08e99ad12f2c4fb3afca2ea7efbe485b nd-unfolding/rounding_mechanism_probe.py
25179f9f704e61a920c9d0005283b4fcd357d825 nd-unfolding/estimator_stability_probe.py
0e4718902e1b156d340ba5a9848d522b5be0fc45 nd-unfolding/estimator_stability_analyze.py
fa4781edab2447793156fc92ec71aacbba2470cd nd-unfolding/s5p_numerics.py
14f7a01186bed708e8a673f7f42c82052b76373e nd-unfolding/s5p_nullexp.py
21ba1cc953c49d0a754cbf40b4ef0036a881ce58 nd-unfolding/s5e_trace.py
1a1898fe6b5a2c6b66d7b77d4d1f02e1fbb81f59 nd-unfolding/s5n_pseudo.py
e21c033b779fc604fa6cda72f1fc71d7f58b1e9c nd-unfolding/s5c_unfold.py
bdc79a29ad90e110413898f42c81178410f7269c $SUMS
BLOBS
bad2=0
while read -r h p; do
  [ "$(sha256sum "$D/$p" | cut -d' ' -f1)" = "$h" ] || { echo "SHA256 MISMATCH $p"; bad2=$((bad2 + 1)); }
done <<SHAS
1b8a4592d9e4cad126b2a386afd8f8d169db2c11cec12a837f91cbb0f1cff698 $E/ENS1-ADDENDUM-A1.md
fb523c7a7a8215b451d21093b2637ed12548f3f2ce4b714990c194b05d21a2fb $E/ENS1-DECLARATION.md
cabff142a1c0ec881ce8ba1ee348c88f02b74d44b5052a7e6aae51afacfa4dfc $E/ENS1-BINDING-1.md
807c40d3cb64e2e09d2fa9a5b91fb7a786f4eb51090e4291d65b3896b47e3b25 nd-unfolding/ensemble_estimator_probe.py
1d6a0448ac75c90a2282ceb8bd5383cf0cae27024c0dbb9a5adc27ff93b11281 nd-unfolding/ensemble_estimator_analyze.py
0390e5c71f1b958558dbae7916e39ead33865362c1369d2f25b205061b2b7267 nd-unfolding/sbatch_ens1.sh
e2c35e55402b809f522c86f597df20b058fc0c49596b9595448c4a944be333ee $SUMS
SHAS
echo "blobs: 12 checked, $bad mismatches; sha256: 7 checked, $bad2 mismatches"
[ "$bad" -eq 0 ] && [ "$bad2" -eq 0 ] || { echo "STOP: bound bytes"; finish 9; }
( cd "$NEW/refs" && find runs -type f -print0 | sort -z | xargs -0 sha256sum ) > "$NEW/logs/refs-SHA256SUMS-full"
cmp -s "$NEW/logs/refs-SHA256SUMS-full" "$NEW/logs/refs-SHA256SUMS" && [ "$(grep -c . "$NEW/logs/refs-SHA256SUMS")" -eq 20 ] \
  || { echo "STOP: the control-jitter copies are not the dry connect's"; finish 9; }
echo "control-jitter copies: 20, as at the dry connect"

echo "== the stage-1 queue (as the dry connect wrote it)"
( cd "$SD" && sha256sum dry.tsv shard0.tsv shard1.tsv shard2.tsv shard3.tsv shard4.tsv shard5.tsv ) > "$NEW/logs/queue-sha256-full.txt"
cat "$NEW/logs/queue-sha256-full.txt"
cat > "$NEW/logs/queue-sha256-full.expected" <<SUMS1
83ae2e8c6ce7916725ed3c31096ae4ea7c831b40aed70386225dff520de0f8f2  dry.tsv
76b3b25a31a37f818126fe5d03e2b99f4694ee7581ce5ef1791b5ca936b71349  shard0.tsv
30383483dfe727762c8ba268996ae266385a547944b58e2ec339d36d422d4741  shard1.tsv
4df6defc7b2b542062edda09d4bc32d7a973f058e30f51489f2c3364a6a5701a  shard2.tsv
7df85feadf16a3c1c6f166661acbda57d27004bec21dcb3935ca8f6f3dba86f5  shard3.tsv
eeca67f3ded9548611db5544830dc8075c7f6fdfd3bf4bee503a22afdf9f2468  shard4.tsv
761c27c42131f2c1b4013301e972e5b7d5f34a28fda84bd6e7df25e420ee615a  shard5.tsv
SUMS1
cmp -s "$NEW/logs/queue-sha256-full.txt" "$NEW/logs/queue-sha256-full.expected" || { echo "STOP: the queue is not the one sent"; finish 5; }
counts=""; for i in 0 1 2 3 4 5; do counts="$counts $(grep -vc '^#' "$SD/shard$i.tsv")"; done
echo "shard tasks:$counts"
[ "$counts" = " 168 168 167 167 167 167" ] || { echo "STOP: the shard task counts are not 168/168/167/167/167/167"; finish 5; }

echo "== six sbatch calls"
date -u +%FT%TZ
cd "$NEW" || finish 9
jobs=""
undo() {  # cancel every shard this connect submitted, then stop
  echo "$1"
  for j in $jobs; do scancel "$j"; echo "scancel $j rc $?"; done
  sleep 5; [ -n "$jobs" ] && sacct -j "$(echo $jobs | tr ' ' ',')" -X -n -P -o JobID,JobName,State,Elapsed
  finish "$2"
}
for i in 0 1 2 3 4 5; do
  sbatch --time=$TLIMIT_ARG --job-name=ens1_a1_s1_$i --output="$NEW/logs/%x_%j.out" \
    "$D/nd-unfolding/sbatch_ens1.sh" shard 1 "$i" "$D" "$M" "$NEW" > "$NEW/logs/submit-a1-full-$i.out" 2>&1
  rc=$?; echo "shard $i: sbatch rc=$rc $(cat "$NEW/logs/submit-a1-full-$i.out")"
  [ $rc = 0 ] || undo "STOP at sbatch, shard $i" 6
  job=$(sed -n 's/^Submitted batch job \([0-9][0-9]*\)$/\1/p' "$NEW/logs/submit-a1-full-$i.out")
  [ -n "$job" ] || undo "STOP: no job id for shard $i" 6
  jobs="$jobs $job"; echo "$i $job" >> "$NEW/logs/a1-full.jobids"
  tl=$(scontrol show job "$job" | sed -n 's/.*TimeLimit=\([^ ]*\).*/\1/p' | head -1)
  echo "shard $i job $job scontrol TimeLimit=$tl (declared $TLIMIT)"
  [ "$tl" = "$TLIMIT" ] || undo "STOP: shard $i TimeLimit $tl is not $TLIMIT" 6
done
sleep 5
squeue -j "$(echo $jobs | tr ' ' ',')" -h -o "%i %j %T %M %l %D %q %a"
n=$(git -C "$D" status --porcelain --untracked-files=no | wc -l); echo "modified tracked files after: $n"
[ "$n" -eq 0 ] || { echo "the deploy changed after the submission (the jobs are queued; reported, not cancelled)"; finish 8; }
finish 0
