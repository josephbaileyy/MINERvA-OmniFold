#!/bin/bash
# ENS1 stage-2 DRY run under addendum A1 (ENS1-DECLARATION §3.2, §5, §8; ENS1-BINDING-2 ruling 2; the director's
# 2026-11-08 release after STAB_PASS, rulings 2, 3 and 5): the submission. Runs on a login node from a /dev/shm copy of
# itself whose path is $1; it deletes that copy at exit. In order:
#   refusals before anything is written: stage 1's analysis done file reads 0 and its ens1_stage1.json is at its
#     receipted sha256 (7f5a9ce4) with verdict STAB_PASS; $NEW/stage2, this connect's log directory $NEW/logs-s2 and
#     every stage-2 reference copy do not exist; no ens1_* job queued or running;
#   iris (read first): stop unless ENS1's caps (55.0 + 46.0) and RS1's 8.0 together are at most half of m3246's balance;
#   the fence, as before: the queue may hold only rs1_* and ens1_* jobs; a cov2d-*, prr_* or any other name is a stop;
#   stage 2's charge ceiling: no ens1_a1_s2* job in sacct since 2026-11-07, so stage 2's spend is 0 and the dry run's
#     0:45:00 (0.75) is within its 46.0 cap;
#   the shared inputs unchanged since the records-only stat (receipt stage1-a1-analysis/stage2-inputs, 16:51:53Z): the
#     npz, the bkg, bank_sweep_5d_bkgaware/ and bank_detector/ by type|inode|nlink|size|mtime|path (atime and ctime
#     excluded), 738 lines at the sha256 sent; the pv-ladder nuwro.json stat'ed and copied once with dd iflag=noatime
#     to check its pin (fd_f0_regrade.RATIO["closure_nuwro"], 38e47eb6) and that its atime did not move;
#   the deploy $NEW/deploy re-checked: HEAD M_A1, 0 modified tracked files, the 12 blobs and 7 sha256s of every ENS1
#     connect; stage 1's 20 control-jitter copies unchanged (logs/refs-SHA256SUMS);
#   FD-STAB's references for stage 2 (rulings 3 and 5), each stat'ed before and after, copied with dd iflag=noatime into
#     $NEW/refs/runs/control/, each original's atime unchanged and each copy at its line in FD-STAB's SHA256SUMS
#     (e2c35e55): the control base stab_control_b-_j-.npz, the 31 jitters j21-j51, and the 18 closure lines §3.2 names
#     (A7_mnvtune, the determinism duplicate of nominal, is copied and not judged); the copy window is logged;
#   the environment pre-check (0 node-h) and the stage-2 queue from the bound probe's own `tasks --stage 2`, under the
#     sourced environment: dry.tsv and the six shards at the digests sent (7 dry tasks; shards 136/136/136/135/135/135);
#   one sbatch: sbatch_ens1.sh dry 2 at M_A1, --time=0:45:00, job name ens1_a1_s2_dry, from the plain login
#     environment; scontrol's TimeLimit must read 00:45:00, or the job is cancelled at once and the connect stops.
# The determinism control, the truth vectors and the timing are read by the post-run connect, after the job ends.
# Every module call runs under the sourced environment (Python 3.11). Writes only $NEW/logs-s2, $NEW/stage2 (through
# the bound probe) and the stage-2 copies under $NEW/refs. Attempt 1's root is not touched. No set -u.
SELF=$1
M=f4d2d7f3833834390b7b031df61ba1a5765e9900
NEW=/pscratch/sd/j/josephrb/ens1-a1-20261108
D=$NEW/deploy
L2=$NEW/logs-s2
A1S=$NEW/analysis-s1
CAPS=109.0                                                       # ENS1 55.0 + 46.0, and RS1's 8.0
STAGE_CAP=46.0
TLIMIT_ARG=0:45:00
TLIMIT=00:45:00
JOBNAME=ens1_a1_s2_dry
S1_SHA=7f5a9ce4da8f59f3284715ff6f14f8106034b42c0301ad04979a8ed6b461ad99      # receipts/stage1-a1-analysis/ens1_stage1.json
IDENT_SHA=f533a9add1b24143017b3a0a4aaea250b01994d894a3bc2386526f3938526ee6   # its stage2-inputs-stat.txt, 6 columns
NUWRO_SHA=38e47eb6b6ac63f6657022ae0cc5a2b5eaffc6a2e503735ce7222275771fea6e   # fd_f0_regrade.RATIO["closure_nuwro"]
NPZ=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz
BKG=/pscratch/sd/j/josephrb/s5c-20260924/runs/p2/bkg_dump.npz
BANK=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/bank_sweep_5d_bkgaware
DET=/pscratch/sd/j/josephrb/s5p-20260926/bank_detector
PVL=/pscratch/sd/j/josephrb/pv-ladder-20261024
NUWRO=$PVL/prep/ratios/L-5D-PV/nuwro.json
REFSRC=/pscratch/sd/j/josephrb/fd-stab-a1r-20261104
REFDST=$NEW/refs
S=docs/orchestration/state/measurement-paper/5d-community-20261024
E=$S/fd/rounding-stability-20261106/ensemble
SUMS=$S/fd/receipts-stab-a1r/full/SHA256SUMS
TRUTHS="nominal W1 W2 W3 q3 stage0c_gibuu closure_nuwro A7_mnvtune A7_genie_cv A7_genie_mec A7_nuwro A7_gibuu P1r P2r P3r P1g P2g P3g"
REFS="runs/control/stability/stab_control_b-_j-.npz"
for j in $(seq 21 51); do REFS="$REFS runs/control/stability/stab_control_b-_j$j.npz"; done
for t in $TRUTHS; do REFS="$REFS runs/control/closure/$t/stab_control_${t}_s991000.npz"; done
bail() { rm -f -- "$SELF"; exit 9; }
[ -n "$SELF" ] && [ -f "$SELF" ] || exit 9
[ -d "$NEW/logs" ] && [ -d "$D" ] && [ -d "$REFDST/runs/control/stability" ] || bail
[ "$(cat "$A1S/connect-analysis.done" 2>/dev/null)" = 0 ] || bail
[ "$(sha256sum "$A1S/ens1_stage1.json" 2>/dev/null | cut -d' ' -f1)" = "$S1_SHA" ] || bail
grep -q '"verdict": "STAB_PASS"' "$A1S/ens1_stage1.json" || bail
[ ! -e "$NEW/stage2" ] && [ ! -e "$L2" ] && [ ! -e "$REFDST/runs/control/closure" ] || bail
for r in $REFS; do [ ! -e "$REFDST/$r" ] || bail; done
q0=$(squeue --me -h -o '%j') || bail
[ -z "$(printf '%s\n' "$q0" | grep -E '^ens1_')" ] || bail
mkdir "$L2" || bail
exec > "$L2/connect-s2-dry.log" 2>&1
finish() { echo "ens1 a1 stage-2 dry submit rc=$1"; date -u +%FT%TZ; echo "$1" > "$L2/connect-s2-dry.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$L2/ens1_a1_s2_dry_submit.sh"
echo "stage 1: analysis done 0; ens1_stage1.json $S1_SHA, verdict STAB_PASS"

echo "== iris"; timeout 120 iris < /dev/null > "$L2/iris.txt" 2>&1; head -2 "$L2/iris.txt"
row=$(grep -E '^m3246 ' "$L2/iris.txt" | head -1); echo "$row"
bal=$(echo "$row" | awk 'NF>=5 {printf "%.1f", $5-$4}')
[ -n "$bal" ] || { echo "STOP: could not read the m3246 balance"; finish 9; }
echo "balance_node_h=$bal half=$(awk -v b="$bal" 'BEGIN{printf "%.1f", b/2}') caps=$CAPS"
awk -v b="$bal" -v c=$CAPS 'BEGIN{exit !(c <= b/2)}' || { echo "STOP: the caps are above half the balance"; finish 9; }

echo "== the fence (only rs1_* and ens1_* pass; cov2d-*, prr_* or any other name stops)"
squeue -u josephrb -h -o '%i|%j|%T|%M|%l' > "$L2/squeue-before.txt" 2>&1 || { echo "STOP: squeue failed"; finish 9; }
cat "$L2/squeue-before.txt"
other=$(awk -F'|' '$2 !~ /^(rs1_|ens1_)/' "$L2/squeue-before.txt")
ens=$(awk -F'|' '$2 ~ /^ens1_/' "$L2/squeue-before.txt")
[ -z "$other" ] || { echo "FENCE STOP: a cov2d-* job or a job of another name is present:"; printf '%s\n' "$other"; finish 9; }
[ -z "$ens" ] || { echo "STOP: an ens1_* job is already queued or running:"; printf '%s\n' "$ens"; finish 9; }
echo "FENCE: pass ($(grep -c . "$L2/squeue-before.txt") jobs; none outside rs1_*, no ens1_*)"

echo "== stage 2's charge ceiling (sacct)"
sacct -u josephrb -S 2026-11-07 -X -n -P -o JobID,JobName,State,ElapsedRaw,NNodes > "$L2/sacct-before.txt" 2>&1 \
  || { echo "STOP: sacct failed"; finish 9; }
s2=$(awk -F'|' '$2 ~ /^ens1_a1_s2/' "$L2/sacct-before.txt")
[ -z "$s2" ] || { echo "STOP: a stage-2 job is already in sacct:"; printf '%s\n' "$s2"; finish 9; }
echo "stage 2 spent 0 node-h; + the dry run's 0.75 = 0.75; cap $STAGE_CAP"

echo "== the shared inputs (unchanged since the records-only stat; stat only)"
F="%F|%i|%h|%s|%Y|%n"
{ stat -c "$F" "$NPZ" "$BKG"
  for d in "$BANK" "$DET"; do stat -c "$F" "$d"; find "$d" -mindepth 1 -print0 | sort -z | xargs -0 stat -c "$F"; done
} > "$L2/inputs-identity.txt" 2> "$L2/inputs-identity.err"
got=$(sha256sum "$L2/inputs-identity.txt" | cut -d' ' -f1)
echo "inputs identity: $(grep -c . "$L2/inputs-identity.txt") lines, sha256 $got (sent $IDENT_SHA); errors: $(grep -c . "$L2/inputs-identity.err")"
[ "$got" = "$IDENT_SHA" ] && [ ! -s "$L2/inputs-identity.err" ] || { echo "STOP: the shared inputs changed since the records-only stat"; finish 9; }
stat -c '%n size=%s mtime=%y atime=%x' "$NPZ" "$BKG" "$NUWRO" || { echo "STOP: an input is missing"; finish 9; }
na0=$(stat -c %X "$NUWRO")
dd if="$NUWRO" iflag=noatime of="$L2/nuwro.json.copy" bs=4M status=none || { echo "STOP: nuwro.json copy"; finish 9; }
na1=$(stat -c %X "$NUWRO"); ngot=$(sha256sum "$L2/nuwro.json.copy" | cut -d' ' -f1)
echo "pv-ladder nuwro.json sha256 $ngot (pin $NUWRO_SHA); atime $na0 -> $na1"
[ "$ngot" = "$NUWRO_SHA" ] && [ "$na0" = "$na1" ] || { echo "STOP: nuwro.json is not at its pin, or its atime moved"; finish 9; }

echo "== the deploy (re-checked)"
[ "$(git -C "$D" rev-parse HEAD)" = "$M" ] || { echo "STOP: HEAD is not M_A1"; finish 9; }
n=$(git -C "$D" status --porcelain --untracked-files=no | wc -l); echo "HEAD $M; modified tracked files: $n"
git -C "$D" status --porcelain --ignored > "$L2/deploy-status.txt"
echo "porcelain --ignored lines (recorded): $(grep -c . "$L2/deploy-status.txt")"
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
( cd "$REFDST" && find runs -type f -print0 | sort -z | xargs -0 sha256sum ) > "$L2/refs-SHA256SUMS-before"
cmp -s "$L2/refs-SHA256SUMS-before" "$NEW/logs/refs-SHA256SUMS" && [ "$(grep -c . "$NEW/logs/refs-SHA256SUMS")" -eq 20 ] \
  || { echo "STOP: stage 1's control-jitter copies are not the dry connect's"; finish 9; }
echo "stage 1's control-jitter copies: 20, as at the dry connect"

echo "== FD-STAB's stage-2 references (dd iflag=noatime; stat before and after)"
nref=$(echo $REFS | wc -w | tr -d " "); echo "references: $nref (base 1, jitters j21-j51 31, closures 18)"
[ "$nref" -eq 50 ] || { echo "STOP: the reference list is not 50"; finish 9; }
SF='%n|%i|%h|%s|%Y|%X|%Z'
miss=0
for r in $REFS; do stat -c "$SF" "$REFSRC/$r" || miss=$((miss + 1)); done > "$L2/refs-stat-before.txt"
[ "$miss" -eq 0 ] || { echo "STOP: $miss references missing"; cat "$L2/refs-stat-before.txt"; finish 9; }
echo "copy window start $(date -u +%FT%T.%3NZ)"
bad=0
for r in $REFS; do
  a0=$(stat -c %X "$REFSRC/$r")
  mkdir -p "$(dirname "$REFDST/$r")"
  dd if="$REFSRC/$r" iflag=noatime of="$REFDST/$r" bs=4M status=none || { echo "COPY FAILED $r"; bad=$((bad + 1)); continue; }
  a1=$(stat -c %X "$REFSRC/$r")
  want=$(awk -v n="$r" '$2 == n {print $1}' "$D/$SUMS")
  got=$(sha256sum "$REFDST/$r" | cut -d' ' -f1)
  [ "$a0" = "$a1" ] || { echo "ATIME MOVED $r ($a0 -> $a1)"; bad=$((bad + 1)); }
  [ -n "$want" ] && [ "$got" = "$want" ] || { echo "NOT PINNED $r ($got vs '$want')"; bad=$((bad + 1)); }
done
echo "copy window end $(date -u +%FT%T.%3NZ)"
for r in $REFS; do stat -c "$SF" "$REFSRC/$r"; done > "$L2/refs-stat-after.txt"
cmp -s "$L2/refs-stat-before.txt" "$L2/refs-stat-after.txt" && st=identical || st=DIFFERENT
echo "references: $nref copied, $bad problems; stat before/after (incl. atime and ctime): $st"
( cd "$REFDST" && find runs -type f -print0 | sort -z | xargs -0 sha256sum ) > "$L2/refs-SHA256SUMS"
echo "refs now: $(grep -c . "$L2/refs-SHA256SUMS") files (20 from stage 1 + $nref)"
[ "$bad" -eq 0 ] && [ "$st" = identical ] && [ "$(grep -c . "$L2/refs-SHA256SUMS")" -eq 70 ] \
  || { echo "STOP: a stage-2 reference"; finish 9; }

echo "== the environment (sourced)"
( source "$D/setup_salloc_env.sh" > "$L2/env-precheck.log" 2>&1
  python3 -B -c "import lightgbm, scipy, numpy, sys; print('python', sys.version.split()[0], 'lightgbm', lightgbm.__version__, 'scipy', scipy.__version__, 'numpy', numpy.__version__)" ) \
  || { echo "STOP: the environment lacks lightgbm/scipy (see env-precheck.log)"; finish 7; }

echo "== the stage-2 queue (sourced)"
( source "$D/setup_salloc_env.sh" > "$L2/env-tasks.log" 2>&1
  cd "$D" && PYTHONDONTWRITEBYTECODE=1 nice -n 19 python3 -B nd-unfolding/ensemble_estimator_probe.py tasks --stage 2 \
    --out-dir "$NEW/stage2" --runs "$NEW/runs" --npz "$NPZ" --bkg "$BKG" --bank "$BANK" --detector-dir "$DET" \
    --closure-ratio-dir "$PVL" --expect-npz-sha256 07fccc1abc7204bc29349b4ba96850986fe91e909e83fc54e8d1a6b3922a649f \
    --expect-bkg-sha256 2addac8f26055c5ed69862e7afe29e12ac51dbe23a8d6eeed79d71bec9d82955 ) || { echo "STOP: tasks"; finish 5; }
( cd "$NEW/stage2" && sha256sum dry.tsv shard0.tsv shard1.tsv shard2.tsv shard3.tsv shard4.tsv shard5.tsv ) > "$L2/queue-sha256.txt"
cat "$L2/queue-sha256.txt"
cat > "$L2/queue-sha256.expected" <<SUMS2
b55370daaee3443fad48285364aeee05d94ec0c675d87cd23ae1d9c609597c77  dry.tsv
bdc92a9c4f99f04db553caca532412bffa6dc89ff24e67ab8c2db40b63ea85e0  shard0.tsv
855d9f951c909f1cd32b91682766bffa4888ce77ae2415757f2a5945ed1c7528  shard1.tsv
773ab6bbc2202ad7bd7886573af2b48c71fabd7bee1762cb11e7f442606cee53  shard2.tsv
01c002b1913d9b47f44253d5b3f7f0411073a407d17e793ce0842b6414b4b2b6  shard3.tsv
26d4e7cd900a30098e15fd3e0c109f0497f9b4462ac7270869a64fbabbf22f50  shard4.tsv
7f1ac5bf33c9d4c387b3090cf33c9e1bd9f27bf5b8a54ffc4361c0f5c04ab3fd  shard5.tsv
SUMS2
cmp -s "$L2/queue-sha256.txt" "$L2/queue-sha256.expected" || { echo "STOP: the queue is not the one sent"; finish 5; }
nd=$(grep -vc '^#' "$NEW/stage2/dry.tsv"); echo "dry tasks: $nd"
echo "shard tasks: $(for i in 0 1 2 3 4 5; do grep -vc '^#' "$NEW/stage2/shard$i.tsv"; done | tr '\n' ' ')"
[ "$nd" -eq 7 ] || { echo "STOP: the dry run is not 7 tasks"; finish 5; }

date -u +%FT%TZ
cd "$NEW" || finish 9
sbatch --time=$TLIMIT_ARG --job-name=$JOBNAME --output="$L2/%x_%j.out" \
  "$D/nd-unfolding/sbatch_ens1.sh" dry 2 "$D" "$M" "$NEW" > "$L2/submit-s2-dry.out" 2>&1
rc=$?; echo "sbatch rc=$rc"; cat "$L2/submit-s2-dry.out"
[ $rc = 0 ] || { echo "STOP at sbatch (final)"; finish $rc; }
job=$(sed -n 's/^Submitted batch job \([0-9][0-9]*\)$/\1/p' "$L2/submit-s2-dry.out")
[ -n "$job" ] || { echo "STOP: no job id"; finish 9; }
echo "stage-2 dry job $job"; echo "$job" > "$L2/s2-dry.jobid"
tl=$(scontrol show job "$job" | sed -n 's/.*TimeLimit=\([^ ]*\).*/\1/p' | head -1)
echo "scontrol TimeLimit=$tl (declared $TLIMIT)"
if [ "$tl" != "$TLIMIT" ]; then
  scancel "$job"; echo "STOP: TimeLimit $tl is not $TLIMIT; job $job cancelled (rc $?)"; sleep 5
  sacct -j "$job" -X -n -P -o JobID,State,Elapsed; finish 6
fi
sleep 5
squeue -j "$job" -h -o "%i %j %T %M %l %D %q %a"
n=$(git -C "$D" status --porcelain --untracked-files=no | wc -l); echo "modified tracked files after: $n"
[ "$n" -eq 0 ] || { echo "the deploy changed after the submission (the job is queued; reported, not cancelled)"; finish 8; }
finish 0
