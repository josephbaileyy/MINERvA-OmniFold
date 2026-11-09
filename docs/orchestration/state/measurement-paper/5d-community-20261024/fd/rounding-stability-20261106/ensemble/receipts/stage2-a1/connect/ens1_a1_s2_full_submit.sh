#!/bin/bash
# ENS1 stage-2 FULL run under addendum A1 (ENS1-DECLARATION §5, §8; ENS1-BINDING-2 ruling 2): the submission of the six
# one-node shards, after the stage-2 dry run (job 61004211, receipt #942) and the director's projection gate PASS
# (meta seconds_unfold max 603.117 s, 5.779 h of 6.75 h). Runs on a login node from a /dev/shm copy of itself whose
# path is $1; it deletes that copy at exit. In order:
#   refusals before anything is written: the stage-2 dry DONE at its receipted sha256 and no FAILED; the dry post-run's
#     done file 0 and its s2-dry-read.json at its receipted sha256 with verdict PASS; no stage-2 shard log; this
#     connect's own log and job-id file absent; no ens1_* job queued or running;
#   iris (read first): stop unless ENS1's caps (55.0 + 46.0) and RS1's 8.0 together are at most half of m3246's balance;
#   the fence (the director's ruling for this run: unchanged): the queue may hold only rs1_* and ens1_* jobs; cov2d-*,
#     ll5d_*, prr_*, fd1b_* or any other name is a stop;
#   stage 2's charge ceiling: sacct's ens1_a1_s2* jobs since 2026-11-07 must be exactly the dry run
#     (61004211|ens1_a1_s2_dry|COMPLETED|705|1); its spend plus 6 x 7.5 must be at most 46.0 (0.1958 + 45.00 = 45.20);
#   the shared inputs unchanged (the same 738-line identity as the dry connect, f533a9ad); the pv-ladder nuwro.json
#     copied once more with dd iflag=noatime, at its pin and with its atime unchanged;
#   the deploy $NEW/deploy re-checked: HEAD M_A1, 0 modified tracked files, the 12 blobs and 7 sha256s of every ENS1
#     connect; the 70 reference copies under $NEW/refs at the dry connect's refs-SHA256SUMS;
#   the stage-2 queue as the dry connect wrote it: the seven files at the digests sent, shards 136/136/136/135/135/135;
#   six sbatch calls, shard 0..5: sbatch_ens1.sh shard 2 <i> at M_A1, --time=7:30:00, job name ens1_a1_s2_<i>, from the
#     plain login environment; each scontrol TimeLimit must read 07:30:00. Any failed sbatch, missing job id or wrong
#     TimeLimit cancels every shard this connect submitted and stops (all six or none).
# sbatch_ens1.sh itself refuses a shard without the stage-2 dry DONE at the same pin. Writes only this connect's files
# under $NEW/logs-s2. Module calls: none. No set -u.
SELF=$1
M=f4d2d7f3833834390b7b031df61ba1a5765e9900
NEW=/pscratch/sd/j/josephrb/ens1-a1-20261108
D=$NEW/deploy
SD=$NEW/stage2
L2=$NEW/logs-s2
PD=$NEW/post-s2-dry
CAPS=109.0                                                       # ENS1 55.0 + 46.0, and RS1's 8.0
STAGE_CAP=46.0
SHARD_H=7.5
TLIMIT_ARG=7:30:00
TLIMIT=07:30:00
DONE_SHA=7da1740aac6c5bfc5a160970704487e3ddec7f44aac87cbdb7519ea0881b6852   # receipts/stage2-dry-a1/log-dry/DONE
READ_SHA=b5f7127f39087aa3f8b1141dd1bea7088df39becc4d73155995056a11943e5b2   # receipts/stage2-dry-a1/post/s2-dry-read.json
IDENT_SHA=f533a9add1b24143017b3a0a4aaea250b01994d894a3bc2386526f3938526ee6
NUWRO_SHA=38e47eb6b6ac63f6657022ae0cc5a2b5eaffc6a2e503735ce7222275771fea6e   # fd_f0_regrade.RATIO["closure_nuwro"]
NPZ=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz
BKG=/pscratch/sd/j/josephrb/s5c-20260924/runs/p2/bkg_dump.npz
BANK=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/bank_sweep_5d_bkgaware
DET=/pscratch/sd/j/josephrb/s5p-20260926/bank_detector
NUWRO=/pscratch/sd/j/josephrb/pv-ladder-20261024/prep/ratios/L-5D-PV/nuwro.json
S=docs/orchestration/state/measurement-paper/5d-community-20261024
E=$S/fd/rounding-stability-20261106/ensemble
SUMS=$S/fd/receipts-stab-a1r/full/SHA256SUMS
LOG=$L2/connect-s2-full.log
bail() { rm -f -- "$SELF"; exit 9; }
[ -n "$SELF" ] && [ -f "$SELF" ] || exit 9
[ -d "$L2" ] && [ -d "$D" ] && [ -d "$SD" ] || bail
[ ! -e "$LOG" ] && [ ! -e "$L2/s2-full.jobids" ] || bail
[ "$(sha256sum "$SD/log-dry/DONE" 2>/dev/null | cut -d' ' -f1)" = "$DONE_SHA" ] && [ ! -e "$SD/log-dry/FAILED" ] || bail
[ "$(cat "$PD/connect-postrun.done" 2>/dev/null)" = 0 ] || bail
[ "$(sha256sum "$PD/s2-dry-read.json" 2>/dev/null | cut -d' ' -f1)" = "$READ_SHA" ] && grep -q '"verdict": "PASS"' "$PD/s2-dry-read.json" || bail
for i in 0 1 2 3 4 5; do [ ! -e "$SD/log-shard$i" ] || bail; done
q0=$(squeue --me -h -o '%j') || bail
[ -z "$(printf '%s\n' "$q0" | grep -E '^ens1_')" ] || bail
exec > "$LOG" 2>&1
finish() { echo "ens1 a1 stage-2 full submit rc=$1"; date -u +%FT%TZ; echo "$1" > "$L2/connect-s2-full.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$L2/ens1_a1_s2_full_submit.sh"
echo "dry DONE sha256 $DONE_SHA: $(cat "$SD/log-dry/DONE")"
echo "dry post-run: done 0; s2-dry-read.json $READ_SHA, verdict PASS"

echo "== iris"; timeout 120 iris < /dev/null > "$L2/iris-full.txt" 2>&1; head -2 "$L2/iris-full.txt"
row=$(grep -E '^m3246 ' "$L2/iris-full.txt" | head -1); echo "$row"
bal=$(echo "$row" | awk 'NF>=5 {printf "%.1f", $5-$4}')
[ -n "$bal" ] || { echo "STOP: could not read the m3246 balance"; finish 9; }
echo "balance_node_h=$bal half=$(awk -v b="$bal" 'BEGIN{printf "%.1f", b/2}') caps=$CAPS"
awk -v b="$bal" -v c=$CAPS 'BEGIN{exit !(c <= b/2)}' || { echo "STOP: the caps are above half the balance"; finish 9; }

echo "== the fence (only rs1_* and ens1_* pass; cov2d-*, ll5d_*, prr_*, fd1b_* or any other name stops)"
squeue -u josephrb -h -o '%i|%j|%T|%M|%l' > "$L2/squeue-before-full.txt" 2>&1 || { echo "STOP: squeue failed"; finish 9; }
cat "$L2/squeue-before-full.txt"
other=$(awk -F'|' '$2 !~ /^(rs1_|ens1_)/' "$L2/squeue-before-full.txt")
ens=$(awk -F'|' '$2 ~ /^ens1_/' "$L2/squeue-before-full.txt")
[ -z "$other" ] || { echo "FENCE STOP: a job of another name is present:"; printf '%s\n' "$other"; finish 9; }
[ -z "$ens" ] || { echo "STOP: an ens1_* job is already queued or running:"; printf '%s\n' "$ens"; finish 9; }
echo "FENCE: pass ($(grep -c . "$L2/squeue-before-full.txt") jobs; none outside rs1_*, no ens1_*)"

echo "== stage 2's charge ceiling (sacct)"
sacct -u josephrb -S 2026-11-07 -X -n -P -o JobID,JobName,State,ElapsedRaw,NNodes > "$L2/sacct-before-full.txt" 2>&1 \
  || { echo "STOP: sacct failed"; finish 9; }
awk -F'|' '$2 ~ /^ens1_a1_s2/' "$L2/sacct-before-full.txt" > "$L2/sacct-stage2-before.txt"
cat "$L2/sacct-stage2-before.txt"
[ "$(cat "$L2/sacct-stage2-before.txt")" = "61004211|ens1_a1_s2_dry|COMPLETED|705|1" ] \
  || { echo "STOP: stage 2's jobs in sacct are not exactly the receipted dry run"; finish 9; }
awk -F'|' -v cap=$STAGE_CAP -v sh=$SHARD_H '{s += $4 * $5} END {
  spent = s / 3600; ceil = spent + 6 * sh
  printf "stage 2 spent %.4f node-h; + 6 x %.1f = %.4f; cap %.1f\n", spent, sh, ceil, cap
  exit !(ceil <= cap)}' "$L2/sacct-stage2-before.txt" || { echo "STOP: the charge ceiling is above the cap"; finish 9; }

echo "== the shared inputs (unchanged; stat only) and the pv-ladder ratio (one noatime copy)"
F="%F|%i|%h|%s|%Y|%n"
{ stat -c "$F" "$NPZ" "$BKG"
  for d in "$BANK" "$DET"; do stat -c "$F" "$d"; find "$d" -mindepth 1 -print0 | sort -z | xargs -0 stat -c "$F"; done
} > "$L2/inputs-identity-full.txt" 2> "$L2/inputs-identity-full.err"
got=$(sha256sum "$L2/inputs-identity-full.txt" | cut -d' ' -f1)
echo "inputs identity: $(grep -c . "$L2/inputs-identity-full.txt") lines, sha256 $got (sent $IDENT_SHA); errors: $(grep -c . "$L2/inputs-identity-full.err")"
[ "$got" = "$IDENT_SHA" ] && [ ! -s "$L2/inputs-identity-full.err" ] || { echo "STOP: the shared inputs changed"; finish 9; }
stat -c '%n size=%s mtime=%y atime=%x' "$NPZ" "$BKG" "$NUWRO" || { echo "STOP: an input is missing"; finish 9; }
na0=$(stat -c %X "$NUWRO")
dd if="$NUWRO" iflag=noatime of="$L2/nuwro-full.json.copy" bs=4M status=none || { echo "STOP: nuwro.json copy"; finish 9; }
na1=$(stat -c %X "$NUWRO"); ngot=$(sha256sum "$L2/nuwro-full.json.copy" | cut -d' ' -f1)
echo "pv-ladder nuwro.json sha256 $ngot (pin $NUWRO_SHA); atime $na0 -> $na1"
[ "$ngot" = "$NUWRO_SHA" ] && [ "$na0" = "$na1" ] || { echo "STOP: nuwro.json is not at its pin, or its atime moved"; finish 9; }

echo "== the deploy (re-checked)"
[ "$(git -C "$D" rev-parse HEAD)" = "$M" ] || { echo "STOP: HEAD is not M_A1"; finish 9; }
n=$(git -C "$D" status --porcelain --untracked-files=no | wc -l); echo "HEAD $M; modified tracked files: $n"
git -C "$D" status --porcelain --ignored > "$L2/deploy-status-full.txt"
echo "porcelain --ignored lines (recorded): $(grep -c . "$L2/deploy-status-full.txt")"
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
( cd "$NEW/refs" && find runs -type f -print0 | sort -z | xargs -0 sha256sum ) > "$L2/refs-SHA256SUMS-full"
cmp -s "$L2/refs-SHA256SUMS-full" "$L2/refs-SHA256SUMS" && [ "$(grep -c . "$L2/refs-SHA256SUMS")" -eq 70 ] \
  || { echo "STOP: the reference copies are not the dry connect's"; finish 9; }
echo "reference copies: 70, as at the dry connect"

echo "== the stage-2 queue (as the dry connect wrote it)"
( cd "$SD" && sha256sum dry.tsv shard0.tsv shard1.tsv shard2.tsv shard3.tsv shard4.tsv shard5.tsv ) > "$L2/queue-sha256-full.txt"
cat "$L2/queue-sha256-full.txt"
cat > "$L2/queue-sha256-full.expected" <<SUMS2
b55370daaee3443fad48285364aeee05d94ec0c675d87cd23ae1d9c609597c77  dry.tsv
bdc92a9c4f99f04db553caca532412bffa6dc89ff24e67ab8c2db40b63ea85e0  shard0.tsv
855d9f951c909f1cd32b91682766bffa4888ce77ae2415757f2a5945ed1c7528  shard1.tsv
773ab6bbc2202ad7bd7886573af2b48c71fabd7bee1762cb11e7f442606cee53  shard2.tsv
01c002b1913d9b47f44253d5b3f7f0411073a407d17e793ce0842b6414b4b2b6  shard3.tsv
26d4e7cd900a30098e15fd3e0c109f0497f9b4462ac7270869a64fbabbf22f50  shard4.tsv
7f1ac5bf33c9d4c387b3090cf33c9e1bd9f27bf5b8a54ffc4361c0f5c04ab3fd  shard5.tsv
SUMS2
cmp -s "$L2/queue-sha256-full.txt" "$L2/queue-sha256-full.expected" || { echo "STOP: the queue is not the one sent"; finish 5; }
counts=""; for i in 0 1 2 3 4 5; do counts="$counts $(grep -vc '^#' "$SD/shard$i.tsv")"; done
echo "shard tasks:$counts"
[ "$counts" = " 136 136 136 135 135 135" ] || { echo "STOP: the shard task counts are not 136/136/136/135/135/135"; finish 5; }

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
  sbatch --time=$TLIMIT_ARG --job-name=ens1_a1_s2_$i --output="$L2/%x_%j.out" \
    "$D/nd-unfolding/sbatch_ens1.sh" shard 2 "$i" "$D" "$M" "$NEW" > "$L2/submit-s2-full-$i.out" 2>&1
  rc=$?; echo "shard $i: sbatch rc=$rc $(cat "$L2/submit-s2-full-$i.out")"
  [ $rc = 0 ] || undo "STOP at sbatch, shard $i" 6
  job=$(sed -n 's/^Submitted batch job \([0-9][0-9]*\)$/\1/p' "$L2/submit-s2-full-$i.out")
  [ -n "$job" ] || undo "STOP: no job id for shard $i" 6
  jobs="$jobs $job"; echo "$i $job" >> "$L2/s2-full.jobids"
  tl=$(scontrol show job "$job" | sed -n 's/.*TimeLimit=\([^ ]*\).*/\1/p' | head -1)
  echo "shard $i job $job scontrol TimeLimit=$tl (declared $TLIMIT)"
  [ "$tl" = "$TLIMIT" ] || undo "STOP: shard $i TimeLimit $tl is not $TLIMIT" 6
done
sleep 5
squeue -j "$(echo $jobs | tr ' ' ',')" -h -o "%i %j %T %M %l %D %q %a"
n=$(git -C "$D" status --porcelain --untracked-files=no | wc -l); echo "modified tracked files after: $n"
[ "$n" -eq 0 ] || { echo "the deploy changed after the submission (the jobs are queued; reported, not cancelled)"; finish 8; }
finish 0
