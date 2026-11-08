#!/bin/bash
# RS1 full run, resumed under RS1-BINDING-2 addendum A1 (RS1-ADDENDUM-A1.md §2-§3): the staging and the submission, on a
# login node, from a /dev/shm copy of itself whose path is $1 (deleted at exit). In order:
#   the COV2D fence, recorded; iris against the half-balance rule;
#   attempt 1, from its own files: log-dry/SHA256SUMS e3cc597c (#891), log-full/SHA256SUMS 846e322a (#901), FAILED
#     "rc=124", no log-full/DONE; sacct 60970044 COMPLETED|944|1 and 60972000 FAILED|3520|1, so 1.2400 node-h spent and
#     the 4.5 node-h ceiling fits in 8.0 - 1.2400;
#   a stat of both inputs;
#   two fresh clones into a NEW root: $NEW/deploy at M (the bound RS1 code, the dry run's pin) and $NEW/a1 at A1's M,
#     both clean, with their blobs and the declaration's, binding 1's and the addendum's sha256;
#   the queue from the bound probe's own tasks --runs $NEW/runs: 66 tasks, 9 dry, at the digests attempt 1's queue gives
#     with only its root changed (252c9628, 92195b6d);
#   the planner's --help, then the staging (rs1_a1_plan.py stage), both under the deploy's sourced environment: 66 tasks, 20 done, 46 todo with rs1_V_02 among them, 102 files copied, V_02's
#     leftovers in runs-attempt1/rs1_V_02 only; then verify;
#   the environment pre-check (0 node-h);
#   one sbatch: sbatch_rs1_a1.sh, --time=04:30:00, from the plain login environment; scontrol's TimeLimit must read
#     04:30:00, or the job is cancelled at once and the connect stops.
# Writes only under the NEW root (refused if it exists). Attempt 1's root is read, never written. No set -u.
SELF=$1
M=e306087e68fd497541d32b440848a40f7f29611e
MA1=1f747346519d75a680b5c67d644bae798eeb5f86
OLD=/pscratch/sd/j/josephrb/rs1-20261106
NEW=/pscratch/sd/j/josephrb/rs1-a1-20261107
PRICE=8.0
TLIMIT=04:30:00
NPZ=/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz
BKG=/pscratch/sd/j/josephrb/s5c-20260924/runs/p2/bkg_dump.npz
S=docs/orchestration/state/measurement-paper/5d-community-20261024/fd/rounding-stability-20261106
bail() { rm -f -- "$SELF"; exit 9; }
[ -n "$SELF" ] && [ -f "$SELF" ] || exit 9
[ ! -e "$NEW" ] && [ -d "$OLD/runs" ] || bail
[ -z "$(squeue --me -h -n rs1_dry,rs1_full,rs1_a1 -o %i)" ] || bail
mkdir "$NEW" && mkdir "$NEW/logs" || bail
LOG=$NEW/logs/connect-a1.log
exec > "$LOG" 2>&1
finish() { echo "rs1 a1 submit rc=$1"; date -u +%FT%TZ; echo "$1" > "$NEW/logs/connect-a1.done"; rm -f -- "$SELF"; exit "$1"; }
echo "node $(hostname) nproc=$(nproc) loadavg $(cut -d' ' -f1-3 /proc/loadavg)"
date -u +%FT%TZ
echo "connect script sha256 $(sha256sum "$SELF" | cut -d' ' -f1)"
cp "$SELF" "$NEW/logs/rs1_a1_submit.sh"

echo "== COV2D fence"
squeue -u josephrb -h -o '%i|%j|%T|%M|%l' > "$NEW/logs/squeue-before.txt" 2>&1 || { echo "STOP: squeue failed"; finish 9; }
hits=$(awk -F'|' '$2 ~ /^cov2d-/' "$NEW/logs/squeue-before.txt")
if [ -n "$hits" ]; then echo "FENCE: cov2d jobs present (recorded; RS1 reads no COV2D input):"; printf '%s\n' "$hits"
else echo "FENCE: no cov2d-* job queued or running"; fi

echo "== iris"; timeout 120 iris < /dev/null > "$NEW/logs/iris.txt" 2>&1; head -2 "$NEW/logs/iris.txt"
row=$(grep -E '^m3246 ' "$NEW/logs/iris.txt" | head -1); echo "$row"
bal=$(echo "$row" | awk 'NF>=5 {printf "%.1f", $5-$4}')
[ -n "$bal" ] || { echo "STOP: could not read the m3246 balance"; finish 9; }
echo "balance_node_h=$bal half=$(awk -v b="$bal" 'BEGIN{printf "%.1f", b/2}') price=$PRICE"
awk -v b="$bal" -v c=$PRICE 'BEGIN{exit !(c <= b/2)}' || { echo "STOP: the price is above half the balance"; finish 9; }

echo "== attempt 1"
dsum=$(sha256sum "$OLD/log-dry/SHA256SUMS" | cut -d' ' -f1); fsum=$(sha256sum "$OLD/log-full/SHA256SUMS" | cut -d' ' -f1)
echo "log-dry/SHA256SUMS $dsum; log-full/SHA256SUMS $fsum; FAILED '$(cat "$OLD/log-full/FAILED")'"
[ "$dsum" = e3cc597cdc1cdb0a3bfea0095130b9a2f99a3578c63ce1541c2a893092ab2935 ] \
  && [ "$fsum" = 846e322a8ced04ecb63953e7109328ca6f01b6d115486c205fedcfac83d97fd3 ] \
  && [ "$(cat "$OLD/log-full/FAILED")" = "rc=124" ] && [ ! -e "$OLD/log-full/DONE" ] || { echo "STOP: attempt 1 is not the one recorded"; finish 4; }
s1=$(sacct -j 60970044 -X -n -P -o State,ElapsedRaw,NNodes | head -1); s2=$(sacct -j 60972000 -X -n -P -o State,ElapsedRaw,NNodes | head -1)
echo "60970044 $s1; 60972000 $s2"
[ "$s1" = "COMPLETED|944|1" ] && [ "$s2" = "FAILED|3520|1" ] || { echo "STOP: the charges are not the receipts'"; finish 4; }
spent=$(awk 'BEGIN{printf "%.4f", (944 + 3520) / 3600}')
echo "spent $spent node-h; ceiling 4.5; cap $PRICE"
awk -v s="$spent" -v c=$PRICE 'BEGIN{exit !(s + 4.5 <= c)}' || { echo "STOP: the ceiling does not fit the cap"; finish 4; }

echo "== stat"
for f in "$NPZ" "$BKG"; do stat -c '%n size=%s mtime=%y atime=%x' "$f" || { echo "STOP: input missing"; finish 9; }; done

echo "== the clones"
for pair in "deploy $M" "a1 $MA1"; do
  set -- $pair
  git clone -q https://github.com/josephbaileyy/MINERvA-OmniFold.git "$NEW/$1" > "$NEW/logs/clone-$1.log" 2>&1 || { echo "STOP: clone $1"; finish 3; }
  git -C "$NEW/$1" -c advice.detachedHead=false checkout -q "$2" || { echo "STOP: checkout $1"; finish 3; }
  [ "$(git -C "$NEW/$1" rev-parse HEAD)" = "$2" ] || { echo "STOP: $1 HEAD is not $2"; finish 9; }
  n=$(git -C "$NEW/$1" status --porcelain --ignored | wc -l); echo "$1 at $2; porcelain --ignored lines: $n"
  [ "$n" -eq 0 ] || { echo "STOP: $1 is not clean"; finish 9; }
done
bad=0
while read -r dir b p; do
  [ "$(git -C "$NEW/$dir" hash-object "$p")" = "$b" ] || { echo "MISMATCH $dir $p"; bad=$((bad + 1)); }
done <<BLOBS
deploy 8465d84f08e99ad12f2c4fb3afca2ea7efbe485b nd-unfolding/rounding_mechanism_probe.py
deploy d58c241eff687a96bda94812d145a90d9f4790ed nd-unfolding/rounding_mechanism_analyze.py
deploy 9ad7dece80ba4ca7a6a0548c02c07bae4c947d2b nd-unfolding/sbatch_rs1.sh
a1 5023db6777c1a4c0b30ea888fe63409459d1053f nd-unfolding/rs1_a1_plan.py
a1 0e10551263de66f095014c1fd953056147187768 nd-unfolding/sbatch_rs1_a1.sh
a1 8465d84f08e99ad12f2c4fb3afca2ea7efbe485b nd-unfolding/rounding_mechanism_probe.py
BLOBS
decl=$(sha256sum "$NEW/deploy/$S/RS1-DECLARATION.md" | cut -d' ' -f1); b1=$(sha256sum "$NEW/deploy/$S/RS1-BINDING-1.md" | cut -d' ' -f1)
add=$(sha256sum "$NEW/a1/$S/RS1-ADDENDUM-A1.md" | cut -d' ' -f1)
echo "blobs: 6 checked, $bad mismatches; declaration $decl; binding 1 $b1; addendum A1 $add"
[ "$bad" -eq 0 ] && [ "$decl" = dbfb0c941b2ad6999b2edb3b8bf77ca735b2f01f86ca593425e44c2ad5c91e76 ] \
  && [ "$b1" = 947fd2750343ead7aff5281af8bfb03a137f76346071a84233b62ebf12744255 ] \
  && [ "$add" = cef9555afdf99ecfebe21b60f374c64728640968496ecdf310afd29242d90e5a ] || { echo "STOP: bound bytes"; finish 9; }

echo "== the queue"
( source "$NEW/deploy/setup_salloc_env.sh" > "$NEW/logs/env-tasks.log" 2>&1
  cd "$NEW/deploy" && PYTHONDONTWRITEBYTECODE=1 python3 -B nd-unfolding/rounding_mechanism_probe.py tasks \
    --out "$NEW/queue.tsv" --dry-out "$NEW/dry.tsv" --npz "$NPZ" --bkg "$BKG" \
    --expect-npz-sha256 07fccc1abc7204bc29349b4ba96850986fe91e909e83fc54e8d1a6b3922a649f \
    --expect-bkg-sha256 2addac8f26055c5ed69862e7afe29e12ac51dbe23a8d6eeed79d71bec9d82955 --runs "$NEW/runs" ) \
  || { echo "STOP: tasks"; finish 5; }
qs=$(sha256sum "$NEW/queue.tsv" | cut -d' ' -f1); ds=$(sha256sum "$NEW/dry.tsv" | cut -d' ' -f1)
echo "queue.tsv $qs; dry.tsv $ds"
[ "$qs" = 252c9628c0a238820d851f5d77e72afefda3d9e61d6fcc9a658e5a3e8543ea73 ] \
  && [ "$ds" = 92195b6dc70658d8e3d348737d6eda5a83952dc4f88a5ff1a81b574f6541071d ] || { echo "STOP: the queue is not the one sent"; finish 5; }
[ "$(sed 's#/rs1-20261106/#/rs1-a1-20261107/#g' "$OLD/queue.tsv" | sha256sum | cut -d' ' -f1)" = "$qs" ] \
  || { echo "STOP: the new queue differs from attempt 1's beyond its root"; finish 5; }

echo "== the planner's --help under the deploy's sourced environment (never the system python3; A1 connect 1)"
( source "$NEW/deploy/setup_salloc_env.sh" > "$NEW/logs/env-help.log" 2>&1
  python3 --version
  python3 -B "$NEW/a1/nd-unfolding/rs1_a1_plan.py" --help ) > "$NEW/logs/plan-help.out" 2>&1 \
  || { cat "$NEW/logs/plan-help.out"; echo "STOP: the planner's --help failed under the sourced environment"; finish 6; }
cat "$NEW/logs/plan-help.out"
echo "== the staging, under the deploy's environment"
( source "$NEW/deploy/setup_salloc_env.sh" > "$NEW/logs/env-stage.log" 2>&1
  python3 --version
  python3 -B "$NEW/a1/nd-unfolding/rs1_a1_plan.py" stage --old "$OLD" --new "$NEW" ) > "$NEW/logs/stage.out" 2>&1 \
  || { cat "$NEW/logs/stage.out"; echo "STOP: staging"; finish 6; }
cat "$NEW/logs/stage.out"
cat "$NEW/stage.json"
python3 -I -c '
import json, sys
s = json.load(open(sys.argv[1]))
ok = s["tasks"] == 66 and s["done"] == 20 and len(s["todo"]) == 46 and "rs1_V_02" in s["todo"] \
    and s["copied_files"] == 102 and s["attempt1_left"] == ["rs1_V_02"]
sys.exit(0 if ok else 1)' "$NEW/stage.json" || { echo "STOP: the staging is not the declared 20 done / 46 todo"; finish 6; }
( source "$NEW/deploy/setup_salloc_env.sh" > /dev/null 2>&1
  python3 -B "$NEW/a1/nd-unfolding/rs1_a1_plan.py" verify --root "$NEW" ) || { echo "STOP: verify"; finish 6; }
ls "$NEW/runs-attempt1/rs1_V_02"

echo "== the environment"
( source "$NEW/deploy/setup_salloc_env.sh" > "$NEW/logs/env-precheck.log" 2>&1
  python3 -B -c "import lightgbm, scipy, numpy, sys; print('python', sys.version.split()[0], 'lightgbm', lightgbm.__version__, 'scipy', scipy.__version__, 'numpy', numpy.__version__)" ) \
  || { echo "STOP: the environment lacks lightgbm/scipy"; finish 7; }

date -u +%FT%TZ
cd "$NEW" || finish 9
sbatch --time=$TLIMIT --job-name=rs1_a1 --output="$NEW/logs/%x_%j.out" \
  "$NEW/a1/nd-unfolding/sbatch_rs1_a1.sh" "$NEW/deploy" "$M" "$NEW" "$NEW/a1" "$MA1" > "$NEW/logs/submit.out" 2>&1
rc=$?; echo "sbatch rc=$rc"; cat "$NEW/logs/submit.out"
[ $rc = 0 ] || { echo "STOP at sbatch (final)"; finish $rc; }
job=$(sed -n 's/^Submitted batch job \([0-9][0-9]*\)$/\1/p' "$NEW/logs/submit.out")
[ -n "$job" ] || { echo "STOP: no job id"; finish 9; }
echo "a1 job $job"; echo "$job" > "$NEW/logs/a1.jobid"
tl=$(scontrol show job "$job" | sed -n 's/.*TimeLimit=\([^ ]*\).*/\1/p' | head -1)
echo "scontrol TimeLimit=$tl (declared $TLIMIT)"
if [ "$tl" != "$TLIMIT" ]; then
  scancel "$job"; echo "STOP: TimeLimit $tl is not $TLIMIT; job $job cancelled (rc $?)"; sleep 5
  sacct -j "$job" -X -n -P -o JobID,State,Elapsed; finish 6
fi
sleep 5
squeue -j "$job" -h -o "%i %j %T %M %l %D %q %a"
for dir in deploy a1; do echo "$dir porcelain --ignored after: $(git -C "$NEW/$dir" status --porcelain --ignored | wc -l)"; done
finish 0
