#!/bin/bash
# E96D dry run under amendment 1: the submission (E96D-BINDING-1 addendum A1 at M_A1 b438ab27; derived from the
# 2026-11-11 e96d_dry_submit.sh c8e017dd, whose run STOPped at the gate's projection). Runs on a login node from a
# /dev/shm copy of itself whose path is $1; it deletes that copy at exit. In order:
#   the fence: stop if a cov2d*/t2a* job or an e96data* job of ours is queued or running, or if LL5D's gate jobs
#     61078463 / 61078506 (ll5d_gate_*) are still in squeue (addendum A1: E96D waits for them to end); cov2d_fence.sh
#     16a2a5cd runs as its own connect first;
#   iris: stop unless the 5.1 node-h cap is at most half of m3246's remaining balance;
#   a stat of the two inputs and of (e)'s product (stat only; sizes must equal AT-RISK's 2026-11-11 stat);
#   a fresh clone at M_A1 into $NEW/deploy: clean, the sha256 of the six files addendum A1 binds, and binding 1 at
#     origin/main naming M_A1;
#   the environment pre-check (0 node-h) and the queues from the bound module's own `tasks`, under the sourced
#     environment: dry.tsv and full.tsv at the digests sent (2 dry tasks, 50 full tasks);
#   one sbatch: sbatch_e96data.sh dry at M_A1, --time=0:30:00, job name e96data_dry; scontrol's TimeLimit must read
#     00:30:00, or the job is cancelled at once and the connect stops.
# The gate runs inside the dry job (the job script, after DONE) and writes $NEW/log-dry/GATE.json; it is read by the
# next connect. Writes only under $NEW (new; refused if it exists). No set -u.
SELF=$1
M=b438ab2710b2dcfd30238107187caa3628393b11
NEW=/pscratch/sd/j/josephrb/e96data-a1
D=$NEW/deploy
CAP=5.1
TLIMIT_ARG=0:30:00
TLIMIT=00:30:00
JOBNAME=e96data_dry
NPZ=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz
BKG=/pscratch/sd/j/josephrb/s5c-20260924/runs/p2/bkg_dump.npz
EPROD=/pscratch/sd/j/josephrb/s5p-20260926/runs/s2/num/data/data_b-_j-.npz
E=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/e96-data-20261110
bail() { rm -f -- "$SELF"; exit 9; }
[ -n "$SELF" ] && [ -f "$SELF" ] || exit 9
[ ! -e "$NEW" ] || { echo "STOP: $NEW exists"; bail; }
q0=$(squeue --me -h -o '%j') || { echo "STOP: squeue failed"; bail; }
[ -z "$(printf '%s\n' "$q0" | grep -E '^(e96data|cov2d|t2a|ll5d_gate_)')" ] || { echo "STOP: an e96data/cov2d/t2a/ll5d_gate job is present"; bail; }
mkdir "$NEW" && mkdir "$NEW/logs" || bail
LOG=$NEW/logs/connect-dry.log
exec > >(tee -a "$LOG") 2>&1
finish() { echo "e96data dry submit rc=$1"; date -u +%FT%TZ; echo "$1" > "$NEW/logs/connect-dry.done"; rm -f -- "$SELF"; sleep 1; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$NEW/logs/e96d_dry_submit.sh"

echo "== the fence (a cov2d*/t2a*, e96data* or ll5d_gate_* job, or job 61078463/61078506, stops)"
squeue -u josephrb -h -o '%i|%j|%T|%M|%l' > "$NEW/logs/squeue-before.txt" 2>&1 || { echo "STOP: squeue failed"; finish 9; }
cat "$NEW/logs/squeue-before.txt"
hit=$(awk -F'|' '$2 ~ /^(cov2d|t2a|e96data|ll5d_gate_)/ || $1 == "61078463" || $1 == "61078506"' "$NEW/logs/squeue-before.txt")
[ -z "$hit" ] || { echo "FENCE STOP:"; printf '%s\n' "$hit"; finish 9; }
echo "FENCE: pass ($(wc -l < "$NEW/logs/squeue-before.txt" | tr -d ' ') jobs, none cov2d/t2a/e96data/ll5d_gate)"
sacct -j 61078463,61078506 -X -n -P -o JobID,JobName,State,Start,End > "$NEW/logs/ll5d-gates-sacct.txt" 2>&1
cat "$NEW/logs/ll5d-gates-sacct.txt"

echo "== iris"; timeout 120 iris < /dev/null > "$NEW/logs/iris.txt" 2>&1; head -2 "$NEW/logs/iris.txt"
row=$(grep -E '^m3246 ' "$NEW/logs/iris.txt" | head -1); echo "$row"
bal=$(echo "$row" | awk 'NF>=5 {printf "%.1f", $5-$4}')
[ -n "$bal" ] || { echo "STOP: could not read the m3246 balance"; finish 9; }
echo "balance_node_h=$bal half=$(awk -v b="$bal" 'BEGIN{printf "%.1f", b/2}') cap=$CAP"
awk -v b="$bal" -v c=$CAP 'BEGIN{exit !(c <= b/2)}' || { echo "STOP: the cap is above half the balance"; finish 9; }

echo "== stat (stat only)"
miss=0
for pair in "$NPZ 1548438020" "$BKG 16017201" "$EPROD 95564"; do
  set -- $pair
  s=$(stat -c %s "$1" 2>/dev/null) || { echo "MISSING $1"; miss=$((miss + 1)); continue; }
  echo "stat utc=$(date -u +%FT%TZ) $(stat -c 'atime=%X mtime=%Y size=%s %n' "$1")"
  [ "$s" = "$2" ] || { echo "SIZE $1 is $s, not $2"; miss=$((miss + 1)); }
done
echo "stat: 3 files, $miss problems"
[ "$miss" -eq 0 ] || { echo "STOP: an input or (e)'s product is missing or resized"; finish 9; }

echo "== the deploy"
git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "$D" > "$NEW/logs/clone.log" 2>&1 || { echo "STOP: clone"; finish 3; }
git -C "$D" -c advice.detachedHead=false checkout -q "$M" || { echo "STOP: checkout"; finish 3; }
[ "$(git -C "$D" rev-parse HEAD)" = "$M" ] || { echo "STOP: HEAD is not M_A1"; finish 9; }
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "HEAD $M; porcelain --ignored lines before: $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy is not clean"; finish 9; }
bad=0
while read -r h p; do
  [ "$(sha256sum "$D/$p" | cut -d' ' -f1)" = "$h" ] || { echo "SHA256 MISMATCH $p"; bad=$((bad + 1)); }
done <<SHAS
486068bd2d171512fcafed01ae4424d1ea3c7af81f58c2977b3b45d30afe6704 $E/E96D-DECLARATION.md
16c1fd2f58fcd5a833fd9591ae579d99b9296028b805cd64de165a3d15ecfaee $E/E96D-AMENDMENT-1.md
414f7d352560b1cd310666af8e363fe294fda6ebb13239309887cb96c5f0b33a nd-unfolding/ensemble_estimator_data.py
72680b62d48e07554e1c8ac07dc6bd7289798892bdfaa08f0733068c8d17ec7e nd-unfolding/sbatch_e96data.sh
186d881a29fc51c1941bd9a3d575061f4b841692c198b437ea02ff40abb35469 nd-unfolding/tests/test_ensemble_estimator_data.py
2a7187422715599f3186e29ee2902c46ab50ce3ce08cea8356f8dc19a0f3cdbd nd-unfolding/tests/ensemble_estimator_data_mutation.py
SHAS
b1=$(git -C "$D" show "origin/main:$E/E96D-BINDING-1.md" 2>/dev/null)
b1ok=0; printf '%s\n' "$b1" | grep -qF "M_A1 = \`$M\`" && b1ok=1
echo "sha256: 6 checked, $bad mismatches; E96D-BINDING-1 at origin/main names M_A1: $b1ok"
echo "origin/main $(git -C "$D" rev-parse origin/main); binding 1 sha256 $(printf '%s\n' "$b1" | sha256sum | cut -d' ' -f1)"
[ "$bad" -eq 0 ] && [ "$b1ok" -eq 1 ] || { echo "STOP: bound bytes"; finish 9; }

echo "== the environment (sourced)"
( source "$D/setup_salloc_env.sh" > "$NEW/logs/env-precheck.log" 2>&1
  python3 -B -c "import lightgbm, scipy, numpy, sys; print('python', sys.version.split()[0], 'lightgbm', lightgbm.__version__, 'scipy', scipy.__version__, 'numpy', numpy.__version__)" ) \
  || { echo "STOP: the environment lacks lightgbm/scipy (see env-precheck.log)"; finish 7; }

echo "== the queues (sourced)"
( source "$D/setup_salloc_env.sh" > "$NEW/logs/env-tasks.log" 2>&1
  cd "$D" && PYTHONDONTWRITEBYTECODE=1 nice -n 19 python3 -B nd-unfolding/ensemble_estimator_data.py tasks \
    --out-dir "$NEW" --runs "$NEW/runs" --npz "$NPZ" --bkg "$BKG" ) || { echo "STOP: tasks"; finish 5; }
( cd "$NEW" && sha256sum dry.tsv full.tsv ) > "$NEW/logs/queue-sha256.txt"
cat "$NEW/logs/queue-sha256.txt"
cat > "$NEW/logs/queue-sha256.expected" <<SUMS1
db37968122076d6ba3204f1347a4931a4cbc2de015fbf8cdf285222de053f9cb  dry.tsv
3aa0bc5e864144714e7f4509b91b1622f036436ec7cb6c27d7433b938299f5a1  full.tsv
SUMS1
cmp -s "$NEW/logs/queue-sha256.txt" "$NEW/logs/queue-sha256.expected" || { echo "STOP: the queues are not the ones sent"; finish 5; }
nd=$(grep -vc '^#' "$NEW/dry.tsv"); nf=$(grep -vc '^#' "$NEW/full.tsv"); echo "dry tasks: $nd; full tasks: $nf"
[ "$nd" -eq 2 ] && [ "$nf" -eq 50 ] || { echo "STOP: the queues are not 2 and 50 tasks"; finish 5; }
n=$(git -C "$D" status --porcelain --ignored | wc -l); echo "porcelain --ignored lines before sbatch: $n"
[ "$n" -eq 0 ] || { echo "STOP: the deploy changed"; finish 9; }

date -u +%FT%TZ
cd "$NEW" || finish 9
sbatch --time=$TLIMIT_ARG --job-name=$JOBNAME --output="$NEW/logs/%x_%j.out" \
  "$D/nd-unfolding/sbatch_e96data.sh" dry "$D" "$M" "$NEW" > "$NEW/logs/submit-dry.out" 2>&1
rc=$?; echo "sbatch rc=$rc"; cat "$NEW/logs/submit-dry.out"
[ $rc = 0 ] || { echo "STOP at sbatch (final)"; finish $rc; }
job=$(sed -n 's/^Submitted batch job \([0-9][0-9]*\)$/\1/p' "$NEW/logs/submit-dry.out")
[ -n "$job" ] || { echo "STOP: no job id"; finish 9; }
echo "dry job $job"; echo "$job" > "$NEW/logs/dry.jobid"
tl=$(scontrol show job "$job" | sed -n 's/.*TimeLimit=\([^ ]*\).*/\1/p' | head -1)
echo "scontrol TimeLimit=$tl (declared $TLIMIT)"
if [ "$tl" != "$TLIMIT" ]; then
  scancel "$job"; echo "STOP: TimeLimit $tl is not $TLIMIT; job $job cancelled (rc $?)"; sleep 5
  sacct -j "$job" -X -n -P -o JobID,State,Elapsed; finish 6
fi
sleep 5
squeue -j "$job" -h -o "%i %j %T %M %l %D %q %a %S"
finish 0
